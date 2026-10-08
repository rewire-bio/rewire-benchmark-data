# Regulatory variant and gene follow-up: bounded evidence research, 2026-10-08

Case 10 of 17 in the evidence programme ([rewire-benchmark-data #3](https://github.com/rewire-bio/rewire-benchmark-data/issues/3); benchmark programme [rewire-benchmarks #25](https://github.com/rewire-bio/rewire-benchmarks/issues/25), items B347 and BL347). Use case `use-case-regulatory-variant-gene-follow-up`, slug `regulatory-variant-gene-follow-up`. The article issue is [rewire.it #347](https://github.com/rewire-bio/rewire.it/issues/347) ("[Article plan] Choosing models for regulatory variant/gene follow-up"). It was resolved from repository evidence: `docs/omics/use-case-coverage-2026-09-30.md` links #347 to this use case, `docs/omics/amp-use-case-coverage-2026-10-07.md` repeats the link, and the issue body carries the marker `rewire-use-case-article-plan:regulatory-variant-gene-follow-up` and the use-case ID.

Starting commit: producer `main` 563d97ed353d88a98d6bed540dc3dee84a7b1e42 (merge of case 9). Worker: local Claude Code, model `claude-sonnet-5-5`, no skills and no subagents. Revised after independent Codex review of the primary XML and the pinned benchmark tables. No catalogue, mapping, definition, release, builder, test or generated file was changed, and no earlier dossier was touched. No model was run or trained. No neural-network checkpoint or sequence-model weights were downloaded. One incidental download did contain pre-fitted model files: the MPRabc code archive from Zenodo includes four `model.pkl` files, which were listed in the archive but never opened, loaded or executed. The archive and all other caches were kept. All times are UTC request starts from the ignored workbench `workbench/regulatory-followup-20261008/retrieval-log.tsv` and `search-log.tsv`.

## Disposition in brief

1. The existing MPRabc evidence stands. The article XML re-fetched at 09:34:13 has SHA-256 `7717b5605e01c9346bd04e9510f4d99dff8a05c7af0feb956a82184b4dd7ce46`, identical to the 30 September receipt and to Codex's independent fetch. All 10 recorded values (Table 3, and the Figure 2 paragraph for ABC 0.612 and megamap 0.690) match the text.
2. The "no cross-validation" gap in the original catalogue is unchanged. In this dossier it is read more narrowly: the sentence describes the benchmarking pipeline, and the MPRabc paper does not say how MPRabc itself was fitted or split. This is a reading in the new dossier only; no catalogue wording was changed. ENCODE-rE2G and scE2G state hold-one-chromosome-out scores on their K562 training set and add a separate held-out CRISPR set.
3. Counts and metric values from different papers, versions and populations are kept as source-specific rows (tables below). Only one count disagreement is inside a single source: the Nature paper gives 4,378 held-out pairs in its Figure 2d legend and 4,405 in its narrative.
4. A distance comparator is absent from the existing records. The Nature Supplementary Table 3 reports distance to TSS at AUPRC 0.436 and ENCODE-rE2G at 0.662 on the K562 set (positive prevalence 4.55 percent).
5. No source read here is an endogenous allele-edit benchmark, and none compares methods by confirmed hits per assay budget. This is bounded to the queries below, not a global absence claim.
6. Disposition: docs-only. This is final for this bounded research intake. A possible numeric extension (distance and ENCODE-rE2G rows from one supplement table) is recorded in the ignored plan as future work; it is not a required action and no approval is pending.
7. Focused-issue gap: after full open and closed dedup of four repositories no focused equivalent of B347 existed. Codex then posted the gap as [rewire-benchmarks #36](https://github.com/rewire-bio/rewire-benchmarks/issues/36). That issue is planning only. This worker posted nothing. Independent human scientific review remains outstanding.

## Existing inventory (unchanged)

In `data/omics/use-cases/inputs.json` this use case has five mappings: `use-case-mapping-20260930-347-81e84acc2274` (protocol `ucc-research-protocol-mprabc-k562`, six evaluations, relevance proxy, constraint "10,356 pairs, 471 positive, 9,885 negative; bootstrap intervals use 10,000 pair resamples") and four AMP proxy mappings for Feng et al. eQTL, sQTL, paQTL and ipaQTL causal-versus-noncausal discrimination. The use-case gaps are the three bullets in the 30 September audit (`data/omics/use-case-coverage-20260930/research/research.md`, section #347). Nothing below contradicts those records. The Feng primary text was not re-read; the AMP intake notes were used as given.

## Search log (exact, dated)

Nine web-search queries in three batches, six Europe PMC REST queries, two Crossref queries, one bioRxiv API call and one `gh issue list` per repository. Batch 1 started 09:34:38. Batches 2 and 3 were run in parallel and not individually timed; their windows are given. Full strings are in `search-log.tsv`.

| Time (UTC) | Tool | Query | Outcome |
|---|---|---|---|
| 09:34:38 | web, standard | ENCODE-rE2G Gschwind encyclopedia of enhancer-gene regulatory interactions CRISPRi benchmark chromosome cross-validation | preprint and PubMed record; chromosome hold-out confirmed later in primary text |
| 09:34:38 | web, standard | scE2G single-cell enhancer-gene regulatory maps ATAC multiome CRISPRi benchmark | preprint, then Nature Genetics record |
| 09:34:38 | web, extended | benchmark sequence-to-function models CRISPR-edited allele endogenous variant effect expression Borzoi AlphaGenome | AlphaGenome paper, RHD base-editing preprint, a genomics-x-AI post, a 2025 reporter-variant benchmark |
| 09:34:38 | web, extended | prospective variant-to-gene effector gene prediction CRISPRi validation GWAS loci enhancer-gene model performance versus distance 2026 | locus-specific CRISPRi studies (titles only, not read), ABC papers |
| 09:35:03 to 09:35:32 | web, standard | Gschwind Mualim Sheth Engreitz Nature 2026 "enhancer-gene" ENCODE-rE2G encyclopedia | Nature version; DOI found through Europe PMC |
| 09:35:03 to 09:35:32 | web, standard | Engreitz scE2G "Mapping enhancer-gene regulatory interactions from single-cell data" Nature Genetics 2026 | DOI 10.1038/s41588-026-02695-8 |
| 09:38:27 to 09:39:07 | web, extended | benchmark sequence-to-function models against endogenous base editing or prime editing noncoding variant expression effects prediction Enformer Borzoi AlphaGenome | no benchmark scoring models against edit-induced expression; pooled prime-editing preprints seen as titles only |
| 09:38:27 to 09:39:07 | web, standard | Benchmarking seq2func models on distal enhancer effects with CRISPRi screens genomicsxai | Karollus 2023; the post itself was fetched directly |
| 09:38:27 to 09:39:07 | web, extended | noncoding variant CRISPR editing in situ regulatory SNP allele-specific expression validation predicted by deep learning model prioritization hit rate versus MPRA | one case report, reviews; no hit-rate comparison |

Europe PMC REST: 09:34:59 `EXT_ID:38014075 AND SRC:MED`; 09:35:32 `DOI:"10.1038/s41588-026-02695-8"`; 09:35:32 `TITLE:"encyclopedia of human enhancer-gene regulatory interactions"`; 09:35:33 `DOI:"10.1038/s41586-025-10014-0"`; 09:39:49 the DOIs of Nasser 2021 and Fulco 2019; 09:41:26 two title queries for the MPRALegNet source paper (one returned 0 rows). Crossref: 09:35:14 returned HTTP 500 (cause not determined); 09:35:20 used a different query form and succeeded. bioRxiv API 09:35:15: version 1 only, `published` NA for 10.1101/2023.11.09.563812; the Nature version was found through Europe PMC.

Inclusion rule: a primary source (full text and supplement) that reports a labelled benchmark for allele effect, element-gene linking, variant-to-gene assignment, or an endogenous edit, with a stated population. Exclusions: reviews, titles seen only in search snippets, annotation resources that do not report a benchmark (the ENCODE cCRE registry named in the article issue was not read), clinical classification. Nothing here infers absence from catalogue silence or from the search.

## Findings

### 1. MPRabc: exact context of the no-cross-validation statement

Source: Nucleic Acids Research, DOI 10.1093/nar/gkag554, PMC13232518, PMID 42234579, published 2026-06-03; bioRxiv preprint 10.64898/2026.05.01.722242. The Methods section "Benchmarking" says, verbatim: "The benchmarking pipeline does not perform cross-validation. Instead, models are evaluated on predefined CRISPRi datasets provided by Gschwind et al." It continues with the population (10,356 perturbations, 471 positive, 9,885 negative), 10,000 pair bootstrap replicates, percentile 95% intervals, and "the threshold corresponding to 70% recall for binary predictions".

- The sentence is about the pipeline, which scores supplied predictions against a fixed table. It does not say MPRabc was fitted without a split.
- The paper says MPRabc was trained and benchmarked on K562 with the CRISPRi data from that line, and that candidate pairs lacking CRISPRi evidence "were treated as negatives" in training, while the benchmark has 9,885 tested negatives. Whether training negatives were the tested negatives or all candidate pairs within 5 Mb is not stated.
- No fold, chromosome or locus scheme is given for fitting MPRabc. The MPRabc fit and the baseline ENCODE-rE2G and ABC numbers it reports are separate things: the paper does not say how its baseline rows were produced beyond citing the benchmarking pipeline, so differences from other papers' baseline values are not attributed here.
- Code: `KreimerLab/MPRabc` commit `bf95d8f0fdff85e7364de31fa6d70a209b44a4b6` (MIT) and the Zenodo record 20162603 `MPRabc.zip` (SHA-256 `4418f321...1cd8`) hold feature-extraction utilities, feature tables, threshold files and pre-fitted `model.pkl` files, and no training or evaluation script and no README (the README URL returned 404). `Data.zip` (110 MB) and `MPRabc-analyses.zip` were not fetched.
- Feature overlap, not label overlap: MPRabc takes predictions from MPRALegNet and Sei. The MPRALegNet source paper (Agarwal et al., Nature 2025) trained on K562 lentiMPRA data with random 10-fold cross-validation over elements, not by chromosome, and itself intersected its elements with CRISPRi studies. How many CRISPRi-tested elements are in that training data, and which fold's weights scored which element, is not reported. Sei's training split was not inspected.

### 2. ENCODE-rE2G (Nature 2026) and its benchmark

Gschwind et al., Nature, DOI 10.1038/s41586-026-10781-4, published 2026-07-15, PMC13471189 (XML SHA-256 `df07ed8c...a3b642`, 278,941 bytes; Codex's independent fetch has the same hash), CC BY. The 2023 preprint (bioRxiv 10.1101/2023.11.09.563812, PMC10680627, CC BY-NC-ND) was read for comparison only.

- Pool: K562 element-gene pairs, 10,356 tested, 471 positive, 9,885 negative; negatives had no significant reduction despite good power for effects above 15 to 25 percent (Supplementary Note 1). The pinned table (`EngreitzLab/CRISPR_comparison` commit `50587422e6b11259ead6fbc6f867681c788f39b7`, training_K562 file SHA-256 `9eddfe18...9405`) has exactly 10,356 rows, 471 `Regulated=TRUE`, 9,885 `FALSE`, all K562, from three source datasets. Codex's independent copy matches. Positive prevalence is 4.55 percent, the no-skill reference for AUPRC, not a value every random ranking would realise exactly.
- Split: "hold-one-chromosome-out cross-validation" for supervised models; models applied elsewhere are trained on all chromosomes. The bootstrap resamples labelled pairs; clustering by element or locus is not described.
- Held-out set: eight screens in five cell types, pairs shared with training removed, weighted by the estimated probability of a direct effect. Count conflict inside this source: the Figure 2d legend states 4,378 pairs and 190 positives (157.39 weighted), the narrative states 4,405 tested pairs, and the pinned held-out file has 4,378 rows with 190 positive (SHA-256 `7783534a...2ffd0f`). The 4,405 figure is not reconciled by any text read.
- Distance comparator: Supplementary Table 3, sheet "Combined K562 data (training)", reports distance to TSS at AUPRC 0.436 (95% CI 0.387 to 0.482) against ENCODE-rE2G at 0.662 (0.616 to 0.706) in the same sheet. The text rounds these as 0.66 and 0.74 for the Extended model; the table gives 0.662 and 0.737, which agree after rounding.
- Other tasks, kept separate and not extracted numerically: fine-mapped GTEx eQTL variant-gene links, fine-mapped GWAS variant enrichment, and a blood-trait anchor-gene precision and recall test. These are variant-to-gene tasks, not element-level.
- The authors list limits: few positives, selection biases in the CRISPR tests, mostly K562, low power for small effects, and weaker performance for indirect effects, small effects, elements without H3K27ac and ubiquitously expressed genes.
- Access: paper CC BY; code `EngreitzLab/ENCODE_rE2G` (MIT, head `d039062b7092de338ed10a77ea208b3d5b06e89c`); benchmark tables in `EngreitzLab/CRISPR_comparison` (MIT repository; the licence scope for the third-party data inside the tables was not verified). Fitted logistic-regression coefficient files in the repositories were not inspected, and their reuse terms are not established beyond the repository licence.

### 3. scE2G (Nature Genetics 2026)

DOI 10.1038/s41588-026-02695-8, published 2026-08-03, PMC13447104, CC BY. Code `EngreitzLab/scE2G` (MIT, head `4f57df9f44c24566dceb0be084e7c34bcdd20548`). Read: full text, Tables S2 and S3 (`41588_2026_2695_MOESM3_ESM.xlsx`); the Supplementary Information PDF was fetched, not read line by line.

- Its own training population is 10,342 pairs, 466 positive, 9,876 negative (K562, aggregated from three studies); Figure 2b uses a subset within 1 Mb. This is a separate population from the Nature rE2G pool and is recorded as such, with no inference about why it differs.
- Hold-one-chromosome-out cross-validation scores are used for all benchmarking against the training data. Its held-out CRISPR set (4,175 pairs, 189 positive, five cell types, weighted by direct-effect probability) is a separate population from the Nature held-out set.
- Table S3 includes a distance-to-TSS row. The paper states that only scE2G and ABC-based models outperformed distance baselines. Its models need ATAC or paired RNA and ATAC data in the target cell type, which are different required inputs from bulk DNase; no comparative cost was measured here.

### 4. ABC (methods and results as primary evidence)

- Fulco et al., Nature Genetics 2019 (DOI 10.1038/s41588-019-0538-0, PMC6886585, read) built the K562 CRISPRi-FlowFISH benchmark: positives were decreases, negatives were tested pairs with power for 25 percent effects, and ABC was compared with distance-only and closest-expressed-gene rules. Distance thresholds had low precision for regulatory elements even when recall was high.
- Nasser et al., Nature 2021 (DOI 10.1038/s41586-021-03446-x, PMC9153265; Europe PMC XML returned HTTP 500 at 09:39:53, so the PMC HTML and the bioRxiv PDF were read) applied ABC in 131 biosamples and compared ABC-Max with closest-gene assignment at fine-mapped credible sets. At locus level, closest gene was a strong baseline with higher coverage than ABC-Max on the curated set, and ABC-Max was more precise on the loci it called. Precision on a subset and recall on all loci are different budgets and cannot be compared without matching.
- Implementation identity: the current `broadinstitute/ABC-Enhancer-Gene-Prediction` repository (MIT, head `92ac50360231a6bcfd654f3147839d078be445d9`) is not the 2019 or 2021 code. Comparisons must name the version and configuration. No ABC configuration is inferred for MPRabc from numerical closeness.

### 5. AlphaGenome and other sequence predictors

Avsec et al., Nature, DOI 10.1038/s41586-025-10014-0, published 2026-01-28, PMC12851941, CC BY. The Supplementary Information PDF and Supplementary Table 4 were fetched; their numerical rows are not extracted here.

- Allele-effect outputs are reported on fine-mapped GTEx eQTL (sign, effect size and causality discrimination) against Borzoi and Enformer. These are population-variant tasks, not endogenous edits.
- Linking: the paper evaluates AlphaGenome on the ENCODE-rE2G CRISPRi pool (471 positives, 10,356 pairs; 3 dropped for gene IDs in the supplement, 10,353 scored) using K562 RNA-seq input gradients or a permutation of a 2 kb element. These are whole-element scores, not allele effects. The text says zero-shot performance was within 1 percent AUPRC of ENCODE-rE2G Extended and that both Borzoi and AlphaGenome underestimate very distal enhancers.
- Split distinction: track-level evaluations use fold-specific models on held-out genome intervals with a rule removing test windows whose 1 Mb input overlaps training windows. Variant and linking evaluations use all-fold models trained on all eight genome sections ("exclusively evaluated on variant interpretation benchmarks"). Without a locus-level overlap audit, no claim is made either way about whether a specific tested locus was seen in training.
- Access (separate): paper CC BY; code `google-deepmind/alphagenome_research` Apache-2.0 (head `8112c2b95352471f7cde9635b14a9f26cf47c5d0`); weights via Kaggle or Hugging Face after accepting non-commercial model terms; the hosted API is described as non-commercial. Only the README summary of the terms was reviewed; the full model-terms page was not.
- Other sequence-model evaluations read qualitatively: Karollus et al., Genome Biology 2023 (PMC10045630) reports that Enformer discounts distal enhancer effects roughly in proportion to inverse distance. A June 2026 genomics-x-AI post (not peer reviewed; licence not found) repeats the in-silico knockdown comparison for newer models and states that predicted effects are compressed relative to CRISPRi and that both screens are K562. A 2025 Genes paper (PMC12562713) compares models on reporter-assay and eQTL-derived variant sets; it is reporter-based and its split construction was not extracted. None of these supplies an endogenous allele-edit endpoint, and their numerical values are not recorded here.

### 6. Endogenous allele editing

The only endogenous edit study found and read is a bioRxiv preprint on non-coding variants affecting RHD expression (10.64898/2026.01.21.700828, PMC12889522, CC BY): AlphaGenome was used to nominate sites, then base editing in K562 was done at two sites, with qPCR and flow cytometry readouts and bystander edits near the higher-scored site. It is a single-locus case report with no distance, linking or random comparator and no hit-rate denominator, so it is not a benchmark. Pooled prime-editing screens appeared only as titles in search snippets and were not read.

## Endpoint separation

| Question | Assay and label | Metric in sources | Comparators present | Held-out structure |
|---|---|---|---|---|
| Allele effect, reporter | MPRA or SuRE reporter QTL | accuracy or correlation | sequence models | unextracted |
| Allele effect, population | GTEx fine-mapped eQTL | sign, effect size, causality | Borzoi, Enformer | all-fold AlphaGenome models; overlap not audited |
| Allele effect, endogenous edit | base or prime edit | none benchmarked | none | not applicable |
| Whole-element linking | CRISPRi, K562; rE2G, MPRabc and AlphaGenome use the 10,356-pair pool (471 positive; AlphaGenome scored 10,353); scE2G uses its own 10,342-pair pool (466 positive) and distance-limited subsets | AUPRC, precision at 70% recall | distance, ABC, rE2G, scE2G, sequence models | chromosome CV and separate held-out set (rE2G, scE2G); MPRabc fit split unreported |
| Effect magnitude | CRISPRi, K562 | correlation among positives | in-silico knockdown by sequence models | none; zero-shot |
| Credible-set variant-to-gene | known anchor genes at GWAS loci | precision, recall | closest gene, ABC-Max, rE2G | curated anchors |
| Shortlist hit yield per budget | confirmed hits per assay | none found | none found | none |

AUPRC base rates differ by dataset, so AUPRC values from different pools are not comparable. Precision at 70 percent recall uses a threshold fixed on the same labelled benchmark, even with cross-validated scores, so it is not a prospective operating point. Negatives in all sources read are tested pairs with a power rule; untested pairs are not labelled negative in those benchmarks, though the MPRabc training sentence leaves its own training negatives ambiguous.

## Source-specific values and populations

These are different papers, model versions, inputs and populations. They are not treated as contradictions of one experiment unless the same input and configuration are shown, which no source does.

| Item | Value and source | Comparison limit |
|---|---|---|
| K562 pool, pairs / positives / negatives | 10,411 / 472 / 9,938 (2023 preprint); 10,356 / 471 / 9,885 (Nature, MPRabc, pinned file); 10,342 / 466 / 9,876 (scE2G, own training aggregation) | Different data aggregations; no ordering or cause is inferred |
| AlphaGenome scored pairs | 10,353 of 10,356 (3 dropped for gene IDs, supplement) | Same pool, three pairs fewer |
| Held-out pairs, Nature | 4,378 (Figure 2d legend, pinned file); 4,405 (narrative) | Disagreement within one source, unresolved |
| Held-out pairs, scE2G | 4,175 with 189 positives | Separate population |
| ENCODE-rE2G K562 AUPRC | about 0.63 (preprint), 0.634 (MPRabc Table 3), 0.648 (scE2G Table S3), 0.662 (Nature Supplementary Table 3; 0.66 in text) | Different model versions, inputs and populations; MPRabc's and scE2G's baseline settings are not shown to equal the Nature model |
| Distance to TSS AUPRC | 0.436 (Nature Supplementary Table 3); scE2G Table S3 has its own row on its population | Reported per source |

## Access and reuse (paper, code, data, fitted models, weights)

| Source | Paper | Code | Data | Pre-fitted models and weights |
|---|---|---|---|---|
| MPRabc | CC BY (NAR) | MIT (GitHub, Zenodo) | Zenodo record metadata MIT; scope over third-party data inside not verified | pre-fitted `model.pkl` files in the repo and archive, MIT as part of the repo, never opened; MPRALegNet and Sei weights are third-party, terms not reviewed |
| ENCODE-rE2G | CC BY (Nature); preprint CC BY-NC-ND | MIT | `CRISPR_comparison` repository MIT; scope over embedded third-party tables not verified; supplement CC BY | fitted coefficients not inspected; terms beyond repository licence not established |
| scE2G | CC BY | MIT | supplement CC BY | not inspected |
| ABC | Fulco open access; Nasser author manuscript | MIT | supplement tables, terms not reviewed | none inspected |
| AlphaGenome | CC BY | Apache-2.0 | evaluation data referenced by the repository, not reviewed | neural weights under non-commercial terms (README summary only); not downloaded |
| genomics-x-AI post | licence not found | linked repository not inspected | Karollus Zenodo tables not fetched | public checkpoints not fetched |

## What the sources can and cannot support

- They support: a comparison of whole-element linking methods on a shared K562 CRISPRi pool with distance as a baseline; the existence of held-out CRISPR sets for rE2G and scE2G; allele-effect proxies from eQTL and reporter data.
- They do not support: a claim that a method selects more confirmed allele edits than distance or ABC at the same budget; transfer of K562 results to a disease tissue; use of reporter activity or whole-element CRISPRi as an allele-effect label; disease causality for any gene. No clinical or diagnostic claim follows.

## Unresolved or unretrieved

- How MPRabc was split and which MPRALegNet fold weights scored which elements.
- Sei's training split and the count of CRISPRi-tested elements in MPRALegNet or Sei training data.
- The 4,405 versus 4,378 held-out count in the Nature paper.
- Supplementary Methods and Notes PDFs for rE2G and scE2G were fetched, not read line by line.
- The ENCODE cCRE registry paper and locus-specific CRISPRi studies seen only in search results.
- Feng et al. primary text (existing AMP records).
- Full AlphaGenome model terms.

## Bounded access failures

- 09:35:14 Crossref with field selection returned HTTP 500 (cause not determined); a different query form at 09:35:20 worked.
- 09:36:03 MPRabc README at the pinned commit: HTTP 404 (no README in the tree).
- About 09:37:00 Europe PMC `supplementaryFiles` timed out after 30 seconds for three articles; replaced by the publisher's static supplement URLs, which worked.
- 09:39:53 Europe PMC full-text XML for PMC9153265 returned HTTP 500; the PMC HTML and the bioRxiv PDF were used instead.

## Cached bytes (ignored workbench `workbench/regulatory-followup-20261008/cache/`)

About 48 MB, with per-file times, sizes and SHA-256 in `retrieval-log.tsv`: Europe PMC XML for the papers listed above, the PMC HTML for PMC9153265, supplements for scE2G, AlphaGenome and ENCODE-rE2G, the two pinned CRISPR benchmark tables, the MPRabc code archive (kept, includes unopened `model.pkl` files), the genomics-x-AI post, GitHub and Zenodo metadata, and issue exports for four repositories. Downloaded files were read as data only and nothing from them was executed or loaded.

## Issue deduplication

At 09:40:14 UTC `gh issue list --state all --limit 1000` returned titles and bodies for rewire-benchmarks (17 issues), rewire-benchmark-data (11), rewire-database (23) and rewire.it (304). A keyword scan (regulatory, enhancer, variant, ABC, rE2G, scE2G, MPRA, CRISPRi, AlphaGenome, effector, GWAS, B347, BL347) plus a read of every body that matched found:
- rewire-benchmarks #25 (programme, open) lists B347 and BL347 as checklist items. It is not a focused ticket.
- Focused tickets #26 to #35 cover B343, B349, B345, B334, B335, B348, B336, B337, B341 and an AMP umbrella. None addresses regulatory variants or linking; #34 and #35 matched only on the word "variant".
- rewire-benchmark-data #3 lists "Regulatory variant/gene follow-up" as unchecked; #19 (Feng audit) covers the QTL proxy mappings only.
- rewire.it #347 is the article plan (open); #365 and #351 list it; closed articles #77, #235, #239 and #286 are background articles, not duplicates.

Conclusion: no focused equivalent existed within these searches. Codex posted the B347 gap as [rewire-benchmarks #36](https://github.com/rewire-bio/rewire-benchmarks/issues/36), linked to #25, #3 and #347. The ignored plan holds this worker's pre-posting draft. This worker posted nothing.

## Paths

- Tracked: `docs/omics/evidence-research/regulatory-variant-gene-follow-up-2026-10-08.md`.
- Ignored: `workbench/regulatory-followup-20261008/intake-plan.md`, `retrieval-log.tsv`, `search-log.tsv`, `sources.json`, `cache/`, extracted text files and issue exports.

## Review status

Automated source review by a local Sonnet worker (`claude-sonnet-5-5`), then independent review by Codex on 2026-10-08. Codex independently fetched the primary XML for MPRabc, the Nature rE2G paper (PMC13471189, SHA-256 `df07ed8c37a62732ba0ae26b74a6c8bcb9b48540fefd03c064115d9a87a3b642`), scE2G and AlphaGenome, matched the pinned benchmark tables (training 10,356 rows with 471 positive; held-out 4,378 rows with 190 positive), and verified the Nature supplement ZIP (SHA-256 `88eb6c5239019cbec55281b545a3b6e450e2a83384d067ca94a0974968428332`) and the two Supplementary Table 3 rows used above (distance to TSS AUPRC 0.43593 with CI 0.38734 to 0.48235; ENCODE-rE2G 0.66224 with CI 0.61562 to 0.70591).

Main scientific qualifications:
- The MPRabc fit and split are unreported; the reading in section 1 is a narrower interpretation in this dossier only. Original catalogue definitions, history and releases are unchanged.
- Counts and AUPRC values come from different papers, versions and populations and are not pooled. The 4,378 versus 4,405 held-out count inside the Nature paper is unresolved.
- Whole-element perturbation, reporter activity and population-variant data are not allele-edit evidence, and no source reads a confirmed-hits-per-budget comparison.
- No benchmark or model was executed. Independent human scientific review remains outstanding.

Disposition is docs-only and final for this intake; no catalogue change is warranted in this pass. The follow-on issue #36 is planning only. The case awaits CI and merge.
