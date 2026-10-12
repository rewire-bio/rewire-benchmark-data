# Review: lit-cells-networks-20261011-ye2026grn, 2026-10-12

Source: Ye et al. 2026, static GRN reconstruction from single-cell foundation models (bioRxiv v1).

Reviewer: Claude review agent `reviewer-cn-1`, independent of the extractor `lit-cells-networks`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

The reviewer reported on this batch together with `lit-cells-networks-20261011-sun2026de`. The common sections and this batch's corrections and answers follow, unchanged.

# Reviewer cn-1 verdict: Ye 2026 GRN and Sun 2026 DE batches

Reviewer: Claude (Opus 5.5) review agent cn-1, independent of the lit-cells-networks collector; no human review claimed. Date 2026-10-12. Worktree `rewire-benchmark-data-lit-cells-networks`, batch folders as found (uncommitted). Nothing was edited, committed or added to the store.

## Verdicts

| Batch | Verdict |
| --- | --- |
| `lit-cells-networks-20261011-ye2026grn` | Approved with corrections (Y1 to Y6) |
| `lit-cells-networks-20261011-sun2026de` | Approved with corrections (S1 to S5) |

Every printed value in both batches matches the source. The corrections are a missed source error (Ye Table 7 GENIE3), one wrong origin (Sun Scouter and TranScouter: a co-author developed both), and descriptive and comparison-field fixes. No result value needs superseding.

## Ye 2026 corrections

**Y1. New evidence concern (required).** Append to `attributes.evidence_concerns` of `lit-cells-networks-20261011-ye2026grn-source-ye2026`:

```json
{"source_id": "lit-cells-networks-20261011-ye2026grn-source-ye2026", "message": "Table 7 (TFs+1000 AUPRC) repeats Table 6 (TFs+500 AUPR) exactly in the GENIE3 column of the STRING, Cell-type-specific ChIP-seq and Nonspecific ChIP-seq blocks: all 18 dataset values and the three mean and std rows are identical (for example STRING hESC 1.6241, mean 3.301, std 2.244). Only the OmniPath block differs. Every other column, and GENIE3 in the EPR Tables 4 and 5, differs between the two gene sets, and the Table 6 values match Table 1. These 21 Table 7 GENIE3 values are likely a copy of the TFs+500 values and should not be compared.", "source_locator": "Table 7, column group 'ML', column 'GENIE3', blocks 'STRING', 'Cell-type-specific' and 'Nonspecific'; Table 6, same cells; Table 1, GENIE3 AUPRC ratio", "artifact_sha256": "a6c3aae569b1f1614c71569efb0692f15700aea473c64c7bc0bc660e81330dc7", "review_date": "2026-10-12"}
```

In the `review.note` of each of these 21 results, add "Subject to the source evidence concern on Table 7 GENIE3 (duplicates Table 6).":
`lit-cells-networks-20261011-ye2026grn-result-tf-plus-1000-{string,cell-type-specific-chip-seq,non-specific-chip-seq}-{hesc,hhep,mdc,mhsc-e,mhsc-gm,mhsc-l,six-datasets}-genie3-auprc-ratio` (3 x 7 = 21 IDs).

**Y2. Uniform comparison fields (required).** The evaluations currently use two `adaptation` values ("Zero-shot (pretrained weights)" for the 18 foundation-model configurations, "Fitted to the expression matrix" for GENIE3, DeepSEM and GRNBoost). `catalogue-query.ts` treats any difference in a comparison field as incompatible, so the store cannot compare the foundation models with the baselines, which is the paper's main comparison. The split text also says "zero-shot" for the fitted baselines. Following the Csendes 2025 precedent (one text per protocol, detail on the configuration), set on all 1,176 evaluations:
- `comparison.adaptation`: "Foundation models zero-shot from pretrained weights; GENIE3, DeepSEM and GRNBoost fitted to each expression matrix"
- `comparison.split`: "No train/test split; networks inferred from each full expression matrix"
- `comparison.inputs` for TFs+500 evaluations: "BEELINE-preprocessed expression matrix, TFs+500 gene set (token-embedding configurations use only the gene list)"; for TFs+1000 evaluations the same with "TFs+1000".
The configurations already carry `training_setting`, which keeps the zero-shot versus fitted distinction.

**Y3. Protocol descriptions (required).** AUPRC uses the full ranked list (Appendix B.3), not only the top K edges. Replace the `description` of the eight `lit-cells-networks-20261011-ye2026grn-protocol-*` records with: "Rank TF-target candidate edges by absolute weight; early precision ratio scores the top K edges (K = number of reference edges) and AUPRC ratio the full ranked list, each over a random predictor, against the <REFERENCE> reference." where <REFERENCE> is the text each description has now ("STRING functional interactions", "OmniPath signalling and pathway interactions", "non-specific ChIP-seq", "cell-type-specific ChIP-seq").

**Y4. Checkpoint metadata (required).** Appendix A.2 does name some checkpoints, so the note "Checkpoint names are in Table 3 and Appendix A.2, not extracted" with reason `unreported` is inconsistent. For each configuration, add `attributes.checkpoint` and replace `missing_metadata.version` as follows (the same values for the costok, attn and coshid configurations of each model):
- scGPT (`-config-scgpt-{costok,attn,coshid}`): checkpoint "Whole-human checkpoint pretrained on 33 million normal human cells (Appendix A.2)"; `missing_metadata.version` = {"reason": "unreported", "note": "No release or revision named"}.
- Geneformer (`-config-geneformer-*`): checkpoint "12-layer checkpoint, the larger of the 6- and 12-layer releases; Table 3 lists 30M pretraining cells (Appendix A.2; Table 3)"; version note as for scGPT.
- scCello and scPRINT (`-config-sccello-*`, `-config-scprint-*`): checkpoint "Default released pretrained checkpoint (Appendix A.2)"; version note as for scGPT.
- scFoundation and LangCell (`-config-scfoundation-*`, `-config-langcell-*`): no checkpoint attribute; `missing_metadata.version` = {"reason": "unreported", "note": "Source names no checkpoint; Table 3 gives size, layers and pretraining cells"}.

**Y5. DeepSEM method type (required).** Appendix A.2 describes DeepSEM as unsupervised ("in an unsupervised manner"). Change `facets.method_types` from `supervised_machine_learning` to `specialist` on `lit-cells-networks-20261011-ye2026grn-method-deepsem` and `lit-cells-networks-20261011-ye2026grn-config-deepsem`, matching GENIE3 and GRNBoost.

**Y6. GRNBoost configuration (minor).** On `lit-cells-networks-20261011-ye2026grn-config-grnboost`, set `name` to "GRNBoost (Ye et al. 2026 baseline)" (keep `reported_name` "GRNboost" as printed in the headers) and `description` to "GRNBoost run by Ye et al. 2026 directly on each expression matrix with the default benchmark configuration, without pretrained representations. The paper cites GRNBoost2 and arboreto (Moerman et al. 2019, reference 12)." The family link to `discovery-model-grnboost` stays.

## Answers to the collector's questions

Ye 2026:
- Table 1 'ChIP-seq' label: confirmed, and more broadly than the collector checked (scGPT costok only). I compared all 108 Table 1 mean and std cells with Tables 4 and 6. Every one equals the 'Nonspecific ChIP-seq' block for its middle column and the STRING and OmniPath blocks for the others. Not extracting Table 1 is right; the concern stands as written.
- Table 6 'AUPR' as `auprc-ratio`: agreed. Values sit around and above 1, the Table 6 mean rows equal Table 1's "AUPRC ratio" columns exactly, and Appendix B.3 defines only the AUPRC ratio. The concern stands.
- About 2,350 parser-derived results: checked with my own parser (below), not the collector's script. Every cell matches. I also recomputed all 336 mean and std rows from the six dataset rows: every mean matches to rounding, and every std is the sample standard deviation (n - 1). `standard_deviation` with n = 6 is therefore correct. The parser found the GENIE3 duplication, which the collector missed (Y1).
- Archived copy as hash reference: accepted. The gunzipped archive hashes to the recorded raw SHA-256 (a6c3aae5...). bioRxiv returned HTTP 429 to my re-download, so I could not compare a fresh copy.

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

1. Y1: the reviewer's evidence concern is on the source, verbatim, and the 21 Table 7 GENIE3 results carry the reviewer's sentence in `review.note`.
2. Y2: all 1,176 evaluations carry the reviewer's `adaptation`, `split` and gene-set `inputs` text.
3. Y3: the eight protocol descriptions use the reviewer's sentence with each reference's text.
4. Y4: `attributes.checkpoint` and `missing_metadata.version` as specified for the scGPT, Geneformer, scCello, scPRINT, scFoundation and LangCell configurations.
5. Y5: DeepSEM method and configuration are `specialist`.
6. Y6: GRNBoost configuration name and description are the reviewer's text; `reported_name` stays 'GRNboost'.
7. Every record is `source_checked`; each result's and claim's `review` block names the reviewer and keeps the extraction note.

## Records after correction

- benchmark: 1
- configuration: 21
- dataset_subset: 14
- evaluation: 1176
- method: 1
- model: 1
- protocol: 8
- result: 2352
- source: 1
