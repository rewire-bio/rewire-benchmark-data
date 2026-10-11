# Retrieval log

All requests were made from the collector's scratch area with Python urllib or curl. No personal identifier was sent; the only email used for an API was the placeholder research-agent@example.invalid (Unpaywall).

1. arXiv v2 PDF downloaded; Tables 3-8 and 10 parsed from pdftotext -layout text with header and row assertions.
2. No licence printed; hashed, not archived.

Re-run the extraction with:

```sh
pdftotext -layout <paper.pdf> <paper.txt>; python3 -I extract/extract_genbench.py <paper.pdf> <paper.txt> <batch-folder>
```

`extract/lib.py` holds the shared record builders. The script asserts the artifact hash before parsing.
