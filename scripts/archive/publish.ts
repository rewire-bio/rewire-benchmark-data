/** The GitHub release asset publish path.
 *
 * The sibling of ./upload.ts that works today. upload.ts needs four Cloudflare
 * R2 secrets that do not exist in this environment; this needs no new
 * credential at all. A release asset of this repository is written with the
 * repository's own token, which is what the gh CLI already holds locally and
 * what github.token already grants in CI, so the archive stops living only on
 * one laptop without anybody creating a secret first.
 *
 * ADR 0004 sets the layout. An object is published as the asset
 * <sha256>.gz on the tag archive/objects-<first hex digit of the key>, so the
 * tag shard is the manifest shard and a reader finds the tag from the hash
 * with no lookup. archiveAssetUrl() in ./objects builds that URL and nothing
 * here invents a second one.
 *
 * Release assets are public, so visibility is the whole safety property of
 * this command. assertPublishable() is the only path to an upload and it
 * refuses anything the manifest does not call public. Selection filters the
 * restricted rows out and counts them; a restricted row that reaches the gate
 * throws with its sha256 and its tier, because that would mean a bug upstream
 * rather than an ordinary private object.
 *
 * Publishing and recording are two steps on purpose. The uploader reads the
 * release listing and never touches git. Marking a row writes a manifest
 * shard, and a fetch that is still running owns those shards, so --no-mark
 * leaves the recording for a later run. A later run uploads nothing, because
 * an asset already on the tag is skipped, and marks what it finds.
 */
import fs from "node:fs";
import { execFileSync } from "node:child_process";
import { archiveAssetName, archiveAssetUrl, hasObject, objectPath } from "./objects";
import { readManifest, markMirror } from "./manifest";
import { repository } from "../release/files";
import { objectShard, visibilityOf, type ManifestRow } from "../../shared/archive/schema";

/** The tag a key's bytes are published on: ADR 0004's archive/objects-<shard>. */
export const archiveTag = (shard: string): string => {
  if (!/^[0-9a-f]$/.test(shard)) throw new Error(`Not a manifest shard: ${shard}`);
  return `archive/objects-${shard}`;
};

/** What the publisher needs of GitHub. Injected so a test never calls gh.
 * assets() returns null for a release that does not exist, which is a
 * different fact from a release with no assets. */
export interface ReleaseClient {
  assets(tag: string): string[] | null;
  create(tag: string, title: string, notes: string): void;
  upload(tag: string, file: string): void;
}

const gh = (...args: string[]): string =>
  execFileSync("gh", args, { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"], maxBuffer: 64 * 1024 ** 2 });

/** The notes a shard tag carries. They say what an asset is and where the row
 * describing it lives, so a reader who finds one object can check it. */
export const shardNotes = (shard: string): string =>
  [
    `Archive objects whose sha256 begins with ${shard}.`,
    "",
    "Each asset is named <sha256>.gz and holds the gzip of the exact bytes of one",
    "primary source. Expand it and check the sha256 against the asset name.",
    "",
    `The row for every asset here is in data/archive/objects/${shard}.jsonl: the media type,`,
    "the byte count, the URL the bytes came from, the licence tier they are published under",
    "and the source records they answer for.",
    "",
    "Only objects at a licence tier that permits publication are here. See",
    "docs/source-preservation.md, which also carries the takedown contact.",
  ].join("\n");

/** The default client. Separates a release that is not there from a gh call
 * that failed, so an authentication error never reads as a missing release
 * and never produces a create attempt. */
export function ghClient(repo = repository): ReleaseClient {
  return {
    assets(tag) {
      try {
        const listing = JSON.parse(gh("release", "view", tag, "--repo", repo, "--json", "assets"));
        return (listing.assets as { name: string }[]).map((asset) => asset.name);
      } catch (error) {
        const output = `${(error as { stderr?: string }).stderr ?? ""}${(error as Error).message ?? ""}`;
        if (/release not found/i.test(output)) return null;
        throw new Error(`gh release view ${tag} failed: ${output.trim()}`);
      }
    },
    create(tag, title, notes) {
      // --latest=false keeps a shard tag out of the repository's Latest
      // release, which the knowledge graph and serving releases own.
      gh(
        "release",
        "create",
        tag,
        "--repo",
        repo,
        "--latest=false",
        ...(process.env.RELEASE_TARGET_SHA ? ["--target", process.env.RELEASE_TARGET_SHA] : []),
        "--title",
        title,
        "--notes",
        notes,
      );
    },
    upload(tag, file) {
      // Never --clobber. An asset already on the tag is skipped by name before
      // this is called, and replacing published bytes is not a thing this does.
      gh("release", "upload", tag, "--repo", repo, file);
    },
  };
}

/** The gate. The only path to an upload, and the reason this command is safe
 * to point at a public repository. */
export function assertPublishable(row: ManifestRow): void {
  if (row.visibility !== "public" || visibilityOf(row.archive_tier) !== "public")
    throw new Error(
      `Refusing to publish ${row.sha256}: tier ${row.archive_tier} is ${visibilityOf(row.archive_tier)}, ` +
        "and only a public object may become a release asset.",
    );
}

export interface PublishCandidate {
  key: string;
  shard: string;
  tag: string;
  name: string;
  url: string;
  bytes: number;
  compressed_bytes: number;
  archive_tier: string;
  row: ManifestRow;
}

export interface PublishPlan {
  manifest_rows: number;
  public_rows: number;
  public_by_tier: Record<string, number>;
  public_bytes: number;
  public_compressed_bytes: number;
  refused: number;
  refused_by_tier: Record<string, number>;
  public_not_in_cache: number;
  candidates: PublishCandidate[];
  by_tag: Record<string, number>;
}

const compressedBytes = (key: string, root: string): number => {
  try {
    return fs.statSync(objectPath(key, root)).size;
  } catch {
    return 0;
  }
};

/** What a run would consider, read off the manifest and the cache. No network
 * and no writes, so the dry run and the real run select identically.
 *
 * A public row whose bytes the cache does not hold, or holds corrupt, is
 * counted and left out: hasObject() expands the file and checks it against the
 * key, so bytes that no longer hash to their name are never uploaded. */
export function planPublish(options: { root?: string; limit?: number } = {}): PublishPlan {
  const root = options.root ?? ".";
  const manifest = readManifest(root);
  const publicByTier: Record<string, number> = {};
  const refusedByTier: Record<string, number> = {};
  const cached: PublishCandidate[] = [];
  let publicRows = 0;
  let publicBytes = 0;
  let publicCompressed = 0;
  let refused = 0;
  let notInCache = 0;
  for (const key of [...manifest.keys()].sort()) {
    const row = manifest.get(key)!;
    if (row.visibility !== "public") {
      refused += 1;
      refusedByTier[row.archive_tier] = (refusedByTier[row.archive_tier] ?? 0) + 1;
      continue;
    }
    publicRows += 1;
    publicByTier[row.archive_tier] = (publicByTier[row.archive_tier] ?? 0) + 1;
    publicBytes += row.bytes;
    if (!hasObject(key, root)) {
      notInCache += 1;
      continue;
    }
    const shard = objectShard(key);
    const name = archiveAssetName(key);
    const compressed = compressedBytes(key, root);
    publicCompressed += compressed;
    cached.push({
      key,
      shard,
      tag: archiveTag(shard),
      name,
      url: archiveAssetUrl(shard, name),
      bytes: row.bytes,
      compressed_bytes: compressed,
      archive_tier: row.archive_tier,
      row,
    });
  }
  const candidates = options.limit === undefined ? cached : cached.slice(0, options.limit);
  const byTag: Record<string, number> = {};
  for (const candidate of candidates) byTag[candidate.tag] = (byTag[candidate.tag] ?? 0) + 1;
  return {
    manifest_rows: manifest.size,
    public_rows: publicRows,
    public_by_tier: publicByTier,
    public_bytes: publicBytes,
    public_compressed_bytes: publicCompressed,
    refused,
    refused_by_tier: refusedByTier,
    public_not_in_cache: notInCache,
    candidates,
    by_tag: byTag,
  };
}

export interface PublishSummary {
  dry_run: boolean;
  manifest_rows: number;
  public_rows: number;
  public_by_tier: Record<string, number>;
  public_bytes: number;
  public_compressed_bytes: number;
  refused: number;
  refused_by_tier: Record<string, number>;
  public_not_in_cache: number;
  considered: number;
  uploaded: number;
  already_present: number;
  failed: { key: string; message: string }[];
  tags_created: string[];
  tags_present: string[];
  marked: number;
  urls: string[];
}

/** Publish every public cached object the manifest lists that the tag does not
 * already hold, and record where it went.
 *
 * Idempotent on the asset name. The name is the key, so a name already on the
 * tag is those exact bytes and there is nothing to send. The bytes are not
 * downloaded and compared: gzip output is not stable across zlib versions, so
 * comparing the compressed asset would fail on objects that are correct.
 *
 * urls holds what a dry run would publish, or what a real run did publish. An
 * object that was already an asset, or whose upload failed, is not in it.
 */
export async function publishObjects(
  options: {
    root?: string;
    limit?: number;
    dryRun?: boolean;
    mark?: boolean;
    client?: ReleaseClient;
    log?: (line: string) => void;
  } = {},
): Promise<PublishSummary> {
  const root = options.root ?? ".";
  const dryRun = options.dryRun ?? false;
  const mark = options.mark ?? true;
  const client = options.client ?? ghClient();
  const log = options.log ?? (() => undefined);
  const plan = planPublish({ root, limit: options.limit });
  const summary: PublishSummary = {
    dry_run: dryRun,
    manifest_rows: plan.manifest_rows,
    public_rows: plan.public_rows,
    public_by_tier: plan.public_by_tier,
    public_bytes: plan.public_bytes,
    public_compressed_bytes: plan.public_compressed_bytes,
    refused: plan.refused,
    refused_by_tier: plan.refused_by_tier,
    public_not_in_cache: plan.public_not_in_cache,
    considered: plan.candidates.length,
    uploaded: 0,
    already_present: 0,
    failed: [],
    tags_created: [],
    tags_present: [],
    marked: 0,
    urls: [],
  };

  // One listing per tag, read once. A dry run reads them too, so it reports
  // what exists rather than guessing.
  const listings = new Map<string, string[] | null>();
  for (const tag of Object.keys(plan.by_tag).sort()) {
    const assets = client.assets(tag);
    listings.set(tag, assets);
    if (assets === null) summary.tags_created.push(tag);
    else summary.tags_present.push(tag);
  }

  const published: PublishCandidate[] = [];
  for (const candidate of plan.candidates) {
    assertPublishable(candidate.row);
    const existing = listings.get(candidate.tag);
    if (existing && existing.includes(candidate.name)) {
      summary.already_present += 1;
      published.push(candidate);
      continue;
    }
    if (dryRun) {
      summary.urls.push(candidate.url);
      continue;
    }
    if (listings.get(candidate.tag) === null) {
      client.create(candidate.tag, `Archive objects ${candidate.shard}`, shardNotes(candidate.shard));
      listings.set(candidate.tag, []);
      log(`created ${candidate.tag}`);
    }
    try {
      client.upload(candidate.tag, objectPath(candidate.key, root));
      listings.set(candidate.tag, [...(listings.get(candidate.tag) ?? []), candidate.name]);
      summary.uploaded += 1;
      summary.urls.push(candidate.url);
      published.push(candidate);
      log(`uploaded ${candidate.name} to ${candidate.tag}`);
    } catch (error) {
      summary.failed.push({ key: candidate.key, message: (error as Error).message.trim() });
    }
  }
  if (dryRun) {
    // A dry run creates nothing, so the tags it names as absent stay absent.
    return summary;
  }

  // The manifest mark is the second step. A release asset is a second copy of
  // bytes whose home is the bucket, so it is recorded as a mirror: with
  // archiveAssetUrl() that is the whole record of where this copy is, and no
  // reader is told the archive itself has moved onto a public tag.
  if (mark)
    for (const candidate of published) {
      if (candidate.row.mirrors.includes("github-release")) continue;
      if (await markMirror(candidate.key, "github-release", root)) summary.marked += 1;
    }
  return summary;
}
