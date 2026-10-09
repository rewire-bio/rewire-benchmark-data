# Sources: patient-RNA splicing use-case pass, 2026-10-09

All sources were retrieved from the Europe PMC REST API (full-text XML and, for Drost et al., the supplementary-file bundle). Hashes are SHA-256 of the exact bytes parsed. Only the CC BY 4.0 source is archived; the two CC BY-NC-ND 4.0 articles are not archived, following the CNV pass precedent.

| Source ID | Title | Version | Retrieved (UTC) | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `rna-splicing-20261009-source-drost2025` | Routine RNA-based analysis of potential splicing variants facilitates genomic diagnostics and reveals limitations of in silico prediction tools | HGG Advances 7(1):100521, published online 2025-09-22; PMC12547740 full-text XML. Licence CC BY 4.0 | 2026-10-09T20:30:41Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12547740/fullTextXML | `2a2e970526e4348d505d26356b830d96da9e32688c4de84841ac8137b62d5d32` |
| `rna-splicing-20261009-source-drost2025-data-s1` | Drost et al. 2025, Data S1 (Tables S1-S6) | `mmc2.xlsx` inside the supplementaryFiles zip. Licence CC BY 4.0 | 2026-10-09T20:31:37Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12547740/supplementaryFiles | `a3a69202b8f0d9ecb7fa22a16991d5e4d583b5ae72fd598206ea5c2b4c5c14ca` (member); zip `1c89a7ebc0bf686c6087d0fee86ba6f364a6d754d5bc7eb9c446b7db017f1ebc` |
| `rna-splicing-20261009-source-segarracasas2025` | Translating Muscle RNAseq Into the Clinic for the Diagnosis of Muscle Diseases | Ann Clin Transl Neurol 12(7):1465, published online 2025-05-25; PMC12257123 full-text XML. Licence CC BY-NC-ND 4.0 | 2026-10-09T20:33:50Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12257123/fullTextXML | `6e61a917c80d08357fe7316ad84f5cb84ac457fcce4cb1d3b5bf866046e2095d` |
| `rna-splicing-20261009-source-segers2026` | saseR: juggling offsets unlocks RNA-seq tools for fast and scalable differential usage, aberrant splicing and expression retrieval | Genome Biology 27:103, published online 2026-02-18; PMC13019952 full-text XML. Licence CC BY-NC-ND 4.0 | 2026-10-09T20:30:42Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13019952/fullTextXML | `af11b79beec80f945a14f13ce487193ad733d740cace922eba0bd6d63b9de560` |

The Europe PMC supplementaryFiles zip is assembled per request, so its hash may differ on re-download; the `mmc2.xlsx` member hash is the one bound to the records.

## Reused records

| Record | Use in this pass |
| --- | --- |
| `catalog-model-spliceai` | `configuration_of` target for the Drost SpliceAI configuration |
| `catalog-model-pangolin` | `configuration_of` target for the Drost Pangolin configuration |
| `amp-oncology-rna-20261007-dataset-kremer-patient-rna` | `data` and `uses_data` target for the Segers Kremer evaluations; same 119-sample fibroblast cohort, as junction and gene counts from the FRASER paper's Zenodo release |

## Archived copies

| File | SHA-256 of gzip (`gzip -n -9`) |
| --- | --- |
| `artifacts/drost2025-article.xml.gz` | `33e83a7a110a2c83166612b9a304697c3fc8b13c0f7a500f8c9d713bd947e48d` |
| `artifacts/drost2025-data-s1.xlsx.gz` | `868e1e124e5b1477a953f024c0bd13b9c0c6dfce4bc819fa37ffd87d9f3ecaf5` |
