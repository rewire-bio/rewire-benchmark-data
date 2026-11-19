/** The one stage of the extraction pipeline that asks anything outside this repository.
 *
 * ADR 0002 permits exactly one, and this is it. Everything else in `shared/omics/extract` is a
 * lookup against a label somebody already wrote down, and every span and every value in a
 * candidate file can be re-checked on a fresh clone with nothing but the layer bytes. That stays true
 * after this stage runs, because of what this stage is not allowed to touch.
 *
 * The safety property, stated once:
 *
 *   The stage is never given a number. It is given the words a document prints around a table
 *   and a shortlist of records the store already holds, and asked which one the table is
 *   about. A hallucination therefore cannot produce a wrong value. The worst it can do is
 *   attach a correct value to the wrong task, which is serious, which is what `check.ts`
 *   exists to catch, and which is what the evaluation has to measure.
 *
 * Nothing here writes a record, and nothing here writes into the candidate file. The
 * deterministic pass's output is a function of the archived bytes and the store, and it stays
 * that way: the stage's output is its own file, beside it, saying which candidates a label
 * would apply to and what was checked before it was allowed to. ADR 0002 decision 6 keeps
 * candidates in files for the same reason, one step earlier.
 *
 * Abstention is an answer. A table nothing can be said about leaves every candidate
 * unlabelled, with the reason recorded, and the receipt reports the rate. That rate is meant
 * to be high rather than low.
 */
import { readAnswer, type Answer } from "./answer";
import { cacheKey, labelCache, type CacheEntry, type LabelCache } from "./cache";
import { checkAnswer, type CheckResult, type LabelRefusal } from "./check";
import { renderQuestion, type Prompt } from "./prompt";
import { shortlistFor, type Shortlist, type ShortlistIndex } from "./shortlist";
import type { LabelTable } from "./table";
import {
  DEFAULT_EFFORT,
  DEFAULT_MAX_TOKENS,
  DEFAULT_MODEL,
  type LabelReply,
  type LabelRequest,
  type LabelTransport,
} from "./transport";
import { answerJsonSchema } from "./answer";
import type { LayerIndex } from "../../spans/offsets";
import type { Span } from "../../locator";

export * from "./answer";
export * from "./cache";
export * from "./check";
export * from "./prompt";
export * from "./shortlist";
export * from "./table";
export * from "./transport";

/** The shortest caption the stage will ask about. A label of three characters or fewer is not
 * a quote anything can be checked against, and `check.ts` would refuse the answer anyway, so
 * the question is not asked and the cost is not paid. */
export const ANCHOR_MINIMUM = 4;

/** What one table came to, with everything a reader needs to disagree. */
export interface LabelOutcome {
  table_id: string;
  source_id: string;
  layer_sha256: string;
  anchor: LabelTable["anchor"];
  /** The caption or label the question printed, which is the only text an answer may quote. */
  anchor_text: string;
  /** The candidates a label applies to. */
  candidate_ids: string[];
  shortlist: Shortlist;
  /** False where a precondition stopped the question being asked at all. */
  asked: boolean;
  /** True where the answer was read back from the cache rather than asked for. */
  cached: boolean;
  answer: Answer | null;
  outcome: "labelled" | "abstained" | "refused";
  record_id: string | null;
  /** Where the quoted evidence is in the source's own layer. */
  span: Span | null;
  reason: LabelRefusal | null;
  detail: string;
  checks: CheckResult[];
}

/** The receipt ADR 0002 decision 12 requires, and the sentence it requires it not to overclaim
 * with. */
export interface LabelReceipt {
  stage: "label";
  /** What a label is. The receipt says this rather than leaving it to be inferred, because a
   * machine-readable field saying `labelled` reads like a fact and is not one. */
  statement: string;
  model: string;
  prompt: { id: string; path: string; sha256: string };
  effort: string;
  max_tokens: number;
  /** Where the shortlist, the answer and the checks for each table are written, one line
   * each. The receipt totals them; it does not restate them, because a receipt that repeats a
   * file can disagree with it. */
  per_table: string;
  tables: number;
  asked: number;
  from_cache: number;
  labelled: number;
  abstained: number;
  refused: number;
  /** Candidates a label applies to, which is what the coverage gained actually is. */
  candidates_labelled: number;
  refusals_by_reason: Record<string, number>;
  /** The pre-filter, measured over the tables this run saw. */
  shortlist: {
    considered: number;
    /** Tables the filter offered nothing for, which can never be labelled. */
    empty: number;
    min: number;
    median: number;
    max: number;
    mean: number;
  };
  tokens: { input: number; output: number };
}

/** Where `labelTables` says the per-table lines are written. The caller writes the file; this
 * is the path the receipt names, so the two cannot drift apart silently. */
export const PER_TABLE_FILE = "extract/stages/label.jsonl";

export const RECEIPT_STATEMENT =
  "A label on this file is a machine judgement about what a table is about, made from the words printed around it and checked against a span in the source's own text layer. It is not a verified fact, and nothing here was read by a person. The value, the metric and the span beside it were decided deterministically and can be re-checked from the layer bytes alone.";

const median = (values: number[]): number => {
  if (values.length === 0) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const middle = sorted.length >> 1;
  return sorted.length % 2 === 1 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
};

export interface LabelRun {
  tables: LabelTable[];
  shortlistIndex: ShortlistIndex;
  /** The source's own title, as the store's source record names it. */
  sourceTitle: (sourceId: string) => string;
  /** The indexed text layer a span would be taken in, or null where the run does not hold it. */
  layerIndex: (layerSha256: string) => LayerIndex | null;
  transport: LabelTransport;
  prompt: Prompt;
  cache?: LabelCache;
  model?: string;
  effort?: string;
  maxTokens?: number;
}

/**
 * Ask about every table, check every answer, and record what happened to each.
 *
 * Tables arrive sorted by id and are processed in that order, one at a time. One at a time
 * because the cache and the token counts are read and written per table and a receipt that
 * counted them out of order would be harder to reconcile than the run is slow.
 */
export async function labelTables(run: LabelRun): Promise<{ outcomes: LabelOutcome[]; receipt: LabelReceipt }> {
  const model = run.model ?? DEFAULT_MODEL;
  const effort = run.effort ?? DEFAULT_EFFORT;
  const max_tokens = run.maxTokens ?? DEFAULT_MAX_TOKENS;
  const cache = run.cache ?? labelCache();
  const outcomes: LabelOutcome[] = [];
  const tokens = { input: 0, output: 0 };
  let asked = 0;
  let fromCache = 0;

  for (const table of run.tables) {
    const shortlist = shortlistFor(run.shortlistIndex, table);
    const base = {
      table_id: table.table_id,
      source_id: table.source_id,
      layer_sha256: table.layer_sha256,
      anchor: table.anchor,
      anchor_text: table.anchor_text,
      candidate_ids: table.candidate_ids,
      shortlist,
      asked: false,
      cached: false,
      answer: null,
      record_id: null,
      span: null,
      checks: [] as CheckResult[],
    };
    const stop = (reason: LabelRefusal, detail: string): LabelOutcome => ({ ...base, outcome: "refused", reason, detail });

    // Preconditions. None of these asks anything, and each is a fact about the table or the
    // store rather than a verdict on it.
    if (table.decided.length > 0) {
      outcomes.push(stop("already_decided", `the deterministic pass decided ${table.decided.join(", ")} on this table`));
      continue;
    }
    if (table.anchor_text.trim().length < ANCHOR_MINIMUM) {
      outcomes.push(stop("no_anchor_text", "the document prints no caption or label for this table"));
      continue;
    }
    if (shortlist.ids.length === 0) {
      outcomes.push(stop("empty_shortlist", `no record of a result-carrying kind matched, of ${shortlist.considered} held`));
      continue;
    }
    const index = run.layerIndex(table.layer_sha256);
    if (!index) {
      outcomes.push(stop("quote_unresolved", `the run does not hold layer ${table.layer_sha256.slice(0, 12)}, so no quote could be checked`));
      continue;
    }

    const request: LabelRequest = {
      model,
      effort,
      max_tokens,
      system: run.prompt.text,
      question: renderQuestion({ table, shortlist, sourceTitle: run.sourceTitle(table.source_id) }),
      schema: answerJsonSchema,
    };
    const key = cacheKey({
      layer_sha256: table.layer_sha256,
      extent: table.extent,
      prompt_sha256: run.prompt.sha256,
      shortlist: shortlist.ids,
      model,
    });

    let reply: LabelReply;
    const held = cache.get(key);
    if (held) {
      reply = held.reply;
      fromCache += 1;
    } else {
      try {
        reply = await run.transport(request);
      } catch (error) {
        outcomes.push({ ...stop("transport_failed", (error as Error).message), asked: true });
        continue;
      }
      asked += 1;
      const entry: CacheEntry = {
        asked: {
          layer_sha256: table.layer_sha256,
          extent: table.extent,
          prompt_sha256: run.prompt.sha256,
          shortlist: shortlist.ids,
          model,
          table_id: table.table_id,
          source_id: table.source_id,
        },
        reply,
      };
      cache.set(key, entry);
      // Counted only where the question was asked. A rerun that reads every answer back spent
      // nothing, and a receipt that restated the first run's spend would be claiming a cost
      // that was not paid.
      tokens.input += reply.input_tokens ?? 0;
      tokens.output += reply.output_tokens ?? 0;
    }

    const read = readAnswer(reply.text);
    if (!read.ok) {
      outcomes.push({ ...stop("answer_malformed", read.detail), asked: true, cached: held !== undefined });
      continue;
    }
    const record = run.shortlistIndex.records.get(read.answer.record_id) ?? null;
    const checked = checkAnswer({
      table,
      shortlist,
      answer: read.answer,
      index,
      record: record ? { id: record.id, kind: record.kind } : null,
      names: run.shortlistIndex.namesOf.get(read.answer.record_id) ?? [],
    });

    outcomes.push({
      ...base,
      asked: true,
      cached: held !== undefined,
      answer: read.answer,
      outcome: checked.outcome,
      record_id: checked.outcome === "labelled" ? checked.record_id : null,
      span: checked.outcome === "labelled" ? checked.span : null,
      reason: checked.outcome === "refused" ? checked.reason : null,
      detail: checked.outcome === "refused" ? checked.detail : read.answer.reason,
      checks: checked.checks,
    });
  }

  const refusals: Record<string, number> = {};
  for (const outcome of outcomes) if (outcome.outcome === "refused" && outcome.reason) refusals[outcome.reason] = (refusals[outcome.reason] ?? 0) + 1;
  const sizes = outcomes.map((outcome) => outcome.shortlist.ids.length);

  return {
    outcomes,
    receipt: {
      stage: "label",
      statement: RECEIPT_STATEMENT,
      model,
      prompt: { id: run.prompt.id, path: run.prompt.path, sha256: run.prompt.sha256 },
      effort,
      max_tokens,
      per_table: PER_TABLE_FILE,
      tables: outcomes.length,
      asked,
      from_cache: fromCache,
      labelled: outcomes.filter((outcome) => outcome.outcome === "labelled").length,
      abstained: outcomes.filter((outcome) => outcome.outcome === "abstained").length,
      refused: outcomes.filter((outcome) => outcome.outcome === "refused").length,
      candidates_labelled: labelsByCandidate(outcomes).size,
      refusals_by_reason: refusals,
      shortlist: {
        considered: run.shortlistIndex.considered,
        empty: sizes.filter((size) => size === 0).length,
        min: sizes.length ? Math.min(...sizes) : 0,
        median: median(sizes),
        max: sizes.length ? Math.max(...sizes) : 0,
        mean: sizes.length ? Number((sizes.reduce((total, size) => total + size, 0) / sizes.length).toFixed(2)) : 0,
      },
      tokens,
    },
  };
}

/**
 * The label each candidate would take, for a later stage that promotes one.
 *
 * Only a labelled outcome contributes, and the caller is handed the table and the span with
 * it, so a promotion can say where the judgement came from rather than only what it was.
 */
export function labelsByCandidate(outcomes: LabelOutcome[]): Map<string, { record_id: string; table_id: string; span: Span }> {
  const out = new Map<string, { record_id: string; table_id: string; span: Span }>();
  for (const outcome of outcomes) {
    if (outcome.outcome !== "labelled" || !outcome.record_id || !outcome.span) continue;
    for (const id of outcome.candidate_ids) out.set(id, { record_id: outcome.record_id, table_id: outcome.table_id, span: outcome.span });
  }
  return out;
}
