---
name: extract-evaluations
description: Capture a primary source and extract its models, benchmarks, datasets, protocols, evaluations, results and descriptive claims into a hash-bound batch, with exact printed values and source locators. Use after literature-search has identified a source worth extracting. Does not mark its own work reviewed.
---

# Extract evaluations

Follow [docs/collection.md](../../../docs/collection.md), sections 3, 4 and 6, and the field rules in [docs/record-contract.md](../../../docs/record-contract.md).

## Inputs

- One source: URL, version and the tables or figures to extract.
- A batch folder name, `data/omics/<batch>/`. Ask if unclear.

## Steps

1. Retrieve the artifact, compute its SHA-256, and create the `source` record (`url`, `version`, `retrieved_at`, `artifact_sha256`, `doi`, `publication_status`, `licence`). Pin GitHub links to a commit. If retrieval fails, stop and report the gap.
2. Search the canonical store (`data/entities/*.jsonl`, `data/evidence/*.jsonl`) for the same models, configurations, benchmarks, protocols, datasets and sources. Reuse their IDs; create new ones only for genuinely new entities.
3. Extract every cell of each chosen table, not a selection. Use `scripts/omics/extract/<benchmark>.ts` if one exists. For each result record keep `printed_value` exactly as printed (or, for a value computed from the source's own Source Data rows, the computed value with a `derivation`; see below), `numeric_value` as a decimal string or `null`, `metric` and `unit` as concept keys from `data/vocab/metric.ttl` and `unit.ttl` (with `metric_qualifier` and `unit_detail` for anything the concept does not hold), `metric_direction`, `uncertainty` and a precise `source_locator`. Put the printed row and column labels in `source_locator`, and a tool's printed name in `reported_name`. Do not use `source_label`: it is reserved for records renamed through a reviewed `source_identity`, and the release refuses it otherwise (`tests/source-identity-store.test.ts`). Areas, method types, review method and reviewer are concept keys too; see docs/collection.md.
4. Set unknown fields to `null` with a reason in `missing_metadata`. Do not assign a result to a specific checkpoint unless the source names it. Do not read numbers off unlabelled figures or from pixels. Where the source publishes the per-item rows behind a figure (a Source Data workbook or a supplementary table) and states the aggregation in its own words, you may compute the value (docs/collection.md, "Values computed from source data"): create a `source` record for each file with its SHA-256, re-download and check it before use, write a deterministic script in the repository that asserts the row counts, and record a `derivation` with the inputs (`source_id`, `artifact_sha256`, `locator`, `row_filter`, `row_count`), the quoted `aggregation` with `aggregation_source_id` and `aggregation_locator`, `script`, `script_sha256` and `precision`. Keep the evaluation's origin as the source states it. If the aggregation is ambiguous, do not compute it; record a gap. Never use a third party's reanalysis.
5. Write descriptive facts about models or benchmarks as `claim` records with their own locators.
6. Write the new records to `data/omics/<batch>/batch.jsonl`, plus `claims.csv`, `sources.md`, `retrieval-log.md` and `research.md` (and `coverage.json` for use-case work). For use-case work, add one relevance judgement per protocol that bears on the use case: an `assessed_by` link on the `use_case` record and a judgement claim recording relevance (`direct`, `proxy` or `outside_scope`), endpoint, rationale, constraints, limitations and the sources it rests on, with status `needs_review` (docs/use-cases.md). Fill `method_types`, version and access on every configuration you add. For grouped tables, add `comparison_group`, `comparison_title`, `stratum_label`, `stratum_order` and `headline_metric` to each judgement. Draft or update the use case's `summary` claim (descriptive, every number traceable to a result, author-reported benchmarks and truth-set bias named, no recommendation). Never mark your own judgement or summary reviewed.
7. After `review-evidence` has written the receipt, add the batch to the store: `npm run records -- add data/omics/<batch>/batch.jsonl data/omics/<batch>`.
8. In each result's `review.notes`, record how it was extracted (parser, transcription, page render). Leave review sign-off to `review-evidence`.
9. Run `npm test`, `npm run typecheck` and `npm run build`.

## Outputs

The batch files, the source record, any mapping change, and a report listing the record counts, every gap, and anything that needs a reviewer's judgement (conflicting tables, unclear units, abstract and body disagreeing).

## Rules

- Never edit an existing record's value, ID or hash. Corrections go through `review-evidence`.
- Never record a missing value as zero.
- Do not change `data/omics/release-config.json`.
