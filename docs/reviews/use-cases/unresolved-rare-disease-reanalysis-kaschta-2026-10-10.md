# Unresolved rare-disease reanalysis: independent review of the Kaschta et al. 2026 batch

Batch: `data/omics/use-case-coverage-reanalysis-kaschta-20261010/` (48 records). Use case: `use-case-unresolved-rare-disease-reanalysis` ("Which reanalysis methods find new diagnoses or reduce review effort when given the same updated information?").

Reviewer: a separate Claude review agent that did not extract this batch. No human review is claimed. Nothing was executed or reproduced; this is a check of transcription and relevance against the pinned source.

## Outcome

- The JATS XML re-downloads to the pinned SHA-256. It is not archived, because all rights are reserved, and the supplement was not downloaded.
- All 27 results come from prose. Each quoted phrase occurs in the cited paragraph, each printed value occurs in its phrase, and each numeric value matches. Every percentage that has a stated count recomputes.
- One result is disputed: the Talos total diagnostic yield printed as 41.9%, which contradicts its own sentence. The other 26 are `source_checked`.
- The 3 judgements pass with the relevance the collector recorded (1 direct, 2 proxy). They are `source_checked` with `reviewed_evaluations` and a review; pins are not set. Their limitations were tightened.
- Corrections, none of which changes a number:
  - the disputed result;
  - limitations on the Talos and manual evaluations;
  - the trio dataset description;
  - the protocol and judgement limitations.
- No case number, gene or variant is in any file of the batch.

## How the check was done

1. Downloaded the JATS XML into an empty directory. The supplement was not requested.
2. Numbered the paragraphs with a stdlib parser written for this review. Abstract paragraphs are counted in order; body paragraphs are the direct `<p>` children of each section, with tables and figures excluded. This reproduces the collector's locators. The extractor's scripts were not imported or run.
3. For each result, parsed the locator into section, paragraph number and quoted phrase. Asserted the phrase occurs in that paragraph and the printed value in the phrase, and compared the numeric value, with number words mapped to digits.
4. Read the cited paragraphs for meaning: arm, qualifier, unit, direction and denominator. Paragraphs that name cases were read with case numbers and gene symbols masked, and nothing from them was written to any file.
5. Recomputed percentages from the counts the text prints, and checked that the case categories after reanalysis sum to 377 in each arm.
6. Checked authorship against the Talos reference (ref. 13) and read the competing-interest and funding statements.
7. Dry run: `addBatch` into a scratch copy of the store, then `loadRecords` and `deriveUseCaseInputs` with the three proposed `assessed_by` links added to the scratch use case.

## Source and hash

| Source ID | Artifact | SHA-256 (re-downloaded 2026-10-10T06:11:15Z) | Matches record |
| --- | --- | --- | --- |
| `reanalysis-kaschta-20261010-source-kaschta2026` | medRxiv JATS source XML, v1 | `db4ed16a501eda14ba114f8693f39596b03d7afaeafa8adafa41d84d9a61f6bd` | Yes, also equal to the 2026-10-09 retrieval |

## Values checked

| Group | Results | Outcome |
| --- | --- | --- |
| Manual reanalysis of 219 cases (Abstract P3; Results 'Manual Reanalysis' P1 and P3) | 8 | All confirmed. 3 new P/LP and 2 new VUS give the 5 cases with new findings. After reanalysis: 161 P/LP, 50 VUS, 166 none, total 377. 161 of 377 is 42.7%. |
| Talos reanalysis of 219 cases (Abstract P3; Results 'Automated Reanalysis' P1) | 7 | 6 confirmed. After reanalysis: 161 P/LP, 49 VUS, 167 none, total 377. The total-yield value 41.9% is disputed (see Conflicts). |
| Singleton benchmark (Results 'Singleton Cases' P2 and P3) | 4 | All confirmed: 28 of 35 is 80.0%, 4 of 35 is 11.4%, 3 of 35 is 8.6%; 2 of 21 VUS |
| Trio benchmark (Results 'Trio Cases' P1 to P3) | 8 | All confirmed: 109 of 145 is 75.2%; 120 of 145 is 82.8%; 11 of 145 is 7.6%; 9 of 145 is 6.2% (twice); 3 of 145 is 2.1%; 4 of 145 is 2.8%; 6 of 43 VUS. The failure modes (4 + 3 + 9 + 9 = 25) equal the 21 in-scope misses plus 4 out of scope. |
| Total | 27 | 26 confirmed, 1 disputed |

Configurations, datasets and claims:
- Talos version 8.2.0 matches Methods 'Study Cohort' P3.
- The DRAGEN versions match Methods: v3.7.5 for the initial analysis; v4.2.4 for re-called small variants; v4.2 for SMN, STR and SV.
- The cohort split matches Methods 'Study Cohort' P2: singletons 29, 16 and 27; trios 129, 33 and 143; together 158, 49 and 170 of 377.
- Cohort P1 and the sequencing paragraph confirm the 660-day mean interval (range 208 to 1,208), the January 2022 to April 2023 recruitment and the mean 38x coverage.
- Both descriptive claims match their paragraphs.

## Conflicts, narrowed

1. **41.9% against 161 of 377 = 42.7%.** Results 'Automated Reanalysis' P1 reads "increased the number of cases with a P/LP finding from 158 to 161 (+0.8 percentage points; 41.9% total diagnostic yield), which is identical to the manual result". The sentence contradicts itself: 161 of 377 is 42.7%, the manual paragraph prints 42.7% for the same 161, and 41.9% is the initial yield (Abstract P3, Cohort P2, Discussion P1). I disputed this one result (`result-talos-total-diagnostic-yield`) rather than keep it as a limitation, because a page showing 41.9% for Talos beside 42.7% for manual would present a difference the source itself says does not exist. The printed value is kept and the review note gives the reason. No corrected result is added, because the source prints no Talos-specific 42.7%. The Talos count of 161 is stored and consistent. A disputed result only drops out of the evaluation's reviewed rows; the dry run shows the Talos evaluation still eligible through its other six results. The source as a whole is not unreliable, so no source concern is raised.
2. **8.6% in the text against 9.6% in the Fig. 2B legend.** Kept as a limitation; the stored 8.6% stands. 3 of 35 is 8.6%, and the text shares (11.4%, 8.6%, 80.0%) sum to 100% while the legend's (11.4%, 9.6%, 80.0%) sum to 101%, so the legend is the inconsistent value. This affects only `result-singleton-miss-conversion`; the limitation and review note say so.
3. **Mean against median Talos workload.** Kept as a limitation on `result-talos-candidates-per-case`. Results 'Automated Reanalysis' P1 ("On average") and Discussion 'Strengths and Limitations' P3 ("an average of only three") print a mean, and Discussion P1 prints "a median of approximately three". The stored value is the mean, which matches the `candidates-per-case` concept. It is a rounded number word, and the paragraph does not say whether it averages over the 219 reanalysis cases or the whole cohort. Both points are now in the limitations.

Further inconsistencies, noted and not stored:
- Methods 'Benchmarking of Automated Reanalysis' P1 gives 34 trio cases with VUS where two other paragraphs give 33. Now in the trio dataset's population text.
- The same Methods paragraph defines the detection rate per case, but the Results report per-variant concordance (28 of 35 variants). Now in the benchmark limitations.
- The manual no-finding change is printed as "-1.0%" where 4 of 377 is 1.1%. The stored value is the count, 166.

## Direct or proxy for the reanalysis comparison

**Decision: direct, with the unequal inputs stated as the second limitation.** Reasoning:

- The relevance scheme defines direct as measuring "the use case's endpoint on inputs of the kind the use case describes". The endpoint is new findings and review effort in a previously unresolved cohort. Both arms measure it on the same 219 cases, with the kinds of input the use case lists: original calls, updated phenotype and gene-disease evidence, and dated changes to calling and interpretation methods. Relevance grades how closely the protocol bears on the question, not how strong the evidence is.
- The use case already holds a direct judgement under the same condition. `use-case-mapping-20260930-342-3c7f6c5e1873` (the Talos programme) is direct, with the limitation "No equal-input refreshed conventional control". Grading Kaschta proxy for lacking equal inputs would be inconsistent with it. Kaschta is closer to the question than the programme judgement, since it compares two methods on the same cases.
- The unequal inputs do not answer the "same updated information" part. Manual reanalysis re-called the reads with DRAGEN v4.2.4 while Talos used the archived v3.7.5 calls. The arms also ran at different times: manual from October 2024 to December 2025, Talos once in October 2025. And Talos is scored against the manual result. The judgement now says in its second limitation that it does not meet that condition, and that a difference between the arms cannot be attributed to the method. The two evaluations carry different `comparison.inputs`, so they are never grouped for automatic comparison.
- How far the inequality matters can be narrowed. Talos recovered all three new P/LP cases from the archived calls, so none of the P/LP gains depended on re-calling. The one manual finding Talos did not return is attributed by the authors to sparse gene-disease evidence, not to calling. The manual arm had the advantage, and still the P/LP counts are equal.
- The exclusions hold. Nothing is counted as algorithmic improvement (second exclusion): the source and the judgement attribute the gains to updated calling, gene-disease evidence and literature (claim `claim-drivers-of-new-findings`). And a new classification is not treated as a confirmed diagnosis (third exclusion; already a limitation).

The two benchmark judgements stay proxy: recovering known findings is excluded as evidence of new yield (first exclusion).

## Origin per arm

| Evaluation | Origin | Basis |
| --- | --- | --- |
| Manual reanalysis | `author_reported` | The authors' own diagnostic workflow, which is also the reference. Added: Illumina, which makes DRAGEN and Emedgene, provided reagents, software licences and technical support and supported the study (Competing interests; Funding statement). |
| Talos reanalysis and the three benchmark evaluations | `independent_paper` | Talos is Welland et al. (ref. 13); none of its authors is among the eight named authors here (plus the Genom-RD consortium). The authors adapted the ingestion step to accept DRAGEN-annotated VCFs, which is now stated on the Talos evaluation. |

## Vocabulary: `review-time-per-case`

Approved as written. It is needed because `runtime` is defined as computation time. It follows `candidates-per-case`: a mean per case, with no external match. Its direction (`lower`) is right, and its definition makes the source's inclusions explicit and points to `runtime` for computation time. No other branch defines it.

## Judgements

| Judgement | Relevance | Evaluations reviewed | Outcome |
| --- | --- | --- | --- |
| `use-case-mapping-reanalysis-kaschta-20261010-manual-vs-talos` | direct | 2 | Pass. Added limitations: the equal-input condition is not met; effort units differ; timing differs; the scoring reference and what it implies; Illumina support. Yield and workload limitations rewritten. |
| `...-talos-singleton-benchmark` | proxy | 1 | Pass. Per-case against per-variant definition added |
| `...-talos-trio-benchmark` | proxy | 2 | Pass. As above |

None has `excluded_evaluations`. In the dry run each derives exactly its `reviewed_evaluations`, each is withheld only because pins are unset, and all ten existing judgements on the use case stay active.

## Approved use-case changes

Links and gaps only. No pinned field changes, so the existing judgements, including the direct programme judgement `use-case-mapping-20260930-342-3c7f6c5e1873`, are unaffected; the dry run shows them all active.

Add to `use-case-unresolved-rare-disease-reanalysis` `links`, each with relation `assessed_by`:

- `reanalysis-kaschta-20261010-protocol-manual-vs-talos-219-reanalysis`
- `reanalysis-kaschta-20261010-protocol-talos-singleton-benchmark`
- `reanalysis-kaschta-20261010-protocol-talos-trio-benchmark`

In `evidence_gaps`, the second and third entries (index 1 and 2) say nothing was imported from Kaschta et al. 2026. Replace them with these two entries:

> Kaschta et al. 2026 (medRxiv 10.64898/2026.05.16.26352295, version 1) is the only study found that compares two reanalysis methods by new findings on the same unresolved cases, and it prints its values only in prose. Its Table 1 is an image of individual variants, its supplement is per-patient data and was not read, and its licence reserves all rights, so the source is pinned by hash and not archived.

> In Kaschta et al. 2026 the arms did not receive the same updated information: manual reanalysis re-called the reads with DRAGEN v4.2.4 while Talos used the archived v3.7.5 calls, the arms ran at different times, and Talos was scored against the manual findings. Review effort was measured as analyst minutes per case for the manual arm and candidate variants per case for Talos. Its automated total yield is printed as 41.9% where 161 of 377 is 42.7%; that value is disputed and not shown.

The existing summary claim `use-case-summary-unresolved-rare-disease-reanalysis` says the preprint "is not included", which is no longer true once this batch is added. Its replacement text is below. Changing it is a reviewed change to that claim, followed by `npm run use-cases:repin` with this review. It is not a use-case field change.

## Evidence summary

Replacement text for `use-case-summary-unresolved-rare-disease-reanalysis`. Add `reanalysis-kaschta-20261010-source-kaschta2026` to its source IDs.

> No study gives two reanalysis methods the same updated information and compares their new diagnoses, so this evidence cannot show which method finds more. One preprint compares methods on the same unresolved cases: in Kaschta et al. 2026, manual expert reanalysis and the automated tool Talos were applied to 219 genomes without a prior pathogenic or likely pathogenic finding. The arms had unequal inputs: the manual arm re-called the original reads with a newer DRAGEN version while Talos used the archived calls, and Talos was scored against the manual findings, so findings only Talos might have made were not counted. Each arm added the same three pathogenic or likely pathogenic cases, taking the cohort from 158 to 161 of 377 cases (42.7%), and manual reanalysis classified two new VUS cases, one of which Talos returned. Manual review took a mean of 81 minutes per case and Talos returned about three variants per case on average, but no analyst time was printed for reviewing the Talos output, so the two effort figures cannot be compared. The numbers are small, from one centre with a high initial yield, and Illumina, which makes the manual arm's software, supported the study. The other printed comparisons measure review workload, or recovery of diagnoses that were already known. In the Solve-RD CNV reanalysis of unsolved exomes, three callers returned different numbers of calls for expert review: ExomeDepth 4205, ClinCNV 2782 and CoNIFER 862. These counts overlap where callers found the same CNV, thresholds differ by caller, and ClinCNV was developed by the study's first author. In 100,000 Genomes Project cases diagnosed after a new disease-gene association, the Exomiser developers' recommended flagging rule (phenotype score increase 0.2, variant score 0.8) flagged 31 of the 37 diagnostic variants and 23 other variants, while the loosest rule tested flagged all 37 and 182 others; the rules were chosen on these same cases. In the Talos developers' ACG trio cohort, strict phenotype filtering returned 403 candidate variants instead of 487 and recovered 164 known diagnoses instead of 177. The known diagnoses come from each cohort's earlier analysis, and Talos recovery counts only diagnoses its own calling pipeline could detect. Recall on known diagnoses is not new diagnostic yield, each comparison was reported by the developers of at least one method compared, and none is clinical validation.

| Number in the text | Record ID (prefix `reanalysis-kaschta-20261010-` unless stated) |
| --- | --- |
| 219 | `data-uksh-219-unresolved-genomes` (`patient_count`) |
| three, three (same) | `result-manual-new-plp-cases`, `result-talos-new-plp-cases` |
| 158 to 161 of 377 | `result-manual-plp-cases-after` and `result-talos-plp-cases-after` (161; their qualifiers give 158 before and 377) |
| 42.7% | `result-manual-total-diagnostic-yield` |
| two new VUS, one returned | `result-manual-new-vus-cases`, `result-talos-new-vus-cases-recovered` |
| 81 minutes | `result-manual-review-time` |
| about three variants | `result-talos-candidates-per-case` |
| 4205, 2782, 862; 31, 37, 23, 182; 0.2, 0.8; 403, 487, 164, 177 | Unchanged from the reviewed summary: `rare-reanalysis-20261009-result-demidov2024-*-total`, `rare-reanalysis-20261009-result-vestito2024-dh2-vs8-*` and `-dh1-vs1-*`, `uc-clinical-20260930-talos-acg-trio-*` |
| 2026, 100,000 | Publication year and project name |

## Privacy

The supplement (per-patient clinical data) was not requested. The XML was parsed as data. Results 'Manual Reanalysis' P1 and P2, 'Automated Reanalysis' P1 and 'Comparison' P1 name cases, genes and variants. They were read only with case numbers and gene symbols masked, and nothing from them entered any file. A scan of every file in the batch folder found no case number, patient number or gene symbol from those paragraphs. The scratch download was deleted after the review.

## Remaining gaps

- No equal-input comparison of reanalysis methods exists in the evidence.
- Table 1 (an image), the figures and the supplement were not read.
- Per-case confirmation of the new findings is in the supplement and was not checked.
- `npm test` (500 passed) and `npm run typecheck` passed. `npm run build` was not run, by instruction; the dry run stands in for the store checks.
