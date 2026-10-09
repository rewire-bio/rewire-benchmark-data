# Retrieval log: rare-disease reanalysis use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Each download went into its own folder in a session scratch directory and was opened only as data (XML parse, XLSX cell XML parse, `pdftotext`). No reanalysis tool was executed.

Times are UTC request starts. All requests went to the Europe PMC REST API unless the table says otherwise.

| Time | Request | Status | Bytes | Result |
| --- | --- | --- | --- | --- |
| 20:36:38 | `PMC11655964/fullTextXML` | 200 | 42,890 | Vestito et al. 2024 article XML. Extracted |
| 20:36:47 | `PMC11655964/supplementaryFiles` | 200 | 116,881 | Bundle holding `41525_2024_456_MOESM1_ESM.pdf` (Supplementary Table 1). Extracted |
| 20:37:57 | `api.biorxiv.org/details/medrxiv/10.64898/2026.05.16.26352295` | 200 | | Kaschta et al. 2026 version 1 metadata (licence "cc_no") and JATS URL |
| 20:38:04 | `medrxiv.org/content/early/2026/05/19/2026.05.16.26352295.source.xml` | 200 | 108,323 | Kaschta et al. JATS XML. Read, not extracted |
| 20:38:26 | `medrxiv.org/.../2026.05.16.26352295/DC1/embed/media-1.xlsx` | 200 | 174,339 | Per-patient supplement. Headers inspected, then deleted from scratch |
| 20:38:44 | `medrxiv.org/content/early/2021/01/04/2020.12.29.20248974.source.xml` | 200 | 107,552 | AMELIE 3 JATS XML. Tables are images |
| 20:38:57 | `PMC13472938/fullTextXML`, `PMC12258758/fullTextXML` | 200, 200 | 189,457; 145,395 | Talos article and preprint. Section titles read for locators only |
| 20:39:32 | `PMC9950798/fullTextXML`, `PMC11221788/fullTextXML` | 500, 500 | 150; 151 | Metadata showed both are ranking studies (retinal-disease tool benchmark, AI-MARRVEL), not the Moon reanalysis study |
| 20:40:03 | `PMC8795168/fullTextXML` | 200 | 102,341 | Romero et al. 2022. Screened |
| 20:40:13 | `PMC11513043/fullTextXML` | 200 | 426,796 | Demidov et al. 2024 article XML. Extracted |
| 20:40:14 | `PMC10853235/fullTextXML`, `PMC11835725/fullTextXML` | 200, 200 | 117,996; 321,174 | MEI benchmark and Solve-RD Nature Medicine 2025. Screened |
| 20:40:40 | `PMC11513043/supplementaryFiles` | 200 | 2,117,416 | Bundle holding `41525_2024_436_MOESM1_ESM.pdf`. Extracted |
| 20:44:36 | `static-content.springer.com/.../41591_2024_3420_MOESM3_ESM.xlsx` | 200 | 929,914 | Solve-RD Nature Medicine supplementary tables. Sheet headers inspected, then deleted from scratch |

Metadata for each PMC article came from `search?query=PMCID:...&resultType=core` at the same time as the full text.

## How each table was read

`extract/extract_rare_reanalysis.py` asserts every label it relies on before writing a record; a failed assertion stops the run.

- **Demidov et al. Table 1** (`table-wrap id="Tab1"`, rowspans and colspans expanded): asserts the caption, the footnote ("Numbers in brackets denote the subset of calls detected on sex chromosomes."), the header row (Tool, Long, 0, 1, 2, 3, 4, >4, Total) and the five row labels. Each cell must match `count (count)`; the outside value is stored as all chromosomes and the bracketed value as sex chromosomes, both with the full printed cell as `printed_value` and a `source_label` saying which part was taken.
- **Demidov et al. Supplementary Table 4**: `pdftotext -layout` (poppler 26.08.0) output of the pinned PDF. Asserts the legend line, the heading `Supplementary Table 4`, the first header line and the four row labels. Numbers use `.` for thousands and `,` for decimals; the extractor converts them and asserts that each caller's "All CNVs" equals its Table 1 total.
- **Vestito et al. Supplementary Table 1**: `pdftotext -layout` output. Asserts the header line (Diff human score, Var score, TP, FN, FP, TN, recall, precision, Fscore, F2score), exactly 81 data lines of 10 tokens, that the threshold pairs form the full 9 by 9 grid from 0.1 to 0.9, and that every row has TP + FN = 37 and TP + FN + FP + TN = 1846. Locators give the line number in the pdftotext output and the threshold pair.

`printed_value` is the token as printed (for example `0.837837838`, `1`, `2,782 (469)`, `1.561`). `numeric_value` is the same number as a plain decimal string.

Run: `python3 -I extract/extract_rare_reanalysis.py <download-dir> <batch-dir>`, with the download folders named as in the table above and `pdftotext` on the PATH.

## Checks run after extraction

- Every summary number in `coverage.json` was looked up in the batch or the store.
- Dry run: `addBatch` from `scripts/omics/records.ts` on a scratch copy of `data/entities`, `data/evidence` and `data/provenance` added 904 records, and `loadRecords` then accepted the store (31,275 records). `deriveUseCaseInputs` produced 9 draft mappings for this use case alongside the existing active Talos programme mapping: 3 evaluations for Demidov et al., 81 for Vestito et al., 2 for each Talos stratum and 1 for the Exomiser comparison. SHACL (`npm run kg:shapes`) was not run.
