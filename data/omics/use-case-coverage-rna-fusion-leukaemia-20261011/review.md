# Review: use-case-coverage-rna-fusion-leukaemia-20261011, 2026-10-11

Reviewer: Claude research agent `reviewer-onc-2`, independent of the extractor `uc-oncology`. No human review claimed. Source transcription is not reproduction. Full review: `docs/reviews/use-cases/tumour-rna-fusion-detection-2026-10-11.md`.

## Reviewer's verdict for this batch (verbatim)

### use-case-coverage-rna-fusion-leukaemia-20261011 (Kim et al. 2025): approved with corrections

All 83 values are correct. The corrections are one unsupported statement and the numeric form of ten non-measurements.

L1. The batch says several of the RNA-seq-only fusions were confirmed by RT-PCR and Sanger sequencing. The retrieved article does not support this. Figure 1 shows RT-PCR and Sanger confirmation for KMT2A::THAP12, which is a conventional-positive fusion with an unspecified partner (row KMT2A::?), and for MLLT10::UBE2L6, which is RNA-seq only. FUS::ZNF362 and RUNX1::PRPF19 were not tested. Supplemental Figure S1 was not retrieved. Make these replacements:
- In `limitations` of protocol `rna-fusion-leukaemia-20261011-protocol-conventional-diagnostics` and of claim `use-case-mapping-rna-fusion-leukaemia-20261011-conventional-diagnostics`, replace "Truth is conventional diagnostics (karyotyping, FISH, multiplex RT-PCR), which miss some fusions: RNA-seq-only fusions count against specificity although several were confirmed by RT-PCR and Sanger sequencing." with:
  > Truth is conventional diagnostics (karyotyping, FISH, multiplex RT-PCR), which miss some fusions: the 12 RNA-seq-only fusions count against specificity, although the authors describe several as well-known recurrent fusions and confirmed one of them (MLLT10::UBE2L6) by RT-PCR and Sanger sequencing (Figure 1); validation was attempted only for novel or rare fusions with residual sample.
- In result `rna-fusion-leukaemia-20261011-result-arriba-one-minus-specificity`, set `metric_qualifier` to:
  > overall, 56 fusion-negative results by conventional diagnostics; RNA-seq-only fusions counted as errors, though the authors describe several as well-known recurrent fusions and confirmed one by RT-PCR and Sanger sequencing
- In `coverage.json` `use_case_changes.evidence_gaps_add[0]`, use the text approved below.

L2. In the ten RNA-seq-only concordance results, the printed 0 is not a measured agreement, yet `numeric_value` is "0". As stored, the page would show 0% agreement. Every `undefined_reason` result in the store has a null `numeric_value`, and so do this lane's Dorney F1 'NA' rows. For each ID below, keep `printed_value` "0" and `undefined_reason`, set `numeric_value` to null, and add `missing_metadata.value` = `{"reason": "inapplicable", "note": "Concordance is not defined for fusions with no conventional detection; the table prints 0"}`. If the validator rejects a null numeric value with a numeric printed value, report it instead of working around it.
`rna-fusion-leukaemia-20261011-result-etv6-ncoa2-concordance`, `-fus-znf362-concordance`, `-hnrnph1-erg-concordance`, `-igh-crlf2-concordance`, `-mllt10-ube2l6-concordance`, `-p2ry8-crlf2-concordance`, `-pax5-jak2-concordance`, `-pax5-nol4l-concordance`, `-picalm-mllt10-concordance`, `-runx1-usp42-concordance` (each with prefix `rna-fusion-leukaemia-20261011-result`). Do not change `kmt2a-mllt10-concordance` or `tra-d-unspecified-concordance`: those are real 0% agreements (0 of 1 and 0 of 2).

L3. Add this limitation to the protocol and the claim:
> Per-patient results (Supplemental Data Tables S2 and S3) and Supplemental Figure S1 were not retrieved; the AML (86.4%) and B-ALL (87.0%) sensitivities are printed only in the Discussion, without denominators.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store; then `extract/apply_review.py` recorded the review on every record.

1. L1: conventional-diagnostics limitation and the 1 - specificity qualifier replaced with the reviewer's text; coverage.json gap text uses the approved wording.
2. L2: the ten RNA-seq-only concordance results now have a null numeric value with missing_metadata.value inapplicable; printed value and undefined_reason kept.
3. L3: limitation on unretrieved supplementary per-patient results added to the protocol and judgement.

## Records after correction

- claim: 1
- configuration: 1
- dataset: 1
- evaluation: 1
- protocol: 1
- result: 83
- source: 1
