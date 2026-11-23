# ClinGen PP3/BP4 CPU Calibration Records Review, 2026-11-23

Reviewer: deterministic verification script (`rewire-deterministic-table-checker`). Every numeric value was read directly by `extract/build_batch.py` from `benchmarks/clingen-pp3-bp4/results/calibration_summary.json` at `rewire-bio/rewire-benchmarks` commit `fbf4fd5df880ee685fa276dfa6a5bb46da4bcf73` with integer and float tokens preserved as strings, then verified against raw GitHub bytes and SHA-256 digests. No human scientific review is claimed.

## Source Files (`rewire-bio/rewire-benchmarks` @ `fbf4fd5df880ee685fa276dfa6a5bb46da4bcf73`)

- `benchmarks/clingen-pp3-bp4/README.md`
- `benchmarks/clingen-pp3-bp4/results/calibration_summary.json`
- `benchmarks/clingen-pp3-bp4/results/calibration_tables.tsv`
- `benchmarks/clingen-pp3-bp4/results/receipt.json`
- `benchmarks/clingen-pp3-bp4/cohorts/cohort_summary.json`
- `benchmarks/clingen-pp3-bp4/raw/download_manifest.json`

## Rulings

- All 27 evaluations (`origin: "rewire_run"`) carry status `source_checked`, citing both `calibration_summary.json` and the CPU `receipt.json`.
- A scoped `evidence_concerns` entry on `rewire-local-20261123-clingen-source-readme` names the three `EVEE` evaluations because EVEE incorporates ClinVar labels through `2026-03-20`.
- Three `links:assessed_by:` relevance judgements link the three cohorts to `use-case-missense-pp3-bp4-calibrated-evidence`, covering the eight unconfounded predictor tracks per cohort.
