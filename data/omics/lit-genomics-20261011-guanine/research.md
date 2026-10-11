# Research notes

Part of the 2026-10-11 genomics literature pass (window 2025-10-01 to 2026-10-11). The search log is in `data/omics/lit-search-20261011-genomics/ledger.jsonl`.

## Why this source

GUANinE v1.1 (Robson and Ioannidis, Bioinformatics 2026) extends the GUANinE suite with new model evaluations and two variant tasks (cadd-snv, clinvar-snv). It was chosen because it is a new benchmark version absent from the store, covers about 30 supervised models, gLMs and baselines in one protocol, and the evaluators did not develop most of the models (hgT5 and the T5 baseline are theirs and are recorded as author_reported).

## Record counts

- benchmark: 1
- configuration: 55
- dataset: 8
- evaluation: 225
- method: 8
- model: 8
- protocol: 8
- result: 225
- source: 1

Record counts are after the corrections from the 2026-10-11 independent review. The review, its corrections and the receipt are in `review.md` and `review.json`.

## Extraction notes (written before review; `review.md` takes precedence where they differ)

- Origin: third-party models are independent_paper; hgT5-8195 and the T5 baseline are author_reported. Some Table 2 cells are 'previously reported' (blue in the PDF) and may repeat GUANinE v1 numbers; the colour is not in the XML.
- Metric: every column is printed as 'ρ'. The text does not define it for the Boolean variant tasks (cadd-snv, clinvar-snv); recorded as Spearman correlation x100 as printed. A reviewer should confirm from the GUANinE papers.
- Table 4 has no Eval. column, so its configurations are recorded with 'evaluation mode not printed'.
- Table 2 prints a dagger for Evo2_7B on gpra-c and gpra-d (computationally infeasible); those two results have no numeric value.
- Model family mapping reuses existing store records (Enformer, Borzoi, Sei, ChromBPNet, Caduceus, DNABERT-2, GENA-LM, Evo 2, NT v2, GPN, AlphaGenome, Pangolin, DeepSEA, CADD, phyloP). The store has duplicate family records for DNABERT-2, Evo 2 and Pangolin (catalog-model-* and discovery-model-*); the discovery-model-* records were used.
