# Comparison settings pilot, 2026-11-26

## Why

The store cannot surface disagreements between papers as it stands. Measured on release 2026-11-25-42e2bf19ad6f:

- 1,984 of 2,012 protocols with results hold results from exactly one study.
- Of 25,841 model, protocol and metric combinations, 79 are measured by two or more studies.
- The overlap exists but is not linked: protocols that mention ProteinGym come from 12 studies, ClinVar from 21, BRCA1 from 14, splicing from 19.

Each paper's evaluation was recorded as its own protocol and its own dataset, so two papers that ran the same test almost never share a record. The missing step is saying which protocols are the same test.

## What was tried

One agent per cluster read an export of the cluster's protocols with their descriptions, datasets, sources and up to 400 results each, and proposed *settings*: one test that different papers could run and get comparable numbers on. Each protocol in a setting is graded `same`, `near` (same data and metric, a stated difference) or `related` (same benchmark family, not comparable number for number). The agent then listed every case where the same model has different values from two sources, or two sources order a pair of models oppositely. `BRIEF.md` is the instruction it worked from. It used no network and only the export.

| Cluster | Protocols read | Settings | Protocols linked | Links graded same / near / related | Unassigned | Disagreements |
| --- | --- | --- | --- | --- | --- | --- |
| proteingym | 16 | 6 | 5 | 13 / 0 / 0 | 11 | 4 |
| clinvar-missense | 97 | 9 | 40 | 6 / 12 / 30 | 57 | 16 |
| splicing | 83 | 6 | 16 | 6 / 1 / 13 | 67 | 0 |

## What it found

- **ProteinGym.** ESM3 open scores 0.409 in the HyPLM report and 0.466 in the ProteinGym table on the v1.3 zero-shot average, most likely sequence-only against structure input. Five of eight shared models agree within 0.001. Rewire's local ESM-2 8M run on one assay reproduces the official value exactly.
- **ClinVar and BRCA1.** PhyloGPN: 0.84 from its authors against 0.799 from an independent paper running the official example code. Evo 2 7B on BRCA1 saturation genome editing, all SNVs: 0.904 in the Evo 2 paper against 0.875 in Rewire's run on the same 3,893 variants, and the coding subset differs in the other direction. ESM1b: 0.892 against 0.919 with the same scoring pipeline and different variant sets. CADD cannot be matched because the paper does not state its version, and v1.3 and v1.7 differ by 0.05 to 0.08.
- **Splicing.** Only 16 of 83 protocols could be linked, and no formal disagreement was found: most splicing work in the store appears in one paper only. Two leads are in its notes (Pangolin on MFASS, SpliceAI on the Riepe set).

## What it shows about the data format

1. Linking protocols to a shared setting is what makes results comparable. The existing `evaluates_task` link and the discrepancy rules' scope already use this; too few links exist.
2. A model identifier is too coarse for comparison. The model link merges Evo 2 40B, 7B and 7B base, CADD v1.3 and v1.7, and four phyloP tracks. Comparison has to be made at the checkpoint or version.
3. The stratum a result belongs to (coding, noncoding, a ClinVar cohort) sits in free-text locators, not in a field.
4. No rule looks for the simplest disagreement: the same system on the same setting with different values in two sources.

## Status

These are proposals. Nothing in the store was changed from them. The next change gives a setting a stored form (a task record that protocols link to, with a claim on the link that carries the grade and the stated differences), applies these three clusters, and adds the same-system rule.
