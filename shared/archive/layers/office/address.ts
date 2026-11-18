/** From a cell reference to a character range in the layer.
 *
 * A claim cites a PDF by a character range. ADR 0002 decision 2 says a claim
 * cites a spreadsheet by A1 notation and a delimited file by RFC 7111 row and
 * column references. This file is the arithmetic between the two, and it is
 * computed from the layer text alone: give it the characters and a cell
 * reference and it gives back the half open code point range, with no
 * workbook, no package and no registry.
 *
 * The rule, in full, for a layer `ooxml-sheet-tsv@1` produced.
 *
 *   A sheet block opens with a line beginning "\f# sheet", whose tab
 *   separated fields are the marker, the 1-based sheet index, the sheet name
 *   and the range.
 *   Sheet row R is the layer line at that header's line number plus R.
 *   Sheet column C is the Cth tab separated field of that line, A being 1.
 *   The cell is the half open code point range of that field.
 *
 * Read as RFC 7111 over the same layer, which counts records and fields from
 * 1, the cell is `#cell=(H + R + 1),C` where H is the header's 0-based line
 * number. The first sheet's header is line 0, so cell B7 of the first sheet
 * is `#cell=8,2`.
 *
 * Offsets are Unicode code points, which is what `oa:TextPositionSelector`
 * counts and what `sliceSpan` in `shared/omics/layers` takes. They are not
 * JavaScript string indices: a layer holding one astral character makes the
 * two disagree from that character onward.
 */
import { blockMarker, columnLabel, columnNumber, parseReference, unescapeCell } from "./sheet";

export interface SheetBlock {
  /** 1-based, as the header writes it. */
  index: number;
  /** The sheet name, with the layer's escaping undone. */
  name: string;
  /** The range the header declares: "A1:H250", or "empty". */
  range: string;
  /** 0-based line number of the header line. */
  header_line: number;
  /** Rows the block holds, which is the last row that holds a value. */
  rows: number;
}

export interface CellRange {
  /** First code point of the cell, counted from 0. */
  start: number;
  /** One past the last code point of the cell. */
  end: number;
  /** The field as the layer writes it, escaping included. */
  field: string;
  /** The field with the escaping undone, which is the stored value. */
  value: string;
  /** 0-based line number the cell sits on. */
  line: number;
  /** 1-based field number, which is the column. */
  field_number: number;
}

/** Code points in the first `end` UTF-16 units of a string. Counting skips
 * the low half of a surrogate pair, which is the half that does not start a
 * code point. */
function codePointsBefore(text: string, end: number): number {
  let count = 0;
  for (let index = 0; index < end; index += 1) {
    const unit = text.charCodeAt(index);
    if (unit >= 0xdc00 && unit <= 0xdfff) continue;
    count += 1;
  }
  return count;
}

/** Every line of the layer, as a half open pair of UTF-16 indices. The final
 * newline does not open a line. */
function lineSpans(text: string): [number, number][] {
  const spans: [number, number][] = [];
  let at = 0;
  while (at <= text.length) {
    const end = text.indexOf("\n", at);
    if (end < 0) {
      if (at < text.length) spans.push([at, text.length]);
      break;
    }
    spans.push([at, end]);
    at = end + 1;
  }
  return spans;
}

/** The sheet blocks a layer holds, in order. An empty list means the text is
 * not a sheet layer. */
export function sheetBlocks(text: string): SheetBlock[] {
  const spans = lineSpans(text);
  const blocks: SheetBlock[] = [];
  spans.forEach(([start, end], line) => {
    const content = text.slice(start, end);
    if (!content.startsWith(blockMarker)) return;
    const fields = content.split("\t");
    const index = Number.parseInt(fields[1] ?? "", 10);
    blocks.push({
      index: Number.isInteger(index) ? index : blocks.length + 1,
      name: unescapeCell(fields[2] ?? ""),
      range: fields[3] ?? "",
      header_line: line,
      rows: 0,
    });
  });
  blocks.forEach((block, at) => {
    const next = at + 1 < blocks.length ? blocks[at + 1].header_line : spans.length;
    block.rows = Math.max(0, next - block.header_line - 1);
  });
  return blocks;
}

/** The block a name or a 1-based index names, or null.
 *
 * A name is matched exactly first. A workbook may hold two sheets whose names
 * differ only in case, so a case insensitive match is tried second and only
 * when it is unambiguous: two candidates means the citation does not say
 * which, and a resolver must not pick one.
 */
export function findBlock(blocks: SheetBlock[], sheet: string | number): SheetBlock | null {
  if (typeof sheet === "number") return blocks.find((block) => block.index === sheet) ?? null;
  const exact = blocks.filter((block) => block.name === sheet);
  if (exact.length === 1) return exact[0];
  if (exact.length > 1) return null;
  const folded = blocks.filter((block) => block.name.toLowerCase() === sheet.toLowerCase());
  return folded.length === 1 ? folded[0] : null;
}

/**
 * The character range of one cell.
 *
 * `sheet` is a sheet name or a 1-based sheet index. `row` and `column` are
 * 1-based, as A1 counts them. Returns null when the sheet is not in the
 * layer, when the row is past the block, or when the row holds no field at
 * that column, which is what an empty cell looks like in the layer.
 */
export function cellRange(text: string, sheet: string | number, row: number, column: number): CellRange | null {
  if (!Number.isInteger(row) || row < 1 || !Number.isInteger(column) || column < 1) return null;
  const block = findBlock(sheetBlocks(text), sheet);
  if (!block) return null;
  const spans = lineSpans(text);
  const line = block.header_line + row;
  if (line >= block.header_line + 1 + block.rows || line >= spans.length) return null;
  const [lineStart, lineEnd] = spans[line];

  let fieldStart = lineStart;
  for (let number = 1; number < column; number += 1) {
    const tab = text.indexOf("\t", fieldStart);
    if (tab < 0 || tab >= lineEnd) return null;
    fieldStart = tab + 1;
  }
  const tab = text.indexOf("\t", fieldStart);
  const fieldEnd = tab < 0 || tab > lineEnd ? lineEnd : tab;
  const field = text.slice(fieldStart, fieldEnd);
  const start = codePointsBefore(text, fieldStart);
  return {
    start,
    end: start + codePointsBefore(field, field.length),
    field,
    value: unescapeCell(field),
    line,
    field_number: column,
  };
}

/** The character range of an A1 reference on a named sheet, which is how a
 * locator writes it: `sheet 'Table S3', cell B12`. */
export function cellRangeByReference(text: string, sheet: string | number, reference: string): CellRange | null {
  const parsed = parseReference(reference);
  return parsed === null ? null : cellRange(text, sheet, parsed.row, parsed.column);
}

/**
 * The RFC 7111 fragment that names the same cell in this layer.
 *
 * RFC 7111 counts records and fields from 1 over the whole file, so the
 * record number is the 0-based layer line plus one.
 */
export function rfc7111Fragment(range: CellRange): string {
  return `#cell=${range.line + 1},${range.field_number}`;
}

/** The A1 reference a sheet row and column make. */
export function reference(row: number, column: number): string {
  return `${columnLabel(column)}${row}`;
}

export { columnLabel, columnNumber, parseReference };
