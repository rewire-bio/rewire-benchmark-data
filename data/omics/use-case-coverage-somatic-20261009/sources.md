# Sources: tumour somatic SNV and indel use-case pass, 2026-10-09

Article XML came from the Europe PMC REST API. The Wang et al. supplementary workbook came from the publisher's static file server. The Guille et al. supplementary files are members of the Europe PMC `supplementaryFiles` zip; that zip is assembled per request, so only the member file hashes are pinned. Hashes are SHA-256 of the exact bytes read. Gzip copies (`gzip -n -9`) of every pinned artifact are in `artifacts/`; all five are CC BY 4.0.

| Source ID | Title | Version | Retrieved (UTC) | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `somatic-20261009-source-wang2020` | SomaticCombiner: improving the performance of somatic variant calling based on evaluation tests and a consensus approach | Scientific Reports 10:12898, published 2020-07-30; PMC7393490 full-text XML | 2026-10-09T20:00:37Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7393490/fullTextXML | `5f4e6b16675a3a6587f7999792ef479a059851ea8f7a31b4a954901aced5a8b1` |
| `somatic-20261009-source-wang2020-tables` | Wang et al. 2020, Supplementary Tables (somatic caller performance) | 41598_2020_69772_MOESM3_ESM.xlsx (Tables S1-S9) | 2026-10-09T20:00:59Z | https://static-content.springer.com/esm/art%3A10.1038%2Fs41598-020-69772-8/MediaObjects/41598_2020_69772_MOESM3_ESM.xlsx | `b9b5c68c7f78ff16863f64bb414394fd7b7dcd600795532aab30e39cd8d39c81` |
| `somatic-20261009-source-guille2025` | A benchmarking study of individual somatic variant callers and voting-based ensembles for whole-exome sequencing | Briefings in Bioinformatics 26(1):bbae697, published online 2025-01-18; PMC11790059 full-text XML | 2026-10-09T19:56:52Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11790059/fullTextXML | `2c6fc6f329f7ebea34889de5f0cc8dff2d0d90b9a8dc3192ddac0949281c9827` |
| `somatic-20261009-source-guille2025-table-s7` | Guille et al. 2025, Supplementary Table S7 (validation dataset) | `tables7_bbae697.xls` in the Europe PMC supplementary files zip | 2026-10-09T20:08:20Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11790059/supplementaryFiles | `735470fcb1ae7c3578ab3efefe12fde4b73bac279a1e7185950e5c2c0f1073f2` |
| `somatic-20261009-source-guille2025-supplementary-methods` | Guille et al. 2025, supplementary methods (caller command lines) | `supplementary_methods_bbae697.docx` in the same zip | 2026-10-09T20:08:20Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11790059/supplementaryFiles | `222509b8ec4b47b0278d6ea504291dba07a615c2fa23e3aaef600ea6aaf39709` |

The Guille zip downloaded at 20:08:20Z had SHA-256 `f1f19b89f77e573914a7c164583657e7c211d54d0c9ca6e34f19a03fb30ab3d6` (13,019,486 bytes). Its member timestamps equal the request time, so this hash will not reproduce.

## Existing source cited, not changed

| Source ID | Use in this pass |
| --- | --- |
| `amp-oncology-rna-20261007-source-pmc6123722` | Lancet paper. Its stored Lancet and Strelka2 F1 results are quoted in the summary proposal. Not re-downloaded. |

## Archived copies

| File | SHA-256 of gzip |
| --- | --- |
| `artifacts/guille2025-article.xml.gz` | `3af933bafa3109a3334c0436f19badbb0868fad793ed1799b11830e07cff8add` |
| `artifacts/guille2025-supplementary-methods.docx.gz` | `b52fe35565efd599c029111e4ba79892ab1cb32206ea2856ccaeb3442b39b975` |
| `artifacts/guille2025-table-s7.xls.gz` | `3dbb73436ce41c15001be42ffce31a2b01d87500d3c4a80fc41cf18ae50b2734` |
| `artifacts/wang2020-article.xml.gz` | `dc88008f5a29cb5edee6b0915578f2866a85dc32ca50e3204bdd8261ad5c32f5` |
| `artifacts/wang2020-supplementary-tables.xlsx.gz` | `1d6fa20bf9f3efe7f42bd5dca2ea84af13f4e6d099f1d6639305c1b16d34d1a5` |
