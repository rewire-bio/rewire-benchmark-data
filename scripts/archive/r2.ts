/** The four values the Cloudflare R2 backend needs, and the signature one
 * request carries.
 *
 * Two commands share this: `upload` puts the restricted cached objects in the
 * bucket, `pull` brings objects back down into a cache that has none. Both
 * read the environment inside the function they are called from and never at
 * import time, so a command that touches no object needs no secret, and both
 * report an absent value by name rather than failing while signing.
 *
 * R2 speaks the S3 API, so a request is an ordinary SigV4 request and no new
 * dependency is needed for one.
 */
import crypto from "node:crypto";

export interface R2Settings {
  accountId: string;
  accessKeyId: string;
  secretAccessKey: string;
  bucket: string;
}

export const VARIABLES = ["R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET"] as const;

/** The four values, read at call time. Absent values are named, all of them,
 * so an operator sees which secret is missing rather than a signing failure
 * or a 403. */
export function readSettings(env: NodeJS.ProcessEnv = process.env): R2Settings {
  const missing = VARIABLES.filter((name) => !env[name]?.trim());
  if (missing.length)
    throw new Error(
      `The Cloudflare R2 backend needs ${missing.join(", ")} in the environment. ` +
        "Every other archive command runs without a credential; this one does not, and it refuses here rather than part way through a transfer.",
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

/** What a reply has to offer for the two commands to read it.
 *
 * Narrower than the platform's own Response, so a test passes a plain object
 * and no test opens a socket. A caller reads the body one way or the other,
 * never both: on a real Response the second read throws. */
export interface R2Reply {
  status: number;
  arrayBuffer(): Promise<ArrayBuffer>;
  text(): Promise<string>;
}

/** The one network call either command makes, injected so a test can stand in
 * front of it. `upload` still uses the platform's own; `pull` takes this. */
export type R2Fetch = (url: string, init: { method: string; headers: Record<string, string> }) => Promise<R2Reply>;

/** The platform's fetch, narrowed to the reply shape above. */
export const platformFetch: R2Fetch = (url, init) => fetch(url, init) as unknown as Promise<R2Reply>;
