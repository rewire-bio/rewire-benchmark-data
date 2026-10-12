# Review: use-case-coverage-ctdna-fragmentia2026-20261011, 2026-10-12

Reviewer: Claude (Opus 5.5) review agent `reviewer-ctdna`, separate from the extracting agent `uc-ctdna`. No human review claimed. Source transcription is not reproduction. The full review, covering all five plasma ctDNA batches and the two use-case summaries, is `docs/reviews/use-cases/plasma-ctdna-use-cases-2026-10-12.md`.

## Reviewer's report (verbatim)

| Batch | Verdict |
| --- | --- |
| `use-case-coverage-ctdna-fragmentia2026-20261011` | Approved with corrections (F1 to F3) |

### All batches

A1. Delete `extract/__pycache__/` in all five batch folders before the review receipt is written; compiled bytecode should not be hashed into `review.json` or committed.

A2. Locators of the form `Results P32`, `Methods P59` count `<p>` elements of the JATS XML from zero in document order, front matter included (checked: Zeng `P32` is the paragraph beginning "We next assessed the generalization", Helzer `P12` begins "In the UW cohort, we found that the FoundationOne Liquid CDx panel", Fragmentia-AI WGS `P19` begins "We then assessed the generalizability"). The convention is stated nowhere. In the four JATS source records (`ctdnalit-20261011-zeng2026-source-article`, `ctdnalit-20261011-helzer2025-source-article`, `ctdnalit-20261011-fragmentia2026-source-article`, `ctdnalit-20261011-fragmentiawgs2026-source-article`) replace `attributes.source_locator`

`Full artifact bytes; per-record locators on each record`

with

`Full artifact bytes; per-record locators on each record. 'Pn' is the zero-based index of the <p> element in document order in this JATS XML, front matter included.`

### Fragmentia-AI (Cell Reports Medicine 2026)

F1. Origin on the 18 baseline evaluations is wrong. The origin vocabulary defines `author_reported` as "reported by the authors of the evaluated method". Geneseeq did not develop DELFI, Griffin, FRAGMA, FDI or the nucleosome features; they re-implemented them (Results P44: "we implemented the feature extraction pipelines for each method"). The store records competitor baselines run by another method's developers as `independent_paper` (UNITE's ichorCNA comparator `ctdnafrag-20261009-eval-wang2026-ichorcna-tf-*`, Hou et al. 2024), and Helzer does the same in this pass. Set `attributes.origin` to `independent_paper` on `ctdnalit-20261011-fragmentia2026-eval-{delfi,griffin,fragma,fdi,nucleosome,subnucleosome}-{random-forest,xgboost,deep-learning}`. Keep `author_reported` on `ctdnalit-20261011-fragmentia2026-eval-fragmentia-ai-ulp-wgs`. In `sources.md` replace the Origin line with `Origin: the Fragmentia-AI evaluation is author_reported; the 18 baseline evaluations are independent_paper, because Geneseeq re-implemented methods it did not develop. The study is still a developer comparison: the baselines were re-implemented and run by the developers of the competing model.`

F2. The configuration parameters name a stored checkpoint the paper does not name. The article says the fragments are "processed ... through a DNABERT-2 architecture" with LoRA on the Wqkv layers; it does not say which pretrained weights, if any, initialise it. In `ctdnalit-20261011-fragmentia2026-config-fragmentia-ai-ulp-wgs` replace `attributes.parameters`

`DNABERT-2 backbone (catalog-model-dnabert-2) fine-tuned end to end with an attention-based MIL classifier on the ULP-WGS training cohort`

with

`DNABERT-2 architecture with LoRA on the Wqkv layers, trained end to end with an attention-based MIL classifier on the ULP-WGS training cohort; the paper does not name the pretrained weights, if any, that initialise it`

Do not add a `uses_model` link to `catalog-model-dnabert-2`.

F3. Append to `attributes.limitations` of `ctdnalit-20261011-fragmentia2026-protocol-ulp-wgs-heldout-auc` and of `use-case-mapping-ctdna-lit-20261011-fragmentia2026-ulp-wgs-heldout`: `The cohort has 1,245 non-cancer controls, the same number as the training cohort of the Fragmentia-AI WGS paper (Molecular Biomedicine 2026, Table S1) from the same company, so the two studies may share samples; neither paper says.`

Answers to question 4: the held-out split size is not printed (confirmed); 0.956 and 0.97 are both in Results P43 for what reads as the same quantity (confirmed, recorded); the p-value test is not named (confirmed); FRAGMA, FDI, nucleosome and subnucleosome are cited (refs 14 to 18) but not defined (confirmed). None of these blocks storage; all are in the limitations.

## Corrections applied

Applied by the extractor's scripts as the reviewer specified, before the batch was added to the store. Where the reviewer gave text, it is used verbatim.

1. A1: extract/__pycache__/ deleted before the receipt was written.
2. A2: the article source's source_locator now states the zero-based <p> convention, in the reviewer's words.
3. F1: origin set to independent_paper on the 18 baseline evaluations; the Fragmentia-AI evaluation stays author_reported; the Origin line in sources.md replaced (research.md updated to match).
4. F2: parameters of ctdnalit-20261011-fragmentia2026-config-fragmentia-ai-ulp-wgs replaced; no uses_model link.
5. F3: the reviewer's sample-overlap limitation appended to the protocol and the judgement.
6. Records not otherwise named are source_checked. Each result, descriptive claim and judgement carries the reviewer's review block (method, reviewer, reviewer_note, date and note; the extraction note moved to method_note). Each judgement lists the reviewer's reviewed_evaluations.
7. Corrections were applied in the extraction scripts under extract/ (marked with their review item), and batch.jsonl, claims.csv and use-case-links.json were regenerated from the pinned artifacts; coverage.json was updated to match.

Form change after the review, not a review item: extract/common.py now writes missing_metadata keys in sorted order, as the store keeps them (shared/omics/attributes.ts normalizeAttributes). This reorders the keys on 19 evaluations in batch.jsonl; no value, reason or note changed. The receipt was rewritten for the new file hashes.

## Records after correction

- claim: 1
- configuration: 19
- dataset: 1
- evaluation: 19
- method: 5
- protocol: 1
- result: 19
- source: 2

## Judgements

- `use-case-mapping-ctdna-lit-20261011-fragmentia2026-ulp-wgs-heldout`: proxy, 19 reviewed evaluations
