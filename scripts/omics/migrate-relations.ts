/** Rename relationships in the canonical store to their single-meaning names (issue #42, stage 2).
 *
 * Applies shared/omics/relations.ts normalizeRecords, the same function every reader
 * uses on older releases, to the records in data/entities and data/evidence, and records each
 * changed record in data/provenance/records.jsonl. Claims whose field cites a renamed link
 * ("links:variant_of:...") are updated with it. Running it again changes nothing.
 *
 * Usage: npm run relations:migrate -- <review.md> */
import fs from "node:fs";
import { normalizeRecords } from "../../shared/omics/relations";
import { recordChanges, recordFiles } from "./records";

type StoreRecord = {
  id: string;
  kind: string;
  links: { relation: string; target_id: string }[];
  attributes: Record<string, unknown>;
};

const review = process.argv[2];
if (!review || !fs.existsSync(review)) {
  console.error("Usage: npm run relations:migrate -- <review.md>  (the review must exist)");
  process.exit(1);
}
const files = new Map(
  recordFiles().map((file) => [
    file,
    fs.readFileSync(file, "utf8").split("\n").filter(Boolean).map((line) => JSON.parse(line) as StoreRecord),
  ]),
);
const all = [...files.values()].flat();
const normalized = new Map(normalizeRecords(all).map((record) => [record.id, record]));
const changed = all.filter((record) => normalized.get(record.id) !== record).map((record) => record.id);
for (const [file, records] of files)
  if (records.some((record) => normalized.get(record.id) !== record))
    fs.writeFileSync(file, records.map((record) => JSON.stringify(normalized.get(record.id)) + "\n").join(""));
if (changed.length) recordChanges(changed.sort(), "shared/omics/relations.ts", review);
console.log(`Renamed relationships in ${changed.length} records.`);
