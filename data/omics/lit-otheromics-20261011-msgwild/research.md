# Research notes

Part of the 2026-10-11 RNA and other-omics literature pass. Search log: `data/omics/lit-search-20261011-rna-otheromics/ledger.jsonl`.

## Why this source

MassSpecGym in the Wild (arXiv:2606.19624v1, CC BY) audits 26 papers that report MassSpecGym results and republishes corrected leaderboards. It bears directly on `use-case-mass-spectrum-molecule-shortlisting` and on every MassSpecGym value in the store, because it documents leakage and candidate-set artifacts that inflate published hit rates.

## Record counts

- claim: 2
- configuration: 34
- dataset: 3
- evaluation: 156
- method: 4
- model: 12
- protocol: 14
- result: 156
- source: 1

Counts after the review corrections (review.md).

## Extraction notes

- Every cell of Table 2 (mass-based retrieval, MIST with different formula sources), Table 3 (formula-known retrieval leaderboard: literature values, corrected and inflated artifact-exploiting methods, spectrum-blind stress tests) and Table 9 (de novo with formula). Table 4 repeats Table 9 rows apart from a MIST encoder Tanimoto column, which has no metric concept; not extracted.
- Grey rows (the paper's mark for leaking or inflated results) are separate configurations with a limitation saying why; the judgements exclude them.
- Origin is set per row: `paper_compilation` for values the table repeats from cited works; `author_reported` for the authors' own runs of methods from their groups (MIST, ICEBERG, DreaMS-based and spectrum-blind baselines; authors include the MassSpecGym, DreaMS, MIST, ICEBERG and FRIGID developers); `independent_paper` for the two dagger reimplementations (nearest neighbour; MIST + MolForge). A reviewer should check these.
- Uncertainty: the parenthesised ranges are bootstrap confidence intervals. The appendix states 99.9% over 20,000 resamples for the authors' evaluations; for compiled values the level is left unset.
- Table 2 prints hit rates without a percent sign; recorded as percent with a `unit_detail`.
- Relevance judgements (status needs_review) for the Table 2 Hit rate@1 and Hit rate@20 protocols on `use-case-mass-spectrum-molecule-shortlisting`, rated proxy, with the four grey evaluations excluded. Proposed `assessed_by` links are in `use-case-links.json`, not applied. Note the use case excludes formula-conditioned retrieval 'including MIST'; here MIST uses a formula predicted from the spectrum (MIST-CF), which a reviewer should judge.
- Table 3 rows Random, DeepSets, Fingerprint FFN, DeepSets + Fourier and MIST vMassSpecGym repeat MassSpecGym (arXiv:2410.23326v1) Table 3, already in the store under part2-massspecgym-arxiv-v1; not re-added.
