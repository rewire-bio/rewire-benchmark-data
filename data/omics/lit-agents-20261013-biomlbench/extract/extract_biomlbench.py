"""Build the BioML-bench extraction batch from the pinned sources.

Usage:
  python3 -I extract_biomlbench.py <v3.pdf> <repo-dir> <batch-dir>

<v3.pdf> is bioRxiv 10.1101/2025.09.01.673319 version 3 (SHA-256 checked below).
<repo-dir> is science-machine/biomlbench unpacked at commit 673f3d8 (files hashed below).
Table 4 is parsed from `pdftotext -layout` output; row labels, block order and
column count are asserted. Only the Drug Discovery, Protein Engineering and
Single Cell Omics blocks are written; Biomedical Imaging is out of scope.
"""

import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

PDF_SHA = "875cb3519dac9b0ec51c35224e1fc90b107b0676a4cc7c22cecb56eb8ac38b35"
REPO_TAR_SHA = "c23978275652d61452e710dfdf94613237b85ab9b90605af457d082c351ae559"
COMMIT = "673f3d8d3462fc6cdcbbd9695fba612b9332ca65"
REPO_FILES = {
    "README.md": "90e9f9e352d4f2c22817ba8305aa836c12dd56a0055ac7518de014e625721c92",
    "experiments/biomlbench_v0.1a.txt": "d19b815b1222f178457ba4e46e5430eaa2dba299e4c06d3240367624a26b5faf",
    "agents/biomni/config.yaml": "2443f151826a640d16f711384b44a8b4843cc70c940bc62fc50dfcc9f461d26d",
    "agents/biomni/main.py": "52e8344651c19c1d86b0bf24a68652f884d2fbc9dc75ce8ad0cda83794d68134",
    "agents/aide/config.yaml": "c5ee94e79b2962e47b780f7d3c1cfa0a4f588287ee157b33c42cfd81388494f5",
    "agents/aide/requirements.txt": "c8f06bcea1f98df3739a265e599c35b089fff3951360351517f02b74809aba34",
    "agents/stella/config.yaml": "5ca7fd937e28e228caf58c414d4385e5e868b1078507a7c01bf838b5e8af9a7f",
    "agents/mlagentbench/config.yaml": "85806153b3c25d42a1b2ab96ee93054766f08b60eea52b05e8254568250c9205",
}
RETRIEVED_PDF = "2026-10-13T12:38:42Z"
RETRIEVED_REPO = "2026-10-13T12:38:10Z"
TODAY = "2026-10-13"
P = "lit-agents-20261013-biomlbench"
SRC = f"{P}-source-miller2025-v3"
REPO = f"{P}-source-repo-673f3d8"
BENCH = f"{P}-benchmark-biomlbench"
PDF_URL = "https://www.biorxiv.org/content/10.1101/2025.09.01.673319v3.full.pdf"
EXTRACTOR = "Extractor: Claude (Opus 5.5) research agent; not independent review; no human review claimed"
FACETS = {"research": ["research"]}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def extraction_review(method_note, note="Extraction only; pending independent review."):
    return {
        "method": ["pdf-text-parse"],
        "method_note": method_note,
        "reviewer": ["claude"],
        "reviewer_note": EXTRACTOR,
        "date": TODAY,
        "note": note,
    }


def rec(id_, kind, name, description, areas, source_ids, links, attributes, method_types=None):
    facets = {"areas": areas, "contexts": ["research"]} if areas else {}
    if method_types:
        facets["method_types"] = method_types
    return {
        "id": id_,
        "kind": kind,
        "name": name,
        "description": description,
        "status": "needs_review",
        "facets": facets,
        "source_ids": source_ids,
        "links": links,
        "attributes": attributes,
    }


# --- Table 4 -----------------------------------------------------------------

AGENTS = ["Dummy", "MLAgentBench", "AIDE", "STELLA", "Biomni"]
DOMAINS = ["Biomedical Imaging", "Drug Discovery", "Protein Engineering", "Single Cell Omics"]
COLUMNS = ["Leaderboard Percentile", "Mean Rank", "Above Median (%)", "Any Medal (%)", "Completion Rate (%)"]
PM = r"(\d+\.\d+ ± \d+\.\d+)"
ROW = re.compile(
    r"^\s*(?:(Penalized|Non-penalized)\s+)?(?:(Biomedical Imaging|Drug Discovery|Protein Engineering|Single Cell Omics)\s+)?"
    r"(?:(Penalized|Non-penalized)\s+)?(Dummy|MLAgentBench|AIDE|STELLA|Biomni)\s+"
    + r"\s+".join([PM] * 4)
    + r"\s+(NA|-|\d+\.\d+)\s*$"
)


def parse_table4(text):
    start = text.index("Table 4: BioML-bench results by domain")
    end = text.index("Figure 6: Failure mode analysis")
    block = text[start:end]
    assert "Type            Domain                Agent          Leaderboard Percentile   Mean Rank     Above Median (%)   Any Medal (%)   Completion Rate (%)" in block
    rows = []
    for line in block.splitlines():
        m = ROW.match(line)
        if m:
            rows.append(m.groups())
    assert len(rows) == 40, len(rows)
    out = []
    for i, g in enumerate(rows):
        setting = "penalized" if i < 20 else "non-penalized"
        domain = DOMAINS[(i % 20) // 5]
        agent = AGENTS[i % 5]
        assert g[3] == agent, (i, g)
        if g[1]:
            assert g[1] == domain, (i, g)
        label = g[0] or g[2]
        if label:
            assert label.lower() == setting, (i, g)
        out.append({"setting": setting, "domain": domain, "agent": agent, "cells": list(g[4:9])})
    # Each domain label is printed once per block on the first (Dummy) row.
    return out


# --- Entities ------------------------------------------------------------------

DOMAIN_INFO = {
    "Drug Discovery": {
        "slug": "drug-discovery",
        "areas": ["molecular-interactions"],
        "tasks": [
            ("polaris-pkis2-egfr-wt-c-1", "polarishub/polaris-pkis2-egfr-wt-c-1", "Classify compounds as EGFR wild-type kinase inhibitors (>80% inhibition). Scaffold-based split for glioblastoma drug discovery.", "Polaris Hub benchmark polaris/pkis2-egfr-wt-c-1; grader main metric pr_auc", None),
            ("polaris-adme-fang-hclint-1", "polarishub/polaris-adme-fang-hclint-1", "Predict human liver microsomal intrinsic clearance from SMILES (Fang et al. 2023, 2,229 compounds).", "Polaris Hub benchmark polaris/adme-fang-hclint-1; grader main metric pearsonr", None),
            ("polaris-adme-fang-hppb-1", "polarishub/polaris-adme-fang-hppb-1", "Predict fraction unbound in human plasma protein binding from molecular structure (2,218 compounds).", "Polaris Hub benchmark polaris/adme-fang-hppb-1; grader main metric pearsonr", None),
            ("polaris-adme-fang-solu-1", "polarishub/polaris-adme-fang-solu-1", "Predict compound solubility from SMILES using standardized ADME protocols (1,578 compounds).", "Polaris Hub benchmark polaris/adme-fang-solu-1; grader main metric pearsonr", None),
            ("tdcommons-cyp2d6-substrate", "polarishub/tdcommons-cyp2d6-substrate-carbonmangels", "Classify CYP2D6 enzyme substrates from molecular structure for drug–drug interaction risk.", "Polaris Hub benchmark tdcommons/cyp2d6-substrate-carbonmangels; grader main metric pr_auc", "discovery-benchmark-tdc-molecular-tasks"),
            ("tdcommons-lipophilicity", "polarishub/tdcommons-lipophilicity-astrazeneca", "Predict lipophilicity (logP) from SMILES (AstraZeneca dataset).", "Polaris Hub benchmark tdcommons/lipophilicity-astrazeneca; grader main metric mean_absolute_error", "discovery-benchmark-tdc-molecular-tasks"),
            ("tdcommons-herg", "polarishub/tdcommons-herg", "Classify hERG potassium channel blockers to assess cardiotoxicity risk.", "Polaris Hub benchmark tdcommons/herg; grader main metric roc_auc", "discovery-benchmark-tdc-molecular-tasks"),
            ("tdcommons-bbb-martins", "polarishub/tdcommons-bbb-martins", "Classify blood–brain barrier penetration for CNS drug development.", "Polaris Hub benchmark tdcommons/bbb-martins; grader main metric roc_auc", "discovery-benchmark-tdc-molecular-tasks"),
            ("tdcommons-caco2-wang", "polarishub/tdcommons-caco2-wang", "Predict intestinal permeability in Caco-2 cell assay from SMILES.", "Polaris Hub benchmark tdcommons/caco2-wang; grader main metric mean_absolute_error", "discovery-benchmark-tdc-molecular-tasks"),
        ],
        "split": "Each task's train and test split as downloaded from its Polaris Hub benchmark",
        "upstream": "Polaris Hub (paper Table 1). Five tasks are Polaris-hosted Therapeutics Data Commons (tdcommons) benchmarks; four are Polaris ADME (Fang et al.) and PKIS2 kinase benchmarks.",
    },
    "Protein Engineering": {
        "slug": "protein-engineering",
        "areas": ["protein-function"],
        "tasks": [
            ("SPIKE_SARS2_Starr_2020", "proteingym-dms/SPIKE_SARS2_Starr_2020_binding", "Predict ACE2 binding fitness for SARS-CoV-2 spike RBD single-site variants.", "ProteinGym DMS assay SPIKE_SARS2_Starr_2020_binding; Spearman averaged over the random, modulo and contiguous 5-fold cross-validation schemes", "discovery-benchmark-proteingym"),
            ("SPA_STAAU_Tsuboyama_2023", None, "Predict stability of Staphylococcus aureus protein A multi-substitution variants.", "ProteinGym DMS assay; repository task list names SBI_STAAM_Tsuboyama_2023_2JVG at this position, not an SPA_STAAU assay", "discovery-benchmark-proteingym"),
            ("PSAE_PICP2_indels", None, "Predict stability effects of indel variants in photosystem I subunit IV.", "ProteinGym DMS assay; repository task list names PSAE_PICP2_Tsuboyama_2023_1PSE (the substitution assay), not the _indels assay", "discovery-benchmark-proteingym"),
            ("CBX4_HUMAN_multi-sub", None, "Predict stability of human CBX4 SUMO ligase multi-substitution variants.", "ProteinGym DMS assay; repository task list names CBX4_HUMAN_Tsuboyama_2023_2K28", "discovery-benchmark-proteingym"),
            ("Q8EG35_SHEON_indels", "proteingym-dms/Q8EG35_SHEON_Campbell_2022_indels", "Predict organismal fitness for Shewanella MtrA protein indel variants.", "ProteinGym DMS assay Q8EG35_SHEON_Campbell_2022_indels; Spearman averaged over the random, modulo and contiguous 5-fold cross-validation schemes", "discovery-benchmark-proteingym"),
            ("CSN4_MOUSE_indels", "proteingym-dms/CSN4_MOUSE_Tsuboyama_2023_1UFM_indels", "Predict stability of mouse COP9 signalosome subunit 4 indel variants.", "ProteinGym DMS assay CSN4_MOUSE_Tsuboyama_2023_1UFM_indels; Spearman averaged over the random, modulo and contiguous 5-fold cross-validation schemes", "discovery-benchmark-proteingym"),
        ],
        "split": "ProteinGym supervised cross-validation folds (fold_random_5, fold_modulo_5, fold_contiguous_5) per DMS assay",
        "upstream": "ProteinGym (paper Table 1).",
    },
    "Single Cell Omics": {
        "slug": "single-cell-omics",
        "areas": ["single-cell"],
        "tasks": [
            ("open-problems-modality", "manual/open-problems-predict-modality", "Cross-modal prediction of protein abundance from RNA expression in CITE-seq data.", "Adapted from Open Problems; BMMC CITE-seq; grader rmse", None),
            ("open-problems-perturbations", "manual/open-problems-single-cell-perturbations", "Predict differential gene expression in PBMCs under small molecule perturbations.", "Adapted from Open Problems; 144 compounds in PBMCs; grader mean-rowwise-rmse", None),
            ("open-problems-label-projection", "manual/open-problems-label-projection", "Project cell type labels across diabetic kidney disease datasets.", "Adapted from Open Problems; grader f1-weighted", None),
            ("open-problems-spatial-genes", "manual/open-problems-spatially-variable-genes", "Identify spatially variable genes in mouse cortex Slide-seqV2 data.", "Adapted from Open Problems; simulated Slide-seqV2 mouse cortex; grader kendall-correlation", None),
            ("open-problems-cell-communication", "manual/open-problems-cell-cell-communication-ligand-target", "Predict ligand–target interactions driving cell–cell communication in breast cancer scRNA-seq.", "Adapted from Open Problems; TNBC (Wu et al. 2021) with a BioML-bench 10/90 train/test split; grader odds-ratio", None),
        ],
        "split": "Task-specific splits defined by BioML-bench's own preparation scripts",
        "upstream": "Open Problems (paper Table 1). BioML-bench prepares its own data files and splits; they are not the Open Problems benchmark splits.",
    },
}

AGENT_INFO = {
    "Dummy": {"slug": "dummy", "config": f"{P}-config-dummy", "method": f"{P}-method-dummy-agent"},
    "MLAgentBench": {"slug": "mlagentbench", "config": f"{P}-config-mlagentbench-gpt-4-1", "method": f"{P}-method-mlagentbench"},
    "AIDE": {"slug": "aide", "config": f"{P}-config-aide-gpt-4-1", "method": f"{P}-method-aide"},
    "STELLA": {"slug": "stella", "config": f"{P}-config-stella-openrouter-default", "method": f"{P}-method-stella"},
    "Biomni": {"slug": "biomni", "config": f"{P}-config-biomni-claude-sonnet-4", "method": "tgtval-20261009-method-biomni"},
}

METRICS = [
    # column, metric, slug, direction, unit, unit_detail, qualifier stem
    ("Leaderboard Percentile", "leaderboard-percentile", "leaderboard-percentile", "higher", "percent", "percentile of public leaderboard entries, 0 to 100", "mean over tasks in the domain"),
    ("Mean Rank", "rank", "mean-rank", "lower", "unitless", None, "mean relative rank among the five Table 4 agents (Dummy, MLAgentBench, AIDE, STELLA, Biomni) by leaderboard percentile, over tasks in the domain"),
    ("Above Median (%)", "proportion", "above-median", "higher", "percent", None, "share of tasks where the agent's mean score exceeds the median human leaderboard submission (Section 3.4 definition)"),
    ("Any Medal (%)", "proportion", "any-medal", "higher", "percent", None, "share of tasks where the agent reaches a public leaderboard medal threshold, MLE-bench definition (Section 3.4)"),
    ("Completion Rate (%)", "proportion", "completion-rate", "higher", "percent", None, "share of tasks that yield a valid, gradable submission (Section 3.4 definition)"),
]

SETTING_TEXT = {
    "penalized": "penalized: runs without a valid submission scored as percentile 0",
    "non-penalized": "non-penalized: runs without a valid submission omitted",
}


def build(pdf_path, repo_dir):
    assert sha(pdf_path) == PDF_SHA, "PDF hash mismatch"
    for rel, digest in REPO_FILES.items():
        assert sha(Path(repo_dir) / rel) == digest, rel
    text = subprocess.run(["pdftotext", "-layout", str(pdf_path), "-"], check=True, capture_output=True, text=True).stdout
    task_list = (Path(repo_dir) / "experiments/biomlbench_v0.1a.txt").read_text().split()
    assert len(task_list) == 24, len(task_list)

    records, claims_rows = [], []

    # Sources
    records.append(rec(SRC, "source", "BioML-bench: Evaluation of AI Agents for End-to-End Biomedical ML",
        "bioRxiv preprint (version 3) introducing BioML-bench and reporting four agents against human leaderboards.",
        ["molecular-interactions", "protein-function", "single-cell"], [], [], {
            "url": "https://www.biorxiv.org/content/10.1101/2025.09.01.673319v3",
            "artifact_url": PDF_URL,
            "version": "bioRxiv 2025.09.01.673319 version 3, posted 2025-09-28 (versions 1 and 2 posted 2025-09-04 and 2025-09-07)",
            "retrieved_at": RETRIEVED_PDF,
            "artifact_sha256": PDF_SHA,
            "doi": "10.1101/2025.09.01.673319",
            "publication_status": "preprint",
            "licence": "CC-BY-4.0",
            "media_type": "application/pdf",
            "source_locator": "Full artifact bytes; per-record locators on each record",
            "access_and_reuse": "CC-BY-4.0 permits redistribution of the article bytes.",
            "archive_note": "Not archived in the batch: the PDF is 2,282,513 bytes and the repository keeps releases small. The artifact_sha256 pins the bytes that were read.",
            "extraction_method": "pdftotext -layout text layer, parsed by extract/extract_biomlbench.py",
            "limitations": [
                "Preprint, not peer reviewed. No published version was found (bioRxiv publication API, 2026-10-13).",
                "Results are printed only as aggregates: Table 2 over all 24 tasks and Table 4 per domain. Per-task leaderboard percentiles appear only as points in Figures 2 and 4, with no printed values.",
                "Table 3 names three protein engineering tasks differently from the repository's task list at commit 673f3d8 (experiments/biomlbench_v0.1a.txt): SPA_STAAU_Tsuboyama_2023 versus SBI_STAAM_Tsuboyama_2023_2JVG, PSAE_PICP2_indels versus PSAE_PICP2_Tsuboyama_2023_1PSE, and CBX4_HUMAN_multi-sub versus CBX4_HUMAN_Tsuboyama_2023_2K28. Which assays were run is unresolved.",
                "Table 4 prints a value with a plus-or-minus spread but its caption does not say what the spread is. Figures 2 and 4 show the same per-domain leaderboard percentiles as mean ± SEM across tasks, and the Table 2 caption refers to the reported SEM.",
                "Section 3.4 defines Above Median, Any Medal and Completion Rate over tasks, but the Table 4 values are multiples of 1/(4 x tasks in the domain) (for example 45.8% = 11/24 for 6 protein tasks), which fits counting replicate runs. The denominator is unresolved.",
                "Table 4 prints Completion Rate 'NA' for Dummy in the penalized block, while Table 2 prints 100.0 for Dummy overall.",
                "All agents were run by the benchmark's authors, who did not build them. B. T. is CTO of ScienceMachine, which provided compute and LLM API resources (Competing Interests; Acknowledgments).",
            ],
        }))
    records.append(rec(REPO, "source", "science-machine/biomlbench repository at commit 673f3d8",
        "Official BioML-bench code repository (README states v0.1-alpha), pinned to the default-branch head at retrieval.",
        ["molecular-interactions", "protein-function", "single-cell"], [], [], {
            "url": f"https://github.com/science-machine/biomlbench/tree/{COMMIT}",
            "artifact_url": f"https://codeload.github.com/science-machine/biomlbench/tar.gz/{COMMIT}",
            "version": f"Git commit {COMMIT} (2025-09-14, head of main at retrieval); README title 'BioML-bench (v0.1-alpha)'",
            "retrieved_at": RETRIEVED_REPO,
            "artifact_sha256": REPO_TAR_SHA,
            "hash_scope": "SHA-256 of the codeload tar.gz archive for the commit; two downloads gave identical bytes. Per-file hashes of the files cited are in sources.md.",
            "publication_status": "official_project_source",
            "licence": "MIT",
            "media_type": "application/gzip",
            "source_locator": "README.md; experiments/biomlbench_v0.1a.txt; agents/*/config.yaml; per-record locators on each record",
            "limitations": [
                "The repository holds no agent results or leaderboard snapshots; the human leaderboards are fetched from upstream services at grading time.",
                "Agent configuration files are the repository defaults at this commit. The paper does not say the reported runs used exactly these files, and some differ from Section 3 (STELLA's model, per-agent time limits).",
            ],
        }))

    # Benchmark
    records.append(rec(BENCH, "benchmark", "BioML-bench",
        "Benchmark of autonomous LLM agents on end-to-end biomedical machine learning: an agent reads a task description, builds and runs its own pipeline and submits test-set predictions, which are graded by the task's original metric and placed on that task's public human leaderboard.",
        ["molecular-interactions", "protein-function", "single-cell"], [SRC, REPO], [], {
            "entity_level": "suite",
            "version": "v0.1-alpha; 24-task set listed in experiments/biomlbench_v0.1a.txt at commit 673f3d8 and Table 3 of bioRxiv v3",
            "task": "End-to-end biomedical ML by autonomous agents, scored against public human leaderboards",
            "scope_note": "Four domains: drug discovery (9 tasks), protein engineering (6), single-cell omics (5) and biomedical imaging (4). Only the three molecular and omics domains are recorded; the imaging domain and the all-task Table 2 aggregate (which includes imaging) are out of scope.",
            "source_locator": "Sections 3.1-3.4; Table 1; Table 3; repository README",
            "limitations": [
                "Scores are leaderboard percentiles: they depend on who submitted to each public leaderboard and when, not only on the task metric.",
                "Results are per-domain aggregates over 5 to 9 tasks; per-task values are not printed.",
                "Built on the MLE-bench scaffold; tasks are repackaged from Polaris Hub, ProteinGym and Open Problems with BioML-bench's own preparation scripts.",
            ],
        }))

    # Methods and models
    records.append(rec(f"{P}-method-aide", "method", "AIDE",
        "General-purpose ML engineering agent that searches over candidate code solutions using an LLM.",
        ["molecular-interactions", "protein-function", "single-cell"], [SRC], [], {
            "reported_name": "AIDE", "entity_level": "method",
            "source_locator": "Section 3.3",
            "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the run version is on the configuration"}},
        }, ["foundation_model"]))
    records.append(rec(f"{P}-method-stella", "method", "STELLA",
        "Self-evolving LLM agent for biomedical research.",
        ["molecular-interactions", "protein-function", "single-cell"], [SRC], [], {
            "reported_name": "STELLA", "entity_level": "method",
            "source_locator": "Section 3.3",
            "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; settings are on configurations"}},
        }, ["foundation_model"]))
    records.append(rec(f"{P}-method-mlagentbench", "method", "MLAgentBench research agent",
        "General-purpose ML experimentation agent from the MLAgentBench benchmark.",
        ["molecular-interactions", "protein-function", "single-cell"], [SRC], [], {
            "reported_name": "MLAgentBench", "entity_level": "method",
            "source_locator": "Section 3.3",
            "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; settings are on configurations"}},
        }, ["foundation_model"]))
    records.append(rec(f"{P}-method-dummy-agent", "method", "BioML-bench Dummy agent",
        "Null control that submits uninformative predictions (random or zero depending on the task).",
        ["molecular-interactions", "protein-function", "single-cell"], [SRC], [], {
            "reported_name": "Dummy", "entity_level": "method",
            "source_locator": "Section 3.3, last sentence",
            "missing_metadata": {"version": {"reason": "inapplicable", "note": "Defined by the benchmark itself"}},
        }))
    records.append(rec(f"{P}-model-gpt-4-1", "model", "GPT-4.1",
        "OpenAI language model, used as the LLM backend for AIDE and MLAgentBench in BioML-bench.",
        ["molecular-interactions", "protein-function", "single-cell"], [SRC], [], {
            "entity_level": "service", "reported_name": "GPT-4.1",
            "source_locator": "Section 3.3",
            "missing_metadata": {
                "version": {"reason": "unreported", "note": "The paper prints 'GPT-4.1' only. The repository's AIDE and MLAgentBench configs name gpt-4.1-2025-04-14, but the paper does not say the runs used those files."},
                "checkpoint_revision": {"reason": "unreported"},
                "training_data": {"reason": "unreported"},
            },
        }))
    records.append(rec(f"{P}-model-claude-sonnet-4", "model", "Claude Sonnet 4",
        "Anthropic language model, used as the LLM backend for Biomni in BioML-bench.",
        ["molecular-interactions", "protein-function", "single-cell"], [SRC], [], {
            "entity_level": "service", "reported_name": "Claude Sonnet 4",
            "source_locator": "Section 3.3",
            "missing_metadata": {
                "version": {"reason": "unreported", "note": "The paper prints 'Claude Sonnet 4' only. The repository's Biomni config names claude-sonnet-4-20250514, but the paper does not say the runs used that file."},
                "checkpoint_revision": {"reason": "unreported"},
                "training_data": {"reason": "unreported"},
            },
        }))

    # Configurations
    cfg_common_lim = "Run by the BioML-bench authors in the configuration described in Section 3.3; four replicate runs per task."
    configs = [
        ("Biomni", "Biomni v0.0.5, Claude Sonnet 4 backend (BioML-bench)", [{"relation": "configuration_of", "target_id": "tgtval-20261009-method-biomni"}, {"relation": "uses_model", "target_id": f"{P}-model-claude-sonnet-4"}],
         {"reported_name": "Biomni", "version": "v0.0.5", "parameters": "Biomni (specifically, v0.0.5) with Claude Sonnet 4 as LLM backend; agent class A1 in the repository wrapper (agents/biomni/main.py)",
          "source_locator": "Section 3.3; repository agents/biomni/main.py line 11 ('from biomni.agent import A1')", "access_reuse": "Open-source agent; LLM backend is a hosted API",
          "limitations": [cfg_common_lim]}, ["foundation_model"]),
        ("AIDE", "AIDE v6.3.3, GPT-4.1 backend (BioML-bench)", [{"relation": "configuration_of", "target_id": f"{P}-method-aide"}, {"relation": "uses_model", "target_id": f"{P}-model-gpt-4-1"}],
         {"reported_name": "AIDE", "version": "v6.3.3", "parameters": "AIDE (v6.3.3) with GPT-4.1 as LLM backend. The repository installs it from the fork github.com/AIxBio/aideml_bmlb (agents/aide/requirements.txt).",
          "source_locator": "Section 3.3; repository agents/aide/requirements.txt", "access_reuse": "Open-source agent; LLM backend is a hosted API",
          "limitations": [cfg_common_lim]}, ["foundation_model"]),
        ("MLAgentBench", "MLAgentBench, GPT-4.1 backend (BioML-bench)", [{"relation": "configuration_of", "target_id": f"{P}-method-mlagentbench"}, {"relation": "uses_model", "target_id": f"{P}-model-gpt-4-1"}],
         {"reported_name": "MLAgentBench", "parameters": "MLAgentBench with GPT-4.1 as LLM backend",
          "source_locator": "Section 3.3", "access_reuse": "Open-source agent; LLM backend is a hosted API",
          "missing_metadata": {"version": {"reason": "unreported", "note": "No release or commit of MLAgentBench is printed"}},
          "limitations": [cfg_common_lim]}, ["foundation_model"]),
        ("STELLA", "STELLA, OpenRouter default backend (BioML-bench)", [{"relation": "configuration_of", "target_id": f"{P}-method-stella"}],
         {"reported_name": "STELLA", "parameters": "STELLA with 'the OpenRouter default' as LLM backend (Section 3.3)",
          "source_locator": "Section 3.3", "access_reuse": "Open-source agent; LLM backend is a hosted API",
          "missing_metadata": {"version": {"reason": "unreported", "note": "No release or commit of STELLA is printed"},
                               "model": {"reason": "conflicting", "note": "The paper says STELLA used 'the OpenRouter default' LLM and names no model. The repository config at commit 673f3d8 sets model: claude-sonnet-4 and passes OpenRouter, Anthropic, Gemini and Mem0 keys. No uses_model link is made."}},
          "limitations": [cfg_common_lim]}, ["foundation_model"]),
        ("Dummy", "Dummy agent (BioML-bench)", [{"relation": "configuration_of", "target_id": f"{P}-method-dummy-agent"}],
         {"reported_name": "Dummy", "parameters": "Uninformative predictions, random or zero depending on the task",
          "source_locator": "Section 3.3",
          "missing_metadata": {"version": {"reason": "unreported"}},
          "limitations": ["Null control, not a method anyone would deploy."]}, None),
    ]
    for agent, name, links, attrs, mt in configs:
        records.append(rec(AGENT_INFO[agent]["config"], "configuration", name, "Agent configuration as run in BioML-bench (bioRxiv v3).",
                           ["molecular-interactions", "protein-function", "single-cell"], [SRC, REPO] if "repository" in attrs["source_locator"] else [SRC], links, attrs, mt))

    # Tasks, protocols, datasets
    repo_ids = set(task_list)
    for domain, info in DOMAIN_INFO.items():
        slug = info["slug"]
        proto = f"{P}-protocol-{slug}"
        data = f"{P}-data-{slug}-tasks"
        n = len(info["tasks"])
        task_names = ", ".join(t[0] for t in info["tasks"])
        records.append(rec(data, "dataset_subset", f"BioML-bench v0.1-alpha {domain.lower()} tasks ({n} tasks)",
            f"The {n} {domain.lower()} tasks of BioML-bench v0.1-alpha, as listed in Table 3: {task_names}.",
            info["areas"], [SRC, REPO], [], {
                "subset_scope": f"{n} tasks listed under '{domain if domain != 'Single Cell Omics' else 'Single-cell omics'}' in Table 3. {info['upstream']}",
                "split": info["split"],
                "version": "BioML-bench v0.1-alpha task set (experiments/biomlbench_v0.1a.txt at commit 673f3d8)",
                "source_locator": "Table 3; repository experiments/biomlbench_v0.1a.txt",
                "limitations": ["The paper's Table 3 and the repository task list disagree on three protein engineering assays; see the source limitations."] if slug == "protein-engineering" else [],
            }))
        if slug != "protein-engineering":
            records[-1]["attributes"].pop("limitations")
        records.append(rec(proto, "protocol", f"BioML-bench {domain.lower()} domain: agent leaderboard percentile over {n} tasks",
            f"Each agent runs four independent replicates on each of the {n} {domain.lower()} tasks. Each submission is graded with the task's original metric and mapped to that task's public leaderboard percentile; Table 4 reports domain means and rates.",
            info["areas"], [SRC], [{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": data}], {
                "protocol": "Task capsule per task: task description, training data, test features and a sample submission. The agent designs, implements and runs ML models in a Docker container with a pre-built conda environment and submits test-set predictions, which are validated and graded with the task's original metric. Four independent replicates per agent and task. Scored in two settings: penalized (runs without a valid submission get percentile 0) and non-penalized (such runs are omitted).",
                "version": "BioML-bench v0.1-alpha as reported in bioRxiv v3 (Sections 3.1-3.4, Table 4)",
                "metric": "leaderboard-percentile",
                "metric_direction": "higher",
                "unit": "percent",
                "unit_detail": "percentile of public leaderboard entries, 0 to 100",
                "metric_definition": "Leaderboard percentile: agent score mapped to the public leaderboard percentile for the task (higher is better). Mean rank: average relative rank of an agent compared to the other agents across tasks, based on leaderboard percentile (lower is better). Above-median: proportion of tasks where the agent's mean score exceeds the median human submission. Any-medal: proportion of tasks where the agent achieves a public leaderboard medal threshold, following the MLE-bench definition. Completion rate: proportion of tasks that yield a valid, gradable submission. (Section 3.4, quoted closely.)",
                "selection": f"Tasks: {task_names} (Table 3).",
                "replicates": "Four independent replicates per agent-task combination",
                "hyperparameters": "Compute budget: CPU-only machines with 16 vCPUs and 64 GB RAM and an 8-hour wall-clock limit for non-imaging tasks (Section 3.4)",
                "source_locator": "Sections 3.1, 3.4 and 4.2; Table 3; Table 4 block '" + domain + "'",
                "limitations": [
                    "Leaderboard percentile depends on the composition of each task's public leaderboard; the paper describes the leaderboards as largely expert-populated but does not print their size or snapshot dates.",
                    "Results are domain means over a small number of tasks; per-task values are only shown in figures.",
                    "The plus-or-minus spread in Table 4 is not identified in its caption; Figures 2 and 4 describe the same quantities as mean ± SEM across tasks.",
                    "Above Median, Any Medal and Completion Rate values fit counting replicate runs rather than tasks; the denominator is unresolved.",
                    "The agents were run by the benchmark's authors, not by their developers.",
                ],
            }))
        for tslug, repo_id, desc, detail, upstream in info["tasks"]:
            tid = f"{P}-task-" + re.sub(r"[^a-z0-9]+", "-", tslug.lower()).strip("-")
            links = [{"relation": "part_of", "target_id": BENCH}, {"relation": "parent", "target_id": proto}]
            if upstream:
                links.append({"relation": "part_of", "target_id": upstream})
            if repo_id:
                assert repo_id in repo_ids, repo_id
            attrs = {
                "task": desc,
                "task_type": domain,
                "dataset": detail,
                "version": "BioML-bench v0.1-alpha" + (f"; repository task ID {repo_id}" if repo_id else ""),
                "source_locator": f"Table 3, row '{tslug}'" + ("; repository experiments/biomlbench_v0.1a.txt and task config.yaml" if repo_id else ""),
            }
            if not repo_id:
                attrs["scope_note"] = "Table 3 label does not match the repository task list at commit 673f3d8; " + detail.split("; ", 1)[1] + ". Recorded under the paper's label."
            elif slug == "drug-discovery" and upstream:
                attrs["scope_note"] = "Polaris-hosted TDC benchmark. Linked to the TDC suite only; whether the Polaris split equals the TDC ADMET benchmark group split was not checked, so it is not linked to the TDC ADMET task or dataset records."
            elif slug == "single-cell-omics":
                attrs["scope_note"] = "Adapted from an Open Problems task with BioML-bench's own data preparation; not linked to the Open Problems suite because the split and data differ from the Open Problems benchmark."
            records.append(rec(tid, "task", f"BioML-bench task {tslug}", desc, info["areas"], [SRC, REPO] if repo_id else [SRC], links, attrs))

    # Evaluations and results
    rows = parse_table4(text)
    n_eval = n_res = 0
    skipped = []
    for row in rows:
        if row["domain"] == "Biomedical Imaging":
            continue
        info = DOMAIN_INFO[row["domain"]]
        slug = info["slug"]
        agent = AGENT_INFO[row["agent"]]
        n_tasks = len(info["tasks"])
        eid = f"{P}-eval-{slug}-{row['setting']}-{agent['slug']}"
        block = "Penalized" if row["setting"] == "penalized" else "Non-penalized"
        llm = {"Biomni": "Claude Sonnet 4", "AIDE": "GPT-4.1", "MLAgentBench": "GPT-4.1", "STELLA": "OpenRouter default (model not named)", "Dummy": "none"}[row["agent"]]
        records.append(rec(eid, "evaluation", f"{row['agent']} on BioML-bench {row['domain'].lower()} ({row['setting']})",
            "Published comparison transcribed from the pinned source; not reproduced.", info["areas"], [SRC],
            [{"relation": "system", "target_id": agent["config"]}, {"relation": "assessment", "target_id": f"{P}-protocol-{slug}"}, {"relation": "data", "target_id": f"{P}-data-{slug}-tasks"}], {
                "origin": "independent_paper",
                "protocol": f"{P}-protocol-{slug}",
                "version": "Primary source as retrieved 2026-10-13",
                "comparison": {
                    "protocol_id": f"{P}-protocol-{slug}",
                    "dataset_version": "BioML-bench v0.1-alpha task set (Table 3)",
                    "split": info["split"],
                    "population": f"{n_tasks} {row['domain'].lower()} tasks, four replicate runs per task",
                    "inputs": "Task description, training data, test features and sample submission",
                    "adaptation": f"Autonomous agent builds and trains its own ML pipeline; LLM backend: {llm}",
                    "metric_implementation": "Task's original metric mapped to the task's public leaderboard percentile",
                    "aggregation": "Mean over tasks in the domain; " + SETTING_TEXT[row["setting"]],
                    "budget": "CPU-only, 16 vCPUs, 64 GB RAM, 8-hour wall-clock limit per run",
                },
                "n_runs": 4,
                "source_locator": f"Table 4, block '{block}', domain '{row['domain']}', row '{row['agent']}'",
                "limitations": ["Reported by the benchmark's authors for a system they did not build."],
            }))
        n_eval += 1
        for cell, (col, metric, mslug, direction, unit, unit_detail, qual) in zip(row["cells"], METRICS):
            locator = f"Table 4 (page 12), block '{block}', domain '{row['domain']}', row '{row['agent']}', column '{col}'"
            if cell in ("NA", "-"):
                skipped.append((locator, cell))
                continue
            attrs = {
                "metric": metric,
                "metric_qualifier": f"{qual}; {SETTING_TEXT[row['setting']]}",
                "metric_direction": direction,
                "unit": unit,
                "printed_value": cell,
                "numeric_value": cell.split(" ± ")[0],
                "source_locator": locator,
            }
            if unit_detail:
                attrs["unit_detail"] = unit_detail
            if " ± " in cell:
                attrs["uncertainty"] = {"type": "unresolved_spread", "value": cell.split(" ± ")[1], "printed": "± " + cell.split(" ± ")[1],
                                        "note": "Table 4 caption does not name the spread. Figures 2 and 4 show per-domain leaderboard percentiles as mean ± SEM across tasks; the Table 2 caption refers to the reported SEM."}
            else:
                attrs["missing_metadata"] = {"uncertainty": {"reason": "unreported"}}
            rid = f"{P}-result-{slug}-{row['setting']}-{agent['slug']}-{mslug}"
            attrs["review"] = extraction_review(
                "Deterministic parse of the pdftotext -layout text of the pinned bioRxiv v3 PDF (extract/extract_biomlbench.py), asserting the Table 4 header, 40 rows, block order, domain labels and agent order. Pending independent review.")
            records.append({
                "id": rid, "kind": "result", "name": f"{row['agent']} BioML-bench {row['domain'].lower()} {row['setting']} {col}",
                "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                "status": "needs_review", "facets": {}, "source_ids": [SRC],
                "links": [{"relation": "evaluation", "target_id": eid}], "attributes": attrs,
            })
            claims_rows.append([rid, SRC, locator, cell, "result"])
            n_res += 1

    # Descriptive claims
    def claim(cid, subject, field, value, locator, source):
        records.append(rec(f"{P}-claim-{cid}", "claim", f"{subject.split(P + '-')[-1]}: {field}", "Descriptive fact transcribed from the pinned source.",
                           ["molecular-interactions", "protein-function", "single-cell"], [source], [{"relation": "subject", "target_id": subject}], {
                               "field": field, "value": value, "source_locator": locator,
                               "review": extraction_review("Transcribed by hand from the pinned source text. Pending independent review.")}))
        claims_rows.append([f"{P}-claim-{cid}", source, locator, value, "claim"])

    claim("benchmark-domains", BENCH, "attributes.scope_note",
          "BioML-bench spans four domains (protein engineering, single-cell omics, biomedical imaging, and drug discovery) with tasks that require agents to parse a task description, build a pipeline, implement models, and submit predictions graded by established metrics (e.g., AUROC, Spearman).",
          "Abstract", SRC)
    claim("benchmark-mle-bench", BENCH, "attributes.limitations",
          "The framework is adapted from MLE-bench, but with key modifications to support biomedical contexts.",
          "Section 3.1, first paragraph", SRC)
    claim("benchmark-human-baselines", BENCH, "attributes.limitations",
          "Agent scores are ranked against human leaderboards which are largely expert-populated; public leaderboards inevitably reflect a mix of participant expertise, effort, and compute budgets.",
          "Figure 1 caption; Section 5.1, second paragraph", SRC)
    claim("benchmark-task-list", BENCH, "attributes.version",
          "24 task IDs in experiments/biomlbench_v0.1a.txt: 6 proteingym-dms, 5 manual (Open Problems), 9 polarishub and 4 kaggle tasks.",
          "Repository experiments/biomlbench_v0.1a.txt at commit 673f3d8", REPO)
    claim("benchmark-licence", BENCH, "attributes.licence", "MIT License", "Repository LICENSE at commit 673f3d8 (GitHub licence metadata: MIT)", REPO)
    claim("biomni-version", AGENT_INFO["Biomni"]["config"], "attributes.version", "Biomni (specifically, v0.0.5)", "Section 3.3", SRC)
    claim("biomni-repo-llm", AGENT_INFO["Biomni"]["config"], "attributes.parameters",
          "Repository default for Biomni: llm: claude-sonnet-4-20250514", "Repository agents/biomni/config.yaml at commit 673f3d8, key biomni.kwargs.llm", REPO)
    claim("aide-version", AGENT_INFO["AIDE"]["config"], "attributes.version", "AIDE (v6.3.3)", "Section 3.3", SRC)
    claim("aide-repo-llm", AGENT_INFO["AIDE"]["config"], "attributes.parameters",
          "Repository default for AIDE: agent.code.model and agent.feedback.model gpt-4.1-2025-04-14; installed from git+https://github.com/AIxBio/aideml_bmlb.git",
          "Repository agents/aide/config.yaml and agents/aide/requirements.txt at commit 673f3d8", REPO)
    claim("mlagentbench-repo-llm", AGENT_INFO["MLAgentBench"]["config"], "attributes.parameters",
          "Repository default for MLAgentBench: llm-name, edit-script-llm-name and fast-llm-name gpt-4.1-2025-04-14",
          "Repository agents/mlagentbench/config.yaml at commit 673f3d8", REPO)
    claim("llm-backends", BENCH, "attributes.limitations",
          "At evaluation time, we used the latest compatible LLM backends: GPT-4.1 for MLAgentBench and AIDE, Claude Sonnet 4 for Biomni, and the OpenRouter default for STELLA.",
          "Section 3.3", SRC)
    claim("stella-repo-llm", AGENT_INFO["STELLA"]["config"], "attributes.parameters",
          "Repository default for STELLA: model: claude-sonnet-4, with OpenRouter, Anthropic, Mem0 and Gemini API keys passed; time_limit 57600 seconds",
          "Repository agents/stella/config.yaml at commit 673f3d8", REPO)
    claim("compute-budget", BENCH, "attributes.limitations",
          "Imaging tasks used a single NVIDIA L4 GPU (16 vCPUs, 64 GB RAM) with a 16-hour wall-clock limit. All other tasks used CPU-only machines with identical specifications and an 8-hour limit.",
          "Section 3.4, last paragraph", SRC)

    return records, claims_rows, n_eval, n_res, skipped


def main():
    pdf, repo, out = sys.argv[1:4]
    records, claims_rows, n_eval, n_res, skipped = build(pdf, repo)
    ids = [r["id"] for r in records]
    assert len(ids) == len(set(ids)), "duplicate IDs"
    records.sort(key=lambda r: r["id"])
    out = Path(out)
    with open(out / "batch.jsonl", "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(out / "claims.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
        for row in sorted(claims_rows):
            w.writerow(row)
    counts = {}
    for r in records:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    print(json.dumps({"counts": counts, "evaluations": n_eval, "results": n_res, "skipped_cells": skipped}, indent=1))


if __name__ == "__main__":
    main()
