# Tumour DNA somatic SNV and indel calling: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-somatic-20261009/` (1,238 records). Use case: `use-case-tumour-dna-somatic-variant-detection`.

Reviewer: a separate Claude review agent that did not extract the batch. No human review is claimed. Nothing was executed or reproduced; this is a check of transcription against the pinned sources and of the relevance judgements.

## Outcome

- All five pinned artifacts re-download to their recorded SHA-256. The archived `artifacts/*.gz` decompress to the same bytes.
- All 918 results match their source cells: printed value, numeric value, locator, metric, qualifier, unit, direction, configuration, protocol and truth count. No number was wrong.
- F1 recomputes from the printed precision and recall on every Wang et al. row (largest difference 0.0012, from three-decimal rounding). In Guille et al. Table S7, TPR, PPV and F1 recompute exactly from TP, FP and P on all 33 rows.
- One Wang et al. row is internally inconsistent (COLO829, VarDict standalone; see Conflicts). Its values are transcribed correctly; its evaluation is excluded from the judgement.
- No source `evidence_concerns` were raised. Every problem found is limited to specific rows and is handled with `excluded_evaluations` or limitations.
- Nine evaluations are excluded from judgements, each with a reason: DeepSomatic and NeuSomatic on Guille's HCC1395 sample (SNV and indel, 4), NeuSomatic on Wang DREAM set 3 (Pass and Lowqual, SNV and indel, 4), and the inconsistent COLO829 VarDict standalone SNV row (1).
- All 15 judgements hold after correction and are set to `source_checked` with `reviewed_evaluations`. Pins are left for the integrator.
- Every record is now `source_checked`. Results and descriptive claims carry a `review` block.

## How the check was done

1. Downloaded each `artifact_url` into an empty directory: the two article XMLs from Europe PMC, the Wang workbook from the publisher, and the Guille Europe PMC `supplementaryFiles` zip. Hashed the files and the two zip members.
2. Read the Wang workbook with a stdlib OOXML reader written for this review and Table S7 with a stdlib BIFF8 reader written for this review. The extractor's `extract/*.py` were not imported or run.
3. Built the expected identity of every cell from the sheet structure (dataset block in column A, truth count in column B, row label in column C or A, metric from the column header, variant type from sheet or column L). Matched every result to its cell through `source_locator` and compared raw text, `printed_value` (shortest round-trip decimal), `numeric_value`, metric, qualifier, unit, direction, the evaluation's configuration `reported_name`, protocol, dataset, `comparison.protocol_id` and the protocol `denominator`. Expected 720 Wang cells and 198 Guille cells; all matched once, none missing, none duplicated.
4. Read the Methods, Results and Discussion of both articles, Guille Tables 1 and 2 and the supplementary methods DOCX, to check versions, datasets, protocols, `missing_metadata`, the three claims and the collector's concerns. Also read Guille Tables S2 and S6 (not extracted) to resolve the 0.807 conflict, and the NeuSomatic SEQC2 paper (PMC8740374, not pinned in this batch) for what its checkpoint was trained on.
5. Ran an in-memory integration of the reviewed batch: `addBatch` against a scratch copy of the store (vocabularies, declared attributes and record validation pass; SHACL not run), then added the 15 proposed `assessed_by` links, pinned the judgements with `claimPins`, and ran `deriveUseCaseInputs`. All 15 new judgements and the existing Lancet judgement derive as `active`. Nothing was written to the store.

## Sources and hashes

| Source ID | Artifact checked | SHA-256 (re-downloaded 2026-10-09) | Matches record |
| --- | --- | --- | --- |
| `somatic-20261009-source-wang2020` | PMC7393490 full-text XML | `5f4e6b16675a3a6587f7999792ef479a059851ea8f7a31b4a954901aced5a8b1` | Yes |
| `somatic-20261009-source-wang2020-tables` | `41598_2020_69772_MOESM3_ESM.xlsx` from static-content.springer.com | `b9b5c68c7f78ff16863f64bb414394fd7b7dcd600795532aab30e39cd8d39c81` | Yes |
| `somatic-20261009-source-guille2025` | PMC11790059 full-text XML | `2c6fc6f329f7ebea34889de5f0cc8dff2d0d90b9a8dc3192ddac0949281c9827` | Yes |
| `somatic-20261009-source-guille2025-table-s7` | `tables7_bbae697.xls` in the Europe PMC zip | `735470fcb1ae7c3578ab3efefe12fde4b73bac279a1e7185950e5c2c0f1073f2` | Yes |
| `somatic-20261009-source-guille2025-supplementary-methods` | `supplementary_methods_bbae697.docx` in the same zip | `222509b8ec4b47b0278d6ea504291dba07a615c2fa23e3aaef600ea6aaf39709` | Yes |

The outer Guille zip hashed `2890fe7f...` this time (13,019,486 bytes, `testzip` clean); its member timestamps equal the request time, so as the collector noted its hash cannot be used to re-verify anything. `tables1_bbae697.xls` (`574501a3...`) and `tables6_bbae697.xls` (`2654481c...`) also match the hashes the collector recorded. Licences: both article XMLs carry CC BY 4.0.

## Values checked

| Source table | Results | Metrics | Mismatches |
| --- | --- | --- | --- |
| Wang Table S1 (`S1 WGS SNVs`), 8 datasets by 15 configurations | 480 | 120 each of count, recall, precision, F1 | 0 |
| Wang Table S2 (`S2 WGS INDELs`), 5 datasets by 12 configurations | 240 | 60 each of count, recall, precision, F1 | 0 |
| Guille Table S7, 18 SNV rows and 15 indel rows | 198 | 33 each of TP, FP, TPR, FPR, F1, PPV | 0 |
| Total | 918 | | 0 |

Truth counts in Wang column B equal article Table 1 for all 13 dataset and variant-type pairs, and equal each protocol's `denominator`. Guille `P` is 1,160 or 50 on every row and equals the protocol `denominator` and Table 2. Caller versions on all 41 configurations match Wang Methods ("Somatic variant calling") and Guille Table 1. Evaluation `origin` is `independent_paper` for every individual caller and `author_reported` for every ensemble row (Wang majority votes; Guille rows with a vote count). The FPR denominator is not defined in Guille; FP/FPR gives about 150.6 million on every row, consistent with a per-base rate over the evaluated regions, which supports leaving it in `missing_metadata`.

The only representational difference: for integer counts in Table S7, `raw_xml_value` holds `978` where my reader gives the double `978.0`. The values are equal; nothing was changed.

Consistency with the article prose (not recorded as results): Wang Results give NeuSomatic_Pass 0.859 on DREAM set 4 SNVs, and MuTect2 0.855, NeuSomatic_Pass 0.853 and majority vote 0.846 on DREAM set 4 indels; all match Tables S1 and S2. Guille Results 'Validation' give 0.880, 0.875, 0.752 and 0.745 for the four ensembles; all match Table S7.

## Corrections made in the batch

None changes a number, ID, link, source list, locator of a result, or comparison field. The batch is not in the store, so fields were edited in place. The collector's copy has SHA-256 `6144688a20bbe61d5dd9342088858046b36242f228e81894940420af98eb695d`. The reviewed `batch.jsonl` has SHA-256 `4053e239d8ad7866857f5332fb5e39415a48246a7aa77bcb927e069522b30ec3`; `review.json` binds it and every other file in the folder.

1. Status: every record set from `needs_review` to `source_checked`. Results and the three descriptive claims got a `review` block naming this reviewer and method; the collector's note is kept and extended.
2. 18 method `description` fields gave facts not in either source (for example "built on DeepVariant", "localised colored de Bruijn graphs", "Markov substitution model"). They now give the algorithm type printed in Guille Table 1 and, for FreeBayes and Pindel, the Methods statement that they were used with tumour-normal filtering.
3. `somatic-20261009-data-guille2025-seqc2-fd-wes`: `split` now says the validation sample is a second WES replicate of the same HCC1395 pair, scored against the same truth set as the development sample SRR7890883 (Table 2 row 'SEQC2'). `accession` now reads "SRA run SRR7890879 (Methods), in experiment SRX4728489 (Table 2)".
4. All 15 protocol `limitations` were rewritten (listed under Judgements). Guille: same cell line as development; DeepSomatic and NeuSomatic not held out; the prose comparison covers classic callers only. Wang: DREAM wording taken from the source ("configured mutations generated by a read simulator", not "spiked into real reads"), cellularity and subclonality per set, no true variants below 10% VAF in sets 1 to 3, CLL and MB truth lacks variants below 2% VAF, AML truth is a validated "platinum" list, COLO829 is a cell line.
5. `somatic-20261009-claim-guille2025-neusomatic-checkpoint`: name was "training_overlap: ..." while the field is `checkpoint`; renamed "checkpoint: NeuSomatic configuration (Guille et al. 2025)".
6. `somatic-20261009-claim-wang2020-neusomatic-dream3-model`: added the authors' statement that the model was "trained by the DREAM set3" (Results 'Evaluation of our consensus approach' paragraph 2) to `value` and `source_locator`; `claims.csv` updated to match.
7. Judgements: limitations, rationale, constraints, stratum labels, Guille and Wang citation locators, `excluded_evaluations`, `reviewed_evaluations` and `review` (see Judgements).

## Claims

| Record | Check | Outcome |
| --- | --- | --- |
| `somatic-20261009-claim-guille2025-deepsomatic-model-type` | DOCX '#DeepSomatic': `run_deepsomatic --model_type=WGS`; Table S7 A17 and A32: `DeepSomatic-WES` | Correct |
| `somatic-20261009-claim-guille2025-neusomatic-checkpoint` | DOCX '#NeuSomatic': `--checkpoint .../NeuSomatic_v0.1.4_standalone_SEQC-WGS-GT50-SpikeWGS10.pth` | Correct; name corrected |
| `somatic-20261009-claim-wang2020-neusomatic-dream3-model` | Methods paragraph 2 names `NeuSomatic_v0.1.3_ensemble_DREAM3.pth`; Results say the model was "trained by the DREAM set3" | Correct; authors' statement added |

## Collector concerns: decisions

1. **Guille prose versus S7 on ensembles against DeepSomatic.** Not a conflict. The stated gains are differences in F1 points against the best classic caller: 0.880 minus Mutect 0.853 is 2.7, and 0.752 minus Mutect2 0.650 is 10.2. Methods 'Ensemble approach' and Results 'Evaluation of the ensemble approach' exclude the three deep-learning and two commercial callers from the ensemble comparison, so "the best individual tool" means the best of the classic callers. VarNet's indel F1 (0.659) is also above Mutect2's, which fits the same reading. Recorded as a limitation on both Guille judgements. No evidence concern.
2. **DeepSomatic indel F1, 0.807 in prose versus 0.564 in S6.** The prose matches Table S2: the mean of the three dedup+BQSR DeepSomatic indel F1 values (NGV3 0.853, SEQC2 0.869, PERMED-01 0.698) is 0.807. Table S6 prints 0.5643 (C32), and its DeepSomatic SNV mean (0.789) is also lower than the prose implies. The NeuSomatic indel mean in S6 (0.831) does match S2 and the prose, so S6 is the odd one for DeepSomatic. Neither table is extracted and no stored value depends on them. No evidence concern; noted here for anyone who later extracts Tables S1, S2 or S6.
3. **DeepSomatic "-WES" label versus `--model_type=WGS`.** Confirmed. It is unresolved which model produced the rows. It no longer matters for the comparison because the DeepSomatic rows are excluded for training overlap (next item). The claim and the configuration's `model_identity_note` stay.
4. **Training leakage.**
   - Wang, NeuSomatic on DREAM set 3: confirmed by the authors, who say the model was "trained by the DREAM set3" and that this explains its DREAM set 4 result. The four NeuSomatic evaluations on DREAM set 3 (SNV and indel, Pass and Lowqual) are excluded from those two judgements. On DREAM set 4 the rows stay, with a limitation that the model was trained on a set from the same simulator.
   - Guille, NeuSomatic: confirmed. The checkpoint `SEQC-WGS-GT50-SpikeWGS10` was trained on HCC1395 ground-truth mutations in 50% of the genome (NeuSomatic SEQC2 paper, PMC8740374, Results; not pinned here), and Guille scored the whole exome target against the same HCC1395 truth. Excluded from both Guille judgements.
   - Guille, DeepSomatic: not raised by the collector. Guille Discussion paragraph 5 says "DeepSomatic used WES from the SEQC2 consortium to build his WES pre-trained model". The validation sample is a SEQC2 HCC1395 WES replicate. Excluded from both Guille judgements. This removes the best printed rows (SNV F1 0.901, indel F1 0.812), which the collector's summary led with.
   - Guille ensembles: the ensembles were chosen on development data that include another WES replicate of the same HCC1395 pair with the same truth set (Table 2 rows 'SEQC2' and 'SEQC2-FD'). This favours the ensembles but is not training on the test labels in the same sense, and the authors present the ensembles as their own method. Kept, with a limitation and a constraint.
5. **Incomplete truth sets on Wang's real tumours.** Confirmed: Results 'Datasets for evaluation' say completeness is unclear, especially at low VAF; Discussion paragraph 5 says CLL and MB truth sets exclude calls below 2% VAF; the AML truth is a validated "platinum" list. Calls absent from the truth set count as false positives, so precision on these pairs is a lower bound. Recorded in each limitation. No evidence concern: this is a property of the benchmark, stated by the authors, not a conflict in the source.
6. **Guille Table 2 versus Methods accession and platform.** Not a conflict. ENA run metadata (checked 2026-10-09, not a pinned source) list SRR7890879 as a run in experiment SRX4728489, Illumina HiSeq 4000. "Different platform (Fudan University)" refers to the sequencing site. The dataset `accession` text was clarified.

## Conflicts found

- **Wang Table S1 row 111 (COLO829, VarDict standalone).** Count 63,263, recall 0.806, precision 0.558, F1 0.660, truth 35,543. Recall gives about 28,650 true positives; precision times count gives about 35,300. Every other row in S1 and S2 agrees to within rounding (the next largest gaps are rows with precision of 0.004 to 0.008, where three-decimal rounding explains them). F1 agrees with the printed precision and recall, so the count is the more likely error, but the source does not show which value is wrong. The evaluation `somatic-20261009-eval-wang2020-vardict-standalone-colo829-snv` is excluded from the COLO829 SNV judgement with this reason; its results are kept as transcribed with a note. VarDict (bcbio), the configuration the authors use in Results, is shown.
- Guille Table S6 versus prose for DeepSomatic indel F1 (concern 2 above).

## Judgements

The question is "Which calling or rescoring workflow reliably detects tumour SNVs and small indels under the available sequencing and normal-sample regime?" Every protocol measures per-caller precision, recall and F1 for somatic SNVs or indels from tumour and matched-normal reads, which is the use case's input and endpoint, so all 15 are `direct`. The DREAM sets are synthetic tumours, but the input type (tumour-normal reads) and the endpoint are the ones the use case describes; the existing reviewed Lancet virtual-tumour judgement is also `direct`. The synthetic origin limits how far the values transfer, which is what limitations are for, and the stratum labels now show it on the page.

Grouping, strata order and headline metric hold: `wang2020-wgs-snv` (8 strata) and `wang2020-wgs-indel` (5 strata) in table order, `guille2025-seqc2-fd-wes` (SNVs, then indels), headline `f1-score`. Stratum labels changed: "Snvs" to "SNVs"; Wang strata now name the kind of sample, for example "DREAM set 1 (synthetic)", "CLL (tumour)", "COLO829 (cell line)".

| Judgement (`use-case-mapping-somatic-20261009-`) | Evaluations | Reviewed | Excluded | Decision |
| --- | --- | --- | --- | --- |
| `guille2025-seqc2-fd-wes-snv` | 18 | 16 | DeepSomatic, NeuSomatic (training overlap) | Holds |
| `guille2025-seqc2-fd-wes-indel` | 15 | 13 | DeepSomatic, NeuSomatic (training overlap) | Holds |
| `wang2020-dream-set1-snv` | 15 | 15 | | Holds |
| `wang2020-dream-set2-snv` | 15 | 15 | | Holds |
| `wang2020-dream-set3-snv` | 15 | 13 | NeuSomatic_Pass, NeuSomatic_Lowqual (trained on this set) | Holds |
| `wang2020-dream-set4-snv` | 15 | 15 | | Holds; NeuSomatic limitation |
| `wang2020-cll-snv` | 15 | 15 | | Holds |
| `wang2020-aml-snv` | 15 | 15 | | Holds |
| `wang2020-mb-snv` | 15 | 15 | | Holds |
| `wang2020-colo829-snv` | 15 | 14 | VarDict (standalone) (inconsistent row) | Holds |
| `wang2020-dream-set3-indel` | 12 | 10 | NeuSomatic_Pass, NeuSomatic_Lowqual (trained on this set) | Holds |
| `wang2020-dream-set4-indel` | 12 | 12 | | Holds; NeuSomatic limitation |
| `wang2020-cll-indel` | 12 | 12 | | Holds |
| `wang2020-mb-indel` | 12 | 12 | | Holds |
| `wang2020-colo829-indel` | 12 | 12 | | Holds |

Limitations now on each judgement (and its protocol):

- Guille SNV and indel: single WES sample, no intervals; truth limited to high-confidence exome regions (1,160 SNVs; 50 indels, so one variant moves recall by 0.02); ensembles chosen on development data that include the same cell line and truth set; post-alignment procedure for Table S7 not stated; DeepSomatic and NeuSomatic models built with SEQC2 HCC1395 data; the prose "best individual tool" comparison covers classic callers only.
- Wang DREAM sets: single pair, no intervals; synthetic tumour from a read simulator; cellularity and subclonality of the set; sets 1 to 3 have no true variant below 10% VAF; set 3 NeuSomatic excluded; set 4 NeuSomatic model trained on a set from the same simulator; caller versions as in Methods.
- Wang CLL, AML, MB, COLO829: single pair, no intervals; truth completeness unclear, precision a lower bound; CLL and MB truth lacks variants below 2% VAF; AML truth is a validated platinum list; COLO829 is a cell line; COLO829 SNV VarDict standalone excluded; caller versions as in Methods.

The judgement `review` follows the reviewed CNV judgements: method `source-hash-verification`, `independent-cell-check`, `ai-assisted-source-review`; reviewer `claude`; `reviewed_at` 2026-10-09T20:30:00Z. `pins` are not set; run `npm run use-cases:repin -- docs/reviews/use-cases/tumour-dna-somatic-variant-detection-2026-10-09.md <claim-id>...` for the 15 claims after `records -- add` and the use-case link change.

## Use-case changes (`coverage.json` `use_case_changes`)

Apply:

- The 15 `assessed_by` links, the five `source_ids` and the two `citation_locators`. These do not withhold the Lancet judgement (confirmed in the dry run).
- `evidence_gaps_add`, all six. Prefix the two kept Lancet-specific gaps with "Lancet paper:" as the collector suggests. The foundation-model gap still holds.
- `exclusions`: drop "Real clinical tumour specimens" from the first exclusion, as proposed. Replace the second exclusion, which now reads as if only Lancet and Strelka2 are covered, with: "Lancet paper: its Strelka, MuTect, MuTect2 and LoFreq rows are not ingested; the unselected LoFreq and MuTect2 rows are internally inconsistent in the source." Also add: "Callers evaluated only with a pre-trained model built from the test cell line or simulator (excluded from the affected judgements)."
- `setting`: apply the proposal with one change, so it does not call the Guille sample held out without qualification: "Published tumour-normal comparisons: a real-read virtual-tumour spike-in (Lancet paper, 80x/40x WGS), four simulated DREAM WGS pairs and four real tumour or cell-line WGS pairs with curated truth sets (Wang et al. 2020), and a validation WES replicate of the SEQC2 HCC1395 cell line (Guille et al. 2025), each measuring per-caller SNV and indel precision, recall and F1."
- `decision`: apply as proposed.
- `clinical_scope` (not proposed by the collector, but its text now describes only the synthetic Lancet test): "Clinical applicability is not established. The linked studies score callers on synthetic tumours, cell lines and research tumour samples against research truth sets; they do not validate any caller for clinical use, FFPE specimens, gene panels or ctDNA, or for copy-number or structural variants."

Changing `exclusions`, `setting`, `decision` or `clinical_scope` changes fields pinned by `use-case-mapping-amp-20261007-issue10-lancet-virtual-tumor`, which is then withheld until re-pinned, and the release workflow refuses a release that withholds a judgement the previous release served. I re-read that judgement against the proposed text: its endpoint, relevance (`direct`), limitations and evaluations are unaffected, and its own limitations already exclude clinical tumours. It still holds. Apply all text changes in the same change as the new judgements and re-pin the Lancet claim by name with this review: `npm run use-cases:repin -- docs/reviews/use-cases/tumour-dna-somatic-variant-detection-2026-10-09.md use-case-mapping-amp-20261007-issue10-lancet-virtual-tumor`.

## Evidence summary (corrected)

Replace the collector's `summary_proposal`. Its main finding (DeepSomatic best on the SEQC2 sample) rests on rows that are not held out.

> Three studies are linked, and their values cannot be pooled: truth sets, sequencing, caller versions and scoring scripts differ. Values are rounded to two decimals. In the Lancet developers' own virtual-tumour test, Lancet and Strelka2 both reached SNV F1 0.85, with indel F1 0.81 and 0.77. Wang et al. 2020 ran eight callers, NeuSomatic and their own majority-vote ensembles on eight whole-genome tumour-normal pairs, with older caller versions (for example MuTect2 from GATK 3.7). An ensemble had the highest SNV F1 on seven of the eight pairs; on DREAM set 4, NeuSomatic, whose model was trained on DREAM set 3, was highest at 0.86. The best single configuration reached SNV F1 0.92 to 0.96 on the simulated DREAM sets 1 to 3 but 0.70 to 0.81 on the CLL, AML and MB tumours, where most callers had precision below 0.6 against curated truth sets that the authors say may be incomplete, so precision there is a lower bound. Indel F1 on the CLL and MB tumours and the COLO829 cell line (AML has no indel truth set) was at most 0.72 for every configuration. Guille et al. 2025, who did not develop the callers, scored them on a WES replicate of the SEQC2 HCC1395 cell line (1,160 truth SNVs, 50 truth indels); another replicate with the same truth set was used to choose their ensembles. Leaving out DeepSomatic and NeuSomatic, whose pre-trained models were built with HCC1395 data, the best single caller reached SNV F1 0.85 (Mutect) and indel F1 0.66 (VarNet), and the authors' ensembles reached 0.88 for SNVs and 0.75 and 0.74 for indels. Strelka reached SNV F1 0.64 there, with precision 0.51, against 0.85 for Strelka2 in the Lancet test, which shows how much results depend on the study. None of the linked studies reports interval estimates or covers FFPE tissue, ctDNA, tumour-only calling or targeted panels, and none establishes clinical performance.

`source_ids`: `amp-oncology-rna-20261007-source-pmc6123722`, `somatic-20261009-source-wang2020`, `somatic-20261009-source-wang2020-tables`, `somatic-20261009-source-guille2025`, `somatic-20261009-source-guille2025-table-s7`, `somatic-20261009-source-guille2025-supplementary-methods`. The articles are needed for the training-overlap, truth-completeness and ensemble-selection statements.

| Statement | Record | Printed |
| --- | --- | --- |
| Lancet SNV F1 0.85 | `amp-oncology-rna-20261007-issue-10-result-lancet-snv-f1-score` | 0.85 |
| Strelka2 SNV F1 0.85 | `amp-oncology-rna-20261007-issue-10-result-strelka2-snv-f1-score` | 0.85 |
| Lancet indel F1 0.81 | `amp-oncology-rna-20261007-issue-10-result-lancet-indel-f1-score` | 0.81 |
| Strelka2 indel F1 0.77 | `amp-oncology-rna-20261007-issue-10-result-strelka2-indel-f1-score` | 0.77 |
| MuTect2 from GATK 3.7 | `somatic-20261009-config-wang2020-mutect2-gatk3-7` (`version`) | GATK v3.7-0 |
| DREAM set 4 SNV, NeuSomatic 0.86 | `somatic-20261009-result-wang2020-neusomatic-pass-dream-set4-snv-f1-score` | 0.859 |
| NeuSomatic model trained on DREAM set 3 | `somatic-20261009-claim-wang2020-neusomatic-dream3-model` | |
| DREAM set 1 best single, 0.96 | `somatic-20261009-result-wang2020-lofreq-dream-set1-snv-f1-score` | 0.963 |
| DREAM set 2 best single, 0.96 | `somatic-20261009-result-wang2020-lofreq-dream-set2-snv-f1-score` | 0.96 |
| DREAM set 3 best single, 0.92 | `somatic-20261009-result-wang2020-muse-dream-set3-snv-f1-score` | 0.918 |
| CLL best single, 0.70 | `somatic-20261009-result-wang2020-lofreq-cll-snv-f1-score` | 0.702 |
| AML best single, 0.80 | `somatic-20261009-result-wang2020-neusomatic-pass-aml-snv-f1-score` | 0.799 |
| MB best single, 0.81 | `somatic-20261009-result-wang2020-muse-mb-snv-f1-score` | 0.806 |
| Indel F1 at most 0.72 (CLL, MB, COLO829) | `somatic-20261009-result-wang2020-vote-5callers-min3-mb-indel-f1-score` (maximum) | 0.716894977169 |
| Truth 1,160 SNVs and 50 indels | `somatic-20261009-protocol-guille2025-seqc2-fd-wes-snv`, `-indel` (`denominator`) | 1160, 50 |
| Mutect SNV F1 0.85 | `somatic-20261009-result-guille2025-mutect-seqc2-fd-wes-snv-f1-score` | 0.853085210577865 |
| VarNet indel F1 0.66 | `somatic-20261009-result-guille2025-varnet-seqc2-fd-wes-indel-f1-score` | 0.658823529411765 |
| Ensemble SNV F1 0.88 (6 callers) | `somatic-20261009-result-guille2025-vote-6snv-min3-seqc2-fd-wes-snv-f1-score` | 0.880514705882353 |
| Ensemble SNV F1 0.88 (3 callers) | `somatic-20261009-result-guille2025-vote-3snv-min2-seqc2-fd-wes-snv-f1-score` | 0.875281404772625 |
| Ensemble indel F1 0.75 | `somatic-20261009-result-guille2025-vote-4indel-min2-seqc2-fd-wes-indel-f1-score` | 0.752475247524752 |
| Ensemble indel F1 0.74 | `somatic-20261009-result-guille2025-vote-3indel-min2-seqc2-fd-wes-indel-f1-score` | 0.74468085106383 |
| Strelka SNV F1 0.64 | `somatic-20261009-result-guille2025-strelka-seqc2-fd-wes-snv-f1-score` | 0.639486356340289 |
| Strelka SNV precision 0.51 | `somatic-20261009-result-guille2025-strelka-seqc2-fd-wes-snv-precision` | 0.509462915601023 |

Counts over linked results: an ensemble has the highest SNV F1 on DREAM sets 1 to 3, CLL, AML, MB and COLO829 (7 of 8). Single-configuration precision below 0.6: 10 of 11 on CLL, 7 of 11 on AML, 9 of 11 on MB. Single callers on Guille SNVs after exclusion: Mutect 0.853 is highest, then Lofreq 0.847, VarNet 0.840, Muse 0.840; on indels VarNet 0.659, then Mutect2 0.650.

## Test edit

`tests/omics-data.test.ts` changes the scope-audit length from 106 to 112 to match the six new `scope-audit.jsonl` lines, which is correct for this branch alone. Three other collectors are adding scope rows in parallel, so an exact count will conflict on every merge. Better: assert `scope.length >= 106` and that `paper_id` values are unique, as the ledger check already uses a lower bound. The test's intent (every row has a reason and a valid decision) is kept by the existing `every` check.

## Checks run

`npm test` passed (46 files, 499 tests) and `npm run typecheck` passed, on the worktree with the reviewed batch. The batch is not yet in the store, so these tests do not read it; the scratch `addBatch` and `deriveUseCaseInputs` dry run above is the check that covers it. `npm run build` was not run, by instruction (disk). SHACL shapes were not run.

## Remaining gaps

- The NeuSomatic SEQC2 paper and ENA metadata were read to resolve two concerns but are not pinned sources in this batch.
- Figures were not checked.
- Not extracted (collector's gaps, unchanged): Guille Tables S1 to S6, Wang Tables S3 to S9, NeuSomatic SEQC2 Additional file 2, Xiao et al. 2021, HG008, tumour-only, FFPE, ctDNA, targeted panels, long-read callers.
- The Guille Table S7 post-alignment procedure is not stated; the development tables show it changes F1 by more than 0.5 for some callers (for example NeuSomatic SEQC2 indels 0.809 with dedup+BQSR versus 0.260 with no post-processing, Table S2 row 29).
