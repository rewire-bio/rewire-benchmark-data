# Patient RNA splicing validation: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-rna-splicing-20261009/` (441 records). Use case: `use-case-patient-rna-splicing-validation`.

Reviewer: a separate Claude review agent that did not extract the batch. No human review is claimed. Nothing was executed or reproduced.

## Verdict

- All pinned artifacts re-download to their recorded SHA-256, and the two archived copies decompress to the same bytes.
- All 348 results match their cells. No value, printed form, locator, metric, unit, direction or configuration, protocol and dataset link was wrong.
- The Drost source-wide concern was a prose slip that touches no stored value. It is now a limitation, so the three Drost judgements can show.
- The identical CAGI6 rows in Drost Table S4 are not a copy error, so nothing was disputed.
- Four judgements change from `direct` to `proxy`: the three Drost judgements and Segers splicing. Segarra-Casas splicing stays `direct`.
- All 7 judgements are `source_checked`, with `reviewed_evaluations` set and pins left for the integrator. Every other record is `source_checked`.
- `negative-predictive-value` in `data/vocab/metric.ttl` is now byte-identical to the RNA pathogen branch.

Do not rerun `extract/extract_rna_splicing.py` on this folder; it would overwrite these changes.

## How the check was done

1. Downloaded each artifact into an empty directory, unpacked the Drost supplement zip, and hashed `mmc2.xlsx`.
2. Read the tables with stdlib readers written for this review; the extractor's scripts were not imported or run:
   - Drost Data S1 Tables S3 and S4: raw OOXML `<v>` text;
   - Segarra-Casas Table 2 and Segers Table 2: article XML, with bold markup read per cell.
3. For each result, compared:
   - the raw value with `raw_xml_value`;
   - the shortest round-trip decimal with `printed_value` and `numeric_value`, or exact text for XML cells;
   - metric, unit and direction from the headers;
   - bold with `printed_source_cell`;
   - the evaluation, configuration, protocol and dataset implied by the row, block and column.
4. 348 expected cells, 348 matched, none missing and none duplicated.
5. Recovered integer counts from Drost Table S4. The positives and negatives are 155 and 88 (entire), 37 and 19 (CAGI6) and 118 and 69 (in-house). The entire-dataset TP and TN equal CAGI6 plus in-house for all eight rows.
6. Recounted the Yes cells in Segarra-Casas Table 2 and the top-10 ranks in Segers Table 2.
7. Dry run: `addBatch` into a scratch copy of the store, then `deriveUseCaseInputs` with the 7 proposed links added in memory.

## Sources and hashes

| Source ID | Artifact | SHA-256 (re-downloaded 2026-10-09T20:50Z) | Matches |
| --- | --- | --- | --- |
| `rna-splicing-20261009-source-drost2025` | PMC12547740 full-text XML | `2a2e970526e4348d505d26356b830d96da9e32688c4de84841ac8137b62d5d32` | Yes |
| `rna-splicing-20261009-source-drost2025-data-s1` | `mmc2.xlsx` in the Europe PMC supplementaryFiles zip | `a3a69202b8f0d9ecb7fa22a16991d5e4d583b5ae72fd598206ea5c2b4c5c14ca` | Yes |
| `rna-splicing-20261009-source-segarracasas2025` | PMC12257123 full-text XML | `6e61a917c80d08357fe7316ad84f5cb84ac457fcce4cb1d3b5bf866046e2095d` | Yes |
| `rna-splicing-20261009-source-segers2026` | PMC13019952 full-text XML | `af11b79beec80f945a14f13ce487193ad733d740cace922eba0bd6d63b9de560` | Yes |

The outer zip hash differs on this download (`25e26cf1...`), as expected for a per-request Europe PMC bundle. The member file matches.

## Values checked

| Source table | Results | Mismatches |
| --- | --- | --- |
| Drost Data S1 Table S3 (AUROC, AUPRC; entire and two strata) | 24 | 0 |
| Drost Data S1 Table S4 (six metrics, eight rows, three blocks) | 144 | 0 |
| Segarra-Casas Table 2 (16 events, five callers and OUTRIDER z-score) | 96 | 0 |
| Segers Table 2 (12 genes, seven method columns) | 84 | 0 |
| Total | 348 | 0 |

## The collector's points

| Point | Finding |
| --- | --- |
| Drost source-wide concern (SQUIRLS AUPRC 0.888 in prose, 0.881 in S3) | A prose slip; no stored value depends on it. Table S3 D13 stores 0.8815, and the prose 0.888 is closer to SPiP's 0.8886. The same paragraphs cite Table S3 for thresholded values that are in Table S4. Both are now a limitation on the article source and in the three Drost judgements. The concern was removed, so the judgements can show. |
| Drost S4 CAGI6 identical rows | Not a copy error. The block implies 37 positives and 19 negatives, and Pangolin, SPiP and SpliceAI each have 32 true positives and 16 true negatives. Subtracting each tool's in-house counts from its entire-dataset counts gives the same 32 and 16 for each tool separately, and the decomposition holds for all eight rows. Their AUROC and AUPRC differ in Table S3, so only the thresholded calls coincide. Nothing disputed; the CAGI6 limitation now says this. |
| Pangolin "4.3.1" | Methods print "Pangolin version 4.3.1". Version numbers in the 4.x series match releases of the unrelated SARS-CoV-2 lineage tool also named pangolin, so the printed number may not identify the splicing model's release. Recorded as printed, with a `model_identity_note` on the configuration and a judgement limitation. |
| Segarra-Casas 68.7% against 66.6% | Results paragraph 3 and Discussion paragraph 5 give 68.7% (11/16); Discussion paragraph 10 gives 66.6%. Table 2 has 10 Yes cells plus case 2 ("*Only identified with all cohort samples"), so 11 of 16 (68.75%). 66.6% is a prose slip. |
| Segarra-Casas n=34 against n=98 | Table 2 reflects the full 98-sample cohort. Results paragraph 3 says the 16 events were identified "in all 98 samples", and that with the 34-sample batch 1 FRASER2 missed only case 2. The batch 1 comparison (Figure 2A and 2B) is about outlier counts and agreement, not Table 2. The limitation now says this instead of "per-run sample count not printed". |
| Segers origin per row | Correct. The saseR-junctions and saseR expression rows are `author_reported`. FRASER 2.0 (autoencoder, PCA), OUTRIDER (autoencoder, PCA) and OutSingle are `independent_paper`, but the saseR authors ran and configured all of them; that is now a limitation. Also added: the 12 genes are those reported by Kremer, Brechtmann (OUTRIDER) and Mertes (FRASER) on this cohort, found partly with OUTRIDER and FRASER, which can favour those approaches. |

Other checks:
- Drost tool versions match Methods: SPiP 2.1 and SQUIRLS 2.0.1, with SpliceAI scores taken from precomputed WGSA 0.95. Segarra-Casas versions match Methods: FRASER v1.8.1, FRASER2 v1.99.4, rMATS-turbo v4.1.2, LeafCutterMD v0.2.7 and OUTRIDER v1.20.1. The Segers article prints no versions for saseR or the comparators; I did not open Additional file 1.
- Segarra-Casas counts from Table 2: FRASER |dPSI| > 0.1 13 of 16 (Results print 81.26%; exact is 81.25%), |dPSI| > 0.3 9, FRASER2 10 plus case 2, rMATS-turbo 7, LeafCutterMD 4 (25%). Bold coincides with Yes in every caller cell.

## Corrections made in the batch

None changes a value.

1. `...source-drost2025`: evidence concern removed and replaced by a limitation (previous message kept in the receipt).
2. `...config-drost2025-pangolin`: `model_identity_note` added.
3. Two claim locators corrected, and `claims.csv` updated:
   - `...claim-segarracasas2025-leafcuttermd-intron-retention`: "Discussion paragraph 3" changed to "Discussion paragraph 5".
   - `...claim-segarracasas2025-prose-detection-rates`: "Discussion paragraph 6" changed to "Discussion paragraphs 5 and 10".
4. Judgements:
   - Drost merged, in-house and CAGI6, and Segers splicing: relevance changed from direct to proxy, with new rationales.
   - Drost: limitations added on the truth method, the author-devised consensus rule, the prose slips, the Pangolin version and the duplicate precision and PPV columns. The CAGI6 limitation was replaced.
   - Segers: limitations added on the truth-set origin and the developer-run comparators.
   - Segarra-Casas: limitations added on the 66.6% figure and the repeated CAPN3 variant; the cohort-size limitation was replaced, and the OUTRIDER bold note was added.
5. `data/vocab/metric.ttl`: removed the extra `skos:altLabel "Neg Pred Value"` so the `negative-predictive-value` block matches the RNA pathogen branch byte for byte. The two branches now add the same 8-line hunk at the same base line (808), so they merge cleanly. Their other insertions do not overlap: splicing at 468, 625 and 1546; pathogen at 1162 and 1170.

## Judgements

| Judgement | Relevance | Reviewed evaluations | Grouping |
| --- | --- | --- | --- |
| drost2025-merged | proxy (was direct) | 8 | `drost2025-rna-validated-variants`, stratum 1, headline AUROC |
| drost2025-inhouse | proxy (was direct) | 8 | stratum 2 |
| drost2025-cagi6 | proxy (was direct) | 8 | stratum 3 |
| segarracasas2025-splicing | direct | 5 | `segarracasas2025-muscle`, stratum 1, headline event-detected |
| segarracasas2025-outrider | proxy | 1 | stratum 2, headline z-score |
| segers2026-kremer-splicing | proxy (was direct) | 3 | `segers2026-kremer`, stratum 1, headline known-gene-rank |
| segers2026-kremer-expression | proxy | 4 | stratum 2 |

None excludes an evaluation.

Why the changes:
- **Drost.** The use case's `output` asks for a recovery curve of known pathogenic splicing events in patient RNA-seq, and keeps sequence classification as "a separate sequence-classification proxy". Drost scores DNA-only predictors against RT-PCR and exon-trapping outcomes, which is that proxy kind of evidence, and its inputs are not patient RNA-seq reads.
- **Segers splicing.** Its 12 genes mix expression and splicing defects without saying which, so a splicing-caller rank is not a recovery of known splicing events. The comparison is also developer-run.
- **Segarra-Casas splicing stays direct.** It recovers known pathogenic events with several callers on the same patient tissue RNA-seq (matched tissue, as the inputs allow).

Grouping and headlines follow the source tables and are right.

Dry run with the 7 links: all 7 are withheld only because pins are not yet recorded. The FRASER judgement stays active.

## Vocabulary

| Concept | Check | Outcome |
| --- | --- | --- |
| `negative-predictive-value` | Same definition and STATO_0000619 match as reviewed on the RNA pathogen branch | Block made byte-identical |
| `z-score` | OLS4 STATO_0000104 "z-score": "a measure of the divergence of an individual experimental result from the most probable result, the mean. Z is expressed in terms of the number of standard deviations from the mean value." Same meaning; direction unknown is right because the sign shows under- or over-expression | Accepted with `skos:exactMatch` STATO_0000104 |
| `event-detected` | Categorical Yes or No per known event; not a rate. Matches Segarra-Casas Table 2. Direction unknown is cautious: a Yes is the desired outcome, but `numeric_value` is null anyway | Accepted, unmapped |
| `known-gene-rank` | Rank of the gene within the patient's sample, 1 best; matches the Segers footnote ("rank of the scores for disease-related gene within diagnosed patients") | Accepted, unmapped |

## Approved use-case changes

Links and gaps only. No pinned field (question, decision, inputs, output, setting, exclusions, clinical scope) changes, so the FRASER judgement `use-case-mapping-amp-20261007-issue12-fraser-kremer` and its pins are unaffected. In the dry run it stays active with the links added; use-case links are not pinned.

Add these `assessed_by` links to `use-case-patient-rna-splicing-validation`:

- `rna-splicing-20261009-protocol-drost2025-merged-243`
- `rna-splicing-20261009-protocol-drost2025-inhouse`
- `rna-splicing-20261009-protocol-drost2025-cagi6`
- `rna-splicing-20261009-protocol-segarracasas2025-known-event-detection`
- `rna-splicing-20261009-protocol-segarracasas2025-outrider-zscore`
- `rna-splicing-20261009-protocol-segers2026-kremer-splicing-rank`
- `rna-splicing-20261009-protocol-segers2026-kremer-expression-rank`

Add these `evidence_gaps`, exact text:

1. AbSplice (Wagner et al. 2023, Nat Genet) reports its tissue-aware comparison with SpliceAI, MMSplice, SQUIRLS and CADD-Splice only in figures and prose in the copies screened, so no tissue-aware DNA predictor comparison is stored.
2. The FRASER 2.0 article (Scheller et al. 2023, AJHG) could not be retrieved as full text, and its comparison with FRASER, LeafCutterMD and SPOT on patient cohorts was not extracted.
3. No table comparing MMSplice, CADD-Splice or AbSplice against RNA-validated variants was found in this pass; Drost et al. cover SpliceAI, Pangolin, SPiP and SQUIRLS only.
4. Drost et al. variant-type strata (Data S1 Tables S5 and S6) are not extracted.
5. Among the sources extracted, no RNA-seq caller comparison reports false positives per sample in a table; outlier workload is figure-only in Segarra-Casas et al.
6. Minigene or MFASS-style proxies beyond the existing MFASS mapping were not added in this pass.

Gaps 1 and 2 rest on the collector's screening, which I did not repeat.

Not approved here: the collector's later wording for `inputs`. When the integrator does widen `decision`, `inputs` and `output` to describe the DNA-predictor and multi-caller evidence, the FRASER judgement must be re-reviewed and re-pinned in the same change.

## Final summary text

> The one recovery result already on this page is FRASER on the 119-sample Kremer fibroblast cohort, reported by its developers: a mean 85% (11 of 13) of known pathogenic splicing events recovered at a 30-sample subsample. Three published comparisons add evidence. Segarra-Casas et al. (2025), independent of the tool developers, recorded which callers reported 16 known pathogenic splicing events in clinical muscle RNA-seq from 98 samples: FRASER with |dPSI| > 0.1 reported 13, FRASER with |dPSI| > 0.3 reported 9, FRASER2 10 (and one more only with the full cohort), rMATS-turbo 7 and LeafCutterMD 4 (Table 2); the events were established partly with these callers. Segers et al. (2026), the saseR developers, ranked 12 reported disease genes in the Kremer cohort: the gene ranked within the top 10 in 9 of 12 samples for saseR-junctions, in 6 of 12 for FRASER 2.0 with the autoencoder and in 7 of 12 for FRASER 2.0 with PCA (Table 2); the 12 genes were reported in earlier analyses of the same cohort, partly with OUTRIDER and FRASER, and several are expression rather than splicing defects. Drost et al. (2025), a diagnostic laboratory independent of the tool developers, scored 243 clinically ascertained variants, each tested for a splicing effect in patient cells or by exon trapping, with four DNA-based predictors. On all 243, AUROC was 0.895 for SpliceAI, 0.885 for Pangolin, 0.830 for SPiP and 0.806 for SQUIRLS (Data S1 Table S3); at literature thresholds sensitivity was 0.871, 0.858, 0.832 and 0.800 and specificity 0.750, 0.773, 0.761 and 0.591 (Table S4), and the authors' rule of requiring at least two of the four tools gave sensitivity 0.916 and specificity 0.727. Most in-house variants were sent for testing because another predictor (Alamut) flagged them, so negatives are mostly predicted-but-unconfirmed variants. All values are transcribed from the publications, not reproduced; none is a diagnostic-yield estimate, and results from different sources measure different endpoints and must not be pooled. This summary describes evidence and does not recommend a clinical workflow.

Number trace:
- **FRASER:** 85% and 11 come from the two stored `amp-oncology-rna-20261007-issue-12-result-fraser-2021-article-implementation-*` results; the evaluation is `author_reported`.
- **Segarra-Casas:** counts of Yes in Table 2 per caller column (13, 9, 10 and 7), LeafCutterMD 4, and case 2 for the extra FRASER2 call. 98 samples is from Results paragraph 3.
- **Segers:** ranks of 10 or less in Table 2:
  - saseR-junctions: 2, 7, 1, 1, 9, 5, 4, 3, 3 (9 genes);
  - FRASER 2.0 autoencoder: 1, 9, 1, 7, 2, 1 (6);
  - FRASER 2.0 PCA: 2, 6, 1, 4, 4, 2, 1 (7).
- **Drost AUROC:** C10 to C13 of Table S3 (0.8852, 0.8305, 0.8946, 0.8061).
- **Drost sensitivity and specificity:** C7 to D10 of Table S4.
- **At least two:** C13 0.9161 and D13 0.7273.
- **Alamut:** claim `...claim-drost2025-alamut-selection` (87%, 176 of 202).

The collector's summary is accurate. This version opens with the FRASER result, names the consensus rule as the authors', and states the Segers truth-set origin. It drops the line about the AUPRC prose slip, which is now a limitation rather than a concern.

## Remaining gaps

- Figures, Drost Tables S1, S2, S5 and S6, and Segers Additional file 1 were not checked.
- Screened sources, including the AbSplice preprint, were not re-read.
- The Pangolin release used by Drost et al. is not established.
- Pins are not recorded; the integrator pins with this review.
