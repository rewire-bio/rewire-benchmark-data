# Research notes

Batch for rewire-benchmark-data issue #163: the AUROC differences in Kendiukhov 2026 (BMC Genomics 27:634), which are the paper's central Objective B numbers. The first extraction, `gfm-guides-20261014-kendiukhov2026` (reviewed, in the store), recorded the absolute AUROCs and listed these differences as a gap for want of a metric concept. This PR adds `auroc-difference` to `data/vocab/metric.ttl`: the AUROC of the evaluated system minus that of a stated reference system on the same items, so `higher` means the evaluated system ranks better.

## Decisions

- Incremental-value tests (gene-level features plus an edge score, minus gene-level features alone): the evaluated systems are two new configurations of the existing method `gfm-guides-20261014-kendiukhov2026-method-gene-level-logistic-regression`: `...-config-gene-level-lr-plus-attention` (with a `uses_model` link to `catalog-model-geneformer`) and `...-config-gene-level-lr-plus-correlation`. The reference (gene-level features only) is named in `metric_qualifier`. Origin author_reported, as for the existing gene-level logistic regression evaluations.
- Attention minus correlation (the "per-perturbation attention advantage"): the evaluated system is the existing `...-config-geneformer-v2-316m-attention-layer-unstated`, because the sentence does not name the layer. Origin independent_paper.
- RPE1 restricted to the top 2,000 HVGs (+0.168, n = 418) needs a new protocol (`...-protocol-pf-rpe1-crispri-hvg2000`) and a new dataset subset (`...-data-rpe1-crispri-418-hvg2000`), because the gene universe differs from the existing RPE1 protocol (3,309 genes).
- The K562 propensity-matched incremental test uses the existing incremental-value protocol and the existing matched-pairs subset. Its cross-validation split is not restated, so the evaluation's `comparison.split` is null with a missing reason.
- Intervals: printed bounds go in `uncertainty`, with the printed text. The Methods default ("Bootstrap confidence intervals use 200 iterations with perturbation-level resampling unless otherwise noted") is quoted in the note; `resamples` is not set, because Fig. 4B's caption gives a bootstrap distribution of n = 100 for the K562 values.
- `printed_value` keeps the source's sign characters (U+2212 minus, explicit plus); `numeric_value` is ASCII. "−0.000" is kept as printed, with numeric_value "-0.000".
- Records are `needs_review`. No review.json yet.

## Record counts

- configuration: 2
- protocol: 1
- dataset_subset: 1
- evaluation: 8
- result: 8

| Value | Interval | Comparison | Data | Page |
| --- | --- | --- | --- | --- |
| −0.0004 | [−0.001, 0.000] | gene + attention minus gene only | K562 CRISPRi, 280 | 8 |
| −0.002 | [−0.005, 0.000] | gene + correlation minus gene only | K562 CRISPRi, 280 | 8 |
| −0.000 | 95% CI [−0.000, +0.000] | gene + attention minus gene only | K562 propensity-matched pairs | 9 |
| +0.0001 | 95% CI [+0.0001, +0.0001] | gene + attention minus gene only | RPE1 CRISPRi, 1,167 | 10 |
| −0.0006 | none printed | gene + correlation minus gene only | RPE1 CRISPRi, 1,167 | 10 |
| +0.060 | [+0.040, +0.080] | attention minus correlation | K562 CRISPRi, 280 | 10 |
| +0.090 | [+0.079, +0.101] | attention minus correlation | RPE1 CRISPRi, 1,251 | 10 |
| +0.168 | none printed | attention minus correlation | RPE1, top 2,000 HVGs, 418 | 10 |

## Extraction note for the reviewer

Method: hand transcription from the article text. `extract/extract_delta.py` asserts the hash of the archived PDF (`data/omics/gfm-guides-20261014-kendiukhov2026/artifacts/kendiukhov2026-bmc-genomics-article.pdf.gz`, raw SHA-256 `4c1699cb...08fe`), that each quoted fragment containing the value occurs on the stated page of the pdftotext reading-order output, that the Methods sentence defining ΔAUROC is on page 16, and that every reused record exists. Run from the repository root:

```sh
gunzip -c data/omics/gfm-guides-20261014-kendiukhov2026/artifacts/kendiukhov2026-bmc-genomics-article.pdf.gz > <scratch>/k.pdf
python3 -I data/omics/gfm-guides-20261014-kendiukhov2026-delta/extract/extract_delta.py <scratch>/k.pdf . data/omics/gfm-guides-20261014-kendiukhov2026-delta
```

Gaps (not recorded):

- Synthetic positive control, ΔAUROC +0.518 [+0.496, +0.544], +0.452 [+0.425, +0.475], +0.492 [+0.463, +0.530] (page 11). Table 1's footnote says the synthetic control "evaluates the pipeline, not a specific model", and the main text does not say which edge score the pipeline adds; recording it would mean inventing the system. Supplementary Note 21 (Additional file 1, screened but not pinned) may say.
- Shuffled-null ΔAUROC "-0.04 to +0.06" (page 11): a range, not a value.
- RPE1 attention advantage by DE threshold, "LFC > 0.5: +0.090; LFC > 0.25: +0.049" (page 10). The +0.090 at LFC > 0.5 matches the bootstrap value recorded above, which suggests the recorded RPE1 value is at LFC > 0.5; the +0.049 at LFC > 0.25 would need a separate protocol. Not recorded.
- Largest ΔAUPRC +0.009 (page 8): a maximum over unstated combinations, and no AUPRC-difference concept was added.
- scGPT ablation deltas (Δtop-20, Δrandom-20, pages 9-10) and the TRRUST ablation ΔAUROC range (-0.002 to -0.003): Objective A or ablation results, outside this batch's scope.

Needs reviewer judgement:

- K562 attention advantage +0.060 versus the L13 AUROCs 0.704 and 0.703 printed for the same 280 perturbations (difference 0.001). The advantage is a per-perturbation statistic whose summary (mean or median) is not named, and the layer is not named, so the two need not agree; the value is recorded against the layer-not-stated configuration.
- Page 10 also prints "the RPE1 attention advantage over correlation (diff = +0.089, p < 10−10)" after the confound battery. It matches the battery AUROCs (0.747 - 0.658 on 1,167 perturbations) but the sentence does not say which perturbation set it uses, so it is not recorded.
- The existing RPE1 1,251 evaluations say the LFC threshold for RPE1 values is not restated. The +0.090 sentence on page 10 places it at LFC > 0.5; the reviewer may want to update that evaluation note.
- The +0.0001 [+0.0001, +0.0001] interval has zero width at the printed precision; kept as printed.
