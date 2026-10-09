# Retrieval log: diagnostic genomics execution use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Every download went to its own folder in a session scratch directory and was opened as data (XML parse, XLSX cell XML parse, PDF text layer via `pdftotext`). Scripts were kept outside the download folders and run with `python3 -I`. No pipeline or model was executed.

Times are UTC, from `date` output or the saved file's modification time.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 20:20:45 | `GET europepmc/webservices/rest/PMC12092081/fullTextXML` (with PMC9748128, PMC7678823, PMC10230726, PMC12684714) | 200 each | 119,969 (PMC12092081) | Samarakoon et al. 2025 and O'Connell et al. 2023 article XML pinned; others screened |
| 20:21:07 | `GET static-content.springer.com/.../41598_2022_26181_MOESM1_ESM.pdf` | 200 | 1,755,036 | Betschart et al. 2022 supplement (screened) |
| 20:21:08 | `GET static-content.springer.com/.../41598_2020_77218_MOESM2_ESM.xlsx` | 200 | 25,149 | Zhao et al. 2020 supplementary tables (screened) |
| 20:21:2x to 20:25:01 | `GET .../PMC12092081/supplementaryFiles` | 200 | 1,698,865 | Complete zip; `zipfile.testzip()` clean; inner `vbaf085_supplementary_data.zip` pinned |
| 20:22 | `GET .../PMC11044436`, `PMC12875585`, `PMC13023369` `/fullTextXML` | 200 each | | Screened |
| 20:22:39 | `GET .../PMC12627752/fullTextXML` | 200 | 97,631 | Franzoso et al. 2025 article XML pinned |
| 20:22 to 20:23:50 | `GET .../PMC12627752/supplementaryFiles` | 500 | 10,135 | Failed |
| 20:24 | `GET ascpt.onlinelibrary.wiley.com/action/downloadSupplement?...TableS2.xlsx` | 403 | 6,046 | Blocked |
| 20:24 to 20:26:38 | `GET .../PMC12627752/supplementaryFiles` (retry) | 200 | 261,303 | Complete zip; `zipfile.testzip()` clean; Tables S1 and S2 pinned |
| 20:25:40 | `GET qudt.org/vocab/unit/USDollar`, `.../unit/MIN` | 200 | | Labels and types checked for the new unit concepts |

While the Samarakoon supplement was still downloading, its complete first member (`vbaf085_supplementary_data.zip`) was decompressed from the partial file for screening; its CRC-32 matched the data descriptor and its SHA-256 equals the member of the complete zip. No record depends on the partial download.

## How each table was read

- **Samarakoon et al. 2025, Supplementary Tables S1, S3 and S4**: the PDF is taken from the pinned publisher zip (whose only member it is) and converted with `pdftotext -layout` (poppler 26.08.0). `extract/extract_model_execution.py` asserts the table titles, each sub-table heading, the header row `Sample CPU L4 A100 H100 DRAGEN`, the sample label of every row (sub-table c uses a different row order, also asserted), six fields per row, and the sample coverages in Table S1. Form feeds are removed and text is split only on newlines, because Python's `splitlines()` also splits at form feeds. The DRAGEN column of sub-table b.2 prints `NA` throughout and gives no evaluation.
- **O'Connell et al. 2023, Table 1**: parsed from `table-wrap id="Tab1"` in the article XML. The script asserts the caption, footnote, header, 66 body rows, the platform and VM-type sequence of each caller block, and that blank Platform and Variant-caller cells occur only where the table layout carries the label down. Cells printed as a dash or as `_` are not recorded as results.
- **Franzoso et al. 2025, Tables S1 and S2**: parsed from the XLSX cell XML with `extract/rawxlsx.py`. The script asserts the title, headers, sample identifiers (against Table S1) and software labels. Runtime cells use built-in number format 21 (`h:mm:ss`, checked in `xl/styles.xml`); `printed_value` is that rendering and `numeric_value` is seconds. Cost `printed_value` is the shortest round-trip decimal of the stored double.

Run: `python3 -I extract/extract_model_execution.py <pinned-dir> <batch-dir>`, where `<pinned-dir>` holds the decompressed `artifacts/*.gz` under their names without `.gz`. The script checks each SHA-256 before reading and needs `pdftotext` on the path.

## Dry run

`addBatch(batch.jsonl, data/omics/use-case-coverage-model-execution-20261009, <scratch root>)` from `scripts/omics/records.ts`, run with `npx tsx` from this worktree (so with the vocabulary additions) against a scratch copy of `data/entities`, `data/evidence` and `data/provenance`, added all 639 records. The SHACL step of `npm run records -- add` was not run.
