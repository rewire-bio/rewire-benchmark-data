#!/usr/bin/env python3
"""Generate the nine new AMP use-case definitions and all nineteen new
mapping objects (dict form), for appending into data/omics/use-cases/
inputs.json. Reads the mapping drafts already produced by
build-amp-coverage.py.

Evidence_sha256 values are left as a 64-character placeholder of zeros here;
a second pass (scripts/omics/fix-amp-mapping-hashes.ts) computes the real
mappingEvidenceHash against a built candidate snapshot and patches them in,
per integration-plan.md ("this hash can only be computed once the referenced
catalogue records exist in a built snapshot").
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/omics/use-case-coverage-amp-20261007"
PLACEHOLDER_HASH = "0" * 64
# Fixed, explicit review completion time -- see build-amp-coverage.py for why
# this is not datetime.now(). Keep these two constants in sync.
REVIEWED_AT = os.environ.get("AMP_REVIEW_AT", "2026-10-07T13:38:59Z")
REVIEWER_ACTOR = "Claude Sonnet AMP-integration worker, bounded transcription of Codex-checked primary values; independently reviewed by Codex (workbench/amp-supervision/primary-review.md, integration-review-corrections.md)"

mappings_draft = json.loads((OUT / "mappings-draft.json").read_text())


def review():
    return {"method": "automated_source_review", "actor": REVIEWER_ACTOR, "reviewed_at": REVIEWED_AT,
            "note": "Bounded primary-source transcription, independently Codex-checked. No new model execution, independent experimental reproduction, qualified human scientific review or clinical validation."}


def mapping_record(draft):
    return {
        "id": draft["id"], "use_case_id": draft["use_case_id"],
        "lifecycle": "active", "revision": 1,
        "reason": "Add Codex-checked primary-source protocol evidence from the bounded AMP intake (rewire.it#365).",
        "protocol_id": draft["protocol_id"],
        "evaluation_ids": draft["evaluation_ids"],
        "endpoint": draft["endpoint"],
        "relevance": draft["relevance"],
        "rationale": draft["rationale"],
        "constraints": [
            "Inspect every linked evaluation's source locator and preserved conflicts before citing a result.",
            "Do not combine this mapping's evaluations with any other protocol's results.",
        ],
        "limitations": draft["case_limitations"] or ["No independent reproduction or qualified human scientific review."],
        "citations": [{"source_id": sid, "locator": "See clinical/claims.csv and clinical/sources.md in data/omics/use-case-coverage-amp-20261007/"}
                      for sid in sorted(set(_mapping_source_ids(draft)))],
        "review": review(),
        "evidence_sha256": PLACEHOLDER_HASH,
    }


def _mapping_source_ids(draft):
    # one representative source id per mapping, derived from its id prefix
    table = {
        "use-case-mapping-amp-20261007-issue10-lancet-virtual-tumor": ["amp-oncology-rna-20261007-source-pmc6123722"],
        "use-case-mapping-amp-20261007-issue11-enfusion-seraseq": ["amp-oncology-rna-20261007-source-pmc8642973"],
        "use-case-mapping-amp-20261007-issue11-enfusion-nch-clinical": ["amp-oncology-rna-20261007-source-pmc8642973"],
        "use-case-mapping-amp-20261007-issue12-fraser-kremer": ["amp-oncology-rna-20261007-source-pmc7822922"],
        "use-case-mapping-amp-20261007-issue13": ["amp-20261007-dna-pathogens-source"],
        "use-case-mapping-amp-20261007-issue14": ["amp-20261007-rna-pathogens-source"],
        "use-case-mapping-amp-20261007-issue15": ["amp-20261007-ctdna-fragmentomics-source"],
        "use-case-mapping-amp-20261007-issue16": ["amp-source-cfmethyl", "amp-source-cfmethyl-correction"],
        "use-case-mapping-amp-20261007-issue17": ["amp-source-dragen", "amp-source-dragen-supplementary-tables"],
        "use-case-mapping-amp-20261007-issue18": ["amp-source-dragen", "amp-source-dragen-supplementary-tables"],
        "use-case-mapping-amp-20261007-feng-splice-acceptor": ["evidence-expansion-dna-foundation-models-2025-5d8ca9bc"],
        "use-case-mapping-amp-20261007-feng-splice-donor": ["evidence-expansion-dna-foundation-models-2025-5d8ca9bc"],
        "use-case-mapping-amp-20261007-feng-promoter-tata": ["evidence-expansion-dna-foundation-models-2025-5d8ca9bc"],
        "use-case-mapping-amp-20261007-feng-promoter-nontata": ["evidence-expansion-dna-foundation-models-2025-5d8ca9bc"],
        "use-case-mapping-amp-20261007-feng-pathogenic-common-variant": ["evidence-expansion-dna-foundation-models-2025-5d8ca9bc"],
        "use-case-mapping-amp-20261007-feng-qtl-eqtl": ["evidence-expansion-dna-foundation-models-2025-5d8ca9bc"],
        "use-case-mapping-amp-20261007-feng-qtl-sqtl": ["evidence-expansion-dna-foundation-models-2025-5d8ca9bc"],
        "use-case-mapping-amp-20261007-feng-qtl-paqtl": ["evidence-expansion-dna-foundation-models-2025-5d8ca9bc"],
        "use-case-mapping-amp-20261007-feng-qtl-ipaqtl": ["evidence-expansion-dna-foundation-models-2025-5d8ca9bc"],
    }
    return table[draft["id"]]


def use_case(id_, slug, title, question, decision, inputs_, output, setting, exclusions,
             clinical_scope, evidence_gaps, citation_source_ids, issue_number, next_step):
    return {
        "id": id_, "slug": slug, "title": title, "question": question,
        "area": "dna-genomes", "contexts": ["clinical_research"],
        "search_terms": [slug.replace("-", " ")],
        "intended_users": [
            "Clinical researchers scoping the available diagnostic-genomics evidence",
            "Computational researchers comparing exact evaluated configurations",
        ],
        "decision": decision, "inputs": inputs_, "output": output, "setting": setting,
        "exclusions": exclusions, "clinical_scope": clinical_scope, "evidence_gaps": evidence_gaps,
        "citations": [{"source_id": sid, "locator": "See data/omics/use-case-coverage-amp-20261007/clinical/sources.md"} for sid in citation_source_ids],
        "review": review(),
        "collection_plan": {
            "status": "collecting",
            "comparison_question": question,
            "baselines": ["The conventional/author-introduced workflow measured in the linked primary source(s)."],
            "outcomes": ["The declared endpoint in this use case's active mapping(s); see evidence_gaps for what remains open."],
            "validation_requirements": ["Independent held-out population matched to the intended clinical setting.", "Qualified human scientific review before any clinical-validation claim."],
            "next_step": next_step,
        },
        "planned_work": [{
            "title": f"Focused benchmark/run task for rewire-benchmark-data issue #{issue_number}",
            "url": f"https://github.com/rewire-bio/rewire-benchmark-data/issues/{issue_number}",
            "status": "planned",
            "reason": "Reviewed literature evidence is bounded (see evidence_gaps); closing the remaining decision gap needs a dedicated protocol/run task with frozen population and matched controls, tracked in rewire-benchmarks.",
        }],
    }


USE_CASES = [
    use_case(
        "use-case-tumour-dna-somatic-variant-detection", "tumour-dna-somatic-variant-detection",
        "Select a tumour DNA somatic variant-calling workflow",
        "Which calling or rescoring workflow reliably detects tumour SNVs and small indels under the available sequencing and normal-sample regime?",
        "Inspect the matched virtual-tumour precision/recall evidence for Lancet and Strelka2 before selecting a caller and designing a validation protocol for the intended sequencing/normal regime.",
        ["Tumour and matched-normal aligned sequencing reads", "The intended variant-fraction, coverage and genomic-context strata"],
        "A sourced set of exact evaluated caller precision/recall/F1 values and remaining validation needs; no patient-level variant classification or clinical recommendation.",
        "A real-read virtual-tumour spike-in (NA12892/NA12891 HapMap samples, 80x/40x WGS) measures SNV and indel precision/recall/F1 for the Lancet caller and the Strelka2 comparator.",
        ["Real clinical tumour specimens, FFPE samples, targeted panels, ctDNA, copy-number and structural variation", "Callers other than Lancet/Strelka2 not transcribed in this bounded intake (Strelka, MuTect, MuTect2, LoFreq rows exist in the source but are not all ingested; LoFreq/MuTect2 unselected rows are internally inconsistent in the source and are excluded)"],
        "Clinical applicability is not established. A synthetic virtual-tumour spike-in does not demonstrate sensitivity in real clinical tumours, FFPE specimens, gene panels, ctDNA, or for copy-number/structural variants.",
        ["Individual-condition confidence intervals are unreported in the source tables.", "Exact caller release versions are not extracted from the primary article.", "No foundation-model component is evaluated in this bounded intake."],
        ["amp-oncology-rna-20261007-source-pmc6123722"], 10,
        "A dedicated rewire-benchmarks protocol/run task with a real clinical tumour cohort, pinned truth set, purity/platform/assembly strata and an explicit foundation-model eligibility check.",
    ),
    use_case(
        "use-case-tumour-rna-fusion-detection", "tumour-rna-fusion-detection",
        "Select a tumour RNA fusion-detection workflow",
        "Which RNA-sequencing workflow detects and prioritises tumour gene fusions with useful sensitivity and a manageable false-positive review burden?",
        "Inspect the matched synthetic Seraseq reference-standard and NCH clinical-ascertainment evidence for Arriba, STAR-Fusion and the EnFusion ensemble before selecting a workflow and review burden for the intended specimen type.",
        ["Paired-end tumour RNA-seq reads", "The intended specimen type (frozen, FFPE or other) and acceptable false-positive review burden"],
        "A sourced set of exact evaluated sensitivity/precision values on a synthetic reference standard and a real clinical cohort, with the ascertainment-bias caveat explicit; no patient-level fusion classification.",
        "A 14-fusion synthetic Seraseq reference standard (undiluted, duplicate libraries) and a 229-sample paediatric cancer/haematologic cohort (67 ensemble-ascertained clinically relevant fusions) measure fusion-calling sensitivity and precision for Arriba, STAR-Fusion and the EnFusion ensemble (with/without filtering and a known-fusion list).",
        ["Novel-fusion discovery performance (the optimised known-fusion rescue measures recovery of 14 known synthetic fusions, not novel-fusion discovery)", "Adult solid-tumour cohorts outside the transcribed NCH cohort", "Non-Seraseq background fusions, all counted false positive in this intake though some may be real endogenous fusions"],
        "Clinical applicability is bounded: the NCH clinical-cohort sensitivity figures are ascertained against the optimised EnFusion ensemble's own calls, not an independent exhaustive truth set, so a false-negative rate for fusions the ensemble itself missed cannot be derived from this evidence.",
        ["Table 2 caption (v3) vs the optimisation narrative (v2) is an unresolved source version conflict.", "STAR-Fusion precision is printed as both 43.6% (Table 2) and 43.8% (paragraph) in the source; both are preserved, neither is silently reconciled.", "No confidence interval or dispersion is printed for the Seraseq Table 2 rows."],
        ["amp-oncology-rna-20261007-source-pmc8642973"], 11,
        "A dedicated rewire-benchmarks protocol/run task with an independent fusion truth set not ascertained by the same ensemble being evaluated.",
    ),
    use_case(
        "use-case-patient-rna-splicing-validation", "patient-rna-splicing-validation",
        "Select a patient-RNA splicing-variant validation workflow",
        "Which DNA/RNA evidence workflow identifies splice-altering variants for inherited-disorder follow-up when patient RNA and tissue-specific context are available?",
        "Inspect the FRASER known pathogenic-event recovery curve and the sequence-classification proxy evidence before selecting a workflow and designing patient-RNA follow-up for the intended cohort size.",
        ["Patient skin-fibroblast (or matched tissue) RNA-seq aligned reads", "The number of samples available for a FRASER-style aberrant-splicing cohort"],
        "A sourced recovery curve (fraction of known pathogenic splicing events recovered as cohort size grows) and a separate sequence-classification proxy; no diagnostic-yield claim for unknown cases.",
        "FRASER, applied to a retrospective Kremer rare-mitochondrial-disorder skin-fibroblast RNA cohort (119 samples/105 individuals, 13 known pathogenic splicing events), recovers a mean 85% (11 of 13) of known events at a reduced 30-sample subsample. A separate, proxy sequence-classification AUC for DNA foundation-model embeddings (Feng et al. 2025, Table 1 Acceptor/Donor) is also linked, scoped as a different endpoint.",
        ["Diagnostic yield in patients without a known pathogenic event (this is recovery of already-known events, not discovery)", "Full-cohort outlier-gene workload counts (12/7/10 genes/sample), a different population from the 30-sample recovery evaluation and not ingested here", "Blinded pathogenicity adjudication or VUS reclassification"],
        "Clinical applicability is not established beyond known-event recovery. This does not demonstrate prospective diagnostic yield, blinded adjudication, or general tissue transfer.",
        ["No numeric confidence interval is reported for the 85% recovery figure in the inspected main text.", "Subsampling repeat count and exact score-aggregation method are unextracted.", "The sequence-classification proxy mapping (Feng Table 1) measures AUC on a different population (DNABERT-2/NT benchmark splice-site datasets), not minigene reporter exon inclusion or patient RNA, and must not be pooled with the FRASER recovery figure."],
        ["amp-oncology-rna-20261007-source-pmc7822922"], 12,
        "A dedicated rewire-benchmarks protocol/run task with a prospective, blinded patient-RNA cohort including cases without a pre-known pathogenic event.",
    ),
    use_case(
        "use-case-diagnostic-dna-pathogen-identification", "diagnostic-dna-pathogen-identification",
        "Select a DNA pathogen-identification workflow for diagnostic testing",
        "Which DNA sequencing classification workflow detects clinically relevant pathogens and handles contamination or organisms absent from the reference?",
        "Inspect the Karius plasma microbial cfDNA positive-percent-agreement evidence against initial blood culture before selecting a workflow and reference standard for the intended specimen population.",
        ["Plasma microbial cell-free DNA sequencing reads", "The reference standard available for agreement/sensitivity comparison (e.g. blood culture, composite adjudication)"],
        "A sourced positive-percent-agreement figure against one reference standard, with the reference standard's own detection limits explicit; no general sensitivity claim against all true infections.",
        "The Karius 2019 plasma microbial cfDNA sequencing assay achieves 93.7% (59 of 63) positive percent agreement with initial blood culture in a prospective 350-patient sepsis-alert cohort (348 paired results).",
        ["Sensitivity against a composite/adjudicated reference standard (a separate, excluded endpoint in the source due to a printed CI conflict)", "RNA viral pathogen detection (this is a DNA-only assay)"],
        "Clinical applicability is bounded to agreement with initial blood culture, a reference standard that does not identify every true infection; this is not an estimate of sensitivity against all infections in the cohort.",
        ["The composite-reference negative-percent-agreement CI is internally conflicting in the source (54.8-70.0 vs 55.2-70.4) and is excluded from this intake.", "The exact executable/database version is not pinned in the inspected primary text.", "The primary article's public redistribution licence is absent; only a compact factual table excerpt is archived."],
        ["amp-20261007-dna-pathogens-source"], 13,
        "A dedicated rewire-benchmarks protocol/run task with a prospectively adjudicated composite reference standard, not solely initial blood culture.",
    ),
    use_case(
        "use-case-diagnostic-rna-pathogen-detection", "diagnostic-rna-pathogen-detection",
        "Select an RNA pathogen-detection workflow for diagnostic testing",
        "Which RNA sequencing workflow detects RNA pathogens reliably in the intended specimen and distinguishes real detections from host/background contamination?",
        "Inspect the UCSF respiratory RNA mNGS sensitivity-against-original-testing evidence before selecting a workflow and specimen-prep protocol for the intended respiratory-target population.",
        ["Respiratory specimen RNA (DNase-treated), reverse-transcribed to cDNA libraries", "The original clinical reference assay(s) available for sensitivity comparison"],
        "A sourced sensitivity-against-original-clinical-testing figure for one respiratory mNGS assay; no general RNA-virus-only diagnostic accuracy claim.",
        "A UCSF respiratory RNA metagenomic next-generation sequencing (mNGS) assay (RNA extraction, DNase treatment, cDNA synthesis; SURPI+ pipeline) achieves 93.6% (103 of 110) sensitivity against original clinical respiratory-virus-panel testing in a residual pre-DTCA mixed respiratory-target cohort (adenovirus transcripts included via transcription).",
        ["A composite-PPA figure (98.7%, 110.5/113) that conflicts with the source's own printed numbers and is excluded from this intake", "Non-respiratory specimen types"],
        "Clinical applicability is bounded to agreement with the original clinical panel on one residual-sample cohort; this is not a mixed DNA/RNA sample-prep comparison and not an RNA-virus-only subgroup score, and is not validated prospectively.",
        ["A positive-specimen BAL/swab count disagreement between the source's Results and Methods sections (104+6 vs 103+7) is unresolved and preserved.", "No confidence interval is extracted for this sensitivity figure in the inspected text."],
        ["amp-20261007-rna-pathogens-source"], 14,
        "A dedicated rewire-benchmarks protocol/run task with a prospective RNA-pathogen cohort and an adjudicated composite reference standard.",
    ),
    use_case(
        "use-case-plasma-ctdna-fragmentomics", "plasma-ctdna-fragmentomics",
        "Select a plasma ctDNA fragmentomics detection workflow",
        "Which fragmentomics workflow detects tumour-derived plasma DNA under realistic low tumour fractions and fixed false-positive constraints?",
        "Inspect the DELFI repeated-cross-validation sensitivity-at-fixed-specificity evidence before selecting a workflow and validation design for the intended screening or diagnostic population.",
        ["Plasma cell-free DNA whole-genome sequencing reads", "The target specificity (false-positive) constraint for the intended use"],
        "A sourced sensitivity figure at one reported specificity, from internal cross-validation; no prospective screening-validation claim.",
        "The DELFI stochastic gradient boosting classifier (GC-corrected total and short fragment coverage across 504 genomic bins, 39 arm Z-scores, mitochondrial representation) achieves 73% (152 of 208) sensitivity at a reported 98% specificity, under repeated 10-fold cross-validation (10 repeats) across 208 cancer patients (seven cancer types) and 215 healthy individuals.",
        ["A combined mutation+DELFI configuration (115/126, 91%), a different subset/configuration not ingested here", "Tumour-fraction-stratified sensitivity (unreported for this endpoint)"],
        "Clinical applicability is not established as prospective screening performance: this is internal repeated cross-validation on one assembled cohort, not a separately held-out validation cohort or a prospective screening trial, and the cohort's clinically identified cancers/healthy comparators differ from an intended screening population.",
        ["4 of 215 healthy individuals were misclassified at the source-labelled 98% specificity; the printed specificity is retained rather than recomputed.", "cfDNA signal reflects total circulating DNA, not purified ctDNA; tumour-fraction limits are unreported for this endpoint."],
        ["amp-20261007-ctdna-fragmentomics-source"], 15,
        "A dedicated rewire-benchmarks protocol/run task with an independent, prospectively collected held-out validation cohort.",
    ),
    use_case(
        "use-case-plasma-ctdna-methylation", "plasma-ctdna-methylation",
        "Select a plasma ctDNA methylation detection workflow",
        "Which measured methylation workflow detects tumour-derived plasma DNA and, where separately supported, identifies tissue of origin?",
        "Inspect the cfMethyl-Seq repeated-split sensitivity/specificity evidence before selecting a workflow and validation design for the intended cancer-detection population.",
        ["Plasma cell-free DNA for targeted/genome-wide methylation sequencing", "The target specificity constraint for the intended use"],
        "A sourced all-stage cancer-detection sensitivity/specificity figure from a repeated random test split; no tissue-of-origin claim is ingested in this bounded intake.",
        "cfMethyl-Seq achieves 80.7% all-stage cancer-detection sensitivity (95% CI 68.6-90.7) at 97.9% specificity, under a repeated random 25% test split (cohort 217 cancers/191 non-cancers, test n=102).",
        ["Tissue-of-origin identification (not ingested in this bounded intake)", "Prospective screening validation"],
        "Clinical applicability is not established as prospective screening performance: this is a repeated random test-split evaluation on one assembled cohort, not an independent prospective validation.",
        ["No per-run scored denominator beyond the printed test n=102 is inferred.", "A correction/source-reuse note on this source is tracked separately from the assay sensitivity/specificity values and must not be conflated with them."],
        ["amp-source-cfmethyl", "amp-source-cfmethyl-correction"], 16,
        "A dedicated rewire-benchmarks protocol/run task with an independent prospective cohort and an explicit tissue-of-origin evaluation if pursued.",
    ),
    use_case(
        "use-case-cnv-detection-characterisation", "cnv-detection-characterisation",
        "Select a copy-number variant detection and characterisation workflow",
        "Which workflow detects and characterises copy-number changes accurately and helps an analyst assess the evidence?",
        "Inspect the DRAGEN 4.2 CNV/SV benchmarking F-score evidence for 1-5 kb deletions before selecting a workflow; evidence-visualisation usability is not addressed by this bounded intake.",
        ["Whole-genome sequencing aligned reads", "The size range and variant class (deletion, duplication, etc.) of clinical interest"],
        "A sourced F-score for one size-stratified deletion class against a truth set; no visualisation-usability or clinical-reporting claim.",
        "DRAGEN 4.2's CNV/SV benchmarking (HG002, GIAB SV truth set) reports an F-score for 1-5 kb deletion detection (selected Table S4 cells, sheet CNVbenchmarking, H6=.926, L6=.391).",
        ["Duplications, larger/smaller size strata, and tumour CNV (not ingested in this bounded intake)", "Evidence-visualisation usability for an analyst (not measured by this F-score endpoint)"],
        "Clinical applicability is not established beyond this one size-stratified deletion F-score; a conflicting comparator figure (.391 vs 39.20% in source table/prose) is preserved unresolved and not promoted.",
        ["Unreported per-bin counts behind the printed F-score.", "No duplication, tumour-CNV or clinical-reporting endpoint is ingested in this bounded intake.", "No foundation-model applicability is established for this task."],
        ["amp-source-dragen", "amp-source-dragen-supplementary-tables"], 17,
        "A dedicated rewire-benchmarks protocol/run task covering duplications and tumour CNV, plus an analyst-facing visualisation-usability evaluation.",
    ),
    use_case(
        "use-case-diagnostic-genomics-model-execution", "diagnostic-genomics-model-execution",
        "Select an execution workflow for large-scale diagnostic genomics",
        "Which eligible model configuration and execution workflow can meet a diagnostic genomics team's resource, throughput and reproducibility constraints?",
        "Inspect the DRAGEN 4.2 single-sample runtime baseline before scoping a foundation-model execution workflow's resource/throughput budget; this conventional baseline is a proxy, not a model-execution benchmark.",
        ["The diagnostic genomics team's available hardware configuration", "The required per-sample turnaround and batch throughput"],
        "A sourced single-sample total runtime baseline on two hardware configurations; no foundation-model execution benchmark is ingested in this bounded intake.",
        "DRAGEN 4.2 Phase 4 total single-sample wall-clock runtime for HG002 is 1,838.5 seconds on one hardware configuration and 5,521.21 seconds on an AWS HG002 configuration (f1.4xlarge, Xeon E5-2686v4, 16 threads); these are hardware comparators, not model comparators, and stage times cannot be summed due to concurrency.",
        ["Any foundation-model inference runtime or throughput benchmark (none is ingested in this bounded intake)", "Peak memory usage (host RAM capacity in the hardware comparator is not measured peak usage)", "Clinical-reporting turnaround time"],
        "Clinical applicability is not established: this is a conventional variant-calling pipeline's operational runtime baseline, a proxy for the resource/throughput constraints a foundation-model execution workflow would need to meet, not itself a model-execution benchmark.",
        ["No peak-memory endpoint is reported.", "No runtime repeat/variance (CI) is reported.", "A separate ~2-hour joint-aggregation figure over 3,202 genomes at concurrency 200 is a different operation and is not assigned to this single-sample runtime."],
        ["amp-source-dragen", "amp-source-dragen-supplementary-tables"], 18,
        "A dedicated rewire-benchmarks protocol/run task that actually executes an eligible foundation-model configuration and measures its resource/throughput budget.",
    ),
]

mapping_objects = [mapping_record(d) for d in mappings_draft]

(OUT / "use-cases-draft.json").write_text(json.dumps({"use_cases": USE_CASES, "mappings": mapping_objects}, indent=2, sort_keys=True) + "\n")
print(f"Wrote {len(USE_CASES)} use cases and {len(mapping_objects)} mappings to {OUT / 'use-cases-draft.json'}")
