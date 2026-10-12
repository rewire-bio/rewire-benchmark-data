# Research: Aspidova et al. 2026, ModernGENA (bioRxiv 10.64898/2026.04.21.719816 v1)

Use case: `use-case-diagnostic-genomics-model-execution`. Pass: diagnostic genomics execution literature search, window 2025-10-01 to 2026-10-11. The search log, candidates and gaps for the whole pass are in `data/omics/lit-search-20261011-uc-execution/` (ledger, scope audit and report).

Selected because it compares inference throughput and the largest batch that fits in memory for four genomic foundation model families (ModernGENA, GENA-LM, DNABERT-2, NTv2) on one stated GPU across input lengths, the only multi-model GFM execution table found in the window.

Modelling:
- New model family `model-moderngena`; GENA-LM, DNABERT-2 and NTv2 configurations link to `regulatory-variant-20261009-model-gena-lm`, `discovery-model-dnabert-2` and `catalog-model-nt-v2`.
- One protocol; sequence length is in `metric_qualifier`, so comparisons pair the same length. New metric `maximum-batch-size` (unit `count`).
- Origin: ModernGENA and GENA-LM `author_reported` (the same group develops both); DNABERT-2 and NTv2 `independent_paper`.

Things a reviewer should judge:
1. Scale of the printed throughput. The column says tokens/s, but 552.44 tokens/s at a batch of 3,631 sequences of 256 tokens would mean about 28 minutes per batch, and the paper gives the ModernGENA pretraining throughput as 1.33M tokens/s on eight A100s (Section 3.2.4). The printed unit may be thousands of tokens per second or another rate. Values are kept as printed; the reviewer should decide whether this needs a source-level `evidence_concerns` entry.
2. Whether `inference-throughput` with unit `sample-per-second` is acceptable here.
3. The `proxy` relevance.

## Records

| Kind | Count |
| --- | --- |
| claim | 1 |
| configuration | 9 |
| dataset | 1 |
| evaluation | 9 |
| model | 1 |
| protocol | 1 |
| result | 92 |
| source | 1 |
