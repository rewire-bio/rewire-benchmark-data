/** Publish the prepared release file as an immutable GitHub Release asset.
 * Tag `serving/<release_id>` holds `catalogue-<release_id>.sqlite` and its
 * receipt. An existing asset is never replaced. A build by the same generator
 * must be byte-identical to it.
 *   npm run serving:publish            publish (requires gh with write access)
 *   npm run serving:publish -- --check verify the published asset only
 */
import fs from "node:fs";
import crypto from "node:crypto";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";

const repository = "rewire-bio/rewire-benchmark-data";
const check = process.argv.includes("--check");
const receiptFile = fs.readdirSync("public/serving").filter((name) => /^catalogue-.+\.json$/.test(name)).sort().pop();
if (!receiptFile) throw new Error("No prepared release found; run npm run serving first");
const receipt = JSON.parse(fs.readFileSync(path.join("public/serving", receiptFile), "utf8"));
const file = path.join("public/serving", receipt.file);
const sha256 = (bytes: Buffer) => crypto.createHash("sha256").update(bytes).digest("hex");
if (sha256(fs.readFileSync(file)) !== receipt.sha256) throw new Error("Prepared file differs from its receipt");
const tag = `serving/${receipt.release_id}`;
const gh = (...args: string[]) => execFileSync("gh", args, { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });

let exists = true;
try { gh("release", "view", tag, "--repo", repository, "--json", "tagName"); } catch { exists = false; }
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
} else if (check) {
  throw new Error(`${tag} is not published`);
} else {
  gh("release", "create", tag, file, path.join("public/serving", receiptFile), "--repo", repository,
    "--title", `Prepared release ${receipt.release_id}`,
    "--notes", `Prepared serving file for release ${receipt.release_id}.\n\nsha256: ${receipt.sha256}\nserving contract: ${receipt.serving_contract_version}\ngenerator: ${receipt.generator_sha256}`);
  console.log(`Published ${tag}: ${receipt.file} (${receipt.sha256}).`);
}
console.log(`URL: https://github.com/${repository}/releases/download/${tag}/${receipt.file}`);
