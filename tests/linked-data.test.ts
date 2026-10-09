import fs from "node:fs";
import { describe, expect, it } from "vitest";
import { Parser } from "n3";
import { buildContext, contextFile, exportQuads, readMapping, recordQuads } from "../scripts/kg/export";
import { kinds } from "../scripts/omics/schema";
import { relations as catalogueRelations } from "../shared/omics/relations";
import { records, recordsById } from "./helpers/records";
// eslint-disable-next-line @typescript-eslint/no-require-imports
const jsonld = require("jsonld");

const mapping = readMapping();
const RB = mapping.vocab;
const ID = mapping.base;

describe("ontology mapping", () => {
  it("maps every record kind and link relation", () => {
    expect(Object.keys(mapping.classes).sort()).toEqual([...kinds].sort());
    expect(Object.keys(mapping.relations).sort()).toEqual([...catalogueRelations].sort());
  });

  it("never equates aliases or lets a pipeline's model count as evaluated", () => {
    const properties = Object.values(mapping.relations).map((r) => r.property);
    expect(properties).not.toContain("owl:sameAs");
    expect(mapping.relations.uses_model.property).not.toBe(mapping.relations.system.property);
    expect(new Set(properties).size).toBe(properties.length); // one property per relation
  });

  it("keeps the committed JSON-LD context in step with the mapping", () => {
    expect(JSON.parse(fs.readFileSync(contextFile, "utf8"))).toEqual(buildContext(mapping));
  });
});

describe("JSON-LD view of canonical records", () => {
  const context = buildContext(mapping);
  const expandRecord = async (id: string) =>
    jsonld.toRDF({ ...context, ...recordsById.get(id) }, { format: "application/n-quads" }) as Promise<string>;

  it("reads a result line as typed linked data", async () => {
    const result = records.find((r) => r.kind === "result" && r.attributes.printed_value)!;
    const nquads = await expandRecord(result.id);
    expect(nquads).toContain(`<${ID}${result.id}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <${RB}Result>`);
    expect(nquads).toContain(`<${ID}${result.id}> <${RB}printedValue> "${String(result.attributes.printed_value).replace(/"/g, '\\"')}"`);
    const evaluation = result.links.find((l) => l.relation === "evaluation")!.target_id;
    expect(nquads).toContain(`<${RB}target> <${ID}${evaluation}>`);
  });

  it("resolves source URLs as IRIs", async () => {
    const source = records.find((r) => r.kind === "source" && String(r.attributes.url).startsWith("https://"))!;
    const nquads = await expandRecord(source.id);
    expect(nquads).toContain(`<https://schema.org/url> <${String(source.attributes.url)}>`);
  });
});

describe("N-Quads export", () => {
  const sample = records.filter((_, i) => i % 97 === 0);
  const nquads = exportQuads(mapping, sample);

  it("parses as N-Quads in one named graph", () => {
    const quads = new Parser({ format: "N-Quads" }).parse(nquads);
    expect(quads.length).toBe(nquads.trim().split("\n").length);
    expect(new Set(quads.map((q) => q.graph.value))).toEqual(new Set([mapping.graph]));
  });

  it("is deterministic and sorted", () => {
    expect(exportQuads(mapping, [...sample].reverse())).toBe(nquads);
    const lines = nquads.trim().split("\n");
    expect([...lines].sort()).toEqual(lines);
  });

  it("types every record and links evaluations to what was actually evaluated", () => {
    const evaluation = records.find((r) => r.kind === "evaluation")!;
    const lines = recordQuads(mapping, evaluation);
    const subject = evaluation.links.find((l) => l.relation === "system")!.target_id;
    expect(lines.some((l) => l.includes(`<${RB}testedSystem> <${ID}${subject}>`))).toBe(true);
    expect(lines.some((l) => l.includes("http://www.w3.org/ns/mls#Run"))).toBe(true);
  });

  it("exports controlled values, including facets, as concept IRIs", () => {
    const result = records.find((r) => r.kind === "result" && r.status === "source_checked")!;
    const withArea = records.find((r) => (r.facets.areas ?? []).length > 0)!;
    const lines = [...recordQuads(mapping, result), ...recordQuads(mapping, withArea)];
    expect(lines.some((l) => l.includes(`<${RB}metric> <https://benchmarks.rewire.it/vocab/metric/${result.attributes.metric}>`))).toBe(true);
    expect(lines.some((l) => l.includes(`<${RB}area> <https://benchmarks.rewire.it/vocab/area/${withArea.facets.areas[0]}>`))).toBe(true);
    expect(lines.some((l) => /<https:\/\/benchmarks\.rewire\.it\/vocab#(metric|area|status|unit)> "/.test(l))).toBe(false);
  });

  it("exports each review method and reviewer in a list", () => {
    const reviewed = records.find((r) => ((r.attributes.review as { method?: string[] } | undefined)?.method?.length ?? 0) > 1)!;
    const methods = (reviewed.attributes.review as { method: string[] }).method;
    const lines = recordQuads(mapping, reviewed);
    for (const method of methods)
      expect(lines.some((l) => l.includes(`<${RB}reviewMethod> <https://benchmarks.rewire.it/vocab/review-method/${method}>`)), method).toBe(true);
  });

  it("gives baselines and dataset subsets their own relations, distinct from evaluations'", () => {
    const baseline = records.find((r) => r.kind === "baseline" && r.links.some((l) => l.relation === "measured_in"))!;
    const lines = recordQuads(mapping, baseline);
    expect(lines.some((l) => l.includes(`<${RB}measuredIn>`))).toBe(true);
    expect(lines.some((l) => l.includes(`<${RB}evaluation>`) || l.includes(`<${RB}testedSystem>`))).toBe(false);
    const subset = records.find((r) => r.kind === "dataset_subset" && r.links.some((l) => l.relation === "used_in"))!;
    const subsetLines = recordQuads(mapping, subset);
    expect(subsetLines.some((l) => l.includes(`<${RB}usedIn>`))).toBe(true);
    expect(subsetLines.some((l) => l.includes(`<${RB}testedOn>`))).toBe(false);
  });
});
