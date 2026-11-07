# HyPLM-Flash technical report, independent review

2026-11-06. Batch `data/omics/hyplm-flash-20261106/`, issue
[#233](https://github.com/rewire-bio/rewire-benchmark-data/issues/233). Reviewed by a Claude
research agent that did not extract the batch, against the extraction frozen at commit
`b4c9fbf3ce7851ff4fd72fd5ac03f3ee49bca67e`. Not human scientific review. Nothing was reproduced:
transcription was checked against the pinned source, which is not reproduction.

Receipt: `data/omics/hyplm-flash-20261106/review.json`. Mismatch report:
`data/omics/hyplm-flash-20261106/value-check.tsv`. Edits:
`data/omics/hyplm-flash-20261106/review/apply-review.py`.

## Sources

All six artifacts were re-downloaded at commit `0dcc533cc9f8f76c90ecbfe944df816b6672328a`, each from
the `artifact_url` its own source record gives, and every hash matched.

| Record | SHA-256 |
| --- | --- |
| `hyplm-flash-20261106-source-report` | `d81d88a415a91c2b00d8e97513a90c03ccffd857ec75033fa7de77227dea1710` |
| `hyplm-flash-20261106-source-model-readme` | `db6ab273ef190a40199a5a8d17c474a2809fd9cedac6013c45ec7c06642542a3` |
| `hyplm-flash-20261106-source-licence` | `a0a9dc95e81d7a1374275195bccb72442e0126be826919b13ff67f52eb64a031` |
| `hyplm-flash-20261106-source-engine-model` | `8bba607aaac45d7365ac011644fcee65157a1f29f306c646aaa29d4258fd4255` |
| `hyplm-flash-20261106-source-engine-packing` | `3eb213e8483bb09551b253aeea9f4ff5a0c5b2e7cd53d985f226f1cbf52c1828` |
| `hyplm-flash-20261106-source-engine-graphs` | `29df2c0d012c6e2f03b2618efb1cc76e070097b531494e5553f548b0bdf3f1bc` |

A note on how that was done, because it nearly produced a false finding. My first fetch of the three
engine files reconstructed their paths from `notes.md`, which gives them as `hyplm/engine/model.py`,
and all three came back with one identical hash. That hash is the SHA-256 of the string
`404: Not Found`. The records' own `artifact_url` has the files one level deeper, under
`AI4Science/hyplm_flash/hyplm/engine/`, and from there all three match. The lesson is the one
`decisions.md` already records about hunk-level versus file-level claims: re-retrieve from the URL
the record states, not from a path reconstructed out of prose, or you will check something else and
believe you have checked the source.

The report's two dates were both read from the pinned bytes: page 1 prints `2026-10-12`, and
`CreationDate` and `ModDate` are both `D:20261029232847+08'00'` (pdfTeX-1.40.19, 13 pages). That is
the shape ruling 8 covers, and the batch handles it as the ruling says: printed date in `version`,
build stamp in `version_note`, no concern, and the note states that no earlier PDF exists at the
pinned commit so whether the rebuild changed content was not checked.

## How the values were compared

`npm run -s batch -- check-values` reproduced the extractor's figures exactly: 267 `in_cell`, 202
`in_row`, 15 `locator_not_parsed`, with no `not_in_row`, `wrong_column` or `overclaimed_in_row`.

The 469 recorded cells of Tables 3, 5, 6 and 7 were re-read by `review/check-cells.py`, written for
this pass, which takes each table's column order from its printed header line and splits every body
row by printed cell without using `extract/parse.py`. Every printed value and every column matched.
The two arithmetic constraints were re-derived rather than taken from the extractor's checker: each
of the 20 Table 3 perplexities against exp of its NLL over the NLL's own rounding interval, and each
of the 14 Table 5 averages against the mean of its five categories. Both hold, including the two the
extractor had to widen: `exp(1.720) = 5.5845` against a printed `5.59` is consistent once the NLL's
own rounding is counted, since `exp(1.7205) = 5.5873`, and E1-300M's categories mean to 0.4164
against a printed 0.417. `extract/check_cells.py` was rerun on the refetched PDF and reproduces
`cell-check.tsv`.

Column assignment in Tables 6 and 7 is anchored outside those tables, which matters because they
carry 404 of the 484 results. Table 3's ten NLL rows reappear in the two likelihood rows; Figure 3a's
and Table 5's ProteinGym values reappear in the ProteinGym row; and Section 4.1's four paired
differences reconcile with that row, 0.409 minus 0.415, 0.406, 0.410 and 0.420 giving exactly the
printed -0.006, +0.003, -0.001 and -0.011. Unlike HyInv's Figure 15, nothing here rests on a rotated
header.

The 15 locators `check-values` cannot parse were read by hand: four Figure 3a bar labels, where each
label and its value share one line of the text layer, and eleven prose values in Sections 3, 4.1 and
4.2. Manual sample: 25 of the 484 drawn with `random.sample` and seed 20261106 over the IDs in sorted
order, each read by eye with its row and column; 19 from Table 6, 5 from Table 7 and 1 from Table 3,
all matching, column assignment included.

## The in_row passes are weaker here than the tooling note says

The coordinator's standing note is that `check-values` can pass a wrong cell when a figure's bar
label printing the same number sits inside its match window. On this source the same failure has a
larger cause, and it is worth recording in its general form.

Tables 6 and 7 are a part-1 and part-2 split of one table, on adjacent pages, with the same 32 task
row labels. The checker's window is 150 lines either side of a caption, so it spans both. Measured
over the 469 parseable locators: 188 of the 202 `in_row` results sit in a window where their row
label occurs on more than one line, and for 16 of them the printed value appears in more than one
candidate row, so a row-level pass cannot say which of the two tables satisfied it. The clearest case
is the task `AAV low-vs-high`, whose Table 6 row prints `0.296` twice and whose Table 7 row prints
`0.296` once.

None of those values is wrong; the column-keyed parse confirmed all 469. What is established is that
a row-level pass carries little information on a split table, and the `overclaimed_in_row` detector
does not catch it, because both rows really do print the value, so the count of claims never exceeds
the count of printings. The general statement for `decisions.md` is wider than figures: **any two
tables within the checker's window that share row labels make an `in_row` pass ambiguous, and a
part-1 and part-2 split of one table is the normal way that happens.** The 267 `in_cell` results are
unaffected, since the checker placed those in the named column.

## Rulings on the extractor's questions

### 1. Reusing `vep-lit-20261014-data-proteingym-dms-substitutions-144fe22`

Right, and the evidence for it is stronger than the extractor claimed. The stored record is a
`dataset_subset` carrying `assay_count: 217` and
`version: 144fe22b07dfaeec2b366f2346203a9838a55b4c (README: latest version v1.3)`, with
`source_locator: reference_files/DMS_substitutions.csv (217 data rows)`. Table 4 of this report
prints `ProteinGym substitutions ... 217 assays ... ProteinGym v1.3`, so assay set, count and version
all match the stored record.

The extractor recorded that the report "does not name the commit of its own assay files". That is
true as far as it goes, but Table 5's caption does print a commit: "other rows are published
leaderboard values (ProteinGym repository, commit 144fe22)". It attributes the commit to the
leaderboard rows the authors quote rather than to their own assay files, so it is not proof that
their files came from the same tree, but it is the same commit the stored record is pinned to and it
belongs on the record rather than only in `notes.md`.

One correction made. All 484 evaluations carried
`split: "Test split as printed in Table 4"` and
`dataset_version: "As used in the HyPLM technical report (2026-10-12)"`. For the 56 ProteinGym
evaluations the first is wrong: Table 4 prints `217 assays` in place of split sizes for this task,
because a zero-shot assay benchmark has no train, validation or test split. `docs/collection.md`
requires a comparison field the source does not state to be null, which blocks automatic comparison
deliberately; a uniform string that is inaccurate for 56 of 484 is neither stated nor null. Those 56
now say what Table 4 prints, and their `dataset_version` carries v1.3, the 217 assays and the Table 5
caption's commit, which is the identity the reuse rests on.

### 2. Reusing the seven FLIP splits when the authors carve their own validation sets

Right. What a record for a test metric identifies is the test split, and the test splits are FLIP's;
Table 4 attributes each to FLIP or FLIP2 by name. The authors' validation data affect layer and
regularisation selection, which `docs/collection.md` puts in the protocol, not in the dataset
identity: "A protocol fixes the split, inputs and metric." Appendix A states the selection rule, "we
evaluate six layers ... and select the layer and the regularization strength on the validation split,
or by 5-fold cross-validation on the training split where a task has none (DGEB EC)", and the batch's
protocols carry it.

Two checks worth recording. The store's AAV split records are named `1-vs-rest`, `2-vs-rest` and
`7-vs-rest` where FLIP calls the same splits `one_vs_many`, `two_vs_many` and `seven_vs_many`, so
reusing `flip-dataset-flip-aav-2-vs-rest-split` for this report's `AAV two-vs-many` looked like a
mismatch and is not: the store renders FLIP's `vs_many` as `vs-rest` for AAV throughout. And Appendix
A singles out exactly the three splits where the self-made validation data cause a problem, GB1
two-vs-rest, GB1 three-vs-rest and the FLIP2 cross-protein hydrolase split, saying their "validation
data come from the training distribution while the test sets are strongly shifted, so probe selection
on them is dominated by noise, and numerically equivalent runs of the same model differ by up to
0.2". The batch scopes an evidence concern to those three protocols, which is the right response and
the right scope.

### 3. `log-loss` for masked-residue NLL and `perplexity` for its exponential

`log-loss` is right. Its definition is "Mean negative log-likelihood of the true labels under the
predicted class probabilities (binary or categorical cross-entropy)", and a masked-residue NLL is
exactly categorical cross-entropy over the true residue at each masked position.

`perplexity` is the right concept for the quantity and the wrong definition for this use, and the
extractor was right to flag it. The scheme defines it as "Exponential of the mean per-token negative
log-likelihood of generated sequences under a reference language model". Here the sequences are
held-out natural proteins, not generated, and the model being evaluated is the model under test, not
a reference scorer. The quantity is identical, exp of the mean per-token NLL, which is why the
PPL-against-exp(NLL) check holds to the last digit on all 20 pairs.

I did not change it. The definition is shared with 19 existing results outside this batch, and ruling
10's principle, that a concept must not encode one source's framing, argues for generalising it
rather than for leaving this batch's 20 results under a definition that does not describe them. The
wording I would propose is "Exponential of the mean per-token negative log-likelihood that a model
assigns to a set of sequences. Whether the sequences are held out or generated, and which model
scores them, belong in the metric qualifier." That is a change to a shared concept used by other
batches, so it is for the owner, not for this review.

### 4. `claim_scope` for the ProteinGym tie

`claim_scope` alone is the wrong home, and the coordinator's reading is confirmed by the code as well
as the text. Three things decide it.

`claim_scope` is declared for a `result`, so it validates, but exactly one result in the whole store
uses it, and that use is a terse endpoint note, "desired-state composition endpoint only". Nothing in
`shared/` or the website reads it: its established meaning comes from
`shared/omics/benchmark-research.ts`, where it is a field of a benchmark-research audit, and from the
two research scripts that populate it at benchmark level. So a reader of a result never meets it and
no comparison path acts on it.

Meanwhile all 17 ProteinGym zero-shot results share one `metric_qualifier`, and comparisons key on
metric, qualifier, unit and direction, so the machinery will happily rank 0.420 above 0.415 above
0.409 across a set that Section 4.1 says is one statistical tie. The protocol those results hang
from carried a single limitation, about BF16 against INT8, and said nothing about the tie.

So the tie now sits in the `proteingym-zero-shot` protocol's `limitations`, quoting Section 4.1 with
all four printed differences and their intervals, naming the eight values that sit inside the tie and
pointing at the four paired-difference results that establish it. `claim_scope` stays on the 12
results that carry it; it costs nothing and may become readable later. This is the same lesson as
HyInv's ruling 3: a caveat belongs where a reader of a result meets it.

I did not put the tie in `metric_qualifier`. Adding it to the eight tied results and not to the other
nine would make the tied set comparable among themselves and incomparable with ProtBERT at 0.343,
which is precisely backwards: the tie is the thing that should not be read as a ranking, while the
gap to ProtBERT is real.

### 5. The throughput result

Defensible, and the condition the coordinator attached is met. The HyInv precedent stands: a measured
speed on a stated workload is a result. The protocol states hardware and workload in the qualifier,
"Residues embedded per second on one NVIDIA H20 for 2,048 held-out proteins (639,806 residues) in
length-sorted batches of at most 16,384 tokens", and carries three limitations: one GPU model and one
workload with HyPLM-Flash optimised against reference implementations; the INT8 threshold, so that a
workload of short batches would not reach this rate; and that only HyPLM-Flash's figure is printed
while baselines appear as unlabelled Figure 1a points and two ranges. An uncomparable number cannot
be silently compared here, because there is nothing recorded to compare it with and the protocol says
why.

The batch also stores, as claims, the three numbers most easily confused with it: the README's
rounded "about 130,000", the BF16 mode's 90,000, and the 1.9-to-2.7-times and 48,000-to-69,000
ranges. That is ruling 12 applied without being asked.

### 6. Figure 1b's sixteen won and lost claims

Keep them. Ruling 12 is the deciding text: numbers most likely to be confused with a headline
comparison must be stored, not omitted. "Won 20 of 35" is exactly the sentence an article draft
reaches for, and the way to stop it being repeated uncritically is to store it with the arithmetic
attached, not to leave it only in the source. They are claims, so they support no comparison, and
dropping them would also delete the evidence of the inconsistency.

But the caveat was on two of the sixteen. Only the ESM-2 650M pair recorded that its row sums to 34
against an axis reading "of 35"; the other fourteen asserted "21 of 35 task splits" with nothing to
say that 35 is undefined against the report's 32 tasks. A reader of the DPLM-650M claim needs that as
much as a reader of the ESM-2 650M one. All sixteen now carry it, including that Appendix A leaves
three regression splits out of Figure 1 altogether.

I agree with the extractor's reversal on the evidence concern, for the reason it gave and the one
ruling 4 gives: scoping a concern to the ESM-2 650M configuration would withhold all 32 of that
model's valid task results over a figure none of them rests on.

## Vocabulary

Both concepts earn their place and neither respells an existing one.

`spearman-correlation-difference` is needed for the same reason `sctm-difference` was in the HyInv
batch: a paired difference computed on the same assays with identical resamples is not the difference
of two separately reported correlations, and its definition says so. It carries
`skos:broader :spearman-correlation` and direction `higher`.

`mean-average-precision-at-5` is not a respelling of `average-precision`: it adds a rank cutoff and
the mean over queries, and the scheme already holds sibling cutoff concepts `precision-at-10`,
`precision-at-100` and `precision-at-l-5`. Its definition is general and keeps the retrieval set, the
relevance rule and the ranking score in the qualifier, which is ruling 10 applied correctly. One
change made: it had no `skos:broader`, while the scheme relates every cutoff and averaging variant to
its parent (`precision-at-10` to `precision`, `macro-average-precision` to `average-precision`). It
now carries `skos:broader :average-precision`. Only that concept's own block was edited, matched by
name and asserted to hold exactly one definition, per the shared-vocabulary rule.

Neither carries an external match. STATO is a statistics ontology, QUDT is units and EDAM covers
operations, data and formats rather than evaluation measures; none has a term for MAP at a rank
cutoff or for a paired correlation difference.

## Evidence concerns

All three are scoped with `applies_to`, as ruling 4 requires, and each matches the text I read:

- the recent-PDB panel described two ways, Section 4.3 and the Table 3 caption giving chains released
  after 2 September 2026 while Table 4 gives entries released 9 September to 7 October, scoped to
  that dataset;
- xTrimoPGLM's embedding results, which Appendix A's "Deviations" paragraph leaves in place while
  reporting an adapter incompatibility the authors did not test, scoped to that configuration;
- the three regression splits Appendix A says differ by up to 0.2 between equivalent runs, scoped to
  their three protocols.

## Gaps

The extractor's nine gaps stand as recorded in `notes.md`. The review adds one.

1. **`dataset_version` is uninformative on the 428 non-ProteinGym evaluations.** "As used in the
   HyPLM technical report (2026-10-12)" is not false, since the report gives no dataset versions
   beyond ProteinGym v1.3 and Table 4's `Source` column, but it records nothing a reader can check.
   Table 4's attributions (TAPE, FLIP, FLIP2, DGEB, SaProt, DeepFRI) could be carried onto the
   evaluations they belong to.

## For the owner

1. **Whether to generalise the `perplexity` definition.** Question 3. It touches 19 results outside
   this batch, which is why the review did not make the change.
2. **Whether `claim_scope` should be readable anywhere.** Question 4. The field is declared for
   results but nothing displays it, so anything put there is invisible to a reader. Either it should
   be surfaced or it should stop being used for caveats; this review routed around it.
