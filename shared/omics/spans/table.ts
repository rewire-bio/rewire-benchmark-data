/** The table cell resolver, over column-aligned text.
 *
 * `pdftotext -layout` keeps a table's geometry: a column is a run of characters at the same
 * horizontal position on consecutive lines, and the separator between two columns is two or more
 * spaces. That is the only geometry the archive gives, and it is the only kind this resolver
 * reads. A layer that prints one cell per line, which is what the HTML and JATS normalisers
 * produce, carries no column positions at all, so a row-and-column locator against one of those
 * is refused with `no_column_geometry` rather than counted into place.
 *
 * Six things have to hold before a cell span is returned, and each has its own refusal.
 *
 *   1. One caption in the layer names the table the locator names.
 *   2. Exactly one of the blocks around that caption holds the table. A caption is printed above
 *      its table in most papers and below it in some, so both sides are read and two sides that
 *      both answer are a refusal.
 *   3. One line in the block carries the column header.
 *   4. One line in the block starts with the row label.
 *   5. Exactly one field on that line sits under that column.
 *   6. That field is one cell and not several columns the renderer joined with a single space,
 *      which is `shared/omics/spans/width.ts`.
 *
 * Steps 5 and 6 are the ones that can be wrong without saying so, which is why the resolved span
 * carries the row label and the column header as the layer prints them. A caller that recorded a
 * span without them would have no way to tell a correct cell from its neighbour.
 */
import type { LocatorAnchor } from "../locator";
import { indexLayer, spanAt, type LayerIndex } from "./offsets";
import { refuse, refusalReasons, type RefusalReason, type Resolution } from "./types";
import { cellWidth } from "./width";

/** How far into the layer a refusal got. `refusalReasons` is ordered from the substrate
 * outwards, so the later reason is the one that read more before it stopped, and that is the one
 * worth reporting when several regions were tried and all of them refused. */
const reasonOrder = (reason: RefusalReason): number => refusalReasons.indexOf(reason);

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

/** The character `pdftotext` writes where one page ends and the next begins. */
const PAGE_BREAK = "\f";

/** The window a table occupies: from its caption to the next caption, the next page, or 200
 * lines, whichever comes first.
 *
 * The page boundary is the form feed `pdftotext` writes between pages. A table is a float and a
 * typesetter puts a float on the page its caption is on, so a window that runs past a form feed
 * is reading a different float. It read one on 2026-11-18: a caption at the foot of its page,
 * with the next page opening on another table that printed the same row and column names with
 * different numbers, and 24 spans committed to those numbers. */
export function tableWindow(index: LayerIndex, caption: number): { from: number; to: number } {
  const limit = Math.min(index.lines.length, caption + 1 + WINDOW_LINES);
  for (let line = caption + 1; line < limit; line += 1)
    if (ANY_CAPTION.test(index.lines[line]) || index.lines[line].includes(PAGE_BREAK)) return { from: caption + 1, to: line };
  return { from: caption + 1, to: limit };
}

/** The same window with the page boundary allowed, which is where a table printed on the page
 * after its caption is found: 96 locators on one layer name a table whose caption stands at the
 * foot of a page and whose body opens the next one. It is read only after the caption's own page
 * has been read and has answered nothing. */
export function widerWindow(index: LayerIndex, caption: number): { from: number; to: number } {
  const limit = Math.min(index.lines.length, caption + 1 + WINDOW_LINES);
  for (let line = caption + 1; line < limit; line += 1) if (ANY_CAPTION.test(index.lines[line])) return { from: caption + 1, to: line };
  return { from: caption + 1, to: limit };
}

/** The part of a caption's own page that lies above it, or null where that part is another
 * caption's table.
 *
 * A caption is printed above its table in most papers and below it in some. Where it is printed
 * below, the window that runs downwards holds the caption's own wrapped text and nothing else,
 * and the table is above.
 *
 * The region runs up from the caption to the first page boundary or caption above it, and is a
 * candidate only when that boundary is a page boundary. A caption above it is taken to own the
 * region: that caption's table, sitting below its own caption in the ordinary way. That test is
 * what keeps the appendix case out. One paper prints one table per dataset with the same row and
 * column names in every one, so the region above Table A2's caption is Table A1's body; reading
 * it as a second candidate for Table A2 withdrew 408 spans as ambiguous, 384 of them printing
 * the stored value exactly, and reading it as a fallback committed 13 spans to the previous
 * table's numbers.
 *
 * The test is an assumption and not a proof. A paper printing its captions under its tables with
 * two tables on one page would have the caption above the region owning it as well, this would
 * return null, and the search would fall through to `widerWindow` and read past the page
 * boundary. What is measured is the outcome and not the path: over all 52,278 locators every
 * span this ordering adds prints the stored value, and no span came to print it nowhere that did
 * not before. Making the fall-through refuse instead costs the 96 locators whose table opens the
 * page after its caption, which is why it does not.
 */
export function blockAbove(index: LayerIndex, caption: number): { from: number; to: number } | null {
  const boundary = (line: number): boolean => ANY_CAPTION.test(index.lines[line]) || index.lines[line].includes(PAGE_BREAK);
  const floor = Math.max(0, caption - WINDOW_LINES);
  let from = caption;
  while (from > floor && !boundary(from - 1)) from -= 1;
  if (from > 0 && ANY_CAPTION.test(index.lines[from - 1])) return null;
  let to = caption;
  while (to > from && index.lines[to - 1].trim() === "") to -= 1;
  while (from < to && index.lines[from].trim() === "") from += 1;
  return from < to ? { from, to } : null;
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

/** One block's worth of work: the header line, the row line and the cell. */
function resolveAt(index: LayerIndex, window: { from: number; to: number }, request: CellRequest): Resolution {
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

  // A field is one cell only where it does not run across its neighbours. Two columns the
  // renderer separated with a single space arrive as one field, and returning it puts a span over
  // several columns while naming one: 66 spans on 2026-11-18, the worst of them covering three
  // models' results with the stored value in the middle.
  const width = cellWidth({
    bands: level.cells.map((cell) => ({ from: cell.from - headerBase, to: cell.to - headerBase })),
    at: level.at,
    field: { text: picked[0].text, from: picked[0].from - rowBase, to: picked[0].to - rowBase },
  });
  if (!width.ok)
    return refuse("column_merged", `row "${request.row}" under column "${request.column}": ${width.detail}`, index.layer_sha256);

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
 * Every caption naming the table is tried, and on each one both the window below it and the
 * block above it, because a caption is printed above its table in most papers and below it in
 * some. The cell is returned only if exactly one of those blocks yields it. That is a
 * cross-check, not a preference: two blocks that both hold a row with this label under this
 * column are a genuine ambiguity, and choosing the one on the side a caption is usually printed
 * would be a guess dressed as a convention.
 */
export function resolveTableCell(index: LayerIndex, request: CellRequest): Resolution {
  if (!ALIGNED_NORMALISERS.has(index.normaliser))
    return refuse("no_column_geometry", `${index.normaliser} prints no column positions, so a row and column cannot be crossed`, index.layer_sha256);
  const word = request.anchor.kind === "figure" ? "Figure" : "Table";
  const captions = captionLines(index, word, request.anchor.value);
  if (captions.length === 0) return refuse("anchor_not_found", `no caption line names ${word} ${request.anchor.value}`, index.layer_sha256);

  // Three regions, in the order of how well the layout places them, and the first that answers
  // decides. A table sits under its caption on the caption's own page; failing that, above it on
  // the caption's own page, which is the paper that prints captions under tables; failing both,
  // past the page boundary, which is the caption standing at the foot of its page.
  //
  // Reading them on equal terms instead was built and measured: it withdrew 408 spans, 384 of
  // them printing the stored value exactly, for the reason `blockAbove` gives. Within one stage
  // the regions are read on equal terms and two that both answer are refused, because there the
  // layout says nothing to tell them apart.
  const stages = [tableWindow, blockAbove, widerWindow];
  let blocks = 0;
  let refusal: Extract<Resolution, { ok: false }> | null = null;
  for (const stage of stages) {
    const hits: Extract<Resolution, { ok: true }>[] = [];
    for (const caption of captions) {
      const window = stage(index, caption);
      if (!window || window.to <= window.from) continue;
      blocks += 1;
      const outcome = resolveAt(index, window, request);
      if (outcome.ok) hits.push(outcome);
      else if (refusal === null || reasonOrder(outcome.reason) > reasonOrder(refusal.reason)) refusal = outcome;
    }
    if (hits.length === 1) return blocks > 1 ? { ...hits[0], anchor_candidates: blocks } : hits[0];
    if (hits.length > 1)
      return refuse(
        "anchor_ambiguous",
        `${hits.length} regions around a caption for ${word} ${request.anchor.value} hold this row and column`,
        index.layer_sha256,
      );
  }
  if (blocks === 0)
    return refuse("empty_table_window", `every caption for ${word} ${request.anchor.value} stands between two captions`, index.layer_sha256);
  return refusal ?? refuse("anchor_not_found", `no caption line names ${word} ${request.anchor.value}`, index.layer_sha256);
}

/** Index a layer for the resolvers. Re-exported here so a caller that only wants a table does
 * not have to know about the offset module. */
export { indexLayer };
