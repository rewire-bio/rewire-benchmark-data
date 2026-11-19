/** The sheet cell resolver, ADR 0002 step 5.
 *
 * The failure this file exists to rule out is one off. A sheet block opens with a header line
 * that is not a sheet row, so sheet row R is the layer line at the block's header line plus R.
 * A resolver that read the layer as a delimited file would take row R as layer line R, which is
 * one line out on the first sheet and thousands of lines out on a later one, and the span would
 * still hold a plausible number. So the first test here takes a workbook the store holds, reads
 * the ground truth from the workbook's own cell references rather than from the text layer, and
 * checks that the row the resolver lands on is the row the spreadsheet calls that number, and
 * that the rows either side of it hold something else.
 *
 * The rest is the refusals. A locator that names no sheet, or a sheet the workbook does not
 * hold, is refused and never answered from the first sheet. A row label or key the addressed row
 * does not hold is refused and the resolver does not go looking for the row that does.
 *
 * Everything here is offline and calls no model. The test that needs the workbook's bytes skips
 * when the object cache is not on this machine, because the cache is gitignored by design.
 */
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { hasObject, readObject } from "../scripts/archive/objects";
import { blockMarker, readPackage, readWorkbook } from "../shared/archive/layers/office/index";
import { cellRangeByReference } from "../shared/archive/layers/office/address";
import { layerText, readRegistry } from "../shared/omics/layers/index";
import { parseLocator } from "../shared/omics/locator";
import { blocksOf, indexLayer, resolveLocator, resolveSheetCell, sheetRequest, type Resolution } from "../shared/omics/spans/index";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const reasonOf = (outcome: Resolution): string => (outcome.ok ? `resolved ${outcome.kind}` : outcome.reason);
const textOf = (outcome: Resolution): string => (outcome.ok ? outcome.span.exact : `refused ${outcome.reason}: ${outcome.detail}`);

/** A layer in the shape `ooxml-sheet-tsv@1` writes: two sheets, each its own block, each opening
 * with a header line that is not a row of the sheet. The second block is what makes an off-by-one
 * visible: its rows start 5 lines into the layer. */
const fixture = [
  `${blockMarker}1\tSummary\tA1:C3`,
  "Method\tAUROC\tAUPRC",
  "Delly\t0.91",
  "Manta\t0.88\t0.74",
  `${blockMarker}2\tBlocks\tA1:D4`,
  "Dataset\tCaller\tRecall\tPrecision",
  "CLL\tLoFreq\t0.42\t0.07",
  "\tStrelka\t0.68\t0.17",
  "MB\tLoFreq\t0.51\t0.09",
  "",
].join("\n");

const index = indexLayer(fixture, "f".repeat(64), "ooxml-sheet-tsv@1");

describe("a sheet block is not a file", () => {
  it("reads row 1 of a sheet as the line after that sheet's own header line", () => {
    expect(textOf(resolveSheetCell(index, { sheet: "Summary", cell: "B1" }))).toBe("AUROC");
    expect(textOf(resolveSheetCell(index, { sheet: "Summary", cell: "B2" }))).toBe("0.91");
  });

  it("counts the rows of a later sheet from that sheet's header line and not from the layer", () => {
    // Row 2 of the second sheet is layer line 6. Layer line 2 is row 1 of the first sheet, and a
    // resolver that counted layer lines would answer with its text and no error.
    expect(textOf(resolveSheetCell(index, { sheet: "Blocks", cell: "C2" }))).toBe("0.42");
    expect(index.lines[2]).toBe("Delly\t0.91");
  });

  it("gives a different span for the row above and the row below", () => {
    const wanted = textOf(resolveSheetCell(index, { sheet: "Blocks", cell: "C3" }));
    expect(wanted).toBe("0.68");
    expect(textOf(resolveSheetCell(index, { sheet: "Blocks", cell: "C2" }))).not.toBe(wanted);
    expect(textOf(resolveSheetCell(index, { sheet: "Blocks", cell: "C4" }))).not.toBe(wanted);
  });

  it("holds the three blocks of the layer apart", () => {
    expect(blocksOf(index).map((block) => `${block.name}:${block.rows}`)).toEqual(["Summary:3", "Blocks:4"]);
  });
});

describe("a workbook is not one table", () => {
  it("refuses a cell reference that names no sheet", () => {
    const outcome = resolveSheetCell(index, { sheet: null, cell: "B2" });
    expect(reasonOf(outcome)).toBe("no_anchor");
    // The refusal says what the workbook holds, and it is not the first sheet's answer.
    expect(outcome.ok === false && outcome.detail).toContain("Summary");
  });

  it("refuses a sheet the workbook does not hold rather than falling back to the first", () => {
    const outcome = resolveSheetCell(index, { sheet: "Table S4", cell: "B2" });
    expect(reasonOf(outcome)).toBe("anchor_not_found");
  });

  it("refuses a row past the end of the block it names", () => {
    expect(reasonOf(resolveSheetCell(index, { sheet: "Summary", cell: "B9" }))).toBe("row_not_found");
  });

  it("refuses a cell the sheet leaves empty", () => {
    expect(reasonOf(resolveSheetCell(index, { sheet: "Summary", cell: "C2" }))).toBe("cell_empty");
  });
});

describe("the labels a locator prints beside the address", () => {
  it("takes a key the sheet prints once above the rows it covers", () => {
    const outcome = resolveSheetCell(index, {
      sheet: "Blocks",
      cell: "C3",
      rowKeys: [
        { key: "dataset", value: "CLL" },
        { key: "caller", value: "Strelka" },
      ],
    });
    expect(textOf(outcome)).toBe("0.68");
  });

  it("refuses a key the addressed row does not hold, and does not move to the row that does", () => {
    const outcome = resolveSheetCell(index, {
      sheet: "Blocks",
      cell: "C2",
      rowKeys: [
        { key: "dataset", value: "CLL" },
        { key: "caller", value: "Strelka" },
      ],
    });
    expect(reasonOf(outcome)).toBe("row_key_unmatched");
  });

  it("refuses a key whose own column holds another value, where a looser check would pass", () => {
    // `MB` is printed in the dataset column of row 4, so a check that asked only whether the
    // sheet prints it anywhere would accept this row. The key names a column the sheet heads, so
    // it is checked against that column alone.
    const outcome = resolveSheetCell(index, {
      sheet: "Blocks",
      cell: "C2",
      rowKeys: [{ key: "dataset", value: "MB" }],
    });
    expect(reasonOf(outcome)).toBe("row_key_unmatched");
  });

  it("refuses a column heading the address contradicts", () => {
    const outcome = resolveSheetCell(index, { sheet: "Summary", cell: "B3", columnHeader: "AUPRC" });
    expect(reasonOf(outcome)).toBe("column_not_found");
  });

  it("takes the column from the heading where the locator gives a row and no reference", () => {
    expect(textOf(resolveSheetCell(index, { sheet: "Summary", row: 3, columnHeader: "AUPRC" }))).toBe("0.74");
  });

  it("refuses two claims about one row", () => {
    expect(reasonOf(resolveSheetCell(index, { sheet: "Summary", cell: "B3", row: 2 }))).toBe("row_ambiguous");
  });
});

// The sheet resolver is on by default, and the test below pins that: a caller that says nothing
// about sheets gets the blocks read. The flag is the other arm of the paired run that measures
// what the blocks are worth, so the first two tests here name it either way.
describe("the dispatch onto a sheet layer", () => {
  it("reads a locator written in the bang form", () => {
    const outcome = resolveLocator(parseLocator("'Blocks'!C3"), index, null, { sheet: true });
    expect(outcome.ok && outcome.kind).toBe("sheet_cell");
    expect(textOf(outcome)).toBe("0.68");
  });

  it("leaves the sheet layer where it was when the toggle is off", () => {
    const outcome = resolveLocator(parseLocator("'Blocks'!C3"), index, null, { sheet: false });
    expect(outcome.ok).toBe(false);
  });

  // Passing the flag on is not the shipped path. No library caller passes a sheet flag at all,
  // so the guard the shipped path runs through is the one that reads an absent flag. Written with
  // the options argument omitted and again with an options object that says nothing about sheets,
  // because those are the shapes a caller actually writes: a guard reading `options.sheet === true`
  // passes the first test above and fails every one of these.
  it("reads the sheet blocks when the caller asks for nothing", () => {
    expect(textOf(resolveLocator(parseLocator("'Blocks'!C3"), index))).toBe("0.68");
    expect(textOf(resolveLocator(parseLocator("'Blocks'!C3"), index, null))).toBe("0.68");
    expect(textOf(resolveLocator(parseLocator("'Blocks'!C3"), index, null, {}))).toBe("0.68");
    expect(textOf(resolveLocator(parseLocator("'Blocks'!C3"), index, null, { legacyQuote: false }))).toBe("0.68");
  });

  it("reads the sheet name off a key where the grammar made no anchor of it", () => {
    const request = sheetRequest(parseLocator("Supplementary Tables workbook sheet 'Blocks', C3"));
    expect(request?.sheet).toBe("Blocks");
  });

  it("says nothing about a locator that names neither a cell nor a sheet with a row", () => {
    expect(sheetRequest(parseLocator("Table 1, row 'Delly', column 'AUROC'"))).toBeNull();
  });
});

/** The off-by-one, on a workbook the store holds.
 *
 * `model-coverage-rhofold-2024-fig2-source` is the RhoFold figure 2 source data workbook. Its
 * seventh sheet, `fig2hi`, opens 2,360 lines into the layer, and the stored locator
 * `fig2hi!D7` is the one this checks. The ground truth is the workbook itself: `readWorkbook`
 * reads the cells with the references the sheet XML writes on them, `r="D7"`, so it does not
 * share any arithmetic with the resolver under test.
 */
describe("a row resolved by number on a stored workbook", () => {
  const source = "model-coverage-rhofold-2024-fig2-source";
  const sheet = "fig2hi";
  const record = readRegistry(root).find(
    (row) => row.normaliser === "ooxml-sheet-tsv@1" && row.sanity !== "fail" && row.source_ids.includes(source),
  );

  it("lands on the row the spreadsheet calls that number, and not on its neighbours", () => {
    if (!record || !hasObject(record.object_sha256, root)) return;
    const pkg = readPackage(readObject(record.object_sha256, root));
    expect(pkg).not.toBeNull();
    const problems: string[] = [];
    const sheets = readWorkbook(pkg!, problems);
    const workbook = sheets.find((candidate) => candidate.name === sheet);
    expect(workbook).toBeDefined();
    /** The value the sheet XML carries at one A1 reference, read off the reference itself. */
    const stored = (row: number, column: number): string =>
      workbook!.cells.find((cell) => cell.row === row && cell.column === column)?.value ?? "";
    expect(stored(7, 4)).not.toBe("");

    const layer = layerText(record, root);
    const live = indexLayer(layer, record.layer_sha256, record.normaliser);
    const outcome = resolveSheetCell(live, { sheet, cell: "D7" });
    expect(outcome.ok && outcome.kind).toBe("sheet_cell");
    expect(textOf(outcome)).toBe(stored(7, 4));
    // A shift of one in either direction would have to show here, so the neighbours have to
    // differ from the cell. On this sheet they do: 7.94 and 17.99 against 12.69.
    expect(stored(6, 4)).not.toBe(stored(7, 4));
    expect(stored(8, 4)).not.toBe(stored(7, 4));
    expect(textOf(resolveSheetCell(live, { sheet, cell: "D6" }))).toBe(stored(6, 4));
    expect(textOf(resolveSheetCell(live, { sheet, cell: "D8" }))).toBe(stored(8, 4));

    // The same cell by row and column number rather than by reference, and the same answer.
    expect(textOf(resolveSheetCell(live, { sheet, row: 7, column: 4 }))).toBe(stored(7, 4));
    // And the arithmetic in shared/archive/layers/office/address.ts, which is the published
    // contract for the same addressing, agrees with the resolver on the characters and on the
    // code point offsets. The two reach them different ways: that file counts code points over
    // the layer, the resolver converts a UTF-16 offset through the per-line index.
    const range = cellRangeByReference(layer, sheet, "D7");
    expect(range?.value).toBe(stored(7, 4));
    expect(outcome.ok && outcome.span.start).toBe(range?.start);
    expect(outcome.ok && outcome.span.end).toBe(range?.end);
  });

  it("resolves the stored locator for that cell to the value its record keeps", () => {
    if (!record || !hasObject(record.object_sha256, root)) return;
    const layer = layerText(record, root);
    const live = indexLayer(layer, record.layer_sha256, record.normaliser);
    const outcome = resolveLocator(
      parseLocator("fig2hi!D7; method fig2hi!A7; target fig2hi!D1; Fig. 2h caption; XML Par13-15 and Par51"),
      live,
      null,
      { sheet: true },
    );
    expect(outcome.ok && outcome.kind).toBe("sheet_cell");
    expect(textOf(outcome)).toContain("12.69");
  });

  it("refuses a column named by a heading the sheet prints twice", () => {
    if (!record || !hasObject(record.object_sha256, root)) return;
    const live = indexLayer(layerText(record, root), record.layer_sha256, record.normaliser);
    // Row 1 of this sheet prints `R1116` over column D and again over column J, once for each of
    // the two measures the sheet holds. A heading on its own does not say which.
    expect(reasonOf(resolveSheetCell(live, { sheet, row: 7, columnHeader: "R1116" }))).toBe("column_ambiguous");
  });
});
