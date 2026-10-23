import { describe, expect, it } from "vitest";
import { normaliseDiscrepancies, summarise } from "../shared/omics/discrepancies";

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

  it("reads a resolved finding (schema 4) and lists it after the live ones", () => {
    const resolved = {
      id: "discrepancy-r", resolved: true, rule: null, label: "model-a and model-b: resolved", severity: "low",
      scope: null, identity_basis: null, review_state: "confirmed-error", review_claim: "claim-2", settled: true,
      systems: ["model-a", "model-b"], previous_ids: ["discrepancy-old"], studies: [], numbers: {},
      actions: [{ revision: 1, claim_id: "claim-2", action: "corrected-records", state: "confirmed-error", date: "2026-11-12" }],
    };
    const file = normaliseDiscrepancies({ release_id: "r", schema_version: 4, discrepancies: [resolved, finding({ severity: "low" })] });
    expect(file.discrepancies.map((d) => [d.id, d.resolved])).toEqual([["discrepancy-a", false], ["discrepancy-r", true]]);
    const [, r] = file.discrepancies;
    expect([r.rule, r.scope, r.state, r.settled]).toEqual(["", "", "confirmed-error", true]);
    expect(summarise(r)).toMatchObject({ resolved: true, actions: 1, last_action_date: "2026-11-12" });
  });
});
