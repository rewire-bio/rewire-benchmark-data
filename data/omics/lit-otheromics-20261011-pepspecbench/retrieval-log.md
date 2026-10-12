# Retrieval log

All requests were made from the collector's scratch area with curl or Python urllib. No personal identifier was sent; the only email used for an API was the placeholder research-agent@example.invalid (Europe PMC).

1. arxiv.org/abs/2605.01945 (licence: arXiv.org perpetual non-exclusive license; one version, v1, 2026-05-03).
2. arxiv.org/html/2605.01945v1 (2026-10-11T21:27:08Z, SHA-256 `af7ed6d4470f0d4f60fccbe55103e72b19c258e53f9dd26c0c0e152a2ef18d81`). Not archived: the licence does not grant reuse.
3. arxiv.org/pdf/2605.01945v1 (same time, SHA-256 `98da8c16b5ab6c5e8ec225f0807ff2b9143fbb0f4d34cef0f3aa79c9b738a2de`). Not archived.
4. Tables 2, 4 and 14 parsed from the HTML `<td>` cells; header rows asserted.

Re-run the extraction with:

```sh
python3 -I extract/extract_pepspecbench.py <2605.01945v1.html> <2605.01945v1.pdf> <batch-folder>
```
