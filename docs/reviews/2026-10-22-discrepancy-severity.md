# Discrepancy rule calibration, 2026-10-22

Rules version 2 (`data/ontology/discrepancy-rules.json`). Issue #174; PR #175.

Checked on the store at the head of PR #175 (main at release `2026-10-22-7edc1288c132`, plus the AlphaGenome comparator links): 2.2M asserted statements.

## What version 1 produced

306 discrepancies: 1 high, 71 medium, 234 low.

- All 36 gap outliers, and 17 ordering reversals, set ProteinGym files against each other: the AMFR assay-level table, the zero-shot DMS substitutions summary and the clinical indels summary, all at commit `144fe22`. They are one benchmark's own summaries at different levels, one assay against the average over 217 assays. Version 1 treated them as independent studies because they share no result record.
- 17 reversals, all but one of them medium, compared the BERTax paper with its own SI appendix: two source records with one DOI.
- The Alavi 2026 AlphaGenome case (`discrepancy-ead251c24ba272c1`) was low, one of 234 lows. It is cross-task and its identity links are unreviewed, so it lost two steps. Nothing separated it from reversals backed by a handful of comparisons.

## Changes

| Change | Why |
| --- | --- |
| Sources with the same DOI are one study | A paper and its supplement are one study. |
| Files from one GitHub repository are one study | A benchmark's leaderboard summaries are not independent of each other. |
| A reversal of a consensus of at least 20 comparisons that agree at least 95% of the time goes up one severity step | A near-unanimous consensus over many comparisons makes a reversal a stronger lead. Of the 234 version 1 lows, 13 met it. |

The other thresholds are unchanged.

## What version 2 produces

254 discrepancies: 1 high, 17 medium, 236 low. The gap rule finds none.

- `discrepancy-ead251c24ba272c1` is medium: "Alavi 2026 ranks Borzoi above AlphaGenome in 9 of 12 comparisons; other studies rank AlphaGenome above Borzoi in 25 of 25." Its review state is `awaiting-correction`.
- The single high is ProteinBench ranking ProteinMPNN above ESM-IF1 in 10 of 10 comparisons, against 24 of 24 elsewhere.
- The 236 lows are cross-task reversals with unreviewed identity links. Livesey and Marsh 2025 (74), Lee 2026 (35) and Chen 2020 (19) account for over half.

## Known limits

- A merged study is labelled by its first source, so the merged ProteinGym study still reads "ProteinGym AMFR assay-level Spearman comparison" in summaries, although it covers all three files. `outlier_sources` lists them all.
- The issue's acceptance test asks for a gap-outlier finding on AlphaGenome's gap to SpliceAI. It does not fire. The AlphaGenome paper's splicing protocols are not linked to the splicing task or use case (issue #174, RC4), so no three studies share a protocol or task for that pair. The rule is not widened to cover it.
- Most identity links in the store have no backing claim, so most findings are `unreviewed` and lose a step. Backing claims for the links involved in medium and high findings would sharpen the ranking.
- Automated calibration by a Claude agent; no human review is claimed.
