"""Sun et al. 2026, differential expression classification benchmark for single-cell perturbation models (bioRxiv 10.64898/2026.07.20.739620 v1):
Tables 1-4 from the pdftotext -layout text of the pinned PDF. The headline macro-F1 results are in figures only and are not extracted.

Usage: pdftotext -layout <paper.pdf> <paper.txt>; python3 -I extract_sun2026.py <paper.pdf> <paper.txt> <batch-folder>
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, judgement, write_links, finalise

pdf, txt, folder = sys.argv[1:4]
SHA = sha256(pdf)
assert SHA == "fa1c6a6345c45e14b9c373dfa8aff12633ae646feece1cfa3899c3ed61f6cfdf", SHA
URL = "https://www.biorxiv.org/content/10.64898/2026.07.20.739620v1.full.pdf"
B = "lit-cells-networks-20261011-sun2026de"
b = Batch(folder, B, areas=["single-cell"])
lines = open(txt, encoding="utf-8").read().replace("\f", "").split("\n")

SRC = b.source(B + "-source-sun2026", "Beyond Expression Prediction: Benchmarking Differential Expression Classification in Single-Cell Perturbation Models", {
    "url": "https://doi.org/10.64898/2026.07.20.739620", "artifact_url": URL, "version": "bioRxiv preprint version 1, posted 2026-07-24",
    "retrieved_at": "2026-10-11T21:35:10Z", "artifact_sha256": SHA, "doi": "10.64898/2026.07.20.739620", "publication_status": "preprint",
    "licence": "CC-BY-4.0", "media_type": "application/pdf",
    "hash_scope": "Exact bytes of one download; bioRxiv serves slightly different PDF bytes per download, so the gzip copy in artifacts/ is the reference.",
    "limitations": ["Preprint, not peer reviewed.", "Single train/test split (60/40 by perturbation); no spread printed in Tables 1-4.",
                    "The authors did not develop scVI, scGen or STATE. Co-author Ouyang Zhu developed Scouter and TranScouter (references 14 and 31), and co-author Yiqun T. Chen developed the GenePT embeddings used by the KNN, logistic-regression, VAE and scVI configurations (reference 30). The majority vote, KNN and logistic regression baselines and the scGen-based VAE adaptation are the authors' own."],
    "evidence_concerns": [{"source_id": B + "-source-sun2026", "message": "Methods describe results on both the full data and a PerturbQA-downsampled subset ('We annotate our results to distinguish between these two settings'), but the captions of Tables 1-4 do not say which setting they report. The printed true DE prevalence (1.75-4.41%) matches the full data's 95-98% non-DE share (Table 5), not the downsampled set; this is an inference, not a printed statement.",
                           "source_locator": "Section 3.2 'Full vs. Curated Dataset'; Tables 1-5", "artifact_sha256": SHA, "review_date": "2026-10-11"}]},
    description="bioRxiv PDF, retrieved and hashed for the 2026-10-11 cells-spatial literature pass.")
SIDS = [SRC]
REV = lambda loc: extraction_review(["pdf-text-parse"], "Parsed the pdftotext -layout text of the pinned PDF with extract_sun2026.py: method rows matched by printed name with exactly five percentages, row order and column headers asserted. " + loc, SHA, URL)

BENCH = b.entity("benchmark", b.rid("benchmark", "de-classification"), "Differential expression classification benchmark for perturbation models (Sun et al. 2026)",
    "Three-class (non-DE, up, down) differential expression prediction for unseen genetic perturbations within a cell line and for seen perturbations in a held-out cell line, on K562, RPE1, HepG2 and Jurkat essential-gene Perturb-seq screens.",
    SIDS, {"entity_level": "suite", "version": "bioRxiv v1 (2026-07-24)", "task": "Prediction of differential expression status after genetic perturbation",
           "scope_note": "DE labels from Wilcoxon rank-sum tests with Benjamini-Hochberg correction per perturbation (adjusted p < 0.01) on observed and predicted expression alike.",
           "source_locator": "Sections 1, 3.1-3.3; Tables 1-5"})

SYS = {  # printed label -> (config name, description, linked family, method type, independent)
    "Majority vote": ("Perturbation majority vote", "Predicts each gene's most frequent DE class across training perturbations, ignoring perturbation identity.", None, "specialist", False),
    "10-NN": ("Weighted 10-NN on GenePT embeddings", "Distance-weighted K-nearest-neighbour vote over training perturbations, K = 10, perturbations represented by GenePT embeddings.", None, "supervised_machine_learning", False),
    "1-NN": ("1-NN on GenePT embeddings", "Nearest training perturbation by cosine similarity of GenePT embeddings, K = 1.", None, "supervised_machine_learning", False),
    "Logistic regression": ("Per-gene L2 logistic regression on GenePT embeddings", "Per-gene L2-regularised multinomial logistic regression (strength 0.01) on GenePT perturbation embeddings, adapted from GenePert.", None, "supervised_machine_learning", False),
    "scVI sampling": ("scVI perturbation model, sampled output", "STATE's benchmarking implementation of scVI conditioned on GenePT perturbation embeddings; DE called on expression sampled from the ZINB output.", "catalog-model-scvi", "supervised_machine_learning", True),
    "scVI mean": ("scVI perturbation model, mean output", "STATE's benchmarking implementation of scVI conditioned on GenePT perturbation embeddings; DE called on the ZINB mean.", "catalog-model-scvi", "supervised_machine_learning", True),
    "VAE scGen": ("VAE adapted from scGen", "Variational autoencoder adapted from scGen by the authors; latent perturbation effects of similar training perturbations (GenePT cosine) are combined and decoded.", None, "supervised_machine_learning", False),
    # Co-author Ouyang Zhu developed Scouter and TranScouter (references 14 and 31), so both are author_reported (reviewer cn-1, S1).
    "Scouter": ("Scouter", "Scouter compressor-generator model with LLM gene embeddings, within-cell-line.", None, "supervised_machine_learning", False),
    "TranScouter": ("TranScouter", "TranScouter, the cross-cell-line extension of Scouter.", None, "supervised_machine_learning", False),
    "STATE": ("STATE (few-shot cross-cell-line)", "Arc Institute STATE transition model in gene-expression mode, without the pretrained State Embedding, trained on the benchmark splits following the official codebase, including the 60% training split of the held-out cell line (few-shot).", "discovery-model-state", "supervised_machine_learning", True),
}
cfgs = {}


def config(label):
    if label not in cfgs:
        name, desc, fam, mt, _ = SYS[label]
        cfgs[label] = b.entity("configuration", b.rid("config", label), f"{name} (Sun et al. 2026)", desc, SIDS, {
            "reported_name": label, "foundation_model_eligible": False, "source_locator": "Section 3.3",
            "missing_metadata": {"version": {"reason": "unreported"}}}, method_types=[mt], links=[{"relation": "configuration_of", "target_id": fam}] if fam else [])
    return cfgs[label]


CELLS = ["K562", "RPE1", "HepG2", "Jurkat"]
data_ids = {c: b.entity("dataset_subset", b.rid("data", c), f"{c} essential-gene Perturb-seq, 40% test perturbations (Sun et al. 2026)",
                        f"{c} essential-gene screen, normalised to 10,000 counts and log1p; perturbations split 60/40 into train and test.", SIDS,
                        {"split": "60% train / 40% test perturbations", "source_dataset_label": c, "source_locator": "Sections 3.1-3.2; Table 5",
                         "missing_metadata": {"version": {"reason": "unreported"}}}) for c in CELLS}
data_ids["Average"] = b.entity("dataset_subset", b.rid("data", "four-cell-lines"), "K562, RPE1, HepG2 and Jurkat test sets (Sun et al. 2026)",
                               "The four cell-line test sets; values are averages across them.", SIDS, {"split": "60% train / 40% test perturbations per cell line",
                               "source_locator": "Tables 1-4", "missing_metadata": {"version": {"reason": "unreported"}}})
PROTO = {
    "within": b.entity("protocol", b.rid("protocol", "within-cell-line"), "Sun et al. 2026 unseen-perturbation DE classification (within cell line)",
        "Predict non-DE, up or down status of every gene for held-out perturbations of the same cell line (60/40 perturbation split).", SIDS,
        {"protocol": "Within-cell-line: train on 60% of perturbations, predict DE class for the 40% held-out perturbations; DE called by Wilcoxon test with BH-adjusted p < 0.01 on predicted and observed expression.",
         "version": "bioRxiv v1", "metric": "accuracy", "metric_direction": "higher", "unit": "percent",
         "limitations": ["Single split; no spread printed.", "Macro-F1 and balanced accuracy, the headline metrics, are in figures only."], "source_locator": "Section 3.1; Tables 1-2"},
        links=[{"relation": "part_of", "target_id": BENCH}]),
    "cross": b.entity("protocol", b.rid("protocol", "cross-cell-line"), "Sun et al. 2026 cellular-context DE classification (cross cell line)",
        "Predict non-DE, up or down status of every gene for perturbations in a held-out cell line, training on the other cell lines over 6,641 shared genes.", SIDS,
        {"protocol": "Cross-cell-line: train on the other three cell lines and score the 40% test perturbations of the held-out cell line; STATE also sees the held-out line's 60% training split.",
         "version": "bioRxiv v1", "metric": "accuracy", "metric_direction": "higher", "unit": "percent",
         "limitations": ["Single split; no spread printed.", "STATE is few-shot (sees the held-out cell line's training split); the other methods are not.",
                         "Macro-F1 and balanced accuracy, the headline metrics, are in figures only."], "source_locator": "Section 3.1; Tables 3-4"},
        links=[{"relation": "part_of", "target_id": BENCH}]),
}

PCT = r"(\d+\.\d+)%"
NAMES = sorted(SYS, key=len, reverse=True) + ["True DE prevalence"]


def rows_of(title, end, expected_labels):
    s = next(i for i, l in enumerate(lines) if l.strip().startswith(title))
    e = next(i for i in range(s + 1, len(lines)) if lines[i].strip().startswith(end))
    out = []
    for l in lines[s:e]:
        m = re.match(r"^\s*(" + "|".join(re.escape(n) for n in NAMES) + r")\s+" + r"\s+".join([PCT] * 5) + r"\s*$", l)
        if m:
            out.append((m.group(1), [v + "%" for v in m.groups()[1:]]))
    assert [r[0] for r in out] == expected_labels, [r[0] for r in out]
    return out


evals, n = {}, 0
W_LABELS = ["Majority vote", "10-NN", "1-NN", "Logistic regression", "scVI sampling", "VAE scGen", "Scouter", "scVI mean"]
C_LABELS = ["Majority vote", "10-NN", "1-NN", "Logistic regression", "STATE", "scVI sampling", "VAE scGen", "TranScouter", "scVI mean"]
QCOLS = {"within": ["Q1 (0–0.016)", "Q2 (0.016–0.034)", "Q3 (0.034–0.060)", "Q4 (0.060–0.108)", "Q5 (>0.108)"],
         "cross": ["Q1 (0–0.017)", "Q2 (0.017–0.037)", "Q3 (0.037–0.065)", "Q4 (0.065–0.116)", "Q5 (>0.116)"]}
prevalence = []
for t, title, end, task, labels, kind in (
        (1, "Table 1: Proportion of perturbation-gene pairs", "2.2 Benchmarking Results", "within", W_LABELS + ["True DE prevalence"], "prop"),
        (2, "Table 2: Overall 3-class prediction accuracy", "Table 3:", "within", W_LABELS[:4] + ["scVI sampling", "scVI mean", "VAE scGen", "Scouter"], "acc"),
        (3, "Table 3: Proportion of perturbation-gene pairs", "produce better predictions", "cross", C_LABELS + ["True DE prevalence"], "prop"),
        (4, "Table 4: Overall 3-class prediction accuracy", "of 2–4%)", "cross", C_LABELS, "acc")):
    for label, vals in rows_of(title, end, labels):
        if label == "True DE prevalence":
            prevalence.append((t, task, vals))
            continue
        cols = CELLS + ["Average"] if kind == "prop" else QCOLS[task]
        for col, v in zip(cols, vals):
            dkey = col if kind == "prop" else "Average"
            c = config(label)
            key = (c, task, dkey)
            if key not in evals:
                evals[key] = b.evaluation(b.rid("eval", task, dkey, label), f"{label} on Sun et al. 2026 {task}-cell-line DE classification, {dkey if dkey != 'Average' else 'four cell lines'}",
                    SIDS, c, PROTO[task], data_ids[dkey], "independent_paper" if SYS[label][4] else "author_reported",
                    {"protocol_id": PROTO[task], "dataset_version": None, "split": "60/40 split by perturbation" + ("; held-out cell line" if task == "cross" else ""),
                     "population": None, "inputs": "Training perturbations with observed expression or DE labels, control-cell expression, and a perturbation representation (GenePT, LLM-derived or learned embedding) where the method uses one", "adaptation": "Trained per split",
                     "metric_implementation": "Wilcoxon rank-sum DE calls, BH-adjusted p < 0.01, on predicted and observed expression",
                     "aggregation": "Average across four cell lines" if dkey == "Average" else "Single cell line", "budget": None},
                    f"Table {t if kind == 'prop' else t}, row '{label}'")
            loc = f"Table {t}, row '{label}', column '{col}'"
            if kind == "prop":
                metric, q, direction = "proportion", "share of perturbation-gene pairs predicted as differentially expressed (compare with the printed true DE prevalence)", "unknown"
            else:
                metric, q, direction = "accuracy", f"3-class (non-DE, up, down) accuracy within true |log2 FC| quantile {col}; quantile bins per cell line, averaged over four cell lines", "higher"
            b.result(b.rid("result", f"t{t}", task, col.split(" ")[0], label), f"{label} {task}-cell-line {col} (Table {t})", SRC, SIDS, evals[key], v, metric, direction, "percent",
                     loc, REV(loc), qualifier=q, numeric=v.rstrip("%"))
            n += 1
assert n == 8 * 5 + 8 * 5 + 9 * 5 + 9 * 5, n
for t, task, vals in prevalence:
    for col, v in zip(CELLS + ["Average"], vals):
        loc = f"Table {t}, row 'True DE prevalence', column '{col}'"
        b.claim(b.rid("claim", f"t{t}", "true-de-prevalence", col), f"True DE prevalence, {col}, {task}-cell-line test set (Table {t})",
                "Share of perturbation-gene pairs that are DE in the observed test data, printed for reference beside the predicted DE proportions.",
                data_ids[col], SIDS, {"field": "true_de_prevalence", "value": v, "source_locator": loc}, source_id=SRC)

UC, UCN = "use-case-genetic-perturbation-response", "Assess models for genetic perturbation experiments"
ev = lambda task: [e for (c, tk, d), e in evals.items() if tk == task]
# Judgement limitations and the cross-cell-line rationale are reviewer cn-1's text (S5), verbatim.
LIM_WITHIN = ["Preprint; one 60/40 perturbation split per cell line; no spread printed.",
 "The printed tables are DE-call proportions and accuracy by effect-size quantile; the macro-F1 and balanced accuracy comparisons are in figures only.",
 "Majority-vote accuracy is near 100% in low-effect quantiles because almost all pairs are non-DE; read the Q5 column and the DE proportions together.",
 "Which data setting (full or PerturbQA-downsampled) the tables report is not printed (source evidence concern).",
 "The authors built the majority-vote, KNN, logistic-regression and scGen-based VAE comparators, and co-author Ouyang Zhu developed Scouter (reference 14); those rows are author-reported. scVI is run through STATE's benchmarking implementation with GenePT perturbation embeddings.",
 "Ground-truth DE labels are Wilcoxon calls (BH-adjusted p < 0.01) on observed expression in four essential-gene Perturb-seq screens, not orthogonally validated effects."]
LIM_CROSS = ["Preprint; one 60/40 perturbation split per cell line; no spread printed.",
 "The printed tables are DE-call proportions and accuracy by effect-size quantile; the macro-F1 and balanced accuracy comparisons are in figures only.",
 "Majority-vote accuracy is near 100% in low-effect quantiles because almost all pairs are non-DE; read the Q5 column and the DE proportions together.",
 "Which data setting (full or PerturbQA-downsampled) the tables report is not printed (source evidence concern).",
 "The authors built the majority-vote, KNN, logistic-regression and scGen-based VAE comparators, and co-author Ouyang Zhu developed TranScouter (reference 31); those rows are author-reported.",
 "Models are trained on the 6,641 genes shared by the four cell lines; STATE runs in gene-expression mode without the pretrained State Embedding.",
 "Ground-truth DE labels are Wilcoxon calls (BH-adjusted p < 0.01) on observed expression in four essential-gene Perturb-seq screens, not orthogonally validated effects."]
links = [
    judgement(b, UC, PROTO["within"], "within-cell-line", SIDS, "proxy",
              "Share of gene-perturbation pairs called DE and 3-class DE accuracy by effect-size quantile for held-out perturbations within K562, RPE1, HepG2 and Jurkat, comparing majority vote, KNN and logistic regression baselines with scVI, scGen-based VAE and Scouter",
              "Directly compares simple controls with deep perturbation models on held-out genetic perturbations, scored on the DE calls that guide follow-up experiments. Proxy: DE classification of predicted expression, not experimental hit rates.",
              ["Inspect every linked evaluation's source locator before citing a result.", "Compare predicted DE proportions with the printed true DE prevalence, not with each other alone."],
              LIM_WITHIN, [{"source_id": SRC, "locator": "Tables 1-2; Sections 2.1 and 3.1-3.3"}],
              "accuracy", "sun2026-de-classification", "DE classification benchmark (Sun et al. 2026)", "Unseen perturbations within a cell line", 1, ev("within"), UCN),
    judgement(b, UC, PROTO["cross"], "cross-cell-line", SIDS, "proxy",
              "Share of gene-perturbation pairs called DE and 3-class DE accuracy by effect-size quantile for perturbations in a held-out cell line, including STATE (few-shot), TranScouter, scVI, scGen-based VAE and simple baselines",
              "Scores DE calls for perturbations in a cell line held out from training, which bears on the use case's gap on performance in a new cell system. Proxy: retrospective DE classification of predicted expression on four essential-gene screens, not a prospective pilot or experimental hit rates.",
              ["Inspect every linked evaluation's source locator before citing a result.", "STATE sees part of the held-out cell line; do not read its rows as zero-shot."],
              LIM_CROSS, [{"source_id": SRC, "locator": "Tables 3-4; Sections 2.2 and 3.1-3.3"}],
              "accuracy", "sun2026-de-classification", "DE classification benchmark (Sun et al. 2026)", "Held-out cell line", 2, ev("cross"), UCN),
]
write_links(folder, links)
finalise(b, "reviewer-cn-1", "2026-10-12T08:40:00Z",
         "value, locator, metric, unit, direction and linked configuration, protocol and dataset checked by the reviewer's own parse of all Tables 1-4 cells and a hand check of 48 values against the rendered pages.",
         "Archived gzip copy unpacked and its SHA-256 matched; a fresh bioRxiv download was rate-limited (HTTP 429).")
print(json.dumps(b.write()))
