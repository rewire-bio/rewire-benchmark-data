/** A cell of a workbook sheet, addressed the way a locator writes it.
 *
 * `ooxml-sheet-tsv@1` keeps a workbook's geometry: one block per sheet, one line per sheet row,
 * one tab separated field per column. 6,390 stored locators reach a layer of that kind and every
 * one of them refused before this resolver, most with `no_column_geometry`, because nothing read
 * the blocks. The arithmetic from a cell reference to a character range was already written in
 * `shared/archive/layers/office/address.ts` and had no caller.
 *
 * THE OFF BY ONE, which is the whole reason this is a resolver of its own.
 *
 * A block opens with a header line, `\f# sheet` and the sheet's index, name and range, and that
 * line is not a sheet row. Sheet row R is the layer line at the block's header line plus R, so
 * row 1 of the first sheet is layer line 1 and not layer line 0. The delimited resolver in
 * ./regions counts the first printing line of the layer as the header row and the Nth line as
 * row N, which is what it has to do for a CSV the archive holds as the file itself. Putting
 * `ooxml-sheet-tsv@1` in `FILE_NORMALISERS` and letting that resolver read it would shift every
 * row of the first sheet by one and every row of the second sheet by the whole of the first,
 * and the span would still hold a number. It would print a plausible wrong value rather than
 * refuse, which is the worst thing a resolver can do. Hence a separate path that reads the
 * blocks, and `tests/omics-spans-sheet.test.ts`, which proves on a stored workbook that a row
 * resolved by number lands on the row the spreadsheet calls that number.
 *
 * WHAT IS EVIDENCE AND WHAT IS AN ADDRESS. The A1 reference is the address and the resolver
 * never searches for a better one. The row label, the row's other keys and the column heading
 * are the redundancy ADR 0002 decision 2 asks a cell span to carry, so they are checked against
 * the cell the reference names: where the addressed row does not print a key the locator names,
 * the span is refused and no other row is tried. A resolver that went looking for the row that
 * does print it would answer a different question from the one the locator asks.
 *
 * WHAT A CELL OF THIS LAYER PRINTS, which is what checking one of these spans depends on. The
 * layer carries the characters the workbook stores, so a computed cell comes out as the full
 * double: 0.81699999999999995, or 5.0452599342583802E-2. The record keeps what the spreadsheet
 * displays, 0.82 or 0.050. Both spell one number and they share no substring, so a value check
 * comparing characters alone calls the right cell a wrong answer, and a run of one did, on 1,706
 * of these spans. `valuePresence` in `scripts/omics/spans/cli.ts` compares a number pair as
 * numbers, at the precision the record writes.
 *
 * Nothing here calls a model and nothing here reads a stored value.
 */
import { columnLabel, columnNumber, findBlock, parseReference, sheetBlocks, type SheetBlock } from "../../archive/layers/office/address";
import { unescapeCell } from "../../archive/layers/office/sheet";
import type { LocatorSelector, ParsedLocator } from "../locator";
import { spanAt, type LayerIndex } from "./offsets";
import { normaliseLabel } from "./table";
import { refuse, type Resolution } from "./types";

/** Normalisers whose layers carry sheet blocks. `ooxml-document-text@1` is the other office
 * normaliser and carries prose, so it is not one of them. */
export const SHEET_NORMALISERS = new Set(["ooxml-sheet-tsv@1"]);

export const isSheetLayer = (normaliser: string): boolean => SHEET_NORMALISERS.has(normaliser);

/** How far down a block a column heading is looked for, in rows.
 *
 * A heading stands at the top of its block, and a sheet that stacks two tables prints a second
 * heading further down. The search runs from row 1 to the addressed row, capped here, so a
 * heading is never read from below the cell it is supposed to label and a locator addressing row
 * 80,000 does not pay for 80,000 rows of searching. */
const HEADING_ROWS = 50;

/** What a locator says about one sheet cell. */
export interface SheetCellRequest {
  /** The sheet the locator names. Null is a refusal: there is no first sheet to fall back on. */
  sheet: string | null;
  /** An A1 reference, where the locator prints one. */
  cell?: string;
  /** A row number the locator prints outside a reference. */
  row?: number;
  /** A 1-based column number, where the locator prints the column as a letter. */
  column?: number;
  /** The column's printed heading, where the locator names one. */
  columnHeader?: string;
  /** Facts the locator states about the addressed row: the row label and the row's other keys,
   * each with the name the locator gave it and, where the two differ, the whole phrase it was
   * printed as. */
  rowKeys?: { key: string; value: string; printed?: string }[];
}

/** The blocks of one layer, read once.
 *
 * `sheetBlocks` scans the whole layer, the longest sheet layer in the store holds 20,823,442
 * characters, and a layer is resolved against hundreds of locators in a run. The key is the
 * layer hash, which names the bytes, so a cached answer can only belong to the text it was read
 * from. */
const blockCache = new Map<string, SheetBlock[]>();

export function blocksOf(index: LayerIndex): SheetBlock[] {
  const held = blockCache.get(index.layer_sha256);
  if (held) return held;
  // The store holds 65 sheet layers. The bound is here so that a longer-lived process cannot
  // hold every layer it has ever seen.
  if (blockCache.size > 128) blockCache.clear();
  const blocks = sheetBlocks(index.text);
  blockCache.set(index.layer_sha256, blocks);
  return blocks;
}

/** One field of a layer line, with the UTF-16 offsets `spanAt` takes. */
export interface SheetField {
  text: string;
  from: number;
  to: number;
}

/** The tab separated fields of one layer line. Field numbering is 1-based, as A1 counts
 * columns, so field C is `fieldsOfLine(...)[C - 1]`. */
export function fieldsOfLine(index: LayerIndex, line: number): SheetField[] {
  const text = index.lines[line] ?? "";
  const base = index.u16[line] ?? 0;
  const fields: SheetField[] = [];
  let from = 0;
  for (;;) {
    const tab = text.indexOf("\t", from);
    const end = tab < 0 ? text.length : tab;
    fields.push({ text: text.slice(from, end), from: base + from, to: base + end });
    if (tab < 0) return fields;
    from = tab + 1;
  }
}

/** The value a field holds, with the layer's escaping undone. */
const valueOf = (field: SheetField | undefined): string => (field === undefined ? "" : unescapeCell(field.text));

/** A column a heading is printed over, and the row it is printed in. */
interface HeadingHit {
  column: number;
  row: number;
}

/** The columns a heading is printed in, looked for above the addressed row only. One entry per
 * column, carrying the first row of the block that prints the heading there. */
function headingColumns(index: LayerIndex, block: SheetBlock, row: number, heading: string): HeadingHit[] {
  const wanted = normaliseLabel(heading);
  if (wanted === "") return [];
  const last = Math.min(row - 1, block.rows, HEADING_ROWS);
  const found = new Map<number, number>();
  for (let above = 1; above <= last; above += 1)
    fieldsOfLine(index, block.header_line + above).forEach((field, at) => {
      if (normaliseLabel(valueOf(field)) === wanted && !found.has(at + 1)) found.set(at + 1, above);
    });
  return [...found.entries()].map(([column, at]) => ({ column, row: at })).sort((a, b) => a.column - b.column);
}

/** How far above a row a merged cell's value is looked for, in rows. A block of a spreadsheet
 * that prints its key once and leaves the rows below it blank is the shape this follows, and the
 * longest such block in the store is under 40 rows. */
const CARRY_ROWS = 200;

/**
 * The value each column holds at this row, with a merged cell read as the rows it covers.
 *
 * A spreadsheet prints `CLL` once in the dataset column and leaves the next four rows of that
 * column empty, and the file stores exactly that: one value, then nothing. So the value in force
 * at a row is the nearest value at or above it in the same column. Reading only the row's own
 * fields would refuse every row of such a block but the first.
 *
 * Each column is answered separately, so a key cannot be satisfied by a value standing in a
 * different column, and the search never looks below the row.
 */
function valuesInForce(index: LayerIndex, block: SheetBlock, row: number): Map<number, string> {
  const inForce = new Map<number, string>();
  const first = Math.max(1, row - CARRY_ROWS);
  for (let above = row; above >= first; above -= 1)
    fieldsOfLine(index, block.header_line + above).forEach((field, at) => {
      const text = valueOf(field).trim();
      if (text !== "" && !inForce.has(at + 1)) inForce.set(at + 1, text);
    });
  return inForce;
}

/** The heading the layer prints over a column, for the span to carry.
 *
 * Row 1 of the sheet, which is where this layer's own documentation says a sheet puts its column
 * names. Not the nearest value above the cell: on a table of 700 rows that is the row before,
 * which is another number and not a heading. Where the locator named the heading itself and it
 * was found, that row is used instead, so a sheet whose names are two rows down reports the name
 * the locator was checked against. */
function headingOf(index: LayerIndex, block: SheetBlock, column: number, at = 1): string | undefined {
  if (at < 1 || at > block.rows) return undefined;
  const text = valueOf(fieldsOfLine(index, block.header_line + at)[column - 1]).trim();
  return text === "" ? undefined : text;
}

/**
 * The span one sheet cell occupies, or the one reason the locator does not reach it.
 *
 * The order is the order the evidence binds: the sheet, then the row, then the column, then the
 * cell, then the labels the locator printed beside the address.
 */
export function resolveSheetCell(index: LayerIndex, request: SheetCellRequest): Resolution {
  if (!isSheetLayer(index.normaliser))
    return refuse("no_column_geometry", `${index.normaliser} carries no sheet blocks`, index.layer_sha256);
  const blocks = blocksOf(index);
  if (blocks.length === 0)
    return refuse("no_column_geometry", "this layer holds no sheet block", index.layer_sha256);

  // The refusal says which sheets the workbook does hold, because that is what a reader needs to
  // see next. A workbook with many sheets gets the first few and a count.
  const names = blocks.slice(0, 8).map((block) => `"${block.name}"`).join(", ");
  const held = `this workbook holds ${blocks.length}: ${names}${blocks.length > 8 ? " and more" : ""}`;
  const wanted = request.sheet === null ? "" : request.sheet.trim();
  // A workbook is not a file with one table in it. A cell reference means nothing until a sheet
  // is named, and the first sheet is not the one the locator meant: it is the one that happens
  // to be first.
  if (wanted === "") return refuse("no_anchor", `the locator names a cell and no sheet, and ${held}`, index.layer_sha256);
  const block = findBlock(blocks, wanted);
  if (!block) {
    const folded = blocks.filter((candidate) => candidate.name.toLowerCase() === wanted.toLowerCase());
    if (folded.length > 1)
      return refuse("anchor_ambiguous", `${folded.length} sheets of this workbook are named "${wanted}" up to case`, index.layer_sha256);
    return refuse("anchor_not_found", `no sheet of this workbook is named "${wanted}", and ${held}`, index.layer_sha256);
  }

  let row: number | null = null;
  let column: number | null = null;
  if (request.cell !== undefined) {
    const reference = parseReference(request.cell);
    if (reference === null)
      return refuse("no_resolver_for_kind", `"${request.cell}" is not an A1 reference`, index.layer_sha256);
    row = reference.row;
    column = reference.column;
  }
  if (request.row !== undefined) {
    // Two claims about one row. `cell I365, row 365` is the common shape and the two agree; where
    // they do not, the locator contradicts itself and neither reading is evidence.
    if (row !== null && row !== request.row)
      return refuse("row_ambiguous", `the locator names cell row ${row} and row ${request.row}`, index.layer_sha256);
    row = request.row;
  }
  if (row === null) return refuse("no_row_in_locator", `the locator names sheet "${block.name}" and no row`, index.layer_sha256);
  if (request.column !== undefined && column === null) column = request.column;

  let headingRow = 1;
  if (column === null) {
    if (request.columnHeader === undefined)
      return refuse("no_column_in_locator", `the locator names row ${row} of sheet "${block.name}" and no column`, index.layer_sha256);
    const columns = headingColumns(index, block, row, request.columnHeader);
    if (columns.length === 0)
      return refuse(
        "column_not_found",
        `no row above row ${row} of sheet "${block.name}" prints the heading "${request.columnHeader}"`,
        index.layer_sha256,
      );
    if (columns.length > 1)
      return refuse(
        "column_ambiguous",
        `sheet "${block.name}" prints the heading "${request.columnHeader}" in ${columns.length} columns above row ${row}`,
        index.layer_sha256,
      );
    column = columns[0].column;
    headingRow = columns[0].row;
  } else if (request.columnHeader !== undefined) {
    // The letter and the heading are two claims about one column. Where the heading is printed
    // above the cell at all, it has to be printed over that column. Where it is printed nowhere
    // above the cell there is nothing to contradict the letter, which is the case on a sheet
    // whose headings are two rows deep or are not the locator's wording, so the address stands.
    const columns = headingColumns(index, block, row, request.columnHeader);
    const agreed = columns.find((hit) => hit.column === column);
    if (columns.length > 0 && agreed === undefined)
      return refuse(
        "column_not_found",
        `sheet "${block.name}" prints the heading "${request.columnHeader}" over column ` +
          `${columns.map((hit) => columnLabel(hit.column)).join(" and ")}, and the locator names column ${columnLabel(column)}`,
        index.layer_sha256,
      );
    if (agreed !== undefined) headingRow = agreed.row;
  }

  if (row > block.rows)
    return refuse(
      "row_not_found",
      `sheet "${block.name}" holds ${block.rows} rows and the locator names row ${row}`,
      index.layer_sha256,
    );
  const fields = fieldsOfLine(index, block.header_line + row);
  const field = fields[column - 1];
  // A row line stops at its last printing cell, so a column past the end of the line is a cell
  // the sheet leaves empty rather than a column the sheet does not have.
  if (field === undefined || valueOf(field).trim() === "")
    return refuse(
      "cell_empty",
      `row ${row} of sheet "${block.name}" prints nothing in column ${columnLabel(column)}`,
      index.layer_sha256,
    );

  // Every fact the locator states about the row has to hold at the row the reference names, and
  // where one does not the span is refused rather than moved. A key whose own name is a heading
  // of this sheet is checked against that column and nothing else, which is the stronger test;
  // a key the sheet does not head is checked against every column, as the keyed-row resolver in
  // ./regions does for the same reason.
  const inForce = valuesInForce(index, block, row);
  const unmatched = (request.rowKeys ?? []).filter((entry) => {
    // Two spellings of one fact. `row 2 'Combined All Features (1%)'` parses to the key
    // `combined all features` and the value `1%`, because a bracket is a selector form, and the
    // sheet prints the whole phrase in one cell. Both are tried and either satisfies the key.
    const spellings = [entry.value, entry.printed ?? ""].map(normaliseLabel).filter((text) => text !== "");
    if (spellings.length === 0) return false;
    const named = headingColumns(index, block, row, entry.key);
    const held = named.length === 1 ? [inForce.get(named[0].column) ?? ""] : [...inForce.values()];
    return !held.some((text) => spellings.includes(normaliseLabel(text)));
  });
  if (unmatched.length > 0)
    return refuse(
      "row_key_unmatched",
      `row ${row} of sheet "${block.name}" does not hold ${unmatched.map((entry) => `${entry.key} "${entry.value}"`).join(" or ")}`,
      index.layer_sha256,
    );

  const label = fields.map((entry) => valueOf(entry).trim()).find((text) => text !== "");
  const outcome: Resolution = {
    ok: true,
    kind: "sheet_cell",
    span: spanAt(index, field.from, field.to),
    layer_sha256: index.layer_sha256,
    row_label: label,
    column_header: headingOf(index, block, column, headingRow),
  };
  return outcome;
}

const ROW_WORDS = new Set(["row", "rows"]);
const COLUMN_WORDS = new Set(["column", "col", "columns", "sub-column", "sub-col"]);
/** Keys whose value is printed above the row rather than on it: a block heading, a level of a
 * stacked header, a panel. Requiring one of them on the row would refuse every row that has
 * one, so they are not row keys. They are also not read as a second address: which block a row
 * belongs to is geometry this layer does not carry. */
const ABOVE_THE_ROW = /\b(?:block|blocks|group|groups|panel|panels|section|sections|part|parts|subtable|under|metric)\b/i;
/** A row number as a locator prints it, `365` or `365:`. */
const ROW_NUMBER = /^(\d{1,7})\s*[.:,;]?$/;
/** A column letter run, which is what the rest of the key holds in `column D 'mean'`. */
const COLUMN_LETTERS = /^[A-Za-z]{1,3}$/;

const firstWord = (key: string): string => key.trim().split(/\s+/)[0].toLowerCase();
const restOfKey = (key: string): string => key.trim().split(/\s+/).slice(1).join(" ");

/** The 1-based column a letter run names, or undefined. The arithmetic is the office layer's
 * own, so A1 means here what it means there; the guard is what keeps `column 'mean'` from being
 * read as a run of column letters. */
function columnOfLetters(letters: string): number | undefined {
  if (!COLUMN_LETTERS.test(letters)) return undefined;
  return columnNumber(letters.toUpperCase()) || undefined;
}

/** Is this selector the sheet name, read off a key rather than off an anchor?
 *
 * 720 stored locators write `Supplementary Tables workbook sheet 'S2 WGS INDELs'`, where the
 * grammar reads the whole phrase before the name as the key, so the sheet never becomes an
 * anchor. The name is still printed and still says which sheet. */
const namesSheet = (selector: LocatorSelector): boolean => /(?:^|\s)sheets?$/i.test(selector.key.trim());

/**
 * What a parsed locator says about a sheet cell, or null where it says nothing this resolves.
 *
 * Null leaves the locator on the dispatch it already had. The two shapes read here are the two
 * ADR 0002 decision 2 names for a spreadsheet: a sheet and an A1 reference, and a sheet with a
 * row and a column.
 *
 * A locator that cites several cells prints the value's own cell first and its supporting cells
 * after it: `fig2hi!D7; method fig2hi!A7; target fig2hi!D1` reads the value from D7 and names
 * the method in A7 and the target in D1. So the first reference and the first sheet anchor are
 * taken, and the later ones are left alone.
 */
export function sheetRequest(parsed: ParsedLocator): SheetCellRequest | null {
  const cell = parsed.addresses.find((address) => address.kind === "sheet_cell");
  const rowAddress = parsed.addresses.find((address) => address.kind === "row_number");
  const anchor = parsed.anchors.find((candidate) => candidate.kind === "sheet" && candidate.value.trim() !== "");

  let sheet = anchor ? anchor.value : null;
  let row: number | undefined;
  let column: number | undefined;
  let columnHeader: string | undefined;
  const rowKeys: NonNullable<SheetCellRequest["rowKeys"]> = [];

  if (rowAddress) {
    const number = Number.parseInt(rowAddress.value, 10);
    if (Number.isInteger(number) && number > 0) row = number;
  }

  for (const selector of parsed.selectors) {
    if (selector.value === null) continue;
    if (sheet === null && namesSheet(selector)) {
      sheet = selector.value;
      continue;
    }
    const head = firstWord(selector.key);
    if (COLUMN_WORDS.has(head)) {
      // `column D 'mean'` names the column twice, by letter and by heading. The letter is only
      // read where the locator prints no cell reference, because a reference already carries the
      // column and the two are then crossed against each other instead.
      const letters = columnOfLetters(restOfKey(selector.key));
      if (letters !== undefined && column === undefined) column = letters;
      if (columnHeader === undefined) columnHeader = selector.value;
      continue;
    }
    if (ROW_WORDS.has(head)) {
      const number = ROW_NUMBER.exec(selector.value.trim());
      if (number) {
        const parsedRow = Number.parseInt(number[1], 10);
        if (row === undefined && parsedRow > 0) row = parsedRow;
      } else rowKeys.push({ key: selector.key, value: selector.value, printed: selector.raw });
      continue;
    }
    if (ABOVE_THE_ROW.test(selector.key)) continue;
    rowKeys.push({ key: selector.key, value: selector.value, printed: selector.raw });
  }

  if (cell === undefined && !(sheet !== null && row !== undefined && (column !== undefined || columnHeader !== undefined)))
    return null;

  const request: SheetCellRequest = {
    sheet,
    rowKeys: rowKeys.filter((entry) => entry.value.trim() !== "" && entry.value !== sheet),
  };
  if (cell !== undefined) request.cell = cell.value;
  if (row !== undefined) request.row = row;
  // A letter read off a column key says nothing the reference does not already say.
  if (column !== undefined && cell === undefined) request.column = column;
  if (columnHeader !== undefined) request.columnHeader = columnHeader;
  return request;
}
