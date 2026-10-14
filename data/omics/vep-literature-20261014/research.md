# Research notes

Reviewed on 2026-10-14 (`docs/reviews/vep-literature-2026-10-14-review.md`); the review changes decisions 3 and 7 below and revises the judgements' limitations.

Scope: literature pass for variant effect predictors (VEPs), rewire-benchmark-data #153, #154 and #155. Cutoff 2026-10-14; budget 60 queries, 10 used (ledger entries `search-vep-lit-20261014-q01` to `q10`). Use cases considered: BRCA1/BRCA2 germline interpretation, rare-disease candidate ranking, unresolved rare-disease reanalysis, somatic small-variant oncogenicity, protein stability, splicing follow-up, regulatory variant and gene follow-up. The AVE predictor list was used only to know which names to look for; no record cites it.

Literature first: nothing was run. Two priority sources were extracted completely at the level chosen (below); everything else found is a recorded gap.

## What was already in the store

- ProteinGym: the NeurIPS 2023 paper tables (21 zero-shot models, supervised and indel tasks, `proteingym-task-*`), the AMFR assay row of the DMS-level Spearman CSV at 144fe22 (97 models, `uc20260930-proteingym-amfr-*`), Rewire's own AMFR runs, and the runner protocol `rewire-proteingym-v1-3-dms-substitutions` (upstream 144fe22, no evaluations).
- Clinical VEPs as methods from the somatic oncogenicity and BRCA passes (`somatic-oncogenicity-20261009-method-*`, `brca-20261009-method-*`), with configurations from Chen 2020, Lee 2026 and Cubuk 2021.
- Nothing from Livesey and Marsh.

## Added in this batch (3,364 records, all needs_review)

1. Livesey and Marsh 2025 (Genome Biol 26:104). Six protocols under one new benchmark: the DMS ranking on all 36 DMS sets (Table S3), direct-only and indirect-only (Table S5), SNV-accessible only (Table S6), SNV-accessible with gaps filled (Table S7), and the clinical AUROC ranking on 819 proteins (Table S8). 99 configurations (one per printed VEP label, plus 'CADD' and 'COSMIS' that appear only in S8), 570 evaluations, 667 results. Every value is the VEP's rank score (average pairwise win rate, 0-100), plus the top-5 win rate in Table S3; the 'proteins' column is kept as result coverage.
2. ProteinGym at 144fe22. All 18 metric columns of the zero-shot DMS substitutions Spearman summary for 97 models (1,746 results; the average carries the bootstrap standard error as uncertainty), and the three clinical AUC summaries (13 zero-shot substitution rows, 17 supervised substitution rows, 18 zero-shot indel rows). 27 new configurations for clinical labels with no ProteinGym configuration in the store; the 97 existing ProteinGym snapshot configurations are reused.
3. 27 new methods: 26 VEPs first seen in Livesey and Marsh 2025 (17 from #153, 6 from #154, plus PhD-SNP, iGEMME and mutationTCN) and the ProteinGym 'Hidden Markov Model' baseline. Descriptions use only what the paper's Table S2 says (type and prediction source).
4. 13 relevance judgements (all proxy, needs_review): 9 for rare-disease candidate ranking, 3 for BRCA1/BRCA2, 1 for protein stability.
5. One metric concept, `pairwise-win-rate`, in `data/vocab/metric.ttl`.
6. One `tables_not_extracted` claim on the Livesey supplement.

## Decisions a reviewer should check

1. **ProteinGym protocol reuse.** The DMS summary rows are assessed by the existing `rewire-proteingym-v1-3-dms-substitutions` protocol, because it is the same track at the same upstream commit and its documented aggregation matches `performance_DMS_benchmarks.py`. That record also carries Rewire runner recipes. If the reviewer prefers to keep runner and leaderboard apart, a separate protocol is the alternative.
2. **ProteinGym configuration reuse.** The 97 systems are the existing `uc20260930-proteingym-amfr-config-*` records. Despite the "amfr" prefix they are label-level snapshot configurations at 144fe22 ("Exact official CSV source-label configuration"), not AMFR-specific.
3. **Origin.** ProteinGym rows use `author_reported`, matching the existing ProteinGym evaluations; ProteinGym's authors computed most rows for models they did not develop. Livesey and Marsh rows use `independent_paper`.
4. **Printed values from the workbook.** All cells are General format and stored at up to 17 significant digits. `printed_value` is the shortest round-trip decimal of the stored number (for example `92.81631101` for CPT-1), with `raw_xml_value` and `workbook_number_format` kept. The paper text rounds (92.8%).
5. **Label mapping in Table S8.** 'CPT' is mapped to the CPT-1 configuration and 'fathmm-XF' to the FathmmXF configuration, each result carrying a `source_anomaly`. The text calls the top population-free clinical VEP CPT-1, and Table S2 has one Fathmm-XF row. 'CADD' in S8 gets its own configuration with version unreported, because S2 lists CADD 1.6 and 1.7 separately and S8 also prints CADD_1.7. 'COSMIS' has no row in S2 and is not mentioned in the text.
6. **MTBAN versus mutationTCN.** Table S2 cites Kim and Kim 2020 (Bioinformatics 36:2047, a temporal convolutional network) for 'mutationTCN' and gives the MTBAN server as the prediction source. It is recorded as a new method `mutationTCN`, not as MTBAN (#154).
7. **Identity choices.** MVP maps to `somatic-oncogenicity-20261009-method-mvp`, not `uc20260930-model-mvp` (a metabolomics model with the same name). fitCons maps to `somatic-oncogenicity-20261009-method-integrated-fitcons`; the paper does not say which dbNSFP fitCons score was used. SIFT4G maps to the SIFT family, as in the existing Chen 2020 and Lee 2026 configurations. ESM2 maps to `discovery-model-esm-2`. PolyPhen-2 HumDiv/HumVar, BayesDel and BayesDel_noAF, EVmutation epistatic/independent, and VARITY_R/ER are separate configurations of their families.
8. **Method types** on configurations are the collector's assignment: CPT-1, DeMaSk and Envision as supervised machine learning (the paper says they are trained on DMS data); protein language models as foundation models; conservation and alignment-generative models as specialist or conventional pipeline.
9. **Uncertainty.** ProteinGym's DMS bootstrap standard error is recorded as a standard error of the difference from the top model (10,000 resamples), from reading the scoring script at the same commit; whether that script produced this exact file is not recorded in the repository. The clinical files' `Bootstrap_standard_error_AUC` is recorded as `unresolved_spread`, because the clinical script was not read.
10. **Relevance.** All judgements are proxy. No judgement was added for unresolved reanalysis, somatic oncogenicity, splicing or regulatory follow-up; reasons are in `coverage.json`. The stability judgement points at the DMS protocol and tells users to read only the Function_Stability column.

## Source anomalies found

- Table S1 has no row 3 and blank assay descriptions for TPK1, SUMO1, UBE2I and CASP7, so the direct and indirect groups of Table S5 cannot be reconstructed from it.
- Table S2 types Rhapsody as "Clinical-trained," with a trailing comma; recorded as clinical-trained.
- The ProteinGym clinical zero-shot substitutions CSV repeats the `Model_rank` header, with an empty second column, and lists only 13 models.
- ProteinGym ranks AIDO Protein-RAG (16B) first and VenusREM second; both print 0.518.

## Not extracted (gaps)

- Pairwise win-rate matrices (S3, S8 bodies), bootstrap counts (S4) and all figures of Livesey and Marsh 2025, including the AUPRC ranking (Fig. S5, figure only).
- Livesey and Marsh 2023 and 2020 editions; the 2023 supplement could not be retrieved.
- CAGI6 Annotate-All-Missense (Hum Genet 2025) and Tabet et al. 2024 (Genome Biol): independent VEP benchmarks not in the store.
- Two 2026 preprints: missense predictors on activating cancer drivers, and gene identity in ClinVar benchmarks.
- Other ProteinGym summaries (zero-shot DMS AUC, MCC, NDCG, top recall; indel and supervised DMS; per-protein clinical files).
- Developer-reported results for the #155 non-coding predictors and PrimateAI-3D.

## Validation

- `extract/extract_vep.py` reruns deterministically from the pinned bytes.
- Dry-run of the `records -- add` validators (vocabularies, attributes, derivations, links) against the current store: passes.
- `records -- add` on a temporary copy of the repository (not this worktree): SHACL shapes conform; `records -- check`, `npm run test:fast` (370 tests) and `npm run build` pass on that copy.
- In this worktree: `npm run test:fast` and `npm run typecheck` pass. The batch is not in the store.
