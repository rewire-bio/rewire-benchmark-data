import { mkdtempSync, readFileSync, readdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import {
  LABEL, LIMITS, SWEEP_LABEL, checkLink, checkpointBase, fixtureFetch, hfIdsInText, licenceAgrees, main, parseUpdateMarker, planIssues, renderUpdateIssue, tiersDue,
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

  it("drops what Sonnet does not confirm, what an earlier issue filed, and repositories Haiku says are not the entity's own", async () => {
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
    // A 404 already listed in an open sweep issue is not listed again.
    expect(r.deadIssue.body).not.toContain("lab.example.org");
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
      if (prompt.startsWith("Ownership check")) return answers.ownership.all;
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

  it("uses Haiku with thinking off to classify and Sonnet with the fallback to confirm, then files the issues", async () => {
    const f = fakes();
    const r = await main(args, env, f.deps);
    const haiku = f.calls.filter((c) => c.model === "claude-haiku-5-5");
    const sonnet = f.calls.filter((c) => c.model === "claude-sonnet-5-5");
    expect(haiku).toHaveLength(2); // one ownership call, one changed page
    for (const c of haiku) expect(c.thinking).toEqual({ type: "disabled" });
    expect(sonnet.map((c) => /Record (\S+)/.exec(c.prompt)?.[1]).sort()).toEqual(["fixture-benchmark-arena", "fixture-model-dune", "fixture-model-helix", "fixture-model-quarry"]);
    for (const c of sonnet) expect(c.fallbacks).toBe("default");
    expect(f.created.map((i) => i.labels)).toEqual([[LABEL, "tier-1"], [LABEL, "tier-1"], [LABEL, "tier-1"], [SWEEP_LABEL]]);
    expect(r.filed.size).toBe(4);
    expect(r.usage.total()).toBeGreaterThan(0);
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
