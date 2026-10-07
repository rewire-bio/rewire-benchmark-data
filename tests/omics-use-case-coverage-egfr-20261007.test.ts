import fs from "node:fs";
import { gunzipSync } from "node:zlib";
import { createHash } from "node:crypto";
import { describe, expect, it } from "vitest";
import { addUseCaseCoverage } from "../scripts/omics/use-case-coverage";
import { validateRecords, publicRecords, type RecordEntry } from "../scripts/omics/schema";
import { validateSnapshot } from "../services/omics/src/validation";
import { loadUseCases } from "../scripts/omics/use-cases";
import { buildUseCaseArtifact } from "../services/omics/src/use-cases";

const NEW_ROOT = "data/omics/use-case-coverage-egfr-20261007";
const PRIOR_MAPPING_ID = "use-case-mapping-20260930-345-ba1ec69965eb";
const NEW_MAPPING_ID = "use-case-mapping-20261007-345-7c4af3e091bd";
const SOURCE_ID = "ucc-clinical-egfr-source-civicfact-v3";
const PROTOCOL_ID = "ucc-clinical-egfr-protocol-civicfact-v3-retrieval";
const DATASET_ID = "ucc-clinical-egfr-data-civicfact-v3-postcutoff";
const CONFIG_MEDCPT_ID = "ucc-clinical-egfr-config-medcpt-ft";
const CONFIG_QWEN_ID = "ucc-clinical-egfr-config-qwen3-reranker-8b";
const EVAL_MEDCPT_ID = "ucc-clinical-egfr-eval-medcpt-ft-postcutoff";
const EVAL_QWEN_ID = "ucc-clinical-egfr-eval-qwen3-8b-postcutoff";
const RESULT_MEDCPT_ID = "ucc-clinical-egfr-result-medcpt-ft-postcutoff-appropriate";
const RESULT_QWEN_ID = "ucc-clinical-egfr-result-qwen3-8b-postcutoff-appropriate";
// Already-catalogued CIViC MCP records that must not be duplicated by this intake.
const EXISTING_CIVIC_MCP_IDS = [
  "uc-clinical-20260930-source-civic",
  "uc-clinical-20260930-source-civic-supp",
  "uc-clinical-20260930-civic-100-data",
];

describe("bounded EGFR NSCLC evidence-retrieval CIViC-Fact v3 intake, 2026-10-07", () => {
  const baseline = JSON.parse(
    gunzipSync(fs.readFileSync("data/omics/releases/2026-09-28-c7b5ac6d34f2/catalogue.json.gz")).toString(),
  );
  // Mirror the exact chain in scripts/omics/release.ts: default 20260930 root,
  // then 20261005, 20261006, 20261007, then the new egfr-20261007 root.
  const after1 = addUseCaseCoverage(baseline.records);
  const after2 = addUseCaseCoverage(after1, "data/omics/use-case-coverage-20261005");
  const after3 = addUseCaseCoverage(after2, "data/omics/use-case-coverage-20261006");
  const after4 = addUseCaseCoverage(after3, "data/omics/use-case-coverage-20261007");
  const records = addUseCaseCoverage(after4, NEW_ROOT);
  const newRecords = records.slice(after4.length);
  const byId = new Map<string, RecordEntry>(newRecords.map((record) => [record.id, record]));

  it("validates every new record and preserves every prior record byte-identically", () => {
    validateRecords(records);
    expect(records.slice(0, after4.length)).toEqual(after4);
    const snapshot = {
      ...baseline,
      release_id: "2026-10-07-000000000002",
      released_at: "2026-10-07T09:59:21Z",
      records,
    };
    validateSnapshot(snapshot);
  });

  it("adds exactly 9 new clinical-lane records, none claiming a new execution", () => {
    expect(newRecords).toHaveLength(9);
    for (const record of newRecords) {
      expect(record.status).not.toBe("reproduced");
      expect(record.attributes.origin).not.toBe("rewire_run");
    }
    expect(newRecords.filter((r) => r.kind === "source")).toHaveLength(1);
    expect(newRecords.filter((r) => r.kind === "dataset")).toHaveLength(1);
    expect(newRecords.filter((r) => r.kind === "protocol")).toHaveLength(1);
    expect(newRecords.filter((r) => r.kind === "configuration")).toHaveLength(2);
    expect(newRecords.filter((r) => r.kind === "evaluation")).toHaveLength(2);
    expect(newRecords.filter((r) => r.kind === "result")).toHaveLength(2);
  });

  it("does not duplicate the already-catalogued CIViC MCP source/dataset records", () => {
    for (const id of EXISTING_CIVIC_MCP_IDS) {
      expect(byId.has(id)).toBe(false);
      const existing = after4.find((r: RecordEntry) => r.id === id);
      expect(existing, `missing baseline record ${id}`).toBeDefined();
    }
    // No attributes appended to the existing CIViC MCP dataset record.
    const existingDataset = after4.find((r: RecordEntry) => r.id === "uc-clinical-20260930-civic-100-data")!;
    const newDataset = records.find((r) => r.id === "uc-clinical-20260930-civic-100-data")!;
    expect(newDataset).toEqual(existingDataset);
  });

  it("adds one new source record archived as a committed gzip artifact matching its declared SHA-256", () => {
    const source = byId.get(SOURCE_ID)!;
    expect(source.kind).toBe("source");
    expect(source.attributes.artifact_sha256).toBe(
      "6beb79ede82f7263a06eafc844bcb4ae41538323e3c9a9a7fa5420f08a8add55",
    );
    const artifactPath = String(source.attributes.review_artifact);
    expect(artifactPath).toBe(`${NEW_ROOT}/clinical/artifacts/civic-fact-v3-biorxiv.pdf.gz`);
    expect(fs.existsSync(artifactPath)).toBe(true);
    const bytes = gunzipSync(fs.readFileSync(artifactPath));
    expect(createHash("sha256").update(bytes).digest("hex")).toBe(source.attributes.artifact_sha256);
    // Distinct from the v2 PMC copy used in the prior research pass.
    expect(source.attributes.artifact_sha256).not.toBe(
      "2d07cf3123a919b2eba19919e8125f1cc79a250bb318466891fa447a6d7d6d12",
    );
  });

  it("records the nested GPLv3 LICENSE file precisely, without claiming the repository root has one or that it licenses every component", () => {
    const source = byId.get(SOURCE_ID)!;
    const reuse = String(source.attributes.code_data_model_reuse);
    // Root-level fact, unchanged: null licence metadata, no root LICENSE file.
    expect(reuse).toMatch(/Repository-root GitHub licence metadata is null/);
    expect(reuse).toMatch(/no root LICENSE file exists/);
    // The broad "no LICENSE file" claim is explicitly withdrawn.
    expect(reuse).not.toMatch(/has no LICENSE file and a null `license` field/);
    expect(reuse).toMatch(/does not mean the repository has no LICENSE file anywhere/);
    // Exact nested file, pinned commit, and blob identity.
    expect(reuse).toMatch(/data_builder\/LICENSE/);
    expect(reuse).toMatch(/GNU GPL version 3/);
    expect(reuse).toMatch(/1a767d889b015a836f0f4331afcac5cef165ec7f/);
    expect(reuse).toMatch(
      /https:\/\/github\.com\/creisle\/civicfact\/blob\/1a767d889b015a836f0f4331afcac5cef165ec7f\/data_builder\/LICENSE/,
    );
    // Adjacent pyproject.toml has no explicit licence declaration.
    expect(reuse).toMatch(/pyproject\.toml does not explicitly declare a licence/);
    // Scope is explicitly not assumed to cover every dataset/model/experiment component.
    expect(reuse).toMatch(/do not treat it as licensing every repository component/);
    // Article licence remains a separate fact; no code/data/model copies ingested.
    expect(reuse).toMatch(/Article licence \(CC-BY-4\.0\) is a separate fact/);
    expect(reuse).toMatch(/No code\/data\/model copies are included in this record/);
  });

  it("builds the post-cutoff 150->66->42->40 selection chain exactly on the dataset record", () => {
    const dataset = byId.get(DATASET_ID)!;
    expect(dataset.kind).toBe("dataset");
    const population = dataset.attributes.population as Record<string, unknown>;
    expect(population.candidate_entries).toBe(150);
    expect(population.excluded_full_text_not_accessible).toBe(68);
    expect(population.excluded_manuscript_in_train_dev_test).toBe(14);
    expect(population.excluded_non_content_data_error).toBe(2);
    expect(population.entries_curator_evaluated).toBe(66);
    expect(population.excluded_nei_requires_supplement_or_images).toBe(24);
    expect(population.entries_maintext_eligible).toBe(42);
    expect(population.excluded_nei_substantially_revised_claim).toBe(2);
    expect(population.entries_scored).toBe(40);
    const breakdown = population.scored_breakdown as Record<string, number>;
    expect(breakdown.revisions_major + breakdown.revisions_minor + breakdown.supports_no_revision).toBe(40);
    // Arithmetic check of the full chain.
    expect(150 - 68 - 14 - 2).toBe(66);
    expect(66 - 24).toBe(42);
    expect(42 - 2).toBe(40);
  });

  it("distinguishes the fine-tuned MedCPT configuration from the pretrained (not fine-tuned) Qwen3-Reranker-8B configuration", () => {
    const medcpt = byId.get(CONFIG_MEDCPT_ID)!;
    const qwen = byId.get(CONFIG_QWEN_ID)!;
    expect(medcpt.kind).toBe("configuration");
    expect(qwen.kind).toBe("configuration");
    const ft = medcpt.attributes.fine_tuning as Record<string, unknown>;
    expect(ft.effective_batch_size).toBe(64);
    expect(ft.learning_rate).toBe(0.00002);
    expect(ft.max_epochs).toBe(5);
    expect(ft.early_stopping).toBe(true);
    // No assumed seed, run count, checkpoint identity, or calibration procedure.
    expect(ft).not.toHaveProperty("seed");
    expect(ft).not.toHaveProperty("checkpoint");
    expect(ft).not.toHaveProperty("calibration");
    const qwenFt = qwen.attributes.fine_tuning as Record<string, unknown>;
    expect(qwenFt.applied).toBe(false);
    // Exact Huggingface namespace identifiers, confirmed via Table 4, distinguished from an
    // unreported immutable checkpoint revision.
    expect(String(medcpt.attributes.model_version)).toMatch(/ncbi\/MedCPT-Cross-Encoder/);
    expect(String(medcpt.attributes.model_version)).toMatch(/Table 4/);
    expect(String(medcpt.attributes.model_identity_note)).toMatch(/not an immutable checkpoint revision/);
    expect(String(qwen.attributes.model_version)).toMatch(/Qwen\/Qwen3-Reranker-8B/);
    expect(String(qwen.attributes.model_version)).toMatch(/Table 4/);
    expect(String(qwen.attributes.model_identity_note)).toMatch(/not an immutable checkpoint revision/);
  });

  it("gives each evaluation exactly one protocol, one configuration and one dataset link, sharing the same protocol and dataset", () => {
    const evalMedcpt = byId.get(EVAL_MEDCPT_ID)!;
    const evalQwen = byId.get(EVAL_QWEN_ID)!;
    for (const evaluation of [evalMedcpt, evalQwen]) {
      expect(evaluation.kind).toBe("evaluation");
      expect(evaluation.links.filter((l) => l.relation === "protocol")).toEqual([
        { relation: "protocol", target_id: PROTOCOL_ID },
      ]);
      expect(evaluation.links.filter((l) => l.relation === "dataset")).toEqual([
        { relation: "dataset", target_id: DATASET_ID },
      ]);
    }
    expect(evalMedcpt.links.filter((l) => l.relation === "configuration")).toEqual([
      { relation: "configuration", target_id: CONFIG_MEDCPT_ID },
    ]);
    expect(evalQwen.links.filter((l) => l.relation === "configuration")).toEqual([
      { relation: "configuration", target_id: CONFIG_QWEN_ID },
    ]);
  });

  it("transcribes both results as 37/40 (92.5%) on the identical cohort, higher direction, uncertainty unreported", () => {
    const resultMedcpt = byId.get(RESULT_MEDCPT_ID)!;
    const resultQwen = byId.get(RESULT_QWEN_ID)!;
    for (const result of [resultMedcpt, resultQwen]) {
      expect(result.kind).toBe("result");
      expect(result.attributes.unit).toBe("percent");
      expect(result.attributes.printed_value).toBe("37/40 (92.5%)");
      expect(result.attributes.numeric_value).toBe("92.5");
      expect(result.attributes.numerator).toBe(37);
      expect(result.attributes.denominator).toBe(40);
      expect(result.attributes.metric_direction).toBe("higher");
      expect(result.attributes.uncertainty).toBeNull();
      expect(result.source_ids).toEqual([SOURCE_ID]);
      // Locator must name the actual Results subsection, not the Methods heading.
      expect(String(result.attributes.source_locator)).toMatch(
        /Passage Retrieval Models Perform Well without Fine-Tuning/,
      );
      expect(String(result.attributes.source_locator)).not.toMatch(/^Results p\.14, 'Temporal evaluation'/);
      const missing = result.attributes.missing_metadata as Record<string, unknown>;
      expect(missing.reviewer_count).toBeTruthy();
      expect(missing.blinding).toBeTruthy();
      expect(missing.replicates_or_seeds).toBeTruthy();
      const serialized = JSON.stringify(result);
      expect(serialized).toMatch(/NOT an EGFR- or NSCLC-specific score/);
      expect(serialized).toMatch(/NOT a clinical efficacy result/);
      expect(serialized).toMatch(/NOT the static stance-classification accuracy/);
    }
    // Same cohort, not two independent cohorts.
    expect(resultMedcpt.attributes.printed_value).toBe(resultQwen.attributes.printed_value);
    const evalMedcpt = byId.get(EVAL_MEDCPT_ID)!;
    const evalQwen = byId.get(EVAL_QWEN_ID)!;
    expect(JSON.stringify(evalMedcpt)).toMatch(/one temporal cohort, not two independent cohorts/);
    expect(JSON.stringify(evalQwen)).toMatch(/one temporal cohort, not two independent cohorts/);
  });

  it("scopes the protocol to within-linked-publication retrieval, excluding open-corpus search and the static stance task", () => {
    const protocol = byId.get(PROTOCOL_ID)!;
    const serialized = JSON.stringify(protocol);
    expect(serialized).toMatch(/not a literature-search or citation-context benchmark/);
    expect(serialized).toMatch(/single publication CIViC already/);
    expect(serialized).toMatch(/not the static, separately-scoped retrieval-subset evaluation/);
    expect(JSON.stringify(protocol.attributes.limitations)).toMatch(/Pan-cancer protocol; no EGFR/);
    expect(JSON.stringify(protocol.attributes.limitations)).toMatch(/rewire-benchmarks #28/);
    // Manual review phrasing is neutral (no invented single-curator claim), and reviewer
    // count/blinding/replicate structure for the retrieval judgment is explicitly unreported,
    // distinguished from the separately described label-assignment consensus process.
    expect(serialized).not.toMatch(/A curator then manually judges/);
    expect(serialized).not.toMatch(/a curator manually judges 'appropriate' retrieval/);
    expect(serialized).toMatch(/UNREPORTED in the source/);
    expect(JSON.stringify(protocol.attributes.limitations)).toMatch(
      /Reviewer count, blinding, and replicate\/seed structure.*UNREPORTED/,
    );
  });

  it("gives the new mapping an active lifecycle, a fresh evidence fingerprint distinct from the prior mapping, and preserves the prior mapping byte-identically", () => {
    const reviewed = loadUseCases()!;
    const snapshot = {
      ...baseline,
      release_id: "2026-10-07-000000000002",
      released_at: "2026-10-07T09:59:21Z",
      records,
    };
    const artifact = buildUseCaseArtifact(snapshot, reviewed.inputs);
    const mappings = artifact.mappings.filter((m) => m.use_case_id === "use-case-egfr-nsclc-actionability-resistance-evidence");
    expect(mappings).toHaveLength(2);
    expect(mappings.every((m) => m.lifecycle === "active")).toBe(true);
    expect(mappings.every((m) => !("stale_from" in m))).toBe(true);

    const prior = mappings.find((m) => m.id === PRIOR_MAPPING_ID);
    expect(prior).toBeDefined();
    expect(prior!.evidence_sha256).toBe("87704e39bcce294a0e4e2aa7f06674b10169e976a057f55b805d09bd08423041");

    const newMapping = mappings.find((m) => m.id === NEW_MAPPING_ID)!;
    expect(newMapping).toBeDefined();
    expect(newMapping.protocol_id).toBe(PROTOCOL_ID);
    expect(newMapping.relevance).toBe("proxy");
    expect(newMapping.evaluation_ids).toEqual([EVAL_MEDCPT_ID, EVAL_QWEN_ID]);
    expect(newMapping.evidence_sha256).toMatch(/^[a-f0-9]{64}$/);
    expect(newMapping.evidence_sha256).not.toBe("0".repeat(64));
    // Refreshed after the fourth-cycle correction to the underlying records.
    expect(newMapping.evidence_sha256).toBe("73429814be7f5d20503b6cce41f30f875d995c497f97cb4d22987c30f1a14d90");
    expect(new Set(mappings.map((m) => m.evidence_sha256)).size).toBe(2);
    expect(newMapping.review?.method).toBe("automated_source_review");
  });

  it("keeps every new result public and source-checked", () => {
    const resultIds = newRecords.filter((record) => record.kind === "result").map((record) => record.id);
    expect(resultIds).toHaveLength(2);
    const published = new Set(publicRecords(records).map((record) => record.id));
    for (const id of resultIds) {
      expect(published.has(id)).toBe(true);
      expect(byId.get(id)!.status).toBe("source_checked");
    }
  });
});
