#!/usr/bin/env python3
"""Build data/omics/use-case-coverage-binder-20261022/coverage.json from batch.jsonl.

Run after build_batch.py, from this directory:  python3 build_coverage.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import usecase

OUT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATCH = os.path.join(OUT_DIR, "batch.jsonl")

REUSED = {
    "discovery-model-rfdiffusion": "Reused as the parent of the AlphaProteo comparator configuration "
                                   "(configuration_of) and of the Bennett antibody pipeline "
                                   "(variant_of).",
    "discovery-model-proteinmpnn": "Reused as a uses_model target from the BindCraft and Bennett "
                                   "configurations.",
}

CHECKED_NOT_USED = {
    "discovery-model-genie-3": "Checked; not linked. Genie 3 appears in no extracted source with a "
                               "measured binder design outcome.",
    "catalog-model-boltz-2": "Checked; not linked. Boltz-2 appears in no extracted source with a "
                             "measured binder design outcome. BoltzGen, which does, was not reached.",
    "lit-interactions-20261011-mochibind-protocol-alphabind-pem-pairwise-accuracy":
        "Checked; not linked. The AlphaBind protocols score affinity and pairing prediction, not "
        "design, so they bear on use-case-structural-hypotheses-experiments.",
    "lit-interactions-20261011-mochibind-protocol-alphabind-pp489-pairwise-accuracy": "As above.",
    "lit-interactions-20261011-mochibind-protocol-alphabind-tra-pairwise-accuracy": "As above.",
    "lit-interactions-20261011-mochibind-protocol-alphabind-vhh72-pairwise-accuracy": "As above.",
    "structural-20261009-protocol-smorodina2026-vhh-cognate-vs-shuffled":
        "Checked; not linked. The nanobody protocols score antigen pairing by ipTM, not design.",
    "structural-20261009-protocol-smorodina2026-vhh-dockq-vs-sampling": "As above.",
    "structural-20261009-protocol-smorodina2026-vhh-iptm-dockq-calibration": "As above.",
    "use-case-structural-hypotheses-experiments":
        "Checked; a neighbouring decision, not an alias. It covers choosing structural hypotheses to "
        "test; this use case covers designing a binder. No record is shared.",
}


def main():
    records = [json.loads(line) for line in open(BATCH, encoding="utf-8")]
    by_kind = {}
    for rec in records:
        by_kind.setdefault(rec["kind"], []).append(rec["id"])

    judgements = {}
    for rec in records:
        if rec["kind"] != "claim":
            continue
        field = rec["attributes"].get("field", "")
        if field.startswith("links:assessed_by:"):
            judgements[rec["id"]] = {
                "protocol": rec["attributes"]["value"],
                "relevance": rec["attributes"]["relevance"],
                "comparison_group": rec["attributes"]["comparison_group"],
                "headline_metric": rec["attributes"]["headline_metric"],
                "status": rec["status"],
            }

    coverage = {
        "schema_version": "1.0",
        "batch": "data/omics/use-case-coverage-binder-20261022",
        "issue": "https://github.com/rewire-bio/rewire-benchmark-data/issues/176",
        "use_case": usecase.USE_CASE_ID,
        "slug": "de-novo-binder-design",
        "extracted_at": "2026-10-22",
        "extracted_by": "Claude extraction agent; no human review claimed",
        "review_status": "none. Every record is needs_review and no review.json is written; review is "
                         "a separate pass by a different worker (docs/collection.md section 5).",
        "added_to_store": False,
        "new_record_counts": {kind: len(ids) for kind, ids in sorted(by_kind.items())},
        "new_records_total": len(records),
        "new_ids": {kind: sorted(ids) for kind, ids in sorted(by_kind.items())
                    if kind in ("source", "use_case", "pipeline", "method", "protocol")},
        "reused_ids": REUSED,
        "checked_not_used_ids": CHECKED_NOT_USED,
        "judgements": judgements,
        "judgement_counts_by_relevance": {
            relevance: sum(1 for j in judgements.values() if j["relevance"] == relevance)
            for relevance in ("direct", "proxy", "outside_scope")
        },
        "vocabulary_added": {
            "data/vocab/metric.ttl": ["hit-rate", "dissociation-constant"],
            "data/vocab/unit.ttl": ["nanomolar", "micromolar"],
        },
        "sources_extracted": [
            "AlphaProteo, arXiv:2409.08022v1: Table 1, Table S2 and Table S3 in full",
            "BindCraft, Nature 10.1038/s41586-025-09429-6: per-target counts and affinities from the "
            "Results prose, the 46.3% mean and the 10-100% range, and Supplementary Table 1 in full",
            "Bennett 2025, Nature 10.1038/s41586-025-09721-5: Supplementary Methods Tables 5 and 6 in "
            "full",
            "Adaptyv EGFR competition, bioRxiv 10.1101/2025.04.17.648362 and its round 2 repository at "
            "commit fc91b91ddc367830b755b215dbc69669675ad6a0: every funnel count, rate and per-method "
            "outcome printed in the body prose",
        ],
        "gaps": usecase.EVIDENCE_GAPS,
        "not_reached": [
            "BoltzGen (bioRxiv 10.1101/2025.11.20.689494) Tables 2 and 3",
            "Filius et al. 2025 (ACS Chem Biol 10.1021/acschembio.5c00774) Supporting Information "
            "Table S3",
            "Nature Communications minibinder paper (doi 10.1038/s41467-026-76760-5) and its Source "
            "Data",
            "PXDesign's own measured values (bioRxiv 10.1101/2025.08.15.670450 Tables 1 and 2)",
            "BenchBB (benchbb.bio) and ProtDBench (arXiv:2605.04118)",
            "Adaptyv round 1 repository and the round 2 raw kinetic, neutralisation, structure and "
            "embedding packages",
            "The primary sources behind AlphaProteo's compilation rows (Procko, Gainza, Cao, Berger, "
            "Yang, Watson)",
        ],
        "figures_not_read": [
            "BindCraft Fig. 1b (per-target numerators and denominators in graphic boxes)",
            "Adaptyv Figures 3, 8, 9 and 10 (per-method comparison, per-round counts at three "
            "undefined thresholds, design-category breakdown, the 60 affinities)",
            "AlphaProteo Figures 1D, 1E and S1 to S7",
            "Bennett Extended Data Fig. 10 (the retrospective ipTM analysis; its printed statistics "
            "are recorded from the prose instead)",
        ],
        "values_not_computed_from_source_data": [
            "BindCraft Supplementary Data 1: the row filter that reconciles with the Results prose for "
            "nine of twelve targets fails for PD-L1, CrSAS-6 and CbAgo, so the per-target counts are "
            "not recomputed from it.",
            "Adaptyv results/result_summary.csv: neither the repository nor the paper states an "
            "aggregation over these rows, method labels are entrants' free text, and the three binding "
            "thresholds behind the figure counts are undefined, so no per-method rate is computed.",
        ],
        "excluded_by_rule": [
            "PXDesign's baseline column: AlphaProteo and Chai-2 values copied from publications and "
            "partly adjusted by the PXDesign authors using their own HTRF data. A third party's "
            "reanalysis.",
            "AlphaProteo Table 1 'Other design methods' and 'Other design methods, optimized' rows and "
            "Table S2 'RFdiffusion (published)' row: copied from publications not retrieved here, with "
            "asterisked values re-measured by the AlphaProteo authors and one design substituted for "
            "the published best one (Section S4.2). Transcribed verbatim as a claim, not recorded as "
            "results.",
            "Junker and Schoeder 2026 (PLOS ONE 10.1371/journal.pone.0355549) and Nanda 2026 "
            "(doi 10.21203/rs.3.rs-11106209/v1): in silico only, no wet-lab arm. Recorded as gaps.",
        ],
        "reviewer_must_judge": [
            "Whether grading the three affinity protocols `direct` is right, given that each value is a "
            "best-of-subset over a set the authors chose to follow up.",
            "Whether `hit-rate` should exist as a concept separate from `success-rate`. It is declared "
            "`skos:broader :success-rate` and differs in two ways the batch relies on: the criterion is "
            "a wet-lab measurement and the denominator is the tested set.",
            "Whether AlphaProteo's compilation rows should instead be results with origin "
            "`paper_compilation`, which docs/collection.md permits, rather than a transcription claim.",
            "Whether the five internal inconsistencies recorded as source evidence_concerns are "
            "complete and correctly worded.",
            "Whether one protocol per hit definition, with targets as datasets, is the right "
            "granularity, or whether a protocol per target would serve the use-case page better.",
        ],
    }

    path = os.path.join(OUT_DIR, "coverage.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(coverage, fh, indent=2, ensure_ascii=False, sort_keys=False)
        fh.write("\n")
    print(f"wrote {path}: {len(records)} records, {len(judgements)} judgements")


if __name__ == "__main__":
    main()
