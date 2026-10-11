# Review: genomic foundation model batches, 2026-10-11

Independent review of the three batches from the `lit-gfm-2` literature pass
(`data/omics/lit-search-20261011-gfm-2/report.md`). Reviewer: Claude (Opus 5.5) review agent `reviewer-gfm-a`. It
did not extract any of these batches. No human review is claimed. Source transcription is not reproduction.

Each batch folder holds the full review (`review.md`, with a row for every value checked), the receipt
(`review.json`, binding the SHA-256 of every file in the folder), the review script (`review/review.py`)
and the list of edits by record ID (`review/corrections.json`).

## Outcome

| Batch | Source | Pinned artifact SHA-256 | Values checked | Verdict |
| --- | --- | --- | --- | --- |
| `gfm2-20261011-buzkova2026` | Bůžková et al. 2026, bioRxiv 10.64898/2026.09.25.754388v1, CC BY 4.0 | `9a589a20…f75c19` (archived copy matches; fresh copies differ only in the per-request banner) | 90 results, 9 claims | Pass with corrections; 196 records |
| `gfm2-20261011-datta2026` | Datta et al. 2026, arXiv:2608.05329v1 | `df36e477…bb5c` (fresh download matches) | 144 results, 1 claim | Pass with corrections; 303 records; source blocked from automatic comparison by two evidence concerns |
| `gfm2-20261011-you2026` | You et al. 2026, Nat Commun, PMC12780105 and Supplementary Information, CC BY-NC-ND 4.0 | XML `2c6b2816…28e4`, supplement PDF `cbb69e05…d882` (both match) | 176 results, 1 claim | Pass with corrections; 22 results rejected to `data/omics/pending-review/gfm2-20261011-you2026-topk/`; 242 records |

No printed or numeric value was wrong in any batch. Every correction is to identity, metadata, uncertainty
type, qualifier or limitations.

## Main findings

- **Bůžková.** The text prints 95% Wilson intervals for five accuracy results, but they were marked
  unreported; they are now added. The Table 10 foundation-model rows had been linked to the Table 3
  best-pooling configurations, but the paper never states the long-sequence pooling. They now link to
  four new configurations with the pooling marked unreported. The precision and recall qualifiers are now
  consistent with the rest of each row. Table 9 prints 0.9244 for unperturbed NTv3-650M against 0.9265 in
  Tables 3, 6 and 7 (Table 9 is not extracted).
- **Datta.** Every printed recovery percentage agrees with the two extracted scores. The FT spreads are now
  typed `unresolved_spread`. The qualifiers name the task. Table 4 shows that Table 1's frozen values are
  test-set grid-best values. A second evidence concern records that Table 1 and Table 4 disagree on
  HyenaDNA Splice Acceptor. The duplicated NT enhancer cell is confirmed. A source-level concern blocks
  all of a source's results from automatic comparison, and that is kept on purpose.
- **You.** SpTransformer is the first author's own method (ref. 12), so its four evaluations are
  `author_reported`. The 500 bp input was wrongly applied to the NT splice-site datasets. SpliceAI and
  SpTransformer were retrained, not used as distributed. RNA-FM and GENA-LM duplicated existing store
  families. DNABERT and SpTransformer were `method` records. The "Average Top-k" results are rejected:
  the source defines top-k accuracy as the true label being among the top k predicted labels, with k
  unstated, which does not match `splice-top-k-accuracy`.

## Relevance judgements

None were proposed and none were added. I agree with the extractor that the nearest use cases
(`use-case-diagnostic-dna-pathogen-identification`, `use-case-splicing-follow-up`) would be weak proxies.

## Remaining gaps

- Bůžková Tables 4, 5, 6, 8, 9 and 11; Datta Tables 2 to 9; You Supplementary Tables 2, 3 and 6. No figures
  were read.
- Datta's single NT benchmark dataset record should be repointed to the per-task records from the
  `lit-genomics` pass once they land.
- `catalog-model-nt-v2` is a family record with `version` "50M multi-species", and the Bůžková 250M and 500M
  configurations link to it. That existing record is not changed here.

## Store change recorded by this review

The Bůžková and Datta batches were added to the store (commits `1db08e4` and `9aa8074`) before `npm test`
had run. `tests/attributes.test.ts` ("leaves current records unchanged") then failed on 250 of their
records, for two reasons. The review blocks carried both `date` and `reviewed_at`, and the attribute
normaliser drops `date` when `reviewed_at` is present. The four new long-sequence configurations also
listed their `missing_metadata` keys out of sorted order. The review scripts now write `date` only and
sorted keys. The batches were regenerated from the extractor output. The 250 stored records were replaced
with the regenerated versions and recorded with `npm run records -- change` against this review. No
value, link or status changed.

## Checks run

- Each batch passes the store's schema, vocabulary, attribute and relation checks (`addBatch` against a
  scratch copy of the store). The You batch has not been added to the store.
- `npm run records -- check`: 46,103 records match their provenance.
- `npm test`: 48 files, 515 tests passed (after the store change above).
- `npm run typecheck`: passed.
- `npm run build`: passed. Its packaged website output was discarded, not committed; packaging belongs to
  the release step.
