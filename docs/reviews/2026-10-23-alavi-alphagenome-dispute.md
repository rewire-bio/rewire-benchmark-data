# Alavi 2026 AlphaGenome results disputed, 2026-10-23

Record changes for [#174](https://github.com/rewire-bio/rewire-benchmark-data/issues/174) after the author of Alavi 2026 (bioRxiv 10.64898/2026.10.02.756289) confirmed an off-by-one bug in the preprint's AlphaGenome scripts. Prepared by a Claude agent. No human review is claimed, and the extractor and reviewer were the same agent. No value was changed and nothing was reproduced.

The batch is `data/omics/alavi-alphagenome-dispute-20261023/`. `apply-changes.py` in that folder makes every edit to existing records listed below; the IDs were then recorded with `npm run records -- change` against this review, and the three use-case claims re-pinned with `npm run use-cases:repin`.

## Evidence

- Upstream issue [marcel-2c8/Probing-genomic-foundation-models-2026#2](https://github.com/marcel-2c8/Probing-genomic-foundation-models-2026/issues/2), opened 2026-10-19. Both AlphaGenome scripts (`2c8_alphagenome_splicescorer.py` lines 98 and 120, `2c8_alphagenome_junctionscorer.py` lines 89 and 110, commit `3c0c6cc`) convert the variant position to 0-based and pass it to `genome.Variant`, whose `position` is 1-based. Each variant was applied one base from its true position.
- The author's reply of 2026-10-20T16:11:48Z labels the issue a bug, says that running the splice scorer with the 1-based position "substantially improved accuracy", and promises updated scripts in calendar week 44 and a revised manuscript in early November.
- Both are archived as returned by the GitHub API in `data/omics/discrepancy-review-20261022-alavi-alphagenome/artifacts/` (`issue-2.json`, `issue-2-comments.json`) and recorded as source `discrepancy-review-20261022-source-alavi-issue-2`.
- The supplementary archive (Zenodo 10.5281/zenodo.23105803, `supplementary_materials_alavi_2026_v01.zip`, SHA-256 `1a064bbb2dc415cc9b7d1bfc42c9242ab4d9105220ef4d9e65792ef185d3cdb5`), added as source `rna-splicing-20261011-alavi2026-source-supplementary-tables`. Its licence (CC BY-NC-ND 4.0) does not allow redistribution, so only the hash and `classify-table-vi.py` are stored. Retrievals on 2026-10-19 and 2026-10-23 had the same hash.

## 1. AlphaGenome results disputed

All 42 results of the nine AlphaGenome evaluations (splice scorer, junction scorer and either module, on the multi-gene set, the OPA1 evaluation sets and the extended OPA1 positive calls) change from `source_checked` to `disputed`. Each gets a `source_warnings` entry saying why. The printed and numeric values are unchanged; corrected values do not exist yet. When the revised preprint is published, its AlphaGenome values are added as results that supersede these.

The thresholds for every protocol were tuned on OPA1 scores made with the same shifted positions, so the OPA1 rows are as affected as the multi-gene rows. The other models' scripts handle coordinates correctly (issue #2), and their results are unchanged.

## 2. Scoped evidence concern on the article

`rna-splicing-20261011-alavi2026-source-article` gets one `evidence_concerns` entry with `applies_to` naming the nine AlphaGenome evaluations (docs/collection.md, "Corrections and concerns"). It withholds those evaluations' results from comparisons, use-case judgements and discrepancy inference, and leaves the SpliceAI, Borzoi, NTv3, Evo2 and Genos results of the same article usable. A concern without `applies_to` would have withheld every use case citing the article.

The results are also `disputed`, and the release leaves out disputed records (`publicRecords` in `scripts/omics/schema.ts`), so they never reach the knowledge graph and neither `excluded.disputed` nor `excluded.concern` in `discrepancies.json` counts them. The concern still matters: it marks the source for readers and covers the evaluations, which stay in the release.

## 3. Multi-gene population corrected

The dataset `rna-splicing-20261011-alavi2026-data-multigene` and the twelve multi-gene evaluations repeated the preprint's text: "76 functionally validated, spliceogenic substitutions within the canonical splice sites of 65 genes". The author's own Supplemental Table VI lists every variant with its coding coordinate. `classify-table-vi.py` reads its 183 rows and classifies each by HGVS offset (`composition.tsv`):

| Group | Variants | Gene symbols | Position |
| --- | --- | --- | --- |
| Spliceogenic positives | 76 | 64 | 26 canonical ±1,2; 35 near-splice intronic (+3 to +7, -3 to -7, -13); 15 exonic |
| Benign controls | 107 | 46 | all intronic, ±3 to ±10 |

The population now says this. The dataset also gets `population_detail` with the counts, a `scope_note`, and the supplement as a source. Its name keeps the paper's "65 genes" label. The previous text is kept in `metadata-correction-alavi2026-20261023-dataset-population` and `metadata-correction-alavi2026-20261023-evaluation-population`.

The issue reports 75 unique positives after de-duplication against the table's 76. The population keeps the table's count.

## 4. Use-case claims

For "Select a patient-RNA splicing-variant validation workflow":

- `use-case-mapping-rna-splicing-20261011-alavi2026-multigene` and `use-case-mapping-rna-splicing-20261011-alavi2026-opa1-evaluation` move their three AlphaGenome evaluations from `reviewed_evaluations` to `excluded_evaluations` with the reason, drop AlphaGenome from `endpoint`, and add a limitation saying so. The multi-gene judgement's limitation on the positives is corrected as in section 3.
- `use-case-summary-patient-rna-splicing-validation` no longer quotes AlphaGenome's 56.6% sensitivity and 80.4% specificity. It describes the positives as in section 3, says the AlphaGenome rows are disputed and why, and cites the supplement and the issue.

Without these edits the judgements would list evaluations whose results are disputed and the build would hold them for re-review. The rest of the summary is unchanged; the SpliceAI, NTv3, Evo2 and Genos values in the Alavi sentence were checked against their results.

## 5. Discrepancy follow-up

`discrepancy-review-20261023-alavi-alphagenome-splicing-corrected` is revision 2 of the review of `discrepancy-52a714eb6bb63442` (previously `discrepancy-ead251c24ba272c1`): action `corrected-records`, state `confirmed-error`, dated 2026-10-23, with `resolved_by` naming the article and the 42 disputed results. Its subjects are the nine AlphaGenome evaluations and Alavi's six Borzoi evaluations, the other system compared: once the finding stops firing, the build keeps it as a resolved finding and takes its systems from the review claims' subjects.

Revision 1 (`discrepancy-review-20261022-alavi-alphagenome-splicing`, `awaiting-correction`) is kept as the earlier step. Its subjects were six of the results now disputed, and the release leaves out every record that links to a disputed one, so revision 1 would have dropped out and the follow-up history would have started at revision 2. Its links now name the three multi-gene AlphaGenome evaluations those six results belong to, and the two multi-gene Borzoi evaluations. The previous links are kept in `metadata-correction-alavi2026-20261023-discrepancy-review-links`.

With the results disputed they leave the release, so the rules no longer see them and the ordering reversal stops firing. `confirmed-error` settles it, so the build retires the review (`derived.retired_reviews` in the bundle manifest) instead of failing, and keeps the finding as resolved with its history. The counts from a local knowledge-graph build are in the pull request.

## Still open

- The revised preprint and scripts. When they are published, add the rerun AlphaGenome values as superseding results, and add revision 3 if the discrepancy changes.
- The preprint's other points raised in issue #2 (track labels, the unused gene-mask scorer, the raw junction delta) are the author's to address; nothing in the store depends on them beyond the disputed results.
