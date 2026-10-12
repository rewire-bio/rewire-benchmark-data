"""Deterministic extraction of the cfMeDIP-seq methylation and fragmentomic classifier comparison in Zeng et al. 2026.

Usage: python3 -I extract_zeng2026.py <download-dir> <batch-dir>

Reads two pinned artifacts:
  - the article, PMC12948677 full-text JATS XML (Nature Cancer 2026, 10.1038/s43018-026-01116-3)
  - Source Data Fig. 4 (43018_2026_1116_MOESM6_ESM.xlsx), all eight sheets Fig.4a-Fig.4h
Every cell of the eight sheets is extracted: per feature set, the mean, s.d., minimum and maximum AUC over the
cross-validation fold models (a, c, e, g) and the mean and spread of sensitivity at 99% specificity (b, d, f, h).
The header row, row labels and row counts are asserted, and the sentences of the article that the records rely on
are checked against the XML text. Writes batch.jsonl, claims.csv and use-case-links.json.

Corrections from the independent review (docs/reviews/use-cases/plasma-ctdna-use-cases-2026-10-12.md) are applied here
and marked with their review item (A2, Z1 to Z4); B.finalize applies the review to every record.
"""
import os, re, sys
import xml.etree.ElementTree as ET
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rawxlsx  # noqa: E402
from common import (Batch, FACETS, UC_METH, UC_FRAG, Q_METH, Q_FRAG, sha, expect, shortest)  # noqa: E402

DL, BATCH = sys.argv[1], sys.argv[2]
B = Batch("ctdnalit-20261011-zeng2026", "2026-10-11")
P = B.P
XML, SD = f"{DL}/zeng/PMC12948677.xml", f"{DL}/zeng/43018_2026_1116_MOESM6_ESM.xlsx"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12948677/fullTextXML"
SD_URL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs43018-026-01116-3/MediaObjects/43018_2026_1116_MOESM6_ESM.xlsx"
S_ART, S_SD = f"{P}-source-article", f"{P}-source-source-data-fig4"
SRC = [S_ART, S_SD]

# ---------------------------------------------------------------- article text checks
root = ET.parse(XML).getroot()
FLAT = " ".join(" ".join("".join(p.itertext()).split()) for p in root.iter("p"))


def has(fragment, where):
    expect(fragment in FLAT, True, where)


for frag in (
        "classifiers based on PCs derived from methylation alone achieved the highest mean area under the curve (mAUC) across model folds (0.986)",
        "Integrating PCs that contributed >1% of the variance for methylation, 5′ end motifs and fragment ratios resulted in an mAUC of 0.974",
        "The combination of fragment ratios and methylation achieved the highest mAUC of 0.954 (Fig. 4c), close to the primary PE results of 0.961",
        "However, fragment ratios and methylation alone produced mAUCs of 0.848 and 0.674, respectively (Fig. 4c)",
        "At 99% specificity, sensitivity was 76.6 ± 4.0% for the combined model versus 63.3 ± 1.9% for methylation",
        "Differences in 5′ motif baselines for the HCC healthy controls, likely protocol-related",
        "In our primary SE dataset, methylation achieved an mAUC of 0.938 across folds, whereas 5′ end motifs outperformed methylation with an mAUC of 0.965",
        "Error bars in a,c,e and g represent ±1 × s.d. across cross-validation folds (n = 10). In b,d f and h, dots show per-fold means (n = 10), and error bars indicate the s.e.",
        "External validation was performed using either an independent cohort (for PE data) or a 10% hold-out set (for SE data), which was excluded from PCA, training and hyperparameter tuning.",
        "We were restricted to 95 baseline samples that passed the QC for our validation",
        "for the same validation set (n = 140 samples)",
        "validation SE dataset (n = 39 samples [nHealthy = 9, nAML = 5, nBladder cancer = 2, nBreast cancer = 5, nColorectal cancer = 3, nLung cancer = 7, nPancreatic cancer = 6, nRenal cancer = 2])",
        "primary PE dataset (total samples n = 356 [nAML = 5, nLung cancer = 59, nUveal Melanoma = 10, nProstate cancer = 97, nHead & neck cancer = 33, nBrain cancer = 152] and healthy controls n = 64)",
        "primary SE dataset (total samples: n = 339 [nHealthy = 76, nAML = 53, nBladder cancer = 17, nBreast cancer = 20, nColorectal cancer = 20, nLung cancer = 70, nPancreatic cancer = 65, nRenal cancer = 18])",
        "In cancer versus healthy classification (Fig. 4c), LFS-previvor and LFS-survivor cases were excluded from training but scored post hoc",
        "for sensitivity summaries, they were labeled as ‘cancer’ given their elevated risk",
        "We benchmarked multiple classification algorithms, including LASSO, support vector machines, random forest, gradient-boosting machines and XGBoost",
        "S.L.W. and M.M.H. have a patent application licensed to Adela."):
    has(frag, f"article sentence: {frag[:60]}")

# ---------------------------------------------------------------- sources
B.source(S_ART, "A pan-cancer compendium of 1,294 plasma cell-free DNA methylomes and fragmentomes enabling multicancer detection",
         "Primary source retrieved and hashed for the 2026-10-11 plasma ctDNA literature pass.",
         {"url": "https://doi.org/10.1038/s43018-026-01116-3", "artifact_url": XML_URL,
          "version": "Nature Cancer, published online 2026-02-19; Europe PMC full-text JATS XML of PMC12948677",
          "retrieved_at": "2026-10-11T21:40:43Z", "artifact_sha256": sha(XML), "doi": "10.1038/s43018-026-01116-3",
          "publication_status": "peer_reviewed", "licence": "CC-BY-NC-ND-4.0", "media_type": "application/xml",
          "source_locator": ("Full artifact bytes; per-record locators on each record. 'Pn' is the zero-based index of the <p> "
                             "element in document order in this JATS XML, front matter included."),  # review A2
          "archive_note": "Not archived in the batch: CC BY-NC-ND 4.0. The artifact_sha256 pins the bytes that were read.",
          "scope_note": ("Developer study: the authors produced the cfMeDIP-seq cohorts (The Cancer Genetics and Epigenetics project) "
                         "and built and ran every classifier. Two authors have a patent application licensed to Adela and one "
                         "author declares stock and a leadership position in Adela (Competing interests).")})
B.source(S_SD, "Zeng et al. 2026, Source Data Fig. 4 (classifier AUC and sensitivity summaries)",
         "Supplementary Source Data workbook retrieved and hashed for the 2026-10-11 plasma ctDNA literature pass.",
         {"url": "https://doi.org/10.1038/s43018-026-01116-3", "artifact_url": SD_URL,
          "version": "43018_2026_1116_MOESM6_ESM.xlsx (Source Data Fig. 4), publisher supplementary file",
          "retrieved_at": "2026-10-11T21:41:25Z", "artifact_sha256": sha(SD), "doi": "10.1038/s43018-026-01116-3",
          "publication_status": "peer_reviewed", "licence": "CC-BY-NC-ND-4.0",
          "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          "source_locator": "Sheets Fig.4a to Fig.4h; per-result locators on each result",
          "retrieval_note": "The same bytes are served inside the Europe PMC supplementaryFiles bundle for PMC12948677 (checked 2026-10-11T21:40:45Z).",
          "archive_note": "Not archived in the batch: CC BY-NC-ND 4.0; the 17,627-byte file is pinned by hash."})
# Review Z1: the 0.694 against 0.674 conflict is a result-level dispute (source_warnings on the result), not a source concern.

# ---------------------------------------------------------------- datasets
D = {k: f"{P}-data-{k}" for k in ("pe-primary", "pe-validation", "se-primary", "se-validation")}
COMMON_SCOPE = ("cfMeDIP-seq of baseline plasma samples from The Cancer Genetics and Epigenetics (TCGE) studies, processed with "
                "MEDIPIPE and normalised with ComBat-seq and DESeq2 separately for paired-end (PE) and single-end (SE) data. "
                "Clinically diagnosed cancers and healthy donors; not a screening population.")
B.rec(D["pe-primary"], "dataset", "Zeng et al. 2026 primary paired-end cfMeDIP-seq dataset (420 samples)",
      "Paired-end cfMeDIP-seq baseline samples of the TCGE studies used for classifier training and cross-validation, LFS cases excluded.", SRC,
      attributes={"version": "Zeng et al. 2026 primary PE dataset", "total": 420, "positives": 356, "negatives": 64,
                  "population": "356 cancers (AML 5, lung 59, uveal melanoma 10, prostate 97, head and neck 33, brain 152) and 64 healthy controls",
                  "assay": "cfMeDIP-seq, paired-end", "scope_note": COMMON_SCOPE,
                  "source_locator": "Extended Data Fig. 7b and Fig. 9 legends; Results P29; Methods P59-P62"})
B.rec(D["pe-validation"], "dataset", "Zeng et al. 2026 independent paired-end validation dataset",
      "Independent paired-end cfMeDIP-seq cohorts (TCGE-CFMe-LFS, TCGE-CFMe-INSPIRE cancers and TCGE-CFMe-HCC healthy donors).", SRC,
      attributes={"version": "Zeng et al. 2026 PE validation dataset",
                  "population": ("Cancers of the INSPIRE pembrolizumab study (mixed, ovarian, breast, head and neck, melanoma), LFS-positive, "
                                 "LFS-survivor and LFS-previvor carriers, and healthy donors from the HCC study. The text says 95 baseline "
                                 "samples passed QC; the Extended Data Fig. 9f legend gives n = 140 for the same validation set."),
                  "assay": "cfMeDIP-seq, paired-end",
                  "scope_note": (COMMON_SCOPE + " LFS-previvor and LFS-survivor cases were excluded from training but scored and, for "
                                 "sensitivity summaries, labelled as cancer. The 17 HCC-study healthy controls used a different laboratory "
                                 "protocol that shifts their 5' end-motif baseline."),
                  "missing_metadata": {"total": {"reason": "conflicting", "note": "95 in Results P28, 140 in the Extended Data Fig. 9f legend"}},
                  "source_locator": "Results P28 and P32; Extended Data Fig. 7e and Fig. 9f legends"})
B.rec(D["se-primary"], "dataset", "Zeng et al. 2026 primary single-end cfMeDIP-seq dataset (339 samples)",
      "Single-end cfMeDIP-seq baseline samples of the TCGE-CFMe-MCA study used for training and cross-validation.", SRC,
      attributes={"version": "Zeng et al. 2026 primary SE dataset (TCGE-CFMe-MCA)", "total": 339, "positives": 263, "negatives": 76,
                  "population": "263 cancers (AML 53, bladder 17, breast 20, colorectal 20, lung 70, pancreatic 65, renal 18) and 76 healthy controls",
                  "assay": "cfMeDIP-seq, single-end", "scope_note": COMMON_SCOPE,
                  "source_locator": "Extended Data Fig. 10d legend; Results P33; Methods P60"})
B.rec(D["se-validation"], "dataset", "Zeng et al. 2026 single-end 10% hold-out set (39 samples)",
      "Ten per cent of the single-end TCGE-CFMe-MCA samples held out from PCA, training and tuning.", SRC,
      attributes={"version": "Zeng et al. 2026 SE hold-out set", "total": 39, "positives": 30, "negatives": 9,
                  "population": "30 cancers (AML 5, bladder 2, breast 5, colorectal 3, lung 7, pancreatic 6, renal 2) and 9 healthy controls",
                  "assay": "cfMeDIP-seq, single-end",
                  "scope_note": COMMON_SCOPE + " A hold-out split of the same study as the SE training data, not an independent cohort.",
                  "source_locator": "Extended Data Fig. 10e legend; Methods P60"})

# ---------------------------------------------------------------- method and configurations
M = f"{P}-method-pca-classifier"
B.method(M, "Zeng et al. 2026 cfMeDIP-seq PCA classification workflow",
         ("Principal components of cfDNA methylation (cfMeDIP-seq DMR counts) and of fragmentomic features of the same reads "
          "(5' end motifs, DELFI-style fragment ratios, insert size, nucleosome peak distance), fed to the best of seven "
          "algorithms (LASSO, SVM, random forest, gradient boosting, XGBoost, LDA, KNN) chosen by repeated 10-fold "
          "cross-validation on Cohen's kappa and tuned by nested cross-validation."),
         SRC, ["supervised_machine_learning"], "Methods P59-P61; Extended Data Fig. 7a, 9b and 10c", reported="classification workflow")
FEATS = {  # sheet label: (key, inputs, method-type note)
    "Methylation": ("methylation", "PCs of cfMeDIP-seq methylation"),
    "End Motifs": ("end-motifs", "PCs of 5' 4-mer end-motif frequencies"),
    "Fragment Ratio": ("fragment-ratio", "PCs of genome-wide short-to-long fragment ratios in 5 Mb bins (DELFI-style)"),
    "Insert Size": ("insert-size", "PCs of insert-size (fragment length) distributions"),
    "Nucleosome Peak": ("nucleosome-peak", "PCs of nucleosome peak distances"),
    "Combined Motif + Methylation (1%)": ("motif-methylation-1pct", "5' end-motif and methylation PCs each contributing >1% of variance"),
    "Combined Ratios + Methylation (1%)": ("ratios-methylation-1pct", "Fragment-ratio and methylation PCs each contributing >1% of variance"),
    "Combined Motif + Methylation + Ratios (1%)": ("motif-methylation-ratios-1pct", "5' end-motif, fragment-ratio and methylation PCs each contributing >1% of variance"),
    "Combined All Features (1%)": ("all-features-1pct", "PCs of all five feature sets, each contributing >1% of variance"),
    "Combined All Features (5%)": ("all-features-5pct", "PCs of all five feature sets, each contributing >5% of variance"),
}
CFG = {}
for label, (key, inputs) in FEATS.items():
    CFG[label] = f"{P}-config-{key}"
    B.configuration(CFG[label], f"Zeng et al. 2026 classifier: {label}", M, SRC, label,
                    "Source Data Fig. 4 row labels; Results P29-P33; Methods P59", ["supervised_machine_learning"],
                    "Code and the uniformly processed data are described as a resource in the article; no locked model release is printed",
                    inputs + " from cfMeDIP-seq reads; algorithm chosen per feature set by nested cross-validation (not stated per row)",
                    version_note="No model release or commit is printed; the algorithm selected for each feature set is not named in the Source Data")

# ---------------------------------------------------------------- protocols
PR = {k: f"{P}-protocol-{k}" for k in ("pe-primary-cv", "pe-validation", "se-primary-cv", "se-validation")}
LIM = ["Developer study: the authors produced the cfMeDIP-seq cohorts and built and ran every classifier.",
       "Clinically diagnosed cancers, many metastatic or advanced, against healthy donors; not an intended-use screening population.",
       "Values are summaries over the 10 cross-validation fold models; the fold-level spread is reported, not a confidence interval over samples.",
       "Fragmentomic features are computed from cfMeDIP-enriched (methylated) fragments, not from whole-genome sequencing."]
SPREAD = ("Source Data columns are headed sd_sens99 and the sheets' text column prints 'Sensitivity=x ± y'; the Figure 4 legend "
          "says the error bars in panels b, d, f and h are s.e.")
B.rec(PR["pe-primary-cv"], "protocol", "Zeng et al. 2026 primary PE dataset: cancer vs healthy, nested cross-validation",
      "Ten feature sets classified cancer vs healthy on the primary paired-end dataset; mean over 10 outer folds.", SRC,
      [{"relation": "uses_data", "target_id": D["pe-primary"]}],
      {"protocol": ("Nested cross-validation on the 420-sample primary PE dataset (ten outer and ten inner folds for n > 250), "
                    "class balance by down-sampling; PCA and standardisation fitted within training folds. AUC and sensitivity at "
                    "99% specificity are summarised over the 10 outer-fold models."),
       "version": "Zeng et al. 2026, Fig. 4a-b and Source Data Fig. 4 sheets Fig.4a and Fig.4b; Methods P59-P61",
       "metric": "auroc", "metric_direction": "higher", "limitations": LIM,
       "source_locator": "Results P29; Fig. 4a-b legend; Methods P59-P62"})
B.rec(PR["pe-validation"], "protocol", "Zeng et al. 2026 independent PE validation dataset: cancer vs healthy",
      "Fold models from the primary PE dataset applied to an independent paired-end validation dataset; mean over 10 fold models.", SRC,
      [{"relation": "uses_data", "target_id": D["pe-validation"]}],
      {"protocol": ("Each of the 10 fold models trained on the primary PE dataset scores the independent PE validation samples, "
                    "which were excluded from PCA, training and tuning. LFS-previvor and LFS-survivor samples are scored post hoc "
                    "and counted as cancer for sensitivity summaries."),
       "version": "Zeng et al. 2026, Fig. 4c-d and Source Data Fig. 4 sheets Fig.4c and Fig.4d; Results P28 and P32",
       "metric": "auroc", "metric_direction": "higher",
       "limitations": LIM + ["The 17 healthy controls from the HCC study used a different laboratory protocol; the authors say this "
                             "lowered the AUC and sensitivity of every classifier that includes 5' end motifs.",
                             "LFS-previvor and LFS-survivor carriers without current cancer are labelled as cancer for sensitivity summaries.",
                             "Validation size is printed as 95 baseline samples in the Results and n = 140 in the Extended Data Fig. 9f legend."],
       "source_locator": "Results P28 and P32; Fig. 4c-d legend; Methods P60-P61"})
B.rec(PR["se-primary-cv"], "protocol", "Zeng et al. 2026 primary SE dataset: cancer vs healthy, nested cross-validation",
      "Methylation, 5' end-motif and combined classifiers on the single-end TCGE-CFMe-MCA dataset; mean over 10 outer folds.", SRC,
      [{"relation": "uses_data", "target_id": D["se-primary"]}],
      {"protocol": "As for the PE primary dataset, on the 339-sample single-end training set (10% held out beforehand).",
       "version": "Zeng et al. 2026, Fig. 4e-f and Source Data Fig. 4 sheets Fig.4e and Fig.4f; Results P33",
       "metric": "auroc", "metric_direction": "higher", "limitations": LIM,
       "source_locator": "Results P33; Fig. 4e-f legend; Methods P60"})
B.rec(PR["se-validation"], "protocol", "Zeng et al. 2026 SE 10% hold-out set: cancer vs healthy",
      "Fold models from the SE training set applied to the 39-sample hold-out set of the same study.", SRC,
      [{"relation": "uses_data", "target_id": D["se-validation"]}],
      {"protocol": "Each of the 10 SE fold models scores the 39-sample hold-out set, which was excluded from PCA, training and tuning.",
       "version": "Zeng et al. 2026, Fig. 4g-h and Source Data Fig. 4 sheets Fig.4g and Fig.4h; Results P33",
       "metric": "auroc", "metric_direction": "higher",
       "limitations": LIM + ["A 10% hold-out of the same study (39 samples, 9 healthy), not an independent cohort."],
       "source_locator": "Results P33; Fig. 4g-h legend; Extended Data Fig. 10e legend; Methods P60"})

# ---------------------------------------------------------------- Source Data Fig. 4
cells = rawxlsx.read(SD)
expect(sorted(cells), ["Fig.4a", "Fig.4b", "Fig.4c", "Fig.4d", "Fig.4e", "Fig.4f", "Fig.4g", "Fig.4h"], "Source Data sheets")
SHEETS = {  # sheet: (protocol, kind, header, expected labels)
    "Fig.4a": ("pe-primary-cv", "auc", ["Metric", "mean_auc", "sd_auc", "min_auc", "max_auc"], list(FEATS)),
    "Fig.4b": ("pe-primary-cv", "sens", ["Metric", "mean_sens99", "sd_sens99", "sens_text"], list(FEATS)),
    "Fig.4c": ("pe-validation", "auc", ["Metric", "mean_auc", "sd_auc", "min_auc", "max_auc", "y_values"], list(FEATS)),
    "Fig.4d": ("pe-validation", "sens", ["Metric", "mean_sens99", "sd_sens99"], list(FEATS)),
    "Fig.4e": ("se-primary-cv", "auc", ["Metric", "mean_auc", "sd_auc"], ["Combined Motif + Methylation (1%)", "End Motifs", "Methylation"]),
    "Fig.4f": ("se-primary-cv", "sens", ["Metric", "mean_sens99", "sd_sens99", "sens_text"], ["Combined Motif + Methylation (1%)", "End Motifs", "Methylation"]),
    "Fig.4g": ("se-validation", "auc", ["Metric", "mean_auc", "sd_auc"], ["Combined Motif + Methylation (1%)", "End Motifs", "Methylation"]),
    "Fig.4h": ("se-validation", "sens", ["Metric", "mean_sens99", "sd_sens99", "sens_text"], ["Combined Motif + Methylation (1%)", "End Motifs", "Methylation"]),
}
COLS = "ABCDEFG"
POP = {"pe-primary-cv": ("Zeng et al. 2026 primary PE dataset", "356 cancers and 64 healthy controls", "Nested cross-validation, 10 outer folds"),
       "pe-validation": ("Zeng et al. 2026 PE validation dataset", "Independent PE validation samples (95 or 140; see dataset)", "Independent validation of the 10 fold models"),
       "se-primary-cv": ("Zeng et al. 2026 primary SE dataset", "263 cancers and 76 healthy controls", "Nested cross-validation, 10 outer folds"),
       "se-validation": ("Zeng et al. 2026 SE hold-out set", "30 cancers and 9 healthy controls", "10% hold-out of the same study")}
QUAL = {"pe-primary-cv": "cancer vs healthy, primary PE dataset, mean over 10 fold models",
        "pe-validation": "cancer vs healthy, independent PE validation dataset, mean over 10 fold models",
        "se-primary-cv": "cancer vs healthy, primary SE dataset, mean over 10 fold models",
        "se-validation": "cancer vs healthy, SE 10% hold-out set, mean over 10 fold models"}
Z1_WARNING = ("Source Data Fig. 4 sheet Fig.4c cell B6 prints a mean AUC of 0.69415032679738597 for the methylation-only classifier "
              "in the PE validation dataset; Results P32 of the article prints 0.674 for the same quantity. The other validation AUCs "
              "quoted in the text (0.954, 0.848) match the sheet. Which figure is right cannot be told from the source. The value is "
              "kept as printed and does not support comparison (independent review 2026-10-12).")
REV = B.review(["deterministic-table-parse"], SD, SD_URL,
               "Extracted by deterministic parse of the pinned XLSX cell XML (extract/rawxlsx.py) with sheet names, headers, row "
               "labels and row counts asserted. General-format cells; printed_value is the shortest round-trip decimal of the stored value.")
PANELS = {"pe-primary-cv": "ab", "pe-validation": "cd", "se-primary-cv": "ef", "se-validation": "gh"}
EVS = {}
n_results = 0
for sheet, (pk, kind, header, labels) in SHEETS.items():
    c = cells[sheet]
    expect([c.get(f"{col}1") for col in COLS[:len(header)]], header, f"{sheet} header")
    expect(c.get(f"{COLS[len(header)]}1"), None, f"{sheet} header width")
    expect(sorted(c.get(f"A{r}") for r in range(2, len(labels) + 2)), sorted(labels), f"{sheet} row labels")
    expect(c.get(f"A{len(labels) + 2}"), None, f"{sheet} row count")
    for r in range(2, len(labels) + 2):
        label = c[f"A{r}"]
        key = FEATS[label][0]
        ev = EVS.get((pk, label))
        if not ev:
            ev = EVS[(pk, label)] = f"{P}-eval-{pk}-{key}"
            dv, pop, split = POP[pk]
            lim = None
            if pk == "pe-validation" and "Motif" in label:
                lim = ["Includes 5' end motifs, whose baseline differs in the HCC-study healthy controls (Results P32)."]
            B.evaluation(ev, f"{label} on {pk.replace('-', ' ')} (Zeng et al. 2026)", CFG[label], PR[pk], D[pk.rsplit('-cv', 1)[0]], SRC,
                         "author_reported",
                         {"dataset_version": dv, "split": split, "population": pop, "inputs": FEATS[label][1],
                          "adaptation": "Trained on the primary dataset of the same sequencing mode",
                          "metric_implementation": None, "aggregation": "Mean over 10 cross-validation fold models", "budget": None},
                         f"Source Data Fig. 4, sheets Fig.4{PANELS[pk][0]} and Fig.4{PANELS[pk][1]}, row '{label}'",
                         limitations=lim,
                         missing={"comparison.metric_implementation": {"reason": "unreported", "note": "ROC and threshold code not described"},
                                  "comparison.budget": {"reason": "inapplicable"}})
        mean = c[f"B{r}"]
        loc = f"Source Data Fig. 4, sheet {sheet}, row {r} '{label}', column B '{header[1]}'"
        if kind == "auc":
            sd = c[f"C{r}"]
            unc = {"type": "standard_deviation", "value": shortest(sd), "printed": f"sd_auc {shortest(sd)}",
                   "scope": "across the 10 cross-validation fold models", "source_column": "C sd_auc",
                   "note": "Figure 4 legend: error bars in a, c, e and g are ±1 s.d. across cross-validation folds (n = 10)."}
            extra = {"raw_xml_value": mean}
            more = [f"{col}{r} {header[i]} {shortest(c[f'{col}{r}'])}" for i, col in enumerate(COLS[:len(header)]) if i >= 3 and header[i] != "y_values"]
            if "y_values" in header:
                more.append(f"F{r} y_values {shortest(c[f'F{r}'])} (plot position, not a result)")
            if more:
                extra["source_cells"] = more
            if Decimal(mean) < Decimal("0.5"):
                extra["source_anomaly"] = ("Mean AUC below 0.5, below chance for a cancer vs healthy classifier. The article attributes lower "
                                           "AUCs of motif-containing classifiers in this dataset to the HCC-study healthy controls' different "
                                           "laboratory protocol (Results P32).")
            if sheet == "Fig.4c" and label == "Methylation":
                extra["source_discrepancy"] = "Results P32 prints 0.674 for this value; the sheet prints 0.69415032679738597. See source_warnings."  # review Z1
                extra["source_warnings"] = [Z1_WARNING]
            B.result(f"{ev.replace('-eval-', '-result-')}-auroc", ev, SRC, loc, shortest(mean), "auroc", QUAL[pk], "unitless", REV,
                     uncertainty=unc, extra=extra)
        else:
            sd = c[f"C{r}"]
            unc = {"type": "unresolved_spread", "value": shortest(sd), "printed": f"sd_sens99 {shortest(sd)}",
                   "scope": "across the 10 cross-validation fold models", "source_column": "C sd_sens99",
                   "note": SPREAD + " Methods P61 says error bars denote across-fold s.d."}  # review Z4
            extra = {"raw_xml_value": mean}
            if "sens_text" in header:
                txt = c[f"D{r}"]
                expect(txt.startswith(f"{label}: Sensitivity="), True, f"{sheet} row {r} text label")
                extra["printed_source_cell"] = f"D{r} sens_text: {txt}"
            B.result(f"{ev.replace('-eval-', '-result-')}-sensitivity-99spec", ev, SRC, loc, shortest(mean),
                     "sensitivity-at-99-percent-specificity", QUAL[pk], "fraction", REV, uncertainty=unc, extra=extra)
        n_results += 1
expect(n_results, 52, "result count")
REC = {r["id"]: r for r in B.records}
REC[f"{P}-result-pe-validation-methylation-auroc"]["status"] = "disputed"  # review Z1

# ---------------------------------------------------------------- claims
CREV = B.review(["transcription"], XML, XML_URL, "Hand transcription from the article text, checked by string match in extract/extract_zeng2026.py.")
B.claim(f"{P}-claim-algorithm-selection", M, "classifier_selection",
        ("Seven algorithms were benchmarked per feature set by repeated 10-fold cross-validation on Cohen's kappa with class "
         "balance by down-sampling; the best per feature set was tuned by nested cross-validation. The selected algorithm per "
         "feature set is shown only in Extended Data Fig. 9b and 10c, not in the Source Data rows extracted here."),
        [S_ART], "Methods P60; Extended Data Fig. 9b and 10c legends", CREV)
B.claim(f"{P}-claim-validation-text-values", PR["pe-validation"], "text_values",
        ("Results P32: combined fragment ratio and methylation mAUC 0.954 in validation against 0.961 in the primary PE dataset; "
         "fragment ratio alone 0.848 and methylation alone 0.674; at 99% specificity sensitivity 76.6 ± 4.0% for the combined "
         "model and 63.3 ± 1.9% for methylation; at 90% specificity 84.3 ± 5.7% and 65.2 ± 2.0%."),
        [S_ART], "Results P32", CREV)

# ---------------------------------------------------------------- judgements
J = "use-case-mapping-ctdna-lit-20261011-zeng2026"
CONS = ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
        "Do not combine this mapping's evaluations with any other protocol's results; assays, cohorts and validation designs differ.",
        "Fold-model means are not sample-level confidence intervals; spreads are across 10 fold models."]
REASON = "Add the same-sample cfMeDIP-seq methylation and fragmentomic classifier comparison of Zeng et al. 2026 (Nature Cancer), retrieved 2026-10-11."
CITES = [(S_ART, "Results P28-P33; Fig. 4 legend; Methods P59-P62"), (S_SD, "Sheets Fig.4a-Fig.4h")]
G, T = "zeng2026-cfmedip-feature-sets", "cfMeDIP-seq methylation and fragmentomic feature sets on the same samples (Zeng et al. 2026)"
JLIM = LIM + ["Spread of sensitivity values: " + SPREAD]
# Review Z3: few healthy controls set the 99% specificity threshold.
Z3 = {"pe-primary-cv": ("Sensitivity at 99% specificity is read within each outer fold, which holds six or seven of the 64 healthy donors, "
                        "so a 99% specificity threshold allows no false positive among them (counts from the source; the resolution is Rewire arithmetic)."),
      "pe-validation": ("The validation set has 17 healthy controls (Results P28 and P32), so a 99% specificity threshold allows no false "
                        "positive among them (counts from the source; the resolution is Rewire arithmetic)."),
      "se-primary-cv": ("Sensitivity at 99% specificity is read within each outer fold, which holds seven or eight of the 76 healthy donors, "
                        "so a 99% specificity threshold allows no false positive among them (counts from the source; the resolution is Rewire arithmetic)."),
      "se-validation": ("The hold-out set has 9 healthy controls, so a 99% specificity threshold allows no false positive among them "
                        "(counts from the source; the resolution is Rewire arithmetic).")}
# Review Z2: motif-containing classifiers are excluded from both PE validation judgements.
Z2_REASON = ("Includes 5' end motifs; the authors attribute motif-containing classifiers' validation scores to a laboratory-protocol "
             "difference in the HCC-study healthy controls (Results P32), so the values reflect that batch effect, not the classifier.")
Z2_EXCLUDED = [f"{P}-eval-pe-validation-{k}" for k in ("end-motifs", "motif-methylation-1pct", "motif-methylation-ratios-1pct",
                                                        "all-features-1pct", "all-features-5pct")]
links = []
STRATA = [("pe-primary-cv", "Primary PE dataset, cross-validation", 1), ("pe-validation", "Independent PE validation dataset", 2),
          ("se-primary-cv", "Primary SE dataset, cross-validation", 3), ("se-validation", "SE 10% hold-out set", 4)]
for pk, label, order in STRATA:
    extra_lim = B.records[[r["id"] for r in B.records].index(PR[pk])]["attributes"]["limitations"][len(LIM):]
    jid = f"{J}-meth-{pk}"
    B.judgement(jid, UC_METH, Q_METH, PR[pk], "proxy",
                f"Cancer vs healthy ROC-AUC and sensitivity at 99% specificity (means over 10 fold models) for cfMeDIP-seq methylation, fragmentomic feature sets of the same reads and their combinations: {label.lower()}",
                ("A same-sample comparison of a measured methylation workflow (cfMeDIP-seq) with fragmentomic features and their "
                 "combination, at a declared 99% specificity. Proxy rather than direct: the cohorts are clinically diagnosed and "
                 "largely advanced cancers against healthy donors, the specificity is a fold-model threshold rather than a locked "
                 "screening threshold, and the developer ran every arm."),
                CONS, JLIM + extra_lim + [Z3[pk]], CITES, REASON, G, T, "auroc", label, order)
    links.append({"use_case": UC_METH, "relation": "assessed_by", "target_id": PR[pk], "judgement_claim": jid})
for pk, label, order in STRATA[:2]:
    extra_lim = B.records[[r["id"] for r in B.records].index(PR[pk])]["attributes"]["limitations"][len(LIM):]
    jid = f"{J}-frag-{pk}"
    B.judgement(jid, UC_FRAG, Q_FRAG, PR[pk], "proxy",
                f"Cancer vs healthy ROC-AUC and sensitivity at 99% specificity (means over 10 fold models) for 5' end-motif, fragment ratio, insert size and nucleosome peak feature sets from cfMeDIP-seq reads, alone and combined with methylation: {label.lower()}",
                ("Compares several fragmentomic feature sets on the same plasma samples at a fixed 99% specificity, with an independent "
                 "validation dataset. Proxy: the fragments are cfMeDIP-enriched (methylated) reads rather than whole-genome "
                 "sequencing, no tumour-fraction stratum is reported, and the developer ran every arm."),
                CONS, JLIM + extra_lim + ["No tumour-fraction stratification is reported for these classifiers.", Z3[pk]], CITES, REASON,
                G, T, "auroc", label, order)
    links.append({"use_case": UC_FRAG, "relation": "assessed_by", "target_id": PR[pk], "judgement_claim": jid})
for pk in PR:
    a = REC[PR[pk]]["attributes"]
    a["limitations"] = a["limitations"] + [Z3[pk]]  # review Z3 (a new list: protocols share LIM)
REC = {r["id"]: r for r in B.records}
EVALS = {}
for r in B.records:
    if r["kind"] == "evaluation":
        EVALS.setdefault(r["attributes"]["protocol"], []).append(r["id"])
REVIEWED = {}
for kind, pk in [("meth", pk) for pk in PR] + [("frag", "pe-primary-cv"), ("frag", "pe-validation")]:
    jid = f"{J}-{kind}-{pk}"
    if pk == "pe-validation":
        REC[jid]["attributes"]["excluded_evaluations"] = [{"id": e, "reason": Z2_REASON} for e in Z2_EXCLUDED]  # review Z2
    REVIEWED[jid] = [e for e in EVALS[PR[pk]] if e not in Z2_EXCLUDED]

B.finalize("Re-downloaded the pinned artifacts and matched their SHA-256; compared every value, s.d. column, sheet, row label and "
           "header with a separate stdlib OOXML reader written for this review (the extractor's script was not run) and read the "
           "sheet dump in full; cross-checked the values quoted in Results P29, P32 and P33 against the sheet.",
           ["source-hash-verification", "deterministic-table-parse", "independent-cell-check"], REVIEWED,
           notes={f"{P}-result-pe-validation-methylation-auroc": "The value conflicts with another part of the same source; see source_warnings."})
B.write(BATCH, links)
