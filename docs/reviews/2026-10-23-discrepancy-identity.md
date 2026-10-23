# Discrepancy identity, gap reference and exclusions, 2026-10-23

Rules version 3 (`data/ontology/discrepancy-rules.json`). Issue #174.

Checked on the store at release `2026-10-23-a1a0ac69daa3` plus this change.

## Changes

| Change | Why |
| --- | --- |
| A discrepancy's ID hashes a canonical key: rule, the two systems after configuration, family and alias resolution, anchor, metric and the outlier study's key | Version 2 hashed the smallest source IRI of the outlier study, so the ID changed when a source joined the study. |
| The study key is the lowest DOI among the study's sources, else the lowest GitHub repository URL, else the source with the earliest `retrieved_at` (tie-break: ID) | None of these change when another source joins the study. |
| A `discrepancy_review` claim can list `previous_ids`; the build maps them forward to its `discrepancy_id` | Lets a review follow its discrepancy when the key changes. |
| The build fails when an accepted, unsettled review claim names an ID that is neither derived nor mapped forward | Version 2 silently dropped such a review. A settled claim whose discrepancy no longer fires is retired and listed in the manifest, since a confirmed error stops firing once its results are disputed. |
| The gap rule compares each system with a reference that every study in the group measured, preferring a named baseline | Version 2 used the second system in IRI order as the reference. A group without a shared reference is skipped. |
| Results marked `disputed`, and results covered by a source's `evidence_concerns`, are left out | A recorded error stops raising the same lead. |

Thresholds are unchanged.

## Results

| | Version 2 (release `2026-10-23-a1a0ac69daa3`) | Version 3 |
| --- | --- | --- |
| Discrepancies | 254 | 221 |
| Ordering reversals | 254 | 221 |
| Gap outliers | 0 | 0 |
| High, medium, low | 1, 17, 236 | 1, 13, 207 |
| Results left out as disputed | not checked | 0 |
| Results left out under an evidence concern | not checked | 6712 |

- 37 version 2 reversals no longer fire (32 low, 5 medium), because results under evidence concerns are now left out of the outlier study or of the consensus. The outlier studies most affected are ViroBench (Ye 2026, 16; its source carries two source-wide concerns) and the GENE-B leaderboard (12).
- 4 reversals are new: leaving out concerned results changed the consensus they are measured against. 3 findings changed severity (2 low to medium, 1 medium to low).
- The gap rule still finds none. No group of three or more studies of one metric on one protocol or task shares a reference system and has a study more than 0.10 outside the others' range.
- The Alavi finding keeps its review: `awaiting-correction`, medium.

## Re-keyed review

`discrepancy-review-20261022-alavi-alphagenome-splicing` named `discrepancy-ead251c24ba272c1`, the version 2 ID of the Alavi 2026 AlphaGenome against Borzoi reversal. Under version 3 the same finding is `discrepancy-52a714eb6bb63442` (outlier study key `doi:10.64898/2026.10.02.756289`). The claim now names the new ID and keeps the old one in `previous_ids`. It also records `action: reported-upstream`, the step its `report_url` and `reported_on` (2026-10-19) already describe. Its state, dates and rationale are unchanged. Recorded with `npm run records -- change`.

## Known limits

- The study key uses `retrieved_at` where a study has no DOI and no repository URL. Records carry no creation date, and `retrieved_at` is the closest stable field.
- An ordering reversal pools every comparison of its two systems, so its key has no anchor or metric.
- Automated change by a Claude agent; no human review is claimed.
