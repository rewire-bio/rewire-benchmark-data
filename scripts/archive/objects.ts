/** The content-addressed object store.
 *
 * An object is keyed on the sha256 of its expanded bytes, which is the key
 * ADR 0004 defines and the hash a later claim cites a span in. Bytes live
 * gzipped in a local cache that git ignores; the manifest that enters git is
 * text only and lists one line per object.
 *
 * Gzip output is not byte-stable across zlib versions, so a cached object is
 * verified by expanding it and checking the expanded bytes, through the same
 * expand() the release files use.
 */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import zlib from "node:zlib";
import { expand, safePath, repository } from "../release/files";
import { objectShard } from "../../shared/archive/schema";

/** The gitignored cache. Overridable for a test or a run outside the tree. */
export const cacheRoot = (root = "."): string => process.env.ARCHIVE_CACHE ?? path.join(root, "data/archive/cache");

export const sha256 = (bytes: Buffer): string => crypto.createHash("sha256").update(bytes).digest("hex");

/** The cached file for a key: two-digit fan-out, then the key, gzipped. */
export function objectPath(key: string, root = "."): string {
  if (!/^[a-f0-9]{64}$/.test(key)) throw new Error(`Not a sha256 key: ${key}`);
  return path.join(cacheRoot(root), key.slice(0, 2), `${key}.gz`);
}

/** The release asset an object is published as. Keys never carry .gz in the
 * manifest; the asset name appends it, as assetName() does for release files. */
export const archiveAssetName = (key: string): string => {
  if (!/^[a-f0-9]{64}$/.test(key)) throw new Error(`Not a sha256 key: ${key}`);
  return `${key}.gz`;
};

/** ADR 0004's sibling of assetUrl(): the tag is archive/objects-<shard>, which
 * the release RELEASE_ID pattern rejects, so this cannot reuse assetUrl(). */
export function archiveAssetUrl(shard: string, name: string): string {
  if (!/^[0-9a-f]$/.test(shard)) throw new Error(`Not a manifest shard: ${shard}`);
  if (!safePath(name) || name.includes("/")) throw new Error(`Unsafe archive asset name: ${name}`);
  return `https://github.com/${repository}/releases/download/archive/objects-${shard}/${name}`;
}

/** Whether the cache holds the key, with its bytes verified against it. */
export function hasObject(key: string, root = "."): boolean {
  const file = objectPath(key, root);
  if (!fs.existsSync(file)) return false;
  try {
    expand(fs.readFileSync(file), key, file);
    return true;
  } catch {
    return false;
  }
}

/** The expanded bytes of a cached object, verified. Throws when absent. */
export function readObject(key: string, root = "."): Buffer {
  const file = objectPath(key, root);
  return expand(fs.readFileSync(file), key, file);
}

/** Put bytes in the cache under their own key. Returns the key and whether the
 * write was new, so a second run can report that it wrote nothing. Writing is
 * atomic: a temporary file in the same directory, then a rename, so an
 * interrupted run never leaves a half object behind. */
export function putObject(bytes: Buffer, root = "."): { key: string; bytes: number; written: boolean } {
  const key = sha256(bytes);
  const file = objectPath(key, root);
  if (hasObject(key, root)) return { key, bytes: bytes.length, written: false };
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temporary = `${file}.${process.pid}.${crypto.randomBytes(6).toString("hex")}.tmp`;
  fs.writeFileSync(temporary, zlib.gzipSync(bytes, { level: 9 }));
  fs.renameSync(temporary, file);
  return { key, bytes: bytes.length, written: true };
}

/** Move a file already on disk into the cache under its key, without holding
 * the whole thing in memory twice. Used by the fetcher, which streams a body
 * to a temporary file while hashing it. */
export function adoptFile(file: string, key: string, root = "."): { key: string; written: boolean } {
  const destination = objectPath(key, root);
  if (hasObject(key, root)) {
    fs.rmSync(file, { force: true });
    return { key, written: false };
  }
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  const temporary = `${destination}.${process.pid}.${crypto.randomBytes(6).toString("hex")}.tmp`;
  fs.writeFileSync(temporary, zlib.gzipSync(fs.readFileSync(file), { level: 9 }));
  fs.renameSync(temporary, destination);
  fs.rmSync(file, { force: true });
  return { key, written: true };
}

/** Every key the cache holds, and the bytes those gzip files occupy. */
export function cacheContents(root = "."): { keys: string[]; compressed_bytes: number } {
  const base = cacheRoot(root);
  const keys: string[] = [];
  let compressed = 0;
  if (!fs.existsSync(base)) return { keys, compressed_bytes: 0 };
  for (const folder of fs.readdirSync(base).sort()) {
    const directory = path.join(base, folder);
    if (!fs.statSync(directory).isDirectory()) continue;
    for (const name of fs.readdirSync(directory).sort()) {
      const match = /^([a-f0-9]{64})\.gz$/.exec(name);
      if (!match) continue;
      keys.push(match[1]);
      compressed += fs.statSync(path.join(directory, name)).size;
    }
  }
  return { keys, compressed_bytes: compressed };
}

export { objectShard };
