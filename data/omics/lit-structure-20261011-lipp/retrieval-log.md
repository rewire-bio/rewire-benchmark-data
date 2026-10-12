# Retrieval log

All requests were made from the collector's scratch area with Python urllib. No personal identifier was
sent to any service.

1. Europe PMC search API, `resultType=core`, for the DOI, to resolve the PMC identifier, the open-access
   status and the licence.
2. Europe PMC `PMC13292216/fullTextXML`, saved to the scratch area and hashed (SHA-256 above).
3. The table inventory was listed from the saved bytes, then Tables 2 and 3 were parsed.

Re-run the extraction with:

```sh
python3 -I extract/extract_lipp.py <PMC13292216.xml> <batch-folder>
```

`extract/lib.py` holds the shared record builders and `extract/jats.py` the JATS table-grid parser
(rowspan and colspan expanded). The script asserts the artifact hash before parsing and asserts every
row and column label.
