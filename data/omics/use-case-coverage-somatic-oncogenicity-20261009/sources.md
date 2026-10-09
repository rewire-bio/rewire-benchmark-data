# Sources: somatic small-variant oncogenicity use-case pass, 2026-10-09

The existing OncoVI source (`uc-clinical-20260930-source-oncovi`) is not duplicated. Article XML came from the Europe PMC REST API; supplementary workbooks from the publisher; the preprint from bioRxiv; the result table from the author's GitHub repository at a pinned commit. Hashes are SHA-256 of the bytes read. Gzip copies (`gzip -n -9`) are in `artifacts/` (CC BY 4.0 for Chen et al. and the preprint; MIT for the repository file).

| Source ID | Title | Version | Retrieved (UTC) | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `somatic-oncogenicity-20261009-source-chen2020` | Comprehensive assessment of computational algorithms in predicting cancer driver mutations | Genome Biology 21:43, 2020-02-20; PMC7033911 XML | 2026-10-09T20:45:50Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7033911/fullTextXML | `fef52f70c3a0ff3f82902f87080933c220e12274787de6309b41ee283daf8b8e` |
| `...-chen2020-additional-file-1` | Default prediction categories of 17 algorithms | MOESM1_ESM.xlsx | 2026-10-09T20:47:19Z | https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-020-01954-z/MediaObjects/13059_2020_1954_MOESM1_ESM.xlsx | `483840c2546f42b3517bcbcd583a3af083df45470e35e4955eda260a19152b09` |
| `...-chen2020-additional-file-9` | Benchmark 2, median threshold, 33 algorithms | MOESM9_ESM.xlsx | 2026-10-09T20:46:04Z | https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-020-01954-z/MediaObjects/13059_2020_1954_MOESM9_ESM.xlsx | `64b284aefb768c963a5e7079594d3bb7173ef3a5a5e6b0936d0a78126f25440c` |
| `...-chen2020-additional-file-10` | Benchmark 2, default categories, 17 algorithms | MOESM10_ESM.xlsx | 2026-10-09T20:46:14Z | https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-020-01954-z/MediaObjects/13059_2020_1954_MOESM10_ESM.xlsx | `b9c41136f45b38533312baa4abfe2923390861c4e49d4d91c6d0275a85222294` |
| `...-chen2020-additional-file-21` | Benchmark 5, median threshold, 33 algorithms | MOESM21_ESM.xlsx | 2026-10-09T20:46:04Z | https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-020-01954-z/MediaObjects/13059_2020_1954_MOESM21_ESM.xlsx | `47c4d461085334b017994d1846ceb06d6e44e7be369ecd2ecfe00620d6a0f7f5` |
| `...-chen2020-additional-file-22` | Benchmark 5, default categories, 17 algorithms | MOESM22_ESM.xlsx | 2026-10-09T20:46:15Z | https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-020-01954-z/MediaObjects/13059_2020_1954_MOESM22_ESM.xlsx | `21ed28f45eee2149e88dff6b75680c99001c4b6daa9805cc9e473d2300ae117a` |
| `somatic-oncogenicity-20261009-source-lee2026` | An openly licensed benchmark and per-gene calibration map for missense pathogenicity predictors on activating cancer drivers | bioRxiv 2026.07.16.739080 v1 (posted 2026-07-23), full-text HTML (mutable page; one retrieval) | 2026-10-09T20:48:19Z | https://www.biorxiv.org/content/10.64898/2026.07.16.739080v1.full | `1b4dfadc861c6b8dbecde6ebb5efdb5ab7203bcf6f1b4e06edc70e167e7050e9` |
| `somatic-oncogenicity-20261009-source-lee2026-oncocal-tool-performance` | OncoCal tables/tool_performance.tsv | commit 40b7770f2a768ba800c4f4c6b48e2bfe967ed14a | 2026-10-09T20:48:49Z | https://raw.githubusercontent.com/tjdrnjsqpf/oncocal/40b7770f2a768ba800c4f4c6b48e2bfe967ed14a/tables/tool_performance.tsv | `8f5a81078482c8010b83bba6225e9707980a3a7cebbb2ca00ed8b155ad34c3b5` |

Source ID prefix `...` is `somatic-oncogenicity-20261009-source`.

## Archived copies

| File | SHA-256 of gzip |
| --- | --- |
| `artifacts/chen2020-additional-file-1.xlsx.gz` | `eac8e0a5e52c8a638208ab446cd6e6692318042805949b81426e713074045715` |
| `artifacts/chen2020-additional-file-10.xlsx.gz` | `53dc97164a1e625bc55c87d0e4be246189c7234935f9bfb85df04b7977c20dca` |
| `artifacts/chen2020-additional-file-21.xlsx.gz` | `4d64f1b12fe251f73da5417ffc09c996f8f64baa0787440fdeb83dfcd0812f18` |
| `artifacts/chen2020-additional-file-22.xlsx.gz` | `ee707905d7df18b72042403949948d65e3e5575d64c2ced22f6aa679e63f509c` |
| `artifacts/chen2020-additional-file-9.xlsx.gz` | `358afffe609030633cb88106fc161b39b681b7e5e3efa908b118d59e7980fcdb` |
| `artifacts/chen2020-article.xml.gz` | `409167ef6b039a6b96d75555e7f463cc3601dad742100cd65c966d05a4c0e553` |
| `artifacts/lee2026-oncocal-tool-performance.tsv.gz` | `f9161781d60d5341ac1eadcd9344057cd793f16b0b93e5d65bcd0c5de76bfb66` |
| `artifacts/lee2026-preprint-full-text.html.gz` | `4d8a602a29e89f6bf3295ea656cdaa9a541faf20e1d786e6d74db129b991869d` |
