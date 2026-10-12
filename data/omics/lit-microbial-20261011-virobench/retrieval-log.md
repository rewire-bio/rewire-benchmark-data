# Retrieval log

All requests were made from the collector's scratch area with curl. No personal identifier was sent.

1. `api.biorxiv.org` and Europe PMC were used for screening only (see the lane ledger).
2. `curl -sL https://arxiv.org/pdf/2605.25388v1` returned 200, 12 pages reported by `file` but 42 by
   `pdfinfo`; SHA-256 `22ad7d74...`.
3. `pdftotext -layout v1.pdf v1.txt` (poppler 26.08.0), 2,799 lines, SHA-256 `48071e2e...`. The text
   layer is what the extractor parses; it is archived under `artifacts/` (the licence is CC BY).
4. Table 25 (appendix, full suite) and Table 4 (main text) were parsed. Table 4 rows that also appear
   in Table 25 are asserted to agree cell by cell; only the two rows Table 25 omits (ViroDNABERT2 and
   ViroCaduceus) are taken from Table 4.
5. Generation results (Tables 5, 6, 27 and 28) and all figures were not extracted.

Re-run the extraction with:

```sh
curl -sL -o v1.pdf https://arxiv.org/pdf/2605.25388v1
pdftotext -layout v1.pdf v1.txt
python3 -I extract/extract_virobench.py v1.pdf v1.txt <batch-folder>
```

`extract/lib.py` holds the shared record builders. The script asserts the PDF hash before parsing.
