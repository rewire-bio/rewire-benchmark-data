# Research: cell-type annotation transfer use-case pass, 2026-10-09

Use case: `use-case-cell-type-annotation-transfer` ("Which annotation workflow can label my new dataset reliably and recognise unsupported cell populations?"). Existing judgements, all proxy, rest on Abdelaal et al. 2019 and scTab; neither source is duplicated here.

Goal: independent comparisons of several annotation methods across datasets with printed per-method values, especially rejection of unseen cell types; macro-F1 or per-population metrics preferred over accuracy.

Bounds: cutoff 2026-10-09; 25 queries budgeted, 9 used; at most 3 sources, 1 extracted. Lane `cells-spatial`. Kept lean as asked.

## Queries

All 9 are in `data/omics/search-ledger.jsonl` as `search-use-case-cell-type-cells-spatial-q1` to `q8` and one `source-resolution` entry.

| # | Query (shortened) | Outcome |
| --- | --- | --- |
| 1 | novel-cell rejection benchmarks with CellTypist, scANVI, SingleR, Azimuth, scArches | Huang et al. 2021 (figure-only) |
| 2 | independent scGPT and Geneformer annotation benchmarks against simple baselines | Boiarsky et al. 2023 and two preprints as leads |
| 3 | Europe PMC: annotation benchmarks in titles | Ma et al. 2021 (results in an R data file) |
| 4 | Europe PMC: annotation benchmarks with unknown or novel cells | Developer method papers only |
| 5 | Boiarsky et al., logistic regression against scBERT and scGPT | Preprint tables are images |
| 6 | Europe PMC: foundation-model annotation benchmarks (too narrow) | 1 hit |
| 7 | Europe PMC: same, broadened | Wu et al. 2025 extracted; scEval and BioLLM screened |
| 8 | unseen-type detection benchmarks with supplementary tables | Developer method papers only |
| 9 | bioRxiv API: Boiarsky et al. | Resolution |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Wu et al. 2025 (scFM-Bench), Supplementary Tables S2-S3 | Extract all 92 cells | Independent cross-study transfer between two atlases for six foundation models and 17 ensembles, with macro-F1 |
| Wu et al. 2025, intra-dataset and novel-cell-type results | Not extracted | Figure-only (Fig. 3, Fig. S22) |
| Huang et al. 2021 | Excluded | Figure-only |
| Ma et al. 2021 | Excluded | Results stored in an R data file, not a printed table |
| Boiarsky et al. 2023 | Excluded | Image tables in the preprint |
| scEval (Liu et al. 2026), BioLLM (2025) | Excluded | Qualitative or descriptive tables |
| mtANN, scDOT, HiCat, MiCAS, scParadise | Not opened | Developer method papers |

## Relevance judgements

Two, both `proxy` and status `needs_review`, as strata of `wu2025-cross-atlas` (Tabula Sapiens to HLCA, HLCA to Tabula Sapiens), headline `macro-f1`. They are proxy because the truth labels are atlas annotations (use-case exclusion), only the 14 shared cell types are scored so rejection of unsupported populations is not tested, and the classifier is OnClass on frozen embeddings rather than an end-to-end annotation workflow.

## Systems

Six single-model configurations (OnClass on zero-shot embeddings from scGPT, scFoundation, Geneformer, UCE, LangCell and scCello) and 17 ensembles (15 pairwise logit sums, full logit aggregation and full majority voting). scGPT, scFoundation and Geneformer reuse the catalogue model records. UCE, LangCell and scCello are new family records, because the only existing UCE record is a scTab-specific method identity. Ensembles carry `uses_model` links to their members.

## Things a reviewer should judge

1. The evidence concern on the supplement: the text and both tables disagree on which full-ensemble strategy wins on which metric.
2. Origin `independent_paper` for all rows rests on the source not stating any developer relationship.
3. Accuracy and macro-F1 diverge sharply (accuracy above 0.6, macro-F1 0.08-0.30). The judgements headline macro-F1 as asked.
4. No conventional baseline is in the tables, so these results cannot show whether a foundation model beats a simple classifier here.

## Coverage

Bounded and lean. Not covered: printed rejection metrics for CellTypist, scANVI, SingleR, Azimuth or scArches; cross-species transfer; Boiarsky et al.'s published tables; scEval's supplementary zip; 2026 hits beyond their titles.
