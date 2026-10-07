# Primary sources

## scTab (no new source record; reused by reference)

Both scTab facts (ROC-AUC 0.782, 0.891) come from the main text of a source already catalogued on
2026-09-30:

- `ucc-research-source-sctab-paper` — [scTab: Scaling cross-tissue single-cell annotation models](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11298532/fullTextXML). Version: 10.1038/s41467-024-51059-5; published article XML. Originally retrieved 2026-09-30T21:23:28Z, SHA-256 `e61b11cd873f3d13e891e9c33bac0847070826200f8fbe0b3969d994f1c52290`. **Independently re-fetched and re-hashed in this pass** at 2026-10-06T12:16:47Z (bounded research dossier, `docs/omics/evidence-research/cell-type-annotation-transfer-2026-10-06.md`) and again verified byte-identical against an independent fetch by a separate reviewer (`workbench/source-review-20261006/PMC11298532.xml`, gitignored, not part of this release): identical SHA-256 both times. No article version drift. Inspected this pass: Methods, subsection "Uncertainty quantification for scTab model".

Existing catalogue records reused by reference (not modified, not redefined): `ucc-research-config-sctab-sctab` (configuration), `ucc-research-data-sctab-census-20230515` (dataset), `ucc-research-benchmark-sctab` (benchmark).

## Abdelaal et al. 2019 (new source record this pass)

- `ucc-research-source-abdelaal-2019-paper` — [A comparison of automatic cell identification methods for single-cell RNA sequencing data](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6734286/fullTextXML). Version: 10.1186/s13059-019-1795-z; published article XML. **Provenance correction (independent review):** the original research dossier logged only a bounded retrieval window (12:16:47Z-12:18:28Z UTC, 2026-10-06) across five sources fetched together, not an individual timestamp per file; `retrieved_at` must not borrow the window's end as if it were this file's own exact fetch time. This source was therefore **re-fetched directly** in this review pass at **2026-10-06T23:28:54Z UTC** (request start time; response completed one second later), confirmed byte-identical, SHA-256 `6df0937c5a2d8ba06465ba356c2321fb9f52d9ecf23456876acd82f828b41d4c` (no article version drift across either fetch). The retrieved bytes are archived as a **committed, gzip-compressed artifact** at `artifacts/abdelaal-2019-pmc6734286-fulltext.xml.gz` (tracked in version control, not gitignored -- the stable cache path the release build can read), round-trip-verified to the same SHA-256; the uncompressed copy also remains available, untracked, at `workbench/source-review-20261006/PMC6734286.xml` for interactive inspection only. License, quoted verbatim: "This article is distributed under the terms of the Creative Commons Attribution 4.0 International License" (CC BY 4.0), (c) The Author(s) 2019. Inspected this pass: Methods, "Intra-dataset classification"; Results, "Benchmarking automatic cell identification methods (intra-dataset evaluation)" > "All classifiers perform well in intra-dataset experiments"; Table 1 (method identities); Table 2 (dataset population); Fig. 1a,b (legend only -- heatmap cell values not independently re-extracted beyond the two quoted sentences below).

Scope ingested: the Baron Human **intra-dataset** (same single dataset, stratified 5-fold cross-validation) rejection-option baseline only -- four median F1-score values and three cells-left-unlabeled percentages, exactly as quoted in `claims.csv` and `retrieval-log.md`. The source's genuine **inter-dataset** (cross-platform/cross-study) experiments (Fig. 4 brain, Fig. 5 pancreatic) are explicitly out of scope for this ingestion and are not catalogued here; see `research.md`.

## scArches (checked, not ingested -- see "Unresolved" in research.md)

scArches (PMC8763644) was re-checked this pass for its ~84% Tabula-Muris-query accuracy figure. No new
source record is created: the figure's exact denominator (whether cells labelled "unknown" are counted
against accuracy or excluded from it) could not be established from the accessible primary text for the
specific panel (Fig. 4c) that reports it. See `research.md`, "Unresolved: scArches ~84% accuracy," for
the full quoted evidence and reasoning.
