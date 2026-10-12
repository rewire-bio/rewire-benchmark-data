# Review: lit-cells-networks-20261011-sun2026de, 2026-10-12

Source: Sun et al. 2026, DE classification benchmark for perturbation models (bioRxiv v1).

Reviewer: Claude review agent `reviewer-cn-1`, independent of the extractor `lit-cells-networks`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

The reviewer reported on this batch together with `lit-cells-networks-20261011-ye2026grn`. The common sections and this batch's corrections and answers follow, unchanged.

# Reviewer cn-1 verdict: Ye 2026 GRN and Sun 2026 DE batches

Reviewer: Claude (Opus 5.5) review agent cn-1, independent of the lit-cells-networks collector; no human review claimed. Date 2026-10-12. Worktree `rewire-benchmark-data-lit-cells-networks`, batch folders as found (uncommitted). Nothing was edited, committed or added to the store.

## Verdicts

| Batch | Verdict |
| --- | --- |
| `lit-cells-networks-20261011-ye2026grn` | Approved with corrections (Y1 to Y6) |
| `lit-cells-networks-20261011-sun2026de` | Approved with corrections (S1 to S5) |

Every printed value in both batches matches the source. The corrections are a missed source error (Ye Table 7 GENIE3), one wrong origin (Sun Scouter and TranScouter: a co-author developed both), and descriptive and comparison-field fixes. No result value needs superseding.

## Sun 2026 corrections

**S1. Origin of Scouter and TranScouter (required).** Co-author Ouyang Zhu (University of Notre Dame, ozhu@nd.edu on the title page) is first author of both cited method papers: reference 14 "Zhu, O., Li, J.: Scouter predicts transcriptional responses to genetic perturbations" and reference 31 "Zhu, O., Li, J.: Investigating cross-condition prediction of transcriptional response". Set `attributes.origin` from `independent_paper` to `author_reported` on these 10 evaluations:
- `lit-cells-networks-20261011-sun2026de-eval-within-{k562,rpe1,hepg2,jurkat,average}-scouter`
- `lit-cells-networks-20261011-sun2026de-eval-cross-{k562,rpe1,hepg2,jurkat,average}-transcouter`
The extractor's `SYS` table should set the independence flag to False for both. scVI and STATE remain `independent_paper` (no overlap with Lopez et al. or Adduri et al.). The KNN and logistic-regression baselines use GenePT and GenePert, both by co-author Yiqun T. Chen; they are already `author_reported`.

**S2. Source limitation (required).** In `lit-cells-networks-20261011-sun2026de-source-sun2026`, replace the third `limitations` entry with: "The authors did not develop scVI, scGen or STATE. Co-author Ouyang Zhu developed Scouter and TranScouter (references 14 and 31), and co-author Yiqun T. Chen developed the GenePT embeddings used by the KNN, logistic-regression, VAE and scVI configurations (reference 30). The majority vote, KNN and logistic regression baselines and the scGen-based VAE adaptation are the authors' own."

**S3. STATE configuration (required).** Section 3.3.7 says STATE was used "in the gene expression mode (without the pretrained State Embedding component)" and trained on the benchmark splits, so it is not a pretrained foundation model here. On `lit-cells-networks-20261011-sun2026de-config-state`: `facets.method_types` = ["supervised_machine_learning"], `foundation_model_eligible` = false, and `description` = "Arc Institute STATE transition model in gene-expression mode, without the pretrained State Embedding, trained on the benchmark splits following the official codebase, including the 60% training split of the held-out cell line (few-shot)."

**S4. Comparison inputs (minor).** STATE uses a learned perturbation embedding and the majority vote uses no embedding, so "Control expression and GenePT or LLM perturbation embeddings" is not right for every row. On all 85 evaluations set `comparison.inputs` to "Training perturbations with observed expression or DE labels, control-cell expression, and a perturbation representation (GenePT, LLM-derived or learned embedding) where the method uses one".

**S5. Relevance judgements (required; final text below).** Both `proxy` judgements hold. The within-cell-line endpoint matches the use case's inputs (perturbed and control single-cell expression with perturbation labels) and output (predicted expression changes assessed against measured responses), scored through DE calls. The cross-cell-line judgement is a proxy for the use case's evidence gap on a new cell system; the use-case exclusion on cross-cell-type transfer is about GEARS usage scope, and GEARS is not evaluated here, so no use-case field change is needed. Both judgements need the author overlap and the ground-truth caveat in their limitations, and the cross-cell-line rationale overstated the link to the use case's pilot advice. Apply verbatim:

`use-case-mapping-lit-cells-networks-20261011-sun2026de-within-cell-line`: keep `relevance`, `endpoint`, `rationale`, `description` and `constraints`. Set `limitations` to:

```json
["Preprint; one 60/40 perturbation split per cell line; no spread printed.",
 "The printed tables are DE-call proportions and accuracy by effect-size quantile; the macro-F1 and balanced accuracy comparisons are in figures only.",
 "Majority-vote accuracy is near 100% in low-effect quantiles because almost all pairs are non-DE; read the Q5 column and the DE proportions together.",
 "Which data setting (full or PerturbQA-downsampled) the tables report is not printed (source evidence concern).",
 "The authors built the majority-vote, KNN, logistic-regression and scGen-based VAE comparators, and co-author Ouyang Zhu developed Scouter (reference 14); those rows are author-reported. scVI is run through STATE's benchmarking implementation with GenePT perturbation embeddings.",
 "Ground-truth DE labels are Wilcoxon calls (BH-adjusted p < 0.01) on observed expression in four essential-gene Perturb-seq screens, not orthogonally validated effects."]
```

`use-case-mapping-lit-cells-networks-20261011-sun2026de-cross-cell-line`: keep `relevance`, `endpoint` and `constraints`. Set both `rationale` and `description` to: "Scores DE calls for perturbations in a cell line held out from training, which bears on the use case's gap on performance in a new cell system. Proxy: retrospective DE classification of predicted expression on four essential-gene screens, not a prospective pilot or experimental hit rates." Set `limitations` to:

```json
["Preprint; one 60/40 perturbation split per cell line; no spread printed.",
 "The printed tables are DE-call proportions and accuracy by effect-size quantile; the macro-F1 and balanced accuracy comparisons are in figures only.",
 "Majority-vote accuracy is near 100% in low-effect quantiles because almost all pairs are non-DE; read the Q5 column and the DE proportions together.",
 "Which data setting (full or PerturbQA-downsampled) the tables report is not printed (source evidence concern).",
 "The authors built the majority-vote, KNN, logistic-regression and scGen-based VAE comparators, and co-author Ouyang Zhu developed TranScouter (reference 31); those rows are author-reported.",
 "Models are trained on the 6,641 genes shared by the four cell lines; STATE runs in gene-expression mode without the pretrained State Embedding.",
 "Ground-truth DE labels are Wilcoxon calls (BH-adjusted p < 0.01) on observed expression in four essential-gene Perturb-seq screens, not orthogonally validated effects."]
```

The `reviewed_evaluations` lists (40 within, 45 cross) are complete and correct; I checked every evaluation in them. After the corrections, set both claims to `source_checked`, fill `review`, and run `npm run use-cases:repin`.

**Summary text and use-case fields.** The collector proposed no summary text and no use-case field change. I approve none. If a summary is drafted later, it must state that the KNN, logistic-regression and VAE comparators, Scouter and TranScouter are the authors' own, and that DE truth is Wilcoxon calls on essential-gene screens. The `phenotype-perturbation-selection` use case was considered and not linked; its exclusions rule out transcriptome-derived scores alone.

## Answers to the collector's questions

Sun 2026:
- Full versus downsampled data: the evidence concern is justified and correctly worded as an inference. Section 2.4 says the full versus curated comparison is in Figure 5. Section 2.1 cites the 2.9% true prevalence from Table 1, which fits the full data (Table 5: 95 to 98% non-DE), not a set downsampled for non-DE pairs. Keep the concern; it should not block the batch.
- Proportion of pairs predicted DE with direction `unknown`: agreed. The paper reads these rows against the true prevalence, so neither higher nor lower is better. The `metric_qualifier` says so, and the judgement's constraint tells readers to compare with the true DE prevalence claims.
- Archived copy as hash reference: accepted on the same basis (gunzipped bytes match fa1c6a63...; re-download rate-limited).

## Checks run

1. **Source hashes.** Both `.gz` archives match their recorded hashes (Ye 661fed5a..., Sun 939e0a8d...). Both unpack to PDFs whose SHA-256 equals `artifact_sha256` in the source records. A fresh download from bioRxiv returned HTTP 429 (17-byte body), so all value checks used the archived bytes.
2. **Automated full comparison, own parser.** I wrote my own scripts, independent of `extract/`, which ran on `pdftotext -layout` output of the unpacked PDFs.
   - Ye: within each Table 4 to 7 region, lines with 21 decimal tokens. Asserted 32 rows per table (4 reference blocks x 6 datasets plus mean and std) and 2,688 cells. Results: 2,352 of 2,352 printed and numeric values match, none missing, none extra. All 336 mean rows carry the matching std as `uncertainty.value`, and no dataset row carries uncertainty. Every result's evaluation links to the configuration, protocol (gene set and reference) and dataset subset its locator implies. Each of the 1,176 evaluations has exactly two results, one EPR and one AUPRC. Table 4 and 5 results are `early-precision-ratio`, Table 6 and 7 `auprc-ratio`; all are `higher` and `unitless`.
   - Sun: rows with five percentages under each Table 1 to 4 caption. 180 cells: 170 of 170 results and the 10 true-DE-prevalence claims match, none missing, none extra. Every result links to the evaluation implied by its locator (configuration, cell line or four-line average, protocol). Tables 1 and 3 are `proportion`/`unknown`/`percent`, Tables 2 and 4 `accuracy`/`higher`/`percent`.
   - `claims.csv` agrees with `batch.jsonl` for every result row in both batches.
3. **Hand check against the rendered tables.** I rendered the PDF pages to images (Ye pages 21 to 24, rotated; Sun pages 6 to 8) and read the cells by eye.
   - Ye: 48 values, 12 per table, 3 per reference block per table. They cover all six foundation models, all three extraction strategies, all three baselines, all six datasets and mean rows with their std. All 48 match.
   - Sun: 48 values, 12 per table, covering every method and every column type. All 48 match.
   - The rendered pages also confirm the row and column order my parser assumed, and the Table 7 GENIE3 duplication.
4. **Completeness.** No cell of Ye Tables 4 to 7 or Sun Tables 1 to 4 is missing. Ye std rows are stored as uncertainty, not as results. Not extracted, as stated in `research.md`: Ye Table 1 (duplicate means), Table 8 (topology) and the figures; Sun Table 5 (dataset statistics) and the figures.
5. **Metric, qualifier, direction, unit, uncertainty, denominator, dataset, split.** Correct, apart from the comparison-field issues in Y2 and S4. Ye qualifiers carry gene set, reference and mean scope. Sun qualifiers carry the quantile and its printed range.
6. **Origin and author overlap.** Ye: authors Ye, Yang, Yang, Mao, Tang. None appear on the cited papers for GENIE3 [11], GRNBoost2 [12], DeepSEM [13], Geneformer [15], scGPT [16], scFoundation [23], LangCell [24], scCello [25] or scPRINT [26] ("Tang" on scCello is Jian Tang, not Chao Tang). `independent_paper` is correct for all 1,176 evaluations. Sun: overlap found (S1).
7. **Locators.** Every result locator names table, block or row, and column, and resolves to the cell it holds.
8. **Duplicates.** I searched the store on origin/main (bba147c, fetched 2026-10-12), every `claude/lit-20261011-*` branch (local and remote) and the uncommitted files in all `../rewire-benchmark-data-lit-*` worktrees. Search terms: both DOIs, both titles, scPRINT and DeepSEM. No duplicate source, model or method was found. The only "Sun et al. 2026" hit is a different paper (ancestry-stratified Borzoi, scope-audit). None of the new IDs collide with the store, and all reused IDs exist (scGPT, scFoundation, Geneformer, LangCell, scCello, GENIE3, GRNBoost, scVI, STATE, the use case).
9. **Scope.** Ye fits `networks-mechanistic` and `cells-spatial`, and no use case covers GRN inference (all 26 use cases checked), so no judgement is right. Sun fits `cells-spatial`. Judgements: see S5.
10. **Not run.** `npm test`, `npm run typecheck` and `npm run build` were not run in this review, because the instructions were not to edit records. They must run after the corrections, with `records -- add`. Receipts (`review.json`) and dated reviews were not written; they belong to whoever applies the corrections.

Notes, no change needed: in Ye Table 6, scFoundation coshid prints exactly 1.0000 (random level) for four of six datasets in each of the STRING and both ChIP-seq blocks, which may mean a degenerate edge ranking. It is a printed value and the protocol limitations already warn against reading ratios across references. Geneformer and LangCell costok values are identical in 7 of 24 Table 4 cells and 9 of 24 Table 5 cells. LangCell's cell encoder is initialised from Geneformer, so this is plausible and not flagged.

## Corrections applied

Applied by the extractor in the `extract/` scripts, as the reviewer specified, before the batch was added to the store.

1. S1: the ten Scouter and TranScouter evaluations are `author_reported`, set in the extractor's `SYS` table.
2. S2: the source's third limitation is the reviewer's text.
3. S3: the STATE configuration is `supervised_machine_learning`, not foundation-model eligible, with the reviewer's description.
4. S4: all 85 evaluations carry the reviewer's `comparison.inputs`.
5. S5: both judgements carry the reviewer's limitations, and the cross-cell-line rationale and description are the reviewer's text. Both are `source_checked`, linked from `use-case-genetic-perturbation-response` and pinned with `npm run use-cases:repin`.
6. No summary text or use-case field change was approved, and none was applied.
7. Every record is `source_checked`; each result's and claim's `review` block names the reviewer and keeps the extraction note.

## Records after correction

- benchmark: 1
- claim: 12
- configuration: 10
- dataset_subset: 5
- evaluation: 85
- protocol: 2
- result: 170
- source: 1
