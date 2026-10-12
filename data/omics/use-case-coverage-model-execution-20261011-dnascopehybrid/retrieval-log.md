# Retrieval log: Hu et al. 2026, DNAscope Hybrid (Frontiers in Bioinformatics 5:1691056)

Worker: Claude (Opus 5.5) research agent `uc-execution` in Claude Code. No human review claimed. Every download went to its own new folder in the session scratch directory and was opened as data (XML parse, `pdftotext -layout` from poppler, `pdfimages -list`, `pdftoppm` renders). Scripts were kept outside the download folders and run with `python3 -I`. Nothing was executed or reproduced. Times are UTC from `date` output or the saved file's modification time.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 21:35:29 | `GET .../PMC12813096/fullTextXML (screening copy)` | 200 | 132,089 | Read for Table 2, Methods and Conflict of interest |
| 21:42:46 | `GET the same URL (pinned copy)` | 200 | 132,089 | Same bytes |

## How the tables were read

- Table 2 is parsed from `table-wrap id="T2"` in the article XML by `extract/build.py`, which asserts the caption text, the header and the eight row labels.

Run: `python3 -I extract/build.py <PMC12813096 XML>`.
