# Review: lit-otheromics-20261011-msgwild, 2026-10-12

Reviewer: Claude review agent `reviewer-ro-2`, independent of the extractor `lit-rna-otheromics`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

Excerpts of `reviewer-ro-2`'s report that concern this batch, unedited.

Reviewer: Claude (Opus 5.5) research agent, reviewer-ro-2. No human review claimed. I did not extract any of these batches.

Every printed value in all four batches matches the source. All corrections are to metadata, origin notes, duplicates and judgement text. No numerical result needs a superseding record.

## lit-otheromics-20261011-msgwild: approved with corrections

M1. Remove 20 results that duplicate the store. In Table 3's top section ("Reported Performance in Retrieval Task w/ Bonus"), five rows repeat the MassSpecGym paper's Table 3 bonus formula challenge. That table is already in the store from source `part2-massspecgym-arxiv-v1`, with identical values and CIs (configurations `paper-model-789f6bd16613fb33ad`, `-6aa2fbcc807dd6adec`, `-41673c8f70a104f690`, `-1141e4258c691bbc3a`, `-443f59c5d84e63e793`). The rows are Random, DeepSets, Fingerprint FFN, DeepSets + Fourier and MIST vMassSpecGym. Apply it like this:
- Delete every result whose `source_locator` starts with `Table 3, section 'Reported Performance in Retrieval Task w/ Bonus (i.e., Formula Known)', row '` followed by `Random'`, `DeepSets'`, `Fingerprint FFN'`, `DeepSets + Fourier'` or `MIST vMassSpecGym'`. That is 20 results, 4 per row. Also delete each one's evaluation (20 evaluations) and its claims.csv row.
- Delete configurations `lit-otheromics-20261011-msgwild-config-deepsets-fingerprint-retrieval-massspecgym-baseline`, `...-config-fingerprint-ffn-retrieval-massspecgym-baseline`, `...-config-deepsets-plus-fourier-features-retrieval-massspecgym-baseline` and `...-config-mist-massspecgym-checkpoint-vmassspecgym`. Also delete methods `lit-otheromics-20261011-msgwild-method-deepsets-plus-fourier` and `...-method-fingerprint-ffn`. Nothing else links to them.
- Keep `...-config-random-ranking`: the Table 2 Random rows use it.
- Add one line to research.md: "Table 3 rows Random, DeepSets, Fingerprint FFN, DeepSets + Fourier and MIST vMassSpecGym repeat MassSpecGym (arXiv:2410.23326v1) Table 3, already in the store under part2-massspecgym-arxiv-v1; not re-added."
- Batch counts after M1: result 156, evaluation 156, configuration 34, method 4.

M2. Table 3 uncertainty level. The 48 Table 3 results (28 after M1) with `uncertainty.level` null carry the note "its interval settings are not restated in this table". That note is wrong. The Table 3 caption says: "The values in brackets indicate 99.9% BCa confidence intervals upon bootstrapping (20,000 resamples)". It applies to every bracketed value. For every result whose locator starts with `Table 3` and whose `uncertainty.level` is null:
- set `uncertainty.level` to `0.999`
- set `uncertainty.resamples` to `20000`
- replace `uncertainty.note` with: "Range printed in parentheses after the mean. Table 3 caption: 99.9% BCa bootstrap intervals over 20,000 resamples, stated for all bracketed values. Value repeated from the cited work; that work's own interval settings were not checked."

This also answers report question 4: the 99.9% level is not limited to the authors' own runs.

M3. Inferred `comparison.dataset_version`. The extractor hard-codes "Original MassSpecGym candidates" for Table 2 and for any label containing "inflated". It also gives the Table 9 MolForge "corrected" rows "Corrected candidate canonicalization (MassSpecGym v1.5)". Table 2 does not state a candidate version. The Table 9 "inflated" and "corrected" labels refer to the batched-inference bug, not to candidate canonicalization, and de novo generation has no candidate set. For the 24 Table 2 evaluations (`...-eval-*-mass-retrieval-*`) and the 12 Table 9 MolForge evaluations (`...-eval-mist-plus-molforge-reimplemented-by-the-authors-batched-inference-bug-batch-size-24-denovo-bonus-*` and `...-eval-mist-plus-molforge-reimplemented-by-the-authors-corrected-denovo-bonus-*`):
- set `comparison.dataset_version` to null
- add `missing_metadata["comparison.dataset_version"] = {"reason": "unreported", "note": "The table does not state the MassSpecGym candidate or canonicalization version"}`

Keep the Table 3 values: "inflated" and "corrected" there are about candidate canonicalization, which Section 5.1 states.

M4. Inferred `comparison.metric_implementation`. The 80 evaluations with "MassSpecGym v1.5 standardized metric implementation" (all non-compilation rows) rely on Section 6.2. That section recommends the v1.5 reference metrics but does not say the tables were computed with them. For each:
- set the field to null
- add `missing_metadata["comparison.metric_implementation"] = {"reason": "unreported", "note": "Section 6.2 recommends the MassSpecGym v1.5 reference metrics; the tables do not state which implementation produced these values"}`

M5. Inputs on leaking Table 2 rows. The 16 grey Table 2 evaluations have `comparison.inputs` "MS/MS spectrum and precursor mass". Those are the track's allowed inputs, not what these runs used. Set it as follows:
- 8 evaluations `...-eval-random-ranking-among-candidates-filtered-by-the-ground-truth-formula-mass-retrieval-*` and `...-eval-mist-retrieval-with-the-ground-truth-formula-mass-retrieval-*`: "MS/MS spectrum, precursor mass and ground-truth formula (leaks into the mass-based track)"
- 8 evaluations `...-eval-mist-retrieval-with-top-1-formula-from-mist-cf-trained-on-test-data-only-mass-retrieval-*` and `...-eval-mist-retrieval-with-top-1-formula-from-mist-cf-trained-on-train-and-test-data-mass-retrieval-*`: "MS/MS spectrum and precursor mass; formula from a MIST-CF annotator trained on test spectra"

M6. Author overlap on the source record. In `lit-otheromics-20261011-msgwild-source-liu2026`, replace `attributes.limitations[3]` with: "Authors include developers of MassSpecGym, DreaMS, MIST, MIST-CF, ICEBERG, DiffMS and FRIGID (Pluskal and Coley groups) and of JESTR, MVP and FLARE (Hassoun group); compiled rows for those methods repeat their developers' own results." Soha Hassoun and Yinkai Wang (Tufts) are co-authors, and [37] to [39] are Hassoun-group papers. Origin stays `paper_compilation` for those rows.

M7. MolForge origin note. `independent_paper` is right: MolForge [42] is by Neo et al., who are not authors, and the authors reimplemented it. But the pipeline's MIST encoder comes from the corresponding author's group. Append this limitation to the 16 MolForge evaluations listed under M3 and to `...-eval-mist-plus-molforge-generative-retrieval-reimplemented-by-the-authors-formula-retrieval-*` (4): "The MIST encoder in this pipeline was developed in the corresponding author's (Coley) group; the MolForge decoder was not."

M8. Judgement claims. Replace these fields in both `use-case-mapping-lit-otheromics-20261011-msgwild-mass-retrieval-hit-rate-1` and `use-case-mapping-lit-otheromics-20261011-msgwild-mass-retrieval-hit-rate-20`. Keep `relevance` as `proxy`. Keep endpoint, excluded_evaluations and the other fields as they are.

`rationale`:
"Proxy, not direct. The mass-based track withholds the formula, which matches the use case's formula-free input and shortlist endpoint. MIST here takes the top-1 formula predicted from the spectrum by a MIST-CF retrained on the MassSpecGym training split only, and that formula is not used to filter candidates (Section 4.3), so the pipeline needs only the spectrum and precursor mass. This differs from the formula-conditioned MIST the use case excludes, which receives the true formula. Only two valid configurations are measured (random ranking and this MIST pipeline), and the candidate pool and split differ from the MSAlign settings the use case was built on."

`constraints`:
1. "Use only the two non-grey evaluations; the grey rows leak ground-truth or test-trained formula information and are excluded."
2. "Treat MIST with the MIST-CF top-1 formula as a two-model pipeline (formula annotator plus formula-aware retriever). Do not transfer its score to MIST given a known formula, or to MIST-CF checkpoints trained on test spectra."
3. "Do not combine with the formula-known (bonus) retrieval results of Table 3 or with MSAlign's split-specific pools."
4. "Compare within this table only; corrected MassSpecGym v1.5 candidate canonicalization may change other published values."

`limitations`:
1. "Authors include the MIST, MIST-CF and MassSpecGym developers (author_reported)."
2. "Preprint (arXiv:2606.19624v1)."
3. "The true structure must be in the candidate set; not open-world identification."
4. "Retrieval inherits the errors of the formula annotator; its formula accuracy is in Table 7, not extracted."
5. "Table 8 reports a further non-grey variant (MIST-CF top-5 formulas, element-wise max), not extracted."
6. "Values are percentages printed without a percent sign in Table 2."

`reviewed_evaluations`, to set when repinning:
- hit-rate-1: `lit-otheromics-20261011-msgwild-eval-random-ranking-mass-retrieval-hit-rate-1`, `lit-otheromics-20261011-msgwild-eval-mist-retrieval-with-mist-cf-top-1-predicted-formula-mass-retrieval-hit-rate-1`
- hit-rate-20: the same two IDs with `hit-rate-20`.

Check these IDs exist after M1 to M5, then run `npm run use-cases:repin`.

Use-case fields: no change approved. Keep `use-case-mass-spectrum-molecule-shortlisting` as it is, exclusions and inputs included. The exclusion "Formula-conditioned retrieval, including MIST, FLARE and MSAlign+Filter" was written for MSAlign's formula-supplied rows. The judgement above keeps MIST with a predicted formula inside the use case's question without editing its scope. The proposed `assessed_by` links in use-case-links.json are approved as written.

Summary text: the batch proposes none, so there is nothing to approve.

Answer to report question 4:
- Per-row origins are correct: paper_compilation for values repeated from cited works, author_reported for the authors' own runs (MIST, MIST-CF, ICEBERG, DreaMS-based and spectrum-blind baselines), and independent_paper for the two dagger reimplementations. M6 and M7 add the missing overlap notes.
- The grey-row handling is correct: separate configurations, each with a limitation, all excluded from the judgements. I checked the grey state in my own HTML parse and on the rendered PDF.
- The 99.9% level applies to all of Table 3 (M2).
- MIST with a MIST-CF predicted formula is not caught by the exclusion as intended. It is accepted as proxy with the M8 text.

## Duplicates across branches and worktrees

- None of the four batches duplicates another batch in this worktree: rnalm-zeroshot, rna3d and rnagym are RNA sources with different DOIs. msgwild and khoo share no values.
- No record ID in the four batches exists in the store or in another batch.
- No other worktree (cells-networks, microbial-interactions, protein-structure, uc-ctdna, uc-execution, uc-splicing-cnv) or branch (cells-micro, protein) mentions the four arXiv IDs.
- Branch claude/lit-20261011-rna-other (ef64700) still carries liu2026 (MassSpecGym in the Wild), yang2026 and the original khoo2026 and zhong2026 batches. It must not be merged alongside this branch.
- Against the store, the only duplicates are the 20 values in M1. No model, method, benchmark or dataset name in the four batches matches an existing record. The new families (DiffMS, ICEBERG, FRIGID, Prosit, AlphaPeptDeep, MassFormer and others) are absent from the store. Existing MIST, JESTR, MVP, FLARE, DreaMS and MassSpecGym records are reused correctly.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store. The review fields were set by `finalise` in `extract/lib.py`.

1. M1: the 20 Table 3 results of the Random, DeepSets, Fingerprint FFN, DeepSets + Fourier and MIST vMassSpecGym rows, their 20 evaluations and claims.csv rows, 4 configurations and 2 methods are not extracted. The Random ranking configuration is kept for Table 2. The reviewer's line is added to research.md. Counts: result 156, evaluation 156, configuration 34, method 4.
2. M2: the 28 remaining Table 3 results with no interval level have level 0.999, 20000 resamples and the reviewer's note.
3. M3: `comparison.dataset_version` is null, with the reviewer's missing_metadata note, on the 24 Table 2 and 12 Table 9 MolForge evaluations; Table 3 values are kept.
4. M4: `comparison.metric_implementation` is null, with the reviewer's missing_metadata note, on the 80 non-compilation evaluations.
5. M5: the 16 grey Table 2 evaluations carry the reviewer's `comparison.inputs` text.
6. M6: the source's fourth limitation is the reviewer's text.
7. M7: the MIST encoder limitation is appended to every MolForge evaluation. M7 says "the 16 MolForge evaluations listed under M3" plus 4; M3 lists 12 Table 9 MolForge evaluations, so the limitation is on 12 + 4 = 16 evaluations, which are all the MolForge evaluations in the batch.
8. M8: both judgement claims carry the reviewer's rationale, constraints and limitations; relevance stays proxy and the other fields are unchanged. `reviewed_evaluations` is set in the extractor to the two evaluations per protocol the reviewer listed. The claims are not pinned (see 9).
9. Deferred: the approved `assessed_by` links in use-case-links.json are not yet applied to `use-case-mass-spectrum-molecule-shortlisting`, because the edit must be recorded with `records -- change`, which needs owner approval. The two judgement claims therefore stay `needs_review`, unpinned and without a review block, as unlinked drafts holding the reviewer's text. A follow-up adds the links, sets the claims to `source_checked` with the review block and pins them. No use-case field changed in this batch.
10. Review fields: every record except the two judgement claims is `source_checked`; each result carries a review block naming reviewer-ro-2, with the extraction description kept in `note`.

## Records after correction

- claim: 2
- configuration: 34
- dataset: 3
- evaluation: 156
- method: 4
- model: 12
- protocol: 14
- result: 156
- source: 1

Status: source_checked 380, needs_review 2 (the deferred judgement claims).
