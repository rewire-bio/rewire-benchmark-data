# Retrieval log

1. 2026-10-14: unpacked the three archived artifacts from data/omics/gfm-guides-20261014-esm1b/artifacts/ into a scratch directory. Each hashes to its pinned SHA-256 (the script asserts all three). Nothing was downloaded.
2. Read the workbook's `Contents` sheet for the column definitions, the article's Results 'ESM1b can predict the effects of multiresidue variants', Fig. 4 legend and Methods ('Generalized effect scores for indels and stop-gain variants', 'Baseline scores of indel and stop-gain variant effects', 'AUC metrics for pathogenicity classification', 'Other VEP methods'), and the Supplementary Methods 'Indels and stop gain ClinVar benchmarks'.
3. Ran extract/build_supp2.py (command in research.md). It wrote batch.jsonl and claims.csv.
4. Added the batch with `npm run records -- add`; records stay needs_review.
