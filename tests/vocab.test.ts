import fs from "node:fs";
import { describe, expect, it } from "vitest";
import { readMapping } from "../scripts/kg/export";
import { migratedSchemes, readCsv, readTable } from "../scripts/omics/migrate-vocab";
import { controlledValues, loadSchemes, schemeIri, validateVocabularies } from "../scripts/omics/vocab";

const mapping = readMapping();
const schemes = loadSchemes();
const mappedSchemes = [
  ...Object.values(mapping.fields),
  ...Object.values(mapping.facets),
  ...Object.values(mapping.attributes),
  ...Object.values(mapping.review),
].flatMap((term) => ((term as { scheme?: string }).scheme ? [(term as { scheme: string }).scheme] : []));

describe("controlled vocabularies", () => {
  it("has a SKOS scheme for every field the mapping marks as controlled", () => {
    for (const scheme of new Set(mappedSchemes)) {
      expect(schemes.get(scheme)?.concepts.size, scheme).toBeGreaterThan(0);
      expect(schemes.get(scheme)?.iri).toBe(schemeIri(scheme));
    }
  });

  it("gives every concept a label and no two concepts in a scheme the same label", () => {
    for (const scheme of schemes.values()) {
      const labels = [...scheme.concepts.values()].map((c) => c.label.toLowerCase());
      expect(new Set(labels).size, scheme.name).toBe(labels.length);
    }
  });

  it("maps every migration table row to concepts that exist", () => {
    for (const scheme of migratedSchemes)
      for (const row of readTable(scheme).values())
        for (const key of row.concept.split(";").map((k) => k.trim()))
          expect(schemes.get(scheme)!.concepts.has(key), `${scheme}: ${row.source_string} -> ${key}`).toBe(true);
  });

  it("rejects free text in a controlled field", () => {
    const record = { id: "x", facets: { areas: ["genomics"] }, attributes: { metric: "AUPRC" }, status: "source_checked" };
    expect(controlledValues(mapping, record).map((v) => v.field).sort()).toEqual(["attributes.metric", "facets.areas", "status"]);
    expect(() => validateVocabularies(mapping, [record], schemes)).toThrow(/is not a concept in the (area|metric) vocabulary/);
    const fixed = { ...record, facets: { areas: ["dna-genomes"] }, attributes: { metric: "auprc" } };
    expect(() => validateVocabularies(mapping, [fixed], schemes)).not.toThrow();
  });

  it("reads quoted CSV fields with commas, quotes and line breaks", () => {
    const rows = readCsv('a,b\n"x, ""y""","line one\nline two"\nplain,\n');
    expect(rows).toEqual([{ a: 'x, "y"', b: "line one\nline two" }, { a: "plain", b: "" }]);
  });

  it("keeps the migration tables and schemes in the repository", () => {
    expect(fs.existsSync("data/vocab/migration/metric.csv")).toBe(true);
    expect(fs.existsSync("data/vocab/metric.ttl")).toBe(true);
  });
});
