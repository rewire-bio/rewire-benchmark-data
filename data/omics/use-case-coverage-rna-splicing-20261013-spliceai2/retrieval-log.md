# Retrieval log: SpliceAI2 (Jaganathan et al. 2026)

Extractor: Claude (Opus 5.5) research agent spliceai2-extract, 2026-10-13, for issue #127. Downloads went to an empty scratch directory; scripts were kept in a separate directory and Python was run with `-I`. No email or personal identifier was sent to any service.

1. 12:38 UTC: downloaded the Illumina-hosted PDF named in the issue (HTTP 200, 3,273,641 bytes). `pdfinfo`: 57 pages, created 2026-10-03. Read the full text layer (`pdftotext -layout`).
2. 12:40 UTC: Europe PMC search for "SpliceAI2" found the bioRxiv preprint PPR1338942, DOI 10.64898/2026.10.08.757673. `api.biorxiv.org/details` gave version 1, posted 2026-10-11, licence cc_by_nc, published NA.
3. 12:40 UTC: downloaded the bioRxiv JATS XML (front matter only), the v1 full-text PDF (HTTP 200, 2,679,664 bytes) and the single supplement, Supplementary Table 1 (TSV, 898 bytes).
4. Compared the two PDFs: after removing the bioRxiv licence header printed on each page, the multiset of words in the two text layers differs only in fragments of rotated figure labels. The bioRxiv PDF is pinned for extraction.
5. 12:41 UTC: GitHub API for Illumina/SpliceAI2: created 2026-10-07, four commits, tag v2.0 at `aa63437`. Downloaded README.md, LICENSE and setup.py at `1dcd2a1` from raw.githubusercontent.com. The two commits after v2.0 change README.md only.
6. 12:41 UTC: downloaded the announcement page (HTML, 384,836 bytes) and read its body text. It is a lead only. It says "more than 46 million observed splice junctions after filtering", while the paper prints 67,493,026 junctions (Supplementary Table 1, before the per-gene filters); not used.
7. 12:44 UTC: Hugging Face API for illumina-ai: model illumina-ai/SpliceAI2, revision `55948ba`, gated, two checkpoints. Weights not downloaded.
8. Rendered pages 11, 13, 15, 17, 52 and 55 of the pinned PDF at 130 dpi (`pdftoppm`) to read rotated column labels (Extended Data Fig. 2) and to check bar colours against the legends (Figs. 3c, 3f, 4g).
9. Ran `extract/build_batch.py` on the pinned PDF and TSV. It checks both SHA-256 values, parses Extended Data Fig. 2 from the text layer (panel titles, row labels and 17 values per row asserted, "All" column cross-checked against Fig. 1d and the main text), reads bar labels of Figs. 3c, 3f and 4g with `pdftotext -bbox` and asserts their left-to-right order, and asserts every main-text sentence a value or claim is taken from.
