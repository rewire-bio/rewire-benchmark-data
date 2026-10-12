# Retrieval log

All requests were made from the collector's scratch area with curl. No personal identifier was sent.

1. `api.biorxiv.org/details/biorxiv/10.64898/2026.09.17.752433` returned version 1, posted
   2026-09-23, licence `cc_by_nc_nd`, no published journal version.
2. Europe PMC holds the record (PPR1326152) but not the full text, so the bioRxiv PDF was used.
3. `curl -sL https://www.biorxiv.org/content/10.64898/2026.09.17.752433v1.full.pdf` returned 200
   after a 429 and a wait; 30 pages; SHA-256 `5fba9691...`.
4. `pdftotext -layout v1.pdf v1.txt` (poppler 26.08.0), 2,708 lines, SHA-256 `acc4a3c5...`. Not
   archived: the licence is CC BY-NC-ND.
5. Tables 2 (Davis and KIBA under three splits), 3 (CASP16 L1000 and L3000) and 4 (ChEMBL35) parsed,
   every cell. Figures, including the input-pose-accuracy ladder and the per-target Kendall tau
   heatmap, were not read.

Re-run the extraction with:

```sh
curl -sL -A "<a browser user agent>" -o v1.pdf https://www.biorxiv.org/content/10.64898/2026.09.17.752433v1.full.pdf
pdftotext -layout v1.pdf v1.txt
python3 -I extract/extract_leakctl.py v1.pdf v1.txt <batch-folder>
```

A fresh download has a different hash because of the bioRxiv banner, so the script's hash assertion
is against the retrieval recorded above. A reviewer re-downloading the PDF should compare the table
cells, not the PDF bytes.
