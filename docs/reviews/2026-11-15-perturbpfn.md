# PerturbPFN, independent review

2026-11-15. Batch `data/omics/perturbpfn-20261115/`, issue
[#246](https://github.com/rewire-bio/rewire-benchmark-data/issues/246). Reviewed by a Claude agent
that did not extract the batch, against the extraction frozen at `batch.jsonl` SHA-256
`1b50664da2bfe60287cbe48e3b996d562f6c5594539bb07a06f46505560a12ca`. Not human scientific review.
Nothing was reproduced: transcription was checked against the pinned source, which is not
reproduction.

Receipt: `data/omics/perturbpfn-20261115/review.json`. Mismatch report:
`data/omics/perturbpfn-20261115/value-check.tsv`. Reviewer re-read:
`data/omics/perturbpfn-20261115/review/recheck_tables.py`. Edits:
`data/omics/perturbpfn-20261115/review/apply_review.py`.

## Sources

| Record | SHA-256 | Result |
| --- | --- | --- |
| `perturbpfn-20261115-source-arxiv-v1` | `42191efa04b45ca04b2be38b51ea374cd9bf891efe2399d331fec9eaeab200b1` | Matched |
| `perturbpfn-20261115-source-arxiv-abs` | `1f42d94a62e4251c24e7e138abd0a4904a6863a3e1ab94c5b155c885c929922a` | Matched |

Both were re-retrieved on 2026-11-15. The abstract page is mutable and its record says the hash
describes one retrieval, so a mismatch there would have been expected rather than a finding; it
matched anyway, and the refetched page still prints "Submitted on 26 Jul 2026", the CC BY 4.0
licence link and the FMSD 2026 Seoul comments line.

Every stored value was parsed from a text layer, so that layer matters as much as the PDF. A
`pdftotext -layout` run (poppler 26.08.0) on my own refetched PDF hashes to
`28b341ce3c893e7d734d05de5e522973152a3b0936bf0e6dd16565112eb9c0bb`, which is exactly the
decompressed content of `artifacts/arxiv-2607.23447v1.pdftotext-layout.txt.gz`. The archive is
therefore provably derived from the pinned bytes, not merely asserted to be.

No code, weights or checkpoint hash exists to check. The extractor's 2026-11-15 searches found
none; I did not repeat them, and the records state access as unavailable rather than open.

## How the values were compared

`npm run -s batch -- check-values`, rerun against the regenerated text layer, reproduced the
extractor's figures exactly and wrote a `value-check.tsv` byte-identical to the extractor's
(`9ea6f87b679db972807b832b538b1b4c063c45d08c0cfc67c0d8d761eebe8df8`): 64 `in_cell`, 11 `in_row`,
6 `locator_not_parsed`, and no `not_in_row`, `wrong_column` or `overclaimed_in_row`. The command
exits 1, because the six unparsed locators leave the status set outside `in_cell`/`in_row`. That is
a prompt to check those six by hand, not a mismatch. They are the five PerturbPFN Table 2 score
cells, which sit on an unlabelled line between the two runtime rows, and the Section 4.1 prose
value 0.6287.

All 81 results were then re-read by `review/recheck_tables.py`, written for this pass. It uses
neither of the extractor's scripts and a different strategy from both: it takes each table's column
spans from the character offsets of that table's own printed header line, assigns every numeric
token on a body line to the column whose header centre is nearest, and refuses any assignment that
is not one to one and in printed order. It matches cells to records through each result's
`source_locator` text rather than its ID, so a record whose locator names the wrong row or column
fails, and it checks `printed_value`, `numeric_value`, the printed spread and the system the
result's evaluation names. It covers all six locators `check-values` could not parse. All 81 agreed.

Two negative controls confirm the script can fail. Swapping RF X-Learner's printed 0.8793 and
0.9696 in the text layer fails on `printed_value`; pushing PORTIA's R-Prec. cell one column width to
the right fails on geometry, with the token landing in R-Recall.

Independently of the printed cells, each row's overall score was re-derived as the equal-weight mean
of its three normalised columns, as Appendix D.3 defines it. Every row agrees to within 0.00006.

Manual sample, 16 cells, drawn to cover column assignment in all three tables:

- Table 1, the third label and value pair on each of the three rows, where a positional parse is
  most exposed: `|ψ| ratio →1` 0.9386, `∆ cosine ↑` 0.7437, `Obs. NLL ↓` -0.1375. Also the first and
  second pairs of the third row, `Proj. F1 ↑` 0.3261 and `F1 ↑` 0.7649, which are the two F1 values a
  block mix-up would swap.
- Table 2, the unlabelled PerturbPFN score line (0.7186, 0.8813, 0.9183, 0.8394, #2), read against
  the header offsets of the RF X-Learner row printed above it; the GIM time 4495.6 ± 116.9; and the
  two PerturbPFN times 432.8 ± 0.34 and 1.11 ± 0.34, each on its own labelled row.
- Table 3, the middle columns: PORTIA R-Prec. 0.3970 and R-Recall 0.2668, SCENIC TFB-F1 0.1180 and
  R-Prec. 0.3802, PPCOR TFB-F1 0.0000.

The 54 descriptive records were read against Sections 2 to 5, Appendices A to E and Tables 4 to 8.
The checkpoint identity (step 3100 of a 3,500-step seed-17 run, 14.98M parameters, Tables 6 and 7),
the top-k gate k = 3 (Table 6), the 1.44 GPU-hours on one RTX 4090 (Appendix B), the four Sci-Plex
baseline settings (Appendix D.4), the GeneRNIB panel settings (Table 8, Appendix E.2) and the four
limitations the authors state (Section 5) all match. The model record's "scale-free" wording is the
paper's own, Section 2.1: the prior is "augmented with module structure to induce heterogeneous,
scale-free topology". The PORTIA description's "robust precision matrix estimation" comes from the
title of reference [44], which the record's locator names.

## Rulings

### 1. The six proposed metric concepts: all accepted

Checked against the 259 existing concepts. None of the six respells an existing one, so no result
was remapped, and all six were added to `data/vocab/metric.ttl` (now 265 concepts, inserted in
alphabetical order, insertions only).

- `min-max-normalised-score`, 21 results. Nothing in the scheme is a rescaling within a comparison
  set. `weighted-composite-score` is "a weighted sum of stated component scores", which is the
  overall column, not a single normalised metric; `leaderboard-percentile` is relative to
  submissions, not to a fixed method set. Its scope note states that values are comparable only
  within one table and points at `weighted-composite-score` for the composite.
- `negative-log-likelihood`, 1 result. The nearest existing concept, `log-loss`, is defined as the
  "mean negative log-likelihood of the true labels under the predicted class probabilities", which
  cannot be negative. Table 1 prints -0.1375, and Section 4.1 says "observation NLL evaluates the
  full zero-inflated log-normal predictive distribution": a density, not class probabilities. That
  sign is what decides it. The concept carries `skos:related :log-loss` and a scope note saying so.
- `magnitude-ratio`, 1 result. A ratio of mean absolute predicted to mean absolute true strengths.
  Not `regression-slope`, which is fitted. Direction `unknown`, because Table 1 prints the target as
  `→1`, so neither direction is better; the scope note says that.
- `genernib-regression-precision` and `genernib-regression-recall`, 12 results. The existing
  `r-precision` is "precision among the R highest-ranked items" and is `skos:broader :precision`,
  an information-retrieval measure. Appendix E.3 expands the R: "Regression precision and recall
  (R-Precision and R-Recall) assess whether regulators selected from the inferred network predict
  held-out target-gene expression under conservative and broader regulator budgets". That is a
  regression score, not retrieval precision, so reusing `r-precision` or `precision` would be a
  false match. Benchmark-specific concepts have ample precedent (`perturbench-*`, `scib-*`,
  `amber-*`, `capri-*`, `beeline-stability`).
- `genernib-virtual-cell-score`, 6 results. Not `vcc-score`, which is the Virtual Cell Challenge
  2026 leaderboard composite. The scope note says both that and where the definition came from.

The three GeneRNIB concepts are described from the PerturbPFN text, because the GeneRNIB paper was
not retrieved. Each carries a scope note naming GeneRNIB as the definer and this preprint as the
description's source. I did not retrieve STATO, QUDT or EDAM, so I accepted the extractor's
statement that no external term was found rather than confirming it; none of the six carries an
external match.

One mapping I kept but will not call settled: GS-F1 and TFB-F1 use the generic `f1-score` with a
qualifier. GS-F1 is an F1 over pathway sets and fits. TFB-F1 is described as "normalized agreement
and coverage against TF-binding references", which may not be a plain F1. Without the GeneRNIB paper
there is nothing better to map it to, and a GeneRNIB-specific concept would be guessed rather than
read, so it stays as it is and the receipt records the mapping as provisional.

### 2. Table 2's min-max normalisation: a metric qualifier and a limitation, no evidence concern

The source is explicit about the property. Appendix D.3: "These normalized scores depend on the
included comparison set." Section 4.2: "Because min-max normalization is relative to the models
being compared, Figure 2 additionally reports the raw protocol-level distributions."

That is a documented property of the metric, not a fault in the source, and the concern mechanism is
the wrong instrument for it. An `evidence_concerns` entry withholds a named result from every
comparison, including the comparison the table exists to make, which is the paper's own ranking of
seven methods on one protocol. The property to express is narrower: these values compare within
Table 2 and nowhere else. The 2026-10-22 phenotype-perturbation review declined a concern on the
same ground, that a source concern would block every comparison from the source over one metric's
scope.

Three guards carry it instead, and I checked each rather than assuming it. The metric concept's
scope note says values are comparable only within one table. All 21 qualifiers name the compared set
and the aggregation, for example "Pearson correlation between predicted and observed mean expression
over the 50 marker genes, min-max normalised across the seven Table 2 rows within each of 12
Sci-Plex highest-dose protocols and averaged over protocols"; the seven `weighted-composite-score`
qualifiers name the three components and their equal weights. Every one of the 28 values, and the
seven ranks, carries the limitation "the value changes if a method is added or removed, so it is
comparable only within Table 2", and the protocol and benchmark records carry it too. No tightening
was needed.

One residual risk is worth recording rather than hiding. Within a study, comparisons key on
protocol, dataset, metric, unit, qualifier, split and direction, so the qualifier isolates these
values. Across studies, the gap-outlier rule groups by metric concept and by the protocol or the
task or benchmark it sits within, and not by qualifier. A future study reporting
`min-max-normalised-score` on another protocol under `catalog-task-cell-perturbation` would
therefore pool with these values. Nothing in the store does today, the concept is new to this batch,
and the fix then is a concern scoped to the offending pair, not a blanket one now.

### 3. The five GeneRNIB baseline rows as `paper_compilation`: correct

Appendix E.3, last paragraph: "We compare against Pearson correlation, partial Pearson correlation
(PPCOR), GRNBoost2, PORTIA, and SCENIC. Baseline results are taken from the official GeneRNIB score
archive for the same 300BCG dataset and 50,000-link budget."

The PerturbPFN authors did not run them, so `author_reported` is wrong. No independent paper
reported them either, so `independent_paper` is wrong. The vocabulary's `paper_compilation` is
"result copied into a review, leaderboard or compilation from earlier papers", which is what
happened: an archive's numbers copied into this paper. Section 4.3's "All methods are evaluated using
the same official GeneRNIB pipeline and link budget" describes the scorer, not who ran the methods,
and does not pull the other way. The PerturbPFN row of the same table stays `author_reported`, which
is right: Appendix E.1 and E.2 describe the authors' own inference run. Each of the five evaluations
also records that the archive version, the retrieval date and the baseline method versions are not
stated.

### 4. Sci-Plex identity: the `same_data_as` links removed, no duplicate record

Two corrections to the framing in my brief. There is no new Sci-Plex parent dataset in this batch,
and none should be: the two new `dataset` records are GeneRNIB 300BCG and the synthetic prior
episodes, and `notes.md` decision 1 says why no parent was created, which is that the Srivatsan 2020
paper was not retrieved. The new record is one `dataset_subset`.

Nothing duplicates an existing record. The store holds no GeneRNIB, 300BCG, PORTIA, SCENIC, CondOT,
RF X-Learner or PerturbPFN record at all. GRNBoost2 and PPCOR exist only as BEELINE
`acquired-configuration-*` entries with no parent method and status `discovered`, and
`discovery-model-grnboost` is the earlier Aertslab Spark GRNBoost, not GRNBoost2; the new method
records say so. No existing record describes a Schneider et al. Sci-Plex slice.

The two `same_data_as` links were removed. `same_data_as` is informational data reuse that never
merges results, and the practice recorded in two earlier reviews is that it requires identical data:
the 2026-10-09 plasma ctDNA review states the rule ("`same_data_as` is defined for dataset subsets
with identical data") and the 2026-10-22 phenotype-perturbation review removed a link because a
selected subset "is not the same data". This subset is four HDAC inhibitors in three cell lines with
GIM preprocessing and "a protocol-specific set of 50 marker genes" (Appendix D.1), held out by dose;
the two PerturBench records are covariate-transfer splits to a held-out cell line over PerturBench's
own compound selection. Same experiment, different data. The shared provenance is not lost: it is
already in the subset's `source_dataset` ("Sci-Plex, Srivatsan et al. 2020, Science 367(6473):45-51")
and I added a `reuse_note` naming both PerturBench record IDs and stating that the slices differ and
why no link is recorded.

### 5. Section 4.3's edge AUROC 0.9168 and AP 0.7570: not extracting them is right

Section 4.3: "PerturbPFN achieves edge AUROC 0.9168 and edge average precision 0.7570 in the
auxiliary graph-ranking evaluation (Appendix E), although these metrics are not included in the
official GeneRNIB score table." I read all of Appendix E. E.1 is the GeneRNIB 300BCG protocol, E.2 is
panel construction and network aggregation, E.3 is the official scoring and the baselines. There is
no auxiliary graph-ranking evaluation anywhere in v1, and no reference edge set against which an
edge AUROC could have been computed.

A result needs an evaluation, and an evaluation needs a system, a protocol and data. Two of those
three are missing, and inventing them would be a guess. An evidence concern is not the answer either:
nothing was extracted, so `applies_to` would be empty, and an unscoped concern would withhold every
record resting on the paper over two values that support nothing. The claim
`perturbpfn-20261115-claim-source-appendix-e-auxiliary` on the source record is the right holder. It
quotes the sentence, carries both numbers, locates them at "Section 4.3, last paragraph before
Section 5; Appendix E", and says why they were not extracted. Kept as it is. If a v2 adds the
appendix, the values can be extracted then against a protocol that exists.

### 6. `perturbation-ahlmann-20261011-method-no-change` reused for Observational: correct

Appendix D.4: "The Observational baseline ignores the perturbation and predicts the control
distribution." The stored method's description is "Predicts, for every perturbation, the expression
observed in the unperturbed control condition." Same rule. Reuse is right and a second record would
split one baseline across two IDs.

### 7. The Sci-Plex protocol's link to `catalog-task-cell-perturbation`: kept

The tension is real. That task's scope note is "Predict expression changes after unseen
perturbations", while Appendix D.2 says "The held-out drug is not completely unseen, since lower-dose
responses are available". I kept the link. The query condition, a named drug at its highest dose in a
named cell line, was never observed, so it is an unseen perturbation on a plain reading, and the task
is a broad catalogue entry with no metrics of its own. The protocol and benchmark both carry "Dose
extrapolation, not unseen-drug prediction" as their first limitation and a claim records the paper's
own sentence, so nothing reads the link as a claim of unseen-drug validation. No value merge follows
either: the protocol is also `part_of` its own benchmark, and the normalised metric concept is unique
to this batch.

Two things for a later pass rather than this one. The existing PerturBench Srivatsan20 protocols use
their own `perturbench-task-ct-*` tasks and nothing in the store currently links to
`catalog-task-cell-perturbation`, so this batch is the first user of it; and that task's scope note
would be better phrased as "a held-out perturbation condition" than "unseen perturbations". Both need
a change to a stored record, which is outside a batch review.

### 8. Splitting "Avg. ŝ / rank" into a score and a rank: acceptable

The cell prints two quantities of different kinds, a score and an ordinal, and the store has separate
concepts for them. Each result keeps the cell's own text: `printed_value` "0.8870" with
`numeric_value` 0.8870, and `printed_value` "(#1)" with `numeric_value` 1 under `rank`, whose
vocabulary direction is `lower`. Both locators name the same column and say which part of the cell
they take, so the split is visible to a reader and reversible.

### 9. Keeping the Section 4.1 prose value 0.6287: yes

Section 4.1: "The straight-through top-k gate used by the decoder obtains a lower F1 of 0.6287,
reflecting the additional sparsity constraint imposed during rollout." It is a reported measurement
on the same evaluation as Table 1's target F1, and a reader comparing the two needs both. Being
outside a table is not a reason to drop it; being indistinguishable from the table value would be,
and it is not. Its qualifier is "Intervention targets: straight-through top-k gate used in the
decoder rollout (k = 3, Table 6)" against "Intervention targets: node-wise probabilities thresholded
at 0.5" for Table 1's 0.7649. The k = 3 is Table 6's "Target head, Straight-through top-k, 3".

### 10. Runtime, ranks and the "/" rows

Checked, nothing changed. Table 2 prints "/" in the time column for Naive and Observational; both
evaluations record `timing_seconds` as `inapplicable` with the printed "/" as the note, and neither
has a runtime result, which my script asserts rather than assumes. The two PerturbPFN times are one
evaluation with two results whose qualifiers keep them apart, one "without any one-time pretraining
cost" and one "plus PerturbPFN's one-time pretraining cost divided across the 12 protocols", so the
432.8 s is never compared with an inference time. Both print the same spread, 0.34, which is what
adding a constant does. The caption says only "Times are mean ± standard deviation", so every spread
is recorded as a standard deviation with a note that what it is taken over is not stated.

## What changed

| Where | Change |
| --- | --- |
| `batch.jsonl`, `perturbpfn-20261115-data-sciplex-hdac-3x4` | Two `same_data_as` links removed; `reuse_note` added stating the shared Srivatsan 2020 provenance, the two PerturBench record IDs and why no link is recorded |
| `batch.jsonl`, all 135 records | `review` object replaced with this pass's; `status` raised from `needs_review` to `source_checked` |
| `data/vocab/metric.ttl` | Six concepts added: `min-max-normalised-score`, `magnitude-ratio`, `negative-log-likelihood`, `genernib-regression-precision`, `genernib-regression-recall`, `genernib-virtual-cell-score` |

No value was changed, no result was superseded, no evidence concern was added and no record was
disputed. Every record carries a `source_locator` and every one was checked at it, so none is left
at `needs_review`.

## Conflicts and apparent conflicts

- Table 1's caption says "over 128 held-out synthetic batches" while Section 4.1 says "1,024 fresh
  episodes". These reconcile: Table 7 gives a synthetic batch size of 8, and 128 times 8 is 1,024.
  The dataset record already says so. What stays unstated is whether the printed metrics are pooled
  over the 1,024 episodes or averaged over the 128 batches, which the evaluation records as missing.
- Section 4.3 cites an Appendix E evaluation that v1 does not contain (ruling 5). It is a dangling
  internal reference, not a disagreement between two printed numbers, so it does not touch the
  values in Tables 1, 2 and 3.
- The abstract frames the work as predicting responses to unseen chemical perturbations, while the
  real-data test is dose extrapolation. The claim
  `perturbpfn-20261115-claim-protocol-sciplex-not-unseen-drug` records the gap with Appendix D.2's
  own sentence. No comparison in the store rests on the abstract's framing.

Nothing was found that disagrees with another study. The discrepancy step could not be run: the
rules operate on the built store, so no entry of `discrepancies.json` can name a result of a batch
that has not been built yet. The next build is where these 81 results first become visible to it.

## Gaps that remain

- The GeneRNIB paper, repository and score archive were not retrieved. The benchmark record, the
  300BCG dataset record, the three GeneRNIB metric definitions and the provenance of the five
  baseline rows all rest on this preprint's description, and the archive version is not printed.
- The GIM paper and codebase were not retrieved, so the Sci-Plex preprocessing, the 50 marker genes
  and the split are recorded from the PerturbPFN text alone.
- No code, weights, checkpoint hash or code licence. CC BY 4.0 covers the article text only.
- Figure 2's raw per-protocol mean distance, Pearson r and W2 distributions are box plots with no
  printed values, so the only Sci-Plex numbers in the store are normalised ones.
- Replicate consistency, which Appendix E.3 says the official pipeline also reports, is omitted from
  Table 3 "for space".
- No seeds, repeated runs, cell counts per condition or dose counts per drug are reported, and
  Appendix D.4 says baseline metrics were recomputed "whenever prediction arrays are available"
  without saying whether any baseline lacked them.
- The claim that the GeneRNIB run covers 1,600 genes is arithmetic on Table 8's 100 TF seeds and
  1,500 candidate target genes, not a printed figure. The panel count 190 does follow from Table 8
  (5 TF groups of 20 by 38 target groups of 40).

## For the owner

Two items need a change to an already stored record, so they are named here rather than done:
`catalog-task-cell-perturbation`'s scope note ("unseen perturbations") is narrower than the
protocols that will link to it, and the BEELINE `acquired-configuration-*` entries for GRNBOOST2 and
PPCOR could now be linked to this batch's GRNBoost2 and PPCOR method records.
