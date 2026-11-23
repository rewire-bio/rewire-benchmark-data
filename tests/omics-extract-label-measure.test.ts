/** The measurement command: the cap, the scoring and the write set.
 *
 * Nothing here asks anything. The cap is checked against a stub that counts
 * calls, the scoring against rows of the frozen file, and the claim that the
 * command cannot write a record against the command's own source, because a
 * claim about a write set is only worth something if something checks it.
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, expect, it } from "vitest";
import {
  PASSES,
  cappedTransport,
  planQuestions,
  readHeldout,
  rate,
  recallTable,
  rescoreAnswers,
  scoreOutcome,
  shortlistRecall,
  type HeldoutRow,
} from "../scripts/omics/extract/label-measure";
import { buildShortlistIndex } from "../shared/omics/extract/label/index";
import type { AssessmentRecord, LabelOutcome, LabelTable, LabelTransport, Shortlist } from "../shared/omics/extract/label/index";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const folders: string[] = [];
afterEach(() => folders.splice(0).forEach((folder) => fs.rmSync(folder, { recursive: true, force: true })));

const temporaryFile = (body: string): string => {
  const folder = fs.mkdtempSync(path.join(os.tmpdir(), "label-measure-"));
  folders.push(folder);
  const file = path.join(folder, "heldout.tsv");
  fs.writeFileSync(file, body);
  return file;
};

const table = (id: string, overrides: Partial<LabelTable> = {}): LabelTable => ({
  table_id: id,
  source_id: "source-one",
  layer_sha256: "a".repeat(64),
  anchor: { kind: "table", index: 0, caption: "Table 1. Results on the benchmark", label: "Table 1" } as LabelTable["anchor"],
  anchor_text: "Table 1. Results on the benchmark",
  anchor_text_from: "caption",
  column_headers: ["AUROC"],
  row_labels: ["a model"],
  held_back: { column_headers: 0, row_labels: 0, numeric: 0 },
  extent: { start: 0, end: 100 },
  candidate_ids: [`${id}-c1`],
  decided: [],
  ...overrides,
});

const heldoutRow = (id: string, overrides: Partial<HeldoutRow> = {}): HeldoutRow => ({
  source: "source-one",
  table_id: id,
  truth_count: 1,
  truth_ids: ["protocol-one"],
  scored_answer: "protocol-one",
  shortlist_full_hit: true,
  shortlist_lexical_hit: true,
  caption: '"Table 1"',
  ...overrides,
});

const shortlist = (ids: string[]): Shortlist => ({
  ids,
  entries: ids.map((id) => ({ id, kind: "protocol", name: id, why: ["name_in_table"], name_word_share: 1 })),
  considered: 2242,
  held_back: 0,
});

const outcome = (id: string, over: Partial<LabelOutcome>): LabelOutcome => ({
  table_id: id,
  source_id: "source-one",
  layer_sha256: "a".repeat(64),
  anchor: table(id).anchor,
  anchor_text: "Table 1. Results on the benchmark",
  candidate_ids: [],
  shortlist: shortlist(["protocol-one"]),
  asked: true,
  cached: false,
  answer: null,
  outcome: "abstained",
  record_id: null,
  span: null,
  reason: null,
  detail: "",
  checks: [],
  measured: null,
  ...over,
});

it("plans both rules, interleaved, and truncates to the cap before anything is built", () => {
  const rows = Array.from({ length: 5 }, (_, at) => heldoutRow(`t${at}`));
  const plan = planQuestions({
    rows,
    tableOf: (row) => table(row.table_id),
    shortlistOf: () => shortlist(["protocol-one"]),
    haveLayer: () => true,
    cap: 3,
  });
  expect(plan.questions).toHaveLength(3);
  expect(plan.not_asked_cap).toBe(7);
  // Interleaved, so a small cap measures both rules rather than spending
  // everything on the first.
  expect(plan.questions.map((question) => question.pass)).toEqual(["both_rules", "lexical_only", "both_rules"]);
  expect(plan.by_pass.both_rules.asked).toBe(2);
  expect(plan.by_pass.lexical_only.asked).toBe(1);
  for (const pass of PASSES) expect(plan.by_pass[pass].askable).toBe(5);
});

it("counts, and never asks about, a table the preconditions stop", () => {
  const rows = [heldoutRow("decided"), heldoutRow("silent"), heldoutRow("nothing-offered"), heldoutRow("no-layer"), heldoutRow("fine")];
  const plan = planQuestions({
    rows,
    tableOf: (row) =>
      row.table_id === "decided" ? table(row.table_id, { decided: ["protocol-two"] })
      : row.table_id === "silent" ? table(row.table_id, { anchor_text: "T1" })
      : table(row.table_id),
    shortlistOf: (_pass, built) => shortlist(built.table_id === "nothing-offered" ? [] : ["protocol-one"]),
    haveLayer: (built) => built.table_id !== "no-layer",
    cap: 100,
  });
  expect(plan.by_pass.both_rules.askable).toBe(1);
  expect(plan.by_pass.both_rules.blocked).toEqual({
    already_decided: 1, no_anchor_text: 1, empty_shortlist: 1, quote_unresolved: 1,
  });
  expect(plan.questions.map((question) => question.table.table_id)).toEqual(["fine", "fine"]);
});

it("reports a frozen row this build does not reproduce rather than dropping it", () => {
  const plan = planQuestions({
    rows: [heldoutRow("gone"), heldoutRow("here")],
    tableOf: (row) => (row.table_id === "gone" ? null : table(row.table_id)),
    shortlistOf: () => shortlist(["protocol-one"]),
    haveLayer: () => true,
    cap: 100,
  });
  for (const pass of PASSES) {
    expect(plan.by_pass[pass].in_set).toBe(2);
    expect(plan.by_pass[pass].not_rebuilt).toBe(1);
    expect(plan.by_pass[pass].askable).toBe(1);
  }
});

it("refuses the call past the cap rather than counting it afterwards", async () => {
  let calls = 0;
  const inner: LabelTransport = async (request) => {
    calls += 1;
    return { text: "{}", model: request.model, input_tokens: 1, output_tokens: 1 };
  };
  const guard = cappedTransport(inner, 3);
  const request = { model: "m", effort: "low", max_tokens: 10, system: "s", question: "q", schema: {} };
  for (let at = 0; at < 3; at += 1) await guard.transport(request);
  await expect(guard.transport(request)).rejects.toThrow(/cap of 3 questions/);
  await expect(guard.transport(request)).rejects.toThrow(/cap of 3 questions/);
  // calls() can never pass the cap, so a check on it alone would be unreachable.
  // What the guard refused is the number that says the plan stopped bounding.
  expect({ reached: calls, counted: guard.calls(), refused: guard.refused() })
    .toEqual({ reached: 3, counted: 3, refused: 2 });
});

it("scores a label against the answer frozen before it was given", () => {
  const right = heldoutRow("one");
  expect(scoreOutcome(right, outcome("one", { outcome: "labelled", record_id: "protocol-one" }))).toBe("correct");
  expect(scoreOutcome(right, outcome("one", { outcome: "labelled", record_id: "protocol-two" }))).toBe("wrong");
  expect(scoreOutcome(right, outcome("one", { outcome: "abstained" }))).toBe("abstained");
  expect(scoreOutcome(right, outcome("one", { outcome: "refused", reason: "quote_unresolved" }))).toBe("refused");
});

it("counts any label on a table reporting several assessments as wrong, and its abstention as an abstention", () => {
  const several = heldoutRow("many", { truth_count: 3, truth_ids: ["a", "b", "c"], scored_answer: "none" });
  expect(scoreOutcome(several, outcome("many", { outcome: "labelled", record_id: "a" }))).toBe("wrong");
  // Abstaining is the only right answer here, and it is still reported as an
  // abstention: folding it into the correct rate would flatter the stage.
  expect(scoreOutcome(several, outcome("many", { outcome: "abstained" }))).toBe("abstained");
});

it("prints a rate with its denominator, always", () => {
  expect(rate(66, 67)).toBe("66 of 67, 98.5 percent");
  expect(rate(24, 67)).toBe("24 of 67, 35.8 percent");
  expect(rate(0, 0)).toBe("0 of 0");
});

it("reads the frozen set, and refuses a file that is not it", () => {
  const header = ["source", "table_id", "truth_count", "truth_ids", "scored_answer", "shortlist_full_hit", "shortlist_lexical_hit", "caption"];
  const file = temporaryFile(`${header.join("\t")}\nsource-one\tabc\t2\tp1|p2\tnone\t1\t0\t"Table 1"\n`);
  expect(readHeldout(file)).toEqual([
    { source: "source-one", table_id: "abc", truth_count: 2, truth_ids: ["p1", "p2"], scored_answer: "none",
      shortlist_full_hit: true, shortlist_lexical_hit: false, caption: '"Table 1"' },
  ]);
  const wrong = temporaryFile("source\ttable_id\nsource-one\tabc\n");
  expect(() => readHeldout(wrong)).toThrow(/has no truth_count column, so it is not the held-out set/);
});

it("reads the frozen set this lane actually froze", () => {
  const frozen = path.join(root, "maintenance/reports/label-evaluation-2026-11-19-heldout.tsv");
  if (!fs.existsSync(frozen)) return;
  const rows = readHeldout(frozen);
  expect(rows).toHaveLength(115);
  expect(rows.filter((row) => row.truth_count === 1)).toHaveLength(66);
  // The scored answer is an id where the table reports one assessment and the
  // word none where it reports several. Nothing else is a scorable answer.
  for (const row of rows) expect(row.scored_answer === "none").toBe(row.truth_count !== 1);
});

// --------------------------------------------------------- the write set, checked rather than stated

const source = fs.readFileSync(path.join(root, "scripts/omics/extract/label-measure.ts"), "utf8");

it("imports nothing from the record store that writes one", () => {
  const imports = [...source.matchAll(/import\s*\{([^}]*)\}\s*from\s*"([^"]+)"/g)].map(([, names, from]) => ({
    from,
    names: names.split(",").map((name) => name.replace(/\btype\b/, "").trim()).filter(Boolean),
  }));
  const records = imports.filter((entry) => entry.from.endsWith("/records") || entry.from.endsWith("../records"));
  expect(records.flatMap((entry) => entry.names)).toEqual(["readKind"]);
  // Nothing that writes a record, a manifest row or a cached object is named
  // anywhere in the file, imported or not.
  for (const writer of ["writeKind", "writeStore", "addBatch", "recordChanges", "reshardStore", "upsertRow", "updateRow", "markHome", "markMirror", "markRemoved", "putObject", "adoptFile", "writeRegistry"])
    expect({ writer, present: source.includes(writer) }).toEqual({ writer, present: false });
});

it("writes only under the report directory it was given", () => {
  const writes = [...source.matchAll(/fs\.(writeFileSync|mkdirSync|appendFileSync|rmSync|renameSync)\(([^,)]+)/g)];
  expect(writes.length).toBeGreaterThan(0);
  for (const [, call, target] of writes) {
    // Every write target is the report directory, a path built from the prefix
    // that is joined from it, or the cache file beside them.
    expect({ call, target: target.trim(), rooted: /options\.out|prefix|cacheFile/.test(target) }).toEqual({
      call, target: target.trim(), rooted: true,
    });
  }
  expect(source).toContain('const prefix = path.join(options.out, `label-measurement-${options.date}`)');
  // The one write that does not go through fs here: the cache, whose path is
  // joined from the report directory like everything else.
  expect(source).toContain('const cacheFile = path.join(options.out, `label-measure-cache-${options.date}.json`)');
  expect([...source.matchAll(/writeCache\(([^,)]+)/g)].map(([, target]) => target.trim())).toEqual(["cacheFile"]);
});

it("runs the one stage that asks, and nothing that promotes a candidate into the store", () => {
  for (const promoter of ["labelsByCandidate", "batch.jsonl", "data/entities", "data/evidence", "data/provenance"])
    expect({ promoter, present: source.includes(promoter) }).toEqual({ promoter, present: false });
});

it("re-counts a paid-for run with the confidence rule removed, changing only the rows that rule refused", () => {
  const header = ["pass", "source", "table_id", "truth_count", "scored_answer", "answered", "outcome", "score", "confidence", "refusal", "shortlist_size", "shortlist_holds_truth", "quote"];
  const line = (pass: string, count: number, scored: string, answered: string, score: string, refusal: string, holds = "1") =>
    [pass, "source-one", "t", String(count), scored, answered, score === "refused" ? "refused" : "labelled", score, "high", refusal, "3", holds, '""'].join("\t");
  const file = temporaryFile([
    header.join("\t"),
    line("both_rules", 1, "right", "right", "correct", ""),
    // Refused by the rule and right: a correct label once the rule is gone.
    line("both_rules", 1, "right", "right", "refused", "confidence_unjustified"),
    // Refused by another check: stays refused.
    line("both_rules", 1, "right", "right", "refused", "quote_unresolved"),
    // Refused by the rule and naming another record: a wrong label once the rule is gone.
    line("lexical_only", 1, "right", "other", "refused", "confidence_unjustified", "0"),
    // Refused by the rule on a table with several assessments: no label can be right there.
    line("lexical_only", 3, "none", "one-of-them", "refused", "confidence_unjustified"),
    line("lexical_only", 3, "none", "", "abstained", ""),
  ].join("\n"));

  const [warm, cold] = rescoreAnswers(file);
  expect(warm).toMatchObject({
    pass: "both_rules", asked: 3, single_assessment_tables: 3, single_assessment_tables_with_truth_on_shortlist: 3,
    before: { correct: 1, wrong: 0, abstained: 0, refused: 2 },
    after: { correct: 2, wrong: 0, abstained: 0, refused: 1 },
    refused_by_the_rule: 1, refused_by_the_rule_and_right: 1,
  });
  expect(cold).toMatchObject({
    pass: "lexical_only", asked: 3, single_assessment_tables: 1, single_assessment_tables_with_truth_on_shortlist: 0,
    before: { correct: 0, wrong: 0, abstained: 1, refused: 2 },
    after: { correct: 0, wrong: 2, abstained: 1, refused: 0 },
    refused_by_the_rule: 2, refused_by_the_rule_and_right: 0,
  });
});

it("re-counts the first live run to the figures the pull request states", () => {
  const [warm, cold] = rescoreAnswers(path.join(root, "maintenance/reports/label-measurement-2026-11-20-answers.tsv"));
  expect(warm).toMatchObject({
    asked: 109, single_assessment_tables: 66,
    before: { correct: 15, wrong: 2, abstained: 75, refused: 17 },
    after: { correct: 31, wrong: 2, abstained: 75, refused: 1 },
    refused_by_the_rule: 16, refused_by_the_rule_and_right: 16,
  });
  expect(cold).toMatchObject({
    asked: 43, single_assessment_tables: 19, single_assessment_tables_with_truth_on_shortlist: 7,
    before: { correct: 0, wrong: 5, abstained: 32, refused: 6 },
    after: { correct: 5, wrong: 6, abstained: 32, refused: 0 },
    refused_by_the_rule: 6, refused_by_the_rule_and_right: 5,
  });
});

it("counts shortlist recall for both methods at each size, with citations kept and stripped", () => {
  const records: AssessmentRecord[] = [
    // Named in words the caption prints: both methods reach it.
    { id: "printed", kind: "protocol", name: "Results benchmark", source_ids: ["source-one"] },
    // Named in other words and described in the caption's: only the search reaches it.
    { id: "described", kind: "protocol", name: "Held out split", description: "Results on the benchmark, by AUROC.", source_ids: ["source-one"] },
    // Nothing the caption prints: only its citation reaches it.
    { id: "cited", kind: "protocol", name: "Quite unrelated", source_ids: ["source-one"] },
  ];
  const indexes = {
    both_rules: buildShortlistIndex(records, []),
    lexical_only: buildShortlistIndex(records.map((record) => ({ ...record, source_ids: [] })), []),
  };
  const rows = [
    heldoutRow("t1", { truth_ids: ["printed"], scored_answer: "printed" }),
    heldoutRow("t2", { truth_ids: ["described"], scored_answer: "described" }),
    heldoutRow("t3", { truth_ids: ["cited"], scored_answer: "cited" }),
    heldoutRow("t4", { truth_count: 2, truth_ids: ["printed", "cited"], scored_answer: "none" }),
    heldoutRow("gone"),
  ];
  const recall = shortlistRecall({ rows, tableOf: (row) => (row.table_id === "gone" ? null : table(row.table_id)), indexes, sizes: [10] });
  const of = (pass: string, method: string) => recall.find((row) => row.pass === pass && row.method === method);

  expect(recall).toHaveLength(PASSES.length * 2);
  // A row whose table was not rebuilt is left out of the denominator, not counted as a miss.
  expect(of("both_rules", "lexical")).toMatchObject({ tables: 4, holds_truth: 4, single_tables: 3, single_holds_truth: 3, empty: 0 });
  expect(of("both_rules", "search")).toMatchObject({ tables: 4, holds_truth: 4, single_tables: 3, single_holds_truth: 3 });
  expect(of("lexical_only", "lexical")).toMatchObject({ tables: 4, holds_truth: 2, single_tables: 3, single_holds_truth: 1 });
  expect(of("lexical_only", "search")).toMatchObject({ tables: 4, holds_truth: 3, single_tables: 3, single_holds_truth: 2 });
  expect(recallTable(recall)).toHaveLength(2 + recall.length);
});

it("measures recall and re-counts without a transport, a key or a write", () => {
  for (const name of ["shortlistRecall", "labelRecall", "rescoreAnswers"]) {
    const body = source.slice(source.indexOf(`export function ${name}(`));
    const end = body.indexOf("\n}\n");
    const text = body.slice(0, end);
    for (const banned of ["liveTransport", "transport", "writeFileSync", "writeCache", "process.env"])
      expect({ name, banned, present: text.includes(banned) }).toEqual({ name, banned, present: false });
  }
});
