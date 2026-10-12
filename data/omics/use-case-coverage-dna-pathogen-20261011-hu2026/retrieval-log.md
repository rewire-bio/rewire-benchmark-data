# Retrieval log: Hu et al. 2026, short-read versus host-depleted nanopore mNGS on BALF

Worker: Claude (Opus 5.5) research agent (uc-pathogens) in Claude Code. No human review claimed. Each download went into its own folder in a session scratch directory and was opened only as data (XML, DOCX or XLSX parsed as text). No classifier, pipeline or model was executed.

Times are UTC on 2026-10-11.

| Time | Request | Result |
| --- | --- | --- |
| 21:37:24 | Europe PMC `PMC13339908/fullTextXML` | HTTP 200, 105,750 bytes. Pinned |
| 21:41:40 | Europe PMC `PMC13339908/supplementaryFiles` | HTTP 200 ZIP (489,077 bytes): two supplementary files and figure images. The DOCX member is pinned |
| 21:43:00 | Same ZIP endpoint again; `europepmc.org/articles/PMC13339908/bin/...docx` | ZIP hash differed (rebuilt per request) but the DOCX member hash was identical; the direct file URL returned HTTP 403 |

## How the values were read

`extract/extract_hu2026.py` parses Table 2 from the XML `<table-wrap>` and Supplemental Tables 6 and 7 from `word/document.xml` (fifth and sixth tables). It asserts the header row, block labels (NGS, TGS), the +/- row and column labels and the PPA/NPA (or Sensitivity/Specificity) row labels before writing each value. Values were cross-checked by hand: every PPA and NPA equals its counts to one decimal, except TGS NPA against CMT (printed 79.2%, counts give 80.8%).

