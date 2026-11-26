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

  it("pushes the same commit again, without a merge, when a push fails and main has not moved", async () => {
    const { origin, runner } = repositories();
    const built = build(runner);
    // The origin refuses the first push only.
    const hook = path.join(origin, "hooks", "pre-receive");
    fs.writeFileSync(hook, '#!/bin/sh\nif [ ! -e "$GIT_DIR/refused" ]; then touch "$GIT_DIR/refused"; exit 1; fi\n', { mode: 0o755 });
    const result = await commitRelease(options(runner));
    expect(fs.existsSync(path.join(origin, "refused"))).toBe(true);
    expect(result.main).toBe(result.release);
    expect(git(origin, "rev-list", "--parents", "-n", "1", "main").split(" ")).toEqual([result.release, built]);
  });

  it("refuses, before any push, a release whose config names another commit than the one it was built on", async () => {
    const { origin, other, runner } = repositories();
    const start = git(runner, "rev-parse", "HEAD");
    build(runner);
    // The config names a commit that is not the one checked out.
    write(runner, CONFIG, `${JSON.stringify({ source_revision: mergeSharedChange(other) })}\n`);
    const before = git(origin, "rev-parse", "main");
    await expect(commitRelease(options(runner))).rejects.toThrow(new RegExp(`has parent ${start}, but the release was built from ${before}`));
    expect(git(origin, "rev-parse", "main")).toBe(before);
  });

  it("refuses, before any push, a release commit that would carry files outside data and website", async () => {
    const { origin, runner } = repositories();
    const built = build(runner);
    write(runner, "shared/omics/locator.ts", "export const built = 'edited';\n");
    git(runner, "add", "shared/omics/locator.ts");
    await expect(commitRelease(options(runner))).rejects.toThrow(/changes files outside data\/ and website\/: shared\/omics\/locator.ts/);
    expect(git(origin, "rev-parse", "main")).toBe(built);
  });

  it("logs the release commit, so a failed run shows which commit to publish by hand", async () => {
    const { other, runner } = repositories();
    const built = build(runner);
    mergeSharedChange(other);
    const lines: string[] = [];
    const { release } = await commitRelease({ ...options(runner), log: (line: string) => lines.push(line) });
    expect(lines[0]).toBe(`Release commit ${release}, made on ${built}.`);
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

  it("refuses a merge commit whose first parent is the built commit", () => {
    const { runner } = repositories();
    const built = build(runner);
    git(runner, "add", "-A", "data", "website");
    git(runner, "commit", "--quiet", "-m", `Cut release ${RELEASE} [skip ci]`);
    const release = git(runner, "rev-parse", "HEAD");
    // A merge that sits on the built commit and changes only release files, but is not the release commit.
    git(runner, "checkout", "--quiet", "--detach", built);
    git(runner, "merge", "--quiet", "--no-ff", "-m", `Cut release ${RELEASE} [skip ci]`, release);
    git(runner, "push", "--quiet", "origin", "HEAD:main");
    git(runner, "fetch", "--quiet", "origin");
    const merge = git(runner, "rev-parse", "HEAD");
    expect(git(runner, "rev-list", "--parents", "-n", "1", merge).split(" ")).toEqual([merge, built, release]);
    expect(git(runner, "diff", "--name-only", built, merge).split("\n").every((file) => /^(data|website)\//.test(file))).toBe(true);
    expect(() => verifyReleaseCommit({ commit: merge, cwd: runner })).toThrow(new RegExp(`has parent ${built} ${release}, but the release was built from ${built}`));
    expect(verifyReleaseCommit({ commit: release, cwd: runner })).toEqual({ release, built });
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

// release.yml does not run on pull requests, so its wiring is checked as text here.
describe("release workflow", () => {
  const workflow = (name: string) => fs.readFileSync(path.join(__dirname, "..", ".github", "workflows", name), "utf8");
  /** The steps of a workflow that has one job with steps, keyed by name. */
  const steps = (text: string) => text.split(/\n      - /).slice(1).map((block) => ({ name: /^name: (.+)$/m.exec(block)?.[1] ?? "", block }));
  const release = steps(workflow("release.yml"));
  const step = (name: string) => {
    const found = release.filter((candidate) => candidate.name === name);
    expect(found, name).toHaveLength(1);
    return found[0].block;
  };
  const COMMIT = "Commit the release to main";
  const CHECK = "Check the release commit sits on the commit the release was built from";
  const SERVING = "Publish the prepared release file and the release files";
  const KG = "Publish the knowledge-graph bundle (never replaces an existing asset)";
  const TAGS = "Check both tags name the release commit";
  const ADOPT = "Ask the website to adopt it";
  const SHA = "${{ steps.commit.outputs.sha }}";

  it("commits, checks the commit, publishes, checks the tags and only then asks the website to adopt", () => {
    const order = [COMMIT, CHECK, SERVING, KG, TAGS, ADOPT];
    expect(release.map(({ name }) => name).filter((name) => order.includes(name))).toEqual(order);
    // None of them runs when an earlier step failed or no release is pending.
    for (const name of order) expect(step(name), name).toMatch(/^ {8}if: steps\.pending\.outputs\.release == 'true'$/m);
  });

  it("makes the release commit with commit.mjs, and neither rebases nor pushes itself", () => {
    const text = workflow("release.yml");
    expect(step(COMMIT)).toContain("id: commit");
    expect(step(COMMIT)).toContain('sha=$(node scripts/release/commit.mjs commit "$RELEASE")');
    expect(step(COMMIT)).toContain('echo "sha=$sha" >> "$GITHUB_OUTPUT"');
    expect(text).not.toMatch(/git (rebase|push|commit|pull)/);
  });

  it("tags the commit the commit step returned, in every step that publishes", () => {
    const publishing = release.filter(({ block }) => /npm run \S+:publish/.test(block));
    expect(publishing.map(({ name }) => name)).toEqual([SERVING, KG]);
    for (const { name, block } of publishing) expect(block, name).toContain(`RELEASE_TARGET_SHA: ${SHA}`);
    expect(workflow("release.yml").split("RELEASE_TARGET_SHA:")).toHaveLength(3);
  });

  it("checks that commit before publishing, and both tags before the dispatch", () => {
    expect(step(CHECK).trimEnd().endsWith(`run: node scripts/release/commit.mjs verify "${SHA}"`)).toBe(true);
    // The bundle's tag is checked only when this release built a bundle (a content-only release reuses the last one's discrepancies).
    expect(step(TAGS)).toContain(`run: node scripts/release/commit.mjs verify "${SHA}" "serving/$RELEASE" $KG_TAG`);
    expect(step(TAGS)).toContain("KG_TAG: ${{ steps.candidate.outputs.reused != 'true' && format('kg/{0}', steps.candidate.outputs.next) || '' }}");
    expect(step(TAGS)).toContain("RELEASE: ${{ steps.candidate.outputs.next }}");
    expect(step(ADOPT)).toContain("run: node scripts/release/dispatch-website.mjs");
  });

  // A release cut by hand has no release commit of the kind `verify` checks. Its tags name the
  // merge commit, which the same run rebuilt the release from before the publish job may start.
  it("tags a hand-cut release at the commit data.yml rebuilt it from", () => {
    const text = workflow("data.yml");
    const publish = text.slice(text.indexOf("\n  publish:"));
    expect(publish).toContain("needs: [checks, release]");
    expect(publish).toContain("RELEASE_TARGET_SHA: ${{ github.sha }}");
    expect(publish).toMatch(/- uses: actions\/checkout@v4\n      - uses: actions\/setup-node/);
    const rebuild = text.slice(text.indexOf("\n  release:"), text.indexOf("\n  publish:"));
    expect(rebuild).toContain("run: npm run verify:package && git diff --exit-code -- data website");
  });
});
