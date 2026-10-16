# Saadat and Fellay 2026 extraction (issue #162)

Batch: `data/omics/saadat-fellay-20261015` (38 records). Source: Saadat and Fellay, "Optimizing genomic language models for efficient training, fine-tuning, and inference", ICLR 2026 workshop paper, OpenReview NUleWh1GFx, PDF SHA-256 `4bc2452110f280a7ba8baa4c7c28beac89769511019666bc77fc33af9b3bcd60`.

Independent review: [saadat-fellay-2026-10-15-review.md](saadat-fellay-2026-10-15-review.md). The rest of this page is the extraction handoff as written before review.

Extracted by a Claude (Opus 5.5) agent on 2026-10-15. **Not yet reviewed.** Every record has status `needs_review`, and each result's `review` block says it is an extraction, not a review. An independent `review-evidence` pass is still needed. No human review is claimed, and nothing here is a reproduction.

## Values extracted

| Result | Printed | Locator |
| --- | --- | --- |
| GENA-LM 110M pseudo-perplexity agreement, Pearson r | r = 1.00 | Figure 1 legend (raster), page 4 |
| GENA-LM 336M pseudo-perplexity agreement, Pearson r | r = 1.00 | Figure 1 legend (raster), page 4 |
| NT 500M pseudo-perplexity agreement, Pearson r | r = 1.00 | Figure 1 legend (raster), page 4 |
| NT 2.5B pseudo-perplexity agreement, Pearson r | r = 0.98 | Figure 1 legend (raster), page 4 |
| GENA-LM 110M training peak memory, FlashAttention and checkpointing | 1.18 GB | Section 3.3, page 6 |
| GENA-LM 110M training peak memory, adding ZeRO-2 offload | 2.49 GB | Section 3.3, page 6 |
| NT 2.5B training peak memory, FlashAttention and checkpointing | 33.88 GB | Section 3.3, page 6 |
| NT 2.5B training peak memory, adding ZeRO-2 offload | 11.49 GB | Section 3.3, page 6 |
| NT 2.5B memory, BF16 | 6.7 GB | Section 3.5, page 7 |
| NT 2.5B memory, 4-bit | 5.6 GB | Section 3.5, page 7 |

Three claims record findings without printed values: embedding cosine similarity under quantization (above 0.98 except NT 2.5B, roughly 0.9 for NT 2.5B), the fine-tuning efficiency finding (Figure 4), and the list of figures not extracted.

## For the reviewer

- Re-download the PDF by hand from https://openreview.net/pdf?id=NUleWh1GFx and check its hash.
- Read the four Figure 1 legend values from the figure image independently; the PDF has no text layer for them.
- Check the stage assignment of the Section 3.3 values against Figure 3 (cumulative stages).
- Decide whether the quantization memory discrepancy (Section 2.4 "parameter memory" against Figure 5 "Peak Memory (GB)") should become a source-level evidence concern. It is recorded on the two results only, because a source concern would also block the fidelity and training-memory results.
- Check that linking the training-memory and quantization protocols to the synthetic data is justified by Section 2.4 "Data".

## Gaps

Fine-tuning speed, fine-tuning memory and accuracy (Figure 4), inference scaling (Figure 2) and the remaining Figure 3 and Figure 5 values are plotted without printed values and are not recorded. Checkpoint identities, code and software versions are not given. Details are in the batch's `research.md`.
