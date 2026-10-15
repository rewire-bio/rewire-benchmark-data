/** Release files outside Git.
 *
 * Git keeps each release's receipt (data/omics/releases/<id>.json) and the
 * website manifest (website/manifest.json), which lists every website file
 * with the SHA-256 and size of its expanded bytes. The files themselves
 * (data/omics/releases/<id>/ and website/files/) are build output, ignored by
 * Git, and published as assets of the release's `serving/<id>` GitHub release
 * by `npm run serving:publish`. Each asset is named after its manifest
 * destination with `/` replaced by `.` and `.gz` appended; rewire-database
 * uses the same rule (scripts/release-assets.mjs there).
 *
 * Commands (scripts/release/files-cli.ts):
 *   npm run verify:package            check the built package: manifest and receipt
 *                                     tracked, files untracked, every file's bytes as listed
 *   npm run release:fetch [-- <id>]   put a published release's files in
 *                                     data/omics/releases/<id>/ (default: the release
 *                                     website/manifest.json names, or if that is not
 *                                     published yet, the newest published one)
 *
 * Releases cut before the files left Git have no such assets; their files are
 * read from Git at the `serving/<id>` tag instead. Either way each file is
 * checked against the receipt.
 */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import zlib from "node:zlib";
import { execFileSync } from "node:child_process";

export const repository = "rewire-bio/rewire-benchmark-data";
const RELEASE_ID = /^\d{4}-\d{2}-\d{2}-[a-f0-9]{12}$/;
const MAX_EXPANDED = 4 * 1024 ** 3;

export type ManifestEntry = { source: string; destination: string; sha256: string; bytes: number; scope: string };
export type WebsiteManifest = { schema_version: number; release_id: string; files: ManifestEntry[] };
type Fetch = (url: string, init?: RequestInit) => Promise<Response>;

const sha256 = (bytes: Buffer) => crypto.createHash("sha256").update(bytes).digest("hex");
const safePath = (value: unknown): value is string =>
  typeof value === "string" && /^[A-Za-z0-9_-][A-Za-z0-9._/-]*$/.test(value) &&
  value.split("/").every((part) => part && part !== "." && part !== "..");

/** The asset a manifest destination is published as: its path with `/` as `.`, plus `.gz`. */
export function assetName(destination: string): string {
  if (!safePath(destination)) throw new Error(`Unsafe release asset destination: ${destination}`);
  return destination.split("/").join(".") + ".gz";
}

export function assetUrl(releaseId: string, name: string): string {
  return `https://github.com/${repository}/releases/download/serving/${releaseId}/${name}`;
}

/** Expand gzip bytes and check them against a digest (and size, when known). */
export function expand(compressed: Buffer, digest: string, label: string, bytes?: number): Buffer {
  let expanded: Buffer;
  try { expanded = zlib.gunzipSync(compressed, { maxOutputLength: bytes === undefined ? MAX_EXPANDED : bytes + 1 }); }
  catch { throw new Error(`${label} is not the listed gzip file`); }
  if ((bytes !== undefined && expanded.length !== bytes) || sha256(expanded) !== digest)
    throw new Error(`${label} differs from its listed SHA-256`);
  return expanded;
}

export function readManifest(root = "."): WebsiteManifest {
  const manifest = JSON.parse(fs.readFileSync(path.join(root, "website/manifest.json"), "utf8"));
  if (manifest.schema_version !== 1 || !RELEASE_ID.test(manifest.release_id) || !Array.isArray(manifest.files))
    throw new Error("Invalid website/manifest.json");
  return manifest;
}

/** One asset per manifest entry. Refuses unsafe paths and two entries that would share an asset. */
export function packageAssets(manifest: WebsiteManifest): { name: string; entry: ManifestEntry }[] {
  const names = new Set<string>();
  return manifest.files.map((entry) => {
    if (!safePath(entry.source) || !entry.source.endsWith(".gz") || !/^[a-f0-9]{64}$/.test(entry.sha256) || !Number.isSafeInteger(entry.bytes))
      throw new Error(`Invalid manifest entry: ${entry.destination}`);
    const name = assetName(entry.destination);
    if (names.has(name)) throw new Error(`Two manifest entries map to release asset ${name}`);
    names.add(name);
    return { name, entry };
  });
}

function tracked(root: string): Set<string> {
  return new Set(execFileSync("git", ["ls-files", "-z"], { cwd: root, encoding: "utf8", maxBuffer: 64 * 1024 ** 2 }).split("\0").filter(Boolean));
}

/**
 * The built package is publishable: the manifest and the release receipt are
 * tracked, no listed file is (they go to the release assets), and every listed
 * file is present with exactly the listed bytes.
 */
export function verifyPackage(root = "."): { releaseId: string; sources: number } {
  const manifest = readManifest(root);
  const assets = packageAssets(manifest);
  const inGit = tracked(root);
  for (const file of ["website/manifest.json", `data/omics/releases/${manifest.release_id}.json`])
    if (!inGit.has(file)) throw new Error(`${file} must be committed`);
  const committed = assets.filter(({ entry }) => inGit.has(entry.source)).map(({ entry }) => entry.source);
  if (committed.length) throw new Error(`Release files must not be committed; they are published as release assets (${committed.length}):\n${committed.join("\n")}`);
  for (const { entry } of assets) {
    const file = path.join(root, entry.source);
    if (!fs.existsSync(file) || !fs.lstatSync(file).isFile()) throw new Error(`Release file missing or not a regular file: ${entry.source}`);
    expand(fs.readFileSync(file), entry.sha256, entry.source, entry.bytes);
  }
  return { releaseId: manifest.release_id, sources: assets.length };
}

/** The files a release receipt lists, by name, with the SHA-256 of their expanded bytes. */
export function receiptFiles(root: string, releaseId: string): Record<string, string> {
  if (!RELEASE_ID.test(releaseId)) throw new Error(`Invalid release ID: ${releaseId}`);
  const receipt = JSON.parse(fs.readFileSync(path.join(root, "data/omics/releases", `${releaseId}.json`), "utf8"));
  if (receipt.release_id !== releaseId || !receipt.files || typeof receipt.files !== "object")
    throw new Error(`Invalid receipt for ${releaseId}`);
  for (const [name, digest] of Object.entries(receipt.files))
    if (!/^[a-zA-Z0-9][a-zA-Z0-9._-]*$/.test(name) || typeof digest !== "string" || !/^[a-f0-9]{64}$/.test(digest))
      throw new Error(`Invalid receipt entry ${name} for ${releaseId}`);
  return receipt.files as Record<string, string>;
}

async function download(url: string, fetchImpl: Fetch): Promise<Buffer | null> {
  const response = await fetchImpl(url, { redirect: "follow", signal: AbortSignal.timeout(600_000) });
  if (response.status === 404) return null;
  if (response.status !== 200) throw new Error(`Download failed (${response.status}): ${url}`);
  return Buffer.from(await response.arrayBuffer());
}

/**
 * Put a published release's files in data/omics/releases/<id>/, each checked
 * against the receipt: from its `serving/<id>` asset, or, for a release cut
 * before the files left Git, from Git at that tag. Files already there with
 * the right bytes are kept.
 */
export async function fetchRelease(releaseId: string, { root = ".", fetchImpl = fetch as Fetch } = {}) {
  const files = receiptFiles(root, releaseId);
  const directory = path.join(root, "data/omics/releases", releaseId);
  fs.mkdirSync(directory, { recursive: true });
  const counts = { kept: 0, assets: 0, git: 0 };
  for (const [name, digest] of Object.entries(files).sort()) {
    const target = path.join(directory, `${name}.gz`);
    if (fs.existsSync(target)) {
      try { expand(fs.readFileSync(target), digest, target); counts.kept++; continue; } catch { fs.rmSync(target); }
    }
    let bytes = await download(assetUrl(releaseId, assetName(`public/omics/releases/${releaseId}/${name}`)), fetchImpl);
    let from: "assets" | "git" = "assets";
    if (!bytes) {
      from = "git";
      bytes = await download(`https://raw.githubusercontent.com/${repository}/refs/tags/serving/${releaseId}/data/omics/releases/${releaseId}/${name}.gz`, fetchImpl);
      if (!bytes) throw new Error(`${releaseId}/${name} is neither a release asset nor in Git at serving/${releaseId}; is the release published?`);
    }
    expand(bytes, digest, `${releaseId}/${name} (from ${from})`);
    fs.writeFileSync(`${target}.tmp`, bytes);
    fs.renameSync(`${target}.tmp`, target);
    counts[from]++;
  }
  return counts;
}

async function published(releaseId: string, fetchImpl: Fetch): Promise<boolean> {
  const response = await fetchImpl(assetUrl(releaseId, `catalogue-${releaseId}.json`), { method: "HEAD", redirect: "follow", signal: AbortSignal.timeout(60_000) });
  return response.status === 200;
}

/** The release website/manifest.json names if it is published, otherwise the newest published one by receipt date. */
export async function newestPublished(root = ".", fetchImpl = fetch as Fetch): Promise<string> {
  const current = readManifest(root).release_id;
  if (await published(current, fetchImpl)) return current;
  const receipts = fs.readdirSync(path.join(root, "data/omics/releases"))
    .filter((name) => RELEASE_ID.test(name.replace(/\.json$/, "")) && name.endsWith(".json"))
    .map((name) => JSON.parse(fs.readFileSync(path.join(root, "data/omics/releases", name), "utf8")) as { release_id: string; released_at: string })
    .sort((a, b) => b.released_at.localeCompare(a.released_at));
  for (const receipt of receipts) if (receipt.release_id !== current && await published(receipt.release_id, fetchImpl)) return receipt.release_id;
  throw new Error("No published release found");
}
