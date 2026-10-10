# Research: protein variant stability use-case pass, 2026-10-09

Use case: `use-case-protein-stability` ("What evidence supports ranking protein substitutions by folding stability, and what must be validated before choosing a method?"). Existing evidence: three judgements on the 47-residue AMFR construct in ProteinGym (ESM-2 checkpoints and a fixed-seed random ranking). Their four sources are not duplicated.

Bounds: cutoff 2026-10-09; 5 of 25 queries; 3 of 3 sources. Lane `protein-fitness`. Ledger IDs `search-use-case-protein-stability-protein-fitness-q1` to `-q5`.

## Queries

| # | Query (abridged) | Channel | Outcome |
| --- | --- | --- | --- |
| 1 | S669, Ssym, mega-scale or Tsuboyama with ddG and named predictors | Europe PMC | All three sources selected |
| 2 | title search for stability predictor benchmarks | Europe PMC | Mostly unrelated fields; one homology-structure study opened and excluded |
| 3 | ThermoMPNN, RaSP, Stability Oracle, PROSTATA with held-out or homology splits | Europe PMC | Two newer papers opened; results are figure-level |
| 4 | Full text of the two mega-scale papers, tables confirmed | Europe PMC | Tables 2, 3 and 1 confirmed as printed per-method tables |
| 5 | Dieckhaus reference positions for comparator provenance | Europe PMC | Table 3 rows traced to their source papers |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Pancotti et al. 2022, Table 1 | Extract every cell (231 results) | 21 predictors run once by one group on 669 experimental ddG variants from dissimilar proteins, with reverse variants and antisymmetry; the only independent comparison found |
| Dieckhaus et al. 2024, Tables 2 and 3 | Extract every printed cell (130 results) | Homology-clustered held-out split and a homologue-free split, which is what the question asks about; developer paper, so ThermoMPNN rows are author-reported and Table 3 rows are compilations |
| Chu et al. 2024, Tables 1 and 2 | Extract every cell (66 results) | Shows transfer from held-out mega-scale domains to six larger proteins; developer paper for ESM therm |
| Birolo et al. 2023 | Lead | Same Ssym set, adds structure-source sensitivity |
| Nat Commun 2025 rewired generative models | Excluded | Figure-level results |
| Bioinformatics 2022 homology models | Excluded | Tables describe datasets, not per-method performance |

## Modelling choices

- Twelve protocols: one for S669; four for Dieckhaus (Megascale held-out, Fireprot homologue-free, Ssym, S669); seven for Chu (held-out mega-scale domains and six single-protein datasets). One judgement each.
- Relevance: `direct` where the endpoint is folding stability on held-out proteins (S669, both Dieckhaus Table 2 splits, Chu mega-scale). `proxy` for the Dieckhaus Table 3 compilations and for Chu's six single-protein sets, whose endpoints are melting temperature, chemical stability or abundance.
- Origins: `independent_paper` for comparators the paper ran; `author_reported` for a paper's own method (ThermoMPNN, ESM therm, and the ACDC-NN and DDGun family in Pancotti); `paper_compilation` for Dieckhaus Table 3 rows cited from other papers.
- Method families merge printed variants of one tool (ACDC-NN and ACDC-NN-Seq, DDGun and DDGun3D, INPS variants, I-Mutant variants, DynaMut and DynaMut2, MUpro and MUPRO). ESM-2 and ProteinMPNN reuse the existing model records.
- Method types: physics or statistical tools as `conventional_pipeline`, ESM-2 as `foundation_model`, the rest as `supervised_machine_learning`. My classification; needs review.
- New metric `antisymmetry-bias`; the antisymmetry correlation uses `pearson-correlation` with direction `unknown` and a qualifier.

## Things a reviewer should judge

1. The ACDC-NN S669 RMSE difference between the two sources (1.60 against 1.49).
2. Whether Dieckhaus Table 3 belongs in the store at all, since it mostly repeats other papers.
3. The `proxy` label for Chu's six single-protein sets.
4. Method-type assignments and the new metric concept.
5. Unextracted predictor versions in Pancotti.

## Coverage

Bounded pass. Not covered: Tsuboyama 2023 itself, independent mega-scale comparisons, the ProteinGym stability subset as a printed table, the AMFR construct of the existing judgements, supplementary tables in all three sources, and multi-point or indel variants.
