"""Chen et al. 2026, harmonised benchmark of single-cell and spatial foundation models (arXiv 2607.17227v2): Tables 2-5 and
Supplementary Table S2 from the pdftotext -layout text of the pinned PDF.

Usage: pdftotext -layout <2607.17227v2.pdf> <out.txt>; python3 -I extract_chen2026.py <2607.17227v2.pdf> <out.txt> <batch-folder>
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, judgement, write_links, finalise

pdf, txt, folder = sys.argv[1:4]
SHA = sha256(pdf)
assert SHA == "8137338c6146f570a6546f30707d4244baca9dab848b32c51539665a5ba539da", SHA
URL = "https://arxiv.org/pdf/2607.17227v2"
B = "lit-cells-networks-20261011-chen2026"
b = Batch(folder, B, areas=["single-cell", "spatial-omics"])
lines = open(txt, encoding="utf-8").read().replace("\f", "").split("\n")

SRC = b.source(B + "-source-chen2026", "Harmonised benchmarking of foundation models for single-cell and spatial transcriptomics reveals context-dependent generalisation", {
    "url": "https://arxiv.org/abs/2607.17227v2", "artifact_url": URL, "version": "arXiv 2607.17227v2, updated 2026-09-17 (v1 posted 2026-07-19)",
    "retrieved_at": "2026-10-11T21:29:34Z", "artifact_sha256": SHA, "doi": "10.48550/arXiv.2607.17227", "publication_status": "preprint",
    "licence": "CC-BY-SA-4.0", "media_type": "application/pdf",
    "limitations": ["Preprint, not peer reviewed.", "Single run per cell with a fixed seed (42); no spread is printed.",
                    "Spatial dataset codes BC, MH and ME are not defined in the tables; the Figure 2 legend defines them as BC/HBCA1 (human breast cancer), MH/MHPC (mouse hippocampus) and ME/MOSTA E9.5 (mouse embryo)."],
    # Reviewer cn-2, correction C3 (verbatim).
    "evidence_concerns": [{"source_id": B + "-source-chen2026", "message": "Table 4 precision and recall equal accuracy in all eight Nicheformer and CellPLM rows, as micro (global) averaging would give, but recall differs from accuracy in every scGPT-spatial, GenePT-w, scELMo and Novae row. The Methods call precision and recall 'global' without defining the averaging, so they may be averaged differently between models and should not be compared across models.",
                           "source_locator": "Table 4, columns 'Accuracy', 'Precision' and 'Recall'; Methods 'Cell type annotation' (page 25)", "artifact_sha256": "8137338c6146f570a6546f30707d4244baca9dab848b32c51539665a5ba539da", "review_date": "2026-10-12"}]})
SIDS = [SRC]
REV = lambda loc: extraction_review(["pdf-text-parse"], "Parsed the pdftotext -layout text of the pinned PDF with extract_chen2026.py: data rows matched by dataset code and number count, model labels assigned to fixed blocks in printed order with labels and block sizes asserted. " + loc, SHA, URL)

BENCH = b.entity("benchmark", b.rid("benchmark", "harmonised-sc-spatial-fm"), "Harmonised single-cell and spatial foundation model benchmark (Chen et al. 2026)",
    "Harmonised evaluation of six single-cell and spatial foundation models (Nicheformer, CellPLM, scGPT-spatial, GenePT-w, scELMo, Novae) on zero-shot and continually pretrained clustering, supervised cell type annotation, marker-gene concordance and perturbation prediction.",
    SIDS, {"entity_level": "suite", "version": "arXiv v2 (2026-09-17)", "task": "Clustering, cell type annotation and perturbation prediction from foundation model embeddings",
           "scope_note": "No non-foundation-model baseline (for example PCA or scVI) is reported in the result tables.", "source_locator": "Abstract; Methods 'Downstream evaluation tasks'; Tables 1-5"})

MODELS = {  # label -> (name, description, existing family id or None)
    "Nicheformer": ("Nicheformer", "Transformer foundation model pretrained on dissociated and spatial transcriptomics (Schaub et al., Nature Methods 2025).", None),
    "CellPLM": ("CellPLM", "Cell-level transformer foundation model pretrained on scRNA-seq and spatial transcriptomics (Wen et al., ICLR 2024).", None),
    "scGPT-spatial": ("scGPT-spatial", "scGPT continually pretrained on spatial transcriptomics (SpatialHuman30M) (Wang et al., bioRxiv 2025).", None),
    "GenePT-w": ("GenePT", "Cell embeddings built from GPT text embeddings of gene descriptions, weighted by expression (GenePT-w variant).", None),
    "scELMo": ("scELMo", "Cell embeddings built from large language model embeddings of gene descriptions, weighted by expression.", None),
    "Novae": ("Novae", "Graph attention foundation model for spatial transcriptomics domains (Blampey et al., Nature Methods 2025).", None),
}
fam = {}
for label, (name, desc, existing) in MODELS.items():
    fam[label] = existing or b.entity("model", b.rid("model", name), name, desc, SIDS, {
        "reported_name": label, "entity_level": "family", "source_locator": "Table 1",
        "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}, method_types=["foundation_model"])

MODES = {"zero-shot": "frozen pretrained embeddings, Leiden clustering with resolution tuned to the number of reference labels, seed 42",
         "continual": "two epochs of self-supervised continual pretraining on the target dataset, then the zero-shot clustering workflow",
         "fine-tuned": "supervised fine-tuning or adaptation on reference cell type labels (stratified 8:2 train/test split), each model's recommended workflow",
         "gears-decoder": "model embeddings (or gene embeddings for GenePT-w and scELMo) used with a shared GEARS perturbation decoder in the scGPT-style perturbation workflow",
         "kmeans": "frozen GenePT-w embeddings clustered with k-means"}
cfgs = {}


def config(label, mode):
    k = (label, mode)
    if k not in cfgs:
        cfgs[k] = b.entity("configuration", b.rid("config", label, mode), f"{label} ({mode}, Chen et al. 2026)", f"{label} as run by Chen et al. 2026: {MODES[mode]}.", SIDS, {
            "reported_name": label, "foundation_model_eligible": True, "training_setting": MODES[mode],
            "access_reuse": "Public pretrained checkpoints as released by each model's authors",
            "source_locator": "Methods: model-specific sections under 'Zero-shot cell type clustering', 'Continually-pretrained cell type clustering', 'Cell type annotation' and 'Perturbation prediction'",
            "missing_metadata": {"version": {"reason": "unreported", "note": "Checkpoint names are printed for some models only (CellPLM 20231027_85M)"}}},
            method_types=["foundation_model"], links=[{"relation": "configuration_of", "target_id": fam[label]}])
    return cfgs[k]


DATA = {"ATAA": "ATAA ascending aortic aneurysm scRNA-seq (11 major cell types)", "HS": "HS human splenic dendritic cells scRNA-seq (7 subtypes)",
        "BMMC": "BMMC NeurIPS 2021 CITE-seq bone marrow (45 cell types)", "SEAAD": "SEAAD middle temporal gyrus MERFISH (24 cell types)",
        "BC": "BC spatial dataset (Visium breast cancer HBCA1 per Methods)", "MH": "MH spatial dataset (Slide-seqV2 mouse hippocampus MHPC per Methods)",
        "ME": "ME spatial dataset (Stereo-seq MOSTA E9.5 mouse embryo per Methods)",
        "Norman": "Norman K562 Perturb-seq (131 two-gene and 105 single-gene perturbations)", "Adamson": "Adamson K562 Perturb-seq (87 single-gene perturbations)",
        "Replogle": "Replogle K562 genome-wide CRISPRi Perturb-seq"}
data_ids = {k: b.entity("dataset_subset", b.rid("data", k), f"{k} (Chen et al. 2026)", v + ", as preprocessed by Chen et al. 2026.", SIDS, {
    "source_dataset_label": k, "source_locator": "Methods 'Datasets'", "missing_metadata": {"version": {"reason": "unreported"}}}) for k, v in DATA.items()}

TASKS = {
    "zs-cluster": ("zero-shot cell type and spatial domain clustering", "Leiden clustering of frozen embeddings with resolution tuned so the number of clusters matches the number of labels; ARI, NMI and silhouette (cosine distance) against reference labels", "Table 2; Methods 'Zero-shot cell type clustering'"),
    "cp-cluster": ("continually pretrained clustering", "Two epochs of self-supervised continual pretraining per dataset, then the zero-shot clustering protocol", "Table 3; Methods 'Continually-pretrained cell type clustering'"),
    "annotation": ("supervised cell type annotation", "Supervised fine-tuning on reference labels with a stratified 8:2 train/test split; metrics on the shared held-out test set", "Table 4; Methods 'Cell type annotation'"),
    "perturbation": ("genetic perturbation prediction", "scGPT-style perturbation workflow with a shared GEARS decoder; all models scored on the same intersected gene set per dataset", "Table 5; Results 'Perturbation prediction'; Methods"),
    "kmeans": ("zero-shot clustering with k-means", "k-means clustering of frozen GenePT-w embeddings", "Supplementary Table S2; Methods"),
}
protos = {}


def proto(task, ds):
    k = (task, ds)
    if k not in protos:
        name, desc, loc = TASKS[task]
        metric = {"zs-cluster": "adjusted-rand-index", "cp-cluster": "adjusted-rand-index", "kmeans": "adjusted-rand-index", "annotation": "macro-f1", "perturbation": "pearson-delta"}[task]
        protos[k] = b.entity("protocol", b.rid("protocol", task, ds), f"Chen et al. 2026 {name}, {ds}", f"{desc}. Dataset {ds}.", SIDS, {
            "protocol": desc, "version": "arXiv 2607.17227v2", "metric": metric, "metric_direction": "higher", "unit": "unitless",
            "random_seeds": "Seed 42 for NumPy, Scanpy and PyTorch (Methods)",
            "limitations": ["Single run; no spread printed.", "No non-foundation-model baseline is reported for this task in the tables."],
            "source_locator": loc}, links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": data_ids[ds]}])
    return protos[k]


DS = r"(ATAA|HS|BMMC|SEAAD|BC|MH|ME|Norman|Adamson|Replogle)"
NUM = r"-?\d+\.\d+"


def table_rows(start, end, ncols):
    s = next(i for i, l in enumerate(lines) if l.startswith(start))
    e = next(i for i in range(s + 1, len(lines)) if lines[i].startswith(end))
    rows, labels = [], []
    for l in lines[s:e]:
        m = re.match(r"^\s*(.*?)\s*\b" + DS + r"\s+((?:" + NUM + r"\s+){" + str(ncols - 1) + r"}" + NUM + r")\s*$", l)
        if m:
            rows.append([m.group(1).strip(), m.group(2), m.group(3).split()])
            continue
        t = l.strip()
        if t in MODELS:
            labels.append((len(rows), t))
    return rows, labels


def assign(rows, labels, blocks):
    """blocks: [(model, [datasets])]; model labels sit on a row or on their own line inside the block."""
    out, k = [], 0
    for model, dss in blocks:
        block = rows[k:k + len(dss)]
        assert [r[1] for r in block] == dss, (model, [r[1] for r in block], dss)
        found = {r[0] for r in block if r[0]} | {t for i, t in labels if k < i < k + len(dss) or (i == k and not block[0][0] and t == model)}
        assert found == {model}, (model, found)
        out += [(model, r[1], r[2]) for r in block]
        k += len(dss)
    assert k == len(rows), (k, len(rows))
    return out


SC, SP = ["ATAA", "HS", "BMMC"], ["BC", "MH", "ME"]
CLU = {"ARI": ("adjusted-rand-index", None), "NMI": ("normalized-mutual-information", None),
       "Silhouette": ("silhouette-score", "against reference labels on the model embedding; range -1 to 1; distance stated as cosine in some model sections of the Methods")}
ANN = {"Accuracy": ("accuracy", "held-out test set"), "Precision": ("precision", "held-out test set; described as global in the Methods, averaging not further defined"),
       "Recall": ("recall", "held-out test set; described as global in the Methods, averaging not further defined"), "Macro-F1": ("macro-f1", "held-out test set"),
       "PR-AUC": ("auprc", "held-out test set; macro-averaged over classes"), "ROC-AUC": ("auroc", "held-out test set; macro-averaged over classes")}
PERT = {"MSE": ("mean-squared-error", "all genes, predicted versus observed post-perturbation expression", "lower"),
        "MSE DE": ("mean-squared-error", "top 20 differentially expressed genes per perturbation condition, predicted versus observed post-perturbation expression", "lower"),
        "Pearson": ("pearson-correlation", "all genes, predicted versus observed post-perturbation expression", "higher"),
        "Pearson DE": ("pearson-correlation", "top 20 differentially expressed genes per perturbation condition, predicted versus observed post-perturbation expression", "higher"),
        "Pearson Delta": ("pearson-delta", "all genes in the intersected gene set", "higher"),
        "Pearson Delta DE": ("pearson-delta", "top 20 differentially expressed genes per perturbation condition", "higher")}
evals = {}


def emit(table, task, mode, model, ds, cols, vals, mmap):
    c, p = config(model, mode), proto(task, ds)
    key = (c, p)
    if key not in evals:
        evals[key] = b.evaluation(b.rid("eval", task, ds, model), f"{model} on Chen et al. 2026 {TASKS[task][0]}, {ds}", SIDS, c, p, data_ids[ds], "independent_paper",
            {"protocol_id": p, "dataset_version": None, "split": "Held-out test set (stratified 8:2)" if task == "annotation" else ("Perturbation split of the scGPT-style workflow" if task == "perturbation" else "All cells (unsupervised clustering)"),
             "population": None, "inputs": "Single-cell or spatial expression matrix, aligned to each model's gene vocabulary", "adaptation": MODES[mode],
             "metric_implementation": None, "aggregation": None, "budget": None}, f"{table}, model '{model}', dataset '{ds}'")
    for col, v in zip(cols, vals):
        metric, q, *d = mmap[col]
        direction = d[0] if d else "higher"
        loc = f"{table}, model '{model}', dataset '{ds}', column '{col}'"
        b.result(b.rid("result", task, ds, model, col), f"{model} {ds} {col} ({table})", SRC, SIDS, evals[key], v, metric, direction, "unitless", loc, REV(loc), qualifier=q)
    return len(vals)


n = 0
rows, labels = table_rows("Table 2. Zero-shot", "Table 3. Continually", 3)
for model, ds, vals in assign(rows, labels, [(m, SC) for m in ["Nicheformer", "CellPLM", "scGPT-spatial", "GenePT-w", "scELMo"]] + [(m, SP) for m in ["Nicheformer", "CellPLM", "scGPT-spatial", "GenePT-w", "scELMo", "Novae"]]):
    n += emit("Table 2", "zs-cluster", "zero-shot", model, ds, ["ARI", "NMI", "Silhouette"], vals, CLU)
assert n == 99, n
rows, labels = table_rows("Table 3. Continually", "Table 4. Cell type", 3)
for model, ds, vals in assign(rows, labels, [(m, SC) for m in ["Nicheformer", "CellPLM", "scGPT-spatial"]] + [(m, SP) for m in ["Nicheformer", "CellPLM", "scGPT-spatial", "Novae"]]):
    n += emit("Table 3", "cp-cluster", "continual", model, ds, ["ARI", "NMI", "Silhouette"], vals, CLU)
assert n == 99 + 63, n
rows, labels = table_rows("Table 4. Cell type", "Table 5. Perturbation", 6)
ANNDS = ["ATAA", "HS", "BMMC", "SEAAD"]
for model, ds, vals in assign(rows, labels, [(m, ANNDS) for m in ["Nicheformer", "CellPLM", "scGPT-spatial", "GenePT-w", "scELMo"]] + [("Novae", ["SEAAD"])]):
    n += emit("Table 4", "annotation", "fine-tuned", model, ds, ["Accuracy", "Precision", "Recall", "Macro-F1", "PR-AUC", "ROC-AUC"], vals, ANN)
assert n == 162 + 126, n
rows, labels = table_rows("Table 5. Perturbation", "Supplementary Table S1", 6)
PDS = ["Norman", "Adamson", "Replogle"]
for model, ds, vals in assign(rows, labels, [(m, PDS) for m in ["CellPLM", "scGPT-spatial", "GenePT-w", "scELMo"]]):
    n += emit("Table 5", "perturbation", "gears-decoder", model, ds, ["MSE", "MSE DE", "Pearson", "Pearson DE", "Pearson Delta", "Pearson Delta DE"], vals, PERT)
assert n == 288 + 72, n
rows, labels = table_rows("Supplementary Table S2", "                                                        48", 3)
for r in rows:  # model label sits on its own line between the two modality blocks
    r[0] = ""
for model, ds, vals in assign(rows, labels, [("GenePT-w", SC + SP)]):
    n += emit("Supplementary Table S2", "kmeans", "kmeans", model, ds, ["ARI", "NMI", "Silhouette"], vals, CLU)
assert n == 360 + 18, n

# Relevance judgements.
UCP, UCPN = "use-case-genetic-perturbation-response", "Assess models for genetic perturbation experiments"
UCA, UCAN = "use-case-cell-type-annotation-transfer", "Transfer cell-type annotations to a new dataset"
ev_for = lambda task, ds: [e for (c, p), e in evals.items() if p == protos[(task, ds)]]
LIM = ["Preprint; single run with seed 42 and no spread, so small differences are not testable.",
       "The authors did not develop any of the six models (independent comparison), but no conventional baseline is in the tables."]
links = []
for i, ds in enumerate(PDS):
    links.append(judgement(b, UCP, protos[("perturbation", ds)], "perturbation-" + ds.lower(), SIDS, "proxy",
        f"MSE, Pearson and Pearson delta (all genes and DE genes) of predicted post-perturbation expression on {ds} K562 Perturb-seq for CellPLM, scGPT-spatial, GenePT-w and scELMo with a shared GEARS decoder",
        "Compares foundation-model representations as inputs to the same GEARS perturbation decoder on held-out perturbations. Proxy and narrow: no no-change, mean or linear control is reported, which the use case asks for, and the endpoint is expression agreement only.",
        ["Inspect every linked evaluation's source locator before citing a result.", "Do not compare with other sources' Norman, Adamson or Replogle results; gene sets and splits differ.",
         "Use Pearson Delta and the DE-gene metrics; global Pearson is about 0.98-0.99 for every model (Results)."],
        LIM + ["DE metrics use the top 20 differentially expressed genes per perturbation condition (Methods); the DE gene sets are not printed."]
        + (["Scores average single-gene and two-gene test perturbations under the GEARS simulation split; the number of two-gene combinations in training is not printed."] if ds == "Norman" else []),
        [{"source_id": SRC, "locator": "Table 5; Results 'Perturbation prediction separates expression reconstruction from functional response modelling'"}],
        "pearson-delta", "chen2026-harmonised-fm", "Harmonised single-cell and spatial foundation model benchmark (Chen et al. 2026)", f"{ds} K562 Perturb-seq", i + 1, ev_for("perturbation", ds), UCPN))
for i, ds in enumerate(ANNDS):
    links.append(judgement(b, UCA, protos[("annotation", ds)], "annotation-" + ds.lower(), SIDS, "proxy",
        f"Accuracy, precision, recall, macro-F1, PR-AUC and ROC-AUC of supervised cell type annotation on a stratified held-out split of {ds}",
        "Scores foundation models fine-tuned on reference labels and tested on held-out cells of the same dataset. Proxy: the use case transfers labels to a new dataset, while this split keeps train and test cells from the same study and batch structure.",
        ["Inspect every linked evaluation's source locator before citing a result.", "Prefer macro-F1 and PR-AUC; accuracy and ROC-AUC saturate on ATAA (Results)."],
        LIM + ["Within-dataset split by tissue section (whole sections held out; train and test from the same study), not cross-dataset transfer." if ds == "SEAAD" else "Within-dataset stratified split, not cross-dataset transfer.",
               "PR-AUC and ROC-AUC are macro-averaged (Methods); precision and recall are called global without a definition and appear to be averaged differently between models (source evidence concern), so do not compare them across models.",
               "Reference labels are the datasets' curated marker-gene and expert annotations, not independent ground truth.",
               "No rejection of unseen cell types or unassigned output is evaluated."],
        [{"source_id": SRC, "locator": "Table 4; Results on supervised annotation; Methods 'Cell type annotation'"}],
        "macro-f1", "chen2026-harmonised-fm", "Harmonised single-cell and spatial foundation model benchmark (Chen et al. 2026)", f"{ds} held-out annotation", i + 1, ev_for("annotation", ds), UCAN))
write_links(folder, links)
finalise(b, "reviewer-cn-2", "2026-10-12T08:44:00Z",
         "value, locator, metric, unit, direction and linked configuration and protocol checked by the reviewer's own parse of all Tables 2-5 and S2 cells and a hand check of 45 values against the rendered pages.",
         "Artifact re-downloaded from arXiv and SHA-256 matched; the archived gzip copy decompresses to the same bytes.")
print(json.dumps(b.write()))
