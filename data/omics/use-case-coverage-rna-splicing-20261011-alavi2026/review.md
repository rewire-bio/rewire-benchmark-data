# Review: use-case-coverage-rna-splicing-20261011-alavi2026, 2026-10-12

Reviewer: independent Claude review agent `reviewer-scnv`, separate from the extracting agent `uc-splicing-cnv`. No human review claimed. Source transcription is not reproduction. The full review, covering all five splicing and CNV batches, is `docs/reviews/use-cases/splicing-cnv-use-cases-2026-10-12.md`.

## Reviewer's report (verbatim)

| Batch | Verdict |
| --- | --- |
| `use-case-coverage-rna-splicing-20261011-alavi2026` | Approved with corrections (duplicate Genos model, names, limitations, hash scope) |

Applies to every batch: delete `extract/__pycache__/` from each batch folder before writing `review.json`, so the receipt does not hash compiled bytecode.

### alavi2026: approved with corrections

1. Duplicate model. `lit-microbial-20261011-virobench-model-genos` (Genos family, `source_checked`) has already been added to the store in the microbial worktree. Remove `rna-splicing-20261011-alavi2026-model-genos` from `batch.jsonl` and `claims.csv`. Point the `configuration_of` link of `rna-splicing-20261011-alavi2026-config-genos-10b` and `rna-splicing-20261011-alavi2026-config-genos-10b-clinvar` at `lit-microbial-20261011-virobench-model-genos`, and update `coverage.json`. If the microbial batch does not land first, the microbial batch must reuse the Alavi ID instead; the two records must not both reach the store.
2. Name casing. In the `name` field of every configuration, evaluation and result record in the batch, replace:
   - `Alphagenome` with `AlphaGenome`
   - `Spliceai` with `SpliceAI`
   - `Ntv3` with `NTv3`
   - `Clinvar` with `ClinVar`
   - `-Bp)` with `-bp)`
   - `(W/O Hu. Ident.)` with `(without human identifier)`
   - `(Hu. Ident.)` with `(human identifier)`

   Leave `attributes.reported_name` as printed. In `attributes.version`, set `rna-splicing-20261011-alavi2026-protocol-opa1-evaluation` and `-opa1-extended-positive-calls` to `Table III`, and `-protocol-multigene` to `Table IV`.
3. `rna-splicing-20261011-alavi2026-source-article`, `attributes.limitations`: append
   "Four printed accuracies differ from those computed from the same row's counts: Table III Borzoi (128-bp) 89.1% (counts give 89.8%); Table IV AlphaGenome (either module) 71.6% (70.5%), Borzoi (128-bp) 80.9% (81.4%) and Genos 10B 61.7% (61.2%)."
4. Same source: add `attributes.hash_scope`:
   "SHA-256 of one retrieval of the bioRxiv PDF. bioRxiv stamps the PDF when serving it (ModDate and the second document ID), so later retrievals differ. A reviewer retrieval on 2026-10-12 of the same length (1,823,372 bytes) had SHA-256 e22491e217c7c158528668b38bcb8b9855b89617b807c60b740795a204c84b0a and ModDate D:20261011221204-07'00'. All 168 Table III and IV cells in that copy match the stored results."
5. Append to `attributes.limitations` on `rna-splicing-20261011-alavi2026-protocol-multigene` and `use-case-mapping-rna-splicing-20261011-alavi2026-multigene`:
   "Genos 10B ClinVar is fine-tuned on ClinVar labels and the benign controls are ClinVar variants; training overlap is not tested in the source."

Genos 10B row: confirmed as `ZhejiangLab/Genos-10B` (v1). Results B says "this optimized Genos 10B configuration outperformed both the fine-tuned ClinVar model and the extended-species v2 iteration (Table III; ... Supplementary Table III)". Origin `independent_paper` confirmed: single author at 712 North Inc., who developed none of the models. The equity disclosure concerns 712 North only. Both judgements are confirmed as `proxy`. `reviewed_evaluations` should list the 12 evaluations on each protocol. Results reviewed on this source must not use the `source-hash-verification` method; use `pdf-text-parse` and `independent-cell-check`.

Answers to the collector's questions that concern this batch:

5. Alavi. Genos 10B is v1, confirmed. Both Table IV mismatches are confirmed, and I found four more accuracy cells that disagree with their counts (correction 3). The `proportion` concept with a qualifier for type II error and positive-call rates is acceptable. A false-negative-rate concept would not respell an existing one, but adding it is not needed for this batch.

## Corrections applied

Applied by a separate Claude agent (not the reviewer) exactly as the reviewer specified, before the batch was added to the store.

1. Correction 1: rna-splicing-20261011-alavi2026-model-genos removed; both Genos configurations link configuration_of to lit-microbial-20261011-virobench-model-genos; coverage.json updated. The model record was not in claims.csv.
2. Correction 2: configuration, evaluation and result names use the reviewer's casing; reported_name is unchanged; protocol versions are 'Table III' and 'Table IV'.
3. Correction 3: the four accuracy mismatches appended to the source limitations.
4. Correction 4: hash_scope added to the source record with the reviewer's text.
5. Correction 5: the Genos 10B ClinVar training-overlap limitation appended to protocol-multigene and its judgement.
6. Results use the review method pdf-text-parse, independent-cell-check and automated-source-review, not source-hash-verification.
7. The pinned PDF is not archived and bioRxiv stamps each serving, so the batch was regenerated from the reviewer's 2026-10-12 retrieval (SHA-256 e22491e2..., the copy named in hash_scope). The extraction script accepts that hash as well as the pinned one; before any correction it produced a batch.jsonl byte-identical to the extracted one. Records stay bound to the pinned SHA-256.
8. Every correction is applied in the extraction script under extract/ (marked 'review correction N'), and batch.jsonl, claims.csv, use-case-links.json and coverage.json were regenerated by rerunning it. A field-by-field comparison with the extracted batch shows no change beyond the corrections and the review fields.
9. Reviewed records are source_checked. Each result and claim carries the reviewer's review block (method, reviewer, reviewer_note, date, artifact_sha256 and retrieval_url from the source record; the extraction method description is kept as method_note; the note points to this file and the dated review). Each reviewed judgement lists the reviewer's reviewed_evaluations.
10. extract/__pycache__/ deleted before this receipt was written.

## Records after correction

- claim: 2
- configuration: 12
- dataset: 3
- evaluation: 36
- protocol: 3
- result: 168
- source: 1

All records are source_checked.
