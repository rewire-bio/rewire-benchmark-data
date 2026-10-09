# Research: patient-RNA splicing use-case pass, 2026-10-09

Use case: `use-case-patient-rna-splicing-validation` ("Which DNA/RNA evidence workflow identifies splice-altering variants for inherited-disorder follow-up when patient RNA and tissue-specific context are available?"). Before this pass it had one reviewed judgement: FRASER recovery of 13 known pathogenic splicing events at 30 of 119 Kremer fibroblast samples, with a single evaluation.

Bounds: cutoff 2026-10-09; budget 25 search queries, 12 used; at most 3 sources extracted. Lane `rna`. In scope: published tables with per-method values for several methods on the same patient RNA-seq cohort or the same RNA-validated variant set. Excluded by the use case: diagnostic yield in unsolved patients, full-cohort outlier workload counts, blinded pathogenicity adjudication.

## Queries

| # | Time (UTC) | Query | Channel | Outcome |
| --- | --- | --- | --- | --- |
| 1 | 20:30:02 | `(FRASER OR LeafCutterMD OR SPOT OR OUTRIDER) AND "aberrant splicing" AND (benchmark OR comparison) AND (patient OR "rare disease") AND PUB_YEAR:[2019 TO 2026]` | Europe PMC REST | 254 hits; saseR (PMC13019952), FRASER 2.0 (PMC10716352), Drost et al. (PMC12547740) |
| 2 | 20:30:10 | `(SpliceAI AND (MMSplice OR Pangolin OR SQUIRLS OR AbSplice OR "CADD-Splice")) AND ("RNA-seq" OR "RNA validated" OR "RNA studies" OR minigene) AND (sensitivity OR AUC OR benchmark) AND PUB_YEAR:[2020 TO 2026]` | Europe PMC REST | 98 hits; Smith and Kitzman 2023 MPSA (already a stored source), heart-specific model (PMC11476204), Gigascience 2022 deep-intronic benchmark |
| 3 | 20:30:19 | `(AbSplice OR "aberrant splicing prediction") AND (SpliceAI OR MMSplice) AND (tissue OR GTEx) AND PUB_YEAR:[2022 TO 2026]` | Europe PMC REST | 31 hits; AbSplice paper itself not returned as open full text |
| 4 | 20:30:19 | `("splice-altering" OR "spliceogenic") AND ("RNA-seq" OR "RNA studies") AND (SpliceAI) AND (patients OR "rare disease" OR "diagnostic") AND (comparison OR performance OR benchmark) AND (ROC OR sensitivity OR "precision") AND PUB_YEAR:[2021 TO 2026]` | Europe PMC REST | 87 hits; PLoS One 2026 (PMC13170886), Drost et al. again |
| 5 | 20:30:27 | `DOI:10.1038/s41588-023-01373-3` | Europe PMC REST | AbSplice (Nat Genet 2023); no PMCID |
| 6 | 20:30:28 | `(LeafCutterMD OR "SPOT" OR FRASER2 OR "FRASER 2.0" OR MAJIQ OR "MAJIQ-CLIN") AND (FRASER) AND ("aberrant splicing" OR "splicing outlier") AND (comparison OR benchmark OR compared) AND PUB_YEAR:[2020 TO 2026]` | Europe PMC REST | 44 hits; Segarra-Casas et al. (PMC12257123), Solve-RD preprint |
| 7 | 20:31:11 | `(AbSplice) AND (SpliceAI OR Pangolin OR MMSplice) AND (AUPRC OR precision OR benchmark OR "outliers")` | Europe PMC REST | 23 hits; no independent AbSplice table |
| 8 | 20:33:43 | `("LeafCutterMD" OR "FRASER") AND ("known pathogenic" OR "positive control" OR "previously diagnosed" OR "solved cases") AND ("RNA-seq") AND (sensitivity OR detected OR recall) AND (tools OR methods) AND PUB_YEAR:[2020 TO 2026]` | Europe PMC REST | 217 hits; screened NAR Genom Bioinform 2026 and J Transl Med 2025 |
| 9 | about 20:35 | `https://www.nature.com/articles/s41588-023-01373-3` | WebFetch | Login redirect; not followed |
| 10 | 20:35:34 | `TITLE:"Aberrant splicing prediction across human tissues"` | Europe PMC REST (core) | Journal record and bioRxiv preprint, neither open full text in Europe PMC |
| 11 | 20:36:00 | `(MMSplice OR SQUIRLS OR "CADD-Splice" OR SpliceVault) AND (SpliceAI) AND ("RNA-seq" OR "RNA analysis" OR "RNA-validated" OR "patient RNA") AND (benchmark OR comparison OR "in silico") AND PUB_YEAR:[2020 TO 2026]` | Europe PMC REST | 73 hits; no new tabled comparison with MMSplice or CADD-Splice |
| 12 | 20:36:00 | `(minigene OR MFASS OR "massively parallel splicing" OR "saturation") AND (SpliceAI AND Pangolin) AND (benchmark OR "performance") AND PUB_YEAR:[2021 TO 2026]` | Europe PMC REST | 37 hits; MFASS reproducible-benchmark preprint (2026), Smith and Kitzman 2023 |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Drost et al. 2025, HGG Advances, Data S1 Tables S3 and S4 | Extract all cells | Independent diagnostic laboratory; 243 clinically ascertained variants with splicing tested in patient RNA or exon trapping; SpliceAI, Pangolin, SPiP and SQUIRLS plus at-least-N consensus; AUROC, AUPRC and six thresholded metrics, overall and by cohort |
| Segarra-Casas et al. 2025, ACTN, Table 2 | Extract all cells | Independent clinical study; 16 known pathogenic splicing events in muscle RNA-seq; FRASER at two cutoffs, FRASER2, LeafCutterMD, rMATS-turbo and OUTRIDER on the same samples |
| Segers et al. 2026, Genome Biology, Table 2 | Extract all cells | Ranks of 12 reported disease genes on the Kremer cohort for saseR, FRASER 2.0 (two settings), OUTRIDER (two settings) and OutSingle. Developer paper, but the only printed comparison of FRASER 2.0 settings on patient RNA found |
| Drost Data S1 Tables S5 and S6 | Not extracted | Variant-type strata; deferred to keep the batch lean. Table S6 prints 0 sensitivity and `.` precision for AtLeast4 in every stratum, which a reviewer should check before extraction |
| AbSplice (Wagner et al. 2023) | Excluded from extraction | Tissue-aware comparison with SpliceAI, MMSplice, SQUIRLS and CADD-Splice is reported in figures and prose only |
| FRASER 2.0 (Scheller et al. 2023) | Not decided | XML full text withheld by the publisher in Europe PMC and PMC; comparisons with LeafCutterMD and SPOT appear to be figure-based |
| PLoS One 2026 (PMC13170886) | Lead | Tables 1-6 compare SpliceAI, CI-SpliceAI, OpenSpliceAI and a legacy ensemble on six benchmarks (Riepe, SPiP, Barbosa, ClinVar). Only SpliceAI-family tools; candidate proxy evidence |
| Genome Med 2024 heart-specific model (PMC11476204) | Lead | Myocardial RNA outlier events with random-forest model contingency tables; single developed model |
| Brief Bioinform 2026 bbaf705 | Excluded | Junction-detection benchmark on deep sequencing, not patient variants or known events |
| Brief Bioinform 2026 bbag329 | Excluded | Review; the two printed tables summarise models and resources, with no per-method values |

## Modelling choices

- Each Drost cohort block (all 243, in-house, CAGI6) is its own protocol, because the population differs; the three judgements share one comparison group with stratum labels.
- Segarra-Casas and Segers each mix splicing and expression columns in one table. Splicing columns and expression columns are separate protocols; the expression protocols are judged `proxy`.
- Four metric concepts were added to `data/vocab/metric.ttl`: `negative-predictive-value` (STATO_0000619), `z-score` (STATO_0000104), `event-detected` and `known-gene-rank`. STATO definitions were checked through the OLS API.
- SpliceAI and Pangolin configurations point at the existing `catalog-model-*` family records. New method records were created for FRASER, LeafCutterMD, rMATS-turbo, OUTRIDER, OutSingle, saseR, SPiP, SQUIRLS and the consensus rule; none existed in the store.
- Origin: Drost and Segarra-Casas evaluations are `independent_paper` except the Drost consensus rule, which the authors devised (`author_reported`). In Segers, saseR evaluations are `author_reported` and the comparators `independent_paper`.

## Things a reviewer should judge

1. Drost Results prose prints SQUIRLS AUPRC 0.888; Data S1 Table S3 D13 stores 0.881 (SPiP is 0.8886). Recorded as an evidence concern on the article source, which holds the three Drost judgements as draft. A reviewer may decide this is a typo that does not affect the table.
2. Drost Table S4 CAGI6 block: Pangolin, SPiP and SpliceAI rows are identical in all six columns (rows 20-22). Plausible for 56 variants but worth a second look.
3. Drost Results cite Table S3 for thresholded TPR, F1 and NPV that appear in Table S4.
4. Drost Pangolin is printed as "version 4.3.1", which does not match the Pangolin release numbering the extractor knows. Recorded as printed with a limitation.
5. Segarra-Casas: FRASER2 detection rate is 68.7% (11/16) in Results and 66.6% in Discussion. Table 2 does not state the cohort size per run; Results first describe a 34-sample batch-1 comparison and then report events across all 98 samples. Recorded as protocol limitations, not as an evidence concern.
6. Segarra-Casas: case 2 FRASER2 cell prints "*Only identified with all cohort samples"; kept as printed with `numeric_value` null.
7. Segers: 12 disease genes include mono-allelic-expression cases (ALDH18A1, MCOLN1) and TIMMDC1 twice. Ranks are developer-run.

## Coverage

Bounded pass against the sources above. Not systematic. Not covered: tabled AbSplice or MMSplice comparisons, CADD-Splice on RNA-validated variants, blood or fibroblast multi-caller tables outside the three sources, Drost variant-type strata, minigene or MFASS-style proxies beyond the existing mapping, and the FRASER 2.0 article.
