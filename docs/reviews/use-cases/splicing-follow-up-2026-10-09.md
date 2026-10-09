# Splicing follow-up selection: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-splicing-follow-up-20261009/` (682 records as collected, 680 after review). Use case: `use-case-splicing-follow-up`.

Reviewer: a separate Claude review agent that did not extract the batch. No human review is claimed. Nothing was executed or reproduced; this is a check of transcription against the pinned sources, plus a judgement of the relevance claims.

## Outcome

- All four pinned artifacts re-download to their recorded SHA-256, including the Znabu et al. PDF. The three archived `artifacts/*.gz` decompress to the pinned bytes.
- All 522 results match their source cells: printed value, numeric value, locator, metric, qualifier, direction and the evaluation's configuration, protocol and dataset. Every expected cell has exactly one result.
- Every Riepe et al. rate and MCC reproduces from its printed confusion matrix.
- No value is wrong and no result is disputed. Corrections are of form or description only (listed below):
  - 12 integer cells are now printed `1` or `0` instead of `1.0` or `0.0`;
  - 10 Znabu AUROC and AP units are now `unitless`, the store's convention;
  - one claim locator is corrected;
  - the two source notes on version and hash were wrong and are rewritten;
  - limitations are added for HAL, S-Cap, Spidex, the SpliceAI background scores and the Znabu SpliceAI imputation.
- The Smith and Kitzman sources are not duplicates. The existing `evidence-expansion-splice-evaluation-6960a140` pins the bioRxiv preprint (PMC10187268); the new record pins the Genome Biology version (PMC10734170). Both are kept.
- SQUIRLS now reuses `rna-splicing-20261009-method-squirls` and CADD reuses `somatic-oncogenicity-20261009-method-cadd`; this batch's two method records are removed. No other tool in the batch exists in main's store or in those batches. The reused CADD record's description is too narrow; a replacement is given under Follow-up corrections.
- All 10 judgements hold and are `source_checked`: 9 as `proxy` with `reviewed_evaluations` filled, and MLH1 as `outside_scope` with its grouping fields removed. Pins are left for the integrator.
- The dry run loaded the store, the reviewed patient RNA splicing batch, the reviewed somatic oncogenicity batch, then this batch. All validate, and with the approved use-case changes and pins, all 14 judgements on the use case derive as active.

## How the check was done

1. Downloaded each `artifact_url` into its own empty directory and hashed it. Unzipped the Smith and Kitzman supplementary zip and hashed the MOESM3 member.
2. Read the Smith and Kitzman workbook with a stdlib OOXML reader written for this review (shared strings, raw `<v>` text, number format; all cells General). Read Riepe et al. Tables 3 to 5 from `table-wrap` `humu24212-tbl-0003` to `-0005` with a separate XML reader. Read the Znabu et al. results table from the PDF text layer (`pdftotext -layout`). The extractor's `extract/*.py` was not imported or run.
3. Built every cell's expected identity from its headers and row labels, then matched each result through `source_locator` and compared printed value, numeric value, raw cell text, metric, qualifier, unit, direction, interval, and the linked evaluation's configuration, protocol and dataset.
4. Recomputed accuracy, PPV, sensitivity, specificity, NPV and MCC from TP, FP, TN and FN for all 31 Riepe rows.
5. Recomputed the Smith and Kitzman prose medians from the sheet.
6. Read the cited Methods, Results and Discussion paragraphs of all three sources, their author lists and competing-interest statements, and the dataset references of Smith and Kitzman.
7. Dry run in memory: loaded the store, then validated in turn the reviewed patient RNA splicing batch, the reviewed somatic oncogenicity batch and this batch, each on top of the last. The branches' vocabularies were merged in a scratch copy, since each branch adds metric concepts; shared blocks are byte-identical. I then applied the approved use-case changes, computed pins with `claimPins`, and ran `deriveUseCaseInputs`. Nothing was written to either store.

Paragraph numbers count body paragraphs and exclude figure and table captions.

## Sources and hashes

| Source | Pinned SHA-256 | Re-download 2026-10-09 |
| --- | --- | --- |
| `splicing-follow-up-20261009-source-smith2023` (PMC10734170 XML) | `5aceff06...0769` | Match; archive decompresses to it |
| `splicing-follow-up-20261009-source-smith2023-table-s2` (MOESM3 xlsx member) | `c5ed8dc1...00fa` | Match; archive decompresses to it. The outer Europe PMC zip differs per request (this copy `c7d4f987...e3f4`), as `hash_scope` says |
| `splicing-follow-up-20261009-source-riepe2021` (PMC8360004 XML) | `595be536...7112` | Match; CC BY-NC, not archived |
| `splicing-follow-up-20261009-source-znabu2026` (bioRxiv v1 PDF) | `52a2d1cc...7552` | Match; archive decompresses to it |
| `evidence-expansion-splice-evaluation-6960a140` (stored; PMC10187268 XML) | `6960a140...f071` | Match |

## Values checked

| Table | Results | Matched | Wrong |
| --- | --- | --- | --- |
| Smith and Kitzman Additional file 3, sheet 'Sensitivity 10% SDV' (166 non-blank cells) | 166 | 166 | 0 |
| Riepe et al. Tables 3 to 5 (31 rows, 11 columns) | 341 | 341 | 0 |
| Znabu et al. Section 4 results table (5 rows, n, AUROC, AP with interval) | 15 | 15 | 0 |
| Total | 522 | 522 | 0 |

Riepe recomputation: every derived value matches its confusion matrix after rounding. Three sensitivities are exactly 62.5% (40 of 64) and are printed as 63, which is half-up rounding. Row totals are constant within each table: 71 (ABCA4 NCSS), 81 (ABCA4 DI) and 61 (MYBPC3). The positives are 64, 21 and 34, matching Results P20.

Smith and Kitzman prose check: the medians in Results P13 (SpliceAI 87.3%, ConSpliceML 85.8%, Pangolin 79.9%) reproduce from the 'all variants' rows over all six columns (0.8726, 0.8584, 0.7990). They therefore include the MLH1 column, which this use case treats as outside scope. This is now in the claim's review note.

Two patterns in the sheet are explained by the Methods, not by errors:
- HAL's all-variant row equals its exonic row in every column, because HAL scores exonic variants only (Methods P31).
- FAS has no intronic values, because its assay covers the exon only.

## The collector's concerns

### Riepe: cutoffs and variant selection

Both concerns are real. Neither shows a value to be wrong, so they stay as limitations, not evidence concerns or disputes.

- **Cutoffs.** Methods P19 and Results P23 say the cutoff for each tool was chosen from the ROC curve of each data set, and Table 2 lists those cutoffs. Tables 3 to 5 do not restate which cutoff they use, but P24 presents them as the performance at the chosen thresholds. The confusion matrices are therefore in-sample at tuned cutoffs and likely optimistic. This is recorded on every Riepe protocol, configuration and judgement, and as `missing_metadata` for the metric implementation.
- **Selection.** ABCA4 variants were chosen for testing when at least two Alamut programs predicted a change, and MYBPC3 variants when MaxEntScan scored below the reference (Methods P7). The authors discuss this bias and report the opposite of what it would predict (Discussion P26): Alamut 3/4 performs best on MYBPC3, and MaxEntScan only relatively well on ABCA4. Both facts are now in the limitations.
- **Spidex, found at review.** Spidex has 5 unscored variants in ABCA4 NCSS and 3 in MYBPC3, yet its four counts sum to the same total as every other tool. The unscored variants were therefore counted in some cell, and the article does not say which; P16 sets missing scores to zero only for the Alamut tools. Recorded on the Spidex configuration, its results and the protocols.

### Smith and Kitzman: SpliceAI 1.3 versus 1.3.1, and masking

Confirmed from Methods P30.
- Benchmark variants were scored with SpliceAI 1.3.1, with distance set to the exon length and both masked and unmasked scores computed.
- The background set that fixes each tool's threshold used SpliceAI 1.3 precomputed scores from Illumina BaseSpace, whose distance and masking settings the article does not state.
- For both SpliceAI and Pangolin, the article does not say whether Table S2 uses masked or unmasked scores.

The threshold and the benchmark scores may therefore come from differently configured runs. That limits the SpliceAI column and the masking question applies to both tools, but nothing shows a value to be wrong. Recorded on the two configurations, the six Smith protocols and the six Smith judgements.

A related point found at review: HAL and S-Cap leave 56.5% and 61.0% of the background unscored (Methods P31). Their 10% thresholds therefore come from a different part of the background than the other tools' thresholds. Recorded on both configurations, their results, the protocols and the judgements.

### Smith and Kitzman source record

The collector's note said the existing record had "the same Europe PMC URL". It does not:

| Record | Artifact | DOI | Version |
| --- | --- | --- | --- |
| `evidence-expansion-splice-evaluation-6960a140` (stored) | PMC10187268 full-text XML | 10.1101/2023.05.04.539398 | bioRxiv preprint, 2023-05 |
| `splicing-follow-up-20261009-source-smith2023` (new) | PMC10734170 full-text XML | 10.1186/s13059-023-03144-z | Genome Biology 24:294, 2023-12 |

Both re-download to their pinned hashes today. The bytes differ because they are different versions of the work, not because of retrieval. One record cannot serve both: each `artifact_sha256` binds a different document, and the batch's values come from the peer-reviewed version and its supplement. Both are kept. The new record's `version_note` now names the preprint record, its DOI and hash, and says why both stay. The stored record is unchanged; it is cited only by `catalog-task-rna-splice-sites`.

### Znabu et al.

- **Preprint hash.** `hash_scope` said a re-download gives different bytes. Mine gave identical bytes; the PDF's ModDate (2026-10-09 21:52:24 BST) is the one bioRxiv stamped at the collector's retrieval. The text now says the re-download matched, and to compare the text layer if a later one does not.
- **Population.** Znabu et al. drop unlabelled variants from 28,972 to 27,733 (1,050 SDVs). This equals `cohort_variants` of `rewire-mfass-v2-dataset`. Variant-level identity was not checked; that is recorded, and the judgement keeps the constraint against pooling with the matched and v2 held-out protocols.
- **Independence.** No author developed a compared tool, and the authors declare no competing interests. Three tools were run through the Proto ecosystem (Merchant et al. 2026), which is not by the benchmark authors.
- **Added limitations.**
  - SpliceAI was given 0 where it returns no score (outside annotated genes). The authors report the same order on the 12,855 variants that SpliceAI scores above zero; those values are not extracted.
  - MMSplice was scored on a reconstructed cassette context.
  - The predictors may have seen these exons' wild-type sites in training (authors' caveat).

### Proxy versus direct

All nine assay judgements stay `proxy`, consistent with the four existing judgements. The matched MFASS judgement says the endpoint "informs assay-oriented prioritisation under its declared conditions. Selecting variants for a different follow-up experiment requires transfer validation." The new sources measure splicing in an experiment, as MFASS does, but none measures the decision itself: which variants a tool would choose for a new experiment, and how many of those then prove splice-disruptive. Instead:
- Smith and Kitzman report sensitivity at a genome-wide call rate, with no precision on the benchmark.
- Riepe et al. report classification at cutoffs tuned on the same data, on variants selected with some of the tools being compared.
- Znabu et al. report ranking metrics on a whole reporter cohort.

A direct judgement would need precision or yield among tool-selected variants, confirmed in the intended assay, at a stated follow-up capacity. Grading these sources direct while the existing MFASS top-100 precision judgement is proxy would be inconsistent. That judgement is closer to a selection endpoint than any of them. This is recorded as a new evidence gap.

MLH1 stays `outside_scope`. Methods P28 says its labels come from patient blood RNA RT-PCR or minigene analysis, and that essential splice-site variants from Lynch syndrome patients are included without molecular evidence. The use case excludes patient-RNA effects and pathogenicity. Following the EGFR review's precedent, its grouping fields are removed, so it no longer takes a stratum in the Smith and Kitzman comparison; its evaluations do not count. The other five Smith strata are renumbered 1 to 5.

## Cross-branch records

| Tool | This batch | Elsewhere | Decision |
| --- | --- | --- | --- |
| SQUIRLS | `splicing-follow-up-20261009-method-squirls` | `rna-splicing-20261009-method-squirls` (reviewed; integrates first) | Removed here; `splicing-follow-up-20261009-config-smith2023-squirls-1-0-0` now has `configuration_of` `rna-splicing-20261009-method-squirls` |
| SpliceAI, Pangolin | reuse `catalog-model-spliceai`, `catalog-model-pangolin` | Same targets in the patient RNA splicing batch | Already reused; no change |
| SPiP | not in this batch | `rna-splicing-20261009-method-spip` | No overlap |
| CADD | `splicing-follow-up-20261009-method-cadd` | `somatic-oncogenicity-20261009-method-cadd` (reviewed; integrates before this batch) | Removed here; `splicing-follow-up-20261009-config-riepe2021-cadd-1-6` now has `configuration_of` `somatic-oncogenicity-20261009-method-cadd`. Its description is too narrow; see Follow-up corrections |

I searched main's store for every other tool in the batch (Alamut consensus, DSSP, GeneSplicer, MaxEntScan, MMSplice, NNSPLICE, SpliceRover, SpliceSiteFinder-like, ConSpliceML, HAL, S-Cap, SPANR or SPIDEX, SpliceTransformer). None exists there. Among the other open branches' batches, only CADD recurs.

The batch now depends on the patient RNA splicing and somatic oncogenicity batches. It will not validate until both are in the store, because `rna-splicing-20261009-method-squirls` and `somatic-oncogenicity-20261009-method-cadd` must exist.

## Corrections made in the batch

The batch is not in the store, so fields were edited in place. The collector's copy has SHA-256 `38012f610e442a8b6f9e51bbd500bf0cd76600cf6235eee63dc6cc9cf7d02152` (batch) and `5763ccbbda692a364350eea02dc78d9a1a54486539fb3ca37b6c07c630c04e1c` (claims.csv). A field-by-field diff shows no change to any ID, metric, qualifier, direction, locator (except one claim), interval, comparison field or evaluation link.

| Record | Field | Change |
| --- | --- | --- |
| `splicing-follow-up-20261009-method-squirls` | record | Removed; replaced by `rna-splicing-20261009-method-squirls` |
| `...-config-smith2023-squirls-1-0-0` | `links` | `configuration_of` now `rna-splicing-20261009-method-squirls` |
| `splicing-follow-up-20261009-method-cadd` | record | Removed; replaced by `somatic-oncogenicity-20261009-method-cadd` |
| `...-config-riepe2021-cadd-1-6` | `links` | `configuration_of` now `somatic-oncogenicity-20261009-method-cadd` |
| 12 Smith results with raw cell `1` or `0` | `printed_value`, `numeric_value` | `1.0` and `0.0` to `1` and `0`, the stored and displayed text; `claims.csv` synced |
| 10 Znabu AUROC and AP results | `unit` | `fraction` to `unitless`, the store's convention for these metrics |
| All 522 results | `status`, `review` | `source_checked`; independent review block. Notes on Riepe recomputation, Spidex, HAL and S-Cap |
| `...-source-smith2023` | `version_note` | Rewritten: preprint versus journal version (see above) |
| `...-source-znabu2026` | `hash_scope` | Rewritten: the re-download matched |
| `...-data-smith2023-pou1f1-exon2-mpsa`, `...-wt1-exon9-mpsa` | `scope_note` | Published by the benchmark authors' group (refs 57, 58) |
| `...-config-smith2023-spliceai-1-3-1`, `-pangolin-1-0-2` | `parameters` | Double full stop fixed |
| `...-config-smith2023-spliceai-1-3-1` | `limitations` | Background distance and masking unstated |
| `...-config-smith2023-hal`, `-s-cap`, `...-config-riepe2021-spidex-1-0` | `limitations` | Partial scoring and its effect |
| 6 Smith, 3 Riepe and the Znabu protocol | `limitations` | Items listed in the concerns above |
| `...-claim-riepe2021-mmsplice-spidex-di-excluded` | `source_locator` | Paragraph 3 to paragraph 7 (the last); `claims.csv` synced |
| 4 descriptive claims | `status`, `review` | Checked against the text; correct as worded |
| 10 judgements | `status`, `review`, `limitations`; `reviewed_evaluations` for 9; `stratum_order` for 3 Smith judgements; grouping fields, `rationale` and `description` for MLH1 | See Relevance judgements |
| All other records | `status` | `source_checked` |

`research.md`, `sources.md` and `coverage.json` are the collector's notes. They still describe the source records as sharing a URL and list the SQUIRLS and CADD methods; they were left unchanged.

## Vocabulary

`negative-predictive-value` is left as the reviewed block. It is byte-identical to the patient RNA splicing branch's copy.

`true-negative-count` uses the block finalised by the rare-reanalysis review, with `skos:exactMatch` to STATO_0000597. This branch's block was compared with `data/vocab/metric.ttl` on the rare-reanalysis branch on 2026-10-09 and is byte-identical, so no edit was needed. My own check agrees with that match: STATO_0000597 is "number of true negative", "a count which denotes how many elements are correctly classified as void of a feature they are actually known to be missing" (OLS, retrieved 2026-10-09). The sibling count concepts carry exact matches to STATO_0000595, STATO_0000596 and STATO_0000598.

## Relevance judgements

| Judgement | Grade | Endpoint fit | Changes | Reviewed evaluations |
| --- | --- | --- | --- | --- |
| `...-riepe2021-abca4-ncss` | proxy | Classification against midigene results on 71 selected variants; 90% positive | Selection observation; Spidex counting | 11 |
| `...-riepe2021-abca4-di` | proxy | As above on 81 deep-intronic variants; MMSplice and Spidex excluded by the authors | As above | 9 |
| `...-riepe2021-mybpc3-ncss` | proxy | As above on 61 minigene-tested variants | As above | 11 |
| `...-smith2023-brca1-sge` | proxy | Sensitivity at a 10% genome-wide call rate, endogenous editing | Masking, HAL and S-Cap, SpliceAI background | 8 |
| `...-smith2023-fas-exon6-mpsa` | proxy | As above, minigene MPSA, exonic only | As above | 8 |
| `...-smith2023-pou1f1-exon2-mpsa` | proxy | As above | As above; stratum 4 to 3 | 8 |
| `...-smith2023-mst1r-exon11-mpsa` | proxy | As above | As above; stratum 5 to 4 | 8 |
| `...-smith2023-wt1-exon9-mpsa` | proxy | As above | As above; stratum 6 to 5 | 8 |
| `...-smith2023-mlh1-curated` | outside_scope | Labels include patient RNA and a pathogenicity rule | Grouping fields removed; rationale names the Methods section | none |
| `...-znabu2026-mfass` | proxy | AUROC and AP on the whole labelled MFASS cohort | SpliceAI imputation; MMSplice context | 5 |

Headline metrics are right:
- `matthews-correlation-coefficient` is the one Riepe et al. recommend for unbalanced sets (Methods P19).
- `recall` is the only metric in the Smith and Kitzman sheet.
- `average-precision` is Znabu et al.'s primary metric at a 3.79% base rate.

The Riepe strata run from ABCA4 NCSS to ABCA4 DI to MYBPC3, and the Smith strata from endogenous editing to the four minigene exons.

## Use-case changes (coverage.json)

- The ten `assessed_by` links are right, including MLH1, since every judgement needs its link.
- The collector proposed no change to pinned fields, to avoid withholding the four existing judgements. I approve changing `decision` and `setting`. Both describe only the matched MFASS study, which misdescribes a page that will show three more sources.
- The existing `output`, `exclusions`, `clinical_scope`, `inputs` and `intended_users` still fit and are unchanged.
- The proposed gaps are kept as written, and one gap is added on why the evidence is proxy.
- The three article sources are added to `source_ids`, because the new setting text rests on them. The Smith supplement stays cited by its judgements only.

The change withholds the four existing judgements until re-pinned. In the dry run they are withheld with "pinned evidence changed since review (use-case-splicing-follow-up)" and active again once re-pinned. The integrator must re-pin them in the same change as the ten new judgements:

```
npm run use-cases:repin -- docs/reviews/use-cases/splicing-follow-up-2026-10-09.md \
  use-case-mapping-20260930-339-25925e279972 use-case-mapping-amp-20261007-feng-splice-acceptor \
  use-case-mapping-amp-20261007-feng-splice-donor use-case-mapping-splicing-mfass-matched-v1
```

### Approved use-case changes

Exact final values for `use-case-splicing-follow-up`. Fields not listed are unchanged.

`links`: keep the four existing `assessed_by` links and add `assessed_by` links to:

```
splicing-follow-up-20261009-protocol-riepe2021-abca4-ncss
splicing-follow-up-20261009-protocol-riepe2021-abca4-di
splicing-follow-up-20261009-protocol-riepe2021-mybpc3-ncss
splicing-follow-up-20261009-protocol-smith2023-brca1-sge-tn10
splicing-follow-up-20261009-protocol-smith2023-fas-exon6-mpsa-tn10
splicing-follow-up-20261009-protocol-smith2023-mlh1-curated-tn10
splicing-follow-up-20261009-protocol-smith2023-mst1r-exon11-mpsa-tn10
splicing-follow-up-20261009-protocol-smith2023-pou1f1-exon2-mpsa-tn10
splicing-follow-up-20261009-protocol-smith2023-wt1-exon9-mpsa-tn10
splicing-follow-up-20261009-protocol-znabu2026-mfass-full-cohort
```

`source_ids`:

```
evidence-expansion-mfass-readme-62a93814
use-case-source-mfass-matched-intake-194a78b
rewire-mfass-matched-v1-source-report
splicing-follow-up-20261009-source-smith2023
splicing-follow-up-20261009-source-riepe2021
splicing-follow-up-20261009-source-znabu2026
```

`decision`:

> Inspect the configurations evaluated against experimentally measured splicing of human SNVs (MFASS reporter assays, saturation minigene and genome-editing assays, and mini- or midigene tests), with their limitations, before selecting a method and designing validation in the intended experimental setting.

`setting`:

> Each linked comparison scores splice predictors against splicing measured in an experiment. MFASS measures exon recognition of human SNVs in an artificial minigene reporter; the matched study evaluates genomic-context SpliceAI and Pangolin configurations against this endpoint on a fixed held-out population. Saturation minigene assays and BRCA1 saturation genome editing measure every SNV in and around single exons, and mini- or midigene tests in HEK293T cells assess selected ABCA4 and MYBPC3 variants. Each source reports its own population, thresholds and metrics, and results are not pooled across sources.

`evidence_gaps`: keep the nine existing entries and append:

```
No linked source measures precision among the variants a tool would select for a new splicing experiment. The sources report sensitivity at a genome-wide background call rate (Smith and Kitzman 2023), classification at cutoffs tuned on the same data (Riepe et al. 2021), or ranking metrics on a whole assay cohort (Znabu et al. 2026).
Smith and Kitzman 2023 report sensitivity at transcriptome-normalised thresholds; precision and prAUC per tool and dataset are figure-only (Figure 3), and the 5% and 20% call-rate sheets and the sensitivity-AUC sheet of Table S2 are not extracted.
Riepe et al. 2021 Tables 3 to 5 do not state the cutoff applied; Table 2 cutoffs were optimised on the same data sets, so values may be optimistic.
Znabu et al. 2026 is a preprint scoring the whole labelled MFASS cohort; it is not comparable with the matched-annotation or v2 held-out MFASS protocols.
CAGI5 Vex-seq and MaPSy assessments (Mount et al. 2019) print per-submission values for challenge entries, most of which are not released tools; not extracted.
No independent printed comparison on Vex-seq or MaPSy for current tools (SpliceAI, Pangolin, SpliceTransformer) was found.
OpenSplice (bioRxiv 2026.05.22.727141) and SeqSplice BRCA1/BRCA2 (Genome Res 2025) are leads not screened for per-tool tables.
```

`citation_locators`: keep the three existing entries and append:

```
{"source_id": "splicing-follow-up-20261009-source-smith2023", "locator": "Results 'Benchmarking in the context of genome-wide prediction'; Methods 'Saturation mutagenesis datasets', 'Manual curation of clinical MLH1 variants' and 'Scoring with eight splice effect predictors'"}
{"source_id": "splicing-follow-up-20261009-source-riepe2021", "locator": "Methods 'Datasets' and 'In silico splice prediction tools'; Tables 3 to 5"}
{"source_id": "splicing-follow-up-20261009-source-znabu2026", "locator": "Sections 2 to 4 and the Section 4 results table"}
```

### Do the four existing judgements still hold?

Yes, each unchanged, as `proxy`.

- `use-case-mapping-splicing-mfass-matched-v1` and `use-case-mapping-20260930-339-25925e279972`: the new setting keeps the sentence describing the matched study and the MFASS endpoint, and the decision still covers MFASS reporter assays. Their limitations (held-out population, tie sensitivity, no pooling with historical runs) are untouched. The existing exclusion against pooling the matched study with historical runs, and the new judgements' constraints, keep Znabu et al. separate from both.
- `use-case-mapping-amp-20261007-feng-splice-acceptor` and `-donor`: these are sequence-label classification tasks, not measured-splicing comparisons. The new decision says "configurations evaluated against experimentally measured splicing", which these do not strictly meet. But their rationale already grades them proxy because the endpoint differs, and the old decision ("Inspect the matched MFASS configurations") did not cover them either. Their grade and limitations remain correct under the new text.

## Evidence summary

The collector's proposal is accurate in every number. It needs four changes:
- name the authors' independence and the Smith and Kitzman assay authorship;
- say why every result is proxy;
- add the Znabu SpliceAI imputation;
- add HAL's exonic-only scoring.

Final text:

> Three independent comparisons score several splice predictors against experimentally measured splicing of human SNVs; none of their authors developed the tools compared. Znabu et al. (2026, preprint) scored all 27,733 labelled MFASS reporter SNVs, of which 1,050 disrupt splicing. Average precision was 0.421 for Pangolin (bootstrap 95% interval 0.386 to 0.454), 0.321 for SpliceAI, 0.317 for SpliceTransformer, 0.256 for MMSplice and 0.228 for SPANR, with AUROC 0.888, 0.819, 0.786, 0.758 and 0.748. SpliceAI was given a score of zero where it returns none. This is a different MFASS population from the matched and v2 held-out protocols and is not pooled with them. Smith and Kitzman (2023) set each tool's threshold so that it flags 10% of 500,000 random exonic and near-exonic SNVs, then measured sensitivity on saturation assays, two of which their own group produced. SpliceAI detected 0.982 of splice-disruptive variants in BRCA1 saturation genome editing, 0.885 in POU1F1 exon 2, 0.860 in WT1 exon 9, 0.539 in FAS exon 6 and 0.237 in MST1R exon 11; Pangolin detected 0.982, 0.948, 0.667, 0.487 and 0.330. Sensitivity depends strongly on the exon, precision is not measured at these thresholds, and HAL and S-Cap score only part of the variants. A curated MLH1 column is recorded but judged outside scope, because its labels include patient RNA and a pathogenicity rule. Riepe et al. (2021) tested up to 11 tools on ABCA4 and MYBPC3 variants assayed in mini- or midigenes. MCC for SpliceAI was 0.42 for ABCA4 noncanonical splice sites, 0.84 for ABCA4 deep-intronic variants and 0.35 for MYBPC3, where the Alamut 3/4 consensus reached 0.53. Those variants were chosen for testing with Alamut or MaxEntScan, and the cutoffs were tuned on the same data. None of these sources measures how many variants a tool would select for a new experiment and how many of those then prove splice-disruptive, so all are proxy evidence for that choice. All values are transcribed from the publications, not reproduced. Reporter and minigene endpoints do not establish patient-RNA effects or pathogenicity, and results from different sources must not be pooled. This summary describes evidence and does not recommend a method.

Every number is a `source_checked` result in this batch:
- Znabu: `splicing-follow-up-20261009-result-znabu2026-{pangolin,spliceai,splicetransformer,mmsplice,spanr}-{ap,auroc}` and `...-znabu2026-pangolin-n` (27,733). The 1,050 SDVs come from Section 2, recorded on the protocol.
- Smith and Kitzman, rounded to three decimals: `...-result-smith2023-{brca1-sge,pou1f1-exon2-mpsa,wt1-exon9-mpsa,fas-exon6-mpsa,mst1r-exon11-mpsa}-{spliceai-1-3-1,pangolin-1-0-2}-all`. The 500,000 background SNVs and 10% call rate come from the protocol.
- Riepe: `...-result-riepe2021-{abca4-ncss,abca4-di,mybpc3-ncss}-spliceai-1-3-1-mcc` and `...-riepe2021-mybpc3-ncss-alamut-consensus-mcc`.

The summary claim's `result_ids` should be these 25 results.

## Follow-up corrections

These apply to records on other branches. They are not edited here; the lead will apply them as reviewed changes once both batches are in the store.

### `somatic-oncogenicity-20261009-method-cadd`: `description`

Current value: "Variant effect predictor for missense variants."

This is narrower than the tool. CADD scores single nucleotide variants and short insertions and deletions anywhere in the reference assembly, not only missense variants. This batch uses it to score noncanonical splice-site and deep-intronic SNVs (Riepe et al. Tables 3 and 4).

Replacement value:

> Combined Annotation-Dependent Depletion: a genome-wide variant deleteriousness score that integrates more than 60 genomic features in a machine learning model trained to separate simulated de novo variants from variants fixed in human populations since the human-chimpanzee split. It scores single nucleotide variants and short insertions and deletions anywhere in the reference assembly, not only missense variants (Rentzsch et al. 2019, Nucleic Acids Research 47:D886).

Sources:
- Rentzsch P, Witten D, Cooper GM, Shendure J, Kircher M. CADD: predicting the deleteriousness of variants throughout the human genome. Nucleic Acids Research 2019;47(D1):D886-D894. DOI 10.1093/nar/gky1016, PMC6323892. The replacement restates its abstract (Europe PMC record, retrieved 2026-10-09).
- Riepe et al. 2021, Table 1, row 'CADD' ("Integrates more than 60 genomic features into a single score"; trained on simulated and observed SNVs, insertions and deletions), which cites that paper as ref 38. This is `splicing-follow-up-20261009-source-riepe2021`.

The store has no source record for the CADD paper itself. When applying the change, add `splicing-follow-up-20261009-source-riepe2021` to the method's `source_ids`, so that the description rests on a pinned source, and cite this review in the provenance entry. The method's `reported_name`, facets and links need no change.

## Checks run

- Dry run in memory (store, then the patient RNA splicing batch, then the somatic oncogenicity batch, then this batch, with a merged scratch vocabulary): all three batches pass `recordSchema`, the vocabulary check, the attribute check and `validateRecords`. With the approved use-case changes, all 14 judgements derive as active after pinning. Before re-pinning, the four existing judgements are withheld.
- `npm run typecheck`: exit 0.
- `npm run records -- check`: 30,371 records match their provenance (the batch is not in the store).
- `npm test`: 499 of 499 pass.
- `npm run build` was not run, as instructed.

## Remaining gaps

- The Riepe cutoffs are unstated and tuned; the analysis scripts (github.com/cmbi/Benchmarking_splice_prediction_tools) were not read and could settle which cutoffs Tables 3 to 5 use.
- How Spidex's unscored variants were counted is unresolved.
- The masking setting behind Table S2, and the SpliceAI 1.3 background settings, are unresolved.
- Smith and Kitzman per-dataset counts (Additional file 2) and figure-only prAUC values were not read.
- Znabu et al. variant-level identity with `rewire-mfass-v2-dataset` was not checked; the released per-tool scores would allow it.
- Not covered, as the collector recorded: CAGI5 per-submission tables, Vex-seq and MaPSy comparisons, OpenSplice, SeqSplice and the remaining Table S2 sheets.
