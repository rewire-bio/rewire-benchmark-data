/** Ask once, ever.
 *
 * The same table asked twice costs money twice and can answer twice, which would mean a rerun
 * of the command changes the batch for no reason anyone could point at. The cache makes a
 * rerun free and reproducible: a second run over the same archive, the same store and the same
 * prompt reads every answer back and asks nothing.
 *
 * The key is the layer hash and the table's span in it, which is what ADR 0002's span
 * substrate already calls a place in a source, plus the three things that would make the same
 * place a different question: the prompt's hash, the shortlist it was given and the model
 * identifier. Keying on the place alone would serve a stale answer after a prompt edit, and
 * the receipt would then name a prompt that never produced it.
 *
 * The file is canonical JSON with keys sorted at every depth, so two runs write the same bytes
 * and a diff means an answer changed.
 */
import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";
import { canonicalJson } from "../../../archive/layers/grid/index";
import type { LabelReply } from "./transport";

export interface CacheKeyInput {
  layer_sha256: string;
  /** The code point range the table's own cells occupy in that layer. */
  extent: { start: number; end: number };
  prompt_sha256: string;
  /** The ids the question printed, in the order it printed them. */
  shortlist: string[];
  model: string;
}

export const cacheKey = (input: CacheKeyInput): string =>
  createHash("sha256")
    .update(
      canonicalJson({
        layer_sha256: input.layer_sha256,
        extent: input.extent,
        prompt_sha256: input.prompt_sha256,
        shortlist: input.shortlist,
        model: input.model,
      }),
    )
    .digest("hex");

export interface CacheEntry {
  /** What the key stands for, written out so the file is readable without recomputing it. */
  asked: CacheKeyInput & { table_id: string; source_id: string };
  reply: LabelReply;
}

export interface LabelCache {
  get(key: string): CacheEntry | undefined;
  set(key: string, entry: CacheEntry): void;
  /** How many answers were read back rather than asked for, over this cache's life. */
  readonly hits: number;
  readonly entries: number;
  /** Canonical JSON for the file, or null where nothing was ever stored. */
  serialise(): string | null;
}

/** A cache over a plain object, which is what the file holds. */
export function labelCache(held: Record<string, CacheEntry> = {}): LabelCache {
  const store: Record<string, CacheEntry> = { ...held };
  let hits = 0;
  return {
    get(key) {
      const entry = store[key];
      if (entry) hits += 1;
      return entry;
    },
    set(key, entry) {
      store[key] = entry;
    },
    get hits() {
      return hits;
    },
    get entries() {
      return Object.keys(store).length;
    },
    serialise() {
      return Object.keys(store).length === 0 ? null : `${canonicalJson(store)}\n`;
    },
  };
}

/** Read a cache file, or an empty cache where there is none. A file that will not parse is an
 * error: a cache that silently starts empty would ask every question again and bill for it. */
export function readCache(file: string): LabelCache {
  if (!fs.existsSync(file)) return labelCache();
  const text = fs.readFileSync(file, "utf8");
  if (text.trim() === "") return labelCache();
  try {
    return labelCache(JSON.parse(text) as Record<string, CacheEntry>);
  } catch (error) {
    throw new Error(`The label cache at ${file} will not parse, so a rerun would ask every question again: ${(error as Error).message}`);
  }
}

/** Write the cache, where it holds anything. */
export function writeCache(file: string, cache: LabelCache): void {
  const body = cache.serialise();
  if (body === null) return;
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, body);
}
