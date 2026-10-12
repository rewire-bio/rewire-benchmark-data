# Retrieval log: Alavi 2026, Probing Genomic Foundation Models with Splice-Variant Perturbations (bioRxiv)

Collector agent uc-splicing-cnv, 2026-10-11. Downloads went to an empty scratch directory; scripts were kept in a separate directory and run with `python3 -I`.

1. Found by Europe PMC queries sp05, sp09 and sp10. Licence and JATS URL from api.biorxiv.org (query sp11).
2. The JATS XML returned HTTP 429 four times and then HTTP 200, but held metadata only (9,626 bytes, no body).
3. 21:42 UTC: the full-text PDF returned HTTP 200 (1,823,372 bytes).
4. Tables III (PDF page 6) and IV (page 9) read with pdftotext -layout (poppler 26.08.0) in extract/extract_alavi2026.py: value rows found by token pattern, 12 rows per table, row-label fragments asserted, percentages checked against counts. Methods C to H read in reading-order text for thresholds and model versions.
5. Not archived: CC BY-NC-ND.
