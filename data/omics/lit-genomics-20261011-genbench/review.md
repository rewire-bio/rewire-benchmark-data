# Review: lit-genomics-20261011-genbench, 2026-10-11

Reviewer: Claude review agent `reviewer-gen-2`, independent of the extractor `lit-genomics`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

genbench (lit-genomics-20261011-genbench @ ce56c11): APPROVED WITH CORRECTIONS. All values are correct.

Checks:
- Source: SHA-256 24105d26… matches the re-downloaded arXiv v2 PDF.
- Values: I wrote my own parser and compared all 381 results across Tables 3-8 and 10 (printed and numeric). 0 mismatches and no missing cells. The 12 '-' cells in Table 7 have numeric_value null with an 'unavailable' note, which is correct.
- I also checked a seeded stratified sample of 61 cells (every table, all 13 model columns) against the rendered pages 6, 7 and 15. All matched.
- Metrics and directions match the headers: accuracy as a fraction, Pearson, AUROC, Spearman, MSE lower.
- Origin independent_paper is right: the Westlake/Zhejiang/USC authors developed none of the evaluated models.
- claims.csv agrees with the batch. Scope fits.

Corrections:
1. Configuration `lit-genomics-20261011-genbench-config-nt`: retarget configuration_of from `discovery-model-nucleotide-transformer` to `catalog-model-nt-v2`. Table 9 gives 29 layers, width 1024 and 498M parameters, which is the NT-v2 500M architecture. NT-v1 500M has 24 layers and width 1280. The text's NT scaling study (50/100/500M) also uses v2 sizes. This affects 54 evaluations.
2. Duplicates inside the batch. Table 10 rows "Human Splice Site Detection, dataset Reconstructed" and "Virus Covid Variant Classification, dataset Covid" are single-dataset tasks and repeat the Table 4 cells exactly. Fix: remove those 14 results and evals (`...-genbench-{result,eval}-<model>-short-human-splice-site-detection-reconstructed` and `...-short-virus-covid-variant-classification-covid`), plus their 2 protocols and 2 datasets. Then add "also Table 10" to the Table 4 locators.
3. comparison.aggregation "Top-1 over runs" on all 364 evals reads more into the source than it says. The paper never defines Top-1, and for classification it is ordinary top-1 accuracy. Set it to null with missing_metadata reason unreported, or to "Top-1 as printed (undefined)". The protocol text "best (Top-1) score" needs the same change.
4. Source limitations or evidence_concerns should record three things:
   - The NeurIPS checklist answers "error bars reported: Yes", but no table prints any.
   - Table 3 is called short-range in its caption and long-range in Section 4.2.
   - The Table 8 caption names 3 models while the table has 5.
   - In addition, Table 4 multi-dataset rows are means of the Table 10 rows (the existing metric_qualifier only says "task-level value as printed").
5. Quality, not blocking: the 54 dataset records are bare ("GenBench dataset X."). Table 2 gives training size, test size, length and task type for each task, and these should go into population or description. Optional informational `same_data_as` links: `short-mouse-enhancers` to `reported-dataset-f0bf60a62ad7c3`, and `short-human-core-promoter-detection-*` to `reported-dataset-8e9488896becd4`.

Duplicates against the store and PR #107: no GenBench source or results exist on main or in #107. The DNABERT-1 config depends on `lit-genomics-20261011-gfmbench-model-dnabert`, so the gfmbench batch must ship with this one (the same applies to ntbench).

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store.

1. Configuration lit-genomics-20261011-genbench-config-nt retargeted to catalog-model-nt-v2 (Table 9 gives the NT-v2 500M architecture).
2. Table 10 rows for Human Splice Site Detection (Reconstructed) and Virus Covid Variant Classification (Covid) removed (14 results and evaluations, 2 protocols, 2 datasets); the Table 4 locators say 'also Table 10'.
3. comparison.aggregation is 'Top-1 as printed (undefined)' and the protocol text no longer says 'best'.
4. Source limitations record the unprinted error bars, the Table 3 short-range/long-range conflict, the Table 8 caption naming 3 of 5 models, and that Table 4 multi-dataset rows are means of Table 10 rows.
5. Datasets carry their Table 2 type, training size, testing size and length; informational same_data_as links to reported-dataset-f0bf60a62ad7c3 (Mouse Enhancers) and reported-dataset-8e9488896becd4 (Human Core Promoter Detection).

## Records after correction

- benchmark: 1
- configuration: 10
- dataset: 52
- evaluation: 350
- model: 3
- protocol: 52
- result: 367
- source: 1
