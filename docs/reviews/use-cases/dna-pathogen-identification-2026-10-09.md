# DNA pathogen identification: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-dna-pathogen-20261009/` (926 records). Use case: `use-case-diagnostic-dna-pathogen-identification`.

Reviewer: a separate Claude review agent that did not extract the batch. No human review is claimed. Nothing was executed or reproduced. This is a check of transcription and judgement against the pinned sources.

## Verdict

- The three article XMLs re-download to their pinned SHA-256, and the archived copies decompress to the same bytes.
- All 744 results match their table cells. No value, printed form, locator, metric, qualifier, unit, direction, interval or configuration, protocol and dataset link was wrong.
- Six fields were corrected and one vocabulary definition was fixed. None changes a number.
- One evidence concern was added, on Song et al. 2025 (Table 1 Kraken column). Under the current gates it withholds both Song judgements.
- All 12 relevance judgements hold as `proxy`. Their limitations were missing several source caveats, which I added. Each now lists its checked evaluations in `reviewed_evaluations` and is `source_checked`. Pins are left for the integrator.
- Every record in the batch is now `source_checked`.
- The summary proposal in `coverage.json` needs changes before it is used. My corrected text is at the end.

Do not rerun `extract/extract_pathogen.py` on this folder: it would overwrite the corrections.

## How the check was done

1. Downloaded each `artifact_url` into an empty directory and hashed it.
2. Read the tables with a stdlib JATS reader written for this review, with `rowspan` and `colspan` expanded. The extractor's script was not imported or run.
3. Built the expected identity of every cell from the headers and row labels: tool and database, dataset block, metric column. Matched every result to its cell through `source_locator`. Compared `printed_value` (exact string), `numeric_value` (as a decimal, reading U+2010 E notation and thousands separators), metric, qualifier, unit and direction, and the evaluation's `system`, `assessment` and `data` links. For Hall, I also compared the interval bounds, level and Wilson method with the cell and the footnote. For Song, I compared `reported_p_value` with the p-value row.
4. 744 expected cells, 744 matched, none missing and none duplicated.
5. Recomputed Portik's precision, recall, F1 and F0.5 from the printed TP, FP and FN for all 70 rows.
6. Read Methods, Results, Discussion and declarations of all three articles for versions, datasets, protocols, `missing_metadata` reasons, the four descriptive claims and the six collector concerns.
7. Dry run: `addBatch` into a scratch copy of the store, then `deriveUseCaseInputs` with the 12 proposed `assessed_by` links added in memory.

## Sources and hashes

| Source ID | Artifact | SHA-256 (re-downloaded 2026-10-09T20:06Z) | Matches |
| --- | --- | --- | --- |
| `dna-pathogen-20261009-source-portik2022` | PMC9749362 full-text XML | `42cf6834ec87e149752176a65247f3aab9873f7b215037a195175a8a3113c1fe` | Yes |
| `dna-pathogen-20261009-source-song2025` | PMC12705909 full-text XML | `7b122b551b2155b43c26f5a15e7382a0662d859520d2939dc91e04d88e5656ef` | Yes |
| `dna-pathogen-20261009-source-hall2024` | PMC10993716 full-text XML | `ea3c34a01222d5c5203c52a85a700b7dae5cccd6f48e6d50808d5abbd6385554` | Yes |

The three `artifacts/*.gz` files decompress to these hashes, and their gzip hashes equal those in `sources.md`.

## Values checked

| Source table | Results | Metrics | Mismatches |
| --- | --- | --- | --- |
| Portik Table 4 (70 rows, 6 dataset blocks) | 560 | TP, FP, FN counts; precision; recall; F1; F0.5; L1 | 0 |
| Song Table 1 | 36 | 32 relative abundances; 4 eta squared with p-values | 0 |
| Song Table 2 | 28 | relative abundance | 0 |
| Hall Tables 5 to 8 | 120 | throughput, peak memory, specificity and sensitivity (with 95% Wilson intervals), Youden's index (with intervals) | 0 |
| Total | 744 | | 0 |

Portik recomputation: 270 of 280 printed values equal the exact value rounded to two decimals. The other 10 differ from exact rounding by 0.005 to 0.009. For example, Kraken2 F1 on HiFi Zymo D6331 is printed 0.13, but TP 14, FP 196 and FN 1 give 0.124. The printed 0.13 is what F1 gives from the rounded precision 0.07 and recall 0.93. Sourmash-k51 precision on ONT R10 is printed 0.76, while 10/13 = 0.769. These are source rounding quirks, not transcription errors. The values are kept as printed.

In the last block of Portik Table 4 (Illumina Zymo D6300), the XML gives the "Short read" method-type cell `rowspan=7`, so it covers the two Sourmash rows, which the other blocks label "General". This affects only that label, not any value.

## Corrections made in the batch

None of these changes a number.

1. The three Hall minimap2 configurations recorded `version` "2.26". The article states v2.26 only for the human read removal configuration; the classification section does not restate it. The kraken configurations had been left unreported for the same reason (v2.1.2 is stated only for the library download). For consistency and the no-guessing rule, `version` is now unset with a `missing_metadata.version` note that keeps the v2.26 statement.
2. `dna-pathogen-20261009-config-song2025-metaphlan-native-db-galaxy`: `parameters` said "default settings". Methods 'Data Analysis' sets a 90% minimum sequence similarity "for all software where it was not the default value". The parameters now say so, as for BLAST, Kraken and RTG Core.
3. The 12 judgements: source caveats were added to `limitations` (listed under Judgements), and `reason` now cites this review.
4. `data/vocab/metric.ttl`, `youden-index`: the definition said "from 0 to 1". Youden's index is sensitivity plus specificity minus 1 and ranges from -1 to 1. Hall states 0 to 1, which holds only for tests no worse than chance. The definition now gives the full range and notes the narrower convention.

## Evidence concern added

On `dna-pathogen-20261009-source-song2025`: Table 1 prints Kraken relative abundances of 5.17E‐10 (Salmonella enterica, Escherichia coli), 5.17E‐11 (Lactobacillus fermentum) and 5.17E‐12 (Enterococcus faecalis). That is one mantissa across three orders of magnitude. As read fractions these would need at least about 2 billion to 190 billion reads for each assigned read. The study's patient libraries average 33.5 M reads after QC, and the control library size is not given. The values are probably a computation or formatting artefact. The Kraken column of Table 1 and its eta squared (3.20E‐2) should not be compared. The values are kept as printed.

Effect: `cleanSource` treats any concern on a source as blocking. Both Song judgements are therefore withheld, and no Song evaluation is eligible, even though Table 2 is not affected. If that is too broad, the alternative is a result-level dispute on the five Kraken Table 1 results instead of a source concern. That is a store-policy choice for the integrator, so I did not make it.

## The collector's concerns

| Concern | Finding |
| --- | --- |
| Song Kraken 5.17E-10, E-11, E-12 | Confirmed as printed. Raised as an evidence concern (above). |
| BLAST false positives, prose versus Table 2 | Table 2 shows BLAST at 1.03E‐1 in negative blood and 2.59E‐1 in the no-template control. The control values are above four (no-template control) and three (negative blood) of the five patient samples. Methods says a detection is valid only if absent from both controls, so none of BLAST's Table 2 assignments meets the study's own rule. Results paragraph 2 says this. The Abstract, Discussion paragraph 3 and Conclusion claim of complete concordance without false positives refers to the later e-value run in Figure 1, which is not in any table. Recorded in the judgement limitations. No separate concern, because the table and Results agree. Separately, Discussion paragraph 4 gives a Wilson 95% interval of 0.61 to 1 for BLAST; that lower bound corresponds to 6 of 6, while the text describes five samples plus positive and negative controls. Not recorded as a concern. |
| Kraken 1 or 2 in Song | Not determinable. The references are Wood and Salzberg 2014 (Kraken 1) and Salzberg and Wood 2021 ("Releasing the Kraken", a review of the family), and the tool ran on Galaxy, which hosts both. Linking to a generic Kraken method with the major version unreported is right. |
| Portik prose "40-300" false positives | Results says "most short-read methods" detected 40 to 300 false positives. Short-read rows in Table 4 range from 0 to 307. Kraken2, Bracken and Centrifuge-h22 are 16 to 307, and Centrifuge-h22 on HiFi Zymo D6331 (307) is just above 300. A loose summary, not a conflict. Also, Discussion says sourmash had "only 2-3 false positives" on the HiFi datasets; Table 4 prints 1 to 5 (k31 HiFi ATCC 5). Same judgement. Table values recorded; no concern. |
| Kraken versions in Hall | Hall cites Kraken 2 (Wood, Lu and Langmead 2019) and uses the Kraken 2 standard indexes of 2023-06-05, so linking to `catalog-model-kraken2` is supported. The minor version is stated only for the library download, so `version` is rightly unreported. I applied the same rule to minimap2 (correction 1). |
| Sourmash rows `author_reported` | Agree. C. T. Brown and N. T. Pierce-Ward are authors of all three cited sourmash papers (references 33 to 35), and Pierce-Ward performed the data analysis (Author contributions). The competing-interests statement declares no interests for them. The first author is a PacBio employee and shareholder, and the MEGAN-LR rows ran through PacBio's pb-metagenomics-tools; those rows are `independent_paper` with the affiliation noted on the evaluations and judgements. I agree with that split: PacBio does not develop MEGAN-LR. |

Further caveats found in the sources:
- Song's theoretical column lists eight bacteria summing to 0.990. Results paragraph 1 mentions yeasts, which the table omits.
- Hall states that the genomes used to simulate reads were excluded only from the kraken Myco database. For the minimap2 databases, which include 17 M. tuberculosis references, overlap with the simulated or real M. tuberculosis genomes is not stated.

## Descriptive claims

| Claim | Check | Outcome |
| --- | --- | --- |
| `...claim-hall2024-kraken-fn-genus` | Results 'Real Illumina' paragraph 3 | Correct |
| `...claim-portik2022-missing-reference-species` | Methods 'Detection metrics' paragraph 4 and Table 4 footnote. TP+FN is 15 for every method in that block, so the exclusion applied to all methods | Correct |
| `...claim-song2025-blast-controls` | Results paragraph 2 and 'Reduction of False-Positive Signals' paragraphs 1 and 2 | Correct |
| `...claim-song2025-zymo-theoretical-composition` | Table 1 'Theoretical' column | Correct |

## Judgements

All 12 pass as `proxy`. `reviewed_evaluations` lists every evaluation on each protocol (14, 7 or 6 per Portik block; 6 per Hall table; 4 per Song table). None is excluded.

**Fit to the use case.** The use case's question is broad: which DNA classification workflow detects pathogens and handles contamination and organisms absent from the reference. Its `decision`, `inputs` and `output` are still written for the Karius assay: plasma cell-free DNA reads, and positive percent agreement against one reference standard. None of the new endpoints produces that output. Under the relevance definitions this is what `proxy` means ("a related endpoint, input or setting that informs the use case"), so the judgements hold. The page will read oddly while the decision text names only Karius. I recommend widening `decision`, `inputs` and `output` in a reviewed change and re-pinning the Karius judgement in the same change, as `coverage.json` already notes.

**song2025-bsi-blood: proxy, not direct.** `direct` requires the use case's endpoint on inputs of the kind it describes. Song's specimen is DNA from 200 µL of whole blood after host-DNA depletion and whole-genome amplification, not plasma cell-free DNA. Its Table 2 prints relative abundances, not detection calls or agreement. It has five culture-positive samples of one organism group and no culture-negative patients. Even with the use case widened, the endpoint is not a detection or agreement measure. Proxy is right.

**Limitations added.**
- Portik (all six): the 0.001% of total reads detection threshold. The authors note it penalises methods that assign fewer reads, and that 0.1% cut short-read false positives from several hundred to about 10 or fewer. Also the precise sourmash authorship statement.
- Portik ONT R10 and Q20: the exclusion of reads under 2 kb and the authors' finding that shorter reads lower precision and F-scores for every method.
- Hall (all four): possible overlap between the minimap2 databases' M. tuberculosis references and the truth genomes, which is stated as excluded only for kraken Myco. Also that kraken's species-level misses are at least 90% correct at genus level.
- Song Table 1: the Kraken concern and the omitted yeasts.
- Song Table 2: the study's control rule applied to BLAST's control values, where the "complete concordance" claim comes from, whole blood rather than plasma cfDNA, and the source concern.

**Page grouping.**
- Portik: one group, strata in Table 4 block order (HiFi ATCC, Illumina ATCC, HiFi Zymo, ONT R10, ONT Q20, Illumina Zymo), headline F1. F1 is the authors' own summary measure. It is right.
- Hall: one group, strata in table order (Tables 5 to 8), headline Youden's index, the authors' combined accuracy measure. It is right.
- Song: two single-protocol groups with headline `proportion`, direction unknown. Acceptable, since the tables print abundances only.

**Dry run.** With these edits and the 12 links added, `deriveUseCaseInputs` withholds the 10 Portik and Hall judgements only because pins are not yet recorded. The two Song judgements are also withheld by the source concern. The Karius judgement stays active.

## Vocabulary

| Concept | Check | Outcome |
| --- | --- | --- |
| `eta-squared` | Definition (between-group over total sum of squares, 0 to 1) matches Song Methods 'Data Analysis' paragraph 2 and Cohen 1988. Direction unknown per result is right | Accepted. No external mapping was checked, so none is added |
| `f-beta-score` | Formula (1 + beta^2) PR / (beta^2 P + R) matches Portik's F0.5 description | Accepted, unmapped |
| `peak-memory` | Matches Hall ("maximum from 10 executions") | Accepted, unmapped |
| `youden-index` | Range wrong | Corrected (correction 4) |
| `gigabyte` | `skos:exactMatch` QUDT `unit:GigaBYTE`. Fetched the QUDT term on 2026-10-09: "1 gigabyte is 1,000,000,000 bytes", conversionMultiplier 8.0E9 (bits) | Accepted. The match holds. Hall does not say whether GB means 10^9 or 2^30 bytes, which `unit_detail` keeps |

Hall's throughput uses the existing `inference-throughput` and `sample-per-second`, with `unit_detail` "reads per second". This is acceptable, but a read-rate unit would be more exact. That is not part of this batch.

## coverage.json

**`add_links`:** the 12 `assessed_by` targets equal the 12 judgement protocols. Correct.

**`setting_proposal`:** the numbers are correct (14 configurations, six datasets, four pipelines, five patients). Its last sentence makes an absence claim. It should read: "None of the sources found in this bounded search compares workflows on a large clinical cohort with a composite reference standard."

**`evidence_gaps_add` (6):** gaps 1, 2, 3, 5 and 6 are accurate. Gap 4 (Lao et al. 2024) rests on the collector's screening, which I did not repeat. I suggest one further gap: "Song et al. 2025 Table 1 Kraken values are under an evidence concern, so the only patient-sample comparison is withheld."

**`summary_proposal`:** every number traces to a result. Checked values:
- Kraken2 and Bracken FP 44 to 204, precision 0.05 to 0.21, FN 0 except 1 on HiFi Zymo.
- MEGAN-LR and BugSeq-V2 FP 0 to 2, recall 0.70 to 1.00.
- Song 1.03E‐1 and 2.59E‐1; Kraken non-zero in samples 1, 3 and 4; RTG Core and MetaPhlAn in sample 3.
- Hall kraken standard 0.0731 to 0.7408, Myco 0.9715 to 0.9953, specificity 1.0.

It needs four changes:
1. It does not name the threshold dependence of the false-positive counts.
2. It does not name the PacBio affiliation behind the long-read rows.
3. It does not say that BLAST's control values fail the study's own validity rule.
4. It cites Song, whose judgements are now withheld, so the summary would describe evidence the page does not show. It should also mention the Karius result, which is the one active judgement on a clinical cohort.

## Corrected summary text

For use while the Song concern stands:

> Among the reviewed comparisons, workflows are compared only on mock communities or constructed metagenomes. The one clinical-cohort result is a single assay: Karius plasma cell-free DNA sequencing agreed with initial blood culture in 93.7% (59 of 63) of culture-positive patients in a sepsis-alert cohort, as reported by the assay's developers, and blood culture does not detect every infection. In six mock-community datasets (Portik et al. 2022), Kraken2 and Bracken detected all or all but one of the scored species but also called 44 to 204 species that were not in the community at the authors' threshold of 0.001% of reads, so their precision was 0.05 to 0.21; the authors report far fewer false positives at a 0.1% threshold. On the four long-read datasets, MEGAN-LR (three variants) and BugSeq-V2 called 0 to 2 absent species, with recall 0.70 to 1.00; the study's first author is a PacBio employee and the MEGAN-LR runs used PacBio's workflows, and two species missing from several reference databases were removed from scoring on one dataset. For M. tuberculosis reads in constructed sputum-like metagenomes (Hall and Coin 2024), kraken with its standard database classified 0.07 to 0.74 of the M. tuberculosis reads as M. tuberculosis, against 0.97 to 0.995 with a Mycobacterium database built by the same authors; specificity was 1.0 for every kraken database. Each configuration used its own reference database, so method and database effects are not separated, and none of these results is clinical validation.

If the Song concern is resolved and its Table 2 judgement becomes active, add after the Karius sentence:

> In shotgun reads from five blood-culture-positive patients, all with viridans group streptococci (Song et al. 2025), BLAST assigned viridans group streptococci in all five samples but also in the negative blood control (1.03E-1) and the no-template control (2.59E-1), so none of its assignments met the study's rule that a detection counts only if it is absent from both controls; Kraken assigned them in three samples, and RTG Core and MetaPhlAn in one, with none in the controls.

Number trace for the additions:
- 93.7% and 59 of 63 come from `amp-20261007-dna-pathogens-result` (printed 93.7, locator "NGS positive 59, NGS negative 4"), origin `author_reported`.
- "Far fewer false positives at 0.1%" is the authors' prose (Results 'Detection metrics' paragraph 5: "from several hundred to ~ 10 or fewer"), not a stored result, so no number is given.

## Remaining gaps

- Figures not checked, including Song Figure 1.
- Portik Additional file 1 and Hall Supplementary Tables S1 to S12 not opened.
- Screened sources in `research.md` not re-read.
- Pins not recorded; the integrator pins with this review.
- The use case's decision, inputs and output still describe only the Karius assay (see Judgements).
