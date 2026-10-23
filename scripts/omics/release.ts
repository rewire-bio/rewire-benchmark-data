import { currentRecords } from "../../shared/omics/current";
import { benchmarkCoverage as benchmarkPageCoverage } from "../../shared/omics/benchmark-coverage";
import { validateSnapshot } from "../../shared/omics/validation";
import { writeBaselineAudit } from "./baseline-coverage";
import { writeImmutableChunks } from "./stream-files";
import { loadUseCases, useCaseInputFiles, useCaseSourceDeclaration, writeUseCaseSourceCopies, validateUseCaseHistory } from "./use-cases";
import {
  buildUseCaseArtifact,
  MAX_USE_CASE_BYTES,
  useCaseDeclaration,
  useCaseHash,
  type UseCaseInputs,
} from "../../shared/omics/use-cases";

import { loadResearchInputs, researchFiles, researchInputFiles } from "./research-release";
import { withResearchPins } from "./research-snapshot";
import { deriveResearchReadiness, validateResearchData, type ResearchData } from "../../shared/omics/research";
import { auditFiles, loadAudits } from "./audit/release";
import { benchmarkCoverage } from "./audit-benchmark-evidence";
import { legacyKinds } from "../../shared/omics/entity-kinds";
import { assertNoPrivateFields } from "../../shared/omics/private-fields";
import {
  createEvidenceIndex,
  evidenceJsonlLines,
} from "../../shared/omics/evidence-table";
import fs from "node:fs";
import { loadRecords, storeDigests } from "./records";
import path from "node:path";
import crypto from "node:crypto";
import { type OmicsProfile } from "../../lib/omics-profile";
import {
  validateRecords,
  publicRecords,
  kinds,
  type RecordEntry,
} from "./schema";
const sha = (s: string | Buffer) =>
  crypto.createHash("sha256").update(s).digest("hex");
export function buildRelease(
  input: RecordEntry[],
  releasedAt: string,
  extraCoverage: Record<string, unknown> = {},
  streamEvidence = false,
  useCases?: UseCaseInputs,
  useCaseSources?: Record<string, string>,
  research?: ResearchData,
) {
  // Records written with older relation names are released under the current ones.
  const records = currentRecords(input);
  // Release notes go in the receipt only. They do not enter the coverage or the release ID,
  // so a release whose records are unchanged is recognised as unchanged (next.mjs pending).
  const { changelog, ...coverageInputs } = extraCoverage;
  extraCoverage = coverageInputs;
  if (useCases) {
    validateUseCaseHistory(useCases);
    const declaration = useCaseDeclaration(useCases);
    if (extraCoverage.use_cases !== undefined &&
        useCaseHash(extraCoverage.use_cases) !== useCaseHash(declaration))
      throw Error("Use-case declaration does not match reviewed inputs");
    // Bind the logical input digest before deriving the release ID. Artifact
    // bytes then embed that ID and receive their own manifest file checksum.
    extraCoverage = { ...extraCoverage, use_cases: declaration };
  } else if (extraCoverage.use_cases !== undefined) {
    throw Error("Declared use cases require reviewed inputs");
  }
  if (useCaseSources) {
    if (!useCases) throw Error("Use-case sources require declared use cases");
    const declaration = useCaseSourceDeclaration(useCaseSources);
    if (extraCoverage.use_case_sources !== undefined &&
        useCaseHash(extraCoverage.use_case_sources) !== useCaseHash(declaration))
      throw Error("Use-case source declaration does not match reviewed bytes");
    extraCoverage = { ...extraCoverage, use_case_sources: declaration };
  } else if (extraCoverage.use_case_sources !== undefined) {
    throw Error("Declared use-case sources require reviewed bytes");
  }
  // Assessments belong to the new serving release, never copy a prior release's IDs.
  if (research) research = { schema_version: research.schema_version, manifests: research.manifests, investigations: research.investigations };
  validateRecords(records);
  const schemaVersion =
    extraCoverage.entity_schema_version === "1.1" ? "1.1" : "1.0";
  if (
    schemaVersion === "1.0" &&
    records.some(
      (record) => !(legacyKinds as readonly string[]).includes(record.kind),
    )
  )
    throw new Error(
      "Entity kinds introduced in 1.1 require schema version 1.1",
    );
  const releaseKinds = schemaVersion === "1.0" ? legacyKinds : kinds;
  const ordered = [...records].sort((a, b) => a.id.localeCompare(b.id));
  const all = ordered.map((r) => JSON.stringify(r)).join("\n") + "\n";
  const visible = publicRecords(ordered);
  validateRecords(visible);
  if (research) {
    validateResearchData(research, { schema_version: schemaVersion, release_id: "validation", released_at: releasedAt, records: visible, coverage: {} });
    extraCoverage = { ...extraCoverage, research_schema_version: "1.0" };
  }
  const releaseId =
    releasedAt.slice(0, 10) +
    "-" +
    sha(all + releasedAt + JSON.stringify(extraCoverage) + (research ? JSON.stringify(research) : "")).slice(0, 12);
  const counts = Object.fromEntries(
    releaseKinds.map((k) => [k, visible.filter((r) => r.kind === k).length]),
  );
  const coverage = {
    ...extraCoverage,
    total_records: ordered.length,
    public_records: visible.length,
    counts,
    quarantined_results: ordered.filter(
      (r) =>
        r.kind === "result" && ["needs_review", "disputed"].includes(r.status),
    ).length,
    scope_excluded_records: ordered.filter((r) => r.status === "excluded")
      .length,
    source_checked_results: visible.filter(
      (r) => r.kind === "result" && r.status === "source_checked",
    ).length,
    rewire_result_rows: visible.filter(
      (r) => r.kind === "result" && r.status === "reproduced",
    ).length,
    scope:
      "Specialist omics and molecular models; no clinical assistants or standalone medical imaging.",
    limitation:
      "A dated discovery and source-transcription review, not an exhaustive census or independent reproduction of external experiments.",
  };
  const snapshot = {
    schema_version: schemaVersion,
    release_id: releaseId,
    released_at: releasedAt,
    records: visible,
    coverage,
    ...(research ? { research } : {}),
  };
  if (snapshot.research) snapshot.research = { ...snapshot.research, readiness: deriveResearchReadiness(snapshot) };
  assertNoPrivateFields(snapshot);
  const files: Record<string, string> = {
    "catalogue.json": JSON.stringify(snapshot, null, 2) + "\n",
    "records.jsonl": visible.map((r) => JSON.stringify(r)).join("\n") + "\n",
    ...researchFiles(snapshot),
  };
  const streamedHashes: Record<string, string> = {};
  if (extraCoverage.evidence_table_version === "1.0" && streamEvidence) {
    const index = createEvidenceIndex(snapshot, { cache: false });
    const dir = path.join("public/omics/releases", releaseId);
    streamedHashes["evidence.jsonl"] = writeImmutableChunks(
      path.join(dir, "evidence.jsonl"),
      evidenceJsonlLines(index.iterate()),
    );
  } else if (extraCoverage.evidence_table_version === "1.0") {
    const evidence = createEvidenceIndex(snapshot).all();
    files["evidence.jsonl"] =
      evidence.map((row) => JSON.stringify(row)).join("\n") + "\n";
  }
  if (extraCoverage.audit_history)
    Object.assign(files, auditFiles(loadAudits(), releaseId).files);
  if (useCases) {
    const bytes = JSON.stringify(buildUseCaseArtifact(snapshot, useCases), null, 2) + "\n";
    if (Buffer.byteLength(bytes) > MAX_USE_CASE_BYTES)
      throw Error("Use-case artifact exceeds serving byte budget");
    files["use-cases.json"] = bytes;
  }
  if (useCaseSources) Object.assign(files, useCaseSources);
  const manifest = {
    schema_version: schemaVersion,
    release_id: releaseId,
    released_at: releasedAt,
    counts,
    coverage,
    archive_sha256: sha(all),
    catalogue_sha256: sha(files["catalogue.json"]),
    files: Object.fromEntries([
      ...Object.entries(files).flatMap(([name, data]) => [
        [name, sha(data)],
        ...(name === "records.jsonl" ? Object.entries(streamedHashes) : []),
      ]),
    ]),
    changelog: Array.isArray(changelog)
      ? changelog
      : [
          "Initial omics-only linked catalogue; original literature identifiers and scores retained.",
          "Only checked external numerical claims enter the catalogue; ambiguous values remain in the review queue.",
          "Existing MFASS v2 runs remain separate from external literature.",
        ],
    compatibility: {
      papers: "/benchmark-literature/papers.json",
      results: "/benchmark-literature/results.csv",
      note: "Historical compatibility files retain the original collection, including out-of-scope and unreviewed records. Use this release for current scoped data.",
    },
  };
  return { snapshot, manifest, files };
}
function writeArchive(output: ReturnType<typeof buildRelease>) {
  const dir = path.join("public/omics/releases", output.snapshot.release_id);
  fs.mkdirSync(dir, { recursive: true });
  const files = {
    ...output.files,
    "manifest.json": JSON.stringify(output.manifest, null, 2) + "\n",
  };
  for (const [name, data] of Object.entries(files)) {
    const file = path.join(dir, name);
    if (fs.existsSync(file)) {
      if (fs.readFileSync(file, "utf8") !== data)
        throw new Error("Attempt to overwrite immutable release " + file);
    } else fs.writeFileSync(file, data);
  }
}
function main() {
  const records = loadRecords();
  if (!records.length) throw new Error("No reviewed catalogue records");
  const research = withResearchPins(() => loadResearchInputs());
  const ledger = fs.existsSync("data/omics/search-ledger.jsonl")
    ? fs
        .readFileSync("data/omics/search-ledger.jsonl", "utf8")
        .trim()
        .split("\n")
        .filter(Boolean)
        .map((l) => JSON.parse(l))
    : [];
  const audit = JSON.parse(
    fs.readFileSync("data/omics/release-config.json", "utf8"),
  );
  const reviewedUseCases = loadUseCases(records);
  const profiles = records
    .filter((record) => record.attributes.profile)
    .map((record) => record.attributes.profile as OmicsProfile);
  const factStates = [
    "source_checked",
    "unreported",
    "unextracted",
    "unavailable",
    "inapplicable",
    "unclassified",
  ];
  const facts = profiles.flatMap((profile) => profile.facts);
  const benchmarkCounts = benchmarkCoverage(publicRecords(records));
  const output = buildRelease(
    records,
    audit.released_at,
    {
      // The September audit history stays in data/omics/audits; releases no longer republish it.
      entity_schema_version: "1.1",
      entity_migration: {
        baseline_release: "2026-09-17-5054ddf2a281",
        note: "Separate models, methods, configurations, pipelines, hosted services, benchmarks, tasks, protocols and evaluators. IDs, printed scores and archived releases remain unchanged.",
      },
      acquisition_review: {
        date: "2026-09-19",
        scope:
          "Nine benchmark result collections; PEtab timing data remains quarantined. Source cells checked independently; not experimental reproduction.",
      },
      run_instructions: {
        review: "Official source instructions; not executed by rewire",
        guides: records.filter((r) => r.attributes.run_guide).length,
        documentation_audits: records.filter(
          (r) => r.attributes.run_documentation,
        ).length,
      },
      run_recipe_coverage: {
        recipes: records.reduce(
          (total, record) =>
            total +
            (Array.isArray(record.attributes.run_recipes)
              ? record.attributes.run_recipes.length
              : 0),
          0,
        ),
        evaluations_with_verified_recipe_links: records.filter(
          (record) => record.attributes.reproduction,
        ).length,
        top_level_benchmarks: publicRecords(records).filter(
          (record) => record.kind === "benchmark",
        ).length,
        official_documentation_or_gap: publicRecords(records).filter(
          (record) =>
            record.kind === "benchmark" && record.attributes.run_documentation,
        ).length,
        note: "Source-reviewed instructions and exact applicability links; execution receipts do not establish reproduction of published scores. Production contributions remain disabled.",
      },
      // No bulk evidence.jsonl from 2026-10-11: it passed 2 GB, and record pages and the
      // serving database derive the same rows from the catalogue (#110).
      ...(research ? { research_generator_sha256: sha(["shared/omics/research.ts", "shared/omics/research-integrity.ts", "scripts/omics/research-release.ts"].map(file => fs.readFileSync(file, "utf8")).join("\n")) } : {}),
      // The rules that infer discrepancies between studies, so a rule change cuts a release
      // even when no record changed (docs/discrepancies.md).
      discrepancy_generator_sha256: sha(
        ["scripts/kg/contradictions.py", "data/ontology/discrepancy-rules.json"].map((file) => fs.readFileSync(file, "utf8")).join("\n"),
      ),
      evidence_table_generator_sha256: sha(
        [
          "shared/omics/evidence-table.ts",
          "shared/omics/run-recipe.ts",
          "shared/omics/profile-schema.ts",
          "shared/omics/private-fields.ts",
        ]
          .map((file) => fs.readFileSync(file, "utf8"))
          .join("\n"),
      ),
      ...(profiles.length
        ? {
            profile_coverage: {
              total: profiles.length,
              fact_status_counts: Object.fromEntries(
                factStates.map((state) => [
                  state,
                  facts.filter(
                    (fact) => (fact.status || "unclassified") === state,
                  ).length,
                ]),
              ),
              note: "Source review applies to individual cited claims. Missing fields and inaccessible evidence remain explicit; profile coverage is not independent experimental verification.",
              reviewed: profiles.filter(
                (profile) => profile.coverage === "reviewed",
              ).length,
              limited: profiles.filter(
                (profile) => profile.coverage === "limited",
              ).length,
            },
            benchmark_paper_review: {
              date: audit.released_at.slice(0, 10),
              top_level_benchmarks: benchmarkCounts.length,
              benchmark_pages_with_results: benchmarkCounts.filter(
                (row) => row.results > 0,
              ).length,
              benchmark_pages_with_figures: benchmarkCounts.filter(
                (row) => row.charts > 0,
              ).length,
              published_comparison_figures: benchmarkCounts.reduce(
                (sum, row) => sum + row.charts,
                0,
              ),
              source_checked_result_rows: records.filter(
                (r) => r.kind === "result" && r.status === "source_checked",
              ).length,
              scope:
                "Counts derived from this release through the production relationship and chart gates. Figures are source-specific, and metric rows are not independent experiments. Source review is not reproduction.",
            },
          }
        : {}),
      // Release notes: the merged pull requests since the previous release, written into the
      // release config by scripts/release/next.mjs prepare. They go in the receipt only.
      changelog: Array.isArray(audit.changelog) ? audit.changelog : [],
      research_lanes: 9,
      search_entries: ledger.length,
      legacy_papers: 100,
      legacy_result_rows: 149,
      // The store is listed as one file per kind (sharded kinds by their unsharded bytes), so
      // splitting a file into shards does not change the release.
      source_inputs: [
        ...storeDigests(),
        ...[
          ...useCaseInputFiles(),
          ...researchInputFiles.filter(file => fs.existsSync(file)),
          "data/omics/search-ledger.jsonl",
        ].map((file) => ({
          file,
          sha256: fs.existsSync(file) ? sha(fs.readFileSync(file)) : null,
        })),
      ],
    },
    true,
    reviewedUseCases?.inputs,
    reviewedUseCases?.sourceFiles,
    research,
  );
  // Enforce the live API contract before writing or building a new release.
  validateSnapshot(output.snapshot);
  writeArchive(output);
  if (reviewedUseCases) writeUseCaseSourceCopies(reviewedUseCases.sourceFiles);
  fs.writeFileSync(
    "public/omics/catalogue.json",
    output.files["catalogue.json"],
  );
  fs.writeFileSync(
    "public/omics/manifest.json",
    JSON.stringify(output.manifest, null, 2) + "\n",
  );
  fs.mkdirSync("public/omics/coverage", { recursive: true });
  fs.writeFileSync(
    `public/omics/coverage/${output.snapshot.release_id}.json`,
    JSON.stringify(benchmarkPageCoverage(output.snapshot), null, 2) + "\n",
  );
  writeBaselineAudit();
  console.log(
    `Omics ${output.snapshot.release_id}: ${output.snapshot.records.length} public records; ${output.manifest.coverage.source_checked_results} source-checked result rows; ${output.manifest.coverage.quarantined_results} in review.`,
  );
}
if (process.argv[1]?.endsWith("release.ts")) main();
