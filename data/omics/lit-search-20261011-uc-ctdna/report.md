# Literature pass uc-ctdna: plasma ctDNA fragmentomics and methylation, 2026-10-11

Use cases: `use-case-plasma-ctdna-fragmentomics` and `use-case-plasma-ctdna-methylation`. Window 2025-10-01 to 2026-10-11. Budget about 30 queries per use case; 26 searches and lookups used (`ledger.jsonl`), 22 papers screened in `scope-audit.jsonl`. Worker: Claude (Opus 5.5) research agent uc-ctdna. Nothing here is reviewed; every record is `needs_review`. Worktree branch `claude/lit-20261011-uc-ctdna`.

Before searching I read both use-case records, their judgements and summaries, the 2026-10-09 dossiers, the three earlier batches (`use-case-coverage-ctdna-fragmentomics-20261009`, `-methylation-20261009`, `-jamshidi-20261010`) and their 27 ledger entries. No logged query was repeated, and stored sources (DecoNFlow, LIONHEART, the ctDNA mutation-calling benchmark, the conversion-chemistry comparisons) were skipped.

## Extracted

Five batches, 1,196 records, 906 results. All pass the store's vocabulary, attribute, derivation and relation validators against the current store (dry run of `records add`; nothing added).

| Batch | Source | Use case | Records | Results | Judgements |
| --- | --- | --- | --- | --- | --- |
| `use-case-coverage-ctdna-zeng2026-20261011` | Zeng et al. 2026, Nature Cancer: cfMeDIP-seq methylation vs fragmentomic feature sets of the same reads, Source Data Fig. 4 (all 8 sheets) | both | 107 | 52 | 4 methylation, 2 fragmentomics |
| `use-case-coverage-ctdna-helzer2025-20261011` | Helzer et al. 2025, Nature Communications: 13 fragmentomic metrics and Griffin on targeted cfDNA panels, Supplementary Tables S1-S2 (all cells) | fragmentomics | 938 | 790 | 2 |
| `use-case-coverage-ctdna-fragmentia2026-20261011` | Fragmentia-AI, Cell Reports Medicine 2026: cfDNA language model vs six fragmentomic feature sets x three classifiers on ULP-WGS, Table S5 | fragmentomics | 67 | 19 | 1 |
| `use-case-coverage-ctdna-fragmentiawgs2026-20261011` | Fragmentia-AI WGS, Molecular Biomedicine 2026: AUC and fixed-cutoff sensitivity by ichorCNA tumour fraction, Results text and Table S4 | fragmentomics | 53 | 30 | 3 |
| `use-case-coverage-ctdna-cpgpt2026-20261011` | Xu and Feng 2026, medRxiv: fine-tuned CpGPT vs four classical classifiers on cfDNA targeted methylation, Table 3 | methylation | 31 | 15 | 1 |

Add order matters: Helzer (adds the generic Griffin method), then Fragmentia-AI (uses it; adds the Fragmentia-AI method), then Fragmentia-AI WGS (uses that). Zeng and CpGPT are independent. Each batch has `use-case-links.json` with the proposed `assessed_by` links, to apply after review.

Ranking, as the task asked: Zeng first (same-sample methylation vs fragmentomics comparison at 99% specificity with an independent validation set; fills a gap in both use cases), Helzer second (largest multi-metric comparison, mostly other groups' metrics, two cohorts), Fragmentia-AI third (the only foundation-model vs fragmentomic-baseline head-to-head), Fragmentia-AI WGS fourth (second tumour-fraction-stratified study, large independent test set, single model), CpGPT fifth (the only methylation foundation model with conventional comparators; small and leaky).

## Candidates not extracted

| Source | Why not |
| --- | --- |
| Fate-AI, bioRxiv 10.1101/2025.10.20.683167 (CC BY) | Compares fragmentomics plus cfMeDIP features with DELFI, Griffin and ichorCNA on several cohorts and a melanoma dilution series, but per-method values are only text summaries (some averaged over six cancer types) and heatmaps; no supplementary tables. Worth a later pass if the authors publish tables. |
| DNAmBERT, Brief Bioinform 2026 (bbag455) | Table 3 compares DNAmBERT with DISMIR on read-level classification; read-level rather than patient-level, developer study. |
| MOCDT, Bioinformatics 2026 (btag274) | Table 1 compares cancer detection and tissue of origin with three multi-omics graph models; cohort modalities not checked within budget. |
| DeepFRAG, Bioinform Adv 2026 (vbag024) | Table 2: 73 cancers and 80 healthy, feature variants of one developer method. |
| PANGEM, medRxiv 2026 | Baseline values only in figures. |
| Fragmentia-AI panel results (Tables S1-S3, MRD cohorts) | Single model, outside the comparison. |
| Zeng et al. Supplementary Tables 22-23 and Fig. 5 | Per-cancer-type accuracy and cancer-type classifiers; left to keep the batch bounded. |

Two reference-material papers (artificial cfDNA reference standards, bioRxiv 2026; NIST and LGC methylated cfDNA candidate reference materials, Clinical Epigenetics 2026) are possible truth sets for analytical validation but carry no named-method results; they were not added as `discovered` records because neither defines a benchmark protocol for computational workflows. A reviewer may disagree.

## Gaps that remain

- Fragmentomics: still no independent dilution-series or limit-of-detection comparison of fragmentomic tools with printed values (Helzer's in silico mixing and Fate-AI's dilutions are figure-only). Still no cancer-test specificity in patients with inflammatory, autoimmune or vascular disease. Tumour-fraction-stratified evidence now comes from two developer studies (UNITE and Fragmentia-AI WGS); neither stratum is a measured tumour fraction.
- Methylation: still no same-sample detection comparison of methylation assays (cfMeDIP-seq, WGBS, EM-seq, targeted bisulfite), and no independent methylation-only tissue-of-origin comparison on patient plasma. Zeng et al. add a same-sample methylation vs fragmentomics comparison, but from one assay and one group.
- Search: Europe PMC hit counts were large (80 to 933); only the first 60 by relevance were screened per query. Science Translational Medicine full text was not served. Meta-analyses were not followed to every primary study.

## What needs a reviewer's judgement

1. Zeng: Source Data prints 0.694 for the methylation-only validation AUC where the text prints 0.674 (evidence concern on the Source Data source). Three validation AUCs are below 0.5 (motif-containing classifiers; flagged `source_anomaly`); consider excluding those evaluations from the validation judgements. Validation size is 95 in the text and 140 in a legend. Sensitivity spreads are headed sd but the legend says s.e. (`unresolved_spread`). LFS carriers without cancer count as cancer in sensitivity summaries.
2. Zeng relevance for methylation: recorded `proxy`; it is close to `direct` (declared 99% specificity on plasma).
3. Helzer: the article swaps the S1/S2 labels relative to the PDF captions; locators follow the PDF. Origin split (`author_reported` for the authors' entropy metrics and the combined model, `independent_paper` for the rest) needs confirming. Only the two full-panel protocols are mapped; decide whether the commercial-panel subsets should be.
4. Fragmentia-AI: held-out split not described; the same paragraph gives 0.956 and 0.97 for the same-platform AUC; p-value test not named; four baseline feature sets are not defined in the paper.
5. Fragmentia-AI WGS: sensitivity at a cutoff transferred from training is stored as `recall` with the cutoff in the qualifier, not as a sensitivity-at-specificity concept; confirm. The DELFI cohort overlaps the DELFI 2019 samples behind stored evidence.
6. CpGPT: features selected on all 300 samples including test partitions; test sets of about 30. Origin `independent_paper` for CpGPT and `author_reported` for the baselines.
7. Griffin method reuse across two batches, and Fragmentia-AI WGS reusing the Fragmentia-AI method record (same company, same architecture family), create add-order dependencies.

## Proposed summary text

Drafts only, for the reviewer to approve; the existing summary claims are not edited. Each would be appended to the current summary of its use case, before its final sentence about comparability. Numbers trace to the results named in brackets.

**Fragmentomics.** Zeng et al. 2026 (Nature Cancer), by the cfMeDIP-seq developers, computed fragmentomic features from cfMeDIP-seq reads of the same plasma samples and report means over 10 fold models. On an independent paired-end validation set, a fragment-ratio classifier reached AUC 0.848 and detected 0.533 of cancers at 99% specificity, and fragment ratios combined with methylation 0.954 and 0.766; models with end motifs fell below 0.5, which the authors attribute to healthy controls processed with a different protocol [zeng2026 pe-validation results]. Helzer et al. 2025 (Nature Communications) applied thirteen published fragmentomic metrics and Griffin to targeted exon-panel data from metastatic cancers with one classifier and shared folds; the healthy-versus-cancer one-vs-rest AUROC ranged from 0.835 (open-chromatin entropy) to 0.989 (first-exon depth) in 431 UW samples, with Griffin at 0.944, and from 0.951 to 1.000 in 198 public GRAIL panel samples [helzer2025 uw-full and grail-full 'Normal' results]. In a developer comparison on 0.1x ULP-WGS (Cell Reports Medicine 2026), a fragment-level language model (Fragmentia-AI) reached AUC 0.9561 on a held-out set against 0.9209 to 0.935 for re-implemented DELFI features and 0.881 to 0.8863 for Griffin features under three classifiers [fragmentia2026 results]. The same company's whole-genome model, on an independent test cohort of 5,996 samples, reached AUC 0.910 for cancers with an ichorCNA tumour fraction below 3% and detected 0.46 of them at a cutoff set to 98% specificity in training (observed test specificity 0.97); among those low-fraction cancers it detected 0.391 at stage I/II (637 of 1,628) and 0.708 at stage III/IV (345 of 487) [fragmentiawgs2026 test results and Table S4]. All four are retrospective case-control studies; three are developer studies, and the panel study uses targeted panels rather than whole-genome sequencing.

**Methylation.** Zeng et al. 2026 (Nature Cancer), by the cfMeDIP-seq developers, compared a cfMeDIP-seq methylation classifier with fragmentomic features of the same reads. In cross-validation on 356 cancers and 64 healthy donors, methylation alone reached AUC 0.986 and detected 0.949 of cancers at 99% specificity (means over 10 fold models); on an independent validation set its sensitivity at 99% specificity fell to 0.633, against 0.766 for methylation combined with fragment ratios. The Source Data give the methylation-only validation AUC as 0.694 and the text as 0.674 [zeng2026 results; source concern]. Xu and Feng 2026, a medRxiv preprint by authors who did not develop CpGPT, fine-tuned the CpGPT methylation foundation model on targeted bisulfite cfDNA data from 254 gastrointestinal cancers and 46 controls; on three train/validation/test splits of about 30 test samples, mean test AUROC was 0.9904 against 0.9573 (SVM), 0.9420 (elastic net), 0.8460 (gradient boosting) and 0.8408 (random forest), with features selected on all samples including the test partitions [cpgpt2026 results]. Neither study reports performance in a screening population.

## Files

- `ledger.jsonl` (26 entries) and `scope-audit.jsonl` (22 entries) in this folder, for the team lead to merge into the shared files.
- The five batch folders above, each with `batch.jsonl`, `claims.csv`, `coverage.json`, `sources.md`, `retrieval-log.md`, `research.md`, `use-case-links.json` and `extract/` (deterministic scripts; run as `python3 -I extract/<script>.py <download-dir> <batch-dir>`). CC BY article XML is archived for Helzer and Fragmentia-AI WGS; nothing else is archived (licences or size).
- No review receipts: review is for a separate worker.
