# AMP issue #15: DELFI 2019 internally cross-validated cancer detection

Candidate only. Cristiano et al., Nature 570, 385–389 (2019), author manuscript PMC6774252. DOI 10.1038/s41586-019-1272-6

Endpoint: 73% percent; uncertainty: 95% CI 67%–79%; sensitivity intervals from 2,000 bootstrap replicates. Numerator 152; denominator 208.

Locator: PMC6774252 Table 1 T1 Cancer row / 98% specificity columns; Results P15; Methods P34; Extended Data Fig. 7 F11.

Population: 208 patients with seven cancer types and 215 healthy individuals used for classifier; broader study abstract 236 cancers/245 healthy is not classifier denominator.

Workflow: DELFI stochastic gradient boosting: GC-corrected short/long fragment coverage in 504 genomic bins, 39 autosomal arm Z-scores and mitochondrial representation. R gbm 2.1-4, n.trees=150, interaction.depth=3, shrinkage=0.1, n.minobsinside=10.

Split: 10-fold cross-validation repeated 10 times; feature selection and model estimation on training folds only

Conventional baseline: Same Fig. 4/Results P15 feature comparisons: chromosomal-arm copy number ML AUC 0.88, individual copy-number scores AUC 0.78, mitochondrial copy number AUC 0.72; separate ROC endpoints, not sensitivity-matched comparisons.

Retrieval: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6774252/fullTextXML at 2026-10-07T12:24:27.091080+00:00; SHA-256 1c9b4eca18f8e2f11c647f938aa55dea0a20e3db17e0bb5ba5eb839dab182923.

Limitations:

- 4 of 215 healthy individuals misclassified at source-labelled 98% specificity. Retain rounded printed specificity; do not recompute sensitivity.

- Internal repeated cross-validation is not independent prospective screening validation; clinically identified cancers and healthy comparators differ from intended screening population.

- DELFI composite features include CNAs/mtDNA, so this exact result is not pure fragmentation alone.

- cfDNA signal is not purified ctDNA, tumour fraction limit is unreported for this endpoint.

- Combined mutation+DELFI 115/126 (91%) is a different subset/configuration and is excluded.

No matching DOI/workflow found in baseline-catalogue.json or both 2026-10-07 archived record bundles; no existing identity reused.

Candidates remain needs_review pending parent source check.
