# Retrieval log: Silverstein et al. 2026, Benchmarking RNA-seq Tools for Real-World Diagnostic Applications (medRxiv)

Collector agent uc-splicing-cnv, 2026-10-11. Downloads went to an empty scratch directory; scripts were kept in a separate directory and run with `python3 -I`.

1. Found by Europe PMC queries sp03, sp04 and sp06 (titles and abstracts, window 2025-10-01 to 2026-10-11). Licence (CC0) and JATS URL from api.biorxiv.org/details/medrxiv/10.64898/2026.01.27.26344940.
2. 21:38 UTC: first request for the JATS XML returned HTTP 429 (Cloudflare rate limit, error 1015); a second request a few minutes later returned HTTP 200 (163,062 bytes).
3. The XML lists three supplements (file07 PDF, file08 DOCX, file09 XLSX). The XLSX was requested at the DC3 media URL and returned HTTP 200 (41,367 bytes); it holds sheets 'Table S1' to 'Table S10'.
4. Read the body text to locate the definitions of true positives and negatives, the tool runs and the metric computation. Table 1 is an image (graphic element) and was not read.
5. Read sheet 'Table S9' with extract/ooxml.py (stdlib zipfile and ElementTree): A1:J10, every cell. Cell values are stored formula results with the General number format; the formulas are kept in each result's review note. Tables S3 to S5, S7 and S8 were read to check denominators, not extracted.
