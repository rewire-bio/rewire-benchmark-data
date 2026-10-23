import { describe, expect, it } from "vitest";
import { normaliseDiscrepancies } from "../shared/omics/discrepancies";

const finding = (extra: Record<string, unknown> = {}) => ({
  id: "discrepancy-a", rule: "ordering-reversal", severity: "high", review_state: "open",
  systems: ["model-a", "model-b"], ...extra,
});

describe("normaliseDiscrepancies", () => {
  it("reads a finding without studies (schema 1 and 2) as having none", () => {
    const file = normaliseDiscrepancies({ release_id: "r", schema_version: 2, discrepancies: [finding()] });
    expect(file.discrepancies[0].studies).toEqual([]);
  });

  it("keeps a schema 3 finding's studies in order", () => {
    const studies = [
      {
        key: "doi:10.1/x", role: "outlier", source_ids: ["source-x"], higher: { "model-a": 0, "model-b": 2 }, ties: 1, gap: null,
        comparisons_total: 3,
        comparisons: [{
          protocol: "protocol-p", dataset: null, metric: "auroc", unit: "unitless", qualifier: null, split: null,
          values: { "model-a": 0.7, "model-b": 0.8 }, results: { "model-a": "result-1", "model-b": "result-2" }, higher: "model-b",
        }],
      },
      { key: "source:source-y", role: "consensus", source_ids: ["source-y"], higher: { "model-a": 5, "model-b": 0 }, ties: 0, gap: null, comparisons_total: 5, comparisons: [] },
    ];
    const file = normaliseDiscrepancies({ release_id: "r", schema_version: 3, discrepancies: [finding({ studies })] });
    expect(file.discrepancies[0].studies).toEqual(studies);
  });
});
