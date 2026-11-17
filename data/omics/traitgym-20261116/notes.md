# TraitGym benchmark paper (Benegas, Eraslan and Song 2025), batch traitgym-20261116

Extraction for the fifth part of rewire-bio/rewire-benchmark-data issue #226. Lane: genomics.
Search cutoff 2026-11-16. Extractor: Claude extraction agent; no human review claimed. Review is
a separate pass and has not been done.

Frozen extraction hash: `batch.jsonl` sha256
`c38c6cef1cfe11f06f9f14c978948f4694e2d231af38650f852e7663a3ce3c3e` (350 records, 729,882 bytes).
Scripts: `extract/parse_tables.py` sha256
`088bd266ccc97b562ac1d52cd5cd7fa22bedcd8382f7f7ee1017d7c5ec23cbea`, `extract/compare_s8.py`
sha256 `e334d9c1bdef2da2eb39471ae7f01893d332db74183884a831a6ce643a26f45d`, `extract/build.py`
sha256 `c7ce4895ad08dac067662757735605a10b555c4b9901e6da493dc8c2ef0ca994`.

Every record has `status` `source_checked`, the store's convention for a value transcribed from a
pinned source. It is the extractor's statement that the value came from the artifact, not a review
sign-off; each record's `review` block names the extraction method and says sign-off is left to
`review-evidence`.

## The version pinned

The issue asks for "the benchmark paper". It is still a preprint:

> Benegas, G., Eraslan, G. and Song, Y. S. **Benchmarking DNA Sequence Models for Causal
> Regulatory Variant Prediction in Human Genetics.** bioRxiv 10.1101/2025.02.11.637758, version 2,
> posted 2025-03-04. CC BY-NC-ND 4.0. Not certified by peer review.

Tonight's GPN-Star batch found a preprint that the bioRxiv API still called unpublished but which
had appeared in Nature under a changed title, so publication was checked four ways rather than
trusting the API. The bioRxiv API lists two versions and `published: "NA"`. PubMed holds the
preprint as 39990426 and nothing else for this work; a PubMed author search for Benegas G returns
the lab's other 2026 papers, including GPN-Star in Nature, but no journal version of TraitGym.
Europe PMC holds PPR978187, the preprint, with no full text. Crossref holds only the
`posted-content` record, with an empty `relation` object, and a Crossref title search finds no
journal article. The preprint is the version of record as of 2026-11-16.

Source record: `traitgym-20261116-source-biorxiv-v2`.

| What | Value |
| --- | --- |
| Artifact | `https://www.biorxiv.org/content/10.1101/2025.02.11.637758v2.full.pdf`, 37 pages |
| PDF sha256 | `80426c499e0b498e07c07ea598a2f68049adea7569b30fda58cdc0ebafa6c7aa` (this retrieval) |
| Text layer sha256 | `23ae4d67751f1092e5cc2da66b52091fa9bbc3ec59310f06bc65be28f93c5097` (stable) |
| Retrieved | 2026-11-16T01:09:36Z |

bioRxiv stamps each download, so the PDF hash pins one retrieval and not the document: a second
download minutes later gave `5f424797ed5c92a3852a52e8ecf29f0c3a3416740a47fe9f9fefe9fd9fb0c876`.
The `pdftotext -layout` text layer was byte-identical across both downloads, and that is what every
value in this batch was read from, so the text-layer hash is the check a reviewer should use. The
source record says so in `hash_scope`. The copies used for the extraction are at
`/private/tmp/claude-501/-Users-timrichardson-Documents-projects-personal-blog/2b3e629e-c97e-4855-9278-c3793c720747/scratchpad/traitgym/`
as `paper.pdf` and `paper.txt`; that is session scratch, so re-download rather than rely on it. The
PDF is not archived under `artifacts/`: it is open at a stable URL, and under CC BY-NC-ND the batch
does not need a copy to read it.

The supplementary material is pages 19 to 37 of the same PDF. The v2 supplementary-material page
lists no separate file, so Tables S1 to S11 are in the artifact already pinned.

## What the store already held, and from where

Every TraitGym record in the store before this batch rests on one source,
`lit-genomics-20261011-traitgym-source-hf-metrics`: the benchmark's own metric CSVs on Hugging Face
at revision `1fde19555fe8`, not a paper. That is the gap issue #226 names.

| Kind | Count | IDs |
| --- | --- | --- |
| source | 1 | `lit-genomics-20261011-traitgym-source-hf-metrics` |
| benchmark | 1 | `lit-genomics-20261011-traitgym-benchmark-traitgym` |
| dataset | 2 | `...-data-mendelian-traits-matched-9`, `...-data-complex-traits-matched-9` |
| protocol | 4 | `...-protocol-{mendelian,complex}-traits-matched-9-{zero-shot,linear-probing}` |
| configuration | 81 | `lit-genomics-20261011-traitgym-config-*` |
| method | 5 | four logistic regression ensembles and phastCons |
| model | 1 | `lit-genomics-20261011-traitgym-model-specieslm` |
| evaluation | 156 | `lit-genomics-20261011-traitgym-eval-*` |
| result | 156 | `lit-genomics-20261011-traitgym-result-*` |
| claim | 11 | 6 GPN-MSA identity claims, 1 use-case mapping per protocol (4), 1 more |

The 156 results split 63 Mendelian zero-shot, 57 complex zero-shot, 18 Mendelian linear probing and
18 complex linear probing, all AUPRC by chromosome with a sample-size weighted average over
chromosomes, on subset `all`, with a bootstrap standard error.

Two other batches hold TraitGym records of their own, from their own sources, and were left alone:
GFMBench-API (`lit-genomics-20261011-gfmbench-*`, six protocols and two datasets, from the
GFMBench-API preprint) and the AlphaGenome Atlas (`ag-atlas-20261019-*`, four protocols and two
subsets, from the Atlas preprint).

## Paper against store, cell by cell

Table S8 is the paper's only table that prints values which correspond to stored results: the
zero-shot AUPRC of ten genomic language models under five scoring approaches on both datasets, 100
cells at three decimal places.

**The protocols are the same.** Appendix B.4 (page 24) ends: "To allow easy comparison, we also use
the weighted average AUPRC to evaluate zero-shot scores, even though it is not strictly necessary."
So the paper's zero-shot AUPRCs are on the chromosome-weighted basis, which is the basis of the
stored values (files under `AUPRC_by_chrom_weighted_average/all/`). This contradicts the stored
source record, which says the opposite; see the correction below.

**Mapping.** The embedding columns map to the `Embeddings.*` metric files, not to the
`InnerProduct`/`EuclideanDistance` files the benchmark also publishes for six Mendelian rows. The
discriminating cell is GPN-Promoter, L2 dist., Mendelian: the paper prints 0.345,
`GPN_final_Embeddings.plus.euclidean_distance` is 0.34499569 and
`GPN_final_EuclideanDistance.plus.score` is 0.34696330, which rounds to 0.347.

**Outcome.** `extract/compare_s8.py` maps each cell to the stored result whose `source_locator`
names the matching CSV, rounds the stored full-precision value to three decimal places and
compares. All 100 cells agree. No correction claim about a value is needed.

| Status | Rows | Meaning |
| --- | --- | --- |
| matched | 100 | paper value equals the stored value rounded to 3 dp |
| DIFFERS | 0 | none |
| no_paper_counterpart | 36 | stored linear probing results; the paper prints them only in Figure 5 |
| no_paper_counterpart | 14 | stored zero-shot results of models that are not gLMs (Borzoi, Enformer, Sei, CADD, phastCons-43p, phyloP-100v, phyloP-241m, on both datasets); Table S8 covers gLMs only |
| no_paper_counterpart | 6 | duplicate scoring variants in the metric files, whose `Embeddings.*` twin Table S8 prints |

100 + 36 + 14 + 6 = 156, so every stored result is accounted for. The full table, one row per
stored result with the stored ID, the stored value, the rounded value, the paper value and whether
the protocol is the same, is `extract/comparison.tsv`. A sample of the matched rows:

| Dataset | Model | Score | Paper | Stored | Rounded | Stored result |
| --- | --- | --- | --- | --- | --- | --- |
| Mendelian | GPN-MSA | LLR | 0.694 | 0.6944749707632801 | 0.694 | `...-result-gpn-msa-llr-minus-score-mendelian-traits-matched-9` |
| Mendelian | GPN-Promoter | L2 dist. | 0.345 | 0.3449956870746872 | 0.345 | `...-result-gpn-final-embeddings-plus-euclidean-distance-mendelian-traits-matched-9` |
| Mendelian | Evo2 40B | LLR | 0.557 | 0.5565372191993592 | 0.557 | `...-result-evo2-40b-llr-minus-score-mendelian-traits-matched-9` |
| Complex | GPN-MSA | abs(LLR) | 0.224 | 0.22364303968775792 | 0.224 | `...-result-gpn-msa-absllr-plus-score-complex-traits-matched-9` |
| Complex | Caduceus | LLR | 0.098 | 0.09827404703580568 | 0.098 | `...-result-caduceus-llr-minus-score-complex-traits-matched-9` |

Table S8 was **not** re-extracted as result records. Its cells are the same measurements as 100
results already in the store, printed at lower precision and without the standard errors. Adding
them would put two records of one measurement in the store. The reconciliation is recorded instead
as the claim `traitgym-20261116-claim-paper-agrees-with-benchmark-metric-files` on the benchmark,
which names the comparison file and the mapping rule.

## Recommended corrections to stored records (nothing was edited)

No stored record was edited and `records -- change` was not run.

1. **`lit-genomics-20261011-traitgym-source-hf-metrics`, `attributes.limitations[1]`** says: "The
   paper's Table S8 prints rounded zero-shot AUPRCs on a related but unweighted basis and was not
   extracted." The first half is wrong. Appendix B.4 says the weighted average is used for
   zero-shot scores too, and all 100 cells match the stored weighted values at three decimal
   places. Recommended replacement: "The paper's Table S8 prints the same zero-shot AUPRCs rounded
   to three decimal places, on the same chromosome-weighted basis (paper Appendix B.4); all 100
   cells match these values and were reconciled rather than re-extracted in
   data/omics/traitgym-20261116."
2. **The eight `lit-genomics-20261011-traitgym-config-gpn-final-*` configurations** link
   `configuration_of` to `regulatory-variant-20261009-model-gpn`, the GPN model. The paper's
   `GPN_final` is GPN-Promoter, a different model that the paper introduces as "This work": 152M
   parameters, ByteNet architecture, trained on 512-bp promoter windows of 434 animal genomes
   (Table 2, Appendix B.2, Table S6). It follows GPN's training objective but is not GPN. This
   batch registers `traitgym-20261116-model-gpn-promoter` with that metadata and leaves the stored
   links untouched. Recommended: relink those eight configurations to the GPN-Promoter record. That
   also affects 14 stored evaluations and 14 stored results, which currently read as GPN results.
3. **`lit-genomics-20261011-traitgym-benchmark-traitgym`** rests only on the metrics source and its
   `scope_note` and `version` describe a Hugging Face revision. The 21 benchmark claims this batch
   adds give it the paper's own definition. Recommended: add
   `traitgym-20261116-source-biorxiv-v2` to its `source_ids`, which an extractor cannot do without
   editing the record.
4. **`companion_of`** should run from the metrics source to the paper source, and the relation is
   declared only in that direction, so the edge has to go on the stored record. Recommended: add
   `{"relation": "companion_of", "target_id": "traitgym-20261116-source-biorxiv-v2"}` to
   `lit-genomics-20261011-traitgym-source-hf-metrics`.
5. **The stored source's `hash_scope`** warns that Hugging Face datasets are mutable. Unrelated to
   the paper, but worth re-checking at review: revision `1fde19555fe8` was last modified
   2025-03-25 and the hash was verified in the 2026-10-11 review.

## What was extracted as new results

Four tables print values the metric files do not hold. Every cell of each was taken.

| Table | Page | Cells | What |
| --- | --- | --- | --- |
| S11 | 28 | 104 | AUPRC per trait for Borzoi, GPN-MSA, CADD and the ensemble, 26 traits |
| 5 | 13 | 18 | highest AUPRC among Borzoi tracks from a tissue, top three tissues for six traits |
| 4 | 12 | 6 | AUPRC of a single CADD input feature, top feature in three categories per dataset |
| S4 | 22 | 4 | global AUPRC of the features the controls were matched on |

132 results, 132 evaluations, all `origin` `author_reported`.

Existing IDs reused rather than created again:

- benchmark `lit-genomics-20261011-traitgym-benchmark-traitgym` (every new protocol is `part_of` it)
- datasets `lit-genomics-20261011-traitgym-data-{mendelian,complex}-traits-matched-9` (the new trait
  subsets are `same_data_as` them, and Tables 4 and S4 use them directly)
- model `regulatory-variant-20261009-model-borzoi` (Table S11 Borzoi column; the 15 new tissue
  configurations are `configuration_of` it)
- model `gfm-guides-20261014-gpnmsa-model-gpn-msa` (Table S11 GPN-MSA column)
- method `somatic-oncogenicity-20261009-method-cadd` (Table S11 CADD column). It is a
  version-free family record: `missing_metadata.version` reads "Family record; score sources are on
  configurations", and its status is `source_checked`. The paper's CADD is v1.7, from the GRCh38
  `whole_genome_SNVs_inclAnno` file (Appendix B.1), so the 26 evaluations that use it carry
  `model_version` "CADD v1.7, GRCh38 whole_genome_SNVs_inclAnno (Appendix B.1)". The same is done
  for Borzoi (gReLU Model Zoo) and GPN-MSA (songlab/gpn-msa-sapiens) on the Table S11 rows.
- method `lit-genomics-20261011-traitgym-method-cadd-plus-gpn-msa-plus-borzoi-logistic-regression`
  (Table S11 complex Ensemble column, the full feature ensemble)

New entity records: 1 model (GPN-Promoter), 10 methods (the lightweight ensemble, six CADD input
features, three matched features), 15 configurations (Borzoi tracks per tissue), 26 dataset subsets
(one per trait), 8 protocols (two per table, Mendelian and complex).

The systems of Tables 4 and S4 are `method` records, not `baseline` records: an evaluation's
`system` link accepts a configuration, model, method, pipeline or service, and `baseline` is not
among them.

The two conservation methods of Table 4 are **not** the stored `phyloP-241m` and `phastCons-43p`
configurations. Table 4's ZooVerPhyloP is 0.673 on Mendelian traits where the stored phyloP-241m is
0.696, and ZooPriPhyloP is 0.225 on complex traits where the stored phastCons-43p is 0.237. The
CADD-bundled annotation and the separately downloaded bigWig are different systems; each method
record says so in `identity_scope`.

Protocols were created rather than reused because each of these tables fixes a different selection
rule, and the stored zero-shot and linear-probing protocols fix neither:

- Table S11 reports, per cell, the better of the zero-shot and the linear probing score, and does
  not say which. `comparison.adaptation` says so; `metric_implementation` and `aggregation` are
  null with reason `unreported`, which blocks automatic comparison, as intended.
- Table 5 reports the highest AUPRC among the Borzoi tracks of a tissue, on the trait's own
  variants, with the track unnamed.
- Table 4 reports the top CADD input feature per category, selected on the same variants.
- Table S4 is a global AUPRC, not the weighted average: `metric_qualifier` says "global AUPRC over
  all variants; single matching feature as the score".

Each of those selection rules is also recorded in the protocol's `selection_bias`, because every
one of them selects on the variants it then reports.

## What was extracted as claims

25 claims, 21 on the benchmark and 4 on GPN-Promoter. The point of this batch is that the
benchmark's definition should rest on its paper rather than on a metrics table, so the claims cover:
the paper of record; the variant and trait counts (Table 1); how Mendelian positives and controls
are defined (OMIM via Smedley et al. 2016 Table S6, MAF at most 0.1 per cent in gnomAD 3.1.2,
controls above 5 per cent); how complex positives and controls are defined (UK Biobank fine-mapping
of 2019-12-03, FINEMAP and SuSiE averaged, disagreement above 5 per cent dropped, PIP above 0.9,
p below 5e-8, controls below 0.01); the matching procedure and the 0.1 baseline; the annotation
pipeline (VEP 109.1, `--most_severe --distance 1000`, non-coding consequences only, ENCODE cCRE
categories and their 500-bp flanks); the task definition and the allowed inputs; the metric and its
weighting, with the Appendix B.4 quote; the bootstrap schemes behind the standard errors (1000
samples of chromosomes for linear probing, 100 within-class samples for zero-shot); the linear
probing pipeline and the leave-one-chromosome-out split; the zero-shot score selection rule
(Table S9, each selected approach being the argmax of Table S8); the CADD training overlap counts
(Table S10); the matched-feature control; the expanded datasets; the consequence and trait
composition; the benchmarked models and their checkpoints (Tables 2 and S5, Appendix B.1); the
feature and score definitions (Table 3, Appendix B.3); availability; which rows are
author-reported; the paper's stated limitations; and the Table S8 reconciliation.

Table S9 was written as a claim, not as results: it is the rule that decides which stored
configuration stands for each model in the paper's headline figure, not a measurement. It was
checked against Table S8 cell by cell; every selected approach is that model's highest-scoring
approach on that dataset, which is itself a selection-on-test-set caveat and is stated in the claim.

GPN-Promoter is registered as a model because the paper introduces it and the store had its scoring
configurations without it. No identity edge to GPN was added: the paper says GPN-Promoter follows
GPN's training objective and the ByteNet architecture, which is not the same as being a variant of
a GPN checkpoint, and `variant_of` and `family` edges carry weight in result navigation. The
question is put to the reviewer below.

## How the values were read

`extract/parse_tables.py` reads the `pdftotext -layout` text layer, asserting its SHA-256 first,
and parses eleven tables by splitting body lines on runs of two or more spaces. For each table it
asserts the column headers, the row labels and the cell count, and for Tables 4, S4, S8 and S11 the
full expected cell set or row set. It writes one TSV per table into `extract/`.
`extract/build.py` turns the TSVs into records; no value is typed into `build.py` by hand except
the quoted sentences in the claims.

Two independent checks were run:

- `npm run batch -- table <text> "Table S8"` and the same for Tables 1, S10 and S11: the
  repository's own reader, which recovers columns from the character positions the body lines share
  rather than from a split, reproduced Tables 1, S8 and S10 cell for cell, and all 104 values of
  Table S11. On two Table S11 rows, the two longest trait names (Estimated heel bone mineral
  density, Estimated glomerular filtration rate (cystain C)), it splits the row label so that the
  first value lands in the label slot: the values are all there but those eight are attributed to
  the wrong row, which is the case `parse_tables.py` handles by taking the last four cells of a row
  as its values. The reader found no table body for Tables 4, 5, S4 and S9, which is why
  `parse_tables.py` anchors each table on its header line rather than on the caption.
- `npm run batch -- check-values data/omics/traitgym-20261116 traitgym-20261116-source-biorxiv-v2=<text>`:
  132 results, 96 `in_cell`, 36 `in_row`, no `not_in_row`, no `wrong_column`, no
  `overclaimed_in_row` (`value-check.tsv`). The 36 that fall back to the row are the 18 Table 5
  cells and the 6 Table 4 cells, whose AUPRC header does not line up with the value column, the 8
  Table S11 cells of the two traits whose names run into the first value column, and the 4 Table S4
  cells, whose row label is shared between the two datasets. A reviewer should re-read those 36 by
  hand.

The batch passes every check `npm run records -- add` makes (schema, vocabularies, attributes,
descriptions, derivations, concerns, relations), run as a dry run that does not write the store.

## Use cases: deliberately not touched

Issue #226 asks that variant results be linked to the variant interpretation use cases (#222, #223,
#224). This batch does not add use-case judgements or a `coverage.json`, for two reasons. The four
stored TraitGym protocols already carry `assessed_by` judgements against
`use-case-regulatory-variant-gene-follow-up` from the 2026-10-11 pass, and those are the protocols
that bear on a use case: whole-dataset zero-shot and linear-probing AUPRC. The eight protocols added
here are a per-trait slice of the same measurements, a tissue-level Borzoi ablation and two feature
ablations, which inform how the benchmark was built rather than how a tool would be used. Adding a
judgement per protocol would also mean updating the stored `use_case` records' `assessed_by` links,
which an extractor cannot do without editing them. If a reviewer wants the per-trait protocols
judged, Table S11 is the one worth considering, because it is the only place the benchmark reports
per-trait performance.

## Gaps

- **The headline comparisons are figures.** Figures 5 to 10 and Figures S1 to S11 print no values.
  bioRxiv publishes no source data file for this preprint, so none of them can be recomputed from
  the source's own rows under docs/collection.md, "Values computed from source data". Figure 5 is
  covered by the stored metric files; Figures 6 to 10 are not covered anywhere.
- **The expanded datasets** (Figure 6, millions of controls, n=339 against 4.9M for Mendelian
  traits and n=1.1K against 2.9M for complex traits) have no printed values in the paper and no
  metric files in the store. The paper's strongest claim for GPN-MSA, that its margin over other
  alignment-based zero-shot scores shows only on these datasets, therefore has no result behind it
  in the store. The benchmark publishes the expanded datasets, but scoring them would be a Rewire
  run, not an extraction.
- **Table S11 cells** do not say whether they are zero-shot or linear probing, and the Mendelian
  Ensemble column does not say which lightweight ensemble it is.
- **Table 5 cells** do not name the Borzoi track behind the value, and the caption's wording
  ("ranked by the highest AUPRC of Borzoi predicted tracks from such tissue/cell type") does not
  settle whether a cell is one track's AUPRC or an aggregate over the tissue's tracks.
- **The AUPRC basis** of Tables 4, 5 and S11 is not stated: weighted average over chromosomes or
  global. Recorded as `unreported` on each evaluation rather than assumed.
- **Per-trait variant counts** are not printed. Each trait subset records `positive_count` and
  `test_count` as `unreported`; the paper states only that a reported trait has at least 10 causal
  variants and less than 10 per cent overlap of causal variants with other traits.
- **Table S7** (ClinVar "Pathogenic" variant consequences) was not transcribed cell by cell. It
  describes a comparison set the paper mentions in passing and supports no result here.
- **Tables S1, S2, S3, S5, S6 and S10** are descriptive and went into claims rather than records of
  their own.
- **The GitHub repository and the leaderboard Space** named in the availability statement were not
  pinned; see `scope-audit.jsonl`.

## Questions for the reviewer

1. **Table S8 duplicates.** Is reconciling the 100 cells against the stored results, and recording
   the outcome as one claim plus `extract/comparison.tsv`, the right call, or should the paper's
   rounded values also exist as result records so that the paper has its own results for the
   headline table? The argument against is that it puts two records of one measurement in the
   store.
2. **GPN_final is GPN-Promoter.** Should the eight stored `...-config-gpn-final-*` configurations be
   relinked from `regulatory-variant-20261009-model-gpn` to
   `traitgym-20261116-model-gpn-promoter`? Fourteen stored results currently read as GPN results.
   If so, that is a reviewed change to stored records, not something this batch did.
3. **GPN-Promoter's identity edges.** Should the new model carry a `family` or `variant_of` edge to
   `regulatory-variant-20261009-model-gpn`, given that the paper says only that it follows GPN's
   training objective and the ByteNet architecture, or should it stand alone as it does now?
4. **Which lightweight ensemble.** Table S11's Mendelian Ensemble column is "lightweight feature
   ensemble" and Figure 8 shows three of them. This batch created
   `traitgym-20261116-method-lightweight-ensemble` for `CADD+GPN-MSA_LLR+Borzoi_L2_L2`, the best in
   Figure 8, and said in the method's `provenance_note` and in each Ensemble result's `limitations`
   that the caption does not name it. Is naming the best one the right reading, or should those
   eight results carry an unidentified system?
5. **Table 5's construction.** Each cell is the best single Borzoi track within a tissue, selected
   on the same variants it is scored on, with the track unnamed, and only the top three tissues of
   traits Borzoi did well on are reported. This batch extracted the 18 cells with that stated in
   the protocol, in `selection_bias` and in every result's `limitations`. Is that preferable to
   recording the table as a gap?
6. **Table 4 and S4 as methods.** Six single CADD input features and three matching features are
   `method` records so that they can be an evaluation's `system`. A `baseline` record would read
   more naturally for "the feature the controls were matched on", but `baseline` is not an allowed
   `system` kind. Is the method modelling right, or should these carry `baseline` records alongside?
7. **Protocol proliferation.** Eight new protocols for 132 results, because each table fixes its
   own selection rule. Could any of them be folded into the stored zero-shot or linear-probing
   protocols without losing the rule?
8. **`metric_qualifier` wording.** The new qualifiers ("best of zero-shot and linear probing; single
   trait; chromosome aggregation unreported", "highest AUPRC among the Borzoi tracks from one
   tissue; single trait; chromosome aggregation unreported", "single CADD input feature as the
   score; chromosome aggregation unreported", "global AUPRC over all variants; single matching
   feature as the score") are new phrasings. Comparisons require identical qualifiers, so these
   deliberately do not compare with the stored "weighted average over chromosomes of
   per-chromosome AUPRC; subset 'all'". Confirm that is wanted.
9. **The 36 `in_row` results.** `check-values` could place 96 of 132 values in their cell and 36
   only in their row. Those 36 need the reviewer's own cell check.
