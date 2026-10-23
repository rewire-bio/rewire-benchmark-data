import fs from "node:fs";
import os from "node:os";
import path from "node:path";
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

  it("maps every migration table row to concepts that exist or that a later correction retired", () => {
    // A concept retired after the migration must have had its records moved by a reviewed
    // correction table, so the history stays traceable.
    const retired = new Set(
      fs.readdirSync("data/vocab/corrections").flatMap((file) =>
        readCsv(fs.readFileSync(`data/vocab/corrections/${file}`, "utf8")).map((row) => row.old_value),
      ),
    );
    for (const scheme of migratedSchemes)
      for (const row of readTable(scheme).values())
        for (const key of row.concept.split(";").map((k) => k.trim()))
          expect(schemes.get(scheme)!.concepts.has(key) || retired.has(key), `${scheme}: ${row.source_string} -> ${key}`).toBe(true);
  });

  it("rejects free text in a controlled field", () => {
    const record = { id: "x", facets: { areas: ["genomics"] }, attributes: { metric: "AUPRC" }, status: "source_checked" };
    expect(controlledValues(mapping, record).map((v) => v.field).sort()).toEqual(["attributes.metric", "facets.areas", "status"]);
    expect(() => validateVocabularies(mapping, [record], schemes)).toThrow(/is not a concept in the (area|metric) vocabulary/);
    const fixed = { ...record, facets: { areas: ["dna-genomes"] }, attributes: { metric: "auprc" } };
    expect(() => validateVocabularies(mapping, [fixed], schemes)).not.toThrow();
  });

  it("rejects links to concepts that do not exist, scheme mismatches and broader cycles", () => {
    const head = (name: string) => `@prefix skos: <http://www.w3.org/2004/02/skos/core#> .\n@prefix : <${schemeIri(name)}> .\n<${schemeIri(name)}> a skos:ConceptScheme .\n`;
    const concept = (name: string, key: string, extra = "") =>
      `:${key} a skos:Concept ; skos:inScheme <${schemeIri(name)}> ; skos:prefLabel "${key}"@en${extra} .\n`;
    const load = (files: Record<string, string>) => {
      const root = fs.mkdtempSync(path.join(os.tmpdir(), "vocab-"));
      fs.mkdirSync(path.join(root, "data/vocab"), { recursive: true });
      for (const [name, body] of Object.entries(files)) fs.writeFileSync(path.join(root, "data/vocab", `${name}.ttl`), head(name) + body);
      return () => loadSchemes(root);
    };
    const dir = concept("direction", "higher");
    const ok = load({ direction: dir, metric: concept("metric", "a") + concept("metric", "b", ` ; skos:broader :a ; skos:related <${schemeIri("direction")}higher>`) });
    expect(ok).not.toThrow();
    expect(load({ direction: dir, metric: concept("metric", "b", " ; skos:broader :missing") })).toThrow(/metric\/missing>, which is not a concept/);
    expect(load({ direction: dir, metric: concept("metric", "b", ` ; skos:related <${schemeIri("direction")}lower>`) })).toThrow(/direction\/lower>, which is not a concept/);
    expect(load({ direction: dir, metric: concept("metric", "a") + `:x skos:inScheme <${schemeIri("direction")}> .\n` }))
      .toThrow(/metric\/x> is in scheme <.*direction\/>/);
    expect(load({ direction: dir, metric: concept("metric", "a", " ; skos:broader :b") + concept("metric", "b", " ; skos:narrower :a") })).not.toThrow();
    expect(load({ direction: dir, metric: concept("metric", "a", " ; skos:broader :b") + concept("metric", "b", " ; skos:broader :c") + concept("metric", "c") + `:a skos:narrower :c .\n` }))
      .toThrow(/skos:broader cycle/);
  });

  it("controls a discrepancy review's follow-up action", () => {
    const record = { id: "x", facets: {}, attributes: { field: "discrepancy_review", value: "investigating", action: "looked" } };
    expect(() => validateVocabularies(mapping, [record], schemes)).toThrow(/is not a concept in the discrepancy-action vocabulary/);
    const fixed = { ...record, attributes: { ...record.attributes, action: "investigated" } };
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
