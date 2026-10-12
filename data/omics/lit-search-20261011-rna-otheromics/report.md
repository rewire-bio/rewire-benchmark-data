# Literature pass: rna and other-omics lanes, 2026-10-11

Window 2025-10-01 to 2026-10-11, plus a completeness check of well-known suites. Focus: benchmarks of foundation models in RNA and other omics, and independent comparisons of them with conventional methods. This branch combines two passes. The lit-rna-otheromics pass ran 27 searches and 6 lookups. FlexMS and Khoo 2026 come from the lit-rna-other pass (branch claude/lit-20261011-rna-other, commit ef64700). Its duplicate batches for the other four shared sources were dropped. The search log is ledger.jsonl and the include and exclude decisions are scope-audit.jsonl in this folder. All records are needs_review. No batch has been added to the store; that happens after review.

## Extracted

| Batch | Source | Results |
| --- | --- | --- |
| lit-rna-20261011-rnalm-zeroshot | Wang et al. 2026, Brief Bioinform bbag098 (CC BY). Zero-shot benchmark of 21 RNA LMs with DNA LM controls; Supplementary Tables 4-11 | 1190 |
| lit-rna-20261011-rna3d | Ludaic and Elofsson 2026, NAR gkag813 (CC BY). Ten deep learning RNA 3D methods on RNAs released after the training cut-offs; Tables 2-5 and Supplementary S6, S7, S15 | 216 |
| lit-rna-20261011-rnagym | RNAGym official fitness leaderboard v0.1.1 at commit 2828cf9 (MIT). 12 models on 31 ncRNA DMS assays plus an AIDO.RNA scaling series; suite was absent from the store | 64 |
| lit-otheromics-20261011-msgwild | MassSpecGym in the Wild, arXiv:2606.19624v1 (CC BY). Corrected and inflated retrieval and de novo results; Tables 2, 3, 9 | 176 |
| lit-otheromics-20261011-pepspecbench | PepSpecBench, arXiv:2605.01945v1 (arXiv non-exclusive licence, not archived). Six peptide MS/MS predictors, in-domain and cross-species; Tables 2, 4, 14 | 168 |
| lit-rna-other-20261011-zhong2026 | FlexMS, arXiv:2602.22822v4. 33 embedder-predictor combinations for spectrum prediction on MassSpecGym; Table 2 | 66 |
| lit-rna-other-20261011-khoo2026 | Khoo 2026, arXiv:2610.02249v1. Nearest-neighbour fingerprint prediction under three information assumptions on NPLIB1 and MassSpecGym; Tables 1-2 | 128 |

Total: 2008 results. Each batch has batch.jsonl, claims.csv, sources.md, retrieval-log.md, research.md and a deterministic extract/ script that asserts the artifact hashes and table headers. All seven batches validate together against the store: vocabularies, attribute registry, record schema and relations. The SHACL step runs only inside records add and was not run. `npx tsc --noEmit -p .` and `npx vitest run` passed (48 files, 515 tests) before the import; rerun them before the PR.

Order: add lit-rna-20261011-rnalm-zeroshot before lit-rna-20261011-rnagym. The rnagym batch links to the AIDO.RNA and RiNALMo family records the rnalm-zeroshot batch creates.

Vocabulary: four metric concepts added to data/vocab/metric.ttl: one-minus-overlap-ratio, spectral-angle, spectral-angle-similarity and fingerprint-tanimoto-similarity (the last from the lit-rna-other pass).

Use cases: two relevance judgements, rated proxy, for use-case-mass-spectrum-molecule-shortlisting on the MassSpecGym in the Wild mass-based retrieval protocols (Hit rate@1 and @20). They exclude the four rows the paper greys out as leaking. The proposed assessed_by links are in that batch's use-case-links.json and are not applied.

## Not extracted

- CodonBench, bioRxiv 10.64898/2026.08.12.744371 (CC BY). Leakage-controlled codon LM benchmark of high value, but the full-text request was rate-limited (Cloudflare 1015). First candidate for the next pass.
- codlncRNA benchmark, Genome Biol 10.1186/s13059-026-04134-7. Main comparisons are in figures; supplementary tables hold an ablation and per-transcript probabilities with no stated threshold.
- CHANRG, arXiv:2603.22330. Values are in heatmaps only.
- DLDN-Bench and DeNovo-PBI (bioRxiv). Full text not retrieved.
- eFold, Sci Adv adz4967. Developer paper, not a foundation model benchmark.
- JASMS 2026 MS/MS featurization benchmark. Values are in figures and a 19.8 MB CSV that was not analysed.
- bbag329 splicing assessment. Figures only; also excluded on 2026-10-09.
- CASP16 RNA assessments. Structure lane; not open access or no tables.
- Epigenetic clock comparisons and the CpGPT evaluation. Not foundation model benchmarks.
- Reviews. Used as leads only.
- Leads screened in the lit-rna-other pass, with workbooks not opened: Quartet/MAQC splicing 10.1038/s41467-026-76380-z, microprotein MS 10.1038/s41467-025-68002-x, DIA single-cell proteomics 10.1038/s41467-025-65174-4, long-read fusion 10.64898/2026.08.07.743439.
- You et al. 2026, 10.1038/s41467-025-66899-y. Supplementary Tables 2, 3 and 6 are still open; that work is assigned to lit-gfm-2.

## Gaps

- No independent benchmark of DNA methylation, glycan or lipid foundation models was found in the window.
- bioRxiv full texts were unavailable in this session.
- RNAGym structure results were not extracted, and the RNAGym mRNA table is linked from the leaderboard but absent at the pinned commit.
- NovoBench was not checked on its repository.
- Reviews were not followed citation by citation.
- This is a bounded pass, not an exhaustive one.

## For the reviewer

1. rna3d: Tables 2-3 print identical GDT-TS, INF and lDDT for DRfold and DeepFoldRNA, and their supplementary per-target columns are identical too. Table 3 prints RF2NA hard-set INF as 0.668; the mean of its Supplementary S3 column is 0.608. Decide whether these need evidence_concerns.
2. rnalm-zeroshot: RNA-MSM is recorded as author_reported because it comes from the corresponding authors' group. RFamLlama 1 - OR is 0.000 with a non-zero MCC, transcribed as printed. Check that the 14 new family records do not duplicate existing ones.
3. rnagym: confirm that the label "RNA-ERNIE" means RNAErnie (Nature Machine Intelligence 2024), not ERNIE-RNA.
4. msgwild: check the per-row origins (paper_compilation, author_reported, independent_paper) and how the grey rows are handled. The 99.9% confidence level is applied only to the authors' own runs. Decide whether MIST with a MIST-CF predicted formula falls under the use case's exclusion of formula-conditioned retrieval.
5. pepspecbench: the area proteins-complexes stands in because the vocabulary has no proteomics area. PredFull's PROSPECT SA prints as 0.204 in Table 2 and 0.203 in Table 4.
6. The NAR PDF and bbag098 .docx sources hash the file inside the Europe PMC supplementaryFiles zip.
7. zhong2026 and khoo2026 were extracted by lit-rna-other and only copied in here unchanged; their record IDs use the prefix lit20261011-.

## After review (2026-10-12)

reviewer-ro-1 reviewed rnalm-zeroshot, rnagym, rna3d and the metric concepts; reviewer-ro-2 reviewed msgwild, pepspecbench, khoo2026 and zhong2026. All seven batches were approved, five with corrections. Each batch folder has the reviewer's report and the corrections applied in review.md, and the receipt in review.json. The summary is docs/reviews/2026-10-12-rna-other-omics-batches.md.
