# Retrieval log, cell-type-annotation-transfer bounded ingestion, 2026-10-07

No new web retrieval was performed to produce the nine ingested values: the source PDF (Additional File 1) was already cached and hashed from the 2026-10-06 pass (SHA-256 `797a2b22f584135f4ff6f7c98203d8e9529d6600f675b500205607b47b212a81`, originally retrieved 2026-10-06T21:17:27Z via the Springer/BMC static-content route). This pass's own work was local: re-hashing the cached bytes to confirm no drift, archiving them as a committed artifact, and extracting Figure S10's printed values via page-image rendering (`pdftoppm`, 2400 dpi for Figure S10, up to 4800 dpi for a Figure S9 Panel A spot-check) rather than `pdftotext` or OCR.

## Local extraction steps (2026-10-07)

1. `pdfinfo` confirmed 18 pages; per-page `pdftotext -f N -l N` caption matching confirmed page 14 = Figure S9, page 15 = Figure S10 (not assumed).
2. `pdftoppm -r 400/600` full-page renders of pages 14–15 for whole-panel visual inspection.
3. `pdftoppm -r 2400`, cropped via `-x/-y/-W/-H`, for Figure S10 Panel A and Panel B at digit-legible resolution; header strips re-rendered separately to confirm exact training-set/test-set column labels.
4. `pdftoppm -r 4800` spot-check of a representative region of Figure S9 Panel A (10XV2 training block); confirmed no printed digit labels at that resolution, consistent with the whole-panel 400–600 dpi check.
5. All nine Figure S10 Panel B SVMrejection values and their train/test column order were read directly from the rendered images in step 3.
6. Bytes re-hashed (`shasum -a 256`) against the independently-cached copy in the neighboring `cell-type-evidence-20261006` worktree before archiving; identical, confirming no retrieval-to-archival drift.
7. Archived via `gzip -9`; round-trip decompression re-hashed to confirm the committed artifact reconstructs the exact original bytes.

## Independent cross-check

Before this ingestion was authored, a separate reviewer (Codex) independently rendered the same original PDF pages (14 and 15) and independently confirmed the same nine SVMrejection values in the same column order directly from the source, as well as the Figure S9 Panel A caption/legend/title conflict and the Table 2 denominator-scope issue addressed in the preceding completion-assessment correction pass. No value in this ingestion was taken on trust from a single read.

## Not retrieved / not re-attempted in this pass

No new network access was performed. The CellTypist bioRxiv-preprint supplement and the scParadise `media-2.csv` lead (both explored in the 2026-10-07 completion assessment) were not re-attempted here; neither is part of this ingestion. See `docs/omics/evidence-research/cell-type-completion-assessment-2026-10-07.md` for their status.
