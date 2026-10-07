# AMP bounded evidence intake, 2026-10-07 (clinical lane)

Additive intake for rewire.it#365 (benchmark-data issues #10-19). Covers nine
new AMP use-case decisions (tumour DNA somatic variant detection, tumour RNA
fusion detection, patient-RNA splicing validation, diagnostic DNA/RNA
pathogen identification, plasma ctDNA fragmentomics/methylation detection,
CNV detection/characterisation, diagnostic genomics model execution) plus a
bounded Feng/Peng Wei DNA-foundation-model table expansion (issue #19).

Scope: 431 new catalogue records (10 source,
19 protocol,
24 dataset,
94 configuration,
94 evaluation,
190 result) and 19 new
use-case mapping objects (nine against the new AMP use cases, four against
existing use cases from the Feng expansion).

All status_checked promotions are bounded transcription of primary-source
table cells: automated review per workbench/amp-supervision/primary-review.md
and integration-review-corrections.md, independently checked by a Codex root
reviewer, not qualified human scientific review or independent experimental
reproduction. See workbench/amp-supervision/sonnet-integration-report.md for
exact counts, diff and remaining blockers.

Research and experimental lanes are empty scaffolding only; no record in
this intake is an experimental/research-only lane entry.

## Explicit preserved conflicts and scope limits

- Lancet (PMC6123722): virtual-tumour SNV/indel precision/recall only; no
  tumour clinical utility inference. Strelka2 indel TP 3,647 + FN 1,298 =
  4,945, consistent with the declared 4,945 truth indels. Unselected LoFreq
  (TP 3,210 + FN 1,744 = 4,954; call count 4,853 vs TP 3,210 + FP 1,652 =
  4,862) and MuTect2 (call count 4,873 vs TP 2,712 + FP 2,071 = 4,783) rows
  are internally inconsistent in the source and are excluded from this
  intake, not silently reconciled.
- EnFusion (PMC8642973): synthetic Seraseq known-fusion rescue (optimised,
  100% precision/sensitivity configuration) does not measure novel-fusion
  discovery. NCH clinical-cohort sensitivity (94.0% STAR-Fusion, 88.1%
  Arriba) is ascertained against the optimised EnFusion ensemble's own calls,
  not an independent exhaustive truth set. Table 2 caption (v3) vs
  optimisation narrative (v2) and STAR-Fusion 43.6% (Table 2) vs 43.8%
  (paragraph) precision conflicts are preserved unresolved.
- FRASER (PMC7822922): 85% / mean 11-of-13 known pathogenic splicing-event
  recovery at 30 of 119 patient RNA samples is recovery of known events, not
  diagnostic yield in unknown cases. Full-cohort outlier-gene workload counts
  (12/7/10 genes/sample) are a different population and are not attached to
  this 30-sample recovery evaluation.
- Karius/Blauwkamp 2019: 93.7% (59/63) positive percent agreement with
  initial blood culture is a bounded Table 2 transcription, not sensitivity
  against all 350 sepsis-alert patients; initial blood culture does not
  identify every true infection.
- UCSF respiratory mNGS (PMC11558004): 93.6% (103/110) is sensitivity against
  original clinical RVP testing on a residual pre-DTCA mixed respiratory
  target cohort (RNA extraction, DNase, cDNA synthesis; adenovirus
  transcripts included via transcription). The conflicting composite PPA
  figure (98.7%, 110.5/113) is excluded. This is not a mixed DNA/RNA
  sample-prep comparison and not an RNA-virus-only subgroup score.
- DELFI (PMC6774252): 73% (152/208) sensitivity at a reported 98% specificity
  is from repeated 10-fold cross-validation (10 repeats), not a separately
  held-out validation cohort and not prospective screening validation.
  Classifier inputs are GC-corrected TOTAL and SHORT fragment coverage across
  504 genomic bins, 39 arm Z-scores and mitochondrial representation (not a
  short/long fragment-length ratio).
- cfMethyl-Seq: 80.7% sensitivity (95% CI 68.6-90.7) at 97.9% specificity,
  repeated random 25% test split, cohort 217 cancers/191 non-cancers, test
  n=102. No per-run denominator is inferred beyond what is printed.
- DRAGEN 4.2: CNV/SV 1-5 kb deletion F-score (H6=.926, L6=.391 selected) is a
  bounded Table S4 transcription; the .391 vs 39.20% comparator-table/prose
  conflict is preserved, not promoted. Phase 4 total single-sample runtime
  (AE20=1838.5s HG002; AE7=5521.21s AWS HG002) is a conventional-pipeline
  operational baseline, a proxy for foundation-model execution workload, not
  a model-execution benchmark; stage times cannot be summed due to
  concurrency, and host RAM capacity in the hardware comparator is not
  measured peak usage.
- Feng et al. 2025 (PMC12663285): source `evidence-expansion-dna-foundation-models-2025-5d8ca9bc`
  is reused unchanged; retrieval SHA-256 independently reconfirmed by Codex.
  Table 1 (Acceptor/Donor), Table 2 (Arabidopsis TATA/NonTATA), Table 5
  (pathogenic/common SNP AUC + Cohen's d) and Table 6 (eQTL/sQTL/paQTL/ipaQTL
  AUC + Cohen's d) are added as source-reported ({"origin": "independent_paper"})
  evaluations: Feng et al. benchmark third-party pretrained models and
  introduce none of them. Cohen's d is a signed effect size with no stated
  universal desirable direction and is recorded with metric_direction
  "unknown"; Table 6's AlphaGenome eQTL=0.8029/sQTL=0.7147 table cells are
  retained exactly even though source prose elsewhere states AlphaGenome's
  QTL AUC as approximately 0.80, a prose/table discrepancy that is not
  silently resolved. Short-window and long-window variant populations are
  distinct and are never pooled. Gene expression (Table 4), TAD analysis,
  CNN comparators, runtime figures and supplements remain outstanding for
  issue #19. No mapping is made to pathogen detection, tumour variant
  calling, ctDNA cancer detection, Human-5mC-to-ctDNA, or any BRCA-specific
  subgroup.

No new model execution. No qualified human scientific review. No broad
clinical validation is claimed for any mapping in this intake.
