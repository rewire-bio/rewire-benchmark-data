# Variant effect predictor use cases: bounded literature pass, 2026-10-14

Second pass on variant effect predictors (VEPs), after [variant-effect-predictors-2026-10-14.md](variant-effect-predictors-2026-10-14.md) (PR #160). It covers:

- [rewire-benchmark-data #151](https://github.com/rewire-bio/rewire-benchmark-data/issues/151): a new use case for classifying missense variants in any gene with calibrated computational evidence (ACMG/AMP PP3/BP4);
- [#152](https://github.com/rewire-bio/rewire-benchmark-data/issues/152): a new use case for predicting missense variant effects in a protein of interest;
- the predictors in [#153](https://github.com/rewire-bio/rewire-benchmark-data/issues/153), [#154](https://github.com/rewire-bio/rewire-benchmark-data/issues/154) and [#155](https://github.com/rewire-bio/rewire-benchmark-data/issues/155) that had no record after PR #160;
- the `evidence_checked` update for the seven use cases searched in PR #160.

Starting commit 9beb63e (branch `claude/vep-literature-pass`, which holds the reviewed first-pass batch); this branch is `claude/vep-use-cases`. Cutoff 2026-10-14. Budget 80 queries; 21 used. No predictor or model was run, nothing was paid for or requested, and nobody was contacted. The AVE predictor list was used only to know which names to look for; no record cites it. This is an extraction awaiting independent review: no record is marked reviewed, there is no `review.json`, and the batch is not in the store.

Batch: `data/omics/vep-use-cases-20261014/` (323 records).

## Disposition in brief

1. Use case `use-case-missense-pp3-bp4-calibrated-evidence` (#151). Its core evidence is the ClinGen Sequence Variant Interpretation (SVI) calibration: Pejaver et al. 2022 (AJHG, CC BY) Table 2, score intervals for 13 predictors at four PP3 and four BP4 strengths, and Table 3, developer thresholds of SIFT, PolyPhen-2 and CADD; and Bergquist et al. 2025 (Genet Med) Table 1, points-scale intervals for BayesDel, MutPred2, REVEL, VEST4, AlphaMissense, ESM1b and VARITY_R. 173 results, every cell of the three tables. 15 relevance judgements (4 on the new protocols, 11 on existing ones) and a baseline claim (SIFT).
2. Use case `use-case-protein-variant-effect-prediction` (#152). No new extraction: 6 judgements, all direct, on the ProteinGym zero-shot DMS substitutions track at 144fe22 and the five Livesey and Marsh 2025 DMS strata. Baseline claim: the site-independent alignment model.
3. Predictors. 36 of the 40 without a record now have one, with status `discovered` and a captured primary source (19 from #153, 6 from #154, 11 from #155). EA also has results, from Pejaver et al. 2022. Four are gaps: PON-PS, EvoRator2, TransEFVP and VAMPP. Combined with PR #160, 36 of 40 (#153), 12 of 12 (#154) and 11 of 11 (#155) predictors have records; 17, 7 and 0 have results.
4. A new metric concept, `evidence-strength-score-interval`.
5. The seven first-pass use cases: a proposed `evidence_checked` of 2026-10-14 is in `evidence-checked.json`, to be applied with `records -- change` after review.

## The two new use cases

### #151: calibrated PP3/BP4 evidence for missense variants

Question: which predictor and score thresholds give calibrated ACMG/AMP computational evidence (PP3/BP4) for a missense variant in a gene without a gene-specific calibration, and at what strength? The decision is choosing one predictor in advance and its thresholds; the output is calibrated score intervals, the highest strength each predictor reaches, and the limits of the calibration. Exclusions: genes with their own expert-panel thresholds (BRCA1/BRCA2 has its own use case), non-missense variant classes, combining predictors, somatic oncogenicity and final classification.

What the evidence shows, descriptively and before review:

- In Pejaver et al. 2022, BayesDel, MutPred2, REVEL and VEST4 reach PP3_Strong; REVEL also reaches BP4_Very Strong and MutPred2 and CADD BP4_Strong. GERP++ reaches no PP3 strength and MPC no BP4 strength (Table 2).
- At their developer thresholds, SIFT (0.050), PolyPhen-2 (0.902) and CADD (20.000) do not reach PP3 Supporting: local likelihood ratios 0.048, 1.993 and 0.157 against a cut-off of 2.406. At those thresholds they call 50.4%, 29.3% and 65.1% of the gnomAD reference set pathogenic, against a 4.41% prior (Table 3).
- In Bergquist et al. 2025, AlphaMissense, ESM1b and VARITY_R reach PP3_Strong (+4) and at least BP4_Moderate; VARITY_R reaches BP4_Strong (Table 1). The developer thresholds of AlphaMissense (0.564) and ESM1b (−7.5) do not reach Supporting (Results).

The limits recorded on the protocols, judgements and use case:

- The developers of BayesDel (B.-J. Feng), MPC (A. O'Donnell-Luria), MutPred2 (V. Pejaver, K.A. Pagel, S.D. Mooney, P. Radivojac), REVEL (V. Pejaver) and VEST4 (R. Karchin) are authors of Pejaver et al. 2022, so those evaluations are `author_reported`. In Bergquist et al. 2025, MutPred2 and REVEL are `author_reported`.
- The calibration is genome-wide. Tejura et al. 2024 (AJHG) found that about 70% of gene-level REVEL and BayesDel intervals with enough control variants exceeded the incorrect predictions the genome-wide recommendations imply.
- Labels are ClinVar classifications; Stenton et al. 2024 state the assumption that computational evidence played no major role in them.

### #152: missense variant effects in a protein of interest

Question: which predictor best ranks the functional effects of amino acid substitutions in a given protein, with or without an alignment or structure? Evidence: ProteinGym's zero-shot DMS substitutions track at 144fe22 (97 models, 217 assays, with MSA-depth, function, taxon and mutational-depth breakdowns, already in the store from PR #160) and the Livesey and Marsh 2025 rankings on 36 human DMS sets. No new extraction was needed. ProteinGym's supervised DMS results are stored only as tasks from the 2023 paper, which judgements cannot target; this is recorded as a gap.

## Relevance judgements (all `needs_review`)

| Use case | Protocol | Relevance | Comparison group |
| --- | --- | --- | --- |
| #151 | `vep-uc-20261014-protocol-pejaver2022-intervals` | direct | ClinGen SVI PP3/BP4 calibrations |
| #151 | `vep-uc-20261014-protocol-bergquist2025-point-intervals` | direct | ClinGen SVI PP3/BP4 calibrations |
| #151 | `vep-uc-20261014-protocol-pejaver2022-developer-threshold-lr` | direct | ClinGen SVI PP3/BP4 calibrations |
| #151 | `vep-uc-20261014-protocol-pejaver2022-developer-threshold-gnomad-fraction` | proxy | ClinGen SVI PP3/BP4 calibrations |
| #151 | Livesey and Marsh 2025 clinical AUROC ranking | proxy | Livesey and Marsh 2025 VEP rankings |
| #151 | Livesey and Marsh 2025 DMS rankings (5 strata) | proxy | Livesey and Marsh 2025 VEP rankings |
| #151 | ProteinGym clinical substitutions, zero-shot and supervised (2) | proxy | ProteinGym clinical benchmark |
| #151 | `brca-20261009-protocol-ramadane2025-pp3-bp4` | proxy | Gene-level checks of calibrated thresholds |
| #151 | ENIGMA generic BayesDel thresholds, BRCA1 and BRCA2 (2) | proxy | Gene-level checks of calibrated thresholds |
| #152 | `rewire-proteingym-v1-3-dms-substitutions` | direct | ProteinGym zero-shot DMS substitutions |
| #152 | Livesey and Marsh 2025 DMS rankings (5 strata) | direct | Livesey and Marsh 2025 VEP rankings |

The proxy judgements for #151 say why: the rankings measure discrimination, not evidence strength at a threshold, and the BRCA studies are single-gene checks. The ProteinGym clinical zero-shot indel protocol was not mapped to #151, which is about missense variants. The limitation text reused from the reviewed first-pass judgements is unchanged.

## Predictors (#153 to #155)

`coverage.json` (`issue_predictor_coverage`) lists every predictor in the three issues with its record, source, publication year and a single access probe of its stated URL. Notes:

- DAMpred: the AVE list cites Gao, Zhou and Skolnick 2015 (Structure 23:1362), which does not describe DAMpred. The record cites Quan et al. 2019 (J Mol Biol), which does; Gao et al. is excluded in the scope audit.
- PromoterAI and LOL-EVE rest on their official repository READMEs pinned to commits (Illumina/PromoterAI ce9fcd0, debbiemarkslab/LOL-EVE deed3bd). The PromoterAI Science paper is not open access; the LOL-EVE paper was not found in Europe PMC.
- ESGMM rests on its CC BY Research Square preprint; the published Discover Computing version returned a bot challenge.
- GPN-Star rests on the Nature accelerated-preview PDF (CC BY), which hashed identically on two downloads; the article HTML did not.
- MTBAN and mutationTCN are separate records; Livesey and Marsh 2025 score mutationTCN with predictions from the MTBAN server, which the first-pass review left without results for MTBAN.
- Results from the predictors' own papers were not extracted (optional per the task). EA is the only new record with results.

Gaps, no record created:

| Predictor | Reference | Why |
| --- | --- | --- |
| PON-PS | Niroula and Vihinen 2017, Hum Mutat | No PMC copy; Wiley HTTP 403; the server path returns 404 and is not listed on the group's site. Livesey and Marsh 2025 dropped it because predictions were no longer available. |
| EvoRator2 | Nagar et al. 2023, J Mol Biol | No PMC copy; Elsevier linking page only; server did not respond. |
| TransEFVP | Yan et al. 2024, J Chem Inf Model | No PMC copy; ACS HTTP 403. A GitHub repository of that name holds only an 11-byte README and does not identify its authors. |
| VAMPP | Aydin et al. 2024, bioRxiv | Preprint only; the bioRxiv JATS route was rate limited twice (HTTP 429). Retry later. |

On #153, timini commented "please do not add anything too old or outdated or bad". All retrievable tools were recorded; the reviewer can exclude old or unavailable ones using the year and probe in `coverage.json`. The oldest are SAAPpred (2013), EA and GWAVA (2014), PaPI (2015), ENTPRISE, VIPUR and UMD-Predictor (2016) and CpGenie (2017). The single probe got no HTTP response for PaPI, DAMpred, ENTPRISE, PON-P3, MTBAN, UMD-Predictor, FINSURF and CpGenie, HTTP 500 for EA and HTTP 502 for AFFIPred.

## Search log (exact, dated)

Times are UTC request starts. Europe PMC used the REST `search` endpoint with `resultType=lite` (q01 to q04, q21) or `core` (q13 to q19).

| ID | Mode | Exact query | Time | Outcome |
| --- | --- | --- | --- | --- |
| q01 | Europe PMC | `(TITLE_ABS:"PP3" OR TITLE_ABS:"BP4") AND (TITLE_ABS:"calibration" OR TITLE_ABS:"calibrated" OR TITLE_ABS:"calibrating") AND PUB_YEAR:[2022 TO 2026]` | 14:44:25Z | 17 hits; Pejaver 2022, Bergquist 2025, Stenton 2024 captured; Genet Med 2026 calibration, BayesQuantify, INDELVAR, Dubé 2026 and the 5' cis-regulatory calibration noted |
| q02 | Europe PMC | `(TITLE_ABS:"AlphaMissense" OR TITLE_ABS:"REVEL" OR TITLE_ABS:"BayesDel" OR TITLE_ABS:"MutPred2" OR TITLE_ABS:"VEST4" OR TITLE_ABS:"CADD") AND (TITLE_ABS:"evidence strength" OR TITLE_ABS:"likelihood ratio" OR TITLE_ABS:"ClinGen") AND (TITLE_ABS:"threshold" OR TITLE_ABS:"thresholds" OR TITLE_ABS:"calibration") AND PUB_YEAR:[2023 TO 2026]` | 14:44:35Z | 21 hits; Tejura 2024 captured; P-KNN and gene-specific studies noted |
| q03 | Europe PMC | title search for the #153 papers (full string in ledger `search-vep-uc-20261014-q03`) | 14:47:32Z | 330 hits, mostly unrelated; #153 primary papers located |
| q04 | Europe PMC | title search for the #154 and #155 papers (full string in ledger q04) | 14:47:44Z | 40 hits; primary papers located |
| q05 | Open-access lookup | doi:10.1016/j.gim.2026.102606 | 14:49:27Z | Closed access; gap |
| q06-q12 | GitHub repository search | PromoterAI; LOL-EVE; VAMPP; TransEFVP; EvoRator2; ESGMM; GPN-Star | 14:49:41Z | Official PromoterAI and LOL-EVE repositories; nothing usable for the others |
| q13-q19 | Europe PMC | `DOI:"…"` for VAMPP, ESGMM, EvoRator2, PON-PS, TransEFVP, GPN-Star, PromoterAI | 14:49:56Z | No PMC full text for any; ESGMM preprint CC BY |
| q20 | Crossref | bibliographic query for the ESGMM title | 14:50:08Z | Published version doi:10.1007/s10791-024-09487-w found; not retrievable |
| q21 | Europe PMC | `TITLE:"DAMpred" OR (TITLE:"VAMPP-Score") OR (TITLE:"EvoRator")` | 14:52:02Z | DAMpred primary paper (Quan et al. 2019) found |

Retrievals are listed step by step in the batch's `retrieval-log.md`.

## Use cases from the first pass: `evidence_checked`

The seven use cases searched in PR #160 (BRCA1/BRCA2 germline interpretation, rare-disease candidate ranking, unresolved rare-disease reanalysis, somatic small-variant oncogenicity, protein stability, splicing follow-up, regulatory variant and gene follow-up) still show `evidence_checked` 2026-10-09. `evidence-checked.json` proposes date and cutoff 2026-10-14 with the first-pass dossier, its review, this dossier and the search ledger as records. It changes existing records, so it needs `npm run records -- change` with the reviewer's dated review; the collector did not apply it. On a temporary copy of the repository it applies cleanly (see Validation). The two new use cases carry `evidence_checked` 2026-10-14 in the batch.

Two leads bear on first-pass use cases and were not mapped: the Pejaver and Bergquist thresholds are a proxy for BRCA1/BRCA2 interpretation (the BRCA use case already cites generic Pejaver BayesDel thresholds through ENIGMA), and the regional 5' cis-regulatory calibration (AJHG 2024, PMC11267523) bears on regulatory variant follow-up.

## Open questions for the reviewer

1. Accept the result encoding for calibrated intervals (printed interval, `numeric_value` as the bound a score must reach) and the new metric concept, or prefer `numeric_value` null for two-sided intervals.
2. Origin of the BayesDel and VEST4 rows in Bergquist et al. 2025, whose thresholds are carried over from a paper their developers co-wrote (`independent_paper` as recorded, or `author_reported`).
3. Whether the gnomAD over-calling protocol should be mapped at all (recorded as proxy).
4. Whether to drop old or unreachable predictors in response to the #153 comment.
5. Whether PMC pages hashed after blanking two per-request tokens are acceptable source artifacts, or whether these papers should wait for a stable artifact.
6. `docs/use-cases.md` says "There are 26" use cases; after this batch there would be 28. Not changed here, because the batch is not in the store.

## Validation

In this worktree, with the batch not in the store: `npm run typecheck` passes and `npm run test:fast` passes (42 files, 370 tests). `build_batch.py` run twice gives the same `batch.jsonl` (SHA-256 `d6fa3f4eed1c722bcb61c83b35b2f9433040698d232bb496bdb199a0dad6c85a`).

On a temporary copy of the repository, deleted afterwards: `records -- add` of the batch passes the attribute checks and SHACL shapes (323 records added); applying `evidence-checked.json` to the seven use cases with `records -- change` passes the shapes; `records -- check` reports 77,050 records matching their provenance; `npm run build` exits 0. In the built `use-cases.json` the two new use cases carry `evidence_checked` 2026-10-14 and all 21 judgements are drafts, as expected before review. Built as drafts, the new use cases are listed in the artifact with no active evidence, so the batch should enter the store only after review.

## Source hashes

Every source record with its URL, version, retrieval time and SHA-256 is listed in the batch's `sources.md`. The calibration sources:

| Source | SHA-256 |
| --- | --- |
| Pejaver et al. 2022 XML, PMC9748256 | `a78c7bcaacb0ccb72291264bbe7c1f9a16867b0c6207dcbb45c3c59a14af6b3b` |
| Bergquist et al. 2025, PMC12208618 page (normalised) | `4fe954451167b5a5717a4c37f4054432e1f02fb59862d0fb909edb525e6bb8e2` |
| Stenton et al. 2024, PMC11560577 page (normalised) | `debe1ae8e304ac0a6272c093bcf7874977e7b9b3921dbe7f5ba096701611ebe7` |
| Tejura et al. 2024, PMC11393694 page (normalised) | `e00fb418efba3924e47db1aba3be26835dbdbb9f0a4c14aca06a61215ca16ecf` |
