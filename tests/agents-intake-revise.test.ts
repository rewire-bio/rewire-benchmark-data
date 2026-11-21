// The intake agent's one revision after a review (intake.mjs --revise). Everything here runs
// without an API key, network or git. The fixture is pull request #338 (Add CycPepNet from #283):
// its batch folder, its files and the review the reviewer agent posted, which passed 8 of 9 fields
// and asked to drop the area proteins-complexes. The model replies in the fixture folder
// (revise-notes.md, revise-reply.json) are written by hand in the shape the two calls return.
import { createHash } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import {
  applyRevision,
  batchLines,
  HUMAN_LABEL,
  main,
  parseReviewVerdict,
  planRevision,
  renderRevisionComment,
  REVISION_MARKER,
  revisedAlready,
  strayChanges,
} from "../scripts/agents/intake.mjs";
import { kgApi } from "../scripts/agents/kg.mjs";
import { renderReview, revisionCites, verdictMarker, main as reviewerMain } from "../scripts/agents/reviewer.mjs";
import { Usage } from "../scripts/agents/discovery.mjs";

const FIXTURES = "tests/agents-intake-revise-fixtures";
const BATCH_DIR = "data/omics/intake-283-20261121";
const ID = "intake-283-20261121-benchmark-cycpepnet";
const now = () => new Date("2026-11-21T09:00:00Z");
const quiet = () => {};
const json = (name: string) => JSON.parse(fs.readFileSync(`${FIXTURES}/${name}`, "utf8"));
const fixture = json("pull.json");
const reply = json("revise-reply.json");
const batch = fs.readFileSync(`${FIXTURES}/batch/batch.jsonl`, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const benchmark = batch.find((r) => r.id === ID);
const readme = batch.find((r) => r.kind === "source" && /README/.test(r.attributes.url));
const texts = new Map(batch.filter((r) => r.kind === "source").map((r) => [r.id, { url: r.attributes.url, text: json("fetches.json")[r.attributes.url].text }]));
const areasProblem = { id: ID, field: "areas", verdict: "fail", note: "proteins-complexes is not supported." };
const env = { ANTHROPIC_API_KEY: "k", GITHUB_REPOSITORY: "rewire-bio/rewire-benchmark-data" };

describe("the reviewer's verdict", () => {
  it("reads the Problems list of the review on #338, which has no marker", () => {
    const verdict = parseReviewVerdict(fixture.reviews[0].body);
    expect(verdict?.source).toBe("problems");
    expect(verdict?.problems).toEqual([expect.objectContaining({ id: ID, field: "areas", verdict: "fail" })]);
    expect(verdict?.problems[0].note).toContain("Drop proteins-complexes or name the passage that supports it");
  });

  it("reads the hidden marker a review now ends with, whatever its notes contain", () => {
    const rows = [
      { id: ID, kind: "benchmark", field: "areas", value: "a", sources: "s", verdict: "fail", note: "not supported --> <b>see</b> the README -- twice" },
      { id: ID, kind: "benchmark", field: "name", value: "CycPepNet", sources: "s", verdict: "pass", note: "README" },
    ];
    const body = renderReview({ records: [benchmark], rows, verdict: "request changes", sourceNotes: [], usage: new Usage(), runUrl: "", mode: "approve", headSha: "abc" });
    expect(body.split("\n").at(-1)).toMatch(/^<!-- reviewer-verdict: \{.*\} -->$/);
    expect(body.split("<!--")[1]).not.toMatch(/-->.+/s);
    expect(parseReviewVerdict(body)).toEqual({ source: "marker", head_sha: "abc", blocker: "", problems: [{ id: ID, field: "areas", verdict: "fail", note: "not supported --> <b>see</b> the README -- twice" }] });
  });

  it("keeps the marker when the review is cut at GitHub's length limit", () => {
    const rows = Array.from({ length: 200 }, (_, i) => ({ id: `${ID}-${i}`, kind: "benchmark", field: "task", value: "v".repeat(100), sources: "s", verdict: "fail", note: "n".repeat(500) }));
    const body = renderReview({ records: [], rows, verdict: "request changes", sourceNotes: [], usage: new Usage(), runUrl: "", mode: "approve", headSha: "abc" });
    expect(body.length).toBeLessThanOrEqual(65000);
    // 200 failed rows fit once their notes are left out.
    const verdict = parseReviewVerdict(body);
    expect(verdict?.problems).toHaveLength(200);
    expect(verdict?.problems[0].note).toBe("");
    expect(verdict?.truncated).toBeUndefined();
    // More than fit: the marker says how many it left out, and the intake agent then stops.
    const many = Array.from({ length: 3000 }, (_, i) => ({ ...rows[0], id: `${ID}-${i}` }));
    const cut = parseReviewVerdict(renderReview({ records: [], rows: many, verdict: "request changes", sourceNotes: [], usage: new Usage(), runUrl: "", mode: "approve", headSha: "abc" }));
    expect(cut!.problems.length + cut!.truncated!).toBe(3000);
  });

  it("carries the reason an all-pass review is not an approval", () => {
    const marker = verdictMarker({ rows: [], verdict: "approve", blocker: "CI is red (checks: failure).", headSha: "abc" });
    expect(parseReviewVerdict(`**Reviewer agent verdict: not approved. CI is red (checks: failure).** All 9 fields pass.\n\n${marker}`)).toEqual({ source: "marker", head_sha: "abc", blocker: "CI is red (checks: failure).", problems: [] });
  });

  it("returns null for text that is not a reviewer agent review", () => {
    expect(parseReviewVerdict("Looks good to me.")).toBeNull();
  });
});

describe("what a revision may change", () => {
  it("puts areas and attributes to the model, works out the depth tier itself, and leaves the rest to a person", () => {
    const plan = planRevision([
      areasProblem,
      { id: ID, field: "depth_tier", verdict: "fail", note: "" },
      { id: ID, field: "description", verdict: "fail", note: "" },
      { id: ID, field: "duplicates", verdict: "fail", note: "" },
      { id: "(store diff)", field: "store diff", verdict: "fail", note: "" },
      { id: readme.id, field: "areas", verdict: "fail", note: "" },
    ], batch);
    expect(plan.ask.map((p) => p.field)).toEqual(["areas"]);
    expect(plan.derived.map((p) => p.field)).toEqual(["depth_tier"]);
    expect(plan.blocked.map((p) => `${p.id === ID ? "benchmark" : p.id === readme.id ? "source" : p.id} ${p.field}`)).toEqual(["benchmark description", "benchmark duplicates", "(store diff) store diff", "source areas"]);
  });

  it("drops the unsupported area and changes nothing but that field and what follows from it", () => {
    const applied = applyRevision(batch, [areasProblem], reply, texts);
    expect(applied.unresolved).toEqual([]);
    expect(applied.fields).toEqual([expect.objectContaining({ id: ID, field: "areas", action: "drop", dropped: ["proteins-complexes"], after: ["molecular-interactions"] })]);
    // docs/tiers.md: molecular-interactions without a protein area is tier 3.
    expect(applied.derived[0]).toEqual({ id: ID, field: "depth_tier", before: 2, after: 3 });
    const after = applied.records.find((r) => r.id === ID);
    expect(after.facets.areas).toEqual(["molecular-interactions"]);
    // Every other byte of the record is as it was.
    const same = (r: any) => JSON.stringify({ ...r, facets: { ...r.facets, areas: [] }, attributes: { ...r.attributes, depth_tier: 0 } });
    expect(same(after)).toBe(same(benchmark));
    for (const s of applied.records.filter((r) => r.kind === "source")) {
      const before = batch.find((r) => r.id === s.id);
      expect(s.facets.areas).toEqual(["molecular-interactions"]);
      expect(JSON.stringify({ ...s, facets: { ...s.facets, areas: [] } })).toBe(JSON.stringify({ ...before, facets: { ...before.facets, areas: [] } }));
    }
    expect(strayChanges(batch, applied.records, applied.fields)).toEqual([]);
    // The input is not changed in place.
    expect(benchmark.facets.areas).toEqual(["molecular-interactions", "proteins-complexes"]);
  });

  it("keeps a value when the quoted passage is in a source the record cites, and changes no byte", () => {
    const problem = { id: ID, field: "entity_level", verdict: "fail", note: "not a suite" };
    const cite = { revisions: [{ id: ID, field: "entity_level", action: "cite", values: [], passage: "The framework covers 20 regression/classification tasks, 45 model configurations", source_url: readme.attributes.url, reason: "" }] };
    const applied = applyRevision(batch, [problem], cite, texts);
    expect(applied.unresolved).toEqual([]);
    expect(applied.fields).toEqual([expect.objectContaining({ field: "entity_level", action: "cite", source_url: readme.attributes.url })]);
    expect(batchLines(applied.records)).toBe(batchLines(batch));
  });

  it("refuses a passage that is not in the source text, or is too short to mean anything", () => {
    const problem = { id: ID, field: "areas", verdict: "fail", note: "" };
    for (const passage of ["CycPepNet benchmarks protein complexes and their binding partners.", "20 tasks"]) {
      const applied = applyRevision(batch, [problem], { revisions: [{ id: ID, field: "areas", action: "cite", values: [], passage, source_url: readme.attributes.url, reason: "" }] }, texts);
      expect(applied.unresolved.map((u) => u.reason)).toEqual(["the quoted passage is not in the text of a source the record cites"]);
      expect(applied.fields).toEqual([]);
    }
  });

  it("drops a whole attribute, records it as missing and removes its locator", () => {
    const problem = { id: ID, field: "task", verdict: "fail", note: "" };
    const applied = applyRevision(batch, [problem], { revisions: [{ id: ID, field: "task", action: "drop", values: [], passage: "", source_url: "", reason: "" }] }, texts);
    const after = applied.records.find((r) => r.id === ID);
    expect(after.attributes.task).toBeUndefined();
    expect(after.attributes.missing_metadata.task).toEqual({ reason: "unextracted", note: expect.stringContaining("Dropped in the revision after review") });
    expect(Object.keys(after.attributes.missing_metadata)).toEqual(["scope_note", "task", "version"]);
    expect(after.attributes.source_locator).toBe("description: README first two paragraphs; the 12/8 split derives from benchmark.py supplementary markings");
    expect(strayChanges(batch, applied.records, applied.fields)).toEqual([]);
  });

  it("drops only the named limitations", () => {
    const problem = { id: ID, field: "limitations", verdict: "fail", note: "" };
    const two = batch.map((r) => (r.id === ID ? { ...r, attributes: { ...r.attributes, limitations: ["One stated limit.", "One invented limit."] } } : r));
    const applied = applyRevision(two, [problem], { revisions: [{ id: ID, field: "limitations", action: "drop", values: ["One invented limit."], passage: "", source_url: "", reason: "" }] }, texts);
    expect(applied.records.find((r) => r.id === ID).attributes.limitations).toEqual(["One stated limit."]);
  });

  it("does not settle a field the reply leaves out, an area the record lacks, the last area, or a dropped entity_level", () => {
    const reasons = (problem: any, revisions: any[]) => applyRevision(batch, [problem], { revisions }, texts).unresolved.map((u) => u.reason);
    const answer = (field: string, values: string[]) => [{ id: ID, field, action: "drop", values, passage: "", source_url: "", reason: "" }];
    expect(reasons(areasProblem, [])).toEqual(["the revision gave neither a value to drop nor a passage"]);
    expect(reasons(areasProblem, [{ ...answer("areas", [])[0], action: "none" }])).toEqual(["the revision gave neither a value to drop nor a passage"]);
    expect(reasons(areasProblem, answer("areas", ["dna-genomes"]))).toEqual(["the revision named no area of the record to drop"]);
    expect(reasons(areasProblem, answer("areas", ["molecular-interactions", "proteins-complexes"]))).toEqual(["dropping these areas would leave the record without an area"]);
    expect(reasons({ ...areasProblem, field: "entity_level" }, answer("entity_level", []))).toEqual(["entity_level cannot be dropped"]);
    expect(reasons({ ...areasProblem, field: "depth_tier" }, [])).toEqual(["the depth tier already follows the areas, so the revision cannot change it"]);
  });

  it("names a change outside the failed fields", () => {
    const applied = applyRevision(batch, [areasProblem], reply, texts);
    const edited = applied.records.map((r) => (r.id === ID ? { ...r, description: "Another description." } : r));
    expect(strayChanges(batch, edited, applied.fields)).toEqual([`${ID}: /description changed`]);
    expect(strayChanges(batch, applied.records.slice(1), applied.fields)).toEqual([`${ID}: removed`]);
  });

  it("counts a revision by the marker, by revision.json, or by a second commit", () => {
    const pull = fixture.pull;
    expect(revisedAlready(pull, fixture.files)).toBe("");
    expect(revisedAlready({ ...pull, body: `${pull.body}\n\n<!-- ${REVISION_MARKER}: {"n":1} -->` }, fixture.files)).toContain("revision marker");
    expect(revisedAlready(pull, [...fixture.files, { filename: `${BATCH_DIR}/revision.json`, status: "added" }])).toContain("revision.json");
    expect(revisedAlready({ ...pull, commits: 2 }, fixture.files)).toContain("2 commits");
  });
});

/** A draft overlay that accepts every record and exports the lines the real one writes. */
function fakeKg({ exportFails = false } = {}) {
  const drafts = new Map<string, any>();
  const client = {
    async callTool({ name, arguments: args }: { name: string; arguments: any }) {
      let out: any;
      if (name === "draft_upsert") {
        drafts.set(args.record.id, args.record);
        out = { id: args.record.id, status: "added", problems: [], warnings: [], possible_duplicates: [] };
      } else if (name === "draft_remove") out = { id: args.id, removed: drafts.delete(args.id) };
      else if (name === "draft_export") {
        if (exportFails) throw new Error("MCP error -32001: draft_export timed out");
        const records = [...drafts.values()];
        out = { exported: true, batch: batchLines(records), batch_sha256: "f".repeat(64), summary: { release: "fake", added: records.map((r) => ({ id: r.id, kind: r.kind, label: r.name, links: r.links, warnings: [], possible_duplicates: [] })) } };
      } else throw new Error(`unknown tool ${name}`);
      return { content: [{ type: "text", text: JSON.stringify(out) }], structuredContent: out };
    },
  };
  return kgApi(client, { config: { iri_base: "https://benchmarks.rewire.it/id/", kinds: { benchmark: "rb:Benchmark", source: "rb:Source" } }, stats: { calls: {}, ms: 0, release: "fake", statements: 5 } as any });
}

/** A checkout of the pull request head: the batch folder as the first run wrote it. */
function rootWithBatch(edit: (name: string, text: string) => string = (_n, t) => t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "intake-revise-"));
  fs.mkdirSync(path.join(root, BATCH_DIR), { recursive: true });
  for (const name of fs.readdirSync(`${FIXTURES}/batch`)) fs.writeFileSync(path.join(root, BATCH_DIR, name), edit(name, fs.readFileSync(`${FIXTURES}/batch/${name}`, "utf8")));
  return root;
}
const readBatch = (root: string, name: string) => fs.readFileSync(path.join(root, BATCH_DIR, name), "utf8");

function fakes({ pull = {} as Record<string, unknown>, reviews = fixture.reviews as any[], files = fixture.files as any[], researchTokens = 4000, fail = "" } = {}) {
  const calls: string[] = [];
  const log: string[] = [];
  const prompts: string[] = [];
  const anthropic = {
    beta: { messages: { stream: (req: any) => ({ finalMessage: async () => {
      calls.push(`research ${req.model}`);
      prompts.push(req.messages[0].content);
      return { model: req.model, stop_reason: "end_turn", content: [{ type: "text", text: fs.readFileSync(`${FIXTURES}/revise-notes.md`, "utf8") }], usage: { input_tokens: researchTokens, output_tokens: 300 } };
    } }) } },
    messages: { create: async (req: any) => {
      calls.push(`structure ${req.model}`);
      return { stop_reason: "end_turn", content: [{ type: "text", text: JSON.stringify(reply) }], usage: { input_tokens: 500, output_tokens: 200 } };
    } },
  };
  const github = {
    pull: async () => ({ ...fixture.pull, ...pull }),
    pullFiles: async () => files,
    reviews: async () => reviews,
    updatePull: async (_r: string, _n: number, patch: { body: string }) => {
      log.push(`body ${patch.body.includes(`<!-- ${REVISION_MARKER}: `) ? "with marker" : "without marker"}`);
    },
    addLabels: async (_r: string, _n: number, labels: string[]) => {
      log.push(`label ${labels.join(",")}`);
    },
    comment: async (_r: string, _n: number, body: string) => {
      log.push(`comment ${body.split("\n")[0]}`);
    },
  };
  const fetches = json("fetches.json");
  const fetchImpl = async (url: string) => new Response(fetches[url]?.text || `bytes of ${url}`, { status: fetches[url] ? 200 : 404, headers: { "content-type": "text/plain" } });
  const run = (cmd: string, args: string[]) => {
    const line = [cmd, ...args].join(" ");
    log.push(line);
    if (fail && line.startsWith(fail)) return { ok: false, output: `${fail}: refused` };
    return { ok: true, output: line === "git rev-parse HEAD" ? `${fixture.pull.head_sha}\n` : "ok" };
  };
  return { calls, log, prompts, deps: { anthropic, github, fetch: fetchImpl, run, now, log: quiet, kg: fakeKg() } };
}
const commandsOf = (log: string[]) => log.filter((l) => /^(git|npm|npx) /.test(l));
const writesOf = (log: string[]) => log.filter((l) => /^(body|label|comment) /.test(l) || /^git (add|commit|push)/.test(l));

describe("dry run", () => {
  it("writes the revised batch folder from the fixtures and calls nothing", async () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "intake-revise-"));
    const run = () => {
      throw new Error("no command expected");
    };
    const r = await main(["--revise", "--dry-run", "--root", root], {}, { now, log: quiet, run, kg: fakeKg() });
    expect(r.outcome).toBe("ready: revision not pushed in this mode");
    expect(r.batchDir).toBe(BATCH_DIR);
    expect(fs.readdirSync(path.join(root, BATCH_DIR)).sort()).toEqual(["batch.jsonl", "kg.json", "notes.md", "review.json", "revision.json"]);
    const revised = readBatch(root, "batch.jsonl").trim().split("\n").map((l) => JSON.parse(l));
    expect(revised.map((x) => x.id)).toEqual(batch.map((x) => x.id));
    expect(revised.every((x) => JSON.stringify(x.facets.areas) === '["molecular-interactions"]')).toBe(true);
    expect(revised[0].attributes.depth_tier).toBe(3);
    const revision = JSON.parse(readBatch(root, "revision.json"));
    expect(revision.pull).toBe(338);
    expect(revision.review.verdict_from).toBe("problems");
    expect(revision.fields).toEqual([expect.objectContaining({ field: "areas", action: "drop", dropped: ["proteins-complexes"] })]);
    // review.json locks the files the revision rewrote.
    const review = JSON.parse(readBatch(root, "review.json"));
    const sha = (name: string) => createHash("sha256").update(readBatch(root, name)).digest("hex");
    expect(review.files).toEqual({ "batch.jsonl": sha("batch.jsonl"), "kg.json": sha("kg.json"), "revision.json": sha("revision.json") });
    expect(review.reviewed_at).toBe("2026-11-21T04:15:37Z");
    expect(readBatch(root, "notes.md")).toContain("## Revision after review");
    // The description says which records changed tier, and carries the count.
    expect(r.pull.body).toContain(`\`${ID}\` is now depth tier 3, not 2 as listed above.`);
    expect(r.pull.body).toMatch(/<!-- intake-revision: \{"n":1,.*\} -->$/);
    expect(`${r.pull.body}${readBatch(root, "notes.md")}`.replace(fixture.pull.body, "")).not.toMatch(/[\u2013\u2014]/);
  });
});

describe("a live revision, with fakes", () => {
  it("makes one Sonnet call and one Haiku call, runs the store checks on the restored store, marks the pull request and pushes", async () => {
    const f = fakes();
    const root = rootWithBatch();
    const r = await main(["--revise", "--pr", "338", "--root", root], env, f.deps);
    expect(r.outcome).toBe("revised");
    expect(f.calls).toEqual(["research claude-sonnet-5-5", "structure claude-haiku-5-5"]);
    // The reviewer's finding and the record reach the model; the passing fields are not asked about.
    expect(f.prompts[0]).toContain("Drop proteins-complexes or name the passage that supports it");
    expect(f.prompts[0]).toContain('"field": "areas"');
    expect(f.prompts[0]).not.toContain('"field": "task"');
    expect(commandsOf(f.log)).toEqual([
      "git rev-parse HEAD",
      ...fixture.files.filter((x: any) => /^data\/(entities|provenance)\//.test(x.filename)).map((x: any) => `git checkout HEAD~1 -- ${x.filename}`),
      `npx tsx scripts/agents/intake-check.ts ${BATCH_DIR}/batch.jsonl`,
      `npm run -s records -- add ${BATCH_DIR}/batch.jsonl ${BATCH_DIR}`,
      "npm run -s records -- check",
      `git add -- ${BATCH_DIR} data/entities data/provenance`,
      expect.stringMatching(/^git commit -m Revise CycPepNet from #283 after review -m One revision after the reviewer agent requested changes on #338: areas \(drop\)\./),
      "git push origin HEAD:refs/heads/intake/issue-283",
    ]);
    // Marked before the push, never force-pushed, never labelled.
    expect(writesOf(f.log).slice(2)).toEqual(["body with marker", "git push origin HEAD:refs/heads/intake/issue-283", expect.stringMatching(/^comment The intake agent revised this pull request after the review\./)]);
    expect(f.log.join("\n")).not.toMatch(/--force|--delete|label /);
    // Through the draft overlay: its export is the batch, and the receipt has its diff.
    const receipt = JSON.parse(readBatch(root, "kg.json"));
    expect(receipt.failures).toEqual([]);
    expect(receipt.summary.added.map((a: any) => a.id)).toEqual(batch.map((x) => x.id));
    expect(receipt.kg.release).toBe("fake");
    expect(r.records.find((x: any) => x.id === ID).facets.areas).toEqual(["molecular-interactions"]);
  });

  it("labels the pull request and calls no model when it was already revised", async () => {
    for (const pull of [{ body: `${fixture.pull.body}\n\n<!-- ${REVISION_MARKER}: {"n":1} -->` }, { commits: 2 }]) {
      const f = fakes({ pull });
      const r = await main(["--revise", "--pr", "338", "--root", rootWithBatch()], env, f.deps);
      expect(r.outcome).toMatch(/^needs-tim: the reviewer agent requested changes again and the pull request was already revised once/);
      expect(f.calls).toEqual([]);
      expect(f.log).toEqual([`label ${HUMAN_LABEL}`, expect.stringMatching(/^comment The intake agent did not revise this pull request: /)]);
    }
  });

  it("leaves a failed field it may not change to a person, without a model call", async () => {
    const body = fixture.reviews[0].body.replace("` areas (fail)", "` description (fail)");
    const f = fakes({ reviews: [{ ...fixture.reviews[0], body }] });
    const r = await main(["--revise", "--pr", "338", "--root", rootWithBatch()], env, f.deps);
    expect(r.outcome).toContain("needs-tim: the review failed fields the revision may not change: description of");
    expect(f.calls).toEqual([]);
    expect(writesOf(f.log)).toEqual([`label ${HUMAN_LABEL}`, expect.stringMatching(/^comment /)]);
  });

  it("leaves a request for changes with no failed field, such as red CI, to a person", async () => {
    const marker = verdictMarker({ rows: [], verdict: "approve", blocker: "CI is red (checks (tests-1): failure).", headSha: fixture.pull.head_sha });
    const f = fakes({ reviews: [{ ...fixture.reviews[0], body: `**Reviewer agent verdict: not approved. CI is red.** All 9 fields pass.\n\n${marker}` }] });
    const r = await main(["--revise", "--pr", "338", "--root", rootWithBatch()], env, f.deps);
    expect(r.outcome).toBe("needs-tim: the review requests changes but lists no failed field (CI is red (checks (tests-1): failure).)");
    expect(f.calls).toEqual([]);
  });

  it("does nothing when the review is not a request for changes on the head commit, or the pull request is not the bot's", async () => {
    const cases: [Parameters<typeof fakes>[0], string][] = [
      [{ reviews: [{ ...fixture.reviews[0], commit_id: "0".repeat(40) }] }, "skipped: the latest review by the reviewer agent is of an earlier commit"],
      [{ reviews: [...fixture.reviews, { ...fixture.reviews[0], state: "APPROVED" }] }, "skipped: the latest review by the reviewer agent does not request changes"],
      [{ reviews: [{ ...fixture.reviews[0], user: "someone" }] }, "skipped: the latest review by the reviewer agent does not request changes"],
      [{ pull: { author: "someone" } }, "skipped: the author is someone, not rewire-bot[bot]"],
      [{ pull: { head_ref: "feature/x" } }, "skipped: the head feature/x is not an intake branch of this repository"],
      [{ pull: { head_repo: "fork/rewire-benchmark-data" } }, "skipped: the head intake/issue-283 is not an intake branch of this repository"],
      [{ pull: { state: "closed" } }, "skipped: the pull request is not open"],
      [{ pull: { labels: [HUMAN_LABEL] } }, "skipped: the pull request is already labelled needs-tim"],
    ];
    for (const [options, outcome] of cases) {
      const f = fakes(options);
      const r = await main(["--revise", "--pr", "338", "--root", rootWithBatch()], env, f.deps);
      expect(r.outcome).toBe(outcome);
      expect(f.calls).toEqual([]);
      expect(f.log).toEqual([]);
    }
  });

  it("accepts the lower-case state of a review event payload", async () => {
    const f = fakes({ reviews: [{ ...fixture.reviews[0], state: "changes_requested" }] });
    const r = await main(["--revise", "--pr", "338", "--report-only", "--root", rootWithBatch()], env, f.deps);
    expect(r.outcome).toBe("ready: revision not pushed in this mode");
  });

  it("stops when the review failed more fields than its verdict lists", async () => {
    const rows = Array.from({ length: 3000 }, (_, i) => ({ id: `${ID}-${i}`, kind: "benchmark", field: "task", value: "v", sources: "s", verdict: "fail", note: "n" }));
    const f = fakes({ reviews: [{ ...fixture.reviews[0], body: `**Reviewer agent verdict: request changes.**\n\n${verdictMarker({ rows, verdict: "request changes", headSha: fixture.pull.head_sha })}` }] });
    const r = await main(["--revise", "--pr", "338", "--root", rootWithBatch()], env, f.deps);
    expect(r.outcome).toMatch(/^needs-tim: the review failed more fields than its verdict could list \(\d+ left out\)$/);
    expect(f.calls).toEqual([]);
  });

  it("does not revise an update pull request", async () => {
    const f = fakes({ files: [...fixture.files, { filename: "data/omics/update-9-20261121/changes.jsonl", status: "added" }] });
    const r = await main(["--revise", "--pr", "338", "--root", rootWithBatch()], env, f.deps);
    expect(r.outcome).toContain("needs-tim: it changes an existing record");
    expect(f.calls).toEqual([]);
  });

  it("does not revise a pull request that touches files outside the batch folder and the store", async () => {
    const f = fakes({ files: [...fixture.files, { filename: "scripts/omics/records.ts", status: "modified" }] });
    const r = await main(["--revise", "--pr", "338", "--root", rootWithBatch()], env, f.deps);
    expect(r.outcome).toContain("needs-tim: it touches files outside the batch folder and the store (scripts/omics/records.ts)");
    expect(f.calls).toEqual([]);
    expect(commandsOf(f.log)).toEqual([]);
  });

  it("in report-only mode, calls the model and checks the batch but writes nothing to GitHub or the branch", async () => {
    const f = fakes();
    const root = rootWithBatch();
    const r = await main(["--revise", "--pr", "338", "--report-only", "--root", root], env, f.deps);
    expect(r.outcome).toBe("ready: revision not pushed in this mode");
    expect(f.calls).toHaveLength(2);
    expect(writesOf(f.log)).toEqual([]);
    expect(commandsOf(f.log).at(-1)).toBe("npm run -s records -- check");
    expect(r.pull.body).toContain("**Revision after review**");
    expect(r.pushed).toBe(false);
  });

  it("in report-only mode, shows the label and comment instead of writing them", async () => {
    const f = fakes({ pull: { commits: 2 } });
    const r = await main(["--revise", "--pr", "338", "--report-only", "--root", rootWithBatch()], env, f.deps);
    expect(r.label).toBe(HUMAN_LABEL);
    expect(r.comment).toContain("left for a person");
    expect(f.log).toEqual([]);
  });

  it("stops at the cost cap before the structuring call, and pushes nothing", async () => {
    const f = fakes({ researchTokens: 2_000_000 });
    const r = await main(["--revise", "--pr", "338", "--root", rootWithBatch()], env, f.deps);
    expect(r.outcome).toBe("needs-tim: the revision passed the $1.5 cost cap before structuring");
    expect(f.calls).toEqual(["research claude-sonnet-5-5"]);
    expect(writesOf(f.log)).toEqual([`label ${HUMAN_LABEL}`, expect.stringMatching(/^comment /)]);
  });

  it("does not push when the reply settles nothing", async () => {
    const f = fakes();
    f.deps.anthropic.messages.create = async () => ({ stop_reason: "end_turn", content: [{ type: "text", text: JSON.stringify({ revisions: [{ ...reply.revisions[0], action: "none", values: [] }] }) }], usage: { input_tokens: 1, output_tokens: 1 } });
    const r = await main(["--revise", "--pr", "338", "--root", rootWithBatch()], env, f.deps);
    expect(r.outcome).toContain("needs-tim: the revision could not settle every failed field: areas of");
    expect(commandsOf(f.log)).toEqual([]);
  });

  it("fails the run and labels the pull request when a store check or the push fails", async () => {
    for (const [fail, outcome, marked] of [["npm run -s records -- add", "failed: records add", false], ["git push", "failed: git push", true]] as const) {
      const f = fakes({ fail });
      const r = await main(["--revise", "--pr", "338", "--root", rootWithBatch()], env, f.deps);
      expect(r.outcome).toBe(outcome);
      expect(f.log.includes("body with marker")).toBe(marked);
      expect(f.log.slice(-2)).toEqual([`label ${HUMAN_LABEL}`, expect.stringMatching(/^comment The intake agent did not revise this pull request: /)]);
      expect(r.pushed).toBe(false);
    }
  });

  it("refuses to run when the working tree is not the pull request head", async () => {
    const f = fakes();
    f.deps.run = (cmd: string, args: string[]) => ({ ok: true, output: cmd === "git" && args[0] === "rev-parse" ? "1".repeat(40) : "ok" });
    const r = await main(["--revise", "--pr", "338", "--root", rootWithBatch()], env, f.deps);
    expect(r.outcome).toBe("failed: checkout");
  });

  it("never revises live without the store checks", async () => {
    await expect(main(["--revise", "--pr", "338", "--no-store-checks"], env, fakes().deps)).rejects.toThrow("cannot use --no-store-checks");
  });
});

describe("the duplicate check after a revision", () => {
  const carried = { step: "duplicate_search", entity: "CycPepNet", query: "CycPepNet", error: "MCP error -32001: draft_upsert timed out" };
  const withFailure = (name: string, text: string) => (name === "kg.json" ? JSON.stringify({ ...JSON.parse(text), failures: [carried] }) : text);

  it("keeps a failed duplicate search of the first run in the revised kg.json", async () => {
    const f = fakes();
    const root = rootWithBatch(withFailure);
    const r = await main(["--revise", "--pr", "338", "--root", root], env, f.deps);
    expect(r.outcome).toBe("revised");
    expect(JSON.parse(readBatch(root, "kg.json")).failures).toEqual([carried]);
  });

  it("records a draft overlay that does not finish, and says so in the description", async () => {
    for (const kg of [fakeKg({ exportFails: true }), null]) {
      const f = fakes();
      const root = rootWithBatch();
      const r = await main(["--revise", "--pr", "338", "--report-only", "--root", root], env, { ...f.deps, kg });
      expect(r.outcome).toBe("ready: revision not pushed in this mode");
      const receipt = JSON.parse(readBatch(root, "kg.json"));
      expect(receipt.failures.map((x: any) => x.step)).toEqual(["draft_overlay"]);
      expect(receipt.summary).toBeNull();
      // The reviewer can still start its own graph from the receipt.
      expect(receipt.kg.kinds.benchmark).toBe("rb:Benchmark");
      expect(r.pull.body).toContain("a human must check the store for duplicates before merging");
      // The script's own lines are the lines the overlay would have exported.
      expect(readBatch(root, "batch.jsonl")).toBe(batchLines(applyRevision(batch, [areasProblem], reply, texts).records));
    }
  });

  it("is not approved by the reviewer when the revised batch carries a failed duplicate check", async () => {
    const root = rootWithBatch(withFailure);
    await main(["--revise", "--pr", "338", "--report-only", "--root", root], env, fakes().deps);
    const revised = readBatch(root, "batch.jsonl").trim().split("\n").map((l) => JSON.parse(l));
    fs.mkdirSync(path.join(root, "data/entities"), { recursive: true });
    const file: Record<string, string> = { benchmark: "benchmarks", source: "sources" };
    const patches = new Map<string, string[]>();
    for (const x of revised) patches.set(file[x.kind], [...(patches.get(file[x.kind]) ?? []), `+${JSON.stringify(x)}`]);
    const posted: { event: string; body: string }[] = [];
    const prompts: string[] = [];
    const allPass = { records: [{ id: ID, fields: ["name", "description", "areas", "entity_level", "task", "limitations", "source_ids"].map((field) => ({ field, verdict: "pass", problem: "", evidence: "README" })) }], unopened: [] };
    const client = {
      getPull: async () => ({ number: 338, title: fixture.pull.title, author: fixture.pull.author, state: "open", head_sha: "b".repeat(40), html_url: fixture.pull.html_url }),
      files: async () => [
        ...["batch.jsonl", "kg.json", "notes.md", "review.json", "revision.json"].map((n) => ({ filename: `${BATCH_DIR}/${n}`, status: "added" })),
        ...[...patches].map(([name, lines]) => ({ filename: `data/entities/${name}.jsonl`, status: "modified", patch: `@@ -1,1 +1,${lines.length + 1} @@\n {"id":"context"}\n${lines.join("\n")}` })),
      ],
      checkRuns: async () => [{ name: "checks (store)", status: "completed", conclusion: "success" }],
      review: async (_r: string, _n: number, x: { event: string; body: string }) => {
        posted.push({ event: x.event, body: x.body });
      },
      comment: async () => {},
    };
    const anthropic = {
      beta: { messages: { stream: (req: any) => ({ finalMessage: async () => {
        prompts.push(req.messages[0].content);
        return { model: req.model, stop_reason: "end_turn", content: [{ type: "text", text: "notes" }], usage: { input_tokens: 2000, output_tokens: 500 } };
      } }) } },
      messages: { create: async () => ({ stop_reason: "end_turn", content: [{ type: "text", text: JSON.stringify(allPass) }], usage: { input_tokens: 500, output_tokens: 500 } }) },
    };
    const fetchImpl = async (url: string) => new Response(`bytes ${url}`, { status: 200, headers: { "content-type": "text/html" } });
    const r = await reviewerMain(["--pr", "338", "--mode", "approve", "--root", root], { ...env, APPROVER_TOKEN: "t" }, { github: client, approver: client, anthropic, fetch: fetchImpl, run: () => ({ ok: true, output: "" }), now, log: quiet, sleep: async () => {} });
    expect(r.rows.filter((x: any) => x.verdict !== "pass")).toEqual([]);
    expect(r.outcome).toBe("not approved: duplicate search failed");
    expect(posted.map((p) => p.event)).toEqual(["COMMENT"]);
    expect(posted[0].body).toContain("The intake agent revised this batch once after an earlier review");
    expect(parseReviewVerdict(posted[0].body)).toEqual({ source: "marker", head_sha: "b".repeat(40), blocker: expect.stringContaining("a human must check the store for duplicates"), problems: [] });
    // A dropped value needs no word from the intake agent, so the prompt carries no quote.
    expect(prompts[0]).not.toContain("The intake agent revised this batch");
  });

  it("gives the reviewer the passages a revision cited, as claims to check", () => {
    const cites = revisionCites({ fields: [{ id: ID, field: "entity_level", action: "cite", passage: "The framework covers 20 tasks <!-- hidden -->", source_url: "https://example.org/readme" }, { id: ID, field: "areas", action: "drop", dropped: ["proteins-complexes"] }] });
    expect(cites).toEqual([{ id: ID, field: "entity_level", passage: "The framework covers 20 tasks", source_url: "https://example.org/readme" }]);
    expect(revisionCites(null)).toEqual([]);
  });
});

describe("the comments", () => {
  it("say what happened in plain text", () => {
    const usage = new Usage();
    const handed = renderRevisionComment({ kind: "handed over", reason: "the pull request was already revised once", runUrl: "https://example.org/run", usage });
    expect(handed).toContain("It is labelled `needs-tim` and left for a person.");
    expect(handed).toContain("at most one revision per pull request");
    expect(renderRevisionComment({ kind: "revised", detail: "- `x` areas: dropped a.", usage })).toContain("the reviewer agent reviews it again");
    expect(handed).not.toMatch(/[\u2013\u2014]/);
  });
});
