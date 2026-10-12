# Sources: Hu et al. 2026, short-read versus host-depleted nanopore mNGS on BALF

Part of the 2026-10-11 pathogen use-case literature pass (window 2025-10-01 to 2026-10-11). Hashes are SHA-256 of the exact bytes parsed.

| Source ID | Title | Version | Retrieved (UTC) | Artifact URL | SHA-256 | Licence |
| --- | --- | --- | --- | --- | --- | --- |
| `dna-pathogen-20261011-hu2026-source` | Benchmarking next- versus third-generation sequencing in metagenomics: performance metrics and diagnostic efficacy | Microbiology Spectrum 14(7):e03993-25, published 2026-06-03; PMC13339908 full-text XML | 2026-10-11T21:37:24Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13339908/fullTextXML | `555995fd870d878dd0e6c112064bbf1d2535a1cb1af17f70570ecc11774caa2d` | CC-BY-4.0 |
| `dna-pathogen-20261011-hu2026-source-supp` | Hu et al. 2026 Supplemental Tables S1 to S4, S6 and S7 (spectrum.03993-25-s0001.docx) | spectrum.03993-25-s0001.docx as distributed with PMC13339908 | 2026-10-11T21:41:40Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13339908/supplementaryFiles | `7ab6c2cde30619e506a5e015ef5bbb253dfa6359ebd56140577eef136b153ed9` | CC-BY-4.0 |

DOI: 10.1128/spectrum.03993-25.

## Tables used

| Source | Tables | Results |
| --- | --- | --- |
| Article XML | Table 2 (2 workflows x 3 reference standards x 6 cells) | 36 |
| Supplementary DOCX | Supplemental Table 6 (bacteria) and Table 7 (fungi), same layout | 72 |

## Authorship and origin

Eight of the listed authors, including co-corresponding author Lifeng Li, are affiliated with Genskey Medical Technology (Beijing), a clinical mNGS provider; the article states that the authors declare no conflict of interest. Both workflows are the authors' own laboratory workflows, so all six evaluations are `author_reported`.

## Licence and archived copies

The article XML `<license>` element states CC BY 4.0; the supplement is distributed with the article under the same terms. Gzip copies (`gzip -n -9`) of both are archived in `artifacts/`.

| Archive | Source | Gzip SHA-256 | Decompresses to |
| --- | --- | --- | --- |
| `artifacts/PMC13339908.xml.gz` | `dna-pathogen-20261011-hu2026-source` | `e56c3b77df658ca936816f1a85d31b1b78ec85baaf0bdcfe936c203ed66f3ccf` | `555995fd870d878dd0e6c112064bbf1d2535a1cb1af17f70570ecc11774caa2d` |
| `artifacts/spectrum.03993-25-s0001.docx.gz` | `dna-pathogen-20261011-hu2026-source-supp` | `cde5c548403958270d4e61c8f4f1bf49861cb7ced4c058c8483a500645896b75` | `7ab6c2cde30619e506a5e015ef5bbb253dfa6359ebd56140577eef136b153ed9` |
