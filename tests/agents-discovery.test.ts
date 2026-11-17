import { mkdtempSync, readFileSync, readdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import {
  AREAS, GENOMIC_AREAS, PROTEIN_AREAS, Usage, clean, findDuplicate, identifiersOf, keyOf, main, parseBlogIndex,
  planFiling, readStoreNames, renderArticleIssue, renderDataIssue, tierOf,
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
        reply = paused ? msg("scan notes") : msg("partial", "pause_turn");
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
          if (notes.includes("scan notes")) {
            return msg(JSON.stringify({ candidates: [
              { name: "GenoNova fixture", aliases: [], kind: "model", summary: "s", urls: ["https://doi.org/10.1101/2026.11.10.700001"], in_scope: true, reason: "" },
              { name: "MIMOSA", aliases: [], kind: "method", summary: "s", urls: [], in_scope: true, reason: "" },
              { name: "Off topic", aliases: [], kind: "model", summary: "s", urls: [], in_scope: false, reason: "not biology" },
              { name: "ProtSpec fixture", aliases: [], kind: "model", summary: "s", urls: [], in_scope: true, reason: "" },
            ] }), "end_turn", { input_tokens: 500, output_tokens: 50 } as any);
          }
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
    expect(streams).toHaveLength(4);
    expect(streams.every((c) => c.params.tools.map((t: any) => t.type).join() === "web_search_20260318,web_fetch_20260209")).toBe(true);
    // The scan runs on Haiku, without the fallback Haiku does not offer, and resumes its pause_turn.
    expect(streams.slice(0, 2).map((c) => [c.params.model, c.params.fallbacks])).toEqual([["claude-haiku-5-5", undefined], ["claude-haiku-5-5", undefined]]);
    expect(streams[1].params.messages.at(-1).role).toBe("assistant");
    // The judge runs on Sonnet with the refusal fallback.
    expect(streams.slice(2).map((c) => [c.params.model, c.params.fallbacks])).toEqual([["claude-sonnet-5-5", "default"], ["claude-sonnet-5-5", "default"]]);
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
    expect(usage!.byModel["claude-haiku-5-5"].webSearches).toBe(4);
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
