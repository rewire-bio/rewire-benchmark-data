/** RDF terms for declared record attributes (issue #42, stage 3b).
 *
 * Every attribute declared in shared/omics/attribute-registry.ts is exported. Its property is
 * the one in data/ontology/mapping.json "attributes" when listed there, otherwise
 * rb:<camelCaseKey>; its datatype follows the registry type for the record's kind. Structured
 * values (uncertainty, coverage, reported population, missing reasons) become nodes with their
 * own IRIs under the record's IRI. The same tables generate the property declarations
 * (data/ontology/rb-attributes.ttl) and the per-kind shapes (data/ontology/attribute-shapes.ttl):
 *   npm run kg -- terms */
import { attributeRegistry } from "../../shared/omics/attribute-registry";
import type { Mapping } from "./export";

export const registry = attributeRegistry as Record<string, Record<string, string>>;
export const camel = (key: string) => key.replace(/_([a-z0-9])/g, (_, c: string) => c.toUpperCase());

/** Attributes the record's own fields or the review mapping already export. */
export const notExported = new Set(["review"]);

export function attributeProperty(mapping: Mapping, key: string): string {
  return mapping.attributes[key]?.property ?? `rb:${camel(key)}`;
}

/** How a registry type is written in RDF. */
export type Encoding =
  | { kind: "literal"; datatype?: string; list?: boolean }
  | { kind: "iri"; list?: boolean }
  | { kind: "record"; list?: boolean }
  | { kind: "concept"; scheme: string; list?: boolean }
  | { kind: "node"; node: keyof typeof nodes }
  | { kind: "missing" };

export function encoding(type: string): Encoding {
  if (type.startsWith("concept:")) return { kind: "concept", scheme: type.slice(8) };
  if (type.startsWith("concepts:")) return { kind: "concept", scheme: type.slice(9), list: true };
  switch (type) {
    case "integer": return { kind: "literal", datatype: "xsd:integer" };
    case "number": return { kind: "literal", datatype: "xsd:double" };
    case "boolean": return { kind: "literal", datatype: "xsd:boolean" };
    case "decimal":
    case "decimal-or-null": return { kind: "literal", datatype: "xsd:decimal" };
    case "date": return { kind: "literal", datatype: "xsd:date" };
    case "datetime": return { kind: "literal", datatype: "xsd:dateTime" };
    case "url": return { kind: "iri" };
    case "record-id": return { kind: "record" };
    case "record-ids": return { kind: "record", list: true };
    case "texts":
    case "entity-kinds": return { kind: "literal", list: true };
    case "json": return { kind: "literal", datatype: "rdf:JSON" };
    case "uncertainty": return { kind: "node", node: "uncertainty" };
    case "coverage": return { kind: "node", node: "coverage" };
    case "reported-population": return { kind: "node", node: "reported-population" };
    case "missing-metadata": return { kind: "missing" };
    default: return { kind: "literal" }; // text, doi, sha256, git-sha, url-or-path
  }
}

type NodeField = { property: string; datatype?: string; scheme?: string; range?: string };
/** Structured attribute values: class, and property and datatype of each field. */
export const nodes = {
  uncertainty: {
    class: "rb:Uncertainty",
    comment: "A result's reported uncertainty: one of the uncertainty types, with its spread or interval.",
    fields: {
      type: { property: "rb:uncertaintyType", scheme: "uncertainty-type" },
      printed: { property: "rb:printedUncertainty" },
      value: { property: "rb:spread", datatype: "xsd:decimal" },
      half_width: { property: "rb:halfWidth", datatype: "xsd:decimal" },
      lower: { property: "rb:lowerBound", datatype: "xsd:decimal" },
      upper: { property: "rb:upperBound", datatype: "xsd:decimal" },
      center: { property: "rb:spreadCenter", datatype: "xsd:decimal" },
      level: { property: "rb:confidenceLevel", datatype: "xsd:decimal", range: "sh:minExclusive 0 ; sh:maxExclusive 1" },
      method: { property: "rb:estimationMethod" },
      n: { property: "rb:sampleSize", datatype: "xsd:integer" },
      resamples: { property: "rb:resampleCount", datatype: "xsd:integer" },
      scope: { property: "rb:uncertaintyScope" },
      unit: { property: "rb:uncertaintyUnit" },
      source_column: { property: "rb:sourceColumn" },
      note: { property: "rb:note" },
    } as Record<string, NodeField>,
  },
  coverage: {
    class: "rb:Coverage",
    comment: "How many items were scored out of how many were eligible.",
    fields: {
      scored: { property: "rb:scoredCount", datatype: "xsd:integer" },
      eligible: { property: "rb:eligibleCount", datatype: "xsd:integer" },
      unit: { property: "rb:countUnit" },
      generated_per_run: { property: "rb:generatedPerRun", datatype: "xsd:integer" },
      repeats: { property: "rb:repeatCount", datatype: "xsd:integer" },
      note: { property: "rb:note" },
    } as Record<string, NodeField>,
  },
  "reported-population": {
    class: "rb:ReportedPopulation",
    comment: "The population size a source reports, as a count or as train, validation and test counts.",
    fields: {
      count: { property: "rb:populationCount", datatype: "xsd:integer" },
      unit: { property: "rb:populationUnit" },
      train: { property: "rb:trainCount", datatype: "xsd:integer" },
      validation: { property: "rb:validationCount", datatype: "xsd:integer" },
      test: { property: "rb:testCount", datatype: "xsd:integer" },
      note: { property: "rb:note" },
    } as Record<string, NodeField>,
  },
} as const;

export const missing = {
  property: "rb:missingValue",
  class: "rb:MissingValue",
  comment: "A declared field the record has no value for, and why.",
  field: "rb:missingField",
  reason: "rb:missingReason",
  note: "rb:note",
};

/** Property to the kinds and registry types it carries, for declarations and shapes. */
export function attributeUses(mapping: Mapping): Map<string, { kind: string; key: string; type: string }[]> {
  const uses = new Map<string, { kind: string; key: string; type: string }[]>();
  for (const [kind, keys] of Object.entries(registry))
    for (const [key, type] of Object.entries(keys)) {
      if (notExported.has(key)) continue;
      const property = type === "missing-metadata" ? missing.property : attributeProperty(mapping, key);
      uses.set(property, [...(uses.get(property) ?? []), { kind, key, type }]);
    }
  return uses;
}

const xsdOf = (e: Encoding): string | undefined => (e.kind === "literal" ? (e.datatype ?? "xsd:string") : undefined);

/** Turtle declaring every rb: property and class the attribute export uses that rb.ttl does not. */
export function declarationsTurtle(mapping: Mapping, declaredInRb: Set<string>): string {
  const lines = [
    "# Generated by npm run kg -- terms from shared/omics/attribute-registry.ts. Do not edit.",
    "# Properties for declared record attributes. schema:domainIncludes and schema:rangeIncludes",
    "# document use without adding inference; the per-kind shapes in attribute-shapes.ttl enforce it.",
    "",
    ...Object.entries(mapping.prefixes).filter(([p]) => ["rb", "rdf", "rdfs", "xsd", "schema", "mls", "dcat", "obo"].includes(p))
      .map(([p, ns]) => `@prefix ${p}: <${ns}> .`),
    "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
    "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
    "",
  ];
  const classOf = (kind: string) => mapping.classes[kind].types[0];
  const declared = new Set(declaredInRb);
  const declare = (property: string, objectProperty: boolean, label: string, comment: string, domains: string[], ranges: string[]) => {
    if (!property.startsWith("rb:") || declared.has(property)) return;
    declared.add(property);
    lines.push(
      `${property} a owl:${objectProperty ? "ObjectProperty" : "DatatypeProperty"} ;`,
      `    rdfs:label "${label}"@en ;`,
      `    rdfs:comment "${comment.replace(/"/g, '\\"')}"@en${domains.length || ranges.length ? " ;" : " ."}`,
      ...[...domains.map((d) => `schema:domainIncludes ${d}`), ...ranges.map((r) => `schema:rangeIncludes ${r}`)]
        .map((line, i, all) => `    ${line}${i === all.length - 1 ? " ." : " ;"}`),
      "",
    );
  };
  for (const [property, uses] of [...attributeUses(mapping)].sort(([a], [b]) => (a < b ? -1 : 1))) {
    const encodings = uses.map((use) => encoding(use.type));
    const objectProperty = encodings.every((e) => e.kind !== "literal");
    const keys = [...new Set(uses.map((use) => use.key))];
    const kinds = [...new Set(uses.map((use) => use.kind))].sort();
    const ranges = [...new Set(encodings.flatMap((e) =>
      e.kind === "node" ? [nodes[e.node].class] : e.kind === "missing" ? [missing.class] : e.kind === "concept" ? ["skos:Concept"] : (xsdOf(e) ? [xsdOf(e)!] : [])))].sort();
    const comment = property === missing.property ? missing.comment : `The ${keys.join(" or ")} attribute of ${kinds.map((k) => k.replace(/_/g, " ")).join(", ")} records.`;
    declare(property, objectProperty, keys[0].replace(/_/g, " "), comment, kinds.map(classOf), ranges);
  }
  for (const node of Object.values(nodes)) {
    if (!declared.has(node.class)) lines.push(`${node.class} a owl:Class ;`, `    rdfs:comment "${node.comment}"@en .`, "");
    declared.add(node.class);
    for (const [field, f] of Object.entries(node.fields))
      declare(f.property, !!f.scheme, field.replace(/_/g, " "), `Field ${field} of ${node.class.slice(3)} nodes.`, [node.class], [f.scheme ? "skos:Concept" : (f.datatype ?? "xsd:string")]);
  }
  lines.push(`${missing.class} a owl:Class ;`, `    rdfs:comment "${missing.comment}"@en .`, "");
  declare(missing.field, false, "missing field", "The declared attribute that has no value.", [missing.class], ["xsd:string"]);
  declare(missing.reason, true, "missing reason", "Why the field has no value, from the missingness scheme.", [missing.class], ["skos:Concept"]);
  return lines.join("\n") + "\n";
}

const schemeShape = (scheme: string) => `[ sh:class skos:Concept ; sh:property [ sh:path skos:inScheme ; sh:hasValue <https://benchmarks.rewire.it/vocab/${scheme}/> ; sh:minCount 1 ] ]`;

function valueConstraint(e: Encoding): string {
  switch (e.kind) {
    case "literal":
      if (e.datatype === "xsd:dateTime") return "sh:or ( [ sh:datatype xsd:dateTime ] [ sh:datatype xsd:date ] )";
      return `sh:datatype ${e.datatype ?? "xsd:string"}`;
    case "iri":
    case "record": return "sh:nodeKind sh:IRI";
    case "concept": return `sh:node ${schemeShape(e.scheme)}`;
    case "node": return `sh:node rbs:${nodes[e.node].class.slice(3)}`;
    case "missing": return "sh:node rbs:MissingValue";
  }
}

/** Per-kind SHACL shapes for declared attributes, with shapes for the structured nodes. */
export function shapesTurtle(mapping: Mapping): string {
  const lines = [
    "# Generated by npm run kg -- terms from shared/omics/attribute-registry.ts. Do not edit.",
    "# Each declared attribute has the datatype, node kind or concept scheme its registry type gives;",
    "# single-valued attributes appear at most once.",
    "",
    "@prefix sh: <http://www.w3.org/ns/shacl#> .",
    "@prefix rbs: <https://benchmarks.rewire.it/shapes#> .",
    ...Object.entries(mapping.prefixes).filter(([p]) => ["rb", "rdf", "xsd", "schema", "mls", "dcat", "obo"].includes(p))
      .map(([p, ns]) => `@prefix ${p}: <${ns}> .`),
    "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
    "",
  ];
  for (const [kind, keys] of Object.entries(registry)) {
    const props = Object.entries(keys)
      .filter(([key]) => !notExported.has(key))
      .map(([key, type]) => {
        const e = encoding(type);
        const property = type === "missing-metadata" ? missing.property : attributeProperty(mapping, key);
        const single = e.kind !== "missing" && !("list" in e && e.list) ? " sh:maxCount 1 ;" : "";
        return `[ sh:path ${property} ;${single} ${valueConstraint(e)} ]`;
      });
    const name = mapping.classes[kind].types[0].slice(3);
    lines.push(`rbs:${name}Attributes a sh:NodeShape ;`, `    sh:targetClass ${mapping.classes[kind].types[0]} ;`,
      `    sh:property\n        ${props.join(" ,\n        ")} .`, "");
  }
  for (const node of Object.values(nodes)) {
    const props = Object.values(node.fields).map((f) =>
      `[ sh:path ${f.property} ; sh:maxCount 1 ; ${f.scheme ? `sh:node ${schemeShape(f.scheme)}` : `sh:datatype ${f.datatype ?? "xsd:string"}`}${f.range ? ` ; ${f.range}` : ""} ]`);
    lines.push(`rbs:${node.class.slice(3)} a sh:NodeShape ;`, `    sh:class ${node.class} ;`, `    sh:property\n        ${props.join(" ,\n        ")} .`, "");
  }
  lines.push(
    "rbs:MissingValue a sh:NodeShape ;",
    `    sh:class ${missing.class} ;`,
    `    sh:property [ sh:path ${missing.field} ; sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:string ] ,`,
    `        [ sh:path ${missing.reason} ; sh:minCount 1 ; sh:maxCount 1 ; sh:node ${schemeShape("missingness")} ] ,`,
    `        [ sh:path ${missing.note} ; sh:maxCount 1 ; sh:datatype xsd:string ] .`,
    "",
  );
  return lines.join("\n");
}
