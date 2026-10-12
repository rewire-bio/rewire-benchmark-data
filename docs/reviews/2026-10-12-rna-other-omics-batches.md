# Review: RNA and other-omics batches, 2026-10-12

Independent review of the seven batches from the 2026-10-11 RNA and other-omics literature passes. Reviewers:
Claude review agents `reviewer-ro-1` (rnalm-zeroshot, rnagym, rna3d and the four new metric concepts) and
`reviewer-ro-2` (msgwild, pepspecbench, khoo2026, zhong2026). Neither extracted these batches: five were
extracted by `lit-rna-otheromics`, and khoo2026 and zhong2026 by `lit-rna-other` (imported from commit
ef64700 unchanged). No human review is claimed. Source transcription is not reproduction.

Each batch folder holds the reviewer's report for that batch, verbatim, and the corrections applied
(`review.md`), and the receipt (`review.json`, binding the SHA-256 of every file in the folder). The
corrections were applied by the extractor in the extraction scripts, as the reviewers specified, before the
batches were added to the store.

## Outcome

All seven batches passed: five with corrections, pepspecbench and zhong2026 with one optional change each,
which was applied. No printed, numeric or uncertainty value was wrong. Each reviewer re-retrieved every
pinned artifact, matched its SHA-256, compared every result with their own parser (not the extractor's
scripts), and read a seeded sample by hand.

| Batch | Source | Artifact SHA-256 | Reviewer | Values checked | Hand sample |
| --- | --- | --- | --- | --- | --- |
| `lit-rna-20261011-rnalm-zeroshot` | Wang et al. 2026, zero-shot benchmark of RNA language models (Brief Bioinform bbag098), Supplementary Tables 4-11 | `c8fc78c3…71e214` (.docx), `835b64d5…533808` (XML) | reviewer-ro-1 | 1190 of 1190 match | 48 |
| `lit-rna-20261011-rnagym` | RNAGym fitness leaderboard v0.1.1 at commit 2828cf9 | `c947a7a4…11b891` (README) and 3 more files | reviewer-ro-1 | 64 of 64 match | 64 |
| `lit-rna-20261011-rna3d` | Ludaic and Elofsson 2026, limits of deep-learning RNA 3D prediction (NAR gkag813), Tables 2-5 and S6, S7, S15 | `02043b4a…15ad1f` (XML), `0e26a301…9d463c` (PDF) | reviewer-ro-1 | 216 of 216 match | 42 |
| `lit-otheromics-20261011-msgwild` | MassSpecGym in the Wild, arXiv:2606.19624v1, Tables 2, 3 and 9 | `47f32939…efb0d2` (HTML) | reviewer-ro-2 | 176 of 176 match (156 kept) | 40 |
| `lit-otheromics-20261011-pepspecbench` | PepSpecBench, arXiv:2605.01945v1, Tables 2, 4 and 14 | `af7ed6d4…f18d81` (HTML) | reviewer-ro-2 | 168 of 168 match | 42 |
| `lit-rna-other-20261011-khoo2026` | Khoo 2026, nearest-neighbour fingerprint prediction baselines, arXiv:2610.02249v1, Tables 1-2 | `19c0dddb…374f1e` (PDF) | reviewer-ro-2 | 128 of 128 match | 40 |
| `lit-rna-other-20261011-zhong2026` | FlexMS, arXiv:2602.22822v4, Table 2 | `44c83ca8…2e546d` (PDF) | reviewer-ro-2 | 66 of 66 match | 40 |

Total after correction: 1988 results.

## Conflicts found in the sources

These values are transcribed as printed and marked `disputed` on the result, with the reviewer's
`source_warnings`. The reviewer chose result-level marks over source-level `evidence_concerns`, which would
block comparison for every result of the source.

- rnalm-zeroshot, 8 results: RFamLlama prints 1 - OR 0.000±0.000 in Supplementary Tables 6-9 next to AUC
  values of 0.61 to 0.69 in the same rows.
- rna3d, 24 results: DRfold and DeepFoldRNA have identical INF, GDT-TS and lDDT, in Tables 2-3 and in every
  per-target row of Supplementary Tables S3-S5, while their TM-scores differ.
- rna3d, 1 result: Table 3 prints RF2NA hard-set INF 0.668; the mean of its Supplementary Table S3 column is
  0.608.
- rna3d, 1 result: Supplementary Table S7 prints AF3 hard-set GDT-TS success 37.78%, which is not k/49;
  Supplementary Table S4 gives 19 of 49 (38.78%). Found by the reviewer.

## Main corrections

- **rnalm-zeroshot.** The Tables 7 and 9 starred rows state the 440 nt exclusion from their table notes. Four
  dataset locators are fixed. The four classification F1 protocols note that F1 0.667 with MCC near 0 is what
  an all-homologous classifier scores.
- **rnagym.** The six autoregressive and contrastive model configurations no longer carry the masked
  language model scoring convention.
- **rna3d.** The supplement's source record notes the S7 and S3-S5 inconsistencies.
- **msgwild.**
  - 20 Table 3 results that repeat MassSpecGym's own Table 3, already in the store under
    `part2-massspecgym-arxiv-v1`, are not added, with their evaluations, 4 configurations and 2 methods.
  - All Table 3 intervals are 99.9% BCa over 20,000 resamples, as the caption states.
  - Candidate versions and the v1.5 metric implementation, which the tables do not state, are null with a
    reason.
  - The grey Table 2 rows record the formula information they actually used.
  - Author overlap with the Hassoun group, and the MIST encoder in the MolForge pipeline, are noted.
- **pepspecbench.** The source ID names the first author (`...-source-yang2026`).
- **khoo2026.** DreaMS uses the pre-trained checkpoint without contrastive fine-tuning (Note S2). The random
  splits carry their structure leakage (62.9% NPLIB1, 95.3% MassSpecGym).
- **zhong2026.** The FlexMS protocol evaluates the MassSpecGym spectrum simulation task; it is not part of the
  MassSpecGym benchmark.

## Vocabulary

Four metric concepts are added to `data/vocab/metric.ttl`: `one-minus-overlap-ratio`, `spectral-angle`,
`spectral-angle-similarity` and `fingerprint-tanimoto-similarity`. The reviewers differed on
`spectral-angle`: reviewer-ro-2 approved it as written, reviewer-ro-1 asked for correction V1. The team lead
chose V1. PepSpecBench defines SA = arccos(cosine)/π, lower better, so the altLabel "Normalized spectral
contrast angle" is removed (Prosit uses that name for 1 − 2·arccos/π, higher better), and the definition and
scope note are reviewer-ro-1's text.

## Use-case judgements

Only msgwild proposes judgements: two `proxy` judgements of its mass-based retrieval protocol (Hit rate@1
and Hit rate@20) for `use-case-mass-spectrum-molecule-shortlisting`. reviewer-ro-2 approved them with the
rationale, constraints and limitations in M8, which the claims carry verbatim, and approved the two
`assessed_by` links in `use-case-links.json`. No use-case field change and no summary text was approved.

The `assessed_by` links are deferred to a follow-up, because adding them must be recorded with
`records -- change`, which needs owner approval. Until then the two judgement claims are unlinked drafts:
`needs_review`, unpinned and without a review block. The follow-up adds the links, sets the claims to
`source_checked` with reviewer-ro-2's review block, and pins them.

This PR leaves the use case, its seven existing judgements and its summary unchanged. The summary says
every value comes from two versions of one arXiv preprint (MSAlign). Once the MassSpecGym in the Wild
judgements are linked, that sentence is no longer accurate, and the summary may be withheld until it is
revised and re-reviewed.

The other six batches propose no judgement or summary: no existing use case covers RNA language models,
RNA fitness, RNA 3D structure, peptide spectrum prediction, molecule-to-spectrum prediction or fingerprint
prediction.

## Remaining gaps

- No figures were read.
- RNAGym structure results were not extracted, and its mRNA table is absent at the pinned commit.
- msgwild Tables 1, 4, 5 to 8 and 10, khoo2026 Tables 3 and 4, and zhong2026 Tables 3 to 8 and S1 to S5
  were not extracted. msgwild Table 8 holds a further formula-free MIST row.
- The new RNA model family records are not yet linked to same-named configuration and pipeline records
  already in the store (`mrnabench-*`, `nabench-*` and others). reviewer-ro-1 lists them as a follow-up.
- Wang et al.'s 31 RNAGym ncRNA assays and RNAGym v0.1.1's 31 are probably the same set, but neither source
  confirms it; they stay separate datasets.
