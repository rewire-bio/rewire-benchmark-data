# Intake for issue #465

Add discovered model FoldScape: Q-conditioned protein folding-ensemble generation from sequence

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-27. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-465-20261127-model-foldscape` (model, depth tier 2)

## Sources

- https://arxiv.org/abs/2611.04287: `intake-465-20261127-source-2611-04287-predicting-protein-structures-at-any-folding-stag`, SHA-256 b75c856d37690faee381184e72657372fe9a8fa66946067f4425d708442b9b29, text/html
- https://arxiv.org/html/2611.04287: `intake-465-20261127-source-1-introduction`, SHA-256 4c9a4aaab94b9a2e2344de32d6113b25f4238b44a5268bbd32c16bc6c8dc0286, text/html
- https://arxiv.org/pdf/2611.04287v2: `intake-465-20261127-source-arxiv-org-pdf-2611-04287v2`, SHA-256 832fa043f90c93eb3e4bc22f0d107ffaa32af733ea2f93007b631b7fd6f2b7c5, application/pdf

## Not added

- None.

## Links

- None.

## Possible duplicates in the store

- None.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| FoldScape | version |   | No |
| FoldScape | access |   | No |
| FoldScape | licence |   | No |
| FoldScape | training_data | Folding data from coarse-grained Gō models with native contacts biased toward AlphaFold-predicted structures; unfolding  | Yes |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 | 8917 | 3487 | 39242 | 5795 | 0 | 3 | $0.0046 |
| claude-sonnet-5-5 | 4 | 22168 | 10695 | 2047 | 0 | 0 | $0.0770 |
| Total | | | | | | | $0.0816 |
