# Variant effect predictors: bounded literature pass, 2026-10-14

Literature pass for missense and non-coding variant effect predictors (VEPs) named in [rewire-benchmark-data #153](https://github.com/rewire-bio/rewire-benchmark-data/issues/153), [#154](https://github.com/rewire-bio/rewire-benchmark-data/issues/154) and [#155](https://github.com/rewire-bio/rewire-benchmark-data/issues/155), which list predictors on the Atlas of Variant Effects Alliance (AVE) list that are not in the store. The AVE list was used only to know which names to look for. It has no scores and no licence, and no record cites it.

Use cases considered (from `data/entities/use-cases.jsonl`): `use-case-brca1-brca2-germline-interpretation`, `use-case-rare-disease-candidate-ranking`, `use-case-unresolved-rare-disease-reanalysis`, `use-case-somatic-small-variant-oncogenicity`, `use-case-protein-stability`, `use-case-splicing-follow-up`, `use-case-regulatory-variant-gene-follow-up`.

Starting commit: `origin/main` b67ec370d884ccdf5bc4d2728e6407474044aa13 (release 2026-10-14-53895165fa97), branch `claude/vep-literature-pass`. Search window cutoff 2026-10-14. Budget 60 queries; 10 used. No predictor, model or ProteinGym code was run, no weights were downloaded, nothing was paid for or requested, and nobody was contacted. Values were transcribed from a supplementary workbook and repository CSVs by a deterministic script. This is an extraction awaiting independent review: no record is marked reviewed, no `review.json` exists, and the batch is not in the store.

Batch: `data/omics/vep-literature-20261014/`.

## Disposition in brief

1. Livesey and Marsh 2025 (Genome Biol 26:104, CC BY 4.0) is the current edition of the Edinburgh DMS benchmark. It ranks 97 VEPs against 36 human deep mutational scanning (DMS) datasets and 83 VEPs on ClinVar pathogenic versus gnomAD missense variants in 819 proteins. Its supplementary Tables S3 and S5 to S8 print every VEP's rank score. All of those rank scores are extracted: 6 protocols, 570 evaluations, 667 results.
2. ProteinGym at commit 144fe22 (still the head of `main`): the official zero-shot DMS substitutions Spearman summary for 97 models, all 18 metric columns (1,746 results), and the three clinical AUC summaries (48 results). Existing ProteinGym configurations are reused.
3. Of the predictors in the three issues, 23 now have results: 17 of 40 in #153, 6 of 12 in #154, 0 of 11 in #155. All come from Livesey and Marsh 2025.
4. 13 relevance judgements, all proxy and all `needs_review`: rare-disease candidate ranking (9), BRCA1/BRCA2 (3), protein stability (1). None for reanalysis, somatic oncogenicity, splicing or regulatory follow-up.
5. The strongest sources not extracted are the CAGI6 Annotate-All-Missense assessment (Hum Genet 2025) and Tabet et al. 2024 (Genome Biol). Neither is in the store.

## Existing inventory

- ProteinGym: paper tables from NeurIPS 2023 (21 zero-shot models and the supervised and indel tasks), the AMFR row of the DMS-level Spearman CSV at 144fe22 for 97 models, Rewire's own AMFR runs, and the runner protocol `rewire-proteingym-v1-3-dms-substitutions` with no evaluations.
- Clinical VEPs as methods with configurations from the somatic oncogenicity pass (Chen 2020, Lee 2026) and the BRCA pass (Cubuk 2021).
- No Livesey and Marsh records and no ledger entries mentioning them.

## Search log (exact, dated)

Times are UTC request starts. Europe PMC queries used the REST `search` endpoint with `resultType=lite`.

| ID | Mode | Exact query | Time | Outcome |
|---|---|---|---|---|
| q01 | Europe PMC | `AUTH:"Livesey BJ" AND AUTH:"Marsh JA"` | 13:35:49Z | 27 hits; 2020, 2023 and 2025 editions and the 2026 Nat Commun discordance paper |
| q02 | Europe PMC | `(TITLE_ABS:"variant effect predictor" OR TITLE_ABS:"variant effect predictors") AND (TITLE_ABS:"deep mutational scanning" OR TITLE_ABS:"multiplexed assay") AND (TITLE_ABS:"benchmark" OR TITLE_ABS:"benchmarking") AND PUB_YEAR:[2024 TO 2026]` | 13:40:08Z | 3 hits; nothing new |
| q03 | Europe PMC | `(TITLE_ABS:"missense" ) AND (TITLE_ABS:"predictors" OR TITLE_ABS:"variant effect prediction") AND (TITLE_ABS:"benchmark" OR TITLE_ABS:"benchmarking" OR TITLE_ABS:"independent evaluation" OR TITLE_ABS:"comparison") AND (TITLE_ABS:"MAVE" OR TITLE_ABS:"deep mutational" OR TITLE_ABS:"functional assay" OR TITLE_ABS:"saturation genome editing") AND PUB_YEAR:[2024 TO 2026]` | 13:40:14Z | 8 hits; two 2026 preprint leads (cancer-driver missense benchmark; gene identity in ClinVar benchmarks) |
| q04 | Europe PMC | `(TITLE_ABS:"ProteinGym") AND (TITLE_ABS:"clinical" OR TITLE_ABS:"ClinVar") AND PUB_YEAR:[2023 TO 2026]` | 13:40:14Z | 6 hits; ProteinGym preprint already stored |
| q05 | Europe PMC | `(TITLE_ABS:"GPN-Star" OR TITLE_ABS:"PromoterAI" OR TITLE_ABS:"LOL-EVE" OR TITLE_ABS:"PrimateAI-3D") AND PUB_YEAR:[2023 TO 2026]` | 13:43:02Z | 13 hits; developer papers only |
| q06 | Europe PMC | `(TITLE_ABS:"non-coding" OR TITLE_ABS:"noncoding" OR TITLE_ABS:"regulatory") AND (TITLE_ABS:"variant effect predictors" OR TITLE_ABS:"variant effect prediction") AND (TITLE_ABS:"benchmark" OR TITLE_ABS:"benchmarking") AND PUB_YEAR:[2025 TO 2026]` | 13:43:02Z | 6 hits; method papers; none names a #155 tool |
| q07 | GitHub API | `repos/OATML-Markslab/ProteinGym/commits/main`; `git/trees/144fe22b...?recursive=1` | 13:39:17Z | head unchanged at 144fe22; four summary CSVs retrieved |
| q08 | Europe PMC | `(TITLE_ABS:"CAGI") AND (TITLE_ABS:"Annotate-All-Missense" OR TITLE_ABS:"annotate all missense")` | 13:52:29Z | CAGI6 assessment, PMC11976771; not extracted |
| q09 | Europe PMC | `(TITLE_ABS:"variant effect predictors") AND (TITLE_ABS:"UK Biobank") AND (TITLE_ABS:"All of Us") AND PUB_YEAR:[2024 TO 2026]` | 13:52:29Z | Tabet et al. 2024, PMC11218265; not extracted |
| q10 | Retrieval | Europe PMC `supplementaryFiles` and `bin/` routes for PMC10407742 | 13:37:00Z | failed: zip stalled; file route HTTP 403 challenge |

Search summaries and titles were used to find candidates only. No number below comes from a summary. Findings are bounded to these queries; no global absence or novelty claim is made.

## Findings

### 1. What the two sources measure

- **DMS ranking (Livesey and Marsh).** For each of 36 human proteins, one DMS score set (at least 1,000 single amino acid substitutions after removing every variant in ClinVar or gnomAD). Each pair of VEPs is compared on the variants scored by the DMS and both VEPs; the VEP with the higher absolute Spearman correlation wins. A VEP's rank score is its win rate against each other VEP, averaged over all others, on a 0 to 100 scale. It is relative: it depends on which VEPs are in the table and is not a correlation.
- **Clinical ranking (Livesey and Marsh).** The same pairwise method using per-protein AUROC, ClinVar pathogenic and likely pathogenic missense variants (obtained "06/08/2024", 0-star and conflicting removed) against all gnomAD v4.1 missense variants not classed pathogenic, in 819 proteins with at least 10 of each. No training variants were removed, so clinical-trained VEPs are not on equal footing. The authors attribute most of their gain on this benchmark to circularity (Results, Fig. 4).
- **VEP types.** Livesey and Marsh class each VEP as clinical-trained (53 VEPs), population-tuned (6) or population-free (38) by its exposure to human clinical or population variants (Results). Five VEPs trained on DMS data (Envision, CPT-1, DeMaSk, VARITY_R, VARITY_ER) are scored without the DMS sets they were trained on.
- **ProteinGym DMS summary.** Spearman per assay over 217 substitution assays (single and multiple substitutions), averaged per protein and selection type, then equally over five selection types (`performance_DMS_benchmarks.py` at 144fe22, lines 304 to 315). Breakdown columns by function, MSA depth, taxon and mutational depth.
- **ProteinGym clinical summaries.** Average AUC over proteins for pathogenic versus benign clinical variants (README lines 22 to 52). Supervised predictors come from dbNSFP 4.4a (README line 106) and were trained on clinical labels.

### 2. Livesey and Marsh 2025: top of each ranking

Values are the rank scores as stored in Supplementary Material 2 (shown here to one decimal place; full precision is in the records). "Proteins" is the number of DMS sets or clinical proteins with predictions for that VEP.

| Rank | DMS, all 36 sets (Table S3) | Score | Proteins | Clinical AUROC, 819 proteins (Table S8) | Score | Proteins |
|---|---|---|---|---|---|---|
| 1 | CPT-1 | 92.8 | 29 | SNPred | 83.2 | 805 |
| 2 | AlphaMissense | 90.7 | 36 | MetaRNN | 82.2 | 814 |
| 3 | ESCOTT | 88.2 | 36 | PHACTboost | 80.7 | 811 |
| 4 | popEVE | 87.3 | 30 | AlphaMissense | 77.5 | 818 |
| 5 | iGEMME | 86.0 | 36 | VEST4 | 77.1 | 802 |
| 6 | GEMME | 84.9 | 36 | popEVE | 76.6 | 604 |
| 7 | SaProt | 83.6 | 36 | MutScore | 76.6 | 796 |
| 8 | TranceptEVE | 82.1 | 28 | REVEL | 76.0 | 812 |
| 9 | VARITY_R | 81.8 | 27 | MOIpred_benign | 74.3 | 714 |
| 10 | ESM-1v | 81.5 | 36 | BayesDel_noAF | 71.8 | 811 |
| 11 | VARITY_ER | 80.5 | 27 | CPT (CPT-1) | 71.7 | 783 |

The top two DMS places are the same in every sensitivity table: direct assays only (CPT-1 93.5, AlphaMissense 92.1), indirect only (92.1, 89.5), SNV-accessible substitutions only (92.1, 89.2), and SNV-accessible with gaps filled (91.9, 89.5). VARITY_R moves from 9th overall to 3rd on indirect assays (86.4). The clinical ranking puts clinical-trained meta-predictors first, and CPT-1 is the top population-free VEP there.

### 3. ProteinGym at 144fe22

Clinical substitutions, supervised predictors (all 17 rows, Average_AUC): ClinPred 0.981, MetaRNN 0.977, BayesDel (addAF) 0.972, VEST4 0.929, REVEL 0.928, BayesDel (noAF) 0.925, VARITY (R) 0.921, VARITY (ER) 0.918, gMVP 0.914, CADD 0.905, PolyPhen2 (HVAR) 0.896, DEOGEN2 0.894, MPC 0.881, PolyPhen2 (HDIV) 0.879, MutationTaster 0.816, DANN 0.812, FATHMM 0.723.

Clinical substitutions, zero-shot (all 13 rows): TranceptEVE L 0.92, PoET (200M) 0.92, GEMME 0.919, EVE 0.914, ESM-1b 0.892, Provean 0.886, SIFT 0.878, SIFT4G 0.877, MutationAssessor 0.877, MutPred 0.875, PrimateAI 0.855, LIST-S2 0.842, LRT 0.805.

Clinical indels, zero-shot (18 rows): highest PoET (200M) 0.935, Provean 0.927, RITA L 0.922; lowest Unirep 0.599.

DMS substitutions (97 models): Average_Spearman highest VenusREM and AIDO Protein-RAG (16B), both 0.518; Function_Stability highest ProSST (K=2048) 0.653, ProSST (K=4096) 0.652, VenusREM 0.65.

The supervised and zero-shot clinical tables use different predictor sets and different training exposure. The supervised AUCs are not evidence that supervised predictors are better, because their training labels overlap ClinVar and the summary does not remove them.

### 4. Issue predictors now with results

All from Livesey and Marsh 2025. "DMS" means the five DMS protocols; "clinical" means Table S8.

| Issue | Predictor | DMS | Clinical | Note |
|---|---|---|---|---|
| #153 | 3Cnet, AlphScore, CAPICE, DeepSAV, InMeRF, MISTIC, Rhapsody, SIGMA, SNPred, SPRI, UNEECON, mvPPT, Sequence UNET | Yes | Yes | |
| #153 | MOI-Pred, Maverick | Yes | Yes | printed as `MOIpred_benign` and `Maverick_benign` |
| #153 | SNPs&GO, SNPs&GO3D | Yes | No | |
| #154 | Envision, DeMaSk, PHACT, LASSIE | Yes | Yes | Envision and DeMaSk scored without their training DMS sets |
| #154 | CPT | Yes (as CPT-1) | Yes (as CPT) | |
| #154 | COSMIS | No | Yes | no row in Table S2; not described in the text |

Not found with results in this pass: the other 23 of #153 (PON-PS and PaPI were dropped by Livesey and Marsh because predictions were no longer available), MTBAN, EA, UMD-Predictor, SSEmb, ESGMM and PrimateAI-3D of #154, and all 11 of #155. Livesey and Marsh score `mutationTCN` (Kim and Kim 2020) from the MTBAN server; it is recorded as its own method, not as MTBAN.

### 5. Relevance to the use cases

| Use case | Protocols judged | Relevance | Why not direct |
|---|---|---|---|
| Rare-disease candidate ranking | 5 Livesey DMS protocols, Livesey clinical, 3 ProteinGym clinical | proxy | Within-protein variant ordering and pathogenic-versus-population discrimination, not recovery of causal variants in cases or review effort |
| BRCA1/BRCA2 germline | Livesey clinical, ProteinGym clinical zero-shot and supervised | proxy | Pan-gene and uncalibrated to ACMG/AMP evidence strength; whether BRCA1 or BRCA2 are among the 819 proteins is not stated in the extracted tables (BRCA1 was dropped from the DMS set for too few variants) |
| Protein stability | ProteinGym DMS (Function_Stability column only) | proxy | The headline average mixes non-stability assays; stability assays include multiple substitutions |
| Unresolved reanalysis | none | | No protocol measures new diagnoses or effort from reanalysis |
| Somatic oncogenicity | none | | Clinical sets are germline ClinVar labels; the cancer-driver preprint is a lead, not extracted |
| Splicing, regulatory follow-up | none | | No splicing or non-coding endpoint was extracted |

The `assessed_by` links on the use cases are listed in `coverage.json` (`pending_use_case_links`) and are to be added with `records -- change` after review. Use-case summary claims were not drafted, because they should cite reviewed results.

## Source conflicts and anomalies (left as printed)

1. Table S8 prints 'CPT' and 'fathmm-XF' where Tables S2 and S3 print 'CPT-1' and 'FathmmXF'. Mapped to the same configurations, each result carrying a `source_anomaly`.
2. Table S8 prints 'CADD' alongside 'CADD_1.7'; Table S2 lists CADD 1.6 and 1.7. The version of the 'CADD' row is unstated and it has its own configuration.
3. 'COSMIS' appears in Table S8 only.
4. Table S1 has no row 3 and blank assay descriptions for TPK1, SUMO1, UBE2I and CASP7, so the direct and indirect groups cannot be counted from it.
5. The paper text says 83 VEPs in the clinical ranking; Table S8 has 85 rows (BayesDel, PolyPhen-2 and VARITY variants are separate rows).
6. ProteinGym's clinical zero-shot substitutions CSV repeats the `Model_rank` header with an empty column and lists only 13 models; its completeness is not stated.
7. ProteinGym's bootstrap standard errors are relative to the top model (top rows print 0.0); recorded as such for the DMS file and as an unresolved spread for the clinical files.

## Access and reuse

| Item | Paper | Data | Code |
|---|---|---|---|
| Livesey and Marsh 2025 | CC BY 4.0 | Predictions at figshare doi:10.6084/m9.figshare.28295198 and 28295249 (not retrieved) | Scripts at figshare doi:10.6084/m9.figshare.28295408, MIT (not retrieved) |
| ProteinGym 144fe22 | n/a | Summary CSVs in an MIT repository; assay and clinical data carry their own terms | MIT |

Failed access, not retried: the Livesey and Marsh 2023 supplementary zip (stalled at 2,666,496 bytes) and its Table EV6 file route (HTTP 403 challenge HTML, SHA-256 `7135c12e1c5332dd0cb5122ba3dcd3ddbf0700428d4ee154231dcfdf40fe1800`).

## Gaps for the next pass

1. CAGI6 Annotate-All-Missense (doi:10.1007/s00439-025-02732-2): 60 VEPs on clinical variants deposited after a cutoff, with a gene-balanced subset. The best available independent clinical comparison.
2. Tabet et al. 2024 (doi:10.1186/s13059-024-03314-7): 24 VEPs scored on trait inference in UK Biobank and All of Us.
3. Preprints 10.64898/2026.07.16.739080 (missense predictors on activating cancer drivers; bears on somatic oncogenicity) and 10.64898/2026.08.21.746180 (gene identity in ClinVar benchmarks).
4. Livesey and Marsh 2023 and 2020, and the 2026 Nat Commun discordance paper's Supplementary Data.
5. Other ProteinGym summaries (zero-shot DMS AUC, MCC, NDCG, top recall; indel and supervised DMS; per-protein clinical AUC).
6. No independent benchmark found for the #155 non-coding predictors or PrimateAI-3D; their developer papers were not extracted.

## Validation

Validator dry-run against the store passes. On a temporary copy of the repository (not this worktree), `records -- add` (SHACL), `records -- check`, `npm run test:fast` and `npm run build` pass. In the worktree, `npm run test:fast` and `npm run typecheck` pass.

## Source hashes (SHA-256 of fetched bytes)

| Source | Retrieved (UTC) | SHA-256 |
|---|---|---|
| Livesey and Marsh 2025 XML, PMC12016141 | 13:36:01Z | `1735ee461ef192d9de67c914e9ad73d72d8aa255ea0e3479eb68cd8631d99fa2` |
| Livesey and Marsh 2025 Supplementary Material 2 | 13:36:25Z | `1b0d792d1a5d3daa95545a7973cabb131c45e42c952e7e5a447a72deef1d1e70` |
| ProteinGym DMS substitutions Spearman summary, 144fe22 | 13:39:32Z | `ee61a7c09efbfbd8d9a6c9355092c798032a578fa58c6f6256b5da8778555fd4` |
| ProteinGym clinical zero-shot substitutions AUC, 144fe22 | 13:39:33Z | `fbe453d1aaa6c30a1d0adf610f7fc23c36044a8e2548b178d316777383f8fe93` |
| ProteinGym clinical supervised substitutions AUC, 144fe22 | 13:39:33Z | `f2e38aeac2624d87e7a35a5b16bd580de62c24db36973848e1d94ac3ce510359` |
| ProteinGym clinical zero-shot indels AUC, 144fe22 | 13:39:33Z | `98a532c0e2c3d4720b73b7c05cf0dcf0419438c326761aaae3b788799f5aa836` |
| ProteinGym README, 144fe22 (matches stored) | 13:41:35Z | `321487a8de52c6cfa647a658f61150dd72e0acb0125470524fb94d1f8b23321a` |
| ProteinGym performance_DMS_benchmarks.py, 144fe22 (matches stored) | 13:41:35Z | `0002bc1b031c02dc2d67fde53da092c8fd301415645e8e83b425b4183570eba2` |
| Livesey and Marsh 2023 XML, PMC10407742 (screened) | 13:36:01Z | `c548931adfd231f2f1f3426d0423f1c89b85d8c72ed5413772a7058ca232e353` |
| Livesey and Marsh 2020 XML, PMC7336272 (screened) | 13:36:01Z | `db4522ec782b019e6e6c2d5ef3c86ad269bdf6e0ce2d264fbab4f1729ff670d0` |
| Livesey et al. 2026 XML, PMC13620131 (screened) | 13:36:02Z | `409bb57fa79b3206fe84508e87522efc1ab90270e16df53cd8d53459d5c2cdc4` |
