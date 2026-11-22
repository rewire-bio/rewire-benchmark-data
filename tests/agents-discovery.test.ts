import { existsSync, mkdtempSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import {
  AREAS, GENOMIC_AREAS, LABELS, LIMITS, PRICES, PROTEIN_AREAS, SCAN_LANES, Usage, ageInDays, clean, dataLabels, findDuplicate,
  findRejected, githubClient, identifiersOf, keyOf, knownTitles, main, matchForm, nearMatches, parseBlogIndex, planFiling,
  callCounts, DIRECT_ONLY, laneLine, pendingDirect, rejectedDirectOnly, queriesOf, readRejected, readStoreNames, redactor, renderArticleIssue, renderDataIssue, renderSummary, scanEnding, scanPrompt, spellForm, tierOf,
  toolActivity, triageLane, verdictOf,
} from "../scripts/agents/discovery.mjs";

// The discovery scan (#254). Everything here runs without an API key or network: the dry run
// reads candidates, issues, store names and articles from tests/agents-discovery-fixtures.
const FIXTURES = "tests/agents-discovery-fixtures";
const now = new Date("2026-11-17T08:00:00Z");
const quiet = () => {};

async function dryRun(extraArgs: string[] = [], env: Record<string, string> = {}) {
  return main(["--dry-run", "--fixtures", FIXTURES, "--max-pairs", "10", ...extraArgs], env, { now, log: quiet });
}

describe("depth tier", () => {
  it("follows docs/tiers.md: genomic beats protein beats everything else", () => {
    expect(tierOf(["dna-genomes"])).toBe(1);
    expect(tierOf(["rna-transcriptomes", "protein-structure"])).toBe(1);
    expect(tierOf(["protein-function"])).toBe(2);
    expect(tierOf(["single-cell", "molecular-interactions"])).toBe(3);
    expect(tierOf([])).toBe(3);
  });
  it("uses the same tier area lists as shared/omics/depth-tier.ts and only areas in the vocabulary", () => {
    const rule = readFileSync("shared/omics/depth-tier.ts", "utf8");
    const read = (name: string) => [...(new RegExp(`export const ${name} = \\[([^\\]]*)\\]`).exec(rule)?.[1] ?? "").matchAll(/"([^"]+)"/g)].map((m) => m[1]);
    expect(GENOMIC_AREAS).toEqual(read("genomicAreas"));
    expect(PROTEIN_AREAS).toEqual(read("proteinAreas"));
    const vocab = [...readFileSync("data/vocab/area.ttl", "utf8").matchAll(/^:([a-z-]+) a skos:Concept/gm)].map((m) => m[1]);
    // A subset, so a new area added to the vocabulary does not fail this test.
    expect(AREAS.filter((a) => !vocab.includes(a))).toEqual([]);
  });
});

describe("deduplication", () => {
  const issues = JSON.parse(readFileSync(`${FIXTURES}/issues.json`, "utf8"));
  const candidate = (name: string, extra: Record<string, unknown> = {}) => ({ name, aliases: [], sources: [], ...extra });

  it("matches issues filed by hand or by the old automation by name in the title", () => {
    expect(findDuplicate(candidate("MIMOSA"), { issues })?.ref).toBe("rewire-bio/rewire-benchmark-data#249");
    expect(findDuplicate(candidate("Enchant v3"), { issues })?.ref).toBe("rewire-bio/rewire-benchmark-data#229");
  });
  it("does not match a name inside a longer word", () => {
    expect(findDuplicate(candidate("Enchant"), { issues })?.ref).toBe("rewire-bio/rewire-benchmark-data#229");
    expect(findDuplicate(candidate("Mimo"), { issues })).toBeNull();
  });
  it("matches its own marker even after the title was edited", () => {
    expect(findDuplicate(candidate("HelixMark fixture"), { issues })?.reason).toContain("filed before");
  });
  it("matches a primary DOI across preprint versions", () => {
    const c = candidate("Something else", { sources: [{ url: "https://www.biorxiv.org/content/10.1101/2026.01.15.599999v3", role: "preprint" }] });
    expect(identifiersOf(c)).toContain("10.1101/2026.01.15.599999");
    expect(findDuplicate(c, { issues })?.ref).toBe("rewire-bio/rewire-benchmark-data#229");
  });
  it("reads a DOI from bioRxiv full-text links", () => {
    const c = candidate("x", { sources: [{ url: "https://www.biorxiv.org/content/10.1101/2026.01.15.599999v2.full.pdf", role: "preprint" }, { url: "https://arxiv.org/pdf/2611.01234v2", role: "preprint" }] });
    expect(identifiersOf(c)).toEqual(["10.1101/2026.01.15.599999", "2611.01234"]);
  });
  it("ignores identifiers from announcements and other non-primary sources", () => {
    const c = candidate("Something else", { sources: [{ url: "https://github.com/iambic-fixture/enchant", role: "announcement" }] });
    expect(findDuplicate(c, { issues })).toBeNull();
  });
  it("matches record-store names and reported names, streamed from the entity files", async () => {
    const names = await readStoreNames(`${FIXTURES}/entities`);
    expect(findDuplicate(candidate("Bacformer"), { storeNames: names })?.where).toBe("store");
    expect(findDuplicate(candidate("ProteinGym v1.3"), { storeNames: names })?.ref).toBe("discovery-benchmark-proteingym");
    expect(findDuplicate(candidate("ESM 2"), { storeNames: names })?.ref).toBe("discovery-model-esm-2");
    // The scan reads the store in matchForm, so a name written without the hyphen still matches.
    const matched = await readStoreNames(`${FIXTURES}/entities`, matchForm);
    expect(findDuplicate(candidate("ESM2"), { storeNames: matched })?.ref).toBe("discovery-model-esm-2");
    expect(findDuplicate(candidate("ProteinGym v1.3"), { storeNames: matched })?.ref).toBe("discovery-benchmark-proteingym");
    expect(findDuplicate(candidate("ESM3"), { storeNames: matched })).toBeNull();
  });
});

describe("issue bodies", () => {
  const judgements = JSON.parse(readFileSync(`${FIXTURES}/judgements.json`, "utf8"));
  const geno = judgements[0];

  it("strips @-mentions, dashes and HTML comments from model text", () => {
    expect(clean("by @someone \u2014 20\u201326% <!-- discovery-key: x -->")).toBe("by someone, 20-26%");
    expect(clean("email a@b.org and `@scope/pkg`")).toBe("email a@b.org and `@scope/pkg`");
  });
  it("labels the data issue with its tier, keeps a marker and states the tier scope", () => {
    const issue = renderDataIssue(geno, { tier: 1, runDate: "2026-11-17", article: { inline: true }, dedupNote: "No match." });
    expect(issue.labels).toEqual(["entity-request", "tier-1"]);
    expect(issue.title).toBe("Add discovered model GenoNova fixture: Predicts variant effects on gene expression from DNA sequence.");
    expect(issue.body).toContain(`<!-- discovery-key: ${keyOf(geno.name)} -->`);
    expect(issue.body).toContain("Tier 1 (DNA and RNA genomics): full records, evaluations");
    expect(issue.body).toContain("## Article request");
    expect(issue.body).toContain("(announcement; seen in search results, not opened)");
    expect(issue.body).toContain("(preprint; retrieved 2026-11-17)");
    expect(issue.body).not.toMatch(/[\u2013\u2014]|@fixture_author/);
  });
  it("asks for a metadata-only record at tier 3", () => {
    const issue = renderDataIssue(judgements[2], { tier: 3, runDate: "2026-11-17", article: null, dedupNote: "" });
    expect(issue.labels).toEqual(["entity-request", "tier-3"]);
    expect(issue.body).toContain("metadata-only record. Do not extract evaluations or results.");
  });
  it("labels the article issue article and links its data issue", () => {
    const issue = renderArticleIssue(geno, { dataUrl: "https://github.com/rewire-bio/rewire-benchmark-data/issues/999", runDate: "2026-11-17", dedupNote: "" });
    expect(issue.labels).toEqual(["article"]);
    expect(issue.title).toBe("Research GenoNova fixture: what GenoNova fixture changes for practitioners");
    expect(issue.body.split("\n")[0]).toBe("Counterpart database issue: https://github.com/rewire-bio/rewire-benchmark-data/issues/999");
  });
});

describe("dry run", () => {
  it("files every new tier with an article request and skips the rest with a reason", async () => {
    const { planned, skipped, summary } = await dryRun();
    expect(planned.map((p) => [p.name, p.tier, p.labels])).toEqual([
      ["GenoNova fixture", 1, ["entity-request", "tier-1"]],
      ["ProtSpec fixture", 2, ["entity-request", "tier-2"]],
      ["CellAtlasLM fixture", 3, ["entity-request", "tier-3"]],
      ["SpliceAtlas fixture", 1, ["entity-request", "tier-1"]],
      ["RiboScope fixture", 1, ["entity-request", "tier-1"]],
    ]);
    // Without a rewire.it token the article request is a section of the data issue.
    for (const p of planned.filter((p) => p.name !== "SpliceAtlas fixture")) {
      expect(p.article).toBeNull();
      expect(p.data.body).toContain("## Article request");
    }
    // A published article already covers SpliceAtlas: link it instead of requesting another.
    const splice = planned.find((p) => p.name === "SpliceAtlas fixture")!;
    expect(splice.data.body).toContain("Existing article: https://rewirebio.io/blog/spliceatlas-fixture-explained/");
    expect(splice.data.body).not.toContain("## Article request");
    expect(Object.fromEntries(skipped!.map((s) => [s.name, s.reason]))).toEqual({
      MIMOSA: '"mimosa" is in the title of rewire-bio/rewire-benchmark-data#249',
      Bacformer: '"bacformer" matches store record bacformer-20261115-model-bacformer',
      "Enchant Next fixture": "10.1101/2026.01.15.599999 is cited in rewire-bio/rewire-benchmark-data#229",
      "HelixMark fixture": "filed before as rewire-bio/rewire-benchmark-data#301",
      "Weak fixture": "judge: software wrapper with no new model",
      "GenoNova-fixture v1": "repeats GenoNova fixture in this run",
      "Unsourced fixture": "no name, task or retrieved primary source",
    });
    expect(summary).toContain("## Discovery scan, 2026-11-17 (dry run)");
    expect(summary).toContain("No model calls.");
  });

  it("pairs an article issue in rewire.it when it has a token, and checks rewire.it issues too", async () => {
    const { planned, skipped } = await dryRun([], { ARTICLE_TOKEN: "dry" });
    expect(planned.map((p) => p.name)).not.toContain("RiboScope fixture");
    expect(skipped!.find((s) => s.name === "RiboScope fixture")?.reason).toBe('"riboscope fixture" is in the title of rewire-bio/rewire.it#460');
    const geno = planned.find((p) => p.name === "GenoNova fixture")!;
    expect(geno.article?.labels).toEqual(["article"]);
    expect(geno.data.body).not.toContain("## Article request");
  });

  it("stops at the per-run cap and leaves the rest for the next run", async () => {
    const { planned, skipped } = await dryRun(["--max-pairs", "2"]);
    expect(planned).toHaveLength(2);
    expect(skipped!.filter((s) => s.reason.startsWith("over the per-run cap"))).toHaveLength(3);
  });

  it("writes the planned issues to --out for inspection", async () => {
    const out = mkdtempSync(join(tmpdir(), "discovery-"));
    await dryRun(["--out", out]);
    expect(readdirSync(out).sort()).toEqual(["1-data.md", "2-data.md", "3-data.md", "4-data.md", "5-data.md", "plan.json", "scan", "usage.json"]);
  });
});

// What each run records about its scan lanes. The dry run reads tests/agents-discovery-fixtures/scan.json,
// which is written for these tests and is not a recorded API reply.
describe("lane files and lane lines", () => {
  const lane = (out: string, name: string) => JSON.parse(readFileSync(join(out, "scan", `${name}.json`), "utf8"));

  it("writes, for each lane of a dry run, the queries, the notes, the raw candidates and each drop with its reason", async () => {
    const out = mkdtempSync(join(tmpdir(), "discovery-"));
    const lines: string[] = [];
    const { planned, lanes } = await main(["--dry-run", "--fixtures", FIXTURES, "--max-pairs", "10", "--out", out], {}, { now, log: (m: string) => lines.push(m) });
    expect(readdirSync(join(out, "scan")).sort()).toEqual([
      "cells-and-other-biology-notes.md", "cells-and-other-biology.json", "genomics-notes.md", "genomics.json", "proteins-notes.md", "proteins.json",
    ]);
    const genomics = lane(out, "genomics");
    // One query was given to the search tool, one was inside code, one search returned an error.
    expect(genomics.queries).toEqual(["bioRxiv genomic language model November 2026", "variant effect prediction benchmark 2026", "site:huggingface.co RNA foundation model"]);
    expect(genomics.tool_activity.find((a: any) => a.results)?.results.map((r: any) => r.url)).toEqual(["https://www.biorxiv.org/content/10.1101/2026.11.10.700001v1", "https://example.org/news/ai-biology-roundup"]);
    expect(genomics.tool_activity.find((a: any) => a.error)?.error).toBe("max_uses_exceeded");
    expect(genomics.tool_activity.find((a: any) => a.stdout)?.stdout).toContain("VariantBench fixture");
    expect(genomics.requests).toEqual([{ stop_reason: "end_turn", input_tokens: 9000, output_tokens: 900, web_search_requests: 3, web_fetch_requests: 1, tool_use_reported: true, text_characters: 260 }]);
    // The candidate list is kept as it came back, before any filter.
    expect(genomics.raw_candidates.map((c: any) => c.name)).toEqual(["GenoNova fixture", "VariantBench fixture", "Bacformer", "PipeWrap fixture", ""]);
    expect(genomics.dropped).toEqual([
      { name: "Bacformer", category: "known", reason: 'already known, not judged: "bacformer" matches store record bacformer-20261115-model-bacformer' },
      { name: "PipeWrap fixture", category: "other", reason: "triage: workflow wrapper with no model" },
      { name: "(no name)", category: "other", reason: "the candidate has no name" },
    ]);
    expect(genomics.to_judge).toEqual(["GenoNova fixture", "VariantBench fixture"]);
    // Two searches and the fetch were direct calls; code made the third search.
    expect(genomics.counts).toMatchObject({ direct_searches: 2, code_searches: 1, direct_fetches: 1, code_fetches: 0 });
    expect(genomics.tool_activity.filter((a: any) => a.call).map((a: any) => [a.name, a.call, a.caller])).toEqual([
      ["web_search", "direct", undefined], ["web_search", "code", "code_execution_20260120"], ["web_search", "direct", undefined], ["web_fetch", "direct", undefined],
    ]);
    expect(genomics.counts).toMatchObject({ searches: 3, fetches: 1, raw: 5, known: 1, remembered: 0, other: 2, to_judge: 2 });
    expect(readFileSync(join(out, "scan", "genomics-notes.md"), "utf8")).toContain("VariantBench fixture, a benchmark of variant effect predictors");
    // The page text a fetch returns and encrypted search content are never copied.
    const written = readdirSync(join(out, "scan")).map((f) => readFileSync(join(out, "scan", f), "utf8")).join("\n");
    expect(written).not.toContain("Full page text");
    expect(written).not.toContain("EqgfCioIARgB");
    expect(written).not.toContain("encrypted_content");

    expect(lane(out, "proteins").dropped.map((d: any) => [d.name, d.category])).toEqual([["MIMOSA", "known"], ["Enchant-3", "known"], ["GenoNova", "other"]]);
    expect(lines.filter((l) => l.startsWith("scan "))).toEqual([
      "scan genomics: 3 searches (2 direct), 5 raw candidates, 1 dropped as known, 0 dropped as remembered, 2 dropped for another reason, 2 to judge",
      "scan proteins: 2 searches (1 direct), 3 raw candidates, 2 dropped as known, 0 dropped as remembered, 1 dropped for another reason, 0 to judge",
      "scan cells and other biology: 8 searches, 0 raw candidates, 0 dropped as known, 0 dropped as remembered, 0 dropped for another reason, 0 to judge",
    ]);
    for (const report of lanes!) {
      const n = lane(out, report.lane.replace(/ /g, "-")).counts;
      expect(n.known + n.remembered + n.other + n.to_judge).toBe(n.raw);
    }
    // The lane files do not change what a dry run plans.
    expect(planned).toHaveLength(5);
  });

  it("puts the lane table in the summary", async () => {
    const { summary } = await dryRun();
    expect(summary).toContain("### Scan lanes");
    expect(summary).toContain("| genomics | read from fixtures | 3 | 1 | 5 | 1 | 0 | 2 | 2 |");
    expect(summary).toContain("| cells and other biology | read from fixtures | 8 | 0 | 0 | 0 | 0 | 0 | 0 |");
  });

  it("reads tool blocks by their fields, so a block type it has not seen is still recorded", () => {
    const activity = toolActivity([
      { type: "text", text: "notes" },
      { type: "some_future_tool_use", name: "web_search", input: { query: "arXiv q-bio.GN DNA language model" } },
      { type: "some_future_tool_result", content: { results_blob: "x", content: [{ url: "https://arxiv.org/abs/2611.00001", title: "A DNA model", encrypted_content: "secret" }] } },
      { type: "server_tool_use", name: "bash_code_execution", input: { command: "search --query 'RNA structure benchmark'\n" + "#".repeat(5000) } },
      null,
    ]);
    expect(activity.map((a: any) => a.type)).toEqual(["some_future_tool_use", "some_future_tool_result", "server_tool_use"]);
    expect(activity[1].results).toEqual([{ url: "https://arxiv.org/abs/2611.00001", title: "A DNA model" }]);
    expect(activity[2].code).toMatch(/\[cut from 50\d\d characters\]$/);
    expect(queriesOf(activity)).toEqual(["arXiv q-bio.GN DNA language model", "RNA structure benchmark"]);
    expect(toolActivity(undefined)).toEqual([]);
  });

  it("marks each search and fetch call as direct or made from code, and counts them for the lane line", () => {
    const code = { type: "code_execution_20260120", tool_id: "srvtoolu_c" };
    const activity = toolActivity([
      { type: "server_tool_use", id: "srvtoolu_a", name: "web_search", input: { query: "one" } },
      { type: "web_search_tool_result", tool_use_id: "srvtoolu_a", content: [] },
      { type: "server_tool_use", id: "srvtoolu_b", name: "web_search", input: { query: "two" }, caller: { type: "direct" } },
      { type: "server_tool_use", id: "srvtoolu_c", name: "code_execution", input: { code: "await web_search({'query': q})" } },
      { type: "server_tool_use", id: "srvtoolu_d", name: "web_search", input: { query: "three" }, caller: code },
      { type: "web_search_tool_result", tool_use_id: "srvtoolu_d", caller: code, content: [] },
      { type: "server_tool_use", id: "srvtoolu_e", name: "web_fetch", input: { url: "https://example.org/a" }, caller: code },
      { type: "server_tool_use", id: "srvtoolu_f", name: "web_fetch", input: { url: "https://example.org/b" } },
    ]);
    // Only the calls are marked: not the results, and not the code call itself.
    expect(activity.map((a: any) => a.call)).toEqual(["direct", undefined, "direct", undefined, "code", undefined, "code", "direct"]);
    expect(activity.map((a: any) => a.caller)).toEqual([undefined, undefined, "direct", undefined, "code_execution_20260120", undefined, "code_execution_20260120", undefined]);
    expect(callCounts(activity)).toEqual({ direct_searches: 2, code_searches: 1, direct_fetches: 1, code_fetches: 1 });
    expect(callCounts(undefined)).toEqual({ direct_searches: 0, code_searches: 0, direct_fetches: 0, code_fetches: 0 });

    const report = (calls: any[]) => ({ lane: "genomics", status: "finished", requests: [{ web_search_requests: 8 }], activity: toolActivity(calls), raw_candidates: [], dropped: [], to_judge: [] });
    const direct = Array.from({ length: 8 }, (_, i) => ({ type: "server_tool_use", name: "web_search", input: { query: `q${i}` } }));
    expect(laneLine(report(direct))).toMatch(/^scan genomics: 8 searches \(8 direct\), 0 raw candidates, /);
    // The run of 22 November 2026: every search made from code.
    expect(laneLine(report(direct.map((c) => ({ ...c, caller: code }))))).toMatch(/^scan genomics: 8 searches \(0 direct\), /);
    // A reply with no search call in it gives no count.
    expect(laneLine(report([]))).toMatch(/^scan genomics: 8 searches, /);
  });

  it("sorts each dropped candidate into known, remembered or another reason", () => {
    const candidate = (name: string, extra: any = {}) => ({ name, aliases: [], in_scope: true, reason: "", ...extra });
    const isKnown = (c: any) => c.name === "Held" ? { where: "store", reason: "in the store" } : c.name === "Rejected" ? { where: "rejected", reason: "rejected before" } : null;
    const seen = new Map([["earlier", "Earlier"]]);
    const { fresh, dropped } = triageLane([candidate("Held"), candidate("Rejected"), candidate("Weak", { in_scope: false, reason: "a wrapper" }), candidate("Earlier"), candidate("New"), {}], { isKnown, seen });
    expect(fresh.map((c: any) => c.name)).toEqual(["New"]);
    expect(dropped.map((d: any) => [d.name, d.category])).toEqual([["Held", "known"], ["Rejected", "remembered"], ["Weak", "other"], ["Earlier", "other"], ["(no name)", "other"]]);
    expect(laneLine({ lane: "genomics", status: "no notes; the last request stopped with refusal", requests: [{ web_search_requests: 2 }], raw_candidates: null, dropped: [], to_judge: [] }))
      .toBe("scan genomics: 2 searches, no candidate list (no notes; the last request stopped with refusal)");
  });

  it("finds the queries in a list that code loops over, in the order written", () => {
    const code = [
      "import asyncio",
      "queries = [",
      '    "bioRxiv DNA language model 2026",',
      "    'arXiv q-bio.GN variant effect benchmark',",
      "]",
      "results = await asyncio.gather(*[web_search(q) for q in queries])",
      'extra = web_search("site:huggingface.co RNA foundation model")',
      'labels = ["not a query"]',
      'search_results = [r["title"] for r in results]',
      'titles_of_queries = [r["url"] for r in results]',
    ].join("\n");
    const activity = toolActivity([{ type: "server_tool_use", name: "code_execution", input: { code } }]);
    expect(queriesOf(activity)).toEqual(["bioRxiv DNA language model 2026", "arXiv q-bio.GN variant effect benchmark", "site:huggingface.co RNA foundation model"]);
    // A list under a typed name, and a query built at run time, which is not found.
    expect(queriesOf(toolActivity([{ type: "server_tool_use", name: "code_execution", input: { code: 'search_terms: list[str] = ["genomic benchmark preprint"]\nweb_search(prefix + name)' } }]))).toEqual(["genomic benchmark preprint"]);
  });

  it("cuts what code printed at 4,000 characters, and keeps it: it can hold result text", () => {
    const [entry] = toolActivity([{ type: "code_execution_tool_result", content: { type: "code_execution_result", stdout: `Result title\n${"x".repeat(5000)}`, stderr: "e".repeat(4500), return_code: 0 } }]);
    expect(entry.stdout).toMatch(/^Result title\nx{3987} \[cut from 5013 characters\]$/);
    expect(entry.stderr).toMatch(/^e{4000} \[cut from 4500 characters\]$/);
  });

  it("says at the end of a lane line when the notes may be incomplete", () => {
    const report = (stop: string) => ({ lane: "genomics", status: scanEnding([{ stop_reason: "pause_turn" }, { stop_reason: stop }]), requests: [{ web_search_requests: 8 }], raw_candidates: [], dropped: [], to_judge: [] });
    expect(laneLine(report("end_turn"))).toBe("scan genomics: 8 searches, 0 raw candidates, 0 dropped as known, 0 dropped as remembered, 0 dropped for another reason, 0 to judge");
    expect(laneLine(report("max_tokens"))).toBe("scan genomics: 8 searches, 0 raw candidates, 0 dropped as known, 0 dropped as remembered, 0 dropped for another reason, 0 to judge (finished; the notes were cut at max_tokens and may be incomplete)");
    expect(laneLine(report("pause_turn"))).toContain("0 to judge (finished; the scan stopped at the pause_turn cap and the notes may be incomplete)");
  });

  it("keeps a bar or a line break in a lane status inside its table cell", () => {
    const summary = renderSummary({ mode: "live", runDate: "2026-11-22", usage: new Usage(), filed: [], skipped: [], lanes: [{ lane: "genomics", status: "failed: 500 upstream said a|b\nsecond line", requests: [], raw_candidates: null, dropped: [], to_judge: [] }] });
    expect(summary).toContain("| genomics | failed: 500 upstream said a\\|b second line | 0 | 0 | 0 | 0 | 0 | 0 | 0 |");
  });

  it("replaces a token as JSON writes it, when the value holds a quote or a backslash", () => {
    const token = 'tok"en\\with-escapes-0123';
    const redact = redactor({ GITHUB_TOKEN: token });
    expect(redact(JSON.stringify({ notes: `before ${token} after` }))).toBe('{"notes":"before [redacted] after"}');
    expect(redact(`plain ${token}`)).toBe("plain [redacted]");
  });

  it("replaces the value of a token and leaves short values and other text alone", () => {
    const redact = redactor({ ANTHROPIC_API_KEY: "sk-ant-fixture-0123456789", GH_TOKEN: "ghs_fixture0123456789", ARTICLE_TOKEN: "t" });
    expect(redact("key sk-ant-fixture-0123456789 and token ghs_fixture0123456789, not this")).toBe("key [redacted] and token [redacted], not this");
    expect(redactor({})("unchanged")).toBe("unchanged");
  });
});

describe("live mode without a key", () => {
  it("writes a notice and returns without reading GitHub or calling a model", async () => {
    const summaryFile = join(mkdtempSync(join(tmpdir(), "discovery-")), "summary.md");
    const github = new Proxy({}, { get: () => { throw new Error("GitHub must not be read"); } });
    const { planned } = await main([], { GITHUB_STEP_SUMMARY: summaryFile, ANTHROPIC_API_KEY: "" }, { now, log: quiet, github });
    expect(planned).toEqual([]);
    expect(readFileSync(summaryFile, "utf8")).toContain("Skipped: the ANTHROPIC_API_KEY secret is not set.");
  });
});

describe("usage", () => {
  it("prices tokens and web searches per model", () => {
    const usage = new Usage();
    usage.add("claude-sonnet-5-5", { input_tokens: 100_000, output_tokens: 10_000, cache_read_input_tokens: 50_000, server_tool_use: { web_search_requests: 10, web_fetch_requests: 4 } });
    usage.add("claude-haiku-5-5", { input_tokens: 20_000, output_tokens: 4_000 });
    expect(usage.costOf("claude-sonnet-5-5")).toBeCloseTo(0.2 + 0.1 + 0.005 + 0.1, 6);
    expect(usage.costOf("claude-haiku-5-5")).toBeCloseTo(0.002 + 0.002, 6);
    expect(usage.table()).toContain("| claude-sonnet-5-5 | 100000 | 0 | 50000 | 10000 | 10 | 4 | $0.4050 |");
  });
});

describe("blog index", () => {
  it("reads article links and their titles", () => {
    const html = '<a href="/blog/genomic-foundation-models-in-the-diagnostic-lab/"><h2>Genomic foundation models</h2></a><a href="/blog/">All</a><a href="https://rewirebio.io/blog/x-y/">X <em>Y</em></a>';
    expect(parseBlogIndex(html)).toEqual([
      { url: "https://rewirebio.io/blog/genomic-foundation-models-in-the-diagnostic-lab/", title: "Genomic foundation models" },
      { url: "https://rewirebio.io/blog/x-y/", title: "X Y" },
    ]);
  });
});

describe("workflow", () => {
  const workflow = readFileSync(".github/workflows/discovery.yml", "utf8");
  it("passes the key and the optional rewire.it token, and has a timeout", () => {
    expect(workflow).toContain("ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}");
    expect(workflow).toMatch(/timeout-minutes: \d+/);
    expect(workflow).toContain("actions/create-github-app-token");
  });
  it("only gets issue write access with the default token", () => {
    expect(workflow).toMatch(/permissions:\n {2}contents: read\n {2}issues: write\n/);
  });
});

describe("live path with stand-in clients", () => {
  // Stand-ins for the Anthropic and GitHub clients, so the model-call and filing code runs
  // without a key. The Sonnet turns return notes; the Haiku calls return the structured JSON.
  const judgements = JSON.parse(readFileSync(`${FIXTURES}/judgements.json`, "utf8"));
  const msg = (text: string, stop = "end_turn", usage = { input_tokens: 1000, output_tokens: 100, server_tool_use: { web_search_requests: 2, web_fetch_requests: 1 } }) =>
    ({ content: [{ type: "text", text }], stop_reason: stop, usage, stop_details: stop === "refusal" ? { category: "bio" } : null });

  function anthropic({ refuse = "", fail = "" } = {}) {
    const calls: { kind: string; params: any }[] = [];
    let paused = false;
    function stream(params: any) {
      calls.push({ kind: "stream", params });
      const prompt = String(params.messages[0].content);
      let reply;
      if (prompt.includes("Find AI-for-biology")) {
        // First scan turn pauses once to exercise the resume.
        reply = paused ? msg(`scan notes ${/Lane: ([^.]*)\./.exec(prompt)?.[1]}`) : msg("partial", "pause_turn");
        paused = true;
      } else if (refuse && prompt.includes(`Name: ${refuse}`)) reply = msg("", "refusal");
      else if (fail && prompt.includes(`Name: ${fail}`)) throw Object.assign(new Error("Overloaded"), { status: 529 });
      else reply = msg(`notes for ${/Name: (.*)/.exec(prompt)?.[1]}\nFILE`);
      return { finalMessage: async () => ({ ...reply, model: params.model }) };
    }
    return {
      calls,
      beta: { messages: { stream } },
      messages: {
        async create(params: any) {
          calls.push({ kind: "create", params });
          const notes = String(params.messages[0].content);
          if (notes.includes("scan notes genomics")) {
            return msg(JSON.stringify({ candidates: [
              { name: "GenoNova fixture", aliases: [], kind: "model", released: "2026-11-14", summary: "s", urls: ["https://doi.org/10.1101/2026.11.10.700001"], in_scope: true, reason: "" },
              { name: "MIMOSA", aliases: [], kind: "method", released: "", summary: "s", urls: [], in_scope: true, reason: "" },
              { name: "Off topic", aliases: [], kind: "model", released: "", summary: "s", urls: [], in_scope: false, reason: "not biology" },
              { name: "ProtSpec fixture", aliases: [], kind: "model", released: "", summary: "s", urls: [], in_scope: true, reason: "" },
            ] }), "end_turn", { input_tokens: 500, output_tokens: 50 } as any);
          }
          // The other two lanes find nothing.
          if (notes.includes("scan notes")) return msg(JSON.stringify({ candidates: [] }), "end_turn", { input_tokens: 500, output_tokens: 50 } as any);
          const name = /notes for (.*)/.exec(notes)?.[1];
          return msg(JSON.stringify(judgements.find((j: any) => j.name === name)), "end_turn", { input_tokens: 500, output_tokens: 50 } as any);
        },
      },
    };
  }

  function github(repo: string, issues: any[]) {
    const created: any[] = [];
    const updated: any[] = [];
    const labels: string[] = [];
    let next = 900;
    return {
      created, updated, labels,
      async listIssues(r: string) { expect(r).toBe(repo); return issues; },
      async ensureLabels(r: string, names: string[]) { labels.push(...names.map((n) => `${r}:${n}`)); },
      async createIssue(r: string, issue: any) { const number = next++; created.push({ repo: r, number, ...issue }); return { number, html_url: `https://github.com/${r}/issues/${number}` }; },
      async updateIssue(r: string, number: number, patch: any) { updated.push({ repo: r, number, ...patch }); },
    };
  }

  const blog = async () => ({ ok: true, status: 200, text: async () => "" });
  const env = { ANTHROPIC_API_KEY: "test", GITHUB_REPOSITORY: "rewire-bio/rewire-benchmark-data" };
  const args = ["--store-dir", `${FIXTURES}/entities`];

  it("scans, triages, judges and files paired issues with tier labels", async () => {
    const client = anthropic();
    const data = github("rewire-bio/rewire-benchmark-data", JSON.parse(readFileSync(`${FIXTURES}/issues.json`, "utf8")));
    const articles = github("rewire-bio/rewire.it", JSON.parse(readFileSync(`${FIXTURES}/article-issues.json`, "utf8")));
    const { planned, skipped, usage } = await main(args, { ...env, ARTICLE_TOKEN: "t" }, { now, log: quiet, anthropic: client, github: data, articleGithub: articles, fetch: blog });

    // The scan resumed its pause_turn; MIMOSA was dropped by name before judging; the judge used Sonnet with web tools.
    const streams = client.calls.filter((c) => c.kind === "stream");
    // Three scan lanes, one of them resumed, then two judge calls.
    expect(streams).toHaveLength(6);
    expect(streams.filter((c) => String(c.params.messages[0].content).includes("Find AI-for-biology")).map((c) => /Lane: ([^.]*)\./.exec(c.params.messages[0].content)![1]).sort())
      .toEqual(["cells and other biology", "cells and other biology", "genomics", "proteins"]);
    // A resume is given only the searches and fetches the first request left.
    expect(streams.slice(0, 3).map((c) => c.params.tools.map((t: any) => t.max_uses))).toEqual([
      [LIMITS.scanSearches, LIMITS.scanFetches], [LIMITS.scanSearches - 2, LIMITS.scanFetches - 1], [LIMITS.scanSearches, LIMITS.scanFetches],
    ]);
    expect(streams.every((c) => c.params.tools.map((t: any) => t.type).join() === "web_search_20260318,web_fetch_20260209")).toBe(true);
    // The scan runs on Haiku, without the fallback Haiku does not offer, and resumes its pause_turn.
    expect(streams.slice(0, 2).map((c) => [c.params.model, c.params.fallbacks])).toEqual([["claude-haiku-5-5", undefined], ["claude-haiku-5-5", undefined]]);
    expect(streams[1].params.messages.at(-1).role).toBe("assistant");
    // The judge runs on Sonnet with the refusal fallback.
    expect(streams.slice(4).map((c) => [c.params.model, c.params.fallbacks])).toEqual([["claude-sonnet-5-5", "default"], ["claude-sonnet-5-5", "default"]]);
    expect(client.calls.filter((c) => c.kind === "create").every((c) => c.params.model === "claude-haiku-5-5" && c.params.output_config.format.type === "json_schema")).toBe(true);
    expect(skipped!.map((s) => s.name)).toEqual(["MIMOSA", "Off topic"]);

    expect(planned.map((p) => [p.name, p.labels])).toEqual([["GenoNova fixture", ["entity-request", "tier-1"]], ["ProtSpec fixture", ["entity-request", "tier-2"]]]);
    expect(data.created.map((i) => i.labels)).toEqual([["entity-request", "tier-1"], ["entity-request", "tier-2"]]);
    expect(articles.created.map((i) => [i.labels, i.body.split("\n")[0]])).toEqual([
      [["article"], "Counterpart database issue: https://github.com/rewire-bio/rewire-benchmark-data/issues/900"],
      [["article"], "Counterpart database issue: https://github.com/rewire-bio/rewire-benchmark-data/issues/901"],
    ]);
    // Each data issue is then edited to link its article issue.
    expect(data.updated.map((u) => [u.number, u.body.split("\n")[0]])).toEqual([
      [900, "Counterpart article issue: https://github.com/rewire-bio/rewire.it/issues/900"],
      [901, "Counterpart article issue: https://github.com/rewire-bio/rewire.it/issues/901"],
    ]);
    expect(data.labels).toEqual(["rewire-bio/rewire-benchmark-data:entity-request", "rewire-bio/rewire-benchmark-data:tier-1", "rewire-bio/rewire-benchmark-data:tier-2", "rewire-bio/rewire-benchmark-data:tier-3"]);
    expect(usage!.byModel["claude-haiku-5-5"].webSearches).toBe(8);
    expect(usage!.byModel["claude-sonnet-5-5"].webSearches).toBe(4);
    expect(usage!.total()).toBeGreaterThan(0);
  });

  it("skips a refused candidate and files nothing in report-only mode", async () => {
    const client = anthropic({ refuse: "ProtSpec fixture" });
    const data = github("rewire-bio/rewire-benchmark-data", []);
    const { planned, skipped } = await main([...args, "--report-only"], env, { now, log: quiet, anthropic: client, github: data, fetch: blog });
    expect(planned.map((p) => p.name)).toEqual(["GenoNova fixture", "MIMOSA"]);
    expect(skipped!.find((s) => s.name === "ProtSpec fixture")?.reason).toBe("judge refused or did not finish");
    expect(data.created).toEqual([]);
    expect(data.labels).toEqual([]);
  });

  it("keeps going when one judge call fails", async () => {
    const data = github("rewire-bio/rewire-benchmark-data", []);
    const { planned, skipped } = await main([...args, "--report-only"], env, { now, log: quiet, anthropic: anthropic({ fail: "GenoNova fixture" }), github: data, fetch: blog });
    expect(planned.map((p) => p.name)).toEqual(["MIMOSA", "ProtSpec fixture"]);
    expect(skipped!.find((s) => s.name === "GenoNova fixture")?.reason).toBe("judge call failed (529 Overloaded); the next run picks it up");
  });

  it("puts the article request in the data issue when the article issue fails", async () => {
    const data = github("rewire-bio/rewire-benchmark-data", []);
    const articles = github("rewire-bio/rewire.it", []);
    articles.createIssue = async () => { throw Object.assign(new Error("Forbidden"), { status: 403 }); };
    const { summary } = await main([...args, "--max-pairs", "1"], { ...env, ARTICLE_TOKEN: "t" }, { now, log: quiet, anthropic: anthropic(), github: data, articleGithub: articles, fetch: blog });
    expect(data.updated).toHaveLength(1);
    expect(data.updated[0].body).toContain("## Article request");
    expect(data.updated[0].body.split("\n")[0]).toContain("not filed");
    expect(summary).toContain("Article issue for GenoNova fixture failed (403 Forbidden)");
  });

  it("writes the summary with token usage even when filing fails", async () => {
    const summaryFile = join(mkdtempSync(join(tmpdir(), "discovery-")), "summary.md");
    const data = github("rewire-bio/rewire-benchmark-data", []);
    data.createIssue = async () => { throw new Error("GitHub is down"); };
    await expect(main(args, { ...env, GITHUB_STEP_SUMMARY: summaryFile }, { now, log: quiet, anthropic: anthropic(), github: data, fetch: blog })).rejects.toThrow("GitHub is down");
    expect(readFileSync(summaryFile, "utf8")).toContain("| claude-sonnet-5-5 |");
  });
});

// Everything below came out of the scheduled runs of 18 to 20 November 2026, which passed and
// filed nothing: the scan asked only for the last three days, returned names from its own skip
// list, and triage dropped the rest for their release date.
const RECORDED = `${FIXTURES}/recorded`;
const realIssues = JSON.parse(readFileSync(`${RECORDED}/issues-2026-11.json`, "utf8"));
const recordedScan = JSON.parse(readFileSync(`${RECORDED}/scan-2026-11-20.json`, "utf8")).lanes;

describe("issues filed by hand or by the old automation, with no marker", () => {
  // Real titles of rewire-benchmark-data #229 to #336, all opened by timini, none with a
  // discovery-key marker. The first live run must not file any of these again.
  const named: Record<number, string[]> = {
    315: ["SEPIQ 2026", "SEPIQ", "AVIDa-hHER2"], 287: ["ChemRefine"], 283: ["CycPepNet"], 251: ["CASP-DREAM TAP Challenge", "CASP-DREAM TAP"],
    250: ["hEVO"], 249: ["MIMOSA"], 247: ["Ladon"], 246: ["PerturbPFN"], 245: ["Bacformer", "BacBench"], 244: ["EditJumps"],
    243: ["TorchCraft"], 241: ["BioEmu-2", "BioEmu2", "bioemu 2"], 240: ["RFD4-Proteína", "RFD4-Proteina", "RFD 4 Proteina"], 235: ["BenchBench-Cloning", "BenchBench Cloning"],
    234: ["HyCell"], 233: ["HyPLM-Flash"], 232: ["HyInv"], 231: ["POISK"], 229: ["Enchant v3", "Enchant"],
  };

  it("has no marker and one author in the recorded issues", () => {
    expect(realIssues.every((i: any) => i.user === "timini" && !i.body.includes("discovery-key"))).toBe(true);
  });
  it("matches every one of them by the name in its title", () => {
    for (const [number, names] of Object.entries(named)) {
      for (const name of names) {
        expect([name, findDuplicate({ name, aliases: [], sources: [] }, { issues: realIssues })?.ref]).toEqual([name, `rewire-bio/rewire-benchmark-data#${number}`]);
      }
    }
  });
  it("matches a name given only as an alias", () => {
    expect(findDuplicate({ name: "Biomolecular Emulator 2", aliases: ["BioEmu-2"], sources: [] }, { issues: realIssues })?.ref).toBe("rewire-bio/rewire-benchmark-data#241");
  });
  it("still lets through a resource none of them names", () => {
    for (const name of ["GenoNova fixture", "HyCell-XL", "Emu", "Pois", "BioEmu-3"]) expect([name, findDuplicate({ name, aliases: [], sources: [] }, { issues: realIssues })]).toEqual([name, null]);
  });
  it("ignores a two-character alias, which would match half the titles", () => {
    expect(findDuplicate({ name: "GenoNova fixture", aliases: ["v3", "V 3", "2"], sources: [] }, { issues: realIssues })).toBeNull();
  });
  it("compares names without accents and with letters split from digits, and leaves keys alone", () => {
    expect(matchForm("RFD4-Proteína")).toBe(matchForm("rfd 4 proteina"));
    expect(matchForm("ESM2")).toBe(matchForm("ESM-2"));
    expect(keyOf("HelixMark fixture")).toBe("helixmark-fixture");
  });
  it("shows the scan the resource requests only, newest first", () => {
    const titles = knownTitles(realIssues, "rewire-bio/rewire-benchmark-data");
    expect(titles.slice(0, 3)).toEqual([
      "Add SEPIQ 2026 challenge and AVIDa-hHER2 dataset",
      "Add ChemRefine: learned-potential and quantum-chemistry workflow pipeline",
      "Add CycPepNet cyclic-peptide property benchmark metadata (tier 3)",
    ]);
    expect(titles).toContain("Add BioEmu-2: October 2026 research preview");
    expect(titles.filter((t: string) => /^(Lane|Acceptance|Add areas|Add a tier|Require|Declare)/.test(t))).toEqual([]);
    expect(knownTitles(realIssues, "rewire-bio/rewire-benchmark-data", 5)).toHaveLength(5);
    expect(knownTitles(realIssues, "rewire-bio/rewire.it")).toEqual([]);
  });
});

describe("scan prompt", () => {
  const prompt = scanPrompt({ lane: SCAN_LANES[0], runDate: "2026-11-21", lookbackDays: 30, titles: ["Add BioEmu-2: October 2026 research preview"] });

  it("asks for what the database lacks, with a 30-day period to look at first", () => {
    expect(prompt).toContain("that the database does not hold yet");
    expect(prompt).toContain("in the last 30 days (since 2026-10-22)");
    expect(prompt).toContain("Never leave a candidate out for its age alone.");
    expect(prompt).not.toMatch(/last 3 days/);
  });
  it("tells the scan not to return the requests it is shown", () => {
    expect(prompt).toContain("Do not list a resource they name as a candidate");
    expect(prompt).toContain("- Add BioEmu-2: October 2026 research preview");
    expect(prompt).not.toMatch(/which you can skip/);
  });
  it("defaults to 30 days and reads release dates", async () => {
    expect(ageInDays("2026-11-14", "2026-11-21")).toBe(7);
    expect(ageInDays("2026-06", "2026-11-21")).toBe(173);
    expect(ageInDays("June 2026", "2026-11-21")).toBeNull();
    expect(ageInDays("", "2026-11-21")).toBeNull();
    await expect(main(["--dry-run", "--lookback-days", "0"], {}, { now, log: quiet })).rejects.toThrow("--lookback-days");
  });
});

describe("scan budget", () => {
  it("keeps the search fees of a full scan inside the budget", () => {
    const searches = SCAN_LANES.length * LIMITS.scanSearches;
    expect(searches).toBe(24);
    expect(searches * PRICES.webSearch).toBeLessThan(LIMITS.maxScanUsd);
    // The worst case allows one extra search for each resume of each lane.
    expect(SCAN_LANES.length * (LIMITS.scanSearches + LIMITS.maxContinuations) * PRICES.webSearch).toBeLessThanOrEqual(LIMITS.maxScanUsd);
  });
});

describe("tier label", () => {
  it("files tier 3 issues with the label intake reads to close them", () => {
    const intake = readFileSync("scripts/agents/intake.mjs", "utf8");
    const read = /const closes = \(issue\.labels \?\? \[\]\)\.includes\('([a-z0-9-]+)'\)/.exec(intake)?.[1];
    expect(read).toBe("tier-3");
    expect(dataLabels(3)).toContain(read);
    expect(dataLabels(1)).toEqual(["entity-request", "tier-1"]);
    for (const tier of [1, 2, 3] as const) for (const label of dataLabels(tier)) expect(LABELS[label]).toBeDefined();
  });
});

describe("recorded scan of 20 November 2026", () => {
  const judgements = JSON.parse(readFileSync(`${FIXTURES}/judgements.json`, "utf8"));
  const runDay = new Date("2026-11-21T08:00:00Z");
  const env = { ANTHROPIC_API_KEY: "test", GITHUB_REPOSITORY: "rewire-bio/rewire-benchmark-data" };
  const args = ["--store-dir", `${FIXTURES}/entities`];
  const blog = async () => ({ ok: true, status: 200, text: async () => "" });
  const laneOf = (text: string) => Object.keys(recordedScan).find((l) => text.includes(`lane ${l}.`) || text.includes(`Lane: ${l}.`))!;

  // Replays the recorded lane notes and candidate lists. `searches` is what each scan request reports.
  function replay({ searches = 8, pauseForever = "" } = {}) {
    const calls: { kind: string; params: any }[] = [];
    const reply = (text: string, stop: string, usage: any) => ({ content: [{ type: "text", text }], stop_reason: stop, usage, stop_details: null });
    return {
      calls,
      beta: { messages: { stream(params: any) {
        calls.push({ kind: "stream", params });
        const prompt = String(params.messages[0].content);
        const lane = prompt.includes("Find AI-for-biology") ? laneOf(prompt) : "";
        const usage = { input_tokens: 2000, output_tokens: 500, server_tool_use: { web_search_requests: lane ? searches : 1, web_fetch_requests: 0 } };
        const message = !lane ? reply(`notes for ${/Name: (.*)/.exec(prompt)?.[1]}\nFILE`, "end_turn", usage)
          : lane === pauseForever ? reply(recordedScan[lane].notes, "pause_turn", usage)
          : reply(recordedScan[lane].notes, "end_turn", usage);
        return { finalMessage: async () => ({ ...message, model: params.model }) };
      } } },
      messages: { async create(params: any) {
        calls.push({ kind: "create", params });
        const notes = String(params.messages[0].content);
        const lane = notes.includes("Recorded scan notes") ? laneOf(notes) : "";
        const body = lane ? { candidates: recordedScan[lane].candidates } : judgements.find((j: any) => j.name === /notes for (.*)/.exec(notes)?.[1]);
        return reply(JSON.stringify(body), "end_turn", { input_tokens: 500, output_tokens: 50 });
      } },
    };
  }

  function github(issues: any[]) {
    const created: any[] = [];
    let next = 900;
    return {
      created,
      async listIssues() { return issues; },
      async ensureLabels() {},
      async createIssue(r: string, issue: any) { const number = next++; created.push({ repo: r, number, ...issue }); return { number, html_url: `https://github.com/${r}/issues/${number}` }; },
      async updateIssue() {},
    };
  }

  const LANE_LINES = [
    "scan genomics: 8 searches, 4 raw candidates, 2 dropped as known, 0 dropped as remembered, 0 dropped for another reason, 2 to judge",
    "scan proteins: 8 searches, 4 raw candidates, 2 dropped as known, 0 dropped as remembered, 1 dropped for another reason, 1 to judge",
    "scan cells and other biology: 8 searches, 3 raw candidates, 1 dropped as known, 0 dropped as remembered, 1 dropped for another reason, 1 to judge",
  ];
  const judgedNames = (client: ReturnType<typeof replay>) => client.calls.filter((c) => c.kind === "stream")
    .map((c) => /Name: (.*)/.exec(String(c.params.messages[0].content))?.[1]).filter(Boolean);

  it("judges none of the names the scan echoed from its skip list, and files what the database lacks", async () => {
    const client = replay();
    const data = github(realIssues);
    const { planned, skipped, summary, usage } = await main(args, env, { now: runDay, log: quiet, anthropic: client, github: data, fetch: blog });

    const echoed = ["Ladon", "Bacformer", "BioEmu2", "RFD4-Proteina", "BenchBench-Cloning"];
    for (const name of echoed) expect([name, skipped!.find((s) => s.name === name)?.reason.startsWith("already known, not judged: ")]).toEqual([name, true]);
    expect(skipped!.find((s) => s.name === "RFD4-Proteina")?.reason).toContain("rewire-bio/rewire-benchmark-data#240");
    expect(skipped!.find((s) => s.name === "BioEmu2")?.reason).toContain("rewire-bio/rewire-benchmark-data#241");
    // Ladon came back marked as a duplicate by triage; the script's own check names the issue.
    expect(skipped!.find((s) => s.name === "Ladon")?.reason).toContain("rewire-bio/rewire-benchmark-data#247");
    expect(judgedNames(client).filter((n) => echoed.includes(n!))).toEqual([]);
    expect(summary).toContain("The scan returned 5 candidates that an issue or the record store already holds. None was judged.");

    // One from each lane in turn; inside a lane the recent release goes before the old one.
    expect(judgedNames(client)).toEqual(["GenoNova fixture", "ProtSpec fixture", "CellAtlasLM fixture", "SpliceAtlas fixture"]);
    expect(skipped!.find((s) => s.name === "GenoNova")?.reason).toBe("repeats GenoNova fixture from another scan lane");
    expect(skipped!.find((s) => s.name === "Off topic")?.reason).toBe("triage: workflow wrapper with no model");
    // SpliceAtlas was released five months before the run. The old three-day window dropped it.
    expect(planned.map((p) => [p.name, p.labels])).toEqual([
      ["GenoNova fixture", ["entity-request", "tier-1"]],
      ["ProtSpec fixture", ["entity-request", "tier-2"]],
      ["CellAtlasLM fixture", ["entity-request", "tier-3"]],
      ["SpliceAtlas fixture", ["entity-request", "tier-1"]],
    ]);
    expect(data.created.map((i) => i.labels.join())).toEqual(["entity-request,tier-1", "entity-request,tier-2", "entity-request,tier-3", "entity-request,tier-1"]);
    expect(data.created.every((i) => i.body.includes("<!-- discovery-key: "))).toBe(true);

    // The scan prompt carried the request titles and not the other issues.
    const scan = client.calls.find((c) => c.kind === "stream")!.params.messages[0].content as string;
    expect(scan).toContain("- Add RFD4-Proteína: 2026-10-19 matched flow/autoencoder release");
    expect(scan).not.toContain("Lane 5: rebuild the evidence store");
    expect(scan).toContain("Lane: genomics.");
    // 24 searches by Haiku: the scan's share of the run stays inside its budget.
    expect(usage!.byModel["claude-haiku-5-5"].webSearches).toBe(24);
    expect(usage!.costOf("claude-haiku-5-5")).toBeLessThan(LIMITS.maxScanUsd);
  });

  it("does not file the same resources again on the next run", async () => {
    const first = github(realIssues);
    await main(args, env, { now: runDay, log: quiet, anthropic: replay(), github: first, fetch: blog });
    const filed = first.created.map((i) => ({ ...i, html_url: `https://github.com/${i.repo}/issues/${i.number}`, created_at: "2026-11-21T17:00:00Z" }));
    const client = replay();
    const second = github([...realIssues, ...filed]);
    const { planned, summary } = await main(args, env, { now: new Date("2026-11-22T08:00:00Z"), log: quiet, anthropic: client, github: second, fetch: blog });
    expect(planned).toEqual([]);
    expect(second.created).toEqual([]);
    expect(judgedNames(client)).toEqual([]);
    expect(summary).toContain("The scan returned 10 candidates that an issue or the record store already holds.");
  });

  it("counts issues already filed today against the cap", async () => {
    const today = [1, 2, 3].map((n) => ({ repo: env.GITHUB_REPOSITORY, number: 400 + n, title: `Add discovered model Earlier ${n}: x`, body: `<!-- discovery-key: earlier-${n} -->`, labels: ["entity-request", "tier-1"], created_at: "2026-11-21T09:00:00Z" }));
    const yesterday = { repo: env.GITHUB_REPOSITORY, number: 399, title: "Add discovered model Older: x", body: "<!-- discovery-key: older -->", labels: ["entity-request"], created_at: "2026-11-20T09:00:00Z" };
    const data = github([...realIssues, yesterday, ...today]);
    const { planned, skipped, summary } = await main(args, env, { now: runDay, log: quiet, anthropic: replay(), github: data, fetch: blog });
    expect(planned.map((p) => p.name)).toEqual(["GenoNova fixture"]);
    expect(data.created).toHaveLength(1);
    expect(skipped!.filter((s) => s.reason === "over the daily cap of 4 (3 already filed today); the next run picks it up").map((s) => s.name)).toEqual(["ProtSpec fixture", "CellAtlasLM fixture", "SpliceAtlas fixture"]);
    expect(summary).toContain("3 issues were already filed today; the cap of 4 counts them.");
  });

  it("does not start a lane that would take the scan past its budget", async () => {
    // 21 searches a lane is $0.21: after two lanes a third would pass $0.55.
    const client = replay({ searches: 21 });
    const { summary, usage } = await main([...args, "--report-only"], env, { now: runDay, log: quiet, anthropic: client, github: github(realIssues), fetch: blog });
    expect(summary).toContain('Scan lane "cells and other biology" was not run: the scan would have passed $0.55.');
    expect(client.calls.filter((c) => c.kind === "stream" && String(c.params.messages[0].content).includes("Find AI-for-biology"))).toHaveLength(2);
    expect(usage!.byModel["claude-haiku-5-5"].webSearches).toBe(42);
  });

  it("uses the notes written so far when a lane stops at the resume cap, and gives each resume what is left", async () => {
    const client = replay({ searches: 3, pauseForever: "genomics" });
    const { planned, skipped } = await main([...args, "--report-only"], env, { now: runDay, log: quiet, anthropic: client, github: github(realIssues), fetch: blog });
    const genomics = client.calls.filter((c) => c.kind === "stream" && String(c.params.messages[0].content).includes("Lane: genomics."));
    expect(genomics.map((c) => c.params.tools[0].max_uses)).toEqual([8, 5, 2]);
    expect(planned.map((p) => p.name)).toContain("GenoNova fixture");
    expect(skipped!.find((s) => s.name === "Bacformer")?.reason).toContain("already known, not judged");
    const lines: string[] = [];
    await main([...args, "--report-only"], env, { now: runDay, log: (m: string) => lines.push(m), anthropic: replay({ searches: 3, pauseForever: "genomics" }), github: github(realIssues), fetch: blog });
    expect(lines).toContain("scan genomics: stopped after the pause_turn cap");
    expect(lines.find((l) => l.startsWith("scan genomics: 9 searches"))).toMatch(/2 to judge \(finished; the scan stopped at the pause_turn cap and the notes may be incomplete\)$/);
  });

  it("prints one line per lane and keeps the lane's working for the run artifact", async () => {
    const out = mkdtempSync(join(tmpdir(), "discovery-"));
    const lines: string[] = [];
    const { lanes } = await main([...args, "--report-only", "--out", out], env, { now: runDay, log: (m: string) => lines.push(m), anthropic: replay(), github: github(realIssues), fetch: blog });
    expect(lines.filter((l) => l.startsWith("scan "))).toEqual(LANE_LINES);
    expect(lanes!.map((l: any) => l.status)).toEqual(["finished", "finished", "finished"]);
    const genomics = JSON.parse(readFileSync(join(out, "scan", "genomics.json"), "utf8"));
    expect(genomics.mode).toBe("report only");
    expect(genomics.notes).toBe(recordedScan.genomics.notes);
    expect(genomics.raw_candidates).toEqual(recordedScan.genomics.candidates);
    expect(genomics.requests).toEqual([{ stop_reason: "end_turn", input_tokens: 2000, output_tokens: 500, web_search_requests: 8, web_fetch_requests: 0, tool_use_reported: true, text_characters: recordedScan.genomics.notes.length }]);
    expect(genomics.dropped.map((d: any) => [d.name, d.category])).toEqual([["Ladon", "known"], ["Bacformer", "known"]]);
    expect(genomics.to_judge).toEqual(["GenoNova fixture", "SpliceAtlas fixture"]);
  });

  it("gives a lane that never ran a line and a row with the reason", async () => {
    const lines: string[] = [];
    const { lanes, summary } = await main([...args, "--report-only"], env, { now: runDay, log: (m: string) => lines.push(m), anthropic: replay({ searches: 13 }), github: github(realIssues), fetch: blog });
    expect(lines).toContain("scan cells and other biology: 0 searches, no candidate list (not run: scan budget)");
    expect(lanes!.map((l: any) => [l.lane, l.status])).toContainEqual(["cells and other biology", "not run: scan budget"]);
    expect(summary).toContain("| cells and other biology | not run: scan budget | 0 | 0 | 0 | 0 | 0 | 0 | 0 |");
  });

  it("rotates the first lane by day", async () => {
    const client = replay();
    await main([...args, "--report-only"], env, { now: new Date("2026-11-22T08:00:00Z"), log: quiet, anthropic: client, github: github(realIssues), fetch: blog });
    expect(String(client.calls[0].params.messages[0].content)).toContain("Lane: proteins.");
  });
});

// Guards the review of #339 found untested or open. Each test here fails when its guard is removed.
describe("guards on the live path", () => {
  const judgements = JSON.parse(readFileSync(`${FIXTURES}/judgements.json`, "utf8"));
  const runDay = new Date("2026-11-21T08:00:00Z");
  const env = { ANTHROPIC_API_KEY: "test", GITHUB_REPOSITORY: "rewire-bio/rewire-benchmark-data" };
  const args = ["--store-dir", `${FIXTURES}/entities`];
  const blog = async () => ({ ok: true, status: 200, text: async () => "" });
  const tools = { web_search_requests: 1, web_fetch_requests: 1 };
  const scanCandidate = (name: string, extra: Record<string, unknown> = {}) => ({ name, aliases: [], kind: "model", released: "2026-11-10", summary: "s", urls: [], in_scope: true, reason: "", ...extra });
  const judgementFor = (name: string, n: number) => ({ ...judgements[0], name, aliases: [], sources: [{ url: `https://doi.org/10.1101/2026.11.01.80000${n}`, title: "Preprint", role: "preprint", retrieved_at: "2026-11-21" }] });

  // A stand-in Anthropic client. `candidates` come back from the genomics lane; the other lanes
  // find nothing. `judge` gives the judge's reply for a name, `scan` the scan's reply for a
  // lane and request number, and `structured` can replace a structuring reply.
  function standIn({ candidates = [] as any[], judge = (name: string): any => ({}), scan = (lane: string, request: number): any => ({}), structured = (notes: string): any => undefined, decision = "file" } = {}) {
    const calls: { kind: string; params: any }[] = [];
    const requests: Record<string, number> = {};
    const message = (text: string, over: any = {}) => ({ content: [{ type: "text", text }], stop_reason: "end_turn", usage: { input_tokens: 1000, output_tokens: 100, server_tool_use: tools }, stop_details: null, ...over });
    return {
      calls,
      judgedNames: () => [...new Set(calls.filter((c) => c.kind === "stream").map((c) => /^Name: (.*)$/m.exec(String(c.params.messages[0].content))?.[1]).filter(Boolean))],
      judgePrompt: (name: string) => String(calls.find((c) => c.kind === "stream" && String(c.params.messages[0].content).includes(`Name: ${name}\n`))?.params.messages[0].content),
      beta: { messages: { stream(params: any) {
        calls.push({ kind: "stream", params });
        const prompt = String(params.messages[0].content);
        const lane = /Lane: ([^.]*)\./.exec(prompt)?.[1];
        const name = /^Name: (.*)$/m.exec(prompt)?.[1];
        const key = lane ?? name!;
        requests[key] = (requests[key] ?? 0) + 1;
        const reply = lane ? message(`scan notes ${lane}`, scan(lane, requests[key])) : message(`notes for ${name}\nFILE`, judge(name!));
        return { finalMessage: async () => ({ ...reply, model: params.model }) };
      } } },
      messages: { async create(params: any) {
        calls.push({ kind: "create", params });
        const notes = String(params.messages[0].content);
        const plain = { usage: { input_tokens: 500, output_tokens: 50 } };
        const override = structured(notes);
        if (override) return message("", { ...plain, ...override });
        if (notes.includes("scan notes")) return message(JSON.stringify({ candidates: notes.includes("scan notes genomics") ? candidates : [] }), plain);
        const name = /notes for (.*)/.exec(notes)?.[1] ?? "";
        return message(JSON.stringify({ ...judgementFor(name, candidates.findIndex((c) => c.name === name) + 1), decision, skip_reason: decision === "skip" ? "an incremental checkpoint" : "" }), plain);
      } },
    };
  }

  function github(issues: any[] = []) {
    const created: any[] = [];
    let next = 900;
    return {
      created,
      async listIssues() { return [...issues]; },
      async ensureLabels() {},
      async createIssue(r: string, issue: any) { const number = next++; created.push({ repo: r, number, ...issue }); return { number, html_url: `https://github.com/${r}/issues/${number}` }; },
      async updateIssue() {},
    };
  }
  const run = (client: any, data: any, extra: string[] = [], over: Record<string, any> = {}) =>
    main([...args, ...extra], { ...env, ...over.env }, { now: over.now ?? runDay, log: quiet, anthropic: client, github: data, fetch: blog, ...over.deps });
  const eight = ["Alder", "Birch", "Cedar", "Dogwood", "Elder", "Fir", "Ginkgo", "Hazel"].map((n) => scanCandidate(`${n}Fold`));

  describe("record store", () => {
    it("stops before any model call or issue when no store name can be read", async () => {
      const client = standIn({ candidates: [scanCandidate("Bacformer")] });
      const data = github();
      const summaryFile = join(mkdtempSync(join(tmpdir(), "discovery-")), "summary.md");
      await expect(main(["--store-dir", "no/such/dir"], { ...env, GITHUB_STEP_SUMMARY: summaryFile }, { now: runDay, log: quiet, anthropic: client, github: data, fetch: blog }))
        .rejects.toThrow("No record-store names were read");
      expect(client.calls).toEqual([]);
      expect(data.created).toEqual([]);
      expect(readFileSync(summaryFile, "utf8")).toContain("Nothing was scanned or filed");
    });
    it("drops a stored name before the judge in a live run", async () => {
      const client = standIn({ candidates: [scanCandidate("Bacformer"), scanCandidate("ESM2"), scanCandidate("AlderFold")] });
      const data = github();
      const { skipped } = await run(client, data);
      expect(client.judgedNames()).toEqual(["AlderFold"]);
      expect(data.created.map((i) => i.title)).toEqual(["Add discovered model AlderFold: Predicts variant effects on gene expression from DNA sequence."]);
      expect(skipped!.find((s) => s.name === "Bacformer")?.reason).toContain("matches store record bacformer-20261115-model-bacformer");
      expect(data.created[0].body).toContain("4 record-store names");
    });
    it("is checked out by the workflow", () => {
      const workflow = readFileSync(".github/workflows/discovery.yml", "utf8");
      expect(/sparse-checkout: \|\n((?: {12}\S+\n)+)/.exec(workflow)?.[1].split("\n").map((l) => l.trim())).toContain("data/entities");
    });
  });

  describe("filing and judging limits", () => {
    it("judges at most six candidates a run and files at most four", async () => {
      const client = standIn({ candidates: eight });
      const data = github();
      const { skipped } = await run(client, data);
      expect(LIMITS.maxJudged).toBe(6);
      expect(client.judgedNames()).toEqual(eight.slice(0, 6).map((c) => c.name));
      expect(skipped!.filter((s) => s.reason === "over the judge cap of 6; the next run picks it up").map((s) => s.name)).toEqual(["GinkgoFold", "HazelFold"]);
      expect(LIMITS.maxPairs).toBe(4);
      expect(data.created).toHaveLength(4);
    });
    it("judges no further candidate once the run has cost more than $1", async () => {
      // Each judge call reports 60 searches: $0.60. The third candidate starts after $1.20.
      const client = standIn({ candidates: eight, judge: () => ({ usage: { input_tokens: 1000, output_tokens: 100, server_tool_use: { web_search_requests: 60, web_fetch_requests: 0 } } }) });
      const { skipped, usage } = await run(client, github(), ["--report-only"]);
      expect(LIMITS.maxRunUsd).toBe(1);
      expect(client.judgedNames()).toEqual(["AlderFold", "BirchFold"]);
      expect(skipped!.filter((s) => s.reason === "run cost passed $1; not judged, the next run picks it up")).toHaveLength(4);
      expect(usage!.total()).toBeLessThan(LIMITS.maxRunUsd + 0.6 + 0.1);
    });
    it("refuses a --max-pairs that is not a whole number", async () => {
      for (const bad of ["abc", "-1", "2.5", ""]) await expect(run(standIn(), github(), ["--max-pairs", bad])).rejects.toThrow("--max-pairs needs a whole number");
      const data = github();
      await run(standIn({ candidates: eight }), data, ["--max-pairs", "0"]);
      expect(data.created).toEqual([]);
    });
    it("files four by default in the workflow", () => {
      const workflow = readFileSync(".github/workflows/discovery.yml", "utf8");
      expect(workflow).toContain("MAX_PAIRS: ${{ inputs.max_pairs || '4' }}");
      expect(workflow).toMatch(/max_pairs:\n\s+description: [^\n]+\n\s+default: "4"\n/);
      expect(workflow).toContain('--max-pairs "$MAX_PAIRS"');
    });
    it("gives the judge its own search and fetch allowance, page size and reply size", async () => {
      const client = standIn({ candidates: [scanCandidate("AlderFold")] });
      await run(client, github(), ["--report-only"]);
      const judge = client.calls.find((c) => c.kind === "stream" && String(c.params.messages[0].content).includes("Name: AlderFold"))!.params;
      expect(judge.tools.map((t: any) => [t.name, t.max_uses, t.max_content_tokens])).toEqual([["web_search", 3, undefined], ["web_fetch", 4, 15000]]);
      expect(judge.max_tokens).toBe(10000);
      const scan = client.calls.find((c) => c.kind === "stream")!.params;
      expect(scan.tools.map((t: any) => t.max_uses)).toEqual([8, 2]);
    });
  });

  describe("direct tool calls", () => {
    it("restricts search and fetch to direct calls on every scan and judge request, resumes included", async () => {
      const client = standIn({
        candidates: [scanCandidate("AlderFold"), scanCandidate("BirchFold")],
        scan: (lane, request) => request === 1 ? { stop_reason: "pause_turn" } : {},
        judge: (name) => name === "AlderFold" ? { stop_reason: "pause_turn" } : {},
      });
      await run(client, github(), ["--report-only"]);
      const requests = client.calls.filter((c) => c.kind === "stream").map((c) => c.params);
      const of = (match: string) => requests.filter((r) => String(r.messages[0].content).includes(match));
      // Each lane is resumed once, AlderFold up to the cap, BirchFold not at all.
      expect(of("Lane: ")).toHaveLength(6);
      expect(of("Name: AlderFold")).toHaveLength(1 + LIMITS.maxContinuations);
      expect(of("Name: BirchFold")).toHaveLength(1);
      expect(requests).toHaveLength(10);
      expect(DIRECT_ONLY).toEqual(["direct"]);
      for (const request of requests) {
        expect(request.tools.map((t: any) => [t.type, t.name, t.allowed_callers])).toEqual([
          ["web_search_20260318", "web_search", ["direct"]],
          ["web_fetch_20260209", "web_fetch", ["direct"]],
        ]);
        // No code execution tool is declared, so nothing in the request offers a code path.
        expect(JSON.stringify(request.tools)).not.toContain("code_execution");
      }
    });
    it("tells the scan to search directly, one query at a time, and to keep a candidate whose fetch failed", () => {
      const prompt = scanPrompt({ lane: SCAN_LANES[0], runDate: "2026-11-22", lookbackDays: 30, titles: [] });
      expect(prompt).toContain("Call the search tool yourself, one query at a time, and read each result before you write the next query.");
      expect(prompt).toContain("Do not write code to search or fetch.");
      expect(prompt).toContain("Never run a query twice.");
      expect(prompt).toContain("Keep two searches for following up your best leads.");
      expect(prompt).toContain("Fetch a URL exactly as a search result gave it.");
      expect(prompt).toContain("A fetch that fails is not a reason to drop a candidate");
      const system = readFileSync("agents/discovery.md", "utf8");
      expect(system).toContain("Call the search and fetch tools yourself");
    });
    it("keeps the advice on failed fetches out of the system prompt, which the judge also reads", () => {
      // To the judge "keep the candidate" would mean FILE. Only the scan prompt says it.
      const system = readFileSync("agents/discovery.md", "utf8");
      expect(system).not.toContain("not a reason to drop a candidate");
      expect(system).not.toMatch(/keep it and say/i);
      expect(system).toContain("- A page that fails to load (403, paywall, timeout) is an access gap, not evidence that something is absent. Say which page failed and on which date.\n");
    });

    describe("when the API rejects allowed_callers", () => {
      const invalid = (message: string, status = 400) => Object.assign(new Error(message), { status });
      const fieldOf = (tool: any) => "allowed_callers" in tool;
      const ofLane = (client: any, lane: string) => client.calls.filter((c: any) => c.kind === "stream" && String(c.params.messages[0].content).includes(`Lane: ${lane}.`)).map((c: any) => c.params.tools.map(fieldOf));

      it("reads which tools a 400 names, and nothing from any other error", () => {
        expect(rejectedDirectOnly(invalid('400 {"type":"error","error":{"type":"invalid_request_error","message":"tools.1.web_fetch_20260209.allowed_callers: Extra inputs are not permitted"}}'))).toEqual(["web_fetch"]);
        expect(rejectedDirectOnly(invalid("tools.0.allowed_callers: unexpected value"))).toEqual(["web_search"]);
        expect(rejectedDirectOnly(invalid("allowed_callers is not supported"))).toEqual(["web_search", "web_fetch"]);
        expect(rejectedDirectOnly(invalid("max_uses: must be positive for web_fetch"))).toEqual([]);
        expect(rejectedDirectOnly(invalid("allowed_callers: overloaded", 529))).toEqual([]);
        expect(rejectedDirectOnly(new Error("allowed_callers"))).toEqual([]);
        expect(rejectedDirectOnly(undefined)).toEqual([]);
      });
      it("sends the request once more without the field on the tool the 400 names, and keeps it off for the resumes", async () => {
        const out = mkdtempSync(join(tmpdir(), "discovery-"));
        const lines: string[] = [];
        const client: any = standIn({
          candidates: [scanCandidate("AlderFold")],
          scan: (lane, request) => {
            if (fieldOf(client.calls.at(-1).params.tools[1])) throw invalid('400 {"type":"error","error":{"type":"invalid_request_error","message":"tools.1.web_fetch_20260209.allowed_callers: Extra inputs are not permitted"}}');
            return lane === "genomics" && request === 2 ? { stop_reason: "pause_turn" } : {};
          },
        });
        const { lanes } = await run(client, github(), ["--report-only", "--out", out], { deps: { log: (m: string) => lines.push(m) } });
        // Rejected, sent again without the field on fetch, then one resume that never sends it.
        expect(ofLane(client, "genomics")).toEqual([[true, true], [true, false], [true, false]]);
        // Each call starts with the field: a later lane asks again.
        expect(ofLane(client, "proteins")).toEqual([[true, true], [true, false]]);
        expect(lanes!.map((l: any) => l.status)).toEqual(["finished", "finished", "finished"]);
        expect(lines.filter((l) => l.includes("rejected allowed_callers"))).toHaveLength(3);
        expect(lines).toContain('scan genomics: the API rejected allowed_callers on web_fetch (400 400 {"type":"error","error":{"type":"invalid_request_error","message":"tools.1.web_fetch_20260209.allowed_callers: Extra inputs are not permitted"}}); sent again without it, so those calls can run from code');
        const genomics = JSON.parse(readFileSync(join(out, "scan", "genomics.json"), "utf8"));
        expect(genomics.requests.map((r: any) => r.allowed_callers_dropped)).toEqual([["web_fetch"], ["web_fetch"]]);
        // The judge still sends the field on both tools, and its row would say if it had not.
        const judge = client.calls.find((c: any) => c.kind === "stream" && String(c.params.messages[0].content).includes("Name: AlderFold"))!.params;
        expect(judge.tools.map(fieldOf)).toEqual([true, true]);
      });
      it("drops the field from both tools when the 400 names neither", async () => {
        const client: any = standIn({ scan: () => { if (client.calls.at(-1).params.tools.some(fieldOf)) throw invalid("allowed_callers: Extra inputs are not permitted"); return {}; } });
        const { lanes } = await run(client, github(), ["--report-only"]);
        expect(ofLane(client, "genomics")).toEqual([[true, true], [false, false]]);
        expect(lanes!.map((l: any) => l.status)).toEqual(["finished", "finished", "finished"]);
      });
      it("leaves the row as it was when nothing is rejected", async () => {
        const out = mkdtempSync(join(tmpdir(), "discovery-"));
        await run(standIn(), github(), ["--report-only", "--out", out]);
        expect(JSON.parse(readFileSync(join(out, "scan", "genomics.json"), "utf8")).requests.every((r: any) => !("allowed_callers_dropped" in r))).toBe(true);
      });
      it("does not send again after a 400 about something else, or after a second 400", async () => {
        const other: any = standIn({ scan: () => { throw invalid("max_uses: Input should be greater than 0"); } });
        const first = await run(other, github(), ["--report-only"]);
        expect(ofLane(other, "genomics")).toEqual([[true, true]]);
        expect(first.lanes!.map((l: any) => l.status)).toEqual(Array(3).fill("failed: 400 max_uses: Input should be greater than 0"));
        expect(first.summary).toContain("No scan lane finished; nothing was judged.");
        const twice: any = standIn({ scan: () => { throw invalid("tools.0.allowed_callers: Extra inputs are not permitted"); } });
        const second = await run(twice, github(), ["--report-only"]);
        expect(ofLane(twice, "genomics")).toEqual([[true, true], [false, true]]);
        expect(second.lanes!.map((l: any) => l.status)).toEqual(Array(3).fill("failed: 400 tools.0.allowed_callers: Extra inputs are not permitted"));
        // A resume that is rejected for a tool the field is already off: no further request.
        const later: any = standIn({ scan: (lane, request) => { if (request !== 2) throw invalid("tools.0.allowed_callers: Extra inputs are not permitted"); return { stop_reason: "pause_turn" }; } });
        await run(later, github(), ["--report-only"]);
        expect(ofLane(later, "genomics")).toEqual([[true, true], [false, true], [false, true]]);
      });
    });
  });

  describe("judge replies that are not a verdict", () => {
    it("does not file a candidate whose judge call stopped at the resume cap", async () => {
      const client = standIn({ candidates: [scanCandidate("AlderFold"), scanCandidate("BirchFold")], judge: (name) => name === "AlderFold" ? { stop_reason: "pause_turn" } : {} });
      const data = github();
      const { skipped } = await run(client, data);
      expect(client.calls.filter((c) => c.kind === "stream" && String(c.params.messages[0].content).includes("Name: AlderFold"))).toHaveLength(1 + LIMITS.maxContinuations);
      expect(skipped!.find((s) => s.name === "AlderFold")?.reason).toBe("judge refused or did not finish");
      expect(data.created.map((i) => i.title.split(":")[0])).toEqual(["Add discovered model BirchFold"]);
    });
    it("does not file a candidate whose judge reply was cut off at max_tokens", async () => {
      const client = standIn({ candidates: [scanCandidate("AlderFold"), scanCandidate("BirchFold")], judge: (name) => name === "AlderFold" ? { stop_reason: "max_tokens", content: [{ type: "text", text: "notes for AlderFold, which stop in the middle of" }] } : {} });
      const data = github();
      const { skipped } = await run(client, data);
      expect(skipped!.find((s) => s.name === "AlderFold")?.reason).toBe("judge refused or did not finish");
      expect(data.created.map((i) => i.title.split(":")[0])).toEqual(["Add discovered model BirchFold"]);
    });
    it("does not file notes that end with SKIP, whatever the structuring call returns", async () => {
      const client = standIn({ candidates: [scanCandidate("AlderFold")], judge: () => ({ content: [{ type: "text", text: "notes for AlderFold\nIt could be FILE, but it is a checkpoint.\nSKIP: an incremental checkpoint." }] }) });
      const data = github();
      const { skipped } = await run(client, data);
      expect(data.created).toEqual([]);
      expect(skipped!.find((s) => s.name === "AlderFold")?.reason).toBe("judge: the judge notes conclude SKIP");
      expect(verdictOf("Verdict: FILE. The paper says skip connections help.")).toBe("FILE");
      expect(verdictOf("SKIP was my first reading.\nAfter the preprint: FILE (not SKIP, the weights are new).")).toBe("FILE");
      expect(verdictOf("FILE looked right.\nSKIP: it is the same checkpoint. The FILE case fails.\nSources are listed above.")).toBe("SKIP");
      expect(verdictOf("I would file this.")).toBeNull();
    });
    it("does not use a structuring reply that did not finish", async () => {
      const cut = { stop_reason: "max_tokens", content: [{ type: "text", text: JSON.stringify({ candidates: [scanCandidate("AlderFold")] }) }] };
      const client = standIn({ structured: (notes) => notes.includes("scan notes genomics") ? cut : undefined });
      const { summary } = await run(client, github(), ["--report-only"]);
      expect(summary).toContain('Scan lane "genomics": triage returned no usable candidate list.');
      expect(client.judgedNames()).toEqual([]);
    });
  });

  describe("searches a response does not report", () => {
    it("counts a response without server_tool_use as the full allowance, for resumes and for cost", async () => {
      const silent = { input_tokens: 1000, output_tokens: 100 };
      const client = standIn({
        candidates: [scanCandidate("AlderFold")],
        scan: () => ({ stop_reason: "pause_turn", usage: silent }),
        judge: () => ({ stop_reason: "pause_turn", usage: silent }),
      });
      const { usage } = await run(client, github(), ["--report-only"]);
      const uses = (match: string) => client.calls.filter((c) => c.kind === "stream" && String(c.params.messages[0].content).includes(match)).map((c) => c.params.tools.map((t: any) => t.max_uses));
      // The first request is taken to have used all 8 searches and both fetches; a resume keeps the minimum of one.
      expect(uses("Lane: genomics.")).toEqual([[8, 2], [1, 1], [1, 1]]);
      expect(uses("Name: AlderFold")).toEqual([[3, 4], [1, 1], [1, 1]]);
      // Three lanes of 8 + 1 + 1 searches, and one judge call of 3 + 1 + 1.
      expect(usage!.byModel["claude-haiku-5-5"].webSearches).toBe(30);
      expect(usage!.byModel["claude-sonnet-5-5"].webSearches).toBe(5);
    });
    it("does not take direct calls off a resume's allowance, because the API counts them itself", async () => {
      const search = (n: number, caller?: any) => ({ type: "server_tool_use", id: `srvtoolu_${n}`, name: "web_search", input: { query: `q${n}` }, ...(caller ? { caller } : {}) });
      const fetched = { type: "server_tool_use", id: "srvtoolu_f", name: "web_fetch", input: { url: "https://example.org/a" } };
      const paused = (content: any[], searches: number, fetches: number) => ({ stop_reason: "pause_turn", content: [...content, { type: "text", text: "scan notes so far" }], usage: { input_tokens: 1, output_tokens: 1, server_tool_use: { web_search_requests: searches, web_fetch_requests: fetches } } });
      const uses = (client: any) => client.calls.filter((c: any) => c.kind === "stream" && String(c.params.messages[0].content).includes("Lane: genomics.")).map((c: any) => c.params.tools.map((t: any) => t.max_uses));
      // Three direct searches and one direct fetch in each paused reply: the allowance stays whole.
      const direct = standIn({ scan: (lane, request) => lane === "genomics" && request < 3 ? paused([search(1), search(2), search(3), fetched], 3, 1) : {} });
      await run(direct, github(), ["--report-only"]);
      expect(uses(direct)).toEqual([[8, 2], [8, 2], [8, 2]]);
      // One of the three searches came from code: only that one is taken off.
      const mixed = standIn({ scan: (lane, request) => lane === "genomics" && request === 1 ? paused([search(1), search(2), search(3, { type: "code_execution_20260120", tool_id: "srvtoolu_c" })], 3, 0) : {} });
      await run(mixed, github(), ["--report-only"]);
      expect(uses(mixed)).toEqual([[8, 2], [7, 2]]);
      // A refused direct call is in the reply and not in the reported use: nothing goes below zero.
      const refused = standIn({ scan: (lane, request) => lane === "genomics" && request === 1 ? paused([search(1), search(2)], 1, 0) : {} });
      await run(refused, github(), ["--report-only"]);
      expect(uses(refused)).toEqual([[8, 2], [8, 2]]);
      // The same for a refused direct fetch: the surplus does not hide a later fetch that has no block.
      const done = (id: string) => ({ type: "web_fetch_tool_result", tool_use_id: id, content: { type: "web_fetch_tool_error", error_code: "max_uses_exceeded" } });
      const fetches = standIn({ scan: (lane, request) => lane === "genomics" && request === 1 ? paused([{ ...fetched, id: "srvtoolu_g" }, done("srvtoolu_g"), fetched, done("srvtoolu_f"), search(1, { type: "code_execution_20260120", tool_id: "srvtoolu_c" })], 1, 1) : lane === "genomics" && request === 2 ? paused([], 0, 1) : {} });
      await run(fetches, github(), ["--report-only"]);
      expect(uses(fetches)).toEqual([[8, 2], [7, 2], [7, 1]]);
    });
    it("does not take off a direct call whose use is reported one reply late", async () => {
      const call = (name: string, id: string, input: any) => ({ type: "server_tool_use", id, name, input });
      const answer = (type: string, id: string) => ({ type, tool_use_id: id, content: [] });
      const reply = (content: any[], searches: number, fetches: number, stop = "pause_turn") => ({ stop_reason: stop, content: [...content, { type: "text", text: "scan notes so far" }], usage: { input_tokens: 1, output_tokens: 1, server_tool_use: { web_search_requests: searches, web_fetch_requests: fetches } } });
      const first = [call("web_search", "s1", { query: "q1" }), answer("web_search_tool_result", "s1"), call("web_search", "s2", { query: "q2" }), call("web_fetch", "f1", { url: "https://example.org/a" })];
      expect(pendingDirect(first)).toEqual({ searches: 1, fetches: 1 });
      expect(pendingDirect([...first, answer("web_search_tool_result", "s2"), answer("web_fetch_tool_result", "f1")])).toEqual({ searches: 0, fetches: 0 });
      expect(pendingDirect([{ ...first[2], caller: { type: "code_execution_20260120", tool_id: "c1" } }])).toEqual({ searches: 0, fetches: 0 });
      expect(pendingDirect(undefined)).toEqual({ searches: 0, fetches: 0 });
      // The first reply pauses on a search and a fetch that have not run. The second holds their
      // results and reports their use, with no call block, and one more search with no block at
      // all. Only that last one is taken off.
      const client = standIn({ scan: (lane, request) => lane !== "genomics" ? {}
        : request === 1 ? reply(first, 1, 0)
        : request === 2 ? reply([answer("web_search_tool_result", "s2"), answer("web_fetch_tool_result", "f1")], 2, 1) : {} });
      await run(client, github(), ["--report-only"]);
      const uses = client.calls.filter((c: any) => c.kind === "stream" && String(c.params.messages[0].content).includes("Lane: genomics.")).map((c: any) => c.params.tools.map((t: any) => t.max_uses));
      expect(uses).toEqual([[8, 2], [8, 2], [7, 2]]);
    });
    it("still reads a reported count of zero as zero", async () => {
      const client = standIn({ scan: (lane, request) => request === 1 ? { stop_reason: "pause_turn", usage: { input_tokens: 1, output_tokens: 1, server_tool_use: { web_search_requests: 0, web_fetch_requests: 0 } } } : {} });
      await run(client, github(), ["--report-only"]);
      expect(client.calls.filter((c) => c.kind === "stream").slice(0, 2).map((c) => c.params.tools.map((t: any) => t.max_uses))).toEqual([[8, 2], [8, 2]]);
    });
  });

  describe("candidates the judge rejected", () => {
    const stateFile = () => join(mkdtempSync(join(tmpdir(), "discovery-")), "state", "rejected.json");

    it("remembers a rejection and does not judge the candidate again the next day", async () => {
      const state = stateFile();
      const candidates = [scanCandidate("AlderFold", { aliases: ["Alder-Fold v1"] }), scanCandidate("BirchFold")];
      const first = standIn({ candidates, decision: "skip" });
      await run(first, github(), ["--state", state]);
      expect(first.judgedNames()).toEqual(["AlderFold", "BirchFold"]);
      const saved = JSON.parse(readFileSync(state, "utf8")).rejected;
      expect(saved.map((r: any) => [r.name, r.date, r.reason])).toEqual([["AlderFold", "2026-11-21", "an incremental checkpoint"], ["BirchFold", "2026-11-21", "an incremental checkpoint"]]);
      expect(saved[0].names).toEqual(["alderfold", "alder fold v 1"]);

      // Next day the scan returns the first under its alias, the second again, and one new name.
      const second = standIn({ candidates: [scanCandidate("Alder-Fold v1"), scanCandidate("BirchFold"), scanCandidate("CedarFold")] });
      const data = github();
      const { skipped, summary } = await run(second, data, ["--state", state], { now: new Date("2026-11-22T08:00:00Z") });
      expect(second.judgedNames()).toEqual(["CedarFold"]);
      expect(skipped!.find((s) => s.name === "BirchFold")?.reason).toBe("not judged again: the judge rejected it on 2026-11-21 (an incremental checkpoint); it can be judged again from 2026-12-21");
      expect(summary).toContain("The scan returned 2 candidates that the judge rejected in the last 30 days. None was judged again.");
      expect(data.created).toHaveLength(1);
      // The scan is told not to return them.
      const scan = String(second.calls[0].params.messages[0].content);
      expect(scan).toContain("Checked in an earlier run and not filed. Do not list these either:\n- AlderFold\n- BirchFold\n");
      expect(JSON.parse(readFileSync(state, "utf8")).rejected).toHaveLength(2);
    });
    it("judges a rejected candidate again once the lookback period has passed, and drops the old entry", async () => {
      const state = stateFile();
      await run(standIn({ candidates: [scanCandidate("AlderFold")], decision: "skip" }), github(), ["--state", state]);
      const later = standIn({ candidates: [scanCandidate("AlderFold")] });
      const data = github();
      await run(later, data, ["--state", state], { now: new Date("2026-12-21T08:00:00Z") });
      expect(later.judgedNames()).toEqual(["AlderFold"]);
      expect(data.created).toHaveLength(1);
      expect(JSON.parse(readFileSync(state, "utf8")).rejected).toEqual([]);
      const entry = [{ name: "AlderFold", names: ["alderfold"], date: "2026-11-21", reason: "" }];
      expect(findRejected({ name: "AlderFold" }, entry, "2026-12-20", 30)?.where).toBe("rejected");
      expect(findRejected({ name: "AlderFold" }, entry, "2026-12-21", 30)).toBeNull();
    });
    it("records only what the judge rejected: not a filed candidate, a failed call or a refusal", async () => {
      const state = stateFile();
      const client = standIn({ candidates: [scanCandidate("AlderFold"), scanCandidate("BirchFold")], judge: (name) => name === "BirchFold" ? { stop_reason: "refusal", content: [] } : {} });
      await run(client, github(), ["--state", state]);
      expect(JSON.parse(readFileSync(state, "utf8")).rejected).toEqual([]);
    });
    it("runs with a missing state file, says so when it cannot be read, and writes none in a dry run", async () => {
      const state = stateFile();
      const { summary } = await run(standIn({ candidates: [scanCandidate("AlderFold")] }), github(), ["--state", state, "--report-only"]);
      expect(summary).not.toContain("could not be read");
      writeFileSync(state, "{ not json");
      expect(readRejected(state)).toEqual([]);
      const again = await run(standIn({ candidates: [scanCandidate("AlderFold")] }), github(), ["--state", state, "--report-only"]);
      expect(again.summary).toContain("The rejected-candidate file could not be read");
      const dry = stateFile();
      await main(["--dry-run", "--fixtures", FIXTURES, "--state", dry], {}, { now, log: quiet });
      expect(existsSync(dry)).toBe(false);
    });
    it("is kept between runs by the workflow, and not in a dry run", () => {
      const workflow = readFileSync(".github/workflows/discovery.yml", "utf8");
      expect(workflow).toContain("uses: actions/cache/restore@v4");
      expect(workflow).toContain("restore-keys: discovery-state-");
      expect(workflow).toContain("if: always() && env.MODE != 'dry-run' && hashFiles('discovery-state/rejected.json') != ''");
      expect(workflow.match(/key: discovery-state-\$\{\{ github\.run_id \}\}-\$\{\{ github\.run_attempt \}\}/g)).toHaveLength(2);
      expect(workflow).toContain('report-only) args="--report-only --out discovery-out --state discovery-state/rejected.json"');
      expect(workflow).toContain('live) args="--out discovery-out --state discovery-state/rejected.json"');
      expect(workflow).toContain('dry-run) args="--dry-run --out discovery-out" ;;');
    });
  });

  describe("names under another spelling", () => {
    const candidate = (name: string) => ({ name, aliases: [], sources: [] });
    const known = async () => ({ issues: realIssues, storeNames: await readStoreNames(`${FIXTURES}/entities`, matchForm) });

    it("drops a known resource written with other spacing, hyphens, a v before the version or a trailing .0", async () => {
      const k = await known();
      const refs = Object.fromEntries(["BioEmu 2.0", "BioEmu v2", "Perturb-PFN", "Torch Craft", "CycPep-Net", "HyPLMFlash", "h-EVO", "Enchant-3", "Splice AI", "Protein Gym", "Bac-former"]
        .map((n) => [n, findDuplicate(candidate(n), k)?.ref.replace("rewire-bio/rewire-benchmark-data", "")]));
      expect(refs).toEqual({
        "BioEmu 2.0": "#241", "BioEmu v2": "#241", "Perturb-PFN": "#246", "Torch Craft": "#243", "CycPep-Net": "#283", "HyPLMFlash": "#233", "h-EVO": "#250",
        "Enchant-3": "#229", "Splice AI": "#336", "Protein Gym": "discovery-benchmark-proteingym", "Bac-former": "#245",
      });
      expect(spellForm("Enchant v3")).toBe(spellForm("Enchant-3"));
    });
    it("does not drop another version, a longer or shorter word, or a short name", async () => {
      const k = await known();
      for (const n of ["BioEmu-3", "Enchant v4", "ESM3", "ESM-2 650M", "ProteinGym-Indels", "Mimo", "Torch", "Bac", "h-E"]) expect([n, findDuplicate(candidate(n), k)]).toEqual([n, null]);
      // Words of a title that only run together by chance are not a name: "areas to" is not "AreaSto".
      expect(findDuplicate(candidate("Tierrule"), k)).toBeNull();
      // Three characters are too few to compare as a spelling.
      expect(findDuplicate(candidate("G-PT"), { issues: [{ repo: "r", number: 1, title: "Add GPT for cells" }] })).toBeNull();
      expect(findDuplicate(candidate("G-PTX"), { issues: [{ repo: "r", number: 1, title: "Add GPTX for cells" }] })?.ref).toBe("r#1");
    });
    it("gives the judge the records and requests that differ only by version or size, and no claim that the database lacks the resource", async () => {
      const k = await known();
      expect(nearMatches(candidate("ESM-2 650M"), k)).toEqual(['store record discovery-model-esm-2 ("esm 2")']);
      expect(nearMatches(candidate("BioEmu-3"), k)).toEqual(["rewire-bio/rewire-benchmark-data#241: Add BioEmu-2: October 2026 research preview"]);
      expect(nearMatches(candidate("AlderFold"), k)).toEqual([]);

      const client = standIn({ candidates: [scanCandidate("ESM-2 650M"), scanCandidate("AlderFold")] });
      await run(client, github(realIssues), ["--report-only"]);
      const near = client.judgePrompt("ESM-2 650M");
      expect(near).toContain('Records and requests with a similar name:\n- store record discovery-model-esm-2 ("esm 2")\nIf the candidate is one of these under another spelling, or only a size, checkpoint or minor release of it, conclude SKIP');
      expect(near).toContain(`A script compared the name and aliases with ${realIssues.length} issue titles and 4 record-store names and found none under this spelling.`);
      const plain = client.judgePrompt("AlderFold");
      expect(plain).not.toContain("similar name");
      for (const prompt of [near, plain]) expect(prompt).not.toContain("The database does not hold this resource");
    });
  });

  describe("reading GitHub", () => {
    it("lists open and closed issues on every page and leaves out pull requests", async () => {
      const urls: string[] = [];
      const pages: Record<string, any[]> = {
        "1": [{ number: 1, title: "Add One", body: null, state: "closed", labels: [{ name: "entity-request" }], user: { login: "someone" } }, { number: 2, title: "A pull request", pull_request: {} }],
        "2": [{ number: 3, title: "Add Three", body: "b", state: "open", labels: [] }],
      };
      const fake = async (url: any) => {
        urls.push(String(url));
        const page = /[?&]page=(\d+)/.exec(String(url))![1];
        return { ok: true, status: 200, json: async () => pages[page], headers: { get: () => page === "1" ? '<https://api.github.com/x?page=2>; rel="next"' : null } };
      };
      const issues = await githubClient("t", fake as any).listIssues("rewire-bio/rewire-benchmark-data");
      expect(urls).toEqual([1, 2].map((p) => `https://api.github.com/repos/rewire-bio/rewire-benchmark-data/issues?state=all&per_page=100&page=${p}`));
      expect(issues.map((i: any) => [i.number, i.state, i.labels])).toEqual([[1, "closed", ["entity-request"]], [3, "open", []]]);
    });
    it("drops a candidate named only in a rewire.it issue", async () => {
      const client = standIn({ candidates: [scanCandidate("AlderFold"), scanCandidate("BirchFold")] });
      const data = github();
      const articles = github([{ repo: "rewire-bio/rewire.it", number: 77, title: "Research AlderFold: what it changes", body: "", labels: ["article"] }]);
      const { skipped } = await run(client, data, [], { env: { ARTICLE_TOKEN: "t" }, deps: { articleGithub: articles } });
      expect(client.judgedNames()).toEqual(["BirchFold"]);
      expect(skipped!.find((s) => s.name === "AlderFold")?.reason).toBe('already known, not judged: "alderfold" is in the title of rewire-bio/rewire.it#77');
    });
  });

  describe("a reply resumed after pause_turn", () => {
    const text = (t: string) => [{ type: "text", text: t }];
    const structuredNotes = (client: ReturnType<typeof standIn>, marker: string) => String(client.calls.find((c) => c.kind === "create" && String(c.params.messages[0].content).includes(marker))?.params.messages[0].content);

    it("keeps the scan notes written before the pause", async () => {
      // The resumed reply holds only what was written after the pause.
      const client = standIn({
        candidates: [scanCandidate("AlderFold")],
        scan: (lane, request) => lane !== "genomics" ? {} : request === 1
          ? { stop_reason: "pause_turn", content: text("scan notes genomics, first part: AlderFold, a structure model.") }
          : { content: text("Second part: nothing further.") },
      });
      const { lanes } = await run(client, github(), ["--report-only"]);
      const notes = structuredNotes(client, "first part");
      expect(notes).toContain("scan notes genomics, first part: AlderFold, a structure model.\n\nSecond part: nothing further.");
      expect(client.judgedNames()).toEqual(["AlderFold"]);
      const genomics = lanes!.find((l: any) => l.lane === "genomics")!;
      expect(genomics.requests.map((r: any) => r.stop_reason)).toEqual(["pause_turn", "end_turn"]);
      expect(genomics.notes).toContain("first part");
    });
    it("keeps the judge notes written before the pause, and still reads the verdict at the end", async () => {
      const requests: Record<string, number> = {};
      const client = standIn({
        candidates: [scanCandidate("AlderFold")],
        judge: (name) => (requests[name] = (requests[name] ?? 0) + 1) === 1
          ? { stop_reason: "pause_turn", content: text(`notes for ${name}\nSources opened: the preprint.`) }
          : { content: text("The weights are new.\nFILE") },
      });
      const data = github();
      await run(client, data);
      expect(structuredNotes(client, "Sources opened")).toContain("Sources opened: the preprint.\n\nThe weights are new.\nFILE");
      expect(data.created).toHaveLength(1);
    });
    it("reads the verdict the judge ends with, not a SKIP it wrote before the pause", async () => {
      const requests: Record<string, number> = {};
      const client = standIn({
        candidates: [scanCandidate("AlderFold")],
        judge: (name) => (requests[name] = (requests[name] ?? 0) + 1) === 1
          ? { stop_reason: "pause_turn", content: text(`notes for ${name}\nI will end with FILE or SKIP.\nFirst reading: SKIP, it looks like a checkpoint.`) }
          : { content: text("The preprint shows a new architecture.\nFILE") },
      });
      const data = github();
      await run(client, data);
      expect(data.created).toHaveLength(1);
    });
    it("records why a lane has no notes", async () => {
      const lines: string[] = [];
      const client = standIn({ scan: (lane) => lane === "genomics" ? { stop_reason: "refusal", stop_details: { category: "bio" }, content: [] } : {} });
      const { lanes, summary } = await run(client, github(), ["--report-only"], { deps: { log: (m: string) => lines.push(m) } });
      expect(lines).toContain("scan genomics: 1 searches, no candidate list (no notes; the last request stopped with refusal)");
      expect(lanes!.find((l: any) => l.lane === "genomics")!.requests).toHaveLength(1);
      expect(summary).toContain("| genomics | no notes; the last request stopped with refusal | 1 | 1 | 0 | 0 | 0 | 0 | 0 |");
      expect(summary).toContain('Scan lane "genomics" was refused or did not finish.');
    });
  });

  describe("what a live run writes to --out", () => {
    it("marks a lane whose scan was cut at max_tokens, in its line, its file and the summary", async () => {
      const out = mkdtempSync(join(tmpdir(), "discovery-"));
      const lines: string[] = [];
      const client = standIn({ candidates: [scanCandidate("AlderFold")], scan: (lane) => lane === "genomics" ? { stop_reason: "max_tokens" } : {} });
      const { summary } = await run(client, github(), ["--report-only", "--out", out], { deps: { log: (m: string) => lines.push(m) } });
      const status = "finished; the notes were cut at max_tokens and may be incomplete";
      expect(lines).toContain(`scan genomics: 1 searches, 1 raw candidates, 0 dropped as known, 0 dropped as remembered, 0 dropped for another reason, 1 to judge (${status})`);
      expect(lines).toContain("scan proteins: 1 searches, 0 raw candidates, 0 dropped as known, 0 dropped as remembered, 0 dropped for another reason, 0 to judge");
      expect(JSON.parse(readFileSync(join(out, "scan", "genomics.json"), "utf8")).status).toBe(status);
      expect(summary).toContain(`| genomics | ${status} | 1 | 1 | 1 | 0 | 0 | 0 | 1 |`);
      // The candidates in cut notes are still judged.
      expect(client.judgedNames()).toEqual(["AlderFold"]);
    });
    it("lists a candidate with no name in the lane file and not among the skipped names", async () => {
      const out = mkdtempSync(join(tmpdir(), "discovery-"));
      const client = standIn({ candidates: [scanCandidate(""), scanCandidate("Bacformer"), scanCandidate("AlderFold")] });
      const { skipped, summary } = await run(client, github(), ["--report-only", "--out", out]);
      expect(JSON.parse(readFileSync(join(out, "scan", "genomics.json"), "utf8")).dropped.map((d: any) => d.name)).toEqual(["(no name)", "Bacformer"]);
      expect(skipped!.map((s) => s.name)).toEqual(["Bacformer"]);
      expect(summary).not.toContain("- (no name)");
    });
    it("finishes the run and says so when the lane files cannot be written", async () => {
      const out = mkdtempSync(join(tmpdir(), "discovery-"));
      writeFileSync(join(out, "scan"), "a file where the folder should be");
      const lines: string[] = [];
      const data = github();
      const { planned } = await run(standIn({ candidates: [scanCandidate("AlderFold")] }), data, ["--out", out], { deps: { log: (m: string) => lines.push(m) } });
      expect(planned.map((p) => p.name)).toEqual(["AlderFold"]);
      expect(data.created).toHaveLength(1);
      expect(existsSync(join(out, "usage.json"))).toBe(true);
      expect(lines.find((l) => l.startsWith("::warning::The lane files could not be written"))).toBeTruthy();
    });
    it("keeps the error that ended a run when the lane files cannot be written either", async () => {
      const out = mkdtempSync(join(tmpdir(), "discovery-"));
      writeFileSync(join(out, "scan"), "a file where the folder should be");
      const data = { ...github(), async createIssue() { throw new Error("GitHub is down"); } };
      await expect(run(standIn({ candidates: [scanCandidate("AlderFold")] }), data, ["--out", out])).rejects.toThrow("GitHub is down");
    });
    it("counts a remembered rejection apart from a known name, and keeps tokens out of the lane files", async () => {
      const state = join(mkdtempSync(join(tmpdir(), "discovery-")), "state", "rejected.json");
      await run(standIn({ candidates: [scanCandidate("AlderFold")], decision: "skip" }), github(), ["--state", state]);
      const out = mkdtempSync(join(tmpdir(), "discovery-"));
      const key = "sk-ant-fixture-0123456789";
      const lines: string[] = [];
      const client = standIn({
        candidates: [scanCandidate("AlderFold"), scanCandidate("Bacformer"), scanCandidate("CedarFold")],
        scan: (lane) => lane === "genomics" ? { content: [
          { type: "server_tool_use", id: "s1", name: "web_search", input: { query: `bioRxiv protein structure ${key}` } },
          { type: "web_search_tool_result", tool_use_id: "s1", content: [{ type: "web_search_result", url: "https://www.biorxiv.org/content/10.1101/2026.11.01.800001v1", title: "CedarFold" }] },
          { type: "text", text: `scan notes genomics ${key}` },
        ] } : {},
      });
      await run(client, github(), ["--state", state, "--out", out], { now: new Date("2026-11-22T08:00:00Z"), env: { ANTHROPIC_API_KEY: key }, deps: { log: (m: string) => lines.push(m) } });
      expect(lines).toContain("scan genomics: 1 searches (1 direct), 3 raw candidates, 1 dropped as known, 1 dropped as remembered, 0 dropped for another reason, 1 to judge");
      const genomics = JSON.parse(readFileSync(join(out, "scan", "genomics.json"), "utf8"));
      expect(genomics.dropped.map((d: any) => [d.name, d.category])).toEqual([["AlderFold", "remembered"], ["Bacformer", "known"]]);
      expect(genomics.queries).toEqual(["bioRxiv protein structure [redacted]"]);
      for (const file of readdirSync(join(out, "scan"))) expect(readFileSync(join(out, "scan", file), "utf8")).not.toContain(key);
      expect(readFileSync(join(out, "scan", "genomics-notes.md"), "utf8")).toBe("scan notes genomics [redacted]\n");
      // A lane that found nothing still has its files.
      expect(JSON.parse(readFileSync(join(out, "scan", "proteins.json"), "utf8")).counts).toMatchObject({ raw: 0, to_judge: 0 });
    });
  });
});
