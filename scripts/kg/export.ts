/** RDF projection of the catalogue, driven by data/ontology/mapping.json.
 *   context: write data/ontology/context.jsonld, which makes each canonical
 *            record line readable as JSON-LD 1.1
 *   export:  write the public records as sorted N-Quads, with a manifest,
 *            to public/kg/ (the asserted graph of a knowledge-graph bundle)
 *   terms:   write data/ontology/rb-attributes.ttl and attribute-shapes.ttl, the property
 *            declarations and per-kind shapes for declared attributes (attribute-terms.ts)
 * Usage: npm run kg -- context | export | terms */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { loadRecords } from "../omics/records";
import { publicRecords, type RecordEntry } from "../omics/schema";
import { schemeIri } from "../omics/vocab";
import { attributeProperty, declarationsTurtle, encoding, missing, nodes, notExported, registry, shapesTurtle } from "./attribute-terms";

/** scheme: the value is a concept key in data/vocab/<scheme>.ttl, exported as the concept IRI. */
type Term = { property: string; iri?: boolean; datatype?: string; scheme?: string };
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
export const attributeDeclarationsFile = "data/ontology/rb-attributes.ttl";
export const attributeShapesFile = "data/ontology/attribute-shapes.ttl";
export const readMapping = (): Mapping => JSON.parse(fs.readFileSync(mappingFile, "utf8"));

export function expand(mapping: Mapping, curie: string): string {
  const [prefix, local] = curie.split(":", 2);
  const ns = mapping.prefixes[prefix];
  if (!ns || local === undefined) throw new Error(`Unknown prefix in ${curie}`);
  return ns + local;
}

/** Context terms for every declared attribute. A key whose type differs between kinds gets
 * no type here; the N-Quads export, which knows each record's kind, is authoritative. */
function attributeContext(mapping: Mapping): Record<string, unknown> {
  const types = new Map<string, Set<string>>();
  for (const keys of Object.values(registry))
    for (const [key, type] of Object.entries(keys)) types.set(key, (types.get(key) ?? new Set()).add(type));
  const scalar = (datatype?: string) => (datatype ? { "@type": datatype } : {});
  const fieldContext = (fields: Record<string, { property: string; datatype?: string; scheme?: string }>) =>
    Object.fromEntries(Object.entries(fields).map(([name, f]) => [name, {
      "@id": f.property,
      ...(f.scheme ? { "@type": "@vocab", "@context": { "@vocab": schemeIri(f.scheme) } } : scalar(f.datatype)),
    }]));
  const out: Record<string, unknown> = {};
  for (const [key, set] of [...types].sort(([a], [b]) => (a < b ? -1 : 1))) {
    if (notExported.has(key)) continue;
    const id = attributeProperty(mapping, key);
    const e = set.size === 1 ? encoding([...set][0]) : undefined;
    out[key] = { "@id": id, "@nest": "attributes", ...(
      !e ? {} :
      e.kind === "missing" ? { "@id": missing.property, "@container": "@index", "@index": missing.field,
        "@context": { reason: { "@id": missing.reason, "@type": "@vocab", "@context": { "@vocab": schemeIri("missingness") } }, note: missing.note } } :
      e.kind === "node" ? { "@context": fieldContext(nodes[e.node].fields) } :
      e.kind === "concept" ? { "@type": "@vocab", "@context": { "@vocab": schemeIri(e.scheme) } } :
      e.kind === "iri" || e.kind === "record" ? { "@type": "@id" } :
      e.datatype === "rdf:JSON" ? { "@type": "@json" } : scalar(e.datatype)) };
  }
  return out;
}

/** JSON-LD 1.1 context for the canonical JSONL records. */
export function buildContext(mapping: Mapping) {
  const term = (t: Term) =>
    t.scheme
      ? { "@id": t.property, "@type": "@vocab", "@context": { "@vocab": schemeIri(t.scheme) } }
      : { "@id": t.property, ...(t.iri ? { "@type": "@id" } : t.datatype ? { "@type": t.datatype } : {}) };
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
      ...attributeContext(mapping),
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

/** The xsd:decimal lexical form of a number written with or without an exponent, without
 * floating-point rounding ("1.39e-16" becomes "0.000000000000000139"). */
export function canonicalDecimal(text: string): string | undefined {
  const match = /^([-+]?)(\d+)(?:\.(\d+))?(?:[eE]([-+]?\d+))?$/.exec(text.trim());
  if (!match) return undefined;
  const [, sign, whole, fraction = "", exponent = "0"] = match;
  let digits = whole + fraction;
  let point = whole.length + Number(exponent);
  if (point <= 0) { digits = "0".repeat(1 - point) + digits; point = 1; }
  if (point > digits.length) digits = digits + "0".repeat(point - digits.length);
  const integer = digits.slice(0, point).replace(/^0+(?=\d)/, "");
  const decimals = digits.slice(point);
  return `${sign === "-" ? "-" : ""}${integer}${decimals ? "." + decimals : ""}`;
}

/** JSON with object keys sorted, so the same value always gives the same rdf:JSON literal. */
export function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value && typeof value === "object")
    return `{${Object.keys(value).sort().map((k) => `${JSON.stringify(k)}:${canonicalJson((value as Record<string, unknown>)[k])}`).join(",")}}`;
  return JSON.stringify(value);
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
    if (t.scheme) return iri(schemeIri(t.scheme) + text);
    if (t.iri) return /^https?:\/\//.test(text) ? iri(text) : undefined;
    if (t.datatype === "xsd:decimal") {
      const decimal = canonicalDecimal(text);
      return decimal === undefined ? `"${escapeLiteral(text)}"` : `"${decimal}"^^${iri(expand(mapping, "xsd:decimal"))}`;
    }
    // A date without a time is a valid xsd:date, not an xsd:dateTime.
    const datatype = t.datatype === "xsd:dateTime" && /^\d{4}-\d{2}-\d{2}$/.test(text) ? "xsd:date" : t.datatype;
    return datatype ? `"${escapeLiteral(text)}"^^${iri(expand(mapping, datatype))}` : `"${escapeLiteral(text)}"`;
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
    if (t)
      for (const value of values) {
        const object = literal(value, t);
        if (object) add(t.property, object);
      }
  }
  for (const link of record.links) {
    const relation = mapping.relations[link.relation];
    if (!relation) throw new Error(`No property mapping for relation ${link.relation}`);
    add(relation.property, iri(mapping.base + link.target_id));
  }
  // A list value (review methods and reviewers, for example) gives one statement per item.
  const addValue = (value: unknown, t: Term) => {
    for (const item of Array.isArray(value) ? value : [value]) {
      const object = literal(item, t);
      if (object) add(t.property, object);
    }
  };
  const declared = registry[record.kind] ?? {};
  const node = (path: string) => iri(`${mapping.base}${record.id}/${path}`);
  const addTo = (subject: string, predicate: string, object: string) =>
    lines.push(`${subject} ${iri(expand(mapping, predicate))} ${object} ${graph} .`);
  const nodeLiteral = (value: unknown, datatype?: string, scheme?: string) =>
    literal(typeof value === "number" ? String(value) : value, { property: "", datatype, scheme });
  for (const [key, value] of Object.entries(record.attributes)) {
    const type = declared[key];
    if (!type || notExported.has(key) || value === undefined) continue;
    const e = encoding(type);
    const property = attributeProperty(mapping, key);
    if (e.kind === "missing") {
      for (const [field, entry] of Object.entries(value as Record<string, { reason: string; note?: string }>)) {
        const subject = node(`missing/${field}`);
        add(missing.property, subject);
        addTo(subject, "rdf:type", iri(expand(mapping, missing.class)));
        addTo(subject, missing.field, `"${escapeLiteral(field)}"`);
        addTo(subject, missing.reason, iri(schemeIri("missingness") + entry.reason));
        if (entry.note) addTo(subject, missing.note, `"${escapeLiteral(entry.note)}"`);
      }
    } else if (e.kind === "node") {
      const spec = nodes[e.node];
      const subject = node(key);
      add(property, subject);
      addTo(subject, "rdf:type", iri(expand(mapping, spec.class)));
      const fields = { ...(value as Record<string, unknown>) };
      const split = fields.train_validation_test;
      if (Array.isArray(split)) [fields.train, fields.validation, fields.test] = split;
      for (const [field, f] of Object.entries(spec.fields)) {
        const object = fields[field] === undefined ? undefined : nodeLiteral(fields[field], f.datatype, f.scheme);
        if (object) addTo(subject, f.property, object);
      }
    } else if (e.kind === "literal" && e.datatype === "rdf:JSON") {
      add(property, `"${escapeLiteral(canonicalJson(value))}"^^${iri(expand(mapping, "rdf:JSON"))}`);
    } else {
      const term: Term = e.kind === "concept" ? { property, scheme: e.scheme } : e.kind === "iri" ? { property, iri: true }
        : e.kind === "record" ? { property } : { property, datatype: e.datatype };
      for (const item of Array.isArray(value) ? value : [value]) {
        const object = e.kind === "record" ? iri(mapping.base + String(item)) : literal(typeof item === "number" ? String(item) : item, term);
        if (object) add(property, object);
      }
    }
  }
  const review = record.attributes.review;
  if (review && typeof review === "object" && !Array.isArray(review))
    for (const [name, t] of Object.entries(mapping.review)) addValue((review as Record<string, unknown>)[name], t);
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
    // Before a release is cut (at intake, or on a pull request) the graph is labelled unreleased.
    const releaseManifest = "public/omics/manifest.json";
    const release = fs.existsSync(releaseManifest) ? JSON.parse(fs.readFileSync(releaseManifest, "utf8")) : { release_id: "unreleased" };
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
  } else if (command === "terms") {
    const rb = fs.readFileSync("data/ontology/rb.ttl", "utf8");
    const declared = new Set([...rb.matchAll(/^(rb:[A-Za-z0-9]+) a /gm)].map((m) => m[1]));
    fs.writeFileSync(attributeDeclarationsFile, declarationsTurtle(mapping, declared));
    fs.writeFileSync(attributeShapesFile, shapesTurtle(mapping));
    console.log(`Wrote ${attributeDeclarationsFile} and ${attributeShapesFile}`);
  } else {
    console.error("Usage: npm run kg -- context | export | terms");
    process.exit(1);
  }
}
