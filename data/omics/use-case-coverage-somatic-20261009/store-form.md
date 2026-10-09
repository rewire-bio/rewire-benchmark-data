# Store form of the reviewed batch

`batch.jsonl` is the reviewed batch and is unchanged, so the receipt in `review.json` still binds the reviewed bytes.

The store copy of the dataset below differs from `batch.jsonl` only in the key order of `missing_metadata`: `population_detail` now comes before `version`. The order was produced by `normalizeAttributes` (`shared/omics/attributes.ts`). No key or value changed; a deep comparison with sorted keys is equal before and after.

- `somatic-20261009-data-guille2025-seqc2-fd-wes`
