/** The fetcher, against a local server. No test here reaches the network. */
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { createHash } from "node:crypto";
import { afterEach, expect, it } from "vitest";
import { failureReason, planRun, runFetch } from "../scripts/archive/fetch";
import { hasObject } from "../scripts/archive/objects";
import { readManifest } from "../scripts/archive/manifest";
import { readReceipts } from "../scripts/archive/receipts";
import { routeChain } from "../scripts/archive/routes";

const roots: string[] = [];
const servers: http.Server[] = [];
afterEach(async () => {
  roots.splice(0).forEach((root) => fs.rmSync(root, { recursive: true, force: true }));
  await Promise.all(servers.splice(0).map((server) => new Promise((resolve) => server.close(resolve))));
});

const digest = (bytes: Buffer | string) => createHash("sha256").update(bytes).digest("hex");

async function serve(handler: http.RequestListener): Promise<string> {
  const server = http.createServer(handler);
  servers.push(server);
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  if (!address || typeof address === "string") throw new Error("no address");
  return `http://127.0.0.1:${address.port}`;
}

/** A root holding only the source records the fetcher reads. */
function fixtureRoot(sources: { id: string; url: string; doi?: string }[]): string {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "archive-fetch-"));
  roots.push(root);
  fs.mkdirSync(path.join(root, "data/entities"), { recursive: true });
  fs.writeFileSync(
    path.join(root, "data/entities/sources.jsonl"),
    sources
      .map((source) =>
        JSON.stringify({
          id: source.id,
          kind: "source",
          attributes: { artifact_url: source.url, ...(source.doi ? { doi: source.doi } : {}) },
        }),
      )
      .join("\n") + "\n",
  );
  return root;
}

const run = (root: string, extra: Record<string, unknown> = {}) =>
  runFetch({ root, concurrency: 2, delayMs: 0, requestTimeoutMs: 5000, ...extra });

it("stores what it fetched, writes one manifest row and one receipt per source, and writes nothing on a second run", async () => {
  const body = Buffer.from("primary source bytes");
  let requests = 0;
  const base = await serve((_request, response) => {
    requests += 1;
    response.writeHead(200, { "Content-Type": "application/pdf; charset=binary" });
    response.end(body);
  });
  const root = fixtureRoot([
    { id: "source-one", url: `${base}/one.pdf` },
    { id: "source-two", url: `${base}/one.pdf` },
    { id: "source-three", url: `${base}/three.pdf` },
  ]);

  const first = await run(root);
  expect(first.stored).toBe(3);
  expect(first.failed).toBe(0);
  // Two sources share a URL, so they share one transfer and one object.
  expect(requests).toBe(2);
  expect(first.objects_written).toBe(1);

  const manifest = readManifest(root);
  expect(manifest.size).toBe(1);
  const row = manifest.get(digest(body));
  expect(row?.media_type).toBe("application/pdf");
  expect(row?.layer).toBe("exact-bytes");
  expect(row?.archive_tier).toBe("t4-private");
  expect(row?.visibility).toBe("restricted");
  expect(row?.source_ids).toEqual(["source-one", "source-three", "source-two"]);
  expect(hasObject(digest(body), root)).toBe(true);
  expect(readReceipts(root)).toHaveLength(3);

  const before = fs.readFileSync(path.join(root, "data/archive/objects", `${digest(body)[0]}.jsonl`), "utf8");
  const second = await run(root);
  expect(second).toMatchObject({ planned: 0, attempted: 0, stored: 0, skipped_held: 3, objects_written: 0 });
  expect(requests).toBe(2);
  expect(readReceipts(root)).toHaveLength(3);
  expect(fs.readFileSync(path.join(root, "data/archive/objects", `${digest(body)[0]}.jsonl`), "utf8")).toBe(before);
});

it("records a failure with its status and leaves the three fallbacks visible as unrun without a DOI", async () => {
  const base = await serve((_request, response) => {
    response.writeHead(403);
    response.end("no");
  });
  const root = fixtureRoot([{ id: "source-one", url: `${base}/paid.pdf` }]);
  const summary = await run(root);
  expect(summary).toMatchObject({ stored: 0, failed: 1, failures_by_reason: { http_error: 1 } });
  const [receipt] = readReceipts(root);
  expect(receipt.outcome).toBe("failed");
  expect(receipt.http_status).toBe(403);
  expect(receipt.routes_tried.map((attempt) => [attempt.route, attempt.reason])).toEqual([
    ["direct", "http_error"],
    ["unpaywall", "no_doi"],
    ["europepmc", "no_doi"],
    ["preprint", "no_doi"],
  ]);
  // A source with a receipt is not attempted again unless asked.
  expect(planRun(root, false).todo).toHaveLength(0);
  expect(planRun(root, true).todo).toHaveLength(1);
});

it("keeps a cookie wall without calling it stored, and runs the rest of the chain first", async () => {
  // Modelled on link.springer.com for 10.1007/978-3-031-90252-9_7, which the
  // pilot stored as 346 KB of HTML whose whole text layer was a 76 character
  // title line. A 200 called that stored.
  const wall = Buffer.from(`<!doctype html><html lang="en"><head>
<title>A Phylogenetic Approach to Genomic Language Modeling | Springer Nature Link</title></head>
<body><dialog open><p>We use cookies to give you the best experience. Accept all cookies to
continue, or manage your cookies at any time.</p></dialog><main></main></body></html>`);
  let requests = 0;
  const base = await serve((_request, response) => {
    requests += 1;
    response.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    response.end(wall);
  });
  const root = fixtureRoot([{ id: "source-one", url: `${base}/chapter` }]);
  const summary = await run(root);

  expect(summary.stored).toBe(0);
  expect(summary.not_artifact).toBe(1);
  expect(summary.not_artifact_by_reason).toEqual({ interstitial_body: 1 });
  expect(summary.failed).toBe(0);

  // The bytes are kept. What a host served is a fact worth holding, and the
  // manifest row is how a later run knows we have seen it.
  const [receipt] = readReceipts(root);
  expect(receipt.outcome).toBe("not_artifact");
  expect(receipt.reason).toBe("interstitial_body");
  expect(receipt.sha256).toBe(digest(wall));
  expect(receipt.route).toBe("direct");
  expect(hasObject(digest(wall), root)).toBe(true);
  expect(readManifest(root).size).toBe(1);

  // The direct route did not end the chain. Without a DOI the three fallbacks
  // have nothing to resolve and say so, which is what proves they ran.
  expect(receipt.routes_tried.map((attempt) => [attempt.route, attempt.reason])).toEqual([
    ["direct", "interstitial_body"],
    ["unpaywall", "no_doi"],
    ["europepmc", "no_doi"],
    ["preprint", "no_doi"],
  ]);
  expect(requests).toBe(1);

  // Not held, so not counted as held; and not re-fetched until asked.
  const second = await run(root);
  expect(second).toMatchObject({ planned: 0, attempted: 0, skipped_held: 0, skipped_not_artifact: 1 });
  expect(planRun(root, false).todo).toHaveLength(0);
  expect(planRun(root, true).todo).toHaveLength(1);
});

it("refuses a body over the ceiling without holding it", async () => {
  const base = await serve((_request, response) => {
    response.writeHead(200, { "Content-Type": "application/octet-stream" });
    response.end(Buffer.alloc(4096));
  });
  const root = fixtureRoot([{ id: "source-one", url: `${base}/big.bin` }]);
  const summary = await run(root, { maxBytes: 1024 });
  expect(summary.failures_by_reason).toEqual({ too_large: 1 });
  expect(readManifest(root).size).toBe(0);
});

it("stops a host that keeps rate limiting and leaves its sources for the next run", async () => {
  let requests = 0;
  const base = await serve((_request, response) => {
    requests += 1;
    response.writeHead(429, { "Retry-After": "0" });
    response.end("slow down");
  });
  const root = fixtureRoot([
    { id: "source-one", url: `${base}/one.pdf` },
    { id: "source-two", url: `${base}/two.pdf` },
    { id: "source-three", url: `${base}/three.pdf` },
  ]);
  const summary = await run(root, { concurrency: 1, hostBackoffLimit: 2 });
  expect(summary.hosts_stopped).toHaveLength(1);
  expect(summary.sources_left_for_next_run).toBeGreaterThan(0);
  expect(summary.stored).toBe(0);
  // Backing off once per attempt, then stopping: a stopped host is not asked again.
  expect(requests).toBe(2);
  expect(planRun(root, false).todo.length).toBe(3 - summary.attempted);
});

it("holds the whole host lane for Retry-After, not just the worker that saw it", async () => {
  const arrivals: number[] = [];
  let served = 0;
  const base = await serve((_request, response) => {
    arrivals.push(Date.now());
    served += 1;
    if (served === 1) {
      response.writeHead(429, { "Retry-After": "1" });
      response.end("slow down");
      return;
    }
    response.writeHead(200, { "Content-Type": "text/plain" });
    response.end(`bytes ${served}`);
  });
  const root = fixtureRoot([
    { id: "source-one", url: `${base}/one.txt` },
    { id: "source-two", url: `${base}/two.txt` },
  ]);
  // Two workers, one host, no gap of its own: the only thing that can keep the
  // second request back is the hold the first one's Retry-After put on the lane.
  const summary = await runFetch({ root, concurrency: 2, delayMs: 0, requestTimeoutMs: 5000 });
  expect(summary.stored).toBe(2);
  expect(arrivals.length).toBeGreaterThanOrEqual(3);
  expect(arrivals[1] - arrivals[0]).toBeGreaterThanOrEqual(900);
}, 20_000);

it("plans and fetches nothing on a dry run", async () => {
  let requests = 0;
  const base = await serve((_request, response) => {
    requests += 1;
    response.writeHead(200, { "Content-Type": "text/plain" });
    response.end("bytes");
  });
  const root = fixtureRoot([{ id: "source-one", url: `${base}/one.txt` }]);
  const summary = await run(root, { dryRun: true });
  expect(summary.stored).toBe(1);
  expect(requests).toBe(1);
  expect(readReceipts(root)).toEqual([]);
  expect(readManifest(root).size).toBe(0);
});

it("tries the four routes in order and skips Unpaywall with a reason when no address is configured", async () => {
  const asked: string[] = [];
  const getJson = async (url: string) => {
    asked.push(url);
    if (url.includes("europepmc"))
      return { status: 200, body: { resultList: { result: [{ pmcid: "PMC1", inEPMC: "Y" }] } } };
    if (url.includes("biorxiv")) return { status: 200, body: { collection: [{ doi: "10.1101/x", version: "2" }] } };
    return { status: 200, body: { best_oa_location: { url_for_pdf: "https://example.org/open.pdf" } } };
  };
  expect(routeChain.map((step) => step.route)).toEqual(["direct", "unpaywall", "europepmc", "preprint"]);

  const input = { url: "https://example.org/paid.pdf", doi: "10.1101/x", getJson };
  expect(await routeChain[0].resolve(input)).toEqual({ url: "https://example.org/paid.pdf", reason: null });
  expect(await routeChain[1].resolve({ ...input, unpaywallEmail: undefined })).toEqual({ url: null, reason: "unpaywall_no_email" });
  expect(await routeChain[1].resolve({ ...input, unpaywallEmail: "archive@example.org" })).toEqual({
    url: "https://example.org/open.pdf",
    reason: null,
  });
  expect(await routeChain[2].resolve(input)).toEqual({
    url: "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC1/fullTextXML",
    reason: null,
  });
  expect(await routeChain[3].resolve(input)).toEqual({ url: "https://www.biorxiv.org/content/10.1101/xv2.full.pdf", reason: null });
  expect(await routeChain[3].resolve({ ...input, doi: null })).toEqual({ url: null, reason: "no_doi" });
  expect(asked.some((url) => url.includes("sci-hub"))).toBe(false);
});

it("calls a source paywalled only when every fallback actually answered", () => {
  const direct = { route: "direct" as const, url: "https://example.org/paid.pdf", status: 403, reason: "http_error" as const };
  const answered = [
    { route: "unpaywall" as const, url: null, status: null, reason: "no_open_copy" as const },
    { route: "europepmc" as const, url: null, status: null, reason: "no_open_copy" as const },
    { route: "preprint" as const, url: null, status: null, reason: "not_found" as const },
  ];
  expect(failureReason("10.1101/x", [direct, ...answered])).toBe("paywalled_not_held");

  // Unpaywall skipped for want of a configured address: not an answer.
  const noEmail = [{ ...answered[0], reason: "unpaywall_no_email" as const }, answered[1], answered[2]];
  expect(failureReason("10.1101/x", [direct, ...noEmail])).toBe("http_error");

  // Europe PMC unreachable because its host was stopped: not an answer.
  const stopped = [answered[0], { ...answered[1], reason: "host_stopped" as const }, answered[2]];
  expect(failureReason("10.1101/x", [direct, ...stopped])).toBe("http_error");

  // No DOI, so the three fallbacks never had anything to ask with.
  const noDoi = answered.map((attempt) => ({ ...attempt, reason: "no_doi" as const }));
  expect(failureReason(null, [direct, ...noDoi])).toBe("http_error");

  // A fallback that resolved a URL the host then refused is an answer.
  const refused = [
    { route: "unpaywall" as const, url: "https://example.org/open.pdf", status: 404, reason: "not_found" as const },
    answered[1],
    answered[2],
  ];
  expect(failureReason("10.1101/x", [direct, ...refused])).toBe("paywalled_not_held");
});
