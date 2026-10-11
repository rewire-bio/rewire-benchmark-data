# Review: use-case-coverage-rna-pathogen-20261011-sanderson2026, 2026-10-11

Reviewer: Claude (Opus 5.5) review agent `reviewer-path`, separate from the extracting agent `uc-pathogens`. No human review claimed. Source transcription is not reproduction. The full review, covering all five pathogen batches, is `docs/reviews/use-cases/pathogen-use-cases-2026-10-11.md`.

## Reviewer's report (verbatim)

| Batch | Verdict |
| --- | --- |
| `use-case-coverage-rna-pathogen-20261011-sanderson2026` | Approved with corrections (S1 to S3) |

### Sanderson et al. 2026

S1. Relevance of `use-case-mapping-rna-pathogen-20261011-sanderson2026-validation`: set `relevance` to `proxy` (question 4). Replace `rationale` with

`A prospective validation of one RNA metagenomic workflow on respiratory swabs, scored as target-level sensitivity and specificity against the original clinical PCR, with thresholds fixed on a separate derivation set, matches the use case's inputs (nuclease-treated respiratory RNA, reverse-transcribed) and its output (sensitivity against original clinical testing for one respiratory mNGS assay). It is proxy evidence for the same reason as the UCSF anchor: agreement with the clinical PCR panel is not sensitivity against all infections, and samples were selected by PCR result. It compares detection criteria within one workflow, not different workflows.`

and in `reason` delete `; the direct relevance is a proposal`.

S2. Add two limitations the judgement misses (Methods 'Respiratory samples for pathogen detection' paragraph 1 and 'Procedures' paragraph 4). Append to `limitations` of the judgement and of `rna-pathogen-20261011-sanderson2026-protocol-validation`:

`Spectrum bias: inclusion required a pathogen detected at Ct or Cn 30 or below on the four-target assays, or FilmArray testing, with about one FilmArray-negative sample collected per eight positive samples; sensitivity and specificity are not estimates for unselected swabs.`

`Reads were mapped only to a curated database of the 23 PCR-panel pathogens, so the study does not measure detection of organisms outside the panel or false calls outside it.`

S3. On `rna-pathogen-20261011-sanderson2026-result-prespecified-specificity`, append to `source_anomaly`: ` Independent review 2026-10-11: both counts give 99.8%; the result-level note is sufficient and no source-level concern is raised.` On `rna-pathogen-20261011-sanderson2026-result-alternative-sensitivity`, append: ` Independent review 2026-10-11: 159/274 = 58.0% and 159/260 = 61.2% are each arithmetically consistent with the printed percentages; the 274 denominator appears to include the DNA targets that the 61% result excludes, and 'samples' in that sentence appears to mean targets. Kept as printed with this note.`

## Corrections applied

Applied by the extractor as the reviewer specified, before the batch was added to the store.

1. S1: judgement relevance set to proxy, rationale replaced with the reviewer's text, and '; the direct relevance is a proposal' removed from reason.
2. S2: the two limitations appended to the judgement and to protocol-validation.
3. S3: the reviewer's sentences appended to source_anomaly on prespecified-specificity and alternative-sensitivity.
4. All records set to source_checked. Each result, descriptive claim and judgement carries the reviewer's review block (method, reviewer, reviewer_note, date and note as specified; the extraction note moved to method_note). Each judgement lists the reviewer's reviewed_evaluations.
5. Corrections were applied in the extraction script under extract/, and batch.jsonl, claims.csv, coverage.json, sources.md and research.md were regenerated.

## Records after correction

- claim: 2
- configuration: 2
- dataset: 1
- evaluation: 2
- method: 1
- protocol: 1
- result: 14
- source: 1
