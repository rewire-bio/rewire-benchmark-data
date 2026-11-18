/** How wide a cell span may be, and which block around a caption a table is read from.
 *
 * Both are defects the resolvers shipped with, both were measured over the whole store rather
 * than noticed on an example, and both are pinned here so they cannot come back.
 *
 * 1. A field that runs across more than one column is not a cell. `pdftotext -layout` separates
 *    columns with two or more spaces, and where it leaves one space two columns arrive as one
 *    field: 66 spans on 2026-11-18 held more than one column, the worst of them three models'
 *    results with the stored value in the middle, and a containment check scored it correct.
 * 2. A caption is printed above its table in most papers and below it in some. A window that
 *    only runs downwards from the caption reads the next table on the page after it, and 24
 *    spans committed to another table's numbers that way.
 *
 * The fixtures are written to print what the real layers print. The two tests that read the
 * store skip when the object cache is not on this machine, because the cache is gitignored by
 * design.
 */
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { hasObject } from "../scripts/archive/objects";
import { layerText, readRegistry } from "../shared/omics/layers/index";
import { parseLocator } from "../shared/omics/locator";
import {
  blockAbove,
  cellWidth,
  indexLayer,
  resolveLocator,
  resolveTableCell,
  tableWindow,
  tokensOf,
  widerWindow,
  type LayerIndex,
  type RefusalReason,
  type Resolution,
} from "../shared/omics/spans/index";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const reasonOf = (outcome: Resolution): RefusalReason | "resolved" => (outcome.ok ? "resolved" : outcome.reason);
const index = (text: string, letter = "a"): LayerIndex => indexLayer(text, letter.repeat(64), "pdf-text-layer@1");

/** Two columns the renderer separated with a single space, which is the shape of the datta2026
 * layer: each cell prints three figures and the gap between two cells is one space. */
const MERGED = [
  "Table 1. Main benchmark, each cell Frozen / FT / Recovery",
  "",
  "Task                      HyenaDNA                      GENERATOR-v2            Omni-DNA",
  "H3               .6926/.779/89   .6952/.784/89 .7381/.806/92 .7220/.818/88",
  "",
].join("\n");

/** One cell wider than its own heading, which is ordinary and is not a merge. */
const WIDE = [
  "Table 2. Accuracy with intervals",
  "",
  "Model          AUROC              AUPRC",
  "Caduceus       0.991 +/- 0.003    0.845",
  "",
].join("\n");

/** A table printed above its own caption, with the next table opening the following page and
 * printing the same row and column names. This is the ntbench layer in miniature. */
const CAPTION_BELOW = [
  "Dataset                  Promoter all      Splice donor",
  "NT-1000G (500M)          0.715             0.542",
  "",
  "   Supplementary Table 6: Downstream performance for all probing models.",
  "   Performance per task is the median of the cross-validation folds.",
  "",
  "\f Dataset                  Promoter all      Splice donor",
  " NT-1000G (500M)          0.727             0.952",
  "",
  "   Supplementary Table 7: Downstream performance for all finetuned models.",
  "",
].join("\n");

/** Two appendix tables, each captioned above itself, printing the same rows and columns. The
 * region above Table A2's caption is Table A1's body and must never answer for Table A2. */
const CAPTIONS_ABOVE = [
  "Table A1. Baseline performance for Amylase one-to-many",
  "Model                       Spearman      NDCG",
  "Ridge (one-hot)             0.430         0.903",
  "",
  "Table A2. Baseline performance for Amylase close-to-far",
  "Model                       Spearman      NDCG",
  "Ridge (one-hot)             0.612         0.955",
  "",
].join("\n");

const cellOf = (layer: LayerIndex, table: string, row: string, column: string): Resolution =>
  resolveTableCell(layer, { anchor: { kind: "table", value: table, raw: `Table ${table}` }, row, column });

describe("a cell span is one column wide", () => {
  it("refuses a field that runs across more than one column", () => {
    const outcome = cellOf(index(MERGED), "1", "H3", "GENERATOR-v2");
    expect(reasonOf(outcome)).toBe("column_merged");
  });

  it("returns the column the renderer did separate, in the same table", () => {
    const outcome = cellOf(index(MERGED), "1", "H3", "HyenaDNA");
    expect(outcome.ok && outcome.span.exact).toBe(".6926/.779/89");
  });

  it("does not narrow a merged field to the run under the named column", () => {
    // Narrowing was built and measured. It fired on 9 of the 66 and returned the neighbouring
    // column's number on 4 of them, because a cell printing "X / Y / N" has single spaces inside
    // it and its runs do not line up with the columns. Nothing in a merged field may be returned.
    const outcome = cellOf(index(MERGED), "1", "H3", "GENERATOR-v2");
    expect(outcome.ok).toBe(false);
  });

  it("returns a cell wider than its own heading whole", () => {
    const outcome = cellOf(index(WIDE), "2", "Caduceus", "AUROC");
    expect(outcome.ok && outcome.span.exact).toBe("0.991 +/- 0.003");
  });

  it("counts the runs of a field and the bands they sit under", () => {
    expect(tokensOf({ text: "0.8 0.9", from: 10 })).toEqual([
      { from: 10, to: 13 },
      { from: 14, to: 17 },
    ]);
    const bands = [
      { from: 0, to: 5 },
      { from: 20, to: 25 },
    ];
    expect(cellWidth({ bands, at: 0, field: { text: "0.8 0.9", from: 2, to: 9 } }).ok).toBe(true);
    expect(cellWidth({ bands, at: 0, field: { text: "0.8 0.9 0.7 0.6 0.95", from: 2, to: 22 } }).ok).toBe(false);
  });
});

describe("the block a table is read from", () => {
  it("stops a window at the page boundary and lets the wider one cross it", () => {
    const layer = index(["Table 9. Results", "a row", "\fTable 10. Other results", "another row"].join("\n"));
    expect(tableWindow(layer, 0)).toEqual({ from: 1, to: 2 });
    expect(widerWindow(layer, 0)).toEqual({ from: 1, to: 2 });
    const foot = index(["Table 9. Results", "", "\fModel   AUROC", "Caduceus   0.912"].join("\n"));
    expect(tableWindow(foot, 0)).toEqual({ from: 1, to: 2 });
    expect(widerWindow(foot, 0).to).toBe(4);
  });

  it("reads the region above a caption when the boundary above it is a page break", () => {
    const layer = index(CAPTION_BELOW);
    const above = blockAbove(layer, 3);
    expect(above).toEqual({ from: 0, to: 2 });
    const outcome = cellOf(layer, "6", "NT-1000G (500M)", "Promoter all");
    expect(outcome.ok && outcome.span.exact).toBe("0.715");
  });

  it("never reads the region above a caption when another caption claims it", () => {
    const layer = index(CAPTIONS_ABOVE);
    expect(blockAbove(layer, 4)).toBe(null);
    const outcome = cellOf(layer, "A2", "Ridge (one-hot)", "Spearman");
    expect(outcome.ok && outcome.span.exact).toBe("0.612");
  });

  it("reads a table that opens the page after its caption", () => {
    const layer = index(["Table 11. Accuracy", "", "\fModel        AUROC", "Caduceus     0.912", ""].join("\n"));
    const outcome = cellOf(layer, "11", "Caduceus", "AUROC");
    expect(outcome.ok && outcome.span.exact).toBe("0.912");
  });
});

/** The two locators the defects were found on, read against the layers the store holds. These
 * are the regression tests that matter: a fixture proves the rule and a real layer proves the
 * rule applies to the thing it was written for. */
describe("over the store itself", () => {
  const registry = readRegistry(root);
  const layerStarting = (prefix: string): LayerIndex | null => {
    const record = registry.find((row) => row.layer_sha256.startsWith(prefix));
    if (!record || !hasObject(record.object_sha256, root)) return null;
    return indexLayer(layerText(record, root), record.layer_sha256, record.normaliser);
  };

  it("refuses the datta2026 cell whose field held three models' columns", () => {
    const layer = layerStarting("b2458cdb");
    if (!layer) return;
    const parsed = parseLocator("Table 1, row 'H3', column 'GENERATOR-v2'");
    expect(reasonOf(resolveLocator(parsed, layer))).toBe("column_merged");
  });

  it("reads the ntbench cell from the block above its own caption", () => {
    const layer = layerStarting("3bbf2a64");
    if (!layer) return;
    const parsed = parseLocator("Supplementary Table 6, row 'NT-1000G (2.5B)', column 'Splice donor'");
    const outcome = resolveLocator(parsed, layer);
    // The stored value is 0.621 (± 0.011). The window below the caption holds the next table,
    // which prints 0.963 (± 0.001) for the same row and column.
    expect(outcome.ok && outcome.span.exact).toBe("0.621 (± 0.011)");
  });
});
