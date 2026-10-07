# Current-source review: original cases 13–17

Original 17 use cases sorted alphabetically by ID, positions 13–17. Five bounded source families and five exact fresh numeric endpoints confirmed. Existing IDs retained; no results duplicated.

## Prioritise variants for splicing experiments

Existing result `rewire-mfass-matched-v1-result-s0-auroc`: 0.8035576794956798 dimensionless. Current numeric check: confirmed.

/conditions/S0/metrics/auroc

Fresh pinned JSON matches the prior SHA-256. S0 AUROC is 0.8035576794956798; 8,297 of 8,324 variants scored, with 314 positives. Reporter splice disruption is proxy evidence for follow-up, not patient RNA or pathogenicity. No new run.

Current primary source ID `rewire-mfass-matched-v1-source-report`; retrieval {'name': 'splicing', 'url': 'https://raw.githubusercontent.com/rewire-bio/rewire-benchmarks/093fd1ae198c80ce34408d84d6543bca4fc538f2/benchmarks/mfass/results/matched-annotation-v1/report.json', 'retrieved_at': '2026-10-07T12:34:04.643276+00:00', 'status': 200, 'bytes': 29614, 'sha256': '259eb542313914b9114c21b62891f022c0ec0d9e3337196b8d7b2c6d5ae54ef3'}

Version/correction: {'pinned_version': '093fd1ae198c80ce34408d84d6543bca4fc538f2', 'byte_hash_unchanged': True, 'latest_default_branch_checked': False}

Active mappings: ['use-case-mapping-20260930-339-25925e279972', 'use-case-mapping-splicing-mfass-matched-v1']; inventory: 6 evaluations, 22 results. No duplicated results.

Gaps retained: ['All four conditions scored 8,297 of 8,324 held-out variants. The same 27 exclusions comprise 23 hg19-to-hg38 assembly-orientation mismatches and four canonical-transcript-span exclusions; the latter are not established faulty variants. Missing predictions are not negative predictions.', "No top-100 precision difference is established; Pangolin's masked top-100 result is sensitive to the registered tie order. Precision at 100 does not transfer automatically to another follow-up capacity or prevalence.", "Individual-condition uncertainty intervals are not recorded. Paired-contrast intervals concern differences between conditions and must not be shown as each condition's uncertainty.", 'The study is exploratory: prior outcomes were inspected and nine contrast intervals are unadjusted. Matching annotation does not isolate model architecture.', 'Author confirmation of the assembly-orientation finding is not established. Human scientific review and independent replication remain outstanding.', "These mappings do not change the MFASS task's discovered status. A source-reviewed applicability mapping is separate from reviewing the task record.", '30 September 2026 audit: The four matched conditions exclude the same 27 of 8,324 held-out variants; missing scores are not negative predictions.', '30 September 2026 audit: Historical v2 marginal scores have different scored subsets/annotations and require their own paired comparisons. Constant-prior top-100 counts reflect tied-score order. DNABERT2 is a pipeline rather than an exact configuration and remains outside the active mapping.', '30 September 2026 audit: MFASS reporter exon inclusion does not validate patient RNA, diagnosis or prospective clinical follow-up. Human scientific review and external reproduction remain outstanding.']

Runner links: ['/benchmarks/runs/mfass-v2/', 'https://github.com/rewire-bio/rewire-benchmarks/blob/093fd1ae198c80ce34408d84d6543bca4fc538f2/benchmarks/mfass/results/matched-annotation-v1/README.md', 'https://github.com/rewire-bio/rewire-benchmarks/blob/093fd1ae198c80ce34408d84d6543bca4fc538f2/benchmarks/mfass/results/matched-annotation-v1/report.json', 'https://github.com/rewire-bio/rewire-benchmarks/blob/1663d1f04b2bbd6dfcff77fea78129d30b0de191/research/mfass-null-2026-09-21/README.md', 'https://github.com/rewire-bio/rewire-benchmarks/blob/1663d1f04b2bbd6dfcff77fea78129d30b0de191/research/mfass-null-2026-09-21/evidence/training-prior.report.json', 'https://github.com/rewire-bio/rewire-benchmarks/blob/f80cef7f818bec33e51b7f43ad499eb5078c8d87/docs/mfass.md', 'https://github.com/rewire-bio/rewire-benchmarks/blob/f80cef7f818bec33e51b7f43ad499eb5078c8d87/packages/rewirebench/src/rewirebench/protocols/mfass.py']

Article/source links: ['https://github.com/rewire-bio/rewire-benchmarks/blob/093fd1ae198c80ce34408d84d6543bca4fc538f2/benchmarks/mfass/results/matched-annotation-v1/manifest-v1.json', 'https://github.com/rewire-bio/rewire-benchmarks/blob/093fd1ae198c80ce34408d84d6543bca4fc538f2/benchmarks/mfass/results/matched-annotation-v1/provenance.json', 'https://github.com/rewire-bio/rewire-benchmarks/blob/093fd1ae198c80ce34408d84d6543bca4fc538f2/benchmarks/mfass/results/matched-annotation-v1/report.json', 'https://github.com/rewire-bio/rewire-benchmarks/blob/093fd1ae198c80ce34408d84d6543bca4fc538f2/benchmarks/mfass/results/matched-annotation-v1/verification.json', 'https://github.com/rewire-bio/rewire-benchmarks/blob/1663d1f04b2bbd6dfcff77fea78129d30b0de191/research/mfass-null-2026-09-21/README.md', 'https://github.com/rewire-bio/rewire-benchmarks/blob/1663d1f04b2bbd6dfcff77fea78129d30b0de191/research/mfass-null-2026-09-21/evidence/training-prior.report.json', 'https://github.com/rewire-bio/rewire-benchmarks/blob/1663d1f04b2bbd6dfcff77fea78129d30b0de191/research/mfass-null-2026-09-21/evidence/verification.json', 'https://github.com/rewire-bio/rewire-benchmarks/blob/4be7a98e2553fa2378c29625b13eb3e8ac2e58fb/docs/mfass-matched-study-exclusions/verification.json', 'https://github.com/rewire-bio/rewire-benchmarks/blob/f80cef7f818bec33e51b7f43ad499eb5078c8d87/docs/mfass.md', 'https://github.com/rewire-bio/rewire-benchmarks/blob/f80cef7f818bec33e51b7f43ad499eb5078c8d87/packages/rewirebench/src/rewirebench/protocols/mfass.py', 'https://github.com/timini/rewire-benchmarks/tree/bee9133b83f3aedaf2bbb9013f1875515845607e']

## Choose structural hypotheses to guide experiments

Existing result `ucc-docking-cluspro-bm5-2020-result-others-top10-count`: 27 targets. Current numeric check: confirmed.

Table 1 Others first (top 10) row / Good models Number

Fresh primary HTML confirms 27 targets among 101 evaluable Others targets (102 attempted). DockQ >= 0.23; ClusPro Others mode; unbound partner structures. Structure quality is proxy evidence and establishes no binding, affinity or causal validation.

Current primary source ID `ucc-docking-cluspro-bm5-2020-source`; retrieval {'name': 'docking-html', 'url': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC7484347/', 'retrieved_at': '2026-10-07T12:35:08.814437+00:00', 'status': 200, 'bytes': 239056, 'sha256': '27ae227290cc1b2615fb2aef1907acb3641c7d3d789e23755df58fa11ca4d42c'}

Version/correction: {'queries_at': '2026-10-07T12:33:46Z', 'outcome': 'No correction surfaced in bounded returned search results; absence is not certified.'}

Active mappings: ['use-case-mapping-20260930-350-54e8c47f1c29', 'use-case-mapping-20260930-350-746ab300cdfe', 'use-case-mapping-20260930-350-85c0ffafe7cd', 'use-case-mapping-20260930-350-ae963dc25ccb', 'use-case-mapping-20260930-350-d7a6088b3a59']; inventory: 9 evaluations, 64 results. No duplicated results.

Gaps retained: ['Automated source review only; independent human scientific review remains outstanding.', 'No intervals in Table 3; no prospective experimental utility or matched conventional mutation/construct baseline.', 'Scored target populations differ; Table 1 assessable counts are retained as coverage context, not verified metric denominators. Some Table 3 rates do not reconcile with integer counts after rounding. No complete-cohort estimate is inferred.', 'ClusPro uses component 3D structures and BM5 targets, so scores cannot be directly compared with FoldBench; BM4 parameter benchmarking limits holdout independence. Exact ClusPro revision and input hashes remain unextracted.', 'ClusPro Total/easy/top10 source prints 87 although subtotals and 51.68% imply 77; literal 87 is retained as needs_review outside use-case mappings. Antibody and aggregate classes are not mapped to this issue.']

Runner links: []

Article/source links: ['https://pmc.ncbi.nlm.nih.gov/articles/PMC7484347/', 'https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-67127-3/MediaObjects/41467_2025_67127_MOESM1_ESM.pdf', 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12800276/fullTextXML']

## Select therapeutic targets for validation

Existing result `ucc-research-result-cppc-table-s2-d-row-2-robust-topk-overlap-auc`: 0.519114225709815 score. Current numeric check: confirmed.

Supplementary Table S2 media-3.xlsx sheet Challenge 1 & 2 cell D2

Fresh supplementary ZIP access succeeded on the bounded retry. The media-3.xlsx member SHA-256 matches the prior reviewed source exactly. Sheet Challenge 1 & 2, cell D2 stores 0.519114225709815. Primary XML also matches the prior SHA-256; bioRxiv API returns version 1 (2026-05-22), published=NA. Mouse T-cell Perturb-seq prediction is proxy evidence for target nomination, not clinical efficacy. The full supplementary ZIP and workbook were discarded after extracting this numeric cell because other fields contain contributor contact details.

Current primary source ID `ucc-research-source-challenge-paper`; retrieval {'name': 'cppc', 'url': 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13228547/fullTextXML', 'retrieved_at': '2026-10-07T12:34:04.643637+00:00', 'status': 200, 'bytes': 237539, 'sha256': '6c98a7d0f0ab7abff1c76a7f184382a10ca82c39b34879b83d205a994412aa22'}

Version/correction: {'queries_at': '2026-10-07T12:33:46Z', 'outcome': 'No correction surfaced in bounded returned search results; absence is not certified.', 'current_primary_api_version': '1', 'date': '2026-05-22', 'published': 'NA', 'api_artifact': 'cppc-versions.raw.gz', 'supplement_member_hash_unchanged': True}

Active mappings: ['use-case-mapping-20260930-346-15b6eed3fb55', 'use-case-mapping-20260930-346-910458dfd409']; inventory: 21 evaluations, 21 results. No duplicated results.

Gaps retained: ['61 nominations / Results 57 selected targets / README 59 targets / 50 post-QC perturbations need reconciliation; no success fraction calculated.', 'Automated source review only; independent human scientific review remains outstanding.', 'Custom ranking AUC is not ROC AUC, prospective hit rate or efficacy.', 'No matched-budget conventional/random prospective comparison; no antitumor efficacy, rescue or selectivity result in this endpoint.', 'Original model implementations/checkpoints are not pinned in the intake; no uncertainty printed.', 'Preprint v1; original and reimplemented ranking scores kept separate. Screen2 ranking population is enriched by original nomination methods.']

Runner links: []

Article/source links: ['https://raw.githubusercontent.com/uhlerlab/cancer_immunotherapy_data_science_challenge/283328a9b8afc6e882eeb503ac4710bbe9f37371/README.md', 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13228547/fullTextXML', 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13228547/supplementaryFiles']

## Reanalyse unresolved rare-disease cases

Existing result `uc-clinical-20260930-reanalysis-additional-diagnostic-yield`: 5.1% percent. Current numeric check: confirmed.

Results / Iterative reanalysis / paragraph beginning Review of Talos output

Fresh publisher HTML prints 5.1% additional yield: 241 new diagnoses in 238 individuals from 4,735 unresolved individuals, including three dual diagnoses. Preserve the rounded percentage and diagnosis/person distinction. Cohort-specific accredited-laboratory classification supports direct reanalysis evidence; no comparative winner.

Current primary source ID `uc-clinical-20260930-source-talos`; retrieval {'name': 'talos', 'url': 'https://www.nature.com/articles/s41591-026-04477-5', 'retrieved_at': '2026-10-07T12:34:04.643721+00:00', 'status': 200, 'bytes': 582433, 'sha256': 'd8b4024e46ee817db94fcd6c59d63225ca1d07ca2fc0bfc09807ead0117ac263'}

Version/correction: {'queries_at': '2026-10-07T12:33:46Z', 'outcome': 'No correction surfaced in bounded returned search results; absence is not certified.'}

Active mappings: ['use-case-mapping-20260930-342-3c7f6c5e1873']; inventory: 1 evaluations, 14 results. No duplicated results.

Gaps retained: ['Equal updated calls, phenotypes and knowledge with matched review effort are not established in the extracted peer-reviewed programme.', 'A 2026 medRxiv automated-versus-manual comparison was discovered (10.64898/2026.05.16.26352295); full text retrieval failed with HTTP403 and indexed percentages conflict between text and caption. No measurements imported from that preprint.', 'False alerts, review time, retracted diagnoses and source denominator inconsistencies need adjudication.', 'Qualified human scientific review remains outstanding; automated source transcription does not establish experimental replication.']

Runner links: []

Article/source links: ['https://www.nature.com/articles/s41591-026-04477-5']

## Set baselines for UTR translation experiments

Existing result `uc20260930-framepool-result-random-25-100nt-optimus-50`: 0.743 correlation. Current numeric check: confirmed.

S1 Table cell B3 / Random 25–100 nt / Optimus 50

Fresh XLSX cell B3 stores numeric 0.743; the supplement SHA-256 is identical. This is Pearson correlation on MPRA random 25–100 nt 5′ UTRs. Reporter translation is proxy evidence for endogenous expression, not therapeutic or clinical efficacy. Uncertainty is unreported.

Current primary source ID `uc20260930-source-framepool-s1`; retrieval {'name': 'utr-supp', 'url': 'https://journals.plos.org/ploscompbiol/article/file?type=supplementary&id=10.1371/journal.pcbi.1008982.s020', 'retrieved_at': '2026-10-07T12:34:05.542694+00:00', 'status': 200, 'bytes': 5227, 'sha256': '4ed99aebadc607b43fca67bc2c6336cf4f167cc4b9cdd57b0abfcad0d2a06562'}

Version/correction: {'queries_at': '2026-10-07T12:33:46Z', 'outcome': 'No correction surfaced in bounded returned search results; absence is not certified.', 'article_and_supplement_hash_unchanged': True}

Active mappings: ['use-case-mapping-20260930-340-9c66a82c516b', 'use-case-mapping-20260930-340-b6a5b397be2c', 'use-case-mapping-20260930-340-f41565cc8be6', 'use-case-mapping-20260930-340-fe382f327cba', 'use-case-mapping-utr-translation-baselines-designed-v1']; inventory: 32 evaluations, 36 results. No duplicated results.

Gaps retained: ['Only two procedural controls have been evaluated here; no pretrained model or more complex sequence model has a matched result in this protocol.', 'There is one split and one execution per configuration, with no uncertainty interval or seed-variability estimate. The split does not establish homology separation or compositional generalisation.', 'RidgeCV uses training labels only and leaves the validation split unused. This differs from upstream probing; the selected test MSE must not be compared as if it were the paper’s aggregated Pearson score or default validation result.', 'The training-mean control has undefined Pearson and Spearman correlations because its predictions are constant. Unavailable correlations are not zero performance scores.', 'The original run’s raw inputs and saved predictions are not publicly archived. The public reports record hashes and a recipe for obtaining source data and running the controls again; prior predictions cannot be rescored from those reports. Dataset reuse terms are unreported.', 'The recorded repeat recipe executes all four local sequence controls, including a separate protein dataset. Portable command examples have not been rerun verbatim during this review. Timings cover the reported calculation sections, not complete setup or cross-machine performance.', '30 September 2026 audit: FramePool/Sample random and truncated-human libraries differ from the locally evaluated mRNABench designed-MRL split. Learned results exist for the use case, but no new result fills that exact local protocol gap.', '30 September 2026 audit: Sequence-length transfer is measured; Pearson correlation does not establish absolute calibration, design success, therapeutic translation or full-length endogenous prediction.', '30 September 2026 audit: Local protocol raw predictions/input reuse terms remain unresolved; supplementary tables do not establish permissions for those separate inputs.', '30 September 2026 audit: Per-configuration uncertainty and exact human cohort denominators remain unextracted.']

Runner links: ['https://github.com/rewire-bio/rewire-benchmarks/blob/ca73fa47136d182f2d4ddb083d084712198fc0e2/research/local-runs-2026-09-20/README.md', 'https://github.com/rewire-bio/rewire-benchmarks/blob/ca73fa47136d182f2d4ddb083d084712198fc0e2/research/local-runs-2026-09-20/mrnabench-composition/report.json', 'https://github.com/rewire-bio/rewire-benchmarks/blob/ca73fa47136d182f2d4ddb083d084712198fc0e2/research/local-runs-2026-09-20/mrnabench-train-mean/report.json']

Article/source links: ['https://github.com/rewire-bio/rewire-benchmarks/blob/ca73fa47136d182f2d4ddb083d084712198fc0e2/research/local-runs-2026-09-20/README.md', 'https://github.com/rewire-bio/rewire-benchmarks/blob/ca73fa47136d182f2d4ddb083d084712198fc0e2/research/local-runs-2026-09-20/mrnabench-composition/report.json', 'https://github.com/rewire-bio/rewire-benchmarks/blob/ca73fa47136d182f2d4ddb083d084712198fc0e2/research/local-runs-2026-09-20/mrnabench-train-mean/report.json', 'https://journals.plos.org/ploscompbiol/article/file?type=supplementary&id=10.1371/journal.pcbi.1008982.s020', 'https://journals.plos.org/ploscompbiol/article/file?type=supplementary&id=10.1371/journal.pcbi.1008982.s023', 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8136849/fullTextXML']
