import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { BOT_LOGIN, buildTable, main, mechanicalProblems, overallVerdict, reviewInput } from "../scripts/agents/reviewer.mjs";

// The reviewer agent (#256). Everything here runs without an API key or network. The fixture
// batch is the first intake pull request for #250 (#296), whose review must find that
// hEVO-large-o cites the hEVO-base-o card and that the -o models are checkpoints.
const FIXTURES = "tests/agents-reviewer-fixtures";
const now = () => new Date("2026-11-19T12:00:00Z");
const quiet = () => {};
const batch = readFileSync(`${FIXTURES}/batch.jsonl`, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const fixtureReview = JSON.parse(readFileSync(`${FIXTURES}/review.json`, "utf8"));
const pull = JSON.parse(readFileSync(`${FIXTURES}/pull.json`, "utf8"));
const empty = { storeNames: new Map<string, string>(), storeSourceIds: new Set<string>() };
const model = batch.find((r) => r.id.endsWith("model-hevo-base"));

describe("mechanical checks", () => {
  it("passes the fixture batch", () => {
    expect(mechanicalProblems(batch, empty)).toEqual([]);
  });

  it("finds a wrong depth tier, a bad entity_level, a store duplicate, a missing source and a non-entity kind", () => {
    const bad = [
      { ...model, id: "m1", attributes: { ...model.attributes, depth_tier: 3, entity_level: "suite" } },
      { ...model, id: "m2", name: "ESM-2", source_ids: ["nowhere"] },
      { id: "c1", kind: "claim", name: "c", facets: {}, source_ids: ["s"], links: [], attributes: {} },
    ];
    const problems = mechanicalProblems(bad, { storeNames: new Map([["esm 2", "discovery-model-esm-2"]]), storeSourceIds: new Set(["s", ...model.source_ids]) });
    expect(problems.map((p: { id: string; field: string }) => `${p.id} ${p.field}`)).toEqual([
      "m1 depth_tier", "m1 entity_level", "m2 name", "m2 source_ids", "c1 kind",
    ]);
  });
});

describe("verdicts", () => {
  it("marks a field the model did not judge unverifiable, so it cannot approve", () => {
    const rows = buildTable([model], { records: [{ id: model.id, fields: [{ field: "name", verdict: "pass", problem: "", evidence: "README" }] }] }, []);
    expect(rows.find((r: { field: string }) => r.field === "description")!.verdict).toBe("unverifiable");
    expect(rows.find((r: { field: string }) => r.field === "depth_tier")!.verdict).toBe("pass");
    expect(overallVerdict(rows)).toBe("request changes");
  });

  it("lets a mechanical problem fail a field the model passed", () => {
    const fields = ["name", "description", "areas", "entity_level", "version", "access", "training_data", "source_ids"].map((field) => ({ field, verdict: "pass", problem: "", evidence: "x" }));
    const rows = buildTable([model], { records: [{ id: model.id, fields }] }, [{ id: model.id, field: "entity_level", text: "entity_level x is not allowed" }]);
    expect(rows.find((r: { field: string }) => r.field === "entity_level")!.verdict).toBe("fail");
  });

  it("shows the reviewer each record's fields and the URL of every cited source", () => {
    const input = reviewInput(batch);
    const largeO = input.find((r: { id: string }) => r.id.endsWith("hevo-large-o"));
    expect(largeO.entity_level).toBe("family");
    expect(largeO.sources.map((s: { url: string }) => s.url)).toContain("https://huggingface.co/MulinLab/hEVO-base-o");
  });
});

describe("dry run on the #296 batch", () => {
  it("requests changes for exactly the two known problems", async () => {
    const r = await main(["--dry-run"], {}, { now, log: quiet });
    expect(r.verdict).toBe("request changes");
    const fails = r.rows.filter((x: { verdict: string }) => x.verdict !== "pass").map((x: { id: string; field: string }) => `${x.id.replace("intake-250-20261119-", "")} ${x.field}`);
    expect(fails).toEqual(["model-hevo-base-o entity_level", "model-hevo-large-o entity_level", "model-hevo-large-o source_ids"]);
    expect(r.body).toContain("| Field | Value | Source | Verdict | Evidence or problem |");
    expect(r.body).toContain("comment-only");
    expect(r.body).not.toMatch(/[–—]/);
  });
});

describe("posting, with fakes", () => {
  const allPass = {
    records: batch.filter((r) => r.kind !== "source").map((r) => ({
      id: r.id,
      fields: ["name", "description", "areas", "entity_level", "version", "access", "licence", "training_data", "task", "scope_note", "species", "repository", "limitations", "source_ids"]
        .map((field) => ({ field, verdict: "pass", problem: "", evidence: "README" })),
    })),
    unopened: [],
  };

  function fakes({ review = fixtureReview, checks = [{ name: "checks (store)", status: "completed", conclusion: "success" }], author = BOT_LOGIN } = {}) {
    const posted: { event: string; body: string; by: string }[] = [];
    const commands: string[] = [];
    const calls: string[] = [];
    const client = (by: string) => ({
      getPull: async () => ({ ...pull, author }),
      files: async () => pull.files,
      checkRuns: async () => checks,
      review: async (_repo: string, _n: number, r: { event: string; body: string }) => {
        if (by === "bot" && r.event !== "COMMENT") {
          const e = new Error("422 Can not request changes on your own pull request") as Error & { status: number };
          e.status = 422;
          throw e;
        }
        posted.push({ event: r.event, body: r.body, by });
      },
      comment: async () => {},
    });
    const anthropic = {
      beta: { messages: { stream: (req: { model: string }) => ({ finalMessage: async () => {
        calls.push(`review ${req.model}`);
        return { model: req.model, stop_reason: "end_turn", content: [{ type: "text", text: "notes" }], usage: { input_tokens: 2000, output_tokens: 500 } };
      } }) } },
      messages: { create: async (req: { model: string }) => {
        calls.push(`structure ${req.model}`);
        return { stop_reason: "end_turn", content: [{ type: "text", text: JSON.stringify(review) }], usage: { input_tokens: 500, output_tokens: 500 } };
      } },
    };
    const fetches = JSON.parse(readFileSync(`${FIXTURES}/fetches.json`, "utf8"));
    const fetchImpl = async (url: string) => new Response(`bytes ${url}`, { status: fetches[url] ? 200 : 404, headers: { "content-type": "text/html" } });
    const run = (cmd: string, args: string[]) => {
      commands.push([cmd, ...args].join(" "));
      return { ok: true, output: "" };
    };
    return { posted, commands, calls, deps: { github: client("bot"), approver: client("approver"), anthropic, fetch: fetchImpl, run, now, log: quiet, sleep: async () => {} } };
  }
  const env = { ANTHROPIC_API_KEY: "k", GITHUB_REPOSITORY: "rewire-bio/rewire-benchmark-data" };
  const args = (mode: string) => ["--pr", "296", "--mode", mode];

  it("uses Sonnet to review and Haiku only to structure, and posts a comment review in comment mode", async () => {
    const f = fakes();
    const root = await rootWithBatch();
    const r = await main(["--pr", "296", "--mode", "comment", "--root", root], env, f.deps);
    expect(f.calls).toEqual(["review claude-sonnet-5-5", "structure claude-haiku-5-5"]);
    expect(r.outcome).toBe("commented: request changes");
    expect(f.posted.map((p) => p.event)).toEqual(["COMMENT"]);
    expect(f.commands).toEqual([]);
  });

  async function rootWithBatch() {
    const fs = await import("node:fs");
    const os = await import("node:os");
    const dir = fs.mkdtempSync(`${os.tmpdir()}/reviewer-`);
    fs.mkdirSync(`${dir}/data/omics/intake-250-20261119`, { recursive: true });
    fs.copyFileSync(`${FIXTURES}/batch.jsonl`, `${dir}/data/omics/intake-250-20261119/batch.jsonl`);
    fs.mkdirSync(`${dir}/data/entities`, { recursive: true });
    return dir;
  }

  it("in approve mode, approves with the approver token and enables auto-merge when every field and check passes", async () => {
    const f = fakes({ review: allPass });
    const r = await main(["--pr", "296", "--mode", "approve", "--root", await rootWithBatch()], { ...env, APPROVER_TOKEN: "t" }, f.deps);
    expect(r.verdict).toBe("approve");
    expect(f.posted).toEqual([expect.objectContaining({ event: "APPROVE", by: "approver" })]);
    expect(f.commands).toEqual(["gh pr merge 296 --auto --merge --repo rewire-bio/rewire-benchmark-data"]);
    expect(r.outcome).toBe("approved; auto-merge enabled");
  });

  it("in approve mode, does not approve when CI failed", async () => {
    const f = fakes({ review: allPass, checks: [{ name: "checks (tests-1)", status: "completed", conclusion: "failure" }] });
    const r = await main(["--pr", "296", "--mode", "approve", "--root", await rootWithBatch()], { ...env, APPROVER_TOKEN: "t" }, f.deps);
    expect(r.outcome).toBe("not approved: CI red");
    expect(f.posted).toEqual([expect.objectContaining({ event: "REQUEST_CHANGES", by: "approver" })]);
    // The headline says why it is not an approval, so it never contradicts the review event.
    expect(f.posted[0].body.split("\n")[0]).toMatch(/^\*\*Reviewer agent verdict: not approved. CI is red \(checks \(tests-1\): failure\).\*\* All \d+ fields pass.$/);
    expect(f.commands).toEqual([]);
  });

  it("in approve mode, requests changes when a field fails, and never merges", async () => {
    const f = fakes();
    const r = await main(["--pr", "296", "--mode", "approve", "--root", await rootWithBatch()], { ...env, APPROVER_TOKEN: "t" }, f.deps);
    expect(r.outcome).toBe("requested changes");
    expect(f.posted).toEqual([expect.objectContaining({ event: "REQUEST_CHANGES", by: "approver" })]);
    expect(f.commands).toEqual([]);
  });

  it("does not approve without an approver token", async () => {
    const f = fakes({ review: allPass });
    const r = await main(["--pr", "296", "--mode", "approve", "--root", await rootWithBatch()], env, f.deps);
    expect(r.outcome).toBe("not approved: no approver token");
    expect(f.posted.map((p) => p.event)).toEqual(["COMMENT"]);
  });

  it("skips pull requests the bot did not open", async () => {
    const f = fakes({ author: "someone" });
    const r = await main(args("comment"), env, f.deps);
    expect(r.outcome).toContain("not rewire-bot[bot]");
    expect(f.calls).toEqual([]);
  });
});
