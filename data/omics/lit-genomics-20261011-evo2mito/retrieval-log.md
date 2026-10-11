# Retrieval log

All requests were made from the collector's scratch area with Python urllib or curl. No personal identifier was sent; the only email used for an API was the placeholder research-agent@example.invalid (Unpaywall).

1. bioRxiv v1 full-text PDF downloaded (CC BY); JATS tables are images. Table 2 parsed from the pdftotext -layout text; header and the eight row labels asserted.

Re-run the extraction with:

```sh
pdftotext -layout <paper.pdf> <paper.txt>; python3 -I extract/extract_evo2mito.py <paper.pdf> <paper.txt> <batch-folder>
```

`extract/lib.py` holds the shared record builders. The script asserts the artifact hash before parsing.
