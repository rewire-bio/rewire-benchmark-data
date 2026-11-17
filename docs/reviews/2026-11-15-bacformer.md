# Bacformer and BacBench, independent review

2026-11-15. Batch `data/omics/bacformer-20261115/`, issue
[#245](https://github.com/rewire-bio/rewire-benchmark-data/issues/245). Reviewed by a Claude
(Opus 5) agent that did not extract the batch, against the extraction frozen at `batch.jsonl`
SHA-256 `776ec11726d7f9f42ec845745341abe0bbfb3006c74b9851e00ca8910995a1ac`, 490 records. Not human
scientific review. Nothing was reproduced: transcription was checked against the pinned sources,
which is not reproduction.

Receipt: `data/omics/bacformer-20261115/review.json`. Mismatch report:
`data/omics/bacformer-20261115/value-check.tsv`. Reviewer scripts and the negative-control log:
`data/omics/bacformer-20261115/review/`.

Two corrections were applied to `batch.jsonl` before the batch was stored. Both are described
below under [Corrections](#corrections). Everything else stands as extracted.

## Sources and hashes

Eleven of the thirteen artifacts were downloaded again at review time. Every one hashed to exactly
the value its source record records, and every one is byte-identical to the copy kept in
`artifacts/`.

| Record | SHA-256 | Refetched |
| --- | --- | --- |
| `source-bacformer-readme` | `6e4fdabbd05c93ff63b0eb583ce6a9309eaa13998087cc32ddeaa6928025b235` | matches |
| `source-bacbench-readme` | `c9d28efef5b4cc30adbcc9de224c350100f5aa2a15a025beaf10dcdeb86cd93e` | matches |
| `source-bacformer-licence`, `source-bacbench-licence` | `d7fe40bfc2a639daa18e4caf57fab7545ece94bd38fb181c1f5b780d3b8cfa01` | matches |
| seven Hugging Face model cards | as recorded in the batch | all match |
| `source-preprint-v3` | `d86de3315063e038ec8d5bed60b7b1a916c137ee60973e55d9d5c82f078d8dfd` | does not reproduce, by design |
| `source-preprint-v2` | `a842db88eabf2b83d4e0de861e8a6767a01ee3f72c62b6a177494ffafd6d9703` | does not reproduce |

### The preprint hash note checks out, and the text layer is exact

The extractor's account of the version 3 PDF is right, and this review reproduced it independently.
Two downloads minutes apart returned the same 21,613,661 bytes but different files:
`0287e3b6c1272cbe9f02a36b3b2abd0d26fddf3f214ad11aff9107298494cc70` and
`47fc16b387904db0a4ad935d3fd8e2cc375af497fac4dd899c833468fd267382`. Neither matches the recorded
hash, nor the second hash the extractor saw. The cause is visible in the file: the PDF's `Producer`
is `iLovePDF` and its `CreationDate` is the moment of the download, so bioRxiv regenerates the
container per request.

The text layer is stable. `pdftotext -layout` over both of my downloads produced byte-identical
output, SHA-256 `86636e89b167d7304b3a83ee7f159cad0a9bdbe97019588ce836087b8fe3b0b2`, which is exactly
the hash recorded in `hash_scope`, and `artifacts/biorxiv-665723v3-text-layer.txt.gz` (itself
`0afdefd78a410d036d1c4f17e33bdf481e8d76241ee02f4c84c7c4be91ee72aa`, the recorded `archive_sha256`)
decompresses to those same bytes. The archive is therefore provably derived from a current
retrieval of the pinned URL, not merely asserted to be.

No hash was changed. The version 3 source record now carries `review_artifact` and
`review_artifact_matches_original_artifact_sha256` false, and a limitation naming the text layer as
the stable identity, so a later reader is not left to rediscover this.

Version 2 is weaker and should be read that way. Its container also failed to reproduce
(`af77c2be437b151b5e464f2f5078f6b97b95a29c2913affefc566337eecfbad4`), and unlike version 3 the
record pins nothing below the container, so the artifact is unverifiable at any layer. Nothing in
the batch rests on it.

## How the values were compared

`npm run -s batch -- check-values`, run against a text layer regenerated from a fresh download,
reproduced the extractor's figures exactly: 186 of 186 found, 36 `in_cell`, 150 `in_row`, no
`wrong_column`, no `overclaimed_in_row`, nothing missing. The `value-check.tsv` it wrote was
byte-identical to the extractor's own.

That check only proves each value is somewhere in the row its locator names, so for the 150
`in_row` results the column assignment was entirely this review's to establish. All 186 cells were
re-read by `review/recheck_cells.py`, written for this pass. It uses neither
`extract/parse_tables.py` nor `extract/check_tables.py`, and it does not read the
`pdftotext -layout` text layer that both of those read. It takes the word bounding boxes that
`pdftotext -bbox-layout` emits for a freshly downloaded version 3 PDF, groups words into printed
lines by their y coordinate, derives each table's column boundaries from the x extent of that
table's own printed header words, and assigns every number to a column by where it sits on the page.
A value printed under one header therefore cannot be read as a value of another.

Besides the values it asserts the structure: the printed row order of each table, that every column
of every row is filled, that each cell holds exactly a mean and a spread, that each cell prints its
own plus-minus sign in its own column, and, for Tables S13 and S18, that the group header sits
geometrically over the two columns this review names after it (so "Zero-shot AUPRC" and "Binary
AUPRC" are established from the page, not from column order). The plus-minus glyphs sit on their
own baseline in this PDF and are matched back to the row above them.

All 186 cells agreed, on the printed value, the mean, the spread, the spread's printed string and
the spread's recorded source column, with zero disagreements, and the six tables print no cell the
batch leaves unrecorded.

### Negative controls

A checker that passes says nothing until it is known to fail. `review/negative_controls.py` writes
three mutated copies of `batch.jsonl`, each with one planted error, and requires all three to be
rejected and the unmutated batch to be accepted. The log is
`data/omics/bacformer-20261115/review/negative-controls.txt`.

| Control | Result |
| --- | --- |
| Two cells of one Table S13 row exchange their values, locators unchanged | rejected, 2 mismatches |
| One Table S18 cell takes the value printed in the column beside it | rejected, 1 mismatch |
| Every Table S18 locator names the column one to its right | rejected, 48 mismatches |
| Unmutated batch | accepted |

### Manual sample

47 cells were read by eye against the printed table bodies: 24 drawn over all 186 with
`random.sample` at seed 20261115, all 18 cells of Table S12, and the eight Evo and Evo-2 cells of
Tables S1 and S14. The last group is deliberate: the twelve systems appear in two different printed
orders, with Evo and Evo-2 second and third in Tables S1 and S14 but fifth and sixth in S13, S16 and
S18, which is where a row-order mistake would land. The sample spans every table and every column of
every table. All 47 matched, column assignment included.

## Corrections

### 1. The unit concept was wrong on 168 results

The extractor recorded `unit: percent` with `unit_detail: "Printed on a 0 to 100 scale"` for every
result of Tables S1, S13, S14, S16 and S18, that is for AUROC, AUPRC, R squared and the Pearson
correlation. `data/vocab/unit.ttl` rules the other way, in the scope note of `unitless`:

> A unitless statistic printed x100 (MCC, R2, Spearman, AUC) stays unitless with unit_detail
> 'printed x100'; percent would imply a proportion.

and in the scope note of `fraction`: "Normalised scores such as TM-score, NDCG and AUROC are
unitless." The stored catalogue follows that rule: 4,403 AUROC results are `unitless` against 9
`percent`, and 1,847 AUPRC against 177. Since comparisons require the same unit, leaving these as
`percent` would have put 168 results in a class of their own and stopped them comparing with the
AUROC and AUPRC values already in the store.

`review/apply_review.py` set `unit` to `unitless` and `unit_detail` to `printed x100` on those 168
results and on their `uncertainty` objects. No printed value, numeric value or spread was touched.

A second pass caught what the first missed. The 14 protocols that govern those results carried
`unit: percent` too, and changing only the results would have left a protocol declaring one unit
over results declaring another. `review/fix_protocol_units.py` applied the same change to them, in
`data/entities/protocols.jsonl` and in `batch.jsonl` together, and it was recorded with
`npm run records -- change docs/reviews/2026-11-15-bacformer.md data/omics/bacformer-20261115 <14
protocol ids>` because the batch was already stored by then. The three strain-clustering protocols
are printed on a 0 to 1 scale and were already `unitless`. The store's own convention agrees: 77
AUROC and AUPRC protocols are `unitless` against 19 that are not.
Table S18's caption does say "Performance (percent, higher is better)", but that describes the
printed scale; it does not make an AUROC a proportion of items. The 18 Table S12 results were
already `unitless` and are unchanged. `notes.md` decision 8 is superseded by this.

### 2. Version 2 does not print different values for the examples given

The claim `bacformer-20261115-claim-preprint-version-differences`, the version 2 source description
and one of the version 3 source limitations all stated that version 2 "prints different values for
the same analyses", citing two examples: almost 95% balanced accuracy for genus-level retrieval, and
0.81 plus or minus 0.07 median essentiality AUROC.

Both examples are identical in the two versions. Rendered at 200 dpi, version 2 page 5 reads "with
the method achieving almost 95% balanced accuracy across diverse genera" and page 8 reads
"achieving 0.81 ± 0.07 median AUROC across diverse genomes". Version 3 prints the same figures at
paragraphs 141 and 222.

The error came from the mis-encoded text layer, and the renders confirm that diagnosis exactly: in
version 2's text layer the rendered "0.81 ± 0.07" appears as `+.)! ± +.+(` and the rendered "95%"
as `*'%`. The extractor was right that nothing can be transcribed from that text layer, and then
drew a conclusion from it anyway.

What the sources support is kept. Version 2 nowhere mentions Bacformer Large: zero occurrences of
"Bacformer Large" or "Bacformer-L" in its text layer, where letters render correctly. The claim now
says that, says the two versions are separate reports whose numbers must not be pooled, and records
that where the two were compared the figures agreed. Its limitation now states that no systematic
numeric comparison was made, because only two pages were rendered.

## Rulings on the extractor's questions

### 1. The parameter counts: leave the claims as they stand

Nine claims, one per printed figure, no value on the model records. That is right, and for the base
model it is not even a close call: the `model` kind declares no parameter-count attribute in
`shared/omics/attribute-registry.ts`, and no model record in the store carries one, so there is no
field in which to pick a winner. The `configuration` kind does carry `parameters`, and the
configurations follow the source correctly: Bacformer Large's carry 332M, which Tables S9 and S11
agree on, and base Bacformer's carry no value with `missing_metadata.parameters` set to
`conflicting`, because the same source prints two figures.

Two observations that were not available to the extractor, both arithmetic on repository metadata
rather than printed statements, so no record rests on either.

The base disagreement is probably two roundings of one number. Hugging Face serves a weight total of
50,852,241 for every base checkpoint. The pinned `config.json` of `bacformer-masked-MAG` gives
`protein_clusters_vocab_size` 50000 and `hidden_size` 480, so the protein-family head alone is
50,000 x 480 = 24,000,000, leaving a trunk of about 26.85M. That rounds to 27M and truncates to 26M.
Neither printed figure is an error, which is the strongest reason not to mark one.

The Large figure of 332M is not the copy of ESM-C's row that the extractor suspected. The pinned
`bacformer-large-masked-MAG` config gives 30 layers at `hidden_size` 960; a transformer layer with a
four-fold feed-forward is 12d² parameters, so 30 x 12 x 960 x 960 = 331,776,000, which is 332M. The
332M that Table S9 also gives ESM-C is the same arithmetic on a model of the same shape, not a
transcription accident. The 300M on the README and the model cards is the nominal name of the ESM-C
base model carried over. The served weight total for both large checkpoints, 431,765,841, is
accounted for by neither figure once the 50,001-cluster head is subtracted, so the Large count stays
genuinely open.

### 2. No evidence concern for the BacBench README's "Bacformer Large, 27M"

The test for an evidence concern in `docs/collection.md` is a problem that should block comparison.
Nothing in this batch rests on that cell. It is recorded as one printed figure among nine, with a
`limitations` entry saying the other sources contradict it, and a concern scoped to the claim would
withhold the record of the disagreement itself, which is the opposite of what the concern mechanism
is for.

It is also less mysterious than it looks. The BacBench Params column disagrees with preprint Table
S9 for several models (ProkBERT 27M against 26M, Nucleotide Transformer 250M against 235M, ProtBert
420M against 412M), so the column reads as nominal model sizes rather than measured counts, and the
Bacformer Large row repeats the Bacformer row's 27M while changing the dimension to 960. That
observation is now in the claim's review note.

### 3. Table S16's seed conflict: result-level warning, not a concern

The conflict is real and both halves were read in the source. The caption:

> Table S16. Overall phenotypic traits prediction performance across all phenotypes. Values are
> mean ± standard deviation across 5 seeds.

The Methods, paragraph 766:

> Because many traits are rare, we repeated this procedure across three independent runs with
> different data splits to improve robustness and obtain more stable performance estimates.

The source does not reconcile them, and they may not even denote the same quantity: the Methods
describe repeats of the genus-level split, the caption describes seeds, and the benchmarking section
separately mentions a learning-rate sweep "across seeds and phenotypes". The disagreement is about
what the spread is taken over, not about the means, and the `uncertainty` objects correctly assert no
replicate count, give both readings in `scope`, and carry the conflict in `source_warnings` on all
24 results.

An evidence concern scoped to the two phenotypic-trait protocols would withhold all 24 results from
every comparison and use-case judgement over an unresolved footnote about a standard deviation. That
is disproportionate. Keep the warning.

For contrast, the antibiotic-resistance Methods say plainly "We repeat this procedure across three
random splits", and Table S18's caption says the spread is across antibiotics, so that table has no
such conflict.

### 4. Configuration granularity: keep two adaptations per system

Twenty-four configurations, one zero-shot and one linear-probe per system, plus two for clustering.
The source states the head and its schedule per task, and the batch puts those on the protocols,
where `metric_qualifier` already carries the adaptation for each table. Splitting into one
configuration per system and task would duplicate the checkpoint identity across records that differ
only in what the protocol already says. No change.

### 5. The Table S12 checkpoint stays unassigned

Leave it at family level with `missing_metadata.checkpoint` set to `conflicting`. The two sides are
both explicit and neither is about this table specifically.

Preprint Methods, paragraph 331, under "General modelling details":

> All checkpoints used were downloaded directly from HuggingFace and are specified in Table S9.

and Table S9 names `macwiatrak/bacformer-masked-complete-genomes` and
`macwiatrak/bacformer-large-masked-complete-genomes`.

The BacBench README, footnote on the Bacformer and Bacformer Large rows of its "Benchmarked models"
table:

> Historical strain clustering runs used the MAG version of the Bacformer model
> (bacformer-masked-MAG and bacformer-large-masked-MAG) because the inputs are
> metagenome-assembled genomes (MAGs), rather than complete genomes.

The preprint's own Strain clustering section names no checkpoint at all, and its data are 6,071 MAGs
sampled from MGnify. `docs/collection.md` settles it: "An unidentified model version stays at family
level and is not assigned to a specific checkpoint." Assigning on the strength of a study-wide
sentence, against a task-specific footnote that gives a reason, would be a guess. The extractor's
handling stands.

### 6. Table S15 stays out

Protein function prediction is not among BacBench's tasks. The BacBench README lists five active
tasks and one deprecated one, and Table S11's GPU-hour columns are exactly those five active tasks.
The batch registers BacBench, so the table falls outside it. The gap is recorded in `notes.md` and in
the `result_coverage` claim, which names Table S15 and says it was not extracted. Nothing stops a
later batch adding it against the Bacformer model records instead.

### 7. The clustering protocols keep the limitation, with no evidence concern

The selection is as described. Methods, paragraphs 398 to 402:

> we ran Leiden clustering over a parameter grid, varying the resolution in [0.1, 0.25, 0.5, 1.0]
> and the number of neighbours in [5, 10, 15], and evaluated all pairwise combinations. We then
> retained the combination of resolution and number of neighbours that maximised the mean of the
> three metrics described above (ARI, NMI and ASW) at the species level.

So every value in Table S12 is a best-of-grid chosen on the metrics the table reports, with no
held-out selection. That inflates all three metrics. But it is applied identically to all six
systems, so it biases the level of every value rather than their ranking against each other, and it
is a property of the protocol, which all three clustering protocols already record as their first
limitation, backed by the `selection_bias` claim quoting the Methods. A concern would withhold the
whole table from comparison; the limitation tells a reader exactly what the numbers are. Keep the
limitation.

### 8. `discovery-model-nucleotide-transformer` is the right family

The benchmarked checkpoint is `nucleotide-transformer-v2-250m-multi-species`, printed in Table S9.
`catalog-model-nt-v2` is a family record whose `version` field says "50M multi-species", which is a
different checkpoint; attaching a 250M configuration to it would contradict the record's own version.
`discovery-model-nucleotide-transformer` is a family record with no version, described as a family of
DNA encoders. The configuration carries the exact checkpoint either way. The extractor's choice
stands.

Worth a separate look, outside this batch: `catalog-model-nt-v2` is marked `entity_level` family but
pins a specific size in `version`, which is what forced the choice. That is a record-level
inconsistency in the store, not a problem with this batch.

## Other checks

- Every `uncertainty` denominator is the source's own. Operon n = 5 comes from the Methods
  ("We report performance averaged across all five sequenced strains"), not from the caption, which
  states no scope. The antibiotic counts come from the Methods ("This resulted in 37 unique
  antibiotics" for the binary setting, 56 for regression), and Table S17 prints exactly 37 drug rows.
  Table S12's bootstrap method and its 10 resamples over 80% of the data are the caption's own words.
- Every claim was read against its pinned artifact at its recorded locator. The training-corpus
  figures (1.3M MAGs, 3 billion proteins, 225 million contigs, 25,000 species, 70 environments), the
  pretraining objective (50,000 protein-family clusters, 15% masked, 87.5/12.5), the context limits
  (6,000 proteins, more than 98% of genomes, 1,024 amino acids), the 2025-05-15 Bacformer Large bug
  notice, the README checkpoint-table conflict, the ESM++ licence note and the Apache 2.0 availability
  statement all read as recorded.
- Access was rechecked rather than taken from `notes.md`. At 2026-11-15T23:41:36Z,
  `bacformer-causal-protein-family-modeling-complete-genomes` and
  `bacformer-for-essential-genes-prediction` returned HTTP 401 from both the web page and the model
  API, and `bacformer-for-ppi-prediction` returned 200. HTTP 401 still does not distinguish a private
  repository from one that does not exist, and the records say so.
- `silhouette-score` is the right concept for Average Silhouette Width. Its definition is worded for
  single-cell embeddings, but it is the same statistic, and adding a concept that respells an existing
  one is forbidden. The printed name is kept in `metric_qualifier`. No vocabulary concept was missing
  and `data/vocab` is untouched.
- Metric directions are all `higher`, which the captions support ("higher is better" in S18 and S15,
  best value bolded elsewhere), and every metric concept matches its printed column header.
- No discrepancy involves this batch: none of its IDs was in the store before this review, so no
  `discrepancies.json` could list them. The knowledge-graph build after the add may raise new leads.

## Gaps that remain

The twelve gaps in `notes.md` all stand, with two amendments: gap 5 now reads as a conflict about
what the Table S16 spread covers rather than a simple seed-count discrepancy, and the version 2
comparison recorded under "Decisions" is narrower than the extractor stated (see
[Corrections](#corrections)). Two further gaps from this review:

1. The version 2 PDF is unverifiable at any layer, since its container hash does not reproduce and
   the record pins nothing below it. Only two of its pages were rendered, so whether any other figure
   differs between the versions is unknown.
2. Bacformer Large's parameter count is not reconciled by any accounting available here. 332M matches
   the trunk arithmetic, 300M is the base model's nominal name, and the served weight total of
   431,765,841 matches neither once the output head is subtracted.
