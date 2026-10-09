# Use cases moved into the record store, 2026-10-09

Issue #42, use-case stage. `batch.jsonl` holds 126 records written by `npm run use-cases:migrate -- data/omics/use-case-records-20261009` from `data/omics/use-cases/inputs.json` as it stood on `main` at the start of this branch:

- 26 `use_case` records, one per use case, with the same IDs. Every field of the old entry is kept. Citations become `source_ids` plus `citation_locators`, and the review becomes a record review whose `reviewer_note` keeps the original free-text actor verbatim. Each use case links `assessed_by` every protocol it was mapped to.
- 100 relevance judgement claims, one per mapping, with the mapping's ID. Each keeps relevance, endpoint, rationale, constraints, limitations, revision, reason, citations and review, adds `pins` computed against the store at migration time, and lists in `excluded_evaluations` the evaluations on its protocol that the mapping did not include. Only two mappings excluded any (`use-case-mapping-20260930-339-25925e279972`: 3; `use-case-mapping-20260930-349-1af09c2e0e0f`: 2).

Mappings that were `active` become `source_checked` claims; drafts become `needs_review` claims. No mapping was withdrawn or superseded, so there are no tombstones.

`inputs.json` and `sources.json` are retired. The four documentation source records were already in the store. `review.json` now binds only the four source files.

## Round trip

`deriveUseCaseInputs` applied to the store after the batch gives back the old inputs exactly: 26 of 26 use cases identical, and 100 of 100 mappings identical in every field, including `evidence_sha256`. Only the order of `evaluation_ids` differs, because derived lists are sorted. The release built from records has 26 use cases, 97 active mappings and 3 drafts, as before.

No scientific record, value or source changed.
