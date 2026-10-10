# Sources: genetic perturbation response use-case pass, 2026-10-09

One study is extracted, pinned as two source records. Hashes are SHA-256 of the exact bytes parsed. Both files are CC BY 4.0 and are archived in `artifacts/`.

| Source ID | Title or file | Version | Retrieved (UTC) | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `perturbation-response-20261009-source-csendes2025` | Benchmarking foundation cell models for post-perturbation RNA-seq prediction | BMC Genomics 26:393, published 2025-04-23; PMC12016270 full-text XML | 2026-10-09T20:58:48Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12016270/fullTextXML | `b59088e4169385c602d0b7a51253d7c1131688666e64e95c06fb54950a514c19` |
| `perturbation-response-20261009-source-csendes2025-supp` | Csendes et al., Supplementary Material 4 (Supplementary Tables 1-3) | `12864_2025_11600_MOESM4_ESM.xlsx` (15,262 bytes) from the Europe PMC supplementary bundle | 2026-10-09T20:58:56Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12016270/supplementaryFiles | `b5bfcb633921a642de077a39fcb015c6d36bc36a52d9c5e9ceca33be483d3261` |

DOI: 10.1186/s12864-025-11600-2. The workbook hash is of the XLSX itself; Europe PMC rebuilds the bundle zip on each request.

| Archived file | SHA-256 of gzip |
| --- | --- |
| `artifacts/csendes2025-article.xml.gz` | `a04677b6c72ead6ad8331f2055fc83cd7d15c68399385f43f20eaa8a944ea14e` |
| `artifacts/csendes2025-supplementary-tables.xlsx.gz` | `01d8a4dd550053c0b1495134ce07c60101a35304c3bb0fd2d46e7f0a191e9a9a` |

## Tables used

| Table | Cells |
| --- | --- |
| Supplementary Table 2: 4 datasets by 15 models by 6 Pearson metrics | 352 results; the 8 Wilcoxon cells for scGPT and scFoundation are blank in the source and asserted blank |
| Supplementary Table 1: train, validation and test perturbation counts per dataset, and Norman test subgroups | Dataset attributes and one claim |

Supplementary Table 3 (Norman subgroups) is not extracted because its metric is not labelled.

## Authorship and origin

All authors are full-time employees of Turbine Ltd., Budapest, and K. Szalay is a founder (Competing interests). They built the Train Mean, random forest, elastic net and kNN baselines and argue that baselines outperform the foundation models, so the 52 baseline evaluations are `author_reported`. They re-ran scGPT (v0.2.1 fork, commit 7301b51) and scFoundation (commit 69b0710) from the developers' code, so those 8 evaluations are `independent_paper`.

## Not duplicated

The three existing judgements rest on GEARS Supplementary Table 6 (`coverage-source-gears-supp`) and PertEval-scFM (`perteval-scfm-2025-source`). Neither is re-pinned or re-extracted here.
