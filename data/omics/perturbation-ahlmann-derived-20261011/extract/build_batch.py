"""Write batch.jsonl and claims.csv for the Ahlmann-Eltze et al. 2025 Source Data batch.

The 59 values come from derived-values.jsonl, the output of
scripts/omics/derive/ahlmann_eltze_2025.py on the four pinned workbooks. Everything else
(sources, models, configurations, datasets, protocols, evaluations, claims and relevance
judgements) is hand-written below from the article text, with locators.

Usage, from the repository root: python3 -I data/omics/perturbation-ahlmann-derived-20261011/extract/build_batch.py
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

BATCH = Path("data/omics/perturbation-ahlmann-derived-20261011")
SCRIPT = "scripts/omics/derive/ahlmann_eltze_2025.py"
P = "perturbation-ahlmann-20261011"
DOI = "10.1038/s41592-025-02772-6"
TODAY = "2026-10-11"
FACETS = {"areas": ["cells-tissues", "single-cell"], "contexts": ["research"]}
ESM = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41592-025-02772-6/MediaObjects/41592_2025_2772_MOESM{}_ESM.xlsx"

ARTICLE = f"{P}-source-article"
WORKBOOKS = {
    "MOESM3": (f"{P}-source-data-fig1", "Source Data Fig. 1", "c9bd4d688b8ca8a3d3846593da3bab80cc2e65dbdbdc251a96b2bdcd05b75081", 1659842),
    "MOESM4": (f"{P}-source-data-fig2", "Source Data Fig. 2", "2ccfa7239c195f329e1632b51510adebfd493e0a5a7427a0f012e078e0e59c35", 1837063),
    "MOESM6": (f"{P}-source-data-ed-fig2", "Source Data Extended Data Fig. 2", "1f05ffc452445de659d9b0bb4b05c673892ce7a4f2657ea3098a7904f95f24b3", 529066),
    "MOESM10": (f"{P}-source-data-ed-fig8", "Source Data Extended Data Fig. 8", "040dae4985b4461817b96eb807390c8fe3f2c115523f4dfcb7692485aa0734e3", 586193),
}
ARTICLE_SHA = "dc5ccf62cb51d301f327a3c3e629d60be719bb2aaf02b57fb4999be43a4d95c7"
SRC = lambda w: WORKBOOKS[w][0]


def record(id, kind, name, description, attributes, links=(), source_ids=(ARTICLE,), facets=FACETS):
    return {"id": id, "kind": kind, "name": name, "description": description, "status": "needs_review",
            "facets": dict(facets), "source_ids": list(source_ids), "links": [dict(relation=r, target_id=t) for r, t in links],
            "attributes": attributes}


records: list[dict] = []
claims_csv: list[dict] = []

# ---- Sources ----

records.append(record(ARTICLE, "source",
    "Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines",
    "Ahlmann-Eltze, Huber and Anders, Nature Methods 2025 (Brief Communication). Primary source for the methods, legends and stated aggregation.",
    {"url": f"https://doi.org/{DOI}", "artifact_url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12328236/fullTextXML",
     "version": "Nature Methods 22(8):1657, published online 2025-08-04; PMC12328236 full-text XML",
     "retrieved_at": "2026-10-11T00:48:13Z", "artifact_sha256": ARTICLE_SHA, "doi": DOI, "publication_status": "peer_reviewed",
     "licence": "CC-BY-4.0", "media_type": "application/xml", "venue": "Nature Methods", "year": 2025,
     "source_locator": "Licence from the article XML <license> element (Creative Commons Attribution 4.0 International)"},
    source_ids=(), facets=FACETS))

CONCERN_DATE = "2026-10-11T00:00:00Z"
concerns = {
    "MOESM4": [
        ("Fig. 2 legend versus Source Data Fig. 2, sheet \"Panel A\"",
         "The Fig. 2 legend gives \"134, 210 and 24 unseen single perturbations across two test-training splits\". In Panel A these are the split 1 counts only (Replogle K562 134, Replogle RPE1 210, Adamson 24 rows per method); split 2 has 128, 203 and 24, so the two-split totals are 262, 413 and 48. The Fig. 2a means recorded here use all Panel A rows; whether the plotted red lines use both splits is not stated beyond the sheet itself."),
        ("Methods 'Single perturbation benchmark setup' paragraph 4 versus Source Data Fig. 2, sheets \"Panel A\" and \"Panel C\"",
         "Methods restricts the single-perturbation analysis to perturbations predicted by all models: 73 for Adamson, 398 for Replogle K562 and 629 for Replogle RPE1. No sheet of Source Data Fig. 2 has these counts (Panel A: 48, 262 and 413 per method over two splits; Panel C: 20, 214 and 224 test or val rows per method)."),
        ("Source Data Fig. 2, sheet \"Panel C\" versus the Fig. 2 legend and Methods",
         "The test and val rows in Panel C (20, 214 and 224 per method for Adamson, Replogle K562 and Replogle RPE1) match neither the Fig. 2 legend counts nor the Methods counts. Fig. 2c was not extracted."),
        ("Main text paragraph 16 versus Source Data Fig. 2, sheet \"Panel C\"",
         "The main text says CPA was not included in the single-perturbation benchmark, but method \"cpa\" has rows in Panel C. Fig. 2c was not extracted."),
    ],
    "MOESM10": [
        ("Methods 'Single perturbation benchmark setup' paragraph 4 versus Source Data Extended Data Fig. 8, sheet \"Panel A\"",
         "Panel A repeats Source Data Fig. 2 Panel A row for row (48, 262 and 413 rows per method over two splits). Methods restricts the analysis to 73, 398 and 629 perturbations predicted by all models; the sheet does not have these counts."),
    ],
}
for workbook, (sid, label, sha, size) in WORKBOOKS.items():
    attrs = {"url": ESM.format(workbook[5:]), "version": f"{label} (41592_2025_2772_{workbook}_ESM.xlsx) as published with the article",
             "retrieved_at": "2026-10-11T00:48:13Z", "artifact_sha256": sha, "doi": DOI, "publication_status": "peer_reviewed",
             "licence": "CC-BY-4.0", "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
             "venue": "Nature Methods", "year": 2025,
             "source_locator": f"Article 'Data availability' and the '{label}' link under the figure; the article licence covers its supplementary material",
             "scope_note": f"{size} bytes. Each row of sheet \"Panel A\" is one held-out perturbation in one test-training split (column seed), labelled test or val in column train."}
    if workbook in concerns:
        attrs["evidence_concerns"] = [{"source_id": sid, "message": m, "source_locator": loc,
                                       "artifact_sha256": sha, "reviewed_at": CONCERN_DATE, "review_method": "ai-assisted-source-review"}
                                      for loc, m in concerns[workbook]]
    records.append(record(sid, "source", f"{label}, Ahlmann-Eltze et al. 2025",
        f"Authors' Source Data workbook for {label[12:]}, published by the journal with the article.", attrs, source_ids=(), facets=FACETS))

# ---- Models and methods ----

records.append(record(f"{P}-model-scbert", "model", "scBERT",
    "Single-cell foundation model pretrained on unlabelled scRNA-seq with a BERT-style masked objective.",
    {"entity_level": "family", "reported_name": "scBERT", "source_locator": "Main text paragraph 2; Methods 'Software versions and parameters'",
     "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the commit is on the configuration"}}},
    facets={**FACETS, "method_types": ["foundation_model"]}))
records.append(record(f"{P}-model-cpa", "model", "CPA (compositional perturbation autoencoder)",
    "Deep generative model of single-cell perturbation responses.",
    {"entity_level": "family", "reported_name": "CPA", "source_locator": "Main text paragraph 2; Methods 'Software versions and parameters'",
     "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the version is on the configuration"}}},
    facets={**FACETS, "method_types": ["supervised_machine_learning"]}))
METHOD_FACETS = {**FACETS, "method_types": ["conventional_pipeline"]}
records.append(record(f"{P}-method-no-change", "method", "No change baseline",
    "Predicts, for every perturbation, the expression observed in the unperturbed control condition.",
    {"entity_level": "method", "reported_name": "no change", "source_locator": "Main text paragraph 5; Methods 'Double perturbation benchmark setup' paragraph 2",
     "missing_metadata": {"version": {"reason": "inapplicable", "note": "A computed baseline with no software version"}}}, facets=METHOD_FACETS))
records.append(record(f"{P}-method-additive", "method", "Additive baseline for double perturbations",
    "Predicts a double perturbation of genes A and B as the sum of the two single-perturbation log fold changes: yA + yB minus the control expression.",
    {"entity_level": "method", "reported_name": "additive", "source_locator": "Main text paragraph 5; Methods 'Double perturbation benchmark setup' paragraph 2, equation (2)",
     "missing_metadata": {"version": {"reason": "inapplicable", "note": "A computed baseline with no software version"}}}, facets=METHOD_FACETS))
records.append(record(f"{P}-method-linear-model", "method", "Linear perturbation model (Ahlmann-Eltze et al. 2025)",
    "Bilinear model Y = G W P^T + b, with read-out gene embedding G and perturbation embedding P from a PCA of the training data or from an external source, W fitted by ridge-regularised least squares and b the training row means.",
    {"entity_level": "method", "reported_name": "linear model", "source_locator": "Main text paragraph 14, equation (1); Methods 'Single perturbation benchmark setup' paragraphs 2 and 3",
     "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; settings are on the configuration"}}}, facets=METHOD_FACETS))

# ---- Configurations ----

CODE = "Prediction scripts for every model: github.com/const-ae/linear_perturbation_prediction-Paper (benchmark/src), archived on Zenodo; branch link, not pinned to a commit in the article."
SOFTWARE = "Methods 'Software versions and parameters'"
configs = {
    # key: (Source Data label, name, target, method type, foundation, version or None, parameters, extra)
    "scgpt": ("scgpt", "scGPT", "catalog-model-scgpt", "foundation_model", True, "scGPT 0.2.1",
              "Fine-tuned with the parameters and code of the scGPT perturbation-prediction tutorial.",
              {"model_identity_note": "The pretrained checkpoint is not named in the article."}),
    "scfoundation": ("scfoundation", "scFoundation", "catalog-model-scfoundation", "foundation_model", True, "scFoundation, built on a fork of GEARS 0.0.2",
                     "Fine-tuned through its GEARS-based API for five epochs (fine-tuning time limited to 3 days). Double-perturbation benchmark only.",
                     {"model_identity_note": "The pretrained checkpoint is not named in the article."}),
    "gears": ("gears", "GEARS", "catalog-model-gears", "supervised_machine_learning", False, "GEARS 0.1.2",
              "Trained through the GEARS API with default parameters.", {}),
    "cpa": ("cpa", "CPA", f"{P}-model-cpa", "supervised_machine_learning", False, "CPA 0.8.8",
            "Code from the CPA tutorial on predicting combinatorial CRISPR perturbations on the Norman dataset. The CPA authors submitted a fix that performed worse; results use the original code.",
            {}),
    "geneformer": ("geneformer", "Geneformer", "catalog-model-geneformer", "foundation_model", True, "Geneformer 0.1.0",
                   "Fine-tuned to predict the perturbation labels of the training data; in silico perturbation gives the perturbed embedding, and a ridge regression decoder fitted on training data maps embeddings to expression (mean prediction per perturbation).",
                   {}),
    "uce": ("uce", "UCE", "cell-type-20261009-model-uce", "foundation_model", True, "UCE commit 8227a65c, four-layer model",
            "Zero-shot, no fine-tuning. The post-perturbation embedding is computed from the unperturbed expression matrix with the perturbed genes' rows overwritten by ground-truth values; a ridge regression decoder maps embeddings to expression.",
            {"model_identity_note": "The authors report the four-layer model and say the 33-layer model performed the same."}),
    "scbert": ("scbert", "scBERT", f"{P}-model-scbert", "foundation_model", True, "scBERT commit 262fd4b9, model weights provided by the scBERT authors",
               "Fine-tuned to predict the perturbation labels of the training data; perturbed embedding computed as for UCE; ridge regression decoder.", {}),
    "no-change": ("no_change", "No change", f"{P}-method-no-change", "conventional_pipeline", False, None,
                  "Predicts the control-condition expression for every perturbation; uses no perturbation data.", {}),
    "additive": ("additive_model", "Additive", f"{P}-method-additive", "conventional_pipeline", False, None,
                 "Sum of the two single-perturbation log fold changes; uses no double-perturbation data.", {}),
    "mean": ("mean", "Mean", "perturbation-response-20261009-method-train-mean", "conventional_pipeline", False, None,
             "Mean of the expression values over the training perturbations, predicted for every unseen perturbation.", {}),
    "linear-model": ("lpm_selftrained", "Linear model (G and P from training data)", f"{P}-method-linear-model", "conventional_pipeline", False, None,
                     "K = 10 principal components of the training data for G; P is G restricted to genes perturbed in training; ridge penalty lambda = 0.1; b the training row means.",
                     {}),
}
CONFIG = lambda key: f"{P}-config-{key}"
LOCATOR_FOR = {"no-change": "Methods 'Double perturbation benchmark setup' paragraph 2", "additive": "Methods 'Double perturbation benchmark setup' paragraph 2",
               "mean": "Main text paragraph 15; Methods 'Single perturbation benchmark setup' paragraph 2",
               "linear-model": "Methods 'Single perturbation benchmark setup' paragraphs 2 and 4"}
for key, (label, name, target, mtype, foundation, version, parameters, extra) in configs.items():
    attrs = {"reported_name": f"{name} (Source Data method \"{label}\")",
             "source_locator": f"{LOCATOR_FOR.get(key, SOFTWARE)}; Source Data column method \"{label}\"",
             "foundation_model_eligible": foundation, "parameters": parameters, "access_reuse": CODE, **extra}
    if version:
        attrs["version"] = version
    else:
        attrs["missing_metadata"] = {"version": {"reason": "inapplicable", "note": "A computed baseline with no software version"}}
    records.append(record(CONFIG(key), "configuration", f"{name} (Ahlmann-Eltze et al. 2025)",
        f"{name} as run by Ahlmann-Eltze et al. 2025 for perturbation-effect prediction.", attrs,
        links=[("configuration_of", target)], facets={**FACETS, "method_types": [mtype]}))
BY_LABEL = {v[0]: k for k, v in configs.items()}

# ---- Datasets and protocols ----

GENES = "the 1,000 most highly expressed genes in the control condition"
datasets = {
    "norman": ("Norman et al. 2019 Perturb-seq, K562 CRISPRa single and double perturbations (scFoundation reprocessing, Ahlmann-Eltze et al. 2025)",
               "100 single-gene and 124 two-gene CRISPRa perturbations plus control in K562 cells, as reprocessed and distributed by scFoundation.",
               {"version": "scFoundation reprocessing, figshare file 44477939", "access": "https://figshare.com/ndownloader/files/44477939 (article 'Data availability')",
                "population": "224 perturbations (100 single, 124 double) plus control; 19,264 genes in main text paragraph 3 but 19,624 genes, 81,143 cells and 225 conditions in the Extended Data Fig. 10 legend",
                "source_locator": "Main text paragraph 3; Methods 'Data'; 'Data availability'; Extended Data Fig. 10 legend",
                "scope_note": "The gene count differs between main text paragraph 3 (19,264) and the Extended Data Fig. 10 legend (19,624). This is the scFoundation reprocessing, not the GEARS processing used for the Csendes et al. 2025 Norman record."}),
    "adamson": ("Adamson et al. 2016 Perturb-seq, K562 CRISPRi single perturbations (GEARS distribution, Ahlmann-Eltze et al. 2025)",
                "Single-gene CRISPRi Perturb-seq in K562 cells, as distributed by GEARS.",
                {"version": "GEARS distribution, Harvard Dataverse datafile 6154417", "access": "https://dataverse.harvard.edu/api/access/datafile/6154417 (article 'Data availability')",
                 "source_locator": "Main text paragraph 13; Methods 'Data'; 'Data availability'"}),
    "replogle-k562": ("Replogle et al. 2022 Perturb-seq essential-gene screen, K562 CRISPRi (GEARS distribution, Ahlmann-Eltze et al. 2025)",
                      "Single-gene CRISPRi Perturb-seq of essential genes in K562 cells, as distributed by GEARS.",
                      {"version": "GEARS distribution, Harvard Dataverse datafile 7458695", "access": "https://dataverse.harvard.edu/api/access/datafile/7458695 (article 'Data availability')",
                       "source_locator": "Main text paragraph 13; Methods 'Data'; 'Data availability'"}),
    "replogle-rpe1": ("Replogle et al. 2022 Perturb-seq essential-gene screen, RPE1 CRISPRi (GEARS distribution, Ahlmann-Eltze et al. 2025)",
                      "Single-gene CRISPRi Perturb-seq of essential genes in RPE1 cells, as distributed by GEARS.",
                      {"version": "GEARS distribution, Harvard Dataverse datafile 7458694", "access": "https://dataverse.harvard.edu/api/access/datafile/7458694 (article 'Data availability')",
                       "source_locator": "Main text paragraph 13; Methods 'Data'; 'Data availability'"}),
}
for key, (name, description, attrs) in datasets.items():
    records.append(record(f"{P}-data-{key}", "dataset", name, description, attrs))

SINGLE_SPLIT = "GEARS 'simulation' test-training split, run twice (two splits)"
DOUBLE_SPLIT = "All 100 single perturbations and a random half (62) of the 124 doubles for training; the other 62 doubles held out (31 labelled test and 31 val in the Source Data); repeated with five random splits"
COMMON_LIMITS = [
    "The paper prints no per-model value; the means are computed by Rewire from the authors' Source Data rows and have not been checked against a printed number.",
    "Four datasets, all from cancer cell lines, chosen because the GEARS, scGPT and scFoundation publications used them; the original quality control was not improved, so perturbations that did not affect their own target gene are included (main text paragraph 22).",
    "The authors ran every model themselves with default parameters as far as possible and asked the model developers to review their code (Methods 'Software versions and parameters').",
]
protocols = {
    "norman-double": ("norman", "Norman double perturbations: expression prediction for held-out double perturbations (Ahlmann-Eltze et al. 2025 Fig. 1a and Extended Data Fig. 2a)",
                      "Models are trained on all single and half of the double perturbations and predict expression for the 62 held-out doubles in each of five random splits. Error is the L2 distance, and agreement the Pearson delta, between predicted and observed expression over " + GENES + ", per perturbation.",
                      DOUBLE_SPLIT, 310, "Main text paragraphs 4 and 6; Fig. 1 legend; Extended Data Fig. 2 legend; Methods 'Double perturbation benchmark setup' and 'Evaluation metrics'"),
    "adamson-single": ("adamson", "Adamson: expression prediction for unseen single perturbations (Ahlmann-Eltze et al. 2025 Fig. 2a and Extended Data Fig. 8a)",
                       None, SINGLE_SPLIT, 48, None),
    "replogle-k562-single": ("replogle-k562", "Replogle K562: expression prediction for unseen single perturbations (Ahlmann-Eltze et al. 2025 Fig. 2a and Extended Data Fig. 8a)",
                             None, SINGLE_SPLIT, 262, None),
    "replogle-rpe1-single": ("replogle-rpe1", "Replogle RPE1: expression prediction for unseen single perturbations (Ahlmann-Eltze et al. 2025 Fig. 2a and Extended Data Fig. 8a)",
                             None, SINGLE_SPLIT, 413, None),
}
SINGLE_PROTOCOL = ("Models are trained on the perturbations in the training part of a GEARS 'simulation' split and predict the mean expression profile for unseen single perturbations. Error is the L2 distance, and agreement the Pearson delta, between the mean predicted and observed expression over " + GENES + ", per perturbation.")
SINGLE_LOCATOR = "Main text paragraphs 13 and 16; Fig. 2 legend; Extended Data Fig. 8 legend; Methods 'Single perturbation benchmark setup' and 'Evaluation metrics'"
for key, (data, name, text, split, rows, locator) in protocols.items():
    limits = list(COMMON_LIMITS)
    if key == "norman-double":
        limits.append("UCE's post-perturbation embedding uses ground-truth expression of the perturbed genes, which the authors note could leak test data (Methods 'Software versions and parameters').")
    else:
        limits += ["The Fig. 2 legend's perturbation counts are the split 1 counts only, and the Methods counts of perturbations predicted by all models (73, 398 and 629) match no Source Data sheet; see the evidence concerns on the Source Data Fig. 2 and Extended Data Fig. 8 source records.",
                   "scFoundation and CPA are not in this benchmark (main text paragraph 16)."]
    records.append(record(f"{P}-protocol-{key}", "protocol", name, text or SINGLE_PROTOCOL,
        {"protocol": text or SINGLE_PROTOCOL, "scope_note": f"Split: {split}. {rows} held-out perturbation-split rows per model in the Source Data.", "denominator": rows,
         "metric_definition": "L2 distance: square root of the summed squared differences over " + GENES + ". Pearson delta: correlation of predicted and observed expression after subtracting the control expression (Methods 'Evaluation metrics').",
         "aggregation": "Mean per model over held-out perturbations, pooling the rows labelled test and val and all splits (\"The horizontal red lines show the mean per model\").",
         "source_locator": locator or SINGLE_LOCATOR, "limitations": limits,
         "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "The figures show per-perturbation points and the mean; no spread of the mean is stated"}}},
        links=[("uses_data", f"{P}-data-{data}")]))

# ---- Evaluations and results ----

DATASET_KEY = {"norman_from_scfoundation": "norman", "adamson": "adamson", "replogle_k562_essential": "replogle-k562", "replogle_rpe1_essential": "replogle-rpe1"}
PROTOCOL_KEY = {"norman": "norman-double", "adamson": "adamson-single", "replogle-k562": "replogle-k562-single", "replogle-rpe1": "replogle-rpe1-single"}
DATASET_NAME = {"norman": "Norman doubles", "adamson": "Adamson", "replogle-k562": "Replogle K562", "replogle-rpe1": "Replogle RPE1"}
BASELINES = {"no-change", "additive", "mean", "linear-model"}
FIGURE = {"fig1a": ("Fig. 1a", "Fig. 1 legend"), "ed2a": ("Extended Data Fig. 2a", "Extended Data Fig. 2 legend"),
          "fig2a": ("Fig. 2a", "Fig. 2 legend"), "ed8a": ("Extended Data Fig. 8a", "Extended Data Fig. 8 legend")}
QUALIFIER = "1,000 most highly expressed control genes; mean over held-out perturbations and splits"

script_sha = hashlib.sha256(Path(SCRIPT).read_bytes()).hexdigest()
derived = [json.loads(line) for line in (BATCH / "derived-values.jsonl").read_text().splitlines()]
evaluations = {}
gaps = []
for row in derived:
    data = DATASET_KEY[row["dataset"]]
    key = BY_LABEL[row["method"]]
    protocol = f"{P}-protocol-{PROTOCOL_KEY[data]}"
    eval_id = f"{P}-eval-{data}-{key}"
    config_name = configs[key][1]
    if eval_id not in evaluations:
        double = data == "norman"
        evaluations[eval_id] = record(eval_id, "evaluation", f"{config_name} on {DATASET_NAME[data]} (Ahlmann-Eltze et al. 2025)",
            "Benchmark run by the paper's authors. The per-model mean is computed by Rewire from the authors' Source Data rows; not reproduced.",
            {"origin": "author_reported" if key in BASELINES else "independent_paper", "protocol": protocol,
             "version": f"Primary source as retrieved {TODAY}",
             "comparison": {
                 "protocol_id": protocol,
                 "dataset_version": datasets[data][2]["version"],
                 "split": DOUBLE_SPLIT if double else SINGLE_SPLIT,
                 "population": ("62 held-out double perturbations in each of five splits (310 rows per model)" if double else
                                f"Unseen single perturbations in Source Data Fig. 2 Panel A over two splits ({row['row_count']} rows per model)"),
                 "inputs": "Expression of training perturbations and control; identity of the perturbed genes",
                 "adaptation": "Fine-tuned, fitted or applied per split by the paper's authors with default parameters where possible",
                 "metric_implementation": "L2 distance and Pearson delta over " + GENES + " (Methods 'Evaluation metrics')",
                 "aggregation": "Arithmetic mean per model over held-out perturbations, pooling test and val rows and all splits",
                 "budget": None},
             "source_locator": f"{'Fig. 1a and Extended Data Fig. 2a' if double else 'Fig. 2a and Extended Data Fig. 8a'}; Source Data method \"{row['method']}\"",
             "limitations": (["Baseline built or adopted by the paper's authors, who conclude that simple baselines are not outperformed."] if key in BASELINES else
                             ["Third-party model fine-tuned and run by the paper's authors, not by its developers."])},
            links=[("system", CONFIG(key)), ("assessment", protocol), ("data", f"{P}-data-{data}")],
            source_ids=(ARTICLE, SRC("MOESM3") if double else SRC("MOESM4")))
    figure, legend = FIGURE[row["target"]]
    l2 = row["column"] == "l2"
    if row["value"] is None:
        gaps.append(f"{figure}, {DATASET_NAME[data]}, {config_name}: no value; all {row['row_count']} rows have no {row['column']}, and the {legend} says the correlation for the no change predictions could not be calculated because they were all zero.")
        continue
    metric = "l2-distance" if l2 else "pearson-delta"
    wb, sheet, column = row["workbook"], row["sheet"], row["column"]
    sid, label, sha, _ = WORKBOOKS[wb]
    filt = f"dataset_name == \"{row['dataset']}\" and method == \"{row['method']}\"; train in {{test, val}}; seed in {{{', '.join(row['splits'])}}}; column {column}"
    locator = f"{label} ({wb}), sheet \"{sheet}\", rows with dataset_name \"{row['dataset']}\" and method \"{row['method']}\", column \"{column}\"; plotted as the red line in {figure}"
    result_id = f"{P}-result-{row['target']}-{data}-{key}"
    attrs = {
        "printed_value": row["value"], "numeric_value": row["value"], "metric": metric, "metric_qualifier": QUALIFIER,
        "metric_direction": "lower" if l2 else "higher", "unit": "unit-unreported" if l2 else "unitless",
        "source_locator": locator,
        "coverage": {"scored": row["rows_with_value"], "eligible": row["row_count"], "unit": "perturbation-split rows"},
        "derivation": {
            "method": "computed-from-source-data",
            "inputs": [{"source_id": sid, "artifact_sha256": sha, "locator": f"{label} ({wb}), sheet \"{sheet}\"", "row_filter": filt, "row_count": row["row_count"]}],
            "aggregation": "The horizontal red lines show the mean per model",
            "aggregation_source_id": ARTICLE, "aggregation_locator": f"{legend}, panel {figure[-1]}",
            "script": SCRIPT, "script_sha256": script_sha,
            "precision": "Exact arithmetic mean of the stored cell values, rounded half to even to 3 decimal places",
            "note": ("The sheet labels each held-out perturbation test or val; both are held out from training, and the Fig. 1 legend's 62 doubles per split equals the two together, so both are pooled." if data == "norman" else
                     "The sheet labels each held-out perturbation test or val; both are pooled, as for Fig. 1. The Fig. 2 legend counts are the split 1 counts only; this mean uses both splits as the sheet does (see the source's evidence concerns)."),
        },
        "review": {"method": ["deterministic-table-parse"],
                   "note": f"Computed by {SCRIPT} (sha256 {script_sha}) from the re-downloaded workbook, whose SHA-256 the script checks along with every row count. Not printed in the source. Pending independent review; the extractor did not review its own work."},
        "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "No spread of the mean is stated; Rewire did not compute one"}},
    }
    if l2:
        attrs["unit_detail"] = "distance between log-transformed expression profiles; the expression unit is not otherwise stated"
    records.append(record(result_id, "result",
        f"{config_name} on {DATASET_NAME[data]}: mean {'L2 distance' if l2 else 'Pearson delta'} ({figure}, computed from Source Data)",
        "Computed by Rewire from the authors' Source Data rows; the paper plots this mean but does not print it. Not independently reproduced.",
        attrs, links=[("evaluation", eval_id)], source_ids=(ARTICLE, sid)))
    claims_csv.append({"record_id": result_id, "source_id": sid, "locator": locator, "printed_value": row["value"],
                       "review_scope": "computed from source data; pending independent review"})
records.extend(evaluations.values())

# ---- Descriptive claims ----


def claim(slug, subject, field, value, locator, source_ids=(ARTICLE,)):
    cid = f"{P}-claim-{slug}"
    records.append(record(cid, "claim", f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.",
        {"field": field, "value": value, "source_locator": locator,
         "review": {"method": ["transcription"], "note": "Hand transcription from the article XML. Pending independent review."}},
        links=[("subject", subject)], source_ids=source_ids, facets={}))
    claims_csv.append({"record_id": cid, "source_id": ARTICLE, "locator": locator, "printed_value": value, "review_scope": "descriptive claim; pending independent review"})


claim("double-additive-not-beaten", f"{P}-protocol-norman-double", "reported_finding",
      "All models had a prediction error substantially higher than the additive baseline (Fig. 1a,b). Other summary statistics, including the Pearson delta and L2 distances over other gene subsets, gave the same overall result (Extended Data Fig. 2).",
      "Main text paragraph 6")
claim("double-interactions-no-change", f"{P}-protocol-norman-double", "genetic_interaction_finding",
      "None of the models was better than the 'no change' baseline at predicting genetic interactions (Fig. 1c), and the same ranking was observed with other metrics (Extended Data Fig. 4). Fig. 1c and Extended Data Fig. 4 were not extracted.",
      "Main text paragraphs 8 and 9")
for key in ["adamson-single", "replogle-k562-single", "replogle-rpe1-single"]:
    claim(f"{key}-baselines-not-beaten", f"{P}-protocol-{key}", "reported_finding",
          "None of the deep learning models was able to consistently outperform the mean prediction or the linear model (Fig. 2a and Extended Data Fig. 8).",
          "Main text paragraph 16")
claim("linear-model-pretrained-embeddings", f"{P}-method-linear-model", "reported_finding",
      "The linear model with gene embeddings from scFoundation or scGPT, or the perturbation embedding from GEARS, performed as well as or better than scGPT and GEARS with their own decoders, and the scFoundation and scGPT gene embeddings outperformed the mean baseline but not consistently the linear model fitted on the training data. A linear model with the perturbation embedding pretrained on Replogle data (K562 for Adamson and RPE1, RPE1 for K562) consistently outperformed all other models (Fig. 2c). Fig. 2c was not extracted.",
      "Main text paragraphs 17 and 18")
claim("scfoundation-single-excluded", CONFIG("scfoundation"), "scope_note",
      "scFoundation was not included in the single-perturbation benchmark because it required each dataset to exactly match the genes from its own pretraining data, and most of the required genes were missing for the Adamson and Replogle data.",
      "Main text paragraph 16")
claim("cpa-single-excluded", CONFIG("cpa"), "scope_note",
      "CPA was not included in the single-perturbation benchmark, as it is not designed to predict the effects of unseen perturbations. (Source Data Fig. 2 Panel C nevertheless has cpa rows; see the evidence concern on that source.)",
      "Main text paragraph 16")
claim("uce-test-leakage", CONFIG("uce"), "design_limitation",
      "UCE has no in silico perturbation, so the authors took the unperturbed expression matrix and overwrote the rows of the perturbed genes with ground-truth values, accepting that this test data leakage could in theory give UCE an advantage. scBERT's perturbed embedding was computed the same way.",
      "Methods 'Software versions and parameters', UCE and scBERT paragraphs")

# ---- Relevance judgements ----

UC = "use-case-genetic-perturbation-response"
strata = [("norman-double", "Norman doubles (K562 CRISPRa)", 1), ("adamson-single", "Adamson (K562 CRISPRi)", 2),
          ("replogle-k562-single", "Replogle K562 (CRISPRi)", 3), ("replogle-rpe1-single", "Replogle RPE1 (CRISPRi)", 4)]
judgements = []
for key, stratum, order in strata:
    protocol = f"{P}-protocol-{key}"
    double = key == "norman-double"
    workbooks = ("MOESM3", "MOESM6") if double else ("MOESM4", "MOESM10")
    models = ("scGPT, scFoundation, GEARS, CPA and three foundation models with a linear decoder (Geneformer, UCE, scBERT) against the no change and additive baselines"
              if double else "scGPT, GEARS and three foundation models with a linear decoder (Geneformer, UCE, scBERT) against the mean baseline and a linear model")
    rationale = (f"{models} are scored on the same held-out perturbations, which is the methods-and-controls comparison the use case asks for, from authors who did not develop the deep models. "
                 "It is proxy evidence: expression-prediction error does not establish mechanism or experimental prioritisation (use-case exclusion), and the per-model means are computed by Rewire from the authors' Source Data rather than printed.")
    limitations = [
        "Values are computed by Rewire from the authors' per-perturbation Source Data (attributes.derivation on each result); the paper prints no per-model number.",
        "The authors ran all models themselves; the deep models were not run by their developers, although the developers were asked to review the code.",
        "No spread of the mean is stated, so small differences between models are not testable from these values.",
    ]
    if double:
        limitations += ["Training includes every single perturbation and half of the doubles, the setting the use case's GEARS combination guidance requires.",
                        "UCE and scBERT post-perturbation embeddings use ground-truth expression of the perturbed genes (possible test leakage, Methods).",
                        "The Pearson delta for the no change baseline is undefined and not recorded.",
                        "The Norman gene count differs between the main text (19,264) and the Extended Data Fig. 10 legend (19,624)."]
    else:
        limitations += ["The Fig. 2 legend's counts are split 1 only, and the Methods counts (73, 398, 629) match no sheet; the Source Data sources carry evidence concerns, so these results do not support automatic comparison.",
                        "scFoundation and CPA are not evaluated here; Fig. 2c (embedding variants, bootstrapped ratios) was not extracted because its aggregation is ambiguous."]
    jid = f"use-case-mapping-{P}-{key}"
    attrs = {
        "field": f"links:assessed_by:{protocol}", "value": protocol, "relevance": "proxy",
        "endpoint": f"Mean L2 distance and mean Pearson delta between predicted and observed expression over the 1,000 most highly expressed genes, for {models}, {stratum}",
        "rationale": rationale,
        "constraints": ["Inspect every linked evaluation's source locator, derivation and preserved limitations before citing a result.",
                        "Do not combine these results with another protocol's results; splits, gene subsets and metric implementations differ between sources.",
                        "Cite these values as computed by Rewire from the authors' Source Data, not as printed values."],
        "limitations": limitations,
        "citation_locators": [{"source_id": SRC(w), "locator": f"{WORKBOOKS[w][1]}, sheet \"Panel A\""} for w in workbooks]
                             + [{"source_id": ARTICLE, "locator": ("Fig. 1 and Extended Data Fig. 2 legends; main text paragraphs 4 to 6; Methods" if double else "Fig. 2 and Extended Data Fig. 8 legends; main text paragraphs 13 to 16; Methods")}],
        "source_locator": f"{ARTICLE}: {'Fig. 1 and Extended Data Fig. 2' if double else 'Fig. 2 and Extended Data Fig. 8'} legends and Methods; " + "; ".join(f"{SRC(w)}: sheet \"Panel A\"" for w in workbooks),
        "revision": 1,
        "reason": f"Recorded from the Ahlmann-Eltze et al. 2025 Source Data pass {TODAY} (data/omics/perturbation-ahlmann-derived-20261011); pending independent review.",
        "comparison_group": "ahlmann2025-perturbation-baselines",
        "comparison_title": "Deep learning and foundation models against simple baselines (Ahlmann-Eltze et al. 2025)",
        "headline_metric": "l2-distance", "stratum_label": stratum, "stratum_order": order,
    }
    sources = [ARTICLE, *(SRC(w) for w in workbooks)]
    records.append(record(jid, "claim",
        f"Relevance of {protocols[key][1]} to \"Assess models for genetic perturbation experiments\"", rationale, attrs,
        links=[("subject", UC)], source_ids=sources, facets={}))
    judgements.append({"judgement_id": jid, "protocol_id": protocol, "relevance": "proxy", "comparison_group": attrs["comparison_group"],
                       "stratum_label": stratum, "stratum_order": order,
                       "evaluation_ids": sorted(e for e in evaluations if evaluations[e]["links"][1]["target_id"] == protocol)})

records.sort(key=lambda r: r["id"])
(BATCH / "batch.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))
with open(BATCH / "claims.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["record_id", "source_id", "locator", "printed_value", "review_scope"])
    writer.writeheader()
    writer.writerows(sorted(claims_csv, key=lambda r: r["record_id"]))
(BATCH / "extract" / "judgements.json").write_text(json.dumps(judgements, indent=2) + "\n")
(BATCH / "extract" / "gaps.json").write_text(json.dumps(gaps, indent=2) + "\n")
counts = {}
for r in records:
    counts[r["kind"]] = counts.get(r["kind"], 0) + 1
print(json.dumps(counts, sort_keys=True))
