# Perturbation selection for a defined cellular response: evidence refresh, 2026-10-22

Use case `use-case-phenotype-perturbation-selection`, refresh issue [rewire-benchmark-data #184](https://github.com/rewire-bio/rewire-benchmark-data/issues/184). Batch `data/omics/use-case-refresh-phenotype-20261022`. Cutoff 2026-10-22. Previous dossier: [2026-10-07](phenotype-perturbation-selection-2026-10-07.md).

Actors: Claude (Opus 5.5) agents in the evidence-pass workflow, one per stage (search, extraction per source, independent source review per source, use-case judgement, judgement review, finalise). No human review is claimed. No model was run. Values are transcribed from the sources, not reproduced.

## Outcome

- Three sources extracted and reviewed: AssayLoop / AssayBench-Loop, NAIAD and Virtual CRISPR. 1,279 new records (866 results, 224 evaluations, 114 configurations, 23 models, 18 methods, 17 claims, 7 datasets, 5 protocols, 3 sources, 1 baseline, 1 dataset subset).
- Three new relevance judgements on the use case: AssayBench-Loop (proxy), NAIAD active learning top-200 (proxy) and NAIAD downsampling RMSE (outside scope). The two CPPC judgements are unchanged.
- Three existing records changed: the use case (new `assessed_by` links, evidence gaps, search terms, collection plan, evidence date), the baseline claim (rationale) and the summary claim (revision 2). Their reviewed copies are in the batch's `changes.jsonl`.
- Five metric concepts added to `data/vocab/metric.ttl`: `hit-enrichment-factor`, `normalized-cumulative-hits-auc`, `effective-number-of-groups`, `vendi-ratio`, `annotation-overlap-ratio`. None respells an existing concept; no STATO, QUDT or EDAM match was confirmed.
- The gap "no machine-learning method compared with random selection on the same data" is replaced by a narrower one: the matched random comparisons are retrospective only. No prospective matched-budget comparison was found.

## Sources and hashes

| Source record | Artifact | SHA-256 |
| --- | --- | --- |
| `ucpheno-20261022-source-edwards2026` | arXiv:2609.11877v1 PDF | `adcaaa5b7f9bd0e3bc1f91d94d26c8d4924c5c0b3064b6625c01ba92c6eaef28` |
| `pheno-20261022-qin2025-source-pmlr` | PMLR 267 `qin25g.pdf` | `983b2da8aed78f0aced27053301c15f0f67ebd0fac706435bb6800e309dd64eb` |
| `pheno-20261022-source-song2025` | ACL Anthology `2025.bionlp-1.30.pdf` | `6c53ffec88444768fbb5c1a65031c096f07b3d9ac48de8163bc8f47d0d51205c` |

Each PDF was re-downloaded by its reviewer and matched the source record. The AssayLoop digest also matches the 2026-10-07 dossier. None of the PDFs is archived in the batch. AssayLoop and Virtual CRISPR are CC BY 4.0; the NAIAD PDF prints no reuse licence. Values were checked against `pdftotext -layout` text layers of these PDFs.

## How values were compared

**AssayLoop (530 results).** `batch.py check-values` on the pre-review part, rerun after the review edits with identical output: 470 `in_row`, 60 `row_not_found`, all other statuses 0. The 60 are the last six Supplementary Table 4 Ablations rows, which sit beyond the script's 80-line caption window. A separate reviewer parse (`review/edwards2026assayloop-check.py`) resolved every locator to one cell by group, row label, preceding row and column position and matched 530 of 530 values. A seeded sample of 36 results (seed 20261022) and every Supplementary Table 4 block, including the 60 overflow results, were checked by eye against rendered PDF pages 8 and 31, column order included. Outputs: `review/edwards2026assayloop-value-check.tsv`, `review/edwards2026assayloop-independent-check.tsv`.

**NAIAD (212 results).** `check-values`: 200 `in_row`, 12 `row_not_found` (Table 1 GEARS x8 and Table 6 Linear x4, where the gene-frequency label starts the line). All 12 were confirmed by hand. A separate reviewer parse (`review/qin2025naiad-check.py`) mapped results to cells through the evaluation links and qualifiers rather than locators: 212 of 212 match on printed value, numeric value and SE, with 0 locator inconsistencies. Rendered pages 6 to 8, 18 and 20 were compared by eye, including column order. All 16 Table 3 cells were recomputed as (P4 - P0)/4 from Table 2 and agree. Outputs: `review/qin2025naiad-value-check.tsv`, `review/qin2025naiad-independent-check.tsv`.

**Virtual CRISPR (124 results).** `check-values` on the part alone: first run 124 `locator_not_parsed` (single-quoted locators, "Appendix Table 8"). After the locators were normalised to the documented form, 124 `row_not_found`, 0 `in_cell`, 0 `in_row`. The cause is layout, not values: Table 1 sits in the right text column, and Tables 2 and 8 print their captions below the rows. A replacement column-aware parser (`review/song2025virtualcrispr_verify.py`) found 124 of 124 correct on value, numeric value, uncertainty, column, linked configuration, Table 7 version and protocol. Tables 1, 2 and 8 were also rendered and checked by eye. Outputs: `review/song2025virtualcrispr-value-check.tsv`, `review/song2025virtualcrispr-verify.tsv`.

The per-source notes, with every ruling and correction, are in the batch's `notes.md`.

## Rulings on questions raised in the pass

1. **AssayLoop Random row.** Stored as a configuration of `tgtval-20261009-method-random-selection` and as a baseline with `baseline_type` `null_control` (the scheme has no `random` concept). Table 1 caption: "Random is an instantiation of the random policy, not an expected value". The draw is noted on the configuration, evaluation and baseline. The source does not say whether it samples from the full gene universe or the screen library; the extractor's "over the candidate pool" was removed.
2. **AssayLoop metrics.** EF, nAUC, the EP scopes, the Vendi ratio and pathway overlap need the five new concepts. EF is "the ratio between the number of hits found and the expected number of hits under random selection" (Methods 4.3, eq. 3). FH maps to `recall` and SF and %ess to `proportion`. Directions follow Table 1's arrows; %ess, EP, Vendi and pathway overlap print none and are `unknown`.
3. **EP-B, EP-S, EP-D.** Extracted, each with its own qualifier. The caption says the three scopes are not comparable with each other, not that methods are incomparable within a scope. The Table 1 caption says every metric is averaged per screen, while Appendix H pools EP-D over the test set ("M = 6000 across the complete test set"). The qualifier follows Appendix H and each EP-D result notes the conflict. It was not raised as an `evidence_concern`, because a source concern would block every comparison from the source over one breadth diagnostic.
4. **One protocol for Table 1 and Supplementary Table 4.** Same runs, screens, budget and metrics; the caption says "See full results in Supplementary Table 4". All shared cells are identical and four repeated S4 runs are identical, so each run is one evaluation. The label-ablation rows share the protocol's inputs: Appendix K, "we simply omit the hit labels while preserving the history of previously acquired genes".
5. **AssayLoop origin.** Third-party LLMs and algorithms run by the AssayLoop authors (BPMF, MAML, BioBO, Probability-of-Hit, LLMNN, ICBR-EF, Transformer + DAgger, the Haiku-4.5 coding agent) are `independent_paper`, as for the stored AssayBench evaluations. AssayFormer, AssayLLM, the handoffs and the authors' own baselines are `author_reported`. Correction: RF (greedy) and RF + UCB are uncited and undescribed row labels, so they were changed to `author_reported`. BioBO and Probability-of-Hit are the AssayLoop authors' runs, not those papers' results; both papers remain retrieval gaps.
6. **AssayLoop dataset subset.** The `same_data_as` link to the AssayBench test set was removed. Methods 4.2 selects 20 screens from the post-2021 pool against stated criteria, so it is not the same data.
7. **NAIAD endpoint.** Its own protocol, a recovery proxy. Appendix D counts a pair as found if it is in the top 200 of the measured-plus-predicted ranking. Table 8's caption calls these counts "True Positive Rate"; they are counts out of 200, noted on the source.
8. **NAIAD Uniform.** A matched random-acquisition control inside the model's pipeline (Section 5.3: "we started with the same uniformly sampled gene pairs for all acquisition functions"; Appendix C.5: "Uniform sampling: α = β = 0"), not the use case's random-selection baseline. It is not linked to the random-selection method and has no baseline record.
9. **NAIAD Tables 2/3 against Table 4.** Separate runs: Table 2 prints integers with no error, Table 4 means with "Error is SE across three cross-fold replicates", and they differ by more than rounding (MPE, Horlbeck Jurkat 161 against 150.0). Table 2/3 keep `comparison.aggregation` null; the judgement and summary cite Table 4 for round-4 comparisons.
10. **NAIAD cross-table slip.** Table 7 round 4 and Table 4 on Norman agree for NAIAD MPE and RECOVER MPE but not for NAIAD Uniform (93.7 against 93.3, SE 0.7). It is smaller than the SE and changes no comparison, so it is a limitation on the affected evaluations, not an `evidence_concern`.
11. **Virtual CRISPR endpoint and judgement.** Binary hit/no-hit classification of genes already known to have a significant effect ("The answer is binary: 'Yes' (hit) or 'No' (no-hit)", Section 2.2). There is no candidate pool, budget or ranked shortlist, so neither protocol bears on the use case. No judgement was written. An `outside_scope` judgement would be withheld indefinitely by `cleanSource` because of the source's evidence concern (item 12).
12. **Virtual CRISPR random baseline (evidence concern added).** Appendix A.2 weights the random baseline by "the overall proportion of actual 'hits' in the specific benchmark dataset". Table 8's printed values (sensitivity 0.46, PPV 0.47, FPR 0.36, specificity 0.64, NPV 0.63) match the expectation from each screen's own hit rate (Table 3), not the pooled 41.3%. Values are kept and the source carries the concern.
13. **Virtual CRISPR corrections.** Locators rewritten to the documented form; "v1.1.16" removed from the training release (Section 3 names only "the BioGRID-ORCS database"); "pooled" removed from the assay fields; the random evaluation's implementation and the embedding classifier's inputs corrected; Youden's J threshold choice recorded as a limitation, not a concern.
14. **AssayBench-Loop judgement: proxy.** Same 21,147-gene universe, screens and budget for every policy, and a random policy. Proxy because the replay is retrospective ("remain to be validated prospectively in a live experimental loop", Discussion), hits are each screen's own calls, test screens passed a best-LLM floor (Methods 4.2, "AnDCG@100 ≥ 0.05"), every row was run by the authors, and the paper says nothing about whether the models saw the screens' publications in training. Headline metric `hit-enrichment-factor`.
15. **NAIAD judgements.** Active learning top-200: proxy, all 120 evaluations kept. Downsampling RMSE: `outside_scope`, so the RMSE values are not read as selection performance.
16. **Use case kept at `source_checked`.** Only unpinned fields changed; status, name, description, facets and decision fields are byte-identical, so the CPPC judgement pins still hold.
17. **Summary kept at the same ID (revision 2).** A second `field: summary` claim could hide the new one. Every outcome number was matched to a batch result, and the CPPC range was rechecked against the 20 stored Challenge 2 results (0.4517 to 0.5656).
18. **Baseline claim revised in this pass.** Its rationale said no linked evidence scores random selection, which is false once the AssayBench-Loop judgement is active. Value, `method_ids` and `source_ids` are unchanged.

## Changes made at finalising

`records -- add` rejected four attribute forms in the reviewed parts. They were fixed in `batch.jsonl` before the receipt was written; no value, locator or link changed:

- `pheno-20261022-data-song2025-orcs-training`: the `version` text duplicated its `missing_metadata.version` reason (release not stated), so `version` was omitted.
- `ucpheno-20261022-protocol-edwards2026-assaybench-loop-test-10x100`: `heldout_test` and `heldout_validation` wrapped as one-item lists; `uncertainty_reporting` split into `printed`, `runs` and `note` with the same content.
- 55 records: `missing_metadata` keys sorted, the form the attribute normaliser writes (`tests/attributes.test.ts`, "leaves current records unchanged").

## Conflicts found

- The prospective CPPC challenge scored near a random ordering, while both retrospective replays show the leading model-guided policies above their random or uniform arm. They differ in endpoint, candidate set, setting and who ran them. The summary states the contrast without claiming a direction. This is a lead for follow-up, not a contradiction within one source.
- AssayLoop Figure 5 prints EP-S 46.7 for AssayLoop where the tables print 46.6. The table value is stored and the gap noted.
- AssayLoop Methods 4.2 names the floor model "Gemini 3.1 Pro", Appendix A "Gemini-3-Pro".

## Remaining gaps

- No prospective comparison of a model shortlist against random or conventional selection at the same budget.
- No independent replication of AssayBench-Loop or NAIAD.
- AssayLoop Figures 4 and 6, per-screen results and Supplementary Table 2 were not extracted; uncertainty and run counts are unreported.
- NAIAD figures 3 to 9, drug-combination results, its repository and the RECOVER and GEARS papers were not read.
- Virtual CRISPR's repository (`czbiohub-chi/immune-llm-acl`) is unpinned; it could confirm the per-screen random rate.
- BioBO and Probability-of-Hit papers are retrieval gaps.
- BioDiscoveryAgent and the Gupta et al. replication, already stored under the target-validation use case, also compare selection with random at a fixed budget. Judging them against this use case is left to a follow-up issue.
