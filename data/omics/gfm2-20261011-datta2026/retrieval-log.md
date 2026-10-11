# Retrieval log: Datta et al. 2026

Worker: Claude (Opus 5.5) research agent lit-gfm-2 in Claude Code. No human review claimed. Downloads went to
a session scratch directory and were read as data (`pdftotext -layout`, Python under `-I`). No model was run.
Times are UTC.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 00:39:51 | arXiv API search for genomic foundation model benchmarks and evaluations in the window (ledger q7) | 200 | | 32 entries; this preprint among them |
| 00:45:40 | `arxiv.org/pdf/2608.05329v1` (screening copy) | 200 | 3,571,652 | PDF; read for table structure |
| 00:51:27 | Same URL, pinned retrieval | 200 | 3,571,652 | SHA-256 `df36e477...` |
| 00:51:28 | `arxiv.org/abs/2608.05329v1` | 200 | | Licence: arXiv perpetual non-exclusive distribution 1.0; v1 only |
| 00:51:29 | `pdftotext -layout` (poppler 26.08.0) | | | Text layer; 599 non-empty lines |

## What was read

- Section 2.2 (model inventory with parameter counts), Sections 2.3 to 2.7 (pooling, probes, readout grid,
  variant representation, controlled fine-tuning), Section 3.1 (datasets), Section 3.2 (metrics) and
  Section 3.3 (reporting). These fix the protocols, the metric per task family and the provenance of the
  fine-tuned column.
- Table 1, all 72 cells: the frozen score with its standard deviation and the reference fine-tuned score with
  its standard deviation where printed. 144 results.

## What was not read as results

- The recovery percentage inside each Table 1 cell and the two average-recovery rows. Recovery is defined in
  Equation 7 as frozen score divided by fine-tuned score times 100, so it is a ratio of two extracted values
  and has no metric concept in `data/vocab/metric.ttl`. A claim record states this.
- Table 2 (Genomic Benchmark) and Table 7 (variant-effect prediction on Genomics Long-Range Benchmark tasks).
  Both are in scope and would be valuable, but the source does not print which metric each column reports:
  Section 3.2 says only "the benchmark-reported metric ... where applicable". Assigning a metric concept would
  be a guess, so these tables are recorded as a gap.
- Tables 3 to 6, 8 and 9 (readout-sensitivity diagnostics, validation-selected readouts, layer-wise probing,
  in-silico mutagenesis, embedding geometry, and the controlled DNABERT-2 LoRA comparison with run times).
  Table 9 is the one matched frozen-versus-adapted comparison in the paper and is worth a later pass; its
  metric per task is again unstated.
- All figures.
