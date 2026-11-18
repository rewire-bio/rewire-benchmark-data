/** Reading the tables out of a markup document, with no second parser.
 *
 * The text layer is built by one scan of the markup. This listens to that
 * same scan, so a cell's characters are the characters the layer holds and
 * not a second rendering of them that happens to look similar. There is no
 * way for the grid and the text to drift, because there is one scan.
 *
 * What the markup is read as. Both JATS and HTML write a table the same way
 * here: `table`, `tr`, `td` and `th`, with `thead` marking the header rows
 * and `colspan` and `rowspan` as attributes. That is what the store holds.
 * Measured over the 436 JATS and HTML layers the archive has on 2026-11-18:
 * 1,210 `table` elements, 67,496 `td`, 6,094 `th`, 826 `thead`, 0 `tgroup`
 * and 13 `entry`. CALS tables, which would need `namest`, `nameend` and
 * `morerows`, are not present, so they are not read and a document that
 * used them would produce no grid rather than a wrong one.
 *
 * What is recovered and what is refused. A span is the number the markup
 * writes. A header row is a row the markup marks, by `thead` or by writing
 * every cell as `th`. Where the markup marks neither, `header_rows` is 0
 * and the grid says so; it does not pick the first row and hope. A cell the
 * markup leaves out is left out, and a cell that prints nothing carries no
 * offsets, so a resolver refuses it rather than returning its neighbour.
 *
 * Tag soup. A document that omits `</td>` or `</tr>` is closed implicitly
 * at the next cell, row, section or table, which is what a browser does and
 * is deterministic. Nothing else is repaired.
 */
import { scanRaw, tidyTraced, type ScanRules } from "../markup";
import type { Grid, GridCell, GridNormaliser, GridRange, GridTable } from "./types";

/** A cell span the markup may legally write. Past this the number is not a
 * table, and the cell is placed at 1 with the fact recorded. */
const MAX_SPAN = 1000;
/** Coordinates one table may cover. A document that asks for more is not
 * describing a table a reader read. */
const MAX_COORDINATES = 1_000_000;
/** Columns one table may have. The coordinate key packs a row and a column
 * into one integer, and this is where the column part ends. */
const COLUMN_LIMIT = 4096;

/** A half open range of the untidied scan, before it is mapped onto the
 * layer. -1 means nothing was written there. */
interface RawRange {
  from: number;
  to: number;
}

const empty = (): RawRange => ({ from: -1, to: -1 });

function extend(range: RawRange, from: number, to: number): void {
  if (range.from < 0) range.from = from;
  range.to = to;
}

interface RawCell {
  header: boolean;
  row_span: number;
  column_span: number;
  range: RawRange;
  row: number;
  column: number;
}

interface RawRow {
  cells: RawCell[];
  /** The row sits inside a thead. */
  marked: boolean;
}

interface RawTable {
  index: number;
  rows: RawRow[];
  problems: string[];
  label: RawRange | null;
  caption: RawRange | null;
  /** Open state while the scan runs. */
  row: RawRow | null;
  cell: RawCell | null;
  head: number;
  /** The document holds a thead somewhere in this table. */
  any_head: boolean;
}

interface Wrap {
  label: RawRange | null;
  caption: RawRange | null;
  tables: RawTable[];
}

/** The value of one attribute, quoted or not. */
function attribute(attributes: string, name: string): string | null {
  const pattern = new RegExp(`(?:^|\\s)${name}\\s*=\\s*("([^"]*)"|'([^']*)'|([^\\s"'>]+))`, "i");
  const match = pattern.exec(attributes);
  if (!match) return null;
  return match[2] ?? match[3] ?? match[4] ?? null;
}

/** A span attribute as a whole number of cells. Anything else is one cell
 * and a recorded problem, because a span nobody can read is not evidence
 * that the cell is wider. */
function span(attributes: string, name: string, problems: string[], where: string): number {
  const written = attribute(attributes, name);
  if (written === null) return 1;
  const value = Number.parseInt(written.trim(), 10);
  if (!Number.isInteger(value) || value < 1) {
    problems.push(`${where} writes ${name}="${written}", which is not a count of cells, so it is placed as one`);
    return 1;
  }
  if (value > MAX_SPAN) {
    problems.push(`${where} writes ${name}="${written}", over the ${MAX_SPAN} cell limit, so it is placed as one`);
    return 1;
  }
  return value;
}

/** Every table the markup writes, in document order, with each cell's range
 * in the untidied scan. */
function readTables(markup: string, rules: ScanRules): { raw: string; tables: RawTable[] } {
  const tables: RawTable[] = [];
  const open: RawTable[] = [];
  const wraps: Wrap[] = [];
  /** The label or caption being read, and what it belongs to. */
  let capture: { range: RawRange; name: string; depth: number; assign: (range: RawRange) => void } | null = null;

  const top = (): RawTable | null => (open.length ? open[open.length - 1] : null);

  const closeCell = (table: RawTable): void => {
    table.cell = null;
  };
  const closeRow = (table: RawTable): void => {
    closeCell(table);
    table.row = null;
  };

  const startCapture = (name: string): void => {
    if (capture) {
      if (capture.name === name) capture.depth += 1;
      return;
    }
    const table = top();
    const wrap = wraps.length ? wraps[wraps.length - 1] : null;
    if (!table && !wrap) return;
    const range = empty();
    const assign = (value: RawRange): void => {
      const field = name === "label" ? "label" : "caption";
      if (table) {
        if (table[field] === null) table[field] = value;
      } else if (wrap && wrap[field] === null) wrap[field] = value;
    };
    capture = { range, name, depth: 1, assign };
  };

  const endCapture = (name: string): void => {
    if (!capture || capture.name !== name) return;
    capture.depth -= 1;
    if (capture.depth > 0) return;
    closeCapture();
  };

  /** End the capture wherever it has got to. A document that omits
   * `</caption>` would otherwise read the rest of itself as the caption. */
  const closeCapture = (): void => {
    if (!capture) return;
    if (capture.range.from >= 0) capture.assign(capture.range);
    capture = null;
  };

  /** The elements a caption or a label cannot run past. */
  const structure = new Set(["table", "table-wrap", "thead", "tbody", "tfoot", "tr", "td", "th"]);

  const events = {
    open: (name: string, attributes: string): void => {
      if (structure.has(name)) closeCapture();
      if (name === "table-wrap") {
        wraps.push({ label: null, caption: null, tables: [] });
        return;
      }
      if (name === "table") {
        const table: RawTable = {
          index: tables.length,
          rows: [],
          problems: [],
          label: null,
          caption: null,
          row: null,
          cell: null,
          head: 0,
          any_head: false,
        };
        tables.push(table);
        open.push(table);
        if (wraps.length) wraps[wraps.length - 1].tables.push(table);
        return;
      }
      if (name === "caption" || name === "label") {
        startCapture(name);
        return;
      }
      const table = top();
      if (!table) return;
      if (name === "thead") {
        closeRow(table);
        table.head += 1;
        table.any_head = true;
        return;
      }
      if (name === "tbody" || name === "tfoot") {
        closeRow(table);
        return;
      }
      if (name === "tr") {
        closeRow(table);
        table.row = { cells: [], marked: table.head > 0 };
        table.rows.push(table.row);
        return;
      }
      if (name === "td" || name === "th") {
        closeCell(table);
        if (!table.row) {
          table.row = { cells: [], marked: table.head > 0 };
          table.rows.push(table.row);
          table.problems.push(`a ${name} outside any tr, placed in a row of its own`);
        }
        const where = `table ${table.index}, row ${table.rows.length}`;
        const cell: RawCell = {
          header: name === "th",
          row_span: span(attributes, "rowspan", table.problems, where),
          column_span: span(attributes, "colspan", table.problems, where),
          range: empty(),
          row: -1,
          column: -1,
        };
        table.row.cells.push(cell);
        table.cell = cell;
      }
    },
    close: (name: string): void => {
      if (name === "caption" || name === "label") {
        endCapture(name);
        return;
      }
      if (name === "table" || name === "table-wrap") closeCapture();
      if (name === "table-wrap") {
        const wrap = wraps.pop();
        if (!wrap) return;
        for (const table of wrap.tables) {
          if (table.label === null) table.label = wrap.label;
          if (table.caption === null) table.caption = wrap.caption;
        }
        return;
      }
      const table = top();
      if (!table) return;
      if (name === "td" || name === "th") closeCell(table);
      else if (name === "tr") closeRow(table);
      else if (name === "thead") table.head = Math.max(0, table.head - 1);
      else if (name === "table") {
        closeRow(table);
        open.pop();
      }
    },
    text: (from: number, to: number): void => {
      if (capture) extend(capture.range, from, to);
      // A nested table's text is inside the outer cell as well, so every
      // open cell grows. The inner table keeps its own cell either way.
      for (const table of open) if (table.cell) extend(table.cell.range, from, to);
    },
  };

  const raw = scanRaw(markup, rules, events);
  return { raw, tables };
}

/** Where every cell sits, once the spans are expanded.
 *
 * The rule is the one a browser applies: a cell takes the first free
 * coordinate on its row and then occupies its span. Nothing is moved to
 * make a table rectangular, so a row that is short is short. */
function place(table: RawTable): { columns: number; cover: Map<number, RawCell> } {
  const taken = new Set<number>();
  const cover = new Map<number, RawCell>();
  let columns = 0;
  let coordinates = 0;
  let overflowed = false;
  const key = (row: number, column: number): number => row * COLUMN_LIMIT + column;
  table.rows.forEach((row, index) => {
    let column = 0;
    for (const cell of row.cells) {
      while (column < COLUMN_LIMIT && taken.has(key(index, column))) column += 1;
      if (column >= COLUMN_LIMIT) {
        if (!overflowed) {
          table.problems.push(`the table runs past column ${COLUMN_LIMIT}, so the rest of it is not placed`);
          overflowed = true;
        }
        return;
      }
      cell.row = index;
      cell.column = column;
      coordinates += cell.row_span * cell.column_span;
      if (coordinates > MAX_COORDINATES) {
        if (!overflowed) {
          table.problems.push(`the spans cover more than ${MAX_COORDINATES} coordinates, so the rest of the table is not placed`);
          overflowed = true;
        }
        return;
      }
      for (let r = index; r < index + cell.row_span; r += 1)
        for (let c = column; c < column + cell.column_span && c < COLUMN_LIMIT; c += 1) {
          taken.add(key(r, c));
          if (r < table.rows.length && !cover.has(key(r, c))) cover.set(key(r, c), cell);
        }
      column += cell.column_span;
      if (column > columns) columns = column;
    }
  });
  if (columns > COLUMN_LIMIT) columns = COLUMN_LIMIT;
  return { columns, cover };
}

/** Leading rows the markup marks as the header.
 *
 * Marked by `thead` where the document uses one. Where it does not, a
 * leading row whose every cell is a `th` is a header row, which is how a
 * JATS table without a thead writes one. Where the markup marks neither,
 * the answer is zero: a resolver is told there is no header rather than
 * being handed the first row as though the document had said so. */
function headerRows(table: RawTable): number {
  let count = 0;
  for (const row of table.rows) {
    const marked = table.any_head ? row.marked : row.cells.length > 0 && row.cells.every((cell) => cell.header);
    if (!marked) break;
    count += 1;
  }
  return count;
}

/** The map from the untidied scan onto the layer, and code point offsets. */
interface Mapping {
  text: string;
  out: Int32Array;
  /** Code points before each UTF-16 index of `text`. */
  points: Int32Array;
}

function mapping(raw: string): Mapping {
  const { text, out } = tidyTraced(raw);
  const points = new Int32Array(text.length + 1);
  let count = 0;
  for (let index = 0; index < text.length; index += 1) {
    points[index] = count;
    const unit = text.charCodeAt(index);
    const low = index + 1 < text.length ? text.charCodeAt(index + 1) : 0;
    if (unit >= 0xd800 && unit <= 0xdbff && low >= 0xdc00 && low <= 0xdfff) {
      points[index + 1] = count;
      index += 1;
    }
    count += 1;
  }
  points[text.length] = count;
  return { text, out, points };
}

/** The layer characters a raw range became, trimmed of the whitespace the
 * boundaries put around it. Null when the range prints nothing. */
function range(map: Mapping, raw: RawRange): GridRange | null {
  if (raw.from < 0) return null;
  let first = -1;
  let last = -1;
  for (let index = raw.from; index < raw.to && index < map.out.length; index += 1) {
    const at = map.out[index];
    if (at < 0) continue;
    if (/\s/.test(map.text[at])) continue;
    if (first < 0) first = at;
    last = at;
  }
  if (first < 0) return null;
  const end = last + 1;
  return { start: map.points[first], end: map.points[end], text: map.text.slice(first, end) };
}

/**
 * The grid for one markup document.
 *
 * `markup` is the decoded source and `rules` are the normaliser's own, so
 * the text this walks is the text the layer holds. The caller checks that
 * by hashing it.
 */
export function gridOf(
  markup: string,
  rules: ScanRules,
  normaliser: GridNormaliser,
  textNormaliser: string,
  textLayerSha256: string,
): { grid: Grid; text: string } {
  const { raw, tables } = readTables(markup, rules);
  const map = mapping(raw);
  const built: GridTable[] = [];
  for (const table of tables) {
    const { columns, cover } = place(table);
    const header_rows = headerRows(table);
    const cells: GridCell[] = [];
    for (const row of table.rows)
      for (const cell of row.cells) {
        if (cell.row < 0) continue;
        const where = range(map, cell.range);
        cells.push({
          row: cell.row,
          column: cell.column,
          row_span: cell.row_span,
          column_span: cell.column_span,
          header: cell.header,
          start: where ? where.start : null,
          end: where ? where.end : null,
          text: where ? where.text : "",
        });
      }
    cells.sort((a, b) => a.row - b.row || a.column - b.column);
    const headers: string[][] = [];
    for (let column = 0; column < columns; column += 1) {
      const path: string[] = [];
      for (let level = 0; level < header_rows; level += 1) {
        const cell = cover.get(level * COLUMN_LIMIT + column);
        const where = cell ? range(map, cell.range) : null;
        path.push(where ? where.text : "");
      }
      headers.push(path);
    }
    built.push({
      index: table.index,
      rows: table.rows.length,
      columns,
      header_rows,
      headers,
      label: table.label ? range(map, table.label) : null,
      caption: table.caption ? range(map, table.caption) : null,
      cells,
      problems: table.problems,
    });
  }
  return {
    grid: { normaliser, text_layer_sha256: textLayerSha256, text_normaliser: textNormaliser, tables: built },
    text: map.text,
  };
}
