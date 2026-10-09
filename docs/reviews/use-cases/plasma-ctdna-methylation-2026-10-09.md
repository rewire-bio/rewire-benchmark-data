# Plasma ctDNA methylation: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-ctdna-methylation-20261009/` (487 records). Use case: `use-case-plasma-ctdna-methylation`.

Reviewer: a separate Claude review agent that did not extract the batch. No human review is claimed. Nothing was executed or reproduced; this is a check of transcription against the pinned sources, plus a judgement of the relevance claims.

## Outcome

- Six of the seven source artifacts re-download to the pinned SHA-256, and the two archived `artifacts/*.gz` decompress to the same bytes. The DecoNFlow preprint PDF cannot be reproduced by re-download, because bioRxiv rewrites the file on every download. No result value comes from that PDF (see Sources and hashes).
- All 380 results match their source cells. No numerical value, printed value, metric, qualifier, unit, direction, denominator or scored n was wrong, and no result is attached to the wrong configuration or protocol. Every expected cell has exactly one result.
- Both of the collector's evidence concerns are real. Both are narrower than recorded, so I moved each from the whole source down to the affected values:
  - 30 DecoNFlow RRBS-CL results for five tools are `disputed`, and their five evaluations are excluded from the RRBS-CL judgement.
  - 48 SPOT-MAS stage-stratum results (the breast and all-cancer rows) are `disputed`.
  - The other 302 results are `source_checked`.
- Three locators were wrong and are corrected. Dataset count notes and judgement limitations were corrected or extended. No value changed.
- All seven relevance judgements hold as `proxy` and are set to `source_checked`, with `reviewed_evaluations` filled. Their pins are left for the integrator.
- In a simulation, I added the reviewed batch and the proposed `assessed_by` links to an in-memory copy of the store and computed the pins. All seven judgements derive as active, and the existing cfMethyl-Seq judgement stays active. With the two source-level concerns in place, none of the new judgements could have been shown.

## How the check was done

1. Downloaded each `artifact_url` into an empty directory and hashed it. bioRxiv returned HTTP 429 at first; the files were fetched on later retries.
2. Read each workbook with a stdlib OOXML reader written for this review. It reads shared strings, the raw `<v>` text, and the number format from `styles.xml`. The extractor's `extract/*.py` was not imported or run.
3. Built the expected identity of every cell from the table headers: tool or classifier, dataset or cohort, depth, stratum, cancer type and n column. Then matched every result to its cell through `source_locator` and compared:
   - `raw_xml_value` to the raw cell text;
   - `printed_value` to the displayed text: the fixed-decimals rendering where the cell format is `0.0000` or `0.00_ `, otherwise the shortest round-trip decimal;
   - `numeric_value`, metric, qualifier, unit and direction;
   - for Sun et al., `denominator_note` against the cohort sizes in Methods;
   - for Nguyen et al., `coverage.scored` against the n column of the same stratum;
   - the configuration and protocol of the linked evaluation.
4. Compared all 140 sheet A values of Giuili et al. Supplementary Table 3 with Figure 4A, which I read from the text layer of the preprint PDF (`pdftotext -layout`). For SPOT-MAS, compared the stage-stratum sizes in Table S9 with Table S8, Table S2, article Table 1, and a count of the per-patient rows in Table S1.
5. Read the cited Methods and Results paragraphs of all three articles to check definitions, cohort sizes, model names and locators. Paragraph numbers here count body paragraphs and exclude figure and table captions, which is the scheme the extractor used.
6. Loaded the reviewed batch with `recordSchema`, `validateVocabularies`, `validateAttributes` and `validateRecords` against the current store, in memory. Then ran `deriveUseCaseInputs` with the proposed links and computed pins. Nothing was written to the store.

## Sources and hashes

| Source | Pinned SHA-256 | Re-download |
| --- | --- | --- |
| `ctdnameth-20261009-source-sun2024` (PMC11660681 XML) | `ce2ac867...6714e8` | Match |
| `ctdnameth-20261009-source-sun2024-additional-file-1` | `1489ec85...31b0` | Match |
| `ctdnameth-20261009-source-giuili2025` (v1 PDF) | `1893cc99...adc7` | Not reproducible: the new copy is `fa7bcf8c25532f86dc99ed7d76a13a49ae70e29ab9f46559b3e0972e86aa9b96`, same length (7,728,127 bytes) |
| `ctdnameth-20261009-source-giuili2025-supp-table-1` | `779ef36e...8e34` | Match |
| `ctdnameth-20261009-source-giuili2025-supp-table-3` | `c585f11e...ed32` | Match |
| `ctdnameth-20261009-source-nguyen2023` (PMC10567114 XML) | `e09cfb58...cfa8` | Match; archive decompresses to it |
| `ctdnameth-20261009-source-nguyen2023-supp-file-1` | `4797d7ea...7331` | Match; archive decompresses to it |

The preprint PDF carries `ModDate` and two XMP dates set to the download time (13:21:07 -07:00 for my copy). Resetting those three stamps to any second of the retrieval day does not give the pinned hash, so at least one other per-download field also differs. The PDF supports only definitions, counts and the Figure 4A comparison. I recorded this in the source's `hash_scope` and kept it `source_checked`. A future pass could pin the text layer instead of the bytes.

I also read Supplementary Table 2 (media-4.xlsx, `7057389b1ca89f5cd59b4004b7c8b00578988311b02bc5c9c5b7993915b4c06c`) to check the tested grid quoted in the LoD definition claim. It is not a source record of the batch.

## Values checked

| Table | Cells | Matched | Wrong | Disputed after review |
| --- | --- | --- | --- | --- |
| Sun et al. Table S7, AUC block I4:M9 | 30 | 30 | 0 | 0 |
| Giuili et al. Supplementary Table 3, sheet A B3:O12 | 140 | 140 | 0 | 25 |
| Giuili et al. Supplementary Table 3, sheet B B3:D12 | 30 | 30 | 0 | 5 |
| Nguyen et al. Table S9, accuracy cells (with 60 n cells as `coverage.scored`) | 180 | 180 | 0 | 48 |
| Total | 380 | 380 | 0 | 78 |

Display precision follows the workbook formats:
- Giuili cells use `0.0000`, so for example `0.0250` is printed for a stored `2.5000000000000001E-2`.
- Sun cell I7 uses `0.00_ ` and prints `0.80`.
- All other Sun and Nguyen cells are General and print as the shortest round-trip decimal, for example `0.820513`.
- The five Giuili text cells keep their asterisk (`0.0070*`), and their `scope_note` explains it.
- The three validation lung stage I cells are `N/A` with n = 0 and `numeric_value` null.

The article text checks agree with the tables:
- Sun cohorts (24 and 32; 225 cancers, with 67, 41, 30, 54 and 33 by type, and 193 healthy) match Methods P30.
- The CelFiE limits quoted in the Giuili Results (0.7% at 10M on RRBS-TT, 0.7% at 310M on WGBS-TT, 0.1% at 2M on RRBS-CL, and Houseman 0.7% at 310M) match D3, I3, K3, I5 and I6.
- The SPOT-MAS GCNN accuracies in Results P25 (0.87, 0.82, 0.54; and 0.78, 0.76, 0.66, 0.63, 0.55) match Table S9.

One small text-table difference in Nguyen et al.: P25 gives the GCNN validation median as 0.70, while Table S9 prints 0.69 for all cancers. The median of the five per-cancer values is 0.66. Results use Table S9.

## The two evidence concerns

### DecoNFlow RRBS-CL block

The collector is right that five rows conflict, and the conflict has a clear shape. In the RRBS-CL columns (K to O), the sheet A rows for UXM, MetDecode, meth_atlas, PRMeth and CIBERSORT are a cyclic shift of the Figure 4A rows:

- sheet A UXM equals Figure 4A MetDecode;
- sheet A MetDecode equals Figure 4A meth_atlas;
- sheet A meth_atlas equals Figure 4A PRMeth;
- sheet A PRMeth equals Figure 4A CIBERSORT;
- sheet A CIBERSORT equals Figure 4A UXM.

Sheet B's overall RRBS-CL medians follow Figure 4A (UXM 0.025, MetDecode 0.003, meth_atlas 0.003, PRMeth 0.25, CIBERSORT 0.1). The Results sentence that "MetDecode reaches it at 20M" follows sheet A. Every other cell agrees with Figure 4A:
- all 40 WGBS-TT values;
- all 50 RRBS-TT values;
- the RRBS-CL values of CelFiE, both Houseman variants, EpiSCORE and EpiDISH.

Decision: withhold only the affected cells. The 30 RRBS-CL results of the five tools (five depths plus the overall median each) are `disputed`, with the detail in `source_warnings`. Their five evaluations are listed in the RRBS-CL judgement's `excluded_evaluations` with a reason. I removed the source-level `evidence_concerns` entry and recorded the same facts in the source's `limitations`. A source-level concern would have withheld all three DecoNFlow judgements, including 140 values that agree with the figure.

### SPOT-MAS stage strata

The collector is right that Table S9's stage sizes differ from Table S8 and Table 1. Counting the per-patient rows of Table S1 locates the difference. Only the breast rows differ:

| | Table S9 (I, II, III, unknown) | Tables S1, S2, S8 (I, II, III, unknown) |
| --- | --- | --- |
| Discovery breast | 29, 78, 25, 24 | 31, 84, 27, 14 |
| Validation breast | 13, 20, 5, 29 | 14, 31, 8, 14 |

The colorectal, gastric, liver and lung stage strata, and every all-stage n, agree across all four tables. The all-cancer stage strata differ only by the breast difference. The Table S9 values are internally consistent with Table S9's own n; for example, the discovery stage II RF value 0.820513 is 64/78. So the values reflect a stage grouping that is not the published one.

Decision: withhold only the affected cells. The 48 breast and all-cancer stage-stratum results (4 strata, 2 rows, 3 models, 2 cohorts) are `disputed`. All-stage values and the other cancers' stage strata stay `source_checked`. As with DecoNFlow, I moved the source-level concern into `limitations`.

## Other points the collector asked about

- **EpiDISH_CP_eq, EpiDISH_CP_ineq and EpiDISH_RPC versus Houseman_eq, Houseman_ineq and EpiDISH.** Confirmed. Supplementary Table 1A lists Houseman's CP with equality and with inequality constraint, and EpiDISH RPC, all in EpiDISH v2.16.0. More decisively, all 14 depth values of each row equal the Figure 4A row of the same name, and the eq and ineq rows can be told apart (WGBS-TT 62M: 0.0375 and 0.0500). The `model_identity_note` fields are accurate.
- **DNN versus CNN.** Confirmed. Table S9 and Methods P50 say DNN (H2O multi-layer feedforward network, version 3.36.1.2). Results P23 and the Figure 8 figure supplement 1 caption say convolutional neural network. Keeping `DNN` with the note is correct.
- **3,690 versus 3,630 mixtures.** The conflict is wider than recorded:
  - The abstract and Methods state 3,690.
  - The Results dataset counts (1,640, 1,550, 440) sum to 3,630.
  - The Methods arithmetic gives 1,600, 1,500 and 500 tumour mixtures plus 40, 50 and 50 healthy replicates, which is 3,740.
  - The RRBS-CL design as described (five depths, ten fractions plus 0%, ten replicates) gives 550, not 440.

  I rewrote the three dataset `scope_note` fields and the RRBS-CL `split` to say this. No count is used in any value.
- **Per-cancer rows stored as recall, "printed as accuracy".** Correct. A per-cancer row is the share of that cancer's patients assigned to the right type, which is per-class recall. The all-cancer row is overall accuracy: the n-weighted mean of the per-cancer RF values in discovery is 0.491, against 0.49 printed.
- **Display precision.** Correct throughout (see Values checked).
- **Link the cfMethyl-Seq cohort to `amp-data-cfmethyl-408`?** No, and keeping the relation in `scope_note` is right. Both use the Stackpole et al. EGA study, but they are not the same data:
  - Sun et al. use EGAD00001009003 with 225 cancers and 193 controls, aligned to hg38.
  - `amp-data-cfmethyl-408` is the 408 QC-passing samples (217 and 191), aligned to hg19.
  - `same_data_as` is defined for dataset subsets with identical data and is not appropriate here.
- **Sun et al. independence.** Not contradicted. The eleven authors do not include the developers I could identify for the five tools (CelFiE: Caggiano and Zaitlen; UXM and MethAtlas: Loyfer, Moss, Dor and Kaplan; CelFEER: Keukeleire; cfNOMe: Erger). I did not check each tool paper's full author list.
- **Nguyen et al. conflicts of interest.** Most authors are affiliated with Gene Solutions. Five hold equity, and four of them are inventors on patent application USPTO 17930705.

## Corrections made in the batch

| Record | Field | Change |
| --- | --- | --- |
| Both Sun protocols | `version`, `source_locator` | P41 to P49. P41 is the sequencing-depth filter paragraph; P49 defines the random forest ROC-AUC. P30 (cohorts) was added. |
| `ctdnameth-20261009-claim-sun2024-auc-definition` | `source_locator` | P41 to P49 |
| `ctdnameth-20261009-claim-nguyen2023-too-features` | `source_locator` | Results P9 to Results P18, Methods P47 and P49, where the nine feature sets are named |
| Two Sun judgements | `citation_locators`, `source_locator` | Methods P30, P41 to P30, P49 |
| Two Nguyen judgements | `citation_locators` | Discussion P29 added (tissue-of-origin discussion) |
| Three DecoNFlow datasets | `scope_note`; RRBS-CL `split` | Full count conflict stated |
| `ctdnameth-20261009-source-giuili2025` | `hash_scope` | Per-download PDF stamp recorded |
| Two table sources | `evidence_concerns` moved to `limitations` | The affected results carry `source_warnings` and are `disputed` |
| Five RRBS-CL evaluations, two SPOT-MAS protocols | `limitations` | Reworded to the narrowed conflict |
| SPOT-MAS validation protocol | `limitations` | GCNN transductive training added (see below) |
| `claims.csv` | two `locator` cells | Synchronised with the corrected claim locators |

The descriptive claims are correct as worded:
- The LoD definition claim matches the Results and Methods text, and its tested grid matches Supplementary Table 2D.
- The SPOT-MAS feature claim names the nine feature groups of Methods P47.
- The Sun AUC claim matches P49.

## New metric concept `limit-of-detection`

Accepted. The definition ("lowest analyte level ... still distinguished from blank samples under a stated test") is the usual analytical meaning. It fits the DecoNFlow rule: the last tumour fraction whose ten replicates are significantly above the 0% replicates under a one-tailed Mann-Whitney U test with BH-adjusted p < 0.01. The scope note correctly says that values from different grids or rules are not comparable. The direction is `lower`, which is right: a lower detectable fraction is better. No external match is asserted, which is acceptable.

## Relevance judgements

All seven are `proxy`, and I agree with each grade. The use case asks for detection of tumour-derived plasma DNA, with sensitivity at a stated specificity, and for tissue of origin where separately supported. None of these protocols measures sensitivity at a declared specificity on an intended-use population.

| Judgement | Endpoint fit | Changes made | Reviewed evaluations |
| --- | --- | --- | --- |
| `...-sun2024-hcc-wgbs` | Detection on real plasma, but as a discrimination AUC of a downstream random forest | Locator; added that the forest uses all 35 cell-type fractions, so detection can rest on non-tumour tissue signals | 5 |
| `...-sun2024-cfmethyl` | As above, five cancer types against one control group | As above | 5 |
| `...-giuili2025-wgbs-tt` | Analytical sensitivity on in silico mixtures, not patients | Concern line reworded (this block is clean); added that medians pool tumour types and DMR tools, and that the two reference-free tools are not in the table | 10 |
| `...-giuili2025-rrbs-tt` | As above | As above | 10 |
| `...-giuili2025-rrbs-cl` | As above, one neuroblastoma cell line | Five evaluations excluded with reasons; endpoint now says five of ten tools; cell-line limitation added | 5 |
| `...-nguyen2023-too-discovery` | Tissue of origin from plasma, multimodal features, cancer patients only, 10-fold CV | Concern line reworded; per-class recall note added | 3 |
| `...-nguyen2023-too-validation` | As above, independent cohort | As above, plus: the GCNN was trained transductively on a graph that includes the validation samples as nodes (Methods P51) | 3 |

- **Random forest design (Sun et al.).** The validation split is not stated anywhere I could find in the article, which is already recorded. The added limitation covers the other weakness: the classifier sees every cell-type fraction, not only the affected tissue.
- **Grouping.** Three comparisons with strata, ordered sensibly. The headline metrics (`auroc`, `limit-of-detection`, `accuracy`) exist among each comparison's results. For SPOT-MAS, `accuracy` selects the all-cancer rows, which is the right headline.

## Use-case changes (coverage.json)

The proposed `assessed_by` links and the two clean Sun sources are fine. Before the SPOT-MAS judgements are published, the integrator must also change the use case. Each of these changes alters a pinned field of the existing judgement `use-case-mapping-amp-20261007-issue16`, which will then be withheld until it is re-reviewed and re-pinned. The release guard will flag it.

- `exclusions` still lists "Tissue-of-origin identification (not ingested in this bounded intake)", and `output` says no tissue-of-origin claim is ingested. Both contradict the two SPOT-MAS judgements. Replace them with the proposed exclusions.
- `decision`, `output` and `setting` describe only the single cfMethyl-Seq result. The proposal does not touch them, but they now need wording that covers several methods and the proxy endpoints.
- Two of the proposed `evidence_gaps` refer to "evidence concern". Reword them to: "One block of Giuili et al. Supplementary Table 3 (RRBS-CL, five tools) conflicts with Figure 4A; those values are not shown" and "Nguyen et al. Table S9 breast stage strata disagree with the per-patient table; those values are not shown". Add the GCNN transductive training.

## Approved use-case changes

This is the exact text to apply to `use-case-plasma-ctdna-methylation`. Fields not listed here stay unchanged: `name`, `description`, `question`, `facets`, `inputs`, `intended_users`, `search_terms`, `collection_plan` and `planned_work`.

### `exclusions`

Replace the whole list with:

```json
[
  "Prospective screening validation",
  "Tissue-of-origin identification by methylation alone: the only tissue-of-origin comparison ingested (Nguyen et al. 2023) uses combined methylation, fragment-length, copy-number and end-motif features and classifies cancer patients only"
]
```

This removes "Tissue-of-origin identification (not ingested in this bounded intake)", which the two SPOT-MAS judgements contradict.

### `output`

```json
"A sourced all-stage cancer-detection sensitivity at a declared specificity where one is reported, otherwise the reported proxy endpoint (detection ROC-AUC on patient plasma, tumour-fraction limit of detection in in silico mixtures, or tissue-of-origin accuracy among cancer patients), each with the method, cohort and validation design it comes from."
```

### `decision`

```json
"Inspect the cfMethyl-Seq repeated-split sensitivity/specificity evidence, and the proxy comparisons of deconvolution methods and tissue-of-origin classifiers, before selecting a workflow and validation design for the intended cancer-detection population."
```

### `setting`

The first sentence is unchanged; one sentence is added:

```json
"cfMethyl-Seq achieves 80.7% all-stage cancer-detection sensitivity (95% CI 68.6-90.7) at 97.9% specificity, under a repeated random 25% test split (cohort 217 cancers/191 non-cancers, test n=102). The other evidence is an independent benchmark of five deconvolution methods on two plasma cohorts, a preprint benchmark of ten deconvolution tools on in silico mixtures, and one author-reported tissue-of-origin comparison on cancer patients recruited in Vietnam."
```

### `clinical_scope`

This field also has to change. It currently says "this is a repeated random test-split evaluation on one assembled cohort", which no longer describes the evidence.

```json
"Clinical applicability is not established as prospective screening performance. The cfMethyl-Seq figure comes from a repeated random test split on one assembled cohort; the other comparisons are proxies (a random forest AUC with no stated validation split, in silico mixtures, and tissue of origin among cancer patients only), and none is an independent prospective validation."
```

### `evidence_gaps`

Keep the two existing entries and append these seven:

```json
[
  "No result is comparable across sources: cohorts, inputs, metrics and validation designs differ.",
  "No sensitivity at a declared specificity for several methods on the same plasma samples was found in a retrievable source; Jamshidi et al. 2022 (Cancer Cell, 10.1016/j.ccell.2022.10.022) could not be retrieved.",
  "Sun et al. 2024 does not state the random forest validation split for its AUCs.",
  "Giuili et al. 2025 is a preprint on in silico mixtures; in its Supplementary Table 3 the RRBS-CL values of five tools (UXM, MetDecode, meth_atlas, PRMeth and CIBERSORT) conflict with Figure 4A, and those values are not shown.",
  "Nguyen et al. 2023 is author-reported by the assay developer; its Table S9 breast stage strata disagree with the per-patient table and are not shown, and its graph network was trained with the validation samples in its graph.",
  "No independent methylation-only tissue-of-origin comparison on patient plasma with printed per-method values was found.",
  "No assay-level comparison (cfMeDIP-seq, WGBS, EM-seq or targeted bisulfite) with a detection endpoint on the same plasma samples was found."
]
```

### `links`

Add `assessed_by` links to these seven protocols, keeping the existing link to `amp-protocol-cfmethyl-randomsplit-detection`:

- `ctdnameth-20261009-protocol-giuili2025-rrbs-cl-tumour-fraction-lod`
- `ctdnameth-20261009-protocol-giuili2025-rrbs-tt-tumour-fraction-lod`
- `ctdnameth-20261009-protocol-giuili2025-wgbs-tt-tumour-fraction-lod`
- `ctdnameth-20261009-protocol-nguyen2023-spotmas-too-discovery-cv`
- `ctdnameth-20261009-protocol-nguyen2023-spotmas-too-validation`
- `ctdnameth-20261009-protocol-sun2024-cfmethyl-detection-auc`
- `ctdnameth-20261009-protocol-sun2024-hcc-wgbs-detection-auc`

### `source_ids` and `citation_locators`

Add the two Sun et al. sources to `source_ids`, and add these entries to `citation_locators`:

```json
[
  {"source_id": "ctdnameth-20261009-source-sun2024", "locator": "Methods P30 (cohorts) and P49 (detection ROC-AUC); Results P20 and P21"},
  {"source_id": "ctdnameth-20261009-source-sun2024-additional-file-1", "locator": "Table S7, AUC block H2:M9"}
]
```

Do not add the Giuili et al. or Nguyen et al. sources to the use case. Each judgement already cites its own sources. A use-case source that later gains a concern withholds every positive judgement on the use case, so the use case should cite only what its own text needs. The new sentence in `setting` describes those two papers only in general terms, and their judgements carry the citations.

### Existing judgement `use-case-mapping-amp-20261007-issue16`

It still holds under the new text, and nothing on it needs to change:
- Its endpoint (all-stage sensitivity at a declared specificity on a repeated random 25% test split) is the first branch of the new `output`.
- `direct` remains justified: the measured quantity is the use case's declared endpoint, and `inputs` still asks for a target specificity constraint.
- The new `decision` still names this evidence first. The new `setting` keeps its figures word for word. The new `clinical_scope` keeps its caveat.
- No new exclusion touches it.
- Its limitations (no foundation-model comparison, no prospective screening benefit, no independent reproduction) remain accurate.

Its pins cover `decision`, `output`, `setting`, `exclusions` and `clinical_scope`, so applying this text will withhold it until it is re-pinned. Re-pin it, with the seven new judgements and the summary claim, against this review.

## Corrected summary

The collector's proposal is mostly right. It needs four changes:
- It cites CIBERSORT's RRBS-CL value, which is now disputed.
- It does not name the SPOT-MAS developer affiliation.
- It does not mention the transductive GCNN.
- It does not say that only reference-based tools are in the DecoNFlow table.

Proposed text:

> Three bounded sources compare cfDNA methylation methods. None is a prospective screening study and none measures clinical benefit. Sun et al. 2024 (Genome Biology), an independent benchmark whose authors did not develop the tools, deconvolved real plasma with five methods and reported the ROC-AUC of a random forest trained on the estimated cell-type fractions; the paper does not state how the random forest was validated, so the AUCs may be in-sample. For 24 liver cancer patients and 32 healthy individuals (WGBS), AUCs were 0.96 (CelFEER), 0.93 (CelFiE), 0.91 (MethAtlas), 0.77 (cfNOMe) and 0.72 (UXM). On cfMethyl-Seq plasma (30 to 67 patients per cancer type, each against the same 193 healthy individuals), AUCs ranged from 0.72 (UXM, lung squamous cell carcinoma) to 0.93 (CelFiE, gastric cancer), and no method was highest for every cancer type. Giuili et al. 2025, a bioRxiv preprint not yet peer reviewed, ran ten reference-based tools inside the authors' DecoNFlow pipeline on in silico mixtures of tumour tissue or cell-line reads in healthy plasma reads. CelFiE had the lowest overall median tumour-fraction limit of detection in each dataset: 0.0070 (WGBS-TT), 0.0100 (RRBS-TT) and 0.0010 (RRBS-CL). CIBERSORT and EpiDISH had overall medians of 0.1000 to 0.2500 on WGBS-TT and RRBS-TT. For five tools the RRBS-CL values disagree between the supplementary table and Figure 4A and are not shown. Nguyen et al. 2023 (eLife), by the developers of the SPOT-MAS assay at Gene Solutions, compared three tissue-of-origin classifiers on combined methylation, fragment-length, copy-number and end-motif features from cancer patients only. In the validation cohort of 239 patients, overall accuracy was 0.53 (random forest), 0.69 (deep neural network) and 0.69 (graph convolutional network); the graph network was trained with the validation samples in its graph. Tissue-of-origin evidence here comes from one author-reported multimodal workflow, not from a methylation-only comparison.

Every number above is a `source_checked` result in this batch:
- Sun Table S7 I4:M4, M8 and J9;
- Giuili sheet B, B4:D4 for CelFiE, and B3:C3 and B7:C7 for CIBERSORT and EpiDISH_RPC;
- Nguyen Table S9 C19:E19.

The case counts come from Sun Methods P30 and Nguyen Table S9 B19.

## Checks run

- In-memory: the reviewed batch passes `recordSchema`, the vocabulary check (including `limit-of-detection`), the attribute check and `validateRecords` against the current store.
- `npm run typecheck`: exit 0.
- `npm run records -- check`: 29,444 records match their provenance (the batch is not in the store).
- `npm test`: 498 of 499. The failure is `tests/omics-data.test.ts` "documents an explicit scope decision": it expects 106 scope-audit entries and finds 113. The seven extra entries are this pass's new `data/omics/scope-audit.jsonl` lines, not a review change. The test's count needs updating when the batch is integrated.
- `npm run build` was not run. The batch is not in the store, so the build would not include it, and the build writes release files outside this review's scope.

## Remaining gaps

- The two conflicts are unresolved at the source. Both are worth reporting to the authors.
- The preprint PDF cannot be pinned by byte hash.
- Not covered, as the collector recorded: Jamshidi et al. 2022 and other CCGA papers, assay-level comparisons with a detection endpoint, prospective studies, and figure-only results.
- `research.md` says sheet A has 150 values; it has 140 (10 tools by 14 depths). `sources.md` still describes the two concerns as source-level. These are the collector's notes and were left unchanged.
