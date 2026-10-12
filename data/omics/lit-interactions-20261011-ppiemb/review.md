# Review: lit-interactions-20261011-ppiemb, 2026-10-11

Reviewer: Claude review agent `reviewer-mi-2`, independent of the extractor `lit-microbial-interactions`. No human review claimed. Source transcription is not reproduction.

The reviewer's full report for this batch, with the checks run and their outcomes, is in [2026-10-11-microbial-interactions-lit.md](../../../docs/reviews/2026-10-11-microbial-interactions-lit.md).

## Reviewer's verdict (verbatim)

| `lit-interactions-20261011-ppiemb` (bbag313, 308 results) | Approved with corrections |

Every printed value in all three batches matches its source. The corrections below are metadata only:
training and adaptation descriptions, origin, populations, splits, units and limitations. None changes a
number.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store.

1. P1. The four protocols and the source now say that no per-cell uncertainty or run count is printed and that the footnote of Tables 5 and 6 gives only the table-wide maximum standard deviation (0.0711 OGBl-ppa, 0.0928 HuRI). All 308 results carry that note on `missing_metadata.uncertainty`, keeping the reason `unreported`.
2. P2. The HuRI dataset's invented split is removed and recorded as `unreported`, because the main text does not describe the HuRI train and test edge split, and its version now points to Supplementary Table S1, which was not retrieved. The OGBl-ppa split says the OGB split is implied by the reproduced leaderboard hyperparameters but not confirmed. The 154 HuRI evaluations have `comparison.split` null with reason `unreported`.
3. P3. The 28 evaluations whose system is a majority-vote ensemble configuration are `author_reported`, because the ensemble is the study authors' own construction. The other 280 remain `independent_paper`.
4. P4. The ProstT5 model record and its seven configurations note that Tables 5 and 6 print ProstT5 under Structure while Experimental design names ProtT5 as the third structure embedding, that the table label was followed, and that Supplementary Table S3 was not retrieved.
5. P5. The source's evidence concern now also records that the random-feature baselines on OGBl-ppa (GCN 0.0588, GS 0.0104 Hits@100) look far below the public OGB leaderboard values the authors say they reproduced, with Supplementary Table S2 not retrieved and the leaderboard values not verified by the reviewer.

The reviewers wrote the evidence concerns with a `date` field; the store's concerns use `reviewed_at` with a `review_method`, so each concern carries `reviewed_at: 2026-10-11T00:00:00Z` and `review_method: ai-assisted-source-review`. Every message, locator and artifact hash is verbatim.

No use-case judgement or summary was written: the reviewer agreed that no extracted protocol bears directly on a use case in `data/entities/use-cases.jsonl`.

## Records after correction

- benchmark: 1
- configuration: 77
- dataset: 2
- evaluation: 308
- method: 11
- model: 3
- protocol: 4
- result: 308
- source: 1
