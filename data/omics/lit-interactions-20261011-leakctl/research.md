# Research notes

Part of the 2026-10-11 microbial and interactions literature pass (window 2025-10-01 to 2026-10-11).
The search log is in `data/omics/lit-search-20261011-microbial-interactions/ledger.jsonl`.

## Why this source

PLABench is the most useful protein-ligand affinity evaluation found in the window. It puts nine
models on four test sets, two of which control leakage explicitly: the CASP16 pharmaceutical series
(prospective) and a ChEMBL v35 set with every ligand within ECFP4 Tanimoto 0.85 of any training
molecule of any evaluated model removed. It also standardises the structural input by giving every
structure-based model the same AlphaFold3 predictions, which is what makes the comparison readable.

The store had Boltz-2 only through its developers' own reporting. This batch adds an independent
evaluation of it on a leakage-controlled set, where it reaches Pearson 0.321 and Kendall 0.211,
second to FLOWR.ROOT (0.392 and 0.264).

## Record counts

- benchmark: 1
- configuration: 12
- dataset: 9
- evaluation: 45
- model: 7
- protocol: 9
- result: 279
- source: 1

## Extraction notes (written before review)

- Nine protocols: Davis and KIBA each under warm, cold-target and cold-drug splits (six), CASP16
  L1000 and L3000 (two), and ChEMBL35 (one). Table 2 covers only the three sequence-based models,
  which the authors retrained; Tables 3 and 4 cover all nine.
- Two configurations per model: one for the Davis and KIBA retraining and one for the CASP16 and
  ChEMBL35 evaluation, because the adaptation differs.
- Boltz2 is counted among the six structure-based models in the Results but co-folds its own complex,
  so its configuration records that the supplied structures are not consumed, and Figure 3 draws it
  as a horizontal line. Its inputs are recorded as sequence and SMILES.
- MSE and RMSE carry no printed unit. They are recorded as `unit-unreported` with `unit_detail`
  naming the affinity scale of each dataset (Davis and CASP16 pKd, KIBA score), following the
  store's existing convention for error metrics in unstated target units.
- rm2 and CI needed new metric concepts: `modified-squared-correlation` (Roy's rm2) and
  `concordance-index`. Both are defined in the paper's Methods and the definitions are quoted in the
  concept scope notes.
- Origin: FlowDock is by Morehead and Cheng, and Cheng is the senior author of this benchmark, so
  FlowDock's evaluations are `author_reported`; the other eight are `independent_paper`. A reviewer
  should confirm that call.
- The metrics are computed over all test pairs of a set (Methods). The text describes the ChEMBL35
  analysis as target-centric but does not say whether Table 4 pools complexes or averages over the
  71 targets; recorded as a protocol limitation.
