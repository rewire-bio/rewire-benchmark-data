# Research notes

Why: SCMBench is an independent benchmark of 19 domain-specific integration methods against four single-cell foundation models (scGPT, UCE, Geneformer, scFoundation) and the authors' FM-scVI adapter, on paired and unpaired RNA-ATAC integration.

Decisions:
- Extracted the two overall integration accuracy sheets of Supplementary Data 2: per dataset, the mean of MAP, NMI, ASW and ARI ('The overall score represents the mean of these four integration accuracy metrics', Results), plus the across-dataset mean column. The per-metric sheets, biomarker, trajectory and batch-correction results are not extracted.
- printed_value is the stored double at 15 significant digits (the precision a spreadsheet shows for a General-format cell); raw_xml_value keeps the stored string. Overall cells are formulas; their cached values are recorded.
- New method records for the 18 domain-specific methods (descriptions from Supplementary Data 1); reuse catalog-model-scvi, cell-type-20261009-model-uce, catalog-model-scgpt, catalog-model-scfoundation and catalog-model-geneformer.
- New metric concept scmbench-integration-accuracy.
- Origin independent_paper except FM-scVI (the authors' adapter, author_reported).
- No current use case covers multi-omics integration, so no relevance judgement is proposed.

For the reviewer:
- 'unpaired_inte_overall' has an unlabelled column H. Each H cell is =AVERAGE(Bn:Gn) over the dataset cells with values, so rows with a blank Yao cell average five datasets; recorded as an evidence concern and labelled 'unlabelled column H' in locators (review S1, S3).
- 'FM-scVI' is a different foundation model per dataset (Fig. 2 legend); evidence concern recorded.
- Paired 'scGPT' is scored on PBMC-10k only, and the sheet does not say whether it is the fine-tuned or zero-shot mode.
