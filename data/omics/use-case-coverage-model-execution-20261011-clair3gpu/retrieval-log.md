# Retrieval log: Zheng et al. 2026, accelerated Clair3 (Bioinformatics 42(5), btag181)

Worker: Claude (Opus 5.5) research agent `uc-execution` in Claude Code. No human review claimed. Every download went to its own new folder in the session scratch directory and was opened as data (XML parse, `pdftotext -layout` from poppler, `pdfimages -list`, `pdftoppm` renders). Scripts were kept outside the download folders and run with `python3 -I`. Nothing was executed or reproduced. Times are UTC from `date` output or the saved file's modification time.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 21:35:29 | `GET .../PMC13141153/fullTextXML (first screening copy)` | 200 | 74,047 | Read for Methods, Results and figure captions |
| 21:3x | `GET .../PMC13141153/supplementaryFiles (first screening copy)` | 200 | 1,169,933 | Zip with the supplementary PDF and figure images |
| 21:42:40 | `GET .../PMC13141153/fullTextXML and /supplementaryFiles (pinned copies)` | 200 | 74,047; 1,169,933 | Same PDF member SHA-256 as the screening copy |

## How the tables were read

- Supplementary Table 1 is in the PDF text layer and is parsed by `extract/build.py` (sample, platform, coverage and seven numeric columns asserted for four rows).
- Supplementary Tables 2 and 3 are raster images (`pdfimages -list` shows one 1537 px wide image on each of pages 2 and 3, with no text layer). Their cells were transcribed by hand from `pdftoppm -r 300` crops of the pinned PDF, then read again from a 110 dpi render of the whole page; the two readings agreed. The transcribed values are written out in `extract/build.py`. A reviewer must re-read every one of the 350 transcribed cells.
- Supplementary Tables 4 to 6 (accuracy on other GIAB samples, LongPhase versus WhatsHap, haplotagging counts) were not extracted: they do not bear on execution resources.
- Figure 2a (runtime of Clair3 v0.1, v1.2 CPU and GPU, and DeepVariant CPU and GPU) prints no numbers and was not read.

Run: `python3 -I extract/build.py <btag181_supplementary_data.pdf>`; it checks the SHA-256 and needs `pdftotext`.
