# Review: lit-structure-20261011-scaffoldlab, 2026-10-11

Reviewer: Claude review agent `reviewer-ps-2`, independent of the extractor `lit-protein-structure`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

# Review: structure batches of the 2026-10-11 protein and structure pass (reviewer-ps-2)

Reviewer: separate Claude review agent, independent of the collector; no human review claimed. Date 2026-10-11.

## 1. lit-structure-20261011-scaffoldlab (160 results): approved with corrections

S1. Designability mapping (collector question 3). The store's `designability` concept is defined as scRMSD below 2 Angstrom. Scaffold-Lab uses sc-TM above 0.5, so reusing that concept carries a definition the source contradicts. There is a second problem. Equation (1) in the Metrics section makes success a per-backbone outcome (mean sc-TM of the top 3 sequences above 0.5), with 100 backbones per length. That would give two-decimal fractions, but Table 3 prints three-decimal values (0.691, 0.956) and calls them "mean values within each group". The table does not say whether the column is the share of designable backbones or a mean sc-TM. Keep the concept and the values, but block automatic comparison:
- On all 28 designability results (`lit-structure-20261011-scaffoldlab-result-designability-*`) and on `lit-structure-20261011-scaffoldlab-protocol-designability`, replace the start of `metric_qualifier` up to the length suffix with: "Table 3 'Designability' column, printed as a group mean without data preprocessing; the Metrics section counts a backbone as designable when the mean sc-TM of its top 3 ProteinMPNN sequences refolded with ESMFold exceeds 0.5 (equation 1); the table does not state whether the value is the share of designable backbones or a mean sc-TM; not comparable with the 2 Angstrom sc-RMSD criterion in the concept definition". Keep the existing "; length N" suffix on results.
- Add to `lit-structure-20261011-scaffoldlab-source-zheng2026` `attributes.evidence_concerns` one entry: source_id the same, message "Table 3 Designability column: equation (1) defines a per-backbone success over 100 backbones per length, which gives two-decimal fractions, but the column prints three-decimal group means; the aggregation behind the column is not stated, and the criterion is sc-TM above 0.5, not the 2 Angstrom sc-RMSD in the store's designability concept. Do not compare these values with other designability results.", source_locator "Table 3, column 'Designability(↑)'; Metrics, equation (1)", artifact_sha256 9ff68ef80dc57d6ef85920d4d2104e86d071215ac9c74367a72b2a85669840d0, date 2026-10-11.

S2. Vocabulary (collector question 2). Both concepts are approved. In `:rank`, delete `skos:altLabel "Rank"@en`, which only repeats the prefLabel. `:topsis-relative-closeness` is approved as written. Neither concept carries an external mapping, which is correct.

S3. Add to the source record's `limitations`: "The acknowledgements thank Brian L. Trippe, an author of FrameDiff, for contributing to the Scaffold-Lab codebase; he is not an author of this paper." Origin stays `independent_paper`: none of the nine authors (Zheng, Zhang, Zhong, Yu, Liu, Li, Zhu, Wei, Chen) is an author of Chroma, FrameDiff, FrameFlow, Genie or RFdiffusion.

Confirmed as extracted: novelty as `tm-score` with direction lower and the pdb-TM qualifier; diversity as `proportion`; efficiency as `runtime` with `unit-unreported` (question 4: agreed, because the table prints no unit and "several minutes" in the text is not a unit statement); Ci, mean Ci and rank. The four new model families (Chroma, FrameDiff, FrameFlow, Genie) do not duplicate any model record. The store holds ProteinBench and Genie 3 configurations with those names but no family records; linking them is optional later work, not a correction.

No use-case judgement was proposed for this batch.

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

Applied by the extractor in `extract/extract_scaffoldlab.py` and `data/vocab/metric.ttl`, as the reviewer specified, before the batch was added to the store.

1. S1: the 28 designability results and the designability protocol carry the reviewer's qualifier verbatim, results keeping their "; length N" suffix. The source carries the reviewer's evidence concern verbatim, with the date in the `review_date` key used by the store's other concerns.
2. S2: `skos:altLabel "Rank"@en` removed from `:rank`; `:topsis-relative-closeness` unchanged.
3. S3: the source's limitations include the acknowledgement note verbatim. Origin stays `independent_paper`.
4. Every record is `source_checked`; each result's `review` block names the reviewer and keeps the extraction note.

## Records after correction

- benchmark: 1
- configuration: 5
- dataset: 1
- evaluation: 160
- model: 4
- protocol: 7
- result: 160
- source: 1
