# Research notes

Why: the genomic foundation model guides cite Kedzierska et al. 2025 (Genome Biology 26:101) for the finding that scGPT and Geneformer zero-shot cell embeddings do worse than 2,000 highly variable genes, Harmony and scVI. The store had no source or result records for it (issue rewire-benchmark-data#129).

What the paper evaluates: zero-shot cell embeddings from Geneformer and four scGPT variants (random initialisation, kidney, blood, whole-human) against HVG, Harmony and scVI on five human datasets (Pancreas 16k, PBMC 12k, PBMC 95k, Immune 330k, Tabula Sapiens 483k; the score sheets add a 'Pancreas (8k)' row). Metrics from scib 1.0.4: cell-type ASW, NMI, ARI and their mean AvgBIO; batch integration ASW, PCR and their mean 'Average batch'. Scores are computed in full embedding dimensions and after UMAP projection. A second analysis checks each model's pretraining reconstruction objective. None of the authors developed the evaluated models, so every evaluation has origin independent_paper.

Decisions:

- The headline comparisons are figures (Fig. 1B AvgBIO, Fig. 1E average batch score, Fig. 2 reconstruction) and are not read. The per-dataset numbers are in Additional file 1, which is extracted instead.
- Reused records: catalog-model-scgpt (scGPT family; all 23 existing scGPT configurations link here, and discovery-model-scgpt is an alias_of it), catalog-model-geneformer, catalog-model-scvi, and lit-cells-networks-20261011-scmbench-method-harmony (the only Harmony method record). No existing record matched the HVG baseline, the datasets as preprocessed here, or the protocols, so these are new.
- Each configuration links with configuration_of to its family or method record. scGPT random (no pretrained weights) is linked to the scGPT family as an architecture-only configuration.
- Datasets are new dataset_subset records because the paper's preprocessing and cell counts differ from existing Pancreas, PBMC and Tabula Sapiens records. A seventh subset holds results aggregated across datasets (ranks and the text median).
- Metrics map to existing concepts: ASW to scib-asw-label, NMI to normalized-mutual-information, ARI to adjusted-rand-index, 'Batch integration' to scib-asw-batch (the Methods define it as one minus absolute batch silhouette per cell type, averaged), PCR to scib-pcr-batch, ranks to rank, the reconstruction correlation to pearson-correlation. All unitless.
- No use case covers zero-shot cell embedding quality in this pass, so no relevance judgement is proposed.

## Extraction note for the reviewer

Method: deterministic parse of the pinned workbook with extract/extract_kedzierska2025.py (stdlib OOXML reader; titles, headers and every row label asserted), plus hand transcription of two text values checked by the same script against the pdftotext output of the pinned PDF. Extraction only; nothing here has been reviewed.

Tables extracted (locators use the workbook sheet names):

| Sheet | Article caption number | Content | Cells extracted |
| --- | --- | --- | --- |
| TableS6 | S1 | Scores for cell embeddings, full dimensions | 224: single-value column for ASW, NMI, ARI (6 dataset rows) and Batch integration, PCR (5 rows), 8 representations |
| TableS7 | S5 | Scores for UMAP-projected embeddings | 224, same layout |
| TableS3 | S2 | Rank of median score across datasets, 7 metrics | 56 (8 x 7) |
| TableS4 | S4 | Average ranking, full dimensions, overall and per dataset | 48 (8 x 6) |
| TableS5 | S6 | Average ranking, UMAP | 48 (8 x 6) |
| Article page 5 | text | Geneformer reconstruction, median 0.56 and best 0.95 Pearson correlation across datasets | 2 |
| TableS2 | S3 | Pretraining overlap | 3 claims (Pancreas GSE84133 in Geneformer pretraining; Tabula Sapiens and Immune in scGPT pretraining) |

TableS1 (caption S7, dataset overview) was used for dataset descriptions only.

Record counts: 2 sources, 1 benchmark, 3 protocols, 7 dataset subsets, 1 method, 8 configurations, 113 evaluations, 602 results, 3 claims (740 records).

Gaps:

1. AvgBIO and Average batch rows not extracted (176 whole-dataset cells across TableS6 and TableS7). No metric concept fits. AvgBIO is the headline metric of Fig. 1B. Concepts needed: `avg-bio` (arithmetic mean of cell-type ASW, NMI and ARI, as defined for scGPT by Cui et al. 2024; higher is better; unitless) and `average-batch-score` (arithmetic mean of batch-integration ASW and PCR batch score, defined by Kedzierska et al. 2025, Methods page 10; higher is better; unitless). Once added, the script can emit these rows after setting the concept, qualifier and slug for those two blocks (METRIC_BLOCKS, QUAL, SLUG). Their ranks are already recorded from TableS3 (columns 'Average BIO' and 'Average batch').
2. Subsample columns not extracted (312 bracketed cells per score sheet, 624 in all, for example '0.553 (0.542 - 0.558)'). The caption says 10 repeats on 10% subsamples but does not say whether the central value is a mean or median, or what the bracketed range is. The scVI column often shows a zero-width range (for example TableS6 H3 '0.580 (0.580 - 0.580)'), which the reviewer may want to raise with the authors.
3. Figures not read: Fig. 1B, 1E, Fig. 2A-E (including scGPT reconstruction MSE, which is printed nowhere), Additional file 2 Figs. S1-S9.
4. UMAP parameters, HVG selection flavour, and Harmony and scVI versions and hyperparameters are not stated (missing_metadata on the configurations and protocol).

Needs reviewer judgement:

- Table numbering: the workbook's sheet numbers differ from the article's Additional file 1 caption (recorded as an evidence concern on the workbook source, with the full mapping). The text cites 'Table S1' for scores; that is workbook sheet TableS6.
- Column inference: each model has two unlabelled columns under one merged header. The single-value column is read as the whole-dataset score and the bracketed one as the 10-repeat subsample summary (evidence concern on the workbook source).
- 'Pancreas (8k)': the Methods say the authors also scored the Pancreas subset that excludes GSE84133 (in Geneformer pretraining). The workbook does not say this row is that subset; the record describes it as unconfirmed.
- Text versus table: page 4 says 'the best batch integration scores for all datasets were achieved by selecting HVG (Additional file 1: Table S2)'. In TableS6, scGPT random scores higher than HVG on Pancreas (16k) (0.96 against 0.93) and Pancreas (8k) (0.96 against 0.9). HVG ranks first on the median in TableS3. Recorded here only; the values themselves are as printed.
- Ties: TableS4 and TableS5 print shared ranks (for example scVI and Harmony both 1 on Pancreas (16k) in TableS4).
- scGPT random as a configuration of the scGPT family, and Harmony linked to the SCMBench Harmony method record.
- The brief named discovery-model-scgpt as the canonical scGPT family. In this store discovery-model-scgpt is alias_of catalog-model-scgpt, and every existing scGPT configuration uses catalog-model-scgpt, so the new configurations do too. Change the links if the alias direction is meant to be the other way.
