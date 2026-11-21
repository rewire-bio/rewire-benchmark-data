# MFASS v2: DNABERT-2, Pangolin and SpliceAI records marked source checked, 2026-11-21

Reviewer: Claude agent, automated. No human review is claimed. Nothing was run.

## What changed

Three evaluations and their nine results move from status `reproduced` to `source_checked`:

| Evaluation | Results |
| --- | --- |
| `rewire-evaluation-dnabert2-117m-frozen-pair-logreg` | `rewire-result-dnabert2-117m-frozen-pair-logreg-auroc`, `-average-precision`, `-precision-at-100` |
| `rewire-evaluation-pangolin-maskfalse` | `rewire-result-pangolin-maskfalse-auroc`, `-average-precision`, `-precision-at-100` |
| `rewire-evaluation-spliceai-1-3-1` | `rewire-result-spliceai-1-3-1-auroc`, `-average-precision`, `-precision-at-100` |

Each evaluation gains a `review` block that states the reason. Each result keeps its review block; one sentence giving the reason is added to the end of its `note`. No value, metric, source, link, origin or comparison field changed. `origin` stays `rewire_run`: these are Rewire's own runs.

## Why

The records say so themselves, and no receipt supports the stronger status.

- Each result's review has method `existing-run-import` and the note "Imported existing documented own-run record, not a newly executed reproduction."
- Each evaluation's `reproduction.explanation` says the recipe "does not regenerate model predictions or establish reproduction of the published score."
- The store holds one receipt of a full-protocol MFASS v2 run, `runner-receipt-mfass-v2-cpu-baselines-779eeb5c`. Its description and README name two runs, `mfass-kmer-position-v2` and `training-prior-v1`. It does not cover DNABERT-2, Pangolin or SpliceAI.
- On 2026-11-21 `benchmarks/mfass/reproductions/` on the main branch of rewire-bio/rewire-benchmarks held one folder, `2026-10-12-cpu-baselines`, the one that receipt pins.

The values were imported from the result files at `bee9133b` and are cited to `rewire-mfass-v2-source` with a locator each, which is what `source_checked` means. The k-mer baseline evaluation and its three results stay `reproduced`; they now cite the receipt (`docs/reviews/2026-11-21-mfass-receipt-citation.md`).

A full-protocol run of any of the three, with a receipt cited from its evaluation, is the route back to `reproduced`.

## Effects

- The release summary field `rewire_result_rows` counts results with status `reproduced`. It falls from 12 to 3, and `source_checked_results` rises by 9.
- Comparisons, use cases and the discrepancy rules treat `source_checked` and `reproduced` alike, so no result leaves a comparison.
- Use-case judgements: status is a pinned field, but only reviewed evaluations are pinned. The MFASS v2 judgement `use-case-mapping-20260930-339-25925e279972` lists one reviewed evaluation, the k-mer baseline, which did not change. Recomputing `claimPins` for every reviewed judgement, summary and baseline claim gives the same four stale summaries before and after, none caused by this change. No repin is needed.
