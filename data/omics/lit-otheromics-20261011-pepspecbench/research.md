# Research notes

Part of the 2026-10-11 RNA and other-omics literature pass. Search log: `data/omics/lit-search-20261011-rna-otheromics/ledger.jsonl`.

## Why this source

PepSpecBench (arXiv:2605.01945v1) is a new benchmark for peptide MS/MS fragment intensity prediction: six models (Prosit, Prosit Transformer, AlphaPeptDeep, PredFull, UniSpec, FastSpel) retrained on backbone-disjoint splits of PROSPECT and MassIVE-KB, scored in one canonical fragment space, and transferred zero-shot to five out-of-distribution species and cell sets. The store had no proteomics spectrum-prediction benchmark.

## Record counts

- benchmark: 1
- configuration: 12
- dataset: 7
- evaluation: 156
- model: 6
- protocol: 16
- result: 168
- source: 1

## Extraction notes

- Every cell of Table 2 (in-domain SAS, SA, PCC per source), Table 4 (SA / SAS for five OOD sets, by training source) and Table 14 (four-decimal median SA with 95% bootstrap CI). Table 4's 'ID (SA)' column repeats Table 2 and was not extracted again. Table 6 (all seven OOD subsets with PCC) was not chosen; a later pass can add it.
- Table 14 values are extra results on the same in-domain SA evaluations, with a distinct `metric_qualifier` so they are not compared with the three-decimal Table 2 values.
- New metric concepts `spectral-angle` and `spectral-angle-similarity` (added to `data/vocab/metric.ttl`), following the paper's Section 3 definitions.
- Area: `proteins-complexes` is used because the vocabulary has no proteomics area; a reviewer or the owner may prefer a new concept.
- Origin `independent_paper`: the benchmark authors retrained all six models and developed none of them.
- PROSPECT PredFull SA is 0.204 in Table 2 but 0.203 in Table 4 and 0.2035 in Table 14 (recorded in the source limitations).
