# Sources: BRCA1/BRCA2 germline interpretation use-case pass, 2026-10-09

The five sources behind the existing judgements (ENIGMA specification, Benet-Pages, HECTOR preprint, Hu 2026, So 2024) are not duplicated. Two papers, three source records. Hashes are SHA-256 of the bytes read. Both papers are CC BY 4.0; gzip copies (`gzip -n -9`) are in `artifacts/`.

| Source ID | Title | Version | Retrieved (UTC) | Artifact URL | SHA-256 | Licence |
| --- | --- | --- | --- | --- | --- | --- |
| `brca-20261009-source-cubuk2021` | Clinical likelihood ratios and balanced accuracy for 44 in silico tools against multiple large-scale functional assays of cancer susceptibility genes | Genetics in Medicine 23(11):2096, 2021-07-06; PMC8553612 XML | 2026-10-09T21:18:04Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8553612/fullTextXML | `ea6391e04f5f01353bb611fd45437f21c531848cf3e93b288bdc52494efc90ae` | CC BY 4.0 |
| `brca-20261009-source-cubuk2021-supplementary-tables` | Cubuk et al. 2021, Supplementary tables 1-13 | 41436_2021_1265_MOESM3_ESM.xlsx | 2026-10-09T21:18:15Z | https://static-content.springer.com/esm/art%3A10.1038%2Fs41436-021-01265-z/MediaObjects/41436_2021_1265_MOESM3_ESM.xlsx | `02df1b0dbf916d598dd8278ba45091022bf78c5722ac13a07d5b1b70d64dc179` | CC BY 4.0 |
| `brca-20261009-source-ramadane2025` | ACMG/AMP interpretation of BRCA1 missense variants: Structure-informed scores add evidence strength granularity to the PP3/BP4 computational evidence | American Journal of Human Genetics 112(5):993, 2025; PMC12120176 XML | 2026-10-09T21:18:06Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12120176/fullTextXML | `cd089e7c621818f457f54f93c37cc1b9d535e531212b1aaf431fcbdd733bbda1` | CC BY 4.0 |

## Existing records reused, not changed

| Record | Use in this pass |
| --- | --- |
| `uc-clinical-20260930-method-bayesdel` (main) | Method for the four Cubuk BayesDel configurations and the Ramadane-Morchadi BayesDel configuration |
| 27 `somatic-oncogenicity-20261009-method-*` records (reviewed, not yet merged) | Methods for the matching Cubuk configurations and the AlphaMissense configurations; listed in `coverage.json` |
| `protein-stability-20261009-method-foldx` (reviewed, not yet merged) | Method for the four FoldX ΔΔG configurations |

The two unmerged batches must be integrated before this one.

## Archived copies

| File | SHA-256 of gzip |
| --- | --- |
| `artifacts/cubuk2021-article.xml.gz` | `c8fd47b55ae97b58b1784fdfcd805df326be67541983d352cebe96551d0d1994` |
| `artifacts/cubuk2021-supplementary-tables.xlsx.gz` | `ad3badc7cb9cf1e45a788129bbc33c8db1708a1716d66d4c4377abe48b7d6e6d` |
| `artifacts/ramadane2025-article.xml.gz` | `b5014b2f7e4d728af56f83b7c3a5e1560539f9577a2b114479a6253d54b101f4` |
