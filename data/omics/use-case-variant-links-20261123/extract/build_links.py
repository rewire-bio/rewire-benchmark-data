#!/usr/bin/env python3
"""Build reviewed relevance-judgement claims and store changes for PR 2C (issue #224 and #56).

  python3 data/omics/use-case-variant-links-20261123/extract/build_links.py <repo-root> <out-dir>
  add --check to verify batch.jsonl against a clean deterministic rebuild.
"""
import glob
import hashlib
import json
import sys
from pathlib import Path

NOW = "2026-11-23T16:32:00Z"
REVIEW_DOC = "docs/reviews/use-cases/variant-interpretation-links-2026-11-23.md"
REVIEWER_NOTE = (
    "Deterministic scope and store verification against pinned records, protocol sources and "
    "scoped evidence concerns. No human scientific review."
)

# Each entry: (use_case_id, protocol_id, headline_metric, relevance, endpoint, rationale, constraints, extra_limits, meta)
LINKS = [
    # 1. Rare-disease candidate variant ranking (rare-disease-v2 PR #346 + TraitGym Mendelian)
    (
        "use-case-rare-disease-candidate-ranking",
        "rewire-local-20261121-rdv2-protocol-replication-500-main",
        "top-1-accuracy",
        "proxy",
        "Top-1, top-5 and top-10 recall of an inserted ClinVar >=2-star pathogenic SNV across 500 simulated rare-disease cases (50 held-out people)",
        "Proxy calibrated on simulated 1000 Genomes rare-disease exome candidate lists under non-1000G gnomAD v3.1.2 grpmax < 0.1%. Directly answers the held-out replication question on adding GPN-MSA (-0.2 percentage points, 98.33% CI -1.6 to +1.4, p = 0.844) and AlphaGenome AVI (+1.8 points, 95% CI -0.4 to +4.0) on top of combined lookups.",
        [
            "Simulated PanelApp 285 intellectual-disability candidate lists in 1000 Genomes backgrounds rather than real patient exomes.",
            "Keep distinct from clinical exome studies whose candidate lists reflect real diagnostic referrals.",
        ],
        [
            "gnomAD presence is only partly fixed: most ClinVar diagnostics are absent from gnomAD while background variants rarely are.",
        ],
        {"comparison_group": "rewire-rare-disease-v2-20261121", "comparison_title": "Rewire rare-disease-v2 diagnostic candidate ranking", "stratum_label": "500 replication SNV cases (50 new people)", "stratum_order": 1},
    ),
    (
        "use-case-rare-disease-candidate-ranking",
        "rewire-local-20261121-rdv2-protocol-snv-200-main",
        "top-1-accuracy",
        "proxy",
        "Top-1, top-5 and top-10 recall of an inserted ClinVar >=2-star pathogenic SNV across 200 SNV discovery cases (50 people)",
        "Proxy development cohort used to fit the locked combined rare-disease ranking models. Withholds Rule + AVI due to the flagged gnomAD presence split check.",
        [
            "Development cohort used to lock the combined lookup weights evaluated on the 500 replication set.",
            "Rule + AVI (rewire-local-20261121-rdv2-evaluation-rule-avi-snv-200) is excluded by scoped evidence concern.",
        ],
        [
            "Combined models on this 200-case cohort are cross-validated and exploratory.",
        ],
        {"comparison_group": "rewire-rare-disease-v2-20261121", "comparison_title": "Rewire rare-disease-v2 diagnostic candidate ranking", "stratum_label": "200 SNV cases (50 people)", "stratum_order": 2},
    ),
    (
        "use-case-rare-disease-candidate-ranking",
        "rewire-local-20261121-rdv2-protocol-indel-120-main",
        "top-1-accuracy",
        "proxy",
        "Top-1, top-5 and top-10 recall of an inserted ClinVar >=2-star pathogenic indel across 120 simulated indel cases",
        "Proxy evaluating single-tool lookup, CADD and Evo 2 7B indel candidate ranking on 120 simulated PanelApp 285 cases.",
        [
            "Covers small insertions and deletions only; SNV missense predictors do not score these events directly.",
        ],
        [
            "Small case sample (120 cases across 50 people) with cross-validated combined fits only.",
        ],
        {"comparison_group": "rewire-rare-disease-v2-20261121", "comparison_title": "Rewire rare-disease-v2 diagnostic candidate ranking", "stratum_label": "120 indel cases (50 people)", "stratum_order": 3},
    ),
    (
        "use-case-rare-disease-candidate-ranking",
        "lit-genomics-20261011-traitgym-protocol-mendelian-traits-matched-9-zero-shot",
        "auprc",
        "proxy",
        "Chromosome-weighted AUPRC discriminating OMIM noncoding Mendelian pathogenic variants from 9 matched negative controls",
        "Proxy measuring noncoding Mendelian regulatory variant prioritisation across DNA language models and CADD in a balanced 1:9 matched-control benchmark.",
        [
            "Measures curated OMIM noncoding variant discrimination with 9 matched negatives per causal variant rather than full patient exome/genome shortlists.",
        ],
        [
            "Fixed 1:9 case-control ratio inflates AUPRC relative to whole-genome clinical variant screening.",
        ],
        {},
    ),
    (
        "use-case-rare-disease-candidate-ranking",
        "lit-genomics-20261011-traitgym-protocol-mendelian-traits-matched-9-linear-probing",
        "auprc",
        "proxy",
        "Chromosome-weighted AUPRC of supervised linear probes discriminating OMIM noncoding Mendelian pathogenic variants from 9 matched controls",
        "Proxy measuring linear-probed embeddings from DNA foundation models and supervised baselines on noncoding Mendelian variants.",
        [
            "Linear probing requires labeled causal variants and matched negatives; compare separately from zero-shot scores.",
        ],
        [
            "Does not evaluate coding missense/nonsense alleles that dominate clinical diagnostic yield.",
        ],
        {},
    ),
    (
        "use-case-rare-disease-candidate-ranking",
        "ag-atlas-20261019-protocol-traitgym-mendelian-auprc",
        "auprc",
        "proxy",
        "AUPRC discriminating OMIM noncoding Mendelian variants from matched controls with AlphaGenome Variant Impact and baselines",
        "Proxy evaluating AlphaGenome Variant Impact noncoding Mendelian discrimination after MAF filtering.",
        [
            "Evaluated on TraitGym noncoding Mendelian subsets rather than whole-genome rare-disease cases.",
        ],
        [],
        {},
    ),
    (
        "use-case-rare-disease-candidate-ranking",
        "ag-atlas-20261019-protocol-table-s2-traitgym-mendelian",
        "auprc",
        "proxy",
        "AVI ablation AUPRC on TraitGym Mendelian noncoding variants across modality and pooling configurations",
        "Proxy ablation benchmark showing modality contributions to AlphaGenome noncoding Mendelian variant ranking.",
        [
            "Ablation table comparing internal AVI feature configurations rather than clinical candidate-ranking pipelines.",
        ],
        [],
        {},
    ),
    # 2. BRCA1 / BRCA2 germline interpretation (evo2ops PR #345 + Evo 2 Brixi 2026 BRCA1/BRCA2 SNV strata)
    (
        "use-case-brca1-brca2-germline-interpretation",
        "rewire-local-20261121-evo2ops-protocol-brca1-all-auroc",
        "auroc",
        "proxy",
        "AUROC classifying Findlay et al. BRCA1 SGE loss-of-function vs functional/intermediate across all 3,893 SNVs",
        "Proxy functional assay classification reproducing Evo 2 7B against CADD v1.7, REVEL and SpliceAI on the full Findlay BRCA1 SGE truth set.",
        [
            "Uncalibrated SGE functional score classification (AUROC) without ClinGen/ENIGMA germline likelihood ratios.",
        ],
        [],
        {"comparison_group": "rewire-evo2ops-20261121-brca1", "comparison_title": "Rewire Evo 2 7B BRCA1 SGE reproduction (evo2-cloud-operations)", "stratum_label": "All 3,893 BRCA1 SNVs", "stratum_order": 1},
    ),
    (
        "use-case-brca1-brca2-germline-interpretation",
        "rewire-local-20261121-evo2ops-protocol-brca1-coding-auroc",
        "auroc",
        "proxy",
        "AUROC classifying BRCA1 SGE loss-of-function across coding SNVs (missense, nonsense, synonymous)",
        "Proxy functional classification on BRCA1 coding SNVs comparing Evo 2 7B against REVEL v1.3, CADD and SpliceAI.",
        [
            "Pools nonsense and missense coding variants; inspect missense-only stratum separately before extrapolating to VUS triage.",
        ],
        [],
        {"comparison_group": "rewire-evo2ops-20261121-brca1", "comparison_title": "Rewire Evo 2 7B BRCA1 SGE reproduction (evo2-cloud-operations)", "stratum_label": "Coding BRCA1 SNVs", "stratum_order": 2},
    ),
    (
        "use-case-brca1-brca2-germline-interpretation",
        "rewire-local-20261121-evo2ops-protocol-brca1-missense-auroc",
        "auroc",
        "proxy",
        "AUROC classifying BRCA1 SGE loss-of-function within missense SNVs only",
        "Proxy functional assay discrimination isolated to BRCA1 missense substitutions without stop-gain signal.",
        [
            "Missense-only SGE functional classification; no ACMG/AMP PP3/BP4 likelihood calibration.",
        ],
        [],
        {"comparison_group": "rewire-evo2ops-20261121-brca1", "comparison_title": "Rewire Evo 2 7B BRCA1 SGE reproduction (evo2-cloud-operations)", "stratum_label": "Missense BRCA1 SNVs", "stratum_order": 3},
    ),
    (
        "use-case-brca1-brca2-germline-interpretation",
        "rewire-local-20261121-evo2ops-protocol-brca1-noncoding-auroc",
        "auroc",
        "proxy",
        "AUROC classifying BRCA1 SGE loss-of-function across noncoding/splice-region SNVs",
        "Proxy evaluating noncoding/splice BRCA1 functional sensitivity where REVEL has no coverage.",
        [
            "Includes promoter, UTR, intronic and splice-region Findlay SGE SNVs; predominantly splice-mediated LOF.",
        ],
        [],
        {"comparison_group": "rewire-evo2ops-20261121-brca1", "comparison_title": "Rewire Evo 2 7B BRCA1 SGE reproduction (evo2-cloud-operations)", "stratum_label": "Noncoding BRCA1 SNVs", "stratum_order": 4},
    ),
    (
        "use-case-brca1-brca2-germline-interpretation",
        "gfm-guides-20261014-evo2-brixi2026-protocol-brca1-both-snv",
        "auroc",
        "proxy",
        "Zero-shot AUROC and AUPRC on BRCA1 combined coding and noncoding SNVs (Evo 2 paper Supplementary Data 1)",
        "Proxy rank discrimination benchmarking Evo 2 and sequence models against baseline variant predictors on BRCA1 functional truth sets.",
        [
            "Uncalibrated AUROC/AUPRC from author tables; does not establish ENIGMA germline evidence thresholds.",
        ],
        [],
        {"comparison_group": "brixi2026-brca", "comparison_title": "Evo 2 paper BRCA1/BRCA2 SNV strata (Brixi et al. 2026)", "stratum_label": "BRCA1 coding + noncoding SNVs", "stratum_order": 1},
    ),
    (
        "use-case-brca1-brca2-germline-interpretation",
        "gfm-guides-20261014-evo2-brixi2026-protocol-brca1-coding-snv",
        "auroc",
        "proxy",
        "Zero-shot AUROC and AUPRC on BRCA1 coding SNVs (Evo 2 paper Supplementary Data 1)",
        "Proxy coding-stratum rank discrimination across Evo 2 models and comparators on BRCA1 functional variants.",
        ["Uncalibrated functional assay discrimination only; includes nonsense and synonymous variants."],
        [],
        {"comparison_group": "brixi2026-brca", "comparison_title": "Evo 2 paper BRCA1/BRCA2 SNV strata (Brixi et al. 2026)", "stratum_label": "BRCA1 coding SNVs", "stratum_order": 2},
    ),
    (
        "use-case-brca1-brca2-germline-interpretation",
        "gfm-guides-20261014-evo2-brixi2026-protocol-brca1-intronic-snv",
        "auroc",
        "proxy",
        "Zero-shot AUROC and AUPRC on BRCA1 intronic SNVs (Evo 2 paper Supplementary Data 1)",
        "Proxy intronic-stratum rank discrimination for BRCA1 SNVs across sequence models and splice predictors.",
        ["Uncalibrated author-reported AUROC/AUPRC; small positive class in intronic regions."],
        [],
        {"comparison_group": "brixi2026-brca", "comparison_title": "Evo 2 paper BRCA1/BRCA2 SNV strata (Brixi et al. 2026)", "stratum_label": "BRCA1 intronic SNVs", "stratum_order": 3},
    ),
    (
        "use-case-brca1-brca2-germline-interpretation",
        "gfm-guides-20261014-evo2-brixi2026-protocol-brca1-noncoding-snv",
        "auroc",
        "proxy",
        "Zero-shot AUROC and AUPRC on BRCA1 noncoding SNVs (Evo 2 paper Supplementary Data 1)",
        "Proxy noncoding-stratum rank discrimination on BRCA1 functional truth sets.",
        ["Uncalibrated author-reported AUROC/AUPRC."],
        [],
        {"comparison_group": "brixi2026-brca", "comparison_title": "Evo 2 paper BRCA1/BRCA2 SNV strata (Brixi et al. 2026)", "stratum_label": "BRCA1 noncoding SNVs", "stratum_order": 4},
    ),
    (
        "use-case-brca1-brca2-germline-interpretation",
        "gfm-guides-20261014-evo2-brixi2026-protocol-brca1-splice-region-snv",
        "auroc",
        "proxy",
        "Zero-shot AUROC and AUPRC on BRCA1 splice-region SNVs (Evo 2 paper Supplementary Data 1)",
        "Proxy splice-region BRCA1 rank discrimination benchmark across sequence foundation models and baselines.",
        ["Uncalibrated author-reported AUROC/AUPRC; compare splice thresholds with ClinGen ENIGMA criteria."],
        [],
        {"comparison_group": "brixi2026-brca", "comparison_title": "Evo 2 paper BRCA1/BRCA2 SNV strata (Brixi et al. 2026)", "stratum_label": "BRCA1 splice-region SNVs", "stratum_order": 5},
    ),
    (
        "use-case-brca1-brca2-germline-interpretation",
        "gfm-guides-20261014-evo2-brixi2026-protocol-brca2-both-snv",
        "auroc",
        "proxy",
        "Zero-shot AUROC and AUPRC on BRCA2 combined coding and noncoding SNVs (Evo 2 paper Supplementary Data 1)",
        "Proxy rank discrimination across Evo 2 models and comparators on BRCA2 SNV functional/clinical sets.",
        ["Uncalibrated author-reported AUROC/AUPRC; does not establish ENIGMA likelihood ratios."],
        [],
        {"comparison_group": "brixi2026-brca", "comparison_title": "Evo 2 paper BRCA1/BRCA2 SNV strata (Brixi et al. 2026)", "stratum_label": "BRCA2 coding + noncoding SNVs", "stratum_order": 6},
    ),
    (
        "use-case-brca1-brca2-germline-interpretation",
        "gfm-guides-20261014-evo2-brixi2026-protocol-brca2-coding-snv",
        "auroc",
        "proxy",
        "Zero-shot AUROC and AUPRC on BRCA2 coding SNVs (Evo 2 paper Supplementary Data 1)",
        "Proxy coding-stratum rank discrimination on BRCA2 SNVs.",
        ["Uncalibrated author-reported AUROC/AUPRC."],
        [],
        {"comparison_group": "brixi2026-brca", "comparison_title": "Evo 2 paper BRCA1/BRCA2 SNV strata (Brixi et al. 2026)", "stratum_label": "BRCA2 coding SNVs", "stratum_order": 7},
    ),
    (
        "use-case-brca1-brca2-germline-interpretation",
        "gfm-guides-20261014-evo2-brixi2026-protocol-brca2-noncoding-snv",
        "auroc",
        "proxy",
        "Zero-shot AUROC and AUPRC on BRCA2 noncoding SNVs (Evo 2 paper Supplementary Data 1)",
        "Proxy noncoding-stratum rank discrimination on BRCA2 SNVs.",
        ["Uncalibrated author-reported AUROC/AUPRC."],
        [],
        {"comparison_group": "brixi2026-brca", "comparison_title": "Evo 2 paper BRCA1/BRCA2 SNV strata (Brixi et al. 2026)", "stratum_label": "BRCA2 noncoding SNVs", "stratum_order": 8},
    ),
    # 3. Missense PP3/BP4 proxies (uncalibrated ClinVar SNV discrimination from #224)
    (
        "use-case-missense-pp3-bp4-calibrated-evidence",
        "gfm-guides-20261014-evo2-brixi2026-protocol-clinvar-coding-snv",
        "auroc",
        "proxy",
        "Zero-shot ClinVar coding SNV classification AUROC and AUPRC (Evo 2 paper Supplementary Data 1)",
        "Proxy: reports uncalibrated coding ClinVar SNV rank discrimination across Evo 2 and baseline predictors without ClinGen PP3/BP4 local posterior thresholds.",
        [
            "Proxy evidence only: lacks Pejaver/Bergquist calibrated posterior score thresholds and pools missense with nonsense coding SNVs.",
            "Compare with calibrated Rewire/Pejaver/Bergquist protocols rather than inferring PP3/BP4 points from AUROC.",
        ],
        [],
        {},
    ),
    (
        "use-case-missense-pp3-bp4-calibrated-evidence",
        "gfm-guides-20261014-gpnmsa-protocol-ablation-clinvar-auroc",
        "auroc",
        "proxy",
        "ClinVar Pathogenic versus gnomAD common missense AUROC (GPN-MSA Supplementary Table 4)",
        "Proxy: measures rank discrimination on ClinVar missense versus common gnomAD variants without ClinGen PP3/BP4 posterior calibration or rare-variant benign control.",
        [
            "Proxy evidence only: no calibrated PP3/BP4 thresholds; common-gnomAD negatives overstate separation among rare VUS.",
            "Omits gfm-guides-20261014-gpnmsa-eval-ablation-msa-frequency-clinvar and gfm-guides-20261014-gpnmsa-eval-ablation-phylop-phastcons-combined-clinvar (linked to method rather than configuration records), leaving the 15 configuration-backed GPN-MSA evaluations.",
        ],
        [],
        {},
    ),
    (
        "use-case-missense-pp3-bp4-calibrated-evidence",
        "gfm-guide-20261014-protocol-evee-deconfounded-snv-auroc",
        "auroc",
        "proxy",
        "Deconfounded ClinVar SNV pathogenicity AUROC across EVEE linear probes and zero-shot baselines (Pearce et al. 2026 Figure 1c)",
        "Proxy: measures gene-deconfounded ClinVar rank discrimination (AUROC) for foundation model probes and comparators without ClinGen PP3/BP4 calibrated cutoffs. Excludes the concerned NTv3 and AlphaMissense-Overall evaluations.",
        [
            "Proxy evidence only: no calibrated PP3/BP4 score intervals and preprint (bioRxiv v4).",
            "Excludes gfm-guide-20261014-eval-evee-deconfounded-ntv3-cosine and gfm-guide-20261014-eval-evee-deconfounded-alphamissense (scoped concerns on evee-v4).",
        ],
        [
            "EVEE supervised probes are trained on ClinVar variants under gene-holdout; does not yield standalone zero-shot evidence thresholds.",
        ],
        {},
    ),
    (
        "use-case-missense-pp3-bp4-calibrated-evidence",
        "ag-atlas-20261019-protocol-clinvar-snv-by-consequence-auprc",
        "auprc",
        "proxy",
        "ClinVar pathogenic versus benign SNV AUPRC stratified by VEP consequence, including missense (AlphaGenome Atlas)",
        "Proxy: reports AlphaGenome AVI and baseline AUPRC stratified by consequence without ClinGen PP3/BP4 posterior score calibration.",
        [
            "Proxy evidence only: uncalibrated AUPRC does not provide ACMG/AMP PP3 or BP4 score cutoffs; use rewire-clingen-pp3-bp4 for calibrated AVI intervals.",
        ],
        [],
        {},
    ),
    (
        "use-case-missense-pp3-bp4-calibrated-evidence",
        "ag-atlas-20261019-protocol-table-s2-clinvar",
        "auprc",
        "proxy",
        "AVI feature ablation ClinVar AUPRC column (AlphaGenome Atlas Table S2)",
        "Proxy: reports ClinVar discrimination across internal AlphaGenome AVI feature ablations without PP3/BP4 posterior threshold calibration.",
        [
            "Proxy evidence only: feature-ablation AUPRC without ACMG/AMP threshold calibration or allele-frequency stratification.",
        ],
        [],
        {},
    ),
    (
        "use-case-missense-pp3-bp4-calibrated-evidence",
        "lit-genomics-20261011-guanine-protocol-clinvar-snv",
        "spearman-correlation",
        "proxy",
        "GUANinE v1.1 clinvar-snv Spearman rank correlation (x100) across zero-shot DNA models",
        "Proxy: reports GUANinE ClinVar SNV Spearman rank correlation without calibrated ACMG/AMP PP3/BP4 evidence thresholds.",
        [
            "Proxy evidence only: Spearman correlation over ClinVar SNVs provides no calibrated likelihood ratios or point cutoffs.",
        ],
        [],
        {},
    ),
    # 4. Splicing follow-up (Evo 2 clean SpliceVarDB SNV strata + AlphaGenome Atlas DNM1 minigene AP)
    (
        "use-case-splicing-follow-up",
        "gfm-guides-20261014-evo2-brixi2026-protocol-splicevardb-both-snv",
        "auroc",
        "proxy",
        "Zero-shot SpliceVarDB combined coding and noncoding SNV splice-altering classification AUROC/AUPRC (Evo 2 paper Supplementary Data 1)",
        "Proxy evaluating zero-shot foundation models and splice predictors on experimentally validated SpliceVarDB SNVs.",
        [
            "Excludes the disputed SpliceVarDB intronic-only stratum (rewire-benchmark-data#163).",
            "SpliceVarDB validation rates reflect literature-curated assays rather than prospective clinical RNA testing.",
        ],
        [],
        {"comparison_group": "brixi2026-splicevardb", "comparison_title": "Evo 2 paper SpliceVarDB SNV strata (Brixi et al. 2026)", "stratum_label": "SpliceVarDB both (coding + noncoding) SNVs", "stratum_order": 1},
    ),
    (
        "use-case-splicing-follow-up",
        "gfm-guides-20261014-evo2-brixi2026-protocol-splicevardb-exonic-snv",
        "auroc",
        "proxy",
        "Zero-shot SpliceVarDB exonic SNV splice-altering classification AUROC/AUPRC (Evo 2 paper Supplementary Data 1)",
        "Proxy isolating exonic splice-altering SNV prioritisation in SpliceVarDB.",
        [
            "Exonic splice assays only; companion intronic-only stratum excluded while counts remain disputed (rewire-benchmark-data#163).",
        ],
        [],
        {"comparison_group": "brixi2026-splicevardb", "comparison_title": "Evo 2 paper SpliceVarDB SNV strata (Brixi et al. 2026)", "stratum_label": "SpliceVarDB exonic SNVs", "stratum_order": 2},
    ),
    (
        "use-case-splicing-follow-up",
        "ag-atlas-20261019-protocol-dnm1-active-variant-ap",
        "average-precision",
        "proxy",
        "DNM1 saturation minigene splice-assay active versus inactive variant average precision (AlphaGenome Atlas)",
        "Proxy benchmarking AlphaGenome AVI and baselines on experimental DNM1 intronic/exonic splicing saturation assays.",
        [
            "Single-gene DNM1 minigene screen; AlphaGenome main-paper Table 3/4 splicing protocols remain needs_review until independently checked.",
        ],
        [],
        {},
    ),
]


def load_store(root: Path):
    records = {}
    raw_lines = {}
    for pat in ("data/entities/*.jsonl", "data/evidence/evaluations/*.jsonl", "data/evidence/results/*.jsonl"):
        for f in sorted(root.glob(pat)):
            for line in f.read_text().splitlines():
                if not line:
                    continue
                d = json.loads(line)
                records[d["id"]] = d
                raw_lines[d["id"]] = line
    prov = {}
    for f in sorted((root / "data/provenance/records").glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if not line:
                continue
            d = json.loads(line)
            prov[d["id"]] = d
    return records, raw_lines, prov


def scoped_concern_targets(records: dict) -> set[str]:
    targets = set()
    for r in records.values():
        if r["kind"] == "source":
            for item in r["attributes"].get("evidence_concerns") or []:
                if isinstance(item, dict) and item.get("applies_to"):
                    for tid in item["applies_to"]:
                        targets.add(tid)
    return targets


def build(root: Path):
    records, raw_lines, prov = load_store(root)

    # Compute the scoped concerns update on evee-v4 first so our eligibility filter sees it
    evee_id = "gfm-guide-20261014-source-evee-v4"
    evee_orig = json.loads(raw_lines[evee_id])
    evee_orig["attributes"]["evidence_concerns"][0]["applies_to"] = [
        "gfm-guide-20261014-eval-evee-deconfounded-ntv3-cosine"
    ]
    evee_orig["attributes"]["evidence_concerns"][1]["applies_to"] = [
        "gfm-guide-20261014-eval-evee-deconfounded-alphamissense"
    ]
    records_after_scope = dict(records)
    records_after_scope[evee_id] = evee_orig
    scoped = scoped_concern_targets(records_after_scope)

    whole_concerned = set()
    for r in records_after_scope.values():
        if r["kind"] == "source":
            for item in r["attributes"].get("evidence_concerns") or []:
                if isinstance(item, str) or (isinstance(item, dict) and not item.get("applies_to")):
                    whole_concerned.add(r["id"])

    def clean_source(sid: str) -> bool:
        s = records_after_scope.get(sid)
        return bool(s and s["kind"] == "source" and s["status"] in ("source_checked", "reproduced") and sid not in whole_concerned)

    evals_by_proto = {}
    results_by_eval = {}
    for r in records_after_scope.values():
        if r["kind"] == "evaluation":
            for l in r["links"]:
                if l["relation"] == "assessment":
                    evals_by_proto.setdefault(l["target_id"], []).append(r)
        elif r["kind"] == "result":
            for l in r["links"]:
                if l["relation"] == "evaluation":
                    results_by_eval.setdefault(l["target_id"], []).append(r)

    batch_claims = []
    uc_additions = {}

    for uc_id, proto_id, hmetric, relevance, endpoint, rationale, constraints, extra_limits, meta in LINKS:
        proto = records_after_scope[proto_id]
        assert proto["status"] == "source_checked", proto_id
        assert all(clean_source(s) for s in proto["source_ids"]), (proto_id, proto["source_ids"])

        clean_evs = []
        for e in sorted(evals_by_proto.get(proto_id, []), key=lambda x: x["id"]):
            if e["status"] not in ("source_checked", "reproduced"):
                continue
            cfgs = [
                records_after_scope.get(l["target_id"])
                for l in e["links"]
                if l["relation"] == "system"
                and records_after_scope.get(l["target_id"], {}).get("kind") == "configuration"
            ]
            if not cfgs or any(
                c["status"] not in ("source_checked", "reproduced")
                or any(not clean_source(s) for s in c["source_ids"])
                for c in cfgs
            ):
                continue
            dts = [records_after_scope.get(l["target_id"]) for l in e["links"] if l["relation"] == "data"]
            if any(
                not d
                or d["kind"] not in ("dataset", "dataset_subset")
                or d["status"] in ("disputed", "excluded", "superseded")
                or any(not clean_source(s) for s in d["source_ids"])
                for d in dts
            ):
                continue
            rows = [r for r in results_by_eval.get(e["id"], []) if r["status"] in ("source_checked", "reproduced")]
            if not rows or any(any(not clean_source(s) for s in (r["source_ids"] + e["source_ids"])) for r in rows):
                continue
            assessments = [
                records_after_scope.get(l["target_id"])
                for l in e["links"]
                if l["relation"] == "assessment"
            ]
            base_path = (
                [e["id"]]
                + [l["target_id"] for l in e["links"] if l["relation"] in ("system", "assessment", "data")]
                + [l["target_id"] for a in assessments if a for l in a["links"] if l["relation"] == "part_of"]
            )
            if any(pid in scoped for r in rows for pid in ([r["id"]] + base_path)):
                continue
            clean_evs.append(e["id"])

        assert clean_evs, f"No clean evaluations found for {proto_id}"
        # Keep existing protocol source_locator or default to primary source
        p_sources = proto["source_ids"]
        claim_id = f"use-case-mapping-20261123-{proto_id}"
        attrs = {
            "field": f"links:assessed_by:{proto_id}",
            "value": proto_id,
            "relevance": relevance,
            "endpoint": endpoint,
            "rationale": rationale,
            "constraints": constraints,
            "limitations": list(proto["attributes"].get("limitations", []))[:3] + extra_limits,
            "citation_locators": [{"source_id": s, "locator": proto["attributes"].get("source_locator", "See protocol record")} for s in p_sources[:2]],
            "source_locator": proto["attributes"].get("source_locator", f"{proto_id}: see protocol record"),
            "headline_metric": hmetric,
            **meta,
            "reason": "Use-case variant interpretation linking pass 2026-11-23 (rewire-benchmark-data#224, #345 BRCA1, #346 rare-disease-v2).",
            "review": {
                "method": ["scope-review", "source-hash-verification"],
                "reviewer": ["rewire-deterministic-table-checker"],
                "reviewer_note": REVIEWER_NOTE,
                "reviewed_at": NOW,
                "note": f"Reviewed and verified clean evaluations ({len(clean_evs)}) against {REVIEW_DOC}.",
            },
            "reviewed_evaluations": clean_evs,
        }
        batch_claims.append({
            "id": claim_id,
            "kind": "claim",
            "name": f"Relevance of {proto_id} to {uc_id}",
            "description": rationale,
            "status": "source_checked",
            "facets": {},
            "source_ids": p_sources,
            "links": [{"relation": "subject", "target_id": uc_id}],
            "attributes": attrs,
        })
        uc_additions.setdefault(uc_id, []).append(proto_id)

    changes = []
    # First change: gfm-guide-20261014-source-evee-v4 scoped concerns
    evee_base = hashlib.sha256(raw_lines[evee_id].encode("utf-8")).hexdigest()
    assert prov[evee_id]["sha256"] == evee_base
    evee_line = json.dumps(evee_orig, ensure_ascii=False, separators=(",", ":"))
    evee_sha = hashlib.sha256(evee_line.encode("utf-8")).hexdigest()
    changes.append({"id": evee_id, "base_sha256": evee_base, "sha256": evee_sha, "record": evee_orig})

    # Subsequent changes: append assessed_by links to the 4 use_cases
    for uc_id, proto_ids in uc_additions.items():
        uc = json.loads(raw_lines[uc_id])
        base_sha = hashlib.sha256(raw_lines[uc_id].encode("utf-8")).hexdigest()
        assert prov[uc_id]["sha256"] == base_sha
        existing = {(l["relation"], l["target_id"]) for l in uc["links"]}
        for pid in proto_ids:
            if ("assessed_by", pid) not in existing:
                uc["links"].append({"relation": "assessed_by", "target_id": pid})
        new_line = json.dumps(uc, ensure_ascii=False, separators=(",", ":"))
        new_sha = hashlib.sha256(new_line.encode("utf-8")).hexdigest()
        changes.append({"id": uc_id, "base_sha256": base_sha, "sha256": new_sha, "record": uc})

    return batch_claims, changes


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--check"]
    root, out_dir = Path(args[0]), Path(args[1])
    claims, changes = build(root)
    text = "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in claims)
    batch_file = out_dir / "batch.jsonl"
    if "--check" in sys.argv:
        assert batch_file.read_text() == text, "batch.jsonl differs from rebuild"
        print(f"{len(claims)} claims verified against rebuild")
    else:
        out_dir.mkdir(parents=True, exist_ok=True)
        batch_file.write_text(text)
        ch_text = "".join(json.dumps(c, ensure_ascii=False, separators=(",", ":")) + "\n" for c in changes)
        (out_dir / "changes.jsonl").write_text(ch_text)
        print(f"Wrote {len(claims)} claims and {len(changes)} changes to {out_dir}")
