# Review: use-case-coverage-rna-splicing-20261011-silverstein2026, 2026-10-12

Reviewer: independent Claude review agent `reviewer-scnv`, separate from the extracting agent `uc-splicing-cnv`. No human review claimed. Source transcription is not reproduction. The full review, covering all five splicing and CNV batches, is `docs/reviews/use-cases/splicing-cnv-use-cases-2026-10-12.md`.

## Reviewer's report (verbatim)

| Batch | Verdict |
| --- | --- |
| `use-case-coverage-rna-splicing-20261011-silverstein2026` | Approved with corrections; the expression judgement is held (Tables S7 and S9 conflict) |

Applies to every batch: delete `extract/__pycache__/` from each batch folder before writing `review.json`, so the receipt does not hash compiled bytecode.

### silverstein2026: approved with corrections; expression judgement held

New finding: Table S7 conflicts with Table S9 on the expression negatives. In Tables S3, S4 and S8, "YES" in a true-negative row marks a sample with no outlier. That reading reproduces Table S9 for FRASER2.0 (4 TN, 2 FP), ANEVA-H (1 TN, 4 FP) and MAE (0 TN, 5 FP). Read the same way, Table S7 gives OUTRIDER 8 clean of 9 negative samples (5 of 6 muscle, 3 of 3 fibroblast), where Table S9 row 7 and the Results prose give 4 TN and 5 FP (56%). Table S7 lists 6 muscle negatives for OUTRIDER + GTEx, with 1 clean (5 of 6 = 83%, as in the prose), where Table S9 row 8 counts 5 (TN 1, FP 4). Neither reading of "YES" reconciles Table S7 with Table S9 row 7.

1. Do not add the `assessed_by` link for `rna-splicing-20261011-silverstein2026-protocol-expression`. Keep `use-case-mapping-rna-splicing-20261011-silverstein2026-expression` at `needs_review`, and keep `rna-splicing-20261011-silverstein2026-eval-outrider`, `-eval-outrider-plus-gtex` and their 18 results at `needs_review`. Remove the expression entry from `use-case-links.json`.
2. Append to `attributes.limitations` on `rna-splicing-20261011-silverstein2026-source-tables-s1-s10`, `rna-splicing-20261011-silverstein2026-protocol-expression` and `use-case-mapping-rna-splicing-20261011-silverstein2026-expression`:
   "Table S7 true-negative rows do not reproduce Table S9 rows 7 and 8: read as in Tables S3, S4 and S8 ('YES' = no outlier), Table S7 gives OUTRIDER 8 of 9 negative samples without outliers (Table S9: 4) and OUTRIDER + GTEx 1 of 6 (Table S9: 1 of 5). The prose rates (56% and 83%) match Table S9 for OUTRIDER and Table S7 for OUTRIDER + GTEx."
3. On all three protocols and all three judgement claims, replace the limitation beginning "Variants with clinically interpretable mechanisms were selected" with:
   "Variants with clinically interpretable mechanisms were selected; the authors state this favours clearly defined events and likely underestimates tool sensitivity, and that binary outlier scoring of negatives may overestimate false-positive rates and lowers MCC (Discussion, limitations paragraph)."

The splicing judgement is confirmed as `direct` and allelic imbalance as `proxy`. `reviewed_evaluations`:
- splicing: `rna-splicing-20261011-silverstein2026-eval-fraser`, `-fraser2-0`, `-leafcuttermd`, `-mintie`, `-rmats`
- allelic imbalance: `rna-splicing-20261011-silverstein2026-eval-aneva-h`, `-eval-mae`

Answers to the collector's questions that concern this batch:

1. Silverstein discrepancies. None of the five should be an `evidence_concern`. A concern on either Silverstein source withholds every result from it (`cleanSource` in `shared/omics/use-cases.ts`; `published-comparisons.ts`), including the direct splicing rows. Those rows agree across Tables S3 to S5, S9 and the prose, apart from the 22 versus 21 negative count. All five stay as limitations. The sixth conflict, Table S7 against Table S9 for OUTRIDER, is handled by holding the expression judgement (above), not by a concern.
2. ANEVA-H as `author_reported`: confirmed. Reference 36 is "Ganapathy KR, Broly M, Silverstein S, ..."; Ganapathy and Silverstein are authors here, and so is P. Mohammadi. Splicing `direct` and allelic imbalance `proxy` are confirmed. Expression would be `proxy`, but it is held.
3. Mixed units. The shared qualifier "positives per known event or gene, negatives per true-negative sample" plus the protocol limitation is enough. The summary cites only counts and recall, never accuracy, precision or MCC.

## Corrections applied

Applied by a separate Claude agent (not the reviewer) exactly as the reviewer specified, before the batch was added to the store.

1. Correction 1: the expression judgement, rna-splicing-20261011-silverstein2026-eval-outrider, -eval-outrider-plus-gtex and their 18 results stay needs_review; their review notes and the judgement's reason say they are held. The expression entry is removed from use-case-links.json, so no assessed_by link is added for protocol-expression.
2. Correction 2: the Table S7 versus Table S9 limitation appended to source-tables-s1-s10, protocol-expression and the expression judgement.
3. Correction 3: the event-selection limitation replaced with the reviewer's text on all three protocols and all three judgements.
4. Splicing stays direct and allelic imbalance proxy; reviewed_evaluations as listed. No evidence_concern is added (answer 1).
5. Every correction is applied in the extraction script under extract/ (marked 'review correction N'), and batch.jsonl, claims.csv, use-case-links.json and coverage.json were regenerated by rerunning it. A field-by-field comparison with the extracted batch shows no change beyond the corrections and the review fields.
6. Reviewed records are source_checked. Each result and claim carries the reviewer's review block (method, reviewer, reviewer_note, date, artifact_sha256 and retrieval_url from the source record; the extraction method description is kept as method_note; the note points to this file and the dated review). Each reviewed judgement lists the reviewer's reviewed_evaluations.
7. extract/__pycache__/ deleted before this receipt was written.

## Records after correction

- claim: 4
- configuration: 9
- dataset: 1
- evaluation: 9
- method: 3
- protocol: 3
- result: 81
- source: 2

Held at needs_review: 1 claim, 2 evaluation, 18 result. All other records are source_checked.
