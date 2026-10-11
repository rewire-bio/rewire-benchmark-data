# Sources: You et al. 2026, benchmarking pre-trained genomic language models on RNA-related tasks

| Source ID | Title | Version | Retrieved (UTC) | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `gfm2-20261011-you2026-source` | Benchmarking pre-trained genomic language models for RNA sequence-related predictive applications | Nat Commun 17:223, published online 2025-12-07; PMC12780105 full-text XML. CC BY-NC-ND 4.0 | 2026-10-11T00:55:34Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12780105/fullTextXML | `2c6b2816846a21296c56b4dd58f3d1e8810e9d96e224d3ab21b5eb8faa9928e4` |
| `gfm2-20261011-you2026-source-supplement` | You et al. 2026, Supplementary Information (Supplementary Tables 1-6) | `41467_2025_66899_MOESM1_ESM.pdf` inside the Europe PMC supplementaryFiles zip | 2026-10-11T00:55:34Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12780105/supplementaryFiles | `cbb69e05045a4526e35479d2c1361ebb9cfadfd968e00675390dad597035d882` (member PDF) |

The outer supplementaryFiles zip is assembled per request; the copy read here hashed
`9a0d0a8d8643872ab265e3e6ed7eea944563da4861bf764f97c68fc6aa502525`, and only the member PDF hash is bound to
the records. The licence is CC BY-NC-ND 4.0, so no copy of either artifact is archived in this repository.

The supplementary text layer (`pdftotext -layout`, poppler 26.08.0) hashed
`4a54c8b1acbb475db01d8768b4ff7279a9b503714b395738496d6f817127308e`. `extract/extract.py` parses that text and
asserts every method label against the inventory and the column order of each table block.

## Reused records

| Record | Use in this batch |
| --- | --- |
| `discovery-model-dnabert-2` | `configuration_of` target for the DNABERT2 configuration |
| `discovery-model-nucleotide-transformer` | `configuration_of` target for the NucleotideTransformer configuration |
| `discovery-model-spliceai` | `configuration_of` target for the SpliceAI configuration |

New family records: DNABERT, GENA-LM (shared by the base and large configurations), SpliceBERT, RNA-FM,
RNA-MSM, RNAErnie, RNABERT, UTR-LM (models) and SpTransformer (method). The store held none of these as
entities.
