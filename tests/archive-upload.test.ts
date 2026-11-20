/** The R2 upload path: the refusal when a value is absent, the shape of the signature, and what
 * the transfer leaves the manifest saying. Nothing here opens a socket. */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, expect, it, vi } from "vitest";
import { readSettings, signRequest, uploadObjects } from "../scripts/archive/upload";
import { putObject } from "../scripts/archive/objects";
import { readManifest, upsertRow } from "../scripts/archive/manifest";
import { manifestRowSchema, type ManifestRow } from "../shared/archive/schema";

const settings = {
  accountId: "account",
  accessKeyId: "key",
  secretAccessKey: "secret",
  bucket: "archive",
};

it("names every missing environment variable rather than failing while signing", () => {
  expect(() => readSettings({})).toThrow(/R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET/);
  expect(() => readSettings({ R2_ACCOUNT_ID: "a", R2_ACCESS_KEY_ID: "b", R2_SECRET_ACCESS_KEY: "c" })).toThrow(/R2_BUCKET/);
  expect(readSettings({ R2_ACCOUNT_ID: "a", R2_ACCESS_KEY_ID: "b", R2_SECRET_ACCESS_KEY: "c", R2_BUCKET: "d" })).toEqual({
    accountId: "a",
    accessKeyId: "b",
    secretAccessKey: "c",
    bucket: "d",
  });
});

it("signs the method it is about to send, at the bucket path, with the payload hash", () => {
  const at = new Date("2026-11-17T09:00:00Z");
  const put = signRequest(settings, "PUT", "abc.gz", Buffer.from("bytes"), at);
  const head = signRequest(settings, "HEAD", "abc.gz", Buffer.alloc(0), at);
  expect(put.url).toBe("https://account.r2.cloudflarestorage.com/archive/abc.gz");
  expect(put.headers["x-amz-date"]).toBe("20261117T090000Z");
  expect(put.headers.Authorization).toMatch(/^AWS4-HMAC-SHA256 Credential=key\/20261117\/auto\/s3\/aws4_request, /);
  expect(put.headers.Authorization).not.toBe(head.headers.Authorization);
});

/** The transfer itself, with the global fetch stubbed.
 *
 * The header above used to say this path had never been run against a live endpoint and so was
 * checked only for its refusal and its signature. That left the part that decides what the
 * manifest ends up saying untested, and it is the part a CI job depends on: an upload that sends
 * bytes and does not record where they now live leaves the store claiming they are somewhere
 * else. Nothing here opens a socket.
 */
const roots: string[] = [];
afterEach(() => {
  vi.unstubAllGlobals();
  roots.splice(0).forEach((root) => fs.rmSync(root, { recursive: true, force: true }));
});

const temporaryRoot = () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "archive-upload-"));
  roots.push(root);
  return root;
};

const secrets = { R2_ACCOUNT_ID: "account", R2_ACCESS_KEY_ID: "key", R2_SECRET_ACCESS_KEY: "secret", R2_BUCKET: "archive" };

const listed = (key: string, bytes: number, overrides: Partial<ManifestRow> = {}): ManifestRow =>
  manifestRowSchema.parse({
    sha256: key,
    bytes,
    media_type: "application/pdf",
    layer: "exact-bytes",
    origin: "https://example.org/one.pdf",
    requested_url: null,
    first_seen_at: "2026-11-17T09:00:00Z",
    store: "github-release",
    visibility: "public",
    archive_tier: "t0-public",
    observed_licence: null,
    exposure: "policy",
    derived_from: null,
    derivation: null,
    previous_path: null,
    source_ids: ["source-one"],
    ...overrides,
  });

/** A bucket that answers HEAD from what it holds and records every request. */
function stubBucket(holds: Set<string>, putStatus = 200) {
  const sent: string[] = [];
  vi.stubGlobal("fetch", async (url: string, init: { method: string }) => {
    const name = url.split("/").pop()!;
    sent.push(`${init.method} ${name}`);
    if (init.method === "HEAD") return { status: holds.has(name) ? 200 : 404, ok: holds.has(name) };
    if (putStatus === 200) holds.add(name);
    return { status: putStatus, ok: putStatus === 200 };
  });
  return sent;
}

it("sends the bytes the cache holds and records the bucket as their home", async () => {
  const root = temporaryRoot();
  const bytes = Buffer.from("bytes on a release tag and nowhere else");
  const { key } = putObject(bytes, root);
  await upsertRow(listed(key, bytes.length), root);
  const sent = stubBucket(new Set());

  const summary = await uploadObjects({ root, env: secrets });
  expect({ uploaded: summary.uploaded, skipped: summary.skipped, marked: summary.marked, failed: summary.failed })
    .toEqual({ uploaded: 1, skipped: 0, marked: 1, failed: [] });
  expect(sent).toEqual([`HEAD ${key}.gz`, `PUT ${key}.gz`]);
  expect(readManifest(root).get(key)).toMatchObject({ store: "r2", mirrors: ["github-release"] });
});

it("marks a row whose bytes the bucket already holds, so an interrupted run can be repaired", async () => {
  // The state a cancelled job leaves: the object is in the bucket and the manifest commit never
  // happened. The second run must not skip the row silently, or it stays wrong for good.
  const root = temporaryRoot();
  const bytes = Buffer.from("already up, never recorded");
  const { key } = putObject(bytes, root);
  await upsertRow(listed(key, bytes.length), root);
  const sent = stubBucket(new Set([`${key}.gz`]));

  const summary = await uploadObjects({ root, env: secrets });
  expect({ uploaded: summary.uploaded, skipped: summary.skipped, marked: summary.marked })
    .toEqual({ uploaded: 0, skipped: 1, marked: 1 });
  expect(sent).toEqual([`HEAD ${key}.gz`]);
  expect(readManifest(root).get(key)).toMatchObject({ store: "r2", mirrors: ["github-release"] });
});

it("leaves the row alone when the bucket refuses the bytes", async () => {
  const root = temporaryRoot();
  const bytes = Buffer.from("the bucket says no");
  const { key } = putObject(bytes, root);
  await upsertRow(listed(key, bytes.length), root);
  stubBucket(new Set(), 403);

  const summary = await uploadObjects({ root, env: secrets });
  expect({ uploaded: summary.uploaded, marked: summary.marked, failed: summary.failed })
    .toEqual({ uploaded: 0, marked: 0, failed: [{ key, status: 403 }] });
  expect(readManifest(root).get(key)).toMatchObject({ store: "github-release", mirrors: [] });
});

it("needs no credential and sends nothing on a dry run", async () => {
  const root = temporaryRoot();
  const bytes = Buffer.from("counted, not sent");
  const { key } = putObject(bytes, root);
  await upsertRow(listed(key, bytes.length), root);
  const sent = stubBucket(new Set());

  const summary = await uploadObjects({ root, env: secrets, dryRun: true });
  // skipped stays 0 and the summary says it was a dry run. Counting these as skipped read as
  // "the bucket already holds them", which is a claim no dry run is in a position to make: it
  // never sends the HEAD that would settle it.
  expect({ considered: summary.considered, uploaded: summary.uploaded, skipped: summary.skipped, would: summary.would_upload, dry: summary.dry_run, marked: summary.marked })
    .toEqual({ considered: 1, uploaded: 0, skipped: 0, would: 1, dry: true, marked: 0 });
  expect(sent).toEqual([]);
  expect(readManifest(root).get(key)).toMatchObject({ store: "github-release", mirrors: [] });
});
