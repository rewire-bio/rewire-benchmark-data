# EGFR NSCLC actionability and resistance evidence: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-egfr-nsclc-20261009/`. It had 130 records and now has 128. Use case: `use-case-egfr-nsclc-actionability-resistance-evidence`.

Reviewer: a separate Claude review agent that did not extract the batch. No human review is claimed. Nothing was executed or reproduced. This review checks the transcription against the pinned sources and judges the relevance claims.

## Outcome

- All four source artifacts re-download to the pinned SHA-256.
- All 41 results match their source cells. No value, confidence interval, metric, qualifier, unit, direction or locator was wrong, and every expected cell has exactly one result.
- All 25 TREC Table 5 values also match independent copies: the TREC browser results page for infNDCG and P@10, and each run's appendix PDF for all three Phase 1 metrics, R-prec included.
- The run printed as "uog ufmg bg df5" is a misprint of uog_ufmg_sb_df5. I merged it into that run: one configuration and one evaluation were removed, and the result was renamed and relinked. This is why the batch now has 128 records.
- Four judgements hold as `proxy`. The FoundationOne judgement is regraded `outside_scope`. The two manual TREC runs are excluded from the Phase 2 judgement, with reasons.
- Several descriptive fields were corrected or extended. No number changed. Every record is now `source_checked`.
- Simulation: I added the reviewed batch to an in-memory copy of the store, applied the use-case changes below and computed pins. All seven judgements on the use case then derive as active: the five new ones and the two existing ones.

## How the check was done

1. Downloaded each `artifact_url` into an empty directory and hashed it. The TREC browser page was fetched through the GitHub contents API at the pinned commit.
2. Lin et al. Tables 1 and 2: parsed `table-wrap` `Tab1` and `Tab2` from the article XML with a parser written for this review. The extractor's script was not imported or run.
3. TREC overview Tables 5 and 6: parsed from the text layer (`pdftotext -layout`) of the pinned PDF.
4. For every result I built the expected identity of its cell from the table headers (model and setting, dataset, block, row, team, run). Then I compared:
   - printed value, numeric value and the 95% CI;
   - metric, qualifier, unit and direction;
   - the configuration and protocol of the linked evaluation.
5. For TREC, I also parsed the browser `results.md` at the same commit (not a source record; SHA-256 `eb91f6976732d8245905be8073e38d861ca0c6f983a5d4eb4b864a8c607068cf`) and the 14 run appendix PDFs. I compared every Table 5 value with both, and recomputed each team's best run per metric.
6. Read the cited Methods, Results and Discussion paragraphs of Lin et al., and the overview's sections on topics, relevance, evidence tiers and results, to check definitions, counts, run types and locators.
7. Loaded the reviewed batch against the current store in memory with `recordSchema`, `validateVocabularies` (including the two new metric concepts), `validateAttributes` and `validateRecords`. Then ran `deriveUseCaseInputs` with the proposed links and exclusion and computed pins. Nothing was written to the store.

## Sources and hashes

| Source | Pinned SHA-256 | Re-download |
| --- | --- | --- |
| `egfrnsclc-20261009-source-lin2025` (PMC12078457 XML) | `09c67fca...0f80` | Match |
| `egfrnsclc-20261009-source-trec2020-pm-overview` (OVERVIEW.PM.pdf) | `7951225e...26c2` | Match |
| `egfrnsclc-20261009-source-trec2020-pm-topics` (topics2020.xml) | `18053304...5e32` | Match |
| `egfrnsclc-20261009-source-trec-browser-pm2020-runs` (runs.md at `75ec9339`) | `910bdd0f...35ec` | Match |

The run appendix PDFs were read for cross-checks only and are not source records. Their hashes are in the review scratch directory.

## Values checked

| Table | Cells | Matched | Cross-checked elsewhere |
| --- | --- | --- | --- |
| Lin et al. Table 1 (mean, 95% CI, p value) | 9 | 9 | Results text P12, P16 |
| Lin et al. Table 2 (7 new rows; 4 rows repeat Table 1 and were confirmed equal) | 7 | 7 | Results text P20 to P23 |
| TREC Table 5, infNDCG | 5 | 5 | Browser and appendices: 5 of 5 |
| TREC Table 5, R-prec | 5 | 5 | Appendices: 5 of 5 |
| TREC Table 5, P@10 | 5 | 5 | Browser and appendices: 5 of 5 |
| TREC Table 6, std-gains and exp-gains | 10 | 10 | None available (see below) |
| Total | 41 | 41 | 15 of 25 TREC values |

The best-run-per-team order in Table 5 agrees with the browser. One exception: P@10 has a tie at fifth place. BITEM's sibtm_run1 and POZNAN's pozbaseline both score 0.5323, and only POZNAN is printed. This is now a limitation on the Phase 1 judgement.

## The collector's points

- **"uog ufmg bg df5".** It is a misprint, and I merged it.
  - UoGTr submitted five runs (Table 4 and the browser): uog_ufmg_DFRee, uog_ufmg_s_dfr5, uog_ufmg_secL2R, uog_ufmg_s_dfr0 and uog_ufmg_sb_df5. None is "bg".
  - The printed 0.5484 equals uog_ufmg_sb_df5's P@10 in the browser and in its appendix, and it is that team's highest P@10.
  - The same team's infNDCG row in Table 5 prints "uog ufmg sb df5".
  - Keeping a separate configuration for a run that does not exist would put a phantom system on the page. So I removed `config-trec2020-pm-uog-ufmg-bg-df5` and `eval-trec2020-pm-phase1-uog-ufmg-bg-df5`. The result is now `result-trec2020-pm-uog-ufmg-sb-df5-p10` on the uog_ufmg_sb_df5 Phase 1 evaluation. A `scope_note` keeps the printed name and the reasoning, and the locator still quotes the printed name.
  - I updated `claims.csv` and `coverage.json` to match.
- **Manual runs.** Run types confirmed from the browser: damoespcbh3 (ALIBABA) and uwman (MRG UWaterloo) are manual; Table 4 notes three manual runs each from these teams.
  - damoespcbh3 used "human-in-the-loop active learning" with "private annotations of relevance". uwman used "manual screening and relevance feedback".
  - Human relevance input on the test topics makes them human-assisted workflows, not systems comparable with the automatic runs.
  - Decision: exclude both evaluations from the Phase 2 judgement with reasons. Their results stay `source_checked` because the transcription is correct.
  - Separately, r1st (PINGAN NLP, Phase 1) is listed as automatic, but its description says the team manually labelled about 2,000 PubMed papers to train its models. It is not excluded, because the run type is automatic and it is not stated whether the labels concern the 2020 topics. Its configuration and the Phase 1 judgement now carry that caveat.
- **TREC origin.** Keep `independent_paper`. The vocabulary defines it as "Result reported in a paper by authors independent of the evaluated method". The overview is written by the track organisers, who scored every run against NIST assessors' judgements; none of the 16 participating teams is an organiser. `unreported` is a missingness state and does not apply, because the origin is clear.
- **Llama 3 against Llama 3.1.** Methods P39, P46 and P48, the Results text and Table 2 all say Llama 3.1 (70B). Only the Table 1 header says "Llama 3", and the Table 1 caption says "Llama 3.1". I read the header as a short form. The `parameters` note on the configuration records the difference, which is enough.
- **Training-data contamination.** Confirmed as stated (Discussion P33). The cutoffs given in Methods P39 (GPT-4o October 2023, Llama 3.1 December 2023, Qwen 2.5 undisclosed) predate the 2024-11-20 table downloads. This means that entries added after a cutoff are also unseen, which works against the models. Both effects are in the judgements' limitations and in the proposed evidence gaps.
- **R-prec and NDCG@30.**
  - The R-prec cells can be cross-checked after all: every run appendix prints "Mean R-prec", and all five match Table 5.
  - Table 6 cannot. The browser lists only `ndcg_cut_10` for Phase 2, the appendices show only Phase 1 measures, and the per-run evidence-eval summaries need participant credentials.
  - The ten Table 6 values are transcribed correctly from the PDF, but they rest on the overview alone. This is a limitation on the Phase 2 judgement.

## Additional findings and corrections

| Record | Field | Change |
| --- | --- | --- |
| Nine Table 1 results | `metric_qualifier` | "mean over iterations" to "mean over 100 iterations" (Methods P47: 100 iterations for basic prompts) |
| Two Llama temperature results (0.4, 0) | `metric_qualifier` | Notes that Methods P47 says 10 iterations while the Figure 7 caption says 100 |
| Nine Table 1 results | `reported_p_value` | The test is named in Methods P52 (ANOVA); the batch said it was not named |
| OncoKB and CIViC protocols and judgements | `limitations` | Queries name no drug, while the reference tables assign levels per drug or per evidence item, so a variant with both a sensitivity and a resistance level has no single correct answer, and the paper does not say how such queries were scored |
| Three Lin protocols | `limitations` | The 95% CIs are 0.0004 to 0.0049 wide and appear to describe run-to-run variation, not sampling of variants |
| CIViC judgement | `rationale` | It repeated the OncoKB text ("including OncoKB resistance levels"); rewritten for CIViC levels, which grade strength, not direction |
| `config-trec2020-pm-r1st`, Phase 1 judgement | `limitations` | Manual labelling caveat (see above) |
| Both TREC protocols and judgements | `limitations` | Topics name a gene, not a variant; the EGFR topics are afatinib and osimertinib; no topic asks for resistance evidence |
| 15 TREC evaluations | `comparison.population` | "Topics with judged documents (31 of 40)" was wrong, because all 40 topics have judged documents (Table 3). Now: 31 of 40 scored as the appendices state, with the dropped topics not identified |
| TREC dataset | `population` | The 31-topic figure is attributed to the run appendices |
| `claims.csv` | 25 TREC rows | `source_id` changed from the browser runs page to the overview, which is where the values are printed |

The two descriptive claims are correct:
- The Lin query example matches Methods P45.
- The EGFR topic judgement counts match Table 3: topic 15 has 226, 94 and 252; topic 16 has 182, 44 and 302.

The new GPT-4o model record does not duplicate the store's `reported-model-f53062b0ae4285`, which is excluded and scoped to another paper.

## Metric concepts

`precision-at-10` and `r-precision` are accepted as written:
- Both definitions match the standard information-retrieval measures that trec_eval reports as `P_10` and `Rprec`.
- `skos:broader :precision` is right, and the direction is `higher`.
- I searched the EBI Ontology Lookup Service for "R-precision", "precision at 10", "precision at k" and "precision@k". It returned no metric term with these definitions; STATO has only the precision-recall curve. So no external match is added.

infNDCG and NDCG@30 are stored under the general `ndcg` concept with the variant in the qualifier. That is acceptable, because the concept's definition says the cutoff is unspecified unless a narrower concept is used.

## Fit of the judgements

The use case asks for source-linked evidence assertions with regimen, sensitivity or resistance direction, treatment setting and native evidence tier, for advanced EGFR-mutant NSCLC, including after EGFR-targeted therapy. Both existing judgements are pan-cancer CIViC proxies, so pan-cancer alone does not rule a protocol out. The question is which parts of the output each protocol scores.

| Judgement | Grade | Reason | Reviewed evaluations |
| --- | --- | --- | --- |
| `...-lin2025-oncokb` | proxy | Scores the native OncoKB tier for a variant in a tumour type, including the resistance levels R1 and R2. It retrieves nothing, names no drug and cites no source. | 6 |
| `...-lin2025-civic` | proxy | Scores the native CIViC level for a molecular profile in a disease. CIViC levels grade strength only. Rationale corrected. | 4 |
| `...-lin2025-foundationone` | outside_scope | Scores whether a model reproduces one hospital's FoundationOne CDx reports' split into reported findings and VUS. No regimen, direction, setting, tier or source is scored, and the reference is one vendor's interpretation. Grouping fields removed. | none |
| `...-trec2020-phase1` | proxy | Scores retrieval of literature matching a disease, gene and treatment, which is regimen-scoped retrieval. | 9 |
| `...-trec2020-phase2` | proxy | Scores ranking by evidence strength, a form of native tier. Manual runs damoespcbh3 and uwman are excluded. | 4 |

**Are the TREC topics close enough even for a proxy?** Yes, as weak proxies at the same level as the two existing CIViC judgements.
- In favour: both phases score open-corpus literature retrieval for a named cancer, gene and drug, and Phase 2 scores evidence strength. Both are named parts of the use case's output. Topics 15 and 16 are EGFR NSCLC and have among the largest judged-relevant sets of all 40 topics (226 and 182 definitely relevant).
- Against: the topics name a gene, not a variant. The two EGFR topics are sensitivity drugs, afatinib and osimertinib, and no topic asks for resistance evidence or gives prior therapy (the overview says so in section 5.2). Phase 2 deliberately weights conclusive negative results the same as positive ones, so direction is not scored. At most two of the 31 scored topics are EGFR, so most of each score comes from other cancers.
- These limits are written on both judgements. They hold as proxies but should not be read as evidence about resistance retrieval.

**Grouping.** The Lin group keeps OncoKB and CIViC as strata 2 and 3. Stratum 1, FoundationOne, is removed with its regrading. The TREC group keeps Phase 1 and Phase 2. The headline metrics exist among each comparison's results. TREC Phase 2 has two `ndcg` results per run, which the qualifier separates as standard and exponential gains.

## Approved use-case changes

This is the exact text to apply to `use-case-egfr-nsclc-actionability-resistance-evidence`. Fields not listed stay unchanged. `decision`, `output`, `setting`, `inputs` and `clinical_scope` already describe the target correctly, and none of the new judgements contradicts them.

### `exclusions`

Keep the three existing entries and append one:

```json
"Treatment-recommendation concordance (for example LLM agreement with NCCN guidelines or tumour-board decisions) is treatment selection, not evidence retrieval."
```

I approve this exclusion. It records why the screened treatment-recommendation studies were not taken forward.

### `evidence_gaps`

Keep the five existing entries and append these five. The collector's first proposed gap repeats the first existing entry word for word and is not added.

```json
[
  "Multi-system comparisons found are pan-cancer: LLM evidence-level assignment (Lin et al. 2025) and literature ranking for cancer, gene and treatment topics (TREC 2020 Precision Medicine, two EGFR topics); neither prints an EGFR-only score.",
  "TREC 2020 Precision Medicine scores for the two EGFR topics appear only as figures in the run appendices, and the topics name a gene and a drug (afatinib, osimertinib) but no variant, prior therapy or resistance question.",
  "LLM evidence-level accuracy may be inflated by training-data exposure to the public OncoKB and CIViC tables (Lin et al. 2025 Discussion), and its queries name no drug, so sensitivity and resistance levels for the same variant are not separated.",
  "TREC 2020 Precision Medicine Phase 2 (evidence-tier ranking) values rest on the overview alone; no public per-run NDCG@30 was found to check them.",
  "No multi-system comparison of retrieving resistance evidence (for example T790M, C797S or MET amplification) after progression on an EGFR inhibitor was found."
]
```

### `links`

Add `assessed_by` links to these five protocols, keeping the two existing links. The FoundationOne link is needed even though that judgement is `outside_scope`: every judgement needs its link, and the claim's grade decides whether its evaluations count.

- `egfrnsclc-20261009-protocol-lin2025-foundationone-relevant-vs-vus`
- `egfrnsclc-20261009-protocol-lin2025-oncokb-level-assignment`
- `egfrnsclc-20261009-protocol-lin2025-civic-level-assignment`
- `egfrnsclc-20261009-protocol-trec2020-pm-phase1-relevance`
- `egfrnsclc-20261009-protocol-trec2020-pm-phase2-evidence`

### `source_ids` and `citation_locators`

Add `egfrnsclc-20261009-source-lin2025` and `egfrnsclc-20261009-source-trec2020-pm-overview` to `source_ids`. Both are clean and hash-verified. Add:

```json
[
  {"source_id": "egfrnsclc-20261009-source-lin2025", "locator": "Methods P36 to P47 (datasets, queries, iterations); Tables 1 and 2; Discussion P33"},
  {"source_id": "egfrnsclc-20261009-source-trec2020-pm-overview", "locator": "Sections 5.2, 5.3 and 6; Tables 3 to 6"}
]
```

### Existing judgements under the new exclusion

Both still hold, and nothing on them needs to change:
- `use-case-mapping-20260930-345-ba1ec69965eb` (CIViC evidence-direction retrieval, precision, recall and F1) measures retrieval of CIViC evidence direction, not agreement with a treatment recommendation.
- `use-case-mapping-20261007-345-7c4af3e091bd` (CIViC-Fact v3 within-publication passage retrieval) measures passage retrieval, not treatment selection.
- Neither endpoint, rationale nor limitation refers to treatment-recommendation concordance.

In the simulation, applying the new `exclusions` withholds both existing judgements, with "pinned evidence changed since review" naming only the use case, because `exclusions` is pinned. After re-pinning they derive as active. Re-pin both against this review together with the five new judgements and the summary claim.

## Final summary text

> Two sources add multi-system comparisons on precision-oncology evidence tasks. Neither is specific to EGFR-mutant NSCLC after targeted therapy, and neither tests treatment choice or patient benefit. Lin et al. 2025 (npj Precision Oncology), whose authors did not develop the models, asked GPT-4o, Llama 3.1 and Qwen 2.5 to assign knowledge-base evidence levels to queries naming a gene, an alteration and a tumour type but no drug. Mean top-1 accuracy over 100 runs in assigning OncoKB levels, which include the resistance levels R1 and R2, was 0.3393, 0.3066 and 0.3328; for CIViC levels it was 0.1865, 0.1212 and 0.2485. The authors note that the public OncoKB and CIViC tables may be in the models' training data. In the TREC 2020 Precision Medicine track, scored by the track organisers, systems ranked MEDLINE abstracts for 40 cancer, gene and treatment topics, two of them EGFR-mutant NSCLC with afatinib or osimertinib. For topical relevance the best printed runs reached infNDCG 0.5325 (a BM25 baseline tuned on 2019 data) and 0.5303 (BioBERT re-ranking). For ranking by evidence tier, the best printed automatic run reached NDCG@30 0.4238 (monoT5 with trial and meta-analysis terms added to the query); two manual runs that used human relevance input are not counted. The overview prints only the best run of the top five teams per metric, per-topic EGFR scores are not tabulated, and the topics carry no variant, prior-therapy or resistance context. No source measures retrieval of source-linked resistance evidence after progression on an EGFR inhibitor.

Every number is a `source_checked` result in this batch, or a count printed in a source:

- **Lin et al.:**
  - OncoKB: `result-lin2025-gpt-4o-basic-oncokb-top1`, `-llama-basic-t0-8-oncokb-top1`, `-qwen-basic-oncokb-top1`.
  - CIViC: the matching three `-civic-top1` results.
  - The 100 iterations are from Methods P47.
- **TREC:**
  - `result-trec2020-pm-baseline-infndcg`, `result-trec2020-pm-csiromed-strrr-infndcg`, `result-trec2020-pm-monot5rct-stdgains`.
  - The topic counts are from topics2020.xml and the overview.

The FoundationOne values in the collector's proposal are removed, because that judgement is now `outside_scope`. So is the manual run's 0.4780.

## Checks run

- In memory: the reviewed batch (128 records) passes the schema, vocabulary, attribute and record checks against the current store.
- `npm run typecheck`: exit 0.
- `npm run records -- check`: 30,371 records match their provenance (the batch is not in the store).
- `npm test`: 499 of 499 pass.
- `npm run build`: not run. The batch is not in the store, and the build writes release files outside this review's scope.

## Remaining gaps

- Per-topic scores for the two EGFR topics, and Phase 2 per-run values, have no public table.
- Lin et al. do not report how queries with several reference levels were scored.
- Not covered, as the collector recorded: TREC 2017 to 2019, JAX-CKB, CGI, My Cancer Genome, the MOAlmanac RAG supplement, and prospective or clinician-in-the-loop evaluations.
