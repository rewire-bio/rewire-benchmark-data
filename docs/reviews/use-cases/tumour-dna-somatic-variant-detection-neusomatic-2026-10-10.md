# Tumour DNA somatic variant detection: independent review of the NeuSomatic SEQC2 batch, 2026-10-10

Batch: `data/omics/use-case-coverage-somatic-neusomatic-20261010/` (2,595 records). Use case: `use-case-tumour-dna-somatic-variant-detection`. Source: Sahraeian et al. 2022, Genome Biology 23:12, and its Additional file 2 (Supplementary Tables S1 to S10, PDF).

Reviewer: a separate Claude review agent that did not extract the batch. No human review is claimed. Nothing was executed or reproduced.

## Outcome

- Both pinned artifacts re-download to their recorded SHA-256, and the archived copies decompress to the same bytes.
- All 2,464 results match the cells of my own parse of the PDF: Tables S2, S3 and S4, SNV and indel sections. Column identity was confirmed independently against the article prose. Every printed Average equals the mean of its rows within 0.05.
- No number was wrong. No source `evidence_concerns` were raised.
- **Exclusions.** The 42 evaluations of models trained on the SEQC2 HCC1395 data, or not identified, are excluded from the six judgements with reasons. Seven per judgement: six NeuSomatic models and Octopus-RF.
- **Judgements.** All six hold as `direct`. They are `source_checked` with 10 (SNV) or 8 (indel) reviewed evaluations each. Pins are left for the integrator.
- **Records.** Every record is now `source_checked`. I corrected wording in several fields and removed a stray `extract/__pycache__` folder.
- **Batch size.** The full S3 table is kept; I found no quality reason to cut it to its averages.

## How the check was done

1. Downloaded both `artifact_url`s into empty directories and hashed them.
2. Ran `pdftotext -bbox` and wrote my own word-box parser; the extractor's `extract/*.py` were not run.
   - The parser splits each page into table segments at the "Table Sn" titles, so the S5 and S6 headers on the S4 page are not mixed in.
   - Columns are fixed from the x-centres of the numbers in full data rows.
   - Each rotated header word is assigned to the nearest column within 10 points, and must give exactly one name per column.
   - The NeuSomatic-S and NeuSomatic model groups are split at the second DREAM3 header, after checking that the NeuSomatic-S group label lies over the first group.
3. My first attempt split the groups at the midpoint of the two group labels. That assigned the long rotated label "SEQC-WGS-GT50-SpikeWGS10" of the NeuSomatic-S group to the ensemble group, and a uniqueness check caught it. This is the concrete risk with these tables; the final parse gives 17 distinct columns on every page.
4. Matched every result to its cell by table, section, row and column, and compared printed and numeric value, protocol and configuration. 2,464 expected, 2,464 matched, none missing or extra. The '-' cells (SomaticSniper and MuSE in every indel section, nowhere else) are correctly not stored.
5. Checked column identity against the article, independently of the header positions.
   - **Table S2.** NeuSomatic SEQC-WGS-GT50-SpikeWGS10 averages 94.6 (SNV) and 87.9 (indel), as Results 'WGS dataset' states. Its indel lead over the best non-NeuSomatic column (Octopus-RF, 84.2) is 3.7 points, as stated.
   - **Table S3.** With 5% tumour in the 80x normal, the SNV and indel F1 of MuTect2, MuSE and Lancet drop by up to 49.1, 44.1 and 48.3 points ("drops of up to ~50%"). Strelka2's median change over SNVs and indels is about 8.5 points ("8.4% median change"), and NeuSomatic's is under 5.
   - **Table S4.** Indel averages are DRAGEN 72.5, Lancet 67.4, Octopus-RF 66.3 and NeuSomatic 63.6, the order Results give. NeuSomatic's SNV lead over Octopus-RF is 0.6 points, as stated.
   - **Columns.** The two SNV-only columns are SomaticSniper and MuSE; the MuSE identity also follows from its contamination drop.
6. Read the article in full, including Methods on every model, the evaluation region, the author list, references, contributions and competing interests.
7. Integration dry run. `addBatch` against a scratch copy of this worktree's store passes (SHACL not run). With the six `assessed_by` links pinned in memory, `deriveUseCaseInputs` gives all six new judgements `active` (10, 8, 10, 8, 10 and 8 evaluations) and all 16 existing judgements `active`.

## Sources and hashes

| Source ID | Artifact checked | SHA-256 (re-downloaded 2026-10-10) | Matches record |
| --- | --- | --- | --- |
| `somatic-neusomatic-20261010-source-sahraeian2022` | PMC8740374 full-text XML | `78dbe540c2558585bc7537e0e6563706fdaa329b2708e5dc82b77074379b4a6e` | Yes |
| `somatic-neusomatic-20261010-source-sahraeian2022-additional-file-2` | `13059_2021_2592_MOESM2_ESM.pdf` from static-content.springer.com | `10a109d80f6f49446ea84bd9f7f6b31c20d634516c8666376ac8a8f51f3236d0` | Yes |

## Values checked

| Table | Rows (per section) | Results | Mismatches | Largest Average gap |
| --- | --- | --- | --- | --- |
| S2, 21 WGS replicate pairs and Average | 22 | 704 (374 SNV, 330 indel) | 0 | within 0.05 |
| S3, 47 purity and coverage pairs and Average | 48 | 1,536 (816 SNV, 720 indel) | 0 | within 0.05 |
| S4, 6 library pairs and Average | 7 | 224 (119 SNV, 105 indel) | 0 | within 0.05 |
| Total | | 2,464 | 0 | 0.05 |

## Corrections made in the batch

No number, ID, link or comparison field changed. The collector's copy has SHA-256 `754952bfcc017435d61543a747ccc997538050caebd16ff17d7f435d77e3616f`. The reviewed `batch.jsonl` has SHA-256 `448750cd0f42f62c3524a897d4c9181e8d1a85036f02c9251e233e4127e7fd5d`; `review.json` binds it and every other file in the folder.

1. **Status.** Every record is `source_checked`. Results carry a `review` block, with the collector's note kept.
2. **`evidence_overlap`** on the 42 SEQC2-model evaluations. These said "the cell line, truth set and evaluation region are shared with training". The evaluation region is held out from SEQC-WGS-GT-50 training, so that was wrong for GT-50. It is true for the Spike models, which were trained across the genome. Each note now states the training data of its own model.
3. **Octopus-RF `training_overlap`.** It said Results describe the forest as "trained on the SEQC-WGS-GT50-SpikeWGS10 training data". Results say the authors trained Octopus forests on their SEQC2 training sets, and that the GT50-SpikeWGS10 forest did best, but not which forest the tables use. Rewritten as unresolved, with the same text as a `model_identity_note`.
4. **WGS dataset `population`.** It now explains the seven site codes against six centres (concern 3 below).
5. **Limitations.** All six protocol and judgement `limitations` were rewritten.
   - Two statements not in the source were removed: "caller versions are from 2017-2021", and that the authors trained the Octopus forest.
   - Added: the patent application, the truth-set authorship, NeuSomatic ensemble inputs, the 1 ng library coverage, and the titration design.
6. **Constraints.** The constraint asking readers to exclude the seven models by hand is replaced by the `excluded_evaluations` entries. A new constraint says the paper's own rankings, which use the excluded models, differ from what is shown.
7. **Judgement `endpoint`.** It now says how many of the configurations are shown.

## Collector concerns and lead questions: decisions

1. **The 42 flagged evaluations: excluded.**
   - This follows my earlier HCC1395 decision on Guille et al. (NeuSomatic and DeepSomatic excluded) and the use case's exclusion "Callers evaluated only with a pre-trained model built from the test cell line or simulator".
   - **GT-50 and GT50-SpikeWGS10** (NeuSomatic and NeuSomatic-S) were trained on HCC1395/HCC1395BL replicates with the SEQC2 truth set in the other half of the genome.
   - **SEQC-WGS-Spike** was trained on spike-ins into HCC1395BL replicates across the whole genome.
   - The scored region removes truth-label overlap for GT-50, but not same-cell-line and same-library overlap. GT50-SpikeWGS10 was also chosen as the default model from these same evaluations.
   - Each exclusion has a model-specific reason.
2. **Octopus-RF: excluded as unresolved.**
   - Methods say Octopus-RF filters with "the pretrained random forest model". Results say "we used the same training datasets to train random forest classifiers for Octopus", report an average gain of about 10 points over Octopus-hard from "these models trained on SEQC2 samples", and say "despite the advantage observed in training Octopus on SEQC2 data". The tables do not say which forest is in the Octopus-RF column.
   - Its gain over Octopus-hard in the Tables S2 to S4 averages (3.3 to 35.2 points) fits the SEQC2-trained reading but does not prove it.
   - As with DeepSomatic before, a model whose identity is unresolved, and that may be trained on the test cell line, is excluded. Origin stays `author_reported`.
3. **DREAM3 models: kept.**
   - NeuSomatic and NeuSomatic-S DREAM3 were trained on ICGC-TCGA DREAM Stage 3 in silico data (Methods 'DREAM3 model'), not on SEQC2 or HCC1395.
   - The use-case exclusion for a model built from "the test simulator" applies to DREAM test sets, not to this HCC1395 test.
   - They are the developers' models and stay `author_reported`.
4. **S3 and S4 rows for SEQC2-trained models: excluded for every SEQC2-trained model.**
   - The titration and library-preparation libraries are not described as training data, and the region is held out.
   - The cell line, truth set and (for the Spike-based models) the scored region are shared with training.
   - Applying the same rule across all six protocols keeps one comparison set per study, and avoids showing these models only where the overlap is harder to see.
5. **Six centres against seven site codes.**
   - Results say "21 WGS replicates sequenced in six sequencing centers"; the row labels carry EA, FD, IL, LL, NC, NS and NV.
   - Methods describe "multiple NovaSeq sequencing replicates from Illumina", so IL (HiSeq) and NV (NovaSeq) are probably both Illumina. That makes six centres and seven centre-platform codes.
   - The source does not state this outright, so it is recorded as probable on the dataset and in the S2 limitations. No value depends on it.
6. **SomaticSeq and truth-set authorship.**
   - The SEQC2 truth set (v1.0) was built with the SomaticSeq classifier (reference 20, whose authors include co-authors L. T. Fang and M. Mohiyuddin).
   - The SEQC2 reference papers (references 2 and 3) have co-authors W. Xiao and L. T. Fang as first authors.
   - S. M. E. Sahraeian and M. Mohiyuddin have filed a patent application on NeuSomatic.
   - So the truth set and the evaluated model come partly from the same people. That is a limitation, not an evidence concern: the truth set is the consortium's public reference.
   - Which callers fed the truth set is not stated in this paper, so I make no claim that the compared callers are favoured.
7. **DRAGEN reuse: correct, but the description should be broadened.** `cnv-20261009-method-dragen` is the DRAGEN family record and the right target for the v3.7.5 somatic configuration. Its description, "Illumina DRAGEN secondary analysis platform; CNV and integrated CNV-SV callers.", now misdescribes its uses. Follow-up correction (a `records -- change` on the stored record, with a `metadata-correction-*` claim keeping the old value):
   - **Description:** "Illumina DRAGEN secondary analysis platform, used here for copy-number and integrated CNV-SV calling and for somatic small-variant calling."
   - **Source:** add `somatic-neusomatic-20261010-source-sahraeian2022` to its `source_ids`.
   - No pinned field is affected; method records are not pinned by judgements.
8. **Batch size.** Kept in full. Every S3 cell was verified, the per-row values carry the purity, coverage and contamination detail the use case asks about, and the averages alone would lose the normal-contamination rows.

## Origins and records

- Origins:
  - `independent_paper` for VarDict, SomaticSniper, MuSE, DRAGEN, Octopus-hard, MuTect2, Lancet and Strelka2. No author is a developer of these.
  - `author_reported` for all NeuSomatic and NeuSomatic-S rows and for Octopus-RF.
  - DRAGEN v3.7.5 is Illumina's; the authors are at Roche, the FDA and NCBI.
- Configuration versions match Methods 'Somatic mutation detection algorithms'.
- The new Octopus method record's description comes from the title of reference 17.
- All reused methods resolve in the store.

## Judgements

| Judgement (`use-case-mapping-somatic-neusomatic-20261010-`) | Relevance | Reviewed | Excluded | Decision |
| --- | --- | --- | --- | --- |
| `wgs-snv` | direct | 10 of 17 | 7 SEQC2-trained or unidentified | Holds |
| `wgs-indel` | direct | 8 of 15 | 7 | Holds |
| `titration-snv` | direct | 10 of 17 | 7 | Holds |
| `titration-indel` | direct | 8 of 15 | 7 | Holds |
| `library-prep-snv` | direct | 10 of 17 | 7 | Holds |
| `library-prep-indel` | direct | 8 of 15 | 7 | Holds |

All six are `direct`: paired tumour-normal WGS of a reference cancer cell line against a consortium truth set, varying the sequencing site, purity, coverage, normal contamination and library, which is the regime the question asks about. The groups (`neusomatic2022-seqc2-*`, SNV and indel strata) and the `f1-score` headline hold. The `review` follows the earlier reviews; `reviewed_at` is 2026-10-10T06:25:00Z. Pin with `npm run use-cases:repin -- docs/reviews/use-cases/tumour-dna-somatic-variant-detection-neusomatic-2026-10-10.md <claim-id>...`.

## Approved use-case changes

Apply to `use-case-tumour-dna-somatic-variant-detection`. These are links, sources, citations and gaps only, so no pinned field changes and the 16 existing judgements need no re-pin; the dry run confirms they stay active.

1. Add `assessed_by` links to the six protocols `somatic-neusomatic-20261010-protocol-sahraeian2022-{wgs,titration,library-prep}-{snv,indel}`.
2. Add `source_ids` `somatic-neusomatic-20261010-source-sahraeian2022` and `somatic-neusomatic-20261010-source-sahraeian2022-additional-file-2`.
3. Add a `citation_locator`: `somatic-neusomatic-20261010-source-sahraeian2022-additional-file-2`, "Additional file 2 Tables S1-S4; see data/omics/use-case-coverage-somatic-neusomatic-20261010/claims.csv".
4. In `evidence_gaps`, replace "SEQC2 HCC1395 whole-genome caller comparisons (Xiao et al. 2021; NeuSomatic 2022 Additional file 2) were not extracted: the first is not open access through Europe PMC and the second prints its tables only in a PDF with rotated headers." with:
   - "The SEQC2 consortium's own whole-genome caller comparison (Xiao et al. 2021) was not retrieved (not open access through Europe PMC); Sahraeian et al. 2022 Tables S5 to S10 (WES, AmpliSeq, FFPE, sample-specific models, runtime) are not linked."
5. Append to `evidence_gaps`:
   - "The SEQC2 whole-genome comparison is a developer study on one cell line, and the developers' SEQC2-trained NeuSomatic models and Octopus-RF are excluded for training on that cell line; no linked comparison tests those models on an independent tumour."

## Summary text

The use case has a reviewed summary claim (`use-case-summary-tumour-dna-somatic-variant-detection`). Adding six judgements changes its pinned evaluation set, so it must be updated and re-pinned in the same change. Replace its `value` with the text below, add the two Sahraeian sources to its `source_ids` and `source_locator`, and re-pin it by name with this review. I re-read the unchanged sentences against their stored results: they still hold.

> Four studies are linked, and their values cannot be pooled: truth sets, sequencing, caller versions and scoring scripts differ. Values are rounded to two decimals, except where the source prints percentages. In the Lancet developers' own virtual-tumour test, Lancet and Strelka2 both reached SNV F1 0.85, with indel F1 0.81 and 0.77. Wang et al. 2020 ran eight callers, NeuSomatic and their own majority-vote ensembles on eight whole-genome tumour-normal pairs, with older caller versions (for example MuTect2 from GATK 3.7). An ensemble had the highest SNV F1 on seven of the eight pairs; on DREAM set 4, NeuSomatic, whose model was trained on DREAM set 3, was highest at 0.86. The best single configuration reached SNV F1 0.92 to 0.96 on the simulated DREAM sets 1 to 3 but 0.70 to 0.81 on the CLL, AML and MB tumours, where most callers had precision below 0.6 against curated truth sets that the authors say may be incomplete, so precision there is a lower bound. Indel F1 on the CLL and MB tumours and the COLO829 cell line (AML has no indel truth set) was at most 0.72 for every configuration. Guille et al. 2025, who did not develop the callers, scored them on a WES replicate of the SEQC2 HCC1395 cell line (1,160 truth SNVs, 50 truth indels); another replicate with the same truth set was used to choose their ensembles. Leaving out DeepSomatic and NeuSomatic, whose pre-trained models were built with HCC1395 data, the best single caller reached SNV F1 0.85 (Mutect) and indel F1 0.66 (VarNet), and the authors' ensembles reached 0.88 for SNVs and 0.75 and 0.74 for indels. Strelka reached SNV F1 0.64 there, with precision 0.51, against 0.85 for Strelka2 in the Lancet test, which shows how much results depend on the study. Sahraeian et al. 2022, the NeuSomatic developers, scored callers on SEQC2 HCC1395 whole-genome data in the half of the genome held out from their model training: 21 replicate pairs from six centres, 47 tumour purity and coverage mixtures, and six library preparations. Their NeuSomatic and NeuSomatic-S models trained on SEQC2 data (SEQC-WGS-Spike, SEQC-WGS-GT-50 and SEQC-WGS-GT50-SpikeWGS10) and Octopus-RF, whose random forest is not identified, are left out because they were built from the same cell line or may have been. Among the rest, mean F1 over the 21 replicates was 92.3% for DRAGEN, 91.8% for NeuSomatic with its DREAM3 model and 89.0% for Strelka2 for SNVs, and 81.7%, 79.3% and 72.8% for indels. Over the purity and coverage mixtures (10x to 300x, 5% to 100% tumour), mean SNV F1 was at most 67.7% (Octopus with hard filters). With 5% tumour in an 80x normal, SNV F1 for a pure tumour fell from 88.6% to 43.8% for MuTect2 and from 93.3% to 47.8% for Lancet, but only from 92.4% to 90.9% for Strelka2. None of the linked studies reports interval estimates or covers FFPE tissue, ctDNA, tumour-only calling or targeted panels, and none establishes clinical performance.

New statements and their records (prefix `somatic-neusomatic-20261010-`):

| Statement | Record | Printed |
| --- | --- | --- |
| 21 pairs, 47 mixtures, 6 libraries | `data-sahraeian2022-wgs`, `-titration`, `-library-prep` (`population`) | |
| Held-out half of the genome | `protocol-sahraeian2022-*` (`protocol`) | |
| Excluded models and reasons | `use-case-mapping-somatic-neusomatic-20261010-*` (`excluded_evaluations`) | |
| DRAGEN 92.3 / 81.7 | `result-sahraeian2022-dragen-wgs-snv-average`, `-dragen-wgs-indel-average` | 92.3; 81.7 |
| NeuSomatic DREAM3 91.8 / 79.3 | `result-sahraeian2022-neusomatic-dream3-wgs-snv-average`, `-indel-average` | 91.8; 79.3 |
| Strelka2 89.0 / 72.8 | `result-sahraeian2022-strelka2-wgs-snv-average`, `-indel-average` | 89.0; 72.8 |
| Mixtures, at most 67.7 (Octopus-hard) | `result-sahraeian2022-octopus-hard-titration-snv-average` (highest of the 10 shown) | 67.7 |
| MuTect2 88.6 to 43.8 | `result-sahraeian2022-mutect2-titration-snv-spp-80x-100-t-spp-80x-100-n`, `...-spp-80x-95-n` | 88.6; 43.8 |
| Lancet 93.3 to 47.8 | `result-sahraeian2022-lancet-titration-snv-spp-80x-100-t-spp-80x-100-n`, `...-spp-80x-95-n` | 93.3; 47.8 |
| Strelka2 92.4 to 90.9 | `result-sahraeian2022-strelka2-titration-snv-spp-80x-100-t-spp-80x-100-n`, `...-spp-80x-95-n` | 92.4; 90.9 |

## Checks run

`npm test` passed (47 files, 500 tests) and `npm run typecheck` passed, on the worktree with the reviewed batch. The batch is not yet in the store, so the tests do not read it; the scratch `addBatch` and `deriveUseCaseInputs` dry run is the check that covers it. `npm run build` and SHACL shapes were not run.

## Remaining gaps

- Precision and recall, VAF bins and difficult regions are figure-only; Tables S5 to S10 and Additional file 1 were not checked.
- Which WGS pairs were used for training is not stated, so the S2 overlap cannot be narrowed to specific rows.
- The Octopus-RF forest remains unidentified; the Octopus authors' pretrained somatic forest was not checked.
