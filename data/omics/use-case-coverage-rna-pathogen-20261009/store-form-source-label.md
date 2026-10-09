# Store form: source_label moved on 120 records, 2026-10-09

`source_label` is reserved for records renamed through a reviewed `source_identity` (shared/omics/source-identity.ts); the release build and tests/source-identity-store.test.ts refuse it otherwise. On these 120 records it held reviewed notes about the printed table, which now live in declared fields, word for word:

- 60 Carbo et al. 2022 ROC-distance results: the printed column note moved to `scope_note`.
- 60 evaluations: the printed row rank moved to the end of `source_locator`.

No value and no other field changed. `batch.jsonl` and `review.json` are unchanged, as reviewed.
