# Review: use-case-coverage-somatic-clairs-to-20261011, 2026-10-11

Reviewer: Claude research agent `reviewer-onc-1`, independent of the extractor `uc-oncology`. No human review claimed. Source transcription is not reproduction. Full review: `docs/reviews/use-cases/tumour-dna-somatic-variant-detection-2026-10-11.md`.

## Reviewer's verdict for this batch (verbatim)

### ClairS-TO (`use-case-coverage-somatic-clairs-to-20261011`)

**C1.** In all eight claims `use-case-mapping-somatic-clairs-to-20261011-{ont-colo829-snv, ont-colo829-indel, ont-hcc1395-snv, ont-hcc1395-indel, pacbio-colo829-snv, pacbio-colo829-indel, illumina-colo829-snv, illumina-colo829-indel}`, and in `coverage.json` `judgements`, set `relevance` to `proxy`. Replace `rationale` and the claim `description` with:

> Proxy, not direct: the endpoint matches (per-caller precision, recall and F1 on held-out cell lines with consortium truth sets), but the callers used tumour reads only, whereas this use case's inputs include a matched normal and its exclusions list tumour-only calling. Linked as the closest evidence for users without a matched normal.

Delete `coverage.json` `use_case_changes` keys `exclusions_replace`, `inputs_add` and `setting_append`, or mark them rejected. The same change applies to the copies in the other three batches' `coverage.json`.

**C2.** Add "Whether the DeepSomatic 1.7.0 models were trained with COLO829 data is not stated in the source." to the six COLO829 protocols (`somatic-clairs-to-20261011-protocol-{ont,pacbio,illumina}-colo829-{snv,indel}`) and their six claims.

**C3.** Add "Competing interests: the senior author (R.L.) receives research funding from ONT." to all eight protocols and all eight claims.

**C4.** Add this limitation to `somatic-clairs-to-20261011-protocol-illumina-colo829-snv` and `-indel` and to their two claims:

> TP + FN is not identical across callers (SNV 40,232, but 40,230 for Pisces; indel 715, but 714 for Mutect2 and 713 for Octopus), so the scored truth set differs slightly between rows; the source does not explain this.

**C5 (optional).** TP + FN is constant within each other protocol, so `denominator` could be set: ONT COLO829 SNV 37533, indel 585; ONT HCC1395 SNV 32212, indel 1356; PacBio COLO829 SNV 39086, indel 610. Note in each that it is TP + FN after the authors' truth filter. Leave the Illumina protocols without a denominator.

## Reviewer's answers to the collector's questions (verbatim)

1. **Tumour-only scope.** Do not change the use case's `exclusions`, `inputs` or `setting`. Mark all 14 ClairS-TO and VarNet-T judgements `proxy` (C1, V1). The tumour-only evidence is two developer papers. That does not clearly justify a scope change that would withhold the 17 reviewed judgements until they are re-pinned. Only the non-pinned fields change: `evidence_gaps`, `assessed_by` links, `source_ids` and `citation_locators` (text below).
2. **Hasan 2026 quality.** `direct` is acceptable and no `evidence_concern` is needed. The inputs and endpoint match the use case, and the author developed none of the callers. The Zenodo tables are checksum-bound and agree with the manuscript. Every precision, recall and F1 recomputes from TP, FP and FN to within 5e-7. The preprint status, the author's company and the missing scoring code belong in the limitations; the scoring-code point is currently missing from the judgements (H4). DeepSomatic and HG008: the source does not say whether DeepSomatic 1.10.0's WGS model saw HG008. The DeepSomatic README, metrics page and WGS case study (github.com/google/deepsomatic, commit 09d605a966e5dcb10361cd036e05cb79d21b0062) do not list training samples. They name only HCC1395, with chr1 held out. This is unresolved and is recorded as a limitation (H4).
3. **Repository and Source Data values.** For VarNet-T the question does not arise. Supplementary Tables 1 and 4 have a text layer in the pinned PDF (physical pages 18 and 21, printed pages 17 and 20). I rendered both pages and read every cell. All 63 values are printed exactly as stored, so they are ordinary printed values. The locators and `printed_value_basis` must say so (V2). Dorney is not in my scope.
4. **Conflicts.** López-Cade FreeBayes: I confirm TP 1,908 + FN 2,314 = 4,222, and 1,908/4,222 = 0.4519. TP + FP equals Total Query in all three rows. Excluding FreeBayes from the judgement and keeping the limitation is right. A source `evidence_concern` would block the two consistent rows, which the abstract corroborates, so do not add one. VarNet-T DeepSom indel AUPRC: keep the values as printed. The limitation needs a citation (V5).
5. **Training overlap.** I agree with excluding DeepSomatic from the two VarNet-T SEQC2 judgements. ClairS-TO's omission of DeepSomatic on HCC1395 is the authors' choice and is recorded. Three further overlaps need limitations: VarNet-T's training cohort includes 38 gastric tumours, against two stomach PCAWG test samples; DeepSom's BLCA-US, GACA-CN and LAML models share cancer types with the bladder, stomach and AML test samples; and nobody states whether DeepSomatic 1.7.0 saw COLO829 (C2, V3, V4). Best-F1 thresholds chosen on test data are in every ClairS-TO qualifier and limitation, which is enough.
6. **Headline metrics and Clair3.** I accept the headline metrics: F1 for HG008 and ClairS-TO, AUPRC for VarNet-T, recall for López-Cade. Keep Clair3 in the ClairS-TO judgements. Its limitation already says it is a germline caller used as a naive baseline, and its distance from ClairS-TO (ONT COLO829 50x SNV F1 0.71 against 0.76 to 0.77) is useful to someone choosing a method.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store; then `extract/apply_review.py` recorded the review on every record.

1. C1: all eight judgements set to proxy with the reviewer's rationale and description; collector's use-case scope changes rejected in coverage.json.
2. C2: COLO829 DeepSomatic training limitation added to the six COLO829 protocols and judgements.
3. C3: competing-interests limitation added to all eight protocols and judgements.
4. C4: TP + FN inconsistency limitation added to the two Illumina protocols and judgements.
5. C5 (optional, applied): denominators set on the six ONT and PacBio protocols, with a limitation noting they are TP + FN after the authors' truth filter.

## Records after correction

- claim: 8
- configuration: 14
- dataset: 4
- evaluation: 34
- method: 3
- protocol: 8
- result: 434
- source: 3
