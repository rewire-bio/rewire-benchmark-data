# Review verdict: somatic batches of the 2026-10-11 uc-oncology pass (reviewer-onc-1)

Reviewer: Claude (Opus 5.5) research agent acting as independent reviewer; I did not extract these batches. No human review claimed. Date 2026-10-11. Worktree `rewire-benchmark-data-lit-uc-oncology`, uncommitted files. I edited no records; every change below is for the collector to apply.

## Verdicts

| Batch | Verdict |
| --- | --- |
| `use-case-coverage-somatic-hg008-20261011` | Approved with corrections (H1 to H5) |
| `use-case-coverage-somatic-clairs-to-20261011` | Approved with corrections (C1 to C4; C5 optional) |
| `use-case-coverage-somatic-varnet-t-20261011` | Approved with corrections (V1 to V6) |
| `use-case-coverage-somatic-wes-synthetic-20261011` | Approved with corrections (W1 to W3) |

No stored number is wrong in any batch. All 749 results match their sources. The corrections are to relevance, limitations, locators and one missing uncertainty.

## Answers to the collector's questions

1. **Tumour-only scope.** Do not change the use case's `exclusions`, `inputs` or `setting`. Mark all 14 ClairS-TO and VarNet-T judgements `proxy` (C1, V1). The tumour-only evidence is two developer papers. That does not clearly justify a scope change that would withhold the 17 reviewed judgements until they are re-pinned. Only the non-pinned fields change: `evidence_gaps`, `assessed_by` links, `source_ids` and `citation_locators` (text below).
2. **Hasan 2026 quality.** `direct` is acceptable and no `evidence_concern` is needed. The inputs and endpoint match the use case, and the author developed none of the callers. The Zenodo tables are checksum-bound and agree with the manuscript. Every precision, recall and F1 recomputes from TP, FP and FN to within 5e-7. The preprint status, the author's company and the missing scoring code belong in the limitations; the scoring-code point is currently missing from the judgements (H4). DeepSomatic and HG008: the source does not say whether DeepSomatic 1.10.0's WGS model saw HG008. The DeepSomatic README, metrics page and WGS case study (github.com/google/deepsomatic, commit 09d605a966e5dcb10361cd036e05cb79d21b0062) do not list training samples. They name only HCC1395, with chr1 held out. This is unresolved and is recorded as a limitation (H4).
3. **Repository and Source Data values.** For VarNet-T the question does not arise. Supplementary Tables 1 and 4 have a text layer in the pinned PDF (physical pages 18 and 21, printed pages 17 and 20). I rendered both pages and read every cell. All 63 values are printed exactly as stored, so they are ordinary printed values. The locators and `printed_value_basis` must say so (V2). Dorney is not in my scope.
4. **Conflicts.** López-Cade FreeBayes: I confirm TP 1,908 + FN 2,314 = 4,222, and 1,908/4,222 = 0.4519. TP + FP equals Total Query in all three rows. Excluding FreeBayes from the judgement and keeping the limitation is right. A source `evidence_concern` would block the two consistent rows, which the abstract corroborates, so do not add one. VarNet-T DeepSom indel AUPRC: keep the values as printed. The limitation needs a citation (V5).
5. **Training overlap.** I agree with excluding DeepSomatic from the two VarNet-T SEQC2 judgements. ClairS-TO's omission of DeepSomatic on HCC1395 is the authors' choice and is recorded. Three further overlaps need limitations: VarNet-T's training cohort includes 38 gastric tumours, against two stomach PCAWG test samples; DeepSom's BLCA-US, GACA-CN and LAML models share cancer types with the bladder, stomach and AML test samples; and nobody states whether DeepSomatic 1.7.0 saw COLO829 (C2, V3, V4). Best-F1 thresholds chosen on test data are in every ClairS-TO qualifier and limitation, which is enough.
6. **Headline metrics and Clair3.** I accept the headline metrics: F1 for HG008 and ClairS-TO, AUPRC for VarNet-T, recall for López-Cade. Keep Clair3 in the ClairS-TO judgements. Its limitation already says it is a germline caller used as a naive baseline, and its distance from ClairS-TO (ONT COLO829 50x SNV F1 0.71 against 0.76 to 0.77) is useful to someone choosing a method.

## Corrections

### HG008 (`use-case-coverage-somatic-hg008-20261011`)

**H1. Missing uncertainty on the six all-region F1 results.** The manuscript Results print 95% block-bootstrap intervals for these F1 values (section "Sensitivity analyses show benchmark-context dependence without establishing population generalization", paragraph 2, citing Supplementary Table 2). The Zenodo `tables/TableS3_G9_all_region_bootstrap.tsv` agrees after rounding. In each result below, delete `missing_metadata.uncertainty` and add `uncertainty`:

```json
{"type": "confidence_interval", "lower": "<L>", "upper": "<U>", "level": 0.95, "method": "bootstrap_percentile", "resamples": 10000, "printed": "<L>–<U>", "source_column": "Manuscript Results, 'Sensitivity analyses show benchmark-context dependence without establishing population generalization', paragraph 2 (Supplementary Table 2)", "note": "Genomic block bootstrap over 5-Mb blocks, linear percentile interval; prespecified, but executed after the primary external evaluation; spatial variation within the benchmark region, not between tumours"}
```

| Result ID | L | U |
| --- | --- | --- |
| `somatic-hg008-20261011-result-mutect2-all-region-overall-f1-score` | 0.7854 | 0.7980 |
| `somatic-hg008-20261011-result-strelka2-all-region-overall-f1-score` | 0.6691 | 0.7205 |
| `somatic-hg008-20261011-result-deepsomatic-all-region-overall-f1-score` | 0.7689 | 0.7822 |
| `somatic-hg008-20261011-result-union-all-region-overall-f1-score` | 0.7018 | 0.7521 |
| `somatic-hg008-20261011-result-majority-all-region-overall-f1-score` | 0.7875 | 0.8003 |
| `somatic-hg008-20261011-result-strictintersection-all-region-overall-f1-score` | 0.7316 | 0.7456 |

(`printed` keeps the source's own en dash between the two bounds. That is a transcription, not prose.)

**H2.** In `somatic-hg008-20261011-protocol-all-region-overall` and `use-case-mapping-somatic-hg008-20261011-all-region-overall`, replace the limitation "Prespecified sensitivity region that includes variants near germline variants; no interval estimates are printed for it in Table 4 (Supplementary Table 2 holds a separate block bootstrap, not extracted)." with:

> Prespecified sensitivity region that includes variants near germline variants. Its 95% block-bootstrap F1 intervals are printed in the manuscript Results (Supplementary Table 2); that analysis was prespecified but executed after the primary external evaluation.

**H3.** Add this limitation to `somatic-hg008-20261011-protocol-primary-overall`, `-primary-snv` and `-primary-indel`, and to the matching claims `use-case-mapping-somatic-hg008-20261011-primary-overall`, `-primary-snv` and `-primary-indel`:

> The primary region (nogermlineinterference) holds 14,014 of the 18,207 truth variants in the full benchmark; the rest are sites with germline interference. Over the full benchmark (Table 4) overall F1 is 0.70 to 0.79 rather than 0.78 to 0.91, and in the germline-interference stratum DeepSomatic F1 is 0.0528 (Results).

**H4.** In all four protocols and all four claims of this batch:
- change "The authors do not establish" to "The author does not establish" (single author);
- add "The original scoring and bootstrap code was not retained; the author reports that a later internal reimplementation reproduced the numbers. No external replication.";
- add "Whether DeepSomatic 1.10.0's bundled WGS model was trained with HG008 data is stated neither in the source nor in the DeepSomatic README, metrics page and WGS case study (github.com/google/deepsomatic, commit 09d605a966e5dcb10361cd036e05cb79d21b0062, checked 2026-10-11); the DeepSomatic paper was not checked."

**H5.** In `coverage.json` `gaps`, change the first entry so that it no longer lists the all-region bootstrap as unextracted. Overall intervals are now recorded; the per-class all-region intervals in TableS3 are not.

### ClairS-TO (`use-case-coverage-somatic-clairs-to-20261011`)

**C1.** In all eight claims `use-case-mapping-somatic-clairs-to-20261011-{ont-colo829-snv, ont-colo829-indel, ont-hcc1395-snv, ont-hcc1395-indel, pacbio-colo829-snv, pacbio-colo829-indel, illumina-colo829-snv, illumina-colo829-indel}`, and in `coverage.json` `judgements`, set `relevance` to `proxy`. Replace `rationale` and the claim `description` with:

> Proxy, not direct: the endpoint matches (per-caller precision, recall and F1 on held-out cell lines with consortium truth sets), but the callers used tumour reads only, whereas this use case's inputs include a matched normal and its exclusions list tumour-only calling. Linked as the closest evidence for users without a matched normal.

Delete `coverage.json` `use_case_changes` keys `exclusions_replace`, `inputs_add` and `setting_append`, or mark them rejected. The same change applies to the copies in the other three batches' `coverage.json`.

**C2.** Add "Whether the DeepSomatic 1.7.0 models were trained with COLO829 data is not stated in the source." to the six COLO829 protocols (`somatic-clairs-to-20261011-protocol-{ont,pacbio,illumina}-colo829-{snv,indel}`) and their six claims.

**C3.** Add "Competing interests: the senior author (R.L.) receives research funding from ONT." to all eight protocols and all eight claims.

**C4.** Add this limitation to `somatic-clairs-to-20261011-protocol-illumina-colo829-snv` and `-indel` and to their two claims:

> TP + FN is not identical across callers (SNV 40,232, but 40,230 for Pisces; indel 715, but 714 for Mutect2 and 713 for Octopus), so the scored truth set differs slightly between rows; the source does not explain this.

**C5 (optional).** TP + FN is constant within each other protocol, so `denominator` could be set: ONT COLO829 SNV 37533, indel 585; ONT HCC1395 SNV 32212, indel 1356; PacBio COLO829 SNV 39086, indel 610. Note in each that it is TP + FN after the authors' truth filter. Leave the Illumina protocols without a denominator.

### VarNet-T (`use-case-coverage-somatic-varnet-t-20261011`)

**V1.** In all six claims `use-case-mapping-somatic-varnet-t-20261011-{seqc2-snv, seqc2-indel, colo829-snv, colo829-indel, pcawg-snv, low-tmb-snv}`, and in `coverage.json`, set `relevance` to `proxy`. Replace `rationale` and `description` with:

> Proxy, not direct: per-caller AUPRC on real tumour and cell-line WGS with tumour-normal-derived truth sets is close to the use case's endpoint, but the callers used tumour reads only, whereas this use case's inputs include a matched normal and its exclusions list tumour-only calling; precision, recall and F1 are not extracted. Linked as the closest evidence for users without a matched normal.

**V2. Tables 1 and 4 are printed text, not images.** In the 63 results whose `source_locator` contains "(table image; value from Source Data sheet": these are all of Supplementary Table 1 (36) and all of Table 4 (27).
- In `source_locator`, delete the parenthesis " (table image; value from Source Data sheet 'Supplementary Table N')". Example: "Supplementary Table 1, row 'ClairS-TO', column 'COLO829 INDEL'".
- Delete `printed_value_basis`.
- Set `review.artifact_sha256` to `c808b4361e17a64911a59ded81d9db04c7a3dd5ba95fb3e1e060a293182f2842`, set `review.retrieval_url` to the MOESM1 PDF URL, and set `review.method` to `pdf-text-parse`. The method note should say the values were parsed from the PDF text layer (physical pages 18 and 21) and cross-checked against the Source Data sheet.
- `printed_value` and `numeric_value` are already correct.
- Fix `retrieval-log.md` step 3, `research.md` and the first `coverage.json` gap, which say these tables have no text layer.

**V3. PCAWG training overlap.**
- In `somatic-varnet-t-20261011-data-pcawg`, replace `split` with: "Samples not used in VarNet-T training. The source says the five cancer types were not in the training cohorts, but the training cohort includes 38 gastric tumours and two test samples (DO38547, DO38423) are stomach adenocarcinomas."
- Add both of these limitations to `somatic-varnet-t-20261011-protocol-pcawg-snv` and `use-case-mapping-somatic-varnet-t-20261011-pcawg-snv`:
  - "The source says the PCAWG cancer types were not used in training (Results; Methods 'PCAWG benchmark samples'), but its training cohort includes 38 gastric tumours (Methods 'Training data'); VarNet-T is not held out at cancer-type level for the two stomach samples DO38547 and DO38423."
  - "DeepSom's BLCA-US and GACA-CN models were trained on ICGC projects of the same cancer types as the bladder (DO804, DO522) and stomach (DO38547, DO38423) test samples; the source does not say whether those donors were in DeepSom's training data."

**V4.** Add "DeepSom-LAML was trained on TCGA acute myeloid leukaemia data (Methods; Discussion); whether this AML sample is in its training data is not stated." to `somatic-varnet-t-20261011-protocol-low-tmb-snv` and its claim.

**V5.** In `somatic-varnet-t-20261011-protocol-seqc2-indel`, `-colo829-indel` and their claims, replace "DeepSom models score SNVs; the source prints indel AUPRC for them without explanation." with:

> DeepSom's developers describe it as a caller of somatic SNVs (github.com/sergeyvilov/DeepSom repository description, checked 2026-10-11; not a pinned source); this source prints indel AUPRC for its models without explanation.

**V6. Truth sets.**
- `somatic-varnet-t-20261011-data-colo829`: add `scope_note` "Truth: TGen multi-institution COLO829 reference set, about 35,000 SNVs (Results 'Benchmarking on somatic reference datasets', 'Challenges in tumor samples with low somatic mutation burden'). This is a different truth set and sequencing run from Chen et al. 2025 (NYGC truth, 42,993 SNVs before filtering)."
- `somatic-varnet-t-20261011-data-seqc2`: add `scope_note` "Truth: SEQC2 consortium reference call set in its high-confidence regions, about 39,000 SNVs."
- Add this limitation to `somatic-varnet-t-20261011-protocol-colo829-snv`, `-colo829-indel` and their claims: "COLO829 truth is the TGen reference set and the reads are EGA EGAD00001002142; Chen et al. 2025 used the NYGC truth set and other COLO829 sequencing, so COLO829 values from the two papers are not comparable (ClairS-TO Illumina SSRS v0.4.0 SNV AUPRC 0.6500 there, 0.270 here)."

### López-Cade (`use-case-coverage-somatic-wes-synthetic-20261011`)

**W1.** In `somatic-wes-synthetic-20261011-protocol-bamsurgeon-wes-snv` and `use-case-mapping-somatic-wes-synthetic-20261011-bamsurgeon-wes-snv`, replace "Callers run with nf-core/sarek defaults and no tuning; a custom panel of normals was not used (Discussion)." with:

> Callers run with nf-core/sarek 3.5.0 defaults and no tuning; no custom panel of normals was specified, and sarek's default GATK GRCh38 panel of normals was applied to Mutect2 (Discussion).

**W2.** `somatic-wes-synthetic-20261011-config-freebayes` `parameters` is wrong: the source does not say sarek filtered FreeBayes for somatic status. Replace with:

> nf-core/sarek 3.5.0 default parameters; FreeBayes has no PASS filter, so the authors kept calls with QUAL >= 1, SAF > 0, SAR > 0, RPL > 1 and RPR > 1 (Methods 'Variant Calling and Bioinformatic Workflow')

In `somatic-wes-synthetic-20261011-result-freebayes-bamsurgeon-wes-snv-total-query`, change `unit_detail` to "counted entity: filtered SNV calls" and `metric_qualifier` to "SNV only, synthetic WES, total filtered calls".

**W3.** In every record of this batch, replace the locator section name "Methods 'Variant Calling'" with "Methods 2.4 'Variant Calling and Bioinformatic Workflow'". Replace "'Synthetic Data Generation'" with "2.3 'Generation of Synthetic Data with Known Somatic SNVs'" where it appears.

## Approved summary for `use-case-tumour-dna-somatic-variant-detection`

Final approved text, verbatim. The middle is the existing summary unchanged, from "Values are rounded" through "92.4% to 90.9% for Strelka2."

> Eight studies are linked, and their values cannot be pooled: truth sets, sequencing, caller versions and scoring scripts differ. Values are rounded to two decimals, except where the source prints percentages. In the Lancet developers' own virtual-tumour test, Lancet and Strelka2 both reached SNV F1 0.85, with indel F1 0.81 and 0.77. Wang et al. 2020 ran eight callers, NeuSomatic and their own majority-vote ensembles on eight whole-genome tumour-normal pairs, with older caller versions (for example MuTect2 from GATK 3.7). An ensemble had the highest SNV F1 on seven of the eight pairs; on DREAM set 4, NeuSomatic, whose model was trained on DREAM set 3, was highest at 0.86. The best single configuration reached SNV F1 0.92 to 0.96 on the simulated DREAM sets 1 to 3 but 0.70 to 0.81 on the CLL, AML and MB tumours, where most callers had precision below 0.6 against curated truth sets that the authors say may be incomplete, so precision there is a lower bound. Indel F1 on the CLL and MB tumours and the COLO829 cell line (AML has no indel truth set) was at most 0.72 for every configuration. Guille et al. 2025, who did not develop the callers, scored them on a WES replicate of the SEQC2 HCC1395 cell line (1,160 truth SNVs, 50 truth indels); another replicate with the same truth set was used to choose their ensembles. Leaving out DeepSomatic and NeuSomatic, whose pre-trained models were built with HCC1395 data, the best single caller reached SNV F1 0.85 (Mutect) and indel F1 0.66 (VarNet), and the authors' ensembles reached 0.88 for SNVs and 0.75 and 0.74 for indels. Strelka reached SNV F1 0.64 there, with precision 0.51, against 0.85 for Strelka2 in the Lancet test, which shows how much results depend on the study. Sahraeian et al. 2022, the NeuSomatic developers, scored callers on SEQC2 HCC1395 whole-genome data in the half of the genome held out from their model training: 21 replicate pairs from six centres, 47 tumour purity and coverage mixtures, and six library preparations. Their NeuSomatic and NeuSomatic-S models trained on SEQC2 data (SEQC-WGS-Spike, SEQC-WGS-GT-50 and SEQC-WGS-GT50-SpikeWGS10) and Octopus-RF, whose random forest is not identified, are left out because they were built from the same cell line or may have been. Among the rest, mean F1 over the 21 replicates was 92.3% for DRAGEN, 91.8% for NeuSomatic with its DREAM3 model and 89.0% for Strelka2 for SNVs, and 81.7%, 79.3% and 72.8% for indels. Over the purity and coverage mixtures (10x to 300x, 5% to 100% tumour), mean SNV F1 was at most 67.7% (Octopus with hard filters). With 5% tumour in an 80x normal, SNV F1 for a pure tumour fell from 88.6% to 43.8% for MuTect2 and from 93.3% to 47.8% for Lancet, but only from 92.4% to 90.9% for Strelka2. Hasan 2026, a single-author preprint run under the author's own company by someone who developed none of the callers, scored Mutect2, Strelka2, DeepSomatic and three ensembles defined by the author on the GIAB HG008 tumour-normal pair against a draft truth set of clonal and truncal variants; the original scoring code was not retained. In the primary region (14,014 truth variants, excluding sites with germline interference), F1 was 0.91 for a two-of-three majority vote, 0.90 for Mutect2 and DeepSomatic and 0.78 for Strelka2; for indels Mutect2 reached 0.82 and DeepSomatic and Strelka2 0.69. Over the whole draft benchmark, F1 was 0.70 to 0.79 for all six. Two developer papers tested tumour-only calling, without the matched normal this use case assumes, so they are linked as proxy evidence. On Illumina COLO829 at 50x, ClairS-TO's developers report SNV F1 0.77 for ClairS-TO against 0.62 for DeepSomatic, 0.58 for Mutect2, 0.40 for Octopus and 0.22 for Pisces, with indel F1 at most 0.29; each F1 is at the threshold that gave that caller its best F1 on the test data, and truth variants with fewer than three supporting reads or VAF below 0.05 in the tested data were not scored. The VarNet-T developers report SNV AUPRC 0.77 for VarNet-T on SEQC2 and 0.66 on COLO829, against 0.54 and 0.27 for ClairS-TO and 0.08 and 0.07 for Mutect2; on three low-burden tumours every tumour-only caller had AUPRC at most 0.11. The two papers used different COLO829 sequencing data and truth sets: the same ClairS-TO model (Illumina SSRS, v0.4.0) had COLO829 SNV AUPRC 0.65 in its developers' paper and 0.27 in the VarNet-T paper. On a synthetic WES pair, where inserted SNVs make precision near 1 by construction, Mutect2 recalled 0.63 of inserted SNVs and Strelka2 0.46 with default nf-core/sarek settings. Only the HG008 preprint reports interval estimates; no linked study covers FFPE tissue, ctDNA or targeted panels, and none establishes clinical performance.

Every new number traces to a stored result:
- HG008: 14,014 is the primary-overall protocol denominator; 0.913635, 0.897772, 0.897278, 0.778996, 0.823756, 0.689546, 0.690887 for the primary region; 0.697597 to 0.793961 for the all region.
- ClairS-TO Table 7b: 0.7650 and 0.7699, 0.6189, 0.5816, 0.4030, 0.2240; indel maximum 0.2943; SSRS SNV AUPRC 0.6500.
- VarNet-T Table 1: 0.773, 0.656, 0.543, 0.270, 0.078, 0.072. Table 4 maximum: 0.112.
- López-Cade: 0.6313 and 0.4625.

Changes from the collector's draft:
- Rounded the three-decimal and four-decimal values to two decimals, to follow the summary's own rounding rule.
- Labelled the tumour-only evidence as proxy.
- Named the truth-set biases: primary region, draft clonal truth, ClairS-TO's read-support filter and the synthetic precision.
- Stated the missing scoring code.
- Replaced "the same tool scores differently in different developers' hands" with the documented cause: different COLO829 data and truth sets.

## Approved use-case field changes (non-pinned fields only)

No change to `exclusions`, `inputs`, `setting`, `question`, `decision` or `output`.

`evidence_gaps`, replace:
- "No linked comparison covers tumour-only calling, FFPE tissue, ctDNA or targeted panels." with "Tumour-only calling is covered only by proxy evidence from two developer papers (ClairS-TO, VarNet-T) on cell lines and research tumours; no linked comparison covers FFPE tissue, ctDNA or targeted panels."
- "No peer-reviewed HG008 small-variant caller comparison was found; the GIAB HG008 somatic small-variant benchmark is a draft." with "The only linked HG008 small-variant caller comparison is a single-author preprint scored on the draft HG008-T v0.3 benchmark."
- "No linked study reports interval estimates for per-caller precision, recall or F1." with "Only the HG008 preprint (Hasan 2026) reports interval estimates, for F1 only (genomic block bootstrap within one sample); no other linked study reports interval estimates for per-caller precision, recall or F1."

`evidence_gaps`, add:
- "Both linked tumour-only comparisons are developer papers (ClairS-TO, VarNet-T); no independent tumour-only comparison with printed per-caller values was found in the 2025-10 to 2026-10 window."
- "Tumour-only precision, recall and F1 in Chen et al. 2025 are at a threshold chosen on the test data; Krishnamachari et al. 2026 is extracted as AUPRC only."
- "The two tumour-only papers used different COLO829 sequencing data and truth sets (NYGC in Chen et al. 2025, TGen in Krishnamachari et al. 2026), so their COLO829 values are not comparable."
- "Long-read tumour-normal calling (ClairS, Nature Methods 2026) and the peer-reviewed DeepSomatic paper (Nature Biotechnology 2025, not open access) are not linked."
- The collector's amplicon-panel item (Bharne and Gaston 2026), verbatim as in `coverage.json`.

Also approved:
- `assessed_by` links for the 19 protocols in these four batches;
- `source_ids` for their 9 source records;
- one `citation_locators` entry per batch pointing to its `claims.csv`.

## Checks run and outcomes

**Sources.** I re-downloaded all nine artifacts from their recorded URLs and checked their SHA-256 against the source records. All nine match:

| Artifact | Bytes | SHA-256 |
| --- | --- | --- |
| Hasan PDF | 654,435 | 358502e2... |
| Zenodo zip | 1,934,562 | 629921b1... |
| ClairS-TO XML | 143,443 | 6b5e5262... |
| ClairS-TO Source Data | 1,887,973 | 4347c74f... |
| ClairS-TO supplement | 3,006,945 | 806cd474... |
| VarNet-T XML | 97,917 | b42db521... |
| VarNet-T Source Data | 44,784 | 4a2deae7... |
| VarNet-T supplement | 7,533,710 | c808b436... |
| López-Cade XML | 108,973 | 0d115f3c... |

I unzipped the Zenodo zip in its own folder. The three table members match their recorded hashes. The four archived gzips match their recorded gzip and raw hashes.

**Automated full comparison.** I used my own parsers in the scratchpad (`onc1/scripts`), not the collector's scripts:
- HG008: Zenodo TSVs, 144 of 144 cells, matched on row, class, column, evaluation, configuration, protocol, metric, interval and denominator. Zero mismatches.
- ClairS-TO: my regex parse of `pdftotext -layout`, with row labels assigned from the printed layout and confirmed against my own stdlib parse of the Source Data workbook. 434 of 434 cells, zero mismatches.
- VarNet-T: per-page PDF text parse plus Source Data, 153 of 153. Both sources agree after rounding to three decimals. Zero mismatches.
- López-Cade: XML table parse, 18 of 18, zero mismatches.
- No result is left unmatched and no table cell is missing. `claims.csv` covers every result and claim, and its printed values equal the records.

**Arithmetic.** Precision, recall and F1 recompute from the counts to within 5e-7 for HG008 and within 5e-5 for ClairS-TO. TP + FN is constant within every HG008 protocol and equals the stored denominators (14,014; 9,078; 4,936; 18,207). For ClairS-TO it is constant except on Illumina (C4). López-Cade: TP + FP equals Total Query in all three rows, and FreeBayes TP + FN is 4,222 (Q4).

**Hand check against rendered tables.**
- HG008: all 108 cells of Zenodo Extended Data Table 1 (PNG) against the stored values after rounding to four decimals, plus the six all-region F1 values printed in Results.
- ClairS-TO: 63 cells from pages 9 and 15 rendered at 100 to 110 dpi. These were 9 full rows covering Tables 2a, 2b, 7a and 7b and the callers ClairS-TO SS, Clair3, DeepSomatic, Pisces and Mutect2. They include the three-decimal printed values ("0.763").
- VarNet-T: all 36 cells of Table 1, all 27 of Table 4, and 40 of Table 2 (rows VarNet-T, ClairS-TO, Mutect2 and DeepSom-GACA), from rendered pages 18, 19 and 21.
- López-Cade: all 18 cells. The table has only 18, so a 40-value sample is not possible.

Every value agreed.

**Metric, direction, unit, qualifier and uncertainty.**
- All metric and unit keys exist in `data/vocab`. Directions are correct.
- ClairS-TO P, R, F1 and counts carry "at the best-F1 threshold", and AUPRC does not.
- The HG008 intervals match the source: 10,000 replicates, 5-Mb blocks, linear percentile. The one gap is H1.
- No null field lacks a `missing_metadata` reason. The ClairS-TO and VarNet-T protocols have no denominator (C5).

**Origin and author overlap.** I compared author lists with tool provenance:
- Hasan: one author, AmbioSpire. Callers are `independent_paper`; the author's own ensembles are `author_reported`.
- ClairS-TO: Chen, Zheng, Su, Yu, Wong, Zhang, Lee and Luo of HKU-BAL. Clair3 is from the same lab and is correctly `author_reported`.
- VarNet-T: Krishnamachari, Bui Nguyen, Kadioglu, Ong Tze and Skanderup; the VarNet group. DeepSom (Vilov and Heinig), DeepSomatic, Mutect2 and ClairS-TO are `independent_paper`.
- López-Cade: a clinical group, all `independent_paper`.
- All of this is consistent with the store's convention (somatic-neusomatic-20261010).

**Locators.** All the locators I checked find their cell. The wrong ones are V2 (image claim) and W3 (section names).

**Duplicates.**
- No new ID collides with the store (data/entities, data/evidence).
- Every link resolves when the batches are added in the order clairs-to, varnet-t, hg008, wes-synthetic.
- I searched by DOI, PMC ID, Zenodo record, ClairS-TO and VarNet-T across all nine `../rewire-benchmark-data-lit-*` worktrees and all 14 `claude/lit-20261011-*` branches. There are no extractions. The only hits are earlier ledger and research mentions of the HG008 preprint (somatic-20261009) and one uc-execution ledger line naming ClairS-TO.
- Reused methods are appropriate (Strelka2 maps to `somatic-20261009-method-strelka`, matching the Sahraeian batch). The new families ClairS-TO, Clair3, Pisces, DeepSom and VarNet-T are not in the store.

**Scope and relevance.** I read every judgement and `excluded_evaluations` entry. All exclusions have reasons and match the source (VarNet-T SEQC2 DeepSomatic; López-Cade FreeBayes). The relevance changes are C1 and V1, and the missing caveats are H3, H4, C2 to C4 and V3 to V6.

**Not done.**
- I wrote no `review.json` and no dated review, and ran no `npm test`, `typecheck`, `build` or `use-cases:repin`. Those follow once the collector applies the corrections.
- I did not read the DeepSomatic paper, PCAWG donor-project metadata or the Europe PMC rendered HTML of López-Cade Table 1. The XML table was the comparison source.
