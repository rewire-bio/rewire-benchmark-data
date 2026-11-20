import { describe, expect, it } from "vitest";
import { Usage } from "../scripts/agents/discovery.mjs";
import { agentRuns, diffDiscrepancies, main, parseVerdict, planIssue, provisionalBatches, renderDigest, stateMatches, windowOf, writeSummary } from "../scripts/agents/digest.mjs";
import { renderReview } from "../scripts/agents/reviewer.mjs";

const quiet = { log: () => {} };
const env = { GITHUB_REPOSITORY: "rewire-bio/rewire-benchmark-data" };
const dryRun = () => main(["--dry-run"], env, quiet);

describe("parseVerdict", () => {
  it("reads the reviewer agent's own headline", () => {
    const rows = [
      { id: "m", kind: "model", field: "name", value: "x", sources: "s", verdict: "pass", note: "ok" },
      { id: "m", kind: "model", field: "licence", value: "MIT", sources: "s", verdict: "fail", note: "Apache" },
      { id: "m", kind: "model", field: "species", value: "human", sources: "s", verdict: "unverifiable", note: "" },
    ];
    const records = [{ id: "m", kind: "model", name: "M" }];
    const body = renderReview({ records, rows, verdict: "request changes", sourceNotes: [], usage: new Usage(), mode: "comment" });
    expect(parseVerdict(body)).toEqual({ verdict: "request changes", fails: 1, unverifiable: 1, total: 3 });
    const pass = renderReview({ records, rows: [rows[0]], verdict: "approve", sourceNotes: [], usage: new Usage(), mode: "approve" });
    expect(parseVerdict(pass)).toEqual({ verdict: "approve", fails: 0, unverifiable: 0, total: 1 });
  });
  it("reads a blocked approval as not approved, and ignores other text", () => {
    expect(parseVerdict("**Reviewer agent verdict: not approved. A check failed.** All 4 fields pass.")?.verdict).toBe("not approved");
    expect(parseVerdict("Looks good to me")).toBeNull();
  });
  it("flags a review state that contradicts its body", () => {
    expect(stateMatches({ verdict: "approve", state: "CHANGES_REQUESTED" })).toBe(false);
    expect(stateMatches({ verdict: "approve", state: "APPROVED" })).toBe(true);
    expect(stateMatches({ verdict: "request changes", state: "COMMENTED" })).toBe(true);
  });
});

describe("agentRuns", () => {
  const w = windowOf("2026-11-23T06:30:00Z");
  it("counts runs whose agent job ran, and only the artifacts' recorded spend", () => {
    const runs = {
      discovery: [
        { id: 1, event: "schedule", conclusion: "success", created_at: "2026-11-20T08:00:00Z" },
        { id: 2, event: "pull_request", conclusion: "success", created_at: "2026-11-20T08:00:00Z" },
        { id: 3, event: "schedule", conclusion: "success", created_at: "2026-11-01T08:00:00Z" },
      ],
      reviewer: [
        { id: 4, event: "pull_request", conclusion: "failure", created_at: "2026-11-20T08:00:00Z", agentJobFailed: false },
        { id: 5, event: "pull_request", conclusion: "success", created_at: "2026-11-20T08:00:00Z" },
      ],
    };
    const artifacts = [1, 2, 3, 5].map((id) => ({ name: `x-${id}`, workflow_run: { id } }));
    const out = agentRuns(runs, artifacts, { 1: { estimatedUsd: 0.2 }, 2: { estimatedUsd: 0 } }, w);
    expect(out.discovery).toMatchObject({ runs: 1, spend: 0.2, recorded: 1 });
    expect(out.reviewer).toMatchObject({ runs: 1, recorded: 0, failed: [] });
  });
});

describe("diffDiscrepancies", () => {
  const d = (id: string, extra = {}) => ({ id, resolved: false, listing: "public", previous_ids: [], ...extra });
  it("follows previous_ids, and separates new, resolved and stopped firing", () => {
    const out = diffDiscrepancies(
      { discrepancies: [d("a"), d("old"), d("b"), d("gone")] },
      { discrepancies: [d("a"), d("renamed", { previous_ids: ["old"] }), d("b", { resolved: true }), d("c", { listing: "review" })] },
    );
    expect(out.added.map((x) => x.id)).toEqual(["c"]);
    expect(out.resolved.map((x) => x.id)).toEqual(["b"]);
    expect(out.stopped.map((x) => x.id)).toEqual(["gone"]);
    expect(out).toMatchObject({ open: 3, openPublic: 2 });
  });
});

describe("provisionalBatches", () => {
  it("counts records still discovered or needs_review in the store", () => {
    const batches = [{ folder: "intake-1", records: [{ id: "a" }, { id: "b" }, { id: "c" }] }, { folder: "intake-2", records: [{ id: "d" }] }];
    const status = new Map([["a", "discovered"], ["b", "source_checked"], ["d", "reproduced"]]);
    expect(provisionalBatches(batches, status)).toEqual([{ folder: "intake-1", total: 2, provisional: 1 }]);
  });
});

describe("planIssue", () => {
  const w = windowOf("2026-11-23T06:30:00Z");
  const marker = (until: string) => `x\n<!-- weekly-digest: ${JSON.stringify({ since: "s", until })} -->`;
  it("updates this week's digest and closes older ones", () => {
    const thisWeek = { number: 2, body: marker("2026-11-23T06:31:00Z") };
    const last = { number: 1, body: marker("2026-11-16T06:30:00Z") };
    const other = { number: 3, body: "a digest-labelled issue a person wrote" };
    expect(planIssue([thisWeek, last, other], w)).toEqual({ update: thisWeek, close: [last] });
    expect(planIssue([last], w)).toEqual({ update: null, close: [last] });
  });
});

describe("dry run", () => {
  it("renders every section from fixtures with links", async () => {
    const { title, body, action } = await dryRun();
    expect(action).toBe("none");
    expect(title).toBe("Weekly digest: 2026-11-16 to 2026-11-23");
    expect(body).toContain("### Waiting on Tim: 3");
    expect(body).toContain("[#310](https://github.com/rewire-bio/rewire-benchmark-data/pull/310)");
    expect(body).toContain("GitHub recorded the review as CHANGES_REQUESTED, which does not match");
    expect(body).toContain("[rewire.it#447](https://github.com/rewire-bio/rewire.it/issues/447)");
    expect(body).toContain("Intake: 3 pull requests opened, 1 merged, 1 closed without merging");
    expect(body).toContain("| discovery | 2 | [1](https://github.com/rewire-bio/rewire-benchmark-data/actions/runs/102) | $0.21 (1 run not recorded) |");
    expect(body).toContain("| reviewer | 2 | [1](https://github.com/rewire-bio/rewire-benchmark-data/actions/runs/303) | not recorded |");
    expect(body).toContain("the newest release `2026-11-21-bbbb` is not live yet");
    expect(body).toContain("1 of 2 records still provisional");
    expect(body).toContain("2 new, 1 resolved, 1 stopped firing");
    expect(body).toContain("[`discrepancy-cccc`](https://benchmarks.rewirebio.io/contested/discrepancy-cccc/)");
    expect(body).toContain("- Open leads: 1");
    expect(body).toContain("### Pipeline: 1 `pipeline-broken` issue open");
    expect(body).toContain("Closed this week: [#265]");
    expect(body).toContain("Not read: `rewire-bio/rewire-database`");
    expect(body).toMatch(/<!-- weekly-digest: \{.*"until":"2026-11-23T06:30:00.000Z"\} -->$/);
  });
  it("writes no dashes, arrows or tick glyphs", async () => {
    const { body } = await dryRun();
    expect(body).not.toMatch(/[–—→✅❌]/);
  });
});

describe("live posting", () => {
  it("opens the digest as rewire-bot, assigned and labelled, and closes last week's", async () => {
    const calls: [string, string, unknown][] = [];
    const lastWeek = { number: 40, body: `old\n<!-- weekly-digest: ${JSON.stringify({ since: "a", until: "2026-11-16T06:30:00.000Z" })} -->` };
    const github = {
      call: async (method: string, path: string, body?: unknown) => {
        calls.push([method, path, body]);
        if (method === "POST" && path.endsWith("/issues")) return { number: 41, html_url: "https://github.com/x/41" };
        return {};
      },
      all: async () => [lastWeek],
    };
    const { fixtureSource } = await import("../scripts/agents/digest.mjs");
    const source = fixtureSource("tests/agents-digest-fixtures");
    const out = await main([], { ...env, GH_TOKEN: "t" }, { ...quiet, source, github });
    expect(out.action).toBe("opened");
    const create = calls.find(([m, p]) => m === "POST" && p.endsWith("/issues"))!;
    expect(create[2]).toMatchObject({ title: "Weekly digest: 2026-11-16 to 2026-11-23", labels: ["digest"], assignees: ["timini"] });
    expect(calls).toContainEqual(["POST", "/repos/rewire-bio/rewire-benchmark-data/issues/40/comments", { body: "Superseded by #41." }]);
    expect(calls).toContainEqual(["PATCH", "/repos/rewire-bio/rewire-benchmark-data/issues/40", { state: "closed", state_reason: "completed" }]);
  });
});

describe("writeSummary", () => {
  it("strips dashes and stays under the cost cap", async () => {
    const { facts } = await dryRun();
    const usage = new Usage();
    const client = { messages: { create: async () => ({ stop_reason: "end_turn", usage: { input_tokens: 900, output_tokens: 90 }, content: [{ type: "text", text: "One PR waits — #310." }] }) } };
    const text = await writeSummary(client, usage, { system: "s", facts, log: () => {} });
    expect(text).toBe("One PR waits, #310.");
    expect(usage.total()).toBeLessThan(0.25);
    expect(renderDigest(facts, { summary: text }).startsWith("One PR waits, #310.")).toBe(true);
  });
});
