/** The table cell resolver, over column-aligned text.
 *
 * `pdftotext -layout` keeps a table's geometry: a column is a run of characters at the same
 * horizontal position on consecutive lines, and the separator between two columns is two or more
 * spaces. That is the only geometry the archive gives, and it is the only kind this resolver
 * reads. A layer that prints one cell per line, which is what the HTML and JATS normalisers
 * produce, carries no column positions at all, so a row-and-column locator against one of those
 * is refused with `no_column_geometry` rather than counted into place.
 *
 * Five things have to hold before a cell span is returned, and each has its own refusal.
 *
 *   1. One caption in the layer names the table the locator names.
 *   2. The window from that caption to the next caption holds the table.
 *   3. One line in the window carries the column header.
 *   4. One line in the window starts with the row label.
 *   5. Exactly one cell on that line sits under that column.
 *
 * Step 5 is the one that can be wrong without saying so, which is why the resolved span carries
 * the row label and the column header as the layer prints them. A caller that recorded a span
 * without them would have no way to tell a correct cell from its neighbour.
 */
import type { LocatorAnchor } from "../locator";
import { indexLayer, spanAt, type LayerIndex } from "./offsets";
import { refuse, type Resolution } from "./types";

/** Normalisers whose output keeps the horizontal position of a cell. */
export const ALIGNED_NORMALISERS = new Set(["pdf-text-layer@1"]);

/** How far past a caption a table may run before the resolver stops looking. */
const WINDOW_LINES = 200;

/** How many lines under a header line a second header level may occupy. */
const SUB_HEADER_LINES = 2;

/** One field of a column-aligned line, with where it sits on that line. */
export interface Cell {
  text: string;
  /** UTF-16 offsets into the layer, not into the line. */
  from: number;
  to: number;
}

/** Compare two printed labels. Case, surrounding quotes, footnote marks and the difference
 * between one space and three are not what distinguishes one row from another. */
export function normaliseLabel(text: string): string {
  return text
    .replace(/[‘’“”'"]/g, "")
    .replace(/[*†‡§¶]+/g, "")
    .replace(/\s+/g, " ")
    .replace(/^[\s.,:;]+|[\s.,:;]+$/g, "")
    .toLowerCase();
}

/** Split a line on runs of two or more spaces, which is how a layout renderer separates two
 * columns. A single space is inside a cell: "Ridge (one-hot + likelihoods)" is one field. */
export function cellsOf(index: LayerIndex, line: number): Cell[] {
  const text = index.lines[line];
  const base = index.u16[line];
  const cells: Cell[] = [];
  const pattern = /[^ ](?:[^ ]| (?! ))*/g;
  let match: RegExpExecArray | null;
  while ((match = pattern.exec(text)) !== null) {
    const trimmed = match[0].replace(/\s+$/, "");
    if (!trimmed) continue;
    cells.push({ text: trimmed, from: base + match.index, to: base + match.index + trimmed.length });
  }
  return cells;
}

/** Where a field sits across the line, which is the only thing a column band compares. The
 * offsets on a Cell are into the layer, so the line's own start has to come off first: two
 * fields on two lines have the same column when their centres agree within the line. */
const centre = (cell: Cell, base: number): number => (cell.from + cell.to) / 2 - base;

/** Escape a printed label for use inside a regular expression. */
export const escape = (text: string): string => text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/** Lines whose first printed text is a caption for this anchor.
 *
 * A caption starts a line. A mention in a sentence ("as Table A2 shows") does not, and reading a
 * table body from a sentence is how the present code returned Table G2's rows for a Table G1
 * request.
 *
 * Starting the line is not enough on its own, because a renderer wraps a sentence and the
 * continuation starts a line too: "Figure 2a using pretrained AF3 weights through TorchFold."
 * was read as the caption of Figure 2a on 4 locators while the real caption stood elsewhere. A
 * figure label therefore has to be followed by what follows a label and not by what follows a
 * mention: the end of the line, the punctuation a caption is introduced with, or a capitalised
 * word.
 *
 * A table label is not held to it. The same test over table captions was measured withdrawing
 * 96 correct cell spans and removing no wrong one, because a table caption is wrapped and
 * continued far more often than a figure caption is mentioned mid-sentence, and because a table
 * cell has the row and the column to cross-check the caption with while a caption span has
 * nothing. */
export function captionLines(index: LayerIndex, word: "Table" | "Figure", value: string): number[] {
  const label = escape(value);
  const head = word === "Table" ? "Tables?" : "(?:Figures?|Fig\\.?)";
  const pattern = new RegExp(`^\\s*(?:Supplementary\\s+|Supplemental\\s+|Extended\\s+Data\\s+|Appendix\\s+)?${head}\\s*${label}(?![0-9A-Za-z])`, "i");
  const found: number[] = [];
  for (let line = 0; line < index.lines.length; line += 1) {
    const match = pattern.exec(index.lines[line]);
    // CAPTION_TAIL is matched case sensitively, which is the whole of its work: the label of a
    // caption is followed by punctuation or by a capital, and the label of a mention the
    // renderer wrapped onto a new line is followed by the rest of the sentence in lower case.
    if (!match) continue;
    if (word === "Figure" && !CAPTION_TAIL.test(index.lines[line].slice(match[0].length))) continue;
    found.push(line);
  }
  return found;
}

/** What follows a caption's label: the end of the line, the punctuation a caption is introduced
 * with, or a capitalised word. Case sensitive, and the one place in this file that is. */
const CAPTION_TAIL = /^(?:\s*$|\s*[.:|)\u2013\u2014,;]|\s+["'(\u2018\u201c]?[A-Z0-9])/;

/** Any caption, of any table or figure. The end of one table's window is the start of the next
 * caption, so a resolver never reads across the boundary ADR 0002 decision 2 names. */
const ANY_CAPTION = /^\s*(?:Supplementary\s+|Supplemental\s+|Extended\s+Data\s+|Appendix\s+)?(?:Tables?|Figures?|Fig\.)\s*[0-9A-Z]/i;

/** The window a table occupies: from its caption to the next caption, or 200 lines. */
export function tableWindow(index: LayerIndex, caption: number): { from: number; to: number } {
  const limit = Math.min(index.lines.length, caption + 1 + WINDOW_LINES);
  for (let line = caption + 1; line < limit; line += 1) if (ANY_CAPTION.test(index.lines[line])) return { from: caption + 1, to: line };
  return { from: caption + 1, to: limit };
}

/** Marks a printed header carries that do not say which column it is: a direction arrow, and a
 * unit or note in brackets after the name. */
const DECORATION = /[↑↓↕⇑⇓]/g;
const TRAILING_BRACKET = /\s*[([][^()[\]]*[)\]]\s*$/;

/** The forms of a printed header that name the same column: as printed, and with a trailing
 * bracketed unit removed. Both are compared, so "AUROC" matches a header reading "AUROC (%)"
 * and a locator naming "Designability(↑)" matches a header reading "Designability". */
export function columnForms(text: string): string[] {
  const plain = normaliseLabel(text.replace(DECORATION, " "));
  const stripped = normaliseLabel(plain.replace(TRAILING_BRACKET, ""));
  return stripped === plain || stripped === "" ? [plain] : [plain, stripped];
}

/** Does this field name the column the locator asks for?
 *
 * Equality between those forms, not containment. Containment was measured returning a wrong cell
 * on 68 of the 133 wrong table spans of 2026-11-18, in three ways. A header reading "ESM3-Open
 * ProtBert" is two columns the layout renderer joined with a single space, and accepting it for
 * "ProtBert" returns the neighbouring block's number. A header reading "CATH4.3 Test CATH4.2
 * Test" is the same defect across a two-level header. And "ωAUROC" is a different metric from
 * "AUROC", which the old boundary test let through because the Greek letter is not an ASCII
 * letter; both columns sat in the same table. Decoration is the only difference allowed. */
function namesColumn(cell: Cell, wanted: string[]): boolean {
  const here = columnForms(cell.text);
  return here.some((form) => wanted.includes(form));
}

interface CellRequest {
  anchor: LocatorAnchor;
  row: string;
  column: string;
  /** The rest of what the locator says identifies the row.
   *
   * Half the locators that the old grammar could not read select a row by a composite key:
   * `row 'Medium' / 'FrameDiff' / length 400`. Taking the first part and ignoring the rest is how
   * a resolver lands on a plausible neighbouring row, which is worse than refusing, so every part
   * has to be printed on the line that is accepted as the row. Where they are not, the refusal is
   * `row_key_unmatched`: the layer holds the table and the resolver cannot tell which row. */
  keys?: string[];
  /** Further column levels the locator names: `column "Perc. within 2", sub-column "cent."`.
   *
   * A two-level header prints the parent on one line and its children on the next. Reading the
   * parent alone and returning whichever child the geometry lands on was measured wrong on 41
   * locators across two sources, so the child is placed by its name and by sitting inside the
   * parent's band, and a child that cannot be placed that way is refused. */
  subColumns?: string[];
}

/** One caption's worth of work: the window, the header line, the row line and the cell. */
function resolveAt(index: LayerIndex, caption: number, request: CellRequest): Resolution {
  const window = tableWindow(index, caption);
  if (window.to <= window.from) return refuse("empty_table_window", `the caption at line ${caption + 1} is followed by another caption`, index.layer_sha256);
  const wantedColumn = columnForms(request.column);
  const wantedRow = normaliseLabel(request.row);

  let header: { line: number; cells: Cell[]; at: number } | null = null;
  for (let line = window.from; line < window.to && header === null; line += 1) {
    const cells = cellsOf(index, line);
    if (cells.length < 2) continue;
    const at = cells.map((cell, index) => ({ cell, index })).filter((entry) => namesColumn(entry.cell, wantedColumn));
    // A header that prints the same column name twice is a table of two blocks side by side.
    // Taking the first is how a resolver returns the other block's number for a request that
    // named this one, which is the defect this lane exists to make impossible.
    if (at.length > 1)
      return refuse("column_ambiguous", `the header on line ${line + 1} prints "${request.column}" ${at.length} times`, index.layer_sha256);
    if (at.length === 1) header = { line, cells, at: at[0].index };
  }
  if (header === null) return refuse("column_not_found", `no line between ${window.from + 1} and ${window.to} carries the column "${request.column}"`, index.layer_sha256);

  // The level under the named column, where the locator names one. A two-level header prints the
  // parent on one line and its children on the next, and the child's own band is narrower than
  // the parent's. Reading the parent's band and taking whichever field the geometry lands on
  // returns one of the children at random, which was measured wrong on 41 locators. The child is
  // placed here, by its name and by sitting inside the parent's band, or the locator is refused.
  let level = header;
  const subColumns = request.subColumns ?? [];
  if (subColumns.length > 0) {
    if (subColumns.length > 1)
      return refuse("column_ambiguous", `the locator names ${subColumns.length} levels under "${request.column}" and this resolver reads one`, index.layer_sha256);
    const parentBase = index.u16[header.line];
    const parent = header.cells[header.at];
    const wantedSub = columnForms(subColumns[0]);
    const under: { line: number; cells: Cell[]; at: number }[] = [];
    for (let line = header.line + 1; line < Math.min(header.line + 1 + SUB_HEADER_LINES, window.to); line += 1) {
      const cells = cellsOf(index, line);
      const base = index.u16[line];
      cells.forEach((cell, at) => {
        if (!namesColumn(cell, wantedSub)) return;
        if (!(cell.from - base < parent.to - parentBase && parent.from - parentBase < cell.to - base)) return;
        under.push({ line, cells, at });
      });
      if (under.length > 0) break;
    }
    if (under.length === 0)
      return refuse("column_not_found", `no line under the header prints "${subColumns[0]}" inside the band of "${request.column}"`, index.layer_sha256);
    if (under.length > 1)
      return refuse("column_ambiguous", `${under.length} fields under "${request.column}" print "${subColumns[0]}"`, index.layer_sha256);
    level = under[0];
  }

  const labelled: { line: number; cells: Cell[] }[] = [];
  for (let line = level.line + 1; line < window.to; line += 1) {
    const cells = cellsOf(index, line);
    if (cells.length > 0 && normaliseLabel(cells[0].text) === wantedRow) labelled.push({ line, cells });
  }
  if (labelled.length === 0) return refuse("row_not_found", `no line between ${level.line + 2} and ${window.to} starts with the row "${request.row}"`, index.layer_sha256);

  const keys = (request.keys ?? []).map(normaliseLabel).filter((key) => key !== "" && key !== wantedRow && !wantedColumn.includes(key));
  const rows = keys.length === 0
    ? labelled
    : labelled.filter((candidate) => {
        const line = normaliseLabel(index.lines[candidate.line]);
        return keys.every((key) => line.includes(key));
      });
  if (rows.length === 0)
    return refuse("row_key_unmatched", `the row "${request.row}" is printed, and not on a line that also prints ${keys.map((key) => `"${key}"`).join(" and ")}`, index.layer_sha256);
  if (rows.length > 1) return refuse("row_ambiguous", `${rows.length} lines in the window start with the row "${request.row}"`, index.layer_sha256);

  // Which field of the row sits in the header's column is a question about horizontal position,
  // and only about horizontal position. Counting fields and taking the nth was measured
  // returning the neighbouring column's number whenever the two lines hold different numbers of
  // fields for the same columns, which a row label or a wrapped sentence in the header line is
  // enough to cause. So the geometry decides, always.
  const row = rows[0];
  const headerBase = index.u16[level.line];
  const rowBase = index.u16[row.line];
  const centres = level.cells.map((cell) => centre(cell, headerBase));
  const band = level.cells[level.at];
  const nearest = row.cells.filter((cell, at) => {
    // The row's first field is its label. A label is never the value of a later column, and
    // returning it was measured on 10 locators whose table prints the label on a line of its
    // own: the only field on that line is the label, so nearest-column assignment returns it.
    if (at === 0 && level.at !== 0) return false;
    const here = centre(cell, rowBase);
    let best = 0;
    for (let i = 1; i < centres.length; i += 1) if (Math.abs(centres[i] - here) < Math.abs(centres[best] - here)) best = i;
    return best === level.at;
  });
  // Nearest is not under. Two fields that share no horizontal extent are not in the same column
  // however close their centres fall, and a row whose fields do not overlap the header is a row
  // whose layout the renderer did not preserve. Refusing is the answer there.
  const picked = nearest.filter(
    (cell) => cell.from - rowBase < band.to - headerBase && band.from - headerBase < cell.to - rowBase,
  );
  if (picked.length === 0 && nearest.length > 0)
    return refuse(
      "column_unaligned",
      `row "${request.row}" prints ${nearest.length} field(s) nearest column "${request.column}" and none of them overlaps it`,
      index.layer_sha256,
    );
  if (picked.length === 0) return refuse("cell_empty", `row "${request.row}" prints nothing under column "${request.column}"`, index.layer_sha256);
  if (picked.length > 1) return refuse("column_ambiguous", `${picked.length} fields on row "${request.row}" sit under column "${request.column}"`, index.layer_sha256);

  return {
    ok: true,
    kind: "table_cell",
    span: spanAt(index, picked[0].from, picked[0].to),
    layer_sha256: index.layer_sha256,
    row_label: row.cells[0].text,
    column_header: level.cells[level.at].text,
  };
}

/**
 * The cell a table locator names, or a refusal.
 *
 * Where more than one caption names the table, each is tried and the cell is returned only if
 * exactly one of them yields it. That is a cross-check, not a preference: two captions that both
 * hold a row with this label under this column are a genuine ambiguity and are refused.
 */
export function resolveTableCell(index: LayerIndex, request: CellRequest): Resolution {
  if (!ALIGNED_NORMALISERS.has(index.normaliser))
    return refuse("no_column_geometry", `${index.normaliser} prints no column positions, so a row and column cannot be crossed`, index.layer_sha256);
  const word = request.anchor.kind === "figure" ? "Figure" : "Table";
  const captions = captionLines(index, word, request.anchor.value);
  if (captions.length === 0) return refuse("anchor_not_found", `no caption line names ${word} ${request.anchor.value}`, index.layer_sha256);

  const hits: Resolution[] = [];
  let lastRefusal: Resolution | null = null;
  for (const caption of captions) {
    const outcome = resolveAt(index, caption, request);
    if (outcome.ok) hits.push(outcome);
    else lastRefusal = outcome;
  }
  if (hits.length === 1) {
    const only = hits[0] as Extract<Resolution, { ok: true }>;
    return captions.length > 1 ? { ...only, anchor_candidates: captions.length } : only;
  }
  if (hits.length > 1)
    return refuse("anchor_ambiguous", `${hits.length} of ${captions.length} captions for ${word} ${request.anchor.value} hold this row and column`, index.layer_sha256);
  return lastRefusal ?? refuse("anchor_not_found", `no caption line names ${word} ${request.anchor.value}`, index.layer_sha256);
}

/** Index a layer for the resolvers. Re-exported here so a caller that only wants a table does
 * not have to know about the offset module. */
export { indexLayer };
