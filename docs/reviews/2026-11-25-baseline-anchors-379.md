# Protocol Anchor Claims and Release Support (Issue #379)

Date: 2026-11-25

## Summary

Adds first-class sourced anchor claims (`null_baseline`, `conventional_baseline`, `experimental_ceiling`) on protocols, with explicit source citations, locators, pin verification, use-case release export, and release graph properties (`rb:servedNullBaseline`, `rb:servedConventionalBaseline`, `rb:servedExperimentalCeiling`).

## Seeded Anchor Claims

1. `anchor-mrnabench-designed-mrl-v1-null-baseline` (`null_baseline` on `rewire-protocol-mrnabench-designed-mrl-v1`): constant training-target mean control on the canonical 15,003-record Sample designed test split (`mean-squared-error`, `2.3655294722554605`, lower is better), cited from `rewire-local-20260920-source-mrnabench-train-mean` and `rewire-local-20260920-audit-source-mrnabench-train-mean` (`metrics.mse`).
2. `anchor-mrnabench-designed-mrl-v1-conventional-baseline` (`conventional_baseline` on `rewire-protocol-mrnabench-designed-mrl-v1`): train-only sequence composition + RidgeCV control on the same canonical 15,003-record split (`mean-squared-error`, `1.914439715839851`, lower is better), cited from `rewire-local-20260920-source-mrnabench-composition` and `rewire-local-20260920-audit-source-mrnabench-composition` (`metrics.mse`).
3. `anchor-ross-experimental-survey-ceiling-kendall-tau` (`experimental_ceiling` on `uc-leadopt-20261022-protocol-ross-experimental-survey`): repeat-assay experimental concordance ceiling (`kendall-tau`, `0.71`, printed `0.71 [0.65, 0.74]`, higher is better), cited from `uc-leadopt-20261022-source-ross2023` (`Table 3, row "Kendall τ", column "Experimental survey"`).
