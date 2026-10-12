# Review: lit-otheromics-20261011-pepspecbench, 2026-10-12

Reviewer: Claude review agent `reviewer-ro-2`, independent of the extractor `lit-rna-otheromics`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

Excerpts of `reviewer-ro-2`'s report that concern this batch, unedited.

Reviewer: Claude (Opus 5.5) research agent, reviewer-ro-2. No human review claimed. I did not extract any of these batches.

Every printed value in all four batches matches the source. All corrections are to metadata, origin notes, duplicates and judgement text. No numerical result needs a superseding record.

## lit-otheromics-20261011-pepspecbench: approved

There are no required corrections.

Answer to report question 5:
- The area `proteins-complexes` is acceptable. `metabolomics` is defined as small molecules and would be wrong here. A dedicated proteomics area is a vocabulary decision for the owner and is not needed for this batch.
- PredFull PROSPECT SA, printed 0.204 in Table 2 and 0.203 in Table 4, is a rounding difference of the Table 14 median 0.2035. The source limitation already records it. No evidence_concern is needed, and nothing needs superseding. In Table 2 the same rounding makes SAS + SA sum to 1.001 for that cell. Two Table 4 FastSpel pairs sum to 1.001 and 0.999 for the same reason.

Origin `independent_paper` is right. The authors (Yang, Liu, Li, Zhong, Xia; HKUST Guangzhou) developed none of the six models. They share four authors with FlexMS, which does not affect origin.

Optional P1: the source ID suffix `li2026` does not match the first author (Zhiwen Yang; Li is third). If the collector wants to fix it, rename it to `lit-otheromics-20261011-pepspecbench-source-yang2026` in every `source_ids` and in the ledger before `records add`. After the add, the ID is permanent.

## Vocabulary review by reviewer-ro-1 (verbatim)

Reviewer: Claude review agent (reviewer-ro-1), independent of the collector lit-rna-otheromics; no human review claimed.

- `data/vocab/metric.ttl`: `one-minus-overlap-ratio`, `spectral-angle-similarity` and `fingerprint-tanimoto-similarity` approved; `spectral-angle` approved with correction V1.

### data/vocab/metric.ttl

V1. `spectral-angle`. PepSpecBench Section 3, Eq. 3 defines SA = arccos(cosine)/π with lower better. The source does not use the name "normalized spectral contrast angle" and does not say it follows Prosit. In Prosit that name is a higher-is-better quantity, 1 − 2·arccos(cosine)/π, so the altLabel would match results this concept does not describe. Remove `skos:altLabel "Normalized spectral contrast angle"@en`. Replace the definition with "Angular distance between a predicted and an observed fragment-ion intensity vector after l2-normalisation, divided by π (SA = arccos(cosine)/π); 0 means identical relative intensities." Replace the scopeNote with "As defined by PepSpecBench (arXiv:2605.01945, Section 3, Eq. 3). Not the Prosit normalized spectral contrast angle (1 − 2·arccos/π), and not comparable with spectrum cosine similarity without conversion." This differs from reviewer-ro-2, who approved the concept as written. The team lead should reconcile the two before applying.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store. The review fields were set by `finalise` in `extract/lib.py`.

1. P1 (optional, applied): the source ID is `lit-otheromics-20261011-pepspecbench-source-yang2026` in every `source_ids`, sources.md and the pass ledger.
2. Vocabulary: `spectral-angle` follows reviewer-ro-1's correction V1, the team lead's decision where the two reviews differ (reviewer-ro-2 approved the concept as first written). The altLabel "Normalized spectral contrast angle" is removed and the definition and scope note are reviewer-ro-1's text.
3. Review fields: every record is `source_checked`; each result carries a review block naming reviewer-ro-2, with the extraction description kept in `note`.

## Records after correction

- benchmark: 1
- configuration: 12
- dataset: 7
- evaluation: 156
- model: 6
- protocol: 16
- result: 168
- source: 1

Status: source_checked 367.
