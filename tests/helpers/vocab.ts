import { readTable } from "../../scripts/omics/migrate-vocab";

/** Translate a value as written in an original extraction batch into the concept key the
 * canonical store now holds, using the reviewed tables in data/vocab/migration/. */
const tables = new Map<string, ReturnType<typeof readTable>>();
export function migrated(scheme: string, source: string): string {
  if (!tables.has(scheme)) tables.set(scheme, readTable(scheme));
  const row = tables.get(scheme)!.get(source);
  if (!row) throw new Error(`${source} is not in data/vocab/migration/${scheme}.csv`);
  return row.concept;
}
