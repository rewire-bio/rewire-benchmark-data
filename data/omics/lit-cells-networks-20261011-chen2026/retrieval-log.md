# Retrieval log

1. Lead from a web search for spatial foundation model benchmarks (ledger q21). arXiv export API: v1 2026-07-19, v2 2026-09-17, licence CC BY-SA 4.0 on the abstract page. The arXiv HTML for this paper returned 404, so the PDF was used.
2. `curl -sSL -o 2607.17227v2.pdf https://arxiv.org/pdf/2607.17227v2` at 2026-10-11T21:29:34Z; an earlier download had the same SHA-256.
3. `pdftotext -layout` (poppler) then `python3 -I extract/extract_chen2026.py <pdf> <txt> <batch-folder>`. The script asserts the PDF hash, strips form feeds, matches data rows by dataset code and number count, assigns model labels to fixed blocks in printed order (labels sit on the middle row or on their own line) and asserts block sizes, labels and per-table result counts (99, 63, 126, 72 and 18).
