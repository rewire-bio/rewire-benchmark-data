# Regulatory variant and gene follow-up: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-regulatory-variant-20261009/` (384 records from the collector, 388 after review). Use case: `use-case-regulatory-variant-gene-follow-up`.

Reviewer: a separate Claude review agent that did not extract the batch. No human review is claimed. Nothing was executed or reproduced; this is a check of transcription against the pinned sources and of the relevance judgements.

## Outcome

- All four pinned artifacts re-download to their recorded SHA-256. The archived `artifacts/*.gz` copies decompress to the same bytes. Tang et al. (CC BY-NC-ND) has no archive, as recorded.
- All 160 results match their source cells, including all 36 Gschwind bootstrap intervals and all 96 Manzo bracketed standard errors. No number was wrong.
- Four origins were wrong. In Gschwind et al., EPIraction and EpiMap come from co-authors' groups, so all four of their evaluations are now `author_reported`. In Tang et al., MPRAnn is a published architecture that the authors retrained, so its two evaluations are now `independent_paper`.
- The Manzo et al. methods contradict themselves about how Enformer, Borzoi and HyenaDNA were run. Geneformer, a single-cell model, was applied to DNA tokens. Twelve Manzo evaluations (Enformer, Borzoi and Geneformer in each of the four cell lines) are excluded from the judgements with reasons.
- The Gschwind K562 training stratum is now `outside_scope`, so it is not shown as evidence.
- No source `evidence_concerns` were raised. Every problem is limited to specific rows or is a property of the design.
- All eight judgements pass after correction and are `source_checked`, with `reviewed_evaluations` set. Pins are left for the integrator.

## How the check was done

1. Downloaded each `artifact_url` into an empty directory: the three article XMLs, and the Gschwind Europe PMC `supplementaryFiles` zip. In the zip I hashed the MOESM3 inner zip and the `Supplementary_Table_3.xlsx` member, and read `Supplementary_table_legends.docx`.
2. Read the workbook with a stdlib OOXML reader written for this review, and the Manzo and Tang tables from the article XML with my own `table-wrap` reader, which resolves Tang's row-spanning Training task cells. The extractor's `extract/*.py` were not imported or run.
3. Matched every result to its cell and compared raw text, `printed_value` (shortest round-trip decimal for XLSX; the Unicode minus kept for Manzo), `numeric_value`, the `uncertainty` bounds or standard error, metric, qualifier, locator, and the linked configuration and protocol. Expected 36 + 96 + 28 = 160 cells; all matched once, none missing or duplicated. Every Gschwind point estimate lies inside its interval.
4. Read the three articles in full, including author lists and references, to check origins, versions, adaptations and the collector's concerns.
5. Searched the store of main and every `rewire-benchmark-data-*` worktree, and every batch folder in them, for `model`, `method`, `baseline`, `pipeline` and `service` records matching each new family (script `dupsearch.py` in the review scratch directory).
6. Integration dry run. `addBatch` against a scratch copy of the store passes (vocabularies, declared attributes and record validation; SHACL not run). With the eight `assessed_by` links added and the judgements pinned in memory, `deriveUseCaseInputs` gives all eight new judgements and all five existing ones as `active`. The K562 training judgement is active with no evaluations, as `outside_scope` requires.

## Sources and hashes

| Source ID | Artifact checked | SHA-256 (re-downloaded 2026-10-09) | Matches record |
| --- | --- | --- | --- |
| `regulatory-variant-20261009-source-gschwind2026` | PMC13471189 full-text XML | `df07ed8c37a62732ba0ae26b74a6c8bcb9b48540fefd03c064115d9a87a3b642` | Yes |
| `regulatory-variant-20261009-source-gschwind2026-table-s3` | `2023-11-20318B-s3/Supplementary_Table_3.xlsx` in MOESM3 | `81f7f2a3c4379adfca9db362a3aa2c2a8b4121bed0a54337a747f9afeee85904` | Yes; MOESM3 zip `88eb6c52...` also matches |
| `regulatory-variant-20261009-source-manzo2025` | PMC12562713 full-text XML | `c49e7cef821d7c1a7966db9922b58c2f51d852df13f5cdc3969bf54818e5ed9e` | Yes |
| `regulatory-variant-20261009-source-tang2025` | PMC12261763 full-text XML | `f6925cc2d93d0694ccc689970207c2df9b7b0d2562d276ede99f0c78d413b08b` | Yes |

The outer supplementaryFiles zip hashed `70804511...` this time, not the recorded `78dc8641...`. It is assembled per request, as `hash_scope` says, so this is expected.

## Values checked

| Source table | Results | Metrics | Mismatches |
| --- | --- | --- | --- |
| Gschwind Supplementary Table 3, sheet 'Held-out benchmarks', rows 2 to 37 | 36 | weighted AUPRC, precision and recall at threshold, each with a 95% bootstrap interval | 0 |
| Manzo Table 1, 24 models by 4 cell lines | 96 | Pearson r with bracketed standard error | 0 |
| Tang Table 1, 14 models by 2 cell lines | 28 | Pearson r | 0 |
| Total | 160 | | 0 |

Consistency with the prose: Gschwind Results give AUPRC 0.66 versus 0.56 for ENCODE-rE2G and ABC on the combined K562 data, matching the K562 rows (0.666, 0.561). Manzo prose differs from its table in places (see Conflicts).

## Corrections made in the batch

None changes a number, interval or standard error. The batch is not in the store, so fields were edited in place. The collector's copy has SHA-256 `714fe35eb539ff221871cf0d105706f282137493fb8659313b3ffb8b975e11a4`. The reviewed `batch.jsonl` has SHA-256 `f61e8648971dc38b5a0fd0990fcdd050893b0da33db691aac999a95684836edb`; `review.json` binds it and every other file in the folder.

1. **Status.** Every record is now `source_checked`. Results and claims got a `review` block, with the collector's note kept.
2. **Gschwind origins.** The four EPIraction and EpiMap evaluations changed from `independent_paper` to `author_reported`. EPIraction (reference 27) is by co-authors Ramil N. Nurtdinov and Roderic Guigó. EpiMap (reference 8, Boix et al. 2021) includes co-authors Benjamin T. James and Manolis Kellis. Two claims, `...-claim-gschwind2026-epiraction-developer` and `...-claim-gschwind2026-epimap-developer`, record this.
3. **Tang origin.** The two MPRAnn evaluations changed from `author_reported` to `independent_paper`. MPRAnn comes from the lentiMPRA study (reference 73); Tang et al. retrained it "with model structure and training parameters obtained from Github directory of original publication". ResidualBind, the baseline CNN and the embedding probes are the authors' own and stay `author_reported`.
4. **Family records.** Eight neural-network families (Borzoi, Caduceus, Enformer, GENA-LM, GPN, HyenaDNA, Sei, TREDNet) were `method` records with `-method-` IDs. They are now `model` records with `entity_level` `family` and IDs `regulatory-variant-20261009-model-*`, matching DNABERT-2, Nucleotide Transformer, Geneformer and ChromBPNet, which are models in the store. Configuration links were updated. The IDs are new, so no stored ID changes. Distance to TSS, element-promoter correlation, EpiMap, EPIraction, MPRAnn, ResidualBind and the lentiMPRA probe remain `method`.
5. **Descriptions.** All 14 family descriptions stated facts not in the sources. They now quote the sources. Manzo Table 3 itself contains errors (it calls Caduceus Transformer-based, and gives GENA-LM the Geneformer applications text), so only uncontested entries were used.
6. **Reused model links.**
   - The DNABERT-2 configuration linked `catalog-model-dnabert-2`, which is `alias_of` `discovery-model-dnabert-2`; it now links the canonical record.
   - The four Nucleotide Transformer v2 configurations (50M to 500M) linked `catalog-model-nt-v2`, whose `version` is "50M multi-species". They now link the family `discovery-model-nucleotide-transformer`, as the other NT configurations already did.
7. **Configuration versions.** 38 configurations had a `version` such as "Borzoi (as printed)", which is a label, not a version. Each now has `missing_metadata.version` `unreported` with the printed label in the note; `reported_name` keeps the label. The Tang HyenaDNA configuration now has `version` "hyenadna-tiny-1k-seqlen-d256 (Methods 'HyenaDNA')", which the source names.
8. **Configuration notes.**
   - The Tang GPN (human) configuration notes that it is a custom checkpoint the authors trained on hg38 (Methods 'Custom GPN').
   - The ABC configuration's method type changed from `supervised_machine_learning` to `conventional_pipeline`. ABC "multiplies enhancer activity and 3D contact frequency" (Results).
   - Enformer, Borzoi and HyenaDNA `parameters` and `comparison.adaptation` now state the source's conflicting descriptions instead of choosing one. Geneformer got a `model_identity_note`.
9. **Tang element name.** The dataset description, and the population of each HepG2 evaluation, said "LDLR" as though the source prints it. They now say the source prints 'LDLT', presumably LDLR.
10. **Claims.**
    - `...-claim-manzo2025-prose-averages`: the locator was wrong. The averages are in Results 2.1 paragraph 5, not paragraph 2. The value now also records the Results 2.3 figures and the HeLa ranking conflict.
    - Added `...-claim-manzo2025-adaptation-conflict` and `...-claim-manzo2025-snp-counts`.
    - `claims.csv` was updated to match.
11. **Limitations.** All eight protocol and judgement `limitations` were rewritten (below), and the rationales and citation locators corrected.

## Reused and new records

| Record | Check | Outcome |
| --- | --- | --- |
| `ucc-research-method-mprabc-abc`, `ucc-research-method-mprabc-re2g` | Same models as Gschwind's ABC and ENCODE-rE2G | Accepted |
| `ucc-research-data-mprabc-k562-crispri` | Gschwind Results: 10,356 pairs, 471 positives, the record's counts | Accepted. Its protocol is now `outside_scope` |
| `catalog-model-dnabert-2` | `alias_of` `discovery-model-dnabert-2` | Replaced by the canonical record |
| `catalog-model-nt-v2` | `version` "50M multi-species" does not fit 100M to 500M | Replaced by `discovery-model-nucleotide-transformer` |
| `discovery-model-nucleotide-transformer`, `catalog-model-geneformer`, `discovery-model-chrombpnet` | Family records | Accepted |
| New HyenaDNA, Caduceus, Enformer, Sei, Borzoi, GENA-LM, GPN and TREDNet families | No `model` or `method` record for these families in main or any worktree. Paper-specific `pipeline` records exist (for example `mrnabench-variants-2025-method-hyenadna-small-32k`, `paper-model-53f00fb44417cec450` "Caduceus†", `alphagenome-2026-comparator-*` Borzoi ensembles), but they are configurations of other studies, not families | Accepted as new `model` families |
| New EPIraction, EpiMap, distance and correlation baselines, MPRAnn, ResidualBind, lentiMPRA probe | No matching record anywhere | Accepted |

Two pre-existing duplicate pairs remain in the store and are not changed here: `catalog-model-dnabert-2` and `discovery-model-dnabert-2`, and the NT records. They are worth a separate cleanup.

## Collector concerns: decisions

1. **Gschwind K562 training stratum.** **Decision: `outside_scope`.**
   - ENCODE-rE2G was fitted on these pairs (scored by hold-one-chromosome-out cross-validation, Results).
   - Every predictor's threshold was set at 70% recall on them (Methods; Supplementary Table 3 legend), so "recall at threshold" is near 0.7 by construction. The sheet prints 0.710 to 0.755 for all six predictors.
   - The pairs are already linked through the existing K562 CRISPRi mapping.
   - As `proxy` the values would appear next to the held-out stratum and invite a held-out reading. As `outside_scope` they are recorded and reviewed but supply no evidence, which meets the requirement that they not be shown as held-out performance. The judgement keeps the in-sample limitation.
2. **Held-out CRISPR stratum: direct or proxy.** **Decision: `proxy`.** The question asks which variants, elements and genes to perturb at a disease locus. Element-gene links from whole-element CRISPRi bear on the element and gene part, but the use case's own exclusions say whole-element perturbation is not allele editing and a link is not a causal disease role. The existing K562 CRISPRi judgement is `proxy` on the same reasoning. The limitations now also say that held-out K562 pairs from other screens remain, and that thresholds and model design were set on K562.
3. **Thresholds** (collector item 5). Resolved. Methods 'Collection of published predictions and baseline predictors' and the Table 3 legend set every predictor's threshold at 70% recall on the combined K562 data. This is in the limitations.
4. **Manzo SNP counts.** Confirmed. For K562, Table 4 gives 19,237 + 2,756 = 21,993, against 19,321 in the header. For HepG2, 14,183 raQTLs plus a SORT1 saturation set and 284 SNPs do not explain 16,255. NPC (14,042) and HeLa (1,962 + 1,614 + 1,665 = 5,241) agree. No filtering step is stated. Recorded in a claim and in the K562 and HepG2 limitations. No value depends on the counts.
5. **Manzo prose averages.** Confirmed and extended. Results 2.1 paragraph 5 gives averages over nine dataset-level correlations (TREDNet 0.297, ChromBPNet 0.289, SEI 0.276). Results 2.3 paragraph 3 gives TREDNet 0.318 and SEI 0.295. The paragraph after Table 1 says Enformer (0.245) ranks second in HeLa "only to SEI (0.279)", but Table 1 prints SEI 0.280 and ChromBPNet 0.289. Table values are recorded; the claim and the limitations name the conflicts.
6. **Manzo standard errors.** The caption says "Standard Error is reported in brackets" and gives no basis; several exceed the estimate (for example DNABERT-2 HepG2 0.096 with 0.191). Kept as `standard_error`, as printed, with a limitation. They should not be used for intervals.
7. **Enformer and Borzoi on 1 kb input.** Worse than the collector recorded: the source contradicts itself. Table 2 says Enformer input was "truncated to 1 kb and padding as needed" and Borzoi was "applied directly on 1 kb input sequences". Section 4.2 paragraph 2 says that for Enformer (196 kb) and Borzoi (512 kb) "we retained their full input size", inserting the 1 kb sequence into genomic contexts and averaging. Which setup produced Table 1 cannot be told, so the values cannot be attributed to a defined configuration. **Excluded:** the eight Enformer and Borzoi evaluations, from the four Manzo judgements. HyenaDNA has a smaller conflict: Table 2 says inference-only, while Section 4.2 paragraph 4 lists it among fine-tuned models. It is kept with the conflict in its `parameters` and the limitations, because both readings give HyenaDNA its own input type.
8. **Geneformer on DNA tokens.** Geneformer is a single-cell transcriptome model with a gene-level vocabulary. Manzo et al. tokenised 1 kb DNA with that vocabulary ("tokens mapped sequence chunks to gene-like units"). The values (0.005 to 0.027, standard errors up to 0.198) describe an off-label use, and linking them to `catalog-model-geneformer` on a variant-effect page would misdescribe the model. **Excluded:** the four Geneformer evaluations, with reasons. The configuration keeps a `model_identity_note`.
9. **Tang 'LDLT'.** Recorded as printed. No gene has that symbol; the CAGI5 regulation challenge element is presumably LDLR, but the source does not say so. Record text now says this instead of asserting LDLR.
10. **Origins per row.**
    - Gschwind: all six rows `author_reported` (two corrected).
    - Manzo: TREDNet `author_reported` (reference 18 is from the senior author's group); the other 23 `independent_paper`. No Manzo author is an author of the other models.
    - Tang: the lentiMPRA probes, CNN and ResidualBind `author_reported`; MPRAnn corrected to `independent_paper`; the zero-shot language models, Sei and Enformer `independent_paper`. GPN (human) is a custom checkpoint the authors trained with the published architecture; I kept `independent_paper`, as for MPRAnn, and recorded the custom training on the configuration.

## Conflicts found

- Manzo Table 2 against Section 4.2, on Enformer, Borzoi and HyenaDNA adaptation (concern 7).
- Manzo prose against Table 1 (concern 5); Manzo SNP counts (concern 4).
- Gschwind EPIraction and EpiMap origins (correction 2).
- Manzo Table 3 describes Caduceus as Transformer-based and repeats the Geneformer applications text for GENA-LM; not used for descriptions.

## Judgements

| Judgement (`use-case-mapping-regulatory-variant-20261009-`) | Relevance | Reviewed | Excluded | Decision |
| --- | --- | --- | --- | --- |
| `gschwind2026-heldout` | proxy | 6 of 6 | | Holds; developer and threshold limitations |
| `gschwind2026-k562-training` | outside_scope | 0 | | Changed from proxy; not shown as evidence |
| `manzo2025-k562` | proxy | 21 of 24 | Enformer, Borzoi, Geneformer | Holds |
| `manzo2025-hepg2` | proxy | 21 of 24 | Enformer, Borzoi, Geneformer | Holds |
| `manzo2025-npc` | proxy | 21 of 24 | Enformer, Borzoi, Geneformer | Holds |
| `manzo2025-hela` | proxy | 21 of 24 | Enformer, Borzoi, Geneformer | Holds |
| `tang2025-cagi5-hepg2` | proxy | 14 of 14 | | Holds |
| `tang2025-cagi5-k562` | proxy | 14 of 14 | | Holds |

All reporter-assay judgements stay `proxy`: reporter activity on episomal constructs is not endogenous regulation, which is the use case's first exclusion. Groups, strata and headline metrics hold:
- `gschwind2026-heldout` is now a single stratum, because the training stratum no longer shows.
- `manzo2025-reporter-variants` has strata K562, HepG2, NPC and HeLa in table order.
- `tang2025-cagi5` has strata HepG2 and K562.
- Headlines are AUPRC and Pearson r.

Limitations, by source:
- **Gschwind:** developer comparison (all six rows from the authors or co-authors); whole-element perturbation; the direct-effect weighting; thresholds at 70% recall on K562; held-out composition, which is five cell types pooled, with remaining K562 pairs from other screens.
- **Manzo:** reporter activity; TREDNet authorship; unequal adaptation and the source conflicts; Geneformer off-label use; undefined standard errors; prose against table; per cell line, the dataset composition and count mismatch.
- **Tang:** reporter activity; one element in K562 and three averaged in HepG2 ('LDLT' as printed), with no uncertainty; which models are the authors' own; overlap between the CAGI5 elements and the lentiMPRA training sequences is not stated.

The judgement `review` follows the earlier reviews: method `source-hash-verification`, `independent-cell-check`, `ai-assisted-source-review`; reviewer `claude`; `reviewed_at` 2026-10-09T21:25:00Z. Pin the eight with `npm run use-cases:repin -- docs/reviews/use-cases/regulatory-variant-gene-follow-up-2026-10-09.md <claim-id>...` after `records -- add` and the link change.

## Approved use-case changes

Apply to `use-case-regulatory-variant-gene-follow-up`. These are links and gaps only; no pinned field changes, so the five existing judgements are not affected and need no re-pin.

1. Add `assessed_by` links to:
   - `regulatory-variant-20261009-protocol-gschwind2026-heldout-weighted`
   - `regulatory-variant-20261009-protocol-gschwind2026-k562-training-weighted` (the `outside_scope` judgement needs the link too)
   - `regulatory-variant-20261009-protocol-manzo2025-k562-pearson`, `-hepg2-pearson`, `-npc-pearson`, `-hela-pearson`
   - `regulatory-variant-20261009-protocol-tang2025-cagi5-hepg2`, `-cagi5-k562`
2. Append to `evidence_gaps`:
   - "No locus-to-gene comparison with printed per-method precision and recall was found. CALDERA (Schipper et al. 2026, PLoS Genet) prints only Brier scores for CALDERA, FLAMES, L2G and cS2G (Table 1); its AUPRC comparison is figure-only."
   - "No benchmark of variant-effect predictors against endogenous allele edits (base, prime or saturation editing of noncoding sites) with printed per-method values was found; the linked variant comparisons use reporter assays."
   - "The linked element-gene linking comparisons are by the developers of ENCODE-rE2G and ABC and their co-authors; the astrocyte CRISPRi benchmark (Green et al. 2026, Nat Neurosci), an independent test of ABC and ENCODE-rE2G, reports per-model values only in figures, prose and bootstrap source data."
   - "No linked comparison scores long-context sequence models (Enformer, Borzoi) on reporter allelic effects with a documented input setup; Manzo et al. 2025 describe it two ways, so those rows are excluded."
   - "Gschwind et al. Supplementary Tables 5 and 7 (eQTL and GWAS enrichment benchmarks) and the per-predictor K562 sheets of Table 3 are not extracted."
   - "Manzo et al. causal-SNP top-k results within LD blocks are figure-only."

No change to `decision`, `inputs`, `output`, `setting` or `exclusions` is approved. The existing text already separates allele-effect prediction, element-gene linking and shortlist selection. Because nothing pinned changes, I did not need to re-confirm the five existing judgements.

## Evidence summary

Replaces the collector's `summary_proposal`. That text did not name Manzo's Enformer and Borzoi setup conflict, counted EPIraction and EpiMap as independent, and quoted Enformer and Borzoi values that are now excluded.

> Three comparisons are linked beside the existing K562 CRISPRi and QTL evidence. All values are transcribed from the publications, not reproduced, and values from different sources must not be pooled. For element-gene linking, Gschwind et al. 2026, the developers of ENCODE-rE2G and ABC, scored six predictors, all from their own or co-authors' groups, on 4,378 CRISPR-tested element-gene pairs (190 positives) from five cell types, held out from training. Weighted AUPRC was 0.556 for ENCODE-rE2G (95% bootstrap interval 0.468 to 0.631), 0.465 for ABC (0.378 to 0.541), 0.383 for EPIraction, 0.363 for distance to the TSS, 0.268 for EpiMap and 0.211 for element-promoter DNase correlation. Weighted precision at each predictor's 70%-recall threshold was 0.544, 0.437, 0.347, 0.245, 0.292 and 0.112. These are whole-element perturbations; they do not test single alleles or establish a disease role. For allele effects, Manzo et al. 2025, whose group developed TREDNet, correlated predicted with reporter-measured variant effects. In K562 the Pearson correlation was 0.315 for TREDNet, 0.297 for Sei and 0.287 for ChromBPNet, against at most 0.199 for the DNA language models (Nucleotide Transformer v2 500M). In NPC no model exceeded 0.080, and in HeLa ChromBPNet reached 0.289 and Sei 0.280, while TREDNet reached 0.076. Enformer, Borzoi and Geneformer rows are not shown because the source describes their setup inconsistently or applied the model outside its input type. On CAGI5 saturation mutagenesis MPRA of four regulatory elements, Tang et al. 2025 found zero-shot DNA language models at most 0.135, published supervised models Sei at 0.545 (HepG2) and 0.641 (K562) and Enformer at 0.510 and 0.685, and the authors' own CNN on Sei embeddings at 0.579 and 0.701. Reporter assays measure activity on episomal constructs, not endogenous regulation, and none of these comparisons tests endogenous allele edits.

`source_ids`: `regulatory-variant-20261009-source-gschwind2026`, `regulatory-variant-20261009-source-gschwind2026-table-s3`, `regulatory-variant-20261009-source-manzo2025`, `regulatory-variant-20261009-source-tang2025`.

| Statement | Record (`regulatory-variant-20261009-`) | Printed |
| --- | --- | --- |
| 4,378 pairs, 190 positives, five cell types | `claim-gschwind2026-heldout-composition` | |
| EPIraction and EpiMap from co-authors' groups | `claim-gschwind2026-epiraction-developer`, `claim-gschwind2026-epimap-developer` | |
| ENCODE-rE2G AUPRC 0.556 (0.468 to 0.631) | `result-gschwind2026-heldout-encode-re2g-auprc` | 0.556151043664563 (0.467852411496632 to 0.631223913857611) |
| ABC 0.465 (0.378 to 0.541) | `result-gschwind2026-heldout-abc-dnase-avg-hic-auprc` | 0.465393786445695 (0.378228901913079 to 0.541415553632906) |
| EPIraction 0.383 | `result-gschwind2026-heldout-epiraction-auprc` | 0.382683898818773 |
| Distance to TSS 0.363 | `result-gschwind2026-heldout-distance-to-tss-auprc` | 0.363055349859503 |
| EpiMap 0.268 | `result-gschwind2026-heldout-epimap-auprc` | 0.268199731808225 |
| Element-promoter correlation 0.211 | `result-gschwind2026-heldout-ep-dnase-correlation-auprc` | 0.210746626296449 |
| Precision at threshold 0.544, 0.437, 0.347, 0.245, 0.292, 0.112 | `result-gschwind2026-heldout-{encode-re2g,abc-dnase-avg-hic,epiraction,distance-to-tss,epimap,ep-dnase-correlation}-precision` | 0.54424518399133; 0.43712922044365; 0.346611784087571; 0.244850836794557; 0.292474185581438; 0.112254845156556 |
| 70%-recall threshold | Methods; Supplementary Table 3 legend (recorded in protocol limitations) | |
| K562: TREDNet 0.315, Sei 0.297, ChromBPNet 0.287, NT v2 500M 0.199 | `result-manzo2025-k562-{trednet,sei,chrombpnet,nt-v2-500m-ms}-pearson` | 0.315; 0.297; 0.287; 0.199 |
| NPC at most 0.080 | `result-manzo2025-npc-chrombpnet-pearson` (maximum) | 0.080 |
| HeLa ChromBPNet 0.289, Sei 0.280, TREDNet 0.076 | `result-manzo2025-hela-{chrombpnet,sei,trednet}-pearson` | 0.289; 0.280; 0.076 |
| Zero-shot language models at most 0.135 | `result-tang2025-k562-self-supervised-pre-training-nt-2b5species-pearson` (maximum of 12) | 0.135 |
| Sei 0.545 and 0.641 | `result-tang2025-{hepg2,k562}-supervised-one-hot-sei-pearson` | 0.545; 0.641 |
| Enformer 0.510 and 0.685 | `result-tang2025-{hepg2,k562}-supervised-one-hot-enformer-dnase-pearson` | 0.510; 0.685 |
| CNN on Sei embeddings 0.579 and 0.701 | `result-tang2025-{hepg2,k562}-lentimpra-embedding-cnn-sei-pearson` | 0.579; 0.701 |

"At most 0.199 for the DNA language models" is the maximum of the 18 language-model rows in the K562 column, excluding Geneformer: DNABERT-2, NT, GENA-LM, HyenaDNA and Caduceus. The four-element count is from `data-tang2025-cagi5-saturation-mpra`.

## Checks run

`npm test` passed (46 files, 499 tests) and `npm run typecheck` passed, on the worktree with the reviewed batch. The batch is not yet in the store, so these tests do not read it; the scratch `addBatch` and `deriveUseCaseInputs` dry run is the check that covers it. `npm run build` and SHACL shapes were not run. The collector's ledger query contains an en dash because it is verbatim; it was left as is.

## Remaining gaps

- Figures were not checked, including Manzo's LD-block causal-SNP results and Gschwind's per-cell-type figures.
- Manzo Supplementary Tables S1 and S2 (dataset-level correlations) and Tang Additional file 1 were not retrieved.
- Gschwind Supplementary Table 1 (predictor aggregation and thresholds) was not read; the threshold rule comes from Methods and the legend.
- Collector's gaps unchanged: locus-to-gene comparisons with printed precision and recall, endogenous allele-editing benchmarks, the astrocyte and scE2G tables, and the Gschwind eQTL and GWAS benchmarks.
