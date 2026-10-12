# Research notes

Why: an independent (the authors developed none of the models) and recent benchmark of six single-cell and spatial foundation models across clustering, continual pretraining, supervised annotation and perturbation prediction, including spatial-aware models (Nicheformer, scGPT-spatial, Novae) that the store did not hold.

Decisions:
- New model families: Nicheformer, CellPLM, scGPT-spatial, GenePT (printed as GenePT-w), scELMo, Novae. Configurations per model and mode (zero-shot, continual pretraining, fine-tuned, GEARS decoder, k-means).
- One protocol per task and dataset. Dataset subsets keep the printed codes. The spatial codes BC, MH and ME are not defined in the tables; the Methods describe HBCA1 (breast cancer Visium), MHPC (mouse hippocampus Slide-seqV2) and MOSTA E9.5 (mouse embryo Stereo-seq), and the Results text ties BC to HBCA1 and ME to MOSTA. The reviewer confirmed the mapping from the Figure 2 legend, which the source limitation now cites (C4).
- Metrics: ARI, NMI, accuracy, precision, recall, macro-F1, AUPRC, AUROC, MSE, Pearson and Pearson delta map to existing concepts with qualifiers. Silhouette is on the native -1 to 1 scale, so a new concept silhouette-score was added (not the scIB rescaled ASW).
- PR-AUC and ROC-AUC are macro-averaged (Methods, 'Cell type annotation'). Precision and recall are described as global without a definition, and appear to be averaged differently between models; recorded in qualifiers and as an evidence concern on the source (review C2, C3).
- Relevance judgements (needs_review): Table 5 perturbation protocols (Norman, Adamson, Replogle) to use-case-genetic-perturbation-response, and Table 4 annotation protocols (ATAA, HS, BMMC, SEAAD) to use-case-cell-type-annotation-transfer, both proxy.

For the reviewer:
- No conventional baseline appears in any table, so the protocols compare foundation models only.
- The 'DE' perturbation metrics use the top 20 differentially expressed genes per perturbation condition (Methods, 'Perturbation prediction'); recorded in qualifiers (review C1).
- Supplementary Table S2 (k-means) covers GenePT-w only.
