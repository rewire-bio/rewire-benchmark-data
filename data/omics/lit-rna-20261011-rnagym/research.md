# Research notes

Part of the 2026-10-11 RNA and other-omics literature pass (store completeness check of well-known suites). Search log: `data/omics/lit-search-20261011-rna-otheromics/ledger.jsonl`.

## Why this source

RNAGym is a well-known RNA fitness and structure benchmark suite and was absent from the store. Its official fitness leaderboard was updated in the window (v0.1.1, commit of 2026-08-14) with AIDO.RNA, RNAGenesis, Evo 2 and rescored RiNALMo and RNA-FM. The official leaderboard is a primary source (official project source); the preprint is out of window and CC BY-NC-ND.

## Record counts

- benchmark: 1
- configuration: 16
- dataset: 4
- evaluation: 64
- model: 3
- protocol: 4
- result: 64
- source: 1

## Extraction notes

- Every cell of both leaderboard tables except the AIDO.RNA-1.6B scaling row, which repeats the main-table AIDO.RNA (1.6B) row (asserted equal).
- Metric: signed Spearman (`spearman-correlation`), mean over assays per category and the unweighted macro-mean over three categories. Not comparable with the absolute Spearman of Wang et al. 2026 on the same 31 assays.
- Origin `independent_paper`: the RNAGym maintainers scored every model with their own scripts. No model on the board is theirs, as far as the README shows.
- Cross-batch dependency: AIDO.RNA and RiNALMo configurations link to the family records created in `lit-rna-20261011-rnalm-zeroshot`; add that batch first.
- 'RNA-ERNIE' (table) and 'RNAErnie' (CSV) were mapped to RNAErnie (Wang et al., Nature Machine Intelligence 2024), which the repository README lists. A reviewer should confirm this is not ERNIE-RNA.
- The README links `mRNA/leaderboard_signed_mRNA.csv`, absent at this commit; mRNA assay results were not extracted.
- The leaderboard cautions that ranks differing by less than about 0.01 are not meaningful; recorded on the benchmark.
