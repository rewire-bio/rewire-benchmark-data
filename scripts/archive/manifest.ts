/** The committed manifest: one line per stored object, text only.
 *
 * data/archive/objects/<0-f>.jsonl, sharded on the first hex digit of the key
 * and sorted by key, as ADR 0004 defines. A shard file is created only when it
 * has a row, so a tree with nothing stored commits no shards.
 *
 * Every write rewrites one shard through a temporary file and a rename, and
 * all writes go through one queue, so four fetch workers cannot interleave on
 * the same shard and an interrupted run leaves either the old shard or the new
 * one.
 */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import {
  canonicalLine,
  manifestRowSchema,
  objectShard,
  objectShards,
  visibilityOf,
  type Exposure,
  type ManifestRow,
  type ArchiveTier,
} from "../../shared/archive/schema";

export const manifestDir = (root = "."): string => path.join(root, "data/archive/objects");
export const shardPath = (shard: string, root = "."): string => {
  if (!/^[0-9a-f]$/.test(shard)) throw new Error(`Not a manifest shard: ${shard}`);
  return path.join(manifestDir(root), `${shard}.jsonl`);
};

const byKey = (a: ManifestRow, b: ManifestRow) => (a.sha256 < b.sha256 ? -1 : a.sha256 > b.sha256 ? 1 : 0);

/** One shard's rows, in file order. A missing shard is an empty shard. */
export function readShard(shard: string, root = "."): ManifestRow[] {
  const file = shardPath(shard, root);
  if (!fs.existsSync(file)) return [];
  return fs
    .readFileSync(file, "utf8")
    .split("\n")
    .filter((line) => line.trim())
    .map((line, index) => {
      const parsed = manifestRowSchema.safeParse(JSON.parse(line));
      if (!parsed.success) throw new Error(`data/archive/objects/${shard}.jsonl line ${index + 1}: ${parsed.error.issues[0].message}`);
      return parsed.data;
    });
}

/** The whole manifest, keyed on sha256. */
export function readManifest(root = "."): Map<string, ManifestRow> {
  const rows = new Map<string, ManifestRow>();
  for (const shard of objectShards) for (const row of readShard(shard, root)) rows.set(row.sha256, row);
  return rows;
}

function writeShard(shard: string, rows: ManifestRow[], root = "."): void {
  const file = shardPath(shard, root);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const body = rows
    .slice()
    .sort(byKey)
    .map((row) => canonicalLine(row as unknown as Record<string, unknown>))
    .join("\n");
  const temporary = `${file}.${process.pid}.${crypto.randomBytes(6).toString("hex")}.tmp`;
  fs.writeFileSync(temporary, body ? `${body}\n` : "");
  fs.renameSync(temporary, file);
}

let queue: Promise<unknown> = Promise.resolve();
/** Run a shard write after every write queued before it. */
function serialise<T>(work: () => T): Promise<T> {
  const next = queue.then(work, work);
  queue = next.catch(() => undefined);
  return next;
}

/** Add a row, or widen an existing row's source_ids. The bytes decide the row,
 * so a second fetch of the same object changes nothing and reports false. */
export function upsertRow(row: ManifestRow, root = "."): Promise<{ added: boolean; changed: boolean }> {
  manifestRowSchema.parse(row);
  const shard = objectShard(row.sha256);
  return serialise(() => {
    const rows = readShard(shard, root);
    const existing = rows.findIndex((candidate) => candidate.sha256 === row.sha256);
    if (existing < 0) {
      writeShard(shard, [...rows, row], root);
      return { added: true, changed: true };
    }
    const merged = [...new Set([...rows[existing].source_ids, ...row.source_ids])].sort();
    if (merged.length === rows[existing].source_ids.length) return { added: false, changed: false };
    rows[existing] = manifestRowSchema.parse({ ...rows[existing], source_ids: merged });
    writeShard(shard, rows, root);
    return { added: false, changed: true };
  });
}

/** Change an object's licence columns in place. This is the one write the
 * licence work makes: a determination moves a tier, visibility follows the
 * tier, and no bytes are fetched again. Returns false when the key is not in
 * the manifest. */
export function updateRow(
  sha256: string,
  patch: { archive_tier: ArchiveTier; observed_licence?: string | null; exposure?: Exposure },
  root = ".",
): Promise<boolean> {
  const shard = objectShard(sha256);
  return serialise(() => {
    const rows = readShard(shard, root);
    const index = rows.findIndex((row) => row.sha256 === sha256);
    if (index < 0) return false;
    rows[index] = manifestRowSchema.parse({
      ...rows[index],
      archive_tier: patch.archive_tier,
      visibility: visibilityOf(patch.archive_tier),
      observed_licence: patch.observed_licence ?? rows[index].observed_licence,
      exposure: patch.exposure ?? rows[index].exposure,
    });
    writeShard(shard, rows, root);
    return true;
  });
}

/** Structural checks, offline and credential free: every row parses, sits in
 * the shard its key names, and each shard is sorted with no duplicate key. */
export function checkManifest(root = "."): { rows: number; problems: string[] } {
  const problems: string[] = [];
  let count = 0;
  for (const shard of objectShards) {
    let rows: ManifestRow[];
    try {
      rows = readShard(shard, root);
    } catch (error) {
      problems.push((error as Error).message);
      continue;
    }
    const seen = new Set<string>();
    let previous = "";
    for (const row of rows) {
      count += 1;
      if (objectShard(row.sha256) !== shard) problems.push(`${row.sha256} is in shard ${shard}, not ${objectShard(row.sha256)}`);
      if (seen.has(row.sha256)) problems.push(`${row.sha256} appears twice in shard ${shard}`);
      if (row.sha256 < previous) problems.push(`shard ${shard} is not sorted at ${row.sha256}`);
      seen.add(row.sha256);
      previous = row.sha256;
    }
  }
  return { rows: count, problems };
}
