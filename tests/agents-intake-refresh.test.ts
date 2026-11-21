// The intake agent's refresh of a conflicting pull request (intake.mjs --refresh), its queue of
// issues (--drain) and its waits on a rate limit. The fakes run without an API key or network.
// The fixture is pull request #352 (Add ProtCell from #350) as it stood on 21 Nov 2026, open and
// conflicting with main: its files, its batch and its store diff. The comments of issue #347 are
// the ones a run that ended on HTTP 429 left that day. One block runs real git against a bare
// repository in a temporary folder, for what fakes cannot show: the lease and the merge.
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterAll, describe, expect, it } from "vitest";
import {
  BOT_LOGIN,
  FAILED_MARKER,
  githubClient,
  HUMAN_LABEL,
  issueQueueState,
  LIMITS,
  main,
  parseRunMarker,
  queueState,
  queuedIssues,
  REFRESH_MARKER,
  refreshMarks,
  REFUSED_MARKER,
  renderRefreshComment,
  retryableError,
  retryDelaySeconds,
  retryingClient,
  REVISION_MARKER,
  revisedAlready,
  runGroup,
  runMarker,
  storeLines,
  tieToBatch,
  transientError,
  withApiRetry,
} from "../scripts/agents/intake.mjs";
import { Usage } from "../scripts/agents/discovery.mjs";

const FIXTURES = "tests/agents-intake-refresh-fixtures";
const INTAKE_FIXTURES = "tests/agents-intake-fixtures";
const REPO = "rewire-bio/rewire-benchmark-data";
const fixture = JSON.parse(fs.readFileSync(`${FIXTURES}/pull.json`, "utf8"));
const batchText = fs.readFileSync(`${FIXTURES}/batch.jsonl`, "utf8");
const batch = batchText.trim().split("\n").map((l) => JSON.parse(l));
const issue347 = JSON.parse(fs.readFileSync(`${FIXTURES}/issue-347-comments.json`, "utf8")).comments;
const BATCH_DIR = "data/omics/intake-350-20261121";
const STORE = "data/entities data/provenance";
const HEAD = fixture.pull.head_sha as string;
const MERGE_BASE = fixture.merge_base as string;
const BASE = "a".repeat(40);
const now = () => new Date("2026-11-21T12:00:00Z");
const quiet = () => {};
const sha256 = (text: string) => createHash("sha256").update(text).digest("hex");
const env = { GITHUB_REPOSITORY: REPO, GITHUB_RUN_ID: "77" };
const roots: string[] = [];
const tempRoot = (prefix = "intake-refresh-") => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), prefix));
  roots.push(root);
  return root;
};
afterAll(() => {
  for (const root of roots) fs.rmSync(root, { recursive: true, force: true });
});

describe("the store lines of a pull request", () => {
  const lines = storeLines(fixture.diff);

  it("reads the four lines #352 adds, and no file header", () => {
    expect(lines.removed).toEqual([]);
    expect(lines.added).toHaveLength(4);
    expect(lines.added.every((l) => l.startsWith("{"))).toBe(true);
    expect(storeLines("--- a/data/entities/models.jsonl\n+++ b/data/entities/models.jsonl\n@@ -3 +3 @@\n-{\"id\":\"x\"}\n+{\"id\":\"y\"}\n unchanged")).toEqual({ added: ['{"id":"y"}'], removed: ['{"id":"x"}'] });
  });

  it("ties them to the batch: one record line and one provenance line each, and the digest is the stored line's", () => {
    expect(tieToBatch(lines, batch, BATCH_DIR)).toEqual([]);
    // Record identity is the SHA-256 of the stored line; the provenance line carries it.
    for (const r of batch) {
      const stored = lines.added.find((l) => JSON.parse(l).id === r.id && JSON.parse(l).kind);
      const provenance = lines.added.map((l) => JSON.parse(l)).find((v) => v.id === r.id && !v.kind);
      expect(provenance).toEqual({ id: r.id, sha256: sha256(stored!), added_in: BATCH_DIR, added_by: "records:add", changed_by: [] });
    }
  });

  it("names a removed line, a record the batch does not hold, an edited line, another batch folder and a missing line", () => {
    expect(tieToBatch({ ...lines, removed: ['{"id":"old"}'] }, batch, BATCH_DIR)[0]).toContain("removes or changes 1 store line");
    expect(tieToBatch({ ...lines, added: [...lines.added, '{"id":"stray-record","kind":"model"}'] }, batch, BATCH_DIR)).toEqual(["it adds store lines for 1 record that batch.jsonl does not hold (stray-record)"]);
    const edited = lines.added.map((l) => (JSON.parse(l).kind === "model" ? l.replace('"name":"ProtCell"', '"name":"ProtCell 2"') : l));
    expect(edited).not.toEqual(lines.added);
    expect(tieToBatch({ ...lines, added: edited }, batch, BATCH_DIR)[0]).toMatch(/^the provenance of intake-350-20261121-model-protcell gives SHA-256 [0-9a-f]{64}, but its store line has [0-9a-f]{64}$/);
    expect(tieToBatch(lines, batch, "data/omics/intake-999-20261121")[0]).toContain(`names ${BATCH_DIR}, not data/omics/intake-999-20261121`);
    expect(tieToBatch({ ...lines, added: lines.added.filter((l) => JSON.parse(l).kind !== "model") }, batch, BATCH_DIR)[0]).toContain("has 0 record lines and 1 provenance line");
    expect(tieToBatch({ ...lines, added: [...lines.added, "not json"] }, batch, BATCH_DIR)).toEqual(["a line it adds to the store is not a record or a provenance line"]);
  });
});

/** A checkout of main with the pull request's batch folder on it (the git commands are fakes). */
function rootWithBatch() {
  const root = tempRoot();
  fs.mkdirSync(path.join(root, BATCH_DIR), { recursive: true });
  fs.writeFileSync(path.join(root, BATCH_DIR, "batch.jsonl"), batchText);
  return root;
}

function fakes({ pull = {} as Record<string, unknown>, pulls = null as Record<string, unknown>[] | null, files = fixture.files as any[], comments = [] as any[], fail = "", failOutput = "", oldDiff = fixture.diff as string, newDiff = fixture.diff as string } = {}) {
  const log: string[] = [];
  const sleeps: number[] = [];
  // One pull request unless `pulls` gives several; each read takes the next state of that pull request.
  const states = new Map<number, Record<string, unknown>[]>();
  const github = {
    pull: async (_r: string, number: number) => {
      log.push(`read #${number}`);
      const given = pulls?.find((p) => p.number === number) ?? pull;
      const queue = states.get(number);
      return { ...fixture.pull, number, ...given, ...(queue?.length ? queue.shift() : {}) };
    },
    pullFiles: async () => files,
    comments: async () => comments,
    compare: async (_r: string, base: string, head: string) => {
      log.push(`compare ${base}...${head}`);
      return { merge_base: MERGE_BASE };
    },
    openPulls: async () => [
      ...(pulls ?? [pull]).map((p) => ({ number: fixture.pull.number, author: BOT_LOGIN, head_ref: fixture.pull.head_ref, head_repo: REPO, ...p })),
      { number: 346, author: "timini", head_ref: "rare-disease-v2-records", head_repo: REPO },
      { number: 900, author: BOT_LOGIN, head_ref: "discovery/2026-11-21", head_repo: REPO },
      { number: 901, author: BOT_LOGIN, head_ref: "intake/issue-5", head_repo: "someone/fork" },
    ],
    addLabels: async (_r: string, number: number, labels: string[]) => {
      log.push(`label #${number} ${labels.join(",")}`);
    },
    comment: async (_r: string, number: number, body: string) => {
      log.push(`comment #${number} ${body.split("\n")[0]}`);
      bodies.push(body);
    },
  };
  const bodies: string[] = [];
  const run = (cmd: string, args: string[]) => {
    const line = [cmd, ...args].join(" ");
    log.push(line);
    if (fail && line.startsWith(fail)) return { ok: false, output: failOutput || `${fail}: refused` };
    if (line === "git rev-parse HEAD") return { ok: true, output: `${BASE}\n` };
    if (line.startsWith("git diff --cached")) return { ok: true, output: newDiff };
    if (line.startsWith("git diff")) return { ok: true, output: oldDiff };
    return { ok: true, output: "ok" };
  };
  const sleep = async (ms: number) => {
    sleeps.push(ms);
  };
  return { log, sleeps, bodies, states, deps: { github, run, now, sleep, log: quiet } };
}
const commandsOf = (log: string[]) => log.filter((l) => /^(git|npm|npx) /.test(l));
const writesOf = (log: string[]) => log.filter((l) => /^(label|comment) /.test(l) || /^git (commit|push)/.test(l));
const onBase = [`git fetch --quiet --depth 1 origin ${HEAD} ${MERGE_BASE}`, `git checkout --quiet --force --detach ${BASE}`, `git reset --quiet --hard ${BASE}`, "git clean -fdq -- data", `git checkout --quiet ${HEAD} -- ${BATCH_DIR}`, `git diff --unified=0 --no-color ${MERGE_BASE} ${HEAD} -- ${STORE}`];
const readded = [`npx tsx scripts/agents/intake-check.ts ${BATCH_DIR}/batch.jsonl`, `npm run -s records -- add ${BATCH_DIR}/batch.jsonl ${BATCH_DIR}`, "npm run -s records -- check", `git add -- ${BATCH_DIR} ${STORE}`, `git diff --cached --unified=0 --no-color ${BASE} -- ${STORE}`];
const LEASE_PUSH = `git push --force-with-lease=refs/heads/intake/issue-350:${HEAD} origin HEAD:refs/heads/intake/issue-350`;
const refreshOne = (f: ReturnType<typeof fakes>, extra: string[] = [], root = rootWithBatch()) => main(["--refresh", "--pr", "352", "--root", root, ...extra], env, f.deps);

describe("a live refresh, with fakes", () => {
  it("puts the batch folder on main, adds it again, and pushes one commit with a lease on the head it read", async () => {
    const f = fakes();
    const r = await refreshOne(f);
    expect(r.outcome).toBe("refreshed");
    expect(commandsOf(f.log)).toEqual([
      "git rev-parse HEAD",
      ...onBase,
      ...readded,
      expect.stringMatching(/^git commit -q -m Add ProtCell from #350 -m The batch folder of #352 as the pull request held it at 61df692, added again with records add on the base branch at aaaaaaa\./),
      LEASE_PUSH,
    ]);
    expect(f.log).toContain(`compare ${BASE}...${HEAD}`);
    expect(r.lines).toBe(4);
    // One comment, after the push; no label; the description is never written (the fake has no updatePull).
    expect(writesOf(f.log).slice(-2)).toEqual([LEASE_PUSH, "comment #352 The intake agent rebuilt this pull request on `main` at aaaaaaa, because it conflicted with it. The batch folder is as it was at 61df692, and the store gains the same 4 lines as before, so every record keeps its digest."]);
    expect(f.log.join("\n")).not.toMatch(/push (--force|-f) |--delete|label /);
    expect(f.bodies[0].split("\n").at(-1)).toBe(`<!-- ${REFRESH_MARKER}: ${JSON.stringify({ n: 1, base: BASE, from: HEAD })} -->`);
  });

  it("makes no model call and needs no API key", async () => {
    // The environment has no ANTHROPIC_API_KEY and the fakes have no model client: a call would throw.
    const f = fakes();
    expect("ANTHROPIC_API_KEY" in env).toBe(false);
    expect((await refreshOne(f)).outcome).toBe("refreshed");
    expect((f.deps as Record<string, unknown>).anthropic).toBeUndefined();
  });

  it("does not count as the one revision", async () => {
    const f = fakes();
    await refreshOne(f);
    // After a refresh the pull request has one commit, the description it had, and no revision.json.
    expect(revisedAlready({ ...fixture.pull, commits: 1 }, fixture.files)).toBe("");
    expect(f.bodies.join("\n")).not.toContain(REVISION_MARKER);
    expect(commandsOf(f.log).filter((l) => l.startsWith("git commit"))).toHaveLength(1);
    // A pull request that was revised keeps the two signs that travel with it.
    const revised = { ...fixture.pull, commits: 1, body: `${fixture.pull.body}\n\n<!-- ${REVISION_MARKER}: {"n":1} -->` };
    expect(revisedAlready(revised, fixture.files)).toContain("revision marker");
  });

  it("leaves a pull request that merges as it is", async () => {
    const f = fakes({ pull: { mergeable: true } });
    const r = await refreshOne(f);
    expect(r.outcome).toBe("skipped: it merges with its base branch as it is");
    expect(f.log).toEqual(["git rev-parse HEAD", "read #352"]);
  });

  it("never reads an answer GitHub has not given as merging: it asks again, a bounded number of times", async () => {
    const f = fakes({ pull: { mergeable: null } });
    const r = await refreshOne(f);
    expect(r.outcome).toBe("skipped: GitHub has not yet said whether it merges; the next run looks again");
    expect(f.sleeps).toEqual(Array(LIMITS.mergeablePolls).fill(LIMITS.mergeablePollSeconds * 1000));
    expect(f.log.slice(1)).toEqual(Array(LIMITS.mergeablePolls + 1).fill("read #352"));
    // Unknown twice, then conflicting: the refresh goes ahead.
    const later = fakes();
    later.states.set(352, [{ mergeable: null }, { mergeable: null }, { mergeable: false }]);
    expect((await refreshOne(later)).outcome).toBe("refreshed");
    expect(later.sleeps).toHaveLength(2);
  });

  it("looks only at an open pull request by the bot, on an intake branch of this repository, that no person holds", async () => {
    for (const [pull, why] of [
      [{ state: "closed" }, "the pull request is not open"],
      [{ author: "timini" }, `the author is timini, not ${BOT_LOGIN}`],
      [{ head_ref: "feature/x" }, "the head feature/x is not an intake branch of this repository"],
      [{ head_repo: "someone/fork" }, "the head intake/issue-350 is not an intake branch of this repository"],
      // The branch name is matched whole: a longer name that holds an intake branch name is not one.
      [{ head_ref: "x/intake/issue-5/y" }, "the head x/intake/issue-5/y is not an intake branch of this repository"],
      [{ head_ref: "intake/issue-350-again" }, "the head intake/issue-350-again is not an intake branch of this repository"],
      // The checkout is main, so a pull request against another branch is not rebuilt on it.
      [{ base_ref: "release-1" }, "its base branch is release-1, not main"],
      [{ labels: [HUMAN_LABEL] }, `the pull request is labelled ${HUMAN_LABEL}`],
    ] as const) {
      const f = fakes({ pull });
      expect((await refreshOne(f)).outcome).toBe(`skipped: ${why}`);
      expect(commandsOf(f.log)).toEqual(["git rev-parse HEAD"]);
      expect(writesOf(f.log)).toEqual([]);
    }
  });

  it("hands a pull request it may not rebuild to a person, before any command", async () => {
    const refreshed = { user: BOT_LOGIN, body: `rebuilt\n\n<!-- ${REFRESH_MARKER}: {"n":1} -->` };
    for (const [given, reason] of [
      [{ files: [...fixture.files, { filename: `${BATCH_DIR}/changes.jsonl`, status: "added" }] }, "it changes an existing record, and a refresh only adds records again"],
      [{ files: [...fixture.files, { filename: "scripts/omics/records.ts", status: "modified" }] }, "it touches files outside the batch folder and the store (scripts/omics/records.ts)"],
      [{ files: [...fixture.files, { filename: "data/omics/intake-350-20261122/batch.jsonl", status: "added" }] }, "it has 2 intake batch files, not one"],
      [{ files: fixture.files.map((x: any) => ({ ...x, filename: x.filename.replace("intake-350-", "intake-349-") })) }, "its batch folder data/omics/intake-349-20261121 is not one of issue #350, which its branch names"],
      [{ comments: Array(LIMITS.refreshesPerPull).fill(refreshed) }, `it was rebuilt ${LIMITS.refreshesPerPull} times already and conflicts again`],
      // A second commit that is not the intake's revision is a person's; one rebuilt commit would replace it.
      [{ pull: { commits: 2 } }, "it has 2 commits and was not revised by the intake agent, so someone added to it by hand"],
    ] as const) {
      const f = fakes(given as any);
      const r = await refreshOne(f);
      expect(r.outcome).toContain(`${HUMAN_LABEL}: ${reason}`);
      expect(commandsOf(f.log)).toEqual(["git rev-parse HEAD"]);
      expect(writesOf(f.log)).toEqual([`label #352 ${HUMAN_LABEL}`, expect.stringMatching(/^comment #352 The intake agent did not rebuild this pull request on its base branch: /)]);
    }
    // Refresh comments by someone else, or fewer than the limit, do not count against it.
    const some = fakes({ comments: [...Array(LIMITS.refreshesPerPull - 1).fill(refreshed), { ...refreshed, user: "timini" }] });
    expect((await refreshOne(some)).outcome).toBe("refreshed");
    expect(some.bodies[0]).toContain(`"n":${LIMITS.refreshesPerPull}`);
    // The count is of the pull request's whole life, and every other batch that merges takes one.
    expect(LIMITS.refreshesPerPull).toBeGreaterThanOrEqual(15);
    // Already rebuilt on the commit of main this run would build on: a commit on it cannot
    // conflict with it, so GitHub's answer is old or main has moved. Not rebuilt twice, not labelled.
    const same = fakes({ comments: [{ user: BOT_LOGIN, body: renderRefreshComment({ kind: "refreshed", pull: fixture.pull, base: BASE, lines: 4 }) }] });
    expect((await refreshOne(same)).outcome).toBe(`skipped: it was rebuilt on ${BASE.slice(0, 7)} already, which is the commit this run would build on; the next run looks again`);
    expect(commandsOf(same.log)).toEqual(["git rev-parse HEAD"]);
    expect(writesOf(same.log)).toEqual([]);
    const moved = fakes({ comments: [{ user: BOT_LOGIN, body: renderRefreshComment({ kind: "refreshed", pull: fixture.pull, base: "b".repeat(40), lines: 4 }) }] });
    expect((await refreshOne(moved)).outcome).toBe("refreshed");
    // A revised pull request has two commits, the marker and revision.json: it is rebuilt.
    const revised = fakes({ pull: { commits: 2, body: `x\n\n<!-- ${REVISION_MARKER}: {"n":1} -->` } });
    expect((await refreshOne(revised)).outcome).toBe("refreshed");
    const withFile = fakes({ pull: { commits: 2 }, files: [...fixture.files, { filename: `${BATCH_DIR}/revision.json`, status: "added" }] });
    expect((await refreshOne(withFile)).outcome).toBe("refreshed");
  });

  it("hands over a pull request whose store lines are not its batch, without running the store tools", async () => {
    const edited = fixture.diff.replace('"name":"ProtCell"', '"name":"ProtCell (edited)"');
    expect(edited).not.toBe(fixture.diff);
    const f = fakes({ oldDiff: edited });
    const r = await refreshOne(f);
    expect(r.outcome).toBe(`${HUMAN_LABEL}: the store lines the pull request adds are not its batch as records add writes it: the provenance of intake-350-20261121-model-protcell gives SHA-256 ${JSON.parse(storeLines(fixture.diff).added.find((l) => l.includes('"added_in"') && l.includes("model-protcell"))!).sha256}, but its store line has ${sha256(storeLines(edited).added.find((l) => l.includes("(edited)"))!)}`);
    expect(commandsOf(f.log)).toEqual(["git rev-parse HEAD", ...onBase]);
    expect(writesOf(f.log).map((l) => l.split(" ")[0])).toEqual(["label", "comment"]);
  });

  it("fails the run and does not label the pull request the first time a store check fails: the fault may be the tool's", async () => {
    for (const [fail, step] of [["npx tsx scripts/agents/intake-check.ts", "intake-check"], ["npm run -s records -- add", "records add"], ["npm run -s records -- check", "records check"]] as const) {
      const f = fakes({ fail, failOutput: "error: Failed to download `pyshacl`: connection reset by peer" });
      const r = await refreshOne(f);
      expect(r.outcome).toBe(`failed: ${step}`);
      expect(r.label).toBeNull();
      expect(writesOf(f.log)).toEqual([expect.stringMatching(/^comment #352 The intake agent could not rebuild this pull request on its base branch: `.*` failed on the batch added to the base branch as it is now\. It is the first time this step failed here/)]);
      expect(f.bodies[0]).toContain("Failed to download");
      expect(f.bodies[0]).toContain("the pull request is not labelled");
      expect(refreshMarks([{ user: BOT_LOGIN, body: f.bodies[0] }])).toEqual([{ kind: "failed", base: BASE, step }]);
    }
  });

  it("hands over and fails the run when the same store check fails a second time", async () => {
    const first = fakes({ fail: "npm run -s records -- add", failOutput: "Batch cannot replace or duplicate record: intake-350-20261121-source-x" });
    await refreshOne(first);
    const before = [{ user: BOT_LOGIN, body: first.bodies[0] }];
    const f = fakes({ fail: "npm run -s records -- add", failOutput: "Batch cannot replace or duplicate record: intake-350-20261121-source-x", comments: before });
    const r = await refreshOne(f);
    expect(r.outcome).toBe("failed: records add");
    expect(r.label).toBe(HUMAN_LABEL);
    expect(writesOf(f.log)).toEqual([`label #352 ${HUMAN_LABEL}`, expect.stringMatching(/^comment #352 The intake agent did not rebuild this pull request on its base branch: `records add` failed on the batch added to the base branch as it is now\./)]);
    expect(f.bodies[0]).toContain("Batch cannot replace or duplicate record");
    // Another step failing is the first failure of that step.
    const other = fakes({ fail: "npm run -s records -- check", comments: before });
    expect((await refreshOne(other)).label).toBeNull();
    // A failure before the last rebuild is not held against the pull request, and neither is one
    // somebody else's comment claims.
    const rebuilt = { user: BOT_LOGIN, body: renderRefreshComment({ kind: "refreshed", pull: fixture.pull, base: "b".repeat(40), lines: 4 }) };
    const since = fakes({ fail: "npm run -s records -- add", comments: [...before, rebuilt] });
    expect((await refreshOne(since)).label).toBeNull();
    const forged = fakes({ fail: "npm run -s records -- add", comments: [{ ...before[0], user: "timini" }] });
    expect((await refreshOne(forged)).label).toBeNull();
    // A sound pull request with one failure behind it is rebuilt as usual.
    const sound = fakes({ comments: before });
    expect((await refreshOne(sound)).outcome).toBe("refreshed");
  });

  it("pushes nothing when the rebuilt store does not gain exactly the lines the pull request held", async () => {
    const other = fixture.diff.replace('"added_by":"records:add"', '"added_by":"records:add-v2"');
    for (const newDiff of [other, `${fixture.diff}+{"id":"one-more","kind":"source"}\n`, `${fixture.diff}-{"id":"taken-away","kind":"source"}\n`, fixture.diff.split("\n").filter((l: string) => !l.includes('"kind":"model"')).join("\n")]) {
      const f = fakes({ newDiff });
      const r = await refreshOne(f);
      expect(r.outcome).toBe("failed: store lines");
      expect(r.reason).toContain("so a rebuild would change a record or its digest");
      expect(commandsOf(f.log)).toEqual(["git rev-parse HEAD", ...onBase, ...readded]);
      expect(writesOf(f.log).map((l) => l.split(" ")[0])).toEqual(["label", "comment"]);
    }
  });

  it("stops when the checkout is not main, GitHub names no common commit, or the batch folder cannot be taken", async () => {
    const head = fakes();
    head.deps.run = (cmd: string, args: string[]) => ({ ok: true, output: cmd === "git" && args[0] === "rev-parse" ? HEAD : "ok" });
    expect((await refreshOne(head)).reason).toBe("the checkout is the pull request head, not the base branch");
    const none = fakes();
    none.deps.github.compare = async () => ({ merge_base: "" });
    expect((await refreshOne(none)).outcome).toBe("failed: checkout");
    expect(commandsOf(none.log)).toEqual(["git rev-parse HEAD"]);
    const f = fakes({ fail: `git checkout --quiet ${HEAD}` });
    expect((await refreshOne(f)).outcome).toBe("failed: checkout");
    expect(commandsOf(f.log).some((l) => /^(npm|npx) /.test(l))).toBe(false);
  });

  it("does nothing more when the branch moved while it ran: the lease refuses the push, and no person is asked", async () => {
    const f = fakes({ fail: "git push", failOutput: " ! [rejected]        HEAD -> intake/issue-350 (stale info)\nerror: failed to push some refs to 'origin'" });
    const r = await refreshOne(f);
    expect(r.outcome).toBe("skipped: the branch moved while the refresh ran, so nothing was pushed; the next run looks again");
    expect(writesOf(f.log).at(-1)).toBe(LEASE_PUSH);
    expect(f.log.join("\n")).not.toMatch(/label |comment /);
  });

  it("fails the run once, with one comment and no label, when GitHub refuses the push over a workflow file main changed", async () => {
    // The token's limit, not a fault of the pull request: it stays open to a later refresh.
    const failOutput = " ! [remote rejected] HEAD -> intake/issue-350 (refusing to allow a GitHub App to create or update workflow `.github/workflows/intake.yml` without `workflows` permission)";
    const f = fakes({ fail: "git push", failOutput });
    const r = await refreshOne(f);
    expect(r.outcome).toBe("failed: git push refused over a workflow file");
    expect(r.reason).toContain("the rewire-bot app token may not write workflows");
    expect(writesOf(f.log).slice(-2)).toEqual([LEASE_PUSH, expect.stringMatching(/^comment #352 The intake agent rebuilt this pull request on its base branch but could not push it\./)]);
    expect(f.log.join("\n")).not.toMatch(/label /);
    expect(f.bodies[0]).toContain("`refresh_pr`");
    const refused = [{ user: BOT_LOGIN, body: f.bodies[0] }];
    expect(refreshMarks(refused)).toEqual([{ kind: "refused", base: BASE, step: "" }]);
    // The run after the next push to main leaves that pull request, and does not fail on it again.
    const next = fakes({ fail: "git push", failOutput, comments: refused });
    const all = await main(["--refresh", "--root", rootWithBatch()], env, next.deps);
    expect(all.pulls.map((p: any) => p.outcome)).toEqual(["skipped: an earlier push of its rebuild was refused over a workflow file; a manual run that names this pull request tries again"]);
    expect(commandsOf(next.log)).toEqual(["git rev-parse HEAD"]);
    expect(writesOf(next.log)).toEqual([]);
    // A manual run that names it tries the push again. Refused again, it fails and adds no second comment.
    const again = fakes({ fail: "git push", failOutput, comments: refused });
    expect((await refreshOne(again)).outcome).toBe("failed: git push refused over a workflow file");
    expect(again.log.join("\n")).not.toMatch(/label |comment /);
    const allowed = fakes({ comments: refused });
    expect((await refreshOne(allowed)).outcome).toBe("refreshed");
    // After a rebuild that was pushed, the refusal is over: automatic runs look at it again.
    const after = fakes({ comments: [...refused, { user: BOT_LOGIN, body: allowed.bodies[0].replaceAll(BASE, "b".repeat(40)) }] });
    expect((await main(["--refresh", "--root", rootWithBatch()], env, after.deps)).pulls[0].outcome).toBe("refreshed");
    // Any other refused push is a failed step: a comment the first time, a person the second.
    const other = fakes({ fail: "git push", failOutput: "remote: Repository not found." });
    expect((await refreshOne(other)).outcome).toBe("failed: git push");
    expect(writesOf(other.log).slice(-2).map((l) => l.split(" ")[0])).toEqual(["git", "comment"]);
    const twice = fakes({ fail: "git push", failOutput: "remote: Repository not found.", comments: [{ user: BOT_LOGIN, body: other.bodies[0] }] });
    expect((await refreshOne(twice)).outcome).toBe("failed: git push");
    expect(writesOf(twice.log).slice(-2).map((l) => l.split(" ")[0])).toEqual(["label", "comment"]);
  });

  it("in report-only mode rebuilds and checks, and writes nothing to GitHub or the branch", async () => {
    const f = fakes();
    const out = tempRoot();
    const r = await refreshOne(f, ["--report-only", "--out", out]);
    expect(r.outcome).toBe("ready: refresh not pushed in this mode");
    expect(commandsOf(f.log)).toEqual(["git rev-parse HEAD", ...onBase, ...readded]);
    expect(writesOf(f.log)).toEqual([]);
    expect(JSON.parse(fs.readFileSync(path.join(out, "result.json"), "utf8")).pulls[0]).toMatchObject({ pr: 352, lines: 4, base: BASE, pushed: false });
    // What it would write for a pull request it hands over is in the result, not on GitHub. It
    // does not fail the run: nothing labels the pull request, so it would fail after every push.
    const once = fakes({ fail: "npm run -s records -- add" });
    const o = await refreshOne(once, ["--report-only"]);
    expect(o.outcome).toBe("not rebuilt: `records add` failed on the batch added to the base branch as it is now");
    expect(o.label).toBeNull();
    expect(o.comment).toContain("the pull request is not labelled");
    expect(writesOf(once.log)).toEqual([]);
    const handed = fakes({ fail: "npm run -s records -- add", comments: [{ user: BOT_LOGIN, body: `x\n\n<!-- ${FAILED_MARKER}: {"step":"records add","base":"${BASE}"} -->` }] });
    const h = await refreshOne(handed, ["--report-only"]);
    expect(h.outcome).toBe(`${HUMAN_LABEL}: \`records add\` failed on the batch added to the base branch as it is now`);
    expect(h.label).toBe(HUMAN_LABEL);
    expect(h.comment).toContain("left for a person");
    expect(writesOf(handed.log)).toEqual([]);
  });

  it("never refreshes live without the store checks, and --pr needs a job", async () => {
    await expect(main(["--refresh", "--pr", "352", "--no-store-checks"], env, fakes().deps)).rejects.toThrow("a live --refresh cannot use --no-store-checks");
    await expect(main(["--pr", "352"], env, fakes().deps)).rejects.toThrow("--pr needs --revise or --refresh");
    await expect(main(["--refresh", "--revise", "--pr", "352"], env, fakes().deps)).rejects.toThrow("separate runs");
  });

  it("without --pr, looks at every open intake pull request by the bot and at no other", async () => {
    const pulls = [{ number: 354, head_ref: "intake/issue-349", mergeable: true }, { number: 352 }, { number: 338, head_ref: "intake/issue-283", labels: [HUMAN_LABEL] }];
    const f = fakes({ pulls });
    const r = await main(["--refresh", "--root", rootWithBatch()], env, f.deps);
    expect(f.log.filter((l) => l.startsWith("read "))).toEqual(["read #338", "read #352", "read #354"]);
    expect(r.pulls.map((p: any) => `${p.pr} ${p.outcome.split(":")[0]}`)).toEqual(["338 skipped", "352 refreshed", "354 skipped"]);
    // main is read once, before the first pull request, not again after a commit was made on it.
    expect(f.log.filter((l) => l === "git rev-parse HEAD")).toHaveLength(1);
    expect(f.log.indexOf("git rev-parse HEAD")).toBeLessThan(f.log.indexOf("read #338"));
    expect(r.outcome).toBe("1 of 3 open intake pull requests refreshed");
  });

  it("goes on to the next pull request when one cannot be read, and fails the run", async () => {
    const f = fakes({ pulls: [{ number: 352 }, { number: 354, head_ref: "intake/issue-349" }] });
    const read = f.deps.github.pull;
    f.deps.github.pull = async (r: string, n: number) => {
      if (n === 352) throw Object.assign(new Error("GET /pulls/352: 502 Bad Gateway"), { status: 502 });
      return read(r, n);
    };
    // #354's branch names issue 349, and the fixture files are those of issue 350: handed over.
    const r = await main(["--refresh", "--root", rootWithBatch()], env, f.deps);
    expect(r.pulls.map((p: any) => p.outcome.split(":")[0])).toEqual(["failed", HUMAN_LABEL]);
    expect(r.outcome).toBe("failed: 1 of 2 pull requests (#352)");
  });
});

describe("the refresh dry run", () => {
  it("ties the fixture's store diff to its batch and runs nothing", async () => {
    const out = tempRoot();
    const commands: string[] = [];
    const r = await main(["--refresh", "--dry-run", "--out", out], {}, { now, log: quiet, run: (cmd: string) => (commands.push(cmd), { ok: true, output: "" }) });
    expect(r.outcome).toBe("ready: refresh not pushed in this mode");
    expect(commands).toEqual([]);
    expect(JSON.parse(fs.readFileSync(path.join(out, "result.json"), "utf8"))).toMatchObject({ outcome: "ready: refresh not pushed in this mode", pulls: [{ pr: 352, lines: 4 }] });
  });
});

describe("the comments of a refresh", () => {
  it("say what happened in plain text", () => {
    const done = renderRefreshComment({ kind: "refreshed", pull: fixture.pull, base: BASE, lines: 4, n: 2, runUrl: "https://example.org/run" });
    expect(done).toContain("This is not a revision: no model was called and no field changed.");
    expect(done).toContain("Run: https://example.org/run");
    const handed = renderRefreshComment({ kind: "handed over", reason: "it has 2 intake batch files, not one" });
    expect(handed).toContain("It is labelled `needs-tim` and left for a person.");
    expect(handed).toContain("A refresh calls no model and changes no record.");
    expect(`${done}${handed}`).not.toMatch(/[–—]/);
  });
});

// ---------- Real git: a bare origin, a conflicting intake branch, and the lease ----------

describe("a refresh against a real repository", () => {
  const git = (cwd: string, ...args: string[]) => execFileSync("git", args, { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();
  const MODELS = "data/entities/models.jsonl";
  const PROVENANCE = "data/provenance/records/0.jsonl";
  const DIR = "data/omics/intake-7-20261121";
  const DIR8 = "data/omics/intake-8-20261121";
  const record = (id: string) => JSON.stringify({ id, kind: "model", name: id });
  const provenance = (id: string, dir: string) => JSON.stringify({ id, sha256: sha256(record(id)), added_in: dir, added_by: "records:add", changed_by: [] });
  const sorted = (lines: string[]) => `${[...lines].sort((a, b) => (JSON.parse(a).id < JSON.parse(b).id ? -1 : 1)).join("\n")}\n`;
  /** What records add does to the store, for this test: every batch line and its provenance line, files kept sorted by id. */
  const add = (root: string, ids: string[], dir: string) => {
    const read = (file: string) => fs.readFileSync(path.join(root, file), "utf8").trim().split("\n");
    fs.writeFileSync(path.join(root, MODELS), sorted([...read(MODELS), ...ids.map(record)]));
    fs.writeFileSync(path.join(root, PROVENANCE), sorted([...read(PROVENANCE), ...ids.map((id) => provenance(id, dir))]));
  };

  /**
   * origin: main with two records. intake/issue-7 adds intake-7-a from there (the bot's pull
   * request). Then main gains intake-6-a, which sorts next to it, so the two conflict. Returns
   * a clone on main as it is now, as the workflow checks it out.
   */
  function scene() {
    const top = tempRoot("intake-refresh-git-");
    const origin = path.join(top, "origin.git");
    const seed = path.join(top, "seed");
    const work = path.join(top, "work");
    fs.mkdirSync(origin);
    git(origin, "init", "--quiet", "--bare", "--initial-branch=main");
    // A shallow fetch of one commit by its SHA, as GitHub allows.
    git(origin, "config", "uploadpack.allowAnySHA1InWant", "true");
    git(top, "clone", "--quiet", `file://${origin}`, seed);
    const identity = (dir: string) => {
      git(dir, "config", "user.name", "Test");
      git(dir, "config", "user.email", "test@example.org");
      git(dir, "config", "commit.gpgsign", "false");
    };
    identity(seed);
    const commit = (message: string) => {
      git(seed, "add", "-A");
      git(seed, "commit", "--quiet", "-m", message);
      return git(seed, "rev-parse", "HEAD");
    };
    fs.mkdirSync(path.join(seed, "data/entities"), { recursive: true });
    fs.mkdirSync(path.join(seed, "data/provenance/records"), { recursive: true });
    fs.writeFileSync(path.join(seed, MODELS), sorted([record("a-first"), record("z-last")]));
    fs.writeFileSync(path.join(seed, PROVENANCE), sorted([provenance("a-first", "data/omics/seed"), provenance("z-last", "data/omics/seed")]));
    const mergeBase = commit("Seed the store");
    git(seed, "push", "--quiet", "origin", "HEAD:refs/heads/main");
    // The intake's pull request.
    git(seed, "checkout", "--quiet", "-b", "intake/issue-7");
    fs.mkdirSync(path.join(seed, DIR), { recursive: true });
    fs.writeFileSync(path.join(seed, DIR, "batch.jsonl"), `${record("intake-7-a")}\n`);
    fs.writeFileSync(path.join(seed, DIR, "notes.md"), "Notes of the first run.\n");
    add(seed, ["intake-7-a"], DIR);
    const head = commit("Add intake-7-a from #7");
    git(seed, "push", "--quiet", "origin", "intake/issue-7");
    // A second intake pull request, from the same main.
    git(seed, "checkout", "--quiet", "-b", "intake/issue-8", mergeBase);
    fs.mkdirSync(path.join(seed, DIR8), { recursive: true });
    fs.writeFileSync(path.join(seed, DIR8, "batch.jsonl"), `${record("intake-8-a")}\n`);
    add(seed, ["intake-8-a"], DIR8);
    const head8 = commit("Add intake-8-a from #8");
    git(seed, "push", "--quiet", "origin", "intake/issue-8");
    // Another batch merges into main.
    git(seed, "checkout", "--quiet", "main");
    add(seed, ["intake-6-a"], "data/omics/intake-6-20261121");
    const base = commit("Add intake-6-a from #6");
    git(seed, "push", "--quiet", "origin", "main");
    git(top, "clone", "--quiet", "--depth", "1", "--branch", "main", `file://${origin}`, work);
    identity(work);
    const added: string[][] = [];
    const run = (cmd: string, args: string[]) => {
      if (cmd !== "git") {
        // intake-check and records check pass; records add writes the store as the CLI would.
        if (args.includes("add")) {
          const dir = args.at(-1)!;
          const ids = fs.readFileSync(path.join(work, dir, "batch.jsonl"), "utf8").trim().split("\n").map((l) => JSON.parse(l).id);
          added.push(ids);
          add(work, ids, dir);
        }
        return { ok: true, output: "ok" };
      }
      try {
        return { ok: true, output: execFileSync("git", args, { cwd: work, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }) };
      } catch (e: any) {
        return { ok: false, output: `${e.stdout ?? ""}${e.stderr ?? ""}` };
      }
    };
    const log: string[] = [];
    const pull = { number: 70, title: "Add intake-7-a from #7", body: "First description.", state: "open", author: BOT_LOGIN, head_ref: "intake/issue-7", head_sha: head, head_repo: REPO, commits: 1, labels: [], mergeable: false, base_ref: "main" };
    const pull8 = { ...pull, number: 80, title: "Add intake-8-a from #8", head_ref: "intake/issue-8", head_sha: head8 };
    const github = {
      pull: async (_r: string, number: number) => (number === 80 ? pull8 : pull),
      pullFiles: async (_r: string, number: number) => (number === 80 ? [MODELS, PROVENANCE, `${DIR8}/batch.jsonl`] : [MODELS, PROVENANCE, `${DIR}/batch.jsonl`, `${DIR}/notes.md`]).map((filename) => ({ filename, status: filename.startsWith("data/omics/") ? "added" : "modified" })),
      openPulls: async () => [pull, pull8].map((p) => ({ number: p.number, author: p.author, head_ref: p.head_ref, head_repo: p.head_repo })),
      comments: async () => [],
      compare: async () => ({ merge_base: mergeBase }),
      addLabels: async (_r: string, _n: number, labels: string[]) => void log.push(`label ${labels.join(",")}`),
      comment: async (_r: string, _n: number, body: string) => void log.push(`comment ${body.split("\n")[0]}`),
    };
    return { origin, seed, work, head, head8, base, mergeBase, added, log, pull, deps: { github, run, now, sleep: async () => {}, log: quiet } };
  }

  it("conflicts before, and after the refresh is one commit on main that merges, with every store line as it was", async () => {
    const s = scene();
    // The branch as pushed does not merge into main.
    expect(() => git(s.seed, "merge", "--no-edit", "intake/issue-7")).toThrow();
    git(s.seed, "merge", "--abort");
    const before = git(s.origin, "diff", "--unified=0", s.mergeBase, s.head, "--", "data/entities", "data/provenance");

    const r = await main(["--refresh", "--pr", "70", "--root", s.work], env, s.deps);
    expect(r.outcome).toBe("refreshed");
    expect(s.added).toEqual([["intake-7-a"]]);
    const tip = git(s.origin, "rev-parse", "refs/heads/intake/issue-7");
    expect(tip).not.toBe(s.head);
    // One commit, whose parent is main as it is now.
    expect(git(s.origin, "rev-parse", `${tip}^`)).toBe(s.base);
    expect(git(s.origin, "rev-list", "--count", `${s.base}..${tip}`)).toBe("1");
    expect(git(s.origin, "log", "-1", "--format=%s", tip)).toBe("Add intake-7-a from #7");
    // It changes the batch folder and the two store files, and nothing else.
    expect(git(s.origin, "diff", "--name-only", s.base, tip).split("\n").sort()).toEqual([MODELS, `${DIR}/batch.jsonl`, `${DIR}/notes.md`, PROVENANCE].sort());
    // The batch folder is byte for byte the pull request's.
    for (const name of ["batch.jsonl", "notes.md"]) expect(git(s.origin, "show", `${tip}:${DIR}/${name}`)).toBe(git(s.origin, "show", `${s.head}:${DIR}/${name}`));
    // The store gains the same lines as before: same record line, same provenance line, same digest.
    const after = git(s.origin, "diff", "--unified=0", s.base, tip, "--", "data/entities", "data/provenance");
    expect(storeLines(after).added.sort()).toEqual(storeLines(before).added.sort());
    expect(storeLines(after).removed).toEqual([]);
    expect(storeLines(after).added).toContain(provenance("intake-7-a", DIR));
    // main's later record is there too, and the branch now merges.
    expect(git(s.origin, "show", `${tip}:${MODELS}`)).toBe(sorted(["a-first", "intake-6-a", "intake-7-a", "z-last"].map(record)).trim());
    git(s.seed, "fetch", "--quiet", "origin");
    git(s.seed, "merge", "--quiet", "--no-edit", "--ff-only", tip);
    expect(s.log).toEqual([expect.stringMatching(/^comment The intake agent rebuilt this pull request on `main` at /)]);
  });

  it("rebuilds two conflicting pull requests in one run each on main, not one on top of the other", async () => {
    const s = scene();
    const r = await main(["--refresh", "--root", s.work], env, s.deps);
    expect(r.pulls.map((p: any) => `${p.pr} ${p.outcome}`)).toEqual(["70 refreshed", "80 refreshed"]);
    expect(r.pulls.map((p: any) => p.base)).toEqual([s.base, s.base]);
    for (const [branch, dir, id, other] of [["intake/issue-7", DIR, "intake-7-a", "intake-8-a"], ["intake/issue-8", DIR8, "intake-8-a", "intake-7-a"]]) {
      const tip = git(s.origin, "rev-parse", `refs/heads/${branch}`);
      // One commit on main as it was when the run started.
      expect(git(s.origin, "rev-parse", `${tip}^`)).toBe(s.base);
      // Its own batch folder and the two store files, and nothing of the other pull request.
      const changed = git(s.origin, "diff", "--name-only", s.base, tip).split("\n");
      expect(changed.filter((f) => f.startsWith("data/omics/")).every((f) => f.startsWith(`${dir}/`))).toBe(true);
      expect(changed.filter((f) => !f.startsWith("data/omics/")).sort()).toEqual([MODELS, PROVENANCE].sort());
      const lines = storeLines(git(s.origin, "diff", "--unified=0", s.base, tip, "--", "data/entities", "data/provenance"));
      expect(lines.added.sort()).toEqual([record(id), provenance(id, dir)].sort());
      expect(git(s.origin, "show", `${tip}:${MODELS}`)).not.toContain(other);
    }
  });

  it("puts the store back as main has it with git restore, removing a store file only the batch made", async () => {
    // What the revision does between its two commits (intake.mjs, step 6).
    const s = scene();
    await main(["--refresh", "--pr", "70", "--report-only", "--root", s.work], env, s.deps);
    const shard = "data/provenance/records/f.jsonl";
    fs.writeFileSync(path.join(s.work, shard), `${provenance("intake-7-b", DIR)}\n`);
    git(s.work, "add", "--", shard);
    expect(git(s.work, "status", "--porcelain", "--", "data/entities", "data/provenance")).not.toBe("");
    git(s.work, "restore", "--source", s.base, "--staged", "--worktree", "--", "data/entities", "data/provenance");
    expect(fs.existsSync(path.join(s.work, shard))).toBe(false);
    expect(git(s.work, "status", "--porcelain", "--", "data/entities", "data/provenance")).toBe("");
    expect(fs.readFileSync(path.join(s.work, MODELS), "utf8")).toBe(sorted(["a-first", "intake-6-a", "z-last"].map(record)));
    // The batch folder is still there, staged, for the commit.
    expect(git(s.work, "status", "--porcelain", "--", DIR)).toContain(`${DIR}/batch.jsonl`);
  });

  it("pushes nothing when the branch moved after the pull request was read", async () => {
    const s = scene();
    // Someone pushes to the branch between the read of the pull request and the push.
    git(s.seed, "checkout", "--quiet", "intake/issue-7");
    fs.appendFileSync(path.join(s.seed, DIR, "notes.md"), "A later note.\n");
    git(s.seed, "commit", "--quiet", "-am", "Edit the notes");
    git(s.seed, "push", "--quiet", "origin", "intake/issue-7");
    const moved = git(s.seed, "rev-parse", "HEAD");
    const r = await main(["--refresh", "--pr", "70", "--root", s.work], env, s.deps);
    expect(r.outcome).toBe("skipped: the branch moved while the refresh ran, so nothing was pushed; the next run looks again");
    expect(git(s.origin, "rev-parse", "refs/heads/intake/issue-7")).toBe(moved);
    expect(s.log).toEqual([]);
  });

  it("starts from a clean main each time: nothing of one pull request is left in the tree for the next", async () => {
    const s = scene();
    fs.mkdirSync(path.join(s.work, "data/omics/intake-5-20261120"), { recursive: true });
    fs.writeFileSync(path.join(s.work, "data/omics/intake-5-20261120/batch.jsonl"), `${record("intake-5-a")}\n`);
    add(s.work, ["intake-5-a"], "data/omics/intake-5-20261120");
    git(s.work, "add", "-A");
    const r = await main(["--refresh", "--pr", "70", "--report-only", "--root", s.work], env, s.deps);
    expect(r.outcome).toBe("ready: refresh not pushed in this mode");
    expect(fs.existsSync(path.join(s.work, "data/omics/intake-5-20261120"))).toBe(false);
    expect(fs.readFileSync(path.join(s.work, MODELS), "utf8")).toBe(sorted(["a-first", "intake-6-a", "intake-7-a", "z-last"].map(record)));
    expect(git(s.origin, "rev-parse", "refs/heads/intake/issue-7")).toBe(s.head);
  });
});

// ---------- The queue ----------

describe("the marker on the intake's issue comments", () => {
  it("round-trips, and nothing in an outcome can close the comment early", () => {
    const marker = runMarker({ outcome: "error: 429 --> <b>rate limit</b>", retry: true });
    expect(marker.match(/-->/g)).toHaveLength(1);
    expect(parseRunMarker(`The intake agent wrote a batch.\n\n${marker}`)).toEqual({ outcome: "error: 429 --> <b>rate limit</b>", retry: true });
    expect(parseRunMarker(`${marker}\n\nmore text`)).toBeNull();
    expect(parseRunMarker("The intake agent opened a pull request.")).toBeNull();
    expect(runMarker({ outcome: "opened" })).toBe('<!-- intake-run: {"outcome":"opened","retry":false} -->');
  });
});

describe("where an issue stands in the queue", () => {
  const bot = (body: string) => ({ user: BOT_LOGIN, body });
  const failed = bot(`The intake agent wrote a batch but \`the intake run\` failed, so no pull request was opened.\n\n${runMarker({ outcome: "error: 529 overloaded", retry: true })}`);
  const skipped = bot(`The intake agent did not open a pull request: the request is out of scope for the database.\n\n${runMarker({ outcome: "skipped: out of scope" })}`);

  it("is new when the intake never answered, whatever anyone else wrote", () => {
    expect(queueState([])).toEqual({ state: "new", attempts: 0 });
    expect(queueState([{ user: "timini", body: "The intake agent should look at this." }, { user: BOT_LOGIN, body: "Filed by the discovery scan." }])).toEqual({ state: "new", attempts: 0 });
  });

  it("picks up issue #347, whose run ended on HTTP 429 before the marker existed", () => {
    expect(issue347).toHaveLength(1);
    expect(issue347[0].body).toContain("Number of concurrent connections has exceeded your rate limit");
    expect(parseRunMarker(issue347[0].body)).toBeNull();
    expect(queueState(issue347)).toEqual({ state: "retry", attempts: 1 });
  });

  it("is done after a final answer, also an old one without a marker", () => {
    expect(queueState([skipped]).state).toBe("done");
    expect(queueState([bot("The intake agent opened https://github.com/x/y/pull/1 with 2 records (estimated cost $0.2100). It needs a review before merging.")]).state).toBe("done");
    expect(queueState([bot("The intake agent wrote a batch but `records add` failed, so no pull request was opened.\n\n```\nBatch cannot replace or duplicate record: x-429\n```")]).state).toBe("done");
    // A failure that was retried and then answered for good is done.
    expect(queueState([failed, skipped])).toEqual({ state: "done", attempts: 1 });
  });

  it("is tried again after a failure another run may get past, a bounded number of times", () => {
    expect(queueState([failed])).toEqual({ state: "retry", attempts: 1 });
    expect(queueState(Array(LIMITS.queueAttempts - 1).fill(failed)).state).toBe("retry");
    expect(queueState(Array(LIMITS.queueAttempts).fill(failed))).toEqual({ state: "exhausted", attempts: LIMITS.queueAttempts });
    // Without the time of the label, every attempt counts. With it, a label added again starts the count at none (below).
    expect(queueState([...issue347, failed, failed]).state).toBe("exhausted");
  });

  it("lists the labelled issues with no pull request and no final answer, lowest first", async () => {
    const asked: string[] = [];
    const gh = {
      labelledIssues: async (_r: string, label: string) => (label === "entity-request" ? [350, 349, 348, 347, 283, 360] : [361, 350]).map((number) => ({ number })),
      pullsFor: async (_r: string, branch: string) => {
        asked.push(branch);
        return branch.endsWith("-350") ? [{ state: "open" }] : branch.endsWith("-348") ? [{ state: "closed", merged_at: "2026-11-21T10:00:00Z" }] : branch.endsWith("-349") ? [{ state: "closed", merged_at: null }] : [];
      },
      comments: async (_r: string, number: number) => (number === 347 ? issue347 : number === 283 ? [skipped] : number === 361 ? Array(LIMITS.queueAttempts).fill(failed) : []),
    };
    const settled = new Set<number>();
    const queue = await queuedIssues(gh, REPO, settled);
    // #350 has an open pull request, #348 a merged one, #283 a final answer, #361 used its attempts.
    // #349's pull request was closed unmerged and the intake wrote nothing since: it is new.
    expect(queue).toEqual([{ number: 347, state: "retry", attempts: 1 }, { number: 349, state: "new", attempts: 0 }, { number: 360, state: "new", attempts: 0 }]);
    expect([...settled].sort()).toEqual([283, 348, 350, 361]);
    // A second look in the same run does not ask about the settled ones again.
    asked.length = 0;
    await queuedIssues(gh, REPO, settled);
    expect(asked).toEqual(["intake/issue-347", "intake/issue-349", "intake/issue-360"]);
  });
});

describe("a queued run, with fakes", () => {
  const START = "c".repeat(40);
  // An issue's process that opens no pull request comments on the issue itself, unless `silent`
  // (its comment did not post) or the outcome is "killed" (it ended without a result).
  function fakes({ queue = [[348, 349], [349], []] as number[][], outcomes = {} as Record<number, { outcome: string; ok?: boolean; transient?: string; prUrl?: string; silent?: boolean }>, minutes = [] as number[], failReset = false, failComment = false } = {}) {
    const log: string[] = [];
    const lists = [...queue];
    const own = new Map<number, { user: string; body: string }[]>();
    const github = {
      labelledIssues: async (_r: string, label: string) => (label === "entity-request" ? (lists.length > 1 ? lists.shift()! : lists[0] ?? []).map((number) => ({ number })) : []),
      pullsFor: async () => [],
      comments: async (_r: string, number: number) => [...(own.get(number) ?? []), ...posted.filter((p) => p.number === number).map((p) => ({ user: BOT_LOGIN, body: p.body }))],
      comment: async (_r: string, number: number, body: string) => {
        if (failComment) throw Object.assign(new Error("POST comments: 502 Bad Gateway"), { status: 502 });
        posted.push({ number, body });
      },
    };
    const posted: { number: number; body: string }[] = [];
    const run = (cmd: string, args: string[], opts: { timeoutMs?: number } = {}) => {
      if (cmd === "git") {
        log.push(`git ${args.join(" ")}`);
        if (args[0] === "rev-parse") return { ok: true, output: `${START}\n` };
        return failReset && args[0] === "checkout" ? { ok: false, output: "error: cannot checkout" } : { ok: true, output: "" };
      }
      expect(cmd).toBe(process.execPath);
      expect(args[0].endsWith("scripts/agents/intake.mjs")).toBe(true);
      expect(opts.timeoutMs).toBe(LIMITS.issueMinutes * 60 * 1000);
      const number = Number(args[args.indexOf("--issue") + 1]);
      const since = args.includes("--since") ? ` since ${args[args.indexOf("--since") + 1]}` : "";
      log.push(`issue ${number}${since}`);
      const given = outcomes[number] ?? { outcome: "opened", prUrl: `https://github.com/${REPO}/pull/${number + 1000}` };
      const out = args[args.indexOf("--out") + 1];
      if (given.outcome === "killed") return { ok: false, output: "" };
      if (!given.prUrl && !given.silent) own.set(number, [...(own.get(number) ?? []), { user: BOT_LOGIN, body: `The intake agent wrote a batch but \`the intake run\` failed.\n\n${runMarker({ outcome: given.outcome, retry: Boolean(given.transient) })}` }]);
      fs.mkdirSync(out, { recursive: true });
      fs.writeFileSync(path.join(out, "result.json"), JSON.stringify({ outcome: given.outcome, prUrl: given.prUrl ?? null, transient: given.transient ?? "", kg: { used: true, release: `kg-of-${number}` } }));
      return { ok: given.ok ?? true, output: `log of ${number}` };
    };
    const clock = [...minutes];
    return { log, posted, deps: { github, run, now, log: quiet, elapsedMinutes: () => (clock.length > 1 ? clock.shift()! : clock[0] ?? 0) } };
  }
  const reset = [`git checkout --quiet --force --detach ${START}`, `git reset --quiet --hard ${START}`, "git clean -fdq -- data"];
  const liveEnv = { ...env, ANTHROPIC_API_KEY: "k" };
  const drain = (f: ReturnType<typeof fakes>, extra: string[] = ["--issue", "347", "--since", "2026-11-21T09:00:00Z"], out = tempRoot()) => main(["--drain", ...extra, "--root", tempRoot(), "--out", out], liveEnv, f.deps);

  it("works the labelled issue first, then each waiting issue in its own process on a clean checkout", async () => {
    const f = fakes();
    const out = tempRoot();
    const r = await drain(f, undefined, out);
    expect(f.log).toEqual(["git rev-parse HEAD", "issue 347 since 2026-11-21T09:00:00Z", ...reset, "issue 348", ...reset, "issue 349"]);
    expect(r.outcome).toBe("worked 3 issues");
    expect(r.left).toBe("");
    const result = JSON.parse(fs.readFileSync(path.join(out, "result.json"), "utf8"));
    expect(result.issues.map((i: any) => `${i.issue} ${i.outcome}`)).toEqual(["347 opened", "348 opened", "349 opened"]);
    // The knowledge graph figures the workflow reports are those of the first issue.
    expect(result.kg.release).toBe("kg-of-347");
  });

  it("with no issue, works only what is waiting, and does nothing when nothing is", async () => {
    const f = fakes({ queue: [[347], []] });
    expect((await drain(f, [])).outcome).toBe("worked 1 issue");
    expect(f.log).toEqual(["git rev-parse HEAD", "issue 347"]);
    const idle = fakes({ queue: [[]] });
    expect((await drain(idle, [])).outcome).toBe("worked 0 issues");
    expect(idle.log).toEqual(["git rev-parse HEAD"]);
  });

  it("works four issues labelled at once in one run, so the runs GitHub cancelled while waiting lose nothing", async () => {
    // #347 to #350 are labelled within seconds. The first run is for #347; the runs for #348 and
    // #349 are replaced while waiting. All four are on the list by the time #347 is done.
    const f = fakes({ queue: [[347, 348, 349, 350], [348, 349, 350], [349, 350], [350], []] });
    await drain(f);
    expect(f.log.filter((l) => l.startsWith("issue "))).toEqual(["issue 347 since 2026-11-21T09:00:00Z", "issue 348", "issue 349", "issue 350"]);
  });

  it("does not work an issue twice in a run, even if it stays on the list", async () => {
    const f = fakes({ queue: [[348]], outcomes: { 348: { outcome: "error", ok: false, transient: "server error" } } });
    const r = await drain(f);
    expect(f.log.filter((l) => l.startsWith("issue "))).toEqual(["issue 347 since 2026-11-21T09:00:00Z", "issue 348"]);
    expect(r.outcome).toBe("failed: 1 of 2 issue runs (#348)");
    // The run's own issue too: answered with a failure another run may get past, it stays on the
    // list as retry, and this run does not start it a second time.
    const first = fakes({ queue: [[347]], outcomes: { 347: { outcome: "error", ok: false, transient: "server error" } } });
    await drain(first);
    expect(first.log.filter((l) => l.startsWith("issue "))).toEqual(["issue 347 since 2026-11-21T09:00:00Z"]);
  });

  it("stops at its issue limit and its time limit, and says what is left", async () => {
    const many = Array.from({ length: 10 }, (_, i) => 400 + i);
    const f = fakes({ queue: [many] });
    const r = await drain(f, []);
    expect(f.log.filter((l) => l.startsWith("issue "))).toHaveLength(LIMITS.queueIssues);
    expect(r.left).toBe(`${many.slice(LIMITS.queueIssues).map((n) => `#${n}`).join(", ")}: this run has worked its ${LIMITS.queueIssues} issues`);
    const slow = fakes({ queue: [many], minutes: [5, LIMITS.queueMinutes + 1] });
    const s = await drain(slow, []);
    expect(slow.log.filter((l) => l.startsWith("issue "))).toEqual(["issue 400"]);
    expect(s.left).toContain(`this run has gone on for over ${LIMITS.queueMinutes} minutes`);
  });

  it("starts no other issue after one ends on a rate limit, and fails the run", async () => {
    const f = fakes({ outcomes: { 347: { outcome: "error", ok: false, transient: "rate limit" } } });
    const r = await drain(f);
    expect(f.log).toEqual(["git rev-parse HEAD", "issue 347 since 2026-11-21T09:00:00Z"]);
    expect(r.left).toBe("any issue still queued: #347 ended on a rate limit, so this run starts no other");
    expect(r.outcome).toBe("failed: 1 of 1 issue runs (#347)");
  });

  it("goes on after an issue that failed a store check, and fails the run at the end", async () => {
    const f = fakes({ outcomes: { 347: { outcome: "failed: records add", ok: false } } });
    const r = await drain(f);
    expect(f.log.filter((l) => l.startsWith("issue "))).toHaveLength(3);
    expect(r.outcome).toBe("failed: 1 of 3 issue runs (#347)");
  });

  it("comments for a process that ended without an answer, so the attempt counts and the issue is not tried without end", async () => {
    const f = fakes({ queue: [[]], outcomes: { 347: { outcome: "killed" } } });
    const r = await drain(f);
    expect(r.outcome).toBe("failed: 1 of 1 issue runs (#347)");
    expect(f.posted).toHaveLength(1);
    expect(f.posted[0].number).toBe(347);
    expect(queueState([{ user: BOT_LOGIN, body: f.posted[0].body }])).toEqual({ state: "retry", attempts: 1 });
    expect(queueState(Array(LIMITS.queueAttempts).fill({ user: BOT_LOGIN, body: f.posted[0].body })).state).toBe("exhausted");
    // A process that wrote its own result posted its own comment; the queue adds none.
    const own = fakes({ queue: [[]], outcomes: { 347: { outcome: "error", ok: false, transient: "server error" } } });
    await drain(own);
    expect(own.posted).toEqual([]);
    // Nor for a pull request, which is the answer, or a closed issue, which is not in the queue.
    const opened = fakes({ queue: [[]], outcomes: { 347: { outcome: "opened", prUrl: "https://github.com/x/y/pull/1", silent: true } } });
    await drain(opened);
    expect(opened.posted).toEqual([]);
    const closed = fakes({ queue: [[]], outcomes: { 347: { outcome: "skipped: closed", silent: true } } });
    await drain(closed);
    expect(closed.posted).toEqual([]);
  });

  it("writes the answer itself when an issue's own comment did not reach the issue, so the issue does not stay new", async () => {
    // A final outcome: the issue is done, and no later run works it again.
    const final = fakes({ queue: [[]], outcomes: { 347: { outcome: "failed: records add", ok: false, silent: true } } });
    await drain(final);
    expect(final.posted).toHaveLength(1);
    expect(final.posted[0].body).toContain("its own comment did not reach the issue");
    expect(parseRunMarker(final.posted[0].body)).toEqual({ outcome: "failed: records add", retry: false });
    expect(queueState([{ user: BOT_LOGIN, body: final.posted[0].body }]).state).toBe("done");
    // A failure another run may get past: counted as one attempt.
    const again = fakes({ queue: [[]], outcomes: { 347: { outcome: "error", ok: false, transient: "rate limit", silent: true } } });
    await drain(again);
    expect(parseRunMarker(again.posted[0].body)).toEqual({ outcome: "error", retry: true });
    expect(queueState([{ user: BOT_LOGIN, body: again.posted[0].body }])).toEqual({ state: "retry", attempts: 1 });
  });

  it("stops and fails the run when no answer can be written on an issue, instead of working on with nothing counted", async () => {
    const f = fakes({ outcomes: { 347: { outcome: "skipped: out of scope", silent: true } }, failComment: true });
    const r = await drain(f);
    expect(f.log.filter((l) => l.startsWith("issue "))).toEqual(["issue 347 since 2026-11-21T09:00:00Z"]);
    expect(r.outcome).toBe("failed: 1 of 1 issue runs (#347)");
    expect(r.left).toContain("the answer on #347 could not be read or written (502 POST comments: 502 Bad Gateway), so this run starts no other");
  });

  it("stops when the checkout cannot be put back, without starting the next issue on a used tree", async () => {
    const f = fakes({ failReset: true });
    const r = await drain(f);
    expect(f.log.filter((l) => l.startsWith("issue "))).toEqual(["issue 347 since 2026-11-21T09:00:00Z"]);
    expect(r.outcome).toBe("failed: 1 of 2 issue runs (#348)");
  });

  it("is a live intake run only, and does nothing without an API key", async () => {
    for (const flag of ["--dry-run", "--report-only", "--revise", "--refresh"]) await expect(main(["--drain", flag], liveEnv, fakes().deps)).rejects.toThrow("--drain is a live intake run");
    await expect(main(["--drain", "--since", "yesterday"], liveEnv, fakes().deps)).rejects.toThrow("--since takes a time");
    const f = fakes();
    expect((await main(["--drain", "--issue", "347"], env, f.deps)).outcome).toBe("no key");
    expect(f.log).toEqual([]);
  });
});

// ---------- One issue: the marker, the label time, and a failure another run may get past ----------

function intakeFakes({ comments = [] as { user: string; body: string; created_at: string }[], fail = [] as unknown[] } = {}) {
  const read = (name: string) => JSON.parse(fs.readFileSync(`${INTAKE_FIXTURES}/${name}`, "utf8"));
  const calls: string[] = [];
  const posted: string[] = [];
  const sleeps: number[] = [];
  const structured = [read("proposal.json"), read("verification.json")];
  const failures = [...fail];
  const anthropic = {
    beta: { messages: { stream: (req: { model: string }) => ({ finalMessage: async () => {
      calls.push(`research ${req.model}`);
      if (failures.length) throw failures.shift();
      return { model: req.model, stop_reason: "end_turn", content: [{ type: "text", text: "notes" }], usage: { input_tokens: 1000, output_tokens: 100 } };
    } }) } },
    messages: { create: async (req: { model: string }) => {
      calls.push(`structure ${req.model}`);
      return { stop_reason: "end_turn", content: [{ type: "text", text: JSON.stringify(structured.shift()) }], usage: { input_tokens: 500, output_tokens: 200 } };
    } },
  };
  const github = {
    getIssue: async () => read("issue.json"),
    pullsFor: async () => [],
    comments: async () => comments,
    createPull: async () => ({ html_url: `https://github.com/${REPO}/pull/1` }),
    comment: async (_r: string, _n: number, body: string) => void posted.push(body),
  };
  const fetches = read("fetches.json");
  const fetchImpl = async (url: string) => (fetches[url]?.error ? new Response("no", { status: 403 }) : new Response(`bytes of ${url}`, { status: 200, headers: { "content-type": "text/html; charset=utf-8" } }));
  return { calls, posted, sleeps, deps: { anthropic, github, fetch: fetchImpl, run: () => ({ ok: true, output: "ok" }), now, log: quiet, sleep: async (ms: number) => void sleeps.push(ms) } };
}
const rateLimited = () => Object.assign(new Error('429 {"type":"error","error":{"type":"rate_limit_error","message":"Number of concurrent connections has exceeded your rate limit."}}'), { status: 429 });
const overloaded = () => Object.assign(new Error('529 {"type":"error","error":{"type":"overloaded_error","message":"Overloaded"}}'), { status: 529 });
const issueEnv = { ...env, ANTHROPIC_API_KEY: "k" };
const runIssue = (f: ReturnType<typeof intakeFakes>, extra: string[] = [], out = tempRoot()) => main(["--issue", "9999", "--store-dir", `${INTAKE_FIXTURES}/entities`, "--root", tempRoot(), "--out", out, ...extra], issueEnv, f.deps);

describe("one issue in the queue", () => {
  it("ends every comment it posts with the marker, so a later run knows the issue has its answer", async () => {
    const f = intakeFakes();
    expect((await runIssue(f)).outcome).toBe("opened");
    expect(f.posted).toHaveLength(1);
    expect(parseRunMarker(f.posted[0])).toEqual({ outcome: "opened", retry: false });
    expect(queueState([{ user: BOT_LOGIN, body: f.posted[0] }]).state).toBe("done");
  });

  it("is not worked again by the run its label started, when an earlier run answered it after the label was added", async () => {
    const answer = { user: BOT_LOGIN, body: `The intake agent opened a pull request.\n\n${runMarker({ outcome: "opened" })}`, created_at: "2026-11-21T09:05:00Z" };
    const f = intakeFakes({ comments: [answer] });
    const r = await runIssue(f, ["--since", "2026-11-21T09:00:00Z"]);
    expect(r.outcome).toBe("skipped: an earlier run worked this issue after the label was added");
    expect(f.calls).toEqual([]);
    expect(f.posted).toEqual([]);
    // The label was added again after that answer (a person asks for another run): it runs.
    const again = intakeFakes({ comments: [answer] });
    expect((await runIssue(again, ["--since", "2026-11-21T10:00:00Z"])).outcome).toBe("opened");
    // An answer by anyone else does not count.
    const other = intakeFakes({ comments: [{ ...answer, user: "timini" }] });
    expect((await runIssue(other, ["--since", "2026-11-21T09:00:00Z"])).outcome).toBe("opened");
  });

  it("waits and tries the call again on a 429 and a 529, and counts the retries", async () => {
    const f = intakeFakes({ fail: [rateLimited(), overloaded()] });
    const out = tempRoot();
    expect((await runIssue(f, [], out)).outcome).toBe("opened");
    expect(f.calls.slice(0, 3)).toEqual(["research claude-haiku-5-5", "research claude-haiku-5-5", "research claude-haiku-5-5"]);
    expect(f.sleeps).toEqual([LIMITS.apiRetryBaseSeconds * 1000, LIMITS.apiRetryBaseSeconds * 2000]);
    const usage = JSON.parse(fs.readFileSync(path.join(out, "usage.json"), "utf8"));
    expect(usage.retries).toEqual({ count: 2, waitSeconds: LIMITS.apiRetryBaseSeconds * 3, gaveUp: 0 });
    // A request refused before it started reported no tokens: only the calls that ran are priced.
    expect(usage.byModel["claude-haiku-5-5"].input).toBe(1000 + 500 + 500);
  });

  it("leaves an issue whose run still ends on a rate limit in a state the next run picks up", async () => {
    const f = intakeFakes({ fail: Array.from({ length: LIMITS.apiRetries + 1 }, rateLimited) });
    const out = tempRoot();
    await expect(runIssue(f, [], out)).rejects.toThrow("429");
    expect(f.calls).toHaveLength(LIMITS.apiRetries + 1);
    expect(f.sleeps).toHaveLength(LIMITS.apiRetries);
    expect(f.posted).toHaveLength(1);
    expect(f.posted[0]).toContain(`The failure looks temporary (rate limit). The next intake run tries this issue again; an issue gets at most ${LIMITS.queueAttempts} such runs.`);
    expect(parseRunMarker(f.posted[0])).toMatchObject({ retry: true });
    expect(queueState([{ user: BOT_LOGIN, body: f.posted[0] }])).toEqual({ state: "retry", attempts: 1 });
    expect(JSON.parse(fs.readFileSync(path.join(out, "result.json"), "utf8")).transient).toBe("rate limit");
    expect(JSON.parse(fs.readFileSync(path.join(out, "usage.json"), "utf8")).retries).toMatchObject({ count: LIMITS.apiRetries, gaveUp: 1 });
  });

  it("marks a failure no later run would get past as final", async () => {
    const f = intakeFakes({ fail: [new TypeError("Cannot read properties of undefined (reading 'map')")] });
    await expect(runIssue(f)).rejects.toThrow("Cannot read properties");
    expect(f.sleeps).toEqual([]);
    expect(parseRunMarker(f.posted[0])).toMatchObject({ retry: false });
    expect(f.posted[0]).not.toContain("looks temporary");
    expect(queueState([{ user: BOT_LOGIN, body: f.posted[0] }]).state).toBe("done");
  });
});

// ---------- Waiting on a rate limit ----------

describe("waits on 429 and 529", () => {
  const free = () => Object.assign(new Usage(), {}) as Usage & { retries?: { count: number; waitSeconds: number; gaveUp: number } };
  const failing = (errors: unknown[], value = "done") => {
    const left = [...errors];
    let calls = 0;
    return { call: async () => {
      calls += 1;
      if (left.length) throw left.shift();
      return value;
    }, calls: () => calls };
  };
  const sleeper = () => {
    const sleeps: number[] = [];
    return { sleeps, sleep: async (ms: number) => void sleeps.push(ms) };
  };

  it("tells a rate limit and an overload from anything else", () => {
    expect(retryableError(rateLimited())).toBe("rate limit");
    expect(retryableError(overloaded())).toBe("overloaded");
    // In a stream the error has no status, only its type.
    expect(retryableError({ error: { type: "error", error: { type: "overloaded_error", message: "Overloaded" } } })).toBe("overloaded");
    expect(retryableError(new Error('{"type":"error","error":{"type":"rate_limit_error"}}'))).toBe("rate limit");
    for (const e of [Object.assign(new Error("400 bad request"), { status: 400 }), Object.assign(new Error("500"), { status: 500 }), new TypeError("x"), null]) expect(retryableError(e)).toBe("");
    expect(transientError(Object.assign(new Error("502 Bad Gateway"), { status: 502 }))).toBe("server error");
    expect(transientError(Object.assign(new Error("Connection error."), { name: "APIConnectionError" }))).toBe("connection error");
    expect(transientError(Object.assign(new Error("422 Validation Failed"), { status: 422 }))).toBe("");
  });

  it("waits 20, 40 and 80 seconds, or as long as the reply says, never over the longest wait", () => {
    expect([0, 1, 2].map((n) => retryDelaySeconds(rateLimited(), n))).toEqual([20, 40, 80]);
    expect(retryDelaySeconds(rateLimited(), 5)).toBe(LIMITS.apiRetryMaxSeconds);
    expect(retryDelaySeconds({ status: 429, headers: { "retry-after": "7" } }, 0)).toBe(7);
    expect(retryDelaySeconds({ status: 429, headers: new Headers({ "retry-after": "31.2" }) }, 0)).toBe(32);
    expect(retryDelaySeconds({ status: 429, headers: { "retry-after": "3600" } }, 0)).toBe(LIMITS.apiRetryMaxSeconds);
    expect(retryDelaySeconds({ status: 429, headers: { "retry-after": "soon" } }, 1)).toBe(40);
  });

  it("tries again after each wait and returns the answer", async () => {
    const usage = free();
    const s = sleeper();
    const f = failing([rateLimited(), overloaded()]);
    expect(await withApiRetry(f.call, { usage, sleep: s.sleep })).toBe("done");
    expect(f.calls()).toBe(3);
    expect(s.sleeps).toEqual([20_000, 40_000]);
    expect(usage.retries).toEqual({ count: 2, waitSeconds: 60, gaveUp: 0 });
  });

  it("is bounded: a fixed number of retries per call", async () => {
    const usage = free();
    const s = sleeper();
    const f = failing(Array.from({ length: 10 }, rateLimited));
    await expect(withApiRetry(f.call, { usage, sleep: s.sleep })).rejects.toThrow("429");
    expect(f.calls()).toBe(LIMITS.apiRetries + 1);
    expect(s.sleeps).toEqual([20_000, 40_000, 80_000]);
    expect(usage.retries).toEqual({ count: 3, waitSeconds: 140, gaveUp: 1 });
  });

  it("is bounded: all the waits of a run together", async () => {
    const usage = free();
    const s = sleeper();
    usage.retries = { count: 9, waitSeconds: LIMITS.apiRetryWaitSeconds - 30, gaveUp: 0 };
    // 20 seconds still fit; the 40 after them do not.
    const f = failing(Array.from({ length: 10 }, rateLimited));
    await expect(withApiRetry(f.call, { usage, sleep: s.sleep })).rejects.toThrow("429");
    expect(s.sleeps).toEqual([20_000]);
    expect(usage.retries.waitSeconds).toBe(LIMITS.apiRetryWaitSeconds - 10);
  });

  it("is bounded: no retry once the run is over its cost cap", async () => {
    const usage = free();
    usage.add("claude-sonnet-5-5", { input_tokens: 2_000_000, output_tokens: 0 });
    expect(usage.total()).toBeGreaterThan(LIMITS.maxRunUsd);
    const s = sleeper();
    const f = failing([overloaded()]);
    await expect(withApiRetry(f.call, { usage, sleep: s.sleep })).rejects.toThrow("529");
    expect(f.calls()).toBe(1);
    expect(s.sleeps).toEqual([]);
  });

  it("does not wait on any other error", async () => {
    const usage = free();
    const s = sleeper();
    const f = failing([Object.assign(new Error("400 invalid_request_error"), { status: 400 })]);
    await expect(withApiRetry(f.call, { usage, sleep: s.sleep })).rejects.toThrow("400");
    expect(f.calls()).toBe(1);
    expect(usage.retries).toEqual({ count: 0, waitSeconds: 0, gaveUp: 0 });
  });

  it("counts what a stream reported before it failed, and nothing for a request refused before it started", async () => {
    const usage = free();
    const s = sleeper();
    let n = 0;
    const client = {
      beta: { messages: { stream: () => {
        n += 1;
        // The first request is refused outright. The second starts, reports its input tokens, then fails.
        if (n === 1) return { finalMessage: async () => { throw rateLimited(); } };
        if (n === 2) return { currentMessage: { usage: { input_tokens: 30_000, output_tokens: 1 } }, finalMessage: async () => { throw { error: { type: "error", error: { type: "overloaded_error" } } }; } };
        return { finalMessage: async () => ({ model: "claude-sonnet-5-5", usage: { input_tokens: 30_000, output_tokens: 500 } }) };
      } } },
      messages: { create: async () => ({ ok: true }) },
    };
    const wrapped = retryingClient(client, usage, { sleep: s.sleep });
    const message = await wrapped.beta.messages.stream({ model: "claude-sonnet-5-5" }).finalMessage();
    expect(message.usage.output_tokens).toBe(500);
    expect(n).toBe(3);
    expect(s.sleeps).toEqual([20_000, 40_000]);
    // The failed stream's 30,000 input tokens are in the estimate before the answer's own are added.
    expect(usage.byModel["claude-sonnet-5-5"]).toMatchObject({ input: 30_000, output: 1 });
    expect(usage.total()).toBeGreaterThan(0);
    expect(await wrapped.messages.create({ model: "claude-haiku-5-5" })).toEqual({ ok: true });
  });
});

// ---------- Fixes after the review of the refresh and the queue ----------

describe("a label added again", () => {
  const at = (created_at: string, body: string) => ({ user: BOT_LOGIN, body, created_at });
  const skipped = (t: string) => at(t, `The intake agent did not open a pull request: the request is out of scope for the database. Remove and re-add the \`entity-request\` label to run it again.\n\n${runMarker({ outcome: "skipped: out of scope" })}`);
  const failed = (t: string) => at(t, `The intake agent wrote a batch but \`the intake run\` failed, so no pull request was opened.\n\n${runMarker({ outcome: "error: 529 overloaded", retry: true })}`);

  it("starts the issue afresh: answers older than the label are not counted", () => {
    const comments = [skipped("2026-11-21T09:05:00Z")];
    expect(queueState(comments).state).toBe("done");
    expect(queueState(comments, "2026-11-21T09:00:00Z").state).toBe("done");
    expect(queueState(comments, "2026-11-21T10:00:00Z")).toEqual({ state: "new", attempts: 0 });
    // An issue that used its attempts gets them again with a new label, and only then.
    const used = Array.from({ length: LIMITS.queueAttempts }, (_, i) => failed(`2026-11-21T09:0${i}:00Z`));
    expect(queueState(used, "2026-11-21T08:00:00Z").state).toBe("exhausted");
    expect(queueState(used, "2026-11-21T10:00:00Z")).toEqual({ state: "new", attempts: 0 });
    expect(queueState([...used, failed("2026-11-21T10:05:00Z")], "2026-11-21T10:00:00Z")).toEqual({ state: "retry", attempts: 1 });
    // #347 was labelled before its run failed: it is still tried again.
    expect(queueState(issue347.map((c: any) => ({ ...c, created_at: "2026-11-21T08:31:00Z" })), "2026-11-21T08:30:00Z")).toEqual({ state: "retry", attempts: 1 });
  });

  it("is found by the queue when its label run was cancelled while waiting, with one more call only for an issue that would be left", async () => {
    const asked: number[] = [];
    const gh = {
      labelledIssues: async (_r: string, label: string) => (label === "entity-request" ? [283, 300, 347, 360] : [361]).map((number) => ({ number })),
      pullsFor: async () => [],
      comments: async (_r: string, number: number) => (number === 283 || number === 300 ? [skipped("2026-11-21T09:05:00Z")] : number === 361 ? Array.from({ length: LIMITS.queueAttempts }, () => failed("2026-11-21T09:05:00Z")) : number === 347 ? issue347 : []),
      labelledAt: async (_r: string, number: number) => {
        asked.push(number);
        // #283 and #361 were labelled again after their answers; #300 was not.
        return number === 300 ? "2026-11-21T09:00:00Z" : "2026-11-21T11:00:00Z";
      },
    };
    const settled = new Set<number>();
    expect(await queuedIssues(gh, REPO, settled)).toEqual([{ number: 283, state: "new", attempts: 0 }, { number: 347, state: "retry", attempts: 1 }, { number: 360, state: "new", attempts: 0 }, { number: 361, state: "new", attempts: 0 }]);
    expect([...settled]).toEqual([300]);
    // The events are read only for the issues the comments call done or exhausted.
    expect(asked).toEqual([283, 300, 361]);
    expect(await issueQueueState({ comments: gh.comments, labelledAt: async () => "" }, REPO, 283)).toEqual({ state: "done", attempts: 0 });
  });

  it("reads the time from the issue's events: the last time an intake label was added", async () => {
    const urls: string[] = [];
    const events = [
      { event: "labeled", label: { name: "entity-request" }, created_at: "2026-11-21T08:00:00Z" },
      { event: "unlabeled", label: { name: "entity-request" }, created_at: "2026-11-21T09:00:00Z" },
      { event: "labeled", label: { name: "entity-request" }, created_at: "2026-11-21T10:00:00Z" },
      { event: "labeled", label: { name: "tier-2" }, created_at: "2026-11-21T12:00:00Z" },
      { event: "closed", created_at: "2026-11-21T13:00:00Z" },
    ];
    const client = githubClient("t", (async (url: string) => {
      urls.push(url);
      return new Response(JSON.stringify(url.includes("/issues/5/") ? [] : events), { status: 200 });
    }) as typeof fetch);
    expect(await client.labelledAt(REPO, 283)).toBe("2026-11-21T10:00:00Z");
    expect(urls).toEqual([`https://api.github.com/repos/${REPO}/issues/283/events?per_page=100&page=1`]);
    expect(await client.labelledAt(REPO, 5)).toBe("");
  });
});

describe("the run a label started, when an earlier run reached its issue first", () => {
  const at = (created_at: string, body: string) => ({ user: BOT_LOGIN, body, created_at });
  const SINCE = ["--since", "2026-11-21T09:00:00Z"];
  const retry = (t: string) => at(t, `The intake agent wrote a batch but \`the intake run\` failed.\n\n${runMarker({ outcome: "error: 429", retry: true })}`);

  it("works the issue when that run ended on a failure another run may get past", async () => {
    const f = intakeFakes({ comments: [retry("2026-11-21T09:05:00Z")] });
    expect((await runIssue(f, SINCE)).outcome).toBe("opened");
    expect(f.posted).toHaveLength(1);
  });

  it("does not work it once its attempts since the label are used up", async () => {
    const f = intakeFakes({ comments: Array.from({ length: LIMITS.queueAttempts }, (_, i) => retry(`2026-11-21T09:1${i}:00Z`)) });
    expect((await runIssue(f, SINCE)).outcome).toBe("skipped: an earlier run worked this issue after the label was added");
    expect(f.calls).toEqual([]);
    // Attempts before the label do not count against the new one.
    const before = intakeFakes({ comments: Array.from({ length: LIMITS.queueAttempts }, (_, i) => retry(`2026-11-21T08:1${i}:00Z`)) });
    expect((await runIssue(before, SINCE)).outcome).toBe("opened");
  });

  it("takes a final answer without a marker as an answer too", async () => {
    const f = intakeFakes({ comments: [at("2026-11-21T09:05:00Z", "The intake agent opened https://github.com/x/y/pull/1 with 2 records. It needs a review before merging.")] });
    expect((await runIssue(f, SINCE)).outcome).toBe("skipped: an earlier run worked this issue after the label was added");
    expect(f.calls).toEqual([]);
    expect(f.posted).toEqual([]);
  });
});

describe("the list the two-hourly check asks for", () => {
  it("names the waiting issues and tells the workflow whether there are any, reading GitHub only", async () => {
    const lines: string[] = [];
    const gh = (numbers: number[]) => ({ labelledIssues: async (_r: string, label: string) => (label === "entity-request" ? numbers : []).map((number) => ({ number })), pullsFor: async () => [], comments: async (_r: string, number: number) => (number === 347 ? issue347 : []) });
    const output = path.join(tempRoot(), "output");
    const r = await main(["--queued"], { ...env, GITHUB_OUTPUT: output }, { github: gh([347, 360]), log: (m: string) => void lines.push(m) });
    expect(r.outcome).toBe("2 issues waiting");
    expect(lines).toEqual(["Waiting for an intake run: #347 (retry), #360 (new)"]);
    expect(fs.readFileSync(output, "utf8")).toBe("any=true\n");
    fs.rmSync(output);
    expect((await main(["--queued"], { ...env, GITHUB_OUTPUT: output }, { github: gh([]), log: quiet })).outcome).toBe("0 issues waiting");
    expect(fs.readFileSync(output, "utf8")).toBe("any=false\n");
    await expect(main(["--queued", "--issue", "5"], env, { github: gh([]) })).rejects.toThrow("--queued takes no other argument");
  });
});

describe("an issue's process at its time limit", () => {
  it("is ended with everything it started", async () => {
    const dir = tempRoot();
    const pidFile = path.join(dir, "pid");
    // A parent that starts a child which would run for a minute, then waits itself.
    const script = `const { spawn } = require("node:child_process"); const c = spawn(process.execPath, ["-e", "setTimeout(() => {}, 60000)"], { stdio: "ignore" }); require("node:fs").writeFileSync(${JSON.stringify(pidFile)}, String(c.pid)); console.log("started"); setTimeout(() => {}, 60000);`;
    const started = Date.now();
    const r = await runGroup(process.execPath, ["-e", script], { cwd: dir, timeoutMs: 1500, graceMs: 500 });
    expect(r.ok).toBe(false);
    expect(r.output).toContain("started");
    expect(r.output).toContain("Ended at its time limit of 2 s.");
    expect(Date.now() - started).toBeLessThan(20_000);
    const pid = Number(fs.readFileSync(pidFile, "utf8"));
    const alive = () => {
      try {
        process.kill(pid, 0);
        return true;
      } catch {
        return false;
      }
    };
    for (let i = 0; i < 50 && alive(); i++) await new Promise((done) => setTimeout(done, 100));
    expect(alive()).toBe(false);
  }, 30_000);

  it("gives the output and the exit of a command that ends in time", async () => {
    expect(await runGroup(process.execPath, ["-e", "console.log('fine')"], { timeoutMs: 20_000 })).toEqual({ ok: true, output: "fine\n" });
    expect((await runGroup(process.execPath, ["-e", "console.error('bad'); process.exit(3)"])).ok).toBe(false);
    expect((await runGroup("no-such-command-here", [])).ok).toBe(false);
  });
});

describe("what the review's mutations got past", () => {
  it("keeps an answer GitHub has not given apart from one that says the pull request merges", async () => {
    const pullOf = (mergeable: unknown) => githubClient("t", (async () => new Response(JSON.stringify({ number: 352, state: "open", user: { login: BOT_LOGIN }, head: { ref: "intake/issue-350", sha: HEAD, repo: { full_name: REPO } }, base: { ref: "main" }, labels: [], ...(mergeable === undefined ? {} : { mergeable }) }), { status: 200 })) as typeof fetch).pull(REPO, 352);
    expect((await pullOf(null)).mergeable).toBeNull();
    expect((await pullOf(undefined)).mergeable).toBeNull();
    expect((await pullOf(false)).mergeable).toBe(false);
    expect((await pullOf(true)).mergeable).toBe(true);
    expect((await pullOf(false)).base_ref).toBe("main");
  });

  it("names a record that has two record lines or two provenance lines in the store diff", () => {
    const lines = storeLines(fixture.diff);
    const record = lines.added.find((l) => l.includes('"kind":"model"'))!;
    const provenance = lines.added.find((l) => l.includes('"added_in"') && l.includes("model-protcell"))!;
    expect(tieToBatch({ added: [...lines.added, record], removed: [] }, batch, BATCH_DIR)).toEqual(["intake-350-20261121-model-protcell has 2 record lines and 1 provenance line in the store diff, not one of each"]);
    expect(tieToBatch({ added: [...lines.added, provenance], removed: [] }, batch, BATCH_DIR)).toEqual(["intake-350-20261121-model-protcell has 1 record line and 2 provenance lines in the store diff, not one of each"]);
  });

  it("waits on a 529 that carries a status and no error type", () => {
    expect(retryableError({ status: 529, message: "upstream" })).toBe("overloaded");
    expect(retryableError({ status: 429, message: "slow down" })).toBe("rate limit");
    expect(retryableError({ status: 500, message: "upstream" })).toBe("");
  });

  it("waits and tries the structuring call again too", async () => {
    const usage = new Usage();
    const sleeps: number[] = [];
    let n = 0;
    const client = {
      beta: { messages: { stream: () => ({ finalMessage: async () => ({}) }) } },
      messages: { create: async () => {
        n += 1;
        if (n === 1) throw Object.assign(new Error("429 rate_limit_error"), { status: 429 });
        return { ok: true };
      } },
    };
    const wrapped = retryingClient(client, usage, { sleep: async (ms: number) => void sleeps.push(ms) });
    expect(await wrapped.messages.create({ model: "claude-haiku-5-5" })).toEqual({ ok: true });
    expect(n).toBe(2);
    expect(sleeps).toEqual([LIMITS.apiRetryBaseSeconds * 1000]);
    expect((usage as any).retries).toEqual({ count: 1, waitSeconds: LIMITS.apiRetryBaseSeconds, gaveUp: 0 });
  });

  it("reads the refresh's own marks from the bot's comments only", () => {
    const body = (marker: string, json: string) => `text\n\n<!-- ${marker}: ${json} -->`;
    expect(refreshMarks([
      { user: BOT_LOGIN, body: body(REFRESH_MARKER, '{"n":1,"base":"abc","from":"def"}') },
      { user: "timini", body: body(REFUSED_MARKER, '{"base":"abc"}') },
      { user: BOT_LOGIN, body: body(FAILED_MARKER, '{"step":"records add","base":"abc"}') },
      { user: BOT_LOGIN, body: body(REFUSED_MARKER, '{"base":"abc","from":"def"}') },
      { user: BOT_LOGIN, body: "The intake agent opened a pull request." },
    ])).toEqual([{ kind: "refreshed", base: "abc", step: "" }, { kind: "failed", base: "abc", step: "records add" }, { kind: "refused", base: "abc", step: "" }]);
  });
});

// ---------- The workflow ----------

describe("the refresh job and the queue in intake.yml", () => {
  const workflow = fs.readFileSync(".github/workflows/intake.yml", "utf8");
  const intake = workflow.slice(workflow.indexOf("\n  intake:\n"), workflow.indexOf("\n  revise:\n"));
  const job = workflow.slice(workflow.indexOf("\n  refresh:\n"));
  const step = (name: string, within = job) => {
    const at = within.indexOf(`      - name: ${name}\n`);
    expect(at, name).toBeGreaterThan(-1);
    const rest = within.slice(at + 1);
    const end = rest.search(/\n      (- |# )/);
    return end < 0 ? rest : rest.slice(0, end);
  };
  const group = /\nconcurrency:\n  group: intake-\$\{\{ (.*) \}\}\n  cancel-in-progress: (.*)\n/.exec(workflow)!;

  it("starts the refresh on a push to main that touches data, or on a named pull request, and on nothing else", () => {
    expect(workflow).toMatch(/\n  push:\n    branches: \[main\]\n    paths:\n      - data\/\*\*\n/);
    expect(workflow).toMatch(/\n      refresh_pr:\n        description: .*\n        default: ""\n/);
    expect(job).toContain("\n    if: github.event_name == 'push' || (github.event_name == 'workflow_dispatch' && inputs.refresh_pr != '')\n");
    // Neither starts the intake job or the revise job.
    expect(intake).toContain("\n    if: github.event_name != 'pull_request_review' && !inputs.revise_pr && github.event_name != 'push' && !inputs.refresh_pr && (github.event_name != 'issues' || github.event.label.name == 'entity-request' || github.event.label.name == 'entity-update')\n");
    const revise = workflow.slice(workflow.indexOf("\n  revise:\n"), workflow.indexOf("\n  refresh:\n"));
    expect(revise).not.toMatch(/'push'|refresh_pr/);
  });

  it("refreshes report-only after a push unless the repository variable says otherwise", () => {
    expect(job).toContain("      MODE: ${{ github.event_name == 'push' && (vars.INTAKE_REFRESH_MODE || 'report-only') || inputs.mode }}\n");
    expect(job).not.toMatch(/\|\| 'live'/);
    expect(step("Check the inputs")).toContain('case "$MODE" in dry-run|report-only|live) ;; *) echo "::error::Unknown mode $MODE"; exit 1 ;; esac');
    expect(step("Check the inputs")).toContain('if [ "$GITHUB_EVENT_NAME" != push ] && ! [[ "$PR" =~ ^[0-9]+$ ]]; then echo "::error::A pull request number is required"; exit 1; fi');
  });

  it("makes the app token only in live mode, after a named pull request is checked, and gives every other step the default token", () => {
    const token = step("Token for the rewire-bot app");
    expect(token).toContain("        if: env.MODE == 'live' && steps.open.outputs.any == 'true'\n");
    expect(job.match(/create-github-app-token/g)).toHaveLength(1);
    expect(token).not.toContain("permission-workflows");
    const check = step("Check the pull request is the intake's");
    expect(check).toContain("        if: env.PR != '' && env.MODE != 'dry-run'\n");
    expect(check).toContain(`if [ "$author" != 'rewire-bot[bot]' ] || ! [[ "$branch" =~ ^intake/issue-[0-9]+$ ]] || [ "$head" != "$GITHUB_REPOSITORY" ]; then`);
    const order = ["Check the inputs", "Check the pull request is the intake's", "Open intake pull requests", "Token for the rewire-bot app"].map((n) => job.indexOf(`- name: ${n}\n`));
    expect(order).toEqual([...order].sort((a, b) => a - b));
    expect(job.indexOf("- uses: actions/checkout@v4")).toBeGreaterThan(order[3]);
    expect(job).not.toMatch(/\n    permissions:/);
    expect(step("Commit as the bot")).toContain("        if: steps.app.outputs.token != ''\n");
  });

  it("checks out the default branch only, makes no model call, and passes the mode to the script", () => {
    expect(job.match(/- uses: actions\/checkout@v4\n/g)).toHaveLength(1);
    expect(job).toContain("      - uses: actions/checkout@v4\n        with:\n          ref: ${{ github.event.repository.default_branch }}\n          token: ${{ steps.app.outputs.token || github.token }}\n");
    expect(job).not.toMatch(/refs\/pull|ANTHROPIC_API_KEY: /);
    const run = step("Refresh the pull requests");
    expect(run).toContain("          GH_TOKEN: ${{ steps.app.outputs.token || github.token }}\n");
    expect(run).toContain('dry-run) args="--dry-run" ;;');
    expect(run).toContain('report-only) args="--report-only${PR:+ --pr $PR}" ;;');
    expect(run).toContain('live) args="${PR:+--pr $PR}" ;;');
    expect(run).toContain('node scripts/agents/intake.mjs --refresh $args --out "$RUNNER_TEMP/intake-out"');
  });

  it("installs and runs nothing when no intake pull request is open", () => {
    const open = step("Open intake pull requests");
    // The script's own filter, so no app token is made for a pull request it would not touch:
    // the bot's, the whole branch name, and a head in this repository.
    expect(open).toContain(`select(.user.login == "rewire-bot[bot]" and (.head.ref | test("^intake/issue-[0-9]+$")) and .head.repo.full_name == env.GITHUB_REPOSITORY)`);
    expect(open).not.toContain("startswith");
    for (const name of ["Install the store tools", "Install the agent dependencies", "Refresh the pull requests"]) expect(step(name)).toContain("steps.open.outputs.any == 'true'");
  });

  it("queues live intake runs in one group that never cancels a run, with a label the intake ignores kept out of it", () => {
    expect(group[2]).toBe("${{ github.event_name == 'pull_request' }}");
    expect(group[1]).toContain("github.event_name == 'issues' && ((github.event.label.name == 'entity-request' || github.event.label.name == 'entity-update') && 'queue' || format('label-{0}', github.run_id))");
    expect(group[1]).toContain(" || inputs.mode == 'live' && 'queue' || ");
    // No group is keyed by the issue of a label event any more: that let four runs start at once.
    expect(group[1]).not.toContain("github.event.issue.number");
    // The refresh and the revision have groups of their own, ahead of the issue terms.
    expect(group[1].startsWith("github.event_name == 'push' && 'refresh' || inputs.refresh_pr && format('refresh-{0}', inputs.refresh_pr) || github.event_name == 'pull_request_review' && format('revise-{0}', github.event.pull_request.number) || inputs.revise_pr && format('revise-{0}', inputs.revise_pr) || ")).toBe(true);
  });

  it("has a live run work the queue, because GitHub keeps only one waiting run per group", () => {
    const run = step("Run the intake", intake);
    expect(run).toContain('live) args="--drain${ISSUE:+ --issue $ISSUE}${SINCE:+ --since $SINCE}" ;;');
    expect(run).toContain('report-only) args="--report-only --issue $ISSUE ${REPLAY:-}" ;;');
    expect(intake).toContain("      SINCE: ${{ github.event_name == 'issues' && github.event.issue.updated_at || '' }}\n");
    expect(intake).toContain("      MODE: ${{ github.event_name == 'issues' && 'live' || github.event_name == 'pull_request' && 'dry-run' || inputs.mode }}\n");
    // Six issues of up to 20 minutes do not fit. The run starts none after 25 minutes, so the
    // last one ends by minute 45 of the script, which leaves the setup 10 minutes under the job's
    // 60 and the hour the app token lives. A job killed at its limit would leave no answer.
    expect(LIMITS.queueMinutes + LIMITS.issueMinutes).toBeLessThanOrEqual(50);
    expect(intake).toContain("\n    timeout-minutes: 60\n");
    // All the waits of one run fit in one issue's time several times over.
    expect(LIMITS.apiRetryWaitSeconds).toBeLessThan((LIMITS.issueMinutes * 60) / 2);
  });

  it("asks every two hours whether an issue waits, and starts a live run that works the queue only when one does", () => {
    const check = fs.readFileSync(".github/workflows/intake-queue.yml", "utf8");
    expect(check).toMatch(/\non:\n  schedule:\n    - cron: "\d+ \*\/2 \* \* \*"\n  workflow_dispatch:\n/);
    // A repository variable stops the scheduled check.
    expect(check).toContain("\n    if: github.event_name != 'schedule' || vars.INTAKE_QUEUE_SCHEDULE != 'off'\n");
    // It reads GitHub with the default token: no app token, no API key, nothing installed. The
    // one thing it may write is a workflow run.
    expect(check).toContain("\npermissions:\n  contents: read\n  issues: read\n  pull-requests: read\n  actions: write ");
    expect(check).not.toMatch(/create-github-app-token|ANTHROPIC_API_KEY|npm ci|secrets\./);
    expect(check).toContain("        id: waiting\n        env:\n          GH_TOKEN: ${{ github.token }}\n        run: node scripts/agents/intake.mjs --queued\n");
    // The run it starts is a manual live run with no issue number, of the default branch: the
    // intake job takes it, in the queue's group, and --drain works the waiting issues only.
    expect(check).toContain("        if: steps.waiting.outputs.any == 'true'\n        env:\n          GH_TOKEN: ${{ github.token }}\n        run: gh workflow run intake.yml --repo \"$GITHUB_REPOSITORY\" -f mode=live\n");
    expect(check).not.toMatch(/--ref|-f issue=|revise_pr|refresh_pr/);
    expect(group[1]).toContain(" || inputs.mode == 'live' && 'queue' || ");
    expect(step("Run the intake", intake)).toContain('live) args="--drain${ISSUE:+ --issue $ISSUE}${SINCE:+ --since $SINCE}" ;;');
    // The intake workflow itself has no schedule: an idle check must not count as an intake run
    // that passed, which would close an alert about one that failed.
    expect(workflow).not.toMatch(/\n  schedule:\n/);
    expect(fs.readFileSync(".github/workflows/pipeline-alert.yml", "utf8")).toContain('      - "Intake queue"\n');
  });

  it("rebuilds only pull requests against the branch it checked out", () => {
    expect(step("Refresh the pull requests")).toContain("          BASE_BRANCH: ${{ github.event.repository.default_branch }}\n");
    const revise = workflow.slice(workflow.indexOf("\n  revise:\n"), workflow.indexOf("\n  refresh:\n"));
    expect(step("Revise the batch", revise)).toContain("          BASE_BRANCH: ${{ github.event.repository.default_branch }}\n");
  });

  it("runs the refresh dry run on pull requests that touch the agent", () => {
    const run = step("Run the intake", intake);
    expect(run).toContain("node scripts/agents/intake.mjs --refresh --dry-run --out intake-out/refresh");
    expect(run).toContain('r.outcome !== "ready: refresh not pushed in this mode" || r.pulls?.[0]?.lines !== 4');
    expect(workflow).toMatch(/\n  pull_request:\n    paths:\n      - agents\/intake\.md\n      - scripts\/agents\/\*\*\n      - tests\/agents-intake\*\/\*\*\n/);
  });
});
