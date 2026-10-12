# Mass-spectrum molecule shortlisting: MassSpecGym in the Wild links, 2026-10-12

Use case: `use-case-mass-spectrum-molecule-shortlisting`. Batch: `data/omics/lit-otheromics-20261011-msgwild/` (PR #125). Batch review: [2026-10-12-rna-other-omics-batches.md](../2026-10-12-rna-other-omics-batches.md).

This change applies the use-case part of that review, which PR #125 deferred. The owner approved adding the links. The judgement text and the links were approved by `reviewer-ro-2`, a Claude review agent that did not extract the batch. No human review is claimed. This change was applied by a different Claude agent, which made no judgement of its own.

## Changes

1. `use-case-mass-spectrum-molecule-shortlisting` gains two `assessed_by` links, as proposed in the batch's `use-case-links.json`:
   - `lit-otheromics-20261011-msgwild-protocol-mass-retrieval-hit-rate-1`
   - `lit-otheromics-20261011-msgwild-protocol-mass-retrieval-hit-rate-20`

   No other use-case field changes.
2. The two judgement claims move from `needs_review` to `source_checked`, with a review block naming reviewer-ro-2 (method `automated-source-review`, no human review):
   - `use-case-mapping-lit-otheromics-20261011-msgwild-mass-retrieval-hit-rate-1`
   - `use-case-mapping-lit-otheromics-20261011-msgwild-mass-retrieval-hit-rate-20`
3. Both claims are pinned with `npm run use-cases:repin`.

The claims on main already carried reviewer-ro-2's M8 rationale, four constraints and six limitations verbatim; a script compared each string with the review file and found no difference. `relevance` stays `proxy`. `endpoint`, `excluded_evaluations` (the four grey rows per protocol) and the other fields are unchanged. `reviewed_evaluations` is the reviewer's list:

| Claim | Reviewed evaluations | Stored result (99.9% interval) |
| --- | --- | --- |
| hit-rate-1 | `lit-otheromics-20261011-msgwild-eval-random-ranking-mass-retrieval-hit-rate-1` | 0.43 (0.29 to 0.61) |
| hit-rate-1 | `lit-otheromics-20261011-msgwild-eval-mist-retrieval-with-mist-cf-top-1-predicted-formula-mass-retrieval-hit-rate-1` | 26.64 (25.53 to 27.75) |
| hit-rate-20 | `lit-otheromics-20261011-msgwild-eval-random-ranking-mass-retrieval-hit-rate-20` | 7.99 (7.34 to 8.74) |
| hit-rate-20 | `lit-otheromics-20261011-msgwild-eval-mist-retrieval-with-mist-cf-top-1-predicted-formula-mass-retrieval-hit-rate-20` | 54.90 (53.69 to 56.06) |

Values are percentages of MassSpecGym test spectra, with 99.9% bootstrap intervals, from Table 2 of arXiv:2606.19624v1. All four results are `source_checked` by reviewer-ro-2.

## Reviewer approval

From `reviewer-ro-2`'s report (2026-10-12), M8:

> Replace these fields in both `use-case-mapping-lit-otheromics-20261011-msgwild-mass-retrieval-hit-rate-1` and `use-case-mapping-lit-otheromics-20261011-msgwild-mass-retrieval-hit-rate-20`. Keep `relevance` as `proxy`. Keep endpoint, excluded_evaluations and the other fields as they are.

> Use-case fields: no change approved. Keep `use-case-mass-spectrum-molecule-shortlisting` as it is, exclusions and inputs included. The exclusion "Formula-conditioned retrieval, including MIST, FLARE and MSAlign+Filter" was written for MSAlign's formula-supplied rows. The judgement above keeps MIST with a predicted formula inside the use case's question without editing its scope. The proposed `assessed_by` links in use-case-links.json are approved as written.

From the answer to report question 4:

> The grey-row handling is correct: separate configurations, each with a limitation, all excluded from the judgements. I checked the grey state in my own HTML parse and on the rendered PDF.

> MIST with a MIST-CF predicted formula is not caught by the exclusion as intended. It is accepted as proxy with the M8 text.

## State after the change

Checked with `deriveUseCaseInputs` before and after:

- Both msgwild judgements are active, each with the two reviewed evaluations.
- The seven existing judgements on this use case stay active. No judgement on any use case that was active before is withheld or dropped.
- The summary claim `use-case-summary-mass-spectrum-molecule-shortlisting` is no longer published. Its pins include the reviewed evaluations of every reviewed judgement on the use case, so the two new judgements withhold it. Its text is also out of date: it says every value comes from two versions of one arXiv preprint. It is not re-pinned. A replacement is drafted in `data/omics/use-case-followups-20261012/summary-drafts.md` for separate review.

## Remaining gaps

- The use case's `setting` and `output` still describe only MSAlign's Table 3 (256-candidate pools, six configurations). The reviewer approved no field change, so they are unchanged. A later reviewed change could describe the MassSpecGym in the Wild pool as well.
- MassSpecGym in the Wild Table 8 (MIST-CF top-5 formulas) and Table 7 (formula accuracy) are not extracted.
