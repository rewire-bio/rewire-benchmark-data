/** The Cloudflare R2 download path.
 *
 * Nothing here opens a socket. The transport is injected, so what is checked
 * is the whole of what pull decides: the refusal when a secret is absent, the
 * refusal on a removed row, the verification before anything is kept, and the
 * two properties a job in front of every run depends on, which are that a
 * cached object that verifies is never fetched and never written over, and
 * that a second run fetches nothing.
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import zlib from "node:zlib";
import { createHash } from "node:crypto";
import { afterEach, beforeEach, expect, it } from "vitest";
import { onARelease, pullObjects, selectRows } from "../scripts/archive/pull";
import { readSettings } from "../scripts/archive/r2";
import { upsertRow, readManifest } from "../scripts/archive/manifest";
import { objectPath } from "../scripts/archive/objects";
import { manifestRowSchema, visibilityOf, type ArchiveTier, type ManifestRow } from "../shared/archive/schema";

const roots: string[] = [];
const held = process.env.ARCHIVE_CACHE;
// cacheRoot() reads ARCHIVE_CACHE before it reads the root it was passed, so a
// value left in this process would send every write to one place.
beforeEach(() => { delete process.env.ARCHIVE_CACHE; });
afterEach(() => {
  if (held === undefined) delete process.env.ARCHIVE_CACHE;
  else process.env.ARCHIVE_CACHE = held;
  roots.splice(0).forEach((root) => fs.rmSync(root, { recursive: true, force: true }));
});

const temporaryRoot = () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "archive-pull-"));
  roots.push(root);
  return root;
};

const digest = (bytes: Buffer | string) => createHash("sha256").update(bytes).digest("hex");

const secrets = {
  R2_ACCOUNT_ID: "account",
  R2_ACCESS_KEY_ID: "key",
  R2_SECRET_ACCESS_KEY: "secret",
  R2_BUCKET: "archive",
};

const row = (bytes: Buffer, tier: ArchiveTier, overrides: Partial<ManifestRow> = {}): ManifestRow =>
  manifestRowSchema.parse({
    sha256: digest(bytes),
    bytes: bytes.length,
    media_type: "application/pdf",
    layer: "exact-bytes",
    origin: "https://example.org/one.pdf",
    requested_url: null,
    first_seen_at: "2026-11-17T09:00:00Z",
    store: "local-cache",
    visibility: visibilityOf(tier),
    archive_tier: tier,
    observed_licence: null,
    exposure: "policy",
    derived_from: null,
    derivation: null,
    previous_path: null,
    source_ids: ["source-one"],
    ...overrides,
  });

/** A bucket that holds gzip files by asset name, and a log of every request. */
function fakeBucket(objects: Record<string, Buffer>, status: Record<string, number> = {}) {
  const asked: string[] = [];
  return {
    asked,
    fetch: async (url: string, init: { method: string; headers: Record<string, string> }) => {
      const name = url.split("/").pop()!;
      asked.push(`${init.method} ${name}`);
      const code = status[name] ?? (objects[name] ? 200 : 404);
      const body = objects[name] ?? Buffer.alloc(0);
      return {
        status: code,
        arrayBuffer: async () => body.buffer.slice(body.byteOffset, body.byteOffset + body.byteLength) as ArrayBuffer,
        text: async () => (code === 200 ? body.toString("utf8") : `<Error><Code>NoSuchKey</Code><Key>${name}</Key></Error>`),
      };
    },
  };
}

it("names every missing secret at the call, and never at import", () => {
  expect(() => readSettings({})).toThrow(/R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET/);
  expect(() => readSettings({ ...secrets, R2_BUCKET: "  " })).toThrow(/R2_BUCKET/);
});

it("refuses to run with no credential, once there is something to fetch", async () => {
  const root = temporaryRoot();
  const bytes = Buffer.from("one");
  await upsertRow(row(bytes, "t4-private"), root);
  await expect(pullObjects({ root, env: {}, fetch: fakeBucket({}).fetch })).rejects.toThrow(/R2_ACCOUNT_ID/);
});

it("needs no credential at all when the cache is already complete", async () => {
  const root = temporaryRoot();
  const bytes = Buffer.from("one");
  const listed = row(bytes, "t4-private");
  await upsertRow(listed, root);
  fs.mkdirSync(path.dirname(objectPath(listed.sha256, root)), { recursive: true });
  fs.writeFileSync(objectPath(listed.sha256, root), zlib.gzipSync(bytes));
  const bucket = fakeBucket({});
  const summary = await pullObjects({ root, env: {}, fetch: bucket.fetch });
  expect({ held: summary.already_held, downloaded: summary.downloaded, asked: bucket.asked }).toEqual({ held: 1, downloaded: 0, asked: [] });
});

it("never asks for a removed row, whatever the bucket still holds", async () => {
  const root = temporaryRoot();
  const bytes = Buffer.from("taken down");
  const listed = row(bytes, "t5-no-store", { removed_at: "2026-11-18T09:00:00Z", removed_reason: "rights holder request", removed_requester: "docs/reviews/2026-11-18.md" });
  await upsertRow(listed, root);
  const bucket = fakeBucket({ [`${listed.sha256}.gz`]: zlib.gzipSync(bytes) });
  const summary = await pullObjects({ root, env: secrets, fetch: bucket.fetch });
  expect({ removed: summary.removed, selected: summary.selected, downloaded: summary.downloaded, asked: bucket.asked })
    .toEqual({ removed: 1, selected: 0, downloaded: 0, asked: [] });
  expect(fs.existsSync(objectPath(listed.sha256, root))).toBe(false);
});

it("downloads, verifies and keeps the bytes the bucket served, and fetches nothing on a second run", async () => {
  const root = temporaryRoot();
  const bytes = Buffer.from("the archived artifact");
  const listed = row(bytes, "t4-private");
  await upsertRow(listed, root);
  const compressed = zlib.gzipSync(bytes);
  const bucket = fakeBucket({ [`${listed.sha256}.gz`]: compressed });

  const first = await pullObjects({ root, env: secrets, fetch: bucket.fetch });
  expect({ downloaded: first.downloaded, failed: first.failed, bytes: first.expanded_bytes })
    .toEqual({ downloaded: 1, failed: [], bytes: bytes.length });
  expect(bucket.asked).toEqual([`GET ${listed.sha256}.gz`]);
  // The received gzip file is what is kept: re-compressing is not byte stable,
  // and the cache should hold what the bucket holds.
  expect(fs.readFileSync(objectPath(listed.sha256, root))).toEqual(compressed);

  const second = await pullObjects({ root, env: secrets, fetch: bucket.fetch });
  expect({ downloaded: second.downloaded, held: second.already_held }).toEqual({ downloaded: 0, held: 1 });
  expect(bucket.asked).toEqual([`GET ${listed.sha256}.gz`]);
});

it("fails by name on bytes that do not hash to the manifest key, and writes nothing", async () => {
  const root = temporaryRoot();
  const bytes = Buffer.from("the archived artifact");
  const listed = row(bytes, "t4-private");
  await upsertRow(listed, root);
  const bucket = fakeBucket({ [`${listed.sha256}.gz`]: zlib.gzipSync(Buffer.from("something else entirely")) });

  const summary = await pullObjects({ root, env: secrets, fetch: bucket.fetch });
  expect(summary.downloaded).toBe(0);
  expect(summary.failed).toHaveLength(1);
  expect(summary.failed[0].key).toBe(listed.sha256);
  expect(summary.failed[0].message).toMatch(listed.sha256);
  expect(fs.existsSync(objectPath(listed.sha256, root))).toBe(false);
  // The manifest is untouched: pull writes under the cache and nowhere else.
  expect([...readManifest(root).keys()]).toEqual([listed.sha256]);
});

it("names the key, the status and the bucket's own error when a request fails", async () => {
  const root = temporaryRoot();
  const listed = row(Buffer.from("missing"), "t4-private");
  await upsertRow(listed, root);
  const bucket = fakeBucket({}, { [`${listed.sha256}.gz`]: 403 });
  const summary = await pullObjects({ root, env: secrets, fetch: bucket.fetch });
  expect(summary.failed).toEqual([{ key: listed.sha256, status: 403, message: expect.stringContaining("NoSuchKey") }]);
});

it("leaves an object that already verifies exactly as it was, even when the bucket holds other bytes", async () => {
  const root = temporaryRoot();
  const bytes = Buffer.from("the archived artifact");
  const listed = row(bytes, "t0-public");
  await upsertRow(listed, root);
  const mine = zlib.gzipSync(bytes, { level: 9 });
  fs.mkdirSync(path.dirname(objectPath(listed.sha256, root)), { recursive: true });
  fs.writeFileSync(objectPath(listed.sha256, root), mine);
  const bucket = fakeBucket({ [`${listed.sha256}.gz`]: zlib.gzipSync(bytes, { level: 1 }) });

  await pullObjects({ root, env: secrets, fetch: bucket.fetch });
  expect(fs.readFileSync(objectPath(listed.sha256, root))).toEqual(mine);
  expect(bucket.asked).toEqual([]);
});

it("re-fetches an object held under the right name whose bytes no longer verify", async () => {
  const root = temporaryRoot();
  const bytes = Buffer.from("the archived artifact");
  const listed = row(bytes, "t4-private");
  await upsertRow(listed, root);
  fs.mkdirSync(path.dirname(objectPath(listed.sha256, root)), { recursive: true });
  fs.writeFileSync(objectPath(listed.sha256, root), Buffer.from("not a gzip file at all"));
  const good = zlib.gzipSync(bytes);
  const bucket = fakeBucket({ [`${listed.sha256}.gz`]: good });

  const summary = await pullObjects({ root, env: secrets, fetch: bucket.fetch });
  expect({ downloaded: summary.downloaded, held: summary.already_held }).toEqual({ downloaded: 1, held: 0 });
  expect(fs.readFileSync(objectPath(listed.sha256, root))).toEqual(good);
});

it("takes a filter, so a job pulls what it reads rather than the whole archive", async () => {
  const root = temporaryRoot();
  const one = row(Buffer.from("one"), "t0-public", { source_ids: ["source-one"] });
  const two = row(Buffer.from("two"), "t4-private", { source_ids: ["source-two"] });
  await upsertRow(one, root);
  await upsertRow(two, root);
  const manifest = readManifest(root);
  expect(selectRows(manifest, { sources: ["source-two"] }).map((entry) => entry.sha256)).toEqual([two.sha256]);
  expect(selectRows(manifest, { keys: [one.sha256] }).map((entry) => entry.sha256)).toEqual([one.sha256]);
  expect(selectRows(manifest, {}).map((entry) => entry.sha256)).toEqual([one.sha256, two.sha256].sort());

  const bucket = fakeBucket({ [`${one.sha256}.gz`]: zlib.gzipSync(Buffer.from("one")), [`${two.sha256}.gz`]: zlib.gzipSync(Buffer.from("two")) });
  const summary = await pullObjects({ root, env: secrets, fetch: bucket.fetch, sources: ["source-two"] });
  expect({ matched: summary.matched, downloaded: summary.downloaded, asked: bucket.asked })
    .toEqual({ matched: 1, downloaded: 1, asked: [`GET ${two.sha256}.gz`] });
});

it("reports the selection and fetches nothing on a dry run, with no credential", async () => {
  const root = temporaryRoot();
  await upsertRow(row(Buffer.from("one"), "t0-public"), root);
  await upsertRow(row(Buffer.from("two"), "t4-private"), root);
  const bucket = fakeBucket({});
  const summary = await pullObjects({ root, env: {}, fetch: bucket.fetch, dryRun: true });
  expect({ selected: summary.selected, restricted: summary.selected_restricted, open: summary.selected_public, asked: bucket.asked })
    .toEqual({ selected: 2, restricted: 1, open: 1, asked: [] });
});

it("takes a limit, so a large pull can be taken in stages and the rest is counted", async () => {
  const root = temporaryRoot();
  const objects: Record<string, Buffer> = {};
  for (const word of ["one", "two", "three"]) {
    const listed = row(Buffer.from(word), "t4-private");
    await upsertRow(listed, root);
    objects[`${listed.sha256}.gz`] = zlib.gzipSync(Buffer.from(word));
  }
  const bucket = fakeBucket(objects);
  const summary = await pullObjects({ root, env: secrets, fetch: bucket.fetch, limit: 2 });
  expect({ downloaded: summary.downloaded, back: summary.held_back_by_limit, asked: bucket.asked.length })
    .toEqual({ downloaded: 2, back: 1, asked: 2 });
});

/** Pulling from the release assets rather than from the bucket.
 *
 * This exists for one job and the tests say which: filling a cache so that
 * objects can be put into the bucket. A runner has no cache and upload sends
 * only what the cache holds, so without this an upload job would find nothing
 * to send and report success. The assets are public, so it takes no credential,
 * and it must not quietly ask the bucket for anything.
 */
it("pulls from the release assets with no credential at all", async () => {
  const root = temporaryRoot();
  const bytes = Buffer.from("published on a release tag");
  const listed = row(bytes, "t0-public", { store: "github-release" });
  await upsertRow(listed, root);
  const compressed = zlib.gzipSync(bytes);
  const urls: string[] = [];
  const assets = fakeBucket({ [`${listed.sha256}.gz`]: compressed });
  const watch = async (url: string, init: { method: string; headers: Record<string, string> }) => {
    urls.push(url);
    expect(init.headers).toEqual({});
    return assets.fetch(url, init);
  };

  const summary = await pullObjects({ root, env: {}, from: "release", fetch: watch });
  expect({ downloaded: summary.downloaded, failed: summary.failed, inR2: summary.already_in_the_bucket, nowhere: summary.no_remote_copy })
    .toEqual({ downloaded: 1, failed: [], inR2: 0, nowhere: 0 });
  expect(urls).toEqual([`https://github.com/rewire-bio/rewire-benchmark-data/releases/download/archive/objects-${listed.sha256[0]}/${listed.sha256}.gz`]);
  expect(fs.readFileSync(objectPath(listed.sha256, root))).toEqual(compressed);
});

it("tells a row already safe in the bucket from one with a single copy on this machine", async () => {
  // Both are rows no release tag holds, and lumping them together is what made the first
  // version of this read 0 objects at risk when the real answer was 296 safe and 0 at risk.
  // Only the second is a problem, and only it should be reported as one.
  const root = temporaryRoot();
  const inBucket = row(Buffer.from("only in the bucket"), "t4-private", { store: "r2" });
  const onlyHere = row(Buffer.from("only on this laptop"), "t3-verbatim-nd-nc", { store: "local-cache" });
  await upsertRow(inBucket, root);
  await upsertRow(onlyHere, root);
  const assets = fakeBucket({});

  const summary = await pullObjects({ root, env: {}, from: "release", fetch: assets.fetch });
  expect({ selected: summary.selected, inR2: summary.already_in_the_bucket, nowhere: summary.no_remote_copy, downloaded: summary.downloaded, asked: assets.asked })
    .toEqual({ selected: 2, inR2: 1, nowhere: 1, downloaded: 0, asked: [] });
});

it("takes a release copy that has become a mirror, because the bytes are still there", async () => {
  const bytes = Buffer.from("home in the bucket, mirrored on a tag");
  expect(onARelease(row(bytes, "t0-public", { store: "r2", mirrors: ["github-release"] }))).toBe(true);
  expect(onARelease(row(bytes, "t0-public", { store: "github-release" }))).toBe(true);
  expect(onARelease(row(bytes, "t4-private", { store: "r2" }))).toBe(false);
  expect(onARelease(row(bytes, "t4-private", { store: "local-cache" }))).toBe(false);
});

it("refuses a removed row on the release path too, whatever a tag still holds", async () => {
  const root = temporaryRoot();
  const bytes = Buffer.from("taken down");
  const listed = row(bytes, "t5-no-store", {
    store: "github-release",
    removed_at: "2026-11-18T09:00:00Z",
    removed_reason: "rights holder request",
    removed_requester: "docs/reviews/2026-11-18.md",
  });
  await upsertRow(listed, root);
  const assets = fakeBucket({ [`${listed.sha256}.gz`]: zlib.gzipSync(bytes) });

  const summary = await pullObjects({ root, env: {}, from: "release", fetch: assets.fetch });
  expect({ removed: summary.removed, selected: summary.selected, downloaded: summary.downloaded, asked: assets.asked })
    .toEqual({ removed: 1, selected: 0, downloaded: 0, asked: [] });
  expect(fs.existsSync(objectPath(listed.sha256, root))).toBe(false);
});
