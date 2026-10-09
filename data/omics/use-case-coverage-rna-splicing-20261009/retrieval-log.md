# Retrieval log: patient-RNA splicing use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Downloads went to a session scratch directory, one folder per artifact; every file was opened as data (XML parse, XLSX cell XML parse, PDF text layer for screening only). No tool, model or caller was executed.

Times are UTC request starts.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 20:30:36 | `GET europepmc/webservices/rest/PMC10716352/fullTextXML` | 500 | 151 | FRASER 2.0 (AJHG 2023); retried 20:30:41 and 20:31:11, same error |
| 20:30:41 | `GET .../PMC12547740/fullTextXML` | 200 | 130,507 | Drost et al. article XML |
| 20:30:42 | `GET .../PMC13170886/fullTextXML` | 200 | 159,910 | PLoS One 2026 SpliceAI-family comparison (screened) |
| 20:30:42 | `GET .../PMC11476204/fullTextXML` | 200 | 199,434 | Genome Med 2024 heart-specific splice model (screened) |
| 20:30:42 | `GET .../PMC13019952/fullTextXML` | 200 | 196,872 | Segers et al. (saseR) article XML |
| 20:30:43 | `GET .../PMC13283436/fullTextXML` | 200 | 260,547 | Brief Bioinform 2026 review (screened) |
| 20:31:22 | `GET eutils efetch db=pmc id=10716352` | 200 | 9,818 | Front matter only: "The publisher of this article does not allow downloading of the full text in XML form." |
| 20:31:22 | `GET .../PMC12790623/fullTextXML` | 200 | not logged | Brief Bioinform 2026 junction-detection paper (screened) |
| 20:31:37 | `GET .../PMC12547740/supplementaryFiles` | 200 | 19,638,616 | Zip with Figures, `mmc1.pdf`, `mmc2.xlsx` (Data S1, Tables S1-S6), `mmc3.pdf` |
| 20:33:28 | `GET .../PMC13019952/supplementaryFiles` | 200 | 4,074,340 | Zip with figures and Additional file 1 PDF |
| 20:33:50 | `GET .../PMC12257123/fullTextXML` | 200 | 175,705 | Segarra-Casas et al. article XML |
| 20:33:50 | `GET .../PMC12891912/fullTextXML`, `.../PMC12105386/fullTextXML` | 200, 200 | not logged | Screened for multi-caller tables |
| about 20:35 | `WebFetch https://www.nature.com/articles/s41588-023-01373-3` | 303 | | Redirect to a Nature login flow; not followed |
| 20:35:40 | `GET nature.com/articles/s41588-023-01373-3.pdf` | 200 | 418,044 | HTML page, not a PDF |
| 20:35:40 | `GET biorxiv.org/.../2022.06.13.495326.full.pdf` | 200 | 1,649,625 | AbSplice preprint PDF (CC BY-NC-ND 4.0); text layer scanned, no tables, per-method values in figures and prose only |

## How each table was read

- **Drost Data S1 Table S3**: parsed from the XLSX cell XML by `extract/rawxlsx.py` (copied from the CNV pass). `extract/extract_rna_splicing.py` asserts the sheet title in B2, the block titles in B4 and F4, the headers in B9:D9 and F6:I6, the dataset labels in G7 and G12, and the four tool labels in each block. All 24 value cells are extracted.
- **Drost Data S1 Table S4**: same parser. Asserts the sheet title, the three block titles (B4, B17, B30), the six metric headers in each header row (6, 19, 32) and the eight row labels per block. All 144 value cells are extracted. Precision and Pos Pred Value columns hold the same numbers; both are kept, distinguished by `metric_qualifier`.
- **Segarra-Casas Table 2**: parsed from the article XML `table-wrap id="acn370078-tbl-0002"`. Asserts the caption, the nine column headers and the 16 case labels in order. All 96 value cells are extracted (5 caller columns and the OUTRIDER column). Bold formatting, which the footnote defines as a correct outlier call, is kept in `printed_source_cell`. OUTRIDER values keep the printed Unicode minus; `numeric_value` uses an ASCII minus.
- **Segers Table 2**: parsed from `table-wrap id="Tab2"`. Asserts the caption, the three header rows and the 12 row labels. All 84 rank cells are extracted.

`printed_value` for XLSX cells is the shortest decimal that round-trips to the stored IEEE double; the stored text is kept in `raw_xml_value`. Workbook display formatting was not applied. Variant labels, case labels and gene labels are asserted, not stored as results.

Run: `python3 -I extract/extract_rna_splicing.py <download-dir> <batch-dir>`, with the download directory laid out as `PMC12547740/fulltext.xml`, `PMC12547740/supp/mmc2.xlsx` (zip unpacked in place), `PMC12547740/supp.zip`, `PMC12257123/fulltext.xml` and `PMC13019952/fulltext.xml`.
