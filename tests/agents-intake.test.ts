import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import {
  KIND_FIELDS, SOURCE_FIELDS, buildBatch, doiOf, fetchSource, fetchableUrl, htmlTitle, isChallengePage, main, publicationStatusOf, renderSkipComment,
  screenEntities, urlsInText, verifiedValue, versionOf, withSourceUrls,
} from "../scripts/agents/intake.mjs";
import { Usage } from "../scripts/agents/discovery.mjs";
import { intakeProblems } from "../scripts/agents/intake-check";

// The intake agent (#255). Everything here runs without an API key, network or the record store:
// the dry run reads the issue, proposal, verification and fetched sources from
// tests/agents-intake-fixtures and its store names from the fixture entities. The workflow's pull
// request dry run is what runs records -- add on the real store.
const FIXTURES = "tests/agents-intake-fixtures";
const now = () => new Date("2026-11-19T09:00:00Z");
const quiet = () => {};
const roots: string[] = [];
const tempRoot = () => {
  const root = mkdtempSync(join(tmpdir(), "intake-"));
  roots.push(root);
  return root;
};
afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
});

const dryRun = (root: string) =>
  main(["--dry-run", "--store-dir", `${FIXTURES}/entities`, "--root", root, "--no-store-checks"], {}, { now, log: quiet });

/** Attribute names declared per kind in shared/omics/attribute-registry.ts. */
function declared(kind: string): string[] {
  const text = readFileSync("shared/omics/attribute-registry.ts", "utf8");
  const block = new RegExp(`\\n  ${kind}: \\{([^}]*)\\}`).exec(text)?.[1] ?? "";
  return [...block.matchAll(/^\s+([a-z0-9_]+):/gm)].map((m) => m[1]);
}

describe("record shapes", () => {
  it("only writes attributes the registry declares for each kind", () => {
    const fixed = ["source_locator", "review", "missing_metadata"];
    for (const [kind, spec] of Object.entries(KIND_FIELDS)) {
      const fields = [...spec.text, ...fixed, ...(spec.tier ? ["depth_tier"] : []), ...(spec.provenance ? ["provenance_note"] : []),
        ...(spec.limitations ? ["limitations"] : []), ...(spec.repository ? ["repository"] : [])];
      expect(fields.filter((f) => !declared(kind).includes(f)), kind).toEqual([]);
    }
    expect(SOURCE_FIELDS.filter((f) => !declared("source").includes(f))).toEqual([]);
  });

  it("gives a depth tier to exactly the kinds that declare one", () => {
    for (const [kind, spec] of Object.entries(KIND_FIELDS)) expect(spec.tier, kind).toBe(declared(kind).includes("depth_tier"));
  });
});

describe("dry run", () => {
  it("adds the verified entities and their sources, and drops duplicates and unopenable sources", async () => {
    const root = tempRoot();
    const result = await dryRun(root);
    expect(result.outcome).toBe("ready: pull request not opened in this mode");
    expect(result.entities.map((e: { id: string }) => e.id)).toEqual([
      "intake-9999-20261119-model-helixgram-fixture",
      "intake-9999-20261119-dataset-helixgram-fixture-pretraining-corpus",
    ]);
    expect(result.dropped.map((d: { name: string; reason: string }) => `${d.name}: ${d.reason}`)).toEqual([
      'ESM-2: already in the store as discovery-model-esm-2 ("esm 2")',
      "Helixgram fixture splice benchmark: no primary source could be opened: https://example.org/helixgram-fixture/splice-benchmark (HTTP 403)",
    ]);
    const written = readFileSync(join(root, result.batchDir, "batch.jsonl"), "utf8").trim().split("\n").map((l) => JSON.parse(l));
    expect(written.map((r) => r.kind).sort()).toEqual(["dataset", "model", "source", "source"]);
    expect(intakeProblems(written)).toEqual([]);
  });

  it("keeps only confirmed fields and records the rest as missing", async () => {
    const result = await dryRun(tempRoot());
    const model = result.records.find((r: { kind: string }) => r.kind === "model");
    expect(model.attributes.access).toBe("Weights and code on GitHub"); // corrected by the verifier
    expect(model.attributes.licence).toBeUndefined(); // unsupported
    expect(model.attributes.missing_metadata).toEqual({ licence: { reason: "unextracted", note: expect.stringContaining("Not confirmed") } });
    expect(model.attributes.depth_tier).toBe(1);
    expect(model.status).toBe("discovered");
    expect(model.links).toEqual([]);
    const dataset = result.records.find((r: { kind: string }) => r.kind === "dataset");
    expect(dataset.attributes.depth_tier).toBeUndefined();
    expect(dataset.attributes.version).toBeUndefined();
  });

  it("dates every review with reviewed_at only", async () => {
    const result = await dryRun(tempRoot());
    for (const r of result.records.filter((r: { kind: string }) => r.kind !== "source")) {
      expect(r.attributes.review.reviewed_at).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/);
      expect(r.attributes.review).not.toHaveProperty("date");
    }
  });

  it("hashes sources with the script, gives them the citing entities' facets and no licence", async () => {
    const result = await dryRun(tempRoot());
    const sources = result.records.filter((r: { kind: string }) => r.kind === "source");
    expect(sources).toHaveLength(2);
    for (const s of sources) {
      expect(s.attributes.artifact_sha256).toMatch(/^[0-9a-f]{64}$/);
      expect(s.attributes.retrieved_at).toMatch(/Z$/);
      expect(s.attributes.version).toBeTruthy();
      expect(s.attributes).not.toHaveProperty("licence");
      expect(s.facets.areas).toEqual(["dna-genomes"]);
    }
  });
});

describe("screening and verification", () => {
  const storeNames = new Map([["esm 2", "discovery-model-esm-2"]]);
  const entity = (extra: Record<string, unknown>) => ({ kind: "model", name: "New model", aliases: [], areas: ["dna-genomes"], source_urls: [], ...extra });

  it("drops an entity with no area, an unknown kind, a store alias or a repeat", () => {
    const { keep, dropped } = screenEntities({ entities: [
      entity({ areas: [] }), entity({ kind: "evaluation", name: "E" }), entity({ name: "Other", aliases: ["ESM-2"] }), entity({}), entity({}),
    ] }, { storeNames });
    expect(keep).toHaveLength(1);
    expect(dropped.map((d: { reason: string }) => d.reason)).toEqual([
      "no biology area from the vocabulary, so the depth tier cannot be set",
      "not a model, method, benchmark or dataset (evaluation)",
      'already in the store as discovery-model-esm-2 ("esm 2")',
      "proposed twice in this issue",
    ]);
  });

  it("stores a supported value, a corrected value, and nothing else", () => {
    const verdict = { fields: [
      { field: "version", verdict: "supported", value: "", locator: "p1" },
      { field: "access", verdict: "corrected", value: "Open", locator: "p2" },
      { field: "licence", verdict: "unsupported", value: "MIT", locator: "" },
    ] };
    expect(verifiedValue(verdict, "version", "v2")).toEqual({ value: "v2", locator: "p1" });
    expect(verifiedValue(verdict, "access", "Closed")).toEqual({ value: "Open", locator: "p2" });
    expect(verifiedValue(verdict, "licence", "MIT")).toBeNull();
    expect(verifiedValue(verdict, "training_data", "x")).toBeNull();
    expect(verifiedValue(verdict, "version", "")).toBeNull();
  });

  it("drops an entity whose description the verifier did not confirm", () => {
    const sources = new Map([["https://example.org/a", { id: "s1" }]]);
    const built = buildBatch({
      entities: [entity({ description: "Does things.", source_urls: ["https://example.org/a"] })],
      verification: { entities: [{ name: "New model", keep: true, reason: "", fields: [{ field: "description", verdict: "unsupported", value: "", locator: "" }] }] },
      sources, batch: "b", issue: 1, runDate: "2026-11-19", reviewedAt: "2026-11-19T00:00:00Z", reviewModel: "claude-sonnet-5-5", runUrl: "",
    });
    expect(built.records).toEqual([]);
    expect(built.dropped[0].reason).toBe("verification did not confirm the description");
  });

  it("reuses a stored source instead of adding a second record for the same URL", () => {
    const sources = new Map([["https://example.org/a", { id: "existing-source" }]]);
    const built = buildBatch({
      entities: [entity({ description: "Does things.", source_urls: ["https://example.org/a"] })],
      verification: { entities: [{ name: "New model", keep: true, reason: "", fields: [{ field: "description", verdict: "supported", value: "", locator: "Abstract" }, { field: "areas", verdict: "supported", value: "", locator: "Abstract" }] }] },
      sources, batch: "b", issue: 1, runDate: "2026-11-19", reviewedAt: "2026-11-19T00:00:00Z", reviewModel: "claude-opus-5-5", runUrl: "",
    });
    expect(built.records.map((r: { kind: string }) => r.kind)).toEqual(["model"]);
    expect(built.records[0].source_ids).toEqual(["existing-source"]);
    expect(built.records[0].attributes.review.reviewer).toEqual(["claude"]); // a fallback model is not claude-sonnet
  });

  it("drops an entity whose areas the verifier did not confirm, because they set the depth tier", () => {
    const sources = new Map([["https://example.org/a", { id: "s1" }]]);
    const built = buildBatch({
      entities: [entity({ description: "Does things.", source_urls: ["https://example.org/a"] })],
      verification: { entities: [{ name: "New model", keep: true, reason: "", fields: [{ field: "description", verdict: "supported", value: "", locator: "Abstract" }] }] },
      sources, batch: "b", issue: 1, runDate: "2026-11-19", reviewedAt: "2026-11-19T00:00:00Z", reviewModel: "claude-sonnet-5-5", runUrl: "",
    });
    expect(built.records).toEqual([]);
    expect(built.dropped[0].reason).toContain("did not confirm an area");
  });

  it("matches verdicts to entities by the script's key, even when the verifier respells the name", async () => {
    const result = await dryRun(tempRoot());
    // The fixture verifier calls the corpus "Helixgram Fixture Pre-training Corpus".
    expect(result.entities.map((e: { name: string }) => e.name)).toContain("Helixgram fixture pretraining corpus");
  });

  it("takes source names, versions and publication status from the URL and the bytes, not the model", () => {
    expect(versionOf("https://arxiv.org/abs/2611.01234v2", "2026-11-19")).toBe("arXiv 2611.01234v2");
    expect(versionOf("https://www.biorxiv.org/content/10.1101/2026.01.15.599999v3.full", "2026-11-19")).toBe("10.1101/2026.01.15.599999 version 3");
    expect(versionOf(`https://github.com/a/b/tree/${"a".repeat(40)}`, "2026-11-19")).toBe(`Commit ${"a".repeat(40)}`);
    expect(versionOf("https://example.org/page", "2026-11-19")).toBe("As served on 2026-11-19; the page may change");
    expect(publicationStatusOf("https://www.biorxiv.org/content/x")).toBe("preprint");
    expect(publicationStatusOf("https://huggingface.co/org/model")).toBe("official_project_source");
    expect(publicationStatusOf("https://doi.org/10.1/x")).toBe("");
    expect(htmlTitle("<html><head><title>\n A &amp; B \u2014 page </title>")).toBe("A & B, page");
  });

  it("falls back to the proposal's sources, then to the issue's URLs, when the draft cites none for an entity", () => {
    const body = "README: https://github.com/a/b/blob/abc/README.md. Card: https://huggingface.co/A/m (gated). Post https://www.linkedin.com/posts/x and #1 https://github.com/a/b/issues/3";
    expect(urlsInText(body)).toEqual(["https://github.com/a/b/blob/abc/README.md", "https://huggingface.co/A/m"]);
    const [own, listed] = withSourceUrls([entity({ source_urls: ["https://example.org/own"] }), entity({ source_urls: [] })], { sources: [{ url: "https://example.org/listed" }] }, body);
    expect(own.source_urls).toEqual(["https://example.org/own"]);
    expect(listed.source_urls).toEqual(["https://example.org/listed"]);
    expect(withSourceUrls([entity({ source_urls: [] })], { sources: [] }, body)[0].source_urls).toEqual(urlsInText(body));
  });

  it("resolves short source references to the full URLs that contain them", () => {
    const body = "README https://github.com/mulinlab/hEVO/blob/eac1314/README.md and https://pmc.ncbi.nlm.nih.gov/articles/PMC13738607/ and https://huggingface.co/MulinLab/hEVO-base-o";
    const proposal = { sources: [{ url: "github.com/mulinlab/hEVO" }, { url: "PMC13738607" }] };
    const [a, b] = withSourceUrls([entity({ source_urls: ["MulinLab/hEVO-base-o"] }), entity({ source_urls: ["PMC13738607"] })], proposal, body);
    expect(a.source_urls).toEqual(["https://huggingface.co/MulinLab/hEVO-base-o"]);
    expect(b.source_urls).toEqual(["https://pmc.ncbi.nlm.nih.gov/articles/PMC13738607/"]);
  });

  it("refuses a bot check page served with HTTP 200", async () => {
    expect(isChallengePage("Checking your browser - reCAPTCHA", "")).toBe(true);
    expect(isChallengePage("hEVO: a DNA model", "<p>Results</p>")).toBe(false);
    expect(isChallengePage("Model card", "<p>Without approval the download returns access denied.</p><div class=g-recaptcha></div>")).toBe(false);
    const fetchImpl = (async () => new Response("<html><title>Just a moment...</title></html>", { status: 200, headers: { "content-type": "text/html" } })) as unknown as typeof fetch;
    expect((await fetchSource("https://pmc.ncbi.nlm.nih.gov/articles/PMC1/", { fetchImpl })).error).toContain("bot check page");
  });

  it("fetches only public http(s) URLs and reads bare DOIs", () => {
    expect(fetchableUrl("https://www.biorxiv.org/content/10.1101/2026.01.01.1v1")).toBe(true);
    for (const bad of ["file:///etc/passwd", "http://localhost:8080/", "http://169.254.169.254/latest", "https://user:pw@example.org/", "http://[::1]/", "https://intranet/"])
      expect(fetchableUrl(bad), bad).toBe(false);
    expect(doiOf("https://doi.org/10.64898/2026.09.24.753155")).toBe("10.64898/2026.09.24.753155");
    expect(doiOf("https://example.org/page")).toBe("");
  });

  it("explains a skip on the issue in plain words", () => {
    const text = renderSkipComment({ kind: "sources", detail: "https://x.org: HTTP 403", usage: new Usage(), runUrl: "https://run" });
    expect(text).toContain("no primary source could be opened");
    expect(text).toContain("remove and re-add the `entity-request` label");
    expect(text).not.toMatch(/[–—]/);
  });
});

describe("live run with fakes", () => {
  const fixture = (name: string) => JSON.parse(readFileSync(`${FIXTURES}/${name}`, "utf8"));

  function fakes({ pulls = [] as unknown[] } = {}) {
    const calls: string[] = [];
    const comments: string[] = [];
    const created: Record<string, unknown>[] = [];
    const structured = [fixture("proposal.json"), fixture("verification.json")];
    const anthropic = {
      beta: { messages: { stream: (req: { model: string }) => ({ finalMessage: async () => {
        calls.push(`research ${req.model}`);
        return { model: req.model, stop_reason: "end_turn", content: [{ type: "text", text: "notes" }], usage: { input_tokens: 1000, output_tokens: 100 } };
      } }) } },
      messages: { create: async (req: { model: string }) => {
        calls.push(`structure ${req.model}`);
        return { stop_reason: "end_turn", content: [{ type: "text", text: JSON.stringify(structured.shift()) }], usage: { input_tokens: 500, output_tokens: 200 } };
      } },
    };
    const github = {
      getIssue: async () => fixture("issue.json"),
      pullsFor: async () => pulls,
      createPull: async (_repo: string, pull: Record<string, unknown>) => {
        created.push(pull);
        return { html_url: "https://github.com/rewire-bio/rewire-benchmark-data/pull/1" };
      },
      comment: async (_repo: string, _n: number, body: string) => {
        comments.push(body);
      },
    };
    const fetches = fixture("fetches.json");
    const fetchImpl = async (url: string) =>
      fetches[url]?.error ? new Response("no", { status: 403 }) : new Response(`bytes of ${url}`, { status: 200, headers: { "content-type": "text/html; charset=utf-8" } });
    const commands: string[] = [];
    const run = (cmd: string, args: string[]) => {
      commands.push([cmd, ...args].join(" "));
      return { ok: true, output: "ok" };
    };
    return { calls, comments, created, commands, deps: { anthropic, github, fetch: fetchImpl, run, now, log: quiet } };
  }

  const env = { ANTHROPIC_API_KEY: "test", GITHUB_REPOSITORY: "rewire-bio/rewire-benchmark-data", GITHUB_RUN_ID: "42" };

  it("uses Haiku to draft and structure and Sonnet only to verify, then checks, pushes, opens the pull request and comments", async () => {
    const f = fakes();
    const result = await main(["--issue", "9999", "--store-dir", `${FIXTURES}/entities`, "--root", tempRoot()], env, f.deps);
    expect(f.calls).toEqual(["research claude-haiku-5-5", "structure claude-haiku-5-5", "research claude-sonnet-5-5", "structure claude-haiku-5-5"]);
    expect(f.commands.map((c) => c.split(" ").slice(0, 6).join(" "))).toEqual([
      "npx tsx scripts/agents/intake-check.ts data/omics/intake-9999-20261119/batch.jsonl",
      "npm run -s records -- add",
      "npm run -s records -- check",
      "git checkout -B intake/issue-9999",
      "git add -- data/omics/intake-9999-20261119 data/entities data/provenance",
      expect.stringMatching(/^git commit -m Add Helixgram fixture/),
      "git push --force origin HEAD:refs/heads/intake/issue-9999",
    ].map((c) => (typeof c === "string" ? c.split(" ").slice(0, 6).join(" ") : c)));
    expect(f.created[0]).toMatchObject({ head: "intake/issue-9999", base: "main" });
    // The fixture issue is tier 1, whose evaluations wait for #274, so the pull request does not close it.
    expect(String(f.created[0].body)).toContain("Refs #9999");
    expect(String(f.created[0].body)).not.toContain("Closes #9999");
    expect(String(f.created[0].body)).toContain("actions/runs/42");
    expect(f.comments).toHaveLength(1);
    expect(f.comments[0]).toContain("pull/1");
    expect(result.outcome).toBe("opened");
    expect(result.usage.total()).toBeGreaterThan(0);
  });

  it("opens nothing and comments the failure when a store check fails", async () => {
    const f = fakes();
    f.deps.run = (cmd: string, args: string[]) => {
      f.commands.push([cmd, ...args].join(" "));
      return args.includes("add") ? { ok: false, output: "Batch cannot replace or duplicate record: x" } : { ok: true, output: "" };
    };
    const result = await main(["--issue", "9999", "--store-dir", `${FIXTURES}/entities`, "--root", tempRoot()], env, f.deps);
    expect(result.outcome).toBe("failed: records add");
    expect(f.created).toEqual([]);
    expect(f.commands.some((c) => c.startsWith("git"))).toBe(false);
    expect(f.comments[0]).toContain("Batch cannot replace or duplicate record");
  });

  it("comments on the issue when the run throws", async () => {
    const f = fakes();
    f.deps.github.createPull = async () => {
      throw new Error("POST /pulls: 422 Validation Failed");
    };
    await expect(main(["--issue", "9999", "--store-dir", `${FIXTURES}/entities`, "--root", tempRoot()], env, f.deps)).rejects.toThrow("422");
    expect(f.comments[0]).toContain("422 Validation Failed");
  });

  it("skips with a comment when a pull request for the issue already exists, before any model call", async () => {
    const f = fakes({ pulls: [{ state: "open", html_url: "https://github.com/x/y/pull/7" }] });
    const result = await main(["--issue", "9999"], env, f.deps);
    expect(result.outcome).toContain("existing pull request");
    expect(f.calls).toEqual([]);
    expect(f.comments[0]).toContain("already exists");
  });

  it("writes nothing to GitHub in report-only mode", async () => {
    const f = fakes();
    const result = await main(["--issue", "9999", "--report-only", "--store-dir", `${FIXTURES}/entities`, "--root", tempRoot()], env, f.deps);
    expect(result.outcome).toBe("ready: pull request not opened in this mode");
    expect(f.created).toEqual([]);
    expect(f.comments).toEqual([]);
    expect(f.commands.some((c) => c.startsWith("git"))).toBe(false);
    expect(result.pull.title).toContain("Helixgram fixture");
  });

  it("passes without a key and does nothing", async () => {
    const result = await main(["--issue", "1"], {}, { now, log: quiet });
    expect(result.outcome).toBe("no key");
  });
});
