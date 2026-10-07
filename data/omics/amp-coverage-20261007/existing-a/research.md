# Existing use-case coverage review A

Reviewed 2026-10-07T12:35:12.080986+00:00. Six dynamically selected original cases; no new results, mapping writes or publication. Existing result IDs are reused.

## Interpret BRCA1/BRCA2 germline variants

Case: `use-case-brca1-brca2-germline-interpretation`. Article rewire.it #343; benchmark execution gap #None (null means unextracted). Active mappings: 10; existing results: 48.

BRCA1 BayesDel ≥0.28 calibration: printed LR 7.09 (95% CI 6.06–8.30); 377/456 functionally pathogenic, 149/1278 functionally benign. Exact Table2 row inspected in freshly fetched primary PMC HTML. Functional-reference calibration, not independent complete clinical classification. Historical article specifies v1.0; a new prospective evaluation must pin the then-current ClinGen specification.

Source `uc-clinical-20260930-source-enigma`; retrieval 2026-10-07T12:33:10.164438+00:00; current request status fetched; SHA256 fca9f678b3ad1b832910dd0c6f7013613997a5c620f755591fb57e4d88111ae7.

Verdict: retain scoped existing evidence; no duplicate scientific result or new candidate.

Remaining gaps: Independent complete clinical classifications, serious-error adjudication and equal-evidence reviewer-time comparison were not found in selected evidence. BayesDel labels derive from functional assays; threshold calibration is not held-out pathogenicity validation. Study v1.0 manual pilot revises specifications on the same variants; current specification version must be pinned for any new run. Generic BayesDel thresholds from Pejaver are a relevant alternative described in Table S4; supplement download returned challenge HTML, so the four primary-body percentages/bounds are entered while unverified Table S4 cells remain missing. Qualified human scientific review remains outstanding; automated source transcription does not establish experimental replication.

## Transfer cell-type annotations to a new dataset

Case: `use-case-cell-type-annotation-transfer`. Article rewire.it #349; benchmark execution gap #None (null means unextracted). Active mappings: 5; existing results: 27.

Fresh Europe PMC XML Par11 confirms scmapcell Baron Human median F1 0.984 and 4.2% unlabeled; SVM rejection 0.991 and 1.5%, SVM 0.980 and 100% classified. Intra-dataset cross-validation, not transfer to a new dataset; do not widen the applicable task claim. Fresh XML SHA identical to reviewed 2026-10-06 source.

Source `ucc-research-source-abdelaal-2019-paper`; retrieval 2026-10-07T12:31:55.408302+00:00; current request status fetched; SHA256 6df0937c5a2d8ba06465ba356c2321fb9f52d9ecf23456876acd82f828b41d4c.

Verdict: retain scoped existing evidence; no duplicate scientific result or new candidate.

Remaining gaps: Automated source review only; independent human scientific review remains outstanding. Checkpoint and split hashes unextracted; no deployment calibration claim. Reference labels are author annotations, not independent ground truth. Unknown-type rejection ROC appears in Supplementary Figure 4 but numerical curve labels are not extracted here.

## Review EGFR lung-cancer actionability evidence

Case: `use-case-egfr-nsclc-actionability-resistance-evidence`. Article rewire.it #345; benchmark execution gap #28 (null means unextracted). Active mappings: 2; existing results: 164.

Current PDF fetch blocked HTTP429. Existing archived v3 primary PDF SHA checked and page15/printed14 inspected: 37 of 40 (92.5%) appropriate-content for fine-tuned MedCPT and Qwen3-Reranker-8B. Fresh bioRxiv API confirms latest listed version3 dated2026-08-29, published NA. Cached bytes and live metadata agree in version identity, but new current PDF byte identity cannot be established. Pan-cancer within-linked-publication retrieval proxy, no EGFR-only score.

Source `ucc-clinical-egfr-source-civicfact-v3`; retrieval 2026-10-07T12:31:55.408476+00:00; current request status blocked; SHA256 unavailable.

Verdict: retain scoped existing evidence; no duplicate scientific result or new candidate.

Remaining gaps: No independently adjudicated advanced EGFR-mutant NSCLC evidence-retrieval benchmark with prior therapy, treatment line, date, jurisdiction and contradictions was established by this bounded search. CIViC study reports pan-cancer aggregate and predictive direction metrics; no published EGFR-only score was found. OncoTraj (arXiv:2606.11144) predicts longitudinal resistance and is outside the requested evidence-retrieval endpoint. Manual versioned lookup plus primary-source review still needs measured equal effort. Qualified human scientific review remains outstanding; automated source transcription does not establish experimental replication.

## Assess models for genetic perturbation experiments

Case: `use-case-genetic-perturbation-response`. Article rewire.it #334; benchmark execution gap #None (null means unextracted). Active mappings: 2; existing results: 8.

Fresh publisher supplement PDF SHA identical to original; printed p34/PDFp35 SupplementaryTable6 GEARS MSE 0.216±0.053, CPA 0.354±0.049; GEARS PearsonDE0.556±0.030. Exact Table6 extracted with pdftotext. Norman2019 transcriptional response endpoint; exact scoring-gene set and printed± spread type unextracted. Crossmark reports Document is current.

Source `coverage-source-gears-supp`; retrieval 2026-10-07T12:31:55.408552+00:00; current request status fetched; SHA256 1daaeb10f072577a3e420a796cd7e29e88ea9462639de7332ae91b2fe86b3b24.

Verdict: retain scoped existing evidence; no duplicate scientific result or new candidate.

Remaining gaps: The exact Table 6 split manifest, scoring gene subset, scored counts and checkpoint revisions remain unextracted. Do not silently label the MSE endpoint as Top20. The table does not identify its printed spread as SD, SE or a confidence interval; these scores do not establish a statistically supported winner. Both endpoints and the repeated No Perturb row are overlapping evidence from one source comparison, not independent replications. Performance in a new cell system and experimental hit rates need a separate prospective evaluation. Human scientific review remains outstanding. 30 September 2026 audit: A benchmark exists for expression responses, but prospective experiment-selection hit rates and transfer to a new cell system remain uncovered by this mapped comparison. 30 September 2026 audit: Table 6 scoring gene set, checkpoint revisions and exact split manifests remain unextracted; do not infer Top20 MSE or confidence intervals from the printed spreads.

## Shortlist molecular identities from tandem mass spectra

Case: `use-case-mass-spectrum-molecule-shortlisting`. Article rewire.it #335; benchmark execution gap #None (null means unextracted). Active mappings: 7; existing results: 69.

Fresh explicitly versioned arXiv v2 PDF SHA identical to existing v2 source; header2605.19752v2 dated25Sep2026. Table3 printed/PDFp7 MassSpecGym Formula Split R@1, formula-free raw MSAlign column, 47.5±3.4 percent, SD over3 random splits. True structure assumed present among256 candidates; no authenticated open-world structure identification. Existing v1 records retain distinct values/version; fresh v2 fetch does not validate v1 values.

Source `uc20260930-source-msalign-v2`; retrieval 2026-10-07T12:31:55.408615+00:00; current request status fetched; SHA256 a31d1167b0ded72f64717881dd6cba0946a56b495d76f169d8e44115c3266fda.

Verdict: retain scoped existing evidence; no duplicate scientific result or new candidate.

Remaining gaps: The correct structure must be in a 256-candidate mass-filtered pool. Scores do not transfer automatically to a larger database, a different pool-construction procedure or a missing true structure. MCES and formula splits impose different distribution shifts. The source authors favour formula splits for their deployment interpretation; that choice does not prove that formula-split performance represents every intended application. Reported methods are the paper implementations: DeepSets training was extended to 50 epochs. These are not interchangeable with original model-paper scores or current checkpoints. Exact test denominators, split-manifest hashes, checkpoint hashes and evaluator revisions remain unextracted or unreported in the catalogue. No uncertainty values or new independent reproduction are established. Candidate recall is not an authenticated metabolite identification, a clinical diagnosis or a calibrated probability. Human domain review remains outstanding. The four metric and split groups come from one paper and do not constitute independent replications. 30 September 2026 audit: v1 source record labels 2605.19752v1 but uses an unversioned URL that now serves v2; old source bytes/values must remain immutable. v1-specific URL returned HTTP406 during this audit. 30 September 2026 audit: For MCES, the v2 Table3 generic caption says three random splits, but Section5.1 explicitly uses two validation/test-swapped variants; the discrepancy is preserved. 30 September 2026 audit: Benchmark assumes the true structure is present among 256 neutral-mass-matched candidates. Unknown candidates, instrument-specific prospective performance and authenticated identification remain gaps.

## Select perturbations for a defined cellular response

Case: `use-case-phenotype-perturbation-selection`. Article rewire.it #348; benchmark execution gap #None (null means unextracted). Active mappings: 2; existing results: 21.

Fresh EuropePMC XML SHA identical to prior preprintv1; Discussion P43 explicitly prints two targets Dimt1,Ndufv2, and abstractP3 names both. Existing numeric2 retained; no success fraction. Mouse T-cell desired-state composition endpoint, not antitumor efficacy. Candidate denominator unresolved61 abstract nominations/57 selected Results/59 README/50 postQC; no matched-budget prospective conventional/random control.

Source `ucc-research-source-challenge-paper`; retrieval 2026-10-07T12:31:55.408390+00:00; current request status fetched; SHA256 6c98a7d0f0ab7abff1c76a7f184382a10ca82c39b34879b83d205a994412aa22.

Verdict: retain scoped existing evidence; no duplicate scientific result or new candidate.

Remaining gaps: 61 nominations / Results 57 selected targets / README 59 targets / 50 post-QC perturbations need reconciliation; no success fraction calculated. Automated source review only; independent human scientific review remains outstanding. Custom ranking AUC is not ROC AUC, prospective hit rate or efficacy. No matched-budget conventional/random prospective comparison; no antitumor efficacy, rescue or selectivity result in this endpoint. Original model implementations/checkpoints are not pinned in the intake; no uncertainty printed. Preprint v1; original and reimplemented ranking scores kept separate. Screen2 ranking population is enriched by original nomination methods.

## Access, version and review limits

ENIGMA XML returnedHTTP500; primary PMC HTML succeeded and Table2 checked. CIViC-Fact live PDF returnedHTTP429; archived v3 bytes verified and fresh API lists version3 as latest with publishedNA. These access results are retained rather than presented as successful current PDF retrieval. GEARS, MSAlignv2, Abdelaal and challengev1 freshly fetched bytes match prior digests. No new score is computed. Source query times and retrieval hashes are in review.json and per-request JSON.

The challenge article is CC BY-NC-ND4.0; source archive is an unmodified research evidence copy and must not be assumed licensed for commercial redistribution. ENIGMA primary page carries copyright restrictions; no public source redistribution is authorized by this review. Other article/code/model licences must remain distinct. Qualified human scientific review remains unassigned.
