"""Build batch.jsonl for the PerturbPFN batch (issue #246) from extract/tables.json and hand
transcription of the pinned arXiv v1 PDF text layer.

Usage (from the repository root):
  python3 -I data/omics/perturbpfn-20261115/extract/parse_tables.py
  python3 -I data/omics/perturbpfn-20261115/extract/build.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BATCH = HERE.parent
T = json.loads((HERE / "tables.json").read_text())

P = "perturbpfn-20261115"
PDF_SHA = "42191efa04b45ca04b2be38b51ea374cd9bf891efe2399d331fec9eaeab200b1"
ABS_SHA = "1f42d94a62e4251c24e7e138abd0a4904a6863a3e1ab94c5b155c885c929922a"
TXT_GZ_SHA = "bb23dabbced4f8a40a42d8d0f74c10a0b27b1c54dddbbb53d314bff9c04221c6"
PDF_URL = "https://arxiv.org/pdf/2607.23447v1"
SRC = f"{P}-source-arxiv-v1"
SRC_ABS = f"{P}-source-arxiv-abs"
DATE = "2026-11-15"
RESEARCH = ["research"]
CELL_AREAS = ["single-cell", "cells-tissues"]
NET_AREAS = ["biological-networks", "single-cell"]
SYN_AREAS = ["biological-networks"]

NO_CODE = (
    "The paper links no code repository, weights or checkpoint. On 2026-11-15 a GitHub repository "
    "search for 'perturbpfn' returned 0 repositories, the first author's and Prior Labs' public "
    "repositories hold no PerturbPFN code, and Hugging Face model searches for 'perturbpfn' and "
    "'perturb-pfn' returned nothing. Code and weights access is unknown, not open."
)

REVIEWER = ["claude"]
REVIEWER_NOTE = (
    "Claude (Opus 5.5) extraction agent. Extraction only: no independent review is claimed, and "
    "a different agent reviews this batch."
)
PARSE_NOTE = (
    "Extraction: parsed from the pdftotext -layout text layer (poppler 26.08.0) of the pinned PDF "
    "by extract/parse_tables.py, which finds each table by its caption, asserts every row label "
    "and column header, and asserts that each Table 2 'Avg. ŝ' equals the mean of the three "
    "normalised columns to within 0.00006. The text layer is archived gzipped in artifacts/."
)
HAND_NOTE = (
    "Extraction: transcribed by hand from the pdftotext -layout text layer of the pinned PDF and "
    "checked against the passage the locator names."
)


def review(note=None, hand=False):
    r = {
        "method": (["transcription", "pdf-text-parse", "source-hash-verification"] if hand
                   else ["deterministic-table-parse", "pdf-text-parse", "source-hash-verification"]),
        "method_note": HAND_NOTE if hand else PARSE_NOTE,
        "reviewer": REVIEWER,
        "reviewer_note": REVIEWER_NOTE,
        "date": DATE,
        "artifact_sha256": PDF_SHA,
        "retrieval_url": PDF_URL,
    }
    if note:
        r["note"] = note
    return r


records = []


def rec(id_, kind, name, description, attributes, links=(), areas=CELL_AREAS, method_types=None,
        source_ids=(SRC,)):
    facets = {"areas": list(areas), "contexts": RESEARCH}
    if method_types:
        facets["method_types"] = list(method_types)
    r = {
        "attributes": attributes,
        "description": description,
        "facets": facets,
        "id": id_,
        "kind": kind,
        "links": [{"relation": a, "target_id": b} for a, b in links],
        "name": name,
        "source_ids": list(source_ids),
        "status": "needs_review",
    }
    records.append(r)
    return r


def link(r):
    return r["id"]


# ---------------------------------------------------------------- sources
rec(
    SRC, "source",
    "PerturbPFN: Probing the Limits of Synthetic Priors in Drug Perturbation Modelling (arXiv:2607.23447v1)",
    "Workshop paper by Yuche Gao, José Miguel Hernández-Lobato and Siyuan Guo introducing PerturbPFN and evaluating it on synthetic episodes, Sci-Plex and GeneRNIB 300BCG.",
    {
        "url": PDF_URL,
        "artifact_url": PDF_URL,
        "version": "arXiv v1, submitted 2026-07-26",
        "retrieved_at": "2026-11-15T20:27:40Z",
        "artifact_sha256": PDF_SHA,
        "doi": "10.48550/arXiv.2607.23447",
        "publication_status": "preprint",
        "licence": "CC-BY-4.0",
        "media_type": "application/pdf",
        "venue": "2nd ICML Workshop on Foundation Models for Structured Data (FMSD 2026), Seoul (page 1 footer; arXiv comments field)",
        "year": 2026,
        "hash_scope": "Exact bytes of the PDF. Three downloads on 2026-11-15 (20:22Z to 20:27Z) gave identical bytes.",
        "archive_sha256": TXT_GZ_SHA,
        "archive_note": "artifacts/arxiv-2607.23447v1.pdftotext-layout.txt.gz is the gzipped (gzip -n -9) pdftotext -layout text layer (poppler 26.08.0) every table value was parsed from. The PDF is refetchable at the versioned URL and is not archived.",
        "source_locator": "Whole paper, 19 pages: Sections 1 to 5 and Appendices A to E",
        "limitations": [
            "arXiv preprint of a workshop paper; the evaluations are run and reported by the model's authors.",
        ],
        "missing_metadata": {
            "code_url": {"reason": "unavailable", "note": NO_CODE},
        },
        "review": review(hand=True, note="PDF hash recomputed on each of three downloads; licence and submission date read from the arXiv abstract page (companion source)."),
    },
    areas=CELL_AREAS + ["biological-networks"], source_ids=(),
)
rec(
    SRC_ABS, "source",
    "arXiv abstract page for 2607.23447 (PerturbPFN)",
    "arXiv listing page for PerturbPFN, giving the submission date, version history, comments field and article licence.",
    {
        "url": "https://arxiv.org/abs/2607.23447",
        "version": "Page as served on 2026-11-15, listing v1 only",
        "retrieved_at": "2026-11-15T20:27:34Z",
        "artifact_sha256": ABS_SHA,
        "publication_status": "preprint",
        "licence": "CC-BY-4.0",
        "media_type": "text/html",
        "hash_scope": "Mutable web page; the hash describes one retrieval. Two fetches of this URL on 2026-11-15 gave identical bytes; the v1-suffixed URL serves different bytes (its title carries 'v1').",
        "source_locator": "Submission history ('[v1] ... 26 Jul 2026'); Comments field; licence link to creativecommons.org/licenses/by/4.0",
        "review": review(hand=True),
    },
    links=[("companion_of", SRC)], areas=CELL_AREAS + ["biological-networks"], source_ids=(),
)

# ---------------------------------------------------------------- PerturbPFN
MODEL = f"{P}-model-perturbpfn"
rec(
    MODEL, "model", "PerturbPFN",
    "PerturbPFN is a transformer trained only on simulated perturbation episodes that, given observed responses to other perturbations in context, infers a latent gene graph, sparse intervention targets and strengths and rolls them through a causal decoder to predict the expression distribution under a new perturbation.",
    {
        "entity_level": "family",
        "reported_name": "PerturbPFN",
        "version": "As described in arXiv:2607.23447v1; one checkpoint is reported, step 3100 of a 3,500-step run with seed 17",
        "training_data": "Prior-predictive synthetic episodes only: modular scale-free gene graphs of 40 to 60 genes, synthetic drug families with Hill-type dose-response strengths, and zero-inflated log-normal observations with SERGIO noise; no real perturbation responses are used for training (Section 2.3, Appendix A, Tables 4 and 5).",
        "access": "Not openly available as checked. " + NO_CODE,
        "provenance_note": "Registered from the authors' preprint. Kept at family level: the reported step-3100 checkpoint is named in the paper but no weights or hash are published; the configurations carry the checkpoint identity.",
        "source_locator": "Abstract; Sections 2.2 to 2.5; Appendices A and B; Tables 6 and 7",
        "missing_metadata": {
            "licence": {"reason": "unavailable", "note": "The article is CC BY 4.0, which covers the text only. No code or weights licence exists to read because no release was found. " + NO_CODE},
            "checkpoint_revision": {"reason": "unavailable", "note": "No weights are published, so no checkpoint hash can be recorded."},
        },
        "review": review(hand=True),
    },
    areas=CELL_AREAS + ["biological-networks"], method_types=["specialist"],
)

CHECKPOINT = "Training step 3100 of a 3,500-step run (2,500 structure-pretraining steps, 500 graph-GT joint steps, 500 soft-graph continuation steps), random seed 17, selected on a development set (Table 7, Appendix B)"
CFG_ICL = f"{P}-config-perturbpfn-step3100"
rec(
    CFG_ICL, "configuration", "PerturbPFN step-3100 checkpoint, in-context forward pass",
    "Configures PerturbPFN as the step-3100 checkpoint applied with one forward pass and no parameter updates, extracting a hard graph by prior-density calibration and greedy DAG projection and gating targets with a top-3 straight-through gate.",
    {
        "reported_name": "PerturbPFN",
        "checkpoint": CHECKPOINT,
        "parameters": "14.98M parameters (Table 6)",
        "hyperparameters": "At most 60 nodes and an 11-dimensional regime descriptor per pass; shared encoder 192 hidden, 6 heads, 5 blocks; structure encoder 256 hidden, 8 heads, 4 blocks; top-k target gate k = 3; strength head 81 bins on [-2, 2]; SCM decoder 64 hidden, 2 layers (Table 6). Hard projected graph used at test time (Section 2.4).",
        "training_setting": "Synthetic-only pretraining with AdamW, learning rate 3e-4, weight decay 1e-4, batch size 8, 20 context and 4 query regimes per episode; the complete 3,500-step run took about 1.44 GPU-hours on one NVIDIA RTX 4090 (Table 7, Appendix B).",
        "accelerator_details": "Training and the Table 2 timings on a single NVIDIA RTX 4090 (24 GB)",
        "version": "Step 3100, as reported in arXiv:2607.23447v1",
        "access_reuse": NO_CODE,
        "provenance_note": "The paper states that every reported result uses this one checkpoint without parameter updates (Section 4, Appendix B).",
        "source_locator": "Sections 2.4, 2.5 and 4; Appendix B; Tables 6 and 7",
        "missing_metadata": {
            "checkpoint_sha256": {"reason": "unavailable", "note": "Weights are not published."},
            "code_commit": {"reason": "unavailable", "note": NO_CODE},
        },
        "review": review(hand=True),
    },
    links=[("configuration_of", MODEL)], areas=CELL_AREAS + ["biological-networks"], method_types=["specialist"],
)
CFG_GRN = f"{P}-config-perturbpfn-step3100-genernib-panels"
rec(
    CFG_GRN, "configuration", "PerturbPFN step-3100 checkpoint, GeneRNIB panel aggregation",
    "Configures PerturbPFN as the step-3100 checkpoint run on 190 overlapping panels of 20 transcription factors and 40 target genes, averaging continuous edge probabilities over 32 sampled episodes per panel and keeping the top 50,000 TF-gene links.",
    {
        "reported_name": "PerturbPFN",
        "checkpoint": CHECKPOINT,
        "parameters": "14.98M parameters (Table 6)",
        "hyperparameters": "Input: 380 log-normalised inference profiles; 100 highest-variance TF seeds from the official GeneRNIB TF list and 1,500 candidate target genes; 20 TFs and 40 targets per panel, 190 panels; 32 episodes per panel of 64 context and 16 query profiles; edge score = mean edge probability over episodes, maximum over overlapping panels; continuous unthresholded probabilities exported, not the projected DAG; at most 50,000 links (Table 8, Appendix E.2).",
        "version": "Step 3100, as reported in arXiv:2607.23447v1",
        "access_reuse": NO_CODE,
        "source_locator": "Section 4.3; Appendix E.1 and E.2; Table 8",
        "missing_metadata": {
            "checkpoint_sha256": {"reason": "unavailable", "note": "Weights are not published."},
            "code_commit": {"reason": "unavailable", "note": NO_CODE},
        },
        "review": review(hand=True),
    },
    links=[("configuration_of", MODEL)], areas=NET_AREAS, method_types=["specialist"],
)

# ---------------------------------------------------------------- Sci-Plex benchmark
BENCH_SP = f"{P}-benchmark-sciplex-highest-dose"
PROT_SP = f"{P}-protocol-sciplex-highest-dose-normalised"
DATA_SP = f"{P}-data-sciplex-hdac-3x4"
SP_LIMITS = [
    "Dose extrapolation, not unseen-drug prediction: lower doses of the held-out drug are in the context (Appendix D.2).",
    "Table 2 prints only min-max normalised scores; each normalised value depends on which seven rows are compared, so the numbers are not comparable with any other study or comparison set (Appendix D.3). Raw MD, Pearson r and W2 appear only as box plots in Figure 2 with no printed values.",
    "Four HDAC inhibitors in three cell lines and 50 marker genes per protocol; a small slice of Sci-Plex.",
    "Run and reported by the PerturbPFN authors, who also ran every baseline.",
    "No uncertainty is printed for the normalised scores, and no seeds or repeated runs are reported.",
]
rec(
    BENCH_SP, "benchmark", "Sci-Plex highest-dosage holdout benchmark (GIM protocol)",
    "Twelve cell line and drug protocols from Sci-Plex in which a model predicts the single-cell expression distribution at a drug's highest dose from controls, the drug's lower doses and the other drugs' doses.",
    {
        "entity_level": "suite",
        "task": "Predict the expression distribution of cells at a held-out highest drug dose",
        "version": "As run in arXiv:2607.23447v1, following the highest-dosage holdout protocol and preprocessing of Schneider et al. 2025 (GIM, ICML 2025)",
        "scope_note": "A549, K562 and MCF7 crossed with belinostat, dacinostat, givinostat and quisinostat 2HCl, each pair one protocol. Cells normalised to the median control count, filtered, log-transformed and restricted to 50 marker genes chosen per protocol from training conditions only.",
        "limitations": SP_LIMITS,
        "source_locator": "Section 4.2; Appendix D.1 and D.2",
        "missing_metadata": {
            "split_manifest": {"reason": "unavailable", "note": "No cell lists, marker-gene lists or code are published with the paper; the protocol is said to follow the GIM codebase, which was not retrieved for this batch."},
        },
        "review": review(hand=True),
    },
    links=[("evaluates_task", "catalog-task-cell-perturbation")],
)
rec(
    DATA_SP, "dataset_subset", "Sci-Plex HDAC-inhibitor subset, 3 cell lines by 4 drugs (GIM preprocessing)",
    "Sci-Plex single-cell profiles of A549, K562 and MCF7 cells treated with belinostat, dacinostat, givinostat or quisinostat 2HCl at several doses, plus controls, preprocessed as in the GIM benchmark.",
    {
        "source_dataset": "Sci-Plex, Srivatsan et al. 2020, Science 367(6473):45-51 (reference [20])",
        "subset_scope": "Cell lines A549, K562, MCF7; drugs belinostat, dacinostat, givinostat, quisinostat 2HCl; all doses of these drugs and control cells",
        "split": "Per cell line and drug pair (12 protocols): the drug's highest dose is the query; context is the control cells, the drug's lower doses and all available doses of the other three drugs in the same cell line",
        "version": "Preprocessed epigenetic-regulation benchmark of Schneider et al. 2025, as used in arXiv:2607.23447v1 Appendix D.1",
        "source_locator": "Appendix D.1 and D.2",
        "missing_metadata": {
            "test_count": {"reason": "unreported", "note": "Cell counts per condition and the number of doses per drug are not printed."},
            "exact_manifest": {"reason": "unavailable", "note": "No cell list or marker-gene list is published."},
        },
        "review": review(hand=True, note="The two existing Srivatsan20 subsets in the store are PerturBench covariate-transfer splits over the full compound panel; linked with same_data_as as the same underlying Sci-Plex measurements, not the same split."),
    },
    links=[("used_in", PROT_SP),
           ("same_data_as", "lit-cells-networks-20261011-perturbench-v4-data-srivatsan20"),
           ("same_data_as", "perturbench-dataset-srivatsan20")],
)
NORM_DEF = (
    "\"For Table 2, each metric is oriented so that higher is better and min-max normalized within each protocol ... "
    "We first average each normalized metric across the 12 protocols and then average the three metric scores to obtain the overall score and rank. "
    "These normalized scores depend on the included comparison set.\" (Appendix D.3)"
)
rec(
    PROT_SP, "protocol", "Sci-Plex highest-dose holdout with min-max normalised MD, Pearson r and W2 (PerturbPFN Table 2)",
    "Hold out each drug's highest dose in each of 12 cell line and drug pairs, predict the held-out cell distribution, score mean distance, Pearson r and Sinkhorn W2, min-max normalise each across the compared methods within a protocol and average over protocols.",
    {
        "protocol": "For each of the 12 cell line and drug pairs, the highest dose is removed from the context and used as the query. Context: control cells, lower doses of the held-out drug and all available doses of the remaining drugs in the same cell line. The method predicts the distribution of expression vectors at the held-out dose without observing drug targets. All methods are scored on the same held-out cells with the same metric code.",
        "allowed_information": "Control cells; drug identity and dose descriptors; expression of all context conditions. Drug targets are not given. PerturbPFN makes no parameter updates; GIM, CondOT, MLP and RF X-Learner are fitted per protocol on its training conditions.",
        "heldout_test": ["Highest dose of the protocol's drug in the protocol's cell line"],
        "metric_definition": "MD = || E[X_pred] - E[X_true] ||_2; r = Pearson correlation of the predicted and true mean-expression vectors over genes; W2 approximated as the square root of the debiased entropic Sinkhorn cost with squared-Euclidean ground cost, epsilon 0.1, at most 200 iterations, tolerance 1e-6, on equally sized deterministically sampled cell sets (Appendix D.3). " + NORM_DEF,
        "aggregation": "Per metric: min-max normalisation across the seven compared rows within each protocol, then the mean over 12 protocols. Overall: mean of the three metric means; rank by overall score.",
        "metric_implementation": "Same metric code for every method, recomputed from prediction arrays 'whenever prediction arrays are available' (Appendix D.4).",
        "publication_status": "preprint",
        "version": "arXiv:2607.23447v1",
        "limitations": SP_LIMITS,
        "source_locator": "Section 4.2; Appendix D; Table 2",
        "missing_metadata": {
            "random_seeds": {"reason": "unreported", "note": "No seeds or repeated runs are reported for any method."},
        },
        "review": review(hand=True),
    },
    links=[("part_of", BENCH_SP), ("uses_data", DATA_SP), ("evaluates_task", "catalog-task-cell-perturbation")],
)

# Sci-Plex baselines
NO_CHANGE = "perturbation-ahlmann-20261011-method-no-change"
methods = {}


def method(key, name, reported, description, locator, mtypes, areas=CELL_AREAS, version_note=None, extra=None):
    id_ = f"{P}-method-{key}"
    attrs = {
        "entity_level": "method",
        "reported_name": reported,
        "source_locator": locator,
        "provenance_note": "Registered from its use as a comparator in arXiv:2607.23447v1; the method's own paper was not retrieved for this batch.",
        "missing_metadata": {"version": {"reason": "unreported", "note": version_note or "No software version is printed."}},
        "review": review(hand=True),
    }
    if extra:
        attrs.update(extra)
    rec(id_, "method", name, description, attrs, areas=areas, method_types=mtypes)
    methods[key] = id_
    return id_


method("gim", "GIM (generative intervention model)", "GIM",
       "Learns a generative map from perturbation descriptors to latent atomic interventions (targets and strengths) in a causal model whose graph it also learns, fitting each dataset by optimisation, and predicts post-intervention expression.",
       "Section 3 'Structured perturbation models'; Appendix D.4 'GIM'; reference [4]", ["specialist"])
method("condot", "CondOT", "CondOT",
       "Learns a perturbation-conditioned optimal-transport map from control cells to treated-cell distributions and predicts treated cells by transporting sampled control cells.",
       "Section 3; Appendix D.4 'CondOT'; reference [31]", ["specialist"])
method("mlp-shift", "MLP shift regression", "MLP",
       "Regresses the mean expression shift relative to control from the perturbation descriptor with a multilayer perceptron and adds the predicted shift to sampled control cells.",
       "Appendix D.4 'MLP'", ["supervised_machine_learning"])
method("rf-x-learner", "RF X-Learner", "RF X-Learner",
       "Applies the X-learner treatment-effect strategy with random-forest regressors to perturbation descriptors and adds a constant-weight mixture of the two fitted effect models to sampled control cells.",
       "Appendix D.4 'RF X-Learner'; reference [41]", ["supervised_machine_learning"])
method("naive-lower-dose", "Naive nearest-lower-dose baseline", "Naive",
       "Predicts the response at a held-out highest dose as the observed response at the nearest lower dose of the same drug in the same cell line.",
       "Section 4.2 'Baselines'; Appendix D.4 'Naive and Observational'", ["conventional_pipeline"],
       version_note=None, extra={"missing_metadata": {"version": {"reason": "inapplicable", "note": "A rule with no software version."}}})

CFG = {}


def config(key, name, description, method_id, hyper, locator, mtypes):
    id_ = f"{P}-config-{key}"
    rec(id_, "configuration", name, description, {
        "reported_name": name.split(" (")[0],
        "hyperparameters": hyper,
        "version": "As run in arXiv:2607.23447v1 Appendix D.4",
        "provenance_note": "Run by the PerturbPFN authors on each held-out protocol.",
        "source_locator": locator,
        "missing_metadata": {"code_commit": {"reason": "unreported", "note": "No code commit or package version is printed."}},
        "review": review(hand=True),
    }, links=[("configuration_of", method_id)], method_types=mtypes)
    CFG[key] = id_
    return id_


config("gim-sciplex", "GIM (Sci-Plex configuration, PerturbPFN Table 2)",
       "Configures GIM with the Sci-Plex settings of the GIM codebase, fitted separately to each held-out protocol for 100,000 optimisation steps.",
       methods["gim"],
       "Authors' implementation and Sci-Plex preprocessing; nonlinear zero-inflated log-normal inference model; unknown intervention targets; Adam, step size 1e-3; graph-prior and intervention-sparsity penalties; augmented-Lagrangian acyclicity; 100,000 optimisation steps; fitted per held-out protocol",
       "Appendix D.4 'GIM'", ["specialist"])
config("condot-sciplex", "CondOT (PICNN, PerturbPFN Table 2)",
       "Configures CondOT with the PICNN implementation of the GIM benchmark, two four-layer 128-unit potentials trained for 100,000 alternating steps, fitted separately to each held-out protocol.",
       methods["condot"],
       "PICNN implementation from the GIM benchmark; descriptors encode drug identity and dose; two transport potentials, each four hidden layers of 128 units; 100,000 alternating steps; Adam, learning rate 1e-4, betas (0.5, 0.9); fitted per protocol on its training conditions",
       "Appendix D.4 'CondOT'", ["specialist"])
config("mlp-shift-sciplex", "MLP shift regression (GIM codebase, PerturbPFN Table 2)",
       "Configures the shift-regression MLP of the GIM codebase as a two-layer regressor with hidden size 100 trained for at most 20,000 iterations.",
       methods["mlp-shift"],
       "Two-layer MLP regressor, hidden size 100, learning rate 1e-3, at most 20,000 iterations; follows the shift-regression baseline of the GIM codebase",
       "Appendix D.4 'MLP'", ["supervised_machine_learning"])
config("rf-x-learner-sciplex", "RF X-Learner (100-tree random forest, PerturbPFN Table 2)",
       "Configures the X-learner with a multi-output random forest of 100 trees, no depth limit, the full training data and z-scored targets.",
       methods["rf-x-learner"],
       "Multi-output RandomForestRegressor, 100 trees, no maximum depth, full training data, no downsampling; targets z-scored for fitting and transformed back for evaluation",
       "Appendix D.4 'RF X-Learner'", ["supervised_machine_learning"])

SP_SYSTEMS = {
    "RF X-Learner": (CFG["rf-x-learner-sciplex"], "rf-x-learner", "Fitted per protocol on its training conditions (global response model, then two effect models)", "Random forest of 100 trees per protocol"),
    "CondOT": (CFG["condot-sciplex"], "condot", "Fitted per protocol on its training conditions", "100,000 alternating optimisation steps per protocol"),
    "MLP": (CFG["mlp-shift-sciplex"], "mlp", "Fitted per protocol on its training conditions", "At most 20,000 iterations per protocol"),
    "GIM": (CFG["gim-sciplex"], "gim", "Fitted per protocol by instance-specific optimisation", "100,000 optimisation steps per protocol"),
    "Naive": (methods["naive-lower-dose"], "naive", "None: a rule applied to the observed lower doses", "No fitting"),
    "Observational": (NO_CHANGE, "observational", "None: predicts the control distribution", "No fitting"),
    "PerturbPFN": (CFG_ICL, "perturbpfn", "None: one forward pass of the synthetic-pretrained step-3100 checkpoint, no parameter updates", "One forward pass per protocol; pretraining about 1.44 GPU-hours on one RTX 4090, done once"),
}

SP_COMPARISON = {
    "protocol_id": PROT_SP,
    "dataset_version": "Sci-Plex subset preprocessed as in the GIM benchmark (Schneider et al. 2025): median-control-count normalisation, filtering, log transform, 50 marker genes per protocol chosen from training conditions",
    "split": "Per cell line and drug pair, the highest dose is the query; context is controls, lower doses of that drug and all doses of the other three drugs in the same cell line",
    "population": "12 protocols: A549, K562 and MCF7 by belinostat, dacinostat, givinostat and quisinostat 2HCl",
    "inputs": "Control cells, drug identity and dose descriptors and the expression of every context condition; no drug targets",
    "metric_implementation": "MD, Pearson r of mean vectors and debiased Sinkhorn W2 (epsilon 0.1, 200 iterations, tolerance 1e-6), each oriented higher-is-better and min-max normalised across the seven Table 2 rows within each protocol",
    "aggregation": "Mean over 12 protocols per metric; overall score is the mean of the three metric means",
}

SCORE_COLS = [
    ("sMD", "ŝMD ↑", "min-max-normalised-score",
     "Mean distance (L2 distance between predicted and observed mean expression over the 50 marker genes), negated, then min-max normalised across the seven Table 2 rows within each of 12 Sci-Plex highest-dose protocols and averaged over protocols"),
    ("sr", "ŝr ↑", "min-max-normalised-score",
     "Pearson correlation between predicted and observed mean expression over the 50 marker genes, min-max normalised across the seven Table 2 rows within each of 12 Sci-Plex highest-dose protocols and averaged over protocols"),
    ("sW2", "ŝW2 ↑", "min-max-normalised-score",
     "Debiased Sinkhorn 2-Wasserstein distance between predicted and observed cell sets (epsilon 0.1), negated, then min-max normalised across the seven Table 2 rows within each of 12 Sci-Plex highest-dose protocols and averaged over protocols"),
]
AVG_Q = "Equal-weight mean of the three protocol-averaged min-max normalised scores (mean distance, Pearson r, Sinkhorn W2) across the seven Table 2 rows on 12 Sci-Plex highest-dose protocols"
RANK_Q = "Rank of the overall normalised score among the seven Table 2 rows on 12 Sci-Plex highest-dose protocols"
RUNTIME_Q = "Mean wall-clock seconds per Sci-Plex highest-dose protocol on one NVIDIA RTX 4090 worker, without any one-time pretraining cost"
RUNTIME_AMORT_Q = "Mean wall-clock seconds per Sci-Plex highest-dose protocol on one NVIDIA RTX 4090 worker, plus PerturbPFN's one-time pretraining cost divided across the 12 protocols"
NORM_LIMIT = "Min-max normalised within the seven compared rows: the value changes if a method is added or removed, so it is comparable only within Table 2."
SD_SCOPE = "Table 2 caption: 'Times are mean ± standard deviation'; what the spread is taken over (presumably the 12 protocols) is not stated"

results = 0


def result(id_, eval_id, name, printed, numeric, metric, direction, unit, qualifier, locator,
           uncertainty=None, missing_unc=True, limitations=None, note=None, hand=False, unit_detail=None,
           areas=CELL_AREAS):
    global results
    attrs = {
        "printed_value": printed,
        "numeric_value": numeric,
        "metric": metric,
        "metric_direction": direction,
        "metric_qualifier": qualifier,
        "unit": unit,
        "source_locator": locator,
        "review": review(note=note, hand=hand),
    }
    if unit_detail:
        attrs["unit_detail"] = unit_detail
    if uncertainty:
        attrs["uncertainty"] = uncertainty
    elif missing_unc:
        attrs["missing_metadata"] = {"uncertainty": {"reason": "unreported", "note": "No spread is printed for this value."}}
    if limitations:
        attrs["limitations"] = limitations
    rec(id_, "result", name,
        "Value transcribed as printed in arXiv:2607.23447v1. Author-reported; not reproduced by Rewire.",
        attrs, links=[("evaluation", eval_id)], areas=areas)
    results += 1


def sd(printed_time):
    mean, spread = printed_time.split(" ± ")
    return mean, {"type": "standard_deviation", "value": spread, "printed": "± " + spread, "scope": SD_SCOPE}


for row in T["table2"]:
    model = row["model"]
    system, key, adaptation, budget = SP_SYSTEMS[model]
    ev = f"{P}-eval-sciplex-{key}"
    comparison = dict(SP_COMPARISON, adaptation=adaptation, budget=budget)
    eattrs = {
        "origin": "author_reported",
        "protocol": PROT_SP,
        "comparison": comparison,
        "version": "arXiv:2607.23447v1",
        "source_locator": f"Table 2, row '{model}'" if model != "PerturbPFN" else "Table 2, rows 'PerturbPFN (amortized)' and 'PerturbPFN (ICL only)' and their shared score line",
        "limitations": [
            "Run by the PerturbPFN authors, who developed the proposed method and ran every comparator.",
            NORM_LIMIT,
        ],
        "review": review(),
    }
    if model in ("Naive", "Observational"):
        eattrs["missing_metadata"] = {"timing_seconds": {"reason": "inapplicable", "note": "Table 2 prints '/' in the time column for this training-free baseline."}}
    rec(ev, "evaluation", f"{model} on the Sci-Plex highest-dose holdout (PerturbPFN Table 2)",
        "Author-reported evaluation transcribed from the pinned preprint; run by the PerturbPFN authors and not reproduced by Rewire.",
        eattrs, links=[("system", system), ("assessment", PROT_SP), ("data", DATA_SP)])

    if model == "PerturbPFN":
        loc_scores = "Table 2, unlabelled score line printed between the rows 'PerturbPFN (amortized)' and 'PerturbPFN (ICL only)', column '{}'"
        for which, field, q, label in (("icl-only", "time_icl_only", RUNTIME_Q, "PerturbPFN (ICL only)"),
                                        ("amortized", "time_amortized", RUNTIME_AMORT_Q, "PerturbPFN (amortized)")):
            mean, unc = sd(row[field])
            result(f"{P}-result-sciplex-perturbpfn-runtime-{which}", ev,
                   f"{label}: time per protocol, Sci-Plex highest-dose holdout", mean, mean, "runtime", "lower", "second", q,
                   f"Table 2, row '{label}', column 'Time (s) / protocol'", uncertainty=unc,
                   note="The amortized time adds the one-time pretraining cost spread over the 12 protocols, so it is not a per-protocol inference time." if which == "amortized" else None)
    else:
        loc_scores = f"Table 2, row '{model}', column '{{}}'"
        if row["time"] != "/":
            mean, unc = sd(row["time"])
            result(f"{P}-result-sciplex-{key}-runtime", ev, f"{model}: time per protocol, Sci-Plex highest-dose holdout",
                   mean, mean, "runtime", "lower", "second", RUNTIME_Q,
                   f"Table 2, row '{model}', column 'Time (s) / protocol'", uncertainty=unc)
    for field, header, metric, q in SCORE_COLS:
        result(f"{P}-result-sciplex-{key}-{field.lower()}", ev, f"{model}: {header.split(' ')[0]}, Sci-Plex highest-dose holdout",
               row[field], row[field], metric, "higher", "unitless", q, loc_scores.format(header), limitations=[NORM_LIMIT])
    result(f"{P}-result-sciplex-{key}-avg-score", ev, f"{model}: overall normalised score, Sci-Plex highest-dose holdout",
           row["avg"], row["avg"], "weighted-composite-score", "higher", "unitless", AVG_Q,
           loc_scores.format("Avg. ŝ / rank") + ", score before the bracket", limitations=[NORM_LIMIT],
           note="Recomputed as the mean of the three printed normalised columns; agrees to within 0.00006.")
    result(f"{P}-result-sciplex-{key}-rank", ev, f"{model}: overall rank, Sci-Plex highest-dose holdout",
           "(" + row["rank"] + ")", row["rank"].lstrip("#"), "rank", "lower", "unitless", RANK_Q,
           loc_scores.format("Avg. ŝ / rank") + ", bracketed rank", missing_unc=False, limitations=[NORM_LIMIT])

# ---------------------------------------------------------------- in-prior synthetic recovery
PROT_IP = f"{P}-protocol-in-prior-latent-recovery"
DATA_IP = f"{P}-data-in-prior-synthetic-episodes"
IP_LIMITS = [
    "In-prior evaluation: the episodes come from the same synthetic prior the model was trained on, so it tests amortised inference under that prior, not transfer to biology (Section 4.1).",
    "Only PerturbPFN is scored; no baseline is run on these episodes.",
    "No uncertainty is printed.",
]
rec(
    DATA_IP, "dataset", "PerturbPFN synthetic prior, 1,024 held-out episodes",
    "Fresh episodes sampled from PerturbPFN's hierarchical synthetic prior, each a 40 to 60 gene modular graph with synthetic drugs, dose-dependent sparse targets and simulated zero-inflated log-normal responses, with the true graph, targets and strengths known.",
    {
        "total": 1024,
        "scope_note": "1,024 fresh episodes (Section 4.1), scored as 128 held-out synthetic batches (Table 1 caption) of batch size 8 (Table 7). Edge prevalence 0.0363 (Section 4.1 Results). Prior settings in Tables 4 and 5.",
        "version": "Synthetic prior of the final checkpoint, arXiv:2607.23447v1 Appendix A",
        "split": "Held-out episodes drawn fresh from the prior; not used in training",
        "source_locator": "Section 4.1; Table 1 caption; Appendix A; Tables 4, 5 and 7",
        "missing_metadata": {
            "manifest": {"reason": "unavailable", "note": "Episodes are generated on the fly; no seed or simulator code is published."},
        },
        "review": review(hand=True),
    },
    areas=SYN_AREAS,
)
rec(
    PROT_IP, "protocol", "PerturbPFN in-prior latent recovery on held-out synthetic episodes (Table 1)",
    "Score the model's inferred graph, intervention targets, strengths and predicted responses against the known latent variables of fresh episodes from its own synthetic prior.",
    {
        "protocol": "Apply the checkpoint to fresh prior episodes. Graph AUROC and AUPRC rank all directed non-self edges by predicted probability; projected F1 keeps the top-scoring edges up to the true edge count, skipping edges that would form a cycle. Target AUROC and AUPRC use node-wise target probabilities; target F1 thresholds them at 0.5. Strength ratio = mean |predicted strength| over mean |true strength| on true target nodes. Delta cosine compares centred predicted and true mean response shifts relative to control. Observation NLL is the mean negative log-likelihood of query responses under the predicted zero-inflated log-normal (Section 4.1, Appendix C).",
        "version": "arXiv:2607.23447v1",
        "publication_status": "preprint",
        "limitations": IP_LIMITS,
        "task_link_exemption": "A check of the model's own latent variables under its synthetic training prior; no catalogue task covers it.",
        "source_locator": "Section 4.1; Appendix C; Table 1",
        "review": review(hand=True),
    },
    links=[("uses_data", DATA_IP)], areas=SYN_AREAS,
)
EV_IP = f"{P}-eval-in-prior-perturbpfn"
rec(EV_IP, "evaluation", "PerturbPFN on in-prior latent recovery (PerturbPFN Table 1)",
    "Author-reported evaluation transcribed from the pinned preprint; run by the PerturbPFN authors and not reproduced by Rewire.",
    {
        "origin": "author_reported",
        "protocol": PROT_IP,
        "comparison": {
            "protocol_id": PROT_IP,
            "dataset_version": "1,024 fresh episodes from the synthetic prior of the final checkpoint",
            "split": "Held-out synthetic episodes",
            "population": "128 batches of 8 episodes",
            "inputs": "Context regime descriptors and condition-level mean responses; no target or graph labels",
            "adaptation": "None: one forward pass, no parameter updates",
            "metric_implementation": "Appendix C definitions",
            "aggregation": None,
            "budget": None,
        },
        "version": "arXiv:2607.23447v1",
        "source_locator": "Table 1; Section 4.1 Results",
        "limitations": IP_LIMITS,
        "missing_metadata": {"aggregation": {"reason": "unreported", "note": "Whether metrics are pooled over all episodes or averaged over batches is not stated."}},
        "review": review(),
    },
    links=[("system", CFG_ICL), ("assessment", PROT_IP), ("data", DATA_IP)], areas=SYN_AREAS)

T1 = {
    ("Graph", "AUROC ↑"): ("graph-auroc", "auroc", "higher", "Latent graph: all directed non-self edges ranked by predicted edge probability; PerturbPFN in-prior synthetic episodes"),
    ("Graph", "AUPRC ↑"): ("graph-auprc", "auprc", "higher", "Latent graph: all directed non-self edges ranked by predicted edge probability, edge prevalence 0.0363; PerturbPFN in-prior synthetic episodes"),
    ("Graph", "Proj. F1 ↑"): ("graph-projected-f1", "f1-score", "higher", "Latent graph edges after keeping the top-scoring acyclic edges up to the true edge count (density-matched DAG projection); PerturbPFN in-prior synthetic episodes"),
    ("Target", "AUROC ↑"): ("target-auroc", "auroc", "higher", "Intervention targets: node-wise target probabilities; PerturbPFN in-prior synthetic episodes"),
    ("Target", "AUPRC ↑"): ("target-auprc", "auprc", "higher", "Intervention targets: node-wise target probabilities; PerturbPFN in-prior synthetic episodes"),
    ("Target", "F1 ↑"): ("target-f1", "f1-score", "higher", "Intervention targets: node-wise probabilities thresholded at 0.5; PerturbPFN in-prior synthetic episodes"),
    ("Strength / Response", "|ψ| ratio →1"): ("strength-ratio", "magnitude-ratio", "unknown", "Mean absolute predicted intervention strength over mean absolute true strength on true target nodes; 1 is the correct scale; PerturbPFN in-prior synthetic episodes"),
    ("Strength / Response", "∆ cosine ↑"): ("response-shift-cosine", "cosine-similarity", "higher", "Predicted against true mean response shift relative to control, both centred across genes; PerturbPFN in-prior synthetic episodes"),
    ("Strength / Response", "Obs. NLL ↓"): ("observation-nll", "negative-log-likelihood", "lower", "Mean negative log-likelihood of query responses under the predicted zero-inflated log-normal distribution; PerturbPFN in-prior synthetic episodes"),
}
for cell in T["table1"]:
    key, metric, direction, q = T1[(cell["block"], cell["row_label"])]
    v = cell["printed_value"]
    unit = "unit-unreported" if metric == "negative-log-likelihood" else "unitless"
    result(f"{P}-result-in-prior-{key}", EV_IP, f"PerturbPFN in-prior latent recovery: {cell['block']}, {cell['row_label']}",
           v, v, metric, direction, unit, q,
           f"Table 1, block '{cell['block']}', row \"{cell['row_label']}\"",
           unit_detail="Log base and per-gene or per-condition normalisation not stated" if metric == "negative-log-likelihood" else None,
           note=("Printed with the target '→1'; the best value is 1, so the direction is recorded as unknown." if metric == "magnitude-ratio" else
                 "Table 1 prints three label-value blocks per line; the locator's block names which pair."),
           areas=SYN_AREAS)
for p in T["prose"]:
    result(f"{P}-result-in-prior-target-topk-gate-f1", EV_IP, "PerturbPFN in-prior target F1 of the top-k gate",
           p["printed_value"], p["printed_value"], "f1-score", "higher", "unitless",
           "Intervention targets: straight-through top-k gate used in the decoder rollout (k = 3, Table 6); PerturbPFN in-prior synthetic episodes",
           "Section 4.1 'Results', sentence 'The straight-through top-k gate used by the decoder obtains a lower F1 of 0.6287'",
           hand=True, note="Prose value, not in Table 1.", areas=SYN_AREAS)

# ---------------------------------------------------------------- GeneRNIB 300BCG
BENCH_G = f"{P}-benchmark-genernib"
PROT_G = f"{P}-protocol-genernib-300bcg-50k"
DATA_G = f"{P}-data-genernib-300bcg"
G_LIMITS = [
    "The five baseline rows are copied from the official GeneRNIB score archive, not rerun by the PerturbPFN authors; the archive version and retrieval date are not stated (Appendix E.3).",
    "Replicate consistency, a metric the official pipeline also reports, is omitted from Table 3 (Section 4.3).",
    "PerturbPFN's graph is an intervention-propagation graph, not a curated GRN; the authors say it is related to but not identical to the regulatory references GeneRNIB scores against (Section 4.3).",
    "No uncertainty is printed.",
]
rec(
    BENCH_G, "benchmark", "GeneRNIB",
    "A living benchmark for gene regulatory network inference that scores a submitted ranked TF-gene network with an official pipeline of pathway, TF-binding, regression and virtual-cell metrics on held-out data.",
    {
        "entity_level": "suite",
        "task": "Gene regulatory network inference from expression data",
        "version": "As used in arXiv:2607.23447v1 (Nourisa et al. 2025, bioRxiv, reference [21]); release not stated",
        "scope_note": "Methods output at most 50,000 directed TF-gene links. Metrics: GS-F1, TFB-F1 against UniBind, ChIP-Atlas and ReMap, R-Precision and R-Recall, a virtual-cell score and replicate consistency, all computed by the official all_metrics pipeline.",
        "limitations": ["Registered from its description in arXiv:2607.23447v1; the GeneRNIB paper and repository were not retrieved for this batch."],
        "source_locator": "Section 4.3; Appendix E.1 and E.3",
        "missing_metadata": {"protocol_version": {"reason": "unreported", "note": "No GeneRNIB release, commit or archive date is printed."}},
        "review": review(hand=True),
    },
    areas=NET_AREAS,
)
rec(
    DATA_G, "dataset", "GeneRNIB 300BCG",
    "GeneRNIB's 300BCG dataset: expression profiles from 38 donors, whose baseline profiles are used to infer a network and whose held-out three-month profiles are used only for scoring.",
    {
        "species": "Human",
        "scope_note": "The inference matrix PerturbPFN receives holds 380 log-normalised expression profiles with cell-type labels; held-out three-month profiles and external regulatory references are used only for evaluation.",
        "split": "Official GeneRNIB split: infer from baseline profiles of 38 donors; evaluate on held-out three-month profiles",
        "version": "GeneRNIB 300BCG as used in arXiv:2607.23447v1; release not stated",
        "source_locator": "Section 4.3 'Protocol'; Appendix E.1",
        "missing_metadata": {
            "accession": {"reason": "unreported", "note": "No accession or download location is printed."},
            "assay": {"reason": "unreported", "note": "Whether the profiles are single-cell, pseudobulk or bulk is not stated."},
        },
        "review": review(hand=True),
    },
    areas=NET_AREAS,
)
rec(
    PROT_G, "protocol", "GeneRNIB 300BCG GRN inference, 50,000-link budget, official all_metrics scoring (PerturbPFN Table 3)",
    "Infer a weighted directed TF-gene network from 300BCG baseline profiles, submit at most 50,000 ranked links and score them with the official GeneRNIB pipeline on held-out profiles and external references.",
    {
        "protocol": "Infer from the benchmark inference matrix only; held-out three-month profiles, the regulator consensus and TF-binding references are not accessed. Submit at most 50,000 directed TF-gene links in the official format; score with the official all_metrics pipeline using ridge regression for the regression-based metrics.",
        "metric_definition": "GS-F1: pathways enriched among predicted TF targets against pathways active in held-out expression, averaged across gene-set collections. TFB-F1: normalised agreement and coverage against UniBind, ChIP-Atlas and ReMap. R-Precision and R-Recall: how well TFs selected from the network predict target-gene expression under conservative and broader regulator budgets. VC: whether a GRN-constrained virtual-cell model predicts held-out perturbed expression. Higher is better for all (Section 4.3, Appendix E.3).",
        "version": "arXiv:2607.23447v1",
        "publication_status": "preprint",
        "limitations": G_LIMITS,
        "source_locator": "Section 4.3; Appendix E; Table 3",
        "review": review(hand=True),
    },
    links=[("part_of", BENCH_G), ("uses_data", DATA_G)], areas=NET_AREAS,
)

method("pearson-grn", "Pearson correlation network", "Pearson corr.",
       "Ranks candidate regulator-target links by the Pearson correlation of the two genes' expression across profiles.",
       "Section 4.3 'Metrics and baselines'; Appendix E.3", ["conventional_pipeline"], areas=NET_AREAS)
method("ppcor", "PPCOR (partial Pearson correlation)", "PPCOR",
       "Ranks gene pairs by partial Pearson correlation, their correlation after removing the linear effect of the other genes, computed with the ppcor R package.",
       "Section 4.3 'Metrics and baselines'; reference [42]", ["conventional_pipeline"], areas=NET_AREAS)
method("grnboost2", "GRNBoost2", "GRNBoost2",
       "Tree-based network inference from the arboreto package that ranks candidate regulators of each target gene by their importance in a tree-ensemble regression of its expression.",
       "Section 4.3 'Metrics and baselines'; reference [43]", ["conventional_pipeline"], areas=NET_AREAS,
       extra={"provenance_note": "Registered from its use as a comparator in arXiv:2607.23447v1. Distinct from the store's GRNBoost method (discovery-model-grnboost), the earlier Spark implementation; the store's BEELINE GRNBOOST2 entries are unlinked configurations."})
method("portia", "PORTIA", "PORTIA",
       "Expression-based network inference that ranks regulator-target links from a robust estimate of the gene-expression precision matrix.",
       "Section 4.3 'Metrics and baselines'; reference [44]", ["conventional_pipeline"], areas=NET_AREAS)
method("scenic", "SCENIC", "SCENIC",
       "Infers co-expression modules between transcription factors and candidate targets and prunes them to regulons whose targets carry the factor's binding motif.",
       "Section 4.3 'Metrics and baselines'; reference [45]", ["conventional_pipeline"], areas=NET_AREAS)

G_COLS = [
    ("GS-F1", "gs-f1", "f1-score", "GeneRNIB gene-set F1: pathways enriched among predicted TF targets against pathways active in held-out expression, averaged across gene-set collections; 300BCG, at most 50,000 links"),
    ("TFB-F1", "tfb-f1", "f1-score", "GeneRNIB TF-binding F1: normalised agreement and coverage against UniBind, ChIP-Atlas and ReMap TF-binding references; 300BCG, at most 50,000 links"),
    ("R-Prec.", "r-precision", "genernib-regression-precision", "GeneRNIB regression precision with ridge regression, conservative regulator budget; 300BCG, at most 50,000 links"),
    ("R-Recall", "r-recall", "genernib-regression-recall", "GeneRNIB regression recall with ridge regression, broader regulator budget; 300BCG, at most 50,000 links"),
    ("VC", "vc", "genernib-virtual-cell-score", "GeneRNIB virtual-cell score: prediction of held-out perturbed expression by a model constrained by the inferred network; 300BCG, at most 50,000 links"),
]
G_SYSTEMS = {
    "Pearson corr.": methods["pearson-grn"], "PPCOR": methods["ppcor"], "GRNBoost2": methods["grnboost2"],
    "PORTIA": methods["portia"], "SCENIC": methods["scenic"], "PerturbPFN": CFG_GRN,
}
for row in T["table3"]:
    model = row["model"]
    key = {"Pearson corr.": "pearson"}.get(model, model.lower())
    ev = f"{P}-eval-genernib-300bcg-{key}"
    ours = model == "PerturbPFN"
    eattrs = {
        "origin": "author_reported" if ours else "paper_compilation",
        "protocol": PROT_G,
        "comparison": {
            "protocol_id": PROT_G,
            "dataset_version": "GeneRNIB 300BCG; release not stated",
            "split": "Official GeneRNIB split: infer from baseline profiles of 38 donors, score on held-out three-month profiles",
            "population": "38 donors",
            "inputs": "380 log-normalised inference profiles and the official GeneRNIB TF list" if ours else None,
            "adaptation": "None: the synthetic-pretrained checkpoint with no gradient updates, run on 190 TF-target panels" if ours else None,
            "metric_implementation": "Official GeneRNIB all_metrics pipeline, ridge regression for the regression-based metrics",
            "aggregation": None,
            "budget": "At most 50,000 directed TF-gene links",
        },
        "version": "arXiv:2607.23447v1",
        "source_locator": f"Table 3, row '{model}'",
        "limitations": (["Run and scored by the PerturbPFN authors with the official pipeline."] if ours else
                        ["Copied by the PerturbPFN authors from the official GeneRNIB score archive for 300BCG at the 50,000-link budget (Appendix E.3); who ran it, the archive version and the method version are not stated."]) + G_LIMITS[1:3],
        "missing_metadata": {"aggregation": {"reason": "unreported", "note": "How GeneRNIB aggregates each metric is not described in the paper."}},
        "review": review(),
    }
    if not ours:
        eattrs["missing_metadata"]["original_evaluation"] = {"reason": "unavailable", "note": "The GeneRNIB archive entry was not retrieved and has no record in the store."}
    rec(ev, "evaluation", f"{model} on GeneRNIB 300BCG (PerturbPFN Table 3)",
        ("Author-reported evaluation transcribed from the pinned preprint; run by the PerturbPFN authors and not reproduced by Rewire." if ours else
         "Baseline score copied by the PerturbPFN authors from the official GeneRNIB score archive and transcribed from the pinned preprint; not reproduced by Rewire."),
        eattrs, links=[("system", G_SYSTEMS[model]), ("assessment", PROT_G), ("data", DATA_G)], areas=NET_AREAS)
    for header, ckey, metric, q in G_COLS:
        unit = "unitless"
        result(f"{P}-result-genernib-300bcg-{key}-{ckey}", ev, f"{model}: {header} on GeneRNIB 300BCG",
               row[header], row[header], metric, "higher", unit, q, f"Table 3, row '{model}', column '{header}'",
               areas=NET_AREAS)

# ---------------------------------------------------------------- claims
claims = 0


def claim(key, subject, field, value, locator, name, rationale=None, limitations=None):
    global claims
    attrs = {"field": field, "value": value, "source_locator": locator, "review": review(hand=True)}
    if rationale:
        attrs["rationale"] = rationale
    if limitations:
        attrs["limitations"] = limitations
    rec(f"{P}-claim-{key}", "claim", name,
        "Descriptive fact read from the pinned preprint at the locator given; not a measurement on a benchmark panel.",
        attrs, links=[("subject", subject)], areas=CELL_AREAS + ["biological-networks"])
    claims += 1


claim("model-training-data", MODEL, "training_data",
      "PerturbPFN is trained entirely on prior-predictive synthetic episodes in which the graph, intervention targets, strengths and outcomes are known by construction; no real perturbation responses are used for training.",
      "Section 2.3, last sentence of the first paragraph; Section 2.5", "PerturbPFN: synthetic-only training")
claim("model-inputs-outputs", MODEL, "inputs_outputs",
      "Inputs are context pairs of a regime descriptor (drug embedding, dose and control indicator) and an observed response, plus a query regime descriptor; target propensities and target identities are not inputs. Outputs are point estimates of an episode-level graph, sparse query targets and strengths, and the location, variance and zero probability of a zero-inflated log-normal predictive distribution.",
      "Section 2.2; Section 2.4 'Intervention heads and SCM rollout'; Appendix A 'Highest-dose episodic protocol'", "PerturbPFN: inputs and outputs")
claim("model-size-compute", MODEL, "model_size_and_compute",
      "The selected step-3100 checkpoint has 14.98M parameters; the complete 3,500-step run took about 1.44 GPU-hours on one NVIDIA RTX 4090 with batch size 8.",
      "Appendix B 'Compute resources'; Tables 6 and 7", "PerturbPFN: size and training compute")
claim("model-gene-panel-limit", MODEL, "input_scale",
      "One forward pass supports at most 60 nodes (genes); training graphs have 40 to 60 genes, and the GeneRNIB run splits 1,600 genes into 190 panels of at most 60 genes.",
      "Table 6 'Maximum nodes'; Table 4 'Number of genes'; Appendix E.2", "PerturbPFN: gene panel size")
claim("model-stated-limitations", MODEL, "limitations",
      "The authors state that the latent variables' meaning is set by the synthetic prior and recovering them in-prior does not show they are identifiable biological mechanisms; graphs, targets and strengths are point estimates; the system is assumed sparse and acyclic; and gene panels are much smaller than a transcriptome.",
      "Section 5 'Limitations and Outlook'", "PerturbPFN: stated limitations")
claim("model-access", MODEL, "access",
      "The preprint gives no code repository, weights or checkpoint download, and states no code or model licence; the article itself is CC BY 4.0.",
      "Whole text of arXiv:2607.23447v1; licence from the arXiv abstract page", "PerturbPFN: access as stated in the preprint",
      rationale=NO_CODE)
claim("protocol-sciplex-not-unseen-drug", PROT_SP, "split_semantics",
      "\"This protocol tests dose extrapolation under unknown perturbation targets. The held-out drug is not completely unseen, since lower-dose responses are available, but the target and mechanism at the highest dose are not provided to the model.\"",
      "Appendix D.2, second paragraph", "Sci-Plex highest-dose holdout: not unseen-drug prediction",
      rationale="The abstract frames the problem as predicting responses to unseen chemical perturbations; the real-data test is dose extrapolation within a drug seen at lower doses.")
claim("protocol-sciplex-normalisation", PROT_SP, "metric_scope",
      "Table 2 scores are min-max normalised within each protocol across the compared methods and then averaged; \"These normalized scores depend on the included comparison set.\"",
      "Section 4.2 'Metrics', second paragraph; Appendix D.3 'Normalized multi-metric score'", "Sci-Plex Table 2: scores depend on the comparison set")
claim("protocol-sciplex-baseline-metrics", PROT_SP, "metric_implementation_note",
      "\"All baselines are evaluated on the same held-out protocols, and all reported metrics are recomputed using the same metric code as PerturbPFN whenever prediction arrays are available.\" The paper does not say whether any baseline lacked prediction arrays.",
      "Appendix D.4, first paragraph", "Sci-Plex Table 2: baseline metric recomputation")
claim("protocol-sciplex-runtime-accounting", PROT_SP, "runtime_accounting",
      "For PerturbPFN, the ICL-only time measures applying the pretrained checkpoint (1.11 s per protocol); the amortized time adds the one-time pretraining cost divided across the 12 protocols (432.8 s per protocol). All runtimes were measured on one compute worker with a single NVIDIA RTX 4090.",
      "Section 4.2 'Metrics', second paragraph; Table 2 caption", "Sci-Plex Table 2: runtime accounting")
claim("protocol-genernib-baselines-archive", PROT_G, "baseline_provenance",
      "\"Baseline results are taken from the official GeneRNIB score archive for the same 300BCG dataset and 50,000-link budget.\"",
      "Appendix E.3, last paragraph", "GeneRNIB 300BCG Table 3: baseline provenance")
claim("protocol-genernib-graph-export", PROT_G, "submission_semantics",
      "The GeneRNIB submission uses PerturbPFN's continuous, unthresholded edge probabilities rather than the projected DAG, so the exported network may contain cycles.",
      "Appendix E.2, last paragraph", "GeneRNIB 300BCG: PerturbPFN graph export")
claim("source-appendix-e-auxiliary", SRC, "unextracted_values",
      "Section 4.3 reports edge AUROC 0.9168 and edge average precision 0.7570 for PerturbPFN 'in the auxiliary graph-ranking evaluation (Appendix E)', but Appendix E of v1 describes only the GeneRNIB protocol and gives no auxiliary evaluation, reference network or edge set. The two values were not extracted.",
      "Section 4.3, last paragraph before Section 5; Appendix E", "PerturbPFN v1: auxiliary graph-ranking values without a described protocol",
      rationale="Without the reference edges or the protocol the values cannot be tied to a dataset or compared.")

records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
assert len(ids) == len(set(ids)), "duplicate ids"
with open(BATCH / "batch.jsonl", "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
from collections import Counter
print(Counter(r["kind"] for r in records), "results", results, "claims", claims)
