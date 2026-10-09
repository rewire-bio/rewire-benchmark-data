# Retrieval log: tumour somatic SNV and indel use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Every download went to its own folder in a session scratch directory and was opened as data (XML parse, XLSX cell XML parse, BIFF8 record parse, DOCX text parse). Scripts were kept outside the download folders and run with `python3 -I`. No caller, model or pipeline was executed.

Times are UTC. Where no `date` output was captured, the time is the file modification time of the saved response.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 19:55:07 | `GET europepmc/webservices/rest/PMC9705725/fullTextXML` | 200 | 62,255 | FANSe pipeline comparison (screened, lead) |
| 19:55:30 | `GET .../PMC8506910/fullTextXML` | 500 | 150 | Xiao et al. 2021 not available as open-access XML |
| 19:55:31 | `GET .../PMC11146589/fullTextXML` | 200 | 92,044 | MuSE 2 paper (screened, excluded) |
| 19:56:22 | `GET .../PMC10967217`, `PMC10958848`, `PMC13064521`, `PMC13285312` `/fullTextXML` | 200 each | 34,000 to 120,000 | COSAP (excluded), SEQC2 WES replicates (lead), Lancet2 (lead), VariantMedium (lead) |
| 19:56:52 | `GET .../PMC11790059/fullTextXML` | 200 | 136,573 | Guille et al. 2025 article XML (pinned) |
| 19:56:52 | `GET .../PMC7044309`, `PMC7722876`, `PMC12650410` `/fullTextXML` (same batch as PMC11790059) | 200 each | 80,000 to 109,000 | Screened |
| 19:57:04 | `GET .../PMC11790059/supplementaryFiles` | stalled | 10,301,440 (partial, last byte 20:00:14) | Stopped by hand after the transfer stalled |
| 19:58:30 | `WebFetch researchsquare.com/article/rs-11210923/v1` | 200 | | Only the title was readable |
| 19:59:56 | `GET .../PMC8740374/fullTextXML`, `PMC12852940/fullTextXML` | 200, 200 | 104,884; 142,172 | NeuSomatic SEQC2 2022 (lead), ctDNA benchmark (excluded by scope) |
| 20:00:11 to 20:01:15 | `GET .../PMC13064521/supplementaryFiles` | 500 | 10,135 | Lancet2 supplement not available |
| 20:00:37 | `GET .../PMC7393490/fullTextXML` | 200 | 118,897 | Wang et al. 2020 article XML (pinned) |
| 20:00:53 | `GET .../PMC7393490/supplementaryFiles` | stalled | 69,632 (partial) | Stopped; the publisher copy above was used instead |
| 20:00:59 | `GET static-content.springer.com/esm/art%3A10.1038%2Fs41598-020-69772-8/MediaObjects/41598_2020_69772_MOESM3_ESM.xlsx` | 200 | 131,010 | Wang et al. supplementary workbook (pinned) |
| 20:02:30 | `GET static-content.springer.com/.../13059_2021_2592_MOESM2_ESM.pdf` | 200 | 172,578 | NeuSomatic 2022 Additional file 2 (screened with `pdftotext -layout`; not extracted) |
| 20:03:05 | `GET pmc.ncbi.nlm.nih.gov/articles/instance/11790059/bin/tables1_bbae697.xls` | 200 | 1,817 | HTML "Preparing to download" page, not the file |
| 20:04 to 20:06:01 | `GET .../PMC11790059/supplementaryFiles` (third attempt) | 500 | 10,135 | Failed |
| 20:04:51 | `GET doi.org/10.1093/bib/bbae697` | 403 | 5,749 | OUP landing page blocked |
| 20:08:20 | `GET .../PMC11790059/supplementaryFiles` (second attempt, started 20:01) | 200 | 13,019,486 | Complete zip; `zipfile.testzip()` clean; members `tables7_bbae697.xls` and `supplementary_methods_bbae697.docx` pinned |

While the complete zip was pending, complete members were recovered from the stalled partial download only to screen the tables (decompressing each local entry until the end of its deflate stream). `tables1_bbae697.xls` recovered that way has the same SHA-256 as the member of the complete zip (`574501a3...`). No record depends on the partial download.

## How each table was read

- **Wang et al. 2020, Supplementary Tables S1 and S2** (sheets `S1 WGS SNVs`, `S2 WGS INDELs`): parsed from the XLSX cell XML by `extract/rawxlsx.py` (copied from the CNV batch). `extract/extract_somatic.py` asserts the sheet order and titles, the seven column headers in row 3 (including their leading spaces), each dataset label in column A, the truth count in column B against article Table 1, the 15 (S1) or 12 (S2) configuration labels in column C for every dataset, empty A and B cells inside each block, and that no cell lies below the last block.
- **Guille et al. 2025, Supplementary Table S7** (`tables7_bbae697.xls`, sheet `Results`): a legacy BIFF8 workbook read by `extract/rawxls.py`, a standard-library reader written for this pass (OLE2 container, shared string table, NUMBER, RK, MULRK, LABELSST and FORMULA records). The extractor asserts the title, the 12 column headers, every row label, the truth count `P` (1160 or 50), `Nb_Vote`, `Nb_Tools`, `Categ` (Classic, Neural Network or the ensemble categories) and `Type of variant`, and that no cell lies below row 36.
- **Guille et al. 2025, article Tables 1 and 2**: parsed from the article XML (`table-wrap id="TB1"`, `id="TB2"`). Table 1 gives each caller's version and download link; Table 2's `SEQC2-FD` row is asserted cell by cell.
- **Guille et al. 2025, supplementary methods**: DOCX paragraph text. The extractor asserts the NeuSomatic checkpoint line, the DeepSomatic `--model_type=WGS` line and the Strelka `--exome` line.

`printed_value` is the shortest decimal that round-trips to the stored IEEE double (for example stored `0.70099999999999996` gives `0.701`); scientific notation is written out as a plain decimal. The stored text is kept in `raw_xml_value` (for the BIFF file, the Python repr of the stored double). Spreadsheet display formatting was not applied.

Run: `python3 -I extract/extract_somatic.py <pinned-dir> <batch-dir>`, where `<pinned-dir>` holds the five artifacts under the names in `ARTIFACTS` (the decompressed contents of `artifacts/*.gz`). The script checks each SHA-256 before reading.

## Dry run

`addBatch(batch.jsonl, data/omics/use-case-coverage-somatic-20261009, <scratch root>)` from `scripts/omics/records.ts`, run with `npx tsx` against a scratch copy of `data/entities`, `data/evidence` and `data/provenance`, added all 1,238 records (vocabularies, declared attributes and record validation passed). The SHACL export step of `npm run records -- add` was not run.
