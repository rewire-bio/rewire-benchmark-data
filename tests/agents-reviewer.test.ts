import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { BOT_LOGIN, buildTable, changedRecords, worktreePull, main, mechanicalProblems, overallVerdict, renderReview, reviewInput, reviewSchema, storeDiff, storeLine, tieStoreDiff } from "../scripts/agents/reviewer.mjs";
import { recordSchema } from "../scripts/omics/schema";
import { Usage } from "../scripts/agents/discovery.mjs";
import { createHash } from "node:crypto";

// The reviewer agent (#256). Everything here runs without an API key or network. The fixture
// batch is the first intake pull request for #250 (#296), whose review must find that
// hEVO-large-o cites the hEVO-base-o card and that the -o models are checkpoints.
const FIXTURES = "tests/agents-reviewer-fixtures";
const now = () => new Date("2026-11-19T12:00:00Z");
const quiet = () => {};
const batch = readFileSync(`${FIXTURES}/batch.jsonl`, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const fixtureReview = JSON.parse(readFileSync(`${FIXTURES}/review.json`, "utf8"));
const pull = JSON.parse(readFileSync(`${FIXTURES}/pull.json`, "utf8"));
const empty = { storeNames: new Map<string, string>(), storeSourceIds: new Set<string>() };
const model = batch.find((r) => r.id.endsWith("model-hevo-base"));

describe("mechanical checks", () => {
  it("passes the fixture batch", () => {
    expect(mechanicalProblems(batch, empty)).toEqual([]);
  });

  it("finds a wrong depth tier, a bad entity_level, a store duplicate, a missing source and a non-entity kind", () => {
    const bad = [
      { ...model, id: "m1", attributes: { ...model.attributes, depth_tier: 3, entity_level: "suite" } },
      { ...model, id: "m2", name: "ESM-2", source_ids: ["nowhere"] },
      { id: "c1", kind: "claim", name: "c", facets: {}, source_ids: ["s"], links: [], attributes: {} },
    ];
    const problems = mechanicalProblems(bad, { storeNames: new Map([["esm 2", "discovery-model-esm-2"]]), storeSourceIds: new Set(["s", ...model.source_ids]) });
    expect(problems.map((p: { id: string; field: string }) => `${p.id} ${p.field}`)).toEqual([
      "m1 depth_tier", "m1 entity_level", "m2 name", "m2 source_ids", "c1 kind",
    ]);
  });
});

describe("verdicts", () => {
  it("marks a field the model did not judge unverifiable, so it cannot approve", () => {
    const rows = buildTable([model], { records: [{ id: model.id, fields: [{ field: "name", verdict: "pass", problem: "", evidence: "README" }] }] }, []);
    expect(rows.find((r: { field: string }) => r.field === "description")!.verdict).toBe("unverifiable");
    expect(rows.find((r: { field: string }) => r.field === "depth_tier")!.verdict).toBe("pass");
    expect(overallVerdict(rows)).toBe("request changes");
  });

  it("lets a mechanical problem fail a field the model passed", () => {
    const fields = ["name", "description", "areas", "entity_level", "version", "access", "training_data", "source_ids"].map((field) => ({ field, verdict: "pass", problem: "", evidence: "x" }));
    const rows = buildTable([model], { records: [{ id: model.id, fields }] }, [{ id: model.id, field: "entity_level", text: "entity_level x is not allowed" }]);
    expect(rows.find((r: { field: string }) => r.field === "entity_level")!.verdict).toBe("fail");
  });

  it("shows the reviewer each record's fields and the URL of every cited source", () => {
    const input = reviewInput(batch);
    const largeO = input.find((r: { id: string }) => r.id.endsWith("hevo-large-o"));
    expect(largeO.entity_level).toBe("family");
    expect(largeO.sources.map((s: { url: string }) => s.url)).toContain("https://huggingface.co/MulinLab/hEVO-base-o");
  });
});

describe("dry run on the #296 batch", () => {
  it("requests changes for exactly the two known problems", async () => {
    const r = await main(["--dry-run"], {}, { now, log: quiet });
    expect(r.verdict).toBe("request changes");
    const fails = r.rows.filter((x: { verdict: string }) => x.verdict !== "pass").map((x: { id: string; field: string }) => `${x.id.replace("intake-250-20261119-", "")} ${x.field}`);
    expect(fails).toEqual(["model-hevo-base-o entity_level", "model-hevo-large-o entity_level", "model-hevo-large-o source_ids"]);
    expect(r.body).toContain("| Field | Value | Source | Verdict | Evidence or problem |");
    expect(r.body).toContain("comment-only");
    expect(r.body).not.toMatch(/[–—]/);
  });
});

describe("posting, with fakes", () => {
  const allPass = {
    records: batch.filter((r) => r.kind !== "source").map((r) => ({
      id: r.id,
      fields: ["name", "description", "areas", "entity_level", "version", "access", "licence", "training_data", "task", "scope_note", "species", "repository", "limitations", "source_ids"]
        .map((field) => ({ field, verdict: "pass", problem: "", evidence: "README" })),
    })),
    unopened: [],
  };

  function fakes({ review = fixtureReview, checks = [{ name: "checks (store)", status: "completed", conclusion: "success" }], author = BOT_LOGIN } = {}) {
    const posted: { event: string; body: string; by: string }[] = [];
    const commands: string[] = [];
    const calls: string[] = [];
    const client = (by: string) => ({
      getPull: async () => ({ ...pull, author }),
      files: async () => pull.files,
      checkRuns: async () => checks,
      review: async (_repo: string, _n: number, r: { event: string; body: string }) => {
        if (by === "bot" && r.event !== "COMMENT") {
          const e = new Error("422 Can not request changes on your own pull request") as Error & { status: number };
          e.status = 422;
          throw e;
        }
        posted.push({ event: r.event, body: r.body, by });
      },
      comment: async () => {},
    });
    const anthropic = {
      beta: { messages: { stream: (req: { model: string }) => ({ finalMessage: async () => {
        calls.push(`review ${req.model}`);
        return { model: req.model, stop_reason: "end_turn", content: [{ type: "text", text: "notes" }], usage: { input_tokens: 2000, output_tokens: 500 } };
      } }) } },
      messages: { create: async (req: { model: string }) => {
        calls.push(`structure ${req.model}`);
        return { stop_reason: "end_turn", content: [{ type: "text", text: JSON.stringify(review) }], usage: { input_tokens: 500, output_tokens: 500 } };
      } },
    };
    const fetches = JSON.parse(readFileSync(`${FIXTURES}/fetches.json`, "utf8"));
    const fetchImpl = async (url: string) => new Response(`bytes ${url}`, { status: fetches[url] ? 200 : 404, headers: { "content-type": "text/html" } });
    const run = (cmd: string, args: string[]) => {
      commands.push([cmd, ...args].join(" "));
      return { ok: true, output: "" };
    };
    return { posted, commands, calls, deps: { github: client("bot"), approver: client("approver"), anthropic, fetch: fetchImpl, run, now, log: quiet, sleep: async () => {} } };
  }
  const env = { ANTHROPIC_API_KEY: "k", GITHUB_REPOSITORY: "rewire-bio/rewire-benchmark-data" };
  const args = (mode: string) => ["--pr", "296", "--mode", mode];

  it("uses Sonnet to review and Haiku only to structure, and posts a comment review in comment mode", async () => {
    const f = fakes();
    const root = await rootWithBatch();
    const r = await main(["--pr", "296", "--mode", "comment", "--root", root], env, f.deps);
    expect(f.calls).toEqual(["review claude-sonnet-5-5", "structure claude-haiku-5-5"]);
    expect(r.outcome).toBe("commented: request changes");
    expect(f.posted.map((p) => p.event)).toEqual(["COMMENT"]);
    expect(f.commands).toEqual([]);
  });

  async function rootWithBatch() {
    const fs = await import("node:fs");
    const os = await import("node:os");
    const dir = fs.mkdtempSync(`${os.tmpdir()}/reviewer-`);
    fs.mkdirSync(`${dir}/data/omics/intake-250-20261119`, { recursive: true });
    fs.copyFileSync(`${FIXTURES}/batch.jsonl`, `${dir}/data/omics/intake-250-20261119/batch.jsonl`);
    fs.mkdirSync(`${dir}/data/entities`, { recursive: true });
    return dir;
  }

  it("in approve mode, approves with the approver token and enables auto-merge when every field and check passes", async () => {
    const f = fakes({ review: allPass });
    const r = await main(["--pr", "296", "--mode", "approve", "--root", await rootWithBatch()], { ...env, APPROVER_TOKEN: "t" }, f.deps);
    expect(r.verdict).toBe("approve");
    expect(f.posted).toEqual([expect.objectContaining({ event: "APPROVE", by: "approver" })]);
    expect(f.commands).toEqual(["gh pr merge 296 --auto --merge --repo rewire-bio/rewire-benchmark-data"]);
    expect(r.outcome).toBe("approved; auto-merge enabled");
  });

  it("in approve mode, does not approve when CI failed", async () => {
    const f = fakes({ review: allPass, checks: [{ name: "checks (tests-1)", status: "completed", conclusion: "failure" }] });
    const r = await main(["--pr", "296", "--mode", "approve", "--root", await rootWithBatch()], { ...env, APPROVER_TOKEN: "t" }, f.deps);
    expect(r.outcome).toBe("not approved: CI red");
    expect(f.posted).toEqual([expect.objectContaining({ event: "REQUEST_CHANGES", by: "approver" })]);
    // The headline says why it is not an approval, so it never contradicts the review event.
    expect(f.posted[0].body.split("\n")[0]).toMatch(/^\*\*Reviewer agent verdict: not approved. CI is red \(checks \(tests-1\): failure\).\*\* All \d+ fields pass.$/);
    expect(f.commands).toEqual([]);
  });

  it("in approve mode, requests changes when a field fails, and never merges", async () => {
    const f = fakes();
    const r = await main(["--pr", "296", "--mode", "approve", "--root", await rootWithBatch()], { ...env, APPROVER_TOKEN: "t" }, f.deps);
    expect(r.outcome).toBe("requested changes");
    expect(f.posted).toEqual([expect.objectContaining({ event: "REQUEST_CHANGES", by: "approver" })]);
    expect(f.commands).toEqual([]);
  });

  it("does not approve without an approver token", async () => {
    const f = fakes({ review: allPass });
    const r = await main(["--pr", "296", "--mode", "approve", "--root", await rootWithBatch()], env, f.deps);
    expect(r.outcome).toBe("not approved: no approver token");
    expect(f.posted.map((p) => p.event)).toEqual(["COMMENT"]);
  });

  it("in approve mode, comments and asks for a human when the intake's duplicate search failed", async () => {
    const fs = await import("node:fs");
    const f = fakes({ review: allPass });
    const root = await rootWithBatch();
    const failures = [{ step: "duplicate_search", entity: "hEvo-base", query: "hEvo-base", error: "MCP error -32001: draft_upsert timed out" }];
    fs.writeFileSync(`${root}/data/omics/intake-250-20261119/kg.json`, JSON.stringify({ kg: { used: false }, links: [], duplicate_rulings: [], failures, summary: null }));
    const r = await main(["--pr", "296", "--mode", "approve", "--root", root], { ...env, APPROVER_TOKEN: "t" }, f.deps);
    expect(r.outcome).toBe("not approved: duplicate search failed");
    expect(f.posted).toEqual([expect.objectContaining({ event: "COMMENT", by: "approver" })]);
    expect(f.posted[0].body.split("\n")[0]).toContain("a human must check the store for duplicates before merging");
    expect(f.posted[0].body).toContain("duplicate search for hEvo-base failed");
    expect(f.commands).toEqual([]);
  });

  it("does not approve when its own duplicate search fails", async () => {
    const f = fakes({ review: allPass });
    const kg = { search: async () => { throw new Error("search timed out"); }, idOf: () => null, kindOfClass: () => null };
    const r = await main(["--pr", "296", "--mode", "approve", "--root", await rootWithBatch()], { ...env, APPROVER_TOKEN: "t" }, { ...f.deps, kg });
    expect(r.outcome).toBe("not approved: duplicate search failed");
    expect(f.posted.map((p) => p.event)).toEqual(["COMMENT"]);
    expect(f.posted[0].body).toContain("The reviewer's knowledge-graph duplicate search");
  });

  async function rootWithReceipt(receipt: any) {
    const fs = await import("node:fs");
    const root = await rootWithBatch();
    fs.writeFileSync(`${root}/data/omics/intake-250-20261119/kg.json`, JSON.stringify({ links: [], duplicate_rulings: [], ...receipt }));
    return root;
  }
  const kgUsed = { release: "kg/x", iri_base: "https://example.org/id/", kinds: { model: "rb:Model" } };
  const summary = { release: "kg/x", added: [] };

  it("does not approve when the intake's draft overlay failed", async () => {
    const f = fakes({ review: allPass });
    const root = await rootWithReceipt({ kg: kgUsed, failures: [{ step: "draft_overlay", error: "draft_export failed: timed out", dropped: [] }], summary: null });
    const r = await main(["--pr", "296", "--mode", "approve", "--root", root], { ...env, APPROVER_TOKEN: "t" }, f.deps);
    expect(r.outcome).toBe("not approved: duplicate search failed");
    expect(f.posted.map((p) => p.event)).toEqual(["COMMENT"]);
    expect(f.posted[0].body).toContain("draft overlay failed before exporting the batch");
    expect(f.commands).toEqual([]);
  });

  it("does not approve when its own knowledge graph does not start", async () => {
    const f = fakes({ review: allPass });
    const root = await rootWithReceipt({ kg: kgUsed, failures: [], summary });
    const r = await main(["--pr", "296", "--mode", "approve", "--root", root], { ...env, APPROVER_TOKEN: "t", KG_BUNDLE: "/nonexistent/kg.tar.gz" }, f.deps);
    expect(r.outcome).toBe("not approved: duplicate search failed");
    expect(f.posted[0].body).toContain("The reviewer's knowledge graph did not start");
    expect(f.commands).toEqual([]);
  });

  it("does not approve when nothing checked the batch against the graph", async () => {
    const f = fakes({ review: allPass });
    const root = await rootWithReceipt({ kg: kgUsed, failures: [], summary: null });
    const r = await main(["--pr", "296", "--mode", "approve", "--root", root], { ...env, APPROVER_TOKEN: "t" }, f.deps);
    expect(r.outcome).toBe("not approved: duplicate search failed");
    expect(f.posted[0].body).toContain("No knowledge-graph duplicate check of this batch ran");
  });

  it("in comment mode, does not head the review as an approval when a duplicate search failed", async () => {
    const f = fakes({ review: allPass });
    const root = await rootWithReceipt({ kg: { used: false }, failures: [{ step: "duplicate_search", entity: "hEvo-base", error: "timed out" }], summary: null });
    const r = await main(["--pr", "296", "--mode", "comment", "--root", root], env, f.deps);
    expect(r.outcome).toBe("commented: not approved: duplicate search failed");
    expect(f.posted[0].body.split("\n")[0]).toContain("Reviewer agent verdict: not approved.");
    expect(f.posted[0].body.split("\n")[0]).not.toContain("verdict: approve");
  });

  it("skips pull requests the bot did not open", async () => {
    const f = fakes({ author: "someone" });
    const r = await main(args("comment"), env, f.deps);
    expect(r.outcome).toContain("not rewire-bot[bot]");
    expect(f.calls).toEqual([]);
  });
});

// Changes to existing records (rdf-kg-mcp #10). The fixture is the intake's SpliceAI update: the
// archived repository changes access, adds a source and a source_locator note.
describe("changed records and the store diff", () => {
  const UPDATE = `${FIXTURES}/update`;
  const upull = JSON.parse(readFileSync(`${UPDATE}/pull.json`, "utf8"));
  const changes = readFileSync(`${UPDATE}/changes.jsonl`, "utf8").trim().split("\n").map((l) => JSON.parse(l));
  const sources = readFileSync(`${UPDATE}/batch.jsonl`, "utf8").trim().split("\n").map((l) => JSON.parse(l));
  const sha = (t: string) => createHash("sha256").update(t).digest("hex");
  const tie = (files: { filename: string; patch?: string; status?: string }[]) =>
    tieStoreDiff(storeDiff(files), { batch: sources, changes });

  it("reviews every changed field and approves when each passes and the store diff ties", async () => {
    const r = await main(["--dry-run", "--fixtures", UPDATE], {}, { now, log: quiet });
    const rows = r.rows.map((x: { id: string; field: string; verdict: string }) => `${x.id} ${x.field} ${x.verdict}`);
    expect(rows).toEqual([
      "discovery-model-spliceai /source_ids pass",
      "discovery-model-spliceai /attributes/access pass",
      "discovery-model-spliceai /attributes/source_locator pass",
      "(store diff) store diff pass",
    ]);
    expect(r.verdict).toBe("approve");
    expect(r.body).toContain("SpliceAI (model, changed): 3 of 3 changed fields pass");
    expect(r.body).toContain("| /attributes/access | changed. Before: official_source_linked. After: The code and trained models");
  });

  it("gives the model the field-level diff and lets it judge each changed path", () => {
    const { before } = tie(upull.files);
    const changed = changedRecords(changes, before);
    const input = reviewInput(sources, changed);
    expect(input[0]).toMatchObject({ id: "discovery-model-spliceai", changed_record: true });
    expect(input[0].changed_fields.map((f: { field: string }) => f.field)).toEqual(["/source_ids", "/attributes/access", "/attributes/source_locator"]);
    expect(input[0].changed_fields[1].before).toBe("official_source_linked");
    // A stored source the change cites is shown with its URL, so the model can open it.
    const stored = reviewInput([], changed, new Map([["src-discovery-illumina-spliceai", "https://github.com/Illumina/SpliceAI"]]));
    expect(stored[0].sources[0]).toEqual({ id: "src-discovery-illumina-spliceai", url: "https://github.com/Illumina/SpliceAI" });
    const fieldEnum = reviewSchema(["/attributes/access"]).properties.records.items.properties.fields.items.properties.field.enum;
    expect(fieldEnum).toContain("/attributes/access");
    expect(fieldEnum).toContain("name");
  });

  it("refuses approval when the store diff touches a record that is not in the reviewed files", async () => {
    const stray = '{"id":"catalog-model-spliceai","kind":"model","name":"SpliceAI"}';
    const models = upull.files.find((f: { filename: string }) => f.filename === "data/entities/models.jsonl");
    const files = upull.files.map((f: { filename: string; patch?: string }) => (f === models ? { ...f, patch: `${f.patch}\n-${stray}\n+${stray.replace("SpliceAI\"}", "SpliceAI v2\"}")}` } : f));
    expect(tie(files).problems).toEqual([{ id: "catalog-model-spliceai", text: expect.stringContaining("the store diff changes catalog-model-spliceai (data/entities/models.jsonl), which is in neither batch.jsonl nor changes.jsonl") }]);

    // The same through main, with every changed field passing: the store diff row alone refuses it.
    const fs = await import("node:fs");
    const os = await import("node:os");
    const dir = fs.mkdtempSync(`${os.tmpdir()}/reviewer-update-`);
    for (const name of ["changes.jsonl", "batch.jsonl", "review.json", "fetches.json"]) fs.copyFileSync(`${UPDATE}/${name}`, `${dir}/${name}`);
    fs.cpSync(`${UPDATE}/entities`, `${dir}/entities`, { recursive: true });
    fs.writeFileSync(`${dir}/pull.json`, JSON.stringify({ ...upull, files }));
    const r = await main(["--dry-run", "--fixtures", dir], {}, { now, log: quiet });
    fs.rmSync(dir, { recursive: true, force: true });
    expect(r.verdict).toBe("request changes");
    expect(r.rows.filter((x: { verdict: string }) => x.verdict !== "pass")).toEqual([
      expect.objectContaining({ id: "(store diff)", field: "store diff", value: "catalog-model-spliceai", verdict: "fail" }),
    ]);
    expect(r.body).toContain("which is in neither batch.jsonl nor changes.jsonl");
  });

  it("refuses a store diff it cannot read, a stale base, extra provenance and an added record that existed", () => {
    const models = upull.files.find((f: { filename: string }) => f.filename === "data/entities/models.jsonl");
    const without = upull.files.map((f: { filename: string }) => (f === models ? { filename: f.filename, status: "modified" } : f));
    expect(tie(without).problems.map((p: { text: string }) => p.text)).toEqual(expect.arrayContaining([
      expect.stringContaining("GitHub gave no diff for it"),
      expect.stringContaining("removes 0 and adds 0 lines"),
    ]));
    const staleLines = [{ ...changes[0], base_sha256: sha("an older line") }];
    const stale = tieStoreDiff(storeDiff(upull.files), { batch: sources, changes: staleLines });
    expect(stale.problems.map((p: { text: string }) => p.text)).toEqual([expect.stringContaining("not the base_sha256")]);
    const prov = [...upull.files, { filename: "data/provenance/records/0.jsonl", status: "modified", patch: '+{"id":"someone-else","sha256":"x"}' }];
    expect(tie(prov).problems).toEqual([{ id: "someone-else", text: expect.stringContaining("provenance of someone-else") }]);
    const re = upull.files.map((f: { filename: string; patch?: string }) => (f.filename === "data/entities/sources.jsonl" ? { ...f, patch: `${f.patch}\n-${JSON.stringify(sources[0])}` } : f));
    expect(tie(re).problems.map((p: { text: string }) => p.text)).toEqual([expect.stringContaining("it was already in the store")]);
    expect(tie(upull.files).problems).toEqual([]);
  });

  it("writes a batch record as records add does", () => {
    const record = sources[0];
    const shuffled = Object.fromEntries(Object.entries({ ...record, links: [{ target_id: "discovery-model-spliceai", relation: "family", note: "dropped" }] }).reverse());
    expect(storeLine(shuffled)).toBe(JSON.stringify(recordSchema.parse(shuffled)));
    expect(storeLine(record)).toBe(JSON.stringify(recordSchema.parse(record)));
  });

  it("refuses an added line whose content is not the batch record", () => {
    const sourcesFile = upull.files.find((f: { filename: string }) => f.filename === "data/entities/sources.jsonl");
    const renamed = JSON.stringify({ ...sources[0], name: "Something else" });
    const files = upull.files.map((f: { filename: string; patch?: string }) =>
      f === sourcesFile ? { ...f, patch: f.patch!.split("\n").map((l) => (l === `+${storeLine(sources[0])}` ? `+${renamed}` : l)).join("\n") } : f);
    expect(files).not.toEqual(upull.files);
    expect(tie(files).problems).toEqual([{ id: sources[0].id, text: expect.stringContaining("is not the batch.jsonl record as records add writes it") }]);
  });

  it("refuses a changed line that moves keys the change did not touch", () => {
    const models = upull.files.find((f: { filename: string }) => f.filename === "data/entities/models.jsonl");
    const added = models.patch.split("\n").find((l: string) => l.startsWith("+") && !l.startsWith("+++")).slice(1);
    const record = JSON.parse(added);
    const reversed = JSON.stringify({ ...record, attributes: Object.fromEntries(Object.entries(record.attributes).reverse()) });
    const files = upull.files.map((f: { filename: string; patch?: string }) => (f === models ? { ...f, patch: f.patch!.replace(`+${added}`, `+${reversed}`) } : f));
    // Digests made consistent, so only the key order gives it away.
    const moved = [{ ...changes[0], sha256: sha(reversed), record: JSON.parse(reversed) }];
    const problems = tieStoreDiff(storeDiff(files), { batch: sources, changes: moved }).problems;
    expect(problems).toEqual([{ id: changes[0].id, text: expect.stringContaining("moves keys the change does not touch") }]);
  });

  it("refuses a change to a store file it cannot tie", () => {
    for (const filename of ["data/provenance/moved-attributes.jsonl", "data/entities/models.jsonl.gz"]) {
      const files = [...upull.files, { filename, status: "modified", patch: '+{"id":"someone-else"}' }];
      expect(tie(files).problems).toEqual([{ id: "(store diff)", text: expect.stringContaining(`${filename} changed, but it is neither a record file`) }]);
    }
  });

  it("says a report-only review is not posted", () => {
    const body = renderReview({ records: [], rows: [], verdict: "comment", sourceNotes: [], usage: new Usage(), mode: "report-only" });
    expect(body).toContain("This review is report-only: it is not posted");
  });

  it("marks a changed field the model did not judge unverifiable", async () => {
    const fs = await import("node:fs");
    const os = await import("node:os");
    const dir = fs.mkdtempSync(`${os.tmpdir()}/reviewer-update-`);
    fs.cpSync(UPDATE, dir, { recursive: true });
    const review = JSON.parse(fs.readFileSync(`${dir}/review.json`, "utf8"));
    review.records[0].fields = review.records[0].fields.filter((f: { field: string }) => f.field !== "/attributes/source_locator");
    fs.writeFileSync(`${dir}/review.json`, JSON.stringify(review));
    const r = await main(["--dry-run", "--fixtures", dir], {}, { now, log: quiet });
    fs.rmSync(dir, { recursive: true, force: true });
    expect(r.verdict).toBe("request changes");
    expect(r.rows.find((x: { field: string }) => x.field === "/attributes/source_locator").verdict).toBe("unverifiable");
  });
});

describe("the working tree as a pull request", () => {
  it("reads the store diff from git and the new batch files under data/omics", () => {
    const base = '{"id":"m","kind":"model","name":"M"}';
    const outputs: Record<string, string> = {
      diff: [
        "diff --git a/data/entities/models.jsonl b/data/entities/models.jsonl",
        "index 1..2 100644",
        "--- a/data/entities/models.jsonl",
        "+++ b/data/entities/models.jsonl",
        "@@ -3 +3 @@",
        `-${base}`,
        `+${base.replace('"M"', '"M2"')}`,
        "",
      ].join("\n"),
      "ls-files": "data/omics/update-1-20261120/changes.jsonl\ndata/omics/update-1-20261120/review.json\n",
    };
    const calls: string[] = [];
    const run = (_cmd: string, args: string[]) => {
      calls.push(args.join(" "));
      if (args[0] === "diff" && args.includes("--name-only")) return { ok: true, output: "" };
      return { ok: true, output: outputs[args[0]] ?? "" };
    };
    const pull = worktreePull(run);
    expect(calls[0]).toBe("diff --no-color --no-ext-diff -U0 HEAD -- data/entities data/evidence data/provenance");
    expect(pull.author).toBe(BOT_LOGIN);
    expect(pull.files).toEqual([
      { filename: "data/entities/models.jsonl", status: "modified", patch: `@@ -3 +3 @@\n-${base}\n+${base.replace('"M"', '"M2"')}` },
      { filename: "data/omics/update-1-20261120/changes.jsonl", status: "added" },
      { filename: "data/omics/update-1-20261120/review.json", status: "added" },
    ]);
    const diff = storeDiff(pull.files);
    expect([...diff.records.keys()]).toEqual(["m"]);
  });
});
