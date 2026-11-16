/** Run the repository's own record checks over this batch without writing to the store.
 *
 * It loads data/entities for link targets, kinds and the shared-description check, then applies
 * the schema, the vocabularies, the attribute registry, the description rules and the relation
 * rules to the batch records. It never writes anything.
 *
 * Run from the repository root:
 *   npx tsx data/omics/poisk-20261115/extract/validate_batch.ts
 */
import fs from "node:fs";
import path from "node:path";
import { recordSchema } from "../../../../scripts/omics/schema";
import { loadSchemes, validateVocabularies } from "../../../../scripts/omics/vocab";
import { attributeIssues } from "../../../../shared/omics/attributes";
import { descriptionProblems } from "../../../../shared/omics/descriptions";
import { relationAllows } from "../../../../shared/omics/relations";
import { validateDatasetReuseLink } from "../../../../shared/omics/entity-kinds";

const BATCH = "data/omics/poisk-20261115/batch.jsonl";
const readJsonl = (file: string) =>
  fs
    .readFileSync(file, "utf8")
    .split("\n")
    .filter((line) => line.trim())
    .map((line) => JSON.parse(line));

const entityDir = "data/entities";
const existing = fs
  .readdirSync(entityDir)
  .filter((name) => name.endsWith(".jsonl"))
  .flatMap((name) => readJsonl(path.join(entityDir, name)));
const batch = readJsonl(BATCH).map((value) => recordSchema.parse(value));

const problems: string[] = [];
const kinds = new Map<string, string>();
for (const record of [...existing, ...batch]) kinds.set(record.id, record.kind);
for (const record of batch) {
  if (existing.some((other) => other.id === record.id)) problems.push(`${record.id} already exists in the store`);
  for (const issue of attributeIssues(record)) problems.push(`${record.id}: ${issue}`);
  for (const id of record.source_ids)
    if (kinds.get(id) !== "source") problems.push(`${record.id}: source_ids names ${id}, which is not a source record`);
  for (const link of record.links) {
    const targetKind = kinds.get(link.target_id);
    if (!targetKind) {
      problems.push(`${record.id}: link ${link.relation} points at the unknown record ${link.target_id}`);
      continue;
    }
    if (!relationAllows(link.relation, record.kind, targetKind))
      problems.push(`${record.id}: ${link.relation} cannot link ${record.kind} to ${targetKind} ${link.target_id}`);
    try {
      validateDatasetReuseLink(record, link, { id: link.target_id, kind: targetKind });
    } catch (error) {
      problems.push(`${record.id}: ${(error as Error).message}`);
    }
  }
  if (record.kind === "evaluation")
    for (const role of ["system", "assessment", "data"])
      if (record.links.filter((link) => link.relation === role).length !== 1)
        problems.push(`${record.id}: evaluation needs exactly one ${role} link`);
  if (record.kind === "result" && record.links.filter((link) => link.relation === "evaluation").length !== 1)
    problems.push(`${record.id}: result needs exactly one evaluation link`);
}
for (const problem of descriptionProblems([...existing, ...batch] as never).filter((p) =>
  batch.some((record) => record.id === p.id),
))
  problems.push(`${problem.id}: ${problem.message}${problem.shared_with ? ` (${problem.shared_with.join(", ")})` : ""}`);

try {
  validateVocabularies(JSON.parse(fs.readFileSync("data/ontology/mapping.json", "utf8")), batch, loadSchemes());
} catch (error) {
  problems.push((error as Error).message);
}

const sorted = batch.map((record) => record.id);
if (sorted.join("\u0000") !== [...sorted].sort().join("\u0000")) problems.push("batch.jsonl is not sorted by ID");

if (problems.length) {
  console.error(`${problems.length} problems:\n${problems.join("\n")}`);
  process.exit(1);
}
console.log(`${batch.length} records pass the schema, attribute, vocabulary, description and relation checks.`);
