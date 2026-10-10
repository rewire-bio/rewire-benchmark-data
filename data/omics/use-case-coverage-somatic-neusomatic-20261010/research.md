# Research: NeuSomatic SEQC2 follow-up, tumour DNA somatic variant detection, 2026-10-10

Use case: `use-case-tumour-dna-somatic-variant-detection` ("Which calling or rescoring workflow reliably detects tumour SNVs and small indels under the available sequencing and normal-sample regime?"). This follow-up closes the evidence gap recorded by the 2026-10-09 pass: the SEQC2 HCC1395 whole-genome tables of Sahraeian et al. 2022 were not extracted because they are printed only in a PDF with rotated headers.

Bounds: 1 query (title lookup), 1 paper, 2 source records. Ledger ID `search-use-case-tumour-somatic-genomics-neusomatic-q1`.

## What was taken

| Table | Content | Results |
| --- | --- | --- |
| S2 | 21 WGS replicate pairs by sequencing site and platform, plus average | 704 |
| S3 | Tumour purity 5-100% at 10x-300x with a pure normal, and 10-100% at 80x with a 95% pure normal, plus average | 1,536 |
| S4 | TruSeq-Nano and Nextera Flex libraries from 1, 10 and 100 ng DNA, plus average | 224 |

Every cell of each table, SNV and indel sections. Columns: VarDict, SomaticSniper, MuSE, DRAGEN, Octopus-RF, Octopus-hard, MuTect2, Lancet, Strelka2, and NeuSomatic in standalone (NeuSomatic-S) and ensemble mode with four models each (DREAM3, SEQC-WGS-Spike, SEQC-WGS-GT-50, SEQC-WGS-GT50-SpikeWGS10). LoFreq and TNscope are not in these tables. Tables S5-S8 (WES, AmpliSeq, FFPE) fall under the use case's exclusions; S9 and S10 were not taken.

## Modelling choices

- Six protocols (three tables by SNV and indel), one judgement each, in three comparison groups with SNV and indel strata. All `direct`: paired tumour-normal WGS with a consortium truth set, the regime the question asks about.
- One evaluation per configuration and protocol; one result per printed row, with the tumour and normal labels in `metric_qualifier`. Average rows are kept as printed, with a `scope_note`.
- 17 configurations, one per column, with versions from Methods. NeuSomatic configurations record the model and its training data (`checkpoint`, `training_overlap`, from Table S1 and Methods). Ensemble configurations link `uses_model` to the five callers whose calls they take as input.
- Origins: NeuSomatic and NeuSomatic-S rows `author_reported`. Octopus-RF also `author_reported`, because Results say the authors trained its random forest on their SEQC2 data. The other eight callers `independent_paper`: no author developed them.
- New method: Octopus. All other methods are reused.

## Leakage

All tables score only the 50% of the high-confidence genome held out from SEQC-WGS-GT-50 training, so no truth label used in training is scored. Even so, every SEQC2-trained model is scored on the cell line and truth set it was built from. In Table S2 the training replicates are also among the scored pairs, and the paper does not say which ones. Under the use case's rule for models built from the test cell line, the 42 evaluations of SEQC2-trained models (NeuSomatic and NeuSomatic-S Spike, GT-50 and GT50-SpikeWGS10, and Octopus-RF, on all six protocols) are flagged with `evidence_overlap` and listed in `coverage.json` for exclusion. `excluded_evaluations` is not set. The DREAM3 models were trained on simulated DREAM data and are kept.

## Things a reviewer should judge

1. Whether Octopus-RF is SEQC2-trained (Results) or Octopus's own pretrained forest (Methods).
2. Whether the S3 and S4 rows of SEQC2-trained models should be excluded under the cell-line rule, given that their region and libraries are held out.
3. The six-centre prose against seven site codes in the S2 row labels.
4. Reuse of `cnv-20261009-method-dragen`, whose description names CNV callers.

## Coverage

Not covered: precision and recall (figures only), VAF bins, difficult regions, the non-SEQC2 synthetic samples (Additional file 1), and the SEQC2 consortium's own WGS comparison (Xiao et al. 2021).
