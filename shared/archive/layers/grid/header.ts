/** A candidate header row, for a table whose markup marks none.
 *
 * Measured over the 1,156 tables the archive holds on 2026-11-18, 327 carry
 * no header row the markup marks, 319 of them HTML. Nearly all of those are
 * arXiv pages, where a table is written with `td` throughout and the heading
 * row is a heading only to a reader. The grid stores no heading for them, so
 * a resolver cannot name a column and 2,506 stored locators are refused
 * `column_not_found` against a table that has the column printed at the top
 * of it.
 *
 * The inference belongs here and not in a resolver. Here the markup is still
 * in hand and can contradict it: a table whose markup marks a header
 * elsewhere is declined outright, which a resolver reading a grid could not
 * do. And here it is recorded once, in bytes a reader can check, rather than
 * being re-derived differently by every resolver that wants a column.
 *
 * What is recorded is never a header the markup wrote. `header_rows` and
 * `headers` carry the marked header and nothing else, and a candidate goes in
 * `inferred_header` with the rule that chose it named in it. A reader can
 * always tell the two apart and a resolver can decline the second by looking
 * only at the field name.
 *
 * The rule, and what each test is for. A row is the candidate only when it is
 * the first row of the table and all of this holds.
 *
 *  1. The markup marks no header cell anywhere in the table unless it marks
 *     one on the first row, and it wrote no thead the first row is not in.
 *     Markup that says where the header is wins, and where it puts it
 *     somewhere else the answer is no candidate.
 *  2. Three columns and three rows. A two column table is as often a list of
 *     keys and values as a headed table, and the rule cannot tell those
 *     apart. Measured with two columns allowed it takes three data rows on
 *     the ground truth below rather than one, and two of the three are the
 *     first line of a two column hyperparameter list.
 *  3. The first row writes its own cell in every column, each spanning one
 *     row and one column. A spanning cell is the top level of a header with
 *     more than one level, and the deeper levels are where the column is
 *     actually named, so flattening it to the top level would name a heading
 *     that stands over several columns. Those tables stay refused.
 *  4. Every cell of the first row prints something, except that the first
 *     column may be blank, which is the empty corner over a stub.
 *  5. No cell of the first row prints a value. A heading names a column and
 *     a value is what the column holds, so a first row printing one is data.
 *  6. The first row prints no heading twice. Two columns under one heading
 *     are ambiguous to a resolver anyway.
 *  7. Some column prints values below the first row: at least two of them,
 *     and at least half of what that column prints. Without this a list of
 *     names and URLs reads as a headed table.
 *  8. The row under the first row prints a value. This is what tells one
 *     header row from two: a second header level prints names, not numbers,
 *     and the rule has no way to carry a second level.
 *
 * What it was measured against, and the two rates. The 829 tables whose
 * markup does mark a header are the ground truth. Run on those with the
 * marking ignored, the rule names a row for 382 of them: 379 times the row
 * the markup marks, and 3 times the first row of a header the markup marks
 * as two rows, where in two of the three the second marked row is a summary
 * line the markup put inside the thead. It never names a row the markup
 * leaves out of its header.
 *
 * The stronger test strips the marked header rows away and runs the rule on
 * the body alone, where every row it could name is a data row read as
 * headings, which is the failure that makes a resolver name the wrong column
 * and print a plausible wrong value. 714 of the stripped tables are big
 * enough for the rule to run on and it names a row in 1 of them, 0.14%, and
 * that one row is a line of column names the markup left out of its thead.
 *
 * Both rates are in maintenance/reports/grid-candidate-headers-2026-11-18.md
 * with the commands that produced them, together with what the looser value
 * tests cost. Counting a cell as a value because it begins with a digit buys
 * 24 more locators on the row below the first, and on both tests at once it
 * buys 303 and takes 16 of the stripped bodies instead of 1.
 */
import type { GridCell, GridInferredHeader } from "./types";

/** The rule that chose a candidate, recorded on it. A resolver that does not
 * trust a rule can decline it by name, and a later rule gets a new name
 * rather than changing what this one means. */
export const CANDIDATE_RULE = "first-row@1";

/** Why no candidate was recorded. Nothing is stored in the layer for a table
 * with no candidate, so these are what the function returns and what the
 * measurement counts, not a field. */
export const candidateDeclinedReasons = [
  "marked_elsewhere",
  "too_few_columns",
  "too_few_rows",
  "first_row_incomplete",
  "first_row_spans",
  "first_row_blank_cell",
  "first_row_prints_a_value",
  "first_row_repeats_a_heading",
  "no_column_of_values_below",
  "row_below_prints_no_value",
] as const;
export type CandidateDeclined = (typeof candidateDeclinedReasons)[number];

/** Columns and rows a table needs before the rule will look at it. */
const MIN_COLUMNS = 3;
const MIN_ROWS = 3;

/**
 * A number as a paper prints one: a comparator or a bracket, digits with
 * thousands separators and a decimal part, an exponent written as `e-4` or
 * as `x 10^-4`, a unit, and a closing bracket or a footnote mark.
 *
 * Deliberately a whole string test. A cell is a value when the whole of it is
 * a number, not when it starts with one: "19,237 raQTLs" and "10-cl./binary"
 * both start with a digit and both are headings a paper writes.
 */
const NUMBER =
  /^[([{<>\u2264\u2265~\u2248]*\s*[+\-\u2010\u2011\u2212]?\d[\d,\u00a0 ]*(?:\.\d+)?(?:\s*(?:[eE]|[\u00d7x]\s*10)\s*\^?\s*[+\-\u2010\u2011\u2212]?\d+)?(?:\s*(?:bp|kb|Mb|Gb|kB|MB|GB|min|ms|mM|nM|%|\u2030|[KkMGBbshm]))?[)\]}%*\u2020\u2021]*$/;

/** What a table prints where it has no value: a dash, a tick, a cross, or
 * one of the words for nothing. A heading is none of these. */
const PLACEHOLDERS = new Set([
  "-",
  "--",
  "\u2013",
  "\u2014",
  "\u2212",
  "n/a",
  "na",
  "nd",
  "ns",
  "yes",
  "no",
  "true",
  "false",
  "\u2713",
  "\u2714",
  "\u2715",
  "\u2716",
  "\u2717",
  "\u2718",
  "\u221a",
  "\u00d7",
  "\u2022",
]);

/** Where one part of a compound value ends and the next begins: a value
 * printed as "0.722 / 0.948", "76.1 {71.1\u201380.6}" or "0.020 \u00b1 3e-4" is
 * several numbers and a reader reads it as one value. */
const PARTS = /[\s\u00b1]*(?:\u00b1|\+\/-|\/|\u2013|\u2014|,|;|\u2192)\s*|\s+/;

/** Does this cell print a number, alone or as a compound of numbers? */
export function printsNumber(text: string): boolean {
  const trimmed = text.trim();
  if (trimmed === "") return false;
  if (NUMBER.test(trimmed)) return true;
  const parts = trimmed.split(PARTS).filter((part) => part.trim() !== "");
  return parts.length > 1 && parts.every((part) => NUMBER.test(part));
}

/** Does this cell print a value, which is a number or the mark a table uses
 * for no number? */
export function printsValue(text: string): boolean {
  const trimmed = text.trim();
  if (PLACEHOLDERS.has(trimmed.toLowerCase())) return true;
  return printsNumber(trimmed);
}

/** What the rule needs of a table: its shape and the cells the markup wrote. */
export interface CandidateInput {
  rows: number;
  columns: number;
  cells: GridCell[];
}

/** What the markup said about headers in this table, which the shape alone
 * does not carry. */
export interface CandidateMarking {
  /** The markup wrote a thead in this table. An empty thead, or one standing
   * below the first row, marks a header the rule is not looking at. */
  thead: boolean;
}

export interface CandidateOutcome {
  header: GridInferredHeader | null;
  declined: CandidateDeclined | null;
}

const no = (declined: CandidateDeclined): CandidateOutcome => ({ header: null, declined });

/** The cell covering each coordinate, a spanning cell covering all of its
 * own. The grid module publishes the same rule as `cellAt`; it is repeated
 * here so this file depends on the types and not on the reader. */
function cover(cells: GridCell[]): Map<string, GridCell> {
  const found = new Map<string, GridCell>();
  for (const cell of cells)
    for (let row = cell.row; row < cell.row + cell.row_span; row += 1)
      for (let column = cell.column; column < cell.column + cell.column_span; column += 1) {
        const key = `${row},${column}`;
        if (!found.has(key)) found.set(key, cell);
      }
  return found;
}

/** One heading, compared the way two headings are told apart: the
 * whitespace a renderer put in it is not part of it, and case is not either. */
const sameHeading = (text: string): string => text.replace(/\s+/g, " ").trim().toLowerCase();

/**
 * The candidate header row of a table whose markup marks none, or the test
 * that declined it.
 *
 * Call it only where `header_rows` is 0. A table whose markup marks a header
 * keeps that header and gets no candidate, because the markup has already
 * answered and an inference cannot improve on it.
 */
export function candidateHeader(table: CandidateInput, marking: CandidateMarking): CandidateOutcome {
  const { rows, columns, cells } = table;
  // 1. The markup marks a header somewhere else in the table.
  const marked = cells.filter((cell) => cell.header);
  if (marking.thead || (marked.length > 0 && !marked.some((cell) => cell.row === 0))) return no("marked_elsewhere");
  if (columns < MIN_COLUMNS) return no("too_few_columns");
  if (rows < MIN_ROWS) return no("too_few_rows");

  // 3. The first row writes its own unspanned cell in every column.
  const first = new Map<number, GridCell>();
  for (const cell of cells) if (cell.row === 0) first.set(cell.column, cell);
  if (first.size !== columns) return no("first_row_incomplete");
  const heading: string[] = [];
  for (let column = 0; column < columns; column += 1) {
    const cell = first.get(column);
    if (!cell) return no("first_row_incomplete");
    if (cell.row_span !== 1 || cell.column_span !== 1) return no("first_row_spans");
    heading.push(cell.text.trim());
  }

  // 4. Every cell prints something, except the corner over a stub.
  for (let column = 1; column < columns; column += 1) if (heading[column] === "") return no("first_row_blank_cell");
  const named = heading.filter((text) => text !== "");
  // 5. A heading is not a value.
  if (named.some((text) => printsValue(text))) return no("first_row_prints_a_value");
  // 6. Nor is it printed twice.
  const distinct = new Set(named.map(sameHeading));
  if (distinct.size !== named.length) return no("first_row_repeats_a_heading");

  // 7. Some column prints values below.
  const covered = cover(cells);
  let columnsOfValues = 0;
  for (let column = 0; column < columns; column += 1) {
    const printed: string[] = [];
    for (let row = 1; row < rows; row += 1) {
      const cell = covered.get(`${row},${column}`);
      if (!cell) continue;
      const text = cell.text.trim();
      if (text !== "") printed.push(text);
    }
    if (printed.length < 2) continue;
    const values = printed.filter((text) => printsNumber(text)).length;
    if (values >= 2 && values * 2 >= printed.length) columnsOfValues += 1;
  }
  if (columnsOfValues === 0) return no("no_column_of_values_below");

  // 8. The row under the first row is data and not a second heading level.
  const below: string[] = [];
  for (let column = 0; column < columns; column += 1) {
    const cell = covered.get(`1,${column}`);
    const text = cell ? cell.text.trim() : "";
    if (text !== "") below.push(text);
  }
  if (!below.some((text) => printsValue(text))) return no("row_below_prints_no_value");

  return { header: { rule: CANDIDATE_RULE, rows: 1, headers: heading.map((text) => [text]) }, declined: null };
}
