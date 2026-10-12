# Use-case summaries: mass-spectrum shortlisting and genetic perturbation response, 2026-10-12

Claims:

- `use-case-summary-mass-spectrum-molecule-shortlisting`
- `use-case-summary-genetic-perturbation-response`

Drafts: `data/omics/use-case-followups-20261012/summary-drafts.md`. Reviewer: a separate Claude review agent that did not write the drafts. No human review is claimed.

Both drafts hold after the corrections below. Each claim's `value`, `source_ids` and `source_locator` now carry the corrected text, its review block names this review, and both claims are re-pinned.

## Method

- Rebuilt the use-case artifact with `deriveUseCaseInputs` and listed the active judgements on each use case with their derived evaluations.
- For every number in each draft, read the stored result, its evaluation and the judgement that lists it. Each number equals the stored `printed_value`, rounded where the draft says so; each result and evaluation is `source_checked`; each evaluation belongs to an active judgement on the use case.
- Checked every range, ranking and "every" statement against all results of the active evaluations on that protocol, not only the cited rows.
- Checked origins, publication status, truth-set and leakage limits against the judgement, protocol, dataset and source records.
- Checked that every cited source is `source_checked` with no `evidence_concerns`, that neither text uses a withheld judgement, that neither recommends, and that neither has an em or en dash.

## (a) Mass-spectrum molecule shortlisting

Active judgements: the four MSAlign v1 judgements (`use-case-mapping-msms-*`), the three MSAlign v2 judgements (`use-case-mapping-20260930-335-*`), and the two MassSpecGym in the Wild judgements activated on this branch.

| Number | Stored result | Outcome |
| --- | --- | --- |
| 47.5, 58.2, 42.7, 13.9, 4.7 | v2 formula split R@1 (MSAlign, score fusion, Emb-Cos, JESTR, DeepSet) | Match |
| 0.5 to 3.4 | SDs of those five rows: 3.4, 3.4, 3.0, 0.5, 0.6 | Match |
| 19.0, 30.8, 12.6, 7.9, 1.9 | v2 MCES split R@1, same order | Match; ranking order identical to the formula split |
| 87.0, 92.8 / 64.9, 82.0 | v2 R@20, MSAlign and score fusion, formula / MCES | Match |
| 53.8, 41.2 | v1 formula split R@1, MSAlign and Emb-Cos | Match |
| 26.64, 54.90 | MSGWild, MIST with MIST-CF top-1 formula, Hit rate@1 and @20 | Match (percent) |
| 0.43, 7.99 | MSGWild, random ranking, Hit rate@1 and @20 | Match (percent) |

"Ranks first among the formula-free methods on every split the paper reports" holds for MSAlign (excluding its own score-fusion variant) on all three v2 blocks and all four v1 no-formula blocks, NPLIB1 included, at R@1 and R@20. The 256-candidate pool, PubChem candidates and the MCES caption discrepancy come from the v2 dataset and protocol records.

Corrections:

1. "reports two valid formula-free configurations on the MassSpecGym test fold, with up to 256 mass-matched candidates per spectrum." became "reports two formula-free configurations that it does not flag for formula leakage, on the MassSpecGym test fold with up to 256 mass-matched candidates per spectrum." The source's main finding is formula leakage in other rows, which the judgements exclude; "valid" did not say so.
2. "were scored by the authors of the leading method" became "were scored by the MSAlign authors". With a second preprint in the text, "the leading method" was ambiguous.
3. `source_locator`: restored the v2 Spectraverse block, and widened the v1 entry to the no-formula blocks, because "every split the paper reports" rests on them. Added Section 4.3 of MassSpecGym in the Wild, which states that the predicted formula does not filter candidates.

## (b) Genetic perturbation response

Active judgements: GEARS Supplementary Table 6 (MSE and Pearson delta), PertEval-scFM, PerturBench v4 (Norman19, Frangieh21, Jiang24), Ahlmann-Eltze et al. 2025 Norman doubles, and Csendes et al. 2025 (four datasets). That is eleven, not ten as the drafts file says; the GEARS Pearson delta judgement is not described in the text, which is acceptable.

| Number | Stored result | Outcome |
| --- | --- | --- |
| 2.766 / 0.892 | Ahlmann-Eltze additive baseline, L2 / Pearson delta | Match |
| 3.478 / 0.773, 4.096 / 0.631, 4.616 / 0.527, 4.722 / 0.537, 12.205 / 0.146 | Geneformer, GEARS, scGPT, scFoundation, CPA | Match |
| 4.279 / 0.610 | UCE and scBERT | Match for both; see below |
| 5.616 | no change, L2 (its Pearson delta is undefined) | Match |
| 0.41, 0.44, 0.79, 0.76, 0.60 | PerturBench Norman19 cosine logFC (Biolord, GEARS, Latent Additive, CPA, Linear) | Match; 0.41 and 0.79 are the minimum and maximum of all eleven rows |
| 0.01 to 0.22 | Frangieh21 cosine logFC, all ten rows | Match (Linear 0.01, SAMS-VAE (S) 0.22) |
| 0.000 | Frangieh21 DEG recall, all seven printed rows | Match |
| 0.17 to 0.64 | Jiang24 cosine logFC, all seven rows | Match (Linear 0.17, Decoder 0.64) |
| 0.711, 0.557, 0.373, 0.628 | Csendes Train Mean, Pearson delta | Match (rounded from 0.711148, 0.557266, 0.372996, 0.628385) |
| 0.641, 0.554, 0.327, 0.596 | Csendes scGPT | Match (rounded) |
| 0.552, 0.459, 0.269, 0.471 | Csendes scFoundation | Match (rounded) |
| 0.216, 0.354, 0.551 | GEARS Table 6 MSE (GEARS, CPA, no perturbation) | Match; spreads `unresolved_spread` |
| 0.815, 4.484, 4.612 | PertEval-scFM AUSPC (GEARS, MLP, mean); direction lower | Match |

Author-reported and truth-set limits named in the text: Ahlmann-Eltze ran all models and did not develop the deep models; PerturBench is a preprint whose authors trained every model and built three baselines; Csendes authors are Turbine employees who built the baselines; the GEARS values are developer-reported; PertEval trained GEARS itself; all scores are agreement with observed expression on held-out perturbations, not experimental success.

Corrections:

1. "Five sources on this page score" became "The five sources whose comparisons are shown on this page score". The page also lists the withheld chen2026, sun2026de and Ahlmann-Eltze single-perturbation judgements as held for review, so "five sources on this page" was not true.
2. "used ground-truth expression of the perturbed genes." became "used ground-truth expression of the perturbed genes, a possible test leakage." This is the judgement's own limitation; the draft described the input but not why it matters.
3. `source_locator`: added the Ahlmann-Eltze article (Fig. 1 and Extended Data Fig. 2 legends; Methods) and the Csendes main text (Results; Methods; Competing interests). Both are in `source_ids` and support statements in the text.

### UCE and scBERT

The identical means are real, not a derivation error. Re-downloaded Source Data Fig. 1 (MOESM3, SHA-256 `c9bd4d68...b75081`) and Extended Data Fig. 2 (MOESM6, `1f05ffc4...24b3`); both match the source records. A separate reader written for this review found 310 rows for each method (`norman_from_scfoundation`, train test or val, seeds 1 to 5). The rows match one to one by seed, split and perturbation, and none of the 310 pairs has identical values; they differ from about the fourth decimal (for example AHR+FEV, seed 1: L2 6.79355 for UCE and 6.79340 for scBERT). The exact means are:

| Method | L2 | Pearson delta |
| --- | --- | --- |
| UCE | 4.27936 | 0.61012 |
| scBERT | 4.27926 | 0.61006 |

Both round to 4.279 and 0.610. The text's "4.279 and 0.610 for both UCE and scBERT" is correct.

### Pins and withheld judgements

`claimPins` and `reviewedSummary` (`shared/omics/use-cases.ts`) pin the reviewed evaluations of every `source_checked` judgement on the use case, active or withheld. The re-pinned summary therefore also pins the evaluations of the eight reviewed but withheld judgements: chen2026 (three), sun2026de (two) and the three Ahlmann-Eltze single-perturbation judgements. The text uses none of them: no number or statement in it comes from chen2026, sun2026de, Fig. 2 or Extended Data Fig. 8, and `perturbation-ahlmann-20261011-source-data-fig2` is not cited. A later fix to any withheld judgement will withhold this summary again until it is re-reviewed.

## State after the change

Checked with `deriveUseCaseInputs`: both summaries publish; both MassSpecGym in the Wild judgements are active; every judgement active on `origin/main` is still active.

## Remaining gaps

- The perturbation text does not describe the GEARS Table 6 Pearson delta judgement or PertEval's foundation-model embeddings.
- The `description` of both summary claims still says "Draft until reviewed."; it is unchanged.
- No human scientific review.
