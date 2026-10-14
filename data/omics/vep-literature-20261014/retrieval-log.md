# Retrieval log

All requests were plain HTTPS GETs with curl (or `gh api` for GitHub metadata) from the collector's scratch area on 2026-10-14. No credentials beyond the GitHub CLI token for the API calls, and no personal identifiers, were sent. Nothing was run except the extraction script below; no model, predictor or ProteinGym code was executed.

1. 13:35:49Z: Europe PMC search for the Livesey and Marsh author pair (ledger q01).
2. 13:36:01Z to 13:36:02Z: Europe PMC full-text XML for PMC7336272, PMC10407742, PMC12016141 and PMC13620131. All HTTP 200.
3. 13:36:25Z: Springer static-content URLs for `13059_2025_3575_MOESM2_ESM.xlsx` and `MOESM1_ESM.docx`, using the file names in the PMC12016141 XML `<supplementary-material>` elements. HTTP 200. The workbook was read as a zip of sheet XML.
4. 13:37:00Z: Europe PMC `supplementaryFiles` endpoint for PMC10407742 (2023 edition). The download stalled at 2,666,496 bytes and was stopped after about four minutes; the partial file was deleted.
5. 13:39:17Z to 13:39:24Z: `gh api` for the ProteinGym `main` head (still 144fe22) and the recursive tree at 144fe22 (SHA-256 of the JSON `72903f76e04ffb0c5cbb07d8e3366072698304b68aaf717e7f6a3f7cf04537a9`).
6. 13:39:32Z to 13:39:33Z: the four ProteinGym summary CSVs from raw.githubusercontent.com at 144fe22. HTTP 200.
7. 13:41:35Z: ProteinGym `README.md` and `proteingym/performance_DMS_benchmarks.py` at 144fe22, to check the hashes of the existing source records and read the aggregation code (lines 85-111, 260-402).
8. 13:42:46Z: `https://europepmc.org/articles/PMC10407742/bin/MSB-19-e11474-s008.xlsx` (2023 Table EV6). HTTP 403 with 5,580 bytes of challenge HTML (SHA-256 `7135c12e1c5332dd0cb5122ba3dcd3ddbf0700428d4ee154231dcfdf40fe1800`). Not retried; the challenge was not solved or bypassed.
9. 13:40 to 13:52Z: further Europe PMC searches (ledger q02 to q09).

Re-run the extraction with:

```sh
python3 -I data/omics/vep-literature-20261014/extract/extract_vep.py <download-dir> data/omics/vep-literature-20261014
```

`<download-dir>` must hold `PMC12016141.xml`, `gb2025/MOESM2_ESM.xlsx` and `pg/<path with / replaced by _>.csv` (the archived copies in `artifacts/` decompress to the same bytes). The script asserts every artifact hash, the article title and four methods phrases, the workbook sheet names, the legends of Tables S3 and S5-S8, the Table S2 header and row count (93), the column headers of every extracted table, row counts (97 in S3, S5, S6, S7; 85 in S8; 97, 13, 17 and 18 in the ProteinGym files), that the S5-S7 label sets equal S3's, and that S8's extra labels are exactly CADD, COSMIS, CPT and fathmm-XF. It reads `extract/pg_configurations.tsv`, the label-to-configuration map for ProteinGym models already in the store, generated from `data/entities/configurations.jsonl` (configurations whose ID starts `uc20260930-proteingym-amfr-config-` and whose version is 144fe22).
