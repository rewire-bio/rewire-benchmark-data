# Retrieval log: Zeng et al. 2026, 2026-10-11

Worker: Claude (Opus 5.5) research agent uc-ctdna in Claude Code. No human review claimed. Downloads went to a session scratch directory, one folder per source, and were read as data (pdftotext -layout, Python under -I). No model was run. Times are UTC.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 21:34:30 | Europe PMC search (ledger `search-lit-20261011-uc-ctdna-m06`) | 200 | | Lead: PMC12948677, CC BY-NC-ND |
| ~21:38 | Europe PMC `PMC12948677/fullTextXML` (screening copy) | 200 | 238,630 | Tables, Source Data list and Results read |
| 21:40:43 | Europe PMC `PMC12948677/fullTextXML` (pinned) | 200 | 238,630 | `72e82320...e761e323`; same bytes as the screening copy |
| 21:40:45 | Europe PMC `PMC12948677/supplementaryFiles` | 200 | 27,900,341 | Zip of 15 files; `43018_2026_1116_MOESM6_ESM.xlsx` (Source Data Fig. 4) has SHA-256 `fae75168...0163b4` |
| 21:41:25 | Springer `static-content.springer.com/.../43018_2026_1116_MOESM6_ESM.xlsx` | 200 | 17,627 | Same SHA-256 as the bundle member; pinned with this URL |

## How each value was read

`extract/extract_zeng2026.py` reads the XLSX cell XML with `extract/rawxlsx.py` (stored values, no number formatting). It asserts the eight sheet names, each header row and its width, the set of row labels in each sheet and the row count, and 18 sentences of the article (the mAUCs quoted in Results P29, P32 and P33, the Figure 4 legend on error bars, the validation designs, the dataset compositions and the competing-interest statement). For each row the mean is the value and the s.d. column the uncertainty; for AUC sheets the minimum, maximum and plot position are kept in `source_cells`. 52 results.

The Results quote 0.674 for the methylation-only validation AUC; sheet Fig.4c prints 0.69415. Recorded as a disputed result with a source warning and `source_discrepancy` on the result (after independent review), not as a source evidence concern.
