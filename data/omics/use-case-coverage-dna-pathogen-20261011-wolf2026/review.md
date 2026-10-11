# Review: use-case-coverage-dna-pathogen-20261011-wolf2026, 2026-10-11

Reviewer: Claude (Opus 5.5) review agent `reviewer-path`, separate from the extracting agent `uc-pathogens`. No human review claimed. Source transcription is not reproduction. The full review, covering all five pathogen batches, is `docs/reviews/use-cases/pathogen-use-cases-2026-10-11.md`.

## Reviewer's report (verbatim)

| Batch | Verdict |
| --- | --- |
| `use-case-coverage-dna-pathogen-20261011-wolf2026` | Approved with corrections (W1 to W4) |

### Wolf et al. 2026

W1. Relevance of `use-case-mapping-dna-pathogen-20261011-wolf2026-diagnosis`: set `relevance` to `proxy` (question 4). Replace `rationale` with

`Diagnostic sensitivity of the Karius plasma cell-free DNA assay against blood-culture organisms at bloodstream infection onset matches the use case's inputs and endpoint (agreement with blood culture for plasma microbial cell-free DNA), measured prospectively in a second population. It is proxy evidence for the same reason as the Karius anchor: blood culture does not identify every infection, so this is agreement with culture, not sensitivity against all infections. The population is children and young adults with high-risk leukaemia, and Karius took part in processing and analysis.`

and in `reason` delete the sentence `The direct relevance is a proposal.`

W2. `dna-pathogen-20261011-wolf2026-protocol-specificity`: replace `protocol` with

`Proportion of evaluable control samples (no fever or documented infection in the 7 days before or after collection) in which mcfDNA-Seq detected no bacterium or yeast (moulds, viruses and parasites excluded a priori; Burkholderia cepacia excluded afterwards for possible local contamination), or no common bloodstream infection pathogen; with all positive tests and with the post-hoc 140 molecules per microlitre cut-off. 95% CIs as printed. The laboratory was masked to sample status.`

set `version` to `Table 3`, and replace `limitations` with `["Control samples come from the same high-risk leukaemia population and are not patients tested for suspected infection.", "The 140 molecules per microlitre cut-off was chosen post hoc by maximising Youden's index on the consolidated data."]`.

W3. Set `version` to `Table 2` on `dna-pathogen-20261011-wolf2026-protocol-prediction` and `dna-pathogen-20261011-wolf2026-protocol-diagnosis`.

W4. In the three Wolf judgements, replace the limitation `Karius provided testing and took part in processing, analysis and data management; one author is a Karius employee.` with `Karius provided testing and took part in sample processing and analysis, data management and manuscript review; one author (AAA) is a Karius employee and coinventor on a pending Karius patent, and two others report research or sequencing support from Karius.`

## Corrections applied

Applied by the extractor as the reviewer specified, before the batch was added to the store.

1. W1: diagnosis judgement relevance set to proxy, rationale replaced with the reviewer's text, and 'The direct relevance is a proposal.' removed from reason.
2. W2: protocol-specificity protocol text, version (Table 3) and limitations replaced with the reviewer's text.
3. W3: version set to Table 2 on protocol-prediction and protocol-diagnosis.
4. W4: the Karius involvement limitation in the three judgements replaced with the reviewer's text.
5. The service record's source_locator was merged into its access text, because services do not declare source_locator (found in the pre-review dry run).
6. All records set to source_checked. Each result, descriptive claim and judgement carries the reviewer's review block (method, reviewer, reviewer_note, date and note as specified; the extraction note moved to method_note). Each judgement lists the reviewer's reviewed_evaluations.
7. Corrections were applied in the extraction script under extract/, and batch.jsonl, claims.csv, coverage.json, sources.md and research.md were regenerated.

## Records after correction

- benchmark: 1
- claim: 4
- configuration: 2
- dataset: 2
- evaluation: 4
- protocol: 3
- result: 44
- service: 1
- source: 1
