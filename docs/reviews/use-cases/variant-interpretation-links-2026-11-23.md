# Variant Interpretation Use-Case Links Review, 2026-11-23

Reviewer: deterministic store verification (`rewire-deterministic-table-checker`). All 28 `links:assessed_by:` relevance judgements, cited protocols, eligible evaluations and source hashes were verified against pinned store records and `shared/omics/use-cases.ts` gates. No human scientific review is claimed.

## Scope and Rulings

- Links `28` protocols across four clinical genomics and rare-disease use cases (`rewire-benchmark-data#224`, PR `#345`, PR `#346` / `rewire-benchmarks#56`):
  - `use-case-rare-disease-candidate-ranking` (`7` protocols): `rewire-local-20261121-rdv2-protocol-replication-500-main`, `-snv-200-main` (excluding `rule-avi-snv-200` under its scoped gnomAD split concern), `-indel-120-main`, and `4` configuration-backed TraitGym Mendelian noncoding prioritisation protocols (`proxy`).
  - `use-case-brca1-brca2-germline-interpretation` (`12` protocols): `4` PR `#345` `evo2ops` BRCA1 SGE AUROC protocols and `8` Evo 2 paper (`brixi2026`) BRCA1/BRCA2 SNV strata (`proxy`, uncalibrated rank discrimination).
  - `use-case-missense-pp3-bp4-calibrated-evidence` (`6` protocols): uncalibrated ClinVar rank-discrimination proxies (`Evo 2` coding SNV, `GPN-MSA` ClinVar AUROC across its `15` configuration-backed evaluations, `EVEE` deconfounded SNV, `AlphaGenome Atlas` ClinVar consequence AUPRC and Table S2 ablation, and `GUANinE` ClinVar SNV Spearman), each marked `relevance: "proxy"` with explicit constraints noting lack of calibrated ACMG/AMP PP3/BP4 cutoffs.
  - `use-case-splicing-follow-up` (`3` protocols): `2` clean Evo 2 `SpliceVarDB` SNV strata (`both`, `exonic`) and `AlphaGenome Atlas` `DNM1` minigene average precision (`proxy`).
- Exclusions verified:
  - Excludes the 4 disputed `brixi2026` Evo 2 strata (`clinvar-coding-non-snv`, `clinvar-noncoding-non-snv`, `clinvar-noncoding-snv`, `splicevardb-intronic-snv`) cited in `rewire-benchmark-data#163`.
  - Leaves `alphagenome-2026-t3-*` and `alphagenome-2026-t4-*` splicing protocols unlinked while those records remain `needs_review`.
  - Leaves `traitgym-20261116-protocol-mendelian-matched-feature-global-auprc` and `traitgym-20261116-protocol-mendelian-per-trait-best-of-zero-shot-and-linear-probing` unlinked because their evaluations link `system` to `method` or `model` records rather than `configuration` records (`evaluationLinks` in `shared/omics/use-cases.ts`), and omits the two `method`-linked feature comparators (`gfm-guides-20261014-gpnmsa-eval-ablation-msa-frequency-clinvar`, `gfm-guides-20261014-gpnmsa-eval-ablation-phylop-phastcons-combined-clinvar`) from `gfm-guides-20261014-gpnmsa-protocol-ablation-clinvar-auroc` so its `15` configuration-backed GPN-MSA evaluations stay active.
- Scopes the two legacy un-scoped `evidence_concerns` on `gfm-guide-20261014-source-evee-v4` using `applies_to` strictly to `gfm-guide-20261014-eval-evee-deconfounded-ntv3-cosine` (Figure 1b/1c NTv3 column mismatch) and `gfm-guide-20261014-eval-evee-deconfounded-alphamissense` (Overall row missense copying), keeping both evaluations withheld while activating the six remaining deconfounded evaluations.
