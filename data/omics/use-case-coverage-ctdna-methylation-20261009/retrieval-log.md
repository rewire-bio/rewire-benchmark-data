# Retrieval log: plasma ctDNA methylation use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Downloads went to a session scratch directory, one folder per source; every file was read as data (XML parse, XLSX cell XML parse, PDF text layer via `pdftotext -layout`). No deconvolution tool or classifier was run.

Times are UTC. Times recorded by the download commands are exact; times marked `~` are approximate, from command order.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| ~19:54:50 | `GET api.biorxiv.org/details/biorxiv/<doi>` for three preprints | 200 | | Versions, licences, abstracts |
| ~19:55:01 | `GET biorxiv.org/content/early/2025/11/27/2025.11.27.688590.source.xml` | 429 | 17 | Cloudflare error 1015; not used |
| ~19:55:14 | `GET europepmc/webservices/rest/PPR1127337/fullTextXML` | 500 | 150 | Not used |
| ~19:55:20 | `GET europepmc.org/api/fulltextRepo?pprId=PPR1127337...` | 403 | 46 | "PDF link has expired"; not used |
| 19:55:30 | `GET biorxiv.org/content/10.1101/2025.11.27.688590v1.full.pdf` | 200 | 7,728,127 | DecoNFlow preprint v1, 34 pages |
| ~19:55:53 | `GET biorxiv.org/content/10.1101/2025.11.27.688590v1.supplementary-material` | 200 | 120,863 | Links to media-1 to media-6 |
| 19:56:00 | `GET .../DC3/embed/media-3.xlsx` | 429 | 17 | Retried at 20:03:05 |
| 19:56:03-08 | `GET .../DC4/media-4.xlsx`, `.../DC5/media-5.xlsx`, `.../DC6/media-6.xlsx` | 200 | 29,806; 23,549; 17,722 | Supplementary Tables 2, 3 and 4 |
| ~19:57:30 | `GET cell.com/cancer-cell/fulltext/S1535-6108(22)00513-X` | 403 | 5,806 | Bot challenge; Jamshidi et al. 2022 not retrieved |
| 19:58:16 | `GET europepmc/webservices/rest/PMC11660681/fullTextXML` | 200 | 289,472 | Sun et al. 2024 article XML |
| 19:58:22 | `GET static-content.springer.com/.../13059_2024_3456_MOESM1_ESM.xlsx` | 200 | 108,268 | Sun et al. Additional file 1 |
| ~19:59-20:01 | `GET europepmc/.../PMC12135323, PMC13639271, PMC11742067, PMC8575022, PMC11379469 /fullTextXML` | 200 | | Screened (tables and supplement lists only) |
| ~20:01:40 | `GET sciencedirect.com/science/article/pii/S153561082200513X` | 403 | 832,805 | Jamshidi et al. 2022 not retrieved |
| ~20:01:56 | `GET pmc.ncbi.nlm.nih.gov/.../btae522_supplementary_data.zip` | 200 | 1,814 | HTML proof-of-work page, not the file |
| ~20:02:10 | `GET pmc-oa-opendata.s3.amazonaws.com/PMC11379469.1/btae522_supplementary_data.zip` | 200 | 1,710,279 | MetDecode supplement (MD5 matches the PMC XML); screened, not extracted |
| 20:03:05 | `GET .../DC3/embed/media-3.xlsx` (retry) | 200 | 25,878 | Supplementary Table 1 |
| ~20:03:30 | `GET europepmc/.../PMC10567114, PMC10417284, PMC9744803 /fullTextXML` | 200 | | Screened |
| 20:03:58 | `GET pmc-oa-opendata.s3.amazonaws.com/PMC10567114.1/elife-89083-supp1.xlsx` | 200 | 280,297 | SPOT-MAS Supplementary file 1 |
| 20:04:09 | `GET europepmc/webservices/rest/PMC10567114/fullTextXML` | 200 | 265,940 | SPOT-MAS article XML; bytes identical to the 20:03:30 copy |

## How each table was read

All three tables were parsed from the XLSX cell XML by `extract/rawxlsx.py` (shared strings resolved, stored values unformatted) inside `extract/extract_ctdna_methylation.py`, which also reads each cell's number format from `xl/styles.xml`. Where a fixed-decimals format applies, `printed_value` is the displayed text (for example `0.0250` under `0.0000`, `0.80` under `0.00_ `) and the format is kept in `workbook_number_format`; otherwise it is the shortest round-trip decimal of the stored value. `raw_xml_value` keeps the stored text.

- **Sun et al. Table S7** (sheet `Table S7 `, trailing space in the sheet name): asserts the title in A1, `AUC values ` in H2, the five method headers in I3:M3 and the six dataset labels in A4:A9 and H4:H9, and that no row lies below row 9. All 30 cells of the AUC block H2:M9 are extracted. The p-value block A2:F9 is not (see `research.md`).
- **Giuili et al. Supplementary Table 3**: asserts the three dataset headers in sheet A row 1, the 14 depth headers in row 2, the ten tool labels in A3:A12, the three footnotes in A13, B16 and B17, the three dataset headers and ten tool labels of sheet B, and the total cell count (170 + 44). All 150 values of sheet A and 30 values of sheet B are extracted; the four text cells `0.0070*` keep their asterisk.
- **Giuili et al. Supplementary Table 1** (sheet 1A): asserts the header and the ten tool labels; read only for the printed version and container of each tool.
- **Nguyen et al. Table S9**: asserts the title, the Discovery and Validation block labels, the five stratum headers and `n`, `RF`, `DNN`, `GCNN` headers in both blocks, the six cancer labels per block, and the total cell count (307). All 180 accuracy cells are extracted; the 60 `n` cells are recorded as each result's `coverage.scored`. Three `N/A` cells (validation lung stage I, n = 0) are kept with `numeric_value` null.
- **Article text**: methods, cohort sizes and definitions were read from the article XML paragraphs (Sun et al., Nguyen et al.) and from the PDF text layer (Giuili et al.). Figure 4A of Giuili et al. was read through its text layer only to check Supplementary Table 3; no value was taken from a figure.
