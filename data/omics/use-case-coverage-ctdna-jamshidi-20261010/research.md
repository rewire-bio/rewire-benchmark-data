# Research: CCGA substudy 1 follow-up pass, 2026-10-10

Task: extract Jamshidi et al. 2022 (Cancer Cell, 10.1016/j.ccell.2022.10.022), which the 2026-10-09 methylation pass logged as a gap because the publisher returned 403. Use cases: `use-case-plasma-ctdna-methylation` and `use-case-plasma-ctdna-fragmentomics`. Both already have reviewed judgements and summaries; their settings and exclusions were read first and are not edited.

Bounds: one named source; 4 queries (ledger `search-use-case-ctdna-jamshidi-q1` to `q4`); lean batch (79 records). Worker: Claude (Opus 5.5) research agent; no human review claimed.

## Retrieval

The paper is not in PMC, Europe PMC holds neither full text nor supplementary files, and no preprint exists. cell.com and ScienceDirect returned 403 and the Elsevier API returned 429. OpenAlex and Unpaywall both list a deposit by the Francis Crick Institute on figshare (10.25418/crick.21731870.v1). Its one file is the publisher PDF of the version of record (Elsevier file name and metadata, CC BY-NC-ND notice), and its MD5 matches. Every value comes from that PDF; no secondary summary was used. The publisher's supplement (mmc1) was also retrievable and was read, but not extracted.

## What the paper compares

CCGA (NCT02889978) substudy 1 ran three prototype assays on contemporaneous blood draws from the same participants, randomised to a training set (1,414 analysable) and an independent validation set (847 analysable):

- whole-genome bisulfite sequencing (WG methylation classifier);
- 507-gene targeted sequencing (SNV, and SNV-WBC with matched white-blood-cell background removal);
- 30x whole-genome sequencing (SCNA, SCNA-WBC, fragment endpoints, fragment lengths, allelic imbalance).

It also tests a pan-feature classifier over all nine cfDNA classifier scores, and a clinical risk-factor classifier with no cfDNA.

| Protocol | What is stored | Use cases |
| --- | --- | --- |
| `ctdnajam-20261010-protocol-ccga1-training-cv-sens-98spec` | Table 3 training columns: 9 classifiers, sensitivity at 98% specificity under 10-fold cross-validation, with 95% CI and TP/total | methylation (direct), fragmentomics (proxy) |
| `ctdnajam-20261010-protocol-ccga1-validation-sens-98spec` | Table 3 validation columns: 10 classifiers, with McNemar marks against WG methylation | methylation (direct), fragmentomics (proxy) |
| `ctdnajam-20261010-protocol-ccga1-validation-cso-accuracy` | Results text: cancer signal origin accuracy for WG methylation, SCNA and SNV-WBC on 127 jointly detected cancers | methylation (proxy) |

Validation sensitivities at 98% specificity:

| Classifier | Sensitivity |
| --- | --- |
| Pan-feature | 36% |
| WG methylation | 34% (30%-39%) |
| SNV-WBC | 33% |
| SCNA-WBC | 30% |
| Fragment lengths | 29% |
| SCNA | 27% |
| Allelic imbalance | 22% |
| Fragment endpoints | 18% |
| SNV | 16% |
| Clinical data | 2.6% |

## Relevance

- **Methylation detection: direct.** Both protocols measure the declared endpoint, all-stage sensitivity at a declared specificity on plasma cfDNA, as the stored direct cfMethyl-Seq judgement does. The weaknesses are carried as limitations: developer-run, case-control, a post hoc threshold and prototype assays. A reviewer may prefer proxy because the threshold was set on the validation set itself.
- **Methylation tissue of origin: proxy**, as for the stored SPOT-MAS judgements. It is a methylation-only origin result, which the use case's second exclusion says was missing, so `coverage.json` proposes narrowing that exclusion.
- **Fragmentomics: proxy for both protocols**, consistent with the reviewed fragmentomics judgements. The use case asks about low tumour fractions, and the per-classifier limits of detection by tumour allele fraction are in figures only.

## Sample overlap

None. CCGA sequencing data are not public. None of the cohorts behind either use case's existing judgements comes from CCGA:

- methylation: cfMethyl-Seq cohorts, a liver WGBS cohort, in silico mixtures and the SPOT-MAS Vietnam cohorts;
- fragmentomics: DELFI 2019, Jiang et al. 2018, Mathios et al. 2021, Zhou et al. 2022 and the pooled UNITE set.

The three new protocols share one set of CCGA participants with each other.

## Things a reviewer should judge

1. **Post hoc threshold.** STAR Methods state that the 98% specificity cutoff was set post hoc in both the training and the validation sets. Observed specificity was 97.9% (548/560) in training and 97.8% (354/362) in validation. This is recorded on every protocol and judgement, and in a claim.
2. **Post-unblinding classifiers.** The fragment endpoint, fragment length, allelic imbalance and pan-feature classifiers, and all origin classifiers, were developed after validation blinding was lifted. Recorded on the protocols and on each affected evaluation. This matters most for the fragmentomics judgements.
3. **Denominators.** Table 3 scores 833 training and 464 validation cancers; Table 1 has 854 and 485 analysable cancers. The gap of 21 in each set is not explained. Stored as printed.
4. **Jointly detected set.** The Results and the Methods name different classifier triples for the 127-cancer origin set. Accuracy also counts "other" as correct for six cancer types, so it is lenient.
5. **Supplementary Table S2.** It holds validation partial AUCs over 98% to 100% specificity, with 0.50 for the clinical classifier, which implies a standardised partial AUC the source does not define. It was not extracted, and no vocabulary concept was added. A follow-up could add it with a reviewer-agreed concept.
6. **Targeted methylation limit of detection.** The text prints one limit of detection: the later targeted methylation test at 1.3 x 10^-4 cTAF (second substudy, 559 solid cancers). It is a different assay on different samples, so it is a claim, not a result.

## Coverage

Not covered: per-classifier limits of detection (figure-only), sensitivity by stage (Figure S1), origin accuracy on each classifier's own detected set (Figure S5), Table S2, the GitHub summary statistics, and later CCGA substudies.
