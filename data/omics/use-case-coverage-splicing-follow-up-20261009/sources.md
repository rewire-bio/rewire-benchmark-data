# Sources: splicing follow-up use-case pass, 2026-10-09

Hashes are SHA-256 of the exact bytes parsed. CC BY 4.0 sources are archived as `gzip -n -9` copies in `artifacts/`; the CC BY-NC article (Riepe et al.) is not archived.

| Source ID | Title | Version | Retrieved (UTC) | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `splicing-follow-up-20261009-source-smith2023` | Benchmarking splice variant prediction algorithms using massively parallel splicing assays | Genome Biology 24:294, published 2023-12-21; PMC10734170 full-text XML. CC BY 4.0 | 2026-10-09T20:49:26Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10734170/fullTextXML | `5aceff067af63ab59400ade7dd7db563a16fc7f4d6db6fa55d5b34689f7a0769` |
| `splicing-follow-up-20261009-source-smith2023-table-s2` | Smith and Kitzman 2023, Additional file 3 (Table S2) | `13059_2023_3144_MOESM3_ESM.xlsx` inside the supplementaryFiles zip. CC BY 4.0 | 2026-10-09T20:49:34Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10734170/supplementaryFiles | `c5ed8dc1488f87a1aff766c0ed4c8b3faab148259ca6e6f28e729b9a57a700fa` (member); zip `e06758da73eda5d4ba9c61361514ed2d84573bf50df5bf8036102389e019d525` |
| `splicing-follow-up-20261009-source-riepe2021` | Benchmarking deep learning splice prediction tools using functional splice assays | Human Mutation 42(7):799, published online 2021-05-20; PMC8360004 full-text XML. CC BY-NC 4.0 | 2026-10-09T20:52:02Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8360004/fullTextXML | `595be5360a9d3d421c4d4b6adda30175b4048e1aa0b563eb7afd2b7850277112` |
| `splicing-follow-up-20261009-source-znabu2026` | A Reproducible MFASS Benchmark of Splice-Disruption Predictors Reveals a Shared Exon-Interior Blind Spot | bioRxiv 2026.07.21.739871 v1, posted 2026-07-26; full-text PDF. Preprint, CC BY 4.0 | 2026-10-09T20:52:21Z | https://www.biorxiv.org/content/biorxiv/early/2026/07/26/2026.07.21.739871.full.pdf | `52a2d1ccfd99ef62f847b323030acdb7d881ae75b6c9dda8805884a2e7727552` |

Notes:

- The store already holds `evidence-expansion-splice-evaluation-6960a140` for the same Smith and Kitzman Europe PMC URL (retrieved 2026-09-17, SHA-256 `6960a140...`). The bytes retrieved here differ, so a new source record pins them; the earlier record is unchanged. A reviewer may decide to link or retire one of them.
- bioRxiv writes the download time into the PDF ModDate, so a re-download of the Znabu preprint gives a different file hash. The hash describes this retrieval; a reviewer should compare the text layer.
- The Europe PMC supplementaryFiles zip is assembled per request; the xlsx member hash is the one bound to the records.

## Reused records

| Record | Use in this pass |
| --- | --- |
| `catalog-model-spliceai` | `configuration_of` target for the SpliceAI configurations in all three sources |
| `catalog-model-pangolin` | `configuration_of` target for the Pangolin configurations (Smith and Kitzman, Znabu) |
| `rewire-mfass-v2-dataset` | `data` and `uses_data` target for the Znabu evaluations; its `cohort_variants` (27,733) matches the labelled MFASS SNVs scored by Znabu et al. Variant-level identity was not checked |

## Archived copies

| File | SHA-256 of gzip |
| --- | --- |
| `artifacts/smith2023-article.xml.gz` | `208784c07a8df62c06170cea09f2fa9d3efe4d4c7b11d6fc8841a191f7abfc16` |
| `artifacts/smith2023-table-s2.xlsx.gz` | `0588a7a69ad6a02769023e0f42a2b3f3b34f03dd74d56fc7ff54ac7a6f0f6c81` |
| `artifacts/znabu2026-preprint.pdf.gz` | `c2e4679943c8cd7d4f56a943d48ed6fe916f1aafd01ba5ac183257cd42dd2bac` |
