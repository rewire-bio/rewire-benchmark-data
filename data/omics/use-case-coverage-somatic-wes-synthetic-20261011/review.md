# Review: use-case-coverage-somatic-wes-synthetic-20261011, 2026-10-11

Reviewer: Claude research agent `reviewer-onc-1`, independent of the extractor `uc-oncology`. No human review claimed. Source transcription is not reproduction. Full review: `docs/reviews/use-cases/tumour-dna-somatic-variant-detection-2026-10-11.md`.

## Reviewer's verdict for this batch (verbatim)

### López-Cade (`use-case-coverage-somatic-wes-synthetic-20261011`)

**W1.** In `somatic-wes-synthetic-20261011-protocol-bamsurgeon-wes-snv` and `use-case-mapping-somatic-wes-synthetic-20261011-bamsurgeon-wes-snv`, replace "Callers run with nf-core/sarek defaults and no tuning; a custom panel of normals was not used (Discussion)." with:

> Callers run with nf-core/sarek 3.5.0 defaults and no tuning; no custom panel of normals was specified, and sarek's default GATK GRCh38 panel of normals was applied to Mutect2 (Discussion).

**W2.** `somatic-wes-synthetic-20261011-config-freebayes` `parameters` is wrong: the source does not say sarek filtered FreeBayes for somatic status. Replace with:

> nf-core/sarek 3.5.0 default parameters; FreeBayes has no PASS filter, so the authors kept calls with QUAL >= 1, SAF > 0, SAR > 0, RPL > 1 and RPR > 1 (Methods 'Variant Calling and Bioinformatic Workflow')

In `somatic-wes-synthetic-20261011-result-freebayes-bamsurgeon-wes-snv-total-query`, change `unit_detail` to "counted entity: filtered SNV calls" and `metric_qualifier` to "SNV only, synthetic WES, total filtered calls".

**W3.** In every record of this batch, replace the locator section name "Methods 'Variant Calling'" with "Methods 2.4 'Variant Calling and Bioinformatic Workflow'". Replace "'Synthetic Data Generation'" with "2.3 'Generation of Synthetic Data with Known Somatic SNVs'" where it appears.

## Reviewer's answers to the collector's questions (verbatim)

1. **Tumour-only scope.** Do not change the use case's `exclusions`, `inputs` or `setting`. Mark all 14 ClairS-TO and VarNet-T judgements `proxy` (C1, V1). The tumour-only evidence is two developer papers. That does not clearly justify a scope change that would withhold the 17 reviewed judgements until they are re-pinned. Only the non-pinned fields change: `evidence_gaps`, `assessed_by` links, `source_ids` and `citation_locators` (text below).
2. **Hasan 2026 quality.** `direct` is acceptable and no `evidence_concern` is needed. The inputs and endpoint match the use case, and the author developed none of the callers. The Zenodo tables are checksum-bound and agree with the manuscript. Every precision, recall and F1 recomputes from TP, FP and FN to within 5e-7. The preprint status, the author's company and the missing scoring code belong in the limitations; the scoring-code point is currently missing from the judgements (H4). DeepSomatic and HG008: the source does not say whether DeepSomatic 1.10.0's WGS model saw HG008. The DeepSomatic README, metrics page and WGS case study (github.com/google/deepsomatic, commit 09d605a966e5dcb10361cd036e05cb79d21b0062) do not list training samples. They name only HCC1395, with chr1 held out. This is unresolved and is recorded as a limitation (H4).
3. **Repository and Source Data values.** For VarNet-T the question does not arise. Supplementary Tables 1 and 4 have a text layer in the pinned PDF (physical pages 18 and 21, printed pages 17 and 20). I rendered both pages and read every cell. All 63 values are printed exactly as stored, so they are ordinary printed values. The locators and `printed_value_basis` must say so (V2). Dorney is not in my scope.
4. **Conflicts.** López-Cade FreeBayes: I confirm TP 1,908 + FN 2,314 = 4,222, and 1,908/4,222 = 0.4519. TP + FP equals Total Query in all three rows. Excluding FreeBayes from the judgement and keeping the limitation is right. A source `evidence_concern` would block the two consistent rows, which the abstract corroborates, so do not add one. VarNet-T DeepSom indel AUPRC: keep the values as printed. The limitation needs a citation (V5).
5. **Training overlap.** I agree with excluding DeepSomatic from the two VarNet-T SEQC2 judgements. ClairS-TO's omission of DeepSomatic on HCC1395 is the authors' choice and is recorded. Three further overlaps need limitations: VarNet-T's training cohort includes 38 gastric tumours, against two stomach PCAWG test samples; DeepSom's BLCA-US, GACA-CN and LAML models share cancer types with the bladder, stomach and AML test samples; and nobody states whether DeepSomatic 1.7.0 saw COLO829 (C2, V3, V4). Best-F1 thresholds chosen on test data are in every ClairS-TO qualifier and limitation, which is enough.
6. **Headline metrics and Clair3.** I accept the headline metrics: F1 for HG008 and ClairS-TO, AUPRC for VarNet-T, recall for López-Cade. Keep Clair3 in the ClairS-TO judgements. Its limitation already says it is a germline caller used as a naive baseline, and its distance from ClairS-TO (ONT COLO829 50x SNV F1 0.71 against 0.76 to 0.77) is useful to someone choosing a method.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store; then `extract/apply_review.py` recorded the review on every record.

1. W1: panel-of-normals limitation replaced in the protocol and judgement.
2. W2: FreeBayes configuration parameters replaced; FreeBayes Total Query unit_detail and metric_qualifier corrected.
3. W3: Methods section names corrected in every locator.

## Records after correction

- claim: 1
- configuration: 3
- dataset: 1
- evaluation: 3
- protocol: 1
- result: 18
- source: 1
