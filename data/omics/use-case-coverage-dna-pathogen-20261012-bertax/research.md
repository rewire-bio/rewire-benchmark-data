# Research notes

Part of the 2026-10-12 ML-versus-baseline pass for issue #121. No literature search was run: the source was named in the issue. The store had no BERTax, DeepMicrobes or Mock et al. 2022 records before this batch.

## Why this source

The DNA pathogen-identification use case names Kraken2, minimap2 and MEGAN-LR as its baseline and records that no machine-learning method had been compared with them on the same data. Mock et al. 2022 score BERTax and DeepMicrobes against Kraken2, minimap2, sourmash and MMseqs2, with every tool given the same reference or training data.

## What was extracted

Every method cell of Table 1 (macro AveP, 9 tools by 7 dataset and rank columns), SI Table S2 (accuracy and proportion classified, 9 tools by 8 columns) and SI Table S5 (accuracy with and without homologous test sequences, 3 tools by 6 columns): 153 results.

Record counts: benchmark 1, claim 6 (3 descriptive, 3 relevance judgements), configuration 27, dataset 3, evaluation 27, model 2, pipeline 2, protocol 3, result 153, source 3. Everything is `needs_review`.

## Not extracted

- The `random` rows of Table 1 and Table S2 (chance reference, not a method).
- SI Tables S1, S3, S4, S6 and S7: BERTax architectures, per-superkingdom AveP, epochs, homology split for BERTax only, ablations.
- PR and ROC curves, confusion matrices and other figures.

## Relevance judgements (drafts)

- `use-case-mapping-dna-pathogen-20261012-bertax-closely`: proxy; stratum 1.
- `use-case-mapping-dna-pathogen-20261012-bertax-distantly`: proxy; stratum 2. Closest to the use case's question about organisms absent from the reference.
- `use-case-mapping-dna-pathogen-20261012-bertax-final`: proxy; stratum 3.

All in comparison group `bertax2022-fragments`, headline metric macro AveP. Proxy because the inputs are simulated 1,500-nt genome fragments and the ranks stop at genus.

## Questions for the reviewer

See `coverage.json` (`concerns_for_reviewer`).
