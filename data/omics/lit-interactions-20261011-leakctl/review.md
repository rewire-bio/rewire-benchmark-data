# Review: lit-interactions-20261011-leakctl, 2026-10-11

Reviewer: Claude review agent `reviewer-mi-2`, independent of the extractor `lit-microbial-interactions`. No human review claimed. Source transcription is not reproduction.

The reviewer's full report for this batch, with the checks run and their outcomes, is in [2026-10-11-microbial-interactions-lit.md](../../../docs/reviews/2026-10-11-microbial-interactions-lit.md).

## Reviewer's verdict (verbatim)

| `lit-interactions-20261011-leakctl` (PLABench, 279 results) | Approved with corrections |

Every printed value in all three batches matches its source. The corrections below are metadata only:
training and adaptation descriptions, origin, populations, splits, units and limitations. None changes a
number.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store.

1. L1. The nine CASP16 and ChEMBL35 evaluations of DeepDTA, LLF and MixingDTA now record that the benchmark authors retrained them on the PDBbind v2020 refined set (4,465 training and 497 validation complexes; longest single chain), and their three configurations carry the full training description from Methods, replacing the earlier "applied to CASP16 and ChEMBL35 without retraining on them".
2. L2. MFE's three evaluations have `comparison.adaptation` null with `missing_metadata` reason `conflicting`, because Results says the structure-based models used official pretrained checkpoints while Data availability lists retrained MFE checkpoints. The same note is appended to its configuration's parameters.
3. L3. The 27 CASP16 and ChEMBL35 evaluations now record the stated populations: 17 ligands (chymase, L1000), 123 ligands (autotaxin, L3000) and 4,862 ligand-target pairs across 71 targets (ChEMBL35).
4. L4. The ChEMBL35 protocol's first limitation now says that Methods define each metric over N target-ligand pairs but the source does not state whether Table 4 pools all 4,862 pairs or averages per-target values, and the contradictory wording is gone. The two CASP16 protocols say that each series is a single target and that Figure 2 computes each tau over all ligands of a series.
5. L5. The twelve cold-split evaluations record the stated aggregation: the predictions of the five fold models on one fixed test set are aggregated, with the aggregation function not stated.
6. L6. The 18 ChEMBL35 MSE and RMSE results carry a `unit_detail` naming the ChEMBL35 Kd, Ki or IC50 affinities with EC50 excluded, and all 36 other MSE results now read "Squared error in" rather than "Error in".
7. L7. The Boltz-2 configuration records its inference settings (10 structural samples, affinity scored on the highest-ipTM pose, 500 sampling steps, 5 recycling steps), and the six Davis and KIBA dataset records carry the standardised dataset sizes.

The reviewers wrote the evidence concerns with a `date` field; the store's concerns use `reviewed_at` with a `review_method`, so each concern carries `reviewed_at: 2026-10-11T00:00:00Z` and `review_method: ai-assisted-source-review`. Every message, locator and artifact hash is verbatim.

No use-case judgement or summary was written: the reviewer agreed that no extracted protocol bears directly on a use case in `data/entities/use-cases.jsonl`.

## Records after correction

- benchmark: 1
- configuration: 12
- dataset: 9
- evaluation: 45
- model: 7
- protocol: 9
- result: 279
- source: 1
