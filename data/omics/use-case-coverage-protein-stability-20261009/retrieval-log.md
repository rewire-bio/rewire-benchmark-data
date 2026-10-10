# Retrieval log: protein variant stability use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Each download went to its own scratch folder and was opened as data (JATS XML parse). Scripts ran with `python3 -I` from outside the download folders. No predictor was run.

| Time (UTC) | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 21:00:42 | `GET europepmc/.../PMC8921618/fullTextXML` | 200 | 136,014 | Pancotti et al. 2022 pinned |
| 21:00:43 | `GET .../PMC9155634/fullTextXML` | 200 | 164,888 | Homology-model study screened (excluded) |
| 21:00:44 | `GET .../PMC10742815/fullTextXML` | 200 | 109,334 | Birolo et al. 2023 screened (lead) |
| 21:01:06 | `GET .../PMC10861915/fullTextXML` | 200 | | Dieckhaus et al. 2024 pinned |
| 21:01:07 | `GET .../PMC12830971`, `PMC12967566` `/fullTextXML` | 200 | | Screened (figure-level results) |
| 21:01:08 | `GET .../PMC11293664/fullTextXML` | 200 | | Chu et al. 2024 pinned |

No supplementary files were downloaded: every value extracted is in a main-text table.

## How each table was read

All three tables come from the pinned JATS XML, parsed by `extract/extract_protein_stability.py`.

- **Pancotti et al. 2022, Table 1** (`table-wrap` `TB1`): the script asserts the caption, the two header rows, the group rows `Structure-based` and `Sequence-based`, the 15 structure-based and 6 sequence-based method labels in order, and 12 fields per data row. Each row yields 11 results: Pearson r, RMSE and MAE for all, direct and reverse variants, plus the antisymmetry correlation and bias. Printed minus signs are en dashes; `printed_value` keeps them and `numeric_value` uses a hyphen.
- **Dieckhaus et al. 2024, Tables 2 and 3** (`t02`, `t03`): the script asserts both captions, both header rows, the 12 row labels of Table 2 and the footnote text of each table. Footnote markers are stripped from `printed_value`, kept in `printed_source_cell`, and their meaning is recorded in `source_warnings`. Reference numbers in Table 3 row labels are recorded on the evaluation as a limitation, and those rows have origin `paper_compilation`. Empty RMSE cells (ABYSSAL) are skipped.
- **Chu et al. 2024, Tables 1 and 2** (`pcbi.1012248.t001`, `t002`): the script asserts the caption, both header rows and the seven method columns, and reads Table 2 for each dataset's protein, length, measured quantity and sequence count, which become the dataset records.

Run: `python3 -I extract/extract_protein_stability.py <pinned-dir> <batch-dir>` with the decompressed `artifacts/*.gz`.

## Dry run

`addBatch` from `scripts/omics/records.ts` with `npx tsx`, run from this worktree (with the antisymmetry-bias vocabulary addition) against a scratch copy of the store, added all 651 records. SHACL not run.
