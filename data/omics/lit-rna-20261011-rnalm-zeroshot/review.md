# Review: lit-rna-20261011-rnalm-zeroshot, 2026-10-12

Reviewer: Claude review agent `reviewer-ro-1`, independent of the extractor `lit-rna-otheromics`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

Excerpts of `reviewer-ro-1`'s report that concern this batch, unedited.

Reviewer: Claude review agent (reviewer-ro-1), independent of the collector lit-rna-otheromics; no human review claimed.
Date: 2026-10-12. Worktree reviewed: /Users/timrichardson/Documents/projects/personal/blog/rewire-benchmark-data-lit-rna-otheromics (batch folders treated as the source of truth; no record was edited and nothing was committed).

- `data/omics/lit-rna-20261011-rnalm-zeroshot` (1190 results): approved with corrections (C1 to C4).

- `data/vocab/metric.ttl`: `one-minus-overlap-ratio`, `spectral-angle-similarity` and `fingerprint-tanimoto-similarity` approved; `spectral-angle` approved with correction V1.

No printed value, numeric value, uncertainty value or locator is wrong in any of the three batches. The corrections mark results whose source is internally inconsistent, fix one wrong descriptive field, and tighten wording.

None of the three batches proposes a use-case judgement or summary text, and no existing use case covers RNA language models, RNA fitness or RNA 3D structure. There is no summary text or use-case field change to approve.

## Corrections

All corrections apply to `batch.jsonl` before `records -- add`, so no `records -- change` or `metadata-correction-*` claim is needed. Status `disputed` with `attributes.source_warnings` follows the store's precedent for results the source contradicts (for example the ctdnameth, brca and alphagenome-2026 results). I did not use source-level `evidence_concerns` because the build then blocks comparison for every result citing that source: all 216 rna3d results or all 1190 rnalm-zeroshot results, when the problem is confined to a few cells.

### lit-rna-20261011-rnalm-zeroshot

C1. RFamLlama 1 - OR contradicts AUC in the same rows. For each of these 8 results set `status` to `disputed` and add `attributes.source_warnings` with the one string given:

| Result ID | AUC printed in the same row |
| --- | --- |
| `lit-rna-20261011-rnalm-zeroshot-result-rfamllama-base-t6-1-or-sampled-mean` | 0.660±0.001 |
| `lit-rna-20261011-rnalm-zeroshot-result-rfamllama-large-t6-1-or-sampled-mean` | 0.685±0.001 |
| `lit-rna-20261011-rnalm-zeroshot-result-rfamllama-base-t7-1-or-sampled-mean` | 0.613±0.001 |
| `lit-rna-20261011-rnalm-zeroshot-result-rfamllama-large-t7-1-or-sampled-mean` | 0.654±0.002 |
| `lit-rna-20261011-rnalm-zeroshot-result-rfamllama-base-t8-1-or-sampled-mean` | 0.654±0.001 |
| `lit-rna-20261011-rnalm-zeroshot-result-rfamllama-large-t8-1-or-sampled-mean` | 0.688±0.002 |
| `lit-rna-20261011-rnalm-zeroshot-result-rfamllama-base-t9-1-or-sampled-mean` | 0.613±0.002 |
| `lit-rna-20261011-rnalm-zeroshot-result-rfamllama-large-t9-1-or-sampled-mean` | 0.655±0.001 |

Warning text (substitute N and the AUC from the table): "Supplementary Table N prints 1 − OR 0.000±0.000 for this row, meaning the homologous and non-homologous similarity distributions overlap completely, but prints AUC <AUC> in the same row; complete overlap implies an AUC near 0.5. Recorded as printed; not resolved from the source."

C2. Wrong length limit on starred rows of Supplementary Tables 7 and 9. The notes under Tables 7 and 9 say sequences over 440 nt were excluded; only Tables 6 and 8 say 440/512 nt. In every evaluation whose `attributes.source_locator` starts with "Supplementary Table 7," or "Supplementary Table 9," and whose `attributes.comparison.population` is "Starred row: sequences longer than the model's limit (440 or 512 nt) were excluded", set `comparison.population` to "Starred row: sequences longer than 440 nt were excluded (table note)".

C3. Dataset locators. In `lit-rna-20261011-rnalm-zeroshot-data-rfamsample`, `-data-rnagym-ncrna31`, `-data-ts` and `-data-ts-hard`, set `attributes.source_locator` to "Main text Methods 'Datasets'". Keep `-data-archiveii-nr` as it is.

C4. Degenerate classifier rows. Append this string to `attributes.limitations` of the four protocols `lit-rna-20261011-rnalm-zeroshot-protocol-t6-f1-sampled-mean`, `-t7-f1-sampled-mean`, `-t8-f1-sampled-mean` and `-t9-f1-sampled-mean`: "Many rows print F1 0.667 with MCC near 0, which is what a classifier that labels every pair homologous scores when the two classes are equal in size; the source does not describe the decision threshold for F1 and MCC."

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

2. rnalm-zeroshot. `author_reported` for RNA-MSM is correct. RNA-MSM (ref. 29, Zhang Y, Lang M, Jiang J et al., NAR 2024) is from the corresponding authors' group (Zhan J, Zhou Y; first author Zhang Yikun), and the TS and VL1 sets also come from ref. 29. The benchmark record's limitation already says so. No other evaluated model shares an author: ref. 60 (SpliceBERT) lists a "Zhou Y", but that is Yue Zhou of a different group. RFamLlama 1 - OR 0.000 is correctly transcribed as printed, but it contradicts the AUC in the same rows, so all 8 such results should be disputed (C1). The 14 new family records duplicate no `model` record on origin/main (bba147c). The store does hold configuration and pipeline records with the same names but no family link: `mrnabench-method-aido-rna`, `mrnabench-method-ernie-rna`, `mrnabench-method-rinalmo`, `mrnabench-method-orthrus`, `nabench-method-aido-rna`, `nabench-method-rinalmo-giga`, `nabench-method-genslm`, `reported-model-d023fbe78bc4df` (ERNIE-RNA), `reported-model-3e58d0faf88d2e` (RiNALMo) and the `mimic-2026-mrnabench-*` and `mrnabench-variants-2025-*` pipelines. They are not duplicates of family records. Linking them to the new families is a separate follow-up and does not block this batch.

6. Confirmed. My fresh Europe PMC supplementaryFiles zips hash differently from the collector's zip hash (wang `766b8a02...` against the recorded `560f4810...`), because Europe PMC rebuilds the archive. The files inside match the recorded hashes exactly: `bbag098_supplymentary_information_20260209.docx` c8fc78c3... and `gkag813_supplemental_file.pdf` 0e26a301.... Pinning the inner file is the right choice.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store. The review fields were set by `finalise` in `extract/lib.py`.

1. C1: the 8 RFamLlama 1 - OR results are `disputed`, each with the reviewer's `source_warnings` text and the AUC printed in its row (asserted against the parsed table).
2. C2: starred rows of Supplementary Tables 7 and 9 have `comparison.population` "Starred row: sequences longer than 440 nt were excluded (table note)" (8 evaluations).
3. C3: the RfamSample, RNAGym ncRNA, TS and TS-Hard dataset locators are "Main text Methods 'Datasets'"; ArchiveII-Nr is unchanged.
4. C4: the degenerate-classifier limitation is appended to the four Table 6-9 F1 protocols.
5. Review fields: every other record is `source_checked`; each result carries the reviewer's review block. The result `note` keeps the extraction description, prefixed "Extraction:", and appends the reviewer's sentence (and "Disputed: see source_warnings." on the C1 results).

## Records after correction

- benchmark: 1
- configuration: 40
- dataset: 5
- evaluation: 1190
- model: 14
- protocol: 36
- result: 1190
- source: 2

Status: disputed 8, source_checked 2470.
