/** The route chain for one source, tried in a fixed order.
 *
 *   1 direct      the URL the record carries
 *   2 unpaywall   a legal open copy or author manuscript the publisher allows
 *   3 europepmc   the author manuscript Europe PMC holds
 *   4 preprint    the bioRxiv or medRxiv version of the same work
 *
 * Nothing here circumvents access control. There is no Sci-Hub, no
 * institutional credential, no cookie replay and no spoofed user agent. Each
 * route asks a public service for a copy it is entitled to serve. A source no
 * route reaches is recorded paywalled_not_held, which is a legitimate outcome.
 *
 * Routes 2 to 4 need a DOI, and only part of the store carries one, so a
 * source without a DOI fails at the direct route with the status it returned
 * and the three fallbacks record no_doi rather than silently not running.
 */
import { type Reason, type Route } from "../../shared/archive/schema";

export interface RouteInput {
  url: string;
  doi: string | null;
  /** A polite JSON GET, supplied by the fetcher so politeness and backoff are
   * one implementation. transport is set when nothing was asked or nothing
   * came back, which is not the same as the service answering. */
  getJson: (url: string) => Promise<{ status: number; body: unknown | null; transport?: Reason }>;
  /** Read at call time, never at import time, and never written to a file. */
  unpaywallEmail?: string;
}

export interface RouteResult {
  /** The URL to fetch, or null when this route has nothing to offer. */
  url: string | null;
  reason: Reason | null;
}

const asRecord = (value: unknown): Record<string, unknown> | null =>
  value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : null;
const asString = (value: unknown): string | null => (typeof value === "string" && value.trim() ? value.trim() : null);

/** The URL the record already carries. */
async function direct(input: RouteInput): Promise<RouteResult> {
  return { url: input.url, reason: null };
}

/** Unpaywall's API requires a contact address as a query parameter. It is read
 * from UNPAYWALL_EMAIL at call time; with no address the route is skipped and
 * says so, because no address is invented and none is committed. */
async function unpaywall(input: RouteInput): Promise<RouteResult> {
  if (!input.doi) return { url: null, reason: "no_doi" };
  const email = input.unpaywallEmail ?? process.env.UNPAYWALL_EMAIL;
  if (!email) return { url: null, reason: "unpaywall_no_email" };
  const { status, body, transport } = await input.getJson(
    `https://api.unpaywall.org/v2/${encodeURIComponent(input.doi)}?email=${encodeURIComponent(email)}`,
  );
  if (transport) return { url: null, reason: transport };
  if (status === 404) return { url: null, reason: "not_found" };
  if (status !== 200 || !body) return { url: null, reason: "http_error" };
  const record = asRecord(body);
  const best = asRecord(record?.best_oa_location);
  const found = asString(best?.url_for_pdf) ?? asString(best?.url);
  return found ? { url: found, reason: null } : { url: null, reason: "no_open_copy" };
}

/** Europe PMC holds author manuscripts for a large part of the life sciences
 * literature and serves them as full text XML. */
async function europepmc(input: RouteInput): Promise<RouteResult> {
  if (!input.doi) return { url: null, reason: "no_doi" };
  const query = `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%22${encodeURIComponent(input.doi)}%22&resultType=core&format=json`;
  const { status, body, transport } = await input.getJson(query);
  if (transport) return { url: null, reason: transport };
  if (status !== 200 || !body) return { url: null, reason: status === 404 ? "not_found" : "http_error" };
  const results = asRecord(asRecord(body)?.resultList)?.result;
  const first = Array.isArray(results) ? asRecord(results[0]) : null;
  if (!first) return { url: null, reason: "not_found" };
  const pmcid = asString(first.pmcid);
  const inEuropePmc = first.inEPMC === "Y" || first.isOpenAccess === "Y";
  if (!pmcid || !inEuropePmc) return { url: null, reason: "no_open_copy" };
  return { url: `https://www.ebi.ac.uk/europepmc/webservices/rest/${pmcid}/fullTextXML`, reason: null };
}

/** The preprint version of the same work. The two servers share one API. */
async function preprint(input: RouteInput): Promise<RouteResult> {
  if (!input.doi) return { url: null, reason: "no_doi" };
  let transportFailure: Reason | null = null;
  for (const server of ["biorxiv", "medrxiv"] as const) {
    const { status, body, transport } = await input.getJson(`https://api.biorxiv.org/details/${server}/${encodeURIComponent(input.doi)}`);
    if (transport) {
      transportFailure = transport;
      continue;
    }
    if (status !== 200 || !body) continue;
    const collection = asRecord(body)?.collection;
    if (!Array.isArray(collection) || !collection.length) continue;
    const newest = asRecord(collection[collection.length - 1]);
    const doi = asString(newest?.doi) ?? input.doi;
    const version = asString(newest?.version) ?? "1";
    return { url: `https://www.${server}.org/content/${doi}v${version}.full.pdf`, reason: null };
  }
  return { url: null, reason: transportFailure ?? "no_open_copy" };
}

/** The chain, in the order it is tried and recorded. */
export const routeChain: { route: Route; resolve: (input: RouteInput) => Promise<RouteResult> }[] = [
  { route: "direct", resolve: direct },
  { route: "unpaywall", resolve: unpaywall },
  { route: "europepmc", resolve: europepmc },
  { route: "preprint", resolve: preprint },
];
