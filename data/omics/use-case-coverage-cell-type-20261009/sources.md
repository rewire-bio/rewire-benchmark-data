# Sources: cell-type annotation transfer use-case pass, 2026-10-09

One study is extracted, pinned as two source records. Hashes are SHA-256 of the exact bytes parsed. The licence is CC BY-NC-ND 4.0, so nothing is archived; following the earlier handling of no-derivatives licences, the hashes and URLs are recorded instead.

| Source ID | Title or file | Version | Retrieved (UTC) | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `cell-type-20261009-source-wu2025` | Biology-driven insights into the power of single-cell foundation models | Genome Biology 26:334, published 2025-10-03; PMC12492631 full-text XML (354,140 bytes) | 2026-10-09T21:22:13Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12492631/fullTextXML | `368051b7cda5acd4864331875a1faac6f1d68e0a209ed999e4c2ee3b25b57c2c` |
| `cell-type-20261009-source-wu2025-supp` | Wu et al. 2025, Additional file 3 (Supplementary Tables S1-S13) | `13059_2025_3781_MOESM3_ESM.xlsx` (38,926 bytes), as linked from the article XML `<supplementary-material id="MOESM3">` | 2026-10-09T21:22:24Z | https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-025-03781-6/MediaObjects/13059_2025_3781_MOESM3_ESM.xlsx | `51ecea4318178dfb7dc6b51eae23303d68f25e83641809c95429b082353dc99d` |

DOI: 10.1186/s13059-025-03781-6. Code: https://github.com/wujialu/scFM-Bench (MIT, per Code availability; not pinned here).

## Tables used

| Table | Rows | Cells |
| --- | --- | --- |
| Supplementary Table S2: Tabula Sapiens to HLCA | 6 single models, 15 pairwise ensembles, 2 full ensembles | 46 results (Accuracy@1, macro-F1) |
| Supplementary Table S3: HLCA to Tabula Sapiens | same 23 configurations | 46 results |

Table 1 (model overview) and Table 2 (datasets) of the article supply model, dataset and label-column attributes. Supplementary Table S6 holds donor-level demographics for AIDA v2 and was not extracted.

## Evidence concern

The supplement source carries one concern: Results 'Cross-dataset validation' paragraph 4 describes the full-ensemble comparison the opposite way round from both tables. The table values are recorded, and the extractor asserts the table direction.

## Label source

The truth labels are the atlases' own annotations: `cell_ontology_class` for Tabula Sapiens and `cell_type` for HLCA core (Table 2), downloaded from CELLxGENE and reduced to leaf ontology terms with at least 10 cells (37 HLCA types, 120 Tabula Sapiens types, 14 shared).

## Authorship and origin

The source does not state that any author developed the six evaluated models; all 46 evaluations are `independent_paper` on that basis.

## Not duplicated

The five existing judgements rest on Abdelaal et al. 2019 and scTab. Neither is re-pinned or re-extracted.
