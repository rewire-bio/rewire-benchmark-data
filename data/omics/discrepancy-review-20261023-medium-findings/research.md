# Research: review of the open medium discrepancies, 2026-10-23

Release `2026-10-23-968c8720eea6` (rules version 3) had 13 open medium findings and one high. This batch records a review state for 13 of them. The fourteenth, Alavi 2026 (`discrepancy-52a714eb6bb63442`), already has its own review and is awaiting a correction.

For each finding, every outlier and consensus result on its contested page was read with its protocol, metric, configuration and source, and the two sides were compared for task, setting and configuration. No original paper was re-opened and no result was changed.

## Decisions

| Discrepancy | Pair | State | Reason | Issue |
| --- | --- | --- | --- | --- |
| `d734930095432234` | ESM-IF1, ProteinMPNN | explained | Sequence design (ProteinBench) against variant effect prediction (ProteinGym) | #201 |
| `f82ed80f71c6f0bd` | ESM3, ProteinMPNN | explained | The same task split; mirror of the next row | #205 |
| `fed245c475fd08dc` | ESM3, ProteinMPNN | explained | Mirror of the previous row | #205 |
| `14ca3a59b4201d63` | DNABERT-2, RNA-FM | explained | Mature mRNA tasks against non-coding RNA tasks; small margins | #202 |
| `34c6589a558a894f` | Eigen, MutationAssessor | explained | DMS endpoints against clinical endpoints; Livesey's own clinical result agrees with the consensus | |
| `1980d1e1d257348a` | Geneformer, scGPT | explained | Annotation transfer against embedding quality; consensus is mostly one study | #201, #206 |
| `80cbd3e7a2363fde` | Geneformer, scGPT | explained | Perturbation prediction against embedding quality | #201, #206 |
| `826efbc8dbe634da` | Mutect2, Octopus | explained | Tumour-only against paired tumour-normal calling; consensus is one study | #201 |
| `90953ef91286fc66` | DeepSomatic, ensembles | false-positive | Union, intersection and majority vote pooled as one system | #204 |
| `6e0a1543c1c68a64` | ESM-1v, ESM-2 | false-positive | Different ESM-2 sizes in the ProteinGym paper and repository | #206, #207 |
| `8c69346a6089882b` | RNAErnie, AIDO.RNA | investigating | Same assays, opposite order; signed against absolute Spearman | #209 |
| `4db3e5d24233e19b` | ESM-2, ESM3 | investigating | PFMBench's ProteinGym zero-shot scores differ from ProteinGym's own | #210 |
| `36711e250f9269de` | ESM-1b, EVE | investigating | Global AUC against per-gene average AUC | #211 |

Each claim's `rationale` gives the values behind its decision. The subjects are the finding's outlier results.

## Limits

- Automated review by a Claude agent from the published records; not human scientific review. The original papers were not re-opened, so a value extracted wrongly into the store would not have been caught.
- `14ca3a59b4201d63` is marked explained on the difference in sequence domain. RNA-FM's input length limit, which would add a second reason, has not been checked (#202).
- The two false positives settle findings that rule fixes (#204, #206, #207) should stop from firing. Once those fixes land, these findings will be kept as resolved findings.
- The three `investigating` claims have a next check of 2026-11-06.
