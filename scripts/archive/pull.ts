/** The Cloudflare R2 download path: the inverse of ./upload.
 *
 * Why it exists. The object cache at data/archive/cache is gitignored by
 * design, so every figure this lane has published was measured on one laptop
 * and nobody else could recompute one. That is the failing the papers this
 * store describes are criticised for, and it was ours. With the objects in
 * R2 a runner can rebuild the cache from the committed manifest and a
 * credential, and a measurement becomes something a second machine can
 * repeat.
 *
 * What it will not do.
 *
 * A row at t5-no-store is refused before any request, for the reason
 * assertStorable() gives on the way up: a rights holder asked for those
 * bytes to go, and a copy left in a bucket is not permission to bring them
 * back. The gate is here rather than left to the bucket's contents, so the
 * order of a takedown and a pull does not matter.
 *
 * A cached object that already verifies is never fetched and never written
 * over. hasObject() expands the file and checks the expanded bytes against
 * the key, so "already held" means held and correct, and a second run makes
 * no request at all.
 *
 * Bytes are checked before they are kept, against the key the committed
 * manifest names and the byte count the row states. The check is expand()
 * from the release lane, the same function the publish path verifies an
 * asset with. A reply that does not hash to its key is a named failure and
 * nothing is written: putObject() would otherwise have stored it happily
 * under the hash of whatever came back, and it would have surfaced days later
 * as an unlisted object.
 *
 * Where it differs from ./upload, and why. Upload refuses a public row,
 * because a public object is published as a release asset instead and sending
 * it to the restricted bucket would store the same bytes twice under two
 * rules. Pull applies no visibility gate. Nothing is disclosed by bringing
 * bytes down into a gitignored cache on a runner, and the held-out set this
 * was built for needs 53 public objects and 5 restricted ones: a visibility
 * gate here would refuse the larger half of the job for no gain. The split is
 * counted and reported, so the asymmetry is visible rather than assumed.
 */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { expand } from "../release/files";
import { archiveAssetName, archiveAssetUrl, hasObject, objectPath } from "./objects";
import { readManifest } from "./manifest";
import { readSettings, signRequest, platformFetch, type R2Fetch, type R2Settings } from "./r2";
import { objectShard, type ManifestRow } from "../../shared/archive/schema";

export interface PullOptions {
  root?: string;
  env?: NodeJS.ProcessEnv;
  /** Manifest keys to pull. Absent means every row the other filters leave. */
  keys?: string[];
  /** Pull the objects these source records cite, which is the filter a job
   * uses: it knows which sources it reads, not which bytes they are. */
  sources?: string[];
  /** A ceiling on the number of objects fetched in one run. The run is
   * resumable, so a limit is a way to take a large pull in stages. */
  limit?: number;
  /** Where the bytes come from. "r2" is the home and needs the credential.
   *
   * "release" reads the public release assets ./publish wrote, needs no
   * credential at all, and exists for the one job the bucket cannot serve:
   * filling a cache so those objects can be put *into* the bucket. The 871
   * objects whose only recorded home is a release tag are not in R2 yet, and
   * a runner has no cache, so without this an upload job would find nothing
   * to upload and report success. It selects only rows a release tag holds
   * and counts the rest rather than asking for them and collecting 404s. */
  from?: "r2" | "release";
  /** Report the selection and fetch nothing. Needs no credential. */
  dryRun?: boolean;
  fetch?: R2Fetch;
  log?: (line: string) => void;
}

export interface PullSummary {
  manifest_rows: number;
  /** Rows the filters left, before any refusal. */
  matched: number;
  /** Rows refused at t5-no-store. Their bytes were taken down and never go back. */
  removed: number;
  /** Rows selected to pull: matched, minus the removed. */
  selected: number;
  selected_restricted: number;
  selected_public: number;
  /** Already in the cache, verified against the key. Not fetched, not touched. */
  already_held: number;
  /** Rows the limit held back this run. A second run takes them. */
  held_back_by_limit: number;
  /** Pulling from the release assets, selected rows no release tag holds, split by whether
   * that matters. A row already homed in the bucket is simply not this path's business. A row
   * in neither place has exactly one copy, in the cache of whichever machine fetched it, and
   * nothing remote can rebuild it: that is the number worth reading. */
  already_in_the_bucket: number;
  no_remote_copy: number;
  downloaded: number;
  /** Expanded bytes of what was downloaded, and the bytes written to disk. */
  expanded_bytes: number;
  compressed_bytes: number;
  dry_run: boolean;
  failed: { key: string; status: number | null; message: string }[];
}

/** Whether a release tag holds this row's bytes: it is the row's home, or a
 * recorded mirror of it once the bucket has become the home. */
export const onARelease = (row: ManifestRow): boolean => row.store === "github-release" || row.mirrors.includes("github-release");

/** The rows the filters leave, sorted by key so two runs select in one order. */
export function selectRows(
  manifest: Map<string, ManifestRow>,
  filters: { keys?: string[]; sources?: string[] },
): ManifestRow[] {
  const keys = filters.keys?.length ? new Set(filters.keys) : null;
  const sources = filters.sources?.length ? new Set(filters.sources) : null;
  const rows: ManifestRow[] = [];
  for (const key of [...manifest.keys()].sort()) {
    const row = manifest.get(key)!;
    if (keys && !keys.has(key)) continue;
    if (sources && !row.source_ids.some((id) => sources.has(id))) continue;
    rows.push(row);
  }
  return rows;
}

/** Write the gzip file the bucket served, atomically, under the key it was
 * verified against.
 *
 * The received bytes are written rather than a re-compression of the expanded
 * ones: gzip output is not byte-stable across zlib versions, so recompressing
 * would put a file in the cache that differs from the one upload sent while
 * holding the same object. A temporary file in the same directory then a
 * rename means an interrupted run leaves no half object. */
function writeCompressed(key: string, compressed: Buffer, root: string): void {
  const file = objectPath(key, root);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temporary = `${file}.${process.pid}.${crypto.randomBytes(6).toString("hex")}.tmp`;
  fs.writeFileSync(temporary, compressed);
  fs.renameSync(temporary, file);
}

/** The body of a reply that is not a 200, for the message. R2 answers with an
 * XML error document, and a pull that printed only the status would leave the
 * operator guessing between a wrong bucket, a wrong key and an expired one. */
async function failureText(reply: { text(): Promise<string> }): Promise<string> {
  try {
    const body = (await reply.text()).trim().replace(/\s+/g, " ");
    return body.length > 300 ? `${body.slice(0, 300)}...` : body;
  } catch {
    return "no body";
  }
}

/**
 * Bring objects down into the local cache, verified, resumable and idempotent.
 *
 * Idempotent because the only thing that decides whether a request is made is
 * whether the cache already holds the key with bytes that verify. A second run
 * over the same filter makes no request and writes no file, which is what
 * makes it safe to put in front of every job that needs the cache.
 */
export async function pullObjects(options: PullOptions = {}): Promise<PullSummary> {
  const root = options.root ?? ".";
  const from = options.from ?? "r2";
  const log = options.log ?? (() => undefined);
  const manifest = readManifest(root);
  const matched = selectRows(manifest, { keys: options.keys, sources: options.sources });

  const summary: PullSummary = {
    manifest_rows: manifest.size,
    matched: matched.length,
    removed: 0,
    selected: 0,
    selected_restricted: 0,
    selected_public: 0,
    already_held: 0,
    held_back_by_limit: 0,
    already_in_the_bucket: 0,
    no_remote_copy: 0,
    downloaded: 0,
    expanded_bytes: 0,
    compressed_bytes: 0,
    dry_run: options.dryRun ?? false,
    failed: [],
  };

  const wanted: ManifestRow[] = [];
  for (const row of matched) {
    if (row.archive_tier === "t5-no-store") {
      summary.removed += 1;
      continue;
    }
    summary.selected += 1;
    if (row.visibility === "restricted") summary.selected_restricted += 1;
    else summary.selected_public += 1;
    if (hasObject(row.sha256, root)) {
      summary.already_held += 1;
      continue;
    }
    if (from === "release" && !onARelease(row)) {
      if (row.store === "r2" || row.mirrors.includes("r2")) summary.already_in_the_bucket += 1;
      else summary.no_remote_copy += 1;
      continue;
    }
    wanted.push(row);
  }

  const limit = options.limit ?? wanted.length;
  const take = wanted.slice(0, limit);
  summary.held_back_by_limit = wanted.length - take.length;

  if (summary.dry_run) {
    log(
      `dry run: ${take.length} objects would be fetched from the ${from === "r2" ? "bucket" : "release assets"}, ` +
        `${summary.already_held} are already held`,
    );
    return summary;
  }
  if (take.length === 0) {
    log(`nothing to fetch: ${summary.already_held} of ${summary.selected} selected objects are already held and verified`);
    return summary;
  }

  // Read at call time, and only once there is something to fetch, so a run
  // that finds the cache complete needs no credential at all. A release pull
  // needs none ever, because the assets are public.
  const settings: R2Settings | null = from === "r2" ? readSettings(options.env ?? process.env) : null;
  const send = options.fetch ?? platformFetch;

  for (const row of take) {
    const key = row.sha256;
    const name = archiveAssetName(key);
    const request = settings
      ? signRequest(settings, "GET", name, Buffer.alloc(0))
      : { url: archiveAssetUrl(objectShard(key), name), headers: {} as Record<string, string> };
    let reply;
    try {
      reply = await send(request.url, { method: "GET", headers: request.headers });
    } catch (error) {
      summary.failed.push({ key, status: null, message: (error as Error).message });
      continue;
    }
    if (reply.status !== 200) {
      summary.failed.push({ key, status: reply.status, message: await failureText(reply) });
      continue;
    }
    const compressed = Buffer.from(await reply.arrayBuffer());

    // Verified before anything is written, against the key the committed
    // manifest names and the byte count the row states. expand() throws on
    // either, and the key goes in the message.
    let expanded: Buffer;
    try {
      expanded = expand(compressed, key, `${from === "r2" ? "R2 object" : "release asset"} ${key}`, row.bytes);
    } catch (error) {
      summary.failed.push({ key, status: reply.status, message: (error as Error).message });
      continue;
    }

    writeCompressed(key, compressed, root);
    summary.downloaded += 1;
    summary.expanded_bytes += expanded.length;
    summary.compressed_bytes += compressed.length;
    if (summary.downloaded % 50 === 0) log(`  ${summary.downloaded} of ${take.length} objects`);
  }

  return summary;
}
