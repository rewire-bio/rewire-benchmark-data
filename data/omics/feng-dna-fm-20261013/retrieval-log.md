# Retrieval log

All requests were plain HTTPS GETs with curl from the collector's scratch area on 2026-10-13. No credentials or personal identifiers were sent.

1. Europe PMC full-text XML for PMC12663285. SHA-256 matched the stored source `evidence-expansion-dna-foundation-models-2025-5d8ca9bc`.
2. Supplementary Information PDF (MOESM1) and Supplementary Data workbook (MOESM3) from Springer static content, using the file names listed in the article XML `<supplementary-material>` elements. MOESM3 is an .xlsm workbook; it was read as a zip of sheet XML, with no macros run.
3. `README.md` and `job_scripts/gtex_hyena.py` from raw.githubusercontent.com at commit `3f4c81ce066f3c47422a83466b085aac1a6be902` (repository HEAD on 2026-10-13; tags v1.0 and v1.1 exist; the paper cites Zenodo 10.5281/zenodo.17349484, not retrieved).
4. The Nature article page was not used; an earlier pass recorded that it redirects to an identity provider.

Re-run the extraction with:

```sh
python3 -I extract/extract_feng.py <epmc.xml> <MOESM3_ESM.xlsm> <MOESM1_ESM.pdf> <gtex_hyena.py> data/omics/feng-dna-fm-20261013
```

The script asserts all four artifact hashes, the Table 1 and Table 4 captions, column headers and row labels, and the expected count of 110 new Table 1 results before writing.
