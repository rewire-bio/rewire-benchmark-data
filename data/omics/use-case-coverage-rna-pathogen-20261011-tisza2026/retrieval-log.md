# Retrieval log: Tisza et al. 2026, EsViritu virus profiler benchmark (preprint)

Worker: Claude (Opus 5.5) research agent (uc-pathogens) in Claude Code. No human review claimed. Each download went into its own folder in a session scratch directory and was opened only as data (XML, DOCX or XLSX parsed as text). No classifier, pipeline or model was executed.

Times are UTC on 2026-10-11.

| Time | Request | Result |
| --- | --- | --- |
| 21:39:50 | api.biorxiv.org details; bioRxiv JATS `2026.09.29.755457.source.xml` | HTTP 429 at 21:39:3x, then HTTP 200, 66,618 bytes. Pinned. Contains no tables; points to supplementary file DC1 |
| 21:42:50-21:45:51 | bioRxiv `DC1/embed/media-1.xlsx` | HTTP 429 twice, then HTTP 200. Pinned |
| 21:37:26 | Europe PMC `PMC13648648/fullTextXML` | HTTP 200, abstract only (6,295 bytes); PMC and bioRxiv PDFs blocked (HTML challenge or 429). Not used |

## How the values were read

`extract/extract_tisza2026.py` reads the workbook's sheet XML and shared strings without a spreadsheet library, asserts each sheet's header row and every row's tool, rank and depth labels, and writes the shortest decimal that round-trips to each stored number. 'NA' cells keep `printed_value` 'NA' with `numeric_value` null and a missing reason.

