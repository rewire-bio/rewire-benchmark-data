# Sources: de novo binder design evidence (#176)

Seven artifacts, all retrieved on 2026-10-22. Hashes are of the exact bytes read.

| Record | Artifact | Version | Retrieved (UTC) | SHA-256 | Status | Licence |
| --- | --- | --- | --- | --- | --- | --- |
| `uc-binder-20261022-source-alphaproteo` | https://arxiv.org/pdf/2409.08022v1 (PDF, 49 pages, 12,333,400 bytes) | arXiv v1, posted 2024-09-12 | 2026-10-22T11:53:00Z | `953b35644c0fa06ff090d7614c2e19525831f8fde50242e176d54474133c5a42` | preprint | CC BY-NC-SA 4.0 |
| `uc-binder-20261022-source-bindcraft` | Europe PMC JATS full text for PMC12507698 | Nature version of record, doi 10.1038/s41586-025-09429-6 | 2026-10-22T11:55:00Z | `74bd2902d46460ec387ed6ee46b5bf8fe61b9ea09f2d7be4daa2046ac7e59d5d` | peer reviewed | CC BY-NC-ND 4.0 |
| `uc-binder-20261022-source-bindcraft-si` | Europe PMC supplementary archive for PMC12507698 (13,409,376 bytes) | holds `41586_2025_9429_MOESM1_ESM.pdf` and `41586_2025_9429_MOESM4_ESM.csv` | 2026-10-22T12:00:00Z | `a402ac50b4860e24430494cb4344c569bf29ef3b8e769372adcd3298659267de` | peer reviewed | CC BY-NC-ND 4.0 |
| `uc-binder-20261022-source-bennett` | Europe PMC JATS full text for PMC12727541 | Nature version of record, doi 10.1038/s41586-025-09721-5 | 2026-10-22T11:55:00Z | `d7876bc73c47f2cb3fcb0fa1ef917c89c9b67750a22f6402bf515f978cd1564a` | peer reviewed | CC BY 4.0 |
| `uc-binder-20261022-source-bennett-si` | `41586_2025_9721_MOESM1_ESM.pdf` (129 pages, 100,209,865 bytes), extracted from the Europe PMC supplementary archive for PMC12727541 | Supplementary Information, ModDate 2026-09-15 | 2026-10-22T12:05:00Z | `f5d4fc4f3a65a2dc3ab696e165bb86bf150b2437cdc1a7046cfbecae8ccab05c` | peer reviewed | CC BY 4.0 |
| `uc-binder-20261022-source-adaptyv-preprint` | https://www.biorxiv.org/content/10.1101/2025.04.17.648362v1.full (HTML) | bioRxiv v1 | 2026-10-22T12:01:00Z | `17039d69ecc37f45f6c402511b8f4497ce631003689fa95ad1ab221f8f787a4f` | preprint | not stated on the page |
| `uc-binder-20261022-source-adaptyv-repo-round2` | `results/result_summary.csv` in github.com/adaptyvbio/egfr_competition_2 | commit `fc91b91ddc367830b755b215dbc69669675ad6a0` | 2026-10-22T12:02:00Z | `b98dd231fa663e10e2768ad0cb7c8b33ba993bc809bd6168390ac87120ce3b7b` | official project source | code Apache-2.0, data ODbL |

## Hash scope notes

- **AlphaProteo.** The search pass could not retrieve this artifact: it exceeds the 10 MB page-fetch limit. It was downloaded with `curl` and read with `pdftotext -layout`. The hash is of that one retrieval.
- **Adaptyv preprint.** A mutable web page. The hash describes the 2026-10-22 retrieval, not a stable artifact.
- **Bennett Supplementary Information.** The Europe PMC supplementary archive for PMC12727541 came back without an end-of-central-directory record (103,690,987 bytes, SHA-256 `6b1bd61ba4d69d5393f56e0e0d12bb4349b45ce12496a1d3e6a5a8467c39203a`), so `unzip` and Python `zipfile` both refuse it. `bsdtar` read it as a stream and extracted the Supplementary Information member before failing on a later member. `pdfinfo` confirms the extracted member is a complete 129-page PDF with the article's title. The pinned hash is of that member, not of the truncated archive.
- **Adaptyv repository.** Pinned to a commit, not a branch. Only `results/result_summary.csv` was read and hashed; `results/replicate_summary.csv` (SHA-256 `a9209c25f8b891c2ead4cd4fe2573da8e6a5397c8c6b45b3a7e179a8211bf6a8`) was retrieved at the same commit but not used.

## Other artifacts fetched and not used as a source

| Artifact | Why not |
| --- | --- |
| `results/replicate_summary.csv`, `results/foldseek_results.tsv`, `results/sequence_similarity.csv`, `results/destress_binder_only.csv`, `results/destress_binder_with_egfr.csv` at the pinned Adaptyv commit | Computational metrics and per-replicate rows; no measured outcome this pass records |
| `41586_2025_9429_Fig1_HTML.gif` and the other BindCraft figure images | Figure numbers were not read from images |
| PMC article PDFs for both Nature papers | HTTP 404 through the PMC instance path; the JATS full text was used instead |

## Evidence concerns recorded on sources

Four, all internal inconsistencies in a source rather than extraction errors:

1. **AlphaProteo:** Table S2 prints the RFdiffusion IL-7RA rate as 16.8% and Table 1 as 17, but Section S4.1 states it as "16% versus 33%" and the TrkA value as "0% (versus 6%)" where the table prints 0.0 and 6.3. The text rounds down rather than to nearest.
2. **BindCraft:** Supplementary Data 1's row filter reconciles with the Results prose for nine of twelve targets and fails for PD-L1, CrSAS-6 and CbAgo, so the per-target counts cannot be recomputed from it.
3. **BindCraft:** Fig. 1b's caption defines success as binding observed on SPR, but PD-1 was screened by BLI in a bivalent Fc-fusion format and CLDN1 against soluble analogues, so the 46.3% average pools different endpoints.
4. **Bennett:** the main text states 95 designs per target for the SPR-screened campaigns; Supplementary Methods Table 6 prints 96.
5. **Adaptyv:** the paper prints round 1 as both 2.5% (5/201) and 3%, and round 2 expression as both 95% (378 of 400) and 94%. All printed values are recorded with their locators and none is reconciled.
