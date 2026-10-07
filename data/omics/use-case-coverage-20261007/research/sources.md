# Primary sources

## Abdelaal et al. 2019 main-text XML (no new source record; reused by reference)

`ucc-research-source-abdelaal-2019-paper` — already catalogued (2026-10-06 additive intake), committed artifact at `data/omics/use-case-coverage-20261006/research/artifacts/abdelaal-2019-pmc6734286-fulltext.xml.gz`, SHA-256 `6df0937c5a2d8ba06465ba356c2321fb9f52d9ecf23456876acd82f828b41d4c`. Reused here only for Table 2's VISp/ALM/MTG raw dataset-size figures (context only, not a scored denominator) and the Methods "Brain" train-test-design quote. Not re-fetched, not modified.

## Abdelaal et al. 2019 Additional File 1, Supplementary Data PDF (new source record this pass)

- `ucc-research-source-abdelaal-2019-supplement` — [Additional File 1](https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-019-1795-z/MediaObjects/13059_2019_1795_MOESM1_ESM.pdf). Version: 10.1186/s13059-019-1795-z; Additional File 1 (Supplementary Data PDF, 18 pages). **A separate byte artifact from the main-text XML above** — same article, same license (CC BY 4.0, same copyright statement), different file.
- **Provenance.** Originally retrieved via the Springer/BMC static-content route on **2026-10-06T21:17:27Z** (logged in the 2026-10-06 research dossier's "Resumed pass" retrieval ledger), HTTP 200, 13,495,279 bytes, SHA-256 `797a2b22f584135f4ff6f7c98203d8e9529d6600f675b500205607b47b212a81`. **Re-verified byte-identical** directly in this pass (2026-10-07), re-hashed against the cached copy held in the neighboring `cell-type-evidence-20261006` worktree's `workbench/source-review-20261006/PMC6734286_supp1.pdf` (gitignored, not part of any release) before archiving — identical SHA-256, no version drift. The retrieved bytes are archived as a **committed, gzip-compressed artifact** at `artifacts/abdelaal-2019-pmc6734286-supplement1.pdf.gz` (tracked in version control, round-trip SHA-256 verified), the stable cache path the release build reads.
- **Extraction method.** Page-to-figure mapping established directly via per-page `pdftotext` caption matching (page 14 of 18 = Figure S9; page 15 of 18 = Figure S10). Figure S10's printed digit values (both panels) were read from `pdftoppm` image renders at 2400 dpi — not from `pdftotext` (the heatmap cell values are not present in the PDF's extractable text layer) and not from color-to-value inference. Figure S9 Panel A was checked at up to 4800 dpi on a representative region and found to carry no printed digit labels at all.
- **Scope ingested from this source in this pass:** Figure S10, Panel B (34-cell-population annotation level) only, SVMrejection row only (9 of the 18 classifier rows shown). Figure S10 Panel A (3-population level), Figure S9 (both panels), and the other 17 classifier rows of Panel B are explicitly out of scope for this ingestion.
- **Independent cross-check.** The nine values and their column order were independently re-derived by a separate reviewer (Codex) directly from the original PDF before this ingestion proceeded; both reads agree exactly.

## License

CC BY 4.0, quoted verbatim in the already-catalogued main-text XML (same article): "This article is distributed under the terms of the Creative Commons Attribution 4.0 International License" (c) The Author(s) 2019. Applies to the article as a whole, including Additional File 1.
