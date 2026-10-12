# Review: use-case-coverage-ctdna-fragmentiawgs2026-20261011, 2026-10-12

Reviewer: Claude (Opus 5.5) review agent `reviewer-ctdna`, separate from the extracting agent `uc-ctdna`. No human review claimed. Source transcription is not reproduction. The full review, covering all five plasma ctDNA batches and the two use-case summaries, is `docs/reviews/use-cases/plasma-ctdna-use-cases-2026-10-12.md`.

## Reviewer's report (verbatim)

| Batch | Verdict |
| --- | --- |
| `use-case-coverage-ctdna-fragmentiawgs2026-20261011` | Approved with corrections (W1 to W5) |

### All batches

A1. Delete `extract/__pycache__/` in all five batch folders before the review receipt is written; compiled bytecode should not be hashed into `review.json` or committed.

A2. Locators of the form `Results P32`, `Methods P59` count `<p>` elements of the JATS XML from zero in document order, front matter included (checked: Zeng `P32` is the paragraph beginning "We next assessed the generalization", Helzer `P12` begins "In the UW cohort, we found that the FoundationOne Liquid CDx panel", Fragmentia-AI WGS `P19` begins "We then assessed the generalizability"). The convention is stated nowhere. In the four JATS source records (`ctdnalit-20261011-zeng2026-source-article`, `ctdnalit-20261011-helzer2025-source-article`, `ctdnalit-20261011-fragmentia2026-source-article`, `ctdnalit-20261011-fragmentiawgs2026-source-article`) replace `attributes.source_locator`

`Full artifact bytes; per-record locators on each record`

with

`Full artifact bytes; per-record locators on each record. 'Pn' is the zero-based index of the <p> element in document order in this JATS XML, front matter included.`

### Fragmentia-AI WGS (Molecular Biomedicine 2026)

W1. Supplementary Table S1 prints the class counts. Add to `ctdnalit-20261011-fragmentiawgs2026-data-train`: `"positives": 2450, "negatives": 1245`; to `ctdnalit-20261011-fragmentiawgs2026-data-validation`: `"positives": 894, "negatives": 1149`; and append ` Table S1: 2,450 cancers and 1,245 non-cancer controls.` and ` Table S1: 894 cancers and 1,149 non-cancer controls.` to their `population` strings.

W2. The limitation `Tumour-fraction strata are ichorCNA estimates; low TF (< 3%) is below ichorCNA's stated detection limit, so the stratum mixes truly low-TF cancers with misestimated ones.` adds an inference the paper does not make. In all four protocols and three judgements replace it with

`Tumour-fraction strata are ichorCNA estimates, not measured fractions; the authors chose the 3% cutoff because the ichorCNA study reported 0.03 as its lower limit for detecting tumour from ULP-WGS (Results P8), so the low stratum holds cancers whose tumour fraction ichorCNA cannot resolve.`

W3. Make `use-case-mapping-ctdna-lit-20261011-fragmentiawgs2026-test` `direct`. Its endpoint is the use case's: detection within ichorCNA tumour-fraction strata, including below 3%, at a false-positive cutoff fixed in advance, on whole-genome cfDNA, in a test cohort not used for fitting or selection. The proxy reasons given (no comparator, estimated strata, case-control, observed specificity 0.97) are limitations, not an endpoint mismatch; the CCGA methylation validation was judged `direct` with a post hoc threshold. Set `relevance` to `direct` and replace `rationale` with

`Measures the use case's endpoint for one workflow: detection within ichorCNA tumour-fraction strata, including below 3%, at a cutoff fixed in advance at 98% specificity in the training cohort and applied unchanged to an independent test cohort of 2,952 cancers and 3,044 non-cancer controls that was not used for fitting or model selection (observed specificity 0.97). Direct despite its limitations: the strata are ichorCNA estimates rather than measured tumour fractions, no comparator method is run on the cohort, the cohort is retrospective case-control, and the developer reports every value.`

Keep `proxy` for the validation judgement (the set was used for model selection) and the DELFI judgement (no strata, specificity 0.92 at the transferred cutoff, overlapping samples).

W4. Append to `attributes.limitations` of the test, validation and train protocols and of the test and validation judgements: `The training cohort has 1,245 non-cancer controls, the same number as the ULP-WGS cohort of the Fragmentia-AI paper (Cell Reports Medicine 2026) from the same company, so the two studies may share samples; neither paper says.`

W5. `coverage.json` `remaining_gaps` item 1 says cancer-type results are figure-only, but Results P19 prints test-cohort sensitivities for nine of 17 cancer types. Replace item 1 with `Per-stratum AUCs of the high/medium-TF scheme other than low TF, and cancer-type AUCs, are figure-only. Results P19 prints test-cohort sensitivity for nine of 17 cancer types (liver/biliary 0.88 to head and neck 0.29); these were not extracted because the list is partial.`

Answers to question 5: `recall` with the cutoff in the qualifier is correct. The vocabulary defines `sensitivity-at-98-percent-specificity` as recall at the threshold that gives 98% specificity, and the transferred cutoff gives 0.97 in the test cohort and 0.92 in the DELFI cohort. The DELFI overlap is recorded on the dataset, protocol and judgement. Question 7: the add order Helzer, Fragmentia-AI, Fragmentia-AI WGS is acceptable. Reusing the Fragmentia-AI method record is acceptable because it is a family record and each configuration carries the reported scheme name; the generic Griffin method under a `helzer2025` ID is acceptable because IDs are opaque.

## Corrections applied

Applied by the extractor's scripts as the reviewer specified, before the batch was added to the store. Where the reviewer gave text, it is used verbatim.

1. A1: extract/__pycache__/ deleted before the receipt was written.
2. A2: the article source's source_locator now states the zero-based <p> convention, in the reviewer's words.
3. W1: positives and negatives added to the train and validation datasets, and the reviewer's strings appended to their population.
4. W2: the tumour-fraction limitation replaced in all four protocols and three judgements.
5. W3: use-case-mapping-ctdna-lit-20261011-fragmentiawgs2026-test is direct, with the reviewer's rationale; validation and DELFI stay proxy.
6. W4: the reviewer's sample-overlap limitation appended to the train, validation and test protocols and the test and validation judgements.
7. W5: coverage.json remaining_gaps item 1 replaced.
8. Records not otherwise named are source_checked. Each result, descriptive claim and judgement carries the reviewer's review block (method, reviewer, reviewer_note, date and note; the extraction note moved to method_note). Each judgement lists the reviewer's reviewed_evaluations.
9. Corrections were applied in the extraction scripts under extract/ (marked with their review item), and batch.jsonl, claims.csv and use-case-links.json were regenerated from the pinned artifacts; coverage.json was updated to match.

Form change after the review, not a review item: extract/common.py now writes missing_metadata keys in sorted order, as the store keeps them (shared/omics/attributes.ts normalizeAttributes). This reorders the keys on 7 evaluations in batch.jsonl; no value, reason or note changed. The receipt was rewritten for the new file hashes.

## Records after correction

- claim: 3
- configuration: 3
- dataset: 4
- evaluation: 7
- protocol: 4
- result: 30
- source: 2

## Judgements

- `use-case-mapping-ctdna-lit-20261011-fragmentiawgs2026-delfi`: proxy, 1 reviewed evaluations
- `use-case-mapping-ctdna-lit-20261011-fragmentiawgs2026-test`: direct, 1 reviewed evaluations
- `use-case-mapping-ctdna-lit-20261011-fragmentiawgs2026-validation`: proxy, 3 reviewed evaluations
