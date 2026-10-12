# Retrieval log

All requests were made from the collector's scratch area with Python urllib. No personal identifier was
sent to any service.

1. Europe PMC search API, `resultType=core`, for the DOI, to resolve the PMC identifier, the open-access
   status and the licence.
2. Europe PMC `PMC13225634/fullTextXML`, saved to the scratch area and hashed (SHA-256 above).
3. Table 3 parsed from the saved bytes; the metric definitions (sc-TM designability, pdb-TM novelty,
   Foldseek-Cluster diversity, average time per backbone, TOPSIS with CRITIC weighting) were read from
   the Metrics section.

Re-run the extraction with:

```sh
python3 -I extract/extract_scaffoldlab.py <PMC13225634.xml> <batch-folder>
```

`extract/lib.py` holds the shared record builders and `extract/jats.py` the JATS table-grid parser. The
script asserts the artifact hash before parsing, forward-fills the type and method columns and asserts
that the repeated mean-closeness and rank cells agree down each group.
