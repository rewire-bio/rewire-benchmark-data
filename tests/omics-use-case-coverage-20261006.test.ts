import fs from "node:fs";
import { gunzipSync } from "node:zlib";
import { createHash } from "node:crypto";
import { describe, expect, it } from "vitest";
import { addUseCaseCoverage } from "../scripts/omics/use-case-coverage";
import { validateRecords, publicRecords, type RecordEntry } from "../scripts/omics/schema";
import { validateSnapshot } from "../services/omics/src/validation";
import { loadUseCases } from "../scripts/omics/use-cases";
import { buildUseCaseArtifact } from "../services/omics/src/use-cases";

const NEW_ROOT = "data/omics/use-case-coverage-20261006";
const EXISTING_MAPPING_ID = "use-case-mapping-20260930-349-1af09c2e0e0f";
// Two scTab mappings added on 2026-10-06 (first pass), one per new protocol.
const SCTAB_MAPPING_PROTOCOLS: Record<string, string> = {
  "use-case-mapping-20261006-349-2cfbe5c7674a": "ucc-research-protocol-sctab-uncertainty-absent",
  "use-case-mapping-20261006-349-6a9d63555f43": "ucc-research-protocol-sctab-uncertainty-error",
};
const SCTAB_MAPPING_IDS = Object.keys(SCTAB_MAPPING_PROTOCOLS);
// Third mapping added the same day (continuation): Abdelaal et al. 2019 Baron Human intra-dataset.
const ABDELAAL_MAPPING_ID = "use-case-mapping-20261006-349-967caca02e7d";
const ABDELAAL_PROTOCOL_ID = "ucc-research-protocol-abdelaal-baron-human-intra";
const NEW_MAPPING_IDS = [...SCTAB_MAPPING_IDS, ABDELAAL_MAPPING_ID];

describe("additive cell-type-annotation-transfer research-evidence intake, 2026-10-06", () => {
  const baseline = JSON.parse(
    gunzipSync(fs.readFileSync("data/omics/releases/2026-09-28-c7b5ac6d34f2/catalogue.json.gz")).toString(),
  );
  // Mirror the exact chain in scripts/omics/release.ts: default 20260930 root,
  // then 20261005, then 20261006, then the new 20261007 root, so buildUseCaseArtifact
  // sees every protocol the current reviewed inputs reference (including the later
  // 2026-10-07 cell-type-annotation-transfer addition, which shares one inputs.json).
  const afterFirstIntake = addUseCaseCoverage(baseline.records);
  const afterSecondIntake = addUseCaseCoverage(afterFirstIntake, "data/omics/use-case-coverage-20261005");
  const afterThirdIntake = addUseCaseCoverage(afterSecondIntake, NEW_ROOT);
  const afterFourthIntake = addUseCaseCoverage(afterThirdIntake, "data/omics/use-case-coverage-20261007");
  const afterEgfr = addUseCaseCoverage(afterFourthIntake, "data/omics/use-case-coverage-egfr-20261007");
  const records = addUseCaseCoverage(afterEgfr, "data/omics/use-case-coverage-amp-20261007");
  const newRecords = records.slice(afterSecondIntake.length, afterThirdIntake.length);

  it("validates every new record and preserves every prior record byte-identically", () => {
    validateRecords(records);
    expect(records.slice(0, baseline.records.length)).toEqual(baseline.records);
    expect(records.slice(0, afterSecondIntake.length)).toEqual(afterSecondIntake);
    const snapshot = {
      ...baseline,
      release_id: "2026-10-06-000000000001",
      released_at: "2026-10-06T23:02:20Z",
      records,
    };
    validateSnapshot(snapshot);
  });

  it("adds exactly 27 new research-lane records (scTab pass + Abdelaal continuation), none claiming a new execution", () => {
    expect(newRecords).toHaveLength(27);
    for (const record of newRecords) {
      expect(record.status).not.toBe("reproduced");
      expect(record.attributes.origin).not.toBe("rewire_run");
    }
    expect(newRecords.filter((r) => r.kind === "source")).toHaveLength(1);
    expect(newRecords.filter((r) => r.kind === "dataset")).toHaveLength(1);
    expect(newRecords.filter((r) => r.kind === "protocol")).toHaveLength(3);
    expect(newRecords.filter((r) => r.kind === "method")).toHaveLength(3);
    expect(newRecords.filter((r) => r.kind === "configuration")).toHaveLength(4);
    expect(newRecords.filter((r) => r.kind === "evaluation")).toHaveLength(6);
    expect(newRecords.filter((r) => r.kind === "result")).toHaveLength(9);
  });

  it("adds exactly one new source record (Abdelaal et al. 2019); the scTab protocols reuse the existing scTab source by reference", () => {
    const sources = newRecords.filter((r) => r.kind === "source");
    expect(sources).toHaveLength(1);
    expect(sources[0].id).toBe("ucc-research-source-abdelaal-2019-paper");
    expect(sources[0].attributes.sha256).toBe("6df0937c5a2d8ba06465ba356c2321fb9f52d9ecf23456876acd82f828b41d4c");

    const sctabRecords = newRecords.filter((r) => r.id.includes("sctab-uncertainty"));
    for (const record of sctabRecords) {
      expect(record.source_ids).toEqual(["ucc-research-source-sctab-paper"]);
    }
    const abdelaalRecords = newRecords.filter((r) => r.id.includes("abdelaal") && r.kind !== "source");
    for (const record of abdelaalRecords) {
      expect(record.source_ids).toEqual(["ucc-research-source-abdelaal-2019-paper"]);
    }
  });

  it("does not add any record for scArches: the re-checked ~84% figure stays unresolved, not promoted", () => {
    const serialized = JSON.stringify(newRecords);
    expect(serialized).not.toMatch(/scArches/i);
    expect(serialized).not.toMatch(/PMC8763644/);
    expect(serialized).not.toMatch(/0\.84|84%|~84/);
  });

  it("leaves the one existing active mapping byte-identical and adds three new active mappings", () => {
    const inputs = loadUseCases()!.inputs;
    const snapshot = { ...baseline, release_id: "2026-10-06-000000000001", released_at: "2026-10-06T23:02:20Z", records };
    const artifact = buildUseCaseArtifact(snapshot, inputs);
    const mappings = artifact.mappings.filter(
      (mapping) => mapping.use_case_id === "use-case-cell-type-annotation-transfer",
    );
    // inputs.json is shared across dated passes; a later pass (2026-10-07) adds a fifth
    // mapping for this use case, which is out of scope for this 2026-10-06 test file and
    // is covered by tests/omics-use-case-coverage-20261007.test.ts instead. Assert this
    // pass's own four mapping IDs are present, not that they are the only ones.
    const actualIds = new Set(mappings.map((mapping) => mapping.id));
    for (const id of [EXISTING_MAPPING_ID, ...NEW_MAPPING_IDS]) expect(actualIds.has(id)).toBe(true);
    expect(mappings.every((mapping) => mapping.lifecycle === "active")).toBe(true);
    expect(mappings.every((mapping) => !("stale_from" in mapping))).toBe(true);

    // The one prior mapping must stay byte-identical; this is the only
    // existing-record contract this additive pass is allowed to touch.
    const existing = mappings.find((mapping) => mapping.id === EXISTING_MAPPING_ID)!;
    expect(existing.protocol_id).toBe("ucc-research-protocol-sctab-seed");
    expect(existing.evidence_sha256).toBe("4872ccaea598db25c6371bbcfe66915403991bf2f182b54c0a3e8ed2b337cfbc");

    // Each new mapping targets a distinct new protocol, stays a proxy, and
    // carries its own reviewed evidence hash distinct from the others.
    const newMappings = mappings.filter((mapping) => NEW_MAPPING_IDS.includes(mapping.id));
    expect(newMappings).toHaveLength(3);
    for (const mapping of newMappings) {
      expect(mapping.relevance).toBe("proxy");
      expect(mapping.evidence_sha256).toMatch(/^[a-f0-9]{64}$/);
      expect(mapping.evidence_sha256).not.toBe("0".repeat(64));
    }
    for (const [id, protocolId] of Object.entries(SCTAB_MAPPING_PROTOCOLS)) {
      expect(newMappings.find((m) => m.id === id)!.protocol_id).toBe(protocolId);
    }
    expect(newMappings.find((m) => m.id === ABDELAAL_MAPPING_ID)!.protocol_id).toBe(ABDELAAL_PROTOCOL_ID);

    expect(new Set(newMappings.map((mapping) => mapping.protocol_id)).size).toBe(3);
    expect(new Set(newMappings.map((mapping) => mapping.endpoint)).size).toBe(3);
    expect(new Set(newMappings.map((mapping) => mapping.evidence_sha256)).size).toBe(3);

    for (const mapping of newMappings) {
      expect(mapping.review?.method).toBe("automated_source_review");
      expect(JSON.stringify(mapping)).not.toMatch(/rewire_run|Rewire execution/i);
    }
  });

  it("keeps the unknown-type and known-type-error endpoints explicitly distinct, never combined", () => {
    const inputs = loadUseCases()!.inputs;
    const snapshot = { ...baseline, release_id: "2026-10-06-000000000001", released_at: "2026-10-06T23:02:20Z", records };
    const artifact = buildUseCaseArtifact(snapshot, inputs);
    const byProtocol = new Map(
      artifact.mappings
        .filter((m) => m.use_case_id === "use-case-cell-type-annotation-transfer" && NEW_MAPPING_IDS.includes(m.id))
        .map((m) => [m.protocol_id, m]),
    );

    const absent = byProtocol.get("ucc-research-protocol-sctab-uncertainty-absent")!;
    expect(absent.endpoint).toMatch(/absent from training/);
    expect(absent.endpoint).not.toMatch(/incorrect/i);
    expect(JSON.stringify(absent.limitations)).toMatch(/unknown\/absent-type detection only/);
    expect(JSON.stringify(absent.limitations)).toMatch(/must not be combined/);

    const error = byProtocol.get("ucc-research-protocol-sctab-uncertainty-error")!;
    expect(error.endpoint).toMatch(/correctly from incorrectly predicted/);
    expect(error.endpoint).not.toMatch(/absent from training/);
    expect(JSON.stringify(error.rationale)).toMatch(/NOT an unknown-type or absent-reference detection result/);
    expect(JSON.stringify(error.limitations)).toMatch(/not unknown-type or absent-reference detection/);

    // Neither mapping's own citations/limitations ever states the other's headline number
    // as if it were evidence for the same endpoint.
    expect(JSON.stringify(absent)).not.toMatch(/0\.891 is (also )?unknown/i);
    expect(JSON.stringify(error)).not.toMatch(/0\.782 is (also )?known-type error/i);

    const abdelaal = byProtocol.get(ABDELAAL_PROTOCOL_ID)!;
    expect(JSON.stringify(abdelaal.constraints)).toMatch(/INTRA-dataset/);
    // The mapping explicitly disclaims cross-study/cross-platform scope (a correct negative
    // statement); it must never affirmatively claim cross-study/cross-platform coverage.
    expect(JSON.stringify(abdelaal)).toMatch(/does not establish cross-study or cross-platform/);
    expect(JSON.stringify(abdelaal)).not.toMatch(/establishes? cross-study|establishes? cross-platform|demonstrates? cross-study|demonstrates? cross-platform/i);
  });

  it("transcribes both scTab ROC-AUC values exactly as printed, with distinct locators", () => {
    const byId = new Map<string, RecordEntry>(newRecords.map((record) => [record.id, record]));

    const absent = byId.get("ucc-research-result-sctab-uncertainty-absent-rocauc")!;
    expect(absent.attributes.printed_value).toBe("0.782");
    expect(absent.attributes.numeric_value).toBe("0.782");
    expect(absent.attributes.metric).toBe("roc-auc");
    expect(String(absent.attributes.source_locator)).toMatch(/Group 3/);

    const error = byId.get("ucc-research-result-sctab-uncertainty-error-rocauc")!;
    expect(error.attributes.printed_value).toBe("0.891");
    expect(error.attributes.numeric_value).toBe("0.891");
    expect(error.attributes.metric).toBe("roc-auc");
    expect(String(error.attributes.source_locator)).toMatch(/Group 2/);

    // Neither protocol claims a whole-study or whole-platform holdout, and neither
    // invents the unstated Group 2/Group 3 denominators.
    const protoAbsent = byId.get("ucc-research-protocol-sctab-uncertainty-absent")!;
    const protoError = byId.get("ucc-research-protocol-sctab-uncertainty-error")!;
    for (const proto of [protoAbsent, protoError]) {
      expect(JSON.stringify(proto)).not.toMatch(/cross-study|cross-platform|whole-study holdout/i);
      expect(JSON.stringify(proto.attributes.limitations)).toMatch(/not stated in the retrieved main text/);
    }
  });

  it("transcribes all four Abdelaal median F1 values and three unlabeled percentages exactly as printed, intra-dataset only", () => {
    const byId = new Map<string, RecordEntry>(newRecords.map((record) => [record.id, record]));

    const f1Values: Record<string, string> = {
      "ucc-research-result-abdelaal-baron-human-svm-rejection-medianf1": "0.991",
      "ucc-research-result-abdelaal-baron-human-scmapcell-medianf1": "0.984",
      "ucc-research-result-abdelaal-baron-human-scpred-medianf1": "0.981",
      "ucc-research-result-abdelaal-baron-human-svm-medianf1": "0.980",
    };
    for (const [id, value] of Object.entries(f1Values)) {
      const result = byId.get(id)!;
      expect(result.attributes.metric).toBe("median-f1");
      expect(result.attributes.printed_value).toBe(value);
      expect(result.attributes.numeric_value).toBe(value);
    }

    const unlabeledValues: Record<string, string> = {
      "ucc-research-result-abdelaal-baron-human-svm-rejection-unlabeled": "1.5%",
      "ucc-research-result-abdelaal-baron-human-scmapcell-unlabeled": "4.2%",
      "ucc-research-result-abdelaal-baron-human-scpred-unlabeled": "10.8%",
    };
    for (const [id, value] of Object.entries(unlabeledValues)) {
      const result = byId.get(id)!;
      expect(result.attributes.metric).toBe("pct-unlabeled");
      expect(result.attributes.printed_value).toBe(value);
      // Percentage unlabeled is a coverage/rejection-rate tradeoff, not a metric with one
      // universal direction; it must use the schema's "unknown" value, never an invented one.
      expect(result.attributes.metric_direction).toBe("unknown");
      expect(String(result.attributes.scope_note)).toMatch(/F1\/rejection tradeoff/);
    }
    // median-F1 keeps its genuine "higher is better" direction.
    for (const id of Object.keys(f1Values)) {
      expect(byId.get(id)!.attributes.metric_direction).toBe("higher");
    }

    // SVM (no rejection) gets only a median-F1 result, no separate unlabeled-percentage record.
    expect(byId.has("ucc-research-result-abdelaal-baron-human-svm-unlabeled")).toBe(false);

    // Every Abdelaal result record's scope_note is a correct negative disclaimer (NOT
    // cross-study/cross-platform); none affirmatively claims cross-study/cross-platform scope.
    const abdelaalResultIds = [...byId.keys()].filter((id) => id.includes("abdelaal") && byId.get(id)!.kind === "result");
    expect(abdelaalResultIds.length).toBeGreaterThan(0);
    for (const id of abdelaalResultIds) {
      const serialized = JSON.stringify(byId.get(id));
      expect(serialized).toMatch(/NOT cross-study or cross-platform/);
      expect(serialized).not.toMatch(/establishes? cross-study|establishes? cross-platform|demonstrates? cross-study|demonstrates? cross-platform/i);
    }
    const protocol = byId.get("ucc-research-protocol-abdelaal-baron-human-intra")!;
    expect(JSON.stringify(protocol.attributes.limitations)).toMatch(/INTRA-dataset only/);
    expect(JSON.stringify(protocol)).toMatch(/does not establish cross-study or cross-platform/);
    const dataset = byId.get("ucc-research-data-abdelaal-baron-human")!;
    expect((dataset.attributes.population as { cells: number }).cells).toBe(8569);
    expect(JSON.stringify(dataset)).toMatch(/NOT a cross-study or cross-platform split/);
    // 8,569 is the Table 2 dataset size; it must not be asserted as a confirmed per-classifier
    // scored denominator anywhere in the dataset or protocol records.
    expect(JSON.stringify(dataset)).toMatch(/not independently confirmed as the exact scored denominator/);
    expect(JSON.stringify(protocol.attributes.limitations)).toMatch(/not independently confirmed as the exact scored denominator/);
  });

  it("gives the Abdelaal source a real, logged retrieved_at and a committed (non-workbench) cache artifact", () => {
    const byId = new Map<string, RecordEntry>(newRecords.map((record) => [record.id, record]));
    const source = byId.get("ucc-research-source-abdelaal-2019-paper")!;

    // retrieved_at must be the actual logged fetch time, not the earlier bounded batch
    // window's end (12:18:28Z) borrowed as if it were this file's own exact timestamp.
    expect(source.attributes.retrieved_at).toBe("2026-10-06T23:28:54Z");
    expect(source.attributes.retrieved_at).not.toBe("2026-10-06T12:18:28Z");

    // The retrieved bytes must be archived at a stable, committed (non-gitignored) path the
    // release build can read, not only the workbench scratch cache.
    const artifactPath = String(source.attributes.review_artifact);
    expect(artifactPath).toBe(
      "data/omics/use-case-coverage-20261006/research/artifacts/abdelaal-2019-pmc6734286-fulltext.xml.gz",
    );
    expect(fs.existsSync(artifactPath)).toBe(true);
    const bytes = gunzipSync(fs.readFileSync(artifactPath));
    expect(createHash("sha256").update(bytes).digest("hex")).toBe(source.attributes.sha256);
    expect(source.attributes.sha256).toBe("6df0937c5a2d8ba06465ba356c2321fb9f52d9ecf23456876acd82f828b41d4c");
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
