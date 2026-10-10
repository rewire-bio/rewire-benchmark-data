# Sources: rare-disease candidate ranking use-case pass, 2026-10-09

All artifacts were retrieved from the Europe PMC REST API. Hashes are SHA-256 of the exact bytes parsed. CC BY 4.0 sources were archived as `gzip -n -9` copies in `artifacts/`; the CC BY-NC source (Yuan et al. 2022) is not archived. The Yuan et al. 2024 archive was removed in review on 2026-10-09: the article's Table 2 and Results name individual cases with their causal variants, which must not be stored here. Its URL and SHA-256 remain on the source record, and the Europe PMC XML re-downloads to that hash.

| Source ID | Title | Version | Retrieved (UTC) | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `rare-ranking-20261009-source-yuan2022` | Evaluation of phenotype-driven gene prioritization methods for Mendelian diseases | Briefings in Bioinformatics 23(2):bbac019, published 2022-02-04; PMC8921623 full-text XML. CC BY-NC 4.0 | 2026-10-09T21:18:05Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8921623/fullTextXML | `a0e15e5a113ecbc1c8a3b17072a4028c55ae53c09ba0677d6fdb7601cfc8f1ca` |
| `rare-ranking-20261009-source-yuan2022-sm-table-3` | Yuan et al. 2022, SM Table 3 | `sm_table_3_r1_bbac019.docx` inside the supplementaryFiles zip. CC BY-NC 4.0 | 2026-10-09T21:18:19Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8921623/supplementaryFiles | `5a49ff00fe9b6ed8a92786c83cee79da7b2c9b958a6784d41e496ef59f17e707` (member); zip `2477ed033ada78ae776a159b0cf0a0daa15231a71a6f87ea705e6e4d3d996d41` |
| `rare-ranking-20261009-source-yuan2024` | Refined preferences of prioritizers improve intelligent diagnosis for Mendelian diseases | Scientific Reports 14:2845, published 2024-02-03; PMC10838329 full-text XML. CC BY 4.0 | 2026-10-09T21:20:19Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10838329/fullTextXML | `a5dbb24eb1e29ef8fde2832da1ff49a436464210d0e54d2a1fd10ad764a24b45` |
| `rare-ranking-20261009-source-kafkas2025` | The application of Large Language Models to the phenotype-based prioritization of causative genes in rare disease patients | Scientific Reports 15, published 2025-04-29; PMC12041562 full-text XML. CC BY 4.0 | 2026-10-09T21:20:27Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12041562/fullTextXML | `75851f55d59fb0f194ca8bbcf10f47b6f593e8658239dc0fb85f5d2844236a3b` |

The supplementaryFiles zip is assembled per request; the docx member hash is the one bound to the records.

## Reused records

| Record | Use in this pass |
| --- | --- |
| `uc-clinical-20260930-method-exomiser` | `configuration_of` target for the Exomiser configurations in all three sources |

The Talos study sources already behind this use case (`uc-clinical-20260930-source-talos`, `uc-clinical-20260930-source-talos-table1`) and the Feng source are not reused.

## Archived copies

| File | SHA-256 of gzip |
| --- | --- |
| `artifacts/kafkas2025-article.xml.gz` | `9735bfca70a8a359070ec009995bbeb2f5e752f0c16710bf31972ac0c273540d` |
