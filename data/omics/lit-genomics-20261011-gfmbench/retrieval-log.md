# Retrieval log

All requests were made from the collector's scratch area with Python urllib or curl. No personal identifier was sent; the only email used for an API was the placeholder research-agent@example.invalid (Unpaywall).

1. bioRxiv details API gave version 2 (2026-08-11, CC BY). The JATS XML holds the appendix tables as images, so the v2 full-text PDF was downloaded.
2. pdftotext -layout (poppler) text of appendix Tables 1-5 parsed by row pattern; model names matched exactly; task labels assigned to fixed blocks of model rows in printed order (4 models per block in Tables 1 and 4; 5 in Table 3, 4 for VEP-eval, which prints no Evo2 row); row and task counts asserted.

Re-run the extraction with:

```sh
pdftotext -layout <paper.pdf> <paper.txt>; python3 -I extract/extract_gfmbench.py <paper.pdf> <paper.txt> <batch-folder>
```

`extract/lib.py` holds the shared record builders. The script asserts the artifact hash before parsing.
