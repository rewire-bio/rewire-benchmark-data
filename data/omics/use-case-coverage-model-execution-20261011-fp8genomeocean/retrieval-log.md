# Retrieval log: Yu et al. 2026, FP8 inference on GenomeOcean (bioRxiv 10.64898/2026.08.09.743676 v1)

Worker: Claude (Opus 5.5) research agent `uc-execution` in Claude Code. No human review claimed. Every download went to its own new folder in the session scratch directory and was opened as data (XML parse, `pdftotext -layout` from poppler, `pdfimages -list`, `pdftoppm` renders). Scripts were kept outside the download folders and run with `python3 -I`. Nothing was executed or reproduced. Times are UTC from `date` output or the saved file's modification time.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 21:35:30 | `GET api.biorxiv.org/details/biorxiv/10.64898/2026.08.09.743676` | 200 |  | Version 1, 2026-08-18, cc_by, not published |
| 21:3x | `GET biorxiv.org/.../2026.08.09.743676v1.full.pdf (two attempts)` | 429 | 17 | Rate limited (Cloudflare error 1015) |
| 21:39:27 | `GET biorxiv.org/.../2026.08.09.743676v1.full.pdf` | 200 | 1,355,483 | Screening copy |
| 21:42:49 | `GET biorxiv.org/.../2026.08.09.743676v1.full.pdf` | 200 | 1,355,483 | Pinned copy; 40 bytes differ from the screening copy, text layer identical |

## How the tables were read

- Tables 3 and 4 are parsed from the `pdftotext -layout` text by `extract/build.py`, which checks the text-layer SHA-256, asserts the six Table 3 rows (model scale and precision) and the three Table 4 rows, and splits each `mean ± SD` cell.
- Figure 3 (time per output token by batch size and context length) prints no numbers and was not read.

Run: `python3 -I extract/build.py <preprint.pdf>`.
