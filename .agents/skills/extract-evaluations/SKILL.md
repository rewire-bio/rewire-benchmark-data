---
name: extract-evaluations
description: Capture a primary source and extract its models, benchmarks, datasets, protocols, evaluations, results and descriptive claims into a hash-bound batch, with exact printed values and source locators. Use after literature-search has identified a source worth extracting. Does not mark its own work reviewed.
---

# Extract evaluations

Follow [docs/collection.md](../../../docs/collection.md), sections 3, 4 and 6, and the field rules in [docs/record-contract.md](../../../docs/record-contract.md).

## Inputs

- One source: URL, version and the tables or figures to extract.
- Where the records go: a benchmark batch (`data/omics/reviewed/<benchmark>-<year>.jsonl`) or a use-case coverage batch (`data/omics/use-case-coverage-<batch>/<lane>/`). Ask if unclear.

## Steps

1. Retrieve the artifact, compute its SHA-256, and create the `source` record (`url`, `version`, `retrieved_at`, `artifact_sha256`, `doi`, `publication_status`, `licence`). Pin GitHub links to a commit. If retrieval fails, stop and report the gap.
2. Search existing records for the same models, configurations, benchmarks, protocols and datasets. Reuse their IDs; create new ones only for genuinely new entities.
3. Extract every cell of each chosen table, not a selection. Use `scripts/omics/extract/<benchmark>.ts` if one exists. For each result record keep `printed_value` exactly as printed, `numeric_value` as a decimal string or `null`, `metric`, `metric_direction`, `unit`, `uncertainty` and a precise `source_locator`.
4. Set unknown fields to `null` with a reason in `missing_metadata`. Do not assign a result to a specific checkpoint unless the source names it. Do not read numbers off unlabelled figures.
5. Write descriptive facts about models or benchmarks as `claim` records with their own locators.
6. For a use-case batch, also write `claims.csv`, `coverage.json`, `sources.md`, `retrieval-log.md` and `research.md` for the lane. Add or update the use-case mapping in `data/omics/use-cases/inputs.json`.
7. Register a new batch as a build input (`scripts/omics/inputs.ts` for benchmark batches, the `addUseCaseCoverage` chain in `scripts/omics/release.ts` for use-case batches).
8. In each result's `review.notes`, record how it was extracted (parser, transcription, page render). Leave review sign-off to `review-evidence`.
9. Run `npm test`, `npm run typecheck` and `npm run build`.

## Outputs

The batch files, the source record, any mapping change, and a report listing the record counts, every gap, and anything that needs a reviewer's judgement (conflicting tables, unclear units, abstract and body disagreeing).

## Rules

- Never edit an existing record's value, ID or hash. Corrections go through `review-evidence`.
- Never record a missing value as zero.
- Do not change `data/omics/release-config.json`.
