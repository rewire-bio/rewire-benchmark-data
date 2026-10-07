# Use-case coverage research: issue #349, additive intake

Additive reviewed intake for `use-case-cell-type-annotation-transfer` (issue #349), 2026-10-06.
Baseline: release `2026-10-06-fea06f63ac0e` (the latest immutable release at the time of this pass,
already including the 2026-09-30 and 2026-10-05 additive intakes). Only two independently checkable
facts are ingested in this pass; everything else identified in the bounded research dossier stays
unresolved pending further verification. No existing record, mapping, or release is changed. No release
is built or frozen by this pass.

## What is added

Both facts come from the same already-catalogued source (`ucc-research-source-sctab-paper`, scTab,
Nature Communications 2024), Methods subsection "Uncertainty quantification for scTab model", within
the same donor-held-out split of the same pooled 249-dataset CELLxGENE corpus already used for the
existing Table 1a mapping. They are **two distinct comparisons using the same deep-ensemble
uncertainty-score mechanism** and must not be conflated:

1. **`ucc-research-protocol-sctab-uncertainty-absent`** (unknown/absent-type detection): ROC-AUC
   **0.782**, correct known-type (Group 1) vs. absent-type (Group 3 -- cell types excluded entirely from
   training for being too rare). This is the endpoint the use case's own `evidence_gaps` already
   flagged as under-extracted ("Unknown-type rejection ROC appears in Supplementary Figure 4 but
   numerical curve labels are not extracted here"). The correction established in the 2026-10-06
   research dossier: the number is not confined to the supplementary figure -- it is stated in running
   Methods text in the main article.
2. **`ucc-research-protocol-sctab-uncertainty-error`** (known-type error/confidence detection): ROC-AUC
   **0.891**, correct known-type (Group 1) vs. incorrect known-type (Group 2). This is a different
   endpoint from (1): it measures whether the model's own mistakes among types it was trained on can be
   flagged, not whether types absent from training can be detected. It is ingested as its own separate
   protocol/evaluation/result/mapping so that it can never be merged with, averaged with, or mistaken
   for the absent-type figure.

Neither protocol establishes cross-study or cross-platform transfer of either capability: both are
measured within one donor-level holdout of one pooled corpus. Whether individual datasets/studies
contribute donors to more than one split is not directly confirmed in the retrieved text (see
limitations on each protocol record). Exact denominators for Group 2 and Group 3 (how many cell types
and cells each contains) are not stated in the retrieved main text and are recorded as explicit missing
denominators, not invented.

## What is explicitly not added in this pass (as of the first 2026-10-06 intake)

Per `workbench/cell-type-ingestion-plan.md` (gitignored, not part of this release), the following
candidate facts from the same research dossier were held, not ingested, because they were not yet
independently checkable to the same standard:

- Hao et al. 2021's internally conflicting 73.8%/79.4% "stronger Seurat support" figure (unresolved
  source conflict).
- Abdelaal et al. 2019's genuine inter-dataset/cross-platform results (Fig. 4, Fig. 5): real but
  graphical heatmap values, not machine-extractable as text in the bounded search. Its **intra-dataset**
  Baron Human numbers were a different (non-cross-platform) result not pursued at the time; **these are
  ingested in the same-day continuation below.**
- scArches's and scParadise's figures (approximate/aggregated, or dependent on an unretrieved
  supplementary table).
- CellTypist's ~0.9 figure (split/holdout methodology inaccessible, Supplementary Text).

This use case (`use-case-cell-type-annotation-transfer`) remains incomplete: `collection_plan.status`
in `data/omics/use-cases/inputs.json` is untouched (`"collecting"`), and its `evidence_gaps` are
untouched -- this pass corrects the "numerical curve labels are not extracted" gap's scope (the number
*is* now extracted and catalogued for one of the two distinct comparisons) without claiming the
broader compound cross-study/matched-coverage endpoint is resolved.

## Correction, same day (2026-10-06)

An independent review of the six records above found three mechanism/terminology errors, all now
corrected in `records.jsonl` before any release:

1. **Averaging order.** The source states: *"one just averages the predicted probabilities across
   several networks that were independently trained... In our case, we averaged the predictions across
   5 models."* Predicted probabilities are averaged across the 5 ensemble members **first**, and the
   uncertainty score is then 1 minus the maximum of that averaged probability vector. An earlier version
   of `uncertainty_mechanism`/`comparison.adaptation` said the **uncertainty scores** (not the
   probabilities) were averaged across the ensemble -- a different computation. Corrected throughout.
2. **"Temperature-scaled."** An earlier version described the predicted probability as
   "temperature-scaled." That phrase is not in this Methods subsection (it was carried over in error from
   a different source, scParadise, elsewhere in the same research dossier) and has been removed.
3. **Ensemble size vs. run count.** `n_runs: 5` (an evaluation-attribute convention this catalogue
   otherwise uses for repeated/seeded training runs feeding a mean-plus-SD result, as in the existing
   Table 1a mapping) has been replaced with `ensemble_size: 5`, since this single ROC-AUC is computed
   once from a 5-member ensemble's averaged probability, not from 5 separately reported runs.
4. **Training-setting link.** `comparison.inputs` previously asserted "Data augmentation enabled" for
   the uncertainty-quantification ensemble. This subsection does not independently restate that training
   setting; it is now described as unconfirmed for this specific analysis, with a parallel limitation
   added to both protocol records.

All six records' SHA-256 bytes changed as a result; `review.json` (this folder) and both mappings'
`evidence_sha256` in `data/omics/use-cases/inputs.json` were refreshed to match. No ROC-AUC value, group
definition, or endpoint scoping changed.

## Same-day continuation (2026-10-06): Abdelaal et al. 2019 Baron Human intra-dataset, ingested; scArches re-checked, held

Added, same dated lane, same baseline, no release built: a new source record
(`ucc-research-source-abdelaal-2019-paper`), a new dataset record for the Baron Human pancreatic
dataset, one new intra-dataset protocol, 3 methods, 4 configurations, 4 evaluations, and 7 results (4
median F1-score values, 3 cells-left-unlabeled percentages) -- 21 new records, all `source_checked`,
all `author_reported` (no new execution).

**Scope, explicitly bounded to intra-dataset.** Methods, quoted verbatim: *"We evaluated the
classification performance through two experimental setups: (1) intra-dataset in which we applied
5-fold cross-validation within each dataset and (2) inter-dataset involving across datasets
comparisons."* Everything ingested here is from setup (1) only, for one dataset (Baron Human, Table 2:
8,569 cells, 17,499 genes, 14/13 cell populations, inDrop protocol). Results, quoted verbatim, "All
classifiers perform well in intra-dataset experiments": *"for the Baron Human dataset, the median
F1-score for SVM rejection, scmapcell, scPred, and SVM is 0.991, 0.984, 0.981, and 0.980, respectively
(Fig. 1a). However, SVM rejection, scmapcell, and scPred assigned 1.5%, 4.2%, and 10.8% of the cells,
respectively, as unlabeled while SVM (without rejection) classified 100% of the cells with a median
F1-score of 0.98 (Fig. 1b)."* Four median F1 values and three unlabeled-percentage values (SVM's
"classified 100% of the cells" is the complement of 0% unlabeled but is not given its own
rejection-percentage result record, matching the scope requested). Method identities (version, language,
underlying classifier) are transcribed from Table 1, not assumed: SVM and SVMrejection share the same
underlying classifier (scikit-learn 0.19.2, SVM linear kernel) and differ only in the Table 1 "Rejection
option" column (No vs. Yes); scmapcell is R package scmap 1.5.1 (kNN); scPred is R package scPred
0.0.0.9000 (SVM, radial kernel).

This protocol does **not** establish cross-study or cross-platform transfer. The source's own genuine
inter-dataset (cross-platform/cross-study) experiments -- Fig. 4 (brain datasets) and Fig. 5 (pancreatic
datasets, training on three of Baron Human/Muraro/Segerstolpe/Xin and testing on the fourth) -- remain
unretrieved as precise numeric values (confirmed via Supplementary Figs. S9/S10: real per-classifier
heatmap data exists for these, but is graphical, not machine-extractable text) and are **not** ingested
in this pass.

### Unresolved: scArches ~84% accuracy (re-checked, not ingested)

Re-read directly, this pass, both the scArches main text and its supplement
(`workbench/source-review-20261006/PMC8763644.xml` and `..._supp1.txt`). Main text, quoted verbatim,
Results: *"scArches achieved ~84% accuracy across all tissues (Fig. 4c)."* This is explicitly
approximate (`~`) and aggregated ("across all tissues"); no exact fraction or per-tissue breakdown is
stated in running text, and Fig. 4c/4e are figures, not extracted as numbers in this pass.

The decisive, disqualifying gap: **the accuracy formula's denominator is not stated for this figure.**
The classification pipeline labels each cell correct, incorrect, or "unknown" (>50% uncertainty,
Methods). Whether "~84% accuracy across all tissues" is computed as correct/(correct+incorrect+unknown)
("all-cell" denominator, unknowns count against accuracy) or correct/(correct+incorrect) ("accepted-only"
denominator, unknowns excluded) is not stated next to Fig. 4c. The *only* place in the accessible text
(main or supplement) that explicitly defines an accuracy formula is a *different* figure's caption,
Supplementary Fig. 17: *"The Y axis denotes the accuracy (#correct/#all_cells) of classification for the
query Tabula Muris data calculated for all cells excluding trachea."* That formula is explicitly scoped
to a population **excluding** the unseen/trachea tissue -- the opposite of what would be needed to
resolve Fig. 4c's "across all tissues" (which, per Fig. 4's own legend, includes the trachea cells, since
panel (c) is described as showing "misclassified and unknown cells" including "the highlighted tissue
[that] represents tracheal cells"). Applying Supplementary Fig. 17's formula to Fig. 4c by analogy would
require assuming the same convention *and* the same inclusion/exclusion choice across two different
figures with two different stated populations -- an inference, not a transcription. Per instruction, this
value is **not promoted**; it is recorded here as source-backed but unresolved. No source, dataset,
protocol, evaluation, or result record for scArches is added in this pass.

## Correction, independent review (2026-10-06/07)

Four provenance/schema issues in the Abdelaal ingestion above were found and corrected directly in
`records.jsonl` (the six scTab lines are preserved byte-identical; only the 21 Abdelaal records were
rewritten). Full detail in `retrieval-log.md`; summary:

1. **`retrieved_at` was invented.** The research dossier logged only a bounded five-source batch
   window (12:16:47Z-12:18:28Z UTC), not a per-file timestamp; using the window's end as Abdelaal's own
   exact fetch time was unsupported precision. The source was **re-fetched directly** this pass at the
   real, logged timestamp `2026-10-06T23:28:54Z` UTC -- confirmed byte-identical (SHA-256 unchanged).
2. **Cache path was workbench-only (gitignored).** The re-fetched bytes are now archived as a
   **committed** gzip artifact, `artifacts/abdelaal-2019-pmc6734286-fulltext.xml.gz`, round-trip
   SHA-256-verified, referenced via a new `review_artifact` attribute (matching this repository's
   existing `review_artifact` convention).
3. **`metric_direction: "lower"` on the three unlabeled-percentage results was an unsupported universal
   claim.** Percentage unlabeled is a coverage/rejection-rate choice, not a performance metric with one
   direction: lowering it can raise or lower the same classifier's own F1 depending on which cells get
   accepted. Changed to `metric_direction: "unknown"` -- the schema's existing third value
   (`services/omics/src/validation.ts`: `["higher", "lower", "unknown"]`; no new value invented) -- with
   an explicit F1/rejection-tradeoff note added to each result's `scope_note` and to the protocol's
   `limitations`.
4. **8,569 cells (Table 2) was not distinguished from a confirmed per-classifier scored denominator.**
   The dataset, protocol and evaluation records now state explicitly that 8,569 is the Table 2
   dataset-size figure, not independently confirmed as the exact number of cells scored for any one
   classifier's median F1 or unlabeled-percentage result.

No printed value changed (0.991/0.984/0.981/0.980 median F1; 1.5%/4.2%/10.8% unlabeled). All prior
mappings and all six scTab records remain byte-identical. `review.json` (this folder) and the Abdelaal
mapping's `evidence_sha256` in `data/omics/use-cases/inputs.json` were refreshed to match the corrected
record bytes.

## Extraction scope

Two scTab ROC-AUC values and nine Abdelaal et al. 2019 Baron Human intra-dataset values (4 median F1, 3
unlabeled percentages, plus their dataset/method identities from Table 1/Table 2), all quoted verbatim
from running text or table cells, all byte-verified against independently re-fetched source bytes (see
`sources.md`). No supplementary-figure heatmap cell, no scArches value, and no per-group (scTab Group
2/3) cell count was extracted in this pass beyond what is stated above.

Final research intake, this pass: 27 new records (1 source, 1 dataset, 3 protocol, 3 method, 4
configuration, 6 evaluation, 9 result); 9 new results.
