# Research: Zeng et al. 2026 cfMeDIP-seq methylation and fragmentomic classifiers, 2026-10-11

Use cases: `use-case-plasma-ctdna-methylation` and `use-case-plasma-ctdna-fragmentomics`.

Bounds: window 2025-10-01 to 2026-10-11; about 30 queries per use case for the whole uc-ctdna pass (26 logged); at most about 6 sources extracted across both use cases. Lane `genomics`. Worker: Claude (Opus 5.5) research agent uc-ctdna; no human review claimed. The search log is `data/omics/lit-search-20261011-uc-ctdna/ledger.jsonl` and the pass report is `data/omics/lit-search-20261011-uc-ctdna/report.md`.

## Why this source

Zeng et al. 2026 (Nature Cancer, 10.1038/s43018-026-01116-3) pool 1,074 cfMeDIP-seq profiles from nine studies and compare, on the same plasma samples and folds, a methylation classifier, four fragmentomic feature sets computed from the same reads (5' end motifs, DELFI-style fragment ratios, insert size, nucleosome peak distance) and their combinations. Each has an AUC and a sensitivity at 99% specificity, in cross-validation and in an independent paired-end validation dataset. This fills two stated gaps: the methylation use case has no same-sample comparison of methylation with other cfDNA features outside CCGA, and both use cases lack recent results at a high declared specificity.

## Record design

- Two sources: the article XML and Source Data Fig. 4 (all eight sheets extracted: 52 results).
- Four datasets and four protocols: primary PE (420), independent PE validation (95 or 140, see below), primary SE (339) and the SE 10% hold-out (39).
- One method (the PCA plus best-of-seven-algorithms workflow) and ten configurations, one per feature set.
- 26 evaluations, all `author_reported`. AUC results carry the fold-level s.d. as `standard_deviation`; sensitivity results carry `unresolved_spread` because the column is headed sd_sens99 while the Figure 4 legend calls those error bars s.e.
- Six relevance judgements, all `proxy`: four for methylation (one per protocol) and two for fragmentomics (PE protocols only; the SE sheets have only end motifs).

## Things a reviewer should judge

1. **Methylation validation AUC.** Sheet Fig.4c prints 0.69415; Results P32 prints 0.674. Evidence concern on the Source Data source, `source_discrepancy` on the result.
2. **Below-chance validation AUCs.** In Fig.4c, 'Combined Motif + Methylation (1%)' is 0.066 and 'End Motifs' 0.188. The authors attribute lower motif AUCs to the HCC-study healthy controls' different protocol. Flagged with `source_anomaly`; a reviewer may prefer to exclude these two evaluations from the validation judgements.
3. **Validation size.** Results P28 says 95 baseline samples passed QC; the Extended Data Fig. 9f legend says n = 140. The dataset records the conflict.
4. **LFS carriers counted as cancer.** LFS-previvor and LFS-survivor carriers were scored post hoc and labelled as cancer for sensitivity summaries.
5. **Relevance.** `proxy` for both use cases. For methylation it is close to `direct` (a measured methylation workflow at a declared 99% specificity), but the threshold is a fold-model threshold on a case-control set of mostly advanced cancers.
6. **Spread type.** Whether the sensitivity spreads are s.d. (column header, text '±' matches) or s.e. (legend).

## Not extracted

Supplementary Tables 22-23 (per-cancer-type accuracy), cancer-type and subtype classifiers (Fig. 5, Source Data Fig. 5), and the text-only sensitivity at 90% specificity (kept as a claim).
