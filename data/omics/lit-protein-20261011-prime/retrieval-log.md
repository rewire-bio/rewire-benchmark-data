# Retrieval log

All requests were made from the collector's scratch area with Python urllib. No personal identifier was
sent to any service.

1. Europe PMC search API, `resultType=core`, for the DOI, to resolve the PMC identifier, the open-access
   status and the licence.
2. Europe PMC `PMC13425921/fullTextXML`, saved to the scratch area and hashed (SHA-256 above).
3. Table 1 parsed from the saved bytes; its three header rows (split, target, metric) were asserted.

Re-run the extraction with:

```sh
python3 -I extract/extract_prime.py <PMC13425921.xml> <batch-folder>
```

`extract/lib.py` holds the shared record builders and `extract/jats.py` the JATS table-grid parser. The
script asserts the artifact hash before parsing and asserts every row and column label.
