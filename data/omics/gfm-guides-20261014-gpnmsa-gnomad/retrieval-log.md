# Retrieval log

1. 2026-10-14T16:59:20Z: downloaded https://www.biorxiv.org/content/10.1101/2023.10.10.561776v2.full.pdf with curl (browser user agent). 37 pages, 2,247,726 bytes, SHA-256 c066dab1...0978. The pinned copy is not archived (licence CC BY-NC-ND), and bioRxiv per-download stamps change the hash.
2. Converted with `pdftotext -layout` (poppler 26.08.0).
3. Ran `python3 -I extract/build_gnomad.py v2.pdf v2.txt . <batch-dir>` from the repository root. Besides the caption, header, row-label and page assertions, the script checks that the 102 ClinVar, COSMIC and OMIM cells it parses equal the reviewed values in the store, which ties this text layer to the pinned version.
4. Added the batch with `npm run records -- add`; records stay needs_review.
