# Research notes: Bůžková et al. 2026

## Why this source

An independent evaluation: the authors develop none of the nine models they compare, and they give BLAST the
same labelled reference sequences, so the comparison is a controlled one. It covers a model generation the
store did not hold any results for (NTv3, three sizes) and prints complete tables.

## How the records are shaped

- One configuration per model and pooling strategy, because the pooling choice changes the result by up to
  0.26 accuracy for NTv3-650M. Pooling is part of the configuration, not of the protocol.
- Three protocols: the pooling comparison on the 33-class dataset (Table 3), the BLAST comparison (Table 7)
  and the long-sequence task (Table 10). Table 7 reports four metrics on two datasets, so its evaluations
  are split by dataset.
- `origin` is `independent_paper` on every evaluation, including the BLAST rows: the authors ran both sides.
- The nearest-neighbour setup is a probe over labelled reference embeddings. The paper says so explicitly
  (Section 2.7) and so does each protocol's `limitations`; it is not zero-shot classification.

## Judgement calls a reviewer should check

1. The star in `⋆0.9265` (Table 3, NTv3-650M, max pooling) marks the table's overall best. It is kept inside
   `printed_value` because that is the printed string, with the reason in the result's `review.note`.
2. The 40-class dataset is recorded as its own dataset record rather than a subset, because the 33-class set
   is a refinement that removes seven classes and the paper reports both as separate populations.
3. Long-sequence rows for DNABERT-2, NTv2-50M and NTv2-250M are chunk-scored, which the paper flags in a
   footnote. They share a protocol with the whole-sequence rows but carry their own limitation, and their
   `comparison.aggregation` says "Over chunks". A reviewer may prefer two protocols.
4. Only accuracy is extracted from Table 3; macro F1, precision and recall for those configurations are not
   printed there (they appear for the best configuration only, in Table 7).

## Related store records

Feng et al. 2025 (`amp-feng-20261007-*`) and Tang et al. 2025 (`regulatory-variant-20261009-*`) already hold
Nucleotide Transformer and DNABERT-2 results on regulatory and variant tasks. This batch adds a retrieval and
taxonomy task and the first NTv3 results, so no evaluation here supersedes an existing one.
