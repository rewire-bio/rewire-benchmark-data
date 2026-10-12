# Research notes

Part of the 2026-10-11 microbial and interactions literature pass (window 2025-10-01 to 2026-10-11).
The search log is in `data/omics/lit-search-20261011-microbial-interactions/ledger.jsonl`.

## Why this source

The question this answers is narrow and useful: does swapping a 1D convolution protein encoder for a
protein language model embedding help drug-target affinity prediction? The authors hold the drug
encoder fixed across four GNN variants, vary only the protein representation, and add a plain
architectural change to the convolution encoder (DeepGraphDTA) as the control. Their own reading is
that the control closes most of the gap: on KIBA, DeepGraphDTA with GAT-GCN reaches CI 0.903 against
PLM-GraphDTA with ProstT5 at 0.904.

This batch is smaller than the others and overlaps PLABench on Davis and KIBA, which is why it is
worth having: the two sources give different numbers for DeepDTA and GraphDTA on the same datasets,
under different training protocols. They are recorded under separate protocols, so nothing merges.

## Record counts

- benchmark: 1
- configuration: 23
- dataset: 2
- evaluation: 32
- method: 2
- model: 4
- protocol: 2
- result: 64
- source: 1

## Extraction notes (written before review)

- Two protocols, one per dataset, on the predefined DeepDTA holdout fold (train:test 5:1).
- 16 rows per table, each with CI and MSE, so 64 results.
- Origin: `author_reported` for the authors' PLM-GraphDTA and DeepGraphDTA rows, `unreported` for the
  baselines (KronRLS, SimBoost, DeepDTA, GraphDTA, PGraphDTA). The source does not say whether the
  baseline values were rerun or copied from the original papers, so `comparison.adaptation` is null
  with a missing reason rather than guessed.
- For the authors' own rows the values are means over five random seeds (Section 3.4.3); that is in
  `comparison.aggregation`. No spread is printed in Tables 2 and 3.
- MSE carries no printed unit, so it is `unit-unreported` with `unit_detail` naming the scale
  (Davis pKd, KIBA score). CI uses the new `concordance-index` concept.
- Tables 2 and 3 show only the PLM that won the 5-fold selection for each drug backbone (ESMC 600M
  on Davis, ProstT5 and ESMC 600M on KIBA). The full per-PLM comparison, which would be the more
  valuable evidence, is in Appendix D figures with no printed values: recorded as a gap.
- The ProstT5 family record comes from the `lit-interactions-20261011-ppiemb` batch, so that batch
  must be added to the store first.
