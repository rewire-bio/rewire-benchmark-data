# Retrieval log

All requests were made from the collector's scratch area with curl or Python urllib. No personal identifier was sent; the only email used for an API was the placeholder research-agent@example.invalid (Europe PMC).

1. Europe PMC REST fullTextXML for PMC13501138 (2026-10-11T21:27:03Z).
2. Europe PMC supplementaryFiles archive for PMC13501138 (2026-10-11T21:28:04Z). `gkag813_supplemental_file.pdf` (12.1 MB, SHA-256 `0e26a301a5b5c39a0e2dfaa092760d6099345dcb9e0545e23b730374f39d463c`) was extracted from it. The PDF is not archived here because of its size; the hash pins it.
3. Tables 2-5 parsed from the XML `<td>` cells; header rows asserted.
4. Supplementary Tables S1 (versions), S6, S7 and S15 read from `pdftotext -layout` output; header rows and method order asserted.
5. Extractor check, not a derivation: the means of the per-target columns of Supplementary Tables S2-S5 reproduce Tables 2 and 3 to rounding (easy n = 30, hard n = 49; lDDT 29 and 47), except RF2NA INF on the hard set (Table 3 prints 0.668; the S3 column mean is 0.608). The DRfold and DeepFoldRNA per-target columns are identical in S3-S5.

Re-run the extraction with:

```sh
python3 -I extract/extract_rna3d.py <PMC13501138 fullTextXML> <gkag813_supplemental_file.pdf> <batch-folder>
```
