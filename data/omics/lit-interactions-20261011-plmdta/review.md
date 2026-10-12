# Review: lit-interactions-20261011-plmdta, 2026-10-11

Reviewer: Claude review agent `reviewer-mi-2`, independent of the extractor `lit-microbial-interactions`. No human review claimed. Source transcription is not reproduction.

The reviewer's full report for this batch, with the checks run and their outcomes, is in [2026-10-11-microbial-interactions-lit.md](../../../docs/reviews/2026-10-11-microbial-interactions-lit.md).

## Reviewer's verdict (verbatim)

| `lit-interactions-20261011-plmdta` (bioRxiv 2026.08.31.748056v1, 64 results) | Approved with corrections |

Every printed value in all three batches matches its source. The corrections below are metadata only:
training and adaptation descriptions, origin, populations, splits, units and limitations. None changes a
number.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store.

1. D1. The Davis dataset records that it is the version corrected by Monteiro et al. 2022 with mutant sequences resolved, not the commonly used DeepDTA repository sequences. The eight Davis baseline evaluations are `independent_paper` with the adaptation "Trained by the study authors on the DeepDTA training folds of the corrected Davis set (Appendix A)", and the protocol's first limitation now separates the proposed models' five-seed means from the baselines, whose seed averaging is not stated.
2. D2. The three KIBA baseline evaluations (KronRLS, SimBoost, DeepDTA) keep origin `unreported` and note that their printed values are identical to the Ozturk et al. 2018 KIBA table and were likely copied rather than rerun. The source carries an evidence concern against comparing those three rows with the proposed models automatically, and the KIBA protocol repeats the point.
3. D3. The four ESMC 600M configurations record version "ESMC 600M" and the PGraphDTA configuration records "ESM-2 650M, no contact maps (Section 3.3)", with their `missing_metadata.version` entries removed.

The reviewers wrote the evidence concerns with a `date` field; the store's concerns use `reviewed_at` with a `review_method`, so each concern carries `reviewed_at: 2026-10-11T00:00:00Z` and `review_method: ai-assisted-source-review`. Every message, locator and artifact hash is verbatim.

No use-case judgement or summary was written: the reviewer agreed that no extracted protocol bears directly on a use case in `data/entities/use-cases.jsonl`.

## Records after correction

- benchmark: 1
- configuration: 23
- dataset: 2
- evaluation: 32
- method: 2
- model: 4
- protocol: 2
- result: 64
- source: 1
