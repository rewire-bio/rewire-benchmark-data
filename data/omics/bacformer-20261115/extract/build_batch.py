#!/usr/bin/env python3
"""Build data/omics/bacformer-20261115/batch.jsonl from extract/tables.json and the pinned sources.

Every numeric value comes from extract/tables.json, which parse_tables.py produced from the
archived text layer of the pinned preprint PDF. Descriptive text comes from the pinned
repository READMEs, LICENSE files and Hugging Face model cards, each with its own locator.

Usage: python3 extract/build_batch.py [out.jsonl]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BATCH = HERE.parent
P = "bacformer-20261115-"
DATE = "2026-11-15"
RETRIEVED_SMALL = "2026-11-15T23:09:36Z"
RETRIEVED_PDF = "2026-11-15T22:55:00Z"
RETRIEVED_PDF_V2 = "2026-11-15T22:53:00Z"

PDF_V3_SHA = "d86de3315063e038ec8d5bed60b7b1a916c137ee60973e55d9d5c82f078d8dfd"
PDF_V3_SECOND_SHA = "08fcc83af256845d942345fc6b63c64911878733acd028edab5e9307d63319db"
TEXT_SHA = "86636e89b167d7304b3a83ee7f159cad0a9bdbe97019588ce836087b8fe3b0b2"
TEXT_GZ_SHA = "0afdefd78a410d036d1c4f17e33bdf481e8d76241ee02f4c84c7c4be91ee72aa"
PDF_V2_SHA = "a842db88eabf2b83d4e0de861e8a6767a01ee3f72c62b6a177494ffafd6d9703"
BACFORMER_README_SHA = "6e4fdabbd05c93ff63b0eb583ce6a9309eaa13998087cc32ddeaa6928025b235"
BACBENCH_README_SHA = "c9d28efef5b4cc30adbcc9de224c350100f5aa2a15a025beaf10dcdeb86cd93e"
APACHE_LICENCE_SHA = "d7fe40bfc2a639daa18e4caf57fab7545ece94bd38fb181c1f5b780d3b8cfa01"
BACFORMER_COMMIT = "61dca9537429b95365d73d72a3e11c207df1ed6c"
BACBENCH_COMMIT = "64b7d45823b2ff2ef88458e3aa235caa461a12aa"
PDF_V3_URL = "https://www.biorxiv.org/content/10.1101/2025.07.20.665723v3.full.pdf"

EXTRACTOR_NOTE = (
    "Claude (Opus 5) extraction agent; no human review claimed. Extraction only: a different agent "
    "reviews this batch, and nothing here is marked reproduced."
)
PARSE_NOTE = (
    "Extraction: the six supplementary benchmark tables were parsed from the gzipped pdftotext -layout "
    "text layer of the pinned v3 PDF (artifacts/biorxiv-665723v3-text-layer.txt.gz) by "
    "extract/parse_tables.py, which locates each table by its own printed caption line, searches only "
    "the lines between the previous caption and that caption, and asserts every row label in the "
    "printed order. extract/check_tables.py re-reads the same cells by character position against each "
    "table's printed metric header; both agree on all 186 cells."
)

# Hugging Face model cards: slug -> (revision, artifact sha256, safetensors total as served)
CARDS = {
    "bacformer-masked-MAG": ("340a08cf5d5cd7d9f1ffac9075cde733d108a82b", "d735d1b2c8caa57a9f6abf990a457b2aa084f626070e555d6c01ca4a46b6bf7c", 50852241),
    "bacformer-masked-complete-genomes": ("d1c461f1db75902e6502e5ba7588ea1a4ea96b29", "02575bd9d4ae949e3c38a5a5890767b862c75bc2a20e84afa4a517bd2f067ff1", 50852241),
    "bacformer-large-masked-MAG": ("cb92cdf04e1b32993a19fdd9cf6f8f49efde2665", "3809ffe59057788ba942d697a085edcd8458edbf815a116018e38e721d1e788d", 431765841),
    "bacformer-large-masked-complete-genomes": ("84f85c37a05e55559142b842c1569e265183b554", "19142e40c2aa69f1b3125fb7594cc8c6ea9f775e1878645583df21952c175596", 431765841),
    "bacformer-causal-MAG": ("e4c8d6dc4decaa88729ce3853b1f329fee3b4960", "a054cf81eb8ca4abac0ffd2063358fc97cc38ebcd7b7e945ff2cb026d7cde12c", 50852241),
    "bacformer-causal-complete-genomes": ("6d2af6ac98f5aaf420ab33b475b891c8398e3bb9", "048353f8367af281dd2a9d13404d9f4a257247bb308be3bfb578315e56c8047d", 50852241),
    "bacformer-for-ppi-prediction": ("553108a6a1190d45fabea32e64b0ddf8755e6e0e", "0336368f8274a5ed09f54cee8d56a851ecee96026d9f391a6735762c16608a60", 26802241),
}
CARD_SOURCE = {slug: f"{P}source-hf-card-{slug.lower().replace('_', '-')}" for slug in CARDS}

RECORDS: list[dict] = []


def add(record: dict) -> dict:
    RECORDS.append(record)
    return record


def review(method: list[str], artifact_sha: str, url: str, note: str, method_note: str = PARSE_NOTE) -> dict:
    return {
        "method": method,
        "method_note": method_note,
        "reviewer": ["claude"],
        "reviewer_note": EXTRACTOR_NOTE,
        "date": DATE,
        "artifact_sha256": artifact_sha,
        "retrieval_url": url,
        "note": note,
    }


def preprint_review(note: str) -> dict:
    return review(["deterministic-table-parse", "pdf-text-parse", "source-hash-verification"], PDF_V3_SHA, PDF_V3_URL, note)


def text_review(artifact_sha: str, url: str, note: str) -> dict:
    return review(
        ["transcription", "source-hash-verification"],
        artifact_sha,
        url,
        note,
        method_note=(
            "Extraction: the statement was read from the pinned artifact, whose SHA-256 was checked, and "
            "transcribed by hand with its locator. The artifact was retrieved twice on 2026-11-15 with "
            "identical bytes and a copy is kept in artifacts/."
        ),
    )


MICROBIAL = {"areas": ["microbes-communities"], "contexts": ["research"]}


def facets(*extra_areas: str, method_types: list[str] | None = None) -> dict:
    out = {"areas": ["microbes-communities", *extra_areas], "contexts": ["research"]}
    if method_types:
        out["method_types"] = method_types
    return out


# ---------------------------------------------------------------- sources

def sources() -> None:
    add({
        "id": f"{P}source-preprint-v3",
        "kind": "source",
        "name": "Bacformer preprint, bioRxiv 2025.07.20.665723 version 3",
        "description": "Preprint describing Bacformer, a contextualised protein language model of bacterial genomes, and its evaluation against other genomic language models on the BacBench tasks.",
        "status": "needs_review",
        "facets": dict(MICROBIAL),
        "source_ids": [],
        "links": [],
        "attributes": {
            "url": PDF_V3_URL,
            "version": "Version 3, posted 17 August 2026 according to the page banner; the bioRxiv API lists version 3 with date 2026-08-19",
            "retrieved_at": RETRIEVED_PDF,
            "doi": "10.1101/2025.07.20.665723",
            "publication_status": "preprint",
            "artifact_sha256": PDF_V3_SHA,
            "archive_sha256": TEXT_GZ_SHA,
            "licence": "CC BY 4.0",
            "article_licence": "CC-BY 4.0 International, stated in the banner on every page",
            "media_type": "application/pdf",
            "hash_scope": (
                "The hash is of one download. bioRxiv regenerates this PDF on request, so the container "
                "bytes differ between downloads: a second download minutes later gave "
                f"{PDF_V3_SECOND_SHA}. The pdftotext -layout text layer of both downloads is byte-identical "
                f"(SHA-256 {TEXT_SHA}), and that text layer, archived gzipped in artifacts/ with SHA-256 "
                f"{TEXT_GZ_SHA}, is what every extracted value was read from."
            ),
            "retrieval_note": (
                "The issue reported HTTP 403 for a version 2 retrieval during discovery. On 2026-11-15 the "
                "bioRxiv API listed versions 1 (2025-07-20), 2 (2025-08-13) and 3 (2026-08-19); the version "
                "3 PDF was served over plain curl without a 403. Europe PMC also serves this study as "
                "PPR1052405, whose full-text XML carries article-version number 3 but holds no tables."
            ),
            "extraction_method": "pdftotext -layout text layer, parsed by extract/parse_tables.py and rechecked by extract/check_tables.py",
            "source_locator": "Supplementary Tables S1, S9, S10, S11, S12, S13, S14, S15, S16, S17 and S18; Methods sections 'Downstream tasks & analysis' and 'Code and data availability'",
            "limitations": [
                "Preprint; not certified by peer review.",
                "Version 2 (posted 13 August 2025) prints different values for the same analyses and does not include Bacformer Large; no value in this batch comes from it.",
                "The tables carry no per-cell counts for some aggregations, so several denominators stay unreported.",
            ],
            "review": preprint_review(
                "Both downloads of the PDF were hashed; their text layers are byte-identical. All 186 extracted "
                "cells come from this artifact's text layer."
            ),
        },
    })
    add({
        "id": f"{P}source-preprint-v2",
        "kind": "source",
        "name": "Bacformer preprint, bioRxiv 2025.07.20.665723 version 2",
        "description": "The August 2025 version of the Bacformer preprint, which reports the study before Bacformer Large was added and prints different values for the same analyses.",
        "status": "needs_review",
        "facets": dict(MICROBIAL),
        "source_ids": [],
        "links": [{"relation": "companion_of", "target_id": f"{P}source-preprint-v3"}],
        "attributes": {
            "url": "https://www.biorxiv.org/content/biorxiv/early/2025/08/13/2025.07.20.665723.full.pdf",
            "version": "Version 2, posted 13 August 2025 according to the page banner",
            "retrieved_at": RETRIEVED_PDF_V2,
            "doi": "10.1101/2025.07.20.665723",
            "publication_status": "preprint",
            "artifact_sha256": PDF_V2_SHA,
            "licence": "CC BY 4.0",
            "media_type": "application/pdf",
            "hash_scope": "One download of 2026-11-15; the same caveat applies as for version 3, whose container bytes change between downloads.",
            "scope_decision": (
                "Registered to record the version history and that the retrieval reported as HTTP 403 in the "
                "discovery issue succeeded. No value was extracted from it: it is superseded by version 3, and "
                "its text layer mis-encodes digits (the body font maps digits to punctuation, so '1.3 million' "
                "reads as '!.# million'), which makes transcription from the text layer unsafe."
            ),
            "limitations": [
                "Superseded by version 3 and not used for any value in this batch.",
                "Its text layer mis-encodes digits, so numbers cannot be read from it without a page render.",
            ],
            "review": review(
                ["source-hash-verification"],
                PDF_V2_SHA,
                "https://www.biorxiv.org/content/biorxiv/early/2025/08/13/2025.07.20.665723.full.pdf",
                "Retrieved and hashed only. The prose numbers it prints differ from version 3, which is why the two versions are kept apart.",
                method_note="Retrieved and hashed; not parsed, because its text layer mis-encodes digits.",
            ),
        },
    })
    add({
        "id": f"{P}source-bacformer-readme",
        "kind": "source",
        "name": "Bacformer repository README at commit 61dca95",
        "description": "The Bacformer repository README, which lists the released checkpoints, the base protein language model of each size and the installation requirements.",
        "status": "needs_review",
        "facets": dict(MICROBIAL),
        "source_ids": [],
        "links": [{"relation": "companion_of", "target_id": f"{P}source-preprint-v3"}],
        "attributes": {
            "url": f"https://github.com/macwiatrak/Bacformer/blob/{BACFORMER_COMMIT}/README.md",
            "artifact_url": f"https://raw.githubusercontent.com/macwiatrak/Bacformer/{BACFORMER_COMMIT}/README.md",
            "version": f"Commit {BACFORMER_COMMIT}",
            "retrieved_at": RETRIEVED_SMALL,
            "publication_status": "official_project_source",
            "artifact_sha256": BACFORMER_README_SHA,
            "media_type": "text/markdown",
            "code_url": "https://github.com/macwiatrak/Bacformer",
            "source_locator": "Sections 'News', 'Requirements', 'Pretrained model checkpoints' and 'Citation'",
            "limitations": [
                "The 'Pretrained model checkpoints' table repeats the MAG training description on the bacformer-large-masked-complete-genomes row, which its own model card contradicts.",
                "The news list is not in date order and the dates of the Bacformer Large release entries precede the preprint entry they follow.",
            ],
            "review": text_review(BACFORMER_README_SHA, f"https://raw.githubusercontent.com/macwiatrak/Bacformer/{BACFORMER_COMMIT}/README.md", "Pinned to the commit named in the discovery issue."),
        },
    })
    add({
        "id": f"{P}source-bacbench-readme",
        "kind": "source",
        "name": "BacBench repository README at commit 64b7d45",
        "description": "The BacBench repository README, which states the active and deprecated tasks, the benchmarked models and the dataset locations.",
        "status": "needs_review",
        "facets": dict(MICROBIAL),
        "source_ids": [],
        "links": [{"relation": "companion_of", "target_id": f"{P}source-preprint-v3"}],
        "attributes": {
            "url": f"https://github.com/macwiatrak/BacBench/blob/{BACBENCH_COMMIT}/README.md",
            "artifact_url": f"https://raw.githubusercontent.com/macwiatrak/BacBench/{BACBENCH_COMMIT}/README.md",
            "version": f"Commit {BACBENCH_COMMIT}",
            "retrieved_at": RETRIEVED_SMALL,
            "publication_status": "official_project_source",
            "artifact_sha256": BACBENCH_README_SHA,
            "media_type": "text/markdown",
            "code_url": "https://github.com/macwiatrak/BacBench",
            "source_locator": "Sections 'News', 'Datasets', 'Benchmarked models' and 'Task overview'",
            "limitations": [
                "Prints no numeric task results; a model leaderboard is on its to-do list.",
                "Its 'Benchmarked models' table gives Bacformer Large 27M parameters, which every other source contradicts, and differs from the preprint on several other parameter counts and context lengths.",
                "Mutable repository file; pinned here to one commit.",
            ],
            "review": text_review(BACBENCH_README_SHA, f"https://raw.githubusercontent.com/macwiatrak/BacBench/{BACBENCH_COMMIT}/README.md", "Pinned to the commit named in the discovery issue."),
        },
    })
    for key, repo, commit in (
        ("bacformer", "Bacformer", BACFORMER_COMMIT),
        ("bacbench", "BacBench", BACBENCH_COMMIT),
    ):
        add({
            "id": f"{P}source-{key}-licence",
            "kind": "source",
            "name": f"{repo} LICENSE file at commit {commit[:7]}",
            "description": f"The licence file of the {repo} repository, which carries the Apache License 2.0 text.",
            "status": "needs_review",
            "facets": dict(MICROBIAL),
            "source_ids": [],
            "links": [{"relation": "companion_of", "target_id": f"{P}source-preprint-v3"}],
            "attributes": {
                "url": f"https://github.com/macwiatrak/{repo}/blob/{commit}/LICENSE",
                "artifact_url": f"https://raw.githubusercontent.com/macwiatrak/{repo}/{commit}/LICENSE",
                "version": f"Commit {commit}",
                "retrieved_at": RETRIEVED_SMALL,
                "publication_status": "official_project_source",
                "artifact_sha256": APACHE_LICENCE_SHA,
                "media_type": "text/plain",
                "licence": "Apache-2.0",
                "source_locator": "Lines 1 to 3 and the terms that follow",
                "access_and_reuse": "Covers the contents of this repository only. It says nothing about the dependency models or the third-party measurements the datasets come from.",
                "limitations": [
                    "Both repositories serve byte-identical licence files, so the hash does not distinguish them; the URL and commit do.",
                ],
                "review": text_review(APACHE_LICENCE_SHA, f"https://raw.githubusercontent.com/macwiatrak/{repo}/{commit}/LICENSE", "Unmodified Apache License 2.0 text."),
            },
        })
    for slug, (revision, sha, total) in CARDS.items():
        empty = slug == "bacformer-for-ppi-prediction"
        add({
            "id": CARD_SOURCE[slug],
            "kind": "source",
            "name": f"Hugging Face model card for macwiatrak/{slug}",
            "description": (
                f"The Hugging Face model card of the {slug} checkpoint, which is the auto-generated transformers "
                "template and carries no description, licence or training detail."
                if empty
                else f"The Hugging Face model card of the {slug} checkpoint, which states its size, training corpus, base protein language model and licence."
            ),
            "status": "needs_review",
            "facets": dict(MICROBIAL),
            "source_ids": [],
            "links": [{"relation": "companion_of", "target_id": f"{P}source-preprint-v3"}],
            "attributes": {
                "url": f"https://huggingface.co/macwiatrak/{slug}",
                "artifact_url": f"https://huggingface.co/macwiatrak/{slug}/raw/{revision}/README.md",
                "version": f"Repository revision {revision}",
                "retrieved_at": RETRIEVED_SMALL,
                "publication_status": "official_project_source",
                "artifact_sha256": sha,
                "media_type": "text/markdown",
                "source_locator": "YAML front matter and the body of the card",
                "access_note": (
                    f"The repository metadata served alongside the card gives a safetensors parameter total of "
                    f"{total:,} for this checkpoint. That total is served by the API rather than printed in the "
                    "card, and no record in this batch rests on it."
                ),
                "limitations": (
                    ["Auto-generated template with every field left as 'More Information Needed', including the licence."]
                    if empty
                    else ["Mutable repository file; pinned here to one revision."]
                ),
                "review": text_review(sha, f"https://huggingface.co/macwiatrak/{slug}/raw/{revision}/README.md", "Retrieved twice on 2026-11-15 with identical bytes."),
            },
        })


# ---------------------------------------------------------------- models

CHECKPOINTS = [
    {
        "slug": "bacformer-masked-MAG",
        "id": "model-bacformer-masked-mag",
        "name": "bacformer-masked-MAG",
        "size": "base",
        "description": "Bacformer checkpoint pretrained on metagenome-assembled genomes with a masked objective, which predicts the protein family of masked proteins from the other proteins in the genome.",
        "training_data": "Pretrained on the MAG corpus of about 1.3 million metagenome-assembled genomes with about 3 billion proteins, masking 15% of the proteins.",
        "parameters_printed": "27M-parameter base transformer model",
        "card_locator": "Body: 'A key member of this collection is bacformer-masked-MAG, a 27M-parameter base transformer model'; 'License: Apache 2.0'",
    },
    {
        "slug": "bacformer-masked-complete-genomes",
        "id": "model-bacformer-masked-complete-genomes",
        "name": "bacformer-masked-complete-genomes",
        "size": "base",
        "description": "Bacformer checkpoint initialised from the masked MAG checkpoint and further pretrained on about 40 thousand complete RefSeq genomes with a masked objective.",
        "training_data": "Pretrained on the MAG corpus of about 1.3 million genomes, then further pretrained on about 40 thousand complete genomes from NCBI RefSeq.",
        "parameters_printed": "27M-parameter transformer",
        "card_locator": "Body: '27M-parameter transformer further pretrained on ~40 k complete genomes from NCBI RefSeq'; 'License: Apache 2.0'",
    },
    {
        "slug": "bacformer-causal-MAG",
        "id": "model-bacformer-causal-mag",
        "name": "bacformer-causal-MAG",
        "size": "base",
        "description": "Bacformer checkpoint pretrained on metagenome-assembled genomes with an autoregressive objective, which predicts the next protein family along the genome.",
        "training_data": "Pretrained on the MAG corpus of about 1.3 million metagenome-assembled genomes with an autoregressive objective.",
        "parameters_printed": "27M-parameter base transformer model",
        "card_locator": "Body: 'a 27M-parameter base transformer model trained on ~1.3M'; 'License: Apache 2.0'",
    },
    {
        "slug": "bacformer-causal-complete-genomes",
        "id": "model-bacformer-causal-complete-genomes",
        "name": "bacformer-causal-complete-genomes",
        "size": "base",
        "description": "Bacformer checkpoint initialised from the autoregressive MAG checkpoint and further pretrained on about 40 thousand complete RefSeq genomes.",
        "training_data": "Pretrained on the MAG corpus, then further pretrained on about 40 thousand complete genomes from NCBI RefSeq with an autoregressive objective.",
        "parameters_printed": "27M-parameter transformer",
        "card_locator": "Body: '27M-parameter transformer further pretrained on ~40 k complete genomes from NCBI RefSeq'; 'License: Apache 2.0'",
    },
    {
        "slug": "bacformer-large-masked-MAG",
        "id": "model-bacformer-large-masked-mag",
        "name": "bacformer-large-masked-MAG",
        "size": "large",
        "description": "Bacformer Large checkpoint pretrained on metagenome-assembled genomes with a masked objective over ESM-C protein embeddings.",
        "training_data": "Pretrained on the MAG corpus of about 1.3 million metagenome-assembled genomes with a masked objective.",
        "parameters_printed": "300M-parameter base transformer model",
        "card_locator": "Body: 'Number of parameters: Bacformer Large is much larger (>300M parameters)' and '300M-parameter base transformer model trained on ~1.3M'; 'License: Apache 2.0'",
    },
    {
        "slug": "bacformer-large-masked-complete-genomes",
        "id": "model-bacformer-large-masked-complete-genomes",
        "name": "bacformer-large-masked-complete-genomes",
        "size": "large",
        "description": "Bacformer Large checkpoint initialised from the large masked MAG checkpoint and further pretrained on about 40 thousand complete RefSeq genomes.",
        "training_data": "Pretrained on the MAG corpus of about 1.3 million genomes, then further pretrained on about 40 thousand complete genomes from NCBI RefSeq.",
        "parameters_printed": "300M-parameter transformer",
        "card_locator": "Body: '300M-parameter transformer further pretrained on ~40 k complete genomes from NCBI RefSeq' and 'This model was initialised from bacformer-large-masked-MAG'; 'License: Apache 2.0'",
    },
    {
        "slug": "bacformer-for-ppi-prediction",
        "id": "model-bacformer-for-ppi-prediction",
        "name": "bacformer-for-ppi-prediction",
        "size": "base",
        "description": "Bacformer checkpoint released with a protein-protein interaction prediction head trained on the STRING DB pair labels.",
        "training_data": None,
        "parameters_printed": None,
        "card_locator": "Auto-generated template; the card states no size, training data or licence",
    },
]

UNAVAILABLE_CHECKPOINTS = [
    {
        "id": "model-bacformer-causal-protein-family-modeling-complete-genomes",
        "slug": "bacformer-causal-protein-family-modeling-complete-genomes",
        "size": "base",
        "name": "bacformer-causal-protein-family-modeling-complete-genomes",
        "description": "Bacformer checkpoint that takes protein-family tokens instead of protein sequences as input, so that it can generate sequences of protein families.",
        "readme_row": "Row 'bacformer-causal-protein-family-modeling-complete-genomes': 'A bacformer-causal-MAG finetuned on a set of ~40 k complete genomes with an autoregressive objective. In contrast to other models, this model takes as input a protein-family token rather than the protein sequence, allowing generation of sequences of protein families.'",
    },
    {
        "id": "model-bacformer-for-essential-genes-prediction",
        "slug": "bacformer-for-essential-genes-prediction",
        "size": "base",
        "name": "bacformer-for-essential-genes-prediction",
        "description": "Bacformer checkpoint finetuned for essential-gene prediction on top of the masked complete-genome checkpoint.",
        "readme_row": "Row 'bacformer-for-essential-genes-prediction': 'A bacformer-masked-complete-genomes finetuned on the essential-genes prediction task.'",
    },
]

PARAM_CONFLICT_NOTE_BASE = (
    "Printed parameter counts for the base model disagree across sources: '26M' in the Bacformer README "
    "'Requirements' section and in preprint Table S11, and '27M' on the model cards, in preprint Table S9 "
    "and in the BacBench README model table. Left unresolved for review."
)
PARAM_CONFLICT_NOTE_LARGE = (
    "Printed parameter counts for Bacformer Large disagree across sources: '300M' in the Bacformer README "
    "and on the model cards, '332M' in preprint Tables S9 and S11, and '27M' in the BacBench README model "
    "table. Left unresolved for review."
)


def models() -> None:
    add({
        "id": f"{P}model-bacformer",
        "kind": "model",
        "name": "Bacformer",
        "description": "Bacformer models a whole bacterial genome as a sequence of proteins ordered by their genomic coordinates and turns per-protein embeddings from a protein language model into contextual protein embeddings that condition each protein on the other proteins in the genome.",
        "status": "needs_review",
        "facets": facets("protein-function"),
        "source_ids": [f"{P}source-bacformer-readme", f"{P}source-preprint-v3", CARD_SOURCE["bacformer-masked-MAG"]],
        "links": [{"relation": "uses_model", "target_id": "discovery-model-esm-2"}],
        "attributes": {
            "entity_level": "family",
            "reported_name": "Bacformer",
            "licence": "Apache-2.0 for the code and models in the Bacformer repository",
            "training_data": "Pretrained on a MAG corpus of about 1.3 million bacterial genomes and about 3 billion proteins; checkpoints for complete genomes are further pretrained on about 40 thousand NCBI RefSeq genomes.",
            "access": "Public checkpoints on Hugging Face under macwiatrak, installed through the bacformer package; inference needs protein embeddings from a base protein language model.",
            "identity_scope": "The base size of the family, which embeds proteins with ESM-2 t12 35M and runs a 12-layer transformer of hidden size 480 over them.",
            "provenance_note": PARAM_CONFLICT_NOTE_BASE,
            "source_locator": "Bacformer README opening paragraph and 'Requirements'; preprint Methods 'Bacformer'; model card body",
            "version": "Checkpoints released on Hugging Face as of 2026-11-15",
            "review": text_review(BACFORMER_README_SHA, f"https://raw.githubusercontent.com/macwiatrak/Bacformer/{BACFORMER_COMMIT}/README.md", "Family record. Parameter counts are left to the claims because the sources disagree."),
        },
    })
    add({
        "id": f"{P}model-bacformer-large",
        "kind": "model",
        "name": "Bacformer Large",
        "description": "Bacformer Large is the larger size of Bacformer, which runs a 30-layer transformer of hidden size 960 over ESM-C protein embeddings to compute contextual protein embeddings for a whole genome.",
        "status": "needs_review",
        "facets": facets("protein-function"),
        "source_ids": [f"{P}source-bacformer-readme", f"{P}source-preprint-v3", CARD_SOURCE["bacformer-large-masked-MAG"]],
        "links": [
            {"relation": "variant_of", "target_id": f"{P}model-bacformer"},
            {"relation": "uses_model", "target_id": "discovery-model-esmc"},
        ],
        "attributes": {
            "entity_level": "family",
            "reported_name": "Bacformer Large",
            "licence": "Apache-2.0 for the code and models in the Bacformer repository",
            "training_data": "Pretrained on the same MAG corpus of about 1.3 million genomes; the complete-genome checkpoint is further pretrained on about 40 thousand NCBI RefSeq genomes.",
            "access": "Public checkpoints on Hugging Face under macwiatrak; needs ESM-C protein embeddings as input.",
            "identity_scope": "The large size of the family, released on 2025-01-20 according to the README news list.",
            "provenance_note": PARAM_CONFLICT_NOTE_LARGE,
            "source_locator": "Bacformer README 'News', 'Requirements' and 'Pretrained model checkpoints'; preprint Table S9; model card body",
            "version": "Checkpoints released on Hugging Face as of 2026-11-15",
            "review": text_review(BACFORMER_README_SHA, f"https://raw.githubusercontent.com/macwiatrak/Bacformer/{BACFORMER_COMMIT}/README.md", "Separate record because the two sizes use different base protein language models and different transformer shapes."),
        },
    })
    for spec in CHECKPOINTS:
        family = f"{P}model-bacformer-large" if spec["size"] == "large" else f"{P}model-bacformer"
        base_plm = "discovery-model-esmc" if spec["size"] == "large" else "discovery-model-esm-2"
        revision, sha, total = CARDS[spec["slug"]]
        missing: dict[str, dict] = {}
        attrs: dict = {
            "entity_level": "checkpoint",
            "reported_name": spec["slug"],
            "checkpoint_revision": revision,
            "access": f"Public Hugging Face repository macwiatrak/{spec['slug']}, served at revision {revision} on 2026-11-15.",
            "source_locator": spec["card_locator"],
            "version": f"Hugging Face revision {revision}",
            "provenance_note": (
                PARAM_CONFLICT_NOTE_LARGE if spec["size"] == "large" else PARAM_CONFLICT_NOTE_BASE
            ),
            "review": text_review(sha, f"https://huggingface.co/macwiatrak/{spec['slug']}/raw/{revision}/README.md", "Checkpoint record; the parameter count is left to the claims because the sources disagree."),
        }
        if spec["training_data"]:
            attrs["training_data"] = spec["training_data"]
        else:
            missing["training_data"] = {"reason": "unreported", "note": "The model card is the auto-generated template and states no training data; the preprint names the checkpoint but does not describe its training beyond the PPI head."}
        if spec["slug"] == "bacformer-for-ppi-prediction":
            attrs["licence"] = "Not stated"
            del attrs["licence"]
            missing["licence"] = {"reason": "unreported", "note": "The card's licence field reads 'More Information Needed' and the repository declares no licence; the Apache-2.0 statement covers the Bacformer repository, not this checkpoint."}
            attrs["provenance_note"] = (
                "Named in the preprint Methods as the released PPI prediction model. Its card is the "
                "auto-generated transformers template, so no size, training data or licence is stated."
            )
        else:
            attrs["licence"] = "Apache-2.0, stated in the card front matter and body"
        if missing:
            attrs["missing_metadata"] = missing
        source_ids = [CARD_SOURCE[spec["slug"]], f"{P}source-bacformer-readme"]
        if spec["slug"] == "bacformer-for-ppi-prediction":
            source_ids = [CARD_SOURCE[spec["slug"]], f"{P}source-preprint-v3"]
        add({
            "id": P + spec["id"],
            "kind": "model",
            "name": spec["name"],
            "description": spec["description"],
            "status": "needs_review",
            "facets": facets("protein-function"),
            "source_ids": source_ids,
            "links": [
                {"relation": "family", "target_id": family},
                {"relation": "uses_model", "target_id": base_plm},
            ],
            "attributes": attrs,
        })
    for spec in UNAVAILABLE_CHECKPOINTS:
        add({
            "id": P + spec["id"],
            "kind": "model",
            "name": spec["name"],
            "description": spec["description"],
            "status": "needs_review",
            "facets": facets("protein-function"),
            "source_ids": [f"{P}source-bacformer-readme"],
            "links": [
                {"relation": "family", "target_id": f"{P}model-bacformer"},
                {"relation": "uses_model", "target_id": "discovery-model-esm-2"},
            ],
            "attributes": {
                "entity_level": "checkpoint",
                "reported_name": spec["slug"],
                "access": (
                    f"Listed in the Bacformer README checkpoint table, but https://huggingface.co/macwiatrak/{spec['slug']} "
                    "and the Hugging Face model API both returned HTTP 401 to an anonymous request on 2026-11-15, so "
                    "nothing was retrieved from it."
                ),
                "source_locator": f"Pretrained model checkpoints table, {spec['readme_row']}",
                "provenance_note": "Registered from the README checkpoint table alone; no artifact of this checkpoint was retrieved.",
                "missing_metadata": {
                    "checkpoint_revision": {"reason": "unavailable", "note": "The repository returned HTTP 401 on 2026-11-15, so no revision could be read."},
                    "licence": {"reason": "unavailable", "note": "No card could be retrieved; the repository Apache-2.0 statement is about the Bacformer repository, not this checkpoint."},
                },
                "training_data": "Described in the README checkpoint table as a Bacformer checkpoint finetuned on about 40 thousand complete genomes.",
                "version": "Not retrievable on 2026-11-15",
                "review": text_review(BACFORMER_README_SHA, f"https://raw.githubusercontent.com/macwiatrak/Bacformer/{BACFORMER_COMMIT}/README.md", "Registered from the README row; the Hugging Face repository returned HTTP 401, which is recorded as a claim and in access."),
            },
        })
    add({
        "id": f"{P}model-glm2",
        "kind": "model",
        "name": "gLM2",
        "description": "gLM2 is a mixed-modality genomic language model that reads a genomic scaffold as amino-acid tokens for coding regions and nucleotide tokens for intergenic regions.",
        "status": "needs_review",
        "facets": facets("dna-genomes", "protein-function"),
        "source_ids": [f"{P}source-preprint-v3", f"{P}source-bacbench-readme"],
        "links": [],
        "attributes": {
            "entity_level": "family",
            "reported_name": "gLM2",
            "access": "Public Hugging Face checkpoint tattabio/gLM2_650M.",
            "source_locator": "Table S9, row 'gLM2'; Methods 'gLM2 (mixed-modality LM)'",
            "provenance_note": "Created because the store held no gLM2 record; it is a comparator in this benchmark, not a Bacformer component.",
            "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the benchmarked checkpoint is on the configurations."}},
            "review": preprint_review("Identity read from Table S9 and the Methods; no gLM2 record existed in the store."),
        },
    })


# ---------------------------------------------------------------- configurations

SYSTEMS = [
    {
        "slug": "mistral-dna",
        "name": "Mistral-DNA",
        "family": "lit-genomics-20261011-guanine-model-mistral-dna",
        "checkpoint": "Mistral-DNA-v1-138M-bacteria",
        "parameters": "138M",
        "dim": "768",
        "context": "512 tokens",
        "modality": "DNA",
        "objective": "Autoregressive",
        "tokenisation": "Byte-pair",
        "corpus": "Bacteria",
    },
    {
        "slug": "dnabert-2",
        "name": "DNABERT-2",
        "family": "discovery-model-dnabert-2",
        "checkpoint": "DNABERT-2-117M",
        "parameters": "117M",
        "dim": "768",
        "context": "512 tokens",
        "modality": "DNA",
        "objective": "Masked",
        "tokenisation": "Byte-pair",
        "corpus": "Multi-kingdom",
    },
    {
        "slug": "nucleotide-transformer",
        "name": "Nucleotide Transformer",
        "family": "discovery-model-nucleotide-transformer",
        "checkpoint": "nucleotide-transformer-v2-250m-multi-species",
        "parameters": "235M",
        "dim": "768",
        "context": "2,048 tokens",
        "modality": "DNA",
        "objective": "Masked",
        "tokenisation": "k-mer",
        "corpus": "Multi-kingdom",
    },
    {
        "slug": "prokbert",
        "name": "ProkBERT",
        "family": "catalog-model-prokbert",
        "checkpoint": "neuralbioinfo/prokbert-mini-long",
        "parameters": "26M",
        "dim": "384",
        "context": "4,096 tokens",
        "modality": "DNA",
        "objective": "Masked",
        "tokenisation": "k-mer",
        "corpus": "Bacteria",
    },
    {
        "slug": "evo",
        "name": "Evo",
        "family": "lit-genomics-20261011-geneb-model-evo",
        "checkpoint": "evo-1-8k-base (1.1_fix)",
        "parameters": "6.5B",
        "dim": "4,096",
        "context": "8,192 tokens",
        "modality": "DNA",
        "objective": "Autoregressive",
        "tokenisation": "Single nucleotide",
        "corpus": "Multi-kingdom",
    },
    {
        "slug": "evo-2",
        "name": "Evo-2",
        "family": "discovery-model-evo-2",
        "checkpoint": "evo2_1b_base",
        "parameters": "1B",
        "dim": "1,920",
        "context": "8,192 tokens",
        "modality": "DNA",
        "objective": "Autoregressive",
        "tokenisation": "Single nucleotide",
        "corpus": "Multi-kingdom",
    },
    {
        "slug": "esm-2",
        "name": "ESM-2",
        "family": "discovery-model-esm-2",
        "checkpoint": "esm2_t12_35M_UR50D",
        "parameters": "35M",
        "dim": "480",
        "context": "1,024 tokens",
        "modality": "Single protein sequence",
        "objective": "Masked",
        "tokenisation": "Single amino acid",
        "corpus": "Multi-kingdom",
    },
    {
        "slug": "esm-c",
        "name": "ESM-C",
        "family": "discovery-model-esmc",
        "checkpoint": "esmc_300m",
        "parameters": "332M",
        "dim": "960",
        "context": "1,024 tokens",
        "modality": "Single protein sequence",
        "objective": "Masked",
        "tokenisation": "Single amino acid",
        "corpus": "Multi-kingdom",
    },
    {
        "slug": "protbert",
        "name": "ProtBERT",
        "family": "lit-protein-20261011-deepprotein-model-protbert",
        "checkpoint": "prot_bert",
        "parameters": "412M",
        "dim": "1,024",
        "context": "1,024 tokens",
        "modality": "Single protein sequence",
        "objective": "Masked",
        "tokenisation": "Single amino acid",
        "corpus": "Multi-kingdom",
    },
    {
        "slug": "glm2",
        "name": "gLM2",
        "family": f"{P}model-glm2",
        "checkpoint": "tattabio/gLM2_650M",
        "parameters": "650M",
        "dim": "1,280",
        "context": "4,096 tokens",
        "modality": "Mixed modality (DNA and protein sequence)",
        "objective": "Masked",
        "tokenisation": "Single nucleotide and single amino acid",
        "corpus": "Bacteria",
    },
    {
        "slug": "bacformer",
        "name": "Bacformer",
        "family": f"{P}model-bacformer",
        "configures": f"{P}model-bacformer-masked-complete-genomes",
        "checkpoint": "macwiatrak/bacformer-masked-complete-genomes",
        "parameters": None,
        "dim": "480",
        "context": "6,000 proteins",
        "modality": "Multiple protein sequences ordered by genomic coordinates",
        "objective": "Masked",
        "tokenisation": "Single protein",
        "corpus": "Bacteria",
    },
    {
        "slug": "bacformer-large",
        "name": "Bacformer Large",
        "family": f"{P}model-bacformer-large",
        "configures": f"{P}model-bacformer-large-masked-complete-genomes",
        "checkpoint": "macwiatrak/bacformer-large-masked-complete-genomes",
        "parameters": "332M",
        "dim": "960",
        "context": "6,000 proteins",
        "modality": "Multiple protein sequences ordered by genomic coordinates",
        "objective": "Masked",
        "tokenisation": "Single protein",
        "corpus": "Bacteria",
    },
]
SYSTEM_BY_NAME = {s["name"]: s for s in SYSTEMS}

EMBEDDING_RECIPE = {
    "DNA": (
        "DNA windows of the model's context length with the stride in Table S10, last-layer hidden states "
        "mean-pooled; gene-level tasks slide a window over the gene with its upstream promoter, and Evo and "
        "Evo-2 centre the gene in a longer context and mean-pool only the gene's own tokens"
    ),
    "Single protein sequence": "Each protein embedded on its own, last-layer hidden states mean-pooled over amino acids",
    "Mixed modality (DNA and protein sequence)": (
        "Mixed-modality scaffolds up to 4,096 tokens with coding regions as amino acids and intergenic regions "
        "as nucleotides, last-layer hidden states mean-pooled, gene tasks masked to the gene's own tokens"
    ),
    "Multiple protein sequences ordered by genomic coordinates": (
        "Per-protein embeddings from the base protein language model, ordered by genomic coordinates and passed "
        "through the genome-level transformer; the contextual protein embeddings of the last layer are used"
    ),
}


def configurations() -> None:
    for system in SYSTEMS:
        for kind in ("zero-shot", "linear-probe"):
            is_probe = kind == "linear-probe"
            configures = system.get("configures", system["family"])
            links = [{"relation": "configuration_of", "target_id": configures}]
            if "configures" in system:
                links.append({"relation": "family", "target_id": system["family"]})
            if system["slug"] == "bacformer":
                links.append({"relation": "uses_model", "target_id": "discovery-model-esm-2"})
            if system["slug"] == "bacformer-large":
                links.append({"relation": "uses_model", "target_id": "discovery-model-esmc"})
            attrs: dict = {
                "configuration_type": "paper_evaluation",
                "checkpoint": system["checkpoint"],
                "reported_name": system["name"],
                "representation": EMBEDDING_RECIPE[system["modality"]],
                "model_family": system["name"],
                "access_reuse": (
                    "Public checkpoint downloaded from Hugging Face; the embedding and evaluation code is in the "
                    "BacBench repository, whose exact commit for these runs is not stated."
                ),
                "hyperparameters": (
                    "Backbone frozen; a task-specific head is trained on the stored embeddings with the learning "
                    "rate tuned per task and model, every other setting unchanged."
                    if is_probe
                    else "No trained parameters; embeddings are scored directly."
                ),
                "source_locator": f"Table S9, row '{system['name']}'; Methods 'Benchmarking' and 'General modelling details'",
                "provenance_note": (
                    "One configuration per benchmarked system and adaptation. The adaptation is the frozen-backbone "
                    "linear head used across the supervised tasks; each task's head and training schedule are on the "
                    "protocol, because the source states them per task."
                    if is_probe
                    else "One configuration per benchmarked system and adaptation. This is the untrained setting, where "
                    "embeddings are scored directly by cosine similarity or clustered."
                ),
                "version": "As benchmarked in version 3 of the preprint",
                "review": preprint_review(f"Checkpoint, dimensionality and context read from Table S9 row '{system['name']}'."),
            }
            if system["parameters"]:
                attrs["parameters"] = system["parameters"]
            else:
                attrs["missing_metadata"] = {
                    "parameters": {
                        "reason": "conflicting",
                        "note": "Table S9 prints 27M for Bacformer and Table S11 prints 26M for the same model in the same source; the Bacformer README says 26M and its model cards say 27M.",
                    }
                }
            add({
                "id": f"{P}config-{system['slug']}-{kind}",
                "kind": "configuration",
                "name": f"{system['name']} ({'frozen embeddings with a trained linear head' if is_probe else 'frozen embeddings, no trained head'})",
                "description": (
                    f"{system['name']} embeddings computed with the backbone frozen and a single trained linear layer "
                    "on top, which turns the stored embeddings into the task prediction."
                    if is_probe
                    else f"{system['name']} embeddings used without any trained parameters, scored directly by cosine "
                    "similarity between embeddings or clustered as whole-genome vectors."
                ),
                "status": "needs_review",
                "facets": facets(
                    "dna-genomes" if system["modality"].startswith(("DNA", "Mixed")) else "protein-function",
                    method_types=["foundation_model", "supervised_machine_learning"] if is_probe else ["foundation_model"],
                ),
                "source_ids": [f"{P}source-preprint-v3"],
                "links": links,
                "attributes": attrs,
            })
    for slug, family, size in (
        ("bacformer", f"{P}model-bacformer", "base"),
        ("bacformer-large", f"{P}model-bacformer-large", "large"),
    ):
        name = "Bacformer" if size == "base" else "Bacformer Large"
        add({
            "id": f"{P}config-{slug}-zero-shot-clustering",
            "kind": "configuration",
            "name": f"{name} genome embeddings for strain clustering (checkpoint not resolved)",
            "description": f"{name} whole-genome embeddings, mean-pooled over the contextual protein embeddings and clustered without any trained parameters.",
            "status": "needs_review",
            "facets": facets("protein-function", method_types=["foundation_model"]),
            "source_ids": [f"{P}source-preprint-v3", f"{P}source-bacbench-readme"],
            "links": [
                {"relation": "configuration_of", "target_id": family},
                {"relation": "uses_model", "target_id": "discovery-model-esmc" if size == "large" else "discovery-model-esm-2"},
            ],
            "attributes": {
                "configuration_type": "paper_evaluation",
                "reported_name": name,
                "representation": EMBEDDING_RECIPE["Multiple protein sequences ordered by genomic coordinates"] + ", mean-pooled across the genome",
                "model_family": name,
                "access_reuse": "Public checkpoints on Hugging Face; the strain clustering code is in the BacBench repository and the task is deprecated there.",
                "hyperparameters": "No trained parameters; Leiden clustering over a resolution and neighbour grid.",
                "source_locator": "Methods 'Strain clustering'; Table S9; BacBench README 'Benchmarked models' footnote",
                "provenance_note": (
                    "Kept separate from the other runs of this system and left at family level because the two sources "
                    "disagree about which checkpoint produced the clustering numbers."
                ),
                "version": "As benchmarked in version 3 of the preprint",
                "missing_metadata": {
                    "checkpoint": {
                        "reason": "conflicting",
                        "note": (
                            "Table S9 names the complete-genome checkpoint for the study, while the BacBench README "
                            "footnote states that strain clustering runs used the MAG checkpoint because the inputs are "
                            "metagenome-assembled genomes. The clustering dataset is 6,071 MAGs, which fits the footnote, "
                            "but no source names the checkpoint for this table."
                        ),
                    },
                    "parameters": {
                        "reason": "conflicting",
                        "note": PARAM_CONFLICT_NOTE_BASE if size == "base" else PARAM_CONFLICT_NOTE_LARGE,
                    },
                },
                "review": preprint_review("Separate configuration because the checkpoint behind Table S12 is not stated by either source."),
            },
        })


# ---------------------------------------------------------------- benchmark, tasks, datasets, protocols

TASKS = [
    {
        "slug": "operon-identification",
        "name": "Operon identification from long-read RNA sequencing",
        "status_text": "Active",
        "task_type": "binary boundary prediction between contiguous genes",
        "scope_note": "Decide for each pair of contiguous genes whether the two genes belong to the same operon, scored against operon annotations derived from long-read RNA sequencing of five strains.",
        "splits": "No split; the whole dataset is the test set, because the evaluation is zero-shot.",
        "areas": ["dna-genomes"],
    },
    {
        "slug": "protein-protein-interaction",
        "name": "Protein-protein interaction prediction",
        "status_text": "Active",
        "task_type": "binary classification of protein pairs",
        "scope_note": "Decide whether two proteins of the same genome interact, using STRING DB combined scores binarised at 0.6 as labels.",
        "splits": "Phylogeny-aware split by genus, 60/20/20 train, validation and test.",
        "areas": ["molecular-interactions", "protein-function"],
    },
    {
        "slug": "essential-genes",
        "name": "Essential gene prediction",
        "status_text": "Active",
        "task_type": "binary classification of genes",
        "scope_note": "Decide whether a gene is essential, using the Database of Essential Genes annotations mapped onto NCBI assemblies.",
        "splits": "Phylogeny-aware split by genus, 60/20/20 train, validation and test.",
        "areas": ["protein-function"],
    },
    {
        "slug": "phenotypic-traits",
        "name": "Phenotypic trait prediction",
        "status_text": "Active",
        "task_type": "categorical classification of whole genomes",
        "scope_note": "Predict categorical phenotypic traits of a strain from a whole-genome representation, one model per trait.",
        "splits": "Per-trait phylogeny-aware split by genus, 60/20/20, repeated over independent runs.",
        "areas": [],
    },
    {
        "slug": "antibiotic-resistance",
        "name": "Antibiotic resistance prediction",
        "status_text": "Active",
        "task_type": "per-drug binary classification and MIC regression from whole genomes",
        "scope_note": "Predict resistance of a strain to a given antibiotic, either as a resistant or susceptible call or as a minimum inhibitory concentration, from a whole-genome representation.",
        "splits": "Random 70/10/20 split per antibiotic and seed; deliberately not phylogeny-aware.",
        "areas": [],
    },
    {
        "slug": "strain-clustering",
        "name": "Strain clustering",
        "status_text": "Deprecated",
        "task_type": "unsupervised clustering of whole genomes",
        "scope_note": "Cluster genome embeddings and score the clusters against species labels; deprecated in BacBench on 2026-05-13 but kept in the repository for reproducibility.",
        "splits": "No split; all genomes are clustered and scored against their species labels.",
        "areas": [],
    },
]

DATASETS = [
    {
        "slug": "data-operon-long-read-rna-seq",
        "name": "BacBench operon identification dataset from long-read RNA sequencing",
        "description": "Operon annotations for five bacterial strains derived from long-read RNA sequencing triplicates mapped onto their RefSeq assemblies, with the DNA and protein sequences of each gene.",
        "task": "operon-identification",
        "attributes": {
            "assay": "Long-read RNA sequencing in triplicate, reads mapped to annotated genes with minimap2 and SAMtools and the triplicate predictions merged into operon annotations.",
            "species": "Staphylococcus aureus RN450 (GCF_000013425.1), Mycobacterium tuberculosis H37Rv 102J23 leuD panCD deletion strain (GCF_000195955.2), Mycobacterium abscessus ATCC 19977 (GCF_000069185.1), Pseudomonas aeruginosa PAO1 (GCF_000006765.1) and Escherichia coli DH5a (GCF_002899475.1)",
            "total": 5,
            "split": "Evaluation only; the whole dataset is the test set",
            "repository": "https://huggingface.co/datasets/macwiatrak/operon-identification-long-read-rna-sequencing-protein-sequences",
            "access": "Published as Hugging Face datasets in protein-sequence and DNA modalities; the preprint calls the underlying long-read RNA sequencing proprietary.",
            "source_locator": "Methods 'Zero-shot operon prediction using long-read RNA sequencing' and 'Benchmarking'; BacBench README 'Datasets'",
            "label_semantics": "A gene pair is positive when the two contiguous genes were called as belonging to the same operon by the merged long-read RNA sequencing annotations.",
            "reuse_restrictions": "The Hugging Face protein-sequence copy declares the Apache-2.0 licence in its card metadata; the DNA copy declares none. Neither card was pinned as a source in this batch.",
            "missing_metadata": {
                "total_targets": {"reason": "unreported", "note": "The number of scored contiguous gene pairs is not printed."},
                "accession": {"reason": "unreported", "note": "No sequencing read accession is given; only the RefSeq assembly accessions of the five strains."},
            },
        },
    },
    {
        "slug": "data-ppi-stringdb",
        "name": "BacBench protein-protein interaction dataset from STRING DB",
        "description": "Protein pairs of 261 bacterial genomes sampled from STRING DB across 215 genera, labelled by binarising the STRING combined interaction score at 0.6, with DNA matched from GenBank.",
        "task": "protein-protein-interaction",
        "attributes": {
            "assay": "STRING DB combined interaction scores, which pool evidence channels, binarised at a threshold of 0.6.",
            "total": 261,
            "population": "261 genomes across 215 genera, randomly sampled from the bacterial organisms in STRING DB",
            "split": "Phylogeny-aware split by genus, 60/20/20",
            "repository": "https://huggingface.co/datasets/macwiatrak/bacbench-ppi-stringdb-protein-sequences-small",
            "access": "Published as Hugging Face datasets in protein-sequence and DNA modalities, with a larger protein-only version of more than 10 thousand genomes.",
            "source_locator": "Methods 'Benchmarking' under protein-protein interaction prediction; BacBench README 'Datasets'",
            "label_semantics": "A pair is positive when its STRING DB combined score is at least 0.6, which the authors state leaves about 10% of pairs positive; the threshold was chosen on validation AUROC and AUPRC.",
            "reuse_restrictions": "Derived from STRING DB and GenBank, whose own terms apply to the underlying measurements; the Hugging Face copies declare Apache-2.0 in their card metadata, which was not pinned as a source in this batch.",
            "missing_metadata": {
                "total_targets": {"reason": "unreported", "note": "Up to 2,000,000 labelled pairs were retained per strain, said to be more than 99% of available pairs, but no total pair count is printed."},
            },
        },
    },
    {
        "slug": "data-essential-genes-deg",
        "name": "BacBench essential gene dataset from the Database of Essential Genes",
        "description": "Genes of 55 bacterial genomes with essentiality labels taken from the Database of Essential Genes version 15 and mapped onto NCBI GenBank assemblies.",
        "task": "essential-genes",
        "attributes": {
            "assay": "Essentiality annotations collected in the Database of Essential Genes version 15, mapped to genes of the downloaded assemblies by protein sequence, locus tag, UniProt and protein identifiers, gene name and length-based matching above 90% identity.",
            "total": 55,
            "positives": 21626,
            "negatives": 171587,
            "population": "55 genomes, after removing duplicates from the 66 genomes in the database; 193,213 proteins in total",
            "split": "Phylogeny-aware split by genus, 60/20/20",
            "repository": "https://huggingface.co/datasets/macwiatrak/bacbench-essential-genes-protein-sequences",
            "access": "Published as Hugging Face datasets in protein-sequence and DNA modalities.",
            "source_locator": "Methods 'Gene essentiality prediction and benchmarking'; BacBench README 'Datasets'",
            "label_semantics": "A gene is positive when the Database of Essential Genes labels it essential for the matching genome.",
            "reuse_restrictions": "Derived from the Database of Essential Genes and NCBI GenBank, whose own terms apply; the Hugging Face copies declare Apache-2.0 in their card metadata, which was not pinned as a source in this batch.",
        },
    },
    {
        "slug": "data-phenotypic-traits",
        "name": "BacBench phenotypic trait dataset",
        "description": "Categorical phenotypic trait labels for 24,462 genomes over 138 traits, collated from two trait catalogues with source-prefixed labels and an agreement filter, with genome sequences from NCBI GenBank.",
        "task": "phenotypic-traits",
        "attributes": {
            "assay": "Trait annotations collated from two published catalogues; traits present in both were kept only when Cohen's kappa between the sources reached 0.5.",
            "total": 24462,
            "population": "138 categorical traits across 24,462 genomes, after keeping traits with at least 500 genomes and classes with at least 50 samples",
            "split": "Per-trait phylogeny-aware split by genus, 60/20/20",
            "repository": "https://huggingface.co/datasets/macwiatrak/bacbench-phenotypic-traits-protein-sequences",
            "access": "Published as Hugging Face datasets in protein-sequence and DNA modalities.",
            "source_locator": "Methods 'Phenotypic traits prediction'; BacBench README 'Datasets'",
            "label_semantics": "Each label is a category of one trait, prefixed with the catalogue it came from so that collisions between the two catalogues are explicit.",
            "reuse_restrictions": "Derived from two third-party trait catalogues and NCBI GenBank, whose own terms apply; the Hugging Face copies declare Apache-2.0 in their card metadata, which was not pinned as a source in this batch.",
        },
    },
    {
        "slug": "data-amr-ncbi-ast",
        "name": "BacBench antibiotic resistance dataset from the NCBI AST browser",
        "description": "Antibiotic susceptibility readings from the NCBI Antibiotic Susceptibility Test browser matched to 26,052 GenBank genomes, as resistant or susceptible calls and as minimum inhibitory concentrations.",
        "task": "antibiotic-resistance",
        "attributes": {
            "assay": "Antibiotic susceptibility testing records from the NCBI AST browser, matched to genome assemblies by assembly identifier.",
            "total": 26052,
            "population": "26,052 unique genomes with matched resistance labels",
            "split": "Random 70/10/20 per antibiotic and seed, repeated over three random splits",
            "repository": "https://huggingface.co/datasets/macwiatrak/bacbench-antibiotic-resistance-protein-sequences",
            "access": "Published as Hugging Face datasets in protein-sequence and DNA modalities.",
            "source_locator": "Methods 'Predicting antimicrobial resistance'; Table S17; BacBench README 'Datasets'",
            "label_semantics": "Binary labels are the susceptible or resistant calls of the test record. Regression targets are the quoted minimum inhibitory concentration, with x for =, at most and at least, 2x for greater than and 0.5x for less than, then log(1+x) transformed.",
            "reuse_restrictions": "Derived from the NCBI AST browser and GenBank, whose own terms apply; the Hugging Face copies declare Apache-2.0 in their card metadata, which was not pinned as a source in this batch.",
        },
    },
    {
        "slug": "data-strain-clustering-mags",
        "name": "BacBench strain clustering dataset of 6,071 MGnify MAGs",
        "description": "A random sample of 6,071 metagenome-assembled genomes from MGnify spanning 25 species, 10 genera and 7 families, used to score genome clusterings against species labels.",
        "task": "strain-clustering",
        "attributes": {
            "assay": "Metagenome-assembled genomes from MGnify with their taxonomic labels; no new measurement.",
            "total": 6071,
            "population": "6,071 metagenome-assembled genomes across 25 species, 10 genera and 7 families",
            "split": "Evaluation only; all genomes are clustered",
            "repository": "https://huggingface.co/datasets/macwiatrak/bacbench-strain-clustering-protein-sequences-small",
            "access": "Published as Hugging Face datasets in protein-sequence and DNA modalities; the BacBench task that uses them is deprecated.",
            "source_locator": "Methods 'Strain clustering'; BacBench README 'Task overview'",
            "label_semantics": "Cluster quality is scored against the species label of each genome.",
            "reuse_restrictions": "Derived from MGnify, whose own terms apply; neither Hugging Face copy declares a licence in its card metadata.",
        },
    },
]

SUBSETS = [
    {
        "slug": "data-amr-binary",
        "name": "Antibiotic resistance binary prediction subset, 37 antibiotics",
        "description": "The antibiotics kept for the resistant or susceptible prediction setting: those with at least 500 labelled genomes in total and at least 50 genomes in each class.",
        "parent": "data-amr-ncbi-ast",
        "eligible": 37,
        "scope": "37 antibiotics with susceptible and resistant calls; Table S17 prints the resistant, susceptible and total genome count for each",
        "locator": "Methods 'Predicting antimicrobial resistance'; Table S17",
    },
    {
        "slug": "data-amr-regression",
        "name": "Antibiotic resistance MIC regression subset, 56 antibiotics",
        "description": "The antibiotics kept for the minimum inhibitory concentration regression setting: those with at least 500 available readings.",
        "parent": "data-amr-ncbi-ast",
        "eligible": 56,
        "scope": "56 antibiotics with quoted minimum inhibitory concentrations, log(1+x) transformed",
        "locator": "Methods 'Predicting antimicrobial resistance'",
    },
]

PROTOCOLS = [
    # (slug, table, task, dataset, column, metric, qualifier, unit, direction, extra)
    {
        "slug": "protocol-operon-zero-shot-auroc", "table": "S1", "task": "operon-identification", "data": "data-operon-long-read-rna-seq",
        "column": "AUROC", "metric": "auroc", "unit": "percent",
        "name": "BacBench operon identification, zero-shot AUROC",
        "qualifier": "zero-shot operon boundary prediction scored by embedding cosine similarity times a same-strand indicator, mean over the five sequenced strains",
    },
    {
        "slug": "protocol-operon-zero-shot-auprc", "table": "S1", "task": "operon-identification", "data": "data-operon-long-read-rna-seq",
        "column": "AUPRC", "metric": "auprc", "unit": "percent",
        "name": "BacBench operon identification, zero-shot AUPRC",
        "qualifier": "zero-shot operon boundary prediction scored by embedding cosine similarity times a same-strand indicator, mean over the five sequenced strains",
    },
    {
        "slug": "protocol-ppi-zero-shot-auroc", "table": "S13", "task": "protein-protein-interaction", "data": "data-ppi-stringdb",
        "column": "Zero-shot AUROC", "metric": "auroc", "unit": "percent",
        "name": "BacBench protein-protein interaction, zero-shot AUROC",
        "qualifier": "zero-shot pair scoring by embedding cosine similarity, genus-level split, mean over held-out test genomes",
    },
    {
        "slug": "protocol-ppi-zero-shot-auprc", "table": "S13", "task": "protein-protein-interaction", "data": "data-ppi-stringdb",
        "column": "Zero-shot AUPRC", "metric": "auprc", "unit": "percent",
        "name": "BacBench protein-protein interaction, zero-shot AUPRC",
        "qualifier": "zero-shot pair scoring by embedding cosine similarity, genus-level split, mean over held-out test genomes",
    },
    {
        "slug": "protocol-ppi-linear-probe-auroc", "table": "S13", "task": "protein-protein-interaction", "data": "data-ppi-stringdb",
        "column": "Finetuned AUROC", "metric": "auroc", "unit": "percent",
        "name": "BacBench protein-protein interaction, linear probe AUROC",
        "qualifier": "linear head on frozen pair embeddings plus their cosine similarity, genus-level split, mean over held-out test genomes",
    },
    {
        "slug": "protocol-ppi-linear-probe-auprc", "table": "S13", "task": "protein-protein-interaction", "data": "data-ppi-stringdb",
        "column": "Finetuned AUPRC", "metric": "auprc", "unit": "percent",
        "name": "BacBench protein-protein interaction, linear probe AUPRC",
        "qualifier": "linear head on frozen pair embeddings plus their cosine similarity, genus-level split, mean over held-out test genomes",
    },
    {
        "slug": "protocol-essential-genes-linear-probe-auroc", "table": "S14", "task": "essential-genes", "data": "data-essential-genes-deg",
        "column": "AUROC", "metric": "auroc", "unit": "percent",
        "name": "BacBench essential gene prediction, linear probe AUROC",
        "qualifier": "linear head on frozen gene embeddings, genus-level split, median over held-out test genomes",
    },
    {
        "slug": "protocol-essential-genes-linear-probe-auprc", "table": "S14", "task": "essential-genes", "data": "data-essential-genes-deg",
        "column": "AUPRC", "metric": "auprc", "unit": "percent",
        "name": "BacBench essential gene prediction, linear probe AUPRC",
        "qualifier": "linear head on frozen gene embeddings, genus-level split, median over held-out test genomes",
    },
    {
        "slug": "protocol-phenotypic-traits-linear-probe-auroc", "table": "S16", "task": "phenotypic-traits", "data": "data-phenotypic-traits",
        "column": "AUROC", "metric": "auroc", "unit": "percent",
        "name": "BacBench phenotypic trait prediction, linear probe AUROC",
        "qualifier": "linear head per trait on frozen genome embeddings, macro-averaged across classes of each trait, genus-level split, mean over traits and seeds",
    },
    {
        "slug": "protocol-phenotypic-traits-linear-probe-auprc", "table": "S16", "task": "phenotypic-traits", "data": "data-phenotypic-traits",
        "column": "AUPRC", "metric": "auprc", "unit": "percent",
        "name": "BacBench phenotypic trait prediction, linear probe AUPRC",
        "qualifier": "linear head per trait on frozen genome embeddings, macro-averaged across classes of each trait, genus-level split, mean over traits and seeds",
    },
    {
        "slug": "protocol-amr-binary-auroc", "table": "S18", "task": "antibiotic-resistance", "data": "data-amr-binary",
        "column": "Binary AUROC", "metric": "auroc", "unit": "percent",
        "name": "BacBench antibiotic resistance, binary linear probe AUROC",
        "qualifier": "linear head per drug on frozen genome embeddings, random 70/10/20 split, mean over 37 antibiotics",
    },
    {
        "slug": "protocol-amr-binary-auprc", "table": "S18", "task": "antibiotic-resistance", "data": "data-amr-binary",
        "column": "Binary AUPRC", "metric": "auprc", "unit": "percent",
        "name": "BacBench antibiotic resistance, binary linear probe AUPRC",
        "qualifier": "linear head per drug on frozen genome embeddings, random 70/10/20 split, mean over 37 antibiotics",
    },
    {
        "slug": "protocol-amr-regression-r2", "table": "S18", "task": "antibiotic-resistance", "data": "data-amr-regression",
        "column": "Regression R2", "metric": "coefficient-of-determination", "unit": "percent",
        "name": "BacBench antibiotic resistance, MIC regression R squared",
        "qualifier": "linear head per drug on frozen genome embeddings predicting log(1+MIC), random 70/10/20 split, mean over 56 antibiotics, printed as a percentage",
    },
    {
        "slug": "protocol-amr-regression-pearson", "table": "S18", "task": "antibiotic-resistance", "data": "data-amr-regression",
        "column": "Regression Pearson", "metric": "pearson-correlation", "unit": "percent",
        "name": "BacBench antibiotic resistance, MIC regression Pearson correlation",
        "qualifier": "linear head per drug on frozen genome embeddings predicting log(1+MIC), random 70/10/20 split, mean over 56 antibiotics, printed as a percentage",
    },
    {
        "slug": "protocol-strain-clustering-ari", "table": "S12", "task": "strain-clustering", "data": "data-strain-clustering-mags",
        "column": "ARI", "metric": "adjusted-rand-index", "unit": "unitless",
        "name": "BacBench strain clustering, adjusted Rand index",
        "qualifier": "Leiden clustering of mean-pooled genome embeddings scored against species labels, at the resolution and neighbour count that maximise the mean of the three reported metrics",
    },
    {
        "slug": "protocol-strain-clustering-nmi", "table": "S12", "task": "strain-clustering", "data": "data-strain-clustering-mags",
        "column": "NMI", "metric": "normalized-mutual-information", "unit": "unitless",
        "name": "BacBench strain clustering, normalised mutual information",
        "qualifier": "Leiden clustering of mean-pooled genome embeddings scored against species labels, at the resolution and neighbour count that maximise the mean of the three reported metrics",
    },
    {
        "slug": "protocol-strain-clustering-asw", "table": "S12", "task": "strain-clustering", "data": "data-strain-clustering-mags",
        "column": "ASW", "metric": "silhouette-score", "unit": "unitless",
        "name": "BacBench strain clustering, average silhouette width",
        "qualifier": "average silhouette width of the Leiden clustering of mean-pooled genome embeddings, at the resolution and neighbour count that maximise the mean of the three reported metrics",
    },
]

TABLE_INFO = {
    "S1": {
        "caption": "Table S1. Overall operon identification performance across methods. Values are mean ± standard deviation; best value for each metric is bolded.",
        "procedure": (
            "Zero-shot. For each pair of contiguous genes the score is the cosine similarity between the two gene "
            "embeddings multiplied by an indicator that both genes are on the same strand; the intergenic-distance "
            "term of the Bacformer operon model is deliberately left out so that the comparison is about the "
            "embeddings. Performance is averaged across all five sequenced strains."
        ),
        "aggregation": "Mean and standard deviation over the five sequenced strains",
        "scope": "across the five long-read RNA sequenced strains",
        "n": 5,
        "budget": "Under 5 minutes for all models on one NVIDIA H100 with 96 GB of memory and 72 CPU cores, excluding the cost of embedding the genomes",
        "limitations": [
            "The operon labels come from long-read RNA sequencing of five strains only, so the mean is over five values.",
            "The benchmark score deliberately drops the intergenic-distance term used by the paper's own operon model, so it is not the operon method the paper proposes.",
        ],
    },
    "S13": {
        "caption": "Table S13. Protein-protein interaction performance on held-out genomes. Values are mean ± standard deviation across test genomes; best value for each metric is bolded.",
        "procedure": (
            "Zero-shot columns score each protein pair by the cosine similarity of the two embeddings. The finetuned "
            "columns train a single linear layer, preceded by layer normalisation and dropout of 0.2, on the average "
            "of the two frozen protein embeddings together with their cosine similarity, so the input is of dimension "
            "D plus one; binary cross-entropy loss, Adam with weight decay 0.01, at most 20 epochs with early stopping "
            "patience 5 on AUROC, and a learning-rate sweep per model. Metrics are computed per genome on the test split."
        ),
        "aggregation": "Mean and standard deviation across held-out test genomes",
        "scope": "across held-out test genomes",
        "n": None,
        "budget": "About 90 minutes for the zero-shot evaluation of all models and 91 hours for the finetuning including the learning-rate sweep, on one NVIDIA H100 with 96 GB of memory and 72 CPU cores, excluding the cost of embedding the genomes",
        "limitations": [
            "STRING DB combined scores are themselves predictions pooled from several evidence channels, not direct interaction measurements.",
            "The positive threshold of 0.6 was chosen on validation AUROC and AUPRC, so the label definition is tuned on the same metrics that are reported.",
            "The number of test genomes behind each mean is not printed.",
        ],
    },
    "S14": {
        "caption": "Table S14. Performance on gene-essentiality prediction. Values are median ± standard deviation over test genomes; the best score for each metric is highlighted in bold.",
        "procedure": (
            "The backbone is frozen and a single linear layer, preceded by dropout of 0.2 and layer normalisation, is "
            "trained on the gene embeddings with binary cross-entropy loss, at most 100 epochs, early stopping patience "
            "10 on macro AUROC over validation genomes, Adam with weight decay 0.02, and a learning-rate sweep per model. "
            "Evo and Evo-2 are reported without layer normalisation, which the authors state worked better for them."
        ),
        "aggregation": "Median over held-out test genomes, with a standard deviation over the same genomes",
        "scope": "over held-out test genomes",
        "n": None,
        "budget": "About 5 hours on one NVIDIA H100 with 96 GB of memory and 72 CPU cores, including the learning-rate sweep and testing, excluding the cost of embedding the genomes",
        "limitations": [
            "The central value is a median while the spread is a standard deviation, so the two are not the same statistic.",
            "Two of the twelve systems are reported without layer normalisation, so the head is not identical across rows.",
            "Essentiality labels are collected across studies and conditions in the Database of Essential Genes rather than measured under one protocol.",
            "The number of test genomes behind each median is not printed.",
        ],
    },
    "S16": {
        "caption": "Table S16. Overall phenotypic traits prediction performance across all phenotypes. Values are mean ± standard deviation across 5 seeds. The results were macro-averaged across classes for each phenotype. Best value for each metric is bolded.",
        "procedure": (
            "One linear model per trait on mean-pooled whole-genome embeddings: a single layer preceded by dropout of 0.1 "
            "and layer normalisation, cross-entropy loss, at most 100 epochs, early stopping patience 10 on validation "
            "AUROC, a learning-rate sweep per model across seeds and traits, and no class weighting. Scores are "
            "macro-averaged across the classes of each trait."
        ),
        "aggregation": "Mean and standard deviation across seeds, over macro-averaged per-trait scores",
        "scope": "across 5 seeds according to the table caption; the Methods state three independent runs with different data splits",
        "n": None,
        "budget": "About 19 hours on one NVIDIA H100 with 96 GB of memory and 72 CPU cores, including tuning, training and testing for all models across seeds, excluding the cost of embedding the genomes",
        "limitations": [
            "The caption says the spread is across 5 seeds while the Methods say the split was repeated across three independent runs; the source does not reconcile the two.",
            "Traits are pooled: one number stands for 138 traits of very different prevalence and difficulty.",
            "Trait labels come from two catalogues that agree only above a Cohen's kappa of 0.5 for shared traits.",
        ],
    },
    "S18": {
        "caption": "Table S18. Performance (percent, higher is better) on antibiotic-resistance prediction tasks across drugs. Values are mean ± standard deviation across antibiotics; best value for each metric is bolded.",
        "procedure": (
            "One linear model per drug on mean-pooled whole-genome embeddings: a single layer preceded by dropout of 0.1 "
            "and layer normalisation, binary cross-entropy for the resistant or susceptible setting and mean squared "
            "error for the log(1+MIC) regression, at most 100 epochs, early stopping patience 10 on validation AUROC or "
            "validation R squared, a learning-rate sweep per model across seeds and drugs, Adam with weight decay 0.01, "
            "and three random splits."
        ),
        "aggregation": "Mean and standard deviation across antibiotics",
        "scope": "across antibiotics",
        "n": None,
        "budget": "About 50 hours on one NVIDIA H100 with 96 GB of memory and 72 CPU cores, including tuning, training and testing for all models across seeds, excluding the cost of embedding the genomes",
        "limitations": [
            "The split is random rather than phylogeny-aware, which the authors justify by the small number of labelled strains per drug and the species specificity of resistance; genomes of the same genus can therefore fall on both sides of the split.",
            "Per-drug sample sizes vary by more than an order of magnitude, which the authors name as a reason for the high variance across drugs.",
            "R squared and the Pearson correlation are printed as percentages rather than on their natural scales.",
        ],
    },
    "S12": {
        "caption": "Table S12. Clustering performance across species-level genome clustering, reported as Adjusted Rand Index (ARI), Normalised Mutual Information (NMI), and Average Silhouette Width (ASW). Best value for each metric is bolded. Mean ± standard deviation, where standard deviation was computed by performing 10 independent bootstrap resamples, each using 80% of the data.",
        "procedure": (
            "Final-layer hidden states are mean-pooled into one vector per genome and clustered with Leiden over a grid "
            "of resolutions 0.1, 0.25, 0.5 and 1.0 and neighbour counts 5, 10 and 15; the combination that maximises the "
            "mean of the adjusted Rand index, normalised mutual information and average silhouette width at the species "
            "level is retained. Clustering is run with Scanpy."
        ),
        "aggregation": "Mean over 10 bootstrap resamples, each of 80% of the genomes, with the standard deviation over the same resamples",
        "scope": "over 10 bootstrap resamples, each using 80% of the 6,071 genomes",
        "n": None,
        "budget": "Not stated for this table",
        "limitations": [
            "The clustering hyperparameters are chosen to maximise the mean of the three metrics that are then reported, on the same data, so the values are a best-of-grid rather than a held-out measurement.",
            "BacBench deprecated the strain clustering task on 2026-05-13, so this table does not correspond to a current BacBench task.",
            "Only six of the twelve benchmarked systems appear; the average amino-acid identity and average nucleotide identity comparisons described in the Methods are not in this table.",
        ],
    },
}


def benchmark_and_tasks() -> None:
    add({
        "id": f"{P}benchmark-bacbench",
        "kind": "benchmark",
        "name": "BacBench",
        "description": "BacBench is a multi-task benchmark for machine-learning models of bacterial genomics, which embeds whole genomes with a chosen model and scores the embeddings on five active tasks across the bacterial tree of life.",
        "status": "needs_review",
        "facets": dict(MICROBIAL),
        "source_ids": [f"{P}source-bacbench-readme", f"{P}source-preprint-v3"],
        "links": [],
        "attributes": {
            "entity_level": "suite",
            "version": f"BacBench repository at commit {BACBENCH_COMMIT}, README retrieved 2026-11-15",
            "task": "Embedding bacterial genomes with genomic language models and scoring the embeddings on essential gene prediction, operon identification, protein-protein interaction, antibiotic resistance and phenotypic trait prediction",
            "executable_suite": True,
            "runner": "Per-task scripts under bacbench/modeling for embedding and bacbench/tasks for evaluation, run from the repository",
            "scope_note": (
                "Five active tasks as of the pinned commit, with the strain clustering task deprecated but kept in the "
                "repository for reproducibility. Datasets are published on Hugging Face in DNA and protein-sequence "
                "modalities. The README prints no numeric results; a model leaderboard for each task is on its to-do list."
            ),
            "limitations": [
                "The repository prints no numeric task results, so every number in this batch comes from the Bacformer preprint instead.",
                "Its 'Benchmarked models' table gives Bacformer Large 27M parameters, which the Bacformer README, the model cards and the preprint all contradict, and it differs from preprint Table S9 on several other parameter counts and context lengths.",
                "The essential gene and protein-protein interaction tasks changed to phylogeny-aware genus splits on 2026-05-13, so results from before that date are not on the current protocol.",
                "Dataset licences are declared only in Hugging Face card metadata, which this batch did not pin as sources.",
            ],
            "missing_metadata": {
                "split_manifest": {"reason": "unreported", "note": "No split manifest or seed list is published in the repository README; the splits are described in prose in the preprint."},
                "protocol_version": {"reason": "unreported", "note": "The repository is not versioned by releases; it is pinned here by commit."},
            },
            "source_locator": "BacBench README opening paragraph, 'News', 'Benchmarked models', 'Task overview' and 'To-do-list'",
            "review": text_review(BACBENCH_README_SHA, f"https://raw.githubusercontent.com/macwiatrak/BacBench/{BACBENCH_COMMIT}/README.md", "Suite record read from the pinned README; the task list and the deprecation were taken from its own 'Task overview' table."),
        },
    })
    for task in TASKS:
        add({
            "id": f"{P}task-{task['slug']}",
            "kind": "task",
            "name": f"BacBench {task['name']}",
            "description": task["scope_note"],
            "status": "needs_review",
            "facets": facets(*task["areas"]),
            "source_ids": [f"{P}source-bacbench-readme", f"{P}source-preprint-v3"],
            "links": [{"relation": "part_of", "target_id": f"{P}benchmark-bacbench"}],
            "attributes": {
                "task": task["name"],
                "task_type": task["task_type"],
                "scope_note": f"{task['scope_note']} BacBench lists this task as {task['status_text'].lower()}.",
                "splits": task["splits"],
                "version": f"BacBench repository at commit {BACBENCH_COMMIT}",
                "source_locator": "BacBench README 'Task overview' table and 'Datasets'; preprint Methods 'Downstream tasks & analysis'",
            },
        })
    for dataset in DATASETS:
        attrs = dict(dataset["attributes"])
        attrs["version"] = "As described in version 3 of the preprint and published on Hugging Face"
        attrs["review"] = preprint_review("Counts and construction read from the Methods; dataset locations cross-checked against the pinned BacBench README.")
        add({
            "id": P + dataset["slug"],
            "kind": "dataset",
            "name": dataset["name"],
            "description": dataset["description"],
            "status": "needs_review",
            "facets": facets(*next(t["areas"] for t in TASKS if t["slug"] == dataset["task"])),
            "source_ids": [f"{P}source-preprint-v3", f"{P}source-bacbench-readme"],
            "links": [],
            "attributes": attrs,
        })
    for subset in SUBSETS:
        add({
            "id": P + subset["slug"],
            "kind": "dataset_subset",
            "name": subset["name"],
            "description": subset["description"],
            "status": "needs_review",
            "facets": dict(MICROBIAL),
            "source_ids": [f"{P}source-preprint-v3"],
            "links": [{"relation": "same_data_as", "target_id": P + subset["parent"]}],
            "attributes": {
                "source_dataset": P + subset["parent"],
                "subset_scope": subset["scope"],
                "eligible_count": subset["eligible"],
                "split": "Random 70/10/20 per antibiotic and seed, repeated over three random splits",
                "source_locator": subset["locator"],
                "version": "As described in version 3 of the preprint",
                "review": preprint_review("Antibiotic counts read from the Methods; Table S17 prints the per-drug genome counts of the binary setting."),
            },
        })


def protocols() -> None:
    for protocol in PROTOCOLS:
        info = TABLE_INFO[protocol["table"]]
        data_id = P + protocol["data"]
        add({
            "id": P + protocol["slug"],
            "kind": "protocol",
            "name": protocol["name"],
            "description": f"{protocol['name']} as measured in the Bacformer preprint benchmark.",
            "status": "needs_review",
            "facets": facets(*next(t["areas"] for t in TASKS if t["slug"] == protocol["task"])),
            "source_ids": [f"{P}source-preprint-v3"],
            "links": [
                {"relation": "part_of", "target_id": f"{P}benchmark-bacbench"},
                {"relation": "evaluates_task", "target_id": f"{P}task-{protocol['task']}"},
                {"relation": "uses_data", "target_id": data_id},
            ],
            "attributes": {
                "metric": protocol["metric"],
                "metric_direction": "higher",
                "metric_qualifier": protocol["qualifier"],
                "unit": protocol["unit"],
                "metric_definition": info["caption"],
                "aggregation": info["aggregation"],
                "protocol": info["procedure"],
                "scope_note": "Split: " + next(t["splits"] for t in TASKS if t["slug"] == protocol["task"]),
                "uncertainty_reporting": {
                    "type": "standard_deviation",
                    "scope": info["scope"],
                    "printed_with_value": True,
                },
                "limitations": info["limitations"],
                "access_note": (
                    "The evaluation scripts are in the BacBench repository; the preprint does not state the commit used "
                    "for these runs, and no split manifest is published."
                ),
                "reproducibility_note": (
                    "Not reproduced by Rewire. The datasets and code are public, but the exact splits, seeds and "
                    "repository commit behind these numbers are not published."
                ),
                "publication_status": "preprint",
                "source_table": int(protocol["table"][1:]),
                "source_locator": f"Table {protocol['table']}, column '{protocol['column']}'",
                "version": "As printed in version 3 of the preprint",
                "missing_metadata": {
                    "random_seeds": {"reason": "unreported", "note": "Seed values are not printed; only the number of repeats where stated."},
                },
                "review": preprint_review(f"Metric, direction and aggregation read from the caption of Table {protocol['table']} and the matching Methods section."),
            },
        })
        if protocol["unit"] == "percent":
            RECORDS[-1]["attributes"]["unit_detail"] = "Printed on a 0 to 100 scale"


# ---------------------------------------------------------------- evaluations and results

CONFIG_FOR = {
    "S1": lambda slug: f"{P}config-{slug}-zero-shot",
    "S12": lambda slug: (
        f"{P}config-{slug}-zero-shot-clustering" if slug in ("bacformer", "bacformer-large") else f"{P}config-{slug}-zero-shot"
    ),
    "S13-zero": lambda slug: f"{P}config-{slug}-zero-shot",
    "S13-probe": lambda slug: f"{P}config-{slug}-linear-probe",
    "S14": lambda slug: f"{P}config-{slug}-linear-probe",
    "S16": lambda slug: f"{P}config-{slug}-linear-probe",
    "S18": lambda slug: f"{P}config-{slug}-linear-probe",
}

METRIC_SLUG = {
    "AUROC": "auroc",
    "AUPRC": "auprc",
    "ARI": "ari",
    "NMI": "nmi",
    "ASW": "asw",
    "Zero-shot AUROC": "zero-shot-auroc",
    "Zero-shot AUPRC": "zero-shot-auprc",
    "Finetuned AUROC": "probe-auroc",
    "Finetuned AUPRC": "probe-auprc",
    "Binary AUROC": "binary-auroc",
    "Binary AUPRC": "binary-auprc",
    "Regression R2": "regression-r2",
    "Regression Pearson": "regression-pearson",
}
TASK_SLUG_SHORT = {
    "S1": "operon",
    "S12": "strain-clustering",
    "S13": "ppi",
    "S14": "essential-genes",
    "S16": "phenotypic-traits",
    "S18": "amr",
}


def population_for(data_slug: str) -> str:
    """The scored population of a dataset or, for the antibiotic resistance subsets, of the subset."""
    for subset in SUBSETS:
        if subset["slug"] == data_slug:
            parent = next(d for d in DATASETS if d["slug"] == subset["parent"])
            return f"{subset['scope']}; drawn from {parent['attributes']['population']}"
    dataset = next(d for d in DATASETS if d["slug"] == data_slug)
    return dataset["attributes"].get("population") or dataset["attributes"]["species"]


def protocol_for(table: str, column: str) -> dict:
    for protocol in PROTOCOLS:
        if protocol["table"] == table and protocol["column"] == column:
            return protocol
    raise SystemExit(f"no protocol for {table} {column}")


def evaluations_and_results(tables: dict) -> None:
    for table_key in ("S1", "S12", "S13", "S14", "S16", "S18"):
        table = tables[table_key]
        info = TABLE_INFO[table_key]
        for row in table["rows"]:
            system = SYSTEM_BY_NAME[row["label"]]
            for cell in row["cells"]:
                protocol = protocol_for(table_key, cell["column"])
                if table_key == "S13":
                    config_key = "S13-probe" if cell["column"].startswith("Finetuned") else "S13-zero"
                else:
                    config_key = table_key
                config_id = CONFIG_FOR[config_key](system["slug"])
                data_id = P + protocol["data"]
                suffix = f"{TASK_SLUG_SHORT[table_key]}-{system['slug']}-{METRIC_SLUG[cell['column']]}"
                eval_id = f"{P}eval-{suffix}"
                result_id = f"{P}result-{suffix}"
                adaptation = (
                    "Linear head trained on frozen embeddings"
                    if "probe" in config_id or "linear-probe" in config_id
                    else "No training; embeddings scored directly"
                )
                n_value = info["n"]
                uncertainty = {
                    "type": "standard_deviation",
                    "value": cell["standard_deviation"],
                    "printed": cell["printed_value"],
                    "scope": info["scope"],
                    "unit": protocol["unit"],
                    "source_column": cell["column"],
                }
                if n_value:
                    uncertainty["n"] = n_value
                if table_key == "S12":
                    uncertainty["method"] = "bootstrap"
                    uncertainty["resamples"] = 10
                if table_key == "S18":
                    uncertainty["n"] = 37 if cell["column"].startswith("Binary") else 56
                    uncertainty["note"] = (
                        "The caption says the spread is across antibiotics; the Methods state 37 antibiotics in the "
                        "binary setting and 56 in the regression setting."
                    )
                add({
                    "id": eval_id,
                    "kind": "evaluation",
                    "name": f"{system['name']} on {protocol['name']}",
                    "description": f"{system['name']} scored on the protocol '{protocol['name']}' in the Bacformer preprint benchmark.",
                    "status": "needs_review",
                    "facets": {},
                    "source_ids": [f"{P}source-preprint-v3"],
                    "links": [
                        {"relation": "system", "target_id": config_id},
                        {"relation": "assessment", "target_id": P + protocol["slug"]},
                        {"relation": "data", "target_id": data_id},
                    ],
                    "attributes": {
                        "origin": "author_reported",
                        "protocol": info["procedure"],
                        "version": "As printed in version 3 of the preprint",
                        "comparison": {
                            "protocol_id": P + protocol["slug"],
                            "dataset_version": "As described in version 3 of the preprint and published on Hugging Face",
                            "split": next(t["splits"] for t in TASKS if t["slug"] == protocol["task"]),
                            "population": population_for(protocol["data"]),
                            "inputs": f"{system['modality']}. {EMBEDDING_RECIPE[system['modality']]}",
                            "adaptation": adaptation,
                            "metric_implementation": protocol["qualifier"],
                            "aggregation": info["aggregation"],
                            "budget": info["budget"],
                        },
                        "limitations": [
                            "Reported by the authors of Bacformer, who also built BacBench and ran every benchmarked model on it.",
                            "Not reproduced by Rewire; the exact splits, seeds and BacBench commit behind the runs are not published.",
                        ],
                        "source_locator": f"Table {table_key}, row '{row['label']}', column '{cell['column']}'",
                        "review": preprint_review(f"One evaluation per printed cell of Table {table_key}."),
                    },
                })
                result_attrs = {
                    "printed_value": cell["printed_value"],
                    "numeric_value": cell["mean"],
                    "metric": protocol["metric"],
                    "metric_direction": "higher",
                    "metric_qualifier": protocol["qualifier"],
                    "unit": protocol["unit"],
                    "uncertainty": uncertainty,
                    "source_table": table_key,
                    "source_locator": f"Table {table_key}, row '{row['label']}', column '{cell['column']}'",
                    "review": preprint_review(
                        "Printed value, mean and standard deviation parsed from the pinned text layer and rechecked by "
                        "column position."
                    ),
                }
                if protocol["unit"] == "percent":
                    result_attrs["unit_detail"] = "Printed on a 0 to 100 scale"
                if table_key == "S16":
                    result_attrs["source_warnings"] = [
                        "The caption says the standard deviation is across 5 seeds; the Methods say the split was repeated across three independent runs. The source does not reconcile the two."
                    ]
                if table_key == "S12":
                    result_attrs["source_warnings"] = [
                        "The clustering resolution and neighbour count were chosen to maximise the mean of the three metrics reported in this table, on the same data.",
                        "Neither source states which Bacformer checkpoint produced this table; Table S9 names the complete-genome checkpoint for the study while the BacBench README footnote says strain clustering used the MAG checkpoint.",
                    ] if system["slug"].startswith("bacformer") else [
                        "The clustering resolution and neighbour count were chosen to maximise the mean of the three metrics reported in this table, on the same data."
                    ]
                if cell["standard_deviation"] == "0.00":
                    result_attrs["rounding_note"] = "The printed spread is 0.00, which the source does not explain."
                add({
                    "id": result_id,
                    "kind": "result",
                    "name": f"{system['name']}, {protocol['name']}",
                    "description": "Value transcribed from the pinned preprint table. Not independently reproduced.",
                    "status": "needs_review",
                    "facets": {},
                    "source_ids": [f"{P}source-preprint-v3"],
                    "links": [{"relation": "evaluation", "target_id": eval_id}],
                    "attributes": result_attrs,
                })


# ---------------------------------------------------------------- claims

def claim(slug: str, subject: str, field: str, value: str, locator: str, source_ids: list[str], rationale: str, review_block: dict, name: str, limitations: list[str] | None = None) -> None:
    attrs = {
        "field": field,
        "value": value,
        "source_locator": locator,
        "rationale": rationale,
        "review": review_block,
    }
    if limitations:
        attrs["limitations"] = limitations
    add({
        "id": f"{P}claim-{slug}",
        "kind": "claim",
        "name": name,
        "description": rationale,
        "status": "needs_review",
        "facets": dict(MICROBIAL),
        "source_ids": source_ids,
        "links": [{"relation": "subject", "target_id": subject}],
        "attributes": attrs,
    })


def claims() -> None:
    bacformer = f"{P}model-bacformer"
    large = f"{P}model-bacformer-large"
    readme_review = text_review(BACFORMER_README_SHA, f"https://raw.githubusercontent.com/macwiatrak/Bacformer/{BACFORMER_COMMIT}/README.md", "Read from the pinned README.")
    bacbench_review = text_review(BACBENCH_README_SHA, f"https://raw.githubusercontent.com/macwiatrak/BacBench/{BACBENCH_COMMIT}/README.md", "Read from the pinned README.")

    def card_review(slug: str) -> dict:
        revision, sha, _ = CARDS[slug]
        return text_review(sha, f"https://huggingface.co/macwiatrak/{slug}/raw/{revision}/README.md", "Read from the pinned model card.")

    # Parameter counts, one claim per printed figure.
    claim(
        "bacformer-parameters-readme-26m", bacformer, "parameter_count", "26M",
        "Bacformer README, 'Requirements': 'Bacformer (26M parameters) uses ESM-2 (esm2_t12_35M_UR50D)'",
        [f"{P}source-bacformer-readme"],
        "The Bacformer README gives the base model 26M parameters, which the model cards and the preprint's Table S9 contradict.",
        readme_review, "Bacformer base parameter count printed in the repository README",
        ["One of five printed figures for this model's size; the sources disagree and the disagreement is unresolved."],
    )
    claim(
        "bacformer-parameters-card-27m", bacformer, "parameter_count", "27M",
        "Hugging Face model card for macwiatrak/bacformer-masked-MAG: 'a 27M-parameter base transformer model'",
        [CARD_SOURCE["bacformer-masked-MAG"], CARD_SOURCE["bacformer-masked-complete-genomes"], CARD_SOURCE["bacformer-causal-MAG"], CARD_SOURCE["bacformer-causal-complete-genomes"]],
        "All four base model cards give the base model 27M parameters, against the 26M of the repository README.",
        card_review("bacformer-masked-MAG"), "Bacformer base parameter count printed on the model cards",
        ["One of five printed figures for this model's size; the sources disagree and the disagreement is unresolved."],
    )
    claim(
        "bacformer-parameters-preprint-s9-27m", bacformer, "parameter_count", "27M",
        "Table S9, row 'Bacformer', column 'Params'",
        [f"{P}source-preprint-v3"],
        "Table S9 of the preprint gives Bacformer 27M parameters.",
        preprint_review("Read from Table S9."), "Bacformer base parameter count printed in preprint Table S9",
        ["Table S11 of the same source prints 26M for the same model."],
    )
    claim(
        "bacformer-parameters-preprint-s11-26m", bacformer, "parameter_count", "26M",
        "Table S11, row 'Bacformer (26M)'",
        [f"{P}source-preprint-v3"],
        "Table S11 of the preprint labels the same model 26M, so the preprint disagrees with itself about the base size.",
        preprint_review("Read from the Table S11 row label."), "Bacformer base parameter count printed in preprint Table S11",
        ["Table S9 of the same source prints 27M for the same model."],
    )
    claim(
        "bacformer-parameters-bacbench-27m", bacformer, "parameter_count", "27M",
        "BacBench README, 'Benchmarked models' table, row 'Bacformer', column 'Params'",
        [f"{P}source-bacbench-readme"],
        "The BacBench model table gives Bacformer 27M parameters with an output dimension of 480.",
        bacbench_review, "Bacformer base parameter count printed in the BacBench README",
    )
    claim(
        "bacformer-large-parameters-readme-300m", large, "parameter_count", "300M",
        "Bacformer README, 'News' entry of 2025-01-20 and 'Requirements': 'Bacformer Large (300M parameters) uses ESM-C'",
        [f"{P}source-bacformer-readme"],
        "The Bacformer README gives Bacformer Large 300M parameters.",
        readme_review, "Bacformer Large parameter count printed in the repository README",
        ["The preprint prints 332M for the same model and the BacBench README prints 27M."],
    )
    claim(
        "bacformer-large-parameters-card-300m", large, "parameter_count", "300M",
        "Hugging Face model cards for macwiatrak/bacformer-large-masked-MAG and macwiatrak/bacformer-large-masked-complete-genomes: 'Number of parameters: Bacformer Large is much larger (>300M parameters)' and '300M-parameter'",
        [CARD_SOURCE["bacformer-large-masked-MAG"], CARD_SOURCE["bacformer-large-masked-complete-genomes"]],
        "Both Bacformer Large model cards give 300M parameters, stated once as more than 300M.",
        card_review("bacformer-large-masked-MAG"), "Bacformer Large parameter count printed on the model cards",
        ["The preprint prints 332M for the same model and the BacBench README prints 27M."],
    )
    claim(
        "bacformer-large-parameters-preprint-332m", large, "parameter_count", "332M",
        "Table S9, row 'Bacformer Large', column 'Params'; Table S11, row 'Bacformer Large (332M)'",
        [f"{P}source-preprint-v3"],
        "The preprint gives Bacformer Large 332M parameters in both of its model tables, the same figure it gives ESM-C.",
        preprint_review("Read from Tables S9 and S11."), "Bacformer Large parameter count printed in the preprint",
        ["Equal to the figure the same table gives the ESM-C base model, which is worth checking against the released weights."],
    )
    claim(
        "bacformer-large-parameters-bacbench-27m", large, "parameter_count", "27M",
        "BacBench README, 'Benchmarked models' table, row 'Bacformer Large', columns 'Params' and 'dim'",
        [f"{P}source-bacbench-readme"],
        "The BacBench model table gives Bacformer Large 27M parameters, the same figure as its Bacformer row, while giving it the larger output dimension of 960.",
        bacbench_review, "Bacformer Large parameter count printed in the BacBench README",
        ["Contradicted by the Bacformer README, the model cards and the preprint; recorded as printed and left for review."],
    )
    claim(
        "model-table-parameter-differences", f"{P}benchmark-bacbench", "model_table_differences",
        "The BacBench README and preprint Table S9 disagree on Nucleotide Transformer (250M against 235M), ProkBERT (27M against 26M), ESM-C (300M against 332M), ProtBert (420M against 412M), Bacformer Large (27M against 332M) and on the ESM-C context length (2,048 against 1,024 tokens)",
        "BacBench README 'Benchmarked models' table against preprint Table S9",
        [f"{P}source-bacbench-readme", f"{P}source-preprint-v3"],
        "The two official model tables of the same project disagree on several parameter counts and context lengths, so neither can be taken as the project's single statement of model size.",
        bacbench_review, "Model table differences between the BacBench README and the preprint",
    )
    # What the model does.
    claim(
        "bacformer-inputs-outputs", bacformer, "inputs_and_outputs",
        "Inputs are the protein sequences encoded by a genome, embedded one by one with a base protein language model and ordered by their coordinates on the chromosome and plasmids; outputs are contextual protein embeddings, a mean-pooled genome embedding, and protein-family predictions from the pretraining head",
        "Bacformer README opening paragraph and 'Usage'; model card 'Architecture'; preprint Methods 'Bacformer'",
        [f"{P}source-bacformer-readme", CARD_SOURCE["bacformer-masked-MAG"], f"{P}source-preprint-v3"],
        "Recorded because Bacformer is not a DNA model: it never reads nucleotides, and its outputs are embeddings or protein-family labels rather than predictions of a biological endpoint.",
        readme_review, "What Bacformer takes as input and returns",
    )
    claim(
        "bacformer-pretraining-objective", bacformer, "pretraining_objective",
        "Predict the protein family of masked proteins, or the next protein family, from the other proteins in the genome, over a vocabulary of 50,000 protein-family clusters obtained by unsupervised clustering of protein embeddings; 15% of proteins are masked, of which 87.5% are replaced by the mask token and 12.5% are left unchanged",
        "Hugging Face model card for macwiatrak/bacformer-masked-MAG, 'Pretraining' and 'Pretraining classification head'",
        [CARD_SOURCE["bacformer-masked-MAG"]],
        "The input is the exact protein sequence while the prediction target is a discrete protein family, which is what makes the model usable at amino-acid level while still allowing pretraining.",
        card_review("bacformer-masked-MAG"), "Bacformer pretraining objective and protein-family vocabulary",
    )
    claim(
        "bacformer-training-corpus", bacformer, "training_data",
        "A MAG corpus of more than 1.3 million metagenome-assembled genomes, 3 billion proteins and 225 million contigs, collected across about 25,000 species and 70 environments from MGnify and SPIRE",
        "Preprint Figure 1 legend, panel A; Methods 'Data'; model card 'Training Data'",
        [f"{P}source-preprint-v3", CARD_SOURCE["bacformer-masked-MAG"]],
        "The pretraining corpus is the basis of every claim about generalisation across the bacterial tree of life, and overlaps with the MGnify genomes used in the deprecated clustering task.",
        preprint_review("Read from the Figure 1 legend and the Methods."), "Bacformer pretraining corpus",
    )
    claim(
        "bacformer-complete-genome-finetune", bacformer, "complete_genome_pretraining",
        "The complete-genome checkpoints are initialised from the corresponding MAG checkpoint and further pretrained on about 40,000 complete genomes from NCBI RefSeq, so the MAG and complete-genome checkpoints are different configurations of the same architecture",
        "Hugging Face model cards for macwiatrak/bacformer-masked-complete-genomes and macwiatrak/bacformer-large-masked-complete-genomes: 'This model was initialised from ... and further pretrained on ~40 k complete genomes'",
        [CARD_SOURCE["bacformer-masked-complete-genomes"], CARD_SOURCE["bacformer-large-masked-complete-genomes"], f"{P}source-bacformer-readme"],
        "Recorded because results must not be moved between the MAG and complete-genome checkpoints: they differ by a further pretraining stage on a different genome type.",
        card_review("bacformer-masked-complete-genomes"), "MAG and complete-genome checkpoints are distinct",
    )
    claim(
        "bacformer-readme-checkpoint-table-conflict", f"{P}model-bacformer-large-masked-complete-genomes", "training_data_conflict",
        "The README checkpoint table describes bacformer-large-masked-complete-genomes as 'A 300M parameter model pretrained on the ~1.3 M metagenome-assembled genomes (MAG) with a masked objective', repeating the text of the MAG row, while its own model card says it was initialised from bacformer-large-masked-MAG and further pretrained on about 40,000 complete RefSeq genomes",
        "Bacformer README 'Pretrained model checkpoints' table, row 'bacformer-large-masked-complete-genomes', against the model card body",
        [f"{P}source-bacformer-readme", CARD_SOURCE["bacformer-large-masked-complete-genomes"]],
        "Two official sources describe the same checkpoint's training differently; the checkpoint record follows the model card and this claim keeps the README's wording on the record.",
        readme_review, "README checkpoint table conflicts with the model card on training data",
    )
    claim(
        "bacformer-context-limits", bacformer, "context_limits",
        "At most 6,000 proteins per genome, which the authors state covers more than 98% of the genomes in the training corpus, and at most 1,024 amino acids per protein",
        "Hugging Face model card for macwiatrak/bacformer-masked-MAG, 'Preprocessing' and 'Pretraining details'; preprint Table S10 footnote",
        [CARD_SOURCE["bacformer-masked-MAG"], f"{P}source-preprint-v3"],
        "The protein limit is the model's context, so genomes with more proteins than the limit are truncated, which bears on large genomes such as Streptomyces.",
        card_review("bacformer-masked-MAG"), "Bacformer context limits in proteins and amino acids",
    )
    claim(
        "bacformer-base-plm-esm2", bacformer, "base_protein_language_model",
        "ESM-2 t12 35M (facebook/esm2_t12_35M_UR50D), whose 480-dimensional mean-pooled per-protein embeddings are the input tokens",
        "Bacformer README 'Requirements'; model card 'Architecture'; preprint Table S9 and Methods 'Bacformer'",
        [f"{P}source-bacformer-readme", CARD_SOURCE["bacformer-masked-MAG"], f"{P}source-preprint-v3"],
        "Bacformer cannot run without the upstream protein language model, so the dependency is part of its identity and its terms are not the Bacformer licence.",
        readme_review, "Base protein language model of Bacformer",
    )
    claim(
        "bacformer-large-base-plm-card", large, "base_protein_language_model",
        "ESM-C 300M (EvolutionaryScale/esmc-300m-2024-12), with 960-dimensional per-protein embeddings",
        "Hugging Face model cards for the Bacformer Large checkpoints, 'Architecture'; preprint Table S9 row 'ESM-C' checkpoint 'esmc_300m'",
        [CARD_SOURCE["bacformer-large-masked-MAG"], f"{P}source-preprint-v3"],
        "The model cards and the preprint name the EvolutionaryScale ESM-C checkpoint as the base model of Bacformer Large.",
        card_review("bacformer-large-masked-MAG"), "Base protein language model of Bacformer Large, as the cards name it",
        ["The Bacformer README instead names the ESM++ reimplementation Synthyra/ESMplusplus_small for the same model."],
    )
    claim(
        "bacformer-large-base-plm-readme", large, "base_protein_language_model",
        "ESM-C through the ESM++ reimplementation Synthyra/ESMplusplus_small, which the README calls a faithful implementation of ESM-C",
        "Bacformer README 'Requirements': 'Bacformer Large (300M parameters) uses ESM-C (Synthyra/ESMplusplus_small)' and the note that follows it",
        [f"{P}source-bacformer-readme"],
        "The README names a different artifact for the same dependency than the model cards and the preprint do, and the two artifacts carry different licences.",
        readme_review, "Base protein language model of Bacformer Large, as the README names it",
        ["Conflicts with the model cards and preprint Table S9, which name EvolutionaryScale's own esmc_300m checkpoint."],
    )
    claim(
        "bacformer-licence-apache", bacformer, "licence",
        "Apache License 2.0 for the code and models in the Bacformer repository",
        "Preprint 'Code and data availability': 'publicly available at https://github.com/macwiatrak/Bacformer under a permissive Apache 2.0 license'; LICENSE file at the pinned commit; model card front matter 'license: apache-2.0'",
        [f"{P}source-preprint-v3", f"{P}source-bacformer-licence", CARD_SOURCE["bacformer-masked-MAG"]],
        "Three sources agree that Apache-2.0 covers the Bacformer code and the released checkpoints, which is narrower than the dependency models and the datasets.",
        preprint_review("Read from the availability statement and checked against the pinned LICENSE file and card metadata."),
        "Apache-2.0 covers the Bacformer code and checkpoints",
        ["Does not cover the base protein language models, the benchmarked comparator models, or the third-party measurements behind the datasets."],
    )
    claim(
        "dependency-licence-esmplusplus", bacformer, "dependency_licence",
        "The ESM++ implementation that the README names for Bacformer Large is governed by the EvolutionaryScale Cambrian Open License Agreement, not by Apache-2.0",
        "Bacformer README 'Requirements', note: 'ESM++ is a faithful implementation of ESM-C (license)' linking to evolutionaryscale.ai/policies/cambrian-open-license-agreement",
        [f"{P}source-bacformer-readme"],
        "Running Bacformer Large needs the ESM-C family, whose terms are set by EvolutionaryScale rather than by the Apache-2.0 licence of the Bacformer repository.",
        readme_review, "The base protein language model of Bacformer Large carries its own licence",
        ["The licence text itself was not retrieved in this batch, so only the README's statement about it is recorded."],
    )
    claim(
        "bacformer-large-bug-notice", large, "known_issue",
        "A bug in the Bacformer Large code on Hugging Face, announced on 2025-05-15, significantly degraded the output embeddings; the README says it is fixed and that anyone who downloaded or cached the model before that date must re-download the latest revision before running evaluations",
        "Bacformer README 'News', entry dated 2025-05-15",
        [f"{P}source-bacformer-readme"],
        "Any Bacformer Large number produced from a checkpoint cached before that date is not comparable with a number from the fixed code, and no source says which revision the preprint's runs used.",
        readme_review, "Bacformer Large embedding bug fixed on 2025-05-15",
        ["The preprint does not state the checkpoint revision used for its runs, so whether its Bacformer Large numbers predate the fix cannot be settled from these sources."],
    )
    for spec in UNAVAILABLE_CHECKPOINTS:
        claim(
            f"checkpoint-unavailable-{spec['slug'].replace('_', '-')}", P + spec["id"], "access",
            f"https://huggingface.co/macwiatrak/{spec['slug']} and the Hugging Face model API both returned HTTP 401 to an anonymous request on 2026-11-15",
            f"Bacformer README 'Pretrained model checkpoints' table, {spec['readme_row'][:60]}...; retrieval attempted 2026-11-15",
            [f"{P}source-bacformer-readme"],
            "The README lists this checkpoint among the released models, but it could not be retrieved, so nothing about its contents is recorded.",
            readme_review, f"Checkpoint {spec['slug']} was not retrievable",
            ["Checked once, anonymously, on 2026-11-15; HTTP 401 from Hugging Face does not distinguish a private repository from one that does not exist."],
        )
    claim(
        "ppi-checkpoint-no-card", f"{P}model-bacformer-for-ppi-prediction", "documentation",
        "The checkpoint resolves and serves weights, but its card is the auto-generated transformers template, with the model description, licence and training data all left as 'More Information Needed'",
        "Hugging Face model card for macwiatrak/bacformer-for-ppi-prediction, whole card",
        [CARD_SOURCE["bacformer-for-ppi-prediction"], f"{P}source-preprint-v3"],
        "The preprint offers this checkpoint as the released protein-protein interaction model, so the absence of any licence statement on it matters for reuse.",
        card_review("bacformer-for-ppi-prediction"), "The released PPI checkpoint has no model card content",
    )
    # BacBench claims.
    claim(
        "bacbench-licence-apache", f"{P}benchmark-bacbench", "licence",
        "Apache License 2.0, stated by the README licence badge and carried by the LICENSE file at the pinned commit",
        "BacBench README licence badge, line 3; LICENSE file at the pinned commit",
        [f"{P}source-bacbench-readme", f"{P}source-bacbench-licence"],
        "Apache-2.0 covers the BacBench code only; the datasets it points at carry their own terms and the measurements behind them are third-party.",
        bacbench_review, "Apache-2.0 covers the BacBench code",
        ["Says nothing about the Hugging Face datasets or the databases they are derived from."],
    )
    claim(
        "bacbench-active-tasks", f"{P}benchmark-bacbench", "tasks",
        "Five active tasks (essential gene prediction, operon identification from long-read RNA sequencing, protein-protein interaction, antibiotic resistance prediction and phenotypic trait prediction) and one deprecated task (strain clustering), which remains in the repository for reproducibility",
        "BacBench README opening paragraph and 'Task overview' table",
        [f"{P}source-bacbench-readme"],
        "The task list and the deprecation set what the benchmark currently covers, and the deprecated task is still reported in the preprint.",
        bacbench_review, "BacBench has five active tasks and one deprecated task",
    )
    claim(
        "bacbench-split-change", f"{P}benchmark-bacbench", "protocol_change",
        "On 13 May 2026 BacBench updated the essential gene and protein-protein interaction tasks to a phylogeny-aware split by genus, added BacLM as a benchmarked model and deprecated the strain clustering task",
        "BacBench README 'News', entry dated 13.05.2026",
        [f"{P}source-bacbench-readme"],
        "Results produced before that change are on a different split from results produced after it, so they are not the same protocol and must not be pooled.",
        bacbench_review, "BacBench changed the essential gene and PPI splits on 2026-05-13",
        ["The README does not publish a split manifest, so whether version 3 of the preprint used exactly the current split files cannot be checked from these sources; its Methods do describe genus-level 60/20/20 splits for both tasks."],
    )
    claim(
        "bacbench-no-printed-results", f"{P}benchmark-bacbench", "reported_results",
        "The repository prints no numeric results for any task; 'Create model leaderboard for each task' is an unchecked item on its to-do list",
        "BacBench README 'To-do-list'; the README has no results table",
        [f"{P}source-bacbench-readme"],
        "Every numeric result in this batch therefore comes from the Bacformer preprint, which is the authors' own report, and not from the benchmark repository.",
        bacbench_review, "BacBench publishes no numeric results",
    )
    claim(
        "bacbench-results-source", f"{P}benchmark-bacbench", "result_coverage",
        "All five active tasks have printed numeric results in the supplementary tables of version 3 of the Bacformer preprint: operon identification in Table S1, protein-protein interaction in Table S13, essential genes in Table S14, phenotypic traits in Table S16 and antibiotic resistance in Table S18; the deprecated strain clustering task is in Table S12 and a protein function prediction task that BacBench does not list is in Table S15",
        "Preprint Tables S1, S12, S13, S14, S15, S16 and S18",
        [f"{P}source-preprint-v3", f"{P}source-bacbench-readme"],
        "Records where the numbers for each task come from, and that the preprint also reports one task the benchmark does not list and one the benchmark has deprecated.",
        preprint_review("Table set read from the supplementary tables of the pinned PDF."),
        "Where each BacBench task's printed results are",
        ["Table S15, protein function prediction, is not among BacBench's listed tasks and was not extracted in this batch."],
    )
    claim(
        "operon-labels-long-read", f"{P}task-operon-identification", "label_provenance",
        "Operon annotations come from long-read RNA sequencing triplicates of five strains, mapped to annotated genes with minimap2 and SAMtools and merged across replicates; the preprint calls the sequencing proprietary while publishing the derived annotations on Hugging Face",
        "Preprint Methods 'Zero-shot operon prediction using long-read RNA sequencing' and 'Benchmarking'; 'Code and data availability'",
        [f"{P}source-preprint-v3"],
        "The operon labels are a measurement made by the authors rather than a public annotation set, so the task's labels and its benchmark protocol come from the same group.",
        preprint_review("Read from the Methods and the availability statement."),
        "Operon labels come from the authors' own long-read RNA sequencing",
        ["No sequencing read accession is given; only the derived annotations are published."],
    )
    claim(
        "phenotypic-seed-conflict", f"{P}protocol-phenotypic-traits-linear-probe-auroc", "aggregation_conflict",
        "Table S16 says its values are the mean and standard deviation across 5 seeds, while the Methods say the per-trait split was repeated across three independent runs with different data splits",
        "Preprint Table S16 caption against Methods 'Phenotypic traits prediction'",
        [f"{P}source-preprint-v3"],
        "The number of repeats behind the phenotypic trait spread is stated two ways in the same source, so the aggregation of those values is not settled.",
        preprint_review("Both statements read from the pinned text layer."),
        "The phenotypic trait table and Methods disagree on the number of repeats",
        ["Recorded as a note on the results rather than withheld; whether this warrants an evidence concern is a question for the reviewer."],
    )
    claim(
        "strain-clustering-selection", f"{P}protocol-strain-clustering-ari", "selection_bias",
        "The Leiden resolution and neighbour count were chosen as the combination that maximised the mean of the adjusted Rand index, normalised mutual information and average silhouette width at the species level, on the same genomes the table reports",
        "Preprint Methods 'Strain clustering': 'We then retained the combination of resolution and number of neighbours that maximised the mean of the three metrics described above (ARI, NMI and ASW) at the species level'",
        [f"{P}source-preprint-v3"],
        "The reported clustering values are the best of a hyperparameter grid scored on the same data, so they are not held-out measurements and overstate what a fresh dataset would give.",
        preprint_review("Quoted from the Methods."),
        "Clustering hyperparameters were selected on the reported metrics",
    )
    claim(
        "preprint-version-differences", f"{P}source-preprint-v3", "version_differences",
        "Version 3 (posted 17 August 2026) reports Bacformer Large and prints, for example, almost 95% balanced accuracy for the genus-level nearest-neighbour retrieval and 0.81 plus or minus 0.07 median AUROC for essentiality; version 2 (posted 13 August 2025) has no Bacformer Large and prints different values for the same analyses",
        "Version 3 Results sections against version 2 of the same preprint",
        [f"{P}source-preprint-v3", f"{P}source-preprint-v2"],
        "The two versions are different reports of the same study, so their numbers must not be pooled; every value in this batch comes from version 3.",
        preprint_review("Version 3 values read from its text layer; the version 2 figures were only compared qualitatively because its text layer mis-encodes digits."),
        "Preprint versions 2 and 3 print different values",
        ["Version 2 was retrieved and hashed but not parsed, so the comparison rests on prose read from a text layer whose digits are unreliable."],
    )
    claim(
        "benchmark-author-built", f"{P}benchmark-bacbench", "independence",
        "The same group built Bacformer, built BacBench, curated every task dataset and ran all twelve benchmarked models, including the comparators",
        "Preprint 'Author Contributions' and Methods 'Benchmarking'; BacBench README, which is in the same author's namespace",
        [f"{P}source-preprint-v3", f"{P}source-bacbench-readme"],
        "Every number in this batch is author-reported in the strict sense: the authors of the winning model also chose the tasks, the splits, the comparator checkpoints and their learning rates.",
        preprint_review("Read from the author contributions and the benchmarking section."),
        "Bacformer's authors also built and ran the benchmark",
    )


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else BATCH / "batch.jsonl"
    tables = json.loads((HERE / "tables.json").read_text())["tables"]
    sources()
    models()
    configurations()
    benchmark_and_tasks()
    protocols()
    evaluations_and_results(tables)
    claims()
    ids = [record["id"] for record in RECORDS]
    if len(ids) != len(set(ids)):
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        raise SystemExit(f"duplicate record ids: {duplicates}")
    records = sorted(RECORDS, key=lambda record: record["id"])
    with out.open("w") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    counts: dict[str, int] = {}
    for record in records:
        counts[record["kind"]] = counts.get(record["kind"], 0) + 1
    print(f"wrote {len(records)} records to {out}")
    for kind in sorted(counts):
        print(f"  {kind}: {counts[kind]}")


if __name__ == "__main__":
    main()
