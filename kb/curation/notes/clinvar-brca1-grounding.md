Status: written by one agent on 26 November 2026 from the record fields. A second agent checked every line and 48 were corrected (clinvar-brca1-grounding-review.md). No person has checked it. Where this note and the review differ, the review is right.

# Grounding notes: ClinVar and BRCA1 slice

472 observations grounded, one line each in grounding.jsonl. 141 have a system key ending in `-unspecified`; none has an unspecified subset or adaptation. 110 distinct system keys. 15 lines are low confidence (all from PhyloGPN Table 1 rows whose class does not clearly match a Lu et al. panel). ground.py does the work with ordered rules over system_name, system_version, system_checkpoint, parameters_text, metric_qualifier and source_locator.

## Policy for system keys

- A version, size or checkpoint is pinned only when system_name, system_version, system_checkpoint or parameters_text states it. "Not stated" in parameters_text or system_version wins over a version mentioned elsewhere.
- A named score file or release also pins the key: `dbnsfp-4-3a` for the Brandes et al. rows, `songlab/gpn-msa-hg38-scores` for GPN-MSA, the hegelab AlphaMissense files, the PrimateAI-3D BaseSpace files.
- Anything else ends in `-unspecified`. That includes tools that may only ever have had one public release (AlphaMissense, EVE, MTBAN, MPC). I did not use outside knowledge of release histories. If a human decides that single-release tools need no suffix, the unspecified count drops.
- The scoring variant is part of the key where it is stated: `-llr`, `-cls-l2`, `-phred` versus `-raw`, quantile versus raw for AlphaGenome, masked for SpliceAI.
- The compute platform is not part of the key. The three Evo 2 7B platform runs are all `evo-2-7b`, because system_version and system_checkpoint both say `evo2_7b`.
- Ablation models that are not released checkpoints get `ablation-<paper>-<row>`.
- checkpoints.json has no entry for any system in this slice. The only string hits are the hEVO checkpoints, which match on the letters "evo" and are unrelated, so no observation links to a checkpoint id.

## Adaptation

- `zero-shot`: foundation models scored by likelihood or embedding distance, and the Evo 2 paper rows that the qualifier labels zero-shot.
- `precomputed-scores`: released score files, dbNSFP, the Findlay table, and the Pejaver and Bergquist calibrations.
- `supervised`: anything fitted with labels: the EVEE probe, the Evo 2 mean-pooled probe, the EVEE control and the variant-type prior.
- `linear-probe`: only the NTv3 logistic regression, the one probe the file describes as linear.

## System keys

- `ablation-gpnmsa-st4-51-mammals`: GPN-MSA paper ablation model '51 mammals' (2 obs)
- `ablation-gpnmsa-st4-51-vertebrates`: GPN-MSA paper ablation model '51 vertebrates' (2 obs)
- `ablation-gpnmsa-st4-default`: GPN-MSA paper ablation model 'Default' (2 obs)
- `ablation-gpnmsa-st4-dont-replace-non-conserved`: GPN-MSA paper ablation model 'Don’t replace non-conserved' (2 obs)
- `ablation-gpnmsa-st4-dont-upweight-conserved`: GPN-MSA paper ablation model 'Don’t upweight conserved' (2 obs)
- `ablation-gpnmsa-st4-include-closest-primates`: GPN-MSA paper ablation model 'Include closest primates' (2 obs)
- `ablation-gpnmsa-st4-train-on-100pct-of-genome`: GPN-MSA paper ablation model 'Train on 100% of genome' (2 obs)
- `ablation-gpnmsa-st4-train-on-50pct-most-conserved`: GPN-MSA paper ablation model 'Train on 50% most conserved' (2 obs)
- `ablation-gpnmsa-st4-w-o-msa`: GPN-MSA paper ablation model 'w/o MSA' (2 obs)
- `ablation-gpnmsa-st4-window-size-16`: GPN-MSA paper ablation model 'Window size = 16' (2 obs)
- `ablation-gpnmsa-st4-window-size-256`: GPN-MSA paper ablation model 'Window size = 256' (2 obs)
- `ablation-gpnmsa-st4-window-size-32`: GPN-MSA paper ablation model 'Window size = 32' (2 obs)
- `ablation-gpnmsa-st4-window-size-4`: GPN-MSA paper ablation model 'Window size = 4' (2 obs)
- `ablation-gpnmsa-st4-window-size-64`: GPN-MSA paper ablation model 'Window size = 64' (2 obs)
- `ablation-gpnmsa-st4-window-size-8`: GPN-MSA paper ablation model 'Window size = 8' (2 obs)
- `ablation-gpnstar-st3-gpn-msa-exclude-10-closest-species`: GPN-Star paper ablation model 'GPN-MSA (exclude 10 closest species)' (1 obs)
- `ablation-gpnstar-st3-gpn-msa-no-species-curation`: GPN-Star paper ablation model 'GPN-MSA (no species curation)' (1 obs)
- `ablation-gpnstar-st3-gpn-star-default`: GPN-Star paper ablation model 'GPN-Star default' (1 obs)
- `ablation-gpnstar-st3-msa-transformer-like-architecture`: GPN-Star paper ablation model 'MSA Transformer-like architecture' (1 obs)
- `ablation-gpnstar-st3-no-evol-distance-encoding`: GPN-Star paper ablation model 'no evol. distance encoding' (1 obs)
- `ablation-gpnstar-st3-no-pooling-into-clades`: GPN-Star paper ablation model 'no pooling into clades' (1 obs)
- `ablation-gpnstar-st3-no-species-tree-no-evol-distances-no-clades`: GPN-Star paper ablation model 'no species tree (no evol. distances, no clades)' (1 obs)
- `ablation-gpnstar-st3-only-use-one-target-species-human`: GPN-Star paper ablation model 'only use one target species (human)' (1 obs)
- `alphagenome-all-outputs-quantile-max`: AlphaGenome API, maximum quantile over all outputs (15 obs)
- `alphagenome-avi-phred-unspecified`: AlphaGenome Variant Impact, PHRED scale, release not stated (3 obs)
- `alphagenome-avi-raw-unspecified`: AlphaGenome Variant Impact, raw score, release not stated (3 obs)
- `alphagenome-splice-composite-quantile`: AlphaGenome API, splice composite of quantiles (1 obs)
- `alphagenome-splice-composite-raw`: AlphaGenome API, original splice variant scorer (raw weighted sum) (1 obs)
- `alphagenome-splice-junction-quantile-max`: AlphaGenome API, splice junction outputs, maximum quantile (1 obs)
- `alphagenome-splice-junction-raw-max`: AlphaGenome API, splice junction outputs, maximum raw score (1 obs)
- `alphagenome-splice-site-quantile-max`: AlphaGenome API, splice site outputs, maximum quantile (1 obs)
- `alphagenome-splice-site-raw-max`: AlphaGenome API, splice site outputs, maximum raw score (1 obs)
- `alphagenome-splice-site-usage-quantile-max`: AlphaGenome API, splice site usage outputs, maximum quantile (1 obs)
- `alphagenome-splice-site-usage-raw-max`: AlphaGenome API, splice site usage outputs, maximum raw score (1 obs)
- `alphamissense-precomputed-hegelab`: AlphaMissense precomputed scores from alphamissense.hegelab.org (4 obs)
- `alphamissense-unspecified`: AlphaMissense, score release not stated (11 obs)
- `bayesdel-noaf-unspecified`: BayesDel without allele frequency, release not stated (12 obs)
- `bstatistic-dbnsfp-4-3a`: bStatistic, dbNSFP 4.3a precomputed (1 obs)
- `cadd-unspecified`: CADD, version not stated (8 obs)
- `cadd-v1-3`: CADD v1.3 (as supplied in the Findlay et al. table) (3 obs)
- `cadd-v1-7-phred`: CADD v1.7, PHRED scale (4 obs)
- `cadd-v1-7-raw`: CADD v1.7, raw score (GRCh37) (3 obs)
- `caduceus-ps-131k-d256-l16-llr`: Caduceus-PS 131k, d_model 256, 16 layers, likelihood ratio (12 obs)
- `consequence-rule-baseline`: Consequence-ranking rule baseline (3 obs)
- `dnabert-2-117m-cls-l2`: DNABERT-2 117M, CLS embedding L2 distance (14 obs)
- `esm-1b-650m-llr`: ESM-1b esm1b_t33_650M_UR50S, log-likelihood ratio (6 obs)
- `esm-1b-unspecified`: ESM-1b, release not stated (7 obs)
- `esm-1v-650m-model1-llr`: ESM-1v esm1v_t33_650M_UR90S_1, log-likelihood ratio (5 obs)
- `esm-2-650m-llr`: ESM-2 esm2_t33_650M_UR50D, log-likelihood ratio (5 obs)
- `eve-unspecified`: EVE, score file not stated (1 obs)
- `evee-covariance-probe-evo-2-7b-l27`: EVEE covariance probe on Evo 2 7B layer 27 (bioRxiv v4 deployed probe) (1 obs)
- `evee-unspecified`: EVEE classifier, version not stated (3 obs)
- `evo-1-unspecified`: Evo 1, checkpoint not stated (4 obs)
- `evo-2-40b`: Evo 2 40B (1M context) (4 obs)
- `evo-2-40b-base`: Evo 2 40B base (before context extension) (4 obs)
- `evo-2-7b`: Evo 2 7B (1M context) (13 obs)
- `evo-2-7b-base`: Evo 2 7B base (before context extension) (18 obs)
- `evo-2-7b-l27-meanpool-probe`: Mean-pooled embedding probe on Evo 2 7B layer 27 (1 obs)
- `evolutionary-action-unspecified`: Evolutionary Action, release not stated (4 obs)
- `fathmm-unspecified`: FATHMM, release not stated (4 obs)
- `genocanyon-dbnsfp-4-3a`: GenoCanyon, dbNSFP 4.3a precomputed (1 obs)
- `gerp-plus-plus-dbnsfp-4-3a`: GERP++, dbNSFP 4.3a precomputed (1 obs)
- `gerp-plus-plus-unspecified`: GERP++, release not stated (2 obs)
- `gpn-msa-llr`: GPN-MSA, published hg38 precomputed log-likelihood ratio (29 obs)
- `gpn-msa-unspecified`: GPN-MSA, score source not stated (3 obs)
- `gpn-star-m447-llr`: GPN-Star mammal m447, calibrated log-likelihood ratio (3 obs)
- `gpn-star-v100-llr`: GPN-Star vertebrate v100, calibrated log-likelihood ratio (3 obs)
- `hyenadna-medium-160k-llr`: HyenaDNA medium 160k, log-likelihood ratio (12 obs)
- `integrated-fitcons-dbnsfp-4-3a`: fitCons, dbNSFP 4.3a precomputed (1 obs)
- `lrt-dbnsfp-4-3a`: LRT, dbNSFP 4.3a precomputed (1 obs)
- `mpc-unspecified`: MPC, release not stated (2 obs)
- `msa-frequency-baseline`: MSA allele-frequency log-likelihood ratio baseline (no neural net) (2 obs)
- `mtban-unspecified`: MTBAN, score file not stated (1 obs)
- `mutationassessor-dbnsfp-4-3a`: MutationAssessor, dbNSFP 4.3a precomputed (1 obs)
- `mutpred2-unspecified`: MutPred2, release not stated (14 obs)
- `ntv3-650m-l11-logreg-probe`: NTv3 650M layer-11 embedding logistic-regression probe (1 obs)
- `nucleotide-transformer-2-5b-multispecies-cls-l2`: Nucleotide Transformer 2.5B multi-species, CLS embedding L2 distance (14 obs)
- `nucleotide-transformer-unspecified`: Nucleotide Transformer, checkpoint not stated (4 obs)
- `nucleotide-transformer-v2-500m-multispecies-llr`: Nucleotide Transformer v2 500M multi-species, log-likelihood ratio (12 obs)
- `pangolin-unspecified`: Pangolin, release not stated (3 obs)
- `phastcons-mammalian-dbnsfp-4-3a`: phastCons (mammalian), dbNSFP 4.3a precomputed (1 obs)
- `phastcons-primate-dbnsfp-4-3a`: phastCons (primate), dbNSFP 4.3a precomputed (1 obs)
- `phastcons-vertebrate-dbnsfp-4-3a`: phastCons (vertebrate), dbNSFP 4.3a precomputed (1 obs)
- `phylogpn`: PhyloGPN (481 bp receptive field) (26 obs)
- `phylop-100way`: phyloP 100-way (18 obs)
- `phylop-241way`: phyloP 241-way (4 obs)
- `phylop-447way`: phyloP 447-way (4 obs)
- `phylop-470way`: phyloP 470-way (4 obs)
- `phylop-mammalian-dbnsfp-4-3a`: phyloP (mammalian), dbNSFP 4.3a precomputed (1 obs)
- `phylop-mammalian-unspecified`: Mammalian phyloP, alignment not stated (3 obs)
- `phylop-phastcons-combined-gpnmsa`: phyloP and phastCons combination used by GPN-MSA training (2 obs)
- `phylop-primate-dbnsfp-4-3a`: phyloP (primate), dbNSFP 4.3a precomputed (1 obs)
- `phylop-unspecified`: phyloP (alignment not stated), release not stated (4 obs)
- `phylop-vertebrate-dbnsfp-4-3a`: phyloP (vertebrate), dbNSFP 4.3a precomputed (1 obs)
- `polyphen-2-humvar-unspecified`: PolyPhen-2 HumVar, release not stated (4 obs)
- `primateai-3d-precomputed-basespace`: PrimateAI-3D precomputed scores (primateai3d.basespace.illumina.com) (4 obs)
- `primateai-unspecified`: PrimateAI, release not stated (4 obs)
- `provean-dbnsfp-4-3a`: PROVEAN, dbNSFP 4.3a precomputed (1 obs)
- `revel-unspecified`: REVEL, release not stated (15 obs)
- `revel-v1-3`: REVEL v1.3 (3 obs)
- `rna-fm-unspecified`: RNA-FM, checkpoint not stated (3 obs)
- `sift-dbnsfp-4-3a`: SIFT, dbNSFP 4.3a precomputed (1 obs)
- `sift-unspecified`: SIFT, release not stated (4 obs)
- `sift4g-dbnsfp-4-3a`: SIFT4G, dbNSFP 4.3a precomputed (1 obs)
- `siphy-dbnsfp-4-3a`: SiPhy, dbNSFP 4.3a precomputed (1 obs)
- `spliceai-masked-precomputed-cadd-v1-7`: SpliceAI masked precomputed delta score, via CADD v1.7 annotations (3 obs)
- `spliceai-unspecified`: SpliceAI, score variant and release not stated (3 obs)
- `variant-type-prior-baseline`: Variant-type pathogenicity prior from benchmark labels (2 obs)
- `varity-r-loo`: VARITY_R, leave-variant-out precomputed scores (8 obs)
- `vest4-unspecified`: VEST4, dbNSFP release not stated (12 obs)

## Subsets per setting

- ClinVar missense AUROC:
  - `all`: the source's whole missense set. That is the Brandes et al. table, the Lu et al. Missense panel and the PhyloGPN Table 1 Missense row.
  - Cohorts from the rewire run: `clinvar-2023-12-holdout`, `clinvar-2023-12-holdout-af001` and `clinvar-2025-03-holdout`.
  - Lu et al. panels: `all-snv-consequences`, `noncoding-pooled`, `intron-non-splice`, `rna-gene`, `splice`, `canonical-splice-s2`, `start-loss`, `stop-gain`, `stop-loss`, `synonymous`, `utr3`, `utr5`, `missense-and-intron-non-splice` and `missense-and-utr3`.
  - PhyloGPN classes: `downstream`, `upstream`, `intronic`, `noncoding-class`, `splice-acceptor`, `splice-donor`, `start-codon`, plus the shared `stop-loss`, `synonymous`, `utr3` and `utr5`.
- BRCA1 SGE all, coding and noncoding SNVs: each setting is already one stratum, so every row is `all`.
- ClinGen PP3/BP4 thresholds: the evidence strength is the subset, because each number is the threshold for one strength. The ids are `pp3-supporting`, `pp3-moderate`, `pp3-3-points`, `pp3-strong`, `bp4-supporting`, `bp4-moderate`, `bp4-3-points`, `bp4-strong` and `bp4-very-strong`. The calibration data set itself is not in the file.
- COSMIC versus gnomAD AUPRC: `all`.
- ClinVar indel AUROC: `all`.
- ClinVar missense AUPRC and BRCA1 SGE missense threshold evidence: no observations in the file.

## Comparison result

36 groups have the same key, setting, metric and subset in two or more studies. 13 differ by more than rounding (comparisons.md). The 23 that agree are the GPN-MSA missense row (Lu et al. 0.906, PhyloGPN paper 0.91) and 22 ClinGen thresholds where Bergquist et al. 2025 reprints the Pejaver et al. 2022 calibrations for BayesDel, MutPred2, REVEL and VEST4.

All 13 differences are real disagreements about the same checkpoint on similar data:

- Nine are PhyloGPN and GPN-MSA, PhyloGPN paper versus Lu et al. The large gaps are in UTR classes, for example PhyloGPN on 5' UTR: 0.94 versus 0.601.
- Three are Evo 2 7B on BRCA1, Evo 2 paper versus the rewire run. All SNVs: 0.904 versus 0.875.
- One is ESM-1b 650M on ClinVar missense, Brandes et al. 0.892 versus Lu et al. 0.919.

## Things that look wrong or need a human

1. The missense setting holds non-missense results. 175 of its 238 rows are other consequences or pooled sets: Lu et al. All variants, Noncoding, Splice, UTRs and so on, and every PhyloGPN Table 1 class. They are grounded with their own subset ids, but they belong in a setting such as "ClinVar SNVs by consequence class". Only `all` and the three cohort subsets match the setting definition.
2. Rows trained on labels sit in settings defined as "without training on the labels":
   - In the indel setting, the EVEE covariance probe (trained on ClinVar SNVs), the Evo 2 mean-pooled probe and the NTv3 probe (both supervised on indels).
   - In the missense setting, the EVEE ClinVar-supervised control and the Lu et al. variant-type prior (fitted on the benchmark's own labels).
3. Lu et al. AlphaGenome on All variants reads 0.310 AUROC, worse than chance, while the same scorer gets 0.991 on Noncoding and 0.96 on Intron. Check whether the bar label was misread or the score sign is flipped for that panel.
4. Lu et al. has two splice sets: the Figure 1 Splice panel (N=11,042) and Supplementary Figure S2 canonical splice (N=11,047). The same AlphaGenome all-outputs quantile scorer reads 0.592 in one and 0.614 in the other. I kept them as separate subsets.
5. The Evo 2 paper CADD rows say "the version used is not stated" in parameters_text, but system_description says "CADD v1.7". I used `cadd-unspecified`. The description should be corrected or the version confirmed from the paper.
6. Subsets that may be the same class but that the file does not tie together. These were kept apart, which is why they are low confidence:
   - PhyloGPN 'Intronic' versus Lu et al. 'Intron (Non-splice)'.
   - PhyloGPN 'Start Codon' versus Lu et al. 'Start loss'.
   - PhyloGPN 'Noncoding', a class row, versus Lu et al. 'Noncoding', a pooled panel.
   - 'Stop Lost' and 'Stop loss' were merged at medium confidence.
7. GPN-Star Supplementary Table 3 'GPN-MSA (exclude 10 closest species)' (0.373 mean AUPRC) may be the same configuration as GPN-MSA Supplementary Table 4 'Default' (0.348 mean), which filters the closest primates. The file does not say so, so they have separate keys.
8. The COSMIC setting holds both mean and maximum over seeds for each GPN-MSA ablation. That is an aggregation, not a subset, so both rows share key and subset. A later comparison should pick one.
9. The rewire AlphaGenome AVI PHRED and raw rows have identical AUROC in every stratum. That is expected for a monotone transform, but the second row adds nothing.
10. source_names has no keys for the eight DOI study ids. comparisons.md labels them from the assessment names in the file.
11. The coding and noncoding definitions may differ between the Evo 2 paper (Genomic_Feature labels) and the rewire run (coding means missense, nonsense and synonymous; noncoding means all other consequences, including splice region). Both are grounded as `all` for their setting. Check the definitions before treating the Evo 2 7B gaps as model differences.
12. The ClinGen `value` is one bound of an interval. Bergquist et al. 'Moderate (+2)' and Pejaver et al. 'Moderate' share their lower PP3 bound but have different upper bounds, because Pejaver's Moderate spans +2 and +3 points. The comparison checks the stored bound only.
