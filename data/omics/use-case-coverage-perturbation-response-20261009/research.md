# Research: genetic perturbation response use-case pass, 2026-10-09

Use case: `use-case-genetic-perturbation-response` ("Which prediction methods and controls should I test before using expression predictions to plan genetic perturbation experiments?"). Existing judgements, all proxy: GEARS Supplementary Table 6 MSE and Pearson DE on Norman, and PertEval-scFM AUSPC. Neither of their sources is duplicated here.

Goal: independent comparisons of several perturbation-response predictors against simple baselines on the same Perturb-seq data, with per-method values printed in tables, and the baselines and controls recorded as configurations.

Bounds: cutoff 2026-10-09; 25 queries budgeted, 5 used; at most 3 sources, 1 extracted. Lane `cells-spatial`. Kept lean as asked.

## Queries

| # | Query (shortened) | Outcome |
| --- | --- | --- |
| 1 | Ahlmann-Eltze 2025, deep learning versus linear baselines | Opened: figure-only, with per-perturbation Source Data |
| 2 | Csendes 2025 foundation cell model benchmark | Extracted |
| 3 | Systema control-aware evaluation | Opened: figure-only |
| 4 | Europe PMC: perturbation prediction benchmarks 2024-2026 | Li et al. 2026 opened (figure-only); 2026 preprints and a closed Nature Methods paper noted |
| 5 | independent GEARS, scGPT, CPA, linear and mean baseline benchmark tables | Nothing new; PerturBench is already stored as tasks |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Csendes et al. 2025, Supplementary Table 2 | Extract all 352 printed cells | scGPT and scFoundation against a Train Mean control and 12 feature-based regressors on the same unseen perturbations in Adamson, Norman, Replogle K562 and Replogle RPE1 |
| Csendes et al. Supplementary Table 1 | Dataset attributes and one claim | Split sizes |
| Csendes et al. Supplementary Table 3 | Not extracted | The metric column is unlabelled; the Supplementary Figure 1 legend says "Pearson delta metrics", but a legend is not taken as a column label |
| Ahlmann-Eltze et al. 2025 | Not extracted | The main independent comparison, but there are no tables: per-method results are figures and the Source Data are thousands of per-perturbation rows that would need aggregation |
| Systema (2025) | Not extracted | Method comparisons are figure-only |
| Li et al. 2026 (Science Advances) | Not extracted | Results are figure-only |
| PerturBench (already in store) | Not judged | Its combination tasks are `task` records; `assessed_by` needs a protocol |

## Relevance judgements

Four, all `proxy` and status `needs_review`, grouped as strata of `csendes2025-perturbseq` (Adamson, Norman, Replogle K562, Replogle RPE1), headline `pearson-delta`. They are proxy for the same reason as the three existing judgements: expression-prediction scores do not establish mechanism or experimental prioritisation. The comparison is on the GEARS perturbation-exclusive splits within one cell line per dataset, so it stays inside the GEARS usage scope; Norman includes combinations seen in training as singles or not at all.

## Configurations

Fifteen. Twelve feature-based regressors (random forest, elastic net and kNN, each with Gene Ontology, scELMO, scFoundation or scGPT embeddings of the perturbed gene); the Train Mean control; scGPT v0.2.1 fork (commit 7301b51) fine-tuned per dataset; and scFoundation (commit 69b0710) embeddings in GEARS, fine-tuned per dataset. The two foundation models link to the existing `catalog-model-scgpt` and `catalog-model-scfoundation` records.

## Things a reviewer should judge

1. Results paragraph 8 cites Supplementary Table 1 for the Pearson Delta DE and target-gene results, which are in Supplementary Table 2.
2. The 8 blank Wilcoxon cells for the foundation models are blank in the source and get no result.
3. The 16 Pearson Delta values quoted in Results paragraph 6 match the table to three decimals; the extractor asserts this.
4. Baselines are `author_reported`; the reproduced foundation models are `independent_paper`.
5. Whether a Pearson Delta difference such as Norman Train Mean 0.557266 against scGPT 0.553838 means anything without spread. The protocols say no spread is printed.

## Coverage

Bounded and lean. Not covered: Ahlmann-Eltze et al. values, Systema control-aware metrics, 2026 preprints on baseline gaps and leakage-aware splits, the closed Nature Methods 2026 generalisation benchmark, and any measure of experimental hit rate.
