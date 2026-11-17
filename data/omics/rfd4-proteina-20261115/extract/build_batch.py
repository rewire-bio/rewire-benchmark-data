#!/usr/bin/env python3
"""Build data/omics/rfd4-proteina-20261115/batch.jsonl.

Every result comes from extract/efficiency-table.json, which is written by
extract/parse_efficiency_table.py from the pinned model card with its row labels asserted.
Descriptive values come from the pinned artifacts listed in SOURCES; the locator on each
record names where in which artifact it is printed.

Run: python3 -I extract/build_batch.py
"""

from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
BATCH_DIR = HERE.parent
P = "rfd4-proteina-20261115-"

RETRIEVED_AT = "2026-11-15T23:10:00Z"
DATE = "2026-11-15"

CODE_COMMIT = "68058693cb88762a8aaf806571e13b291ce6318a"
HF_REVISION = "621b785abf9d61dd24f4b81ae4dbd1330728f030"

REVIEWER = ["claude"]
REVIEWER_NOTE = (
    "Claude (Opus 5) extraction agent; no human review claimed. Extraction only: a different "
    "agent reviews this batch, and nothing here is reproduced."
)

AREAS = ["proteins-complexes", "protein-structure", "molecular-interactions"]
FACETS_MODEL = {"areas": AREAS, "contexts": ["research"], "method_types": ["foundation_model"]}
FACETS_PLAIN = {"areas": AREAS, "contexts": ["research"]}

# --- sources -------------------------------------------------------------------------------

PREPRINT_ID = P + "source-preprint-v3"

SOURCES = [
    {
        "id": P + "source-hf-model-card",
        "name": "RFD4-Proteina Hugging Face model card at revision 621b785",
        "description": (
            "The model card of the nvidia/RFD4-Proteina weight repository, pinned to one commit, "
            "which carries the release checkpoint pair, the compute presets, the licence scope and "
            "the measured design efficiency table."
        ),
        "url": "https://huggingface.co/nvidia/RFD4-Proteina/blob/" + HF_REVISION + "/README.md",
        "retrieval_url": "https://huggingface.co/nvidia/RFD4-Proteina/raw/" + HF_REVISION + "/README.md",
        "version": "Hugging Face revision " + HF_REVISION,
        "artifact_sha256": "38479d8e4c6e46ed7e1ec4ece0dd02c358ae46d73d56790c44be813201fd9b98",
        "archive_sha256": "685e0d82607b569a16e106afb9c69e34139a56cedba3f053cf45cc59722894c8",
        "archive_member": "artifacts/hf_README.md.gz",
        "media_type": "text/markdown",
        "licence": "BSD 3-Clause for the RFD4-Proteina model, weights and code; optional third-party assets keep their own upstream terms",
        "publication_status": "official_project_source",
        "source_locator": (
            "Sections 'Where to find each entry point', 'At a glance', 'Checkpoints in this release', "
            "'Compute presets', 'Hardware requirements', 'Measured design efficiency', "
            "'Training data and limitations', 'Other repository files' and 'License'"
        ),
        "limitations": [
            "The card states that the efficiency table was measured on the previous release pair in the October 9, 2026 frozen project benchmark and has not been re-measured on the 2026-10-19 release.",
            "Author-published; no independent evaluation.",
        ],
    },
    {
        "id": P + "source-hf-release-checkpoints",
        "name": "RFD4-Proteina release-checkpoints.json at revision 621b785",
        "description": "The release manifest of the pinned weight repository, giving the pair identity, the stable filenames, the source training filenames and the SHA-256 of each published and full checkpoint.",
        "url": "https://huggingface.co/nvidia/RFD4-Proteina/blob/" + HF_REVISION + "/release-checkpoints.json",
        "retrieval_url": "https://huggingface.co/nvidia/RFD4-Proteina/raw/" + HF_REVISION + "/release-checkpoints.json",
        "version": "Hugging Face revision " + HF_REVISION,
        "artifact_sha256": "17b8b56247bcae1caf5b39e758c40178863572de0485048dd41f261c93ad16c4",
        "archive_sha256": "944a1fcefa207b13afb222d0152cbf0cb070350f26ec760c9992686766066353",
        "archive_member": "artifacts/hf_release-checkpoints.json.gz",
        "media_type": "application/json",
        "licence": "BSD 3-Clause",
        "publication_status": "official_project_source",
        "source_locator": "Keys 'checkpoints', 'bundles', 'adapters', 'supersedes' and 'policy'",
    },
    {
        "id": P + "source-hf-benchmark-provenance",
        "name": "RFD4-Proteina benchmarks/provenance.json at revision 621b785",
        "description": "The provenance file of the published benchmark packet, naming the frozen supplement release it was taken from, the metric expression and the scope of the runs.",
        "url": "https://huggingface.co/nvidia/RFD4-Proteina/blob/" + HF_REVISION + "/benchmarks/provenance.json",
        "retrieval_url": "https://huggingface.co/nvidia/RFD4-Proteina/raw/" + HF_REVISION + "/benchmarks/provenance.json",
        "version": "Hugging Face revision " + HF_REVISION,
        "artifact_sha256": "4e7a3051a58902cc7713d02c52941894eb9581b82e5af85a3b4f256f1a258336",
        "archive_sha256": "90008405bef72cb56f687e08d4dd5678b4cc867cb9987dcbe2098eae217cc50a",
        "archive_member": "artifacts/hf_benchmarks_provenance.json.gz",
        "media_type": "application/json",
        "licence": "BSD 3-Clause",
        "publication_status": "official_project_source",
        "source_locator": "Keys 'source_release', 'paper_commit', 'metric', 'sha256' and 'scope'",
    },
    {
        "id": P + "source-hf-benchmark-methods",
        "name": "RFD4-Proteina benchmarks/METHODS.md at revision 621b785",
        "description": "The methods supplement of the published benchmark packet, giving the timing accounting, the per-method recipes, the common AlphaFold3 pass criteria and the clustering rule.",
        "url": "https://huggingface.co/nvidia/RFD4-Proteina/blob/" + HF_REVISION + "/benchmarks/METHODS.md",
        "retrieval_url": "https://huggingface.co/nvidia/RFD4-Proteina/raw/" + HF_REVISION + "/benchmarks/METHODS.md",
        "version": "Hugging Face revision " + HF_REVISION,
        "artifact_sha256": "46d1e181c495d4ecc9a3992a4e7f3cd8fae0b4904fb799ab5c1a883090ca837b",
        "archive_sha256": "874fbc30bc22db1b38acee7a244cdc59daddb2ff88600aabcc2209888d93783e",
        "archive_member": "artifacts/hf_benchmarks_METHODS.md.gz",
        "media_type": "text/markdown",
        "licence": "BSD 3-Clause",
        "publication_status": "official_project_source",
        "source_locator": "Sections 'Common accounting and timing', 'Model recipes and adaptations', 'Common AF3 scoring' and 'Supplement selection and conditioning comparisons'",
        "limitations": [
            "States that the executed schedule and checkpoint for each RFD4-Proteina cohort come from its own native config, which is not published in this packet, so no row in it is tied to a named checkpoint file.",
        ],
    },
    {
        "id": P + "source-hf-benchmark-summary",
        "name": "RFD4-Proteina benchmarks/summary.csv at revision 621b785",
        "description": "The full comparison table behind the model card's efficiency table, with 52 method rows giving pass rates and per-10-GPU-minute efficiency for each panel, protocol, conditioning arm and pass criterion.",
        "url": "https://huggingface.co/nvidia/RFD4-Proteina/blob/" + HF_REVISION + "/benchmarks/summary.csv",
        "retrieval_url": "https://huggingface.co/nvidia/RFD4-Proteina/raw/" + HF_REVISION + "/benchmarks/summary.csv",
        "version": "Hugging Face revision " + HF_REVISION,
        "artifact_sha256": "5c6d525d988d0df7fecb74396f86401c1ddb4c31fa83f00b357ba77d855d8a10",
        "archive_sha256": "b6b62e88afe03468941c5b7f17810cab215477f6bd7c38afd7f349c6bd18a439",
        "archive_member": "artifacts/hf_benchmarks_summary.csv.gz",
        "media_type": "text/csv",
        "licence": "BSD 3-Clause",
        "publication_status": "official_project_source",
        "source_locator": "Columns panel, model, protocol, dataset, label, criterion, unique_per_10_gpu_min, targets, attempts",
        "limitations": [
            "Its SHA-256 equals the value benchmarks/provenance.json declares for summary.csv, so the packet is internally consistent.",
            "Only the 8 cells the model card prints were taken into records; the remaining rows were used as a unit cross-check and are a recorded gap.",
        ],
    },
    {
        "id": P + "source-github-readme",
        "name": "RFD4-Proteina repository README at commit 6805869",
        "description": "The README of the RosettaCommons/RFD4-Proteina repository, pinned to one commit, which states the design tasks, the installation routes, the runtime requirements and the citation.",
        "url": "https://github.com/RosettaCommons/RFD4-Proteina/blob/" + CODE_COMMIT + "/README.md",
        "retrieval_url": "https://raw.githubusercontent.com/RosettaCommons/RFD4-Proteina/" + CODE_COMMIT + "/README.md",
        "version": "git commit " + CODE_COMMIT,
        "artifact_sha256": "e3327fb127c36d9ff3d464caf14afbbd76ded521158a6be1abf860c11169fa64",
        "archive_sha256": "c2ab38624ec3bdd9383735846019f533d256f94336edfd15eecd0c47546804f8",
        "archive_member": "artifacts/gh_README.md.gz",
        "media_type": "text/markdown",
        "licence": "BSD 3-Clause",
        "publication_status": "official_project_source",
        "source_locator": "Sections 'Try it now', 'System requirements', 'Install', 'Run the model', 'More workflows' and 'Citation'",
        "code_url": "https://github.com/RosettaCommons/RFD4-Proteina",
    },
    {
        "id": P + "source-github-licence",
        "name": "RFD4-Proteina repository LICENSE at commit 6805869",
        "description": "The licence file of the RFD4-Proteina repository at the pinned commit.",
        "url": "https://github.com/RosettaCommons/RFD4-Proteina/blob/" + CODE_COMMIT + "/LICENSE",
        "retrieval_url": "https://raw.githubusercontent.com/RosettaCommons/RFD4-Proteina/" + CODE_COMMIT + "/LICENSE",
        "version": "git commit " + CODE_COMMIT,
        "artifact_sha256": "0927a01536709c20efa64834482fd4d50c9bb954353dbcf35c95a98675545470",
        "archive_sha256": "eadedffe9908ffaedf1a5b486f3039834a6f9e7c6b49d800d93005f5aee8d84c",
        "archive_member": "artifacts/gh_LICENSE.gz",
        "media_type": "text/plain",
        "licence": "BSD 3-Clause",
        "publication_status": "official_project_source",
        "source_locator": "Whole file: 'BSD 3-Clause License, Copyright (c) 2026, Institute for Protein Design, University of Washington'",
        "limitations": [
            "The file itself names no model weights or third-party assets; what the licence covers is stated on the Hugging Face model card instead.",
        ],
    },
    {
        "id": P + "source-github-checkpoints-doc",
        "name": "RFD4-Proteina checkpoints reference at commit 6805869",
        "description": "The documentation page listing the checkpoint roles RFD4-Proteina loads, the released pair and their training recipes, pinned to one commit.",
        "url": "https://github.com/RosettaCommons/RFD4-Proteina/blob/" + CODE_COMMIT + "/docs/reference/checkpoints.md",
        "retrieval_url": "https://raw.githubusercontent.com/RosettaCommons/RFD4-Proteina/" + CODE_COMMIT + "/docs/reference/checkpoints.md",
        "version": "git commit " + CODE_COMMIT,
        "artifact_sha256": "b18b755f5098208611f02cb4b4100eedeeca5730a450d484b2356e844fec8f3b",
        "archive_sha256": "b22f79dfc1aa56de7263efe66a04bffd5b0a4affa49ab6a66b63fe0e74f1b07c",
        "archive_member": "artifacts/gh_docs_reference_checkpoints.md.gz",
        "media_type": "text/markdown",
        "licence": "BSD 3-Clause",
        "publication_status": "official_project_source",
        "source_locator": "Sections 'Types of checkpoints', 'Released checkpoints' and 'Downloading'",
    },
    {
        "id": P + "source-github-docs-index",
        "name": "RFD4-Proteina documentation index at commit 6805869",
        "description": "The documentation landing page source, which lists the design tasks the released checkpoint supports and attributes the work to the Baker Lab, NVIDIA GenAIR and the Institute for Protein Design.",
        "url": "https://github.com/RosettaCommons/RFD4-Proteina/blob/" + CODE_COMMIT + "/docs/index.rst",
        "retrieval_url": "https://raw.githubusercontent.com/RosettaCommons/RFD4-Proteina/" + CODE_COMMIT + "/docs/index.rst",
        "version": "git commit " + CODE_COMMIT,
        "artifact_sha256": "228ddfd74255e4458fd8e542bdd8d0a2926ba639c5178f411996848b693c9c48",
        "archive_sha256": "6d54456dd316c5fac95ad25488e00674bb095952a58557a722962577a8160c09",
        "archive_member": "artifacts/gh_docs_index.rst.gz",
        "media_type": "text/x-rst",
        "licence": "BSD 3-Clause",
        "publication_status": "official_project_source",
        "source_locator": "Hero paragraph and the 'What you can design' list-table",
    },
    {
        "id": P + "source-docs-site",
        "name": "RFD4-Proteina documentation site, latest, as served on 2026-11-15",
        "description": "The published documentation landing page at rfd4-proteina.org/latest/, retrieved once to confirm the documentation named in the issue resolves and serves the same design-task table as the pinned repository page.",
        "url": "https://rfd4-proteina.org/latest/",
        "retrieval_url": "https://rfd4-proteina.org/latest/",
        "version": "Page as served on 2026-11-15; the site is mutable and 'latest' is a moving pointer",
        "artifact_sha256": "3156b3a2e728a2d656cc0f16bcba75ab088e71641abf8518d502944383becf61",
        "media_type": "text/html",
        "publication_status": "official_project_source",
        "source_locator": "Page title and the rendered 'What you can design' table",
        "limitations": [
            "Mutable site and a moving 'latest' pointer; the hash describes one retrieval, although two retrievals on 2026-11-15 were byte-identical.",
            "Used only to confirm the documentation URL resolves; every documented fact in this batch is taken from the pinned repository files instead.",
        ],
        "missing": {
            "licence": {"reason": "unreported", "note": "The rendered page states no licence of its own."},
        },
    },
    {
        "id": P + "source-rosettacommons-post",
        "name": "RosettaCommons post on the RFD4-Proteina release, 23 October 2026",
        "description": "The RosettaCommons organisation post about the release, which states the model lineage and the collaborating organisations.",
        "url": "https://rosettacommons.org/2026/10/23/rfd4-proteina-improves-computational-protein-design-through-open-science-and-collaboration/",
        "retrieval_url": "https://rosettacommons.org/2026/10/23/rfd4-proteina-improves-computational-protein-design-through-open-science-and-collaboration/",
        "version": "Page as served on 2026-11-15",
        "artifact_sha256": "cb0d0739ef0d8f367f10f910c721ca299ca7a7b24d214f8929373604c9760f6b",
        "media_type": "text/html",
        "publication_status": "official_project_source",
        "source_locator": "Opening section and the section 'Collaborations Across Academia and Industry Lead to Scientific Advancements in Protein Design'",
        "limitations": [
            "An announcement, not a technical source. Used only for the stated lineage and the collaborating organisations; no performance claim rests on it.",
            "Its first mention of the model is spelled 'RDF4-Proteina'; every later mention is 'RFD4-Proteina'.",
            "Reports that early users at the Institute for Protein Design described shorter design timelines, with no measurement, protocol or endpoint behind it; that statement is not recorded as a result.",
            "Mutable page; the hash describes one retrieval, although two retrievals on 2026-11-15 were byte-identical.",
        ],
        "missing": {
            "licence": {"reason": "unreported", "note": "The page states no reuse licence."},
        },
    },
    {
        "id": PREPRINT_ID,
        "name": "Biomolecular design through latent reasoning with RFD4-Proteina, preprint version 3",
        "description": "The 101-page project preprint describing RFD4-Proteina, its architecture, its training stages and its evaluations, retrieved at its versioned URL.",
        "url": "https://rfd4-proteina.org/assets/paper/versions/RFD4-Proteina-v3-20261113T070435Z.pdf",
        "retrieval_url": "https://rfd4-proteina.org/assets/paper/RFD4-Proteina.pdf",
        "version": "Version 3, uploaded 2026-11-13T07:04:35Z",
        "artifact_sha256": "b581fc10da53e94b263c36a7871906f10ba6559f993c02e08f8b3de6b1d0347e",
        "media_type": "application/pdf",
        "article_licence": "CC BY 4.0",
        "publication_status": "preprint",
        "source_locator": "Title page; Sections S4.1 to S4.2 with Tables S11 and S12; Code availability",
        "limitations": [
            "The title page states 'This preprint has not been peer reviewed.'",
            "Self-hosted on the project page: no preprint-server record or DOI was found, so the version history rests on the project's own preprint-versions.json.",
            "Only the title page, the training-stage sections with Tables S11 and S12, and the code-availability statement were read. The supplementary result tables, including Tables S18, S22 and S28, which also report passers per GPU-hour, were not extracted and are a recorded gap.",
        ],
        "missing": {
            "doi": {"reason": "unavailable", "note": "The preprint carries no DOI and is not posted to a preprint server that assigns one."},
        },
        "no_companion": True,
    },
    {
        "id": P + "source-preprint-versions",
        "name": "RFD4-Proteina preprint version manifest as served on 2026-11-15",
        "description": "The project page's own manifest of preprint versions, giving each version's upload time, SHA-256 and stated changes.",
        "url": "https://rfd4-proteina.org/data/preprint-versions.json",
        "retrieval_url": "https://rfd4-proteina.org/data/preprint-versions.json",
        "version": "Manifest as served on 2026-11-15, listing versions 1 to 3",
        "artifact_sha256": "1c6c825a8694c5987d47c03d044385cc38b8a9162e2dbb69d78e9edb5cbc0b4d",
        "archive_sha256": "5cd8ecc74fa2b7ad00fdda194a45fdcf0039c6f0319ee657f5b7ec7512c5907a",
        "archive_member": "artifacts/preprint-versions-live.json.gz",
        "media_type": "application/json",
        "publication_status": "official_project_source",
        "source_locator": "Key 'versions', entries 1, 2 and 3",
        "limitations": [
            "Mutable file on a live site; the hash describes one retrieval, although two retrievals on 2026-11-15 were byte-identical.",
            "The copy of this file committed at the pinned code commit lists only versions 1 and 2, so version 3 is known from the live file alone.",
            "The declared SHA-256 for version 3 matches the retrieved PDF, and the declared SHA-256 for version 2 matched a separate retrieval of the version 2 PDF.",
        ],
        "missing": {
            "licence": {"reason": "unreported", "note": "The file states no licence."},
        },
    },
]

# --- the frozen benchmark, its datasets and its protocols ----------------------------------

BENCHMARK_ID = P + "benchmark-frozen-project-benchmark-20261009"
MODEL_ID = P + "model-rfd4-proteina"
RELEASE_CONFIG_ID = P + "config-release-2026-10-19"
DIFFUSERS_CONFIG_ID = P + "config-diffusers-release-2026-10-19"
PREVIOUS_CONFIG_ID = P + "config-previous-release-high-thinking"

DATASETS = {
    "ppi": {
        "id": P + "dataset-ppi-24-targets",
        "name": "Frozen project benchmark protein-binding target set, 24 targets",
        "description": "The 24 protein-binding design targets of the frozen project benchmark, combining cases from the Proteina-Complex and RFdiffusion3 papers.",
        "targets": 24,
        "scope_note": "The 24 targets combine cases from the Proteina-Complex and RFdiffusion3 papers. The benchmark notes state backbone-only conditioning retains target sequence and backbone coordinates, while all-atom conditioning also supplies target sidechains.",
        "locator": "benchmarks/METHODS.md, 'Common AF3 scoring' table row 'PPI, 24 targets'; benchmarks/summary.csv, panel ppi, column targets",
        "sources": [P + "source-hf-benchmark-methods", P + "source-hf-benchmark-summary"],
    },
    "small_molecule": {
        "id": P + "dataset-small-molecule-77-targets",
        "name": "Frozen project benchmark small-molecule binding target set, 77 targets",
        "description": "The 77 small-molecule binder design entries of the frozen project benchmark, taken from the DISCO Figure 2C set.",
        "targets": 77,
        "scope_note": "77 small-molecule entries, described in the project benchmark notes as the DISCO Figure 2C set of 65 single-target and 12 multi-ligand tasks with protein lengths of 100 to 155 residues; nucleic-acid entries are evaluated separately.",
        "locator": "benchmarks/METHODS.md, 'Common AF3 scoring' table row 'Small molecule, 77 targets'; benchmarks/summary.csv, panel small_molecule, column targets",
        "sources": [P + "source-hf-benchmark-methods", P + "source-hf-benchmark-summary"],
    },
    "ame": {
        "id": P + "dataset-ame-37-targets",
        "name": "Frozen project benchmark Atomic Motif Enzyme target set, 37 tasks",
        "description": "The 37 Atomic Motif Enzyme scaffolding tasks of the frozen project benchmark, out of 41, with four excluded for input representation or missing experimental coordinates.",
        "targets": 37,
        "scope_note": "Both ligand conditions use the same 37 of 41 Atomic Motif Enzyme tasks. The four exclusions are stated to concern input representation or missing observed coordinates, not model performance.",
        "locator": "benchmarks/METHODS.md, 'Common AF3 scoring' table row 'Atomic Motif Enzyme (AME), 37 targets'; benchmarks/summary.csv, panel ame, column targets",
        "sources": [P + "source-hf-benchmark-methods", P + "source-hf-benchmark-summary"],
    },
    "dna": {
        "id": P + "dataset-dna-3-targets",
        "name": "Frozen project benchmark DNA-binding target set, 3 targets",
        "description": "The three DNA-binding design targets of the frozen project benchmark, with 120 to 150 residue protein binders.",
        "targets": 3,
        "scope_note": "Three targets. The project benchmark notes name them 7m5w, 7n5u and 7rte, taken from a published generative DNA-binding protein study, with 120 to 150 residue protein binders in both conditions.",
        "locator": "benchmarks/METHODS.md, 'Common AF3 scoring' table row 'DNA, 3 targets'; benchmarks/summary.csv, panel dna, column targets",
        "sources": [P + "source-hf-benchmark-methods", P + "source-hf-benchmark-summary"],
    },
}

PASS_CRITERIA = {
    "ppi": (
        "AF3 binder pTM at least 80 on the native 0 to 100 scale, minimum interface PAE at most 1.5 A, "
        "and target-backbone-aligned binder backbone RMSD at most 2.5 A, with valid required target "
        "mapping and conditioning"
    ),
    "small_molecule": (
        "AF3 minimum interface PAE at most 1.5 A, chain-of-interest ipTM at least 80 out of 100, "
        "protein-backbone RMSD at most 1.5 A, and protein-backbone-aligned ligand RMSD at most 5 A "
        "(the sm_binder criterion, not the looser historical disco criterion)"
    ),
    "ame": (
        "protein-backbone RMSD at most 2 A, required motif all-atom RMSD at most 1.5 A, and AF3 minimum "
        "interface PAE below 1.5 A"
    ),
    "dna": (
        "AF3 minimum interface PAE at most 1.5 A and DNA-target-aligned binder backbone RMSD at most 8 A, "
        "aligning on all target DNA atoms in both the fixed and unfixed modes"
    ),
}

PROTOCOLS = {
    "ppi_backbone": {
        "id": P + "protocol-ppi-backbone-passers-per-gpu-hour",
        "name": "Frozen project benchmark protein binding, backbone conditioning: distinct passers per GPU-hour",
        "panel": "ppi",
        "dataset": "ppi",
        "conditioning": "Backbone conditioning: the target sequence and backbone coordinates are supplied, target sidechains are not.",
        "arm": "ppi_backbone",
    },
    "ppi_all_atom": {
        "id": P + "protocol-ppi-all-atom-passers-per-gpu-hour",
        "name": "Frozen project benchmark protein binding, all-atom conditioning: distinct passers per GPU-hour",
        "panel": "ppi",
        "dataset": "ppi",
        "conditioning": "All-atom conditioning: the target sequence, backbone coordinates and sidechains are supplied.",
        "arm": "ppi_all_atom",
    },
    "small_molecule_unfixed": {
        "id": P + "protocol-small-molecule-unfixed-passers-per-gpu-hour",
        "name": "Frozen project benchmark small-molecule binding, unfixed ligand: distinct passers per GPU-hour",
        "panel": "small_molecule",
        "dataset": "small_molecule",
        "conditioning": "Unfixed-ligand conditioning: the ligand position is not held fixed. The benchmark notes record that fixed-ligand routes are a separate arm.",
        "arm": "studio_figure_2c_unfixed",
    },
    "ame_fixed": {
        "id": P + "protocol-ame-fixed-ligand-passers-per-gpu-hour",
        "name": "Frozen project benchmark Atomic Motif Enzyme, fixed ligand: distinct passers per GPU-hour",
        "panel": "ame",
        "dataset": "ame",
        "conditioning": "Fixed-ligand conditioning. The methods supplement states that 'partially fixed' refers to ligand conditioning and that catalytic motif constraints are present in both conditions.",
        "arm": "mcsa_fixed",
    },
    "dna_unfixed": {
        "id": P + "protocol-dna-unfixed-passers-per-gpu-hour",
        "name": "Frozen project benchmark DNA binding, unfixed DNA: distinct passers per GPU-hour",
        "panel": "dna",
        "dataset": "dna",
        "conditioning": "Unfixed-DNA conditioning: the DNA sequence is specified and its geometry may change.",
        "arm": "dna_unfixed",
    },
    "dna_fixed": {
        "id": P + "protocol-dna-fixed-passers-per-gpu-hour",
        "name": "Frozen project benchmark DNA binding, fixed DNA: distinct passers per GPU-hour",
        "panel": "dna",
        "dataset": "dna",
        "conditioning": "Fixed-DNA conditioning: the DNA sequence and its coordinates are both specified.",
        "arm": "dna_fixed",
    },
}

METRIC = "passing-design-clusters-per-accelerator-hour"
UNIT = "count-per-hour"
UNIT_DETAIL = (
    "structurally distinct computational passers per GPU-hour, counting generation time and common "
    "AlphaFold3 evaluation time"
)

# Which configuration and protocol each printed cell belongs to, and the printed name in the cell.
CELLS = [
    {
        "row": "Protein binders",
        "side": "rfd4",
        "config": PREVIOUS_CONFIG_ID,
        "protocol": "ppi_backbone",
        "reported_name": "RFD4-Proteina, high thinking",
        "column": "RFD4-Proteina, high thinking",
    },
    {
        "row": "Protein binders",
        "side": "other",
        "config": P + "config-proteina-complexa-ppi",
        "protocol": "ppi_all_atom",
        "reported_name": "Proteina-Complexa",
        "column": "Best other method in this comparison",
    },
    {
        "row": "Small-molecule binders",
        "side": "rfd4",
        "config": PREVIOUS_CONFIG_ID,
        "protocol": "small_molecule_unfixed",
        "reported_name": "RFD4-Proteina, high thinking",
        "column": "RFD4-Proteina, high thinking",
    },
    {
        "row": "Small-molecule binders",
        "side": "other",
        "config": P + "config-boltzgen",
        "protocol": "small_molecule_unfixed",
        "reported_name": "BoltzGen",
        "column": "Best other method in this comparison",
    },
    {
        "row": "Atomic Motif Enzyme",
        "side": "rfd4",
        "config": PREVIOUS_CONFIG_ID,
        "protocol": "ame_fixed",
        "reported_name": "RFD4-Proteina, high thinking",
        "column": "RFD4-Proteina, high thinking",
    },
    {
        "row": "Atomic Motif Enzyme",
        "side": "other",
        "config": P + "config-alphaprotein-novo-codesign",
        "protocol": "ame_fixed",
        "reported_name": "AlphaProtein-novo (Codesign)",
        "column": "Best other method in this comparison",
    },
    {
        "row": "DNA binders",
        "side": "rfd4",
        "config": PREVIOUS_CONFIG_ID,
        "protocol": "dna_unfixed",
        "reported_name": "RFD4-Proteina, high thinking",
        "column": "RFD4-Proteina, high thinking",
    },
    {
        "row": "DNA binders",
        "side": "other",
        "config": P + "config-boltzgen",
        "protocol": "dna_fixed",
        "reported_name": "BoltzGen (fixed DNA)",
        "column": "Best other method in this comparison",
    },
]

SLUG = {
    "Protein binders": "protein-binders",
    "Small-molecule binders": "small-molecule-binders",
    "Atomic Motif Enzyme": "atomic-motif-enzyme",
    "DNA binders": "dna-binders",
}

CONFIG_SLUG = {
    PREVIOUS_CONFIG_ID: "rfd4-proteina-high-thinking",
    P + "config-proteina-complexa-ppi": "proteina-complexa",
    P + "config-boltzgen": "boltzgen",
    P + "config-alphaprotein-novo-codesign": "alphaprotein-novo-codesign",
}


def review(methods: list[str], artifact_sha256: str, retrieval_url: str, note: str, method_note: str | None = None) -> dict:
    out = {
        "method": methods,
        "reviewer": REVIEWER,
        "reviewer_note": REVIEWER_NOTE,
        "date": DATE,
        "artifact_sha256": artifact_sha256,
        "retrieval_url": retrieval_url,
        "note": note,
    }
    if method_note:
        out["method_note"] = method_note
    return out


CARD_SHA = "38479d8e4c6e46ed7e1ec4ece0dd02c358ae46d73d56790c44be813201fd9b98"
CARD_URL = "https://huggingface.co/nvidia/RFD4-Proteina/raw/" + HF_REVISION + "/README.md"
PARSE_NOTE = (
    "Parsed from the gzipped model card archived in artifacts/ by extract/parse_efficiency_table.py, "
    "which checks the archive against the pinned artifact hash, asserts the four printed row labels "
    "and the four printed header cells, and requires every value to be printed to two decimals. Each "
    "value was then cross-checked against benchmarks/summary.csv from the same pinned revision, which "
    "prints the same quantity per 10 GPU-minutes: every card value equals its summary.csv row times "
    "six at the printed precision, and the attempts column of each row equals its targets times the "
    "200 attempts per target the card states."
)


def source_record(spec: dict) -> dict:
    attributes = {
        "url": spec["url"],
        "retrieval_url": spec["retrieval_url"],
        "version": spec["version"],
        "retrieved_at": RETRIEVED_AT,
        "artifact_sha256": spec["artifact_sha256"],
        "media_type": spec["media_type"],
        "publication_status": spec["publication_status"],
        "source_locator": spec["source_locator"],
        "review": review(
            ["source-hash-verification", "automated-source-review"],
            spec["artifact_sha256"],
            spec["retrieval_url"],
            "Retrieved twice on 2026-11-15 with identical bytes; the hash is of the retrieved artifact, not of a text layer.",
        ),
    }
    for key in ("archive_sha256", "archive_member", "licence", "article_licence", "code_url", "limitations"):
        if key in spec:
            attributes[key] = spec[key]
    if "missing" in spec:
        attributes["missing_metadata"] = spec["missing"]
    links = [] if spec.get("no_companion") else [{"relation": "companion_of", "target_id": PREPRINT_ID}]
    return {
        "id": spec["id"],
        "kind": "source",
        "name": spec["name"],
        "description": spec["description"],
        "status": "source_checked",
        "facets": FACETS_PLAIN,
        "source_ids": [],
        "links": links,
        "attributes": attributes,
    }


ALL_SOURCE_IDS = sorted(s["id"] for s in SOURCES)


def main() -> int:
    table = json.loads((HERE / "efficiency-table.json").read_text(encoding="utf-8"))
    rows = {r["benchmark_label"]: r for r in table["rows"]}
    checks = table["summary_cross_check"]
    records: list[dict] = []

    for spec in SOURCES:
        records.append(source_record(spec))

    # ---- model -----------------------------------------------------------------------------
    records.append(
        {
            "id": MODEL_ID,
            "kind": "model",
            "name": "RFD4-Proteina",
            "description": (
                "Generates protein and biomolecular sequences together with all-atom coordinates using a "
                "flow-matching latent model paired with an autoencoder, conditioned on the molecular "
                "context a design must preserve, such as a binding target, an enzyme motif or a ligand."
            ),
            "status": "source_checked",
            "facets": FACETS_MODEL,
            "source_ids": ALL_SOURCE_IDS,
            "links": [],
            "attributes": {
                "entity_level": "family",
                "reported_name": "RFD4-Proteina",
                "access": (
                    "Code at https://github.com/RosettaCommons/RFD4-Proteina, weights at "
                    "https://huggingface.co/nvidia/RFD4-Proteina, documentation at https://rfd4-proteina.org/latest/. "
                    "Public repositories need no authentication. Two hosted Hugging Face Spaces are also offered and "
                    "require a Hugging Face sign-in."
                ),
                "licence": (
                    "BSD 3-Clause for the RFD4-Proteina model, weights and code, Copyright (c) 2026, Institute for "
                    "Protein Design, University of Washington. Optional third-party refolding assets and the training "
                    "data carry separate terms."
                ),
                "training_data": (
                    "Described on the companion Hugging Face dataset card, which the model card says should not be read "
                    "as the exact training history of every checkpoint. The preprint states the unified autoencoder was "
                    "trained from scratch with 256-token crops and the flow model pretrained to 320,000 optimizer steps "
                    "and then fine-tuned with LoRA."
                ),
                "provenance_note": (
                    "Registered from the pinned repository commit, the pinned Hugging Face model revision, the pinned "
                    "documentation pages and the project preprint version 3. Kept at family level because the project "
                    "publishes dated release pairs, which are registered as configurations."
                ),
                "source_locator": (
                    "Hugging Face model card, 'RFD4-Proteina' opening paragraph and 'At a glance'; repository README, "
                    "subtitle and 'Try it now'; documentation index, hero paragraph"
                ),
                "review": review(
                    ["automated-source-review", "source-hash-verification"],
                    CARD_SHA,
                    CARD_URL,
                    "Identity, access, licence scope and training-data pointer read from the pinned artifacts; no checkpoint-level identity is asserted on this record.",
                ),
                "missing_metadata": {
                    "version": {
                        "reason": "inapplicable",
                        "note": "The family record covers every release; the dated release pairs are registered as configurations.",
                    },
                    "checkpoint_revision": {
                        "reason": "inapplicable",
                        "note": "Checkpoint revisions belong to the configuration records, not to the family.",
                    },
                },
            },
        }
    )

    # ---- configurations --------------------------------------------------------------------
    records.append(
        {
            "id": RELEASE_CONFIG_ID,
            "kind": "configuration",
            "name": "RFD4-Proteina 2026-10-19 release pair, native bundle",
            "description": (
                "Configures RFD4-Proteina for generation from the matched 2026-10-19 flow model and "
                "autoencoder, loaded as the native Hugging Face bundle with 32 latent channels per "
                "residue and a 147-class residue vocabulary."
            ),
            "status": "source_checked",
            "facets": FACETS_MODEL,
            "source_ids": [
                P + "source-hf-model-card",
                P + "source-hf-release-checkpoints",
                P + "source-github-checkpoints-doc",
                P + "source-github-readme",
                P + "source-github-docs-index",
                PREPRINT_ID,
            ],
            "links": [{"relation": "configuration_of", "target_id": MODEL_ID}],
            "attributes": {
                "configuration_type": "paper_evaluation",
                "reported_name": "RFD4-Proteina",
                "version": "2026-10-19 release pair",
                "checkpoint": (
                    "Denoiser rfd4-proteina-flow-release-2026-10-19.ckpt with autoencoder "
                    "rfd4-proteina-ae-release-2026-10-19.ckpt, published as the stable filenames "
                    "flow_checkpoints/rfd4_proteina_flow-ema.ckpt and ae_checkpoints/rfd4_proteina_ae-ema.ckpt"
                ),
                "checkpoint_revision": HF_REVISION,
                "checkpoint_sha256": "c1c8b7068e87c41a334ec5b77e7d7cdda30bd31ed4504909d93bd72f7742afe4",
                "weights_sha256": "5b549dd61adb2f6c6b5cb95bda13f40f5e31556b4e6c755edc0ca6f011c68fb0",
                "resources_sha256": {
                    "flow_checkpoints/rfd4_proteina_flow-ema.ckpt": "c1c8b7068e87c41a334ec5b77e7d7cdda30bd31ed4504909d93bd72f7742afe4",
                    "ae_checkpoints/rfd4_proteina_ae-ema.ckpt": "24536372f3fc9a5083b6b813baa80630d2287a5d61fbf2f126c9735802e1d21a",
                    "flow_checkpoints/rfd4_proteina_flow_pretrain-ema.ckpt": "561bbbe3e97f37ded11ddc934ff2184adcd98038396f7aa1f16e6f9d57f0f8b2",
                    "model.safetensors": "5b549dd61adb2f6c6b5cb95bda13f40f5e31556b4e6c755edc0ca6f011c68fb0",
                    "base/model.safetensors": "10e90a76e3b09c94a700d2f67e89ed660af7f3018e3f2209b5d52f24d00fbd39",
                    "adapter/adapter_model.safetensors": "3b0762a73b543dfd88958267ba93a729fd91b31f2e18dba2d34c302260f50402",
                },
                "parameters": "435,622,465 stored parameters across the paired bundle, in FP32; 1.74 GB for model.safetensors",
                "representation": "32 latent channels per residue; 147-class residue vocabulary covering proteins, RNA, DNA and modified residues",
                "runtime": (
                    "RFD4 Python package on Linux x86_64 with Python 3.12 and an NVIDIA GPU with a CUDA 13-compatible "
                    "driver; torch.compile by default with an optional BioIR backend"
                ),
                "code_commit": CODE_COMMIT,
                "limitations": [
                    "The flow model and the autoencoder are a matched pair. Mixing a flow model with a different release's autoencoder is stated to produce nonsense rather than an error.",
                    "The published checkpoints hold exponential-moving-average weights and hyperparameters only, so they initialize weights for inference or fine-tuning and do not resume a training run.",
                    "An unannotated structure is not a complete design specification: the annotations are what state which atoms and residues to preserve.",
                    "No result in this batch is attached to this configuration. The published efficiency table states it was measured on the previous release pair.",
                ],
                "provenance_note": (
                    "Checkpoint filenames, hashes, latent dimension, vocabulary size and parameter count taken from the "
                    "pinned model card and its release-checkpoints.json at Hugging Face revision " + HF_REVISION + "."
                ),
                "source_locator": (
                    "Hugging Face model card, 'At a glance' and 'Checkpoints in this release'; release-checkpoints.json, "
                    "keys checkpoints, bundles, adapters and policy; checkpoints reference, 'Types of checkpoints' and "
                    "'Released checkpoints'"
                ),
                "review": review(
                    ["automated-source-review", "source-hash-verification"],
                    CARD_SHA,
                    CARD_URL,
                    "Checkpoint identity and hashes transcribed from the pinned manifest; no checkpoint file was downloaded, so no weight hash was verified against the published value.",
                ),
                "missing_metadata": {
                    "hyperparameters": {
                        "reason": "inapplicable",
                        "note": "Sampling settings belong to a generation run, not to the released pair; the published recycling presets are recorded as a claim.",
                    },
                },
            },
        }
    )

    records.append(
        {
            "id": DIFFUSERS_CONFIG_ID,
            "kind": "configuration",
            "name": "RFD4-Proteina 2026-10-19 release pair, Diffusers pipeline",
            "description": (
                "Configures the same 2026-10-19 RFD4-Proteina release to run as a Hugging Face Diffusers "
                "pipeline, with the weights re-prefixed and split across a transformer and a vae folder "
                "in a separate Hub repository."
            ),
            "status": "source_checked",
            "facets": FACETS_MODEL,
            "source_ids": [P + "source-hf-model-card", P + "source-github-readme"],
            "links": [
                {"relation": "configuration_of", "target_id": MODEL_ID},
                {"relation": "uses_model", "target_id": MODEL_ID},
            ],
            "attributes": {
                "configuration_type": "reported_configuration",
                "reported_name": "RFD4-Proteina-Diffusers",
                "version": "Same 2026-10-19 release, served from nvidia/RFD4-Proteina-Diffusers",
                "runtime": (
                    "RFD4ProteinaPipeline in Hugging Face Diffusers, merged into Diffusers on 2026-10-20 and shipping "
                    "in the next release; until then Diffusers is installed from GitHub. Annotated-CIF preprocessing "
                    "comes from the separate nvidia/RFD4-Proteina-prep package."
                ),
                "model_identity_note": (
                    "The card states it is one model throughout and nothing is retrained: the Diffusers weights are the "
                    "same tensors re-prefixed and split across transformer/ and vae/, in a separate repository only "
                    "because Diffusers requires model_index.json at the root."
                ),
                "limitations": [
                    "Partial diffusion and inverse folding are stated to work in this port; the card does not say the port covers every native workflow.",
                    "No result in this batch was measured through this package.",
                ],
                "provenance_note": "Registered from the entry-point table and the Diffusers section of the pinned model card.",
                "source_locator": "Hugging Face model card, 'Where to find each entry point' table and 'Loading the model' / 'Diffusers'",
                "review": review(
                    ["automated-source-review", "source-hash-verification"],
                    CARD_SHA,
                    CARD_URL,
                    "Recorded as a second runtime package of the same release, not as a second model, because the card states the tensors are identical and nothing is retrained.",
                ),
                "missing_metadata": {
                    "checkpoint_sha256": {
                        "reason": "unreported",
                        "note": "The card gives no hashes for the Diffusers repository's files.",
                    },
                    "checkpoint_revision": {
                        "reason": "unreported",
                        "note": "No revision of nvidia/RFD4-Proteina-Diffusers is pinned on the card, and that repository was not retrieved in this pass.",
                    },
                },
            },
        }
    )

    records.append(
        {
            "id": PREVIOUS_CONFIG_ID,
            "kind": "configuration",
            "name": "RFD4-Proteina (high thinking), previous release pair",
            "description": (
                "Configures RFD4-Proteina for one-shot generation with the high-thinking recycling "
                "schedule on the flow and autoencoder pair that preceded the 2026-10-19 release."
            ),
            "status": "source_checked",
            "facets": FACETS_MODEL,
            "source_ids": [
                P + "source-hf-model-card",
                P + "source-hf-benchmark-methods",
                P + "source-hf-benchmark-summary",
                P + "source-hf-benchmark-provenance",
            ],
            "links": [{"relation": "configuration_of", "target_id": MODEL_ID}],
            "attributes": {
                "configuration_type": "paper_evaluation",
                "reported_name": "RFD4-Proteina, high thinking",
                "benchmark_method_label": "RFD4-Proteina (high thinking)",
                "version": "The release pair preceding 2026-10-19, as the model card names it; no checkpoint filename is tied to the efficiency table",
                "selection": "One-shot generation: a single draw per attempt, with no reward-guided search and no intrinsic selection stage",
                "hyperparameters": (
                    "High-thinking recycling schedule, the front-loaded bands [[10,9],[10,8],[10,5],[20,3],[10,2]] over "
                    "60 steps for 300 trunk passes, selected in the native runtime as "
                    "recycle_strategy=thinking_high. The card states the released recipes differ only in how often the "
                    "trunk is recycled per sampling step."
                ),
                "model_identity_note": (
                    "The efficiency table's scope note says only that the numbers were measured on 'the previous release "
                    "pair', in the October 9, 2026 frozen project benchmark. The same card's checkpoint table has a "
                    "column headed 'Previous release' naming the flow checkpoint "
                    "chk_epoch_00000169_step_000000340000-ema with the autoencoder 2026_09_04_release_ae_z16_400k-ema, "
                    "latent dimension 16, 33 residue classes and 434,348,737 stored parameters; the same card also says "
                    "the 2026-10-19 pair supersedes a 2026-10-15 pair "
                    "(2026_10_15_hero_s43_c512_80k-ema and 2026_10_15_unified_ae_s43_400k-ema). Neither candidate is "
                    "named in the table or its scope note, and the benchmark methods supplement states that the exact "
                    "schedule and checkpoint of each cohort come from its own native config, which the packet does not "
                    "publish. The identity is therefore left as the source gives it and the two candidate pairs are "
                    "recorded for the reviewer to rule on."
                ),
                "limitations": [
                    "This is not the 2026-10-19 release. The card states the table's numbers have not been re-measured on the current release and should not be read as describing it.",
                    "No checkpoint filename, hash or Hugging Face revision is tied to the table, so the configuration cannot be rerun as published.",
                ],
                "provenance_note": (
                    "Registered to carry the efficiency table's RFD4-Proteina rows without attaching them to the "
                    "2026-10-19 release, whose own configuration record is "
                    + RELEASE_CONFIG_ID
                    + "."
                ),
                "source_locator": (
                    "Hugging Face model card, 'Measured design efficiency' scope note and table, 'Checkpoints in this "
                    "release' table and 'Compute presets' table; benchmarks/METHODS.md, 'Model recipes and adaptations' "
                    "row RFD4-Proteina"
                ),
                "review": review(
                    ["automated-source-review", "source-hash-verification"],
                    CARD_SHA,
                    CARD_URL,
                    "The checkpoint identity is deliberately left at the wording the source uses. Nothing was inferred about which named pair the table was measured on.",
                ),
                "missing_metadata": {
                    "checkpoint": {
                        "reason": "conflicting",
                        "note": "The card names a 'Previous release' pair and separately a superseded 2026-10-15 pair, and ties neither to the efficiency table.",
                    },
                    "checkpoint_sha256": {
                        "reason": "unreported",
                        "note": "No hash is published for the pair the table was measured on.",
                    },
                    "checkpoint_revision": {
                        "reason": "unreported",
                        "note": "No Hugging Face revision is given for the pair the table was measured on.",
                    },
                    "code_commit": {
                        "reason": "unreported",
                        "note": "The benchmark packet gives a paper commit for the supplement, not a code commit for the generation runs.",
                    },
                },
            },
        }
    )

    comparators = [
        {
            "id": P + "config-proteina-complexa-ppi",
            "name": "Proteina-Complexa (V1), protein binding, all-atom conditioning",
            "description": (
                "Configures Proteina-Complexa for protein-binder design with one 400-step joint draw and "
                "no additional sequence design or selection, taking native atom37 and template features "
                "with residue-projected hotspots."
            ),
            "reported_name": "Proteina-Complexa",
            "settings": (
                "One 400-step joint draw, no additional LigandMPNN step and no selection. The protein-binding arm uses "
                "V1 weights. Protein-binding inputs use native atom37 and template features with residue-projected "
                "hotspots."
            ),
            "locator": (
                "Hugging Face model card, 'Measured design efficiency' table, row 'Protein binders', column 'Best other "
                "method in this comparison'; benchmarks/METHODS.md, 'Model recipes and adaptations' row Proteina-Complexa"
            ),
            "note": "The methods supplement states Proteina-Complexa has no DNA route and no fully unfixed ligand route, and that its small-molecule route uses fixed ligands.",
        },
        {
            "id": P + "config-boltzgen",
            "name": "BoltzGen, frozen project benchmark recipe",
            "description": (
                "Configures BoltzGen for binder design with 500 design steps over 3 recycles, inverse "
                "folding at 200 steps over 3 recycles and one final sequence, with no terminal folding, "
                "filtering or ranking."
            ),
            "reported_name": "BoltzGen",
            "settings": (
                "Design at 500 steps and 3 recycles; inverse folding at 200 steps and 3 recycles with one final "
                "sequence. Original indices 0 to 99 use the diverse setting and 100 to 199 the adherence setting. No "
                "terminal folding, filtering or ranking. Atom hotspots become residue hotspots and protein-binding "
                "inputs are all-atom."
            ),
            "locator": (
                "Hugging Face model card, 'Measured design efficiency' table, rows 'Small-molecule binders' and 'DNA "
                "binders', column 'Best other method in this comparison'; benchmarks/METHODS.md, 'Model recipes and "
                "adaptations' row BoltzGen"
            ),
            "note": (
                "One configuration carries both printed BoltzGen cells. The card prints 'BoltzGen' for small-molecule "
                "binders and 'BoltzGen (fixed DNA)' for DNA binders; the difference is the DNA conditioning arm, which "
                "is held on the protocol, and each result keeps its own printed name."
            ),
        },
        {
            "id": P + "config-alphaprotein-novo-codesign",
            "name": "AlphaProtein-novo (Codesign), Atomic Motif Enzyme",
            "description": (
                "Configures AlphaProtein-novo for enzyme motif scaffolding as a native 1000-step joint "
                "codesign draw, without the paired sequence-design arm."
            ),
            "reported_name": "AlphaProtein-novo (Codesign)",
            "settings": (
                "Native 1000-step joint codesign. The separate paired arm that adds one LigandMPNN sequence at "
                "temperature 0.1 is a different row and is not this configuration."
            ),
            "locator": (
                "Hugging Face model card, 'Measured design efficiency' table, row 'Atomic Motif Enzyme', column 'Best "
                "other method in this comparison'; benchmarks/METHODS.md, 'Model recipes and adaptations' row "
                "AlphaProtein-novo"
            ),
            "note": (
                "The methods supplement records that this method's handling of one composite-ligand case changes the "
                "interface interpretation, and that its two arms share original scaffolds and are not independent "
                "samples."
            ),
        },
    ]

    for spec in comparators:
        records.append(
            {
                "id": spec["id"],
                "kind": "configuration",
                "name": spec["name"],
                "description": spec["description"],
                "status": "source_checked",
                "facets": FACETS_PLAIN,
                "source_ids": [P + "source-hf-model-card", P + "source-hf-benchmark-methods", P + "source-hf-benchmark-summary"],
                "links": [],
                "attributes": {
                    "configuration_type": "reported_configuration",
                    "reported_name": spec["reported_name"],
                    "hyperparameters": spec["settings"],
                    "model_identity_note": (
                        "A comparator row of the frozen project benchmark. No model record is created for it in this "
                        "batch: no primary source for this method was retrieved, and the store holds none. "
                        + spec["note"]
                    ),
                    "limitations": [
                        "Run by the RFD4-Proteina authors, not by this method's developers.",
                        "The methods supplement states that the release does not assert that all models were equally optimized.",
                    ],
                    "provenance_note": (
                        "Registered to carry one printed comparator cell of the published efficiency table, with the "
                        "recipe taken from the benchmark methods supplement at the same pinned revision."
                    ),
                    "source_locator": spec["locator"],
                    "review": review(
                        ["automated-source-review", "deterministic-table-parse", "source-hash-verification"],
                        CARD_SHA,
                        CARD_URL,
                        "Printed comparator name taken from the table cell by the parser; recipe read from the methods supplement.",
                    ),
                    "missing_metadata": {
                        "checkpoint": {
                            "reason": "unreported",
                            "note": "The benchmark packet names no checkpoint file or revision for this comparator.",
                        },
                        "version": {
                            "reason": "unreported",
                            "note": "No version is printed for this comparator in the card or the methods supplement.",
                        },
                        "code_commit": {
                            "reason": "unreported",
                            "note": "The methods supplement links the method's repository but pins no commit.",
                        },
                    },
                },
            }
        )

    # ---- benchmark -------------------------------------------------------------------------
    records.append(
        {
            "id": BENCHMARK_ID,
            "kind": "benchmark",
            "name": "RFD4-Proteina frozen project benchmark, October 9 2026 supplement",
            "description": (
                "The frozen benchmark packet published with RFD4-Proteina, which scores design methods on "
                "four target sets with a common AlphaFold3 evaluation and reports pass rates and "
                "efficiency per GPU-hour."
            ),
            "status": "source_checked",
            "facets": FACETS_PLAIN,
            "source_ids": [
                P + "source-hf-model-card",
                P + "source-hf-benchmark-provenance",
                P + "source-hf-benchmark-methods",
                P + "source-hf-benchmark-summary",
            ],
            "links": [],
            "attributes": {
                "entity_level": "suite",
                "version": "supplement-20261009, from paper commit 8614542c149875b13ed3fed5d8d6ec739f2daff4",
                "task": "Conditioned biomolecular binder and enzyme-scaffold design, scored by a common AlphaFold3 evaluation and by efficiency per GPU-hour",
                "executable_suite": False,
                "scope_note": (
                    "Four target sets: 24 protein-binding targets, 77 small-molecule binding entries, 37 Atomic Motif "
                    "Enzyme tasks and 3 DNA-binding targets. Each model, protocol and target has 200 original attempts, "
                    "including native failures, with no replacement of rejected originals. The provenance file states "
                    "the scope as 'Frozen project benchmark runs; not a new evaluation of every model Hub revision', "
                    "and the methods supplement states the release uses frozen cohorts rather than every run in the live "
                    "catalog, excluding antibody, HalluDesign, full-pipeline BindCraft and Genie3 search arms."
                ),
                "limitations": [
                    "Built and run by the RFD4-Proteina authors, who are also the authors of the best-performing method in it.",
                    "The published efficiency table counts computational passers, which the card states do not establish experimental activity.",
                    "Conditioning differs between some rows: protein binding compares RFD4 backbone conditioning with all-atom conditioning for several baselines, and DNA compares unfixed RFD4 inputs with fixed-DNA baselines.",
                    "Only three DNA targets are included.",
                    "The methods supplement records timing exceptions, including an approved backbone timing proxy with no measured AlphaFold3 cost for the historical protein-binding all-atom RFD4 arm, and batched remeasurements rather than batch-1 wall time for one comparator's fixed-small-molecule costs.",
                    "The exact schedule and checkpoint of each cohort are stated to come from its own native config, which the packet does not publish, so no row is tied to a named checkpoint file.",
                    "Not executable as published: the packet publishes summary and per-target rows, not a runner.",
                    "No wet-lab endpoint: every pass criterion is computational and is defined by the packet itself.",
                ],
                "source_locator": (
                    "benchmarks/provenance.json, keys source_release, paper_commit, metric and scope; "
                    "benchmarks/METHODS.md, 'Supplement methods' opening, 'Common accounting and timing' and 'Common AF3 "
                    "scoring'; Hugging Face model card, 'Measured design efficiency'"
                ),
                "review": review(
                    ["automated-source-review", "source-hash-verification"],
                    "4e7a3051a58902cc7713d02c52941894eb9581b82e5af85a3b4f256f1a258336",
                    "https://huggingface.co/nvidia/RFD4-Proteina/raw/" + HF_REVISION + "/benchmarks/provenance.json",
                    "The SHA-256 the provenance file declares for summary.csv equals the hash of the retrieved summary.csv, so the packet is internally consistent.",
                ),
                "missing_metadata": {
                    "split": {
                        "reason": "inapplicable",
                        "note": "An evaluation-only target set with no train or test split.",
                    },
                    "runner": {
                        "reason": "unavailable",
                        "note": "No runner or harness is published with the packet; it publishes result tables and per-target rows.",
                    },
                },
            },
        }
    )

    # ---- datasets --------------------------------------------------------------------------
    for spec in DATASETS.values():
        records.append(
            {
                "id": spec["id"],
                "kind": "dataset",
                "name": spec["name"],
                "description": spec["description"],
                "status": "source_checked",
                "facets": FACETS_PLAIN,
                "source_ids": spec["sources"],
                "links": [],
                "attributes": {
                    "total_targets": spec["targets"],
                    "scope_note": spec["scope_note"],
                    "split": "Evaluation only; every target scored",
                    "assay": "In silico design and structure-prediction scoring; no wet-lab assay",
                    "access": (
                        "Per-target rows are published as benchmarks/source_data.csv in the pinned Hugging Face model "
                        "repository. That file was not retrieved in this pass, so no input structure or target list was "
                        "downloaded or hashed."
                    ),
                    "source_locator": spec["locator"],
                    "review": review(
                        ["automated-source-review", "source-hash-verification"],
                        "46d1e181c495d4ecc9a3992a4e7f3cd8fae0b4904fb799ab5c1a883090ca837b",
                        "https://huggingface.co/nvidia/RFD4-Proteina/raw/" + HF_REVISION + "/benchmarks/METHODS.md",
                        "Target count read from the pass-criteria table and cross-checked against the targets column of every summary.csv row in this panel.",
                    ),
                    "missing_metadata": {
                        "accession": {
                            "reason": "unreported",
                            "note": "No accession or archive DOI is given for the target set as a whole.",
                        },
                        "version": {
                            "reason": "unreported",
                            "note": "The packet gives no version for the target set beyond the frozen supplement release it belongs to.",
                        },
                        "manifest": {
                            "reason": "unextracted",
                            "note": "benchmarks/source_data.csv holds the per-target rows and was not retrieved in this pass.",
                        },
                    },
                },
            }
        )

    # ---- protocols -------------------------------------------------------------------------
    for key, spec in PROTOCOLS.items():
        panel = spec["panel"]
        records.append(
            {
                "id": spec["id"],
                "kind": "protocol",
                "name": spec["name"],
                "description": (
                    "Mean over targets of structurally distinct computational passers per GPU-hour on the "
                    + DATASETS[spec["dataset"]]["name"].lower()
                    + ", under "
                    + spec["conditioning"].split(":")[0].lower()
                    + ", with 200 original attempts per target."
                ),
                "status": "source_checked",
                "facets": FACETS_PLAIN,
                "source_ids": [
                    P + "source-hf-model-card",
                    P + "source-hf-benchmark-methods",
                    P + "source-hf-benchmark-provenance",
                    P + "source-hf-benchmark-summary",
                ],
                "links": [
                    {"relation": "part_of", "target_id": BENCHMARK_ID},
                    {"relation": "uses_data", "target_id": DATASETS[spec["dataset"]]["id"]},
                ],
                "attributes": {
                    "metric": METRIC,
                    "metric_direction": "higher",
                    "unit": UNIT,
                    "unit_detail": UNIT_DETAIL,
                    "metric_qualifier": metric_qualifier(panel),
                    "metric_definition": (
                        "The card prints the metric as '"
                        + table["metric_definition"]
                        + "'. The provenance file gives the expression "
                        + "mean_over_targets(3600 * passing_structure_clusters / (generation_gpu_s + af3_gpu_s)). "
                        + "The methods supplement defines the default efficiency as the arithmetic mean across targets "
                        + "of successes divided by generation plus AlphaFold3 GPU time, and publishes it per 10 GPU-minutes."
                    ),
                    "metric_implementation": (
                        "generation_gpu_s is the complete stored warm generation cost, including required sequence "
                        "design and intrinsic folding or search, and excluding setup, loading, warmup and compilation "
                        "where separately measured. af3_gpu_s is the separate common evaluation time. Batched costs are "
                        "amortized across the batch's originals."
                    ),
                    "aggregation": "Arithmetic mean of target-level rates, not a pooled total and not single-design latency",
                    "allowed_information": spec["conditioning"],
                    "denominator": DATASETS[spec["dataset"]]["targets"] * table["attempts_per_target"],
                    "procedure": (
                        "200 original attempts per model, protocol and target, including native failures and unmatched "
                        "required motifs. Rejected originals are not replaced and failed attempts keep their consumed "
                        "time. Passing designs are clustered within each model, protocol and target with Foldseek at TM "
                        "threshold 0.5, alignment type 1 and minimum sequence identity 0; clusters are not pooled "
                        "between targets or models."
                    ),
                    "success_threshold": {
                        "criterion": PASS_CRITERIA[panel],
                        "evaluator": "Common AlphaFold3 evaluation reused from existing accelerated external-eval outputs; the packet states it launches no new generation, folding or rescoring",
                        "note": "The pass criterion is the benchmark's own common evaluation, not the model's acceptance filter",
                    },
                    "measurement_status": "Author-published summary of a frozen cohort; no runner was published and nothing was rerun",
                    "limitations": [
                        "Computational passers only; the card states they do not establish experimental activity.",
                        "Clusters are algorithmic structural clusters, not experimental successes or globally distinct proteins.",
                        "Efficiency depends on how each method was timed and optimized; the packet states it does not assert that all models were equally optimized.",
                    ],
                    "scope_note": (
                        "The published packet labels this conditioning arm '"
                        + spec["arm"]
                        + "' in the dataset column of summary.csv. It is recorded here as a protocol because it fixes "
                        "the inputs a method is given, and the target set is the same."
                    ),
                    "source_locator": (
                        "Hugging Face model card, 'Measured design efficiency' metric line and the sentences below the "
                        "table; benchmarks/METHODS.md, 'Common accounting and timing' and the 'Common AF3 scoring' table "
                        "row for this benchmark; benchmarks/summary.csv, dataset '" + spec["arm"] + "'"
                    ),
                    "review": review(
                        ["automated-source-review", "deterministic-table-parse", "source-hash-verification"],
                        CARD_SHA,
                        CARD_URL,
                        "Metric, aggregation and pass criterion read from the pinned card and methods supplement; the conditioning arm was read from the dataset column of the summary.csv rows the parser matched to each printed cell.",
                    ),
                    "missing_metadata": {
                        "version": {
                            "reason": "unreported",
                            "note": "The packet versions the supplement release, not the individual protocol.",
                        },
                        "random_seeds": {
                            "reason": "unreported",
                            "note": "No seeds are published for the generation runs.",
                        },
                        "reproducibility_note": {
                            "reason": "unavailable",
                            "note": "No runner, native config or checkpoint pin is published, so the protocol cannot be rerun as described.",
                        },
                    },
                },
            }
        )

    # ---- evaluations and results -----------------------------------------------------------
    for cell in CELLS:
        row = rows[cell["row"]]
        check = checks[f"{cell['row']}|{cell['side']}"]
        protocol = PROTOCOLS[cell["protocol"]]
        dataset = DATASETS[protocol["dataset"]]
        panel = protocol["panel"]
        printed = row["rfd4_printed_value"] if cell["side"] == "rfd4" else row["comparator_printed_value"]
        printed_cell = row["rfd4_printed_cell"] if cell["side"] == "rfd4" else row["comparator_printed_cell"]
        eval_id = P + "evaluation-" + CONFIG_SLUG[cell["config"]] + "-" + SLUG[cell["row"]]
        result_id = P + "result-" + CONFIG_SLUG[cell["config"]] + "-" + SLUG[cell["row"]]
        attempts = dataset["targets"] * table["attempts_per_target"]
        locator = (
            "Hugging Face model card, 'Measured design efficiency' table, row '"
            + cell["row"]
            + "', column '"
            + cell["column"]
            + "'"
        )
        if cell["side"] == "other":
            locator += " (printed as '" + row["comparator_printed_cell"] + "')"

        records.append(
            {
                "id": eval_id,
                "kind": "evaluation",
                "name": cell["reported_name"] + " on " + protocol["name"],
                "description": (
                    "Author-published measurement of "
                    + cell["reported_name"]
                    + " on the frozen project benchmark "
                    + panel.replace("_", " ")
                    + " panel, reported as structurally distinct computational passers per GPU-hour."
                ),
                "status": "source_checked",
                "facets": FACETS_PLAIN,
                "source_ids": [
                    P + "source-hf-model-card",
                    P + "source-hf-benchmark-methods",
                    P + "source-hf-benchmark-provenance",
                    P + "source-hf-benchmark-summary",
                ],
                "links": [
                    {"relation": "system", "target_id": cell["config"]},
                    {"relation": "assessment", "target_id": protocol["id"]},
                    {"relation": "data", "target_id": dataset["id"]},
                ],
                "attributes": {
                    "origin": "author_reported",
                    "protocol": protocol["id"],
                    "version": "supplement-20261009",
                    "assessable_targets": dataset["targets"],
                    "denominator": attempts,
                    "comparison": {
                        "protocol_id": protocol["id"],
                        "dataset_version": None,
                        "split": "Evaluation only; every target scored",
                        "population": str(dataset["targets"]) + " targets, 200 original attempts each",
                        "inputs": protocol["conditioning"],
                        "adaptation": (
                            "One-shot generation with the high-thinking recycling schedule and no reward-guided search"
                            if cell["side"] == "rfd4"
                            else "Native recipe as the benchmark methods supplement records it; no terminal selection by the common evaluation"
                        ),
                        "metric_implementation": (
                            "mean_over_targets(3600 * passing_structure_clusters / (generation_gpu_s + af3_gpu_s)), "
                            "published per 10 GPU-minutes in summary.csv and per GPU-hour on the model card"
                        ),
                        "aggregation": "Arithmetic mean of target-level rates",
                        "budget": None,
                    },
                    "coverage": {
                        "scored": attempts,
                        "eligible": attempts,
                        "unit": "design attempts",
                        "note": str(dataset["targets"]) + " targets times 200 original attempts; failed attempts count and keep their consumed time",
                    },
                    "inference_budget": (
                        "High-thinking schedule, 300 trunk passes over 60 steps"
                        if cell["side"] == "rfd4"
                        else "Native recipe as recorded in the methods supplement"
                    ),
                    "limitations": [
                        "Reported by the RFD4-Proteina authors, who built and ran the benchmark.",
                        "Not reproduced: no runner, native config, seed or checkpoint pin is published for the generation runs.",
                    ]
                    + (
                        [
                            "The card states the RFD4-Proteina numbers were measured on the previous release pair, not on the 2026-10-19 release, and the pair is not named by filename.",
                        ]
                        if cell["side"] == "rfd4"
                        else [
                            "A comparator run by another method's developers would not necessarily use this recipe.",
                        ]
                    ),
                    "interpretation": (
                        "Comparison across the two rows of one benchmark is not automatic: the inputs differ where the "
                        "conditioning arm differs, and the comparison fields record that."
                    ),
                    "source_locator": locator,
                    "review": review(
                        ["deterministic-table-parse", "source-hash-verification"],
                        CARD_SHA,
                        CARD_URL,
                        "Evaluation assembled from the printed table cell and the methods supplement for the same pinned revision.",
                        PARSE_NOTE,
                    ),
                    "missing_metadata": {
                        "inference_hardware": {
                            "reason": "unreported",
                            "note": "The card and the packet give GPU-hours without naming the GPU model used for the benchmark runs.",
                        },
                        "replicate_count": {
                            "reason": "inapplicable",
                            "note": "The 200 original attempts per target are the unit of measurement; no repeated runs of the whole panel are reported.",
                        },
                        "checkpoint_revision": {
                            "reason": "unreported",
                            "note": "The packet states each cohort's checkpoint comes from its own native config, which is not published.",
                        },
                    },
                },
            }
        )

        records.append(
            {
                "id": result_id,
                "kind": "result",
                "name": cell["reported_name"] + " on " + protocol["name"] + ": distinct passers per GPU-hour",
                "description": (
                    "Printed value "
                    + printed
                    + " structurally distinct computational passers per GPU-hour for "
                    + cell["reported_name"]
                    + " on the "
                    + cell["row"].lower()
                    + " panel of the frozen project benchmark."
                ),
                "status": "source_checked",
                "facets": FACETS_PLAIN,
                "source_ids": [P + "source-hf-model-card", P + "source-hf-benchmark-summary"],
                "links": [{"relation": "evaluation", "target_id": eval_id}],
                "attributes": {
                    "printed_value": printed,
                    "numeric_value": printed,
                    "metric": METRIC,
                    "metric_direction": "higher",
                    "unit": UNIT,
                    "unit_detail": UNIT_DETAIL,
                    "metric_qualifier": metric_qualifier(panel),
                    "printed_source_cell": printed_cell,
                    "conditioning": protocol["conditioning"],
                    "aggregation": "Arithmetic mean of target-level rates",
                    "denominator": attempts,
                    "coverage": {
                        "scored": attempts,
                        "eligible": attempts,
                        "unit": "design attempts",
                        "note": str(dataset["targets"]) + " targets times 200 original attempts",
                    },
                    "source_locator": locator,
                    "source_cells": [
                        locator,
                        "benchmarks/summary.csv, panel '"
                        + check["summary_panel"]
                        + "', label '"
                        + check["summary_label"]
                        + "', criterion '"
                        + check["summary_criterion"]
                        + "', dataset '"
                        + check["summary_dataset"]
                        + "', column unique_per_10_gpu_min = "
                        + check["summary_unique_per_10_gpu_min"],
                    ],
                    "scope_note": (
                        "Computational passers per GPU-hour, not experimentally active designs. The card states that "
                        "computational passers do not establish experimental activity."
                    )
                    + (
                        " The card states this number was measured on the previous release pair in the October 9, 2026 "
                        "frozen project benchmark, not on the 2026-10-19 release."
                        if cell["side"] == "rfd4"
                        else ""
                    ),
                    "limitations": [
                        "Printed to two decimals with no interval; the card prints no uncertainty for any cell.",
                        "The equivalent row in summary.csv is printed per 10 GPU-minutes; the per-GPU-hour value is the card's own printed figure.",
                    ],
                    "review": review(
                        ["deterministic-table-parse", "source-hash-verification"],
                        CARD_SHA,
                        CARD_URL,
                        "Value parsed from the archived model card with the row labels and header asserted, and cross-checked against the summary.csv row for the same panel, label, criterion and conditioning arm: "
                        + check["summary_unique_per_10_gpu_min"]
                        + " per 10 GPU-minutes times six gives "
                        + check["recomputed_per_gpu_hour"]
                        + ", the printed value.",
                        PARSE_NOTE,
                    ),
                    "missing_metadata": {
                        "uncertainty": {
                            "reason": "unreported",
                            "note": "The table prints point values with no interval or spread.",
                        },
                        "numerator": {
                            "reason": "unreported",
                            "note": "The table prints the mean rate, not the passing-cluster count behind it; per-target rows are in benchmarks/source_data.csv, which was not retrieved.",
                        },
                        "hardware": {
                            "reason": "unreported",
                            "note": "GPU-hours are reported without naming the GPU model used for the benchmark runs.",
                        },
                        "seed": {
                            "reason": "unreported",
                            "note": "No seeds are published for the generation runs.",
                        },
                    },
                },
            }
        )

    records.extend(claims(table))

    records.sort(key=lambda r: r["id"])
    ids = [r["id"] for r in records]
    assert len(ids) == len(set(ids)), "duplicate record ids"
    out = BATCH_DIR / "batch.jsonl"
    with out.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(strip_none(record), ensure_ascii=False, sort_keys=True) + "\n")
    counts: dict[str, int] = {}
    for record in records:
        counts[record["kind"]] = counts.get(record["kind"], 0) + 1
    print(f"wrote {out} with {len(records)} records: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    return 0


def strip_none(value):
    """Drop nulls from attributes, except inside an evaluation's comparison object, where a null
    field is meaningful: it is what blocks automatic comparison."""
    if isinstance(value, dict):
        return {
            k: (v if k == "comparison" else strip_none(v))
            for k, v in value.items()
            if v is not None or k == "comparison"
        }
    if isinstance(value, list):
        return [strip_none(v) for v in value]
    return value


def metric_qualifier(panel: str) -> str:
    return (
        "mean over targets of structurally distinct computational passers per GPU-hour, counting generation "
        "and common AlphaFold3 evaluation time, with 200 original attempts per target and failed attempts "
        "included; passing designs clustered within each model, protocol and target by Foldseek at TM 0.5; "
        "pass criterion: " + PASS_CRITERIA[panel]
    )


# --- descriptive claims ---------------------------------------------------------------------


SUBJECT_LABELS = {
    MODEL_ID: "RFD4-Proteina",
    RELEASE_CONFIG_ID: "RFD4-Proteina 2026-10-19 release pair",
    PREVIOUS_CONFIG_ID: "RFD4-Proteina (high thinking), previous release pair",
    BENCHMARK_ID: "RFD4-Proteina frozen project benchmark, October 9 2026 supplement",
}


def claims(table: dict) -> list[dict]:
    card = P + "source-hf-model-card"
    manifest = P + "source-hf-release-checkpoints"
    ckpt_doc = P + "source-github-checkpoints-doc"
    readme = P + "source-github-readme"
    docs_index = P + "source-github-docs-index"
    methods = P + "source-hf-benchmark-methods"
    provenance = P + "source-hf-benchmark-provenance"
    post = P + "source-rosettacommons-post"
    licence_file = P + "source-github-licence"
    versions = P + "source-preprint-versions"

    specs = [
        {
            "slug": "inputs",
            "subject": MODEL_ID,
            "field": "inputs",
            "value": (
                "Annotated CIF structures or text-based YAML or JSON design specifications. The annotations carry the "
                "conditions: fixed motifs, hotspots, burial, hydrogen bonds and coordinate groups."
            ),
            "locator": "Hugging Face model card, 'At a glance' table row 'Inputs'; repository README, 'Run the model' and key features",
            "sources": [card, readme],
            "artifact": CARD_SHA,
            "url": CARD_URL,
        },
        {
            "slug": "outputs",
            "subject": MODEL_ID,
            "field": "outputs",
            "value": (
                "Designed molecular structures in CIF format, with generated residue identities and coordinates written "
                "to the run's inference_samples directory."
            ),
            "locator": "Hugging Face model card, 'At a glance' table row 'Outputs'; repository README, 'Run the model'",
            "sources": [card, readme],
            "artifact": CARD_SHA,
            "url": CARD_URL,
        },
        {
            "slug": "design-tasks",
            "title": "supported design tasks",
            "subject": RELEASE_CONFIG_ID,
            "field": "supported_tasks",
            "value": (
                "The documentation lists six design tasks as supported by the released checkpoint: unconditional "
                "generation, motif scaffolding, enzyme design, small-molecule binder design, protein binder design and "
                "DNA binder design. The checkpoints reference adds folding and inverse folding, and states the denoiser "
                "accepts generalized sequence-probability conditioning."
            ),
            "locator": "Documentation index, 'What you can design' list-table, all six rows; checkpoints reference, 'Released checkpoints' table row for the denoiser",
            "sources": [docs_index, ckpt_doc],
            "artifact": "228ddfd74255e4458fd8e542bdd8d0a2926ba639c5178f411996848b693c9c48",
            "url": "https://raw.githubusercontent.com/RosettaCommons/RFD4-Proteina/" + CODE_COMMIT + "/docs/index.rst",
        },
        {
            "slug": "matched-pair",
            "subject": MODEL_ID,
            "field": "matched_checkpoint_pair",
            "value": (
                "Generation always loads two checkpoints together: a flow-matching denoiser and the autoencoder it was "
                "trained against. The release is a matched pair and the components are not interchangeable across "
                "releases, because the autoencoder defines the latent space the flow model generates in; the card states "
                "that mixing a flow model with a different autoencoder produces nonsense rather than an error. The "
                "2026-10-19 release changes the latent dimension from 16 to 32 and the residue vocabulary from 33 to 147 "
                "classes, which is stated to be what makes the two releases incompatible with each other's components. "
                "An optional PEFT adapter must be loaded onto the exact base denoiser and autoencoder pair it was "
                "fine-tuned against."
            ),
            "locator": (
                "Hugging Face model card, 'Checkpoints in this release' opening paragraph and the paragraph on the "
                "unified autoencoder; release-checkpoints.json, key 'policy'; checkpoints reference, 'Types of "
                "checkpoints' opening sentence and table rows for the autoencoder and the PEFT adapter"
            ),
            "sources": [card, manifest, ckpt_doc],
            "artifact": CARD_SHA,
            "url": CARD_URL,
        },
        {
            "slug": "release-pair-identity",
            "title": "released checkpoint pair identity",
            "subject": RELEASE_CONFIG_ID,
            "field": "checkpoint_identity",
            "value": (
                "The current release pair is rfd4-proteina-flow-release-2026-10-19.ckpt, the pretrained base at step "
                "320000 with a rank-32 LoRA fine-tune merged in, and rfd4-proteina-ae-release-2026-10-19.ckpt, a unified "
                "protein, RNA, DNA and modified-residue autoencoder with 32 latent channels per residue trained to 400k "
                "steps. Both hold exponential-moving-average weights. The pair supersedes the 2026-10-15 pair "
                "2026_10_15_hero_s43_c512_80k-ema and 2026_10_15_unified_ae_s43_400k-ema, which has the same "
                "architecture. The published files are the stable names flow_checkpoints/rfd4_proteina_flow-ema.ckpt "
                "with SHA-256 c1c8b7068e87c41a334ec5b77e7d7cdda30bd31ed4504909d93bd72f7742afe4 and "
                "ae_checkpoints/rfd4_proteina_ae-ema.ckpt with SHA-256 "
                "24536372f3fc9a5083b6b813baa80630d2287a5d61fbf2f126c9735802e1d21a."
            ),
            "locator": (
                "Hugging Face model card, 'Checkpoints in this release' table, column 'Current release (2026-10-19)', "
                "and the paragraph beginning 'The 2026-10-19 pair supersedes'; release-checkpoints.json, key "
                "'checkpoints'; checkpoints reference, 'Released checkpoints' table"
            ),
            "sources": [card, manifest, ckpt_doc],
            "artifact": "17b8b56247bcae1caf5b39e758c40178863572de0485048dd41f261c93ad16c4",
            "url": "https://huggingface.co/nvidia/RFD4-Proteina/raw/" + HF_REVISION + "/release-checkpoints.json",
        },
        {
            "slug": "previous-pair-identity",
            "title": "checkpoint identity of the pair the efficiency table was measured on",
            "subject": PREVIOUS_CONFIG_ID,
            "field": "checkpoint_identity",
            "value": (
                "The efficiency table's scope note names only 'the previous release pair'. The card's checkpoint table "
                "gives a 'Previous release' column with flow checkpoint chk_epoch_00000169_step_000000340000-ema, "
                "autoencoder 2026_09_04_release_ae_z16_400k-ema, latent dimension 16, 33 residue classes and 434,348,737 "
                "stored parameters. The same card separately says the 2026-10-19 pair supersedes a 2026-10-15 pair. "
                "Neither pair is tied to the table, and the benchmark methods supplement says each cohort's exact "
                "schedule and checkpoint come from its own native config, which the packet does not publish. No "
                "checkpoint filename is assigned to the table's rows in this batch."
            ),
            "locator": (
                "Hugging Face model card, 'Measured design efficiency' blockquote above the table, and 'Checkpoints in "
                "this release' table column 'Previous release'; benchmarks/METHODS.md, 'Model recipes and adaptations' "
                "row RFD4-Proteina"
            ),
            "sources": [card, methods],
            "artifact": CARD_SHA,
            "url": CARD_URL,
            "rationale": (
                "Recorded so the reviewer can rule on whether 'the previous release pair' is the pair in the 'Previous "
                "release' column or the superseded 2026-10-15 pair. The October 9, 2026 freeze predates both dated "
                "October pairs, which favours the 'Previous release' column, but the card does not say so."
            ),
        },
        {
            "slug": "one-model-two-packages",
            "subject": MODEL_ID,
            "field": "runtime_packages",
            "value": (
                "The native bundle in nvidia/RFD4-Proteina and the Diffusers pipeline in "
                "nvidia/RFD4-Proteina-Diffusers are the same model: the card states it is one model throughout, nothing "
                "is retrained, and the Diffusers weights are the same tensors re-prefixed and split across transformer/ "
                "and vae/. The separate repository exists because Diffusers requires model_index.json at the root. Both "
                "hold the same 2026-10-19 release."
            ),
            "locator": "Hugging Face model card, 'Where to find each entry point' table and the two paragraphs below it",
            "sources": [card],
            "artifact": CARD_SHA,
            "url": CARD_URL,
            "rationale": "Recorded as one model with two runtime configurations so that no second model record is created for the Diffusers package.",
        },
        {
            "slug": "parameters",
            "subject": RELEASE_CONFIG_ID,
            "field": "parameters",
            "value": (
                "435,622,465 stored parameters across the paired bundle, in FP32. model.safetensors is 1.74 GB and the "
                "cached release bundle is about 1.7 GB including its autoencoder. The published EMA exports are 1.74 GB "
                "and 1.03 GB rather than 4.21 GB and 3.10 GB because the duplicate shadow copy, optimizer, scheduler and "
                "loop state are removed; their weight tensors are stated to be bit-identical to the full training "
                "checkpoints."
            ),
            "locator": "Hugging Face model card, 'At a glance' rows 'Weights' and 'Download', and the paragraph beginning 'The published .ckpt files'; release-checkpoints.json, key 'stored_parameters' and the size fields",
            "sources": [card, manifest, readme],
            "artifact": CARD_SHA,
            "url": CARD_URL,
        },
        {
            "slug": "flow-training",
            "title": "flow-model training compute",
            "subject": RELEASE_CONFIG_ID,
            "field": "training_compute",
            "value": (
                "The preprint states the release flow model was pretrained with 256-token crops to 320,000 optimizer "
                "steps using four independently noised candidates per example, requiring about 16,000 GPU-hours, and "
                "then fine-tuned for about 2,000 GPU-hours with low-rank adaptation at rank 32, scaling factor 64 and no "
                "adapter dropout, over 60,000 additional updates with 384-token padding. Both flow stages use the same "
                "frozen autoencoder."
            ),
            "locator": "Preprint version 3, Section S4.2 'Training stages' and Table S12 'Flow-model training stages'",
            "sources": [PREPRINT_ID, card],
            "artifact": "b581fc10da53e94b263c36a7871906f10ba6559f993c02e08f8b3de6b1d0347e",
            "url": "https://rfd4-proteina.org/assets/paper/versions/RFD4-Proteina-v3-20261113T070435Z.pdf",
        },
        {
            "slug": "autoencoder-training",
            "subject": RELEASE_CONFIG_ID,
            "field": "autoencoder_training",
            "value": (
                "The preprint states the unified biomolecular autoencoder was trained from scratch with 256-token crops "
                "and a global batch size of 512, requiring about 4,000 GPU-hours on NVIDIA H200s. The checkpoints "
                "reference adds that the released autoencoder covers proteins, RNA, DNA and modified residues with 32 "
                "latent channels per residue and was trained to 400k steps, and that it also has to be loaded when "
                "training a new denoiser because it fixes the latent space."
            ),
            "locator": "Preprint version 3, Section S4.2 'Training stages', first paragraph; checkpoints reference, 'Released checkpoints' table row for the autoencoder and 'Types of checkpoints' table",
            "sources": [PREPRINT_ID, ckpt_doc],
            "artifact": "b18b755f5098208611f02cb4b4100eedeeca5730a450d484b2356e844fec8f3b",
            "url": "https://raw.githubusercontent.com/RosettaCommons/RFD4-Proteina/" + CODE_COMMIT + "/docs/reference/checkpoints.md",
        },
        {
            "slug": "thinking-presets",
            "subject": MODEL_ID,
            "field": "sampling_presets",
            "value": (
                "The released recipes differ only in how often the trunk is recycled per sampling step, as bands over 60 "
                "steps: low [[10,4],[10,3],[10,2],[30,1]] for 120 trunk passes, medium [[5,6],[10,5],[5,4],[10,3],[20,2],"
                "[10,1]] for 180 trunk passes and the default, and high [[10,9],[10,8],[10,5],[20,3],[10,2]] for 300 "
                "trunk passes. The native runtime also offers flat and mid-peak schedules for each budget."
            ),
            "locator": "Hugging Face model card, 'Compute presets' table and the two sentences around it",
            "sources": [card],
            "artifact": CARD_SHA,
            "url": CARD_URL,
        },
        {
            "slug": "licence-scope",
            "title": "what the BSD 3-Clause licence covers",
            "subject": MODEL_ID,
            "field": "licence",
            "value": (
                "The BSD 3-Clause licence, Copyright (c) 2026, Institute for Protein Design, University of Washington, "
                "covers the RFD4-Proteina model, weights and code only. The optional AlphaFold2 and OpenFold3 or "
                "AlphaFold3 refolding container images package third-party software that stays under its own upstream "
                "licences, some of which the card says restrict commercial use or redistribution; the ported OpenFold3 "
                "weights are stated to be Apache-2.0. The card says each upstream licence must be reviewed before using "
                "the images and not to assume the BSD licence applies to them. Neither refolding oracle is needed for "
                "generation."
            ),
            "locator": "Hugging Face model card, 'License' section and the 'Other repository files' details block; LICENSE file, whole file",
            "sources": [card, licence_file],
            "artifact": CARD_SHA,
            "url": CARD_URL,
        },
        {
            "slug": "training-data-terms",
            "subject": MODEL_ID,
            "field": "training_data_terms",
            "value": (
                "The card states the training data has its own source terms, described on the companion Hugging Face "
                "dataset card, and that the dataset's upload date or proposed sampling mix should not be interpreted as "
                "the exact training history of every checkpoint. Training datasets are a separate download from the "
                "model weights and are not needed for generation."
            ),
            "locator": "Hugging Face model card, 'Training data and limitations' and 'License' sections; repository README, 'Hugging Face and Python'",
            "sources": [card, readme],
            "artifact": CARD_SHA,
            "url": CARD_URL,
            "limitations": [
                "The companion dataset card was not retrieved or hashed in this pass, so the dataset's own licence is a recorded gap.",
            ],
        },
        {
            "slug": "annotation-requirement",
            "subject": MODEL_ID,
            "field": "input_requirements",
            "value": (
                "The annotations on an input specify what to hold fixed and what to design. The card states that an "
                "ordinary, unannotated structure is not a complete design specification."
            ),
            "locator": "Hugging Face model card, 'Start with one design', step 3, final sentence",
            "sources": [card],
            "artifact": CARD_SHA,
            "url": CARD_URL,
        },
        {
            "slug": "tested-hardware",
            "subject": MODEL_ID,
            "field": "hardware_requirements",
            "value": (
                "Linux x86_64, Python 3.12 and a CUDA 13-compatible driver are required; macOS and Windows are not "
                "supported. The card lists the NVIDIA GPUs it says are tested and confirmed: Blackwell B200, B300, "
                "GB200, GB300, RTX PRO 6000 Blackwell Server Edition, RTX PRO 6000 Blackwell Workstation Edition and "
                "GB10 (DGX Spark); Hopper H100 SXM, H100 PCIe, H100 NVL, H200, H200 NVL and GH200 144GB; Ada Lovelace "
                "L40S and RTX 6000 Ada Generation; Ampere A100 SXM4 40GB and 80GB and A100 PCIe 40GB and 80GB. Peak GPU "
                "memory is said to depend on token count, batch size and recycle depth rather than on the weights."
            ),
            "locator": "Hugging Face model card, 'Hardware requirements' table and the paragraph below it; repository README, 'System requirements'",
            "sources": [card, readme],
            "artifact": CARD_SHA,
            "url": CARD_URL,
        },
        {
            "slug": "lineage",
            "title": "stated lineage from RFdiffusion and Proteina",
            "subject": MODEL_ID,
            "field": "lineage",
            "value": (
                "The RosettaCommons post describes RFD4-Proteina as the next generation of RFdiffusion from the "
                "Institute for Protein Design, developed in collaboration with NVIDIA, building on previous models "
                "including RFdiffusion, RFdiffusion2 and RFdiffusion3 and incorporating advances from NVIDIA's Proteina "
                "model. It names a broader collaboration with Rosetta Commons, the Open Rosetta project at OMSF and the "
                "OpenFold Consortium, and records that the release coincides with a formal release of TMol and relies on "
                "a newly released version of AtomWorks."
            ),
            "locator": "RosettaCommons post, second paragraph and the section 'Collaborations Across Academia and Industry Lead to Scientific Advancements in Protein Design'",
            "sources": [post, card],
            "artifact": "cb0d0739ef0d8f367f10f910c721ca299ca7a7b24d214f8929373604c9760f6b",
            "url": "https://rosettacommons.org/2026/10/23/rfd4-proteina-improves-computational-protein-design-through-open-science-and-collaboration/",
            "target_id": "discovery-model-rfdiffusion",
            "rationale": (
                "Recorded as a lineage statement, not as a graph edge. The store already holds RFdiffusion as "
                "discovery-model-rfdiffusion at family level, and the named target_id points at it. No model record is "
                "created for RFdiffusion2, RFdiffusion3 or Proteina: the store holds none, and the only Proteina records "
                "in it are evaluated configurations from a third-party comparison. Whether a variant_of or supersedes "
                "edge from RFD4-Proteina to RFdiffusion is wanted is left to the reviewer, because 'next generation of' "
                "in an announcement is not the same statement as either relation."
            ),
            "limitations": [
                "From an announcement page, not a technical source. No architectural inheritance is asserted.",
            ],
        },
        {
            "slug": "efficiency-table-scope",
            "subject": BENCHMARK_ID,
            "field": "efficiency_table_scope",
            "value": (
                "The card prints above the efficiency table: '"
                + table["scope_note"].replace("**", "")
                + "' The provenance file gives the packet's source release as supplement-20261009 from paper commit "
                "8614542c149875b13ed3fed5d8d6ec739f2daff4, and its scope as 'Frozen project benchmark runs; not a new "
                "evaluation of every model Hub revision.'"
            ),
            "locator": "Hugging Face model card, 'Measured design efficiency' blockquote; benchmarks/provenance.json, keys source_release, paper_commit and scope",
            "sources": [card, provenance],
            "artifact": CARD_SHA,
            "url": CARD_URL,
            "rationale": (
                "This is why no result in this batch is attached to the 2026-10-19 release configuration. The eight "
                "printed values are attached to a configuration whose checkpoint identity is left as the source gives it."
            ),
        },
        {
            "slug": "efficiency-metric-meaning",
            "subject": BENCHMARK_ID,
            "field": "metric_definition",
            "value": (
                "The card defines the table's metric as '"
                + table["metric_definition"]
                + "', higher being better, and adds that computational passers do not establish experimental activity. "
                "The provenance file gives the expression mean_over_targets(3600 * passing_structure_clusters / "
                "(generation_gpu_s + af3_gpu_s)). The methods supplement defines a passing cluster as a distinct "
                "Foldseek cluster among passing originals, computed within each model, protocol and target at TM "
                "threshold 0.5, and says these are algorithmic structural clusters, not experimental successes or "
                "globally distinct proteins."
            ),
            "locator": "Hugging Face model card, 'Measured design efficiency' metric line and the paragraph below the table; benchmarks/provenance.json, key metric; benchmarks/METHODS.md, final paragraph of 'Common AF3 scoring'",
            "sources": [card, provenance, methods],
            "artifact": CARD_SHA,
            "url": CARD_URL,
        },
        {
            "slug": "conditioning-differences",
            "subject": BENCHMARK_ID,
            "field": "conditioning_differences",
            "value": table["conditioning_note"],
            "locator": "Hugging Face model card, 'Measured design efficiency', paragraph beginning 'Conditioning differs between some methods'",
            "sources": [card, methods],
            "artifact": CARD_SHA,
            "url": CARD_URL,
            "rationale": (
                "Each conditioning arm is recorded as its own protocol, so the protein-binding and DNA rows of the table "
                "sit on different protocols and their comparison fields differ. The small-molecule and enzyme rows share "
                "a protocol because both of their printed methods use the same arm."
            ),
        },
        {
            "slug": "pass-criteria",
            "subject": BENCHMARK_ID,
            "field": "pass_criteria",
            "value": (
                "Protein binding, 24 targets: "
                + PASS_CRITERIA["ppi"]
                + ", with CA-only RMSD for one CA-only comparator. Small molecule, 77 targets: "
                + PASS_CRITERIA["small_molecule"]
                + ". Atomic Motif Enzyme, 37 targets: "
                + PASS_CRITERIA["ame"]
                + ". DNA, 3 targets: "
                + PASS_CRITERIA["dna"]
                + ". The pass criteria are a common AlphaFold3 evaluation, stated not to be the model's own acceptance "
                "filter, and the packet reuses existing scores rather than launching new folding or rescoring."
            ),
            "locator": "benchmarks/METHODS.md, 'Common AF3 scoring' table, all five rows, and the paragraph above it",
            "sources": [methods],
            "artifact": "46d1e181c495d4ecc9a3992a4e7f3cd8fae0b4904fb799ab5c1a883090ca837b",
            "url": "https://huggingface.co/nvidia/RFD4-Proteina/raw/" + HF_REVISION + "/benchmarks/METHODS.md",
        },
        {
            "slug": "attempt-accounting",
            "subject": BENCHMARK_ID,
            "field": "attempt_accounting",
            "value": (
                "Each model, protocol and target has 200 original attempts, including native failures and unmatched "
                "required motifs. Rejected originals are not replaced and outputs are not selected with the common "
                "AlphaFold3 evaluation. Failed attempts consume time and stay included in the efficiency denominator, "
                "while setup, compilation, CPU scoring and idle allocation time are excluded. Values are means of "
                "target-level rates, not pooled totals or single-design latency."
            ),
            "locator": "Hugging Face model card, 'Measured design efficiency', paragraph beginning 'There are 200 original attempts per target'; benchmarks/METHODS.md, 'Common accounting and timing'",
            "sources": [card, methods],
            "artifact": CARD_SHA,
            "url": CARD_URL,
        },
        {
            "slug": "preprint-status",
            "title": "preprint and its versions",
            "subject": MODEL_ID,
            "field": "publication_status",
            "value": (
                "A preprint, 'Biomolecular design through latent reasoning with RFD4-Proteina', is published on the "
                "project page and states on its title page that it has not been peer reviewed and is licensed CC BY 4.0. "
                "The project's own manifest lists three versions: version 1 uploaded 2026-10-21T12:07:43Z, version 2 "
                "uploaded 2026-10-22T00:30:19Z correcting a Figure 4a plotting error and adding confidence intervals and "
                "methodological detail for calmodulin binding, and version 3 uploaded 2026-11-13T07:04:35Z updating the "
                "author list and affiliations, updating Figures 1 and 6, the enzyme results and associated text, and "
                "combining the main manuscript and supplement into a single PDF. The repository README cites it as a "
                "preprint with no DOI."
            ),
            "locator": "Preprint version 3, title page; preprint-versions.json, key 'versions', entries 1 to 3; repository README, 'Citation'",
            "sources": [PREPRINT_ID, versions, readme],
            "artifact": "1c6c825a8694c5987d47c03d044385cc38b8a9162e2dbb69d78e9edb5cbc0b4d",
            "url": "https://rfd4-proteina.org/data/preprint-versions.json",
            "limitations": [
                "No preprint-server record or DOI was found for it, so the version history rests on the project's own manifest.",
                "The copy of the manifest committed at the pinned code commit lists only versions 1 and 2; version 3 is known from the live file.",
            ],
            "rationale": (
                "Recorded because the issue asks whether a paper or preprint exists. It does, it is pinned as "
                + PREPRINT_ID
                + ", and its result tables are a recorded gap rather than part of this batch."
            ),
        },
        {
            "slug": "attribution",
            "subject": MODEL_ID,
            "field": "developers",
            "value": (
                "Developed by the Baker Lab at the Institute for Protein Design, University of Washington, and NVIDIA "
                "GenAIR. The preprint's corresponding authors are Kieran Didi and David Baker, with four joint first "
                "authors."
            ),
            "locator": "Hugging Face model card, 'Attribution and support'; documentation index, hero paragraph; preprint version 3, title page and corresponding-author footnote",
            "sources": [card, docs_index, PREPRINT_ID],
            "artifact": CARD_SHA,
            "url": CARD_URL,
        },
    ]

    out = []
    for spec in specs:
        attributes = {
            "field": spec["field"],
            "value": spec["value"],
            "source_locator": spec["locator"],
            "review": review(
                ["automated-source-review", "source-hash-verification"],
                spec["artifact"],
                spec["url"],
                "Read from the pinned artifact named in the locator; quoted wording is quoted, and nothing beyond the source's own statement is asserted.",
            ),
        }
        for key in ("rationale", "limitations", "target_id"):
            if key in spec:
                attributes[key] = spec[key]
        subject_label = SUBJECT_LABELS[spec["subject"]]
        out.append(
            {
                "id": P + "claim-" + spec["slug"],
                "kind": "claim",
                "name": subject_label + ": " + spec.get("title", spec["field"].replace("_", " ")),
                "description": (
                    "Descriptive fact about "
                    + subject_label
                    + ", taken from the pinned project sources named in the locator."
                ),
                "status": "source_checked",
                "facets": FACETS_PLAIN,
                "source_ids": sorted(spec["sources"]),
                "links": [{"relation": "subject", "target_id": spec["subject"]}],
                "attributes": attributes,
            }
        )
    return out


if __name__ == "__main__":
    sys.exit(main())
