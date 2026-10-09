# Unresolved rare-disease reanalysis: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-rare-reanalysis-20261009/` (904 records). Use case: `use-case-unresolved-rare-disease-reanalysis` ("Which reanalysis methods find new diagnoses or reduce review effort when given the same updated information?").

Reviewer: a separate Claude review agent that did not collect or extract the batch. No human review is claimed. Nothing was executed or reproduced; this is a check of transcription and relevance against the pinned sources.

## Outcome

- All four new source artifacts re-download to their pinned SHA-256. The archived supplement decompresses to the same bytes.
- All 711 results match their source cells: printed value, numeric value, locator, metric, qualifier, unit, direction, evaluation, configuration, protocol and dataset. No number was wrong.
- Recall, precision, F1 and F2 recompute from the TP, FN and FP cells on all 81 Vestito et al. rows, to within 5e-10 of the printed nine-digit values.
- Corrections: 3 configuration versions that the source does print, 1 configuration parameter, 81 configuration parameter notes, 1 claim wording, 1 evaluation and 1 protocol limitation, and limitations on all 9 judgements. None changes a number. Listed below.
- Privacy: the archived Demidov et al. article XML held Table 2, which lists each pathogenic CNV with pseudonymised individual and family identifiers. It was removed from the batch (see Privacy).
- The 9 judgements are confirmed as proxy and are now `source_checked` with `reviewed_evaluations` and a review. Pins are not set. Six Talos judgements now use `candidates-per-case` as their headline metric.
- Every record in the batch now has status `source_checked`.

## How the check was done

1. Downloaded each artifact into its own empty directory. The two Europe PMC `supplementaryFiles` requests returned HTTP 500, so the two supplementary PDFs were fetched from the publisher's static-content URLs. Their bytes match the pinned hashes, so they are the pinned artifacts.
2. Read Demidov et al. Table 1 from `table-wrap id="Tab1"` in the article XML with a stdlib XML reader written for this review. Read Demidov et al. Supplementary Table 4 and Vestito et al. Supplementary Table 1 from `pdftotext -layout` (poppler 26.08.0) output. The extractor's `extract/extract_rare_reanalysis.py` was not imported or run.
3. Built the expected identity of every cell from the table headers (caller or threshold pair, column, and for Table 1 whether the value is outside or inside the brackets), matched every result to its cell by ID and locator, and compared printed value, numeric value, metric, qualifier, unit, direction and the linked evaluation's configuration, protocol and dataset. Checked that each expected cell has exactly one result: 711 expected, 711 matched.
4. Arithmetic checks: Table 1 class cells sum to each row's Total for both the outside and bracketed values; Supplementary Table 4 deletions plus duplications equal all CNVs, all CNVs equal the Table 1 total for each caller, and both proportion columns recompute from the counts to two decimals; Vestito et al. rows satisfy TP + FN = 37 and TP + FN + FP + TN = 1846, form the full 9 by 9 grid from 0.1 to 0.9, and their four derived metrics recompute.
5. Read the Abstract, Results, Methods, Code availability and Author contributions of both articles to check configurations, datasets, protocols, `null` fields, origins and the five descriptive claims.
6. For the seven reused Talos protocols, read the Talos article from its PMC copy (PMC13472938) and compared all 60 Talos Table 1 values and the 8 Exomiser counts and percentages with the stored results. All match. The stored source pins the publisher page, so the PMC hash is recorded in the judgement reviews rather than compared with the stored hash.
7. Checked that the judgements' evaluations pass the evidence gates, by a dry run: `addBatch` into a scratch copy of the store, then `loadRecords` and `deriveUseCaseInputs` with the nine proposed `assessed_by` links added to the scratch use case.
8. Re-read the Kaschta et al. 2026 JATS XML (the same bytes the collector hashed) to check every statement the gap text makes. Its supplement was not downloaded.

## Sources and hashes

| Source ID | Artifact checked | SHA-256 (re-downloaded 2026-10-09) | Matches record |
| --- | --- | --- | --- |
| `rare-reanalysis-20261009-source-demidov2024` | PMC11513043 full-text XML | `8bd0d50c0f3a1018c1f5ada9088a748d27d787eb5598e9857d2ddede85854ce6` | Yes |
| `rare-reanalysis-20261009-source-demidov2024-supp` | `41525_2024_436_MOESM1_ESM.pdf` (95 pages) | `521480b4999903af5acfac1c33c9453ce1f1e5a8b641a1682c5e96e11aa577ef` | Yes |
| `rare-reanalysis-20261009-source-vestito2024` | PMC11655964 full-text XML | `b8cd48ed7e4a337ddf954d1b9bb004305ac78c383268592828e6203418d04058` | Yes |
| `rare-reanalysis-20261009-source-vestito2024-supp` | `41525_2024_456_MOESM1_ESM.pdf` (4 pages) | `d761ccee3944cd762d1c07e5388ed2810bd57634e1fc2c23a054b547a710a5ad` | Yes |
| `uc-clinical-20260930-source-talos` (stored, not re-pinned) | PMC13472938 full-text XML, read for comparison only | `219ba75789e767341d642128750be600433764d5f271db8d7c0ffb5aa6a4d1dd` | Not comparable: the record pins the publisher page |
| Kaschta et al. 2026 (not a record) | medRxiv JATS XML, version 1 | `db4ed16a501eda14ba114f8693f39596b03d7afaeafa8adafa41d84d9a61f6bd` | Same as the collector's hash |

`artifacts/demidov2024-supplementary-information.pdf.gz` decompresses to `521480b4...`. Before removal, `artifacts/demidov2024-article.xml.gz` decompressed to `8bd0d50c...`.

## Values checked

| Source table | Results | Metrics | Mismatches |
| --- | --- | --- | --- |
| Demidov et al. Table 1, three caller rows by eight columns, outside and bracketed values | 48 | count | 0 |
| Demidov et al. Supplementary Table 4, three caller rows by five columns | 15 | 9 count, 6 proportion | 0 |
| Vestito et al. Supplementary Table 1, 81 rows by eight columns | 648 | 81 each of TP, FN, FP, TN, recall, precision, F1, F2 | 0 |
| Total | 711 | | 0 |

European number formatting in Supplementary Table 4 is converted correctly on all 15 results: `1.561` is 1561, `0,35` is 0.35. The conversion is confirmed independently of Table 1 by the row sums and by recomputing the proportions (for example 2782 / 7849 = 0.354, printed `0,35`; 1221 / 2782 = 0.439, printed `0,44`).

Descriptive claims: all five match their cited paragraphs or table rows. The Table 1 `Total` and `% of Events` rows and the Supplementary Table 4 `Total` row in `claim-demidov2024-pooled-calls` match cell by cell.

## Corrections made in the batch

The batch is not yet in the store, so fields were edited in place. Previous values are kept here. A copy of the collector's `batch.jsonl` (SHA-256 `265f2e6bc21b95585fdb7d630aad6ed92a92a7a0bf8762602b1282d1f62df16c`) was compared with the reviewed file: apart from statuses and review blocks, only the fields below changed. No ID, link, source list, printed or numeric value, metric, qualifier, unit, direction, comparison, origin, relevance or endpoint changed.

1. Caller versions. The three Demidov et al. configurations had `missing_metadata.version` "unreported: No caller version is printed in the article text read". The article's Code availability section prints ClinCNV 1.16.6, ExomeDepth 1.1.15 and CoNIFER 0.2.2. `version` is now set on `config-demidov2024-clincnv`, `-exomedepth` and `-conifer`, the missing reason is removed, and "; version from 'Code availability'" is appended to each `source_locator`.
2. `config-demidov2024-conifer` parameters said batches were rerun "until the median call count was below 10". Methods 'Conifer workflow' paragraph 2 says rerun until every experiment had fewer than 30 calls or the median was below 10, after which experiments with more than 30 calls failed QC. Wording corrected.
3. ClinCNV origin. `author_reported` is correct, and the reason is stronger than recorded. Methods calls ClinCNV "developed recently by a Solve-RD partner" and cites ref. 47, which is G. Demidov's 2019 thesis; G. Demidov is the first author and is listed under Software. The limitation on `eval-demidov2024-clincnv` and on the protocol now say so. Previous text: "ClinCNV was developed by a Solve-RD partner (Methods ...), so this row is recorded as author_reported."
4. Per-caller overlap. Supplementary Table 2 describes the 'Tool' annotation given to experts: "CNVs may have been identified by more than one tool but will be shown on different rows". The per-caller counts therefore overlap, and the 7849 total counts calls, not distinct CNVs. Added to the protocol limitations and the Demidov judgement.
5. `claim-demidov2024-per-caller-detection`. Previous value said "Conifer's call was later discarded for ten of them, and ExomeDepth's for one". The source says one of those ten was also discarded by ExomeDepth. Reworded. The gene of the single Conifer-only CNV was removed: it is case-level detail and the claim does not need it. `claims.csv` updated to match.
6. The 81 Vestito et al. configurations said "Exomiser default settings otherwise (Methods 'Reanalysis optimisation')". That section does not mention settings; only 'Analysis of 100kGP samples' says default settings, for the main 24,015-case reanalysis. Now: "other settings for these runs are not stated (Methods 'Analysis of 100kGP samples' gives default settings for the main 24,015-case reanalysis)".
7. Judgement limitations rewritten on all nine (see Judgements).
8. Six Talos judgements: `headline_metric` changed from `recall` to `candidates-per-case`. For this use case the strata bear on review effort; a recall headline on known diagnoses reads too easily as yield. Recall is still shown.
9. `data/vocab/metric.ttl`: added `skos:exactMatch <http://purl.obolibrary.org/obo/STATO_0000597>` to `true-negative-count` (see Vocabulary).

If `extract/extract_rare_reanalysis.py` is rerun, it will write the collector's original wording for items 1, 2, 5 and 6. The reviewed `batch.jsonl` is the record of the batch, not the script output.

## Privacy

The brief allows no per-patient data in any file. The Demidov et al. supplementary PDF holds Supplementary Tables 1 to 5: ERN gene lists, the annotation sources given to experts, family counts per ERN, and per-tool summaries. It has no per-patient rows, so its archive stays.

The article XML's Table 2 lists the 105 potentially pathogenic CNVs one per row, with pseudonymised `Individual_ID` and `Family_ID`, coordinates, genes and status. The header was inspected to identify it; one data row was printed in the review scratch output by mistake, and that output was deleted. The batch's `artifacts/demidov2024-article.xml.gz` contained this table, so it was removed. `sources.md` now says why. The source record keeps the URL and SHA-256, and the Europe PMC XML re-downloads to that hash. No per-patient value is in any record, receipt or review file.

## Points the collector asked the reviewer to judge

1. **ExomeDepth BF > 15 against BF < 0.15.** Confirmed: Methods 'Alignment and definition of capture regions of interest' paragraph 2 says BF > 15 was required; 'ExomeDepth workflow' paragraph 2 says calls with BF < 0.15 were discarded. The two cannot both describe one cut-off, and the source does not say which was applied. It affects only how the ExomeDepth configuration is described. Its counts are printed after filtering, whichever threshold applied, so no extracted value depends on it. Agree with keeping both in `parameters` and with no evidence concern. The judgement limitation now gives both locators.
2. **Supplementary Table 5 caption swap.** Confirmed, and the swap is also in Table 5's column headers ("Length of Duplications (n=3,487)", "Length of Deletions (n=4,362)"). Supplementary Table 4 and Results 'Technical results' paragraph 3 agree with each other: 3,487 deletions and 4,362 duplications. Table 5 was not extracted and no record depends on it. Agree: no concern.
3. **European decimals in Supplementary Table 4.** Conversion correct on all 15 results (see Values checked).
4. **Vestito et al. database releases.** Results paragraph 6 compares the February 2019 and February 2022 databases and reports 54 new candidates, 31 correct, recall 84% and precision 57%. The 0.2/0.8 row prints TP 31 and FP 23 (31 + 23 = 54; 31/37 = 0.838; 31/54 = 0.574). The constant denominator of 1846 variants in every row supports reading all 81 rows as one comparison, but the table does not say so. The claim states this as an inference, and the judgement and the source record say the releases are not printed. Accept. Narrowed: the match is exact only for the 0.2/0.8 row; for the other 80 rows the release pair is an inference.
5. **Thresholds tuned on the same 37 cases.** Confirmed: Results paragraph 5 says F2 "was used for optimising the best combination of scores" on these cases, and the table is sorted by F2 with 0.2/0.8 first. Narrowed: the bias applies to reading the selected 0.2/0.8 row, which is also the recommended setting, as expected performance on new cases. The 81 values are as printed and are not affected. The judgement limitation now says this.
6. **ClinCNV author_reported.** Agree, with the stronger reason in correction 3. CoNIFER and ExomeDepth as `independent_paper` are reasonable: the first authors of their method papers (Krumm 2012, ref. 4; Plagnol 2012, ref. 6) are not among this paper's authors.
7. **Talos and Exomiser judgements reusing protocols mapped for candidate ranking.** Agree. The two use cases ask different questions of the same evaluations, and the dry run shows the seven candidate-ranking judgements stay active.
8. **Kaschta et al. 2026.** Not extracted, by the lead's decision. See Kaschta et al. 2026 below.

## Talos 194 against 190

The Results ('Comparison with other tools' paragraph 2) give 194 ACG trio families with SNV or indel diagnoses; the Extended Data Fig. 1 legend gives N = 190 for the trio panels. Every printed Exomiser percentage matches 194 and none matches 190: 172/194 = 88.7% (printed 89%; 172/190 would be 90.5%), 164/194 = 84.5% (85%), 157/194 = 80.9% (81%), 127/194 = 65.5% (65%). The conflict is therefore confined to the figure legend, whose paired panels are not extracted. No stored result depends on 190. A separate denominator also matters: Talos Table 1 recovers 177 of 196 known ACG trio diagnoses of all variant types, while the Exomiser comparison uses 194 SNV or indel families. Talos and Exomiser recall are on different denominators, and the judgements keep them in separate comparison groups. The Exomiser judgement limitation now says both things. The existing protocol limitation ("Extended Data Fig. 1 reports N=190 versus body N=194; no cross-panel pooling") stays correct.

## Judgements

Each was checked against the use case's question, inputs, output and three exclusions. All nine are proxy, and each says why. None is direct, because none measures new confirmed diagnoses per method on the same unsolved cohort. All pass.

| Judgement | Evaluations reviewed | Why proxy | Outcome |
| --- | --- | --- | --- |
| `...-demidov2024-cnv-callers` | 3 | Calls returned for review per caller on the same unsolved cohort; not diagnoses per caller | Pass; limitations add overlap and ClinCNV origin |
| `...-vestito2024-exomiser-thresholds` | 81 | Recovery of known later diagnoses (first exclusion); developer-run | Pass; tuning limitation narrowed to the 0.2/0.8 row |
| `...-talos2026-acg-trio`, `-acg-singleton`, `-acg-full`, `-rgp-trio`, `-rgp-singleton`, `-rgp-full` | 2 each | Recovery of known diagnoses (first exclusion); developer-run | Pass; limitations state plainly that recall on known diagnoses is not new yield; headline now candidates per case |
| `...-talos2026-exomiser-acg` | 1 | Recovery of known diagnoses; a rank budget is not measured effort | Pass; 194 against 190 narrowed |

None has `excluded_evaluations`: every evaluation on each protocol applies.

Exclusions:
- **Reranking known solved cases does not establish new diagnostic yield.** Vestito et al., the six Talos strata and the Exomiser comparison are all on known diagnoses. They are shown as proxy for review effort, and each judgement's first limitation now says the recall is not new diagnostic yield.
- **New knowledge, phenotypes or calls must not be counted as algorithmic improvement.** Within each comparison the information is held fixed: Demidov et al. run three callers on the same alignments with the same downstream filters, Vestito et al. vary only the flagging rule for one database pair, and Talos default and strict use the same calls. No judgement credits a method with yield that came from updated knowledge.
- **A changed database label is not a diagnosis.** Vestito et al. count flagged variants against diagnosed variants (TP) and count other flagged variants as FP. The Talos strata count recovered known diagnoses. Nothing counts a relabelled variant as a diagnosis.

Stored evidence on the seven Talos protocols: all 12 Talos evaluations and the Exomiser evaluation are `source_checked` and `author_reported`, their configurations `uc-clinical-20260930-talos-default`, `-talos-strict` and `-exomiser-v14` are `source_checked`, all 68 results are `source_checked`, and neither Talos source has evidence concerns. The candidate-ranking judgements list the same evaluations as reviewed. In the dry run, each new judgement derives exactly the evaluations listed in its `reviewed_evaluations` (3, 81, 2 per stratum and 1), and each is withheld only because its pins are not yet set.

## Kaschta et al. 2026

Kaschta et al., "Automated versus manual reanalysis in rare disease genomics", medRxiv 10.64898/2026.05.16.26352295 version 1, is the main lead for this use case and is not extracted. Statements checked against the JATS XML:

- 377 index cases (158 with P/LP findings, 49 with VUS findings, 170 with no findings). Manual reanalysis covered the 219 cases without a prior P/LP diagnosis; Talos was benchmarked on the 158 P/LP cases and then applied to the same 219 (Abstract; Results).
- Both arms added three P/LP cases (Results 'Reanalysis Diagnostic Yield'; Fig. 4 legend "41.9% to 42.7%").
- The automated paragraph prints "from 158 to 161 (+0.8 percentage points; 41.9% total diagnostic yield)"; 161 of 377 is 42.7%. The singleton paragraph gives pipeline conversion errors as 8.6%, and the Fig. 2B legend gives 9.6% (3 of 35 is 8.6%).
- Unequal inputs: the manual arm reprocessed the raw FASTQ files with DRAGEN v4.2.4 (Methods 'Manual Reanalysis' paragraph 1); Talos used the archived per-case VCFs, adapted to accept DRAGEN-annotated files "without recalling variants" (Methods 'Automated Reanalysis Using Talos' paragraphs 2 and 3).
- Review effort is measured in different units: a mean of 81 minutes per case for manual reanalysis; an average of three candidate variants per case for Talos (Results; Discussion).
- Table 1 is an image and lists individual variants. The licence statement reads "All rights reserved. The material may not be redistributed, re-used or adapted without the author's permission."

It is recorded as excluded in `data/omics/scope-audit.jsonl`, in the q3 and q9 search-ledger entries, in `research.md`, `sources.md` and `coverage.json`, and in the approved gap text below. The use case's existing gap on this preprint says full-text retrieval failed with HTTP 403. That is out of date, and the approved changes replace it.

## Vocabulary

`true-negative-count` follows the other confusion-count concepts. STATO was checked through OLS4 on 2026-10-09: `STATO:0000597` is "number of true negative", defined as "a count which denotes how many elements are correctly classified as void of a feature they are actually known to be missing". This matches the concept's definition. STATO_0000595, 0000596 and 0000598 are the TP, FP and FN terms already matched. The `exactMatch` was added. This batch's definition is exactly "Number of negative items correctly predicted as negative." and does not differ in meaning from that text. The splicing branch adds the same concept; the two blocks are to be made identical at integration. The default direction `higher` matches `true-positive-count`. Note for readers: in Vestito et al. TN is mostly the size of the non-diagnostic candidate pool (1846 variants less the flagged and diagnosed ones), so FP and precision carry the review-effort information, not TN.

## Approved use-case changes

Links and gaps only. No pinned field (question, decision, inputs, output, exclusions, setting, clinical scope, intended users) changes, so the existing Talos programme judgement `use-case-mapping-20260930-342-3c7f6c5e1873` is not affected. The dry run with the links added shows it still active.

Add to `use-case-unresolved-rare-disease-reanalysis` `links`, each with relation `assessed_by`:

- `rare-reanalysis-20261009-protocol-demidov2024-cnv-calls-for-interpretation`
- `rare-reanalysis-20261009-protocol-vestito2024-new-candidate-flagging`
- `uc-clinical-20260930-talos-acg-trio-protocol`
- `uc-clinical-20260930-talos-acg-singleton-protocol`
- `uc-clinical-20260930-talos-acg-full-protocol`
- `uc-clinical-20260930-talos-rgp-trio-protocol`
- `uc-clinical-20260930-talos-rgp-singleton-protocol`
- `uc-clinical-20260930-talos-rgp-full-protocol`
- `uc-clinical-20260930-exomiser-acg-protocol`

In `evidence_gaps`, replace the second entry ("A 2026 medRxiv automated-versus-manual comparison was discovered (10.64898/2026.05.16.26352295); full text retrieval failed with HTTP403 and indexed percentages conflict between text and caption. No measurements imported from that preprint.") with these two entries:

> Kaschta et al. 2026 (medRxiv 10.64898/2026.05.16.26352295, version 1) is the closest match to this question: manual and automated (Talos) reanalysis of the same 219 unresolved cases. Nothing was imported from it. Its per-method results are printed only in prose, its Table 1 is an image of individual variants, its supplement is per-patient data, and its licence reserves all rights.

> In Kaschta et al. 2026 the two arms did not receive equal updated inputs: the manual arm re-called variants from the raw reads with an updated DRAGEN version, while Talos used the archived variant calls. Review effort was measured as minutes per case for the manual arm and candidates per case for Talos. The prose is also inconsistent: the automated yield is printed as 41.9% where 161 of 377 is 42.7%, and one failure share is 8.6% in the text and 9.6% in the Fig. 2 legend.

Append these entries, keeping the others:

> No printed table compares several reanalysis methods by new confirmed diagnoses on the same unsolved cohort.

> The Solve-RD CNV reanalysis (Demidov et al. 2024) tables count the calls each caller returned for review. Calls found by more than one caller are counted once per caller, and per-caller detection of the confirmed pathogenic CNVs is printed only in the text.

> The Exomiser flagging thresholds (Vestito et al. 2024) and the Talos evaluation cohorts are scored on diagnoses already known, which the first exclusion keeps out of new-yield evidence. The Exomiser thresholds were also chosen on the same 37 cases they are scored on.

> AMELIE 3 (medRxiv 2020.12.29.20248974) reports alerts per patient per year, but its tables are images; not extracted.

> Genet Med 2022 (Moon versus Exomiser on 80 nondiagnostic exomes) and J Mol Diagn 2019 (automated exome reanalysis) were not open access and were not retrieved.

## Evidence summary

Final text for the use case's `summary` claim (source IDs `rare-reanalysis-20261009-source-demidov2024`, `rare-reanalysis-20261009-source-vestito2024-supp`, `uc-clinical-20260930-source-talos-table1`). It is reviewed text for a later claim; no summary record was added in this batch.

> No study found so far compares reanalysis methods by new confirmed diagnoses on the same unsolved cohort in a printed table, so this evidence cannot show which method finds more new diagnoses. The closest study, a 2026 preprint comparing manual and automated reanalysis of the same cases, reports its results only in prose and is not included. The printed comparisons measure review workload, or recovery of diagnoses that were already known. In the Solve-RD CNV reanalysis of unsolved exomes, three callers returned different numbers of calls for expert review: ExomeDepth 4205, ClinCNV 2782 and CoNIFER 862. These counts overlap where callers found the same CNV, thresholds differ by caller, and ClinCNV was developed by the study's first author. In 100,000 Genomes Project cases diagnosed after a new disease-gene association, the Exomiser developers' recommended flagging rule (phenotype score increase 0.2, variant score 0.8) flagged 31 of the 37 diagnostic variants and 23 other variants, while the loosest rule tested flagged all 37 and 182 others; the rules were chosen on these same cases. In the Talos developers' ACG trio cohort, strict phenotype filtering returned 403 candidate variants instead of 487 and recovered 164 known diagnoses instead of 177. The known diagnoses come from each cohort's earlier analysis, and Talos recovery counts only diagnoses its own calling pipeline could detect. Recall on known diagnoses is not new diagnostic yield, each comparison was reported by the developers of at least one method compared, and none is clinical validation.

| Number in the text | Result ID |
| --- | --- |
| 4205, 2782, 862 | `rare-reanalysis-20261009-result-demidov2024-exomedepth-total`, `-clincnv-total`, `-conifer-total` |
| 0.2, 0.8; 31 of the 37; 23 | `rare-reanalysis-20261009-result-vestito2024-dh2-vs8-tp` (31), `-dh2-vs8-fn` (6, so 37), `-dh2-vs8-fp` (23); thresholds are the evaluation's configuration `rare-reanalysis-20261009-config-vestito2024-exomiser-13-1-0-dh2-vs8` |
| all 37; 182 | `rare-reanalysis-20261009-result-vestito2024-dh1-vs1-tp` (37), `-dh1-vs1-fp` (182) |
| 403, 487 | `uc-clinical-20260930-talos-acg-trio-strict-candidate-variants`, `uc-clinical-20260930-talos-acg-trio-default-candidate-variants` |
| 164, 177 | `uc-clinical-20260930-talos-acg-trio-strict-diagnoses`, `uc-clinical-20260930-talos-acg-trio-default-diagnoses` |
| 2026, 100,000 | Publication year and project name, not measurements |

The draft in `coverage.json` was revised. It said "In 37 100,000 Genomes cases" and gave the cohort size 9171, which traces to a dataset record rather than a result. It did not say that the caller counts overlap, that ClinCNV is the first author's tool, that the thresholds were chosen on the same cases, or how the known-diagnosis truth sets were built.

## Remaining gaps

- No comparison of new diagnoses across methods on the same cohort is available in a printed table. Kaschta et al. 2026 is the only same-cohort comparison found, and it is prose-only with unequal inputs.
- Figures were not read. Demidov et al. Fig. 3 (lengths of the pathogenic CNVs by caller, including calls later removed by QC) and Talos Extended Data Fig. 1 (paired Talos and Exomiser counts) remain unchecked.
- Demidov et al. also report a mean of 5 minutes of expert interpretation per CNV (Methods 'Clinical interpretation'), pooled over callers. It is noted in the workload claim review and the judgement, not recorded as a result.
- Vestito et al. report precision 88% and recall 82% when the ACMG/AMP classifier is added (Results paragraph 6). This is not in Supplementary Table 1 and is not recorded as a result; the protocol limitation says so.
- The ExomeDepth threshold (BF > 15 or BF < 0.15) is unresolved.
- Not covered by the batch: closed-access reanalysis comparisons, AMELIE 3 values, false alerts per method over repeated cycles, and LIRICAL, Xrare, PhenIX, VarSeq or GEM on unsolved cohorts.
- `npm test` and `npm run typecheck` results are in the receipt. `npm run build` was not run, by instruction (disk limit); the dry run above stands in for the store checks.
