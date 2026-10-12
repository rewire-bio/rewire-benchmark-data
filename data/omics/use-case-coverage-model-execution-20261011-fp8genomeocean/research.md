# Research: Yu et al. 2026, FP8 inference on GenomeOcean (bioRxiv 10.64898/2026.08.09.743676 v1)

Use case: `use-case-diagnostic-genomics-model-execution`. Pass: diagnostic genomics execution literature search, window 2025-10-01 to 2026-10-11. The search log, candidates and gaps for the whole pass are in `data/omics/lit-search-20261011-uc-execution/` (ledger, scope audit and report).

Selected because it is the only in-window source found that prints inference throughput, peak GPU memory, power and energy efficiency for a genomic foundation model on stated hardware, with spread over five trials, which addresses the use case's gaps on foundation-model execution, peak memory and repeated runs.

Modelling:
- Configurations link `configuration_of` to the existing `lit-genomics-20261011-geneb-model-genomeocean` family.
- Two protocols (Protocol A embedding, Protocol B generation), as the paper separates them and says their throughputs are not comparable across engines.
- Throughput uses the existing `inference-throughput` metric with unit `sample-per-second` and `unit_detail` naming tokens, following the existing use with reads per second. New concepts: metrics `throughput-change`, `power-draw`, `energy-efficiency`; units `watt` (exactMatch QUDT W) and `sample-per-joule`.
- Origin `author_reported`: three authors are at the DOE Joint Genome Institute, where GenomeOcean was developed; the paper prints no competing-interest statement.
- Uncertainty: throughput, power, efficiency and ARI carry the printed standard deviation with n = 5 (seeds 42-46); perplexity carries n = 96 with the paper's note that it reflects sequence heterogeneity.

Things a reviewer should judge:
1. Whether tokens per second may be recorded under `sample-per-second`, or whether a token unit is needed.
2. Whether the GenomeOcean configurations should name exact Hugging Face checkpoints; the paper names only scales (100M, 500M, 4B).
3. The `proxy` relevance: microbial sequence and embedding or generation workloads, not diagnostic pipelines.

## Records

| Kind | Count |
| --- | --- |
| claim | 2 |
| configuration | 9 |
| dataset | 2 |
| evaluation | 9 |
| protocol | 2 |
| result | 33 |
| source | 1 |
