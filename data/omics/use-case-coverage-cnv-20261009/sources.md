# Sources: CNV detection use-case pass, 2026-10-09

All new sources were retrieved from the Europe PMC REST API (full-text XML and supplementary-file bundles). Hashes are SHA-256 of the exact bytes used. Container hashes are recorded on each supplement source record. Gzip copies (`gzip -n -9`) of every new artifact are in `artifacts/`; all are CC BY 4.0.

| Source ID | Title | Version | Retrieved (UTC) | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `cnv-20261009-source-delavega2025` | Benchmarking of germline copy number variant callers from whole genome sequencing data for clinical applications | Bioinformatics Advances 5(1):vbaf071, published 2025-04-10; PMC12005901 full-text XML | 2026-10-09T15:24:22Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12005901/fullTextXML | `ed6492f89d77454416d4fb135bb56bdcd5fb202e8a0ba94b92fa450441b4091f` |
| `cnv-20261009-source-delavega2025-table-s3` | De La Vega et al. 2025, Supplemental Table 3 | Supplemental_Table_3.xlsx inside vbaf071_supplementary_data.zip | 2026-10-09T15:24:22Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12005901/supplementaryFiles | `d900a69ec00915f1eb62dcf6b1ece0240cd4ba7937000652a6423fb813420bde` |
| `cnv-20261009-source-gabrielaite2021` | A Comparison of Tools for Copy-Number Variation Detection in Germline Whole Exome and Whole Genome Sequencing Data | Cancers 13(24):6283, published 2021-12-14; PMC8699073 full-text XML | 2026-10-09T15:21:28Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8699073/fullTextXML | `d8e954e141a06601b11b986338e45b57a3d5a98ac9e85411895b0ca1249b790f` |
| `cnv-20261009-source-gabrielaite2021-table-s2` | Gabrielaite et al. 2021, Table S2 (precision and recall of CNV calling tools) | Supplementary Materials/Table S2.xlsx inside cancers-13-06283-s001.zip | 2026-10-09T15:21:28Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8699073/supplementaryFiles | `eb4bb389b248508531ca371ba80e004a573f4e85029583cff336f217307fde85` |
| `cnv-20261009-source-nardone2025` | A Hitchhiker Guide to Structural Variant Calling: A Comprehensive Benchmark Through Different Sequencing Technologies | Biomedicines 13(8):1949, published 2025-08-09; PMC12383524 full-text XML | 2026-10-09T15:28:17Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12383524/fullTextXML | `45317b1396f900fd8bcbe6e95519a4b475fda4c5ee416c63752811b71e154eb8` |
| `cnv-20261009-source-nardone2025-table-s1` | Nardone et al. 2025, Table S1 (ten short-read SV callers on HG002) | TableS1.xlsx inside biomedicines-13-01949-s001.zip | 2026-10-09T15:28:17Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12383524/supplementaryFiles | `1e84dde9132aa977c069e3ce50132247a83969316cbd7c98f238ac54db032b14` |
| `cnv-20261009-source-seqc2-somatic-cnv-2024` | Evaluation of somatic copy number variation detection by NGS technologies and bioinformatics tools on a hyper-diploid cancer genome | Genome Biology 25:163, published 2024-06-20; PMC11188507 full-text XML | 2026-10-09T15:25:50Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11188507/fullTextXML | `944529ff7c2859bf04e5a95bd139eb2faffe444dc754d0f0736b648b706c8f6b` |

## Reused source

| Source ID | Use in this pass | Check |
| --- | --- | --- |
| `amp-source-dragen-supplementary-tables` | All cells of sheet `S4 CNV benchmarking` except H6 (already stored as `amp-result-dragen-cnv-sv-1-5kb-fscore`) | Re-downloaded 2026-10-09T15:30:17Z from the recorded `artifact_url`; SHA-256 `c8d66e8373f22382f1c5e4a576d2c85825a18232a14767d239966bc8ab56c3d9` equals the record's `original_artifact_sha256`. Not archived here: article licence is CC BY-NC-ND 4.0, consistent with the AMP intake. |
| `amp-source-dragen` | Cited alongside the supplement, as in the AMP intake | Article HTML not re-read in this pass |

## Archived copies

| File | SHA-256 of gzip |
| --- | --- |
| `artifacts/delavega2025-article.xml.gz` | `8dff71a628c7dd6d3f346f9ae69be7714b2026d0ced51017bb21aa31be8cb223` |
| `artifacts/delavega2025-supplemental-table-3.xlsx.gz` | `e996551634a2459df7df16614647cc6e05263c455acc296fc6cc15eb945583d8` |
| `artifacts/gabrielaite2021-article.xml.gz` | `4867db2675ab103d52035e41315b807d40c9331240017d5da14a90b366d155eb` |
| `artifacts/gabrielaite2021-table-s2.xlsx.gz` | `1d28586794ad54d0401d52f512b1e79d320714ed8cd66955ec7d9500ac87cdba` |
| `artifacts/nardone2025-article.xml.gz` | `d7ceb3d5fa446c594f7224185d188637393656e5410d6dbd7cd0e2ff522d7d14` |
| `artifacts/nardone2025-table-s1.xlsx.gz` | `640abb6f7cb6504a44457bacce473e85ae4eaa810f3e08154c4f85c57ba78fa8` |
| `artifacts/seqc2-somatic-cnv-2024-article.xml.gz` | `d26beb81379661b79b75fb4080e5f34d0589755840b1f011af70877d53c49fcd` |
