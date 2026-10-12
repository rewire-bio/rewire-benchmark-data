# Use-case summary drafts, 2026-10-12

Two replacement summaries, drafted for a separate reviewer. Neither summary claim has been changed. After review, each draft replaces the claim's `value`, `source_ids` and `source_locator`, followed by `records -- change` and `use-cases:repin -- <review> <claim-id>`.

Every number in a draft is listed in its table with the stored result it comes from. A check script (scratch, not committed) confirmed that each listed result is `source_checked`, belongs to an evaluation of an active judgement on the use case, and has a stored value that rounds to the number as written. Drafted by a Claude agent; no human review.

## (a) `use-case-summary-mass-spectrum-molecule-shortlisting`

**Why it needs replacing.** The two MassSpecGym in the Wild judgements are now active (`docs/reviews/use-cases/mass-spectrum-molecule-shortlisting-2026-10-12.md`). The summary pins the reviewed evaluations of every reviewed judgement on the use case, so `deriveUseCaseInputs` no longer publishes it. Its last sentence, "all of them come from two versions of one arXiv preprint", is also no longer true.

**What changes.** The MSAlign sentences are the reviewed 2026-10-10 text with two edits: the opening now introduces two preprints, and "every split recorded" becomes "every split the paper reports", because MSAlign is not measured in MassSpecGym in the Wild. The MassSpecGym in the Wild part and the closing sentence are new.

### Proposed text

> Two preprints report formula-free retrieval of the true structure from mass-matched PubChem candidates for MassSpecGym spectra, and their values are not directly comparable. In the MSAlign preprint, MSAlign ranks first among the formula-free methods on every split the paper reports, but its top-1 recall falls from about half on the formula split to under a fifth on the MCES split. On the MassSpecGym formula split, Recall@1 was 47.5 for MSAlign and 58.2 with score fusion, against 42.7 for Emb-Cos, 13.9 for JESTR and 4.7 for DeepSet, with standard deviations of 0.5 to 3.4 over three random splitting seeds. On the MCES split the order is the same but the values are much lower: 19.0, 30.8, 12.6, 7.9 and 1.9; the table caption describes three splits there too, but the methods describe two swapped variants. Recall@20 reaches 87.0 for MSAlign and 92.8 with score fusion on the formula split, and 64.9 and 82.0 on MCES. An earlier version of the same paper reports Recall@1 of 53.8 for MSAlign and 41.2 for Emb-Cos on the formula split, so the two versions differ and are not independent measurements. These MSAlign values assume the true structure is among 256 mass-matched candidates and were scored by the authors of the leading method. MassSpecGym in the Wild, whose authors include the developers of MIST, MIST-CF and MassSpecGym, reports two valid formula-free configurations on the MassSpecGym test fold, with up to 256 mass-matched candidates per spectrum. MIST given the top formula predicted by MIST-CF found the true structure at rank 1 for 26.64 percent of test spectra and within the top 20 for 54.90 percent, against 0.43 and 7.99 percent for random ranking. Its candidate pool and split differ from MSAlign's, and the MIST score depends on the formula annotator as well as the retriever. All of these values are reported by the authors of preprints, and none measures open-world identification, because the true structure is always among the candidates.

### source_ids

- `evidence-official-760ab2fa8c396aeb796c` (MSAlign v1, arXiv:2605.19752v1)
- `uc20260930-source-msalign-v2` (MSAlign v2, arXiv:2605.19752v2)
- `lit-otheromics-20261011-msgwild-source-liu2026` (MassSpecGym in the Wild, arXiv:2606.19624v1)

All three are `source_checked` with no evidence concerns.

Proposed `source_locator`: "uc20260930-source-msalign-v2: Table 3 p7, massspecgym-formula and massspecgym-mces blocks, R@1 and R@20 rows; evidence-official-760ab2fa8c396aeb796c: Table 3, MassSpecGym formula split, R@1 row; lit-otheromics-20261011-msgwild-source-liu2026: Table 2, rows 'Random' and 'MIST (MIST-CF top-1 formula)', columns 'Hit rate@1' and 'Hit rate@20'"

### Numbers and their results

| Number | Meaning | Result ID |
| --- | --- | --- |
| 47.5 | MSAlign, formula split, R@1 (v2) | `uc20260930-msalign-v2-result-massspecgym-formula-formula-free-msalign-r1` |
| 58.2 | MSAlign score fusion, formula split, R@1 (v2) | `uc20260930-msalign-v2-result-massspecgym-formula-formula-free-msalign-score-fusion-overbar-r1` |
| 42.7 | Emb-Cos, formula split, R@1 (v2) | `uc20260930-msalign-v2-result-massspecgym-formula-formula-free-emb-cos-r1` |
| 13.9 | JESTR, formula split, R@1 (v2) | `uc20260930-msalign-v2-result-massspecgym-formula-formula-free-jestr-r1` |
| 4.7 | DeepSet, formula split, R@1 (v2) | `uc20260930-msalign-v2-result-massspecgym-formula-formula-free-deepset-r1` |
| 0.5 | lowest SD of the five, formula split, R@1 (JESTR, 13.9 ± 0.5) | `uc20260930-msalign-v2-result-massspecgym-formula-formula-free-jestr-r1` |
| 3.4 | highest SD of the five, formula split, R@1 (MSAlign, 47.5 ± 3.4) | `uc20260930-msalign-v2-result-massspecgym-formula-formula-free-msalign-r1` |
| 19.0 | MSAlign, MCES split, R@1 (v2) | `uc20260930-msalign-v2-result-massspecgym-mces-formula-free-msalign-r1` |
| 30.8 | MSAlign score fusion, MCES split, R@1 (v2) | `uc20260930-msalign-v2-result-massspecgym-mces-formula-free-msalign-score-fusion-overbar-r1` |
| 12.6 | Emb-Cos, MCES split, R@1 (v2) | `uc20260930-msalign-v2-result-massspecgym-mces-formula-free-emb-cos-r1` |
| 7.9 | JESTR, MCES split, R@1 (v2) | `uc20260930-msalign-v2-result-massspecgym-mces-formula-free-jestr-r1` |
| 1.9 | DeepSet, MCES split, R@1 (v2) | `uc20260930-msalign-v2-result-massspecgym-mces-formula-free-deepset-r1` |
| 87.0 | MSAlign, formula split, R@20 (v2) | `uc20260930-msalign-v2-result-massspecgym-formula-formula-free-msalign-r20` |
| 92.8 | MSAlign score fusion, formula split, R@20 (v2) | `uc20260930-msalign-v2-result-massspecgym-formula-formula-free-msalign-score-fusion-overbar-r20` |
| 64.9 | MSAlign, MCES split, R@20 (v2) | `uc20260930-msalign-v2-result-massspecgym-mces-formula-free-msalign-r20` |
| 82.0 | MSAlign score fusion, MCES split, R@20 (v2) | `uc20260930-msalign-v2-result-massspecgym-mces-formula-free-msalign-score-fusion-overbar-r20` |
| 53.8 | MSAlign, formula split, R@1 (v1) | `msalign-2026-table3-result-msalign-massspecgym-formula-split-no-formula-r-1-recall-at-1` |
| 41.2 | Emb-Cos, formula split, R@1 (v1) | `msalign-2026-table3-result-emb-cos-massspecgym-formula-split-no-formula-r-1-recall-at-1` |
| 26.64 | MIST with MIST-CF top-1 formula, Hit rate@1 | `lit-otheromics-20261011-msgwild-result-mist-retrieval-with-mist-cf-top-1-predicted-formula-mass-retrieval-hit-rate-1` |
| 54.90 | MIST with MIST-CF top-1 formula, Hit rate@20 | `lit-otheromics-20261011-msgwild-result-mist-retrieval-with-mist-cf-top-1-predicted-formula-mass-retrieval-hit-rate-20` |
| 0.43 | Random ranking, Hit rate@1 | `lit-otheromics-20261011-msgwild-result-random-ranking-mass-retrieval-hit-rate-1` |
| 7.99 | Random ranking, Hit rate@20 | `lit-otheromics-20261011-msgwild-result-random-ranking-mass-retrieval-hit-rate-20` |

Other statements and where they come from:

- "About half" and "under a fifth": 47.5 and 19.0 above. "Ranks first on every split the paper reports" also holds on the v2 Spectraverse block (score fusion 41.3, MSAlign 31.8, Emb-Cos 26.6 at R@1).
- Three random splitting seeds, the MCES caption discrepancy, 256 candidates, scored by the leading method's authors: the reviewed 2026-10-10 summary and the use case's evidence gaps.
- MassSpecGym test fold with up to 256 mass-matched PubChem candidates per spectrum: dataset record `lit-otheromics-20261011-msgwild-data-mass-retrieval`.
- Two valid formula-free configurations, pool and split differ, dependence on the formula annotator, author overlap: the M8 rationale and limitations on both msgwild judgements.
- Origin: every result on the active judgements is `author_reported`, except MSAlign v1's comparator rows, which are `independent_paper` in the store but were scored by the MSAlign authors. "Reported by the authors of preprints" holds for both.

## (b) `use-case-summary-genetic-perturbation-response`

**Why it is withheld.** `deriveUseCaseInputs` publishes no summary for this use case. The claim is `source_checked` and both its sources are clean, but its pins no longer match. A summary pins the reviewed evaluations and results of every reviewed judgement on its use case. This one was pinned on 2026-10-09 with 437 pins; the current set has 1,071. All 634 differences are records added since then. None of the pinned records changed.

| Batch | Evaluations | Results |
| --- | --- | --- |
| `lit-cells-networks-20261011-perturbench-v4` | 28 | 178 |
| `lit-cells-networks-20261011-sun2026de` | 85 | 170 |
| `lit-cells-networks-20261011-chen2026` | 12 | 72 |
| `perturbation-ahlmann-20261011` | 30 | 59 |

The pin set includes the evaluations of reviewed judgements that are themselves withheld (chen2026, sun2026de and the three Ahlmann-Eltze single-perturbation judgements). `reviewedSummary` in `shared/omics/use-cases.ts` collects every `source_checked` judgement, not only active ones.

The current text covers only Csendes et al. 2025 in detail and names the GEARS and PertEval-scFM comparisons only to say they are separate.

**What changes.** The draft covers all ten active judgements: GEARS Supplementary Table 6 (two), PertEval-scFM, PerturBench v4 (Norman19, Frangieh21, Jiang24), Ahlmann-Eltze et al. 2025 (Norman doubles) and Csendes et al. 2025 (four datasets, in one passage). The five withheld judgements are not described. The Csendes passage keeps the reviewed numbers and caveats in shorter form; the random forest values are dropped.

### Proposed text

> Five sources on this page score how well models predict expression changes after genetic perturbations they were not trained on. Each uses its own split, gene set and metric, so their values are not pooled. Ahlmann-Eltze et al. 2025, who did not develop the deep models and ran them all themselves, scored held-out two-gene CRISPRa perturbations in K562 cells (Norman), training on every single-gene perturbation and half of the pairs. A baseline that adds the two single-gene effects had a mean L2 distance of 2.766 and a Pearson delta of 0.892 over the 1,000 most highly expressed genes, against 3.478 and 0.773 for Geneformer with a linear decoder, 4.096 and 0.631 for GEARS, 4.279 and 0.610 for both UCE and scBERT, 4.616 and 0.527 for scGPT, 4.722 and 0.537 for scFoundation, and 12.205 and 0.146 for CPA; predicting no change gave an L2 distance of 5.616. Rewire computed these means from the authors' Source Data, no spread is stated, and the UCE and scBERT runs used ground-truth expression of the perturbed genes. In PerturBench v4, a preprint whose authors trained every model and built the Linear, Latent Additive and Decoder baselines, the cosine similarity of predicted log fold change on held-out Norman pairs ranged from 0.41 for Biolord and 0.44 for GEARS to 0.79 for the Latent Additive baseline, with CPA at 0.76 and the Linear baseline at 0.60, each a mean over five training seeds. When effects were transferred to melanoma co-culture (Frangieh21) every model scored between 0.01 and 0.22 and every printed DEG recall was 0.000; on held-out cell line and cytokine states (Jiang24) scores ranged from 0.17 for Linear to 0.64 for the Decoder baseline, and the paper describes the held-out states in two different ways. In Csendes et al. 2025, whose authors are employees of Turbine Ltd. and built the baselines themselves, predicting the mean training response gave a higher Pearson delta than scGPT and scFoundation, as re-run by the same authors, on all four Perturb-seq datasets: 0.711, 0.557, 0.373 and 0.628 for Adamson, Norman, Replogle K562 and Replogle RPE1, against 0.641, 0.554, 0.327 and 0.596 for scGPT and 0.552, 0.459, 0.269 and 0.471 for scFoundation. Each dataset there has one split and one run per model with no spread printed, so small gaps such as 0.557 against 0.554 cannot be tested. The GEARS developers report a mean squared error of 0.216 for GEARS on Norman, against 0.354 for CPA and 0.551 for a no-change control, with spreads of unstated type. PertEval-scFM, whose authors trained GEARS from scratch, reports an area under its distribution-shift curve of 0.815 for GEARS against 4.484 for an MLP and 4.612 for a mean baseline, lower being better. All of these scores measure agreement with observed expression in held-out perturbations; they do not show which experiments will succeed.

### source_ids

- `perturbation-ahlmann-20261011-source-article`
- `perturbation-ahlmann-20261011-source-data-fig1`
- `perturbation-ahlmann-20261011-source-data-ed-fig2`
- `lit-cells-networks-20261011-perturbench-v4-source-wu2025`
- `perturbation-response-20261009-source-csendes2025`
- `perturbation-response-20261009-source-csendes2025-supp`
- `coverage-source-gears-supp`
- `perteval-scfm-2025-source`

All eight are `source_checked` with no evidence concerns. `perturbation-ahlmann-20261011-source-data-fig2` has evidence concerns and is not cited; the draft uses no Fig. 2 value.

Proposed `source_locator`: "perturbation-ahlmann-20261011-source-data-fig1: sheet 'Panel A', Norman, column l2; perturbation-ahlmann-20261011-source-data-ed-fig2: sheet 'Panel A', Norman, column r2_delta; lit-cells-networks-20261011-perturbench-v4-source-wu2025: Tables 3, 4 and 7, columns 'Cosine logFC' and 'DEG recall'; perturbation-response-20261009-source-csendes2025-supp: Supplementary Tables 1 and 2; coverage-source-gears-supp: Table 6, MSE; perteval-scfm-2025-source: Table 1, Norman single-gene AUSPC"

### Numbers and their results

| Number | Meaning | Result ID |
| --- | --- | --- |
| 2.766 | additive baseline, Norman doubles, mean L2 | `perturbation-ahlmann-20261011-result-fig1a-norman-additive` |
| 0.892 | additive baseline, Pearson delta | `perturbation-ahlmann-20261011-result-ed2a-norman-additive` |
| 3.478 | Geneformer, L2 | `perturbation-ahlmann-20261011-result-fig1a-norman-geneformer` |
| 0.773 | Geneformer, Pearson delta | `perturbation-ahlmann-20261011-result-ed2a-norman-geneformer` |
| 4.096 | GEARS, L2 | `perturbation-ahlmann-20261011-result-fig1a-norman-gears` |
| 0.631 | GEARS, Pearson delta | `perturbation-ahlmann-20261011-result-ed2a-norman-gears` |
| 4.279 | UCE, L2 | `perturbation-ahlmann-20261011-result-fig1a-norman-uce` |
| 4.279 | scBERT, L2 | `perturbation-ahlmann-20261011-result-fig1a-norman-scbert` |
| 0.610 | UCE, Pearson delta | `perturbation-ahlmann-20261011-result-ed2a-norman-uce` |
| 0.610 | scBERT, Pearson delta | `perturbation-ahlmann-20261011-result-ed2a-norman-scbert` |
| 4.616 | scGPT, L2 | `perturbation-ahlmann-20261011-result-fig1a-norman-scgpt` |
| 0.527 | scGPT, Pearson delta | `perturbation-ahlmann-20261011-result-ed2a-norman-scgpt` |
| 4.722 | scFoundation, L2 | `perturbation-ahlmann-20261011-result-fig1a-norman-scfoundation` |
| 0.537 | scFoundation, Pearson delta | `perturbation-ahlmann-20261011-result-ed2a-norman-scfoundation` |
| 12.205 | CPA, L2 | `perturbation-ahlmann-20261011-result-fig1a-norman-cpa` |
| 0.146 | CPA, Pearson delta | `perturbation-ahlmann-20261011-result-ed2a-norman-cpa` |
| 5.616 | no change baseline, L2 | `perturbation-ahlmann-20261011-result-fig1a-norman-no-change` |
| 0.41 | Biolord, Norman19 cosine logFC | `lit-cells-networks-20261011-perturbench-v4-result-norman19-biolord-cosine-logfc-t3` |
| 0.44 | GEARS, Norman19 cosine logFC | `lit-cells-networks-20261011-perturbench-v4-result-norman19-gears-cosine-logfc-t3` |
| 0.79 | Latent Additive, Norman19 cosine logFC | `lit-cells-networks-20261011-perturbench-v4-result-norman19-la-cosine-logfc-t3` |
| 0.76 | CPA, Norman19 cosine logFC | `lit-cells-networks-20261011-perturbench-v4-result-norman19-cpa-cosine-logfc-t3` |
| 0.60 | Linear, Norman19 cosine logFC | `lit-cells-networks-20261011-perturbench-v4-result-norman19-linear-cosine-logfc-t3` |
| 0.01 | Linear, Frangieh21 cosine logFC (lowest) | `lit-cells-networks-20261011-perturbench-v4-result-frangieh21-linear-cosine-logfc-t7` |
| 0.22 | SAMS-VAE (S), Frangieh21 cosine logFC (highest) | `lit-cells-networks-20261011-perturbench-v4-result-frangieh21-sams-vae-s-cosine-logfc-t7` |
| 0.000 | Frangieh21 DEG recall, Biolord | `lit-cells-networks-20261011-perturbench-v4-result-frangieh21-biolord-deg-recall-t7` |
| 0.000 | Frangieh21 DEG recall, CPA | `lit-cells-networks-20261011-perturbench-v4-result-frangieh21-cpa-deg-recall-t7` |
| 0.000 | Frangieh21 DEG recall, CPA (noAdv) | `lit-cells-networks-20261011-perturbench-v4-result-frangieh21-cpa-noadv-deg-recall-t7` |
| 0.000 | Frangieh21 DEG recall, Latent Additive | `lit-cells-networks-20261011-perturbench-v4-result-frangieh21-la-deg-recall-t7` |
| 0.000 | Frangieh21 DEG recall, Linear | `lit-cells-networks-20261011-perturbench-v4-result-frangieh21-linear-deg-recall-t7` |
| 0.000 | Frangieh21 DEG recall, SAMS-VAE | `lit-cells-networks-20261011-perturbench-v4-result-frangieh21-sams-vae-deg-recall-t7` |
| 0.000 | Frangieh21 DEG recall, SAMS-VAE (S) | `lit-cells-networks-20261011-perturbench-v4-result-frangieh21-sams-vae-s-deg-recall-t7` |
| 0.17 | Linear, Jiang24 cosine logFC (lowest) | `lit-cells-networks-20261011-perturbench-v4-result-jiang24-linear-cosine-logfc-t4` |
| 0.64 | Decoder, Jiang24 cosine logFC (highest) | `lit-cells-networks-20261011-perturbench-v4-result-jiang24-decoder-cosine-logfc-t4` |
| 0.711 | mean training response, Adamson, Pearson delta | `perturbation-response-20261009-result-csendes2025-adamson-mean-pearson-delta` |
| 0.557 | mean training response, Norman | `perturbation-response-20261009-result-csendes2025-norman-mean-pearson-delta` |
| 0.373 | mean training response, Replogle K562 | `perturbation-response-20261009-result-csendes2025-replogle-k562-mean-pearson-delta` |
| 0.628 | mean training response, Replogle RPE1 | `perturbation-response-20261009-result-csendes2025-replogle-rpe1-mean-pearson-delta` |
| 0.641 | scGPT, Adamson | `perturbation-response-20261009-result-csendes2025-adamson-scgpt-pearson-delta` |
| 0.554 | scGPT, Norman | `perturbation-response-20261009-result-csendes2025-norman-scgpt-pearson-delta` |
| 0.327 | scGPT, Replogle K562 | `perturbation-response-20261009-result-csendes2025-replogle-k562-scgpt-pearson-delta` |
| 0.596 | scGPT, Replogle RPE1 | `perturbation-response-20261009-result-csendes2025-replogle-rpe1-scgpt-pearson-delta` |
| 0.552 | scFoundation, Adamson | `perturbation-response-20261009-result-csendes2025-adamson-scfoundation-pearson-delta` |
| 0.459 | scFoundation, Norman | `perturbation-response-20261009-result-csendes2025-norman-scfoundation-pearson-delta` |
| 0.269 | scFoundation, Replogle K562 | `perturbation-response-20261009-result-csendes2025-replogle-k562-scfoundation-pearson-delta` |
| 0.471 | scFoundation, Replogle RPE1 | `perturbation-response-20261009-result-csendes2025-replogle-rpe1-scfoundation-pearson-delta` |
| 0.216 | GEARS, Table 6 MSE | `gears-2023-supp-table6-result-gears-mse-mse` |
| 0.354 | CPA, Table 6 MSE | `gears-2023-supp-table6-result-cpa-mse-mse` |
| 0.551 | no perturbation, Table 6 MSE | `gears-2023-supp-table6-result-no-perturb-mse-mse` |
| 0.815 | GEARS, PertEval-scFM AUSPC | `perteval-scfm-2025-result-gears-auspc` |
| 4.484 | MLP baseline, AUSPC | `perteval-scfm-2025-result-mlp-baseline-auspc` |
| 4.612 | mean baseline, AUSPC | `perteval-scfm-2025-result-mean-baseline-auspc` |

The ranges ("from 0.41 ... to 0.79", "between 0.01 and 0.22", "from 0.17 ... to 0.64") were checked against every printed cosine logFC result of the active evaluations on that protocol, not only the cited rows. "Every printed DEG recall was 0.000" covers all seven printed Frangieh21 rows; three rows print no DEG recall. "1,000 most highly expressed genes" is the judgement's endpoint, not a result value.

Other statements and where they come from:

- Ahlmann-Eltze: authors ran every model and did not develop the deep models; training on every single and half the doubles; 1,000 genes; computed by Rewire from Source Data; no spread; UCE and scBERT ground-truth embedding: the Norman judgement's endpoint, rationale and limitations, and each result's `derivation`. Origins: `author_reported` for the additive and no-change baselines, `independent_paper` for the deep models.
- PerturBench v4: preprint; authors trained every model and built the Linear, Latent Additive and Decoder baselines; five training seeds; the two held-out state descriptions: the three PerturBench judgements' limitations. Origins: `author_reported` for the authors' own baselines, `independent_paper` for CPA, SAMS-VAE, Biolord and GEARS.
- Csendes: Turbine authors, one split and one run per model, no spread, the 0.557 against 0.554 caveat: the reviewed 2026-10-09 summary. Baselines `author_reported`, scGPT and scFoundation `independent_paper`.
- GEARS Table 6: developer-reported (`author_reported`); "spreads of unstated type" is the judgement limitation "Reported spreads have unspecified type".
- PertEval-scFM: GEARS trained from scratch by the paper's authors; lower AUSPC is better: the judgement's endpoint and limitations.

## Notes for the reviewer

1. The Ahlmann-Eltze UCE and scBERT means are identical on both metrics (4.279 and 0.610). The batch review (`docs/reviews/use-cases/genetic-perturbation-response-2026-10-11.md`, Fig. 1a and ED Fig. 2a rows) recomputed both and found them as stored. The draft reports them as stored. Whether the Source Data rows for the two methods are distinct is worth checking.
2. Re-pinning summary (b) also pins the evaluations of the five withheld judgements. A later fix to any of those will withhold the summary again.
3. Re-pinning summary (a) fixes the four msgwild evaluations into its pins.
4. The `description` of both summary claims still says "Draft until reviewed." It is unchanged.
