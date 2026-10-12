# Retrieval log

1. Lead from Europe PMC (ledger q01). Europe PMC fullTextXML read for the article; tables are absent from the main text, results are in figures and Supplementary Data.
2. Springer ESM files MOESM3-7 and MOESM10 (Source Data) downloaded and inventoried. Supplementary Data 2 (MOESM4) holds per-dataset integration results; the sheets 'paired_inte_overall' and 'unpaired_inte_overall' were chosen.
3. `python3 -I extract/extract_scmbench.py <MOESM4.xlsx> <MOESM3.xlsx> <PMC13342640.xml> <batch-folder>`. The script asserts the three hashes, reads cells from the sheet XML (extract/xlsx_cells.py, standard library only), asserts header rows, row counts and the General number format, and asserts 241 results (128 paired, 113 unpaired, blank cells skipped).
