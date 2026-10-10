# Cell-type annotation transfer: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-cell-type-20261009/` (175 records). Use case: `use-case-cell-type-annotation-transfer`.

Reviewer: a separate Claude review agent that did not extract the batch. No human review is claimed. Nothing was executed or reproduced.

## Verdict

- Both pinned artifacts re-download to their recorded SHA-256. Nothing is archived, because the licence is CC BY-NC-ND 4.0.
- I read only Supplementary Tables S2 and S3. The donor-level demographics in Table S6 were not read or extracted, and I deleted the downloaded workbook after the check. No scratch or batch file holds any of its content.
- All 92 results match their cells, including every configuration's model links.
- The source-wide concern was a prose reversal. The two tables agree with each other, so the concern is lifted and recorded as a limitation, as for Drost.
- The macro-F1 qualifier assumed a class set the source does not state. Corrected on all 46 macro-F1 results.
- Both judgements hold as `proxy` and are `source_checked` with `reviewed_evaluations` (23 each, none excluded). Pins are left for the integrator.
- Every other record is `source_checked`.

Do not rerun `extract/extract_cell_type.py` on this folder; it would overwrite these changes.

## How the check was done

1. Downloaded the article XML and Additional file 3 into an empty directory and hashed them.
2. Read Tables S2 and S3 with a stdlib OOXML reader written for this review; no other sheet was printed or parsed for values, and the extractor's script was not run. I asserted the header row, the section labels and the 23 model rows in each table.
3. For each result I checked:
   - the cell's shortest round-trip decimal against `printed_value` and `numeric_value`;
   - metric, unit and direction;
   - the evaluation's protocol and dataset;
   - that the configuration's `configuration_of` or `uses_model` links name exactly the models in the row label, and that origin is `independent_paper`.
4. 92 expected cells, 92 matched, none missing and none duplicated.
5. Read the article's Results, Methods, Table 2, references and declarations.
6. Dry run: `addBatch` into a scratch copy of the store, then `deriveUseCaseInputs` with the 2 proposed links added in memory.

## Sources and hashes

| Source ID | Artifact | SHA-256 (re-downloaded 2026-10-09T21:28Z) | Matches |
| --- | --- | --- | --- |
| `cell-type-20261009-source-wu2025` | PMC12492631 full-text XML | `368051b7cda5acd4864331875a1faac6f1d68e0a209ed999e4c2ee3b25b57c2c` | Yes |
| `cell-type-20261009-source-wu2025-supp` | `13059_2025_3781_MOESM3_ESM.xlsx` from Springer | `51ecea4318178dfb7dc6b51eae23303d68f25e83641809c95429b082353dc99d` | Yes |

## Values checked

| Source table | Results | Mismatches |
| --- | --- | --- |
| Table S2, Tabula Sapiens to HLCA (6 single, 15 pairwise, 2 full; Accuracy@1 and macro-F1) | 46 | 0 |
| Table S3, HLCA to Tabula Sapiens (same rows) | 46 | 0 |
| Total | 92 | 0 |

Pairwise configurations are shared across both tables, so a configuration named "LangCell + scGPT" also serves the row printed "scGPT + LangCell". The member sets match in every case. Order is irrelevant to summed logits.

## The lead's points

| Point | Finding |
| --- | --- |
| Evidence concern (full-ensemble prose against tables) | The tables are internally consistent. In both, majority voting has the higher Accuracy@1 (S2 0.758 against 0.753; S3 0.83 against 0.82) and logit aggregation the higher macro-F1 (0.163 against 0.119; 0.285 against 0.28). Only Results 'Cross-dataset validation' paragraph 4 reverses this. Its other statements match the tables: the best pairwise ensemble does not beat the best single model on accuracy but does on macro-F1; both full ensembles fall below the best pairs; Geneformer plus scGPT goes from 0.674 to 0.756. Concern lifted; the reversal is a limitation on the supplement source and in both judgements. |
| Origin | `independent_paper` is right for all 46 evaluations. Wu et al.'s ten authors (Wu, Ye, Wang, Hu, Zhu, Yin, Wang, Wang, Hsieh, Hou; Zhejiang University and Hangzhou Carbonsilicon AI Technology) do not appear among the listed authors of the scored models' references: scGPT (Cui et al.), scFoundation (Hao et al.), Geneformer (Theodoris et al.), UCE (Rosen et al.), LangCell (Zhao, Zhang, Wu, Luo, Nie) and scCello (Yuan, Zhan, Zhang, Zhou, Zhao, Han et al.). LangCell's "Wu" is Y. Wu, not J. Wu. The paper declares no competing interests. Some reference author lists are truncated with "et al.", so the check covers only the names printed. |
| New UCE, LangCell and scCello family records | No existing records for these models in main or in any worktree. The stored `ucc-research-method-uce` is "UCE frozen embeddings + classifier", a method identity used in the scTab comparison, not a model family, so a new family record is right. They are not the same identity, so no `alias_of` link is warranted. |
| Ensemble `uses_model` links | Correct for all 15 pairs (two models each) and both full ensembles (all six). The method record is described as summing logits or majority voting, so linking the majority-voting configuration to `method-logit-ensemble` is right in substance, although the ID names only logits. |
| Label-source caveat | The truth labels are the atlases' own annotations: `cell_ontology_class` for Tabula Sapiens and `cell_type` for HLCA core (Table 2). Non-leaf terms and types with fewer than 10 cells were removed, leaving 120 and 37 types, of which 14 are shared (Methods). The use case excludes treating atlas labels as infallible ground truth; this is the first limitation of both judgements. |
| Rejection endpoint | Absent from Tables S2 and S3. The paper's novel-cell-type results are figure-only: AUROC and AUPRC across unseen ratios in Fig. S22, and Accuracy@FPR in Fig. 3e and Fig. S23. So this evidence does not bear on the use case's "explicit unassigned group" output. That is part of why it is proxy, and it is stated in the limitations. |

Further findings:
- **Macro-F1 qualifier.** Methods define macro-F1 "across all classes". The cross-dataset classifier is trained on all source types (120 or 37) on the 20% intra-dataset training split, and applied to every cell of the 14 shared types. The class set the macro-F1 averages over is not stated, so the stored qualifier "over the 14 shared cell types" was an assumption. It now says the class set is not stated.
- **Baselines.** The judgements said conventional baselines (logistic regression, scVI) appear in Fig. 3b. The text reports scVI for cross-dataset transfer (Fig. 3b) and logistic regression only for intra-dataset validation (Fig. 3a). Corrected.
- **Claims.** The two descriptive claims match Results 'Cross-dataset validation' paragraph 2.

## Corrections made in the batch

None changes a value.

1. `...source-wu2025-supp`: evidence concern removed and replaced by a limitation (previous message kept in the receipt).
2. All 46 macro-F1 results: `metric_qualifier` changed from "over the 14 shared cell types" to "test cells of the 14 shared cell types; averaged over 'all classes' (Methods 'Macro-F1'), not stated as the 14 shared types or every source-atlas type".
3. Both judgements: three limitations replaced with fuller ones, plus the training and test design, the absent spread and the prose reversal. `reason` cites this review.

## Judgements

| Judgement | Relevance | Reviewed evaluations | Stratum |
| --- | --- | --- | --- |
| wu2025-ts-to-hlca | proxy | 23 | 1, Tabula Sapiens to HLCA |
| wu2025-hlca-to-ts | proxy | 23 | 2, HLCA to Tabula Sapiens |

Proxy is right for three reasons: atlas labels are the truth, rejection is not tested, and the classifier is OnClass on frozen zero-shot embeddings rather than a complete annotation workflow. The grouping (`wu2025-cross-atlas`) and the macro-F1 headline suit the use case, which needs balanced per-population performance. Accuracy is above 0.6 everywhere, but macro-F1 is 0.08 to 0.30.

Dry run with the 2 links: both are withheld only because pins are not yet recorded. The 5 existing judgements stay active.

## Approved use-case changes

Links and gaps only. No pinned field changes, so the five existing judgements are unaffected; in the dry run they stay active.

Add these `assessed_by` links to `use-case-cell-type-annotation-transfer`:

- `cell-type-20261009-protocol-wu2025-ts-to-hlca`
- `cell-type-20261009-protocol-wu2025-hlca-to-ts`

Add these `evidence_gaps`, exact text:

1. No independent comparison found in this pass prints per-method rejection of unseen cell types (unknown-population F1 or AUROC) for CellTypist, scANVI, SingleR, Azimuth or scArches; such results appear in developer method papers or in figures.
2. Wu et al. 2025's novel-cell-type results (AUROC and AUPRC across unseen ratios, and Accuracy@FPR) are figure-only, as are its scVI cross-dataset baseline and its logistic regression intra-dataset baseline.
3. Boiarsky et al. 2023 (logistic regression against scBERT and scGPT) prints its tables as images in the preprint; the published version was not retrieved.
4. The extracted cross-atlas transfer uses the atlases' own labels as truth, scores only cells of the 14 shared cell types, and does not state which classes its macro-F1 averages over.

Gaps 1 and 3 rest on the collector's screening, which I did not repeat.

## Final summary text

> In Wu et al. 2025 (scFM-Bench), whose authors did not develop the scored models, OnClass classifiers on zero-shot embeddings from six single-cell foundation models transferred cell-type labels between two public atlases, scored on cells of the 14 cell types the atlases share and against the atlases' own annotations, which are not independent ground truth. From Tabula Sapiens to the lung atlas (HLCA), Accuracy@1 ranged from 0.653 (LangCell) to 0.785 (scCello) but macro-F1 only from 0.08 to 0.105; from HLCA to Tabula Sapiens, Accuracy@1 ranged from 0.614 (scGPT) to 0.857 (scCello) and macro-F1 from 0.209 to 0.283 (UCE). The best pairwise ensembles raised macro-F1 to 0.164 (Geneformer + scCello) and 0.303 (UCE + scCello) without exceeding the best single model's accuracy. The source does not state which classes macro-F1 averages over, there is one run per configuration with no spread, no conventional baseline appears in these tables, and rejection of cell types absent from the reference is reported only in figures, so this evidence does not show whether a workflow can flag unsupported populations. The page's other evidence (Abdelaal et al. 2019, scTab) uses separate protocols and is not pooled with these values.

Number trace:
- **Tabula Sapiens to HLCA (Table S2):** Accuracy@1 0.653 (B4, LangCell) to 0.785 (B9, scCello); macro-F1 0.08 (C4) to 0.105 (C9).
- **HLCA to Tabula Sapiens (Table S3):** Accuracy@1 0.614 (B4, scGPT) to 0.857 (B9, scCello); macro-F1 0.209 (C4) to 0.283 (C8, UCE).
- **Best pairwise ensembles:** S2 C24 0.164 (Geneformer + scCello) and S3 C25 0.303 (UCE + scCello). Their accuracies, S2 B25 0.775 and S3 B25 0.852, are below the best single models' 0.785 and 0.857.
- **14 shared cell types:** from Methods 'Batch integration and cell type annotation' paragraph 2, recorded in the protocol and dataset records.

The collector's summary was accurate. This version adds the model names, states that the averaging class set is not stated, and drops the caveat about the evidence concern, which is lifted.

## Remaining gaps

- Figures (Fig. 3, Fig. S19 to S23) were not checked.
- Screened sources in `research.md` were not re-read.
- Pins are not recorded; the integrator pins with this review.
