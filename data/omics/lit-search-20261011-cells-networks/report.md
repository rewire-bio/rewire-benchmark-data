# Literature pass 2026-10-11: cells-spatial and networks-mechanistic

Window 2025-10-01 to 2026-10-11, focused on benchmarks of single-cell and spatial foundation models, perturbation-response and virtual cell models, and gene regulatory network inference. 32 logged searches and lookups (ledger.jsonl), 23 scope decisions (scope-audit.jsonl). Branch `claude/lit-20261011-cells-networks`, worktree `../rewire-benchmark-data-lit-cells-networks`. Everything is `needs_review`; nothing has been added to the store.

Update 2026-10-12: all five batches were reviewed independently (reviewer-cn-1 and reviewer-cn-2), corrected as the reviews specified and added to the store; see `docs/reviews/2026-10-12-cells-networks-batches.md` and each batch's `review.md`.

## Extracted

| Batch | Source | Records | Results | Use-case judgements |
| --- | --- | --- | --- | --- |
| `lit-cells-networks-20261011-perturbench-v4` | PerturBench arXiv v4 (NeurIPS 2025 D&B, 2025-10-24), Tables 2-13 | 416 | 340 | 3 (genetic perturbation: Norman19, Jiang24, Frangieh21) |
| `lit-cells-networks-20261011-chen2026` | Chen et al. 2026, harmonised sc and spatial foundation model benchmark, arXiv 2607.17227v2, Tables 2-5 and S2 | 542 | 378 | 7 (genetic perturbation x3, cell-type annotation x4) |
| `lit-cells-networks-20261011-ye2026grn` | Ye et al. 2026, GRN reconstruction from scFMs on BEELINE, bioRxiv v1, Tables 4-7 | 3,575 | 2,352 | none (no GRN use case) |
| `lit-cells-networks-20261011-scmbench` | SCMBench, Nat Commun 2026, Supplementary Data 2 overall integration sheets | 544 | 241 | none (no integration use case) |
| `lit-cells-networks-20261011-sun2026de` | Sun et al. 2026, DE classification benchmark for perturbation models, bioRxiv v1, Tables 1-4 | 286 | 170 | 2 (genetic perturbation: within and cross cell line) |

Each batch folder has `batch.jsonl`, `claims.csv`, `sources.md`, `retrieval-log.md`, `research.md`, a deterministic extractor in `extract/`, and gzip copies of the sources in `artifacts/` where the licence allows (not for the arXiv-licensed PerturBench HTML). Proposed `assessed_by` links are in each batch's `use-case-links.json`; the use_case records are not edited.

New metric concepts in `data/vocab/metric.ttl`: `perturbench-energy-mmd`, `perturbench-matrix-distance`, `perturbench-rmse-transposed-rank`, `silhouette-score`, `scmbench-integration-accuracy`. All five batches pass the store's schema, vocabulary and attribute validation together against the current store (scratch script calling `validateVocabularies`, `validateAttributes` and `validateRecords`); `tests/vocab.test.ts` passes. The SHACL check runs at `records -- add`.

The batches are independent: no batch references a record created by another.

## Not extracted

| Candidate | Reason |
| --- | --- |
| VCBench (bioRxiv 10.64898/2026.06.18.733146, CC BY) | Strong candidate. Table 2 compares five scFMs with additive, mean and no-change baselines across five heterogeneous dimensions; the text layer encodes minus signs as arrows (rendered page checked), and Table 2 prints scGPT PRR 0.503 while the text gives 0.545. Needs per-dimension protocol work and a rendered-page check. |
| Wu et al. 2025, Nat Methods, generalisable perturbation prediction (doi:10.1038/s41592-025-02980-0) | Closed article; results are figures. Source Data and Supplementary Tables are open, but the score columns are defined only in the closed Methods. |
| scDrugMap (Nat Commun 2025) | Supplementary Data 4 lists only models with significant t-tests; complete per-model scores are in Source Data behind figures. Candidate for a source-data derivation. |
| scArchon (Genome Biol 2026) | Supplementary workbook holds per-cell-type raw rows (about 390 rows, 11 metrics) without a printed per-method summary. |
| Deep-learning integration benchmark (Genome Biol 2025, PMC12636214) | 35 MB supplementary workbook not parsed in this pass. |
| PEREGGRN expression forecasting (Genome Biol 2025) | Results in figures only. |
| TF activity inference benchmark (Brief Bioinform 2026) | Supplementary tables print only pairwise differences and tests. |
| EGF signalling pathway inference (Nat Commun 2026) | Results in figures only. |
| Mao et al. 2026 (arXiv 2604.27646); Signal, Bounds, and Baselines; Far from Straightforward; zero-shot scFM benchmark; interventional causal GRN comparison; pathology FM spatial domain benchmark | No printed result tables. |
| Virtual Cell Challenge 2026 (Cell) | Full text not retrievable (cell.com 403, no PMC copy); the store holds the 2026-09-19 leaderboard snapshot. |
| HESCAPE (arXiv 2508.01490) | Posted August 2025, before the window. |

## Gaps

- Research Square preprints (empirical virtual cell comparison rs-10434123, reference-cell design, leakage-aware benchmark, GRN evaluation-choice papers) and the ICML 2026 virtual cell GRN-recovery paper were not opened.
- No in-window mechanistic model benchmark (PEtab-style, kinetic or constraint-based) was found; the broad query (q25) was mostly noise and a narrower search was not run.
- Spatial analysis-method benchmarks without foundation models (clustering, deconvolution, cell-cell communication) were out of this pass's focus.
- The Shift Bioscience metric-calibration preprint was not located (press coverage only).
- The well-known suites already in the store (scIB, BEELINE, Open Problems, HEST, PerturBench, Virtual Cell Challenge) were checked for presence; only PerturBench had an in-window new version.

## Needs a reviewer's judgement

- PerturBench v4: reuse of the v1 configuration records for rows with the same printed name; 'DecoderOnly' mapped to the Decoder configuration (Section 4.2 wording); the Jiang24 held-out-state description differs between Table 4 caption and Appendix D.4; origin split (independent_paper for CPA, SAMS-VAE, Biolord, GEARS).
- Chen 2026: mapping of the undefined spatial codes BC, MH and ME to HBCA1, MHPC and MOSTA; no conventional baselines in any table; precision, recall and AUC averaging unstated; whether the annotation protocols are proxy evidence for annotation transfer.
- Ye 2026: Table 1 mislabels its ChIP-seq column (evidence concern); Table 6 'AUPR' treated as auprc-ratio (evidence concern); about 2,350 results from one preprint, all parser-derived.
- SCMBench: unlabelled column H in 'unpaired_inte_overall' (evidence concern); FM-scVI is a different model per dataset (evidence concern); printed_value convention for General-format cells (15 significant digits, raw value kept).
- Sun 2026: tables do not state full versus downsampled data (evidence concern); proportion-predicted-DE recorded with direction 'unknown'.
- bioRxiv PDFs change bytes per download; the gzip copies in `artifacts/` are the hash reference for Ye and Sun.
