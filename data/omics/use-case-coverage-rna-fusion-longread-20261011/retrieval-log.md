# Retrieval log

1. 2026-10-11. bioRxiv API `details/biorxiv/10.64898/2026.08.07.743439`: version 1, 2026-08-12, licence cc_by, JATS XML URL.
2. 2026-10-11 21:36Z. Downloaded the JATS XML (153,248 bytes, SHA-256 `c665bb40...`). Its three tables are images (`743439v1_tbl1`, `tbls1`, `tbls2`); results are in figures. The Code availability statement names https://github.com/RDorney/LRFusionBenchmark.
3. GitHub API: repository default branch `main`, MIT licence, last push 2026-08-25; tree at commit `83e629fed3098881079fd9ac1c8bc13478ce69ed` lists `Figures/Input_dataframes/*`. Read `DATA_LICENSES.md` (project data under MIT).
4. 2026-10-11 21:36Z to 21:48Z. Downloaded eight files from raw.githubusercontent.com at that commit (paths in the source record). The extractor bundles them into one JSON with each file's SHA-256 and content.
5. `extract/extract_fusion_longread.py` (run with `python3 -I`) checks the XML hash, builds the bundle, asserts headers, row counts and caller labels, checks that Sensitivity equals Recall on every row and that the Huh7 sentence is present verbatim, writes `batch.jsonl` and `claims.csv`, and archives the bundle and the XML (both open licences) under `artifacts/`.
