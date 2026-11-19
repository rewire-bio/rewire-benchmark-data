/** The label stage asked for real, scored against the frozen held-out set.
 *
 * `label-evaluate` measures every bound the pipeline imposes before a question
 * is asked. It asks nothing, and it says so. This is the other half: it asks,
 * it scores, and it reports the four rates that decide whether the stage is
 * fit to label anything.
 *
 * What makes it honest.
 *
 * The set is read from the frozen TSV that `label-evaluate` wrote, not
 * regenerated. The `scored_answer` column was written before any answer
 * existed, which is the only reason a score means anything. A frozen row whose
 * table this build does not reproduce is reported as not rebuilt, never
 * dropped.
 *
 * The pre-filter is measured twice, as two separate runs, because its two
 * rules bound different things. `cites_this_source` is the store saying the
 * record already names this source, which is true only of sources somebody has
 * already extracted: measured on the set it holds the right answer for 113 of
 * 115 tables, and that number says nothing at all about a paper nobody has
 * touched. `name_in_table` is the rule that has to carry a cold source, and on
 * the same set it offers nothing whatever for 72 of the 115. The two cannot be
 * averaged and they are never printed in one table. Asking with the second
 * shortlist is a different question, so it is asked, not derived from the
 * first run's answers.
 *
 * The cost cap binds before the first call. The questions are planned, counted
 * and truncated to the cap while the transport is still untouched; the
 * transport is then wrapped in a counter that refuses the call after the cap as
 * a second guard, and the counter is checked after the run because
 * `labelTables` turns a transport failure into a refusal rather than an error.
 *
 * This writes a report and nothing else. Every path it writes is under the
 * report directory it was given. It imports `readKind` from the record store
 * and nothing that writes one, and `readManifest` from the archive and nothing
 * that writes a row. `tests/omics-extract-label-measure.test.ts` asserts both
 * against this file's own text, so the claim is checked rather than stated.
 */
import fs from "node:fs";
import path from "node:path";
import { buildDecider, extractSource, assessmentKinds, systemKinds } from "../../../shared/omics/extract/index";
import {
  buildShortlistIndex,
  shortlistFor,
  tablesOf,
  labelTables,
  loadPrompt,
  liveTransport,
  recordedTransport,
  DEFAULT_EFFORT,
  DEFAULT_MODEL,
  readCache,
  writeCache,
  type LabelOutcome,
  type LabelTable,
  type LabelTransport,
  type Shortlist,
  type ShortlistIndex,
} from "../../../shared/omics/extract/label/index";
import { layerText, layersForSource } from "../../../shared/omics/layers/index";
import { indexLayer, type LayerIndex } from "../../../shared/omics/spans/offsets";
import { readKind } from "../records";

/** The two pre-filter rules, each measured on its own. The order is the order
 * the report prints them in, and the strong rule comes first because that is
 * the number somebody will quote; the heading beside it says what it is worth. */
export const PASSES = ["both_rules", "lexical_only"] as const;
export type Pass = (typeof PASSES)[number];

export const PASS_TITLE: Record<Pass, string> = {
  both_rules: "Both pre-filter rules: a source the store already cites",
  lexical_only: "The lexical rule alone: a source nothing in the store points at",
};

/** One line of the frozen held-out set. */
export interface HeldoutRow {
  source: string;
  table_id: string;
  truth_count: number;
  truth_ids: string[];
  /** The id a label is scored against, or `none` where the table reports
   * several assessments and no single label can be right. Frozen before any
   * answer existed. */
  scored_answer: string;
  shortlist_full_hit: boolean;
  shortlist_lexical_hit: boolean;
  caption: string;
}

/** Read the frozen set. A missing column is an error naming it: a measurement
 * scored against a file that is not the frozen one is not a measurement. */
export function readHeldout(file: string): HeldoutRow[] {
  const lines = fs.readFileSync(file, "utf8").split("\n").filter((line) => line.trim() !== "");
  if (lines.length < 2) throw new Error(`${file} holds no rows. It is the frozen held-out set label-evaluate writes.`);
  const header = lines[0].split("\t");
  const at = (name: string): number => {
    const index = header.indexOf(name);
    if (index < 0) throw new Error(`${file} has no ${name} column, so it is not the held-out set this is scored against.`);
    return index;
  };
  const columns = {
    source: at("source"), table: at("table_id"), count: at("truth_count"), ids: at("truth_ids"),
    scored: at("scored_answer"), full: at("shortlist_full_hit"), lexical: at("shortlist_lexical_hit"), caption: at("caption"),
  };
  return lines.slice(1).map((line) => {
    const cells = line.split("\t");
    return {
      source: cells[columns.source],
      table_id: cells[columns.table],
      truth_count: Number(cells[columns.count]),
      truth_ids: cells[columns.ids].split("|").filter(Boolean),
      scored_answer: cells[columns.scored],
      shortlist_full_hit: cells[columns.full] === "1",
      shortlist_lexical_hit: cells[columns.lexical] === "1",
      caption: cells[columns.caption],
    };
  });
}

/** Why a table was never asked about. The names are `check.ts`'s own, so a
 * reason here and a reason on a per-table line mean the same thing. */
export type Blocked = "already_decided" | "no_anchor_text" | "empty_shortlist" | "quote_unresolved";

export interface Question {
  pass: Pass;
  row: HeldoutRow;
  table: LabelTable;
}

export interface PassPlan {
  /** Frozen rows in the set. */
  in_set: number;
  /** Frozen rows whose table this build does not reproduce. Reported, never dropped. */
  not_rebuilt: number;
  /** Tables a question could be asked about, before the cap. */
  askable: number;
  blocked: Record<string, number>;
  /** How many of the askable the cap left room for. */
  asked: number;
}

export interface Plan {
  questions: Question[];
  cap: number;
  not_asked_cap: number;
  by_pass: Record<Pass, PassPlan>;
}

/**
 * Which questions a run would ask, in order, truncated to the cap.
 *
 * The two passes are interleaved rather than run one after the other, so a
 * small cap measures both rules instead of spending every question on the
 * first. The order inside a pass is the frozen file's, which is sorted, so the
 * same cap selects the same questions on every run.
 */
export function planQuestions(input: {
  rows: HeldoutRow[];
  tableOf: (row: HeldoutRow) => LabelTable | null;
  shortlistOf: (pass: Pass, table: LabelTable) => Shortlist;
  haveLayer: (table: LabelTable) => boolean;
  cap: number;
}): Plan {
  const perPass = new Map<Pass, Question[]>();
  const by_pass = {} as Record<Pass, PassPlan>;

  for (const pass of PASSES) {
    const plan: PassPlan = { in_set: input.rows.length, not_rebuilt: 0, askable: 0, blocked: {}, asked: 0 };
    const questions: Question[] = [];
    const block = (reason: Blocked) => { plan.blocked[reason] = (plan.blocked[reason] ?? 0) + 1; };
    for (const row of input.rows) {
      const table = input.tableOf(row);
      if (!table) { plan.not_rebuilt += 1; continue; }
      // The same four preconditions labelTables applies, in the same order, so
      // the plan's count and the receipt's agree.
      if (table.decided.length > 0) { block("already_decided"); continue; }
      if (table.anchor_text.trim().length < 4) { block("no_anchor_text"); continue; }
      if (input.shortlistOf(pass, table).ids.length === 0) { block("empty_shortlist"); continue; }
      if (!input.haveLayer(table)) { block("quote_unresolved"); continue; }
      plan.askable += 1;
      questions.push({ pass, row, table });
    }
    perPass.set(pass, questions);
    by_pass[pass] = plan;
  }

  const ordered: Question[] = [];
  const longest = Math.max(0, ...PASSES.map((pass) => perPass.get(pass)!.length));
  for (let at = 0; at < longest; at += 1)
    for (const pass of PASSES) {
      const question = perPass.get(pass)![at];
      if (question) ordered.push(question);
    }

  const cap = Math.max(0, Math.trunc(input.cap));
  const questions = ordered.slice(0, cap);
  for (const question of questions) by_pass[question.pass].asked += 1;
  return { questions, cap, not_asked_cap: ordered.length - questions.length, by_pass };
}

/**
 * The second guard on the cost.
 *
 * The plan is the first: the questions beyond the cap are never built. This
 * refuses a call anyway, so a future caller that forgets to truncate pays for
 * nothing. `labelTables` turns a thrown transport into a `transport_failed`
 * refusal rather than an error, so the caller reads `calls()` after the run and
 * fails the job if it ever exceeded the cap, instead of letting an overrun read
 * as a refusal.
 */
export function cappedTransport(inner: LabelTransport, cap: number): { transport: LabelTransport; calls: () => number; refused: () => number } {
  let calls = 0;
  let refused = 0;
  return {
    transport: async (request) => {
      if (calls >= cap) {
        // Counted, because `calls` can never exceed the cap and a check on it
        // alone would be unreachable. A refusal here means the plan stopped
        // truncating, and the caller fails the run on it rather than letting it
        // read as a transport failure on a line.
        refused += 1;
        throw new Error(`The cap of ${cap} questions was already reached, so this question was not asked and nothing was spent on it.`);
      }
      calls += 1;
      return inner(request);
    },
    calls: () => calls,
    refused: () => refused,
  };
}

/** What one answer came to, against the answer frozen before it was given.
 *
 * `correct` is a label on the frozen id. A table reporting several assessments
 * has no correct label at all, so any label on one is wrong; the abstention
 * that is the right answer there is counted as an abstention and reported
 * separately, because folding it into `correct` would flatter the stage and
 * hide the abstention rate. */
export type Score = "correct" | "wrong" | "abstained" | "refused";

export function scoreOutcome(row: HeldoutRow, outcome: LabelOutcome): Score {
  if (outcome.outcome === "refused") return "refused";
  if (outcome.outcome === "abstained") return "abstained";
  if (row.truth_count !== 1) return "wrong";
  return outcome.record_id === row.scored_answer ? "correct" : "wrong";
}

/** A rate printed with its denominator, always. A bare percentage in this
 * report is a number somebody will move to the other rule's column. */
export const rate = (count: number, total: number): string =>
  total === 0 ? `0 of 0` : `${count} of ${total}, ${((100 * count) / total).toFixed(1)} percent`;

export interface PassResult {
  pass: Pass;
  title: string;
  plan: PassPlan;
  /** The pre-filter, over the tables in the set this build rebuilt. */
  shortlist: { tables: number; holds_truth: number; lacks_truth: number; empty: number; miss: number };
  /** The outcomes, over the questions actually asked in this pass. */
  asked: number;
  correct: number;
  wrong: number;
  abstained: number;
  refused: number;
  abstained_on_multi_assessment_tables: number;
  multi_assessment_tables_asked: number;
  refused_by_reason: Record<string, number>;
  tokens: { input: number; output: number };
}

export interface MeasureOptions {
  heldout: string;
  out: string;
  date: string;
  maxQuestions: number;
  model?: string;
  effort?: string;
  /** Injected for a test, and by `--replies`. The default asks for real and
   * reads the key at the first call, never at import. */
  transport?: LabelTransport;
  /** Plan and report what would be asked, ask nothing and write nothing. */
  planOnly?: boolean;
  log?: (line: string) => void;
}

export async function labelMeasure(root: string, options: MeasureOptions): Promise<Record<string, unknown>> {
  const log = options.log ?? ((line: string) => console.error(line));
  const rows = readHeldout(options.heldout);
  const model = options.model ?? DEFAULT_MODEL;
  const effort = options.effort ?? DEFAULT_EFFORT;

  const kinds = new Set<string>([...systemKinds, ...assessmentKinds]);
  const named = [...kinds].sort().flatMap((kind) => readKind(kind)) as {
    id: string; kind: string; name?: string; source_ids?: string[]; links?: { relation: string; target_id: string }[];
  }[];
  const sourceRecords = readKind("source") as { id: string; name?: string; attributes?: Record<string, unknown> }[];
  const titleOf = new Map(sourceRecords.map((record) => [record.id, record.name ?? String((record.attributes ?? {}).title ?? record.id)]));

  // The two indexes, exactly as label-evaluate builds them. The lexical one is
  // the same records with the store's citations removed, which is what a source
  // nobody has extracted looks like to the filter.
  const indexes: Record<Pass, ShortlistIndex> = {
    both_rules: buildShortlistIndex(named, sourceRecords as { id: string; links?: { relation: string; target_id: string }[] }[]),
    lexical_only: buildShortlistIndex(named.map((record) => ({ ...record, source_ids: [] })), []),
  };

  // Rebuild the tables of every source the frozen set names, and join on
  // table_id, which is a digest of the source, the layer and the anchor.
  const decider = buildDecider(named);
  const tableById = new Map<string, LabelTable>();
  const sourceFailures: { source: string; message: string }[] = [];
  for (const source of [...new Set(rows.map((row) => row.source))].sort()) {
    try {
      const { candidates } = extractSource(source, decider);
      for (const table of tablesOf(candidates)) tableById.set(table.table_id, table);
    } catch (error) {
      sourceFailures.push({ source, message: (error as Error).message });
    }
  }

  const layerIndexes = new Map<string, LayerIndex | null>();
  const layerIndex = (source: string, sha: string): LayerIndex | null => {
    if (!layerIndexes.has(sha)) {
      const record = layersForSource(source).find((layer) => layer.layer_sha256 === sha);
      layerIndexes.set(sha, record ? indexLayer(layerText(record), record.layer_sha256, record.normaliser) : null);
    }
    return layerIndexes.get(sha) ?? null;
  };

  const plan = planQuestions({
    rows,
    tableOf: (row) => tableById.get(row.table_id) ?? null,
    shortlistOf: (pass, table) => shortlistFor(indexes[pass], table),
    haveLayer: (table) => layerIndex(table.source_id, table.layer_sha256) !== null,
    cap: options.maxQuestions,
  });

  // The pre-filter, over the tables this build rebuilt, counted per rule.
  const shortlistOf = (pass: Pass) => {
    let holds = 0, lacks = 0, empty = 0, tables = 0;
    for (const row of rows) {
      const table = tableById.get(row.table_id);
      if (!table) continue;
      tables += 1;
      const ids = shortlistFor(indexes[pass], table).ids;
      if (ids.length === 0) empty += 1;
      else if (row.truth_ids.some((id) => ids.includes(id))) holds += 1;
      else lacks += 1;
    }
    return { tables, holds_truth: holds, lacks_truth: lacks, empty, miss: lacks + empty };
  };

  if (options.planOnly) {
    const planned = {
      generated: options.date,
      heldout: path.basename(options.heldout),
      asked_nothing: true,
      model, effort,
      cap: plan.cap,
      questions_planned: plan.questions.length,
      not_asked_because_of_the_cap: plan.not_asked_cap,
      by_pass: Object.fromEntries(PASSES.map((pass) => [pass, { ...plan.by_pass[pass], shortlist: shortlistOf(pass) }])),
      sources_that_would_not_rebuild: sourceFailures,
    };
    console.log(JSON.stringify(planned, null, 2));
    return planned;
  }

  // Everything above is read only. From here the run asks, and every write is
  // under options.out.
  fs.mkdirSync(options.out, { recursive: true });
  const prefix = path.join(options.out, `label-measurement-${options.date}`);
  // Its own prefix, not the report's: a glob for the report's .json would
  // otherwise match the cache as well.
  const cacheFile = path.join(options.out, `label-measure-cache-${options.date}.json`);
  const cache = readCache(cacheFile);
  const prompt = loadPrompt(root);
  const guard = cappedTransport(options.transport ?? liveTransport(), plan.cap);

  const scored: { question: Question; outcome: LabelOutcome; score: Score }[] = [];
  const results: PassResult[] = [];

  try {
  for (const pass of PASSES) {
    const questions = plan.questions.filter((question) => question.pass === pass);
    log(`${pass}: asking ${questions.length} of ${plan.by_pass[pass].askable} askable tables`);
    const { outcomes, receipt } = await labelTables({
      tables: questions.map((question) => question.table),
      shortlistIndex: indexes[pass],
      sourceTitle: (id) => titleOf.get(id) ?? id,
      layerIndex: (sha) => {
        const owner = questions.find((question) => question.table.layer_sha256 === sha);
        return owner ? layerIndex(owner.table.source_id, sha) : null;
      },
      transport: guard.transport,
      prompt,
      cache,
      model,
      effort,
    });

    const byTable = new Map(questions.map((question) => [question.table.table_id, question]));
    const result: PassResult = {
      pass,
      title: PASS_TITLE[pass],
      plan: plan.by_pass[pass],
      shortlist: shortlistOf(pass),
      asked: outcomes.length,
      correct: 0, wrong: 0, abstained: 0, refused: 0,
      abstained_on_multi_assessment_tables: 0,
      multi_assessment_tables_asked: 0,
      refused_by_reason: receipt.refusals_by_reason,
      tokens: receipt.tokens,
    };
    for (const outcome of outcomes) {
      const question = byTable.get(outcome.table_id);
      if (!question) continue;
      const score = scoreOutcome(question.row, outcome);
      result[score] += 1;
      if (question.row.truth_count !== 1) {
        result.multi_assessment_tables_asked += 1;
        if (score === "abstained") result.abstained_on_multi_assessment_tables += 1;
      }
      scored.push({ question, outcome, score });
    }
    results.push(result);
  }
  } finally {
    // Answers that were paid for are kept whatever else went wrong, so a rerun
    // reads them back instead of buying them again.
    writeCache(cacheFile, cache);
  }

  // The cap, checked after the fact. The plan truncated before anything was
  // built and the guard refused anything past it, so this can only fail if one
  // of the two stopped working, and it fails the run rather than reading as a
  // refusal on a line.
  const asked = guard.calls();
  if (guard.refused() > 0)
    throw new Error(
      `The run tried to ask ${asked + guard.refused()} questions against a cap of ${plan.cap}. The plan stopped bounding the cost, ` +
        "so the report is not written and the rates it would have carried are not trustworthy.",
    );

  const tokens = {
    input: results.reduce((total, result) => total + result.tokens.input, 0),
    output: results.reduce((total, result) => total + result.tokens.output, 0),
  };

  const answers = [[
    "pass", "source", "table_id", "truth_count", "scored_answer", "answered", "outcome", "score",
    "confidence", "refusal", "shortlist_size", "shortlist_holds_truth", "quote",
  ].join("\t")];
  for (const { question, outcome, score } of scored) {
    const ids = shortlistFor(indexes[question.pass], question.table).ids;
    answers.push([
      question.pass, question.row.source, question.row.table_id, String(question.row.truth_count), question.row.scored_answer,
      outcome.answer?.record_id ?? "", outcome.outcome, score, outcome.answer?.confidence ?? "", outcome.reason ?? "",
      String(ids.length), question.row.truth_ids.some((id) => ids.includes(id)) ? "1" : "0",
      JSON.stringify((outcome.answer?.quote ?? "").slice(0, 160)),
    ].join("\t"));
  }
  fs.writeFileSync(`${prefix}-answers.tsv`, `${answers.join("\n")}\n`);

  const summary = {
    generated: options.date,
    heldout: path.basename(options.heldout),
    heldout_rows: rows.length,
    heldout_rows_rebuilt: rows.filter((row) => tableById.has(row.table_id)).length,
    tables_built_over_those_sources: tableById.size,
    sources_that_would_not_rebuild: sourceFailures,
    model, effort,
    prompt: { id: prompt.id, path: prompt.path, sha256: prompt.sha256 },
    cost: {
      cap: plan.cap,
      questions_asked: asked,
      questions_not_asked_because_of_the_cap: plan.not_asked_cap,
      input_tokens: tokens.input,
      output_tokens: tokens.output,
      transport_failures: results.reduce((total, result) => total + (result.refused_by_reason.transport_failed ?? 0), 0),
    },
    // No combined object, on purpose. The two rules bound different things and
    // a reader who wants one number has to pick a rule and carry its name.
    by_pass: Object.fromEntries(results.map((result) => [result.pass, result])),
  };
  fs.writeFileSync(`${prefix}.json`, `${JSON.stringify(summary, null, 2)}\n`);
  fs.writeFileSync(`${prefix}.md`, report(summary, results, options));

  const lost = results.reduce((total, result) => total + (result.refused_by_reason.transport_failed ?? 0), 0);
  if (lost > 0) log(`${lost} of ${asked} questions failed in the transport rather than being answered. Those are a job fault, not a rate.`);
  log(`questions asked ${asked} of a cap of ${plan.cap}; input tokens ${tokens.input}, output tokens ${tokens.output}`);
  log(`wrote ${prefix}.md, ${prefix}.json, ${prefix}-answers.tsv`);
  return summary;
}

/** The prose report. Each rule gets its own section with its own denominators,
 * and no sentence anywhere puts the two rules' numbers in one row. */
function report(summary: Record<string, unknown>, results: PassResult[], options: MeasureOptions): string {
  const cost = summary.cost as { cap: number; questions_asked: number; questions_not_asked_because_of_the_cap: number; input_tokens: number; output_tokens: number; transport_failures: number };
  const lines: string[] = [];
  lines.push(`# Label stage: measured answers, ${options.date}`, "");
  lines.push(
    "The label stage decides one field: which benchmark or task a table reports. This report is the",
    "stage asked for real, scored against the answers frozen in",
    `\`${summary.heldout}\` before any answer existed.`,
    "",
  );
  lines.push("## Read the two sections apart", "");
  lines.push(
    "The pre-filter that puts records in front of the stage is two rules, and they bound different",
    "things. `cites_this_source` holds where the store already records that a record names this",
    "source, which is true only of sources somebody has already extracted. `name_in_table` holds",
    "where the words of a record's name are printed in the table, and it is the only rule that can",
    "reach a paper nothing in the store points at.",
    "",
    "Each rule has its own section below, its own denominators and its own run of questions. The",
    "first section's numbers do not apply to a new source and must not be quoted as if they did.",
    "",
  );
  lines.push("## What it cost", "");
  lines.push("| Item | Value |", "| --- | --- |");
  lines.push(`| Questions asked | ${cost.questions_asked} |`);
  lines.push(`| Cap this run was given | ${cost.cap} |`);
  lines.push(`| Askable questions the cap left unasked | ${cost.questions_not_asked_because_of_the_cap} |`);
  lines.push(`| Input tokens | ${cost.input_tokens} |`);
  lines.push(`| Output tokens | ${cost.output_tokens} |`);
  lines.push(`| Tables in the frozen set | ${summary.heldout_rows} |`);
  lines.push(`| Frozen tables this build reproduced | ${summary.heldout_rows_rebuilt} |`);
  lines.push(`| Transport failures, which are a job fault and not a stage result | ${cost.transport_failures} |`);
  lines.push("");

  for (const result of results) {
    lines.push(`## ${result.title}`, "");
    lines.push(
      `Rule: \`${result.pass === "both_rules" ? "cites_this_source or name_in_table" : "name_in_table"}\`.`,
      "",
    );
    lines.push("### Does the shortlist hold the right answer at all", "");
    lines.push(`Denominator: the ${result.shortlist.tables} tables of the frozen set this build rebuilt.`, "");
    lines.push("| Outcome | Rate |", "| --- | --- |");
    lines.push(`| Shortlist holds a truth record | ${rate(result.shortlist.holds_truth, result.shortlist.tables)} |`);
    lines.push(`| Shortlist offered records, none of them right | ${rate(result.shortlist.lacks_truth, result.shortlist.tables)} |`);
    lines.push(`| Shortlist offered nothing, so nothing was asked | ${rate(result.shortlist.empty, result.shortlist.tables)} |`);
    lines.push(`| Shortlist miss, the two above together | ${rate(result.shortlist.miss, result.shortlist.tables)} |`);
    lines.push("");
    lines.push("### What the stage answered", "");
    lines.push(`Denominator: the ${result.asked} questions asked under this rule.`, "");
    lines.push("| Outcome | Rate |", "| --- | --- |");
    lines.push(`| Correct label | ${rate(result.correct, result.asked)} |`);
    lines.push(`| Wrong label | ${rate(result.wrong, result.asked)} |`);
    lines.push(`| Abstained | ${rate(result.abstained, result.asked)} |`);
    lines.push(`| No label: the answer was refused, or the transport failed | ${rate(result.refused, result.asked)} |`);
    lines.push("");
    lines.push(
      `Questions about a table reporting more than one assessment: ${result.multi_assessment_tables_asked} of ${result.asked}.`,
      `No single label can be right on one of those and abstaining is the only correct answer; the stage`,
      `abstained on ${result.abstained_on_multi_assessment_tables}. Those abstentions are counted in the abstained row above and not in the`,
      "correct row, so the correct rate is labels only.",
      "",
    );
    const refusals = Object.entries(result.refused_by_reason).sort((a, b) => b[1] - a[1]);
    if (refusals.length) {
      lines.push("Refusals by reason:", "");
      lines.push("| Reason | Count |", "| --- | --- |");
      for (const [reason, count] of refusals) lines.push(`| \`${reason}\` | ${count} |`);
      lines.push("");
    }
    lines.push(
      `Questions this rule could have asked but the cap did not reach: ${result.plan.askable - result.asked} of ${result.plan.askable}.`,
      "",
    );
  }

  lines.push("## What this run could not do", "");
  lines.push(
    "It wrote a report. It holds no path to the record store: every file it wrote is under the",
    "report directory, the only record-store function it imports is `readKind`, and the job that",
    "runs it holds a read-only token. `tests/omics-extract-label-measure.test.ts` checks the first",
    "two against this command's own source.",
    "",
  );
  return `${lines.join("\n")}\n`;
}

/** A transport that answers from a recording, for a rerun that opens no socket.
 * Re-exported so the command can offer `--replies` the way the extract command
 * does. */
export { recordedTransport };
