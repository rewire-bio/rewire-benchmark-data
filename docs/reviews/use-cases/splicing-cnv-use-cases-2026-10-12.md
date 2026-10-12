# Verdict: splicing and CNV batches (2026-10-11 pass)

Reviewer: independent Claude review agent `reviewer-scnv`, 2026-10-12. I did not extract these batches. No human review is claimed. Nothing was executed or reproduced. I edited no records; every correction below is for the collector to apply before `records -- add`.

Worktree: `rewire-benchmark-data-lit-uc-splicing-cnv`, batch folders under `data/omics/`.

## Summary of verdicts

| Batch | Verdict |
| --- | --- |
| `use-case-coverage-cnv-20261011-hwang2026` | Approved with corrections (one limitation) |
| `use-case-coverage-cnv-20261011-zhang2026` | Approved with corrections (dbCNV is author_reported) |
| `use-case-coverage-rna-splicing-20261011-alavi2026` | Approved with corrections (duplicate Genos model, names, limitations, hash scope) |
| `use-case-coverage-rna-splicing-20261011-fortier2026` | Approved with corrections (Riepe score rule, CI-SpliceAI caveats) |
| `use-case-coverage-rna-splicing-20261011-silverstein2026` | Approved with corrections; the expression judgement is held (Tables S7 and S9 conflict) |

All 458 stored values match their sources. No value needs a superseding result. The corrections are to origin, qualifiers, limitations, names and one duplicate record.

Applies to every batch: delete `extract/__pycache__/` from each batch folder before writing `review.json`, so the receipt does not hash compiled bytecode.

## Batch corrections

### hwang2026: approved with corrections

1. `cnv-20261011-hwang2026-source-article`, `attributes.limitations`: append
   "The Abstract says all tools improved after filtration; Table 4 gives cn.MOPS sensitivity falling from 0.170 to 0.162."

Judgements `use-case-mapping-cnv-20261011-hwang2026-pre-filter` and `-post-filter`: `proxy` confirmed. Set `reviewed_evaluations` to the four evaluations on each protocol:
- pre-filter: `cnv-20261011-hwang2026-eval-pre-filter-cn-mops`, `-cnvkit`, `-conifer`, `-exomedepth`
- post-filter: `cnv-20261011-hwang2026-eval-post-filter-cn-mops`, `-cnvkit`, `-conifer`, `-exomedepth`

### zhang2026: approved with corrections

dbCNV (reference 24, Lv et al., BMC Genomics 2023) lists Dayang Chen and Xiuming Zhang as authors, both at the Medical Laboratory of the Third Affiliated Hospital of Shenzhen University. They are two of the three authors of this paper, and that laboratory supplied the internal benchmark subset. Table 1 also gives dbCNV's original test set as "Internal dataset". I checked this against the Europe PMC author and affiliation record for PMID 36941551. The paper declares no competing interests.

1. Set `attributes.origin` to `author_reported` on:
   - `cnv-20261011-zhang2026-eval-five-category-dbcnv`
   - `cnv-20261011-zhang2026-eval-three-category-duplications-dbcnv`
   - `cnv-20261011-zhang2026-eval-three-category-deletions-dbcnv`
2. Append this limitation to `attributes.limitations` on all three protocols (`cnv-20261011-zhang2026-protocol-five-category`, `-three-category-duplications`, `-three-category-deletions`) and on all three judgement claims (`use-case-mapping-cnv-20261011-zhang2026-five-category`, `-three-category-duplications`, `-three-category-deletions`):
   "Two of the three authors (X. Zhang and D. Chen) are authors of dbCNV (reference 24), developed in the same laboratory, so the dbCNV rows are author_reported. dbCNV's original test set was that laboratory's internal dataset, and this benchmark includes the laboratory's internal CNV-seq cases (December 2019 to November 2025); overlap is not tested. The paper declares no competing interests."
3. `cnv-20261011-zhang2026-source-article`, `attributes.limitations`: append
   - "The Abstract gives ClassifyCNV VUS accuracy 95.33%; Table 4 prints 94.92% (duplications) and 95.74% (deletions), which with the Table 2 class sizes (886 and 329) pool to about 95.1%."
   - "Two Table 4 deletion cells are not a whole-number share of the Table 2 class size (AnnotSV P 95.16% of 287 P and LP deletions; MarCNV-ISV VUS 89.86% of 329 VUS deletions); the other 28 cells are."

Relevance `proxy` confirmed for all three; I do not prefer `outside_scope`. The use-case question includes characterisation and analyst assessment, and the limitations already say no detection step is evaluated. `reviewed_evaluations` should list the five evaluations on each protocol (`-annotsv`, `-classifycnv`, `-dbcnv`, `-marcnv-isv`, `-x-cnv` after `cnv-20261011-zhang2026-eval-<protocol>-`).

### alavi2026: approved with corrections

1. Duplicate model. `lit-microbial-20261011-virobench-model-genos` (Genos family, `source_checked`) has already been added to the store in the microbial worktree. Remove `rna-splicing-20261011-alavi2026-model-genos` from `batch.jsonl` and `claims.csv`. Point the `configuration_of` link of `rna-splicing-20261011-alavi2026-config-genos-10b` and `rna-splicing-20261011-alavi2026-config-genos-10b-clinvar` at `lit-microbial-20261011-virobench-model-genos`, and update `coverage.json`. If the microbial batch does not land first, the microbial batch must reuse the Alavi ID instead; the two records must not both reach the store.
2. Name casing. In the `name` field of every configuration, evaluation and result record in the batch, replace:
   - `Alphagenome` with `AlphaGenome`
   - `Spliceai` with `SpliceAI`
   - `Ntv3` with `NTv3`
   - `Clinvar` with `ClinVar`
   - `-Bp)` with `-bp)`
   - `(W/O Hu. Ident.)` with `(without human identifier)`
   - `(Hu. Ident.)` with `(human identifier)`

   Leave `attributes.reported_name` as printed. In `attributes.version`, set `rna-splicing-20261011-alavi2026-protocol-opa1-evaluation` and `-opa1-extended-positive-calls` to `Table III`, and `-protocol-multigene` to `Table IV`.
3. `rna-splicing-20261011-alavi2026-source-article`, `attributes.limitations`: append
   "Four printed accuracies differ from those computed from the same row's counts: Table III Borzoi (128-bp) 89.1% (counts give 89.8%); Table IV AlphaGenome (either module) 71.6% (70.5%), Borzoi (128-bp) 80.9% (81.4%) and Genos 10B 61.7% (61.2%)."
4. Same source: add `attributes.hash_scope`:
   "SHA-256 of one retrieval of the bioRxiv PDF. bioRxiv stamps the PDF when serving it (ModDate and the second document ID), so later retrievals differ. A reviewer retrieval on 2026-10-12 of the same length (1,823,372 bytes) had SHA-256 e22491e217c7c158528668b38bcb8b9855b89617b807c60b740795a204c84b0a and ModDate D:20261011221204-07'00'. All 168 Table III and IV cells in that copy match the stored results."
5. Append to `attributes.limitations` on `rna-splicing-20261011-alavi2026-protocol-multigene` and `use-case-mapping-rna-splicing-20261011-alavi2026-multigene`:
   "Genos 10B ClinVar is fine-tuned on ClinVar labels and the benign controls are ClinVar variants; training overlap is not tested in the source."

Genos 10B row: confirmed as `ZhejiangLab/Genos-10B` (v1). Results B says "this optimized Genos 10B configuration outperformed both the fine-tuned ClinVar model and the extended-species v2 iteration (Table III; ... Supplementary Table III)". Origin `independent_paper` confirmed: single author at 712 North Inc., who developed none of the models. The equity disclosure concerns 712 North only. Both judgements are confirmed as `proxy`. `reviewed_evaluations` should list the 12 evaluations on each protocol. Results reviewed on this source must not use the `source-hash-verification` method; use `pdf-text-parse` and `independent-cell-check`.

### fortier2026: approved with corrections

1. Riepe score rule. Methods 'Riepe benchmark dataset' says "the most relevant SpliceAI score was selected based on each variant's effect type". The configurations say the maximum of four delta scores is used, which does not hold for Table 2.
   - Set `attributes.metric_qualifier` to "delta score for each variant's effect type; threshold optimised per gene and algorithm for maximum accuracy (upper bound)" on these 12 results: `rna-splicing-20261011-fortier2026-result-riepe-{spliceai,ci-spliceai,openspliceai}-{balanced-accuracy,f1-score,recall,specificity}`.
   - Set `attributes.comparison.adaptation` to the same text on `rna-splicing-20261011-fortier2026-eval-riepe-spliceai`, `-eval-riepe-ci-spliceai` and `-eval-riepe-openspliceai`.
2. Training split caveat. On all six protocols and all four judgement claims, replace the limitation "Labels and variant sets are reused from earlier publications; the open-source models and SpliceAI were not trained to the same chromosome split." with:
   "Labels and variant sets are reused from earlier publications. CI-SpliceAI was trained on all human chromosomes, so no benchmark variant is held out from its training; ABCA4 lies on a test chromosome held out by both SpliceAI and OpenSpliceAI (Methods 'Technical overview of deep learning methods'; Discussion)."
3. Append to `attributes.limitations` on `rna-splicing-20261011-fortier2026-protocol-ci-spliceai-benchmark` and `use-case-mapping-rna-splicing-20261011-fortier2026-ci-spliceai-benchmark`:
   "The variant set was assembled and published by the CI-SpliceAI developers (reference 9)."
4. `rna-splicing-20261011-fortier2026-source-article`, `attributes.limitations`: append
   "The Discussion says SPiP results hold 'even with optimized thresholds'; Methods and Results use the standard 0.5 threshold for SPiP."
5. Recommended: add this to the description of `rna-splicing-20261011-fortier2026-data-riepe`: "The 213 variants are the union of the stored Riepe sets splicing-follow-up-20261009-data-riepe2021-abca4-di (81), -abca4-ncss (71) and -mybpc3-ncss (61)."

Origin is confirmed: the Legacy Ensemble rows are `author_reported` (Competing Interests: all authors are Golden Helix employees, and VarSeq supplies the legacy algorithms). The deep learning rows are `independent_paper` (Golden Helix "has no commercial relationship with the developers of SpliceAI, OpenSpliceAI, or" CI-SpliceAI). All four judgements are confirmed as `proxy`, and leaving Tables 5 and 6 unjudged (ClinVar labels) is correct. `reviewed_evaluations` should list the four evaluations on each protocol.

### silverstein2026: approved with corrections; expression judgement held

New finding: Table S7 conflicts with Table S9 on the expression negatives. In Tables S3, S4 and S8, "YES" in a true-negative row marks a sample with no outlier. That reading reproduces Table S9 for FRASER2.0 (4 TN, 2 FP), ANEVA-H (1 TN, 4 FP) and MAE (0 TN, 5 FP). Read the same way, Table S7 gives OUTRIDER 8 clean of 9 negative samples (5 of 6 muscle, 3 of 3 fibroblast), where Table S9 row 7 and the Results prose give 4 TN and 5 FP (56%). Table S7 lists 6 muscle negatives for OUTRIDER + GTEx, with 1 clean (5 of 6 = 83%, as in the prose), where Table S9 row 8 counts 5 (TN 1, FP 4). Neither reading of "YES" reconciles Table S7 with Table S9 row 7.

1. Do not add the `assessed_by` link for `rna-splicing-20261011-silverstein2026-protocol-expression`. Keep `use-case-mapping-rna-splicing-20261011-silverstein2026-expression` at `needs_review`, and keep `rna-splicing-20261011-silverstein2026-eval-outrider`, `-eval-outrider-plus-gtex` and their 18 results at `needs_review`. Remove the expression entry from `use-case-links.json`.
2. Append to `attributes.limitations` on `rna-splicing-20261011-silverstein2026-source-tables-s1-s10`, `rna-splicing-20261011-silverstein2026-protocol-expression` and `use-case-mapping-rna-splicing-20261011-silverstein2026-expression`:
   "Table S7 true-negative rows do not reproduce Table S9 rows 7 and 8: read as in Tables S3, S4 and S8 ('YES' = no outlier), Table S7 gives OUTRIDER 8 of 9 negative samples without outliers (Table S9: 4) and OUTRIDER + GTEx 1 of 6 (Table S9: 1 of 5). The prose rates (56% and 83%) match Table S9 for OUTRIDER and Table S7 for OUTRIDER + GTEx."
3. On all three protocols and all three judgement claims, replace the limitation beginning "Variants with clinically interpretable mechanisms were selected" with:
   "Variants with clinically interpretable mechanisms were selected; the authors state this favours clearly defined events and likely underestimates tool sensitivity, and that binary outlier scoring of negatives may overestimate false-positive rates and lowers MCC (Discussion, limitations paragraph)."

The splicing judgement is confirmed as `direct` and allelic imbalance as `proxy`. `reviewed_evaluations`:
- splicing: `rna-splicing-20261011-silverstein2026-eval-fraser`, `-fraser2-0`, `-leafcuttermd`, `-mintie`, `-rmats`
- allelic imbalance: `rna-splicing-20261011-silverstein2026-eval-aneva-h`, `-eval-mae`

## Answers to the collector's questions

1. Silverstein discrepancies. None of the five should be an `evidence_concern`. A concern on either Silverstein source withholds every result from it (`cleanSource` in `shared/omics/use-cases.ts`; `published-comparisons.ts`), including the direct splicing rows. Those rows agree across Tables S3 to S5, S9 and the prose, apart from the 22 versus 21 negative count. All five stay as limitations. The sixth conflict, Table S7 against Table S9 for OUTRIDER, is handled by holding the expression judgement (above), not by a concern.
2. ANEVA-H as `author_reported`: confirmed. Reference 36 is "Ganapathy KR, Broly M, Silverstein S, ..."; Ganapathy and Silverstein are authors here, and so is P. Mohammadi. Splicing `direct` and allelic imbalance `proxy` are confirmed. Expression would be `proxy`, but it is held.
3. Mixed units. The shared qualifier "positives per known event or gene, negatives per true-negative sample" plus the protocol limitation is enough. The summary cites only counts and recall, never accuracy, precision or MCC.
4. Fortier. Legacy Ensemble `author_reported` is confirmed, and both prose slips are confirmed; I found a third (SPiP thresholds) and a stale "three datasets" line, which is already recorded. The Riepe, CI-SpliceAI, SPiP and Barbosa deep intronic protocols do bear on `use-case-splicing-follow-up`; that store already has the three Riepe datasets. Judging them there is a separate pass for the lead, and it does not block this approval.
5. Alavi. Genos 10B is v1, confirmed. Both Table IV mismatches are confirmed, and I found four more accuracy cells that disagree with their counts (correction 3). The `proportion` concept with a qualifier for type II error and positive-call rates is acceptable. A false-negative-rate concept would not respell an existing one, but adding it is not needed for this batch.
6. Zhang. Table 4 as `recall` with a qualifier is correct. All 18 duplication and benign-deletion cells are whole-number shares of the merged Table 2 class sizes (1,048; 886; 191; 290), so the cells are per-class recall. Table 3 aggregation `unreported` is correct. `proxy` is confirmed. dbCNV origin is corrected.
7. Hwang. Post-filter `author_reported` is confirmed (the filter is the authors', defined on the same 180-exome cohort). TP + FN equals the reference count in every column, and sensitivity and PPV recompute from the counts. The prose discrepancies are confirmed, and I added one.
8. Summaries: approved as rewritten below.

## Approved summary text

### use-case-summary-patient-rna-splicing-validation (replace `value` with)

The one recovery result already on this page is FRASER on the 119-sample Kremer fibroblast cohort, reported by its developers: a mean 85% (11 of 13) of known pathogenic splicing events recovered at a 30-sample subsample. Six published comparisons add evidence. Segarra-Casas et al. (2025), independent of the tool developers, recorded which callers reported 16 known pathogenic splicing events in clinical muscle RNA-seq from 98 samples: FRASER with |dPSI| > 0.1 reported 13, FRASER with |dPSI| > 0.3 reported 9, FRASER2 10 (and one more only with the full cohort), rMATS-turbo 7 and LeafCutterMD 4 (Table 2); the events were established partly with these callers. Segers et al. (2026), the saseR developers, ranked 12 reported disease genes in the Kremer cohort: the gene ranked within the top 10 in 9 of 12 samples for saseR-junctions, in 6 of 12 for FRASER 2.0 with the autoencoder and in 7 of 12 for FRASER 2.0 with PCA (Table 2); the 12 genes were reported in earlier analyses of the same cohort, partly with OUTRIDER and FRASER, and several are expression rather than splicing defects. Silverstein et al. (2026, preprint), a clinical research group that did not develop the splicing callers, scored them on 97 previously diagnosed neuromuscular RNA-seq samples and also counted outlier calls in true-negative samples (Table S9). On known pathogenic splicing events in muscle and fibroblast RNA-seq, rMATS-turbo detected 15 of 23 and MINTIE 8 of 23; on muscle, fibroblast and cycloheximide-treated fibroblast RNA-seq, FRASER detected 21 of 68 and LeafcutterMD none of 67; FRASER2.0, run on muscle only, detected 2 of 16. rMATS-turbo and MINTIE reported outliers in all 9 true-negative samples they were run on, FRASER and LeafcutterMD in all 21, and FRASER2.0 in 2 of 6. Denominators differ by tool, a negative sample with any outlier counts as one false positive, and the known events were chosen because they were clinically interpretable and visible in the RNA-seq, which the authors say favours clearly defined events. Drost et al. (2025), a diagnostic laboratory independent of the tool developers, scored 243 clinically ascertained variants, each tested for a splicing effect in patient cells or by exon trapping, with four DNA-based predictors. On all 243, AUROC was 0.895 for SpliceAI, 0.885 for Pangolin, 0.830 for SPiP and 0.806 for SQUIRLS (Data S1 Table S3); at literature thresholds sensitivity was 0.871, 0.858, 0.832 and 0.800 and specificity 0.750, 0.773, 0.761 and 0.591 (Table S4), and the authors' rule of requiring at least two of the four tools gave sensitivity 0.916 and specificity 0.727. Most in-house variants were sent for testing because another predictor (Alamut) flagged them, so negatives are mostly predicted-but-unconfirmed variants. Two further DNA-based comparisons add proxy evidence. Fortier et al. (2026), independent of the SpliceAI, CI-SpliceAI and OpenSpliceAI developers, report balanced accuracy on functional splice-assay variants in ABCA4 and MYBPC3 of 0.836 for SpliceAI, 0.794 for CI-SpliceAI and 0.746 for OpenSpliceAI, and on 242 deep intronic pathogenic variants with 242 common controls of 0.940, 0.890 and 0.841 (Tables 2 and 4); both sets of thresholds were tuned on the same data, so these are upper-bound estimates, and CI-SpliceAI was trained on all chromosomes. Alavi (2026, preprint) applied thresholds tuned on OPA1 variants to 76 functionally validated canonical splice-site variants and 107 ClinVar benign intronic variants from 65 genes: sensitivity and specificity were 88.2% and 99.1% for SpliceAI, 85.5% and 86.9% for pretrained NTv3 650M, 71.1% and 100% for Evo2 40B with a human identifier, 56.6% and 80.4% for AlphaGenome (either module) and 27.6% and 85.0% for Genos 10B (Table IV). All values are transcribed from the publications, not reproduced; none is a diagnostic-yield estimate, and results from different sources measure different endpoints and must not be pooled. This summary describes evidence and does not recommend a clinical workflow.

Update the claim's `source_locator` to add: `rna-splicing-20261011-silverstein2026-source-tables-s1-s10: Table S9 rows 2 to 6; rna-splicing-20261011-fortier2026-source-article: Tables 2 and 4; rna-splicing-20261011-alavi2026-source-article: Table IV`.

### use-case-summary-cnv-detection-characterisation (replace `value` with)

On HG002 deletions, DRAGEN 4.2 with SV-informed CNV calling found 87 to 100% of deletions in every size bin, with precision 0.99 to 1.00; this is the developers' own benchmark. CNVnator matched it above 10 kb but found only 26% of deletions of 1 to 5 kb and 51% of 5 to 10 kb. On NA12878, LUMPY, DELLY and Manta recovered 88 to 94% of known CNVs, but only 20 to 33% of their calls matched; Manta and CNVnator were used to build this truth set, which can favour them. The other callers recovered 1 to 43%. Hwang et al. (2026) compared four exome callers with chromosomal microarray CNVs in 39 clinical exomes, scoring deletion and duplication exons together: sensitivity and PPV were 0.758 and 0.025 for ExomeDepth, 0.662 and 0.096 for CNVkit, 0.768 and 0.239 for CoNIFER and 0.170 and 0.041 for cn.MOPS. The truth set keeps only array CNVs with at least ten probes that overlap exome baits, so any other exon call counts as a false positive. After the authors removed regions where each tool called CNVs in more than 10% of the same 180-exome cohort, ExomeDepth reached 0.903 and 0.102 on a smaller reference set of 2,124 exons (Table 4); this filter is the authors' own method. For characterisation, Zhang et al. (2026) ran five automated ACMG classifiers on 3,031 expert-classified CNVs: five-category accuracy, averaged across classes in a way the paper does not state, ranged from 48.76% (X-CNV) to 69.81% (MarCNV-ISV) (Table 3). With likely and definite classes merged, every tool recognised more pathogenic deletions than pathogenic duplications (AnnotSV 95.16% versus 86.39%) (Table 4). Two of the three authors developed dbCNV and the reference includes their own laboratory's cases, so the dbCNV results are author-reported. None of the comparisons shown reports duplication detection separately, none covers tumour samples or long reads, and none evaluates a foundation model.

Update the claim's `source_locator` to add: `cnv-20261011-hwang2026-source-article: Table 4; Methods 2.2 and 2.5; cnv-20261011-zhang2026-source-article: Tables 3 and 4`.

Both summaries are to be repinned after the judgements they describe (`npm run use-cases:repin -- <dated review> <claim-id>...`).

## Approved use-case field changes

`use-case-patient-rna-splicing-validation`, `attributes.evidence_gaps`:
- Replace "Among the sources extracted, no RNA-seq caller comparison reports false positives per sample in a table; outlier workload is figure-only in Segarra-Casas et al." with "False positives are tabulated only as true-negative samples with any outlier (Silverstein et al. 2026, Table S9); outlier counts per sample remain figure-only."
- Add "MAJIQ-CLIN (Genet Med 2026) compares splicing outlier tools but could not be retrieved as full text."
- Add "Silverstein et al. 2026 expression-outlier true-negative counts conflict between Tables S7 and S9, so the OUTRIDER rows are not linked."

`use-case-cnv-detection-characterisation`, `attributes.evidence_gaps`:
- Replace "Duplication evidence is limited to 10 HG002 duplication truth events in one source (De La Vega et al. 2025)." with "Whole-genome duplication evidence is limited to 10 HG002 duplication truth events in one source (De La Vega et al. 2025); the exome comparison (Hwang et al. 2026) scores duplication and deletion exons together against chromosomal microarray truth."
- Add "The Genome Biology 2026 HG002 T2T-Q100 and CMRG SV benchmark (doi:10.1186/s13059-026-04048-4) is not stored because its supplementary table identity is ambiguous."

No change to `inputs`, `exclusions` or any other pinned field. All new judgements are `proxy` except Silverstein splicing (`direct`), so the existing reviewed judgements stay pinned. `evidence_gaps` is not a pinned field.

## Review fields to record

For every result in an approved batch, the collector or lead fills `review` with: `method` `["source-hash-verification", "independent-cell-check", "automated-source-review"]`. Use `["pdf-text-parse", "independent-cell-check", "automated-source-review"]` for Alavi. Set `reviewer` `["claude"]`, `reviewer_note` "Independent Claude review agent reviewer-scnv; did not extract this batch; no human review claimed", `date` "2026-10-12", and the batch's `artifact_sha256` and `retrieval_url` from its source record. The `note` points to this verdict and the dated review. Judgement claims get the same reviewer and date, `reviewed_evaluations` as listed above, status `source_checked`, then repin. Write `review.json` and the dated review in `docs/reviews/use-cases/` after the corrections, so the receipt hashes the corrected files.

## Checks run and outcomes

Sources and hashes:
- Hwang (PMC12841491 XML), Fortier (PMC13170886 XML) and Zhang (PMC13018948 XML): re-downloaded from Europe PMC; SHA-256 matches the source records. The archived gzip copies of Hwang and Fortier decompress to the same hashes.
- Silverstein article XML and supplement XLSX: archived gzip copies decompress to the pinned SHA-256s. The medRxiv XLSX re-download also matched (3d137444...). The medRxiv XML re-download returned an empty body (rate limit), so the archive was used.
- Alavi PDF: first attempts returned HTTP 429. A later retrieval returned 1,823,372 bytes, the same length as pinned, but a different SHA-256 (e22491e2...). The difference is the per-serving ModDate and document ID stamps. The source is not archived (CC BY-NC-ND), so the pinned bytes cannot be re-verified; see Alavi correction 4.

Automated full comparison, using my own parsers (stdlib ElementTree for JATS tables, stdlib zipfile for the XLSX cell XML, and a token parser over `pdftotext -layout` pages 6 and 9 for Alavi). The collector's scripts were not imported or run.

| Batch | Results | Mismatches | Cells of chosen tables not extracted |
| --- | --- | --- | --- |
| hwang2026 (Table 4) | 48 | 0 | 0 |
| zhang2026 (Tables 3, 4) | 65 | 0 | 0 |
| fortier2026 (Tables 1 to 6) | 96 | 0 | 0 |
| alavi2026 (Tables III, IV) | 168 | 0 | 0 |
| silverstein2026 (Table S9 B2:J10) | 81 | 0 | 0 |

Each comparison checked `printed_value`, `numeric_value` and the row and column labels in `source_locator`. Silverstein printed values are the shortest round-trip decimal of the stored General-format cells, which matches store precedent (ctdnafrag-20261009-source-wang2026). `claims.csv` matches `batch.jsonl` for every result and claim in all five batches.

Hand check of a stratified sample against the rendered table: every table, every model, and every metric column.
- Hwang: all 48.
- Silverstein: all 81.
- Zhang: 40 (20 from Table 3, 20 from Table 4).
- Fortier: 40 (6 or 7 per table).
- Alavi: 40 (24 from Table III, 16 from Table IV, all 12 models).

All matched.

Internal consistency, recomputed from printed counts:
- Hwang: TP + FN = reference in all 8 columns; sensitivity and PPV recompute.
- Silverstein: every Table S9 formula cell recomputes from TP, FN, TN and FP (the LeafcutterMD F1 is a typed 0 where the formula is undefined).
- Alavi: the count and percentage pairs, plus accuracy and PPV from counts, found the 2 recorded and 4 new mismatches.
- Zhang: denominators fit Table 2 class sizes for 28 of 30 Table 4 cells.

Metric, qualifier, direction, unit, uncertainty and denominator were checked against each table's header, caption, footnotes and Methods for all five batches. Corrections are listed above (Fortier Riepe qualifier). Every `null` uncertainty is unprinted in the source.

Origin and author overlap:
- Checked every evaluated tool's reference author list against the paper's authors.
- Found the dbCNV overlap (Zhang).
- Confirmed ANEVA-h (Silverstein), the Legacy Ensemble (Fortier) and the Hwang filter as author-reported.
- No overlap for the other tools; for Alavi, no evaluated model is by the author.

Locators: every result locator resolves to one cell. The Alavi locators give the right PDF pages (6 and 9).

Duplicates:
- No source DOI or PMC ID from these batches is on `origin/main` (bba147c) or in any committed or uncommitted file of the other `claude/lit-20261011-*` branches and `../rewire-benchmark-data-lit-*` worktrees.
- Every reused ID (catalog-model-spliceai, catalog-model-alphagenome, catalog-model-evo-2, regulatory-variant-20261009-model-borzoi, lit-genomics-20261011-guanine-model-nucleotide-transformer-v3, cnv-20261009-method-cn-mops, rare-reanalysis-20261009-method-conifer, rare-reanalysis-20261009-method-exomedepth, and the four rna-splicing-20261009 methods) resolves on `origin/main`.
- No new model, method or dataset matches an existing name on main.
- One duplicate was found: the Genos model record in the microbial worktree (Alavi correction 1). The Fortier Riepe dataset is the union of three stored Riepe datasets, which is not a duplicate (correction 5).

Scope and relevance: every judgement's endpoint was checked against the use case's question, inputs and output. Every limitation was checked against the source's stated caveats, and missing caveats were added above. No judgement has `excluded_evaluations`, and none needs one apart from the held Silverstein expression protocol.

Summaries: every number in both approved texts was traced to a stored or batch result. Each text names author-reported results (the FRASER developers, the saseR developers, the DRAGEN developers, the Hwang filter and dbCNV) and truth-set bias (Segarra-Casas events established with the callers, Drost negatives, the Gabrielaite truth built with Manta and CNVnator, the Silverstein event selection, CMA probe and bait limits, the Fortier in-sample thresholds). Neither recommends.

Not run: `npm test`, `npm run typecheck` and `npm run build`. The batches are not in the store and I was told not to edit records; whoever applies the corrections should run them after `records -- add`.
