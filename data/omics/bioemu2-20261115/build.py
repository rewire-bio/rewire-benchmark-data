"""Build data/omics/bioemu2-20261115/batch.jsonl from the pinned BioEmu-2 sources.

Every value comes from one of the thirteen archived artifacts under artifacts/. The script
checks each artifact's SHA-256 before using it, takes the two model-card tables from
extract/model-card-tables.json (written by extract/parse_model_card.py), and writes the
records sorted by ID.

Run from the repository root:
    python3 -I data/omics/bioemu2-20261115/extract/parse_model_card.py
    python3 -I data/omics/bioemu2-20261115/build.py
"""

import gzip
import hashlib
import json
import pathlib

BATCH = pathlib.Path(__file__).resolve().parent
OUT = BATCH / "batch.jsonl"
PREFIX = "bioemu2-20261115-"
COMMIT = "6d1ca744fa8ed285edafae7b98da65205bf00fd3"
HF_REV = "dd4b0c1b69984b68edcb6200a544213be4d75242"
REPO_BLOB = f"https://github.com/microsoft/bioemu2/blob/{COMMIT}/"
REPO_RAW = f"https://raw.githubusercontent.com/microsoft/bioemu2/{COMMIT}/"
HF_RAW = f"https://huggingface.co/microsoft/bioemu2/raw/{HF_REV}/"
HF_BLOB = f"https://huggingface.co/microsoft/bioemu2/blob/{HF_REV}/"
DATE = "2026-11-15"

REVIEWER = ["claude"]
REVIEWER_NOTE = (
    "Claude (Opus 5) extraction agent. Extraction only: no independent review is claimed, "
    "and a different agent reviews this batch."
)
TRANSCRIBE_NOTE = (
    "Extraction: the archived artifact was decompressed, its SHA-256 checked against the source "
    "record, and the quoted text transcribed by hand from the named section. No numeric "
    "evaluation value appears in any pinned artifact, so no result record was written."
)
TABLE_NOTE = (
    "Extraction: extract/parse_model_card.py decompresses the archived MODEL_CARD.md, checks its "
    "SHA-256, parses the Model summary and Training data tables and asserts every row label; "
    "build.py reads the parsed cells from extract/model-card-tables.json."
)

# key -> (id suffix, archived file, expected sha256, retrieved_at, url, retrieval url, locator,
#          name, description, version, extra attributes)
SOURCES = {
    "mc": {
        "suffix": "source-model-card",
        "file": "repo_MODEL_CARD.md.gz",
        "sha256": "5f62c8cee0e5c364bdbbc3a5ae0359acdeca1c6c4e5e5119aad9aae2ce80f451",
        "retrieved_at": "2026-11-15T22:58:53Z",
        "path": "MODEL_CARD.md",
        "name": "BioEmu-2 model card (microsoft/bioemu2 MODEL_CARD.md at 6d1ca74)",
        "description": (
            "The BioEmu-2 model card in the official repository, holding the model summary, "
            "intended and out-of-scope uses, known limitations, evaluation methodology and "
            "training data tables."
        ),
        "limitations": [
            "The Evaluation methodology section describes four evaluation settings but prints no "
            "numeric evaluation value, so no result record rests on this artifact.",
            "The technical requirements section names an 80 GB A100 as the smallest tested device, "
            "while README.md at the same commit reports testing on V100 and T4 GPUs.",
        ],
    },
    "rd": {
        "suffix": "source-readme",
        "file": "repo_README.md.gz",
        "sha256": "3a12433968a44b7f770515d9f22782a318592551bf6bce558796cdb76e97df9a",
        "retrieved_at": "2026-11-15T22:58:53Z",
        "path": "README.md",
        "name": "BioEmu2 repository README (microsoft/bioemu2 at 6d1ca74)",
        "description": (
            "The repository front page, holding the feature list, system requirements, install "
            "paths for each GPU generation, quick-start commands and the licence statement."
        ),
        "limitations": [
            "The system requirements list the GPUs tested but print no memory figure, so the "
            "smallest supported device cannot be stated in gigabytes from this artifact.",
        ],
    },
    "nt": {
        "suffix": "source-notices",
        "file": "repo_NOTICES.md.gz",
        "sha256": "35e81645788cc09b4362ced578dbcaa0fc317ebaa82100de36b964eaff10c699",
        "retrieved_at": "2026-11-15T22:58:54Z",
        "path": "NOTICES.md",
        "name": "BioEmu2 third-party notices (microsoft/bioemu2 at 6d1ca74)",
        "description": (
            "The third-party notices for the BioEmu2 distribution, naming each borrowed component, "
            "the files it appears in and the licence that covers it."
        ),
    },
    "lc": {
        "suffix": "source-licence",
        "file": "repo_LICENSE.gz",
        "sha256": "7df20dcdf9197e9945c14858d41c60f11b52b93e5b69e2b63416b874d598d322",
        "retrieved_at": "2026-11-15T22:58:54Z",
        "path": "LICENSE",
        "name": "BioEmu2 MIT licence file (microsoft/bioemu2 at 6d1ca74)",
        "description": "The MIT licence text that covers the BioEmu2 repository, copyright Microsoft Corporation.",
    },
    "pp": {
        "suffix": "source-pyproject",
        "file": "repo_pyproject.toml.gz",
        "sha256": "c298c884c0fb013d083be4e21bf1349755b0074cce0ed77947eb4a01253a10c3",
        "retrieved_at": "2026-11-15T22:58:54Z",
        "path": "pyproject.toml",
        "name": "bioemu2 package metadata (microsoft/bioemu2 pyproject.toml at 6d1ca74)",
        "description": (
            "The Python packaging metadata for the bioemu2 inference package, holding its version, "
            "supported interpreters, dependency pins and the two mutually exclusive CUDA extras."
        ),
    },
    "ck": {
        "suffix": "source-docs-checkpoints",
        "file": "repo_docs_checkpoints.md.gz",
        "sha256": "f3afdea65d8a678b5f630642a94656087aa225eef7cb3e49b890dc7913fa6ca9",
        "retrieved_at": "2026-11-15T22:58:54Z",
        "path": "docs/checkpoints.md",
        "name": "BioEmu2 checkpoint loading guide (microsoft/bioemu2 docs/checkpoints.md at 6d1ca74)",
        "description": (
            "The guide to loading BioEmu2 weights, which names the default checkpoint, where it is "
            "downloaded from and cached, and the default precision settings."
        ),
    },
    "sp": {
        "suffix": "source-docs-sampling",
        "file": "repo_docs_sampling.md.gz",
        "sha256": "6615a0e57ec25a27c3702bcd96fec448d2103a3e431f91f271a5ba51e211dc28",
        "retrieved_at": "2026-11-15T22:58:55Z",
        "path": "docs/sampling.md",
        "name": "BioEmu2 sampling guide (microsoft/bioemu2 docs/sampling.md at 6d1ca74)",
        "description": (
            "The guide to predicting and sampling structures, which sets out the two tasks the "
            "model was trained for and the settings each sampling mode selects."
        ),
    },
    "cp": {
        "suffix": "source-docs-context-parallel",
        "file": "repo_docs_context-parallel-sampling.md.gz",
        "sha256": "66355a5b609714d3a55a4f933392f84586ee370bed4d9e0707901edf71582a3a",
        "retrieved_at": "2026-11-15T22:58:55Z",
        "path": "docs/context-parallel-sampling.md",
        "name": "BioEmu2 context-parallel sampling guide (microsoft/bioemu2 docs/context-parallel-sampling.md at 6d1ca74)",
        "description": (
            "The guide to splitting one system across several GPUs, which states the GPU-count "
            "requirement and the largest systems the developers embedded on each grid."
        ),
        "limitations": [
            "The two throughput figures are linked images with no printed numbers, so no "
            "throughput value was extracted.",
        ],
    },
    "pr": {
        "suffix": "source-docs-propagation",
        "file": "repo_docs_propagation.md.gz",
        "sha256": "0ba1efa48e03bec2394d79ef164cfbca529022dd1e54169e1250488b49ab557d",
        "retrieved_at": "2026-11-15T22:58:55Z",
        "path": "docs/propagation.md",
        "name": "BioEmu2 propagation guide (microsoft/bioemu2 docs/propagation.md at 6d1ca74)",
        "description": (
            "The guide to propagating a structure to a future time, which states the usable lag "
            "range and what a propagated sample is."
        ),
    },
    "hf": {
        "suffix": "source-hf-model-card",
        "file": "hf_README.md.gz",
        "sha256": "e1077abb34d63b1c2e8cb2d19d530a4e5ad73d6cee634e454ff6c517c7a10a0b",
        "retrieved_at": "2026-11-15T22:58:55Z",
        "hf_path": "README.md",
        "name": "BioEmu-2 model card on Hugging Face (microsoft/bioemu2 README.md at dd4b0c1b)",
        "description": (
            "The model card as published in the Hugging Face weights repository, which carries the "
            "same text as the repository MODEL_CARD.md under a front matter block declaring the "
            "MIT licence."
        ),
    },
    "cf": {
        "suffix": "source-hf-checkpoint-config",
        "file": "hf_config.yaml.gz",
        "sha256": "90326e3b77e524420f5aad68a777355ecbbbe07bc006ddf88f7ee921b0f772e3",
        "retrieved_at": "2026-11-15T22:58:56Z",
        "hf_path": "checkpoints/bioemu2-preview/config.yaml",
        "name": "bioemu2-preview checkpoint configuration (microsoft/bioemu2 at dd4b0c1b)",
        "description": (
            "The Hydra configuration distributed with the bioemu2-preview checkpoint, which names "
            "the score model and its layer widths, conditioning switches and noise schedule."
        ),
    },
    "pt": {
        "suffix": "source-hf-checkpoint-pointer",
        "file": "hf_checkpoint_pointer.txt.gz",
        "sha256": "bdb4054c9f46080e7421b0892b64a03cd3917395666003874943b2a085594bda",
        "retrieved_at": "2026-11-15T22:58:56Z",
        "hf_path": "checkpoints/bioemu2-preview/checkpoint.ckpt",
        "name": "bioemu2-preview checkpoint Git LFS pointer (microsoft/bioemu2 at dd4b0c1b)",
        "description": (
            "The Git LFS pointer served for the bioemu2-preview weights at the pinned revision, "
            "which publishes the SHA-256 and byte size of the checkpoint file."
        ),
        "limitations": [
            "The pointer publishes the digest of the 2,047,661,181 byte checkpoint; those bytes "
            "were not downloaded, so the digest is the publisher's and was not recomputed here.",
        ],
    },
    "ls": {
        "suffix": "source-hf-revision-listing",
        "file": "hf_api_revision.json.gz",
        "sha256": "8b00ad6b3b8f5a411ac5b0b1e31d2d463a2dd02d1219634feb40ff4ce3b4856d",
        "retrieved_at": "2026-11-15T23:02:46Z",
        "api_url": f"https://huggingface.co/api/models/microsoft/bioemu2/revision/{HF_REV}?blobs=true",
        "name": "Hugging Face file listing for microsoft/bioemu2 at dd4b0c1b",
        "description": (
            "The Hugging Face API listing of every file in the weights repository at the pinned "
            "revision, used to establish which checkpoints the revision releases."
        ),
        "limitations": [
            "The response carries counters that change between calls, such as downloads and likes, "
            "so the hash describes this one retrieval rather than an immutable artifact.",
        ],
    },
}

MODEL = PREFIX + "model-bioemu-2"
CFG_CKPT = PREFIX + "config-checkpoint-bioemu2-preview"
CFG_RUNTIME = PREFIX + "config-runtime-package-0-1-0rc0"
CFG_STRUCTURE = PREFIX + "config-mode-structure-prediction"
CFG_EQUILIBRIUM = PREFIX + "config-mode-equilibrium-sampling"
CFG_PROPAGATION = PREFIX + "config-mode-propagation"

FACETS = {
    "areas": ["protein-structure", "proteins-complexes", "molecular-interactions"],
    "contexts": ["research"],
    "method_types": ["foundation_model"],
}


def artifact_text(key: str) -> str:
    spec = SOURCES[key]
    raw = gzip.open(BATCH / "artifacts" / spec["file"], "rb").read()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == spec["sha256"], f"{spec['file']}: {digest} != {spec['sha256']}"
    return raw.decode("utf-8")


def source_url(spec: dict) -> str:
    if "path" in spec:
        return REPO_BLOB + spec["path"]
    if "hf_path" in spec:
        return HF_BLOB + spec["hf_path"]
    return spec["api_url"]


def retrieval_url(spec: dict) -> str:
    if "path" in spec:
        return REPO_RAW + spec["path"]
    if "hf_path" in spec:
        return HF_RAW + spec["hf_path"]
    return spec["api_url"]


def review(key: str, note: str, method_note: str = TRANSCRIBE_NOTE, table: bool = False) -> dict:
    spec = SOURCES[key]
    method = ["transcription", "source-hash-verification"]
    if table:
        method = ["deterministic-table-parse", "source-hash-verification"]
    return {
        "method": method,
        "method_note": method_note,
        "reviewer": REVIEWER,
        "reviewer_note": REVIEWER_NOTE,
        "date": DATE,
        "artifact_sha256": spec["sha256"],
        "retrieval_url": retrieval_url(spec),
        "note": note,
    }


records: list[dict] = []


def add(record: dict) -> None:
    records.append(record)


# ---------------------------------------------------------------- sources

for key, spec in SOURCES.items():
    artifact_text(key)  # checks the hash
    if "path" in spec:
        version = f"Repository commit {COMMIT}"
        media_type = "text/plain" if spec["path"] == "LICENSE" else (
            "text/markdown" if spec["path"].endswith(".md") else "text/plain"
        )
    elif "hf_path" in spec:
        version = f"Hugging Face revision {HF_REV}"
        media_type = "text/markdown" if spec["hf_path"].endswith(".md") else "text/plain"
    else:
        version = f"API response for revision {HF_REV}, as served on {DATE}"
        media_type = "application/json"
    attributes = {
        "url": source_url(spec),
        "artifact_url": retrieval_url(spec),
        "retrieval_url": retrieval_url(spec),
        "version": version,
        "retrieved_at": spec["retrieved_at"],
        "artifact_sha256": spec["sha256"],
        "media_type": media_type,
        "publication_status": "official_project_source",
        **(
            {}
            if spec["suffix"] == "source-hf-revision-listing"
            else {
                "licence": (
                    "MIT (repository LICENSE at commit 6d1ca74; NOTICES.md lists third-party "
                    "components under other licences, including two files under LGPL-3.0)"
                )
            }
        ),
        "retrieval_method": "HTTP GET with curl; the bytes retrieved are archived gzipped in artifacts/",
        "hash_scope": f"SHA-256 of the retrieved bytes of artifacts/{spec['file'][:-3]}",
        "review": review(
            key,
            "Retrieved once on 2026-11-15; the archived gzip decompresses to bytes with this SHA-256.",
            method_note=(
                "Extraction: retrieved over HTTP, hashed, and archived gzipped under artifacts/. "
                "build.py rechecks the hash of the archived copy before using the text."
            ),
        ),
        "missing_metadata": {
            "doi": {
                "reason": "inapplicable",
                "note": "A repository file and a weights-repository file; neither carries a DOI.",
            },
            **(
                {
                    "licence": {
                        "reason": "inapplicable",
                        "note": (
                            "A Hugging Face Hub API metadata response, not a licensed artifact of "
                            "the repository; the card metadata it reports says license: mit."
                        ),
                    }
                }
                if spec["suffix"] == "source-hf-revision-listing"
                else {}
            ),
        },
    }
    if "limitations" in spec:
        attributes["limitations"] = spec["limitations"]
    source = {
        "id": PREFIX + spec["suffix"],
        "kind": "source",
        "name": spec["name"],
        "description": spec["description"],
        "status": "source_checked",
        "facets": {"areas": FACETS["areas"], "contexts": ["research"]},
        "source_ids": [],
        "links": [],
        "attributes": attributes,
    }
    if spec["suffix"] != "source-model-card":
        source["links"] = [{"relation": "companion_of", "target_id": PREFIX + "source-model-card"}]
        source["source_ids"] = [PREFIX + "source-model-card"]
    add(source)

S = {key: PREFIX + spec["suffix"] for key, spec in SOURCES.items()}

# ---------------------------------------------------------------- model

tables = json.loads((BATCH / "extract" / "model-card-tables.json").read_text(encoding="utf-8"))
summary = tables["model_summary"]
training = tables["training_data"]

add(
    {
        "id": MODEL,
        "kind": "model",
        "name": "BioEmu-2",
        "description": (
            "Diffusion model from Microsoft Research that samples ensembles of all-atom 3D "
            "structures for a supplied biomolecular system, including multi-chain complexes, "
            "nucleic acids and supplied ligands, optionally conditioned on an alignment, contacts "
            "or a method label."
        ),
        "status": "source_checked",
        "facets": dict(FACETS, tasks=[
            "structure prediction",
            "equilibrium conformational ensemble sampling",
            "time-lagged structure propagation",
        ]),
        "source_ids": [S["mc"], S["rd"], S["hf"]],
        "links": [],
        "attributes": {
            "entity_level": "family",
            "version": "October 2026 release; one released checkpoint, bioemu2-preview",
            "reported_name": "BioEmu-2",
            "identity_scope": (
                "The model as published in October 2026: the inference code at commit 6d1ca74 and "
                "the single checkpoint bioemu2-preview at Hugging Face revision dd4b0c1b. The "
                "model card prints no version number for the model itself, so the record stays at "
                "family level and the checkpoint is a separate configuration record."
            ),
            "access": (
                "Public. Inference code at https://github.com/microsoft/bioemu2 and weights at "
                "https://huggingface.co/microsoft/bioemu2, neither gated. The model card says the "
                "model is released for research purposes and does not recommend commercial or "
                "real-world use without further testing and development."
            ),
            "licence": (
                "MIT, printed in the model card License row, in the repository LICENSE and in the "
                "Hugging Face card metadata. NOTICES.md separately covers borrowed components: "
                "two distributed files are under LGPL-3.0, and other portions come from Boltz, "
                "PyTorch3D, torch_scatter, NVIDIA Fold-CP, MDTraj, OpenMM and geostd."
            ),
            "training_data": (
                "Experimental structures from the PDB in the Boltz-1 preprocessing, seven "
                "Microsoft-generated molecular dynamics trajectory sets (MSR_cath2, MSR_cath3, "
                "MSR_cath_dimers, MSR_heterodimers, MSR_pdbbind2020, MSR_pdbbind2020_apo_free, "
                "MSR_megasim_merge) and AI-predicted structures from AFDB monomer, AFDB homodimer "
                "and heterodimer multiconformation sets and Teddymer. Per-set counts are in the "
                "model card training data table and in this batch's training_data claims."
            ),
            "provenance_note": (
                "Registered from the pinned repository commit, its model card and the pinned "
                "Hugging Face revision. No paper or technical report was found for BioEmu-2 by "
                "2026-11-15, and the pinned sources name no predecessor model, so no family or "
                "variant link is recorded."
            ),
            "source_locator": "MODEL_CARD.md, Model summary table and opening paragraph",
            "review": review(
                "mc",
                "Identity, inputs, outputs and access read from the Model summary table and the "
                "opening paragraph; the licence statement cross-read against LICENSE and NOTICES.md.",
            ),
            "missing_metadata": {
                "checkpoint_revision": {
                    "reason": "unreported",
                    "note": (
                        "The model card says the same checkpoint was used for every evaluation but "
                        "does not name it. Only docs/checkpoints.md names bioemu2-preview, as the "
                        "default download, so the evaluated checkpoint is not assigned here."
                    ),
                }
            },
        },
    }
)

# ---------------------------------------------------------------- configurations

add(
    {
        "id": CFG_CKPT,
        "kind": "configuration",
        "name": "bioemu2-preview checkpoint",
        "description": (
            "The single BioEmu-2 checkpoint published at Hugging Face revision dd4b0c1b, a "
            "BioMoaC score model with 48 pair-mixer blocks and contact and method conditioning "
            "enabled, loaded by default at bf16-mixed trunk precision."
        ),
        "status": "source_checked",
        "facets": FACETS,
        "source_ids": [S["ls"], S["pt"], S["cf"], S["ck"], S["mc"]],
        "links": [{"relation": "configuration_of", "target_id": MODEL}],
        "attributes": {
            "configuration_type": "reported_configuration",
            "version": f"bioemu2-preview at Hugging Face revision {HF_REV}",
            "checkpoint": "bioemu2-preview",
            "checkpoint_revision": HF_REV,
            "checkpoint_sha256": "3b4ba9236b7b458f47b40b694847b6bb4110c744becd6d2c53de7b1d04c07a81",
            "parameters": "Approximately 500M parameters, as printed in the model card Parameters row",
            "reported_name": "bioemu2-preview",
            "configuration": {
                "score_model": "bioemu2.shortcuts.BioMoaCModel",
                "sequence_embedder": "bioemu2.shortcuts.PairMixerSequenceEmbedder",
                "token_s": 384,
                "token_z": 256,
                "msa_s": 128,
                "msa_blocks": 4,
                "pairmixer_num_blocks": 48,
                "diffusion_transformer_depth": 16,
                "token_attention_heads": 16,
                "atom_s": 128,
                "atom_z": 16,
                "use_contact_conditioning": True,
                "use_method_conditioning": True,
                "use_dynamics_conditioning": True,
                "edm_schedule": {"sigma_min": 0.0004, "sigma_max": 160.0, "sigma_data": 16.0},
                "default_precision": "bf16-mixed trunk embedding, high float32 matmul precision",
            },
            "access_reuse": (
                "Downloaded automatically from the microsoft/bioemu2 Hugging Face repository into "
                "the Hugging Face cache, or loaded from disk with checkpoint_path. Not gated."
            ),
            "limitations": [
                "The model card rules out reading sampling frequency as a calibrated Boltzmann "
                "probability or a quantitative free energy.",
                "The model card says the model may struggle to produce physically plausible "
                "structures for complexes over 10k tokens.",
                "The 2,047,661,181 byte checkpoint was not downloaded; the SHA-256 recorded here "
                "is the digest published in the Git LFS pointer at the pinned revision.",
            ],
            "provenance_note": (
                "The only checkpoint directory in the pinned Hugging Face revision, and the "
                "checkpoint docs/checkpoints.md names as the default download. The model card does "
                "not say that this is the checkpoint its evaluations used."
            ),
            "source_locator": (
                "Hugging Face API listing for revision dd4b0c1b, siblings entries under "
                "checkpoints/bioemu2-preview/; checkpoints/bioemu2-preview/config.yaml; "
                "docs/checkpoints.md, opening paragraph"
            ),
            "review": review(
                "cf",
                "Layer widths, conditioning switches and the noise schedule transcribed from the "
                "checkpoint config.yaml; the digest and byte size from the Git LFS pointer; the "
                "default precision from docs/checkpoints.md.",
            ),
            "missing_metadata": {
                "weights_sha256": {
                    "reason": "unextracted",
                    "note": (
                        "The checkpoint bytes were not downloaded, so no digest was computed here; "
                        "checkpoint_sha256 holds the digest the Git LFS pointer publishes."
                    ),
                },
                "fine_tuning": {
                    "reason": "unreported",
                    "note": "The pinned sources describe one trained checkpoint and no fine-tuning stage.",
                },
            },
        },
    }
)

add(
    {
        "id": CFG_RUNTIME,
        "kind": "configuration",
        "name": "bioemu2 inference package 0.1.0rc0",
        "description": (
            "The bioemu2 Python inference package at version 0.1.0rc0, which runs BioEmu-2 on "
            "Linux with an NVIDIA GPU through either the CUDA 13 extra for compute capability 7.5 "
            "and newer or the CUDA 12 extra for compute capability 7.0."
        ),
        "status": "source_checked",
        "facets": FACETS,
        "source_ids": [S["pp"], S["rd"], S["cp"], S["mc"]],
        "links": [{"relation": "configuration_of", "target_id": MODEL}],
        "attributes": {
            "configuration_type": "reported_configuration",
            "version": f"bioemu2 0.1.0rc0 at repository commit {COMMIT}",
            "code_commit": COMMIT,
            "software_commit": COMMIT,
            "reported_name": "bioemu2",
            "packages": {
                "distribution": "bioemu2 0.1.0rc0",
                "requires_python": ">=3.12, with the Linux classifiers naming 3.12, 3.13 and 3.14",
                "core_pins": ["torch>=2.11,<2.14", "numpy<2.5", "triton on Linux"],
                "extra_cuda": [
                    "cuequivariance==0.11.1",
                    "cuequivariance-torch==0.11.1",
                    "cuequivariance-ops-torch-cu13==0.11.1",
                    "cuequivariance-ops-cu13==0.11.1",
                ],
                "extra_cuda12": [
                    "torch==2.13.0+cu126 from the PyTorch cu126 index",
                    "cuequivariance==0.11.1",
                    "cuequivariance-torch==0.11.1",
                    "cuequivariance-ops-torch-cu12==0.11.1",
                    "cuequivariance-ops-cu12==0.11.1",
                ],
                "extras_conflict": "The cuda and cuda12 extras are declared mutually exclusive",
                "entry_point": "bioemu2 command line interface",
            },
            "environment": {
                "operating_system": "Linux only; macOS and Windows are not supported",
                "python": "3.12, 3.13 or 3.14; benchmark metrics were evaluated with 3.12 only",
                "msa_service": "ColabFold cache or the public ColabFold server when no MSA is supplied",
            },
            "hardware": {
                "requirement": "An NVIDIA GPU; compute capability 7.0 is the oldest supported",
                "cuda_extra": "Compute capability 7.5 or newer, such as T4, A100, RTX A6000, L40S, H100 and B200",
                "cuda12_extra": "Compute capability 7.0 (Volta, such as V100)",
                "tested_gpus": "V100 (7.0), T4 (7.5, with the CUDA 12 installation), A100 and RTX A6000 (8.0 and 8.6), B200 (10.0); other eligible GPUs not verified end to end",
                "model_card_statement": "The model card says an 80 GB A100 was the smallest tested device",
                "context_parallel": "A square number of NVIDIA GPUs, at least four, arranged as an n x n grid",
                "largest_systems_embedded": "On 192 GB B200 GPUs at MSA depth 4,092: 3,072 tokens on one GPU, 10,240 tokens on a 2x2 grid, 16,384 tokens on a 4x4 grid",
            },
            "accelerator_details": (
                "The minimum device is configuration specific and the two pinned artifacts do not "
                "agree on it. README.md at this commit supports compute capability 7.0 through the "
                "cuda12 extra and reports testing on V100 and T4 GPUs, while the model card at the "
                "same commit names an 80 GB A100 as the smallest tested device. No memory figure is "
                "printed for any system size, and the README ties the evaluated benchmark metrics "
                "to Python 3.12 rather than to a GPU, so neither artifact supports a single minimum."
            ),
            "access_reuse": (
                "Installed from the repository with pip, choosing the cuda or cuda12 extra for the "
                "GPU generation. MIT licensed; NOTICES.md lists the third-party components."
            ),
            "limitations": [
                "The model card and the README at the same commit disagree about the smallest "
                "tested GPU, so no minimum device is stated on the model record.",
                "Context parallelism has not been tested on older GPUs such as the V100.",
                "The context-parallel throughput figures are images with no printed numbers.",
            ],
            "provenance_note": (
                "The runtime package and its two install paths, taken from pyproject.toml and the "
                "README at the pinned commit. These are install configurations of one package, not "
                "separate models."
            ),
            "source_locator": (
                "pyproject.toml, [project] and [project.optional-dependencies]; README.md, "
                "System requirements and Installation; docs/context-parallel-sampling.md, "
                "System requirements and Choose the number of GPUs"
            ),
            "review": review(
                "pp",
                "Package version, interpreter range, dependency pins and both extras transcribed "
                "from pyproject.toml; GPU and operating system requirements from README.md; the "
                "GPU-count requirement and the largest embedded systems from "
                "docs/context-parallel-sampling.md.",
            ),
            "missing_metadata": {
                "peak_memory": {
                    "reason": "unreported",
                    "note": "No GPU memory figure is printed for any system size in the pinned artifacts.",
                },
                "runtime": {
                    "reason": "unreported",
                    "note": (
                        "Throughput appears only in two linked images with no printed numbers, so "
                        "no runtime figure was extracted."
                    ),
                },
            },
        },
    }
)

add(
    {
        "id": CFG_STRUCTURE,
        "kind": "configuration",
        "name": "BioEmu-2 structure-prediction mode",
        "description": (
            "BioEmu-2 run in structure mode, the predict-structure command, which samples with "
            "heuristic sharpening at step scale 1.5 to return an accurate individual folded structure."
        ),
        "status": "source_checked",
        "facets": FACETS,
        "source_ids": [S["sp"], S["rd"]],
        "links": [{"relation": "configuration_of", "target_id": MODEL}],
        "attributes": {
            "configuration_type": "reported_configuration",
            "version": f"docs/sampling.md at commit {COMMIT}",
            "checkpoint": "bioemu2-preview",
            "reported_name": "predict-structure",
            "hyperparameters": "Heuristic sharpening with step_scale=1.5, selected automatically for this mode",
            "task": "Structure prediction: an accurate individual folded structure",
            "provenance_note": (
                "One of the two tasks docs/sampling.md says the model was trained for. Recorded as "
                "a configuration of the model because the mode selects different sampling settings."
            ),
            "source_locator": "docs/sampling.md, Choose a sampling mode table, row bioemu2 predict-structure",
            "review": review(
                "sp",
                "Mode name, session mode and the sharpening and step scale transcribed from the "
                "two-row sampling mode table.",
                table=False,
            ),
            "missing_metadata": {
                "samples": {
                    "reason": "inapplicable",
                    "note": "The sample count is a user argument, not a property of the mode.",
                }
            },
        },
    }
)

add(
    {
        "id": CFG_EQUILIBRIUM,
        "kind": "configuration",
        "name": "BioEmu-2 equilibrium-sampling mode",
        "description": (
            "BioEmu-2 run in equilibrium mode, the sample-equilibrium command, which samples at "
            "step scale 1.0 without sharpening to return independent conformations from the "
            "modelled equilibrium ensemble."
        ),
        "status": "source_checked",
        "facets": FACETS,
        "source_ids": [S["sp"], S["mc"]],
        "links": [{"relation": "configuration_of", "target_id": MODEL}],
        "attributes": {
            "configuration_type": "reported_configuration",
            "version": f"docs/sampling.md at commit {COMMIT}",
            "checkpoint": "bioemu2-preview",
            "reported_name": "sample-equilibrium",
            "hyperparameters": "step_scale=1.0 without sharpening, selected automatically for this mode",
            "task": "Equilibrium sampling: a range of conformations from the modelled equilibrium ensemble",
            "limitations": [
                "The model card rules out reading sampling frequency as a calibrated Boltzmann "
                "probability or a quantitative free energy, so the frequency of a state in these "
                "samples does not give its population or a free energy difference.",
                "The returned frames are independent samples, not a time series.",
            ],
            "provenance_note": (
                "The second of the two tasks docs/sampling.md says the model was trained for. "
                "Recorded as a configuration of the model because the mode selects different "
                "sampling settings."
            ),
            "source_locator": "docs/sampling.md, Choose a sampling mode table, row bioemu2 sample-equilibrium",
            "review": review(
                "sp",
                "Mode name, session mode and step scale transcribed from the two-row sampling mode "
                "table; the calibration limitation carried from the model card Known limitations.",
            ),
            "missing_metadata": {
                "samples": {
                    "reason": "inapplicable",
                    "note": "The sample count is a user argument, not a property of the mode.",
                }
            },
        },
    }
)

add(
    {
        "id": CFG_PROPAGATION,
        "kind": "configuration",
        "name": "BioEmu-2 propagation mode",
        "description": (
            "BioEmu-2 used to propagate a starting structure to a future time with implicit "
            "transfer operator models, sampling endpoints at lags of 1 ns to 1000 ns."
        ),
        "status": "source_checked",
        "facets": FACETS,
        "source_ids": [S["pr"], S["rd"]],
        "links": [{"relation": "configuration_of", "target_id": MODEL}],
        "attributes": {
            "configuration_type": "reported_configuration",
            "version": f"docs/propagation.md at commit {COMMIT}",
            "checkpoint": "bioemu2-preview",
            "reported_name": "propagate",
            "hyperparameters": "lag_time_ns between 1 and 1000, the range the model mostly saw during training",
            "task": "Time-lagged propagation of a structure to a future time",
            "limitations": [
                "Each result is an endpoint at the requested lag, not an intermediate frame of a "
                "trajectory.",
                "Beyond a few milliseconds the documentation directs the user to equilibrium "
                "sampling instead.",
            ],
            "provenance_note": (
                "The third documented operation of the released model, listed in the README key "
                "features as time-lagged trajectory generation with implicit transfer operator "
                "models."
            ),
            "source_locator": "docs/propagation.md, opening paragraphs; README.md, key features list",
            "review": review(
                "pr",
                "Lag range, the endpoint definition and the guidance beyond a few milliseconds "
                "transcribed from the opening paragraphs.",
            ),
            "missing_metadata": {
                "samples": {
                    "reason": "inapplicable",
                    "note": "The number of endpoints is a user argument, not a property of the mode.",
                }
            },
        },
    }
)

# ---------------------------------------------------------------- claims

CLAIM_DESCRIPTION = "Descriptive fact transcribed from the pinned source with its own locator."


def claim(
    slug: str,
    field: str,
    value: str,
    source_key: str,
    locator: str,
    name: str,
    note: str,
    subject: str = MODEL,
    table: bool = False,
    rationale: str | None = None,
    limitations: list[str] | None = None,
    extra_sources: list[str] | None = None,
) -> None:
    attributes = {
        "field": field,
        "value": value,
        "source_locator": locator,
        "review": review(
            source_key,
            note,
            method_note=TABLE_NOTE if table else TRANSCRIBE_NOTE,
            table=table,
        ),
    }
    if rationale:
        attributes["rationale"] = rationale
    if limitations:
        attributes["limitations"] = limitations
    add(
        {
            "id": PREFIX + "claim-" + slug,
            "kind": "claim",
            "name": name,
            "description": CLAIM_DESCRIPTION,
            "status": "source_checked",
            "facets": {},
            "source_ids": [S[source_key]] + (extra_sources or []),
            "links": [{"relation": "subject", "target_id": subject}],
            "attributes": attributes,
        }
    )


# Model summary table, every row.
summary_claims = [
    ("developer", "developer", "Developer", "BioEmu-2: developer"),
    ("model-architecture", "model_architecture", "Model architecture", "BioEmu-2: model architecture"),
    ("parameters", "parameters", "Parameters", "BioEmu-2: parameter count"),
    ("inputs", "inputs", "Inputs", "BioEmu-2: inputs"),
    ("outputs", "outputs", "Outputs", "BioEmu-2: outputs"),
    ("release-date", "release_date", "Release date", "BioEmu-2: release date"),
    ("licence", "licence", "License", "BioEmu-2: licence as printed in the model card"),
]
for slug, field, row, name in summary_claims:
    claim(
        slug,
        field,
        summary[row],
        "mc",
        f'Model summary table, row "{row}"',
        name,
        f'Parsed from the Model summary table row "{row}" with the row label asserted.',
        table=True,
    )

claim(
    "training-dates",
    "training_dates",
    "August to September 2026",
    "mc",
    'Model summary table, row "Training dates"',
    "BioEmu-2: training dates",
    "Parsed from the Model summary table with the row label asserted. The cell prints the two "
    "month names joined by an en dash; the value here writes that span as words.",
    table=True,
)

claim(
    "related-assets",
    "related_assets",
    "Source code at https://github.com/microsoft/bioemu2 and model checkpoints at "
    "https://huggingface.co/microsoft/bioemu2",
    "mc",
    'Model summary table, row "Related assets"',
    "BioEmu-2: related assets",
    "Parsed from the Model summary table with the row label asserted. The cell prints the two "
    "destinations as markdown links; the value here gives the link text and its target in prose.",
    table=True,
)

# Training data table, every row.
for row in training:
    slug = (
        row["dataset"]
        .lower()
        .replace(",", "")
        .replace(" ", "-")
        .replace("_", "-")
        .replace("--", "-")
    )
    claim(
        "training-data-" + slug,
        "training_data_sets",
        f'{row["dataset"]}: {row["train_sequences_systems"]} train sequences/systems; modality '
        f'{row["modality"]}',
        "mc",
        f'Training data table, row "{row["dataset"]}", columns "Modality" and "Train sequences/systems"',
        f'BioEmu-2 training data: {row["dataset"]}',
        f'Parsed from the Training data table row "{row["dataset"]}" with all twelve row labels '
        "asserted in order.",
        table=True,
    )

# Prose claims. Each tuple: slug, field, value, source key, locator, name, note, subject.
prose: list[tuple] = [
    (
        "capability-structure-prediction",
        "capability",
        "Predicts 3D structures of biomolecules given their chemical composition.",
        "mc",
        "Key model capabilities, first bullet",
        "BioEmu-2: capability, structure prediction from composition",
        "Transcribed from the first capability bullet.",
        MODEL,
    ),
    (
        "capability-multiple-conformations",
        "capability",
        "Models multiple conformations rather than returning only one structure.",
        "mc",
        "Key model capabilities, second bullet",
        "BioEmu-2: capability, multiple conformations",
        "Transcribed from the second capability bullet.",
        MODEL,
    ),
    (
        "capability-contact-guidance",
        "capability",
        "Structure prediction can optionally be guided by user-provided information about "
        "distances between specific atoms.",
        "mc",
        "Key model capabilities, third bullet",
        "BioEmu-2: capability, guidance by atom distances",
        "Transcribed from the third capability bullet.",
        MODEL,
    ),
    (
        "supported-system-components",
        "supported_inputs",
        "Molecular systems containing proteins, nucleic acids, ligands, and other chemical "
        "components.",
        "rd",
        "Key features list, first bullet",
        "BioEmu-2: supported system components",
        "Transcribed from the first key-features bullet.",
        MODEL,
    ),
    (
        "intended-users",
        "intended_users",
        "BioEmu-2 is intended for structural-biology and computational-chemistry researchers. It "
        "can predict 3D structures of biomolecules and biomolecular complexes given their "
        "composition.",
        "mc",
        "Usage: Primary use cases",
        "BioEmu-2: intended users",
        "Transcribed from the primary use cases paragraph.",
        MODEL,
    ),
    (
        "out-of-scope-uses",
        "out_of_scope_uses",
        "Not intended or validated for: clinical, diagnostic, treatment, dosing, or other patient "
        "decisions; designing toxins, pathogens, gain-of-function constructs, or other hazardous "
        "biological agents; quantitative binding-affinity or absolute free-energy prediction; de "
        "novo small-molecule design; autonomous or high-risk decision-making (e.g. law enforcement, "
        "legal, finance, healthcare); sensitive domains where inaccurate outputs could lead to "
        "injury or affect someone's legal, financial, or life opportunities; uses that violate "
        "applicable law, export controls, or the Microsoft Acceptable Use Policy.",
        "mc",
        "Usage: Out-of-scope use cases, the seven listed items",
        "BioEmu-2: out-of-scope uses",
        "All seven listed items transcribed from the out-of-scope use cases list.",
        MODEL,
    ),
    (
        "no-sequence-generation-or-affinity",
        "scope_boundary",
        "BioEmu-2 predicts structural ensembles for sequences supplied by the user. It does not "
        "generate sequences, and it does not predict binding affinities.",
        "mc",
        "Usage: Out-of-scope use cases, paragraph after the list",
        "BioEmu-2: does not generate sequences or predict affinity",
        "Transcribed from the paragraph after the out-of-scope list.",
        MODEL,
    ),
    (
        "outputs-are-hypotheses",
        "output_interpretation",
        "Predicted structures are not experimentally validated measurements and should not be "
        "treated as such. Generated structures should be treated as computational hypotheses and "
        "should be assessed using appropriate computational or experimental validation before "
        "informing downstream research.",
        "mc",
        "Usage: Out-of-scope use cases, paragraph after the list; Technical requirements and "
        "integration guidance, second sentence",
        "BioEmu-2: outputs are computational hypotheses",
        "Two sentences from the two named places, joined; both say the outputs are not measurements.",
        MODEL,
    ),
    (
        "usage-recommendation",
        "usage_recommendation",
        "BioEmu-2 is released for research purposes. We do not recommend using it in commercial or "
        "real-world applications without further testing and development.",
        "mc",
        "Usage: Out-of-scope use cases, closing paragraphs",
        "BioEmu-2: research use recommendation",
        "Transcribed from the closing paragraphs. This is the developer's recommendation, not a "
        "licence term; the licence printed in the same model card is MIT.",
        MODEL,
    ),
    (
        "software-access",
        "software_access",
        "BioEmu-2 provides open-source inference code with a Python API and command-line "
        "interface.",
        "mc",
        "Technical requirements and integration guidance, first sentence",
        "BioEmu-2: open-source inference code",
        "Transcribed from the technical requirements section.",
        MODEL,
    ),
    (
        "smallest-tested-gpu-model-card",
        "hardware_tested",
        "BioEmu-2 has been tested using NVIDIA GPUs, with an 80 GB A100 being the smallest tested "
        "device.",
        "mc",
        "Technical requirements and integration guidance, second paragraph",
        "BioEmu-2: smallest tested GPU as stated in the model card",
        "Transcribed from the technical requirements section. README.md at the same commit reports "
        "testing on smaller GPUs, so the two statements are recorded separately and no minimum is "
        "stated on the model record.",
        MODEL,
    ),
    (
        "tested-gpus-readme",
        "hardware_tested",
        "We have tested V100 (compute capability 7.0), T4 (7.5, with the CUDA 12 installation), "
        "A100 and RTX A6000 (8.0 and 8.6), and B200 (10.0); other eligible GPUs have not been "
        "verified end to end.",
        "rd",
        "System requirements, third sentence",
        "BioEmu-2: tested GPUs as listed in the README",
        "Transcribed from the README system requirements. This is the counterpart to the model "
        "card's 80 GB A100 statement.",
        CFG_RUNTIME,
    ),
    (
        "compute-capability-requirement",
        "hardware_requirement",
        "The cuda extra installs CUDA 13 cuEquivariance, which requires compute capability 7.5 or "
        "newer, such as T4, A100, RTX A6000, L40S, H100 and B200. GPUs with compute capability 7.0 "
        "(Volta, such as V100) need the CUDA 12 installation instead, and compute capability below "
        "7.0 is not supported.",
        "rd",
        "System requirements and Installation",
        "BioEmu-2: compute capability requirement per install path",
        "Transcribed from the system requirements and installation sections; the requirement is "
        "stated per install extra, not as one device.",
        CFG_RUNTIME,
    ),
    (
        "operating-system-requirement",
        "platform_requirement",
        "BioEmu2 requires Linux and an NVIDIA GPU; macOS and Windows are not supported.",
        "rd",
        "System requirements, first sentence",
        "BioEmu-2: operating system requirement",
        "Transcribed from the README system requirements.",
        CFG_RUNTIME,
    ),
    (
        "python-versions",
        "python_support",
        "Use Python 3.12, 3.13 or 3.14. The developers tested BioEmu2 and evaluated its benchmark "
        "metrics with Python 3.12; 3.13 and 3.14 pass the test suite, but benchmark metrics were "
        "not evaluated with them.",
        "rd",
        "Installation, first paragraph and the paragraph before the development note",
        "BioEmu-2: supported Python versions and the interpreter used for benchmark metrics",
        "Two statements from the installation section, joined; they tie the evaluated benchmark "
        "metrics to Python 3.12.",
        CFG_RUNTIME,
    ),
    (
        "context-parallel-requirement",
        "hardware_requirement",
        "Context-parallel sampling requires a square number of NVIDIA GPUs, at least four, "
        "arranged as an n x n grid, and the CUDA extra. Context parallelism has not been tested on "
        "older GPUs such as the V100.",
        "cp",
        "System requirements, both bullets",
        "BioEmu-2: context-parallel GPU requirement",
        "Both bullets transcribed from the context-parallel system requirements.",
        CFG_RUNTIME,
    ),
    (
        "largest-systems-embedded",
        "capacity_measured",
        "On 192 GB B200 GPUs with an MSA depth of 4,092, the largest systems we embedded had "
        "3,072 tokens on one GPU, 10,240 tokens on a 2x2 grid, and 16,384 tokens on a 4x4 grid.",
        "cp",
        "Choose the number of GPUs, first paragraph",
        "BioEmu-2: largest systems embedded per GPU grid",
        "Transcribed from the Choose the number of GPUs paragraph. These are developer-reported "
        "capacity figures for the trunk embedding, not an evaluation result, and the source prints "
        "the grid sizes as 2x2 and 4x4 with a multiplication sign.",
        CFG_RUNTIME,
    ),
    (
        "package-identity",
        "package_identity",
        "Distribution bioemu2 version 0.1.0rc0, requires Python 3.12 or newer, license MIT, with "
        "the bioemu2 command line entry point.",
        "pp",
        "[project] table: name, version, requires-python, license and [project.scripts]",
        "BioEmu-2: inference package identity",
        "Transcribed from the [project] table of pyproject.toml.",
        CFG_RUNTIME,
    ),
    (
        "install-extras",
        "install_configurations",
        "Two mutually exclusive install extras: cuda pins cuequivariance 0.11.1 with the CUDA 13 "
        "operator wheels, and cuda12 pins torch 2.13.0+cu126 from the PyTorch cu126 index with "
        "cuequivariance 0.11.1 and the CUDA 12 operator wheels. The core dependency allows "
        "torch>=2.11,<2.14.",
        "pp",
        "[project.optional-dependencies] cuda and cuda12; [tool.uv] conflicts; [project] "
        "dependencies torch pin",
        "BioEmu-2: the two CUDA install configurations",
        "Transcribed from the optional dependency tables and the declared extras conflict. These "
        "are install paths of one package, not separate models.",
        CFG_RUNTIME,
    ),
    (
        "default-checkpoint",
        "default_checkpoint",
        "By default load_model() downloads the bioemu2-preview checkpoint from the "
        "microsoft/bioemu2 Hugging Face repository; the checkpoint and its configuration are "
        "cached in the standard Hugging Face cache.",
        "ck",
        "Opening paragraph and Choose where checkpoints are cached",
        "BioEmu-2: default checkpoint and cache",
        "Transcribed from the checkpoint guide.",
        CFG_CKPT,
    ),
    (
        "default-precision",
        "default_precision",
        "load_model() defaults to bf16-mixed precision for the trunk embedding and high float32 "
        "matmul precision for the denoiser; passing precision 32-true and no matmul precision runs "
        "both in full precision.",
        "ck",
        "Opening paragraph, after the load_model example",
        "BioEmu-2: default precision settings",
        "Transcribed from the checkpoint guide.",
        CFG_CKPT,
    ),
    (
        "released-checkpoint-files",
        "released_checkpoints",
        "The pinned Hugging Face revision releases one checkpoint, bioemu2-preview, as "
        "checkpoints/bioemu2-preview/checkpoint.ckpt with its config.yaml; the repository holds no "
        "other checkpoint directory at this revision.",
        "ls",
        "API listing for revision dd4b0c1b, siblings array",
        "BioEmu-2: released checkpoints at the pinned revision",
        "Read from the five siblings entries in the API listing: .gitattributes, MODEL_CARD.md, "
        "README.md and the two files under checkpoints/bioemu2-preview/.",
        CFG_CKPT,
    ),
    (
        "checkpoint-digest",
        "checkpoint_digest",
        "The Git LFS pointer for checkpoints/bioemu2-preview/checkpoint.ckpt publishes oid "
        "sha256:3b4ba9236b7b458f47b40b694847b6bb4110c744becd6d2c53de7b1d04c07a81 and size "
        "2047661181.",
        "pt",
        "Git LFS pointer, oid and size lines",
        "BioEmu-2: published checkpoint digest and size",
        "Transcribed from the three-line LFS pointer. The checkpoint bytes were not downloaded, so "
        "this digest is the publisher's and was not recomputed here.",
        CFG_CKPT,
    ),
    (
        "checkpoint-architecture",
        "checkpoint_architecture",
        "The distributed configuration builds bioemu2.shortcuts.BioMoaCModel with a "
        "PairMixerSequenceEmbedder of 48 blocks, token embedding widths 384 and 256, 4 MSA blocks, "
        "a diffusion transformer of depth 16 with 16 token attention heads, contact, method and "
        "dynamics conditioning enabled, and an EDM schedule with sigma_min 0.0004, sigma_max 160.0 "
        "and sigma_data 16.0.",
        "cf",
        "config.yaml: score_model, sequence_embedder and edm_schedule blocks",
        "BioEmu-2: checkpoint architecture configuration",
        "Transcribed from the checkpoint config.yaml. The model card prints no architecture detail "
        "beyond calling the model a diffusion-based all-atom score model of approximately 500M "
        "parameters, and the configuration prints no parameter count.",
        CFG_CKPT,
    ),
    (
        "two-trained-tasks",
        "trained_tasks",
        "BioEmu2 was trained for two different tasks, structure prediction and equilibrium "
        "sampling.",
        "sp",
        "Choose a sampling mode, first sentence",
        "BioEmu-2: the two tasks the model was trained for",
        "Transcribed from the sampling guide, immediately before the mode table.",
        MODEL,
    ),
    (
        "msa-default-source",
        "msa_source",
        "If you omit msa, the session loads a cached ColabFold alignment or queries the public "
        "ColabFold server when first needed.",
        "sp",
        "Customize an EmuSession: Provide an MSA",
        "BioEmu-2: default alignment source",
        "Transcribed from the sampling guide, with the backticks around msa removed. This bears on the "
        "model card's MSA dependence "
        "limitation, because the default alignment comes from a public service.",
        MODEL,
    ),
    (
        "propagation-lag-range",
        "propagation_lags",
        "Use lags from 1 to 1000 ns (1 ns to 1 microsecond), the range the model mostly saw during "
        "training. At longer lags, endpoints approach the equilibrium ensemble; beyond a few "
        "milliseconds, use equilibrium sampling instead.",
        "pr",
        "Opening paragraphs, third paragraph",
        "BioEmu-2: usable propagation lag range",
        "Transcribed from the propagation guide. The source writes the upper bound with a micro "
        "sign; the value spells the unit out.",
        CFG_PROPAGATION,
    ),
    (
        "propagation-endpoints",
        "propagation_output",
        "Propagation samples a structure at a future time from a starting structure; each result "
        "is an endpoint, not an intermediate frame in a trajectory.",
        "pr",
        "Opening paragraphs, first two sentences",
        "BioEmu-2: propagated samples are endpoints",
        "Transcribed from the propagation guide, with the code spans around the symbols for the "
        "propagated structure, the time and the lag argument removed.",
        CFG_PROPAGATION,
    ),
    (
        "feature-time-lagged-propagation",
        "capability",
        "Time-lagged trajectory generation with implicit transfer operator models.",
        "rd",
        "Key features list, third bullet",
        "BioEmu-2: capability, time-lagged generation with implicit transfer operators",
        "Transcribed from the third key-features bullet.",
        MODEL,
    ),
    (
        "feature-steering",
        "capability",
        "Contact conditioning and inference-time steering toward desired properties.",
        "rd",
        "Key features list, fourth bullet",
        "BioEmu-2: capability, contact conditioning and inference-time steering",
        "Transcribed from the fourth key-features bullet.",
        MODEL,
    ),
    (
        "feature-context-parallel",
        "capability",
        "Context-parallel sampling of structures that do not fit on one GPU.",
        "rd",
        "Key features list, fifth bullet",
        "BioEmu-2: capability, context-parallel sampling",
        "Transcribed from the fifth key-features bullet.",
        MODEL,
    ),
    (
        "developer-team",
        "developer_team",
        "BioEmu2, short for 'biomolecular emulator', is developed by Microsoft Research AI for "
        "Science.",
        "rd",
        "Paragraph under the title block",
        "BioEmu-2: developing team",
        "Transcribed from the README paragraph under the title block, where biomolecular emulator is in "
        "double quotes. The model card's Developer "
        "row says Microsoft Research.",
        MODEL,
    ),
    (
        "self-description",
        "self_description",
        "A foundation model for biomolecular structure and dynamics. Predict folded structures, "
        "sample equilibrium ensembles, and propagate structures forward in time.",
        "rd",
        "Title block, subtitle and tagline",
        "BioEmu-2: how the repository describes the model",
        "Transcribed from the README title block, which prints the first line as a heading and the "
        "second in bold. This is the wording behind the foundation_model "
        "method type on these records.",
        MODEL,
    ),
    (
        "limitation-quantification",
        "limitation",
        "Outputs are plausible hypotheses, not measurements. The following limitations have not "
        "been quantitatively characterized: MSA dependence, training-distribution bias, "
        "uncalibrated ensembles, ligand scope and the physicality of large systems.",
        "mc",
        "Known limitations, opening sentences",
        "BioEmu-2: limitations are not quantified",
        "The two sentences that open the Known limitations section, followed by the five bullet "
        "headings they introduce.",
        MODEL,
    ),
    (
        "limitation-msa-dependence",
        "limitation",
        "MSA dependence: quality is expected to fall for shallow or poor MSAs, including orphan "
        "proteins, engineered constructs, and some viral proteins.",
        "mc",
        "Known limitations, MSA dependence bullet",
        "BioEmu-2: limitation, MSA dependence",
        "Transcribed from the MSA dependence bullet.",
        MODEL,
    ),
    (
        "limitation-training-distribution-bias",
        "limitation",
        "Training-distribution bias: PDB, AFDB, and Microsoft-generated MD data over-represent "
        "well-studied protein families. Performance on under-represented sequence classes is "
        "uncertain.",
        "mc",
        "Known limitations, Training-distribution bias bullet",
        "BioEmu-2: limitation, training distribution bias",
        "Transcribed from the training-distribution bias bullet.",
        MODEL,
    ),
    (
        "limitation-uncalibrated-ensembles",
        "limitation",
        "Uncalibrated ensembles: sampling frequency must not be interpreted as a calibrated "
        "Boltzmann probability or quantitative free energy.",
        "mc",
        "Known limitations, Uncalibrated ensembles bullet",
        "BioEmu-2: limitation, sampling frequency is not a Boltzmann probability",
        "Transcribed from the uncalibrated ensembles bullet. This limitation is also carried on the "
        "equilibrium-sampling and checkpoint configurations, because it bears on any protocol that "
        "would read state populations or free energy differences off sample counts.",
        MODEL,
    ),
    (
        "limitation-ligand-scope",
        "limitation",
        "Ligand scope: supplied bound ligands are supported, but de novo ligand design and "
        "binding-affinity prediction are out of scope.",
        "mc",
        "Known limitations, Ligand scope bullet",
        "BioEmu-2: limitation, ligand scope",
        "Transcribed from the ligand scope bullet.",
        MODEL,
    ),
    (
        "limitation-large-systems",
        "limitation",
        "Physicality of large systems: the model may struggle to produce physically plausible "
        "structures for extremely large complexes (over 10k tokens).",
        "mc",
        "Known limitations, Physicality of large systems bullet",
        "BioEmu-2: limitation, physicality of large systems",
        "Transcribed from the physicality bullet.",
        MODEL,
    ),
    (
        "responsible-ai-combination-risk",
        "responsible_ai_consideration",
        "Combining the model with sequence-generation or autonomous design tools may create risks "
        "not assessed for the standalone model.",
        "mc",
        "Responsible AI considerations",
        "BioEmu-2: risk of combining with design tools",
        "Transcribed from the Responsible AI considerations section.",
        MODEL,
    ),
    (
        "evaluation-scope",
        "evaluation_scope",
        "The evaluation covers: (i) structure prediction using standard public benchmarks, (ii) "
        "multiconformational sampling performance using a curated benchmark, and (iii) molecular "
        "dynamics (MD) emulation performance using an MD benchmark suite. It also examines the "
        "model's ability to scale to large complexes at inference time.",
        "mc",
        "Evaluation methodology, first paragraph",
        "BioEmu-2: scope of the developer evaluation",
        "Transcribed from the first paragraph of the evaluation methodology. No numeric value is "
        "printed anywhere in this section, so no evaluation or result record was created.",
        MODEL,
    ),
    (
        "evaluation-single-checkpoint",
        "evaluation_checkpoint",
        "We use the same model checkpoint to evaluate all benchmarks.",
        "mc",
        "Evaluation methodology, second paragraph",
        "BioEmu-2: one checkpoint across all evaluations",
        "Transcribed from the evaluation methodology. The checkpoint is not named, so this claim is "
        "not assigned to bioemu2-preview.",
        MODEL,
    ),
    (
        "evaluation-folding",
        "evaluation_protocol",
        "Folding quality is evaluated in terms of root-mean-square deviation (RMSD), TM-score, "
        "local distance difference test (lDDT), physicality, and interface DockQ scores on the "
        "Boltz-1 test set. Average metrics are compared against a range of state-of-the-art "
        "cofolding models.",
        "mc",
        "Evaluation methodology, third paragraph",
        "BioEmu-2: folding evaluation as described",
        "Transcribed from the evaluation methodology. The baselines are described only as a range "
        "of state-of-the-art cofolding models, none named, and no metric value is printed, so no "
        "benchmark, evaluation or result record was created from this paragraph.",
        MODEL,
    ),
    (
        "evaluation-multiconformational",
        "evaluation_protocol",
        "Multiconformational sampling performance is evaluated on an in-house curated subset of "
        "highly similar Protein Data Bank (PDB) structures paired to contrast the effect of "
        "cofolding partners, including small-molecule ligands and other polymer chains. Success is determined "
        "by whether the model can distinguish and correctly generate samples for the designated "
        "states corresponding to the input system definitions.",
        "mc",
        "Evaluation methodology, fourth paragraph",
        "BioEmu-2: paired-conformation evaluation as described",
        "Transcribed from the evaluation methodology. The curated subset is not published or sized "
        "in the pinned sources, so no dataset or benchmark record was created.",
        MODEL,
    ),
    (
        "evaluation-md-emulation",
        "evaluation_protocol",
        "MD emulation performance is evaluated by sampling a holdout set from the MD datasets "
        "described in the Training data section and computing state coverage and "
        "weight-distribution divergences. Better coverage and lower divergence indicate better model "
        "performance.",
        "mc",
        "Evaluation methodology, fifth paragraph",
        "BioEmu-2: MD emulation evaluation as described",
        "Transcribed from the evaluation methodology. The holdout comes from the same MD datasets "
        "the model was trained on, so no benchmark record was created from it, and no metric value "
        "is printed.",
        MODEL,
    ),
    (
        "evaluation-large-complexes",
        "evaluation_protocol",
        "The ability to sample large complexes is evaluated on a subset of complexes exceeding "
        "1,500 tokens and compared against reference PDB structures. The selected systems span a "
        "range of sizes to demonstrate memory consumption, runtime scaling, and feasibility for "
        "multi-GPU deployment. Success is determined by correct overall chain placement, structural "
        "physicality, and standard folding quality metrics.",
        "mc",
        "Evaluation methodology, sixth paragraph",
        "BioEmu-2: large-complex evaluation as described",
        "Transcribed from the evaluation methodology. No memory, runtime or quality value is "
        "printed for these systems.",
        MODEL,
    ),
    (
        "training-data-provenance",
        "training_data_provenance",
        "BioEmu-2 was trained only on publicly available data and data generated in-house by "
        "Microsoft; it did not use datasets specially licensed to Microsoft. The training data "
        "combines experimental structures from the Protein Data Bank (PDB), AI-predicted structures "
        "from the AlphaFold Protein Structure Database (AFDB) and Teddymer, and Microsoft-generated "
        "molecular-dynamics trajectories. The AFDB datasets contain AlphaFold-family predictions, "
        "and Teddymer is derived from AlphaFold2 predictions.",
        "mc",
        "Training data, paragraph after the table",
        "BioEmu-2: training data provenance",
        "Transcribed from the paragraph after the training data table.",
        MODEL,
    ),
    (
        "licence-grant",
        "licence_grant",
        "MIT License, copyright Microsoft Corporation: permission is granted free of charge to use, "
        "copy, modify, merge, publish, distribute, sublicense and sell copies, subject to including "
        "the copyright and permission notice, and the software is provided as is without warranty.",
        "lc",
        "LICENSE, whole file",
        "BioEmu-2: what the repository licence grants",
        "Summarised from the MIT licence text in LICENSE, which is the standard MIT wording with "
        "Microsoft Corporation as copyright holder.",
        MODEL,
    ),
    (
        "licence-and-notices",
        "licence_scope",
        "BioEmu2 is released under the MIT License. It includes code and reference data adapted "
        "from other open-source projects; the third-party notices identify those components and "
        "their licenses.",
        "rd",
        "License section",
        "BioEmu-2: licence statement and its pointer to the notices",
        "Transcribed from the README licence section, with the markdown link targets to LICENSE and "
        "NOTICES.md removed from the link text.",
        MODEL,
    ),
    (
        "notices-scope",
        "third_party_notices",
        "Except where otherwise noted, code authored for BioEmu2 by Microsoft is licensed under the "
        "MIT License. The distribution also contains third-party code under the licences in "
        "licenses/LICENSE.BOLTZ-MIT, LICENSE.GEOSTD, LICENSE.NVIDIA-FOLD-CP-MIT, "
        "LICENSE.PYTORCH3D-BSD, LICENSE.TORCH-SCATTER-MIT, LICENSE.LGPL-3.0 and LICENSE.GPL-3.0.",
        "nt",
        "NOTICES.md, opening paragraph",
        "BioEmu-2: what the MIT licence covers and what the notices cover",
        "Transcribed from the opening paragraph of NOTICES.md. The MIT grant covers "
        "Microsoft-authored code; the notices cover borrowed components separately.",
        MODEL,
    ),
    (
        "notices-lgpl-components",
        "third_party_notices",
        "Two distributed files are not under MIT: src/bioemu2/assets/stereo_chemistry.yaml carries "
        "bond-length and bond-angle reference data exported from OpenStructure 2.11.1 whose monlib "
        "section derives from CCP4 MON_LIB under the LGPL version 3.0, and "
        "src/bioemu2/patches/mdtraj_patcher.py is licensed under the LGPL version 3.0 or any later "
        "version.",
        "nt",
        "NOTICES.md, Stereochemistry reference data and MDTraj patches sections",
        "BioEmu-2: the LGPL-3.0 files in the distribution",
        "Transcribed from the two named sections of NOTICES.md.",
        MODEL,
    ),
    (
        "notices-boltz-derived",
        "third_party_notices",
        "BioMoA layers and operations, denoising and steering code, MSA feature preparation, "
        "data-interface code and all-atom feature preparation contain portions copied or adapted "
        "from Boltz v1.0.0 under the MIT License, and the contact-conditioning code and feature "
        "conventions are adapted from Boltz at commit "
        "b1ebfc46ecf57f5414e0d1a6f9027bbb122c53bc.",
        "nt",
        "NOTICES.md, Boltz-derived code section",
        "BioEmu-2: Boltz-derived components",
        "Transcribed from the Boltz-derived code section. This is a code-reuse relationship, not an "
        "evaluation of Boltz, so no link to a Boltz record was created.",
        MODEL,
    ),
    (
        "notices-other-third-party",
        "third_party_notices",
        "Further borrowed components: quaternion and rotation helpers adapted from PyTorch3D under "
        "a BSD licence, scatter code from torch_scatter under MIT, context-parallel primitives "
        "ported from NVIDIA Fold-CP under MIT, modified OpenMM portions under OpenMM's MIT licence, "
        "and nucleotide link parameters adapted from geostd with its Lawrence Berkeley National "
        "Laboratory notice.",
        "nt",
        "NOTICES.md, PyTorch3D, torch_scatter, NVIDIA Fold-CP, OpenMM and geostd sections",
        "BioEmu-2: other third-party components",
        "Transcribed from the remaining notice sections.",
        MODEL,
    ),
]

for slug, field, value, key, locator, name, note, subject in prose:
    claim(slug, field, value, key, locator, name, note, subject=subject)

claim(
    "model-card-publication",
    "model_card_publication",
    "The model card is published both as MODEL_CARD.md in the repository at commit 6d1ca74 and as "
    "README.md in the Hugging Face weights repository at revision dd4b0c1b; the two carry the same "
    "text.",
    "hf",
    "Hugging Face README.md at dd4b0c1b, whole file; MODEL_CARD.md in the repository at 6d1ca74, "
    "whole file",
    "BioEmu-2: where the model card is published",
    "The two pinned files were compared byte for byte: the Hugging Face README is the repository "
    "MODEL_CARD.md with a four-line YAML front matter block that sets license: mit, and nothing "
    "else differs.",
    extra_sources=[S["mc"]],
)


# ---------------------------------------------------------------- write

records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
assert len(ids) == len(set(ids)), "duplicate record IDs"
with OUT.open("w", encoding="utf-8") as handle:
    for record in records:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

counts: dict[str, int] = {}
for record in records:
    counts[record["kind"]] = counts.get(record["kind"], 0) + 1
print(f"wrote {OUT} with {len(records)} records: {counts}")
