/** The `draft` block of the KG bundle manifest: what rdf-kg-mcp's draft tools (serve --drafts)
 * need to know about a record, so the server holds nothing specific to this store.
 * See https://github.com/rewire-bio/rdf-kg-mcp/blob/main/docs/bundle-format.md#draft-block.
 *
 * Everything here is derived from the code `records add` uses (recordSchema, relationRules, the
 * class mapping, the attribute registry and the vocabularies), so the server's advisory checks
 * follow the store's rules. `records add` in a pull request remains the gate. */
import { z } from "zod";
import { attributeRegistry } from "../../shared/omics/attribute-registry";
import { attributeTypes } from "../../shared/omics/attributes";
import { entityKinds } from "../../shared/omics/entity-kinds";
import { relationRules } from "../../shared/omics/relations";
import { recordIdPattern, recordSchema, statuses } from "../omics/schema";
import { loadSchemes, type Scheme } from "../omics/vocab";
import type { Mapping } from "./export";

type JsonSchema = Record<string, unknown>;

/** One zod type as JSON Schema. Refinements (superRefine) have no JSON Schema form and are left to
 * records add; everything else (types, patterns, enums, strict objects) carries over. */
function jsonSchema(type: z.ZodType): JsonSchema {
  const { $schema: _, ...rest } = z.toJSONSchema(type, { io: "input", unrepresentable: "any" }) as JsonSchema;
  return rest;
}

const typeName = (type: string) => (type.startsWith("concepts:") ? "concepts" : type.startsWith("concept:") ? "concept" : type);
const ref = (def: string) => ({ $ref: `#/$defs/${def}` });

/** A controlled value: one concept key of the scheme, or a list of them when the field is a list.
 * validateVocabularies checks every item of a list against the scheme. */
function controlled(base: JsonSchema, scheme: string): JsonSchema {
  return base.type === "array" ? { type: "array", items: ref(`scheme-${scheme}`) } : ref(`scheme-${scheme}`);
}

/** JSON Schema for the parts of a record records add checks beyond recordSchema: which attribute
 * keys each kind may carry and their types (validateAttributes), and which values come from a
 * vocabulary (validateVocabularies, through mapping.json). */
export function attributeSchemas(mapping: Mapping, schemes: Map<string, Scheme> = loadSchemes()) {
  const used = new Set<string>();
  const control = (base: JsonSchema, scheme: string | undefined) => {
    if (!scheme) return base;
    if (!schemes.has(scheme)) throw new Error(`draft block: no vocabulary data/vocab/${scheme}.ttl`);
    used.add(scheme);
    return controlled(base, scheme);
  };
  const types: Record<string, JsonSchema> = Object.fromEntries(
    Object.entries(attributeTypes).map(([name, type]) => [name, jsonSchema(type as z.ZodType)]),
  );
  // Values inside structured attributes that are controlled too (vocab.ts, controlledValues).
  const patch = (name: string, terms: Record<string, string | undefined>) => {
    const properties = { ...(types[name].properties as Record<string, JsonSchema>) };
    for (const [field, scheme] of Object.entries(terms))
      if (scheme && field in properties) properties[field] = control(properties[field], scheme);
    types[name] = { ...types[name], properties };
  };
  patch("review", Object.fromEntries(Object.entries(mapping.review).map(([field, term]) => [field, term.scheme])));
  patch("derivation", { method: "derivation-method" });

  const registry = attributeRegistry as Record<string, Record<string, string>>;
  const perKind = entityKinds.map((kind) => {
    const declared = registry[kind] ?? {};
    const properties = Object.fromEntries(
      Object.entries(declared).map(([key, type]) => {
        const name = typeName(type);
        const scheme = mapping.attributes[key]?.scheme;
        return [key, scheme ? { allOf: [ref(`type-${name}`), control(types[name], scheme)] } : ref(`type-${name}`)];
      }),
    );
    return {
      if: { properties: { kind: { const: kind } }, required: ["kind"] },
      then: { properties: { attributes: { properties, additionalProperties: false } } },
    };
  });
  const facets = Object.fromEntries(
    Object.entries(mapping.facets)
      .filter(([, term]) => term.scheme)
      .map(([name, term]) => [name, control({ type: "array", items: { type: "string" } }, term.scheme)]),
  );
  const defs: Record<string, JsonSchema> = {};
  for (const name of Object.keys(types).sort()) defs[`type-${name}`] = types[name];
  for (const name of [...used].sort()) defs[`scheme-${name}`] = { type: "string", enum: [...schemes.get(name)!.concepts.keys()].sort() };
  return { defs, perKind, facets };
}

/** Kinds a draft may have. Evaluations, results and claims carry numbers and quotes whose spans
 * must resolve against archived layer bytes, which a draft overlay cannot reach. Baselines are
 * left out because they link to evaluations (measured_in), which are out of scope too. */
export const draftKinds = entityKinds.filter((kind) => !["evaluation", "result", "claim", "baseline"].includes(kind));

export function draftBlock(mapping: Mapping, schemes?: Map<string, Scheme>) {
  const { defs, perKind, facets: controlledFacets } = attributeSchemas(mapping, schemes);
  const shape = Object.keys(recordSchema.shape);
  const properties: Record<string, unknown> = {
    id: { type: "string", pattern: recordIdPattern.source },
    kind: { enum: [...entityKinds] },
    name: { type: "string", minLength: 1 },
    description: { type: "string" },
    status: { enum: [...statuses] },
    facets: { type: "object", properties: controlledFacets, additionalProperties: { type: "array", items: { type: "string" } } },
    source_ids: { type: "array", items: { type: "string", minLength: 1 } },
    links: {
      type: "array",
      items: {
        type: "object",
        required: ["relation", "target_id"],
        properties: { relation: { enum: Object.keys(relationRules) }, target_id: { type: "string", minLength: 1 } },
        additionalProperties: false,
      },
    },
    attributes: { type: "object" },
  };
  const missing = shape.filter((key) => !(key in properties));
  if (missing.length) throw new Error(`draft block: no JSON Schema for record fields ${missing.join(", ")}`);
  return {
    iri_base: mapping.base,
    id_field: "id",
    type_field: "kind",
    label_field: "name",
    record_schema: {
      type: "object",
      required: shape,
      // In recordSchema order, which is the field order records add writes.
      properties: Object.fromEntries(shape.map((key) => [key, properties[key]])),
      additionalProperties: false,
      // Per kind: the declared attribute keys and their types. Controlled values are keys of a vocabulary.
      allOf: perKind,
      $defs: defs,
    },
    // The first mapped type of each kind is its own rb: class; shared types (dcat:Dataset) come later.
    kinds: Object.fromEntries(entityKinds.map((kind) => [kind, mapping.classes[kind].types[0]])),
    draft_kinds: draftKinds,
    links: { field: "links", relation: "relation", target: "target_id" },
    link_rules: Object.fromEntries(
      // Some rules list a kind twice (applicable_to adds evaluator to the assessments, which hold it).
      Object.entries(relationRules).map(([relation, rule]) => [relation, { from: [...new Set(rule.from)], to: [...new Set(rule.to)], description: rule.meaning }]),
    ),
    references: [{ field: "source_ids", kinds: ["source"] }],
    // facets and attributes are z.record, so their key order is kept by records add and is part of the
    // digest. Sorting them makes two drafts of the same record give the same bytes. Links carry no order;
    // source_ids keep the caller's order, because some extraction scripts treat the first as the primary source.
    sort_within: ["attributes", "facets"],
    sort_arrays: ["links"],
  };
}
