// The intake agent with the knowledge graph (rdf-kg-mcp): possible duplicates the verifier rules
// on, links to store records and siblings, and the batch written through the draft overlay. The
// server is replaced by a fake here; .github/workflows/intake.yml runs the real one on the bundle
// in tests/agents-intake-kg-fixtures/bundle on every pull request that touches the agents.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import {
  dupeRulings,
  draftThroughKg,
  kgCandidates,
  kgTools,
  main,
  nameOverlap,
  needsRuling,
  pruneRecords,
  resolveLinks,
} from "../scripts/agents/intake.mjs";
import { kgApi, startKg, toolResult } from "../scripts/agents/kg.mjs";
import { buildTable, mechanicalProblems, possibleDuplicates, reviewInput, withReceipt } from "../scripts/agents/reviewer.mjs";

const FIXTURES = "tests/agents-intake-kg-fixtures";
const now = () => new Date("2026-11-20T10:00:00Z");
const quiet = () => {};
const BASE = "https://benchmarks.rewire.it/id/";

/** The release records the fake server knows, by id. */
const RELEASE: Record<string, { kind: string; label: string }> = {
  "cell-type-20261009-model-uce": { kind: "model", label: "UCE (Universal Cell Embeddings)" },
  "catalog-model-evo-2": { kind: "model", label: "Evo 2" },
  "discovery-model-evo-2": { kind: "model", label: "Evo 2" },
  "mrnabench-method-evo2": { kind: "configuration", label: "Evo2" },
  "catalog-model-dnabert-2": { kind: "model", label: "DNABERT-2" },
};
const CLASS: Record<string, string> = { model: "rb:Model", method: "rb:Method", configuration: "rb:Configuration", dataset: "rb:Dataset", benchmark: "rb:Benchmark", source: "rb:Source" };

const sortDeep = (v: unknown): unknown =>
  Array.isArray(v) ? v.map(sortDeep) : v && typeof v === "object" ? Object.fromEntries(Object.keys(v).sort().map((k) => [k, sortDeep((v as Record<string, unknown>)[k])])) : v;

/** A fake rdf-kg-mcp: possible duplicates by shared words, an overlay, and an export like the server's. */
function fakeKg({ problems = {} as Record<string, string[]> } = {}) {
  const drafts = new Map<string, any>();
  const calls: string[] = [];
  const words = (t: string) => t.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim().split(" ");
  const squash = (t: string) => t.toLowerCase().replace(/[^a-z0-9]/g, "");
  const dupes = (r: any) =>
    Object.entries(RELEASE)
      .filter(([, x]) => squash(x.label) === squash(r.name) || words(x.label).some((w) => w.length > 1 && words(r.name).includes(w)))
      .map(([id, x]) => ({ id, in: "release", kind: x.kind, label: x.label, match: squash(x.label) === squash(r.name) ? "same name" : "search" }));
  const client = {
    async callTool({ name, arguments: args }: { name: string; arguments: any }) {
      calls.push(name);
      let out: any;
      if (name === "draft_upsert") {
        const r = args.record;
        if (RELEASE[r.id]) return { isError: true, content: [{ type: "text", text: `${r.id} is already in release` }] };
        drafts.set(r.id, r);
        out = { id: r.id, status: "added", problems: problems[r.id] ?? [], warnings: [], possible_duplicates: dupes(r) };
      } else if (name === "draft_remove") {
        out = { id: args.id, removed: drafts.delete(args.id) };
      } else if (name === "search") {
        const hits = Object.entries(RELEASE)
          .filter(([, x]) => words(x.label).some((w) => words(args.text).includes(w)))
          .filter(([, x]) => !args.types || args.types.includes(CLASS[x.kind]))
          .map(([id, x]) => ({ id: `id:${id}`, iri: BASE + id, label: x.label, types: [CLASS[x.kind]], score: 1, matched: ["label"] }));
        out = { query: args.text, results: hits };
      } else if (name === "describe_resource") {
        const id = String(args.iri).slice(BASE.length);
        out = { iri: args.iri, label: RELEASE[id]?.label, types: [CLASS[RELEASE[id]?.kind]], outgoing: { statements: [{ predicate: "dcterms:description", object: '"A stored record."' }] } };
      } else if (name === "draft_export") {
        const bad = [...drafts.keys()].filter((id) => problems[id]?.length);
        if (bad.length) out = { exported: false, problems: Object.fromEntries(bad.map((id) => [id, problems[id]])) };
        else {
          const batch = [...drafts.keys()].sort().map((id) => {
            const r = drafts.get(id);
            return JSON.stringify({ ...r, facets: sortDeep(r.facets), attributes: sortDeep(r.attributes) }) + "\n";
          }).join("");
          out = { exported: true, batch, batch_sha256: "f".repeat(64), summary: { release: "fake", added: [...drafts.keys()].sort().map((id) => ({ id, kind: drafts.get(id).kind, label: drafts.get(id).name, links: drafts.get(id).links, warnings: [], possible_duplicates: [] })) } };
        }
      } else throw new Error(`unknown tool ${name}`);
      return { content: [{ type: "text", text: JSON.stringify(out) }], structuredContent: out };
    },
  };
  const kg = kgApi(client, { config: { iri_base: BASE, kinds: CLASS }, stats: { calls: {}, ms: 0, release: "fake", statements: 5 } as any });
  return { kg, drafts, calls };
}

const tempRoot = () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "intake-kg-"));
  fs.mkdirSync(path.join(root, "data/entities"), { recursive: true });
  return root;
};

describe("names and duplicate rulings", () => {
  it("compares distinctive words, not kind words or bare numbers", () => {
    expect(nameOverlap("Universal Cell Embeddings", "UCE (Universal Cell Embeddings)")).toBe(1);
    expect(nameOverlap("Evo2", "Evo 2")).toBe(1);
    expect(nameOverlap("Helixgram splice benchmark", "DeepProtein benchmark")).toBe(0);
    expect(nameOverlap("Evo 2 fixture 1B base", "DNABERT-2")).toBe(0);
    expect(nameOverlap("hEVO-base-o", "hEvo")).toBe(1);
    // Size words and single letters name a checkpoint, not a resource (seen on #250).
    expect(nameOverlap("hEVO-large-o", "Bacformer Large")).toBe(0);
  });

  it("asks for a ruling only on the same kind, or model against method", () => {
    expect(needsRuling("model", "Evo2", { kind: "model", label: "Evo 2", match: "same name" })).toBe(true);
    expect(needsRuling("model", "Evo2", { kind: "configuration", label: "Evo2", match: "same name" })).toBe(false);
    expect(needsRuling("model", "Evo2", { kind: "method", label: "Evo 2", match: "search" })).toBe(true);
    expect(needsRuling("benchmark", "Helixgram splice benchmark", { kind: "benchmark", label: "DeepProtein benchmark", match: "search" })).toBe(false);
  });

  it("drops an entity ruled the same, and one with an unruled possible duplicate", () => {
    const dupes = [{ id: "a", kind: "model", label: "A" }, { id: "b", kind: "model", label: "B" }];
    const same = dupeRulings({ duplicates: [{ id: "a", ruling: "same", locator: "README" }, { id: "b", ruling: "distinct", locator: "x" }] }, dupes);
    expect(same.duplicateOf?.id).toBe("a");
    const unruled = dupeRulings({ duplicates: [{ id: "a", ruling: "distinct", locator: "README" }] }, dupes);
    expect(unruled.unruled.map((d) => d.id)).toEqual(["b"]);
    // The record's name in place of its id still counts (the structuring call wrote one on #250).
    expect(dupeRulings({ duplicates: [{ id: "B", ruling: "distinct", locator: "x" }, { id: "a", ruling: "distinct", locator: "y" }] }, dupes).unruled).toEqual([]);
    // A ruling without a locator is no ruling.
    expect(dupeRulings({ duplicates: [{ id: "a", ruling: "distinct", locator: "" }] }, dupes.slice(0, 1)).unruled).toHaveLength(1);
  });
});

describe("links", () => {
  const built = [
    { id: "b-model-x-1b", key: "e2", kind: "model", name: "X 1B" },
    { id: "b-dataset-c", key: "e3", kind: "dataset", name: "C" },
    { id: "b-benchmark-v", key: "e4", kind: "benchmark", name: "V" },
  ];
  const entities = [{ key: "e1", name: "X" }, { key: "e2", name: "X 1B" }, { key: "e3", name: "C" }, { key: "e4", name: "V" }];
  const known = new Map([["store-model-x", { id: "store-model-x", kind: "model", name: "X" }]]);
  const link = (relation: string, target: string, verdict = "supported", locator = "paper, section 1") => ({ relation, target, verdict, locator });

  it("resolves sibling keys and store ids, and refuses what the rules or the sources do not allow", () => {
    const verification = {
      entities: [
        { key: "e2", name: "X 1B", links: [link("family", "store-model-x"), link("variant_of", "e1"), link("uses_data", "e3"), link("alias_of", "store-model-x", "unsupported")] },
        { key: "e4", name: "V", links: [link("uses_data", "e3"), link("part_of", "store-model-x"), link("evaluates_task", "made-up-id")] },
      ],
    };
    const { links, log, rejected } = resolveLinks({ built, verification, entities, known });
    expect(links.get("b-model-x-1b")).toEqual([{ relation: "family", target_id: "store-model-x" }]);
    expect(links.get("b-benchmark-v")).toEqual([{ relation: "uses_data", target_id: "b-dataset-c" }]);
    expect(log.map((l) => l.in)).toEqual(["store", "batch"]);
    expect(rejected.map((r) => r.reason)).toEqual([
      "the target entity was not added",
      "the intake agent does not write uses_data links from a model",
      "not supported at a location in a source",
      "part_of cannot link a benchmark to a model",
      "the target is neither a kept entity in this batch nor a store record the run looked up",
    ]);
  });

  it("prunes links to dropped records and sources nobody cites", () => {
    const records = [
      { id: "m", kind: "model", source_ids: ["s1"], links: [{ relation: "variant_of", target_id: "n" }], facets: { areas: ["dna-genomes"], contexts: ["research"] } },
      { id: "n", kind: "model", source_ids: ["s2"], links: [], facets: { areas: ["proteins-complexes"], contexts: ["research"] } },
      { id: "s1", kind: "source", source_ids: [], links: [], facets: {} },
      { id: "s2", kind: "source", source_ids: [], links: [], facets: {} },
    ];
    const kept = pruneRecords(records, ["n"]);
    expect(kept.map((r) => r.id)).toEqual(["m", "s1"]);
    expect(kept[0].links).toEqual([]);
    expect(kept[1].facets).toEqual({ areas: ["dna-genomes"], contexts: ["research"] });
  });
});

describe("the knowledge-graph client", () => {
  it("reads structured content, JSON text and tool errors", () => {
    expect(toolResult("x", { structuredContent: { a: 1 }, content: [] })).toEqual({ a: 1 });
    expect(toolResult("x", { structuredContent: { result: [1] }, content: [] })).toEqual([1]);
    expect(toolResult("x", { content: [{ type: "text", text: '{"b":2}' }] })).toEqual({ b: 2 });
    expect(() => toolResult("x", { isError: true, content: [{ type: "text", text: "nope" }] })).toThrow("x: nope");
  });

  it("falls back when there is no bundle or the server does not start", async () => {
    expect((await startKg({ bundle: "", draftConfig: "", draftDir: "" })).error).toMatch(/no KG bundle/);
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "kg-"));
    const config = path.join(dir, "draft.json");
    fs.writeFileSync(config, JSON.stringify({ iri_base: BASE, kinds: CLASS }));
    const failing = await startKg({ bundle: "b.tar.gz", draftConfig: config, draftDir: path.join(dir, "d") }, { connect: async () => { throw new Error("spawn rdf-kg-mcp ENOENT"); } });
    expect(failing).toEqual({ kg: null, error: "spawn rdf-kg-mcp ENOENT" });
    const slow = await startKg({ bundle: "b.tar.gz", draftConfig: config, draftDir: path.join(dir, "d"), timeoutMs: 20 }, { connect: () => new Promise(() => {}) });
    expect(slow.error).toMatch(/not ready/);
  });

  it("lists possible duplicates per entity and link targets of the allowed kinds", async () => {
    const { kg } = fakeKg();
    const c = await kgCandidates(kg, [{ key: "e1", kind: "model", name: "Evo2", aliases: [] }, { key: "e2", kind: "model", name: "Evo 2 fixture 1B base", aliases: [] }]);
    expect(c.get("e1")!.duplicates.map((d) => d.id)).toEqual(["catalog-model-evo-2", "discovery-model-evo-2"]);
    expect(c.get("e2")!.duplicates.map((d) => d.id)).toEqual(["catalog-model-evo-2", "discovery-model-evo-2"]);
    // The configuration named Evo2 is a link target candidate, not a duplicate.
    expect(c.get("e2")!.related.map((d) => d.id)).toContain("catalog-model-dnabert-2");
    const tools = kgTools(kg);
    expect(tools.definitions.map((d) => d.name)).toEqual(["kg_search", "kg_describe"]);
    const hits = await tools.handle("kg_search", { text: "Evo", kinds: ["model"] });
    expect(hits.map((h: any) => h.id)).toEqual(["catalog-model-evo-2", "discovery-model-evo-2"]);
    expect((await tools.handle("kg_describe", { id: "catalog-model-evo-2" })).kind).toBe("model");
    expect(tools.seen.get("catalog-model-evo-2")?.kind).toBe("model");
  });

  it("drops an entity the overlay finds problems in, and one with a new unruled duplicate", async () => {
    const { kg } = fakeKg({ problems: { m2: ["attributes: bad"] } });
    const rec = (id: string, kind: string, name: string, extra: any = {}) => ({ id, kind, name, description: "d", status: "discovered", facets: { areas: ["dna-genomes"], contexts: ["research"] }, source_ids: kind === "source" ? [] : ["s1"], links: [], attributes: { z: 1, a: { y: 2, b: 3 } }, ...extra });
    const out = await draftThroughKg(kg, [rec("m1", "model", "Helixgram"), rec("m2", "model", "Other"), rec("m3", "model", "Evo 2 base"), rec("s1", "source", "Page")], { ruled: new Map([["m3", new Set(["catalog-model-evo-2"])]]) });
    expect(out.error).toBeUndefined();
    expect(out.records!.map((r) => r.id)).toEqual(["m1", "s1"]);
    expect(out.dropped!.map((d) => d.id)).toEqual(["m2", "m3"]);
    expect(out.dropped![1].reason).toContain("discovery-model-evo-2");
    // Keys inside attributes come out sorted, at every depth.
    expect(out.batchText!.split("\n")[0]).toContain('"attributes":{"a":{"b":3,"y":2},"z":1}');
  });
});

describe("intake dry run with the knowledge graph", () => {
  it("drops the duplicate the verifier ruled the same, links to the store and writes the overlay's batch", async () => {
    const root = tempRoot();
    const out = path.join(root, "out");
    const { kg, calls } = fakeKg();
    const result = await main(["--dry-run", "--fixtures", FIXTURES, "--root", root, "--no-store-checks", "--out", out], {}, { now, log: quiet, kg });
    expect(result.outcome).toBe("ready: pull request not opened in this mode");
    expect(result.dropped.find((d: any) => d.name === "Universal Cell Embeddings")?.duplicate).toBe("cell-type-20261009-model-uce");
    const ids = result.records.map((r: any) => r.id);
    expect(ids).toContain("intake-9998-20261120-model-evo-2-fixture-1b-base");
    const model = result.records.find((r: any) => r.id === "intake-9998-20261120-model-evo-2-fixture-1b-base");
    expect(model.links).toEqual([{ relation: "family", target_id: "catalog-model-evo-2" }]);
    const bench = result.records.find((r: any) => r.kind === "benchmark");
    expect(bench.links).toEqual([{ relation: "uses_data", target_id: "intake-9998-20261120-dataset-evo-2-fixture-corpus" }]);
    expect(calls).toContain("draft_export");
    const dir = path.join(root, result.batchDir);
    const batch = fs.readFileSync(path.join(dir, "batch.jsonl"), "utf8");
    // The batch is the overlay's export: attribute keys sorted.
    for (const line of batch.trim().split("\n")) {
      const keys = Object.keys(JSON.parse(line).attributes);
      expect(keys).toEqual([...keys].sort());
    }
    const receipt = JSON.parse(fs.readFileSync(path.join(dir, "kg.json"), "utf8"));
    expect(receipt.links.map((l: any) => [l.relation, l.in])).toEqual([["family", "store"], ["uses_data", "batch"]]);
    expect(receipt.duplicate_rulings.map((d: any) => [d.id, d.ruling])).toEqual([
      ["cell-type-20261009-model-uce", "same"],
      ["catalog-model-evo-2", "distinct"],
      ["discovery-model-evo-2", "distinct"],
    ]);
    const review = JSON.parse(fs.readFileSync(path.join(dir, "review.json"), "utf8"));
    expect(review.limitations.join(" ")).toContain("kg.json lists each with its locator");
    expect(fs.readFileSync(path.join(dir, "notes.md"), "utf8")).toContain("## Links");
    const written = JSON.parse(fs.readFileSync(path.join(out, "result.json"), "utf8"));
    expect(written.kg.used).toBe(true);
    expect(written.links).toHaveLength(2);
  });

  it("falls back to name checks when the server is not available", async () => {
    const root = tempRoot();
    const result = await main(["--dry-run", "--fixtures", FIXTURES, "--root", root, "--no-store-checks"], {}, { now, log: quiet, kg: null });
    // No store candidates: nothing to rule on, so the UCE request is kept; links reach siblings only.
    expect(result.records.some((r: any) => r.id.endsWith("model-universal-cell-embeddings"))).toBe(true);
    const model = result.records.find((r: any) => r.id.endsWith("evo-2-fixture-1b-base"));
    expect(model.links).toEqual([{ relation: "variant_of", target_id: "intake-9998-20261120-model-universal-cell-embeddings" }]);
  });
});

describe("the reviewer's link and duplicate checks", () => {
  const model = { id: "b-model-x-1b", kind: "model", name: "Evo 2 base", source_ids: ["s1"], facets: { areas: ["dna-genomes"] }, attributes: { depth_tier: 1, entity_level: "checkpoint" }, links: [{ relation: "family", target_id: "catalog-model-evo-2" }] };
  const bench = { id: "b-bench", kind: "benchmark", name: "V", source_ids: ["s1"], facets: { areas: ["dna-genomes"] }, attributes: { depth_tier: 1, entity_level: "suite" }, links: [{ relation: "uses_data", target_id: "missing-dataset" }, { relation: "part_of", target_id: "catalog-model-evo-2" }] };
  const source = { id: "s1", kind: "source", name: "Page", source_ids: [], facets: {}, attributes: { url: "https://example.org/p" }, links: [] };
  const receipt = {
    links: [{ from: "b-model-x-1b", relation: "family", to: "catalog-model-evo-2", to_name: "Evo 2", in: "store", locator: "preprint, section 1" }],
    duplicate_rulings: [{ entity: "Evo 2 base", id: "catalog-model-evo-2", label: "Evo 2", ruling: "distinct", locator: "preprint, section 1" }],
    summary: { added: [{ id: "b-model-x-1b", possible_duplicates: [{ id: "catalog-model-evo-2", in: "release", kind: "model", label: "Evo 2", match: "search" }, { id: "discovery-model-evo-2", in: "release", kind: "model", label: "Evo 2", match: "search" }] }] },
  };
  const storeKinds = new Map([["catalog-model-evo-2", "model"], ["discovery-model-evo-2", "model"]]);

  it("checks each link's target, kind and locator, and asks for a ruling on each possible duplicate", async () => {
    const records = withReceipt([model, bench, source], receipt);
    const kgDuplicates = await possibleDuplicates(records, { receipt });
    expect(kgDuplicates.get("b-model-x-1b")!.map((d) => d.id)).toEqual(["catalog-model-evo-2", "discovery-model-evo-2"]);
    const problems = mechanicalProblems(records, { storeNames: new Map(), storeSourceIds: new Set(), storeKinds, receipt, kgDuplicates });
    const text = problems.map((p) => `${p.id} ${p.field}: ${p.text}`);
    expect(text).toContain('b-model-x-1b duplicates: possible duplicate discovery-model-evo-2 ("Evo 2") in the store has no ruling in kg.json');
    expect(text).toContain("b-bench links: uses_data missing-dataset: the target is neither in this pull request nor in the store");
    expect(text.some((t) => t.startsWith("b-bench links: part_of cannot link a benchmark to a model"))).toBe(true);
    expect(text.filter((t) => t.startsWith("b-model-x-1b links"))).toEqual([]);
    // The model sees each link's locator and each ruling, and judges both fields.
    const input = reviewInput(records);
    expect(input[0].links[0]).toMatchObject({ relation: "family", locator: "preprint, section 1", target_name: "Evo 2" });
    expect(input[0].duplicate_rulings[0].ruling).toBe("distinct");
    const rows = buildTable(records, { records: [] }, problems);
    expect(rows.filter((r) => r.id === "b-model-x-1b").map((r) => r.field)).toEqual(expect.arrayContaining(["links", "duplicates"]));
  });

  it("finds possible duplicates with its own search when the graph is loaded", async () => {
    const { kg } = fakeKg();
    const found = await possibleDuplicates([model], { kg });
    expect(found.get("b-model-x-1b")!.map((d) => d.id)).toEqual(["catalog-model-evo-2", "discovery-model-evo-2"]);
  });
});
