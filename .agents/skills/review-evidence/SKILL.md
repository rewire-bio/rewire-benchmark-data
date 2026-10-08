---
name: review-evidence
description: Independently re-check an extracted evidence batch against its pinned sources, record the review on every result, write the hash-bound receipt and a dated review, and raise concerns or superseding corrections. Use after extract-evaluations, or to audit existing records. Must be run by a different worker from the extractor.
---

# Review evidence

Follow [docs/collection.md](../../../docs/collection.md), section 5.

## Inputs

- A batch path, or a set of existing record IDs to audit.
- Confirmation that you did not extract this batch. If you did, stop: review must be independent.

## Steps

1. Re-retrieve each source or open the archived copy, and check its SHA-256 against the `source` record. A mismatch is a finding, not something to fix by updating the hash.
2. For every result, check `printed_value`, `numeric_value`, `source_locator`, metric, direction, unit, uncertainty, denominator and the configuration and protocol it is attached to. Check that every `null` is genuinely unstated in the source.
3. Check descriptive `claim` records the same way.
4. Fill each result's `review`: `method` (plain description of how it was checked), `reviewer` (the actual actor, e.g. "Codex research agent; no human review claimed"), `date`, `artifact_sha256`, `retrieval_url`, `notes`.
5. For problems:
   - a source or result that should not support comparison: add an entry to the source record's `attributes.evidence_concerns` with artifact hash, locator and date
   - a wrong descriptive field: change it and add a `metadata-correction-*` claim keeping the previous value
   - a wrong number in a stored record: add a corrected result that supersedes it; never edit the old value
   - after any edit to a stored record, run `npm run records -- change <dated review> <batch folder> <ids>` so provenance records the change
   - a batch not ready for the build: move it to `data/omics/pending-review/<batch>/` with a README stating why
6. Write the batch receipt `data/omics/<batch>/review.json`: schema version, method, reviewer, reviewed_at, scope, limitations, empty errors, and the SHA-256 of `batch.jsonl` and every other file in the folder.
7. Write a dated review in `docs/reviews/` (or `docs/reviews/use-cases/`): sources and hashes, a table of every value checked with its outcome, conflicts, and remaining gaps.
8. Run `npm test`, `npm run typecheck` and `npm run build`.

## Rules

- Human review is recorded only when a named person did it. Source transcription is not reproduction.
- A review that finds nothing to change is a valid result; record it in the dated review.
- Do not regenerate a receipt to clear a validation failure without re-checking what changed.
