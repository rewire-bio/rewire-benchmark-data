# Retrieval log

1. Lead from Europe PMC (ledger q02); bioRxiv details API gave v1, 2026-07-24, CC BY.
2. Full-text PDF downloaded at 2026-10-11T21:35:10Z (file modification time); a re-download at 21:40 was rate-limited (HTTP 429), so the first download is the pinned copy.
3. `pdftotext -layout` then `python3 -I extract/extract_sun2026.py <pdf> <txt> <batch-folder>`. The script asserts the PDF hash, matches method rows by printed name followed by exactly five percentages, asserts the row order of each table, and asserts 170 results; the 'True DE prevalence' rows become claims on the dataset subsets.
