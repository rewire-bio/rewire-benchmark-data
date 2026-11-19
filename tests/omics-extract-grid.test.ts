/** The deterministic extraction pass, over a document built here rather than fetched.
 *
 * Four propositions, each of which would be a defect if it failed.
 *
 * 1. Every span a candidate carries slices back to the characters the candidate calls its
 *    printed value. This is the whole design: a candidate with a span that does not print its
 *    own value reads as a check that passed and is not one.
 * 2. A cell the markup writes as empty, and a cell that prints a dash, produce no candidate.
 *    Papers write "-" for a method that does not apply, and emitting that as a value would put
 *    a number in the store the document does not hold.
 * 3. Two runs over the same bytes give byte-identical candidate lines. A diff then means
 *    something changed, which is what makes rerunning the command worth anything.
 * 4. The locator is authored as structure and rendered to the printed string, and the string
 *    parses back to the same structure. ADR 0002 decision 2 requires that of a new batch.
 */
import { describe, expect, it } from "vitest";
import { layerOf, readGrid } from "../shared/archive/layers/index";
import { canonicalJson } from "../shared/archive/layers/grid/index";
import { parseLocator, renderLocator } from "../shared/omics/locator";
import { sliceSpan } from "../shared/omics/layers/index";
import { indexLayer } from "../shared/omics/spans/offsets";
import { gridCandidates } from "../shared/omics/extract/grid-pass";
import { buildDecider } from "../shared/omics/extract/decide";

const page = `<!doctype html><html><body>
<p>Results.</p>
<table>
<caption>Table 2. Variant effect prediction on ClinVar.</caption>
<thead><tr><th>Model</th><th>AUROC</th><th>Spearman</th><th>Notes</th></tr></thead>
<tbody>
<tr><td>Alpha-1</td><td>0.812</td><td>0.44</td><td>tuned</td></tr>
<tr><td>Beta-2</td><td>0.790 ± 0.013</td><td>-</td><td></td></tr>
</tbody>
</table>
</body></html>`;

function run() {
  const tree = layerOf(Buffer.from(page, "utf8"), { mediaType: "text/html" });
  const text = tree.layer;
  const grid = tree.grid;
  if (!text || !grid) throw new Error("the fixture produced no text layer or no grid");
  const index = indexLayer(text.bytes.toString("utf8"), text.output_sha256, text.normaliser);
  // An empty store: nothing here should depend on what the catalogue happens to hold.
  const decider = buildDecider([]);
  return {
    index,
    ...gridCandidates({
      decider,
      sourceId: "fixture-source",
      index,
      grid: readGrid(grid.bytes.toString("utf8")),
      gridLayerSha256: grid.output_sha256,
      sanity: "pass",
    }),
  };
}

describe("the deterministic table pass", () => {
  it("puts every candidate on a span that prints its own value", () => {
    const { index, candidates } = run();
    expect(candidates.length).toBeGreaterThan(0);
    for (const candidate of candidates) {
      const slice = sliceSpan(index.text, candidate.span.start, candidate.span.end);
      expect(slice.exact).toBe(candidate.printed_value);
      expect(slice.exact).toBe(candidate.span.exact);
      expect(slice.byte_start).toBe(candidate.span.byte_start);
      expect(slice.byte_end).toBe(candidate.span.byte_end);
      expect(candidate.span.layer_sha256).toBe(index.layer_sha256);
    }
  });

  it("reads the row label and the column heading the markup wrote", () => {
    const { candidates } = run();
    const first = candidates[0];
    expect(first.row_label).toBe("Alpha-1");
    expect(first.column_header).toEqual(["AUROC"]);
    expect(first.header_source).toBe("markup");
    expect(first.metric.decided).toBe("auroc");
    expect(first.direction.decided).toBe("higher");
    expect(first.numeric_value).toBe("0.812");
    // Nothing in the fixture names a unit, and nothing in an empty store names the model or
    // the benchmark, so each of those is empty and asks its question.
    expect(first.unit.decided).toBeNull();
    expect(first.model.decided).toBeNull();
    expect(first.model.printed).toBe("Alpha-1");
    expect(first.undecided.map((question) => question.field).sort()).toEqual(["assessment", "model", "unit"]);
    expect(first.complete).toBe(false);
  });

  it("emits no candidate for a dash, a blank or a word", () => {
    const { candidates } = run();
    const printed = candidates.map((candidate) => candidate.printed_value);
    expect(printed).not.toContain("-");
    expect(printed).not.toContain("tuned");
    expect(printed).toContain("0.790 ± 0.013");
    const spread = candidates.find((candidate) => candidate.printed_value === "0.790 ± 0.013");
    expect(spread?.numeric_value).toBe("0.790");
    expect(spread?.uncertainty_printed).toBe("0.013");
  });

  it("gives byte-identical lines on a rerun", () => {
    const first = run().candidates.map(canonicalJson).join("\n");
    const second = run().candidates.map(canonicalJson).join("\n");
    expect(second).toBe(first);
  });

  it("renders a locator that parses back to the same structure", () => {
    const { candidates } = run();
    for (const candidate of candidates) {
      expect(renderLocator(parseLocator(candidate.source_locator))).toBe(candidate.source_locator);
      const parsed = parseLocator(candidate.source_locator);
      // The markup marks no label on this table and the caption's first words carry one, which
      // is where the identifier comes from.
      expect(parsed.anchors[0].kind).toBe("table");
      expect(parsed.anchors[0].value).toBe("2");
      expect(parsed.residue).toEqual([]);
    }
  });
});
