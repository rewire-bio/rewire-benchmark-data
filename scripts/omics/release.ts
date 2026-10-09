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
import { auditFiles, loadAudits, auditInputFiles } from "./audit/release";
import { benchmarkCoverage } from "./audit-benchmark-evidence";
import { legacyKinds } from "../../shared/omics/entity-kinds";
import { assertNoPrivateFields } from "../../shared/omics/private-fields";
import {
  createEvidenceIndex,
  evidenceCsv,
  evidenceCsvLines,
  evidenceJsonlLines,
} from "../../shared/omics/evidence-table";
import fs from "node:fs";
import { restoreReleaseBundles } from "./archives";
import { loadRecords, recordFiles, provenanceFile } from "./records";
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
  records: RecordEntry[],
  releasedAt: string,
  extraCoverage: Record<string, unknown> = {},
  streamEvidence = false,
  useCases?: UseCaseInputs,
  useCaseSources?: Record<string, string>,
  research?: ResearchData,
) {
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
  const quote = (v: unknown) => '"' + String(v ?? "").replace(/"/g, '""') + '"';
  const csv =
    [
      "id,kind,name,status,description,facets,source_ids,links,attributes",
      ...visible.map((r) =>
        [
          r.id,
          r.kind,
          r.name,
          r.status,
          r.description,
          JSON.stringify(r.facets),
          JSON.stringify(r.source_ids),
          JSON.stringify(r.links),
          JSON.stringify(r.attributes),
        ]
          .map(quote)
          .join(","),
      ),
    ].join("\n") + "\n";
  const files: Record<string, string> = {
    "catalogue.json": JSON.stringify(snapshot, null, 2) + "\n",
    "records.jsonl": visible.map((r) => JSON.stringify(r)).join("\n") + "\n",
    "records.csv": csv,
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
    streamedHashes["evidence.csv"] = writeImmutableChunks(
      path.join(dir, "evidence.csv"),
      evidenceCsvLines(index.iterate()),
    );
  } else if (extraCoverage.evidence_table_version === "1.0") {
    const evidence = createEvidenceIndex(snapshot).all();
    files["evidence.jsonl"] =
      evidence.map((row) => JSON.stringify(row)).join("\n") + "\n";
    files["evidence.csv"] = evidenceCsv(evidence);
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
        ...(name === "records.csv" ? Object.entries(streamedHashes) : []),
      ]),
    ]),
    changelog: Array.isArray(extraCoverage.changelog)
      ? extraCoverage.changelog
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
  // Restore the frozen release first, so rebuilding it fails on any changed byte.
  restoreReleaseBundles();
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
  const reviewedUseCases = loadUseCases();
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
      ...(auditInputFiles().some((f) => f.endsWith(".run.json"))
        ? { audit_history: auditFiles(loadAudits()).coverage }
        : {}),
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
      evidence_table_version: "1.0",
      ...(research ? { research_generator_sha256: sha(["shared/omics/research.ts", "shared/omics/research-integrity.ts", "scripts/omics/research-release.ts"].map(file => fs.readFileSync(file, "utf8")).join("\n")) } : {}),
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
            changelog: [
              "Audit all 17 use cases; add source-reviewed, protocol-specific literature measurements and conventional baselines, with explicit remaining decision and transfer gaps. Automated source review is not independent experimental reproduction or human scientific review.",
              ...(reviewedUseCases ? ["Add two sourced research use cases linking questions to exact existing evaluations, with separate MFASS and AMFR protocol scopes, explicit clinical evidence gaps and an independently versioned, release-pinned use-case artifact. Add two documentation source records; preserve every prior scientific record and numerical result."] : []),
              "Add four MFASS matched canonical-annotation configurations and 16 exact metric rows on the identical 8,297/8,324 scored subset; retain 23 assembly-orientation exclusions and four canonical transcript-scope exclusions, with pinned automated evidence and separate comparison panels.",
              "Add complete bounded primary-source result tables for BEELINE, CAFA, CAMI, CAPRI, CASP, FLIP2, PLINDER, scIB and provisional Virtual Cell Challenge 2026 validation.",
              "Preserve PEtab timing candidates and four conflicting FLIP2 values in acquisition staging with explicit limitations.",
              "Add append-only linked audit runs, field checks, source retrieval receipts and correction history; unresolved fields remain explicit.",
              "Recover 16 omitted ProteinBench percentage results and correct percent units; original printed and numeric values remain unchanged.",
              "Correct DART-Eval correlation units and remove unsupported standard-deviation labels from TDC printed plus/minus spreads.",
              "Recheck pinned extraction inputs, reject unrecognised cells and authenticate PDF-to-text transformations.",
              "Add complete AgroNT promoter and terminator source tables with CNN baselines, source-backed family links and separate assay comparisons.",
              "Link verified model identities and expose downstream evaluations separately; add 1,620 source-checked numerical rows from 13 bounded primary-source comparisons. Preserve quoted evidence and quarantine conflicting mRNABench localization cells.",
              "Count reviewed metrics from the same source evaluation setup together, retaining all original record IDs and links.",
              "Load individual source-scoped charts, remove cross-protocol pooled rankings, and move findings before detailed instructions.",
              "Review 69 selected profile facts across 18 profiles against pinned primary sources, including exact configuration, split, coverage and uncertainty distinctions. Preserve every result value and keep unresolved metadata explicit.",
              "Add two bounded ProteinGym protocol profiles with 24 sourced facts, distinguishing the 217-assay track from one complete AMFR assay. Preserve numerical results, source-authentication gaps and independent-reproduction limits.",
              "Name nine evaluated methods printed only as an author-year citation (eight ATOM3D comparisons) or an author surname (HEST, Ciga), from the benchmark text and the cited original sources. The ATOM3D RSR scorer is named only as a Rosetta scoring function; its citation conflict and settings stay unresolved. Printed labels remain searchable and auditable; IDs, values, locators and comparison conditions are unchanged. Add sourced DeepDTA and DeepAffinity method profiles.",
              "Preserve archived release bytes, historical URLs and MFASS history. Contribution intake remains controlled separately from catalogue publication.",
              ...(research ? ["Add verified research manifests, frozen readiness assessments and reviewed-only investigation contracts. Record IDs and values remain unchanged."] : []),
              "Add a second, additive BRCA1/BRCA2 germline-interpretation evidence intake (issue #343): 42 new source-checked clinical-lane records from five sources (Benet-Pages 2025, So 2024, HECTOR preprint, Hu 2026, Karalidou 2022/MARGINAL source-only), distinguishing reclassification rate, tool agreement, preprint classification concordance and functional-data classification yield from clinical accuracy. Add five new scoped proxy use-case mappings against these records: two for Benet-Pages criteria-version reclassification on a fixed VUS cohort (ACMG/AMP+SVI, then ENIGMA VCEP), one for So 2024 VarSome-vs-CanVIG-UK tool agreement on conflicting BRCA1 missense calls, one for HECTOR preprint agreement with ClinGen eRepo expert calls, and one for Hu 2026 BRCA2 exon 15-26 functional-data classification yield; Karalidou 2022 remains source-only with no mapping added. None of these endpoints establishes clinical accuracy, qualified human scientific review or Rewire execution. All prior scientific records, mapping objects and historic release bytes remain unchanged.",
              "Add a bounded, additive cell-type-annotation-transfer evidence intake (issue #349): Abdelaal et al. 2019 Figure S10 Panel B (34-population inter-dataset, cross-dataset/cross-species-where-applicable brain annotation-transfer comparison), SVMrejection row only (9 percent-unlabeled values across all nine VISp/ALM/MTG train-test combinations; VISp and ALM share a source study, GSE115746, so only the 7 of 9 combinations involving MTG are genuinely cross-study and cross-species), read directly from a page-image render of a separately-sourced supplement-PDF artifact and independently cross-checked before ingestion. Reuses the existing SVMrejection method/configuration records unmodified; adds one new source record, three new dataset records, one new protocol record, nine new evaluation records and nine new result records, plus one new scoped proxy use-case mapping. Scored denominator is explicitly unreported; Table 2's raw per-dataset cell counts are recorded as context only, not a confirmed denominator. Not a known-type accuracy claim, not an unknown-type-detection accuracy claim, and not a superiority claim across methods. All prior scientific records, mapping objects and historic release bytes remain unchanged.",
              "Add a bounded, additive EGFR-NSCLC evidence-retrieval proxy intake (B345/BL345, rewire-benchmarks #25 and #28; use-case-egfr-nsclc-actionability-resistance-evidence): CIViC-Fact v3's post-cutoff within-linked-publication passage-retrieval evaluation (150 candidate CIViC entries submitted/revised 2026-03-03 to 2026-06-09, reduced by sequential source-defined exclusions to 40 scored entries). Nine new clinical-lane records (one source, one dataset, one protocol, two configurations, two evaluations, two results) and one new scoped proxy use-case mapping, alongside the unchanged existing CIViC MCP proxy mapping for the same use case. Both retriever configurations (a fine-tuned MedCPT cross-encoder and a pretrained Qwen3-Reranker-8B) report two linked-paper passage-retrieval results of 37/40 (92.5%) appropriate-content rate on the identical cohort, not two independent cohorts. This is retrieval within each entry's already-identified source publication, not open-corpus literature search, and establishes no EGFR- or NSCLC-specific validation, no clinical efficacy claim, and no close of the benchmark-execution gap tracked separately at rewire-benchmarks #28. Reviewer count, blinding and replicate/seed structure for the manual retrieval judgment are unreported. The code/data repository's root licence metadata is null with no root LICENSE file, but a nested data_builder/LICENSE (GPLv3) exists at a pinned commit; its scope over the dataset/model/experiment components is unestablished and not assumed, and no code/data/model copies were ingested. All prior scientific records, mapping objects, use cases and historic release bytes remain unchanged.",
              "Add a bounded, additive genetic-perturbation-response evidence intake (B334/BL334, rewire-benchmarks #25; focused execution gap rewire-benchmarks #29; use-case-genetic-perturbation-response): PertEval-scFM (Wenteler et al., ICML 2025) Table 1, Norman single-gene section, 2,000 HVGs, three printed AUSPC endpoints (GEARS trained from scratch 0.815+/-0.039, an Xc-plus-co-expression MLP baseline 4.484+/-0.299, a context-mean baseline 4.612+/-0.317, all x10^-2), scoring the perturbation-effect delta=P-Xc rather than raw post-perturbation expression. Twelve new experimental-lane records (one source, one dataset, one protocol, three configurations, three evaluations, three results) and one new scoped proxy use-case mapping, alongside the two unchanged existing GEARS Supplementary Table 6 mappings for the same use case. This is a second, independent, from-scratch GEARS evaluation on a differently-preprocessed dataset, split mechanism and metric from Table 6; the two are not merged. Establishes no prospective experiment-selection hit rate and does not close the focused execution gap tracked separately at rewire-benchmarks #29. All prior scientific records, mapping objects, use cases and historic release bytes remain unchanged.",
              "Add a bounded, additive AMP evidence intake (rewire.it#365; rewire-benchmark-data issues #10-19): nine new use-case definitions (tumour-dna-somatic-variant-detection, tumour-rna-fusion-detection, patient-rna-splicing-validation, diagnostic-dna-pathogen-identification, diagnostic-rna-pathogen-detection, plasma-ctdna-fragmentomics, plasma-ctdna-methylation, cnv-detection-characterisation, diagnostic-genomics-model-execution), transcribed from three research groups' Codex-checked primary-source candidate dossiers (Lancet/Strelka2 virtual-tumour SNV/indel calling; EnFusion Seraseq synthetic reference standard plus a separate NCH clinical-ascertainment mapping; FRASER known pathogenic splicing-event recovery; Karius plasma microbial cfDNA; UCSF respiratory RNA mNGS; DELFI ctDNA fragmentomics; cfMethyl-Seq ctDNA methylation; DRAGEN 4.2 CNV and runtime baselines), plus a bounded Feng et al. 2025 DNA-foundation-model table expansion (Table 1 Acceptor and Donor as two separate tasks, Table 2 Arabidopsis TATA and NonTATA as two separate tasks, Table 5 pathogenic-versus-common SNP AUC/Cohen's d, Table 6 eQTL/sQTL/paQTL/ipaQTL as four separate tasks, 79 task-scoped evaluations and 138 results total) reusing the existing evidence-expansion-dna-foundation-models-2025-5d8ca9bc source unchanged, mapped as nine proxy mappings onto existing use cases (two each for splicing-follow-up and plant-promoter-reporters, one for rare-disease-candidate-ranking, four for regulatory-variant-gene-follow-up). Every preserved source conflict (Lancet/Strelka2 truth-indel counts, EnFusion Table 2 v2/v3 caption and 43.6%/43.8% precision conflicts, DELFI classifier-input wording, UCSF composite-PPA conflict, DRAGEN CNV comparator conflict) stays explicit and unresolved by inference. Automated source review, independently Codex-checked across two review cycles; no qualified human scientific review, no independent experimental reproduction, no broad clinical validation claimed. The 17 prior use cases and 72 prior mapping objects remain byte-identical.",
            ],
          }
        : {}),
      research_lanes: 9,
      search_entries: ledger.length,
      legacy_papers: 100,
      legacy_result_rows: 149,
      source_inputs: [
        ...recordFiles(),
        provenanceFile,
        ...auditInputFiles(),
        ...useCaseInputFiles(),
        ...researchInputFiles.filter(file => fs.existsSync(file)),
        "data/omics/search-ledger.jsonl",
      ].map((file) => ({
        file,
        sha256: fs.existsSync(file) ? sha(fs.readFileSync(file)) : null,
      })),
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
