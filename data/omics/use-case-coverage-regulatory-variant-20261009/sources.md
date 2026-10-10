# Sources: regulatory variant and gene follow-up use-case pass, 2026-10-09

All artifacts were retrieved from the Europe PMC REST API. Hashes are SHA-256 of the exact bytes parsed. CC BY 4.0 sources are archived as `gzip -n -9` copies in `artifacts/`; the CC BY-NC-ND article (Tang et al.) is not archived.

| Source ID | Title | Version | Retrieved (UTC) | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `regulatory-variant-20261009-source-gschwind2026` | An encyclopedia of human enhancer-gene regulatory interactions | Nature 657(8130):179, published online 2026-07-15; PMC13471189 full-text XML. CC BY 4.0 | 2026-10-09T21:03:18Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13471189/fullTextXML | `df07ed8c37a62732ba0ae26b74a6c8bcb9b48540fefd03c064115d9a87a3b642` |
| `regulatory-variant-20261009-source-gschwind2026-table-s3` | Gschwind et al. 2026, Supplementary Table 3 | `2023-11-20318B-s3/Supplementary_Table_3.xlsx` inside `41586_2026_10781_MOESM3_ESM.zip` inside the supplementaryFiles zip. CC BY 4.0 | 2026-10-09T21:04:46Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13471189/supplementaryFiles | `81f7f2a3c4379adfca9db362a3aa2c2a8b4121bed0a54337a747f9afeee85904` (member); MOESM3 zip `88eb6c5239019cbec55281b545a3b6e450e2a83384d067ca94a0974968428332`; outer zip `78dc8641d9c6861568465c274b80329f7046bf7a0145c2546deb422f9a2c0930` |
| `regulatory-variant-20261009-source-manzo2025` | Comparative Analysis of Deep Learning Models for Predicting Causative Regulatory Variants | Genes 16(10):1223, published 2025-10-15; PMC12562713 full-text XML. CC BY 4.0 | 2026-10-09T21:04:27Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12562713/fullTextXML | `c49e7cef821d7c1a7966db9922b58c2f51d852df13f5cdc3969bf54818e5ed9e` |
| `regulatory-variant-20261009-source-tang2025` | Evaluating the representational power of pre-trained DNA language models for regulatory genomics | Genome Biology 26:203, published 2025-07-14; PMC12261763 full-text XML. CC BY-NC-ND 4.0 | 2026-10-09T21:04:28Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12261763/fullTextXML | `f6925cc2d93d0694ccc689970207c2df9b7b0d2562d276ede99f0c78d413b08b` |

The outer supplementaryFiles zip is assembled per request; the xlsx member hash is the one bound to the records.

## Reused records

| Record | Use in this pass |
| --- | --- |
| `ucc-research-method-mprabc-abc`, `ucc-research-method-mprabc-re2g` | `configuration_of` targets for the Gschwind ABC and ENCODE-rE2G configurations |
| `ucc-research-data-mprabc-k562-crispri` | Data for the combined K562 training stratum; same 10,356 pairs and 471 positives as Gschwind et al. Figure 2b |
| `catalog-model-dnabert-2`, `catalog-model-nt-v2`, `discovery-model-nucleotide-transformer`, `catalog-model-geneformer`, `discovery-model-chrombpnet` | `configuration_of` targets for the matching Manzo and Tang configurations |

## Archived copies

| File | SHA-256 of gzip |
| --- | --- |
| `artifacts/gschwind2026-article.xml.gz` | `6f7395cabd170df955712b9929d8c19dbbae450c468d867b6578ce605f85d814` |
| `artifacts/gschwind2026-supplementary-table-3.xlsx.gz` | `03518763e0d1052cf91e930dff69eff98c22f9e8752f4038175098e5c786ba64` |
| `artifacts/manzo2025-article.xml.gz` | `01a66e8bf405804430acd706caaddd746128db731896d2a6bc764bb517bb31a2` |
