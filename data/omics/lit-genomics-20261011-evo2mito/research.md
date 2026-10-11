# Research notes

Part of the 2026-10-11 genomics literature pass (window 2025-10-01 to 2026-10-11). The search log is in `data/omics/lit-search-20261011-genomics/ledger.jsonl`.

## Why this source

Mathur and Sachidanandam (bioRxiv 2026) test Evo2 zero-shot on mtDNA variants and compare it with seven mitochondrial predictors. Chosen as an independent Evo2 VEP evaluation outside nuclear coding regions. Lower confidence than the other batches (see judgement items).

## Record counts

- configuration: 1
- dataset: 1
- evaluation: 1
- protocol: 1
- result: 8
- source: 1

Record counts are after the corrections from the 2026-10-11 independent review. The review, its corrections and the receipt are in `review.md` and `review.json`.

## Extraction notes (written before review; `review.md` takes precedence where they differ)

- Comparator provenance: the source does not say whether APOGEE 2, APOGEE 1, COVEC WMV, CAROL, MetaSNP, Condel and MToolBox DS were scored on the authors' test split or quoted from the APOGEE 2 paper. Their evaluations are origin unreported and the source carries an evidence concern.
- Evo2 balanced accuracy is 0.846 in Table 2 but 87.6% in the Figure 2B legend.
- The Evo2 checkpoint is not stated.
