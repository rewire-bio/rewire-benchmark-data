# Retrieval log

1. 2026-10-11 21:37Z. Europe PMC REST `PMC13243554/fullTextXML` (97,917 bytes, SHA-256 `b42db521...`), CC BY 4.0. No tables in the XML.
2. 2026-10-11 21:51Z. Downloaded `41467_2026_71705_MOESM1_ESM.pdf` (Supplementary Information, 28 pages, 7,533,710 bytes, SHA-256 `c808b436...`), `MOESM4_ESM.xlsx` (TCGA sample lists; not used) and `MOESM6_ESM.xlsx` (Source Data, 44,784 bytes, SHA-256 `4a2deae7...`) from static-content.springer.com.
3. pdftotext -layout of MOESM1: Supplementary Tables 1, 2 and 4 are text (physical pages 18, 19 and 21). The first extraction missed the text layer of Tables 1 and 4; corrected after review.
4. `extract/extract_varnet_t.py` (run with `python3 -I`) checks the hashes, parses Tables 1, 2 and 4 from the PDF and compares every cell with the Source Data sheets, checks three Results values, and writes `batch.jsonl` and `claims.csv`.
5. No copies archived (the PDF is 7.5 MB); hashes and locators only.
