# Retrieval log: rare-disease candidate ranking use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Downloads went to a session scratch directory, one folder per artifact, and were opened as data (XML parse, DOCX table XML parse). No tool or model was executed.

Times are UTC request starts.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 21:18:05 | `GET europepmc/webservices/rest/PMC8921623/fullTextXML` | 200 | 135,371 | Yuan et al. 2022 article XML |
| 21:18:05 | `GET .../PMC13046788/fullTextXML` | 200 | 107,889 | Reese et al. 2026 (EJHG), screened |
| 21:18:05 | `GET .../PMC11929307/fullTextXML` | 200 | 173,548 | PhEval (BMC Bioinformatics 2025), screened |
| 21:18:19 | `GET .../PMC8921623/supplementaryFiles` | 200 | 337,428 | Zip with SM Tables 1-4 (docx and zip) and figures |
| 21:20:19 | `GET .../PMC10838329/fullTextXML` | 200 | 97,963 | Yuan et al. 2024 article XML |
| 21:20:27 | `GET .../PMC12041562/fullTextXML` | 200 | 114,845 | Kafkas et al. 2025 article XML |
| 21:20:28 | `GET .../PMC11480789/fullTextXML` | 200 | 142,711 | Kim et al. 2024 (AJHG), screened |

## How each table was read

- **Yuan 2022 SM Table 3**: parsed from the docx `word/document.xml` by `extract/extract_rare_ranking.py`. Asserts the single table, the caption paragraph 'SM Table 3 Accuracy in each top level experiments of each method', the header row, the DDD and KMCGD labels and the 11 method labels in each block. All 154 cells are extracted.
- **Yuan 2024 Table 1**: parsed from `table-wrap id="Tab1"`, resolving row-spanning cohort and prioritizer cells by position. Asserts the caption, the 10 headers and the exact sequence of 26 (cohort, prioritizer, protocol) rows. All 182 cells are extracted.
- **Kafkas 2025 Table 3**: parsed from `table-wrap id="Tab3"`. Asserts the caption, the three header rows and the 20 (size, metric) rows in order. All 160 cells are extracted.

Values are kept as printed. Run: `python3 -I extract/extract_rare_ranking.py <download-dir> <batch-dir>` with the layout given in the script docstring.
