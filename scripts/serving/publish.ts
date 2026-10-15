/** Publish the release as an immutable GitHub Release.
 * Tag `serving/<release_id>` holds `catalogue-<release_id>.sqlite`, its
 * receipt, and every file website/manifest.json lists, one asset each, named
 * by scripts/release/files.ts. Those files are not committed; rewire-database
 * downloads them from here. An existing asset is never replaced. A prepared
 * file built by the same generator must be byte-identical to the published
 * one; a published website file must have the bytes the manifest lists.
 *   npm run serving:publish            publish, or add assets a failed run left out
 *                                      (requires gh with write access)
 *   npm run serving:publish -- --check verify the published assets only
 */
import fs from "node:fs";
import crypto from "node:crypto";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { expand, packageAssets, readManifest, verifyPackage } from "../release/files";

const repository = "rewire-bio/rewire-benchmark-data";
const check = process.argv.includes("--check");
const receiptFile = fs.readdirSync("public/serving").filter((name) => /^catalogue-.+\.json$/.test(name)).sort().pop();
if (!receiptFile) throw new Error("No prepared release found; run npm run serving first");
const receipt = JSON.parse(fs.readFileSync(path.join("public/serving", receiptFile), "utf8"));
const file = path.join("public/serving", receipt.file);
const sha256 = (bytes: Buffer) => crypto.createHash("sha256").update(bytes).digest("hex");
if (sha256(fs.readFileSync(file)) !== receipt.sha256) throw new Error("Prepared file differs from its receipt");
const tag = `serving/${receipt.release_id}`;
const gh = (...args: string[]) => execFileSync("gh", args, { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"], maxBuffer: 64 * 1024 ** 2 });

// The website files go up with the prepared file, so check them first.
const manifest = readManifest();
if (manifest.release_id !== receipt.release_id) throw new Error(`website/manifest.json is for ${manifest.release_id}, not ${receipt.release_id}`);
if (!check) verifyPackage();
const assets = packageAssets(manifest);
// gh names an asset after its file, so stage each file under its asset name.
const staging = fs.mkdtempSync(path.join(os.tmpdir(), "release-assets-"));
process.on("exit", () => fs.rmSync(staging, { recursive: true, force: true }));
const staged = (names: string[]) => assets.filter(({ name }) => names.includes(name)).map(({ name, entry }) => {
  const target = path.join(staging, name);
  fs.copyFileSync(entry.source, target);
  return target;
});

let exists = true;
let publishedNames: string[] = [];
try { publishedNames = JSON.parse(gh("release", "view", tag, "--repo", repository, "--json", "assets")).assets.map((asset: { name: string }) => asset.name); } catch { exists = false; }
if (exists) {
  // Compare receipts rather than downloading the file. A published asset is never
  // replaced: the same generator must reproduce it exactly, and a later generator
  // leaves it in place until the next release.
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "serving-"));
  gh("release", "download", tag, "--repo", repository, "--pattern", receiptFile, "--dir", directory);
  const published = JSON.parse(fs.readFileSync(path.join(directory, receiptFile), "utf8"));
  fs.rmSync(directory, { recursive: true, force: true });
  if (published.sha256 === receipt.sha256) console.log(`${tag} already published and byte-identical (${receipt.sha256}).`);
  else if (published.generator_sha256 === receipt.generator_sha256)
    throw new Error(`Published ${receipt.file} (${published.sha256}) differs from this build (${receipt.sha256}) with the same generator; the build is not deterministic`);
  else console.log(`${tag} was published by generator ${published.generator_sha256}; this build's generator ${receipt.generator_sha256} differs, so the published asset stays.`);
  // Website files: a published one must have the listed bytes; a missing one is uploaded.
  const missing = assets.filter(({ name }) => !publishedNames.includes(name)).map(({ name }) => name);
  for (const { name, entry } of assets.filter(({ name }) => publishedNames.includes(name))) {
    gh("release", "download", tag, "--repo", repository, "--pattern", name, "--dir", staging, "--clobber");
    expand(fs.readFileSync(path.join(staging, name)), entry.sha256, `Published asset ${name}`, entry.bytes);
  }
  if (missing.length && check) throw new Error(`${tag} lacks ${missing.length} website files: ${missing.slice(0, 5).join(", ")}`);
  if (missing.length) {
    gh("release", "upload", tag, "--repo", repository, ...staged(missing));
    console.log(`Uploaded ${missing.length} website files that ${tag} lacked.`);
  }
  console.log(`${tag} holds all ${assets.length} website files with the listed bytes.`);
} else if (check) {
  throw new Error(`${tag} is not published`);
} else {
  gh("release", "create", tag, ...(process.env.RELEASE_TARGET_SHA ? ["--target", process.env.RELEASE_TARGET_SHA] : []), file, path.join("public/serving", receiptFile),
    ...staged(assets.map(({ name }) => name)), "--repo", repository,
    "--title", `Prepared release ${receipt.release_id}`,
    "--notes", `Prepared serving file and website files for release ${receipt.release_id}.\n\nsha256: ${receipt.sha256}\nserving contract: ${receipt.serving_contract_version}\ngenerator: ${receipt.generator_sha256}\nwebsite files: ${assets.length}, listed with their SHA-256 in website/manifest.json at the tagged commit`);
  console.log(`Published ${tag}: ${receipt.file} (${receipt.sha256}) and ${assets.length} website files.`);
}
console.log(`URL: https://github.com/${repository}/releases/download/${tag}/${receipt.file}`);
