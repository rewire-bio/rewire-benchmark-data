/** The Cloudflare R2 upload path.
 *
 * Written, not run. There is no R2 credential in this environment, so this
 * code has never been exercised against a live endpoint. It reads its four
 * values from the environment inside the function, never at import time, and
 * fails with a clear message when they are absent. Nothing in fetch, verify or
 * status calls it, and no CI job does either.
 *
 * R2 speaks the S3 API, so a PUT is an ordinary SigV4 request and no new
 * dependency is needed for it.
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
import crypto from "node:crypto";
import fs from "node:fs";
import { archiveAssetName, cacheContents, objectPath } from "./objects";
import { readManifest } from "./manifest";
import { isRemoved, type ManifestRow } from "../../shared/archive/schema";

export interface R2Settings {
  accountId: string;
  accessKeyId: string;
  secretAccessKey: string;
  bucket: string;
}

const VARIABLES = ["R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET"] as const;

/** The four values, read at call time. Absent values are named, so the
 * operator sees which secret is missing rather than a signing failure. */
export function readSettings(env: NodeJS.ProcessEnv = process.env): R2Settings {
  const missing = VARIABLES.filter((name) => !env[name]?.trim());
  if (missing.length)
    throw new Error(
      `Cloudflare R2 upload needs ${missing.join(", ")} in the environment. ` +
        "No credential exists yet, so fetch, verify and status run without one and this command does not.",
    );
  return {
    accountId: env.R2_ACCOUNT_ID!.trim(),
    accessKeyId: env.R2_ACCESS_KEY_ID!.trim(),
    secretAccessKey: env.R2_SECRET_ACCESS_KEY!.trim(),
    bucket: env.R2_BUCKET!.trim(),
  };
}

const hmac = (key: crypto.BinaryLike, value: string) => crypto.createHmac("sha256", key).update(value).digest();
const hex = (value: crypto.BinaryLike) => crypto.createHash("sha256").update(value).digest("hex");

/** An AWS SigV4 Authorization header for one request, region auto, service s3. */
export function signRequest(
  settings: R2Settings,
  method: "PUT" | "HEAD" | "GET",
  key: string,
  body: Buffer,
  now = new Date(),
): { url: string; headers: Record<string, string> } {
  const host = `${settings.accountId}.r2.cloudflarestorage.com`;
  const stamp = `${now.toISOString().slice(0, 19).replace(/[-:]/g, "")}Z`;
  const date = stamp.slice(0, 8);
  const payloadHash = hex(body);
  const canonicalPath = `/${settings.bucket}/${key}`;
  const headers: Record<string, string> = {
    host,
    "x-amz-content-sha256": payloadHash,
    "x-amz-date": stamp,
  };
  const signedHeaders = Object.keys(headers).sort().join(";");
  const canonicalHeaders = Object.keys(headers)
    .sort()
    .map((name) => `${name}:${headers[name]}\n`)
    .join("");
  const canonicalRequest = [method, canonicalPath, "", canonicalHeaders, signedHeaders, payloadHash].join("\n");
  const scope = `${date}/auto/s3/aws4_request`;
  const toSign = ["AWS4-HMAC-SHA256", stamp, scope, hex(canonicalRequest)].join("\n");
  const signingKey = hmac(hmac(hmac(hmac(`AWS4${settings.secretAccessKey}`, date), "auto"), "s3"), "aws4_request");
  const signature = crypto.createHmac("sha256", signingKey).update(toSign).digest("hex");
  headers.Authorization = `AWS4-HMAC-SHA256 Credential=${settings.accessKeyId}/${scope}, SignedHeaders=${signedHeaders}, Signature=${signature}`;
  return { url: `https://${host}${canonicalPath}`, headers };
}

export interface UploadSummary {
  considered: number;
  uploaded: number;
  skipped: number;
  /** Rows the manifest marks public. They belong on a release tag. */
  not_restricted: number;
  /** Rows at t5-no-store. Their bytes are gone and never go back. */
  removed: number;
  failed: { key: string; status: number }[];
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
  const summary: UploadSummary = { considered: 0, uploaded: 0, skipped: 0, not_restricted: 0, removed: 0, failed: [] };
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
    if (response.ok) summary.uploaded += 1;
    else summary.failed.push({ key, status: response.status });
  }
  return summary;
}
