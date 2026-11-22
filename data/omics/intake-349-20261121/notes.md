# Intake for issue #349

Add discovered benchmark Learning inhibitor interactions from protein deep mutational scanning data and deep learning models: MET kinase DMS benchmark for ligand-conditioned variant effect and affinit

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-21. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-349-20261121-benchmark-met-kinase-dms-benchmark` (benchmark, depth tier 2)
- `intake-349-20261121-dataset-kinase-inhibitor-datasets` (dataset)

## Sources

- https://github.com/fraser-lab/Kinase_Inhibitor_Datasets: `intake-349-20261121-source-github-fraser-lab-kinase-inhibitor-datasets-github`, SHA-256 c73a674fa8e683a4069ee818111e01f7cff7a93621e825871efacb81e032747d, text/html
- https://www.biorxiv.org/content/10.64898/2026.11.01.763444v2: `intake-349-20261121-source-learning-inhibitor-interactions-from-protein-deep-mutational`, SHA-256 2a41042b43b592162d0e8fe970961858c1460006366eadd5612c37ddc8629616, text/html
- https://www.biorxiv.org/content/10.64898/2026.11.01.763444v1: not opened (HTTP 429)

## Not added

- None.

## Links

- `intake-349-20261121-benchmark-met-kinase-dms-benchmark` uses_data `intake-349-20261121-dataset-kinase-inhibitor-datasets` (Kinase_Inhibitor_Datasets), in this batch: GitHub README, repository layout: the MET tables sit inside the Kinase_Inhibitor_Datasets repository. Treated as a weak link, supported because e2 is kept as a distinct dataset.

## Possible duplicates in the store

- None.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| MET kinase DMS benchmark | version |   | No |
| MET kinase DMS benchmark | task | Mutational-effect prediction (per-variant fitness, mean target in kinase-domain numbering, 287 aa) and affinity or ddG p | Yes |
| MET kinase DMS benchmark | scope_note | Scope is the MET kinase domain plus full-length context. The README also gives five other kinase DMS sets (CDK4, CDK6, E | Yes |
| Kinase_Inhibitor_Datasets | version |   | No |
| Kinase_Inhibitor_Datasets | access | GitHub repository https://github.com/fraser-lab/Kinase_Inhibitor_Datasets; CSVs at the repository root and in kinases/ a | Yes |
| Kinase_Inhibitor_Datasets | species |   | No |
| Kinase_Inhibitor_Datasets | scope_note |   | No |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 (prompt over 100k) | 2161 | 8964 | 93402 | 6711 | 0 | 3 | $0.0281 |
| claude-haiku-5-5 | 8280 | 0 | 0 | 4626 | 0 | 0 | $0.0031 |
| claude-sonnet-5-5 | 4 | 7256 | 9875 | 1970 | 0 | 0 | $0.0388 |
| Total | | | | | | | $0.0701 |

## Revision after review

The reviewer agent requested changes (https://github.com/rewire-bio/rewire-benchmark-data/pull/354#pullrequestreview-6008105703). The intake agent revised the batch once; it changes only the fields the review did not pass, and it does not revise again.

- `intake-349-20261121-dataset-kinase-inhibitor-datasets` duplicates: ruled distinct from `perturbpfn-20261115-data-sciplex-hdac-3x4` ("Sci-Plex HDAC-inhibitor subset, 3 cell lines by 4 drugs (GIM preprocessing)"). Ruled in the revision after review: a different resource. New record: "Deep mutational scanning fitness tables". Store record perturbpfn-20261115-data-sciplex-hdac-3x4 (dataset_subset): "single-cell profiles of A549, K562 and MCF7 cells". The script compared the source URLs, DOIs and repository addresses the two records give and found none in common; it cannot see one resource cited at two unrelated addresses. The new record holds kinase deep mutational scanning data, while the store record holds Sci-Plex single-cell drug-response profiles. The two records share no address: the new record is t
- `intake-349-20261121-dataset-kinase-inhibitor-datasets` duplicates: ruled distinct from `tgtval-20261009-data-carnevale2022-tcell` ("Carnevale et al. 2022 screen, T-cell resistance to tumour-microenvironment inhibitory signals"). Ruled in the revision after review: a different resource. New record: "Deep mutational scanning fitness tables". Store record tgtval-20261009-data-carnevale2022-tcell (dataset): "Perturbation screen identifying genes". The script compared the source URLs, DOIs and repository addresses the two records give and found none in common; it cannot see one resource cited at two unrelated addresses. The new record holds kinase variant fitness measurements under inhibitors, while the store record is a T-cell gene perturbation screen. The two records share no address: the store record's addresses are arx
- `intake-349-20261121-benchmark-met-kinase-dms-benchmark` links: dropped uses_data intake-349-20261121-dataset-kinase-inhibitor-datasets; now none.
