# Retrieval log: Xu and Feng 2026 (medRxiv), 2026-10-11

Worker: Claude (Opus 5.5) research agent uc-ctdna in Claude Code. No human review claimed. Downloads went to a session scratch directory, one folder per source, and were read as data (pdftotext -layout, Python under -I). No model was run. Times are UTC.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 21:34:30 | Europe PMC search (ledger `search-lit-20261011-uc-ctdna-m02`) | 200 | | Lead: PPR1288828 |
| ~21:36 | bioRxiv API `details/medrxiv/10.64898/2026.07.26.26358979` | 200 | | Version 1, 2026-07-29, licence cc_no |
| ~21:36 | medRxiv JATS XML | 200 | 17 | Cloudflare error 1015 (rate limit); not used |
| 21:36:51 | Europe PMC `PPR1288828/fullTextXML` | 500 | 150 | No preprint full text |
| ~21:37 | medRxiv full-text HTML through a web fetch tool | 200 | | Screening only; table bodies not rendered |
| 21:49:59 | medRxiv `10.64898/2026.07.26.26358979v1.full.pdf` | 200 | 2,761,568 | `369746bf...2e7366961e`; pinned |

## How each value was read

`extract/extract_cpgpt2026.py` reads the pdftotext -layout text layer. It finds the Table 3 caption, asserts the header, parses each model's value line and its confidence-interval line (the 'Random Forest' label is split over both), asserts the five model labels in order and the footnote, and asserts eleven sentences of the Methods and Results, including the Results sentence that repeats the four classical test AUROCs. 15 results.
