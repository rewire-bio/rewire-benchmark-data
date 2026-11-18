/** The automatic licence resolver: an observed licence per source, from the
 * service that states it, with the evidence it came from.
 *
 *   npm run licence:resolve -- --cache <dir>
 *
 * 1,075 of 1,483 source records carry no licence string, which is why 1,116
 * sources sit at t4-private and nothing may be published from them. Most of
 * that is unknown rather than restricted. Five services state a licence for a
 * source we already hold a URL or a DOI for, so most of it is resolvable
 * without a person.
 *
 * Four rules shape every line below, and they matter more than coverage.
 *
 * 1. A resolved value is a candidate. It is written beside the record, never
 *    on top of it, and this script writes nothing in data/entities. A licence
 *    a person recorded is never overwritten, and a candidate that disagrees
 *    with one is reported as a lead.
 * 2. A tier comes from data/archive/licence-map.tsv and from nowhere else.
 *    There is no second mapping and no normalisation of the served string: the
 *    value is looked up exactly as served. A string the map does not carry is
 *    reported as unmapped and the run exits non-zero. It never becomes a
 *    silent t4.
 * 3. The evidence per source is the endpoint, the field, the value as served
 *    and the date. A tier with no evidence is worth nothing, so a candidate
 *    without an observation is not written.
 * 4. Two sources of truth that disagree resolve to nothing. Disagreement is
 *    decided by the map's family column, so that rule also runs through the
 *    one mapping.
 *
 * Reads the source records and the licence map. Writes four files, none of
 * them a record:
 *
 *   data/archive/licence-candidates.jsonl                  the candidates
 *   data/omics/audits/<date>-licence-resolve.receipts.jsonl every attempt
 *   maintenance/reports/licence-resolve-<date>.md           the run report
 *   maintenance/reports/licence-resolve-<date>.tsv          the candidate list
 *
 * Nothing here fetches an artifact, and nothing here decides whether a source
 * is fetched. It asks five metadata services what licence they state.
 */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { execFileSync } from "node:child_process";
import { parseArgs } from "node:util";
import { z } from "zod";
import { determineForSource, readLicenceMap, readSourceLicences, sourcesPath, type LicenceRow } from "./map";
import { canonicalLine, defaultArchiveTier, archiveTiers, utcNow, type ArchiveTier } from "../../shared/archive/schema";
import { sourceClassOf } from "../../shared/archive/worklist";

/** The five routes, in the order a tie between two mapped values is broken.
 * Crossref and the repository hosts state an identifier or a licence URL;
 * Europe PMC states a label with no version, so it sits last. */
export const resolveRoutes = ["crossref", "github", "huggingface", "preprint", "europepmc"] as const;
export type ResolveRoute = (typeof resolveRoutes)[number];

/** Why a route produced no licence. The first four are about the metadata, the
 * last four about the transfer. */
export const resolveReasons = [
  "not_applicable",
  "no_licence_in_metadata",
  "not_asserted",
  "ambiguous_version",
  "not_found",
  "http_error",
  "network_error",
  "host_stopped",
] as const;
export type ResolveReason = (typeof resolveReasons)[number];

/** resolved: one family, from at least one string the map carries.
 * conflict: two mapped strings whose families disagree.
 * unmapped: a string was served and the map has no row for it.
 *
 * There is no fourth state. A source no service stated a licence for carries
 * no candidate at all, because a row with no evidence says nothing, and the
 * report counts it as the difference between sources and candidates. */
export const candidateStatuses = ["resolved", "conflict", "unmapped"] as const;
export type CandidateStatus = (typeof candidateStatuses)[number];

const utc = z.string().regex(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/);
const text = z.string().min(1);

/** One licence statement from one service, as served. */
export const observationSchema = z
  .object({
    route: z.enum(resolveRoutes),
    /** The endpoint asked, without any contact parameter. */
    endpoint: text,
    /** Where in the response the value sits. */
    field: text,
    /** The value exactly as served, whitespace trimmed and nothing else. */
    value: text,
    observed_at: utc,
  })
  .strict();
export type Observation = z.infer<typeof observationSchema>;

export const candidateSchema = z
  .object({
    schema_version: z.literal(1),
    source_id: text,
    status: z.enum(candidateStatuses),
    /** The value the tier was read from, exactly as served. */
    observed_licence: z.string().nullable(),
    /** The licence-map family and tier of that value. Null unless resolved. */
    family: z.string().nullable(),
    archive_tier: z.enum(archiveTiers).nullable(),
    /** What the source record carries today, for a reader of this row. This
     * script never changes it. */
    recorded_licence: z.string().nullable(),
    recorded_tier: z.enum(archiveTiers),
    /** How the candidate sits against the recorded licence, by family. */
    agreement: z.enum(["none-recorded", "agrees", "disagrees", "recorded-unmapped", "no-candidate"]),
    /** Values served that the map has no row for. A resolved candidate can
     * still carry one: a second service stating a string nobody has reviewed
     * does not unresolve a licence URL the map covers, and the string is
     * reported either way. */
    unmapped_values: z.array(text),
    /** Set on conflict and unmapped, where no single value can be carried. */
    reason: z.string().nullable(),
    observations: z.array(observationSchema).min(1),
  })
  .strict();
export type Candidate = z.infer<typeof candidateSchema>;

/** One attempt at one route for one source, kept whether it produced a licence
 * or not, so the per-route hit rate is a measurement and not a description. */
export const resolveReceiptSchema = z
  .object({
    schema_version: z.literal(1),
    source_id: text,
    route: z.enum(resolveRoutes),
    /** The endpoint asked, without any contact parameter. Null when the route
     * does not apply to this source and nothing was asked. */
    endpoint: z.string().nullable(),
    attempted_at: utc,
    http_status: z.number().int().nullable(),
    outcome: z.enum(["licence", "no_licence"]),
    reason: z.enum(resolveReasons).nullable(),
    /** The values this route served, as served. */
    values: z.array(text),
  })
  .strict();
export type ResolveReceipt = z.infer<typeof resolveReceiptSchema>;

export const candidatesPath = (root = "."): string => path.join(root, "data/archive/licence-candidates.jsonl");
export const receiptsPath = (date: string, root = "."): string => path.join(root, "data/omics/audits", `${date}-licence-resolve.receipts.jsonl`);
export const reportPath = (date: string, root = "."): string => path.join(root, "maintenance/reports", `licence-resolve-${date}.md`);
export const candidateTablePath = (date: string, root = "."): string => path.join(root, "maintenance/reports", `licence-resolve-${date}.tsv`);

/** The candidates on disk, keyed on source. This is what the licence map work
 * and the triage queue read: a candidate is a suggestion sitting beside the
 * record, so a reader of either can show what a service stated without this
 * file ever having written to a record. A missing file is no candidates. */
export function readCandidates(root = "."): Map<string, Candidate> {
  const file = candidatesPath(root);
  const candidates = new Map<string, Candidate>();
  if (!fs.existsSync(file)) return candidates;
  const lines = fs.readFileSync(file, "utf8").split("\n");
  lines.forEach((line, index) => {
    if (!line.trim()) return;
    const parsed = candidateSchema.safeParse(JSON.parse(line));
    if (!parsed.success) throw new Error(`${file} line ${index + 1}: ${parsed.error.issues[0].message}`);
    candidates.set(parsed.data.source_id, parsed.data);
  });
  return candidates;
}

// ---------------------------------------------------------------- the targets

export interface GithubKey {
  owner: string;
  repo: string;
  /** The commit the URL pins, or null for the default branch. */
  ref: string | null;
}
export interface HuggingfaceKey {
  kind: "models" | "datasets" | "spaces";
  id: string;
  revision: string | null;
}
export interface PreprintKey {
  server: "biorxiv" | "medrxiv" | null;
  doi: string;
  /** The version the URL pins, as a number string, or null. */
  version: string | null;
}

/** The key each route needs for one source, absent where the route does not
 * apply. A source with no key for any route is unresolvable by design: the
 * task's last class is to leave it alone rather than guess. */
export interface RouteKeys {
  crossref?: string;
  github?: GithubKey;
  huggingface?: HuggingfaceKey;
  preprint?: PreprintKey;
  europepmc?: string;
}

export interface Target {
  source_id: string;
  url: string;
  host: string;
  doi: string | null;
  recorded_licence: string | null;
  recorded_tier: ArchiveTier;
  keys: RouteKeys;
}

const hostOf = (url: string): string => {
  try {
    return new URL(url).hostname.toLowerCase();
  } catch {
    return "";
  }
};

const isSha = (value: string): boolean => /^[0-9a-f]{40}$/.test(value);
const trimmed = (value: unknown): string | null => (typeof value === "string" && value.trim() ? value.trim() : null);

/** The preprint servers' DOI prefixes. 10.1101 is the historic one and both
 * servers use it; 10.64898 is the prefix bioRxiv moved to, which is why a
 * server the URL does not name is asked of bioRxiv first and medRxiv second. */
const preprintPrefixes = ["10.1101/", "10.64898/"];

/** Which services can answer for one source, from its URL and DOI alone.
 *
 * Nothing in here is a guess about a licence. It is a guess about which
 * service holds the statement, and a wrong guess costs one request and a
 * not_found receipt. */
export function routeKeysFor(input: { url: string; doi: string | null }): RouteKeys {
  const keys: RouteKeys = {};
  const url = input.url;
  const host = hostOf(url);
  const doi = input.doi;
  let pathname = "";
  try {
    pathname = decodeURIComponent(new URL(url).pathname);
  } catch {
    pathname = "";
  }
  const segments = pathname.split("/").filter(Boolean);

  if (doi) keys.crossref = doi;

  // A PMCID in the URL is Europe PMC's key, whether the URL is Europe PMC's
  // own REST endpoint or an NCBI article page.
  const pmcid = /PMC\d{4,}/.exec(url);
  if (pmcid) keys.europepmc = pmcid[0];

  if (host === "raw.githubusercontent.com" && segments.length >= 3) {
    keys.github = { owner: segments[0], repo: segments[1], ref: isSha(segments[2]) ? segments[2] : null };
  } else if (host === "codeload.github.com" && segments.length >= 4) {
    const ref = segments[segments.length - 1];
    keys.github = { owner: segments[0], repo: segments[1], ref: isSha(ref) ? ref : null };
  } else if (host === "api.github.com" && segments[0] === "repos" && segments.length >= 3) {
    const ref = new URL(url).searchParams.get("ref");
    keys.github = { owner: segments[1], repo: segments[2], ref: ref && isSha(ref) ? ref : null };
  } else if ((host === "github.com" || host === "www.github.com") && segments.length >= 2) {
    const pinned = segments.length >= 4 && ["blob", "tree", "raw", "commit"].includes(segments[2]) && isSha(segments[3]) ? segments[3] : null;
    keys.github = { owner: segments[0], repo: segments[1].replace(/\.git$/, ""), ref: pinned };
  }

  if (host === "huggingface.co" || host === "www.huggingface.co") {
    let rest = segments;
    if (rest[0] === "api") rest = rest.slice(1);
    let kind: HuggingfaceKey["kind"] = "models";
    if (rest[0] === "datasets" || rest[0] === "spaces") {
      kind = rest[0] === "datasets" ? "datasets" : "spaces";
      rest = rest.slice(1);
    }
    if (rest[0] === "models") rest = rest.slice(1);
    const verbs = ["resolve", "raw", "blob", "tree", "revision", "commit"];
    const verb = rest.findIndex((segment) => verbs.includes(segment));
    const id = (verb > 0 ? rest.slice(0, verb) : rest.slice(0, 2)).join("/");
    const revision = verb > 0 && rest[verb + 1] ? rest[verb + 1] : null;
    if (id) keys.huggingface = { kind, id, revision: revision && isSha(revision) ? revision : null };
  }

  const preprintHost = /(^|\.)(biorxiv|medrxiv)\.org$/.exec(host);
  const preprintDoi = doi && preprintPrefixes.some((prefix) => doi.startsWith(prefix)) ? doi : null;
  if (preprintHost || preprintDoi) {
    const server = preprintHost ? (preprintHost[2] as "biorxiv" | "medrxiv") : null;
    // api.biorxiv.org/details/<server>/<doi> and
    // www.biorxiv.org/content/<doi>v<n>... both carry the DOI in the path.
    const inPath = /(10\.\d{4,9}\/[^\s?]+?)(v(\d+))?(\.full|\.full\.pdf|\.supplementary-material)?$/.exec(pathname.replace(/^\/(details|content)\//, "").replace(/^(biorxiv|medrxiv)\//, ""));
    const fromPath = inPath && preprintPrefixes.some((prefix) => inPath[1].startsWith(prefix)) ? inPath[1] : null;
    const chosen = preprintDoi ?? fromPath;
    if (chosen) keys.preprint = { server, doi: chosen, version: inPath?.[3] ?? null };
  }

  return keys;
}

/** Every source record, with the keys each route needs and the licence the
 * record carries today. Reads the store and nothing else. */
export function readTargets(root = "."): Target[] {
  const map = readLicenceMap(root);
  const licences = readSourceLicences(root);
  const targets: Target[] = [];
  for (const line of fs.readFileSync(sourcesPath(root), "utf8").split("\n")) {
    if (!line.trim()) continue;
    const record = JSON.parse(line) as { id: string; kind: string; attributes?: Record<string, unknown> };
    if (record.kind !== "source") continue;
    const attributes = record.attributes ?? {};
    const url = trimmed(attributes.artifact_url) ?? trimmed(attributes.url) ?? "";
    const doi = trimmed(attributes.doi);
    targets.push({
      source_id: record.id,
      url,
      host: hostOf(url),
      doi,
      recorded_licence: licences.get(record.id) ?? null,
      recorded_tier: determineForSource(record.id, map, licences).archive_tier,
      keys: routeKeysFor({ url, doi }),
    });
  }
  return targets;
}

// -------------------------------------------------------------- the transport

export interface HttpResponse {
  status: number;
  body: string;
  /** When these bytes arrived. A cached response keeps the date of the
   * transfer that produced it, so a rerun does not restate a week-old
   * observation as today's. The client fills it when a transport leaves it
   * out. */
  fetched_at?: string;
}
/** What the routes ask of the network. Injected, so the tests run offline. */
export type Transport = (url: string, headers: Record<string, string>) => Promise<HttpResponse>;

/** A host that answered 429 or 503 past the backoff. The run stops asking that
 * host and reports it, rather than hammering it. */
export class HostStopped extends Error {
  constructor(readonly host: string) {
    super(`${host} stopped answering: 429 or 503 past the backoff`);
  }
}

export const userAgent = "rewire-benchmark-data licence resolver (+https://rewire.it)";

const sleep = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms));

/** Serialises every request to one host behind a delay, backs off on 429 and
 * 503, stops asking a host that keeps refusing, and optionally caches each
 * response so a second run of the same work asks nothing. */
export class Client {
  private readonly queues = new Map<string, Promise<unknown>>();
  readonly stopped = new Set<string>();
  readonly counts = new Map<string, number>();

  constructor(
    private readonly options: {
      transport: Transport;
      /** Milliseconds between two requests to the same host. */
      delayMs: number;
      /** Per host, where politeness needs more than the default. */
      hostDelayMs?: Record<string, number>;
      /** Directory for cached responses. Absent means no cache. */
      cacheDir?: string;
      attempts?: number;
      backoffMs?: number;
      log?: (line: string) => void;
    },
  ) {}

  private cacheFile(url: string): string | null {
    if (!this.options.cacheDir) return null;
    return path.join(this.options.cacheDir, `${crypto.createHash("sha256").update(url).digest("hex")}.json`);
  }

  /** One GET, cached, queued behind the host's other requests. Throws
   * HostStopped for a host that is refusing. */
  async get(url: string, headers: Record<string, string> = {}): Promise<HttpResponse> {
    const host = hostOf(url);
    if (this.stopped.has(host)) throw new HostStopped(host);
    const cached = this.cacheFile(url);
    if (cached && fs.existsSync(cached)) {
      const held = JSON.parse(fs.readFileSync(cached, "utf8")) as HttpResponse;
      return { ...held, fetched_at: held.fetched_at ?? utcNow() };
    }
    const previous = this.queues.get(host) ?? Promise.resolve();
    const work = previous.then(
      () => this.fetchOnce(host, url, headers),
      () => this.fetchOnce(host, url, headers),
    );
    this.queues.set(
      host,
      work.then(
        () => undefined,
        () => undefined,
      ),
    );
    const response = await work;
    if (cached) {
      fs.mkdirSync(path.dirname(cached), { recursive: true });
      fs.writeFileSync(cached, JSON.stringify(response));
    }
    return response;
  }

  private async fetchOnce(host: string, url: string, headers: Record<string, string>): Promise<HttpResponse> {
    const attempts = this.options.attempts ?? 3;
    const backoff = this.options.backoffMs ?? 2000;
    const delay = this.options.hostDelayMs?.[host] ?? this.options.delayMs;
    for (let attempt = 1; attempt <= attempts; attempt += 1) {
      if (this.stopped.has(host)) throw new HostStopped(host);
      await sleep(delay);
      this.counts.set(host, (this.counts.get(host) ?? 0) + 1);
      const answered = await this.options.transport(url, { "user-agent": userAgent, ...headers });
      const response = { ...answered, fetched_at: answered.fetched_at ?? utcNow() };
      if (response.status !== 429 && response.status !== 503) return response;
      if (attempt === attempts) break;
      const wait = backoff * attempt * attempt;
      this.options.log?.(`${host} answered ${response.status}, waiting ${Math.round(wait / 1000)}s (attempt ${attempt} of ${attempts})`);
      await sleep(wait);
    }
    this.stopped.add(host);
    this.options.log?.(`${host} is still answering 429 or 503. Nothing further is asked of it in this run.`);
    throw new HostStopped(host);
  }
}

/** The default transport: one fetch with a timeout, nothing retried here. */
export function httpTransport(timeoutMs = 30000): Transport {
  return async (url, headers) => {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(url, { headers, redirect: "follow", signal: controller.signal });
      const body = await response.text();
      return { status: response.status, body, fetched_at: utcNow() };
    } finally {
      clearTimeout(timer);
    }
  };
}

// ------------------------------------------------------------------ the routes

/** What a route found for one key: the values it served, or why it served
 * none. A route never maps a value and never decides a tier. */
export interface RouteResult {
  /** The endpoint that answers for this one key, which is what a reader
   * re-runs to see the value again. */
  endpoint: string;
  /** The request the run actually made, where it differs: Europe PMC is asked
   * for 25 records at a time, so the receipt names the batch and the candidate
   * names the one record. Absent when the two are the same. */
  request?: string;
  http_status: number | null;
  values: { value: string; field: string }[];
  reason: ResolveReason | null;
  /** When the bytes this was read from arrived. */
  observed_at: string | null;
}

const json = (body: string): unknown => {
  try {
    return JSON.parse(body);
  } catch {
    return null;
  }
};

const failure = (endpoint: string, status: number | null, reason: ResolveReason, observedAt: string | null = null): RouteResult => ({
  endpoint,
  http_status: status,
  values: [],
  reason,
  observed_at: observedAt,
});

/** Crossref works metadata. The licence array carries a URL and a
 * content-version per entry. Only vor and am are the licence of the work a
 * reader gets; tdm is a text-mining grant and is dropped, because treating it
 * as a reuse licence would resolve a paywalled article to a licence it does
 * not have. Two different URLs at the same content-version are two
 * observations, which the family rule then calls a conflict. */
export async function crossrefLicences(doi: string, client: Client, contact: string | null): Promise<RouteResult> {
  const endpoint = `https://api.crossref.org/works/${encodeURI(doi)}`;
  const asked = contact ? `${endpoint}?mailto=${encodeURIComponent(contact)}` : endpoint;
  let response: HttpResponse;
  try {
    response = await client.get(asked);
  } catch (error) {
    return failure(endpoint, null, error instanceof HostStopped ? "host_stopped" : "network_error");
  }
  const at = response.fetched_at ?? null;
  if (response.status === 404) return failure(endpoint, 404, "not_found", at);
  if (response.status !== 200) return failure(endpoint, response.status, "http_error", at);
  const message = (json(response.body) as { message?: { license?: unknown[] } } | null)?.message;
  if (!message) return failure(endpoint, response.status, "http_error", at);
  const entries = Array.isArray(message.license) ? (message.license as { URL?: unknown; "content-version"?: unknown }[]) : [];
  const wanted = entries.filter((entry) => entry["content-version"] === "vor" || entry["content-version"] === "am");
  const values: { value: string; field: string }[] = [];
  for (const entry of wanted) {
    const value = trimmed(entry.URL);
    if (!value) continue;
    const field = `message.license[content-version=${String(entry["content-version"])}].URL`;
    if (!values.some((held) => held.value === value)) values.push({ value, field });
  }
  if (!values.length) return failure(endpoint, response.status, "no_licence_in_metadata", at);
  return { endpoint, http_status: response.status, values, reason: null, observed_at: at };
}

/** The Europe PMC search endpoint for one PMCID. This is the endpoint a
 * candidate names, because it is what a reader re-runs to see that one value
 * again. The run asks for 25 records at a time, and the receipt names that
 * batch request. */
export const europepmcEndpoint = (query: string, pageSize: number): string =>
  `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=${encodeURIComponent(query)}&resultType=core&format=json&pageSize=${pageSize}`;

/** Europe PMC states open-access status and a licence label for much of the
 * life sciences literature. The label carries no version and no URL, so it is
 * the weakest of the five, and the map decides whether it says anything this
 * archive can use. Queried in batches, because one request per PMCID would put
 * 281 requests on a host the archive fetch is also working. */
export async function europepmcLicences(pmcids: string[], client: Client): Promise<Map<string, RouteResult>> {
  const results = new Map<string, RouteResult>();
  const request = europepmcEndpoint(pmcids.map((pmcid) => `PMCID:${pmcid}`).join(" OR "), pmcids.length);
  const one = (pmcid: string) => europepmcEndpoint(`PMCID:${pmcid}`, 1);
  let response: HttpResponse;
  try {
    response = await client.get(request);
  } catch (error) {
    const reason: ResolveReason = error instanceof HostStopped ? "host_stopped" : "network_error";
    for (const pmcid of pmcids) results.set(pmcid, { ...failure(one(pmcid), null, reason), request });
    return results;
  }
  const parsed = json(response.body) as { resultList?: { result?: { pmcid?: unknown; license?: unknown }[] } } | null;
  if (response.status !== 200 || !parsed?.resultList) {
    for (const pmcid of pmcids) results.set(pmcid, { ...failure(one(pmcid), response.status, "http_error", response.fetched_at ?? null), request });
    return results;
  }
  for (const record of parsed.resultList.result ?? []) {
    const pmcid = trimmed(record.pmcid);
    if (!pmcid) continue;
    const value = trimmed(record.license);
    results.set(
      pmcid,
      value
        ? {
            endpoint: one(pmcid),
            request,
            http_status: response.status,
            values: [{ value, field: "resultList.result[].license" }],
            reason: null,
            observed_at: response.fetched_at ?? null,
          }
        : { ...failure(one(pmcid), response.status, "no_licence_in_metadata", response.fetched_at ?? null), request },
    );
  }
  for (const pmcid of pmcids)
    if (!results.has(pmcid)) results.set(pmcid, { ...failure(one(pmcid), response.status, "not_found", response.fetched_at ?? null), request });
  return results;
}

/** GitHub's licence endpoint, at the pinned commit where the URL pins one. One
 * response carries both the LICENSE file it read and the SPDX identifier
 * GitHub normalised it to, so the two parts of this route's class are one
 * request. NOASSERTION and other mean GitHub read a licence file it could not
 * identify, which is not a licence string and is left unresolved. */
export async function githubLicence(key: GithubKey, client: Client, token: string | null): Promise<RouteResult> {
  const base = `https://api.github.com/repos/${encodeURIComponent(key.owner)}/${encodeURIComponent(key.repo)}/license`;
  const endpoint = key.ref ? `${base}?ref=${key.ref}` : base;
  const headers: Record<string, string> = { accept: "application/vnd.github+json", "x-github-api-version": "2022-11-28" };
  if (token) headers.authorization = `Bearer ${token}`;
  let response: HttpResponse;
  try {
    response = await client.get(endpoint, headers);
  } catch (error) {
    return failure(endpoint, null, error instanceof HostStopped ? "host_stopped" : "network_error");
  }
  const at = response.fetched_at ?? null;
  if (response.status === 404) return failure(endpoint, 404, "not_found", at);
  if (response.status !== 200) return failure(endpoint, response.status, "http_error", at);
  const body = json(response.body) as { license?: { spdx_id?: unknown }; name?: unknown } | null;
  const spdx = trimmed(body?.license?.spdx_id);
  if (!spdx) return failure(endpoint, response.status, "no_licence_in_metadata", at);
  if (spdx === "NOASSERTION" || spdx.toLowerCase() === "other") return failure(endpoint, response.status, "not_asserted", at);
  const file = trimmed(body?.name);
  return {
    endpoint,
    http_status: response.status,
    values: [{ value: spdx, field: `license.spdx_id (from ${file ?? "the repository licence file"})` }],
    reason: null,
    observed_at: at,
  };
}

/** A Hugging Face model, dataset or space: the cardData licence field at the
 * pinned revision. The field can be a list, and two entries are two
 * observations. other means the card declined to name one. */
export async function huggingfaceLicence(key: HuggingfaceKey, client: Client): Promise<RouteResult> {
  const base = `https://huggingface.co/api/${key.kind}/${key.id}`;
  const endpoint = key.revision ? `${base}/revision/${key.revision}` : base;
  let response: HttpResponse;
  try {
    response = await client.get(endpoint);
  } catch (error) {
    return failure(endpoint, null, error instanceof HostStopped ? "host_stopped" : "network_error");
  }
  const at = response.fetched_at ?? null;
  if (response.status === 404 || response.status === 401) return failure(endpoint, response.status, "not_found", at);
  if (response.status !== 200) return failure(endpoint, response.status, "http_error", at);
  const card = (json(response.body) as { cardData?: { license?: unknown } } | null)?.cardData;
  const declared = card?.license;
  const list = (Array.isArray(declared) ? declared : [declared]).map(trimmed).filter((value): value is string => Boolean(value));
  const values = list
    .filter((value) => value.toLowerCase() !== "other" && value.toLowerCase() !== "unknown")
    .map((value) => ({ value, field: "cardData.license" }));
  if (!values.length) return failure(endpoint, response.status, list.length ? "not_asserted" : "no_licence_in_metadata", at);
  return { endpoint, http_status: response.status, values, reason: null, observed_at: at };
}

/** bioRxiv and medRxiv state a licence per version. The version the URL pins
 * is the one that answers for the bytes. With no version pinned, agreeing
 * versions answer and disagreeing versions resolve to nothing: a preprint
 * relicensed between versions has no single licence, and averaging two is the
 * one thing rule 4 forbids. */
export async function preprintLicence(key: PreprintKey, client: Client): Promise<RouteResult> {
  const servers: ("biorxiv" | "medrxiv")[] = key.server ? [key.server] : ["biorxiv", "medrxiv"];
  let last: RouteResult | null = null;
  for (const server of servers) {
    const endpoint = `https://api.biorxiv.org/details/${server}/${key.doi}`;
    let response: HttpResponse;
    try {
      response = await client.get(endpoint);
    } catch (error) {
      last = failure(endpoint, null, error instanceof HostStopped ? "host_stopped" : "network_error");
      continue;
    }
    const at = response.fetched_at ?? null;
    if (response.status !== 200) {
      last = failure(endpoint, response.status, "http_error", at);
      continue;
    }
    const body = json(response.body) as { collection?: { version?: unknown; license?: unknown }[] } | null;
    const collection = body?.collection ?? [];
    if (!collection.length) {
      last = failure(endpoint, response.status, "not_found", at);
      continue;
    }
    const versions = collection.map((entry) => ({ version: String(entry.version ?? ""), licence: trimmed(entry.license) }));
    const pinned = key.version ? versions.filter((entry) => entry.version === key.version) : versions;
    const found = pinned.map((entry) => entry.licence).filter((value): value is string => Boolean(value));
    const distinct = [...new Set(found)];
    if (!distinct.length) {
      last = failure(endpoint, response.status, pinned.length ? "no_licence_in_metadata" : "not_found", at);
      continue;
    }
    if (distinct.length > 1 && !key.version) {
      last = failure(endpoint, response.status, "ambiguous_version", at);
      continue;
    }
    const field = key.version ? `collection[version=${key.version}].license` : "collection[].license";
    return { endpoint, http_status: response.status, values: distinct.map((value) => ({ value, field })), reason: null, observed_at: at };
  }
  return last ?? failure(`https://api.biorxiv.org/details/biorxiv/${key.doi}`, null, "not_found");
}

// --------------------------------------------------------- building candidates

const routeOrder = new Map<ResolveRoute, number>(resolveRoutes.map((route, index) => [route, index]));
const isUrl = (value: string): boolean => /^https?:\/\//i.test(value);

/** One candidate from one source's observations.
 *
 * The map is the only thing that turns a string into a family and a tier, and
 * the family is also what decides whether two services agree. A value with no
 * row cannot be compared with anything, so it is reported as unmapped rather
 * than read as a disagreement or absorbed into the default. */
export function buildCandidate(input: {
  target: Target;
  observations: Observation[];
  map: Map<string, LicenceRow>;
}): Candidate | null {
  const { target, observations, map } = input;
  if (!observations.length) return null;
  const mapped = observations
    .map((observation) => ({ observation, row: map.get(observation.value) }))
    .filter((pair): pair is { observation: Observation; row: LicenceRow } => Boolean(pair.row));
  const unmapped = [...new Set(observations.filter((observation) => !map.get(observation.value)).map((observation) => observation.value))].sort();
  const recordedRow = target.recorded_licence ? map.get(target.recorded_licence) : undefined;

  const base = {
    schema_version: 1 as const,
    source_id: target.source_id,
    recorded_licence: target.recorded_licence,
    recorded_tier: target.recorded_tier,
    unmapped_values: unmapped,
    observations: [...observations].sort((a, b) => (routeOrder.get(a.route) ?? 0) - (routeOrder.get(b.route) ?? 0)),
  };

  if (!mapped.length) {
    return candidateSchema.parse({
      ...base,
      status: "unmapped",
      observed_licence: null,
      family: null,
      archive_tier: null,
      agreement: "no-candidate",
      reason: `no row in data/archive/licence-map.tsv for ${unmapped.map((value) => `"${value}"`).join(", ")}`,
    });
  }

  const families = [...new Set(mapped.map((pair) => pair.row.family))].sort();
  if (families.length > 1) {
    const stated = mapped.map((pair) => `${pair.observation.route} served "${pair.observation.value}" (${pair.row.family})`).sort();
    return candidateSchema.parse({
      ...base,
      status: "conflict",
      observed_licence: null,
      family: null,
      archive_tier: null,
      agreement: "no-candidate",
      reason: `two services disagree: ${stated.join("; ")}`,
    });
  }

  // One family. Carry the value that states it best: a licence URL over a
  // free-text label, then the earliest route in resolveRoutes.
  const preferred = [...mapped].sort((a, b) => {
    const url = Number(isUrl(b.observation.value)) - Number(isUrl(a.observation.value));
    if (url !== 0) return url;
    return (routeOrder.get(a.observation.route) ?? 0) - (routeOrder.get(b.observation.route) ?? 0);
  })[0];

  const agreement = !target.recorded_licence
    ? "none-recorded"
    : !recordedRow
      ? "recorded-unmapped"
      : recordedRow.family === preferred.row.family
        ? "agrees"
        : "disagrees";

  return candidateSchema.parse({
    ...base,
    status: "resolved",
    observed_licence: preferred.observation.value,
    family: preferred.row.family,
    archive_tier: preferred.row.archive_tier,
    agreement,
    reason: null,
  });
}

// ------------------------------------------------------------------- the run

export interface RunOptions {
  root?: string;
  date?: string;
  transport?: Transport;
  githubToken?: string | null;
  crossrefContact?: string | null;
  cacheDir?: string;
  delayMs?: number;
  hostDelayMs?: Record<string, number>;
  /** Resolve only these sources, for a rerun of one case. */
  only?: string[];
  limit?: number;
  routes?: ResolveRoute[];
  /** Europe PMC PMCIDs per request. */
  batchSize?: number;
  log?: (line: string) => void;
}

export interface RunResult {
  date: string;
  targets: Target[];
  candidates: Candidate[];
  receipts: ResolveReceipt[];
  stoppedHosts: string[];
  requests: Record<string, number>;
}

/** Ask every route that applies, then build one candidate per source.
 *
 * Routes run one after another rather than together, because two of them sit
 * on hosts the archive fetch is also working and a fetch already running is
 * the one thing this must not disturb. Within a route, keys are deduplicated:
 * 165 repositories answer for 549 sources. */
export async function runResolve(options: RunOptions = {}): Promise<RunResult> {
  const root = options.root ?? ".";
  const date = options.date ?? new Date().toISOString().slice(0, 10);
  const map = readLicenceMap(root);
  const log = options.log ?? (() => undefined);
  const wanted = new Set<ResolveRoute>(options.routes ?? resolveRoutes);
  let targets = readTargets(root);
  if (options.only?.length) {
    const only = new Set(options.only);
    targets = targets.filter((target) => only.has(target.source_id));
  }
  if (options.limit) targets = targets.slice(0, options.limit);

  const client = new Client({
    transport: options.transport ?? httpTransport(),
    delayMs: options.delayMs ?? 250,
    // Europe PMC and the preprint API get a full second: the archive fetch is
    // on www.ebi.ac.uk at the same time, and its work comes first.
    hostDelayMs: options.hostDelayMs ?? { "www.ebi.ac.uk": 1000, "api.biorxiv.org": 1000, "api.crossref.org": 250, "api.github.com": 150, "huggingface.co": 250 },
    cacheDir: options.cacheDir,
    log,
  });

  const receipts: ResolveReceipt[] = [];
  const observations = new Map<string, Observation[]>();
  const record = (target: Target, route: ResolveRoute, result: RouteResult): void => {
    // The date the bytes arrived, not the date this run read them again from
    // its cache. A transport that does not say falls back to now.
    const at = result.observed_at ?? utcNow();
    receipts.push(
      resolveReceiptSchema.parse({
        schema_version: 1,
        source_id: target.source_id,
        route,
        // The receipt is a log of the transfer, so it names the request the
        // run made. The candidate names the endpoint that answers for the one
        // source, which for a batched route is not the same URL.
        endpoint: result.request ?? result.endpoint,
        attempted_at: at,
        http_status: result.http_status,
        outcome: result.values.length ? "licence" : "no_licence",
        reason: result.reason,
        values: result.values.map((value) => value.value),
      }),
    );
    if (!result.values.length) return;
    const held = observations.get(target.source_id) ?? [];
    for (const value of result.values)
      held.push(observationSchema.parse({ route, endpoint: result.endpoint, field: value.field, value: value.value, observed_at: at }));
    observations.set(target.source_id, held);
  };

  // Crossref: one request per DOI. The batch filter exists, but a single work
  // endpoint is what Crossref documents for one record and it keeps the
  // endpoint on the receipt the exact thing that was asked.
  if (wanted.has("crossref")) {
    const byDoi = new Map<string, Target[]>();
    for (const target of targets) if (target.keys.crossref) byDoi.set(target.keys.crossref, [...(byDoi.get(target.keys.crossref) ?? []), target]);
    log(`crossref: ${byDoi.size} DOIs for ${[...byDoi.values()].flat().length} sources`);
    let done = 0;
    for (const [doi, group] of byDoi) {
      const result = await crossrefLicences(doi, client, options.crossrefContact ?? null);
      for (const target of group) record(target, "crossref", result);
      done += 1;
      if (done % 50 === 0) log(`crossref: ${done} of ${byDoi.size}`);
    }
  }

  if (wanted.has("github")) {
    const byRepo = new Map<string, { key: GithubKey; targets: Target[] }>();
    for (const target of targets) {
      const key = target.keys.github;
      if (!key) continue;
      const id = `${key.owner}/${key.repo}@${key.ref ?? "default"}`;
      const held = byRepo.get(id);
      if (held) held.targets.push(target);
      else byRepo.set(id, { key, targets: [target] });
    }
    log(`github: ${byRepo.size} repository pins for ${[...byRepo.values()].flatMap((entry) => entry.targets).length} sources`);
    let done = 0;
    for (const { key, targets: group } of byRepo.values()) {
      const result = await githubLicence(key, client, options.githubToken ?? null);
      for (const target of group) record(target, "github", result);
      done += 1;
      if (done % 50 === 0) log(`github: ${done} of ${byRepo.size}`);
    }
  }

  if (wanted.has("huggingface")) {
    const byRepo = new Map<string, { key: HuggingfaceKey; targets: Target[] }>();
    for (const target of targets) {
      const key = target.keys.huggingface;
      if (!key) continue;
      const id = `${key.kind}/${key.id}@${key.revision ?? "default"}`;
      const held = byRepo.get(id);
      if (held) held.targets.push(target);
      else byRepo.set(id, { key, targets: [target] });
    }
    log(`huggingface: ${byRepo.size} repository pins`);
    for (const { key, targets: group } of byRepo.values()) {
      const result = await huggingfaceLicence(key, client);
      for (const target of group) record(target, "huggingface", result);
    }
  }

  if (wanted.has("preprint")) {
    const byDoi = new Map<string, { key: PreprintKey; targets: Target[] }>();
    for (const target of targets) {
      const key = target.keys.preprint;
      if (!key) continue;
      const id = `${key.server ?? "unknown"}/${key.doi}v${key.version ?? "all"}`;
      const held = byDoi.get(id);
      if (held) held.targets.push(target);
      else byDoi.set(id, { key, targets: [target] });
    }
    log(`preprint: ${byDoi.size} DOI versions`);
    let done = 0;
    for (const { key, targets: group } of byDoi.values()) {
      const result = await preprintLicence(key, client);
      for (const target of group) record(target, "preprint", result);
      done += 1;
      if (done % 50 === 0) log(`preprint: ${done} of ${byDoi.size}`);
    }
  }

  if (wanted.has("europepmc")) {
    const byPmcid = new Map<string, Target[]>();
    for (const target of targets) if (target.keys.europepmc) byPmcid.set(target.keys.europepmc, [...(byPmcid.get(target.keys.europepmc) ?? []), target]);
    const ids = [...byPmcid.keys()];
    const size = options.batchSize ?? 25;
    log(`europepmc: ${ids.length} PMCIDs in ${Math.ceil(ids.length / size)} requests`);
    for (let start = 0; start < ids.length; start += size) {
      const batch = ids.slice(start, start + size);
      const results = await europepmcLicences(batch, client);
      for (const pmcid of batch) {
        const result = results.get(pmcid);
        if (!result) continue;
        for (const target of byPmcid.get(pmcid) ?? []) record(target, "europepmc", result);
      }
      log(`europepmc: ${Math.min(start + size, ids.length)} of ${ids.length}`);
    }
  }

  const candidates: Candidate[] = [];
  for (const target of targets) {
    const candidate = buildCandidate({ target, observations: observations.get(target.source_id) ?? [], map });
    if (candidate) candidates.push(candidate);
  }
  candidates.sort((a, b) => (a.source_id < b.source_id ? -1 : a.source_id > b.source_id ? 1 : 0));
  receipts.sort((a, b) =>
    a.source_id === b.source_id
      ? (routeOrder.get(a.route) ?? 0) - (routeOrder.get(b.route) ?? 0)
      : a.source_id < b.source_id
        ? -1
        : 1,
  );
  return { date, targets, candidates, receipts, stoppedHosts: [...client.stopped], requests: Object.fromEntries([...client.counts].sort()) };
}

// ------------------------------------------------------------------ the report

/** A string a service served that the licence map has no row for, with the
 * licence-map key a reviewer would most likely point it at.
 *
 * This is a reading suggestion for the owner and nothing else. It never sets a
 * tier on a candidate, it is not consulted by buildCandidate, and the resolver
 * exits non-zero while any of these strings is still unmapped. Its one job is
 * the conditional figure in the report: how much leaves t4-private if the owner
 * adds these rows. A licence determination is the owner's call, signed under
 * their own name (docs/source-preservation.md).
 *
 * Empty since 2026-11-17. The strings whose reading was mechanical, a licence
 * the map already carries under another spelling, are rows in
 * data/archive/licence-map.tsv and resolve through the map like any other
 * value. What is left unmapped is the set of strings naming terms no row in
 * the map has read, so there is no existing row to propose for any of them and
 * a suggestion here would be a reading rather than a pointer.
 */
export const proposedMapKeys: Record<string, string> = {};

const pad = (value: unknown, width = 5): string => String(value).padStart(width);

export const candidateColumns = [
  "source_id",
  "status",
  "observed_licence",
  "family",
  "archive_tier",
  "recorded_licence",
  "recorded_tier",
  "agreement",
  "routes",
  "endpoints",
  "fields",
  "observed_at",
  "unmapped_values",
  "reason",
] as const;

const cell = (value: string): string => value.replace(/[\t\n]+/g, " ").trim();

/** The full candidate list as a table, one row per candidate. */
export function renderCandidateTable(result: RunResult): string {
  const head = [
    "# Licence candidates, one row per source with at least one observation. Generated, never hand written.",
    "#   npm run licence:resolve",
    `# Generated ${result.date}. A candidate is never promoted into a source record by this file.`,
    candidateColumns.join("\t"),
  ];
  const body = result.candidates.map((candidate) =>
    [
      candidate.source_id,
      candidate.status,
      candidate.observed_licence ?? "",
      candidate.family ?? "",
      candidate.archive_tier ?? "",
      candidate.recorded_licence ?? "",
      candidate.recorded_tier,
      candidate.agreement,
      candidate.observations.map((observation) => observation.route).join(" "),
      candidate.observations.map((observation) => observation.endpoint).join(" "),
      candidate.observations.map((observation) => observation.field).join(" | "),
      candidate.observations[0].observed_at,
      candidate.unmapped_values.join(" | "),
      candidate.reason ?? "",
    ]
      .map((value) => cell(String(value)))
      .join("\t"),
  );
  return `${[...head, ...body].join("\n")}\n`;
}

export interface Counts {
  sources: number;
  attempted: number;
  candidates: number;
  by_status: Record<CandidateStatus, number>;
  by_route: Record<ResolveRoute, { sources: number; licence: number; no_licence: number; by_reason: Record<string, number> }>;
  resolved_by_route: Record<ResolveRoute, number>;
  by_tier: Record<string, number>;
  leaves_t4: number;
  leaves_t4_if_proposed: number;
  agreement: Record<string, number>;
  unmapped_strings: { value: string; sources: number; routes: string[]; example: string; proposed: string | null; proposed_tier: string | null }[];
  unresolved_hosts: { host: string; sources: number }[];
  /** The same sources by the host-behaviour class the repository already keys
   * treatments on, which is what says why a route did not apply. */
  unresolved_classes: { source_class: string; sources: number }[];
  unresolved_reasons: Record<string, number>;
}

/** Every number the report quotes, counted over the run's own output. */
export function countRun(result: RunResult, map: Map<string, LicenceRow>): Counts {
  const byStatus = Object.fromEntries(candidateStatuses.map((status) => [status, 0])) as Record<CandidateStatus, number>;
  const byRoute = Object.fromEntries(
    resolveRoutes.map((route) => [route, { sources: 0, licence: 0, no_licence: 0, by_reason: {} as Record<string, number> }]),
  ) as Counts["by_route"];
  const resolvedByRoute = Object.fromEntries(resolveRoutes.map((route) => [route, 0])) as Record<ResolveRoute, number>;
  const byTier: Record<string, number> = {};
  const agreement: Record<string, number> = {};
  const unmapped = new Map<string, { sources: Set<string>; routes: Set<string>; example: string }>();

  for (const receipt of result.receipts) {
    const entry = byRoute[receipt.route];
    entry.sources += 1;
    if (receipt.outcome === "licence") entry.licence += 1;
    else {
      entry.no_licence += 1;
      const reason = receipt.reason ?? "unknown";
      entry.by_reason[reason] = (entry.by_reason[reason] ?? 0) + 1;
    }
  }

  let leavesT4 = 0;
  let leavesT4IfProposed = 0;
  for (const candidate of result.candidates) {
    byStatus[candidate.status] += 1;
    agreement[candidate.agreement] = (agreement[candidate.agreement] ?? 0) + 1;
    if (candidate.status === "resolved" && candidate.archive_tier) {
      byTier[candidate.archive_tier] = (byTier[candidate.archive_tier] ?? 0) + 1;
      // The route the carried value came from. Where two routes served the
      // same value, the earlier one in resolveRoutes is credited, which is the
      // order buildCandidate sorted the observations into.
      const carried = candidate.observations.find((observation) => observation.value === candidate.observed_licence);
      if (carried) resolvedByRoute[carried.route] += 1;
      if (candidate.recorded_tier === "t4-private" && candidate.archive_tier !== "t4-private" && candidate.archive_tier !== "t5-no-store") {
        leavesT4 += 1;
        leavesT4IfProposed += 1;
      }
    }
    for (const value of candidate.unmapped_values) {
      const held = unmapped.get(value) ?? { sources: new Set<string>(), routes: new Set<string>(), example: candidate.source_id };
      held.sources.add(candidate.source_id);
      for (const observation of candidate.observations) if (observation.value === value) held.routes.add(observation.route);
      unmapped.set(value, held);
    }
    // The conditional figure: an unmapped candidate whose proposed row names a
    // publishable tier would leave t4 if the owner accepted that row.
    if (candidate.status === "unmapped" && candidate.recorded_tier === "t4-private") {
      const tiers = candidate.unmapped_values
        .map((value) => proposedMapKeys[value])
        .map((key) => (key ? map.get(key)?.archive_tier : undefined))
        .filter((tier): tier is ArchiveTier => Boolean(tier));
      const distinct = [...new Set(tiers)];
      if (distinct.length === 1 && distinct[0] !== "t4-private" && distinct[0] !== "t5-no-store") leavesT4IfProposed += 1;
    }
  }

  const withCandidate = new Set(result.candidates.map((candidate) => candidate.source_id));
  const unresolvedHosts = new Map<string, number>();
  const unresolvedClasses = new Map<string, number>();
  for (const target of result.targets) {
    if (withCandidate.has(target.source_id)) continue;
    const host = target.host || "no-url";
    unresolvedHosts.set(host, (unresolvedHosts.get(host) ?? 0) + 1);
    const name = target.host ? sourceClassOf(target.host) : "no-url";
    unresolvedClasses.set(name, (unresolvedClasses.get(name) ?? 0) + 1);
  }

  const unresolvedReasons: Record<string, number> = {};
  for (const receipt of result.receipts) {
    if (withCandidate.has(receipt.source_id) || receipt.outcome === "licence") continue;
    const reason = receipt.reason ?? "unknown";
    unresolvedReasons[`${receipt.route}:${reason}`] = (unresolvedReasons[`${receipt.route}:${reason}`] ?? 0) + 1;
  }
  const attempted = new Set(result.receipts.map((receipt) => receipt.source_id)).size;

  return {
    sources: result.targets.length,
    attempted,
    candidates: result.candidates.length,
    by_status: byStatus,
    by_route: byRoute,
    resolved_by_route: resolvedByRoute,
    by_tier: byTier,
    leaves_t4: leavesT4,
    leaves_t4_if_proposed: leavesT4IfProposed,
    agreement,
    unmapped_strings: [...unmapped]
      .map(([value, held]) => {
        const key = proposedMapKeys[value];
        const row = key ? map.get(key) : undefined;
        return {
          value,
          sources: held.sources.size,
          routes: [...held.routes].sort(),
          example: held.example,
          proposed: key ?? null,
          proposed_tier: row?.archive_tier ?? null,
        };
      })
      .sort((a, b) => b.sources - a.sources || (a.value < b.value ? -1 : 1)),
    unresolved_hosts: [...unresolvedHosts]
      .map(([host, sources]) => ({ host, sources }))
      .sort((a, b) => b.sources - a.sources || (a.host < b.host ? -1 : 1)),
    unresolved_classes: [...unresolvedClasses]
      .map(([source_class, sources]) => ({ source_class, sources }))
      .sort((a, b) => b.sources - a.sources || (a.source_class < b.source_class ? -1 : 1)),
    unresolved_reasons: Object.fromEntries(Object.entries(unresolvedReasons).sort((a, b) => b[1] - a[1])),
  };
}

/** The dated run report. Every number in it comes from countRun over the run's
 * own candidates and receipts. */
export function renderReport(result: RunResult, counts: Counts): string {
  const lines: string[] = [];
  const out = (line = "") => lines.push(line);
  const table = (header: string[], rows: string[][]) => {
    out(`| ${header.join(" | ")} |`);
    out(`| ${header.map(() => "---").join(" | ")} |`);
    for (const row of rows) out(`| ${row.join(" | ")} |`);
    out();
  };

  out(`# Licence resolver run, ${result.date}`);
  out();
  out("Generated by `npm run licence:resolve`. Do not edit. Every figure below is counted over the");
  out("candidates and receipts this run wrote, not modelled.");
  out();
  out("A candidate is a candidate. Nothing here is written into a source record, no licence a person");
  out("recorded is changed, and no tier comes from anywhere but `data/archive/licence-map.tsv`.");
  out();
  out("## What the run did");
  out();
  table(
    ["What", "Count"],
    [
      ["source records read", String(counts.sources)],
      ["sources at least one route applied to", String(counts.attempted)],
      ["sources a service stated a licence for", String(counts.candidates)],
      ["resolved to a tier through the licence map", String(counts.by_status.resolved)],
      ["served a string the map has no row for", String(counts.by_status.unmapped)],
      ["two services disagreeing, resolved to nothing", String(counts.by_status.conflict)],
      ["no service stated a licence", String(counts.sources - counts.candidates)],
    ],
  );
  out("## The number that decides how much can be published");
  out();
  out("Sources that leave t4-private if these candidates are accepted, with the licence map exactly as");
  out(`it stands today: **${counts.leaves_t4}**. That is the measurement, counted over the candidates below.`);
  out();
  out("One further figure is conditional and is not a measurement of anything yet. Sources that would");
  out("leave t4-private if the owner also added a reviewed row for each unmapped string below, with the");
  out(`reading this report proposes: ${counts.leaves_t4_if_proposed}. Those rows do not exist, so that number is a forecast of a`);
  out("decision rather than a count of a state.");
  out();
  out("## Per route");
  out();
  out("One attempt per source per route. A route that applies to a source and states no licence is");
  out("counted here, which is what makes the hit rate a measurement.");
  out();
  table(
    ["Route", "Sources asked", "Stated a licence", "Hit rate", "Carried the resolved value"],
    resolveRoutes
      .filter((route) => counts.by_route[route].sources > 0)
      .map((route) => {
        const entry = counts.by_route[route];
        return [
          `\`${route}\``,
          String(entry.sources),
          String(entry.licence),
          `${((entry.licence / entry.sources) * 100).toFixed(1)} percent`,
          String(counts.resolved_by_route[route]),
        ];
      }),
  );
  out("Why a route stated nothing:");
  out();
  for (const route of resolveRoutes) {
    const entry = counts.by_route[route];
    const reasons = Object.entries(entry.by_reason).sort((a, b) => b[1] - a[1]);
    if (!reasons.length) continue;
    out(`- \`${route}\`: ${reasons.map(([reason, count]) => `${reason} ${count}`).join(", ")}`);
  }
  out();
  out("## Tiers the resolved candidates map to");
  out();
  table(
    ["Tier", "Candidates"],
    Object.entries(counts.by_tier)
      .sort()
      .map(([tier, count]) => [`\`${tier}\``, String(count)]),
  );
  out("## Against the licence a person recorded");
  out();
  table(
    ["Candidate sits", "Sources"],
    Object.entries(counts.agreement)
      .sort()
      .map(([state, count]) => [state, String(count)]),
  );
  out("`disagrees` is a research lead, not a correction. The recorded value stays exactly as it is and");
  out("the candidate sits beside it in `data/archive/licence-candidates.jsonl`.");
  out();
  out("## Strings the licence map has no row for");
  out();
  out("Each one is a build failure by design: the resolver exits non-zero while any of these is");
  out("unmapped, so a new licence string cannot become a silent t4-private. The proposed key is the");
  out("existing map row a reviewer would most likely point the string at. It is a suggestion for the");
  out("owner, it sets no tier, and the resolver does not consult it.");
  out();
  table(
    ["Value as served", "Sources", "Routes", "Example source", "Proposed map row", "Tier that row carries"],
    counts.unmapped_strings.map((entry) => [
      `\`${entry.value}\``,
      String(entry.sources),
      entry.routes.join(" "),
      `\`${entry.example}\``,
      entry.proposed ? `\`${entry.proposed}\`` : "none proposed",
      entry.proposed_tier ? `\`${entry.proposed_tier}\`` : "",
    ]),
  );
  out("## Still unresolved");
  out();
  out(`${counts.sources - counts.candidates} sources came away with no licence statement from any service. By host:`);
  out();
  table(
    ["Host", "Sources"],
    counts.unresolved_hosts.slice(0, 25).map((entry) => [entry.host, String(entry.sources)]),
  );
  const rest = counts.unresolved_hosts.slice(25).reduce((total, entry) => total + entry.sources, 0);
  if (rest) out(`A further ${rest} sources sit on ${counts.unresolved_hosts.length - 25} other hosts.`);
  out();
  out("By the host-behaviour class the repository keys treatments on. A class with no route is one");
  out("this resolver leaves alone on purpose: the rule is to resolve nothing rather than guess, and");
  out("arXiv, a data repository's rights field and a project web page each need their own route.");
  out();
  table(
    ["Source class", "Sources"],
    counts.unresolved_classes.map((entry) => [`\`${entry.source_class}\``, String(entry.sources)]),
  );
  out("Why, by route and reason:");
  out();
  for (const [key, count] of Object.entries(counts.unresolved_reasons).slice(0, 20)) out(`- \`${key}\`: ${count}`);
  out();
  if (result.stoppedHosts.length) {
    out("## Hosts that stopped answering");
    out();
    out("A host that answers 429 or 503 past the backoff is not asked again in the run. Its sources are");
    out("unresolved for this run and nothing about them is inferred.");
    out();
    for (const host of result.stoppedHosts) out(`- ${host}`);
    out();
  }
  out("## Requests made");
  out();
  const requests = Object.entries(result.requests);
  if (requests.length) {
    out("One line per host, counting every request the run sent, including a retry after a 429 or a 503.");
    out();
    table(["Host", "Requests"], requests.map(([host, count]) => [host, String(count)]));
  } else {
    out("None. Every response came from the response cache of an earlier run, which keeps each");
    out("response's own retrieval date, so the dates above are the dates of the transfers and not of");
    out("this run.");
    out();
  }
  out("## Files");
  out();
  out("- `data/archive/licence-candidates.jsonl`: one row per candidate. `readCandidates()` in");
  out("  `scripts/licence/resolve.ts` parses it. The triage queue does not consume it yet.");
  out(`- \`data/omics/audits/${result.date}-licence-resolve.receipts.jsonl\`: every attempt, including the ones`);
  out("  that stated nothing.");
  out(`- \`maintenance/reports/licence-resolve-${result.date}.tsv\`: the full candidate list as a table.`);
  out();
  out("A candidate is promoted into `attributes.licence` by a record change like any other, and the");
  out("manifest's `observed_licence` is written by the archive work, not here.");
  return `${lines.join("\n")}\n`;
}

function printSummary(counts: Counts, result: RunResult): void {
  console.log(`sources                        ${pad(counts.sources)}`);
  console.log(`routes applied to              ${pad(counts.attempted)}`);
  console.log(`candidates                     ${pad(counts.candidates)}`);
  for (const status of candidateStatuses) console.log(`  ${status.padEnd(28)} ${pad(counts.by_status[status])}`);
  console.log(`leaves t4-private              ${pad(counts.leaves_t4)}`);
  console.log(`leaves t4-private if proposed  ${pad(counts.leaves_t4_if_proposed)}`);
  console.log("");
  console.log("per route: asked, stated a licence");
  for (const route of resolveRoutes) {
    const entry = counts.by_route[route];
    if (!entry.sources) continue;
    console.log(`  ${route.padEnd(14)} ${pad(entry.sources)} ${pad(entry.licence)}`);
  }
  if (result.stoppedHosts.length) console.log(`hosts that stopped answering: ${result.stoppedHosts.join(", ")}`);
}

/** The GitHub token, from the gh CLI. 165 repository pins against an
 * unauthenticated API is 60 requests an hour and a 403, so the run needs one.
 * The token is never logged and never written to a file. */
export function githubTokenFromCli(): string | null {
  try {
    const token = execFileSync("gh", ["auth", "token"], { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
    return token || null;
  } catch {
    return null;
  }
}

async function main(): Promise<void> {
  const { values } = parseArgs({
    options: {
      root: { type: "string" },
      date: { type: "string" },
      cache: { type: "string" },
      "delay-ms": { type: "string" },
      limit: { type: "string" },
      source: { type: "string", multiple: true },
      route: { type: "string", multiple: true },
      "batch-size": { type: "string" },
      "dry-run": { type: "boolean" },
      quiet: { type: "boolean" },
    },
  });
  const root = values.root ?? ".";
  const date = values.date ?? new Date().toISOString().slice(0, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) throw new Error(`--date must be YYYY-MM-DD, not "${date}"`);
  const routes = values.route?.length ? (values.route as ResolveRoute[]) : undefined;
  for (const route of routes ?? []) if (!(resolveRoutes as readonly string[]).includes(route)) throw new Error(`--route must be one of ${resolveRoutes.join(", ")}`);

  const result = await runResolve({
    root,
    date,
    cacheDir: values.cache,
    delayMs: values["delay-ms"] ? Number(values["delay-ms"]) : undefined,
    limit: values.limit ? Number(values.limit) : undefined,
    only: values.source,
    routes,
    batchSize: values["batch-size"] ? Number(values["batch-size"]) : undefined,
    githubToken: githubTokenFromCli(),
    // Crossref asks for a contact in the request so it can reach whoever is
    // running a crawl. It is read from the environment and written nowhere.
    crossrefContact: process.env.UNPAYWALL_EMAIL ?? null,
    log: values.quiet ? undefined : (line) => console.error(line),
  });

  const map = readLicenceMap(root);
  const counts = countRun(result, map);

  if (!values["dry-run"]) {
    const candidates = candidatesPath(root);
    fs.mkdirSync(path.dirname(candidates), { recursive: true });
    fs.writeFileSync(candidates, result.candidates.map((candidate) => canonicalLine(candidate as unknown as Record<string, unknown>)).join("\n") + (result.candidates.length ? "\n" : ""));

    const receipts = receiptsPath(date, root);
    fs.mkdirSync(path.dirname(receipts), { recursive: true });
    fs.appendFileSync(receipts, result.receipts.map((receipt) => canonicalLine(receipt as unknown as Record<string, unknown>)).join("\n") + (result.receipts.length ? "\n" : ""));

    const report = reportPath(date, root);
    fs.mkdirSync(path.dirname(report), { recursive: true });
    fs.writeFileSync(report, renderReport(result, counts));
    fs.writeFileSync(candidateTablePath(date, root), renderCandidateTable(result));
    console.log(`${candidates}: ${result.candidates.length} candidates`);
    console.log(`${receipts}: ${result.receipts.length} attempts appended`);
    console.log(`${report}`);
    console.log(`${candidateTablePath(date, root)}`);
  }

  printSummary(counts, result);

  // A string the map does not know is a build failure, not a silent
  // t4-private, and a conflict is a thing a person has to settle. Both are
  // reported first and then exit non-zero.
  const loud = counts.by_status.unmapped + counts.by_status.conflict;
  if (loud) {
    console.error("");
    console.error(`${counts.by_status.unmapped} sources served a licence string data/archive/licence-map.tsv has no row for, and ${counts.by_status.conflict} carry two services that disagree.`);
    console.error("Add a reviewed row for each string, or settle the conflict, then run this again.");
    process.exitCode = 1;
  }
}

if (process.argv[1] && import.meta.url === `file://${process.argv[1]}`)
  main().catch((error: unknown) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  });
