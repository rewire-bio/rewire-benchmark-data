import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";
import { gunzipSync } from "node:zlib";
import { describe, expect, it } from "vitest";
import { addUseCaseCoverage } from "../scripts/omics/use-case-coverage";
import { validateRecords } from "../scripts/omics/schema";
import { validateSnapshot } from "../services/omics/src/validation";
import { loadUseCases } from "../scripts/omics/use-cases";
import { buildUseCaseArtifact, mappingEvidenceHash, useCaseDeclaration } from "../services/omics/src/use-cases";
import { auditUseCaseCoverage, loadCoverageAudit } from "../scripts/omics/audit-amp-coverage";

describe("use-case coverage audit", () => {
  it("derives per-case mapping, protocol, evaluation and result IDs from the generated artifact", () => {
    const baseline = JSON.parse(gunzipSync(fs.readFileSync("data/omics/releases/2026-09-28-c7b5ac6d34f2/catalogue.json.gz")).toString());
    // Mirrors the exact chain in scripts/omics/release.ts.
    const afterFirstIntake = addUseCaseCoverage(baseline.records);
    const afterSecondIntake = addUseCaseCoverage(afterFirstIntake, "data/omics/use-case-coverage-20261005");
    const afterThirdIntake = addUseCaseCoverage(afterSecondIntake, "data/omics/use-case-coverage-20261006");
    const afterFourthIntake = addUseCaseCoverage(afterThirdIntake, "data/omics/use-case-coverage-20261007");
    const afterEgfr = addUseCaseCoverage(afterFourthIntake, "data/omics/use-case-coverage-egfr-20261007");
    const afterPerturbation = addUseCaseCoverage(afterEgfr, "data/omics/use-case-coverage-genetic-perturbation-20261007");
    const records = addUseCaseCoverage(afterPerturbation, "data/omics/use-case-coverage-amp-20261007");
    validateRecords(records);
    const snapshot = { ...baseline, release_id: "2026-10-05-000000000000", released_at: "2026-10-05T21:00:00Z", records };
    validateSnapshot(snapshot);
    const inputs = loadUseCases()!.inputs;
    const artifact = buildUseCaseArtifact(snapshot, inputs);
    const declaration = useCaseDeclaration(inputs);

    const audits = auditUseCaseCoverage(snapshot, artifact, declaration);

    expect(audits).toHaveLength(artifact.use_cases.length);
    expect(audits.map((a) => a.use_case_id)).toEqual([...audits.map((a) => a.use_case_id)].sort());
    for (const audit of audits) {
      expect(artifact.use_cases.some((u) => u.id === audit.use_case_id && u.slug === audit.slug)).toBe(true);
      for (const mapping of audit.mappings) {
        expect(artifact.mappings.some((m) => m.id === mapping.mapping_id)).toBe(true);
        expect(mapping.numeric_result_count).toBeLessThanOrEqual(mapping.result_ids.length);
        if (mapping.lifecycle === "withdrawn" || mapping.lifecycle === "superseded") {
          expect(mapping.evaluation_ids).toHaveLength(0);
          expect(mapping.result_ids).toHaveLength(0);
          expect(mapping.missing_numeric_evidence).toBe(false);
        }
      }
      expect(audit.active_mappings + audit.stale_mappings + audit.withdrawn_mappings).toBeLessThanOrEqual(audit.mappings.length);
    }
    // At least one reviewed, source-checked AMP-priority case already carries numeric evidence end to end.
    const withEvidence = audits.find((a) => a.mappings.some((m) => m.numeric_result_count > 0));
    expect(withEvidence).toBeDefined();
  });

  it("flags a live mapping whose evaluations have no numeric result", () => {
    const { snapshot, useCase, draftMapping } = fixture();
    const audits = auditFixture(snapshot, [useCase], [draftMapping]);
    expect(audits[0].mappings[0].evaluation_ids).toEqual(["eval-1"]);
    expect(audits[0].mappings[0].missing_numeric_evidence).toBe(true);
    expect(audits[0].missing_numeric_evidence).toBe(true);
  });

  it.each(["direct", "proxy"])("flags an active %s mapping with no evaluations", (relevance) => {
    const { snapshot, useCase, draftMapping } = fixture();
    const audits = auditFixture(snapshot, [useCase], [{ ...draftMapping, relevance, evaluation_ids: [] }]);
    expect(audits[0].mappings[0].lifecycle).toBe("active");
    expect(audits[0].mappings[0].evaluation_ids).toEqual([]);
    expect(audits[0].mappings[0].missing_numeric_evidence).toBe(true);
    expect(audits[0].missing_numeric_evidence).toBe(true);
  });

  it("flags an entirely unmapped declared case", () => {
    const { snapshot, useCase } = fixture();
    const audits = auditFixture(snapshot, [useCase], []);
    expect(audits[0].mappings).toEqual([]);
    expect(audits[0].missing_numeric_evidence).toBe(true);
  });

  it("withholds stale evidence and flags the case despite a numeric source result", () => {
    const { snapshot, useCase, draftMapping } = fixture();
    snapshot.records.find((r: any) => r.id === "result-1").attributes.numeric_value = 42;
    const inputs = reviewedInputs(snapshot, [useCase], [draftMapping]);
    snapshot.records.find((r: any) => r.id === "protocol-1").name = "Changed protocol";
    const audits = auditUseCaseCoverage(snapshot, buildUseCaseArtifact(snapshot, inputs), useCaseDeclaration(inputs));
    expect(audits[0].stale_mappings).toBe(1);
    expect(audits[0].mappings[0].evaluation_ids).toEqual([]);
    expect(audits[0].mappings[0].result_ids).toEqual([]);
    expect(audits[0].mappings[0].missing_numeric_evidence).toBe(false);
    expect(audits[0].missing_numeric_evidence).toBe(true);
  });

  it("recognizes active numeric evidence at case level", () => {
    const { snapshot, useCase, draftMapping } = fixture();
    snapshot.records.find((r: any) => r.id === "result-1").attributes.numeric_value = 0;
    const audits = auditFixture(snapshot, [useCase], [draftMapping]);
    expect(audits[0].mappings[0].numeric_result_count).toBe(1);
    expect(audits[0].missing_numeric_evidence).toBe(false);
  });

  it("visits all 101 cases across pagination and accepts an empty declaration", () => {
    const { snapshot, useCase } = fixture();
    const cases = Array.from({ length: 101 }, (_, i) => ({ ...useCase, id: `uc-${i}`, slug: `case-${i}` }));
    const audits = auditFixture(snapshot, cases, []);
    expect(audits).toHaveLength(101);
    expect(new Set(audits.map((a) => a.use_case_id)).size).toBe(101);
    expect(audits.every((a) => a.missing_numeric_evidence)).toBe(true);
    expect(auditFixture(snapshot, [], [])).toEqual([]);
  });

  it("fails for missing build, declaration or declared artifact", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "amp-audit-"));
    try {
      expect(() => loadCoverageAudit(root)).toThrow("No built release found");
      fs.mkdirSync(path.join(root, "public/omics"), { recursive: true });
      fs.writeFileSync(path.join(root, "public/omics/catalogue.json"), JSON.stringify({ release_id: "release" }));
      const manifest = path.join(root, "public/omics/manifest.json");
      fs.writeFileSync(manifest, JSON.stringify({ release_id: "release", coverage: {} }));
      expect(() => loadCoverageAudit(root)).toThrow("declares no use-case coverage");
      fs.writeFileSync(manifest, JSON.stringify({ release_id: "release", coverage: { use_cases: {} } }));
      expect(() => loadCoverageAudit(root)).toThrow("Missing use-cases.json");
      const cli = spawnSync(process.execPath, ["--import", pathToFileURL(createRequire(import.meta.url).resolve("tsx")).href, path.resolve("scripts/omics/audit-amp-coverage.ts"), "--json"], { cwd: root, encoding: "utf8" });
      expect(cli.status).toBe(1);
      expect(cli.stderr).toContain("Missing use-cases.json");
      expect(cli.stdout).toBe("");
      const { snapshot, useCase } = fixture();
      const inputs = reviewedInputs(snapshot, [useCase], []);
      const artifact = buildUseCaseArtifact(snapshot, inputs);
      fs.writeFileSync(path.join(root, "public/omics/catalogue.json"), JSON.stringify(snapshot));
      fs.writeFileSync(manifest, JSON.stringify({ release_id: snapshot.release_id, coverage: { use_cases: useCaseDeclaration(inputs) } }));
      const artifactDir = path.join(root, "public/omics/releases", snapshot.release_id);
      fs.mkdirSync(artifactDir, { recursive: true });
      fs.writeFileSync(path.join(artifactDir, "use-cases.json"), JSON.stringify(artifact));
      const success = spawnSync(process.execPath, ["--import", pathToFileURL(createRequire(import.meta.url).resolve("tsx")).href, path.resolve("scripts/omics/audit-amp-coverage.ts"), "--json"], { cwd: root, encoding: "utf8" });
      expect(success.status).toBe(0);
      const report = JSON.parse(success.stdout);
      expect(report.release_id).toBe(snapshot.release_id);
      expect(report.audits[0].missing_numeric_evidence).toBe(true);
    } finally { fs.rmSync(root, { recursive: true, force: true }); }
  });
});

function fixture() {
    const snapshot = {
      schema_version: "1.1" as const,
      release_id: "2026-10-05-aaaaaaaaaaaa",
      released_at: "2026-10-05T00:00:00Z",
      coverage: {},
      records: [
        { id: "src-1", kind: "source", name: "Source", description: "d", status: "source_checked",
          facets: {}, source_ids: [], links: [], attributes: { url: "https://example.org", version: "1", retrieved_at: "2026-10-01T00:00:00Z" } },
        { id: "protocol-1", kind: "protocol", name: "Protocol", description: "d", status: "source_checked",
          facets: {}, source_ids: ["src-1"], links: [], attributes: { version: "1", task: "t", scope_note: "n", missing_metadata: [] } },
        { id: "config-1", kind: "configuration", name: "Config", description: "d", status: "source_checked",
          facets: {}, source_ids: ["src-1"], links: [], attributes: { version: "1", reported_name: "Config", missing_metadata: [] } },
        { id: "eval-1", kind: "evaluation", name: "Evaluation", description: "d", status: "source_checked",
          facets: {}, source_ids: ["src-1"], links: [{ relation: "protocol", target_id: "protocol-1" }, { relation: "configuration", target_id: "config-1" }],
          attributes: { origin: "author_reported", protocol: "protocol-1", version: "1", comparison: {}, missing_metadata: [] } },
        { id: "result-1", kind: "result", name: "Result", description: "d", status: "source_checked",
          facets: {}, source_ids: ["src-1"], links: [{ relation: "evaluation", target_id: "eval-1" }],
          attributes: {
            printed_value: "not reported", numeric_value: null, metric: "m", metric_direction: "unknown",
            unit: null, uncertainty: null, source_locator: "p1",
            review: { method: "automated_source_review", reviewer: "test", reviewed_at: "2026-10-01T00:00:00Z", notes: "n" },
            missing_metadata: [],
          } },
      ],
    } as any;
    const useCase = {
      id: "uc-1", slug: "uc-1", title: "Case", question: "Q?", area: "area",
      contexts: ["research"], search_terms: [], intended_users: ["u"], decision: "d",
      inputs: ["i"], output: "o", setting: "s", exclusions: [],
      clinical_scope: "c", evidence_gaps: [],
      citations: [{ source_id: "src-1", locator: "p1" }],
      review: { method: "automated_source_review", actor: "test", reviewed_at: "2026-10-01T00:00:00Z", note: "n" },
      planned_work: [],
    };
    const draftMapping = {
      id: "map-1", use_case_id: "uc-1", lifecycle: "active" as const, revision: 1, reason: "r",
      protocol_id: "protocol-1", evaluation_ids: ["eval-1"], endpoint: "e", relevance: "direct" as const,
      rationale: "r", constraints: [], limitations: [],
      citations: [{ source_id: "src-1", locator: "p1" }],
      review: { method: "automated_source_review" as const, actor: "test", reviewed_at: "2026-10-01T00:00:00Z", note: "n" },
    };
    return { snapshot, useCase, draftMapping };
}
function reviewedInputs(snapshot: any, use_cases: any[], mappings: any[]) {
  return { schema_version: "1.0" as const, use_cases, mappings: mappings.map((mapping) => ({
    ...mapping, evidence_sha256: mappingEvidenceHash(snapshot, use_cases.find((u) => u.id === mapping.use_case_id), mapping),
  })) };
}
function auditFixture(snapshot: any, cases: any[], mappings: any[]) {
  const inputs = reviewedInputs(snapshot, cases, mappings);
  return auditUseCaseCoverage(snapshot, buildUseCaseArtifact(snapshot, inputs), useCaseDeclaration(inputs));
}
