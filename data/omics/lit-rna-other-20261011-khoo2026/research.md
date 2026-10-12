# Research notes: Khoo 2026, Nearest-neighbour baselines for fingerprint prediction from MS/MS spectra (arXiv 2610.02249v1)

## Why this source

Short report comparing nearest-neighbour fingerprint prediction under three information assumptions (no formula, formula, formula-annotated peaks) on NPLIB1 and MassSpecGym scaffold and random splits. Gives baselines for fingerprint prediction that make the information each method uses explicit.

## What was extracted

Every cell of Tables 1 (binarised Jaccard index) and 2 (cosine of the raw prediction).

Record counts: configuration 16, dataset 4, evaluation 64, method 1, protocol 12, result 128, source 1 (226 records). Every record has status `needs_review`.

## Identity decisions

One new method family (nearest-neighbour fingerprint retrieval) with 16 configurations (similarity by assumption). Protocols are split by dataset, split and assumption because the assumption fixes the allowed inputs.

## Not extracted and gaps

- Table 3 (dataset sizes, coverage, leakage, oracle) is used for dataset descriptions only; Table 4 (sub-formula hyperparameters) not extracted.
- The DreaMS checkpoint used for embeddings is not stated.

## For the reviewer

- New metric concept `fingerprint-tanimoto-similarity` needs review.
- Fingerprint prediction is not retrieval; no relevance judgement was added for the mass-spectrum shortlisting use case.
