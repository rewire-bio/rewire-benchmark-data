# Search report: phenotype perturbation selection refresh, 2026-10-22

Use case `use-case-phenotype-perturbation-selection` ("Which genetic perturbations should I test to produce a defined cellular response?"), slug `phenotype-perturbation-selection`. Issue [rewire-benchmark-data #184](https://github.com/rewire-bio/rewire-benchmark-data/issues/184). Lane content `cells-spatial`; the use case's own facets are `cells-tissues` and `research`.

Worker: Claude (Opus 5.5) research agent; no human review claimed. No records written in this pass, no model run, nothing committed.

Bounds: cutoff 2026-10-22, query budget 25, 23 used including four failures. Ledger entry `search-use-case-refresh-phenotype-20261022`; include and exclude decisions in `data/omics/scope-audit.jsonl` with the same date.

## What the store already holds, and was not re-read

- Two judgements on the use case, both from the Cancer Immunotherapy Data Science Challenge (CPPC): `ucc-research-protocol-cppc-challenge2-original` (custom top-k overlap area, 20 submissions) and `ucc-research-protocol-cppc-prospective-selection` (prospective nomination campaign, two named hits).
- The 2026-10-07 dossier `docs/reviews/use-cases/phenotype-perturbation-selection-2026-10-07.md`: seventeen earlier queries, the CPPC denominator ledger, and exclusions for ITERPERT, sequential optimal experimental design, the Arc Virtual Cell Challenge wrap-up and the case-4 expression-reconstruction sources. Those exclusions were kept and the queries were not repeated.
- The neighbouring target-validation pass `data/omics/use-case-coverage-target-validation-20261009`, which holds BioDiscoveryAgent (Roohani et al. 2025, hit ratio after 5 rounds of 128 genes, with a `random` row), the Gupta et al. permuted-feedback replication, AssayBench (De Brouwer et al. 2026) and DiscoBAX as a method record. Its own notes list AssayBench-Loop (arXiv:2609.11877) as not covered.

So the retrospective, screen-as-unit comparisons already exist in the store for single-gene selection under the target-validation use case. What was missing for this use case was a matched random comparator at a fixed budget on the same data, and any coverage of combinations.

## Candidates worth extracting, best first

### 1. AssayLoop / AssayBench-Loop, arXiv:2609.11877 v1

Edwards, De Brouwer, Li, Lee, Hajiramezanali, Biton, Mostafavi, Scalia. v1 submitted 10 September 2026, CC BY 4.0. PDF retrieved in this pass (digest in the table below), byte-identical to the copy hashed on 2026-10-07, so the artifact has not moved.

Why it fits: Table 1 ("Performance comparison on held-out test screens") puts 26 policies on the same 20 temporally held-out CRISPR screens under one stated budget, T = 10 rounds of b = 100 requested genes (1,000 acquisitions per screen, about 5% of the library). One of the rows is `Random`, and the caption states it is an instantiation of the random policy rather than an expected value. Columns: EF (enrichment factor, hit rate relative to random), nAUC (%), FH (%, fraction of hits found), SF (%, shortfall), %ess (recovered hits that are DepMap common-essential), and EP-B / EP-S / EP-D (effective number of Reactome level-2 pathway groups at batch, screen and dataset scope). The caption states metrics are computed per screen and then averaged equally over the 20 test screens, and that EP-B/EP-S/EP-D are not comparable across scopes because each gene is assigned one of its pathway groups at random and each scope is subsampled to a fixed annotated-gene count (30, 200, 6000).

Rows are grouped: base LLMs with and without access to outcome labels; the authors' AssayLLM (Qwen3.6-27B base, +SFT, +SFT+GRPO); adaptive experimental design methods (Random, prior-hit baseline, Screen-kNN, BPMF, MAML, BioBO, Probability-of-Hit); agent harnesses (a Haiku-4.5 coding agent, LLMNN, ICBR-EF); AssayFormer variants; and AssayLoop handoffs. The text points to Supplementary Table 4 for full results, which the PDF appears to contain around the appendix table that repeats Table 1's rows with extra columns.

Caveats visible in the source: the paper is the authors' own method (Genentech), so the AssayLoop, AssayFormer and AssayLLM rows are author-reported; test and validation screens were restricted to genome-wide coverage and other criteria, so they are not a random sample of screens; labels are historical, the held-out unit is the screen, and the authors do not report a prospective validation; a sizeable share of recovered hits are common-essential genes, which the %ess column makes explicit.

### 2. NAIAD, PMLR 267:50363-50383 (ICML 2025)

Qin, Wessels, Fernandez-Granda, Hao, "Active Learning for Efficient Discovery of Optimal Combinatorial Perturbations". Preprint arXiv:2411.12010. PDF retrieved from the PMLR assets repository (digest in the table below). Code at `github.com/NeptuneBio/NAIAD` (not pinned in this pass).

Why it fits: it is combination selection, the axis the use case separates out and the store does not cover, and it has a matched random comparator. Table 2 gives the number of the top 200 gene combinations correctly discovered at round 4 of active learning for Uniform, MPE, UCB and Uncertainty acquisition on four datasets (Norman, Simpson, Horlbeck K562, Horlbeck Jurkat). Table 3 gives the marginal gain of those discoveries. Table 4 crosses NAIAD against RECOVER for Uniform, MPE and UCB with standard errors across three cross-fold replicates. Table 1 and appendix Table 6 are RMSE of response prediction, a different endpoint. Appendix Tables 5, 7 and 8 vary ensemble size, rounds and the UCB beta.

Caveats visible in the source: retrospective replay over already-measured combinatorial screens; "top 200 strongest gene pairs" is the ground truth, so the endpoint is recovery of the strongest measured pairs rather than an experimentally confirmed phenotype hit; NAIAD is the authors' own method; the active-learning simulation starts all acquisition functions from the same uniformly sampled seed set.

### 3. VirtualCRISPR, BioNLP 2025 (2025.bionlp-1.30), lower priority

Song et al., "Virtual CRISPR: Can LLMs Predict CRISPR Screen Results?", DOI 10.18653/v1/2025.bionlp-1.30, pages 354-364. A benchmark built from BioGRID-ORCS plus manually curated sources, testing language models and an embedding-based predictor on whether perturbing a gene in a cell type produces a phenotype. Not read in this pass. It is the method behind the psoriasis study below and overlaps AssayBench's data source, so it may be a hit-classification endpoint rather than a budgeted selection one.

## Excluded, with reasons

| Source | Decision | Reason |
| --- | --- | --- |
| AI-guided CRISPR screen in psoriasis (Nat Commun 2026, PMC13473102; preprint PPR1221906) | Excluded | VirtualCRISPR is applied after the genome-wide screen to annotate how novel the already-significant hits are (FDR < 0.1, at least 2 sgRNAs), combined with plausibility and tractability judgements. Two genes were validated. There is no shortlist under a budget, no selection metric and no random or conventional comparator. |
| TFcomb (Genome Research 2025), Mogrify, CellCartographer | Excluded | Reprogramming factor selection, but the endpoint is recovery of known factor combinations or a few validated conversions, not hits per test budget against a matched comparator. Screened from search results only. |
| PDGrapher (Nat Biomed Eng 2025) | Excluded | Ranks known perturbagen targets for phenotype reversal; the comparison is rank improvement over other methods, not hits per budget, and no primary table was resolved here. |
| Probability-of-Hit, "Many Needles in a Haystack" (ICML 2026, OpenReview iZN85pjpsS) | Retrieval gap | Forum page returns a bot challenge and `api2.openreview.net` returns HTTP 403. Scores appear only as a third-party row in AssayLoop Table 1. |
| BioBO (arXiv:2509.19988) | Retrieval gap | Abstract names no datasets, baselines or metrics; paper not read. v1 (24 Sep 2025) and v2 (23 Mar 2026) differ. |
| REIGN (ICLR 2026 listing) | Excluded | Listing only; information-gain acquisition across contexts, which the use case separates from hit selection. |
| GeneDisco (arXiv:2110.11875), DiscoBAX | Not re-screened | The 2026-10-09 exclusion of GeneDisco (no result tables in the text layer) was kept; DiscoBAX already exists as a method record. |

## What the pass did not cover

- No prospective wet-lab comparison of a model shortlist against random or conventional selection at the same budget was found. The gap recorded on the use case stands.
- PubMed was not queried separately; the two Europe PMC topic queries were narrow (three hits between them).
- AssayLoop figures 4 and 6, its per-screen results and its Methods were not read; only Table 1, its caption, the surrounding results text and the appendix table block were inspected.
- NAIAD appendix Tables 5 to 9 were located but not transcribed, and the Methods were not read closely enough to confirm that Uniform draws from the same candidate universe in every round.
- Chemical perturbations, information-gain-only designs, and expression-reconstruction endpoints were left out of scope as before.
- Findings are bounded to the 23 queries in the ledger entry; nothing here is a claim about work outside them.

## Artifact hashes from this pass

Retrieved 2026-10-22, held in the session scratchpad only, not archived in this batch folder:

| Artifact | URL | SHA-256 |
| --- | --- | --- |
| AssayLoop PDF, arXiv:2609.11877 v1 | `https://arxiv.org/pdf/2609.11877` | `adcaaa5b7f9bd0e3bc1f91d94d26c8d4924c5c0b3064b6625c01ba92c6eaef28` |
| NAIAD PDF, PMLR 267 | `https://raw.githubusercontent.com/mlresearch/v267/main/assets/qin25g/qin25g.pdf` | `983b2da8aed78f0aced27053301c15f0f67ebd0fac706435bb6800e309dd64eb` |

The AssayLoop digest matches the value recorded in the 2026-10-07 dossier, so that artifact is unchanged.

## Questions for the extractor

1. In AssayLoop Table 1, should Random be stored as a `baseline` with `baseline_type` random, given the caption says it is one instantiation of the random policy and not an expected value? EF is itself defined relative to random, so EF for the Random row is near 1 by construction.
2. Does EF belong to an existing metric concept, or does hit enrichment over random need a new one? Likewise FH against `recall`, nAUC, and shortfall.
3. Should EP-B, EP-S and EP-D be extracted at all, given the caption says the three are not comparable and that pathway assignment is randomised?
4. Are Table 1 and Supplementary Table 4 one protocol or two, and do the "w/o labels" rows change the allowed inputs enough to be a separate protocol?
5. For the LLM rows, is each named model a `configuration` of a third-party model, and what origin applies when the AssayLoop authors ran another vendor's model: `author_reported` or `independent_paper`?
6. For NAIAD, is "number of the top 200 gene combinations correctly discovered at round 4" a hit-yield endpoint for this use case, or a recovery-of-strongest-measured-pairs proxy that belongs in a separate protocol from AssayLoop's?
7. Does Uniform in NAIAD Tables 2 to 4 qualify as the matched random comparator the use case asks for, given all acquisition functions share the same seed set but the ground truth is a precomputed top-200 list?
8. Tables 2 and 3 print no uncertainty while Table 4 prints standard errors over three cross-fold replicates for an overlapping set of rows. Are Tables 2 and 4 the same experiment at different precision, and if the numbers differ (Uniform Norman 92 against 93.3), which goes in and does the other become a separate evaluation?
9. BioBO and Probability-of-Hit appear only as rows inside AssayLoop Table 1. Should they be stored with origin `independent_paper` on the AssayLoop protocol, or held back until their own papers are retrieved?
10. Does either new source change the existing CPPC judgements, or do they attach as new protocols with their own relevance judgement and leave CPPC untouched?

## Merged extraction, review and judgement notes

The sections below were written per source by the extraction, review and judgement agents. On finalising (2026-10-22) the four part files they mention (`parts/<source>.jsonl`) were merged into `batch.jsonl`, except the three records that already existed in the store (the use case, its baseline claim and its summary), whose reviewed copies are in `changes.jsonl` and were applied with `records -- change`. The `parts/` and `notes/` folders were then deleted.

## Edwards et al. 2026, AssayLoop / AssayBench-Loop (arXiv:2609.11877v1)

Extractor: Claude (Opus 5.5) extraction agent in the evidence-pass workflow; no human review claimed. Nothing here is reviewed.

### Source

- `https://arxiv.org/pdf/2609.11877v1`, retrieved 2026-10-22T13:57:26Z, SHA-256 `adcaaa5b7f9bd0e3bc1f91d94d26c8d4924c5c0b3064b6625c01ba92c6eaef28`. Same digest as the 2026-10-07 dossier and the search pass. CC BY 4.0, preprint, not archived in the batch.
- PDF and its `pdftotext -layout` text layer are in the session scratchpad only:
  `/private/tmp/claude-501/-Users-timrichardson-Documents-projects-personal-blog/c8d6e701-2ef3-40c5-b993-bfed2afd8b62/scratchpad/assayloop-pdf/assayloop-2609.11877v1.pdf` and
  `/private/tmp/claude-501/-Users-timrichardson-Documents-projects-personal-blog/c8d6e701-2ef3-40c5-b993-bfed2afd8b62/scratchpad/assayloop-layout.txt`.
- Read: Sections 2.1 to 2.3, 2.7 in part, Discussion limitations, Methods 4.1 to 4.3, 4.6, 4.7, 4.9, Appendix B, D.5, E.1, H, K, Table 1 and Supplementary Table 4. Not read: Figures 4 and 6, per-screen results (Supplementary Table 2), Appendix F, G, I, J.

### What was extracted

`extract/edwards2026assayloop.py` parses both tables from the text layer, asserts every row label and group heading in order (Table 1: 26 rows, 6 groups; Supplementary Table 4: 57 rows, 7 groups), and asserts that every value printed twice for the same run is identical. It then writes `parts/edwards2026assayloop.jsonl`:

| Kind | Count |
| --- | --- |
| source | 1 |
| dataset_subset | 1 |
| protocol | 1 |
| baseline | 1 |
| model | 10 |
| method | 12 (Random reuses `tgtval-20261009-method-random-selection`) |
| configuration | 53 |
| evaluation | 53 |
| result | 530 (53 runs x 10 metrics) |
| claim | 5 |

#### Duplicate printings, stored once

Supplementary Table 4 is a superset of Table 1: all 26 Table 1 rows reappear there with identical values in the 8 shared columns (asserted). Inside Supplementary Table 4, four more rows repeat a run: `Qwen3.6-27B` (Base LLMs) and `Qwen3.6-27B (base)` (AssayLLM); `AssayFormer (Random)` and `AssayFormer (random embs.)`; `AssayFormer (BPMF)` and `+ BPMF Embeddings`; `BPMF + GRPO` (Ablations) and `+ GRPO (= AssayFormer)`. All values match (asserted). Each run is one evaluation and each metric one result. Where a row is in Table 1, the 8 shared columns cite Table 1 and the Vendi and pathway-overlap columns cite Supplementary Table 4. Every other printing is named in the result's `review.note`. Storing both printings would double-count one measurement in comparisons.

### Decisions on the questions in the brief

#### 1. Random as a baseline

Stored three ways: a configuration of the existing method `tgtval-20261009-method-random-selection`, its evaluation with 10 results, and a `baseline` record (`ucpheno-20261022-baseline-edwards2026-random-policy`) with `implemented_by`, `measured_in` and `applicable_to` links.

`baseline_type` is `null_control`, because `data/vocab/baseline-type.ttl` has no `random` concept and null control is the scheme's concept for a no-information comparator. No new concept was added.

The caption says "Random is an instantiation of the random policy, not an expected value". The draw is recorded in the configuration parameters, the evaluation limitations and the baseline scope note. EF is defined against the random expectation (Methods 4.3, eq. 3), so its expected value under random selection is about 1. The printed 1.04 is one draw, and the row's FH, SF and diversity values are draws too. The row still matters: it is the only matched random comparator on the same screens and budget. For EF, though, the expected value 1 is already built into the metric, so the row adds less than it would for FH or nAUC. The random policy's sampling universe (G or the screen library) is not stated. Random SF is 10.0%, which suggests sampling from G, but that is not recorded as fact.

#### 2. Metric concepts

| Column | Concept | Direction | Unit |
| --- | --- | --- | --- |
| EF | `hit-enrichment-factor` (new, proposed) | higher | unitless |
| nAUC (%) | `normalized-cumulative-hits-auc` (new, proposed) | higher | unitless, printed x100 |
| FH / Frac. hits (%) | `recall` | higher | percent |
| SF / Shortfall (%) | `proportion` | lower (Table 1 arrow) | percent |
| %ess / Ess. (%) | `proportion` | unknown (no arrow) | percent |
| Vendi (%) | `vendi-ratio` (new, proposed) | unknown | unitless, printed x100 |
| Path. Ov. | `annotation-overlap-ratio` (new, proposed) | unknown | unitless |
| EP-B, EP-S, EP-D | `effective-number-of-groups` (new, proposed), scope in `metric_qualifier` | unknown | unitless |

EF needs a new concept. The nearest existing ones are `early-precision-ratio` and `auprc-ratio`, both defined by BEELINE for network edges, and `odds-ratio`, which is a different statistic. EF also uses an adjusted denominator: hallucinated genes and unfilled slots count, while valid genes outside the screen library do not. That goes in the qualifier. FH is recall over the screen's hit set (Appendix H eq. 21), the same concept the store uses for BioDiscoveryAgent's hit ratio. Shortfall fits `proportion` with a qualifier; it is a validity diagnostic, not a hit-yield endpoint. The proposed concept definitions are in `extract/edwards2026assayloop.metric-concepts.ttl`.

**Blocking for the merge stage:** the five proposed concepts are not in `data/vocab/metric.ttl`. This worker may only write its part file, so they were not added. `records -- add` will reject 371 of the 530 results until the concepts are added and reviewed in the same PR. If the reviewer rejects a concept, the matching results need re-keying.

Directions follow the arrows printed in Table 1. `%ess` and the EP columns carry no arrow. The text says larger EP means broader coverage, which describes the measure, not whether higher is better, so those directions are `unknown`.

#### 3. EP-B, EP-S, EP-D

Extracted. The caption says the three are not comparable with each other, because each uses a different rarefaction size. It does not say they are incomparable across methods. Within one scope every method is rarefied to the same annotated-gene count and averaged over the same number of Monte Carlo draws (400 for EP-B and EP-S, 300 for EP-D; Appendix H). The random group assignment is averaged out by those draws rather than fixed once. Each scope therefore has its own `metric_qualifier`, which keeps the three scopes apart under the comparison rules.

One wording conflict: the Table 1 caption says all metrics are computed per screen and then averaged over the 20 test screens, but Appendix H defines EP-D over the complete test set (M = 6000 across the test set). The EP-D qualifier follows Appendix H. This could go in `evidence_concerns` if the reviewer thinks it matters; it was not added. EP values are breadth diagnostics, not hit-yield endpoints, and should not be used as headline metrics.

#### 4. One protocol or two; the "w/o labels" rows

One protocol. Table 1 and Supplementary Table 4 report the same runs on the same 20 test screens, with the same budget and metric definitions. Every shared cell is identical (asserted), and the Table 1 caption itself says "See full results in Supplementary Table 4". Supplementary Table 4 adds rows and two columns, not a different split.

The label-ablation rows ("w/o labels" in Table 1, "- hit labels" in Supplementary Table 4) do not get their own protocol. Appendix K says the authors "simply omit the hit labels while preserving the history of previously acquired genes", and the prompt in Appendix E.1 shows that history. The benchmark exposes the same information to every policy. Withholding labels is a restriction the system places on itself, in the same way that Random and Probability-of-Hit ignore the training screens. So it is recorded on the configuration (parameters and name), not as different protocol inputs. `comparison.inputs` is the same on every evaluation. The reviewer may prefer to mark the ablation arms in `comparison.inputs` so that they are not compared automatically with the labelled arms. That is a defensible alternative: say so if you choose it.

#### 5. Third-party models: configurations and origin

Each named LLM (GLM-5.1, GLM-5.2, Kimi-K2.6, Claude Opus 4.8, Sonnet 4.6, Haiku 4.5, Qwen3.6-27B, Gemini 3.1 Pro, GPT-5.5, GPT-5.6 Sol) is a new `model` record, and each row is a `configuration` of it. None of these releases is in the store; the nearest records (`tgtval-20261009-model-gemini-3-pro`, `-gpt-5-4`, `-qwen3-5-2b`) are different releases and were not reused. `entity_level`:
- `service` for the hosted vendor models (Gemini, GPT, Claude);
- `checkpoint` for Qwen3.6-27B, since the authors fine-tuned it, so they must have had the weights (revision unreported);
- `family` for GLM-5.1, GLM-5.2 and Kimi-K2.6, whose access route is not stated.

Origin follows the store's precedent for AssayBench (`tgtval-20261009-eval-debrouwer2026-gemini-3-pro`, `independent_paper`), from an overlapping author group. The origin definition is "authors of the evaluated method". The AssayLoop authors did not build Gemini, GPT, GLM, Kimi, Claude or Qwen, so bare-LLM rows, with and without labels, are `independent_paper`. The same applies to third-party algorithms the authors ran: BPMF, MAML, BioBO, Probability-of-Hit, LLMNN, ICBR-EF, Transformer + DAgger and the two RF rows. The Haiku-4.5 coding agent is also `independent_paper`: a vendor model in an unnamed general coding harness.
- `author_reported`: AssayFormer and its ablations, AssayLLM (the authors' fine-tune of Qwen3.6-27B, a configuration of the Qwen model, as in the AssayBench `gpt-oss-120b-sft-grpo` precedent), all AssayLoop handoffs, and the authors' own baselines Random, Prior hit and Screen-kNN. Random follows the `tgtval-20261009-config-roohani2025-random` precedent.
- Caveat for the reviewer: for the LLM rows, the prompt, history format and gene-name normalisation are the AssayLoop authors' own. These authors also wrote AssayBench, from which the prompt is adapted. So `independent_paper` here means the authors did not build the model, not that the evaluation is independent of the authors' framework.

BioBO and Probability-of-Hit: stored as `independent_paper` rows on the AssayLoop protocol, not held back. They are the AssayLoop authors' runs of those methods and are labelled as such. They are not those papers' own results; both remain retrieval gaps in the search notes.

#### 6. Direct or proxy

My view is proxy, but the call belongs to the judgement stage, so no judgement record was written. Reasons, from the source:
- Retrospective replay with historical hit labels. The Discussion says "the policies evaluated here remain to be validated prospectively in a live experimental loop".
- The held-out unit is the screen. There are 20 test screens, and the extracted tables give means only.
- Test screens were filtered on a best-LLM performance floor (AnDCG@100 of at least 0.05 for Gemini 3.1 Pro on AssayBench, Methods 4.2). That conditions the test set on screens where an LLM can already name hits.
- A "hit" is the screen's own significance call (for example FDR < 0.05), not a confirmed cellular response the user asked for.
- Many recovered hits are DepMap common-essential genes (%ess ranges from 18.6% for Random to 99.1% for the prior-hit baseline; 30.1% for Gemini-3.1-Pro → AssayFormer).

Even so, it is closer to the decision than anything else in the store: a model-based selection policy and a matched random policy on the same screens, at the same stated budget, scored on hits found.

### Other observations for the reviewer

- **check-values window.** `scripts/omics/batch.py` searches 80 lines after a caption. In the text layer, the last six Supplementary Table 4 rows fall beyond that window: `BPMF + GRPO (EFterminal )`, `SVD + GRPO`, `MF + GRPO`, `MF-Sphere + GRPO`, `GenePT-PCA + GRPO` and `K562-PCA + GRPO`, at lines 82 to 86 after the caption. Their 60 results come back `row_not_found`. The parse script finds and asserts those rows; they need the manual check. A self-run of check-values gave 470 `in_row` and 60 `row_not_found`.
- **Repeated labels.** "w/o labels" appears twice in Table 1, and "- hit labels" five times in Supplementary Table 4. check-values matches any line with that label, so `in_row` does not confirm which row a value came from. Each locator names the row above it ("the row directly under 'GLM-5.1'"). Please spot-check these rows.
- **Row label spelling.** The `EFterminal` label carries a subscript, which renders as `(EFterminal )` in the text layer.
- **Undescribed rows.** RF (greedy), RF + UCB and Transformer + DAgger appear only as row labels in Supplementary Table 4. The Methods do not describe them, so their method descriptions are kept to what the labels say.
- **Uncertainty and runs.** No uncertainty is printed in either table. Supplementary Figure 6D shows ±1 SEM for five methods, as a figure only, and was not read. The number of runs or seeds per row is unreported, except that Random is one draw.
- **Access.** Page 1 carries Website, GitHub, PyPI and "Models & Data" labels, but their URLs were not recoverable from the text layer. This is recorded as `access_reuse` unextracted on each configuration.
- **Ablation table.** Supplementary Table 3 (ablation EFs) repeats Supplementary Table 4 values and was not extracted separately.
- **Headline numbers.** The abstract's headline (EF 5.67, 27.7% of hits at about 5% of the library) matches the `Gemini-3.1-Pro → AssayFormer` row. `GPT-5.6 Sol → AssayFormer` also prints EF 5.67, with FH 27.6.

### Gaps

- The five proposed metric concepts are not in the vocabulary (see question 2).
- Figures 4 and 6, the per-screen results and Supplementary Table 2 were not read or extracted.
- The random policy's sampling universe, the LLM sampling settings, and the API or weight versions are unreported.
- The backbone LLMs of LLMNN and ICBR-EF are not stated.

### Review

Reviewer: Claude (Opus 5.5) review agent in the evidence-pass workflow, independent of the extraction agent; no human review claimed. Date 2026-10-22. Scope: `parts/edwards2026assayloop.jsonl` only. No `review.json`, no store add and no repin were done here; the merge stage does those.

#### How it was checked

- PDF re-hashed: SHA-256 `adcaaa5b…ef28` matches the source record.
- `scripts/omics/batch.py check-values` on the text layer: 470 `in_row`, 60 `row_not_found`. Output kept as `review/edwards2026assayloop-value-check.tsv`. All 60 are the last six Supplementary Table 4 rows (`BPMF + GRPO (EFterminal)`, `SVD`, `MF`, `MF-Sphere`, `GenePT-PCA`, `K562-PCA` + GRPO), which sit beyond the script's 80-line window after the caption. Nothing else failed.
- A separate reviewer script, `review/edwards2026assayloop-check.py`, re-parses Table 1 (26 rows) and Supplementary Table 4 (57 rows) and requires exactly 8 or 10 numeric cells per row. It resolves each locator to one cell by group, row label, the row above it (for the repeated "w/o labels" and "- hit labels" rows) and column position. Result: 530 of 530 printed and numeric values match, and no cell is used twice. Output: `review/edwards2026assayloop-independent-check.tsv`. The same script confirms that all 26 Table 1 rows equal their Supplementary Table 4 printings in the 8 shared columns, and that the four repeated S4 runs are identical.
- Column assignment: pages 8 and 31 were rendered and compared by eye. This covered a seeded sample of 36 results (seed 20261022) and every row of the Base LLM, AssayLLM, Adaptive Experimental Design, Agent, AssayFormer, AssayLoop and Ablations blocks, including the six overflow rows. All matched, and the column order is the same as in the text layer. No cell in either table is empty, so the positional parse cannot shift a column.
- Scope: checked captions, arrows, Methods 4.2, 4.3 and 4.9, Appendix H, Appendix K, Figure 5 caption and the Discussion limitations. The 5 claims were checked against their locators.

#### Rulings on the extractor's questions

1. **Metric concepts: accept all five; do not re-key.** `docs/collection.md`: "If no concept fits, add one to the scheme in the same PR, with a definition and an external match … where one exists … Never add a concept that only respells an existing one." None of the five respells an existing concept. `early-precision-ratio` and `auprc-ratio` are defined for network edges. `odds-ratio` is a different statistic. `one-minus-overlap-ratio` compares two score distributions, not annotation sets. `recall` and `proportion` cannot express a budget-normalised enrichment, an oracle-normalised AUC, a Hill number or a Vendi score. Deciding text: Methods 4.3 eq. 3, "the ratio between the number of hits found and the expected number of hits under random selection", and Appendix H for nAUC, EP, VR and PO. I added a `skos:scopeNote` to each concept in `extract/edwards2026assayloop.metric-concepts.ttl`. No STATO, QUDT or EDAM match was confirmed. The merge stage must add the five concepts to `data/vocab/metric.ttl` in the same PR, or 371 results will be rejected.
2. **One result per run and metric: correct.** The Table 1 caption says "See full results in Supplementary Table 4". The reviewer parse shows all 26 Table 1 rows equal to S4 in the 8 shared columns. It also shows that the four repeated S4 runs (`Qwen3.6-27B`/`(base)`, `AssayFormer (Random)`/`(random embs.)`, `AssayFormer (BPMF)`/`+ BPMF Embeddings`, `BPMF + GRPO`/`+ GRPO (= AssayFormer)`) are identical in all 10 columns. One printing per cell would count one measurement two or three times. The locator split is sound: Table 1 for its 8 columns, S4 for Vendi, Path. Ov. and the S4-only rows.
3. **Random as `null_control`: accept.** The scheme defines `null_control` as "No-information control: training mean, class prior, shuffled input, random network, no change". The store already uses it for a "Seeded random ranking control" (ProteinGym AMFR). The single-draw caveat is placed correctly. Deciding text: Table 1 caption, "Random is an instantiation of the random policy, not an expected value". Figure 5 supports this: its Random ring is "the expected composition of a uniformly drawn batch", with EP-D 81.6 and EP-S 56.4, against the table's draw of 82.6 and 56.9. A note was added to the three Random EP results. **Correction:** the Random configuration said "over the candidate pool". The source does not say whether the policy samples from G or from the screen library, so the parameters and description now say it is unstated.
4. **Label-ablation arms: keep one `comparison.inputs`.** Appendix K: "we simply omit the hit labels while preserving the history of previously acquired genes. This provides a direct measure of how much each model benefits from observing experimental outcomes." The comparison with the labelled arm is the experiment the authors designed, and they print both arms in one table under one protocol. The benchmark offers the same information to every policy. Random, Prior hit and the label-free harnesses ignore parts of it too, and nobody would separate those by inputs. Separate inputs would block exactly the comparison the source makes. The ablation is visible in the configuration name and parameters and in the evaluation limitations.
5. **Origin: confirmed, with one correction.** The origin scheme defines `independent_paper` as "Result reported in a paper by authors independent of the evaluated method". The bare LLMs, BPMF [41], MAML [12, 41], BioBO [27], Probability-of-Hit [40], LLMNN [17], ICBR-EF [51], Transformer + DAgger [39] and the Haiku-4.5 coding agent are third-party methods, so `independent_paper` is right. This matches the AssayBench evaluations already in the store, for example `tgtval-20261009-eval-debrouwer2026-gemini-3-pro-post-cutoff`. The prompt-ownership caveat is already in each LLM evaluation's limitations. **Correction:** `RF (greedy)` and `RF + UCB` were `independent_paper`. They are uncited and undescribed (S4 row labels only, nothing in Methods 4.9), so they are the authors' own constructed baselines in the same sense as Random, Prior hit and Screen-kNN. Both are now `author_reported`, and their limitation says why.
6. **EP-D aggregation: do not add to `evidence_concerns`.** The two texts do conflict. The Table 1 caption says "All performance metrics are computed separately for each screen and then averaged equally across the 20 test screens". Appendix H uses "M = 6000 across the complete test set (EP-D)". But Appendix H is the explicit definition, and the EP-D qualifier already follows it. In this repository a source-level concern blocks every comparison from the source (`shared/omics/catalogue-query.ts`, `published-comparisons.ts`) and withholds any use-case judgement that cites it (`docs/use-cases.md`). One caption sentence about a breadth diagnostic does not justify blocking the only matched ML-versus-random comparison for this use case. Instead, each EP-D result's `coverage.note` records the pooled aggregation and the caption conflict. Each EP-B and EP-S result's `coverage.note` records Appendix H's exclusion rule: "Sample sets containing fewer than the required number of annotated genes are excluded", with the excluded count unreported.
7. **Directions: confirmed.** The Table 1 header prints `EF (↑) nAUC (%)(↑) FH (%)(↑) SF (%)(↓)` and no arrow on `%ess` or the EP columns. S4 prints no arrows. Appendix H describes VR ("A higher Vendi ratio means the genes acquired in the batch are more diverse") and PO ("A value of 1.00 corresponds to random selection") without calling either direction better, so `unknown` is right.
8. **entity_level: confirmed.** `service` for Gemini, GPT and Claude, which are hosted-only, as for the AssayBench precedents `tgtval-20261009-model-gemini-3-pro` and `-gpt-5-4`. `checkpoint` for Qwen3.6-27B, because the authors fine-tuned released weights (Methods 4.7), as for `tgtval-20261009-model-qwen3-5-2b`. `family` for GLM-5.1, GLM-5.2 and Kimi-K2.6 is the conservative choice: the source does not say whether they were run from weights or through an API, and neither `checkpoint` nor `service` is supported.
9. **`same_data_as` to `tgtval-20261009-data-assaybench-test`: removed.** Methods 4.2 says "we limit the validation and test sets to 20 screens each. These screens were selected to satisfy the following criteria". The subset is a selection of 20 screens from AssayBench's post-2021 pool, which has 334 entries. It is not the same data. The store has already ruled that "`same_data_as` is defined for dataset subsets with identical data" (`docs/reviews/use-cases/plasma-ctdna-methylation-2026-10-09.md`). The relation stays in the subset's `source_dataset` text and in a limitation.
10. **Relevance: proxy, agreeing with the extractor.** Deciding text, from the Discussion: "A SSAY B ENCH -L OOP is a retrospective benchmark focused on genome-wide screens with sufficient hit signal, and the policies evaluated here remain to be validated prospectively in a live experimental loop", and "the retrospective formulation treats observed screen outcomes as fixed labels and does not explicitly model experimental noise across replicates". Methods 4.2 adds the best-LLM performance floor on test-screen selection. For the judgement stage:
    - a hit is each screen's own significance call;
    - %ess shows many recovered hits are common-essential genes;
    - Random is a single draw;
    - every row, including the third-party ones, was run by the AssayLoop authors.

#### Other findings

- Figure 5 prints EP-S 46.7 for AssayLoop, while its EP-B 18.4 and EP-D 70.4 match the `Gemini-3.1-Pro → AssayFormer` row, whose tables print EP-S 46.6. The table value is stored, and the gap is noted on that result. It is too small to matter for a breadth diagnostic, and it may be Monte Carlo variation between renderings. It is not a concern.
- Supplementary Figure 10 shows "without hit feedback" EF for AssayFormer and AssayLoop as bars only. These were not extracted, which is correct for a figure.
- The apply script is `review/edwards2026assayloop_apply.py`. It is not idempotent: run it only against the pre-review part.

#### Changes made to the part

- All 667 records: `status` `needs_review` to `source_checked`.
- 530 results: `review` replaced with the reviewer's block (method, `method_note`, reviewer, date, hash, URL). The extractor's printing note is kept and the review outcome added. The 60 overflow results, the three Random EP results and the Gemini AssayLoop EP-S result carry the extra notes above.
- 159 EP results: `coverage.note` added (pooled EP-D, or the exclusion rule).
- 5 claims: `review` replaced with the reviewer's block.
- `config-edwards2026-random`: parameters and description no longer state the sampling universe.
- `eval-edwards2026-rf-greedy`, `eval-edwards2026-rf-ucb`: origin changed to `author_reported`, limitation rewritten.
- `data-edwards2026-assaybench-loop-test`: `same_data_as` link removed, limitation rewritten.
- `extract/edwards2026assayloop.metric-concepts.ttl`: review header and five `skos:scopeNote`s added.

#### Ready for the merge stage?

Yes, provided the five metric concepts are added to `data/vocab/metric.ttl` in the same PR. Otherwise `records -- add` rejects 371 results.

## Qin et al. 2025, NAIAD (PMLR 267:50363-50383)

Extractor: Claude (Opus 5.5) extraction agent; no human review claimed. Part file `parts/qin2025naiad.jsonl`, built by `extract/qin2025naiad.py` from the `pdftotext -layout` layer of the proceedings PDF. All records are `needs_review`.

### Source

- PDF `https://raw.githubusercontent.com/mlresearch/v267/main/assets/qin25g/qin25g.pdf`, retrieved 2026-10-22T13:57:27Z, SHA-256 `983b2da8aed78f0aced27053301c15f0f67ebd0fac706435bb6800e309dd64eb`. This matches the digest from the search pass. The PDF and the text layer are in the session scratchpad only. They are not archived, because the PDF prints "Copyright 2025 by the author(s)" and gives no reuse licence.
- The arXiv preprint 2411.12010 was not read. Only the proceedings version was used.
- Code: `github.com/NeptuneBio/NAIAD`. HEAD on 2026-10-22 was `9207e9e855e865160a196a6989392f6db622b0d6`, and GitHub metadata gives the licence as Apache-2.0. That commit is recorded in `code_url`. The repository was not read, and the paper does not name the commit it used.

### Records

There are 399 records: 1 source, 4 methods (NAIAD, RECOVER, the linear regression comparator and the MLP comparator), 4 datasets, 2 protocols, 31 configurations, 140 evaluations, 212 results and 5 claims. GEARS reuses the existing `catalog-model-gears` record. No store record for NAIAD, RECOVER, or the four viability screens as processed here was found. The existing Norman 2019 datasets in the store are expression profiles, a different measurement, so they were not reused.

Tables extracted in full: Table 1 (40 cells), Table 2 (16), Table 3 (16), Table 4 (24), Table 5 (32), Table 6 (20), Table 7 (20), Table 8 (44). Table 9 (the embedding schedule) is summarised in a claim and in the configuration parameters. Its rows are hyperparameters, not results.

The parse asserts row labels and cells per row. It also checks the arithmetic between Tables 2 and 3: Appendix D defines marginal gain as (P4 - P0)/4, and each dataset gives the same P0 across all four acquisition rows (Norman 88, Simpson 36, Horlbeck K562 37, Horlbeck Jurkat 69). In the scratchpad, `scripts/omics/batch.py check-values` against the text layer gave 200 `in_row` and 12 `row_not_found`. The 12 are the Table 1 GEARS rows and the Table 6 Linear rows. In the layout text the gene-frequency label ("4", "20", "10") starts those lines, so a row locator naming the model does not match the start of the line. The values are present in those lines. The locators keep the printed model label.

### Decisions on the brief's questions

**1. Hit yield, or a recovery proxy?** It is a recovery proxy and needs its own protocol. Appendix D defines the count as P_i = |X_i,P ∩ Y_i,P|. X_i is the measured values of the acquired pairs concatenated with the model's predictions for every unacquired pair, and Y_i,P is the top P measured values across the whole screen. So a strong pair counts as "discovered" when the model's ranking places it in the top 200, whether or not it was ever selected for measurement. This is not the number of strong pairs among those tested. AssayLoop's fraction of hits found counts acquired genes only, so the two endpoints are not the same quantity.

The ground truth is the 200 largest viability effects in the same fully measured screen, not a significance-thresholded or independently confirmed phenotype. The phenotype is cell viability only. Recorded as protocol `pheno-20261022-qin2025-protocol-al-top200` with metric `true-positive-count` (the count is the true positives of a top-200 call against the true top 200), unit `count`, denominator 200.

"Strongest" is not defined by sign. Appendix C.2 has MPE pick the highest absolute predicted effect, and Appendix D says "top P values". This is recorded in the protocol scope note.

**2. Is Uniform the matched random comparator?** Only as a random-acquisition control within the paper's own pipeline, not as a model-free random selection. Section 5.3 says all acquisition functions start "with the same uniformly sampled gene pairs", and Section 4.3 and Appendix C.5 say later rounds add pairs selected uniformly. So budget, rounds, seed set and screen are matched.

The Uniform count is still computed from NAIAD's measured-plus-predicted ranking. It measures NAIAD trained on randomly chosen pairs, not the yield of testing randomly chosen pairs. The yield of pure random selection is not reported. The paper also does not say whether the uniform draws exclude pairs already measured. Uniform is therefore stored as a configuration of NAIAD (and, in Table 4, of RECOVER). It is not linked to the store's `tgtval-20261009-method-random-selection`, and no baseline record was written. Whether the use case should treat it as its random comparator is for the reviewer and the judgement stage.

**3. Tables 2 and 4: the same experiment?** No. They are different runs, and Table 4 should be the comparison evaluation. The evidence:
- Table 2 prints integers. Table 4 prints means of three replicates with SE, and its values are multiples of 1/3.
- The differences are beyond rounding: MPE on Horlbeck Jurkat is 161 in Table 2 and 150.0 (4.0) in Table 4; MPE on Horlbeck K562 is 94 and 99.7 (4.2); Uniform on Simpson is 66 and 70.3 (5.0).
- The round-0 count implied by Tables 2 and 3 for Norman is 88. Table 7 gives NAIAD's round-0 mean on Norman as 86.0 (1.0).

The paper does not say how many runs Table 2 summarises. Integers and a single P0 per dataset are consistent with one replicate, but this is not stated, so it is not recorded as fact. The two tables are stored as separate evaluation groups (`qin2025-table2-3`, `qin2025-table4`). Table 2/3 evaluations carry `comparison.aggregation = null` with `missing_metadata.aggregation` `unreported`, which blocks automatic comparison with Table 4. They are kept because Table 2/3 is the only source of the Uncertainty acquisition row and of the marginal gain.

Other overlaps found:
- Table 7 at round 4 equals Table 4 for NAIAD MPE (143.0 (1.5)) and RECOVER MPE (138.7 (2.7)) on Norman, but NAIAD Uniform is 93.7 (0.7) in Table 7 and 93.3 (0.7) in Table 4.
- Table 8's Uniform row on Norman is 93.3 (2.9), the same mean as Table 4 with a different SE.
- Table 8 at beta = 0 should equal MPE by Appendix C.5, but it reads 138.3 (2.2) against Table 4's 143.0 (1.5).
- No ensemble size in Table 5 reproduces Table 4, so the default ensemble size is unknown.

Each table is kept as its own evaluation group with its own locators. The conflicts are listed in the source record's `limitations`. Whether they warrant an `evidence_concerns` entry is left to the reviewer.

**4. Uncertainty on Tables 2 and 3.** Yes. Every Table 2 and Table 3 result carries `missing_metadata.uncertainty` with reason `unreported`, and a note that the table prints no error and does not state the number of runs. Results in Tables 1 and 4 to 8 carry `standard_error` with n = 3, from captions that say "Error is SE across three cross-fold replicates". The captions do not name the point statistic, and the evaluations say so. The paper does not explain what a cross-fold replicate means in the active-learning setting, and this is listed as a protocol limitation.

**5. Is the acquisition function a configuration or a separate method?** A configuration. The scored system is the pair of surrogate model and acquisition function. Table 4 shows the score depends on both: MPE helps RECOVER and NAIAD by different amounts. The acquisition functions are formulae in Appendix C, not separate software. An evaluation can link only one `system`, so separate acquisition-method records would either need a composite record or would detach the score from the model. Each (model, acquisition) pair is therefore a configuration of NAIAD, RECOVER or GEARS, with the acquisition function in `selection` and in the name. RECOVER keeps one method record across its three acquisition configurations.

### Origins

- NAIAD rows are `author_reported`.
- RECOVER and GEARS rows are `independent_paper`: the NAIAD authors adapted and ran them. RECOVER was moved from drugs to genes with a bilinear projection of gene embeddings and trained on gene-Bliss scores. GEARS was fed synthetic N(0, 1) expression matrices because the screens have no single-cell data. Neither is the developers' own setting, and each evaluation says so.
- The linear and MLP comparators were defined by the paper's authors and are `author_reported`, with `configuration_type` `reported_configuration`.

### Metrics chosen

- Tables 2, 4, 5, 7 and 8 use `true-positive-count`, direction higher, unit `count`, `unit_detail` "gene pairs, out of the 200 strongest measured pairs". The qualifier names the round.
- Table 3 uses `count`, direction higher, `unit_detail` "top-200 gene pairs per round". The qualifier states (P4 - P0)/4. It is an average per-round gain, not a tally, so a reviewer may prefer a dedicated concept.
- Tables 1 and 6 use `root-mean-squared-error`, direction lower, unit `unitless`, `unit_detail` "printed x 10^-2". `numeric_value` is kept at the printed scale, following the store's "printed x100" precedent. The qualifier names the gene frequency (4, 10 or 20).

### Gaps

- Figures 3, 4, 5, 7, 8 and 9 print no values. These include the drug-combination comparison with RECOVER (Section 5.4, Figure 5) and the per-round curves for all acquisition functions (Figure 4). Not extracted.
- Training set sizes behind Table 1 and Table 6 are not printed with those tables. Table 9 gives an approximate size for each average gene frequency, which may be the same schedule. That link is not asserted.
- Accessions for the four processed screens are not printed.
- The code repository was not read, so the code version used for the paper is unknown.

### Review

Reviewer: Claude (Opus 5.5) review agent, independent of the extraction agent; no human review claimed. Date 2026-10-22.

#### What was checked

- Source: re-hashed the scratchpad copy of `qin25g.pdf`; SHA-256 `983b2da8aed78f0aced27053301c15f0f67ebd0fac706435bb6800e309dd64eb` matches the source record.
- `scripts/omics/batch.py check-values` on this part against the `pdftotext -layout` layer: 200 `in_row`, 12 `row_not_found`. Output: `review/qin2025naiad-value-check.tsv`.
- Independent parse: `review/qin2025naiad-check.py` parses Tables 1 to 8 from the text layer with asserted row labels and cells per row, then maps each result to its cell through the evaluation's `system` and `data` links and the metric qualifier (gene frequency, round, beta, ensemble size), not through `source_locator`. All 212 printed values, numeric values and standard errors match, and every locator names the same cell. Output: `review/qin2025naiad-independent-check.tsv`.
- Manual check: compared Tables 1 to 8 by eye with the rendered PDF (pages 6, 7, 8, 18, 20), including column order. This covered every row of Tables 1, 4, 6 and 7, the MPE/Uniform column pairing of Table 5, and Table 8 rows 0 and Uniform. Recomputed all 16 Table 3 cells as (P4 - P0)/4 from Table 2; all agree.
- Descriptive records: datasets (Appendix A.1, Section 4.2), protocols (Sections 4.2, 4.3, 5.3, Appendices C and D), methods and configurations (Appendices B, C, F), claims (Section 3, Section 6, Appendix E, Software and Data). Nothing found that the source does not state.

#### Rulings

1. **The 12 `row_not_found` rows.** Confirmed. They are Table 1 GEARS (gene frequency 4 and 20) and Table 6 Linear (gene frequency 10). In the text layer the frequency label starts the line, e.g. `4   GEARS   16.6 (19.8)  5.4 (3.4)  13.0 (11.6)  13.5 (16.1)`. The rendered Table 1 and Table 6 show the same values in the Norman, Simpson, Horlbeck K562, Horlbeck Jurkat order. Locators keep the printed model label; no change.

2. **Endpoint.** Agree: its own protocol, a recovery proxy, not hit yield. Appendix D: "We concatenate the predictions on the unseen data with the unmasked measured values from the seen data, and call this combined set ... X_i ... Let P_i = |X_i,P ∩ Y_i,P|". A pair counts when the model ranks it in the top 200, whether or not it was measured, so this is not the number of strong pairs among those tested and not the AssayLoop quantity. `true-positive-count` with denominator 200 on the protocol is correct. Note for the judgement stage: Table 8's caption calls the same counts "True Positive Rate (TPR)"; they are counts out of 200. Added to the source limitations.

3. **Uniform as the matched random comparator.** It is a matched random-acquisition control, not the use case's model-free random-selection baseline. Section 5.3: "we started with the same uniformly sampled gene pairs for all acquisition functions"; Section 4.3 fixes the per-round budget; Appendix C.5: "Uniform sampling: α = β = 0". Candidate pool, seed set, budget and model are matched, but the count is still NAIAD's measured-plus-predicted ranking, so it measures NAIAD trained on random pairs, not the yield of testing random pairs. Keep it as a NAIAD (and RECOVER) configuration, do not link it to `tgtval-20261009-method-random-selection` (whose score is the yield of the randomly chosen items themselves), and write no baseline record. The judgement stage may cite MPE against Uniform as an acquisition-against-random-acquisition contrast under this proxy endpoint, saying that it is not the "Random candidate selection" baseline in the use case's collection plan.

4. **Tables 2/3 against Table 4.** Keep Table 2/3 as its own group with `comparison.aggregation` null. Table 2 prints integers with no error and no run count ("Number of top 200 gene combinations correctly discovered at round 4 of active learning."), while Table 4 prints means with "Error is SE across three cross-fold replicates", and they differ by more than rounding (MPE, Horlbeck Jurkat: 161 against 150.0 (4.0)). The null aggregation blocks automatic comparison with Table 4, which is right. Table 2/3 is the only source of the Uncertainty acquisition row and the marginal gain, and the text's headline claims ("over twice as many strong perturbations using MPE sampling compared to uniform sampling", "(Table 2)") cite it. Table 4 is the comparison evaluation.

5. **Cross-table conflicts and `evidence_concerns`.** None added. An evidence concern on this source would block every result and every positive use-case judgement that cites it (`shared/omics/use-cases.ts`, `cleanSource`). The differences do not justify that:
   - Table 2 against Table 4, Table 5 against Table 4, and Table 8 beta 0 against Table 4 MPE: no caption says these repeat one run, and the formats differ (integers against SE means; ensemble sizes 1 to 7 against an unstated size). They are separate runs. Table 8 beta 0 is close to Table 4 MPE in three datasets (Simpson 145.7 against 141.7, K562 99.0 against 99.7, Jurkat 152.3 against 150.0) and 4.7 lower on Norman.
   - Table 8 Uniform on Norman (93.3 (2.9)) shares Table 4's mean but its other three cells differ from Table 4 (69.0, 39.0, 80.3 against 70.3, 38.7, 81.3), so it is a separate run.
   - Table 7 round 4 against Table 4 on Norman is the one same-quantity disagreement: NAIAD MPE (143.0 (1.5)) and RECOVER MPE (138.7 (2.7)) agree exactly, NAIAD Uniform is 93.7 (0.7) in Table 7 and 93.3 (0.7) in Table 4. One cell is probably a transcription slip. It is 0.4 of a count, smaller than the printed SE, and does not change any comparison (NAIAD MPE 143.0 against Uniform about 93). Recorded as a limitation on both evaluations and in the result review notes, not as a concern. The Table 8 beta 0, Table 7 round 0 and Table 8 TPR wording points were also added to the source limitations; the extractor's notes mentioned beta 0 but the source record did not.
   This differs from the `gfm2-20261011-datta2026` precedent, where a duplicated cell could change a model comparison. If a later reviewer weighs the Table 7/Table 4 slip more heavily, the concern belongs on the source record with locator "Table 4, row 'NAIAD Uniform', column 'Norman'; Table 7, row 'NAIAD Uniform', column 'Round 4'".

6. **Table 7 round 4 duplicating Table 4.** Keep both. Table 7 is the only source of rounds 0 to 3 and of GEARS with MPE, and Table 4 is the only full grid; removing either breaks a table. The two shared Table 7 evaluations (NAIAD MPE, RECOVER MPE on Norman) now carry a limitation saying round 4 is probably the same run as Table 4 and is not an independent replicate. Their `adaptation` strings also differ ("NAIAD; MPE acquisition" against "NAIAD ensemble; MPE acquisition"), so automatic comparison will not put them in one panel. The judgement and summary stages should cite Table 4 for round-4 values.

7. **Table 3 metric.** Acceptable as `count` with the qualifier "(P_4 - P_0)/4" and unit_detail "top-200 gene pairs per round". The store already files non-integer derived counts under `count` (migration row "mean total fusions identified,count"). The values cannot be compared with anything else because the qualifier is unique and the evaluations have aggregation null. Add a dedicated concept only if a second source reports a per-round gain.

8. **Origins.** Confirmed. The authors are Qin, Wessels, Fernandez-Granda and Hao; RECOVER is Bertin et al. 2023 and GEARS is Roohani et al. 2023, and Appendix B says the NAIAD authors adapted both ("We adapted RECOVER for gene perturbations"; for GEARS "we generated synthetic Pertub-seq datasets"). `independent_paper` is right for those. Linear and MLP are defined in Appendix B by the same authors, so `author_reported` with `reported_configuration` (a comparator configuration as reported) is right.

9. **RMSE scale.** Confirmed. The column header reads "Dataset RMSE (×10−2)". Keeping `numeric_value` at the printed scale with unit_detail "printed x 10^-2" follows the 425 "printed x100" results in the store.

#### Changes made to the part

- All 399 records: `status` set to `source_checked`; review blocks replaced with this review.
- Limitations added to six evaluations: Table 7 NAIAD MPE, RECOVER MPE and NAIAD Uniform on Norman; Table 4 NAIAD Uniform on Norman; Table 8 Uniform and beta 0 on Norman.
- Three source limitations added: Table 8 beta 0 against Table 4 MPE, Table 7 round 0 against the implied Table 2/3 P0, and the TPR wording in Table 8's caption.
- No value, locator, metric or link changed.

#### Remaining gaps

- The rendered check was by eye, not a second deterministic parse of a different layer.
- The NAIAD repository and the RECOVER and GEARS papers were not read.
- Figures 3 to 9 and the drug-combination results remain unextracted.

## Song et al. 2025, Virtual CRISPR (BioNLP 2025)

Extractor: Claude (Opus 5.5) extraction agent; no human review claimed. Nothing in this part is reviewed, added to the store or committed.

### Source

- Song S, Abdrabou A, Dabholkar A, Day K, Dharmoju P, Perera J, Kindratenko V, Khan AA. "Virtual CRISPR: Can LLMs Predict CRISPR Screen Results?" BioNLP 2025, pages 354-364, 1 August 2025. DOI 10.18653/v1/2025.bionlp-1.30.
- Artifact: `https://aclanthology.org/2025.bionlp-1.30.pdf`, retrieved 2026-10-22T13:57:26Z, SHA-256 `6c53ffec88444768fbb5c1a65031c096f07b3d9ac48de8163bc8f47d0d51205c`. Kept with its `pdftotext -layout` text layer in the session scratchpad, not in the repo.
- Licence: the ACL Anthology landing page says material from 2016 onwards is CC BY 4.0.
- Code and data: `github.com/czbiohub-chi/immune-llm-acl` (Ethics Statement). Not pinned to a commit and not read in this pass.

### What was extracted

Part file `parts/song2025virtualcrispr.jsonl`: 210 records. 1 source, 3 datasets, 2 protocols, 2 methods, 13 new models, 30 configurations, 31 evaluations, 124 results and 4 claims. Script `extract/song2025virtualcrispr.py` parses the text layer and asserts every row label and count.

- Table 1 (Simple Benchmark, prompted LLMs): all 18 rows by F1 and FPR. That is 17 models plus the random baseline, giving 36 results.
- Appendix Table 8 (Simple Benchmark, GPT-4o for each prompting strategy, plus Random): all 11 rows by 6 columns. The 10 GPT-4o rows give 60 results. Random's F1 and FPR repeat Table 1 exactly, so they are recorded once, with a `source_occurrences` entry for the Table 8 cell. Its other four columns give 4 more results.
- Table 2 (Difficult Benchmark): 3 rows by 8 columns, giving 24 results. GPT-4o's AUROC and AUPRC cells print "N/A". They are stored as results with `numeric_value` null and the caption's reason in `undefined_reason`.
- Tables 3 and 4 (benchmark composition) and Table 7 (model versions) are on the dataset, model and configuration records, not stored as results.

Consistency check, not stored: the mean of Table 8's ten GPT-4o F1 values is 0.472 and of their FPR values 0.223. These match Table 1's GPT-4o row (0.47 and 0.22), so Table 1 is the mean of the Table 8 rows for GPT-4o.

### Decision 1: selection endpoint or classification only?

**Classification only.** No budgeted selection endpoint and no top-k yield or enrichment.

- The task is a yes/no answer for each query: "Does {perturbation method} of {gene} in {cell line} causally result in {phenotype}? The answer is binary" (Section 2.2).
- "Performance is primarily assessed using the F1 score and False Positive Rate (FPR)" (Section 4.1). Table 2 adds AUROC, AUPRC, PPV, NPV, sensitivity and specificity. Nothing is ranked, no shortlist is drawn and there is no test budget.
- The candidates are not a library. Only genes with a statistically significant effect in either direction are queried. Table 3's "Genes" column is "after filtering for those with a significant effect", and a no-hit is a significant effect in the opposite direction (Section 2.2). Genes with no effect, which make up most of a screen, never appear. So the task is to predict the direction of a known effect, not to find hits in a library.
- The random comparator is a classifier, not random selection at a budget: "predicts 'hit' or 'no-hit' outcomes randomly, with the probabilities of predicting 'hit' weighted by the overall proportion of actual 'hits'" (Appendix A.2). It is printed only for the Simple Benchmark. Table 2 (Difficult) has no random row. Because the Difficult labels are balanced 907/907, an uninformed classifier would score about 0.5 there, but the paper prints no such value.
- The authors name the limitation themselves: "The current prediction task is framed as a binary 'hit/no-hit' classification" (Limitations). In vitro validation of predictions is listed as future work.
- The stated purpose and what is measured differ. The abstract says prediction would help with "prioritizing experiments", and Section 5 proposes flagging robust hits the model misses as novel biology. Neither is evaluated. I recorded this as the claim `pheno-20261022-claim-song2025-stated-purpose`.

### Decision 2: does it belong in the store, and for this use case?

**In the store, as evaluations.** It does not support this use case beyond a proxy.

- docs/collection.md section 1 puts in scope systems "scored on a task with a molecular or omics endpoint". Prompted LLMs and an LLM-embedding classifier predicting CRISPR screen hit labels meet that, as AssayBench did. The tables are complete, the versions are printed (Table 7), and the paper is peer-reviewed workshop work. A bare method claim would drop 124 printed values that the store can hold under its usual metric concepts.
- For `use-case-phenotype-perturbation-selection`, my reading for the judgement stage is this. The endpoint is per-query classification of pre-filtered, already-significant genes, with no selection step, no budget and no matched random selection. At most it is a weak proxy for "would the model's prediction point the right way", and more likely `outside_scope` for the use case's question. I did not write the judgement. That belongs to the later stage.
- Two features limit any comparison even as a proxy:
  - Simple and Difficult are different tasks and are never scored with the same systems except GPT-4o.
  - The headline embedding classifier (F1 0.84) appears only on the Difficult Benchmark. That benchmark has two screens from two papers, both in mouse cells, and every gene appears once in each phenotype direction with opposite labels (Table 4: 881 + 881 and 26 + 26 = 1,814 queries).
- The Youden's J threshold for the embedding classifier is "binarized using Youden's J statistic" (Section 4.2). The paper does not say whether it was chosen on the validation set or on the test set. If it was chosen on the test set, F1, FPR, PPV, NPV, sensitivity and specificity for Raw Emb. and Summ. Emb. are optimistic. AUROC and AUPRC are not affected. This is recorded as a limitation on the Difficult protocol.

### Decision 3: shared ground truth and leakage with AssayBench and AssayBench-Loop

Record both of the following if all three are linked to this use case.

- **Shared truth set.** All three take hit labels from the original authors' own significance calls as harmonised by BioGRID-ORCS. Virtual CRISPR uses ORCS v1.1.16. The stored AssayBench datasets say "built from the 2025 BioGRID ORCS release and 19 recent publications". The 20261022 search notes say AssayBench-Loop draws on the same screens. Agreement among the three is therefore not independent evidence: they share the same label source, its curation choices and any errors in it. They are three tasks over one truth set, not three confirmations.
- **Training leakage, Virtual CRISPR embedding classifier.** It is trained on 1,678 ORCS v1.1.16 human and mouse screens, covering about 22.6 million gene-level results (Section 3). If that classifier were ever scored on AssayBench or AssayBench-Loop test screens drawn from ORCS, the screens could be in its training data. The store has no such cross-evaluation now, so this is a caution for later linking, not a current defect.
- **Within the paper.** The authors kept the classifier off the ORCS-derived Simple Benchmark and evaluated it only on the Difficult Benchmark, which "contains no data from BioGRID-ORCS" (Section 3). The paper does not say whether the four Simple screens were removed from the training set. That does not matter for the printed results, because the classifier is never scored on them. I recorded it as a missing-metadata note on the training dataset.
- **Overlap between benchmarks.**
  - Simple Benchmark: screens 1837, 1835 and 1733 are in human cells, and 1885 is in J774 mouse macrophages.
  - AssayBench: the stored records describe it as human CRISPR screens. The three human Simple screens could therefore be AssayBench entries. The paper cannot tell us, and I did not check the AssayBench screen lists.
  - Difficult Benchmark: both screens are in mouse cells (NG2-3112 glioblastoma and 3LL Lewis lung carcinoma), so they cannot be AssayBench entries if AssayBench is human-only.
  - AssayBench-Loop: I have not checked its species filter.
- **Pre-training exposure for prompted LLMs.** The Simple screens are public ORCS records whose source papers predate the model cutoffs, so the prompted models may have seen them. The Difficult screens were chosen to post-date "the training cutoffs of all evaluated LLMs" (Section 2.1). The Difficult publications are October and November 2024 (PMIDs 39385035 and 39567689). The GPT-4o snapshot is gpt-4o-2024-11-20. The paper asserts the cutoff ordering but does not print each model's cutoff date.

### Record choices

- **Model identity.** Where the store already has a record with no version (GPT-4o, o1-mini and GPT-3.5-Turbo from tgtval-20261009; Llama-3.1-8B from tgtval-20261009; Llama 3.1 70B from egfrnsclc-20261009), I reused it and put the Table 7 version on the configuration in `version` and `model_version`.
  - GPT-4: the store's `rare-ranking-20261009-model-gpt-4` is pinned to `gpt-4-1106-preview`, while this paper used `gpt-4-0125-preview`. I created a new record.
  - New models: 8 Llama checkpoints (Hugging Face IDs from Table 7), o1, GPT-4o mini, GPT-4 Turbo, GPT-4 (0125-preview) and text-embedding-3-large.
  - New model IDs carry `song2025` to avoid clashing with other parts written in parallel. The merge stage may want to fold them into shared IDs.
- **Model descriptions.** The new models' one-line descriptions describe the model line from general knowledge, not from this source. Each `provenance_note` says so.
- **Origin.** Prompted third-party LLMs are `independent_paper`, with a limitation saying Song et al. ran a model they did not build, following the AssayBench pattern. The embedding classifier and the random baseline are `author_reported`.
- **Random baseline.** I created a new method and configuration and did not reuse `tgtval-20261009-method-random-selection`, which draws genes from a pool each round. That is a different procedure. I did not create a `baseline` record.
- **Protocols.** There are two, Simple (Tables 1 and 8) and Difficult (Table 2), because the datasets and allowed systems differ. The Table 1 rows are mean-over-strategy configurations, and their aggregation is in `comparison.aggregation`. The Table 8 rows are per-strategy configurations. Every `metric_qualifier` is just "Simple Benchmark" or "Difficult Benchmark", so the aggregation field is what separates a mean from a single strategy.
- **Uncertainty.**
  - Table 1 "±" is `standard_deviation` across prompting combinations; the caption says "mean and std. dev.". The number of combinations per model is not printed: it is "up to 10", and smaller for the o1 family, which had no explicit chain-of-thought prompts (Appendix A.1).
  - Table 2's GPT-4o "±" line is `unresolved_spread`, because the caption does not name the statistic.
  - Table 8 and the embedding rows print no uncertainty.
- **Budget.** `comparison.budget` is null on every evaluation. There is no budget concept in this task.
- **Units.** F1, FPR, PPV, NPV, sensitivity and specificity use `fraction`, because the values are printed on a 0 to 1 scale. AUROC and AUPRC use `unitless`, following the store's majority.

### Gaps

- The GitHub repository was not pinned or read. The benchmark query lists, prompts and predictions behind the tables were not checked.
- The paper does not say whether the random baseline is one draw or an expectation, and gives no seed.
- The paper does not say whether the Youden's J threshold was set on validation or test data.
- I did not check whether the three human Simple screens (ORCS 1837, 1835 and 1733) are AssayBench or AssayBench-Loop entries.
- Figures 1 and 2 are conceptual diagrams with no values.

### Review

Reviewer: Claude (Opus 5.5) review agent, independent of the extractor; no human review claimed. Reviewed 2026-10-22. No review.json, no store add, no repin and no commit in this step.

#### Source and method

- Re-downloaded `https://aclanthology.org/2025.bionlp-1.30.pdf` on 2026-10-22. SHA-256 `6c53ffec88444768fbb5c1a65031c096f07b3d9ac48de8163bc8f47d0d51205c` matches the source record. The regenerated `pdftotext -layout` text layer is byte-identical to the extractor's.
- `batch.py check-values` on the part alone: first run, all 124 `locator_not_parsed`, because the locators used single quotes and "Appendix Table 8". After normalising the locators, all 124 are `row_not_found`. The checker cannot read this layout: Table 1 is in the right-hand text column, so no line starts with the row label, and Tables 2 and 8 print their captions below the rows, while the checker only searches below the caption. The final report is `review/song2025virtualcrispr-value-check.tsv`. The merge stage will see the same 124 `row_not_found`. That is a limit of the checker, not a value problem.
- Replacement check: `review/song2025virtualcrispr_verify.py` is a separate parser written for this review. The extractor script was not imported or run. It finds each table by its header, asserts the header and row labels, splits the cells by column, and compares every result's printed value, numeric value, uncertainty, metric-to-column mapping, linked configuration, Table 7 version and protocol. Result: 124 of 124 ok, 0 identity problems (`review/song2025virtualcrispr-verify.tsv`).
- Manual check: I rendered Tables 1, 2 and 8 from the PDF and compared them by eye with the parsed rows, including which column each Table 2 "±" value sits under. Cells read directly from the image:
  - Table 1: o1 (0.16 ± 0.02, 0.03 ± 0.00), Llama-3.2-3B, GPT-4-turbo, Random Baseline.
  - Table 2: Summ. Emb. AUPRC 0.69, GPT-4o NPV 0.23 ± 0.13.
  - Table 8: 2-shot (-/+) N sensitivity 0.53, 1-shot (-) N specificity 0.91, Random NPV 0.63.
- Internal consistency:
  - In every Table 2 and Table 8 row, FPR equals 1 minus specificity.
  - In Table 8, F1 recomputed from PPV and sensitivity agrees to within 0.015.
  - The ten Table 8 GPT-4o rows have mean F1 0.472 and mean FPR 0.223, with standard deviation 0.063 to 0.066 (F1) and 0.058 to 0.061 (FPR). This matches Table 1's GPT-4o row (0.47 ± 0.06, 0.22 ± 0.06).
- Edits are made by `review/song2025virtualcrispr_apply.py`. It is idempotent. The part's SHA-256 was `892dc268da3d3db8c662550c3a8a47f19c53f03bab153552cc3a8fe15eafd96b` before the edits and `19c584343b28b68d295a5d2f1b2d1faea41e192a39d3dca1bb59c451d9ed3f8f` after.

#### Corrections made in the part

- Locators: rewritten to the documented form, `Table N, row "…", column "…"`. Table 8 rows are named by their Model, Few-shot and CoT cells, for example `Table 8, row "GPT-4o 1-shot (-) Y", column "F1"`, so each row label is unique. The caption reads "Table 8:", not "Appendix Table 8".
- Training-set release: Section 3 says "From the BioGRID-ORCS database". It gives no release; v1.1.16 is stated only for the benchmark source (Section 2.1). I removed "v1.1.16" from the training dataset version, the training-data claim, the Simple-from-ORCS claim and both embedding configurations' `training_setting`, and added a `missing_metadata.version` note. The training-data claim now includes the initial pool of 1,924 screens.
- "Pooled" is not stated anywhere in the paper. I removed it from the `assay` fields of the Simple and Difficult datasets.
- Random configuration: the "(41.3% for the Simple Benchmark)" figure in `parameters` was the extractor's reading. I replaced it with the Appendix A.2 wording and a pointer to the new evidence concern.
- Random evaluation: `metric_implementation` said "Binary Yes/No answer extracted from generated text", which does not apply to a random classifier, so I corrected it. I also added three limitations: it is a classifier, not budgeted random selection; it is printed only for the Simple Benchmark; and the per-screen rate finding below.
- Embedding-classifier evaluations: `inputs` said "Natural-language question". The classifier actually takes embeddings of the four component texts (Section 4.2, A.3), so I corrected it. I added two limitations: the Youden's J threshold, and its training on ORCS hit calls.
- Simple dataset: added to the `positives` note that the Table 3 hit counts sum to 485 of 1,175, which matches the printed 41.3%. The value itself stays missing because the paper does not print a total.
- I filled the `review` block on all 124 results and 4 claims, and set all 210 records to `source_checked`.

#### New finding: the random baseline fits per-screen hit rates

Appendix A.2: the baseline predicts a hit with probability "weighted by the overall proportion of actual 'hits' in the specific benchmark dataset being evaluated".

- With one pooled rate (485/1,175 = 0.413), the expected PPV, sensitivity, F1 and FPR are about 0.41, and specificity and NPV about 0.59.
- With each screen's own rate (Table 3: 140/423, 139/343, 76/243, 130/166), the expected sensitivity, PPV and F1 are 0.47, FPR 0.37, and specificity and NPV 0.63.
- Table 8 prints sensitivity 0.46, PPV 0.47, F1 0.47, FPR 0.36, specificity 0.64 and NPV 0.63. These match the per-screen expectation.
- A single draw at the pooled rate would need sensitivity about 2 standard errors above expectation and FPR about 3 below, both at once.

So the baseline very probably uses each screen's hit rate. That is information nobody has before running the screen, and it makes the baseline stronger than the methods text implies. I recorded this as an `evidence_concerns` entry on the source. The values are kept. The expected values are my own calculation from Table 3 and are not stored as results.

#### Rulings

1. **Endpoint.** Confirmed: binary hit/no-hit classification of pre-filtered, already-significant genes, with no ranking, budget, top-k yield or random selection.
   - Source text: "The answer is binary: 'Yes' (hit) or 'No' (no-hit)" (2.2). "'No' (no-hit) signifies a statistically significant effect in the opposite direction" (2.2). Table 3 and Table 4 count genes "after filtering for those with a significant effect". "The current prediction task is framed as a binary 'hit/no-hit' classification" (Limitations).
   - The embedding classifier's AUROC and AUPRC are the only ranking-type numbers, and they rank the direction of known effects in two mouse screens. They are not a ranking over a candidate library.
   - The use case's decision is "Allocate a fixed experimental budget to perturbations most likely to produce the prespecified phenotype", and its output is "a ranked experimental shortlist". Neither is measured here.
   - My reading for the judgement stage: `outside_scope`. If it is linked at all, it is a weak proxy, and the judgement must say that there is no budget and no candidate pool, and that the genes were already known to have a significant effect. The judgement stage makes the final call.
2. **Random comparator.** Confirmed: it should not be treated as the matched random-selection comparator the use case asks for.
   - Source text: "predicts 'hit' or 'no-hit' outcomes randomly, with the probabilities of predicting 'hit' weighted by the overall proportion of actual 'hits'" (A.2). Table 2's rows are Raw Emb., Summ. Emb. and GPT-4o (prompting); there is no random row.
   - It classifies every query, so it draws no shortlist at a budget, and it exists only for the Simple Benchmark, on which the embedding classifier is never scored.
   - The per-screen finding above makes it weaker still as a selection comparator.
   - It does not close the use case's gap: "No machine-learning method has been compared with random selection on the same data".
3. **Origin.** Confirmed.
   - Prompted third-party LLMs are `independent_paper`. Song et al. built the prompts and the benchmark, not the models (A.1, Table 7). This is the same pattern as the stored AssayBench evaluations ("Reported by the benchmark's authors for a system they did not build").
   - The embedding classifier is the authors' own ("we developed a novel embedding-based classification framework", 4.2), and so is the random baseline (A.2). Both are `author_reported`.
4. **Model reuse.** Confirmed.
   - Reusing the version-free store records is right: `tgtval-20261009-model-gpt-4o`, `-o1-mini`, `-gpt-3-5-turbo` and `-llama-3-1-8b`, and `egfrnsclc-20261009-model-llama-3-1-70b`. The Table 7 strings sit on the configurations, and my parser checked all 17 against Table 7. Table 7's alias "GPT-3.5" is the same model as Table 1's "GPT-3.5-turbo" (gpt-3.5-turbo-0125).
   - A new record for GPT-4 is right. `rare-ranking-20261009-model-gpt-4` is pinned to gpt-4-1106-preview, and Table 7 prints "GPT-4 gpt-4-0125-preview". The other GPT-4 record, `reported-model-91d4548437068f`, is a per-paper record with status `excluded` and cannot be reused.
   - The `song2025` IDs are acceptable. The merge stage may fold them into shared IDs.
   - Table 7 prints `meta-llama/Llama-3-8B-Instruct` and `meta-llama/Llama-3-70B-Instruct`. I kept these as printed and did not check them against the Hugging Face repository names.
5. **Random row stored once; Table 2 N/A cells.** Accepted.
   - Table 1 and Table 8 print 0.47 and 0.36 for Random in both places. Storing them once with `source_occurrences` follows store precedent.
   - The N/A cells are stored with `numeric_value` null and an `undefined_reason` quoting the caption: "GPT-4o prompting gives binary outputs and thus AUROC and AUPRC are undefined". `undefined_reason` is already used in the store.
6. **Uncertainty.** Confirmed.
   - Table 2's GPT-4o "±" line is `unresolved_spread`. The caption says only "results aggregated across prompting strategies", and Section 4.2 prints "F1=0.35±0.17" without naming the statistic.
   - Table 1's "±" is `standard_deviation`. The caption says "Results (mean and std. dev.) are aggregated across up to 10 combinations", and the Table 8 recomputation above agrees.
   - n is not printed per model. A.1 says "For OpenAI's 'o1' family of models, explicit CoT prompts were omitted", so o1 and o1-mini have fewer combinations.
7. **Youden's J.** Keep it as a limitation, not an `evidence_concern`. I added it to both embedding evaluations as well as the Difficult protocol, so it sits next to the values.
   - Source text: "Predicted probabilities are binarized using Youden's J statistic" (4.2). The validation set is "used for tasks such as early stopping and hyperparameter tuning" (3). Neither passage says where the threshold was chosen.
   - Reason: the paper is silent, not contradictory. The threshold-free metrics, AUROC 0.89 and AUPRC 0.86, are unaffected. With 1,814 balanced queries, choosing the threshold on the test set could inflate F1 only modestly, which cannot account for the 0.84 versus 0.35 gap to GPT-4o.
   - The store's evidence concerns cover printed values that contradict each other or the methods. This case does not meet that bar.
8. **Shared ground truth and leakage.** Confirmed, with two corrections to the brief's wording.
   - Source text: "considering only results deemed statistically significant ('Hits') by the original study authors" (2.2). The stored AssayBench datasets say "built from the 2025 BioGRID ORCS release and 19 recent publications".
   - Shared truth set: if Virtual CRISPR, AssayBench and AssayBench-Loop are all linked, the judgement and summary must say they are three tasks over largely one truth set (ORCS-harmonised author hit calls), not independent confirmations.
   - Correction 1: the classifier is trained on 1,678 of 1,924 human or mouse ORCS screens, after excluding screens with effects in both directions. That is not all screens, and the training release is not stated.
   - Correction 2: future scoring on AssayBench would be leaked only for screens that are in both sets. AssayBench's post-cutoff cohort and its 19 publications may not be in the training set. Any such scoring needs a screen-level overlap check, and I added that as a limitation on both embedding evaluations.
   - The Difficult screens are mouse, so they cannot overlap human-only AssayBench.

#### Remaining gaps

- The GitHub repository (`czbiohub-chi/immune-llm-acl`) is still unpinned and unread. The per-screen random-rate reading could be confirmed there.
- I did not check whether ORCS v1.1.16 contains the two Difficult-Benchmark publications, or the release dates of the models' training cutoffs.
- The model descriptions come from general knowledge, as their `provenance_note` says, and were not checked against a source.

## Use-case record, judgements and summary

Author: Claude (Opus 5.5) judgement agent in the evidence-pass workflow; no human review claimed. Nothing here is reviewed. Part file `parts/use-case.jsonl` (5 records), built by `extract/use-case.py` from the stored use-case and summary records and the three reviewed parts.

### Records

| ID | Kind | Status | Relevance |
| --- | --- | --- | --- |
| `use-case-phenotype-perturbation-selection` | use_case (updated copy) | source_checked, unchanged | |
| `use-case-mapping-phenotype-20261022-edwards2026-assaybench-loop` | judgement | needs_review | proxy |
| `use-case-mapping-phenotype-20261022-qin2025-al-top200` | judgement | needs_review | proxy |
| `use-case-mapping-phenotype-20261022-qin2025-downsampling-rmse` | judgement | needs_review | outside_scope |
| `use-case-summary-phenotype-perturbation-selection` | summary (updated copy, revision 2) | needs_review | |

### Use-case record

Changed: three `assessed_by` links, `evidence_gaps`, `search_terms` (four added), `collection_plan.next_step` and `evidence_checked` (date and cutoff 2026-10-22; the ledger and the dated review the finalise stage will write at `docs/reviews/use-cases/phenotype-perturbation-selection-2026-10-22.md`). None of these is pinned.

Not changed: status, name, description, facets and every decision field. The script asserts this. Those fields are pinned by the two CPPC judgements and the baseline claim, so setting the use case to `needs_review` would withhold all three until a repin. The record's `review` block, which describes the 2026-09-30 curation, is also left as it was.

Gap replaced: "No machine-learning method has been compared with random selection on the same data in the linked evidence." Once the AssayBench-Loop judgement is active this is no longer true, so it is replaced by a narrower gap: the matched random comparisons are retrospective only. Four further gaps are added: no prospective matched-budget comparison, no independent replication, the nature of retrospective hits and possible pre-training exposure, and the limits of the combination evidence.

### Judgements

**AssayBench-Loop, proxy.** The protocol has the same candidate pool, screens and budget (10 rounds of 100 genes) for every policy, and a random policy on the same screens. That is the comparison the collection plan asks for. It stays proxy, as both the extractor and the source reviewer concluded, because:

- the screens are replayed with historical labels (Discussion: "remain to be validated prospectively in a live experimental loop");
- a hit is each screen's own significance call;
- test screens were filtered with a best-LLM performance floor (Methods 4.2);
- every row was run by the AssayLoop authors.

One limitation is new at this stage. The temporal split is against the training screens. The text layer contains no statement about whether the test screens' publications predate the language models' training data: searches for "cutoff", "contamination", "leak" and "memori" found nothing relevant. Headline metric: `hit-enrichment-factor`. That concept is proposed in `extract/edwards2026assayloop.metric-concepts.ttl` and must be in `data/vocab/metric.ttl` before the batch is added.

**NAIAD active learning, proxy.** This is the only stored evidence on combinations, and the use case's setting says combinations need their own protocol. It is proxy for three reasons. Appendix D counts a pair as found if it is in the top 200 of the measured-plus-predicted ranking. The truth set is the 200 largest viability effects in the same screen. The replay is retrospective. The Uniform arm is a random-acquisition control inside the model's pipeline, not the yield of testing random pairs, so the judgement says it is not the use case's random baseline. Constraints direct readers to Table 4 for round-4 comparisons, following the source reviewer's ruling. All 120 evaluations on the protocol are left in. None is excluded, because each one is an acquisition, round, ensemble or UCB-weight variant of the same selection task.

**NAIAD downsampling RMSE, outside_scope.** RMSE over all held-out pairs measures prediction accuracy, not which pairs to test. It is recorded so that the values are not read as selection performance, following the store's precedent for outside-scope protocols from a linked source. The source is clean, so the judgement can become active.

**Virtual CRISPR (two protocols): no judgement written.** Both protocols are binary hit/no-hit classification of genes already known to have a significant effect. There is no candidate pool, ranking under a budget or selection step, so neither bears on the use case. The extractor and the source reviewer both read it as outside scope. An `outside_scope` judgement was not written because the source carries an `evidence_concerns` entry (the random baseline appears to use per-screen hit rates). `deriveUseCaseInputs` withholds any judgement whose cited source has concerns, including outside-scope ones (`shared/omics/use-cases.ts`, the `cleanSource` blocker). The page would then show a permanently "held for review" mapping for a protocol that supplies no evidence. The reviewer may decide otherwise; see the questions.

### Summary

This is an updated copy of the stored summary, keeping its ID: revision 2, `needs_review`, with the review and pins removed. The CPPC sentences are the reviewed 2026-10-10 text, shortened. Each new number was matched to a part result:

| Number | Result ID |
| --- | --- |
| 4.9, 1.04, 18.6 | `ucpheno-20261022-result-edwards2026-random-{fh,ef,ess}` |
| 1.39, 4.81 | `...-claude-haiku-4-5-ef`, `...-gpt-5-6-sol-ef` (min and max EF of the ten labelled Base LLM rows) |
| 4.49 | `...-bpmf-greedy-ef` |
| 5.67, 27.7, 30.1 | `...-assayloop-gemini-3-1-pro-{ef,fh,ess}` |
| 99.1 | `...-prior-hit-ess` |
| 143.0, 141.7, 99.7, 150.0 | `pheno-20261022-qin2025-result-table4-naiad-mpe-{norman2019,simpson2023,horlbeck2018-k562,horlbeck2018-jurkat}-top200-round4` |
| 93.3, 70.3, 38.7, 81.3 | the matching `table4-naiad-uniform-...` results |

The CPPC range (0.452 to 0.566, 17 of 20 between 0.50 and 0.57) was rechecked against the 20 reviewed evaluations of the challenge 2 judgement. The design figures (20 screens, 10 rounds of 100 genes, top 200, four rounds) come from the protocol records, not from results.

The summary states that the prospective challenge (scores near the random expectation) and the retrospective replays (several-fold enrichment over random) point in different directions and cannot be compared directly. This is a cross-source disagreement worth following up, not a contradiction within one source.

### Not done

- No `reviewed_evaluations`, review blocks or pins. Those belong to the reviewer and the finalise stage.
- The baseline claim `use-case-baseline-phenotype-perturbation-selection` was not edited. Its rationale says no linked evidence scores random selection. That will be out of date once the AssayBench-Loop judgement is active, because the AssayLoop Random configuration belongs to the baseline method `tgtval-20261009-method-random-selection`.
- The BioDiscoveryAgent (`tgtval-20261009-protocol-roohani2025-hitratio-round5`) and Gupta et al. replication protocols already in the store also compare selection methods with random selection at a fixed budget. They are linked only to the target-validation use case. They were outside this stage's brief (protocols in these parts) and were not judged here.

### Review (2026-10-22)

Reviewer: Claude (Opus 5.5) use-case review agent in the evidence-pass workflow, independent of the agent that drafted the records above; no human review claimed. Edits are made by `review/use-case_apply.py`, which asserts the drafted text before changing it. No store command, repin or npm command was run.

Sources re-downloaded to the reviewer's scratchpad and re-hashed; all three match their source records (AssayLoop `adcaaa5b...ef28`, NAIAD `983b2da8...64eb`, Virtual CRISPR `6c53ffec...205c`). Text layers from `pdftotext -layout`.

What was checked:

- Use-case record against the stored copy, field by field. Only `links` (three `assessed_by` added), `evidence_gaps`, `search_terms`, `collection_plan.next_step` and `evidence_checked` differ. Status, name, description, facets and every decision field are byte-identical, so the pins held by the CPPC judgements and the baseline claim still match.
- Each judgement's evaluations: 53 on AssayBench-Loop and 120 on NAIAD active learning, every evaluation, configuration and result `source_checked`. These are listed in `reviewed_evaluations`. None is excluded.
- Every outcome number in the summary against a part result; the CPPC range against the 20 stored Challenge 2 results (0.4517 to 0.5656, 17 between 0.50 and 0.57).
- `shared/omics/use-cases.ts`: an outside-scope judgement must have no `reviewed_evaluations` (a non-empty list becomes "reviewed evaluation no longer eligible"). `cleanSource` withholds any judgement, outside-scope included, whose cited source has concerns. The summary is found with `find` on `field: summary`, whatever its status.

#### Rulings

1. **Use-case status.** Keep `source_checked`. "Status needs_review" in the brief applies to the new claims. The use case's pinned fields are unchanged, and setting it to `needs_review` would withhold the two CPPC judgements and the baseline for no change in meaning. The unpinned edits go through `records -- change` with the dated review.
2. **AssayBench-Loop: proxy.** Same pool (21,147-gene acquisition universe, Appendix A), same screens and budget, and a random policy. But the replay is retrospective ("remain to be validated prospectively in a live experimental loop", Discussion), hits are each screen's own calls, test screens passed a best-LLM floor (Methods 4.2: "a non-trivial LLM performance floor (AnDCG@100 ≥ 0.05 ...)"), and the authors ran every row. The pre-training limitation stands: the text layer has no statement on training cutoffs, contamination or memorisation. The reviewer appended the authors' own caveat (Appendix A: "rather than to represent an unbiased sample of all genome-wide CRISPR screens") to the screen-selection limitation. Small source inconsistency, not material: Methods 4.2 names the floor model "Gemini 3.1 Pro", Appendix A "Gemini-3-Pro".
3. **Headline metric.** Keep `hit-enrichment-factor`. It is the authors' primary metric ("Our primary metric", Methods 4.3) and is closest to the plan's outcome "hits per test budget". The random row adds little on EF, which the constraint already says, and points readers to FH (recall) and nAUC. The concept is needed for the 53 EF results anyway, so it must be added to `data/vocab/metric.ttl` whatever the headline. Note: `headline_metric` is published only inside `presentation`, which needs `comparison_group`. Neither judgement has one, so the field currently has no effect on the page.
4. **NAIAD active learning: proxy.** Agreed. Uniform is a random-acquisition control in the model's pipeline (Section 5.3: "we started with the same uniformly sampled gene pairs for all acquisition functions"; Appendix C.5: "Uniform sampling: α = β = 0"). The count is still the model's measured-plus-predicted ranking (Appendix D), so Uniform is not the use case's random baseline. Keep all 120. The Table 2/3 runs carry `comparison.aggregation` null, which blocks automatic comparison with Table 4, and they are the only source of the Uncertainty row and marginal gain. The one GEARS row (Table 7, Norman, MPE) is a run of the same task, and its synthetic-input caveat is in the limitations. Correction: the limitation "'strongest' is by magnitude" is not stated. Appendix D says "top P values", while MPE uses "the highest absolute predicted effects" (Appendix C). The reviewer rewrote it to say so.
5. **NAIAD downsampling RMSE.** Keep it as `outside_scope` with its link. This follows the five outside-scope precedents in the store, the source is clean, and it stops the RMSE values being read as selection performance. It has no `reviewed_evaluations`, as the code requires.
6. **Virtual CRISPR.** Agree: no judgement. Both protocols classify pre-selected significant genes, with no pool, budget or selection step. An `outside_scope` judgement would be withheld indefinitely by `cleanSource` because of the random-baseline evidence concern. Record this in the dated review.
7. **Summary ID.** Keep the same ID (revision 2). A new ID with `supersedes` would leave two `field: summary` claims on the use case, and `reviewedSummary` takes the first one it finds whatever its status, so the superseded copy could hide the new one. Reviewed and set to `source_checked` here. The finalise stage repins it after the judgements, so no release goes without it.
8. **Summary numbers.** All match results: 4.9, 1.04, 18.6 (random); 1.39 and 4.81 (min and max of the ten labelled Base LLM EF rows); 4.49 (BPMF); 5.67, 27.7, 30.1 (Gemini handoff); 99.1 (prior hit); 143.0, 141.7, 99.7, 150.0 and 93.3, 70.3, 38.7, 81.3 (Table 4 NAIAD MPE and Uniform). Corrections:
   - Two handoffs tie at EF 5.67 (Gemini-3.1-Pro and GPT-5.6 Sol, FH 27.7 and 27.6, %ess 30.1 and 29.4), so "that row" was ambiguous. The text now names the Gemini handoff.
   - Added the best-LLM screen-selection floor and the unaddressed pre-training exposure, the known truth-set biases the summary must name.
   - "Point in different directions" was descriptive but loose: CPPC ranks a candidate set already enriched by Challenge 1 nominations, so a near-random score there is not the opposite finding to genome-wide enrichment. It is now an explicit contrast with no direction claimed. The contrast says "the leading model-guided policies", because some NAIAD acquisition functions score below Uniform (RECOVER UCB on Horlbeck K562 and Jurkat).
   - The locator now adds the GPT-5.6 Sol handoff row and Methods 4.2 / Appendix A.
9. **Design figures.** Accepted. "Every number traceable to a result" covers outcome values. Design parameters (20 screens, 10 rounds of 100 genes, top 200, four rounds, after 2021) are traceable to the reviewed protocol and dataset records, and the stored CPPC summary already did the same with its submission and nomination counts.
10. **Baseline claim.** Revise it in this pass, not in a follow-up. Once the AssayBench-Loop judgement is active, the page would publish "No evidence linked to this use case scores it" next to an active comparison with a Random row. Its pins (use-case fields and the Roohani source) are not touched, so nothing withholds it, and the false sentence would ship. An updated copy is now in this part. Only the rationale and review changed; the value, `method_ids` and `source_ids` did not. The finalise stage must apply it with `records -- change` and include its ID in the repin list.
11. **BioDiscoveryAgent and Gupta et al.** Judge them against this use case in a follow-up issue. They are stored, reviewed retrospective single-gene comparisons with a random comparator at a fixed budget, so they bear on the comparison question. They were not in this pass's parts, and judging them needs their own source check.

#### Other observations, no change made

- The evidence gap "No matched-budget conventional/random prospective comparison ..." (CPPC era) and the new "No prospective comparison of a model shortlist against random or conventional selection at the same budget" overlap. Merging them is optional.
- `review/song2025virtualcrispr-value-check.tsv` has 124 `row_not_found` and no `in_row`. That belongs to the Virtual CRISPR source review. No judgement rests on it.

#### For the finalise stage

Repin these after `records -- add` and `records -- change`: `use-case-mapping-phenotype-20261022-edwards2026-assaybench-loop`, `use-case-mapping-phenotype-20261022-qin2025-al-top200`, `use-case-mapping-phenotype-20261022-qin2025-downsampling-rmse`, `use-case-summary-phenotype-perturbation-selection` (after the judgements) and `use-case-baseline-phenotype-perturbation-selection`. Add the five proposed metric concepts to `data/vocab/metric.ttl` before `records -- add`.
