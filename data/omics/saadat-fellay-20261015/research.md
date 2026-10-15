# Research notes: Saadat and Fellay 2026 (issue #162)

Scope: the one paper named in issue #162, item 1. 2026-10-15. Extraction by a Claude (Opus 5.5) agent. All 38 records have status `needs_review`.

## What was extracted

| What | Records |
| --- | --- |
| Figure 1: Pearson r between reference and efficient-implementation pseudo-perplexity, 50 synthetic sequences of length 1000 | 4 results (GENA-LM 110M 1.00, GENA-LM 336M 1.00, NT 500M 1.00, NT 2.5B 0.98) |
| Section 3.3: training peak GPU memory at length 1000, batch 16, before and after ZeRO Stage-2 CPU offload | 4 results (GENA-LM 110M 1.18 and 2.49 GB; NT 2.5B 33.88 and 11.49 GB) |
| Section 3.5: NT 2.5B memory at BF16 and 4-bit | 2 results (6.7 and 5.6 GB) |
| Findings with no printed values | 3 claims (quantization embedding similarity bounds, fine-tuning efficiency, figures not extracted) |
| Supporting records | 1 source, 1 dataset (synthetic DNA), 3 protocols, 10 configurations, 10 evaluations |

Reused, unchanged: `regulatory-variant-20261009-model-gena-lm` and `discovery-model-nucleotide-transformer` (family-level model records).

## Decisions

- **Checkpoints.** The paper names only the family and size. Several GENA-LM checkpoints have about 110M parameters, and NT 500M and 2.5B each exist for more than one pretraining corpus. Every configuration therefore links to the family record and records the checkpoint as unreported.
- **One configuration per measured setup.** The efficient inference implementation (four models), the two training stages either side of ZeRO offload (GENA-LM 110M and NT 2.5B) and the two NT 2.5B weight precisions are separate configurations, so results with different setups are never compared as if they were the same system.
- **Training stages.** Section 3.3 says ZeRO offload takes NT 2.5B from 33.88 to 11.49 GB and GENA-LM 110M from 1.18 to 2.49 GB. Figure 3 is cumulative (Baseline, + FlashAttention, + Checkpointing, + DeepSpeed), so the first value of each pair is the FlashAttention plus checkpointing stage and the second adds ZeRO.
- **Origin.** `independent_paper`: the authors built the implementation and ran the measurements but did not develop GENA-LM or the Nucleotide Transformer.
- **Data link.** Section 2.4 lists two input types: synthetic uniform random sequences "to isolate implementation and hardware effects", and the promoter and enhancer tasks. The training-memory and quantization experiments are not downstream tasks, so they are linked to the synthetic data, and each protocol says the link rests on that paragraph rather than an explicit statement.
- **Quantization memory.** Section 2.4 calls it parameter memory; Figure 5 labels it peak memory. A 1.1 GB drop from BF16 to 4-bit for a 2.5B model is far smaller than the weight saving alone, so the values are recorded as peak memory with a `source_discrepancy` on both results. This was not raised as a source-level evidence concern because that would also block the unrelated fidelity and training-memory results from comparison; the reviewer may decide otherwise.
- **Bounds and approximations.** "above 0.98" and "roughly 0.9" (embedding cosine similarity) are a claim, not results: one is a bound over three models and two precisions, and the other does not say whether it is the 8-bit or the 4-bit value.
- **Figure 1 values** are printed text inside a raster figure. Existing records already transcribe printed labels from raster figures (EVEE Figure 1c, printed bar labels in Fig. 3f and 4g of another batch); nothing was read from point positions.

## Gaps

- Issue #162 asks for fine-tuning speed. Figure 4 plots total training time, peak memory and accuracy for each model and implementation without printing values, and the text gives no speedup factor, so no fine-tuning speed or fine-tuning memory is recorded.
- Figure 2 (inference memory and throughput curves), the other Figure 3 points and the other Figure 5 bars: plotted only.
- No variance is reported anywhere, although inference benchmarks are said to be the mean of 10 runs.
- No code, checkpoint names or software versions are given in the PDF. The forum page could not be read by script.
- No use-case relevance judgements were added. The three protocols are candidates for `use-case-diagnostic-genomics-model-execution` (training and inference memory on one H100).
