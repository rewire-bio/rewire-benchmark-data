# Retrieval log: Zhong et al. 2026, FlexMS (arXiv 2602.22822v4)

All times UTC, 2026-10-11. Worker: Claude (Opus 5.5) research agent, extraction only; no review claimed.

1. 00:44:14 `https://arxiv.org/pdf/2602.22822` (HTTP 200, 10,864,393 bytes; the PDF header reads v4, 24 Jun 2026). Re-fetched `https://arxiv.org/pdf/2602.22822v4`; identical SHA-256.
2. Licence from the arXiv abstract page: CC BY-NC-ND 4.0.
3. Ran pdftotext 26.08.0 `-layout`. Ran `extract/zhong2026.py`: asserts the Table 2 header (11 embedders), the two metric section labels and the three predictor labels.
4. Dry run of `addBatch` against a copy of the store passes.
