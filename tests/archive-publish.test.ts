/** The release asset publish path.
 *
 * Release assets are public, so the first thing checked here is the refusal:
 * a restricted object never reaches the uploader, and the gate throws with the
 * sha256 and the tier when one is handed to it directly. After that,
 * idempotency, the shard tags and the manifest mark.
 *
 * The GitHub client is injected, so nothing here calls gh or the network.
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createHash } from "node:crypto";
import { afterEach, expect, it } from "vitest";
import { archiveTag, assertPublishable, planPublish, publishObjects, shardNotes, type ReleaseClient } from "../scripts/archive/publish";
import { markHome, readManifest, upsertRow } from "../scripts/archive/manifest";
import { putObject } from "../scripts/archive/objects";
import { manifestRowSchema, visibilityOf, type ArchiveTier, type ManifestRow } from "../shared/archive/schema";

const roots: string[] = [];
afterEach(() => roots.splice(0).forEach((root) => fs.rmSync(root, { recursive: true, force: true })));
const temporaryRoot = () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "archive-publish-"));
  roots.push(root);
  return root;
};
const digest = (bytes: Buffer | string) => createHash("sha256").update(bytes).digest("hex");

const row = (sha256: string, tier: ArchiveTier, overrides: Partial<ManifestRow> = {}): ManifestRow =>
  manifestRowSchema.parse({
    sha256,
    bytes: 4,
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

/** A fake release host: tags it holds, assets per tag, and a log of every call. */
function fakeClient(existing: Record<string, string[]> = {}) {
  const tags = new Map<string, string[]>(Object.entries(existing));
  const created: string[] = [];
  const uploaded: { tag: string; file: string }[] = [];
  const client: ReleaseClient = {
    assets: (tag) => (tags.has(tag) ? [...tags.get(tag)!] : null),
    create: (tag) => {
      if (tags.has(tag)) throw new Error(`${tag} already exists`);
      tags.set(tag, []);
      created.push(tag);
    },
    upload: (tag, file) => {
      const assets = tags.get(tag);
      if (!assets) throw new Error(`${tag} does not exist`);
      const name = path.basename(file);
      if (assets.includes(name)) throw new Error(`${tag} already holds ${name}`);
      assets.push(name);
      uploaded.push({ tag, file });
    },
  };
  return { client, tags, created, uploaded };
}

/** A root holding one object per tier, cached and listed in the manifest. */
async function storeWithEveryTier(root: string): Promise<Record<ArchiveTier, string>> {
  const tiers: ArchiveTier[] = ["t0-public", "t1-public-nc", "t2-verbatim-nd", "t3-verbatim-nd-nc", "t4-private", "t5-no-store"];
  const keys = {} as Record<ArchiveTier, string>;
  for (const tier of tiers) {
    const bytes = Buffer.from(`bytes of ${tier}`);
    const { key } = putObject(bytes, root);
    keys[tier] = key;
    await upsertRow(row(key, tier, { bytes: bytes.length }), root);
  }
  // Every test below reads one tier's tag as that tier's own, so the six keys
  // have to land in six shards. They do, and this says so rather than leaving
  // a later reader to recompute six digests.
  expect(new Set(Object.values(keys).map((key) => key[0])).size).toBe(6);
  return keys;
}

it("publishes the public objects and refuses every restricted one", async () => {
  const root = temporaryRoot();
  const keys = await storeWithEveryTier(root);
  const fake = fakeClient();
  const summary = await publishObjects({ root, client: fake.client });

  const sent = fake.uploaded.map(({ file }) => path.basename(file, ".gz")).sort();
  expect(sent).toEqual([keys["t0-public"], keys["t1-public-nc"], keys["t2-verbatim-nd"], keys["t3-verbatim-nd-nc"]].sort());
  expect(sent).not.toContain(keys["t4-private"]);
  expect(sent).not.toContain(keys["t5-no-store"]);
  expect(summary.uploaded).toBe(4);
  expect(summary.public_rows).toBe(4);
  expect(summary.refused).toBe(2);
  expect(summary.refused_by_tier).toEqual({ "t4-private": 1, "t5-no-store": 1 });
  expect(summary.failed).toEqual([]);
});

it("refuses a restricted row handed straight to the gate, naming its sha256 and its tier", () => {
  const privateKey = digest("private bytes");
  const removedKey = digest("removed bytes");
  expect(() => assertPublishable(row(privateKey, "t4-private"))).toThrow(new RegExp(`${privateKey}.*t4-private`));
  expect(() => assertPublishable(row(removedKey, "t5-no-store"))).toThrow(new RegExp(`${removedKey}.*t5-no-store`));
  expect(() => assertPublishable(row(privateKey, "t4-private"))).toThrow(/restricted/);
  // A row whose visibility disagrees with its tier is refused on the tier.
  // manifestRowSchema rejects that pairing, so the gate is built the row by hand.
  const forged = { ...row(privateKey, "t0-public"), archive_tier: "t4-private" } as ManifestRow;
  expect(() => assertPublishable(forged)).toThrow(/Refusing to publish/);
  // And the publishable four pass.
  for (const tier of ["t0-public", "t1-public-nc", "t2-verbatim-nd", "t3-verbatim-nd-nc"] as ArchiveTier[])
    expect(() => assertPublishable(row(digest(tier), tier))).not.toThrow();
});

it("skips an object already on the tag and uploads nothing on a second run", async () => {
  const root = temporaryRoot();
  const keys = await storeWithEveryTier(root);
  const already = `${keys["t0-public"]}.gz`;
  const fake = fakeClient({ [archiveTag(keys["t0-public"][0])]: [already] });

  const first = await publishObjects({ root, client: fake.client });
  expect(first.already_present).toBe(1);
  expect(first.uploaded).toBe(3);
  expect(fake.uploaded.map(({ file }) => path.basename(file))).not.toContain(already);

  const second = await publishObjects({ root, client: fake.client });
  expect(second.uploaded).toBe(0);
  expect(second.already_present).toBe(4);
  expect(second.tags_created).toEqual([]);
  expect(fake.uploaded).toHaveLength(3);
});

it("puts each object on its shard tag and creates only the tags it needs", async () => {
  const root = temporaryRoot();
  const keys = await storeWithEveryTier(root);
  const fake = fakeClient();
  const summary = await publishObjects({ root, client: fake.client });

  for (const { tag, file } of fake.uploaded) {
    const key = path.basename(file, ".gz");
    expect(tag).toBe(`archive/objects-${key[0]}`);
  }
  expect(fake.created.sort()).toEqual(summary.tags_created.sort());
  expect(fake.created).not.toContain(archiveTag(keys["t4-private"][0]));
  expect(shardNotes("a")).toContain("data/archive/objects/a.jsonl");
  expect(() => archiveTag("g")).toThrow(/Not a manifest shard/);
});

it("makes a release tag the home of bytes that had none but a laptop, and a mirror of bytes that do", async () => {
  const root = temporaryRoot();
  const keys = await storeWithEveryTier(root);
  const before = readManifest(root);
  const summary = await publishObjects({ root, client: fakeClient().client });
  const after = readManifest(root);

  expect(summary.marked).toBe(4);
  // These rows came from a fetch, so their only recorded home was local-cache: a directory on
  // whichever machine fetched them, which no other reader can reach. A tag anyone can download
  // is a better home than that, so it becomes the home rather than a mirror of an unreachable
  // one. Once an upload has made the bucket the home, the tag goes back to being a mirror,
  // which is what the store test covers.
  expect(after.get(keys["t0-public"])!.store).toBe("github-release");
  expect(after.get(keys["t0-public"])!.mirrors).toEqual([]);
  expect(after.get(keys["t3-verbatim-nd-nc"])!.store).toBe("github-release");
  // Restricted bytes are not published at all, so nothing about that row moves.
  expect(after.get(keys["t4-private"])!.store).toBe("local-cache");
  expect(after.get(keys["t4-private"])!.mirrors).toEqual([]);
  // Where the bucket is already the home, the tag is recorded as the second copy it is.
  await markHome(keys["t1-public-nc"], "r2", root);
  await publishObjects({ root, client: fakeClient().client });
  expect(readManifest(root).get(keys["t1-public-nc"])).toMatchObject({ store: "r2", mirrors: ["github-release"] });
  for (const [key, published] of after) {
    const was = before.get(key)!;
    expect({ ...published, store: was.store, mirrors: was.mirrors }).toEqual(was);
  }
  // The URL is archiveAssetUrl's, derived from the key. No second scheme.
  const key = keys["t0-public"];
  expect(summary.urls).toContain(`https://github.com/rewire-bio/rewire-benchmark-data/releases/download/archive/objects-${key[0]}/${key}.gz`);

  // A second run marks nothing, because every row already says where the bytes are.
  const again = await publishObjects({ root, client: fakeClient({}).client });
  expect(again.marked).toBe(0);
});

it("leaves the manifest alone under --no-mark, so a run beside a fetch does not rewrite a shard", async () => {
  const root = temporaryRoot();
  const keys = await storeWithEveryTier(root);
  const fake = fakeClient();
  const summary = await publishObjects({ root, client: fake.client, mark: false });
  expect(summary.uploaded).toBe(4);
  expect(summary.marked).toBe(0);
  expect(readManifest(root).get(keys["t0-public"])).toMatchObject({ store: "local-cache", mirrors: [] });

  // The later run uploads nothing and records what it finds.
  const marking = await publishObjects({ root, client: fake.client });
  expect(marking.uploaded).toBe(0);
  expect(marking.marked).toBe(4);
  expect(readManifest(root).get(keys["t0-public"])).toMatchObject({ store: "github-release", mirrors: [] });
});

it("creates and uploads nothing on a dry run, and counts what would go", async () => {
  const root = temporaryRoot();
  await storeWithEveryTier(root);
  const fake = fakeClient();
  const summary = await publishObjects({ root, client: fake.client, dryRun: true });

  expect(fake.created).toEqual([]);
  expect(fake.uploaded).toEqual([]);
  expect(fake.tags.size).toBe(0);
  expect(summary.dry_run).toBe(true);
  expect(summary.uploaded).toBe(0);
  expect(summary.marked).toBe(0);
  expect(summary.urls).toHaveLength(4);
  expect(summary.public_rows).toBe(4);
  expect(summary.public_by_tier).toEqual({ "t0-public": 1, "t1-public-nc": 1, "t2-verbatim-nd": 1, "t3-verbatim-nd-nc": 1 });
  expect(summary.public_bytes).toBe(
    ["t0-public", "t1-public-nc", "t2-verbatim-nd", "t3-verbatim-nd-nc"].reduce((total, tier) => total + `bytes of ${tier}`.length, 0),
  );
  expect(summary.public_compressed_bytes).toBeGreaterThan(0);
  expect(summary.tags_created.length).toBeGreaterThan(0);
  expect([...readManifest(root).values()].every((row) => row.store === "local-cache")).toBe(true);
});

it("takes the first --limit objects by key and leaves the rest for the next run", async () => {
  const root = temporaryRoot();
  await storeWithEveryTier(root);
  const all = planPublish({ root }).candidates.map((candidate) => candidate.key);
  expect(all).toEqual([...all].sort());
  const limited = planPublish({ root, limit: 2 });
  expect(limited.candidates.map((candidate) => candidate.key)).toEqual(all.slice(0, 2));
  // The totals are the whole manifest's either way; only the work is limited.
  expect(limited.public_rows).toBe(4);
  const summary = await publishObjects({ root, limit: 2, client: fakeClient().client });
  expect(summary.considered).toBe(2);
  expect(summary.uploaded).toBe(2);
});

it("never uploads a public object whose cached bytes are absent or no longer hash to their key", async () => {
  const root = temporaryRoot();
  const keys = await storeWithEveryTier(root);
  const missing = digest("bytes nobody holds");
  await upsertRow(row(missing, "t0-public", { bytes: 19 }), root);
  fs.writeFileSync(path.join(root, "data/archive/cache", keys["t2-verbatim-nd"].slice(0, 2), `${keys["t2-verbatim-nd"]}.gz`), "not gzip");

  const fake = fakeClient();
  const summary = await publishObjects({ root, client: fake.client });
  expect(summary.public_rows).toBe(5);
  expect(summary.public_not_in_cache).toBe(2);
  expect(summary.uploaded).toBe(3);
  const sent = fake.uploaded.map(({ file }) => path.basename(file, ".gz"));
  expect(sent).not.toContain(missing);
  expect(sent).not.toContain(keys["t2-verbatim-nd"]);
});

it("reports an upload that failed and keeps going, and the command exits non-zero on one", async () => {
  const root = temporaryRoot();
  const keys = await storeWithEveryTier(root);
  const fake = fakeClient();
  const failing: ReleaseClient = {
    ...fake.client,
    upload: (tag, file) => {
      if (path.basename(file, ".gz") === keys["t0-public"]) throw new Error("gh release upload: 502 Bad Gateway");
      fake.client.upload(tag, file);
    },
  };
  const summary = await publishObjects({ root, client: failing });
  expect(summary.uploaded).toBe(3);
  expect(summary.failed).toEqual([{ key: keys["t0-public"], message: "gh release upload: 502 Bad Gateway" }]);
  // The failed object keeps its local-cache store, so a later run retries it.
  expect(readManifest(root).get(keys["t0-public"])!.store).toBe("local-cache");
  expect(summary.marked).toBe(3);
});
