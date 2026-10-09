# Sources: plasma ctDNA methylation use-case pass, 2026-10-09

Hashes are SHA-256 of the exact bytes read. Times are UTC. Only the two CC BY 4.0 artifacts are archived (`gzip -n -9`, in `artifacts/`). The Sun et al. and Giuili et al. files are CC BY-NC-ND 4.0 and are pinned by hash only, as for the DRAGEN supplement in the CNV pass.

| Source ID | What | Version | Retrieved | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `ctdnameth-20261009-source-sun2024` | Sun et al., Systematic evaluation of methylation-based cell type deconvolution methods for plasma cell-free DNA | Genome Biology 25:318, 2024-12-19; PMC11660681.1 full-text XML | 19:58:16 | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11660681/fullTextXML | `ce2ac8671cfddf088b33efb150ca50354181de81ca6bfb181dd5bf387c6714e8` |
| `ctdnameth-20261009-source-sun2024-additional-file-1` | Sun et al., Additional file 1 (Tables S1-S8) | 13059_2024_3456_MOESM1_ESM.xlsx | 19:58:22 | https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-024-03456-8/MediaObjects/13059_2024_3456_MOESM1_ESM.xlsx | `1489ec85628ec60916f2d91faa131fff375436709edb850fee2ef50c860b31b0` |
| `ctdnameth-20261009-source-giuili2025` | Giuili et al., A benchmark of DNA methylation deconvolution methods for tumoral fraction estimation using DecoNFlow | bioRxiv preprint v1, 2025-11-27 (not peer reviewed) | 19:55:30 | https://www.biorxiv.org/content/10.1101/2025.11.27.688590v1.full.pdf | `1893cc9932e752a7575640dce585d5b3e3846f90626a564340c006437990adc7` |
| `ctdnameth-20261009-source-giuili2025-supp-table-1` | Giuili et al., Supplementary Table 1 (tools, versions, containers) | bioRxiv v1 media-3.xlsx | 20:03:05 | https://www.biorxiv.org/content/biorxiv/early/2025/11/27/2025.11.27.688590/DC3/embed/media-3.xlsx | `779ef36e9fadba68c18c095ef3684c8fecd890addeece3051356c42ee3c78e34` |
| `ctdnameth-20261009-source-giuili2025-supp-table-3` | Giuili et al., Supplementary Table 3 (median limit of detection) | bioRxiv v1 media-5.xlsx | 19:56:05 | https://www.biorxiv.org/content/biorxiv/early/2025/11/27/2025.11.27.688590/DC5/embed/media-5.xlsx | `c585f11e0b128705d8c224fc8551b3f1c2efe52fa568c0e0dc96e37abaaced32` |
| `ctdnameth-20261009-source-nguyen2023` | Nguyen et al., Multimodal analysis of methylomics and fragmentomics in plasma cell-free DNA for multi-cancer early detection and localization (SPOT-MAS) | eLife 12:RP89083, version of record 2023-10-11; PMC10567114 full-text XML | 20:04:09 | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10567114/fullTextXML | `e09cfb58a6055e89ffa7b553a37539e1687f0fcb26970b7b25eb9eda8e09cfa8` |
| `ctdnameth-20261009-source-nguyen2023-supp-file-1` | Nguyen et al., Supplementary file 1 (Tables S1-S11) | elife-89083-supp1.xlsx, PMC open-access copy PMC10567114.1 | 20:03:58 | https://pmc-oa-opendata.s3.amazonaws.com/PMC10567114.1/elife-89083-supp1.xlsx | `4797d7ea0fde127bfa54cf0bdf717d859092c0442ab996a0af10cc5ce17b7331` |

Licences, as stated in each source: Sun et al. article and additional files CC BY-NC-ND 4.0 (article XML `license`); Giuili et al. preprint CC BY-NC-ND 4.0 (bioRxiv API and PDF page footer); Nguyen et al. CC BY 4.0 (article XML `license`). No code licence was taken from any article.

## Evidence concerns recorded on sources

| Source | Concern |
| --- | --- |
| `ctdnameth-20261009-source-giuili2025-supp-table-3` | Sheet A RRBS-CL cells K4:O12 for UXM, MetDecode, meth_atlas, PRMeth and CIBERSORT disagree with Figure 4A and with the overall medians in sheet B. The WGBS-TT and RRBS-TT columns agree with Figure 4A. |
| `ctdnameth-20261009-source-nguyen2023-supp-file-1` | Table S9 stage-stratum sizes (for example discovery stage I n = 50) differ from Table S8 and article Table 1 (n = 52) for the same cohorts. Per-cancer all-stage sizes agree. |

## Related existing record

`amp-data-cfmethyl-408` describes the cfMethyl-Seq study cohort (Stackpole et al. 2022). Sun et al. reuse the same EGA study (their reference 26) with different counts, so the new dataset record notes the relation in `scope_note` and is not linked as the same data.

## Archived copies

| File | SHA-256 of gzip |
| --- | --- |
| `artifacts/nguyen2023-article.xml.gz` | `abe995e469349c3313640efad96348c82394cfe52f340f218675309404e00eda` |
| `artifacts/nguyen2023-supplementary-file-1.xlsx.gz` | `0edbb20352f7306824f11e41e9c6e9da0f5259a1b018d9349f75ce00f58fb299` |
