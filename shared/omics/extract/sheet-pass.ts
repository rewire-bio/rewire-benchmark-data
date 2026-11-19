/** Every sheet of an Office workbook, read mechanically.
 *
 * `ooxml-sheet-tsv@1` keeps the workbook's geometry: one block per sheet, one line per sheet
 * row, one tab separated field per column. So the same pass works here with no inference at
 * all, and the address is stronger than a table's: a cell has an A1 reference, which the
 * locator grammar already carries as `sheet_cell`.
 *
 * The off by one is the thing to get right and it is not this file's rule. A block opens with a
 * header line that is not a sheet row, so sheet row R is the layer line at the block's header
 * line plus R. `shared/omics/spans/sheet.ts` states that, tests it against a stored workbook,
 * and explains that reading the blocks as a plain delimited file shifts every row and still
 * returns a number, which is the worst thing a reader of this layer can do. The arithmetic here
 * is the same arithmetic.
 *
 * Row 1 is the heading row, which is where that same file says a sheet puts its column names.
 * No second heuristic is tried: a workbook whose names sit two rows down produces candidates
 * with the heading the first row prints, which is what the document prints there, and the
 * mismatch is visible in the candidate rather than papered over.
 *
 * What the workbook prints is not what a paper prints. A computed cell is stored as the full
 * double, 0.81699999999999995 where the paper shows 0.82. The candidate keeps the characters
 * the layer holds, because those are the characters the span covers.
 */
import { columnLabel, type SheetBlock } from "../../archive/layers/office/address";
import { unescapeCell } from "../../archive/layers/office/sheet";
import { readCellValue } from "./value";
import { spanAt, type LayerIndex } from "../spans/offsets";
import { blocksOf, fieldsOfLine } from "../spans/sheet";
import type { Candidate } from "./candidate";
import { buildCandidate } from "./build";
import { decideCell, headingLevels, orientationOf, type Decider } from "./decide";
import type { LayerTally } from "./grid-pass";

const valueOf = (field: { text: string } | undefined): string => (field === undefined ? "" : unescapeCell(field.text));

/** Candidates from one sheet layer, in sheet then row then column order. */
export function sheetCandidates(args: {
  decider: Decider;
  sourceId: string;
  index: LayerIndex;
  sanity: string;
}): { candidates: Candidate[]; tally: LayerTally } {
  const { decider, index } = args;
  const blocks: SheetBlock[] = blocksOf(index);
  const candidates: Candidate[] = [];
  let seen = 0;
  let header = 0;
  let label = 0;
  let empty = 0;
  let notNumeric = 0;

  for (const block of blocks) {
    if (block.rows < 1) continue;
    const headings = fieldsOfLine(index, block.header_line + 1);
    const headingText = headings.map((field) => valueOf(field).trim());
    const labelColumn = headingText.length > 1 ? 1 : -1;
    seen += headings.length;
    header += headings.length;

    const rowLabels: string[] = [];
    for (let row = 2; row <= block.rows; row += 1) rowLabels.push(valueOf(fieldsOfLine(index, block.header_line + row)[0]).trim());
    const orientation = orientationOf(decider, rowLabels, headingText);

    for (let row = 2; row <= block.rows; row += 1) {
      const fields = fieldsOfLine(index, block.header_line + row);
      const labelField = labelColumn >= 1 ? fields[labelColumn - 1] : undefined;
      const rowLabel = valueOf(labelField).trim();
      for (let column = 1; column <= fields.length; column += 1) {
        seen += 1;
        if (column === labelColumn) {
          label += 1;
          continue;
        }
        const field = fields[column - 1];
        const printed = valueOf(field);
        if (printed.trim() === "") {
          empty += 1;
          continue;
        }
        const read = readCellValue(printed);
        if (read === null) {
          notNumeric += 1;
          continue;
        }
        const { value, spread } = read;

        const heading = headingText[column - 1] ?? "";
        const levels = heading === "" ? [] : headingLevels([heading]);
        const inRows = orientation === "systems_in_rows";
        const { fields: decided, undecided } = decideCell(decider, {
          metricLevels: inRows ? levels : rowLabel === "" ? [] : [rowLabel],
          metricReadFrom: inRows ? "column_header" : "row_label",
          systemText: inRows ? rowLabel : heading,
          systemReadFrom: inRows ? "row_label" : "column_header",
          assessmentText: block.name,
          assessmentReadFrom: "sheet_name",
          printedValue: printed,
          headerPresent: inRows ? levels.length > 0 : rowLabel !== "",
          headerReason: "header_blank",
        });

        const reference = `${columnLabel(column)}${row}`;
        const headingField = headings[column - 1];
        candidates.push(
          buildCandidate({
            source_id: args.sourceId,
            layer_sha256: index.layer_sha256,
            normaliser: index.normaliser,
            route: "sheet_cell",
            grid_layer_sha256: null,
            anchor: { kind: "sheet", index: block.index, label: block.name, caption: "" },
            position: { row, column, basis: "a1" },
            row_label: rowLabel,
            column_header: heading === "" ? [] : [heading],
            header_source: "first_row",
            header_rule: null,
            fields: decided,
            printed_value: printed,
            numeric_value: value,
            uncertainty_printed: spread,
            span: spanAt(index, field.from, field.to),
            row_label_span: labelField ? spanAt(index, labelField.from, labelField.to) : null,
            column_header_span: headingField && valueOf(headingField).trim() !== "" ? spanAt(index, headingField.from, headingField.to) : null,
            address: { kind: "sheet_cell", value: reference, raw: `cell ${reference}` },
            undecided,
          }),
        );
      }
    }
  }

  return {
    candidates,
    tally: {
      layer_sha256: index.layer_sha256,
      normaliser: index.normaliser,
      sanity: args.sanity,
      route: "sheet_cell",
      tables: blocks.length,
      cells_seen: seen,
      cells_header: header,
      cells_label: label,
      cells_empty: empty,
      cells_not_numeric: notNumeric,
      candidates: candidates.length,
    },
  };
}
