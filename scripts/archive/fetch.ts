/** The fetcher.
 *
 * Takes the source records as its work list, fetches each source through the
 * route chain, stores the bytes in the content-addressed cache, writes a
 * manifest row and writes a receipt per source. It is resumable and
 * idempotent: a source whose latest receipt says stored, and whose object the
 * cache still verifies, is skipped, so a second run writes nothing new.
 *
 * A 200 is not a success. The route chain ends only when the body is the
 * artifact, which checkArtifact in shared/archive/artifact.ts decides from
 * the bytes; otherwise the remaining routes run and the body is kept with the
 * not_artifact outcome. The pilot that forced this is described there.
 *
 * Politeness. Requests to one host are serialised with a minimum gap. 429,
 * 503 and bioRxiv's 1015 are backed off once, honouring Retry-After. After a
 * few consecutive backoffs a host is stopped for the run and its remaining
 * sources are left without receipts, so the next run picks them up rather than
 * the fetcher hammering a host that is blocking it.
 *
 * Interrupting the run is safe at any point. Bytes land through a rename, a
 * manifest shard is rewritten through a rename, and the receipt is appended
 * last, so the worst a crash costs is one repeated transfer.
 */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { adoptFile, cacheRoot, hasObject } from "./objects";
import { readManifest, upsertRow } from "./manifest";
import { appendReceipt, latestBySource, readReceipts } from "./receipts";
import { routeChain, type RouteInput } from "./routes";
import { groupByUrl, readWorkList, type WorkItem } from "../../shared/archive/worklist";
import { checkArtifact, type ArtifactCheck } from "../../shared/archive/artifact";
import { hasPdftotext } from "../../shared/archive/layers/pdf";
import {
  defaultArchiveTier,
  isRemoved,
  mediaTypeOf,
  utcNow,
  visibilityOf,
  type FetchReceipt,
  type LicenceClassifier,
  type Outcome,
  type Reason,
  type Route,
  type RouteAttempt,
} from "../../shared/archive/schema";

export const userAgent = "rewire-benchmark-data archive fetcher (+https://rewire.it)";

/** GitHub allows an anonymous client about 60 requests an hour and an
 * authenticated one about 5,000. Three fetch passes were stopped by that
 * quota, so a token is sent to GitHub's own hosts and nowhere else. The Fetch
 * standard drops Authorization on a cross-origin redirect, which is what keeps
 * it from reaching a third party when GitHub redirects a download. The token
 * is read once, never logged and never written to a receipt. */
const githubHosts = new Set([
  "github.com",
  "api.github.com",
  "raw.githubusercontent.com",
  "gist.githubusercontent.com",
  "objects.githubusercontent.com",
]);

let cachedGithubToken: string | null | undefined;
function githubToken(): string | null {
  if (cachedGithubToken !== undefined) return cachedGithubToken;
  const fromEnv = process.env.GITHUB_TOKEN ?? process.env.GH_TOKEN;
  if (fromEnv) return (cachedGithubToken = fromEnv);
  try {
    const { execFileSync } = require("node:child_process") as typeof import("node:child_process");
    const out = execFileSync("gh", ["auth", "token"], { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
    return (cachedGithubToken = out || null);
  } catch {
    return (cachedGithubToken = null);
  }
}

/** The headers for one request. Authorization is added only for a GitHub host. */
export function requestHeaders(url: string, accept: string): Record<string, string> {
  const headers: Record<string, string> = { "User-Agent": userAgent, Accept: accept };
  let host: string;
  try {
    host = new URL(url).hostname;
  } catch {
    return headers;
  }
  if (!githubHosts.has(host)) return headers;
  const token = githubToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

export interface FetchOptions {
  root?: string;
  /** How many hosts are in flight at once. One request per host either way. */
  concurrency?: number;
  /** The minimum gap between two requests to the same host, milliseconds. */
  delayMs?: number;
  /** Refuse a body larger than this. The 2026-09-19 audit found artifacts
   * above any sensible per-request ceiling, and they are recorded, not fetched
   * in the same pass. */
  maxBytes?: number;
  requestTimeoutMs?: number;
  /** Consecutive backoffs on one host before it is stopped for this run. */
  hostBackoffLimit?: number;
  /** Stop after this many URL groups. Used for a pilot, not the full run. */
  limit?: number;
  /** Try sources whose latest receipt is a failure again. */
  retryFailed?: boolean;
  /** Fetch as usual and write nothing: no object, no manifest row, no
   * receipt. It is not a way to preview the run without touching the hosts.
   * Every transfer still happens and the body is discarded, so a dry run over
   * the whole work list costs the hosts exactly what a real run costs them.
   * Use --limit to see what a few URLs return. */
  dryRun?: boolean;
  /** The licence work supplies this. Without it every object is t4-private. */
  classify?: LicenceClassifier;
  /** Override the pdftotext probe the artifact check uses. Without pdftotext
   * a PDF produces no text layer, so its length is not measured and it is
   * never called a stub for that. */
  pdftotext?: boolean;
  log?: (line: string) => void;
}

export interface FetchSummary {
  planned: number;
  /** Sources whose bytes the cache still holds. */
  skipped_held: number;
  /** Sources whose last attempt failed and which --retry-failed would pick
   * up. They hold no bytes, so they are counted apart from the held ones. */
  skipped_failed: number;
  /** Sources holding bytes that are not the artifact. --retry-failed picks
   * them up too, because a cookie wall or a missing Unpaywall address is a
   * condition of the run and not a property of the source. */
  skipped_not_artifact: number;
  /** Sources a manifest row at t5-no-store answers for: an object removed on
   * a rights holder's request, or a recorded decision to keep no copy.
   * Counted on their own line and never as held: the archive holds nothing
   * for them and is not going to fetch it again. --retry-failed does not
   * reach them. */
  skipped_removed: number;
  attempted: number;
  stored: number;
  /** Sources where every route returned something other than the artifact. */
  not_artifact: number;
  failed: number;
  objects_written: number;
  bytes_stored: number;
  failures_by_reason: Record<string, number>;
  not_artifact_by_reason: Record<string, number>;
  hosts_stopped: string[];
  sources_left_for_next_run: number;
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/** One request at a time per host, with a minimum gap and a backoff count.
 *
 * hold() is how a backoff reaches the whole host rather than the one worker
 * that saw it. A worker that reads Retry-After holds the lane for that long,
 * so every other request to the host waits it out too. The gap after a
 * request never shortens a hold already in place.
 */
class HostLane {
  private next = 0;
  private chain: Promise<unknown> = Promise.resolve();
  consecutiveBackoffs = 0;
  stopped = false;
  constructor(private readonly delayMs: number) {}

  /** Keep the whole lane quiet for at least this long. */
  hold(ms: number): void {
    this.next = Math.max(this.next, Date.now() + ms);
  }

  run<T>(work: () => Promise<T>): Promise<T> {
    const started = this.chain.then(async () => {
      const wait = this.next - Date.now();
      if (wait > 0) await sleep(wait);
      try {
        return await work();
      } finally {
        this.next = Math.max(this.next, Date.now() + this.delayMs);
      }
    });
    this.chain = started.catch(() => undefined);
    return started;
  }
}

const retryAfterMs = (header: string | null): number | null => {
  if (!header) return null;
  const seconds = Number(header);
  if (Number.isFinite(seconds) && seconds >= 0) return Math.min(seconds, 120) * 1000;
  const date = Date.parse(header);
  return Number.isFinite(date) ? Math.max(0, Math.min(date - Date.now(), 120_000)) : null;
};

/** The two statuses that mean "come back later". Cloudflare's 1015 rate limit,
 * which bioRxiv sits behind, is served as a 429 with the code in the body, so
 * it is already covered here and needs no status of its own. */
const isBackoff = (status: number) => status === 429 || status === 503;

interface Downloaded {
  status: number;
  final_url: string;
  content_type: string | null;
  bytes: number;
  sha256: string;
  file: string;
}

export class Fetcher {
  private readonly lanes = new Map<string, HostLane>();
  readonly stoppedHosts = new Set<string>();

  constructor(private readonly options: Required<Pick<FetchOptions, "delayMs" | "maxBytes" | "requestTimeoutMs" | "hostBackoffLimit">> & { root: string }) {}

  private lane(host: string): HostLane {
    const held = this.lanes.get(host);
    if (held) return held;
    const lane = new HostLane(this.options.delayMs);
    this.lanes.set(host, lane);
    return lane;
  }

  private hostOf(url: string): string {
    try {
      return new URL(url).host.toLowerCase();
    } catch {
      return "";
    }
  }

  /** A polite request. The body is read inside the host's lane, so two
   * transfers to one host never overlap and the gap is measured from the end
   * of the last one. Backs off once on 429, 503 or 1015, then gives up and
   * counts the backoff against the host. */
  private async request<T>(url: string, accept: string, consume: (response: Response) => Promise<T>): Promise<T | { transport: Reason }> {
    const host = this.hostOf(url);
    if (!host) return { transport: "unsupported_url" };
    const lane = this.lane(host);
    if (lane.stopped) return { transport: "host_stopped" };
    for (let attempt = 0; attempt < 2; attempt += 1) {
      const outcome = await lane.run(async (): Promise<{ held: T } | { backoff: number | null } | { failed: Reason }> => {
        let response: Response;
        try {
          response = await fetch(url, {
            redirect: "follow",
            headers: requestHeaders(url, accept),
            signal: AbortSignal.timeout(this.options.requestTimeoutMs),
          });
        } catch (error) {
          return { failed: error instanceof Error && error.name === "TimeoutError" ? "timeout" : "network_error" };
        }
        if (isBackoff(response.status)) {
          await response.body?.cancel().catch(() => undefined);
          const wait = retryAfterMs(response.headers.get("retry-after"));
          // Hold the lane from inside it, so a second worker on this host
          // cannot slip a request in while this one waits out Retry-After.
          lane.hold(wait ?? this.options.delayMs * 2);
          return { backoff: wait };
        }
        return { held: await consume(response) };
      });
      if ("failed" in outcome) return { transport: outcome.failed };
      if ("held" in outcome) {
        lane.consecutiveBackoffs = 0;
        return outcome.held;
      }
      lane.consecutiveBackoffs += 1;
      if (lane.consecutiveBackoffs >= this.options.hostBackoffLimit) {
        lane.stopped = true;
        this.stoppedHosts.add(host);
        return { transport: "host_stopped" };
      }
      if (attempt === 0) await sleep(outcome.backoff ?? this.options.delayMs * 2);
    }
    return { transport: "rate_limited" };
  }

  /** A JSON GET for the route resolvers, through the same politeness. */
  getJson = async (url: string): Promise<{ status: number; body: unknown | null; transport?: Reason }> => {
    const result = await this.request(url, "application/json", async (response) => {
      if (!response.ok) {
        await response.body?.cancel().catch(() => undefined);
        return { status: response.status, body: null };
      }
      try {
        return { status: response.status, body: (await response.json()) as unknown };
      } catch {
        return { status: response.status, body: null };
      }
    });
    return "transport" in result ? { status: 0, body: null, transport: result.transport } : result;
  };

  /** Stream a body to a temporary file, hashing as it goes, and refuse it the
   * moment it passes the ceiling rather than after holding it all. */
  async download(url: string): Promise<Downloaded | { error: Reason; status: number | null }> {
    const result = await this.request(url, "*/*", (response) => this.readBody(url, response));
    return "transport" in result ? { error: result.transport, status: null } : result;
  }

  private async readBody(url: string, response: Response): Promise<Downloaded | { error: Reason; status: number | null }> {
    if (!response.ok) {
      await response.body?.cancel().catch(() => undefined);
      return { error: response.status === 404 ? "not_found" : "http_error", status: response.status };
    }
    if (!response.body) return { error: "empty_body", status: response.status };
    const temporary = path.join(cacheRoot(this.options.root), "incoming", `${process.pid}-${crypto.randomBytes(8).toString("hex")}`);
    fs.mkdirSync(path.dirname(temporary), { recursive: true });
    const hash = crypto.createHash("sha256");
    const handle = fs.openSync(temporary, "w");
    let bytes = 0;
    try {
      for await (const chunk of response.body as unknown as AsyncIterable<Uint8Array>) {
        bytes += chunk.length;
        if (bytes > this.options.maxBytes) {
          fs.closeSync(handle);
          fs.rmSync(temporary, { force: true });
          return { error: "too_large", status: response.status };
        }
        hash.update(chunk);
        fs.writeSync(handle, chunk);
      }
      fs.closeSync(handle);
    } catch {
      try {
        fs.closeSync(handle);
      } catch {
        /* already closed */
      }
      fs.rmSync(temporary, { force: true });
      return { error: "network_error", status: response.status };
    }
    if (!bytes) {
      fs.rmSync(temporary, { force: true });
      return { error: "empty_body", status: response.status };
    }
    return {
      status: response.status,
      final_url: response.url || url,
      content_type: response.headers.get("content-type"),
      bytes,
      sha256: hash.digest("hex"),
      file: temporary,
    };
  }
}

/** The sources every removed manifest row answers for.
 *
 * A takedown marks the row and deletes the bytes. The receipt stays, because
 * it is an observation of a transfer that happened, so a source whose object
 * was removed looks exactly like a source whose cache copy went missing.
 * Without this set the next fetch would transfer those bytes again and cache
 * them again, which is the hole determination 4's path left open.
 *
 * Every row at t5-no-store counts, not only one carrying removed_at. A
 * takedown always writes both, but t5-no-store is also the tier for a
 * recorded decision not to keep a copy, and fetching those bytes again would
 * undo that decision just as surely. */
export function removedSources(root: string): Set<string> {
  const removed = new Set<string>();
  for (const row of readManifest(root).values()) {
    if (row.archive_tier !== "t5-no-store" && !isRemoved(row)) continue;
    for (const sourceId of row.source_ids) removed.add(sourceId);
  }
  return removed;
}

/** Which sources still need a transfer, and why the others do not. */
export function planRun(
  root: string,
  retryFailed: boolean,
): { todo: WorkItem[]; heldSources: number; failedSources: number; notArtifactSources: number; removedSources: number; items: WorkItem[] } {
  const { items } = readWorkList(root);
  const latest = latestBySource(readReceipts(root));
  const removed = removedSources(root);
  const todo: WorkItem[] = [];
  let held = 0;
  let failed = 0;
  let notArtifact = 0;
  let wasRemoved = 0;
  for (const item of items) {
    const receipt = latest.get(item.source_id);
    // Asked first, and before --retry-failed is consulted. A removed source is
    // not held, not failed and never to be attempted: somebody asked us to
    // delete those bytes, so re-fetching them would undo a takedown.
    if (removed.has(item.source_id)) {
      wasRemoved += 1;
      continue;
    }
    if (receipt?.outcome === "stored" && receipt.sha256 && hasObject(receipt.sha256, root)) {
      held += 1;
      continue;
    }
    // A source whose last attempt failed holds no bytes. Counting it as held
    // would read as progress, so it is counted on its own line. A source
    // holding a cookie wall does hold bytes and is still not held, so it gets
    // a line of its own too.
    if (receipt?.outcome === "not_artifact" && !retryFailed) {
      notArtifact += 1;
      continue;
    }
    if (receipt?.outcome === "failed" && !retryFailed) {
      failed += 1;
      continue;
    }
    todo.push(item);
  }
  return { todo, heldSources: held, failedSources: failed, notArtifactSources: notArtifact, removedSources: wasRemoved, items };
}

/** Why a source produced no bytes.
 *
 * paywalled_not_held is only reached when the source carries a DOI and each of
 * the three fallbacks gave a conclusive answer: no open copy, nothing found,
 * or a resolved URL the host refused. A fallback that was skipped, or that
 * failed in transport, is not an answer, so the direct route's reason stands
 * and the source is honestly recorded as not yet reached.
 */
export function failureReason(doi: string | null, tried: RouteAttempt[]): Reason {
  const direct = tried.find((attempt) => attempt.route === "direct");
  const fallbacks = tried.filter((attempt) => attempt.route !== "direct");
  const conclusive = (attempt: RouteAttempt) =>
    attempt.reason === "no_open_copy" ||
    attempt.reason === "not_found" ||
    (attempt.url !== null && attempt.status !== null && attempt.status >= 400 && attempt.status < 500);
  if (doi && fallbacks.length === 3 && fallbacks.every(conclusive)) return "paywalled_not_held";
  return direct?.reason ?? "http_error";
}

/** Fetch one URL through the route chain and write what it produced.
 *
 * A 200 ends the chain only when the body is the artifact. checkArtifact in
 * shared/archive/artifact.ts decides that, and when it says no the body is
 * held as a candidate and the remaining routes run anyway. The first such
 * body is the one kept, because it is what the record's own URL serves and
 * therefore the honest thing to hold; a later one is discarded as it arrives.
 */
async function fetchGroup(
  fetcher: Fetcher,
  group: WorkItem[],
  options: Required<Pick<FetchOptions, "root">> & { classify?: LicenceClassifier; dryRun: boolean; pdftotext: boolean },
): Promise<{ deferred: boolean; receipts: FetchReceipt[]; objectWritten: boolean; bytes: number }> {
  const lead = group[0];
  // Sources sharing a URL share one transfer, and any DOI among them resolves
  // the same three fallbacks. Taking the first one in the group rather than
  // the lead's keeps the route chain and the artifact check agreed on whether
  // there is a DOI to follow.
  const doi = group.find((item) => item.doi !== null)?.doi ?? null;
  const tried: RouteAttempt[] = [];
  let downloaded: Downloaded | null = null;
  let winner: Route | null = null;
  let candidate: { got: Downloaded; route: Route; check: ArtifactCheck } | null = null;
  let lastReason: Reason | null = null;
  let hostStopped = false;

  for (const step of routeChain) {
    const input: RouteInput = { url: lead.url, doi, getJson: fetcher.getJson };
    const resolved = await step.resolve(input);
    if (!resolved.url) {
      tried.push({ route: step.route, url: null, status: null, reason: resolved.reason });
      if (resolved.reason === "host_stopped") hostStopped = true;
      continue;
    }
    const result = await fetcher.download(resolved.url);
    if ("error" in result) {
      tried.push({ route: step.route, url: resolved.url, status: result.status, reason: result.error });
      lastReason = result.error;
      if (result.error === "host_stopped") hostStopped = true;
      continue;
    }
    const check = checkArtifact({
      bytes: fs.readFileSync(result.file),
      mediaType: mediaTypeOf(result.content_type),
      finalUrl: result.final_url,
      requestedUrl: resolved.url,
      hasDoi: doi !== null,
      pdftotext: options.pdftotext,
    });
    tried.push({ route: step.route, url: resolved.url, status: result.status, reason: check.reason });
    if (check.terminal) {
      // A later route found the artifact, so the body we were holding in its
      // place is not needed. Dropping it here matters: the Nature landing
      // page the pilot held this way is 657 KB, and a run over the whole work
      // list would leave one such body per rescued source behind.
      if (candidate) fs.rmSync(candidate.got.file, { force: true });
      downloaded = result;
      winner = step.route;
      break;
    }
    if (candidate) fs.rmSync(result.file, { force: true });
    else candidate = { got: result, route: step.route, check };
  }

  const fetchedAt = utcNow();
  // A host that stopped is not a verdict on the source. Leave it with no
  // receipt so the next run attempts it again, and drop a candidate body with
  // it: a chain cut short has not shown that the artifact is out of reach.
  if (!downloaded && (hostStopped || lastReason === "host_stopped")) {
    if (candidate) fs.rmSync(candidate.got.file, { force: true });
    return { deferred: true, receipts: [], objectWritten: false, bytes: 0 };
  }
  if (!downloaded && !candidate) {
    const reason = failureReason(doi, tried);
    const receipts = group.map((item) =>
      ({
        schema_version: 1,
        source_id: item.source_id,
        requested_url: item.url,
        final_url: null,
        http_status: tried[0]?.status ?? null,
        fetched_at: fetchedAt,
        content_type: null,
        bytes: null,
        sha256: null,
        route: null,
        routes_tried: tried,
        outcome: "failed",
        reason,
        source_class: item.source_class,
      }) satisfies FetchReceipt,
    );
    if (!options.dryRun) for (const receipt of receipts) appendReceipt(receipt, options.root);
    return { deferred: false, receipts, objectWritten: false, bytes: 0 };
  }

  // Either the artifact, or the body we are keeping in its place. Both are
  // stored and both get a manifest row: what a host served is a fact worth
  // holding. Only the outcome on the receipt differs.
  const held = downloaded ?? candidate!.got;
  const outcome: Outcome = downloaded ? "stored" : "not_artifact";
  const reason = downloaded ? null : candidate!.check.reason;
  const route = winner ?? candidate!.route;
  const got = held;
  const mediaType = mediaTypeOf(got.content_type);
  let objectWritten = false;
  if (options.dryRun) {
    fs.rmSync(got.file, { force: true });
  } else {
    objectWritten = adoptFile(got.file, got.sha256, options.root).written;
    const classified = options.classify?.({
      sourceIds: group.map((item) => item.source_id),
      url: got.final_url,
      mediaType,
    });
    const tier = classified?.archive_tier ?? defaultArchiveTier;
    await upsertRow(
      {
        sha256: got.sha256,
        bytes: got.bytes,
        media_type: mediaType,
        layer: "exact-bytes",
        origin: got.final_url,
        requested_url: got.final_url === lead.url ? null : lead.url,
        first_seen_at: fetchedAt,
        store: "local-cache",
        visibility: visibilityOf(tier),
        archive_tier: tier,
        observed_licence: classified?.observed_licence ?? null,
        exposure: classified?.exposure ?? "policy",
        derived_from: null,
        derivation: null,
        previous_path: null,
        source_ids: group.map((item) => item.source_id).sort(),
      },
      options.root,
    );
  }

  const receipts = group.map((item) =>
    ({
      schema_version: 1,
      source_id: item.source_id,
      requested_url: item.url,
      final_url: got.final_url,
      http_status: got.status,
      fetched_at: fetchedAt,
      content_type: got.content_type,
      bytes: got.bytes,
      sha256: got.sha256,
      route,
      routes_tried: tried,
      outcome,
      reason,
      source_class: item.source_class,
    }) satisfies FetchReceipt,
  );
  if (!options.dryRun) for (const receipt of receipts) appendReceipt(receipt, options.root);
  return { deferred: false, receipts, objectWritten, bytes: got.bytes };
}

/** Run the fetch over everything the work list still needs. */
export async function runFetch(options: FetchOptions = {}): Promise<FetchSummary> {
  const root = options.root ?? ".";
  const concurrency = Math.max(1, options.concurrency ?? 4);
  const log = options.log ?? (() => undefined);
  const fetcher = new Fetcher({
    root,
    delayMs: options.delayMs ?? 2000,
    maxBytes: options.maxBytes ?? 64 * 1024 * 1024,
    requestTimeoutMs: options.requestTimeoutMs ?? 120_000,
    hostBackoffLimit: options.hostBackoffLimit ?? 3,
  });

  // An interrupted run can leave a part written body behind. Nothing in the
  // cache depends on it, because an object lands by rename.
  fs.rmSync(path.join(cacheRoot(root), "incoming"), { recursive: true, force: true });

  const plan = planRun(root, options.retryFailed ?? false);
  const { todo, heldSources, failedSources, notArtifactSources } = plan;
  const groups = [...groupByUrl(todo).values()];
  const planned = options.limit ? groups.slice(0, options.limit) : groups;
  // Probed once for the run. The artifact check needs the answer per object
  // and the probe spawns a process, so the probe is done here.
  const pdftotext = options.pdftotext ?? hasPdftotext();

  const summary: FetchSummary = {
    planned: planned.reduce((count, group) => count + group.length, 0),
    skipped_held: heldSources,
    skipped_failed: failedSources,
    skipped_not_artifact: notArtifactSources,
    skipped_removed: plan.removedSources,
    attempted: 0,
    stored: 0,
    not_artifact: 0,
    failed: 0,
    objects_written: 0,
    bytes_stored: 0,
    failures_by_reason: {},
    not_artifact_by_reason: {},
    hosts_stopped: [],
    sources_left_for_next_run: 0,
  };

  let cursor = 0;
  const worker = async () => {
    for (;;) {
      const index = cursor;
      cursor += 1;
      if (index >= planned.length) return;
      const group = planned[index];
      const result = await fetchGroup(fetcher, group, {
        root,
        classify: options.classify,
        dryRun: options.dryRun ?? false,
        pdftotext,
      });
      if (result.deferred) {
        summary.sources_left_for_next_run += group.length;
        log(`deferred ${group[0].url}: host stopped for this run`);
        continue;
      }
      summary.attempted += group.length;
      for (const receipt of result.receipts) {
        const reason = receipt.reason ?? "http_error";
        if (receipt.outcome === "stored") summary.stored += 1;
        else if (receipt.outcome === "not_artifact") {
          summary.not_artifact += 1;
          summary.not_artifact_by_reason[reason] = (summary.not_artifact_by_reason[reason] ?? 0) + 1;
        } else {
          summary.failed += 1;
          summary.failures_by_reason[reason] = (summary.failures_by_reason[reason] ?? 0) + 1;
        }
      }
      if (result.objectWritten) {
        summary.objects_written += 1;
        summary.bytes_stored += result.bytes;
      }
      const first = result.receipts[0];
      const why = first.reason ? `: ${first.reason}` : "";
      log(`${first.outcome} ${group[0].url} (${group.length} source${group.length === 1 ? "" : "s"})${why}`);
    }
  };
  await Promise.all(Array.from({ length: concurrency }, worker));

  summary.hosts_stopped = [...fetcher.stoppedHosts].sort();
  return summary;
}
