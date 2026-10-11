# Sources: Datta et al. 2026, frozen representations of genomic language models

| Source ID | Title | Version | Retrieved (UTC) | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `gfm2-20261011-datta2026-source` | Frozen but Not Always Accessible: A Representation Analysis of Genomic Language Models | arXiv:2608.05329v1, submitted 2026-08-05 | 2026-10-11T00:51:27Z | https://arxiv.org/pdf/2608.05329v1 | `df36e4772562329550c924004a546812c8d76149a1b5238e4d0b0cfa8a82bb5c` |

The licence is the arXiv.org perpetual non-exclusive distribution licence 1.0, which does not grant
redistribution, so no copy of the bytes is archived in this repository. The hash and the locators are enough
to re-check every value.

The extracted text layer (`pdftotext -layout`, poppler 26.08.0) was parsed by `extract/extract.py`, which
asserts the four model column labels and each of the 18 task row labels.

## Reused records

| Record | Use in this batch |
| --- | --- |
| `regulatory-variant-20261009-model-hyenadna` | `configuration_of` target for the two HyenaDNA configurations |
| `discovery-model-nucleotide-transformer` | `configuration_of` target for the two NT-500M configurations |

New family records: `gfm2-20261011-datta2026-model-generator-v2` (GENERATOR) and
`gfm2-20261011-datta2026-model-omni-dna` (Omni-DNA). The store holds GENERATOR only as `geneb-method-*`
configurations with no family record.

## Recorded concern

The source record carries an `evidence_concerns` entry: Table 1 prints the same frozen value and spread for
NT on both `Enhancer` and `Enhancer Types` while the fine-tuned references differ. Both cells are kept as
printed and should not support comparison until the authors clarify.
