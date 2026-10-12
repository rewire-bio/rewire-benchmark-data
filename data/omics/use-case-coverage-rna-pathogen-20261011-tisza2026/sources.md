# Sources: Tisza et al. 2026, EsViritu virus profiler benchmark (preprint)

Part of the 2026-10-11 pathogen use-case literature pass (window 2025-10-01 to 2026-10-11). Hashes are SHA-256 of the exact bytes parsed.

| Source ID | Title | Version | Retrieved (UTC) | Artifact URL | SHA-256 | Licence |
| --- | --- | --- | --- | --- | --- | --- |
| `rna-pathogen-20261011-tisza2026-source` | EsViritu is a sensitive and specific profiler for viral pathogen detection and genome recovery in metagenomes | bioRxiv 10.64898/2026.09.29.755457 v1, posted 2026-09-30; JATS XML | 2026-10-11T21:39:50Z | https://www.biorxiv.org/content/early/2026/09/30/2026.09.29.755457.source.xml | `fd92099655ddefdec31d35e273b80c4b233eed395c1cfc137eaddaa4efee232b` | CC-BY-NC-4.0 |
| `rna-pathogen-20261011-tisza2026-source-supp` | Tisza et al. 2026 Supplemental Tables S1-S25 (bioRxiv media-1.xlsx) | bioRxiv 10.64898/2026.09.29.755457 v1 supplementary file DC1 (755457_file02.xlsx) | 2026-10-11T21:45:51Z | https://www.biorxiv.org/content/biorxiv/early/2026/09/30/2026.09.29.755457/DC1/embed/media-1.xlsx?download=true | `0559022a3ff5ef5b2682e3c451eda51835c4c8d9be9dfdb1ebc9cd9295fb7701` | CC-BY-NC-4.0 |

DOI: 10.64898/2026.09.29.755457.

## Tables used

| Source | Tables | Results |
| --- | --- | --- |
| Supplementary XLSX | S2 (detection probability at 10 and 100 read pairs, 5 tools) | 10 |
| Supplementary XLSX | S6 (negative controls, 5 tools x 4 summaries) | 20 |
| Supplementary XLSX | S9 (mock communities, 5 tools x 5 rank or truth modes x 3 metrics) | 75 |

## Authorship and origin

Developer benchmark. The EsViritu authors (Baylor College of Medicine) built the data, ran all five tools on a parameter grid against one shared database and chose each tool's headline setting. All 15 evaluations are `author_reported`. Kraken2 configurations link to the existing `catalog-model-kraken2`; Centrifuger, Metabuli, Sylph and EsViritu get new family method records.

## Licence and archived copies

CC BY-NC 4.0 (bioRxiv API and JATS XML). No copy is archived; hashes and locators only.
