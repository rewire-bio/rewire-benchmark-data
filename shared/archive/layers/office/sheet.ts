/** ooxml-sheet-tsv@1: a workbook to an addressable tab separated text layer.
 *
 * ADR 0002 decision 1 names `sheet_tsv` as one of the five layer kinds and
 * names `rawxlsx.py` as its builder. That script is copied into eleven batch
 * folders, byte identical in all eleven, and decision 8 promotes it. This is
 * the same reading in TypeScript, because `shared/archive/layers` is pure and
 * may not shell out to Python, and because the layer has to be derived inside
 * the same process that hashes it.
 *
 * The values are the stored text, exactly as rawxlsx.py reads them. A number
 * comes out as the characters in `<v>`, so 0.10 stays 0.10 and 1E-05 stays
 * 1E-05. Excel's display formatting is not applied, because applying it would
 * need the number format table and a locale, and a layer whose characters
 * depend on a locale cannot carry a span. A date is therefore the serial
 * number the file stores, and a boolean is the 0 or 1 the file stores. The
 * 194 batches extracted so far were read this way, so a locator written
 * against this layer agrees with the values already in the store.
 *
 * THE SERIALISATION, which is the part a resolver depends on.
 *
 *     block := "\f# sheet\t" index "\t" name "\t" range "\n" row-line*
 *     layer := block*
 *
 * One block per sheet, in workbook order, index counted from 1. The block
 * opens with a form feed, so the form feed count in the layer is the sheet
 * count, the same way a PDF layer carries one per page. `range` is `A1:` plus
 * the last cell that holds a value, or `empty` for a sheet with no values.
 * The header line is itself tab separated, so a reader splits it rather than
 * parsing it.
 *
 * A block holds one line per sheet row from row 1 to the last row that holds
 * a value, including rows that hold none. A row line holds the row's cells
 * from column A to the last column in that row that holds a value, separated
 * by a single tab, with trailing empty cells dropped. So:
 *
 *     sheet row R is the layer line at the block's header line plus R
 *     sheet column C is the Cth tab separated field of that line, A being 1
 *     the cell is the half open character range of that field
 *
 * That is A1 notation, which ADR 0002 decision 2 names for spreadsheet cells,
 * mapped onto the line and field numbering RFC 7111 defines for a delimited
 * file. Reading the same layer as RFC 7111 does, cell B7 of the first sheet
 * is `#cell=8,2`: record 8 because RFC 7111 counts records from 1 and the
 * header line is record 1, field 2 because B is the second column. The
 * arithmetic is in ./address, and it is computed from the layer text alone so
 * that a reader with the layer and nothing else can check it.
 *
 * A cell value may not hold a tab or a newline, or the field numbering would
 * be a lie, so `escapeCell` replaces them. The rule is part of the normaliser
 * version: change it and the version goes up.
 *
 * Nothing is selected, dropped or reordered. Hidden sheets are kept, because
 * a hidden sheet holds data and dropping it would make this an adaptation
 * rather than a format conversion, which is the line the licence ruling in
 * docs/source-preservation.md section 2 draws.
 */
import { layerFromText } from "../text";
import type { Layer } from "../types";
import { part, type OfficePackage } from "./package";
import { scanXml } from "./xml";

/** Caps, measured over the 65 spreadsheet packages the store holds.
 *
 * The widest sheet is 101 columns, the longest is 83,741 rows, in Table_S1 of
 * btag147_supplementary_data.zip, and the longest layer is 20,823,442
 * characters, from ady9432_data_file_s2.xlsx. Each cap is about three times
 * its measured maximum, so none of them cuts anything the store holds, and
 * each still stops a sheet whose declared extent runs to the format's
 * 1,048,576 rows by 16,384 columns. A breach is reported as an unsupported
 * object, never a truncated layer: a layer that silently lost its last rows
 * would let a span resolve against the wrong characters.
 */
export const sheetLimits = {
  /** Rows serialised per sheet. Measured maximum 83,741. */
  rowsPerSheet: 250_000,
  /** Columns serialised per row. Measured maximum 101. */
  columnsPerRow: 4_096,
  /** Characters in the whole layer. Measured maximum 20,823,442. */
  characters: 64_000_000,
} as const;

export interface SheetCell {
  row: number;
  column: number;
  value: string;
}

export interface Sheet {
  name: string;
  /** The part path inside the package, for a problem line. */
  path: string;
  cells: SheetCell[];
  lastRow: number;
  lastColumn: number;
}

/** The 1-based column number of an A1 column label. A is 1, Z is 26, AA is
 * 27. Returns 0 for anything that is not a label. */
export function columnNumber(label: string): number {
  if (!/^[A-Z]{1,7}$/.test(label)) return 0;
  let value = 0;
  for (const character of label) value = value * 26 + (character.charCodeAt(0) - 64);
  return value;
}

/** The A1 column label of a 1-based column number. */
export function columnLabel(column: number): string {
  if (!Number.isInteger(column) || column < 1) throw new Error(`${column} is not a column number`);
  let label = "";
  let rest = column;
  while (rest > 0) {
    const remainder = (rest - 1) % 26;
    label = String.fromCharCode(65 + remainder) + label;
    rest = (rest - remainder - 1) / 26;
  }
  return label;
}

/** An A1 reference split into its row and column, or null. */
export function parseReference(reference: string): { row: number; column: number } | null {
  const match = /^\$?([A-Z]{1,7})\$?([0-9]{1,7})$/.exec(reference.trim().toUpperCase());
  if (!match) return null;
  const column = columnNumber(match[1]);
  const row = Number.parseInt(match[2], 10);
  if (!column || !row) return null;
  return { row, column };
}

const controlCharacters = /[\\\u0000-\u001f\u007f]/g;

/** Make a value safe to sit in a tab separated field, reversibly.
 *
 * A backslash doubles, the four characters that would break the grid get
 * their usual letter, and any other C0 control or DEL becomes `\xNN` with two
 * lower case hex digits. Nothing else is touched: no trimming, no whitespace
 * collapsing and no Unicode normalisation, so the characters of a value are
 * the characters the file stores. */
export function escapeCell(value: string): string {
  return value.replace(controlCharacters, (character) => {
    if (character === "\\") return "\\\\";
    if (character === "\t") return "\\t";
    if (character === "\n") return "\\n";
    if (character === "\r") return "\\r";
    if (character === "\f") return "\\f";
    return `\\x${character.charCodeAt(0).toString(16).padStart(2, "0")}`;
  });
}

/** Reverse `escapeCell`. An unknown escape is left exactly as written. */
export function unescapeCell(field: string): string {
  if (!field.includes("\\")) return field;
  let out = "";
  for (let index = 0; index < field.length; index += 1) {
    if (field[index] !== "\\") {
      out += field[index];
      continue;
    }
    const next = field[index + 1];
    if (next === "\\") { out += "\\"; index += 1; }
    else if (next === "t") { out += "\t"; index += 1; }
    else if (next === "n") { out += "\n"; index += 1; }
    else if (next === "r") { out += "\r"; index += 1; }
    else if (next === "f") { out += "\f"; index += 1; }
    else if (next === "x" && /^[0-9a-f]{2}$/.test(field.slice(index + 2, index + 4))) {
      out += String.fromCharCode(Number.parseInt(field.slice(index + 2, index + 4), 16));
      index += 3;
    } else out += "\\";
  }
  return out;
}

const T = new Set(["t"]);
const PHONETIC = new Set(["rph"]);

/** The shared string table, one entry per `<si>` in file order.
 *
 * An entry is the text of every `<t>` it holds, in document order, so a
 * string broken into formatting runs comes back whole. Phonetic guide text
 * under `<rPh>` is left out: it is a reading aid printed beside the base
 * text, not part of the value. No package in the store carries any. */
export function sharedStrings(pkg: OfficePackage): string[] {
  const text = part(pkg, "xl/sharedStrings.xml");
  if (text === null) return [];
  const table: string[] = [];
  // `<si>` elements do not nest, so one item is everything between its open
  // and its close, read with the same scanner the rest of this module uses.
  let inItem = false;
  let buffer: string[] = [];
  let keeping = 0;
  let skipping = 0;
  scanXml(text, {
    open(name) {
      if (name === "si") { inItem = true; buffer = []; keeping = 0; skipping = 0; return; }
      if (!inItem) return;
      if (PHONETIC.has(name)) skipping += 1;
      else if (T.has(name)) keeping += 1;
    },
    close(name) {
      if (name === "si") { inItem = false; table.push(buffer.join("")); return; }
      if (!inItem) return;
      if (PHONETIC.has(name)) skipping = Math.max(0, skipping - 1);
      else if (T.has(name)) keeping = Math.max(0, keeping - 1);
    },
    text(value) {
      if (inItem && keeping > 0 && skipping === 0) buffer.push(value);
    },
  });
  return table;
}

/** The sheets a workbook declares, in workbook order, with the part each one
 * lives in resolved through the workbook relationships. */
export function sheetParts(pkg: OfficePackage, problems: string[]): { name: string; path: string }[] {
  const workbook = part(pkg, "xl/workbook.xml");
  if (workbook === null) {
    problems.push("the package holds no xl/workbook.xml");
    return [];
  }
  const relationships = new Map<string, string>();
  const relationshipText = part(pkg, "xl/_rels/workbook.xml.rels");
  if (relationshipText !== null)
    scanXml(relationshipText, {
      open(name, attributes) {
        if (name === "relationship" && attributes.id && attributes.target) relationships.set(attributes.id, attributes.target);
      },
    });

  const sheets: { name: string; path: string }[] = [];
  let index = 0;
  scanXml(workbook, {
    open(name, attributes) {
      if (name !== "sheet") return;
      index += 1;
      const label = attributes.name ?? `sheet${index}`;
      const target = attributes.id ? relationships.get(attributes.id) : undefined;
      // A target is relative to the xl directory unless it opens with a
      // slash, in which case it is already a package path.
      const path = target === undefined
        ? `xl/worksheets/sheet${index}.xml`
        : target.startsWith("/") ? target.slice(1) : `xl/${target}`;
      sheets.push({ name: label, path });
    },
  });
  if (sheets.length === 0) problems.push("xl/workbook.xml declares no sheet");
  return sheets;
}

/** Every cell that holds a value in one worksheet part. */
export function readSheet(text: string, strings: string[], path: string, problems: string[]): Omit<Sheet, "name"> {
  const cells: SheetCell[] = [];
  let lastRow = 0;
  let lastColumn = 0;
  let rowNumber = 0;
  let column = 0;
  let type = "";
  let collecting: "value" | "inline" | null = null;
  let buffer: string[] = [];
  let inlineKeep = 0;

  const finish = (): void => {
    if (collecting === null) return;
    const raw = buffer.join("");
    let value = raw;
    if (collecting === "value" && type === "s") {
      const at = Number.parseInt(raw, 10);
      if (!Number.isInteger(at) || at < 0 || at >= strings.length) {
        problems.push(`${path}: shared string index ${raw} is outside the table of ${strings.length}`);
        value = "";
      } else value = strings[at];
    }
    collecting = null;
    buffer = [];
    if (value === "") return;
    cells.push({ row: rowNumber, column, value });
    if (rowNumber > lastRow) lastRow = rowNumber;
    if (column > lastColumn) lastColumn = column;
  };

  scanXml(text, {
    open(name, attributes) {
      if (name === "row") {
        // A row with no `r` follows the one before it, which is what the
        // format says an omitted index means.
        const declared = attributes.r ? Number.parseInt(attributes.r, 10) : NaN;
        rowNumber = Number.isInteger(declared) && declared > 0 ? declared : rowNumber + 1;
        column = 0;
        return;
      }
      if (name === "c") {
        finish();
        const reference = attributes.r ? parseReference(attributes.r) : null;
        if (reference) {
          rowNumber = reference.row;
          column = reference.column;
        } else {
          // A cell with no reference sits in the next column of its row.
          column += 1;
          if (attributes.r) problems.push(`${path}: cell reference ${attributes.r} is not A1 notation`);
        }
        type = attributes.t ?? "";
        return;
      }
      if (name === "v") { collecting = "value"; buffer = []; return; }
      if (name === "is") { collecting = "inline"; buffer = []; inlineKeep = 0; return; }
      if (collecting === "inline" && name === "t") inlineKeep += 1;
    },
    close(name) {
      if (name === "v" && collecting === "value") { finish(); return; }
      if (name === "is" && collecting === "inline") { inlineKeep = 0; finish(); return; }
      if (name === "c") { finish(); return; }
      if (collecting === "inline" && name === "t") inlineKeep = Math.max(0, inlineKeep - 1);
    },
    text(value) {
      if (collecting === "value") buffer.push(value);
      else if (collecting === "inline" && inlineKeep > 0) buffer.push(value);
    },
  });
  finish();
  return { path, cells, lastRow, lastColumn };
}

/** Every sheet of a workbook, read. */
export function readWorkbook(pkg: OfficePackage, problems: string[]): Sheet[] {
  const strings = sharedStrings(pkg);
  const sheets: Sheet[] = [];
  for (const declared of sheetParts(pkg, problems)) {
    const text = part(pkg, declared.path);
    if (text === null) {
      problems.push(`${declared.path} is declared by the workbook and is not in the package`);
      sheets.push({ name: declared.name, path: declared.path, cells: [], lastRow: 0, lastColumn: 0 });
      continue;
    }
    sheets.push({ name: declared.name, ...readSheet(text, strings, declared.path, problems) });
  }
  return sheets;
}

/** The marker that opens a sheet block. A form feed, then a tab separated
 * header: the word, the index, the name, the range. */
export const blockMarker = "\f# sheet\t";

/** The workbook, serialised. */
export function serialiseWorkbook(sheets: Sheet[]): string {
  const parts: string[] = [];
  let characters = 0;
  const push = (text: string): void => {
    characters += text.length;
    if (characters > sheetLimits.characters)
      throw new Error(`the workbook serialises past the ${sheetLimits.characters} character limit`);
    parts.push(text);
  };

  sheets.forEach((sheet, index) => {
    if (sheet.lastRow > sheetLimits.rowsPerSheet)
      throw new Error(`sheet ${sheet.name} holds ${sheet.lastRow} rows, over the ${sheetLimits.rowsPerSheet} row limit`);
    if (sheet.lastColumn > sheetLimits.columnsPerRow)
      throw new Error(`sheet ${sheet.name} holds ${sheet.lastColumn} columns, over the ${sheetLimits.columnsPerRow} column limit`);
    const range = sheet.lastRow === 0 ? "empty" : `A1:${columnLabel(sheet.lastColumn)}${sheet.lastRow}`;
    push(`${blockMarker}${index + 1}\t${escapeCell(sheet.name)}\t${range}\n`);

    const byRow = new Map<number, Map<number, string>>();
    for (const cell of sheet.cells) {
      const row = byRow.get(cell.row) ?? new Map<number, string>();
      row.set(cell.column, cell.value);
      byRow.set(cell.row, row);
    }
    for (let number = 1; number <= sheet.lastRow; number += 1) {
      const row = byRow.get(number);
      if (!row || row.size === 0) {
        push("\n");
        continue;
      }
      const width = Math.max(...row.keys());
      const fields: string[] = [];
      for (let column = 1; column <= width; column += 1) fields.push(escapeCell(row.get(column) ?? ""));
      push(`${fields.join("\t")}\n`);
    }
  });
  return parts.join("");
}

/** The text layer of a workbook. */
export function sheetLayer(input: Buffer, pkg: OfficePackage, problems: string[]): Layer {
  const sheets = readWorkbook(pkg, problems);
  return layerFromText(
    input,
    serialiseWorkbook(sheets),
    "ooxml-sheet-tsv@1",
    "ooxml-sheet-tsv@1 stored cell values, one tab separated block per sheet",
  );
}
