# Retrieval log

1. 2026-10-23. Read Wang 2026's Methods from the pinned full text (`lit-rna-20261011-rnalm-zeroshot/artifacts/wang2026-PMC12963973-fulltext.xml.gz`): 31 ncRNA DMS assays from RNAGym with wild-type length at most 440 nt; MCC, AUC and "the absolute value of the Spearman correlation coefficient (SR)". Read the WT-LLR and PLL-D definitions and the Table 10 and 11 captions in the pinned supplement.
2. 2026-10-23. `gh api repos/MarksLab-DasLab/RNAGym/contents/fitness/reference_sheet_final.csv?ref=2828cf99316d75daaa8d832a2573cbb25bbd35fe`: 26 ribozyme, 3 tRNA and 2 aptamer assays; the longest construct is 425 nt, so Wang's filter keeps all 31. Not archived; the file is at that commit.
3. 2026-10-23. `gh api repos/MarksLab-DasLab/RNAGym/commits?path=leaderboard/fitness&sha=v0.2` listed the leaderboard commits after the pinned v0.1.1 commit. The default branch `main` has none of them.
4. 2026-10-23. Downloaded the v0.2 README at `75d07fe00e08` and three commits (see sources.md) to `artifacts/`.
5. No score was recomputed. The per-assay prediction files are not in the repository, so the absolute-value effect for this pair was not measured.
