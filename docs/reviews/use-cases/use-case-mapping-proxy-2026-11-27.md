# Use-case mapping gaps: proxy candidates applied, 2026-11-27

Reviewer: `claude`, the agent that drafted the links. Drafter and reviewer are the same agent, so this
is not the second-worker review `docs/use-cases.md` requires; the team lead's verification pass before
merge is that review. No human scientific review is claimed.

Batch: `data/omics/use-case-mapping-proxy-20261127/`. Its `extract/selection.json` lists each applied
candidate and each refusal with its reason; `applied.jsonl` lists each link with the protocol passage
it rests on. The candidates come from `kb/curation/use_case_mapping_candidates.jsonl`
(`docs/reviews/2026-11-27-use-case-mapping-gaps.md`).

## Rule

A candidate is applied at `proxy` when all three hold:

1. the use case already maps the same kind of test at `proxy` (for example ClinVar-style predictor
   discrimination on missense PP3/BP4, structure-accuracy protocols on structural hypotheses,
   sequence splice-site classification on splicing follow-up);
2. the use case's own exclusions do not name the test;
3. the evaluation gates of `shared/omics/use-cases.ts` accept it: a reviewed protocol with clean
   sources and at least one evaluation on a reviewed configuration with reviewed results.

## Applied: 72 judgements

| Use case | Links | What |
| --- | --- | --- |
| structural-hypotheses-experiments | 23 | FoldBench protein-monomer, protein-peptide, protein-DNA and protein-RNA; the ClusPro BM5 aggregate and antibody rows; LiPP full and PoseBusters sets; ESMFold2 Runs N' Poses |
| regulatory-variant-gene-follow-up | 18 | Evo 2 paper noncoding SNV and non-SNV ClinVar strata by conservation and location; TraitGym complex-trait evaluations from the second study and the AlphaGenome Atlas |
| missense-pp3-bp4-calibrated-evidence | 14 | Brandes et al. 2023 ClinVar and HGMD missense comparisons; Evo 2 coding SNV strata; GUANinE cadd-snv; GPN-MSA COSMIC and TADBP; Lu et al. ClinVar, missense stratum only |
| splicing-follow-up | 7 | Nucleotide Transformer splice donor, acceptor and all-site tasks; GTEx tissue splicing (You et al. 2026) |
| rare-disease-candidate-ranking | 3 | PhyloGPN ClinVar likelihood ratio; Lu et al. ClinVar by variant class; TraitGym Mendelian per-trait Borzoi tracks |
| lead-optimisation-affinity-ranking | 2 | PLABench CASP16 L1000 and L3000 affinity under a leakage control |
| patient-rna-splicing-validation | 2 | OPA1 extended positive calls; SpliceAI2 DM1 MBNL1 junction usage |
| genetic-perturbation-response | 1 | PerturBench v4 mode-collapse diagnostics on Frangieh21 (CRISPR) |
| phenotype-perturbation-selection, therapeutic-target-validation | 1 each | CPPC reimplemented best-model Challenge 2 score |

Two notes on what was applied. Lu et al. score 14 variant classes as separate evaluations on one
protocol; on missense PP3/BP4 every class other than missense is listed in `excluded_evaluations`
with a reason, so only the missense evaluations feed the use case. The Evo 2 noncoding and coding
strata linked here are the sub-strata (by conservation, splice distance and location); the four
parent strata whose counts are disputed in rewire-benchmark-data#163 stay unlinked, as the
2026-11-23 batch left them. The sub-strata come from the same supplementary file and carry no
recorded dispute, but a reviewer should read #163 before relying on them.

## Refused at this step: 18

| Candidate | Use case | Why |
| --- | --- | --- |
| RFD4-Proteina computational passers per GPU-hour (6) | de novo binder design | This use case already judges computational filter pass rates `outside_scope` (Bennett RF2 and AF3 filters): a filter is a step in the pipeline, not an outcome |
| Kendiukhov target ranking (6), CPPC Challenge 1 | phenotype perturbation selection | Predicting a perturbation's response, not choosing which to test; the use case already judges Qin et al.'s prediction-error protocol `outside_scope` on the same grounds |
| CPPC Challenge 1 | therapeutic target validation | Predicting four knockouts' effects, not choosing targets |
| Barbosa ClinVar intronic set; Evo 2 ClinVar low-SpliceAI-and-Pangolin set (2) | splicing follow-up | ClinVar clinical labels; the use case excludes disease pathogenicity and already refuses the MLH1 curated set for that reason |
| FoldBench DNA monomer and RNA monomer | structural hypotheses | No protein; the use case's inputs are protein sequences and partners |

## Refused by the gates, from the team lead's list

| Candidate | Why |
| --- | --- |
| CASP16 and the four CAPRI round 61 targets | Their protocol records are `discovered`, not reviewed |
| Virtual Cell Challenge 2026 | Over 500 evaluations on one test, every one a competition submission |
| MassSpecGym Table 3 main retrieval | Protocol is `needs_review` |
| AlphaGenome paper splice-site classification (24) | Protocols are `needs_review` |
| Song et al. Virtual CRISPR (2), EVEE deconfounded ClinVar, Evo 2 mitochondrial pathogenicity | A source with an open evidence concern or not yet checked |
| AlphaFold and ESMFold PDB benchmark strata (16) | The source carries an evidence concern (its method, template-quality and row-total cells conflict with its text); its two mapped headline protocols are drafts, not shown, for the same reason |
| TraitGym matched-feature, single-CADD-feature and best-of protocols (7) | Their evaluations link a method or model, not a configuration |
| Brandes et al. ESM-1b versus EVE shared-variant sets (2), Kendiukhov K562 CRISPRa, Silverstein expression outliers | No evaluation passes the gates (unreviewed configuration, dataset or result) |

Refusals by exclusion stand as before: ProteinGym supervised and indel tracks, mRNABench ribosome load
against UTR baselines, ProteinBench and Genie 3 against binder design, and clinical-label splicing sets.

## Next steps that need record work first

- **Open Problems label projection (24 tests) and PerturBench Norman19 combination tasks (4).** Each
  is a `task` record whose evaluations link the task as their assessment and name no protocol. A
  judgement must name a protocol. The restructure: add one `protocol` record per task (the task's
  dataset, split, metric and source locator), add an `evaluates_task` link from it to the task, and
  change each evaluation's `assessment` link from the task to the new protocol, as one reviewed batch
  with `records -- change`. Evaluations are pinned by existing judgements only if they are already
  mapped; these are not, so nothing active is withheld.
- **scFoundation Supplementary Table 4 (Zheng68K, Segerstolpe).** Every evaluation links its `system`
  to a `method` record (CellTypist, scBERT and others) rather than a `configuration`. The restructure:
  add one `configuration` per method as run in scFoundation's table (`configuration_of` the method,
  citing the supplementary source), and change each evaluation's `system` link to it. The same pattern
  blocks the TraitGym matched-feature protocols and GlycanML's own results.
