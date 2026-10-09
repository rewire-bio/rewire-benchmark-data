# Retrieval log: plasma ctDNA fragmentomics use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Downloads went to a session scratch directory, one folder per source; files were read as data (XML parse, XLSX cell XML parse, PDF text layer). No model or tool was run.

Times are UTC. Times recorded by the download commands are exact; times marked `~` are approximate, from command order.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| ~20:19:45 | `GET europepmc/webservices/rest/PMC12720587/fullTextXML` | 200 | | GigaScience preprocessing study; screened, excluded |
| ~20:20:20 | `GET europepmc/.../PMC11321639, PMC12217890, PMC12948677, PMC12749132, PMC13353424 /fullTextXML` | 200 | | Screening copies (table and supplement lists) |
| 20:20:39 | `GET pmc-oa-opendata.s3.amazonaws.com/PMC11321639.1/ADVS-11-2308243-s001.xlsx` | 200 | 87,411 | Hou et al. Supporting Information workbook |
| ~20:22:20 | `GET europepmc/.../PMC12402995, PMC12100915, PMC12767190 /fullTextXML` | 200 | | Screened |
| 20:22:36 | `GET pmc-oa-opendata.s3.amazonaws.com/PMC12402995.1/pnas.2426890122.sd01-sd08.xlsx` | 200 | | Curtis et al. datasets: per-sample values only; not extracted |
| 20:23:13 | `GET pmc-oa-opendata.s3.amazonaws.com/PMC13353424.1/sciadv.ady9432_sm.pdf` and `..._data_files_s1_and_s2.zip` | 200, 200 | 35,945,869; 7,115,129 | UNITE supplementary text and data files |
| ~20:24:34 | `GET europepmc/.../PMC12597888/fullTextXML`; `GET pmc-oa-opendata.../41467_2025_66503_MOESM5_ESM.csv` | 200, 200 | ; 417,980 | FinaleToolkit and LIONHEART screened |
| 20:27:02 | `GET europepmc/webservices/rest/PMC11321639/fullTextXML` and `/PMC13353424/fullTextXML` | 200, 200 | 171,998; 366,838 | Pinned article copies; bytes identical to the screening copies |

## How each table was read

All parsing is in `extract/extract_ctdna_fragmentomics.py`, using `extract/rawxlsx.py` for workbooks (shared strings resolved, stored values unformatted). Number formats were checked: every extracted workbook cell is General format.

- **Hou et al. Table 1** (article XML `table-wrap id="advs8741-tbl-0001"`): asserts the caption, the four header cells and the eleven row labels. Each cell is parsed as an optional region label, a value and a 95% CI; `/` cells (eight) are not results. 25 results; the full cell text is in `printed_source_cell`.
- **Hou et al. Table S2**: asserts the title, the five headers, the nine group labels in column A at rows 3, 13, ..., 83, the ten pattern labels per group, that column A is empty elsewhere, and the cell count (375). Text cells hold "value (95 CI: lower - upper)"; the leading number is `printed_value`, the CI goes to `uncertainty`, the stored text to `raw_xml_value`. 270 results. Cell E64 lacks its closing bracket; this is noted on that result.
- **Hou et al. Table S3**: asserts the title, headers, the three data-set labels and ten pattern labels per data set, and the cell count (156). Numeric cells; `printed_value` is the shortest round-trip decimal. 90 results.
- **Hou et al. Table S9**: read only to check Table S2 (see the evidence concern); not extracted.
- **UNITE Data file S2, sheets STATS_xgb_x1-x6 and STATS_lr**: asserts the Table of Contents descriptions of both sheets, the ten column headers, the sheet extents (145 and 65 rows), and that every row's stratum, feature and metric label is one of the expected values. One result per row: column D (mean) is the value, G and H the 95% CI, and E, F, I, J (median, sd, sem bounds) are kept in `source_cells`. 208 results.
- **Article text**: dataset sizes, classifiers and validation designs were read from the article XML paragraphs cited in each record's locator.
