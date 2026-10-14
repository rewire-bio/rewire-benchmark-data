# Research notes

Batch for rewire-benchmark-data issue #163: the AvgBIO and average batch score cells of Kedzierska et al. 2025 (Genome Biology 26:101), Additional file 1. The first extraction, `gfm-guides-20261014-kedzierska2025` (reviewed, in the store), skipped these 176 whole-dataset cells because no metric concept fitted. This PR adds the concepts `avg-bio` and `average-batch-score` to `data/vocab/metric.ttl`.

## Decisions

- Metric definitions are from the article: AvgBIO is "the arithmetic mean of three individual metrics: ASW, Normalized Mutual Information (NMI), and Adjusted Rand Index (ARI)" (Methods 'Biological preservation scores', page 9); the Average Batch Score "is computed as the arithmetic mean between the PCR and batch integration scores" (Methods 'Batch mixing scores', page 10).
- Every result links to an evaluation already in the store (`gfm-guides-20261014-kedzierska2025-eval-{emb|umap}-<dataset>-<representation>`); the script asserts each one exists. No new evaluation, configuration, protocol or dataset records.
- Result IDs follow the first batch's pattern (`...-result-<emb|umap>-<dataset>-<representation>-avg-bio` and `...-average-batch`).
- The column reading is the reviewed one: the single-value column per model is the whole-dataset score; the bracketed subsample column is not extracted.
- Records are `needs_review`. No review.json yet.

## Record counts

- result: 176 (AvgBIO: 6 dataset rows x 8 representations x 2 sheets = 96; average batch: 5 x 8 x 2 = 80)

## Extraction note for the reviewer

Method: deterministic parse of the pinned workbook (`data/omics/gfm-guides-20261014-kedzierska2025/artifacts/kedzierska2025-additional-file-1.xlsx.gz`, raw SHA-256 `7adee121...3b5e`) with `extract/extract_avg.py` and the stdlib OOXML reader copied from the first batch. Run:

```sh
gunzip -c data/omics/gfm-guides-20261014-kedzierska2025/artifacts/kedzierska2025-additional-file-1.xlsx.gz > <scratch>/af1.xlsx
python3 -I data/omics/gfm-guides-20261014-kedzierska2025-avg/extract/extract_avg.py <scratch>/af1.xlsx . data/omics/gfm-guides-20261014-kedzierska2025-avg
```

The script asserts the workbook hash, both sheet titles, the model headers C2:Q2, all seven metric block labels in column A and the dataset labels in column B, then reads blocks 'AvgBIO' (rows 21-26) and 'Average batch' (rows 37-41) of TableS6 (full dimensions) and TableS7 (UMAP).

Consistency check (reported, not asserted): each printed AvgBIO is within 0.0067 of the mean of the ASW, NMI and ARI cells in the same column and row, and each average batch value within 0.0050 of the mean of batch integration and PCR. The component cells are stored at two or three decimals, so these differences are what rounding produces; the reviewer may want to confirm the largest (TableS6 E21, AvgBIO, Harmony, Pancreas (16k); TableS6 I37, average batch, scGPT random, Pancreas (16k)).

Gaps (unchanged from the first batch): the bracketed subsample columns, Fig. 1B and 1E (figure-only), and the UMAP, HVG, Harmony and scVI settings.

Needs reviewer judgement:

- Whether `avg-bio` should note that scGPT's own AvgBIO (Cui et al. 2024) may cluster differently; the scope note says only that the clustering procedure goes in the qualifier.
- The rank results from TableS3 ('Average BIO', 'Average batch' columns) are already in the store under metric `rank`; nothing here changes them.
