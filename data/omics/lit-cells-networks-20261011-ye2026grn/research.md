# Research notes

Why: the networks-mechanistic lane had no in-window benchmark in the store. This preprint compares six single-cell foundation models (scGPT, scFoundation, Geneformer, LangCell, scCello, scPRINT), each with three ways of extracting a network, against GENIE3, DeepSEM and GRNBoost on the six BEELINE scRNA-seq datasets, scored against four reference network types. The authors developed none of the methods.

Decisions:
- Appendix Tables 4-7 carry every per-dataset value and the mean and std rows; all cells are extracted. Table 1 repeats the TF+500 mean and std and is not extracted separately (see the evidence concern).
- Mean rows are results on a 'six BEELINE datasets' subset with the printed std as a standard deviation across datasets (n = 6).
- Reuses catalog-model-scgpt, catalog-model-scfoundation, catalog-model-geneformer, cell-type-20261009-model-langcell, cell-type-20261009-model-sccello, discovery-model-genie3 and discovery-model-grnboost. New: scPRINT model and DeepSEM method.
- New dataset subsets rather than the existing BEELINE acquired-dataset records, because the gene sets (TFs+500, TFs+1000) and preprocessing differ.
- Metrics early-precision-ratio and auprc-ratio (existing concepts), with the gene set and reference in metric_qualifier.
- No use case covers GRN inference, so no relevance judgement is proposed.

For the reviewer:
- Table 1 labels its middle column 'ChIP-seq' and its caption says cell-type-specific ChIP-seq, but the values are the non-specific ChIP-seq means. Recorded as an evidence concern on the source.
- Table 6 is titled 'AUPR' but prints ratios like Table 7 'AUPRC'; both recorded as auprc-ratio (evidence concern).
- Column headers print 'Langcell', 'scello' and 'GRNboost'; mapped to LangCell, scCello and GRNBoost.
- The dynamic transition probing results are in figures and are not extracted. Table 8 (network topology) is not extracted.
