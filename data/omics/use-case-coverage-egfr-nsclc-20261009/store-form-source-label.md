# Store form: source_label and source_identity

`batch.jsonl` is the reviewed batch and is unchanged, so the receipt in `review.json` still binds the reviewed bytes.

`source_label` and `source_identity` are reserved for records renamed through a reviewed `source_identity` with a display name (`shared/omics/source-identity.ts`). The 14 TREC 2020 Precision Medicine run configurations below used `source_identity` for run provenance instead. Their store copies were changed under these rules:

1. `source_label` equalled `reported_name`, which keeps the run ID, so it was removed.
2. `source_label` was the run name as printed in the overview table rows, with spaces for underscores. It was appended to `source_locator` as `; row '<label>'` and removed.
4. The run provenance in `source_identity` moved to `model_identity_note` as `Run provenance: run_id <run_id>; run_file_md5 <md5>; listed_in <listed_in>`, with every key and value kept word for word and in order, and `source_identity` was removed. Each value was checked against the old object before writing.

No other field and no value changed.

| Record | Rules |
| --- | --- |
| `egfrnsclc-20261009-config-trec2020-pm-baseline` | 4: run provenance moved from source_identity to model_identity_note; 1: source_label equals reported_name, removed |
| `egfrnsclc-20261009-config-trec2020-pm-bm25` | 4: run provenance moved from source_identity to model_identity_note; 1: source_label equals reported_name, removed |
| `egfrnsclc-20261009-config-trec2020-pm-csiromed-strrr` | 4: run provenance moved from source_identity to model_identity_note; 2: appended row 'CSIROmed strRR' to source_locator, source_label removed |
| `egfrnsclc-20261009-config-trec2020-pm-damoespcbh3` | 4: run provenance moved from source_identity to model_identity_note; 1: source_label equals reported_name, removed |
| `egfrnsclc-20261009-config-trec2020-pm-duot5` | 4: run provenance moved from source_identity to model_identity_note; 1: source_label equals reported_name, removed |
| `egfrnsclc-20261009-config-trec2020-pm-monot5` | 4: run provenance moved from source_identity to model_identity_note; 1: source_label equals reported_name, removed |
| `egfrnsclc-20261009-config-trec2020-pm-monot5rct` | 4: run provenance moved from source_identity to model_identity_note; 1: source_label equals reported_name, removed |
| `egfrnsclc-20261009-config-trec2020-pm-pozbaseline` | 4: run provenance moved from source_identity to model_identity_note; 1: source_label equals reported_name, removed |
| `egfrnsclc-20261009-config-trec2020-pm-r1st` | 4: run provenance moved from source_identity to model_identity_note; 1: source_label equals reported_name, removed |
| `egfrnsclc-20261009-config-trec2020-pm-rrf` | 4: run provenance moved from source_identity to model_identity_note; 1: source_label equals reported_name, removed |
| `egfrnsclc-20261009-config-trec2020-pm-rrf-prf-rprec` | 4: run provenance moved from source_identity to model_identity_note; 2: appended row 'rrf prf rprec' to source_locator, source_label removed |
| `egfrnsclc-20261009-config-trec2020-pm-sibtm-run1` | 4: run provenance moved from source_identity to model_identity_note; 2: appended row 'sibtm run1' to source_locator, source_label removed |
| `egfrnsclc-20261009-config-trec2020-pm-uog-ufmg-sb-df5` | 4: run provenance moved from source_identity to model_identity_note; 2: appended row 'uog ufmg sb df5' to source_locator, source_label removed |
| `egfrnsclc-20261009-config-trec2020-pm-uwman` | 4: run provenance moved from source_identity to model_identity_note; 1: source_label equals reported_name, removed |
