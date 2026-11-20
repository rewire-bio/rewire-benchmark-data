import { describe, expect, it } from "vitest";
import { Usage } from "../scripts/agents/discovery.mjs";
import { LIMITS, agentRuns, anchorSince, artifactsToRead, countedRunIds, diffDiscrepancies, githubClient, isoWeek, main, parseVerdict, planIssue, provisionalBatches, renderDigest, stateMatches, windowOf, writeSummary } from "../scripts/agents/digest.mjs";
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
  it("drops pull request dry-run artifacts before the cap, and reports capped runs as not read", async () => {
    const runs = {
      discovery: [
        ...[1, 2, 3].map((id) => ({ id, event: "pull_request", conclusion: "success", created_at: `2026-11-2${id}T05:00:00Z` })),
        { id: 10, event: "schedule", conclusion: "success", created_at: "2026-11-17T08:00:00Z" },
        { id: 11, event: "workflow_dispatch", conclusion: "success", created_at: "2026-11-18T08:00:00Z" },
      ],
    };
    const artifacts = [1, 2, 3, 10, 11].map((id, k) => ({ name: `discovery-${id}`, created_at: `2026-11-${17 + k}T09:00:00Z`, workflow_run: { id } }));
    const picked = artifactsToRead(artifacts, countedRunIds(runs, w), 1);
    expect(picked.read.map((a) => a.workflow_run.id)).toEqual([11]);
    expect([...picked.unread]).toEqual(["10"]);
    expect(picked.total).toBe(2);
    const out = agentRuns(runs, artifacts, { 11: { estimatedUsd: 0.1 } }, w, picked.unread);
    expect(out.discovery).toMatchObject({ runs: 2, recorded: 1, unread: 1 });
    const { facts } = await dryRun();
    const table = renderDigest({ ...facts, runs: out });
    expect(table).toContain("| discovery | 2 | 0 | $0.10 (1 not read, over the artifact cap) |");
    expect(table).toContain(`1 run not read because the digest reads at most ${LIMITS.artifacts} artifacts`);
    expect(table).not.toContain("left no readable usage.json");
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
  it("counts open as not settled, and lists findings settled while still firing", () => {
    const out = diffDiscrepancies(
      { discrepancies: [d("a"), d("b", { settled: true })] },
      { discrepancies: [d("a", { settled: true, review_state: "explained" }), d("b", { settled: true }), d("c")] },
    );
    expect(out).toMatchObject({ open: 1, openPublic: 1 });
    expect(out.settled.map((x) => x.id)).toEqual(["a"]);
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
  it("updates Monday's digest from a re-run later in the same ISO week", () => {
    const monday = { number: 400, body: marker("2026-11-23T06:35:00Z") };
    expect(planIssue([monday], windowOf("2026-11-24T10:00:00Z"))).toEqual({ update: monday, close: [] });
    expect(planIssue([monday], windowOf("2026-11-29T23:59:00Z"))).toEqual({ update: monday, close: [] });
    expect(planIssue([monday], windowOf("2026-11-30T06:30:00Z"))).toEqual({ update: null, close: [monday] });
    expect(isoWeek("2026-11-23T00:00:00Z")).toBe("2026-W48");
    expect(isoWeek("2027-01-01T00:00:00Z")).toBe("2026-W53");
  });
});

describe("anchorSince", () => {
  const marker = (since: string, until: string) => ({ number: 1, body: `x\n<!-- weekly-digest: ${JSON.stringify({ since, until })} -->` });
  it("starts where last week's digest ended, so a late run neither overlaps nor leaves a gap", () => {
    const last = marker("2026-11-16T06:30:00.000Z", "2026-11-23T07:10:00.000Z");
    const since = anchorSince([last], "2026-11-30T06:30:00Z");
    expect(since).toBe("2026-11-23T07:10:00.000Z");
    expect(windowOf("2026-11-30T06:30:00Z", 7, since)).toMatchObject({ since: "2026-11-23T07:10:00.000Z", label: "2026-11-23 to 2026-11-30" });
  });
  it("keeps this week's start on a re-run, and falls back without a usable digest", () => {
    const monday = marker("2026-11-16T06:30:00.000Z", "2026-11-23T06:30:00.000Z");
    expect(anchorSince([monday], "2026-11-25T12:00:00Z")).toBe("2026-11-16T06:30:00.000Z");
    expect(anchorSince([], "2026-11-25T12:00:00Z")).toBeNull();
    expect(anchorSince([marker("2026-09-01T00:00:00.000Z", "2026-09-08T00:00:00.000Z")], "2026-11-25T12:00:00Z")).toBeNull();
    expect(windowOf("2026-11-25T12:00:00Z", 7, null).since).toBe("2026-11-18T12:00:00.000Z");
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
    expect(body).toContain("2 new, 1 resolved, 1 stopped firing. 3 open (not settled), 2 of them public.");
    expect(body).toContain("Settled since `2026-11-10-0000` and still firing: 1");
    expect(body).toContain("[`discrepancy-cccc`](https://benchmarks.rewirebio.io/contested/discrepancy-cccc/)");
    expect(body).toContain("- Open leads: 1");
    expect(body).toContain("### Pipeline: 1 `pipeline-broken` issue open");
    expect(body).toContain("Closed this week: [#265]");
    expect(body).toContain("Not read: `rewire-bio/rewire-database`");
    expect(body).toMatch(/<!-- weekly-digest: \{.*"until":"2026-11-23T06:30:00.000Z"\} -->$/);
  });
  it("keeps the marker when the body is cut at GitHub's size limit", async () => {
    const { facts } = await dryRun();
    const long = { ...facts, leads: Array.from({ length: 2000 }, (_, k) => ({ number: k, title: `Lead: ${"x".repeat(100)}`, html_url: "u", url: "u", repo: facts.repo })) };
    const prev = LIMITS.maxListed;
    LIMITS.maxListed = 5000;
    try {
      const body = renderDigest(long);
      expect(body.length).toBeLessThanOrEqual(LIMITS.bodyChars);
      expect(body).toContain("Cut at GitHub's issue size limit.");
      expect(body).toMatch(/<!-- weekly-digest: \{.*\} -->$/);
    } finally {
      LIMITS.maxListed = prev;
    }
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
    expect(out.facts.window.since).toBe("2026-11-16T06:30:00.000Z");
  });
});

describe("page limits", () => {
  it("reports a list cut at its page limit, but not one that ended", async () => {
    const hits: string[] = [];
    const full = Array.from({ length: 100 }, (_, k) => ({ k }));
    const fetchImpl = (async (url: string) => ({ ok: true, status: 200, json: async () => (url.includes("/short") ? [{ k: 1 }] : full) })) as unknown as typeof fetch;
    const gh = githubClient("t", fetchImpl, (p: string) => hits.push(p));
    expect(await gh.all("/repos/x/long", { pages: 2 })).toHaveLength(200);
    expect(await gh.all("/repos/x/short", { pages: 2 })).toHaveLength(1);
    expect(hits).toEqual(["/repos/x/long"]);
  });
});

describe("writeSummary", () => {
  it("strips dashes and stays under the cost cap", async () => {
    const { facts } = await dryRun();
    const usage = new Usage();
    const client = { messages: { create: async () => ({ stop_reason: "end_turn", usage: { input_tokens: 900, output_tokens: 90 }, content: [{ type: "text", text: "One PR waits — #310." }] }) } };
    const { text } = await writeSummary(client, usage, { system: "s", facts, log: () => {} });
    expect(text).toBe("One PR waits, #310.");
    expect(usage.total()).toBeLessThan(0.25);
    expect(renderDigest(facts, { summary: text }).startsWith("One PR waits, #310.")).toBe(true);
  });
  it("says why the summary is missing when the model stops early", async () => {
    const source = (await import("../scripts/agents/digest.mjs")).fixtureSource("tests/agents-digest-fixtures");
    const anthropic = { messages: { create: async () => ({ stop_reason: "max_tokens", usage: { input_tokens: 900, output_tokens: 400 }, content: [{ type: "text", text: "One PR" }] }) } };
    const { body } = await main(["--report-only"], { ...env, ANTHROPIC_API_KEY: "k" }, { ...quiet, source, anthropic });
    expect(body).toContain("- No summary: the model stopped with max_tokens.");
  });
});
