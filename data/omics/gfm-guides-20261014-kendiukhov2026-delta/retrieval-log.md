# Retrieval log

1. 2026-10-14: unpacked the archived PDF and Europe PMC XML from data/omics/gfm-guides-20261014-kendiukhov2026/artifacts/ into a scratch directory. The PDF hashes to the pinned SHA-256 (the script asserts it). Nothing was downloaded.
2. Found every ΔAUROC and attention-advantage value in the XML paragraphs, then located each on its PDF page in the `pdftotext` reading-order output.
3. Ran extract/extract_delta.py (command in research.md). It wrote batch.jsonl and claims.csv.
4. Added the batch with `npm run records -- add`; records stay needs_review.
