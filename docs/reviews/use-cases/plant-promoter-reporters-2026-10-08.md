# Plant promoter reporters: bounded evidence research, 2026-10-08

Case 7 of 17 in the evidence programme ([rewire-benchmark-data #3](https://github.com/rewire-bio/rewire-benchmark-data/issues/3); benchmark programme [rewire-benchmarks #25](https://github.com/rewire-bio/rewire-benchmarks/issues/25), items B336 and BL336). Use case `use-case-plant-promoter-reporters`, slug `plant-promoter-reporters`. The article issue is [rewire.it #336](https://github.com/rewire-bio/rewire.it/issues/336) ("[Article plan] Choosing models for plant promoter reporters", open, last updated 2026-10-01). Links confirmed on 2026-10-08 07:28 UTC: `docs/omics/use-case-coverage-2026-09-30.md` row #336 names this use case, #25 lists B336 and BL336, and #3 lists "Plant promoter reporters" as the next unchecked case.

Starting commit: producer `main` 3bee06d98cf547359977fa3f47b33928b5094c17 (branch `codex/plant-promoter-evidence-20261008`, clean at start). No catalogue, mapping, definition, release, builder, test or generated file was changed. No model was run, trained or downloaded. Only sequence and label files, figure source tables, code files and papers were downloaded (about 93 MB in the ignored workbench). All times are UTC request start times from `workbench/plant-promoter-20261008/retrieval-log.tsv` and `search-log.tsv`.

## Disposition in brief

1. The existing records stand. All 12 AgroNT Figure 3e values match the pinned source table (SHA-256 `9cea450b...`, identical to the repository copy and to a fresh fetch of revision `78ec8156...`). One conflict is recorded here and not resolved: the Jores GC/motif linear model in maize protoplasts is 45% in the main text (page 849) and R2 = 0.44 in Figure 8a and in the author repository statistics file. The existing record `uc20260930-jores-result-maize-protoplasts-gc-motif-linear` holds 0.45 and is immutable. No cause is diagnosed.
2. The AgroNT promoter-strength train, validation and test files and the Jores train and test files contain exactly the same sequences per split; their label strings are not all identical and agree within 1e-15 (finding 1). So both papers draw on the same eligible held-out population. That does not show that the same rows were scored: the AgroNT Figure 3c table has fewer rows than the released test sets, and it has no identifiers.
3. The Figure 3e "CNN (Jores et al.)" values equal the species values printed in Jores Figure 8b. That shows the source values were reused or reproduced; it does not establish that a specific fitted checkpoint was reused.
4. Metric label ambiguity: the AgroNT Methods call the metric the coefficient of determination, but the printed Figure 3e AgroNT values equal the squared Pearson correlation of the Figure 3c predictions and not 1 - SSE/SST (recomputed here and independently by Codex). Existing labels are left as printed.
5. No source read compares two or more methods on a fixed-budget shortlist of newly chosen promoters in the same reporter assay. Jores and TargetGAN report experimental design validation without a matched comparator arm. Stable-plant performance is outside the exact use-case definition and is not a required endpoint for the B336 gap.
6. Disposition: docs-only. The optional additions considered (conflict annotation, six species-specific linear-model values, denominators) are declined for this case; the conflict is recorded in this dossier, and no new scientific release is made solely for documentation. The gap is B336, the missing fixed-budget, assay-matched comparator and calibration protocol. No other open or closed issue in rewire-benchmarks, rewire-benchmark-data, rewire-database or rewire.it besides #25 (B336, BL336), #3 and #336 covers a plant-promoter benchmark; the focused issue was posted by Codex after a fresh open and closed dedup as [rewire-benchmarks #33](https://github.com/rewire-bio/rewire-benchmarks/issues/33), linked to #25, #3 and #336. The ignored workbench draft (`benchmark-issue-draft.md`) is the pre-posting version.

## Existing inventory (unchanged)

Ten active mappings for this use case in `data/omics/use-cases/inputs.json`, 26 evaluations, 26 results. The latest release containing them is `2026-10-07-fc6ee0920cef` (also present in `2026-09-30-e37e3ab1284d`).

| Group | Mappings | Evaluations | Source record and locator |
|---|---|---|---|
| AgroNT vs Jores CNN, species-specific, six conditions (maize protoplasts or tobacco leaves host, by A. thaliana, S. bicolor, Z. mays sequences) | `use-case-mapping-plant-promoter-{maize-protoplasts,tobacco-leaves}-{a-thaliana,s-bicolor,z-mays}` | 12 | `agront-2024-fig3e-source` (`Figures/Fig3_panele.txt` lines 2 to 13, column R2); `agront-2024-paper-methods` |
| Jores GC/motif linear vs Jores CNN, pooled species, two hosts | `use-case-mapping-20260930-336-5e27f1b32dcb` (maize), `...-b8c3f8458c77` (tobacco) | 4 | `uc20260930-source-jores-2021`, Figure 8a,b; PDF SHA-256 `31f9157a...` |
| Feng et al. Arabidopsis TATA and NonTATA promoter sequence classification, five DNA foundation-model embeddings each | `use-case-mapping-amp-20261007-feng-promoter-{tata,nontata}` | 10 | `evidence-expansion-dna-foundation-models-2025-5d8ca9bc`, Table 2 |

Existing values (all author-reported, none independently reproduced):

| Condition | AgroNT | CNN (Fig3e) |
|---|---|---|
| Maize protoplasts, A. thaliana / S. bicolor / Z. mays | 0.62 / 0.68 / 0.71 | 0.58 / 0.65 / 0.69 |
| Tobacco leaves, A. thaliana / S. bicolor / Z. mays | 0.62 / 0.74 / 0.75 | 0.57 / 0.71 / 0.73 |

Jores pooled-species, Pearson correlation squared, 10% held-out set: maize protoplasts linear 0.45 (conflict, see finding 3), CNN 0.67; tobacco leaves linear 0.51, CNN 0.71. Feng AUC cells (DNABERT-2, NT-v2, HyenaDNA, Caduceus-Ph, GROVER): Arabidopsis TATA 0.951, 0.95, 0.9609, 0.9372, 0.9486; NonTATA 0.9457, 0.9395, 0.9547, 0.9437, 0.949. A fresh Europe PMC XML fetch of PMC12663285 (2026-10-08, SHA-256 `5d8ca9bc...`) is byte-identical to the 7 October snapshot and contains these cells.

## Search log (exact, dated)

Ten web-search queries (standard mode unless stated), GitHub issue and API lookups, and Europe PMC and Crossref calls. Query text is in `search-log.tsv`.

| Time (UTC) | Query (abridged) | Outcome |
|---|---|---|
| 07:29:01 | Q1 plant core promoter strength STARR-seq deep learning maize protoplasts tobacco 2025 2026 | Jores 2021 and follow-on pages; no new benchmark |
| 07:29:01 | Q2 AgroNT promoter strength CNN Jores prospective validation | AgroNT only |
| 07:29:01 | Q3 (extended) synthetic plant promoter design generative model validated protoplast reporter | TargetGAN (read), CRE.AI.TIVE (abstract), a 2026 review and a root-specific ML paper (titles only) |
| 07:29:16 | Q4 PlantCaduceus, PlantRNA-FM, PlantGFM promoter strength | nothing relevant |
| 07:29:16 | Q5 Plant Genomic Benchmark promoter strength new model vs AgroNT | PlantBiMoE (arXiv 2512.07113, read) |
| 07:29:16 | Q6 (extended) deep learning promoter design top-k validated fraction, tobacco leaf STARR-seq | TargetGAN again; Jores enhancer preprint (excluded) |
| 07:34:45 | Q7 iCREPCP | primary not found; not pursued |
| 07:34:45 | Q8 cross-species held-out plant promoter activity STARR-seq | gene-expression and peak models only; excluded |
| 07:34:45 | Q9 AgroNT fine-tuning recipe, seeds | nothing beyond the paper |
| 07:34:45 | Q10 Jores 2021 correction, stable-plant follow-up | no correction found; MinSyns (rule-based design) excluded |

Inclusion rule: a primary source that reports measured plant promoter or core-promoter reporter activity and either a predictive model evaluated against it or experimentally tested model-designed sequences. Exclusion: gene-expression, accessibility or enhancer endpoints, reviews, rule-based designs with no model comparison. Findings are bounded to these queries. Silence of the catalogue or of these queries does not show that no other evidence exists.

| Source | Decision | Read |
|---|---|---|
| Jores et al. 2021, Nature Plants 7:842-855, doi 10.1038/s41477-021-00932-y | Included (anchor) | full text, Methods, Fig 5 to 8, Extended Data Fig 10 caption; author repository code, notebooks, statistics, saved-model listing, figure source tables |
| Mendoza-Revilla et al. 2024, Commun Biol 7:835, doi 10.1038/s42003-024-06465-2 (AgroNT) | Included (anchor) | full XML, Methods, Results, Supplementary Data 1 to 3, Supplementary Information, peer review file; dataset and model repositories |
| Zhang et al. 2026, TargetGAN, Plant Communications (PMC13174209) | Included (prospective design) | full XML, Results, Methods, availability |
| Lin et al., PlantBiMoE, arXiv 2512.07113v1 (2025-12-08) | Included (third-party retrospective result) | main text and Table III; no appendix with per-dataset values found |
| Feng et al. 2025 (PMC12663285) | Included (existing AMP addition) | Table 2, Methods for promoter and splits |
| CRE.AI.TIVE, bioRxiv 10.1101/2024.12.05.626999 | Excluded (tomato proximal promoter of one gene, mutagenesis; different input and host) | abstract only |
| Jores et al. 2026 enhancer preprint (bioRxiv 10.64898/2026.04.26.720828) | Excluded (enhancers) | metadata and abstract only |
| MinSyns (PMC8454517), iCREPCP, DeepPlantCRE, Predmoter, grass-species expression models | Excluded (not model-versus-model promoter strength, or not found) | titles and snippets only |

## Findings

### 1. Shared population and test denominators

The AgroNT dataset card (`InstaDeepAI/plant-genomic-benchmark`, revision `78ec8156c2ffb3e5475277fdb7eb603294224e53`, licence CC BY-NC-SA 4.0) lists two promoter-strength sets, `leaf` and `protoplast`, each pooling the three species, sequence length 170. I downloaded the six FASTA files and the Jores repository files (commit `ace4ead59de364922fccdecd331554ccf0ac522b`, 2025-07-01) and compared them with the Python standard library (`scripts/pgb_vs_jores_tol.py`, output `cache/pgb-vs-jores-tolerance.txt`; float-based, see the label note below):

- Sequences: for each host, the set of test sequences equals the Jores `CNN_test_*.tsv` set exactly (7,154 and 7,595). AgroNT train plus validation equals the Jores `CNN_train_*.tsv` set exactly (65,004 and 68,213), so the AgroNT validation set (about 10.5%) is carved from Jores training data.
- Labels: matched by sequence, the label strings differ for 2,074 (leaf) and 1,936 (protoplast) test rows, and for 18,712 and 17,308 train plus validation rows. An exact Decimal comparison of the label strings (`scripts/pgb_vs_jores_decimal.py`, confirmed independently by Codex) gives a maximum absolute difference of 1e-15, so labels are equivalent within 1e-15; they are not exactly equal, and the cause of the small serialization differences is not established. A float subtraction reported 8.9e-16, a floating-point rounding artefact, and no precision beyond 1e-15 is claimed. The earlier workbench comparison (`cache/pgb-vs-jores.txt`) rounded labels to 6 decimals, a looser check, and is superseded.
- Headers carry the species (`_At`, `_Sb`, `_Zm`), so species counts of the released files are exact.

| Host | Train | Validation | Test | Test A. thaliana | Test S. bicolor | Test Z. mays |
|---|---:|---:|---:|---:|---:|---:|
| Tobacco leaves | 58,179 | 6,825 | 7,154 | 1,686 | 2,467 | 3,001 |
| Maize protoplasts | 61,051 | 7,162 | 7,595 | 1,690 | 2,638 | 3,267 |

All sequences are 170 bp and unique within each file, with no exact duplicate across splits within a host. Labels are log2 enrichment normalised to the 35S minimal promoter, averaged over two replicates (Jores Methods).

Row counts of prediction tables differ from the released test counts:

| Table | Tobacco leaves | Maize protoplasts |
|---|---|---|
| Released test file; Jores CNN predictions file | 7,154 | 7,595 |
| AgroNT Figure 3c (`Fig3_panelc.txt`, 14,592 rows, no identifiers) | 7,040 | 7,552 |
| Jores linear-model predictions file | 7,146 | 7,587 |

Figure 3c per species: tobacco A. thaliana 1,686, S. bicolor 2,420, Z. mays 2,934; maize A. thaliana 1,690, S. bicolor 2,620, Z. mays 3,242. Because Figure 3c has no identifiers, row identity with the released test sets cannot be established. As a descriptive check only, the labels rounded to 4 decimals of 7,032 of 7,040 and 7,547 of 7,552 Figure 3c rows also occur among the released test labels; this is a value comparison with possible ties and does not show that the scored rows are a subset. The reason for the count differences, and for the 8 fewer rows in the Jores linear file per host, is not stated in the sources read.

### 2. Splits, seeds, checkpoints

Jores (author repository at the commit above). `analysis/modelling.R` line 25 sets `set.seed(1)`; each promoter is then assigned to train or test by an independent draw (probabilities 0.9 and 0.1) within each system and species. The held-out unit is a promoter; the split is not grouped by sequence similarity or chromosome, and the two hosts were drawn separately. CNN (`CNN/CNN_train+evaluate.ipynb`): TensorFlow 2.2, bidirectional convolution layers and one convolution layer with 128 filters of width 13, dropout 0.15, dense 64, one output, first-layer kernels initialised with motifs; Adam, mean squared error, up to 25 epochs, batch 128, `validation_split` 0.1, early stopping (patience 5). In the inspected notebooks there is one training call per host and no seed setting; this does not show how many models the authors trained before the reported one. Saved Keras models are listed in the repository (`CNN/model_leaf`, `CNN/model_proto`); whether they are the checkpoints behind the printed values is not stated. Linear model: base R `lm()` on GC, six core-element scores and 72 TF-motif scores.

AgroNT. Methods Sec16 describes IA3 fine-tuning (about 1% of parameters) with a regression head; Sec21 says the original Jores train and test files were downloaded. The main text, Supplementary Information (Supplementary Table 1 lists pre-training hyperparameters only) and peer-review file give no fine-tuning learning rate, epochs, seeds, stopping rule or checkpoint choice. The Hugging Face model repository (revision `b0e1ea1f53a2bf5bb29f8eab7a7e553bf06c1ab1`) lists the pre-trained base model only, and the GitHub repository `instadeepai/nucleotide-transformer` (commit `2dc37b86e16a6970fbc731751f7719d9f676f7f9`) lists an AgroNT inference notebook and no promoter-strength fine-tuning script. I found no fitted promoter-strength head or checkpoint in those listings; this is bounded to them.

### 3. Metric ambiguity and the 0.44 / 0.45 conflict

Recomputed from `Fig3_panelc.txt` (columns Species, Model, Label, Predicted) with `scripts/fig3c_check.py`:

| Condition | Printed Fig 3e | Squared Pearson | 1 - SSE/SST |
|---|---:|---:|---:|
| Maize protoplasts A. thaliana / S. bicolor / Z. mays | 0.62 / 0.68 / 0.71 | 0.6247 / 0.6837 / 0.7061 | 0.6064 / 0.6464 / 0.7036 |
| Tobacco leaves A. thaliana / S. bicolor / Z. mays | 0.62 / 0.74 / 0.75 | 0.6184 / 0.7392 / 0.7453 | 0.5974 / 0.7197 / 0.7428 |

All six printed values round from the squared Pearson column; none matches 1 - SSE/SST. The AgroNT Methods call the metric the coefficient of determination (Sec21). The source is therefore ambiguous about the statistic, and the existing "R2" labels are not changed. The pooled text values (0.70, 0.73) are consistent with both statistics.

Jores prints "Pearson's R2" and its notebook computes `corr()**2` rounded to 2 decimals. Statistics file values (`CNN/CNN_test_*_stats.tsv`, `figures/rawData/linear-model_*_stats.tsv`) with a recomputation from the prediction files in parentheses:

| Host and model | Pooled | A. thaliana | S. bicolor | Z. mays |
|---|---|---|---|---|
| Tobacco leaves CNN | 0.71 (0.7144) | 0.57 (0.5734) | 0.71 (0.7138) | 0.73 (0.7310) |
| Maize protoplasts CNN | 0.67 (0.6697) | 0.58 (0.5832) | 0.65 (0.6475) | 0.69 (0.6888) |
| Tobacco leaves linear | 0.51 (0.5101) | 0.34 (0.3371) | 0.52 (0.5215) | 0.51 (0.5134) |
| Maize protoplasts linear | 0.44 (0.4377) | 0.28 (0.2757) | 0.40 (0.4041) | 0.47 (0.4661) |

The CNN species values equal the AgroNT Figure 3e "CNN (Jores et al.)" column in all six cells.

Observed conflict, not diagnosed: the main text on page 849 says the linear models "explained 51% and 45%" (tobacco, maize). Figure 8a (page 10 of the author-hosted PDF, SHA-256 `31f9157a...`) prints R2 = 0.44 for the maize linear model, and the repository statistics file gives 0.44. The existing record's value 0.45 is immutable and is left as is.

### 4. Uncertainty and run variability

Neither source prints an interval, seed list or run-to-run variation for these comparisons. Printed values are two-decimal single numbers. The sources do not support a stated margin between methods. No uncertainty is computed here.

### 5. Split structure and pre-training exposure (separate questions)

Supervised split. The held-out unit is a promoter drawn at random; the held-out sequences are exactly disjoint from the training sequences within a host, but the split is not a sequence-group, homology or unseen-species holdout, and the inspected sources contain no similarity or homology analysis. The two hosts were split by separate draws, so the same promoter identifier can be a test promoter in one host and a training promoter in the other. Whether that matters depends on the declared training condition: other-host labels can be legitimate inputs in a host-transfer design, and no universal leakage claim is made. A protocol should declare which labels a method may use.

Pre-training exposure. This is unresolved without a sequence or coordinate check, which was not done. AgroNT Supplementary Data 1 (SHA-256 `c3b77f10...`) lists A. thaliana TAIR10.1, S. bicolor Sorghum_bicolor_NCBIv3 and Z. mays Zm-B73-REFERENCE-NAM-5.0 among the pre-training reference genomes. The Jores script `promoter_annotation/extract_promoter_seqs.sh` takes promoters from TAIR10, Sorghum_bicolor_NCBIv3 and maize B73 RefGen_v4. Matching assemblies for two species make it plausible that held-out promoter loci lie within pre-training genomes. They do not prove that every held-out 170 bp sequence was in the pre-training chunks (Methods: 6,100 nt chunks, N replaced, no stated locus handling), and the maize assemblies differ. Supervised held-out labels and unlabelled pre-training exposure remain separate questions.

### 6. Assay context and the 35S enhancer

Jores Methods: models were trained and validated on the libraries with the 35S enhancer in the dark, 90% train and 10% held out. The AgroNT paper does not state the enhancer or light condition; the sequence identity in finding 1 indicates that its promoter files derive from the Jores model data, which Jores describes as enhancer-in-dark libraries. The Jores libraries without the enhancer are a different assay context: TargetGAN (below) uses promoters measured without enhancer in dark maize protoplasts. Reporter hosts (maize protoplasts, tobacco leaves) are assay systems; A. thaliana, S. bicolor and Z. mays are the species supplying the 170 bp sequence (-165 to +5 around the annotated TSS). The Methods of both papers use only core promoters; terminators (AgroNT Figure 3f) are a separate task and are not read as evidence here.

### 7. Prospective and design evidence

Jores in silico evolution (Figure 8c to f, Extended Data Fig 10, Methods "In silico evolution of promoter sequences"). Starting sequences were 150 native and 160 synthetic promoters. In each round every single-nucleotide variant was scored by the CNN and the best kept; sequences after 3 and 10 rounds were synthesised and their strength measured by STARR-seq in tobacco leaves and in maize protoplasts, with and without the 35S enhancer (about 210 to 245 promoters measured per condition and round, Figure 8c,d). Scoring used the tobacco CNN, the maize CNN, or the mean of both. The endpoint is measured strength against the unevolved starting sequences; the text reports the best result when the scoring model matched the assay. Limits: there is no random-mutation, linear-model or AgroNT arm, the CNN was trained on the enhancer-in-dark libraries, and no stable-plant measurement was made.

TargetGAN (Plant Communications, PMC13174209, CC BY-NC-ND 4.0). Maize protoplast STARR-seq of 170 bp core promoters measured without enhancer in the dark. A generative network trained on the Jores natural promoters (random 8:1:1 split) and a published pre-trained predictor (iCREPCP, Deng et al. 2023; not retrieved) produced designs; 5,250 designs across nine activity targets plus 750 natural promoters were synthesised, and a replicate-variation filter (coefficient of variation below 30% over three replicates) retained 2,909 designs and 671 natural promoters. The endpoint is agreement between predicted and measured activity and comparison with the strongest tested natural promoter. Limits: one design pipeline with no matched alternative or random arm, a substantial share of designs removed by the filter (so any hit fraction depends on the denominator; none is computed here), an assay context (no enhancer) that differs from the Jores model-training libraries, and no comparison with AgroNT or the Jores CNN. Code `xlxianglei/TargetGAN` (commit `352e5d5a970fdcf40f1060c1d1827ac6616c628f`) and Figshare 10.6084/m9.figshare.31482604 exist and were not opened.

PlantBiMoE (arXiv 2512.07113v1, 2025-12-08) reports an average "Promoter strength" R2 over the two released promoter sets and lists an AgroNT value of 73.85 taken from the AgroNT paper. That value does not match the AgroNT text values (0.70 and 0.73) and its source is unexplained. The comparison is retrospective and not a matched protocol; no intervals or seeds were found; the repository link returned HTTP 404 on two routes. Not added.

Gap statement (bounded to the searches above). The sources read contain no comparison of two or more methods choosing a fixed-budget shortlist of candidate promoters in the same reporter assay, and no calibration of predicted strength for new candidates against measured strength. That is the B336 gap. Stable-plant performance is outside the exact use-case definition and is not required for this endpoint.

### 8. Feng et al. TATA and NonTATA (existing AMP addition), endpoint separation

Feng Methods take the multi-species promoter datasets from iPro-WAEL (Zhang et al., NAR 2022; PMC9561371): positives are promoter sequences near the TSS and negatives are computationally chosen non-promoter regions with high sequence similarity. Embeddings are frozen and a random forest is trained (original splits where defined, otherwise a random 70:30 split); the per-task split sizes are in Supplementary Data 6, which was not inspected. The task is sequence identification of promoter versus non-promoter in TATA and NonTATA subsets. It is not reporter strength, not 170 bp core promoters, and not R2. The ten cells stay in their own protocol and are not combined with Figure 3e or Figure 8 values.

## Access and reuse (separately)

| Item | Terms found |
|---|---|
| AgroNT paper | CC BY 4.0 (XML licence element; Crossref) |
| Jores paper | Nature Plants, not open access in Europe PMC; Springer Nature text-and-data-mining terms in Crossref. The author-hosted PDF (`queitschlab.gs.washington.edu`) hash equals the 30 September audit (`31f9157a...`); reuse terms of that copy not stated |
| Jores code, data, models | `tobjores/Synthetic-Promoter-Designs-...` has no licence (GitHub API null; no licence file in the tree at `ace4ead5...`). Saved CNN models and test and train files are in the repository. Raw reads: NCBI SRA PRJNA714258 (not downloaded) |
| AgroNT benchmark data | Hugging Face `plant-genomic-benchmark`, CC BY-NC-SA 4.0; the data are the Jores data re-hosted, and the Jores repository carries no licence, so upstream terms are not established |
| AgroNT weights and code | base model `InstaDeepAI/agro-nucleotide-transformer-1b` CC BY-NC-SA 4.0; GitHub API licence "other" (NOASSERTION), no licence file found at the repository root path; no fitted promoter-strength head found; pre-training code stated proprietary (Code availability) |
| Pre-training data | listed in Supplementary Data 1 and hosted as `InstaDeepAI/plant-multi-species-genomes` (no licence in the card read) |
| TargetGAN | paper CC BY-NC-ND 4.0; code no licence (GitHub API null); data and weights on Figshare (licence not read; not opened) |
| PlantBiMoE | arXiv v1; code repository not reachable |
| Feng et al. | CC BY 4.0 (XML); Supplementary Data 6 not inspected |

No paid access, access workaround, outreach or model execution was used.

## Endpoint separation

| Source and protocol | Pooled species, one host | Species-specific, one host | Promoter versus non-promoter classification | Experimental design validation |
|---|---|---|---|---|
| Jores Figure 8a,b (linear, CNN) | Yes | Printed in colour, not in records | | |
| AgroNT Figure 3e | | Yes (printed R2; numerically squared Pearson) | | |
| AgroNT text, Figure 3c pooled (0.70, 0.73) | Yes (not in records) | | | |
| Feng Table 2 | | | Yes (AUC, Arabidopsis only) | |
| Jores evolution (Figure 8c to f) | | | | Yes (CNN-guided, no comparator arm) |
| TargetGAN | | | | Yes (one pipeline, maize protoplast, no enhancer) |
| PlantBiMoE Table III | Yes (average over two hosts, third party) | | | |

Reporter strength prediction on a random held-out sample is not top-k candidate selection and not calibration of a prediction for a new promoter. Stable-plant fitness is outside the use-case definition.

## Unresolved or unretrieved

- Why the AgroNT Figure 3c tables have 7,040 and 7,552 rows against 7,154 and 7,595 released test rows, and which rows were scored (no identifiers); why the Jores linear file has 7,146 and 7,587 rows.
- Which statistic the AgroNT authors intended by "R2" (printed values equal squared Pearson of Figure 3c).
- The 0.44 (Figure 8a, repository) versus 45% (text) difference in Jores; no erratum was found in Crossref.
- AgroNT fine-tuning settings, seeds, checkpoint choice and a fitted head: not found. Whether the AgroNT promoter results are reproducible from released artifacts is not established. Whether the Jores saved models produced the printed values is not stated.
- Pre-training exposure of the held-out promoters: no sequence or coordinate check was done.
- Sequence-group or homology structure across the random split: not analysed in the sources.
- Not read: the iCREPCP predictor, TargetGAN Figshare data and weights, CRE.AI.TIVE full text, PlantBiMoE per-dataset tables, Feng Supplementary Data 6, Jores Supplementary Tables 6 and 7 (present in the repository as XLSX).
- Terminator evidence (Figure 3f) and other AgroNT tasks are outside this use case.

## Bounded access failures

| Time (UTC) | Request | Result | Next approach |
|---|---|---|---|
| 07:29:38 | bioRxiv API for the Jores 2021 preprint | HTTP 500 | not needed; author-hosted PDF and repository used |
| 07:31:47 | Europe PMC XML for PMC10246763 (Jores) | HTTP 500 | author-hosted PDF (SHA matches 30 September) |
| 07:34:32 | GitHub API, `HUST-Keep-Lin/PlantBiMoE` | HTTP 404 | github.com page (07:34:37), also 404; stopped |
| 07:34:32 | bioRxiv API for CRE.AI.TIVE | HTTP 500 | Europe PMC metadata (abstract only) |
| 07:35:12 | `instadeepai/nucleotide-transformer` LICENSE at HEAD | HTTP 404 | GitHub API licence field ("other") |

## Cached bytes (ignored workbench `workbench/plant-promoter-20261008/cache/`)

Full manifest in `cache/SHA256SUMS`. Key SHA-256 values (retrieved 2026-10-08 unless noted):

- AgroNT XML (Europe PMC) `1f92fdc63b234532121f5a58cce36ef8a24ed4499b6cdc881557934ce1d31b41`; the 23 September snapshot (uncompressed `bcc1ad6d...`) gives identical extracted body text. Supplementary Data `c3b77f104b78e15ac8576d4e5a2d7c6c413dc47076d49672705c200b5a8bb147`; Supplementary Information `883ad9d945cdfce7f6f71d330c5efb010caff86fc7a2b4241ab824b6d5ee7743`; peer review file `30f6798c2ebde804323e1103d44f8b526212a7de3544221c6a36444ae2c9cbdf`.
- PGB revision `78ec8156c2ffb3e5475277fdb7eb603294224e53`: `Fig3_panele.txt` `9cea450b579aa1eb61ff3bcb70e017410402abd6261aef8fc270cafc926a7c7b`; `Fig3_panelc.txt` `5d8d71fd147d97b1828df81e3ccf3be3c9de593711ab634fbde07b498716ea43`; `leaf_test.fa` `781f2279...`; `protoplast_test.fa` `139fa37c...`; dataset card `a746bdd6...`.
- Jores PDF `31f9157ae1ad52c2f405348cf20f87ab4fb17f26a0b1a91032a9563bfadbd47a`; repository commit `ace4ead59de364922fccdecd331554ccf0ac522b`; `CNN_test_leaf.tsv` `8015b4ee...`; `CNN_test_proto.tsv` `6fe91dd6...`; `CNN_test_leaf_stats.tsv` `23ef719b...`; `CNN_test_proto_stats.tsv` `91ca0b9c...`; training notebook `c873ffcd...`; `analysis/modelling.R` `95eaf32d...`.
- TargetGAN XML `79672fb829002967ffbae4a7038fa6642da129c923fcabfbb5cbfaf1b747e150`; PlantBiMoE PDF `8cfc00345339ef253152e96d9628c5171c43252c7fe23d81a5abf572224b4e83`; Feng XML `5d8ca9bcf88cc1b38ad667906a2e4699b1aefa6d31c6f49259784930353f3202`.
- Dataset and model repository listings: PGB `78ec8156...`, model `b0e1ea1f53a2bf5bb29f8eab7a7e553bf06c1ab1`, multi-species genomes `c446274fccf04acb7ca8e10d5c401570bf6676d8`, nucleotide-transformer `2dc37b86e16a6970fbc731751f7719d9f676f7f9`, TargetGAN `352e5d5a970fdcf40f1060c1d1827ac6616c628f`.

Scripts used for the tables above (ignored workbench `scripts/`): `fetch.sh`, `jats2txt.py`, `xlsx_dump.py`, `pgb_counts.py`, `pgb_vs_jores_tol.py`, `pgb_vs_jores_decimal.py`, `fig3c_check.py`, `fig3c_match.py`, `jores_check.py`. Other exploratory script outputs in the ignored workbench are not used in this dossier.

## Review status

Automated source reading by the Sonnet evidence worker, corrected after Codex independent review. Codex re-fetched the Jores PDF (hash identical to the historic value), checked Methods, the Figure 8 caption and prose, verified the 12 historic AgroNT values, and reproduced the Figure 3c recomputation. Recomputed statistics and counts in this dossier are derived from released data and are not source-reported values. No independent human scientific review, no model execution, no outreach. Disposition: docs-only.
