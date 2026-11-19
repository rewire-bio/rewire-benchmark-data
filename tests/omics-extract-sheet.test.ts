/** The deterministic sheet pass, over a layer written in the normaliser's own format.
 *
 * The proposition worth a test of its own is the off by one. A block opens with a header line
 * that is not a sheet row, so sheet row R is the layer line at the block's header line plus R,
 * and the second sheet of a workbook starts over at row 1. A pass that counted layer lines
 * would put a span on a number from the row above, or from the previous sheet, and the span
 * would still hold a number: it would print a plausible wrong value rather than refuse, which
 * is the worst thing a reader of this layer can do.
 */
import { describe, expect, it } from "vitest";
import { createHash } from "node:crypto";
import { blockMarker } from "../shared/archive/layers/office/sheet";
import { indexLayer } from "../shared/omics/spans/offsets";
import { sliceSpan } from "../shared/omics/layers/index";
import { buildDecider } from "../shared/omics/extract/decide";
import { sheetCandidates } from "../shared/omics/extract/sheet-pass";

const layer =
  `${blockMarker}1\tScores\tA1:C3\n` +
  "Model\tAUROC\tNotes\n" +
  "Alpha-1\t0.812\ttuned\n" +
  "Beta-2\t0.7905\t\n" +
  `${blockMarker}2\tCounts\tA1:B2\n` +
  "Model\tn\n" +
  "Alpha-1\t1200\n";

function run() {
  const index = indexLayer(layer, createHash("sha256").update(layer).digest("hex"), "ooxml-sheet-tsv@1");
  return { index, ...sheetCandidates({ decider: buildDecider([]), sourceId: "fixture-source", index, sanity: "pass" }) };
}

describe("the deterministic sheet pass", () => {
  it("numbers rows the way the spreadsheet numbers them, in every block", () => {
    const { candidates } = run();
    const references = candidates.map((candidate) => `${candidate.anchor.label} ${candidate.source_locator.split(",")[1].trim()}`);
    expect(references).toEqual(["Scores cell B2", "Scores cell B3", "Counts cell B2"]);
    // Row 2 of the second sheet is a different line of the layer from row 2 of the first, and
    // both are row 2.
    expect(candidates.map((candidate) => candidate.position.row)).toEqual([2, 3, 2]);
  });

  it("puts every candidate on a span that prints its own value", () => {
    const { index, candidates } = run();
    for (const candidate of candidates) {
      const slice = sliceSpan(index.text, candidate.span.start, candidate.span.end);
      expect(slice.exact).toBe(candidate.printed_value);
      expect(slice.byte_start).toBe(candidate.span.byte_start);
    }
    expect(candidates.map((candidate) => candidate.printed_value)).toEqual(["0.812", "0.7905", "1200"]);
  });

  it("takes the heading from row 1 and the row label from column A", () => {
    const { candidates } = run();
    expect(candidates[0].column_header).toEqual(["AUROC"]);
    expect(candidates[0].row_label).toBe("Alpha-1");
    expect(candidates[0].header_source).toBe("first_row");
    expect(candidates[0].metric.decided).toBe("auroc");
    // The word in the Notes column is not a number, so it is no candidate.
    expect(candidates.some((candidate) => candidate.printed_value === "tuned")).toBe(false);
  });
});
