# Research: therapeutic target validation use-case pass, 2026-10-09

Use case: `use-case-therapeutic-target-validation` ("Which targets should I test to change a defined disease-relevant phenotype?"). Existing judgements, both from the Cancer Immunotherapy Data Science Challenge (CPPC): the Challenge 2 prospective target-ranking score, and a prospective nomination campaign counting targets that improve a T-cell state. The 2026-10-07 dossier (`docs/reviews/use-cases/phenotype-perturbation-selection-2026-10-07.md`) logged seventeen earlier queries for the neighbouring perturbation-selection use case; this pass did not repeat them and kept their exclusions.

Goal: comparisons of several target-prioritisation methods on the same experimentally tested target set, with printed per-method values, respecting the use case's rule that untested targets are not negatives.

Bounds: cutoff 2026-10-09; budget 25 queries, 7 used; at most 3 sources, 3 extracted; lean batch (770 records, 1.2 MB). Lane `cells-spatial` content but filed under the use case's own facets (`cells-tissues`, `research`). Worker: Claude (Opus 5.5) research agent; no human review claimed.

This file is the pass's dossier, as in the earlier batches.

## Queries

Full entries: `search-use-case-target-validation-research-q1` to `q7` in `data/omics/search-ledger.jsonl`.

| # | Query (short form) | Channel | Outcome |
| --- | --- | --- | --- |
| 1 | target prioritisation benchmark against CRISPR screen hits, BioDiscoveryAgent, GeneDisco | web search | Roohani et al. 2025 and GeneDisco taken forward |
| 2 | GWAS gene prioritisation (PoPS, MAGMA, L2G) against CRISPR-validated genes | web search | Ji et al. 2025 found; endpoint is drug approval, not a screen |
| 3 | medRxiv and Europe PMC lookups for Ji et al. 2025 | bioRxiv/Europe PMC API | CC BY; XML and supplementary data screened |
| 4 | CRISPR screen gene prioritisation vs GWAS methods, open access | Europe PMC | 18 hits, screened by title; none is a method comparison |
| 5 | single-cell foundation models predicting screen hits (Geneformer, scGPT) | web search | Liu et al. 2025 found; its tables are page images |
| 6 | LLM agents for perturbation design, hit ratio, follow-up evaluations | web search | AssayBench, AssayBench-Loop and the Gupta replication surfaced |
| 7 | Gupta et al. permuted-label replication of BioDiscoveryAgent | web search | Resolved to EMNLP Findings 2025; taken forward |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Roohani et al. 2025 (ICLR), Table 1 | Extract all 240 values | Twenty selection methods on six CRISPR screens with a measured phenotypic readout each: random, a human pathway baseline, seven acquisition functions, DiscoBAX, nine LLM agents and one hybrid. The closest thing found to the use case's question in retrospective form. |
| Gupta et al. 2025 (EMNLP Findings), Tables 1 and 2 | Extract all 55 values | An independent replication of the same task that adds the control the original lacks: the same agent given randomly permuted feedback, plus classical sequential designs over the same embeddings. |
| De Brouwer et al. 2026 (AssayBench preprint), Table 3 | Extract all 144 values | Sixteen systems ranking genes for 571 described screens, with a post-cutoff cohort that probes prior exposure to the literature. The broadest multi-system comparison found. |
| Gupta et al. Table 3 | Not extracted | Promotes the authors' own hybrid method; the limitation it supports is already carried by Tables 1 and 2. |
| Ji et al. 2025 (medRxiv) | Excluded | Compares nearest gene, Open Targets locus-to-gene and eQTL colocalisation, but the endpoint is drug-approval status rather than a measured phenotype, and the per-method values are in figures. |
| Liu et al. 2025 (bioRxiv, scISP) | Excluded | Compares Geneformer, scGPT and GEARS on in-silico perturbation, but every table in the JATS XML is a page image (`653338v1_tbl1` and similar), so no value could be parsed without reading a figure. |
| GeneDisco (arXiv:2110.11875) | Excluded | The benchmark the Roohani baselines come from, but its text layer contains no result tables. |

## How negatives are defined, and why every judgement is proxy

All three sources define a hit by the screen's own criterion and score only over genes that screen assayed:

- **Roohani and Gupta**: a hit is a gene whose measured response passes a threshold tau. Non-hits are genes the screen assayed that did not pass. The candidate pool is the assayed set, over 18,000 genes per screen and 1,061 for the Scharenberg screen. Neither source prints tau or the hit count; Gupta prints its own ground-truth hit counts per screen (654, 920, 943, 924, 924).
- **AssayBench**: a hit is a gene satisfying its screen's significance criterion. Non-hits are assayed genes with relevance 0. Genes the screen did not assay are removed from the ranked list by a condensing step rather than counted as false positives. In bidirectional screens, genes significant in the opposite direction take negative relevance and are penalised.

So no benchmark treats an untested gene as a negative, which is what the use case requires. The cost is the mirror image: none of them tests whether a method would have found a target outside the assayed pool. Together with the retrospective replay, the restricted pool and the fact that recovering a screen's hits is not the same as a target being worth pursuing, that is why all three judgements are `proxy`. The definitions are recorded on each dataset's `scope_note`, each protocol's `metric_definition` and `limitations`, and each judgement's rationale.

## The replication finding, and how it is recorded

Gupta et al. report that the agent compared in Roohani et al. scores the same when its experimental feedback is replaced by randomly permuted outcomes, and conclude that the models tested do not perform in-context experimental design. In the stored numbers the permuted variant scores at least as high as the agent on three of the five screens with a Llama-3.1-8B backbone and on three of five with a Claude 3.5 Sonnet backbone.

This challenges how the Roohani numbers should be read rather than their transcription, and it comes from a different source, so it is not an `evidence_concerns` entry on either source. It is recorded as:

- a `limitations` entry on `tgtval-20261009-protocol-roohani2025-hitratio-round5`;
- a sentence in the rationale and `limitations` of both affected judgements;
- a descriptive claim, `tgtval-20261009-claim-gupta2025-permuted-feedback`;
- a proposed `evidence_gaps` line in `coverage.json`;
- a paragraph in the `summary_proposal`.

Both sets of numbers are stored exactly as printed. The two papers' configurations link to the same `tgtval-20261009-method-biodiscoveryagent` record, so a reader sees them side by side, and the shared screens link to the same dataset records.

## Things a reviewer should judge

1. **Cross-source arithmetic check (passes).** Gupta's "BDA (Reported Numbers)" row divided by its printed ground-truth hit counts reproduces Roohani's all-gene hit ratios for Claude 3.5 Sonnet on all four shared screens to the printed rounding: 68.01/654 = 0.104 against 0.104, 87.4/920 = 0.095 against 0.095, 39.6/943 = 0.042 against 0.042, 60.72/924 = 0.0657 against 0.066. This indicates both sources score the same screens and the same hit sets, and that the row is a unit conversion rather than a new run. Recorded as `tgtval-20261009-claim-gupta2025-reported-numbers-conversion`.
2. **Replication gap in the same setting.** Gupta's own re-run of the Claude 3.5 Sonnet agent is below the reported numbers on three of four shared screens and far below on one: 59.4 against 68.01 (interleukin-2), 78.8 against 87.4 (interferon-gamma), 31.6 against 60.72 (tau), and above on Carnevale (43.8 against 39.6). Both rows are stored, with the reported row's origin set to `paper_compilation`.
3. **Screen naming across sources.** Roohani's caption defines `Schmidt1` as the interferon-gamma screen and `Schmidt2` as interleukin-2; Gupta names its columns `IL2` and `IFNG` in the opposite order. The extractor maps both to the same dataset records, and check 1 above confirms the mapping. Worth re-checking, since a swap here would silently misalign 70 results.
4. **Gaussian process rows printed identically.** Gupta Table 2 prints the same five values for Gaussian process optimisation under both backbone headings, although the embeddings differ. Recorded as `source_anomaly` on those results.
5. **Precision@100 denominator.** AssayBench divides by `min(100, positive-relevance genes)`, so for screens with fewer than 100 hits it is not precision over 100 predictions. Recorded on every Precision@100 result and in the protocol; the metric concept reused is `precision-at-100`. A reviewer may prefer a separate concept.
6. **Hit ratio stored as recall.** Roohani's hit ratio is the fraction of a screen's hits that were selected, which the source itself calls similar to recall, so `recall` is reused with the round, batch size and scoring population in `metric_qualifier`. The alternative is a new concept.
7. **Essentiality list not printed.** The `N/E` columns count non-essential genes only, but the source does not say which gene list defines essentiality. Recorded as a claim.
8. **Uncertainty not carried.** Roohani Table 7 repeats Table 1 with one standard deviation; it was not extracted, so no stored result from that source has an uncertainty. All 439 results carry `missing_metadata.uncertainty` with reason `unreported`.
9. **AssayBench is a preprint** and its curation uses an LLM-assisted step over BioGRID metadata to extract phenotype descriptions and effect directions. Recorded as a claim and in the protocol's limitations.
10. **Oracle kNN is not a usable method.** It picks the training screen that maximises the metric against the target screen, so it uses the answer. Recorded in its configuration description as an upper bound.

## Coverage

Bounded pass; not systematic. Not covered: prospective nomination campaigns beyond the CPPC records already stored; AssayBench-Loop (arXiv:2609.11877); the GWAS-to-drug-target literature; dependency, tractability and therapeutic-window evidence, which the use case excludes as needing different evidence; two-gene and 30-round variants of the Roohani benchmark; the chemical-property half of the Gupta paper.
