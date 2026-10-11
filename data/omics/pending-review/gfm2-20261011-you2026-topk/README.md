# Pending review: You et al. 2026 "Average Top-k" results

These 22 result records came from `data/omics/gfm2-20261011-you2026`. The independent review of 2026-10-11
(`data/omics/gfm2-20261011-you2026/review.md`) took them out of the batch. They are not part of the store.

Why: the extractor recorded Supplementary Table 5's "Average Top-k" column as `splice-top-k-accuracy`,
which the vocabulary defines as SpliceAI-style top-k accuracy with k equal to the number of true sites.
The source defines top-k accuracy differently: "the fraction of times the true label is among the top k
predicted labels" (Methods, metric definitions). It never states k or how the average over categories is
taken. The printed values are transcribed correctly (checked cell by cell). What is unsupported is the
metric concept.

To bring them back, one of these is needed:

1. evidence that the authors computed the SpliceAI-style metric, for example in their released code or
   in a correction; or
2. a reviewed vocabulary concept for top-k accuracy with k unstated, and the records changed to use it.

The evaluations these results link to remain in the batch, with their Average PR-AUC results.

Files: `batch.jsonl` (the 22 records as extracted, `needs_review`) and `claims.csv` (their rows).
