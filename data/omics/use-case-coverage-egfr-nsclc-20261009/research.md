# Research: EGFR NSCLC evidence-retrieval use-case pass, 2026-10-09

Use case: `use-case-egfr-nsclc-actionability-resistance-evidence` ("Which systems retrieve correctly scoped sensitivity and resistance evidence for advanced EGFR-mutant NSCLC?"). Existing judgements: CIViC evidence-direction retrieval (CIViC MCP study) and CIViC-Fact v3 within-paper passage retrieval. The 2026-10-07 dossier (`docs/reviews/use-cases/egfr-nsclc-evidence-retrieval-2026-10-07.md`) logged ten earlier queries; this pass did not repeat them and kept their exclusions (OncoTraj, MTBBench, JMIR RAG-for-MTB).

Goal: comparisons of several systems on the same precision-oncology evidence task with printed per-system values, kept to the evidence retrieved and its scoping, not treatment outcomes.

Bounds: cutoff 2026-10-09; budget 25 queries, 8 used; at most 3 sources, 2 extracted; lean batch (130 records). Lane `genomics`. Worker: Claude (Opus 5.5) research agent; no human review claimed.

This file is the pass's dossier, as in the CNV and ctDNA batches.

## Queries

Full entries: `search-use-case-egfr-nsclc-evidence-q1` to `q8` in `data/omics/search-ledger.jsonl`.

| # | Query (short form) | Channel | Outcome |
| --- | --- | --- | --- |
| 1 | LLM variant actionability benchmark, OncoKB, CIViC, EGFR T790M, C797S | web search | Leads: Hisch and Wang 2024; GPT-4o, Llama 3, Qwen 2.5 study |
| 2 | LLM title search with OncoKB or CIViC | Europe PMC | Jun et al. 2026 (MOAlmanac RAG) and an MTB recommendation study screened |
| 3 | OncoKB and CIViC concordance or comparison, knowledgebases, evidence levels | Europe PMC | Lin et al. 2025 taken forward; VICC, commercial platforms, Variomes screened |
| 4 | RAG LLM precision-oncology knowledge-base benchmark, osimertinib resistance | web search | No resistance-specific multi-system benchmark |
| 5 | arXiv 2407.04466 | arXiv API | Hisch and Wang 2024 metadata and licence |
| 6 | TREC 2020 Precision Medicine overview results tables | web search | TREC 2020 PM overview and NIST browser taken forward |
| 7 | ChatGPT, Gemini, Claude on EGFR NSCLC osimertinib resistance | web search | Treatment-recommendation and prediction studies only |
| 8 | arXiv 2503.24165 | arXiv API | Resistance prediction; excluded |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Lin et al. 2025, npj Precision Oncology, Tables 1-2 | Extract all value cells (16 results; four Table 2 cells repeat Table 1) | Three LLMs, plus prompt, temperature and RAG variants, assign OncoKB levels (including resistance levels R1 and R2) and CIViC levels to the same queries. Independent of the models' developers. The example query in Methods is EGFR L858R in NSCLC. |
| TREC 2020 PM overview, Tables 5-6 | Extract all 25 cells | Many retrieval systems ranked literature for the same 40 cancer-gene-treatment topics, two of them EGFR NSCLC, with a phase that grades evidence strength regardless of direction. Scored by the track organisers. |
| TREC browser results for all 66 runs | Not extracted | Lean batch; used only to cross-check Table 5. Per-topic EGFR scores are not tabulated anywhere public. |
| Jun et al. 2026, Cancer Cell (MOAlmanac RAG) | Lead | Developer study of retrieving approved biomarker-therapy pairs; per-system values in figures and a supplementary PDF; author manuscript under TDM terms only. |
| Hisch and Wang 2024, arXiv | Lead | CIViC evidence-level labelling of abstracts; the GPT-4 comparison uses 20 test items, and Table 6 repeats Table 5's logistic-regression per-class values with a different overall F1. |
| VICC meta-knowledgebase (Wagner et al. 2020) | Excluded | Supplementary tables are content counts; cross-knowledgebase match rates are in figures. |
| Commercial decision-support platforms (ESMO Open 2020) | Excluded | Concordance in prose and figures only. |
| NCCN-concordance and MTB recommendation LLM studies | Excluded | Treatment selection, outside the endpoint. |

## Record design

- Lin et al.: three protocols (FoundationOne relevant vs VUS; OncoKB level assignment; CIViC level assignment), eight configurations of three new model records (GPT-4o 2024-05-13 via Azure; Llama 3.1 70B and Qwen 2.5 72B via Ollama), 16 evaluations, origin `independent_paper`. Metric `top-1-accuracy`, unit fraction.
- TREC 2020 PM: two protocols (Phase 1 topical relevance; Phase 2 evidence tiers), one dataset (topics over the 2019 MEDLINE snapshot), 15 run configurations under 11 team methods, 16 evaluations, origin `independent_paper` (scored by the organisers, not the teams). Run descriptions, types and MD5s come from the NIST TREC browser at a pinned commit.
- Five judgements, all `proxy`, in two comparison groups.
- Two metric concepts added to `data/vocab/metric.ttl`: `precision-at-10` and `r-precision` (narrower than `precision`, direction higher).

## Things a reviewer should judge

1. **TREC run 'uog ufmg bg df5'.** Overview Table 5 (P@10 block) prints this run name, which is not among the 66 runs in the TREC browser. Its value (0.5484) equals the P@10 of run uog_ufmg_sb_df5 of the same team, which Tables 5 and 6 print elsewhere. Recorded as a separate configuration with an identity note, not merged.
2. **TREC Phase 2 metric.** The overview defines Phase 2 as NDCG@30; the TREC browser lists `ndcg_cut_10` under evidence-eval with different values. Not a conflict (different cutoffs), but Table 6 cannot be cross-checked from the browser.
3. **TREC manual runs.** damoespcbh3 (top of both Phase 2 blocks) and uwman are manual runs per the browser's run type; their configurations carry a limitation.
4. **TREC origin.** Recorded as `independent_paper` because the track organisers, not the teams, wrote the overview and scored the runs. A reviewer may prefer `unreported`.
5. **Lin et al. model naming.** Table 1 prints "Llama 3"; Methods and Table 2 print "Llama 3.1 (70B)". Recorded on the configuration.
6. **Lin et al. p values.** The single p value per row (<0.001) is kept on each of the row's three results as `reported_p_value`; the test is not named in the table.
7. **Lin et al. reference labels.** OncoKB and CIViC tables were accessed 2024-11-20; their content may be in the models' training data, which the authors acknowledge.
8. **OncoKB terms.** No OncoKB data are copied into the batch; the dataset record describes the table's size and level counts as printed by Lin et al.

## Coverage

Bounded pass; not systematic. Not covered: resistance-specific retrieval benchmarks (none found); per-topic TREC scores; TREC 2017-2019 PM tracks; JAX-CKB, CGI and My Cancer Genome comparisons; MOAlmanac RAG supplementary tables; any prospective or clinician-in-the-loop evaluation.
