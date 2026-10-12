# Review: lit-microbial-20261011-virobench, 2026-10-11

Reviewer: Claude review agent `reviewer-mi-1`, independent of the extractor `lit-microbial-interactions`. No human review claimed. Source transcription is not reproduction.

The reviewer's full report for this batch, with the checks run and their outcomes, is in [2026-10-11-microbial-interactions-lit.md](../../../docs/reviews/2026-10-11-microbial-interactions-lit.md).

## Reviewer's verdict (verbatim)

- `data/omics/lit-microbial-20261011-virobench` (912 results): **approved with corrections**. Every
  printed value is right; the corrections are two source-level evidence concerns and one protocol
  limitation wording.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store.

1. V1. Evidence concern added to the source record: the Table 25 taxonomy columns equal the rounded mean of the five Table 26 per-rank values for 143 of 144 ALL-virus cells, the exception being RNA-FM under the genus-disjoint split (48.67 printed against 53.10 as the mean), so that row should not be used in a comparison without checking the published code.
2. V2. Second evidence concern added to the source record: Table 3 lists NT v3 under phage-specific pretraining coverage and Table 9 as non-viral, so NT v3 rows should not support a coverage-versus-performance claim. The existing source limitation is kept.
3. V3. The six taxonomy protocols now say that the source predicts five ranks through five parallel heads and never states how they are combined, that the printed value equals the rounded mean of the Table 26 per-rank values for 143 of 144 ALL-virus cells, and that the mean is an observation rather than a stated aggregation from which no value was computed. The DNA and RNA taxonomy protocols add that Table 26 covers the ALL-virus set only, so the aggregation cannot be checked for those two sets.
4. V4. The six host protocols now carry the source's own caveat that host classification is single-label while many viruses have multi-host tropism, which can penalise biologically reasonable secondary host associations.

The reviewers wrote the evidence concerns with a `date` field; the store's concerns use `reviewed_at` with a `review_method`, so each concern carries `reviewed_at: 2026-10-11T00:00:00Z` and `review_method: ai-assisted-source-review`. Every message, locator and artifact hash is verbatim.

No use-case judgement or summary was written: the reviewer agreed that no extracted protocol bears directly on a use case in `data/entities/use-cases.jsonl`.

## Records after correction

- benchmark: 1
- configuration: 76
- dataset: 6
- evaluation: 912
- method: 2
- model: 10
- protocol: 12
- result: 912
- source: 1
