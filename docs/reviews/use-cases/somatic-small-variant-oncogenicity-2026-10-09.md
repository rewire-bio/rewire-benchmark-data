# Somatic small-variant oncogenicity: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-somatic-oncogenicity-20261009/` (1,193 records as extracted, 1,191 after the duplicate removal below). Use case: `use-case-somatic-small-variant-oncogenicity`. `batch.jsonl` as extracted: SHA-256 `1d9dd8b7b7cdaeea2ecfea775391df92df2075775f03cbd0b1abf0983a9fb487`; as reviewed: `97cc12d84ab9adb743fc3611d38abc0196bc6b6ba64bc37d86444771ce20943f`; after the duplicate removal (final): `98a3b2998df30b5e652051d39076804d6e38729b8736bd51c6369f4145c75bbb`. The receipt is `review.json` in the batch folder. The 2026-10-08 file of the same name is the earlier search dossier, not this review.

Reviewer: a separate Claude review agent that did not collect or extract the batch. No human review is claimed. Nothing was executed or reproduced.

## Outcome

- All eight source artifacts match their pinned SHA-256, and the archived `artifacts/*.gz` decompress to the same bytes. The bioRxiv page re-downloaded with different bytes, as its source record warns; the differences are per-request CDN tokens in links, and the extracted text is identical to the archived copy.
- All 794 results match their source cells. No value, printed value, locator, configuration or protocol link was wrong.
- No result is disputed and no evidence concern was raised.
- Corrections, none of which changes a printed or numeric value: the Chen ±2σ ranges are no longer stored as confidence intervals; the four CanDrA evaluations are `author_reported`; the OncoKB qualifier no longer asserts an unstated positive set; the Lee "AUPRC" column is recorded as `average-precision`, and Lee AUROC and average precision as `unitless`; the Lee metric implementation is filled from the code; 46 method-type assignments are corrected.
- The two Chen median-threshold judgements change from `direct` to `proxy`. All 7 judgements are `source_checked` with `reviewed_evaluations`; pins are left unset.
- `negative-predictive-value` now carries the reviewed block from the RNA pathogen branch, byte for byte.
- Use-case changes are links, sources, citations and gaps only. No pinned field changes, so the four OncoVI judgements are unaffected.

## How the check was done

1. Downloaded each artifact URL into its own empty directory and hashed it. Python ran with `-I` from scripts kept outside those directories.
2. Wrote a new check script (`check.py` in the review scratch area); the extractor's `extract/*.py` were not imported or run.
   - Chen Additional files 9, 10, 21 and 22: read the cell XML directly. The script asserts the single sheet, the headers `Algorithm`, `Accuracy (±2σ)`, `Sensitivity (±2σ)`, `Specificity (±2σ)`, `PPV (±2σ)` and `NPV (±2σ)`, and 33 or 17 rows. It parses every cell as `d.dd (d.dd-d.dd)` and checks the 17 default-category algorithms against Additional file 1.
   - OncoCal `tool_performance.tsv`: split on tabs, asserting the header and 147 rows (49 tools in each of `all`, `oncogene`, `TSG`).
3. Matched every result to exactly one cell through its evaluation's configuration (`reported_name`) and protocol. Then compared printed and numeric value, printed range, metric (from the column), unit, direction, locator (file, cell, algorithm; or tool, group, column), source list, and for Lee the evaluation's `denominator` and `positive_count` against `n` and `pos`.
4. Read Chen's Results, Methods, reference list and competing interests, and the Lee preprint text. At the pinned commit, read the OncoCal code that writes the table (`src/evaluation/part_b.py`) and classifies tools (`src/evaluation/reclassify_tools.py`), plus the repository history through the GitHub API.
5. Ran the edited batch through `addBatch` (`scripts/omics/records.ts`) against a scratch copy of the store; all 1,193 records were accepted, and after the duplicate removal all 1,191 (SHACL not run). In the same scratch store I applied the use-case changes below, pinned the claims with `claimPins` and ran `deriveUseCaseInputs`. All 11 judgements on the use case (4 OncoVI, 7 new) are active, and the summary is published.
6. `npm test` (499 of 499) and `npm run typecheck` pass. `npm run build` was not run, by instruction.

## Sources and hashes

| Source ID (`somatic-oncogenicity-20261009-source-` prefix) | Artifact | SHA-256 | Matches record |
| --- | --- | --- | --- |
| `chen2020` | PMC7033911 full-text XML | `fef52f70c3a0ff3f82902f87080933c220e12274787de6309b41ee283daf8b8e` | Yes |
| `chen2020-additional-file-1` | MOESM1_ESM.xlsx | `483840c2546f42b3517bcbcd583a3af083df45470e35e4955eda260a19152b09` | Yes |
| `chen2020-additional-file-9` | MOESM9_ESM.xlsx | `64b284aefb768c963a5e7079594d3bb7173ef3a5a5e6b0936d0a78126f25440c` | Yes |
| `chen2020-additional-file-10` | MOESM10_ESM.xlsx | `b9c41136f45b38533312baa4abfe2923390861c4e49d4d91c6d0275a85222294` | Yes |
| `chen2020-additional-file-21` | MOESM21_ESM.xlsx | `47c4d461085334b017994d1846ceb06d6e44e7be369ecd2ecfe00620d6a0f7f5` | Yes |
| `chen2020-additional-file-22` | MOESM22_ESM.xlsx | `21ed28f45eee2149e88dff6b75680c99001c4b6daa9805cc9e473d2300ae117a` | Yes |
| `lee2026` | bioRxiv full-text HTML, v1 | `1b4dfadc861c6b8dbecde6ebb5efdb5ab7203bcf6f1b4e06edc70e167e7050e9` (archived copy) | Archived copy yes; a fresh download is `b9df3a90...`, differing only in CDN tokens |
| `lee2026-oncocal-tool-performance` | `tables/tool_performance.tsv` at `40b7770f2a768ba800c4f4c6b48e2bfe967ed14a` | `8f5a81078482c8010b83bba6225e9707980a3a7cebbb2ca00ed8b155ad34c3b5` | Yes |

## Values checked

| Source table | Results | Metrics | Mismatches |
| --- | --- | --- | --- |
| Chen Additional file 9 (benchmark 2, median threshold) | 165 | accuracy, recall, specificity, precision, NPV for 33 algorithms | 0 |
| Chen Additional file 10 (benchmark 2, default calls) | 85 | same, 17 algorithms | 0 |
| Chen Additional file 21 (benchmark 5, median threshold) | 165 | same, 33 algorithms | 0 |
| Chen Additional file 22 (benchmark 5, default calls) | 85 | same, 17 algorithms | 0 |
| OncoCal tool_performance.tsv | 294 | AUROC and average precision, 49 tools by 3 groups | 0 |
| Total | 794 | | 0 |

The 147 Lee evaluations' `denominator` and `positive_count` match `n` and `pos`. Consistency checks: 42 of 49 tools have a lower oncogene AUROC than TSG AUROC, as the preprint states; the top all-gene AUROCs are MutScore 0.8760, VARITY_R 0.8744, VARITY_R_LOO 0.8726, ClinPred 0.8695 and AlphaMissense 0.8679, matching the preprint's "MutScore 0.876, VARITY_R 0.874, ClinPred 0.869, AlphaMissense 0.868". Chen Results values (PROVEAN, VEST4, MPC accuracy 0.69, 0.69, 0.68; DEOGEN2 default 0.70; CTAT-cancer, PrimateAI, CHASM 0.70, 0.70, 0.69 on benchmark 5) agree with the tables. Every Chen range is symmetric about its mean to rounding (exact decimal check, none differs by more than 0.02).

## Collector's concerns

1. **Chen OncoKB counts.** Confirmed. Results 'Benchmark 2' give 773 oncogenic and 497 likely neutral (and 2,327 oncogenic or likely oncogenic). Methods 'OncoKB annotation benchmark' give 816 oncogenic, 1,384 likely oncogenic and 421 likely neutral after excluding 271 inconclusive. Results say Additional file 9 uses "randomly selected 400 positives and 400 negatives", but neither the Results nor the captions of Additional files 9 and 10 say which positive set. The batch named the protocols, results and dataset "OncoKB oncogenic versus likely neutral", which asserts the first set. That is now "OncoKB benchmark (positive set not stated)". The dataset note gives both sets of counts, and the limitations add that 400 negatives drawn from 421 or 497 overlap heavily between repeats. The values are unaffected, so no concern was raised.
2. **±2σ ranges.** The Methods say the 100 repeats were used "to calculate standard deviations", and the headers say "(±2σ)", so each range is the mean plus or minus two standard deviations. That is not a confidence interval. The schema's types do not fit: `confidence_interval` would misstate it, and `standard_deviation` requires a `value` with no bounds, which would mean deriving an SD from bounds rounded to two decimals. So the structured `uncertainty` was removed from all 500 Chen results and replaced with `missing_metadata.uncertainty` (`unextracted`) and a note explaining the printed range. The range itself stays in `printed_source_cell`. A later schema change could add a "mean plus or minus k standard deviations" form.
3. **Median-score threshold.** Accepted as a problem with the endpoint, not the values. The threshold is the median of each tool's scores on the very draw being scored. With balanced draws this forces sensitivity, specificity, PPV and NPV close together (PROVEAN on file 9: 0.70, 0.68, 0.69, 0.70), so the tables rank tools rather than test a threshold a reviewer could apply. Both median-threshold judgements are now `proxy`, and the default-call strata now come first in each group (stratum order 1).
4. **VARITY_R 0.871 against 0.874.** Confirmed. Results first section: "MutScore 0.876, VARITY_R 0.874, ClinPred 0.869, AlphaMissense 0.868", which match the table. The OncoCal section and its figure legend: "VARITY_R 0.871; AlphaMissense 0.870". The OncoCal models are trained on "unique protein keys" (20,815 protein-level entries), while the table counts labelled variant rows (for example 22,791 for AlphaMissense), so the second pair probably comes from that protein-level set. That is an inference. The table is kept, and the limitation and the VARITY_R result note say so.
5. **AI-assistant credit and reproducibility.**
   - The pinned commit (40b7770f, 2026-07-11) has a `Co-Authored-By: Claude Opus 4.8` trailer. It adds `scripts/revision/` and updates the README; it does not touch `tables/tool_performance.tsv` or `src/evaluation/part_b.py`.
   - The table was added in the first commit, b17e658d6b (2026-06-18), which has no such credit. Its blob (`0de8d73a...`) is identical at all three commits.
   - `part_b.py` changed once after that (fc73fd7b74), and only to translate comments from Korean to English.
   - The table is written by `b1_tool_performance` in `part_b.py`: scikit-learn `roc_auc_score` and `average_precision_score` on each dbNSFP rank score, skipping tools with fewer than 50 variants or one class. Its input, `data/processed/dataset.parquet`, needs dbNSFP 5.3.1a and COSMIC v104, which the repository does not redistribute.
   - So the table cannot be regenerated from the repository alone. I did not regenerate it.
   - This is now a limitation on the three Lee protocols and judgements. The AI credit is a fact about a later commit, not evidence about the table.
6. **Method types.** Checked against Chen Table 1 descriptions (as transcribed on the Chen configurations) and against OncoCal `reclassify_tools.py`, which lists the tools scored without clinical labels with a rationale. Method records had defaulted to `supervised_machine_learning` even where their own configurations said otherwise. Final assignments:
   - `foundation_model`: ESM1b (configuration was right; method record was supervised).
   - `specialist` (scores not trained on labelled variants): SIFT, SIFT4G, PROVEAN, MutationAssessor, LRT (sequence homology or alignment scores, Chen Table 1); FATHMM-cancer and FATHMM-disease (hidden Markov models on sequence homology, Chen Table 1); GenoCanyon and Integrated_fitCons (unsupervised statistical models); Eigen and Eigen-PC (unsupervised spectral, Chen Table 1 and OncoCal); CTAT-cancer and CTAT-population (principal components of other tools' scores, Chen Table 1); TransFIC (transformed scores); MisFit, popEVE and the conservation and selection scores GERP, phyloP, phastCons and B-statistic (OncoCal lists them as derived without clinical labels); LIST-S2 (conservation-based, with no labelled training described; the preprint says it was assigned to the supervised group "conservatively").
   - `supervised_machine_learning`: the rest, each described as a trained classifier or trained on labelled or proxy-labelled variants (for example CADD and DANN on observed against simulated variants, PrimateAI on primate common variants, AlphaMissense on population-frequency labels; OncoCal classes the last two as not using clinical labels, which is a different axis).
   - `conventional_pipeline` is no longer used in this batch: no tool here is an analysis workflow.
   - 28 configuration and 18 method records changed.
7. **Origin.**
   - Chen et al. 2020: Liang H and Mills GB are authors of CanDrA (reference 7, Mao et al. 2013). The four CanDrA evaluations are now `author_reported`, with a note on each and a limitation on all four Chen judgements. The cell viability labels come from the same group's assays (reference 42 and new data), which the limitations already say.
   - CTAT-cancer and CTAT-population come from Bailey et al. 2018 (reference 12), whose author list is truncated in the reference, so overlap with Chen's authors could not be checked from the pinned sources. They stay `independent_paper`.
   - The other 30 tools were not developed by the authors, and their rationales now say "none except CanDrA" instead of "none".
   - Lee 2026: the sole author declares no competing interests, and no scored tool is theirs. OncoCal, the author's own model, is not among the 49 rows. All 147 evaluations stay `independent_paper`.
8. **Whether a single-author preprint belongs in the store.** Yes, as proxy evidence. It is a primary source, its table is pinned to a commit with the generating code, its preprint status and germline-benign negatives are stated in every Lee judgement and in the summary, and it is the only source that splits predictors by gene mechanism.

## Corrections made in the batch

The batch is not in the store, so fields were edited in place. No ID, link (other than adding one citation, item 9), printed value, numeric value, locator, direction or `printed_source_cell` changed.

1. 500 Chen results: `uncertainty` (`confidence_interval` with lower, upper, `resamples: 100` and a note) removed; `missing_metadata.uncertainty` added (concern 2).
2. 250 Chen OncoKB results: `metric_qualifier` "OncoKB oncogenic versus likely neutral, ..." became "OncoKB benchmark (positive set not stated), ..." (median-score threshold or default categorical calls). The same wording changed in result, evaluation, protocol and judgement names and endpoints, and in both comparison titles, which now read "OncoKB-curated drivers versus likely neutral". The dataset name now lists all three OncoKB classes. Protocol names said "Oncokb"; now "OncoKB".
3. Four `...-eval-chen2020-candra-*` evaluations: `origin` `independent_paper` became `author_reported`, with the reason added to the description.
4. 147 Lee "AUPRC" results: `metric` `auprc` became `average-precision`. The vocabulary defines that as scikit-learn `average_precision_score`, which the generating code calls. `auprc` is the broader concept for "any integration rule unless a narrower concept is used". The locator keeps the printed column name, and endpoints say "average precision (labelled AUPRC)".
5. 294 Lee results: `unit` `fraction` became `unitless`. Every AUROC in the store (756) is `unitless`, and comparisons require the same unit.
6. 147 Lee evaluations: `comparison.metric_implementation` was null ("Repository code not inspected"); it now names the code (concern 5).
7. `...-data-lee2026-cgc-missense`: `population` now says the table counts variant rows, which exceed the protein-level counts.
8. Method types (concern 6).
9. The two default-category protocols now cite `...-source-chen2020-additional-file-1`, which defines the categories they use and which no record cited before.
10. Limitations, kept identical between each protocol and its judgement:
    - The ±2σ sentence now says what the range is.
    - The median sentence explains why the threshold is not an operating point.
    - The OncoKB sampling-overlap and count conflict are added.
    - The cell viability protocols add a sampling conflict: Results give 376 positives in the combined set, yet Methods say 400 positives were drawn per repeat.
    - The CanDrA authorship is added to the Chen protocols.
    - The Lee preprint sentence now gives the version and posting date, and the VARITY sentence the likely explanation. Lee reproducibility is added (concern 5).
    - Each judgement also gains: "No linked comparison reports calibrated probabilities, per-criterion evidence strength or indels; all variants are missense SNVs."
11. Judgement rationales (and descriptions) rewritten for the relevance decisions and the CanDrA finding. The Chen negatives are described as likely neutral somatic mutations, not "somatic or assay-neutral" for OncoKB.
12. Statuses: all records `source_checked`. Every result's `review` records this review; the extractor's note is kept.

`coverage.json` and `research.md` are the collector's record and were not edited; the batch and this review supersede them where they differ.

## Relevance judgements

| Judgement (`use-case-mapping-somatic-oncogenicity-20261009-` prefix) | Relevance | Reasoning | reviewed_evaluations |
| --- | --- | --- | --- |
| `chen2020-oncokb-default` | direct | Somatic mutations curated by OncoKB, likely neutral somatic negatives, each tool's published default call. | 17 |
| `chen2020-viability-default` | direct | Functional assay labels with assay-neutral negatives and published default calls. A growth effect is one line of oncogenicity evidence, which the rationale states. | 17 |
| `chen2020-oncokb-median` | proxy (was direct) | Threshold taken from the test draw (concern 3). | 33 |
| `chen2020-viability-median` | proxy (was direct) | As above. | 33 |
| `lee2026-all`, `-oncogene`, `-tsg` | proxy | Germline-benign negatives, which the use case's third exclusion rejects as automatic somatic controls; single-author preprint. The mechanism split is the reason to include it. | 49 each |

No evaluation is excluded; every evaluation on each protocol applies. Grouping: `chen2020-oncokb` and `chen2020-cell-viability` each hold default calls (order 1) and median threshold (order 2), with headline `accuracy` in fraction. `lee2026-cgc-mechanism` holds all genes, oncogenes and tumour suppressors (orders 1 to 3), with headline `auroc`, now `unitless` throughout. Units are consistent within each group. Each Lee row has its own `n`, so the evaluations differ in `comparison.population`, and automatic comparison is refused; that is accurate, because the tools score different variant subsets.

## Vocabulary

`negative-predictive-value` in `data/vocab/metric.ttl` was replaced with the block from `rewire-benchmark-data-rna-pathogen/data/vocab/metric.ttl` and is byte-identical to it: definition "True negatives divided by all predicted negatives.", `skos:exactMatch` `obo:STATO_0000619`, default direction higher. The collector's version had a different definition and no external match. No other vocabulary change.

## Approved use-case changes

Changes to `use-case-somatic-small-variant-oncogenicity`. No pinned field (name, description, facets, question, decision, inputs, output, exclusions, setting, clinical scope, intended users) changes, so the four OncoVI judgements (`use-case-mapping-20260930-344-401bec55db2f`, `-8840aa223ede`, `-93b84bc9cf35`, `-a19f78d8cc9b`) keep their pins. In the scratch simulation they remain active with the changes applied. The new sources must be in the store as `source_checked` with no `evidence_concerns`, or every positive judgement on the use case is withheld.

`links`: append `{"relation": "assessed_by", "target_id": ...}` for `somatic-oncogenicity-20261009-protocol-chen2020-oncokb-default`, `...-chen2020-oncokb-median`, `...-chen2020-viability-default`, `...-chen2020-viability-median`, `...-lee2026-all`, `...-lee2026-oncogene` and `...-lee2026-tsg` (prefix `somatic-oncogenicity-20261009-protocol-`).

`source_ids`: append `somatic-oncogenicity-20261009-source-chen2020`, `-chen2020-additional-file-1`, `-chen2020-additional-file-9`, `-chen2020-additional-file-10`, `-chen2020-additional-file-21`, `-chen2020-additional-file-22`, `-lee2026` and `-lee2026-oncocal-tool-performance` (prefix `somatic-oncogenicity-20261009-source`). Additional file 1 is added to the collector's list because the default protocols now cite it.

`attributes.citation_locators`: append

- `somatic-oncogenicity-20261009-source-chen2020`: "Results 'Benchmark 2' and 'Benchmark 5'; Methods 'OncoKB annotation benchmark', 'In vitro cell viability assay benchmark' and 'Calculation of five evaluation metrics based on categorical predictions'; reference 7; Competing interests"
- `somatic-oncogenicity-20261009-source-chen2020-additional-file-1`: "Default prediction categories of 17 algorithms"
- `somatic-oncogenicity-20261009-source-chen2020-additional-file-9`: "Benchmark 2, median-score threshold; see data/omics/use-case-coverage-somatic-oncogenicity-20261009/claims.csv"
- `somatic-oncogenicity-20261009-source-chen2020-additional-file-10`: "Benchmark 2, default categories; see data/omics/use-case-coverage-somatic-oncogenicity-20261009/claims.csv"
- `somatic-oncogenicity-20261009-source-chen2020-additional-file-21`: "Benchmark 5, median-score threshold; see data/omics/use-case-coverage-somatic-oncogenicity-20261009/claims.csv"
- `somatic-oncogenicity-20261009-source-chen2020-additional-file-22`: "Benchmark 5, default categories; see data/omics/use-case-coverage-somatic-oncogenicity-20261009/claims.csv"
- `somatic-oncogenicity-20261009-source-lee2026`: "Methods 'Labels' and 'Features'; Results first section; Competing interests"
- `somatic-oncogenicity-20261009-source-lee2026-oncocal-tool-performance`: "tables/tool_performance.tsv at commit 40b7770f2a768ba800c4f4c6b48e2bfe967ed14a; see data/omics/use-case-coverage-somatic-oncogenicity-20261009/claims.csv"

`attributes.evidence_gaps`: keep the four existing entries and append

1. No linked independent comparison includes CHASMplus, BoostDM or AlphaMissense on somatic driver labels with somatic or functional negatives; the 2026 preprint that includes AlphaMissense uses germline-benign negatives.
2. No linked comparison reports calibration of predictor scores to oncogenicity probability or to ClinGen/CGC/VICC SOP evidence strength.
3. All linked predictor comparisons score missense SNVs; none covers small indels.
4. Per-gene results (for example TP53 transactivation in Chen et al. 2020 benchmark 3) are not transcribed in this intake.
5. Binary metrics in Chen et al. 2020 use each tool's median benchmark score as the threshold, which is not available when classifying a new variant.

Item 3 is new; the others are the collector's text unchanged. The `setting` field says "SNVs and small indels"; the new evidence is missense only. Changing it would withhold the OncoVI judgements for no gain, so gap 3 records the difference instead.

## Evidence summary

Final text for `use-case-summary-somatic-small-variant-oncogenicity` (`field` `summary`). Its `source_ids`: `somatic-oncogenicity-20261009-source-chen2020`, `-chen2020-additional-file-9`, `-chen2020-additional-file-10`, `-chen2020-additional-file-21`, `-chen2020-additional-file-22`, `-lee2026`, `-lee2026-oncocal-tool-performance` (prefix `somatic-oncogenicity-20261009-source`). It is descriptive and recommends nothing.

> Two predictor comparisons join the existing OncoVI evidence; their values cannot be pooled. In Chen et al. 2020 (peer reviewed), 33 predictors scored somatic missense mutations labelled by OncoKB curation or by the authors' own cell viability assays, with likely neutral or assay-neutral somatic negatives. The authors co-developed one scored tool, CanDrA, and developed none of the others. With each tool's own default calls, the highest accuracy was 0.70 on OncoKB labels (DEOGEN2, sensitivity 0.87, specificity 0.51), and several tools called most neutral mutations damaging, for example M-CAP with sensitivity 0.97 and specificity 0.11, and CanDrA with specificity 0.17 and the lowest accuracy, 0.49. On the assay labels the highest default accuracy was 0.65 (PrimateAI). When each tool's median score on the test draw was used as the threshold, which ranks tools but is not an operating point a reviewer could apply, the highest accuracy was 0.69 on OncoKB labels (PROVEAN and VEST4) and 0.70 on assay labels (CTAT-cancer and PrimateAI), and FATHMM-disease scored 0.50 on OncoKB labels. Chen et al. print each value as a mean with a range of two standard deviations over 100 draws, not a confidence interval, and do not say which OncoKB positive set fed these tables. In a single-author bioRxiv preprint that is not peer reviewed (Lee 2026), 49 scores were compared on Cancer Gene Census missense variants whose negatives are germline-benign labels (ClinVar benign or likely benign, and gnomAD common variants), which this use case does not accept as somatic controls. In that table 42 of the 49 scores had a lower AUROC on oncogene variants than on tumour-suppressor variants, for example AlphaMissense 0.885 against 0.900 and CADD 0.821 against 0.894, while popEVE went the other way (0.900 against 0.842). The highest all-gene AUROC was 0.876 (MutScore); these AUROC values are rounded here to three decimals from the table's full precision. None of these comparisons covers small indels, calibrated probabilities, criterion-level evidence strength, drug response or reviewer agreement.

Traceability (all `source_checked`; prefix `somatic-oncogenicity-20261009-result-`):

| Statement | Record | Printed |
| --- | --- | --- |
| DEOGEN2 default OncoKB accuracy, sensitivity, specificity (highest default accuracy of 17) | `chen2020-deogen2-oncokb-default-accuracy`, `-recall`, `-specificity` | 0.70, 0.87, 0.51 |
| M-CAP default OncoKB sensitivity, specificity | `chen2020-m-cap-oncokb-default-recall`, `-specificity` | 0.97, 0.11 |
| CanDrA default OncoKB specificity, accuracy (lowest of 17) | `chen2020-candra-oncokb-default-specificity`, `-accuracy` | 0.17, 0.49 |
| PrimateAI default viability accuracy (highest of 17) | `chen2020-primateai-viability-default-accuracy` | 0.65 |
| PROVEAN, VEST4 median OncoKB accuracy (highest of 33) | `chen2020-provean-oncokb-median-accuracy`, `chen2020-vest4-oncokb-median-accuracy` | 0.69, 0.69 |
| CTAT-cancer, PrimateAI median viability accuracy (highest of 33) | `chen2020-ctat-cancer-viability-median-accuracy`, `chen2020-primateai-viability-median-accuracy` | 0.70, 0.70 |
| FATHMM-disease median OncoKB accuracy | `chen2020-fathmm-disease-oncokb-median-accuracy` | 0.50 |
| 42 of 49 lower on oncogenes | all 98 `lee2026-*-oncogene-auroc` and `-tsg-auroc` results | (count) |
| AlphaMissense oncogene, TSG | `lee2026-alphamissense-oncogene-auroc`, `-tsg-auroc` | 0.884840558849365, 0.8997205148312148 |
| CADD oncogene, TSG | `lee2026-cadd-raw-oncogene-auroc`, `-tsg-auroc` | 0.8209680782909458, 0.8936755950451863 |
| popEVE oncogene, TSG | `lee2026-popeve-oncogene-auroc`, `-tsg-auroc` | 0.9003207957941839, 0.8419454614126403 |
| MutScore all genes (highest of 49) | `lee2026-mutscore-all-auroc` | 0.8760066144430202 |

Every record ID above was confirmed in the reviewed batch. Non-numeric statements trace to Chen reference 7 and Methods (CanDrA authorship, ±2σ, OncoKB sets) and to the Lee preprint (single author, posting date, labels).

## Duplicate records on main (follow-up, 2026-10-09)

The lead found that the batch created `somatic-oncogenicity-20261009-method-bayesdel` although main already has `uc-clinical-20260930-method-bayesdel`. I compared the names and reported names of all 45 batch method records with every method, model, service and pipeline record in `data/entities/` (exact match after removing case and punctuation, then a looser substring search for 28 common predictor names). Three main records share a name:

| Batch record | Main record | Same tool? | Action |
| --- | --- | --- | --- |
| `somatic-oncogenicity-20261009-method-bayesdel` | `uc-clinical-20260930-method-bayesdel` (method, "Computational variant-effect scoring method", ENIGMA source) | Yes: the same BayesDel variant deleteriousness score | Batch record removed; `config-lee2026-bayesdel-addaf` and `config-lee2026-bayesdel-noaf` now link `configuration_of` to the main record |
| `somatic-oncogenicity-20261009-method-esm1b` | `uc20260930-model-esm-1b` (model, entity level family, from the ProteinGym Spearman table) | Yes: the ESM-1b protein language model; dbNSFP's ESM1b score and ProteinGym's ESM-1b score both come from it, and the main record is family-level with no checkpoint claim | Batch record removed; `config-lee2026-esm1b` now links `configuration_of` to the main model. The configuration keeps `method_types: foundation_model` |
| `somatic-oncogenicity-20261009-method-mvp` | `uc20260930-model-mvp` (model, metabolomics, from MSAlign v2 Table 3) | No: the main record is a mass-spectrometry baseline that shares the name; the batch's MVP is the missense variant pathogenicity predictor | Not relinked |

`configuration_of` may target a model or a method (`shared/omics/relations.ts`). No other batch record, `claims.csv` row or note referred to the two removed records. The method named VEST4 (`somatic-oncogenicity-20261009-method-vest4`) is left unchanged, as the lead asked; main has no VEST record. No method name on main matches AlphaMissense, REVEL, CADD, SIFT, PolyPhen-2, PrimateAI, MetaRNN, ClinPred, popEVE, CHASM, CanDrA, DEOGEN2 or VARITY.

After the change the batch has 1,191 records (43 methods). The cell check still matches 794 of 794. A fresh dry-run `addBatch` against a scratch copy of the store accepts all 1,191. The use-case derivation with the approved changes still gives 11 active judgements and a published summary. `npm test` (499 of 499) and `npm run typecheck` pass.

## Remaining gaps

- Chen figures, benchmarks 1, 3 and 4, and the AUC values (printed only in PDF figures) were not checked.
- CTAT authorship overlap with Chen's authors could not be checked from the pinned sources.
- The OncoCal table was not regenerated (licensed inputs); the generating code was read, not run.
- The bioRxiv PDF was not retrieved (the collector's request returned HTTP 429); S1 to S8 Tables were not checked.
- No source here gives indels, calibration or per-criterion evidence strength.
