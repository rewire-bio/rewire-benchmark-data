import { mkdtempSync, readFileSync, readdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import {
  LABEL, LIMITS, SWEEP_LABEL, candidatesFor, checkLink, checkedValue, confirmPrompt, factsText, isPlaceholder, checkpointBase, fixtureFetch, githubFacts, hfFacts, hfIdsInText, knownFromIssues, licenceAgrees, main, markUmbrellas, parseUpdateMarker, pinnedCommit, planIssues, refsOf, renderUpdateIssue, tiersDue,
} from "../scripts/agents/sweep.mjs";

// The monthly entity sweep (#257). Everything here runs without an API key or network: the dry
// run reads the store, the HTTP answers, the model answers and the existing issues from
// tests/agents-sweep-fixtures. The fixture store has six tier 1 entities (a model with a new
// release and a licence change, one with new Hugging Face checkpoints, one whose repository was
// archived and already reported, one that only cites a shared leaderboard repository, a benchmark
// whose page announces a new version, a use case with dead and blocked links), one tier 2 model
// with a new release and one tier 3 model.
const FIXTURES = "tests/agents-sweep-fixtures";
const quiet = () => {};
const at = (iso: string) => () => new Date(iso);
const dirs: string[] = [];
const tempDir = () => {
  const d = mkdtempSync(join(tmpdir(), "sweep-"));
  dirs.push(d);
  return d;
};
afterEach(() => {
  for (const d of dirs.splice(0)) rmSync(d, { recursive: true, force: true });
});
const dryRun = (now = "2026-12-01T05:00:00Z", extra: string[] = []) => main(["--dry-run", ...extra], {}, { now: at(now), log: quiet });

describe("schedule", () => {
  it("sweeps tier 1 every month and tier 2 in January, April, July and October, never tier 3", () => {
    expect(tiersDue(new Date("2026-12-01T05:00:00Z"))).toEqual([1]);
    for (const month of ["01", "04", "07", "10"]) expect(tiersDue(new Date(`2027-${month}-01T05:00:00Z`))).toEqual([1, 2]);
    expect(tiersDue(new Date("2026-12-01"), "2")).toEqual([2]);
    expect(tiersDue(new Date("2026-12-01"), "1,2")).toEqual([1, 2]);
    expect(() => tiersDue(new Date("2026-12-01"), "3")).toThrow("tier 3 is never swept");
  });

  it("does not collide with the other scheduled workflows", () => {
    const cron = /cron: "([^"]+)"/.exec(readFileSync(".github/workflows/sweep.yml", "utf8"))?.[1];
    expect(cron).toBe("0 5 1 * *");
    for (const f of ["pipeline-alert.yml", "discovery.yml", "digest.yml"]) {
      const other = /cron: "([^"]+)"/.exec(readFileSync(`.github/workflows/${f}`, "utf8"))?.[1] ?? "";
      expect(other.split(" ").slice(0, 2).join(" "), f).not.toBe("0 5");
    }
  });
});

describe("deterministic checks", () => {
  it("counts a link dead only on 404 or 410 after a GET, or a host that does not resolve", async () => {
    const fetchImpl = fixtureFetch({
      "HEAD https://a.example.org/x": { status: 405 },
      "https://a.example.org/x": { status: 200, text: "ok" },
      "https://b.example.org/gone": { status: 404 },
      "https://c.example.org/wall": { status: 403 },
      "https://d.example.org/slow": { status: 429 },
      "https://e.example.invalid/x": { error: "ENOTFOUND" },
    }) as unknown as typeof fetch;
    expect((await checkLink("https://a.example.org/x", fetchImpl)).state).toBe("ok");
    expect((await checkLink("https://b.example.org/gone", fetchImpl)).state).toBe("dead");
    expect((await checkLink("https://c.example.org/wall", fetchImpl)).state).toBe("blocked");
    expect((await checkLink("https://d.example.org/slow", fetchImpl)).state).toBe("blocked");
    expect((await checkLink("https://e.example.invalid/x", fetchImpl)).state).toBe("dead");
  });

  it("reads Hugging Face IDs from record text, checkpoint base names and licence statements", () => {
    expect(hfIdsInText("Public Hugging Face checkpoint tattabio/gLM2_650M.")).toEqual(["tattabio/gLM2_650M"]);
    expect(hfIdsInText("See https://huggingface.co/InstaDeepAI/segment_nt and Hugging Face models a/b-1, c/d")).toEqual(["InstaDeepAI/segment_nt", "a/b-1", "c/d"]);
    expect(checkpointBase("gLM2_650M")).toBe("gLM2");
    expect(checkpointBase("Dune_100M")).toBe("Dune");
    expect(licenceAgrees("Apache-2.0 for the code and models", "apache-2.0")).toBe(true);
    expect(licenceAgrees("MIT License", "MIT")).toBe(true);
    expect(licenceAgrees("MIT", "Apache-2.0")).toBe(false);
    expect(licenceAgrees("Code: MIT (songlab-cal/gpn). Checkpoint licence not checked.", "MIT")).toBe(true);
  });
});

describe("dry run", () => {
  it("files one issue per entity and action, for confirmed changes only, in the format intake reads", async () => {
    const r = await dryRun();
    const titles = r.plan.file.map((p: { issue: { title: string } }) => p.issue.title);
    expect(titles).toEqual([
      "Add new checkpoint rewire-fixtures/Dune_500M related to Dune",
      "Update Helix: licence, new release",
      "Update Arena: new benchmark version",
    ]);
    for (const p of r.plan.file) {
      expect(p.issue.labels).toEqual([LABEL, "tier-1"]);
      expect(p.issue.body).not.toMatch(/[–—]/);
      expect(p.issue.body).not.toMatch(/Generated with|Co-Authored-By/i);
    }
    const helix = parseUpdateMarker(r.plan.file[1].issue.body);
    expect(helix).toEqual({
      record_id: "fixture-model-helix", kind: "model", action: "update",
      fields: { licence: "Apache-2.0 for the code in rewire-fixtures/helix", version: "v1.2 (GitHub release, 2026-10-10)" },
      evidence: ["https://github.com/rewire-fixtures/helix", "https://github.com/x/releases/tag/v1.2"],
    });
    // The prerelease after v1.0 is not proposed; the newest full release is.
    expect(r.plan.file[1].issue.body).not.toContain("v1.2-rc1 (");
    const dune = parseUpdateMarker(r.plan.file[0].issue.body);
    expect(dune).toMatchObject({ action: "add", names: ["rewire-fixtures/Dune_500M"] });
    // The add issue names its source URL in the body, where intake's draft looks for it.
    expect(r.plan.file[0].issue.body).toContain("- https://huggingface.co/rewire-fixtures/Dune_500M");
  });

  it("drops what Sonnet does not confirm, what an earlier issue filed, and repositories that are not the entity's own", async () => {
    const r = await dryRun();
    expect(r.unconfirmed.map((u: { observed: string }) => u.observed).sort()).toEqual(["rewire-fixtures/Dune_100M-GGUF", "rewire-fixtures/Dunes-demo"]);
    expect(r.plan.skipped.map((s: { key: string }) => s.key)).toEqual(["fixture-model-quarry:archived:rewirefixturesquarry"]);
    const all = JSON.stringify(r.plan.file);
    // Mosaic only cites a shared leaderboard repository with a new release.
    expect(all).not.toContain("fixture-model-shared");
    // Tier 2 waits for January and tier 3 is never swept.
    expect(r.entities.map((e: { id: string }) => e.id)).not.toContain("fixture-model-fold");
    expect(r.entities.map((e: { id: string }) => e.id)).not.toContain("fixture-model-cells");
  });

  it("groups new dead links in one issue that intake ignores, and leaves blocked links out", async () => {
    const r = await dryRun();
    expect(r.dead.map((d: { url: string }) => d.url)).toEqual(["https://gone.example.invalid-host.org/data"]);
    expect(r.blocked.map((b: { url: string }) => b.url).sort()).toEqual(["https://doi.org/10.1000/fixture.1", "https://www.biorxiv.org/content/10.1101/2026.01.01.000001v1"]);
    expect(r.deadIssue.labels).toEqual([SWEEP_LABEL]);
    expect(r.deadIssue.labels).not.toContain(LABEL);
    expect(r.deadIssue.body).toContain("fixture-use-case-splicing");
    // The archived and moved repository of a benchmark, which has no access field, is reported here.
    expect(r.deadIssue.body).toContain("rewire-fixtures/arena now Rewire-Fixtures/arena-benchmark");
    // A 404 already listed in a sweep issue is not listed again.
    expect(r.deadIssue.body).not.toContain("lab.example.org");
  });

  it("does not list a dead link or repository change again once its issue is closed", () => {
    const known = knownFromIssues([{ state: "closed", body: "<!-- entity-sweep-dead: https://lab.example.org/x -->\n<!-- entity-sweep-dead: fixture-benchmark-arena:archived:rewire-fixtures/arena -->" }]);
    expect(known.dead.has("https://lab.example.org/x")).toBe(true);
    expect(known.dead.has("fixture-benchmark-arena:archived:rewire-fixtures/arena")).toBe(true);
  });

  it("adds tier 2 in a quarter month, and leaves a change without a confirmation unfiled", async () => {
    const r = await dryRun("2027-01-01T05:00:00Z");
    expect(r.entities.map((e: { id: string }) => e.id)).toContain("fixture-model-fold");
    expect(r.unconfirmed).toContainEqual(expect.objectContaining({ record_id: "fixture-model-fold", observed: "v0.2" }));
    expect(JSON.stringify(r.plan.file)).not.toContain("fixture-model-fold");
  });

  it("honours --limit and --ids, and writes the plan, the issue bodies and usage.json", async () => {
    const out = tempDir();
    const r = await dryRun("2026-12-01T05:00:00Z", ["--ids", "fixture-model-helix", "--out", out]);
    expect(r.entities.map((e: { id: string }) => e.id)).toEqual(["fixture-model-helix"]);
    expect((await dryRun("2026-12-01T05:00:00Z", ["--limit", "2"])).entities).toHaveLength(2);
    expect(readdirSync(join(out, "issues"))).toEqual(["01.md"]);
    expect(JSON.parse(readFileSync(join(out, "usage.json"), "utf8"))).toMatchObject({ estimatedUsd: 0 });
    expect(JSON.parse(readFileSync(join(out, "plan.json"), "utf8")).issues[0].record_id).toBe("fixture-model-helix");
  });
});

describe("planning", () => {
  const record = { id: "r1", kind: "model", name: "R", attributes: { depth_tier: 1, version: "v1" } };
  const change = (n: number) => ({ type: "release", field: "version", action: "update" as const, observed: `v${n}`, current: "v1", value: `v${n}`, reason: "new", evidence: ["https://github.com/a/b"], key: `r${n}:release:v${n}`, facts: {} });

  it("caps the issues per run and lists the rest in one summary issue", () => {
    const confirmed = Array.from({ length: LIMITS.maxIssues + 2 }, (_, n) => ({ record: { ...record, id: `r${String(n).padStart(2, "0")}` }, changes: [change(n)] }));
    const plan = planIssues(confirmed, { issues: [], runDate: "2026-12-01" });
    expect(plan.file).toHaveLength(LIMITS.maxIssues);
    expect(plan.overflow).toHaveLength(2);
    expect(plan.overflowIssue?.labels).toEqual([SWEEP_LABEL]);
    expect(plan.overflowIssue?.body).toContain("r15");
    // A second run in the same month does not file the summary again.
    const again = planIssues(confirmed, { issues: [{ state: "open", body: plan.overflowIssue?.body }], runDate: "2026-12-01" });
    expect(again.overflowIssue).toBeNull();
  });

  it("dedupes against earlier issues by change key, open or closed", () => {
    const plan = planIssues([{ record, changes: [change(2), change(3)] }], { issues: [{ state: "closed", body: "<!-- entity-update-key: r2:release:v2 -->" }], runDate: "2026-12-01" });
    expect(plan.file).toHaveLength(1);
    expect(plan.file[0].changes.map((c: { key: string }) => c.key)).toEqual(["r3:release:v3"]);
  });

  it("keeps a marker readable when a value contains a comment terminator", () => {
    const issue = renderUpdateIssue({ record, action: "update", changes: [{ ...change(2), value: "v2 --> sneaky" }], runDate: "2026-12-01" });
    expect(parseUpdateMarker(issue.body)?.fields).toEqual({ version: "v2 --> sneaky" });
  });
});

describe("live and report-only runs with fakes", () => {
  const answers = JSON.parse(readFileSync(`${FIXTURES}/models.json`, "utf8"));
  const http = JSON.parse(readFileSync(`${FIXTURES}/http.json`, "utf8"));
  const issues = JSON.parse(readFileSync(`${FIXTURES}/issues.json`, "utf8"));
  const env = { ANTHROPIC_API_KEY: "test", GITHUB_REPOSITORY: "rewire-bio/rewire-benchmark-data", APP_TOKEN: "true", RUN_URL: "https://run/1" };

  function fakes({ inputTokens = 1000 } = {}) {
    const calls: { model: string; thinking?: unknown; fallbacks?: unknown; prompt: string }[] = [];
    const created: { title: string; labels: string[] }[] = [];
    const reply = (value: unknown) => ({ stop_reason: "end_turn", content: [{ type: "text", text: JSON.stringify(value) }], usage: { input_tokens: inputTokens, output_tokens: 100 } });
    const answerFor = (prompt: string) => {
      if (prompt.startsWith("Benchmark page check")) return answers.pages["https://arena.example.org/"];
      const id = /Record (\S+) \(/.exec(prompt)?.[1] ?? "";
      return answers.confirm[id] ?? { changes: [] };
    };
    const anthropic = {
      messages: { create: async (req: { model: string; thinking?: unknown; messages: { content: string }[] }) => {
        calls.push({ model: req.model, thinking: req.thinking, prompt: req.messages[0].content });
        return { model: req.model, ...reply(answerFor(req.messages[0].content)) };
      } },
      beta: { messages: { create: async (req: { model: string; fallbacks?: unknown; messages: { content: string }[] }) => {
        calls.push({ model: req.model, fallbacks: req.fallbacks, prompt: req.messages[0].content });
        return { model: req.model, ...reply(answerFor(req.messages[0].content)) };
      } } },
    };
    const github = {
      listIssues: async () => issues,
      ensureLabels: async () => {},
      createIssue: async (_repo: string, issue: { title: string; labels: string[] }) => {
        created.push(issue);
        return { html_url: `https://github.com/rewire-bio/rewire-benchmark-data/issues/${600 + created.length}` };
      },
    };
    const deps = { anthropic, github, fetch: fixtureFetch(http), now: at("2026-12-01T05:00:00Z"), log: quiet };
    return { calls, created, deps };
  }
  const args = ["--store-dir", `${FIXTURES}/entities`];

  it("uses Haiku with thinking off to read a changed page and Sonnet with the fallback to confirm, then files the issues", async () => {
    const f = fakes();
    const r = await main(args, env, f.deps);
    const haiku = f.calls.filter((c) => c.model === "claude-haiku-5-5");
    const sonnet = f.calls.filter((c) => c.model === "claude-sonnet-5-5");
    expect(haiku).toHaveLength(1); // one changed page; ownership is never asked
    for (const c of haiku) expect(c.thinking).toEqual({ type: "disabled" });
    expect(sonnet.map((c) => /Record (\S+)/.exec(c.prompt)?.[1]).sort()).toEqual(["fixture-benchmark-arena", "fixture-model-dune", "fixture-model-helix", "fixture-model-quarry"]);
    for (const c of sonnet) expect(c.fallbacks).toBe("default");
    expect(f.created.map((i) => i.labels)).toEqual([[LABEL, "tier-1"], [LABEL, "tier-1"], [LABEL, "tier-1"], [SWEEP_LABEL]]);
    expect(r.filed.size).toBe(4);
    expect(r.usage.total()).toBeGreaterThan(0);
  });

  it("does not file a value Sonnet wrote that the APIs did not observe", async () => {
    const f = fakes();
    const helix = answers.confirm["fixture-model-helix"];
    const create = f.deps.anthropic.beta.messages.create;
    f.deps.anthropic.beta.messages.create = async (req: { model: string; fallbacks?: unknown; messages: { content: string }[] }) => {
      const res = await create(req);
      if (!req.messages[0].content.includes("Record fixture-model-helix ")) return res;
      const changes = helix.changes.map((c: { n: number }) => (c.n === 1 ? { ...c, value: "v9.9.9 (GitHub release, 2027-01-01)" } : c));
      return { ...res, content: [{ type: "text", text: JSON.stringify({ changes }) }] };
    };
    const r = await main([...args, "--report-only"], env, f.deps);
    const marker = parseUpdateMarker(r.plan.file.find((p: { record: { id: string } }) => p.record.id === "fixture-model-helix").issue.body);
    expect(marker?.fields).toEqual({ licence: "Apache-2.0 for the code in rewire-fixtures/helix" });
    expect(r.unconfirmed).toContainEqual(expect.objectContaining({ record_id: "fixture-model-helix", observed: "v1.2", reason: expect.stringContaining("does not carry the observed value") }));
  });

  it("writes usage.json even when filing an issue fails", async () => {
    const out = tempDir();
    const f = fakes();
    f.deps.github.createIssue = async () => {
      throw new Error("GitHub said no");
    };
    await expect(main([...args, "--out", out], env, f.deps)).rejects.toThrow("GitHub said no");
    expect(JSON.parse(readFileSync(join(out, "usage.json"), "utf8")).estimatedUsd).toBeGreaterThan(0);
  });

  it("files nothing in report-only mode", async () => {
    const f = fakes();
    const r = await main([...args, "--report-only"], env, f.deps);
    expect(f.created).toEqual([]);
    expect(r.plan.file).toHaveLength(3);
  });

  it("stops calling models at the cost cap and files nothing it could not confirm", async () => {
    // 20 million input tokens on Haiku cost $2 at the higher band: the first call uses up the cap.
    const f = fakes({ inputTokens: 20_000_000 });
    const r = await main(args, env, f.deps);
    expect(f.calls).toHaveLength(1);
    expect(r.unconfirmed.length).toBeGreaterThan(0);
    expect(r.unconfirmed.every((u: { reason: string }) => u.reason.includes("cost cap"))).toBe(true);
    expect(f.created.map((i) => i.labels)).toEqual([[SWEEP_LABEL]]);
  });

  it("runs the checks without a key but confirms and files nothing", async () => {
    const f = fakes();
    const r = await main(args, { GITHUB_REPOSITORY: "rewire-bio/rewire-benchmark-data" }, { ...f.deps, anthropic: undefined });
    expect(f.created).toEqual([]);
    expect(r.summary).toContain("ANTHROPIC_API_KEY is not set");
    expect(r.unconfirmed.length).toBeGreaterThan(0);
  });

  it("refuses to run outside rewire-bio", async () => {
    await expect(main(args, { ...env, GITHUB_REPOSITORY: "someone/fork" }, fakes().deps)).rejects.toThrow("only runs in rewire-bio");
  });
});

describe("candidates are changes, not gaps the model fills", () => {
  const facts = (releases: { tag: string; published_at: string }[]) => new Map([["github:o/tool", { state: "ok", archived: false, licence: null, html_url: "https://github.com/o/tool", releases: releases.map((r) => ({ ...r, url: `https://github.com/o/tool/releases/tag/${r.tag}` })) }]]);
  const ref = { host: "github", owner: "o", repo: "tool", name: "tool", own: true, exact: true, baseline: "2026-09-16T00:00:00Z", urls: ["https://github.com/o/tool"] };
  const old = { tag: "v1.0.1", published_at: "2022-03-06T00:00:00Z" };
  const fresh = { tag: "v2.0.0", published_at: "2026-10-01T00:00:00Z" };
  const rec = (attributes: Record<string, unknown>, kind = "model") => ({ id: "r", kind, name: "Tool", attributes: { depth_tier: 1, ...attributes } });
  const gap = { missing_metadata: { version: { reason: "unextracted" } } };

  it("proposes no version for a model family that has none", () => {
    expect(candidatesFor(rec({ entity_level: "family", ...gap }), { repos: [ref], pages: [] }, { facts: facts([fresh]) }).candidates).toEqual([]);
  });

  it("counts only releases after the stored sources, and labels a missing version as a gap", () => {
    expect(candidatesFor(rec({ entity_level: "checkpoint", ...gap }), { repos: [ref], pages: [] }, { facts: facts([old]) }).candidates).toEqual([]);
    const [c] = candidatesFor(rec({ entity_level: "checkpoint", ...gap }), { repos: [ref], pages: [] }, { facts: facts([fresh, old]) }).candidates;
    expect(c).toMatchObject({ type: "version_gap", observed: "v2.0.0" });
    expect(c.facts.releases_since_baseline.map((r: { tag: string }) => r.tag)).toEqual(["v2.0.0"]);
    const [r] = candidatesFor(rec({ entity_level: "family", version: "v1.0.1" }), { repos: [ref], pages: [] }, { facts: facts([fresh, old]) }).candidates;
    expect(r).toMatchObject({ type: "release", observed: "v2.0.0" });
  });

  it("does not count an umbrella repository that matches several records as any one record's own", () => {
    const sources = new Map([["s1", { id: "s1", attributes: { url: "https://github.com/facebookresearch/esm" } }]]);
    const records = ["ESM-1v", "ESMFold2", "ESM-2"].map((name, n) => ({ id: `m${n}`, kind: "model", name, source_ids: ["s1"], attributes: { depth_tier: 1 } }));
    // m9 names the Hugging Face repository in its own access text; m8 only matches it by name.
    sources.set("s2", { id: "s2", attributes: { url: "https://huggingface.co/facebook/esm2_t33" } });
    const named = { id: "m9", kind: "model", name: "ESM2 t33", source_ids: ["s2"], attributes: { depth_tier: 1, access: "Hugging Face checkpoint facebook/esm2_t33." } };
    const alias = { id: "m8", kind: "model", name: "ESM2 t33 fine-tune", source_ids: ["s2"], attributes: { depth_tier: 1 } };
    const refsById = new Map([...records, named, alias].map((r) => [r.id, refsOf(r, sources)]));
    // Without the umbrella rule "esm" is inside every name, so each record would claim the repository.
    expect(refsById.get("m1")?.repos[0].own).toBe(true);
    markUmbrellas(refsById, [...refsById.values()]);
    for (const id of ["m0", "m1", "m2"]) expect(refsById.get(id)?.repos[0]).toMatchObject({ own: false, ambiguous: true });
    // A repository the record's own fields name stays its own; another record matching it by name does not.
    expect(refsById.get("m9")?.repos[0]).toMatchObject({ own: true, named: true });
    expect(refsById.get("m8")?.repos[0]).toMatchObject({ own: false, ambiguous: true });
  });

  it("keeps a repository named exactly for the record, and does not count a duplicate record as a second claimant", () => {
    const sources = new Map([["s1", { id: "s1", attributes: { url: "https://github.com/songlab-cal/tape" } }], ["s2", { id: "s2", attributes: { url: "https://github.com/Illumina/SpliceAI" } }]]);
    const rec = (id: string, name: string, src: string, kind = "model") => ({ id, kind, name, source_ids: [src], attributes: { depth_tier: 1 } });
    const all = [rec("b", "TAPE", "s1", "benchmark"), rec("l", "TAPE LSTM", "s1"), rec("c", "SpliceAI", "s2"), rec("d", "SpliceAI", "s2")];
    const refsById = new Map(all.map((r) => [r.id, refsOf(r, sources)]));
    markUmbrellas(refsById, [...refsById.values()]);
    expect(refsById.get("b")?.repos[0].own).toBe(true);
    expect(refsById.get("l")?.repos[0].own).toBe(false);
    expect(refsById.get("c")?.repos[0].own).toBe(true);
    expect(refsById.get("d")?.repos[0].own).toBe(true);
  });

  it("files a value only when it carries what the APIs observed", () => {
    const c = (type: string, observed: string) => ({ type, observed, action: "update" as const, current: "", evidence: [], key: "k", facts: {} });
    expect(checkedValue(c("release", "v1.2"), "v9.9.9 (GitHub release, 2027-01-01)")).toBeNull();
    expect(checkedValue(c("release", "v1.2"), "v1.2 (GitHub release, 2026-10-10)")).toBe("v1.2 (GitHub release, 2026-10-10)");
    expect(checkedValue(c("licence", "Apache-2.0"), "Apache License 2.0 for the code")).toBe("Apache License 2.0 for the code");
    expect(checkedValue(c("licence", "Apache-2.0"), "MIT")).toBeNull();
    expect(checkedValue(c("archived", "o/r archived"), "Code on GitHub.")).toBeNull();
    expect(checkedValue(c("moved", "new/place"), "The code moved to github.com/new/place.")).toBe("The code moved to github.com/new/place.");
    expect(checkedValue({ ...c("checkpoint", "a/B_500M"), action: "add" }, "a/B_900M")).toBe("a/B_500M");
  });
});

describe("failed reads are reported, not read as empty", () => {
  it("records a release list it could not read, and searches checkpoints under the canonical author", async () => {
    const gh = await githubFacts({ owner: "o", repo: "r" }, { fetchImpl: fixtureFetch({
      "https://api.github.com/repos/o/r": { json: { full_name: "o/r", html_url: "https://github.com/o/r" } },
      "https://api.github.com/repos/o/r/releases?per_page=10": { status: 403, json: { message: "rate limit" } },
    }) as unknown as typeof fetch });
    expect(gh).toMatchObject({ state: "ok", releases: [], releases_error: "HTTP 403" });
    const hf = await hfFacts({ type: "model", id: "ArcInstitute/evo2_7b" }, { fetchImpl: fixtureFetch({
      "https://huggingface.co/api/models/ArcInstitute/evo2_7b": { json: { id: "arcinstitute/evo2_7b" } },
      "https://huggingface.co/api/models?author=arcinstitute&search=evo2&sort=createdAt&direction=-1&limit=50": { json: [{ id: "arcinstitute/evo2_20b", createdAt: "2026-10-01T00:00:00Z" }] },
    }) as unknown as typeof fetch });
    expect(hf.siblings.map((s: { id: string }) => s.id)).toEqual(["arcinstitute/evo2_20b"]);
    expect(hf.siblings_error).toBeNull();
    const gated = await hfFacts({ type: "model", id: "a/b" }, { fetchImpl: fixtureFetch({ "https://huggingface.co/api/models/a/b": { status: 403, json: {} } }) as unknown as typeof fetch });
    expect(gated.state).toBe("gated");
  });

  it("says in the summary which repositories were not read", async () => {
    const http = JSON.parse(readFileSync(`${FIXTURES}/http.json`, "utf8"));
    http["https://api.github.com/repos/rewire-fixtures/helix/releases?per_page=10"] = { status: 429, json: { message: "slow down" } };
    delete http["https://api.github.com/repos/rewire-fixtures/quarry"];
    http["https://huggingface.co/api/models/rewire-fixtures/Dune_100M"] = { status: 403, json: {} };
    const r = await main(["--store-dir", `${FIXTURES}/entities`, "--report-only"], { GITHUB_REPOSITORY: "rewire-bio/rewire-benchmark-data" }, { fetch: fixtureFetch(http), github: { listIssues: async () => [] }, now: at("2026-12-01T05:00:00Z"), log: quiet });
    expect(r.summary).toContain("3 repositories or release lists not read");
    expect(r.summary).toContain("not read hf:model:rewire-fixtures/dune_100m repository (gated or rate-limited) (HTTP 403)");
    expect(r.summary).toContain("not read github:rewire-fixtures/helix release list (HTTP 429)");
    expect(r.summary).toContain("not read github:rewire-fixtures/quarry repository");
  });
});

describe("one issue per new checkpoint", () => {
  it("files a checkpoint found by two records once, naming both", () => {
    const facts = new Map([["hf:model:a/dune_100m", { state: "ok", siblings: [{ id: "a/Dune_500M", created_at: "2026-10-20T00:00:00Z" }] }]]);
    const ref = { host: "hf", type: "model", id: "a/Dune_100M", own: true, baseline: "2026-09-01T00:00:00Z", urls: [] };
    const family = { id: "dune", kind: "model", name: "Dune", attributes: { depth_tier: 1, entity_level: "family" } };
    const small = { id: "dune-100m", kind: "model", name: "Dune 100M", attributes: { depth_tier: 1, entity_level: "checkpoint" } };
    const confirmed = [small, family].map((record) => {
      const [c] = candidatesFor(record, { repos: [ref], pages: [] }, { facts }).candidates;
      return { record, changes: [{ ...c, value: c.observed, reason: "new size" }] };
    });
    expect(confirmed[0].changes[0].key).toBe(confirmed[1].changes[0].key);
    const plan = planIssues(confirmed, { issues: [], runDate: "2026-12-01" });
    expect(plan.file).toHaveLength(1);
    expect(plan.file[0].record.id).toBe("dune");
    expect(plan.file[0].issue.body).toContain("Also related to `dune-100m`");
    expect(parseUpdateMarker(plan.file[0].issue.body)).toMatchObject({ action: "add", names: ["a/Dune_500M"], related: ["dune-100m"] });
  });
});

describe("placeholder access values", () => {
  // The real record: its access is the catalogue placeholder "official_source_linked", and its
  // repository illumina/SpliceAI is archived. Run 44732264554 proposed the garbled value below.
  const record = JSON.parse(readFileSync(`${FIXTURES}/placeholder/discovery-model-spliceai.json`, "utf8"));
  const ref = { host: "github", owner: "illumina", repo: "SpliceAI", name: "SpliceAI", own: true, urls: ["https://github.com/illumina/SpliceAI"] };
  const facts = new Map([["github:illumina/spliceai", { state: "ok", archived: true, moved: null, licence: null, html_url: "https://github.com/Illumina/SpliceAI", pushed_at: "2023-01-01T00:00:00Z", releases: [] }]]);
  const sentence = "The GitHub repository illumina/SpliceAI was archived (read-only) by its owner.";

  it("reads a token as no access text, and keeps the change key", () => {
    expect(record.attributes.access).toBe("official_source_linked");
    expect(isPlaceholder("official_source_linked")).toBe(true);
    expect(isPlaceholder("Public code on GitHub.")).toBe(false);
    expect(isPlaceholder("tattabio/gLM2_650M")).toBe(false);
    const [c] = candidatesFor(record, { repos: [ref], pages: [] }, { facts }).candidates;
    expect(c).toMatchObject({ type: "archived", field: "access", current: "", placeholder: "official_source_linked", key: "discovery-model-spliceai:archived:illuminaspliceai" });
    const prompt = confirmPrompt(record, [c]);
    expect(prompt).not.toContain("official_source_linked");
    expect(prompt).toContain('"access":null');
  });

  it("never appends a proposal to the token", () => {
    const [c] = candidatesFor(record, { repos: [ref], pages: [] }, { facts }).candidates;
    expect(checkedValue(c, `official_source_linked. ${sentence}`)).toBe(sentence);
    expect(checkedValue(c, sentence)).toBe(sentence);
    const issue = renderUpdateIssue({ record, action: "update", changes: [{ ...c, value: checkedValue(c, `official_source_linked. ${sentence}`) ?? "", reason: "Own repository, archived." }], runDate: "2026-12-01" });
    expect(parseUpdateMarker(issue.body)?.fields).toEqual({ access: sentence });
    expect(issue.body).toContain("| access | not recorded (placeholder official_source_linked) |");
  });
});

describe("real records from run 44739151738", () => {
  // The records, their sources and the GitHub answers as recorded on 2026-11-20: mRNABench and
  // ViennaRNA RNAfold (sources pinned at the commits of tags v1.3.0 and v2.7.2), the 13 ViroBench
  // records that cite the ViroBench pipeline (moved to SII-AGI4S/ViroBench), and the 16
  // BenchBench-Cloning records whose repository is gone (404).
  const REAL = `${FIXTURES}/real`;
  const http = JSON.parse(readFileSync(`${REAL}/http.json`, "utf8"));
  const env = { ANTHROPIC_API_KEY: "test", GITHUB_REPOSITORY: "rewire-bio/rewire-benchmark-data", RUN_URL: "https://run/1" };

  // A confirmer that says yes to every proposal, with a value that carries what was observed: what
  // is filed is then decided by the data alone.
  function yesToAll() {
    const calls: { model: string; prompt: string }[] = [];
    const answer = (prompt: string) => {
      const changes = [...prompt.matchAll(/^(\d+)\. (\w+) \(field (\w+)\): observed ("[^"]*")/gm)].map(([, n, type, , observed]) => {
        const o = JSON.parse(observed);
        const value = type === "moved" ? `The code moved to github.com/${o}.` : type === "archived" ? "The GitHub repository was archived (read-only) by its owner." : `${o} (Git tag at the pinned commit)`;
        return { n: Number(n), real: true, value, reason: "Confirmed." };
      });
      return { changes };
    };
    const reply = (req: { model: string; messages: { content: string }[] }) => {
      calls.push({ model: req.model, prompt: req.messages[0].content });
      return { model: req.model, stop_reason: "end_turn", content: [{ type: "text", text: JSON.stringify(answer(req.messages[0].content)) }], usage: { input_tokens: 1000, output_tokens: 100 } };
    };
    return { calls, anthropic: { messages: { create: async (req: never) => reply(req) }, beta: { messages: { create: async (req: never) => reply(req) } } } };
  }
  const run = async () => {
    const m = yesToAll();
    const r = await main(["--store-dir", `${REAL}/entities`, "--report-only"], env, { anthropic: m.anthropic, github: { listIssues: async () => [] }, fetch: fixtureFetch(http), now: at("2026-12-01T05:00:00Z"), log: quiet });
    return { r, calls: m.calls };
  };

  it("reads the commit a source pins", () => {
    expect(pinnedCommit("https://github.com/morrislab/mRNABench/blob/74f96b8e6ae9f41cc3cccff089d826a62d5604b8/README.md")).toBe("74f96b8e6ae9f41cc3cccff089d826a62d5604b8");
    expect(pinnedCommit("https://github.com/o/r", "Git commit 1ffec79f5e258896160f7362ced8263450f371dc")).toBe("1ffec79f5e258896160f7362ced8263450f371dc");
    expect(pinnedCommit("https://github.com/QIANJINYDX/ViroBench", "arXiv 2605.25388v1")).toBeNull();
  });

  it("proposes the tag at the pinned commit for mRNABench, and only notes the newer release", async () => {
    const { r } = await run();
    const files = r.plan.file.map((p: { record: { id: string } }) => p.record.id);
    expect(files).toEqual(["discovery-benchmark-mrnabench"]);
    const issue = r.plan.file[0].issue;
    expect(parseUpdateMarker(issue.body)).toMatchObject({ record_id: "discovery-benchmark-mrnabench", fields: { version: "v1.3.0 (Git tag at the pinned commit)" }, evidence: ["https://github.com/morrislab/mRNABench/releases/tag/v1.3.0"] });
    expect(issue.body).not.toContain("v1.3.2 (Git");
    expect(issue.body).toContain("pinned commit: 74f96b8e6ae9f41cc3cccff089d826a62d5604b8");
    const look = r.look.find((l: { records: string[] }) => l.records.includes("discovery-benchmark-mrnabench"));
    expect(look.detail).toContain("a newer release exists: v1.3.2 (2026-10-19), v1.3.1 (2026-10-19)");
    expect(look.detail).toContain("(tag v1.3.0)");
  });

  it("does not propose a release of the shared ViennaRNA package as the RNAfold version", async () => {
    const { r } = await run();
    expect(JSON.stringify(r.plan.file)).not.toContain("viennarna");
    const look = r.look.find((l: { records: string[] }) => l.records.includes("discovery-model-viennarna-rnafold"));
    expect(look.detail).toContain("not named exactly for this entity");
    expect(look.detail).toContain("v2.8.0");
  });

  it("never files a change on a repository the data does not tie to the record, and asks no model about it", async () => {
    const { r, calls } = await run();
    for (const id of ["virocaduceus", "virodnabert2", "virohyena"]) expect(JSON.stringify(r.plan.file)).not.toContain(id);
    expect(calls.filter((c) => c.model.startsWith("claude-haiku"))).toEqual([]);
    expect(calls.map((c) => /Record (\S+)/.exec(c.prompt)?.[1])).toEqual(["discovery-benchmark-mrnabench"]);
    // Two runs give the same plan and the same summary lines.
    const again = await run();
    expect(again.r.plan.file.map((p: { issue: { body: string } }) => p.issue.body)).toEqual(r.plan.file.map((p: { issue: { body: string } }) => p.issue.body));
    expect(again.r.look).toEqual(r.look);
  });

  it("reports the ViroBench move once, in the sweep issue, and the BenchBench-Cloning 404 once", async () => {
    const { r } = await run();
    const body: string = r.deadIssue.body;
    const visible = body.split("\n").filter((l) => !l.startsWith("<!--"));
    expect(visible.filter((l) => l.includes("ViroBench"))).toEqual(["- `lit-microbial-20261011-virobench-benchmark-virobench` (ViroBench): QIANJINYDX/ViroBench now SII-AGI4S/ViroBench"]);
    expect(visible.filter((l) => l.includes("benchbench-cloning"))).toHaveLength(1);
    expect(r.deadIssue.title).toBe("Entity sweep 2026-12: 1 dead link and 1 repository change");
    // The missing repository keeps its marker, so it is not listed on its own next month.
    expect(body).toContain("<!-- entity-sweep-dead: benchbench-cloning-20261106-benchmark-suite:missing:benchling/benchbench-cloning -->");
    // The records that only cite these repositories add no line of their own.
    expect(r.look.filter((l: { type: string }) => l.type !== "version")).toEqual([]);
  });

  it("writes the facts whole, not cut mid-value", () => {
    const releases = Array.from({ length: 5 }, (_, n) => ({ tag: `v1.${n}.0`, published_at: "2026-10-19T07:16:17Z", url: `https://github.com/morrislab/mRNABench/releases/tag/v1.${n}.0` }));
    const text = factsText({ repository: "morrislab/mRNABench", baseline: "2026-09-16T10:30:21.823561+00:00", recorded_version: "none", releases_since_baseline: releases });
    expect(text).toBe("repository: morrislab/mRNABench; baseline: 2026-09-16T10:30:21.823561+00:00; recorded version: none; releases since baseline: v1.0.0 (2026-10-19), v1.1.0 (2026-10-19), v1.2.0 (2026-10-19), v1.3.0 (2026-10-19), v1.4.0 (2026-10-19)");
  });
});
