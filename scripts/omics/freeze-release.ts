/** Freeze the release built in public/omics into data/omics/releases: the
 * receipt is the exact manifest bytes, and each manifest file is stored as
 * gzip (level 9, no timestamp). The previous release's files are removed and
 * its receipt is kept. Existing bytes are never overwritten. */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { gzipSync, gunzipSync } from "node:zlib";

const root = "data/omics/releases";
const manifestBytes = fs.readFileSync("public/omics/manifest.json");
const manifest = JSON.parse(manifestBytes.toString("utf8"));
const id: string = manifest.release_id;
const source = path.join("public/omics/releases", id);
const receipt = path.join(root, `${id}.json`);
const sha = (bytes: Buffer) => crypto.createHash("sha256").update(bytes).digest("hex");

if (fs.existsSync(receipt) && !fs.readFileSync(receipt).equals(manifestBytes))
  throw new Error(`A different receipt already exists for ${id}`);
fs.writeFileSync(receipt, manifestBytes);
const dir = path.join(root, id);
fs.mkdirSync(dir, { recursive: true });
for (const [name, digest] of Object.entries(manifest.files as Record<string, string>)) {
  const bytes = fs.readFileSync(path.join(source, name));
  if (sha(bytes) !== digest) throw new Error(`Checksum mismatch for ${name}`);
  const target = path.join(dir, `${name}.gz`);
  if (fs.existsSync(target)) {
    if (!gunzipSync(fs.readFileSync(target)).equals(bytes)) throw new Error(`Conflicting archive: ${target}`);
    continue;
  }
  const compressed = gzipSync(bytes, { level: 9 });
  if (!gunzipSync(compressed).equals(bytes)) throw new Error(`Round trip failed for ${name}`);
  fs.writeFileSync(target, compressed, { flag: "wx" });
}
for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
  if (entry.isDirectory() && entry.name !== id) fs.rmSync(path.join(root, entry.name), { recursive: true });
}
console.log(`Froze ${id}: ${Object.keys(manifest.files).length} files. Earlier releases keep their receipts only.`);
