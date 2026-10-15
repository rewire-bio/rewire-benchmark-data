# Retrieval log

1. Europe PMC search for the title returned PMID 40251685, PMC12007350, DOI 10.1186/s13059-025-03574-x, licence CC BY. Full-text XML downloaded at 2026-10-14T12:01:05Z; it lists no main-text tables, two figures and three supplementary files (MOESM1 xlsx, MOESM2 pdf, MOESM3 docx).
2. Publisher PDF downloaded from genomebiology.biomedcentral.com at 2026-10-14T12:01:07Z (HTTP 200, 1,548,345 bytes, 13 pages).
3. Additional file 1 (MOESM1 xlsx) downloaded from Springer static content at 2026-10-14T12:01:36Z (HTTP 200, 34,272 bytes). Additional files 2 (supplementary figures) and 3 (review history) were not downloaded: figures are not read and the review history holds no results.
4. Both files gzipped into artifacts/. Re-downloaded at 2026-10-14T12:20:26Z; hashes unchanged.
5. The article text was read with `pdftotext -layout`. The headline comparisons (Fig. 1B, 1E, Fig. 2) are figures only. The text cites Additional file 1 for the numbers.
6. The workbook was read with a stdlib OOXML reader (extract/ooxml.py, copied from the Silverstein 2026 batch). All cells use number format General; values were stored as numbers for scores and ranks and as strings for the bracketed subsample columns.
7. `python3 -I extract/extract_kedzierska2025.py <xlsx> <pdf> <batch-folder>` was run on the files unpacked from artifacts/. The script asserts both SHA-256 values, every sheet title, header row, metric label and dataset label it reads, the format of every score cell and bracketed cell, and the page 5 sentence that carries the two text values. It writes batch.jsonl and claims.csv and asserts 602 results.
8. Validation: the worktree was copied to a scratch directory, the batch added there with `npm run records -- add` (SHACL conformance passed, 740 records added), then `npm run records -- check` (all records match provenance). The canonical store in the worktree was not touched.
