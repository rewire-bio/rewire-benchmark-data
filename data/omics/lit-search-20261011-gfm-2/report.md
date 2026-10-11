# Literature pass: genomic foundation models, 2026-10-11

Lane `genomics`, narrowed to genomic foundation models: independent evaluations that compare several DNA
language or sequence foundation models, plus reviews mined for the primary evaluations they cite.
Window: posted or published 2025-10-01 to 2026-10-11. Worker: Claude (Opus 5.5) research agent `lit-gfm-2`.
No human review claimed, and nothing in this pass is reviewed: every record is `needs_review`.

Benchmark suites (BEND, GUE, Genomic Benchmarks, the Nucleotide Transformer benchmark, DART-Eval, GenBench,
GUANinE, DNALONGBENCH, GENEB, TraitGym) were left to the parallel `lit-genomics` pass by agreement; the
message sent to that teammate lists what I skipped and what I took.

Searches: 25 ledger entries, 22 of them exact queries (16 Europe PMC, 3 arXiv, 1 web search, 1 review
reference-mining entry over eight reviews, 1 retrieval entry). Scope decisions: 45 (3 included, 42 excluded).

- `data/omics/lit-search-20261011-gfm-2/ledger.jsonl`
- `data/omics/lit-search-20261011-gfm-2/scope-audit.jsonl`
- generators: `extract/build-ledger.py`, `extract/build-scope-audit.py`, raw query log `extract/querylog-raw.jsonl`

## Candidates extracted

| Batch | Source | Why | Records |
| --- | --- | --- | --- |
| `data/omics/gfm2-20261011-buzkova2026` | Buzkova et al. 2026, bioRxiv 10.64898/2026.09.25.754388, CC BY 4.0 | Nine Nucleotide Transformer and DNABERT models, frozen embeddings with nearest-neighbour retrieval, against BLAST on the same reference set. First NTv3 results in the store. Independent of every model compared. | 192: 1 source, 1 model, 38 configurations, 3 datasets, 3 protocols, 47 evaluations, 90 results, 9 claims |
| `data/omics/gfm2-20261011-datta2026` | Datta et al. 2026, arXiv:2608.05329v1 | Frozen-embedding probes against fine-tuned references for HyenaDNA, NT-500M, GENERATOR-v2 and Omni-DNA on 18 Nucleotide Transformer benchmark tasks: how much a frozen model recovers, by task family. | 303: 1 source, 2 models, 8 configurations, 1 dataset, 2 protocols, 144 evaluations, 144 results, 1 claim |
| `data/omics/gfm2-20261011-you2026` | You et al. 2026, Nat Commun 10.1038/s41467-025-66899-y, CC BY-NC-ND | Eleven pre-trained language models and five task-specific methods, same splits, same 500 bp input, three runs each, per-method values printed in the supplement. Splicing tables only. | 266: 2 sources, 7 models, 2 methods, 13 configurations, 4 datasets, 6 protocols, 55 evaluations, 176 results, 1 claim |

761 records in total, 410 of them results. Each batch holds `batch.jsonl`, `claims.csv`, `sources.md`,
`retrieval-log.md`, `research.md` and its deterministic extractor under `extract/`. Shared record builders
live in `data/omics/lit-search-20261011-gfm-2/extract/gfm2lib.py`.

Validation: the three batches load against the store's schema, vocabularies, attribute registry and relation
rules together with the current store (761 new records, no ID collisions). They are **not** added to the store
and **not** validated against the SHACL shapes yet; `npm run records -- add` does that, and it runs after
review, as `extract-evaluations` step 7 requires.

## Candidates not extracted

In scope, worth a later pass:

| Source | Reason |
| --- | --- |
| Mathur and Sachidanandam 2026, Evo 2 blind spots (10.64898/2026.03.10.710786) | Could not be retrieved: bioRxiv returned HTTP 429 on two attempts. Recorded as a gap, not as "nothing found". The best candidate for the next pass. |
| Cheng and Zhang 2026, Mechanistic Invariance Test (arXiv:2604.06549v1, CC BY) | Five genomic language models with complete printed tables, but its headline metrics (compensation sensitivity score, spacing consistency ratio) have no concept in `data/vocab/metric.ttl`. Extraction needs a reviewed vocabulary addition first. |
| Baranwal et al. 2026, Dark Regulome (arXiv:2606.06834v2) | Caduceus, HyenaDNA and Enformer on 30,448 dark-genome elements; values in figures, and its variance-decomposition metrics are not in the vocabulary. |
| Sun et al. 2026, ancestry-stratified Borzoi and AlphaGenome (10.64898/2026.06.22.730889, CC BY) | Multi-ancestry eQTL evaluation; per-model values are in figures and Supplementary Tables S1 to S6, which were not retrieved. |
| Ramarao-Milne et al. 2026, AlphaGenome cross-species (10.64898/2026.07.10.737654) | Mouse-versus-human transferability; values quoted in prose and figures, no comparison table. |
| He and Florea 2026, splice site and exon annotation (10.64898/2026.02.22.707219) | SegmentNT, SegmentEnformer, SegmentBorzoi, AlphaGenome, SpliceAI and STEP2h across exon classes: every per-model value is in Figure 1. |
| Bellido Molias and Kudla 2026, splicing predictors on synthetic variants (10.64898/2026.08.24.746734, CC BY) | Eleven predictors including AlphaGenome; values in figures. Also an RNA splicing lane source. |
| Jiang et al. 2026, Nullsettes (10.1021/acssynbio.6c00024, CC BY) | 14 models on synthetic loss-of-function cassettes; success rates in Figure 1C, supplementary tables hold designs and model specifications only. |
| Ebbert et al. 2026, SegmentNT contextual biases (10.1093/nar/gkag704, CC BY) | Independent evaluation with no printed results table; values in figures and the supplementary zip. |
| Sun et al. 2026, multi-species splicing variant review and assessment (10.1093/bib/bbag329) | Ten models including six genomic foundation models across four species; values in figures and a supplementary docx. Overlaps the RNA splicing lane. |
| Evo 2 viral architecture benchmark (10.64898/2026.07.14.738542, CC BY) | Probe accuracies and R-squared values quoted in the abstract and figures only. |
| Sweeney and Kang 2026, sequence-to-omics models for fine-mapping (10.64898/2026.02.04.703796) | AlphaGenome, Borzoi, Enformer and Sei, but the endpoint is fine-mapping replication failure rate; values in figures and supplements. |

Out of scope or already held: see `scope-audit.jsonl`. The main groups are the suites left to `lit-genomics`;
sources already in the store (Feng et al. 2025, Tang et al. 2025, Manzo et al. 2025, the fusion-breakpoint and
quadruplex benchmarks, the tokenizer study, NABench); developer papers (Evo 2, AlphaGenome, PlantCAD2,
GPN-Star, Variformer, SAGE-net); and eight reviews, which printed no new benchmark results.

## Gaps

1. Mathur and Sachidanandam 2026 is unretrieved because of rate limiting, not because it does not exist.
2. The great majority of in-window independent evaluations put their per-model numbers in figures. Nine of the
   twelve candidates above fail only on that. Figures were not read by eye or by colour.
3. Two candidates need new metric concepts before they can be extracted. No concept was added in this pass.
4. Buzkova et al. Tables 8 and 9 (the 6x6 mutation and masking accuracy grids, the paper's robustness result)
   are unextracted: a 36-cell corruption grid needs either 36 protocols or a grid-aware protocol shape, which
   is a design decision rather than a transcription.
5. Datta et al. Table 2 (Genomic Benchmark) and Table 7 (two Genomics Long-Range Benchmark variant-effect
   tasks) are unextracted because the source never names the metric those columns report.
6. You et al. Supplementary Tables 2, 3 and 6 (non-coding RNA classification, m6A, translation efficiency) are
   complete printed tables, unextracted here and flagged to `lit-rna-other`.
7. Benchmark suites cited by the reviews and absent from the store: Genomic Touchstone, the Genomics
   Long-Range Benchmark, the Diverse Genomic Embedding Benchmark, TraitGym. All for the suite pass.
8. No independent zero-shot comparison of Evo 2 against masked DNA models on a shared variant set was found
   in the window with retrievable printed values.
9. The `derivation` result attribute that `derive-collector` is adding had not landed on `origin/main` when
   this pass started, so nothing here uses it and no value is computed from supplementary data.

## What needs a reviewer's judgement

1. **Relevance judgements: none added, deliberately.** Two use cases are adjacent but neither is a close fit.
   Buzkova et al. classify viral sequences against a closed RVDB reference, while
   `use-case-diagnostic-dna-pathogen-identification` asks about clinical plasma microbial cfDNA workflows
   measured by positive percent agreement against blood culture. You et al. predict splice sites and site
   usage, while `use-case-splicing-follow-up` asks which configurations predict the splicing effect of human
   SNVs against experimental measurements. Both would be weak proxies, and a weak `assessed_by` link costs
   more in page noise than it adds. My recommendation is to leave both unlinked; if a reviewer disagrees, the
   protocols to link are the three in the Buzkova batch and the six in the You batch, and the use-case records
   then need `npm run records -- change` with the dated review.
2. **Datta et al. duplicated cell.** Table 1 prints the same frozen value and spread (`.5252+-.0262`) for NT on
   both `Enhancer` and `Enhancer Types`, while the fine-tuned references differ (`.548` and `.424`). I kept
   both as printed and recorded an `evidence_concerns` entry on the source. Please confirm the entry's wording
   and that both cells are blocked from comparison.
3. **Recovery metric.** Datta et al. print a recovery percentage (frozen divided by fine-tuned, times 100) per
   cell and two average-recovery rows. There is no metric concept for a score ratio. I stored the two inputs
   and a claim recording the definition. Adding a concept is a reviewable decision.
4. **Mixed provenance in one table.** Datta et al. Table 1's fine-tuned column is benchmark- or model-reported,
   which the authors say explicitly. I split it into its own protocol and configurations with
   `origin: unreported`. Check that this is the shape the store wants for mixed-provenance tables, because the
   candidate list holds more of them.
5. **Averaging schemes not stated.** You et al. Supplementary Table 4 prints F1, precision and recall without
   saying whether they are macro- or micro-averaged on the three-class task. I used the plain concepts with no
   averaging claim. Buzkova et al. do state macro-averaging, so those results use `macro-f1`.
6. **Chunk-scored rows.** Buzkova et al. Table 10 scores three short-context models over chunks and two
   methods over whole sequences, in one table. They share a protocol and the chunked rows carry their own
   limitation. A reviewer may prefer two protocols.
7. **`printed_value` with a marker.** Buzkova et al. Table 3 prints the overall best with a star marker
   (`*0.9265` in the source's typography). The marker is kept inside `printed_value` with the reason in
   `review.note`.

## Next step

A reviewer other than me runs `review-evidence` over the three batches, then `npm run records -- add` per
batch, then the PR. I have not opened one.
