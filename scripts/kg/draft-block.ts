/** The `draft` block of the KG bundle manifest: what rdf-kg-mcp's draft tools (serve --drafts)
 * need to know about a record, so the server holds nothing specific to this store.
 * See https://github.com/rewire-bio/rdf-kg-mcp/blob/main/docs/bundle-format.md#draft-block.
 *
 * Everything here is derived from the code `records add` uses (recordSchema, relationRules and
 * the class mapping), so the server's advisory checks follow the store's rules. `records add`
 * in a pull request remains the gate. */
import { entityKinds } from "../../shared/omics/entity-kinds";
import { relationRules } from "../../shared/omics/relations";
import { recordIdPattern, recordSchema, statuses } from "../omics/schema";
import type { Mapping } from "./export";

/** Kinds a draft may have. Evaluations, results and claims carry numbers and quotes whose spans
 * must resolve against archived layer bytes, which a draft overlay cannot reach. Baselines are
 * left out because they link to evaluations (measured_in), which are out of scope too. */
export const draftKinds = entityKinds.filter((kind) => !["evaluation", "result", "claim", "baseline"].includes(kind));

export function draftBlock(mapping: Mapping) {
  const shape = Object.keys(recordSchema.shape);
  const properties: Record<string, unknown> = {
    id: { type: "string", pattern: recordIdPattern.source },
    kind: { enum: [...entityKinds] },
    name: { type: "string", minLength: 1 },
    description: { type: "string" },
    status: { enum: [...statuses] },
    facets: { type: "object", additionalProperties: { type: "array", items: { type: "string" } } },
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
