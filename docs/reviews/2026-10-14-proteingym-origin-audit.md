# ProteinGym evaluation origins: audit, 2026-10-14

Issue #161. The review of the VEP literature batch ([vep-literature-2026-10-14-review.md](vep-literature-2026-10-14-review.md), ruling 2) set the 145 new ProteinGym leaderboard evaluations to origin `unreported` and asked for the older ProteinGym evaluations, which all said `author_reported`, to be audited. This review does that.

Who did it: one Claude (Opus 5.5) agent made every judgement here and applied it. There was no separate extractor and no separate reviewer, so the reasoning is written out below for a later reviewer to check. The 275 correction claims are stored as `needs_review` for that reason. No human review is claimed. Nothing was run or reproduced.

Batch folder: `data/omics/proteingym-origin-audit-20261014/` (`apply.py` makes the edits and the claims; `corrections.csv` lists every changed field with its old and new value).

## Outcome

| Group | Source | Evaluations | Before | After |
| --- | --- | --- | --- | --- |
| `proteingym-evaluation-*`, method by authors outside ProteinGym | ProteinGym paper, Tables 2 to 4 | 81 | `author_reported` | `independent_paper` |
| `proteingym-evaluation-*`, method by ProteinGym authors | ProteinGym paper, Tables 2 to 4 | 140 | `author_reported` | `author_reported` (no change) |
| `uc20260930-proteingym-amfr-eval-*` | ProteinGym 144fe22 assay-level Spearman file | 97 | `author_reported` | `unreported` |

178 evaluations changed. The 97 AMFR evaluations also had the description "Author-reported evaluation, source checked; not independently reproduced.", which the new origin makes untrue; it now reads "Official ProteinGym assay-level Spearman for the AMFR assay at commit 144fe22; transcribed, not reproduced." Each changed field has a `metadata-correction-pgorigin-20261014-*` claim that keeps the old value (275 claims: 178 origins, 97 descriptions). No value, ID, link, locator or source hash changed.

One use-case judgement was withheld by the change and was re-reviewed and re-pinned (see [Use-case judgements](#use-case-judgements)).

## Scope

Every evaluation in the store whose sources include a ProteinGym artifact (the paper, its Europe PMC copy, a file in the ProteinGym repository) was listed. Besides the two groups above, these exist and are not changed:

- `vep-lit-20261014-eval-pg-*` (145): already `unreported` under the earlier ruling.
- `evaluation-lit-017`, `evaluation-lit-018` (ESM-2 and ProteinMPNN, source `proteingym-2023`): already `independent_paper`, which matches the rule below.
- `rewire-local-20260920-*`, `rewire-local-20260921-*`: `rewire_run`, Rewire's own runs.
- Evaluations that only cite ProteinGym as a benchmark but whose numbers come from another paper (PFMBench, BioML-bench, the ESM2 OFS paper, the GPN-MSA preprint, Livesey and Marsh 2025). Their origin depends on that paper, not on ProteinGym, so they are outside this issue.

## The rule

The origin vocabulary (`data/vocab/origin.ttl`) defines `author_reported` as "result reported by the authors of the evaluated method" and `independent_paper` as "result reported in a paper by authors independent of the evaluated method". `unreported` means the source does not say. The question for each row is therefore: does the source say who produced the scores, and are those people the method's developers?

- Where the source states that the ProteinGym authors generated the scores and computed the metric, the origin follows from whether any ProteinGym author developed the evaluated method: `author_reported` if so, `independent_paper` if not.
- Where the source does not say who generated each model's scores, the origin is `unreported`. This is the ruling of the VEP review, applied unchanged.
- `paper_compilation` does not fit any of these rows: in every case ProteinGym computed the metric with its own scripts; nothing was copied from an earlier paper.

## Sources

Re-retrieved on 2026-10-14 (from 16:57Z) from the URL on each source record. All hashes match.

| Source record | Artifact | SHA-256 |
| --- | --- | --- |
| `evidence-expansion-proteingym-a3b08cc4` | ProteinGym, NeurIPS 2023 Datasets and Benchmarks PDF | `a3b08cc4a6befd64620cf0f287d78d55a36dc2639955f52c5655f83833c50104` |
| `uc20260930-source-proteingym-amfr-spearman` | `DMS_substitutions_Spearman_DMS_level.csv` at 144fe22 | `f432423b87f79ac9778dfac86e3d95be041d246bc618dc0a406b35b0b7466437` |
| `run-doc-proteingym-readme-md-144fe22b` | `README.md` at 144fe22 | `321487a8de52c6cfa647a658f61150dd72e0acb0125470524fb94d1f8b23321a` |
| `profile-protocol-proteingym-paper-xml-a58110e0` | Europe PMC fullTextXML, PMC10723403 (read for comparison only) | `a58110e02c3efc8395c534d48630f577c3d45e90d48198b7f9989cf52600b045` |

The PDF was read as text with `pdftotext -layout`.

## The paper rows (`proteingym-evaluation-*`, 221)

All 221 rows cite Table 2 (zero-shot substitutions, 105), Table 3 (supervised substitutions, 80) or Table 4 (zero-shot indels, 36) of the paper.

### Who generated the scores and computed the metrics

The paper says the ProteinGym authors did both:

- Section 4.1, Baselines: "We implement a diverse set of 50+ zero-shot baselines". The section then lists the indel-capable models: "We thus only report the performance of the following baselines".
- Section 4.2, Baselines: "For the supervised DMS benchmark, we report two suites of baselines", with OHE and embedding models, "Lastly, we include ProteinNPT".
- Section 6 and Appendix A.3.3: the repository consolidates the baselines and "all of the model predictions can be reproduced using this repository"; checkpoints and files "necessary for scoring (for baselines such as profileHMM, PROVEAN) are also available via our servers".
- Appendix A.4: "Unless otherwise specified, model scores are calculated by taking the log-ratio ...", followed by per-model scoring choices made by the authors (for example the masked-marginal approach for ESM, and the extension of ESM-1b and ESM-1v to sequences longer than the context window).
- GEMME, Appendix A.4.1: "To obtain scores, we used the GEMME web-tool ... with default parameters." The GEMME developers' server produced the predictions, but the ProteinGym authors submitted the jobs and computed the metric. This is an independent use of a published tool, not a result the GEMME authors reported. (The 144fe22 README thanks the GEMME team for providing scores for v0.1; the v1.0 paper describes its own procedure, so the paper governs these rows.)
- The metric is the paper's own: the "corrected average" across assays in the Table 2 and Table 3 captions.

So the source states the scorer for every row. The origin depends only on who developed each method.

### Who developed each method

The paper's author list is Notin, Kollasch, Ritter, van Niekerk, Paul, Spinner, Rollins, Shaw, Weitzman, Frazer, Dias, Franceschi, Orenbuch, Gal and Marks. Each method's developers were read from the paper's reference list, using the reference the paper cites for that method.

Kept as `author_reported` (140 evaluations, 21 configurations): at least one ProteinGym author developed the method.

| Configuration | Reference in the paper | ProteinGym authors among the developers |
| --- | --- | --- |
| Site-Independent, EVmutation | Hopf et al. 2017 | Marks |
| DeepSequence (ensemble) | Riesselman, Ingraham and Marks 2018 | Marks |
| WaveNet | Shin et al. 2021 | Kollasch, Marks |
| EVE (ensemble) | Frazer et al. 2021 | Frazer, Notin, Dias, Gal, Marks |
| Tranception L, Tranception M | Notin et al. 2022a | Notin, Dias, Frazer, Gal, Marks |
| TranceptEVE L, TranceptEVE M | Notin et al. 2022b | Notin, van Niekerk, Kollasch, Ritter, Gal, Marks |
| RITA L, RITA XL | Hesslow et al. 2022 | Notin, Marks |
| ProteinNPT | Notin et al. 2023 | Notin, Weitzman, Marks, Gal |
| OHE (None, DeepSequence, ESM-1v, MSAT, Tranception, TranceptEVE); Embed. (ESM-1v, MSAT, Tranception) | Appendix A.4.2: "We leverage the various supervised baselines defined in Notin et al. [2023]" | Notin, Weitzman, Marks, Gal |

Changed to `independent_paper` (81 evaluations, 17 configurations): no ProteinGym author is among the developers.

| Configuration | Reference in the paper |
| --- | --- |
| CARP (640M) | Yang, Lu and Fusi 2023a |
| ESM-1b | Rives et al. 2021 |
| ESM-1v (ensemble) | Meier et al. 2021 |
| ESM-2 (15B) | Lin et al. 2023 |
| ESM-IF1 | Hsu et al. 2022b |
| GEMME | Laine, Karami and Carbone 2019 |
| HMM | Eddy 2011 (HMMER) |
| MIF-ST | Yang, Zanichelli and Yeh 2023b |
| MSA Transformer (ensemble) | Rao et al. 2021 |
| ProGen2 M, ProGen2 XL | Nijkamp et al. 2022 |
| ProteinMPNN | Dauparas et al. 2022 |
| ProtGPT2 | Ferruz, Schmidt and Hoecker 2022 |
| PROVEAN | Choi et al. 2012 |
| UniRep, UniRep evotuned | Alley et al. 2019 (evotuning was done by the ProteinGym authors) |
| VESPA | Marquet et al. 2022 |

### Judgement calls a reviewer should check

1. **RITA.** It is easy to miss that Notin and Marks are RITA authors (Hesslow, Zanichelli, Notin, Poli and Marks 2022, as listed in the paper's references). RITA L and RITA XL keep `author_reported` for that reason.
2. **Author overlap rather than identical teams.** Site-Independent, EVmutation and DeepSequence share only Marks with ProteinGym; WaveNet shares Kollasch and Marks. The vocabulary does not say how much overlap makes a result the developers' own. This review treats any shared author as `author_reported`, because the developers' group produced and published the number and the label then warns a reader about self-evaluation, which is the purpose of the distinction. A stricter rule (all or most developers) would move these 24 evaluations to `independent_paper`.
3. **The supervised OHE and embedding baselines.** These configurations take features from third-party models (ESM-1v, MSA Transformer) and, for OHE, follow the augmentation approach of Hsu et al. 2022a, who are not ProteinGym authors. But the paper says the configurations were "defined in Notin et al. [2023]", and the evaluated system is the supervised predictor, not the feature model. They keep `author_reported`. One of them, `proteingym-method-ohe-esm-1v`, links `uses_model` to ESM-1v; a reader of that configuration page could mistake the label for ESM-1v's developers reporting it. If a reviewer prefers to treat the configuration as Hsu et al.'s method, the 48 OHE evaluations would become `independent_paper`.

## The AMFR rows (`uc20260930-proteingym-amfr-eval-*`, 97)

The source is `DMS_substitutions_Spearman_DMS_level.csv` at 144fe22, row `AMFR_HUMAN_Tsuboyama_2023_4G3O`. It has one Spearman column per model and no field saying who generated that model's scores. ProteinGym computed the Spearman values with its own scripts.

These are the same kind of row as the 97 DMS summary evaluations in the VEP batch, from the same commit, and each AMFR evaluation links to the same configuration record as its summary counterpart (for example both `uc20260930-proteingym-amfr-eval-tranception-l-no-retrieval` and `vep-lit-20261014-eval-pg-dms-tranception-l-no-retrieval` link to `uc20260930-proteingym-amfr-config-tranception-l-no-retrieval`). The VEP review set the summary rows to `unreported`, including those for Tranception, TranceptEVE and EVE. The same rule gives `unreported` for all 97 AMFR rows.

Considered and not adopted:

- **`author_reported` for the ProteinGym authors' own models in the file.** The paper says the ProteinGym authors scored the v1.0 baselines, but the 144fe22 file is v1.3 and covers 97 models, many added later by other teams. The file does not say which scores were regenerated or by whom, and the VEP review did not make this exception for the summary rows of the same models. Diverging would give one configuration two different origins on the same evidence.
- **`author_reported` for models whose teams contributed them.** The README's acknowledgements (line 222) thank "the ProtSSN, SaProt, PoET, MULAN, VespaG, ProSST, ESCOTT, VenusREM, RSALOR, SiteRM and AIDO teams for integrating their model in the ProteinGym repo", and the "New baselines" section (lines 159 to 170) says requests are considered only when "all model scores for all mutants ... are provided by the requester". Together these suggest those teams supplied their scores. But the acknowledgement says "integrating their model", not that the scores in the 144fe22 files are theirs, and the "New baselines" rule describes the current process, not the history of each column. The file still does not state the scorer per row, and the metric is ProteinGym's. These stay `unreported`.

## Use-case judgements

Judgements pin each reviewed evaluation's origin (docs/use-cases.md, Pins), so a change of origin withholds them. The pins in the store were compared with the store after the change:

- `use-case-mapping-20260930-337-fa51fe46268a` (protein stability, AMFR official snapshot, `proxy`) pins all 97 AMFR evaluations. 97 pinned values differ, all of them the AMFR evaluations; the use case, protocol, sources and results pins are unchanged. It was withheld.
- `use-case-summary-protein-stability` mentions the AMFR evaluations but its pins did not change, so it was not withheld.
- No judgement or summary pins any `proteingym-evaluation-*` record.

Re-review of `use-case-mapping-20260930-337-fa51fe46268a`: the judgement's relevance (`proxy`), endpoint, rationale, constraint and five limitations say nothing about who scored the models, and none of them depends on it. The values, metric, protocol and data are unchanged. The origin change makes the evidence label more cautious (the page will no longer say the developers reported these numbers) but does not change what the comparison shows for the use case. The judgement stands as written and was re-pinned with `npm run use-cases:repin -- docs/reviews/2026-10-14-proteingym-origin-audit.md use-case-mapping-20260930-337-fa51fe46268a`. `tests/use-case-records.test.ts` passes afterwards, with the same number of active judgements as before.

## Remaining gaps

- The 275 correction claims are `needs_review`; a separate reviewer should check the three judgement calls above.
- The paper rows are v1.0 results. Whether ProteinGym later rescored any of these models is not stated in the paper and was not checked.
- The README's evidence that contributing teams supplied their own scores was not followed up per model (for example in the pull requests that added each baseline). If it were, some of the 97 AMFR rows and the matching VEP summary rows could move from `unreported` to `author_reported` together.
