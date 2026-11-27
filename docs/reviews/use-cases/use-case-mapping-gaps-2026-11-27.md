# Use-case mapping gaps: links applied, 2026-11-27

Reviewer: `claude`, the agent that drafted the links, by scope review against each use case's
question, endpoint and exclusions, and by store verification of the evaluation gates
(`shared/omics/use-cases.ts`) and source hashes. Drafter and reviewer are the same agent, so this is
not the second-worker review `docs/use-cases.md` requires, and 12 judgements go live on merge
without one. No human scientific review is claimed. An independent verification pass is needed.

Batch: `data/omics/use-case-mapping-gaps-20261127/`, built by its `extract/build_links.py` on the
pattern of `data/omics/use-case-variant-links-20261123/`. The candidates and the reasoning behind each
grade are in `docs/reviews/2026-11-27-use-case-mapping-gaps.md` and
`kb/curation/use_case_mapping_candidates.jsonl`; every applied link is listed with its passage in
`data/omics/use-case-mapping-gaps-20261127/applied.jsonl`.

## Rulings

12 `links:assessed_by:` judgements, all `proxy`, each on a protocol whose sibling protocols the same
use case already maps as `proxy`. The grade follows that precedent: the store's reviewers grade
retrospective annotation transfer and candidate-pool retrieval as `proxy` on these use cases.

- `use-case-cell-type-annotation-transfer` (4): HyCell annotation transfer to a held-out batch with a
  15-nearest-neighbour classifier, with logistic regression, and after fine-tuning; scTab Table 1b
  donor bootstrap (companion of the mapped seeded-fit protocol).
- `use-case-mass-spectrum-molecule-shortlisting` (8): MassSpecGym in the Wild Hit rate@5 and MCES@1
  (companions of the mapped Hit rate@1 and @20); MSAlign Table 3 formula-free Recall@1, @5 and @20 on
  NPLIB1 and on Spectraverse (companions of the mapped formula-free MassSpecGym columns). The
  formula-conditioned columns stay out, as the use case's exclusions require.

## Considered and not applied

| Protocol | Use case | Why |
| --- | --- | --- |
| scFoundation Supplementary Table 4, Zheng68K and Segerstolpe | cell-type annotation | Every evaluation links its system to a `method` record, not a `configuration`; the evaluation gate refuses them (as the 2026-11-23 batch refused TraitGym's method-linked protocols) |
| Song et al. 2025 Virtual CRISPR simple and difficult hit classification | phenotype perturbation selection | The source carries an open evidence concern on its random-baseline figures, which withholds any judgement resting on it |
| MassSpecGym Table 3 main retrieval (`paper-protocol-a18b4bc79049513fb7`) | mass spectrum shortlisting | The protocol is `needs_review` |
| Fortier et al. Barbosa ClinVar intronic SNVs | splicing follow-up | Labels are ClinVar clinical classifications; the use case excludes disease pathogenicity, as its existing `outside_scope` judgement on the MLH1 set does. Regraded `proxy` in the proposal and not applied |
| PerturBench Srivatsan20 and PBMC covariate transfer, Sci-Plex dose holdout | genetic perturbation | Small-molecule perturbations; the use case is genetic. Regraded `outside_scope` in the proposal |
| PerturBench Norman19 combination tasks, Open Problems label projection | genetic perturbation, cell-type annotation | Their tests are `task` records whose evaluations name no protocol; a judgement must name a protocol, so these need protocol records first |
| Virtual Cell Challenge 2026 | genetic perturbation | One test with 1,048 competition submissions: more than the 500 eligible evaluations a judgement may hold, and each submission is a configuration with no model |
| Evo 2 paper variant evaluations, Brandes et al. 2023, CASP16, CAPRI | variant use cases, structural hypotheses | Graded `proxy` in the proposal as related endpoints (uncalibrated ClinVar discrimination; blind-target structure accuracy) and left for the reviewed proposal |
| Unmapped ProteinGym tests, mRNABench ribosome-load tasks, ProteinBench and Genie 3 | protein variant effect, UTR baselines, binder design | Named in each use case's exclusions (supervised and indel tracks; benchmark-wide mRNABench; unconditional generation) |
