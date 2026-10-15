"""Build batch.jsonl and claims.csv for Kendiukhov 2026 (BMC Genomics 27:634).

Usage: python3 -I extract_kendiukhov2026.py <article.pdf> <batch-folder>

The article prints its perturbation-target (Objective B) results only in running text; Tables 1
and 2 hold no performance values. Each value below was transcribed by hand. The script asserts the
PDF hash and that each quoted sentence fragment, which contains the printed value, occurs on the
stated page of the pdftotext (reading-order) output, after collapsing whitespace.
"""
import csv, hashlib, json, os, re, subprocess, sys
from collections import Counter

PDF_SHA = "4c1699cb964ae588117a6737f5e9e189eb9a5ef5ff78568d2a99e7a13d6608fe"
PDF_URL = "https://bmcgenomics.biomedcentral.com/counter/pdf/10.1186/s12864-026-12965-8.pdf"
P = "gfm-guides-20261014-kendiukhov2026"
SRC = f"{P}-source-article"
DATE = "2026-10-14"
FACETS = {"areas": ["single-cell", "biological-networks"], "contexts": ["research"]}
REVIEWER_NOTE = ("Collector agent issue-129 for the 2026-10-14 genomic foundation model guide fixes; "
                 "extraction only, not a review. Pending an independent review-evidence pass.")

pdf, out = sys.argv[1], sys.argv[2]
assert hashlib.sha256(open(pdf, "rb").read()).hexdigest() == PDF_SHA, "article PDF hash mismatch"
text = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True, check=True).stdout
PAGES = [re.sub(r"\s+", " ", p).replace("- ", "-") for p in text.split("\f")]

records, claims_rows = [], []


def rec(id_, kind, name, description, attributes, links=(), facets=None, source_ids=(SRC,)):
    records.append({"id": id_, "kind": kind, "name": name, "description": description, "status": "needs_review",
                    "facets": FACETS if facets is None else facets, "source_ids": list(source_ids),
                    "links": [{"relation": a, "target_id": b} for a, b in links], "attributes": attributes})


# ---------------------------------------------------------------- source
rec(SRC, "source", "Systematic evaluation of single-cell foundation model interpretability: attention-derived edge scores add no incremental value over gene-level features for perturbation-target prediction (Kendiukhov 2026, BMC Genomics 27:634)",
    "Publisher PDF of the article, retrieved and hashed for the 2026-10-14 genomic foundation model guide fixes (issue rewire-benchmark-data#129).",
    {"url": "https://doi.org/10.1186/s12864-026-12965-8", "artifact_url": PDF_URL,
     "version": "Version of record, BMC Genomics 27:634, published 2026-07-22 (received 2026-03-10, accepted 2026-05-14)",
     "retrieved_at": "2026-10-14T12:01:07Z", "artifact_sha256": PDF_SHA, "doi": "10.1186/s12864-026-12965-8",
     "publication_status": "peer_reviewed", "licence": "CC-BY-4.0", "media_type": "application/pdf",
     "venue": "BMC Genomics", "year": 2026,
     "limitations": [
         "Single-author study; the author developed none of the evaluated foundation models but did develop CSSI and the evaluation framework.",
         "Objective B results are printed in running text only; Figures 3, 4, 6 and 7 are not read.",
         "Primary layer L13 was pre-specified on DLPFC brain data; L15 and L6 values come from an 18-layer profile (L15 selected by nested cross-validation).",
     ],
     "evidence_concerns": [
         {"source_id": SRC,
          "message": "The K562 CRISPRa analysis cites reference 25, Adamson et al. 2016 (Cell 167:1867), which is a CRISPRi Perturb-seq study of the unfolded protein response. The Data availability statement lists 'Dixit/Adamson/Shifrut datasets'. The CRISPRa dataset identity should be checked before the CRISPRa results are compared.",
          "source_locator": "Page 10, 'Context-dependent attention-correlation relationship', sentence 2 ('On K562 CRISPRa [25] (n = 77)'); reference 25; 'Data availability'",
          "artifact_sha256": PDF_SHA, "review_date": DATE},
         {"source_id": SRC,
          "message": "K562 CRISPRi results are reported on two perturbation sets: n = 151 for correlation edges and the gene-level baselines (Fig. 3) and n = 280 evaluable perturbations for the attention versus correlation comparison, where correlation scores 0.703 against 0.696 on the 151 set. The article does not say how the two sets relate. RPE1 is likewise reported at n = 1,251 (attention versus correlation) and n = 1,167 (confound battery), with attention 0.748 (L15) and 0.747 (layer not stated).",
          "source_locator": "Page 7, 'Perturbation-first validation reveals gene-level dominance', paragraphs 1-3; page 10, 'Context-dependent attention-correlation relationship' and 'Cross-cell-type generalisation of confound pattern'",
          "artifact_sha256": PDF_SHA, "review_date": DATE},
     ],
     "review": {"method": ["source-hash-verification"], "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE, "date": DATE}},
    source_ids=())

# ---------------------------------------------------------------- benchmark and protocols
BENCH = f"{P}-benchmark-perturbation-target-prediction"
rec(BENCH, "benchmark", "Perturbation-target prediction from attention-derived edge scores (Kendiukhov 2026, Objective B)",
    "For each CRISPR perturbation, score every other gene by an edge score to the perturbed gene (attention, Spearman correlation) or by a gene-level statistic (variance, mean expression, dropout rate), and measure AUROC for classifying the differentially expressed targets. Incremental-value tests add edge scores to a gene-level logistic regression.",
    {"entity_level": "suite", "version": "BMC Genomics 27:634 (2026)",
     "task": "Predict which genes are differentially expressed after a CRISPRi or CRISPRa perturbation",
     "scope_note": "Replogle genome-scale CRISPRi (K562, RPE1) and a K562 CRISPRa dataset; T cell and iPSC neuron sets have n = 7 perturbations and print no AUROC values.",
     "source_locator": "Pages 4 and 7-10, 'Results'; pages 13-14, 'Methods'"})

PF_IMPL = "Per-perturbation AUROC for classifying differentially expressed targets (Mann-Whitney U test with Benjamini-Hochberg correction and an LFC threshold define DE hits); summary across perturbations not stated"
PROTOS = {
    "pf-k562-crispri": ("Perturbation-first AUROC, K562 CRISPRi (Kendiukhov 2026)",
                        "Edge or gene-level scores rank all other genes for each Replogle K562 CRISPRi perturbation; AUROC against DE targets. Primary parameterisation N_ctrl = 2,000 control cells, HVG = 2,000, LFC > 0.5.",
                        "N_ctrl = 2,000, HVG = 2,000, LFC > 0.5 (primary parameterisation)", "Page 7 paragraph 1; page 14 'Perturbation-first validation'"),
    "pf-k562-crispra": ("Perturbation-first AUROC, K562 CRISPRa (Kendiukhov 2026)",
                        "As the K562 CRISPRi protocol, on the K562 CRISPRa dataset cited as reference 25.",
                        "Parameters for the CRISPRa run are not restated", "Page 10, 'Context-dependent attention-correlation relationship'"),
    "pf-rpe1-crispri": ("Perturbation-first AUROC, RPE1 CRISPRi (Kendiukhov 2026)",
                        "As the K562 CRISPRi protocol, on Replogle RPE1 CRISPRi, with 3,309 HVGs (perturbation genes forced into the HVG set).",
                        "N_ctrl = 2,000, HVG = 3,309 with perturbation genes forced in (Methods); the LFC threshold for the reported RPE1 values is not restated", "Page 10; page 14 'Perturbation-first validation'"),
    "incremental-value-lr": ("Gene-level logistic regression under 5-fold GroupKFold by perturbation (Kendiukhov 2026)",
                             "Logistic regression on perturbation-gene pairs with gene-level features (mean expression, variance, dropout rate), optionally plus an edge score, under 5-fold GroupKFold cross-validation grouped by perturbation; cross-validated AUROC over pairs.",
                             "Perturbation-gene pairs; 5-fold GroupKFold grouped by perturbation", "Page 8 'No incremental pairwise value on the perturbation-target prediction task'; page 14 'Confound decomposition'"),
    "propensity-matched": ("Propensity-matched edge AUROC (Kendiukhov 2026)",
                           "Each DE-positive target matched to k = 5 DE-negative targets with similar expression mean, variance and dropout rate by propensity-score nearest-neighbour matching; edge-score AUROC on the matched pairs.",
                           "Propensity-matched perturbation-gene pairs, k = 5", "Page 9 paragraph 1; page 10 'Cross-cell-type generalisation of confound pattern'; page 14 'Confound decomposition'"),
}
IMPL = {k: PF_IMPL if k.startswith("pf-") else ("Cross-validated AUROC over perturbation-gene pairs" if k == "incremental-value-lr" else "AUROC over propensity-matched perturbation-gene pairs") for k in PROTOS}
PROTO = {}
for slug, (name, desc, inputs, loc) in PROTOS.items():
    PROTO[slug] = f"{P}-protocol-{slug}"
    rec(PROTO[slug], "protocol", name, desc,
        {"protocol": desc, "version": "BMC Genomics 27:634", "metric": "auroc", "metric_direction": "higher", "unit": "unitless",
         "metric_implementation": IMPL[slug],
         "source_locator": loc,
         "limitations": ["Single run; no repeat across seeds reported for these values."]},
        links=[("part_of", BENCH)])

# ---------------------------------------------------------------- datasets
DATA = {
    "k562-crispri-151": ("Replogle genome-scale CRISPRi, K562, 151 perturbations (Kendiukhov 2026)",
                         "Replogle et al. 2022 genome-scale CRISPRi Perturb-seq in K562 (>640,000 cells, 2,024 perturbed genes); 151 perturbations evaluated under the primary parameterisation.",
                         {"source_dataset_label": "Replogle genome-scale CRISPRi (K562)", "scored_count": 151}, "Page 7 paragraph 1; Fig. 3 caption"),
    "k562-crispri-280": ("Replogle genome-scale CRISPRi, K562, 280 evaluable perturbations (Kendiukhov 2026)",
                         "The 280 evaluable K562 CRISPRi perturbations used for the attention versus correlation comparison and the 280 x 1,999 perturbation-gene incremental-value dataset (559,720 pairs, 2.8% positive).",
                         {"source_dataset_label": "Replogle genome-scale CRISPRi (K562)", "scored_count": 280}, "Page 7 paragraph 2; page 8 'No incremental pairwise value'"),
    "k562-crispri-propensity-matched": ("Replogle CRISPRi K562, propensity-matched pairs (Kendiukhov 2026)",
                                        "59,153 propensity-matched perturbation-gene pairs (26.5% positive) from the K562 CRISPRi incremental-value dataset.",
                                        {"source_dataset_label": "Replogle genome-scale CRISPRi (K562), propensity-matched", "scored_count": 59153}, "Page 9 paragraph 1"),
    "k562-crispra-77": ("K562 CRISPRa, 77 perturbations (Kendiukhov 2026)",
                        "K562 CRISPRa perturbation dataset cited as reference 25 (Adamson et al. 2016); 77 perturbations.",
                        {"source_dataset_label": "K562 CRISPRa [25]", "scored_count": 77}, "Page 10, 'Context-dependent attention-correlation relationship'"),
    "rpe1-crispri-1251": ("Replogle genome-scale CRISPRi, RPE1, 1,251 evaluable perturbations (Kendiukhov 2026)",
                          "Replogle et al. 2022 CRISPRi Perturb-seq in RPE1 retinal epithelial cells; 1,251 evaluable perturbations for the attention versus correlation comparison.",
                          {"source_dataset_label": "Replogle CRISPRi (RPE1)", "scored_count": 1251}, "Page 10, 'Context-dependent attention-correlation relationship'"),
    "rpe1-crispri-1167": ("Replogle genome-scale CRISPRi, RPE1, 1,167 perturbations, confound battery (Kendiukhov 2026)",
                          "1,167 evaluated RPE1 perturbations and 3,838,263 gene-pair observations used for the RPE1 confound-decomposition battery.",
                          {"source_dataset_label": "Replogle CRISPRi (RPE1)", "scored_count": 1167}, "Page 10, 'Cross-cell-type generalisation of confound pattern'"),
    "rpe1-crispri-propensity-matched": ("Replogle CRISPRi RPE1, propensity-matched pairs (Kendiukhov 2026)",
                                        "Propensity-matched pairs from the RPE1 confound battery; the matched count is not printed.",
                                        {"source_dataset_label": "Replogle CRISPRi (RPE1), propensity-matched"}, "Page 10, 'Cross-cell-type generalisation of confound pattern', item (iii)"),
}
DS = {}
for slug, (name, desc, extra, loc) in DATA.items():
    DS[slug] = f"{P}-data-{slug}"
    a = {"split": "No train/test split for edge AUROC; cross-validation where stated by the protocol", **extra, "source_locator": loc,
         "missing_metadata": {"version": {"reason": "unreported"}}}
    rec(DS[slug], "dataset_subset", name, desc, a)

# ---------------------------------------------------------------- methods and configurations
GF_ACCESS = "Analysis code github.com/Biodyn-AI/biomechinterp-framework and Zenodo 10.5281/zenodo.18701417; not pinned to a commit in the article"
GF_CKPT = "Geneformer V2-316M, HuggingFace ctheodoris/Geneformer subfolder Geneformer-V2-316M (18 layers, 18 heads), loaded with attn_implementation='eager'; revision not stated"
METHODS = {
    "spearman-edge": ("Absolute Spearman correlation edge score", "Absolute Spearman correlation between the perturbed gene and each other gene across the control cells used for attention extraction.", "Spearman correlation"),
    "gene-variance": ("Target-gene expression variance", "Ranks candidate target genes by their expression variance; no model and no pairwise information.", "variance"),
    "gene-mean-expression": ("Target-gene mean expression", "Ranks candidate target genes by their mean expression; no model and no pairwise information.", "mean expression"),
    "gene-dropout-rate": ("Target-gene dropout rate", "Ranks candidate target genes by their dropout rate; no model and no pairwise information.", "dropout"),
    "gene-level-logistic-regression": ("Gene-level logistic regression (mean expression, variance, dropout rate)", "Logistic regression on gene-level features of the candidate target gene, trained under 5-fold GroupKFold by perturbation.", "Gene-level features"),
}
for slug, (name, desc, reported) in METHODS.items():
    rec(f"{P}-method-{slug}", "method", name, desc,
        {"reported_name": reported, "entity_level": "method", "source_locator": "Page 4 'Evaluation framework'; page 13 'Model coverage by analysis family'; page 14 'Confound decomposition'",
         "missing_metadata": {"version": {"reason": "inapplicable", "note": "Simple statistic or model defined in the article"}}},
        facets={**FACETS, "method_types": ["conventional_pipeline"] if slug != "gene-level-logistic-regression" else ["supervised_machine_learning"]})

CONFIGS = {
    "geneformer-v2-316m-attention-l13": ("Geneformer V2-316M attention edges, layer 13 (Kendiukhov 2026)", "catalog-model-geneformer", True,
                                        "Attention from layer 13, averaged over heads within the layer and then over cells, between the perturbed gene and each other gene. L13 was pre-specified from DLPFC brain data before K562 data were examined.", "Geneformer V2-316M attention L13"),
    "geneformer-v2-316m-attention-l15": ("Geneformer V2-316M attention edges, layer 15 (Kendiukhov 2026)", "catalog-model-geneformer", True,
                                        "Attention from layer 15, averaged over heads and cells. On K562 CRISPRi, L15 was selected as the best of 18 layers by nested cross-validation; on RPE1 it is one of all layers reported.", "Geneformer V2-316M attention L15"),
    "geneformer-v2-316m-attention-l6": ("Geneformer V2-316M attention edges, layer 6 (Kendiukhov 2026)", "catalog-model-geneformer", True,
                                       "Attention from layer 6, averaged over heads and cells (RPE1 only).", "Geneformer V2-316M attention L6"),
    "geneformer-v2-316m-attention-layer-unstated": ("Geneformer V2-316M attention edges, layer not stated (Kendiukhov 2026)", "catalog-model-geneformer", True,
                                                    "Attention edges from Geneformer V2-316M where the article does not name the layer (K562 CRISPRa, K562 propensity-matched, RPE1 confound battery).", "attention"),
    "spearman-edge": ("Absolute Spearman correlation edges (Kendiukhov 2026)", f"{P}-method-spearman-edge", False,
                      "Absolute Spearman correlation between the perturbed gene and each other gene across the same control cells used for attention extraction.", "correlation"),
    "gene-variance": ("Target-gene variance baseline (Kendiukhov 2026)", f"{P}-method-gene-variance", False, "Variance of each candidate target gene.", "variance"),
    "gene-mean-expression": ("Target-gene mean expression baseline (Kendiukhov 2026)", f"{P}-method-gene-mean-expression", False, "Mean expression of each candidate target gene.", "mean expression"),
    "gene-dropout-rate": ("Target-gene dropout rate baseline (Kendiukhov 2026)", f"{P}-method-gene-dropout-rate", False, "Dropout rate of each candidate target gene.", "dropout"),
    "gene-level-logistic-regression": ("Gene-level logistic regression (Kendiukhov 2026)", f"{P}-method-gene-level-logistic-regression", False,
                                       "Logistic regression on mean expression, variance and dropout rate of the candidate target gene, 5-fold GroupKFold by perturbation.", "Gene-level features alone"),
}
CFG = {}
for slug, (name, target, fm, desc, reported) in CONFIGS.items():
    CFG[slug] = f"{P}-config-{slug}"
    a = {"reported_name": reported, "foundation_model_eligible": fm, "representation": desc,
         "source_locator": "Page 13 'Models and data', 'Attention extraction and edge score computation', 'Model coverage by analysis family'"}
    if fm:
        a.update({"training_setting": "Zero-shot; pretrained weights, attention read out without fine-tuning",
                  "checkpoint": GF_CKPT, "version": "Geneformer V2-316M", "access_reuse": GF_ACCESS})
    else:
        a.update({"training_setting": "Computed from each dataset's control cells" if slug != "gene-level-logistic-regression" else "Fitted under 5-fold GroupKFold by perturbation on each dataset",
                  "access_reuse": GF_ACCESS, "missing_metadata": {"version": {"reason": "inapplicable", "note": "Defined in the article"}}})
    rec(CFG[slug], "configuration", name, desc, a, links=[("configuration_of", target)],
        facets={**FACETS, "method_types": ["foundation_model"] if fm else (["supervised_machine_learning"] if slug == "gene-level-logistic-regression" else ["conventional_pipeline"])})

# ---------------------------------------------------------------- evaluations and results
ORIGIN = {"gene-level-logistic-regression": "author_reported"}
EVALS = {}


def evaluation(cfg, proto, ds, aggregation):
    eid = f"{P}-eval-{proto}-{ds}-{cfg}"
    if eid in EVALS:
        return eid
    EVALS[eid] = f"{CONFIGS[cfg][0].removesuffix(' (Kendiukhov 2026)')} on {DATA[ds][0].removesuffix(' (Kendiukhov 2026)')}"
    rec(eid, "evaluation", EVALS[eid], "Published comparison transcribed from the pinned source; not reproduced.",
        {"origin": ORIGIN.get(cfg, "independent_paper"), "protocol": PROTO[proto], "version": "BMC Genomics 27:634 as retrieved 2026-10-14",
         "comparison": {"protocol_id": PROTO[proto], "dataset_version": None,
                        "split": "5-fold GroupKFold by perturbation" if proto == "incremental-value-lr" else "No train/test split; scores computed from control cells and compared with DE labels",
                        "population": None,
                        "inputs": "Control-cell expression and DE labels of the perturbation dataset; " + PROTOS[proto][2],
                        "adaptation": "Foundation-model attention read out zero-shot; correlation and gene-level statistics computed from the same control cells; logistic regression fitted under GroupKFold",
                        "metric_implementation": IMPL[proto], "aggregation": aggregation, "budget": None},
         "source_locator": DATA[ds][3],
         "missing_metadata": {"comparison.dataset_version": {"reason": "unreported"},
                              "comparison.population": {"reason": "unreported"},
                              "comparison.budget": {"reason": "unreported"}}},
        links=[("system", CFG[cfg]), ("assessment", PROTO[proto]), ("data", DS[ds])])
    return eid


QUAL = {"pf-k562-crispri": "per-perturbation AUROC for DE targets (LFC > 0.5), summarised over perturbations; K562 CRISPRi",
        "pf-k562-crispra": "per-perturbation AUROC for DE targets, summarised over perturbations; K562 CRISPRa",
        "pf-rpe1-crispri": "per-perturbation AUROC for DE targets, summarised over perturbations; RPE1 CRISPRi",
        "incremental-value-lr": "cross-validated AUROC over perturbation-gene pairs, 5-fold GroupKFold by perturbation",
        "propensity-matched": "AUROC over propensity-matched perturbation-gene pairs (k = 5 negatives per positive)"}
PF_AGG = "Summary over perturbations; statistic not stated"
# (cfg, protocol, dataset, printed, page, section and sentence locator, quoted fragment that must appear on the page, uncertainty or None)
VALUES = [
    ("spearman-edge", "pf-k562-crispri", "k562-crispri-151", "0.696", 7,
     "Page 7, 'Perturbation-first validation reveals gene-level dominance', paragraph 1, sentence 3", "AUROC = 0.696 under the primary parameterisation", None),
    ("gene-variance", "pf-k562-crispri", "k562-crispri-151", "0.881", 7,
     "Page 7, 'Perturbation-first validation reveals gene-level dominance', paragraph 3, sentence 2", "Variance alone achieves AUROC = 0.881", None),
    ("geneformer-v2-316m-attention-l13", "pf-k562-crispri", "k562-crispri-280", "0.704", 7,
     "Page 7, 'Perturbation-first validation reveals gene-level dominance', paragraph 2, sentence 1", "AUROC = 0.704 at L13 (n = 280 evaluable perturbations)", None),
    ("spearman-edge", "pf-k562-crispri", "k562-crispri-280", "0.703", 7,
     "Page 7, 'Perturbation-first validation reveals gene-level dominance', paragraph 2, sentence 1", "(0.703; Wilcoxon p = 0.73", None),
    ("geneformer-v2-316m-attention-l15", "pf-k562-crispri", "k562-crispri-280", "0.743", 7,
     "Page 7, 'Perturbation-first validation reveals gene-level dominance', paragraph 2, sentence 5 (nested cross-validation over 18 layers)", "identifies L15 as the best layer (AUROC = 0.743", None),
    ("gene-level-logistic-regression", "incremental-value-lr", "k562-crispri-280", "0.895", 8,
     "Page 8, 'No incremental pairwise value on the perturbation-target prediction task', paragraph 1, sentence 2", "Gene-level features alone achieve AUROC = 0.895 [bootstrap 95% CI: 0.884, 0.905]",
     {"type": "confidence_interval", "lower": "0.884", "upper": "0.905", "level": 0.95, "method": "bootstrap", "printed": "[bootstrap 95% CI: 0.884, 0.905]",
      "note": "Methods: bootstrap CIs use 200 iterations with perturbation-level resampling unless otherwise noted"}),
    ("geneformer-v2-316m-attention-layer-unstated", "propensity-matched", "k562-crispri-propensity-matched", "0.609", 9,
     "Page 9, paragraph 1 (continuing 'No incremental pairwise value'), sentence 3", "retain modest raw discriminability (AUROC = 0.609)", None),
    ("geneformer-v2-316m-attention-layer-unstated", "pf-k562-crispra", "k562-crispra-77", "0.55", 10,
     "Page 10, 'Context-dependent attention-correlation relationship', sentence 3", "(AUROC 0.55 vs. 0.65", None),
    ("spearman-edge", "pf-k562-crispra", "k562-crispra-77", "0.65", 10,
     "Page 10, 'Context-dependent attention-correlation relationship', sentence 3", "(AUROC 0.55 vs. 0.65", None),
    ("geneformer-v2-316m-attention-l15", "pf-rpe1-crispri", "rpe1-crispri-1251", "0.748", 10,
     "Page 10, 'Context-dependent attention-correlation relationship', sentence 4", "(L15: 0.748 vs. 0.658", None),
    ("spearman-edge", "pf-rpe1-crispri", "rpe1-crispri-1251", "0.658", 10,
     "Page 10, 'Context-dependent attention-correlation relationship', sentence 4", "(L15: 0.748 vs. 0.658", None),
    ("geneformer-v2-316m-attention-l6", "pf-rpe1-crispri", "rpe1-crispri-1251", "0.776", 10,
     "Page 10, 'Context-dependent attention-correlation relationship', sentence 4", "L6: 0.776", None),
    ("gene-variance", "pf-rpe1-crispri", "rpe1-crispri-1167", "0.866", 10,
     "Page 10, 'Cross-cell-type generalisation of confound pattern', item (i)", "variance AUROC = 0.866, mean expression = 0.851, dropout = 0.797 vs. attention = 0.747 and correlation = 0.658", None),
    ("gene-mean-expression", "pf-rpe1-crispri", "rpe1-crispri-1167", "0.851", 10,
     "Page 10, 'Cross-cell-type generalisation of confound pattern', item (i)", "variance AUROC = 0.866, mean expression = 0.851, dropout = 0.797 vs. attention = 0.747 and correlation = 0.658", None),
    ("gene-dropout-rate", "pf-rpe1-crispri", "rpe1-crispri-1167", "0.797", 10,
     "Page 10, 'Cross-cell-type generalisation of confound pattern', item (i)", "variance AUROC = 0.866, mean expression = 0.851, dropout = 0.797 vs. attention = 0.747 and correlation = 0.658", None),
    ("geneformer-v2-316m-attention-layer-unstated", "pf-rpe1-crispri", "rpe1-crispri-1167", "0.747", 10,
     "Page 10, 'Cross-cell-type generalisation of confound pattern', item (i)", "variance AUROC = 0.866, mean expression = 0.851, dropout = 0.797 vs. attention = 0.747 and correlation = 0.658", None),
    ("spearman-edge", "pf-rpe1-crispri", "rpe1-crispri-1167", "0.658", 10,
     "Page 10, 'Cross-cell-type generalisation of confound pattern', item (i)", "variance AUROC = 0.866, mean expression = 0.851, dropout = 0.797 vs. attention = 0.747 and correlation = 0.658", None),
    ("gene-level-logistic-regression", "incremental-value-lr", "rpe1-crispri-1167", "0.942", 10,
     "Page 10, 'Cross-cell-type generalisation of confound pattern', item (ii)", "Gene-level features alone achieve AUROC = 0.942 under 5-fold GroupKFold CV", None),
    ("geneformer-v2-316m-attention-layer-unstated", "propensity-matched", "rpe1-crispri-propensity-matched", "0.568", 10,
     "Page 10, 'Cross-cell-type generalisation of confound pattern', item (iii)", "(attention = 0.568, correlation = 0.561)", None),
    ("spearman-edge", "propensity-matched", "rpe1-crispri-propensity-matched", "0.561", 10,
     "Page 10, 'Cross-cell-type generalisation of confound pattern', item (iii)", "(attention = 0.568, correlation = 0.561)", None),
]
for cfg, proto, ds, printed, page, loc, fragment, unc in VALUES:
    assert fragment in PAGES[page - 1], (page, fragment)
    assert printed in fragment, (printed, fragment)
    agg = PF_AGG if proto.startswith("pf-") else "Pooled over perturbation-gene pairs"
    eid = evaluation(cfg, proto, ds, agg)
    rid = eid.replace("-eval-", "-result-") + "-auroc"
    full_loc = f"{loc}: '{fragment}'"
    a = {"metric": "auroc", "metric_direction": "higher", "unit": "unitless", "printed_value": printed, "numeric_value": printed,
         "metric_qualifier": QUAL[proto], "source_locator": full_loc,
         "review": {"method": ["transcription", "pdf-text-parse"],
                    "method_note": "Hand transcription from the article text; extract/extract_kendiukhov2026.py asserts that the quoted fragment, which contains the printed value, occurs on the stated page of the pdftotext output of the pinned PDF.",
                    "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE, "date": DATE, "artifact_sha256": PDF_SHA, "retrieval_url": PDF_URL,
                    "note": "Extracted, not reviewed. The review-evidence pass must re-check this value against the pinned artifact."}}
    if unc:
        a["uncertainty"] = unc
    else:
        a["missing_metadata"] = {"uncertainty": {"reason": "unreported"}}
    rec(rid, "result", f"{EVALS[eid]}: AUROC", "Reported measurement transcribed from the pinned source. Not independently reproduced.",
        a, links=[("evaluation", eid)], facets={})
    claims_rows.append([rid, SRC, full_loc, printed, "result"])

# ---------------------------------------------------------------- claim: layer pre-specification
cid = f"{P}-claim-l13-prespecified"
frag = "L13 was pre-specified as the primary layer based on independent data"
assert frag in PAGES[6]
loc = f"Page 7, 'Perturbation-first validation reveals gene-level dominance', paragraph 2, sentence 2: '{frag}'"
val = "Layer 13 was pre-specified as the primary attention layer from DLPFC brain data (TRRUST recovery AUROC 0.694) before any K562 perturbation data were examined; other layers are secondary analyses."
rec(cid, "claim", "Geneformer V2-316M layer 13 pre-specified as primary layer (Kendiukhov 2026)", val,
    {"field": "layer_selection", "value": val, "source_locator": loc,
     "review": {"method": ["transcription", "pdf-text-parse"], "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE, "date": DATE,
                "artifact_sha256": PDF_SHA, "retrieval_url": PDF_URL, "note": "Extracted, not reviewed."}},
    links=[("subject", CFG["geneformer-v2-316m-attention-l13"])], facets={})
claims_rows.append([cid, SRC, loc, "L13 pre-specified", "claim"])

# ---------------------------------------------------------------- write
records.sort(key=lambda r: r["id"])
assert len({r["id"] for r in records}) == len(records)
with open(os.path.join(out, "batch.jsonl"), "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
claims_rows.sort()
with open(os.path.join(out, "claims.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(claims_rows)
counts = Counter(r["kind"] for r in records)
print(dict(sorted(counts.items())))
assert counts["result"] == len(VALUES) == 20
