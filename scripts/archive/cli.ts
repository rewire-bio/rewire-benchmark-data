/** npm run archive -- <command>
 *
 *   worklist   the fetch work list: sources, URLs, classes and hosts
 *   fetch      fetch every source that is not already held, and store it
 *   verify     recompute every cached object against the manifest. A row at
 *              t5-no-store is expected to hold no bytes and is reported as
 *              removed, so a takedown leaves no standing failure
 *   status     sources total, stored, what is held but is not the artifact,
 *              failed by reason, and bytes held
 *   reclassify re-read every manifest row's licence against the map as it
 *              stands and the candidates on disk, and write back archive_tier,
 *              visibility and observed_licence. A row moving from public to
 *              restricted is reported apart and refused: that is a takedown
 *   publish    put the public cached objects on this repository's own release
 *              tags archive/objects-<0-f>, which needs no new credential
 *   upload     put the restricted cached objects in Cloudflare R2, which is the
 *              restricted backend (needs four secrets)
 *   pull       bring objects back down from R2 into a cache that has none,
 *              verified against the manifest key before anything is kept
 *              (needs the same four secrets)
 *
 * fetch, verify and status need no credential and no secret, so they run on a
 * fork pull request. publish writes to this repository, so it needs a token
 * with write access to it and nothing else: the gh CLI's own credential
 * locally, github.token in CI. upload and pull are the two that need the R2
 * secrets, and they are the two that fail without them.
 *
 * pull is what makes a measurement on a second machine possible. The cache is
 * gitignored, so until there was a way to rebuild it every figure this lane
 * published rested on one laptop holding bytes nobody else had.
 */
import fs from "node:fs";
import { parseArgs } from "node:util";
import { readManifest, verifyObjects } from "./manifest";
import { cacheContents, hasObject } from "./objects";
import { latestBySource, readReceipts } from "./receipts";
import { runFetch } from "./fetch";
import { uploadObjects } from "./upload";
import { pullObjects } from "./pull";
import { publishObjects } from "./publish";
import { reclassifyObjects } from "./reclassify";
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
    source: { type: "string", multiple: true },
    key: { type: "string", multiple: true },
    "sources-from": { type: "string" },
    "dry-run": { type: "boolean" },
    "no-mark": { type: "boolean" },
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

/** The whole check lives in ./manifest as verifyObjects(), so a test can call
 * it. A row at t5-no-store is reported as removed and does not fail the
 * command; bytes still held under one do. */
const verify = () => verifyObjects(root);

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

/** Publish the public objects as release assets of this repository. A dry run
 * prints what would go and creates nothing. --no-mark uploads without writing
 * the manifest, which is what a run beside a fetch has to do, because the
 * fetch owns the shard files while it is running. */
async function publish(): Promise<number> {
  const summary = await publishObjects({
    root,
    limit: number("limit"),
    dryRun: values["dry-run"] ?? false,
    mark: !(values["no-mark"] ?? false),
    log: values.quiet ? undefined : (line) => console.error(line),
  });
  if (values.json) print(summary);
  else {
    print(summary.dry_run ? "dry run: nothing was created or uploaded" : "publish");
    print(`manifest rows         ${summary.manifest_rows}`);
    print(`public rows           ${summary.public_rows}`);
    for (const [tier, count] of Object.entries(summary.public_by_tier).sort()) print(`  ${String(count).padStart(5)}  ${tier}`);
    print(`public bytes          ${mib(summary.public_bytes)} expanded, ${mib(summary.public_compressed_bytes)} on disk`);
    print(`refused, not public   ${summary.refused}`);
    for (const [tier, count] of Object.entries(summary.refused_by_tier).sort()) print(`  ${String(count).padStart(5)}  ${tier}`);
    print(`public, no bytes held ${summary.public_not_in_cache}`);
    print(`considered            ${summary.considered}`);
    print(`already an asset      ${summary.already_present}`);
    print(summary.dry_run ? `would upload          ${summary.urls.length}` : `uploaded              ${summary.uploaded}`);
    print(`tags that exist       ${summary.tags_present.join(", ") || "none"}`);
    print(summary.dry_run ? `tags to create        ${summary.tags_created.join(", ") || "none"}` : `tags created          ${summary.tags_created.join(", ") || "none"}`);
    print(`manifest rows marked  ${summary.marked}`);
    if (summary.failed.length) {
      print(`failed                ${summary.failed.length}`);
      for (const failure of summary.failed.slice(0, 10)) print(`  ${failure.key} ${failure.message}`);
    }
  }
  return summary.failed.length ? 1 : 0;
}

/** Re-read every row's licence and write the three columns a licence decides.
 * Offline and credential free. A dry run reports and writes nothing; a real
 * run with any public-to-restricted move writes nothing either and says so. */
async function reclassify(): Promise<number> {
  const summary = await reclassifyObjects({
    root,
    dryRun: values["dry-run"] ?? false,
    log: values.quiet ? undefined : (line) => console.error(line),
  });
  if (values.json) print(summary);
  else {
    print(summary.dry_run ? "dry run: no manifest row was written" : "reclassify");
    print(`manifest rows         ${summary.manifest_rows}`);
    print(`skipped, t5-no-store  ${summary.skipped_removed}`);
    print(`no evidence, unmoved  ${summary.unevidenced}`);
    print("tier before");
    for (const [tier, count] of Object.entries(summary.before)) print(`  ${String(count).padStart(5)}  ${tier}`);
    print("tier after");
    for (const [tier, count] of Object.entries(summary.after)) print(`  ${String(count).padStart(5)}  ${tier}`);
    print(`publishable before    ${summary.publishable_before}`);
    print(`publishable after     ${summary.publishable_after}`);
    print(`rows moving           ${summary.moves.length}`);
    for (const [pair, count] of Object.entries(summary.moves_by_tier)) print(`  ${String(count).padStart(5)}  ${pair}`);
    print(`rows written          ${summary.written}`);
    print("");
    print(`tighter, still public ${summary.tightening.length}`);
    if (summary.tightening.length) {
      print("Not a takedown and not refused. The bytes may already be a release asset carrying the");
      print("old tier, so the tags want rereading after this run.");
      for (const move of summary.tightening) print(`  ${move.sha256} ${move.from} to ${move.to}, store ${move.store}`);
    }
    print("");
    print(`public to restricted  ${summary.restrictive.length}`);
    if (summary.restrictive.length) {
      print("These rows are a takedown, not a reclassification. Nothing was written. Their bytes may");
      print("already be a release asset, so each one goes down the takedown path in");
      print("docs/source-preservation.md, which records who asked and why.");
      for (const move of summary.restrictive)
        print(`  ${move.sha256} ${move.from} to ${move.to}, store ${move.store}, sources ${move.source_ids.join(" ")}`);
    }
  }
  return summary.restrictive.length ? 1 : 0;
}

/** Bring objects down from R2 into the cache. Resumable and idempotent: an
 * object already held and verifying is neither fetched nor written over, so a
 * second run makes no request. --dry-run reports the selection and needs no
 * credential. */
async function pull(): Promise<number> {
  const fromFile = values["sources-from"]
    ? fs
        .readFileSync(values["sources-from"], "utf8")
        .split("\n")
        .map((line) => line.trim())
        .filter((line) => line !== "" && !line.startsWith("#"))
    : [];
  const summary = await pullObjects({
    root,
    keys: values.key,
    sources: [...new Set([...(values.source ?? []), ...fromFile])],
    limit: number("limit"),
    dryRun: values["dry-run"] ?? false,
    log: values.quiet ? undefined : (line) => console.error(line),
  });
  if (values.json) print(summary);
  else {
    print(summary.dry_run ? "dry run: nothing was fetched or written" : "pull");
    print(`manifest rows         ${summary.manifest_rows}`);
    print(`matched the filter    ${summary.matched}`);
    print(`refused, t5-no-store  ${summary.removed}`);
    print(`selected              ${summary.selected} (${summary.selected_restricted} restricted, ${summary.selected_public} public)`);
    print(`already held          ${summary.already_held}`);
    print(`held back by --limit  ${summary.held_back_by_limit}`);
    print(summary.dry_run ? `would fetch           ${summary.selected - summary.already_held - summary.held_back_by_limit}` : `downloaded            ${summary.downloaded}`);
    if (!summary.dry_run) print(`bytes written         ${mib(summary.expanded_bytes)} expanded, ${mib(summary.compressed_bytes)} on disk`);
    if (summary.failed.length) {
      print(`failed                ${summary.failed.length}`);
      for (const failure of summary.failed.slice(0, 10)) print(`  ${failure.key} ${failure.status ?? "no status"} ${failure.message}`);
    }
  }
  return summary.failed.length ? 1 : 0;
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
    case "reclassify":
      return await reclassify();
    case "publish":
      return await publish();
    case "upload":
      print(await uploadObjects({ root, dryRun: values["dry-run"] ?? false }));
      return 0;
    case "pull":
      return await pull();
    default:
      print(
        "Usage: npm run archive -- <worklist|fetch|verify|status|reclassify|publish|upload|pull> [options]\n" +
          "       pull takes --source <id> (repeatable), --key <sha256> (repeatable), --sources-from <file>, --limit, --dry-run",
      );
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
