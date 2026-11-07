/** Run the repository's own record validators over batch.jsonl without adding it to the store.
 *
 * `npm run records -- add` validates and adds in one step, and the extractor must not add the
 * batch (docs/collection.md step 5: review is a separate pass). This runs the same checks the
 * extractor can run alone: attribute registry and types, concept keys, description rules,
 * relation rules, and link and source resolution against the batch plus the existing store.
 *
 * Usage: npx tsx data/omics/benchbench-cloning-20261106/extract/validate_batch.ts
 */
import fs from "node:fs";
import { validateAttributes } from "../../../../shared/omics/attributes.js";
import { validateDescriptions } from "../../../../shared/omics/descriptions.js";
import { entityKinds } from "../../../../shared/omics/entity-kinds.js";
import { relationAllows } from "../../../../shared/omics/relations.js";
import { loadRecords } from "../../../../scripts/omics/records.js";

const batchFile = "data/omics/benchbench-cloning-20261106/batch.jsonl";

type Rec = {
  id: string;
  kind: string;
  name: string;
  description: string;
  status: string;
  facets: Record<string, string[]>;
  source_ids: string[];
  links: { relation: string; target_id: string }[];
  attributes: Record<string, unknown>;
};

const batch: Rec[] = fs
  .readFileSync(batchFile, "utf8")
  .split("\n")
  .filter(Boolean)
  .map((line) => JSON.parse(line) as Rec);

const problems: string[] = [];
const fail = (message: string) => problems.push(message);

const statuses = new Set([
  "discovered",
  "needs_review",
  "source_checked",
  "reproduced",
  "disputed",
  "superseded",
  "excluded",
]);

for (const record of batch) {
  if (!(entityKinds as readonly string[]).includes(record.kind))
    fail(`${record.id}: unknown kind ${record.kind}`);
  if (!statuses.has(record.status)) fail(`${record.id}: unknown status ${record.status}`);
  if (!record.name?.trim()) fail(`${record.id}: no name`);
  if (!record.description?.trim()) fail(`${record.id}: no description`);
  if (!Array.isArray(record.source_ids) || record.source_ids.length === 0)
    if (record.kind !== "source") fail(`${record.id}: no source_ids`);
}

// Attribute registry, types and concept keys.
try {
  validateAttributes(batch);
} catch (error) {
  fail(`attributes: ${(error as Error).message}`);
}

// Description rules (placeholders, provenance, shared descriptions).
try {
  validateDescriptions(batch);
} catch (error) {
  fail(`descriptions: ${(error as Error).message}`);
}

// Relations: the kinds each may link from and to.
const store = loadRecords();
const kindOf = new Map<string, string>([
  ...store.map((r) => [r.id, r.kind] as [string, string]),
  ...batch.map((r) => [r.id, r.kind] as [string, string]),
]);
const storeIds = new Set(store.map((r) => r.id));

for (const record of batch) {
  if (storeIds.has(record.id)) fail(`${record.id}: already in the store`);
  for (const link of record.links) {
    const targetKind = kindOf.get(link.target_id);
    if (!targetKind) {
      fail(`${record.id}: link ${link.relation} to unknown ${link.target_id}`);
      continue;
    }
    if (!relationAllows(link.relation, record.kind, targetKind))
      fail(
        `${record.id}: relation ${link.relation} not allowed from ${record.kind} to ${targetKind}`,
      );
  }
  for (const sourceId of record.source_ids) {
    const sourceKind = kindOf.get(sourceId);
    if (sourceKind !== "source")
      fail(`${record.id}: source_ids entry ${sourceId} is ${sourceKind ?? "missing"}, not a source`);
  }
}

// Evaluations need exactly one system, assessment and data link; results exactly one evaluation.
for (const record of batch) {
  const count = (relation: string) =>
    record.links.filter((link) => link.relation === relation).length;
  if (record.kind === "evaluation")
    for (const relation of ["system", "assessment", "data"])
      if (count(relation) !== 1)
        fail(`${record.id}: evaluation has ${count(relation)} ${relation} links, expected 1`);
  if (record.kind === "result" && count("evaluation") !== 1)
    fail(`${record.id}: result has ${count("evaluation")} evaluation links, expected 1`);
  if (record.kind === "claim" && count("subject") !== 1)
    fail(`${record.id}: claim has ${count("subject")} subject links, expected 1`);
}

// A field never has both a value and a missing reason.
for (const record of batch) {
  const missing = record.attributes.missing_metadata;
  if (missing && typeof missing === "object")
    for (const field of Object.keys(missing as Record<string, unknown>))
      if (record.attributes[field] !== undefined)
        fail(`${record.id}: ${field} has both a value and a missing reason`);
}

if (problems.length) {
  console.error(`${problems.length} problem(s):`);
  for (const problem of problems.slice(0, 60)) console.error(`  ${problem}`);
  if (problems.length > 60) console.error(`  ... and ${problems.length - 60} more`);
  process.exit(1);
}
console.log(`batch.jsonl: ${batch.length} records, no problems found`);
