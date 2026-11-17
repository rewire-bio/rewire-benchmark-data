#!/usr/bin/env python3
"""Build data/omics/traitgym-20261116/batch.jsonl from the parsed TraitGym tables.

Reads the TSVs written by extract/parse_tables.py and emits the batch records: the
paper source, the GPN-Promoter model the paper introduces, the systems, trait subsets
and protocols the paper's printed tables need, one evaluation and one result per
printed cell, and the descriptive claims that put the benchmark's definition on the
paper rather than on its metrics table.

Table S8 is deliberately not re-extracted as results: its 100 cells are the same
measurements as 100 results already in the store, printed to three decimal places
instead of full precision. extract/compare_s8.py reconciles them and the outcome is
recorded as one claim.

Usage: python3 extract/build.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
BATCH = HERE.parent
PREFIX = "traitgym-20261116"

SOURCE = f"{PREFIX}-source-biorxiv-v2"
PAPER_URL = "https://www.biorxiv.org/content/10.1101/2025.02.11.637758v2.full.pdf"
PDF_SHA256 = "80426c499e0b498e07c07ea598a2f68049adea7569b30fda58cdc0ebafa6c7aa"
TEXT_SHA256 = "23ae4d67751f1092e5cc2da66b52091fa9bbc3ec59310f06bc65be28f93c5097"
RETRIEVED_AT = "2026-11-16T01:09:36Z"
DATE = "2026-11-16"

# Records already in the store, reused rather than created again.
BENCHMARK = "lit-genomics-20261011-traitgym-benchmark-traitgym"
DATA = {"Mendelian traits": "lit-genomics-20261011-traitgym-data-mendelian-traits-matched-9",
        "Complex traits": "lit-genomics-20261011-traitgym-data-complex-traits-matched-9"}
MODEL_BORZOI = "regulatory-variant-20261009-model-borzoi"
MODEL_GPN_MSA = "gfm-guides-20261014-gpnmsa-model-gpn-msa"
METHOD_CADD = "somatic-oncogenicity-20261009-method-cadd"
METHOD_FULL_ENSEMBLE = (
    "lit-genomics-20261011-traitgym-method-cadd-plus-gpn-msa-plus-borzoi-logistic-regression")
METHOD_LIGHT_ENSEMBLE = f"{PREFIX}-method-lightweight-ensemble"
MODEL_GPN_PROMOTER = f"{PREFIX}-model-gpn-promoter"

DATASET_KEY = {"Mendelian traits": "mendelian", "Complex traits": "complex"}
FACETS = {"areas": ["dna-genomes"], "contexts": ["research"]}

TABLE_PAGE = {"Table 1": 4, "Table 2": 6, "Table 3": 7, "Table 4": 12, "Table 5": 13,
              "Table S1": 20, "Table S2": 20, "Table S3": 20, "Table S4": 22, "Table S5": 23,
              "Table S6": 23, "Table S7": 26, "Table S8": 27, "Table S9": 27,
              "Table S10": 28, "Table S11": 28}


def slug(text: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-+", "-", out)


def read(name: str) -> list[dict[str, str]]:
    with (HERE / f"{name}.tsv").open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def review(method: list[str], method_note: str, note: str) -> dict:
    return {
        "method": method,
        "method_note": method_note,
        "reviewer": ["claude"],
        "reviewer_note": ("Claude extraction agent; no human review claimed. Independent "
                          "review by review-evidence has not been done."),
        "date": DATE,
        "artifact_sha256": PDF_SHA256,
        "retrieval_url": PAPER_URL,
        "note": note,
    }


PARSE_NOTE = (
    "Extraction: data/omics/traitgym-20261116/extract/parse_tables.py reads the pdftotext "
    "-layout text layer of the pinned PDF, asserts the table's column headers, row labels and "
    "cell count, and writes the cells to extract/<table>.tsv; data/omics/traitgym-20261116/"
    "extract/build.py turns each cell into one evaluation and one result. The repository's own "
    "reader, npm run batch -- table, independently reproduced Tables 1, S8 and S10 in full from "
    "the same text layer, and all 104 values of Table S11, where it mis-splits the row label of "
    "the two longest trait names. Sign-off is left to review-evidence."
)
CLAIM_NOTE = (
    "Transcribed by hand from the pinned PDF's text layer at the locator given; numbers quoted "
    "from a table were taken from extract/<table>.tsv, which parse_tables.py produced with its "
    "row labels asserted. Sign-off is left to review-evidence."
)

RESULT_REVIEW = review(
    ["deterministic-table-parse", "pdf-text-parse"],
    "Scripted parse of the printed table in the PDF text layer, with the expected row labels, "
    "column headers and cell count asserted.",
    PARSE_NOTE)
CLAIM_REVIEW = review(
    ["transcription", "pdf-text-parse"],
    "Read against the pinned PDF's text layer at the locator given.",
    CLAIM_NOTE)


def record(rid: str, kind: str, name: str, description: str, attributes: dict,
           links: list[dict] | None = None, facets: dict | None = None) -> dict:
    return {
        "id": rid,
        "kind": kind,
        "name": name,
        "description": description,
        "status": "source_checked",
        "facets": FACETS if facets is None else facets,
        "source_ids": [SOURCE],
        "links": links or [],
        "attributes": attributes,
    }


records: list[dict] = []


# ------------------------------------------------------------------ source

records.append({
    "id": SOURCE,
    "kind": "source",
    "name": "Benegas, Eraslan and Song 2025, TraitGym benchmark preprint (bioRxiv v2)",
    "description": "Primary source retrieved and hashed for the 2026-11-16 GPN-family pass.",
    "status": "source_checked",
    "facets": FACETS,
    "source_ids": [],
    "links": [],
    "attributes": {
        "url": "https://www.biorxiv.org/content/10.1101/2025.02.11.637758v2",
        "artifact_url": PAPER_URL,
        "doi": "10.1101/2025.02.11.637758",
        "version": "bioRxiv version 2, posted 2025-03-04 (37 pages, main text and Supplementary Material)",
        "version_note": ("The bioRxiv API lists two versions, v1 of 2025-02-12 and v2 of "
                         "2025-03-04, and no published version. PubMed (39990426), Europe PMC "
                         "(PPR978187) and Crossref hold the preprint only, and a Crossref title "
                         "search and a PubMed author search for Benegas G on 2026-11-16 returned "
                         "no journal article of this work. The preprint is the version of record."),
        "retrieved_at": RETRIEVED_AT,
        "artifact_sha256": PDF_SHA256,
        "publication_status": "preprint",
        "licence": "CC BY-NC-ND 4.0",
        "media_type": "application/pdf",
        "hash_scope": ("SHA-256 of the PDF bytes of one download. bioRxiv stamps each download, "
                       "so this hash pins this retrieval and not the document: a second download "
                       "in the same session gave "
                       "5f424797ed5c92a3852a52e8ecf29f0c3a3416740a47fe9f9fefe9fd9fb0c876. The "
                       "stable check is the pdftotext -layout text layer, whose SHA-256 is "
                       f"{TEXT_SHA256} and was byte-identical across both downloads; every value "
                       "in this batch was read from that text layer."),
        "retrieval_note": ("Downloaded with curl from the v2 full-PDF URL. The supplementary "
                           "material is part of the same PDF (pages 19 to 37); bioRxiv lists no "
                           "separate supplementary file for this preprint."),
        "limitations": [
            "Not peer reviewed.",
            "The benchmark's authors developed GPN-MSA and GPN-Promoter, so their rows are author_reported.",
            "The headline comparisons are Figures 5 to 10 and Figures S1 to S11, which print no values, and no source data file is published for them.",
        ],
        "review": review(["source-hash-verification"],
                         "Re-downloaded once in the same session. The PDF bytes differ between "
                         "downloads, as bioRxiv stamps them; the pdftotext -layout text layer was "
                         "byte-identical, and that is what the values were read from.",
                         "Retrieval and hashing by the extraction agent; sign-off is left to "
                         "review-evidence."),
    },
})


# ------------------------------------------------------------------ GPN-Promoter

t2 = {row["model"]: row for row in read("table-2")}
t5_hub = {row["model"]: row["hub_path"] for row in read("table-s5")}
s6 = {row["hyperparameter"]: row["value"] for row in read("table-s6")}

records.append(record(
    MODEL_GPN_PROMOTER, "model", "GPN-Promoter",
    "Masked DNA language model trained on 512-bp windows centred on the transcription start "
    "sites of protein-coding genes in 434 animal reference genomes, scoring variants from the "
    "log-likelihood ratio between alleles or from embedding similarity.",
    {
        "entity_level": "family",
        "version": "GPN-Promoter as introduced in this preprint",
        "reported_name": "GPN-Promoter",
        "access": "Public weights at https://huggingface.co/songlab/gpn-animal-promoter",
        "training_data": "Promoters (512 bp around the TSS of protein-coding genes) of 434 animal "
                         "reference genomes from NCBI Datasets, subsampled to at most one species "
                         "per family; training dataset at "
                         "https://huggingface.co/datasets/songlab/gpn-animal-promoter-dataset",
        "provenance_note": "Introduced by this paper (Table 2 'This work'); registered here because "
                           "the store held TraitGym's GPN-Promoter scoring configurations under the "
                           "GPN model record with no record of GPN-Promoter itself.",
        "source_locator": "Section 5 'Models', Appendix B.2, Table 2 and Table S6",
        "missing_metadata": {
            "licence": {"reason": "unreported",
                        "note": "The paper gives the Hugging Face path but states no licence."},
        },
        "review": CLAIM_REVIEW,
    }))


# ------------------------------------------------------------------ systems

records.append(record(
    METHOD_LIGHT_ENSEMBLE, "method",
    "Lightweight feature ensemble: CADD input features with GPN-MSA LLR and Borzoi l2-of-l2",
    "Ridge logistic regression on the full set of CADD input features together with a much "
    "reduced set of features from other models, the GPN-MSA log-likelihood ratio and the Borzoi "
    "l2-of-l2 score.",
    {
        "entity_level": "method",
        "reported_name": "CADD+GPN-MSA_LLR+Borzoi_L2_L2",
        "parameters": "Ridge logistic regression over 114 CADD input features, the GPN-MSA LLR and "
                      "the Borzoi l2 of l2 scores; leave-one-chromosome-out",
        "provenance_note": "Named in Figure 8 as the best lightweight ensemble and used as the "
                           "Mendelian 'Ensemble' column of Table S11, which does not name which "
                           "lightweight ensemble it is.",
        "source_locator": "Section 6 'Model ensembling' and Figure 8 (page 10); Table S11 caption (page 28)",
        "review": CLAIM_REVIEW,
    }))

# Table 4: single CADD input features used directly as a score.
CADD_FEATURES = {
    "ZooVerPhyloP": ("phyloP conservation score for 241 mammals from Zoonomia, as distributed in "
                     "the CADD v1.7 annotation bundle, used directly as a variant score.",
                     "Conservation in mammals"),
    "EncodetotalRNA-max": ("Maximum ENCODE total RNA-seq level at the variant, as distributed in "
                           "the CADD v1.7 annotation bundle, used directly as a variant score.",
                           "Max. RNA-seq level"),
    "(-) Freq100bp": ("Negated count of common variants within 100 bp of the variant, as "
                      "distributed in the CADD v1.7 annotation bundle, used directly as a variant score.",
                      "# common variants within 100bp"),
    "ZooPriPhyloP": ("phastCons conservation score for 43 primates from Zoonomia, as distributed in "
                     "the CADD v1.7 annotation bundle under a name the paper calls misleading, used "
                     "directly as a variant score.",
                     "Conservation in primates"),
    "EncodeDNase-max": ("Maximum ENCODE DNase-seq level at the variant, as distributed in the CADD "
                        "v1.7 annotation bundle, used directly as a variant score.",
                        "Max. DNase-seq level"),
    "(-) Freq10000bp": ("Negated count of common variants within 10 kb of the variant, as "
                        "distributed in the CADD v1.7 annotation bundle, used directly as a variant score.",
                        "# common variants within 10kb"),
}
CADD_FEATURE_IDS = {name: f"{PREFIX}-method-cadd-feature-{slug(name)}" for name in CADD_FEATURES}

for feature, (description, printed) in CADD_FEATURES.items():
    records.append(record(
        CADD_FEATURE_IDS[feature], "method", f"CADD input feature {feature}", description,
        {
            "entity_level": "method",
            "reported_name": feature,
            "version": "CADD v1.7 annotation bundle (whole_genome_SNVs_inclAnno.tsv.gz, GRCh38)",
            "parameters": f"Single CADD input feature, described in Table 4 as '{printed}'",
            "provenance_note": "One of the top CADD input features per category in Table 4; the "
                               "value is the feature's own AUPRC, not CADD's.",
            "identity_scope": "The feature as distributed in the CADD v1.7 annotation bundle, not "
                              "the conservation score files the paper downloads separately "
                              "(phyloP-241m, phastCons-43p), whose AUPRCs on this benchmark "
                              "differ. The paper notes that the official CADD names ZooVerPhyloP "
                              "and ZooPriPhyloP are misleading and respectively hold mammalian "
                              "phyloP and primate phastCons from Zoonomia.",
            "source_locator": f"Table 4, row \"{feature}\" (page 12); Appendix B.1 for the CADD version",
            "review": CLAIM_REVIEW,
        }))

# Table S4: the features the controls were matched on, used as scores.
MATCHED_FEATURES = {
    "(-) TSS distance": ("Negated distance from the variant to the nearest protein-coding "
                         "transcription start site, used directly as a variant score.",),
    "MAF": ("UK Biobank minor allele frequency of the variant, used directly as a variant score.",),
    "(-) LD score": ("Negated UK Biobank linkage disequilibrium score of the variant, used "
                     "directly as a variant score.",),
}
MATCHED_FEATURE_IDS = {name: f"{PREFIX}-method-matched-feature-{slug(name)}"
                       for name in MATCHED_FEATURES}

for feature, (description,) in MATCHED_FEATURES.items():
    records.append(record(
        MATCHED_FEATURE_IDS[feature], "method", f"TraitGym matched feature {feature}", description,
        {
            "entity_level": "method",
            "reported_name": feature,
            "parameters": "Single matching feature used as the score; no model",
            "provenance_note": "Scored in Table S4 to show that the features the controls were "
                               "matched on carry almost no predictive power.",
            "source_locator": f"Table S4, row \"{feature}\" (page 22); Appendix A.4",
            "review": CLAIM_REVIEW,
        }))

# Table 5: Borzoi predicted tracks restricted to one tissue, cell type or cell line.
t5 = read("table-5")
TISSUES = list(dict.fromkeys(row["tissue"] for row in t5))
TISSUE_IDS = {t: f"{PREFIX}-config-borzoi-tracks-{slug(t)}" for t in TISSUES}

for tissue in TISSUES:
    records.append(record(
        TISSUE_IDS[tissue], "configuration", f"Borzoi predicted tracks from {tissue} (TraitGym)",
        f"Borzoi variant scoring restricted to its predicted tracks from {tissue}, scored as the "
        "l2 norm of the predicted log-fold-change in activity between the reference and alternate "
        "sequences.",
        {
            "reported_name": tissue,
            "configuration_type": "paper_evaluation",
            "foundation_model_eligible": False,
            "parameters": f"Borzoi predicted tracks whose tissue, cell type or cell line is {tissue}",
            "access_reuse": "Borzoi downloaded from gReLU's Model Zoo (paper Appendix B.1)",
            "version": "Borzoi as distributed by gReLU's Model Zoo",
            "source_locator": f"Table 5, rows with tissue \"{tissue}\" (page 13)",
            "limitations": [
                "Table 5 reports the highest AUPRC among the tracks from this tissue and does not "
                "name the track, so the configuration is the tissue, not a single track.",
            ],
            "review": CLAIM_REVIEW,
        },
        links=[{"relation": "configuration_of", "target_id": MODEL_BORZOI}],
        facets={"areas": ["dna-genomes"], "contexts": ["research"],
                "method_types": ["supervised_machine_learning"]}))


# ------------------------------------------------------------------ trait subsets

s11 = read("table-s11")
TRAITS: dict[str, str] = {}  # trait -> dataset label
for row in s11:
    TRAITS.setdefault(row["trait"], row["dataset"])
for row in t5:
    assert row["trait"] in TRAITS, f"Table 5 trait not in Table S11: {row['trait']}"

SUBSET_IDS = {trait: f"{PREFIX}-subset-{DATASET_KEY[ds]}-{slug(trait)}"
              for trait, ds in TRAITS.items()}


# ------------------------------------------------------------------ protocols

PROTOCOLS: dict[tuple[str, str], str] = {}


def add_protocol(key: str, dataset: str, name: str, description: str, attributes: dict,
                 data_links: list[str]) -> str:
    pid = f"{PREFIX}-protocol-{DATASET_KEY[dataset]}-{key}"
    PROTOCOLS[(key, dataset)] = pid
    links = [{"relation": "part_of", "target_id": BENCHMARK}]
    links += [{"relation": "uses_data", "target_id": d} for d in data_links]
    records.append(record(pid, "protocol", name, description, attributes, links=links))
    return pid


COMMON_PROTOCOL = {
    "metric": "auprc",
    "metric_direction": "higher",
    "unit": "unitless",
    "version": "bioRxiv v2 preprint, 2025-03-04",
    "allowed_information": "The reference and alternate allele with the surrounding DNA sequence "
                           "context (Section 4 'Task definition').",
}

for dataset in ("Mendelian traits", "Complex traits"):
    key = DATASET_KEY[dataset]
    traits = [t for t, ds in TRAITS.items() if ds == dataset]
    ensemble = "lightweight feature ensemble" if dataset == "Mendelian traits" else "full feature ensemble"
    add_protocol(
        "per-trait-best-of-zero-shot-and-linear-probing", dataset,
        f"TraitGym {dataset} per trait, AUPRC, best of zero-shot and linear probing",
        f"AUPRC on the causal and matched control variants of one {dataset.lower()} trait, "
        f"reporting for each system the better of its zero-shot and its linear probing score, with "
        f"the {ensemble} standing for the ensemble.",
        dict(COMMON_PROTOCOL,
             protocol=(f"Traits with at least 10 causal variants and less than 10 per cent overlap "
                       f"of causal variants with other traits. For each system the better of its "
                       f"zero-shot and its linear probing score is reported. The ensemble column is "
                       f"the {ensemble}."),
             metric_qualifier="best of zero-shot and linear probing; single trait; chromosome aggregation unreported",
             selection="The better of the zero-shot and the linear probing score, per cell",
             selection_bias=("Both the choice between zero-shot and linear probing and, for the "
                             "ensemble, the choice of feature set are made on the same variants the "
                             "score is reported on."),
             source_locator=f"Table S11, {dataset} block (page 28)",
             limitations=[
                 "The table does not say, for any cell, whether the printed value is the zero-shot "
                 "or the linear probing score.",
                 "Whether the per-trait AUPRC is the chromosome-weighted average or a global AUPRC "
                 "is not stated.",
                 "Trait selection depends on the causal variant counts, which the table does not print.",
             ],
             missing_metadata={
                 "metric_implementation": {"reason": "unreported",
                                           "note": "The basis of the per-trait AUPRC is not stated."},
                 "aggregation": {"reason": "unreported"},
             },
             review=CLAIM_REVIEW),
        [DATA[dataset]] + [SUBSET_IDS[t] for t in traits])

    add_protocol(
        "single-cadd-input-feature-auprc", dataset,
        f"TraitGym {dataset}, AUPRC of a single CADD input feature",
        f"AUPRC on the {dataset.lower()} dataset of one CADD input feature used directly as the "
        "variant score, reported for the top feature in each of three feature categories.",
        dict(COMMON_PROTOCOL,
             protocol="One CADD input feature is used as the score. The paper reports the top "
                      "feature in each of three categories: alignment, functional genomics and "
                      "population data.",
             metric_qualifier="single CADD input feature as the score; chromosome aggregation unreported",
             source_locator=f"Table 4, {dataset} rows (page 12)",
             limitations=[
                 "Whether these AUPRCs are the chromosome-weighted average or a global AUPRC is not stated.",
                 "The features are the top ones in their category, so they are selected on the same "
                 "variants the AUPRC is reported on.",
             ],
             missing_metadata={
                 "metric_implementation": {"reason": "unreported"},
                 "aggregation": {"reason": "unreported"},
             },
             review=CLAIM_REVIEW),
        [DATA[dataset]])

    add_protocol(
        "matched-feature-global-auprc", dataset,
        f"TraitGym {dataset}, global AUPRC of a matching feature",
        f"Global AUPRC on the {dataset.lower()} dataset of one of the features the control "
        "variants were matched on, used directly as the variant score, as a check that matching "
        "left the features with almost no predictive power.",
        dict(COMMON_PROTOCOL,
             protocol="One matching feature is used as the score and a single global AUPRC is "
                      "computed over all variants of the dataset.",
             metric_qualifier="global AUPRC over all variants; single matching feature as the score",
             metric_implementation="Global AUPRC (Table S4 caption), not the weighted average over chromosomes",
             control="The baseline AUPRC is 0.1, the proportion of positives; the caption states "
                     "these values are close to it.",
             aggregation="None; one global AUPRC over all variants",
             source_locator=f"Table S4, {dataset} rows (page 22)",
             review=CLAIM_REVIEW),
        [DATA[dataset]])

for dataset in ("Mendelian traits", "Complex traits"):
    traits = [row["trait"] for row in t5 if row["dataset"] == dataset]
    add_protocol(
        "per-trait-best-borzoi-tissue-track-auprc", dataset,
        f"TraitGym {dataset} per trait, highest AUPRC among Borzoi tracks from one tissue",
        f"AUPRC on the causal and matched control variants of one {dataset.lower()} trait, taking "
        "for each tissue, cell type or cell line the highest AUPRC among the Borzoi predicted "
        "tracks from it.",
        dict(COMMON_PROTOCOL,
             protocol="For each trait, the tissue, cell type or cell line of the Borzoi predicted "
                      "tracks is ranked by the highest AUPRC of a track from it, and the top three "
                      "are reported.",
             metric_qualifier="highest AUPRC among the Borzoi tracks from one tissue; single trait; "
                              "chromosome aggregation unreported",
             selection="The highest-scoring Borzoi track from the tissue, on the trait's own variants",
             selection_bias="Both the track and the top three tissues are selected on the same "
                            "variants the AUPRC is reported on.",
             source_locator=f"Table 5, {dataset} block (page 13)",
             limitations=[
                 "The table does not name the track behind each value, only its tissue, cell type "
                 "or cell line.",
                 "Whether the value is a single track's AUPRC or an aggregate over the tissue's "
                 "tracks is stated only as 'the highest AUPRC of Borzoi predicted tracks from such "
                 "tissue/cell type'.",
                 "Whether it is the chromosome-weighted average or a global AUPRC is not stated.",
                 "Only traits on which Borzoi did well are reported.",
             ],
             missing_metadata={
                 "metric_implementation": {"reason": "unreported"},
                 "aggregation": {"reason": "unreported"},
             },
             review=CLAIM_REVIEW),
        [DATA[dataset]] + [SUBSET_IDS[t] for t in dict.fromkeys(traits)])


# ------------------------------------------------------------------ subsets

for trait, dataset in TRAITS.items():
    used_in = [PROTOCOLS[("per-trait-best-of-zero-shot-and-linear-probing", dataset)]]
    if any(row["trait"] == trait for row in t5):
        used_in.append(PROTOCOLS[("per-trait-best-borzoi-tissue-track-auprc", dataset)])
    locators = [f"Table S11, row \"{trait}\" (page 28)"]
    if len(used_in) > 1:
        locators.append(f"Table 5, trait \"{trait}\" (page 13)")
    records.append(record(
        SUBSET_IDS[trait], "dataset_subset", f"TraitGym {dataset}: {trait}",
        f"The TraitGym {dataset.lower()} causal variants of {trait} with their nine matched "
        "control variants each.",
        {
            "version": "bioRxiv v2 preprint, 2025-03-04",
            "subset_scope": f"Variants of the single trait {trait}",
            "source_locator": "; ".join(locators),
            "limitations": [
                "The trait's variant counts are not printed; the paper states only that a reported "
                "trait has at least 10 causal variants and less than 10 per cent overlap of causal "
                "variants with other traits.",
            ],
            "missing_metadata": {
                "positive_count": {"reason": "unreported"},
                "test_count": {"reason": "unreported"},
            },
            "review": CLAIM_REVIEW,
        },
        links=[{"relation": "same_data_as", "target_id": DATA[dataset]}]
              + [{"relation": "used_in", "target_id": p} for p in used_in]))


# ------------------------------------------------------------------ results

def comparison(protocol_id: str, split: str, population: str, adaptation: str,
               metric_implementation: str | None, aggregation: str | None) -> dict:
    return {
        "protocol_id": protocol_id,
        "dataset_version": "bioRxiv v2 preprint, 2025-03-04",
        "split": split,
        "population": population,
        "inputs": "Reference and alternate allele with DNA sequence context",
        "adaptation": adaptation,
        "metric_implementation": metric_implementation,
        "aggregation": aggregation,
        "budget": None,
    }


def add_result(rid: str, system: str, protocol_id: str, data_id: str, eval_name: str,
               result_name: str, printed: str, locator: str, qualifier: str,
               comparison_object: dict, eval_missing: dict, result_limitations: list[str] | None,
               result_note: str | None, eval_extra: dict | None = None) -> None:
    eid = f"{PREFIX}-eval-{rid}"
    records.append(record(
        eid, "evaluation", eval_name,
        "Published comparison transcribed from the pinned source; not reproduced.",
        {
            "origin": "author_reported",
            "protocol": protocol_id,
            "version": "bioRxiv v2 preprint, 2025-03-04",
            "comparison": comparison_object,
            "source_locator": locator,
            "missing_metadata": eval_missing,
            **(eval_extra or {}),
        },
        links=[{"relation": "system", "target_id": system},
               {"relation": "assessment", "target_id": protocol_id},
               {"relation": "data", "target_id": data_id}]))
    attributes = {
        "metric": "auprc",
        "metric_direction": "higher",
        "metric_qualifier": qualifier,
        "unit": "unitless",
        "printed_value": printed,
        "numeric_value": printed,
        "printed_value_basis": "Value as printed in the table, at the paper's rounding",
        "source_locator": locator,
        "missing_metadata": {"uncertainty": {
            "reason": "unreported",
            "note": "The table prints no standard error; the bootstrap errors of Appendix B.4 are "
                    "reported only in the figures.",
        }},
        "review": dict(RESULT_REVIEW, note=(RESULT_REVIEW["note"] if result_note is None
                                            else f"{result_note} {RESULT_REVIEW['note']}")),
    }
    if result_limitations:
        attributes["limitations"] = result_limitations
    records.append(record(
        f"{PREFIX}-result-{rid}", "result", result_name,
        "Reported measurement transcribed from the pinned source. Not independently reproduced.",
        attributes,
        links=[{"relation": "evaluation", "target_id": eid}],
        facets={}))


# Table S11: per trait, best of zero-shot and linear probing.
S11_SYSTEMS = {
    "Borzoi": lambda dataset: MODEL_BORZOI,
    "GPN-MSA": lambda dataset: MODEL_GPN_MSA,
    "CADD": lambda dataset: METHOD_CADD,
    "Ensemble": lambda dataset: (METHOD_LIGHT_ENSEMBLE if dataset == "Mendelian traits"
                                 else METHOD_FULL_ENSEMBLE),
}
# The paper names the version of each system in Appendix B.1; the reused model and method
# records are version-free family records, so the version is carried on the evaluation.
S11_VERSIONS = {
    "Borzoi": {"model_version": "Borzoi as distributed by gReLU's Model Zoo (Appendix B.1)"},
    "GPN-MSA": {"model_version": "songlab/gpn-msa-sapiens (Table S5)"},
    "CADD": {"model_version": "CADD v1.7, GRCh38 whole_genome_SNVs_inclAnno (Appendix B.1)"},
}
for row in s11:
    dataset, trait, column, value = row["dataset"], row["trait"], row["system"], row["auprc"]
    protocol_id = PROTOCOLS[("per-trait-best-of-zero-shot-and-linear-probing", dataset)]
    ensemble = "lightweight" if dataset == "Mendelian traits" else "full"
    add_result(
        f"s11-{DATASET_KEY[dataset]}-{slug(trait)}-{slug(column)}",
        S11_SYSTEMS[column](dataset), protocol_id, SUBSET_IDS[trait],
        f"{column} on TraitGym {dataset}, trait {trait}",
        f"{column} TraitGym {dataset} {trait} AUPRC",
        value, f"Table S11, row \"{trait}\", column \"{column}\" (page 28)",
        "best of zero-shot and linear probing; single trait; chromosome aggregation unreported",
        comparison(protocol_id,
                   "Leave-one-chromosome-out for linear probing; all variants scored for zero-shot",
                   f"Causal and matched control variants of {trait} only",
                   "Best of zero-shot and linear probing; which one is not stated per cell",
                   None, None),
        {"comparison.metric_implementation": {"reason": "unreported"},
         "comparison.aggregation": {"reason": "unreported"},
         "comparison.budget": {"reason": "unreported"}},
        ["Whether this cell is the zero-shot or the linear probing score is not stated."]
        + ([f"The ensemble is the {ensemble} feature ensemble (Table S11 caption); for Mendelian "
            "traits the caption does not say which lightweight ensemble."]
           if column == "Ensemble" else []),
        None, S11_VERSIONS.get(column))

# Table 4: single CADD input features.
for row in read("table-4"):
    dataset, feature, value = row["dataset"], row["feature"], row["auprc"]
    protocol_id = PROTOCOLS[("single-cadd-input-feature-auprc", dataset)]
    add_result(
        f"t4-{DATASET_KEY[dataset]}-{slug(feature)}",
        CADD_FEATURE_IDS[feature], protocol_id, DATA[dataset],
        f"CADD input feature {feature} on TraitGym {dataset}",
        f"CADD input feature {feature} TraitGym {dataset} AUPRC",
        value, f"Table 4, row \"{feature}\", column \"AUPRC\" (page 12)",
        "single CADD input feature as the score; chromosome aggregation unreported",
        comparison(protocol_id, "All variants", None,
                   "Single CADD input feature used directly as the score", None, None),
        {"comparison.metric_implementation": {"reason": "unreported"},
         "comparison.aggregation": {"reason": "unreported"},
         "comparison.population": {"reason": "inapplicable"},
         "comparison.budget": {"reason": "unreported"}},
        [f"The feature is the top one in the {row['category'].lower()} category, selected on the "
         "same variants the AUPRC is reported on."],
        None,
        {"model_version": "CADD v1.7, GRCh38 whole_genome_SNVs_inclAnno (Appendix B.1)"})

# Table 5: Borzoi tracks by tissue, per trait.
for row in t5:
    dataset, trait, tissue, value = row["dataset"], row["trait"], row["tissue"], row["auprc"]
    protocol_id = PROTOCOLS[("per-trait-best-borzoi-tissue-track-auprc", dataset)]
    add_result(
        f"t5-{DATASET_KEY[dataset]}-{slug(trait)}-{slug(tissue)}",
        TISSUE_IDS[tissue], protocol_id, SUBSET_IDS[trait],
        f"Borzoi tracks from {tissue} on TraitGym {dataset}, trait {trait}",
        f"Borzoi {tissue} tracks TraitGym {dataset} {trait} AUPRC",
        value, f"Table 5, trait \"{trait}\", row \"{tissue}\", column \"AUPRC\" (page 13)",
        "highest AUPRC among the Borzoi tracks from one tissue; single trait; chromosome "
        "aggregation unreported",
        comparison(protocol_id, "All variants of the trait",
                   f"Causal and matched control variants of {trait} only",
                   "Highest-scoring Borzoi predicted track from this tissue, cell type or cell line",
                   None, None),
        {"comparison.metric_implementation": {"reason": "unreported"},
         "comparison.aggregation": {"reason": "unreported"},
         "comparison.budget": {"reason": "unreported"}},
        [f"The value is the highest AUPRC among the Borzoi tracks from {tissue}; the track is not named.",
         f"This tissue is one of the top three for {trait}, ranked on the same variants."],
        f"This cell is rank {row['rank']} of three for this trait.")

# Table S4: matched features, global AUPRC.
for row in read("table-s4"):
    dataset, feature, value = row["dataset"], row["feature"], row["auprc"]
    protocol_id = PROTOCOLS[("matched-feature-global-auprc", dataset)]
    add_result(
        f"s4-{DATASET_KEY[dataset]}-{slug(feature)}",
        MATCHED_FEATURE_IDS[feature], protocol_id, DATA[dataset],
        f"Matched feature {feature} on TraitGym {dataset}",
        f"Matched feature {feature} TraitGym {dataset} global AUPRC",
        value,
        f"Table S4, {dataset} row \"{feature}\", column \"AUPRC\" (page 22)",
        "global AUPRC over all variants; single matching feature as the score",
        comparison(protocol_id, "All variants", None,
                   "Single matching feature used directly as the score",
                   "Global AUPRC (Table S4 caption)", "None; one global AUPRC over all variants"),
        {"comparison.population": {"reason": "inapplicable"},
         "comparison.budget": {"reason": "unreported"}},
        ["The baseline AUPRC is 0.1, the proportion of positives."],
        "The caption states these matched features are close to the 0.1 baseline, as intended.")


# ------------------------------------------------------------------ claims

t1 = {row["dataset"]: row for row in read("table-1")}
s9 = read("table-s9")
s10 = {row["set"]: row for row in read("table-s10")}


def add_claim(field: str, subject: str, subject_name: str, value: str, locator: str) -> None:
    records.append(record(
        f"{PREFIX}-claim-{slug(field)}", "claim", f"{field}: {subject_name}",
        "Descriptive fact transcribed from the pinned source.",
        {"field": field, "value": value, "source_locator": locator, "review": CLAIM_REVIEW},
        links=[{"relation": "subject", "target_id": subject}],
        facets={}))


B = (BENCHMARK, "TraitGym")
G = (MODEL_GPN_PROMOTER, "GPN-Promoter")

add_claim("paper_of_record", *B,
          "The benchmark is defined by Gonzalo Benegas, Gokcen Eraslan and Yun S. Song, "
          "'Benchmarking DNA Sequence Models for Causal Regulatory Variant Prediction in Human "
          "Genetics', bioRxiv 10.1101/2025.02.11.637758, version 2 dated 4 March 2025, released "
          "under CC BY-NC-ND 4.0 and not certified by peer review.",
          "Title page and bioRxiv stamp (page 1)")

add_claim("dataset_counts", *B,
          f"Mendelian traits: {t1['Mendelian traits']['causal_variants']} putatively causal "
          f"variants, {t1['Mendelian traits']['total_variants']} variants in total, across "
          f"{t1['Mendelian traits']['traits']} traits. Complex traits: "
          f"{t1['Complex traits']['causal_variants']} putatively causal variants, "
          f"{t1['Complex traits']['total_variants']} variants in total, across "
          f"{t1['Complex traits']['traits']} traits.",
          "Table 1 (page 4)")

add_claim("mendelian_variant_definition", *B,
          "Curated causal non-coding variants for 113 Mendelian diseases were taken from OMIM via "
          "Table S6 of Smedley et al. (2016), then filtered to minor allele frequency at most 0.1 "
          "per cent in gnomAD version 3.1.2. Controls are gnomAD common variants with minor allele "
          "frequency above 5 per cent.",
          "Section 4 'Mendelian traits' (page 4) and Appendix A.1 (page 20)")

add_claim("complex_variant_definition", *B,
          "Putative causal variants for 83 complex traits come from UK Biobank fine-mapping "
          "(Kanai et al. 2021, data version 3 December 2019): the posterior inclusion probability "
          "was averaged between FINEMAP and SuSiE, variants where the two disagreed by more than 5 "
          "per cent were excluded, positives are variants with averaged probability above 0.9 in "
          "any trait, and positives were further filtered to genome-wide significance p below 5e-8. "
          "Controls are variants with probability below 0.01 in all traits.",
          "Section 4 'Complex traits' (pages 4 to 5) and Appendix A.2 (page 20)")

add_claim("control_matching", *B,
          "Nine control variants are sampled for each putatively causal variant. Chromosome and "
          "consequence are matched exactly; the controls minimise the Euclidean distance to the "
          "positive variant in a robust-scaled space of transcription start site distance, and, for "
          "complex traits, minor allele frequency and UK Biobank linkage disequilibrium score. The "
          "proportion of consequences, including candidate cis-regulatory element categories and "
          "their flanks, is kept identical between positives and controls. Where a chromosome and "
          "consequence had too few controls, positives were subsampled until there were at least "
          "nine controls per positive. The baseline AUPRC is therefore 0.1.",
          "Section 4 'Matching positives and negatives' (page 5) and Appendix A.4 (page 22)")

add_claim("variant_annotation", *B,
          "Consequences were annotated with Ensembl VEP release 109.1 using --most_severe and "
          "--distance 1000, and only non-coding consequences were kept: intergenic, upstream gene, "
          "downstream gene, intron, 5-prime UTR, 3-prime UTR and non-coding transcript exon "
          "variants. Splice region variants and coding variants are excluded. Non-exonic variants "
          "were refined by overlap with five ENCODE candidate cis-regulatory element categories "
          "(PLS, pELS, dELS, DNase-H3K4me3, CTCF-only) and with their 500-bp flanks. For "
          "performance by consequence, non-exonic variants are simplified to proximal (at most 1 kb "
          "from a transcription start site) and distal.",
          "Appendix A.3 with Tables S2 and S3 (pages 20 to 21)")

add_claim("task_definition", *B,
          "The task is to classify whether a variant is putatively causal for any trait or not. "
          "The input data consist of the reference and alternate allele together with the DNA "
          "sequence context.",
          "Section 4 'Task definition' (page 5)")

add_claim("evaluation_metric", *B,
          "The metric is the area under the precision-recall curve, computed for each chromosome "
          "with a model trained on the remaining chromosomes and then averaged across chromosomes "
          "with weights by sample size. The baseline AUPRC is 0.1, the proportion of positives. "
          "Appendix B.4 states that the weighted average AUPRC is used to evaluate zero-shot "
          "scores as well, 'to allow easy comparison', even though it is not strictly necessary "
          "for them. Figure S7 repeats the zero-shot results with a global AUPRC and Figure S6 "
          "with AUROC.",
          "Section 4 'Task definition' (page 5) and Appendix B.4 (page 24)")

add_claim("uncertainty_estimation", *B,
          "For linear probing, the standard error is the standard deviation of the weighted mean "
          "over 1000 bootstrap samples of chromosomes. For zero-shot scores, standard errors come "
          "from 100 bootstrap samples drawn within the positive and the negative set separately, so "
          "as to keep the proportion of positives.",
          "Appendix B.4 (page 24)")

add_claim("linear_probing_protocol", *B,
          "Linear probing trains a ridge logistic regression pipeline in scikit-learn with "
          "imputation, standardisation and a grid search over the regularisation strength, using "
          "as many folds as there are chromosomes: each fold tests on one chromosome using a model "
          "trained on the rest, with the regularisation chosen by group K-fold cross-validation "
          "whose groups are the training chromosomes. For CADD, linear probing uses 113 CADD input "
          "features together with the single CADD output score; for the other models it uses only "
          "output features, that is predicted tracks, log-likelihood ratios or embedding similarity.",
          "Section 5 'Models' (page 6), Figure 5 caption (page 8) and Appendix B.4 with Listing 1 "
          "(pages 24 to 25)")

add_claim("zero_shot_score_selection", *B,
          "Five zero-shot scores are evaluated for each genomic language model (log-likelihood "
          "ratio, its absolute value, embedding l2 distance, embedding cosine distance and "
          "embedding inner product) and the best performing one is used when benchmarking against "
          "other models. The selected score, per model and dataset, is: "
          + "; ".join(f"{row['model']} {row['mendelian_traits']} for Mendelian traits and "
                      f"{row['complex_traits']} for complex traits" for row in s9)
          + ". Each of these is the highest-scoring approach for that model in Table S8, so the "
          "selection is made on the same variants the headline comparison is reported on.",
          "Section 5 'Self-supervised models' (page 7) with Tables S8 and S9 (page 27)")

add_claim("cadd_training_overlap", *B,
          "CADD is the only benchmarked model trained on variants, and its training variants "
          "overlap around 1 per cent of the variants in the datasets. Table S10 gives the overlap "
          "counts: Mendelian traits positives "
          f"{s10['Mendelian traits positives']['cadd_training_positives']} with CADD training "
          f"positives and {s10['Mendelian traits positives']['cadd_training_negatives']} with CADD "
          "training negatives; Mendelian traits negatives "
          f"{s10['Mendelian traits negatives']['cadd_training_positives']} and "
          f"{s10['Mendelian traits negatives']['cadd_training_negatives']}; complex traits "
          f"positives {s10['Complex traits positives']['cadd_training_positives']} and "
          f"{s10['Complex traits positives']['cadd_training_negatives']}; complex traits negatives "
          f"{s10['Complex traits negatives']['cadd_training_positives']} and "
          f"{s10['Complex traits negatives']['cadd_training_negatives']}. The paper states that "
          "CADD's positives and negatives are not defined from causal variant annotations and show "
          "no clear association with the positive or negative sets here, and that repeating the "
          "analysis with the overlapping variants removed left the results stable (Figure S3).",
          "Section 6 'Mendelian traits' (page 8) and Table S10 (page 28)")

add_claim("matching_feature_control", *B,
          "The features the controls were matched on carry almost no predictive power, which is "
          "the intent of the matching: 'Table S4 shows that the matched features have minimal "
          "predictive power, as intended.' The printed global AUPRCs are close to the 0.1 baseline.",
          "Appendix A.4 with Table S4 (page 22)")

add_claim("expanded_datasets", *B,
          "Besides the nine-control datasets, the benchmark provides expanded datasets with "
          "millions of control variants per positive. For Mendelian traits no subsampling of "
          "negatives is needed; for complex traits the negatives are subsampled into 100 equal-size "
          "minor allele frequency bins to match the positive set's distribution. Figure 6 reports "
          "n=339 positives against 4.9M negatives for Mendelian traits and n=1.1K against 2.9M for "
          "complex traits, and only models with precomputed genome-wide zero-shot scores (CADD, "
          "GPN-MSA, phyloP and phastCons) were evaluated on them; the paper estimates that a slower "
          "model such as Caduceus would need about six months on one NVIDIA A100 80GB GPU.",
          "Section 4 'Matching positives and negatives' (page 5), Section 6 'Results on expanded "
          "datasets' with Figure 6 (page 9), Appendix A.4 (page 22) and Appendix B.4 (page 24)")

add_claim("consequence_and_trait_composition", *B,
          "Distal non-exonic variants, the potential enhancers, are 10 per cent of the Mendelian "
          "traits dataset and 76 per cent of the complex traits dataset. Of the 1,140 putative "
          "causal variants for complex traits only 53 affect a disease trait, and 21 of the complex "
          "traits are diseases or disorders (Table S1); the dataset holds only 3 non-coding variants "
          "affecting the risk of Alzheimer's disease. 103 of the complex trait causal variants (9 "
          "per cent) overlap fine-mapped GTEx eQTL variants, with no such overlap for Mendelian "
          "trait variants; those eQTL-overlapping variants are enriched in exonic variants "
          "(Fisher's exact p = 8e-8) and, among non-exonic variants, have lower transcription start "
          "site distances (Mann-Whitney p = 4e-4).",
          "Section 4 'Variant type annotation' (page 5), Section 6 'Results by trait' and 'eQTL "
          "colocalization' (page 12) with Table S1 (page 20)")

add_claim("benchmarked_models", *B,
          "Table 2 lists the benchmarked systems with their dependencies, parameter count, context "
          "size and number of extracted features: "
          + "; ".join(f"{row['model']} ({row['params']} parameters, context {row['context_size']}, "
                      f"{row['extracted_features']} extracted features)" for row in read("table-2"))
          + ". Evo2 was trained with a 1 M context size but uses a shorter context for variant "
          "effect prediction. The downloaded Hugging Face Hub checkpoints are "
          + "; ".join(f"{model} {path}" for model, path in t5_hub.items())
          + ". Evo2 checkpoints Evo2_1b_base, Evo2_7b and Evo2_40b came from the official "
          "repository, Enformer and Borzoi from gReLU's Model Zoo, Sei scores from the Sei web "
          "server, and CADD v1.7 scores and annotations from the Washington GRCh38 "
          "whole_genome_SNVs_inclAnno file. phyloP-100v, phyloP-241m and phastCons-43p were taken "
          "from the UCSC hg38 phyloP100way, cactus241way phyloP and Zoonomia primate phastCons "
          "tracks.",
          "Table 2 (page 6), Table S5 (page 23) and Appendix B.1 (pages 22 to 23)")

add_claim("feature_and_score_definitions", *B,
          "Table 3 fixes what each class of model contributes. Functional-genomics-supervised "
          "models (Enformer, Borzoi) give l2 scores, the norm over spatial positions of the "
          "log2 fold change in predicted activity between the alternate and reference sequence, per "
          "track, plus their aggregation across tracks ('l2 of l2 scores', all tracks and within "
          "each assay type); the zero-shot score is the l2 of l2 over all tracks. Sei gives changes "
          "in sequence class scores, with the maximum absolute change as the zero-shot score. "
          "Self-supervised models give the log-likelihood ratio and its absolute value, and the "
          "embedding inner product for each hidden dimension, with the embedding inner product, l2 "
          "distance and cosine distance as zero-shot scores. The integrative model gives CADD input "
          "features and the CADD score, with the CADD score as the zero-shot score, and conservation "
          "scores are used directly. Predictions are always averaged over the forward and reverse "
          "strand for reverse-complement invariance.",
          "Table 3 and Section 5 (pages 6 to 7) and Appendix B.3 (pages 23 to 24)")

add_claim("availability", *B,
          "The benchmark is at https://huggingface.co/datasets/songlab/TraitGym with a leaderboard "
          "at https://huggingface.co/spaces/songlab/TraitGym-leaderboard, code to reproduce the "
          "analysis at https://github.com/songlab-cal/TraitGym, and a Google Colab notebook that "
          "evaluates a model in a few minutes.",
          "Abstract (page 1) and 'Data, model and code availability' (page 14)")

add_claim("author_reported_models", *B,
          "The benchmark's authors are also the authors of GPN-MSA (Benegas et al. 2025a) and "
          "introduce GPN-Promoter in this paper as 'This work', so the GPN-MSA and GPN-Promoter "
          "rows of the benchmark are author-reported.",
          "Table 2 'Source' column (page 6) and Section 5 'Models' (page 6)")

add_claim("stated_limitations", *B,
          "The paper states that TraitGym was designed to have simple metrics and be tractable even "
          "for billion-parameter models, but has limited ability to resolve subtle differences in "
          "performance: the advantage of GPN-MSA over other alignment-based zero-shot scores on "
          "Mendelian traits is visible only on the expanded datasets. For deeper evaluation it "
          "recommends the genome-wide benchmarks of Benegas et al. (2025a), and for complex traits "
          "partitioned linkage disequilibrium score regression, which is not limited to fine-mapped "
          "or genome-wide-significant variants. The labels are curated pathogenic variants and "
          "fine-mapping output, not experimental measurements.",
          "Section 7 'Discussion' (page 14)")

add_claim("paper_agrees_with_benchmark_metric_files", *B,
          "Table S8 prints the zero-shot AUPRC of ten genomic language models under five scoring "
          "approaches on both datasets, 100 cells, rounded to three decimal places. All 100 cells "
          "equal the corresponding value in the benchmark's own Hugging Face metric files, already "
          "in the store as 100 results from "
          "lit-genomics-20261011-traitgym-source-hf-metrics, when those full-precision values are "
          "rounded to three decimal places, with no disagreement. The two are on the same basis: "
          "Appendix B.4 states the weighted average over chromosomes is used for zero-shot scores "
          "as well, and the stored values come from the files under "
          "AUPRC_by_chrom_weighted_average/all/. The embedding columns correspond to the "
          "Embeddings.* metric files and not to the six InnerProduct and EuclideanDistance files "
          "the benchmark also publishes for Mendelian traits. The paper prints no value for the 36 "
          "stored linear probing results or the 14 stored zero-shot results of models that are not "
          "genomic language models; those appear only in Figure 5. The cell-by-cell table is "
          "data/omics/traitgym-20261116/extract/comparison.tsv, produced by "
          "data/omics/traitgym-20261116/extract/compare_s8.py.",
          "Table S8 (page 27) and Appendix B.4 (page 24)")

add_claim("training_data", *G,
          "GPN-Promoter was trained on 512-bp sequences centred on the transcription start sites of "
          "protein-coding genes in reference genomes of animal species. Transcription start site "
          "coordinates came from NCBI Datasets gene annotations; species with gene annotations were "
          "subsampled to at most one per family, giving 434 reference genomes. The training "
          "objective follows GPN: base-pair-level tokenisation and masked language modelling of "
          "local 512-bp windows, with repeat positions, soft-masked in the reference genome, "
          "downweighted. It is trained only on promoters as an attempt to focus on regulatory "
          "regions; the paper says it would have liked to train on enhancers too but no annotation "
          "exists for non-model organisms.",
          "Section 5 'Models' (page 6) and Appendix B.2 (pages 22 to 23)")

add_claim("architecture_hyperparameters", *G,
          "The architecture follows ByteNet: blocks alternating dilated convolutions and "
          "feed-forward layers. Table S6 gives window size "
          f"{s6['Window size']}, repeat weight {s6['Repeat weight']}, embedding dimension "
          f"{s6['Embedding dimension']}, slim {s6['Slim']}, {s6['Convolutional blocks']} "
          f"convolutional blocks, convolutional kernel size "
          f"{s6['Convolutional kernel size (first block)']} in the first block and "
          f"{s6['Convolutional kernel size (remaining blocks)']} in the remaining blocks, a "
          "dilation schedule of 1, 2, 4, 8, 16, 32, 64, 128 repeating, the AdamW optimizer, weight "
          f"decay {s6['Weight decay']}, batch size {s6['Batch size']}, {s6['Steps']} steps, "
          "learning rate 1e-3 and a 1 K step learning rate warmup. Table 2 gives 152M parameters, "
          "a context size of 512 and 1,026 extracted features. Training took approximately two "
          "weeks on four NVIDIA A100 40GB GPUs.",
          "Table 2 (page 6), Appendix B.2 and Table S6 (pages 22 to 23)")

add_claim("access", *G,
          "GPN-Promoter is available at https://huggingface.co/songlab/gpn-animal-promoter and its "
          "training dataset at https://huggingface.co/datasets/songlab/gpn-animal-promoter-dataset.",
          "'Data, model and code availability' (page 14)")

add_claim("reported_performance_scope", *G,
          "The paper reports that GPN-Promoter performs relatively well on Mendelian traits despite "
          "its small parameter count, that its zero-shot scores do better on proximal non-exonic "
          "and 5-prime UTR variants, which lie in the 512 bp around the transcription start site "
          "that overlap its training data (Figure S10), and that when evaluated only on "
          "promoter-like regions it performs comparably to the Evo2 40B model with only 152M "
          "parameters (Figure S11). None of those figures prints a value.",
          "Section 6 'Mendelian traits' (page 8) and 'Results by consequence' (pages 11 to 12)")


# ------------------------------------------------------------------ write

def main() -> int:
    ids = [r["id"] for r in records]
    assert len(ids) == len(set(ids)), "duplicate record ids"
    path = BATCH / "batch.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for rec in records:
            handle.write(json.dumps(rec, ensure_ascii=True, sort_keys=True) + "\n")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    counts: dict[str, int] = {}
    for rec in records:
        counts[rec["kind"]] = counts.get(rec["kind"], 0) + 1
    for kind in sorted(counts):
        print(f"{kind:15} {counts[kind]}")
    print(f"{'total':15} {len(records)}")
    print(f"batch.jsonl sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
