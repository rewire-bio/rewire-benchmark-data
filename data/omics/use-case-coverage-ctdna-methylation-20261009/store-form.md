# Store form of the reviewed batch

`batch.jsonl` is the reviewed batch and is unchanged, so the receipt in `review.json` still binds the reviewed bytes.

The store copy of the 10 evaluations below differs from `batch.jsonl` only in the key order of `missing_metadata`: `comparison.metric_implementation` now comes before `comparison.split`. The order was produced by `normalizeAttributes` (`shared/omics/attributes.ts`). No key or value changed; a deep comparison with sorted keys is equal before and after.

- `ctdnameth-20261009-eval-sun2024-celfeer-cfmethyl`
- `ctdnameth-20261009-eval-sun2024-celfeer-hcc-wgbs`
- `ctdnameth-20261009-eval-sun2024-celfie-cfmethyl`
- `ctdnameth-20261009-eval-sun2024-celfie-hcc-wgbs`
- `ctdnameth-20261009-eval-sun2024-cfnome-cfmethyl`
- `ctdnameth-20261009-eval-sun2024-cfnome-hcc-wgbs`
- `ctdnameth-20261009-eval-sun2024-methatlas-cfmethyl`
- `ctdnameth-20261009-eval-sun2024-methatlas-hcc-wgbs`
- `ctdnameth-20261009-eval-sun2024-uxm-cfmethyl`
- `ctdnameth-20261009-eval-sun2024-uxm-hcc-wgbs`
