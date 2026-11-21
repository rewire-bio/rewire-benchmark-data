# MFASS v2 k-mer baseline: cite the run receipt, 2026-11-21

Reviewer: Claude agent, automated. No human review is claimed. Nothing was run. This is a check of the receipt's files against the stored records.

## What changed

`rewire-evaluation-baseline-kmer-position-v2` now lists `runner-receipt-mfass-v2-cpu-baselines-779eeb5c` in `source_ids`, after its three existing sources. No other field changed, and no result record changed.

The receipt source was added on 2026-10-12 (`docs/reviews/2026-10-12-mfass-recipe-receipt.md`) and was cited by the protocol `rewire-mfass-v2` and one use-case judgement, but not by the evaluation whose run it repeats. So no record tied the stored scores to a full-protocol run.

## What was checked

The receipt folder is `benchmarks/mfass/reproductions/2026-10-12-cpu-baselines/` in rewire-bio/rewire-benchmarks at commit `779eeb5c88712442fbc9682c3d417cb7a7427fe3`. On 2026-11-21 I downloaded two files at that commit through the GitHub contents API:

| File | SHA-256 of the downloaded bytes | Compared with |
| --- | --- | --- |
| `SHA256SUMS` | `fab950f4822b92f1056108bec7e17e398bf173533008391662c7ed922163c644` | equals the source record's `artifact_sha256` |
| `mfass-kmer-position-v2/report.json` | `1cba80f08af3b50393c710527c3ae81dc2cc49c07d036015be1cbfde4bd985c9` | equals its line in `SHA256SUMS` |

`report.json` has `protocol_id` `mfass-v2`, `completion` `complete`, coverage 8,324 of 8,324, `adapter_provenance.method` `baseline-kmer-position-v2` and `reference_revision` `bee9133b83f3aedaf2bbb9013f1875515845607e`, the version the evaluation records. Its `metrics` against the stored results:

| Metric | `report.json` | Stored result | Stored `printed_value` |
| --- | --- | --- | --- |
| Precision at 100 (`precision_at_capacity`, capacity 100) | 0.61 | `rewire-result-baseline-kmer-position-v2-precision-at-100` | 0.61 |
| Average precision (`average_precision_sklearn`) | 0.28641674595892375 | `rewire-result-baseline-kmer-position-v2-average-precision` | 0.2864167459589237 |
| AUROC (`auroc`) | 0.7779498064677238 | `rewire-result-baseline-kmer-position-v2-auroc` | 0.7779498064677238 |

Precision at 100 and AUROC are identical. Average precision differs in the last printed digit: the two decimals are adjacent double-precision values, 5e-17 apart. The stored value is the one in the original run file at `bee9133b` (`data/omics/audits/mfass-ap-correction.json` records that alignment, 2026-09-19). The stored value was not changed.

## Scope and limits

- The receipt's description names two runs, `mfass-kmer-position-v2` and `training-prior-v1`. Only the k-mer baseline evaluation cites it. The DNABERT-2, Pangolin and SpliceAI evaluations on MFASS v2 are not covered by it and do not cite it.
- `rewire-local-20260921-evaluation-mfass-prior` was not checked against `training-prior-v1/report.json` and does not cite the receipt.
- The receipt is the project's own rerun with its own code and data (`independently_reproduced: false` in the report). It is not an independent reproduction.
- `predictions.json` and the other files in the folder were not downloaded again; the 2026-10-12 review checked all ten against `SHA256SUMS`.

## Use-case judgements

A judgement pins an evaluation's `status`, `links`, `attributes.origin` and `attributes.comparison` (`judgementPinFields` in `shared/omics/use-cases.ts`). `source_ids` is not pinned, so this change withholds no judgement. Checked by recomputing `claimPins` for every reviewed judgement, summary and baseline claim before and after the change: the same four summaries differ from their stored pins before and after, and none of them is caused by this change.
