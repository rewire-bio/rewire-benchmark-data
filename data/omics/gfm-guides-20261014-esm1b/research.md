# Research notes

Batch for rewire-benchmark-data issue #129 (genomic foundation model guide fixes): find a primary source that prints ESM-1b coding-variant pathogenicity performance and extract it.

## Decisions

- Source: Brandes et al. 2023, Nature Genetics (open access, CC BY 4.0). Its Supplementary Table 2 holds the values behind Figure 2e,f; the Results quote the ESM1b versus EVE ROC-AUCs.
- AlphaMissense (Cheng et al. 2023) was not retrieved in this pass; the GPN-MSA preprint prints one ESM-1b number (DMS TADBP AUROC), which is in `gfm-guides-20261014-gpnmsa`.
- Scope: the missense pathogenicity benchmarks only. From Supplementary Table 2, sheets `Table_of_results_ClinVar` and `Table_of_results_HGMD`, columns `AUC_AUROC` and `AUC_Balanced_AUPRC` for the 19 methods the authors judged eligible for clinical benchmarking (all rows with values in those columns), on the shared variant set (n_var 12,095 and 12,357). The head-to-head columns and the other sheets are recorded as gaps below.
- The existing ESM-1b model `uc20260930-model-esm-1b` is reused. The ESM1b configuration names the checkpoint the paper used (esm1b_t33_650M_UR50S) and its long-protein sliding-window scoring.
- Existing method and model records are reused for the comparators: `uc20260930-model-eve`, `somatic-oncogenicity-20261009-method-{sift, provean, mutationassessor, phylop, lrt, gerp, phastcons, genocanyon, bstatistic, integrated-fitcons}` and `brca-20261009-method-siphy`. SIFT4G maps to the SIFT method, as in `somatic-oncogenicity-20261009-config-lee2026-sift4g`. The three phyloP and three phastCons rows (vertebrate, mammalian, primate) are separate configurations of the one phyloP or phastCons method. MTBAN had no record and is a new method.
- No ClinVar dataset in the store matches this one (ClinVar labels with at least one gold star from the EVE portal, primary isoforms), and no HGMD/gnomAD dataset exists, so both are new.
- Origin: author_reported for ESM1b (the authors' workflow); independent_paper for the comparators.

## Record counts

- benchmark: 1
- configuration: 19
- dataset: 2
- evaluation: 42
- method: 1
- protocol: 4
- result: 80
- source: 3

Reused IDs: `uc20260930-model-esm-1b`, `uc20260930-model-eve`, `brca-20261009-method-siphy`, `somatic-oncogenicity-20261009-method-bstatistic`, `somatic-oncogenicity-20261009-method-genocanyon`, `somatic-oncogenicity-20261009-method-gerp`, `somatic-oncogenicity-20261009-method-integrated-fitcons`, `somatic-oncogenicity-20261009-method-lrt`, `somatic-oncogenicity-20261009-method-mutationassessor`, `somatic-oncogenicity-20261009-method-phastcons`, `somatic-oncogenicity-20261009-method-phylop`, `somatic-oncogenicity-20261009-method-provean`, `somatic-oncogenicity-20261009-method-sift`. Every new record has status `needs_review`.

Note on the store: besides the DeepProtein and ProteinGym evaluations, ESM-1b already has three missense evaluations through `somatic-oncogenicity-20261009-config-lee2026-esm1b` (Lee 2026, CGC somatic oncogenicity; negatives are ClinVar benign and gnomAD common variants). This batch adds the first germline pathogenicity evaluations.

## Extraction note for the reviewer

Tables and passages extracted:

1. Supplementary Table 2, sheet `Table_of_results_ClinVar`, rows 2-20 (19 methods), columns B (`AUC_AUROC`) and C (`AUC_Balanced_AUPRC`): 38 results. Method: deterministic parse of the pinned workbook with the stdlib OOXML reader in `extract/build_esm1b.py`; header, n_var (12095), the `included` flag and the 19 labels asserted.
2. Supplementary Table 2, sheet `Table_of_results_HGMD`, the same rows and columns (n_var 12357): 38 results. Same method.
3. Results, section "ESM1b outperforms other VEP methods over clinical and experimental benchmarks", paragraph 2: ESM1b 0.905 and EVE 0.885 on ClinVar (36,537 variants), ESM1b 0.897 and EVE 0.882 on HGMD/gnomAD (30,497 variants): 4 results. Method: transcription from the JATS text, sentences asserted verbatim.
4. Supplementary Methods, "Clinical benchmarks of missense variants": dataset construction (ClinVar from the EVE portal; HGMD DM; gnomAD v2.1.1 MAF > 0.01; 92,942 HGMD/gnomAD variants on primary isoforms). Method: transcription into dataset records.

Gaps (not extracted):

- Supplementary Table 2 head-to-head columns E-I (each method against ESM1b on the variants it scores) for all 45 comparators, in both clinical sheets, including the 27 methods excluded from the clinical comparison for training on clinical data or using allele frequency. About 360 cells.
- Sheet `Table_of_results_DMS` (Spearman correlation with DMS measurements; protein function, not pathogenicity).
- Sheets `Table_of_results_indels` (ClinVar in-frame indels: ESM1b-aPLLR, PLLR, wPLLR, CADD and three baselines) and `Table_of_results_stop_gains` (ClinVar stop-gains by NMD status). These are ESM1b coding-variant pathogenicity results and the obvious next extraction.
- Extended Data Fig. 1 (true-positive rate at 5% false-positive rate, quoted in the Results as 60% versus 49% on ClinVar and 61% versus 51% on HGMD/gnomAD) and gene-average ROC-AUC: not extracted.
- Figures 2e-h, 3 and 6 were not read.

Needs reviewer judgement:

- The Results quote ESM1b 0.905 and EVE 0.885 on 36,537 ClinVar variants, and 0.897 and 0.882 on 30,497 HGMD/gnomAD variants. Supplementary Table 2's EVE head-to-head row gives ESM1b 0.906018 and EVE 0.885312 on 36,522 ClinVar variants, and ESM1b 0.897926 and EVE 0.883988 on 30,483 HGMD/gnomAD variants. The text values are extracted as printed and the difference is recorded in the article source's limitations. The reviewer may prefer to add an `evidence_concerns` entry on the article source, which would block automatic comparison of the four text results.
- EVE's score source is not stated (only that most other methods come from dbNSFP 4.3a). EVE is given method type `specialist`; check that this matches how the store classifies EVE elsewhere.
- 'fitCons' is taken to be integrated fitCons, because the Methods say the three cell-line fitCons versions were excluded. It is linked to `somatic-oncogenicity-20261009-method-integrated-fitcons`.
- Balanced PRC-AUC is stored as metric `auprc` with a qualifier describing the balancing (100 downsamples to equal classes at 80% of the minority class). It is not comparable with an ordinary AUPRC on imbalanced data.
- The HGMD/gnomAD dataset depends on licensed HGMD data and cannot be rebuilt from public files.
