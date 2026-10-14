# Retrieval log

All requests were made with curl from the collector's scratch area. No personal identifier was sent.

1. 2026-10-14T12:00Z. Looked up the existing Evo 2 source records in `data/entities/sources.jsonl`. The record
   `evidence-official-8717ffb993cc8f7eddec` points at the Europe PMC full-text XML for PMC13128491. Re-downloaded
   `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13128491/fullTextXML` and computed its SHA-256:
   `d043dbda49e023ef6b70e36e7ca7832bda6b7af6c5934368e8778a7f23cda8bd`, identical to the stored hash. The record is
   reused; no duplicate source record was created. The XML confirms the Nature version: Nature 652, 1349, DOI
   10.1038/s41586-026-10176-5, epub 2026-03-04, licence CC BY-NC-ND 4.0.
2. The JATS XML contains no `<table-wrap>` elements: the paper has no numbered main tables. Its
   `<supplementary-material>` elements list five files. Two were retrieved:
   `41586_2026_10176_MOESM1_ESM.pdf` (Supplementary Information, 73 pages) and `41586_2026_10176_MOESM3_ESM.xlsx`
   (Supplementary Data 1, human variant effect prediction results), both from
   `https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-026-10176-5/MediaObjects/`, HTTP 200, at
   2026-10-14T12:01:04Z. Hashes are in `sources.md`. The other three files (Reporting Summary, Supplementary Data 2
   motif report, Supplementary Data 3 design sequences) are not about variant effect prediction and were not
   retrieved.
3. The main-text comparisons of Fig. 3 and Extended Data Figs. 4 and 5 are bar charts. No numbers were read from
   them. Supplementary Data 1 publishes the underlying per-stratum AUROC and AUPRC values as printed cells, so the
   results come from the workbook, not the figures.
4. Supplementary Data 1 was read with a stdlib OOXML reader (`extract/ooxml.py`, copied unchanged from
   `data/omics/use-case-coverage-rna-splicing-20261011-silverstein2026/extract/ooxml.py`). The sheet is a single
   flat table, "Sheet1" A1:J706, with no formulas: columns Model, Data, Genomic_Feature, Variant_Type, Sub_category,
   N_pos, N_neg, N_variants_total, AUROC, AUPRC. The extractor asserts the header, 705 data rows, no cell beyond row
   706, that no cell holds a formula, that N_pos + N_neg equals N_variants_total in every row, that each of the 49
   strata has identical counts across models, that the BRCA1 and BRCA2 positive and negative counts match
   Supplementary Information A.3.15, and that the set of model labels matches the 21 configurations extracted.
5. The Supplementary Information PDF was read as text (`pdftotext -layout`) for the protocol and configuration
   metadata and to check whether any per-model AUROC table exists. Supplementary Tables 5 to 8 print AUROC and
   AUPRC values, but only for Evo 2 7B base against a data-ablation model, not for the comparison models; they are
   recorded as a gap, with the values that conflict with Supplementary Data 1, rather than extracted.

Re-run the extraction with:

```sh
python3 -I extract/extract_evo2_brixi2026.py <PMC13128491.xml> <MOESM1_ESM.pdf> <MOESM3_ESM.xlsx> <batch folder>
```

The script asserts the SHA-256 of all three inputs before reading anything.
