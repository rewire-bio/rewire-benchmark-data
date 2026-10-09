# Retrieval log: splicing follow-up use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Downloads went to a session scratch directory, one folder per artifact, and were opened as data (XML parse, XLSX cell XML parse, PDF text layer). No tool or model was executed.

Times are UTC request starts.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 20:49:26 | `GET europepmc/webservices/rest/PMC10734170/fullTextXML` | 200 | 206,841 | Smith and Kitzman article XML |
| 20:49:34 | `GET .../PMC10734170/supplementaryFiles` | 200 | 69,513,450 | Zip with Additional files 1-5 (MOESM1 PDF, MOESM2-4 xlsx, MOESM5 docx) and figures |
| 20:51:12 | `GET .../PMC13495316/fullTextXML` | 200 | 139,459 | Genome Biol 2026 distillation paper (screened; tables only in Additional file 1) |
| 20:51:28 | `GET .../PMC6744318/fullTextXML` | 500 | 150 | CAGI5 splicing assessment |
| 20:51:35 | `GET eutils efetch db=pmc id=6744318` | 200 | 136,683 | CAGI5 author manuscript XML with Tables 1-4C (screened, not extracted) |
| 20:52:02 | `GET .../PMC8360004/fullTextXML` | 200 | 185,439 | Riepe et al. article XML |
| 20:52:03 | `GET https://doi.org/10.64898/2026.07.21.739871` | 200 | 91,879 | Redirect to the bioRxiv landing page (v1); licence CC BY 4.0 |
| 20:52:21 | `GET biorxiv.org/content/biorxiv/early/2026/07/26/2026.07.21.739871.full.pdf` | 200 | 424,898 | Znabu et al. preprint PDF, 9 pages |

## How each table was read

- **Smith and Kitzman Additional file 3 (Table S2), sheet 'Sensitivity 10% SDV'**: parsed from the XLSX cell XML by `extract/rawxlsx.py`. `extract/extract_splicing_follow_up.py` asserts the six dataset headers in B1:G1 and the 32 row labels (8 tools by 4 variant classes). Every non-blank cell (166) is extracted. Blank cells (HAL intronic rows; FAS intronic cells) are not results. The 10% thresholds from sheet 'Thresholds' column C, with its headers and tool labels asserted, are recorded in each configuration's `parameters`.
- **Riepe et al. Tables 3, 4 and 5**: parsed from the article XML (`humu24212-tbl-0003` to `-0005`). Asserts each caption, the 12 column headers and the tool labels in order (11, 9 and 11 rows). All 341 value cells are extracted.
- **Znabu et al. Results table** (page 3, unnumbered): read from the PDF text layer with `pdftotext -layout`. Asserts the single header line `predictor n AUROC AP AP 95% CI`, the five row labels in order, and the footnote naming 1,000-sample bootstraps. 15 values are extracted; each AP interval is stored as the AP result's uncertainty.

`printed_value` for XLSX cells is the shortest decimal that round-trips to the stored double; `raw_xml_value` keeps the stored text. Article and PDF values are kept as printed.

Run: `python3 -I extract/extract_splicing_follow_up.py <download-dir> <batch-dir>`, with `PMC10734170/fulltext.xml`, `PMC10734170/supp.zip`, `PMC10734170/supp/13059_2023_3144_MOESM3_ESM.xlsx`, `PMC8360004/fulltext.xml` and `znabu2026/preprint.pdf` under the download directory. Requires `pdftotext` (poppler).
