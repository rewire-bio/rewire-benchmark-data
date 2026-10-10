# Retrieval log: regulatory variant and gene follow-up use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Downloads went to a session scratch directory, one folder per artifact, and were opened as data (XML parse, XLSX cell XML parse, DOCX legend parse). No model was executed.

Times are UTC request starts.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 21:03:18 | `GET europepmc/webservices/rest/PMC13471189/fullTextXML` | 200 | 278,941 | Gschwind et al. article XML; supplements listed as `media` elements |
| 21:03:18 | `GET .../PMC13447104/fullTextXML` | 200 | 256,800 | scE2G (Nat Genet 2026), screened |
| 21:03:19 | `GET .../PMC12704523/fullTextXML` | 500 | 151 | Single-cell multiome linking (Nat Genet 2025); not retrieved |
| 21:03:20 | `GET .../PMC12971484/fullTextXML` | 200 | 287,361 | Astrocyte CRISPRi (Nat Neurosci 2026), screened |
| 21:03:46 | `GET .../PMC13012518/fullTextXML` | 200 | 162,335 | CALDERA (PLoS Genet 2026), screened |
| 21:04:07 | `GET .../PMC11416642/fullTextXML` and `.../PMC10836580/fullTextXML` | 200, 500 | 171,194; 151 | HGG Adv 2024 eQTL co-regulation screened; PoPS (Nat Genet 2023) not retrieved |
| 21:04:27 | `GET .../PMC12562713/fullTextXML` | 200 | 157,256 | Manzo et al. article XML |
| 21:04:28 | `GET .../PMC12261763/fullTextXML` | 200 | 210,095 | Tang et al. article XML |
| 21:04:46 | `GET .../PMC13471189/supplementaryFiles` | 200 | 18,004,303 | Zip with MOESM1-2 PDFs and `41586_2026_10781_MOESM3_ESM.zip` (Supplementary Tables 1-19 and a legends docx) |

## How each table was read

- **Gschwind Supplementary Table 3, sheet 'Held-out benchmarks'**: parsed from the XLSX cell XML by `extract/rawxlsx.py`. `extract/extract_regulatory_variant.py` asserts the six headers in A1:F1, that rows 2-37 are the only data rows, and that every Dataset, Predictor and Performance metric label is one of the expected values. All 36 rows are extracted; Lower CI and Upper CI become each result's uncertainty. The legend text comes from `Supplementary_table_legends.docx`.
- **Manzo Table 1**: parsed from `table-wrap id="genes-16-01223-t001"`. Asserts the caption start, the four column headers and the 24 model labels in order. All 96 cells are extracted; the bracketed standard error becomes each result's uncertainty. The printed Unicode minus is kept in `printed_value`.
- **Tang Table 1**: parsed from `table-wrap id="Tab1"`, handling the row-spanning Training task cells. Asserts the caption, the four headers and the 14 task and model pairs in order. All 28 cells are extracted.

`printed_value` for XLSX cells is the shortest decimal that round-trips to the stored double; `raw_xml_value` keeps the stored text.

Run: `python3 -I extract/extract_regulatory_variant.py <download-dir> <batch-dir>` with the layout given in the script docstring.
