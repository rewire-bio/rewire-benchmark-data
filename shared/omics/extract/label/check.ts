/** What has to be true before an answer is used, and what happens when it is not.
 *
 * The stage never sees a number, so a wrong answer cannot put a wrong value in the store. What
 * it can do is attach a correct value to the wrong task, which is still a false statement in a
 * public catalogue and is what these checks exist to catch. Each one is deterministic, each
 * one is testable on its own, and a failure drops the answer rather than weakening it.
 *
 * The order is deliberate: the cheap checks that need nothing but the answer come before the
 * ones that read the store, and the one that reads the layer comes last. A failure stops the
 * sequence, so a receipt names the first thing that was wrong rather than all of them.
 *
 *   pass_decided_nothing     the deterministic pass left this field empty on every candidate
 *   id_on_shortlist          the id is one that was offered, not one that was composed
 *   record_exists            the id names a record the store holds
 *   kind_carries_results     that record is a benchmark, a task or a protocol
 *   quote_in_caption         the quoted words are in the caption the question printed
 *   quote_resolves_to_span   those words are at one place in the source's own text layer
 *   confidence_justified     a high confidence quotes words that name the record
 *
 * Refusal is cheap and is meant to be common. An unlabelled table costs coverage, which is
 * work left to do and is visible as work. A wrongly labelled one corrupts the graph and reads
 * as a check that passed.
 */
import { normaliseLabel } from "../../spans/table";
import { resolveQuote } from "../../spans/prose";
import type { LayerIndex } from "../../spans/offsets";
import type { Span } from "../../locator";
import { assessmentKinds } from "../decide";
import { NONE, type Answer } from "./answer";
import type { Shortlist } from "./shortlist";
import type { LabelTable } from "./table";

/** Why a table carries no label. Every one is a fact about the answer, the store or the layer,
 * never a verdict on the table. */
export const labelRefusals = [
  /** The document prints nothing this stage could quote, so the question was never asked. */
  "no_anchor_text",
  /** The deterministic pass had already decided the field. Never asked. */
  "already_decided",
  /** The pre-filter offered no record. Never asked, and the pre-filter's own measurement. */
  "empty_shortlist",
  /** The transport failed or returned nothing. */
  "transport_failed",
  /** The reply is not JSON, or not the four fields. */
  "answer_malformed",
  /** The id was not on the shortlist the question printed. */
  "not_in_shortlist",
  /** The id is on the shortlist and names no record, which means the shortlist is stale. */
  "record_not_found",
  /** The record is not of a kind that can carry results. */
  "kind_cannot_carry_results",
  /** The quoted words are not in the caption the question printed. */
  "quote_not_in_caption",
  /** The quoted words do not resolve to one span in the source's own layer. */
  "quote_unresolved",
  /** A high confidence whose quote does not name the record. */
  "confidence_unjustified",
] as const;
export type LabelRefusal = (typeof labelRefusals)[number];

/** One check, as the receipt records it. */
export interface CheckResult {
  check: string;
  passed: boolean;
  /** For a reader of the receipt. Never parsed. */
  detail: string;
}

export type Checked =
  | { outcome: "labelled"; record_id: string; span: Span; checks: CheckResult[] }
  /** The stage said it could not tell. Not a refusal: a stated answer with no label. */
  | { outcome: "abstained"; checks: CheckResult[] }
  | { outcome: "refused"; reason: LabelRefusal; detail: string; checks: CheckResult[] };

/** Runs of whitespace collapsed to one space, and nothing else relaxed.
 *
 * A caption printed across two lines of a text layer carries a newline nobody typed, so a
 * quote copied from it will not match it character for character. That is the only difference
 * allowed. Case is not relaxed: a quote is text copied from the caption, and letting "AUROC"
 * match "auroc" would admit a quote the caption does not print. This is a comparison of two
 * short strings, not a search over a layer; the search is `resolveQuote`, which is the span
 * machinery and is called below rather than reimplemented. */
export const collapse = (text: string): string => text.replace(/\s+/g, " ").trim();

/** Whether the quote is in the caption the question printed. */
export const quoteInCaption = (quote: string, caption: string): boolean => {
  const wanted = collapse(quote);
  return wanted !== "" && collapse(caption).includes(wanted);
};

/** Whether the quoted words name the record, which is what a high confidence claims. */
export function quoteNamesRecord(quote: string, names: string[]): boolean {
  const said = normaliseLabel(quote);
  return names.some((name) => name !== "" && said.includes(name));
}

/** The shortest text a quote may be. Below four characters a quote addresses nothing, which is
 * where `resolveQuote` refuses too, so the stage refuses for the same reason in its own words
 * rather than passing a string the resolver will reject. */
export const QUOTE_MINIMUM = 4;

export interface CheckInput {
  table: LabelTable;
  shortlist: Shortlist;
  answer: Answer;
  /** The source's own text layer, indexed. The span the answer earns is taken here. */
  index: LayerIndex;
  /** The record the id names, or null where the store holds none. */
  record: { id: string; kind: string } | null;
  /** That record's printed names, normalised, for the confidence check. */
  names: string[];
}

/** Everything that has to be true, in order, for an answer to become a label. */
export function checkAnswer(input: CheckInput): Checked {
  const checks: CheckResult[] = [];
  const refuse = (reason: LabelRefusal, detail: string): Checked => ({ outcome: "refused", reason, detail, checks });
  const record = (check: string, passed: boolean, detail: string) => {
    checks.push({ check, passed, detail });
    return passed;
  };

  if (!record("pass_decided_nothing", input.table.decided.length === 0, input.table.decided.join(", ")))
    return refuse("already_decided", `the deterministic pass decided ${input.table.decided.join(", ")} on this table`);

  if (input.answer.record_id === NONE) {
    checks.push({ check: "answered_none", passed: true, detail: input.answer.reason });
    return { outcome: "abstained", checks };
  }

  if (!record("id_on_shortlist", input.shortlist.ids.includes(input.answer.record_id), input.answer.record_id))
    return refuse("not_in_shortlist", `${input.answer.record_id} was not on the shortlist of ${input.shortlist.ids.length}`);

  if (!record("record_exists", input.record !== null, input.answer.record_id))
    return refuse("record_not_found", `the store holds no record called ${input.answer.record_id}`);

  const kind = input.record!.kind;
  if (!record("kind_carries_results", (assessmentKinds as readonly string[]).includes(kind), kind))
    return refuse("kind_cannot_carry_results", `${input.answer.record_id} is a ${kind}, and a result is carried by a ${assessmentKinds.join(", ")}`);

  if (!record("quote_in_caption", quoteInCaption(input.answer.quote, input.table.anchor_text), input.answer.quote))
    return refuse("quote_not_in_caption", `the quoted text is not in the caption this table prints`);

  if (collapse(input.answer.quote).length < QUOTE_MINIMUM) {
    checks.push({ check: "quote_resolves_to_span", passed: false, detail: "under four characters" });
    return refuse("quote_unresolved", `a quote under ${QUOTE_MINIMUM} characters addresses nothing`);
  }

  const resolved = resolveQuote(input.index, input.answer.quote);
  if (!record("quote_resolves_to_span", resolved.ok, resolved.ok ? resolved.span.exact : resolved.reason))
    return refuse("quote_unresolved", `the quoted text does not resolve in layer ${input.index.layer_sha256.slice(0, 12)}: ${(resolved as { reason: string; detail: string }).reason}, ${(resolved as { detail: string }).detail}`);

  const justified = input.answer.confidence !== "high" || quoteNamesRecord(input.answer.quote, input.names);
  if (!record("confidence_justified", justified, input.answer.confidence))
    return refuse("confidence_unjustified", `a high confidence whose quote does not name ${input.answer.record_id}`);

  return { outcome: "labelled", record_id: input.answer.record_id, span: (resolved as { span: Span }).span, checks };
}
