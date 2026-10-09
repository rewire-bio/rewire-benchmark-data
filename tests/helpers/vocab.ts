import fs from "node:fs";
import { readCsv, readTable } from "../../scripts/omics/migrate-vocab";

/** Translate a value as written in an original extraction batch into the concept key the
 * canonical store now holds: the reviewed migration table in data/vocab/migration/, then any
 * reviewed correction in data/vocab/corrections/ for that record and field. */
const tables = new Map<string, ReturnType<typeof readTable>>();
const corrections = fs
  .readdirSync("data/vocab/corrections")
  .sort()
  .flatMap((file) => readCsv(fs.readFileSync(`data/vocab/corrections/${file}`, "utf8")));
export function migrated(scheme: string, source: string, recordId?: string, field?: string): string {
  if (!tables.has(scheme)) tables.set(scheme, readTable(scheme));
  const row = tables.get(scheme)!.get(source);
  if (!row) throw new Error(`${source} is not in data/vocab/migration/${scheme}.csv`);
  let value = row.concept;
  if (recordId && field)
    for (const c of corrections)
      if (c.record_id === recordId && c.field === field && c.old_value === value) value = c.new_value;
  return value;
}
