# Retrieval log

1. Lead from Europe PMC (ledger q03); bioRxiv details API gave v1, 2026-05-20, CC BY. Europe PMC indexes it as PPR1236009 without full text.
2. The first JATS download was rate-limited (HTTP 429); the full-text PDF was downloaded later. The pinned copy was fetched at 2026-10-11T21:36:31Z.
3. `pdftotext -layout` then `python3 -I extract/extract_ye2026.py <pdf> <txt> <batch-folder>`. The script asserts the PDF hash and each table's column header, takes rows with exactly 21 numbers in printed order, assigns 8 rows (six datasets, mean, std) to each of the four reference blocks, asserts the printed dataset and reference labels, and asserts 2,352 results. It then checks that the scGPT costok TF+500 mean rows of Tables 4 and 6 equal the printed Table 1 values for STRING, ChIP-seq and OmniPath.
