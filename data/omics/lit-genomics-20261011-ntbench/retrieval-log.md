# Retrieval log

All requests were made from the collector's scratch area with Python urllib or curl. No personal identifier was sent; the only email used for an API was the placeholder research-agent@example.invalid (Unpaywall).

1. Supplementary Information PDF (MOESM1, 25 pages) downloaded from Springer static content; the article XML (PMC11810778) has no result tables.
2. Supplementary Tables 6 and 7 (three blocks of six task columns each) and 9 parsed from pdftotext -layout text; Supplementary Table 5 read for task sizes.
3. Licence CC BY-NC-ND 4.0: hashed, not archived.

Re-run the extraction with:

```sh
pdftotext -layout <MOESM1.pdf> <M1.txt>; python3 -I extract/extract_ntbench.py <MOESM1.pdf> <M1.txt> <batch-folder>
```

`extract/lib.py` holds the shared record builders. The script asserts the artifact hash before parsing.
