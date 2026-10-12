# Review: use-case-coverage-dna-pathogen-20261011-hu2026, 2026-10-11

Reviewer: Claude (Opus 5.5) review agent `reviewer-path`, separate from the extracting agent `uc-pathogens`. No human review claimed. Source transcription is not reproduction. The full review, covering all five pathogen batches, is `docs/reviews/use-cases/pathogen-use-cases-2026-10-11.md`.

## Reviewer's report (verbatim)

| Batch | Verdict |
| --- | --- |
| `use-case-coverage-dna-pathogen-20261011-hu2026` | Approved with corrections (H1 to H3) |

### Hu et al. 2026

H1. Author overlap is understated. Eight of the listed authors (Hui Miao, Jianpo Zheng, Dongdan Zhang, Weiqing Guo, Peng Hu, Rui Han, Jing Wang and co-corresponding author Lifeng Li) are affiliated with Genskey Medical Technology (aff3), not one. Replace the string

`One co-corresponding author is affiliated with Genskey Medical Technology, a clinical mNGS provider; the article states that the authors declare no conflict of interest. The workflows are the authors' own, so the evaluations are author_reported.`

with

`Eight of the listed authors, including co-corresponding author Lifeng Li, are affiliated with Genskey Medical Technology (Beijing), a clinical mNGS provider; the article states that the authors declare no conflict of interest. The workflows are the authors' own, so the evaluations are author_reported.`

in `attributes.limitations` of all six evaluations (`dna-pathogen-20261011-hu2026-eval-{culture,cmt,crs}-{mgi,hdont}`) and of the three judgements (`use-case-mapping-dna-pathogen-20261011-hu2026-{culture,cmt,crs}`). Make the same change in `sources.md` ("Authorship and origin").

H2. The CMT reference uses discrepant analysis: qPCR or GeneXpert verification was run on sequencing-positive, culture-negative findings (19 NGS-positive and 17 TGS-positive findings confirmed, Results 'Diagnostic performance for clinical samples' paragraph 2). Append to `limitations` of `dna-pathogen-20261011-hu2026-protocol-cmt` and of `use-case-mapping-dna-pathogen-20261011-hu2026-cmt`:

`Discrepant analysis: confirmatory qPCR or GeneXpert was run on discordant sequencing-positive findings where residual BALF allowed (19 NGS-positive and 17 TGS-positive findings confirmed), so the CMT reference depends partly on the sequencing results and favours the sequencing workflows.`

H3. Append to `limitations` of `use-case-mapping-dna-pathogen-20261011-hu2026-crs`:

`The use case's exclusion of sensitivity against a composite or adjudicated reference was recorded for the Karius source's composite endpoint; this composite reference from a different source is recorded as proxy evidence only, because it is built partly from the scored workflows' own calls.`

No change to the 79.2% result (question 1 below).

## Corrections applied

Applied by the extractor as the reviewer specified, before the batch was added to the store.

1. H1: the Genskey authorship limitation on the six evaluations and three judgements now names eight authors including Lifeng Li, with the reviewer's text; sources.md updated.
2. H2: the discrepant-analysis limitation appended to protocol-cmt and the CMT judgement.
3. H3: the composite-reference limitation appended to the CRS judgement.
4. No change to the 79.2% result; its source_anomaly is kept (reviewer's answer 1).
5. claims.csv no longer lists the judgement claims, as in the other batches.
6. All records set to source_checked. Each result, descriptive claim and judgement carries the reviewer's review block (method, reviewer, reviewer_note, date and note as specified; the extraction note moved to method_note). Each judgement lists the reviewer's reviewed_evaluations.
7. Corrections were applied in the extraction script under extract/, and batch.jsonl, claims.csv, coverage.json, sources.md and research.md were regenerated.

## Records after correction

- benchmark: 1
- claim: 4
- configuration: 2
- dataset: 1
- evaluation: 6
- method: 1
- protocol: 3
- result: 108
- source: 2
