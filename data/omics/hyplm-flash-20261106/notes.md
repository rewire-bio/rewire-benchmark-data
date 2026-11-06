# HyPLM-Flash extraction, 2026-11-06

Batch for issue #233: HyPLM-Flash, Tencent Hunyuan's 650M protein language model released on
2026-11-02, and the evaluation in its technical report (dated 2026-10-12).

Extractor: Claude agent. Not reviewed: every record is `needs_review`, no human review is claimed,
and `review-evidence` has not run. Built in its own worktree (`wt/hyplm-flash`, branch
`claude/hyplm-flash` off `claude/hyra-models` at 8e102ca) per the coordinator's worktree rule.

## Sources

Pinned to commit `0dcc533cc9f8f76c90ecbfe944df816b6672328a` of `Tencent-Hunyuan/Hyra-results`.

| Record | Artifact | SHA-256 |
| --- | --- | --- |
| `hyplm-flash-20261106-source-report` | `AI4Science/hyplm_flash/HyPLM_Technical_Report.pdf` | `d81d88a4…dea1710` |
| `hyplm-flash-20261106-source-model-readme` | `AI4Science/hyplm_flash/README.md` | `db6ab273…42542a3` |
| `hyplm-flash-20261106-source-licence` | `AI4Science/hyplm_flash/LICENSE` | `a0a9dc95…b64a031` |
| `hyplm-flash-20261106-source-engine-model` | `hyplm/engine/model.py` | `8bba607a…8fd4255` |
| `hyplm-flash-20261106-source-engine-packing` | `hyplm/engine/packing.py` | `3eb213e8…f1c1828` |
| `hyplm-flash-20261106-source-engine-graphs` | `hyplm/engine/graphs.py` | `29df2c0d…f3f1bc` |

The shared top-level README is reused as `hyra-results-20261106-source-repository-readme`, added
by the reviewed HyInv batch; no second record is created.

The engine files are separate artifacts from the report, so each has its own record and hash. They
are cited only for the INT8 threshold. Text artifacts and the report's gzipped text layer are in
`artifacts/`; the PDF is not committed because it is refetchable at the pinned commit and
`extract/parse.py` refuses any other bytes.

**Dates.** The report is dated 2026-10-12 on page 1. The PDF's CreationDate and ModDate are both
2026-10-29T23:28:47+08 (pdfTeX-1.40.19), 17 days later. Per the coordinator's ruling this is a note
on the source record (`version_note`), not a concern. No earlier PDF exists at the pinned commit, so
whether the rebuild changed content was not checked.

## How the values were extracted and checked

`extract/parse.py` parses the `pdftotext -layout` text layer with every row label, metric label and
cell count asserted, reads each table's page from the form feeds, and asserts every value printed
twice: Table 2 against Tables 6 and 7; Table 3's NLL against them; Figure 3a and the Table 5
averages against the ProteinGym row; the four printed paired differences against the differences
of the printed scores; and the regression averages against the mean of the ten splits Appendix A
names (checked for the four models whose splits are printed).

`scripts/omics/batch.py check-values` gave 267 `in_cell`, 202 `in_row` and 15
`locator_not_parsed` (`value-check.tsv`). Because the coordinator's tooling note says a row-level
pass is weak evidence, `extract/check_cells.py` adds independent checks (`cell-check.tsv`, 88 rows,
all equal):

- a second parse with `pdftotext -raw` must give the same ordered value sequence for every row of
  Tables 3, 5, 6 and 7, so the column order is confirmed by a different text mode;
- each Table 3 PPL must lie within exp of its NLL's rounding interval, which pins NLL against PPL;
- each Table 5 average must equal the mean of its five categories within combined rounding.

Two tolerances were first set too tight and failed on rounding, not on content: ESM C 600M's PPL
(exp(1.720) = 5.585 against printed 5.59) and E1-300M's Table 5 average (mean 0.4164 against
0.417). Both fit once the rounding of the inputs is counted, and the code now states why.

The 15 unparsed locators are prose values and four Figure 3a bar labels. `check-values` did not
evaluate them, so the shared-window false pass the coordinator flagged cannot arise for them; but
nor were they checked by the tool. Their only check is the parser's anchored match: exact sentence
regexes for prose, and for Figure 3a the label at line start with its value on the same line, in an
asserted order that excludes the legend lines of panel b.

## Record counts

| Kind | Count |
| --- | --- |
| source | 6 (plus the reused repository README) |
| model | 5 |
| configuration | 22 |
| benchmark | 1 |
| dataset | 22 |
| protocol | 42 |
| evaluation | 484 |
| result | 484 |
| claim | 65 |
| total | 1,131 |

## What was extracted

| Location | Results |
| --- | --- |
| Tables 6 and 7, every task for 13 models | 404 (12 Table 7 cells are printed as dashes) |
| Table 3, perplexity for 10 models on 2 panels | 20 |
| Table 3, NLL for ESM-2 3B, ESM-2 15B, ESM C 6B | 6 (the rest repeat Tables 6 and 7) |
| Table 5, the authors' dagger rows by selection type | 35 |
| Table 5, dagger averages not printed elsewhere | 4 |
| Figure 3a, bars for models no table prints | 4 |
| Section 4.1, paired differences with intervals | 4 |
| Section 4.2, ten-split regression averages | 5 |
| Section 4.2, ESM C 6B CB513 accuracy | 1 |
| Section 3, INT8 engine throughput | 1 |

Not extracted as results: Table 2 (a subset of Tables 6 and 7, asserted equal); Table 1 and Table 4
(descriptive; Table 1's HyPLM row and ratios are claims, other models' compute is out of scope);
Table 5's undaggered rows (see below); Figure 1 (see below); Figure 3b (no printed values).

## Decisions the brief asked me to make

### INT8 and BF16: two configurations

Two configurations, not one with a precision qualifier, because the paths execute different
arithmetic and an INT8 label does not mean INT8 throughout. The engine applies INT8 per packed
batch only when the batch holds at least 1,024 tokens (`model.py` lines 41 and 102); smaller
batches run BF16 even with `precision="int8"`, including every CUDA-graph bucket (64 to 512
tokens, `graphs.py` line 12), so the single-protein low-latency path is always BF16.

- `hyplm-flash-20261106-config-hyplm-flash-bf16-evaluation` carries every accuracy result, because
  Section 3 says accuracy is evaluated with BF16 arithmetic. The report does not say whether those
  runs used the engine's bf16 mode, which the configuration states.
- `hyplm-flash-20261106-config-hyplm-flash-int8-engine` carries the throughput result only and
  states the threshold in `condition`. It has no accuracy result because the report prints none.

### Which tasks have per-task values

All 32 tasks have printed values for 13 models (Tables 6 and 7; 12 cells of Table 7 are dashes,
for ProtT5-XL, Ankh-base, Ankh3-large and xTrimoPGLM-1B on the three zero-shot and likelihood
rows). For the other 16 models only aggregates or single tasks are printed: ProteinGym (Figure 3a,
Table 5), the two likelihood panels (Table 3), CB513 for ESM C 6B and the ten-split regression
average for ESM-2 3B (prose). Eight of the 28 public checkpoints have no printed value anywhere,
and the report never lists the 28.

### Throughput: a result, with its condition

Recorded as one result, following the HyInv precedent that a measured speed on a stated workload is
a result: 131,000 residues per second on one H20 for 2,048 held-out proteins (639,806 residues) in
length-sorted batches of at most 16,384 tokens. Its protocol and limitations state that INT8 applies
only to batches of at least 1,024 tokens. Per ruling 12, the numbers most easily confused with it
are stored as claims: the README's rounded "about 130,000", the BF16 mode's 90,000 (no workload
stated, so not a result), the 1.9 to 2.7 times range and the 48,000 to 69,000 baseline range.

### BF16 for regressors: author guidance only

No printed comparison supports it. Section 3 lists what INT8 preserves within 0.01 (zero-shot
fitness, structure, function annotation, likelihood); regression is absent, and no INT8 value is
printed for any task. The recommendation rests on the stated 1% difference between variant
representations. It is a claim marked as author guidance. The gap is sharper than the
recommendation implies: HyPLM-Flash's largest supervised margin over ESM-2 650M, AAV two-vs-many
(0.650 against 0.518), is a regression result measured in BF16, while the released default is INT8.
This is stated on the INT8 configuration (`limitations`, and `missing_metadata.result_status`) and
in the limitations of every regression protocol, so a reader on one regression result sees it.

## Other decisions

- **The ProteinGym tie is on the records.** The 0.409 headline result, and those of the seven models
  Section 4.1 calls statistically tied with it, carry `claim_scope` stating that the differences are
  not significant. The four printed paired differences are results with their 95% intervals, all
  including zero, under the new concept `spearman-correlation-difference`.
- **ProteinGym is a source-specific protocol.** It does not reuse `rewire-proteingym-v1-3-dms-
  substitutions` or any leaderboard protocol: the scoring code, the BF16 adapters and the checkpoint
  revisions are the authors'. It does reuse the 217-assay dataset
  `vep-lit-20261014-data-proteingym-dms-substitutions-144fe22`, because the report names the same
  assay set (ProteinGym v1.3, 217 substitution assays). The report does not name the commit of its
  assay files, which the evaluations state.
- **Table 5's undaggered rows are not recorded.** They are published leaderboard values the authors
  quote and did not run; they belong to the leaderboard's own source. Only the dagger rows are
  results, with `metric_implementation` and `aggregation` left null on the selection-type
  evaluations so nothing compares them automatically with a leaderboard row.
- **Binding gap.** No difference is recorded for any Table 5 column. The only ESM-2 650M binding
  value (0.337) is an undaggered leaderboard row, so 0.277 against it mixes origins with no interval.
  This is a limitation on HyPLM-Flash's binding result. The figure -0.060 is not printed anywhere in
  the report.
- **Figure 1 is not recorded as results.** Figure 1b's won and lost labels are claims, one number
  each. ESM-2 650M's row sums to 34 against the axis's 'of 35' while the other seven sum to 35, and
  Figure 1 summarises "35 task splits" that the report never defines against its 32 tasks. I had told
  the coordinator Figure 1b would get an `evidence_concerns` entry scoped to the ESM-2 650M
  configuration; I dropped it, because it would block comparison for all of that model's valid
  task results over a figure none of them rests on. The claims carry the finding.
- **Store reuse.** Datasets: the ProteinGym set above, TAPE secondary structure, fold and
  fluorescence (sizes match Table 4), the TAPE ProteinNet CASP12 record and seven FLIP splits.
  HumanPPI and DeepLoc were not reused: their printed sizes differ from the store's PEER records.
  TAPE stability was not reused: Table 4 prints one set of sizes for fluorescence and stability
  together. Models: ESM-2, ESM-1b, ESMC, ESM3, ProtBERT, ProtT5-XL and xTrimoPGLM. New families:
  E1, AMPLIFY, DPLM (distinct from DPLM-2) and Ankh. Configurations are all new and source-specific,
  as the store's existing ones are for other sources' runs.
- **Concerns** (all with `applies_to`): the recent-PDB panel described two ways (window start and
  chain against entry differ); xTrimoPGLM's embedding results, which the authors keep as unaffected
  by an adapter incompatibility they did not test (scoped to that configuration); and the three
  regression splits Appendix A says differ by up to 0.2 between equivalent runs (scoped to their
  protocols).
- **Vocabulary**: `mean-average-precision-at-5` and `spearman-correlation-difference` added to
  `metric.ttl`, sorted, neither encoding this source's estimator (ruling 10). NLL uses `log-loss`
  and PPL `perplexity`, following existing store usage of perplexity on held-out sequences.
- `facets.method_types` is filled on every configuration and model.

## Gaps

1. Eight of the 28 public checkpoints have no printed value, and the report never lists the 28.
2. No interval is printed for any table cell, though Section 4 says intervals were computed.
3. No accuracy value for the INT8 engine on any task, including the regression family.
4. Baseline throughputs are not printed per model, only as Figure 1a points and two ranges.
5. Figure 1a's mean normalised score and Figure 3b's per-category bars print no labelled values.
6. The 35 task splits of Figure 1 are not defined.
7. No panel manifest is published; the recent-PDB panel cannot be rebuilt from the report.
8. The weights' GitHub Release tag and shard hashes were not retrieved.
9. Checkpoint revisions are not printed for any baseline.
