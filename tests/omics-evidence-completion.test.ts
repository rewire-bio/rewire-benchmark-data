import { describe, it, expect } from "vitest";
import { profileSchema, validateProfileSources } from "../lib/omics-profile";
import { buildRelease } from "../scripts/omics/release";
import { compareResults, createCatalogueQuery } from "../shared/omics/catalogue-query";
import { movedAttributes, records, recordsById } from "./helpers/records";

const sources = new Map(records.filter((record) => record.kind === "source").map((record) => [record.id, record]));

describe("evidence completion", () => {
  it("pins every profile citation to a source artifact hash", () => {
    for (const record of records.filter((r) => r.attributes.profile)) {
      const profile = profileSchema.parse(record.attributes.profile);
      const cited = [
        ...(profile.summary_source_ids ?? []),
        ...[...profile.facts, ...profile.sections, ...profile.strengths, ...profile.limitations]
          .flatMap((claim) => claim.source_ids),
      ];
      for (const id of cited)
        expect(sources.get(id)?.attributes.artifact_sha256, `${record.id} cites ${id}`).toMatch(/^[a-f0-9]{64}$/);
    }
  });
  it("requires complete summary citations and validates their targets", () => {
    const profile = profileSchema.parse(recordsById.get("discovery-model-alphafold-3")!.attributes.profile);
    expect(() =>
      profileSchema.parse({ ...profile, summary_source_locator: undefined }),
    ).toThrow("Summary evidence");
    expect(() =>
      validateProfileSources({ ...profile, summary_source_ids: ["missing"] }, sources),
    ).toThrow("missing source");
    expect(profile.facts.find((fact) => fact.label === "Parameters")?.status).toBe("unreported");
  });
  it("keeps original discovery gaps in provenance once reviewed profile facts exist", () => {
    const current = recordsById.get("discovery-model-dnabert-2")!;
    expect(current.attributes.historical_missing_metadata).toBeUndefined();
    expect(movedAttributes(current.id).historical_missing_metadata).toBeTruthy();
  });
  it("keeps hosted service restrictions distinct from the local model and logs identity corrections", () => {
    expect(recordsById.get("catalog-model-alphafold-3-server")!.attributes.entity_level).toBe("service");
    expect(recordsById.get("discovery-model-alphafold-3")!.attributes.entity_level).toBe("family");
    expect(
      records.find((record) =>
        record.id.startsWith("metadata-correction-") &&
        record.links.some((link) => link.relation === "subject" && link.target_id === "catalog-model-alphafold-3-server"),
      )!.attributes.previous_value,
    ).toBe("family");
  });
});

describe("unresolved primary-source concerns", () => {
  it("retains the printed score but prevents comparison and surfaces the precise concern", () => {
    const query = createCatalogueQuery(
      buildRelease(records, "2026-09-16T21:00:00Z", { entity_schema_version: "1.1" }).snapshot,
    );
    const row = query.results({ id: "lit-b4-017" }).items[0];
    expect(row.result).toEqual(recordsById.get("lit-b4-017"));
    const comparison = query.compare({ ids: ["lit-b4-017", "b2-barcodebert-2026"] });
    expect(comparison.compatible).toBe(false);
    expect(comparison.reasons).toContain(
      "A source has unresolved evidence concerns; this result cannot support a comparison.",
    );
  });
  it("prevents comparison when a scoped concern names the result's evaluation, from any source", () => {
    const query = createCatalogueQuery(
      buildRelease(records, "2026-09-16T21:00:00Z", { entity_schema_version: "1.1" }).snapshot,
    );
    const rowFor = (id: string) => query.results({ id }).items[0];
    const ids = ["b2-barcodebert-2026", "lit-b4-017"];
    const reason = "An evidence concern applies to this result; it cannot support a comparison.";
    expect(compareResults("test", ids, rowFor, new Set()).reasons).not.toContain(reason);
    const evaluationId = rowFor(ids[0]).evaluation!.id;
    expect(compareResults("test", ids, rowFor, new Set(), new Set([evaluationId])).reasons).toContain(reason);
    // The protocol, task or benchmark the evaluation was tested on, and what that is part of.
    const assessment = rowFor(ids[0]).benchmarks[0];
    for (const id of [assessment.id, ...assessment.links.filter((l) => l.relation === "part_of").map((l) => l.target_id)])
      expect(compareResults("test", ids, rowFor, new Set(), new Set([id])).reasons).toContain(reason);
  });
});
