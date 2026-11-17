/** The object store and the manifest. */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createHash } from "node:crypto";
import { afterEach, expect, it } from "vitest";
import { archiveAssetName, archiveAssetUrl, cacheContents, hasObject, objectPath, putObject, readObject } from "../scripts/archive/objects";
import { checkManifest, readManifest, readShard, shardPath, updateRow, upsertRow } from "../scripts/archive/manifest";
import { appendReceipt, latestBySource, readReceipts } from "../scripts/archive/receipts";
import { canonicalLine, manifestRowSchema, objectShard, type FetchReceipt, type ManifestRow } from "../shared/archive/schema";

const roots: string[] = [];
afterEach(() => roots.splice(0).forEach((root) => fs.rmSync(root, { recursive: true, force: true })));
const temporaryRoot = () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "archive-store-"));
  roots.push(root);
  return root;
};
const digest = (bytes: Buffer | string) => createHash("sha256").update(bytes).digest("hex");

const row = (overrides: Partial<ManifestRow> = {}): ManifestRow =>
  manifestRowSchema.parse({
    sha256: digest("one"),
    bytes: 3,
    media_type: "application/pdf",
    layer: "exact-bytes",
    origin: "https://example.org/one.pdf",
    requested_url: null,
    first_seen_at: "2026-11-17T09:00:00Z",
    store: "local-cache",
    visibility: "restricted",
    archive_tier: "t4-private",
    observed_licence: null,
    exposure: "policy",
    derived_from: null,
    derivation: null,
    previous_path: null,
    source_ids: ["source-one"],
    ...overrides,
  });

it("keys an object on the sha256 of its expanded bytes and verifies it on the way out", () => {
  const root = temporaryRoot();
  const bytes = Buffer.from("primary source bytes");
  const stored = putObject(bytes, root);
  expect(stored.key).toBe(digest(bytes));
  expect(stored.written).toBe(true);
  expect(hasObject(stored.key, root)).toBe(true);
  expect(readObject(stored.key, root).toString()).toBe("primary source bytes");
  expect(putObject(bytes, root).written).toBe(false);
  expect(cacheContents(root).keys).toEqual([stored.key]);
});

it("reports a cached object whose bytes no longer match its key as absent", () => {
  const root = temporaryRoot();
  const { key } = putObject(Buffer.from("primary source bytes"), root);
  fs.writeFileSync(objectPath(key, root), Buffer.from("not gzip and not those bytes"));
  expect(hasObject(key, root)).toBe(false);
  expect(() => readObject(key, root)).toThrow();
});

it("names the archive asset and the shard tag the way ADR 0004 does", () => {
  const key = digest("one");
  expect(archiveAssetName(key)).toBe(`${key}.gz`);
  expect(archiveAssetUrl(objectShard(key), archiveAssetName(key))).toBe(
    `https://github.com/rewire-bio/rewire-benchmark-data/releases/download/archive/objects-${key[0]}/${key}.gz`,
  );
  expect(() => archiveAssetUrl("g", "x.gz")).toThrow(/shard/);
});

it("writes a row into the shard its key names, sorted, and merges a second source into it", async () => {
  const root = temporaryRoot();
  const first = row();
  const second = row({ sha256: digest("two"), source_ids: ["source-two"] });
  expect((await upsertRow(first, root)).added).toBe(true);
  expect((await upsertRow(second, root)).added).toBe(true);
  expect((await upsertRow(first, root)).changed).toBe(false);
  expect((await upsertRow({ ...first, source_ids: ["source-three"] }, root)).changed).toBe(true);
  expect(readShard(objectShard(first.sha256), root)[0].source_ids).toEqual(["source-one", "source-three"]);
  expect(readManifest(root).size).toBe(2);
  expect(checkManifest(root).problems).toEqual([]);
  for (const shard of [first, second].map((entry) => objectShard(entry.sha256))) {
    const lines = fs.readFileSync(shardPath(shard, root), "utf8").split("\n").filter(Boolean);
    expect(lines).toEqual(lines.slice().sort());
  }
});

it("creates no shard file until a row needs one", () => {
  const root = temporaryRoot();
  expect(readManifest(root).size).toBe(0);
  expect(checkManifest(root)).toEqual({ rows: 0, problems: [] });
  expect(fs.existsSync(path.join(root, "data/archive/objects"))).toBe(false);
});

it("refuses a row that would publish a restricted tier or derive a layer with no command", () => {
  expect(() => row({ archive_tier: "t4-private", visibility: "public" })).toThrow(/t4-private is restricted/);
  expect(() => row({ layer: "text-layer" })).toThrow(/needs derived_from and derivation/);
  expect(() => row({ derived_from: digest("container") })).toThrow(/exact-bytes carries no derived_from/);
  expect(row({ layer: "text-layer", derived_from: digest("container"), derivation: "pdftotext -layout" }).layer).toBe("text-layer");
});

it("catches a row in the wrong shard and a shard out of order", () => {
  const root = temporaryRoot();
  const wrong = row({ sha256: digest("one") });
  const shard = objectShard(wrong.sha256) === "0" ? "1" : "0";
  fs.mkdirSync(path.join(root, "data/archive/objects"), { recursive: true });
  fs.writeFileSync(shardPath(shard, root), `${canonicalLine(wrong as unknown as Record<string, unknown>)}\n`);
  expect(checkManifest(root).problems.join(" ")).toMatch(/is in shard/);

  const other = temporaryRoot();
  const a = row({ sha256: `a${"0".repeat(63)}` });
  const b = row({ sha256: `a${"1".repeat(63)}` });
  fs.mkdirSync(path.join(other, "data/archive/objects"), { recursive: true });
  fs.writeFileSync(
    shardPath("a", other),
    [b, a].map((entry) => canonicalLine(entry as unknown as Record<string, unknown>)).join("\n") + "\n",
  );
  expect(checkManifest(other).problems.join(" ")).toMatch(/not sorted/);
});

it("writes a receipt for a failure as well as a success and reads the latest per source", () => {
  const root = temporaryRoot();
  const base = {
    schema_version: 1 as const,
    requested_url: "https://example.org/one.pdf",
    routes_tried: [{ route: "direct" as const, url: "https://example.org/one.pdf", status: 403, reason: "http_error" as const }],
    source_class: "publisher" as const,
  };
  const failed: FetchReceipt = {
    ...base,
    source_id: "source-one",
    final_url: null,
    http_status: 403,
    fetched_at: "2026-11-17T09:00:00Z",
    content_type: null,
    bytes: null,
    sha256: null,
    route: null,
    outcome: "failed",
    reason: "paywalled_not_held",
  };
  const stored: FetchReceipt = {
    ...base,
    source_id: "source-one",
    final_url: "https://example.org/one.pdf",
    http_status: 200,
    fetched_at: "2026-11-18T09:00:00Z",
    content_type: "application/pdf; charset=binary",
    bytes: 3,
    sha256: digest("one"),
    route: "direct",
    outcome: "stored",
    reason: null,
  };
  appendReceipt(failed, root);
  appendReceipt(stored, root);
  expect(fs.readdirSync(path.join(root, "data/omics/audits")).sort()).toEqual([
    "2026-11-17-archive-fetch.receipts.jsonl",
    "2026-11-18-archive-fetch.receipts.jsonl",
  ]);
  const receipts = readReceipts(root);
  expect(receipts).toHaveLength(2);
  expect(latestBySource(receipts).get("source-one")?.outcome).toBe("stored");
  expect(() => appendReceipt({ ...stored, sha256: null }, root)).toThrow(/stored receipt/);
  expect(() => appendReceipt({ ...failed, reason: null }, root)).toThrow(/failed receipt/);

  // not_artifact holds bytes and names what they are instead, so it needs
  // both the digest a stored receipt needs and the reason a failed one needs.
  const kept: FetchReceipt = {
    ...stored,
    fetched_at: "2026-11-19T09:00:00Z",
    outcome: "not_artifact",
    reason: "interstitial_body",
  };
  appendReceipt(kept, root);
  expect(latestBySource(readReceipts(root)).get("source-one")?.outcome).toBe("not_artifact");
  expect(() => appendReceipt({ ...kept, reason: null }, root)).toThrow(/not_artifact receipt carries a reason/);
  expect(() => appendReceipt({ ...kept, sha256: null }, root)).toThrow(/not_artifact receipt carries sha256/);
});

it("moves a row to another tier without refetching, and visibility follows the tier", async () => {
  const root = temporaryRoot();
  const stored = row();
  await upsertRow(stored, root);
  expect(await updateRow(stored.sha256, { archive_tier: "t1-public-nc", observed_licence: "CC BY-NC 4.0" }, root)).toBe(true);
  const updated = readShard(objectShard(stored.sha256), root)[0];
  expect(updated).toMatchObject({ archive_tier: "t1-public-nc", visibility: "public", observed_licence: "CC BY-NC 4.0" });
  expect(updated.sha256).toBe(stored.sha256);
  expect(await updateRow(digest("absent"), { archive_tier: "t0-public" }, root)).toBe(false);
  expect(checkManifest(root).problems).toEqual([]);
});
