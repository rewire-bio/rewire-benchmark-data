# Retrieval log

1. 2026-10-11 21:37Z. Europe PMC REST `PMC12650410/fullTextXML` (108,973 bytes, SHA-256 `0d115f3c...`), CC BY 4.0.
2. Read the body and Table 1 (table-wrap `biomolecules-15-01532-t001`). Supplementary files are on the publisher site and were not needed for Table 1.
3. `extract/extract_wes_synthetic.py` (run with `python3 -I`) checks the hash, parses Table 1, asserts the header, caller labels and Total Truth, writes `batch.jsonl` and `claims.csv`, and archives the XML (CC BY 4.0) under `artifacts/`.
