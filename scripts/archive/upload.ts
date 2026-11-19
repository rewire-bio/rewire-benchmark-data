/** The Cloudflare R2 upload path.
 *
 * The credential reader and the signature live in ./r2, because ./pull needs
 * the same two and a pull is not an upload. They are re-exported here so that
 * the path a reader comes to them by is still this file.
 *
 * It reads its four values from the environment inside the function, never at
 * import time, and fails with a clear message when they are absent.
 *
 * This path takes every cached object the manifest lists, at every tier but
 * one, because the bucket is the archive rather than one of two places the
 * archive might be.
 *
 * It did select on visibility, from 2026-11-17 to 2026-11-19: restricted
 * bytes went to R2 and public bytes went to a release tag, and `store` named
 * whichever had last been written to. That read as symmetry and was a split.
 * 871 objects recorded a release tag as their only home and 296 recorded the
 * bucket, so no single backend held the archive, restoring it meant reading
 * two of them, and which one held a given object was a licence question
 * rather than a storage one. Determination 5 chose R2 for the bytes it was
 * hardest to put anywhere else; it did not say the public bytes should live
 * somewhere different.
 *
 * So: R2 is the home of every object. ./publish still puts the public subset
 * on a release tag, and those copies are now recorded as mirrors, which is
 * what they are. A mirror can be deleted and rebuilt from the bucket. The
 * home cannot.
 *
 * A removed row never goes back, and that is the one refusal left.
 * assertStorable() tests t5-no-store by name and first, so a takedown holds
 * whatever a row's tier or visibility says and whatever order the commands
 * run in.
 */
import fs from "node:fs";
import { archiveAssetName, cacheContents, objectPath } from "./objects";
import { readManifest, markHome } from "./manifest";
import { readSettings, signRequest, type R2Settings } from "./r2";
import { isRemoved, type ManifestRow } from "../../shared/archive/schema";

export { readSettings, signRequest, VARIABLES, type R2Settings } from "./r2";

export interface UploadSummary {
  considered: number;
  uploaded: number;
  skipped: number;
  /** Rows at t5-no-store. Their bytes are gone and never go back. */
  removed: number;
  failed: { key: string; status: number }[];
  /** Rows whose manifest line now records the bucket as the home. A row that
   * still says local-cache after an upload is a row whose only recorded home is a
   * directory on one laptop, which is the thing the bucket exists to end. */
  marked: number;
}

/** The gate, and the only path to a PUT.
 *
 * One refusal, tested by name rather than through the tier's visibility, so
 * that it holds however the tiers are later rearranged. */
export function assertStorable(row: ManifestRow): void {
  if (row.archive_tier === "t5-no-store")
    throw new Error(
      `Refusing to upload ${row.sha256}: it is at t5-no-store` +
        `${isRemoved(row) ? `, removed at ${row.removed_at}` : ""}, so its bytes were taken down and never go back.`,
    );
}

/** Put every cached object the manifest lists into the bucket, keyed exactly
 * as the manifest keys it. Append only: an object already there is left
 * alone, which is what makes a second run cost nothing. */
export async function uploadObjects(options: { root?: string; dryRun?: boolean; env?: NodeJS.ProcessEnv } = {}): Promise<UploadSummary> {
  const root = options.root ?? ".";
  const settings = readSettings(options.env ?? process.env);
  const manifest = readManifest(root);
  const cached = new Set(cacheContents(root).keys);
  const summary: UploadSummary = { considered: 0, uploaded: 0, skipped: 0, removed: 0, failed: [], marked: 0 };
  for (const key of [...manifest.keys()].sort()) {
    const row = manifest.get(key)!;
    // Counted over the manifest, not over the cache, so the refusal says what
    // the manifest holds rather than what this machine happens to have.
    if (row.archive_tier === "t5-no-store") {
      summary.removed += 1;
      continue;
    }
    if (!cached.has(key)) continue;
    assertStorable(row);
    summary.considered += 1;
    const name = archiveAssetName(key);
    if (options.dryRun) {
      summary.skipped += 1;
      continue;
    }
    const body = fs.readFileSync(objectPath(key, root));
    const head = signRequest(settings, "HEAD", name, Buffer.alloc(0));
    const existing = await fetch(head.url, { method: "HEAD", headers: head.headers });
    if (existing.status === 200) {
      summary.skipped += 1;
      continue;
    }
    const put = signRequest(settings, "PUT", name, body);
    const response = await fetch(put.url, { method: "PUT", headers: put.headers, body });
    if (response.ok) {
      summary.uploaded += 1;
      // The bucket becomes the home. A release tag that was this row's only
      // recorded home becomes a mirror of it rather than being forgotten: the
      // asset is still there, and a reader who had been told to look at it is
      // not told it has gone.
      if (await markHome(key, "r2", root)) summary.marked += 1;
    } else summary.failed.push({ key, status: response.status });
  }
  return summary;
}
