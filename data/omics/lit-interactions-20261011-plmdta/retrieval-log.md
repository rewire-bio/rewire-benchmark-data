# Retrieval log

All requests were made from the collector's scratch area with curl. No personal identifier was sent.

1. `api.biorxiv.org/details/biorxiv/10.64898/2026.08.31.748056` returned version 1, posted
   2026-09-03, licence `cc_by_nc`, no published journal version.
2. Europe PMC holds the record (PPR1312720) but not the full text.
3. `curl -sL https://www.biorxiv.org/content/10.64898/2026.08.31.748056v1.full.pdf` returned 200
   with a browser user agent (a default agent was rate-limited with Cloudflare error 1015);
   12,564,280 bytes, 24 pages, SHA-256 `11b88d5a...`.
4. `pdftotext -layout v1.pdf v1.txt` (poppler 26.08.0), SHA-256 `e9b9dff9...`. Not archived: the
   licence is non-commercial.
5. Tables 2 (Davis) and 3 (KIBA) parsed, all 16 rows each with their CI and MSE. Figures 4 and 5
   (cold-start results) and the Appendix D per-PLM selection figures were not read.

Re-run the extraction with:

```sh
curl -sL -A "<a browser user agent>" -o v1.pdf https://www.biorxiv.org/content/10.64898/2026.08.31.748056v1.full.pdf
pdftotext -layout v1.pdf v1.txt
python3 -I extract/extract_plmdta.py v1.pdf v1.txt <batch-folder>
```

A fresh download has a different hash because of the bioRxiv banner.
