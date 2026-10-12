# Review: use-case-coverage-ctdna-cpgpt2026-20261011, 2026-10-12

Reviewer: Claude (Opus 5.5) review agent `reviewer-ctdna`, separate from the extracting agent `uc-ctdna`. No human review claimed. Source transcription is not reproduction. The full review, covering all five plasma ctDNA batches and the two use-case summaries, is `docs/reviews/use-cases/plasma-ctdna-use-cases-2026-10-12.md`.

## Reviewer's report (verbatim)

| Batch | Verdict |
| --- | --- |
| `use-case-coverage-ctdna-cpgpt2026-20261011` | Approved with corrections (C1 to C2) |

### All batches

A1. Delete `extract/__pycache__/` in all five batch folders before the review receipt is written; compiled bytecode should not be hashed into `review.json` or committed.

A2. Locators of the form `Results P32`, `Methods P59` count `<p>` elements of the JATS XML from zero in document order, front matter included (checked: Zeng `P32` is the paragraph beginning "We next assessed the generalization", Helzer `P12` begins "In the UW cohort, we found that the FoundationOne Liquid CDx panel", Fragmentia-AI WGS `P19` begins "We then assessed the generalizability"). The convention is stated nowhere. In the four JATS source records (`ctdnalit-20261011-zeng2026-source-article`, `ctdnalit-20261011-helzer2025-source-article`, `ctdnalit-20261011-fragmentia2026-source-article`, `ctdnalit-20261011-fragmentiawgs2026-source-article`) replace `attributes.source_locator`

`Full artifact bytes; per-record locators on each record`

with

`Full artifact bytes; per-record locators on each record. 'Pn' is the zero-based index of the <p> element in document order in this JATS XML, front matter included.`

### Xu and Feng 2026 (CpGPT)

C1. Source hash could not be re-verified. A fresh download of `https://www.medrxiv.org/content/10.64898/2026.07.26.26358979v1.full.pdf` on 2026-10-12 returned 2,761,577 bytes with SHA-256 `3d37b32e8ff782201ed8ee6677a01808d4f8c86eea70350a530dde7306cab7c9`, against the pinned 2,761,568 bytes and `369746bf...e7366961e`. Its PDF CreationDate is `D:20261011200812-07'00'` (2026-10-12T03:08Z, after the pinned retrieval at 21:49:59Z), so medRxiv regenerates the file and the pinned bytes are not retrievable. The text layer of my copy matches every one of the 15 extracted values, their intervals, the asserted sentences and the footnote. Do not change `artifact_sha256`. Add to `ctdnalit-20261011-cpgpt2026-source-preprint`:

`"hash_scope": "artifact_sha256 describes one retrieval (2026-10-11T21:49:59Z). medRxiv regenerates this PDF: a reviewer download on 2026-10-12 had 2,761,577 bytes, SHA-256 3d37b32e8ff782201ed8ee6677a01808d4f8c86eea70350a530dde7306cab7c9 and PDF CreationDate 2026-10-11T20:08:12-07:00. The reviewer's copy's text layer matched every extracted value. The licence does not allow archiving."`

and record the reviewer copy's hash as the review `artifact_sha256` on the 15 results and on the judgement.

C2. `coverage.json` `remaining_gaps` item 2 says per-split values are not printed for the classical models; they are printed for CpGPT (Results: validation 0.8942, 1.0000, 0.9520; test 1.0000, 1.0000, 0.9712) and were not extracted. Append ` CpGPT's per-split validation and test AUROCs are printed in the Results text and were not extracted.`

Answer to question 6: confirmed. The Methods say DMR discovery "was conducted using all 300 samples in the source cohort" and each test partition is "approximately 10%" with few controls. Origin is right: neither author is a CpGPT developer (Yili Xu, USC; Qianxi Feng, MicroTrace BioAI), the baselines are their own. Qianxi Feng is not Felix Y. Feng of the Helzer author list.

## Corrections applied

Applied by the extractor's scripts as the reviewer specified, before the batch was added to the store. Where the reviewer gave text, it is used verbatim.

1. A1: extract/__pycache__/ deleted before the receipt was written.
2. C1: artifact_sha256 unchanged; the reviewer's hash_scope added to the source; the 15 results and the judgement carry the reviewer copy's hash as review artifact_sha256, and their review method omits source-hash-verification.
3. C2: the reviewer's sentence appended to coverage.json remaining_gaps item 2.
4. Records not otherwise named are source_checked. Each result, descriptive claim and judgement carries the reviewer's review block (method, reviewer, reviewer_note, date and note; the extraction note moved to method_note). Each judgement lists the reviewer's reviewed_evaluations.
5. Corrections were applied in the extraction scripts under extract/ (marked with their review item), and batch.jsonl, claims.csv and use-case-links.json were regenerated from the pinned artifacts; coverage.json was updated to match.

Form change after the review, not a review item: extract/common.py now writes missing_metadata keys in sorted order, as the store keeps them (shared/omics/attributes.ts normalizeAttributes). This reorders the keys on 5 evaluations in batch.jsonl; no value, reason or note changed. The receipt was rewritten for the new file hashes.

## Records after correction

- claim: 1
- configuration: 5
- dataset: 1
- evaluation: 5
- method: 2
- protocol: 1
- result: 15
- source: 1

## Judgements

- `use-case-mapping-ctdna-lit-20261011-cpgpt2026-split-runs`: proxy, 5 reviewed evaluations
