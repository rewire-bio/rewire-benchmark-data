/** The automatic licence resolver.
 *
 * Every test here runs offline against an injected transport and a temporary
 * store, because a test that asks Crossref what it thinks today measures
 * Crossref rather than this code.
 *
 * The four rules the resolver exists to keep are what these tests pin:
 * a recorded licence is never changed, a tier comes only from the licence map,
 * an unknown string is loud rather than private, and two services that
 * disagree resolve to nothing.
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import {
  buildCandidate,
  candidatesPath,
  candidateSchema,
  Client,
  crossrefLicences,
  europepmcLicences,
  githubLicence,
  HostStopped,
  huggingfaceLicence,
  preprintLicence,
  proposedMapKeys,
  readCandidates,
  resolveRoutes,
  routeKeysFor,
  runResolve,
  countRun,
  renderReport,
  type Observation,
  type Target,
  type Transport,
} from "../scripts/licence/resolve";
import { readLicenceMap, type LicenceRow } from "../scripts/licence/map";
import { canonicalLine } from "../shared/archive/schema";

const roots: string[] = [];
afterEach(() => roots.splice(0).forEach((root) => fs.rmSync(root, { recursive: true, force: true })));

const mapRows = (rows: [string, string, string][]): Map<string, LicenceRow> =>
  new Map(rows.map(([licence, family, tier]) => [licence, { licence, family, archive_tier: tier as LicenceRow["archive_tier"], basis: "identifier", note: "" }]));

const map = mapRows([
  ["MIT", "permissive-code", "t0-public"],
  ["https://creativecommons.org/licenses/by/4.0/", "cc-by", "t0-public"],
  ["CC BY 4.0", "cc-by", "t0-public"],
  ["CC-BY-NC-ND-4.0", "cc-by-nc-nd", "t3-verbatim-nd-nc"],
  ["arXiv.org perpetual non-exclusive license 1.0", "arxiv-nonexclusive", "t4-private"],
]);

const target = (overrides: Partial<Target> = {}): Target => ({
  source_id: "source-one",
  url: "https://example.org/one.pdf",
  host: "example.org",
  doi: null,
  recorded_licence: null,
  recorded_tier: "t4-private",
  keys: {},
  ...overrides,
});

const observation = (overrides: Partial<Observation> = {}): Observation => ({
  route: "crossref",
  endpoint: "https://api.crossref.org/works/10.1/one",
  field: "message.license[content-version=vor].URL",
  value: "https://creativecommons.org/licenses/by/4.0/",
  observed_at: "2026-11-17T12:00:00Z",
  ...overrides,
});

/** A transport that answers from a table and records what was asked. */
const transportFor = (answers: Record<string, { status?: number; body: unknown }>, asked: string[] = []): Transport => {
  return async (url) => {
    asked.push(url);
    const key = Object.keys(answers).find((candidate) => url.startsWith(candidate));
    if (!key) return { status: 404, body: "{}" };
    const answer = answers[key];
    return { status: answer.status ?? 200, body: typeof answer.body === "string" ? answer.body : JSON.stringify(answer.body) };
  };
};

describe("which service can answer for a source", () => {
  it("reads a repository and its pinned commit out of every GitHub URL shape the store carries", () => {
    const sha = "3afbffd3674726e5146797be21cf6bd7470a2c5f";
    expect(routeKeysFor({ url: `https://raw.githubusercontent.com/theislab/scib/${sha}/data/metrics.csv`, doi: null }).github).toEqual({
      owner: "theislab",
      repo: "scib",
      ref: sha,
    });
    expect(routeKeysFor({ url: `https://codeload.github.com/science-machine/biomlbench/tar.gz/${sha}`, doi: null }).github).toEqual({
      owner: "science-machine",
      repo: "biomlbench",
      ref: sha,
    });
    expect(routeKeysFor({ url: `https://api.github.com/repos/usnistgov/trec-browser/contents/a/b.md?ref=${sha}`, doi: null }).github).toEqual({
      owner: "usnistgov",
      repo: "trec-browser",
      ref: sha,
    });
    // A repository page pins nothing, so the licence is read at the default branch.
    expect(routeKeysFor({ url: "https://github.com/jwohlwend/boltz", doi: null }).github).toEqual({ owner: "jwohlwend", repo: "boltz", ref: null });
  });

  it("does not treat a GitHub Pages site as a repository", () => {
    expect(routeKeysFor({ url: "https://proteinbench.github.io/", doi: null }).github).toBeUndefined();
  });

  it("reads a Hugging Face dataset, model and revision", () => {
    const sha = "78ec8156c2ffb3e5475277fdb7eb603294224e53";
    expect(routeKeysFor({ url: `https://huggingface.co/datasets/InstaDeepAI/plant-genomic-benchmark/resolve/${sha}/Figures/Fig3.txt`, doi: null }).huggingface).toEqual({
      kind: "datasets",
      id: "InstaDeepAI/plant-genomic-benchmark",
      revision: sha,
    });
    expect(routeKeysFor({ url: "https://huggingface.co/ctheodoris/Geneformer", doi: null }).huggingface).toEqual({
      kind: "models",
      id: "ctheodoris/Geneformer",
      revision: null,
    });
  });

  it("reads the preprint server, DOI and pinned version", () => {
    expect(routeKeysFor({ url: "https://www.biorxiv.org/content/10.1101/2023.04.30.538439v2.full.pdf", doi: null }).preprint).toEqual({
      server: "biorxiv",
      doi: "10.1101/2023.04.30.538439",
      version: "2",
    });
    // The newer bioRxiv prefix goes through the same API, and a DOI with no
    // host hint leaves the server for the route to try.
    expect(routeKeysFor({ url: "https://example.org/a.pdf", doi: "10.64898/2026.07.23.740433" }).preprint).toEqual({
      server: null,
      doi: "10.64898/2026.07.23.740433",
      version: null,
    });
  });

  it("takes a PMCID for Europe PMC and a DOI for Crossref", () => {
    const keys = routeKeysFor({ url: "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12342186/fullTextXML", doi: "10.1093/bioinformatics/btaf417" });
    expect(keys.europepmc).toBe("PMC12342186");
    expect(keys.crossref).toBe("10.1093/bioinformatics/btaf417");
  });

  it("leaves a source no service covers alone", () => {
    expect(routeKeysFor({ url: "https://predictioncenter.org/casp15/results.cgi", doi: null })).toEqual({});
  });
});

describe("a candidate never overwrites what a person recorded", () => {
  it("writes the candidate beside a recorded licence and says the two agree", () => {
    const candidate = buildCandidate({
      target: target({ recorded_licence: "CC BY 4.0", recorded_tier: "t0-public" }),
      observations: [observation()],
      map,
    })!;
    expect(candidate.recorded_licence).toBe("CC BY 4.0");
    expect(candidate.recorded_tier).toBe("t0-public");
    expect(candidate.observed_licence).toBe("https://creativecommons.org/licenses/by/4.0/");
    expect(candidate.agreement).toBe("agrees");
  });

  it("reports a disagreement with a recorded licence as a lead and keeps the recorded value", () => {
    const candidate = buildCandidate({
      target: target({ recorded_licence: "CC-BY-NC-ND-4.0", recorded_tier: "t3-verbatim-nd-nc" }),
      observations: [observation()],
      map,
    })!;
    expect(candidate.agreement).toBe("disagrees");
    expect(candidate.recorded_licence).toBe("CC-BY-NC-ND-4.0");
    expect(candidate.recorded_tier).toBe("t3-verbatim-nd-nc");
  });

  it("says so when the recorded string has no row to compare against", () => {
    const candidate = buildCandidate({ target: target({ recorded_licence: "Not stated on the retrieved page" }), observations: [observation()], map })!;
    expect(candidate.agreement).toBe("recorded-unmapped");
  });
});

describe("the licence map is the only thing that decides a tier", () => {
  it("makes a string with no row unmapped, never t4-private", () => {
    const candidate = buildCandidate({ target: target(), observations: [observation({ route: "europepmc", value: "cc by" })], map })!;
    expect(candidate.status).toBe("unmapped");
    expect(candidate.archive_tier).toBeNull();
    expect(candidate.family).toBeNull();
    expect(candidate.observed_licence).toBeNull();
    expect(candidate.unmapped_values).toEqual(["cc by"]);
    expect(candidate.reason).toContain("licence-map.tsv");
  });

  it("takes the tier from the row and nothing else, including for a restrictive one", () => {
    const candidate = buildCandidate({
      target: target(),
      observations: [observation({ route: "crossref", value: "arXiv.org perpetual non-exclusive license 1.0" })],
      map,
    })!;
    expect(candidate.status).toBe("resolved");
    expect(candidate.archive_tier).toBe("t4-private");
  });

  it("never lets the proposed readings in the report set a tier", () => {
    // proposedMapKeys exists for one conditional figure in the report. If it
    // ever reached a candidate, an unreviewed string would become a tier. It
    // is empty since the mechanical spellings became rows of their own, so
    // what is pinned here is that an unreviewed string stays unmapped.
    expect(Object.keys(proposedMapKeys)).toEqual([]);
    const candidate = buildCandidate({ target: target(), observations: [observation({ route: "europepmc", value: "cc by" })], map })!;
    expect(candidate.status).toBe("unmapped");
    expect(candidate.archive_tier).toBeNull();
  });

  it("prefers a licence URL over a free-text label when both map to one family", () => {
    const candidate = buildCandidate({
      target: target(),
      observations: [observation({ route: "europepmc", value: "CC BY 4.0" }), observation()],
      map,
    })!;
    expect(candidate.observed_licence).toBe("https://creativecommons.org/licenses/by/4.0/");
    expect(candidate.family).toBe("cc-by");
  });

  it("keeps an unreviewed string from a second service visible on a resolved candidate", () => {
    const candidate = buildCandidate({
      target: target(),
      observations: [observation(), observation({ route: "europepmc", value: "cc by" })],
      map,
    })!;
    expect(candidate.status).toBe("resolved");
    expect(candidate.archive_tier).toBe("t0-public");
    expect(candidate.unmapped_values).toEqual(["cc by"]);
  });
});

describe("two services that disagree resolve to nothing", () => {
  it("records a conflict with both statements and no tier", () => {
    const candidate = buildCandidate({
      target: target(),
      observations: [observation(), observation({ route: "github", value: "MIT", field: "license.spdx_id" })],
      map,
    })!;
    expect(candidate.status).toBe("conflict");
    expect(candidate.archive_tier).toBeNull();
    expect(candidate.observed_licence).toBeNull();
    expect(candidate.reason).toContain("crossref");
    expect(candidate.reason).toContain("github");
  });

  it("writes no candidate at all when no service stated a licence", () => {
    expect(buildCandidate({ target: target(), observations: [], map })).toBeNull();
  });
});

describe("every candidate carries its evidence", () => {
  it("names the endpoint, the field, the value as served and the date", () => {
    const candidate = candidateSchema.parse(buildCandidate({ target: target(), observations: [observation()], map })!);
    expect(candidate.observations).toHaveLength(1);
    const [only] = candidate.observations;
    expect(only.endpoint).toBe("https://api.crossref.org/works/10.1/one");
    expect(only.field).toBe("message.license[content-version=vor].URL");
    expect(only.value).toBe("https://creativecommons.org/licenses/by/4.0/");
    expect(only.observed_at).toBe("2026-11-17T12:00:00Z");
  });

  it("refuses a candidate with no observation at all", () => {
    expect(() => candidateSchema.parse({ ...buildCandidate({ target: target(), observations: [observation()], map })!, observations: [] })).toThrow();
  });
});

const client = (transport: Transport) => new Client({ transport, delayMs: 0, attempts: 2, backoffMs: 1 });

describe("the routes read the field the service states and no more", () => {
  it("takes a Crossref licence URL at the version of record and drops a text-mining grant", async () => {
    const asked: string[] = [];
    const transport = transportFor(
      {
        "https://api.crossref.org/works/10.1/one": {
          body: {
            message: {
              license: [
                { URL: "https://www.springer.com/tdm", "content-version": "tdm" },
                { URL: "https://creativecommons.org/licenses/by/4.0/", "content-version": "vor" },
              ],
            },
          },
        },
      },
      asked,
    );
    const result = await crossrefLicences("10.1/one", client(transport), null);
    expect(result.values.map((value) => value.value)).toEqual(["https://creativecommons.org/licenses/by/4.0/"]);
    expect(result.reason).toBeNull();
  });

  it("keeps a contact out of the endpoint it records", async () => {
    const asked: string[] = [];
    const transport = transportFor({ "https://api.crossref.org/works/10.1/one": { body: { message: { license: [] } } } }, asked);
    const result = await crossrefLicences("10.1/one", client(transport), "someone@example.org");
    expect(asked[0]).toContain("mailto=");
    expect(result.endpoint).not.toContain("mailto");
    expect(result.reason).toBe("no_licence_in_metadata");
  });

  it("calls a Crossref work with no licence array unresolved rather than restricted", async () => {
    const transport = transportFor({ "https://api.crossref.org/works/10.1/two": { body: { message: {} } } });
    const result = await crossrefLicences("10.1/two", client(transport), null);
    expect(result.values).toEqual([]);
    expect(result.reason).toBe("no_licence_in_metadata");
  });

  it("takes GitHub's SPDX identifier at the pinned commit", async () => {
    const asked: string[] = [];
    const sha = "941cf20934bef06c6fdae558c5e24765bd07ddfa";
    const transport = transportFor({ "https://api.github.com/repos/o/r/license": { body: { name: "LICENSE", license: { spdx_id: "MIT" } } } }, asked);
    const result = await githubLicence({ owner: "o", repo: "r", ref: sha }, client(transport), null);
    expect(asked[0]).toContain(`?ref=${sha}`);
    expect(result.values[0].value).toBe("MIT");
    expect(result.values[0].field).toContain("license.spdx_id");
  });

  it("leaves a licence file GitHub could not identify unresolved", async () => {
    const transport = transportFor({ "https://api.github.com/repos/o/r/license": { body: { name: "LICENSE", license: { spdx_id: "NOASSERTION" } } } });
    const result = await githubLicence({ owner: "o", repo: "r", ref: null }, client(transport), null);
    expect(result.values).toEqual([]);
    expect(result.reason).toBe("not_asserted");
  });

  it("takes a Hugging Face card licence at the pinned revision and reports two as two", async () => {
    const asked: string[] = [];
    const sha = "78ec8156c2ffb3e5475277fdb7eb603294224e53";
    const transport = transportFor(
      { "https://huggingface.co/api/datasets/o/n/revision": { body: { cardData: { license: ["mit", "cc-by-4.0"] } } } },
      asked,
    );
    const result = await huggingfaceLicence({ kind: "datasets", id: "o/n", revision: sha }, client(transport));
    expect(asked[0]).toContain(`/revision/${sha}`);
    expect(result.values.map((value) => value.value)).toEqual(["mit", "cc-by-4.0"]);
  });

  it("treats a card that says other as stating nothing", async () => {
    const transport = transportFor({ "https://huggingface.co/api/models/o/n": { body: { cardData: { license: "other" } } } });
    const result = await huggingfaceLicence({ kind: "models", id: "o/n", revision: null }, client(transport));
    expect(result.values).toEqual([]);
    expect(result.reason).toBe("not_asserted");
  });

  it("takes the preprint licence of the version the URL pins", async () => {
    const transport = transportFor({
      "https://api.biorxiv.org/details/biorxiv/10.1101/one": {
        body: {
          collection: [
            { version: "1", license: "cc_by" },
            { version: "2", license: "cc_by_nc_nd" },
          ],
        },
      },
    });
    const result = await preprintLicence({ server: "biorxiv", doi: "10.1101/one", version: "2" }, client(transport));
    expect(result.values.map((value) => value.value)).toEqual(["cc_by_nc_nd"]);
    expect(result.values[0].field).toBe("collection[version=2].license");
  });

  it("resolves nothing when versions disagree and the URL pins none", async () => {
    const transport = transportFor({
      "https://api.biorxiv.org/details/biorxiv/10.1101/one": {
        body: {
          collection: [
            { version: "1", license: "cc_by" },
            { version: "2", license: "cc_by_nc_nd" },
          ],
        },
      },
    });
    const result = await preprintLicence({ server: "biorxiv", doi: "10.1101/one", version: null }, client(transport));
    expect(result.values).toEqual([]);
    expect(result.reason).toBe("ambiguous_version");
  });

  it("names the one record a Europe PMC candidate rests on, and the batch the run actually asked", async () => {
    const asked: string[] = [];
    const transport = transportFor(
      {
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search": {
          body: {
            resultList: {
              result: [
                { pmcid: "PMC1", license: "cc by" },
                { pmcid: "PMC2", license: null },
              ],
            },
          },
        },
      },
      asked,
    );
    const results = await europepmcLicences(["PMC1", "PMC2", "PMC3"], client(transport));
    expect(asked, "one request for the batch").toHaveLength(1);
    expect(asked[0]).toContain("PMCID%3APMC1%20OR%20PMCID%3APMC2%20OR%20PMCID%3APMC3");
    const first = results.get("PMC1")!;
    expect(first.values[0].value).toBe("cc by");
    expect(first.endpoint).toContain("query=PMCID%3APMC1&");
    expect(first.endpoint).not.toContain("PMC2");
    expect(first.request).toBe(asked[0]);
    expect(results.get("PMC2")!.reason).toBe("no_licence_in_metadata");
    expect(results.get("PMC3")!.reason).toBe("not_found");
  });

  it("asks medRxiv when bioRxiv holds no post for the DOI", async () => {
    const asked: string[] = [];
    const transport = transportFor(
      {
        "https://api.biorxiv.org/details/biorxiv/10.1101/two": { body: { collection: [] } },
        "https://api.biorxiv.org/details/medrxiv/10.1101/two": { body: { collection: [{ version: "1", license: "cc_by" }] } },
      },
      asked,
    );
    const result = await preprintLicence({ server: null, doi: "10.1101/two", version: null }, client(transport));
    expect(asked).toHaveLength(2);
    expect(result.values.map((value) => value.value)).toEqual(["cc_by"]);
  });
});

describe("a host that refuses is backed off and then left alone", () => {
  it("retries a 503 and takes the answer when it comes", async () => {
    let calls = 0;
    const transport: Transport = async () => {
      calls += 1;
      return calls === 1 ? { status: 503, body: "" } : { status: 200, body: JSON.stringify({ message: { license: [{ URL: "https://creativecommons.org/licenses/by/4.0/", "content-version": "vor" }] } }) };
    };
    const result = await crossrefLicences("10.1/one", client(transport), null);
    expect(calls).toBe(2);
    expect(result.values[0].value).toBe("https://creativecommons.org/licenses/by/4.0/");
  });

  it("stops asking a host that keeps refusing and reports it", async () => {
    let calls = 0;
    const transport: Transport = async () => {
      calls += 1;
      return { status: 429, body: "" };
    };
    const shared = client(transport);
    const first = await crossrefLicences("10.1/one", shared, null);
    expect(first.reason).toBe("host_stopped");
    const before = calls;
    const second = await crossrefLicences("10.1/two", shared, null);
    expect(second.reason).toBe("host_stopped");
    expect(calls, "nothing further is asked of a stopped host").toBe(before);
    expect(shared.stopped.has("api.crossref.org")).toBe(true);
    await expect(shared.get("https://api.crossref.org/works/10.1/three")).rejects.toBeInstanceOf(HostStopped);
  });
});

/** A store of three sources: one GitHub repository, one DOI with a recorded
 * licence, and one host no service covers. */
function temporaryStore(): string {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "licence-resolve-"));
  roots.push(root);
  fs.mkdirSync(path.join(root, "data/entities"), { recursive: true });
  fs.mkdirSync(path.join(root, "data/archive"), { recursive: true });
  const sources = [
    {
      id: "repo-source",
      kind: "source",
      attributes: { artifact_url: "https://raw.githubusercontent.com/o/r/941cf20934bef06c6fdae558c5e24765bd07ddfa/README.md" },
    },
    {
      id: "doi-source",
      kind: "source",
      attributes: { url: "https://example.org/article", doi: "10.1/one", licence: "CC BY 4.0" },
    },
    { id: "nowhere-source", kind: "source", attributes: { url: "https://predictioncenter.org/casp15/" } },
  ];
  fs.writeFileSync(path.join(root, "data/entities/sources.jsonl"), sources.map((source) => JSON.stringify(source)).join("\n") + "\n");
  const rows = [
    "licence\tfamily\ttier\tbasis\tnote",
    "MIT\tpermissive-code\tt0-public\tidentifier\t",
    "CC BY 4.0\tcc-by\tt0-public\tidentifier\t",
    "https://creativecommons.org/licenses/by/4.0/\tcc-by\tt0-public\tprose\t",
  ];
  fs.writeFileSync(path.join(root, "data/archive/licence-map.tsv"), `${rows.join("\n")}\n`);
  return root;
}

describe("a whole run", () => {
  const answers = {
    "https://api.github.com/repos/o/r/license": { body: { name: "LICENSE", license: { spdx_id: "MIT" } } },
    "https://api.crossref.org/works/10.1/one": { body: { message: { license: [{ URL: "https://creativecommons.org/licenses/by/4.0/", "content-version": "vor" }] } } },
  };

  it("writes one candidate per source a service answered for, and a receipt per attempt", async () => {
    const root = temporaryStore();
    const asked: string[] = [];
    const result = await runResolve({ root, date: "2026-11-17", transport: transportFor(answers, asked), delayMs: 0 });
    expect(result.candidates.map((candidate) => candidate.source_id)).toEqual(["doi-source", "repo-source"]);
    expect(result.candidates.every((candidate) => candidate.status === "resolved")).toBe(true);
    // nowhere-source is asked nothing, so it carries no receipt and no candidate.
    expect(result.receipts.map((receipt) => receipt.source_id).includes("nowhere-source")).toBe(false);
    expect(result.targets).toHaveLength(3);
  });

  it("asks one repository once however many sources share it", async () => {
    const root = temporaryStore();
    const sources = fs.readFileSync(path.join(root, "data/entities/sources.jsonl"), "utf8").trim().split("\n");
    const second = JSON.parse(sources[0]) as { id: string; attributes: { artifact_url: string } };
    second.id = "repo-source-two";
    second.attributes.artifact_url = second.attributes.artifact_url.replace("README.md", "LICENSE");
    fs.writeFileSync(path.join(root, "data/entities/sources.jsonl"), `${[...sources, JSON.stringify(second)].join("\n")}\n`);
    const asked: string[] = [];
    const result = await runResolve({ root, date: "2026-11-17", transport: transportFor(answers, asked), delayMs: 0 });
    expect(asked.filter((url) => url.includes("/repos/o/r/license"))).toHaveLength(1);
    expect(result.candidates.filter((candidate) => candidate.source_id.startsWith("repo-source"))).toHaveLength(2);
  });

  it("counts a route that applied and stated nothing, so the hit rate is measured", async () => {
    const root = temporaryStore();
    const result = await runResolve({
      root,
      date: "2026-11-17",
      transport: transportFor({ "https://api.crossref.org/works/10.1/one": { body: { message: {} } } }),
      delayMs: 0,
    });
    const counts = countRun(result, readLicenceMap(root));
    expect(counts.by_route.crossref.sources).toBe(1);
    expect(counts.by_route.crossref.licence).toBe(0);
    expect(counts.by_route.crossref.by_reason.no_licence_in_metadata).toBe(1);
    expect(counts.by_route.github.licence).toBe(0);
    expect(counts.by_route.github.by_reason.not_found).toBe(1);
  });

  it("reports how many sources leave t4-private and never counts an unmapped string among them", async () => {
    const root = temporaryStore();
    const result = await runResolve({
      root,
      date: "2026-11-17",
      transport: transportFor({ ...answers, "https://api.github.com/repos/o/r/license": { body: { license: { spdx_id: "BSD-2-Clause" } } } }),
      delayMs: 0,
    });
    const counts = countRun(result, readLicenceMap(root));
    // The repository source is at t4-private with no recorded licence and
    // BSD-2-Clause has no row, so it stays put and is reported loudly.
    expect(counts.by_status.unmapped).toBe(1);
    expect(counts.leaves_t4).toBe(0);
    expect(counts.unmapped_strings[0].value).toBe("BSD-2-Clause");
    // The DOI source already carries CC BY 4.0, so it is not at t4 either.
    expect(counts.by_status.resolved).toBe(1);
  });

  it("counts a source out of t4-private when a mapped value says so", async () => {
    const root = temporaryStore();
    const result = await runResolve({ root, date: "2026-11-17", transport: transportFor(answers), delayMs: 0 });
    const counts = countRun(result, readLicenceMap(root));
    expect(counts.leaves_t4).toBe(1);
    expect(counts.by_tier["t0-public"]).toBe(2);
    expect(renderReport(result, counts)).toContain("it stands today: **1**");
  });

  it("asks nothing on a second run when the first run's responses are cached", async () => {
    const root = temporaryStore();
    const cacheDir = path.join(root, "cache");
    const asked: string[] = [];
    const first = await runResolve({ root, date: "2026-11-17", transport: transportFor(answers, asked), cacheDir, delayMs: 0 });
    const count = asked.length;
    expect(count).toBeGreaterThan(0);
    const second = await runResolve({ root, date: "2026-11-17", transport: transportFor(answers, asked), cacheDir, delayMs: 0 });
    expect(asked).toHaveLength(count);
    // Identical down to the date: a cached response keeps the date of the
    // transfer that produced it, so a rerun does not restate an old
    // observation as today's.
    expect(second.candidates).toEqual(first.candidates);
  });

  it("writes candidates the licence work can read back", async () => {
    const root = temporaryStore();
    const result = await runResolve({ root, date: "2026-11-17", transport: transportFor(answers), delayMs: 0 });
    fs.mkdirSync(path.dirname(candidatesPath(root)), { recursive: true });
    fs.writeFileSync(candidatesPath(root), `${result.candidates.map((candidate) => canonicalLine(candidate as unknown as Record<string, unknown>)).join("\n")}\n`);
    const read = readCandidates(root);
    expect([...read.keys()]).toEqual(["doi-source", "repo-source"]);
    expect(read.get("repo-source")!.observed_licence).toBe("MIT");
    expect(read.get("repo-source")!.observations[0].field).toContain("license.spdx_id");
  });

  it("reads no candidates when the file is not there", () => {
    expect(readCandidates(temporaryStore()).size).toBe(0);
  });

  it("changes no source record", async () => {
    const root = temporaryStore();
    const before = fs.readFileSync(path.join(root, "data/entities/sources.jsonl"), "utf8");
    await runResolve({ root, date: "2026-11-17", transport: transportFor(answers), delayMs: 0 });
    expect(fs.readFileSync(path.join(root, "data/entities/sources.jsonl"), "utf8")).toBe(before);
  });

  it("runs only the routes it is asked for", async () => {
    const root = temporaryStore();
    const asked: string[] = [];
    await runResolve({ root, date: "2026-11-17", transport: transportFor(answers, asked), delayMs: 0, routes: ["github"] });
    expect(asked.every((url) => url.includes("api.github.com"))).toBe(true);
  });
});

describe("the resolver and the committed licence map", () => {
  it("proposes a row that exists in the map for every string it proposes a reading for", () => {
    const committed = readLicenceMap();
    const missing = Object.entries(proposedMapKeys)
      .filter(([, key]) => !committed.has(key))
      .map(([value, key]) => `${value} points at ${key}`);
    expect(missing, "a proposed reading has to point at a row the map already carries").toEqual([]);
  });

  it("proposes nothing for a string the map already carries", () => {
    const committed = readLicenceMap();
    expect(Object.keys(proposedMapKeys).filter((value) => committed.has(value))).toEqual([]);
  });

  it("reads a spelling a service serves through the committed map, and still fails on a string nobody reviewed", () => {
    // The four largest strings of the 2026-11-17 run, and the property the
    // rows were added without giving up: a value the map has no row for is
    // unmapped, never a guess at a family.
    const committed = readLicenceMap();
    expect(committed.get("cc by")?.archive_tier).toBe("t0-public");
    expect(committed.get("https://creativecommons.org/licenses/by/4.0")?.archive_tier).toBe("t0-public");
    expect(committed.get("http://creativecommons.org/licenses/by/4.0/")?.archive_tier).toBe("t0-public");
    expect(committed.get("cc by-nc-nd")?.archive_tier).toBe("t3-verbatim-nd-nc");
    const candidate = buildCandidate({
      target: target(),
      observations: [observation({ route: "github", value: "Spelled a way nobody has reviewed" })],
      map: committed,
    })!;
    expect(candidate.status).toBe("unmapped");
    expect(candidate.archive_tier).toBeNull();
  });

  it("keeps the route list and the report's route order the same", () => {
    expect([...resolveRoutes]).toEqual(["crossref", "github", "huggingface", "preprint", "europepmc"]);
  });
});
