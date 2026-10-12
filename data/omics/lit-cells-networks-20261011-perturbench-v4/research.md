# Research notes

Why: PerturBench is a well-known perturbation benchmark suite already in the store, but only from arXiv v1 (Tables 2-3, 76 results, scored on cosine logFC, cosine rank, RMSE and RMSE rank). Version 4 (the NeurIPS 2025 Datasets and Benchmarks paper, posted 2025-10-24) reruns every model over 5 seeds and adds Jiang24, Frangieh21 and OP3 experiments, MMD and DEG recall columns, and mode-collapse diagnostics. All result tables of v4 (2-13) are extracted as a separate source.

Decisions:
- Configurations with the same printed name as v1 (CPA*, CPA* (noAdv), CPA* (scGPT), SAMS-VAE*, Biolord*, LA, LA (scGPT), Decoder, Decoder (Cov), Linear) reuse the v1 configuration records; the evaluations record that these are v4 runs. Table 7-8 print 'BioLord*', mapped to the Biolord* configuration. Table 12 'DecoderOnly' is the decoder with only covariates as input (Appendix C.7.1; Figure C.2A), so it is mapped to the Decoder (Cov) configuration (review P1). New configurations: SAMS-VAE* (S), GEARS (PerturBench run, configuration of catalog-model-gears) and DecoderOnly (+ perturbations).
- New dataset subsets and protocols for v4: the v1 records describe different splits and runs.
- Origin: independent_paper for the published models the authors reimplemented or wrapped (CPA*, SAMS-VAE*, Biolord*, GEARS); author_reported for the authors' own baselines and ablations.
- Units follow the v1 records for comparability (cosine and rank metrics 'fraction', RMSE 'unit-unreported').
- New metric concepts in data/vocab/metric.ttl: perturbench-energy-mmd (MMD and MMD PCA, distinguished by metric_qualifier), perturbench-rmse-transposed-rank and perturbench-matrix-distance.
- Relevance judgements (needs_review) proposed for use-case-genetic-perturbation-response on the Norman19, Jiang24 and Frangieh21 protocols (genetic perturbations). Srivatsan20 and OP3 are chemical perturbations and are not mapped.

For the reviewer:
- Table 4 caption says 70% of perturbations from 9 of 30 states are held out; Appendix D.4 describes 12 cytokine-cell line combinations. Recorded as a source limitation, not resolved.
- Tables 12-13 print single values with no spread; their RMSE values differ from the 5-seed means in Tables 5 and 8 for the same models, so they are a separate protocol.
- Check the '-' cells are absent, not zero.
