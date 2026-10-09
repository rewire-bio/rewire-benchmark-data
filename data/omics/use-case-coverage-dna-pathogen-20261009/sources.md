# Sources: DNA pathogen-identification use-case pass, 2026-10-09

All three sources were retrieved as full-text XML from the Europe PMC REST API. Each table used is in the article XML itself, so no supplementary file is pinned. Hashes are SHA-256 of the exact bytes parsed. Each article's XML `<license>` element states Creative Commons Attribution 4.0, so gzip copies (`gzip -n -9`) are archived in `artifacts/`.

| Source ID | Title | Version | Retrieved (UTC) | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `dna-pathogen-20261009-source-portik2022` | Evaluation of taxonomic classification and profiling methods for long-read shotgun metagenomic sequencing datasets | BMC Bioinformatics 23:541, published 2022-12-13; PMC9749362 full-text XML | 2026-10-09T19:45:04Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9749362/fullTextXML | `42cf6834ec87e149752176a65247f3aab9873f7b215037a195175a8a3113c1fe` |
| `dna-pathogen-20261009-source-song2025` | Diagnostic Accuracy of Shotgun Metagenomics for Bloodstream Infections Is Influenced by Bioinformatics Workflow Selection | MicrobiologyOpen 14(6):e70158, published online 2025-12-15; PMC12705909 full-text XML | 2026-10-09T19:48:48Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12705909/fullTextXML | `7b122b551b2155b43c26f5a15e7382a0662d859520d2939dc91e04d88e5656ef` |
| `dna-pathogen-20261009-source-hall2024` | Pangenome databases improve host removal and mycobacteria classification from clinical metagenomic data | GigaScience 13:giae010, published online 2024-04-04; PMC10993716 full-text XML | 2026-10-09T19:55:15Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10993716/fullTextXML | `ea3c34a01222d5c5203c52a85a700b7dae5cccd6f48e6d50808d5abbd6385554` |

DOIs: 10.1186/s12859-022-05103-0, 10.1002/mbo3.70158, 10.1093/gigascience/giae010.

## Tables used

| Source | Tables | Cells |
| --- | --- | --- |
| Portik et al. 2022 | Table 4 (species-level detection at 0.001% of total reads; 70 rows, 8 value columns) | 560 results |
| Song et al. 2025 | Table 1 (8 species and 2 statistic rows by 4 pipelines, plus the theoretical column); Table 2 (7 samples by 4 pipelines) | 36 + 28 results; theoretical column as one dataset claim |
| Hall and Coin 2024 | Tables 5-8 (6 configurations by 5 value columns each) | 120 results |

Tables 1-3 of Portik et al. (datasets, methods, thresholds) and the Methods text supply dataset, configuration and protocol attributes.

## Authorship and origin

- Portik et al. 2022: D. M. Portik is a Pacific Biosciences employee and shareholder (Competing interests). C. T. Brown and N. T. Pierce-Ward are authors of the sourmash papers the article cites (references 33-35), so the two sourmash configurations are `author_reported`. The other 12 configurations are `independent_paper`; the MEGAN-LR rows ran through PacBio's pb-metagenomics-tools workflows, which is noted on those evaluations.
- Song et al. 2025: the authors declare no conflicts and evaluate third-party software (BLAST, Kraken, MetaPhlAn, RTG Core). All evaluations are `independent_paper`.
- Hall and Coin 2024: the authors built the kraken Myco, minimap2 MTB and minimap2 Myco databases and extended the Clockwork database. Those four configurations are `author_reported`; kraken standard and standard-8 are `independent_paper`.

## Archived copies

| File | SHA-256 of gzip |
| --- | --- |
| `artifacts/portik2022-article.xml.gz` | `5f1599ff4ca8eadc7851efddc378f1ad54f082eaa1ea367cc1dcde6d1b69be0a` |
| `artifacts/song2025-article.xml.gz` | `90a1721f9cf900b1ca74b8e6b4aca006abd182abc71d59697b67dbb19f4a6194` |
| `artifacts/hall2024-article.xml.gz` | `661f64e6621d81841cc38c7a378127b3ad678adecfca1fde100ac426758297a3` |
