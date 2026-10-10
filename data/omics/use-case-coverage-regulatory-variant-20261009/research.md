# Research: regulatory variant and gene follow-up use-case pass, 2026-10-09

Use case: `use-case-regulatory-variant-gene-follow-up` ("Which variants, regulatory elements and genes should I perturb to explain a disease-associated locus?"). Existing judgements, all `proxy`: K562 CRISPRi enhancer-gene linking (MPRabc source) and four QTL causal-variant discrimination sets (Feng). Exclusions: reporter activity is not endogenous regulation; whole-element perturbation is not allele editing; a regulatory link is not a causal disease role.

Bounds: cutoff 2026-10-09; budget 25 queries, 5 used; at most 3 sources extracted. Lane `genomics`.

## Queries

| # | Time (UTC) | Query | Channel | Outcome |
| --- | --- | --- | --- | --- |
| 1 | 21:03:09 | `(ENCODE-rE2G OR "activity-by-contact" OR "ABC model") AND (CRISPRi OR "CRISPR perturbation") AND (enhancer-gene OR "enhancer–gene") AND (benchmark OR comparison OR AUPRC) AND PUB_YEAR:[2020 TO 2026]` | Europe PMC REST | 116 hits; Gschwind et al. 2026 (PMC13471189), scE2G, astrocyte CRISPRi, multiome linking |
| 2 | 21:03:38 | `("locus-to-gene" OR L2G OR PoPS OR "gene prioritization" OR "gene prioritisation") AND (GWAS) AND (benchmark OR comparison OR "gold standard") AND (precision OR recall) AND ("nearest gene" OR MAGMA) AND PUB_YEAR:[2020 TO 2026]` | Europe PMC REST | 233 hits; CALDERA (PMC13012518) |
| 3 | 21:04:00 | `(PoPS OR "polygenic priority score" OR FLAMES OR cS2G OR "L2G") AND ("nearest gene" OR "closest gene") AND (precision AND recall) AND (benchmark OR "gold standard" OR "ground truth") AND PUB_YEAR:[2022 TO 2026]` | Europe PMC REST | 12 hits; PoPS (PMC10836580, full text HTTP 500), HGG Adv 2024 eQTL co-regulation |
| 4 | 21:04:18 | `(Enformer OR Borzoi OR Sei OR ChromBPNet OR deltaSVM OR CADD OR AlphaGenome) AND ("MPRA" OR "massively parallel reporter" OR "saturation mutagenesis" OR "allelic") AND ("variant effect") AND (benchmark OR comparison OR evaluation) AND PUB_YEAR:[2021 TO 2026]` | Europe PMC REST | 549 hits; Manzo et al. 2025 (PMC12562713), Tang et al. 2025 (PMC12261763) |
| 5 | 21:11:18 | `("base editing" OR "prime editing" OR "saturation genome editing" OR "allelic series") AND (noncoding OR enhancer OR "regulatory variant") AND (Enformer OR Borzoi OR AlphaGenome OR ChromBPNet OR CADD) AND (prediction OR benchmark) AND PUB_YEAR:[2022 TO 2026]` | Europe PMC REST | 93 hits; PETRA preprint and Cell 2025 'Rewriting regulatory DNA' as leads; no tabled predictor comparison |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Gschwind et al. 2026, Nature, Supplementary Table 3 sheet 'Held-out benchmarks' | Extract all cells | Six predictors and baselines on held-out CRISPR pairs from five cell types, beyond the existing K562 mapping, with bootstrap intervals. Developer paper (ENCODE-rE2G and ABC), recorded as such |
| Gschwind other sheets and Supplementary Tables 4, 5, 7 | Not extracted | The training sheet has more than 500 predictor rows, mostly ABC variants; eQTL and GWAS enrichment tables are a different endpoint. Kept lean |
| Manzo et al. 2025, Genes, Table 1 | Extract all cells | 24 DNA language and sequence-to-function models on reporter-measured allelic effects in four cell lines. TREDNet is the authors' own model |
| Tang et al. 2025, Genome Biology, Table 1 | Extract all cells | 14 models on CAGI5 saturation mutagenesis MPRA; mostly independent of the model developers |
| CALDERA (Schipper et al. 2026, PLoS Genet) | Not extracted; gap | Developer comparison against FLAMES, L2G and cS2G prints only Brier scores (Table 1); AUPRC is figure-only (S3 Fig). No printed precision or recall |
| Astrocyte CRISPRi (Green et al. 2026, Nat Neurosci) | Not extracted; lead | Independent non-K562 benchmark of ABC and ENCODE-rE2G, but per-model values are in figures, prose and bootstrap source data |
| scE2G (Nat Genet 2026) | Not extracted; lead | Developer paper with supplementary tables not opened |
| Multiome linking (Nat Genet 2025) and PoPS (Nat Genet 2023) | Not retrieved | Europe PMC returned HTTP 500 |

## Modelling choices

- The 'Held-out benchmarks' sheet holds two populations, so it gives two protocols: held-out pairs (new dataset) and combined K562 training pairs. The latter reuses `ucc-research-data-mprabc-k562-crispri`, but its weighting differs from the existing K562 protocol, so it is a separate protocol and must not be pooled with it.
- Manzo cell lines and Tang cell lines are each a stratum of one comparison group.
- Origin: ENCODE-rE2G, ABC and the two baselines in Gschwind are `author_reported`; EPIraction and EpiMap are `independent_paper`. TREDNet in Manzo and the lentiMPRA-trained models in Tang are `author_reported`; the rest are `independent_paper`.
- Relevance is `proxy` for every protocol, consistent with the five existing judgements: CRISPR element perturbation does not test alleles, and reporter assays do not measure endogenous regulation.

## Things a reviewer should judge

1. Manzo Table 1 header gives K562 19,321 and HepG2 16,255 SNPs; Table 4 lists K562 datasets of 19,237 and 2,756 variants and HepG2 datasets of 14,183, about 600 and 284, which do not sum to the header counts. Filtering may explain this; it is not stated.
2. Manzo prose averages (TREDNet 0.297, ChromBPNet 0.289, SEI 0.276; elsewhere TREDNet 0.318, SEI 0.295) are aggregates over datasets and differ from the Table 1 per-cell-line values. Stored as a claim, not as results.
3. Manzo standard errors are not defined; Geneformer, a single-cell transcriptome model, was adapted to DNA tokens by the authors.
4. Tang Methods name the HepG2 CREs 'LDLT, SORT1, F9'; 'LDLT' is presumably LDLR. Recorded as printed.
5. Gschwind 'precision at threshold' and 'recall at threshold' do not restate the threshold in this sheet.
6. Relevance: a reviewer may judge the held-out CRISPR stratum `direct` for element-gene linking; `proxy` follows the existing K562 mapping.

## Coverage

Bounded pass. Not systematic. Not covered: locus-to-gene comparisons with printed precision and recall, endogenous allele-editing benchmarks, the astrocyte and scE2G tables, Gschwind eQTL and GWAS benchmarks, and Manzo LD-block causal-SNP results.
