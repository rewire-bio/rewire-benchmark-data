# Research: plasma ctDNA methylation use-case pass, 2026-10-09

Use case: `use-case-plasma-ctdna-methylation` ("Which measured methylation workflow detects tumour-derived plasma DNA and, where separately supported, identifies tissue of origin?"). Before this pass it had one judgement: the cfMethyl-Seq stacked ensemble's all-stage sensitivity at 97.9% specificity, a single result with no comparator.

Goal: published comparisons of several cfDNA methylation methods on the same plasma cohort or a shared in silico benchmark, with printed per-method values.

Bounds: cutoff 2026-10-09; budget 25 queries, 15 used; at most 3 sources extracted. Lane `genomics`. Worker: Claude (Opus 5.5) research agent; no human review claimed.

## Queries

The full entries are `search-use-case-ctdna-methylation-genomics-q1` to `q15` in `data/omics/search-ledger.jsonl`.

| # | Query (short form) | Channel | Outcome |
| --- | --- | --- | --- |
| 1 | cfDNA methylation deconvolution benchmark CelFiE MethAtlas UXM in silico tumour fraction | web search | DecoNFlow preprint, Sun et al. preprint, Hill et al. 2023 |
| 2 | "Systematic evaluation of cell type deconvolution methods for plasma cell-free DNA" published | web search | No journal version found this way |
| 3 | cfDNA methylation deconvolution benchmark (boolean) | Europe PMC | 525 hits, 40 screened; nothing new |
| 4 | bioRxiv API details for three preprints | bioRxiv API | Versions, licences; DecoNFlow XML blocked (429) |
| 5 | DOI lookups for two preprints | Europe PMC | DecoNFlow PPR1127337 (full text not served) |
| 6 | Jamshidi et al. 2022 title | Europe PMC | Found; not in PMC; publisher pages 403 |
| 7 | cfMeDIP-seq vs WGBS vs EM-seq same samples | web search | No detection-endpoint comparison |
| 8 | tissue-of-origin comparison CancerLocator CancerDetector cfSort | web search | Developer papers only |
| 9 | title search deconvolution cfDNA benchmark | Europe PMC | Sun et al. 2024, Genome Biology (PMC11660681) |
| 10 | ML classifiers same cohort DISMIR CancerDetector | web search | DISMIR (developer) noted |
| 11 | EM-seq or cfMeDIP vs bisulfite comparisons | Europe PMC | Two technical comparisons, excluded |
| 12 | read-level tumour fraction MethylBERT DISMIR | web search | MethylBERT screened, excluded |
| 13 | MetDecode tissue of origin vs CelFiE meth_atlas | web search | MetDecode screened, excluded |
| 14 | head-to-head methylation assays same patients (extended) | web search | Nothing usable |
| 15 | tissue of origin cfDNA methylation benchmark (boolean, open access) | Europe PMC | SPOT-MAS (PMC10567114) |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Sun et al. 2024, Genome Biology, Additional file 1 Table S7 | Extract the AUC block (30 cells) | Independent benchmark (none of the authors developed CelFEER, CelFiE, cfNOMe, MethAtlas or UXM). The only per-method printed values on real patient plasma found in this pass. |
| Sun et al. Table S7, -log10(p) block | Not extracted | A one-sided Wilcoxon test of the affected-tissue fraction between groups. It is a test statistic that grows with group size, not a performance measure, and no metric concept fits. Excluded by metric type, not by value. |
| Giuili et al. 2025 (DecoNFlow), Supplementary Table 3 | Extract all 180 values | The only printed per-tool comparison of tumour-fraction detection found: ten tools, three datasets, depth strata. Preprint. The authors wrote the DecoNFlow pipeline; the ten tools are cited as earlier publications, and the MetDecode author list does not overlap with the preprint's. Other tool author lists were not checked. |
| Nguyen et al. 2023 (SPOT-MAS), Table S9 | Extract all 180 accuracy cells and 60 n cells | Only printed per-method tissue-of-origin comparison on patient plasma found, with an independent validation cohort. Author-reported and multimodal. |
| Jamshidi et al. 2022 (Cancer Cell) | Gap | Compares several assays and classifiers on the same CCGA samples at fixed specificity, which is the evidence the use case most needs. Publisher pages returned 403; not in PMC. |
| MetDecode (Bioinformatics 2024) | Excluded | Comparator results only in figures. |
| MethylBERT (Nat Commun 2025) | Excluded | Developer paper; tumour-purity comparisons on lymphoma pseudo-bulks, not plasma. |
| Two conversion-chemistry comparisons (Clin Epigenetics 2025; Front Epigenet Epigenom 2025) | Excluded | Technical metrics only, no detection endpoint. |
| SPOT-MAS Tables S7 and S8 | Not extracted | S7 prints differences between models, not values; S8 is one configuration. Leads for a later pass. |

## Record design

- Sun et al.: two protocols, one per cohort (liver cancer WGBS; cfMethyl-Seq five cancers). The cfMethyl-Seq protocol carries one result per cancer type, distinguished by `metric_qualifier`. Ten evaluations, origin `independent_paper`.
- Giuili et al.: three protocols, one per dataset (WGBS-TT, RRBS-TT, RRBS-CL). Each of the 30 evaluations has a result per sequencing depth (qualifier `median at <depth> aligned reads`) and an overall median (sheet B). Origin `independent_paper`. Unit `fraction` (tumour DNA fraction). A new metric concept `limit-of-detection` was added to `data/vocab/metric.ttl` (direction lower); it needs review with the batch.
- Nguyen et al.: two protocols (discovery 10-fold cross-validation; independent validation). Six evaluations, origin `author_reported`. The "All cancer" rows use `accuracy`; the per-cancer rows are the proportion of that cancer's patients assigned correctly, which is per-class recall, so they use `recall` with "printed as accuracy" in the qualifier.
- Seven relevance judgements, all `proxy` (see `coverage.json`). Grouped as three comparisons with strata.

## Things a reviewer should judge

1. **Giuili et al. Supplementary Table 3, RRBS-CL block.** For UXM, MetDecode, meth_atlas, PRMeth and CIBERSORT, sheet A columns K-O differ from Figure 4A and from sheet B. Example: UXM sheet A 0.003/0.003/0.001/0.003/0.001, Figure 4A 0.05/0.05/0.007/0.025/0.007, sheet B overall 0.025. The Results sentence that MetDecode reaches its RRBS-CL plateau only at 20M fits sheet A. The WGBS-TT and RRBS-TT columns of all ten rows match Figure 4A. Recorded as an evidence concern on the table source, so all three DecoNFlow judgements stay withheld until it is resolved. A reviewer could instead split the concern if the store gains per-result concerns.
2. **Giuili et al. tool names.** The table prints `EpiDISH_CP_eq`, `EpiDISH_CP_ineq` and `EpiDISH_RPC`; the text and figures print `Houseman_eq`, `Houseman_ineq` and `EpiDISH`. Matched through Supplementary Table 1A and identical values; recorded in `model_identity_note`.
3. **Giuili et al. counts.** The abstract gives 3,690 mixtures; the three dataset counts in Results sum to 3,630. Supplementary Table 4 lists 11,880 predictions per tool and the Methods text refers to 3,960 observations; neither is reconciled with 3,630 or 3,690 here. The abstract-versus-Results difference is noted on the datasets.
4. **Sun et al. AUC validation.** The random forest training and evaluation design is not stated, so the AUCs may be in-sample. This is why the judgements are `proxy` and not `direct`.
5. **Sun et al. cfMethyl-Seq cohort.** Same study as `amp-data-cfmethyl-408` (Stackpole et al. 2022), but 225 cancers and 193 controls against 217 and 191 there. Not linked as the same data.
6. **Nguyen et al. stage strata.** Table S9 stage sizes differ from Table S8 and Table 1 (discovery stage I 50 vs 52, unknown stage 138 vs 128). Recorded as an evidence concern on the supplement.
7. **Nguyen et al. second model.** Table S9 and the Methods call it DNN (H2O feedforward network); Results P23 and Figure 8 figure supplement 1 call it a CNN. Recorded on the configuration.
8. **Nguyen et al. text check.** GCNN validation accuracies in Results P25 (breast 0.78, liver 0.76, colorectal 0.66, lung 0.63, gastric 0.55) match Table S9 E14:E18. Discovery values 0.87, 0.82 and 0.54 match E5, E8 and E7.
9. **Giuili et al. text check.** Results quotes CelFiE median LoD 0.7% at 10M (RRBS-TT), 0.7% at 310M (WGBS-TT) and 0.1% at 2M (RRBS-CL); these match D3, I3 and K3.
10. **Printed values.** Giuili et al. cells carry the format `0.0000`, so `printed_value` is the displayed text (`0.0250`). One Sun et al. cell (I7) carries `0.00_ ` and prints `0.80`. Four Giuili et al. cells are text (`0.0070*`).

## Coverage

Bounded pass against the sources above; not systematic. Not covered: Jamshidi et al. 2022 and other CCGA papers; cfSort, cfTools, DISMIR, Hill et al. 2023; assay-level comparisons with a detection endpoint (cfMeDIP-seq, WGBS, EM-seq, targeted bisulfite); prospective or screening-population studies; the figure-only results of all three extracted papers.
