/** Reusable use-case coverage audit. Derives case/protocol/evaluation/result
 * IDs, active/stale mapping counts and source provenance from a generated
 * catalogue/use-case artifact. Reports every use case the artifact declares;
 * it never hard-codes a score, count or case list, so it stays correct as
 * AMP coverage (rewire.it#365, issues #10-18) and any later intake land. */
import fs from "node:fs";
import path from "node:path";
import {
  createUseCaseQuery,
  type ResolvedMapping,
  type UseCaseArtifact,
  type UseCaseDeclaration,
} from "../../services/omics/src/use-cases";
import type { CatalogueSnapshot } from "../../services/omics/src/catalogue-query";

export type MappingAudit = {
  mapping_id: string;
  lifecycle: ResolvedMapping["lifecycle"];
  relevance: ResolvedMapping["relevance"] | null;
  protocol_id: string | null;
  task_id: string | null;
  evaluation_ids: string[];
  result_ids: string[];
  numeric_result_count: number;
  missing_numeric_evidence: boolean;
  source_ids: string[];
};
export type UseCaseAudit = {
  use_case_id: string;
  slug: string;
  title: string;
  active_mappings: number;
  stale_mappings: number;
  withdrawn_mappings: number;
  missing_numeric_evidence: boolean;
  mappings: MappingAudit[];
};

function auditMapping(mapping: ResolvedMapping): MappingAudit {
  const evaluation_ids = mapping.evaluations.map((e) => e.evaluation.id);
  const resultIds: string[] = [];
  let numericResults = 0;
  for (const evaluation of mapping.evaluations) {
    for (const row of evaluation.results) {
      resultIds.push(row.result.id);
      if (row.result.attributes.numeric_value != null) numericResults += 1;
    }
  }
  const live = mapping.lifecycle === "active" && (mapping.relevance === "direct" || mapping.relevance === "proxy");
  return {
    mapping_id: mapping.id,
    lifecycle: mapping.lifecycle,
    relevance: mapping.relevance ?? null,
    protocol_id: mapping.protocol?.id ?? null,
    task_id: mapping.task?.id ?? null,
    evaluation_ids,
    result_ids: resultIds,
    numeric_result_count: numericResults,
    missing_numeric_evidence: live && numericResults === 0,
    source_ids: mapping.sources.map((s) => s.id),
  };
}

/** Walk every declared use case through the resolved query so coverage
 * reflects exactly what an active mapping actually supports, not the raw
 * curated input (which can include draft/needs_review/tombstoned entries). */
export function auditUseCaseCoverage(
  snapshot: CatalogueSnapshot,
  artifact: UseCaseArtifact,
  declaration: UseCaseDeclaration,
): UseCaseAudit[] {
  const query = createUseCaseQuery(snapshot, artifact, declaration);
  const results: UseCaseAudit[] = [];
  let cursor: string | undefined;
  do {
    const page = query.list({ limit: 100, ...(cursor ? { cursor } : {}) });
    for (const entry of page.items) {
      const detail = query.get({ slug: entry.slug });
      if (!detail) continue;
      const mappings = detail.mappings.map(auditMapping);
      results.push({
        use_case_id: entry.id,
        slug: entry.slug,
        title: entry.title,
        active_mappings: mappings.filter((m) => m.lifecycle === "active").length,
        stale_mappings: mappings.filter((m) => m.lifecycle === "needs_review").length,
        withdrawn_mappings: mappings.filter((m) => ["withdrawn", "superseded"].includes(m.lifecycle)).length,
        missing_numeric_evidence: !mappings.some((m) => m.lifecycle === "active" &&
          (m.relevance === "direct" || m.relevance === "proxy") && m.numeric_result_count > 0),
        mappings,
      });
    }
    cursor = page.next_cursor || undefined;
  } while (cursor);
  return results.sort((a, b) => a.use_case_id.localeCompare(b.use_case_id));
}

/** Missing release inputs are audit failures, including undeclared coverage. */
export function loadCoverageAudit(root = process.cwd()) {
  const catalogueFile = path.join(root, "public/omics/catalogue.json");
  const manifestFile = path.join(root, "public/omics/manifest.json");
  if (!fs.existsSync(catalogueFile) || !fs.existsSync(manifestFile))
    throw Error("No built release found. Run the release build before auditing use-case coverage.");
  const snapshot: CatalogueSnapshot = JSON.parse(fs.readFileSync(catalogueFile, "utf8"));
  const manifest = JSON.parse(fs.readFileSync(manifestFile, "utf8"));
  if (!manifest.coverage?.use_cases)
    throw Error("This release declares no use-case coverage.");
  if (manifest.release_id !== snapshot.release_id)
    throw Error("Catalogue and manifest release IDs differ.");
  const artifactFile = path.join(root, "public/omics/releases", manifest.release_id, "use-cases.json");
  if (!fs.existsSync(artifactFile))
    throw Error(`Missing use-cases.json for release ${manifest.release_id}`);
  const artifact: UseCaseArtifact = JSON.parse(fs.readFileSync(artifactFile, "utf8"));
  const audits = auditUseCaseCoverage(snapshot, artifact, manifest.coverage.use_cases);
  return { release_id: manifest.release_id as string, audits };
}

function main() {
  const report = loadCoverageAudit();
  if (process.argv.includes("--json")) {
    console.log(JSON.stringify(report, null, 2));
    return;
  }
  console.log(`Release ${report.release_id}: ${report.audits.length} use cases`);
  for (const audit of report.audits) {
    console.log(`${audit.use_case_id} (${audit.slug}): ${audit.active_mappings} active, ${audit.stale_mappings} needs_review, ${audit.withdrawn_mappings} withdrawn${audit.missing_numeric_evidence ? "; missing active numeric evidence" : ""}`);
    for (const mapping of audit.mappings.filter((m) => m.missing_numeric_evidence))
      console.log(`  missing numeric evidence: ${mapping.mapping_id} (protocol ${mapping.protocol_id ?? "none"}, evaluations ${mapping.evaluation_ids.join(", ") || "none"})`);
  }
  const missing = report.audits.flatMap((a) => a.mappings.filter((m) => m.missing_numeric_evidence));
  console.log(`${missing.length} active direct/proxy mappings and ${report.audits.filter((a) => a.missing_numeric_evidence).length} use cases without numeric evidence.`);
}
if (process.argv[1]?.endsWith("audit-amp-coverage.ts")) {
  try { main(); }
  catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  }
}
