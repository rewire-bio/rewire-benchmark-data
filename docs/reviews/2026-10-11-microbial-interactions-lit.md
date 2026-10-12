# Review: microbial and interactions literature batches, 2026-10-11

Independent review of the five batches from the `lit-microbial-interactions` literature pass (window
2025-10-01 to 2026-10-11). Reviewers: Claude review agents `reviewer-mi-1` (virobench, mochibind) and
`reviewer-mi-2` (leakctl, ppiemb, plmdta). Neither extracted the batches it reviewed. No human review is
claimed. Source transcription is not reproduction.

Each batch folder holds the reviewer's report and the corrections applied (`review.md`) and the receipt
(`review.json`, binding the SHA-256 of every file in the folder). The corrections were applied by the
extractor in the extraction scripts, as the reviewers specified, before the batches were added to the store.

## Outcome

Every batch passed with corrections. No printed or numeric value was wrong in any batch: all 1,579 results
match their sources. Every correction is metadata, namely adaptation and training descriptions, origin,
populations, aggregations, splits, versions, units and limitations, plus five source-level evidence concerns.

| Batch | Source | Artifact SHA-256 | Reviewer | Values | Records |
| --- | --- | --- | --- | --- | --- |
| `lit-microbial-20261011-virobench` | ViroBench: Benchmarking Nucleotide Foundation Models on Viral Genomics Tasks | `22ad7d74…1f9e42` | reviewer-mi-1 | 912 results | 1,932 records |
| `lit-interactions-20261011-leakctl` | Leakage-controlled benchmarking reveals generalization limits of deep learning for protein-ligand binding affinity prediction (PLABench) | `5fba9691…397281` | reviewer-mi-2 | 279 results | 363 records |
| `lit-interactions-20261011-ppiemb` | The role of protein embeddings for protein-protein interaction prediction with graph neural networks | `360d4f17…d4866c` | reviewer-mi-2 | 308 results | 715 records |
| `lit-interactions-20261011-plmdta` | Comprehensive Evaluation of Protein Language Model Embeddings for Drug-Target Affinity Prediction | `11b88d5a…259163` | reviewer-mi-2 | 64 results | 131 records |
| `lit-interactions-20261011-mochibind` | A systematic evaluation framework for universal antibody-antigen binding affinity prediction and candidate recommendation | `0f57b9b1…44368d` | reviewer-mi-1 | 16 results | 49 records |

Total: 1,579 results, 3,190 records.

## Main corrections

- **virobench.** Two source-level evidence concerns. First, the taxonomy columns of Table 25 equal the
  rounded mean of the five per-rank values in Table 26 for 143 of 144 ALL-virus cells, the exception being
  RNA-FM under the genus-disjoint split, where the two tables disagree (48.67 against 53.10); that row must
  not be used in a comparison without checking the published code. Second, Table 3 and Table 9 disagree on
  whether NT v3 has phage-specific or non-viral pretraining coverage, which matters because coverage is the
  paper's main explanatory variable. The six taxonomy protocols now state what is and is not known about the
  rank aggregation, and the six host protocols carry the source's own single-label caveat.
- **leakctl.** The three sequence-based models were retrained on the PDBbind v2020 refined set before CASP16
  and ChEMBL35, which the records had described as "applied without retraining". MFE's training conflicts
  within the source, so its adaptation is now null with reason `conflicting`. The CASP16 and ChEMBL35
  populations (17 ligands, 123 ligands, 4,862 pairs across 71 targets) and the cold-split aggregation are
  stated in the source and are now recorded. `unit_detail` now covers ChEMBL35 and says "squared error" for
  MSE.
- **ppiemb.** The footnote of Tables 5 and 6 gives a table-wide maximum standard deviation, so repeated runs
  exist although no per-cell spread is printed; the protocols, the source and all 308 results now say that.
  The HuRI split was invented by the extractor and is now `unreported`, and the HuRI dataset version was a
  copy error. The majority-vote ensemble is the study authors' own construction, so its 28 evaluations are
  `author_reported`. The evidence concern now also records that the random-feature baselines look far below
  the OGB leaderboard the authors say they reproduced.
- **plmdta.** The Davis data are the Monteiro et al. 2022 corrected version and Appendix A says every model
  was trained on it, so the eight Davis baseline evaluations are `independent_paper` with a stated
  adaptation. The three KIBA baseline rows equal the values printed in Ozturk et al. 2018, which the reviewer
  verified against that paper's own table; they keep origin `unreported` and the source carries an evidence
  concern against comparing them with the proposed models.
- **mochibind.** The test-set denominator is stated twice in the source (200,000 sampled pairs per held-out
  antigen, no affinity-difference threshold), so population and aggregation are now recorded rather than
  marked unreported. The Table 2 footnote contradicts the headers, the cells and the body text, which is now
  an evidence concern.

## Use-case judgements

None. Both reviewers enumerated the 26 use cases in `data/entities/use-cases.jsonl` and agreed that no
extracted protocol bears directly on one, so no `assessed_by` link, judgement claim or summary was written.
`reviewer-mi-1` records that ViroBench's genus-disjoint host and taxonomy protocols are the closest
candidate for `use-case-diagnostic-dna-pathogen-identification` but fail the endpoint test, because the
inputs are curated near-complete viral genomes rather than clinical sequencing data, there is no
contamination or background model, and the output is a coarse host or taxon label rather than a clinical
detection; that would make it at best a `proxy` with heavy limitations, and the owner should decide before
anyone writes it. `reviewer-mi-2` records that the store has no ligand-prioritisation use case at all, which
is a gap for the owner.

## One deviation from the reviewers' text

Both reviewers wrote the evidence concerns with a `date` field. The store's existing concerns use
`reviewed_at` with a `review_method`, which `docs/collection.md` requires, so the five concerns carry
`reviewed_at: 2026-10-11T00:00:00Z` and `review_method: ai-assisted-source-review`. Every message, locator
and artifact hash is verbatim.

## What the reviewers did not check

- virobench: the generation tables (5, 6, 27, 28), the recall, precision and AUPRC tables (22, 23, 24), all
  figures, and the KDD conference version of the paper.
- mochibind: Supplementary Document S1 (the McNemar chi-squared values and the Graphinity before and after
  fine-tuning accuracies), so the footnote conflict is diagnosed from the main text alone.
- ppiemb: Supplementary Tables S1 to S7, including the OGB leaderboard values the concern refers to.
- leakctl and plmdta: the Zenodo deposits, the supplementary notes and all figures.
- No reviewer reran a model or reproduced any result.

## Reviewer reports, verbatim

The two reports follow unchanged, as the review evidence for these batches.

---

# Independent review: ViroBench and MochiBind batches

Reviewer: Claude research agent (reviewer-mi-1); no human review claimed. Date 2026-10-11.
I did not extract either batch. Working copy reviewed: the uncommitted batches in
`/Users/timrichardson/Documents/projects/personal/blog/rewire-benchmark-data-lit-microbial-interactions`.
Nothing was edited.

## Verdicts

- `data/omics/lit-microbial-20261011-virobench` (912 results): **approved with corrections**. Every
  printed value is right; the corrections are two source-level evidence concerns and one protocol
  limitation wording.
- `data/omics/lit-interactions-20261011-mochibind` (16 results): **approved with corrections**. Every
  printed value is right; the test-set denominator is stated in the source and must stop being
  recorded as unreported, and the Table 2 footnote conflict needs an evidence concern.

## Corrections to apply (mechanical)

### ViroBench

V1. Add an `attributes.evidence_concerns` entry to `lit-microbial-20261011-virobench-source-ye2026`:

```
source_id: lit-microbial-20261011-virobench-source-ye2026
message: Table 25 prints one Macro-F1 per model for the taxonomy columns. For 143 of the 144
  model-by-split taxonomy cells on the ALL-virus set, the printed value equals the mean of the five
  per-rank values in Table 26 rounded to two decimals. The exception is RNA-FM under the
  genus-disjoint split: Table 25 prints 48.67 and the mean of the Table 26 ranks (59.96, 65.35,
  37.58, 58.78, 43.82) is 53.10. One of the two tables is wrong for that row, so RNA-FM ALL taxonomy
  G-Split should not be used in a comparison without checking the published code.
source_locator: Table 25, row 'RNA-FM', column 'ALL viruses / Taxonomy / G-Split'; Table 26, row 'RNA-FM'
artifact_sha256: 22ad7d742eeba37dd7f7f407a483776ba15fc38dedfb8c27ec05f5db231f9e42
date: 2026-10-11
```

V2. Add a second `attributes.evidence_concerns` entry to the same source record for the NT v3
coverage conflict, and leave the existing limitations line in place:

```
message: Table 3 lists NT v3 under phage-specific pretraining coverage (P) and Table 9 lists it as
  non-viral (N). Table 25 groups the NTv3 rows under phage-specific coverage, which is what the
  configurations record. Pretraining coverage is the paper's main explanatory variable, so NT v3
  rows should not be used to support a coverage-versus-performance claim.
source_locator: Table 3 row 'NT v3'; Table 9 row 'NT v3'; Table 25 section 'DNA Foundation Models (Phage-specific Coverage)'
artifact_sha256: 22ad7d742eeba37dd7f7f407a483776ba15fc38dedfb8c27ec05f5db231f9e42
date: 2026-10-11
```

V3. In the six taxonomy protocols (`...-protocol-all-taxonomy-g-split`,
`...-protocol-all-taxonomy-t-split`, `...-protocol-dna-taxonomy-g-split`,
`...-protocol-dna-taxonomy-t-split`, `...-protocol-rna-taxonomy-g-split`,
`...-protocol-rna-taxonomy-t-split`), replace the limitation
line that begins "The taxonomy column is a single Macro-F1 per model" with:

```
The taxonomy column is a single Macro-F1 per model; the source predicts five ranks (Kingdom to
Family) through five parallel heads (Appendix B.3) and never states how the ranks are combined. On
the ALL-virus set the printed value equals the rounded mean of the five Table 26 per-rank values for
143 of 144 cells, the exception being RNA-FM under the genus-disjoint split. The mean is an
observation about the printed numbers, not a stated aggregation, and no value was computed from it.
```

For the DNA and RNA taxonomy protocols, keep the same text but say that the per-rank table (Table
26) covers the ALL-virus set only, so the aggregation cannot be checked for those two virus sets.

V4 (optional, recommended). Add to the six host protocols' limitations the source's own caveat:
"Host classification assigns each virus to exactly one coarse-grained host category; the source says
many viruses have multi-host tropism and that single-label framing can penalise biologically
reasonable secondary host associations (Appendix limitations discussion, text-layer lines 2185 to
2199)."

### MochiBind

M1. On all 16 evaluation records (`lit-interactions-20261011-mochibind-eval-*`), set

```
comparison.population: "200,000 sampled antibody pairs from the held-out antigen, no affinity-difference threshold applied"
```

and delete the `missing_metadata["comparison.population"]` entry. The source states it twice: STAR
Methods, "Cross-antigen evaluation setup" ("one for validation (200,000 pairs) and one for testing
(200,000 pairs without threshold)"), and Results, "Pairwise accuracy" ("based on the 200,000 pairs
from the test set"). Add `source_locator` support by appending to the existing locator string:
"; STAR Methods, 'Cross-antigen evaluation setup'".

M2. On the same 16 evaluations, set

```
comparison.aggregation: "Fraction of the 200,000 sampled test pairs in which the stronger binder was identified"
```

and delete the `missing_metadata["comparison.aggregation"]` entry. This follows from the metric
definition plus the stated pair count and is not an inference about an unstated choice.

M3. Add an `attributes.evidence_concerns` entry to
`lit-interactions-20261011-mochibind-source-isci2026`:

```
message: The Table 2 footnote says "Values denote chi-squared statistics, with significance levels in
  parentheses", which contradicts the column headers ("Pairwise accuracy (%)", "Graphinity (%)" and
  so on), the cell contents (percentages between 47.11 and 74.27) and the body text, which places the
  chi-squared statistics in Table S1. The records read the cells as accuracies with a p-value, which
  the headers and body support; the footnote is wrong as printed.
source_locator: Table 2 footnote
artifact_sha256: 0f57b9b13bae7460d3789fdcd7f3aaa062ec8cfe8e8d1ef9242d480ea444368d
date: 2026-10-11
```

M4 (optional). The four protocol limitation lists say "The authors developed MochiBind and ran all
baselines". Add that the Graphinity column is the authors' own fine-tune of a third-party model,
trained on the same rotation, while Boltz-2 and GeoDock are used without any fitting, so the four
columns are not matched on adaptation.

## Answers to the report's questions, for my two batches

**2. ViroBench taxonomy aggregation.** The protocols should say more, as set out in V3. I compared
every ALL-virus taxonomy cell in Table 25 against the mean of the five per-rank values in Table 26
with my own parser: 143 of 144 agree exactly after rounding half up to two decimals, so the printed
taxonomy score is almost certainly the unweighted mean over Kingdom, Phylum, Class, Order and Family.
The single exception, RNA-FM G-Split, is a real inconsistency inside the source and needs the
evidence concern in V1. The aggregation is still not stated by the authors, so the records should
keep it as an observation rather than asserting it.

**3. ViroBench standard deviations.** The reading is right. Section 4.1.2 says "We tune learning
rates (10-2 to 10-4) and evaluate performance across these distinct window configurations. Results
are reported as the mean (standard deviation) across these hyperparameter settings." Appendix E.2
gives the window settings as (W, N, K) in {(512, 8, 64), (1024, 4, 32), (2048, 2, 16)}. Nothing in
the paper reports repeated seeds. The scope text "across hyperparameter settings (window
configurations and learning rates)" is accurate and should stay.

**6. MochiBind pair counts.** A pair count is needed, and the source supplies it: 200,000 test pairs
per held-out antigen, sampled without the 10 percent affinity-difference threshold used for training.
Apply M1 and M2; after that the results support comparison. The one thing still unstated is the
random seed or the stratification used for the test sample, which does not need recording.

**8. NT v3 pretraining coverage.** Recording phage-specific is the right call, because Table 25 is
the table the values come from and it groups the NTv3 rows under phage-specific coverage. The
conflict with Table 9 is not just a metadata footnote: coverage is the variable the paper's headline
conclusion rests on, so it belongs in `evidence_concerns` (V2), not only in the source limitations.

**9. Use-case relevance judgements.** I agree that neither batch should carry a judgement as it
stands. The closest real candidate is ViroBench's host and taxonomy G-Split protocols against
`use-case-diagnostic-dna-pathogen-identification`: a genus-disjoint split is a direct test of
behaviour on organisms absent from the reference, which is part of that use case's question, and
BLAST and Kraken2 are evaluated on the same protocol. It still fails the endpoint test, because the
inputs are curated near-complete viral genomes rather than clinical sequencing data, there is no
contamination or background model, and the output is a coarse host or taxon label rather than a
clinical detection. That makes it at best a `proxy` with heavy limitations, and the owner should
decide before anyone writes it. MochiBind against `use-case-structural-hypotheses-experiments` does
not fit: the endpoint is ranking antibody variants by affinity, not whether a predicted interface is
reliable enough to act on.

## Checks run and outcomes

Sources.

- ViroBench. Re-downloaded `https://arxiv.org/pdf/2605.25388v1`; SHA-256
  `22ad7d742eeba37dd7f7f407a483776ba15fc38dedfb8c27ec05f5db231f9e42`, matching the source record.
  42 pages per `pdfinfo`. Re-ran `pdftotext -layout` with poppler 26.08.0 and got the text layer
  hash `48071e2e329430de04b90c16d92261af52fe953cfc424e8caa5acf2babc574c7`, matching the record and
  the archived gzip in `artifacts/` (gzip hash `a3ee0e52...`, contents hash equal to the text layer).
  So the archived artifact, the record and a fresh retrieval all agree.
- MochiBind. Re-downloaded the Europe PMC full-text XML for PMC13444443; 134,124 bytes, SHA-256
  `0f57b9b13bae7460d3789fdcd7f3aaa062ec8cfe8e8d1ef9242d480ea444368d`, matching the record. The XML
  is correctly not archived under CC BY-NC-ND.

Full automated comparison, written by me, not reusing the collector's scripts.

- ViroBench: my own parser read every row of Table 25 (74 rows, 12 cells each) and Table 4 (34 rows)
  from the pinned text layer and matched each of the 912 results by its `source_locator`. All 912
  printed values, numeric values and standard deviations match; the text-layer line number in each
  locator is correct; there are no duplicate cells and no cell of Table 25 is missing (74 x 12 = 888
  cells, all extracted, plus the 24 cells of the two Table 4 rows Table 25 omits, giving 912).
- Table 4 against Table 25: for every model row present in both, all twelve cells agree, so the
  claim in the retrieval log holds. Only ViroDNABERT2 and ViroCaduceus are unique to Table 4, and
  they are the only Table 4 rows extracted. Their values also agree cell for cell with Table 19.
- MochiBind: parsed all `<table-wrap>` elements of the pinned XML. Table 2 has 4 rows x 4 model
  columns = 16 cells, and all 16 are extracted with the printed string, the numeric accuracy and, for
  MochiBind, the p-value, all matching. Table 1 is a tick-and-cross feature matrix of prior studies,
  correctly not extracted; the key resources table holds no performance values. No other table in the
  XML carries results.

Hand checks against the rendered pages.

- ViroBench: rendered pages 6, 37 and 38 at 150 dpi and read 79 cells by eye, covering both pages of
  Table 25 and both Table 4 rows, all four baselines, all four coverage groups, both tasks, both
  splits, all three virus sets and models from 1M to 40B parameters. 77 matched on the first read.
  The two apparent differences, LucaVirus-gene-step3.8M DNA taxonomy T-Split and RiNALMo DNA host
  T-Split, were my misreading of the small-print standard deviations at 150 dpi; re-rendered at 400
  dpi both read 60.45 (3.93) and 37.68 (5.29), matching the records. Net: 79 of 79 confirmed.
- MochiBind: 16 of 16 cells read directly from the pinned XML table markup, including the header row,
  the footnote and the p-value strings. The batch has only 16 results, so this is the whole batch
  rather than a sample.

Metadata.

- Metric, direction, unit and qualifier. ViroBench: `macro-f1`, higher is better, percent with
  `unit_detail` "Macro-F1 x100 as printed". Tables 4 and 25 print no unit; Tables 17 to 20 state
  "Macro-F1 scores with standard deviation in parentheses (%)", so percent is justified. MochiBind:
  `accuracy`, higher is better, percent, which the column headers print. Both concepts already exist
  in `data/vocab/metric.ttl`; neither batch adds a concept (the three new concepts in the working
  tree's `metric.ttl` diff belong to the other three batches).
- Uncertainty. ViroBench records the parenthesised value as a standard deviation with the
  hyperparameter scope, which Section 4.1.2 supports. MochiBind records no uncertainty, correctly:
  the parenthesised text is a McNemar p-value and is held separately in `reported_p_value`.
- Denominators. ViroBench prints no test-set counts per split beyond Table 1's label counts, and
  `comparison.population` is null with reason unreported, which is right. MochiBind states its
  denominator, hence correction M1.
- Dataset and split mapping. The six ViroBench dataset records match Table 1 panels A, B and C,
  including the 8:1:1 ratio and the temporal cutoffs (ALL 2017.10/2020.02, DNA 2022.07/2023.08, RNA
  2017.03/2017.11). Every result is linked to the dataset matching the virus set and split in its
  locator. The four MochiBind dataset records match the STAR Methods sampling: 10,000 variants for
  PEM, PP489 and VHH72 and 5,000 for TRA.
- Origin. ViroBench: 8 of 76 configurations are `author_reported`, namely the four ViroHyena sizes,
  ViroDNABERT2, ViroCaduceus and the from-scratch BiLSTM and CNN; the other 68, including BLAST and
  Kraken2, are `independent_paper`. That matches the paper: the ViroBland pre-training strategy and
  the Viro* models are the authors' own (Section 5 and Appendix E.3), and no author of the ViroBench
  paper is an author of the third-party models evaluated. MochiBind: MochiBind is `author_reported`
  and Graphinity, Boltz-2 and GeoDock are `independent_paper`. I checked the author list (Li, Zhao,
  Sonmez, Giancardo, Guo, Hong, Cheng, Yilmaz and others) against the three baseline methods and
  found no overlap. Graphinity is borderline only in the sense that the authors fine-tuned it
  themselves; the model is third-party, so `independent_paper` is right, and M4 covers the caveat.
- Locators. Every ViroBench result locator names the table, the row label exactly as printed, the
  column triple and the text-layer line, and all 912 resolve to the cell they name. Every MochiBind
  locator names the Table 2 row and column and resolves.
- Nulls. I checked the `missing_metadata` reasons on a sample of configurations, evaluations and
  results in both batches. The only ones that are not genuinely unstated are MochiBind's
  `comparison.population` and `comparison.aggregation`, which M1 and M2 fix.

Duplicates and scope.

- Neither batch shares a record ID with the store (52,446 existing IDs, zero collisions), and every
  cross-batch link resolves to an existing store record, including `catalog-model-boltz-2`,
  `discovery-model-esm-2`, `catalog-model-kraken2`, `dna-pathogen-20261009-method-blast` and the
  genomics-lane foundation-model records.
- No ViroBench, MochiBind, AlphaBind, GeoDock or Graphinity records exist in `data/entities` or
  `data/evidence`, so neither source is already represented.
- No other open lane branch or worktree holds these sources: I grepped the batches of every
  `../rewire-benchmark-data-lit-*` worktree for `2605.25388`, `isci.2026.116522`, `ViroBench` and
  `MochiBind` and found nothing outside this branch.
- Scope fit. ViroBench is a multi-model independent comparison of nucleotide foundation models with
  conventional baselines on the same protocol, in the microbial lane; areas `microbes-communities`
  and `dna-genomes` are right. MochiBind is an interactions-lane comparison that puts a foundation
  model (Boltz-2) against conventional and supervised baselines on held-out antigens; areas
  `molecular-interactions` and `proteins-complexes` are right. Both fit the pass's focus.

Repository checks.

- `npx tsc --noEmit -p .` passes.
- `npm run test:fast` passes: 40 files, 361 tests.
- `npm run validate:benchmark-literature` passes.
- I ran no build and wrote no receipt, since the corrections above come first and I was asked not to
  change records.

## What I did not check

- Supplementary Tables S1 and S2 of the MochiBind paper (McNemar chi-squared values, Graphinity
  before and after fine-tuning) were not retrieved, so the footnote conflict in M3 is diagnosed from
  the main text alone.
- ViroBench generation results (Tables 5, 6, 27, 28), the recall, precision and AUPRC tables (22, 23,
  24) and all figures are outside the batch's stated scope and were not checked beyond confirming
  that no extracted value comes from them.
- The KDD conference version of ViroBench (ACM DOI 10.1145/3770855.3819057) was not retrieved, so I
  cannot say whether its tables differ from the arXiv v1.

---

# Review: reviewer-mi-2, interactions batches leakctl, ppiemb, plmdta

Reviewer: Claude research agent (reviewer-mi-2), independent of the extractor; no human review claimed.
Date: 2026-10-11. Worktree: `rewire-benchmark-data-lit-microbial-interactions`, uncommitted files. No records were edited.

Every printed value in all three batches matches its source. The corrections below are metadata only:
training and adaptation descriptions, origin, populations, splits, units and limitations. None changes a
number.

## Verdicts

| Batch | Verdict |
| --- | --- |
| `lit-interactions-20261011-leakctl` (PLABench, 279 results) | Approved with corrections |
| `lit-interactions-20261011-ppiemb` (bbag313, 308 results) | Approved with corrections |
| `lit-interactions-20261011-plmdta` (bioRxiv 2026.08.31.748056v1, 64 results) | Approved with corrections |

Prefix shorthand used below: `LC-` = `lit-interactions-20261011-leakctl-`, `PE-` =
`lit-interactions-20261011-ppiemb-`, `PD-` = `lit-interactions-20261011-plmdta-`.

## leakctl corrections

L1. Wrong adaptation for the sequence models on CASP16 and ChEMBL35. The source says DeepDTA, LLF and
MixingDTA were retrained on the PDBbind v2020 refined set before CASP16 and ChEMBL35 (text-layer lines
around Results lines 76-77; Methods lines 357-358 and 397-404: 4,465 training and 497 validation complexes,
a random 90/10 split with early stopping, longest single chain). The records say "Published model applied
without retraining".
- In `attributes.comparison.adaptation` of these 9 evaluations, set the value to
  `"Retrained by the benchmark authors on the PDBbind v2020 refined set (4,465 training, 497 validation complexes; longest single chain)"`:
  `LC-eval-deepdta-casp16-l1000`, `LC-eval-deepdta-casp16-l3000`, `LC-eval-deepdta-chembl35`,
  `LC-eval-llf-casp16-l1000`, `LC-eval-llf-casp16-l3000`, `LC-eval-llf-chembl35`,
  `LC-eval-mixingdta-casp16-l1000`, `LC-eval-mixingdta-casp16-l3000`, `LC-eval-mixingdta-chembl35`.
- In `attributes.parameters` of `LC-config-deepdta-casp16-chembl35`, `LC-config-llf-casp16-chembl35`
  and `LC-config-mixingdta-casp16-chembl35`, replace "Sequence-based model as trained by the benchmark
  authors (Methods); applied to CASP16 and ChEMBL35 without retraining on them" with "Retrained by the
  benchmark authors on the PDBbind v2020 refined set (CASF and CSAR overlaps and censored entries removed;
  4,465 training and 497 validation complexes; random 90/10 split with early stopping; longest single
  chain); applied to CASP16 and ChEMBL35 without further training (Methods, 'PDBbind v2020 dataset')".

L2. MFE training conflicts within the source. Results lines 78-80 say the structure-based methods used
their official pretrained checkpoints. Data availability (line 542) lists "the retrained sequence-model
and MFE checkpoints".
- In `LC-eval-mfe-casp16-l1000`, `LC-eval-mfe-casp16-l3000` and `LC-eval-mfe-chembl35`, remove
  `comparison.adaptation` (set it to null) and add `missing_metadata["comparison.adaptation"] =
  {"reason": "conflicting", "note": "Results (lines 78-80) say structure-based models used official pretrained checkpoints; Data availability (line 542) lists retrained MFE checkpoints"}`.
- In `LC-config-mfe-casp16-chembl35`, append the same note to `parameters`.

L3. Populations are stated but recorded as unreported. CASP16 L1000 has n = 17 ligands and L3000 has
n = 123 (Methods lines 424-425; Figure 2 legend). ChEMBL35 has 4,862 ligand-target pairs across 71
targets (Methods lines 451-453; Data availability line 539).
- For the 9 `LC-eval-*-casp16-l1000` evaluations, set `comparison.population` to
  `"17 ligands (chymase, CASP16 series L1000)"`; for the 9 `LC-eval-*-casp16-l3000` evaluations,
  `"123 ligands (autotaxin, CASP16 series L3000)"`; for the 9 `LC-eval-*-chembl35` evaluations,
  `"4,862 ligand-target pairs across 71 targets"`. Delete `missing_metadata["comparison.population"]` from
  those 27 evaluations.

L4. The ChEMBL35 protocol limitations contradict each other. The first says metrics are computed over all
test pairs; the third says pooling is not stated.
- In `LC-protocol-chembl35` `limitations`, replace the first entry with "Methods ('Evaluation metrics')
  define each metric over N target-ligand pairs, but the source does not state whether Table 4 pools all
  4,862 pairs or averages per-target values." Keep the third entry.
- In the two CASP16 protocols, replace the first limitation with "Each series is a single target; Figure
  2 states that each tau is computed over all ligands of a series, and Methods define the metrics over all
  test pairs." This applies to `LC-protocol-casp16-l1000` and `LC-protocol-casp16-l3000`.

L5. The cold-split aggregation is stated. Methods lines 389-394 say the five fold models were each
evaluated on the same fixed test set "and their final predictions were aggregated".
- For the 12 cold-split evaluations (`LC-eval-{deepdta,llf,mixingdta}-{davis,kiba}-cold-{target,drug}`),
  set `comparison.aggregation` to `"Predictions of the five fold models on one fixed test set aggregated (Methods lines 389-394); the aggregation function is not stated"`
  and remove `missing_metadata["comparison.aggregation"]`.

L6. `unit_detail` on MSE and RMSE does not cover ChEMBL35, and it reads "error" for a squared quantity.
- For the 9 `LC-result-*-chembl35-mse` and 9 `LC-result-*-chembl35-rmse` results, set `unit_detail` to
  `"ChEMBL35 Kd, Ki or IC50 affinities (EC50 excluded; Methods lines 445-450); the scale and unit are not printed"`.
  For MSE, prefix the value with "Squared error; ".
- For the other 36 `LC-result-*-mse` results, change the leading "Error in" to "Squared error in".

L7. Optional, but recommended.
- In `LC-config-boltz2-casp16-chembl35` `parameters`, add "10 structural samples, affinity scored on the
  highest-ipTM pose, 500 sampling steps, 5 recycling steps (Methods lines 437-439)".
- On `LC-data-davis-*`, add `population`: "Standardised Davis: 25,772 pairs, 379 unique sequences, 68
  ligands (Methods lines 363-369)". On `LC-data-kiba-*`, add: "TDC KIBA: 117,657 pairs, 229 proteins,
  2,068 ligands (Methods lines 382-384)".

## ppiemb corrections

P1. Uncertainty is described wrongly. The footnote of Tables 5 and 6 prints "Maximum Standard deviation
value of 0.0711 for OGBl-ppa and of 0.0928 for HuRI". That means repeated runs exist, but no per-cell
spread is given.
- In the 4 protocols `PE-protocol-{ogbl-ppa,huri}-{hits-100,accuracy}`, replace the limitation "No
  uncertainty or number of runs is printed." with "No per-cell uncertainty or run count is printed; the
  footnote of Tables 5 and 6 gives only the table-wide maximum standard deviation (0.0711 OGBl-ppa, 0.0928
  HuRI)."
- In `PE-source-bbag313` `limitations`, make the same replacement for "No uncertainty, seeds or repeat
  counts are printed with Tables 5 and 6."
- On all 308 results, add `"note": "Only a table-wide maximum SD is printed (Table 5/6 footnote)"` to
  `missing_metadata.uncertainty`. Keep the reason `unreported`.

P2. The HuRI split is invented, and the HuRI dataset version is a copy error.
- In `PE-data-huri`, set `version` to "HuRI as used in bbag313; release and file in Supplementary Table
  S1 (not retrieved)". Remove `split` and add `missing_metadata.split = {"reason": "unreported", "note":
  "Main text does not describe the HuRI train/test edge split"}`.
- In `PE-data-ogbl-ppa`, set `split` to "Not stated in the main text; leaderboard hyperparameters
  reproduced (Experimental design), so the OGB split is implied but not confirmed". Alternatively,
  remove it and give the same reason `unreported`.
- On the 154 HuRI evaluations (`PE-eval-*` linked to `PE-protocol-huri-*`), remove `comparison.split`
  and add `missing_metadata["comparison.split"] = {"reason": "unreported"}`.

P3. Origin of the ensemble. The majority-vote ensemble is the study authors' own construction, so the
evaluated method's authors are the paper's authors.
- Set `origin` to `author_reported` on the 28 evaluations whose system is a `PE-config-*-ensemble`
  configuration. The other 280 remain `independent_paper`. The author list (Balbi, Sousa, Cotovio,
  Pesquita) has no overlap with ESM-2, ProGen2, ProtTrans, ESM-IF1, PiFold, ProstT5, TransE, ComplEx,
  RDF2Vec, GCN, GraphSAGE, NGNN or SEAL authors. Sousa is at Mannheim and co-authors with Paulheim, but
  is not an RDF2Vec author.

P4. ProstT5 identity. Add to `PE-model-prostt5` and to the 7 `PE-config-*-prostt5` configurations:
`missing_metadata.version.note`, or a `parameters` note, reading "Tables 5 and 6 print ProstT5 under
Structure; Experimental design names ProtT5 as the third structure embedding. Table label followed;
Supplementary Table S3 not retrieved." `PD-config-plm-graphdta-prostt5-*` links to `PE-model-prostt5`.
That link is fine because the plmdta source names ProstT5 unambiguously, but the two batches must be
added together.

P5. Extend the existing `evidence_concerns` entry (see Q1 below) with: "Random-feature baselines on
OGBl-ppa (GCN 0.0588, GS 0.0104 Hits@100) look far below the public OGB leaderboard values the authors
say they reproduced (Supplementary Table S2, not retrieved; reviewer did not verify the leaderboard
values)."

## plmdta corrections

D1. The Davis data are the corrected Monteiro et al. 2022 version, and Appendix A says all models were
trained on it. The relevant lines (text-layer 1008-1010) read "we trained all models and report
prediction results on this corrected version of the Davis dataset", which reduced MSE by about 15%.
- In `PD-data-davis-deepdta-holdout`, set `version` to "Davis as corrected by Monteiro et al. 2022
  (mutant sequences resolved; Appendix A), DeepDTA folds". Append to `description`: "Evaluated on the
  corrected version with mutant sequences resolved (Appendix A); not the commonly used DeepDTA repository
  sequences."
- For the 8 Davis baseline evaluations (KronRLS, SimBoost, DeepDTA, the four GraphDTA configurations and
  PGraphDTA, on `PD-protocol-davis-deepdta-holdout`), set `origin` to `independent_paper`. No author of
  the source (Marijan, Tanasijevic) is an author of those methods. Set `comparison.adaptation` to
  "Trained by the study authors on the DeepDTA training folds of the corrected Davis set (Appendix A)",
  and remove `missing_metadata["comparison.adaptation"]`.
- In `PD-protocol-davis-deepdta-holdout` `limitations`, replace the first entry with "Proposed models:
  mean over 5 random seeds (Section 3.4.3). Appendix A states that all models, baselines included, were
  trained and evaluated on the corrected Davis set; the seed averaging of baselines is not stated."

D2. The KIBA baselines KronRLS, SimBoost and DeepDTA appear to be copied from Ozturk et al. 2018. Their
printed values (CI/MSE 0.782/0.411, 0.836/0.222 and 0.863/0.194) are identical to DeepDTA arXiv
1801.10193v2 Table 5 (text-layer lines 451-456). I retrieved and checked that table. The plmdta source
does not say whether these were rerun.
- Keep `origin` `unreported` on these 3 KIBA evaluations. Add to each `missing_metadata["comparison.adaptation"].note`:
  "Printed values identical to Ozturk et al. 2018 (arXiv 1801.10193v2) KIBA table; likely copied, not
  rerun."
- Add an `evidence_concerns` entry to `PD-source-marijan2026`: "Table 3 KIBA rows KronRLS, SimBoost and
  DeepDTA equal the values printed in Ozturk et al. 2018, while the proposed models are 5-seed means; the
  rows may not share a training run or protocol. Do not compare these three rows against the proposed
  models automatically." Use locator `Table 3, rows KronRLS, SimBoost, DeepDTA`, the artifact SHA-256
  `11b88d5a...`, and date 2026-10-11.
- In `PD-protocol-kiba-deepdta-holdout` `limitations`, append the same point.

D3. A version is printed but recorded as unreported. Set `version` and remove
`missing_metadata.version` on:
- the 4 `PD-config-plm-graphdta-esmc-600m-*` configurations: `"ESMC 600M"`;
- `PD-config-pgraphdta-esm2-650m-gat`: `"ESM-2 650M, no contact maps (Section 3.3)"`.

## Answers to the collector's questions (my batches only)

1. bbag313 prose against tables. I confirm all three discrepancies. In addition, none of the six
   percentage gains in the first Results paragraph can be derived from Table 5. For example, GS random
   0.0104 against GS RDF2Vec 0.1981 is not "+10.1%", and N-GS random 0.2540 against the best structure
   cell 0.4854 is not "+7.4%". The table cells are consistent between the XML and the rendered PMC HTML
   table. My judgement is that the concern should stay and should block automatic cross-source
   comparison. The prose looks as if it describes a different run. The baselines do not visibly match the
   OGB leaderboard they claim to reproduce, and the third structure column is named differently in prose
   and table. Within-table use (embedding against random features under the same GNN) is reasonable, so
   the batch should not be rejected. Extend the concern as in P5 and record the ProstT5 note (P4).
4. FlowDock origin. Agreed. Reference 7 is Morehead and Cheng, and Cheng is the corresponding senior
   author of PLABench, so `author_reported` is right. I checked references 4-6 and 12-16. None of
   DeepDTA, MixingDTA, Boltz-2, FLOWR.ROOT, Graph_RG (Zhang), LCDD-team (Sim and Lee), MFE (Xu et al.) or
   LLF (Choi and Park) includes Wang or Cheng, so `independent_paper` is right for the other eight.
5. ChEMBL35 aggregation. Keep `comparison.aggregation` null. Methods define metrics over N target-ligand
   pairs, which suggests pooling, but the "target-centric" wording and the per-target figure leave Table
   4 ambiguous. Fix the contradictory limitation (L4).
7. Units. `unit-unreported` with `unit_detail` is right for Davis, KIBA and CASP16, both in PLABench and
   plmdta (plmdta Section 3.1.1 confirms pKd). The leakctl `unit_detail` misses ChEMBL35 and should say
   "squared" for MSE (L6).
9. Use-case relevance. Agreed, none. I enumerated the 26 use cases in `data/entities/use-cases.jsonl`.
   None asks for ligand affinity ranking or PPI link prediction, and
   `use-case-structural-hypotheses-experiments` is about interface or structure reliability, not
   affinity. No judgement claims are needed. The store has no ligand-prioritisation use case; that is a
   gap for the owner.

Questions 2, 3, 6 and 8 concern virobench and mochibind and are outside my scope.

## Checks run and outcomes

Sources and hashes.
- bbag313: re-downloaded the PMC XML from the recorded Europe PMC URL. Its SHA-256
  `360d4f17b779e07f170c3f0c3755bfbfddd064831bf5a81d2642a4cfffd4866c` matches the source record.
- PLABench and plmdta: re-downloaded the bioRxiv PDFs. As the collector warned, the PDF hashes differ
  because of the per-request banner (`c16fa431...` and `0736e340...`; plmdta has the identical byte
  size, 12,564,280). Both have 30 and 24 pages. The `pdftotext -layout` text layers (poppler) hash
  exactly to the recorded `acc4a3c5deb4...` and `e9b9dff90c73...`, so the content I checked is the
  content extracted. I recommend the receipt record both the PDF and text-layer hashes.

Automated full comparison. I used my own parsers in the scratchpad (`mi2scripts/cmp_lc.py`,
`cmp_ppi.py`, `cmp_dta.py`), not the collector's scripts. Each mapped every result through its
evaluation, configuration and protocol to a (model, dataset or split, metric) cell.
- leakctl: 279 of 279 cells parsed (Table 2: 108, Table 3: 108, Table 4: 63). All 279 `printed_value`
  and `numeric_value` match, all locator line numbers match, and no cell was missed.
- ppiemb: 308 of 308 cells (2 tables x 2 datasets x 7 rows x 11 columns). All match and no cell was
  missed. The misaligned HuRI N-GCN row is laid out the same way in the XML and the PMC HTML; reading its
  11 values in column order is the only consistent reading.
- plmdta: 32 rows, 64 cells. All match and no cell was missed.
- `claims.csv`: rows, printed values and locators equal the batch for all 651 results.

Hand check against the rendered tables.
- leakctl: 44 randomly sampled values covering Tables 2, 3 and 4 and all nine models were read from
  rendered page images (pages 6, 10 and 12 at 110 dpi). 44 of 44 match.
- ppiemb: 42 values covering Tables 5 and 6, both datasets, all 7 rows and all 11 columns were read from
  the PMC HTML rendering (pmc.ncbi.nlm.nih.gov, retrieved 2026-10-11). The Europe PMC PDF render was
  blocked by a Cloudflare challenge. 42 of 42 match.
- plmdta: 44 values covering both tables and every model family were read from rendered pages 10 and 11.
  44 of 44 match.
- I also confirmed that the plmdta prose percentages (16.08%, 0.89%, 1.35%, 13.89%) follow from the
  printed cells.

Mappings checked.
- Metric concepts, directions (the arrows in the headers), units, qualifiers and the uncertainty
  missingness were checked against table headers, footnotes and the Methods definitions.
- Configuration and protocol attachment and dataset and split descriptions were checked against the
  Methods. The findings are L1 to L6, P1, P2 and D1 to D3.
- The DeepDTA paper (arXiv 1801.10193v2) was retrieved only to test D2.

Origin and author overlap. I checked the reference lists and author lists of all three sources (see Q4,
P3 and D1). plmdta proposed models (PLM-GraphDTA, DeepGraphDTA) are correctly `author_reported`.

Duplicates.
- Store at `ff5e5aa`: no existing source, model, method, dataset or benchmark for these DOIs, PLABench,
  FlowDock, FLOWR.ROOT, MixingDTA, LLF, Graph_RG, LCDD-team, MFE, GraphDTA, PGraphDTA, KronRLS, SimBoost,
  PiFold, ProtTrans, ProstT5 (only configuration `pfmbench-method-prostt5`, with no model link), OGBl-ppa,
  HuRI, Davis, KIBA or ChEMBL35.
- Reuse of `catalog-model-boltz-2`, `identity-model-deepdta`, `discovery-model-esm-2`,
  `discovery-model-esm-if1`, `discovery-model-esmc` and `uc20260930-model-progen2` is appropriate. The
  store also holds `catalog-model-esm-2`, which is a variant of `discovery-model-esm-2`; the family-level
  link is right.
- Other lit branches (`git grep` on all 14 `claude/lit-20261011-*` branches) and uncommitted lit batches
  in the 9 `../rewire-benchmark-data-lit-*` worktrees hold no record for these sources or models. The
  only hits were description-QA batches touching existing ProstT5 and Boltz records.
- Within this pass, leakctl and plmdta both define Davis and KIBA datasets. They are different versions
  (PLABench-standardised against Monteiro-corrected, MixingDTA splits against DeepDTA folds), so they
  should remain separate records.

Scope. All three are in the `interactions` lane and in scope.

Not done.
- `npm test`, `npm run typecheck` and `npm run build` were not run, because the brief said not to edit
  or commit and these batches are not in the store yet.
- No `review.json` receipt, dated review or `review` objects were written. The collector or integrator
  should do that after applying the corrections and should name this file as the review evidence.
- Supplementary materials (bbag313 Tables S1-S7, PLABench Zenodo deposits) were not retrieved.
- Figures were not read.
