import { describe, expect, it } from "vitest";
import { deriveUseCaseInputs } from "../shared/omics/use-cases";
import type { CatalogueRecord } from "../shared/omics/catalogue-query";
import { batchRecords, recordsById } from "./helpers/records";

describe("ClinGen PP3/BP4 CPU calibration batch", () => {
  const prefix = "rewire-local-20261123-clingen";
  const stored = batchRecords("data/omics/rewire-clingen-pp3-bp4-20261123");
  const evaluations = stored.filter((record) => record.kind === "evaluation");
  const claims = stored.filter((record) => record.kind === "claim");

  it("carries expected source, protocol, configuration, evaluation and claim structure", () => {
    expect(stored.filter((record) => record.kind === "source")).toHaveLength(6);
    expect(stored.filter((record) => record.kind === "benchmark")).toHaveLength(1);
    expect(stored.filter((record) => record.kind === "dataset_subset")).toHaveLength(3);
    expect(stored.filter((record) => record.kind === "protocol")).toHaveLength(3);
    expect(stored.filter((record) => record.kind === "configuration")).toHaveLength(9);
    expect(evaluations).toHaveLength(27);
    expect(claims).toHaveLength(3);
    const af001ReproducedIds = new Set(
      evaluations
        .filter((record) => record.id.endsWith("-post-2023-12-af001") && record.id !== `${prefix}-evaluation-evee-post-2023-12-af001`)
        .map((record) => record.id),
    );
    expect(af001ReproducedIds.size).toBe(8);
    const reproduced = stored.filter((record) => record.status === "reproduced");
    const nonReproduced = stored.filter((record) => record.status !== "reproduced");
    expect(reproduced).toHaveLength(128);
    expect(
      reproduced.every(
        (record) =>
          (record.kind === "evaluation" && af001ReproducedIds.has(record.id)) ||
          (record.kind === "result" &&
            af001ReproducedIds.has(record.links.find((link) => link.relation === "evaluation")?.target_id ?? "")),
      ),
    ).toBe(true);
    expect(nonReproduced.every((record) => record.status === "source_checked")).toBe(true);
  });

  it("scopes the EVEE ClinVar leakage concern strictly to the three EVEE evaluations", () => {
    const readme = recordsById.get(`${prefix}-source-readme`)!;
    const concerns = readme.attributes.evidence_concerns as { message: string; applies_to: string[] }[];
    expect(concerns).toHaveLength(1);
    expect(concerns[0].applies_to.sort()).toEqual([
      `${prefix}-evaluation-evee-post-2023-12`,
      `${prefix}-evaluation-evee-post-2023-12-af001`,
      `${prefix}-evaluation-evee-post-2025-03`,
    ]);
    expect(concerns[0].message).toContain("ClinVar supervision through 2026-03-20");
  });

  it("links all three calibration protocols as active direct judgements on missense PP3/BP4", () => {
    const allRecords = [...recordsById.values()] as unknown as CatalogueRecord[];
    const mappings = deriveUseCaseInputs({ records: allRecords }).mappings;
    for (const suffix of ["post-2023-12", "post-2023-12-af001", "post-2025-03"]) {
      const mapping = mappings.find((m) => m.id === `use-case-mapping-${prefix}-${suffix}`);
      expect(mapping, suffix).toBeDefined();
      expect(mapping!.lifecycle).toBe("active");
      expect(mapping!.relevance).toBe("direct");
      expect(mapping!.evaluation_ids).toHaveLength(8);
    }
  });
});
