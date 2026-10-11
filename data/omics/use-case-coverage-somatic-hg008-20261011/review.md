# Review: use-case-coverage-somatic-hg008-20261011, 2026-10-11

Reviewer: Claude research agent `reviewer-onc-1`, independent of the extractor `uc-oncology`. No human review claimed. Source transcription is not reproduction. Full review: `docs/reviews/use-cases/tumour-dna-somatic-variant-detection-2026-10-11.md`.

## Reviewer's verdict for this batch (verbatim)

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

## Reviewer's answers to the collector's questions (verbatim)

1. **Tumour-only scope.** Do not change the use case's `exclusions`, `inputs` or `setting`. Mark all 14 ClairS-TO and VarNet-T judgements `proxy` (C1, V1). The tumour-only evidence is two developer papers. That does not clearly justify a scope change that would withhold the 17 reviewed judgements until they are re-pinned. Only the non-pinned fields change: `evidence_gaps`, `assessed_by` links, `source_ids` and `citation_locators` (text below).
2. **Hasan 2026 quality.** `direct` is acceptable and no `evidence_concern` is needed. The inputs and endpoint match the use case, and the author developed none of the callers. The Zenodo tables are checksum-bound and agree with the manuscript. Every precision, recall and F1 recomputes from TP, FP and FN to within 5e-7. The preprint status, the author's company and the missing scoring code belong in the limitations; the scoring-code point is currently missing from the judgements (H4). DeepSomatic and HG008: the source does not say whether DeepSomatic 1.10.0's WGS model saw HG008. The DeepSomatic README, metrics page and WGS case study (github.com/google/deepsomatic, commit 09d605a966e5dcb10361cd036e05cb79d21b0062) do not list training samples. They name only HCC1395, with chr1 held out. This is unresolved and is recorded as a limitation (H4).
3. **Repository and Source Data values.** For VarNet-T the question does not arise. Supplementary Tables 1 and 4 have a text layer in the pinned PDF (physical pages 18 and 21, printed pages 17 and 20). I rendered both pages and read every cell. All 63 values are printed exactly as stored, so they are ordinary printed values. The locators and `printed_value_basis` must say so (V2). Dorney is not in my scope.
4. **Conflicts.** López-Cade FreeBayes: I confirm TP 1,908 + FN 2,314 = 4,222, and 1,908/4,222 = 0.4519. TP + FP equals Total Query in all three rows. Excluding FreeBayes from the judgement and keeping the limitation is right. A source `evidence_concern` would block the two consistent rows, which the abstract corroborates, so do not add one. VarNet-T DeepSom indel AUPRC: keep the values as printed. The limitation needs a citation (V5).
5. **Training overlap.** I agree with excluding DeepSomatic from the two VarNet-T SEQC2 judgements. ClairS-TO's omission of DeepSomatic on HCC1395 is the authors' choice and is recorded. Three further overlaps need limitations: VarNet-T's training cohort includes 38 gastric tumours, against two stomach PCAWG test samples; DeepSom's BLCA-US, GACA-CN and LAML models share cancer types with the bladder, stomach and AML test samples; and nobody states whether DeepSomatic 1.7.0 saw COLO829 (C2, V3, V4). Best-F1 thresholds chosen on test data are in every ClairS-TO qualifier and limitation, which is enough.
6. **Headline metrics and Clair3.** I accept the headline metrics: F1 for HG008 and ClairS-TO, AUPRC for VarNet-T, recall for López-Cade. Keep Clair3 in the ClairS-TO judgements. Its limitation already says it is a germline caller used as a naive baseline, and its distance from ClairS-TO (ONT COLO829 50x SNV F1 0.71 against 0.76 to 0.77) is useful to someone choosing a method.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store; then `extract/apply_review.py` recorded the review on every record.

1. H1: 95% block-bootstrap F1 intervals added as uncertainty on the six all-region F1 results (manuscript Results, Supplementary Table 2).
2. H2: all-region protocol and judgement limitation replaced with the reviewer's text on the printed intervals.
3. H3: primary-region limitation on the 14,014 of 18,207 truth variants and the full-benchmark F1 range added to the three primary protocols and judgements.
4. H4: 'The author does not establish'; limitations on the unretained scoring code and on unknown DeepSomatic HG008 training added to all four protocols and judgements.
5. H5: coverage.json gaps no longer list the all-region bootstrap as unextracted.

## Records after correction

- claim: 4
- configuration: 6
- dataset: 1
- evaluation: 24
- protocol: 4
- result: 144
- source: 2
