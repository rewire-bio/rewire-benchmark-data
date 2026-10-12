# Retrieval log

All requests were made from the collector's scratch area with Python urllib. No personal identifier was
sent to any service.

1. Europe PMC search API, `resultType=core`, for the DOI, to resolve the PMC identifier, the open-access
   status and the licence.
2. Europe PMC `PMC12553333/fullTextXML`, saved to the scratch area and hashed (SHA-256 above).
3. Tables 2 to 8 parsed from the saved bytes; the five-seed protocol and the significance marks were read
   from the table footnotes, and the metric wording from the Figure 3 caption.

Re-run the extraction with:

```sh
python3 -I extract/extract_deepprotein.py <PMC12553333.xml> <batch-folder>
```

`extract/lib.py` holds the shared record builders and `extract/jats.py` the JATS table-grid parser. The
script asserts the artifact hash before parsing, asserts each table's two header rows and split-size row,
and asserts every model row label.
