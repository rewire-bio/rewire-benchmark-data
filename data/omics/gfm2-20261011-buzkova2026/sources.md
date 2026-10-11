# Sources: Bůžková et al. 2026, genomic foundation models for viral sequence identification

| Source ID | Title | Version | Retrieved (UTC) | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `gfm2-20261011-buzkova2026-source` | Analyzing Genomic Foundation Models for Viral Sequence Identification | bioRxiv v1, posted 2026-09-28, DOI 10.64898/2026.09.25.754388. CC BY 4.0 | 2026-10-11T00:48:35Z | https://www.biorxiv.org/content/10.64898/2026.09.25.754388v1.full.pdf | `9a589a2088f8466502b1035228db3e594065e984e5755c25d907471225f75c19` |

The licence is CC BY 4.0, so the bytes are archived: `artifacts/buzkova2026-v1.pdf.gz` (`gzip -n -9`),
SHA-256 `d0e35f3314c4cab758d79d0162ef52ee4e16195832a60e92f958aa45763fa081`.

The extracted text layer (`pdftotext -layout`, poppler 26.08.0) has SHA-256
`e1a2027c0ac0f6ac14306635cc5f2301b248eecd1f5b0dcf24a142fed9a2f5ac`. The parser in `extract/extract.py`
reads that text, not the PDF directly, and asserts every row and column label it uses.

A copy downloaded for screening at 00:45 differs from the pinned copy in its byte stream (bioRxiv stamps
the preprint banner per request). Only the hash above is bound to the records.

## Reused records

| Record | Use in this batch |
| --- | --- |
| `discovery-model-nucleotide-transformer` | `configuration_of` target for the NTv1 and NTv3 configurations |
| `catalog-model-nt-v2` | `configuration_of` target for the three NTv2 configurations |
| `discovery-model-dnabert-2` | `configuration_of` target for the DNABERT-2 configurations |
| `dna-pathogen-20261009-method-blast` | `configuration_of` target for the blastn and megablast configurations |

New family record: `gfm2-20261011-buzkova2026-model-dnabert-s` (DNABERT-S), which the store did not hold
as an entity (only an abstract source record, `qa-descriptions-20261010-source-dnabert-s`).
