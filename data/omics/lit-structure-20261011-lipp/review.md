# Review: lit-structure-20261011-lipp, 2026-10-11

Reviewer: Claude review agent `reviewer-ps-2`, independent of the extractor `lit-protein-structure`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

# Review: structure batches of the 2026-10-11 protein and structure pass (reviewer-ps-2)

Reviewer: separate Claude review agent, independent of the collector; no human review claimed. Date 2026-10-11.

## 2. lit-structure-20261011-lipp (27 results): approved with corrections

L1. Duplicate source (required). The store on main already holds this artifact twice, both with SHA-256 6ff34f2f...414e: `evidence-expansion-p2-lipp-2026-6ff34f2f709a` (source_checked) and `lipp-2026` (discovered). Do not add a third. Replace `lit-structure-20261011-lipp-source-raza2026` with `evidence-expansion-p2-lipp-2026-6ff34f2f709a` everywhere in the batch (`source_ids`, `citation_locators[].source_id`) and remove the new source record. This also fixes the slug: the first author is Li-Yen Yang, not Raza. Move the new record's three `limitations` onto the existing source through `records change`, with the corrected count from L3.

L2. Duplicate results (required). Two stored source_checked results duplicate cells in this batch: `lit-041` (Chai-1, 60.7) and `lit-042` (DiffDock-L, 46.8), both Table 2, full LiPP set. Their values are correct. The new records add the confidence interval and the protocol link, so keep the new ones. Add link `{"relation": "supersedes", "target_id": "lit-041"}` to `lit-structure-20261011-lipp-result-rmsd-lipp-331-chai-1`, and `{"relation": "supersedes", "target_id": "lit-042"}` to `lit-structure-20261011-lipp-result-rmsd-lipp-331-diffdock-l`. Set `lit-041` and `lit-042` to status `superseded` via `records change`. The values of the old records are not edited.

L3. Dash count (question 5). Leaving out the `-` cells is right: they mean "not evaluated", not a result. The count is wrong, though. The tables hold 13 dash cells, 4 in Table 2 and 9 in Table 3, not 7 and 13 (and not 20 as the report says). In the source limitation, replace "7 cells in Table 2 and 13 in Table 3" with "4 cells in Table 2 and 9 in Table 3". Fix research.md and the report the same way.

L4. PoseBusters protocols describe lipid poses. PoseBusters v1 and v2 are protein-small molecule sets, and these values come from the literature, so this source does not state the pose selection.
- `lit-structure-20261011-lipp-protocol-rmsd-posebusters-v1-428` and `-v2-308`: set `description`, `attributes.protocol` and `success_threshold.criterion` to "Success is a predicted small-molecule ligand pose with RMSD below 2 Angstrom to the experimental pose, as reported in the publication the LiPP authors cite. Pose selection and the RMSD atom set follow that publication and are not stated in this source." Append " Evaluated on PoseBusters v1." or " Evaluated on PoseBusters v2." to the description only.
- `lit-structure-20261011-lipp-protocol-pb-valid-posebusters-v2-308`: the same, with "RMSD below 2 Angstrom and a PoseBusters-valid pose" in place of "RMSD below 2 Angstrom".
- `lit-structure-20261011-lipp-protocol-pb-valid-posebusters-v1-428` has no value (every cell is a dash) and no evaluation. Remove it.
- The six `lit-structure-20261011-lipp-result-rmsd-posebusters-*` results: in `metric_qualifier`, replace "lipid pose all-atom RMSD below 2 Angstrom" with "ligand pose RMSD below 2 Angstrom, as reported in the cited literature".

L5. Dataset locators. `lit-structure-20261011-lipp-data-posebusters-v1-428` and `-v2-308` quote "N denotes the total number of lipid-protein complexes", which is wrong for those sets. Set their `source_locator` to: "Tables 2 and 3 column headings; Table 3 footnote a ('N denotes the total number of complexes in each dataset')".

Question 6 (origins): agreed. The LiPP columns are the authors' own runs, `independent_paper`; none of the four authors (Yang, Gupta, Mullininx, McShan, Georgia Tech) developed AlphaFold 3, Chai-1, RoseTTAFold AA, DiffDock-L or AutoDock Vina. The PoseBusters columns are `paper_compilation`. The 2019-09-30 cutoff note is on both AlphaFold 3 PoseBusters evaluations. Question 7: the two dagger-prefixed `printed_value` strings match the rendered PMC table exactly.

The 22 confidence intervals match the printed bounds and are tagged 95% exact binomial. Note for readers: some 36-complex percentages are truncated, not rounded (11 of 36 prints as 30.5, 6 of 36 as 16.6, 1 of 36 as 2.7). The printed values are kept.

L6. Relevance judgements: both `proxy` judgements on `use-case-structural-hypotheses-experiments` are approved, with these additions.
- `use-case-mapping-lit-structure-20261011-lipp-rmsd-lipp-test-36`: set `reviewed_evaluations` to the five `lit-structure-20261011-lipp-eval-rmsd-lipp-test-36-{alphafold-3,autodock-vina,chai-1,diffdock-l,rosettafold-aa}`.
- `use-case-mapping-lit-structure-20261011-lipp-pb-valid-lipp-test-36`: set `reviewed_evaluations` to the five `lit-structure-20261011-lipp-eval-pb-valid-lipp-test-36-{alphafold-3,autodock-vina,chai-1,diffdock-l,rosettafold-aa}`.
- Append to `limitations` on both: "Several printed test-set percentages are truncated rather than rounded (for example 11 of 36 printed as 30.5); the values are kept as printed." and "The full LiPP set and the PoseBusters columns are not linked to the use case: the full set includes complexes inside some tools' training windows, and the PoseBusters values are literature compilations on drug-like ligands."
- For consistency with the existing reviewed judgements, add on both: `comparison_group` "lipid-protein-poses", `comparison_title` "Lipid-protein pose predictions", `stratum_label` "Lipid poses on 36 post-cutoff complexes (LiPP)"; `stratum_order` 1 for RMSD and 2 for PB-valid. Keep them out of "protein-ligand-poses": the use case treats complex classes separately.
- Then set both to `source_checked`, fill `review`, and repin with `npm run use-cases:repin`.

## Use-case summary and field changes

The collector proposed no summary text and no use-case field change. The approved use-case summary for `use-case-structural-hypotheses-experiments` stays as it is in the store, verbatim and unchanged. It is still accurate, but once the four new links are applied it will not mention them. A collector should draft a revised summary in a later pass for a separate review, and the draft should name the post-2021 AlphaFold and ESMFold counts and the LiPP test set. I did not draft one, so that a later review stays independent. No change to inputs, exclusions or other use-case fields is approved; every judgement here fits as proxy.

## Checks run and outcomes

- Source hashes: all three JATS files re-retrieved from Europe PMC fullTextXML. SHA-256 matches the source records for all three: 9ff68ef8...840d0 (Scaffold-Lab), 6ff34f2f...414e (LiPP), aae321d0...98b8 (AF/ESMFold).
- Automated full comparison with my own parsers (an ElementTree table grid with rowspan and colspan, then locator-keyed cell matching), not the collector's scripts. Scaffold-Lab: 140 of 140 per-length cells match on printed and numeric value; 20 of 20 mean Ci and rank records equal every repeated cell in their group; mean Ci recomputed from per-length Ci for all 10 groups and consistent. LiPP: 27 of 27. AF/ESMFold: 216 of 216. Totals: 403 of 403 values match, and 22 of 22 LiPP intervals match their bounds and level.
- Completeness: every numeric cell of Scaffold-Lab Table 3 (160), LiPP Tables 2 and 3 (27, plus 13 dash cells) and AF/ESMFold Tables 1 and 2 (216) maps to a result; none was missed.
- Hand sample against the rendered PMC article HTML, read through a separate HTML parser: 45 Scaffold-Lab values (all seven columns, all three length groups, all five methods), all 27 LiPP values (both tables, all four columns, all five tools) and 48 AF/ESMFold values (both tables, every column, all three tools). All 120 match.
- Internal consistency of the AF/ESMFold tables: row and column totals and text cross-checks; findings in A2.
- Metric, qualifier, direction, unit, uncertainty, denominator, dataset and split: checked against the Methods text of each paper; findings in S1, L4, L5 and A1.
- Origin and author overlap: author lists and affiliations read from each JATS file; competing-interest statements read where present; findings in S3 and the LiPP and AF/ESMFold notes.
- Locators: every result locator resolves to exactly one cell, or to one repeated group cell for mean Ci and rank. Dataset locator fix in L5.
- Duplicates. Main store: models, configurations and sources searched by DOI, PMC id and name; LiPP duplicates found (L1, L2), none for the other two. Other open branches (`claude/lit-20261011-*`, 13 besides this one): files changed relative to main searched for the three DOIs and PMC ids; no hits. Worktrees `../rewire-benchmark-data-lit-*`: hits only in files inherited from main (audit receipts, search ledger, legacy review); no new batch for these sources.
- Relevance judgements: endpoints compared with the use case's inputs, output, setting and exclusions, and with the 11 existing reviewed judgements on that use case; findings in L6, A3 and A4.
- Not run: npm test, typecheck and build. I was told not to edit records, and the collector reports the batches already pass `records add`. The collector should run all three after applying the corrections.

## Corrections applied

Applied by the extractor in `extract/extract_lipp.py` and `extract/apply_store_changes.py`, as the reviewer specified.

1. L1: the batch cites `evidence-expansion-p2-lipp-2026-6ff34f2f709a` everywhere and adds no source record. The three source limitations, with the corrected count, were added to that record (`apply_store_changes.py`, recorded with `records change`), and `corrections.jsonl` holds the `metadata-correction-` claim keeping the previous value (absent).
2. L2: `...-result-rmsd-lipp-331-chai-1` and `...-result-rmsd-lipp-331-diffdock-l` supersede `lit-041` and `lit-042`, which are set to `superseded` with `records change`. Their values are not edited.
3. L3: dash cells are 4 in Table 2 and 9 in Table 3, in the source limitation, `research.md` and the pass report.
4. L4: the PoseBusters protocols carry the reviewer's description, protocol and criterion text; the empty PB-valid v1 protocol is removed; the six PoseBusters RMSD results carry the reviewer's qualifier wording.
5. L5: the two PoseBusters datasets carry the reviewer's locator.
6. L6: both judgements carry the five `reviewed_evaluations`, the two added limitations, and the comparison group, title, stratum label and order. Both are `source_checked`, linked from `use-case-structural-hypotheses-experiments` and pinned with `npm run use-cases:repin`.
7. Every record is `source_checked`; each result's `review` block names the reviewer and keeps the extraction note.

## Records after correction

- benchmark: 1
- claim: 2 (relevance judgements), plus 1 metadata-correction claim in `corrections.jsonl`
- configuration: 5
- dataset: 4
- evaluation: 27
- model: 1
- protocol: 7
- result: 27
