/** The Cloudflare R2 upload path.
 *
 * The credential reader and the signature live in ./r2, because ./pull needs
 * the same two and a pull is not an upload. They are re-exported here so that
 * the path a reader comes to them by is still this file.
 *
 * It reads its four values from the environment inside the function, never at
 * import time, and fails with a clear message when they are absent.
 *
 * This path selects the restricted rows and refuses everything else, which is
 * the mirror image of ./publish. It used to upload every cached object the
 * manifest listed. A private bucket made that no leak, but it left the two
 * backends asymmetric: publish filters, upload did not, so whoever wired R2
 * up had to know that the filter was missing on purpose. Two rules replace
 * that:
 *
 * R2 is the restricted backend. Determination 5 of 2026-11-17 puts restricted
 * bytes there, and a public object is published as a release asset by
 * ./publish instead, so a public row in this loop is a row in the wrong
 * command and is refused rather than silently sent twice.
 *
 * A removed row never goes back. t5-no-store is restricted, so a visibility
 * filter on its own would re-upload the bytes of an object a rights holder
 * asked us to remove if a copy were still cached anywhere. That is the trap
 * the old takedown step order worked around in prose. assertRestricted()
 * refuses it, so the order no longer matters.
 */
import fs from "node:fs";
import { archiveAssetName, cacheContents, objectPath } from "./objects";
import { readManifest, markStore } from "./manifest";
import { readSettings, signRequest, type R2Settings } from "./r2";
import { isRemoved, type ManifestRow } from "../../shared/archive/schema";

export { readSettings, signRequest, VARIABLES, type R2Settings } from "./r2";

export interface UploadSummary {
  considered: number;
  uploaded: number;
  skipped: number;
  /** Rows the manifest marks public. They belong on a release tag. */
  not_restricted: number;
  /** Rows at t5-no-store. Their bytes are gone and never go back. */
  removed: number;
  failed: { key: string; status: number }[];
  /** Rows whose manifest line now records that the bytes are in the bucket. A row that
   * still says local-cache after an upload is a row whose only recorded home is a
   * directory on one laptop, which is the thing the bucket exists to end. */
  marked: number;
}

/** The gate, the mirror of assertPublishable() in ./publish and the only path
 * to a PUT. */
export function assertRestricted(row: ManifestRow): void {
  if (row.archive_tier === "t5-no-store")
    throw new Error(
      `Refusing to upload ${row.sha256}: it is at t5-no-store` +
        `${isRemoved(row) ? `, removed at ${row.removed_at}` : ""}, so its bytes were taken down and never go back.`,
    );
  if (row.visibility !== "restricted")
    throw new Error(
      `Refusing to upload ${row.sha256}: tier ${row.archive_tier} is public, and a public object is published as a ` +
        "release asset by scripts/archive/publish.ts rather than put in the restricted bucket.",
    );
}

/** Put every restricted cached object the manifest lists into the bucket,
 * keyed exactly as the manifest keys it. Append only: an object already there
 * is left alone, which is what makes a second run cost nothing. */
export async function uploadObjects(options: { root?: string; dryRun?: boolean; env?: NodeJS.ProcessEnv } = {}): Promise<UploadSummary> {
  const root = options.root ?? ".";
  const settings = readSettings(options.env ?? process.env);
  const manifest = readManifest(root);
  const cached = new Set(cacheContents(root).keys);
  const summary: UploadSummary = { considered: 0, uploaded: 0, skipped: 0, not_restricted: 0, removed: 0, failed: [], marked: 0 };
  for (const key of [...manifest.keys()].sort()) {
    const row = manifest.get(key)!;
    // Counted over the manifest, not over the cache, so the two refusals say
    // what the manifest holds rather than what this machine happens to have.
    if (row.archive_tier === "t5-no-store") {
      summary.removed += 1;
      continue;
    }
    if (row.visibility !== "restricted") {
      summary.not_restricted += 1;
      continue;
    }
    if (!cached.has(key)) continue;
    assertRestricted(row);
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
      if (await markStore(key, "r2", root)) summary.marked += 1;
    } else summary.failed.push({ key, status: response.status });
  }
  return summary;
}
