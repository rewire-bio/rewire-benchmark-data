# CNV detection and characterisation: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-cnv-20261009/` (598 records). Use case: `use-case-cnv-detection-characterisation`.

Reviewer: a separate Claude review agent that did not extract the batch. No human review is claimed. Nothing was executed or reproduced; this is a check of transcription against the pinned sources.

## Outcome

- All seven new source artifacts and the reused DRAGEN supplement re-download to the pinned SHA-256. The archived `artifacts/*.gz` decompress to the same bytes.
- All 488 results match their source cells. No numerical value, printed value, metric, qualifier, unit, direction, configuration or protocol link was wrong.
- 59 descriptive fields were corrected (listed below). None changes a number.
- One comparability problem in the 1-5 kb group was found and then resolved by a post-review alignment edit, which this reviewer re-checked (see 1-5 kb comparison group).
- Every result and claim now has status `source_checked` and a `review` block.

## How the check was done

1. Downloaded each `artifact_url` into an empty directory, unpacked the Europe PMC zips and the inner zips, and hashed the named inner file.
2. Read each table with a stdlib OOXML reader written for this review (shared strings and raw `<v>` text). The extractor's `extract/*.py` was not imported or run. De La Vega Table 1 was read from `table-wrap id="vbaf071-T1"` in the article XML.
3. Built the expected identity of every cell from the table headers (tool row label, length bin, DEL/DUP group, metric column) and mapped it to the expected configuration and protocol. Then matched every result to its cell through `source_locator` and compared: `source_cell_text` to the raw cell text; `printed_value` to the shortest round-trip decimal of the stored double; `numeric_value`; metric, qualifier, unit, direction; the linked evaluation's configuration and protocol; and `scoring_conditions` against the TP/FP/FN (and N_truth, N_DEL, N_DUP) cells of the same row. For Gabrielaite, precision and recall were also recomputed from TP, FP and FN.
4. Checked that every expected cell has exactly one result: 488 expected, 488 matched, none missing, none duplicated. DRAGEN cell H6 is excluded because it is already stored as `amp-result-dragen-cnv-sv-1-5kb-fscore`.
5. Read the Methods, Results and Discussion of the three extracted articles to check configuration versions, dataset and protocol descriptions, `null` and `missing_metadata` reasons, the three claims and the two Nardone evidence concerns.

## Sources and hashes

| Source ID | Artifact checked | SHA-256 (re-downloaded 2026-10-09) | Matches record |
| --- | --- | --- | --- |
| `cnv-20261009-source-delavega2025` | PMC12005901 full-text XML | `ed6492f89d77454416d4fb135bb56bdcd5fb202e8a0ba94b92fa450441b4091f` | Yes |
| `cnv-20261009-source-delavega2025-table-s3` | `Supplemental_Table_3.xlsx` in `vbaf071_supplementary_data.zip` | `d900a69ec00915f1eb62dcf6b1ece0240cd4ba7937000652a6423fb813420bde` | Yes |
| `cnv-20261009-source-gabrielaite2021` | PMC8699073 full-text XML | `d8e954e141a06601b11b986338e45b57a3d5a98ac9e85411895b0ca1249b790f` | Yes |
| `cnv-20261009-source-gabrielaite2021-table-s2` | `Supplementary Materials/Table S2.xlsx` in `cancers-13-06283-s001.zip` | `eb4bb389b248508531ca371ba80e004a573f4e85029583cff336f217307fde85` | Yes |
| `cnv-20261009-source-nardone2025` | PMC12383524 full-text XML | `45317b1396f900fd8bcbe6e95519a4b475fda4c5ee416c63752811b71e154eb8` | Yes |
| `cnv-20261009-source-nardone2025-table-s1` | `TableS1.xlsx` in `biomedicines-13-01949-s001.zip` | `1e84dde9132aa977c069e3ce50132247a83969316cbd7c98f238ac54db032b14` | Yes |
| `cnv-20261009-source-seqc2-somatic-cnv-2024` | PMC11188507 full-text XML | `944529ff7c2859bf04e5a95bd139eb2faffe444dc754d0f0736b648b706c8f6b` | Yes |
| `amp-source-dragen-supplementary-tables` (stored) | MOESM3 XLSX from the recorded Springer `artifact_url` | `c8d66e8373f22382f1c5e4a576d2c85825a18232a14767d239966bc8ab56c3d9` | Yes, equals `original_artifact_sha256` |

The inner publisher zips also match the recorded `container_sha256` values (`82318e5f...`, `0fd70cca...`, `678880a4...`). The outer Europe PMC `supplementaryFiles` zips did not: they are assembled per request (member timestamps equal the request time), so their hashes change on every download (this run: De La Vega `b1c48819...`, Gabrielaite `fa0e131a...`, Nardone `57904828...`). This is not a problem with the pinned artifacts, but the `europepmc_supplementary_zip` hashes cannot be used to re-verify anything. The first De La Vega supplement request returned HTTP 500; the retry succeeded.

All seven `artifacts/*.gz` files decompress to the artifact hashes above, and their gzip hashes equal those listed in `sources.md`.

## Values checked

| Source table | Results | Metrics | Text cells (numeric_value null) | Mismatches |
| --- | --- | --- | --- | --- |
| DRAGEN supplement, sheet `S4 CNV benchmarking` (B6:L10, excluding H6) | 44 | 15 recall, 15 precision, 14 F-score | 2 (`NaN` in D6, D7) | 0 |
| De La Vega Supplemental Table 3 (B6:W13) | 176 | 88 sensitivity (recall), 88 precision | 24 (`NA`) | 0 |
| De La Vega Table 1, article XML | 12 | 12 precision (percent) | 0 | 0 |
| Gabrielaite Table S2, 8 `GB-WGS-NA12878` WGS rows, columns K and L | 16 | 8 precision, 8 recall | 0 | 0 |
| Nardone Table S1 (G5:I84) | 240 | 80 precision, 80 recall, 80 F1 | 7 (`NA`) | 0 |
| Total | 488 | | 33 | 0 |

`scoring_conditions` were checked on all 256 results that carry them (240 Nardone, 16 Gabrielaite): no mismatch. Gabrielaite precision and recall recompute exactly from TP, FP and FN, and `TP_FN` equals `N_truth` (2,076) on every row.

Consistency checks against the article prose (not recorded as results): De La Vega Results 3.1 combined and duplication figures (DRAGEN HS 83% and 30%, Cue 76% and 33%, Delly 77%, HS-F 75%, DRAGEN HS duplication sensitivity 47%, Cue duplication precision 50%) agree with Table S3 to rounding. Nardone Results 3.1 values for DRAGEN v4.2, DRAGEN v4.0 and Manta (all deletions) and for inGAP and DELLY at 1000-4999 bp agree with Table S1. Gabrielaite's "maximum precision of 66.7%" is CLC (0.6667).

## Corrections made in the batch

None of these changes a number. The batch is not yet in the store, so the fields were edited in place; previous values are kept here.

1. Seven Nardone `NA` results: `missing_metadata.value` said "Printed NA; table footnote: no TP data to calculate metric". Table S1 has no such footnote (its only text outside the grid is the A1 caption, and the article does not define NA). The note was copied from De La Vega Table S3, which does have it (A15). New value: "Printed NA; Table S1 has no note defining NA. The same row prints TP=0, which leaves this metric undefined." Records: `cnv-20261009-result-nardone2025-*` for cells I13, G61, I61, G62, I62, G63, I63.
2. 26 results had `uncertainty: null` with no `missing_metadata.uncertainty` reason (the 24 De La Vega `NA` cells and the 2 DRAGEN `NaN` cells). Added `"uncertainty": "Unreported"`, as on the other 455 results.
3. `cnv-20261009-protocol-nardone2025-hg002-del-wittyer`: `missing_metadata.wittyer_version` said "Unreported", but Methods 2.4 names "Witty.er v0.5.2". Removed that entry and changed `protocol` to name Witty.er v0.5.2 (Methods 2.4). `matching_parameters` stays unreported.
4. The 10 Nardone evaluations: `comparison.metric_implementation` changed from "witty.er (version unreported)" to "Witty.er v0.5.2 (Methods 2.4); matching parameters unreported".
5. The 10 Nardone evaluations: `comparison.population` was "5,414 truth deletions". Table S1 prints TP+FN = 4,159 for every caller, and the per-bin values sum to the ALL row, so 4,159 deletions were scored, not 5,414. New value states both numbers and that the article does not explain the difference. Added `missing_metadata.scored_truth_count` to `cnv-20261009-data-nardone2025-hg002-giab-sv06-tier1-del-hg38` with the same facts.
6. `cnv-20261009-config-nardone2025-dragen-4-0`: added `version_note`. Methods 2.2, Table 1 and Table S1 print DRAGEN v4.0, but Discussion paragraph 2 lists "DRAGEN v4.1". v4.0 is kept.
7. `cnv-20261009-claim-na12878-truth-built-with-manta-cnvnator`: `source_locator` changed from "Results 3.7 paragraph 3" to "Results 3.7 paragraph 4; Discussion paragraph 3". Paragraph 3 of Results 3.7 is about WES call counts. `claims.csv` was updated to match.
8. Added an `evidence_concerns` entry to `cnv-20261009-source-delavega2025` (see Conflicts).

## Claims and evidence concerns

| Record | Check | Outcome |
| --- | --- | --- |
| `cnv-20261009-claim-cue-lower-size-limit` | Results 3.1 paragraph 3 ("inability to detect events smaller than 5 kb, which was the lower limit of its training model") and paragraph 5 | Correct |
| `cnv-20261009-claim-dragen-hs-filters` | Methods 2.5: <500 bp and >10 Mb removed, junction-only (SVCLAIM=J) >1 Mb removed, centromere and telomere gap overlap removed, >=90% reciprocal overlap with recurrent artifacts removed, RTG vcffilter with custom JavaScript | Correct |
| `cnv-20261009-claim-na12878-truth-built-with-manta-cnvnator` | Statement is correct; locator was wrong | Locator corrected |
| Nardone Table S1 concern (depth and aligner) | Methods 2.2: 65x subsampled to 25x, bwa-mem2 "for preliminary evaluations"; Results 3.1: "previously aligned using the DRAGEN pipeline"; Data Availability: 30x Illumina 2x250 reads. Results 3.4 also says "25-30x" | Accurate. Agree it should block automatic comparison |
| Nardone article concern (inGAP 5000-9999 bp) | Prose: F1 97%, precision 92%, recall 94%. Table S1 row 17: precision 0.9714, recall 0.9231, F1 0.9466. F1 cannot exceed both precision and recall | Accurate. The prose looks like the three values were permuted and rounded, but that is a guess; table values are recorded |

## Points the extractor asked the reviewer to judge

1. De La Vega Table S3 rows 6 (`Dragen v4.2 HS + Filters`) and 8 (`Dragen v4.2`): confirmed identical in 17 of 22 cells; they differ in O, R, S, U and W. Many strata have few truth events (10 duplications in total), so identical values are possible, and the prose gives no figure for default DRAGEN to test against. I agree with transcribing as printed. I added a note to the review of every result in those two rows; I did not add an evidence concern because nothing in the source shows a row is wrong.
2. Delly v1.1.6 (Table S3) versus v1.6 (Methods 2.3): confirmed. Agree with recording both and not choosing.
3. Origin: the conflict-of-interest statement lists five Illumina employees, so `author_reported` for DRAGEN is right. The other callers are not developed by the authors; `independent_paper` is reasonable. Agree.
4. Nardone depth and aligner conflict: confirmed (see table above). Agree with `comparison.inputs` null. I found a second count problem in the same table (correction 5).
5. Nardone inGAP prose: confirmed. Agree.
6. DRAGEN S4 row 8 label `[10,000-20,0000)`: confirmed as printed in A8. Reading it as 10-20 kb by position between rows 7 and 9 is the only sensible reading. Agree.
7. Gabrielaite truth-set dependency: confirmed, with the locator corrected.

## Conflicts found

- De La Vega Results 3.1 paragraph 5 says CNVnator and Cue could not detect events of 1-5 kb. Table S3 prints CNVnator 1-5 kb deletion sensitivity 0.3098 and precision 0.4207 (B9, C9). Paragraph 3 says Delly had the lowest precision; Table S3 prints lower combined precision for Lumpy (W13 0.0107) than Delly (W11 0.1902). The prose may describe Figures 1 and 3, which were not checked. Recorded as an evidence concern on `cnv-20261009-source-delavega2025`; table values are kept.
- Nardone: 5,414 benchmark deletions in Methods 2.1, 4,159 scored in Table S1 (correction 5).
- Nardone: DRAGEN v4.0 versus v4.1 (correction 6).
- De La Vega: Delly version (extractor point 2).

## 1-5 kb comparison group (resolved after review)

The use-case mapping `use-case-mapping-amp-20261007-issue17` puts the stored `amp-eval-dragen-cnv-sv-1-5kb-fscore` (F-score 0.926) next to the new `cnv-20261009-eval-behera2024-cnvnator-1-5kb` and `cnv-20261009-eval-behera2024-dragen42-cnv-1-5kb`. `services/omics/src/catalogue-query.ts` only groups results with the same `metric_qualifier` and the same comparison strings. They differ:

| Field | Stored (`amp-...`) | New 1-5 kb evaluations and results |
| --- | --- | --- |
| result `metric_qualifier` | absent | `deletions, [1,000-5,000) bp` |
| `comparison.dataset_version` | `GIAB SV v0.6, GRCh37 reference for SV/CNV comparisons` | `GIAB SV v0.6, GRCh37` |
| `comparison.population` | `SingleHG002; [1000,5000)bp truth deletions, exact count unreported` | `HG002 35x; deletion truth in bin [1,000-5,000), count unreported` |
| `comparison.inputs` | `35× WGS; GRCh37 GIAB v0.6 deletion truth` | `35x WGS alignments` |

`metric_implementation` is null on all of them, so automatic comparison is blocked anyway, but if it is ever filled these differences will still split the panel. The new CNV+SV 1-5 kb precision and recall results also attach to the stored evaluation, whose name ends in "fscore". There are two valid fixes: align the batch's 1-5 kb records to the stored strings and drop their qualifier, or change the stored records through a reviewed record change. The choice is the lead's, so I left it.

Resolution, re-checked 2026-10-09: the lead chose the first option and edited 10 lines of `batch.jsonl`. A diff against the reviewed copy (SHA-256 `8a2ae65fd57f348b1a9a925b10985b4c342bcf0d7dab44cd1a1e9068a5339e07`) shows only these changes: `attributes.comparison` on `cnv-20261009-eval-behera2024-cnvnator-1-5kb` and `cnv-20261009-eval-behera2024-dragen42-cnv-1-5kb` now equals the stored `amp-eval-dragen-cnv-sv-1-5kb-fscore` comparison exactly, and the 8 new results on the three 1-5 kb evaluations no longer have `metric_qualifier`, with one sentence appended to each `review.notes`. No other field changed. All nine 1-5 kb results (8 new plus `amp-result-dragen-cnv-sv-1-5kb-fscore`) now share protocol `amp-protocol-hg002-cnv-1-5kb`, dataset `amp-data-hg002-giab-sv06-cnv`, identical comparison fields, no qualifier, unit `fraction` and direction `higher`. The independent cell check was re-run on the edited batch: 488 of 488 still match. The stored evaluation name ending in "fscore" is left as is.

## Remaining gaps

- Figures were not checked, so the De La Vega prose conflicts above are not resolved.
- SEQC2: only the article XML table captions and supplementary file list were checked. Additional file 1 was not reopened, so "per-caller accuracy is in figures only" rests on the extractor's reading.
- The DRAGEN article (`amp-source-dragen`) was not re-read, as in the extraction. The CNVnator version on `cnv-20261009-config-behera2024-cnvnator` stays unset.
- Gabrielaite cohort rows (GB-WGS-01 to 38) and WES rows were not extracted. I agree with the extractor's reason: they use SNP-array truth or exome input, and the selection is by sample and truth set, not by value.
- Not covered by the batch: long-read CNV callers, exome callers, somatic CNV with printed values, T2T-Q100 or CMRG truth, evidence-visualisation usability, the EJHG 2022 supplement, and Nardone Tables S2 to S5.

## Addendum: relation names after rebasing onto single-meaning relations

After this review, `main` renamed relationships across the store (`docs/reviews/2026-10-09-single-meaning-relations.md`). The reviewed `batch.jsonl` is unchanged. The store holds `batch.store.jsonl`, produced from it by `normalizeRecords` in `shared/omics/relations.ts`, the same function the store migration used. Only link relation names differ, in 79 records: evaluations use `system`, `assessment` and `data`; configurations `configuration_of`; protocols and the benchmark `uses_data`. No attribute, value or ID changed. The six active mapping fingerprints were recomputed against the rebuilt snapshot.

## Store form

Checked 2026-10-09 by the same review agent, after the branch was rebuilt on `main` with single-meaning relations (#50) and declared attributes (#54). The store now holds `batch.store.jsonl` (SHA-256 `2b57950eebf38140e49303be16fa5e699cda860bf9f5d9d0adf4b7f52bc8d662`), made from the reviewed `batch.jsonl` (unchanged, `ecedbef04be8d0ef324e5254066abd8e4b354ef1ec5cc37fe2df67ddcfd81446`) in the three steps listed in `store-form.md`. Steps 2 and 3 change attributes, so the addendum's statement above that no attribute changed no longer holds. The checks below are mine. I did not run `extract/registry_fit.py`; I compared its output.

- Steps 1 and 2 re-run: I called `normalizeRecords` and then `normalizeAttributes` (with the same store context and missing-reason table as `attributes:migrate -- --batch`) on `batch.jsonl`. Step 1 changes only link relation names in 79 records, each the name `currentRelation()` returns. Step 2 turns string missing reasons into `{reason, note}` objects, makes `review.reviewer` a list, renames `review.notes` to `review.note`, renames `foundation_model` to `foundation_model_eligible`, and drops redundant fields (`entity_level` on configurations, null `version`, null `uncertainty`, empty `missing_metadata`, and `published_score_reproduction: false`). The last is dropped store-wide as constant scaffolding; these evaluations still say "transcribed, not reproduced" in their description. Running both steps again on `batch.store.jsonl` gives identical bytes.
- Step 3: every difference between my step-2 output and `batch.store.jsonl` is a move listed in `store-form.md`, plus `source_cell_text` renamed to `raw_xml_value` on all 488 results and `pmcid` dropped on 4 sources. Nothing else differs, including top-level fields and links.
- Protected fields: between `batch.jsonl` and `batch.store.jsonl`, no ID, kind, source list, link target, `printed_value`, `numeric_value`, metric, qualifier, unit, direction, `scoring_conditions`, evaluation `comparison`, claim field, value or locator, source hash, URL, version or evidence concern changed. `raw_xml_value` equals the old `source_cell_text` on every result.
- Text kept: every string in each reviewed record appears verbatim in its store record, except relation names (renamed), the four `pmcid` values (each is in that source's `version` and `artifact_url`), bare "Unreported" reasons now coded as `reason: unreported`, and one note. Some moves add wording: `hash_scope` explains that the Europe PMC zip hash covers one retrieval only (consistent with the outer-zip finding above); the Nardone protocol's `metric_implementation` note names Witty.er v0.5.2 (Methods 2.4); the Behera dataset's `scope_note` names `amp-data-hg002-giab-sv06-cnv`; and the Nardone depth and aligner reasons (the dataset's `population_detail` and the 10 evaluations' `comparison.inputs`) are now `conflicting` instead of `unreported`, which matches the source.
- The note lost is on `cnv-20261009-config-delavega2025-delly`: step 2 drops `missing_metadata.version` ("Conflict: Table S3 row label 'Delly (v1.1.6)' versus Methods 2.3 'Delly v1.6'. Not resolved.") because `version` is not null. Both version strings survive in `version` ("Table S3 prints v1.1.6; Methods 2.3 prints v1.6"), so only the words "Not resolved" are gone. I did not change it. A `model_identity_note`, like the one on the Nardone DRAGEN v4.0 configuration, would restore it.
- Store: the 598 IDs each appear once in `data/entities/*.jsonl` or `data/evidence/*.jsonl`, and each stored line is byte-identical to its line in `batch.store.jsonl`. `npm run records -- check` passes (29,317 records match their provenance).
