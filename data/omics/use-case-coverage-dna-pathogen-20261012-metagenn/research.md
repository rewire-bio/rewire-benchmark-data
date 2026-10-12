# Research notes

Part of the 2026-10-12 ML-versus-baseline pass for issue #121. No literature search was run: the source was named in the issue. The store had no MetageNN, GeNet or MetaMaps records before this batch.

## Why this source

Moreno et al. 2024 compare MetageNN, a neural-network classifier, with Kraken2 and MEGAN-LR (two of the use case's three baseline tools) and with MMseqs2, MetaMaps and GeNet, on ONT reads, with every tool using the same 516-genome database. Its stated focus is reads from species missing from the reference, which is part of the use case's question.

## What was extracted

The article prints most accuracy results only in Figures 3 and 4. Extracted: every cell of Table 1 (database storage and speed, 6 tools), the Kraken2 speed printed in the text (it conflicts with the table), and the accuracy values printed in the Results text: MMseqs2 and Kraken2 F1 and sensitivity over all isolates, MetageNN F1 and sensitivity for out-of-database isolates in genera with more than three species, and the share of reads classified on the pseudo-mocks for five tools. 24 results.

Record counts: benchmark 1, claim 5 (3 descriptive, 2 relevance judgements), configuration 6, dataset 2, evaluation 14, method 1, model 2, protocol 3, result 24, source 1. Everything is `needs_review`.

A new metric concept, `reference-storage-size`, was added to `data/vocab/metric.ttl` for Table 1's "Memory (GB)" column; no existing concept covers the size of a stored database or model.

## Relevance judgements (drafts)

- `use-case-mapping-dna-pathogen-20261012-metagenn-isolates`: proxy; headline recall. No printed value compares MetageNN with a baseline on the same subset.
- `use-case-mapping-dna-pathogen-20261012-metagenn-mocks`: proxy; headline proportion (share of reads classified). MetageNN against Kraken2 and MEGAN-LR on the same reads, but reads classified is not accuracy.

No judgement is proposed for the resources protocol (storage and speed); it does not answer the use case's detection question.

## Questions for the reviewer

See `coverage.json` (`concerns_for_reviewer`).
