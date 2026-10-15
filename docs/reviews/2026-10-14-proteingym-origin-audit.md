# ProteinGym evaluation origins: audit, 2026-10-14

Issue #161. The review of the VEP literature batch ([vep-literature-2026-10-14-review.md](vep-literature-2026-10-14-review.md), ruling 2) set the 145 new ProteinGym leaderboard evaluations to origin `unreported` and asked for the older ProteinGym evaluations, which all said `author_reported`, to be audited. This review does that.

Who did it: one Claude (Opus 5.5) agent made every judgement here and applied it. There was no separate extractor and no separate reviewer, so the reasoning is written out below for a later reviewer to check. The 275 correction claims were stored as `needs_review` for that reason. A second Claude agent then reviewed them independently (see [Independent review](#independent-review)) and set them to `source_checked`. No human review is claimed. Nothing was run or reproduced.

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

- The paper rows are v1.0 results. Whether ProteinGym later rescored any of these models is not stated in the paper and was not checked.
- The README's evidence that contributing teams supplied their own scores was not followed up per model (for example in the pull requests that added each baseline). If it were, some of the 97 AMFR rows and the matching VEP summary rows could move from `unreported` to `author_reported` together.
- Several stored locators carry text from the PDF's row-group column ("Alignment- Site-Independent", "based WaveNet", "language CARP (640M)", "Protein UniRep"), and in Table 3 `row(MSAT)` and `row(Tranception)` are used for both the OHE and the embedding configuration. The values differ, so each record still identifies one cell with its system link, but the locator alone does not. This predates the audit and was not changed here.

## Independent review

Reviewer: a second Claude (Opus 5.5) agent, which did not make or apply any of the judgements above. No human review is claimed. Date 2026-10-14. Nothing was run or reproduced.

### Sources

The paper PDF, the 144fe22 assay-level Spearman CSV and the 144fe22 README were downloaded again from the URLs on their source records. All three SHA-256 values match the table in [Sources](#sources). The PDF was read with `pdftotext -layout`.

Method developers were checked against each method paper's own author metadata, not only the ProteinGym reference list: Crossref for the journal and bioRxiv papers (Hopf 2017, Riesselman 2018, Shin 2021, Frazer 2021, Notin 2022b, Notin 2023 (ProteinNPT), Hsu 2022a and 2022b, Laine 2019, Choi 2012, Eddy 2011, Alley 2019, Marquet 2022, Dauparas 2022, Ferruz 2022, Rives 2021, Meier 2021, Rao 2021, Lin 2023, Yang 2022 (CARP), Yang 2023 (MIF-ST)) and arXiv for RITA (2205.05789), ProGen2 (2206.13517) and Tranception (2205.13760). Every list matches the paper's reference list. The overlaps with the ProteinGym author list are as stated in [Who developed each method](#who-developed-each-method), and no developer of the 17 `independent_paper` methods is a ProteinGym author. Zanichelli is a RITA and MIF-ST author but not a ProteinGym author.

### The rule

Agreed. The record contract lists the origin values and `data/vocab/origin.ttl` defines them: `author_reported` is a result "reported by the authors of the evaluated method"; `independent_paper` is a result "reported in a paper by authors independent of the evaluated method". The paper states that its authors implemented and scored the baselines and computed the corrected averages (Sections 4.1, 4.2 and 6; Appendices A.3.3 and A.4). So the reporters of every Table 2 to 4 row are the ProteinGym authors, and the origin depends on whether they overlap the method's developers. `paper_compilation` does not apply, because nothing was copied from an earlier paper.

### The three judgement calls

1. **RITA: agree, `author_reported`.** The arXiv record lists Hesslow, Zanichelli, Notin, Poli and Marks. Notin is ProteinGym's first author and Marks its senior author, so ProteinGym is not by authors independent of RITA.
2. **Any shared author: agree.** The vocabulary decides this. `independent_paper` requires authors independent of the method. Marks is the last author of Hopf 2017 (Site-Independent, EVmutation), Riesselman 2018 (DeepSequence) and Shin 2021 (WaveNet, which also has Kollasch), and of ProteinGym, so these rows are the same lab reporting its own methods. A stricter rule would label these 24 evaluations independent, which the definition does not allow. They keep `author_reported`.
3. **OHE and embedding baselines: agree, Notin et al. 2023.** Appendix A.4.2 says "We leverage the various supervised baselines defined in Notin et al. [2023]", and for the embedding models "We refer to Notin et al. [2023] for all implementation details". Hsu et al. 2022a (Hsu, Nisonoff, Fannjiang and Listgarten, confirmed on Crossref) is cited for the regression approach the OHE models follow, not as the source of these configurations. The evaluated system is the supervised predictor as configured in ProteinNPT, whose four authors (Notin, Weitzman, Marks, Gal) are all ProteinGym authors. The embedding rows do not cite Hsu et al. at all. The 48 OHE and 24 embedding evaluations keep `author_reported`. The concern about `proteingym-method-ohe-esm-1v` is covered by the record contract: `uses_model` "does not assign its result to the base model".

Also agreed: GEMME is `independent_paper` (Appendix A.4.1: for v1.0 the ProteinGym authors ran the GEMME web tool themselves); UniRep evotuned is `independent_paper` (evotuning is Alley et al.'s procedure, and running it does not make the ProteinGym authors its developers); HMM and PROVEAN are `independent_paper`.

### Paper rows checked

All 221 `proteingym-evaluation-*` evaluations were compared automatically with the paper. Each result's `printed_value` was compared with the cell named by its evaluation's table, row and column, using the system link to pick the OHE, embedding or NPT group in Table 3. Each origin was compared with the rule above, using the developer lists from the method papers. 221 of 221 match on value and origin. The diff against the parent commit was also checked: the 81 changed paper evaluations differ only in `origin`, and no other evaluation field, value, link or locator changed.

Sample also read by eye in the table text (30 changed, 21 unchanged, at least one per configuration). The row column gives the table row label, with the Table 3 group added.

| Evaluation | Table, row, column | Printed value | Audit | Origin | Outcome |
| --- | --- | --- | --- | --- | --- |
| `proteingym-evaluation-carp-640m-zs-sub-auc` | Table 2, CARP (640M), Zero-shot substitutions, AUC | 0.701 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-esm-1b-zs-sub-ndcg` | Table 2, ESM-1b, Zero-shot substitutions, NDCG@10% | 0.747 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-esm-1b-zs-sub-spearman` | Table 2, ESM-1b, Zero-shot substitutions, Spearman | 0.394 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-esm-1v-ensemble-zs-sub-ndcg` | Table 2, ESM-1v (ensemble), Zero-shot substitutions, NDCG@10% | 0.749 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-esm-2-15b-zs-sub-recall` | Table 2, ESM-2 (15B), Zero-shot substitutions, top 10% recall | 0.208 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-esm-if1-zs-sub-mcc` | Table 2, ESM-IF1, Zero-shot substitutions, MCC | 0.331 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-esm-if1-zs-sub-spearman` | Table 2, ESM-IF1, Zero-shot substitutions, Spearman | 0.422 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-gemme-zs-sub-mcc` | Table 2, GEMME, Zero-shot substitutions, MCC | 0.352 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-gemme-zs-sub-ndcg` | Table 2, GEMME, Zero-shot substitutions, NDCG@10% | 0.777 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-hmm-zs-indel-spearman-all` | Table 4, HMM, Zero-shot indels, all assays, Spearman | 0.389 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-hmm-zs-indel-spearman-designed` | Table 4, HMM, Zero-shot indels, designed or natural assays, Spearman | 0.518 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-mif-st-zs-sub-mcc` | Table 2, MIF-ST, Zero-shot substitutions, MCC | 0.311 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-msa-transformer-ensemble-zs-sub-mcc` | Table 2, MSA Transformer (ensemble), Zero-shot substitutions, MCC | 0.340 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-msa-transformer-ensemble-zs-sub-spearman` | Table 2, MSA Transformer (ensemble), Zero-shot substitutions, Spearman | 0.434 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-progen2-m-zs-indel-spearman-library` | Table 4, ProGen2 M, Zero-shot indels, library assays, Spearman | 0.472 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-progen2-xl-zs-sub-mcc` | Table 2, ProGen2 XL, Zero-shot substitutions, MCC | 0.306 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-progen2-xl-zs-sub-spearman` | Table 2, ProGen2 XL, Zero-shot substitutions, Spearman | 0.391 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-proteinmpnn-zs-sub-mcc` | Table 2, ProteinMPNN, Zero-shot substitutions, MCC | 0.196 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-protgpt2-zs-indel-spearman-library` | Table 4, ProtGPT2, Zero-shot indels, library assays, Spearman | 0.185 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-provean-zs-indel-auc` | Table 4, PROVEAN, Zero-shot indels, all assays, AUC | 0.725 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-unirep-evotuned-zs-sub-auc` | Table 2, UniRep evotuned, Zero-shot substitutions, AUC | 0.693 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-unirep-evotuned-zs-sub-ndcg` | Table 2, UniRep evotuned, Zero-shot substitutions, NDCG@10% | 0.739 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-unirep-evotuned-zs-sub-recall` | Table 2, UniRep evotuned, Zero-shot substitutions, top 10% recall | 0.181 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-unirep-zs-sub-auc` | Table 2, UniRep, Zero-shot substitutions, AUC | 0.605 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-unirep-zs-sub-ndcg` | Table 2, UniRep, Zero-shot substitutions, NDCG@10% | 0.647 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-unirep-zs-sub-recall` | Table 2, UniRep, Zero-shot substitutions, top 10% recall | 0.139 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-unirep-zs-sub-spearman` | Table 2, UniRep, Zero-shot substitutions, Spearman | 0.190 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-vespa-zs-sub-auc` | Table 2, VESPA, Zero-shot substitutions, AUC | 0.742 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-vespa-zs-sub-recall` | Table 2, VESPA, Zero-shot substitutions, top 10% recall | 0.201 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-vespa-zs-sub-spearman` | Table 2, VESPA, Zero-shot substitutions, Spearman | 0.436 | Changed | `independent_paper` | Match |
| `proteingym-evaluation-deepsequence-ensemble-zs-sub-auc` | Table 2, DeepSequence (ensemble), Zero-shot substitutions, AUC | 0.729 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-embed-esm-1v-sup-sub-spearman-avg` | Table 3, Embed. ESM-1v, Supervised substitutions, average over splits, Spearman | 0.542 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-embed-msat-sup-sub-spearman-contig` | Table 3, Embed. MSAT, Supervised substitutions, contiguous split, Spearman | 0.525 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-embed-tranception-sup-sub-mse-mod` | Table 3, Embed. Tranception, Supervised substitutions, modulo split, MSE | 0.833 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-eve-ensemble-zs-sub-mcc` | Table 2, EVE (ensemble), Zero-shot substitutions, MCC | 0.342 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-evmutation-zs-sub-recall` | Table 2, EVmutation, Zero-shot substitutions, top 10% recall | 0.222 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-npt-proteinnpt-sup-sub-mse-avg` | Table 3, NPT ProteinNPT, Supervised substitutions, average over splits, MSE | 0.683 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-ohe-deepsequence-sup-sub-mse-rand` | Table 3, OHE DeepSequence, Supervised substitutions, random split, MSE | 0.767 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-ohe-esm-1v-sup-sub-spearman-avg` | Table 3, OHE ESM-1v, Supervised substitutions, average over splits, Spearman | 0.417 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-ohe-msat-sup-sub-mse-avg` | Table 3, OHE MSAT, Supervised substitutions, average over splits, MSE | 0.882 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-ohe-none-sup-sub-spearman-mod` | Table 3, OHE None, Supervised substitutions, modulo split, Spearman | 0.027 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-ohe-trancepteve-sup-sub-spearman-avg` | Table 3, OHE TranceptEVE, Supervised substitutions, average over splits, Spearman | 0.477 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-ohe-tranception-sup-sub-mse-avg` | Table 3, OHE Tranception, Supervised substitutions, average over splits, MSE | 0.895 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-rita-l-zs-indel-spearman-library` | Table 4, RITA L, Zero-shot indels, library assays, Spearman | 0.443 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-rita-xl-zs-sub-auc` | Table 2, RITA XL, Zero-shot substitutions, AUC | 0.707 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-site-independent-zs-sub-spearman` | Table 2, Site-Independent, Zero-shot substitutions, Spearman | 0.359 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-trancepteve-l-zs-sub-ndcg` | Table 2, TranceptEVE L, Zero-shot substitutions, NDCG@10% | 0.786 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-trancepteve-m-zs-indel-spearman-all` | Table 4, TranceptEVE M, Zero-shot indels, all assays, Spearman | 0.424 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-tranception-l-zs-sub-ndcg` | Table 2, Tranception L, Zero-shot substitutions, NDCG@10% | 0.779 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-tranception-m-zs-indel-auc` | Table 4, Tranception M, Zero-shot indels, all assays, AUC | 0.733 | Unchanged | `author_reported` | Match |
| `proteingym-evaluation-wavenet-zs-sub-mcc` | Table 2, WaveNet, Zero-shot substitutions, MCC | 0.294 | Unchanged | `author_reported` | Match |

### AMFR rows checked

All 97 `uc20260930-proteingym-amfr-eval-*` results were compared automatically with the 144fe22 CSV (line 15, `AMFR_HUMAN_Tsuboyama_2023_4G3O`, the column named in each evaluation's locator): 97 of 97 match. The 97 changed evaluations differ from the parent commit only in `origin` and `description`. Sample also read by eye:

| Evaluation | CSV column | CSV value | Outcome |
| --- | --- | --- | --- |
| `uc20260930-proteingym-amfr-eval-esm2-150m` | ESM2 (150M) | 0.321 | Match |
| `uc20260930-proteingym-amfr-eval-evmutation` | EVmutation | 0.418 | Match |
| `uc20260930-proteingym-amfr-eval-gemme` | GEMME | 0.396 | Match |
| `uc20260930-proteingym-amfr-eval-mif` | MIF | 0.251 | Match |
| `uc20260930-proteingym-amfr-eval-msa-transformer-single` | MSA Transformer (single) | 0.22 | Match |
| `uc20260930-proteingym-amfr-eval-prosst-k-512` | ProSST (K=512) | 0.479 | Match |
| `uc20260930-proteingym-amfr-eval-proteinmpnn` | ProteinMPNN | 0.353 | Match |
| `uc20260930-proteingym-amfr-eval-rita-s` | RITA S | -0.052 | Match |
| `uc20260930-proteingym-amfr-eval-rsalor` | RSALOR | 0.341 | Match |
| `uc20260930-proteingym-amfr-eval-s2f` | S2F | 0.328 | Match |
| `uc20260930-proteingym-amfr-eval-s3f` | S3F | 0.322 | Match |
| `uc20260930-proteingym-amfr-eval-s3f-msa` | S3F-MSA | 0.362 | Match |
| `uc20260930-proteingym-amfr-eval-tranception-l` | Tranception L | 0.356 | Match |
| `uc20260930-proteingym-amfr-eval-xtrimopglm-3b-mlm` | xTrimoPGLM-3B-MLM | 0.247 | Match |
| `uc20260930-proteingym-amfr-eval-xtrimopglm-7b-clm` | xTrimoPGLM-7B-CLM | -0.144 | Match |

**Origin `unreported`: agree.** The CSV has one Spearman column per model and nothing on who produced the scores. The README at 144fe22 does not state per-model provenance either:

- Its baseline table (lines 68 to 104) gives each model's reference paper, not who scored it.
- The acknowledgement (line 222) thanks the ProtSSN, SaProt, PoET, MULAN, VespaG, ProSST, ESCOTT, VenusREM, RSALOR, SiteRM and AIDO teams "for integrating their model in the ProteinGym repo". That could mean code, scores or both.
- "New baselines" (lines 159 to 170) describes the current policy, that requests are considered when "all model scores for all mutants ... are provided by the requester", and adds that the maintainers plan to score widely used models themselves. It does not say who scored any given column.

That is not a clear statement of per-model provenance, so no row was moved to `author_reported`. It also keeps each AMFR evaluation's origin the same as its VEP summary counterpart on the same configuration, as ruling 2 of the VEP review set.

Considered and not adopted: for the models developed by ProteinGym authors (Tranception, TranceptEVE, EVE, DeepSequence and others in the file), whoever generated the scores was plausibly the developers' group. But the v1.3 file is maintained by a repository team that is not the v1.0 author list, the file states nothing, and ruling 2 declined this inference for the same configurations. `unreported` is the accurate value.

The new AMFR description ("Official ProteinGym assay-level Spearman for the AMFR assay at commit 144fe22; transcribed, not reproduced.") is accurate and no longer claims an origin.

### Use-case judgement

`use-case-mapping-20260930-337-fa51fe46268a` was compared with its state before the PR. Only `attributes.pins` changed: 198 pins before and after, with the same record IDs, and the 97 that differ are all AMFR evaluations, whose pinned fields include `attributes.origin`. Relevance (`proxy`), endpoint, rationale, the constraint, the five limitations, the citation locators and the review are unchanged. None of them mentions or depends on who reported the scores: the limitations concern mixed single and double mutants, coverage, missing uncertainty, input requirements and the stability endpoint. The judgement stands as written. Running `npm run use-cases:repin` for it under this review pinned 0 claims: its pins already match the store, so the pins recorded in the PR stand.

### Claims

All 275 `metadata-correction-pgorigin-20261014-*` claims were checked against the store. Each claim's `previous_value` and `value` equal its subject's field before and after the PR; every changed field has exactly one claim and one `corrections.csv` row; every changed evaluation is covered. All 275 are accepted and set to `source_checked`, with this review in their review notes, in the store and in `batch.jsonl`, and recorded with `npm run records -- change`.

### Verdict

Approve. The rule follows the origin definitions, the three judgement calls are right, every value and origin was checked, and nothing in the store needed correcting. Changes made in this review: the 275 claims set to `source_checked`, the receipt updated, and this section added.
