# Retrieval log: DNA pathogen-identification use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Each download went into its own folder in a session scratch directory and was opened only as data (XML parse, XLSX cell XML parse, DOCX text parse, `pdftotext`). No classifier, pipeline or model was executed.

Times are UTC. All requests are Europe PMC REST (`https://www.ebi.ac.uk/europepmc/webservices/rest/...`) and all returned HTTP 200.

| Time | Request | Bytes | Result |
| --- | --- | --- | --- |
| 19:45:04 | `PMC9749362/fullTextXML` | 213,192 | Portik et al. 2022. Extracted (Table 4) |
| 19:45:04 | `PMC9676057/fullTextXML` | 156,729 | Govender and Eyre 2022. Screened |
| 19:45:04 | `PMC10794705/fullTextXML` | 261,057 | Valencia et al. 2024. Screened |
| 19:45:05 | `PMC11316826/fullTextXML` | 214,537 | Van Uffelen et al. 2024. Screened |
| 19:45:30 | `PMC9676057/supplementaryFiles` | 848,068 | Supplementary PDF (table legends, figures) and XLSX. PDF read with `pdftotext`; tables are model predictions |
| 19:46:07 | `PMC10803466/fullTextXML` | 121,964 | Lao et al. 2024. Screened |
| 19:46:13 | `PMC10803466/supplementaryFiles` | 705,074 | Supplementary Tables 1-7 (XLSX). Per-sample results; no per-pipeline accuracy table |
| 19:48:47 | `PMC8880012/fullTextXML` | 148,163 | Peterson et al. 2022. Screened |
| 19:48:48 | `PMC12705909/fullTextXML` | 73,625 | Song et al. 2025. Extracted (Tables 1 and 2) |
| 19:49:00 | `PMC8880012/supplementaryFiles` | 1,767,820 | Datasets 1-4 and figures. Dataset 2 (accuracy) covers KAT-SECT only |
| 19:49:22 | `PMC12705909/supplementaryFiles` | 281,870 | One DOCX holding the Figure S1 legend only |
| 19:50:13 | `PMC6805339/fullTextXML`, `PMC7523627/fullTextXML` | 139,954; 47,230 | SEPATH (figure-only); McArdle and Kaforou (metadata only) |
| 19:50:38 | `PMC6897419/fullTextXML`, `PMC9026403/fullTextXML` | 179,926; 55,142 | Watts et al. 2019; Buffet-Bataillon et al. 2022. Screened |
| 19:51:17 | `PMC7993542/fullTextXML` | 69,777 | BugSeq paper. Screened |
| 19:51:32 | `PMC9007738/fullTextXML` | 219,228 | CAMI II. Pathogen challenge paragraphs read |
| 19:55:15 | `PMC10993716/fullTextXML` | 138,900 | Hall and Coin 2024. Extracted (Tables 5-8) |

Metadata (DOI, licence, authors, abstract) for each candidate came from the Europe PMC `search?query=PMCID:...&resultType=core` endpoint at the same times. No request failed. Nothing was retrieved from publisher websites.

## How each table was read

`extract/extract_pathogen.py` parses each `<table-wrap>` from the pinned XML into a grid with `rowspan` and `colspan` expanded, then asserts every label it relies on before writing a record. A failed assertion stops the run.

- **Portik Table 4** (`table-wrap id="Tab4"`): asserts the caption, the 11 header labels, the footnote's first sentence, 70 body rows, the dataset label at the start of each of the six blocks (the first block's label is split across two cells, `HiFi ATCC MSA1003` and `(20 species, staggered)`, and both are asserted), each row's method label in order, and which rows of the HiFi Zymo D6331 block carry the asterisk. Locators give the table row counting the header as row 1.
- **Song Table 1** (`mbo370158-tbl-0001`): asserts caption, header (`Theoretical`, `Blast`, `Metaphlan`, `RTG`, `Kraken`), the eight species rows, the `η 2` and `p‐value` row labels, the `*` cells in the theoretical column, and the footnote. The p-value cell is stored as `reported_p_value` on the eta squared result.
- **Song Table 2** (`mbo370158-tbl-0002`): asserts caption, header (`Blast`, `Kraken`, `RTG`, `Metaphlan`) and the seven sample rows.
- **Hall Tables 5-8** (`tbl5` to `tbl8`): asserts each caption, the six header labels, the six method rows in order and the footnote. Interval cells must be a value followed by bracketed lower and upper bounds joined by the source's en dash; the interval is stored as a 95% confidence interval with the footnote's Wilson score method noted.

`printed_value` is the cell text exactly as in the XML, including the U+2010 hyphen in Song's E notation (`8.97E‐1`) and thousands separators in Hall's rates (`1,406`). `numeric_value` is the decimal string of the same number. Hall's interval cells keep the whole cell in `printed_source_cell`.

Run: `python3 -I extract/extract_pathogen.py <portik.xml> <song.xml> <hall.xml> <batch-dir>`.

## Checks run after extraction

- Portik Table 4: precision, recall, F1 and F0.5 recomputed from the printed TP, FP and FN for all 70 rows; all 280 agree with the printed two-decimal values within rounding.
- Dry run: `addBatch` from `scripts/omics/records.ts` on a scratch copy of `data/entities`, `data/evidence` and `data/provenance` added 926 records and `loadRecords` accepted the store (30,370 records). `deriveUseCaseInputs` on the result produced 12 draft mappings for the use case alongside the existing Karius mapping. SHACL (`npm run kg:shapes`) was not run.
