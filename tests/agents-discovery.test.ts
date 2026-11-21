import { mkdtempSync, readFileSync, readdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import {
  AREAS, GENOMIC_AREAS, LABELS, LIMITS, PRICES, PROTEIN_AREAS, SCAN_LANES, Usage, ageInDays, clean, dataLabels, findDuplicate,
  identifiersOf, keyOf, knownTitles, main, matchForm, parseBlogIndex, planFiling, readStoreNames, renderArticleIssue,
  renderDataIssue, scanPrompt, tierOf,
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
    expect(readdirSync(out).sort()).toEqual(["1-data.md", "2-data.md", "3-data.md", "4-data.md", "5-data.md", "plan.json", "usage.json"]);
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
    // 13 searches a lane is $0.13: after two lanes a third would pass $0.35.
    const client = replay({ searches: 13 });
    const { summary, usage } = await main([...args, "--report-only"], env, { now: runDay, log: quiet, anthropic: client, github: github(realIssues), fetch: blog });
    expect(summary).toContain('Scan lane "cells and other biology" was not run: the scan would have passed $0.35.');
    expect(client.calls.filter((c) => c.kind === "stream" && String(c.params.messages[0].content).includes("Find AI-for-biology"))).toHaveLength(2);
    expect(usage!.byModel["claude-haiku-5-5"].webSearches).toBe(26);
  });

  it("uses the notes written so far when a lane stops at the resume cap, and gives each resume what is left", async () => {
    const client = replay({ searches: 3, pauseForever: "genomics" });
    const { planned, skipped } = await main([...args, "--report-only"], env, { now: runDay, log: quiet, anthropic: client, github: github(realIssues), fetch: blog });
    const genomics = client.calls.filter((c) => c.kind === "stream" && String(c.params.messages[0].content).includes("Lane: genomics."));
    expect(genomics.map((c) => c.params.tools[0].max_uses)).toEqual([8, 5, 2]);
    expect(planned.map((p) => p.name)).toContain("GenoNova fixture");
    expect(skipped!.find((s) => s.name === "Bacformer")?.reason).toContain("already known, not judged");
  });

  it("rotates the first lane by day", async () => {
    const client = replay();
    await main([...args, "--report-only"], env, { now: new Date("2026-11-22T08:00:00Z"), log: quiet, anthropic: client, github: github(realIssues), fetch: blog });
    expect(String(client.calls[0].params.messages[0].content)).toContain("Lane: proteins.");
  });
});
