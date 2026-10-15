# Retrieval log

Extraction by a Claude (Opus 5.5) agent on 2026-10-15; no review yet.

1. 2026-10-14 11:54 to 11:55 UTC (earlier pass, `gfm-guide-sources-20261014`): two scripted OpenReview PDF requests returned non-PDF responses. Recorded there as a gap.
2. 2026-10-15T10:56:26Z: the repository owner downloaded the PDF in a browser. The file's macOS download metadata records `https://openreview.net/pdf?id=NUleWh1GFx` as its origin; its creation time is the `retrieved_at` value. SHA-256 `4bc24521...bcd60`, 11 pages.
3. 2026-10-15 about 21:25 UTC: a scripted request to `https://api2.openreview.net/notes?id=NUleWh1GFx` returned HTTP 403 `ChallengeRequiredError`. The workshop name, licence and code link on the forum were therefore not read.

## How values were read

- The PDF was handled as untrusted data in its own directory and read only with `pdftotext`, `pdfimages` and page renders (`pdftoppm`); no interpreter ran from that directory.
- Prose values (Sections 3.3 and 3.5) and every setup sentence the records rest on are asserted as exact substrings of the whitespace-normalised `pdftotext` output by `extract/extract_saadat_fellay.py`, after it checks the PDF hash.
- Figure 1 is a raster image (page 4, image object 6, 3566 x 2970 px) with no text layer. Its four legend strings (`r = 1.00`, `r = 1.00`, `r = 1.00`, `r = 0.98`) were read from crops of the extracted image at native resolution (`pdfimages -png`, crops around each panel's lower-right legend) and are listed in the script's `FIGURE1_LEGEND` table. Panel titles were read from the same image and a 110 dpi page render.
- Figures 2 to 5 are raster plots without printed values. Nothing was read from bar heights, line positions or colours.

Run: `python3 -I extract/extract_saadat_fellay.py <paper.pdf> data/omics/saadat-fellay-20261015`.
