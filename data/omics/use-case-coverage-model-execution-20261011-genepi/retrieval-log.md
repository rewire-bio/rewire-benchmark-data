# Retrieval log: Marangoni et al. 2026, GeNePi (Briefings in Bioinformatics 27(1), bbag001)

Worker: Claude (Opus 5.5) research agent `uc-execution` in Claude Code. No human review claimed. Every download went to its own new folder in the session scratch directory and was opened as data (XML parse, `pdftotext -layout` from poppler, `pdfimages -list`, `pdftoppm` renders). Scripts were kept outside the download folders and run with `python3 -I`. Nothing was executed or reproduced. Times are UTC from `date` output or the saved file's modification time.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 21:35:29 | `GET .../PMC12832024/fullTextXML (screening copy)` | 200 | 134,038 | Read for Methods, Results and Discussion |
| 21:3x | `GET .../PMC12832024/supplementaryFiles (screening copy)` | 200 | 1,140,165 | Zip with the supplementary PDF |
| 21:42:44-45 | `GET the same two URLs (pinned copies)` | 200 | 134,038; 1,140,165 | Same bytes as the screening copies |

## How the tables were read

- Supplementary Table S1 is parsed from the `pdftotext -layout` text by `extract/build.py`, which asserts the header (`Avg. Reads Depth CPU GPU-2xV100 GPU-2xA100 GPU-4xA100`) and the five depth rows. Durations are printed as `17h`, `1h 36m` or `42 m`; `numeric_value` converts them to minutes.
- Figure 2 and Supplementary Figures S10 and S11 (Parabricks versions, 8 A100 and 8 H100 nodes on the EMBL cluster) print no numbers and were not read. Several numbers in the article's running text are missing from the XML (blank inline formulae), so the text's speed-up range ("10 to 78 times") could not be checked against the table.

Run: `python3 -I extract/build.py <genepi_supplinfo_rev_bbag001.pdf>`.
