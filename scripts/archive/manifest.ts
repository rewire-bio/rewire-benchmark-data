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
  isRemoved,
  manifestRowSchema,
  objectShard,
  objectShards,
  utcNow,
  visibilityOf,
  type Exposure,
  type ManifestRow,
  type ArchiveTier,
  type Store,
} from "../../shared/archive/schema";
import { cacheContents, hasObject, readObject } from "./objects";

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
 * the manifest.
 *
 * observed_licence left out keeps the string the row carries. Passing null
 * clears it, which is what a reading that rests on no licence string has to
 * be able to say: leaving a superseded string beside a new tier would make
 * the row name a determination it no longer carries. The two cases are told
 * apart by the key being present, not by the value. */
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
      observed_licence: "observed_licence" in patch ? (patch.observed_licence ?? null) : rows[index].observed_licence,
      exposure: patch.exposure ?? rows[index].exposure,
    });
    writeShard(shard, rows, root);
    return true;
  });
}

/** Record which backend is an object's home, keeping the old home as a mirror.
 *
 * The bytes are already in the new backend when this is called; this is the
 * record of it. A home that is being replaced had a copy of the bytes a
 * moment ago and still does, so it becomes a mirror rather than disappearing:
 * a reader holding the old location finds it still named. The one home never
 * demoted is local-cache, which is a gitignored directory on whichever
 * machine ran the command and is not somewhere another reader can look.
 *
 * Nothing else on the row moves, and the licence columns in particular are not
 * touched. Returns false when the key is not in the manifest. */
export function markHome(sha256: string, store: Store, root = "."): Promise<boolean> {
  const shard = objectShard(sha256);
  return serialise(() => {
    const rows = readShard(shard, root);
    const index = rows.findIndex((row) => row.sha256 === sha256);
    if (index < 0) return false;
    const row = rows[index];
    // Already the home, so nothing is written and nothing is counted. The caller's tally is of
    // rows this moved, not of rows it looked at.
    if (row.store === store) return false;
    const mirrors = [...new Set([...row.mirrors, ...(row.store === "local-cache" ? [] : [row.store])])]
      .filter((named) => named !== store)
      .sort();
    rows[index] = manifestRowSchema.parse({ ...row, store, mirrors });
    writeShard(shard, rows, root);
    return true;
  });
}

/** Record that a backend holds a second copy of an object whose home is
 * elsewhere. This is the one write the publish work makes: a release asset is
 * a copy of bytes the bucket already holds, and recording it as the home
 * would be claiming the archive had moved onto a public tag. Returns false when the key is not
 * in the manifest, and false when the row already records this backend. */
export function markMirror(sha256: string, store: Store, root = "."): Promise<boolean> {
  const shard = objectShard(sha256);
  return serialise(() => {
    const rows = readShard(shard, root);
    const index = rows.findIndex((row) => row.sha256 === sha256);
    if (index < 0) return false;
    const row = rows[index];
    // Already recorded, either as the home or as a mirror, so nothing is written.
    if (row.store === store || row.mirrors.includes(store)) return false;
    rows[index] = manifestRowSchema.parse({ ...row, mirrors: [...row.mirrors, store].sort() });
    writeShard(shard, rows, root);
    return true;
  });
}

/** Record a takedown on a row whose bytes have gone, or are going.
 *
 * This is the one write the takedown path makes. It moves the row to
 * t5-no-store, so visibility follows to restricted and no publish path selects
 * it again, and it records when, why and at whose request. Everything that
 * makes the removal checkable stays: the key, the byte count, the media type,
 * the origin, first_seen_at and source_ids. Mirrors go, because the row keeps no copy.
 * Returns false when the key is not in the manifest.
 *
 * It rewrites one shard, so it waits for a running fetch like every other
 * manifest write. */
export function markRemoved(
  sha256: string,
  removal: { removed_at?: string; removed_reason: string; removed_requester: string },
  root = ".",
): Promise<boolean> {
  const shard = objectShard(sha256);
  return serialise(() => {
    const rows = readShard(shard, root);
    const index = rows.findIndex((row) => row.sha256 === sha256);
    if (index < 0) return false;
    rows[index] = manifestRowSchema.parse({
      ...rows[index],
      archive_tier: "t5-no-store",
      visibility: visibilityOf("t5-no-store"),
      // A removed row keeps no copy, so it names no mirror. Without this a takedown of an
      // object that had been published threw on its own schema rule, and a takedown has to
      // work whatever else a row says.
      mirrors: [],
      removed_at: removal.removed_at ?? utcNow(),
      removed_reason: removal.removed_reason,
      removed_requester: removal.removed_requester,
    });
    writeShard(shard, rows, root);
    return true;
  });
}

export interface Verification {
  objects: number;
  verified: number;
  removed: string[];
  missing: string[];
  corrupt: string[];
  unlisted: string[];
  problems: string[];
}

/** Recompute every cached object against the manifest. Offline, credential
 * free and read only, and what `npm run archive -- verify` reports.
 *
 * A row at t5-no-store is expected to hold no bytes, so it is counted as
 * removed rather than missing and the command stays green after a takedown.
 * The check runs the other way instead: bytes still in the cache under a
 * removed row mean the takedown stopped halfway, and that is a problem. */
export function verifyObjects(root = "."): Verification {
  const { problems } = checkManifest(root);
  const manifest = readManifest(root);
  const removed: string[] = [];
  const missing: string[] = [];
  const corrupt: string[] = [];
  let verified = 0;
  for (const [key, row] of manifest) {
    const held = hasObject(key, root);
    if (row.archive_tier === "t5-no-store") {
      const when = isRemoved(row) ? `, removed at ${row.removed_at}` : "";
      if (held) problems.push(`${key} is at t5-no-store${when} and its bytes are still in the cache`);
      else removed.push(key);
      continue;
    }
    if (!held) {
      missing.push(key);
      continue;
    }
    try {
      const bytes = readObject(key, root);
      if (bytes.length !== row.bytes) corrupt.push(key);
      else verified += 1;
    } catch {
      corrupt.push(key);
    }
  }
  const unlisted = cacheContents(root).keys.filter((key) => !manifest.has(key));
  return { objects: manifest.size, verified, removed, missing, corrupt, unlisted, problems };
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
