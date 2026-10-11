# Retrieval log: You et al. 2026

Worker: Claude (Opus 5.5) research agent lit-gfm-2 in Claude Code. No human review claimed. Downloads went to
a session scratch directory and were read as data (`pdftotext -layout`, Python under `-I`). No model was run.
Times are UTC.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 00:38:35 | Europe PMC discovery sweep (ledger q2) | 200 | | 304 hits; this article among them |
| 00:40:30 | Europe PMC `search?query=DOI:"10.1038/s41467-025-66899-y"` with `resultType=core` | 200 | | Abstract, licence `cc by-nc-nd`, PMC12780105 |
| 00:43:10 | Europe PMC `PMC12780105/supplementaryFiles` (screening copy) | 200 | 3,690,496 | Zip with four MOESM files and the figure images |
| 00:46:00 | Same, re-requested in the background job | 200 | 6,520,832 | Zip assembled per request; member hashes used instead |
| 00:55:34 | Europe PMC `PMC12780105/fullTextXML` | 200 | 219,115 | SHA-256 `2c6b2816...`; Methods, Table 1 and metric definitions read |
| 00:55:35 | `41467_2025_66899_MOESM1_ESM.pdf` from the unpacked zip | | 2,765,690 | SHA-256 `cbb69e05...`; 18 pages; Supplementary Tables 1-6 |
| 00:55:36 | `pdftotext -layout` (poppler 26.08.0) | | | Text layer SHA-256 `4a54c8b1...` |

## What was read

- Methods: the 500 bp input decision for every method, the appended convolution head for the language models,
  the three fine-tuning runs with different random initialisations behind each mean and standard deviation,
  and the metric choice per task (Results, "characteristics of each task").
- Table 1 of the article: dataset sizes, species counts and train/test splits for the splicing datasets.
- Supplementary Table 4, all three blocks (NT-splice-sites-all, -acceptors, -donors): 11 methods by four
  metrics, 132 results.
- Supplementary Table 5, all three blocks (acceptors and donors, Splice-15class, Splice-53class): eight and
  seven methods by two metrics, 44 results.

## What was not read

- Supplementary Table 2 (non-coding RNA classification), Table 3 (m6A, four training-size settings) and
  Table 6 (translation efficiency, two fine-tuning settings). They are complete printed tables and remain
  available; this batch keeps to the splicing tables. A claim record states the omission. The RNA lane
  teammate was told about this source.
- Supplementary Table 1 (fine-tuning hyperparameters) beyond citing it as the configurations' locator.
- The Source Data xlsx and every figure.
