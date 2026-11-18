/** The table cell resolver, over a table grid.
 *
 * A markup text layer prints a table row as one line with the cells joined by a space, so the
 * column a cell sat in is gone before any resolver sees the characters. That is the single
 * largest reason a stored locator cannot be re-checked: measured on 2026-11-18, 10,922 locators
 * name a table, a row and a column against a JATS or HTML layer that prints no columns, and the
 * aligned-text resolver in `table.ts` can only refuse them with `no_column_geometry`. The figure
 * is the count of locators this module is handed a grid for that the same measurement with
 * `measure --no-grid` refuses for want of column geometry, and 3,767 of them resolve.
 *
 * `shared/archive/layers/grid` already keeps that geometry, as a second layer over the same
 * stored bytes: for every cell the markup wrote, the half open code point range of the
 * characters the text layer holds for it. This module reads one. Nothing is inferred from
 * whitespace and nothing is counted into place. The grid says where the cell is or the locator
 * is refused.
 *
 * What a grid can do that aligned text cannot. A two level column heading is two header rows in
 * the markup, and the grid stores `headers[column]` as one entry per header row, so a locator
 * naming a parent heading and a child heading addresses a column the text layer could never
 * have placed. 199 of the 1,167 tables in the archive carry more than one header row.
 *
 * The matching rules, in full, because this is where guessing creeps in.
 *
 * Which table. Two routes, tried in order, and the first that produces any candidate decides.
 *   A. The grid's own label, or its caption where the markup wrote no label, names the table the
 *      locator names. The test is the same caption pattern the aligned resolver uses, so "Table
 *      1" never matches "Table 10". 600 of the 1,167 tables carry a label, nearly all of them
 *      JATS.
 *   B. The text layer carries a caption line naming the table. The candidates are every table of
 *      the grid that begins in the window from that caption to the next caption, and the table
 *      standing against the caption from above, because some papers print a caption under its
 *      table and nothing in a text layer says which side a given paper uses. This is the only
 *      route for an HTML table, where 542 of 546 tables carry no label in the markup at all.
 * Where more than one table is a candidate, each is resolved and the cell is returned only if
 * exactly one of them yields it. Two tables that both hold this row under this column are a
 * genuine ambiguity and are refused with `anchor_ambiguous`. No candidate at all is
 * `anchor_not_found`.
 *
 * Which column. A column is a candidate when one level of its header path equals the column the
 * locator names, by `columnForms`, which allows a difference of decoration and a trailing
 * bracketed unit and nothing else. Equality, never containment: a header reading "CATH4.3 Test
 * CATH4.2 Test" is two headings the renderer joined and accepting it for either would return a
 * neighbouring block's number. Each further level the locator names, as a sub-column, must equal
 * a deeper level of the same path. More than one candidate column is `column_ambiguous` and
 * none is `column_not_found`. A parent heading spanning three children, named with no
 * sub-column, is three candidates and refuses: the locator does not say which child, and that is
 * the refusal this lane exists to make.
 *
 * Which row. A row of the table body is a candidate when one of its cells left of the value's
 * column prints the row label the locator names, compared by `normaliseLabel`. `cellAt` follows a
 * rowspan back to the cell that owns it, so a group label spanning three rows makes all three
 * candidates, and the rest of what the locator says identifies the row then decides between
 * them: every remaining key has to be printed somewhere on the row. No label match is
 * `row_not_found`, keys that eliminate every match are `row_key_unmatched`, and more than one
 * survivor is `row_ambiguous`. More than one candidate always refuses. It never takes the first.
 *
 * Which cell. `cellAt` at the crossing, and a cell the markup did not write or that prints
 * nothing is `cell_empty`. Never the neighbouring cell: the grid holds a cell with no offsets
 * for a blank cell and the distinction is the whole point of it.
 *
 * The span. The grid's offsets are code points, which is what a span publishes, and everything
 * that searches a JavaScript string counts UTF-16 units. The two differ from the first astral
 * character on, and 33 layers in the archive hold one, so the conversion goes through the line
 * tables of `LayerIndex` and the result is checked: the characters the span covers have to be
 * the characters the grid says the cell holds, and the span's code point offsets have to be the
 * grid's own. A grid that disagrees with its text layer is refused with `no_column_geometry`,
 * which leaves the locator in the bucket it was already in and can never read as progress.
 */
import type { Grid, GridCell, GridTable } from "../../archive/layers/grid/types";
import type { LocatorAnchor } from "../locator";
import { spanAt, type LayerIndex } from "./offsets";
import { columnForms, escape, normaliseLabel, tableWindow } from "./table";
import { refuse, type GridRoute, type RefusalReason, type Resolution } from "./types";

/** A refusal reached against a grid, tagged with the route so the measurement can count grid
 * attempts and report the two routes apart. */
const deny = (route: GridRoute, reason: RefusalReason, detail: string, layer: string): Resolution => ({
  ...refuse(reason, detail, layer),
  grid_route: route,
});

/** Any caption, of any table or figure, which is where one table's window ends and the next
 * begins. The same pattern the aligned resolver uses, repeated here because that module keeps it
 * private and this one may not change it. */
const ANY_CAPTION = /^\s*(?:Supplementary\s+|Supplemental\s+|Extended\s+Data\s+|Appendix\s+)?(?:Tables?|Figures?|Fig\.)\s*[0-9A-Z]/i;

/** What this resolver is asked for: the aligned resolver's request, and two things more that
 * only a grid can use. */
export interface GridCellRequest {
  anchor: LocatorAnchor;
  row: string;
  column: string;
  /** The rest of what the locator says identifies the row, each of which the accepted row has
   * to print. */
  keys?: string[];
  /** Further column levels the locator names, outermost first. */
  subColumns?: string[];
  /** Text that may name another level of the column's header path, used only to break a tie.
   *
   * A locator writes the level that tells two columns apart in a trailing bracket as often as
   * it writes it as a sub-column: `column 'EF1%' (Mean)` against a header whose second row
   * prints "Mean" over one of the two "EF1%" columns and "Med" over the other. 1,035 locators
   * were refused `column_ambiguous` against a labelled table on 2026-11-18, and of eleven
   * sampled, every one named a heading printed over more than one column.
   *
   * A hint never makes a match. It only narrows candidates the heading already produced, and
   * only to exactly one. So a bracket holding "PNAS PDF page 4" narrows nothing and the locator
   * is refused as it was. */
  levelHints?: string[];
}

/** Does this printed text name the table the locator names?
 *
 * The same shape as the caption pattern in `table.ts`: an optional container word, the word
 * table, the label, and then something that is not a letter or a digit, so "Table 1" does not
 * match "Table 10" and "Table S2" does not match "Table S21". */
export function namesTable(text: string, value: string): boolean {
  const pattern = new RegExp(
    `^\\s*(?:Supplementary\\s+|Supplemental\\s+|Extended\\s+Data\\s+|Appendix\\s+)?Tables?\\s*${escape(value)}(?![0-9A-Za-z])`,
    "i",
  );
  return pattern.test(text);
}

/** The first code point a table prints, and the last, over the cells the markup wrote. Null
 * where the whole table prints nothing. */
function extent(table: GridTable): { from: number; to: number } | null {
  let from = Number.POSITIVE_INFINITY;
  let to = -1;
  for (const cell of table.cells) {
    if (cell.start === null || cell.end === null) continue;
    if (cell.start < from) from = cell.start;
    if (cell.end > to) to = cell.end;
  }
  return to < 0 ? null : { from, to };
}

/** The line a code point offset falls in, by binary search over the line starts. */
function lineOfPoint(index: LayerIndex, point: number): number {
  let low = 0;
  let high = index.lines.length - 1;
  while (low < high) {
    const middle = (low + high + 1) >> 1;
    if (index.points[middle] <= point) low = middle;
    else high = middle - 1;
  }
  return low;
}

const isHighSurrogate = (unit: number): boolean => unit >= 0xd800 && unit <= 0xdbff;
const isLowSurrogate = (unit: number): boolean => unit >= 0xdc00 && unit <= 0xdfff;

/**
 * The UTF-16 offset of a code point offset, or null where the layer is shorter than that.
 *
 * The line tables make this cost one line rather than the length of the layer, which matters:
 * the longest layer holds 13,778,216 characters. Within the line the walk steps over a
 * surrogate pair as one code point, which is the whole reason this function exists.
 */
export function unitOfPoint(index: LayerIndex, point: number): number | null {
  if (point < 0) return null;
  const line = lineOfPoint(index, point);
  let unit = index.u16[line];
  let left = point - index.points[line];
  const end = Math.min(unit + index.lines[line].length, index.text.length);
  while (left > 0 && unit < end) {
    const here = index.text.charCodeAt(unit);
    unit += isHighSurrogate(here) && unit + 1 < index.text.length && isLowSurrogate(index.text.charCodeAt(unit + 1)) ? 2 : 1;
    left -= 1;
  }
  if (left === 0) return unit;
  // One past the end of a line is its separator, which is one UTF-16 unit and one code point.
  if (left === 1 && unit === end && end < index.text.length) return unit + 1;
  return null;
}

/** The tables of the grid whose own label, or whose caption where the markup wrote no label,
 * names this anchor. */
function tablesByLabel(grid: Grid, value: string): GridTable[] {
  const found: GridTable[] = [];
  for (const table of grid.tables) {
    const label = table.label?.text.trim() ?? "";
    if (label) {
      if (namesTable(label, value)) found.push(table);
      continue;
    }
    const caption = table.caption?.text.trim() ?? "";
    if (caption && namesTable(caption, value)) found.push(table);
  }
  return found;
}

/** The table that ends above a caption line with nothing but blank lines between the two, which
 * is a caption printed under its own table. Null where no table sits against it.
 *
 * Which side of a table its caption is printed on is a fact about the paper that no part of a
 * text layer states, so neither side is preferred and no distance decides it. Both the table
 * above the caption and the tables below it are candidates, and `resolveGridCell` returns a cell
 * only where exactly one of them holds the row and the column. Two tables that both do are a
 * genuine ambiguity. */
function tableAgainstCaption(index: LayerIndex, line: number, extents: { table: GridTable; at: { from: number; to: number } | null }[]): GridTable | null {
  let best: GridTable | null = null;
  let ends = -1;
  for (const entry of extents)
    if (entry.at !== null && entry.at.to <= index.points[line] && entry.at.to > ends) {
      ends = entry.at.to;
      best = entry.table;
    }
  if (best === null) return null;
  for (let above = lineOfPoint(index, ends) + 1; above < line; above += 1) if (index.lines[above].trim() !== "") return null;
  return best;
}

/**
 * The tables of the grid a caption line of the text layer naming this anchor could belong to.
 *
 * The only route to an HTML table, which the markup almost never labels. The window below the
 * caption is the one the aligned resolver uses, from the caption to the next caption, so a table
 * under the next caption is never taken for this one. The table standing against the caption from
 * above is a candidate too, because some papers print a caption under its table.
 */
function tablesAtCaption(index: LayerIndex, grid: Grid, value: string): GridTable[] {
  const found: GridTable[] = [];
  const extents = grid.tables.map((table) => ({ table, at: extent(table) }));
  const take = (table: GridTable | null): void => {
    if (table && !found.includes(table)) found.push(table);
  };
  for (let line = 0; line < index.lines.length; line += 1) {
    if (!namesTable(index.lines[line], value)) continue;
    if (ANY_CAPTION.test(index.lines[line])) take(tableAgainstCaption(index, line, extents));
    const window = tableWindow(index, line);
    if (window.to <= window.from) continue;
    const from = index.points[window.from];
    const to = index.points[window.to];
    for (const entry of extents) if (entry.at !== null && entry.at.from >= from && entry.at.from < to) take(entry.table);
  }
  return found;
}

/** The cell covering a coordinate, following a span back to the cell that owns it. The grid
 * module publishes the same rule; it is repeated here so this resolver depends on the grid's
 * types and not on its reader. */
function cellAt(table: GridTable, row: number, column: number): GridCell | null {
  for (const cell of table.cells)
    if (row >= cell.row && row < cell.row + cell.row_span && column >= cell.column && column < cell.column + cell.column_span) return cell;
  return null;
}

/**
 * The cells of a row that may carry its label: every cell left of the column the value is in,
 * and the first column always.
 *
 * In a plain table that is the first column and nothing else. It is not only the first column
 * because a table's leading columns often hold something else: measured on 2026-11-18, 1,028
 * locators were refused `row_not_found` against a grid holding their table, and the shape behind
 * most of them is a table whose first columns are a dataset and a method type spanning many rows
 * with the row label in the third. A locator that says `row 'Sourmash-k51'` means that third
 * column, and which column of the stub a paper puts the label in is not something a resolver can
 * be told.
 *
 * Nothing here chooses between them. `cellAt` follows a rowspan back to the cell that owns it, so
 * a group label spanning three rows makes all three rows candidates and the label of a row makes
 * one, and either way more than one candidate row refuses unless the locator's own keys leave a
 * single one. Widening the cells a label may be found in therefore widens what can resolve and
 * what refuses, and never what is chosen. Measured over the store: `row_not_found` against a
 * grid holding the table fell from 1,028 to 80, in the same change as the level hints below, and
 * no span the grid resolver returns prints anything other than the stored value.
 */
function labelCells(table: GridTable, row: number, before: number): GridCell[] {
  const found: GridCell[] = [];
  const limit = Math.min(Math.max(before, 1), table.columns);
  for (let column = 0; column < limit; column += 1) {
    const cell = cellAt(table, row, column);
    if (cell && !found.includes(cell)) found.push(cell);
  }
  return found;
}

/** Every distinct cell the row covers, left to right, including a group label spanning into it
 * from above. This is what a row key has to be printed in. */
function rowCells(table: GridTable, row: number): GridCell[] {
  const found: GridCell[] = [];
  for (let column = 0; column < table.columns; column += 1) {
    const cell = cellAt(table, row, column);
    if (cell && !found.includes(cell)) found.push(cell);
  }
  return found;
}

/** The columns whose header path names the column the locator names, with each sub-column
 * matched at a deeper level of the same path, and the level each match was made at. */
function columnsNamed(table: GridTable, column: string, subColumns: string[]): { at: number; level: number }[] {
  const wanted = columnForms(column);
  const deeper = subColumns.map(columnForms);
  const found: { at: number; level: number }[] = [];
  for (let at = 0; at < table.headers.length; at += 1) {
    const path = table.headers[at];
    let level = -1;
    for (let l = 0; l < path.length; l += 1)
      if (columnForms(path[l]).some((form) => wanted.includes(form))) {
        level = l;
        break;
      }
    if (level < 0) continue;
    let placed = true;
    for (const sub of deeper) {
      let next = -1;
      for (let l = level + 1; l < path.length; l += 1)
        if (columnForms(path[l]).some((form) => sub.includes(form))) {
          next = l;
          break;
        }
      if (next < 0) {
        placed = false;
        break;
      }
      level = next;
    }
    if (placed) found.push({ at, level });
  }
  return found;
}

/** The candidates whose header path also prints one of the hints, at a level other than the one
 * the column name was matched at.
 *
 * Narrowing only. The result is used where it leaves exactly one candidate and discarded
 * otherwise, so a hint that names nothing in the table changes no outcome. */
function narrowByHints(table: GridTable, candidates: { at: number; level: number }[], hints: string[]): { at: number; level: number }[] {
  const wanted = hints.map(columnForms);
  return candidates.filter((candidate) =>
    table.headers[candidate.at].some(
      (text, level) => level !== candidate.level && text.trim() !== "" && columnForms(text).some((form) => wanted.some((hint) => hint.includes(form))),
    ),
  );
}

/** One table's worth of work: the column, the row, the cell and the span. */
function resolveIn(index: LayerIndex, route: GridRoute, table: GridTable, request: GridCellRequest): Resolution {
  const layer = index.layer_sha256;
  const subColumns = request.subColumns ?? [];
  const hints = (request.levelHints ?? []).filter((hint) => hint.trim() !== "");
  const matched = columnsNamed(table, request.column, subColumns);
  const named = [request.column, ...subColumns].map((text) => `"${text}"`).join(" then ");
  if (matched.length === 0)
    return deny(
      route,
      "column_not_found",
      `table ${table.index} carries ${table.header_rows} header row(s) and none of its ${table.columns} column headings is ${named}`,
      layer,
    );
  const narrowed = matched.length > 1 && hints.length > 0 ? narrowByHints(table, matched, hints) : matched;
  const columns = narrowed.length === 1 ? narrowed : matched;
  if (columns.length > 1)
    return deny(
      route,
      "column_ambiguous",
      `${columns.length} columns of table ${table.index} carry the heading ${named}` +
        (hints.length > 0 ? ` and ${narrowed.length} of them also print ${hints.map((hint) => `"${hint}"`).join(" or ")}` : ""),
      layer,
    );
  const column = columns[0].at;

  const wantedRow = normaliseLabel(request.row);
  const labelled: number[] = [];
  for (let row = table.header_rows; row < table.rows; row += 1)
    if (labelCells(table, row, column).some((cell) => normaliseLabel(cell.text) === wantedRow)) labelled.push(row);
  if (labelled.length === 0)
    return deny(route, "row_not_found", `no body row of table ${table.index} prints the row label "${request.row}" in a column left of "${request.column}"`, layer);

  const wantedColumn = columnForms(request.column);
  const keys = (request.keys ?? []).map(normaliseLabel).filter((key) => key !== "" && key !== wantedRow && !wantedColumn.includes(key));
  const rows = keys.length === 0
    ? labelled
    : labelled.filter((row) => {
        const printed = normaliseLabel(rowCells(table, row).map((cell) => cell.text).join(" "));
        return keys.every((key) => printed.includes(key));
      });
  if (rows.length === 0)
    return deny(
      route,
      "row_key_unmatched",
      `the row "${request.row}" is printed in table ${table.index}, and not on a row that also prints ${keys.map((key) => `"${key}"`).join(" and ")}`,
      layer,
    );
  if (rows.length > 1)
    return deny(route, "row_ambiguous", `${rows.length} body rows of table ${table.index} print the row label "${request.row}"`, layer);
  const row = rows[0];

  const cell = cellAt(table, row, column);
  if (cell === null) return deny(route, "cell_empty", `table ${table.index} writes no cell at row ${row}, column ${column}`, layer);
  if (cell.start === null || cell.end === null)
    return deny(route, "cell_empty", `the cell at row ${row}, column ${column} of table ${table.index} prints nothing`, layer);

  const from = unitOfPoint(index, cell.start);
  const to = unitOfPoint(index, cell.end);
  if (from === null || to === null)
    return deny(
      route,
      "no_column_geometry",
      `the grid puts the cell at code points [${cell.start}, ${cell.end}) and the layer holds fewer characters than that`,
      layer,
    );
  const span = spanAt(index, from, to);
  // The one check this resolver makes on the grid it was handed. A grid whose offsets do not
  // print the characters it says they do is addressing a document the archive does not hold, and
  // the answer to that is the refusal the locator already had.
  if (span.exact !== cell.text || span.start !== cell.start || span.end !== cell.end)
    return deny(
      route,
      "no_column_geometry",
      `the grid says the cell at row ${row}, column ${column} of table ${table.index} is code points ` +
        `[${cell.start}, ${cell.end}) and the layer prints something else there`,
      layer,
    );

  const stub = labelCells(table, row, column).find((candidate) => normaliseLabel(candidate.text) === wantedRow);
  const path = table.headers[column] ?? [];
  return {
    ok: true,
    kind: "grid_cell",
    span,
    layer_sha256: layer,
    row_label: stub?.text ?? "",
    column_header: path.filter((level) => level.trim() !== "").join(" / "),
    grid_route: route,
  };
}

/**
 * The cell a table locator names in a grid, or a refusal.
 *
 * `grid` has to be the grid over this very text layer. The caller is the dispatcher in
 * `index.ts`, which checks that, and this checks it again: a grid over another layer carries
 * offsets into another document.
 */
export function resolveGridCell(index: LayerIndex, grid: Grid, request: GridCellRequest): Resolution {
  const layer = index.layer_sha256;
  if (grid.text_layer_sha256 !== layer)
    return deny(
      "none",
      "no_column_geometry",
      `the grid addresses layer ${grid.text_layer_sha256.slice(0, 12)} and this is ${layer.slice(0, 12)}`,
      layer,
    );
  if (request.anchor.kind === "figure") return deny("none", "no_resolver_for_kind", "a figure anchor names no table of the grid", layer);

  const byLabel = tablesByLabel(grid, request.anchor.value);
  const candidates = byLabel.length > 0 ? byLabel : tablesAtCaption(index, grid, request.anchor.value);
  if (candidates.length === 0)
    return deny(
      "none",
      "anchor_not_found",
      `no table of the grid is labelled Table ${request.anchor.value} and no caption line in the layer names one`,
      layer,
    );
  const route: GridRoute = byLabel.length > 0 ? "label" : "caption_window";

  const hits: Extract<Resolution, { ok: true }>[] = [];
  let last: Resolution | null = null;
  for (const table of candidates) {
    const outcome = resolveIn(index, route, table, request);
    if (outcome.ok) hits.push(outcome);
    else last = outcome;
  }
  if (hits.length > 1)
    return deny(
      route,
      "anchor_ambiguous",
      `${hits.length} of ${candidates.length} tables found by ${route} hold the row "${request.row}" under the column "${request.column}"`,
      layer,
    );
  if (hits.length === 1) return candidates.length > 1 ? { ...hits[0], anchor_candidates: candidates.length } : hits[0];
  return last ?? deny(route, "anchor_not_found", `no table of the grid names Table ${request.anchor.value}`, layer);
}

/**
 * The two things a grid can read off a parsed locator that aligned text cannot, added to the
 * request the dispatcher has already built.
 *
 * Deeper column levels. The grammar reads `columns 'Random Split' / 'Expression' / 'R2'` as one
 * column selector and two selectors keyed `/`, because a slash is a continuation and not a
 * keyword, and the dispatcher's role reading puts those two among the keys the row has to print.
 * They are not row keys: they are the rest of the column's header path, and the string says so by
 * printing them after the column and not after the row. Each continuation is therefore attached
 * to whichever of the row or the column was named last before it. Nothing about the grammar
 * changes and the aligned resolver is not touched, because a two level header is not something
 * aligned text can place anyway.
 *
 * Level hints. A note in brackets is where a locator writes the level that tells two columns
 * apart about as often as it writes it as a sub-column. The hints only narrow.
 */
export function gridRequest(
  parsed: { selectors: { key: string; value: string | null }[]; qualifiers: { kind: string; text: string }[] },
  base: GridCellRequest,
  roleOf: (key: string) => "row" | "column" | "other",
): GridCellRequest {
  const continued: { row: string[]; column: string[] } = { row: [], column: [] };
  let last: "row" | "column" | null = null;
  for (const selector of parsed.selectors) {
    if (selector.value === null) continue;
    const role = roleOf(selector.key);
    if (role === "row" || role === "column") {
      last = role;
      continue;
    }
    if (/^[/|>+]$/.test(selector.key.trim()) && last !== null) continued[last].push(selector.value);
  }
  const hints = parsed.qualifiers
    .filter((qualifier) => qualifier.kind === "note")
    .map((qualifier) => qualifier.text.replace(/^\(|\)$/g, "").trim())
    .filter((text) => text !== "");
  const subColumns = [...(base.subColumns ?? []), ...continued.column.filter((value) => !(base.subColumns ?? []).includes(value))];
  // A continuation read as a column level is not also a row key. Leaving it in both would make
  // the row require a heading to be printed on it, which refuses every row.
  const keys = (base.keys ?? []).filter((key) => !continued.column.includes(key));
  return { ...base, keys, subColumns, levelHints: hints };
}

/** Which route would find the table, with no cell resolution, and `none` where neither does.
 * The two are reported apart, because a label is what the markup wrote on the table and a
 * caption window is a line of prose above it, which is the weaker evidence. */
export function gridRouteFor(index: LayerIndex, grid: Grid, value: string): GridRoute {
  if (tablesByLabel(grid, value).length > 0) return "label";
  return tablesAtCaption(index, grid, value).length > 0 ? "caption_window" : "none";
}
