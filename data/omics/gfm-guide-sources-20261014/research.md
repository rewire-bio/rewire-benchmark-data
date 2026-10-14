# Research notes: genomic foundation model guide sources (issue #138)

Scope: the seven sources and two fixes listed in issue #138, nothing else. 2026-10-14. Extraction by a Claude (Opus 5.5) agent. All records have status `needs_review`.

## What was extracted

| Source | Records | Notes |
| --- | --- | --- |
| EVEE (Pearce et al. 2026, bioRxiv v4) | 13 results, 13 evaluations, 9 configurations, 1 method, 3 datasets, 3 protocols, 1 claim | Overall rows of Figure 1c (deconfounded SNVs, 8 methods) and Figure 1d (indels, 4 methods); about 20,000 H100-hours for embedding extraction |
| Hegde, Nebel and Rahman 2025 | 8 results | Table A1 training and evaluation time for three seeds; Methods convergence times for NT 500M (about 19 h) and DNABERT-2 (about 1 h per pruned model) |
| NTv3 (Boshar et al. 2025, v1) | 13 results, 2 claims | Table 5 H100 GPU-hours per stage and size (two NA cells not recorded); wall-clock and inference statements as claims |
| Nucleotide Transformer (Nature Methods) | 2 results, 2 claims, 1 source concern | Methods 'Hardware' fine-tuning averages (20 and 50 min); the Discussion's 'under 15 min on a single GPU' as a conflicting claim |
| HyenaDNA (arXiv v2) and model card | 8 results, 1 claim | Table A.2 GPU-hours and wall clock for DNABERT, NT 2.5B and two HyenaDNA models; suggested GPUs per checkpoint |
| AlphaGenome | 3 claims | Under 1 s per variant on an H100 (distilled model); pre-training and distillation compute; README hardware recommendations |
| Patient-RNA splicing use case | 1 correction claim, 1 record change | `evidence_gaps[2]` no longer says Feng Table 1 is linked here; the pinned `setting` text is proposed for the reviewer |

## Decisions

- **EVEE values differ from the issue.** The issue lists SNV AUROC 0.971 (EVEE), 0.972, 0.966, 0.952, 0.932, 0.586 and indel 0.986. As a set they match no row of the v4 Figure 1b or 1c. The issue probably used an earlier version (v1 to v3, April 2026), which was not retrieved. This batch records v4: deconfounded Overall 0.977 EVEE, 0.967 Evo 2 mean probe, 0.929 Evo 2 loss, 0.963 CADD v1.7, 0.972 AlphaMissense, 0.952 GPN-MSA, 0.710 NTv3, 0.574 AlphaGenome; indel Overall 0.991, 0.984, 0.980, 0.828. The main text confirms 0.991 against 0.980 for indels.
- **EVEE figure columns.** Two source concerns are recorded from the authors' plotting code. First, the 'NTv3' column in Figure 1b and 1c is a zero-shot cosine distance, while the Methods describe only a supervised probe. Second, AlphaMissense's Overall cell is its missense-only value. Both values are kept and marked.
- **EVEE independence.** The authors are mostly Goodfire employees. Three of them (N. Nguyen, D. Balsam, N. K. Wang) are on the Evo 2 preprint's author list, matched by name only. The Evo 2 based configurations are `author_reported`. The baselines (CADD, AlphaMissense, GPN-MSA, NTv3, AlphaGenome) are `independent_paper`, because the EVEE authors ran them but did not develop them.
- **Which EVEE table.** The deconfounded benchmark (Figure 1c) controls for consequence-type priors and is the one the guide needs. Figure 1b (833,970 SNVs) and the per-consequence rows are not extracted.
- **Approximate prose values** ('approximately 19 h', 'around 1 h', '∼20,000 H100-hours') are results with `approximate: true`. Statements that are bounds rather than values ('under 15 min', 'less than 1 s', 'just under nine days') are claims.
- **HyenaDNA Table A.2 origin.** The DNABERT and NT rows are not the HyenaDNA authors' runs, and the table cites no source for them, so they are `paper_compilation`. The HyenaDNA rows are `author_reported`.
- **AlphaGenome compute.** The issue says "training on 8 TPU v3". The supplement says each 1 Mb interval is split across 8 TPU cores, and each gradient step needs 512 TPUv3 cores. The claim records what the supplement says.
- **NT fine-tuning conflict.** Recorded as a source evidence concern. The Methods values are results; the Discussion value is a claim.

## Gaps

- **Saadat and Fellay (ICLR 2026, openreview NUleWh1GFx)**: the PDF could not be retrieved by script. It needs a manual download, then extraction.
- **Aspidova et al. 2026 throughput unit**: not resolved. The GENA_LM repository at ed71502 has the figure and its caption but no benchmarking code. Only the authors can say what the tokens/s column measures. The existing source concern (review M1) stands, and no author was contacted.
- No use-case relevance judgements were added. The execution protocols in this batch are candidates for `use-case-diagnostic-genomics-model-execution`.
