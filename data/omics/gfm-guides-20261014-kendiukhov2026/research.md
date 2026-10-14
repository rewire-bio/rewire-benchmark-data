# Research notes

Why: the genomic foundation model guides cite Kendiukhov 2026 (BMC Genomics 27:634) for the finding that attention-derived edge scores from single-cell foundation models do not beat simple gene-level baselines at predicting which genes respond to a CRISPR perturbation. The store had no source or result records for it (issue rewire-benchmark-data#129).

What the paper evaluates: two objectives. Objective A is recovery of curated regulatory edges (TRRUST, DoRothEA, STRING), where the author's own method CSSI is introduced. Objective B is perturbation-target prediction: for each CRISPRi or CRISPRa perturbation, rank all other genes by an edge score to the perturbed gene and compute AUROC for the differentially expressed targets. Edge scores are Geneformer V2-316M attention (and scGPT in some analyses) and absolute Spearman correlation; gene-level baselines are target-gene variance, mean expression and dropout rate, and a logistic regression on all three. This batch covers Objective B, which is what the guides cite.

Decisions:

- Scope: the Objective B values printed in the Results text for K562 CRISPRi, K562 CRISPRa and RPE1 CRISPRi, as absolute AUROC values. 20 results.
- Origin: Geneformer attention, Spearman correlation and the single-statistic baselines are independent_paper (the author developed none of them). The gene-level logistic regression is a predictor the author built for this paper, so it is author_reported. CSSI, the author's own method, has no Objective B values printed and is not recorded.
- Reused records: catalog-model-geneformer (family) for the four attention configurations. No record exists for the Geneformer V2-316M checkpoint; the checkpoint is named in the configuration attributes rather than creating a model record. No scGPT Objective B value is printed in the main text, so no scGPT configuration was created.
- Existing Replogle and Adamson dataset records describe the GEARS-processed essential-gene screens used by other papers. This paper uses the genome-scale K562 screen (2,024 perturbed genes) and its own preprocessing, so new dataset_subset records are used, one per printed perturbation count.
- Metric auroc, unit unitless, direction higher. The qualifier separates per-perturbation AUROC, pooled cross-validated AUROC over perturbation-gene pairs, and propensity-matched AUROC.
- Aggregation over perturbations is not stated (the text says 'per-perturbation AUROC'; the summary statistic is not named), so the evaluations say so instead of assuming a mean.
- No use case covers perturbation-target prediction from attention in this pass, so no relevance judgement is proposed.

## Extraction note for the reviewer

Method: hand transcription from the article text, with extract/extract_kendiukhov2026.py asserting that each quoted fragment, containing the printed value, occurs on the stated PDF page. Extraction only; nothing here has been reviewed.

Tables: Table 1 (model coverage) and Table 2 (multiple-testing families) print no performance values and were not extracted as results. Supplementary tables were screened, not extracted.

Values extracted (all AUROC):

| Setting | n | Configuration | Value | Page |
| --- | --- | --- | --- | --- |
| K562 CRISPRi, primary parameterisation | 151 | Spearman correlation | 0.696 | 7 |
| K562 CRISPRi | 151 | Target-gene variance | 0.881 | 7 |
| K562 CRISPRi | 280 | Geneformer attention L13 | 0.704 | 7 |
| K562 CRISPRi | 280 | Spearman correlation | 0.703 | 7 |
| K562 CRISPRi, nested CV layer choice | 280 | Geneformer attention L15 | 0.743 | 7 |
| K562 CRISPRi, logistic regression | 280 x 1,999 pairs | Gene-level features | 0.895 [bootstrap 95% CI 0.884, 0.905] | 8 |
| K562 CRISPRi, propensity-matched | 59,153 pairs | Geneformer attention, layer not stated | 0.609 | 9 |
| K562 CRISPRa | 77 | Geneformer attention, layer not stated | 0.55 | 10 |
| K562 CRISPRa | 77 | Spearman correlation | 0.65 | 10 |
| RPE1 CRISPRi | 1,251 | Geneformer attention L15 | 0.748 | 10 |
| RPE1 CRISPRi | 1,251 | Spearman correlation | 0.658 | 10 |
| RPE1 CRISPRi | 1,251 | Geneformer attention L6 | 0.776 | 10 |
| RPE1 CRISPRi, confound battery | 1,167 | Variance; mean expression; dropout | 0.866; 0.851; 0.797 | 10 |
| RPE1 CRISPRi, confound battery | 1,167 | Geneformer attention, layer not stated; Spearman correlation | 0.747; 0.658 | 10 |
| RPE1 CRISPRi, logistic regression | 1,167 | Gene-level features | 0.942 | 10 |
| RPE1 CRISPRi, propensity-matched | not printed | Geneformer attention, layer not stated; Spearman correlation | 0.568; 0.561 | 10 |

Record counts: 1 source, 1 benchmark, 5 protocols, 7 dataset subsets, 5 methods, 9 configurations, 20 evaluations, 20 results, 1 claim (69 records).

Gaps:

1. Incremental-value differences not recorded. No metric concept holds a difference in AUROC, and these are the paper's central numbers: K562 gene+attention minus gene-only -0.0004 [-0.001, 0.000], gene+correlation -0.002 [-0.005, 0.000] (page 8); propensity-matched -0.000 [-0.000, +0.000] (page 9); RPE1 +0.0001 [+0.0001, +0.0001] and -0.0006 (page 10); attention minus correlation +0.060 [+0.040, +0.080] (K562), +0.090 [+0.079, +0.101] (RPE1), +0.168 (RPE1 restricted to 2,000 HVGs); largest delta AUPRC +0.009 (page 8); synthetic positive control +0.518, +0.452, +0.492 with CIs (page 11). Concept needed: `auroc-difference` (difference between the AUROC of two predictors on the same data, with the order of subtraction in metric_qualifier; direction depends on that order; unitless). A matching `auprc-difference` would cover the +0.009 value.
2. K562 mean-expression and dropout AUROC are printed only as a range with variance ('0.81-0.88', page 7); individual values are in Fig. 3 only. Not recorded.
3. Absolute AUROC of the gene+attention and gene+correlation logistic regressions (Fig. 4A) and the per-layer profile (printed as ranges 0.47-0.64, 0.60-0.71, 0.69-0.74; Fig. S5) are not printed as values.
4. The 27-condition sensitivity range for correlation edges (0.62-0.76) is a range, not recorded.
5. Not in scope for this batch and not extracted: causal ablation values (pages 9-10, Geneformer head masking 0.704 to 0.697, MLP ablation, scGPT edge-level and forward-pass ablation), all Objective A values (CSSI 1.85x, L13 TRRUST AUROC 0.694, residualisation 0.66 to 0.54, per-TF AUROC, layer-by-database AUROC), Supplementary Tables S1-S18, and the T cell and iPSC neuron comparisons (n = 7, effect sizes and p-values only).
6. Uncertainty is printed only for the K562 gene-level logistic regression; other values have none.

Needs reviewer judgement:

- CRISPRa dataset identity: the K562 CRISPRa analysis cites reference 25, Adamson et al. 2016, which is a CRISPRi screen (evidence concern on the source).
- Two K562 perturbation sets (151 and 280) and two RPE1 sets (1,251 and 1,167) are reported without saying how they relate; correlation is 0.696 on one K562 set and 0.703 on the other (evidence concern on the source).
- Attention values with no layer named (CRISPRa 0.55, K562 propensity-matched 0.609, RPE1 battery 0.747, RPE1 propensity-matched 0.568) are assigned to a 'layer not stated' configuration rather than guessed.
- L15 on K562 was chosen by nested cross-validation over 18 layers; L13 was pre-specified (recorded as a claim). The L15 and L6 values are layer-selection results and should not be compared with L13 as if pre-specified.
- Origin of the gene-level logistic regression (author_reported) versus the other baselines (independent_paper).
