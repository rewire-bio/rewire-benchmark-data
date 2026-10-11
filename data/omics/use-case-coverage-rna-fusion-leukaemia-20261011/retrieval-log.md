# Retrieval log

1. 2026-10-11 21:37Z. Europe PMC REST `PMC13071280/fullTextXML` (156,853 bytes, SHA-256 `4d3a6d48...`), CC BY-NC 4.0.
2. Read Methods, Table 2 and the Results section 'Fusion gene detection performance of RNA-seq compared with that of conventional diagnostic methods'. Supplemental Data Tables S2 and S3 are on the publisher site and were not retrieved.
3. `extract/extract_fusion_leukaemia.py` (run with `python3 -I`) checks the hash, parses Table 2, asserts the header, section structure, row count and column sums, asserts the five quoted sentences verbatim, and writes `batch.jsonl` and `claims.csv`. No copy archived.
