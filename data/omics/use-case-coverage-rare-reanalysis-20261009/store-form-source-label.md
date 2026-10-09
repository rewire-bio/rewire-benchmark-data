# Store form: source_label removed

`batch.jsonl` is the reviewed batch and is unchanged, so the receipt in `review.json` still binds the reviewed bytes.

`source_label` is reserved for records renamed through a reviewed `source_identity` (`shared/omics/source-identity.ts`). The store copies of the 48 Demidov et al. Table 1 results below had a label and no identity. The label was a note on which value of the cell the result holds, not a header:

- a: the note ("value outside brackets") is already in `source_locator` word for word, so `source_label` was removed.
- 5: the note ("value in brackets (sex-chromosome subset, table footnote)") moved to `scope_note` word for word, and `source_label` was removed.

No other field and no value changed.

| Record | Rule |
| --- | --- |
| `rare-reanalysis-20261009-result-demidov2024-clincnv-cn-gt4` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-clincnv-cn-gt4-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-clincnv-cn0` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-clincnv-cn0-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-clincnv-cn1` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-clincnv-cn1-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-clincnv-cn2` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-clincnv-cn2-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-clincnv-cn3` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-clincnv-cn3-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-clincnv-cn4` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-clincnv-cn4-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-clincnv-long` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-clincnv-long-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-clincnv-total` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-clincnv-total-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-conifer-cn-gt4` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-conifer-cn-gt4-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-conifer-cn0` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-conifer-cn0-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-conifer-cn1` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-conifer-cn1-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-conifer-cn2` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-conifer-cn2-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-conifer-cn3` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-conifer-cn3-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-conifer-cn4` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-conifer-cn4-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-conifer-long` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-conifer-long-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-conifer-total` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-conifer-total-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-exomedepth-cn-gt4` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-exomedepth-cn-gt4-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-exomedepth-cn0` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-exomedepth-cn0-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-exomedepth-cn1` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-exomedepth-cn1-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-exomedepth-cn2` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-exomedepth-cn2-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-exomedepth-cn3` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-exomedepth-cn3-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-exomedepth-cn4` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-exomedepth-cn4-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-exomedepth-long` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-exomedepth-long-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-exomedepth-total` | a: note already in source_locator word for word, source_label removed |
| `rare-reanalysis-20261009-result-demidov2024-exomedepth-total-sex-chromosomes` | 5: note moved to scope_note word for word, source_label removed |
