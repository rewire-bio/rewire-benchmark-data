import fs from "node:fs";
import { gunzipSync } from "node:zlib";
import { describe, expect, it } from "vitest";
import { addUseCaseCoverage } from "../scripts/omics/use-case-coverage";
import { validateRecords, publicRecords, type RecordEntry } from "../scripts/omics/schema";
import { validateSnapshot } from "../services/omics/src/validation";
import { loadUseCases } from "../scripts/omics/use-cases";
import { buildUseCaseArtifact } from "../services/omics/src/use-cases";

const NEW_ROOT = "data/omics/use-case-coverage-20261005";
const EXISTING_MAPPING_IDS = [
  "use-case-mapping-20260930-343-2b9e45a46d4b",
  "use-case-mapping-20260930-343-64fb29b5bff8",
  "use-case-mapping-20260930-343-77a677a9f119",
  "use-case-mapping-20260930-343-cf70c367d48e",
  "use-case-mapping-20260930-343-dd4044ac3f2f",
];
// Five further mappings added on 2026-10-05 against the new records above.
const NEW_MAPPING_PROTOCOLS: Record<string, string> = {
  "use-case-mapping-20261005-343-6620c2b7cd1a": "uc-clinical-20261005-benet-pages-t2-protocol",
  "use-case-mapping-20261005-343-b3489257a74c": "uc-clinical-20261005-benet-pages-t3-protocol",
  "use-case-mapping-20261005-343-1d76c37513fa": "uc-clinical-20261005-so-2024-protocol",
  "use-case-mapping-20261005-343-9a16ffea921e": "uc-clinical-20261005-hector-erepo-protocol",
  "use-case-mapping-20261005-343-4d6887d8d2e1": "uc-clinical-20261005-hu-2026-protocol",
};
const NEW_MAPPING_IDS = Object.keys(NEW_MAPPING_PROTOCOLS);

describe("additive BRCA1/BRCA2 research-evidence intake, 2026-10-05", () => {
  const baseline = JSON.parse(
    gunzipSync(fs.readFileSync("data/omics/releases/2026-09-28-c7b5ac6d34f2/catalogue.json.gz")).toString(),
  );
  // The five BRCA1/BRCA2 mappings did not exist yet in the 2026-09-28 release; compare against
  // the 2026-09-30 release, which is where they were first published.
  const previousCases = JSON.parse(
    gunzipSync(fs.readFileSync("data/omics/releases/2026-09-30-e37e3ab1284d/use-cases.json.gz")).toString(),
  );
  // Mirror the exact chain in scripts/omics/release.ts: default 20260930 root, then the
  // 20261005 root, then the 20261006 root, so buildUseCaseArtifact sees every protocol the
  // current reviewed inputs reference (including the later 2026-10-06 cell-type-annotation-
  // transfer addition, which is not part of this BRCA-scoped pass but shares one inputs.json).
  const afterFirstIntake = addUseCaseCoverage(baseline.records);
  const afterSecondIntake = addUseCaseCoverage(afterFirstIntake, NEW_ROOT);
  const records = addUseCaseCoverage(afterSecondIntake, "data/omics/use-case-coverage-20261006");
  const newRecords = records.slice(afterFirstIntake.length, afterSecondIntake.length);

  it("validates every new record and preserves every prior record byte-identically", () => {
    validateRecords(records);
    expect(records.slice(0, baseline.records.length)).toEqual(baseline.records);
    expect(records.slice(0, afterFirstIntake.length)).toEqual(afterFirstIntake);
    const snapshot = {
      ...baseline,
      release_id: "2026-10-05-000000000000",
      released_at: "2026-10-05T16:30:00Z",
      records,
    };
    validateSnapshot(snapshot);
  });

  it("adds exactly 42 new clinical-lane records, none claiming a new execution", () => {
    expect(newRecords).toHaveLength(42);
    for (const record of newRecords) {
      expect(record.status).not.toBe("reproduced");
      expect(record.attributes.origin).not.toBe("rewire_run");
    }
  });

  it("leaves the five existing active BRCA1/BRCA2 mappings byte-identical and adds five new active mappings", () => {
    const inputs = loadUseCases()!.inputs;
    const snapshot = { ...baseline, release_id: "2026-10-05-000000000000", released_at: "2026-10-05T16:30:00Z", records };
    const artifact = buildUseCaseArtifact(snapshot, inputs);
    const brcaMappings = artifact.mappings.filter(
      (mapping) => mapping.use_case_id === "use-case-brca1-brca2-germline-interpretation",
    );
    expect(brcaMappings.map((mapping) => mapping.id).sort()).toEqual(
      [...EXISTING_MAPPING_IDS, ...NEW_MAPPING_IDS].sort(),
    );
    expect(brcaMappings.every((mapping) => mapping.lifecycle === "active")).toBe(true);
    expect(brcaMappings.every((mapping) => !("stale_from" in mapping))).toBe(true);

    // The five prior mappings must stay byte-identical; this is the only
    // existing-record contract this additive pass is allowed to touch.
    const oldMappings = previousCases.mappings.filter(
      (mapping: { use_case_id: string }) => mapping.use_case_id === "use-case-brca1-brca2-germline-interpretation",
    );
    expect(oldMappings).toHaveLength(5);
    for (const oldMapping of oldMappings)
      expect(brcaMappings.find((mapping) => mapping.id === oldMapping.id)).toEqual(oldMapping);

    // Each new mapping targets a distinct 2026-10-05 protocol, stays a proxy
    // (not direct/outside_scope) and carries its own reviewed evidence hash.
    const newMappings = brcaMappings.filter((mapping) => NEW_MAPPING_IDS.includes(mapping.id));
    expect(newMappings).toHaveLength(5);
    for (const mapping of newMappings) {
      expect(mapping.protocol_id).toBe(NEW_MAPPING_PROTOCOLS[mapping.id]);
      expect(mapping.relevance).toBe("proxy");
      expect(mapping.evidence_sha256).toMatch(/^[a-f0-9]{64}$/);
      expect(mapping.evidence_sha256).not.toBe("0".repeat(64));
    }
    expect(new Set(newMappings.map((mapping) => mapping.protocol_id)).size).toBe(5);
    expect(new Set(newMappings.map((mapping) => mapping.endpoint)).size).toBe(5);
    expect(new Set(newMappings.map((mapping) => mapping.evidence_sha256)).size).toBe(5);

    // Endpoints must state the exact population/limitation distinguishing each
    // mapping from an accuracy or full-review claim.
    const byProtocol = new Map(newMappings.map((mapping) => [mapping.protocol_id, mapping]));
    const benetT2 = byProtocol.get("uc-clinical-20261005-benet-pages-t2-protocol")!;
    expect(benetT2.endpoint).toMatch(/121-variant/);
    expect(JSON.stringify(benetT2.limitations)).toMatch(/not accuracy against independent ground truth or a reviewer-time comparison/);
    const benetT3 = byProtocol.get("uc-clinical-20261005-benet-pages-t3-protocol")!;
    expect(benetT3.endpoint).toMatch(/121-variant/);
    expect(JSON.stringify(benetT3.limitations)).toMatch(/not accuracy against independent ground truth or a reviewer-time comparison/);
    expect(JSON.stringify([...benetT2.limitations, ...benetT3.limitations])).not.toMatch(/85%, n = 40|83%, n = 67/);

    const so = byProtocol.get("uc-clinical-20261005-so-2024-protocol")!;
    expect(so.endpoint).toMatch(/Tool-vs-tool concordance/);
    expect(JSON.stringify(so.limitations)).toMatch(/not accuracy against independent ground truth/);

    const hector = byProtocol.get("uc-clinical-20261005-hector-erepo-protocol")!;
    expect(hector.endpoint).toMatch(/Evidence Repository/);
    expect(JSON.stringify(hector.limitations)).toMatch(/not independent accuracy/);
    expect(JSON.stringify(hector.limitations)).toMatch(/[Nn]ot peer reviewed/);

    const hu = byProtocol.get("uc-clinical-20261005-hu-2026-protocol")!;
    expect(hu.endpoint).toMatch(/exon 15-26/);
    expect(JSON.stringify(hu.limitations)).toMatch(/not independent clinical accuracy and not a complete professional classification review/);

    for (const mapping of newMappings) {
      expect(mapping.review?.method).toBe("automated_source_review");
      expect(JSON.stringify(mapping)).not.toMatch(/rewire_run|Rewire execution/i);
    }
  });

  it("gives Karalidou 2022 (MARGINAL) no numeric result and keeps its value-not-extracted gap explicit", () => {
    const marginal = newRecords.find((record) => record.id === "uc-clinical-20261005-source-marginal");
    expect(marginal).toBeDefined();
    expect(marginal!.kind).toBe("source");
    expect(newRecords.some((record) => record.kind === "result" && record.source_ids.includes(marginal!.id))).toBe(
      false,
    );
    expect(Array.isArray((marginal!.attributes as { evidence_concerns?: unknown[] }).evidence_concerns)).toBe(true);
  });

  it("adds no source record for Kwong et al. 2026", () => {
    expect(newRecords.some((record) => /kwong/i.test(JSON.stringify(record)))).toBe(false);
  });

  it("distinguishes reclassification rate, tool agreement, preprint classification agreement and functional-proxy yield", () => {
    const byId = new Map<string, RecordEntry>(newRecords.map((record) => [record.id, record]));

    const benetT2 = byId.get("uc-clinical-20261005-benet-pages-t2-reclassified-lb-fraction")!;
    expect(benetT2.attributes.printed_value).toBe("20%");
    const benetT3 = byId.get("uc-clinical-20261005-benet-pages-t3-reclassified-b-lb-fraction")!;
    expect(benetT3.attributes.printed_value).toBe("83.5%");
    // The gene-split Benet-Pages figures must never appear in this intake.
    expect(newRecords.some((record) => JSON.stringify(record).includes("85%, n = 40"))).toBe(false);
    expect(newRecords.some((record) => JSON.stringify(record).includes("83%, n = 67"))).toBe(false);

    const so = byId.get("uc-clinical-20261005-so-2024-concordance-rate")!;
    expect(so.attributes.printed_value).toBe("58.9%");
    expect(so.attributes.metric).toBe("concordance_rate");
    expect((so.attributes.uncertainty as { low: string; high: string }).low).toBe("52.0");
    expect((so.attributes.uncertainty as { low: string; high: string }).high).toBe("66.4");

    const hectorClassification = byId.get("uc-clinical-20261005-hector-erepo-classification-agreement")!;
    expect(hectorClassification.attributes.printed_value).toBe("75.5% (108/143)");
    const hectorCriteria = byId.get("uc-clinical-20261005-hector-erepo-criteria-agreement")!;
    expect(hectorCriteria.attributes.printed_value).toBe("78.9% (326/413)");
    const hectorSource = byId.get("uc-clinical-20261005-source-hector-preprint")!;
    expect(hectorSource.attributes.publication_status).toBe("preprint_not_peer_reviewed");
    const hectorProtocol = byId.get("uc-clinical-20261005-hector-erepo-protocol")!;
    expect(JSON.stringify(hectorProtocol.attributes.limitations)).toMatch(/not independent accuracy/);

    const hu = byId.get("uc-clinical-20261005-hu-2026-classified-yield")!;
    expect(hu.attributes.printed_value).toBe("92.8% (5926/6383)");
    expect(hu.attributes.metric).toBe("classified_as_p_lp_or_b_lb_fraction");
    const huProtocol = byId.get("uc-clinical-20261005-hu-2026-protocol")!;
    expect(JSON.stringify(huProtocol.attributes.limitations)).toMatch(/not independent clinical accuracy/);

    // Endpoints must stay distinct metrics, not interchangeable accuracy claims.
    const metrics = new Set(
      [benetT2, benetT3, so, hectorClassification, hectorCriteria, hu].map((record) => record.attributes.metric),
    );
    expect(metrics.size).toBe(6);
  });

  it("keeps every new result public and source-checked", () => {
    const resultIds = newRecords.filter((record) => record.kind === "result").map((record) => record.id);
    expect(resultIds).toHaveLength(9);
    const published = new Set(publicRecords(records).map((record) => record.id));
    for (const id of resultIds) {
      expect(published.has(id)).toBe(true);
      expect(byIdStatus(newRecords, id)).toBe("source_checked");
    }
  });
});

function byIdStatus(records: RecordEntry[], id: string): string {
  return records.find((record) => record.id === id)!.status;
}
