/** Every table of a JATS or HTML source, read mechanically.
 *
 * A number in a table does not need a model to find it. The markup already says which cells are
 * header cells, which row a cell is in and which column, and `shared/archive/layers/grid` has
 * already turned that into a grid whose every cell names a half open code point range in the
 * text layer. So this pass walks cells, asks the shared numeric parser whether the cell prints a
 * number, and emits a candidate for each one that does, with the row label and the column
 * heading the markup itself wrote.
 *
 * Nothing is inferred except where the grid producer already put its one inference in a field
 * of its own. A table whose markup marks no header row carries `inferred_header`, which is
 * recorded as `header_source: "inferred"` with the rule's name, so a reader who declines
 * inferences has one word to filter on. A table that carries neither is read with no column
 * headings at all, and every candidate from it says so.
 *
 * What the pass refuses to do is as much the design as what it does. It does not join header
 * levels into a string the document never prints. It does not read a cell the markup wrote as
 * empty. It does not take a neighbouring cell when the one it asked for is absent. And it emits
 * no candidate without a span, because a value with no span is a value nobody can check.
 */
import { cellAt } from "../../archive/layers/grid/index";
import type { Grid, GridTable } from "../../archive/layers/grid/types";
import { readCellValue } from "./value";
import type { LayerIndex } from "../spans/offsets";
import type { Candidate, Tally } from "./candidate";
import { buildCandidate } from "./build";
import { decideCell, headingLevels, orientationOf, type Decider } from "./decide";
import { spanOfPoints } from "./points";

/** One layer's worth of counts, which is a row of the tally. */
export type LayerTally = Tally["layers"][number];

/** The header rows in force, and where they came from. */
function headersOf(table: GridTable): { rows: number; headers: string[][]; source: "markup" | "inferred" | "none"; rule: string | null } {
  if (table.header_rows > 0) return { rows: table.header_rows, headers: table.headers, source: "markup", rule: null };
  if (table.inferred_header)
    return { rows: table.inferred_header.rows, headers: table.inferred_header.headers, source: "inferred", rule: table.inferred_header.rule };
  return { rows: 0, headers: [], source: "none", rule: null };
}

/** The deepest header row that prints anything over a column, for the heading's own span. */
function headerRowFor(table: GridTable, headerRows: number, column: number): number | null {
  for (let row = headerRows - 1; row >= 0; row -= 1) {
    const cell = cellAt(table, row, column);
    if (cell && cell.start !== null && cell.text.trim() !== "") return row;
  }
  return null;
}

/** Candidates from one grid layer, in table then row then column order. */
export function gridCandidates(args: {
  decider: Decider;
  sourceId: string;
  index: LayerIndex;
  grid: Grid;
  gridLayerSha256: string;
  sanity: string;
}): { candidates: Candidate[]; tally: LayerTally } {
  const { decider, index, grid } = args;
  const candidates: Candidate[] = [];
  let seen = 0;
  let header = 0;
  let label = 0;
  let empty = 0;
  let notNumeric = 0;

  for (const table of [...grid.tables].sort((a, b) => a.index - b.index)) {
    const { rows: headerRows, headers, source: headerSource, rule } = headersOf(table);
    const tableLabel = table.label?.text ?? "";
    const caption = table.caption?.text ?? "";
    // The column the row labels are read from. A table of one column has none: every cell in
    // it is a value or is not, and nothing labels it.
    const labelColumn = table.columns > 1 ? 0 : -1;

    const rowLabels: string[] = [];
    for (let row = headerRows; row < table.rows; row += 1) {
      const cell = labelColumn >= 0 ? cellAt(table, row, labelColumn) : null;
      rowLabels.push(cell?.text.trim() ?? "");
    }
    const headingLeaves = headers.map((levels) => headingLevels(levels)[0] ?? "");
    const orientation = orientationOf(decider, rowLabels, headingLeaves);

    for (const cell of [...table.cells].sort((a, b) => a.row - b.row || a.column - b.column)) {
      seen += 1;
      if (cell.header || cell.row < headerRows) {
        header += 1;
        continue;
      }
      if (cell.column === labelColumn) {
        label += 1;
        continue;
      }
      if (cell.start === null || cell.end === null) {
        empty += 1;
        continue;
      }
      // A cell the reader returns nothing for is a dash, an "N/A", a blank, an interval with
      // no point value, or words. batch.ts has the rule and it is the same one here: that is
      // not a result, and emitting it as zero or as a missing value would put a number in the
      // store the document does not hold.
      const read = readCellValue(cell.text);
      if (read === null) {
        notNumeric += 1;
        continue;
      }
      const { value, spread } = read;

      const path = headers[cell.column] ?? [];
      const levels = headingLevels(path);
      const rowLabel = labelColumn >= 0 ? cellAt(table, cell.row, labelColumn)?.text.trim() ?? "" : "";
      const headerRow = headerRows > 0 ? headerRowFor(table, headerRows, cell.column) : null;
      const headerCell = headerRow === null ? null : cellAt(table, headerRow, cell.column);
      const labelCell = labelColumn >= 0 ? cellAt(table, cell.row, labelColumn) : null;
      const assessmentText = caption !== "" ? caption : tableLabel;

      const inRows = orientation === "systems_in_rows";
      const { fields, undecided } = decideCell(decider, {
        metricLevels: inRows ? levels : rowLabel === "" ? [] : [rowLabel],
        metricReadFrom: inRows ? "column_header" : "row_label",
        systemText: inRows ? rowLabel : levels[0] ?? "",
        systemReadFrom: inRows ? "row_label" : "column_header",
        assessmentText,
        assessmentReadFrom: caption !== "" ? "caption" : "table_label",
        printedValue: cell.text,
        headerPresent: inRows ? levels.length > 0 : rowLabel !== "",
        headerReason: headerSource === "none" ? "no_header_marked" : "header_blank",
      });

      candidates.push(
        buildCandidate({
          source_id: args.sourceId,
          layer_sha256: index.layer_sha256,
          normaliser: index.normaliser,
          route: "grid_cell",
          grid_layer_sha256: args.gridLayerSha256,
          anchor: { kind: "table", index: table.index, label: tableLabel, caption },
          position: { row: cell.row, column: cell.column, basis: "grid" },
          row_label: rowLabel,
          column_header: path,
          header_source: headerSource,
          header_rule: rule,
          fields,
          printed_value: cell.text,
          numeric_value: value,
          uncertainty_printed: spread,
          span: spanOfPoints(index, cell.start, cell.end),
          row_label_span:
            labelCell && labelCell.start !== null && labelCell.end !== null ? spanOfPoints(index, labelCell.start, labelCell.end) : null,
          column_header_span:
            headerCell && headerCell.start !== null && headerCell.end !== null
              ? spanOfPoints(index, headerCell.start, headerCell.end)
              : null,
          address: null,
          undecided,
        }),
      );
    }
  }

  return {
    candidates,
    tally: {
      layer_sha256: index.layer_sha256,
      normaliser: index.normaliser,
      sanity: args.sanity,
      route: "grid_cell",
      tables: grid.tables.length,
      cells_seen: seen,
      cells_header: header,
      cells_label: label,
      cells_empty: empty,
      cells_not_numeric: notNumeric,
      candidates: candidates.length,
    },
  };
}
