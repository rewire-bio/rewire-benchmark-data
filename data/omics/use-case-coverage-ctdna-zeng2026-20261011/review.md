# Review: use-case-coverage-ctdna-zeng2026-20261011, 2026-10-12

Reviewer: Claude (Opus 5.5) review agent `reviewer-ctdna`, separate from the extracting agent `uc-ctdna`. No human review claimed. Source transcription is not reproduction. The full review, covering all five plasma ctDNA batches and the two use-case summaries, is `docs/reviews/use-cases/plasma-ctdna-use-cases-2026-10-12.md`.

## Reviewer's report (verbatim)

| Batch | Verdict |
| --- | --- |
| `use-case-coverage-ctdna-zeng2026-20261011` | Approved with corrections (Z1 to Z6) |

### All batches

A1. Delete `extract/__pycache__/` in all five batch folders before the review receipt is written; compiled bytecode should not be hashed into `review.json` or committed.

A2. Locators of the form `Results P32`, `Methods P59` count `<p>` elements of the JATS XML from zero in document order, front matter included (checked: Zeng `P32` is the paragraph beginning "We next assessed the generalization", Helzer `P12` begins "In the UW cohort, we found that the FoundationOne Liquid CDx panel", Fragmentia-AI WGS `P19` begins "We then assessed the generalizability"). The convention is stated nowhere. In the four JATS source records (`ctdnalit-20261011-zeng2026-source-article`, `ctdnalit-20261011-helzer2025-source-article`, `ctdnalit-20261011-fragmentia2026-source-article`, `ctdnalit-20261011-fragmentiawgs2026-source-article`) replace `attributes.source_locator`

`Full artifact bytes; per-record locators on each record`

with

`Full artifact bytes; per-record locators on each record. 'Pn' is the zero-based index of the <p> element in document order in this JATS XML, front matter included.`

### Zeng et al. 2026

Z1. The source-level evidence concern would withhold every Zeng judgement. `cleanSource` in `shared/omics/use-cases.ts` rejects any source with a non-empty `evidence_concerns`, and every Zeng protocol, configuration, dataset and result cites `ctdnalit-20261011-zeng2026-source-source-data-fig4`. Follow the Hou et al. 2024 precedent (result-level dispute) instead:
- In `ctdnalit-20261011-zeng2026-source-source-data-fig4`, delete `attributes.evidence_concerns`.
- In `ctdnalit-20261011-zeng2026-result-pe-validation-methylation-auroc`, set `status` to `disputed`, add `attributes.source_warnings` = `["Source Data Fig. 4 sheet Fig.4c cell B6 prints a mean AUC of 0.69415032679738597 for the methylation-only classifier in the PE validation dataset; Results P32 of the article prints 0.674 for the same quantity. The other validation AUCs quoted in the text (0.954, 0.848) match the sheet. Which figure is right cannot be told from the source. The value is kept as printed and does not support comparison (independent review 2026-10-12)."]`, and replace `attributes.source_discrepancy` with `Results P32 prints 0.674 for this value; the sheet prints 0.69415032679738597. See source_warnings.`
- Update `sources.md` ("Evidence concern recorded on ..." paragraph), `retrieval-log.md` line 17 and `coverage.json` `remaining_gaps` item 4 to say the conflict is recorded as a disputed result with a source warning, not as a source evidence concern.
The evaluation `ctdnalit-20261011-zeng2026-eval-pe-validation-methylation` stays eligible through its sensitivity result.

Z2. Exclude the five classifiers that include end motifs from both PE validation judgements. The authors attribute their validation scores to a protocol difference in the healthy controls (Results P32: "Differences in 5' motif baselines for the HCC healthy controls ... reduced mAUCs and 99%-specificity sensitivities for motif-containing classifiers"), so those values measure a pre-analytical batch effect rather than the classifiers; three of them are below AUC 0.5 (0.066, 0.188, 0.455). In `use-case-mapping-ctdna-lit-20261011-zeng2026-meth-pe-validation` and `use-case-mapping-ctdna-lit-20261011-zeng2026-frag-pe-validation` add

`"excluded_evaluations": [{"id": "ctdnalit-20261011-zeng2026-eval-pe-validation-end-motifs", "reason": "Includes 5' end motifs; the authors attribute motif-containing classifiers' validation scores to a laboratory-protocol difference in the HCC-study healthy controls (Results P32), so the values reflect that batch effect, not the classifier."}, {"id": "ctdnalit-20261011-zeng2026-eval-pe-validation-motif-methylation-1pct", "reason": <same text>}, {"id": "ctdnalit-20261011-zeng2026-eval-pe-validation-motif-methylation-ratios-1pct", "reason": <same text>}, {"id": "ctdnalit-20261011-zeng2026-eval-pe-validation-all-features-1pct", "reason": <same text>}, {"id": "ctdnalit-20261011-zeng2026-eval-pe-validation-all-features-5pct", "reason": <same text>}]`

(`<same text>` is the first reason string, repeated.) The results and their `source_anomaly` notes stay as they are. Also correct the report, which says two validation AUCs are below 0.5; it is three (all-features-1pct 0.455 as well), and all three carry `source_anomaly` already.

Z3. Sensitivity at 99% specificity is read on very few healthy controls, which none of the records says. Append one string to `attributes.limitations`:
- `ctdnalit-20261011-zeng2026-protocol-pe-primary-cv`, and judgements `...-meth-pe-primary-cv` and `...-frag-pe-primary-cv`: `Sensitivity at 99% specificity is read within each outer fold, which holds six or seven of the 64 healthy donors, so a 99% specificity threshold allows no false positive among them (counts from the source; the resolution is Rewire arithmetic).`
- `ctdnalit-20261011-zeng2026-protocol-pe-validation`, and judgements `...-meth-pe-validation` and `...-frag-pe-validation`: `The validation set has 17 healthy controls (Results P28 and P32), so a 99% specificity threshold allows no false positive among them (counts from the source; the resolution is Rewire arithmetic).`
- `ctdnalit-20261011-zeng2026-protocol-se-primary-cv` and judgement `...-meth-se-primary-cv`: `Sensitivity at 99% specificity is read within each outer fold, which holds seven or eight of the 76 healthy donors, so a 99% specificity threshold allows no false positive among them (counts from the source; the resolution is Rewire arithmetic).`
- `ctdnalit-20261011-zeng2026-protocol-se-validation` and judgement `...-meth-se-validation`: `The hold-out set has 9 healthy controls, so a 99% specificity threshold allows no false positive among them (counts from the source; the resolution is Rewire arithmetic).`
(Judgement IDs abbreviated; full prefix `use-case-mapping-ctdna-lit-20261011-zeng2026-`.)

Z4. The spread note is accurate but incomplete: Methods P61 says "error bars denote across-fold s.d.", the Figure 4 legend says s.e. for panels b, d, f and h, and Results P29 and P33 quote the sd_sens99 values as "± ... across folds". Keep `unresolved_spread`; in each sensitivity result's `uncertainty.note` append ` Methods P61 says error bars denote across-fold s.d.`

Z5. Keep `proxy` for the four methylation judgements (question 2). The 99% specificity is read on 6 to 17 healthy controls (Z3), the sensitivities count Li-Fraumeni carriers without cancer as cancers, and the developer ran every arm, so this is not the use case's declared-specificity endpoint in the way the CCGA validation is.

Z6. In `research.md` or the report, no change needed for the validation-size conflict (95 in Results P28, n = 140 in the Extended Data Fig. 9f legend); it is recorded on the dataset and protocol. Confirmed against the source.

## Corrections applied

Applied by the extractor's scripts as the reviewer specified, before the batch was added to the store. Where the reviewer gave text, it is used verbatim.

1. A1: extract/__pycache__/ deleted before the receipt was written.
2. A2: the article source's source_locator now states the zero-based <p> convention, in the reviewer's words.
3. Z1: evidence_concerns removed from ctdnalit-20261011-zeng2026-source-source-data-fig4; ctdnalit-20261011-zeng2026-result-pe-validation-methylation-auroc is disputed, carries the reviewer's source_warnings and source_discrepancy text; sources.md, retrieval-log.md line 17 and coverage.json remaining_gaps item 4 now say the conflict is a disputed result with a source warning.
4. Z2: the five motif-containing evaluations are in excluded_evaluations of both PE validation judgements, with the reviewer's reason; the pass report now says three validation AUCs are below 0.5.
5. Z3: the reviewer's healthy-control limitation appended to each of the four protocols and to the six judgements.
6. Z4: ' Methods P61 says error bars denote across-fold s.d.' appended to uncertainty.note of the 26 sensitivity results.
7. Z5, Z6: no change (relevance stays proxy; validation-size conflict already recorded).
8. Records not otherwise named are source_checked (one result is disputed, Z1). Each result, descriptive claim and judgement carries the reviewer's review block (method, reviewer, reviewer_note, date and note; the extraction note moved to method_note). Each judgement lists the reviewer's reviewed_evaluations.
9. Corrections were applied in the extraction scripts under extract/ (marked with their review item), and batch.jsonl, claims.csv and use-case-links.json were regenerated from the pinned artifacts; coverage.json was updated to match.

Form change after the review, not a review item: extract/common.py now writes missing_metadata keys in sorted order, as the store keeps them (shared/omics/attributes.ts normalizeAttributes). This reorders the keys on 26 evaluations in batch.jsonl; no value, reason or note changed. The receipt was rewritten for the new file hashes.

## Records after correction

- claim: 8
- configuration: 10
- dataset: 4
- evaluation: 26
- method: 1
- protocol: 4
- result: 52
- source: 2

## Judgements

- `use-case-mapping-ctdna-lit-20261011-zeng2026-frag-pe-primary-cv`: proxy, 10 reviewed evaluations
- `use-case-mapping-ctdna-lit-20261011-zeng2026-frag-pe-validation`: proxy, 5 reviewed evaluations, 5 excluded
- `use-case-mapping-ctdna-lit-20261011-zeng2026-meth-pe-primary-cv`: proxy, 10 reviewed evaluations
- `use-case-mapping-ctdna-lit-20261011-zeng2026-meth-pe-validation`: proxy, 5 reviewed evaluations, 5 excluded
- `use-case-mapping-ctdna-lit-20261011-zeng2026-meth-se-primary-cv`: proxy, 3 reviewed evaluations
- `use-case-mapping-ctdna-lit-20261011-zeng2026-meth-se-validation`: proxy, 3 reviewed evaluations
