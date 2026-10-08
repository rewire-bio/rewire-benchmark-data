import { loadRecords, readProvenance } from "../../scripts/omics/records";
import type { RecordEntry } from "../../scripts/omics/schema";

export const records: RecordEntry[] = loadRecords();
export const recordsById = new Map(records.map((record) => [record.id, record]));

/** Records a batch originally added, in their current form. */
export function batchRecords(addedIn: string): RecordEntry[] {
  return [...readProvenance().values()]
    .filter((row) => row.added_in === addedIn)
    .map((row) => recordsById.get(row.id)!);
}

export function readJsonl<T = unknown>(file: string): T[] {
  return require("node:fs").readFileSync(file, "utf8").split("\n").filter(Boolean).map((line: string) => JSON.parse(line));
}

/** The one frozen release kept in the repository. */
export function currentReleaseDir(): string {
  const fs = require("node:fs");
  const dirs = fs.readdirSync("data/omics/releases", { withFileTypes: true })
    .filter((entry: { isDirectory(): boolean }) => entry.isDirectory())
    .map((entry: { name: string }) => entry.name);
  if (dirs.length !== 1) throw new Error(`Expected one frozen release, found ${dirs.length}`);
  return `data/omics/releases/${dirs[0]}`;
}
