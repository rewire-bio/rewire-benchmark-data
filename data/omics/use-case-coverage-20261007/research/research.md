# Research lane, cell-type-annotation-transfer bounded ingestion, 2026-10-07

Bounded additive ingestion for `use-case-cell-type-annotation-transfer` (rewire-benchmark-data [#3](https://github.com/rewire-bio/rewire-benchmark-data/issues/3), rewire-benchmarks B349/#27), continuing the 2026-10-06/2026-10-07 dossier series (`docs/omics/evidence-research/cell-type-annotation-transfer-2026-10-06.md`, `-followup-2026-10-07.md`, `cell-type-completion-assessment-2026-10-07.md`, the last independently reviewed by Codex before this ingestion). No new literature search was performed in this pass.

## What is ingested

Abdelaal et al. 2019 (Genome Biology), Additional File 1 (Supplementary Data PDF), Figure S10 Panel B ("deeper level of annotation with 34 cell populations"), **SVMrejection row only**: nine percent-unlabeled values across all nine train/test combinations of the paper's genuine inter-dataset (cross-dataset, cross-species where applicable) brain comparison (VISp mouse, ALM mouse, MTG human; all SMART-Seq v4). VISp and ALM share GSE115746. MTG is a separate human single-nucleus dataset; combinations involving MTG include cross-species data. Some two-dataset training combinations still share the mouse study with the test dataset, so independent-study holdout must not be inferred for all nine combinations.

| Test | Train | % unlabeled |
|---|---|---|
| ALM | VISp | 16.4 |
| ALM | MTG | 84.6 |
| ALM | VISp & MTG | 22.2 |
| MTG | VISp | 99 |
| MTG | ALM | 99.6 |
| MTG | VISp & ALM | 99.5 |
| VISp | ALM | 14.8 |
| VISp | MTG | 81.1 |
| VISp | ALM & MTG | 22.1 |

These nine values were read directly from a `pdftoppm` image render of page 15 of 18 at 2400 dpi (not `pdftotext` — the heatmap's printed digit labels are not present in the PDF's extractable text layer; not OCR; not inferred from cell color), independently cross-checked against the original PDF by a separate reviewer (Codex) before this ingestion, who confirmed the same nine values in the same column order directly from the source. Both independent reads agree exactly.

## What is explicitly NOT ingested, and why

- **Scored denominator.** Table 2 (main-text XML, already catalogued) gives raw per-dataset cell totals — VISp 12,832, ALM 8,758, MTG 14,636 — but Table 2's own "cell populations (>10 cells)" column already shows a filtering step whose effect on cell-level scored counts is not stated anywhere in the retrieved main text or supplement. These raw totals are recorded on the three new dataset records as **context only**; no result or evaluation record states a denominator, and none should be computed by multiplying a percentage against the Table 2 total. This mirrors the precedent already established for the Baron Human intra-dataset ingestion (2026-10-06), where the 8,569-cell Table 2 figure was likewise distinguished from a confirmed per-classifier scored denominator.
- **The other 17 classifiers** shown in the same Figure S10 Panel B heatmap (scmapcell, Cell_BLAST, scPred, CHETAH, scmapcluster, scID, and ten classifiers with 0% unlabeled across the board). Each would need its own individual justification to ingest; none is given here. SVMrejection alone is ingested because it is already the named fixed-abstention-rule baseline in rewire-benchmarks #25's own BL349 comparator panel, giving it an existing justification the others lack.
- **Figure S10 Panel A** (3-population major-lineage level). A separate figure/protocol from Panel B; not ingested in this pass.
- **Figure S9** (PBMC). Panel A carries no printed digit labels in the source PDF at any resolution checked (verified up to 4800 dpi on a representative region, and by whole-panel visual inspection at 400–600 dpi) — confirmed as a fact about the source, not an extraction-tooling limitation. Separately and independent of the missing digits, Panel A shows an unresolved three-way conflict between its own caption text ("median F1-score"), the page's single legend ("Unlabeled (%)"), and the figure's overall title ("Percentage of unlabeled cells"); this is recorded as an open source-internal inconsistency, not resolved in favor of either reading. Panel B (prior-knowledge classifiers, no training performed within that specific evaluation) is a different, non-transfer endpoint and is also not ingested.
- **Superiority or unknown-type-detection accuracy claims.** This ingestion records a conventional classifier's rejection/coverage rate only. It does not claim SVMrejection outperforms or underperforms any other classifier (no comparison panel is constructed), and it does not claim this figure measures accuracy at detecting unknown or reference-absent cell types specifically — "percentage left unlabeled" is a coverage figure, not a correctness figure, and is recorded with `metric_direction: "unknown"` throughout for exactly this reason (the same schema convention, and the same reasoning, already used for the Baron Human unlabeled-percentage results).
- **CellTypist and scParadise candidate numeric findings** (from the bioRxiv-preprint access route explored in the 2026-10-07 completion assessment) remain explicitly un-ingested. The CellTypist preprint Supplementary Note's mechanism description and internal-split precision/recall/F1 figures carry a substantial version-drift caveat (preprint text dated ~8 months before the final Science publication, not confirmed identical) that needs an explicit maintainer decision on preprint-vs-published sourcing before any catalogue record is written; scParadise's Table S1 (`media-2.csv`) was never retrieved (Cloudflare rate-limited). Neither is part of this ingestion.

## Reused, unmodified existing records

- `ucc-research-method-abdelaal-svm-linear` (method: SVM, linear kernel, scikit-learn) — same classifier identity already catalogued for the Baron Human intra-dataset evaluation (Table 1).
- `ucc-research-config-abdelaal-svm-rejection` (configuration: SVMrejection — same underlying SVM with a rejection option enabled, scikit-learn 0.19.2, Table 1) — reused by reference for this new, different evaluation (Figure S10 Panel B instead of Figure 1a/b Baron Human); the classifier identity is identical across both figures in the same paper, so a new configuration record would duplicate, not refine, the existing one.
- `ucc-research-source-abdelaal-2019-paper` (main-text XML) — reused for Table 2 dataset-size figures and the Methods "Brain" train-test-design quote; not modified.

Neither reused record's bytes, IDs, or attributes are changed by this pass.

## New records added

One new source record (the supplement PDF, a separate byte artifact from the already-catalogued main-text XML), three new dataset records (VISp, ALM, MTG), one new protocol record (the Figure S10 Panel B 34-population inter-dataset design, scoped to the SVMrejection row), nine new evaluation records (one per train/test combination), and nine new result records (one percent-unlabeled value per evaluation). 23 records total. See `records.jsonl`, `claims.csv`, `coverage.json`.

## Scope note

Automated source review only, continuing a bounded, dated evidence-research programme. No model was run, no independent experimental replication was performed, and nothing here has had qualified human scientific review. This ingestion is deliberately narrow (one classifier, one figure panel, nine values) per explicit instruction not to mass-ingest a full heatmap just to inflate the record count. This use case remains open and incomplete; nothing in this ingestion measures or substitutes for the common-protocol cross-study benchmark gap tracked separately at rewire-benchmarks #27.
