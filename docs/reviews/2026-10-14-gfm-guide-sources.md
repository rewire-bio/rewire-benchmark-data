# Genomic foundation model guide sources (issue #138)

Batch: `data/omics/gfm-guide-sources-20261014` (127 records), plus text corrections to `use-case-patient-rna-splicing-validation`.

Extracted by a Claude (Opus 5.5) agent. Reviewed on 2026-10-14 by a separate Claude (Opus 5.5) review agent that did not take part in the extraction. No human review is claimed, and nothing here is a reproduction.

## Outcome

Approved with corrections. All 44 results match their sources: printed value, numeric value, unit and locator. The extractor's judgement calls hold. The review found and fixed five errors (one in the use case), added one source concern, recorded the bioRxiv hash drift and applied the use case `setting` correction. Every batch record is now `source_checked`. None is disputed.

The receipt is `data/omics/gfm-guide-sources-20261014/review.json`. The review scripts are in `review/`: `check_gfm_guide.py` compares every value with the sources and does not import the extraction script; `apply_review.py` sets statuses, writes the review blocks and applies the corrections below.

## Sources and hashes

Every artifact was downloaded again on 2026-10-14 between 13:33 and 13:38 UTC.

| Source record | Artifact | Pinned SHA-256 | Outcome |
| --- | --- | --- | --- |
| `gfm-guide-20261014-source-evee-v4` | bioRxiv v4 PDF | `1d65b070…24eef8` | Hash differs (per-download stamp, below). Fresh copy `9e217644…78710a`, 26 pages |
| `gfm-guide-20261014-source-evee-repo-fig1c-pdf` | evee-manuscript `fig1c_deconf_heatmap.pdf` at e5e4a43 | `3dd79f20…48eec6` | match |
| `gfm-guide-20261014-source-evee-repo-fig1d-pdf` | `fig1d_indel_heatmap.pdf` at e5e4a43 | `b1ec938f…578136` | match |
| `gfm-guide-20261014-source-evee-repo-heatmap-common` | `scripts/figure1/_heatmap_common.py` at e5e4a43 | `1d477d2e…6e2e` | match |
| `gfm-guide-20261014-source-evee-repo-fig1d-script` | `scripts/figure1/fig1d_indel_heatmap.py` at e5e4a43 | `5c03755c…e34d` | match |
| `gfm-guide-20261014-source-evo2-biorxiv-metadata` | bioRxiv API details, Evo 2 | `8b50005d…2254` | match |
| `gfm-guide-20261014-source-hegde2025` | Europe PMC XML PMC12652071 | `9ea68b68…ef47` | match |
| `gfm-guide-20261014-source-ntv3-v1` | bioRxiv v1 PDF | `374a7177…961ea` | Hash differs (per-download stamp). Fresh copy `082ea9b0…3fbcee`, 107 pages |
| `gfm-guide-20261014-source-nt-nature-methods` | Europe PMC XML PMC11810778 | `7c3b78a4…7249` | match |
| `gfm-guide-20261014-source-hyenadna-arxiv-v2` | arXiv 2306.15794v2 PDF | `2f471549…798c` | match |
| `gfm-guide-20261014-source-hyenadna-tiny-1k-card` | HF model card at eed1f67 | `27389371…98f1` | match |
| `gfm-guide-20261014-source-alphagenome-article` | Europe PMC XML PMC12851941 | `50d10530…e13` | match |
| `source-alphagenome-nature2026-supplementary-methods` (existing) | MOESM1 PDF | `86b2e6a0…4c0` | match |
| `evidence-official-578439da3f3a3a476b7f` (existing) | alphagenome_research README at 0db53bd | `c715b22c…2681` | match |

I also read `scripts/figure1/fig1c_deconf_heatmap.py` at e5e4a43 (SHA-256 `2205bc39b34d52472363cb26c77d7e7daca4a2c463472ffcaf541d6be9e7bbf5`; not a source record) to confirm that Figure 1c is drawn through `prepare()` in `_heatmap_common.py`. I also read EVEE bioRxiv v1 (fresh copy `675f5daf…bdca73`, 12 pages, posted 2026-04-11) to trace the issue's numbers. It is not a source record.

bioRxiv stamps each PDF download with its own XMP ModifyDate, MetadataDate, DocumentID and InstanceID, Info ModDate and trailer /ID. The extractor's copies were not kept, so the pinned bytes cannot be re-verified. Following the Alavi 2026 and SpliceAI2 precedent, both bioRxiv source records now have a `hash_scope` that says so and gives the reviewer's copy. Every value from these two PDFs was checked in the fresh copies.

## Method

- `review/check_gfm_guide.py` asserts the pinned hash of every stable artifact. It then parses each table or figure row the batch cites, asserts captions, row labels and column order, and compares printed value, numeric value and unit for all 44 results. It also asserts verbatim the source sentences behind the 9 descriptive claims. Result: 44 of 44 results match and 9 of 9 claims match, with 0 failures.
- EVEE Figure 1 is a raster image in the paper. The Overall rows were parsed from the repository's vector PDFs. Column order comes from `METHOD_GROUPS` (EVE has no values, so it is dropped) and `METHOD_COLS`. I compared all 12 cells by eye with a 300 dpi render of page 3 of the fresh paper copy.
- I read every configuration, protocol, dataset, method and evaluation against the Methods text: checkpoints, layers, windows, hardware, origin, comparison fields and the reasons in `missing_metadata`.
- Link targets were checked in the store. GPN-MSA links to `regulatory-variant-20261009-model-gpn`, as the existing GUANinE and TraitGym GPN-MSA configurations do.
- For the use case I read its links, its 18 `assessed_by` judgements, its baseline and summary claims, and every evaluation on its linked protocols.

## Values checked

### EVEE (bioRxiv v4), Figure 1c, row "Overall (n=158,616, 27.8%P)", AUROC

| Column | Record | Value | Origin | Outcome |
| --- | --- | --- | --- | --- |
| Evo2 Covariance | `result-evee-deconfounded-evo2-covariance` | 0.977 | author_reported | match |
| Evo2 Mean | `result-evee-deconfounded-evo2-mean` | 0.967 | author_reported | match |
| Evo2 Loss | `result-evee-deconfounded-evo2-loss` | 0.929 | author_reported | match |
| CADD v1.7 | `result-evee-deconfounded-cadd-v1-7` | 0.963 | independent_paper | match |
| AlphaMissense | `result-evee-deconfounded-alphamissense` | 0.972 | independent_paper | match; equals its Missense cell (concern) |
| GPN-MSA | `result-evee-deconfounded-gpn-msa` | 0.952 | independent_paper | match |
| NTv3 | `result-evee-deconfounded-ntv3-cosine` | 0.710 | independent_paper | match; cosine distance (concern) |
| AlphaGenome | `result-evee-deconfounded-alphagenome` | 0.574 | independent_paper | match |

### EVEE Figure 1d, row "Overall (n=73,961, 65.1%P)", AUROC

| Column | Record | Value | Outcome |
| --- | --- | --- | --- |
| Evo2 Covariance | `result-evee-indel-evo2-covariance` | 0.991 | match; main text "0.991 vs. 0.980" |
| Evo2 Mean | `result-evee-indel-evo2-mean` | 0.984 | match |
| CADD v1.7 | `result-evee-indel-cadd-v1-7` | 0.980 | match |
| NTv3 (subref probe) | `result-evee-indel-ntv3-subref-probe` | 0.828 | match |

EVEE Methods "Harvesting": `result-evee-embedding-extraction-h100-hours` ∼20,000 H100 GPU-hours (`accelerator-time`, hour, approximate). match.

### Hegde, Nebel and Rahman 2025

| Record | Locator | Value | Unit | Outcome |
| --- | --- | --- | --- | --- |
| `result-hegde-nt-5-epochs-training-time-seed-41` | Table A1 | 7.53 | hour | match |
| `result-hegde-nt-5-epochs-training-time-seed-42` | Table A1 | 7.50 | hour | match |
| `result-hegde-nt-5-epochs-training-time-seed-43` | Table A1 | 7.48 | hour | match |
| `result-hegde-nt-5-epochs-evaluation-time-seed-41` | Table A1 | 8.49 | minute | match |
| `result-hegde-nt-5-epochs-evaluation-time-seed-42` | Table A1 | 8.51 | minute | match |
| `result-hegde-nt-5-epochs-evaluation-time-seed-43` | Table A1 | 8.49 | minute | match |
| `result-hegde-nt-convergence-time` | Methods para. 3 | approximately 19 | hour | match |
| `result-hegde-dnabert-2-pruned-convergence-time` | Methods para. 3 | around 1 | hour | match |

### NTv3 (bioRxiv v1), Table 5, H100 GPU-hours

| Model | Pre-training 8 kb | Length ext. 1-4 | Length ext. 5-7 | Post-training 1 | Post-training 2 | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| 8M | 1,608 | 40 | 40 | NA (not recorded) | NA (not recorded) | match (3 of 3) |
| 100M | 3,000 | 40 | 48 | 1,536 | 192 | match (5 of 5) |
| 650M | 6,736 | 88 | 80 | 1,824 | 192 | match (5 of 5) |

### Nucleotide Transformer (Nature Methods), Methods "Hardware"

| Record | Value | Unit | Outcome |
| --- | --- | --- | --- |
| `result-nt-500m-ia3-fine-tuning-runtime` | 20 | minute | match |
| `result-nt-2-5b-ia3-fine-tuning-runtime` | 50 | minute | match |

### HyenaDNA (arXiv v2), Table A.2

| Column | GPUs | Wall clock | GPU-hrs | Origin | Outcome |
| --- | --- | --- | --- | --- | --- |
| DNABERT 110M | 8-2080 TI | 25 (day) | 12,000 | paper_compilation | match; new concern on GPU-hrs |
| Nucleotide Transformer 2.5B | 128-A100-80GB | 28 (day) | 215,000 | paper_compilation | match; new concern on GPU-hrs |
| HyenaDNA 436K | 1-A100-40GB | 80 (minute) | 1.3 | author_reported | match |
| HyenaDNA 1.6M | 1-A100-40GB | 80 (minute) | 1.3 | author_reported | match |

### Descriptive claims

| Claim | Source text asserted | Outcome |
| --- | --- | --- |
| `claim-alphagenome-recommended-hardware` | README "Model requirements" and introduction | match |
| `claim-alphagenome-training-compute` | Supplementary Methods, Sequence Parallelism, Pre-training, Distillation, Model Training Parameters (PDF pages 20 to 22) | match |
| `claim-alphagenome-variant-scoring-time` | Results, "Taking less than 1 s on an NVIDIA H100 GPU" | match |
| `claim-evee-developer-overlap` | Competing interests; Evo 2 author list | corrected (2) |
| `claim-hyenadna-suggested-gpus` | Model card "GPU requirements (suggested)" and Colab paragraph | match |
| `claim-nt-fine-tuning-single-gpu` | Discussion, "under 15 min on a single GPU" | match; locator corrected (3) |
| `claim-nt-training-compute` | Methods "Hardware", paragraphs 1 and 2 | match |
| `claim-ntv3-650m-pretraining-wall-clock` | Section 4.4.4 "Pre-training Compute" | match |
| `claim-ntv3-inference-hardware` | Results, pages 4 and 6 | match |

## Judgement calls

1. **EVEE v4 rather than the issue's numbers.** The issue's list (0.971, 0.972, 0.966, 0.952, 0.932, 0.586, indels 0.986) is copied exactly from EVEE v1: the Figure S1 caption on the deconfounded benchmark and the v1 indel text. v4 (posted 2026-07-11) is the current version, and its Figure 1c and 1d replace those values. The extractor was right to record v4. v1 values are not recorded.
2. **EVEE concerns.** Both are confirmed. `fig1c_deconf_heatmap.py` calls `prepare()`, which renames `NTv3 cosine dist` to `NTv3` and drops `NTv3 subref probe`. The Methods describe only the layer-11 logistic-regression probe for NTv3; "cosine" appears in the Methods only for selecting positions. `prepare()` also copies AlphaMissense's Missense values into its Overall row; in Figure 1c both cells read 0.972. Values are kept and marked.
3. **Origins.** Evo2 Covariance is EVEE itself, and Evo2 Mean is the authors' own comparator probe, so `author_reported` fits the vocabulary ("reported by the authors of the evaluated method"). For Evo2 Loss, Evo 2's own zero-shot score, `author_reported` is the cautious choice. Three EVEE authors (N. Nguyen, D. Balsam, N. K. Wang) appear in the 600-name Evo 2 author list, matched by name only. Accepted, with the name-only caveat kept in the claim. CADD, AlphaMissense, GPN-MSA, NTv3 and AlphaGenome are `independent_paper`. The HyenaDNA DNABERT and NT columns are `paper_compilation`, because the table cites no source and the authors did not run them.
4. **AlphaGenome hardware wording.** The issue said "training on 8 TPU v3". The supplement splits each 1 Mb interval across 8 TPU cores and uses 512 TPUv3 cores per gradient step, and the claim says so. The README wording ("at least an NVIDIA H100 GPU", "TPUs v3 or higher", API "without needing specialized hardware") is reproduced faithfully. The article says "less than 1 s"; the claim keeps it as a bound, not a value.
5. **Nucleotide Transformer fine-tuning time.** The conflict is real. The Methods say all fine-tuning runs used one node of eight A100s and averaged 20 and 50 min; the Discussion says under 15 min on a single GPU. The Methods values are results, the Discussion bound is a claim, and the source concern is kept. Its locator is corrected (3).
6. **New vocabulary.** `accelerator-time` (metric) and `day` (unit) do not respell existing concepts. `runtime` is wall clock and `compute-cost` is money, so neither covers GPU-hours. `day` has a QUDT exact match. `accelerator-time` has no STATO or QUDT match; that is stated by its absence and acceptable. Both are used correctly: GPU-hours in `hour` under `accelerator-time`, and wall clock under `runtime`.

## Conflicts and corrections

1. `gfm-guide-20261014-config-hegde-nt-500m-human-ref-5-epochs`: `fine_tuning.description` said "Full fine-tuning". Appendix A.3 lists LoRA through peft (r=1, lora_alpha=32, lora_dropout=0.1). Corrected.
2. `gfm-guide-20261014-claim-evee-developer-overlap`: "mostly Goodfire employees" was wrong. The title page and Competing interests give 11 of 23 authors at Goodfire (including the first and last authors) and 11 at Mayo Clinic. Corrected. `research.md` keeps the extractor's wording as a record of the extraction.
3. `gfm-guide-20261014-claim-nt-fine-tuning-single-gpu` and the concern on `gfm-guide-20261014-source-nt-nature-methods`: the "under 15 min" sentence is in Discussion paragraph 3, not 2. Corrected.
4. `gfm-guide-20261014-source-evee-v4` and `-source-ntv3-v1`: `hash_scope` added (see Sources).
5. New concern on `gfm-guide-20261014-source-hyenadna-arxiv-v2`. In Table A.2 the compiled GPU-hours do not equal the GPUs times the wall clock printed beside them: 8 × 25 days is 4,800 against 12,000, and 128 × 28 days is 86,016 against 215,000, both about 2.5 times higher. The NT article also gives 128 A100s for 28 days. The two GPU-hour results keep their printed values and have a limitation.
6. `use-case-patient-rna-splicing-validation` `evidence_gaps[2]`. The extractor's replacement said "No DNA foundation-model result is linked to this use case". That is false: the linked Alavi et al. 2026 protocols (`rna-splicing-20261011-alavi2026-protocol-opa1-evaluation`, `-multigene`) carry source-checked evaluations of Evo 2 40B, Genos 10B and NTv3 650M. The new text says Feng Table 1 is not linked here and names the Alavi foundation-model proxies. `metadata-correction-gfm-guide-20261014-patient-rna-splicing-evidence-gaps-2` keeps the original text as `previous_value`. Its review note keeps the extractor's text.

The batch was already in the store when review started, and no release has included it. Corrections 1 to 3 were therefore made in place, with no `metadata-correction-` claims. Corrections 4 to 6 add text and do not change any value.

Other inconsistencies noted, with no record change: Hegde Table 1 counts (89,060 train, 8,862 test) differ from the Methods (88,717 and 8,846). The EVEE full-dataset counts (1,539,596 + 2,716,001) do not sum to 4,252,870; the dataset record already says "as printed".

## Use case `setting`: re-review and re-pin

The `setting` of `use-case-patient-rna-splicing-validation` ended: "A separate, proxy sequence-classification AUC for DNA foundation-model embeddings (Feng et al. 2025, Table 1 Acceptor/Donor) is also linked, scoped as a different endpoint." Feng Table 1 is linked to `use-case-splicing-follow-up` only.

The extractor's proposed replacement only said that Feng is not linked here. That would drop the statement that separate proxy evidence is linked and kept apart. Five of the pinned judgements rely on that statement: Alavi multigene and OPA1, and Fortier Riepe, SPiP, CI-SpliceAI benchmark and Barbosa deep-intronic. Each describes its protocol as "the sequence-classification kind of evidence the use case keeps separate from patient-RNA recovery". So I applied a wording that keeps that meaning and corrects only the citation:

> Separate, proxy sequence-classification results for DNA foundation models (Alavi et al. 2026: Evo 2 40B, Genos 10B and NTv3 650M classifying variants with established splicing defects against benign variants) are also linked, scoped as a different endpoint. Feng et al. 2025 Table 1 splice acceptor and donor classification is linked to 'Prioritise variants for splicing experiments', not here.

"AUC" is dropped because Alavi reports accuracy, sensitivity, specificity and error rates, not AUC. The question, decision, inputs, output, exclusions and clinical scope are unchanged. I re-read each of the 18 judgements, the baseline and the summary against the new text. None cites Feng, and none depends on the Feng sentence: each judges its own protocol's endpoint against the use case's question and output. Their relevance, endpoints and limitations stand as reviewed.

The old text is kept in `metadata-correction-gfm-guide-20261014-patient-rna-splicing-setting`. The setting is a pinned field, so the claims that pin the use case were re-pinned against this review with `npm run use-cases:repin`:

- the 18 judgements: `use-case-mapping-amp-20261007-issue12-fraser-kremer`, `use-case-mapping-rna-splicing-20261009-drost2025-cagi6`, `-drost2025-inhouse`, `-drost2025-merged`, `-segarracasas2025-outrider`, `-segarracasas2025-splicing`, `-segers2026-kremer-expression`, `-segers2026-kremer-splicing`, `use-case-mapping-rna-splicing-20261011-alavi2026-multigene`, `-alavi2026-opa1-evaluation`, `-fortier2026-barbosa-deep-intronic`, `-fortier2026-ci-spliceai-benchmark`, `-fortier2026-riepe`, `-fortier2026-spip`, `-silverstein2026-allelic-imbalance`, `-silverstein2026-splicing`, `use-case-mapping-rna-splicing-20261013-spliceai2-gel-gtag`, `-spliceai2-gel-prioritised`
- `use-case-baseline-patient-rna-splicing-validation` and `use-case-summary-patient-rna-splicing-validation`, which also pin the use case's fields. Neither mentions Feng.

The `decision` field still says "Inspect the FRASER known pathogenic-event recovery curve and the sequence-classification proxy evidence". That remains true of the linked Alavi, Fortier and Drost proxies and was not changed.

## Remaining gaps for #138

- **Saadat and Fellay, ICLR 2026 (openreview NUleWh1GFx):** not retrieved. The PDF needs a manual download, then extraction and review.
- **Aspidova et al. 2026 throughput unit:** not resolved. GENA_LM at ed71502 has no benchmarking code; only the authors can say what the tokens/s column measures. Review note M1 stands.
- No relevance judgements link the new execution protocols to `use-case-diagnostic-genomics-model-execution`. That needs a separate judgement pass.
- The HyenaDNA Table A.2 GPU-hours discrepancy (correction 5) could be raised with the HyenaDNA authors.
