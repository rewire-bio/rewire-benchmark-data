import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";
import { gzipSync } from "node:zlib";
import { execFileSync } from "node:child_process";
import { afterEach, describe, expect, it, vi } from "vitest";
import { assetName, assetUrl, fetchRelease, newestPublished, packageAssets, verifyPackage, type WebsiteManifest } from "../scripts/release/files";

const id = "2026-10-15-aaaaaaaaaaaa";
const older = "2026-10-01-bbbbbbbbbbbb";
const sha = (bytes: Buffer | string) => crypto.createHash("sha256").update(bytes).digest("hex");
const roots: string[] = [];
afterEach(() => { for (const root of roots.splice(0)) fs.rmSync(root, { recursive: true, force: true }); });
function write(root: string, file: string, bytes: Buffer | string) {
  fs.mkdirSync(path.dirname(path.join(root, file)), { recursive: true });
  fs.writeFileSync(path.join(root, file), bytes);
}
const files = { "catalogue.json": '{"release_id":"x"}', "use-cases.json": '{"mappings":[]}' } as Record<string, string>;

/** A repository with a committed receipt and manifest and an ignored, built release file. */
function packaged() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "release-files-")); roots.push(root);
  execFileSync("git", ["init", "-q", root]);
  const source = `data/omics/releases/${id}/catalogue.json.gz`;
  const manifest: WebsiteManifest = { schema_version: 1, release_id: id, files: [
    { source, destination: `public/omics/releases/${id}/catalogue.json`, sha256: sha(files["catalogue.json"]), bytes: files["catalogue.json"].length, scope: "current" },
  ] };
  write(root, ".gitignore", "/data/omics/releases/*/\n/website/files/\n");
  write(root, "website/manifest.json", JSON.stringify(manifest));
  write(root, `data/omics/releases/${id}.json`, JSON.stringify({ release_id: id, released_at: "2026-10-15T00:00:00Z", files: Object.fromEntries(Object.entries(files).map(([k, v]) => [k, sha(v)])) }));
  write(root, source, gzipSync(files["catalogue.json"]));
  execFileSync("git", ["add", "."], { cwd: root });
  return { root, source, manifest };
}

describe("release asset names", () => {
  it("flatten the manifest destination, as rewire-database expects", () => {
    expect(assetName(`public/omics/releases/${id}/records.jsonl`)).toBe(`public.omics.releases.${id}.records.jsonl.gz`);
    expect(assetName("lib/generated-benchmark-catalog.ts")).toBe("lib.generated-benchmark-catalog.ts.gz");
    expect(assetUrl(id, "x.gz")).toBe(`https://github.com/rewire-bio/rewire-benchmark-data/releases/download/serving/${id}/x.gz`);
    for (const unsafe of ["../x", "a//b", "/a", "a/./b", "a b"]) expect(() => assetName(unsafe)).toThrow("Unsafe");
  });
  it("refuse two entries that would share an asset", () => {
    const entry = { source: "website/files/a/b.json.gz", destination: "a/b.json", sha256: "0".repeat(64), bytes: 1, scope: "current" };
    expect(() => packageAssets({ schema_version: 1, release_id: id, files: [entry, { ...entry, destination: "a.b/json" }] })).toThrow("Two manifest entries");
  });
});

describe("verify:package", () => {
  it("accepts committed receipt and manifest with ignored release files of the listed bytes", () => {
    const { root } = packaged();
    expect(execFileSync("git", ["ls-files"], { cwd: root, encoding: "utf8" }).split("\n").filter(Boolean).sort())
      .toEqual([".gitignore", `data/omics/releases/${id}.json`, "website/manifest.json"]);
    expect(verifyPackage(root)).toEqual({ releaseId: id, sources: 1 });
  });
  it("refuses committed release files", () => {
    const { root, source } = packaged();
    execFileSync("git", ["add", "-f", source], { cwd: root });
    expect(() => verifyPackage(root)).toThrow("must not be committed");
  });
  it("refuses missing, altered or linked files and an uncommitted manifest", () => {
    const { root, source } = packaged();
    write(root, source, gzipSync("altered"));
    expect(() => verifyPackage(root)).toThrow("differs from its listed SHA-256");
    fs.rmSync(path.join(root, source));
    expect(() => verifyPackage(root)).toThrow("missing");
    fs.symlinkSync(path.join(root, "website/manifest.json"), path.join(root, source));
    expect(() => verifyPackage(root)).toThrow("not a regular file");
    execFileSync("git", ["rm", "-q", "--cached", "website/manifest.json"], { cwd: root });
    expect(() => verifyPackage(root)).toThrow("website/manifest.json must be committed");
  });
});

/** Serves assets of `withAssets` releases and raw Git files of the others; `override` replaces bytes by URL suffix. */
function github(withAssets: string[], override: Record<string, Buffer> = {}) {
  const calls: string[] = [];
  const fetchImpl = vi.fn(async (url: string, init?: RequestInit) => {
    calls.push(`${init?.method || "GET"} ${url}`);
    const fixed = Object.entries(override).find(([suffix]) => url.endsWith(suffix));
    const asset = /\/releases\/download\/serving\/([^/]+)\/(.+)$/.exec(url);
    if (asset) {
      if (!withAssets.includes(asset[1]) && !asset[2].startsWith("catalogue-")) return new Response("", { status: 404 });
      if (init?.method === "HEAD") return new Response(null, { status: withAssets.includes(asset[1]) ? 200 : 404 });
      const name = Object.keys(files).find((file) => asset[2] === `public.omics.releases.${asset[1]}.${file}.gz`);
      return fixed ? new Response(new Uint8Array(fixed[1])) : name ? new Response(new Uint8Array(gzipSync(files[name]))) : new Response("", { status: 404 });
    }
    const raw = /refs\/tags\/serving\/([^/]+)\/data\/omics\/releases\/[^/]+\/(.+)\.gz$/.exec(url);
    if (raw && !withAssets.includes(raw[1]) && files[raw[2]]) return new Response(new Uint8Array(fixed ? fixed[1] : gzipSync(files[raw[2]])));
    return new Response("", { status: 404 });
  });
  return { fetchImpl: fetchImpl as unknown as typeof fetch, calls };
}

describe("release:fetch", () => {
  it("downloads a release's files from its assets, checked against the receipt", async () => {
    const { root } = packaged();
    fs.rmSync(path.join(root, "data/omics/releases", id), { recursive: true });
    const { fetchImpl, calls } = github([id]);
    expect(await fetchRelease(id, { root, fetchImpl })).toEqual({ kept: 0, assets: 2, git: 0 });
    expect(calls.every((call) => call.includes("/releases/download/"))).toBe(true);
    expect(fs.readdirSync(path.join(root, "data/omics/releases", id)).sort()).toEqual(["catalogue.json.gz", "use-cases.json.gz"]);
    // A second run keeps verified files.
    expect(await fetchRelease(id, { root, fetchImpl })).toEqual({ kept: 2, assets: 0, git: 0 });
  });
  it("reads a release cut before the files left Git from Git at its tag", async () => {
    const { root } = packaged();
    write(root, `data/omics/releases/${older}.json`, JSON.stringify({ release_id: older, released_at: "2026-10-01T00:00:00Z", files: { "use-cases.json": sha(files["use-cases.json"]) } }));
    const { fetchImpl, calls } = github([id]);
    expect(await fetchRelease(older, { root, fetchImpl })).toEqual({ kept: 0, assets: 0, git: 1 });
    expect(calls.at(-1)).toBe(`GET https://raw.githubusercontent.com/rewire-bio/rewire-benchmark-data/refs/tags/serving/${older}/data/omics/releases/${older}/use-cases.json.gz`);
  });
  it("refuses altered files from either source and an unpublished release", async () => {
    const { root } = packaged();
    fs.rmSync(path.join(root, "data/omics/releases", id), { recursive: true });
    await expect(fetchRelease(id, { root, fetchImpl: github([id], { "catalogue.json.gz": gzipSync("altered") }).fetchImpl })).rejects.toThrow("differs from its listed SHA-256");
    write(root, `data/omics/releases/${older}.json`, JSON.stringify({ release_id: older, released_at: "2026-10-01T00:00:00Z", files: { "use-cases.json": sha(files["use-cases.json"]) } }));
    await expect(fetchRelease(older, { root, fetchImpl: github([], { "use-cases.json.gz": gzipSync("{}") }).fetchImpl })).rejects.toThrow("differs");
    write(root, `data/omics/releases/${older}.json`, JSON.stringify({ release_id: older, released_at: "2026-10-01T00:00:00Z", files: { "missing.json": sha("x") } }));
    await expect(fetchRelease(older, { root, fetchImpl: github([]).fetchImpl })).rejects.toThrow("is the release published?");
    expect(fs.readdirSync(path.join(root, "data/omics/releases", id))).toEqual([]);
  });
  it("defaults to the manifest's release, or the newest published one before it is published", async () => {
    const { root } = packaged();
    write(root, `data/omics/releases/${older}.json`, JSON.stringify({ release_id: older, released_at: "2026-10-01T00:00:00Z", files: {} }));
    expect(await newestPublished(root, github([id]).fetchImpl)).toBe(id);
    expect(await newestPublished(root, github([older]).fetchImpl)).toBe(older);
    await expect(newestPublished(root, github([]).fetchImpl)).rejects.toThrow("No published release");
  });
});
