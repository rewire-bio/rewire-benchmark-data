# Review: use-case-coverage-ctdna-helzer2025-20261011, 2026-10-12

Reviewer: Claude (Opus 5.5) review agent `reviewer-ctdna`, separate from the extracting agent `uc-ctdna`. No human review claimed. Source transcription is not reproduction. The full review, covering all five plasma ctDNA batches and the two use-case summaries, is `docs/reviews/use-cases/plasma-ctdna-use-cases-2026-10-12.md`.

## Reviewer's report (verbatim)

| Batch | Verdict |
| --- | --- |
| `use-case-coverage-ctdna-helzer2025-20261011` | Approved with corrections (H1 to H4) |

### All batches

A1. Delete `extract/__pycache__/` in all five batch folders before the review receipt is written; compiled bytecode should not be hashed into `review.json` or committed.

A2. Locators of the form `Results P32`, `Methods P59` count `<p>` elements of the JATS XML from zero in document order, front matter included (checked: Zeng `P32` is the paragraph beginning "We next assessed the generalization", Helzer `P12` begins "In the UW cohort, we found that the FoundationOne Liquid CDx panel", Fragmentia-AI WGS `P19` begins "We then assessed the generalizability"). The convention is stated nowhere. In the four JATS source records (`ctdnalit-20261011-zeng2026-source-article`, `ctdnalit-20261011-helzer2025-source-article`, `ctdnalit-20261011-fragmentia2026-source-article`, `ctdnalit-20261011-fragmentiawgs2026-source-article`) replace `attributes.source_locator`

`Full artifact bytes; per-record locators on each record`

with

`Full artifact bytes; per-record locators on each record. 'Pn' is the zero-based index of the <p> element in document order in this JATS XML, front matter included.`

### Helzer et al. 2025

H1. The UW commercial block is printed `Foundation One CDx` in Supplementary Table S2 (rendered page 9 checked), not `FoundationOne Liquid CDx`; the article text (Results P11 to P12) names the subset FoundationOne Liquid CDx for both cohorts, so the label in the table looks like a slip, but locators must quote what is printed. In every record of the batch and in `claims.csv`, replace the string

`Supplementary Table S2 (PDF caption), block 'FoundationOne Liquid CDx'`

with

`Supplementary Table S2 (PDF caption), block 'Foundation One CDx' (printed label; the article names this subset FoundationOne Liquid CDx)`

(131 results and the `version` of `ctdnalit-20261011-helzer2025-protocol-uw-foundationone`). Leave the Table S1 locators and all qualifiers unchanged. Append to `attributes.limitations` of `ctdnalit-20261011-helzer2025-protocol-uw-foundationone`: `Supplementary Table S2 prints this block as 'Foundation One CDx'; the article text (Results P11-P12) names the subset FoundationOne Liquid CDx (309 genes; 77% of them available on the UW panel).`

H2. The limitation `One-vs-rest AUROCs come from one multinomial model per metric; the 'Normal' column is the healthy-versus-all-cancer AUROC.` states more than the source. Methods P23 says GLMnet multinomial regression "was used for cancer type and cancer vs. healthy predictions" and does not say whether the Normal column comes from the multinomial model or a separate binary model. In all eight protocols and both judgements replace it with

`Methods P23 names GLMnet multinomial logistic regression for cancer-type and cancer-vs-healthy predictions; whether the 'Normal' (healthy vs all cancers) AUROC comes from the multinomial model or a separate binary model is not stated.`

Also append to the same `limitations` arrays: `The Figure 4 and 5 legends call the plotted value the average AUROC of 25 repeats; the table captions and Methods P23 say median. Values here follow the tables.`

H3. Judgement endpoints miscount the metrics (12 metrics plus All Combined in GRAIL; plus Griffin in UW). In `use-case-mapping-ctdna-lit-20261011-helzer2025-grail-full` replace `for 13 fragmentomic metrics` with `for 12 fragmentomic metrics and their combination`; in `use-case-mapping-ctdna-lit-20261011-helzer2025-uw-full` replace `for 14 fragmentomic metrics` with `for 12 fragmentomic metrics, their combination and Griffin`. In both rationales replace `Compares many published fragmentomic metric classes` with `Compares many fragmentomic metric classes, adapted to exon panels by the authors,`.

H4. Origin split confirmed (question 3): E1 SE is the authors' 2023 panel metric (Results P1 and P3: "We recently reported ... the entropy of fragmentation sizes at the exon nearest to a gene's transcription start site"), All Exons SE extends it and All Combined is the authors' model, so `author_reported`; the other metrics are re-implementations of other groups' WGS metrics and Griffin (Doebley, Ha et al.; no author overlap with the 27 Helzer authors), so `independent_paper`, consistent with the stored Hou et al. 2024 evaluations. The commercial-panel subsets (question 3) should not be mapped: they answer a different question (which genes a commercial panel retains) and the full-panel judgements already cover the comparison. Leave them as stored results without `assessed_by` links.

## Corrections applied

Applied by the extractor's scripts as the reviewer specified, before the batch was added to the store. Where the reviewer gave text, it is used verbatim.

1. A1: extract/__pycache__/ deleted before the receipt was written.
2. A2: the article source's source_locator now states the zero-based <p> convention, in the reviewer's words.
3. H1: the block string replaced in the 130 UW FoundationOne result locators, the protocol version and claims.csv; the reviewer's limitation appended to ctdnalit-20261011-helzer2025-protocol-uw-foundationone. Table S1 locators, evaluation locators (which do not contain the replaced string) and qualifiers unchanged.
4. H2: the multinomial limitation replaced, and the 25-repeats limitation appended, in all eight protocols and both judgements.
5. H3: endpoint metric counts and the rationale wording of both judgements replaced as written.
6. H4: no change (origin split confirmed; commercial-panel subsets left unmapped).
7. Records not otherwise named are source_checked. Each result, descriptive claim and judgement carries the reviewer's review block (method, reviewer, reviewer_note, date and note; the extraction note moved to method_note). Each judgement lists the reviewer's reviewed_evaluations.
8. Corrections were applied in the extraction scripts under extract/ (marked with their review item), and batch.jsonl, claims.csv and use-case-links.json were regenerated from the pinned artifacts; coverage.json was updated to match.

Form change after the review, not a review item: extract/common.py now writes missing_metadata keys in sorted order, as the store keeps them (shared/omics/attributes.ts normalizeAttributes). No record in this batch changed. The receipt was rewritten for the new file hashes.

## Records after correction

- claim: 3
- configuration: 14
- dataset: 2
- evaluation: 105
- method: 14
- protocol: 8
- result: 790
- source: 2

## Judgements

- `use-case-mapping-ctdna-lit-20261011-helzer2025-grail-full`: proxy, 13 reviewed evaluations
- `use-case-mapping-ctdna-lit-20261011-helzer2025-uw-full`: proxy, 14 reviewed evaluations
