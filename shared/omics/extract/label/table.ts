/** The unit of work: one table, never one candidate.
 *
 * Every candidate the deterministic pass reads out of a table carries the same caption, the
 * same label and the same column headings. The field none of them decides is which benchmark
 * or task the table reports, and that field is a property of the table. Asking it once per
 * cell would multiply the cost by the number of cells and could answer one table two ways,
 * which is a table nobody could check. So the candidates are grouped and the question is asked
 * once.
 *
 * The group key is the source, the layer, the anchor kind and the anchor index: exactly what
 * `shared/omics/extract/candidate.ts` writes on each candidate to say which table it came from.
 *
 * Nothing here reads a number. The table carries the words the document prints around its
 * cells, the span its cells occupy in the layer, and the ids of the candidates that would take
 * the label. The printed values stay in the candidate file where the deterministic pass left
 * them.
 */
import { createHash } from "node:crypto";
import type { Candidate } from "../candidate";

/** How many distinct column headings travel with the question.
 *
 * A supplementary sheet can print hundreds of columns, and a shortlist is decided from the
 * table's subject rather than from its full width. The cap is here so the question has a
 * bounded size over an unbounded table, and the count of headings held back is carried on the
 * table so the receipt can state what was not shown. */
export const COLUMN_HEADERS_SHOWN = 24;
/** How many distinct row labels travel with the question, for the same reason. */
export const ROW_LABELS_SHOWN = 12;

/** The separator between the levels of a stacked column heading.
 *
 * `shared/omics/extract/decide.ts` writes the levels of a heading this way in the evidence it
 * records on an undecided field. Using the same separator means a heading reads the same in
 * the question as it does in `questions.jsonl`, and both are visibly a rendering of several
 * printed strings rather than one string the document prints. */
export const LEVEL_SEPARATOR = " | ";

export interface LabelTable {
  /** Stable over reruns: a digest of the source, the layer and the anchor. */
  table_id: string;
  source_id: string;
  layer_sha256: string;
  anchor: Candidate["anchor"];
  /** The words the document prints to name this table: the caption where it prints one, the
   * label otherwise. This is the only text an answer may quote. */
  anchor_text: string;
  /** Which of the two `anchor_text` was taken from, so a reader knows what was quoted. */
  anchor_text_from: "caption" | "label" | "none";
  /** Distinct column headings in column order, each heading's levels joined by
   * `LEVEL_SEPARATOR`, capped at `COLUMN_HEADERS_SHOWN`. */
  column_headers: string[];
  /** Distinct, non-empty row labels in row order, capped at `ROW_LABELS_SHOWN`. */
  row_labels: string[];
  /** Headings and labels that did not travel with the question, counted rather than dropped
   * silently: `column_headers` and `row_labels` are what the caps held back, and `numeric` is
   * what `namesOnly` refused to print. */
  held_back: { column_headers: number; row_labels: number; numeric: number };
  /** The first and last code point the table's own cells occupy in the layer. The cache is
   * keyed on this, so the same table is never asked about twice. */
  extent: { start: number; end: number };
  /** The candidates this table holds, sorted, which is what an accepted label applies to. */
  candidate_ids: string[];
  /** Candidates whose assessment the deterministic pass already decided. A table with any of
   * these is never asked about: the stage may not change a field the pass decided. */
  decided: string[];
}

const digest = (parts: string[]): string =>
  createHash("sha256").update(parts.join("\u0000")).digest("hex").slice(0, 16);

const keyOf = (candidate: Candidate): string =>
  [candidate.source_id, candidate.layer_sha256, candidate.anchor.kind, String(candidate.anchor.index)].join("\u0000");

/** The printed heading of one column, its levels top first, blanks dropped. */
const headingOf = (levels: string[]): string => levels.filter((level) => level.trim() !== "").join(LEVEL_SEPARATOR);

/**
 * Labels that print a name, which is everything with a letter in it.
 *
 * A sheet's first column is a row label by position and is sometimes a number: one layer in
 * the archive prints `0.633980785512857` where a row name would be, and a stacked column
 * heading can be a year or a cutoff. Those are not names, and printing one in the question
 * would be putting a figure from a cell in front of the stage for no gain. The test is a
 * letter rather than a numeric pattern, so `CASF-2016` and `AUROC (%)` travel and `12.5` and
 * `2016` do not.
 */
export const namesOnly = (labels: string[]): string[] => labels.filter((label) => /\p{L}/u.test(label));

/** Distinct values in first-seen order, which for candidates read in cell order is the order
 * the table prints them. */
function distinct(values: string[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const value of values) {
    if (value.trim() === "" || seen.has(value)) continue;
    seen.add(value);
    out.push(value);
  }
  return out;
}

/**
 * Every table the candidates came from, in a stable order.
 *
 * Tables are returned sorted by id, so a run over the same candidates asks the same questions
 * in the same order and a receipt diff means something changed.
 */
export function tablesOf(candidates: Candidate[]): LabelTable[] {
  const groups = new Map<string, Candidate[]>();
  for (const candidate of candidates) {
    const key = keyOf(candidate);
    const held = groups.get(key);
    if (held) held.push(candidate);
    else groups.set(key, [candidate]);
  }

  const tables: LabelTable[] = [];
  for (const group of groups.values()) {
    const first = group[0];
    const caption = first.anchor.caption.trim();
    const label = first.anchor.label.trim();
    const anchor_text = caption !== "" ? caption : label;
    const allHeaders = distinct(group.map((candidate) => headingOf(candidate.column_header)));
    const allLabels = distinct(group.map((candidate) => candidate.row_label));
    const headers = namesOnly(allHeaders);
    const labels = namesOnly(allLabels);
    const decided = [
      ...new Set(group.map((candidate) => candidate.assessment.decided).filter((id): id is string => id !== null)),
    ].sort();

    tables.push({
      table_id: digest([first.source_id, first.layer_sha256, first.anchor.kind, String(first.anchor.index)]),
      source_id: first.source_id,
      layer_sha256: first.layer_sha256,
      anchor: first.anchor,
      anchor_text,
      anchor_text_from: caption !== "" ? "caption" : label !== "" ? "label" : "none",
      column_headers: headers.slice(0, COLUMN_HEADERS_SHOWN),
      row_labels: labels.slice(0, ROW_LABELS_SHOWN),
      held_back: {
        column_headers: Math.max(0, headers.length - COLUMN_HEADERS_SHOWN),
        row_labels: Math.max(0, labels.length - ROW_LABELS_SHOWN),
        numeric: allHeaders.length - headers.length + (allLabels.length - labels.length),
      },
      extent: {
        start: Math.min(...group.map((candidate) => candidate.span.start)),
        end: Math.max(...group.map((candidate) => candidate.span.end)),
      },
      candidate_ids: group.map((candidate) => candidate.candidate_id).sort(),
      decided,
    });
  }
  return tables.sort((a, b) => (a.table_id < b.table_id ? -1 : a.table_id > b.table_id ? 1 : 0));
}
