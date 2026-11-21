import { afterEach, describe, expect, it } from "vitest";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { commitRelease, verifyReleaseCommit } from "../scripts/release/commit.mjs";

// The release tag must name a commit that holds exactly the code the release was built with,
// also when a pull request is merged while the release is being cut (#267).
const RELEASE = "2026-11-17-28b826b7be87";
const CONFIG = "data/omics/release-config.json";
const roots: string[] = [];
const env = { ...process.env, GIT_AUTHOR_NAME: "t", GIT_AUTHOR_EMAIL: "t@example.org", GIT_COMMITTER_NAME: "t", GIT_COMMITTER_EMAIL: "t@example.org", GIT_CONFIG_GLOBAL: "/dev/null", GIT_CONFIG_SYSTEM: "/dev/null" };
const git = (cwd: string, ...args: string[]) => execFileSync("git", args, { cwd, env, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();
const write = (cwd: string, file: string, text: string) => {
  fs.mkdirSync(path.dirname(path.join(cwd, file)), { recursive: true });
  fs.writeFileSync(path.join(cwd, file), text);
};

/** A bare origin with one commit on main, the release runner's clone of it, and a second clone that merges to main. */
function repositories() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "release-commit-"));
  roots.push(root);
  const origin = path.join(root, "origin.git");
  git(root, "init", "--quiet", "--bare", "--initial-branch=main", origin);
  const clone = (name: string) => {
    const directory = path.join(root, name);
    git(root, "clone", "--quiet", origin, directory);
    for (const [key, value] of [["user.name", "t"], ["user.email", "t@example.org"], ["commit.gpgsign", "false"]]) git(directory, "config", key, value);
    return directory;
  };
  const other = clone("other");
  write(other, "shared/omics/locator.ts", "export const built = true;\n");
  write(other, CONFIG, "{}\n");
  write(other, "website/manifest.json", '{"release_id":"previous"}\n');
  git(other, "checkout", "--quiet", "-B", "main");
  git(other, "add", "-A");
  git(other, "commit", "--quiet", "-m", "Start");
  git(other, "push", "--quiet", "origin", "main");
  const runner = clone("runner");
  return { origin, other, runner };
}

/** What `next.mjs prepare` and the build leave in the runner's work tree. */
function build(runner: string) {
  const built = git(runner, "rev-parse", "HEAD");
  write(runner, CONFIG, `${JSON.stringify({ source_revision: built })}\n`);
  write(runner, "website/manifest.json", `{"release_id":"${RELEASE}"}\n`);
  write(runner, `data/omics/releases/${RELEASE}.json`, "{}\n");
  return built;
}

/** A pull request that changes shared code, merged to main behind the runner's back. */
function mergeSharedChange(other: string) {
  write(other, "shared/omics/locator.ts", "export const built = false;\n");
  git(other, "commit", "--quiet", "-am", "Merge pull request #228 from rewire-bio/locator");
  git(other, "push", "--quiet", "origin", "main");
  return git(other, "rev-parse", "HEAD");
}

const options = (runner: string) => ({ releaseId: RELEASE, cwd: runner, wait: async () => {}, log: () => {} });

afterEach(() => {
  for (const root of roots.splice(0)) fs.rmSync(root, { recursive: true, force: true });
});

describe("release commit", () => {
  it("pushes the release commit straight to main when main has not moved", async () => {
    const { origin, runner } = repositories();
    const built = build(runner);
    const result = await commitRelease(options(runner));
    expect(result).toEqual({ release: git(runner, "rev-parse", "HEAD"), built, main: result.release });
    expect(git(origin, "rev-parse", "main")).toBe(result.release);
    expect(git(origin, "log", "-1", "--format=%s", "main")).toBe(`Cut release ${RELEASE} [skip ci]`);
    expect(verifyReleaseCommit({ commit: result.release, cwd: runner })).toEqual({ release: result.release, built });
  });

  it("keeps the release commit on the built commit when a pull request is merged meanwhile", async () => {
    const { origin, other, runner } = repositories();
    const built = build(runner);
    const merged = mergeSharedChange(other);
    const { release, main } = await commitRelease(options(runner));

    // The commit the tags will name is the built commit plus the release's own files.
    expect(git(runner, "rev-parse", `${release}^`)).toBe(built);
    expect(git(runner, "show", `${release}:shared/omics/locator.ts`)).toBe("export const built = true;");
    expect(git(runner, "show", `${release}:website/manifest.json`)).toContain(RELEASE);
    expect(verifyReleaseCommit({ commit: release, cwd: runner })).toEqual({ release, built });

    // main holds both, with the merged pull request on its first-parent line.
    expect(git(origin, "rev-parse", "main")).toBe(main);
    expect(git(origin, "rev-list", "--parents", "-n", "1", "main").split(" ")).toEqual([main, merged, release]);
    expect(git(origin, "log", "-1", "--format=%s", "main")).toBe(`Cut release ${RELEASE} [skip ci]`);
    expect(git(origin, "show", "main:shared/omics/locator.ts")).toBe("export const built = false;");
    expect(git(origin, "show", "main:website/manifest.json")).toContain(RELEASE);

    // The publish steps run from the release commit, not from the merge.
    expect(git(runner, "rev-parse", "HEAD")).toBe(release);
    expect(fs.readFileSync(path.join(runner, "shared/omics/locator.ts"), "utf8")).toBe("export const built = true;\n");
  });

  it("gives up after the allowed attempts", async () => {
    const { other, runner } = repositories();
    build(runner);
    mergeSharedChange(other);
    await expect(commitRelease({ ...options(runner), attempts: 1 })).rejects.toThrow(/Could not push the release after 1 attempts/);
  });
});

describe("release commit check", () => {
  it("refuses a release commit rebased onto a main the release was not built from", () => {
    const { other, runner } = repositories();
    const built = build(runner);
    mergeSharedChange(other);
    // What the workflow did before #267: commit, then rebase onto the new main and tag HEAD.
    git(runner, "add", "-A", "data", "website");
    git(runner, "commit", "--quiet", "-m", `Cut release ${RELEASE} [skip ci]`);
    git(runner, "fetch", "--quiet", "origin", "main");
    git(runner, "rebase", "--quiet", "origin/main");
    git(runner, "push", "--quiet", "origin", "HEAD:main");
    expect(() => verifyReleaseCommit({ commit: "HEAD", cwd: runner })).toThrow(new RegExp(`the release was built from ${built}`));
  });

  it("refuses the merge of a release commit into main, and a release commit that is not on main", async () => {
    const { other, runner } = repositories();
    build(runner);
    mergeSharedChange(other);
    const { release, main } = await commitRelease(options(runner));
    expect(() => verifyReleaseCommit({ commit: main, cwd: runner })).toThrow(/the release was built from/);
    git(runner, "update-ref", "refs/remotes/origin/main", `${release}^`);
    expect(() => verifyReleaseCommit({ commit: release, cwd: runner })).toThrow(/is not on origin\/main/);
  });

  it("refuses a release commit that changes files outside data and website", () => {
    const { runner } = repositories();
    build(runner);
    write(runner, "shared/omics/locator.ts", "export const built = 'edited';\n");
    git(runner, "add", "-A");
    git(runner, "commit", "--quiet", "-m", `Cut release ${RELEASE} [skip ci]`);
    git(runner, "push", "--quiet", "origin", "HEAD:main");
    expect(() => verifyReleaseCommit({ commit: "HEAD", cwd: runner })).toThrow(/changes files outside data\/ and website\/: shared\/omics\/locator.ts/);
  });

  it("checks that each tag on origin names the release commit", async () => {
    const { other, runner } = repositories();
    build(runner);
    mergeSharedChange(other);
    const { release, main } = await commitRelease(options(runner));
    const tags = [`serving/${RELEASE}`, `kg/${RELEASE}`];
    expect(() => verifyReleaseCommit({ commit: release, tags, cwd: runner })).toThrow(`Tag serving/${RELEASE} names nothing`);
    git(runner, "push", "--quiet", "origin", `${release}:refs/tags/serving/${RELEASE}`, `${main}:refs/tags/kg/${RELEASE}`);
    expect(() => verifyReleaseCommit({ commit: release, tags, cwd: runner })).toThrow(`Tag kg/${RELEASE} names ${main}, not release commit ${release}`);
    git(runner, "push", "--quiet", "--force", "origin", `${release}:refs/tags/kg/${RELEASE}`);
    expect(verifyReleaseCommit({ commit: release, tags, cwd: runner }).release).toBe(release);
    // An annotated tag is read through to its commit.
    git(runner, "tag", "-a", "-m", "annotated", `serving/${RELEASE}`, release);
    git(runner, "push", "--quiet", "--force", "origin", `refs/tags/serving/${RELEASE}`);
    expect(verifyReleaseCommit({ commit: release, tags, cwd: runner }).release).toBe(release);
  });
});
