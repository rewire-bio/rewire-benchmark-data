# Research notes

Part of the 2026-10-11 microbial and interactions literature pass (window 2025-10-01 to 2026-10-11).
The search log is in `data/omics/lit-search-20261011-microbial-interactions/ledger.jsonl`.

## Why this source

This is the controlled comparison the interactions lane lacked for protein-protein interaction
prediction: the same two benchmarks (OGBl-ppa and HuRI), the same GNN link predictors, and the only
thing varied is the protein representation, over three protein language models (ESM-2, ProtTrans,
ProGen2), three structure or inverse-folding models (ESM-IF1, ProstT5, PiFold), three knowledge-graph
embeddings (TransE, ComplEx, RDF2Vec), a majority-vote ensemble, and a random-feature baseline. The
MLP rows are a protein-only ablation with no network information, which separates what the embedding
contributes from what the graph contributes.

Its headline reading is that knowledge-graph embeddings of protein function beat sequence and
structure embeddings on both benchmarks, and that the strongest architecture narrows the gap to
nothing: in the N-GS+S row on OGBl-ppa, random node features reach 0.5693 Hits@100 against ESM-2 at
0.4369, and only the knowledge-graph embeddings do better (RDF2Vec 0.5991, ComplEx 0.5722).

## Record counts

- benchmark: 1
- configuration: 77
- dataset: 2
- evaluation: 308
- method: 11
- model: 3
- protocol: 4
- result: 308
- source: 1

## Extraction notes (written before review)

- 7 architectures x 11 feature columns = 77 configurations; each has a Hits@100 and an Accuracy value
  on each of the two datasets, so 308 results.
- The architecture is the configured method and the embedding model is linked with `uses_model`, so
  the same ESM-2 family record carries all seven architectures that use it.
- `hits-at-100` is a new metric concept, defined as the OGB ogbl-ppa official metric.
- Values are fractions as printed (0 to 1), recorded as `unit: fraction`.
- Everything is `independent_paper`: none of the eleven embedding methods or four GNN architectures
  is the authors' own; they ran all of them.
- **Needs a reviewer's judgement.** The Results prose conflicts with the tables in three ways, all
  recorded in the source's `evidence_concerns`: ProtT5 is named where the tables print ProstT5; a
  "GraphSAGE with DistMult (+38% Hits@100 for HuRI)" result is reported although DistMult is not a
  column; and the stated gains cannot be derived from the printed cells (for example "ESM-2 with
  GraphSAGE (+6% Hits@100)" for OGBl-ppa, where the table prints GS random 0.0104 and GS ESM-2
  0.2421). The printed values are what the records hold. The reviewer should decide whether the
  concern is enough to block comparisons.
- No uncertainty, seed count or number of runs is printed for either table.
