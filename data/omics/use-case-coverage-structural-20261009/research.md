# Research: structural hypotheses use-case pass, 2026-10-09

Use case: `use-case-structural-hypotheses-experiments` ("Which predicted interfaces or structures are reliable enough to guide my next experiment?"). Existing judgements: four ClusPro docking protocols on BM5 (enzyme and others, top 10 and top 30) and FoldBench protein-protein, nine evaluations in all, all proxy. No new source here duplicates theirs.

Goal: independent comparisons of several structure or interface predictors on the same experimentally solved, post-cutoff set, with printed per-method values, grouped by complex class because the use case's third exclusion says classes do not transfer.

Bounds: cutoff 2026-10-09; budget 25 queries, 6 used; at most 3 sources, 2 extracted; lean batch (100 records, 152 KB, plus 67 KB of archived XML). Worker: Claude (Opus 5.5) research agent; no human review claimed.

## Queries

Full entries: `search-use-case-structural-hypotheses-q1` to `q6` in `data/omics/search-ledger.jsonl`.

| # | Query (short form) | Channel | Outcome |
| --- | --- | --- | --- |
| 1 | Runs N' Poses ligand cofolding generalisation | web search | Lead found |
| 2 | Runs N' Poses lookups (bioRxiv, Europe PMC, publisher, full text) | bioRxiv API, Europe PMC, web fetch | Values are figure-only; excluded |
| 3 | AF3 and Boltz or Chai on antibody or nanobody complexes, DockQ, open access | Europe PMC | Fromm et al. and Smorodina et al. taken forward |
| 4 | AF3 and Chai or Boltz on protein-ligand, PoseBusters or RMSD, open access | Europe PMC | PoseBench and a Boltz GPCR study screened out |
| 5 | Smorodina et al. record and versions | Europe PMC, bioRxiv API | Version 1, CC BY |
| 6 | Independent protein-ligand pose tables after 2021 | web search | Nothing beyond FoldBench |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Fromm et al. 2026 (Bioinformatics), Table 1 | Extract all 27 values | 110 antibody-antigen complexes after the 30 September 2021 cutoff, 200 AlphaFold3 models each, and nine ways of picking one. The closest match to "which predicted interface can I trust" found: it measures what is lost when a user picks by confidence. |
| Smorodina et al. 2026 (bioRxiv preprint), Results text | Extract 23 printed values | AlphaFold3, Boltz-2 and Chai-1 on nanobody-antigen complexes, with the only test found of whether confidence separates real from non-cognate pairings, plus calibration against DockQ and a sampling curve that adds Boltz-1. |
| FoldBench antibody-antigen and protein-ligand (stored) | Map, no new records | Five tools on held-out targets for the two classes the use case names separately. Proposed instead of extracting a third source. |
| Runs N' Poses (bioRxiv; NSMB 2026) | Excluded | Independent and post-cutoff, but per-method success by training similarity is in figures; the text prints only pocket LDDT-PLI shares from a legend. |
| PoseBench (Nat Mach Intell 2026) | Excluded | Results in figures; the supplement has no result tables. |
| CASP16 oligomer assessment (Proteins 2026) | Excluded | Per-group values in figures; groups are teams, not methods; the supplementary workbook could not be retrieved. |

## How the judgements are grouped

| Group | Stratum | Protocol | What it tells a user |
| --- | --- | --- | --- |
| antibody-antigen-interfaces | 1 | FoldBench antibody-antigen (stored) | Structural success of five tools |
| | 2 | Fromm, model selection | How much picking by confidence loses against the best model |
| | 3 | Smorodina, best of N | How much sampling raises the best available model |
| | 4 | Smorodina, calibration | Whether confidence tracks accuracy, per tool |
| | 5 | Smorodina, cognate versus shuffled | Whether confidence indicates that an interaction exists |
| protein-ligand-poses | 1 | FoldBench protein-ligand (stored) | Pose success of five tools |

The stored protein-protein judgements have no `comparison_group` and were not edited. All six new judgements are proxy: each measures agreement with a deposited structure, or how well a confidence score tracks it, and none links a prediction to the outcome of an experiment (the first exclusion).

## How negatives are defined

Only the Smorodina cognate-versus-shuffled protocol has negatives. Each VHH is paired with every antigen; the observed pairing is the positive and every other pairing a negative. The source states that it assumes shuffled pairs are non-binders. None was tested, so some negatives may bind. This is on the dataset's `label_semantics`, the protocol's `limitations`, claim `structural-20261009-claim-smorodina2026-shuffled-negatives` and the judgement's rationale.

## Things a reviewer should judge

1. **Training exposure in Smorodina.** The set mixes systems inside and outside each tool's training data: AF3 30 of 106 in training, Chai-1 25, Boltz-2 64. The printed values pool all of them. Boltz-2's are the most exposed, which may explain why its best-of-N DockQ (0.57 at N = 1, 0.80 at N = 100) exceeds AF3's (0.24, 0.68) while its confidence is the least specific (average precision 0.026). Recorded on every Smorodina protocol and judgement.
2. **Cutoff statement in Smorodina.** The curation paragraph (P62) says post-October 2021 depositions were kept, "corresponding to the earliest training cutoff among the evaluated tools (Boltz-2)". The methods (P76) give Chai-1 about 12 January 2021 and Boltz-2 about 1 June 2023, so Boltz-2 is the latest, not the earliest. The per-tool counts match the methods. Recorded as a protocol limitation, not an evidence concern, because no printed value conflicts. A reviewer may prefer an `evidence_concerns` entry, which would withhold all three Smorodina judgements.
3. **Which models Fromm Table 1 ranks.** The caption does not give the number of models. Its DockQ row (0.544) matches the text's best-of-200 value (0.54), and the text's top-ranked value at the largest sample size (0.37) matches the ipTM and ranking-confidence rows (0.370, 0.375), so the table is read as selection among 200. Recorded as a limitation.
4. **Fromm per-target correlation.** Figure 6 and section 3.5 give 0.28 for ranking confidence; Table 1 prints 0.214 under a Spearman caption. The figure may use Pearson. Both are kept: the table value as a result, the text value in a limitation.
5. **Oracle rows.** DockQ, aeTM, aeiTM and aeRankConf in Fromm Table 1 use the experimental structure. They are stored as AlphaFold3 configurations with `author_reported` origin and a limitation saying they are upper bounds, as AssayBench's Oracle kNN was in the target validation batch.
6. **Selection rules as configurations.** Each Fromm row is a configuration of `discovery-model-alphafold-3` with the score in `selection`, rather than a new method record for each score. This keeps the batch lean and shows the comparison as one tool with nine pick rules. A reviewer may prefer method records for pDockQ2 and ipSAE, which are separate tools.
7. **Quadrant shares.** Smorodina's Q2 and Q4 percentages are printed for some tools only (Q2 for AF3 and Boltz-2, Q4 for AF3 and Chai-1), and the text does not say which sample they refer to. Unprinted cells are not inferred; each evaluation lists what is missing.
8. **Chai-1 sampling depth.** Chai-1 runs 5 trunk samples, so its smallest sampling depth is 5 models, not 1. Recorded on the protocol and the evaluation.
9. **Supplements not read.** The Smorodina supplementary tables were refused by a browser challenge. Per-system quadrant assignments (Supplementary Table 3) would allow the calibration values to be checked.

## Coverage

Bounded pass; not systematic. Not covered: CASP16 and CAPRI per-group tables, TCR-pMHC benchmarks, protein-nucleic acid classes beyond the stored FoldBench protocols, Runs N' Poses training-similarity strata, and any ipTM or pLDDT calibration table for protein-protein or protein-ligand complexes on a post-cutoff set.
