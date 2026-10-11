# Retrieval log

1. 2026-10-11 21:37Z. Europe PMC REST `PMC12579226/fullTextXML` (143,443 bytes, SHA-256 `6b5e5262...`). Licence in the XML: CC BY-NC-ND 4.0. The XML has no tables; results are in figures and supplementary files.
2. Supplementary files are named in the XML (`41467_2025_64547_MOESM1_ESM.pdf` to `MOESM6_ESM.xlsx`). Downloaded MOESM1 (Supplementary Information, 3,006,945 bytes, SHA-256 `806cd474...`), MOESM4 (Supplementary Data 1, false-positive and false-negative review; not used) and MOESM6 (Source Data, 1,887,973 bytes, SHA-256 `4347c74f...`) from static-content.springer.com.
3. Read MOESM1 with pdftotext -layout (version 26.08.0): Supplementary Tables 1 to 8 and 'Command lines used' (versions, model types, Mutect2 germline resource).
4. Read the Source Data sheets 'Supplementary Table 2', '7a' and '7b' with a stdlib xlsx reader (`extract/xlsx.py`).
5. `extract/extract_clairs_to.py` (run with `python3 -I`) checks the three hashes, parses the PDF rows, matches them to the Source Data rows and asserts every value, then writes `batch.jsonl` and `claims.csv`.
6. Licence is CC BY-NC-ND 4.0, so no copy of the article or supplement is archived; hashes and locators only.
