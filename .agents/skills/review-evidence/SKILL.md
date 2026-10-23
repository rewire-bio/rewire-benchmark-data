---
name: review-evidence
description: Independently re-check an extracted evidence batch against its pinned sources, record the review on every result, write the hash-bound receipt and a dated review, and raise concerns or superseding corrections. Use after extract-evaluations, or to audit existing records. Must be run by a different worker from the extractor.
---

# Review evidence

Follow [docs/collection.md](../../../docs/collection.md), section 5.

## Inputs

- A batch path, or a set of existing record IDs to audit.
- Confirmation that you did not extract this batch. If you did, stop: review must be independent.
- A frozen extraction commit. Do not start while the extractor is still changing the batch.

## Steps

1. Re-retrieve each source or open the archived copy, and check its SHA-256 against the `source` record. A mismatch is a finding, not something to fix by updating the hash.
2. For every result, check `printed_value`, `numeric_value`, `source_locator`, metric concept and qualifier, direction, unit concept, uncertainty, denominator and the configuration and protocol it is attached to. Check that every `null` is genuinely unstated in the source. For a large batch, an automated comparison of every value against the source plus a sampled manual check is enough; record both in the receipt. Run the comparison with `npm run -s batch -- check-values` (docs/collection.md, section 5) and keep its `value-check.tsv` in the batch folder. For a result with a `derivation`: re-download each input and check its SHA-256 against the input and its source record; check that the script's hash matches; rerun the script on the pinned inputs and confirm the row counts and the computed value equal `row_count` and `printed_value`; check the quoted `aggregation` against the source at `aggregation_locator` and that the script applies it and no other; and check that the inputs are the source's own supplementary data. Record `source-data-recomputation` in the review method.
3. Check descriptive `claim` records the same way.
4. For relevance judgements (claims with `field` `links:assessed_by:<protocol>`), check that the endpoint matches the use case's inputs and desired output, that `direct` or `proxy` is justified, that the limitations carry the source's own caveats and evidence concerns, and that every `excluded_evaluations` entry has a reason. If it holds, list the evaluations you checked in `reviewed_evaluations`, set it to `source_checked`, fill its `review`, then record its pins with `npm run use-cases:repin -- <dated review> <claim-id>...`. Review a use case's `summary` claim the same way, after its judgements: every number must match a result, it must name author-reported benchmarks and known truth-set bias, and it must not recommend.
5. Fill each result's `review`: `method` (plain description of how it was checked), `reviewer` (the actual actor, e.g. "Codex research agent; no human review claimed"), `date`, `artifact_sha256`, `retrieval_url`, `notes`.
6. For problems:
   - a source or result that should not support comparison: add an entry to the source record's `attributes.evidence_concerns` with artifact hash, locator and date, and list the affected record IDs in `applies_to` (docs/collection.md). Leave `applies_to` out only when the whole source is unreliable: that withholds every use case citing it
   - a wrong descriptive field: change it and add a `metadata-correction-*` claim keeping the previous value
   - a wrong number in a stored record: add a corrected result that supersedes it; never edit the old value
   - after any edit to a stored record, run `npm run records -- change <dated review> <batch folder> <ids>` so provenance records the change
   - a batch not ready for the build: move it to `data/omics/pending-review/<batch>/` with a README stating why
7. Check the discrepancies that involve the batch's results: in the latest `discrepancies.json` (or the `discrepancies_for_system` named query), look for the batch's result IDs in `outlier_results` and `consensus_results`. A discrepancy is a lead, not an error. If the review settles or advances one, record it as a new `discrepancy_review` claim revision (docs/discrepancies.md): the same `discrepancy_id`, `revision` one above the last accepted one, `value` the state after the step, `action` from `data/vocab/discrepancy-action.ttl`, `date`, `rationale`, and the URLs and `next_check` that apply. A confirmed error is fixed by the record change in step 6, which marks the results `disputed` or adds an evidence concern.
8. Finish every ruling and edit in `batch.jsonl` before this step. Write the batch receipt `data/omics/<batch>/review.json`: schema version, method, reviewer, reviewed_at, scope, limitations, empty errors, the SHA-256 of `batch.jsonl` and every other file in the folder, and the SHA-256 of each source artifact checked. Write the hashes last with `npm run -s batch -- hash`. A `build.py` that rebuilds the batch is optional.
9. Write a dated review in `docs/reviews/` (or `docs/reviews/use-cases/`): sources and hashes, how values were compared and the sample drawn, a link to the mismatch report, a ruling on each question the extractor raised with the deciding source text, conflicts, and remaining gaps. Do not copy every value into a table.
10. Add the batch to the store once (`npm run records -- add`, docs/collection.md step 6), then run `npm run records -- check`, `npm run test:fast`, `npm run typecheck` and `npm run build`. CI runs the full tests and the SHACL check of the whole store; the release is cut after merge.

## Rules

- Human review is recorded only when a named person did it. Source transcription is not reproduction.
- A review that finds nothing to change is a valid result; record it in the dated review.
- Do not regenerate a receipt to clear a validation failure without re-checking what changed.
