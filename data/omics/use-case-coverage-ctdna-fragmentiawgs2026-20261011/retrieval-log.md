# Retrieval log: Fragmentia-AI WGS (Molecular Biomedicine 2026), 2026-10-11

Worker: Claude (Opus 5.5) research agent uc-ctdna in Claude Code. No human review claimed. Downloads went to a session scratch directory, one folder per source, and were read as data (pdftotext -layout, Python under -I). No model was run. Times are UTC.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 21:34:12 | Europe PMC search (ledger `search-lit-20261011-uc-ctdna-f02`) | 200 | | Lead: PMC13469060, CC BY |
| ~21:36 | Europe PMC full text (screening) | 200 | | TF-stratified AUCs in Results text |
| 21:51:36 | Europe PMC `PMC13469060/fullTextXML` (pinned) | 200 | 139,639 | `8c2cd974...32652b5ead` |
| 21:51:38 | Europe PMC `PMC13469060/supplementaryFiles` | 200 | 2,346,054 | Zip; member `43556_2026_538_MOESM1_ESM.docx` `df6f4b15...6e6055e85d0` |
| 21:52:25 | Springer `static-content.springer.com/.../43556_2026_538_MOESM1_ESM.docx` | 200 | 2,480,471 | Same SHA-256 as the bundle member; pinned with this URL |

## How each value was read

`extract/extract_fragmentiawgs2026.py` asserts the full Results sentences of P8, P13, P14, P19 and P21 that carry each value and parses the numbers from those asserted sentences with regular expressions. Table S4 is read from the DOCX table XML; the caption row, header and six row labels are asserted, and each printed sensitivity is checked against detected/total to three decimals. 30 results.
