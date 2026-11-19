# Candidate header rows in the table grids

A table whose markup marks no header row has no heading in its grid, so a
resolver cannot name a column in it. 2,506 stored locators are refused
`column_not_found` for that reason alone. This records a candidate header row
for those tables, in a field of its own, and measures how often the rule that
chooses one would be wrong.

Every number below has the command that produced it. No model was called at
any point.

## The generated file this changed

`data/omics/layers/registry.jsonl`. 10 of its 2,595 rows changed, every one of
them an `html-table-grid@1` row whose layer gained a candidate header and
whose hash therefore moved. The other 274 grid layers hash exactly as before,
because a table with no candidate serialises to the bytes it did before the
field existed. `data/omics/layers/unsupported.jsonl` is byte identical.
`npm run layers -- check` reports `2595 layers reproduce`.

Nothing under `data/entities`, `data/evidence` or `data/provenance` changed.

| Source | Layer before | Layer after | Bytes |
| --- | --- | --- | --- |
| `evidence-discovery-final-perturbench` | `07cf456ac8` | `36086928f3` | 63,952 to 64,335 |
| `lit-otheromics-20261011-pepspecbench-source-yang2026` | `0a5ad33818` | `3d6c01fb62` | 102,347 to 102,784 |
| `lit-otheromics-20261011-msgwild-source-liu2026` | `3172acbffa` | `ef58b9fc72` | 57,138 to 58,011 |
| `evidence-discovery-final-geneb` | `6e7faf4f29` | `5b9a5f5627` | 108,497 to 108,620 |
| `evidence-discovery-final-nabench` | `73e28e6144` | `79de109e85` | 211,569 to 212,835 |
| `coverage-source-metagene-paper-v1` | `83b2238461` | `63bb6383c5` | 58,955 to 59,248 |
| `evidence-discovery-final-dart` | `badeff0390` | `0bd6a41eaf` | 224,346 to 226,822 |
| `evidence-discovery-final-pfmbench` | `c6190cb7b3` | `99bd05c439` | 181,032 to 181,590 |
| `coverage-source-mimic-2026-v1-html` | `dbdaff12d3` | `944c622571` | 71,963 to 72,583 |
| `lit-cells-networks-20261011-perturbench-v4-source-wu2025` | `f5624382b2` | `9a918eed90` | 128,240 to 128,596 |

## What was added

One field on a grid table, `inferred_header`, holding the rule that chose it,
how many rows it covers, which is always 1, and one heading path per column in
the same shape the marked `headers` uses.

```
"inferred_header":{"headers":[["Model"],["AUPRC"],["AUROC"]],"rows":1,"rule":"first-row@1"}
```

`header_rows` and `headers` are untouched and still hold only what the markup
wrote, so `header_rows` is 0 on every table that carries a candidate. A reader
can always tell a marked header from an inferred one, and a resolver that will
not act on an inference ignores one field. Nothing reads `inferred_header`
today: `grep -rn inferred_header` finds it only in
`shared/archive/layers/grid`, so span resolution is exactly what it was before
this change, which is also why this report measures availability and not
resolution.

The field is absent rather than null where there is no candidate. That is what
keeps the other 274 grid layers hashing the same, and it means a reader cannot
mistake a table the rule declined for a table it has not looked at: the rule is
in `shared/archive/layers/grid/header.ts` and gives the same answer on the same
table bytes.

| Path | What it is |
| --- | --- |
| `shared/archive/layers/grid/header.ts` | The rule, its two predicates and the ten reasons it declines |
| `shared/archive/layers/grid/types.ts` | `GridInferredHeader`, and the field on `GridTable` |
| `shared/archive/layers/grid/tables.ts` | Calls the rule, and only where `header_rows` is 0 |
| `shared/archive/layers/grid/grid.test.ts` | 36 tests, 13 of them this change |

## The rule

The candidate is always the first row of the table, and it is recorded only
when all of this holds. The reason each test exists is in `header.ts`.

1. The markup marks no header cell anywhere in the table unless it marks one
   on the first row, and it wrote no `thead` the first row is not in. Markup
   that says where the header is wins.
2. Three columns and three rows.
3. The first row writes its own cell in every column, each spanning one row
   and one column.
4. Every cell of the first row prints something, except that the first column
   may be the blank corner over a stub.
5. No cell of the first row prints a value.
6. No heading is printed twice.
7. Some column prints values below the first row: at least two of them, and at
   least half of what that column prints.
8. The row under the first row prints a value.

Tests 2, 5, 6, 7 and 8 were each added because of a measured false positive,
and the figures for dropping any of them are below. Test 6 removed four of the
first ten: a row reading `Del`, `Dup`, `Del`, `Dup` and one reading
`Pre-filter`, `Post-filter`, `Pre-filter` are data under a two level header,
not a row of headings.

A value is a number as a paper prints one, or the mark a table uses where it
has no number. The test is whole string and not a prefix, which matters: a
heading often begins with a digit, as "19,237 raQTLs", "length 100" and
"10-cl./binary" all do, and the loose version of this test is where every
serious false positive came from.

## The primary result: how often the rule would be wrong

The ground truth is the 829 tables whose markup does mark a header. Two tests
on them, and the second is the stronger one.

**The rule against the marking.** Run the rule on those tables with the
marking ignored, and compare what it names with what the markup marks.

| | Tables |
| --- | --- |
| Marked tables | 829 |
| Rule names a row | 382 |
| of which exactly the rows the markup marks | 379 |
| of which the first row of a header the markup marks as two rows | 3 |
| Rule declines | 447 |

It never names a row the markup leaves out of its header, and that is by
construction rather than a finding: the rule only ever names the first row and
a marked header always starts there, so this test cannot catch a data row read
as headings. The test below is the one that can. The 3 are a loss of
the deeper levels rather than a wrong row, and in two of the three the second
marked row is a summary line the markup put inside the `thead`, a row reading
`Overall (macro)`, `+0.012`, `4/6` in one and `Pathogen-Detect (avg.)` and
five numbers in the other. The third is a row of direction arrows. Because the
first row of those tables writes an unspanned cell per column, each heading the
rule records still belongs to exactly one column, so a locator naming the top
level reaches the right column and a locator naming a deeper level is refused
as it was.

**The rule against the body.** Strip the marked header rows away and run the
rule on what is left. Every row it could name there is a data row read as
headings, which is the failure this lane most needs to avoid: a wrong heading
makes a resolver name the wrong column and commit to a plausible wrong value.

| | Tables |
| --- | --- |
| Stripped bodies the rule can run on, three columns and three rows | 714 |
| Rule names a row | 1 |
| Rate | 0.14% |

The one is a table whose first body row is `learning rate`, `Pearson (R)`,
`Spearman (SP)` and four more names, a line of column names the markup left
out of its `thead`.

## What the looser value tests cost

Four variants, the same geometry tests with the value test swapped, measured on
the same tables. "Begins with a digit" is the obvious cheap predicate and it is
the one to refuse.

| Value test | Stripped bodies taken | Marked tables agreed | Unmarked tables with a candidate | Locators made available |
| --- | --- | --- | --- | --- |
| whole string, both tests (what ships) | 1 of 714, 0.14% | 379 | 50 | 860 |
| begins with a digit, test 7 only | 2 of 714, 0.28% | 380 | 50 | 860 |
| begins with a digit, test 8 only | 2 of 714, 0.28% | 381 | 51 | 884 |
| begins with a digit, both | 16 of 714, 2.24% | 395 | 64 | 1,163 |

The last row buys 303 locators at sixteen times the false positive rate, and
what it takes includes a row of measured values reading `Listeria
monocytogenes`, `8.90E-1`, `8.97E-1` and more of the same, which is exactly
the shape that would put a plausible wrong number on a record.

Dropping test 2, the three column floor, was measured the same way: it adds 2
unmarked tables with a candidate and 2 more stripped bodies taken, and of those
four tables two are the first line of a two column hyperparameter list and two
are real heading rows. A two column table is as often a list of keys and values
as a headed table and the rule cannot tell them apart, so it does not try.

## Availability

What the 2,506 refusals now have. These are the locators that
`npm run spans -- measure` refuses `column_not_found` where the grid it read
records 0 header rows, from the run that reproduced the 2026-11-18 measured
state exactly: 52,278 locators, 11,360 resolved, `column_not_found` 12,012 and
`no_column_geometry` 10,296. They name 36 tables across 8 text layers, which is
why so few tables carry so many refusals.

| The table the locator names | Locators |
| --- | --- |
| now carries a candidate header | 860 |
| first row does not write a cell per column | 870 |
| no column prints values below the first row | 351 |
| the row below the first row prints no value | 156 |
| fewer than three rows | 101 |
| a cell of the first row spans rows or columns | 84 |
| a cell of the first row after the first is blank | 84 |
| total | 2,506 |

860 of 2,506, 34.3%. That figure is availability and not resolution: whether a
locator resolves against a candidate heading is the resolver's to measure, and
no resolver reads the field yet. The 860 is not the 860 spans the phase 3 plan
estimated, which was 2,506 times the measured 34.5% conversion; the two numbers
agree by coincidence and count different things. At that same conversion these
860 would be about 300 spans.

Over the whole archive rather than the refused locators:

| | Tables |
| --- | --- |
| Tables in the grids | 1,156 |
| Markup marks a header | 829 |
| Markup marks none | 327 |
| of those, now carry a candidate | 50 |
| Layers holding at least one candidate | 10 |

Why the other 277 do not, in the rule's own words:

| Reason | Tables |
| --- | --- |
| `too_few_columns` | 152 |
| `too_few_rows` | 68 |
| `no_column_of_values_below` | 21 |
| `first_row_incomplete` | 18 |
| `row_below_prints_no_value` | 7 |
| `first_row_spans` | 5 |
| `first_row_blank_cell` | 2 |
| `first_row_prints_a_value` | 2 |
| `marked_elsewhere` | 2 |

One caveat on that table. It is counted by running the rule over the committed
grid bytes, which do not record whether the markup wrote a `thead`, so a table
declined `marked_elsewhere` for a `thead` is counted under whichever later
test it also fails. The 2 is a floor and one of the rows below it may be one
too high. The 50 candidates are read from the layer itself and are not
affected.

The two largest are tables that are not results tables at all: a one or two
column list, a rendered equation, a JSON or CSV block an arXiv page prints
inside a table. The 870 locators refused `first_row_incomplete` and the 84
refused `first_row_spans` are the opposite case, a header with more than one
level whose top row spans its children, and those stay refused on purpose: the
column is named on the deeper level and one row cannot carry it.

The 351 refused `no_column_of_values_below` are one shape worth naming. They
are arXiv pages that print each cell twice, once rendered and once as the
LaTeX that produced it, so one cell reads `0.020±3×10-40.020\pm 3\times
10^{-4}` as a single string and no whole string number test accepts it. Their
first rows are plainly headings. A looser test takes them and takes data rows
with them, as the table above shows, so the gain there belongs to a cell text
that is not doubled rather than to a weaker rule.

One thing for the resolver lane: 101 of the 2,506 point at a table of one row
holding a rendered equation, 60 of them at one table. A locator naming a table
of results reaching an equation block is the caption window choosing the wrong
table, not a header problem.

## Determinism

The grid stays a function of the input bytes. The rule reads only the cells
the markup wrote, its two predicates are regular expressions over the cell
text, and it reads no clock and no locale. `npm run layers -- check`
regenerates all 2,595 rows and reports them byte identical, and
`shared/archive/layers/grid/grid.test.ts` asserts that a table with no
candidate writes no field at all and that a table with one round trips through
its own bytes.

## Commands

```
npm run layers -- build      # regenerate the registry, 61 s
npm run layers -- check      # regenerate and compare, byte for byte
npx vitest run shared/archive/layers/grid/grid.test.ts --pool=forks --poolOptions.forks.minForks=1 --poolOptions.forks.maxForks=1
npx vitest run tests/omics-layer-registry.test.ts --pool=forks --poolOptions.forks.minForks=1 --poolOptions.forks.maxForks=1
```
