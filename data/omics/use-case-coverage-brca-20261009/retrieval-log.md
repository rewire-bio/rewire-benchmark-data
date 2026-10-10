# Retrieval log: BRCA1/BRCA2 germline interpretation use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Each download went to its own scratch folder and was opened as data (JATS XML parse, XLSX cell XML parse). Scripts ran with `python3 -I` from outside the download folders. No predictor was run.

| Time (UTC) | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 21:17:53 | Europe PMC search, queries 1 and 2 | 200 | | 272 and 2 hits |
| 21:18:04 | `GET europepmc/.../PMC8553612/fullTextXML` | 200 | 136,559 | Cubuk et al. 2021 pinned |
| 21:18:06 | `GET .../PMC12120176/fullTextXML` | 200 | 112,728 | Ramadane-Morchadi et al. 2025 pinned |
| 21:18:06 | `GET .../PMC5870501/fullTextXML` | 200 | 98,138 | Ernst et al. 2018 screened (excluded) |
| 21:18:06 | `GET .../PMC13282463/fullTextXML` | 200 | 180,432 | Hum Mutat 2026 panel study screened (excluded) |
| 21:18:15 | `GET static-content.springer.com/.../41436_2021_1265_MOESM3_ESM.xlsx` | 200 | 260,899 | Cubuk supplementary tables pinned |

## How each table was read

All values are parsed by `extract/extract_brca.py`; the workbook is read with `extract/rawxlsx.py`, which returns stored cell text without number formatting.

- **Cubuk et al. 2021, Supplementary Tables 3, 5, 6, 7 and 9**: the script asserts the sheet names; the Table 7 definitions of the positive likelihood ratio (TPR/FPR) and the negative likelihood ratio (TNR/FNR); the Table 3 BRCA1 and BRCA2 truth-set counts (371 and 1,270; 64 and 124); the Table 9 headers of columns F to I; that the 84 tool labels of Tables 6 and 9 are the same set; and, for every row and gene, that TP + FN and FP + TN equal the printed totals. Table 5 labels differ in spelling from Tables 6 and 9 and are mapped explicitly. Each Table 9 cell prints `value (lower-upper)`; leading zeros are often missing (`.819`) and some values end in a point (`116.`); `printed_value` keeps the text and `numeric_value` normalises it.
- **Ramadane-Morchadi et al. 2025, Tables 1 and 2** (`tbl1`, `tbl2`): the script asserts both captions, the header rows, the footnotes, the four tool groups and their row spans in Table 1, and the group header rows in Table 2. Footnote letters are stripped from thresholds. Minus signs are U+2212 and are normalised in `numeric_value` only. Table 3 (breast cancer odds ratios) is not read.

Rebuild: decompress `artifacts/*.gz` into one folder and run `python3 -I extract/extract_brca.py <folder> <batch-dir>`. A rebuild from the archived copies gave byte-identical `batch.jsonl` and `claims.csv`.

## Checks

- A separate stdlib checker (not importing the extractor) read every result's locator, opened the named workbook cell or JATS table cell, and compared the printed value: 558 of 558 matched.
- `addBatch` from `scripts/omics/records.ts`, run with `tsx` against a scratch copy of this worktree's store and vocabulary, after loading the somatic oncogenicity and protein stability batches (and the antisymmetry-bias concept they need), added all 862 records. Without those two batches it fails on the first link to an unmerged method, as expected. SHACL not run.
- `deriveUseCaseInputs` on the same scratch store with the four proposed `assessed_by` links: the four new judgements are drafts (84, 84, 8 and 6 evaluations) and all ten existing judgements stay active.
