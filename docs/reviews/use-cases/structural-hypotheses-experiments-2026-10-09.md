# Structural hypotheses for experiments: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-structural-20261009/` (100 records). Use case: `use-case-structural-hypotheses-experiments`.

Reviewer: a separate Claude review agent that did not extract the batch. No human review is claimed. Nothing was executed or reproduced. This review checks the transcription against the pinned sources and judges the relevance claims.

## Outcome

- Both article XMLs re-download to the pinned SHA-256, and the two archived `artifacts/*.gz` decompress to the same bytes.
- All 50 results match their sources: 27 Fromm Table 1 cells and 23 Smorodina values, each found in the exact paragraph its locator names. No value, metric, unit, direction, configuration or protocol link was wrong, and every Table 1 cell has exactly one result.
- The four oracle evaluations are excluded from the Fromm judgement with reasons, so no oracle is ever shown as a method a user could apply. The gap they define stays in a descriptive claim.
- The nanobody strata are moved into their own comparison group, because the records themselves say nanobody results do not transfer to conventional antibodies.
- One internal conflict is recorded as a source warning on the affected result: the mean per-target correlation for ranking confidence is 0.28 in the text and 0.214 in Table 1.
- All six judgements hold as `proxy`. Each is `source_checked`, with `reviewed_evaluations` and a review filled in. Pins are left unset.
- Simulation: with the reviewed batch and the use-case changes below applied in memory, and pins computed, all 11 judgements on the use case derive as active: the 6 new ones and the 5 existing ones.

## How the check was done

1. Downloaded both Europe PMC full-text XMLs into an empty directory and hashed them. Decompressed the archived copies and hashed them.
2. Parsed Fromm Table 1 from the JATS XML with a parser written for this review, and extracted every paragraph of both articles with their numbering. The extractor's script was not run.
3. For each Fromm result, built the expected cell from the row label and column header, then compared printed value, numeric value, metric, unit, direction and the linked configuration and protocol.
4. For each Smorodina result, located the exact paragraph its locator names and checked that the printed value appears there, attributed to the named tool, with the stated meaning. The batch numbers paragraphs over the whole article, including figure and table captions; that scheme is used consistently across its locators, and I verified it on every value and on the Methods and claim locators.
5. Read the cited Methods, Results and Discussion paragraphs, the competing-interest statements and the reference lists to check origins, dataset counts, sampling and the collector's points.
6. Checked the two stored FoldBench protocols, their five evaluations each and their results.
7. Loaded the reviewed batch against the current store in memory with `recordSchema`, `validateVocabularies`, `validateAttributes` and `validateRecords`, then ran `deriveUseCaseInputs` with the approved use-case text and computed pins. Nothing was written to the store.

## Sources and hashes

| Source | Pinned SHA-256 | Re-download | Archive |
| --- | --- | --- | --- |
| `structural-20261009-source-fromm2026` (PMC13061134) | `a7320667...275d` | Match | Decompresses to it |
| `structural-20261009-source-smorodina2026` (PPR1221387) | `0ad24054...0732` | Match | Decompresses to it |

## Values checked

| Source | Values | Matched | Notes |
| --- | --- | --- | --- |
| Fromm Table 1 (9 rows by 3 columns) | 27 | 27 | Printed precision kept, including `1.000` and `0.544` |
| Smorodina, average precision (P11) | 3 | 3 | 0.187, 0.067, 0.026 |
| Smorodina, calibration (P19 and P21) | 12 | 12 | Correlations and the four printed quadrant shares |
| Smorodina, sampling (P36) | 8 | 8 | N = 1 and N = 100 medians for four tools |
| Total | 50 | 50 | |

Checks against other parts of the sources:

- The Fromm text values agree with Table 1 where both are printed: the overall correlation for ranking confidence is 0.80 in section 3.5 and 0.799 in Table 1, and the best-of-200 DockQ is 0.54 in section 3.6 and 0.544 in Table 1. The exception is the per-target correlation, below.
- Both descriptive claims are correct. The Fromm claim matches section 3.3 paragraph 1 (0.29 to 0.37, best 0.52; Boltz-1 and Chai-1 0.12 to 0.14) and section 3.6 paragraph 4 (0.35 against 0.54). The Smorodina baseline claim matches P11 (about 0.011; about 89 to 91 positives among about 8041 to 8281 pairs), and the negatives claim quotes P9 exactly.
- The configuration parameters match the methods: AF3 3.0.1 with 50 diffusion samples and seed 1 (P75), Boltz CLI v2.2.0 with 50 samples and seed 42 (P74), Chai-1 0.6.1 with 5 trunk and 10 diffusion samples (P73), and the five-seed saturation design (P91).

## The collector's points

- **Pooled training and held-out systems, and untested negatives.** Both are real and correctly recorded.
  - The per-tool counts in P13 are AF3 30 train and 76 test, Chai-1 25 and 81, Boltz-2 64 and 42, out of 106. Every printed value is over all systems, so none is a post-cutoff result. This is on all three Smorodina protocols and judgements, and it matters most for Boltz-2, which is the most exposed and has both the highest best-of-N DockQ and the least specific confidence.
  - P9 says: "we assume that VHHs and antigens of 'shuffled complexes' are non-binders". No pairing was tested, so some negatives may bind, which would understate the average precision. This is on the dataset's `label_semantics`, the protocol, a descriptive claim and the judgement's rationale. That is the right treatment: the limit is in the design, not in the transcription.
  - I added one count conflict: the abstract gives 11,342 shuffled pairings while P8 gives 11,130, which is 106 squared minus 106. Neither figure is used in a stored value; the scored counts come from P11. Recorded on the pairing dataset and the protocol.
- **The training-cutoff contradiction.** Confirmed, and a limitation rather than a source concern. P62 says post-October 2021 depositions were kept, "corresponding to the earliest training cutoff among the evaluated tools (Boltz-2)". The methods (P76) give Chai-1 about 12 January 2021, AF3 about 30 September 2021 and Boltz-2 about 1 June 2023. So Chai-1 is the earliest, Boltz-2 the latest, and the October 2021 date matches AF3. The per-tool train and test counts follow the methods, and no printed value depends on the mis-stated sentence. I rewrote the limitation to say exactly this on all three protocols and judgements. An `evidence_concerns` entry would withhold all three judgements for a sentence that no value rests on.
- **Fromm's "selection among 200".** This is not an inference that needs a caveat: Methods 2.2.2 states that 40 seeds by 5 models give 200 models per complex, and section 2.4 repeats "we generated 200 models for each complex". The table's DockQ row (0.544) matching the best-of-200 value (0.54) confirms the reading. I replaced the limitation with that statement.
- **0.28 against 0.214.** Section 3.5 gives the mean per-target correlation for ranking confidence as 0.28, citing Figure 6; Table 1 prints 0.214 for the same quantity under a Spearman caption. The text calls it "Cc" and "mean CC" and names no correlation type, so the two may be different statistics, and the figure legend does not resolve it.
  - Decision: keep the table value, which is the better-specified statement, and attach a `source_warnings` entry to that one result saying the text gives 0.28 and that the two must not be cited as the same measurement. I did not dispute the result, because the transcription is right and the table states its statistic while the text does not. The protocol and the judgement carry the same note.
- **The oracle rows.** Agreed, and excluded. Table 1's DockQ, aeTM, aeiTM and aeRankConf rows all need the experimental structure: DockQ picks the best model against it, and the three "ae" scores recompute pTM and ipTM from the true aligned errors (sections 2.7 and 3.6). None is a rule a user could apply before an experiment.
  - Labelling alone is not enough, because a comparison table invites a reader to compare rows. So all four evaluations are now in the judgement's `excluded_evaluations`, each with its reason, and the judgement's endpoint names only the five computable scores (ipTM, pTM, ranking confidence, pDockQ2, ipSAE).
  - Nothing of value is lost: the gap those rows define is the point of the comparison, and it stays in `structural-20261009-claim-fromm2026-top-vs-best`, which records 0.35 for the best predicted-error score against 0.54 for the best achievable pick. Their results stay `source_checked`.
- **Origin per row.** Correct as recorded, with one point of interpretation.
  - Fromm: the authors are Fromm, Ludaic and Elofsson, with no declared conflicts. They did not develop AlphaFold3, Boltz-1 or Chai-1. pDockQ2 is their own group's (Zhu et al. 2023), and that row is `author_reported`. The four oracle rows are the source's own constructs and are also `author_reported`. The ipTM, pTM, ranking confidence and ipSAE rows are `independent_paper`.
  - The evaluated system here is the selection rule applied to AlphaFold3 models, which is why a row can be author-reported even though AlphaFold3 is not the authors' tool. Every Fromm evaluation also carries "Run by authors who did not develop AlphaFold3", which keeps that clear.
  - Smorodina: no author developed AlphaFold3, Boltz-1, Boltz-2 or Chai-1, so all nine evaluations are `independent_paper`. One author declares advisory, consulting and employment roles with antibody-discovery and biotechnology companies; none of the listed companies is a developer of the three tools compared. That is on the source's `scope_note`, which is the right place.

## The two FoldBench judgements

Both reuse stored records and add none. I checked them:

- `ucc-research-protocol-foldbench-antibody-antigen` and `ucc-research-protocol-foldbench-protein-ligand` are `source_checked`, each with `uses_data` and `part_of` links and three FoldBench sources.
- Each has exactly five evaluations (AlphaFold 3, Boltz-1, Chai-1, HelixFold 3, Protenix), all `source_checked`. The antibody-antigen evaluations carry four `source_checked` results each (success rate, LDDT, interface RMSD, ligand RMSD); the protein-ligand ones carry three (success rate, LDDT-LP, LDDT-PLI). So the evidence is reviewed, and the judgements' `reviewed_evaluations` list all five each.
- They fit the use case. Each is a multi-tool comparison on targets with low homology to earlier PDB entries, scored against the deposited complex, which is what the question asks about at the structural level. `proxy` is right, because success is structural agreement and no prediction is tied to an experiment's outcome.
- Their origin is `author_reported`, because the FoldBench authors ran all five tools. The judgements already say the per-tool assessable counts differ, so the populations are not matched.
- I added one limitation to both: the mapped evaluations were reviewed in an earlier batch, and this review checked their status, links and fit, not their values against FoldBench.

## Grouping by complex class

The use case's third exclusion says results from one complex class do not establish performance in another, and `setting` says monomers, antibody complexes and ligand complexes need separate protocols.

The batch had one group, "Antibody and nanobody-antigen interface predictions", holding the two conventional antibody strata and the three nanobody strata, plus a separate protein-ligand group. The Smorodina records say in their own limitations that results "do not transfer to conventional antibodies or other complex classes", so pooling them in one comparison contradicts the records.

I split them:

| Group | Stratum | Judgement |
| --- | --- | --- |
| Antibody-antigen interface predictions | 1 Accuracy of five tools (FoldBench) | `...-foldbench-antibody-antigen` |
| | 2 Picking AlphaFold3 models by confidence (independent) | `...-fromm2026-model-selection` |
| Nanobody-antigen interface predictions (preprint) | 1 Best of N samples | `...-smorodina2026-sampling` |
| | 2 Confidence against accuracy | `...-smorodina2026-calibration` |
| | 3 Confidence as evidence of binding | `...-smorodina2026-cognate-vs-shuffled` |
| Protein-ligand pose predictions | 1 Pose accuracy of five tools (FoldBench) | `...-foldbench-protein-ligand` |

The five existing protein-protein and docking judgements have no group and were not touched. Each group's headline metric exists among its results.

Two notes on the groups:
- The FoldBench antibody-antigen dataset record gives 172 published targets and does not say whether nanobodies are among them. It stays in the antibody-antigen group, which is how FoldBench labels it.
- Within the antibody-antigen group the two strata answer different questions, structural accuracy across tools and the cost of picking by confidence, so they are not two measurements of one quantity. The stratum labels say which is which.

## Judgements

| Judgement | Grade | Fit | Reviewed | Excluded |
| --- | --- | --- | --- | --- |
| `...-foldbench-antibody-antigen` | proxy | Five tools on held-out antibody-antigen targets | 5 | 0 |
| `...-foldbench-protein-ligand` | proxy | Five tools on held-out protein-ligand targets | 5 | 0 |
| `...-fromm2026-model-selection` | proxy | What picking by confidence costs, one tool, 110 post-cutoff complexes | 5 | 4 oracle rows |
| `...-smorodina2026-sampling` | proxy | What sampling gains, four tools, nanobodies | 4 | 0 |
| `...-smorodina2026-calibration` | proxy | Whether confidence tracks accuracy, three tools | 3 | 0 |
| `...-smorodina2026-cognate-vs-shuffled` | proxy | Whether confidence indicates that an interaction exists | 3 | 0 |

`proxy` is right for all six. Each measures agreement with a deposited structure, or how well a confidence score tracks that agreement. None links a prediction to an experiment's outcome, which the use case's first exclusion requires of direct evidence. The cognate-against-shuffled judgement is the closest to the question, but its negatives are assumed rather than tested, so it cannot be direct either.

## Approved use-case changes

This is the exact text to apply to `use-case-structural-hypotheses-experiments`. Fields not listed stay unchanged. `decision`, `output`, `inputs`, `setting` and `clinical_scope` already describe the target correctly, and nothing in the batch contradicts them. In particular `setting` already says antibody complexes and ligand complexes need separate comparison protocols, which the new grouping follows.

### `exclusions`

Keep the three existing entries and append the collector's sentence, which I approve, with the numbers made explicit:

```json
"Confidence scores do not separate real from non-cognate pairings: on nanobody-antigen complexes the best average precision was 0.187 against a 0.011 baseline, so a confident model is not evidence that the interaction exists."
```

This sharpens the existing second exclusion, which already says high confidence does not prove interaction existence, by naming the measurement behind it. Both numbers are `source_checked` results in this batch.

### `evidence_gaps`

Keep the five existing entries and append:

```json
[
  "Confidence selection is tested only for AlphaFold3 on antibody-antigen complexes (Fromm et al. 2026); no equivalent table was found for Boltz, Chai-1, protein-protein or protein-ligand complexes.",
  "The nanobody evidence is a preprint that has not been peer reviewed, pools systems inside and outside each tool's training data, and defines its negatives as untested shuffled pairings.",
  "No linked comparison reports uncertainty intervals for per-tool values.",
  "No linked comparison connects a predicted structure or confidence score to the outcome of an experiment."
]
```

### `links`

Add `assessed_by` links to these six protocols, keeping the five existing links:

- `ucc-research-protocol-foldbench-antibody-antigen`
- `ucc-research-protocol-foldbench-protein-ligand`
- `structural-20261009-protocol-fromm2026-abag-model-selection`
- `structural-20261009-protocol-smorodina2026-vhh-cognate-vs-shuffled`
- `structural-20261009-protocol-smorodina2026-vhh-dockq-vs-sampling`
- `structural-20261009-protocol-smorodina2026-vhh-iptm-dockq-calibration`

### `source_ids` and `citation_locators`

Add the two new sources, both clean and hash-verified, and these locators:

```json
[
  {"source_id": "structural-20261009-source-fromm2026", "locator": "Sections 2.1, 2.2, 2.4, 2.7, 3.3, 3.5 and 3.6; Table 1"},
  {"source_id": "structural-20261009-source-smorodina2026", "locator": "Results P8 to P11, P18 to P22 and P33 to P36; Methods P62, P66, P67 and P73 to P91"}
]
```

The FoldBench sources are not added to the use case. The two FoldBench judgements cite them, and the use case's own text does not rest on them.

### The five existing judgements under the new exclusion

All five still hold:
- the four ClusPro BM5 docking judgements (enzyme and others, top 10 and top 30);
- the FoldBench protein-protein judgement.

Each measures whether a correct pose or structure is among the ranked output, scored against an experimental structure. None claims that a confidence score indicates binding, and none of their endpoints, rationales or limitations depends on confidence at all. The new exclusion therefore removes nothing they assert; it narrows a claim they do not make. The other four fields they pin are unchanged.

`exclusions` is pinned, so applying this text withholds all five until they are re-pinned. In the simulation the only changed pin was the use case's, and after re-pinning all eleven judgements derive as active. Re-pin the five existing judgements with the six new ones against this review.

## Final summary text

> Two new comparisons join the existing docking and FoldBench evidence, both on antibody complexes, and neither ties a prediction to an experiment's outcome. Fromm et al. 2026 generated 200 AlphaFold3 models for each of 110 antibody-antigen complexes deposited after the training cutoff, then asked which model each confidence score picks. Every score a user can compute picked models of about the same quality: mean DockQ 0.375 for ranking confidence, 0.370 for ipTM, 0.369 for pTM, 0.353 for ipSAE and 0.352 for pDockQ2, while the best of the 200 models averaged 0.544. The per-target correlation between score and accuracy stayed at or below 0.247, so within one target the confidence ranking carried little information. Smorodina et al. 2026, a bioRxiv preprint that has not been peer reviewed, ran AlphaFold3, Boltz-2, Boltz-1 and Chai-1 on 106 nanobody-antigen complexes. Sampling raised the best available model for every tool, with median best DockQ rising from 0.24 to 0.68 for AlphaFold3 and from 0.57 to 0.80 for Boltz-2 between 1 and 100 samples, though picking that best sample needs the experimental structure. Confidence tracked accuracy unevenly: the correlation between ipTM and best-sample DockQ was 0.736 for AlphaFold3, 0.665 for Boltz-2 and 0.612 for Chai-1, with 18% of Boltz-2 predictions confident but wrong and 24% of Chai-1 predictions accurate but unconfident. Pairing every nanobody with every antigen showed that confidence does not indicate that an interaction exists at all: average precision for ranking the real pairings above shuffled ones was 0.187 for AlphaFold3, 0.067 for Chai-1 and 0.026 for Boltz-2, against a baseline of about 0.011. The preprint's nanobody set mixes systems inside and outside each tool's training data, and its non-cognate pairings are assumed not to bind rather than tested. A high confidence score is a statement about a predicted structure, not evidence that two molecules interact.

Every number is a `source_checked` result in this batch, or a count printed in a source:

- **Fromm Table 1:** the `<DockQ>` cells for RankConf, ipTM, pTM, ipSAE, pDockQ2 and the DockQ oracle row, and the `<R>` column, whose largest computable value is ipSAE's 0.247.
- **Smorodina:** the eight sampling medians (P36), the three best-sample correlations and the Boltz-2 Q2 and Chai-1 Q4 shares (P19), and the three average precisions with the baseline (P11).
- The 110 complexes and 200 models come from Fromm sections 2.1 and 2.2; the 106 complexes from Smorodina P8.

The oracle 0.544 is quoted as the best of the 200 models, which is what the source defines it as, and is not presented as a method.

## Checks run

- In memory: the reviewed batch (100 records) passes the schema, vocabulary, attribute and record checks against the current store.
- `npm run typecheck`: exit 0.
- `npm run records -- check`: 32,098 records match their provenance (the batch is not in the store).
- `npm test`: 499 of 499 pass.
- `npm run build`: not run. The batch is not in the store, and the build writes release files outside this review's scope.

## Remaining gaps

- The Smorodina supplementary tables were refused by a browser challenge, so the per-system quadrant assignments behind the calibration shares could not be checked.
- The text does not say which sample the quadrant shares refer to, and not every tool has every value printed.
- Not covered, as the collector recorded: CASP16 and CAPRI per-group tables, TCR-pMHC benchmarks, protein-nucleic acid classes beyond the stored FoldBench protocols, and any confidence-calibration table for protein-protein or protein-ligand complexes.
