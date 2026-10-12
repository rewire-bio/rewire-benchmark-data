# Retrieval log: Fragmentia-AI (Cell Reports Medicine 2026), 2026-10-11

Worker: Claude (Opus 5.5) research agent uc-ctdna in Claude Code. No human review claimed. Downloads went to a session scratch directory, one folder per source, and were read as data (pdftotext -layout, Python under -I). No model was run. Times are UTC.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 21:34:05 | Europe PMC search (ledger `search-lit-20261011-uc-ctdna-f01`) | 200 | | Lead: PMC13400139, CC BY-NC-ND |
| ~21:36 | Europe PMC full text and supplementary bundle (screening) | 200 | | Table S5 found in Document S1 |
| 21:41:11 | Europe PMC `PMC13400139/fullTextXML` (pinned) | 200 | 143,657 | `42a96f1b...dfd5fdbd` |
| 21:41:12 | Europe PMC `PMC13400139/supplementaryFiles` | 200 | 7,338,555 | Zip; member `mmc1.pdf` `357004ee...8122d41` pinned |
| 21:41:25 | cell.com `mmc1.pdf` | 403 | 5,852 | Refused (HTML) |
| 21:41:30 | PMC `articles/PMC13400139/bin/mmc1.pdf` | 404 | | Not found |

## How each value was read

`extract/extract_fragmentia2026.py` reads the pdftotext -layout text layer of `mmc1.pdf`. It finds the Table S5 caption and the next table caption, asserts the header words, matches rows (optional feature label, classifier, AUC, optional p value), asserts 19 rows, three classifiers per feature in order, one feature label per block (inline or on a line between rows), and the final Fragmentia-AI row without a p value. Eleven article sentences describing the comparison are asserted. 19 results.
