# ClinGen PP3/BP4 post_2023_12_af001 Executed Recipe and Receipt Review, 2026-11-24

Reviewer: deterministic verification script (`rewire-deterministic-table-checker`). No human scientific review is claimed. Every artifact digest and metric value was verified by automated comparison against the committed `rewirebench 0.6.1` CPU receipt at `rewire-bio/rewire-benchmarks` commit `08fb03f9a47b0b934e73743eea08ccd36a25f0a7` (merge commit of PR #101).

## Outcome

- Added two `source` records (`status: "source_checked"`) via `npm run records -- add`:
  - `runner-receipt-clingen-pp3-bp4-af001-cpu-08fb03f9` for `benchmarks/clingen-pp3-bp4/reproductions/2026-11-24-af001-cpu/SHA256SUMS` and `receipt.json`
  - `runner-recipe-clingen-pp3-bp4-af001-calibration-08fb03f9` for `recipes/clingen-pp3-bp4/clingen-pp3-bp4-af001-calibration.yaml`
- Updated `rewire-local-20261123-clingen-protocol-post-2023-12-af001` via `npm run records -- change` to cite both new sources and record the executed `clingen-pp3-bp4-af001-calibration` entry in `attributes.run_recipes` (`status: "executed"`, `validation_receipt.scope: "full_protocol"`).
- Updated the eight non-leaked `post-2023-12-af001` evaluations (`alphamissense`, `avi`, `avi-phred`, `cadd-phred`, `gpn-msa`, `gpnstar-m`, `gpnstar-v`, `revel`) and all 120 of their child `result` records to `status: "reproduced"`, citing the verified receipt source and adding `attributes.reproduction` on each of the eight evaluations.
- Kept `rewire-local-20261123-clingen-evaluation-evee-post-2023-12-af001`, its 18 results, and the `post-2023-12` and `post-2025-03` strata unchanged at `status: "source_checked"`. EVEE incorporates ClinVar supervision through `2026-03-20` and remains excluded as a leaked descriptive control.

## Checks

| Check | Outcome |
| --- | --- |
| Raw GitHub `SHA256SUMS` at `08fb03f9a47b0b934e73743eea08ccd36a25f0a7` | `af9958559dbc899c168e54ab1509a6b2e17dca03116c5b620162f984e3ba33f1`, matches `artifact_sha256` |
| Raw GitHub `clingen-pp3-bp4-af001-calibration.yaml` at `08fb03f9a47b0b934e73743eea08ccd36a25f0a7` | `3a66001b46aa6dca971010821a91b33b1c279a35463c7fd869c546740b60d88a`, matches `artifact_sha256` |
| Strict receipt verification (`rewirebench receipt verify --strict`) | Passed: 49 hashed files in `SHA256SUMS`, 38 of 38 metric and coverage checks passed, `code.dirty: false` |
| Stored `post_2023_12_af001` results across 8 non-leaked predictors (`120` results) | 120 of 120 numeric values match per-predictor `report.json` values (`max_diff = 0.0`) |
| Platform and timing recorded in `receipt.json` | `macOS-26.6.2-arm64-arm-64bit` (Apple M4), Python `3.12.7`, `rewirebench 0.6.1`, CPU, `67.612 s` wall time |

## Scope and Limits

- This execution reruns the project's own Pejaver 2022 and Bergquist 2025 sliding-window local posterior calibration code over pinned precomputed variant score lookup tables. It does not rerun upstream model inference or constitute independent scientific reproduction by another group.
- `use-case-mapping-rewire-local-20261123-clingen-post-2023-12-af001` was re-reviewed and repinned via `npm run use-cases:repin` because promoting the eight evaluations and their 120 results from `source_checked` to `reproduced` updates their pinned status hashes without altering the underlying cohort, endpoint, relevance (`direct`), or EVEE exclusion boundary.
