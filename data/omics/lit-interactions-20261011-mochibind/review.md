# Review: lit-interactions-20261011-mochibind, 2026-10-11

Reviewer: Claude review agent `reviewer-mi-1`, independent of the extractor `lit-microbial-interactions`. No human review claimed. Source transcription is not reproduction.

The reviewer's full report for this batch, with the checks run and their outcomes, is in [2026-10-11-microbial-interactions-lit.md](../../../docs/reviews/2026-10-11-microbial-interactions-lit.md).

## Reviewer's verdict (verbatim)

- `data/omics/lit-interactions-20261011-mochibind` (16 results): **approved with corrections**. Every
  printed value is right; the test-set denominator is stated in the source and must stop being
  recorded as unreported, and the Table 2 footnote conflict needs an evidence concern.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store.

1. M1. All 16 evaluations record `comparison.population` as 200,000 sampled antibody pairs from the held-out antigen with no affinity-difference threshold applied, which the source states in STAR Methods and again in Results, and the `missing_metadata` entry is removed. The 16 evaluation locators and the 16 result locators now also cite STAR Methods, "Cross-antigen evaluation setup".
2. M2. The same 16 evaluations record `comparison.aggregation` as the fraction of the 200,000 sampled test pairs in which the stronger binder was identified, and the `missing_metadata` entry is removed.
3. M3. An evidence concern on the source records that the Table 2 footnote claims the values are chi-squared statistics, contradicting the column headers, the cell contents and the body text, which places the chi-squared statistics in Table S1; the records read the cells as accuracies with a p-value, which the headers and body support.
4. M4. The four protocols now say that the columns are not matched on adaptation: Graphinity is the authors' own fine-tune of a third-party model while Boltz-2 and GeoDock are used without any fitting.

The reviewers wrote the evidence concerns with a `date` field; the store's concerns use `reviewed_at` with a `review_method`, so each concern carries `reviewed_at: 2026-10-11T00:00:00Z` and `review_method: ai-assisted-source-review`. Every message, locator and artifact hash is verbatim.

No use-case judgement or summary was written: the reviewer agreed that no extracted protocol bears directly on a use case in `data/entities/use-cases.jsonl`.

## Records after correction

- benchmark: 1
- configuration: 4
- dataset: 4
- evaluation: 16
- model: 3
- protocol: 4
- result: 16
- source: 1
