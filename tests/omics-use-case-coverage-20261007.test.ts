import fs from "node:fs";
import { gunzipSync } from "node:zlib";
import { createHash } from "node:crypto";
import { describe, expect, it } from "vitest";
import { addUseCaseCoverage } from "../scripts/omics/use-case-coverage";
import { validateRecords, publicRecords, type RecordEntry } from "../scripts/omics/schema";
import { validateSnapshot } from "../services/omics/src/validation";
import { loadUseCases } from "../scripts/omics/use-cases";
import { buildUseCaseArtifact } from "../services/omics/src/use-cases";

const NEW_ROOT = "data/omics/use-case-coverage-20261007";
const PRIOR_MAPPING_IDS = [
  "use-case-mapping-20260930-349-1af09c2e0e0f",
  "use-case-mapping-20261006-349-2cfbe5c7674a",
  "use-case-mapping-20261006-349-6a9d63555f43",
  "use-case-mapping-20261006-349-967caca02e7d",
];
const PROTOCOL_ID = "ucc-research-protocol-abdelaal-brain-inter-34pop";
const SUPP_SOURCE_ID = "ucc-research-source-abdelaal-2019-supplement";
const REUSED_METHOD_ID = "ucc-research-method-abdelaal-svm-linear";
const REUSED_CONFIG_ID = "ucc-research-config-abdelaal-svm-rejection";

const EXPECTED_VALUES: Record<string, string> = {
  "ucc-research-result-abdelaal-brain-alm-from-visp-unlabeled": "16.4%",
  "ucc-research-result-abdelaal-brain-alm-from-mtg-unlabeled": "84.6%",
  "ucc-research-result-abdelaal-brain-alm-from-visp-mtg-unlabeled": "22.2%",
  "ucc-research-result-abdelaal-brain-mtg-from-visp-unlabeled": "99%",
  "ucc-research-result-abdelaal-brain-mtg-from-alm-unlabeled": "99.6%",
  "ucc-research-result-abdelaal-brain-mtg-from-visp-alm-unlabeled": "99.5%",
  "ucc-research-result-abdelaal-brain-visp-from-alm-unlabeled": "14.8%",
  "ucc-research-result-abdelaal-brain-visp-from-mtg-unlabeled": "81.1%",
  "ucc-research-result-abdelaal-brain-visp-from-alm-mtg-unlabeled": "22.1%",
};

describe("bounded cell-type-annotation-transfer Figure S10 Panel B intake, 2026-10-07", () => {
  const baseline = JSON.parse(
    gunzipSync(fs.readFileSync("data/omics/releases/2026-09-28-c7b5ac6d34f2/catalogue.json.gz")).toString(),
  );
  // Mirror the exact chain in scripts/omics/release.ts: default 20260930 root,
  // then 20261005, then 20261006, then the new 20261007 root.
  const afterFirst = addUseCaseCoverage(baseline.records);
  const afterSecond = addUseCaseCoverage(afterFirst, "data/omics/use-case-coverage-20261005");
  const afterThird = addUseCaseCoverage(afterSecond, "data/omics/use-case-coverage-20261006");
  const afterFourth = addUseCaseCoverage(afterThird, NEW_ROOT);
  const afterEgfr = addUseCaseCoverage(afterFourth, "data/omics/use-case-coverage-egfr-20261007");
  const records = addUseCaseCoverage(afterEgfr, "data/omics/use-case-coverage-amp-20261007");
  const newRecords = records.slice(afterThird.length, afterFourth.length);
  const byId = new Map<string, RecordEntry>(newRecords.map((record) => [record.id, record]));

  it("validates every new record and preserves every prior record byte-identically", () => {
    validateRecords(records);
    expect(records.slice(0, afterThird.length)).toEqual(afterThird);
    const snapshot = {
      ...baseline,
      release_id: "2026-10-07-000000000001",
      released_at: "2026-10-07T07:44:08Z",
      records,
    };
    validateSnapshot(snapshot);
  });

  it("adds exactly 23 new research-lane records, none claiming a new execution", () => {
    expect(newRecords).toHaveLength(23);
    for (const record of newRecords) {
      expect(record.status).not.toBe("reproduced");
      expect(record.attributes.origin).not.toBe("rewire_run");
    }
    expect(newRecords.filter((r) => r.kind === "source")).toHaveLength(1);
    expect(newRecords.filter((r) => r.kind === "dataset")).toHaveLength(3);
    expect(newRecords.filter((r) => r.kind === "protocol")).toHaveLength(1);
    expect(newRecords.filter((r) => r.kind === "method")).toHaveLength(0);
    expect(newRecords.filter((r) => r.kind === "configuration")).toHaveLength(0);
    expect(newRecords.filter((r) => r.kind === "evaluation")).toHaveLength(9);
    expect(newRecords.filter((r) => r.kind === "result")).toHaveLength(9);
  });

  it("adds exactly one new source record (the supplement PDF), a separate artifact from the already-catalogued main-text XML", () => {
    const sources = newRecords.filter((r) => r.kind === "source");
    expect(sources).toHaveLength(1);
    expect(sources[0].id).toBe(SUPP_SOURCE_ID);
    expect(sources[0].attributes.sha256).toBe("797a2b22f584135f4ff6f7c98203d8e9529d6600f675b500205607b47b212a81");
    expect(sources[0].attributes.sha256).not.toBe("6df0937c5a2d8ba06465ba356c2321fb9f52d9ecf23456876acd82f828b41d4c");

    const artifactPath = String(sources[0].attributes.review_artifact);
    expect(artifactPath).toBe(`${NEW_ROOT}/research/artifacts/abdelaal-2019-pmc6734286-supplement1.pdf.gz`);
    expect(fs.existsSync(artifactPath)).toBe(true);
    const bytes = gunzipSync(fs.readFileSync(artifactPath));
    expect(createHash("sha256").update(bytes).digest("hex")).toBe(sources[0].attributes.sha256);
  });

  it("reuses the existing SVMrejection method and configuration records by reference, unmodified", () => {
    const baselineById = new Map<string, RecordEntry>(afterThird.map((r: RecordEntry) => [r.id, r]));
    const method = baselineById.get(REUSED_METHOD_ID)!;
    const config = baselineById.get(REUSED_CONFIG_ID)!;
    expect(method).toBeDefined();
    expect(config).toBeDefined();
    // Neither reused record appears again among the new records (no duplication).
    expect(byId.has(REUSED_METHOD_ID)).toBe(false);
    expect(byId.has(REUSED_CONFIG_ID)).toBe(false);
    // Every new evaluation links to the existing configuration, never a new one.
    const evaluations = newRecords.filter((r) => r.kind === "evaluation");
    expect(evaluations).toHaveLength(9);
    for (const evaluation of evaluations) {
      const configLinks = evaluation.links.filter((l) => l.relation === "configuration");
      expect(configLinks).toEqual([{ relation: "configuration", target_id: REUSED_CONFIG_ID }]);
      const protocolLinks = evaluation.links.filter((l) => l.relation === "protocol");
      expect(protocolLinks).toEqual([{ relation: "protocol", target_id: PROTOCOL_ID }]);
      expect(evaluation.source_ids).toEqual([SUPP_SOURCE_ID]);
    }
  });

  it("transcribes all nine Figure S10 Panel B SVMrejection values exactly as printed, metric_direction unknown, denominator unreported", () => {
    expect(Object.keys(EXPECTED_VALUES)).toHaveLength(9);
    for (const [id, printed] of Object.entries(EXPECTED_VALUES)) {
      const result = byId.get(id)!;
      expect(result, `missing result ${id}`).toBeDefined();
      expect(result.kind).toBe("result");
      expect(result.attributes.metric).toBe("pct-unlabeled");
      expect(result.attributes.printed_value).toBe(printed);
      expect(result.attributes.numeric_value).toBe(printed.replace("%", ""));
      // Never a universal performance direction for a coverage/rejection-rate figure.
      expect(result.attributes.metric_direction).toBe("unknown");
      expect(result.source_ids).toEqual([SUPP_SOURCE_ID]);
      const serialized = JSON.stringify(result);
      expect(serialized).toMatch(/UNREPORTED/);
      expect(serialized).not.toMatch(/12,?832|8,?758|14,?636/);
    }
  });

  it("every result and the protocol explicitly disclaim superiority and unknown-type-detection accuracy claims", () => {
    for (const [id] of Object.entries(EXPECTED_VALUES)) {
      const scopeNote = String(byId.get(id)!.attributes.scope_note);
      expect(scopeNote, id).toMatch(/NOT a known-type accuracy claim/);
      expect(scopeNote, id).toMatch(/NOT an unknown\/absent-type-detection accuracy claim/);
      expect(scopeNote, id).toMatch(/NOT a superiority claim/);
    }
    const protocol = byId.get(PROTOCOL_ID)!;
    expect(JSON.stringify(protocol.attributes.limitations)).toMatch(/NOT a known-type accuracy claim/);
    expect(JSON.stringify(protocol.attributes.limitations)).toMatch(/NOT an unknown\/absent-type-detection accuracy claim/);
    expect(JSON.stringify(protocol.attributes.limitations)).toMatch(/NOT.*SVMrejection outperforms or underperforms/);
  });

  it("marks the scored denominator unreported and Table 2 counts as context only on the dataset records", () => {
    const datasets = newRecords.filter((r) => r.kind === "dataset");
    expect(datasets).toHaveLength(3);
    const expectedCells: Record<string, number> = {
      "ucc-research-data-abdelaal-visp": 12832,
      "ucc-research-data-abdelaal-alm": 8758,
      "ucc-research-data-abdelaal-mtg": 14636,
    };
    for (const dataset of datasets) {
      expect((dataset.attributes.population as { cells: number }).cells).toBe(expectedCells[dataset.id]);
      expect(JSON.stringify(dataset.attributes.population)).toMatch(/context only/);
      expect(JSON.stringify(dataset.attributes.population)).toMatch(/NOT independently confirmed as the exact scored denominator/);
    }
    const protocol = byId.get(PROTOCOL_ID)!;
    expect(JSON.stringify(protocol.attributes.limitations)).toMatch(/UNREPORTED/);
    expect(JSON.stringify(protocol.attributes.limitations)).toMatch(/context only/);
  });

  it("scopes the protocol to Figure S10 Panel B only, explicitly excluding Panel A, the other 17 classifiers, and Figure S9", () => {
    const protocol = byId.get(PROTOCOL_ID)!;
    const serialized = JSON.stringify(protocol);
    expect(serialized).toMatch(/Only the SVMrejection row/);
    expect(serialized).toMatch(/Figure S10 Panel A.*is a separate figure\/protocol and is not ingested/);
    expect(serialized).toMatch(/Figure S9 Panel A.*carries no printed digit labels/);
    expect(serialized).toMatch(/conflict between its own caption text.*the page's only legend.*the figure's overall title/);
  });

  it("gives the new mapping an active lifecycle, a fresh evidence fingerprint, and preserves the four prior mappings byte-identically", () => {
    const reviewed = loadUseCases()!;
    const snapshot = {
      ...baseline,
      release_id: "2026-10-07-000000000001",
      released_at: "2026-10-07T07:44:08Z",
      records,
    };
    const artifact = buildUseCaseArtifact(snapshot, reviewed.inputs);
    const mappings = artifact.mappings.filter((m) => m.use_case_id === "use-case-cell-type-annotation-transfer");
    expect(mappings).toHaveLength(5);
    expect(mappings.every((m) => m.lifecycle === "active")).toBe(true);
    expect(mappings.every((m) => !("stale_from" in m))).toBe(true);

    for (const id of PRIOR_MAPPING_IDS) {
      expect(mappings.find((m) => m.id === id)).toBeDefined();
    }
    const newMapping = mappings.find((m) => !PRIOR_MAPPING_IDS.includes(m.id))!;
    expect(newMapping).toBeDefined();
    expect(newMapping.protocol_id).toBe(PROTOCOL_ID);
    expect(newMapping.relevance).toBe("proxy");
    expect(newMapping.evaluation_ids).toHaveLength(9);
    expect(newMapping.evidence_sha256).toMatch(/^[a-f0-9]{64}$/);
    expect(newMapping.evidence_sha256).not.toBe("0".repeat(64));
    expect(new Set(mappings.map((m) => m.evidence_sha256)).size).toBe(5);
    expect(newMapping.review?.method).toBe("automated_source_review");
  });

  it("keeps every new result public and source-checked", () => {
    const resultIds = newRecords.filter((record) => record.kind === "result").map((record) => record.id);
    expect(resultIds).toHaveLength(9);
    const published = new Set(publicRecords(records).map((record) => record.id));
    for (const id of resultIds) {
      expect(published.has(id)).toBe(true);
      expect(byId.get(id)!.status).toBe("source_checked");
    }
  });
});
