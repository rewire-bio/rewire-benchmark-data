# Retrieval log: CNV detection use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Downloads went to a session scratch directory; every file was opened as data (XML parse, XLSX cell XML parse, DOCX table parse). No tool, model or caller was executed.

Times are UTC request starts.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 15:21:28 | `GET europepmc/webservices/rest/PMC8699073/supplementaryFiles` | 200 | 1,102,990 | Zip with `cancers-13-06283-s001.zip`; inner zip holds Tables S1-S3, File S1, Figures S1-S2 |
| 15:21:28 | `GET .../PMC8699073/fullTextXML` | 200 | 134,850 | Gabrielaite et al. 2021 article XML |
| 15:24:22 | `GET .../PMC12005901/fullTextXML` and `/supplementaryFiles` | 200, 200 | 84,386; 3,678,183 | De La Vega et al. 2025 XML; zip holding `vbaf071_supplementary_data.zip` (Supplemental Tables 1-3, File 1, Figure 1) |
| 15:25:50 | `GET .../PMC11188507/fullTextXML` and `/supplementaryFiles` | 200, 200 | 119,864; 4,460,490 | SEQC2 somatic CNV paper XML; Additional files 1-6 |
| 15:28:01 | `GET .../PMC10762021/fullTextXML` | 200 | 177,237 | ECOLE (screened, excluded) |
| 15:28:01 | `GET .../PMC8821561/fullTextXML` | 200 | 96,212 | Combining-callers paper, EJHG 2022 (screened; supplement not read) |
| 15:28:02 | `GET .../PMC8277855/fullTextXML` | 200 | 147,450 | Gordeeva et al. 2021 (screened, excluded) |
| 15:28:17 | `GET .../PMC12383524/fullTextXML` | 200 | 125,856 | Nardone et al. 2025 XML |
| 15:28:25 | `GET .../PMC12383524/supplementaryFiles` | 200 | 555,537 | Zip with `biomedicines-13-01949-s001.zip` (Tables S1-S5, Figure S1) |
| 15:29:24 | `GET .../PMC8821561/supplementaryFiles` | 200 | 5,614,483 | One 6 MB supplementary PDF; not opened in this pass |
| 15:30:17 | `GET media.springernature.com/.../41587_2024_2382_MOESM3_ESM.xlsx` | 200 | 168,089 | DRAGEN supplementary tables; SHA-256 matches the stored `original_artifact_sha256` |

Failed: `WebFetch https://www.tempus.com/publications/benchmarking-of-germline-copy-number-variant-callers...` returned HTTP 429. Not needed: the same work was retrieved as the peer-reviewed article PMC12005901. `WebFetch https://genomebiology.biomedcentral.com/articles/10.1186/s13059-024-03294-8` redirected to a Springer login flow; the article was retrieved from Europe PMC instead.

## How each table was read

- **DRAGEN Table S4** (`S4 CNV benchmarking`): parsed from the XLSX cell XML by `extract/rawxlsx.py`. The extractor asserts the sheet title, the three configuration headers in B4, F4 and J4, the metric headers in row 5 and the five row labels in A6-A10. Cell H6 is skipped because it is already stored.
- **De La Vega Supplemental Table 3**: same parser. Asserts the title in A1, the NA footnote in A15, the six group headers in row 3, the DEL/DUP headers in row 4, Sensitivity/Precision in row 5 and the eight caller labels in A6-A13.
- **De La Vega Table 1**: parsed from the article XML `table-wrap id="vbaf071-T1"`; header row and both stub columns asserted.
- **Gabrielaite Table S2**: same XLSX parser. Asserts the 12 column headers and that exactly eight rows have sample `GB-WGS-NA12878` and library `WGS`. Only those rows are extracted (see `research.md`).
- **Nardone Table S1**: same XLSX parser. Asserts the nine column headers in row 4, that rows 5-84 hold ten methods with eight rows each, that every row is `DEL`, and the bin order `50-99` to `ALL`.

`printed_value` is the shortest decimal that round-trips to the stored IEEE double (for example stored `0.82220000000000004` gives `0.8222`). The raw stored text is kept in `source_cell_text`. Display formatting in the spreadsheet was not applied. Text cells (`NA`, `NaN`) are kept as printed with `numeric_value` null.

Run: `python3 -I extract/extract_cnv.py <download-dir> <batch-dir>`. The download directory layout is the one used above (Europe PMC zips unpacked in place).
