/** The layer registry and its sanity gate, ADR 0002 step 4.
 *
 * Usage: npm run layers -- build      generate the registry from the manifest
 *        npm run layers -- check      regenerate and report any difference
 *        npm run layers -- coverage   the per-source table and its identity
 *        npm run layers -- surface    the extraction surface, in numbers
 *        npm run layers -- show <id>  the layers a source or an object has
 *
 * `build` is the only command that writes, and it writes two generated files
 * under data/omics/layers/ and nothing else. It touches no record, no
 * vocabulary and no manifest row: the object store and the derivation belong
 * to the archive lane, and this reads them.
 *
 * Every command is offline, credential free and calls no model.
 */
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { readManifest } from "../../archive/manifest";
import { hasObject, readObject } from "../../archive/objects";
import { latestBySource, readReceipts } from "../../archive/receipts";
import {
  buildRegistry,
  coverageOf,
  layerText,
  layersForObject,
  layersForSource,
  readRegistry,
  readUnsupported,
  registryPath,
  serialiseRegistry,
  serialiseUnsupported,
  thresholds,
  unsupportedPath,
  writeRegistry,
  writeUnsupported,
  type CoverageResult,
  type LayerRecord,
  type ReceiptFact,
} from "../../../shared/omics/layers/index";
import { coverageBuckets } from "../../../shared/omics/layers/types";

const SOURCES = "data/entities/sources.jsonl";

function sourceIds(root: string): string[] {
  const file = path.join(root, SOURCES);
  return fs
    .readFileSync(file, "utf8")
    .split("\n")
    .filter((line) => line.trim())
    .map((line) => (JSON.parse(line) as { id: string }).id);
}

function receiptFacts(root: string): Map<string, ReceiptFact> {
  const latest = latestBySource(readReceipts(root));
  const facts = new Map<string, ReceiptFact>();
  for (const [sourceId, receipt] of latest)
    facts.set(sourceId, {
      source_id: sourceId,
      outcome: receipt.outcome,
      sha256: receipt.sha256,
      reason: receipt.reason,
      source_class: receipt.source_class,
    });
  return facts;
}

function generate(root: string, quiet: boolean): ReturnType<typeof buildRegistry> {
  const manifest = readManifest(root);
  const total = manifest.size;
  return buildRegistry(
    manifest.values(),
    (sha256) => {
      if (!hasObject(sha256, root)) throw new Error("the bytes are not in the object cache");
      return readObject(sha256, root);
    },
    (_sha256, done) => {
      if (!quiet && done % 100 === 0) process.stderr.write(`  ${done} of ${total} objects\n`);
    },
  );
}

function build(root: string): number {
  const result = generate(root, false);
  writeRegistry(result.records, root);
  writeUnsupported(result.unsupported, root);
  console.log(`layers           ${result.records.length}`);
  console.log(`objects unread   ${result.unreadable.length}`);
  console.log(`no normaliser    ${result.unsupported.length}`);
  for (const verdict of ["pass", "suspect", "fail"] as const)
    console.log(`sanity ${verdict.padEnd(10)}${result.records.filter((record) => record.sanity === verdict).length}`);
  console.log(`wrote ${registryPath(root)}`);
  console.log(`wrote ${unsupportedPath(root)}`);
  return result.unreadable.length ? 1 : 0;
}

/** Regenerate in memory and compare with the committed file. This is the
 * no-op test as a command: an unchanged store must produce the same bytes. */
function check(root: string): number {
  const result = generate(root, false);
  const problems: string[] = [];
  const onDisk = fs.existsSync(registryPath(root)) ? fs.readFileSync(registryPath(root), "utf8") : "";
  if (serialiseRegistry(result.records) !== onDisk) problems.push("data/omics/layers/registry.jsonl is not what the store produces");
  const unsupportedOnDisk = fs.existsSync(unsupportedPath(root)) ? fs.readFileSync(unsupportedPath(root), "utf8") : "";
  if (serialiseUnsupported(result.unsupported) !== unsupportedOnDisk)
    problems.push("data/omics/layers/unsupported.jsonl is not what the store produces");
  for (const problem of result.unreadable) problems.push(`${problem.object_sha256}: ${problem.reason}`);
  for (const problem of problems) console.error(problem);
  console.log(problems.length ? `${problems.length} problems` : `${result.records.length} layers reproduce`);
  return problems.length ? 1 : 0;
}

function coverage(root: string): CoverageResult {
  return coverageOf(sourceIds(root), receiptFacts(root), readRegistry(root), readUnsupported(root));
}

const pad = (value: string | number, width: number): string => String(value).padStart(width);

function coverageTable(root: string): number {
  const result = coverage(root);
  const { tally } = result;
  console.log("bucket             sources   characters");
  for (const bucket of coverageBuckets) {
    const rows = result.rows.filter((row) => row.bucket === bucket);
    const characters = rows.reduce((total, row) => total + row.characters, 0);
    console.log(`${bucket.padEnd(18)}${pad(tally.buckets[bucket], 7)}   ${pad(characters.toLocaleString("en-GB"), 12)}`);
  }
  const sum = coverageBuckets.reduce((total, bucket) => total + tally.buckets[bucket], 0);
  console.log(`${"total".padEnd(18)}${pad(sum, 7)}   ${pad(tally.characters.toLocaleString("en-GB"), 12)}`);
  console.log(`\nthe character column counts a shared layer once per source. Counted once, it is ${tally.distinct_characters.toLocaleString("en-GB")} over ${tally.distinct_layers} layers.`);
  console.log(`\nidentity: ${coverageBuckets.map((bucket) => tally.buckets[bucket]).join(" + ")} = ${sum}, sources ${tally.sources}`);
  for (const problem of result.problems) console.error(problem);
  return result.problems.length ? 1 : 0;
}

function surface(root: string): number {
  const result = coverage(root);
  const { tally } = result;
  const usableRows = result.rows.filter((row) => row.bucket === "layer_pass" || row.bucket === "layer_suspect");
  console.log(`sources                 ${pad(tally.sources, 8)}`);
  console.log(`usable layer            ${pad(usableRows.length, 8)}  (${tally.buckets.layer_pass} pass, ${tally.buckets.layer_suspect} suspect)`);
  console.log(`characters, distinct    ${pad(tally.distinct_characters.toLocaleString("en-GB"), 8)}  over ${tally.distinct_layers} layers: the text that exists`);
  console.log(`characters, per source  ${pad(tally.characters.toLocaleString("en-GB"), 8)}  a layer cited by two sources counted twice: the reading`);
  const lengths = usableRows.map((row) => row.characters).sort((a, b) => a - b);
  if (lengths.length) {
    const at = (share: number): number => lengths[Math.min(lengths.length - 1, Math.floor(share * lengths.length))];
    console.log(`characters per source   min ${at(0)}, median ${at(0.5)}, p95 ${at(0.95)}, max ${lengths[lengths.length - 1]}`);
  }
  console.log("\nsource class          sources   usable   characters");
  for (const [name, counts] of Object.entries(tally.by_class).sort((a, b) => b[1].usable - a[1].usable))
    console.log(`${name.padEnd(20)}${pad(counts.sources, 8)}${pad(counts.usable, 9)}   ${pad(counts.characters.toLocaleString("en-GB"), 12)}`);

  console.log("\nnot extractable without new work");
  const blocked = result.rows.filter((row) => !["layer_pass", "layer_suspect"].includes(row.bucket));
  const byWork = new Map<string, number>();
  for (const row of blocked) byWork.set(workFor(row.bucket, row.detail), (byWork.get(workFor(row.bucket, row.detail)) ?? 0) + 1);
  for (const [work, count] of [...byWork].sort((a, b) => b[1] - a[1])) console.log(`${pad(count, 6)}  ${work}`);
  console.log(`${pad(blocked.length, 6)}  total`);
  return 0;
}

/** What it would take to make a source extractable. One line per class of
 * obstacle, and nothing speculative: each names the lane that owns the work.
 */
function workFor(bucket: string, detail: string): string {
  if (bucket === "no_normaliser") {
    if (detail.includes("did not expand")) return "a repair of the stored bytes, because the office package will not open";
    if (detail.includes("office presentation package")) return "a slide normaliser, which nothing in the store needs yet";
    if (detail.includes("opendocument package")) return "an opendocument normaliser, which nothing in the store needs yet";
    if (detail.includes("office package")) return "a main part this office package does not declare, so no normaliser can claim it";
    if (detail.includes("legacy office binary")) return "a reader for the pre-2007 office binary formats";
    if (detail.includes("raster image")) return "optical character recognition, which no layer makes verifiable";
    return "a normaliser for a format nothing here reads";
  }
  if (bucket === "not_the_artifact") return "a second capture route for the host that served a page instead of the source, which is the archive lane";
  if (bucket === "no_capture") return "a rescue wave against the host, which is the archive lane";
  if (bucket === "layer_fail") return "a rebuild of the layer, because the one the store holds is unusable";
  return "unclassified";
}

function show(root: string, id: string): number {
  const records: LayerRecord[] = /^[a-f0-9]{64}$/.test(id) ? layersForObject(id, root) : layersForSource(id, root);
  if (!records.length) {
    console.log(`no layer for ${id}`);
    return 1;
  }
  for (const record of records) {
    console.log(`${record.layer_sha256}  ${record.sanity.padEnd(8)}${record.normaliser.padEnd(28)}${record.metrics.characters} characters`);
    if (record.container_path) console.log(`  in ${record.object_sha256} at ${record.container_path}`);
    for (const reason of record.sanity_reasons) console.log(`  ${reason}`);
  }
  const first = records[0];
  const text = layerText(first, root);
  console.log(`\nfirst 300 characters of ${first.layer_sha256}:`);
  console.log([...text].slice(0, 300).join(""));
  return 0;
}

function printThresholds(): number {
  console.log("sanity thresholds, each set from the measured distribution in shared/omics/layers/sanity.ts");
  for (const [name, value] of Object.entries(thresholds)) console.log(`  ${name.padEnd(22)}${value}`);
  return 0;
}

function main(argv: string[]): number {
  const root = process.cwd();
  const [command, ...rest] = argv;
  if (command === "build") return build(root);
  if (command === "check") return check(root);
  if (command === "coverage") return coverageTable(root);
  if (command === "surface") return surface(root);
  if (command === "thresholds") return printThresholds();
  if (command === "show" && rest[0]) return show(root, rest[0]);
  console.error(
    "usage: npm run layers -- build | check | coverage | surface | thresholds\n       npm run layers -- show <source id or object sha256>",
  );
  return 2;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  process.exit(main(process.argv.slice(2)));
}
