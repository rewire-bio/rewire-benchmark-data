"""Build batch.jsonl for the TorchCraft extraction (issue #243).

Run from the repository root:  python3 data/omics/torchcraft-20261115/build.py

Every value comes from the pinned arXiv v1 PDF, its abstract page, the official project site,
or the TorchX repository at commit ebf9dc6676ecb1be505bc72f87de408995f0d8fd. Table S9 is
parsed from the PDF text layer by extract/parse_runtime_table.py; the script's output is read
here, so the runtime numbers in this file are not hand-typed.
"""

import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
PREFIX = "torchcraft-20261115-"
DATE = "2026-11-16"  # the extraction was finished and every value last checked just after 00:00Z
RETRIEVED = "2026-11-15T23:36:26Z"  # per-artifact times below; all within 23:36:17Z to 23:42:58Z
RETRIEVED_PDF = "2026-11-15T23:36:17Z"
RETRIEVED_ABS = "2026-11-15T23:36:25Z"
RETRIEVED_SITE = "2026-11-15T23:36:25Z"
RETRIEVED_HF = "2026-11-15T23:42:58Z"

PAPER_SHA = "f8145b5b95552dd30996eda2940507c0f32d09adfc60f44f28458e7872788f21"
ABS_SHA = "cac39821a99125fe2f245a30d72d8f1465a3a99b784298ada10f68748b2236a0"
SITE_SHA = "fa95060dad51bd3e04278b48c7e3bc62c66f8f909db3871e654f79d5a98dcd3c"
README_SHA = "88da821dfed6d76a6d1d2efd1e3e124a18f35c07d6fdf45a8e374fc2c35fccf0"
LICENCE_SHA = "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4"
DESIGN_SHA = "77a6b7b67f29a7931e58e5ee2bcbaa5efa08a5ff33debd6d658f85ae305ec313"
HF_SHA = "39268aab20e07bb615c1b96c8eb5684686dc953036a7d062dec7684581fbdfcf"
TEXT_LAYER_SHA = "90f1da5f8a936766087beba0ade3f038f5b69504b9f581b42f2391f5640c5e6b"
COMMIT = "ebf9dc6676ecb1be505bc72f87de408995f0d8fd"

S = {
    "paper": PREFIX + "source-arxiv-v1",
    "abs": PREFIX + "source-arxiv-abs",
    "site": PREFIX + "source-project-site",
    "readme": PREFIX + "source-torchx-readme",
    "licence": PREFIX + "source-torchx-licence",
    "design": PREFIX + "source-torchcraft-gpu-readme",
    "hf": PREFIX + "source-huggingface-torchfold",
}

# Existing store identities reused rather than duplicated.
AF3 = "discovery-model-alphafold-3"
PROTEINMPNN = "catalog-model-proteinmpnn"
LIGANDMPNN = "hyinv-20261106-model-ligandmpnn"
ESM2 = "catalog-model-esm-2"

EXTRACTOR = (
    "Claude (Opus 5) extraction agent; no human review claimed. Extraction only: a different "
    "agent reviews this batch, and nothing here is reproduced."
)
TRANSCRIPTION_NOTE = (
    "Hand transcription from the pdftotext -layout text layer of the pinned PDF (text layer "
    "sha256 " + TEXT_LAYER_SHA + ", regenerated with 'pdftotext -layout'). The text layer is not "
    "archived in this batch because the arXiv licence grants no redistribution right."
)
PARSE_NOTE = (
    "Table S9 parsed from the pdftotext -layout text layer of the pinned PDF by "
    "extract/parse_runtime_table.py, which asserts the four row labels, the five column headers "
    "and the cell count, and writes extract/runtime-table.tsv. The same 20 values are printed "
    "again on the official project site, which was checked against the parse."
)


def review(method, note, extra=None, locator_url="https://arxiv.org/pdf/2609.19770v1", sha=PAPER_SHA):
    out = {
        "method": method,
        "method_note": note,
        "reviewer": ["claude"],
        "reviewer_note": EXTRACTOR,
        "date": DATE,
        "artifact_sha256": sha,
        "retrieval_url": locator_url,
    }
    if extra:
        out["note"] = extra
    return out


PDF_REVIEW = ["transcription", "pdf-text-parse", "source-hash-verification"]
PARSE_REVIEW = ["deterministic-table-parse", "pdf-text-parse", "source-hash-verification"]
WEB_REVIEW = ["transcription", "automated-source-review", "source-hash-verification"]


def rec(rid, kind, name, description, attributes, *, status, sources, links=None, facets=None):
    return {
        "id": PREFIX + rid if not rid.startswith(PREFIX) else rid,
        "kind": kind,
        "name": name,
        "description": description,
        "status": status,
        "facets": facets if facets is not None else {"areas": ["protein-structure", "molecular-interactions"], "contexts": ["research"]},
        "source_ids": sources,
        "links": links or [],
        "attributes": attributes,
    }


records = []


def add(*args, **kwargs):
    records.append(rec(*args, **kwargs))


# --------------------------------------------------------------------------- sources
PAPER_LICENCE = (
    "arXiv.org perpetual, non-exclusive license 1.0 "
    "(http://arxiv.org/licenses/nonexclusive-distrib/1.0/), the only licence the abstract page "
    "links. No open reuse or redistribution licence is offered."
)

records.append({
    "id": S["paper"],
    "kind": "source",
    "name": "TorchCraft: Unified binder design by inverting an all-atom structure predictor (arXiv:2609.19770v1)",
    "description": "The TorchCraft preprint, which reports the design framework, the experimental minibinder and VHH campaigns, the computational benchmarks and the full methods.",
    "status": "source_checked",
    "facets": {"areas": ["protein-structure", "molecular-interactions"], "contexts": ["research"]},
    "source_ids": [],
    "links": [],
    "attributes": {
        "url": "https://arxiv.org/pdf/2609.19770v1",
        "artifact_url": "https://arxiv.org/pdf/2609.19770v1",
        "version": "arXiv:2609.19770v1, submitted 17 September 2026",
        "retrieved_at": RETRIEVED_PDF,
        "artifact_sha256": PAPER_SHA,
        "media_type": "application/pdf",
        "publication_status": "preprint",
        "licence": PAPER_LICENCE,
        "article_licence": PAPER_LICENCE,
        "extraction_method": "pdftotext -layout text layer; Table S9 by extract/parse_runtime_table.py, the other values by hand transcription",
        "hash_scope": (
            "SHA-256 of the PDF as downloaded. The pdftotext -layout text layer every value was read "
            "from hashes to " + TEXT_LAYER_SHA + "; it is regenerated from the PDF and is not archived here."
        ),
        "venue": "arXiv (cs.AI)",
        "year": 2026,
        "missing_metadata": {
            "doi": {"reason": "unavailable", "note": "The abstract page serves no citation_doi meta tag for this preprint."}
        },
        "limitations": [
            "Developer-reported: the authors designed, ran and measured everything reported here.",
            "No independent reproduction was attempted for this batch.",
        ],
        "review": review(
            ["source-hash-verification", "automated-source-review"],
            "Refetched on 2026-11-16T00:02Z with byte-identical content, so the hash is not a per-download stamp. The abstract page's citation_title and citation_date match the preprint.",
        ),
    },
})

records.append({
    "id": S["abs"],
    "kind": "source",
    "name": "arXiv abstract page for 2609.19770v1",
    "description": "The arXiv listing page for the TorchCraft preprint, which carries its title, submission date and licence.",
    "status": "source_checked",
    "facets": {"areas": ["protein-structure"], "contexts": ["research"]},
    "source_ids": [S["paper"]],
    "links": [{"relation": "companion_of", "target_id": S["paper"]}],
    "attributes": {
        "url": "https://arxiv.org/abs/2609.19770v1",
        "version": "Abstract page as served on 2026-11-15",
        "retrieved_at": RETRIEVED_ABS,
        "artifact_sha256": ABS_SHA,
        "media_type": "text/html",
        "publication_status": "preprint",
        "licence": PAPER_LICENCE,
        "source_locator": "citation_title, citation_date, submission history and the licence link",
        "limitations": [
            "Mutable page; the hash describes one retrieval on 2026-11-15.",
            "Used only for the title, the 17 September 2026 submission date and the licence.",
        ],
        "missing_metadata": {
            "doi": {"reason": "unavailable", "note": "No citation_doi meta tag is served."}
        },
        "review": review(
            ["source-hash-verification", "automated-source-review"],
            "citation_date is 2026/09/17 and the submission history reads 'Thu, 17 Sep 2026 06:37:20 UTC (18,007 KB)'. The only licence link is http://arxiv.org/licenses/nonexclusive-distrib/1.0/; no Creative Commons link is present. Refetched on 2026-11-16T00:02Z with byte-identical content.",
            locator_url="https://arxiv.org/abs/2609.19770v1",
            sha=ABS_SHA,
        ),
    },
})

records.append({
    "id": S["site"],
    "kind": "source",
    "name": "TorchX project site (torchx-cpl.github.io)",
    "description": "The official TorchX project page, which summarises TorchFold and TorchCraft, reprints the runtime table and states a licence for the implementations and weights.",
    "status": "source_checked",
    "facets": {"areas": ["protein-structure", "molecular-interactions"], "contexts": ["research"]},
    "source_ids": [S["paper"]],
    "links": [{"relation": "companion_of", "target_id": S["paper"]}],
    "attributes": {
        "url": "https://torchx-cpl.github.io/",
        "version": "Project site as served on 2026-11-15",
        "retrieved_at": RETRIEVED_SITE,
        "artifact_sha256": SITE_SHA,
        "media_type": "text/html",
        "publication_status": "official_project_source",
        "source_locator": "Sections '1. TorchFold', '2. TorchCraft', 'Runtime on GPU and Ascend NPU' and the closing licence line",
        "limitations": [
            "Mutable page; the hash describes one retrieval on 2026-11-15.",
            "Its TorchFold figures belong to a separate TorchFold report that could not be retrieved; none of them is used here.",
        ],
        "evidence_concerns": [
            {
                "source_id": S["site"],
                "message": (
                    "The site's closing line says the GPU and NPU implementations, the TorchFold training code and the "
                    "TorchFold-AbAg model weights are open under the MIT license. The repository's own LICENSE file and "
                    "README at commit " + COMMIT + " say Apache License 2.0, and the GitHub repository metadata reports "
                    "apache-2.0. The gated Hugging Face dataset is tagged mit but conditions access on no redistribution, "
                    "rehosting, selling or sharing without written permission. The MIT statement is therefore not relied on."
                ),
                "source_locator": "Project site, closing line below the citations block",
                "artifact_sha256": SITE_SHA,
                "review_date": DATE,
                "applies_to": [PREFIX + "claim-project-site-licence-statement"],
            }
        ],
        "review": review(
            WEB_REVIEW,
            "Refetched on 2026-11-16T00:02Z with byte-identical content. The Table S9 copy it prints was compared cell by cell with the parse of the PDF text layer by extract/check_transcriptions.py and agrees.",
            locator_url="https://torchx-cpl.github.io/",
            sha=SITE_SHA,
        ),
    },
})

records.append({
    "id": S["readme"],
    "kind": "source",
    "name": "TorchX repository README at commit ebf9dc6",
    "description": "The top-level README of the TorchX GPU tree, which names the four modules, the code licence, the two mutually exclusive weight sources and the gated checkpoint release.",
    "status": "source_checked",
    "facets": {"areas": ["protein-structure", "molecular-interactions"], "contexts": ["research"]},
    "source_ids": [S["paper"]],
    "links": [{"relation": "companion_of", "target_id": S["paper"]}],
    "attributes": {
        "url": "https://github.com/Mingchenchen/TorchX/blob/" + COMMIT + "/README.md",
        "artifact_url": "https://raw.githubusercontent.com/Mingchenchen/TorchX/" + COMMIT + "/README.md",
        "code_url": "https://github.com/Mingchenchen/TorchX",
        "version": "commit " + COMMIT + ", authored 2026-11-04T07:22:24Z",
        "immutable_source_version": COMMIT,
        "retrieved_at": RETRIEVED,
        "artifact_sha256": README_SHA,
        "media_type": "text/markdown",
        "publication_status": "official_project_source",
        "code_licence": "Apache-2.0, as stated in this README and in the repository LICENSE file at the same commit",
        "source_locator": "Sections 'TorchX', 'TorchFold overview', 'TorchFold Benchmark', 'TorchCraft overview', 'Repository layout', 'Checkpoints' and 'License'",
        "limitations": [
            "Documentation written after the preprint: the checkpoint options it offers are not all configurations the preprint evaluated.",
            "Its FoldBench-AB figure belongs to the separate TorchFold report, which could not be retrieved.",
        ],
        "review": review(
            WEB_REVIEW,
            "Retrieved at the pinned commit, whose existence and 2026-11-04T07:22:24Z author date were confirmed through the GitHub commits API. Refetched on 2026-11-16T00:02Z with byte-identical content.",
            locator_url="https://raw.githubusercontent.com/Mingchenchen/TorchX/" + COMMIT + "/README.md",
            sha=README_SHA,
        ),
    },
})

records.append({
    "id": S["licence"],
    "kind": "source",
    "name": "TorchX repository LICENSE file at commit ebf9dc6",
    "description": "The licence file of the TorchX repository, which is the Apache License 2.0 text.",
    "status": "source_checked",
    "facets": {"areas": ["protein-structure"], "contexts": ["research"]},
    "source_ids": [S["paper"]],
    "links": [{"relation": "companion_of", "target_id": S["paper"]}],
    "attributes": {
        "url": "https://github.com/Mingchenchen/TorchX/blob/" + COMMIT + "/LICENSE",
        "artifact_url": "https://raw.githubusercontent.com/Mingchenchen/TorchX/" + COMMIT + "/LICENSE",
        "version": "commit " + COMMIT,
        "immutable_source_version": COMMIT,
        "retrieved_at": RETRIEVED,
        "artifact_sha256": LICENCE_SHA,
        "media_type": "text/plain",
        "publication_status": "official_project_source",
        "code_licence": "Apache-2.0",
        "source_locator": "Whole file: 'Apache License, Version 2.0, January 2004'",
        "limitations": [
            "Covers the repository's code only. It does not cover the gated TorchFold checkpoint and training data, or the upstream AlphaFold 3 parameters.",
        ],
        "review": review(
            WEB_REVIEW,
            "The file is the unmodified Apache-2.0 text, refetched on 2026-11-16T00:02Z with byte-identical content. The GitHub repository API also reports spdx_id Apache-2.0 for this repository.",
            locator_url="https://raw.githubusercontent.com/Mingchenchen/TorchX/" + COMMIT + "/LICENSE",
            sha=LICENCE_SHA,
        ),
    },
})

records.append({
    "id": S["design"],
    "kind": "source",
    "name": "TorchX torchcraft_gpu/README.md at commit ebf9dc6",
    "description": "The TorchCraft design-module documentation, which gives the runtime prerequisites, the optional accelerated kernels and the two mutually exclusive weight settings for a design run.",
    "status": "source_checked",
    "facets": {"areas": ["protein-structure", "molecular-interactions"], "contexts": ["research"]},
    "source_ids": [S["paper"]],
    "links": [{"relation": "companion_of", "target_id": S["paper"]}],
    "attributes": {
        "url": "https://github.com/Mingchenchen/TorchX/blob/" + COMMIT + "/torchcraft_gpu/README.md",
        "artifact_url": "https://raw.githubusercontent.com/Mingchenchen/TorchX/" + COMMIT + "/torchcraft_gpu/README.md",
        "version": "commit " + COMMIT,
        "immutable_source_version": COMMIT,
        "retrieved_at": RETRIEVED,
        "artifact_sha256": DESIGN_SHA,
        "media_type": "text/markdown",
        "publication_status": "official_project_source",
        "source_locator": "Sections 'Prerequisite', 'Optional: cueq acceleration' and 'Design'",
        "limitations": [
            "Describes the released GPU tree, not the exact environment of the preprint's runs.",
        ],
        "review": review(
            WEB_REVIEW,
            "Retrieved at the pinned commit named in the discovery issue, and refetched on 2026-11-16T00:02Z with byte-identical content.",
            locator_url="https://raw.githubusercontent.com/Mingchenchen/TorchX/" + COMMIT + "/torchcraft_gpu/README.md",
            sha=DESIGN_SHA,
        ),
    },
})

records.append({
    "id": S["hf"],
    "kind": "source",
    "name": "Hugging Face dataset page TorchX-CPL/TorchFold",
    "description": "The gated Hugging Face dataset page for the TorchFold release, which states its access conditions and what the repository holds.",
    "status": "source_checked",
    "facets": {"areas": ["protein-structure"], "contexts": ["research"]},
    "source_ids": [S["paper"]],
    "links": [{"relation": "companion_of", "target_id": S["paper"]}],
    "attributes": {
        "url": "https://huggingface.co/datasets/TorchX-CPL/TorchFold",
        "version": "Dataset page as served on 2026-11-15, retrieved without signing in",
        "retrieved_at": RETRIEVED_HF,
        "artifact_sha256": HF_SHA,
        "media_type": "text/html",
        "publication_status": "official_project_source",
        "licence": "Page licence tag reads 'mit', while the gate text forbids redistribution, rehosting, selling or sharing without written permission from Changping Laboratory",
        "access_and_reuse": (
            "Gated with manual review. The gate reads: 'By requesting access, you agree to use the TorchFold-AbAg "
            "training data only for the purpose described below. Redistribution, rehosting, selling, or sharing these "
            "files without written permission from Changping Laboratory is not allowed.' Access was not requested."
        ),
        "source_locator": "Licence tag, gate text 'Request access to TorchFold-AbAg training data', and the dataset card",
        "limitations": [
            "Mutable page whose markup carries per-request class hashes, so the hash describes one retrieval; a refetch on 2026-11-16T00:02Z changed only those hashes.",
            "Retrieved without signing in, so the file list behind the gate was not seen.",
        ],
        "review": review(
            WEB_REVIEW,
            "The card describes TorchFold-AbAg training data (data.tar.gz of processed training examples, 1.13 GB total) and gated manual review; it does not itself list the trained weights the repository README says are released here. A refetch on 2026-11-16T00:02Z differed only in per-request CSS class hashes: the licence tag, the gate text and the card were identical, so the recorded hash is a per-retrieval stamp for this page.",
            locator_url="https://huggingface.co/datasets/TorchX-CPL/TorchFold",
            sha=HF_SHA,
        ),
    },
})

# --------------------------------------------------------------------------- the four entities
add(
    "method-torchx",
    "method",
    "TorchX",
    "TorchX is an all-atom biomolecular software stack whose modules predict, score, design and train on biomolecular structures.",
    {
        "entity_level": "suite",
        "version": "GPU tree at commit " + COMMIT,
        "reported_name": "TorchX",
        "access": "Public code at https://github.com/Mingchenchen/TorchX under Apache-2.0; model weights are obtained separately, either from the gated Hugging Face release or by applying to DeepMind for the AlphaFold 3 parameters.",
        "identity_scope": "The software suite only. Its modules, TorchFold, TorchScore, TorchCraft and TorchFold Train, are separate records.",
        "provenance_note": "Registered from the official repository README and LICENSE at commit " + COMMIT + " and the project site; no code was run.",
        "source_locator": "README sections 'TorchX', 'Repository layout' and 'License'",
        "review": review(WEB_REVIEW, "Read from the pinned README and LICENSE; the GPU and NPU branch split and the four modules were taken from the README's own tables.", locator_url="https://raw.githubusercontent.com/Mingchenchen/TorchX/" + COMMIT + "/README.md", sha=README_SHA),
    },
    status="source_checked",
    sources=[S["readme"], S["licence"], S["site"], S["paper"]],
    facets={"areas": ["protein-structure", "molecular-interactions"], "method_types": ["specialist"], "contexts": ["research"]},
)

add(
    "method-torchfold",
    "method",
    "TorchFold",
    "TorchFold predicts all-atom biomolecular complex structures, reimplementing the AlphaFold 3 architecture in PyTorch for GPU and Ascend NPU hardware.",
    {
        "entity_level": "method",
        "version": "GPU tree at commit " + COMMIT,
        "reported_name": "TorchFold",
        "access": "Public code under Apache-2.0. It runs either on the official AlphaFold 3 parameters, applied for from DeepMind, or on the gated TorchFold checkpoint released on Hugging Face.",
        "identity_scope": "The predictor implementation. It is not a new pretrained model: in this preprint it carries the released AlphaFold 3 weights. The separately released antibody-distilled checkpoint is recorded as a distinct configuration.",
        "provenance_note": "Cited in the preprint as reference 21, 'TorchFold: A PyTorch and NPU-compatible reimplementation of AlphaFold3' (2026). That report could not be retrieved: the reference carries no URL or DOI and the project site's TorchFold paper link points at the site itself.",
        "source_locator": "Preprint Section 1, Appendix A.1.1 and A.4.2; README section 'TorchFold overview'",
        "missing_metadata": {
            "parameters": {"reason": "unreported", "note": "Neither the preprint nor the README states a parameter count."},
            "checkpoint_revision": {"reason": "unavailable", "note": "The gated Hugging Face release was not accessed, so no checkpoint revision or hash was seen."},
        },
        "review": review(PDF_REVIEW, TRANSCRIPTION_NOTE, "The preprint describes TorchFold only as the implementation through which the frozen predictor is run; the architecture claim is from the README, which says TorchFold keeps the AlphaFold 3 architecture."),
    },
    status="source_checked",
    sources=[S["paper"], S["readme"], S["site"]],
    links=[{"relation": "uses_model", "target_id": AF3}],
    facets={"areas": ["protein-structure", "molecular-interactions"], "method_types": ["foundation_model"], "contexts": ["research"]},
)

add(
    "evaluator-torchscore",
    "evaluator",
    "TorchScore",
    "TorchScore scores supplied biomolecular coordinates through the confidence pathway of the TorchFold predictor, returning pLDDT, pTM and ipTM without generating a structure.",
    {
        "version": "As described in arXiv:2609.19770v1 Appendix A.4.2; GPU tree at commit " + COMMIT,
        "task": "Confidence scoring of a supplied protein or protein-ligand complex",
        "scope_note": (
            "A score-only loading of the TorchFold implementation: it bypasses the diffusion structure module and "
            "trains no separate scoring network. In this preprint it carries the same pretrained AlphaFold 3 weights "
            "used for design, so its scores are not an independent check of designs optimised against them. It does "
            "not refold a sequence: designs rebuilt with FlowPacker were scored from those coordinates."
        ),
    },
    status="source_checked",
    sources=[S["paper"], S["readme"]],
    facets={"areas": ["protein-structure", "molecular-interactions"], "contexts": ["research"]},
)

add(
    "pipeline-torchcraft",
    "pipeline",
    "TorchCraft",
    "TorchCraft designs binder sequences by optimising a trainable amino-acid logit matrix through a frozen all-atom structure predictor and then discretising it into a sequence with its predicted complex.",
    {
        "version": "As published in arXiv:2609.19770v1; GPU tree at commit " + COMMIT,
        "reported_name": "TorchCraft",
        "configuration_type": "pipeline",
        "access": "Public code in the TorchX repository under Apache-2.0; the weights it optimises through are obtained separately.",
        "parameters": "No trained parameters of its own: the predictor is frozen and only the editable sequence logits are updated.",
        "provenance_note": "Registered from the preprint and the pinned repository; no design run was executed for this batch.",
        "source_locator": "Abstract; Sections 2.1 and 2.2; Appendix A.1.1 to A.1.4",
        "review": review(PDF_REVIEW, TRANSCRIPTION_NOTE, "The four design tasks share one optimiser and differ in editable positions, losses, constraints and schedules (Section 2.1 and Supplementary Table S1)."),
    },
    status="source_checked",
    sources=[S["paper"], S["readme"], S["design"], S["site"]],
    links=[
        {"relation": "uses_model", "target_id": AF3},
        {"relation": "uses_model", "target_id": PREFIX + "method-torchfold"},
    ],
    facets={"areas": ["protein-structure", "molecular-interactions"], "method_types": ["specialist"], "contexts": ["research"]},
)

# --------------------------------------------------------------------------- new model identities
add(
    "model-iglm",
    "model",
    "IgLM",
    "IgLM is an antibody sequence language model that infills a masked segment of an antibody sequence conditioned on the surrounding sequence.",
    {
        "entity_level": "family",
        "reported_name": "IgLM",
        "provenance_note": "Cited by the preprint as reference 22, Shuai, Ruffolo and Gray, 'IgLM: Infilling language modeling for antibody sequence design', Cell Systems 14(11), 2023. Created here because the store held no record of it; only what this preprint and that title state is recorded.",
        "source_locator": "Section 2.3, Appendix A.1.4 and Algorithm 3; references list entry 22",
        "missing_metadata": {
            "version": {"reason": "unreported", "note": "The preprint names no version or checkpoint for IgLM."},
            "licence": {"reason": "unextracted", "note": "Not stated in the sources read for this batch."},
            "training_data": {"reason": "unreported", "note": "Not stated in this preprint."},
        },
        "review": review(PDF_REVIEW, TRANSCRIPTION_NOTE),
    },
    status="source_checked",
    sources=[S["paper"]],
    facets={"areas": ["proteins-complexes"], "method_types": ["foundation_model"], "contexts": ["research"]},
)

add(
    "model-abmpnn",
    "model",
    "AbMPNN",
    "AbMPNN designs antibody sequences for a supplied antibody structure.",
    {
        "entity_level": "family",
        "reported_name": "AbMPNN",
        "provenance_note": "Named in Appendix A.4.3.2 without a citation. Created here because the store held no record of it; only its use as the antibody sequence-redesign step is recorded.",
        "source_locator": "Appendix A.4.3.2",
        "missing_metadata": {
            "version": {"reason": "unreported", "note": "No version, checkpoint or citation is given."},
            "licence": {"reason": "unextracted", "note": "Not stated in the sources read for this batch."},
            "training_data": {"reason": "unreported", "note": "Not stated in this preprint."},
        },
        "review": review(PDF_REVIEW, TRANSCRIPTION_NOTE, "The preprint names AbMPNN only as the redesign step for antibody and VHH sequences; no citation is given for it."),
    },
    status="source_checked",
    sources=[S["paper"]],
    facets={"areas": ["proteins-complexes"], "method_types": ["specialist"], "contexts": ["research"]},
)

add(
    "model-flowpacker",
    "model",
    "FlowPacker",
    "FlowPacker builds all-atom side chains onto a protein backbone for a given sequence.",
    {
        "entity_level": "family",
        "reported_name": "FlowPacker",
        "provenance_note": "Named in Appendix A.4.2 and A.4.3 without a citation. Created here because the store held no record of it; only its use as the side-chain rebuilding step before scoring is recorded.",
        "source_locator": "Appendix A.4.2, A.4.3.1, A.4.3.2 and A.4.3.3",
        "missing_metadata": {
            "version": {"reason": "unreported", "note": "No version, checkpoint or citation is given."},
            "licence": {"reason": "unextracted", "note": "Not stated in the sources read for this batch."},
            "training_data": {"reason": "unreported", "note": "Not stated in this preprint."},
        },
        "review": review(PDF_REVIEW, TRANSCRIPTION_NOTE),
    },
    status="source_checked",
    sources=[S["paper"]],
    facets={"areas": ["protein-structure"], "method_types": ["specialist"], "contexts": ["research"]},
)

# --------------------------------------------------------------------------- predictor configurations
add(
    "config-torchfold-af3-parameters",
    "configuration",
    "TorchFold on pretrained AlphaFold 3 parameters",
    "A TorchFold setting that loads the official pretrained AlphaFold 3 parameters as the frozen predictor weights.",
    {
        "configuration_type": "reported_configuration",
        "version": "Pretrained AlphaFold 3 weights, through the TorchFold implementation; TorchX GPU tree at commit " + COMMIT,
        "checkpoint": "Official AlphaFold 3 parameters directory (model_dir in torchcraft_gpu/task/config/base.yaml, MODEL_DIR elsewhere)",
        "code_commit": COMMIT,
        "access_reuse": "The AlphaFold 3 parameters are applied for from DeepMind and are not distributed with the repository; the code around them is Apache-2.0.",
        "model_identity_note": "The weights are AlphaFold 3's released parameters, not a model trained for this work. Every design and every score reported in the preprint used this setting.",
        "provenance_note": "The configuration the preprint states for all of its experiments; recorded from the preprint and the pinned README, with no run.",
        "source_locator": "Abstract; Section 1 final paragraph; Appendix A.1.1 'All designs reported in this study used pretrained AF3 weights'; Appendix A.4.2; Figure 1 caption; README section 'Checkpoints'",
        "missing_metadata": {
            "weights_sha256": {"reason": "unreported", "note": "No hash or release version is given for the AlphaFold 3 parameters used."},
            "environment": {"reason": "unreported", "note": "The preprint does not state the software environment of its design runs; the pinned README's recommended runtime is Linux x86_64, Python 3.11 and PyTorch 2.8.0 with CUDA 12."},
        },
        "review": review(PDF_REVIEW, TRANSCRIPTION_NOTE, "Four independent places in the preprint state the AF3-weight setting: the abstract, the end of Section 1, Appendix A.1.1 and the Figure 1 caption, which adds that the experimental campaigns and the computational benchmarks used the same setting."),
    },
    status="source_checked",
    sources=[S["paper"], S["readme"], S["design"]],
    links=[
        {"relation": "configuration_of", "target_id": PREFIX + "method-torchfold"},
        {"relation": "uses_model", "target_id": AF3},
    ],
    facets={"areas": ["protein-structure", "molecular-interactions"], "method_types": ["foundation_model"], "contexts": ["research"]},
)

add(
    "config-torchfold-abag-checkpoint",
    "configuration",
    "TorchFold on the gated TorchFold antibody-distilled checkpoint",
    "A TorchFold setting that loads the separately released, access-gated TorchFold checkpoint instead of the AlphaFold 3 parameters.",
    {
        "configuration_type": "reported_configuration",
        "version": "TorchFold trained weights (.pt) from the gated Hugging Face release; TorchX GPU tree at commit " + COMMIT,
        "checkpoint": "TorchFold trained weights (.pt), set through checkpoint_path or CHECKPOINT_PATH; it takes priority if the AlphaFold 3 parameter directory is also set",
        "code_commit": COMMIT,
        "access_reuse": "Gated: the Hugging Face dataset page requires a manually reviewed access request and forbids redistribution, rehosting, selling or sharing the files without written permission from Changping Laboratory. Access was not requested for this batch.",
        "model_identity_note": "A distinct configuration from the AlphaFold 3 parameter setting. No experiment in the preprint used it, so it inherits none of the preprint's performance claims.",
        "provenance_note": "Offered by the repository README and the design-module README at commit " + COMMIT + ". It is not an option the preprint evaluated.",
        "source_locator": "README section 'Checkpoints'; torchcraft_gpu/README.md section 'Design'; preprint Discussion final paragraph",
        "limitations": [
            "Carries no result in this batch: the preprint reports no design or benchmark run with this checkpoint.",
            "The README's FoldBench-AB figure for TorchFold belongs to a separate report that could not be retrieved, so it is recorded as a developer-reported claim and not as a result.",
        ],
        "missing_metadata": {
            "weights_sha256": {"reason": "unavailable", "note": "The gated release was not accessed, so no file hash was seen."},
            "checkpoint_revision": {"reason": "unavailable", "note": "Not visible without approved access."},
        },
        "review": review(WEB_REVIEW, "Read from the pinned READMEs and the Hugging Face dataset page.", "The preprint's Discussion names using this checkpoint for CDR optimisation as future work, which confirms it was not used for the reported designs.", locator_url="https://raw.githubusercontent.com/Mingchenchen/TorchX/" + COMMIT + "/README.md", sha=README_SHA),
    },
    status="discovered",
    sources=[S["readme"], S["design"], S["hf"], S["paper"]],
    links=[{"relation": "configuration_of", "target_id": PREFIX + "method-torchfold"}],
    facets={"areas": ["protein-structure", "proteins-complexes"], "method_types": ["foundation_model"], "contexts": ["research"]},
)

# --------------------------------------------------------------------------- design configurations
SGD = "All design tasks were optimised with the same SGD optimiser (Supplementary Table S1 footnote)."
STAGES = "Stage lengths are iterations of the four-stage schedule: soft warm-up, logits-to-soft transition, temperature annealing and straight-through hard optimisation."


def design_config(rid, name, description, hyper, locator, *, status, extra_links=(), extra_attrs=None, limitations=(), sources=None):
    attrs = {
        "configuration_type": "reported_configuration",
        "version": "As published in arXiv:2609.19770v1, on pretrained AlphaFold 3 weights through TorchFold",
        "hyperparameters": hyper,
        "code_commit": COMMIT,
        "access_reuse": "Public code under Apache-2.0; the AlphaFold 3 parameters are applied for from DeepMind.",
        "provenance_note": "Settings taken from Supplementary Table S1 and the methods appendix of the preprint; no run was executed.",
        "source_locator": locator,
        "review": review(PDF_REVIEW, TRANSCRIPTION_NOTE),
    }
    if limitations:
        attrs["limitations"] = list(limitations)
    if extra_attrs:
        attrs.update(extra_attrs)
    add(
        rid,
        "configuration",
        name,
        description,
        attrs,
        status=status,
        sources=sources or [S["paper"]],
        links=[
            {"relation": "configuration_of", "target_id": PREFIX + "pipeline-torchcraft"},
            {"relation": "uses_model", "target_id": AF3},
            {"relation": "uses_model", "target_id": PREFIX + "config-torchfold-af3-parameters"},
        ] + list(extra_links),
        facets={"areas": ["protein-structure", "molecular-interactions"], "method_types": ["specialist"], "contexts": ["research"]},
    )


design_config(
    "config-minibinder-raw",
    "TorchCraft minibinder design, raw output",
    "A TorchCraft setting that optimises a complete minibinder sequence against a fixed protein target template and returns the sequence without any inverse-folding redesign.",
    "Loss weights: intra-chain binder contact 1, inter-chain target-binder contact 1, binder PAE 1, amino-acid composition 5. Stage iterations 0, 0, 80, 5. Learning rate 1. " + SGD + " " + STAGES,
    "Supplementary Table S1 row 'Minibinder'; Appendix A.1.3 and A.2.1; Section 2.2",
    status="source_checked",
    extra_attrs={
        "selection": "The whole binder sequence is editable; the target template is held fixed.",
        "representation": "Trainable logit matrix over the 20 standard amino acids, one row per editable position",
    },
    limitations=[
        "The amino-acid composition regulariser is part of this setting; the preprint also shows unregularised comparisons whose loss weights it does not print.",
    ],
)

design_config(
    "config-minibinder-mpnn-polished",
    "TorchCraft minibinder design with ProteinMPNN polishing",
    "A TorchCraft minibinder setting that fixes the designed interface residues and resamples every other position eight times with ProteinMPNN, rebuilds side chains and keeps the highest-scoring redesign.",
    "Design as in the raw minibinder setting, then eight ProteinMPNN redesigns of all non-interface positions, FlowPacker side-chain rebuilding and selection of the redesign with the highest TorchScore pTM plus ipTM.",
    "Appendix A.4.3.1; Section 2.2",
    status="discovered",
    extra_links=[
        {"relation": "uses_model", "target_id": PROTEINMPNN},
        {"relation": "uses_model", "target_id": PREFIX + "model-flowpacker"},
    ],
    extra_attrs={"selection": "BindCraft-style polishing: interface residues fixed, all other positions redesigned eight times."},
    limitations=[
        "Carries no result in this batch: Figure 2f prints no numbers.",
        "A separate configuration from the raw setting; the experimentally tested sequences were not polished.",
    ],
)

design_config(
    "config-vhh-raw",
    "TorchCraft framework-conditioned VHH design, raw output",
    "A TorchCraft setting that holds a VHH framework sequence fixed, optimises the three CDR loops under a CDR-restricted antibody language-model prior, and returns the sequence without inverse-folding redesign.",
    "Loss weights: paratope 1, ipTM 10, binder-target interface PAE 1, CDR1-restricted IgLM 1.5, CDR2-restricted IgLM 3.5, CDR3-restricted IgLM 5. Stage iterations 0, 0, 80, 5. Learning rate 0.1. " + SGD + " " + STAGES,
    "Supplementary Table S1 row 'VHH'; Appendix A.1.3, A.1.4 and A.2.1; Section 2.3",
    status="source_checked",
    extra_links=[{"relation": "uses_model", "target_id": PREFIX + "model-iglm"}],
    extra_attrs={
        "selection": "Only the three CDRs are editable; the framework is fixed and the interface objective is restricted to CDR-driven recognition.",
        "representation": "Trainable logit matrix over the editable CDR positions, with the framework and the other CDRs supplying infilling context for the IgLM objective",
    },
)

design_config(
    "config-vhh-abmpnn-polished",
    "TorchCraft VHH design with AbMPNN polishing",
    "A TorchCraft VHH setting that fixes the designed interface CDR residues and resamples every other position eight times with AbMPNN, rebuilds side chains and keeps the highest-scoring redesign.",
    "Design as in the raw VHH setting, then eight AbMPNN redesigns of all positions outside the interface CDR residues, FlowPacker side-chain rebuilding and selection of the redesign with the highest TorchScore ipTM.",
    "Appendix A.4.3.2; Section 2.3",
    status="discovered",
    extra_links=[
        {"relation": "uses_model", "target_id": PREFIX + "model-abmpnn"},
        {"relation": "uses_model", "target_id": PREFIX + "model-flowpacker"},
    ],
    limitations=[
        "Carries no result in this batch: Figure 3i prints no numbers.",
        "A separate configuration from the raw setting; the experimentally tested VHHs were not polished.",
    ],
)

design_config(
    "config-cyclic-head-to-tail-raw",
    "TorchCraft head-to-tail cyclic-peptide design, raw output",
    "A TorchCraft setting that designs a head-to-tail cyclic peptide against a target using cyclic relative positional encoding to represent sequence adjacency across the termini.",
    "Loss weights: intra-chain binder contact 1, inter-chain target-binder contact 1, binder PAE 1, amino-acid composition 5. Stage iterations 30, 60, 45, 5. Learning rate 0.1. " + SGD + " " + STAGES,
    "Supplementary Table S1 row 'Cyclic peptide'; Section 2.4; Appendix A.4.3.3",
    status="discovered",
    extra_attrs={"selection": "All peptide positions editable; cyclic relative positional encoding represents adjacency across the termini."},
    limitations=["Carries no result in this batch: Figure 4c prints no numbers.", "Computational only: no cyclic peptide was measured experimentally."],
)

design_config(
    "config-cyclic-head-to-tail-mpnn",
    "TorchCraft head-to-tail cyclic-peptide design with ProteinMPNN polishing",
    "A head-to-tail cyclic-peptide setting that resamples every peptide position eight times with ProteinMPNN, rebuilds side chains and keeps the highest-scoring redesign.",
    "Design as in the raw head-to-tail setting, then eight ProteinMPNN redesigns of all peptide positions, FlowPacker rebuilding and selection of the redesign with the highest TorchScore pLDDT plus 100 times ipTM.",
    "Appendix A.4.3.3",
    status="discovered",
    extra_links=[
        {"relation": "uses_model", "target_id": PROTEINMPNN},
        {"relation": "uses_model", "target_id": PREFIX + "model-flowpacker"},
    ],
    limitations=["Carries no result in this batch: Figure 4c prints no numbers.", "Computational only."],
)

design_config(
    "config-cyclic-disulfide-raw",
    "TorchCraft disulfide-linked cyclic-peptide design, raw output",
    "A TorchCraft setting that designs a disulfide-linked cyclic peptide against a target, keeping linear positional encoding and fixing the cysteine positions that define the linkage.",
    "Loss weights and stage iterations as for the cyclic-peptide task in Supplementary Table S1: intra-chain binder contact 1, inter-chain target-binder contact 1, binder PAE 1, amino-acid composition 5; stages 30, 60, 45, 5; learning rate 0.1. " + SGD,
    "Section 2.4; Supplementary Table S1 row 'Cyclic peptide'; Appendix A.4.3.3",
    status="discovered",
    extra_attrs={"selection": "All positions except the two cysteines are editable; the cysteines defining the linkage are fixed."},
    limitations=["Carries no result in this batch: Figure 4c prints no numbers.", "Computational only.", "Supplementary Table S1 prints one cyclic-peptide row; it does not separate head-to-tail from disulfide-linked hyperparameters."],
)

design_config(
    "config-cyclic-disulfide-mpnn",
    "TorchCraft disulfide-linked cyclic-peptide design with ProteinMPNN polishing",
    "A disulfide-linked cyclic-peptide setting that resamples every position except the two cysteines eight times with ProteinMPNN, rebuilds side chains and keeps the highest-scoring redesign.",
    "Design as in the raw disulfide-linked setting, then eight ProteinMPNN redesigns of all positions except the two cysteines, FlowPacker rebuilding and the same TorchScore selection as the head-to-tail setting.",
    "Appendix A.4.3.3",
    status="discovered",
    extra_links=[
        {"relation": "uses_model", "target_id": PROTEINMPNN},
        {"relation": "uses_model", "target_id": PREFIX + "model-flowpacker"},
    ],
    limitations=["Carries no result in this batch: Figure 4c prints no numbers.", "Computational only."],
)

design_config(
    "config-ligand-pocket-raw",
    "TorchCraft ligand-conditioned pocket design, raw output",
    "A TorchCraft setting that designs a 160-residue protein around a small-molecule ligand with no supplied scaffold, starting from a ligand-free warm-up and then raising the weight of the interface objective.",
    "Loss weights: intra-chain binder contact 1, inter-chain target-binder contact 1, alpha-helix 0.01, beta 0.15, isotropy 0.3, amino-acid composition 5. Stage iterations 30, 75, 80, 5. Learning rate 0.1. The interface weight rises from zero to its final value during the stated transition stage and is then held fixed. " + SGD,
    "Supplementary Table S1 row 'Small-molecule binder'; Appendix A.1.3; Section 2.5",
    status="discovered",
    extra_attrs={"selection": "All 160 positions editable; no native scaffold is supplied; raw outputs are evaluated without redesign or score-based preselection."},
    limitations=["Carries no result in this batch: Figures 5c, 5d and S9 print no numbers.", "Computational only: no designed pocket was measured experimentally."],
)

design_config(
    "config-ligand-pocket-ligandmpnn",
    "TorchCraft ligand-conditioned pocket design with LigandMPNN redesign",
    "A ligand-pocket setting that fixes the ligand-interface residues, resamples the other positions eight times with LigandMPNN, refolds the redesigned sequences and keeps the highest-confidence structure.",
    "Design as in the raw pocket setting, then eight LigandMPNN redesigns of all positions outside the ligand interface, refolding of the redesigned sequences with TorchFold and selection of the refolded structure with the highest pTM.",
    "Appendix A.4.3.4; Section 2.5",
    status="discovered",
    extra_links=[{"relation": "uses_model", "target_id": LIGANDMPNN}],
    limitations=[
        "Carries no result in this batch: Figures 5c and 5d print no numbers.",
        "Unlike the other polished settings, this one refolds the redesigned sequence with TorchFold rather than rebuilding side chains only.",
    ],
)

# --------------------------------------------------------------------------- runtime configurations
RUNTIME_ROWS = [
    ("npu-fused-attention", "TorchCraft on Ascend 910B with fused attention", "NPU", "w/ FA", "910B (64G)",
     "Ascend 910B NPU with 64 GB memory, using the modified NPU fusion-attention operator"),
    ("npu-no-fused-attention", "TorchCraft on Ascend 910B without fused attention", "NPU", "w/o FA", "910B (64G)",
     "Ascend 910B NPU with 64 GB memory, without the fused-attention operator"),
    ("gpu-cuequivariance", "TorchCraft on A100 with cuequivariance kernels", "GPU", "w/ cuequivariance", "A100 (80G)",
     "NVIDIA A100 GPU with 80 GB memory, using the optional cuequivariance triangle kernels"),
    ("gpu-no-cuequivariance", "TorchCraft on A100 without cuequivariance kernels", "GPU", "w/o cuequivariance", "A100 (80G)",
     "NVIDIA A100 GPU with 80 GB memory, with the default torch kernels"),
]

for rid, name, code, operator, machine, hardware in RUNTIME_ROWS:
    add(
        "config-runtime-" + rid,
        "configuration",
        name,
        "A TorchCraft design run on " + hardware + ", timed per design.",
        {
            "configuration_type": "reported_configuration",
            "version": "As published in arXiv:2609.19770v1 Supplementary Table S9",
            "hardware": {"code": code, "operator": operator, "machine": machine, "description": hardware},
            "accelerator_details": machine,
            "access_reuse": "Public code under Apache-2.0; the hardware is the authors' own. The optional cuequivariance kernels are pinned CUDA 12 packages installed from torchcraft_gpu/requirements-cueq.txt.",
            "runtime": "Minutes per design: the wall-clock time of a batch-size-2 run divided by 2. GPU timings are the mean of three independent runs.",
            "provenance_note": "The hardware and operator settings printed in Supplementary Table S9; no timing was reproduced.",
            "source_locator": "Supplementary Table S9, row '" + code + " " + operator + "'",
            "missing_metadata": {
                "environment": {"reason": "unreported", "note": "Supplementary Table S9 names the machine and the operator setting but no software versions; the pinned design README recommends Python 3.11 and PyTorch 2.8.0 with CUDA 12."},
            },
            "review": review(PARSE_REVIEW, PARSE_NOTE),
        },
        status="source_checked",
        sources=[S["paper"], S["site"], S["design"]],
        links=[
            {"relation": "configuration_of", "target_id": PREFIX + "pipeline-torchcraft"},
            {"relation": "uses_model", "target_id": PREFIX + "config-torchfold-af3-parameters"},
        ],
        facets={"areas": ["protein-structure"], "method_types": ["specialist"], "contexts": ["research"]},
    )

add(
    "config-esm2-150m-expression-classifier",
    "configuration",
    "ESM2-150M perplexity as a VHH expression classifier",
    "A setting that uses ESM2-150M sequence perplexity as a one-dimensional classifier of whether a VHH design expresses above a stated yield, with the threshold chosen to maximise the Matthews correlation coefficient.",
    {
        "configuration_type": "reported_configuration",
        "version": "ESM2-150M as named in arXiv:2609.19770v1 Appendix A.4.3.2",
        "hyperparameters": "Perplexity threshold swept as a one-dimensional classifier; operating threshold chosen by maximising the Matthews correlation coefficient. The threshold is printed as 6.309 in Figure S4b and as 6.31 in Appendix A.4.3.2. Designs with total expression of at least 0.08 mg were labelled high-expression.",
        "access_reuse": "Public ESM-2 checkpoint; the retrospective expression measurements behind the threshold are not released.",
        "provenance_note": "Recorded from the preprint's retrospective analysis; the threshold was not recomputed.",
        "source_locator": "Appendix A.4.3.2; Supplementary Figure S4 caption",
        "missing_metadata": {
            "checkpoint_revision": {"reason": "unreported", "note": "The preprint names ESM2-150M without a checkpoint revision or citation."},
        },
        "review": review(PDF_REVIEW, TRANSCRIPTION_NOTE, "Appendix A.4.3.2 prints the threshold as 6.31 and Figure S4b as 6.309; both are recorded and neither was changed."),
    },
    status="source_checked",
    sources=[S["paper"]],
    links=[{"relation": "uses_model", "target_id": ESM2}],
    facets={"areas": ["proteins-complexes"], "method_types": ["foundation_model"], "contexts": ["research"]},
)

# --------------------------------------------------------------------------- tasks
TASKS = [
    ("task-minibinder-design", "De novo minibinder design against a protein target",
     "Design a protein minibinder sequence that binds a specified protein target at specified hotspot residues.",
     "Inputs are a target structure with a crop and hotspot residues and a binder-length range; the output is a binder sequence with its predicted complex.",
     "Section 2.2; Appendix A.2.1 and A.4.3.1"),
    ("task-vhh-design", "Framework-conditioned VHH design against a protein target",
     "Design the three CDR loops of a VHH on a fixed framework so that the VHH binds a specified protein target.",
     "Inputs are a target structure with a crop and hotspot residues, a framework sequence and CDR length ranges; the output is a VHH sequence with its predicted complex.",
     "Section 2.3; Appendix A.2.1 and A.4.3.2"),
    ("task-cyclic-peptide-design", "Cyclic peptide design against a protein target",
     "Design a cyclic peptide that binds a specified target, cyclised either head to tail or through a disulfide bond.",
     "Inputs are a target structure with hotspot residues and a peptide-length range; the output is a peptide sequence with its predicted complex, classified by whether it satisfies the intended cyclisation.",
     "Section 2.4; Appendix A.4.3.3"),
    ("task-ligand-pocket-design", "Ligand-conditioned protein pocket design",
     "Design a protein that forms a binding pocket around a specified small-molecule ligand without a supplied scaffold.",
     "The input is a small-molecule ligand; the output is a protein sequence with its predicted ligand complex.",
     "Section 2.5; Appendix A.4.3.4"),
    ("task-vhh-expression-prediction", "Prediction of VHH expression from sequence",
     "Predict from its sequence whether a VHH design will express above a stated yield.",
     "The input is a VHH sequence; the output is a score that separates designs expressing at least 0.08 mg in total from the rest.",
     "Appendix A.4.3.2; Supplementary Figure S4"),
    ("task-design-runtime", "Runtime of a binder design run",
     "Measure the wall-clock time a design run takes per design at a stated binder sequence length and hardware setting.",
     "Inputs are a sequence length and a hardware and operator setting; the output is minutes per design.",
     "Supplementary Table S9; Appendix A.3"),
]
for rid, name, description, scope, locator in TASKS:
    add(
        rid,
        "task",
        name,
        description,
        {
            "task": description,
            "scope_note": scope,
            "version": "As published in arXiv:2609.19770v1",
            "source_locator": locator,
        },
        status="source_checked",
        sources=[S["paper"]],
    )

# --------------------------------------------------------------------------- benchmarks
BENCHMARKS = [
    ("benchmark-minibinder-12-target", "TorchCraft 12-target minibinder design benchmark",
     "A computational comparison of minibinder design methods over 12 protein targets at four binder lengths, scored by TorchScore confidence.",
     "12 protein targets (IL-7Ra, InsulinR, PD-L1, TrkA, CD3D, EGFRc, EGFRn, FGFR2, IGF1R, PDGFRb, Tie2, VirB8) at binder lengths of 75, 120, 160 and 200 residues, with hotspots listed separately for each length. 100 designs per method, per length, per target. TorchCraft, BoltzGen and RFdiffusion are compared; results are printed only as the bar chart of Figure 2f.",
     "Figure 2f; Appendix A.4.3.1; Supplementary Table S4"),
    ("benchmark-vhh-15-target", "TorchCraft 15-target VHH design benchmark",
     "A computational comparison of VHH design methods over 15 protein targets and five nanobody frameworks, scored by TorchScore confidence and a sequence-perplexity expression proxy.",
     "15 protein targets (IL13, HNMT, 1433E, BHRF1, EFNA1, CCL2, IL20, CSF1, MZB1, LIF, XIAP, RSPO1, FCGR3B, UNG, DAF) with HCDR1 and HCDR2 of 8 residues and HCDR3 of 9 to 21 residues, over the five frameworks 5JDS, 7EOW, 7XL0, 8COH and 8Z8V. 100 designs per method, per framework, per target. TorchCraft, RFantibody, BoltzGen and Germinal are compared; results are printed only as the charts of Figure 3i and Supplementary Figure S5.",
     "Figure 3i; Supplementary Figure S5; Appendix A.4.3.2; Supplementary Table S5"),
    ("benchmark-cyclic-peptide-8-target", "TorchCraft 8-target cyclic peptide design benchmark",
     "A computational comparison of cyclic peptide design methods over eight target systems in two cyclisation modes, scored by cyclisation integrity and TorchScore confidence.",
     "Eight target systems (MCL-1, MDM2, PD-L1, IL-23R, albumin, KEAP1, GABARAP and RagA:RagC) with peptide lengths of 12 to 18 residues. 100 designs per method per target in the head-to-tail setting. BoltzGen, RFpeptides and TorchCraft are compared, with TorchCraft also run in a disulfide-linked setting; results are printed only as the chart of Figure 4c.",
     "Figure 4c; Appendix A.4.3.3; Supplementary Table S6"),
    ("benchmark-ligand-pocket-10-ligand", "TorchCraft 10-ligand pocket design benchmark",
     "A computational comparison of ligand-conditioned pocket design over ten small-molecule ligands, assessed by docking score, predicted affinity and TorchScore confidence.",
     "Ten chemically diverse ligands (ALE, ATP, CHD, CMP, DLU, FAD, IAI, OQO, SAM and TRP). 500 designs of 160 residues per method per ligand, generated without a supplied native scaffold. BoltzDesign and TorchCraft are compared; results are printed only as the distributions of Figures 5c and 5d and the pass rates of Supplementary Figure S9.",
     "Figures 5c and 5d; Supplementary Figures S8 and S9; Appendix A.4.3.4"),
    ("benchmark-runtime", "TorchCraft runtime benchmark across sequence lengths",
     "A measurement of TorchCraft design runtime at five sequence lengths on two hardware platforms, each with and without an optional accelerated attention path.",
     "Minutes per design at 100, 200, 300, 400 and 500 residues, on an Ascend 910B (64 GB) NPU with and without fused attention and on an A100 (80 GB) GPU with and without cuequivariance kernels. Batch size 2 is the recommended setting; runtime is the wall-clock time of a batch-size-2 run divided by 2, and GPU timings are the mean of three independent runs. All 20 cells are printed in Supplementary Table S9.",
     "Supplementary Table S9; Appendix A.3"),
]
for rid, name, description, scope, locator in BENCHMARKS:
    runtime = rid.endswith("runtime")
    attrs = {
        "entity_level": "suite",
        "version": "As published in arXiv:2609.19770v1",
        "task": "Binder design" if not runtime else "Design runtime measurement",
        "scope_note": scope,
        "source_locator": locator,
        "executable_suite": False,
        "review": review(PARSE_REVIEW if runtime else PDF_REVIEW, PARSE_NOTE if runtime else TRANSCRIPTION_NOTE),
    }
    limitations = [
        "Author-built and author-run: the method's developers defined the panel, the criterion and the comparators.",
    ]
    if not runtime:
        limitations += [
            "Scored by TorchScore, which uses the same pretrained AlphaFold 3 weights the TorchCraft designs were optimised against.",
            "Printed only as a figure; no per-target or aggregate number is printed, so this batch records no result for it.",
            "Pass rates are predictor-derived and are not experimental success rates.",
        ]
    else:
        limitations += [
            "The design task behind the timings is not stated: Supplementary Table S9 gives sequence lengths only.",
        ]
    attrs["limitations"] = limitations
    attrs["missing_metadata"] = {
        "split": {"reason": "inapplicable", "note": "A design panel, not a train and test split."},
    }
    add(rid, "benchmark", name, description, attrs, status="source_checked" if runtime else "discovered", sources=[S["paper"]] + ([S["site"]] if runtime else []))

# --------------------------------------------------------------------------- datasets
def dataset(rid, name, description, attrs, *, status, sources=None, links=None, facets=None):
    base = {
        "version": "As published in arXiv:2609.19770v1",
        "review": review(PDF_REVIEW, TRANSCRIPTION_NOTE),
    }
    base.update(attrs)
    add(rid, "dataset", name, description, base, status=status, sources=sources or [S["paper"]], links=links, facets=facets)


dataset(
    "dataset-minibinder-campaign-targets",
    "Four protein targets of the minibinder validation campaigns",
    "The four protein targets, template structures, crops, hotspots and binder-length ranges used for the experimentally validated minibinder campaigns, with the commercial Fc-fusion proteins used in the assays.",
    {
        "total_targets": 4,
        "assay": "Biolayer interferometry (Gator Bio) on His-tagged binders expressed in a cell-free system",
        "species": "Human",
        "scope_note": (
            "IFNAR2 (PDB 3se4, chain C34-232, 11 hotspots, binder length 90-150), IL-7Ra (7opb, B36-231, 12 hotspots, "
            "90-150), PDGFRb (3mjg, X124-312, 6 hotspots, 90-150) and PD-L1 (8znl, B20-133, 4 hotspots, 60-130). For "
            "IFNAR2 the missing interface residues were repaired by homology modelling with SWISS-MODEL. The assay "
            "proteins are the Fc-fusion constructs of Supplementary Table S7."
        ),
        "access": "Target structures are public PDB entries; the designed sequences are not released in the preprint.",
        "source_locator": "Supplementary Tables S2 and S7; Appendix A.5.1.4",
        "missing_metadata": {
            "manifest": {"reason": "unreported", "note": "No designed or tested sequence is printed or deposited."},
        },
    },
    status="source_checked",
)

dataset(
    "dataset-vhh-campaign-targets",
    "Four protein targets of the VHH validation campaigns",
    "The four protein targets, template structures, crops, hotspots and CDR length ranges used for the experimentally validated VHH campaigns, with the proteins used in the assays.",
    {
        "total_targets": 4,
        "assay": "Biolayer interferometry (Gator Bio) on His-tagged VHHs expressed in CHO cells",
        "species": "Human, except BHRF1, which is an Epstein-Barr virus protein",
        "scope_note": (
            "BHRF1 (PDB 2wh6, chain A2-158, 5 hotspots), EFNA5 (2x11, B32-171, 3 hotspots), PDGFRb (3mjg, X124-312, "
            "3 hotspots) and S100A4 (5lpu, C2-90, 3 hotspots), all with HCDR1 and HCDR2 of 8 residues and HCDR3 of 9 to "
            "21 residues. Frameworks were selected at random from 7EOW (caplacizumab), 8Z8V (ozoralizumab), 5JDS "
            "(envafolimab), 7XL0 (vobarilizumab) and 8COH (gefurulimab). The assay proteins are the Fc-fusion "
            "constructs of Supplementary Table S8, except BHRF1, which was expressed with a cleaved His-SUMO tag in "
            "HEK293 cells because no suitably tagged commercial protein was available."
        ),
        "access": "Target structures are public PDB entries; the designed sequences are not released in the preprint.",
        "source_locator": "Supplementary Tables S3 and S8; Appendix A.5.2.1 and A.5.2.5",
        "missing_metadata": {
            "manifest": {"reason": "unreported", "note": "No designed or tested sequence is printed or deposited."},
        },
    },
    status="source_checked",
)

dataset(
    "dataset-minibinder-benchmark-targets",
    "Twelve protein targets of the minibinder design benchmark",
    "The twelve protein targets, template structures, crops and per-length hotspot sets used for the computational minibinder benchmark.",
    {
        "total_targets": 12,
        "species": "Human, except VirB8, which is a bacterial protein",
        "scope_note": (
            "IL-7Ra (7opb), InsulinR (4zxb), PD-L1 (8znl), TrkA (1www), CD3D (1xiw), EGFRc (1mox), EGFRn (1mox), FGFR2 "
            "(1djs), IGF1R (5u8r), PDGFRb (3mjg), Tie2 (2gy7) and VirB8 (4o3v). Hotspots are listed separately for the "
            "75-residue, 120-residue and 160 or 200-residue settings."
        ),
        "access": "Public PDB entries; no design or score file is released.",
        "source_locator": "Supplementary Table S4; Appendix A.4.1",
    },
    status="discovered",
)

dataset(
    "dataset-vhh-benchmark-targets",
    "Fifteen protein targets of the VHH design benchmark",
    "The fifteen protein targets, template structures, crops and hotspots used for the computational VHH benchmark.",
    {
        "total_targets": 15,
        "species": "Human, except BHRF1, an Epstein-Barr virus protein",
        "scope_note": (
            "IL13 (1ijz), HNMT (1jqd), 1433E (2br9), BHRF1 (2wh6), EFNA1 (3hei), CCL2 (4dn4), IL20 (4doh), CSF1 (4wrm), "
            "MZB1 (7aah), LIF (7n0a), XIAP (1g3f), RSPO1 (4bsp), FCGR3B (1fnl), UNG (2hxm) and DAF (1h03). All designs "
            "used HCDR1 and HCDR2 of 8 residues and HCDR3 of 9 to 21 residues."
        ),
        "access": "Public PDB entries; no design or score file is released.",
        "source_locator": "Supplementary Table S5; Appendix A.4.1",
    },
    status="discovered",
)

dataset(
    "dataset-cyclic-peptide-benchmark-targets",
    "Eight target systems of the cyclic peptide design benchmark",
    "The eight target systems, template structures, crops, hotspots and peptide-length range used for the computational cyclic peptide benchmark.",
    {
        "total_targets": 8,
        "scope_note": (
            "MDM2 (4hfz), MCL-1 (2pqk), GABARAP (7zkr), PD-L1 (5o45), KEAP1 (2flu), RagA:RagC (6s6d), IL-23R (5mzv) "
            "and albumin (1bj5), each with a peptide length range of 12 to 18 residues."
        ),
        "access": "Public PDB entries; no design or score file is released.",
        "source_locator": "Supplementary Table S6; Appendix A.4.1",
    },
    status="discovered",
)

dataset(
    "dataset-ligand-panel-10",
    "Ten small-molecule ligands of the pocket design benchmark",
    "The ten chemically diverse small-molecule ligands used as design targets for the computational pocket benchmark.",
    {
        "total_targets": 10,
        "scope_note": "ALE, ATP, CHD, CMP, DLU, FAD, IAI, OQO, SAM and TRP, described as nucleotides, cofactors, metabolites and drug-like compounds.",
        "access": "Ligand codes only; no structure or design file is released.",
        "source_locator": "Supplementary Figure S8 caption; Section 2.5",
        "missing_metadata": {
            "accession": {"reason": "unreported", "note": "The ligands are named by three-letter code without a database version."},
        },
    },
    status="discovered",
    facets={"areas": ["molecular-interactions"], "contexts": ["research"]},
)

dataset(
    "dataset-runtime-design-runs",
    "TorchCraft runtime benchmark design runs",
    "The design runs timed for the runtime benchmark, at binder sequence lengths of 100, 200, 300, 400 and 500 residues.",
    {
        "scope_note": "Five sequence lengths timed on two hardware platforms. Batch size 2 is the recommended setting; the 500-residue NPU run without fused attention was timed at batch size 1 because batch size 2 exceeded memory.",
        "access": "No run log or design file is released.",
        "source_locator": "Supplementary Table S9",
        "missing_metadata": {
            "manifest": {"reason": "unreported", "note": "The table gives sequence lengths only; it does not say which target or design task was run."},
            "total_targets": {"reason": "unreported", "note": "Not stated."},
        },
        "review": review(PARSE_REVIEW, PARSE_NOTE),
    },
    status="source_checked",
    sources=[S["paper"], S["site"]],
    facets={"areas": ["protein-structure"], "contexts": ["research"]},
)

dataset(
    "dataset-vhh-expression-retrospective",
    "Retrospective VHH expression measurements",
    "The retrospective collection of public nanobody expression measurements combined with the authors' accumulated TorchCraft expression data, used to set a sequence-perplexity threshold for expression.",
    {
        "assay": "Protein expression yield in milligrams, with at least 0.08 mg total treated as high expression",
        "scope_note": "Public expression measurements combined with accumulated TorchCraft expression data. Neither the number of sequences nor the split between the two sources is stated.",
        "access": "Not released: no accession, table or file is given for these measurements.",
        "source_locator": "Appendix A.4.3.2; Supplementary Figure S4",
        "missing_metadata": {
            "total": {"reason": "unreported", "note": "The number of measured sequences is not stated."},
            "accession": {"reason": "unreported", "note": "The public measurements are not cited individually."},
            "manifest": {"reason": "unavailable", "note": "No sequence list or measurement table is released."},
        },
    },
    status="source_checked",
    facets={"areas": ["proteins-complexes"], "contexts": ["research"]},
)

# --------------------------------------------------------------------------- dataset subsets (per campaign target)
CAMPAIGN = {
    "minibinder": [
        ("ifnar2", "IFNAR2", "3se4", "C34-232", "4000 nM to 62.5 nM, or 125 nM to 1.95 nM"),
        ("il7ra", "IL-7Ra", "7opb", "B36-231", "500 nM to 31.25 nM"),
        ("pdgfrb", "PDGFRb", "3mjg", "X124-312", "100 nM to 3.125 nM"),
        ("pdl1", "PD-L1", "8znl", "B20-133", "4000 nM to 62.5 nM"),
    ],
    "vhh": [
        ("bhrf1", "BHRF1", "2wh6", "A2-158", "2000 nM to 31.25 nM"),
        ("efna5", "EFNA5", "2x11", "B32-171", "4000 nM to 125 nM"),
        ("pdgfrb", "PDGFRb", "3mjg", "X124-312", "3200 nM to 50 nM"),
        ("s100a4", "S100A4", "5lpu", "C2-90", "4000 nM to 125 nM"),
    ],
}
for fmt, rows in CAMPAIGN.items():
    for slug, label, pdb, chain, series in rows:
        add(
            "dataset-" + fmt + "-campaign-" + slug,
            "dataset_subset",
            label + " measurements of the " + ("minibinder" if fmt == "minibinder" else "VHH") + " validation campaign",
            "The binding measurements against " + label + " in the " + ("minibinder" if fmt == "minibinder" else "VHH") + " validation campaign.",
            {
                "subset_scope": "One target of the campaign: " + label + " (PDB " + pdb + ", chain and residues " + chain + ").",
                "source_locator": "Supplementary Table S" + ("2" if fmt == "minibinder" else "3") + " row '" + label + "'; Appendix A.5."
                                  + ("1.5" if fmt == "minibinder" else "2.6") + " dilution series",
                "version": "As published in arXiv:2609.19770v1",
                "scored_count": 1,
                "test_denominators": "One displayed representative design. The number of designs expressed and tested against this target is not stated.",
                "missing_metadata": {
                    "eligible_count": {"reason": "unreported", "note": "The preprint does not state how many candidates were expressed and tested per target."},
                },
                "reuse_note": "Serial dilution of the target protein: " + series + ", with a 120 s association and 300 s dissociation and a 1:1 binding model.",
                "review": review(PDF_REVIEW, TRANSCRIPTION_NOTE),
            },
            status="source_checked",
            sources=[S["paper"]],
            links=[
                {"relation": "same_data_as", "target_id": PREFIX + "dataset-" + fmt + "-campaign-targets"},
                {"relation": "used_in", "target_id": PREFIX + "protocol-bli-apparent-kd-" + fmt},
            ],
        )

# --------------------------------------------------------------------------- protocols
def protocol(rid, name, description, attrs, *, status, links, sources=None, facets=None):
    base = {"version": "As published in arXiv:2609.19770v1", "review": review(PDF_REVIEW, TRANSCRIPTION_NOTE)}
    base.update(attrs)
    add(rid, "protocol", name, description, base, status=status, sources=sources or [S["paper"]], links=links, facets=facets)


for fmt, label, locator, pool, filters, series in [
    ("minibinder", "minibinder", "Section 2.2; Appendix A.2.2.1 and A.5.1.5",
     "3,000 candidates generated per target",
     "radius of gyration below 17, binder pTM above 0.7 and TorchCraft ipTM above 0.7, then ranked by Rosetta Interface Analyzer with the composite score 100 x TorchCraft ipTM minus the Rosetta interface score",
     "His-tagged binders at 5 ug/mL loaded on anti-His sensors for 120 s; target proteins in serial dilution; 120 s association and 300 s dissociation; buffer-only background subtraction; apparent KD from a 1:1 binding model"),
    ("vhh", "VHH", "Section 2.3; Appendix A.2.2.2 and A.5.2.6",
     "12,500 candidates generated per target",
     "CDR interface rate above 0.6, CDR3 hotspot coverage rate above 0 and TorchCraft ipTM above 0.7, then ranked by Rosetta Interface Analyzer with the composite score 100 x TorchCraft ipTM minus the Rosetta interface score",
     "His-tagged VHHs at 5 ug/mL loaded on anti-His sensors for 120 s; target proteins in serial dilution; 120 s association and 300 s dissociation; buffer-only background subtraction; apparent KD from a 1:1 binding model"),
]:
    protocol(
        "protocol-bli-apparent-kd-" + fmt,
        "Apparent dissociation constant of a selected " + label + " design by biolayer interferometry",
        "Measures the apparent dissociation constant of a selected " + label + " design against its target by multi-concentration biolayer interferometry with a 1:1 binding model.",
        {
            "metric": "dissociation-constant",
            "metric_direction": "lower",
            "unit": "nanomolar",
            "metric_definition": "Apparent dissociation constant (KD) from a 1:1 binding model fitted to multi-concentration biolayer interferometry traces after buffer-only background subtraction.",
            "metric_qualifier": "apparent KD of one displayed representative design, not a campaign hit rate",
            "procedure": series,
            "selection": pool + ", filtered by " + filters + "; the top-ranked designs were selected for experimental validation. The tested sequences were raw TorchCraft outputs with no post hoc MPNN redesign.",
            "selection_bias": (
                "The measured designs are the survivors of a confidence filter and a Rosetta ranking over a large "
                "generated pool, and only representative designs are displayed. A measured affinity here is evidence "
                "that selected designs bind; it is not a success rate for the campaign, and the number of designs "
                "expressed and tested is not stated."
            ),
            "measurement_status": "Experimentally measured by the authors",
            "source_locator": locator,
            "limitations": [
                "Apparent affinity from a 1:1 fit on an immobilised binder, not a solution-phase equilibrium measurement.",
                "The tested denominator is unreported, so no hit rate can be derived.",
                "Binding does not establish that the predicted interface is correct.",
            ],
            "missing_metadata": {
                "denominator": {"reason": "unreported", "note": "The preprint does not state how many designs were expressed and tested per target."},
                "replicates": {"reason": "unreported", "note": "No replicate count is given for the reported KD values."},
            },
        },
        status="source_checked",
        links=[
            {"relation": "evaluates_task", "target_id": PREFIX + ("task-minibinder-design" if fmt == "minibinder" else "task-vhh-design")},
            {"relation": "uses_data", "target_id": PREFIX + "dataset-" + fmt + "-campaign-targets"},
        ],
    )

protocol(
    "protocol-minibinder-torchscore-pass-rate",
    "Minibinder computational pass rate under TorchScore confidence",
    "Scores the fraction of designed minibinders whose TorchScore pTM and ipTM both exceed 0.7.",
    {
        "metric": "success-rate",
        "metric_direction": "higher",
        "unit": "percent",
        "metric_definition": "A design passes when both TorchScore pTM and TorchScore ipTM exceed 0.7. Figure 2f aggregates over binder lengths of 75, 120, 160 and 200 residues.",
        "metric_qualifier": "computational pass rate under TorchScore pTM above 0.7 and ipTM above 0.7, aggregated over four binder lengths",
        "procedure": (
            "100 designs per method, per length, per target. BoltzGen and RFdiffusion backbones were redesigned with "
            "ProteinMPNN eight times without fixing residues, each redesign rebuilt with FlowPacker, the eight models "
            "scored with TorchScore and the redesign with the highest pTM plus ipTM kept. Raw TorchCraft outputs were "
            "scored directly."
        ),
        "capacity": 100,
        "success_threshold": {"evaluator": "TorchScore", "ptm": "> 0.7", "iptm": "> 0.7"},
        "configurations_in_same_table_not_intaken": ["BoltzGen", "RFdiffusion", "TorchCraft with ProteinMPNN polishing"],
        "metric_implementation": "TorchScore, a score-only loading of TorchFold on the same pretrained AlphaFold 3 weights used for design; it does not refold sequences.",
        "aggregation": "Pass rate per target, aggregated over binder lengths of 75, 120, 160 and 200 residues",
        "source_locator": "Figure 2f caption; Appendix A.4.3.1",
        "limitations": [
            "Figure 2f prints no numbers, so no value is recorded in this batch.",
            "The evaluator uses the weights the TorchCraft designs were optimised against, which the preprint acknowledges.",
            "A predictor-derived pass rate is not an experimental success rate.",
        ],
        "missing_metadata": {
            "denominator": {"reason": "unextracted", "note": "Per-target denominators are not printed; the method states 100 designs per length per target."},
        },
    },
    status="discovered",
    links=[
        {"relation": "part_of", "target_id": PREFIX + "benchmark-minibinder-12-target"},
        {"relation": "evaluates_task", "target_id": PREFIX + "task-minibinder-design"},
        {"relation": "uses_data", "target_id": PREFIX + "dataset-minibinder-benchmark-targets"},
    ],
)

protocol(
    "protocol-vhh-torchscore-perplexity-pass-rate",
    "VHH computational pass rate under TorchScore confidence and ESM2 perplexity",
    "Scores the fraction of designed VHHs whose TorchScore ipTM exceeds 0.7 and whose ESM2-150M perplexity falls below the expression threshold.",
    {
        "metric": "success-rate",
        "metric_direction": "higher",
        "unit": "percent",
        "metric_definition": "A design passes only when TorchScore ipTM exceeds 0.7 and ESM2-150M perplexity is below 6.31, a threshold taken from a retrospective nanobody-expression analysis.",
        "metric_qualifier": "computational pass rate under joint TorchScore ipTM above 0.7 and ESM2-150M perplexity below 6.31",
        "procedure": (
            "100 designs per method, per framework, per target. BoltzGen and RFantibody sequences were redesigned eight "
            "times with AbMPNN without fixing residues; Germinal followed its own pipeline, fixing interface-contacting "
            "CDR residues and redesigning outside the CDRs. Each redesign was rebuilt with FlowPacker, the eight models "
            "scored with TorchScore and the redesign with the highest ipTM kept. Raw TorchCraft outputs were scored directly."
        ),
        "capacity": 100,
        "success_threshold": {"evaluator": "TorchScore", "iptm": "> 0.7", "esm2_150m_perplexity": "< 6.31"},
        "configurations_in_same_table_not_intaken": ["BoltzGen", "RFantibody", "Germinal", "TorchCraft with AbMPNN polishing"],
        "metric_implementation": "TorchScore on the same pretrained AlphaFold 3 weights used for design, plus ESM2-150M perplexity",
        "aggregation": "Pass rate per target; a framework-stratified version is shown in Supplementary Figure S5",
        "source_locator": "Figure 3i caption; Supplementary Figure S5; Appendix A.4.3.2",
        "limitations": [
            "Figures 3i and S5 print no numbers, so no value is recorded in this batch.",
            "The evaluator uses the weights the TorchCraft designs were optimised against.",
            "The expression proxy threshold comes from the authors' own unreleased retrospective expression data.",
            "A predictor-derived pass rate is not an experimental success rate.",
        ],
        "missing_metadata": {
            "denominator": {"reason": "unextracted", "note": "Per-target denominators are not printed; the method states 100 designs per framework per target."},
        },
    },
    status="discovered",
    links=[
        {"relation": "part_of", "target_id": PREFIX + "benchmark-vhh-15-target"},
        {"relation": "evaluates_task", "target_id": PREFIX + "task-vhh-design"},
        {"relation": "uses_data", "target_id": PREFIX + "dataset-vhh-benchmark-targets"},
    ],
)

protocol(
    "protocol-cyclic-peptide-pass-rate",
    "Cyclic peptide computational pass rate under cyclisation and TorchScore confidence",
    "Scores the fraction of designed cyclic peptides whose predicted structure forms the intended cycle without chain breaks and whose TorchScore pLDDT and ipTM exceed their thresholds.",
    {
        "metric": "success-rate",
        "metric_direction": "higher",
        "unit": "percent",
        "metric_definition": "A design passes only if the predicted structure forms the intended cycle without chain breaks and satisfies TorchScore pLDDT above 70 and ipTM above 0.5.",
        "metric_qualifier": "computational pass rate under intended cyclisation, no chain breaks, TorchScore pLDDT above 70 and ipTM above 0.5",
        "procedure": (
            "100 designs per method per target in the head-to-tail setting. BoltzGen and RFpeptides sequences were "
            "redesigned eight times with ProteinMPNN without fixing residues, rebuilt with FlowPacker, scored with "
            "TorchScore and the redesign with the highest pLDDT plus 100 times ipTM kept. Raw TorchCraft outputs were "
            "scored directly, in both a head-to-tail and a disulfide-linked setting."
        ),
        "capacity": 100,
        "success_threshold": {"evaluator": "TorchScore", "cyclisation": "intended cycle formed without chain breaks", "plddt": "> 70", "iptm": "> 0.5"},
        "configurations_in_same_table_not_intaken": ["BoltzGen", "RFpeptides", "TorchCraft with ProteinMPNN polishing"],
        "metric_implementation": "TorchScore on the same pretrained AlphaFold 3 weights used for design, with a cyclisation and backbone-integrity classification",
        "aggregation": "Pass rate per target and cyclisation mode",
        "source_locator": "Figure 4c caption; Appendix A.4.3.3; Supplementary Figure S6",
        "limitations": [
            "Figure 4c prints no numbers, so no value is recorded in this batch.",
            "Computational only: no cyclic peptide was measured experimentally.",
            "The evaluator uses the weights the TorchCraft designs were optimised against.",
        ],
        "missing_metadata": {
            "denominator": {"reason": "unextracted", "note": "Per-target denominators are not printed; the method states 100 designs per target for the head-to-tail setting and does not state a count for the disulfide-linked setting."},
        },
    },
    status="discovered",
    links=[
        {"relation": "part_of", "target_id": PREFIX + "benchmark-cyclic-peptide-8-target"},
        {"relation": "evaluates_task", "target_id": PREFIX + "task-cyclic-peptide-design"},
        {"relation": "uses_data", "target_id": PREFIX + "dataset-cyclic-peptide-benchmark-targets"},
    ],
)

protocol(
    "protocol-ligand-pocket-torchscore-pass-rate",
    "Ligand-pocket computational pass rate under TorchScore confidence",
    "Scores the fraction of designed ligand-binding proteins whose TorchScore pLDDT exceeds 70 and whose TorchScore ipTM exceeds 0.7.",
    {
        "metric": "success-rate",
        "metric_direction": "higher",
        "unit": "percent",
        "metric_definition": "A design passes when TorchScore pLDDT exceeds 70 and TorchScore ipTM exceeds 0.7.",
        "metric_qualifier": "computational pass rate under TorchScore pLDDT above 70 and ipTM above 0.7",
        "procedure": "500 designs of 160 residues per ligand, generated without a supplied native scaffold and evaluated without post hoc redesign or score-based preselection.",
        "capacity": 500,
        "success_threshold": {"evaluator": "TorchScore", "plddt": "> 70", "iptm": "> 0.7"},
        "metric_implementation": "TorchScore on the same pretrained AlphaFold 3 weights used for design",
        "aggregation": "Pass rate per ligand",
        "source_locator": "Supplementary Figure S9; Appendix A.4.3.4",
        "limitations": [
            "Supplementary Figure S9 prints no numbers, so no value is recorded in this batch.",
            "Reported for TorchCraft only; the preprint does not report this pass rate for BoltzDesign.",
            "Computational only: no designed pocket was measured experimentally.",
        ],
    },
    status="discovered",
    links=[
        {"relation": "part_of", "target_id": PREFIX + "benchmark-ligand-pocket-10-ligand"},
        {"relation": "evaluates_task", "target_id": PREFIX + "task-ligand-pocket-design"},
        {"relation": "uses_data", "target_id": PREFIX + "dataset-ligand-panel-10"},
    ],
    facets={"areas": ["molecular-interactions", "protein-structure"], "contexts": ["research"]},
)

protocol(
    "protocol-ligand-pocket-vina-score",
    "Docking score of designed ligand pockets",
    "Scores designed ligand-binding proteins by docking the ligand into them with AutoDock Vina.",
    {
        "metric_definition": "AutoDock Vina docking score in kcal/mol for each designed pocket, shown as a distribution per ligand. No numeric value is printed.",
        "procedure": "500 designs of 160 residues per method per ligand; BoltzDesign and raw TorchCraft outputs were assessed without sequence redesign, and a LigandMPNN-redesigned TorchCraft variant was assessed separately.",
        "capacity": 500,
        "configurations_in_same_table_not_intaken": ["BoltzDesign", "TorchCraft with LigandMPNN redesign"],
        "metric_implementation": "AutoDock Vina, cited as Trott and Olson 2010 and Eberhardt et al. 2021; no version is given",
        "source_locator": "Figure 5c caption; Appendix A.4.3.4",
        "limitations": [
            "Figure 5c prints no numbers, so no value is recorded in this batch.",
            "A docking score of a predicted pocket is not a measured affinity.",
        ],
        "missing_metadata": {
            "metric": {"reason": "unextracted", "note": "No metric concept in data/vocab/metric.ttl covers a docking score; none was added because no value is recorded."},
        },
    },
    status="discovered",
    links=[
        {"relation": "part_of", "target_id": PREFIX + "benchmark-ligand-pocket-10-ligand"},
        {"relation": "evaluates_task", "target_id": PREFIX + "task-ligand-pocket-design"},
        {"relation": "uses_data", "target_id": PREFIX + "dataset-ligand-panel-10"},
    ],
    facets={"areas": ["molecular-interactions"], "contexts": ["research"]},
)

protocol(
    "protocol-ligand-pocket-boltz2-affinity",
    "Predicted affinity of designed ligand pockets",
    "Scores designed ligand-binding proteins by predicting the affinity of the designed complex with Boltz-2.",
    {
        "metric_definition": "Boltz-2 affinity prediction for each designed pocket, shown as a distribution per ligand. No numeric value is printed.",
        "procedure": "The same 500 designs per method per ligand assessed with AutoDock Vina were also assessed with Boltz-2 affinity prediction.",
        "capacity": 500,
        "configurations_in_same_table_not_intaken": ["BoltzDesign", "TorchCraft with LigandMPNN redesign"],
        "metric_implementation": "Boltz-2 affinity prediction; no version is given",
        "source_locator": "Figure 5d caption; Appendix A.4.3.4",
        "limitations": [
            "Figure 5d prints no numbers, so no value is recorded in this batch.",
            "A predicted affinity for a predicted structure is not a measurement.",
        ],
        "missing_metadata": {
            "metric": {"reason": "unextracted", "note": "The printed quantity is a model-specific affinity prediction with no stated unit; no concept was added because no value is recorded."},
        },
    },
    status="discovered",
    links=[
        {"relation": "part_of", "target_id": PREFIX + "benchmark-ligand-pocket-10-ligand"},
        {"relation": "evaluates_task", "target_id": PREFIX + "task-ligand-pocket-design"},
        {"relation": "uses_data", "target_id": PREFIX + "dataset-ligand-panel-10"},
    ],
    facets={"areas": ["molecular-interactions"], "contexts": ["research"]},
)

LENGTHS = ["100", "200", "300", "400", "500"]
for length in LENGTHS:
    protocol(
        "protocol-runtime-" + length + "aa",
        "TorchCraft runtime per design at " + length + " residues",
        "Measures the wall-clock time a TorchCraft design run takes per design at a sequence length of " + length + " residues.",
        {
            "metric": "runtime",
            "metric_direction": "lower",
            "unit": "minute",
            "unit_detail": "minutes per design",
            "metric_definition": "Minutes per design: the total wall-clock time of a batch-size-2 run divided by 2. GPU timings are the mean of three independent runs.",
            "metric_qualifier": "wall-clock minutes per design at " + length + " residues, batch size 2",
            "procedure": "A design run at " + length + " residues on the stated machine and operator setting, timed end to end and divided by the batch size.",
            "memory_measurement": "Not reported, except that the 500-residue NPU run without fused attention needed batch size 1 because batch size 2 exceeded memory.",
            "source_locator": "Supplementary Table S9, column '" + length + " aa'",
            "limitations": [
                "Timed by the authors on their own hardware; not reproduced.",
                "The design task behind the timings is not stated.",
                "NPU and GPU timings come from different machines, so the two platforms are not a controlled comparison.",
            ],
            "missing_metadata": {
                "replicates": {"reason": "unreported", "note": "GPU timings are the mean of three runs; the NPU timings give no replicate count."},
            },
            "review": review(PARSE_REVIEW, PARSE_NOTE),
        },
        status="source_checked",
        links=[
            {"relation": "part_of", "target_id": PREFIX + "benchmark-runtime"},
            {"relation": "evaluates_task", "target_id": PREFIX + "task-design-runtime"},
            {"relation": "uses_data", "target_id": PREFIX + "dataset-runtime-design-runs"},
        ],
        facets={"areas": ["protein-structure"], "contexts": ["research"]},
    )

CLASSIFIER_PROTOCOLS = [
    ("mcc", "matthews-correlation-coefficient", "higher", "unitless",
     "Matthews correlation coefficient of the high-expression classification at the selected perplexity threshold",
     "Matthews correlation coefficient at the selected threshold, which was chosen to maximise it",
     "VHH expression classification by ESM2-150M perplexity: Matthews correlation coefficient",
     "Scores how well ESM2-150M sequence perplexity classifies VHH designs as expressing at least 0.08 mg in total, as the Matthews correlation coefficient at the chosen threshold."),
    ("pearson", "pearson-correlation", "unknown", "unitless",
     "Pearson correlation between ESM2-150M perplexity and measured expression",
     "Pearson correlation between perplexity and expression; the expected relation is negative, so neither direction is uniformly better",
     "VHH expression against ESM2-150M perplexity: Pearson correlation",
     "Measures the linear correlation between ESM2-150M sequence perplexity and measured VHH expression."),
    ("spearman", "spearman-correlation", "unknown", "unitless",
     "Spearman rank correlation between ESM2-150M perplexity and measured expression",
     "Spearman rank correlation between perplexity and expression; the expected relation is negative, so neither direction is uniformly better",
     "VHH expression against ESM2-150M perplexity: Spearman correlation",
     "Measures the rank correlation between ESM2-150M sequence perplexity and measured VHH expression."),
]
for slug, metric, direction, unit, definition, qualifier, protocol_name, protocol_description in CLASSIFIER_PROTOCOLS:
    protocol(
        "protocol-vhh-expression-" + slug,
        protocol_name,
        protocol_description,
        {
            "metric": metric,
            "metric_direction": direction,
            "unit": unit,
            "metric_definition": definition + ". High expression is a total of at least 0.08 mg.",
            "metric_qualifier": qualifier,
            "procedure": "Retrospective analysis combining public nanobody expression measurements with the authors' accumulated TorchCraft expression data; ESM2-150M perplexity was swept as a one-dimensional classifier and the operating threshold chosen by maximising the Matthews correlation coefficient.",
            "selection_bias": "Retrospective and threshold-fitted on the same collection, so the reported figures are in-sample.",
            "source_locator": "Supplementary Figure S4b caption; Appendix A.4.3.2",
            "limitations": [
                "In-sample: the threshold was chosen on the same data the statistics describe.",
                "The underlying expression measurements are not released and their number is not stated.",
            ],
            "missing_metadata": {
                "denominator": {"reason": "unreported", "note": "The number of sequences in the retrospective collection is not stated."},
            },
        },
        status="source_checked",
        links=[
            {"relation": "evaluates_task", "target_id": PREFIX + "task-vhh-expression-prediction"},
            {"relation": "uses_data", "target_id": PREFIX + "dataset-vhh-expression-retrospective"},
        ],
        facets={"areas": ["proteins-complexes"], "contexts": ["research"]},
    )

# --------------------------------------------------------------------------- evaluations and results
def evaluation(rid, name, description, system, assessment, data, comparison, attrs, *, sources=None, facets=None, status="source_checked"):
    base = {
        "origin": "author_reported",
        "comparison": comparison,
        "version": "As published in arXiv:2609.19770v1",
        "review": review(PDF_REVIEW, TRANSCRIPTION_NOTE),
    }
    base.update(attrs)
    add(
        rid,
        "evaluation",
        name,
        description,
        base,
        status=status,
        sources=sources or [S["paper"]],
        links=[
            {"relation": "system", "target_id": system},
            {"relation": "assessment", "target_id": assessment},
            {"relation": "data", "target_id": data},
        ],
        facets=facets,
    )


def result(rid, name, description, evaluation_id, attrs, *, sources=None, facets=None):
    base = {"review": review(PDF_REVIEW, TRANSCRIPTION_NOTE)}
    base.update(attrs)
    add(rid, "result", name, description, base, status="source_checked", sources=sources or [S["paper"]],
        links=[{"relation": "evaluation", "target_id": evaluation_id}], facets=facets)


KD = {
    "minibinder": {"ifnar2": ("60.2", "IFNAR2"), "il7ra": ("8.55", "IL-7Ra"), "pdgfrb": ("2.04", "PDGFRb"), "pdl1": ("23.3", "PD-L1")},
    "vhh": {"bhrf1": ("24.3", "BHRF1"), "efna5": ("122", "EFNA5"), "pdgfrb": ("268", "PDGFRb"), "s100a4": ("354", "S100A4")},
}
KD_SENTENCE = {
    "minibinder": 'Figure 2a caption (page 4), sentence "Apparent dissociation constants of the displayed binders were 60.2, 8.55, 2.04, and 23.3 nM, respectively."',
    "vhh": 'Figure 3a caption (page 5), sentence "Apparent dissociation constants of the displayed binders were 24.3, 122, 268, and 354 nM, respectively."',
}
KD_ORDER = {"minibinder": ["ifnar2", "il7ra", "pdgfrb", "pdl1"], "vhh": ["bhrf1", "efna5", "pdgfrb", "s100a4"]}
KD_POOL = {"minibinder": 3000, "vhh": 12500}
KD_SECTION = {"minibinder": "Section 2.2", "vhh": "Section 2.3"}

for fmt in ("minibinder", "vhh"):
    label_fmt = "minibinder" if fmt == "minibinder" else "VHH"
    for slug in KD_ORDER[fmt]:
        value, target = KD[fmt][slug]
        eval_id = PREFIX + "evaluation-bli-kd-" + fmt + "-" + slug
        evaluation(
            "evaluation-bli-kd-" + fmt + "-" + slug,
            "Measured binding of a selected TorchCraft " + label_fmt + " to " + target,
            "The biolayer interferometry measurement of the displayed TorchCraft " + label_fmt + " design against " + target + ".",
            PREFIX + "config-" + ("minibinder" if fmt == "minibinder" else "vhh") + "-raw",
            PREFIX + "protocol-bli-apparent-kd-" + fmt,
            PREFIX + "dataset-" + fmt + "-campaign-" + slug,
            {
                "protocol_id": PREFIX + "protocol-bli-apparent-kd-" + fmt,
                "dataset_version": "Target " + target + " as prepared in Supplementary Table S" + ("7" if fmt == "minibinder" else "8"),
                "split": None,
                "population": "One displayed representative design against " + target + "; the number of designs expressed and tested is not stated",
                "inputs": "Target structure with crop and hotspots from Supplementary Table S" + ("2" if fmt == "minibinder" else "3") + ", and a " + ("binder length range" if fmt == "minibinder" else "fixed framework with CDR length ranges"),
                "adaptation": "Raw TorchCraft output; no post hoc MPNN sequence redesign",
                "metric_implementation": "Apparent KD from a 1:1 binding model in the instrument's curve-fitting module, after buffer-only background subtraction",
                "aggregation": None,
                "budget": str(KD_POOL[fmt]) + " candidates generated for this target before filtering and ranking",
            },
            {
                "candidate_budget": KD_POOL[fmt],
                "candidate_selection": (
                    "Filtered by " + ("radius of gyration below 17, binder pTM above 0.7 and TorchCraft ipTM above 0.7"
                                      if fmt == "minibinder" else
                                      "CDR interface rate above 0.6, CDR3 hotspot coverage rate above 0 and TorchCraft ipTM above 0.7")
                    + ", then ranked by the composite score 100 x TorchCraft ipTM minus the Rosetta interface score; the top-ranked designs were selected for validation."
                ),
                "candidate_denominator": "Unreported: the preprint states the generated pool and the filters, but not how many designs were expressed and tested.",
                "coverage": {"scored": 1, "unit": "displayed designs", "note": "One representative design is displayed for this target; the tested denominator is not stated."},
                "interpretation": "Experimentally measured by the authors and not reproduced here. One selected design bound its target; this is not a campaign hit rate.",
                "endpoint": "Apparent dissociation constant of a selected design",
                "limitations": [
                    "A single displayed design, not a campaign hit rate.",
                    "Developer-measured and selected after confidence filtering and Rosetta ranking.",
                    "Binding does not establish that the predicted interface is correct.",
                ],
                "missing_metadata": {
                    "denominator": {"reason": "unreported", "note": "The number of designs expressed and tested against this target is not stated."},
                    "replicate_count": {"reason": "unreported", "note": "No replicate count is given for the reported KD."},
                },
            },
        )
        result(
            "result-bli-kd-" + fmt + "-" + slug,
            "Apparent KD of the displayed TorchCraft " + label_fmt + " against " + target,
            "The apparent dissociation constant printed for the displayed TorchCraft " + label_fmt + " design against " + target + ".",
            eval_id,
            {
                "printed_value": value,
                "numeric_value": value,
                "metric": "dissociation-constant",
                "metric_direction": "lower",
                "metric_qualifier": "apparent KD of one displayed representative design from a filtered and ranked pool, not a campaign hit rate",
                "unit": "nanomolar",
                "unit_detail": "nanomolar, printed as nM",
                "coverage": {"scored": 1, "unit": "displayed designs", "note": "One representative design; the tested denominator is not stated."},
                "source_locator": KD_SENTENCE[fmt] + "; value for " + target + ". The same number is printed in " + KD_SECTION[fmt] + " and in the Figure " + ("2a" if fmt == "minibinder" else "3a") + ' panel label "KD: ' + value + 'nM".',
                "claim_scope": "One displayed design against one target. It is not a success rate and not a solution-phase equilibrium constant.",
                "missing_metadata": {
                    "uncertainty": {"reason": "unreported", "note": "No error, interval or replicate spread is printed for the KD values."},
                    "denominator": {"reason": "unreported", "note": "The number of designs expressed and tested against this target is not stated."},
                },
                "review": review(PDF_REVIEW, TRANSCRIPTION_NOTE, "Transcribed from the figure caption sentence and cross-checked against the body text and the figure panel label, which print the same value. The caption lists four values in target order; the order was checked against the panel labels."),
            },
        )

# runtime results, from the parse
parse = subprocess.run([sys.executable, str(HERE / "extract" / "parse_runtime_table.py")], capture_output=True, text=True)
if parse.returncode != 0:
    sys.exit("extract/parse_runtime_table.py failed:\n" + parse.stdout + parse.stderr)
runtime_values = json.loads(parse.stdout)

for rid, name, code, operator, machine, hardware in RUNTIME_ROWS:
    row_key = code + " " + operator
    for length in LENGTHS:
        value = runtime_values[row_key][length]
        oom = row_key == "NPU w/o FA" and length == "500"
        eval_id = PREFIX + "evaluation-runtime-" + rid + "-" + length + "aa"
        attrs = {
            "inference_hardware": hardware,
            "n_runs": 3 if code == "GPU" else None,
            "endpoint": "Wall-clock minutes per design",
            "interpretation": "Timed by the authors on their own hardware and not reproduced here.",
            "limitations": [
                "Timed by the authors; not reproduced.",
                "The design task behind the timing is not stated.",
            ] + (["Timed at batch size 1 because batch size 2 exceeded memory, unlike every other cell of the table."] if oom else []),
        }
        if code != "GPU":
            del attrs["n_runs"]
            attrs["missing_metadata"] = {"n_runs": {"reason": "unreported", "note": "Only the GPU timings are stated to be the mean of three runs."}}
        evaluation(
            "evaluation-runtime-" + rid + "-" + length + "aa",
            "TorchCraft runtime at " + length + " residues, " + code + " " + operator,
            "The timed TorchCraft design run at " + length + " residues on " + hardware + ".",
            PREFIX + "config-runtime-" + rid,
            PREFIX + "protocol-runtime-" + length + "aa",
            PREFIX + "dataset-runtime-design-runs",
            {
                "protocol_id": PREFIX + "protocol-runtime-" + length + "aa",
                "dataset_version": "Runtime benchmark runs as published in Supplementary Table S9",
                "split": None,
                "population": "Design runs at " + length + " residues",
                "inputs": "A design run at " + length + " residues; the target and design task are not stated",
                "adaptation": "Batch size 2" + (" except this cell, which was timed at batch size 1 after batch size 2 exceeded memory" if oom else ""),
                "metric_implementation": "Total wall-clock time of a batch-size-2 run divided by 2" + ("; this cell is a batch-size-1 run" if oom else ""),
                "aggregation": "Mean of three independent runs" if code == "GPU" else None,
                "budget": hardware,
            },
            attrs,
            sources=[S["paper"], S["site"]],
            facets={"areas": ["protein-structure"], "contexts": ["research"]},
        )
        result_attrs = {
            "printed_value": value,
            "numeric_value": value,
            "metric": "runtime",
            "metric_direction": "lower",
            "metric_qualifier": "wall-clock minutes per design at " + length + " residues, batch size 2 run divided by 2" + (", measured at batch size 1 for this cell" if oom else ""),
            "unit": "minute",
            "unit_detail": "minutes per design",
            "hardware": hardware,
            "source_locator": 'Table S9, row "' + code + " " + operator + '", column "' + length + ' aa"',
            "review": review(PARSE_REVIEW, PARSE_NOTE, "The same value is printed on the official project site, which was compared with the parse."),
        }
        if oom:
            result_attrs["scope_note"] = "Printed with a footnote marker: batch size 1, because batch size 2 exceeded memory (OOM). Every other cell of the table is a batch-size-2 run."
            result_attrs["source_anomaly"] = "The cell is printed as '33.47*' with the footnote '* Batch size 1; batch size 2 exceeded memory (OOM).'; printed_value holds the number without the footnote marker."
        result_attrs["missing_metadata"] = {
            "uncertainty": {"reason": "unreported", "note": "No spread is printed; GPU cells are stated to be the mean of three runs without a spread."}
        }
        result(
            "result-runtime-" + rid + "-" + length + "aa",
            "TorchCraft runtime at " + length + " residues, " + code + " " + operator,
            "The printed runtime per design at " + length + " residues on " + hardware + ".",
            eval_id,
            result_attrs,
            sources=[S["paper"], S["site"]],
            facets={"areas": ["protein-structure"], "contexts": ["research"]},
        )

# expression classifier results
CLASSIFIER_VALUES = [
    ("mcc", "matthews-correlation-coefficient", "higher", "0.598", "0.598", "MCC = 0.598", "Matthews correlation coefficient"),
    ("pearson", "pearson-correlation", "unknown", "−0.538", "-0.538", "Pearson r = −0.538", "Pearson correlation"),
    ("spearman", "spearman-correlation", "unknown", "−0.602", "-0.602", "Spearman ρ = −0.602", "Spearman rank correlation"),
]
for slug, metric, direction, printed, numeric, printed_fragment, statistic in CLASSIFIER_VALUES:
    eval_id = PREFIX + "evaluation-vhh-expression-" + slug
    evaluation(
        "evaluation-vhh-expression-" + slug,
        "ESM2-150M perplexity against measured VHH expression: " + statistic,
        "The retrospective comparison of ESM2-150M perplexity with measured VHH expression, reported as the " + statistic.lower() + ".",
        PREFIX + "config-esm2-150m-expression-classifier",
        PREFIX + "protocol-vhh-expression-" + slug,
        PREFIX + "dataset-vhh-expression-retrospective",
        {
            "protocol_id": PREFIX + "protocol-vhh-expression-" + slug,
            "dataset_version": "Retrospective collection as described in Appendix A.4.3.2",
            "split": None,
            "population": "Public nanobody expression measurements combined with accumulated TorchCraft expression data; the number of sequences is not stated",
            "inputs": "VHH sequence only",
            "adaptation": "Perplexity swept as a one-dimensional classifier, with the operating threshold chosen to maximise the Matthews correlation coefficient",
            "metric_implementation": "ESM2-150M perplexity; high expression defined as a total of at least 0.08 mg",
            "aggregation": None,
            "budget": None,
        },
        {
            "retrospective": True,
            "endpoint": "Separation of high-expression VHH designs by sequence perplexity",
            "limitations": [
                "In-sample: the threshold was selected on the same collection.",
                "The underlying measurements are not released and their number is not stated.",
            ],
            "missing_metadata": {
                "denominator": {"reason": "unreported", "note": "The number of sequences in the retrospective collection is not stated."},
            },
        },
        facets={"areas": ["proteins-complexes"], "contexts": ["research"]},
    )
    result(
        "result-vhh-expression-" + slug,
        "ESM2-150M perplexity against measured VHH expression: " + statistic,
        "The printed " + statistic.lower() + " for ESM2-150M perplexity against measured VHH expression.",
        eval_id,
        {
            "printed_value": printed,
            "numeric_value": numeric,
            "metric": metric,
            "metric_direction": direction,
            "metric_qualifier": "retrospective, in-sample statistic at the Matthews-correlation-maximising perplexity threshold, high expression defined as at least 0.08 mg",
            "unit": "unitless",
            "source_locator": 'Supplementary Figure S4 caption, panel b (page 32), fragment "' + printed_fragment + '"',
            "claim_scope": "A retrospective in-sample statistic on unreleased expression measurements, used to set the expression proxy in the VHH benchmark criterion.",
            "missing_metadata": {
                "uncertainty": {"reason": "unreported", "note": "No interval or p-value is printed for these statistics."},
                "denominator": {"reason": "unreported", "note": "The number of sequences behind the statistic is not stated."},
            },
            "review": review(PDF_REVIEW, TRANSCRIPTION_NOTE, "Transcribed from the Figure S4 caption. The caption prints the selected threshold as 6.309 while Appendix A.4.3.2 prints it as 6.31; both are recorded on the configuration and neither was changed."),
        },
        facets={"areas": ["proteins-complexes"], "contexts": ["research"]},
    )

# --------------------------------------------------------------------------- claims
SUBJECT_NAMES = {r["id"]: r["name"] for r in records}


def claim(rid, name, subject, field, value, locator, *, sources=None, rationale=None, limitations=None, review_obj=None, facets=None, status="source_checked"):
    attrs = {
        "field": field,
        "value": value,
        "source_locator": locator,
        "review": review_obj or review(PDF_REVIEW, TRANSCRIPTION_NOTE),
    }
    if rationale:
        attrs["rationale"] = rationale
    if limitations:
        attrs["limitations"] = limitations
    subject_name = SUBJECT_NAMES.get(subject, subject)
    full_name = subject_name + ": " + name
    add(rid, "claim", full_name, "Descriptive fact transcribed from the pinned sources with its own locator.",
        attrs, status=status, sources=sources or [S["paper"]], links=[{"relation": "subject", "target_id": subject}], facets=facets)


WEB_README_REVIEW = review(WEB_REVIEW, "Read from the pinned README at commit " + COMMIT + ".", locator_url="https://raw.githubusercontent.com/Mingchenchen/TorchX/" + COMMIT + "/README.md", sha=README_SHA)

claim(
    "claim-evaluated-weight-configuration",
    "Every reported TorchCraft experiment used pretrained AlphaFold 3 weights",
    PREFIX + "pipeline-torchcraft",
    "evaluated_weight_configuration",
    "All designs reported in the preprint, both the experimentally validated minibinders and VHHs and the computational benchmarks, were generated with pretrained AlphaFold 3 weights through the TorchFold implementation.",
    'Abstract ("Using pretrained AlphaFold3 weights"); Section 1 final paragraph ("All designs reported here, including experimentally validated binders and computational benchmarks, were generated using pretrained AF3 weights"); Appendix A.1.1 ("All designs reported in this study used pretrained AF3 weights"); Figure 1 caption ("Experimental campaigns and computational benchmarks reported here used the same AF3-weight setting")',
    rationale="The configuration question the discovery issue raised. Four independent statements in the preprint agree, and no reported experiment uses the separately released TorchFold checkpoint.",
)

claim(
    "claim-no-trained-weights",
    "TorchCraft trains no model weights of its own",
    PREFIX + "pipeline-torchcraft",
    "training_status",
    "TorchCraft introduces no trained generative model: the predictor is frozen, only the editable sequence logits are updated, and the final sequence is obtained by discrete decoding.",
    'Abstract ("optimizes sequence logits through a frozen all-atom predictor"); Appendix A.1.1 ("the weighted design objective is differentiated with respect to L. Only the editable sequence variables are updated"); Appendix A.1.2 Algorithm 1',
    rationale="Recorded so that TorchCraft is not registered as a new pretrained model identity.",
)

claim(
    "claim-readme-weight-options",
    "The repository offers two mutually exclusive weight sources",
    PREFIX + "method-torchfold",
    "weight_source_options",
    "For folding, scoring and design the repository requires exactly one of CHECKPOINT_PATH or checkpoint_path, the TorchFold trained weights from the gated Hugging Face release, or MODEL_DIR or model_dir, a directory of official AlphaFold 3 parameters applied for from DeepMind. If both are set the checkpoint takes priority.",
    "README section 'Checkpoints'; torchcraft_gpu/README.md section 'Design'",
    sources=[S["readme"], S["design"]],
    rationale="The two settings are different configurations. The preprint's results belong to the AlphaFold 3 parameter setting only.",
    review_obj=WEB_README_REVIEW,
)

claim(
    "claim-abag-checkpoint-unused",
    "No reported result used the antibody-distilled TorchFold checkpoint",
    PREFIX + "config-torchfold-abag-checkpoint",
    "performance_claim_scope",
    "No design or benchmark result in the preprint was produced with the antibody-specialised TorchFold checkpoint. The Discussion names its use for CDR optimisation as a direction still to be tested with matched comparisons.",
    'Appendix A.1.1; Discussion final paragraph ("Its specialized checkpoint may offer more informative guidance during CDR optimization. Matched comparisons ... will be needed to test this potential")',
    rationale="Blocks any inheritance of the preprint's performance claims by the README's alternative checkpoint option.",
)

claim(
    "claim-torchscore-shared-weights",
    "TorchScore uses the design weights and does not refold sequences",
    PREFIX + "evaluator-torchscore",
    "scoring_dependency",
    "TorchScore is a score-only loading of TorchFold: it bypasses the diffusion structure module, trains no separate scoring network, and in this study used the same pretrained AlphaFold 3 weights used for design. It scores supplied coordinates, so designs rebuilt with FlowPacker were scored from those coordinates and were not refolded from sequence.",
    'Appendix A.4.2 ("No separate scoring network is trained. In this study, TorchScore used pretrained AF3 weights, the same checkpoint used for design ... they were not refolded from sequence by TorchScore"); Figure 2f and Figure 3i captions',
    rationale="Every pass-rate protocol in this batch rests on this evaluator, so the dependency is recorded once and named as a limitation on each of those protocols.",
)

claim(
    "claim-pass-rates-not-success-rates",
    "Predictor-derived pass rates are not experimental success rates",
    PREFIX + "evaluator-torchscore",
    "interpretation_limit",
    "The preprint states that predictor-derived pass rates are sensitive to the evaluator and should not be interpreted as experimental success rates.",
    "Discussion, paragraph beginning 'The current study has several limitations'",
)

claim(
    "claim-experimental-scope",
    "Experimental validation covers minibinders and VHHs only",
    PREFIX + "pipeline-torchcraft",
    "experimental_validation_scope",
    "Experimental validation is confined to minibinders and VHHs; the cyclic-peptide and small-molecule results remain computational.",
    "Discussion, paragraph beginning 'The current study has several limitations'; Sections 2.4 and 2.5",
)

claim(
    "claim-binding-not-interface-accuracy",
    "Binding does not establish the predicted interface is correct",
    PREFIX + "pipeline-torchcraft",
    "evidence_limit",
    "The preprint states that binding measurements do not by themselves establish the accuracy of the predicted interfaces.",
    "Discussion, paragraph beginning 'The current study has several limitations'",
)

claim(
    "claim-minibinder-candidate-pool",
    "Minibinder candidate pool, filters and selection",
    PREFIX + "protocol-bli-apparent-kd-minibinder",
    "candidate_pool",
    "3,000 TorchCraft candidates were generated per minibinder target, filtered by radius of gyration below 17, binder pTM above 0.7 and TorchCraft ipTM above 0.7, then ranked by Rosetta Interface Analyzer using the composite score 100 x TorchCraft ipTM minus the Rosetta interface score, and the highest-scoring candidates were taken to the wet lab. The number expressed and tested is not stated.",
    "Section 2.2; Appendix A.2.1 and A.2.2.1",
    rationale="Fixes the generated denominator and records that the tested denominator is unreported, so no hit rate can be derived from the displayed measurements.",
)

claim(
    "claim-vhh-candidate-pool",
    "VHH candidate pool, filters and selection",
    PREFIX + "protocol-bli-apparent-kd-vhh",
    "candidate_pool",
    "12,500 TorchCraft candidates were generated per VHH target, filtered by CDR interface rate above 0.6, CDR3 hotspot coverage rate above 0 and TorchCraft ipTM above 0.7, then ranked by Rosetta Interface Analyzer using the composite score 100 x TorchCraft ipTM minus the Rosetta interface score, and the top-ranked designs were selected for experimental validation. The number expressed and tested is not stated.",
    "Section 2.3; Appendix A.2.1 and A.2.2.2",
    rationale="Fixes the generated denominator and records that the tested denominator is unreported.",
)

claim(
    "claim-tested-sequences-raw",
    "The tested sequences were raw TorchCraft outputs",
    PREFIX + "pipeline-torchcraft",
    "tested_sequence_provenance",
    "The experimentally tested minibinder and VHH sequences were raw TorchCraft outputs, obtained without post hoc MPNN sequence redesign.",
    "Sections 2.2 and 2.3; Appendix A.2.1; Discussion",
)

claim(
    "claim-code-licence",
    "The TorchX code is Apache-2.0",
    PREFIX + "method-torchx",
    "code_licence",
    "The TorchX repository is released under the Apache License 2.0, as stated in the README and in the LICENSE file at commit " + COMMIT + ". The GitHub repository metadata reports the same licence. This covers the code only, not the gated checkpoint and training data, and not the upstream AlphaFold 3 parameters.",
    "LICENSE file, whole file; README section 'License'",
    sources=[S["licence"], S["readme"]],
    review_obj=review(WEB_REVIEW, "Read the LICENSE file and the README at the pinned commit; the GitHub repository API reports spdx_id Apache-2.0.", locator_url="https://raw.githubusercontent.com/Mingchenchen/TorchX/" + COMMIT + "/LICENSE", sha=LICENCE_SHA),
)

claim(
    "claim-project-site-licence-statement",
    "The project site states MIT, which conflicts with the repository licence",
    PREFIX + "method-torchx",
    "licence_conflict",
    "The official project site says the GPU and Ascend NPU implementations, the TorchFold training code and the TorchFold-AbAg model weights are open under the MIT license. The repository's own LICENSE and README at commit " + COMMIT + " say Apache License 2.0, and the gated Hugging Face page forbids redistribution without written permission. The repository's own licence file governs the code; this statement is recorded as a conflict and is not relied on.",
    "Project site, closing line below the citations block",
    sources=[S["site"], S["licence"], S["readme"], S["hf"]],
    rationale="Three official sources disagree about the licence of the same artifacts. The conflict is recorded rather than resolved, and the project-site source carries a matching evidence concern scoped to this claim.",
    limitations=["Withheld from comparison by the evidence concern on the project-site source."],
    review_obj=review(WEB_REVIEW, "Read the site's closing licence line and compared it with the repository LICENSE, the README and the Hugging Face gate text.", locator_url="https://torchx-cpl.github.io/", sha=SITE_SHA),
    status="disputed",
)

claim(
    "claim-checkpoint-access-terms",
    "Gated checkpoint access terms",
    PREFIX + "config-torchfold-abag-checkpoint",
    "access_terms",
    "The Hugging Face release is gated with manual review. Its gate reads: by requesting access you agree to use the TorchFold-AbAg training data only for the stated purpose, and redistribution, rehosting, selling or sharing the files without written permission from Changping Laboratory is not allowed. The page's licence tag reads mit, which does not match that condition. Access was not requested, so the files were not seen.",
    "Hugging Face dataset page: licence tag, gate text 'Request access to TorchFold-AbAg training data' and dataset card",
    sources=[S["hf"], S["readme"]],
    rationale="Separates the checkpoint and data terms from the Apache-2.0 code licence. Commercial usability is not established by either.",
    review_obj=review(WEB_REVIEW, "Read the dataset page as served without signing in.", locator_url="https://huggingface.co/datasets/TorchX-CPL/TorchFold", sha=HF_SHA),
)

claim(
    "claim-released-artifact-mismatch",
    "What the gated release holds is stated inconsistently",
    PREFIX + "method-torchfold",
    "released_artifacts",
    "The repository README says TorchFold trained weights (.pt) and the public TorchFold training data are released on the Hugging Face dataset. The dataset page, retrieved without signing in, describes TorchFold-AbAg training data as data.tar.gz of processed training examples, 1.13 GB in total, and does not itself list trained weights; its file list is not visible without approved access.",
    "README section 'Checkpoints'; Hugging Face dataset page, card and gate text",
    sources=[S["readme"], S["hf"]],
    rationale="Recorded as a gap: whether the weights are obtainable at that URL could not be confirmed without requesting access.",
    review_obj=review(WEB_REVIEW, "Compared the README's statement with the dataset page as served.", locator_url="https://huggingface.co/datasets/TorchX-CPL/TorchFold", sha=HF_SHA),
)

claim(
    "claim-af3-parameter-terms",
    "The AlphaFold 3 parameters come under DeepMind's own terms",
    PREFIX + "config-torchfold-af3-parameters",
    "upstream_parameter_terms",
    "The official AlphaFold 3 parameters are applied for from DeepMind and are not distributed with the repository. DeepMind's terms for those parameters were not retrieved for this batch, so whether this configuration can be used commercially is not established here.",
    "README section 'Checkpoints' ('official AlphaFold 3 parameters directory (apply from DeepMind)'); torchcraft_gpu/README.md section 'Design'",
    sources=[S["readme"], S["design"]],
    rationale="The code licence does not reach the upstream weights. Recorded as a gap rather than a statement about commercial use.",
    review_obj=WEB_README_REVIEW,
)

claim(
    "claim-torchfold-readme-benchmark",
    "Developer-reported TorchFold benchmark figure in the README",
    PREFIX + "config-torchfold-abag-checkpoint",
    "developer_reported_benchmark",
    "The repository README states that TorchFold reaches 70.1% ranked success on FoldBench-AB, compared with AlphaFold3, Protenix-v2 and OpenDDE, with MSAs for every method generated by the official AF3 Jackhmmer search, and that two-round distillation expanded unique antibody-antigen examples from 5.0k to 24.5k.",
    "README sections 'TorchFold overview' and 'TorchFold Benchmark'",
    sources=[S["readme"], S["site"]],
    rationale="Recorded as a developer-reported claim, not as a result: it belongs to the separate TorchFold report, which could not be retrieved, and to the antibody-distilled checkpoint, which no TorchCraft result used.",
    limitations=[
        "Not a result record: the TorchFold report behind it could not be retrieved, so no benchmark, protocol or dataset was registered for it.",
        "Belongs to the antibody-distilled checkpoint configuration, not to the AlphaFold 3 parameter configuration the TorchCraft results used.",
    ],
    review_obj=WEB_README_REVIEW,
)

claim(
    "claim-suite-modules",
    "The four TorchX modules",
    PREFIX + "method-torchx",
    "suite_modules",
    "TorchX has four modules: TorchFold for structure prediction, TorchScore for score-only evaluation of supplied coordinates, TorchCraft for binder design, and TorchFold Train for training and fine-tuning. The repository is split into a GPU tree on main and an Ascend NPU branch, which the README says share the same scientific modules.",
    "README sections 'TorchX', 'Repository layout' and 'Other branches'",
    sources=[S["readme"], S["site"]],
    review_obj=WEB_README_REVIEW,
)

claim(
    "claim-composition-regulariser",
    "The amino-acid composition regulariser and its reference",
    PREFIX + "config-minibinder-raw",
    "sequence_regulariser",
    "An amino-acid composition regulariser matches the average residue distribution of designed minibinders to a reference estimated from ProteinMPNN-redesigned samples; its weight is 5 in Supplementary Table S1. The preprint reports that it changed sequence composition, raised ESMFold confidence across the 12-target benchmark and, in two PDGFRb campaigns, that the regularised round expressed better than the preceding unregularised round. Those comparisons are shown only as figures without printed numbers.",
    "Section 2.2; Supplementary Table S1 row 'Minibinder'; Supplementary Figure S1",
    rationale="Records the regulariser as part of the evaluated configuration and marks the supporting comparisons as figure-only.",
    limitations=["The expression comparison is between successive campaign rounds, not a matched experiment; the preprint says matched comparisons are still needed."],
)

claim(
    "claim-runtime-measurement-setup",
    "How the runtime figures were measured",
    PREFIX + "benchmark-runtime",
    "measurement_setup",
    "Runtime is reported in minutes per design, obtained by dividing the total wall-clock time of a batch-size-2 run by 2, on an Ascend 910B with 64 GB with and without fused attention and on an A100 with 80 GB with and without cuequivariance kernels. Batch size 2 is the recommended setting and GPU timings are the mean of three independent runs.",
    "Supplementary Table S9 caption",
    sources=[S["paper"], S["site"]],
    review_obj=review(PARSE_REVIEW, PARSE_NOTE),
)

claim(
    "claim-runtime-oom-exception",
    "The 500-residue NPU run without fused attention used batch size 1",
    PREFIX + "config-runtime-npu-no-fused-attention",
    "measurement_exception",
    "The 500-residue timing for the Ascend 910B without fused attention was measured at batch size 1 because batch size 2 exceeded memory. Every other cell of the table is a batch-size-2 run divided by 2.",
    "Supplementary Table S9 footnote: '* Batch size 1; batch size 2 exceeded memory (OOM).'",
    sources=[S["paper"], S["site"]],
    review_obj=review(PARSE_REVIEW, PARSE_NOTE),
)

claim(
    "claim-expression-threshold",
    "The expression proxy threshold and its two printed values",
    PREFIX + "config-esm2-150m-expression-classifier",
    "operating_threshold",
    "Designs with a total expression of at least 0.08 mg were classified as high-expression cases, ESM2-150M perplexity was swept as a one-dimensional classifier and the operating threshold chosen by maximising the Matthews correlation coefficient. The threshold is printed as 6.31 in Appendix A.4.3.2 and as 6.309 in the Supplementary Figure S4b caption.",
    "Appendix A.4.3.2; Supplementary Figure S4 caption, panel b",
    rationale="Both printed values are recorded because the VHH benchmark criterion quotes the rounded one; the difference is rounding, not a conflict of substance, and the reviewer should rule on which to carry.",
)

FIGURE_ONLY = [
    ("claim-minibinder-benchmark-figure-only", PREFIX + "benchmark-minibinder-12-target",
     "Figure 2f compares computational pass rates for TorchCraft, BoltzGen and RFdiffusion across 12 protein targets, aggregated over binder lengths of 75, 120, 160 and 200 residues, with an optional ProteinMPNN-polished TorchCraft setting shown separately. 100 designs were generated per method, per length, per target. The figure prints no numbers, so no value was extracted.",
     "Figure 2f and its caption; Appendix A.4.3.1"),
    ("claim-vhh-benchmark-figure-only", PREFIX + "benchmark-vhh-15-target",
     "Figure 3i compares computational pass rates for TorchCraft with RFantibody, BoltzGen and Germinal across 15 targets and five VHH frameworks under a joint TorchScore-confidence and ESM2-perplexity criterion, with an optional AbMPNN-polished setting shown separately and a framework-stratified version in Supplementary Figure S5. 100 designs were generated per method, per framework, per target. Neither figure prints numbers, so no value was extracted.",
     "Figure 3i and its caption; Supplementary Figure S5; Appendix A.4.3.2"),
    ("claim-cyclic-benchmark-figure-only", PREFIX + "benchmark-cyclic-peptide-8-target",
     "Figure 4c compares computational pass rates for BoltzGen, RFpeptides and TorchCraft across eight target systems in head-to-tail and disulfide-linked settings, with optional ProteinMPNN polishing shown separately; Supplementary Figure S6 shows the cyclisation outcome fractions and Supplementary Figure S7 the Rosetta interface scores. 100 designs were generated per method per target in the head-to-tail setting. None of these figures prints numbers, so no value was extracted.",
     "Figure 4c and its caption; Supplementary Figures S6 and S7; Appendix A.4.3.3"),
    ("claim-ligand-pocket-benchmark-figure-only", PREFIX + "benchmark-ligand-pocket-10-ligand",
     "Figures 5c and 5d show AutoDock Vina docking scores and Boltz-2 affinity predictions for designed pockets across the 10-ligand panel, comparing BoltzDesign with TorchCraft and a separately analysed LigandMPNN-redesigned TorchCraft variant; Supplementary Figure S9 shows TorchScore pass rates for TorchCraft. 500 designs of 160 residues were generated per method per ligand. None of these figures prints numbers, so no value was extracted.",
     "Figures 5c and 5d and their captions; Supplementary Figures S8 and S9; Appendix A.4.3.4"),
]
for rid, subject, value, locator in FIGURE_ONLY:
    claim(
        rid,
        "Benchmark reported only as a figure",
        subject,
        "reported_values",
        value,
        locator,
        rationale="Recorded so that the benchmark is registered with its panel, comparators and design counts while the absence of printed values stays explicit. Reading values off the bars was not attempted.",
        limitations=["No result record rests on this benchmark; the gap is recorded in notes.md and the ledger entry."],
    )

claim(
    "claim-design-schedule",
    "The shared four-stage optimisation schedule",
    PREFIX + "pipeline-torchcraft",
    "optimisation_schedule",
    "The sequence logits pass through up to four stages: an optional soft warm-up using softmax probabilities, a linearly scheduled interpolation from raw logits to probabilities, temperature annealing from an initial to a minimum temperature, and straight-through hard optimisation on a one-hot representation with gradients taken through the low-temperature softmax. Minibinder and VHH runs used temperature annealing followed by straight-through optimisation; cyclic-peptide runs used all four stages; small-molecule runs began with a ligand-free warm-up before the ligand was added and the interface weight was raised.",
    "Appendix A.1.2 and A.1.3; Algorithm 1; Supplementary Table S1",
)

claim(
    "claim-implementation-optimisations",
    "Implementation changes that make repeated predictor evaluation affordable",
    PREFIX + "pipeline-torchcraft",
    "implementation_optimisations",
    "Repeated predictor evaluation is supported by multithreaded conformer generation with per-thread random state, reentrant gradient checkpointing for the design graph and non-reentrant checkpointing for the template and MSA modules, caching of trunk conditioning tensors across denoising steps within one prediction, a modified NPU fusion-attention operator, and optional cuequivariance kernels on GPU.",
    "Appendix A.3.1 to A.3.5; Supplementary Table S9",
    sources=[S["paper"], S["design"]],
)

claim(
    "claim-no-reproduction",
    "Nothing in this batch was reproduced",
    PREFIX + "pipeline-torchcraft",
    "reproduction_status",
    "No design run, score, docking calculation or binding measurement was reproduced for this batch. Every value is a transcription from the pinned preprint, checked against the sources named on each record.",
    "Whole batch; see notes.md",
    rationale="Required by docs/collection.md: source-checked is not reproduced.",
)

# --------------------------------------------------------------------------- write
ids = [r["id"] for r in records]
duplicates = sorted({i for i in ids if ids.count(i) > 1})
if duplicates:
    sys.exit("duplicate record ids: " + ", ".join(duplicates))

known = set(ids)
external = {AF3, PROTEINMPNN, LIGANDMPNN, ESM2}
for r in records:
    for link in r["links"]:
        target = link["target_id"]
        if target not in known and target not in external:
            sys.exit("link to unknown record " + target + " from " + r["id"])

records.sort(key=lambda r: r["id"])
out = HERE / "batch.jsonl"
with out.open("w", encoding="utf-8") as fh:
    for r in records:
        fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

counts = {}
for r in records:
    counts[r["kind"]] = counts.get(r["kind"], 0) + 1
print(json.dumps({"records": len(records), "by_kind": counts}, indent=1))
