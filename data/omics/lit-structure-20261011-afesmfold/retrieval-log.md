# Retrieval log

All requests were made from the collector's scratch area with Python urllib. No personal identifier was
sent to any service.

1. Europe PMC search API, `resultType=core`, for the DOI, to resolve the PMC identifier, the open-access
   status and the licence (CC BY-NC, so no full-text copy is committed).
2. Europe PMC `PMC12809598/fullTextXML`, saved to the scratch area and hashed (SHA-256 above).
3. Tables 1 and 2 parsed from the saved bytes; the classification thresholds and the template-quality
   definition were read from the Materials and methods section.

Re-run the extraction with:

```sh
python3 -I extract/extract_afesmfold.py <PMC12809598.xml> <batch-folder>
```

`extract/lib.py` holds the shared record builders and `extract/jats.py` the JATS table-grid parser. The
script asserts the artifact hash before parsing, forward-fills the tool column and asserts every row and
column label.
