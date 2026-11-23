import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterAll, describe, expect, it } from "vitest";
import { Usage } from "../scripts/agents/discovery.mjs";
import { REVIEWER_LOGIN, parseReviewVerdict } from "../scripts/agents/intake.mjs";
import {
  BOT_LOGIN, CARRIED_NOTE, NEW_FAILURE_NOTE, buildTable, carriedFields, closeRows, earlierPasses, fieldsOf, main, overallVerdict, renderReview, rowDigest,
  scopePromptLines, verdictMarker, withReceipt,
} from "../scripts/agents/reviewer.mjs";

// The second review of a revised batch (pull request #354). The intake agent may revise a pull
// request once. The review of 18c09f0 failed a link and the duplicates; the revision settled both
// and changed nothing else. The review of the revised head then failed description and task,
// which the review of 18c09f0 had passed with the same values, and the pull request was left with
// nobody able to act on it. A field an earlier review passed, unchanged since, now keeps its pass
// unless the review quotes a source passage that contradicts it.
//
// The reviews are the real ones (bodies unchanged). They were posted before the verdict marker
// listed what passed, so the review of 18c09f0 is rendered again here from its own verdicts and
// the batch it reviewed, which gives the marker it would carry now.
const DIR = "tests/agents-intake-revise-amend-fixtures/pr-354";
const BATCH_DIR = "data/omics/intake-349-20261121";
const BENCHMARK = "intake-349-20261121-benchmark-met-kinase-dms-benchmark";
const DATASET = "intake-349-20261121-dataset-kinase-inhibitor-datasets";
const SOURCE = "intake-349-20261121-source-github-fraser-lab-kinase-inhibitor-datasets-github";
const REPO_URL = "https://github.com/fraser-lab/Kinase_Inhibitor_Datasets";
const FIRST_HEAD = "18c09f08b0275c5ffbea98be38fef4ad0aac20d8";
const json = (file: string) => JSON.parse(fs.readFileSync(`${DIR}/${file}`, "utf8"));
const lines = (file: string) => fs.readFileSync(`${DIR}/${file}`, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const copy = <T>(x: T): T => JSON.parse(JSON.stringify(x));
const entity = (r: any) => r.kind !== "source";
const now = () => new Date("2026-11-23T12:00:00Z");
const quiet = () => {};

const fixture = json("pull.json");
const first = withReceipt(lines("batch/batch.jsonl"), json("batch/kg.json"));
const revised = withReceipt(lines("revised/batch.jsonl"), json("revised/kg.json"));
const revision = json("revised/revision.json");
const pageText: string = json("fetches.json")[REPO_URL].text;
const pages = new Map([[SOURCE, pageText]]);
const firstReview = fixture.reviews.at(-1);
const secondReview = json("review-after-revision.json").review;
const firstVerdict = parseReviewVerdict(firstReview.body)!;
const secondVerdict = parseReviewVerdict(secondReview.body)!;

/** A review's verdicts as the structuring call returns them: every field of every record passes, except those the review's marker lists. */
function replyOf(records: any[], verdict: { problems: { id: string; field: string; verdict: string; note: string }[] }, change: (f: any, id: string) => any = (f) => f) {
  return {
    records: records.filter(entity).map((r) => ({
      id: r.id,
      fields: fieldsOf(r).map((field: string) => {
        const p = verdict.problems.find((x) => x.id === r.id && x.field === field);
        return change(p ? { field, verdict: p.verdict, problem: p.note, evidence: "", contradiction: "" } : { field, verdict: "pass", problem: "", evidence: `${REPO_URL} README`, contradiction: "" }, r.id);
      }),
    })),
    unopened: [],
  };
}

// The review of 18c09f0 again, from its own verdicts. The finding on duplicates was the script's
// (a store record without a ruling), the one on the link was the model's.
const firstRows = buildTable(first, replyOf(first, firstVerdict), firstVerdict.problems.filter((p) => p.field === "duplicates").map((p) => ({ id: p.id, field: p.field, text: p.note })));
const firstBody = renderReview({ records: first, rows: firstRows, verdict: overallVerdict(firstRows), sourceNotes: [], usage: new Usage(), runUrl: "", mode: "approve", headSha: FIRST_HEAD });
const earlier = () => ({ ...earlierPasses([{ user: REVIEWER_LOGIN, commit_id: FIRST_HEAD, body: firstBody }])!, pages });
const secondReply = (change?: (f: any, id: string) => any) => replyOf(revised, secondVerdict, change);
const row = (rows: any[], id: string, field: string) => rows.find((r) => r.id === id && r.field === field);
const failed = (rows: any[]) => rows.filter((r) => r.verdict !== "pass").map((r) => `${r.id} ${r.field}`);

describe("the two reviews of #354 around its revision", () => {
  it("the first failed a link and the duplicates, the second failed description and task, which had not changed", () => {
    expect(firstReview.commit_id).toBe(FIRST_HEAD);
    expect(firstVerdict.problems.map((p) => `${p.id} ${p.field}`)).toEqual([`${BENCHMARK} links`, `${DATASET} duplicates`]);
    expect(secondReview.user).toBe(REVIEWER_LOGIN);
    expect(secondVerdict.problems.map((p) => `${p.id} ${p.field}`)).toEqual([`${BENCHMARK} description`, `${BENCHMARK} task`]);
    const before = first.find((r) => r.id === BENCHMARK);
    const after = revised.find((r) => r.id === BENCHMARK);
    expect(after.description).toBe(before.description);
    expect(after.attributes.task).toBe(before.attributes.task);
    expect(revision.fields.map((f: any) => `${f.id} ${f.field}`).sort()).toEqual([`${BENCHMARK} links`, `${DATASET} duplicates`]);
  });

  it("the first review rendered again fails what the real one failed", () => {
    expect(parseReviewVerdict(firstBody)!.problems.map((p) => `${p.id} ${p.field} ${p.verdict}`)).toEqual(firstVerdict.problems.map((p) => `${p.id} ${p.field} ${p.verdict}`));
    expect(parseReviewVerdict(firstBody)!.head_sha).toBe(FIRST_HEAD);
  });

  it("without scope, the second review's two failures leave the pull request without an approval", () => {
    const rows = buildTable(revised, secondReply(), [], closeRows(revision, revised));
    expect(failed(rows)).toEqual([`${BENCHMARK} description`, `${BENCHMARK} task`]);
    expect(overallVerdict(rows)).toBe("request changes");
  });
});

describe("the passes a review lists", () => {
  it("are in the verdict marker, one digest per passed field the model judges", () => {
    const marker = JSON.parse(/<!-- reviewer-verdict: (\{.*\}) -->$/.exec(firstBody)![1]);
    expect(Object.keys(marker.passed).sort()).toEqual([BENCHMARK, DATASET]);
    // Not the failed link, not the depth tier (the script's own check), not the missing duplicates.
    expect(Object.keys(marker.passed[BENCHMARK]).sort()).toEqual(["areas", "description", "entity_level", "name", "scope_note", "source_ids", "task"]);
    expect(Object.keys(marker.passed[DATASET]).sort()).toEqual(["access", "areas", "description", "name", "source_ids"]);
    const benchmark = first.find((r) => r.id === BENCHMARK);
    expect(marker.passed[BENCHMARK].description).toBe(rowDigest({ field: "description", value: benchmark.description, sources: SOURCE }));
    expect(marker.passed[BENCHMARK].description).toMatch(/^[0-9a-f]{16}$/);
    // The intake agent's revision reads the same marker and takes no notice of the new key.
    expect(parseReviewVerdict(firstBody)!.source).toBe("marker");
  });

  it("are left out of a marker with nothing to list, and of one that would be too long", () => {
    expect(verdictMarker({ rows: [], verdict: "approve", headSha: "abc" })).not.toContain("passed");
    expect(verdictMarker({ rows: [{ id: "(store diff)", kind: "pull request", field: "store diff", value: "3 record lines", sources: "", verdict: "pass", note: "" }, { id: BENCHMARK, kind: "benchmark", field: "depth_tier", value: "2", sources: SOURCE, verdict: "pass", note: "" }], verdict: "approve", headSha: "abc" })).not.toContain("passed");
    const many = Array.from({ length: 900 }, (_, i) => ({ id: `intake-1-20261121-model-number-${i}`, kind: "model", field: "name", value: `m${i}`, sources: "s", verdict: "pass", note: "" }));
    const fails = Array.from({ length: 3 }, (_, i) => ({ id: `intake-1-20261121-model-fail-${i}`, kind: "model", field: "name", value: "x", sources: "s", verdict: "fail", note: "wrong" }));
    const cut = verdictMarker({ rows: [...many, ...fails], verdict: "request changes", headSha: "abc" });
    expect(cut.length).toBeLessThanOrEqual(30000);
    expect(cut).not.toContain("passed");
    expect(parseReviewVerdict(`**Reviewer agent verdict: request changes.**\n\n${cut}`)!.problems).toHaveLength(3);
  });

  it("are read from the latest review by the reviewer agent only", () => {
    const got = earlierPasses([{ user: REVIEWER_LOGIN, commit_id: FIRST_HEAD, body: firstBody }])!;
    expect(got.head_sha).toBe(FIRST_HEAD);
    expect(got.passed.get(`${BENCHMARK} task`)).toMatch(/^[0-9a-f]{16}$/);
    expect(got.passed.has(`${BENCHMARK} links`)).toBe(false);
    // The comment-mode identity counts too; anyone else's review does not, whatever it holds.
    expect(earlierPasses([{ user: BOT_LOGIN, body: firstBody }])).not.toBeNull();
    expect(earlierPasses([{ user: "someone", body: firstBody }])).toBeNull();
    expect(earlierPasses([{ user: REVIEWER_LOGIN, body: firstBody }, { user: "someone", body: "looks fine" }])).not.toBeNull();
    // A marker quoted earlier in a body is not the verdict.
    expect(earlierPasses([{ user: REVIEWER_LOGIN, body: `${firstBody}\n\nmore text` }])).toBeNull();
    // The latest review by the agent decides even when its marker cannot be read, as in a review
    // GitHub made it post as a comment with a line after the marker: an older pass is not revived.
    expect(earlierPasses([{ user: REVIEWER_LOGIN, body: firstBody }, { user: BOT_LOGIN, body: `${secondReview.body}\n\n(Posted as a comment: GitHub refused REQUEST_CHANGES from this identity.)` }])).toBeNull();
    expect(earlierPasses([{ user: REVIEWER_LOGIN, body: firstBody }, { user: REVIEWER_LOGIN, body: "" }])).toBeNull();
    // The real reviews were posted before the marker listed passes: nothing carries over from them,
    // and nothing from an older review when the latest lists none.
    expect(earlierPasses(fixture.reviews)).toBeNull();
    expect(earlierPasses([{ user: REVIEWER_LOGIN, body: firstBody }, secondReview])).toBeNull();
    expect(earlierPasses([])).toBeNull();
  });
});

describe("a second review in scope", () => {
  it("carries over the fields the first review passed and the revision did not change", () => {
    expect(carriedFields(revised, closeRows(revision, revised), earlier()).map((c) => `${c.id} ${c.field}`)).toEqual([
      `${BENCHMARK} name`, `${BENCHMARK} description`, `${BENCHMARK} areas`, `${BENCHMARK} entity_level`, `${BENCHMARK} task`, `${BENCHMARK} scope_note`, `${BENCHMARK} source_ids`,
      `${DATASET} name`, `${DATASET} description`, `${DATASET} areas`, `${DATASET} access`, `${DATASET} source_ids`,
    ]);
    expect(carriedFields(revised, [], null)).toEqual([]);
  });

  it("passes description and task of #354, shows the objection, and the review approves", () => {
    const rows = buildTable(revised, secondReply(), [], closeRows(revision, revised), earlier());
    expect(failed(rows)).toEqual([]);
    expect(overallVerdict(rows)).toBe("approve");
    for (const field of ["description", "task"]) {
      const r = row(rows, BENCHMARK, field);
      expect(r.note.startsWith(`${CARRIED_NOTE} the review of 18c09f0 passed this value, and the value and the record's sources are the same now. This review objects, but quotes no passage of a cited source that contradicts the value, so it is not a failure: `)).toBe(true);
      expect(r.note).toContain(secondVerdict.problems.find((p) => p.field === field)!.note.slice(0, 80));
    }
    // A carried field the model passes again says only that it was carried.
    expect(row(rows, BENCHMARK, "name").note).toBe(`${CARRIED_NOTE} the review of 18c09f0 passed this value, and the value and the record's sources are the same now.`);
  });

  it("keeps a carried pass when the model returns no verdict or cannot verify the field", () => {
    const silent = secondReply();
    silent.records[0].fields = silent.records[0].fields.filter((f: any) => f.field !== "description");
    expect(row(buildTable(revised, silent, [], [], earlier()), BENCHMARK, "description").verdict).toBe("pass");
    const unsure = secondReply((f, id) => (id === BENCHMARK && f.field === "task" ? { ...f, verdict: "unverifiable", problem: "the page did not load" } : f));
    expect(row(buildTable(revised, unsure, [], [], earlier()), BENCHMARK, "task").verdict).toBe("pass");
  });

  it("judges in full the field the revision changed", () => {
    // The duplicates of the dataset failed in the first review and now hold the revision's rulings.
    const pass = row(buildTable(revised, secondReply(), [], [], earlier()), DATASET, "duplicates");
    expect(pass.verdict).toBe("pass");
    expect(pass.note).toBe(`${REPO_URL} README`);
    const fail = secondReply((f, id) => (id === DATASET && f.field === "duplicates" ? { ...f, verdict: "fail", problem: "the first store record is the same resource", evidence: "store" } : f));
    const r = row(buildTable(revised, fail, [], [], earlier()), DATASET, "duplicates");
    expect(r.verdict).toBe("fail");
    expect(r.note).toBe("the first store record is the same resource Evidence: store");
    // A field the model does not return is unverifiable there, as in a first review.
    const silent = secondReply();
    silent.records[1].fields = silent.records[1].fields.filter((f: any) => f.field !== "duplicates");
    expect(row(buildTable(revised, silent, [], [], earlier()), DATASET, "duplicates").verdict).toBe("unverifiable");
  });

  it("judges in full a field whose value changed since the first review, whoever changed it", () => {
    const edited = copy(revised);
    edited.find((r: any) => r.id === BENCHMARK).description = "Deep mutational scanning of the MET kinase domain, paired with predictions from 57 computational methods.";
    expect(carriedFields(edited, [], earlier()).map((c) => `${c.id} ${c.field}`)).not.toContain(`${BENCHMARK} description`);
    const rows = buildTable(edited, secondReply(), [], [], earlier());
    expect(failed(rows)).toEqual([`${BENCHMARK} description`]);
    expect(row(rows, BENCHMARK, "description").note).not.toContain(NEW_FAILURE_NOTE);
    // A pass was of the value against the record's sources: with another source cited, nothing of that record carries over.
    const resourced = copy(revised);
    resourced.find((r: any) => r.id === BENCHMARK).source_ids.push("another-source");
    expect(carriedFields(resourced, [], earlier()).map((c) => c.id)).not.toContain(BENCHMARK);
  });

  it("fails a carried field as a new failure when the model quotes a passage of the page that contradicts it", () => {
    const quote = "paired with predictions from 57 computational methods";
    const withQuote = (contradiction: string) => secondReply((f, id) => (id === BENCHMARK && f.field === "description" ? { ...f, problem: "The README pairs the data with methods' predictions; it names no ligand-affinity models.", evidence: `${REPO_URL} README intro`, contradiction } : f));
    const rows = buildTable(revised, withQuote(quote), [], [], earlier());
    const r = row(rows, BENCHMARK, "description");
    expect(r.verdict).toBe("fail");
    expect(r.note.startsWith(`${NEW_FAILURE_NOTE} the review of 18c09f0 passed this value and it has not changed since, but a source passage contradicts it.`)).toBe(true);
    expect(r.note).toContain(`Source passage: "${quote}"`);
    // The task objection quotes nothing, so it stays carried: one new failure, not two.
    expect(failed(rows)).toEqual([`${BENCHMARK} description`]);
    expect(overallVerdict(rows)).toBe("request changes");
    // The page breaks the line inside this passage; only white space is folded.
    expect(pageText).toContain("11 inhibitors plus a\nvehicle control");
    expect(row(buildTable(revised, withQuote("against 11 inhibitors plus a vehicle control"), [], [], earlier()), BENCHMARK, "description").verdict).toBe("fail");
  });

  it("does not take a passage that is not in the page of a source the record cites, or is too short", () => {
    const withQuote = (contradiction: string) => secondReply((f, id) => (id === BENCHMARK && f.field === "description" ? { ...f, contradiction } : f));
    const verdictWith = (contradiction: string, scope = earlier()) => row(buildTable(revised, withQuote(contradiction), [], [], scope), BENCHMARK, "description").verdict;
    expect(verdictWith("the README says the affinity values are measured, not predicted")).toBe("pass");
    expect(verdictWith("Paired With Predictions From 57 Computational Methods")).toBe("pass");
    expect(verdictWith("57 computational")).toBe("pass");
    expect(verdictWith("")).toBe("pass");
    // The text of a page the record does not cite, and a page the script could not read.
    expect(verdictWith("paired with predictions from 57 computational methods", { ...earlier(), pages: new Map([["another-source", pageText]]) })).toBe("pass");
    expect(verdictWith("paired with predictions from 57 computational methods", { ...earlier(), pages: new Map() })).toBe("pass");
    // A quote counts only with a fail: a pass that quotes the page is a pass.
    const passing = secondReply((f, id) => (id === BENCHMARK && f.field === "name" ? { ...f, contradiction: "paired with predictions from 57 computational methods" } : f));
    expect(row(buildTable(revised, passing, [], [], earlier()), BENCHMARK, "name").verdict).toBe("pass");
  });

  it("never carries a pass over a problem the script finds itself", () => {
    const rows = buildTable(revised, secondReply(), [{ id: BENCHMARK, field: "name", text: '"MET kinase DMS benchmark" is already in the store as x' }, { id: BENCHMARK, field: "depth_tier", text: "depth_tier is 2 but docs/tiers.md gives 1" }], [], earlier());
    expect(failed(rows)).toEqual([`${BENCHMARK} name`, `${BENCHMARK} depth_tier`]);
    expect(row(rows, BENCHMARK, "name").note).toBe('"MET kinase DMS benchmark" is already in the store as x');
  });

  it("tells the model which fields stand and what would overturn one", () => {
    const text = scopePromptLines([{ id: BENCHMARK, field: "description" }], FIRST_HEAD).join("\n");
    expect(text).toContain("An earlier review by the reviewer agent (of commit 18c09f0) passed the fields listed here");
    expect(text).toContain("copy the passage letter for letter");
    expect(text).toContain(`[{"id":"${BENCHMARK}","field":"description"}]`);
    expect(scopePromptLines([])).toEqual([]);
  });
});

describe("the reviewer's run on the revised #354, with fakes", () => {
  const roots: string[] = [];
  afterAll(() => {
    for (const root of roots) fs.rmSync(root, { recursive: true, force: true });
  });
  const env = { ANTHROPIC_API_KEY: "k", GITHUB_REPOSITORY: "rewire-bio/rewire-benchmark-data", APPROVER_TOKEN: "t" };

  async function run({ reviews, reply = secondReply(), extra = {} }: { reviews: any[] | null; reply?: any; extra?: Record<string, unknown> }) {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "reviewer-scope-"));
    roots.push(root);
    fs.mkdirSync(path.join(root, BATCH_DIR), { recursive: true });
    fs.mkdirSync(path.join(root, "data/entities"), { recursive: true });
    for (const name of ["batch.jsonl", "kg.json", "revision.json"]) fs.copyFileSync(`${DIR}/revised/${name}`, path.join(root, BATCH_DIR, name));
    const fileOf: Record<string, string> = { benchmark: "benchmarks", dataset: "datasets", source: "sources" };
    const posted: { event: string; body: string }[] = [];
    const commands: string[] = [];
    const prompts: string[] = [];
    const client = {
      getPull: async () => ({ number: 354, title: fixture.pull.title, author: BOT_LOGIN, state: "open", head_sha: secondReview.commit_id, html_url: fixture.pull.html_url }),
      files: async () => [
        ...["batch.jsonl", "kg.json", "notes.md", "review.json", "revision.json"].map((n) => ({ filename: `${BATCH_DIR}/${n}`, status: "added" })),
        ...lines("revised/batch.jsonl").map((r) => ({ filename: `data/entities/${fileOf[r.kind]}.jsonl`, status: "modified", patch: `@@ -1,1 +1,2 @@\n {"id":"context"}\n+${JSON.stringify(r)}` })),
      ],
      ...(reviews ? { reviews: async () => reviews } : {}),
      ...extra,
      checkRuns: async () => [{ name: "checks (store)", status: "completed", conclusion: "success" }],
      review: async (_repo: string, _n: number, r: { event: string; body: string }) => {
        posted.push({ event: r.event, body: r.body });
      },
      comment: async () => {},
    };
    const anthropic = {
      beta: { messages: { stream: (req: any) => ({ finalMessage: async () => {
        prompts.push(req.messages[0].content);
        return { model: req.model, stop_reason: "end_turn", content: [{ type: "text", text: "notes" }], usage: { input_tokens: 2000, output_tokens: 500 } };
      } }) } },
      messages: { create: async () => ({ stop_reason: "end_turn", content: [{ type: "text", text: JSON.stringify(reply) }], usage: { input_tokens: 500, output_tokens: 500 } }) },
    };
    const fetchImpl = async () => new Response(pageText, { status: 200, headers: { "content-type": "text/plain" } });
    const result = await main(["--pr", "354", "--mode", "approve", "--root", root], env, { github: client, approver: client, anthropic, fetch: fetchImpl, run: (cmd: string, args: string[]) => (commands.push([cmd, ...args].join(" ")), { ok: true, output: "" }), now, log: quiet, sleep: async () => {} });
    return { result, posted, commands, prompts };
  }
  const earlierReviews = () => [fixture.reviews[0], fixture.reviews[1], { ...firstReview, body: firstBody }];

  it("approves: description and task keep the pass of the first review, and the review says so", async () => {
    const { result, posted, commands, prompts } = await run({ reviews: earlierReviews() });
    expect(result.outcome).toBe("approved; auto-merge enabled");
    expect(posted.map((p) => p.event)).toEqual(["APPROVE"]);
    expect(commands).toEqual(["gh pr merge 354 --auto --merge --repo rewire-bio/rewire-benchmark-data"]);
    expect(prompts[0]).toContain("An earlier review by the reviewer agent (of commit 18c09f0) passed the fields listed here");
    expect(prompts[0]).toContain(`{"id":"${BENCHMARK}","field":"description"}`);
    expect(prompts[0]).not.toContain(`{"id":"${DATASET}","field":"duplicates"}`);
    const body = posted[0].body;
    expect(body).toContain("12 fields that the review of 18c09f0 passed have the same value and sources now and keep that verdict, unless this review quotes a source passage that contradicts one. Every other field is judged in full.");
    expect(body).toContain(`This review objected to 2 carried-over fields without quoting a source passage that contradicts them, so they pass (\`${BENCHMARK}\` description, \`${BENCHMARK}\` task). The objections are in the table.`);
    expect(body).not.toContain("judges the revised records in full");
    // The next review can carry over from this one: the two fields are in its marker.
    const next = earlierPasses([{ user: REVIEWER_LOGIN, body }])!;
    expect(next.head_sha).toBe(secondReview.commit_id);
    expect(next.passed.has(`${BENCHMARK} description`)).toBe(true);
    expect(next.passed.has(`${DATASET} duplicates`)).toBe(true);
  });

  it("requests changes on a new failure, with the passage found in the page it fetched itself", async () => {
    const quote = "paired with predictions from 57 computational methods";
    const reply = secondReply((f, id) => (id === BENCHMARK && f.field === "description" ? { ...f, contradiction: quote } : f));
    const { result, posted } = await run({ reviews: earlierReviews(), reply });
    expect(result.outcome).toBe("requested changes");
    expect(posted[0].event).toBe("REQUEST_CHANGES");
    expect(posted[0].body).toContain(`- \`${BENCHMARK}\` description (fail): ${NEW_FAILURE_NOTE} the review of 18c09f0 passed this value`);
    expect(parseReviewVerdict(posted[0].body)!.problems.map((p) => p.field)).toEqual(["description"]);
  });

  it("judges every field in full when no earlier review lists its passes, as it did on the day", async () => {
    for (const reviews of [fixture.reviews, [], null]) {
      const { result, posted, prompts } = await run({ reviews });
      expect(result.outcome).toBe("requested changes");
      expect(parseReviewVerdict(posted[0].body)!.problems.map((p) => p.field)).toEqual(["description", "task"]);
      expect(posted[0].body).toContain("This review judges the revised records in full, and the intake agent does not revise again.");
      expect(prompts[0]).not.toContain("An earlier review by the reviewer agent");
    }
  });

  it("judges in full, and says why, when the earlier reviews cannot be read", async () => {
    const { result, posted } = await run({ reviews: null, extra: { reviews: async () => { throw new Error("GET /pulls/354/reviews: 502"); } } });
    expect(result.outcome).toBe("requested changes");
    expect(posted[0].body).toContain("The earlier reviews could not be read (GET /pulls/354/reviews: 502), so no verdict is carried over.");
    expect(parseReviewVerdict(posted[0].body)!.problems.map((p) => p.field)).toEqual(["description", "task"]);
  });
});
