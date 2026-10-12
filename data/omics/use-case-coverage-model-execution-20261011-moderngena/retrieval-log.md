# Retrieval log: Aspidova et al. 2026, ModernGENA (bioRxiv 10.64898/2026.04.21.719816 v1)

Worker: Claude (Opus 5.5) research agent `uc-execution` in Claude Code. No human review claimed. Every download went to its own new folder in the session scratch directory and was opened as data (XML parse, `pdftotext -layout` from poppler, `pdfimages -list`, `pdftoppm` renders). Scripts were kept outside the download folders and run with `python3 -I`. Nothing was executed or reproduced. Times are UTC from `date` output or the saved file's modification time.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 21:35:30 | `GET api.biorxiv.org/details/biorxiv/10.64898/2026.04.21.719816` | 200 |  | Version 1, 2026-04-23, cc_by, not published |
| 21:39:38 | `GET biorxiv.org/.../2026.04.21.719816v1.full.pdf` | 200 | 1,293,252 | Pinned copy (time is the file modification time) |
| 21:43:01, 21:43:44 | `GET the same URL` | 429 | 17 | Rate limited; no second copy |

## How the tables were read

- Appendix B Table 2 is parsed from the `pdftotext -layout` text by `extract/build.py`, which checks both hashes, asserts the six sequence-length headers and nine row labels, and requires twelve cells per row. Cells printed as an en dash (GENA base and large from 1,024 tokens) give no result.
- Figure 1 (the same efficiency data as a plot) was not read. Tables 3 to 5 (Nucleotide Transformer benchmark accuracy) were not extracted: they are task accuracy, not execution.

Run: `python3 -I extract/build.py <preprint.pdf>`.
