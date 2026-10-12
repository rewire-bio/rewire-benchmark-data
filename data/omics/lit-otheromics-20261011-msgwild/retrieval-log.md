# Retrieval log

All requests were made from the collector's scratch area with curl or Python urllib. No personal identifier was sent; the only email used for an API was the placeholder research-agent@example.invalid (Europe PMC).

1. arxiv.org/abs/2606.19624 (licence CC BY 4.0; one version, v1, 2026-06-17).
2. arxiv.org/html/2606.19624v1 (2026-10-11T21:27:08Z, SHA-256 `47f329399853bdd2a513707b97271dfd8875271be383168effde1b0f13efb0d2`), archived as gzip.
3. arxiv.org/pdf/2606.19624v1 (same time, SHA-256 `81c23b4035c50661c77594fde0071798a13692cfb4f6b5ddb56e73587efa9fea`), not archived. Every extracted printed value was found verbatim in the PDF text layer (whitespace ignored).
4. Tables 2, 3 and 9 parsed from the HTML `<td>` cells; grey text read from the `--ltx-fg-color:#808080` style; header rows asserted; citation markers and the ICEBERG footnote removed from row labels.

Re-run the extraction with:

```sh
python3 -I extract/extract_msgwild.py <2606.19624v1.html> <2606.19624v1.pdf> <batch-folder>
```
