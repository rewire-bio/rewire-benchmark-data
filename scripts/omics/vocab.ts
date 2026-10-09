/** Controlled vocabularies: SKOS concept schemes in data/vocab/<scheme>.ttl.
 *
 * A record stores a concept's key, the last segment of its IRI (for example "auprc" for
 * https://benchmarks.rewire.it/vocab/metric/auprc). data/ontology/mapping.json names the
 * scheme of each controlled field; the JSON-LD context and the RDF export expand keys to
 * concept IRIs, and validateVocabularies rejects any value that is not a key in its scheme. */
import fs from "node:fs";
import path from "node:path";
import { Parser } from "n3";

export const vocabBase = "https://benchmarks.rewire.it/vocab/";
export const vocabDir = "data/vocab";
const SKOS = "http://www.w3.org/2004/02/skos/core#";
const RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type";

export type Concept = { key: string; iri: string; label: string };
export type Scheme = { name: string; iri: string; concepts: Map<string, Concept> };

export const schemeIri = (name: string) => `${vocabBase}${name}/`;

/** Parse every scheme file. A concept belongs to the scheme whose IRI prefixes its own. */
export function loadSchemes(root = "."): Map<string, Scheme> {
  const dir = path.join(root, vocabDir);
  const schemes = new Map<string, Scheme>();
  if (!fs.existsSync(dir)) return schemes;
  for (const file of fs.readdirSync(dir).filter((name) => name.endsWith(".ttl")).sort()) {
    const name = file.replace(/\.ttl$/, "");
    const iri = schemeIri(name);
    const quads = new Parser({ format: "Turtle" }).parse(fs.readFileSync(path.join(dir, file), "utf8"));
    if (!quads.some((q) => q.subject.value === iri && q.predicate.value === RDF_TYPE && q.object.value === `${SKOS}ConceptScheme`))
      throw new Error(`${file} does not declare the concept scheme <${iri}>`);
    const concepts = new Map<string, Concept>();
    for (const q of quads) {
      if (q.predicate.value !== `${SKOS}inScheme` || q.object.value !== iri) continue;
      const key = q.subject.value.slice(iri.length);
      // Keys are lowercase words joined by hyphens, or by underscores where a closed list
      // already used them in code (for example source_checked, author_reported).
      if (!q.subject.value.startsWith(iri) || !/^[a-z0-9]+(?:[-_][a-z0-9]+)*$/.test(key))
        throw new Error(`${file}: concept <${q.subject.value}> is not <${iri}key> with a lowercase key`);
      const label = quads.find((l) => l.subject.value === q.subject.value && l.predicate.value === `${SKOS}prefLabel`);
      if (!label) throw new Error(`${file}: concept ${key} has no skos:prefLabel`);
      concepts.set(key, { key, iri: q.subject.value, label: label.object.value });
    }
    schemes.set(name, { name, iri, concepts });
  }
  return schemes;
}

type Term = { property: string; scheme?: string };
type MappingSections = {
  fields: Record<string, Term>;
  facets: Record<string, Term>;
  attributes: Record<string, Term>;
  review: Record<string, Term>;
};
type RecordLike = {
  id: string;
  facets: Record<string, string[]>;
  attributes: Record<string, unknown>;
  [field: string]: unknown;
};

/** Every controlled value on a record, with where it came from. */
export function controlledValues(mapping: MappingSections, record: RecordLike): { field: string; scheme: string; value: unknown }[] {
  const found: { field: string; scheme: string; value: unknown }[] = [];
  const add = (field: string, scheme: string, value: unknown) => {
    if (value === null || value === undefined) return;
    for (const item of Array.isArray(value) ? value : [value]) found.push({ field, scheme, value: item });
  };
  for (const [name, t] of Object.entries(mapping.fields)) if (t.scheme) add(name, t.scheme, record[name]);
  for (const [name, t] of Object.entries(mapping.facets)) if (t.scheme) add(`facets.${name}`, t.scheme, record.facets[name]);
  for (const [name, t] of Object.entries(mapping.attributes)) if (t.scheme) add(`attributes.${name}`, t.scheme, record.attributes[name]);
  const review = record.attributes.review;
  if (review && typeof review === "object" && !Array.isArray(review))
    for (const [name, t] of Object.entries(mapping.review))
      if (t.scheme) add(`attributes.review.${name}`, t.scheme, (review as Record<string, unknown>)[name]);
  return found;
}

/** Reject values that are not keys of their field's scheme. */
export function validateVocabularies(mapping: MappingSections, records: RecordLike[], schemes = loadSchemes()): void {
  const problems: string[] = [];
  for (const record of records)
    for (const { field, scheme, value } of controlledValues(mapping, record)) {
      const concepts = schemes.get(scheme)?.concepts;
      if (!concepts) problems.push(`${field} uses scheme "${scheme}", which has no data/vocab/${scheme}.ttl`);
      else if (typeof value !== "string" || !concepts.has(value))
        problems.push(`${record.id}: ${field} ${JSON.stringify(value)} is not a concept in the ${scheme} vocabulary`);
      if (problems.length >= 20) break;
    }
  if (problems.length) throw new Error(`Uncontrolled values:\n  ${[...new Set(problems)].join("\n  ")}`);
}
