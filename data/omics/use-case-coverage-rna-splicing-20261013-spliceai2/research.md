# Research: SpliceAI2 (Jaganathan et al. 2026, bioRxiv v1)

Issue #127. Use cases: `use-case-patient-rna-splicing-validation` and `use-case-splicing-follow-up`. Extraction only, by Claude (Opus 5.5) research agent spliceai2-extract on 2026-10-13. Every record is `needs_review`; nothing is reviewed, reproduced or added to the store. Searches are in `data/omics/search-ledger.jsonl` (`search-spliceai2-20261013-*`) and the include decision in `data/omics/scope-audit.jsonl`.

## What the paper prints

There are no numbered tables. Model comparisons are printed as numbers in two places:

- Extended Data Fig. 2, a heatmap with every cell labelled: four models (SpliceAI, Pangolin, AlphaGenome, SpliceAI2) on five benchmark panels, overall and by region. Fig. 1d repeats the "All" column as bar labels.
- Bar labels in Figs. 3c, 3f and 4g, and a few values in the main text and Methods.

## Decisions

| Item | Decision | Reason |
| --- | --- | --- |
| Extended Data Fig. 2, top block (4 models x 17 cells) | Extracted, 68 results | Printed labels; the paper's main comparison (GTEx GT/AG auPRC and usage, GTEx sQTL auROC and effect size, OpenSplice MPRA) |
| Extended Data Fig. 2, ablation blocks (usage transform, minimum junction count) | Not extracted | Single human-only training variants of SpliceAI2, not released models; not needed for the use cases |
| Fig. 4g, GEL GT/AG auPRC (4 bars) | Extracted | Printed bar labels; patient blood RNA-seq evidence |
| Methods: AlphaGenome raw splice site score 0.63 (GTEx) and 0.45 (GEL) | Extracted as a separate AlphaGenome configuration | Printed; shows the comparator's sensitivity to scoring choice |
| GEL prioritised variants, 23 prioritised and 17 confirmed | Extracted (two counts) | Printed in the main text |
| Fig. 4f validation rates by score bin (n = 41,959) | Not extracted, gap | Bars without printed values |
| Fig. 3c (allele-count Spearman) and 3f (protein Pearson) | Extracted, 8 results | Printed bar labels; proxy evidence (selection, protein abundance) |
| Fig. 3a, 3b, 3d, 3e | Not extracted | No printed values except r = -0.50 for SpliceAI2 in 3d, which 3f repeats as -0.504 |
| 100kGP enrichment: 133 excess variants at OR 2 | Extracted (SpliceAI2 only) | Printed in text; the comparator value 114 is for an unnamed "next best model", so it is kept in a claim, not a result |
| Fig. 4b, 4c, 4d, 4e | Not extracted | Curves and bars without printed model values; 15% burden share kept in a claim |
| Tissue-specific fine-tune: r = 0.44, 0.58, 0.51 | Extracted | Printed in text and Fig. 2b |
| SF3B1 uveal melanoma r = 0.49; myotonic dystrophy mean r = 0.26 | Extracted | Printed in text |
| Myotonic dystrophy r = 0.42 | Claim only | The text does not say which condition pair |
| Extended Data Fig. 4a and 4c | Claim only | Training-strategy ablation and a ridge-regression check, not model comparisons |
| Fig. 1c top-transcript accuracy (0.77, 0.78, 0.82) | Claim only (82% vs 78% from text) | Human-only ablation models |

## Modelling choices

- One family model record for SpliceAI2 and four configurations: the two-model ensemble used for all variant benchmarks, and three fine-tunes (48 GTEx tissues, SF3B1 uveal melanoma, myotonic dystrophy).
- Comparators reuse the existing family models `catalog-model-spliceai`, `catalog-model-pangolin` and `catalog-model-alphagenome`. The paper scores them in different ways for different analyses, so each scoring setup is its own configuration: position-resolved (GT/AG, sQTL, UK Biobank), standard (population and rare-disease analyses), AlphaGenome raw composite (the paper's chosen score) and raw splice site, and the scores released with OpenSplice.
- Region strata of Extended Data Fig. 2 are results on the same evaluation, told apart by `metric_qualifier` ("all variants", "exonic variants", ...). Stratum sizes are not printed.
- Figs. 3c and 3f print negative correlations where the paper says more negative is better, so `metric_direction` is `lower` for those 8 results.
- Every evaluation is `author_reported`. AlphaGenome was run by Oxford co-authors; the comparator OpenSplice scores were made by the OpenSplice authors but the comparison was run by the SpliceAI2 authors.

## Relevance judgements (drafts, `needs_review`)

| Claim | Use case | Protocol | Relevance |
| --- | --- | --- | --- |
| `use-case-mapping-rna-splicing-20261013-spliceai2-gel-gtag` | patient-rna-splicing-validation | GEL GT/AG cryptic activation (auPRC) | proxy |
| `use-case-mapping-rna-splicing-20261013-spliceai2-gel-prioritised` | patient-rna-splicing-validation | GEL prioritised variants confirmed in RNA-seq | proxy |
| `use-case-mapping-rna-splicing-20261013-spliceai2-opensplice` | splicing-follow-up | OpenSplice MPRA (Spearman) | proxy |

The issue calls the GEL blood RNA-seq evaluation "closest to direct evidence". It is graded proxy to match the existing Drost et al. 2025 judgement: the systems take DNA variants, not patient RNA, and the endpoint covers only GT/AG-creating variants. A reviewer may decide otherwise. The proposed `assessed_by` links are in `use-case-links.json` and are not applied.

## Things a reviewer should judge

1. Relevance grade of the GEL GT/AG judgement (proxy or direct).
2. Whether the training overlap (all human genes except chromosomes 21 and 22; GTEx in recount3 training data) should be a source evidence concern that blocks comparison, rather than a limitation. It affects SpliceAI2 only, so comparisons with SpliceAI, Pangolin and AlphaGenome may favour SpliceAI2.
3. OpenSplice: the Methods say comparator scores were taken from the OpenSplice release, but also that the AlphaGenome configuration was chosen across "eight evaluations", which may include OpenSplice. The settings of the released scores are not described.
4. Whether the 17 of 23 confirmation count should carry `true-positive-count` or `count`.
5. The baseline for both use cases (FRASER/OUTRIDER with a legacy splice-site vote; MaxEntScan) is not evaluated in this paper, so no comparison here scores a baseline against a machine-learning method (see issue #121).

## Proposed summary additions (not applied)

The two use-case summaries are reviewed and pinned; adding these judgements will not withhold them, but they will not mention SpliceAI2 until someone updates them. Suggested text, every number traceable to a result in this batch:

- Patient RNA: "Jaganathan et al. (2026, preprint), the SpliceAI2 developers, scored four DNA predictors on rare variants that create a GT or AG dinucleotide in 5,435 Genomics England rare-disease participants with blood RNA-seq, against cryptic junctions seen in the participants' RNA (3,065 cryptic gains, 1,775,800 nulls). auPRC was 0.59 for SpliceAI2, 0.48 for SpliceAI, 0.40 for Pangolin and 0.36 for AlphaGenome (0.45 with AlphaGenome's raw splice site score). Of 23 rare variants SpliceAI2 prioritised in phenotype-matched panel genes, 17 showed the predicted splicing change in RNA-seq; no other tool was put through this step. SpliceAI2 was trained on all human genes except chromosomes 21 and 22, the data are controlled access, and no rule-based splice-site scorer was compared."
- Splicing follow-up: "On the OpenSplice reporter assay (283,121 substitutions in 599 exons), the SpliceAI2 developers report Spearman correlations with measured exon-inclusion change of 0.59 for SpliceAI2, 0.55 for SpliceAI, 0.53 for Pangolin and 0.49 for AlphaGenome, using the comparator scores released with OpenSplice. This is a rank correlation over all substitutions, not precision among variants chosen for an experiment."

## Record counts

| Kind | Records |
| --- | --- |
| claim | 11 (8 descriptive, 3 relevance judgements) |
| configuration | 13 |
| dataset | 10 |
| evaluation | 39 |
| model | 1 |
| protocol | 13 |
| result | 90 |
| source | 5 |
| total | 182 |

## Validation and next step

The batch is not in the store. As a trial, `npm run records -- add` accepted all 182 records (attribute registry, vocabularies and SHACL shapes), and with them in the store `npm test` (518 tests), `npm run typecheck` and `npm run build` passed. The trial store changes and build outputs were then reverted. After `review-evidence` writes `review.json`, the reviewer adds the batch with `npm run records -- add data/omics/use-case-coverage-rna-splicing-20261013-spliceai2/batch.jsonl data/omics/use-case-coverage-rna-splicing-20261013-spliceai2` and applies the links in `use-case-links.json`.

To rebuild the batch: `python3 -I extract/build_batch.py <biorxiv-v1.full.pdf> <supplementary-table-1.tsv> .` (needs poppler; checks both hashes).
