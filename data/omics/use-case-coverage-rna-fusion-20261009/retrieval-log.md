# Retrieval log: tumour RNA fusion detection use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Every download went to its own folder in a session scratch directory and was opened as data (XML parse, PDF text layer via `pdftotext`). Scripts were kept outside the download folders and run with `python3 -I`. No caller was executed.

| Time (UTC) | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 20:37:17 | `GET europepmc/webservices/rest/PMC13230599/fullTextXML` (with PMC12047241) | 200, 200 | 130,845; 228,760 | Tamura et al. 2026 pinned; CTAT-LR-Fusion screened |
| 20:37:2x | `GET .../PMC6802306/fullTextXML` | 200 | 176,473 | Haas et al. 2019 screened |
| 20:37:37 | `GET static-content.springer.com/esm/art%3A10.1038%2Fs41698-026-01397-y/.../41698_2026_1397_MOESM1_ESM.pdf` | 200 | 2,350,048 | Tamura supplementary PDF pinned |
| 20:38:17 | `GET .../PMC8376800/fullTextXML` | 500 | 150 | DREAM SMC-RNA not available |
| 20:38:17 | `GET .../PMC12996614`, `PMC13197905` `/fullTextXML` | 200, 200 | 113,828; 150,754 | Br J Cancer 2026 screened; Lin et al. 2026 pinned |
| 20:38:49 | `GET .../PMC12063385/fullTextXML` | 200 | | BMC Cancer 2025 screened |

## How each table was read

- **Tamura et al. 2026, Supplementary Tables 1, 3 and 5**: `pdftotext -layout` (poppler 26.08.0) on the pinned PDF. `extract/extract_rna_fusion.py` asserts each table title, the sub-table headings 'Conventional RNA-seq of cell lines' and 'Targeted RNA-seq of cell lines', the header words, the 12 algorithm labels in order and the field count of each row, and the footnote defining 'na'. In Table 1 the aligner and parameter columns run together in the text layer for two rows; the script splits off the trailing 'Default' or 'Recommended' and asserts it. Form feeds are removed and text is split only on newlines. The per-algorithm truth-set size in Table 3 is stored as the evaluation `denominator` and listed in `claims.csv`.
- **Lin et al. 2026, Tables 3, 5 and 6**: parsed from `table-wrap` `tbl3`, `tbl5` and `tbl6` in the article XML, with captions, headers and the four algorithm labels asserted. Table 5 (runtime and memory) is a descriptive claim, not results.

Run: `python3 -I extract/extract_rna_fusion.py <pinned-dir> <batch-dir>`, with the three artifacts under the names in `ARTIFACTS`; the script checks each SHA-256 and needs `pdftotext` on the path.

## Dry run

`addBatch(batch.jsonl, data/omics/use-case-coverage-rna-fusion-20261009, <scratch root>)` from `scripts/omics/records.ts` with `npx tsx`, against a scratch copy of `data/entities`, `data/evidence` and `data/provenance`, added all 424 records. The SHACL step was not run.
