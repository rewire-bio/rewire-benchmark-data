# Research: somatic small-variant oncogenicity use-case pass, 2026-10-09

Use case: `use-case-somatic-small-variant-oncogenicity` ("Which methods help classify somatic SNVs and small indels while preserving uncertainty and the relevant gene mechanism?"). Existing evidence: four OncoVI judgements from one source (`uc-clinical-20260930-source-oncovi`), not duplicated here.

Bounds: cutoff 2026-10-09; 7 of 25 queries; 2 of 3 sources. Lane `genomics`. Ledger IDs `search-use-case-somatic-oncogenicity-genomics-q1` to `-q7`.

## Queries

| # | Query (abridged) | Channel | Outcome |
| --- | --- | --- | --- |
| 1 | CHASMplus, CanDrA, FATHMM, BoostDM, AlphaMissense, REVEL, VEST4 with somatic or driver benchmark and AUC | Europe PMC | Chen et al. 2020 selected; Tran et al. 2025 figure-only |
| 2 | title search for driver or somatic predictor benchmarks | Europe PMC | Lee 2026 preprint; two closed-access comparisons |
| 3 | DMS or saturation editing of cancer genes against predictors | Europe PMC | Germline-oriented; nothing selected |
| 4 | oncogene versus tumour suppressor predictor benchmarks | Europe PMC | Nothing new |
| 5 | DOI check for J Mol Diagn 2020 and Comput Biol Med 2022 | Europe PMC | Not open access |
| 6 | DOI check for the 2026 preprint | Europe PMC | CC BY preprint |
| 7 | OncoCal repository | GitHub API | Commit pinned |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Chen et al. 2020, Additional files 9, 10, 21, 22 | Extract every cell (500 results) | 33 predictors, independent group, somatic truth from OncoKB curation and cell viability assays with somatic or assay-neutral negatives |
| Chen et al. 2020, files 5, 13, 17 and AUC PDFs | Not extracted | Benchmark 1 uses non-cancer-gene negatives; benchmarks 3 (TP53) and 4 (71 mutations) kept as gaps to stay lean; AUC values are printed only inside figures |
| Lee 2026 preprint and OncoCal tool_performance.tsv | Extract every cell (294 results) | Only source found that splits predictor performance by oncogene and tumour-suppressor role and includes AlphaMissense, ESM1b and popEVE; proxy because of germline-benign negatives and preprint status |
| Tran et al. 2025 | Lead | Values in figures and source data |

## Modelling choices

- Four Chen protocols (benchmark 2 or 5, median threshold or default categories), grouped `chen2020-oncokb` and `chen2020-cell-viability`, headline accuracy, relevance direct.
- Three Lee protocols (all genes, oncogenes, tumour suppressors), group `lee2026-cgc-mechanism`, headline AUROC, relevance proxy as the use-case exclusion requires for germline-benign negatives.
- Method families group variant labels of one tool (PolyPhen-2 HDIV/HVAR, SIFT/SIFT4G, VARITY variants, BayesDel, MisFit, CTAT, FATHMM cancer/disease, conservation scores). Method types are my classification from each tool's published design and need review; ESM1b is marked foundation_model.
- Chen's '(±2σ)' ranges are stored as an interval with a note, not a confidence level.
- New metric concept `negative-predictive-value`.

## Things a reviewer should judge

1. The uncertainty representation for Chen's ±2σ ranges.
2. Whether the median-threshold protocols should be proxy rather than direct, since the threshold uses the test distribution.
3. OncoKB count conflict between Results and Methods.
4. Method-type assignments, especially specialist versus supervised for popEVE and Eigen.
5. Whether a single-author preprint table belongs in the store at all at this stage.

## Coverage

Bounded pass. Not covered: CHASMplus and BoostDM on independent somatic truth with printed tables, calibration to SOP evidence strength, per-gene results, indels (all evidence is missense SNVs), Chen benchmarks 1, 3 and 4.
