# Discrepancy rules version 4: before and after

Date: 2026-10-24. Decision: [ADR 0001](../adr/0001-comparable-evidence.html), option B. Design: [discrepancy rules version 4](../design/discrepancy-rules-v4.html). Issues: #201, #204, #205, #206, #207, #208.

Version 3 was measured on the release bundle `kg/2026-10-23-9f59283abc5a`. Version 4 was measured on a local `npm run kg:bundle` of this branch: the same store, plus the records in `data/omics/discrepancy-v4-comparability-20261023/` and `data/omics/discrepancy-review-20261024-rules-v4-migration/`, and the review claims from PRs #212 and #215. The build passed its SHACL checks, the orphan check and the new hand-reviewed-findings check.

## Counts

| | Version 3 | Version 4 |
| --- | --- | --- |
| Live findings | 221 | 126 |
| Ordering reversals | 221 | 34 |
| Two-study conflicts | (did not exist) | 92 |
| Gap outliers | 0 | 0 |
| High / medium / low | 1 / 13 / 207 | 0 / 1 / 125 |
| Scope | cross-task 220, same-task 1 | same-task 15, unknown 87, different-task 24 |
| Listing | (did not exist) | public 15, review 111 |
| Resolved findings kept | 0 | 7 |
| Pairs of systems with a finding | 155 | 126 |

23 findings keep their version 3 ID. 54 pairs no longer fire, and 25 pairs fire that did not before. The new pairs are almost all clinical variant-effect predictors (Brandes 2023, Livesey and Marsh 2025 and others), which now share the clinical missense task.

The drop from 221 to 126 comes from counting studies, not rows. A pair that only two studies give a verdict on is now one finding, not two mirror findings. One study can no longer supply a consensus on its own. Taking one configuration per study removed others: the two Geneformer and scGPT findings no longer fire once each study uses one scGPT checkpoint.

## The hand-reviewed findings

These are the findings reviewed in PRs #212 and #215, as recorded in `scripts/kg/fixtures/labelled-findings.json`. The bundle manifest lists the same outcomes in `derived.labelled_findings`.

| Review | Finding | Version 3 | Version 4 |
| --- | --- | --- | --- |
| Real error | Alavi, AlphaGenome and Borzoi (#174) | medium, awaiting correction | resolved: its results were disputed after that release (#203) |
| Lead | PFMBench and ProteinGym, ESM-2 and ESM3 (#210) | medium, cross-task | `a2ed36d1`: two-study conflict, same-task, **medium, public** |
| Lead | Brandes, ESM-1b and EVE (#211) | medium, cross-task | `36711e25`: same ID, same-task, **low, public** |
| Explained | RNAErnie and AIDO.RNA (#209) | medium | `055eb0dd`: conflict, same-task, low, public |
| Explained | ESM-IF1 and ProteinMPNN (#201) | high | `1f1fd7fb`: conflict, different-task, low, review |
| Explained | ESM3 and ProteinMPNN, two mirrors (#205) | medium, medium | `d586dd34`: one conflict, different-task, low, review; `fed245c4` resolved |
| Explained | DNABERT-2 and RNA-FM (#202) | medium | low, unknown, review |
| Explained | Eigen and MutationAssessor | medium | low, unknown, review |
| Explained | Geneformer and scGPT, both findings | medium, medium | no longer fire; resolved |
| Explained | Mutect2 and Octopus | medium | no longer fires; resolved |
| False positive | DeepSomatic and the vote ensembles (#204) | medium | no longer fires; resolved |
| False positive | ESM-1v and ESM-2 (#207) | medium | no longer fires; resolved |

Both leads are public. Every explained finding that still fires is low, and the different-task ones are on the review list. Both false positives are gone. So the public list holds 15 findings, of which the reviewed ones are the two leads and one explained same-task conflict. The other 12 have not been reviewed yet.

## Differences from the design's predictions

- **#211 is low, not medium.** It is same-task with two consensus studies, which caps it at medium, and its configuration links are unreviewed, which takes it to low. 123 of the 126 findings have unreviewed identity, so almost everything is low. Severity now mostly reflects whether identity has been reviewed. To lift a lead, review its configuration links (a `links:configuration_of:` claim); the rules should not be loosened for it.
- **Alavi** is resolved, not a low two-study conflict, because its results were disputed after the version 3 release (#203).
- **ProteinBench and ProteinGym** needed no new task links. Their tasks were already linked to their own benchmarks, so their findings are different-task, not unknown.
- **Several mirrors cannot share one review history.** When `f82ed80f` and `fed245c4` became one conflict, only one claim chain could be carried forward (their revision 1 claims would collide), so `fed245c4` is kept as a resolved finding.

## Known limits

- **A same-task verdict can pool other tasks.** Scope is same-task when any of the two sides' assessments share a task, but each study's verdict pools all its comparisons of the pair. Wang 2026, for example, gives one verdict over its structure, classification and fitness protocols, though only the fitness ones share the RNAGym task. Pooling by task is the next refinement to consider.
- **Model size comes from names.** `parameters` holds settings text, so sizes are read from configuration names, versions, checkpoints and reported names. Only 3 findings show a variant mismatch.
- **Unknown scope is still common.** 87 findings are unknown, each listing the unlinked assessments that would decide it. That is the curation queue for #208. `npm run check:task-links` stops the number of unlinked protocols growing; it is 425 today.
- **No split-study candidates.** The manifest's `split_study_candidates` is empty on this store, once the ProteinGym sources are joined.
- **The website** still shows every finding until it reads `listing` (serving contract 3.4).
