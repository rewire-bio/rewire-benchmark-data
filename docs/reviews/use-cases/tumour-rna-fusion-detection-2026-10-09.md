# Tumour RNA fusion detection: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-rna-fusion-20261009/` (424 records from the collector, 425 after review). Use case: `use-case-tumour-rna-fusion-detection`.

Reviewer: a separate Claude review agent that did not extract the batch. No human review is claimed. Nothing was executed or reproduced; this is a check of transcription against the pinned sources and of the relevance judgements.

## Outcome

- All three pinned artifacts re-download to their recorded SHA-256. There are no archived copies (both licences are non-commercial), so the re-download is the only byte check.
- All 320 results match their source cells: printed value, numeric value, locator, metric, qualifier, unit, direction, configuration and protocol. No number was wrong.
- In Tamura et al. Supplementary Tables 3 and 5, TPR, PPV and F1 recompute from TP, FP and FN within rounding on all 48 rows, and TP plus FN equals the printed truth-set size (Table 3) or the driver truth count, 61 or 24 (Table 5). In Lin et al. Tables 3 and 6, F1 recomputes from the printed sensitivity and precision within rounding.
- One origin was wrong: Genomon, which a Tamura co-author developed, was recorded as `independent_paper`. The four Genomon evaluations are now `author_reported`, and a claim records why.
- No source `evidence_concerns` were raised and no evaluation is excluded. Every problem found is limited to specific rows or is a property of the benchmark design, and is recorded in limitations.
- All six judgements hold after correction. Each is `source_checked` with all of its evaluations in `reviewed_evaluations`. Pins are left for the integrator.
- Every record is now `source_checked`. Results and descriptive claims carry a `review` block.

## How the check was done

1. Downloaded each `artifact_url` into an empty directory (two Europe PMC XMLs and the publisher's supplementary PDF) and hashed them.
2. Read the PDF text layer with `pdftotext -layout` and a row parser written for this review, and the Lin tables from the article XML with my own `table-wrap` reader. The extractor's `extract/extract_rna_fusion.py` was not imported or run. The PDF text layer is the same tool output the extractor used, so the two reads are not independent at the text-extraction step; every row was also checked arithmetically (above), which would expose a misread column.
3. Matched every result to its cell by protocol, configuration `reported_name` and metric, and compared `printed_value`, `numeric_value` (thousands separators removed), `metric_qualifier`, unit, direction and `source_locator`. 288 Tamura cells and 32 Lin cells expected; all matched once, none missing or duplicated. The per-algorithm truth-set sizes in Table 3 equal each all-fusion evaluation's `denominator`.
4. Read both articles in full (Methods, Results, Discussion, author lists, contributions and disclosures) and Tamura Supplementary Table 1, to check versions, datasets, protocols, origins, the runtime claim and the collector's concerns.
5. Integration dry run: `addBatch` against a scratch copy of the store passes (vocabularies, declared attributes, record validation; SHACL not run). With the six proposed `assessed_by` links added and the judgements pinned in memory with `claimPins`, `deriveUseCaseInputs` gives all six new judgements and both existing judgements as `active`. Nothing was written to the store.

## Sources and hashes

| Source ID | Artifact checked | SHA-256 (re-downloaded 2026-10-09) | Matches record |
| --- | --- | --- | --- |
| `rna-fusion-20261009-source-tamura2026` | PMC13230599 full-text XML | `540cf971970ad98557f3d4511f09c3f06a1b4359fe9276a25e29e731e36c0fc1` | Yes |
| `rna-fusion-20261009-source-tamura2026-supplementary` | `41698_2026_1397_MOESM1_ESM.pdf` from static-content.springer.com | `f18ada098fd03b0842c63a8ab9d13002e1876b006243e42c640a118ea3ab3275` | Yes |
| `rna-fusion-20261009-source-lin2026` | PMC13197905 full-text XML | `8cc3b4bca5e2fe9b068a1e891366854d974f3df3102425959e600b9ea19f87b6` | Yes |

Licences in the XML: CC BY-NC-ND 4.0 (Tamura), CC BY-NC 4.0 (Lin), as recorded.

## Values checked

| Source table | Results | Metrics | Mismatches |
| --- | --- | --- | --- |
| Tamura Supplementary Table 3, conventional and targeted, 12 algorithms each | 144 | TP, FP, FN, TPR, PPV, F1 | 0 |
| Tamura Supplementary Table 5, conventional and targeted, 12 algorithms each | 144 | TP, FP, FN, TPR, PPV, F1 | 0 |
| Lin Table 3 (high depth) and Table 6 (low depth), 4 algorithms each | 32 | sensitivity, specificity, precision, F1 | 0 |
| Total | 320 | | 0 |

Configuration versions and aligners match Tamura Supplementary Table 1 on all 12 rows (Pizzly is printed as v0.73.3 and recorded as printed). Lin prints no caller versions; the `unreported` reasons are correct. The runtime claim matches Lin Table 5 and its footnote.

## Corrections made in the batch

None changes a number, ID, link or comparison field. The batch is not in the store, so fields were edited in place. The collector's copy has SHA-256 `d4f8b042cc144a96b2eb349da157cb171571a00892ee7059a6e14221fd879fa6`. The reviewed `batch.jsonl` has SHA-256 `1c611c3be1b1a093eab8c74ea4fdc2642f2ad633c924ee0b9ec55f9156efc843`; `review.json` binds it and every other file in the folder.

1. Status: every record set to `source_checked`; results and claims got a `review` block naming this reviewer and method, with the collector's note kept.
2. Origin: the four `rna-fusion-20261009-eval-tamura2026-genomon-*` evaluations changed from `independent_paper` to `author_reported`. Co-author Yuichi Shiraishi is first author of the cited Genomon fusion paper (reference 25) and is credited with Software (Author contributions). Added claim `rna-fusion-20261009-claim-tamura2026-genomon-developer` with the evidence, and a matching `claims.csv` row. The judgement rationales no longer say the group "developed none of the 12 algorithms".
3. 13 method `description` fields stated facts not in either source (for example "with artefact filters", "Trinity CTAT", "circular RNA detection"). They now use the alignment method in Tamura Supplementary Table 1 or the descriptions in Lin Methods.
4. The four STARChip `na` results: `undefined_reason` reworded. The footnote defines `na` for PPV only; F1 is undefined because Methods define it as the harmonic mean of TPR and PPV.
5. `rna-fusion-20261009-data-lin2026-ball-nanopore`: `population` now records the count conflict (79 runs with a known fusion in Methods, 81 samples with known genomic subtypes in Results).
6. All six protocol and judgement `limitations` rewritten (below), and the Tamura and Lin citation locators made specific (the old "Results paragraph 4" did not say which section).

## Collector concerns: decisions

1. **Tamura driver truth and circularity.** Confirmed. For the driver analysis, a pair entered the truth set only if four or more of the 12 algorithms detected it, with no exclusion of the algorithm being scored, plus a literature report or RT-PCR and Sanger confirmation. Two pairs per assay were added outside that rule. For the all-fusion analysis, by contrast, the scored algorithm is excluded from its own truth. **Decision: keep the driver judgements `direct`.** The endpoint (sensitivity for clinically relevant driver fusions from tumour RNA-seq) is the use case's endpoint, and every truth pair has orthogonal support ("all of which were orthogonally validated", Methods). The selection step biases which fusions are in the truth set, not whether they are real, so it belongs in limitations. Recorded on both driver judgements: driver fusions most callers miss are under-represented, so TPR may overstate sensitivity, most for callers that agree with the majority. A second limitation records that listed driver calls by two or three algorithms that are not in the truth set count as neither TP nor FP.
2. **All-fusion consensus protocols: `proxy` or `outside_scope`.** Keep `proxy`. They are the only linked measure of each caller's unvalidated call volume, which is the review-burden part of the question. PPV here is not precision against a validated truth: false positives are single-caller calls only, and calls by two or three algorithms count as neither. Recorded in limitations.
3. **STARChip `na` cells.** Keep as printed with `numeric_value` null. On targeted RNA-seq STARChip made no calls at all (TP 0, FP 0), so PPV is undefined, and F1, defined in Methods from TPR and PPV, is undefined too. Recording F1 as 0 would be a value the source does not print. The authors also say STARChip "did not detect any driver gene fusions in the default parameter setting".
4. **FUSILLI.** Keep it in the comparison, with limitations. It is the authors' tool and is correctly `author_reported`. The collector's concern that it "is scored on its own gene list" is only partly right: every caller is scored on the dominant fusion among detected B-ALL list fusions (Methods 'Fusion Performance Evaluations'), so the comparators are scored on the same list. The stronger issue is that FUSILLI's filters (two supporting reads, gene distance and overlap) were set from "analyses of candidate fusion-supporting reads" (Methods 'FUSILLI'; Supplemental Figure S1), and the source does not say that data was held out from the evaluated cohorts. That is a plausible but unconfirmed tuning advantage, not demonstrated training on test labels, so I did not exclude it. The page will show `author_reported` on its rows.
5. **Lin as a developer paper: origin on each row.** FUSILLI is `author_reported` on both protocols. FusionSeeker, JAFFAL and LongGF are `independent_paper`, which matches the vocabulary definition ("authors independent of the evaluated method"): no Lin author is an author of the JAFFA, LongGF or FusionSeeker papers. Mullighan and Roberts co-authored the CICERO work used in the truth set, but CICERO is not an evaluated caller.

## Conflicts found

- **Genomon origin** (correction 2).
- **Lin low-depth counts.** Methods give 79 of 119 runs with known B-ALL fusions; Results say FUSILLI "correctly detected 22 B-ALL fusion subtypes (of 81 samples with known genomic subtypes)". Recall is not TP over the known-positive count here (a known-fusion sample with a wrong dominant call is a false positive, not a false negative), so the tables cannot settle which count applies. Recorded on the dataset and in the low-depth limitations. No value depends on it.
- **Lin abstract versus Table 6.** The abstract says FUSILLI outperformed the other callers with "sensitivities ranging from 0.09 to 0.16"; Table 6 prints JAFFAL 0.23. Table values are recorded; noted in the low-depth limitations.

## Judgements

The question is "Which RNA-sequencing workflow detects and prioritises tumour gene fusions with useful sensitivity and a manageable false-positive review burden?"

| Judgement (`use-case-mapping-rna-fusion-20261009-`) | Relevance | Evaluations reviewed | Decision |
| --- | --- | --- | --- |
| `tamura2026-driver-conventional` | direct | 12 of 12 | Holds; circularity, Genomon and parameter limitations added |
| `tamura2026-driver-targeted` | direct | 12 of 12 | Holds; as above, plus small truth set and the authors' own capture panel |
| `tamura2026-all-conventional` | proxy | 12 of 12 | Holds; consensus truth and FP definition limitations |
| `tamura2026-all-targeted` | proxy | 12 of 12 | Holds; as above |
| `lin2026-high-depth` | direct | 4 of 4 | Holds, provided the use-case `inputs` change below is applied; FUSILLI tuning and scoring limitations |
| `lin2026-low-depth` | direct | 4 of 4 | Holds, as above; per-run scoring, count conflict, abstract conflict |

Lin's input is nanopore long reads, while the use case's `inputs` say "Paired-end tumour RNA-seq reads". `direct` requires inputs of the kind the use case describes, so the Lin judgements are direct only if `inputs` is widened (Approved use-case changes, item 3). If the integrator does not apply that change, set both Lin judgements to `proxy` instead.

Grouping, strata order and headline metrics hold: `tamura2026-driver` and `tamura2026-all` (conventional, then targeted), `lin2026-longread` (high depth, then low). Headline `recall` for the driver and long-read groups, which matches the authors' view that sensitivity is the more relevant metric once the analysis is limited to driver fusions; `f1-score` for the consensus group, as in the authors' Fig. 2c.

Common limitations now on the Tamura judgements: haematologic cell lines only (170 conventional, 26 targeted), with clinical-sample results only in a figure; Genomon rows author-reported; default or recommended parameters only, while the authors show parameter changes recover some missed driver fusions. On the Lin judgements: FUSILLI authorship and tuning; dominant-fusion scoring over 74 listed B-ALL fusions, so the review burden of full output is not measured; wrong-fusion calls count as false positives; clinical truth from cytogenetics, FISH and short-read RNA-seq; paediatric B-ALL only, with PAX5::ZCCHC7 excluded and some subtypes untested; no caller versions.

The judgement `review` follows the reviewed CNV and somatic judgements: method `source-hash-verification`, `independent-cell-check`, `ai-assisted-source-review`; reviewer `claude`; `reviewed_at` 2026-10-09T20:55:00Z. After `records -- add` and the use-case change, pin the six with `npm run use-cases:repin -- docs/reviews/use-cases/tumour-rna-fusion-detection-2026-10-09.md <claim-id>...`.

## Approved use-case changes

Apply to `use-case-tumour-rna-fusion-detection`.

Items 1 and 2 do not change pinned fields:

1. Add `assessed_by` links to `rna-fusion-20261009-protocol-lin2026-high-depth`, `rna-fusion-20261009-protocol-lin2026-low-depth`, `rna-fusion-20261009-protocol-tamura2026-all-conventional`, `rna-fusion-20261009-protocol-tamura2026-all-targeted`, `rna-fusion-20261009-protocol-tamura2026-driver-conventional` and `rna-fusion-20261009-protocol-tamura2026-driver-targeted`. Add `source_ids` `rna-fusion-20261009-source-lin2026`, `rna-fusion-20261009-source-tamura2026` and `rna-fusion-20261009-source-tamura2026-supplementary`. Add `citation_locators`:
   - `rna-fusion-20261009-source-tamura2026-supplementary`: "Supplementary Tables 1, 3 and 5; see data/omics/use-case-coverage-rna-fusion-20261009/claims.csv"
   - `rna-fusion-20261009-source-tamura2026`: "Methods 'Comparison of detection algorithms'; Author contributions"
   - `rna-fusion-20261009-source-lin2026`: "Tables 3, 5 and 6; Materials and Methods 'Fusion Performance Evaluations'; see data/omics/use-case-coverage-rna-fusion-20261009/claims.csv"
2. Append to `evidence_gaps`:
   - "No linked comparison of several callers on adult solid tumours or FFPE tissue with printed per-caller values; Br J Cancer 2026 (1,233 FFPE solid tumours) reports Arriba and DRAGEN against panel assays only in figures."
   - "Driver-fusion truth sets in Tamura et al. 2026 were selected mostly from fusions called by at least four algorithms, including the algorithm scored, so sensitivity for fusions most callers miss is not measured."
   - "Per-caller results on 165 clinical haematologic samples in Tamura et al. 2026 are shown only in a figure."
   - "Lin et al. 2026 scores only the dominant fusion among 74 listed B-ALL fusions, so the review burden of long-read callers' full output is not measured."
   - "No linked study compares short-read and long-read callers on the same samples."
   - "The DREAM SMC-RNA fusion challenge results (Cell Systems 2021) were not retrieved, and Haas et al. 2019 prints per-method accuracy only in figures."
   - "No linked study reports interval estimates for per-caller sensitivity or precision."

Items 3 to 5 change pinned fields, so both existing judgements must be re-pinned in the same change:

3. `inputs`: replace "Paired-end tumour RNA-seq reads" with "Tumour RNA-seq reads: paired-end short reads (conventional or targeted capture) or long reads". Keep the second input unchanged. This is needed for the Lin judgements to be `direct`.
4. `setting`: "A 14-fusion synthetic Seraseq reference standard and a 229-sample paediatric cancer and haematologic cohort (67 ensemble-ascertained clinically relevant fusions) for Arriba, STAR-Fusion and the EnFusion ensemble; 12 short-read callers on conventional and targeted RNA-seq of haematologic cancer cell lines, scored against literature-supported driver fusions and against a consensus of the other callers (Tamura et al. 2026); and four long-read callers on nanopore whole-transcriptome sequencing of paediatric B-ALL at two depths, scored by dominant-fusion classification (Lin et al. 2026)."
5. `decision`: "Inspect per-caller sensitivity for validated driver fusions, the single-caller call counts that drive review burden, and the Seraseq and NCH evidence, matched to the intended specimen type and sequencing (short or long reads, conventional or targeted capture), before selecting a workflow and review burden."

Not approved: changes to `exclusions` (the new evidence does not cover adult solid tumours or novel-fusion discovery, so the exclusions stay), `clinical_scope`, `output` and facets. These can follow in a later reviewed change.

**Existing judgements.** I re-read `use-case-mapping-amp-20261007-issue11-enfusion-seraseq` and `use-case-mapping-amp-20261007-issue11-enfusion-nch-clinical` against the text in items 3 to 5. Both still hold. Their endpoints (Seraseq sensitivity, precision and counts; NCH retrospective sensitivity among 67 ensemble-ascertained fusions) are paired-end short-read measurements, which the widened `inputs` still include. The new `setting` keeps the Seraseq and NCH description, and the new `decision` still directs the reader to the Seraseq and NCH evidence. Their relevance (`direct`), limitations and reviewed evaluations need no change. I did not re-check their source values; that is unchanged since their review, and their evaluation and result pins are unaffected. Re-pin them by name with this review:

```sh
npm run use-cases:repin -- docs/reviews/use-cases/tumour-rna-fusion-detection-2026-10-09.md \
  use-case-mapping-amp-20261007-issue11-enfusion-seraseq \
  use-case-mapping-amp-20261007-issue11-enfusion-nch-clinical
```

## Evidence summary

Replaces the collector's `summary_proposal`, which said the Tamura group "wrote none of the 12 callers" and described Lin sensitivity as the fraction "of known fusions".

> Two new comparisons join the Seraseq reference and paediatric NCH cohort evidence; values cannot be pooled across studies. Tamura et al. 2026 ran 12 short-read callers on haematologic cancer cell lines; one, Genomon, comes from a co-author's group. On 61 driver fusions in conventional RNA-seq of 170 cell lines, Arriba detected all 61 (TPR 1), FusionCatcher 0.98, STAR-Fusion 0.93, InFusion 0.43 and STARChip 0.41. On 24 driver fusions in targeted RNA-seq of 26 cell lines, Arriba again reached 1 and STAR-Fusion 0.92, InFusion 0.17 and STARChip 0. A driver fusion entered these truth sets only if at least four callers, including the one scored, found it and it had literature or RT-PCR support, so fusions that most callers miss are under-represented and these values may overstate sensitivity. Against a consensus of the other callers, the number of single-caller calls, a measure of review burden, ranged on conventional RNA-seq from 327 for TrinityFusion-D and 1,061 for STAR-Fusion (PPV 0.39) to 9,567 for Arriba (PPV 0.08), 22,445 for FusionCatcher and 695,295 for Pizzly. On nanopore long reads from 51 paediatric B-ALL samples (Lin et al. 2026), scored on the dominant fusion per sample, JAFFAL reached sensitivity 0.76, LongGF 0.70 and FusionSeeker 0.63, with precision 0.79 to 0.95; the authors' own FUSILLI reached 0.81. At about one tenth of the depth, sensitivity was 0.09 to 0.27. These are cell lines and paediatric leukaemia samples only: no linked comparison covers adult or solid tumours, FFPE tissue or novel-fusion discovery, none reports interval estimates, and none establishes clinical performance.

`source_ids`: `amp-oncology-rna-20261007-source-pmc8642973`, `rna-fusion-20261009-source-tamura2026`, `rna-fusion-20261009-source-tamura2026-supplementary`, `rna-fusion-20261009-source-lin2026`.

| Statement | Record (`rna-fusion-20261009-`) | Printed |
| --- | --- | --- |
| Genomon from a co-author's group | `claim-tamura2026-genomon-developer` | |
| 61 and 24 driver truth pairs | `protocol-tamura2026-driver-conventional`, `-targeted` (`denominator`) | 61, 24 |
| Arriba conventional TPR 1 | `result-tamura2026-arriba-driver-conventional-recall` | 1 |
| FusionCatcher conventional 0.98 | `result-tamura2026-fusioncatcher-driver-conventional-recall` | 0.98 |
| STAR-Fusion conventional 0.93 | `result-tamura2026-star-fusion-driver-conventional-recall` | 0.93 |
| InFusion conventional 0.43 | `result-tamura2026-infusion-driver-conventional-recall` | 0.43 |
| STARChip conventional 0.41 | `result-tamura2026-starchip-driver-conventional-recall` | 0.41 |
| Arriba targeted 1 | `result-tamura2026-arriba-driver-targeted-recall` | 1 |
| STAR-Fusion targeted 0.92 | `result-tamura2026-star-fusion-driver-targeted-recall` | 0.92 |
| InFusion targeted 0.17 | `result-tamura2026-infusion-driver-targeted-recall` | 0.17 |
| STARChip targeted 0 | `result-tamura2026-starchip-driver-targeted-recall` | 0 |
| TrinityFusion-D 327 single-caller calls | `result-tamura2026-trinityfusion-d-all-conventional-false-positive-count` | 327 |
| STAR-Fusion 1,061, PPV 0.39 | `result-tamura2026-star-fusion-all-conventional-false-positive-count`, `-precision` | 1,061; 0.39 |
| Arriba 9,567, PPV 0.08 | `result-tamura2026-arriba-all-conventional-false-positive-count`, `-precision` | 9,567; 0.08 |
| FusionCatcher 22,445 | `result-tamura2026-fusioncatcher-all-conventional-false-positive-count` | 22,445 |
| Pizzly 695,295 | `result-tamura2026-pizzly-all-conventional-false-positive-count` | 695,295 |
| JAFFAL 0.76, LongGF 0.70, FusionSeeker 0.63 | `result-lin2026-jaffal-high-depth-recall`, `-longgf-`, `-fusionseeker-` | 0.76, 0.70, 0.63 |
| Precision 0.79 to 0.95 (comparators) | `result-lin2026-jaffal-high-depth-precision` (0.79), `result-lin2026-longgf-high-depth-precision` (0.95); FusionSeeker 0.94 | 0.79, 0.95 |
| FUSILLI 0.81 | `result-lin2026-fusilli-high-depth-recall` | 0.81 |
| Low depth 0.09 to 0.27 | `result-lin2026-fusionseeker-low-depth-recall` (0.09) to `result-lin2026-fusilli-low-depth-recall` (0.27) | 0.09, 0.27 |

The 170 and 26 cell lines are from the Tamura dataset records; 51 samples and "about one tenth of the depth" (mean 11.2 million versus 1.4 million reads) are from the Lin dataset record and Results.

## Checks run

`npm test` passed (46 files, 499 tests) and `npm run typecheck` passed, on the worktree with the reviewed batch. The batch is not yet in the store, so these tests do not read it; the scratch `addBatch` and `deriveUseCaseInputs` dry run is the check that covers it. `npm run build` and SHACL shapes were not run.

## Remaining gaps

- The PDF text layer was produced by the same `pdftotext` tool the extractor used; the arithmetic checks cover column misreads, but not a shared text-layer defect that is also arithmetically consistent.
- Figures were not checked, including Tamura's clinical-sample results (Fig. 6) and Lin's per-subtype figures.
- Lin Supplemental Tables S1 to S11 were not retrieved, so per-sample classifications and the 79 versus 81 count cannot be checked.
- Collector's gaps unchanged: adult solid tumours and FFPE with printed per-caller values, DREAM SMC-RNA, Haas et al. 2019, short- and long-read callers on the same samples.
