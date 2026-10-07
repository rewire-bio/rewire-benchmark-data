# AMP #12: Inherited patient-RNA splicing validation

Primary source: Detection of aberrant splicing events in RNA-seq data using FRASER. https://doi.org/10.1038/s41467-020-20573-7
Retrieved: 2026-10-07T12:23:57.289375+00:00; source-byte SHA256: 1f1f028cddd9145bd342422ec768ecdca6ecfeb6f9bc2e114ecfab061b5e93a6

Evidence scope: direct patient skin-fibroblast RNA evidence; retrospective known-defect recovery

Randomly remove samples without known pathogenic splicing defect; measure fraction of 13 known events recovered at reduced cohort size. At 30 samples, 85% / mean 11 of 13; 100 samples needed to recover all irrespective of selected samples. FRASER controls latent confounding and models beta-binomial count fractions; cohort analysis uses FDR<0.1 and |effect|>0.3.

Population: 119 RNA-seq samples from 105 individuals; 13 known pathogenic splicing events for sample-size analysis
Input: non-strand-specific RNA-seq; STAR 2.4.2a two-pass, hg19

## Numerical extraction

- FRASER (2021 article implementation): mean known pathogenic splicing-event recovery at 30 samples = 85% %; Results subsection rare disease cohort, paragraph Par18; Supplementary Fig. S20 referenced. Uncertainty: None.
- FRASER (2021 article implementation): mean recovered known pathogenic events at 30 samples = 11 events; Results Par18; Supplementary Fig. S20 referenced. Uncertainty: None.
- FRASER (2021 article implementation): median alternative acceptor outlier genes per sample = 12 genes/sample; Results Par16; Fig.6a. Uncertainty: None.
- FRASER (2021 article implementation): median alternative donor outlier genes per sample = 7 genes/sample; Results Par16; Fig.6a. Uncertainty: None.
- FRASER (2021 article implementation): median splicing efficiency outlier genes per sample = 10 genes/sample; Results Par16; Fig.6a. Uncertainty: None.

## Baselines

- Original Kremer LeafCutter-based pipeline: 1,725 outlier events versus FRASER 1,666, Par16/Fig6b. Counts are workload endpoints, not direct sensitivity comparison.
- PCA z-score, naive beta-binomial, LeafCutterMD and SPOT separately evaluated elsewhere in article; do not transfer simulation scores to this patient protocol.

## Limits and unknowns

- Direct patient-RNA known-event recovery does not establish prospective diagnostic accuracy or patient outcome benefit.
- Known pathogenic-event ascertainment and same-cohort retrospective selection can bias recovery.
- 30 is RNA sample subset size; do not silently equate to 30 independent patients.
- No blinded pathogenicity adjudication, general tissue transfer, VUS reclassification sensitivity or transcriptome-wide precision established by this endpoint.
- Subsampling repeats, exact score aggregation and numeric uncertainty unavailable from inspected main-text endpoint; supplementary PDF DNS retrieval failed.
- FRASER author correction 2022 changes GTEx version V7 to V6p; patient-Kremer endpoint not affected according to correction search result; exact correction bytes not retrieved.

Missing metadata: {"version": "Exact FRASER package version unextracted; do not assign current FRASER2.0", "uncertainty": "No numeric CI for 85% printed in Par18; supplement inaccessible", "replicate_count": "Subsampling repetition count unextracted"}

Candidate status is needs_review. Main text/XML inspected by automated curator; no experimental reproduction or human scientific review. No clinical benefit claimed. See candidates.json for integration metadata.
