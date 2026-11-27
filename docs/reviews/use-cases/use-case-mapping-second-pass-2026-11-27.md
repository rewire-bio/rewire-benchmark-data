# Second verification pass, 2026-11-27

Reviewer: `claude`, applying the second independent verification by agent `verify-mappings` (verdicts
in its `verdicts2.jsonl`, 122 items). No human scientific review.

Batch: `data/omics/use-case-mapping-second-pass-20261127/`. `extract/ties.json` names every tie
change test by test, `extract/fields.json` holds the text changes, and `extract/build.py` writes the
records change.

## What the verification found

- The earlier verification fixes ([use-case-pages-verified-2026-11-27.md](use-case-pages-verified-2026-11-27.md)) all held.
- The 36 amp-feng parent links are right.
- Part A2 (batch `use-case-mapping-proxy-20261127`, 72 proxy ties added by precedent): 40 not agreed
  (55.6 percent). 38 should not be tied and 2 should be direct.
- The viral and microbial use case: 2 of 6 ties wrong. The two Kedzierska ties on single-cell integration are right.
- Five sentences on the pages were wrong.

All verdicts were accepted.

## Why Part A2 went wrong

Part A2 tied a test when the use case already mapped "the same kind of test". That precedent stood in
for reading the test, so the checks that caught the Part B errors were never applied:

- Strata were tied beside the set they divide. The Evo 2 ClinVar strata, for example, are conservation
  and splice-distance partitions of the same variants.
- Totals were tied beside their parts: ClusPro totals, and LiPP's full set, which contains its tied test set.
- Some tests break an exclusion or are the wrong variant class: near-splice strata, somatic hotspots,
  and coding SNVs that are not missense only.
- Some rows compare no models: one Borzoi model's tissue tracks, AlphaGenome ablations, and LiPP rows copied from the literature.
- Two reasons were false: "pooled over series" on the CASP16 tests, and a patient-RNA description on Alavi's OPA1 test.

The rules in [use-cases.md](../../use-cases.md) ("Rules for mapping tests to a use case") now cover
this: the parent-and-parts check and the exclusions check apply to every tie, including ones added by
precedent.

## Changes

| Change | Tests | Detail |
| --- | --- | --- |
| Withdrawn, missense PP3/BP4 | 8 | Six Evo 2 ClinVar coding SNV strata (subsets of the tied set; near-splice is excluded; coding is not missense only); GPN-MSA COSMIC ablation (somatic hotspots); GUANinE cadd-snv (genome-wide proxy labels) |
| Withdrawn, regulatory variant follow-up | 15 | Two Evo 2 near-splice strata (splicing); eight conservation and two intergenic strata (second partition of the same variants); AlphaGenome Table S2 TraitGym complex (ablations); TraitGym complex and Mendelian best Borzoi track (one model's tracks, picked on test labels) |
| Withdrawn, rare disease ranking | 1 | TraitGym Mendelian best Borzoi track |
| Withdrawn, structural hypotheses | 13 | LiPP PoseBusters v1 and v2 rows (copied from the literature, small molecules); LiPP full set RMSD and PB-valid (contains the tied test set); eight ClusPro totals (second partition and sum of tied categories) |
| Withdrawn, patient RNA splicing | 1 | Alavi OPA1 extended positive calls (no splicing truth, no patient RNA) |
| Withdrawn, viral and microbial | 2 | GenBench human against worm (neither viral nor microbial); GenBench long-range species classification (species not named) |
| Regraded to direct, lead optimisation | 2 | Leakage-controlled CASP16 L1000 (chymase, 17 ligands) and L3000 (autotaxin, 123 ligands): each is one congeneric series |
| Reason corrected, missense PP3/BP4 | 2 | ESM1b HGMD tests: HGMD disease-causing against gnomAD common variants, not ClinVar |

### Text changes

- Lead optimisation, exclusions (pinned; its judgements were re-pinned): the first exclusion said no
  source scores a single series. It now says most numbers average across series and the two CASP16
  tests are the exception.
- Genomic element annotation, decision (pinned; re-pinned): "DNA sequence model" for "DNA language model".
- Viral and microbial: a new first gap answers the decision. On this evidence blastn beats the best
  embedding: accuracy 0.968 against 0.927 on the 33-class set (macro F1 0.938 against 0.925), and 0.912
  against 0.875 on the 40-class set (macro F1 0.889 against 0.874). Megablast scores below the embedding
  on both. The GenBench evidence is now only the SARS-CoV-2 variant task.
- Glycan: all 103 results carry a standard deviation over three seeds, not most.
- Protein representation: 13 systems from 12 models are compared on the linked HyPLM tasks.
- Protein design: two of Genie 3's rows are linked to a model; the board orders none, with one study.
- Protein design, protein representation and single-cell integration: Scaffold-Lab, DeepProtein and
  SCMBench are held while a question about one of their sources is open. Those sources are reviewed but
  carry an evidence concern.

### Other corrections

- `catalog-model-nt-v2` loses its `version` attribute ("50M multi-species"). The record serves as the
  family record for 46 configurations of every Nucleotide Transformer v2 size, and Feng et al. state no
  checkpoint size. Its profile still describes the 50M model card it was written from.
- The review of the first fixes was renamed from 2026-11-28 to 2026-11-27, the day it was written. The
  FLIP2 judgement's review date was corrected to match. The provenance hash of that one claim was
  updated for the corrected text.

## Ties and boards, per use case

Counts by query on the store and `kb/board.py` (main's grouping and grades). "Before" is origin/main
before this branch; "now" is after this batch.

| Use case | Ties before | Ties now | Ranked before | Ranked now |
| --- | --- | --- | --- | --- |
| cell-type-annotation-transfer | 11 | 15 | 0 | 4 |
| genetic-perturbation-response | 19 | 20 | 5 | 5 |
| genomic-sequence-element-annotation | none | 105 | none | 6 |
| glycan-property-prediction | none | 21 | none | 0 |
| lead-optimisation-affinity-ranking | 5 | 7 | 0 | 0 |
| mass-spectrum-molecule-shortlisting | 9 | 17 | 3 | 3 |
| missense-pp3-bp4-calibrated-evidence | 23 | 29 | 30 | 47 |
| patient-rna-splicing-validation | 18 | 19 | 3 | 3 |
| phenotype-perturbation-selection | 5 | 6 | 0 | 0 |
| protein-design-quality | none | 5 | none | 0 |
| protein-function-annotation | none | 6 | none | 0 |
| protein-representation-property-prediction | none | 17 | none | 0 |
| rare-disease-candidate-ranking | 32 | 34 | 35 | 43 |
| regulatory-variant-gene-follow-up | 25 | 28 | 8 | 12 |
| rna-structure-prediction | none | 42 | none | 2 |
| single-cell-data-integration | none | 10 | none | 2 |
| splicing-follow-up | 18 | 25 | 6 | 10 |
| structural-hypotheses-experiments | 15 | 25 | 3 | 3 |
| therapeutic-target-validation | 5 | 6 | 0 | 0 |
| viral-microbial-sequence-classification | none | 4 | none | 2 |

The other 19 use cases are unchanged. The store holds 39 use cases, 25 of which order models. With
the two GenBench ties gone, the viral board places DNABERT-2 and Nucleotide Transformer together at 1
to 2, from 22 groups.
