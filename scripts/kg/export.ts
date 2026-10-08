/** RDF projection of the catalogue, driven by data/ontology/mapping.json.
 *   context: write data/ontology/context.jsonld, which makes each canonical
 *            record line readable as JSON-LD 1.1
 *   export:  write the public records as sorted N-Quads, with a manifest,
 *            to public/kg/ (the asserted graph of a knowledge-graph bundle)
 * Usage: npm run kg -- context | export */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { loadRecords } from "../omics/records";
import { publicRecords, type RecordEntry } from "../omics/schema";

type Term = { property: string; iri?: boolean; datatype?: string };
export type Mapping = {
  base: string;
  vocab: string;
  graph: string;
  prefixes: Record<string, string>;
  classes: Record<string, { types: string[] }>;
  relations: Record<string, { property: string }>;
  fields: Record<string, Term>;
  facets: Record<string, Term>;
  attributes: Record<string, Term>;
  review: Record<string, Term>;
};

export const mappingFile = "data/ontology/mapping.json";
export const contextFile = "data/ontology/context.jsonld";
export const readMapping = (): Mapping => JSON.parse(fs.readFileSync(mappingFile, "utf8"));

export function expand(mapping: Mapping, curie: string): string {
  const [prefix, local] = curie.split(":", 2);
  const ns = mapping.prefixes[prefix];
  if (!ns || local === undefined) throw new Error(`Unknown prefix in ${curie}`);
  return ns + local;
}

/** JSON-LD 1.1 context for the canonical JSONL records. */
export function buildContext(mapping: Mapping) {
  const term = (t: Term) => ({ "@id": t.property, ...(t.iri ? { "@type": "@id" } : t.datatype ? { "@type": t.datatype } : {}) });
  return {
    "@context": {
      "@version": 1.1,
      "@base": mapping.base,
      "@vocab": mapping.vocab,
      ...mapping.prefixes,
      id: "@id",
      kind: {
        "@id": "rdf:type",
        "@type": "@vocab",
        "@context": Object.fromEntries(Object.entries(mapping.classes).map(([kind, c]) => [kind, c.types[0]])),
      },
      ...Object.fromEntries(Object.entries(mapping.fields).map(([k, t]) => [k, term(t)])),
      facets: "@nest",
      ...Object.fromEntries(Object.entries(mapping.facets).map(([k, t]) => [k, { ...term(t), "@nest": "facets" }])),
      attributes: "@nest",
      ...Object.fromEntries(Object.entries(mapping.attributes).map(([k, t]) => [k, { ...term(t), "@nest": "attributes" }])),
      links: { "@id": "rb:link" },
      relation: {
        "@id": "rb:relation",
        "@type": "@vocab",
        "@context": Object.fromEntries(Object.entries(mapping.relations).map(([r, t]) => [r, t.property])),
      },
      target_id: { "@id": "rb:target", "@type": "@id" },
    },
  };
}

const escapeLiteral = (value: string) =>
  value.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\n/g, "\\n").replace(/\r/g, "\\r");
const iri = (value: string) => `<${encodeURI(decodeURISafe(value)).replace(/[<>"{}|^`\\]/g, (c) => "%" + c.charCodeAt(0).toString(16).toUpperCase())}>`;
function decodeURISafe(value: string) {
  try { return decodeURI(value); } catch { return value; }
}

/** One N-Quads line per statement; records are projected, never altered. */
export function recordQuads(mapping: Mapping, record: RecordEntry): string[] {
  const graph = iri(mapping.graph);
  const subject = iri(mapping.base + record.id);
  const lines: string[] = [];
  const add = (predicate: string, object: string) => lines.push(`${subject} ${iri(expand(mapping, predicate))} ${object} ${graph} .`);
  const literal = (value: unknown, t: Term): string | undefined => {
    if (value === null || value === undefined || typeof value === "object") return undefined;
    const text = String(value);
    if (t.iri) return /^https?:\/\//.test(text) ? iri(text) : undefined;
    if (t.datatype === "xsd:decimal" && !/^-?\d+(\.\d+)?([eE][-+]?\d+)?$/.test(text)) return `"${escapeLiteral(text)}"`;
    return t.datatype ? `"${escapeLiteral(text)}"^^${iri(expand(mapping, t.datatype))}` : `"${escapeLiteral(text)}"`;
  };
  const kind = mapping.classes[record.kind];
  if (!kind) throw new Error(`No class mapping for kind ${record.kind}`);
  for (const type of kind.types) add("rdf:type", iri(expand(mapping, type)));
  for (const field of ["name", "description", "status"] as const) {
    const object = literal(record[field], mapping.fields[field]);
    if (object && record[field] !== "") add(mapping.fields[field].property, object);
  }
  for (const id of record.source_ids) add(mapping.fields.source_ids.property, iri(mapping.base + id));
  for (const [facet, values] of Object.entries(record.facets)) {
    const t = mapping.facets[facet];
    if (t) for (const value of values) add(t.property, `"${escapeLiteral(value)}"`);
  }
  for (const link of record.links) {
    const relation = mapping.relations[link.relation];
    if (!relation) throw new Error(`No property mapping for relation ${link.relation}`);
    add(relation.property, iri(mapping.base + link.target_id));
  }
  for (const [name, t] of Object.entries(mapping.attributes)) {
    const object = literal(record.attributes[name], t);
    if (object) add(t.property, object);
  }
  const review = record.attributes.review;
  if (review && typeof review === "object" && !Array.isArray(review)) {
    for (const [name, t] of Object.entries(mapping.review)) {
      const object = literal((review as Record<string, unknown>)[name], t);
      if (object) add(t.property, object);
    }
  }
  return lines;
}

export function exportQuads(mapping: Mapping, records: RecordEntry[]): string {
  const lines = [...new Set(publicRecords(records).flatMap((record) => recordQuads(mapping, record)))].sort();
  return lines.join("\n") + "\n";
}

if (process.argv[1]?.endsWith("export.ts")) {
  const command = process.argv[2];
  const mapping = readMapping();
  if (command === "context") {
    fs.writeFileSync(contextFile, JSON.stringify(buildContext(mapping), null, 2) + "\n");
    console.log(`Wrote ${contextFile}`);
  } else if (command === "export") {
    const nquads = exportQuads(mapping, loadRecords());
    const release = JSON.parse(fs.readFileSync("public/omics/manifest.json", "utf8"));
    const sha = (value: string | Buffer) => crypto.createHash("sha256").update(value).digest("hex");
    fs.mkdirSync("public/kg", { recursive: true });
    fs.writeFileSync(path.join("public/kg", "asserted.nq"), nquads);
    const manifest = {
      format_version: "1.0",
      dataset: "rewire-benchmark-data",
      release_id: release.release_id,
      files: { "asserted.nq": { sha256: sha(nquads), quads: nquads.split("\n").filter(Boolean).length } },
      mapping_sha256: sha(fs.readFileSync(mappingFile)),
      inferred: null,
      note: "Asserted statements only. Inference and SHACL validation are a later build step.",
    };
    fs.writeFileSync(path.join("public/kg", "manifest.json"), JSON.stringify(manifest, null, 2) + "\n");
    console.log(`Wrote ${manifest.files["asserted.nq"].quads} quads for ${release.release_id} to public/kg/`);
  } else {
    console.error("Usage: npm run kg -- context | export");
    process.exit(1);
  }
}
