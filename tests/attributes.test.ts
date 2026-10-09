import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { attributeIssues, attributeTypes, convertUncertainty, normalizeAttributes } from "../shared/omics/attributes";
import { attributeRegistry } from "../shared/omics/attribute-registry";
import { addBatch, recordFile, recordSha256 } from "../scripts/omics/records";
import { readMissingLookup } from "../scripts/omics/migrate-attributes";
import { loadSchemes } from "../scripts/omics/vocab";
import { records } from "./helpers/records";

const result = (attributes: Record<string, unknown>, id = "r1") => ({
  id, kind: "result", links: [{ relation: "evaluation", target_id: "e1" }], attributes,
});
const evaluation = (attributes: Record<string, unknown> = {}) => ({ id: "e1", kind: "evaluation", links: [], attributes });
const convert = (attributes: Record<string, unknown>, parent = evaluation()) =>
  normalizeAttributes([parent, result(attributes)])[1].attributes;

describe("declared attributes", () => {
  it("holds every attribute in the store to the registry", () => {
    const problems = records.flatMap((record) => attributeIssues(record).map((issue) => `${record.id}: ${issue}`));
    expect(problems).toEqual([]);
  });

  it("leaves current records unchanged", () => {
    const again = normalizeAttributes(records);
    expect(again.filter((record, i) => record !== records[i]).map((record) => record.id)).toEqual([]);
  });

  it("rejects undeclared keys, bare nulls and a value that also has a missing reason", () => {
    expect(attributeIssues(result({ invented_key: "x" }))).toEqual(["undeclared attribute invented_key"]);
    expect(attributeIssues(result({ denominator: null }))[0]).toMatch(/null; omit it/);
    expect(attributeIssues(result({ denominator: 3, missing_metadata: { denominator: { reason: "unreported" } } })))
      .toContain("denominator has a value and a missing_metadata reason");
    expect(attributeIssues(result({ missing_metadata: { not_a_field: { reason: "unreported" } } })))
      .toContain("missing_metadata names undeclared field not_a_field");
  });

  it("turns nulls and free-text markers into one missing-reason map", () => {
    const a = convert({ denominator: null, source_discrepancy: null, missing_metadata: { seeds: "Unreported per bin", budget: "unextracted" } });
    expect(a).toEqual({
      missing_metadata: {
        budget: { reason: "unextracted" },
        denominator: { reason: "unextracted" },
        seeds: { reason: "unreported", note: "Unreported per bin" },
      },
    });
  });

  it("converts each legacy uncertainty shape to a declared type", () => {
    expect(convertUncertainty({ kind: "source_bootstrap_summary", printed_sd: "0.006", printed_mean: "0.257" }).uncertainty)
      .toEqual({ type: "standard_deviation", method: "bootstrap", value: "0.006", center: "0.257" });
    expect(convertUncertainty({ type: "bootstrap confidence interval", level: 0.999, resamples: 20000, lower: "30.40", upper: "31.21" }).uncertainty)
      .toEqual({ type: "confidence_interval", level: 0.999, lower: "30.40", upper: "31.21", resamples: 20000, method: "bootstrap" });
    expect(convertUncertainty({ type: "confidence_interval", level: "95%", low: "52.0", high: "66.4", unit: "percent" }).uncertainty)
      .toEqual({ type: "confidence_interval", level: 0.95, lower: "52.0", upper: "66.4", unit: "percent" });
    expect(convertUncertainty({ type: "standard_deviation", value: 0.9, n: 3, unit: "same_as_metric" }).uncertainty)
      .toEqual({ type: "standard_deviation", value: "0.9", n: 3 });
    expect(convertUncertainty("± 0.002 standard deviation").uncertainty)
      .toEqual({ type: "standard_deviation", printed: "± 0.002 standard deviation", value: "0.002" });
    expect(convertUncertainty({ status: "unreported" })).toEqual({ missing: { reason: "unreported" } });
    expect(convertUncertainty(null)).toEqual({ missing: { reason: "unextracted" } });
    expect(convert({ uncertainty: null })).toEqual({ missing_metadata: { uncertainty: { reason: "unextracted" } } });
    expect(convertUncertainty({ printed_spread: "nan", type: "unreported", value: null }).missing?.reason).toBe("unreported");
  });

  it("lets a stated uncertainty override a stale missing marker", () => {
    const a = convert({ uncertainty: { type: "standard_deviation", value: "0.1" }, missing_metadata: { uncertainty: "inapplicable" } });
    expect(a).toEqual({ uncertainty: { type: "standard_deviation", value: "0.1" } });
  });

  it("drops result copies of the parent evaluation's values, but keeps ones that differ", () => {
    const parent = evaluation({ total_targets: 10, evidence_overlap: "none" });
    expect(convert({ total_targets: 10, evidence_overlap: "partial" }, parent)).toEqual({ evidence_overlap: "partial" });
  });

  it("gives every review a method list and one reviewer list", () => {
    const a = convert({ review: { method: "transcription", actor: "codex", notes: "checked", reviewed_at: "2026-09-19" } });
    expect(a.review).toEqual({ method: ["transcription"], reviewer: ["codex"], note: "checked", date: "2026-09-19" });
  });

  it("maps every free-text missing reason through the reviewed table to a scheme concept", () => {
    const concepts = loadSchemes().get("missingness")!.concepts;
    for (const [text, row] of readMissingLookup())
      if (row.reason !== "not_missing") expect(concepts.has(row.reason), text).toBe(true);
  });

  it("declares every registry type", () => {
    const types = new Set(Object.values(attributeRegistry).flatMap((keys) => Object.values(keys)));
    const schemes = loadSchemes();
    for (const type of types)
      if (type.startsWith("concept:")) expect(schemes.has(type.slice(8)), type).toBe(true);
      else expect(Object.keys(attributeTypes), type).toContain(type);
  });

  it("refuses an undeclared attribute at intake", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "attributes-"));
    try {
      const source = { id: "test-source", kind: "source" as const, name: "s", description: "", status: "source_checked" as const,
        facets: {}, source_ids: [], links: [], attributes: { url: "https://example.org/paper", version: "v1", retrieved_at: "2026-10-08T00:00:00Z" } };
      fs.mkdirSync(path.dirname(recordFile("source", root)), { recursive: true });
      fs.writeFileSync(recordFile("source", root), JSON.stringify(source) + "\n");
      fs.mkdirSync(path.join(root, "data/provenance"), { recursive: true });
      fs.writeFileSync(path.join(root, "data/provenance/records.jsonl"),
        JSON.stringify({ id: source.id, sha256: recordSha256(source), added_in: "test", added_by: "test", changed_by: [] }) + "\n");
      const batch = path.join(root, "batch.jsonl");
      fs.writeFileSync(batch, JSON.stringify({ ...source, id: "test-model", kind: "model", source_ids: ["test-source"],
        attributes: { entity_level: "method", invented_key: 1 } }) + "\n");
      expect(() => addBatch(batch, "data/omics/test-batch", root)).toThrow("undeclared attribute invented_key");
    } finally {
      fs.rmSync(root, { recursive: true, force: true });
    }
  });
});
