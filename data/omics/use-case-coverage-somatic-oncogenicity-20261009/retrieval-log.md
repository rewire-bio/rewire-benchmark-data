# Retrieval log: somatic small-variant oncogenicity use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Every download went to its own scratch folder and was opened as data (XML, XLSX cell XML, TSV and HTML text). Scripts ran with `python3 -I` from outside the download folders. No predictor was run.

| Time (UTC) | Request | HTTP | Result |
| --- | --- | --- | --- |
| 20:45:50 | `GET europepmc/.../PMC7033911/fullTextXML` (with PMC12474978, PMC13282463) | 200 | Chen et al. 2020 pinned; two screened |
| 20:46:04 to 20:47:19 | `GET static-content.springer.com/.../13059_2020_1954_MOESM{1,5,7,9,10,13,14,17,20,21,22}_ESM.*` | 200 | Additional files 1, 9, 10, 21, 22 pinned; 5, 13, 14, 17 and the AUC PDFs 7 and 20 screened only |
| 20:46:49 | `GET static-content.springer.com/.../41467_2025_63461_MOESM1_ESM.pdf` | 200 | Tran et al. 2025 supplement screened |
| 20:48:19 | `GET www.biorxiv.org/content/10.64898/2026.07.16.739080v1.full` | 200 | Preprint HTML pinned |
| 20:48:40 | `gh api repos/tjdrnjsqpf/oncocal` (repository, commits, tree) | 200 | Commit pinned |
| 20:48:49 | `GET raw.githubusercontent.com/tjdrnjsqpf/oncocal/40b7770f.../tables/tool_performance.tsv` | 200 | Table pinned |
| 20:49:13 | `GET www.biorxiv.org/.../2026.07.16.739080.full.pdf` | 429 | Rate limited; not retried |

## How each table was read

- **Chen et al. 2020, Additional files 9, 10, 21 and 22**: XLSX cell XML via `extract/rawxlsx.py`. The script asserts the single sheet name, the six headers, the row count (33 or 17) and that every algorithm label appears in article Table 1. Each cell prints `mean (lower-upper)`; the regular expression `^\d\.\d\d \(\d\.\d\d-\d\.\d\d\)$` must match, the mean becomes `printed_value` and the range goes into `uncertainty`; the raw cell is kept in `printed_source_cell`. Additional file 1 supplies the default positive and negative categories.
- **Lee 2026, tool_performance.tsv**: split on tabs; the script asserts the header, 147 rows, 49 tools in each of the groups `all`, `oncogene` and `TSG`. `n` and `pos` become the evaluation `denominator` and `positive_count`. One sentence of the preprint ("Across all 49 tools, 42 (86%) achieved a lower AUROC for oncogene") is asserted against the pinned HTML; the table itself gives 42 of 49.

Run: `python3 -I extract/extract_somatic_oncogenicity.py <pinned-dir> <batch-dir>` with the decompressed `artifacts/*.gz`.

## Dry run

`addBatch` from `scripts/omics/records.ts` with `npx tsx`, run from this worktree (with the NPV vocabulary addition) against a scratch copy of the store, added all 1,193 records. SHACL not run.
