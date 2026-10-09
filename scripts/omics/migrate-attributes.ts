/** Convert record attributes in the canonical store to their declared shapes (issue #42, stage 3).
 *
 * Applies shared/omics/attributes.ts normalizeAttributes, the same function every reader uses
 * on older releases, with the reviewed table of free-text missing reasons in
 * data/vocab/migration/missingness.csv. Scaffolding attributes listed in movedAttributes are
 * copied to data/provenance/moved-attributes.jsonl before they leave the record. Each changed
 * record is recorded in data/provenance/records.jsonl. Running it again changes nothing.
 *
 * Usage: npm run attributes:migrate -- <review.md>
 *        npm run attributes:migrate -- --batch <batch.jsonl>  (convert a new batch in place, before
 *                                                              review and npm run records -- add)
 *        npm run attributes:migrate -- --dump <out.jsonl>    (write converted records only) */
import fs from "node:fs";
import { movedAttributes, normalizeAttributes, type MissingLookup, type MissingReason } from "../../shared/omics/attributes";
import { readCsv } from "./migrate-vocab";
import { recordChanges, recordFiles } from "./records";

type StoreRecord = {
  id: string;
  kind: string;
  links: { relation: string; target_id: string }[];
  attributes: Record<string, unknown>;
};

export const movedFile = "data/provenance/moved-attributes.jsonl";

export function readMissingLookup(file = "data/vocab/migration/missingness.csv"): MissingLookup {
  return new Map(
    readCsv(fs.readFileSync(file, "utf8")).map((row) => [
      row.source_string,
      { reason: row.reason as MissingReason | "not_missing", keepNote: row.keep_note === "yes" },
    ]),
  );
}

if (process.argv[1]?.endsWith("migrate-attributes.ts")) {
  const [first, second] = process.argv.slice(2);
  if (first === "--batch") {
    const lines = fs.readFileSync(second, "utf8").split("\n").filter(Boolean).map((line) => JSON.parse(line) as StoreRecord);
    const ids = new Set(lines.map((record) => record.id));
    const store = recordFiles().flatMap((file) => fs.readFileSync(file, "utf8").split("\n").filter(Boolean).map((line) => JSON.parse(line) as StoreRecord));
    const converted = normalizeAttributes([...store.filter((record) => !ids.has(record.id)), ...lines], readMissingLookup())
      .filter((record) => ids.has(record.id));
    fs.writeFileSync(second, converted.map((record) => JSON.stringify(record) + "\n").join(""));
    console.log(`Converted ${converted.length} batch records in ${second}.`);
    process.exit(0);
  }
  const dump = first === "--dump" ? second : undefined;
  const review = dump ? undefined : first;
  if (!dump && (!review || !fs.existsSync(review))) {
    console.error("Usage: npm run attributes:migrate -- <review.md>  (the review must exist)");
    process.exit(1);
  }
  const files = new Map(
    recordFiles().map((file) => [
      file,
      fs.readFileSync(file, "utf8").split("\n").filter(Boolean).map((line) => JSON.parse(line) as StoreRecord),
    ]),
  );
  const all = [...files.values()].flat();
  const normalized = new Map(normalizeAttributes(all, readMissingLookup()).map((record) => [record.id, record]));
  if (dump) {
    fs.writeFileSync(dump, [...normalized.values()].map((record) => JSON.stringify(record) + "\n").join(""));
    console.log(`Wrote ${normalized.size} converted records to ${dump}.`);
    process.exit(0);
  }
  const moved = all.flatMap((record) => {
    const kept = Object.fromEntries(movedAttributes.filter((key) => key in record.attributes).map((key) => [key, record.attributes[key]]));
    return Object.keys(kept).length ? [JSON.stringify({ id: record.id, attributes: kept, moved_by: review }) + "\n"] : [];
  });
  if (moved.length) {
    const previous = fs.existsSync(movedFile) ? fs.readFileSync(movedFile, "utf8") : "";
    fs.writeFileSync(movedFile, previous + moved.join(""));
  }
  const changed = all.filter((record) => normalized.get(record.id) !== record).map((record) => record.id);
  for (const [file, records] of files)
    if (records.some((record) => normalized.get(record.id) !== record))
      fs.writeFileSync(file, records.map((record) => JSON.stringify(normalized.get(record.id)) + "\n").join(""));
  if (changed.length) recordChanges(changed.sort(), "shared/omics/attributes.ts", review!);
  console.log(`Converted attributes on ${changed.length} records; moved scaffolding from ${moved.length}.`);
}
