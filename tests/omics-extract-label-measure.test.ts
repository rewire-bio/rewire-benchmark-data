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
  scoreOutcome,
  type HeldoutRow,
} from "../scripts/omics/extract/label-measure";
import type { LabelOutcome, LabelTable, LabelTransport, Shortlist } from "../shared/omics/extract/label/index";

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
  for (const writer of ["writeKind", "writeStore", "addBatch", "recordChanges", "reshardStore", "upsertRow", "updateRow", "markStore", "markRemoved", "putObject", "adoptFile", "writeRegistry"])
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
