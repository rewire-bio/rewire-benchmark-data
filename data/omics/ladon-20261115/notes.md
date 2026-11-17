# Ladon (Blank Bio), issue #247

Ladon is a bulk RNA-seq foundation model released by Blank Bio on 12 November 2026 with a 47-page
technical report. This batch registers the model at family level, its nine adaptation
configurations, its comparators, cohorts and protocols, ClinBench as a discovered benchmark, and
the values the report prints in its figures. Lane: `rna`. Search cutoff 2026-11-15.

Extraction only, by a Claude extraction agent. A different agent reviews it. Nothing is marked
reproduced and no review sign-off is claimed; every evaluation is developer-reported
(`author_reported`, `retrospective: true`).

Frozen extraction hash (`sha256sum data/omics/ladon-20261115/batch.jsonl`, same as `shasum -a 256`):
`faa416c7837bbc20b7b5520c5b2b18dd6baa41bdbcb6e4765104969342f1ec7c`

## Sources

| ID suffix | Artifact | SHA-256 |
| --- | --- | --- |
| `source-zenodo-pdf` | Zenodo record 24157116, the PDF. Primary source for every value | `64edf7c3c956c50a65aa01a0dcaa13f0cfef28ab4373ecfd50c431e67143893c` |
| `source-web-report` | blank.bio/ladon-technical-report (HTML) | `f60c00508f8672048047477beb23b1e2ea9244abb099e863f68f3554ce05c97f` |
| `source-blog` | blank.bio/introducing-ladon (HTML) | `53e62f1d679bc8f0063d49d6fd688e7fe7e0a520a4c34ac6c466810185ce0dfc` |
| `source-web-fig06` | Figure 6 page of the web report (HTML) | `afa0d46855e1c3b15efa9a6cca8c621d4314ad445dd7777216e62c7ac646629f` |

Why the Zenodo PDF is primary: it is the only hashable, versioned artifact. Two downloads were
byte-identical, its MD5 matches Zenodo's checksum, and it carries the version DOI. The web report
is mutable (Last-Modified 15 November 07:37 UTC, three days after the PDF), though its prose holds
no number that the PDF lacks. The three HTML sources were each fetched twice with identical bytes.

Licence: the Zenodo record's Rights field reads "Copyright (C) 2026 Blank Bio. All rights
reserved." Zenodo's `access_right: open` describes the file download only. Because of that
licence, neither the PDF nor its text layer is archived here. To recheck, regenerate the text
layer with `pdftotext -layout` (poppler 26.08.0 gave SHA-256
`2f5a65a1e6b9830dd2aa1e0155865462c34a58451a230657f697d110b637bd6d`).

## Access, checked 2026-11-15, not taken from the issue

- No weights, code repository or model licence is linked from the report, Zenodo or the
  announcement.
- GitHub organisation `blankbio` exists with 0 public repositories; `blank-bio` is 404.
- Hugging Face `BlankBio` lists 0 models; a model search for "ladon" finds nothing related.
- The report's last paragraph and the announcement ask readers to contact Blank Bio. The
  announcement offers to pay for RNA sequencing of a requester's cohort.

Recorded on the model, every Ladon configuration and a claim: access unresolved, contact the
provider. No open licence is inferred.

## Decisions taken from the source text

**What is a "table".** The report has no tables. All values are labels printed inside figures,
captions or nearby prose, present in the PDF text layer. These are extracted (the BenchBench
batch's precedent for printed figure digits). Anything only drawn (dots, bars, curves) or shown
only on hover in the web version is not.

**Checkpoint identity.** No checkpoint, version or per-experiment model size is named. Ladon is a
`family`-level model. Each experiment uses a different encoder state, so each gets its own
configuration, versioned by the Methods text:

| Configuration | Encoder state | Head | Figures |
| --- | --- | --- | --- |
| `ladon-transfer-cox` | survival mid-trained; TCGA/CPTAC labels excluded | ridge Cox fitted on source cohort | 2 |
| `ladon-clinical-transfer-cox` | same, concatenated with BMRetriever-7B | one ridge Cox | 2 |
| `ladon-trial-survival-cox` | survival-supervised | ridge Cox, lambda 0.3, TCGA + other trials | 3 |
| `ladon-clinical-trial-survival` | same | sum of standardised Ladon and clinical scores | 3, 4 |
| `ladon-pooled-cox-plus-trials` | "fixed trained encoder", state not stated | ridge Cox, TCGA + non-trial cohorts + trials | 5 |
| `ladon-response-tabicl` | mid-trained with academic response labels | PCA 128 + TabICL v2 | 6 |
| `ladon-isoform-imputation` | pretrained; TCGA excluded, ENCODE4 and blood references included | model's own imputation | 11 to 14 |
| `ladon-deconvolution-pbmc` | composition post-trained | PCA 64 + TabICL regressors | 17 |
| `ladon-composition-pcr` | composition post-trained | 12-class composition + L2 logistic, fitted on TransNEO | 18 |

Figure 4 (OAK, C-index 0.61) is assigned to the Figure 3 combined configuration. The caption says
"Ladon combined with clinical covariates ... fitting the risk predictor on other cohorts" but does
not say it is the same predictor; the result carries that caveat.

**ClinBench.** The report defines it with its own protocol (142 tasks: 85 within-cohort with
3-fold CV repeated five times, 57 cross-cohort survival; Harrell's C or AUROC; unweighted mean)
but publishes no task list and prints no score: Figures 20 and 21 are PNG images. It is recorded
as a `discovered` benchmark with claims and no results. The 142 tasks are not 142 trials.

**Response, benefit and prognosis are separate tasks** (`task-survival-prognosis`,
`task-immunotherapy-response`, `task-treatment-benefit`, `task-isoform-recovery`,
`task-cell-composition`, `task-pcr-prediction`). Prognosis has seven protocols (three transfer
panels, OS and PFS hazard ratios, OAK C-index, the training-pool C-index). Response is one
protocol over six trials. Benefit has no protocol and no results: its printed numbers (Figure 8
gaps, 28%/6%, 14%/13%) have no metric concept (a difference in Kaplan-Meier proportions), come
from one retrospective trial with no interval or interaction test, and one comparator panel does
not name its selection. They are claims on the benefit task.

**Baselines and reference-data parity.** For response, Ladon's in-context examples are 1,419
patients from 33 academic cohorts plus the other trials, and its encoder was mid-trained with
academic response labels. The gene TPM baseline uses academic cohorts alone (page 16; the web
figure labels it "Gene TPM · academic only"). This asymmetry is on the protocol, the gene TPM
evaluation and a claim. The report does not state the context used by the BulkRNABert,
BulkFormer and BMRetriever rows beyond "the same PCA and TabICL procedure as Ladon", nor the
context of the DGE signature; recorded as unresolved, not inferred.

**Held-out protection, as stated.** TCGA and CPTAC outcome labels are excluded from encoder
supervision (transfer). Each trial is excluded from fitting its own predictor or context (held-out
trials, response, Figure 5). Isoform pretraining excluded TCGA but included the ENCODE4 and blood
bulk reference libraries, so Figures 13 and 14 score against data seen in pretraining. The single-cell
study paired with the PBMC test bulks was held out of post-training; whether the 35 PBMC bulks
were in bulk pretraining is not stated.

**Multiple testing.** Stars are one-sided paired Wilcoxon tests over six or fewer units,
unadjusted; exact p-values are hover-only. No star is stored. The announcement's "significantly
outperforms all baselines" is recorded as a claim next to the report's test description.

**Metrics.** Uno's and Harrell's C use `concordance-index` with a qualifier. Figure 17's pairwise
ordering accuracy (pairs with distinct measured shares in the right order, ties as half) is a
concordance index by the vocabulary's own definition. Figure 14's direction accuracy uses
`accuracy`, unit `percent`. Figure 11 MAE uses `mean-absolute-error`, unit `percent`, unit_detail
percentage points. Figure 3 needs a hazard-ratio concept: `vocab-proposal.ttl` proposes
`:hazard-ratio` (STATO_0000677 exact, NCIT_C93150 close), used by 14 results.

## Extracted as results (101)

| Figure | Cells | Protocols |
| --- | --- | --- |
| 2, TCGA/CPTAC survival transfer | 8 rows x 3 panels = 24 | transfer TCGA to CPTAC, CPTAC to TCGA, pan-cancer |
| 3, held-out trials risk split | 7 rows x OS/PFS = 14 | OS and PFS hazard ratio (geometric mean) |
| 4, OAK caption | 1 | OAK OS Uno C |
| 5, legend | 3 (largest training pool only) | size-weighted OS Uno C |
| 6, response | 10 | response AUROC |
| 11, INSR readout | 2 r with CI, 3 MAE | INSR r, INSR MAE |
| 12a | 4 medians | 3,000-gene median r |
| 13 | 4 | ENCODE4 organ-pair r |
| 14 (page 27 prose) | 2 methods x 2 contrasts = 4 | direction accuracy, two contrasts |
| 17 bottom | 6 methods x 2 = 12 | PBMC mean r, pairwise ordering |
| 17 top | 5 lineages x Ladon/CIBERSORT = 10 | PBMC per-lineage r |
| 18 | 10 AUCs with CI | pCR ER+/HER2-, pCR HER2+ |

## How the values were checked

1. `extract/parse_figures.py` reads the text layer page by page (split on the running footer),
   asserts every row label in printed order, and for Figure 2, whose rows span several lines,
   assigns each value to its panel by character offset. Output: `extract/figures.json`.
2. `extract/check_against_web.py` reads the numbers embedded in six web figure pages by regular
   expression (the JavaScript is not executed), checks each page's hash, rounds to the printed
   precision and compares: 93 values, 0 differ. One value agrees only under binary float
   rounding (Figure 18 DFCI IBC, embedded 0.735: the figure prints 0.73, the prose 0.74).
   Output: `extract/web-check.txt`. This confirms Figure 2 column assignment and that the Figure 5
   legend is the size-weighted value of the third training stage.
3. `extract/check_locators.py`: every printed value (and printed interval) occurs on the page its
   locator names. 101 of 101. Output: `extract/locator-check.txt`.
4. `npm run -s batch -- check-values`: 101 `locator_not_parsed`, because it parses only
   `Table N` locators. `value-check.tsv` is kept.
5. `extract/validate_batch.ts` (the repository's attribute, description and relation validators,
   run without adding the batch): 317 records, no problems. Every concept key except
   `hazard-ratio` exists in `data/vocab/`.

`extract/build_batch.py` writes `batch.jsonl` from `figures.json` and the decisions above.

## Not extracted (gaps)

- Per-trial, per-cancer and per-gene values, exact p-values and Figure 17 intervals: present in
  the web figures' embedded data or collapsed "Show the data" tables, not printed in the PDF.
- Figure 5 first two training stages: drawn but not printed.
- Figures 7, 8 and 9 (benefit): claims only, see above. Figure 9 prints no rates.
- Figure 12a "Ladon higher in" shares (95.1%, 99.7%, 99.7%): pairwise comparisons, kept as claims.
- Figure 12b, Figure 15, 16 and 19: no printed values (12b) or schematic/UMAP.
- Figure 14 all-gene values (56% against 53%): the contrast is not named; claim.
- Figure 17 middle (one sample's composition) and Figure 13 TBC1D4 example: single-sample
  illustrations, not extracted.
- Figures 20 and 21 (scaling, ClinBench): images, no values.
- Trial data provenance and access: not stated in the report.

## Questions for the reviewer

1. Hover-only per-trial values from the official web figures: may they be stored, and from which
   artifact? Default here is no.
2. Fig 8 comparator panel prints -2.0 / -2.6 pp for an unnamed default selection (probably PD-L1
   mRNA, the first toggle). Leave as an unassigned claim, or assign?
3. Benefit numbers as claims rather than results: agree, or add a risk-difference metric concept?
4. `:hazard-ratio` proposal: definition and default direction `unknown` acceptable?
5. Figure 4 assigned to the Figure 3 combined configuration on a reading of the caption.
6. Existing `ctdnameth-20261009-method-cibersort` is the EpiDISH implementation; Blank Bio
   reimplemented CIBERSORT, so a new method was created. Agree?
7. Fig 2 `‡` on DGE and Hallmark GSEA is unexplained in the PDF; recorded as a claim.
8. Fig 7 prose (304 to 24) and figure (106 to 0 for an unnamed trial; toggle omits IMmotion150;
   caption "550 total") disagree in scope; recorded as one claim, no evidence concern added.
9. Should the response protocol, whose comparators do not share Ladon's labelled context, carry an
   evidence concern so it is withheld from automatic comparison? Not added by the extractor.
