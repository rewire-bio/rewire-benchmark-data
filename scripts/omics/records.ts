/** Canonical record store: one JSONL file per kind under data/entities and
 * data/evidence, and one provenance line per record in
 * data/provenance/records.jsonl. The provenance hash locks each record, so a
 * changed record fails the build until its change is recorded. */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { execFileSync } from "node:child_process";
import { recordSchema, validateRecords, type RecordEntry } from "./schema";
import { loadSchemes, validateVocabularies } from "./vocab";
import { validateAttributes } from "../../shared/omics/attributes";

/** The mapping and vocabularies are repository configuration, not store content: a store under
 * another root (as in tests) is validated against this repository's schemes. */
const readMapping = () => JSON.parse(fs.readFileSync("data/ontology/mapping.json", "utf8"));

export const evidenceKinds = ["evaluation", "result", "claim"] as const;
export const provenanceFile = "data/provenance/records.jsonl";

export type Provenance = {
  id: string;
  sha256: string;
  added_in: string;
  added_by: string;
  changed_by: { step: string; inputs: string; date?: string; review?: string }[];
};

const serialise = (record: RecordEntry) => JSON.stringify(record);
export const recordSha256 = (record: RecordEntry) =>
  crypto.createHash("sha256").update(serialise(record)).digest("hex");

export function recordFile(kind: string, root = "."): string {
  const folder = (evidenceKinds as readonly string[]).includes(kind) ? "evidence" : "entities";
  return path.join(root, "data", folder, `${kind.replace(/_/g, "-")}s.jsonl`);
}

export function recordFiles(root = "."): string[] {
  return ["entities", "evidence"].flatMap((folder) => {
    const dir = path.join(root, "data", folder);
    return fs.existsSync(dir)
      ? fs.readdirSync(dir).filter((name) => name.endsWith(".jsonl")).sort().map((name) => path.join(dir, name))
      : [];
  });
}

const readJsonl = (file: string) =>
  fs.readFileSync(file, "utf8").split("\n").filter(Boolean).map((line) => JSON.parse(line));

export function readProvenance(root = "."): Map<string, Provenance> {
  const file = path.join(root, provenanceFile);
  return new Map((fs.existsSync(file) ? readJsonl(file) : []).map((row: Provenance) => [row.id, row]));
}

/** Load every record, checking file placement, sort order and provenance. */
export function loadRecords(root = "."): RecordEntry[] {
  const provenance = readProvenance(root);
  const records: RecordEntry[] = [];
  for (const file of recordFiles(root)) {
    let previous = "";
    for (const value of readJsonl(file)) {
      const record = recordSchema.parse(value);
      if (recordFile(record.kind, root) !== file)
        throw new Error(`${record.id} (${record.kind}) is in the wrong file: ${file}`);
      if (record.id <= previous) throw new Error(`${file} is not sorted by unique ID at ${record.id}`);
      previous = record.id;
      const row = provenance.get(record.id);
      if (!row) throw new Error(`${record.id} has no provenance entry in ${provenanceFile}`);
      if (row.sha256 !== recordSha256(record))
        throw new Error(`${record.id} changed without a provenance entry. Record the change in ${provenanceFile}.`);
      records.push(record);
    }
  }
  if (provenance.size !== records.length)
    throw new Error(`${provenanceFile} lists ${provenance.size} records; the store holds ${records.length}`);
  validateVocabularies(readMapping(), records, loadSchemes());
  validateAttributes(records);
  return validateRecords(records.sort((a, b) => (a.id < b.id ? -1 : 1)));
}

function writeStore(records: RecordEntry[], provenance: Map<string, Provenance>, root = ".") {
  const byFile = new Map<string, RecordEntry[]>();
  for (const record of [...records].sort((a, b) => (a.id < b.id ? -1 : 1))) {
    const file = recordFile(record.kind, root);
    byFile.set(file, [...(byFile.get(file) ?? []), record]);
  }
  for (const [file, rows] of byFile) {
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, rows.map((row) => serialise(row) + "\n").join(""));
  }
  const rows = [...provenance.values()].sort((a, b) => (a.id < b.id ? -1 : 1));
  fs.mkdirSync(path.dirname(path.join(root, provenanceFile)), { recursive: true });
  fs.writeFileSync(path.join(root, provenanceFile), rows.map((row) => JSON.stringify(row) + "\n").join(""));
}

/** Append a reviewed batch of new records. Existing IDs are never replaced. */
export function addBatch(batchFile: string, batchDir: string, root = "."): number {
  const existing = loadRecords(root);
  const ids = new Set(existing.map((record) => record.id));
  const provenance = readProvenance(root);
  const additions = readJsonl(batchFile).map((value) => recordSchema.parse(value));
  for (const record of additions) {
    if (ids.has(record.id)) throw new Error(`Batch cannot replace or duplicate record: ${record.id}`);
    ids.add(record.id);
    provenance.set(record.id, {
      id: record.id, sha256: recordSha256(record), added_in: batchDir, added_by: "records:add", changed_by: [],
    });
  }
  validateVocabularies(readMapping(), additions, loadSchemes());
  validateAttributes(additions);
  validateRecords([...existing, ...additions]);
  writeStore([...existing, ...additions], provenance, root);
  return additions.length;
}

/** Record a reviewed change to existing records after editing them in place. */
export function recordChanges(ids: string[], inputs: string, review: string, root = "."): void {
  const provenance = readProvenance(root);
  const records = new Map(
    recordFiles(root).flatMap((file) => readJsonl(file)).map((value) => {
      const record = recordSchema.parse(value);
      return [record.id, record] as const;
    }),
  );
  const date = new Date().toISOString().slice(0, 10);
  for (const id of ids) {
    const record = records.get(id);
    const row = provenance.get(id);
    if (!record || !row) throw new Error(`Unknown record: ${id}`);
    row.sha256 = recordSha256(record);
    row.changed_by.push({ step: "records:change", inputs, date, review });
  }
  writeStore([...records.values()], provenance, root);
}

if (process.argv[1]?.endsWith("records.ts")) {
  const [command, ...args] = process.argv.slice(2);
  const usage = "Usage: npm run records -- check | add <batch.jsonl> <batch-dir> | change <review-path> <batch-dir> <id>...";
  if (command === "check") console.log(`${loadRecords().length} records match their provenance.`);
  else if (command === "add" && args.length === 2) {
    // The SHACL shapes are the record contract (issue #42, R6): export the store with the batch
    // and validate it, and put the store back exactly as it was if any record fails.
    const files = [...recordFiles(), provenanceFile];
    const before = new Map(files.map((file) => [file, fs.readFileSync(file)]));
    const added = addBatch(args[0], args[1]);
    try {
      execFileSync("npm", ["run", "-s", "kg:shapes"], { stdio: "inherit" });
    } catch {
      for (const file of recordFiles()) if (!before.has(file)) fs.rmSync(file);
      for (const [file, bytes] of before) fs.writeFileSync(file, bytes);
      console.error("The batch does not conform to data/ontology/shapes.ttl and attribute-shapes.ttl; the store is unchanged.");
      process.exit(1);
    }
    console.log(`Added ${added} records.`);
  }
  else if (command === "change" && args.length >= 3) {
    recordChanges(args.slice(2), args[1], args[0]);
    console.log(`Recorded changes to ${args.length - 2} records.`);
  } else {
    console.error(usage);
    process.exit(1);
  }
}
