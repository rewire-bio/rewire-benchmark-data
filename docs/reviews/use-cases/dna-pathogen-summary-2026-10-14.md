# Use-case summary: DNA pathogen identification, re-review, 2026-10-14

Issue #145. Claim: `use-case-summary-diagnostic-dna-pathogen-identification`.

Reviewer: a separate Claude review agent that did not draft the summary, extract the BERTax or MetageNN batches, or carry out the 2026-10-12 review (`dna-pathogen-summary-2026-10-12.md`). No human review is claimed.

The summary holds. No text, source or locator changes.

## State before this review

The issue reports the summary as withheld after PR #134. In the store it is not: its pins match, its eleven sources are `source_checked` with no `evidence_concerns`, and `deriveUseCaseInputs` publishes it. It was re-pinned in #134 itself (commit 23785d2, after the 2026-10-12 review) and is published as `reviewed` in releases 2026-10-12-5b983e4ada23, 2026-10-14-a2714d701935 and 2026-10-14-53895165fa97. I could not load the live use-case page (the site returned HTTP 429), so I cannot say what the issue's author saw; the release artifacts both carry the summary.

## Method

- Listed the active judgements on the use case (25 of 27; the two Song et al. 2025 judgements are withheld for a source concern, as before) and their 153 reviewed evaluations.
- Matched every number in the text against the stored `source_checked` results on those evaluations (value, interval or denominator), with a script written for this review.
- Read the five judgements added in #134 (`dna-pathogen-20261012-bertax-{closely,distantly,final}`, `dna-pathogen-20261012-metagenn-{isolates,mocks}`) and the use case's amended evidence gaps against the text.
- Checked that no withheld judgement is described, that the text does not recommend, that developer origin and non-clinical data are stated for the trained classifiers, and that it has no em or en dash.

## Numbers

| Text | Stored result (prefix `dna-pathogen-`) | Outcome |
| --- | --- | --- |
| 76.11, 75.59 | `20261012-bertax-result-{kraken2,minimap2}-closely-superkingdom-proportion-classified` | Match |
| 99.82, 99.95 | `20261012-bertax-result-{kraken2,minimap2}-closely-superkingdom-accuracy` | Match |
| 21.56, 19.88 | `20261012-bertax-result-{kraken2,minimap2}-distantly-superkingdom-proportion-classified` | Match |
| 90.71, 94.42 | `20261012-bertax-result-{kraken2,minimap2}-distantly-superkingdom-accuracy` | Match |
| 94.78, 88.95 | `20261012-bertax-result-bertax-{closely,distantly}-superkingdom-accuracy` | Match |
| 93.26, 64.90, 53.06, 85.49 | `20261012-metagenn-result-{metagenn,kraken2,megan-lr,mmseqs2}-mocks-reads-classified` | Match |
| 93.7 (59 of 63) | `amp-20261007-dna-pathogens-result`, denominator 63 | Match |
| 81.3, 51.9; 82.7 (134 of 162) | `20261011-wolf2026-result-{diagnosis,prediction}-all-raw-sensitivity`, `specificity-any-all-specificity` (n 162) and `-negative` (134) | Match |
| 95.2, 44.6, 46.4; 93.3, 90.7 | `20261011-hu2026-result-culture-{mgi,hdont}-all-{ppa,npa}`, `crs-{mgi,hdont}-all-ppa` | Match |
| 63.46, 35.58, 49.04, 9.62; 44.44, 61.11 | `20261011-huang2026-result-all-{bstngs,mngs,cmt,culture}-sensitivity`, `all-{bstngs,mngs}-specificity` | Match |
| 0.07 to 0.74; 0.97 to 0.995 | `20261009-hall2024-result-*-kraken2-standard-sensitivity` (0.0731 to 0.7408) and `-myco-sensitivity` (0.9715 to 0.9953) | Match after rounding |

The Portik and Tisza sentences were re-read against the 2026-10-11 review; their records and pins are unchanged.

## Against the new judgements and gaps

- The text describes the `closely`, `distantly` and `mocks` judgements and says both papers come from the classifiers' developers and use simulated or isolate-derived data. It does not describe `bertax-final` or `metagenn-isolates`; nothing in it contradicts them.
- Accuracies are paired with the share assigned, and the MetageNN shares are stated as reads assigned, not reads assigned correctly, which matches the gap on Peres da Silva et al. 2024 (only the assigned share is printed as a value).
- The amended gaps (machine-learning comparisons only on non-clinical data; no clade-exclusion benchmark with a pathogen focus; Song et al. 2025 under a concern) agree with the text. The text does not mention Song et al. 2025.

## Changes

None to the text or its sources. The claim's `review` block now names this review. Its pins already match the store; `use-cases:repin` was run on it and reported no change.

## Remaining gaps

- The live page could not be checked from here. After the next release, confirm that the use-case page shows the summary.
- No human scientific review.
