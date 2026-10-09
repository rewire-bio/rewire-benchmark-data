/** Publish the knowledge-graph bundle as an immutable GitHub Release asset.
 * Tag `kg/<release_id>` holds `kg-<release_id>.tar.gz` (byte-reproducible, packed by
 * rdf-kg-mcp) and its manifest. An existing asset must be byte-identical; it is never replaced.
 *   npm run kg:publish            publish (requires gh with write access and uv)
 *   npm run kg:publish -- --check verify the published asset only
 */
import fs from "node:fs";
import crypto from "node:crypto";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";

const repository = "rewire-bio/rewire-benchmark-data";
const rdfKgMcp = process.env.RDF_KG_MCP ?? "git+https://github.com/rewire-bio/rdf-kg-mcp@v0.1.0";
const check = process.argv.includes("--check");
const manifestFile = "public/kg/manifest.json";
if (!fs.existsSync(manifestFile)) throw new Error("No knowledge-graph bundle found; run npm run kg:build first");
const manifest = JSON.parse(fs.readFileSync(manifestFile, "utf8"));
if (!manifest.files?.["inferred.nq"]) throw new Error("The bundle has no inferred graph; run npm run kg:build first");

const run = (command: string, ...args: string[]) =>
  execFileSync(command, args, { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
const sha256 = (file: string) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

const directory = fs.mkdtempSync(path.join(os.tmpdir(), "kg-"));
const name = `kg-${manifest.release_id}.tar.gz`;
const archive = path.join(directory, name);
run("uvx", "--from", rdfKgMcp, "rdf-kg-mcp", "pack", "public/kg", "-o", archive);
run("uvx", "--from", rdfKgMcp, "rdf-kg-mcp", "verify", archive);
const built = sha256(archive);
const tag = `kg/${manifest.release_id}`;
const gh = (...args: string[]) => run("gh", ...args);

let exists = true;
try { gh("release", "view", tag, "--repo", repository, "--json", "tagName"); } catch { exists = false; }
if (exists) {
  const download = path.join(directory, "published");
  gh("release", "download", tag, "--repo", repository, "--pattern", name, "--dir", download);
  const published = sha256(path.join(download, name));
  if (published !== built)
    throw new Error(`Published ${name} (${published}) differs from this build (${built}); releases are immutable`);
  console.log(`${tag} already published and byte-identical (${built}).`);
} else if (check) {
  throw new Error(`${tag} is not published`);
} else {
  const files = manifest.files;
  const notes = [
    `Knowledge-graph bundle for release ${manifest.release_id}: ${files["asserted.nq"].quads} asserted and ` +
      `${files["inferred.nq"].quads} inferred statements, SHACL validated.`,
    "",
    `sha256: ${built}`,
    "",
    "Serve it to Claude Code with [rdf-kg-mcp](https://github.com/rewire-bio/rdf-kg-mcp):",
    "",
    "```sh",
    `claude mcp add rewire-benchmarks -- uvx --from ${rdfKgMcp} rdf-kg-mcp serve ` +
      `https://github.com/${repository}/releases/download/${tag}/${name}`,
    "```",
  ].join("\n");
  gh("release", "create", tag, archive, manifestFile, "--repo", repository,
    "--title", `Knowledge graph ${manifest.release_id}`, "--notes", notes);
  console.log(`Published ${tag}: ${name} (${built}).`);
}
fs.rmSync(directory, { recursive: true, force: true });
console.log(`URL: https://github.com/${repository}/releases/download/${tag}/${name}`);
