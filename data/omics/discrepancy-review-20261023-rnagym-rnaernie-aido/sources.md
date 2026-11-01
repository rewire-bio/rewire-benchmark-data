# Sources: the RNAGym v0.2 fitness leaderboard

## `discrepancy-review-20261023-source-rnagym-v0-2-leaderboard`

- URL: https://github.com/MarksLab-DasLab/RNAGym/blob/75d07fe00e087890e844791322f69fd8a264eda9/leaderboard/fitness/README.md
- Version: branch `v0.2`, commit `75d07fe00e087890e844791322f69fd8a264eda9` (2026-10-23T18:45:13Z). The default branch `main` still has the v0.1.1 leaderboard at retrieval.
- Retrieved: 2026-10-23, from raw.githubusercontent.com at that commit
- Archived copy: `artifacts/rnagym-v0.2-leaderboard-fitness-README.md`, SHA-256 `d9d08c7d6d206ca6c63bba3f7a96bce304c89d531aa0b90ef0dcc95d98bae041`
- Licence: MIT

Supporting copies, from `gh api repos/MarksLab-DasLab/RNAGym/commits/<sha>` reduced with jq to sha, dates, message and file patches. All three commits are ancestors of `75d07fe00e08`.

| File | Commit | What it says |
| --- | --- | --- |
| `artifacts/rnagym-commit-d43db8c613.json` | `d43db8c6137026267af4b4820ad9c6358f0e7608` | RNA-ERNIE's scorer and why its score is not comparable with the masked checkpoints |
| `artifacts/rnagym-commit-d024cd81a3.json` | `d024cd81a3861cda9a9ac0367beb1d3896cd391f` | Rescoring the masked models with wt-fill; AIDO.RNA passes RNA-ERNIE |
| `artifacts/rnagym-commit-ac371bff28.json` | `ac371bff28f9b21f2c4e78fce8acf1058df55334` | `performance_fitness.py` returned the absolute Spearman until this commit |

## Existing sources reused

- `lit-rna-20261011-rnagym-source-leaderboard-v0-1-1`: the v0.1.1 leaderboard, the outlier side. Unchanged.
- `lit-rna-20261011-rnalm-zeroshot-source-wang2026` and `-supplement`: Wang et al. 2026, the consensus side. Unchanged.
