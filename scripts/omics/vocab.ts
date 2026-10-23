/** Controlled vocabularies: SKOS concept schemes in data/vocab/<scheme>.ttl.
 *
 * A record stores a concept's key, the last segment of its IRI (for example "auprc" for
 * https://benchmarks.rewire.it/vocab/metric/auprc). data/ontology/mapping.json names the
 * scheme of each controlled field; the JSON-LD context and the RDF export expand keys to
 * concept IRIs, and validateVocabularies rejects any value that is not a key in its scheme. */
import fs from "node:fs";
import path from "node:path";
import { Parser, type Quad } from "n3";

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
  const parsed: { file: string; quads: Quad[] }[] = [];
  for (const file of fs.readdirSync(dir).filter((name) => name.endsWith(".ttl")).sort()) {
    const name = file.replace(/\.ttl$/, "");
    const iri = schemeIri(name);
    const quads = new Parser({ format: "Turtle" }).parse(fs.readFileSync(path.join(dir, file), "utf8"));
    parsed.push({ file, quads });
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
  checkReferences(parsed, schemes);
  return schemes;
}

/** The scheme name and key of a concept IRI, or undefined for anything outside vocab/<scheme>/<key>. */
function conceptParts(iri: string): { scheme: string; key: string } | undefined {
  const m = iri.startsWith(vocabBase) ? /^([a-z0-9-]+)\/(.+)$/.exec(iri.slice(vocabBase.length)) : null;
  return m ? { scheme: m[1], key: m[2] } : undefined;
}

/** Links between concepts are checked here because no test or shape dereferences them: every
 * object IRI in a vocab/<scheme>/ namespace (skos:broader, narrower, related, rb:defaultDirection)
 * must be a concept that exists, every skos:inScheme must name the scheme its subject's IRI sits in,
 * and skos:broader (with narrower read as its inverse) must not loop. External mappings such as
 * skos:closeMatch to STATO are not dereferenced. */
function checkReferences(parsed: { file: string; quads: Quad[] }[], schemes: Map<string, Scheme>): void {
  const problems: string[] = [];
  const parents = new Map<string, Set<string>>();
  const addParent = (child: string, parent: string) => parents.set(child, (parents.get(child) || new Set()).add(parent));
  for (const { file, quads } of parsed)
    for (const q of quads) {
      const subject = conceptParts(q.subject.value);
      if (q.predicate.value === `${SKOS}inScheme`) {
        if (subject && schemeIri(subject.scheme) !== q.object.value)
          problems.push(`${file}: <${q.subject.value}> is in scheme <${q.object.value}> but its IRI is in <${schemeIri(subject.scheme)}>`);
        continue;
      }
      if (q.object.termType !== "NamedNode") continue;
      const target = conceptParts(q.object.value);
      if (!target) continue;
      if (!schemes.get(target.scheme)?.concepts.has(target.key))
        problems.push(`${file}: <${q.subject.value}> ${q.predicate.value.replace(SKOS, "skos:")} <${q.object.value}>, which is not a concept`);
      else if (q.predicate.value === `${SKOS}broader`) addParent(q.subject.value, q.object.value);
      else if (q.predicate.value === `${SKOS}narrower`) addParent(q.object.value, q.subject.value);
    }
  // Depth-first search; a node met again while still on the stack closes a cycle.
  const state = new Map<string, "open" | "done">();
  const visit = (node: string, trail: string[]) => {
    if (state.get(node) === "done") return;
    if (state.get(node) === "open") {
      const loop = trail.slice(trail.indexOf(node)).concat(node).map((iri) => iri.slice(vocabBase.length));
      problems.push(`skos:broader cycle: ${loop.join(", then ")}`);
      return;
    }
    state.set(node, "open");
    for (const parent of parents.get(node) || []) visit(parent, [...trail, node]);
    state.set(node, "done");
  };
  for (const node of parents.keys()) visit(node, []);
  if (problems.length) throw new Error(`Vocabulary references do not resolve:\n  ${problems.slice(0, 20).join("\n  ")}`);
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
  const derivation = record.attributes.derivation;
  if (derivation && typeof derivation === "object" && !Array.isArray(derivation))
    add("attributes.derivation.method", "derivation-method", (derivation as Record<string, unknown>).method);
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
