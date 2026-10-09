# Controlled-vocabulary follow-ups, 2026-10-09

Resolves the known limitations listed in [the controlled-vocabularies review](2026-10-09-controlled-vocabularies.md). Each change was checked by an AI-assisted research pass against the source's paper or official code; no human review is claimed. Every row of `data/vocab/corrections/2026-10-09-vocabulary-followups.csv` gives the record, the field, the value it replaces, the new value and the evidence. The command (`npm run records:correct`) refuses the table if any record no longer holds the expected old value. 2,372 corrections to 1,875 records; 156 more records own curated panels whose metric, unit or qualifier follow their corrected results, so 2,031 records change in all. No IDs, printed or numeric values change.

## Metrics

| Change | Records | Evidence |
| --- | --- | --- |
| Open Problems label projection `f1` to `weighted-f1` | 128 | openproblems v1.0.0 `f1.py`, `average="weighted"`; macro F1 is a separate metric |
| GUE `f1` to `macro-f1` | 10 | DNABERT-2 `train.py`, `average="macro"` |
| PFMBench EC and DeepLoc2 `f1` to `f1-max` | 24 | `model_interface.py` returns `f1_score_max` for multi-label tasks |
| Genomic Benchmarks 3-class regulatory `f1` to `micro-f1` | 2 | Table 2 prints F1 equal to accuracy, as micro F1 is |
| Other Genomic Benchmarks `f1`: qualifier "binary, positive class" | 16 | code at the paper's version |
| BEACON secondary structure `f1`: base-pair qualifier | 17 | `train_secondary_structure.py`, binary F1 over the pooled pairing map at 0.5 |
| Top-k accuracy and MCES: qualifiers "retrieval" or "de novo, exact match" | 313 | MassSpecGym equations 1 and 4; MSAlign and MIST CANOPUS are retrieval |
| Ligand RMSD < 2 Å: atom set and pose selection | 4 | LiPP states all-atom, top-scoring pose; Boltz-1 does not state the atom set |
| Boltz stereochemistry RMSDs: "median over complexes" | 19 | Table 1 footnote a |
| GEARS Pearson DE: "all genes" | 4 | Supplement defines delta expression with no gene subset; Fig. 2c "across all genes" |
| ClusPro CAPRI counts and NMDN screening success: difficulty class, top N, cutoff not stated | 30 | ClusPro BM5 Table 1 footnote; NMDN Table 2 |

All 123 bare "AUC" rows mapped to `auroc` come from sources that state ROC (Feng's Methods, ten other papers, ProteinGym's `roc_auc_score`), so no "curve type assumed" qualifier is needed.

Definitions are corrected for `f1-max` (multi-label implementations), `ligand-rmsd` and `ligand-rmsd-under-2a-rate` (atom set as stated, not heavy atoms only), `pearson-delta` (all genes unless qualified), `capri-medium-target-count` (neutral on whether high-accuracy targets are included) and `casf-screening-success-rate` (cutoff in the qualifier). The top-k concepts carry a scope note: retrieval and de novo values are not comparable.

## Units

- 426 values printed ×100 that are not proportions (BEACON R² and Spearman, GUE MCC, AUROC ×100) move from `percent` to `unitless` with `unit_detail` "printed x100".
- 787 AUROC, TM-score and NDCG values move from `fraction` to `unitless`: they are normalised scores, not proportions of items.
- 22 MCES edit distances move from `count` to `unitless`: MassSpecGym weights them by bond order and averages over spectra.
- One Boltz-1 success rate moves to `fraction`: 0.545 is a proportion of complexes.

`fraction`, `unitless` and `count` carry scope notes stating these rules.

## Areas, method types and baselines

- The 90 records originally tagged `cells-spatial-multiomics` are single-cell RNA-seq: GEARS and PertEval-scFM on Norman 2019 Perturb-seq, scFoundation annotation and scGPT. They move from `cells-tissues` to the narrower `single-cell`.
- `molecular-interactions` matches EDAM topic_0128 (Protein interactions) with topic_0602 as a broad match, so it no longer shares its match with `biological-networks`.
- Method type `baseline` was a role, not a type. Kraken2, AutoDock Vina and scVI move to `specialist`, like their siblings; their comparator role stays on their baseline records. The concept is removed.
- Baseline types `random_forest`, `linear_regression` and `gradient_boosted_trees` named algorithms. Their records move to `simple_statistical`, and the algorithm is kept in the new `baseline_algorithm` field from `data/vocab/algorithm.ttl`, which matches STATO where it can. The three Rewire ridge probes, filed as `established_method` but described as Rewire controls, also move to `simple_statistical` with algorithm `ridge_regression`. The three algorithm concepts are removed from baseline types.

## Noticed, not changed

- Other RNA secondary-structure F1 rows are probably base-pair F1.
- BEACON's modification AUC is a mean over 12 types.
- About 27 TDC ADMET and ATOM3D protocols are filed under molecular interactions.
- Many of the 1,547 `cells-tissues` records are single-cell.
- lit-045 and lit-046 duplicate two Boltz acquired results.
