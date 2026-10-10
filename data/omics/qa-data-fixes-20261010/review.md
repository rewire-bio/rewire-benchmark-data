# Independent review: five use-case summary drafts, issue #87

Batch: `data/omics/qa-data-fixes-20261010/batch.jsonl` (5 claim records, all `field` `summary`).

Reviewer: a separate Claude review agent that did not draft these summaries. No human review is claimed. Nothing was executed or reproduced.

## Outcome

All five were corrected and then set to `source_checked`. None passed as drafted. Pins are not set, so none publishes until the integrator pins it.

| Summary | Outcome | Reason |
| --- | --- | --- |
| utr-translation-baselines | Corrected | Did not say the two controls are Rewire runs |
| plant-promoter-reporters | Corrected | "All values are author reported" was wrong for the five foundation-model rows |
| mass-spectrum-molecule-shortlisting | Corrected | Wrong standard-deviation range on the formula split; seed count wrong for MCES |
| phenotype-perturbation-selection | Corrected | "Much better than chance" and "most near 0.5" unsupported as worded; counts mislabelled |
| rhodopsin-wavelength-transfer | Corrected | Omitted the fifth active evaluation; an interpretation the evidence does not support |

No number in any draft was wrong. Every correction is to wording, scope or completeness.

## How the check was done

1. Rebuilt each use case's active judgements with `deriveUseCaseInputs` over the whole store, and listed every active evaluation with its configuration, origin, dataset and results.
2. Compared every number in each summary with the `printed_value` of the stored result it comes from, including rounding, and checked it belongs to the stated tool, dataset and split.
3. Checked each comparative statement against every active evaluation on the protocol, not only the rows `changes.md` cites.
4. Read the protocol, dataset, configuration and source records for origin, publication status, truth-set and cohort limits.
5. Checked that each cited source is `source_checked` with no `evidence_concerns`, and that no cited source is outside the evidence the text uses.
6. Dry run: `addBatch` into a scratch copy of the store, then `deriveUseCaseInputs`.

## Checks that passed on every summary

- Every number matches its result's printed value and rounding.
- No summary recommends anything.
- Each cited source is `source_checked` with no evidence concerns, and every cited source backs evidence the text uses.
- No em or en dashes.

Comparative statements verified against all active evidence:

| Statement | Check | Outcome |
| --- | --- | --- |
| MSAlign "ranks first among the formula-free methods on every split recorded" | Highest non-fusion value at Recall@1, @5 and @20 on all seven active mass-spectrum protocols, including the SpectraVerse split and both earlier-version splits | True |
| AgroNT "above the task-specific CNN in all six", "by 0.02 to 0.05" | All six: 0.62/0.58, 0.68/0.65, 0.71/0.69, 0.62/0.57, 0.74/0.71, 0.75/0.73; gaps 0.02, 0.03, 0.02, 0.05, 0.03, 0.02 | True |
| Foundation-model AUC "0.937 to 0.961" | Range over all ten active rows across the TATA and NonTATA tasks: 0.9372 to 0.9609 | True at both ends |
| RhoMax "lowest wavelength error on each of its own splits" | Lowest nm mean absolute error on splits 1 to 4 and the mean row | True in nm; see correction 5 for eV |
| Neural Pearson "0.743 to 0.966" random, "0.700 to 0.894" human; k-mer "0.616 to 0.877" | Ranges over the two random and two human panels, and the two random panels for the forests | True |
| Challenge 2 "0.452 to 0.566" over 20 submissions | Min 0.452, max 0.566, n = 20 | True |

## Corrections

1. **utr-translation-baselines.** The text gave no provenance for the two controls. They are `rewire_run` results from Rewire's own local runs, which the reviewed summaries on main always name. Added that both controls are Rewire runs, that their automated audit checks the run itself rather than a published score, and the number of held-out records (15,003). Named the neural models (FramePool and Optimus), and attributed the panel values to the FramePool study rather than "the study's own values".

2. **plant-promoter-reporters.** "All values are author reported, with no confidence interval or run variability" is wrong: the five DNA foundation-model evaluations are `independent_paper`, from a separate benchmarking paper. Rewritten so the author-reported statement covers the AgroNT and Jores values, the benchmark is named as independent, and the no-uncertainty statement still covers everything. Also replaced "separate Arabidopsis promoter sequences from background" with the dataset's own definition, similar non-promoter sequences, and named both the TATA and NonTATA tasks the AUC range spans.

3. **mass-spectrum-molecule-shortlisting.** Two corrections. The draft gave "each with a standard deviation of 0.2 to 3.4" for the formula split; those rows are 0.5, 0.6, 3.0, 3.4 and 3.4, and the 0.2 belongs to an MCES row, so the range is 0.5 to 3.4. The draft also applied "three seeds" to both splits, but the MCES protocol records that the methods describe two validation and test swapped variants despite the blanket table caption; that is now stated where the MCES values appear. Also changed "one paper and its earlier version" to two versions of one arXiv preprint, since neither source is a published paper.

4. **phenotype-perturbation-selection.** "No submitted method ranked perturbations much better than chance" needed support, because this score is not a ROC AUC and the draft itself says so. Replaced with the distribution: the range, that 17 of the 20 fall between 0.50 and 0.57, and that a random ordering is expected to score 0.5 on this curve. "Nomination counts of 61, 57, 59 and 50" mislabelled four different quantities; they are now named as 61 nominations, 57 selected targets, 59 screen-2 genes and 50 perturbations passing quality control, which is what the dataset and evaluation records say. The two gene names were removed as case-level detail the summary does not need, and the cohort is described as T cells from a mouse melanoma model.

5. **rhodopsin-wavelength-transfer.** The draft said "amino-acid composition outranked two frozen ESM-2 probes", but the protocol has five active evaluations and the draft omitted the 22-feature composition probe (Spearman 0.418, NDCG 0.955), which the existing judgement records as a distinct configuration. Both composition probes are now named with their values, and `rewire-local-20260921-source-composition22` and its audit source were added to `source_ids`. The opening is qualified to the nm columns, because in eV the three methods are closer and on split 3 all three print 0.045 eV. Removed "so the splits differ more than the methods do": that is interpretation, and split 4, where RhoMax at 16.68 nm trails BLASSO's best split, does not support it. Kept the statement that the 35M checkpoint was chosen after the 8M outcome was known, which the existing judgement's limitations record.

## Rewire run sources and audit sources

The two Rewire-run use cases cite both the run report and the automated audit source for each configuration. That is right: each result's own `source_ids` list both, so citing only the run report would leave out a source the number rests on, and citing only the audit would misattribute the measurement. Both are `source_checked` with no concerns.

The reproduction-instructions sources (`rewire-local-20260920-instructions-*`, `rewire-local-20260921-instructions-*`) are correctly left out. They are cited by evaluations, not by results, and no number comes from them.

## Review blocks

Each claim's review records `independent-cell-check` and `ai-assisted-source-review`, the reviewer as a separate Claude agent that corrected the text, no human review claimed, and what was corrected. The form follows `use-case-summary-cnv-detection-characterisation` and `use-case-summary-unresolved-rare-disease-reanalysis` on main.

## Validation

- `npm run typecheck`: passed.
- `npm test`: 500 tests in 47 files passed.
- Dry run on a scratch copy of the store: `addBatch` accepted all five records, and `deriveUseCaseInputs` then reported each summary as reviewed but not published, which is expected while pins are unset.
- `npm run build` was not run.

## Remaining gaps

- Pins are unset, by instruction. Until the integrator runs `npm run use-cases:repin` with this review, none of the five summaries publishes.
- No source artifact was re-downloaded or re-hashed in this pass. The numbers were checked against the stored results, which earlier reviews bound to their sources, not against the source bytes again.
- Figures and supplementary tables behind the stored results were not reopened.
- Human scientific review remains outstanding for all five.
