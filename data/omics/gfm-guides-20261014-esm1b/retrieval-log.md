# Retrieval log

All requests were made with curl from the collector's scratch area on 2026-10-14. No personal identifier was sent.

1. Europe PMC search for DOI 10.1038/s41588-023-01465-0: PMID 37563329, PMC10484790, open access.
2. Downloaded the JATS full text from the Europe PMC REST endpoint (12:03:14Z). It lists three supplementary files: MOESM1 (Supplementary Information PDF), MOESM2 (Reporting Summary) and MOESM3 (Supplementary Table 2, xlsx).
3. Downloaded MOESM3 and MOESM1 from static-content.springer.com (12:03:21Z). The Reporting Summary was not needed.
4. Read the workbook with a stdlib OOXML reader and the Supplementary Information with `pdftotext -layout` (poppler 26.08.0).

Re-run the extraction with:

```sh
python3 -I extract/build_esm1b.py brandes.xml st2.xlsx si.pdf <batch-folder>
```

The script checks the three input hashes, writes the gzip archives, reads sheets `Table_of_results_ClinVar` and `Table_of_results_HGMD` (header row A1:D1, the n_var value on every included row, the `included` flag and the set of 19 included method labels are asserted), asserts the two Results sentences with the ESM1b and EVE ROC-AUCs verbatim, and writes `batch.jsonl` and `claims.csv`. Workbook values are written as the shortest round-trip decimal of the stored number.
