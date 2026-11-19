/** What a table grid holds, and what a span may address in one.
 *
 * A text layer flattens a table. Both markup normalisers print a row as one
 * line with the cells separated by a space, so the column a cell sat in is
 * gone before any resolver sees the characters. That loss is the largest
 * single reason a stored locator cannot be re-checked: 10,046 of the 22,528
 * `no_column_geometry` refusals measured on 2026-11-18 are a row and column
 * crossed against a JATS or HTML layer that prints no columns.
 *
 * A grid keeps the geometry the markup already carries. It is a second layer
 * over the same stored bytes, not a replacement: the text layer stays the
 * substrate a quote is taken from, and the grid says which characters of it
 * are the cell at row r, column c.
 *
 * Three properties the rest of this module exists to hold.
 *
 * 1. Every cell names a half open code point range in the text layer. The
 *    grid is useless if the two disagree, so the ranges are computed from
 *    the one scan the text layer is built by and are checked against it.
 * 2. Nothing the markup wrote is inferred. A column span is what the markup
 *    writes, a header row is a row the markup marks as one, and a cell the
 *    markup does not write is absent rather than guessed. Where the markup
 *    marks no header row at all, one inference is made and kept apart from
 *    everything the markup said: `inferred_header`, which `header.ts`
 *    explains and which a reader and a resolver can both decline.
 * 3. The bytes are a function of the input bytes. Keys are sorted, numbers
 *    are integers, no clock and no locale are read, so the layer hashes the
 *    same on every machine.
 */

/** The grid normalisers, paired with the text normaliser each one shadows. */
export const gridNormalisers = {
  "jats-table-grid@1": "europepmc-fulltext-xml@1",
  "html-table-grid@1": "html-text@1",
} as const;
export type GridNormaliser = keyof typeof gridNormalisers;

/** One cell the markup wrote, placed on the grid.
 *
 * `row` and `column` are zero based coordinates of the cell's top left
 * corner. A cell with a span occupies `row_span` by `column_span`
 * coordinates from there, and the coordinates it covers carry no cell of
 * their own.
 *
 * `start` and `end` are code point offsets into the text layer, half open,
 * counted from 0, which is what `oa:TextPositionSelector` counts and what
 * `sliceSpan` in `shared/omics/layers` takes. They are null when the cell
 * prints nothing, which is a cell a resolver must refuse rather than fill.
 */
export interface GridCell {
  row: number;
  column: number;
  row_span: number;
  column_span: number;
  /** True when the markup wrote the cell as a header cell. */
  header: boolean;
  start: number | null;
  end: number | null;
  /** Exactly the characters the text layer holds between the offsets. */
  text: string;
}

/** A run of characters in the text layer, in code points. */
export interface GridRange {
  start: number;
  end: number;
  text: string;
}

/** A header row no markup marked, put forward by the grid producer.
 *
 * This is the one thing in a grid the markup did not write, and it is kept
 * in a field of its own so that nothing can read it as a marked header.
 * `header_rows` stays 0 and `headers` stays empty on a table that has one:
 * a reader comparing the two always knows which is which, and a resolver
 * that will not act on an inference has only to ignore this field.
 *
 * `rows` is how many leading rows the candidate covers, which the one rule
 * that exists always answers as 1. `headers` has the same shape as the
 * marked `headers`, one path per column, so a resolver that accepts the
 * candidate substitutes it and changes nothing else. `rule` names the rule
 * that chose it, so a resolver can accept one rule and decline another.
 */
export interface GridInferredHeader {
  rule: string;
  rows: number;
  headers: string[][];
}

/** One table. */
export interface GridTable {
  /** Zero based position among the tables of this layer, in document
   * order. A nested table counts as its own table. */
  index: number;
  rows: number;
  columns: number;
  /** Leading rows the markup marks as header rows, which may be more than
   * one: a header spanning two levels is two rows and the column's heading
   * is the path through them. */
  header_rows: number;
  /** For each column, the heading at each header row, top level first. An
   * entry is the empty string where that header row carries nothing over
   * the column. The array is `columns` long and each path is `header_rows`
   * long, so a reader can address a level without counting. */
  headers: string[][];
  /** A header row the markup marks nowhere and the rule in `header.ts` puts
   * forward, absent where the markup marks a header and absent where the
   * rule declined to choose one. It is never a header the markup wrote and
   * `header_rows` is always 0 on a table that carries one. */
  inferred_header?: GridInferredHeader;
  /** The label the markup gives the table, such as "Table 3". Null when the
   * markup gives none. */
  label: GridRange | null;
  /** The caption. Null when the markup gives none. */
  caption: GridRange | null;
  /** The cells the markup wrote, in row then column order. */
  cells: GridCell[];
  /** What the parse could not do, one line each. Empty on a clean parse. */
  problems: string[];
}

/** One grid layer. */
export interface Grid {
  normaliser: GridNormaliser;
  /** The text layer the offsets are into, by its own hash. */
  text_layer_sha256: string;
  text_normaliser: string;
  tables: GridTable[];
}
