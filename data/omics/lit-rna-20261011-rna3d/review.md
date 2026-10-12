# Review: lit-rna-20261011-rna3d, 2026-10-12

Reviewer: Claude review agent `reviewer-ro-1`, independent of the extractor `lit-rna-otheromics`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

Excerpts of `reviewer-ro-1`'s report that concern this batch, unedited.

Reviewer: Claude review agent (reviewer-ro-1), independent of the collector lit-rna-otheromics; no human review claimed.
Date: 2026-10-12. Worktree reviewed: /Users/timrichardson/Documents/projects/personal/blog/rewire-benchmark-data-lit-rna-otheromics (batch folders treated as the source of truth; no record was edited and nothing was committed).

- `data/omics/lit-rna-20261011-rna3d` (216 results): approved with corrections (D1 to D4).

No printed value, numeric value, uncertainty value or locator is wrong in any of the three batches. The corrections mark results whose source is internally inconsistent, fix one wrong descriptive field, and tighten wording.

None of the three batches proposes a use-case judgement or summary text, and no existing use case covers RNA language models, RNA fitness or RNA 3D structure. There is no summary text or use-case field change to approve.

## Corrections

All corrections apply to `batch.jsonl` before `records -- add`, so no `records -- change` or `metadata-correction-*` claim is needed. Status `disputed` with `attributes.source_warnings` follows the store's precedent for results the source contradicts (for example the ctdnameth, brca and alphagenome-2026 results). I did not use source-level `evidence_concerns` because the build then blocks comparison for every result citing that source: all 216 rna3d results or all 1190 rnalm-zeroshot results, when the problem is confined to a few cells.

### lit-rna-20261011-rna3d

D1. DRfold and DeepFoldRNA duplicate columns. I confirmed from my own parse of the supplement that the per-target INF, GDT-TS and lDDT columns for the two methods are identical for every target (S3 30 easy and 49 hard, S4 30 and 49, S5 29 and 47), while their TM-score columns in S2 differ for every target. At least one method's INF, GDT-TS and lDDT values are therefore not its own. For these 24 results set `status` to `disputed` and add `attributes.source_warnings`: ["Ludaic and Elofsson 2026 print identical INF, GDT-TS and lDDT for DRfold and DeepFoldRNA in Tables 2-3, and the per-target columns of Supplementary Tables S3-S5 are identical for every target, while their TM-scores differ. At least one method's values are not its own; not resolved from the source."]

- `lit-rna-20261011-rna3d-result-drfold-monomer-easy-mean-gdt-ts`, `-mean-inf`, `-mean-lddt`
- `lit-rna-20261011-rna3d-result-drfold-monomer-hard-mean-gdt-ts`, `-mean-inf`, `-mean-lddt`
- `lit-rna-20261011-rna3d-result-drfold-monomer-easy-success-gdt-ts`, `-success-inf`, `-success-lddt`
- `lit-rna-20261011-rna3d-result-drfold-monomer-hard-success-gdt-ts`, `-success-inf`, `-success-lddt`
- the same 12 IDs with `deepfoldrna` in place of `drfold`

The TM-score results of both methods are not affected.

D2. RF2NA hard-set INF. Table 3 prints 0.668; the mean of the RF2NA column of Supplementary Table S3 over the 49 hard targets is 0.608 by my parse, and every other method's S3 mean reproduces Table 3 to rounding. Set `lit-rna-20261011-rna3d-result-rf2na-monomer-hard-mean-inf` to `status` `disputed` with `attributes.source_warnings`: ["Table 3 prints INF 0.668 for RF2NA on the hard set; the mean of the RF2NA column of Supplementary Table S3 over the 49 hard targets is 0.608. Recorded as printed; not resolved from the source."]

D3. New finding: AF3 hard-set GDT-TS success rate. Supplementary Table S7 prints 37.78%, which is not k/49 for any whole k. Counting AF3 targets with GDT-TS above 0.45 in Supplementary Table S4 gives 19/49 = 38.78%. Every other one of the 80 success-rate cells in S6 and S7 reproduces exactly from S2-S5 with the stated thresholds. Set `lit-rna-20261011-rna3d-result-af3-monomer-hard-success-gdt-ts` to `status` `disputed` with `attributes.source_warnings`: ["Supplementary Table S7 prints 37.78% for AF3 GDT-TS on the hard set, which is not a whole number of the 49 hard targets; Supplementary Table S4 has 19 of 49 AF3 targets above the 0.45 threshold (38.78%). Recorded as printed; not resolved from the source."]

D4. Append to `attributes.limitations` of `lit-rna-20261011-rna3d-source-ludaic2026-supplement`: "Supplementary Table S7 prints 37.78% for AF3 GDT-TS on the hard set; Supplementary Table S4 gives 19 of 49 targets (38.78%). The DRfold and DeepFoldRNA per-target INF, GDT-TS and lDDT columns of Supplementary Tables S3-S5 are identical."

### Review fields to apply

After C1 to D4, set `status` to `source_checked` on every other record in the three batches and fill each result's `review` with the following. Keep `artifact_sha256` and `retrieval_url` as they are, because they match what I checked.

- `method`: ["source-hash-verification", "deterministic-table-parse", "independent-cell-check"]. For rna3d results located in Supplementary Tables S6, S7 and S15, use ["source-hash-verification", "pdf-text-parse", "independent-cell-check"].
- `reviewer`: ["claude"]
- `reviewer_note`: "Claude review agent reviewer-ro-1, independent of the extractor lit-rna-otheromics; no human review claimed"
- `date`: "2026-10-12"
- `method_note`:
  - rnalm-zeroshot: "Re-fetched the Europe PMC supplementary archive; the .docx inside matched its SHA-256. An independent w:tc parse of Supplementary Tables 4-11 matched all 1190 printed values, numeric values, standard deviations and locators; 48 cells were also checked by hand against a textutil rendering."
  - rnagym: "Re-fetched README, CSVs and LICENSE at commit 2828cf9 and matched their SHA-256. An independent Markdown table parse matched all 64 printed and numeric values and locators; all 64 were also read against the rendered table."
  - rna3d: "Re-fetched the PMC XML and the supplementary PDF and matched their SHA-256. An independent parse of Tables 2-5 and Supplementary Tables S6, S7 and S15 (pdftotext -layout and -raw) matched all 216 printed and numeric values and locators; 42 cells were also checked by hand. Success rates in S6-S7 were recomputed from S2-S5 as a consistency check, not as a derivation."
- `note`: keep the extraction note and append "Independent review 2026-10-12: value, locator, metric, unit, direction and linked configuration and protocol checked." For the disputed results, also append "Disputed: see source_warnings."

Then write each batch's `review.json` and the dated review in `docs/reviews/`, and run `npm test`, `npm run typecheck` and `npm run build`.

1. rna3d. Both issues are real and reproduced independently: the identical DRfold and DeepFoldRNA columns, and RF2NA hard INF of 0.668 printed against a column mean of 0.608. I also found a third issue, the AF3 hard GDT-TS success rate (D3). None of the three should go in source-level `evidence_concerns`, because that would block all 216 results. Use result-level `disputed` with `source_warnings` (D1 to D3), and keep the existing source limitations.

6. Confirmed. My fresh Europe PMC supplementaryFiles zips hash differently from the collector's zip hash (wang `766b8a02...` against the recorded `560f4810...`), because Europe PMC rebuilds the archive. The files inside match the recorded hashes exactly: `bbag098_supplymentary_information_20260209.docx` c8fc78c3... and `gkag813_supplemental_file.pdf` 0e26a301.... Pinning the inner file is the right choice.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store. The review fields were set by `finalise` in `extract/lib.py`.

1. D1: the 24 DRfold and DeepFoldRNA INF, GDT-TS and lDDT results (easy and hard, mean and success rate) are `disputed` with the reviewer's `source_warnings`. Their TM-score results are unchanged.
2. D2: `lit-rna-20261011-rna3d-result-rf2na-monomer-hard-mean-inf` is `disputed` with the reviewer's `source_warnings`.
3. D3: `lit-rna-20261011-rna3d-result-af3-monomer-hard-success-gdt-ts` is `disputed` with the reviewer's `source_warnings`.
4. D4: the reviewer's sentence is appended to the limitations of `lit-rna-20261011-rna3d-source-ludaic2026-supplement`.
5. Review fields: every other record is `source_checked`; results located in Supplementary Tables S6, S7 and S15 use method pdf-text-parse, the rest deterministic-table-parse, as the reviewer specified.

## Records after correction

- benchmark: 1
- configuration: 10
- dataset: 5
- evaluation: 216
- model: 5
- protocol: 30
- result: 216
- source: 2

Status: disputed 26, source_checked 459.
