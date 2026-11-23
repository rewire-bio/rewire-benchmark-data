# ClinGen PP3/BP4 Missense Score Calibration (Rewire CPU Study, 2026-11-23)

Batch `data/omics/rewire-clingen-pp3-bp4-20261123/` built from `rewire-bio/rewire-benchmarks` commit `fbf4fd5df880ee685fa276dfa6a5bb46da4bcf73` (`benchmarks/clingen-pp3-bp4/`).

## Scope

- Evaluates nine score tracks across eight predictors (`GPN-MSA`, `GPN-Star vertebrate v100`, `GPN-Star mammal m447`, `AlphaGenome AVI` raw and PHRED, `AlphaMissense`, `REVEL v1.3`, `CADD v1.7`, and leaked `EVEE` control) on three temporally held-out ClinVar `>=2-star` missense SNV cohorts (`post_2023_12`, `post_2023_12_af001`, `post_2025_03`).
- Every numeric result reads its literal JSON number token via JSON pointer from `benchmarks/clingen-pp3-bp4/results/calibration_summary.json`.
- Unreached tiers (`null` in JSON) are omitted from `result` rows and documented in protocol and source limitations.
- EVEE (`Zenodo 19701997`) incorporates ClinVar supervision through `2026-03-20`; a scoped `evidence_concerns` entry on `rewire-local-20261123-clingen-source-readme` withholds its three evaluations (`post_2023_12`, `post_2023_12_af001`, `post_2025_03`) from unconfounded model comparisons and excludes them from `reviewed_evaluations` in the three use-case relevance judgement claims linking to `use-case-missense-pp3-bp4-calibrated-evidence`.
