# Retrieval log

1. 2026-10-14: unpacked the archived workbook and article PDF from data/omics/gfm-guides-20261014-kedzierska2025/artifacts/ into a scratch directory. The workbook hashes to the pinned SHA-256 (the script asserts it). Nothing was downloaded.
2. Read the AvgBIO and Average Batch Score definitions in the pdftotext -layout output of the article (Methods, pages 9-10).
3. Ran extract/extract_avg.py (command in research.md). It wrote batch.jsonl (176 results) and claims.csv.
4. Added the batch with `npm run records -- add`; records stay needs_review.
