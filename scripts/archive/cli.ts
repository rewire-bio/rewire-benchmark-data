/** npm run archive -- <command>
 *
 *   worklist   the fetch work list: sources, URLs, classes and hosts
 *   fetch      fetch every source that is not already held, and store it
 *   verify     recompute every cached object against the manifest
 *   status     sources total, stored, what is held but is not the artifact,
 *              failed by reason, and bytes held
 *   upload     put the cached objects in Cloudflare R2 (needs four secrets)
 *
 * fetch, verify and status need no credential and no secret, so they run on a
 * fork pull request. upload is the only command that needs one, and it is the
 * only one that fails without it.
 */
import { parseArgs } from "node:util";
import { checkManifest, readManifest } from "./manifest";
import { cacheContents, hasObject, readObject } from "./objects";
import { latestBySource, readReceipts } from "./receipts";
import { runFetch } from "./fetch";
import { uploadObjects } from "./upload";
import { readWorkList, summarise } from "../../shared/archive/worklist";
import { licenceClassifier } from "../licence/map";

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    root: { type: "string" },
    concurrency: { type: "string" },
    "delay-ms": { type: "string" },
    "max-bytes": { type: "string" },
    "timeout-ms": { type: "string" },
    limit: { type: "string" },
    "retry-failed": { type: "boolean" },
    "dry-run": { type: "boolean" },
    json: { type: "boolean" },
    quiet: { type: "boolean" },
  },
});

const root = values.root ?? ".";
const number = (name: string): number | undefined => {
  const raw = values[name as keyof typeof values];
  if (typeof raw !== "string") return undefined;
  const parsed = Number(raw);
  if (!Number.isFinite(parsed) || parsed <= 0) throw new Error(`--${name} must be a positive number`);
  return parsed;
};
const print = (value: unknown) => console.log(typeof value === "string" ? value : JSON.stringify(value, null, 2));
const mib = (bytes: number) => `${(bytes / 1024 / 1024).toFixed(1)} MiB`;

function worklist(): void {
  const summary = summarise(root);
  if (values.json) return print(summary);
  print(`sources                 ${summary.sources}`);
  print(`with a fetchable URL    ${summary.with_url}`);
  print(`DOI only, no URL        ${summary.doi_only}`);
  print(`neither URL nor DOI     ${summary.neither}`);
  print(`distinct URLs           ${summary.distinct_urls} (${summary.shared_urls} carried by more than one source)`);
  print(`carrying a DOI          ${summary.with_doi}`);
  print("");
  print("source class");
  for (const [name, count] of Object.entries(summary.by_class)) print(`  ${String(count).padStart(5)}  ${name}`);
  print("");
  print("host");
  for (const [name, count] of Object.entries(summary.by_host).slice(0, 25)) print(`  ${String(count).padStart(5)}  ${name}`);
  const rest = Object.entries(summary.by_host).length - 25;
  if (rest > 0) print(`  ${String(rest).padStart(5)}  further hosts`);
}

async function fetchCommand(): Promise<void> {
  const summary = await runFetch({
    root,
    concurrency: number("concurrency"),
    delayMs: number("delay-ms"),
    maxBytes: number("max-bytes"),
    requestTimeoutMs: number("timeout-ms"),
    limit: number("limit"),
    retryFailed: values["retry-failed"] ?? false,
    dryRun: values["dry-run"] ?? false,
    // The licence map decides the tier a new object is recorded at. Without
    // it every row would land at the private default, which is safe but says
    // nothing. A licence never decides whether the bytes are fetched.
    classify: licenceClassifier(root),
    log: values.quiet ? undefined : (line) => console.error(line),
  });
  print(summary);
}

function verify(): {
  objects: number;
  verified: number;
  missing: string[];
  corrupt: string[];
  unlisted: string[];
  problems: string[];
} {
  const { problems } = checkManifest(root);
  const manifest = readManifest(root);
  const missing: string[] = [];
  const corrupt: string[] = [];
  let verified = 0;
  for (const [key, row] of manifest) {
    if (!hasObject(key, root)) {
      missing.push(key);
      continue;
    }
    try {
      const bytes = readObject(key, root);
      if (bytes.length !== row.bytes) corrupt.push(key);
      else verified += 1;
    } catch {
      corrupt.push(key);
    }
  }
  const unlisted = cacheContents(root).keys.filter((key) => !manifest.has(key));
  return { objects: manifest.size, verified, missing, corrupt, unlisted, problems };
}

function status(): void {
  const { items, withoutUrl } = readWorkList(root);
  const latest = latestBySource(readReceipts(root));
  const manifest = readManifest(root);
  const cache = cacheContents(root);
  const failures: Record<string, number> = {};
  const notArtifactReasons: Record<string, number> = {};
  let stored = 0;
  let notArtifact = 0;
  let failed = 0;
  let expandedBytes = 0;
  let bytesMissing = 0;
  for (const item of items) {
    const receipt = latest.get(item.source_id);
    if (!receipt) continue;
    const reason = receipt.reason ?? "http_error";
    if (receipt.outcome === "stored") {
      // A receipt says a transfer happened. Only the cache says we still hold it.
      if (receipt.sha256 && hasObject(receipt.sha256, root)) stored += 1;
      else bytesMissing += 1;
    } else if (receipt.outcome === "not_artifact") {
      // Bytes we hold that are not the source. Counting these as stored is
      // what the 2026-11-17 pilot showed the archive overstating.
      notArtifact += 1;
      notArtifactReasons[reason] = (notArtifactReasons[reason] ?? 0) + 1;
    } else {
      failed += 1;
      failures[reason] = (failures[reason] ?? 0) + 1;
    }
  }
  for (const key of cache.keys) expandedBytes += manifest.get(key)?.bytes ?? 0;
  const summary = {
    sources: items.length + withoutUrl.length,
    with_url: items.length,
    stored,
    stored_but_bytes_missing: bytesMissing,
    not_artifact: notArtifact,
    failed,
    no_attempt_yet: items.length - stored - bytesMissing - notArtifact - failed,
    not_artifact_by_reason: Object.fromEntries(Object.entries(notArtifactReasons).sort((a, b) => b[1] - a[1])),
    failures_by_reason: Object.fromEntries(Object.entries(failures).sort((a, b) => b[1] - a[1])),
    manifest_rows: manifest.size,
    objects_in_cache: cache.keys.length,
    expanded_bytes: expandedBytes,
    compressed_bytes: cache.compressed_bytes,
  };
  if (values.json) return print(summary);
  print(`sources            ${summary.sources} (${summary.with_url} with a fetchable URL)`);
  print(`stored             ${summary.stored}`);
  print(`bytes missing      ${summary.stored_but_bytes_missing}`);
  print(`not the artifact   ${summary.not_artifact}`);
  for (const [reason, count] of Object.entries(summary.not_artifact_by_reason)) print(`  ${String(count).padStart(5)}  ${reason}`);
  print(`failed             ${summary.failed}`);
  print(`no attempt yet     ${summary.no_attempt_yet}`);
  for (const [reason, count] of Object.entries(summary.failures_by_reason)) print(`  ${String(count).padStart(5)}  ${reason}`);
  print(`manifest rows      ${summary.manifest_rows}`);
  print(`objects in cache   ${summary.objects_in_cache}`);
  print(`bytes held         ${mib(summary.expanded_bytes)} expanded, ${mib(summary.compressed_bytes)} on disk`);
}

async function main(): Promise<number> {
  switch (positionals[0]) {
    case "worklist":
      worklist();
      return 0;
    case "fetch":
      await fetchCommand();
      return 0;
    case "verify": {
      const result = verify();
      print(result);
      return result.missing.length || result.corrupt.length || result.unlisted.length || result.problems.length ? 1 : 0;
    }
    case "status":
      status();
      return 0;
    case "upload":
      print(await uploadObjects({ root, dryRun: values["dry-run"] ?? false }));
      return 0;
    default:
      print("Usage: npm run archive -- <worklist|fetch|verify|status|upload> [options]");
      return positionals[0] ? 1 : 0;
  }
}

main().then(
  (code) => {
    process.exitCode = code;
  },
  (error: unknown) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  },
);
