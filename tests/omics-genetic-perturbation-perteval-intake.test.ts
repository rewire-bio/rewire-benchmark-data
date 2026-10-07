import fs from "node:fs";
import { gunzipSync } from "node:zlib";
import { describe, expect, it } from "vitest";
import { addUseCaseCoverage } from "../scripts/omics/use-case-coverage";
import { validateRecords, publicRecords } from "../scripts/omics/schema";
import { validateSnapshot } from "../services/omics/src/validation";
import { loadUseCases } from "../scripts/omics/use-cases";
import { buildUseCaseArtifact, mappingEvidenceHash } from "../services/omics/src/use-cases";

// This test is a self-contained, read-only "dry run" that proves the bounded
// 2026-10-07 PertEval-scFM intake (data/omics/use-case-coverage-genetic-perturbation-20261007)
// is internally consistent and correctly wired against the current catalogue and use-case
// inputs, WITHOUT modifying scripts/omics/release.ts's actual release chain or the existing
// production-gating tests/omics-use-case-coverage.test.ts. Promotion into the real release
// chain is a separate, later maintainer/Codex decision.
const INTAKE_ROOT = "data/omics/use-case-coverage-genetic-perturbation-20261007";

function assembledRecords() {
  const baseline = JSON.parse(gunzipSync(fs.readFileSync("data/omics/releases/2026-09-28-c7b5ac6d34f2/catalogue.json.gz")).toString());
  const afterFirstIntake = addUseCaseCoverage(baseline.records);
  const afterSecondIntake = addUseCaseCoverage(afterFirstIntake, "data/omics/use-case-coverage-20261005");
  const afterThirdIntake = addUseCaseCoverage(afterSecondIntake, "data/omics/use-case-coverage-20261006");
  const afterFourthIntake = addUseCaseCoverage(afterThirdIntake, "data/omics/use-case-coverage-20261007");
  const afterFifthIntake = addUseCaseCoverage(afterFourthIntake, "data/omics/use-case-coverage-egfr-20261007");
  const withThisIntake = addUseCaseCoverage(afterFifthIntake, INTAKE_ROOT);
  // The shared inputs.json also references the later AMP intake, so artifact builds need it in both fixtures.
  const AMP_ROOT = "data/omics/use-case-coverage-amp-20261007";
  return {
    baseline,
    withoutThisIntake: afterFifthIntake,
    withThisIntake,
    fullWithoutThisIntake: addUseCaseCoverage(afterFifthIntake, AMP_ROOT),
    fullWithThisIntake: addUseCaseCoverage(withThisIntake, AMP_ROOT),
  };
}

describe("genetic-perturbation-response PertEval-scFM bounded intake (dry run, not wired into release.ts)", () => {
  it("accepts the receipt, validates every new record, and leaves all prior records untouched", () => {
    const { withoutThisIntake, withThisIntake } = assembledRecords();
    expect(withThisIntake.length).toBe(withoutThisIntake.length + 12);
    validateRecords(withThisIntake);
    expect(withThisIntake.slice(0, withoutThisIntake.length)).toEqual(withoutThisIntake);
  });

  it("resolves the new mapping against the fully assembled catalogue, and leaves every other mapping byte-identical", () => {
    const { fullWithoutThisIntake, fullWithThisIntake } = assembledRecords();
    const inputs = loadUseCases()!.inputs;
    const newMappingId = "use-case-map-perteval-scfm-norman-single-auspc";
    // inputsWithout mirrors the real inputs.json but omits the new mapping, so that
    // buildUseCaseArtifact can resolve against the catalogue state that predates this
    // intake (which does not contain perteval-scfm-2025-*). This isolates "did every
    // OTHER mapping stay byte-identical" from "does the new mapping itself resolve",
    // tested separately below.
    const inputsWithout = { ...inputs, mappings: inputs.mappings.filter((m) => m.id !== newMappingId) };
    const snapshotWithout = { schema_version: "1.1", release_id: "dry-run-without", released_at: "2026-10-07T11:50:00Z", coverage: {}, records: fullWithoutThisIntake };
    const snapshotWith = { schema_version: "1.1", release_id: "dry-run-with", released_at: "2026-10-07T11:50:00Z", coverage: {}, records: fullWithThisIntake };
    validateSnapshot(snapshotWith);
    const artifactWithout = buildUseCaseArtifact(snapshotWithout, inputsWithout);
    const artifactWith = buildUseCaseArtifact(snapshotWith, inputs);
    expect(artifactWith.mappings.find((m) => m.id === newMappingId)?.lifecycle).toBe("active");
    for (const mapping of artifactWithout.mappings) {
      expect(artifactWith.mappings.find((m) => m.id === mapping.id)).toEqual(mapping);
    }
    expect(artifactWith.mappings).toHaveLength(artifactWithout.mappings.length + 1);
  });

  it("recomputes the mapping's evidence_sha256 identically to the value stored in inputs.json", () => {
    const { fullWithThisIntake } = assembledRecords();
    const inputs = loadUseCases()!.inputs;
    const useCase = inputs.use_cases.find((u) => u.id === "use-case-genetic-perturbation-response")!;
    const mapping = inputs.mappings.find((m) => m.id === "use-case-map-perteval-scfm-norman-single-auspc")!;
    const snapshot = { schema_version: "1.1", release_id: "dry-run-hash-check", released_at: "2026-10-07T11:50:00Z", coverage: {}, records: fullWithThisIntake };
    expect(mappingEvidenceHash(snapshot, useCase, mapping)).toBe(mapping.evidence_sha256);
  });

  it("transcribes the three authorized printed AUSPC values exactly, with correct units and no invented uncertainty type", () => {
    const { withThisIntake } = assembledRecords();
    const byId = new Map(withThisIntake.map((r) => [r.id, r]));
    const gears = byId.get("perteval-scfm-2025-result-gears-auspc")!;
    const mlp = byId.get("perteval-scfm-2025-result-mlp-baseline-auspc")!;
    const mean = byId.get("perteval-scfm-2025-result-mean-baseline-auspc")!;
    expect(gears.attributes.printed_value).toBe("0.815 ± 0.039");
    expect(mlp.attributes.printed_value).toBe("4.484 ± 0.299");
    expect(mean.attributes.printed_value).toBe("4.612 ± 0.317");
    for (const result of [gears, mlp, mean]) {
      expect(result.attributes.unit).toBe("10^-2 (printed column header units)");
      expect((result.attributes.uncertainty as { type: string }).type).toBe("author_reported_propagated_standard_error");
    }
  });

  it("does not create any record ID that collides with the existing catalogue", () => {
    const { withoutThisIntake, withThisIntake } = assembledRecords();
    const existingIds = new Set(withoutThisIntake.map((r) => r.id));
    const newRecords = withThisIntake.slice(withoutThisIntake.length);
    for (const record of newRecords) expect(existingIds.has(record.id)).toBe(false);
    expect(new Set(newRecords.map((r) => r.id)).size).toBe(newRecords.length);
  });

  it("excludes no new record from the public catalogue (all source_checked, none disputed/excluded)", () => {
    const { withoutThisIntake, withThisIntake } = assembledRecords();
    const newRecords = withThisIntake.slice(withoutThisIntake.length);
    const publicNew = publicRecords(withThisIntake).filter((r) => newRecords.some((n) => n.id === r.id));
    expect(publicNew.length).toBe(newRecords.length);
  });
});
