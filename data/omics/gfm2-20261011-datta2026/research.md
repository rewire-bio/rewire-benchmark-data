# Research notes: Datta et al. 2026

## Why this source

An independent probing study across five genomic language model families on a benchmark the store already
holds other results for. It answers a question the store could not: how much of a fine-tuned model's
performance a frozen embedding plus a light probe recovers, and on which task families that gap opens.

## How the records are shaped

- Two configurations per model, frozen and fine-tuned, because the frozen setting is the authors' own protocol
  and the fine-tuned number comes from elsewhere. Keeping them apart stops a reader treating the pair as one
  matched run.
- Two protocols for the same reason. The fine-tuned protocol's `limitations` repeat the authors' own wording:
  benchmark- or model-reported reference values, not fully matched head-to-head comparisons.
- `origin` is `independent_paper` for the frozen evaluations and `unreported` for the fine-tuned ones, since
  the source does not say per cell who produced each reference score.
- Metrics follow Section 3.2: MCC for the ten histone-mark tasks and the two enhancer tasks, F1 for the three
  promoter and three splice-site tasks. MCC carries unit `unitless`, F1 `fraction`.

## Judgement calls a reviewer should check

1. The duplicated NT frozen cell for `Enhancer` and `Enhancer Types` is recorded as an `evidence_concerns`
   entry on the source rather than silently corrected. Both values stay as printed.
2. Standard deviations of `.0000` are recorded as a standard deviation of 0.0000 over five seeds, which is what
   the table prints; several are logistic-regression probes, which the paper says are deterministic.
3. The fine-tuned results carry `n` only where the source prints a spread; GENERATOR-v2's fine-tuned column
   prints no spread at all, so those results record an unreported uncertainty.
4. Whether to add a metric concept for recovery (frozen score as a share of fine-tuned score) is left open. The
   two inputs are both stored, so nothing is lost by waiting.
