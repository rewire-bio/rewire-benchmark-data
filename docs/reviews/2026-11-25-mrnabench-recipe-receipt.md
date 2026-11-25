# mRNABench Sample designed MRL Executed Recipe and Receipt Review, 2026-11-25

Reviewer: deterministic verification script (`rewire-deterministic-table-checker`). No human scientific review is claimed. Every artifact digest and metric value was verified by automated comparison against the committed `rewirebench 0.6.2` CPU receipt at `rewire-bio/rewire-benchmarks` commit `37cf4634f57d1d54619794f62d9b954186a864c6` (merge commit of PR #104, built from tagged release commit `95e7cd6facb41ad18aad27759afd4463a177599f`).

## Outcome

- Added two `source` records (`status: "source_checked"`) via `npm run records -- add`:
  - `runner-receipt-mrnabench-designed-mrl-cpu-37cf4634` for `benchmarks/mrnabench/reproductions/2026-11-25-designed-mrl-cpu/SHA256SUMS` and `receipt.json`
  - `runner-recipe-mrnabench-designed-mrl-baselines-37cf4634` for `recipes/mrnabench/mrnabench-designed-mrl-baselines.yaml`
- Updated `rewire-protocol-mrnabench-designed-mrl-v1` via `npm run records -- change` to cite both new sources and append the executed `mrnabench-designed-mrl-baselines` entry in `attributes.run_recipes` (`status: "executed"`, `validation_receipt.scope: "full_protocol"`), while keeping the earlier `local-20260920-mrnabench-repeat` entry intact.
- Updated both baseline evaluations (`rewire-local-20260920-evaluation-mrnabench-composition` and `rewire-local-20260920-evaluation-mrnabench-train-mean`) to `status: "reproduced"`, citing both new recipe and receipt sources and updating `attributes.reproduction` to `mrnabench-designed-mrl-baselines`, and promoted all six of their child `result` records to `status: "reproduced"` while leaving their `source_ids` unchanged (matching `tests/omics-run-receipt-badge.test.ts`).
- Refined `recordsOf()` in `shared/omics/reports/figures.ts` (`spanInputContent`) so span-resolution drift tracking hashes only the JSONL fields read by `scripts/omics/spans/cli.ts` (`id` on sources; `id`, `source_ids`, `source_locator`, and `printed_value` on results), and regenerated `maintenance/reports/span-resolution-figures-records.tsv` (`56,364` rows across all 18 verified inputs at measurement commit `b2937f57c0b542169c3011164da077c4bff09b04`) without altering `maintenance/reports/span-resolution-figures.json`.

## Checks

| Check | Outcome |
| --- | --- |
| Raw GitHub `SHA256SUMS` at `37cf4634f57d1d54619794f62d9b954186a864c6` | `34706581713c8e53e087203d5152d346fb8885ef2bf45c02d4ccd3d0442486bc`, matches `artifact_sha256` |
| Raw GitHub `mrnabench-designed-mrl-baselines.yaml` at `37cf4634f57d1d54619794f62d9b954186a864c6` | `a025843c19a25d7eb6470c0abef0994da074929f8ad392d7ca4d9c1e7954e996`, matches `artifact_sha256` |
| Strict receipt verification (`rewirebench receipt verify --strict`) | Passed: 15 hashed files in `SHA256SUMS`, 11 of 11 recipe checks passed, 6 metric values verified, `code.dirty: false`, `code.commit: 95e7cd6facb41ad18aad27759afd4463a177599f` |
| Stored `rewire-protocol-mrnabench-designed-mrl-v1` metrics across both baselines (`6` results) | `training-mean-v1` MSE matches bitwise (`2.3655294722554605`, diff `0.0`); `training-mean-v1` Pearson/Spearman remain `undefined` due to constant predictions; `rna-composition-probe-v1` Spearman matches bitwise (`0.49477537290902324`), MSE (`1.9144397158433855` vs stored `1.914439715839851`, diff `3.5e-12`) and Pearson (`0.43678691701454914` vs stored `0.4367869170170987`, diff `2.5e-12`) agree within `1e-9`; all `15,003` of `15,003` test records scored |
| Platform and timing recorded in `receipt.json` | `macOS-26.6.2-arm64-arm-64bit` (Apple M4), Python `3.11.13`, `rewirebench 0.6.2`, CPU, `14.764 s` wall time, `1,010,352,128` bytes peak RSS |

## Scope and Limits

- This execution reruns the project's own sequence-composition RidgeCV and training-mean baselines over the pinned `morrislab/mrl-sample` designed 5' UTR parquet input. It does not rerun an external foundation model or constitute independent scientific reproduction by another group.
- `use-case-mapping-utr-translation-baselines-designed-v1` and `use-case-summary-utr-translation-baselines` were re-reviewed and repinned via `npm run use-cases:repin` because promoting the two evaluations and their six results from `source_checked` to `reproduced` and appending the recipe and receipt sources updates their pinned hashes without altering the underlying split (`seed 2541`, `70,011` train / `15,003` val / `15,003` test), endpoint (`target_mrl_designed`), or `direct` relevance judgement.
