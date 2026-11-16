# POISK patent-derived antibody dataset and binder-screening benchmark

Requested in issue #231. POISK (Patent-extracted Organization of Immunoglobulin Sequence Knowledge)
is a patent-derived antibody dataset released on Zenodo, and the paper that introduces it benchmarks
six published co-folding models on one decision: which antibody candidates to test for binding to a
chosen antigen. Candidates are supplied as heavy-chain, light-chain and target sequences, folded by
each model, and ranked by the full-Fv ipSAE interface confidence of the predicted complex.

**Those scores are evidence for ranking only.** No result in this batch is a measured binding event
or a binding affinity. Every protocol, benchmark and dataset record says so, and the benchmark
record's `scope_note` and `limitations` carry it.

This batch registers the dataset at two versions, the benchmark, its protocols and the systems
evaluated, and extracts the paper's printed performance tables. Extraction only: a different agent
reviews it, nothing is marked reproduced, and no review sign-off is claimed.

Frozen extraction hash: `batch.jsonl` sha256
`4a99cc8675bffe91ddbc7d75a8d23bc94b2447508d44e3ad4014cec66540b694` (221 records).

## Record counts

| Kind | Count |
| --- | --- |
| source | 5 |
| model | 3 (new) |
| method | 1 |
| configuration | 8 |
| dataset | 2 |
| dataset_subset | 3 |
| benchmark | 1 |
| task | 1 |
| protocol | 13 |
| evaluation | 66 |
| result | 78 |
| claim | 40 |

## Sources

| ID suffix | Artifact | sha256 |
| --- | --- | --- |
| `source-manuscript-v1` | bioRxiv v1 PDF, 16 pages, the artifact every stored value was read from | `526def150fb5ae8f9ac4533efcf16c86e547e636cdb9bfba9a574cd1e2a2f924` |
| `source-manuscript-v1-jats` | bioRxiv v1 production JATS XML, for the article text and captions | `4ae08208acb49686958e1ad6a040494f3234ff7035b8cf41756b913ed6caa826` |
| `source-zenodo-dataset-v1-0-1` | Zenodo REST record 19883049, POISK version 1.0.1 | `c1ee96e66dc4b8a694133aae0536dcc502c6d831b797d50337c002dd987505ee` |
| `source-zenodo-dataset-v1-1` | Zenodo REST record 21775623, POISK version 1.1 | `1b95773c269ca57f971f3b60c5df4558c48edc88b11580ca46e97a06e3d99981` |
| `source-explorer` | poisk-explorer.github.io, served HTML | `7795938b8f8bd488222d9a447f5148756029897d82acc127ef1babf158c46378` |

The PDF was downloaded twice with identical bytes, as was the JATS XML, so neither hash is a
per-download stamp. The two Zenodo records and the explorer page are mutable; their hashes describe
one retrieval each on 2026-11-15, and the Zenodo API reported revision 6 (1.0.1, last updated
2026-11-03) and revision 4 (1.1, last updated 2026-10-24).

Why the PDF and not the XML: **every table in the bioRxiv JATS XML is a graphic.** The XML holds the
article text and all nine table captions but no table markup, so no cell can be read from it. All
values therefore come from a `pdftotext -layout` text layer of the PDF (poppler 26.08.0).

Archived under `artifacts/`, gzipped with `gzip -n -9` so the bytes are reproducible:

| File | sha256 of the gzip | sha256 of the contents |
| --- | --- | --- |
| `biorxiv-v1-layout.txt.gz` | `39d2ff104527916aa9b33386ca5d2830d2efd9e14b4d98258af54f07b0598950` | `e75c18130ca43770d2f0ed05ae96528759666c0e4fa08f7725f5a32b21187696` |
| `biorxiv-v1-source.xml.gz` | `5297d30e690a52b256ea9ab2d84786abaa39425bd6ce7280c594257fde3895b1` | `4ae08208acb49686958e1ad6a040494f3234ff7035b8cf41756b913ed6caa826` |
| `zenodo-19883049.json.gz` | `b5c67deddbd5f330bf926f6782c4c2e7d4363b5e1188360f8b85524e61a69811` | `c1ee96e66dc4b8a694133aae0536dcc502c6d831b797d50337c002dd987505ee` |
| `zenodo-21775623.json.gz` | `3a4b1597baf64567a3f4684aa58ead4167e3febce9f68ea1836032190fd69e7a` | `1b95773c269ca57f971f3b60c5df4558c48edc88b11580ca46e97a06e3d99981` |
| `poisk-explorer.html.gz` | `f0d4abaebf7ce2cd5cee03df6dc49343e76ebc5ecf8a87ce1d0d1824d8a1a391` | `7795938b8f8bd488222d9a447f5148756029897d82acc127ef1babf158c46378` |

The PDF itself is refetchable at the versioned URL and is not archived. The paper and both Zenodo
records are CC BY 4.0, so archiving is permitted.

## The three counts, and which record each belongs to

The issue warns that three counts are three different things. They are kept apart:

| Count | What it is | Where it is recorded |
| --- | --- | --- |
| 89,074 records (78,174 unique antibodies, 10,110 patents) | What the extraction pipeline produced; the manuscript's dataset | `dataset-poisk-v1-0-1.attributes.total` and `claim-dataset-record-counts` |
| 11,247 pairs / 22,494 complexes | The balanced co-folding benchmark | `data-cofolding-benchmark-22494` (`positive_count` 11247, `test_count` 22494) and every pairwise protocol's `denominator` |
| 93,193 rows (47 columns) | The current Zenodo version 1.1 release table | `dataset-poisk-v1-1.attributes.total` and `claim-v1-1-row-count` |
| 540 trials over 27 targets, 25 seeds | The 1-in-50 screening simulation | `data-screening-27-targets` and the screening protocol's `denominator`, `random_seeds` and `replicates` |
| 1,232 records | Residue-level epitope annotations, the epitope-recovery denominator | `data-epitope-annotated-1232` |

No result rests on the 93,193 figure. The version 1.1 dataset record states in its `scope_note` that
its row count is neither the manuscript's 89,074 nor the benchmark's 22,494.

## Data version and folding artifacts are pinned separately

The version 1.1 Zenodo record says of the folding metrics and structures it publishes: "These
predictions were run against dataset version 1.0.1, not against this release." So:

- `dataset-poisk-v1-0-1` is what the benchmark subset and every evaluation point at. Each
  evaluation's `comparison.dataset_version` names version 1.0.1 explicitly.
- `dataset-poisk-v1-1` is a separate dataset record, linked `same_data_as` version 1.0.1 and **not**
  `supersedes`. A `supersedes` edge would say the older release is replaced, and it is not: it is
  still the release the published predictions were computed from. Flagged for the reviewer below.
- `claim-v1-1-folding-version` carries the quoted statement, and
  `claim-v1-1-folding-metrics-files` records that the same `poisk_all_models_folding_metrics.zip`,
  with the same md5, is attached to both records (one CSV per model, 22,494 rows, 28 columns).
- `claim-v1-1-target-sequence-provenance` records the corrected `target.sequence`,
  `target.sequence_from_patent` and `target.sequence_from_uniprot` columns, and
  `claim-v1-1-chain-pair-labels` records the release's own warning that a score whose chain pair is
  not antibody-against-antigen is not a binding metric. Anyone recomputing these endpoints from the
  released metrics has to read that label first.

The two releases also describe the audit field differently: version 1.0.1 lists
`CONTRADICTED, PLAUSIBLE, CONFIRMED` and version 1.1 lists `CONFIRMED, PLAUSIBLE, REVIEW`, with
"REVIEW is not an assertion that a row is false". Both are recorded, each on its own dataset record,
each noting the other.

## Which model records were reused

| Engine as printed | Model record | New? |
| --- | --- | --- |
| Protenix-v1, Protenix-v2 | `ucc-research-model-protenix` | reused; both configurations are `configuration_of` the one family record |
| Boltz-2 | `catalog-model-boltz-2` | reused |
| AlphaFold-Multimer | `poisk-20261115-model-alphafold-multimer` | new |
| IntelliFold v2 | `poisk-20261115-model-intellifold` | new |
| OpenFold3 | `poisk-20261115-model-openfold3` | new |

Protenix is not duplicated: the two releases are configurations of the existing family record, which
is also where the record contract puts an unidentified version. The store holds no AlphaFold-Multimer,
IntelliFold or OpenFold3 record; `discovery-model-openfold` is OpenFold, a PyTorch implementation of
AlphaFold 2 and AlphaFold-Multimer, which is not OpenFold3, and
`lit-structure-20261011-afesmfold-model-alphafold2` is AlphaFold 2, not AlphaFold-Multimer. The three
new records are family level with no lineage link, because this source asserts none; see the reviewer
questions.

**Checkpoints are unknown for all six engines.** The paper names each engine by its printed label and
nothing more: no release tag, commit, container, weights hash or parameter count. Every configuration
therefore carries `version` as the printed label only, with `missing_metadata` for `checkpoint`,
`checkpoint_revision`, `hyperparameters` and `code` (`unreported`, except `code`, which is
`unavailable`: no benchmark code is offered anywhere in the preprint). No value is assigned to a
concrete checkpoint. The same applies at model level: `version`, `checkpoint_revision`,
`training_data`, `licence` and `access` are all absent with reasons.

What the configurations do record, from Section 2.3: ColabFold MSAs, no templates, five predictions
per complex (one diffusion sample at each of five random seeds for the five diffusion models, the five
parameter models for AlphaFold-Multimer), and the highest-confidence prediction retained for scoring.

## Endpoints kept separate, with their denominators

Pairwise accuracy and the one-in-fifty retrieval figure are different endpoints on different
denominators, and are never pooled. Thirteen protocols:

| Protocol | Metric | Denominator | Printed in |
| --- | --- | --- | --- |
| `cohens-d-iptm` | Cohen's d of the ipTM distributions | 22,494 complexes | Table 1 |
| `cohens-d-ipsae` | Cohen's d of the full-Fv ipSAE distributions | 22,494 complexes | Table 1 |
| `pairwise-coverage-100` / `-75` / `-50` / `-25` / `-10` | paired accuracy, binder above its matched decoy | 11,247 pairs, top share by within-pair maximum ipSAE | Table 7 (and Table 1 for 50%) |
| `pairwise-tie-fraction` | proportion of pairs with identical ipSAE | 11,247 pairs | Table 7 |
| `screen-1in50-top1` | top-1 retrieval | 540 trials over 27 targets, 25 seeds | Table 8 summary row and Table 1 |
| `screen-1in50-top10` | top-10 retrieval | 540 trials over 27 targets, 25 seeds | Section 3.2.3 prose |
| `epitope-recovery` | success rate, contact within 4 angstrom | 1,232 annotated binder records | Table 2 |
| `consensus-pairwise-accuracy` | paired accuracy under cross-model pose agreement | pairs eligible at the threshold | Section 3.3.1 prose |
| `consensus-pair-coverage` | proportion of pairs eligible | 11,247 pairs | Section 3.3.1 prose |

The 87% figure is the 50%-coverage protocol, not the benchmark accuracy. `claim-coverage-definition`
quotes Appendix F on that: it "is not the accuracy over the benchmark as a whole", and over all 11,247
pairs Protenix-v2 reaches 0.72. The five coverage levels are five protocols because each fixes a
different retained population, and exact ties take half credit at every level.

### Uncertainty: twice a sample standard deviation across seeds, not a confidence interval

Checked against the Figure 5 legend, which reads: "Bars show mean top-1, top-5, and top-10 accuracy
(by ipSAE ranking) over 25 independent runs with different random seeds; error bars indicate plus or
minus 2 sigma (sample standard deviation across runs)." The NeurIPS checklist (item 7) repeats it and
adds that the pairwise benchmarks use all 11,247 pairs without random sampling, so error bars do not
apply there. The issue's description is correct.

Table 8 prints **two** standard deviations, on different axes:

- *across seeds* (1.5, 0.8, 1.7, 1.6, 1.9, 1.4 points) is the run-to-run spread Figure 5 doubles. It
  is each screening result's `uncertainty` object (`type: standard_deviation`, `n: 25`, `unit:
  percentage points`, with the axis in `scope`).
- *across targets* (13.4, 3.3, 19.0, 11.4, 19.5, 20.6 points) is between-target spread, a different
  quantity. There is no metric concept in `data/vocab/metric.ttl` for a standalone standard
  deviation, and it cannot be a second `uncertainty` on the same result, so it is kept as one claim
  per engine (`claim-screen-target-spread-<engine>`), each naming its printed cell. Flagged for the
  reviewer.

Every result whose table prints no spread carries `missing_metadata.uncertainty` with the reason,
rather than an invented one. No missing value is recorded as zero.

### Values printed twice

Two endpoints are printed in two places at different precision. Both printings are kept, each with
its own locator and a `rounding_note`, attached to the same evaluation:

- 50%-coverage pairwise accuracy: Table 1 "Accuracy at 50% Pairs" to two decimals (Protenix-v2 0.87)
  and Table 7 "50%" to three (0.868). Result IDs end `-t1` and `-t7`.
- 1-in-50 top-1: Table 1 as a fraction (0.29) and Table 8's "Mean over targets" row as a percentage
  (28.9). Result IDs end `-t1` and `-t8`. The units differ (`fraction` against `percent`), so they
  cannot be compared with one another by mistake.

## The negatives are putative, and that is recorded twice

As a dataset claim and as a protocol and benchmark limitation:

- Construction (`claim-decoy-construction`): KA-Search against the Observed Antibody Space for the
  closest VH CDR match to each binder, paired with the original antigen. For the 32% of records with
  no close OAS match, germline-encoded regions were reverted to inferred germline and the CDR-H3 loops
  randomised from AbLang predictions, keeping total identity at 85% or above.
- Composition (`claim-decoy-composition`): 7,647 of 11,247 (68.0%) from OAS, 3,600 (32.0%)
  germline-reverted.
- Status (`claim-putative-negatives`), in the paper's own words: "while the biological context
  strongly supports the assumption of non-reactivity, these pairs remain putative negatives and have
  not been experimentally validated for lack of binding." Appendix D adds that neither argument for
  their non-reactivity is a measurement and that the authors claim no numerical false-negative rate.
- Sensitivity (`claim-label-noise-sensitivity`): the target-shuffling experiment, 300 triplets under
  five sampling seeds, 30,000 predictions, about 250 B200 GPU-hours; Protenix-v2 drops from 72.4% on
  valid pairs to 50.3% on invalid ones and Boltz-2 from 55.4% to 52.5%.

The same point appears as a `limitations` entry on the benchmark record, on the benchmark subset and
on all 66 evaluations, so nothing downstream can read an accuracy here as measured non-binding.

Related: `claim-sabdab-overlap` records that only 1,828 benchmark antibodies target antigens with
SAbDab structures and only 70 are within a cumulative CDR edit distance of 10, and
`claim-training-data-disclosure` records the Discussion's own statement that incomplete
training-data disclosure prevents fully excluding overlap. Excluding close SAbDab sequences is not
evidence of absence from training data, and no record says it is.

## Licence, and what it does not cover

Both Zenodo records declare CC BY 4.0 (`license.id` `cc-by-4.0`) for the dataset; the preprint is CC
BY 4.0 for the article. **Neither record nor the manuscript states any position on the patent rights
in the filings the records are extracted from.** That is recorded as the absence it is, in
`claim-dataset-licence-v1-0-1` and `claim-v1-1-licence` and in each dataset's `reuse_restrictions`:
the licence covers the compilation, and a licence to a compilation of patent-derived sequences is not
a licence to the antibodies the patents claim. Both Zenodo records advise verifying critical
sequences or affinities against the original patent documents, reachable through the `patent_id`
column, before downstream experimental validation; that advice is recorded too.

## What was extracted, and what was not

Extracted as results (78):

| Table or passage | Cells | Protocols |
| --- | --- | --- |
| Table 1, all 6 rows by 4 columns | 24 | Cohen's d ipTM, Cohen's d ipSAE, 50%-coverage accuracy, 1-in-50 top-1 |
| Table 7, all 6 rows by 6 columns | 36 | tie fraction plus the five coverage levels |
| Table 2, all 6 rows | 6 | epitope recovery |
| Table 8, the three summary rows (means as results, the two spreads as uncertainty and claims) | 6 results | 1-in-50 top-1 |
| Section 3.2.3, the two printed top-10 values | 2 | 1-in-50 top-10 |
| Section 3.3.1, consensus accuracy and coverage at two settings | 4 | consensus accuracy, consensus coverage |

Not extracted as results, with the reason (all also in `scope-audit.jsonl`):

- **Table 8's 162 per-construct cells.** Each construct is a different candidate pool, so they would
  need 27 antigen-construct subsets and 162 further evaluations. Out of scope for this batch; the
  summary rows and the per-engine spread claims are extracted instead. Retrievable from the same
  pinned artifact.
- **Table 6's 132 cells** (per-seed surviving pairs and percentages over two engines, three decoy
  subsets and two conditions). It measures the benchmark's own label noise, not model performance on
  the benchmark; kept as one claim with its headline means.
- **Tables 3, 4, 5 and 9**: a field list, the manual audit, the evidence tiers and the per-model
  compute breakdown. Kept as claims (`claim-extraction-pipeline`, `claim-manual-audit`,
  `claim-evidence-tiers`, `claim-compute-budget`).
- **Figure 5**: prints no numbers. Top-5 retrieval is unrecorded for every engine and top-10 only for
  the two engines the text names. The 36 error bars are figure-only; their definition is recorded as
  a claim.
- **Figures 3, 4, 7 to 16**: no printed numbers. The text's temporal endpoints (Protenix-v2 0.716 to
  0.689, largest pre-minus-post difference 1.8 points) are kept in `claim-temporal-analysis`, and the
  k of 5 and k of 6 consensus accuracies are "at least 90%" rather than printed values, so they are
  in `claim-consensus-high-stringency` rather than as results.
- **No POISK data file was downloaded.** The 234 MB and 124 MB tables, the 47-column schema file, the
  extractor and auditor prompts and the folding artifacts are unhashed; nothing in this batch rests
  on their contents. Nothing was recomputed from the released per-complex metrics.
- **Version 2 of the preprint** (posted 2026-11-14, inside the search window) was not read: the
  bioRxiv JATS feed serves front matter only for it and no PDF was fetched. Its abstract as served by
  the bioRxiv API is byte-identical to version 1's.

## How the values were extracted, and how to check them

`extract/build_batch.py` is the only thing that writes `batch.jsonl`. It asserts the sha256 of the
text layer, then for each table its single printed caption line, the order of its column headers
left to right, and each row label, before reading any cell. Table 8's body is additionally asserted
to hold exactly 27 construct rows. The six prose values are hard-coded with an assertion that the
sentence each comes from is present in the text layer. It also cross-checks the two printings of the
two twice-printed endpoints against each other. Nothing is read from a figure, by colour or from
pixels.

```sh
python3 data/omics/poisk-20261115/extract/build_batch.py <layout.txt> data/omics/poisk-20261115/batch.jsonl
npx tsx data/omics/poisk-20261115/extract/validate_batch.ts
gzip -dc data/omics/poisk-20261115/artifacts/biorxiv-v1-layout.txt.gz > /tmp/poisk-v1-layout.txt
npm run -s batch -- check-values data/omics/poisk-20261115 \
  poisk-20261115-source-manuscript-v1=/tmp/poisk-v1-layout.txt
```

Results at extraction time:

1. `validate_batch.ts`: 221 records pass the schema, attribute, vocabulary, description and relation
   checks. It loads `data/entities` for link targets and writes nothing.
2. `check-values`: 78 of 78 results found, 36 `in_cell` and 36 `in_row`, 6 `locator_not_parsed`. No
   `wrong_column`, no `not_in_row`, no `overclaimed_in_row`. The 36 `in_row` are the 30 Table 7
   coverage cells and the 6 Table 2 cells: the repository parser cannot name Table 7's columns
   (its "Coverage" group label and the `100% 75% 50% 25% 10%` line do not line up for it) and finds
   no parsable body for Table 2 (its header is split over two lines around the row-label column), so
   both fall back to the row. Every value in those rows is distinct, so no value could be taken from
   a neighbouring column without the row check catching it, but **column assignment for Tables 2 and
   7 still needs the reviewer's manual check**. The 6 `locator_not_parsed` are the prose values, whose
   locators name a section and a sentence.

## Questions for the reviewer

1. **Version 2.** A version 2 of the preprint was posted on 2026-11-14, one day inside the cutoff. The
   issue names version 1, and its abstract is byte-identical, but its tables were not checked because
   its full text is not retrievable from the bioRxiv feed. Re-pin the batch to version 2, or keep
   version 1 and record version 2 as a known later version?
2. **`paired-accuracy` as the metric concept.** The paper's "pairwise accuracy" is structurally the
   paired-comparison accuracy the concept describes (score the positive above its matched control),
   but the concept's definition is written for regulatory elements and their matched controls
   ("Defined by DART-Eval"). Accept `paired-accuracy` with the qualifier, widen the concept's
   definition, or fall back to `accuracy`?
3. **No metric concept for a standalone standard deviation.** Table 8's between-target standard
   deviation is a printed cell per engine with no home as a result: it is not the result's
   `uncertainty` (that is the across-seed spread Figure 5 uses) and no metric concept fits. It is
   kept as six claims. Should a `standard-deviation` metric concept be added instead, so the printed
   cells become results?
4. **Two printings of one value.** The 50%-coverage accuracy and the 1-in-50 top-1 figure are each
   recorded twice, from Table 1 and from Table 7 or 8, on the same evaluation, with a
   `rounding_note` on the Table 1 record. Is keeping both printings right, or should the coarser
   printing be dropped? Note the side effect: the six Table 1 top-1 results carry `unit: fraction`
   while their protocol declares `unit: percent`, because Table 1 prints 0.29 where Table 8 prints
   28.9. That is deliberate (it stops the two printings being pooled) but it does leave results on
   one protocol in two units.
5. **Model lineage links.** The three new model records carry no `variant_of` or `family` edge.
   AlphaFold-Multimer is an AlphaFold 2 extension and OpenFold3 shares a name and a project with
   `discovery-model-openfold`, but this source asserts neither relationship, and the contract wants
   those edges backed by a source-checked association claim. Leave them unlinked?
6. **`same_data_as` rather than `supersedes` between the dataset versions.** Version 1.1 "corrects
   errors found in version 1.0.1", which reads like superseding, but version 1.0.1 is still the
   release the published folding predictions were computed against. Is `same_data_as` plus the version
   claims the right shape?
7. **Table 8's per-construct cells and Table 6.** Both were excluded to keep the batch bounded, with
   reasons recorded. Should either be extracted?
8. **Publication status.** The explorer page states the paper was accepted at NeurIPS 2026, while the
   pinned artifact is a preprint carrying the "not certified by peer review" banner. The source record
   keeps `publication_status: preprint` and the acceptance is a claim
   (`claim-publication-status`). Right call?
9. **The ipSAE tool is not pinned.** The paper scores with "a modified implementation of the ipSAE
   tool" at `https://github.com/DunbrackLab/IPSAE` and names no commit, so no snapshot would describe
   what ran. Nothing was retrieved; the definition is a claim from the paper's wording. Accept?
10. **Column assignment for Tables 2 and 7.** `check-values` could not name their columns, so 36
    results rest on a row-level machine check plus the extractor's own column-order assertions. These
    are the cells to sample by hand.
