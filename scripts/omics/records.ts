/** Canonical record store. Entity kinds are one JSONL file per kind under data/entities.
 * Evidence kinds (evaluations, results, claims) and the provenance log are sharded: a record
 * is in data/evidence/<kind>s/<shard>.jsonl and its provenance line in
 * data/provenance/records/<shard>.jsonl, where <shard> is the first hex digit of the SHA-256
 * of its ID (docs/collection.md, "Where records live"). Every file is sorted by ID. The
 * provenance hash locks each record, so a changed record fails the build until its change
 * is recorded. */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";
import { execFileSync } from "node:child_process";
import { recordSchema, validateRecords, type RecordEntry } from "./schema";
import { loadSchemes, validateVocabularies } from "./vocab";
import { validateConcerns } from "../../shared/omics/concerns";
import { validateAttributes } from "../../shared/omics/attributes";
import { validateDerivations } from "./derivations";
import { descriptionProblems, validateDescriptions } from "../../shared/omics/descriptions";

/** The mapping and vocabularies are repository configuration, not store content: a store under
 * another root (as in tests) is validated against this repository's schemes. */
const readMapping = () => JSON.parse(fs.readFileSync("data/ontology/mapping.json", "utf8"));

export const evidenceKinds = ["evaluation", "result", "claim"] as const;
/** Kinds whose records are split across shard files. */
export const shardedKinds: readonly string[] = evidenceKinds;
/** Hex digits of SHA-256(id) that name a record's shard: 1 gives 16 shards per kind. */
export const shardDigits = 1;
/** Folder of the sharded provenance log. */
export const provenanceDir = "data/provenance/records";
/** The provenance log as one logical file: the name release receipts give its digest. */
export const provenanceFile = "data/provenance/records.jsonl";

export type Provenance = {
  id: string;
  sha256: string;
  added_in: string;
  added_by: string;
  changed_by: { step: string; inputs: string; date?: string; review?: string }[];
};

const serialise = (record: RecordEntry) => JSON.stringify(record);
const sha256 = (text: string) => crypto.createHash("sha256").update(text).digest("hex");
export const recordSha256 = (record: RecordEntry) => sha256(serialise(record));
const byId = <T extends { id: string }>(a: T, b: T) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0);

/** The shard a record ID belongs to. */
export const shardOf = (id: string) => sha256(id).slice(0, shardDigits);

/** A kind's store file or, for a sharded kind, its folder of shards. */
function kindPath(kind: string, root: string): string {
  const folder = (evidenceKinds as readonly string[]).includes(kind) ? "evidence" : "entities";
  const name = `${kind.replace(/_/g, "-")}s`;
  return path.join(root, "data", folder, shardedKinds.includes(kind) ? name : `${name}.jsonl`);
}

/** The file a record belongs in. */
export function recordFile(record: { kind: string; id: string }, root = "."): string {
  const base = kindPath(record.kind, root);
  return shardedKinds.includes(record.kind) ? path.join(base, `${shardOf(record.id)}.jsonl`) : base;
}

const jsonlIn = (dir: string) =>
  fs.existsSync(dir)
    ? fs.readdirSync(dir).filter((name) => name.endsWith(".jsonl")).sort().map((name) => path.join(dir, name))
    : [];

/** Every store file of one kind. */
export function kindFiles(kind: string, root = "."): string[] {
  const base = kindPath(kind, root);
  if (shardedKinds.includes(kind)) return jsonlIn(base);
  return fs.existsSync(base) ? [base] : [];
}

/** Every store file: the entity files, then each evidence kind's shards. */
export function recordFiles(root = "."): string[] {
  return ["entities", "evidence"].flatMap((folder) => {
    const dir = path.join(root, "data", folder);
    if (!fs.existsSync(dir)) return [];
    return fs.readdirSync(dir, { withFileTypes: true })
      .sort((a, b) => (a.name < b.name ? -1 : 1))
      .flatMap((entry) =>
        entry.isDirectory() ? jsonlIn(path.join(dir, entry.name))
        : entry.name.endsWith(".jsonl") ? [path.join(dir, entry.name)] : []);
  });
}

export const provenanceFileFor = (id: string, root = ".") => path.join(root, provenanceDir, `${shardOf(id)}.jsonl`);
export const provenanceFiles = (root = ".") => jsonlIn(path.join(root, provenanceDir));

const readLines = (file: string) => fs.readFileSync(file, "utf8").split("\n").filter(Boolean);
const readJsonl = (file: string) => readLines(file).map((line) => JSON.parse(line));

/** Every stored record of one kind, across its shards, sorted by ID. Not validated. */
export function readKind<T extends { id: string } = RecordEntry>(kind: string, root = "."): T[] {
  return kindFiles(kind, root).flatMap((file) => readJsonl(file) as T[]).sort(byId);
}

function writeGrouped(entries: [string, { id: string }][]) {
  const byFile = new Map<string, { id: string }[]>();
  for (const [file, row] of entries) byFile.set(file, [...(byFile.get(file) ?? []), row]);
  for (const [file, rows] of byFile) {
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, [...rows].sort(byId).map((row) => JSON.stringify(row) + "\n").join(""));
  }
}

/** Write every record of one kind to the files the layout assigns them. */
export function writeKind(kind: string, records: { id: string; kind: string }[], root = "."): void {
  writeGrouped(records.map((record) => {
    if (record.kind !== kind) throw new Error(`${record.id} is a ${record.kind}, not a ${kind}`);
    return [recordFile(record, root), record];
  }));
}

export function readProvenance(root = "."): Map<string, Provenance> {
  const rows = new Map<string, Provenance>();
  for (const file of provenanceFiles(root))
    for (const row of readJsonl(file) as Provenance[]) {
      if (provenanceFileFor(row.id, root) !== file) throw new Error(`Provenance for ${row.id} is in the wrong file: ${file}`);
      rows.set(row.id, row);
    }
  return rows;
}

const idOf = (line: string) => (JSON.parse(line) as { id: string }).id;
/** SHA-256 of the files' lines in ID order: the bytes they would have as one unsharded file. */
const logicalDigest = (files: string[]) =>
  sha256(files.flatMap(readLines).map((line) => ({ id: idOf(line), line })).sort(byId).map(({ line }) => line + "\n").join(""));

/** Digests of the store as one file per kind plus one provenance file, whatever the sharding.
 * A sharded kind's digest is that of its lines in ID order, which is the file it was before it
 * was split, so release receipts and release IDs do not depend on the shard layout. */
export function storeDigests(root = "."): { file: string; sha256: string }[] {
  const logical = new Map<string, string[]>();
  for (const file of recordFiles(root)) {
    const parts = path.relative(root, file).split(path.sep);
    // data/evidence/results/0.jsonl is part of data/evidence/results.jsonl.
    const name = parts.length === 4 ? `${parts.slice(0, 3).join("/")}.jsonl` : parts.join("/");
    logical.set(name, [...(logical.get(name) ?? []), file]);
  }
  return [
    ...[...logical].sort(([a], [b]) => (a < b ? -1 : 1)).map(([file, files]) => ({ file, sha256: logicalDigest(files) })),
    { file: provenanceFile, sha256: logicalDigest(provenanceFiles(root)) },
  ];
}

/** Move every record and provenance line to the file the current layout assigns it, keeping
 * each line's bytes, and delete store files the layout no longer uses. Run after changing
 * shardedKinds or shardDigits, or to split an unsharded store. */
export function reshardStore(root = "."): number {
  const legacyProvenance = path.join(root, provenanceFile);
  const oldProvenance = [...provenanceFiles(root), ...(fs.existsSync(legacyProvenance) ? [legacyProvenance] : [])];
  const oldRecords = recordFiles(root);
  const records = oldRecords.flatMap(readLines).map((line) => {
    const { id, kind } = JSON.parse(line) as { id: string; kind: string };
    return { id, file: recordFile({ id, kind }, root), line };
  });
  const provenance = oldProvenance.flatMap(readLines).map((line) => {
    const id = idOf(line);
    return { id, file: provenanceFileFor(id, root), line };
  });
  const byFile = new Map<string, { id: string; line: string }[]>();
  for (const row of [...records, ...provenance]) byFile.set(row.file, [...(byFile.get(row.file) ?? []), row]);
  for (const file of [...oldRecords, ...oldProvenance]) if (!byFile.has(file)) fs.rmSync(file);
  for (const [file, rows] of byFile) {
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, rows.sort(byId).map((row) => row.line + "\n").join(""));
  }
  for (const dir of new Set(oldRecords.map((file) => path.dirname(file))))
    if (fs.existsSync(dir) && !fs.readdirSync(dir).length) fs.rmdirSync(dir);
  return records.length;
}

/** Load every record, checking file placement, sort order and provenance. */
export function loadRecords(root = "."): RecordEntry[] {
  const provenance = readProvenance(root);
  const records: RecordEntry[] = [];
  for (const file of recordFiles(root)) {
    let previous = "";
    for (const value of readJsonl(file)) {
      const record = recordSchema.parse(value);
      if (recordFile(record, root) !== file)
        throw new Error(`${record.id} (${record.kind}) is in the wrong file: ${file}`);
      if (record.id <= previous) throw new Error(`${file} is not sorted by unique ID at ${record.id}`);
      previous = record.id;
      const row = provenance.get(record.id);
      if (!row) throw new Error(`${record.id} has no provenance entry in ${provenanceDir}`);
      if (row.sha256 !== recordSha256(record))
        throw new Error(`${record.id} changed without a provenance entry. Record the change in ${provenanceDir}.`);
      records.push(record);
    }
  }
  if (provenance.size !== records.length)
    throw new Error(`${provenanceDir} lists ${provenance.size} records; the store holds ${records.length}`);
  validateVocabularies(readMapping(), records, loadSchemes());
  validateAttributes(records);
  validateDerivations(records, root);
  validateDescriptions(records);
  validateConcerns(records);
  return validateRecords(records.sort(byId));
}

/** Write records and their provenance to the files the layout assigns them. */
export function writeStore(records: RecordEntry[], provenance: Map<string, Provenance>, root = ".") {
  writeGrouped(records.map((record) => [recordFile(record, root), record]));
  writeGrouped([...provenance.values()].map((row) => [provenanceFileFor(row.id, root), row]));
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
  validateDescriptions([...existing, ...additions]);
  validateDerivations([...existing, ...additions], root);
  validateConcerns([...existing, ...additions]);
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

/** The SHACL shapes are the record contract (issue #42, R6). Validate the records just written,
 * the records that link to them and their link targets (`npm run kg -- subset`), not the whole
 * store: that takes minutes and runs once in CI (`npm run kg:shapes`). If any checked record
 * fails, put the store back exactly as it was. */
function writeCheckedAgainstShapes(ids: () => string[], write: () => void, what: string) {
  const storeFiles = () => [...recordFiles(), ...provenanceFiles()];
  const before = new Map(storeFiles().map((file) => [file, fs.readFileSync(file)]));
  const restore = () => {
    for (const file of storeFiles()) if (!before.has(file)) fs.rmSync(file);
    for (const [file, bytes] of before) fs.writeFileSync(file, bytes);
  };
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "records-shapes-"));
  try {
    write();
    fs.writeFileSync(path.join(dir, "ids.txt"), ids().join("\n") + "\n");
    execFileSync("npm", ["run", "-s", "kg", "--", "subset", path.join(dir, "ids.txt"), dir], { stdio: "inherit" });
    execFileSync("npm", ["run", "-s", "kg:build", "--", "--shapes-only", "--kg-dir", dir, "--context", path.join(dir, "context.txt")], { stdio: "inherit" });
  } catch (error) {
    restore();
    fs.rmSync(dir, { recursive: true, force: true });
    if (!(error as { status?: number }).status) console.error(error);
    console.error(`${what} failed validation; the store is unchanged.`);
    process.exit(1);
  }
  fs.rmSync(dir, { recursive: true, force: true });
}

if (process.argv[1]?.endsWith("records.ts")) {
  const [command, ...args] = process.argv.slice(2);
  const usage = "Usage: npm run records -- check | descriptions [--json] | add <batch.jsonl> <batch-dir> | change <review-path> <batch-dir> <id>... | reshard";
  if (command === "check") console.log(`${loadRecords().length} records match their provenance.`);
  else if (command === "descriptions") {
    // Every description the check rejects, with counts by kind and rule (issue #88).
    const problems = descriptionProblems(recordFiles().flatMap((file) => readJsonl(file)) as RecordEntry[]);
    if (args.includes("--json")) console.log(JSON.stringify(problems, null, 2));
    else {
      const count = (key: (p: (typeof problems)[number]) => string) =>
        [...problems.reduce((m, p) => m.set(key(p), (m.get(key(p)) ?? 0) + 1), new Map<string, number>())].sort();
      for (const p of problems) console.log(`${p.id}\t${p.rule}\t${p.description}`);
      console.log(`\n${new Set(problems.map((p) => p.id)).size} records, ${problems.length} problems`);
      for (const [k, n] of count((p) => p.kind)) console.log(`  kind ${k}: ${n}`);
      for (const [k, n] of count((p) => p.rule)) console.log(`  rule ${k}: ${n}`);
    }
  }
  else if (command === "add" && args.length === 2) {
    let added = 0;
    writeCheckedAgainstShapes(
      () => readJsonl(args[0]).map((value: RecordEntry) => value.id),
      () => { added = addBatch(args[0], args[1]); },
      "The batch",
    );
    console.log(`Added ${added} records.`);
  }
  else if (command === "change" && args.length >= 3) {
    writeCheckedAgainstShapes(() => args.slice(2), () => recordChanges(args.slice(2), args[1], args[0]), "The changed records");
    console.log(`Recorded changes to ${args.length - 2} records.`);
  } else if (command === "reshard" && !args.length) {
    console.log(`Placed ${reshardStore()} records in their shard files.`);
  } else {
    console.error(usage);
    process.exit(1);
  }
}
