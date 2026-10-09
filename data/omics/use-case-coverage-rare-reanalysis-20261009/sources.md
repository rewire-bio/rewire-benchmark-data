# Sources: rare-disease reanalysis use-case pass, 2026-10-09

Two studies are extracted, each pinned as an article source and a supplementary-file source. Seven protocols from the Talos 2026 study, already in the store with their own sources, receive new judgements; their sources are not re-pinned here. Hashes are SHA-256 of the exact bytes parsed.

| Source ID | Title or file | Version | Retrieved (UTC) | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `rare-reanalysis-20261009-source-demidov2024` | Comprehensive reanalysis for CNVs in ES data from unsolved rare disease cases results in new diagnoses | npj Genomic Medicine 9:49, published online 2024-10-26; PMC11513043 full-text XML | 2026-10-09T20:40:13Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11513043/fullTextXML | `8bd0d50c0f3a1018c1f5ada9088a748d27d787eb5598e9857d2ddede85854ce6` |
| `rare-reanalysis-20261009-source-demidov2024-supp` | Demidov et al., Supplementary Information (Supplementary Tables 1-5) | `41525_2024_436_MOESM1_ESM.pdf` from the Europe PMC supplementary bundle | 2026-10-09T20:40:40Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11513043/supplementaryFiles | `521480b4999903af5acfac1c33c9453ce1f1e5a8b641a1682c5e96e11aa577ef` |
| `rare-reanalysis-20261009-source-vestito2024` | Efficient reinterpretation of rare disease cases using Exomiser | npj Genomic Medicine 9:65, published 2024-12-18; PMC11655964 full-text XML | 2026-10-09T20:36:38Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11655964/fullTextXML | `b8cd48ed7e4a337ddf954d1b9bb004305ac78c383268592828e6203418d04058` |
| `rare-reanalysis-20261009-source-vestito2024-supp` | Vestito et al., Supplementary Table 1 | `41525_2024_456_MOESM1_ESM.pdf` (4 pages, PDF title "Supplementary_table_S1 copy") | 2026-10-09T20:36:47Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11655964/supplementaryFiles | `d761ccee3944cd762d1c07e5388ed2810bd57634e1fc2c23a054b547a710a5ad` |

DOIs: 10.1038/s41525-024-00436-6, 10.1038/s41525-024-00456-2.

The supplementary hashes are of the PDFs. Europe PMC rebuilds the bundle zip on each request (its member timestamps are the request time), so the zip hash is not a stable pin.

## Reused records, not re-pinned

| Record | Use here |
| --- | --- |
| `uc-clinical-20260930-source-talos`, `uc-clinical-20260930-source-talos-table1` | Sources of the six Talos Table 1 protocols and the Exomiser comparison protocol, which get new judgements for this use case. The Talos article is now also in PMC (PMC13472938, retrieved 2026-10-09T20:38:57Z for section titles only); the stored source pins the publisher page, and nothing was re-extracted. |
| `uc-clinical-20260930-method-exomiser` | Method that the 81 Vestito et al. configurations configure. |

## Licences and archives

| Source | Licence | Archived here |
| --- | --- | --- |
| Demidov et al. article | CC BY 4.0 (article XML `<license>`) | No. Removed in review on 2026-10-09: the article's Table 2 lists each pathogenic CNV with pseudonymised individual and family identifiers, which must not be stored here. Hash and URL recorded; the Europe PMC XML re-downloads to the pinned hash. |
| Demidov et al. supplement | CC BY 4.0 (article XML `<license>`) | `artifacts/demidov2024-supplementary-information.pdf.gz` (gene lists, annotation sources and aggregate counts; no per-patient rows) |
| Vestito et al. article and supplement | CC BY-NC-ND 4.0 (article XML `<license>`) | No, following the earlier handling of no-derivatives licences. Hash and URL recorded. |

| Archived file | SHA-256 of gzip |
| --- | --- |
| `artifacts/demidov2024-supplementary-information.pdf.gz` | `450f45168bc338df8308b9206b0cb2ac3f3d429a0ee2c3c0c235133251e76c94` |

## Tables used

| Source | Tables | Cells extracted |
| --- | --- | --- |
| Demidov et al. | Table 1 (three caller rows by eight count columns, each cell holding an all-chromosome count and a bracketed sex-chromosome count); Supplementary Table 4 (three caller rows by five columns) | 48 + 15 results. The 'Total' and '% of Events' rows of Table 1 and the 'Total' row of Supplementary Table 4 pool the callers and are kept as one claim. |
| Vestito et al. | Supplementary Table 1 (81 threshold pairs; TP, FN, FP, TN, recall, precision, F score and F2 score) | 648 results. The two threshold columns define the 81 configurations. |

## Authorship and origin

- **Demidov et al. 2024**: ClinCNV "was developed recently by a Solve-RD partner" (Methods), so ClinCNV is recorded as `author_reported`. CoNIFER and ExomeDepth are `independent_paper`.
- **Vestito et al. 2024**: the authors are the Exomiser developers. The Introduction says "We regularly update the software with new features", and the Author contributions say J. O. B. Jacobsen "developed Exomiser features". All 81 evaluations are `author_reported`.
- **Talos 2026** (reused): the existing evaluations are already `author_reported`.

## Sources read but not extracted

| Source | Why not extracted |
| --- | --- |
| Kaschta et al. 2026, medRxiv 10.64898/2026.05.16.26352295 v1 (JATS XML retrieved 20:38:04Z, sha256 `db4ed16a501eda14ba114f8693f39596b03d7afaeafa8adafa41d84d9a61f6bd`) | This is the closest match to the use-case question: manual versus automated (Talos) reanalysis of the same 219 unsolved genomes, with review minutes and candidates per case. But every per-method result is printed only in prose, Table 1 is an image, and the supplement (sha256 `e4282ab6d497d42bb20fbdb02935e38537ff630f73bfc98cd19b6e1aa0230a75`) is per-patient clinical data. The licence reserves all rights. The per-patient supplement was deleted from the scratch directory after hashing. |
| AMELIE 3, medRxiv 2020.12.29.20248974 v1 | All three tables are images. |
| Solve-RD, Nature Medicine 2025 (PMC11835725) and its Supplementary Tables (MOESM3, sha256 `0e6037a65a0df320cb39e8ec240993aa71643ca16f96eea379a8af11fbbe77b8`) | Yields by ERN and variant type for one workflow; no comparison of methods. The supplementary workbook is largely per-patient and was deleted from scratch after hashing. |
| MEI benchmark (PMC10853235), Romero et al. 2022 (PMC8795168), Talos preprint (PMC12258758) | See research.md. |
