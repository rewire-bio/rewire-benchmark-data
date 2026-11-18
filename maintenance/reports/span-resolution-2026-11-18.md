# Span resolution: how much of the store can be re-checked without a reader

ADR 0002 step 5, measured over the store and the archive as they stand on
2026-11-18. Every number has the command that produced it. Nothing here is an
estimate, and no model was called at any point.

## The two numbers, and why they are different

| | Locators | Share |
| --- | --- | --- |
| Stored result locators | 52,278 | |
| Parsed: fully addressed by the grammar | 39,416 | 75.4% |
| Resolved: a span in a layer the archive holds | 5,399 | 10.3% |

`npm run locator -- coverage` gives the first. `npm run spans -- measure` gives
the second. The first says the grammar read the string. The second says a
machine can go to the bytes and look. A locator can parse perfectly and resolve
nothing, and most do.

Of the 5,399 spans, 5,142 print the value the record stores, 95.2%. Counting
only the span kinds that should print a value, 5,112 of 5,246 cell spans print
it, 97.4%, and the 134 that do not are the resolvers' measured error rate.
That is the number that decides whether resolution can gate anything, and today
it cannot: a check wrong on 2.6% of the cases it commits to would reject
correct records.

## What was built

| Path | What it is |
| --- | --- |
| `shared/omics/spans/offsets.ts` | The per-layer index: UTF-16, code point and UTF-8 byte offsets, converted in time proportional to one line |
| `shared/omics/spans/types.ts` | The resolution contract: seven span kinds, 26 refusal reasons |
| `shared/omics/spans/table.ts` | Table cell in column-aligned text, with the caption, window, header, row and cell steps each refusing on their own |
| `shared/omics/spans/figure.ts` | Figure caption |
| `shared/omics/spans/prose.ts` | Quote or sentence, and a numbered paragraph of a named section |
| `shared/omics/spans/regions.ts` | Delimited cell by line, by A1 notation or by composite row keys; line range; page |
| `shared/omics/spans/reanchor.ts` | Moving a stored span onto a rebuilt layer, or refusing |
| `shared/omics/spans/index.ts` | `resolveLocator(parsed, layer)`, which picks the resolver the locator's shape calls for |
| `scripts/omics/spans/cli.ts` | `npm run spans -- measure \| control \| show <result id>` |
| `tests/omics-spans.test.ts` | 35 tests |

Nothing here writes to the store. `git status --porcelain data/entities
data/evidence data/provenance` is empty.

## Offsets: the two systems, proved to agree on real text

A span carries code point offsets, because that is what
`oa:TextPositionSelector` counts, and UTF-8 byte offsets, because that is what
a resolver slices. JavaScript string indices are UTF-16 code units and are
neither. Below the basic multilingual plane all three agree and the problem is
invisible. Above it they do not.

33 of the 440 layers read in the measurement hold at least one code point above
the basic multilingual plane, 3,648 in all. One of them, layer
`012364921e7e6faf...`, a Europe PMC full text carrying a script capital V:

```
span "0.3 a"   code points [22475, 22480)   UTF-8 bytes [22569, 22574)   UTF-16 index 22478
```

Three different numbers for the same five characters. `spanAt` and the layer
registry's own `sliceSpan` return the same code point and byte offsets for that
span, which is the test in `tests/omics-spans.test.ts`, asserted on a fixture
holding an astral character and a combining mark and again on a layer from the
store.

The index exists because the obvious implementation does not finish. Spreading
a layer into an array of code points costs the length of the layer per span,
the longest layer holds 13,778,216 characters, and there are 52,278 locators.
The per-line tables make a conversion cost one line.

## Resolution by locator class

`npm run spans -- measure`, full table in
`maintenance/reports/span-resolution-2026-11-18-by-class.tsv`.

| Class | Locators | Resolved | Resolved % | Value present | Top refusal |
| --- | --- | --- | --- | --- | --- |
| `table_row_col` | 20,540 | 1,624 | 7.9 | 92.4% | `no_column_geometry` 7,113 |
| `table_unquoted_row` | 7,484 | 353 | 4.7 | 96.9% | `no_column_geometry` 4,872 |
| `line_addressed` | 5,785 | 2,960 | 51.2 | 100.0% | `no_column_geometry` 2,336 |
| `identifier_column` | 5,235 | 235 | 4.5 | 100.0% | `no_column_geometry` 2,562 |
| `sheet_cell` | 4,542 | 0 | 0.0 | | `column_not_found` 1,386 |
| `table_no_row_keyword` | 3,125 | 0 | 0.0 | | `no_column_geometry` 1,487 |
| `json_path` | 2,893 | 0 | 0.0 | | `no_resolver_for_kind` 1,845 |
| `figure` | 1,355 | 31 | 2.3 | 87.1% | `no_resolver_for_kind` 588 |
| `other` | 1,087 | 156 | 14.4 | 24.4% | `no_resolver_for_kind` 602 |
| `roman_table` | 224 | 40 | 17.9 | 100.0% | `row_not_found` 116 |
| `dotted_table` | 8 | 0 | 0.0 | | `column_not_found` 8 |
| total | 52,278 | 5,399 | 10.3 | 95.2% | |

The one class that resolves well is `line_addressed`, at 51.2% with every span
printing the stored value. Those are locators into a CSV or TSV the archive
holds as the file itself, where the address is the answer and there is no
geometry to reconstruct.

Resolution against the parse buckets, which is the cross-tabulation of the two
headline numbers: of the 39,416 fully addressed locators 4,955 resolve
(12.6%), of the 3,212 partial 227 (7.1%), of the 8,192 carrying residue 206
(2.5%), of the 1,458 unanchored 11 (0.8%). Parsing fully triples the odds of
resolving and does not come close to assuring it.

## Why the other 46,879 refuse

`maintenance/reports/span-resolution-2026-11-18-by-reason.tsv`. The reasons
partition the 52,278 exactly: 5,399 resolved plus 46,879 refused, each refused
locator carrying one reason, which `tests/omics-spans.test.ts` asserts rather
than observes.

| Reason | Locators | Share | Who can move it |
| --- | --- | --- | --- |
| `no_column_geometry` | 22,528 | 43.1% | the archive lane and this lane, with a table-grid layer and a sheet-block resolver |
| `column_not_found` | 6,267 | 12.0% | nobody cheaply: multi-level headers |
| `no_resolver_for_kind` | 5,090 | 9.7% | this lane, with a JSON Pointer resolver |
| `row_key_unmatched` | 4,001 | 7.7% | the grammar, by parsing composite row keys |
| `row_not_found` | 2,607 | 5.0% | mixed |
| `no_row_in_locator` | 1,711 | 3.3% | the locator author |
| `no_anchor` | 1,294 | 2.5% | the locator author |
| `anchor_not_found` | 1,058 | 2.0% | mixed: the table is in a supplement that is not held |
| `column_ambiguous` | 847 | 1.6% | nobody cheaply |
| `row_ambiguous` | 561 | 1.1% | the grammar, by parsing block selectors |
| `no_capture` | 448 | 0.9% | the archive lane |
| `cell_empty` | 178 | 0.3% | nobody: the cell is blank |
| `quote_not_found` | 130 | 0.2% | mixed |
| `no_column_in_locator` | 126 | 0.2% | the locator author |
| everything else | 33 | 0.1% | |

`layer_not_readable` is zero, and that is a property of this machine rather
than of the work. The full object cache is present here, including the 296
registry rows on restricted objects. On a clean clone the cache is absent by
design, every one of these locators refuses `layer_not_readable` until
`npm run release:fetch` has run, and the denominator of every figure above
changes.

### The largest fact: the columns are gone before a resolver sees the text

22,528 locators address a place the held layer cannot carry. 9,809 of them
sit on a Europe PMC full text and 3,100 on an HTML page, where the table is
present and its columns are not; 6,016 sit on an office layer, which carries
its geometry in sheet blocks that no resolver here reads yet; 2,869 address a
cell or a line of a file against a PDF layer, which is a rendering of the file
and not the file; and 734 address a file layer whose first line carries no
delimiter.

Both the HTML and the JATS normalisers print one cell per line, so the columns
are gone before a resolver sees the text. The fix is a layer that keeps the
table grid, derived from markup that already carries it, which belongs with the
normalisers in `shared/archive/layers` and not with a resolver counting lines
and hoping. A resolver that inferred the column by counting would resolve most
of these and would be wrong on every table with a spanning header, and a wrong
span is worse than no span.

### The second: the file a locator names is not the file the archive holds

7,076 locators name a file by name, and zero of them name a file the archive
holds as a member of the cited source's object. A locator reading
`counts_SGNex_summary.tsv.gz, row Source 'X', Algorithm 'GFSeeker', column
'known'` is well formed, its keys are the file's own column names, and the
archive holds a different object for that source. The keyed-row resolver that
reads exactly this form is built and tested and resolves none of them today.
It will resolve them when the named files are captured, and that is a capture
decision, not a resolver one.

### The third: JSON

2,893 locators are JSON paths, 1,845 refused `no_resolver_for_kind` and 1,048
`no_anchor`. Every one of them has a `text-utf8@1` layer held. An RFC 6901
resolver over a position-recording JSON reader would address all 2,893, which
is the largest win available to this lane and is not built.

## The resolvers refuse rather than guess, and that was measured

Four changes were made after the first full run, each because the measurement
showed a span being returned that was wrong rather than refused. The counts are
from the run that followed each change.

| Change | Effect, measured |
| --- | --- |
| Every part of a composite row key must be printed on the line accepted as the row | table cells 1,516 to 1,426; wrong cells 226 to 92, and 44 rows previously refused as ambiguous were told apart by the key |
| A table row number resolves as a layer line only where the layer is the file itself | 99 line-range spans withdrawn, every one a table row read as a line of a PDF or HTML rendering |
| A header printing the requested column name twice is `column_ambiguous` | table cells 1,426 to 1,415; wrong cells 92 to 86 |
| Column bands compared within the line, not across the layer | table cells 1,415 to 2,251; wrong cells 86 to 133, a fall from 6.1% to 5.9% |

The last of those was a defect rather than a policy. A field's offsets are
into the layer, and the header line and the row line start at different
offsets, so the nearest-column assignment was meaningless whenever the two
lines began in different places.

Two conventions are set rather than inferred, and both are stated in the code.
A table window runs from its caption to the next caption or 200 lines,
whichever comes first, which under-reads a supplementary table longer than 200
lines and reports `row_not_found` on it. `line N` counts physical lines of the
layer from 1, not RFC 7111 records, because the stored locators were written by
people reading files in an editor.

## Re-anchoring, and the rule

A layer is rebuilt when a tool changes, the hash moves, and every stored offset
points at the wrong place. The quote is what survives. The rule, in order, and
the first test that applies decides:

1. The layer hash equals the span's and the characters at the offsets equal
   `exact`: unchanged.
2. `prefix` + `exact` + `suffix` occurs exactly once: relocated, by context.
3. `exact` occurs exactly once: relocated.
4. `exact` occurs more than once: refused, `quote_ambiguous`.
5. `exact` does not occur, even with its internal whitespace allowed to differ:
   refused, `quote_not_found`.

Nothing picks the occurrence nearest the old offset. Proximity is not evidence,
and a span placed by proximity is exactly the silent wrong answer this lane
exists to prevent. Context is tried before the quote alone because `0.412`
occurs many times in a paper and its surroundings do not. Prefix and suffix are
48 code points, as ADR 0002 decision 1 sets them.

Tested on a real layer from the store, perturbed three ways: 64 characters
inserted before the span relocates it by context with the quote identical;
replacing the quote refuses; duplicating the whole layer refuses with
`quote_ambiguous`.

## The round trip: a report, not a gate

ADR 0002's verification table leaves one ruling to this step.
`renderLocator(parseLocator(x)) === x` is to become a gate at 90% when the
resolvers land, or stay a report if the measured figure is below that. It is
below. Over the 39,416 fully addressed locators the 2026-11-17 coverage run
gives 14,432 exact round trips, 36.6%, against 37,780 that re-parse to the same
structure, 95.8%.

So it stays a report. The 36.6% is a measure of how many stored strings happen
to be written in the renderer's canonical spelling, which is a fact about
punctuation and not about addressing, and a gate on it would block correct
locators for their commas. The 95.8% idempotence figure is the one that bears
on the contract inversion ADR 0002 decision 2 asks for, and it is the figure a
later gate should use.

## The control: the 14 value-check files

`npm run spans -- control`. These files record what a reader found at each
locator, and they are the acceptance test ADR 0002 decision 10 names. All 2,432
rows were found in the store, and the four statuses reconcile exactly with the
figures the ADR pins: 867 `in_cell`, 994 `in_row`, 551 `locator_not_parsed`, 20
`row_not_found`.

| Reader's finding | Rows | Resolver returns the value | Resolver returns something else | Resolver refuses |
| --- | --- | --- | --- | --- |
| `in_cell` | 867 | 385 | 32 | 450 |
| `in_row` | 994 | 195 | 37 | 762 |
| `locator_not_parsed` | 551 | 15 | 27 | 509 |
| `row_not_found` | 20 | 0 | 0 | 20, every one `row_not_found` |

Two things to read off it. On the 867 rows where a reader confirmed the value
is in the named cell, the resolver commits 417 times and is right 385 of them,
92.3%, and declines the other 450. On the 20 rows where the reader could not
find the row, the resolver says `row_not_found` on all 20, which is the one
class where the two agree completely.

The 195 `in_row` rows the resolver resolves with the value are cases where the
legacy checker could not place the column and this one can. The 32 `in_cell`
rows it gets wrong are the error rate again, on the subset that has ground
truth.

This cross-tabulation was run and is reproducible, and it is not pinned as a
baseline file. Row-for-row agreement on `in_cell` against `in_row`, which
decision 10 names as the acceptance test for this step, needs the per-row
expectations committed somewhere a test can read, and that is not done.

## What this says about deterministic re-checking at scale

It is possible for one tenth of the store today, and the ceiling is set by the
archive rather than by the grammar. The order of the work that would move it:

1. A table-grid layer for HTML and JATS. 14,766 locators on those two
   normalisers, more than any other obstacle, and the structure is in the
   markup already.
2. Capturing the files locators name. 7,076 locators name a file by name and
   the archive holds none of them under the cited source.
3. A JSON Pointer resolver. 2,893 locators, every one with a layer held.
4. Composite row keys and block selectors in the grammar. 4,562 locators
   refused as `row_key_unmatched` or `row_ambiguous`, where the locator holds
   the information and the parse drops it.
5. A sheet-block resolver over `ooxml-sheet-tsv@1` and `ooxml-document-text@1`.
   6,390 locators now resolve against an office layer the archive holds, and
   all 6,390 refuse: 6,016 `no_column_geometry`, 280 `no_resolver_for_kind`,
   90 `no_anchor`, 4 `quote_ambiguous`. Neither office normaliser is in
   `FILE_NORMALISERS` or `ALIGNED_NORMALISERS`, so the sheet blocks carry
   geometry no resolver reads. The addressing functions exist in
   `shared/archive/layers/office/address.ts` and nothing calls them.

Multi-level column headers, 7,114 locators across `column_not_found` and
`column_ambiguous`, have no cheap fix and should stay refused.

Nothing in this report should gate `records -- add`. The resolvers are wrong on
2.6% of the cell spans they commit to, and a gate at that rate rejects correct
records. What this is ready for is a report and a queue: a locator that
resolves to a span whose text does not print the stored value is a lead worth a
reader's time, and there are 134 of them.

## Commands

```
npm run spans -- measure              # the tables above, 33 s
npm run spans -- control              # the value-check cross-tab
npm run spans -- show <result id>     # one locator, its layers, its span or its refusal
npx vitest run tests/omics-spans.test.ts --pool=forks --poolOptions.forks.minForks=1 --poolOptions.forks.maxForks=1
```
