# Store form: source_label removed from 13 records, 2026-10-09

The release build refused these records: `source_label` is reserved for records renamed through a reviewed `source_identity` (shared/omics/source-identity.ts), and these 13 had a label but no identity. In each, `source_label` repeated `reported_name` exactly, so it was removed and `reported_name` keeps the printed name. No other field changed and no value changed. `batch.jsonl` and `review.json` are unchanged, as reviewed.

Records: see the provenance `records:change` steps that cite this file.
