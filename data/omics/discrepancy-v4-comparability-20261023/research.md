# Comparability links for discrepancy rules version 4

Date: 2026-10-23. Issues #204, #207 and #208. Design: `docs/design/discrepancy-rules-v4.html`.

The discrepancy rules decide whether two studies measured the same system, are the same study, and measured the same task. These record changes give them what they need for the cases found in the review of the medium findings (#201, PR #212). No result value or status changes.

## New records (batch.jsonl)

| Record | Why |
| --- | --- |
| `discrepancy-v4-20261023-task-clinical-missense-pathogenicity` | Brandes 2023, the ProteinGym clinical substitutions track and Livesey and Marsh 2025 all classify clinical missense variants, but no task record joined them, so ESM-1b against EVE (`discrepancy-36711e250f9269de`, #211) read as cross-task. |
| `discrepancy-v4-20261023-task-rnagym-ncrna-fitness` | The RNAGym leaderboard and Wang 2026 score the same 31 ncRNA DMS assays (Wang's protocols use `lit-rna-20261011-rnalm-zeroshot-data-rnagym-ncrna31`), but no task record joined them (`discrepancy-8c69346a6089882b`, #209). |

Both are `needs_review`: they name a shared prediction question, not a protocol.

## Changes to existing records (`records -- change`)

Combined configurations (#204). The 15 configurations linked to `somatic-20261009-method-majority-vote` combine other callers' calls. Each gets `combination_rule` (for example "at least 2 of 3") and a `uses_model` link to each member caller named in its own name or description. Strelka2 maps to `somatic-20261009-method-strelka` and VarScan2 to `somatic-20261009-method-varscan`, as the store already does for the single-caller configurations. Their `configuration_of` link is unchanged.

Study grouping (#207). `companion_of` links join the ProteinGym repository result files at commit `144fe22` and the NeurIPS paper source `evidence-expansion-proteingym-a3b08cc4` to the DOI source `proteingym-2023`. They are one piece of work. RNAGym has no paper source in the store, and the PFMBench and ProteinBench repository and site sources carry no results, so nothing is linked for them.

Task links (#208):
- `pfmbench-task-proteingym-zs` `evaluates_task` `catalog-task-proteingym-effects` (#210).
- `gfm-guides-20261014-esm1b-benchmark-brandes2023-clinical-missense`, `vep-lit-20261014-protocol-proteingym-clinical-zero-shot-substitutions-auc-144fe22` and `vep-lit-20261014-protocol-livesey2025-clinical-auroc` `evaluates_task` the new clinical missense task.
- `lit-rna-20261011-rnagym-benchmark-rnagym-fitness-leaderboard-v0-1-1` and the Wang 2026 fitness protocols (`lit-rna-20261011-rnalm-zeroshot-protocol-t10-*` and `-t11-*`) `evaluates_task` the new RNAGym task.

The ProteinBench design tasks and the ProteinGym fitness protocols are already linked to their own benchmarks, so they read as different tasks without changes.

## Limits

Automated review by a Claude agent; no human review. Member callers were matched from each configuration's name and description, not re-read from the papers.
