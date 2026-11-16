#!/usr/bin/env python3
"""Apply the 2026-11-16 independent review to data/omics/traitgym-20261116/batch.jsonl.

Run from the repository root. Idempotent: it rewrites every review block and the
amended fields from the constants below, and appends the correction claims only
if they are not already present.

It does not touch stored records; those are edited after `records -- add`.
"""

from __future__ import annotations

import json
import sys

BATCH = "data/omics/traitgym-20261116/batch.jsonl"
PAPER = "traitgym-20261116-source-biorxiv-v2"
TEXT_SHA = "23ae4d67751f1092e5cc2da66b52091fa9bbc3ec59310f06bc65be28f93c5097"
PDF_URL = "https://www.biorxiv.org/content/10.1101/2025.02.11.637758v2.full.pdf"
DATE = "2026-11-16"
AT = "2026-11-16T02:10:00Z"
REVIEWER_NOTE = ("Claude review agent (independent of the extractor); no human review claimed. "
                 "Every value was read against the pinned artifact; nothing was reproduced and no "
                 "model was run.")

HASH_NOTE = (
    "The pinned artifact was re-downloaded from the v2 full-PDF URL for this pass. Its PDF bytes "
    "hash to 961933ed2396ecb0a75737cc27f0655db07ca62be49654f9139ae95815d050f9, not to the "
    "80426c499e0b498e07c07ea598a2f68049adea7569b30fda58cdc0ebafa6c7aa on the source record, and "
    "cannot: bioRxiv restamps the container on every request. The reviewer's download differs "
    "from the extractor's two in 41 and 44 bytes, every one of them a download-time stamp (the "
    "XMP ModifyDate and MetadataDate, the document ModDate and the trailer ID), with the same 37 "
    "pages, the same CreationDate of 2025-03-04 and the same pdftotext -layout text layer. That "
    f"text layer hashes to {TEXT_SHA}, which is the hash the source record's hash_scope names as "
    "the stable check and the hash recorded here; every value in this batch was read from it."
)

VALUE_NOTE = (
    "npm run batch -- check-values reproduced the extractor's report byte for byte: 96 in_cell, 36 "
    "in_row, no not_in_row, no wrong_column, no overclaimed_in_row. All 132 results were then "
    "re-read by data/omics/traitgym-20261116/review/recheck_values.py, written for this pass and "
    "importing nothing from extract/. It fixes a character-column band per table column from the "
    "start offset of each column header token (Table S8 at offsets 59, 71, 88, 102 and 122; Table "
    "S11 at 79, 92, 111 and 124; Table 4 at 85; Table 5 at 113; Table S4 at 98) and accepts a "
    "numeric token only when its own start offset falls inside exactly one band, so column "
    "assignment is checked directly for all 132 results, including the 36 that check-values could "
    "place only in a row. Result: 132 of 132 agree on printed_value and numeric_value, 0 "
    "mismatches (review/recheck-values.tsv). Three negative controls confirm it is a cell check "
    "and not a row check: swapping two values inside one Table S11 row rejects exactly those two "
    "results, copying one value into a neighbouring column band rejects exactly that one, and "
    "shifting a row's values one column left is rejected at parse with the offending offset named. "
    "Independently of both scripts, all 100 cells of Table S8 were transcribed by hand into "
    "review/s8-reviewer-reading.tsv before extract/comparison.tsv was opened, and all 36 in_row "
    "cells of Tables 4, 5, S4 and S11 were read by eye from the text layer; the hand reading of "
    "Table S8 agrees with the band parse in all 100 cells."
)

RECON_NOTE = (
    "The 100-cell reconciliation of Table S8 against the stored Hugging Face metric results was "
    "re-done independently by review/reconcile_s8.py, with the cell-to-metric-file mapping written "
    "out again rather than reused. Four comparisons, all with no differences: the reviewer's "
    "reading of the paper against the stored full-precision values rounded to three decimal "
    "places, the reviewer's reading against the extractor's paper values, the reviewer's rounding "
    "against the extractor's, and the reviewer's cell-to-stored-result mapping against the "
    "extractor's (review/reconcile-s8.tsv). All 156 stored results were accounted for again from "
    "their metric file names alone: 100 Table S8 cells, 36 linear probing "
    "(.LogisticRegression.chrom, 18 systems on each dataset), 14 zero-shot results of seven "
    "non-gLM systems on both datasets, and 6 Mendelian-only duplicate scoring variants, with "
    "nothing left over."
)


def review(extra: str, methods: list[str]) -> dict:
    return {
        "artifact_sha256": TEXT_SHA,
        "date": DATE,
        "method": methods,
        "method_note": HASH_NOTE,
        "note": extra,
        "retrieval_url": PDF_URL,
        "reviewed_at": AT,
        "reviewer": ["claude"],
        "reviewer_note": REVIEWER_NOTE,
    }


RESULT_METHODS = ["source-hash-verification", "deterministic-table-parse", "pdf-text-parse",
                  "independent-cell-check"]
ENTITY_METHODS = ["source-hash-verification", "pdf-text-parse", "scope-review"]
CLAIM_METHODS = ["source-hash-verification", "pdf-text-parse", "transcription", "scope-review"]

NOTE_RESULT = VALUE_NOTE
NOTE_EVAL = (
    "The evaluation's system, protocol, dataset, origin and model_version were checked against the "
    "paper at the result's locator, and its nulls against the source: Tables 4, 5 and S11 print no "
    "standard error and state no chromosome aggregation, and Table S11 does not say whether a cell "
    "is the zero-shot or the linear probing score. " + VALUE_NOTE
)
NOTE_ENTITY = (
    "Scope and every descriptive field were read against the paper at the locator recorded. The "
    "protocols' selection rules, metric qualifiers and selection_bias were checked to be what the "
    "paper states and to differ from the stored zero-shot and linear-probing qualifiers, so these "
    "results do not join the stored comparison groups."
)
NOTE_CLAIM = "Each quoted sentence and number was read against the paper at the locator recorded."
NOTE_SOURCE = (
    "Publication status was re-checked independently on 2026-11-16 and the work is still a preprint "
    "only. The bioRxiv API lists versions 1 and 2 with published \"NA\" and its /pubs endpoint "
    "reports no published version; the v2 article page carries no \"Now published in\" banner; "
    "Crossref holds only the posted-content record with an empty relation object and a "
    "bibliographic search returns no journal article; PubMed has 39990426, the preprint, as the "
    "only match for TraitGym, and the eight Benegas G records for 2025 to 2027 contain no journal "
    "version of this work (the one Nature 2026 paper, 42717086, is GPN-Star); Europe PMC holds "
    "PPR978187 only; OpenAlex types the work as a preprint with bioRxiv, PubMed and PMC locations "
    "and no journal; Semantic Scholar gives the venue as bioRxiv. Searches were by author and by "
    "topic as well as by title, because a journal version can appear under a changed title. "
    + HASH_NOTE
)

# ---------------------------------------------------------------- amendments

RECON_ID = "traitgym-20261116-claim-paper-agrees-with-benchmark-metric-files"
RECON_VALUE = (
    "Table S8 prints the zero-shot AUPRC of ten genomic language models under five scoring "
    "approaches on both datasets, 100 cells, rounded to three decimal places. All 100 cells equal "
    "the corresponding value in the benchmark's own Hugging Face metric files, already in the "
    "store as 100 results from lit-genomics-20261011-traitgym-source-hf-metrics, when those "
    "full-precision values are rounded to three decimal places, with no disagreement. The two are "
    "on the same basis: Appendix B.4 states the weighted average over chromosomes is used for "
    "zero-shot scores as well, and the stored values come from the files under "
    "AUPRC_by_chrom_weighted_average/all/. The embedding columns correspond to the Embeddings.* "
    "metric files rather than to the six InnerProduct and EuclideanDistance files the benchmark "
    "also publishes for Mendelian traits. The printed value settles that mapping for one of the "
    "six: GPN-Promoter, L2 dist., Mendelian traits is 0.345, where "
    "GPN_final_Embeddings.plus.euclidean_distance is 0.3449957 and "
    "GPN_final_EuclideanDistance.plus.score is 0.3469633, which rounds to 0.347. For the other "
    "five, all Inner prod. cells, the two published files agree to three decimal places, so the "
    "printed value is consistent with either and the mapping rests on the column's name and on "
    "the Embeddings.* files being the set published for both datasets. The paper prints no value "
    "for the 36 stored linear probing results, which appear only in Figure 5, for the 14 stored "
    "zero-shot results of models that are not genomic language models, or for those 6 duplicate "
    "scoring variants. The cell-by-cell table is "
    "data/omics/traitgym-20261116/extract/comparison.tsv, produced by "
    "data/omics/traitgym-20261116/extract/compare_s8.py; the review re-did the comparison "
    "independently in data/omics/traitgym-20261116/review/reconcile-s8.tsv."
)

LIGHT_ID = "traitgym-20261116-method-lightweight-ensemble"
LIGHT_PROVENANCE = (
    "Section 6 'Model ensembling' defines the term: \"we do see small improvements when ensembling "
    "CADD with a reduced number of features from other models (LLR for GPN-MSA and “ℓ2 of "
    "ℓ2 scores” for Borzoi), which we refer to as “lightweight” feature "
    "ensembling (Figure 8)\". That composition is this record. The Table S11 caption says only "
    "\"lightweight feature ensemble is evaluated for Mendelian traits\" and does not repeat the "
    "composition; Figure 8 plots this ensemble alongside two smaller feature sets "
    "(CADD+GPN-MSA_LLR and CADD+Borzoi_L2_L2) and CADD alone, and this one scores highest."
)
LIGHT_RESULT_LIMITATION = (
    "The ensemble is the lightweight feature ensemble (Table S11 caption). Section 6 defines "
    "lightweight feature ensembling as CADD features with the GPN-MSA LLR and the Borzoi l2 of l2 "
    "score, which is the system recorded here; the caption itself does not repeat the composition, "
    "and Figure 8 also plots two smaller feature sets and CADD alone."
)
LIGHT_RESULT_OLD = ("The ensemble is the lightweight feature ensemble (Table S11 caption); for "
                    "Mendelian traits the caption does not say which lightweight ensemble.")

MODEL_ID = "traitgym-20261116-model-gpn-promoter"

# ---------------------------------------------------------------- corrections

HF = "lit-genomics-20261011-traitgym-source-hf-metrics"
BENCH = "lit-genomics-20261011-traitgym-benchmark-traitgym"
GPN = "regulatory-variant-20261009-model-gpn"

HF_LIMS_OLD = [
    "Official benchmark repository by the TraitGym authors, who also developed GPN-MSA and GPN-Promoter; those rows are author_reported.",
    "Benchmark paper: Benegas, Eraslan and Song, bioRxiv 10.1101/2025.02.11.637758 v2 (2025-03-04, CC BY-NC-ND), outside the search window; its Figure 2 plots these metrics. The paper's Table S8 prints rounded zero-shot AUPRCs on a related but unweighted basis and was not extracted.",
    "Hugging Face datasets are mutable; the revision hash pins this retrieval.",
]
HF_LIMS_NEW = [
    HF_LIMS_OLD[0],
    "Benchmark paper: Benegas, Eraslan and Song, bioRxiv 10.1101/2025.02.11.637758 v2 (2025-03-04, CC BY-NC-ND), outside the search window; its Figure 2 plots these metrics. Its Table S8 prints the same zero-shot AUPRCs rounded to three decimal places, on the same chromosome-weighted basis: Appendix B.4 says \"To allow easy comparison, we also use the weighted average AUPRC to evaluate zero-shot scores, even though it is not strictly necessary\", and the global-AUPRC version is reported separately in Supplementary Figure S7. All 100 cells match the values here and were reconciled rather than re-extracted, in data/omics/traitgym-20261116; the paper source is linked with companion_of.",
    HF_LIMS_OLD[2],
]

CONFIGS = [
    ("absllr-plus-score", "GPN_final_absLLR.plus.score"),
    ("embeddings-minus-inner-product", "GPN_final_Embeddings.minus.inner_product"),
    ("embeddings-plus-cosine-distance", "GPN_final_Embeddings.plus.cosine_distance"),
    ("embeddings-plus-euclidean-distance", "GPN_final_Embeddings.plus.euclidean_distance"),
    ("euclideandistance-plus-score", "GPN_final_EuclideanDistance.plus.score"),
    ("innerproduct-minus-score", "GPN_final_InnerProduct.minus.score"),
    ("llr-minus-score", "GPN_final_LLR.minus.score"),
    ("logisticregression-chrom", "GPN_final.LogisticRegression.chrom"),
]

RELINK_REASON = (
    "The benchmark's GPN_final is the paper's GPN-Promoter, not GPN. Table 2 lists GPN-Promoter "
    "among the benchmarked self-supervised models with reference \"This work\", 152M parameters and "
    "a 512 bp window, and lists no GPN row at all; Section 5 introduces it as \"a new gLM, called "
    "GPN-Promoter, trained using the genomes of 434 animal species, following the training "
    "objective of GPN (Benegas et al., 2023) and the ByteNet convolutional architecture\"; "
    "Appendix B.2 and Table S6 give its training set and hyperparameters, and the availability "
    "statement gives its weights as songlab/gpn-animal-promoter. The 10 GPN-Promoter cells of "
    "Table S8 equal the GPN_final_* metric files at three decimal places, which ties the file "
    "prefix to the model. A configuration is compared as the model it configures, so while this "
    "link stood, 14 stored results read as results of GPN, a model this paper never benchmarks."
)


def main() -> int:
    records = [json.loads(line) for line in open(BATCH)]
    assert len(records) == 350, len(records)
    by_id = {r["id"]: r for r in records}

    # 1. amendments inside the batch
    recon = by_id[RECON_ID]
    recon["attributes"]["value"] = RECON_VALUE

    light = by_id[LIGHT_ID]
    light["attributes"]["provenance_note"] = LIGHT_PROVENANCE

    model = by_id[MODEL_ID]
    model["facets"]["method_types"] = ["foundation_model"]

    touched = 0
    for r in records:
        lims = r["attributes"].get("limitations")
        if isinstance(lims, list) and LIGHT_RESULT_OLD in lims:
            r["attributes"]["limitations"] = [LIGHT_RESULT_LIMITATION if x == LIGHT_RESULT_OLD else x
                                              for x in lims]
            touched += 1
    assert touched == 8, touched

    # 2. correction claims
    def claim(cid: str, name: str, desc: str, subject: str, field: str, previous: str, value: str,
              locator: str, note: str, extra: dict | None = None) -> dict:
        attrs = {
            "field": field,
            "previous_value": previous,
            "value": value,
            "source_locator": locator,
            "review": review(note, CLAIM_METHODS),
        }
        if extra:
            attrs.update(extra)
        return {
            "id": cid, "kind": "claim", "name": name, "description": desc,
            "status": "source_checked",
            "facets": {"areas": ["dna-genomes"], "contexts": ["research"]},
            "source_ids": [PAPER],
            "links": [{"relation": "subject", "target_id": subject}],
            "attributes": attrs,
        }

    new: list[dict] = []

    new.append(claim(
        "metadata-correction-traitgym-20261116-hf-metrics-source-limitations",
        "limitations: TraitGym official metrics source",
        "Keeps the previous limitations of the TraitGym metrics source record. The second entry said "
        "the paper's Table S8 was on an unweighted basis, which the paper's Appendix B.4 "
        "contradicts.",
        HF, "attributes.limitations",
        json.dumps(HF_LIMS_OLD), json.dumps(HF_LIMS_NEW),
        "Appendix B.4 (page 24); Section 'Additional metrics' (page 7); Table S8 (page 27)",
        "The claim that the paper's Table S8 is on \"a related but unweighted basis\" is wrong. "
        "Appendix B.4 ends \"To allow easy comparison, we also use the weighted average AUPRC to "
        "evaluate zero-shot scores, even though it is not strictly necessary\", and the main text "
        "puts the global-AUPRC version in Supplementary Figure S7, so the weighted average is the "
        "basis of Table S8 and the global AUPRC is the alternative. The reconciliation then holds: "
        "all 100 Table S8 cells equal the stored weighted values rounded to three decimal places. "
        "The entry mattered because it told a reader the paper's values and the stored values are "
        "not comparable when they are the same numbers. " + RECON_NOTE,
    ))

    new.append(claim(
        "metadata-correction-traitgym-20261116-hf-metrics-source-companion-of",
        "links:companion_of:traitgym-20261116-source-biorxiv-v2: TraitGym official metrics source",
        "Adds the companion_of edge from the TraitGym metrics source to the benchmark's paper, "
        "which the paper's availability statement names as the release of the same work.",
        HF, "links:companion_of:" + PAPER,
        "absent", PAPER,
        "Data, model and code availability (page 15); Table S8 (page 27); Appendix B.4 (page 24)",
        "The paper's availability statement gives the benchmark as "
        "https://huggingface.co/datasets/songlab/TraitGym, the dataset these metric files come "
        "from, and all 100 Table S8 cells equal the stored metric values, so the metrics table and "
        "the paper are one piece of work. companion_of is source to source, is used only for study "
        "grouping and never merges results. Without it the discrepancy rules treat the paper's 132 "
        "results and the metrics table's 156 as two studies, and a verdict these authors reach "
        "once would be counted twice, which is what the rules' split-study report exists to find. "
        "The edge is declared in one direction only, from the companion to the paper, so it has to "
        "go on the stored record. " + RECON_NOTE,
        {"target_id": PAPER},
    ))

    new.append(claim(
        "metadata-correction-traitgym-20261116-benchmark-source-ids",
        "source_ids: TraitGym benchmark",
        "Adds the benchmark's own paper to the TraitGym benchmark record's source_ids, which held "
        "only the Hugging Face metrics table.",
        BENCH, "source_ids",
        json.dumps([HF]), json.dumps([HF, PAPER]),
        "Abstract and Section 2 (page 3); Table 1 (page 4); Appendices A.1 to A.4 (pages 19 to 22)",
        "The benchmark record described the suite from a metrics table: its version is a Hugging "
        "Face revision and its scope_note the paths of the metric files. The paper is where the "
        "datasets, the matching, the splits, the allowed inputs, the metric and the leakage "
        "controls are defined, and 21 claims this batch adds carry that definition with the "
        "benchmark as their subject. A benchmark record holds no measurement, so adding a second "
        "source to it does not duplicate a value the way adding one to a result would. version and "
        "scope_note were left as they are: they correctly describe the pinned metric files the 156 "
        "stored results were read from.",
    ))

    for slug, fname in CONFIGS:
        cid = f"lit-genomics-20261011-traitgym-config-gpn-final-{slug}"
        new.append(claim(
            f"metadata-correction-traitgym-20261116-config-gpn-final-{slug}",
            f"links:configuration_of:{MODEL_ID}: {fname} (TraitGym)",
            f"The TraitGym scoring configuration {fname} is a configuration of GPN-Promoter, the "
            "model this paper introduces, not of GPN. Keeps the previous link.",
            cid, "links:configuration_of:" + MODEL_ID,
            GPN, MODEL_ID,
            "Section 5 'Models' (page 8); Table 2 (page 8); Appendix B.2 and Table S6 (page 22); "
            "Table S8 (page 27); Data, model and code availability (page 15)",
            RELINK_REASON + " No family or variant_of edge was added from GPN-Promoter to GPN: a "
            "configuration resolves through configuration_of, then family, then alias_of, so a "
            "family edge would send these configurations back to GPN and undo the relink, and the "
            "paper says only that GPN-Promoter follows GPN's training objective and the ByteNet "
            "architecture, which is not a shared checkpoint.",
            {"target_id": MODEL_ID},
        ))

    assert len(new) == 11, len(new)
    have = {r["id"] for r in records}
    records = [r for r in records if r["id"] not in {n["id"] for n in new}]
    records += [n for n in new]

    # 3. review block on every record
    for r in records:
        if r["id"].startswith("metadata-correction-"):
            continue
        kind = r["kind"]
        if kind == "result":
            r["attributes"]["review"] = review(NOTE_RESULT, RESULT_METHODS)
        elif kind == "evaluation":
            r["attributes"]["review"] = review(NOTE_EVAL, RESULT_METHODS)
        elif kind == "claim":
            note = NOTE_CLAIM + (" " + RECON_NOTE if r["id"] == RECON_ID else "")
            r["attributes"]["review"] = review(note, CLAIM_METHODS)
        elif kind == "source":
            r["attributes"]["review"] = review(NOTE_SOURCE,
                                               ["source-hash-verification", "scope-review"])
        else:
            r["attributes"]["review"] = review(NOTE_ENTITY, ENTITY_METHODS)

    with open(BATCH, "w") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"wrote {len(records)} records ({len(records) - len(have)} new), "
          f"{touched} ensemble limitations amended")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
