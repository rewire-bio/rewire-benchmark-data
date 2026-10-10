# Retrieval log: NeuSomatic SEQC2 follow-up, 2026-10-10

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Each download went to its own scratch folder and was opened as data (JATS XML parse; PDF text through poppler `pdftotext`). Scripts ran with `python3 -I` from outside the download folders. No caller was run.

| Time (UTC) | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 06:04:05 | Europe PMC search, title query | 200 | | 1 hit, PMC8740374 |
| 06:04:11 | `GET europepmc/.../PMC8740374/fullTextXML` | 200 | 104,884 | Article pinned |
| 06:04:16 | `GET static-content.springer.com/.../13059_2021_2592_MOESM2_ESM.pdf` | 200 | 172,578 | Additional file 2 pinned |

## How the tables were read

The PDF has a text layer. Its column headers are rotated, so `pdftotext -layout` prints them out of column order. `extract/pdftables.py` reads `pdftotext -bbox` word boxes instead (poppler 26.08.0):

- For each of Tables S2, S3 and S4 it takes the words between the table title and the next title, and fixes 17 columns at the x-centres of the numbers in the first data row.
- Each rotated header word (VarDict, SomaticSniper, MuSE, DRAGEN, Octopus-RF, Octopus-hard, MuTect2, Lancet, Strelka2 and the four model names) is assigned to the nearest column, within 8 points. Model columns left of the 'NeuSomatic' group label belong to 'NeuSomatic-S'. Every column must get exactly one header.
- Data rows are lines whose first word is a sample label (WGS_, SPP_, LBP_) or 'Average'; each must have 17 cells, each within 6 points of a column. Rows are assigned to the SNVs or INDELs section by the nearest section label above them.

Checks in the extractor: the table titles match the layout text; both sections have the same row labels; SomaticSniper and MuSE are '-' throughout the indel sections and nowhere else; and for every column of every section the mean of the rows matches the printed Average to 0.05. Column identity was also checked against the article prose: the Table S2 averages for NeuSomatic SEQC-WGS-GT50-SpikeWGS10 (94.6 SNV, 87.9 indel) match Results 'WGS dataset', and the Table S4 indel averages give the order DRAGEN, Lancet, Octopus-RF, NeuSomatic stated in Results 'Library preparation and DNA input'.

Rebuild: decompress `artifacts/*.gz` into one folder and run `python3 -I extract/extract_neusomatic.py <folder> <batch-dir>` with poppler on the path. A rebuild from the archived copies gave byte-identical `batch.jsonl` and `claims.csv`.

## Checks

- A separate checker (not importing the extractor) read the `pdftotext -layout` text, where numbers in a row line keep column order, and compared all 2,464 results by table, section, row and column: 0 mismatches over 154 rows.
- `addBatch` from `scripts/omics/records.ts`, run with `tsx` against a scratch copy of this worktree's store and vocabulary, added all 2,595 records. SHACL not run.
- `deriveUseCaseInputs` on the scratch store with the six proposed `assessed_by` links: the six new judgements are drafts (17, 15, 17, 15, 17 and 15 evaluations) and all 16 existing judgements stay active.
