/** jats-table-grid@1 and html-table-grid@1: the table grid as a second layer.
 *
 * A grid layer is built from the same stored bytes as the text layer, by the
 * same scan, and is registered beside it. It never replaces it. A quote is
 * still taken from the text layer; the grid says which characters of that
 * layer are the cell at a row and a column, so a locator that names a row
 * and a column can be crossed against the document instead of refused.
 *
 * The layer bytes are JSON lines, which is what the rest of this repository
 * stores and reads. The first line is the header and names the text layer
 * the offsets are into; the lines after it are one table each, in document
 * order. Keys are sorted at every depth and every number is an integer, so
 * the bytes are a function of the input bytes and the layer hashes the same
 * on any machine.
 *
 * One thing in a grid is not in the markup: a table whose markup marks no
 * header row at all may carry a candidate header row, which `header.ts`
 * chooses and explains. It is recorded in `inferred_header` and nowhere
 * else, so `header_rows` and `headers` still hold only what the markup
 * wrote, and a resolver that will not act on an inference ignores one field.
 *
 * The one check this module makes on itself: the text it scans is hashed and
 * compared with the text layer it was given. A grid whose text does not
 * reproduce the layer byte for byte is not returned at all, because its
 * offsets would point into a document nobody stored.
 *
 * What is not here. There is no grid over a PDF. `pdftotext -layout` gives
 * aligned text, not a grid, and the only way to a column from aligned text
 * is to infer one from runs of spaces. Measured on 2026-11-18, no PDF layer
 * in the store produces a `no_column_geometry` refusal that a grid would
 * answer: all 2,869 of them are locators naming a row or a cell of a
 * delimited file whose only held artifact is the paper's PDF, which is a
 * capture problem and not a geometry one. Inferring columns from whitespace
 * would therefore buy nothing and would put wrong spans on records.
 */
import { createHash } from "node:crypto";
import { decode, encodingOf, type Encoding } from "../classify";
import { htmlRules } from "../html";
import { characterCount } from "../text";
import type { Layer } from "../types";
import { xmlRules } from "../xml";
import { gridOf } from "./tables";
import { gridNormalisers, type Grid, type GridCell, type GridNormaliser, type GridTable } from "./types";

export * from "./types";
export * from "./header";
export { gridOf } from "./tables";

const digest = (bytes: Buffer): string => createHash("sha256").update(bytes).digest("hex");

/** JSON with the keys sorted at every depth, so two runs give one string. */
export function canonicalJson(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value) ?? "null";
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  const entries = Object.entries(value as Record<string, unknown>)
    .filter(([, held]) => held !== undefined)
    .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0));
  return `{${entries.map(([key, held]) => `${JSON.stringify(key)}:${canonicalJson(held)}`).join(",")}}`;
}

/** The header line of a grid layer. */
export interface GridHeader {
  normaliser: GridNormaliser;
  text_layer_sha256: string;
  text_normaliser: string;
  tables: number;
  cells: number;
  /** Cells whose range in the text layer is empty. */
  empty_cells: number;
}

export function headerOf(grid: Grid): GridHeader {
  let cells = 0;
  let empty = 0;
  for (const table of grid.tables)
    for (const cell of table.cells) {
      cells += 1;
      if (cell.start === null) empty += 1;
    }
  return {
    normaliser: grid.normaliser,
    text_layer_sha256: grid.text_layer_sha256,
    text_normaliser: grid.text_normaliser,
    tables: grid.tables.length,
    cells,
    empty_cells: empty,
  };
}

/** The layer bytes: the header, then one line per table. */
export function serialiseGrid(grid: Grid): string {
  const lines = [canonicalJson(headerOf(grid)), ...grid.tables.map((table) => canonicalJson(table))];
  return `${lines.join("\n")}\n`;
}

/** A grid layer read back from its own bytes. */
export function readGrid(text: string): Grid {
  const lines = text.split("\n").filter((line) => line.trim());
  if (lines.length === 0) throw new Error("a grid layer holds at least a header line");
  const header = JSON.parse(lines[0]) as GridHeader;
  const tables = lines.slice(1).map((line) => JSON.parse(line) as GridTable);
  if (tables.length !== header.tables)
    throw new Error(`the grid header says ${header.tables} tables and the layer holds ${tables.length}`);
  return {
    normaliser: header.normaliser,
    text_layer_sha256: header.text_layer_sha256,
    text_normaliser: header.text_normaliser,
    tables,
  };
}

/** Which grid normaliser shadows a text normaliser, or null where none
 * does. A text layer with no grid normaliser gets no grid. */
export function gridNormaliserFor(textNormaliser: string): GridNormaliser | null {
  for (const [grid, text] of Object.entries(gridNormalisers)) if (text === textNormaliser) return grid as GridNormaliser;
  return null;
}

/**
 * The grid layer over a markup object, or null when the document holds no
 * table.
 *
 * `text` is the text layer the normaliser already produced from the same
 * bytes. It is not read for its characters: it is the hash this checks its
 * own scan against, so a grid can never carry an offset into a document the
 * archive does not hold.
 */
export function gridLayer(input: Buffer, text: Layer, encoding?: Encoding): Layer | null {
  const normaliser = gridNormaliserFor(text.normaliser);
  if (!normaliser) return null;
  const found = encoding ?? encodingOf(input);
  if (!found) throw new Error("gridLayer was given bytes that do not decode as text");
  const rules = normaliser === "jats-table-grid@1" ? xmlRules : htmlRules;
  const { grid, text: scanned } = gridOf(decode(input, found), rules, normaliser, text.normaliser, text.output_sha256);
  const scannedSha = digest(Buffer.from(scanned, "utf8"));
  if (scannedSha !== text.output_sha256)
    throw new Error(`the grid scan of ${text.input_sha256} gives ${scannedSha} and the text layer is ${text.output_sha256}`);
  if (grid.tables.length === 0) return null;
  const body = serialiseGrid(grid);
  const bytes = Buffer.from(body, "utf8");
  return {
    normaliser,
    tool: normaliser,
    tool_version: normaliser.split("@")[1],
    derivation: `${normaliser} table geometry over ${text.normaliser}`,
    input_sha256: digest(input),
    output_sha256: digest(bytes),
    bytes,
    characters: characterCount(body),
    identity: false,
  };
}

/** The cell at a grid coordinate, following a span back to the cell that
 * owns it. Null when the markup wrote no cell there. */
export function cellAt(table: GridTable, row: number, column: number): GridCell | null {
  for (const cell of table.cells)
    if (
      row >= cell.row &&
      row < cell.row + cell.row_span &&
      column >= cell.column &&
      column < cell.column + cell.column_span
    )
      return cell;
  return null;
}

/** The table at an index, or null. */
export const tableAt = (grid: Grid, index: number): GridTable | null =>
  grid.tables.find((table) => table.index === index) ?? null;

/**
 * The code point range of one cell, which is what a span cites.
 *
 * The caller slices the text layer with it. `sliceSpan` in
 * `shared/omics/layers` takes exactly these two numbers, and the characters
 * it returns are the `text` on the cell. Null means the grid holds no cell
 * there or the cell prints nothing, and both are a refusal rather than a
 * neighbouring cell.
 */
export function cellRange(
  grid: Grid,
  table: number,
  row: number,
  column: number,
): { start: number; end: number; text: string; cell: GridCell } | null {
  const found = tableAt(grid, table);
  if (!found) return null;
  const cell = cellAt(found, row, column);
  if (!cell || cell.start === null || cell.end === null) return null;
  return { start: cell.start, end: cell.end, text: cell.text, cell };
}
