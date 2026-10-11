# Retrieval log: Bůžková et al. 2026

Worker: Claude (Opus 5.5) research agent lit-gfm-2 in Claude Code. No human review claimed. Downloads went
to a session scratch directory, one folder per artifact, and were read as data (`pdftotext -layout`, Python
under `-I`). No model was run. Times are UTC.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 00:42:06 | Europe PMC search for genomic foundation model benchmarks in microbial and viral genomics (ledger q22) | 200 | | 69 hits; this preprint among them |
| 00:42:30 | Europe PMC `search?query=DOI:"10.64898/2026.09.25.754388"` with `resultType=core` | 200 | | Abstract, author list and PPR record; no full text in Europe PMC |
| 00:44:10 | `api.biorxiv.org/details/biorxiv/10.64898/2026.09.25.754388` | 200 | | Version 1, posted 2026-09-28, licence `cc_by`, category bioinformatics |
| 00:45:12 | `biorxiv.org/content/10.64898/2026.09.25.754388v1.full.pdf` (screening copy) | 200 | 1,177,585 | PDF, 27 pages; read for table structure |
| 00:48:35 | Same URL, pinned retrieval | 200 | 1,177,585 | SHA-256 `9a589a20...`; the byte stream differs from the screening copy (per-request preprint banner), so this retrieval is the bound one |
| 00:48:36 | `pdftotext -layout` (poppler 26.08.0) | | | Text layer SHA-256 `e1a2027c...`; 1,271 lines |
| 00:48:37 | `gzip -n -9` archive of the PDF | | 845,229 | `artifacts/buzkova2026-v1.pdf.gz`, SHA-256 `d0e35f33...` |

## What was read

- Tables 1 and 2 (dataset composition, model inventory): used for the dataset and configuration records and
  one `model_characteristics` claim per model, with each printed cell asserted by the parser.
- Table 3 (nine models by five pooling configurations, 33-class dataset): every value extracted, 33 cells.
  Three NTv3 models print an em dash for the three special-token and CLS configurations; those are absent,
  not zero, and no record is written for them.
- Table 7 (BLAST against the best foundation-model configuration, 40- and 33-class datasets): all 24 cells.
- Table 10 (long-sequence dataset): all 30 cells.

## What was not read

- Tables 4 (misclassification pairs), 5 (embedding-generation time), 6 (PCA retention), 8 and 9 (the 6x6
  mutation and masking accuracy grids for blastn and NTv3-650M) and 11 (ICTV reconciliation). Tables 8 and 9
  are the paper's robustness finding and are worth a later pass; they would need 36 protocol records or a
  grid-aware protocol, which is a design decision for a reviewer rather than this extraction.
- All figures. No value was read off a figure.
