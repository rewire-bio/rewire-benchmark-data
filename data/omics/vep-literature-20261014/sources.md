# Sources

All retrievals ran on 2026-10-14 (UTC). Archived copies in `artifacts/` are `gzip -9 -n` of the raw bytes; the raw SHA-256 is the one on the source record.

## Livesey and Marsh 2025 (new)

Livesey BJ, Marsh JA. Variant effect predictor correlation with functional assays is reflective of clinical classification performance. Genome Biology 26, 104 (2025), published 2025-04-22. DOI 10.1186/s13059-025-03575-w, PMID 40264194, PMC12016141. Licence CC BY 4.0 (article XML `<license>`).

### Article XML

- Record: `vep-lit-20261014-source-livesey2025-article`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12016141/fullTextXML
- Retrieved: 2026-10-14T13:36:01Z
- SHA-256: `1735ee461ef192d9de67c914e9ad73d72d8aa255ea0e3479eb68cd8631d99fa2`
- Archived: `artifacts/PMC12016141.xml.gz` (gzip SHA-256 `29f5202d785eb613e92ac7312879163ca94a6bf5b85fa94e49e2421d3a3916ce`)
- Used for: Results, Methods (rank score, AUROC, ClinVar and gnomAD data, DMS datasets, VEPs), Tables 1-3, Data availability.

### Supplementary Material 2 (Tables S1-S8)

- Record: `vep-lit-20261014-source-livesey2025-supplementary-2`
- Artifact: https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-025-03575-w/MediaObjects/13059_2025_3575_MOESM2_ESM.xlsx
- Retrieved: 2026-10-14T13:36:25Z
- SHA-256: `1b0d792d1a5d3daa95545a7973cabb131c45e42c952e7e5a447a72deef1d1e70`
- Archived: `artifacts/13059_2025_3575_MOESM2_ESM.xlsx.gz` (gzip SHA-256 `ea2295a7d3a4d9946a495a7f50ea710c91486587e0172de25104444938879a09`)
- Used for: Tables S3, S5, S6, S7 and S8 (values); Tables S1 and S2 (dataset and configuration descriptions); Legends sheet.

Supplementary Material 1 (Figs. S1-S6, `13059_2025_3575_MOESM1_ESM.docx`, SHA-256 `a6db30bff251bce412129087e3b1d4cf5a72314b0264d898cc62de4704b862fe`) was retrieved but not used: it holds figures only. No source record.

## ProteinGym at commit 144fe22 (four new, three reused)

Repository OATML-Markslab/ProteinGym, commit `144fe22b07dfaeec2b366f2346203a9838a55b4c` (committed 2026-03-25, head of `main` at retrieval). Licence MIT for the repository; data and model terms are separate.

| Record | File | Retrieved | SHA-256 | Archived |
|---|---|---|---|---|
| `vep-lit-20261014-source-proteingym-dms-substitutions-spearman-summary-144fe22` | `benchmarks/DMS_zero_shot/substitutions/Spearman/Summary_performance_DMS_substitutions_Spearman.csv` | 13:39:32Z | `ee61a7c09efbfbd8d9a6c9355092c798032a578fa58c6f6256b5da8778555fd4` | `artifacts/proteingym-144fe22-DMS_zero_shot_substitutions_Spearman_Summary_performance_DMS_substitutions_Spearman.csv.gz` |
| `vep-lit-20261014-source-proteingym-clinical-zero-shot-substitutions-auc-summary-144fe22` | `benchmarks/clinical_zero_shot/substitutions/AUC/Summary_performance_clinical_substitutions_AUC.csv` | 13:39:33Z | `fbe453d1aaa6c30a1d0adf610f7fc23c36044a8e2548b178d316777383f8fe93` | `artifacts/proteingym-144fe22-clinical_zero_shot_substitutions_AUC_Summary_performance_clinical_substitutions_AUC.csv.gz` |
| `vep-lit-20261014-source-proteingym-clinical-supervised-substitutions-auc-summary-144fe22` | `benchmarks/clinical_supervised/substitutions/AUC/Summary_performance_clinical_substitutions_AUC.csv` | 13:39:33Z | `f2e38aeac2624d87e7a35a5b16bd580de62c24db36973848e1d94ac3ce510359` | `artifacts/proteingym-144fe22-clinical_supervised_substitutions_AUC_Summary_performance_clinical_substitutions_AUC.csv.gz` |
| `vep-lit-20261014-source-proteingym-clinical-zero-shot-indels-auc-summary-144fe22` | `benchmarks/clinical_zero_shot/indels/AUC/Summary_performance_clinical_indels_AUC.csv` | 13:39:33Z | `98a532c0e2c3d4720b73b7c05cf0dcf0419438c326761aaae3b788799f5aa836` | `artifacts/proteingym-144fe22-clinical_zero_shot_indels_AUC_Summary_performance_clinical_indels_AUC.csv.gz` |

Reused unchanged (re-downloaded; hashes match the stored records):

- `run-doc-proteingym-readme-md-144fe22b`: `README.md` at 144fe22, SHA-256 `321487a8de52c6cfa647a658f61150dd72e0acb0125470524fb94d1f8b23321a` (13:41:35Z).
- `profile-protocol-proteingym-proteingym-performance-dms-benchmarks-py-0002bc1b`: `proteingym/performance_DMS_benchmarks.py` at 144fe22, SHA-256 `0002bc1b031c02dc2d67fde53da092c8fd301415645e8e83b425b4183570eba2` (13:41:35Z).
- `profile-protocol-proteingym-reference-files-dms-substitutions-csv-a8f49801`: cited for the 217-assay count; not re-downloaded.

## Screened, not used for records

| Item | Artifact | SHA-256 |
|---|---|---|
| Livesey and Marsh 2020, Mol Syst Biol 16:e9380, PMC7336272 | Europe PMC XML, 13:36:01Z | `db4522ec782b019e6e6c2d5ef3c86ad269bdf6e0ce2d264fbab4f1729ff670d0` |
| Livesey and Marsh 2023, Mol Syst Biol 19:e11474, PMC10407742 | Europe PMC XML, 13:36:01Z | `c548931adfd231f2f1f3426d0423f1c89b85d8c72ed5413772a7058ca232e353` |
| Livesey et al. 2026, Nat Commun, PMC13620131 | Europe PMC XML, 13:36:02Z | `409bb57fa79b3206fe84508e87522efc1ab90270e16df53cd8d53459d5c2cdc4` |
