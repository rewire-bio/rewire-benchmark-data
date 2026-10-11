# Review: lit-structure-20261011-afesmfold, 2026-10-11

Reviewer: Claude review agent `reviewer-ps-2`, independent of the extractor `lit-protein-structure`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

# Review: structure batches of the 2026-10-11 protein and structure pass (reviewer-ps-2)

Reviewer: separate Claude review agent, independent of the collector; no human review claimed. Date 2026-10-11.

## 3. lit-structure-20261011-afesmfold (216 results): approved with corrections

A1. Dimer class qualifiers (required).
- The 30 dimer "Incorrect prediction" results (`lit-structure-20261011-afesmfold-result-2-*-incorrect-prediction`) carry the monomer definition "(RMSD > 3.0 Angstrom and LDDT < 0.7)". Replace it with "(DockQ < 0.23)".
- The collector's note says the band limits are not printed. They are, in the Table 2 footnote and Methods paragraph 14. In the 90 other dimer results, replace the class part:
  - "High quality (DockQ band for high-quality interfaces, as the paper defines it)" becomes "High quality (DockQ >= 0.80)".
  - "Medium quality (DockQ band for medium-quality interfaces, as the paper defines it)" becomes "Medium quality (0.49 <= DockQ < 0.80)".
  - "Acceptable quality (DockQ band for acceptable interfaces, as the paper defines it)" becomes "Acceptable quality (0.23 <= DockQ < 0.49)".
- Add the same four bands to the description of each `lit-structure-20261011-afesmfold-protocol-2-*`, after "incorrect prediction".

A2. Evidence concerns (required). The source contradicts itself in several columns. The values are transcribed correctly and are kept. Add these entries to `lit-structure-20261011-afesmfold-source-mahtha2026` `attributes.evidence_concerns`, each with artifact_sha256 aae321d05839186a7595987d05af6e95aec5ac32b93b35c5cf1126902fe798b8 and date 2026-10-11:
1. locator "Table 1, ESMFold rows, columns 'EM' and 'NMR'; Results paragraph 17; Discussion": "The ESMFold rows give 244 EM and 107 NMR monomers, while the AlphaFold2 and AlphaFold3 rows over the same 1666 targets give 161 and 190, and the text gives 160 and 190. The Discussion says ESMFold mispredicted 139 of 190 NMR monomers, against 56 incorrect and 9 special cases in the table. The EM and NMR cells of the ESMFold incorrect row appear transposed."
2. locator "Table 1, 'Special cases' rows, columns 'XRD', 'EM', 'NMR'; Results paragraphs 24 and 27": "The text says all 11 AlphaFold2 and all 11 AlphaFold3 special cases are NMR structures; the table gives 1 XRD and 10 NMR for AlphaFold2, and 2 XRD, 1 EM and 8 NMR for AlphaFold3."
3. locator "Table 2, AlphaFold3 'Acceptable quality' row, columns 'EM' and 'NMR'": "The row prints EM 3 and NMR 37, so AlphaFold3 totals 184 EM and 49 NMR against 218 and 15 for the other tools over the same 994 targets (text: 219 and 15). The two cells appear transposed."
4. locator "Table 2, columns 'TQ 0', 'TQ 1–40', 'TQ > 40'; Results paragraph 38": "Template quality is a property of the target, yet the column totals differ by tool (TQ 0: 557, 319 and 391). For AlphaFold3 the text gives 414, 326 and 5 accurate and 153, 88 and 8 incorrect dimers by TQ band, against 228, 512 and 4, and 91, 158 and 0, in the table."
5. locator "Tables 1 and 2, row totals": "Several rows do not sum to the 'No.' column: Table 1 AlphaFold2 and AlphaFold3 accurate (method columns 1068 and 1075), ESMFold domain movement (429); Table 2 AlphaFold2 incorrect (method 230), AlphaFold3 medium (TQ 305), ESMFold acceptable (TQ 122) and incorrect (method and TQ 584)."

The 'No.' and 'pLDDT ≥ 70' columns agree with the text everywhere I checked (paragraphs 24, 27, 29, 31, 38, 40 and 60). The two protocols linked to the use case use the 'No.' column only.

A3. Monomer judgement: change `direct` to `proxy`. On `use-case-mapping-lit-structure-20261011-afesmfold-monomeric`, set `relevance` to "proxy" and replace `rationale` with: "Proxy: the protocol counts how often each tool reproduces the deposited monomer within the authors' RMSD and LDDT thresholds on targets with no close pre-2022 homologue. That is structural accuracy against an experimental structure, which the use case treats as intermediate evidence; it does not test whether a prediction improved an experimental choice, and the use case's exclusions state that structural accuracy alone does not establish that an experiment will succeed." Every other judgement on this use case is proxy for the same reason, so this keeps the use case's scope and exclusions unchanged.

A4. Constraints and limitations on both AF/ESMFold judgements (monomeric and dimeric).
- Replace "Counts, not rates: divide by the class totals in the same row block before comparing tools." with "Counts, not rates: divide by 1666 (monomers) or 994 (dimers) before comparing tools."
- On the monomeric judgement, replace the NMR constraint with: "NMR reference structures make up most AlphaFold2 and AlphaFold3 incorrect monomers (128 of 200 and 135 of 191); the ESMFold experimental-method cells conflict with the text, so do not filter ESMFold results by method."
- On the dimeric judgement, delete the NMR constraint: NMR structures are 3 of 231, 5 of 249 and 12 of 585 incorrect dimers.
- Append to `limitations` on both: "The table's experimental-method and template-quality columns conflict with the text in places (see the source's evidence concerns); the linked 'No.' column agrees with the text."
- Append to the monomeric judgement: "AlphaFold2 and AlphaFold3 were scored on their top-ranked model (ranked_0); ESMFold gives one model."
- Append to the dimeric judgement: "For dimers, the AlphaFold2 and AlphaFold3 model scored is the best of five by DockQ against the experimental structure (Methods paragraph 14), a selection a user cannot make; ESMFold gives one model, so the comparison favours AlphaFold." and "Dimers were kept when only one chain lacked a close pre-2022 homologue (Methods paragraph 6)."
- Set `reviewed_evaluations`: monomeric `lit-structure-20261011-afesmfold-eval-1-{alphafold2,alphafold3,esmfold}-no`; dimeric `lit-structure-20261011-afesmfold-eval-2-{alphafold2,alphafold3,esmfold}-no`.
- Add `comparison_group` "monomer-structures", `comparison_title` "Monomer structure predictions", `stratum_label` "Predictive classes on 1666 post-2021 monomers (Mahtha et al. 2026)" for monomers. For dimers: "protein-protein-interfaces", "Protein-protein interface predictions", "DockQ classes on 994 post-2021 dimers (Mahtha et al. 2026)".
- Then set both to `source_checked`, fill `review`, and repin.

Confirmed as extracted: the `count` concept with direction `unknown`; the monomer class definitions, including special cases as "LDDT < 0.7 and RMSD < 3.0" (Fig. 3's legend writes RMSD <= 3.0; the table footnote is the right locator); configurations (AlphaFold2 v2.2.3 local, AlphaFold3 server, ESMFold v1.0.3 is stated in Methods paragraph 8 and could be added to the ESMFold configuration's `version`, optional); and origin `independent_paper` (authors Mahtha, Venkadesan and Mohanty, NII New Delhi; no overlap with DeepMind or Meta).

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

Applied by the extractor in `extract/extract_afesmfold.py`, as the reviewer specified, before the batch was added to the store.

1. A1: the 30 dimer incorrect-prediction results carry "(DockQ < 0.23)"; the 90 other dimer results carry the reviewer's DockQ bands; each dimer protocol's description lists the four bands after "incorrect prediction".
2. A2: the source carries the reviewer's five evidence concerns verbatim, with the date in the `review_date` key used by the store's other concerns.
3. A3: the monomer judgement is `proxy` with the reviewer's rationale verbatim.
4. A4: both judgements carry the reviewer's constraint and limitation changes verbatim, `reviewed_evaluations`, comparison group, title and stratum label.
5. Optional: the ESMFold configuration's `version` is v1.0.3, as stated in Methods ("ESMFold v1.0.3 was run with default parameters").
6. Every record except the judgements is `source_checked`; each result's `review` block names the reviewer and keeps the extraction note.

## Judgements

The reviewer approved both judgements as `proxy` and also required the five evidence concerns of A2 on the source. The use-case derivation (`shared/omics/use-cases.ts`, `cleanSource`) withholds every judgement whose source has any evidence concern, and both judgements cite this source, so they cannot be served while the concerns stand, even though they use only the 'No.' column. The conflict was put to the team lead; no other instruction came back, so the review was applied literally:

- both judgements carry every A3 and A4 change, are linked from `use-case-structural-hypotheses-experiments` with `assessed_by`, and stay `needs_review` (draft), with a `reason` saying why they are not shown;
- every judgement that was active on the use case before this batch is still active.

Serving them needs a decision on the concerns: either they stay and the judgements stay drafts, or the findings move to limitations (they are already summarised in the judgements' limitations) and the judgements are re-reviewed and pinned.

## Records after correction

- benchmark: 1
- claim: 2 (relevance judgements)
- configuration: 3
- dataset: 2
- evaluation: 54
- model: 1
- protocol: 18
- result: 216
- source: 1
