# Retrieval log: Helzer et al. 2025, 2026-10-11

Worker: Claude (Opus 5.5) research agent uc-ctdna in Claude Code. No human review claimed. Downloads went to a session scratch directory, one folder per source, and were read as data (pdftotext -layout, Python under -I). No model was run. Times are UTC.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| ~21:39 | Web search (ledger `search-lit-20261011-uc-ctdna-w4`) | | | Lead: PMC12521513 |
| ~21:39 | Europe PMC search `PMCID:PMC12521513` and full text (screening) | 200 | | CC BY; published 2025-10-14; Tables S1-S2 in the supplement |
| 21:40:59 | Europe PMC `PMC12521513/fullTextXML` (pinned) | 200 | 113,407 | `48e63b92...2f70ead835` |
| 21:41:00 | Europe PMC `PMC12521513/supplementaryFiles` | 200 | 7,283,117 | Zip of 3 PDFs; `41467_2025_64153_MOESM1_ESM.pdf` `3fe7690e...e79b6e` |
| 21:41:25 | Springer `static-content.springer.com/.../41467_2025_64153_MOESM1_ESM.pdf` | 200 | 4,517,508 | Same SHA-256 as the bundle member; pinned with this URL |

## How each value was read

`extract/extract_helzer2025.py` reads the pdftotext -layout text layer (poppler 26.08.0). It locates both table captions and headers, matches each data row by its metric label and a fixed count of three-decimal values (5 for GRAIL, 10 for UW), splits the rows into four panel blocks (13 rows, or 14 for the UW full panel with Griffin), asserts the set of metric labels in each block, asserts that every panel label printed in the body (GRAIL, FoundationOne Liquid CDx, Guardant360 CDx, Tempus xF; UW, Foundation One CDx) falls in its block, and asserts that each 'Mean AUROC' equals the mean of its phenotype columns within 0.0015. The UW column order (the PDF prints 'Prostate' and 'RCC' on separate header lines) is fixed by four sentences of the article that quote values from known columns, which are asserted. 790 results.
