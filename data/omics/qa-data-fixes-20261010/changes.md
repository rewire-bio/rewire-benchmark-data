# Changes: QA data fixes, issue #87 summaries, 2026-10-10

Drafted by a Claude (Opus 5.5) research agent. No human review claimed. Each summary is built only from the active relevance judgements of its use case and the source_checked results those judgements point at, read through deriveUseCaseInputs. No value was recomputed, rounded further or pooled across protocols.

## New records

Five claim records in batch.jsonl, all `status: needs_review`, `attributes.field` `summary`, with a `subject` link to the use case. No pins and no review object: a draft summary is not published, and the reviewer adds the pins.

| Claim | Use case | Sources |
| --- | --- | --- |
| use-case-summary-utr-translation-baselines | use-case-utr-translation-baselines | 7 |
| use-case-summary-plant-promoter-reporters | use-case-plant-promoter-reporters | 3 |
| use-case-summary-mass-spectrum-molecule-shortlisting | use-case-mass-spectrum-molecule-shortlisting | 2 |
| use-case-summary-phenotype-perturbation-selection | use-case-phenotype-perturbation-selection | 2 |
| use-case-summary-rhodopsin-wavelength-transfer | use-case-rhodopsin-wavelength-transfer | 9 |

## Result IDs behind each number

### use-case-summary-utr-translation-baselines

- mean squared error 1.914 and 2.366
  - `rewire-local-20260920-result-mrnabench-composition-mse`
  - `rewire-local-20260920-result-mrnabench-train-mean-mse`
- Pearson 0.437; undefined for the constant control
  - `rewire-local-20260920-result-mrnabench-composition-pearson`
  - `rewire-local-20260920-result-mrnabench-train-mean-pearson`
- neural models 0.743 to 0.966 on random panels
  - `uc20260930-framepool-result-random-25-100nt-optimus-50`
  - `uc20260930-framepool-result-random-50nt-optimus-50`
- neural models 0.700 to 0.894 on human panels
  - `uc20260930-framepool-result-human-25-100nt-optimus-50`
  - `uc20260930-framepool-result-human-25-100nt-framepool-combined`
- k-mer random forests 0.616 to 0.877
  - `uc20260930-framepool-result-random-25-100nt-3mer-random-forest`
  - `uc20260930-framepool-result-random-50nt-frame-forest-4mer`

### use-case-summary-plant-promoter-reporters

- AgroNT 0.62 to 0.75
  - `agront-2024-fig3e-result-agront-promoter-strength-maize-protoplasts-maize-protoplasts-a-thaliana-r2`
  - `agront-2024-fig3e-result-agront-promoter-strength-tobacco-leaves-tobacco-leaves-z-mays-r2`
- CNN 0.57 to 0.73
  - `agront-2024-fig3e-result-cnn-jores-et-al-promoter-strength-tobacco-leaves-tobacco-leaves-a-thaliana-r2`
  - `agront-2024-fig3e-result-cnn-jores-et-al-promoter-strength-tobacco-leaves-tobacco-leaves-z-mays-r2`
- Jores CNN 0.67 and 0.71; linear model 0.45 and 0.51
  - `uc20260930-jores-result-maize-protoplasts-cnn`
  - `uc20260930-jores-result-tobacco-leaves-cnn`
  - `uc20260930-jores-result-maize-protoplasts-gc-motif-linear`
  - `uc20260930-jores-result-tobacco-leaves-gc-motif-linear`
- foundation-model AUC 0.937 to 0.961
  - `amp-feng-20261007-result-promoter-tata-caduceus-ph-auc`
  - `amp-feng-20261007-result-promoter-tata-hyenadna-auc`

### use-case-summary-mass-spectrum-molecule-shortlisting

- formula split Recall@1 47.5, 58.2, 42.7, 13.9, 4.7
  - `uc20260930-msalign-v2-result-massspecgym-formula-formula-free-msalign-r1`
  - `uc20260930-msalign-v2-result-massspecgym-formula-formula-free-msalign-score-fusion-overbar-r1`
  - `uc20260930-msalign-v2-result-massspecgym-formula-formula-free-emb-cos-r1`
  - `uc20260930-msalign-v2-result-massspecgym-formula-formula-free-jestr-r1`
  - `uc20260930-msalign-v2-result-massspecgym-formula-formula-free-deepset-r1`
- MCES split Recall@1 19.0, 30.8, 12.6, 7.9, 1.9
  - `uc20260930-msalign-v2-result-massspecgym-mces-formula-free-msalign-r1`
  - `uc20260930-msalign-v2-result-massspecgym-mces-formula-free-msalign-score-fusion-overbar-r1`
  - `uc20260930-msalign-v2-result-massspecgym-mces-formula-free-emb-cos-r1`
  - `uc20260930-msalign-v2-result-massspecgym-mces-formula-free-jestr-r1`
  - `uc20260930-msalign-v2-result-massspecgym-mces-formula-free-deepset-r1`
- Recall@20 87.0, 92.8, 64.9, 82.0
  - `uc20260930-msalign-v2-result-massspecgym-formula-formula-free-msalign-r20`
  - `uc20260930-msalign-v2-result-massspecgym-formula-formula-free-msalign-score-fusion-overbar-r20`
  - `uc20260930-msalign-v2-result-massspecgym-mces-formula-free-msalign-r20`
  - `uc20260930-msalign-v2-result-massspecgym-mces-formula-free-msalign-score-fusion-overbar-r20`
- earlier version Recall@1 53.8 and 41.2
  - `msalign-2026-table3-result-msalign-massspecgym-formula-split-no-formula-r-1-recall-at-1`
  - `msalign-2026-table3-result-emb-cos-massspecgym-formula-split-no-formula-r-1-recall-at-1`

### use-case-summary-phenotype-perturbation-selection

- 20 submissions, 0.452 to 0.566
  - `ucc-research-result-cppc-table-s2-d-row-6-robust-topk-overlap-auc`
  - `ucc-research-result-cppc-table-s2-d-row-7-robust-topk-overlap-auc`
- two nominated targets reached the desired state
  - `ucc-research-result-cppc-nominated-target-outcome-named-desired-state-hits`

### use-case-summary-rhodopsin-wavelength-transfer

- mean-row error 10.45, 13.46 and 14.90 nm
  - `uc20260930-rhomax-result-mean-rhomax-mean-absolute-error-nm`
  - `uc20260930-rhomax-result-mean-rhomax-retinal-mean-absolute-error-nm`
  - `uc20260930-rhomax-result-mean-blasso-mean-absolute-error-nm`
- per-split RhoMax 7.28 to 16.68 nm
  - `uc20260930-rhomax-result-split-2-rhomax-mean-absolute-error-nm`
  - `uc20260930-rhomax-result-split-4-rhomax-mean-absolute-error-nm`
- Spearman 0.418, -0.146 and -0.222
  - `rewire-local-20260920-result-flip2-composition-spearman`
  - `rewire-local-20260921-result-esm2-8m-spearman`
  - `rewire-local-20260921-result-esm2-35m-spearman`
- NDCG 0.955, 0.896, 0.907 and 0.921
  - `rewire-local-20260920-result-flip2-composition-ndcg`
  - `rewire-local-20260921-result-esm2-8m-ndcg`
  - `rewire-local-20260921-result-esm2-35m-ndcg`
  - `rewire-local-20260920-result-flip2-train-mean-ndcg`

## Changed records

None. Issue #87 adds records only.

## Not done

- No use_case record was edited, so no `assessed_by` link or other field changed.
- No metadata-correction claim was needed, because no existing field was changed.
