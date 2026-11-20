import { readFileSync, readdirSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { judgeJobs, logExcerpt, outcomeOf, plan, readState, sourceOf, staleness, timedOutByAnnotations } from "../scripts/ops/pipeline-alert.mjs";

// The workflows whose failures open the pipeline-broken issue in this repository.
const WATCHED = ["release.yml", "data.yml", "discovery.yml", "intake.yml", "reviewer.yml", "watcher.yml", "digest.yml"];
// Watched by name before their workflow file is merged. Once the file exists, add it to WATCHED.
const AWAITED = ["Monthly entity sweep"];
// Workflows whose runs on the intake agent's pull requests count, and the branch prefix the
// intake pushes to (scripts/agents/intake.mjs).
const PR_WORKFLOWS = ["intake.yml", "reviewer.yml"];
const PR_BRANCH_PREFIX = "intake/";

const now = "2026-11-17T12:00:00.000Z";
const failed = { source: "release.yml", outcome: "fail" as const, url: "https://run/1", summary: "job `release` failure", details: "```\nboom\n```", now };

describe("outcomeOf", () => {
  it("counts failures and successes on main only", () => {
    expect(outcomeOf({ head_branch: "main", event: "workflow_run", conclusion: "failure" })).toBe("fail");
    expect(outcomeOf({ head_branch: "main", event: "push", conclusion: "timed_out" })).toBe("fail");
    expect(outcomeOf({ head_branch: "main", event: "push", conclusion: "success" })).toBe("pass");
    expect(outcomeOf({ head_branch: "main", event: "workflow_dispatch", conclusion: "startup_failure" })).toBe("fail");
  });
  it("ignores branches, pull requests, merge queues, skipped and cancelled runs", () => {
    expect(outcomeOf({ head_branch: "feature", event: "push", conclusion: "failure" })).toBe("ignore");
    expect(outcomeOf({ head_branch: "main", event: "pull_request", conclusion: "failure" })).toBe("ignore");
    expect(outcomeOf({ head_branch: "main", event: "merge_group", conclusion: "failure" })).toBe("ignore");
    expect(outcomeOf({ head_branch: "main", event: "workflow_run", conclusion: "skipped" })).toBe("ignore");
    expect(outcomeOf({ head_branch: "main", event: "push", conclusion: "cancelled" })).toBe("ignore");
  });
  it("counts intake and reviewer runs on the intake agent's pull requests, and nothing else from pull requests", () => {
    const repo = { full_name: "rewire-bio/rewire-benchmark-data" };
    const botRun = { event: "pull_request", head_branch: "intake/issue-250", path: ".github/workflows/reviewer.yml", repository: repo, head_repository: repo };
    const prRuns = { workflows: PR_WORKFLOWS, branchPrefix: PR_BRANCH_PREFIX };
    expect(outcomeOf({ ...botRun, conclusion: "failure" }, prRuns)).toBe("fail");
    expect(outcomeOf({ ...botRun, conclusion: "success" }, prRuns)).toBe("pass");
    expect(outcomeOf({ ...botRun, conclusion: "cancelled" }, prRuns)).toBe("ignore");
    expect(outcomeOf({ ...botRun, path: ".github/workflows/intake.yml", conclusion: "failure" }, prRuns)).toBe("fail");
    // The data checks on a bot pull request are ordinary review, and so is any other branch or a fork.
    expect(outcomeOf({ ...botRun, path: ".github/workflows/data.yml", conclusion: "failure" }, prRuns)).toBe("ignore");
    expect(outcomeOf({ ...botRun, head_branch: "claude/feature", conclusion: "failure" }, prRuns)).toBe("ignore");
    expect(outcomeOf({ ...botRun, head_repository: { full_name: "someone/fork" }, conclusion: "failure" }, prRuns)).toBe("ignore");
    // Without the option, as in rewire-database, no pull request run counts.
    expect(outcomeOf({ ...botRun, conclusion: "failure" })).toBe("ignore");
  });
  it("names the source by workflow file", () => {
    expect(sourceOf({ path: ".github/workflows/release.yml", name: "Cut and publish a release" })).toBe("release.yml");
  });
});

describe("judgeJobs", () => {
  it("ignores a failed run whose only unsuccessful jobs were cancelled", () => {
    expect(judgeJobs([{ id: 1, conclusion: "cancelled" }, { id: 2, conclusion: "skipped" }])).toBe("ignore");
  });
  it("fails a run with a failed job, even beside a cancelled one", () => {
    expect(judgeJobs([{ id: 1, conclusion: "cancelled" }, { id: 2, conclusion: "failure" }])).toBe("fail");
  });
  it("fails a run whose cancelled job hit its time limit", () => {
    const annotations = [{ message: "The job running on runner GitHub Actions 3 has exceeded the maximum execution time of 30 minutes." }];
    expect(timedOutByAnnotations(annotations)).toBe(true);
    expect(timedOutByAnnotations([{ message: "The operation was canceled." }])).toBe(false);
    expect(timedOutByAnnotations(null)).toBe(false);
    expect(judgeJobs([{ id: 1, conclusion: "cancelled" }], new Set([1]))).toBe("fail");
  });
  it("fails a run that failed before any job ran", () => {
    expect(judgeJobs([])).toBe("fail");
  });
});

describe("plan", () => {
  it("opens an issue on the first failure and records the source", () => {
    const d = plan({ issue: null, ...failed });
    expect(d.action).toBe("create");
    expect(readState(d.body).failing["release.yml"]).toEqual({ url: "https://run/1", summary: "job `release` failure", since: now });
    expect(d.comment).toContain("boom");
  });
  it("updates the open issue on a repeat failure and keeps the first failure time", () => {
    const first = plan({ issue: null, ...failed });
    const d = plan({ issue: { number: 7, body: first.body }, ...failed, url: "https://run/2", now: "2026-11-18T00:00:00.000Z" });
    expect(d.action).toBe("update");
    expect(readState(d.body).failing["release.yml"]).toMatchObject({ url: "https://run/2", since: now });
  });
  it("does nothing on success when no issue is open or the source is not failing", () => {
    expect(plan({ issue: null, ...failed, outcome: "pass" }).action).toBe("none");
    const open = plan({ issue: null, ...failed });
    expect(plan({ issue: { number: 7, body: open.body }, ...failed, source: "data.yml", outcome: "pass" }).action).toBe("none");
    expect(plan({ issue: { number: 7, body: open.body }, ...failed, outcome: "ignore" }).action).toBe("none");
  });
  it("closes only when every failing source has succeeded again", () => {
    let body = plan({ issue: null, ...failed }).body;
    body = plan({ issue: { number: 7, body }, ...failed, source: "data.yml" }).body;
    const partial = plan({ issue: { number: 7, body }, ...failed, outcome: "pass" });
    expect(partial.action).toBe("update");
    expect(partial.comment).toContain("Still failing: `data.yml`");
    const done = plan({ issue: { number: 7, body: partial.body }, ...failed, source: "data.yml", outcome: "pass" });
    expect(done.action).toBe("close");
    expect(readState(done.body).failing).toEqual({});
  });
  it("reads an issue without a state marker as having nothing failing", () => {
    expect(readState("written by hand")).toEqual({ failing: {} });
    expect(readState(null)).toEqual({ failing: {} });
  });
});

describe("logExcerpt", () => {
  it("keeps the lines before the first error, without timestamps or group markers", () => {
    const log = [
      "2026-11-16T03:06:50.3868993Z ##[group]Run npm ci",
      "2026-11-16T03:06:50.3868993Z ##[endgroup]",
      ...Array.from({ length: 60 }, (_, i) => `2026-11-16T03:06:50.3868993Z line ${i}`),
      "2026-11-16T03:20:26.8130811Z Knowledge-graph build failed: claims do not match",
      "2026-11-16T03:20:45.9142997Z ##[error]Process completed with exit code 1.",
      "2026-11-16T03:20:46.0000000Z Cleaning up orphan processes",
    ].join("\n");
    const text = logExcerpt(log, 5);
    expect(text.split("\n")).toEqual(["line 57", "line 58", "line 59", "Knowledge-graph build failed: claims do not match", "##[error]Process completed with exit code 1."]);
  });
  it("falls back to the end of the log and cannot break out of the code block", () => {
    expect(logExcerpt("a\nb\n```\nc", 2)).toBe("'''\nc");
  });
  it("drops terminal colour codes", () => {
    expect(logExcerpt("\u001b[36;1mecho hi\u001b[0m")).toBe("echo hi");
  });
  it("caps the excerpt length", () => {
    expect(logExcerpt("x".repeat(10_000)).length).toBeLessThanOrEqual(6004);
  });
});

describe("staleness", () => {
  const releases = [
    { tagName: "kg/2026-11-16-b", publishedAt: "2026-11-16T03:00:00Z" },
    { tagName: "serving/2026-11-16-b", publishedAt: "2026-11-16T03:00:00Z" },
    { tagName: "serving/2026-11-02-a", publishedAt: "2026-11-02T12:00:00Z" },
  ];
  it("is stale when the live release lags the newest serving release by over a day", () => {
    expect(staleness({ liveId: "2026-11-02-a", releases, now })).toMatchObject({ stale: true, newest: "2026-11-16-b" });
  });
  it("allows a day for adoption and deploy", () => {
    expect(staleness({ liveId: "2026-11-02-a", releases, now: "2026-11-16T20:00:00Z" }).stale).toBe(false);
  });
  it("is not stale when the site serves the newest release", () => {
    expect(staleness({ liveId: "2026-11-16-b", releases, now }).stale).toBe(false);
  });
  it("fails loudly when there is no serving release", () => {
    expect(() => staleness({ liveId: "x", releases: [], now })).toThrow(/No published serving/);
  });
});

describe("alert workflow", () => {
  // workflow_run matches workflows by their name, not their file, so a rename would silently stop alerts.
  const alert = readFileSync(".github/workflows/pipeline-alert.yml", "utf8");
  const listed = [...alert.matchAll(/^\s+- "([^"]+)"\s*$/gm)].map((m) => m[1]);
  const nameOf = (file: string) => /^name:\s*(.+)$/m.exec(readFileSync(`.github/workflows/${file}`, "utf8"))?.[1].trim().replace(/^["']|["']$/g, "");
  it.each(WATCHED)("listens to %s by its current name", (file) => {
    expect(readdirSync(".github/workflows")).toContain(file);
    expect(listed).toContain(nameOf(file));
  });
  it("lists no other workflow", () => {
    expect(listed.sort()).toEqual([...new Set([...WATCHED.map(nameOf), ...AWAITED])].sort());
  });
  it("counts pull request runs only of the intake and reviewer, on the intake's branches", () => {
    expect(alert).toContain(`--pr-workflows ${PR_WORKFLOWS.join(",")} --pr-branch-prefix ${PR_BRANCH_PREFIX} `);
    expect(alert).toMatch(new RegExp(`branches: \\[main, "${PR_BRANCH_PREFIX}\\*\\*"\\]`));
    expect(readFileSync("scripts/agents/intake.mjs", "utf8")).toContain("`" + PR_BRANCH_PREFIX + "issue-${");
  });
  it("starts no job for other workflows' runs on the intake's branches", () => {
    const condition = /^ {4}if: >-\n((?: {6}.*\n)+)/m.exec(alert)?.[1] ?? "";
    expect(condition).toContain("github.event.workflow_run.head_branch == 'main'");
    const allowed = [...condition.matchAll(/endsWith\(github\.event\.workflow_run\.path, '\/([^']+)'\)/g)].map((m) => m[1]);
    expect(allowed.sort()).toEqual([...PR_WORKFLOWS].sort());
  });
});
