# The new extractor against the 115 scripts that wrote the store

Measured on 2026-11-19 over the store and the archive as they stand. The store
holds 52,278 results written by 115 hand-written Python scripts and nobody had
measured how good they are. This measures both sides on the same documents, by
position in the same hashed text layers, and says plainly whether the new
command is better. Every number has the command behind it. No model was called
at any point.

## The headline

On the cells both sides can see, the new extractor finds the same number as the
old scripts 10,720 times out of 10,828, agrees on every one of those, and
disagrees on none. It invents nothing: of 418,440 candidates, 18 report a value
their own span does not print as the same characters, every one of those 18 was
read by hand, and every one is the same number in a different notation.

| | Cells | Share |
| --- | --- | --- |
| Comparable: a stored result placed in a layer the extractor read | 10,828 | |
| Agreement | 10,720 | 99.0% |
| Disagreement | 0 | 0% |
| Missed | 108 | 1.0% |

That is the cell question and the answer is yes. The record question is
separate and the answer is no, for one reason named at the end.

## How the two sides were joined

By position, never by value. A table of f1 scores prints 0.73 in four places,
so a value join would manufacture agreement.

Each stored result carries a locator string. `measure` in
`scripts/omics/spans/cli.ts`, the code behind `npm run spans -- measure`,
resolves it to a span in a layer the archive holds: a layer hash and a code
point range. Each candidate carries a span of the same shape, built from the
cell's own offsets. A stored result and a candidate are the same cell when they
name the same layer and their ranges overlap. Overlap, not equality, so a
difference in how each side trims a cell cannot break a match, and a
neighbouring cell cannot be mistaken for the right one because two distinct
cells share no characters.

Running the join:

```
npx tsx scripts/omics/extract/measure-store-spans.ts <out>/store-spans.jsonl
npx tsx scripts/omics/extract/measure-vs-store.ts <out>/store-spans.jsonl <out>/report
```

The first reproduces the committed span figure, 18,667 of 52,278 locators
resolved, 35.7%. The second runs the extractor over every gold source in
process and writes the tables below.

Three checks guard the join itself, because an agreement figure is only worth
what the matching rule is worth.

| Check | Result |
| --- | --- |
| Agreements where more than one candidate overlapped the stored span, so the join could have picked a neighbour printing the same number | 0 of 10,720 |
| Candidates matched to more than one stored result | 24 |
| Agreements that needed the looser half of the number comparison, the leading number of the stored value | 4,571 |

The first is the one that could have manufactured agreement and it is zero: a
grid cell and a sheet cell each resolve to one cell, and two distinct cells
share no characters. The second is a finding about the store and is below.
Thirty of the 4,571 were read by eye, from the first 400 the run records: every
one is the same number with the two sides keeping different text around it, a
spread, a thousands separator, a percent sign or a unicode hyphen in an
exponent.

### 24 stored results carry a value their own locator contradicts

Twenty-four candidates were each matched by two stored results, all of them on
`rare-reanalysis-20261009-source-demidov2024`, and the pairs are the same
shape. Table 1 prints `1,203 (64)`: the total calls and, in brackets, the calls
on sex chromosomes. The old script wrote two records, one locating `(value
outside brackets)` and one `(value in brackets)`, and gave both the printed
value `1,203 (64)`. All 24 of the bracket records store the whole cell rather
than the bracketed number, so 24 records in the store hold a value their own
locator says they do not hold. Nothing here was changed; this is a lead for a
correction batch.

## What was measured, and what could not be

The gold set is not a hand pick and not the 20 sources the extractor was
demonstrated on: those were chosen by source id and most hold no stored results
to compare against. It is every source that has stored results and at least one
layer carrying a geometry the extractor reads, 225 sources, holding 22,445
stored results between them.

| | Results | Share of 22,445 |
| --- | --- | --- |
| Placed in a layer the extractor read: comparable | 10,828 | 48.2% |
| Locator resolved to no span at all | 11,556 | 51.5% |
| Resolved into a layer the extractor does not read | 61 | 0.3% |

The second row is the limit on this measurement and it is a property of the
store's locators, not of either extractor. Half of what the old scripts wrote
cannot be placed in the bytes the archive holds, so it can be neither matched
nor called missed.

There is a second, larger bound on anything built from this extractor. Of the
52,278 stored results, 22,662 sit on a source carrying a grid or a sheet layer
at all, 43.3%. The rest are on PDF-only, prose-only or plain-text sources,
where this pass emits nothing by design: `shared/archive/layers/grid/index.ts`
records why a `pdftotext -layout` layer yields no columns. Measured with a
count over `data/omics/layers/registry.jsonl` and `data/evidence/results`.

## The four numbers, by source class

| Class | Agreement | Disagreement | Missed | Comparable | Not comparable |
| --- | --- | --- | --- | --- | --- |
| `jats-table-grid@1` | 3,697 | 0 | 23 | 3,720 | 5,690 |
| `ooxml-sheet-tsv@1` | 6,989 | 0 | 60 | 7,049 | 1,882 |
| `html-table-grid@1` | 34 | 0 | 25 | 59 | 4,045 |
| All | 10,720 | 0 | 108 | 10,828 | 11,617 |

PDF is absent because it is not a class here: no PDF source carries a geometry
this pass reads, so no PDF source is in the gold set.

The HTML row is small and it is small for a reason that is not about either
extractor. 4,045 of the 4,104 stored results on HTML sources have a locator
that resolves to no span, so there is almost nothing left to compare. Read the
HTML row as 59 cells, not as a rate.

### The disagreements, and why there are none

There were 96 on the first pass and 61 on the second, and every one of the 157
turned out to be one number written two ways. They are listed because the
comparison was wrong before it was right, and a reader should be able to see
which:

| Shape | Count | Example |
| --- | --- | --- |
| Cell prints the value and its spread; the record keeps the value only | 96 | stored `0.114`, cell `0.114 (0.007)` |
| Exponent written with a unicode hyphen | 36 | stored `5.17E‐10`, candidate `5.17e-10` |
| Record keeps a thousands separator | 25 | stored `398,597` and `4,205 (264)` |

The first shape was the comparison reading `printed_value` where it should have
read `numeric_value`: the candidate keeps the cell verbatim and puts the number
in its own field, and comparing the text reports a disagreement on every cell
that prints a spread. The other two were the comparison reading digits where
the repository's own value check reads a number.

The comparison now reads a number the way `valuePresence` in
`scripts/omics/spans/cli.ts` reads one, at the precision the record writes,
with unicode dashes normalised and thousands separators removed. After that,
every pair of numbers the two sides report for the same cell is the same
number. There is no case in the gold set where the old script and the new pass
disagree about what a cell says.

### The 108 misses, every one read

A miss is a stored result placed in a layer the extractor read where no
candidate covers its span.

| Why | Count |
| --- | --- |
| The cell prints a number with a unit the pass has no rule for (`12.69 Å`) | 56 |
| The stored value is a placeholder, not a number (`NaN`, `OOM`, `N/A`, `†`, `–`, `Length Exceeded`) | 18 |
| The cell prints an interval and no point value (`[0.011, 0.031]`) | 17 |
| The number is printed in a sentence or a figure caption, not a table cell | 10 |
| The cell prints a bound and no point value (`≤ 0.070`) | 4 |
| The stored value is a phrase, not a number (`approximately 19`, `around 1`) | 2 |
| The cell prints an unbalanced bracket (`0.9400 (95 CI: 0.9082 - 0.9718`) | 1 |

Ten of the 108 are a number the extractor could have found and did not, and
nine of those ten are printed in running text rather than in a table, which
this pass does not read. The remaining one is the unbalanced bracket.

Twenty of the 108 are a finding about the store rather than about the
extractor. `NaN`, `OOM`, `N/A`, `Length Exceeded`, `†`, `–`, `approximately 19`
and `around 1` are stored as result values with the full result record around
them. The new pass refuses to emit a candidate for any of them, which is the
behaviour `batch.ts` already requires and the old scripts did not follow.

## Invented values: 0

Three checks, run over every candidate of every gold source rather than a
sample, and run against the layer bytes read fresh rather than against the
index the pass built its spans from.

| Check | Candidates | Failures |
| --- | --- | --- |
| The byte offsets decode to the characters the span claims | 418,440 | 0 |
| The code point offsets cover the same characters | 418,440 | 0 |
| The layer at those characters prints the number the candidate reports | 418,440 | 18 |

The 18 are all one source, `mpro-pose-affinity-2025`, and all one shape: the
cell prints `3.51 × 10–35` and the candidate reports `3.51e-35`. Each was read
by hand. Every one is the same number in a different notation, and the check
compares characters. The measured invention rate is 0.

By construction it should be 0, and the construction is worth stating because a
measurement of zero is only as good as the thing it measures. `candidate.ts`
makes the span field required, so a candidate with no span cannot be built.
Both passes build the span with `spanAt`, which slices the layer text at the
cell's own offsets, so `span.exact` is layer bytes rather than anything the
pass composed. The report above is the measurement; the required field is the
reason.

## The extras, and why most of them are not findings

418,440 candidates, 10,696 of them matched to a stored result. The other
407,744 are not 407,744 results the old scripts missed, and the bins say why.

| Class | Invented | Accounted for by an unplaced stored result | In a table the join reached | In a table the join never reached |
| --- | --- | --- | --- | --- |
| `jats-table-grid@1` | 0 | 3,006 | 67 | 20,082 |
| `html-table-grid@1` | 0 | 2,956 | 24 | 4,016 |
| `ooxml-sheet-tsv@1` | 0 | 966 | 30,527 | 346,100 |

The second column is the honest correction. A stored result whose locator does
not resolve cannot match any candidate however right both are, so before a
candidate is called new it is checked, one for one, against the numbers that
source's unplaced stored results hold. The case that forced this: on
`hitdisc-20261022-source-shen2025`, the extractor emits exactly the 20 Table 2
cells the store holds for the row `ipTM`, with the same twenty numbers, and the
span join reached none of them. Without the correction all twenty would have
been reported as results the old scripts missed.

The fourth column is dominated by the workbooks, 346,100 of 370,198, and those
are not missed results either. A supplementary workbook is a dataset: the
`vep-lit-20261014-source-livesey2025-supplementary-2` sheets are per-variant
scores, not reported results. Deciding which sheets report results is a later
stage's job. Compare the JATS and HTML counts with each other and read the
workbook counts as a ceiling.

## What was fixed in the extractor, and what it bought

Two defects, both found by this measurement, both in how a printed cell is read
rather than in how a span is built.

The pass called `parseCell` and treated its refusal as "this cell holds no
number". `parseCell` is right to refuse in both cases and the pass was wrong to
agree. It refuses a cell whose tail is not itself one number, `4.66
(3.77-5.77)`, because a caller filling a standard deviation field cannot use
that tail. It refuses a cell carrying a percent sign unless the caller has
already decided the column is a percentage, so that nothing silently turns a
percentage into a fraction. This pass does neither: it carries the tail
verbatim in `uncertainty_printed` and decides nothing about it, and it keeps
the printed value with its sign while `printedUnit` reads the sign as the unit.
No scale is changed anywhere.

`shared/omics/extract/value.ts` now holds that rule and both passes call it.
Measured over the same gold set, same comparison, with the fallback switched
off and on:

| | Candidates | Agreement | Missed | Disagreement | Invented |
| --- | --- | --- | --- | --- | --- |
| Before | 412,520 | 9,471 (87.5%) | 1,357 | 0 | 0 |
| After | 418,440 | 10,720 (99.0%) | 108 | 0 | 0 |

Reading the tail recovered 1,153 of the 1,357 misses and reading the percent
sign recovered a further 96, leaving 108. Each half was measured on its own:
the tail fallback is switched off by an environment check added for the run and
removed after it, and the percent attempt was added afterwards, so the three
rows 1,357, 204 and 108 are three runs of the same comparison over the same
gold set.

The fix also costs noise, and the cost was measured rather than assumed. 4,671
candidates exist after it that did not exist before, 1,249 of which found a
stored result. Every one of the 4,671 was classified by the shape of the cell
it came from:

| Shape | Count |
| --- | --- |
| A value and a bracketed interval or spread | 3,303 |
| A value and a plus-minus spread | 935 |
| A percentage | 388 |
| A cell holding more than one value (`0.92±0.00 / 0.94±0.00`, `2.88±3.00 Å&2.28±3.30 Å&11.86±7.72 Å`) | 45 |

The last row is the known acceptance: the pass reports the first number and
carries the rest of the cell verbatim in `uncertainty_printed`. Forty-five
cells in 418,440 is the rate. No cell of the form `12 (of 30)` or `3 (see
note)` appeared in the sample, which is the shape that would have made this
fallback a liability.

`npx tsc --noEmit` is clean and the eight tests in
`tests/omics-extract-grid.test.ts` and `tests/omics-extract-sheet.test.ts` pass
unchanged, run one file at a time with
`--pool=forks --poolOptions.forks.minForks=1 --poolOptions.forks.maxForks=1`.

Candidate files are a function of the archive and the store, so this change
moves them. The 23,042 candidates the earlier demonstration run reported over
20 sources is not the number those sources produce now.

## The verdict

**On reading values out of a document, the new extractor is better than the 115
scripts, and the evidence is strong enough to act on.** It agrees with them on
99.0% of the cells both can see, disagrees on none, invents nothing in 418,440
candidates, and every candidate carries a span a stranger can open and check,
which no stored result produced by the old scripts was required to carry.

**It cannot rebuild the store, and not because of anything measured above.** Of
the 10,720 candidates that found a real stored result:

| Field | Decided | Share |
| --- | --- | --- |
| `metric` | 3,083 | 28.8% |
| `direction` | 3,083 | 28.8% |
| `model` | 2,831 | 26.4% |
| `unit` | 548 | 5.1% |
| `assessment` (the benchmark or task) | 0 | 0% |
| Complete: every field decided | 0 | 0% |

**The single thing that would change that is `assessment`.** It is decided zero
times in 10,720, and a result record cannot be written without one. The other
four fields could each be decided perfectly and the count of records this
command can write would still be zero. The reason is in the data: a table
caption is a sentence and a benchmark record has a name, and exact label
matching cannot get from one to the other. Every one of those 10,720 questions
is already written down, with the caption it would be decided from, in each
batch's `extract/questions.jsonl`.

Necessary, not sufficient. `assessment` is the field sitting at zero, so
nothing can be written until it moves, but a stage that reads a caption would
have to settle `metric` and `unit` on the same read: `metric` is decided on
28.8% of these cells and `unit` on 5.1%, and both are needed by a record.
Deciding the caption unblocks the gate; it does not finish the record.

So: good enough to rebuild the values of the store with, under a stage that can
read a caption. Not good enough to rebuild the store with on its own, today.

## What this leaves changed

| Path | State |
| --- | --- |
| `shared/omics/extract/value.ts` | New. The cell reader both passes now call. |
| `shared/omics/extract/grid-pass.ts` | Calls `readCellValue` instead of `parseCell`. |
| `shared/omics/extract/sheet-pass.ts` | Calls `readCellValue` instead of `parseCell`. |
| `shared/omics/extract/index.ts` | Exports `readCellValue`. |
| `scripts/omics/extract/measure-store-spans.ts` | New. Stage one of the join: every stored locator to a span. |
| `scripts/omics/extract/measure-vs-store.ts` | New. Stage two: the extractor over the gold set, and the join. |
| `maintenance/reports/extract-vs-store-2026-11-19.md` | This file. |

The harness was written under `workbench/`, which `.gitignore` excludes, and
then moved under `scripts/` so that the commands above run on a fresh clone.
Neither has an `npm run` entry; both take their paths as arguments and write
only where told. `scripts/omics/extract/tables.ts`,
`scripts/omics/extract/batch.ts`, `docs/collection.md` and
`docs/adr/0002-claim-extraction.html` were read and not changed. The fifth
command is still undescribed in `docs/collection.md`.

`git status --porcelain data/entities data/evidence data/provenance` is empty.
No record was written, read back or rewritten, and `npm run records -- add` was
not run.
