import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";
import { afterEach, describe, expect, it } from "vitest";
import { addBatch, loadRecords, recordFile, recordSha256 } from "../scripts/omics/records";
import type { RecordEntry } from "../scripts/omics/schema";
import { readMapping, recordQuads } from "../scripts/kg/export";
import { createCatalogueQuery } from "../shared/omics/catalogue-query";
import { createEvidenceIndex } from "../shared/omics/evidence-table";
import { fixture } from "./fixtures/catalogue";

const roots: string[] = [];
afterEach(() => { for (const root of roots.splice(0)) fs.rmSync(root, { recursive: true, force: true }); });

const sha = (text: string) => crypto.createHash("sha256").update(text).digest("hex");
const script = "scripts/derive/example.py";
const scriptText = "print('0.123')\n";
const workbookSha = "a".repeat(64);
const doi = "10.1000/example";

const base = (id: string, kind: RecordEntry["kind"], attributes: Record<string, unknown>, links: RecordEntry["links"] = []): RecordEntry => ({
  id, kind, name: id, description: "", status: "needs_review", facets: {},
  source_ids: kind === "source" ? [] : ["paper"], links, attributes,
});
const source = (id: string, extra: Record<string, unknown>) =>
  base(id, "source", { url: `https://example.org/${id}`, version: "v1", retrieved_at: "2026-10-11T00:00:00Z", doi, ...extra });

const derivation = (extra: Record<string, unknown> = {}) => ({
  method: "computed-from-source-data",
  inputs: [{ source_id: "workbook", artifact_sha256: workbookSha, locator: "Source Data Fig. 1, sheet \"Panel A\"", row_filter: "method == \"a\"", row_count: 310 }],
  aggregation: "The horizontal red lines show the mean per model",
  aggregation_source_id: "paper",
  aggregation_locator: "Fig. 1 legend",
  script,
  script_sha256: sha(scriptText),
  precision: "rounded half to even to 3 decimal places",
  ...extra,
});
const result = (attributes: Record<string, unknown> = {}) => ({
  ...base("derived-result", "result", {
    printed_value: "0.123", numeric_value: "0.123", metric: "pearson-delta", metric_direction: "higher", unit: "unitless",
    source_locator: "Source Data Fig. 1, sheet \"Panel A\", rows with method \"a\"", derivation: derivation(), ...attributes,
  }, [{ relation: "evaluation", target_id: "evaluation" }]),
  source_ids: ["paper", "workbook"],
});

function store() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "derivations-"));
  roots.push(root);
  const records = [
    source("paper", {}),
    source("workbook", { artifact_sha256: workbookSha }),
    source("other-paper", { doi: "10.1000/other", artifact_sha256: "b".repeat(64) }),
    base("model", "model", { entity_level: "method" }),
    base("protocol", "protocol", {}),
    base("dataset", "dataset", {}),
    base("evaluation", "evaluation", { origin: "author_reported", comparison: {} }, [
      { relation: "system", target_id: "model" }, { relation: "assessment", target_id: "protocol" }, { relation: "data", target_id: "dataset" },
    ]),
  ].sort((a, b) => (a.id < b.id ? -1 : 1));
  for (const r of records) {
    fs.mkdirSync(path.dirname(recordFile(r.kind, root)), { recursive: true });
    fs.appendFileSync(recordFile(r.kind, root), JSON.stringify(r) + "\n");
  }
  fs.mkdirSync(path.join(root, "data/provenance"), { recursive: true });
  fs.writeFileSync(path.join(root, "data/provenance/records.jsonl"), records.map((r) => JSON.stringify({
    id: r.id, sha256: recordSha256(r), added_in: "test", added_by: "test", changed_by: [],
  }) + "\n").join(""));
  fs.mkdirSync(path.join(root, path.dirname(script)), { recursive: true });
  fs.writeFileSync(path.join(root, script), scriptText);
  return root;
}
const add = (root: string, record: unknown) => {
  const batch = path.join(root, "batch.jsonl");
  fs.writeFileSync(batch, JSON.stringify(record) + "\n");
  return addBatch(batch, "data/omics/test-batch", root);
};

describe("results computed from a source's own data", () => {
  it("accepts a derivation whose script and inputs match their hashes", () => {
    const root = store();
    expect(add(root, result())).toBe(1);
    expect(loadRecords(root).find((r) => r.id === "derived-result")?.attributes.derivation).toEqual(derivation());
  });

  it("rejects a missing script", () => {
    const root = store();
    fs.rmSync(path.join(root, script));
    expect(() => add(root, result())).toThrow(`script ${script} does not exist`);
  });

  it("rejects a script that does not match its hash", () => {
    const root = store();
    fs.writeFileSync(path.join(root, script), "print('0.124')\n");
    expect(() => add(root, result())).toThrow(`script ${script} has sha256`);
  });

  it("rejects an input whose hash differs from its source record", () => {
    const root = store();
    const inputs = [{ ...derivation().inputs[0], artifact_sha256: "c".repeat(64) }];
    expect(() => add(root, result({ derivation: derivation({ inputs }) }))).toThrow("but the source record has");
  });

  it("rejects a derivation with no stated aggregation", () => {
    const root = store();
    const { aggregation: _, ...withoutAggregation } = derivation();
    expect(() => add(root, result({ derivation: withoutAggregation }))).toThrow("derivation is not derivation");
  });

  it("rejects data from another publication", () => {
    const root = store();
    const inputs = [{ ...derivation().inputs[0], source_id: "other-paper", artifact_sha256: "b".repeat(64) }];
    const record = { ...result({ derivation: derivation({ inputs }) }), source_ids: ["paper", "other-paper"] };
    expect(() => add(root, record)).toThrow("same doi");
  });

  it("rejects a derivation method outside its scheme", () => {
    const root = store();
    expect(() => add(root, result({ derivation: derivation({ method: "read-from-figure" }) }))).toThrow("derivation-method vocabulary");
  });

  it("exports the derivation and its inputs as typed nodes", () => {
    const root = store();
    add(root, result());
    const quads = recordQuads(readMapping(), loadRecords(root).find((r) => r.id === "derived-result")!);
    const id = "https://benchmarks.rewire.it/id/derived-result";
    const rb = "https://benchmarks.rewire.it/vocab#";
    expect(quads.some((q) => q.startsWith(`<${id}> <${rb}derivation> <${id}/derivation>`))).toBe(true);
    expect(quads.some((q) => q.startsWith(`<${id}/derivation> <${rb}derivationMethod> <https://benchmarks.rewire.it/vocab/derivation-method/computed-from-source-data>`))).toBe(true);
    expect(quads.some((q) => q.startsWith(`<${id}/derivation/inputs/0> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <${rb}DerivationInput>`))).toBe(true);
    expect(quads.some((q) => q.startsWith(`<${id}/derivation/inputs/0> <${rb}inputSource> <https://benchmarks.rewire.it/id/workbook>`))).toBe(true);
    expect(quads.some((q) => q.includes(`<${rb}rowCount> "310"^^<http://www.w3.org/2001/XMLSchema#integer>`))).toBe(true);
  });

  it("compares a derived result with a printed one under the same checks, and labels it", () => {
    const snapshot = fixture();
    const printed = snapshot.records.find((r: any) => r.id === "result-one");
    const evaluation = snapshot.records.find((r: any) => r.id === "evaluation-one");
    const derived = structuredClone(printed);
    derived.id = "result-two";
    derived.links[0].target_id = "evaluation-two";
    derived.attributes.derivation = derivation({ aggregation_source_id: printed.source_ids[0] });
    const secondEval = structuredClone(evaluation);
    secondEval.id = "evaluation-two";
    snapshot.records.push(derived, secondEval);
    const compare = () => createCatalogueQuery(snapshot).compare({ ids: ["result-one", "result-two"] });
    expect(compare().compatible).toBe(true);
    secondEval.attributes.comparison.aggregation = "median over perturbations";
    expect(compare().reasons).toContain("aggregation differs between evaluations.");
    const rows = createEvidenceIndex(snapshot).all().filter((row: any) => row.field_path === "attributes.printed_value");
    expect(rows.find((row: any) => row.record_id === "result-two")?.property).toBe("Computed by Rewire from source data");
    expect(rows.find((row: any) => row.record_id === "result-one")?.property).toBe("Reported result");
  });
});
