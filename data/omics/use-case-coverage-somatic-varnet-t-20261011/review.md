# Review: use-case-coverage-somatic-varnet-t-20261011, 2026-10-11

Reviewer: Claude research agent `reviewer-onc-1`, independent of the extractor `uc-oncology`. No human review claimed. Source transcription is not reproduction. Full review: `docs/reviews/use-cases/tumour-dna-somatic-variant-detection-2026-10-11.md`.

## Reviewer's verdict for this batch (verbatim)

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

## Reviewer's answers to the collector's questions (verbatim)

1. **Tumour-only scope.** Do not change the use case's `exclusions`, `inputs` or `setting`. Mark all 14 ClairS-TO and VarNet-T judgements `proxy` (C1, V1). The tumour-only evidence is two developer papers. That does not clearly justify a scope change that would withhold the 17 reviewed judgements until they are re-pinned. Only the non-pinned fields change: `evidence_gaps`, `assessed_by` links, `source_ids` and `citation_locators` (text below).
2. **Hasan 2026 quality.** `direct` is acceptable and no `evidence_concern` is needed. The inputs and endpoint match the use case, and the author developed none of the callers. The Zenodo tables are checksum-bound and agree with the manuscript. Every precision, recall and F1 recomputes from TP, FP and FN to within 5e-7. The preprint status, the author's company and the missing scoring code belong in the limitations; the scoring-code point is currently missing from the judgements (H4). DeepSomatic and HG008: the source does not say whether DeepSomatic 1.10.0's WGS model saw HG008. The DeepSomatic README, metrics page and WGS case study (github.com/google/deepsomatic, commit 09d605a966e5dcb10361cd036e05cb79d21b0062) do not list training samples. They name only HCC1395, with chr1 held out. This is unresolved and is recorded as a limitation (H4).
3. **Repository and Source Data values.** For VarNet-T the question does not arise. Supplementary Tables 1 and 4 have a text layer in the pinned PDF (physical pages 18 and 21, printed pages 17 and 20). I rendered both pages and read every cell. All 63 values are printed exactly as stored, so they are ordinary printed values. The locators and `printed_value_basis` must say so (V2). Dorney is not in my scope.
4. **Conflicts.** López-Cade FreeBayes: I confirm TP 1,908 + FN 2,314 = 4,222, and 1,908/4,222 = 0.4519. TP + FP equals Total Query in all three rows. Excluding FreeBayes from the judgement and keeping the limitation is right. A source `evidence_concern` would block the two consistent rows, which the abstract corroborates, so do not add one. VarNet-T DeepSom indel AUPRC: keep the values as printed. The limitation needs a citation (V5).
5. **Training overlap.** I agree with excluding DeepSomatic from the two VarNet-T SEQC2 judgements. ClairS-TO's omission of DeepSomatic on HCC1395 is the authors' choice and is recorded. Three further overlaps need limitations: VarNet-T's training cohort includes 38 gastric tumours, against two stomach PCAWG test samples; DeepSom's BLCA-US, GACA-CN and LAML models share cancer types with the bladder, stomach and AML test samples; and nobody states whether DeepSomatic 1.7.0 saw COLO829 (C2, V3, V4). Best-F1 thresholds chosen on test data are in every ClairS-TO qualifier and limitation, which is enough.
6. **Headline metrics and Clair3.** I accept the headline metrics: F1 for HG008 and ClairS-TO, AUPRC for VarNet-T, recall for López-Cade. Keep Clair3 in the ClairS-TO judgements. Its limitation already says it is a germline caller used as a naive baseline, and its distance from ClairS-TO (ONT COLO829 50x SNV F1 0.71 against 0.76 to 0.77) is useful to someone choosing a method.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store; then `extract/apply_review.py` recorded the review on every record.

1. V1: all six judgements set to proxy with the reviewer's rationale and description.
2. V2: Supplementary Tables 1 and 4 now parsed from the PDF text layer (physical pages 18 and 21); locators, printed_value_basis, review method, artifact hash and retrieval URL corrected; research.md, retrieval-log.md and coverage.json gap fixed.
3. V3: PCAWG dataset split replaced; two training-overlap limitations added to the PCAWG protocol and judgement.
4. V4: DeepSom-LAML limitation added to the low-TMB protocol and judgement.
5. V5: DeepSom indel limitation replaced in the two indel protocols and judgements.
6. V6: scope_note truth sets added to the COLO829 and SEQC2 datasets; COLO829 comparability limitation added to the two COLO829 protocols and judgements.

## Records after correction

- claim: 6
- configuration: 9
- dataset: 4
- evaluation: 54
- method: 2
- protocol: 6
- result: 153
- source: 3
