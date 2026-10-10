# Therapeutic target validation: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-target-validation-20261009/` (770 records). Use case: `use-case-therapeutic-target-validation`. `batch.jsonl` as extracted: SHA-256 `c0badedebb3c68116ddba4bab3d04a0d51b044997626f292849fe531db58b2ef`; as reviewed: `1af52376ee4df4f827fa2135664afe6ffb582631459162beacd17444ee3ef5f6`. The receipt is `review.json` in the batch folder.

Reviewer: a separate Claude review agent that did not collect or extract the batch. No human review is claimed. Nothing was executed or reproduced.

## Outcome

- The three PDFs re-download to their pinned SHA-256. By decision they are not archived in the batch, and each source record says so.
- All 439 results match their source cells. No value, printed value, metric, unit, direction, locator, configuration, protocol or dataset link was wrong, and the Schmidt1/Schmidt2 mapping is correct.
- No result is disputed and no evidence concern was raised.
- Corrections, none of which changes a printed or numeric value:
  - origin on 48 Roohani evaluations;
  - the uncertainty reason on 240 Roohani results;
  - the AssayBench Precision@100 qualifier;
  - the negative definition for AssayBench's secondary metrics;
  - two statements of the replication finding, one of them wrong;
  - an unsupported "CRISPRa" in two dataset names;
  - the comparison grouping;
  - smaller descriptive fixes.
- All 3 judgements stay `proxy` and are `source_checked` with `reviewed_evaluations`; pins are left unset.
- The two new metric concepts are approved as written.
- The use-case changes are approved, including the fourth exclusion. Exclusions are pinned, so both CPPC judgements need re-pinning; both still hold.

## How the check was done

1. Downloaded each artifact URL into its own empty directory, hashed it, and converted it with `pdftotext -layout` (poppler). Python ran with `-I` from scripts kept outside those directories.
2. Wrote a new parser (`check.py` in the review scratch area); the extractor's script was not imported or run.
   - **Roohani Table 1:** asserts the screen header, the `All N/E` header and the 20 row labels in order, and takes 12 three-decimal values per row.
   - **Gupta Tables 1 and 2:** asserts the column header and the ground-truth row (654, 920, 943, 924, 924, identical in both tables). It reads the three backbone blocks and checks that Table 2's BDA rows equal Table 1's.
   - **AssayBench Table 3:** asserts the header and 48 rows.
3. Matched every result to exactly one cell through its configuration's `reported_name`, its dataset (screen or cohort), its table and backbone block, and its scoring population. Compared printed value, numeric value, metric, unit, direction and locator.
4. Recomputed the cross-source conversion, the permuted-feedback counts, the reported-against-replicated gap and the AssayBench cohort changes, and read the definitions, conflicts sections and appendices cited by each record.
5. Ran the edited batch through `addBatch` (`scripts/omics/records.ts`) against a scratch copy of the store; all 770 records were accepted (SHACL not run). In the same scratch store I applied the use-case changes below and ran `deriveUseCaseInputs`.
   - Before re-pinning, both CPPC judgements are withheld ("pinned evidence changed since review").
   - After pinning all five judgements and the summary with `claimPins`, all five are active and the summary is published.
6. `npm test` (499 of 499) and `npm run typecheck` pass. `npm run build` was not run, by instruction.

## Sources and hashes

| Source ID | Artifact | SHA-256 (re-downloaded 2026-10-09) | Matches record |
| --- | --- | --- | --- |
| `tgtval-20261009-source-roohani2025` | arXiv:2405.17631v3 PDF, 3,953,768 bytes | `dd94d80ec75c9bb84ec3989c910a313ef1a7aec57c772d3dd35ecadd250132a7` | Yes |
| `tgtval-20261009-source-gupta2025` | ACL Anthology 2025.findings-emnlp.838 PDF, 475,883 bytes | `7dda0b590f2736b7d30e48b97167a0868a2b4bde253589d8aff7929d01506ff9` | Yes |
| `tgtval-20261009-source-debrouwer2026` | arXiv:2605.10876v1 PDF, 2,889,050 bytes | `805b402c28e0daa186415af202e04df56bf0cd7c7b1f872a6db170ee3c6c623d` | Yes |

## Values checked

| Source table | Results | Metric | Mismatches |
| --- | --- | --- | --- |
| Roohani Table 1 | 240 | recall (hit ratio), 20 methods, 6 screens, all genes and non-essential | 0 |
| Gupta Table 1 | 34 | true-positive-count (cumulative hits), three backbone blocks | 0 |
| Gupta Table 2 (Linear UCB, GP) | 20 | true-positive-count | 0 |
| AssayBench Table 3 | 144 | adjusted NDCG@100, Precision@100, dFDR@100, 16 systems, 3 cohorts | 0 |
| Total | 439 | | 0 |

Gupta Table 2's BDA rows equal Table 1's and are listed in `claims.csv` as duplicates, not stored twice. AssayBench Table 2 (test split) equals the Table 3 test rows. The 16 `NA` dFDR cells and Gupta's one `N/A` cell are stored with null numeric values.

## Collector's points

1. **"Reported Numbers" row as a conversion, origin `paper_compilation`.** Confirmed with one refinement. Each Reported Numbers value divided by Gupta's ground-truth count matches Roohani Table 1 (Claude 3.5 Sonnet, all genes) to three decimals: 68.01/654 = 0.104, 87.4/920 = 0.095, 39.6/943 = 0.042 and 60.72/924 = 0.0657 (printed 0.066). Gupta used values more precise than Roohani prints, since 0.066 x 924 = 60.98, not 60.72. So the row converts Roohani's results, not their printed table. The claim and the five results now say so. `paper_compilation` is right. Gupta prints `N/A` for Sanchez Down because Roohani had no such screen, so that cell's missing reason is now `unreported` rather than `inapplicable`.
2. **Re-run below the reported numbers.** Confirmed. Gupta's replication is lower on 3 of the 4 screens with a reported value (interleukin-2 59.4 against 68.01, interferon-gamma 78.8 against 87.4, tau 31.6 against 60.72) and higher on Carnevale (43.8 against 39.6). The Gupta protocol and judgement limitations said "lower counts on four of five screens", which is wrong; they now give the correct count. `research.md` had it right.
3. **Permuted feedback.** Confirmed, and wider than stated. BDA-Rand scores at least as high as BDA on 3 of 5 screens with each of the three backbones: Llama-3.1-8B (interferon-gamma, Sanchez, Sanchez Down), Qwen-2-7B (interferon-gamma, Carnevale, Sanchez Down), and Claude 3.5 Sonnet against the replicated row (interferon-gamma, Sanchez, Sanchez Down). The collector named two backbones. The source's own wording is that permuted labels have "no impact on performance" (abstract) and that Claude "maintains nearly the same performance" (section 5). The batch's "scores the same" overstated that slightly. The Roohani limitation, the claim and the proposed gap now say "about the same" and give the three-of-five counts.
4. **Schmidt1/Schmidt2 mapping.** Confirmed. The caption defines Schmidt1 as interferon-gamma and Schmidt2 as interleukin-2. The conversion in point 1 fixes the mapping independently, because a swap would give 0.095 x 654 = 62.1 against the printed 68.01. Both sources' results link to the same two dataset records, and the 70 affected results are on the right screens.
5. **Identical Gaussian process rows.** Confirmed: 147.8, 23, 22.2, 27.6 and 30 under both the Llama-3.1-8B and Qwen-2-7B blocks, although Table 2's caption says each method uses its backbone's embeddings. `source_anomaly` on those ten results is the right treatment; the values are kept.
6. **AssayBench Precision@100.** Confirmed: Precision@k divides by min(k, G+), where G+ is the number of positive-relevance genes (section 3.2). For a screen with fewer than 100 hits it is the fraction of the screen's hits recovered, not precision over 100 predictions, and the table reports a mean over entries that mixes both cases. I kept the concept `precision-at-100` and put the denominator in `metric_qualifier` on all 48 results. Comparisons require the same qualifier, so these values are never compared with fixed-denominator precision at 100 elsewhere in the store, which a scope note alone would not prevent. A separate concept would also be defensible; it is not needed to keep comparisons correct.
7. **Hit ratio as recall.** Faithful. Section 2 defines hit ratio as the cumulative set of selected hits divided by the set of all true hits, which is recall over the screen's hit set; the source calls it "similar to recall". The qualifier carries the round, the scoring population and the 10-run mean. No new concept is needed.
8. **No uncertainty from Roohani.** Roohani Appendix Table 7 prints the same values with one standard deviation over 10 runs, so the missing reason on all 240 Roohani results was wrong as `unreported`. It is now `unextracted`, with a note pointing to Table 7. Gupta and AssayBench print no uncertainty for these tables, so `unreported` stays there.
9. **Origin per row.**
   - **Roohani:**
     - BioDiscoveryAgent configurations and the authors' own Random and Human baselines stay `author_reported`.
     - The seven GeneDisco acquisition functions and DiscoBAX were developed by Mehrjou et al. 2021 and Lyle et al. 2023 (references and Appendix), none of whom is a Roohani author. Their 48 evaluations are now `independent_paper`, matching how the store treats third-party tools run by a paper's authors.
     - Two Roohani authors (Steinhart, Marson) are authors of the Schmidt et al. 2022 screens, and the CAR-T screen is unpublished.
     - The conflicts section says patent applications have been filed on the findings. It also lists interests for N.J.K., J.W.F. and A.T.S., who are not authors of this paper, which looks like text carried over from another manuscript. The relevant facts are now in the Roohani limitation and rationale.
   - **Gupta:** all independent of the agent's authors, except the converted row (`paper_compilation`).
   - **AssayBench:** all authors are at Genentech. Systems they built (fine-tuned GPT-OSS, GEPA prompts, the evolved ensemble, the gene-relevance predictor and the retrieval and frequency baselines) are `author_reported`. Third-party models and agents they ran are `independent_paper`. Biomni's reference truncates its author list, so overlap with AssayBench's authors could not be checked; it stays `independent_paper`.

## Negative definition on every protocol

- **Roohani and Gupta:** the candidate pool is the set of genes each screen assayed. The Roohani prompt names "18,939 possible genes" and Gupta says |C| > 18,000, with 1,061 perturbations for Scharenberg. A method cannot select an untested gene. Non-hits are assayed genes below the threshold. The exclusion holds.
- **AssayBench, headline metric:** a system may name any gene. For AnDCG@100, unassayed genes are removed before scoring (section 3.1, condensing step), so the exclusion holds for the judgement's headline metric.
- **AssayBench, secondary metrics:** as printed, the Precision@100 and dFDR@100 formulas (section 3.2) sum over the top-k list without the condensing step.
  - An unassayed gene in the top 100 adds nothing to Precision@100's numerator, so it is treated like a non-hit.
  - It also counts in dFDR@100's denominator k.
  - The prose calls these measures over "in-screen predictions", so whether they were condensed is unclear.
  - The batch said for all three metrics that unassayed genes "are removed rather than penalised", which the source states only for AnDCG@100. The protocol and judgement limitations, the three cohort datasets' scope notes and the judgement rationale now say so.
  - The AssayBench rationale also said unassayed genes are "excluded from the candidate pool", which describes Roohani and Gupta, not AssayBench; it is rewritten.

## Corrections made in the batch

The batch is not in the store, so fields were edited in place. No ID, link, source list, printed value, numeric value, metric, unit, direction or locator changed.

1. 48 Roohani evaluations: origin `author_reported` became `independent_paper` (point 9).
2. 240 Roohani results: `missing_metadata.uncertainty.reason` `unreported` became `unextracted` with a note (point 8).
3. 48 AssayBench Precision@100 results: `metric_qualifier` gained "; denominator min(100, positive-relevance genes)" (point 6). The protocol's `metric_definition` now says what the metric becomes for screens with fewer than 100 hits.
4. Gupta Sanchez Down Reported Numbers result: missing value reason `inapplicable` became `unreported` (point 1). The five Reported Numbers results gained a note on the conversion's precision.
5. Claims:
   - `...-claim-gupta2025-permuted-feedback`: adds the three-of-five counts for each backbone.
   - `...-claim-gupta2025-reported-numbers-conversion`: says the conversion used unrounded values.
   - `claims.csv` rows updated to match.
6. Datasets:
   - `...-data-schmidt2022-ifng` and `-il2`: names said "CRISPRa screen". Schmidt et al. 2022 report both CRISPR activation and interference screens, Roohani describes the data as knockdown, and neither benchmark says which was used. "CRISPRa" is removed and the scope note states this, plus the Steinhart and Marson authorship.
   - `...-data-scharenberg2023-choline`: a missing `total` note said the size is stated as "over 18,000 genes", contradicting its own population of 1,061 perturbations; removed.
   - The three AssayBench cohort datasets: scope notes limit the "removed rather than penalised" statement to AnDCG@100.
7. Configurations and models:
   - `...-config-debrouwer2026-oracle-knn`: description now says it uses the target screen's labels and is an upper bound, not a usable method (section 4.3). `research.md` said this was recorded; it was not.
   - Biomni A1, C2S-Scale and the LLM ensemble have `method_types: foundation_model` but had `foundation_model_eligible: false`, unlike every other foundation-model configuration in the batch; now `true`.
   - `...-model-gpt-oss-120b` and `...-model-qwen3-5-2b` are open-weights releases; `entity_level` `service` became `checkpoint`.
8. Limitations, identical between each protocol and its judgement:
   - **Roohani:** the permuted-feedback sentence (point 3), and the developer-run sentence (now with the screen authorship and the patent statement).
   - **Gupta:** the reported-against-replicated sentence (point 2).
   - **AssayBench:** the negative-definition sentence; the post-cutoff sentence; and a sentence on why the gene-frequency baseline is competitive (section 5.4). The post-cutoff sentence now gives the cohort size (19 against 334), says the source reads it as partly prior exposure, and names the two systems that score higher on it (gene-relevance predictor 0.0660 against 0.0565, Qwen3.5-2B 0.0324 against 0.0284).
   - **All three judgements gain:** "No linked benchmark here runs a prospective validation batch or measures target usefulness, dependency, tractability, therapeutic window or patient benefit."
9. Grouping: the three judgements were one group, `target-nomination-vs-screen-hits`, with three different headline metrics and units (recall as a fraction, cumulative hits as a count, adjusted NDCG). No existing group in the store mixes headline metrics, and the strata are not comparable. Each judgement is now its own group with one stratum:
   - `roohani2025-perturbation-design`: "BioDiscoveryAgent benchmark: hit ratio on six CRISPR screens (developer-run)";
   - `gupta2025-perturbation-replication`: "Independent replication: cumulative hits on five CRISPR screens";
   - `assaybench-screen-ranking`: "AssayBench: ranking 100 genes for described CRISPR screens (preprint)".

   Stratum labels and orders are removed.
10. Statuses: all 770 records `source_checked`. Every result's `review` records this review; the extractor's note is kept.

`coverage.json` and `research.md` are the collector's record and were not edited; the batch and this review supersede them where they differ.

## Relevance judgements

| Judgement (`use-case-mapping-target-validation-20261009-` prefix) | Relevance | Reasoning | reviewed_evaluations |
| --- | --- | --- | --- |
| `roohani2025-hitratio` | proxy | Retrospective replay on six screens, restricted pool, run by the agent's developers, and recovery of screen hits is not target usefulness. | 120 |
| `gupta2025-cumulative-hits` | proxy | Same task on five of the screens, independent, with the permuted-feedback control; bears on how the original numbers should be read. | 55 |
| `debrouwer2026-assaybench` | proxy | Broad screen-ranking benchmark, preprint, LLM-assisted curation; ranking a screen's hits is not target usefulness. | 48 |

No evaluation is excluded. Each group has one headline metric whose unit is constant within it.

## Vocabulary

Approved as written in `data/vocab/metric.ttl`.

- `adjusted-ndcg-at-100`: the definition matches section 3.1. NDCG at 100 is computed after removing unassayed genes, then rescaled by the screen's analytic random baseline so 0 is random and 1 ideal, and values below 0 are possible. `skos:broader :ndcg` is right, and the scope note correctly warns that it is not comparable with plain NDCG. Relevance here is graded and can be negative in bidirectional screens; the definition does not say so, but it does not contradict it.
- `directional-false-discovery-rate-at-100`: the definition matches the printed formula, (1/k) times the count of top-k predictions with negative relevance, defined only where the reference assigns a direction. The direction is lower, as it should be. The source's prose ("scored predictions") may mean a condensed list; that ambiguity belongs to the source and is recorded in the protocol limitations, not the concept.

Neither concept respells an existing one, and no STATO or QUDT term matches; none is claimed.

## Approved use-case changes

Changes to `use-case-therapeutic-target-validation`.

`links`: append `{"relation": "assessed_by", "target_id": ...}` for `tgtval-20261009-protocol-roohani2025-hitratio-round5`, `tgtval-20261009-protocol-gupta2025-cumulative-hits-round5` and `tgtval-20261009-protocol-debrouwer2026-screen-gene-ranking`.

`source_ids`: append `tgtval-20261009-source-roohani2025`, `tgtval-20261009-source-gupta2025` and `tgtval-20261009-source-debrouwer2026`. The collector left AssayBench off because it is a preprint. Preprint status is not a reason to omit a source the page relies on, and the use case's existing CPPC evidence is itself a preprint. All three must be `source_checked` with no `evidence_concerns`, or every positive judgement on the use case is withheld.

`attributes.citation_locators`: append

- `tgtval-20261009-source-roohani2025`: "Sections 2 and 4.1; Table 1; Conflicts of interest; see data/omics/use-case-coverage-target-validation-20261009/claims.csv"
- `tgtval-20261009-source-gupta2025`: "Abstract; sections 4.1 and 5; Tables 1 and 2; see data/omics/use-case-coverage-target-validation-20261009/claims.csv"
- `tgtval-20261009-source-debrouwer2026`: "Sections 2 to 5; Tables 2 and 3; see data/omics/use-case-coverage-target-validation-20261009/claims.csv"

`attributes.exclusions` (pinned): append, as the fourth entry, the collector's text unchanged:

> Recovering a published screen's own hits is not evidence that a nominated target is worth pursuing.

`attributes.evidence_gaps`: keep the six existing entries and append

1. The multi-method comparisons added on 2026-10-09 are retrospective replays of published screens, not prospective validation batches: a method selects genes and the screen's existing measurement is looked up.
2. An independent replication reports that the agent compared in Roohani et al. 2025 performs about the same when its experimental feedback is replaced by randomly permuted outcomes (at least as high on three of five screens with each of three backbones), so its margin over the baselines should not be read as learning from each round's results.
3. No benchmark found scores target nominations against a therapeutic window, selectivity, dependency or tractability, and none establishes patient benefit.
4. AssayBench reports lower scores for most systems on screens published after the models' training cutoff, which its authors read as partly prior exposure to the literature; that cohort has 19 screens, and two systems score higher on it.

Gaps 2 and 4 are edited from the collector's text. The collector said "scores the same" and "every system scores lower"; the second is false (point 3 and correction 8).

**The two CPPC judgements under the new exclusion.** Both still hold.

- `use-case-mapping-20260930-346-15b6eed3fb55` scores original Challenge 2 submissions against measured T-cell state objectives over the prospectively nominated Screen2 targets.
- `use-case-mapping-20260930-346-910458dfd409` counts prospectively nominated targets that improved the defined T-cell state.

Neither is a replay that recovers a published screen's own hits. Their `proxy` relevance, endpoints and limitations are unchanged by the new text, and nothing in it contradicts their rationale. Because `attributes.exclusions` is pinned, both are withheld until re-pinned, and the release guard would refuse a release that withholds a judgement the previous release served. Re-pin them in the same change:

```sh
npm run use-cases:repin -- docs/reviews/use-cases/therapeutic-target-validation-2026-10-09.md use-case-mapping-20260930-346-15b6eed3fb55 use-case-mapping-20260930-346-910458dfd409 use-case-mapping-target-validation-20261009-roohani2025-hitratio use-case-mapping-target-validation-20261009-gupta2025-cumulative-hits use-case-mapping-target-validation-20261009-debrouwer2026-assaybench use-case-summary-therapeutic-target-validation
```

## Evidence summary

Final text for `use-case-summary-therapeutic-target-validation` (`field` `summary`). Its `source_ids`: `tgtval-20261009-source-roohani2025`, `tgtval-20261009-source-gupta2025`, `tgtval-20261009-source-debrouwer2026`. It is descriptive and recommends nothing.

> Three sources compare target-nomination methods against measured CRISPR screen outcomes, and all three are retrospective replays of published screens: a method picks genes and the screen's existing measurement is looked up. Non-hits are genes the screen assayed that did not meet its criterion; genes a screen never assayed are outside the candidate pool or, in AssayBench's headline metric, removed before scoring, so these results say nothing about an untested target. Roohani et al. 2025 (ICLR) were run by the developers of the agent they test, two of whom are authors of two of the screens, and they state that patent applications have been filed on the findings. They report the fraction of each screen's hits found after five rounds of 128 genes. With Claude 3.5 Sonnet the agent reached 0.095 on the interferon-gamma screen, 0.104 on interleukin-2, 0.130 on CAR-T proliferation, 0.326 on lysosomal choline recycling, 0.042 on T-cell inhibition resistance and 0.066 on tau level, against random selection at 0.037, 0.031, 0.033, 0.160, 0.036 and 0.034. Conventional baselines were close on some screens: Coreset reached 0.102 on interleukin-2 and 0.047 on T-cell inhibition resistance, above the agent's 0.042 there. Gupta et al. 2025 (Findings of EMNLP), independent of the agent's authors, replayed five of the same screens and report cumulative hits. Their re-run of the Claude 3.5 Sonnet agent found fewer hits than the original numbers on three of four shared screens, for example 31.6 against 60.72 on tau level. Giving the agent randomly permuted feedback changed little: the permuted variant scored at least as high on three of five screens with each of the three backbones tested, for example 51 against 44 on interferon-gamma with Llama-3.1-8B, and the authors conclude that the models they tested do not perform in-context experimental design. Gaussian process optimisation over the same embeddings reached 147.8 hits on interleukin-2 against the agent's 39.4 with Llama-3.1-8B, from 654 ground-truth hits; the source prints identical Gaussian process values under both backbones. De Brouwer et al. 2026, a preprint that is not peer reviewed, asked 16 systems to rank 100 genes for each of 571 benchmark entries, each a described screen. On the 334 test entries the best system was an evolved ensemble of language models at 0.1631 adjusted NDCG@100 and the best single model, Gemini 3 Pro, 0.1570, against 0.1334 for a baseline ranking genes by how often they are hits in training screens of the same phenotype and 0.2918 for a retrieval upper bound that uses the answer. Most systems scored lower on the 19 entries published after the models' training cutoff, the ensemble falling to 0.1088, which that source reads as partly prior exposure to the literature. None of these sources tests a prospective validation batch, a target's usefulness, dependency, tractability or therapeutic window, or whether modulating a target benefits patients.

Traceability (all `source_checked`; prefix `tgtval-20261009-result-`):

| Statement | Record(s) | Printed |
| --- | --- | --- |
| Agent (Claude 3.5 Sonnet), six screens, all genes | `roohani2025-claude-3-5-sonnet-schmidt2022-ifng-all`, `-schmidt2022-il2-all`, `-cart-proliferation-all`, `-scharenberg2023-choline-all`, `-carnevale2022-tcell-all`, `-sanchez2021-tau-all` | 0.095, 0.104, 0.130, 0.326, 0.042, 0.066 |
| Random, same screens | `roohani2025-random-schmidt2022-ifng-all` and the five matching `roohani2025-random-*-all` | 0.037, 0.031, 0.033, 0.160, 0.036, 0.034 |
| Coreset, interleukin-2 and Carnevale | `roohani2025-coreset-schmidt2022-il2-all`, `roohani2025-coreset-carnevale2022-tcell-all` | 0.102, 0.047 |
| Replicated against reported, tau | `gupta2025-bda-replicated-claude-3-5-sonnet-sanchez2021-tau-hits`, `gupta2025-bda-reported-numbers-claude-3-5-sonnet-sanchez2021-tau-hits` | 31.6, 60.72 |
| Lower on three of four shared screens | the four `gupta2025-bda-replicated-claude-3-5-sonnet-*-hits` and `gupta2025-bda-reported-numbers-claude-3-5-sonnet-*-hits` pairs | (count) |
| Permuted at least as high on 3 of 5 per backbone | the 15 `gupta2025-bda-rand-*-hits` against `gupta2025-bda-llama-3-1-8b-*`, `gupta2025-bda-qwen-2-7b-*` and `gupta2025-bda-replicated-claude-3-5-sonnet-*` | (count) |
| Interferon-gamma, Llama | `gupta2025-bda-rand-llama-3-1-8b-schmidt2022-ifng-hits`, `gupta2025-bda-llama-3-1-8b-schmidt2022-ifng-hits` | 51, 44 |
| GP against agent, interleukin-2, Llama | `gupta2025-gp-llama-3-1-8b-schmidt2022-il2-hits`, `gupta2025-bda-llama-3-1-8b-schmidt2022-il2-hits` | 147.8, 39.4 |
| Ground-truth hits, interleukin-2 | `tgtval-20261009-claim-gupta2025-ground-truth-hits`; the `denominator` on the IL2 results | 654 |
| Ensemble, Gemini 3 Pro, gene frequency, Oracle kNN, test | `debrouwer2026-llm-ensemble-test-adjusted-ndcg-at-100`, `debrouwer2026-gemini-3-pro-test-adjusted-ndcg-at-100`, `debrouwer2026-gene-frequency-by-phenotype-test-adjusted-ndcg-at-100`, `debrouwer2026-oracle-knn-test-adjusted-ndcg-at-100` | 0.1631, 0.1570, 0.1334, 0.2918 |
| Ensemble, post-cutoff | `debrouwer2026-llm-ensemble-post-cutoff-adjusted-ndcg-at-100` | 0.1088 |

Entry counts (571, 334, 19) trace to the three AssayBench cohort dataset records. Non-numeric statements trace to Roohani's author list, the Schmidt et al. 2022 reference and the conflicts section; Gupta's abstract and section 5; and AssayBench sections 4.1 to 5.1.

## Remaining gaps

- Roohani Appendix Table 7 (standard deviations) was not extracted.
- Figures were not read. Gupta Table 3 (the authors' own hybrid) and the AssayBench appendix tables other than Table 3 were not checked.
- Biomni authorship overlap with AssayBench could not be checked from the pinned sources.
- Which Schmidt et al. 2022 screen (CRISPRa or CRISPRi) the benchmarks replay is not stated by either source.
- Whether AssayBench's Precision@100 and dFDR@100 were computed on condensed lists is not stated.
