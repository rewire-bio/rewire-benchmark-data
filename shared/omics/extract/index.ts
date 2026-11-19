/** One archived source in, a file of candidate results out, with no model anywhere.
 *
 * This is the fifth command of the collection method. `archive -- fetch` holds the bytes,
 * `layers -- build` derives the text, this reads values out of that text, and `records -- add`
 * writes what a reviewer promotes. The point of running it with no model at all is that the
 * baseline is then measurable on its own: whatever a model stage adds later is measured against
 * these numbers rather than mixed into them.
 *
 * Which layers get read is decided by what the layer carries, not by what the source is.
 *
 *   a markup layer with a grid beside it   every cell of every table, by the markup's geometry
 *   an Office sheet layer                  every cell of every sheet, by the sheet's geometry
 *   anything else                          skipped, with the reason recorded
 *
 * The third line is most of the archive and is the measurement, not a gap to be filled by
 * trying harder. A `pdf-text-layer@1` layer is aligned text, and the only route from aligned
 * text to a column is to infer one from runs of spaces, which is wrong on every table with a
 * spanning header. `shared/archive/layers/grid/index.ts` records that decision and the
 * measurement behind it. So a PDF-only source yields no candidates here, and the receipt says
 * `no_grid_for_normaliser` rather than nothing.
 *
 * A layer at `fail` is never read: ADR 0002 decision 1 says no record, claim or candidate may
 * cite one.
 */
import { gridForLayer, gridOfRecord, gridsForSource, layerText, layersForSource } from "../layers/index";
import type { LayerRecord } from "../layers/types";
import { indexLayer } from "../spans/offsets";
import type { Candidate, Tally } from "./candidate";
import type { Decider } from "./decide";
import { gridCandidates } from "./grid-pass";
import { sheetCandidates } from "./sheet-pass";

export * from "./candidate";
export { assessmentKinds, buildDecider, decideCell, orientationOf, systemKinds, type Decider } from "./decide";
export { buildCandidate, candidateId } from "./build";
export { gridCandidates } from "./grid-pass";
export { sheetCandidates } from "./sheet-pass";
export { spanOfPoints, u16AtPoint } from "./points";
export { conceptLabels, recordNames, lookup, printedUnit } from "./labels";
export { readCellValue, type CellValue } from "./value";

export interface SourceExtraction {
  candidates: Candidate[];
  tally: Tally;
}

/** Normalisers that carry a geometry this pass can read without inferring one. */
const SHEET = "ooxml-sheet-tsv@1";

export function extractSource(sourceId: string, decider: Decider, root = "."): SourceExtraction {
  const candidates: Candidate[] = [];
  const layers: Tally["layers"] = [];
  const skipped: Tally["skipped"] = [];
  const grids = gridsForSource(sourceId, root);

  for (const record of layersForSource(sourceId, root)) {
    if (record.sanity === "fail") {
      skipped.push({ layer_sha256: record.layer_sha256, normaliser: record.normaliser, reason: "layer_sanity_fail" });
      continue;
    }
    const grid = gridForLayer(record.layer_sha256, root);
    if (grid) {
      const index = indexLayer(layerText(record, root), record.layer_sha256, record.normaliser);
      const read = gridCandidates({
        decider,
        sourceId,
        index,
        grid: gridOfRecord(grid, root),
        gridLayerSha256: grid.layer_sha256,
        sanity: record.sanity,
      });
      candidates.push(...read.candidates);
      layers.push(read.tally);
      continue;
    }
    if (record.normaliser === SHEET) {
      const index = indexLayer(layerText(record, root), record.layer_sha256, record.normaliser);
      const read = sheetCandidates({ decider, sourceId, index, sanity: record.sanity });
      candidates.push(...read.candidates);
      layers.push(read.tally);
      continue;
    }
    skipped.push({
      layer_sha256: record.layer_sha256,
      normaliser: record.normaliser,
      // A markup layer that holds no table has no grid either, which is the same word from the
      // registry's point of view and a different fact. Both are reported; the grid count for
      // the source separates them.
      reason: grids.length > 0 ? "no_grid_for_layer" : "no_grid_for_normaliser",
    });
  }

  const byField: Record<string, number> = {};
  const byReason: Record<string, number> = {};
  let complete = 0;
  for (const candidate of candidates) {
    if (candidate.complete) complete += 1;
    for (const question of candidate.undecided) {
      byField[question.field] = (byField[question.field] ?? 0) + 1;
      byReason[question.reason] = (byReason[question.reason] ?? 0) + 1;
    }
  }

  return {
    candidates,
    tally: {
      source_id: sourceId,
      layers,
      skipped,
      candidates: candidates.length,
      complete,
      needs_completion: candidates.length - complete,
      undecided_by_field: byField,
      undecided_by_reason: byReason,
    },
  };
}

/** The layer rows a source holds, for a caller that wants to say what was available. */
export const layersOfSource = (sourceId: string, root = "."): LayerRecord[] => layersForSource(sourceId, root);
