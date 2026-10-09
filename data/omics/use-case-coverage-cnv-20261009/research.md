# Research: CNV detection use-case pass, 2026-10-09

Use case: `use-case-cnv-detection-characterisation` ("Which workflow detects and characterises copy-number changes accurately and helps an analyst assess the evidence?"). Input in the definition: whole-genome sequencing aligned reads.

Why this use case first: all 26 use cases in `inputs.json` have at least one mapping, but seven AMP-intake use cases rest on one evaluation with one result. This one had a single cell (DRAGEN CNV+SV F-score 0.926 for 1-5 kb deletions), no comparator and no dossier.

Bounds: cutoff 2026-10-09; budget 25 search queries; 8 used. Lane `genomics`. Germline WGS CNV callers on reference samples with printed per-tool values were in scope. Exome-only and somatic work was screened and recorded but not extracted.

## Queries

| # | Query | Channel | Outcome |
| --- | --- | --- | --- |
| 1 | comparison of germline CNV detection tools whole genome sequencing benchmark GIAB HG002 precision recall table | web search | Leads to Tempus/De La Vega benchmark and Gabrielaite 2021 |
| 2 | Gabrielaite 2021 comparison of tools for copy-number variation detection germline whole exome whole genome sequencing | web search | PMC8699073 confirmed; also Zhao 2020 and Gordeeva 2021 (exome) |
| 3 | benchmarking somatic copy number alteration callers tumour whole genome sequencing SEQC2 reference HCC1395 | web search | Genome Biology 2024 (PMC11188507) |
| 4 | "Benchmarking of germline copy number variant callers from whole genome sequencing data for clinical applications" | web search | PMC12005901, Bioinformatics Advances 2025 |
| 5 | deep learning copy number variant caller exome benchmark ECOLE Mandiracioglu 2024 precision recall table | web search | ECOLE, PMC10762021 |
| 6 | CNV caller benchmark HG002 T2T Q100 or GIAB CMRG copy number deletions duplications short-read 2025 | web search | Nardone et al. 2025, Biomedicines (PMC12383524); no T2T-Q100 or CMRG CNV caller benchmark found |
| 7 | Whitford 2019 CNV callers NA12878 whole genome deletions comparison CNVnator ERDS Canvas | web search | EJHG 2022 combining-callers paper (PMC8821561); Whitford 2019 itself not located |
| 8 | Europe PMC `DOI:10.3390/biomedicines13081949` | Europe PMC REST search | PMCID PMC12383524 |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| DRAGEN supplement Table S4 (already stored) | Extract remaining 44 cells | Same sample and truth set as the existing mapping; adds CNV-only DRAGEN and CNVnator comparators and four more length bins |
| De La Vega et al. 2025, Supplemental Table 3 and Table 1 | Extract all cells | HG002 GIAB v0.6 benchmark of 8 configurations including a deep-learning caller (Cue), DEL and DUP by length; Table 1 adds a clinical-panel precision stratification |
| Gabrielaite et al. 2021, Table S2 | Extract the 8 NA12878 WGS rows only | NA12878 rows use a gold-standard truth set. Cohort rows GB-WGS-01 to 38 use SNP-array calls as truth, which cannot see most small CNVs, and are 304 per-sample rows (295 with values); WES rows are outside the use-case input. Selection is by sample and reference standard, not by value |
| Nardone et al. 2025, Table S1 | Extract all 80 rows | Ten short-read callers, HG002 GIAB v0.6 Tier 1 deletions, size-binned TP/FP/FN and P/R/F1. Bins of 1 kb and above are CNV-sized; smaller bins are kept so the table is not cherry-picked |
| SEQC2 somatic CNV, Genome Biology 2024 | Record as `discovered` benchmark and dataset; no results | Per-caller accuracy appears only in figures (main Table 1 and Additional file 1 tables hold set sizes, ploidy, correlation and parameters) |
| ECOLE, Nat Commun 2024 | Exclude | Exome input; Table 3 truth is CNVnator calls ("semi-ground truth") |
| Gordeeva et al. 2021, Sci Rep | Exclude | Exome only; main tables are call counts, not accuracy |
| EJHG 2022 combining callers (PMC8821561) | Not decided | Per-caller NA12878 values sit in a 6 MB supplementary PDF that was downloaded but not read. Gap |
| Nardone Tables S2-S5 | Not extracted | S2 and S3 vary aligner and reference for one caller; S4 and S5 are long-read callers. Candidate for a follow-up pass |

## Things a reviewer should judge

1. De La Vega Table S3: rows `Dragen v4.2 HS + Filters` and `Dragen v4.2` are identical in 17 of 22 cells. Transcribed as printed; worth a second look, but nothing in the article says either row is wrong.
2. De La Vega: Delly is `v1.1.6` in Table S3 and `v1.6` in Methods 2.3. Version recorded with the conflict.
3. De La Vega: co-authors are Tempus and Illumina employees. DRAGEN evaluations are recorded as `author_reported`; other callers as `independent_paper`.
4. Nardone: depth (25x vs 30x) and aligner (bwa-mem2 vs DRAGEN pipeline) conflict across Methods, Results and Data Availability. Recorded as an evidence concern on the Table S1 source; `comparison.inputs` is null.
5. Nardone: Results 3.1 prose for inGAP 5000-9999 bp (F1 97%, P 92%, R 94%) disagrees with Table S1 (0.9466, 0.9714, 0.9231) and is internally impossible. Evidence concern on the article source; table values recorded.
6. DRAGEN S4 row 8 label prints `[10,000-20,0000)`; read as 10-20 kb by position. Label retained.
7. Gabrielaite: Manta and CNVnator helped build the NA12878 truth set (claim record added).

## Coverage

Bounded pass against the sources above. Not systematic. Not covered: long-read CNV callers, exome CNV callers, somatic and tumour CNV with printed values, T2T-Q100 or CMRG truth sets, evidence-visualisation usability, and the EJHG 2022 supplement.
