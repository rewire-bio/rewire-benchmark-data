# Research notes: Zhong et al. 2026, FlexMS (arXiv 2602.22822v4)

## Why this source

New benchmark for molecule-to-MS/MS spectrum prediction with a grid of 11 molecular embedders and 3 predictor heads on MassSpecGym.

## What was extracted

Every cell of Table 2: cosine and Jensen-Shannon similarity for 33 embedder-predictor configurations.

Record counts: configuration 33, dataset 1, evaluation 33, model 3, protocol 1, result 66, source 1 (138 records). Every record has status `needs_review`.

## Identity decisions

New families for the MassFormer, NEIMS and MolMS predictor heads; one configuration per embedder-predictor pair. Embedder abbreviations are expanded from the Table 2 caption.

## Not extracted and gaps

- Tables 3 to 8 and S1 to S5 (efficiency, sparsity, learning rate, pretraining, transfer, CASMI retrieval) were not extracted.
- The bin resolution for Table 2 is not stated in its caption.

## For the reviewer

- Benchmark authors evaluate third-party architectures they reimplemented; origin set to `independent_paper`.
- Check whether Table 2 can be tied to a bin resolution from the text; it is recorded as unreported.
