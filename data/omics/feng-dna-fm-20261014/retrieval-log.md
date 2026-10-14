# Retrieval log

All requests were plain HTTPS GETs with curl from the collector's scratch area on 2026-10-14 (UTC). No credentials or personal identifiers were sent.

1. Europe PMC full-text XML for PMC12663285. SHA-256 matched the stored source.
2. Supplementary Data workbook (MOESM3, .xlsm) and Supplementary Information PDF (MOESM1) from Springer static content. Both hashes matched the sources created in PR #141. The workbook was read as a zip of sheet XML; no macros were run. Number formats were read from `xl/styles.xml`: every numeric cell used is in General format.
3. The PDF text was read with `pdftotext -layout` page by page to locate Supplementary Notes 1 and 2.
4. The author repository was not needed for these tables.

Re-run the extraction from the repository root with:

```sh
python3 -I data/omics/feng-dna-fm-20261014/extract/extract_feng.py <epmc.xml> <MOESM3_ESM.xlsm> <MOESM1_ESM.pdf> . data/omics/feng-dna-fm-20261014
```

The script asserts the three artifact hashes; the Table 2, 3, 5 and 6 captions, footnotes, headers and row labels; the Supplementary Data 4 block titles, headers, model labels and General number format; that every linked existing record is in the store and that the stored Table 3 Human 5mC and Table 5/6 values equal the XML cells; that each Supplementary Data 4 row's mean is within 0.0001 of its stored Table 5/6 AUC; that no new ID is already in the store; and the counts (40 Table 2, 88 Table 3 and 177 Supplementary Data 4 results, 26 CNN claims). It reads the store (sharded or not) and never writes to it. Its output is byte-identical across runs on the pinned files.

Write the batch to the store with:

```sh
npm run records -- add data/omics/feng-dna-fm-20261014/batch.jsonl data/omics/feng-dna-fm-20261014
```
