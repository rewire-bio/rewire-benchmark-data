# Label stage: evaluation against the store's own answers, 2026-11-19

The deterministic extractor leaves one field undecided on every candidate: which benchmark or
task the number belongs to. The label stage is the single judgement stage ADR 0002 decision 5
permits, and it decides that field and nothing else. This report measures it against results the
store already carries a task for, and answers whether it is fit to write records.

Short answer: not yet, and the reason is not the judgement. Three measured facts block it. The
acceptance check on high confidence passes on none of the 66 tables where the right answer is
known, because the catalogue's record names are not the names papers print. The set holds 66
such tables, too few to bound a wrong rate below 4.4 percent even if every answer were right.
And 49 of the 115 tables in the set report more than one assessment, where the only correct
answer is to abstain and where a plausible wrong answer is on the shortlist.

`ANTHROPIC_API_KEY` is not set in this environment, so no question was asked of the judgement and
no answer was scored. Everything below is a bound on the stage, measured from the store, the
layers and the check code. Section 3 says exactly which rates remain unmeasured.

## 1. The held-out set

Selection, in full, with nothing chosen for being easy:

1. Start from all 52,278 stored results and resolve every locator:
   `SPAN_DETAIL=<tsv> npm run spans -- measure`. 18,667 reach a span in a layer the archive holds.
2. Keep the sources whose layer geometry the extractor reads at all: a grid for the layer, or the
   `ooxml-sheet-tsv@1` normaliser, and the layer's sanity verdict not `fail`. 71 sources.
3. Run `extractSource` over each and group the candidates into tables exactly as the stage does,
   with `tablesOf`. 336 tables.
4. Ground truth for a table is the set of assessments reached through the evaluation of every
   stored result whose span falls inside that table's extent in the same layer. Nothing else in
   the store says which table a result came from.
5. Keep every table with at least one such result. 115 tables, 10,789 results, 58 sources.

Nothing was dropped after step 5. Tables at the shortlist cap, tables carrying forty-nine
assessments, tables whose caption prints twice and tables with no caption at all are all in.

The frozen set is `label-evaluation-2026-11-19-heldout.tsv` beside this file, one line per table,
with the scored answer written into the `scored_answer` column before any answer existed. A live
run must be scored against this file, not against a regenerated one.

### Where the other results went

| Stage | Results |
| --- | --- |
| Stored results | 52,278 |
| Locator resolves to a span | 18,667 |
| In a source whose layer geometry the extractor reads | 11,097 |
| Inside a table extent, so the stage can be asked about it | 10,789 |
| Same layer, outside every table extent | 18 |
| Layer holds no table the extractor builds | 290 |

The 7,570 that fall out at the third line are `delimited_cell` 2,983, `table_cell` 2,591,
`json_value` 1,845, `quote` 146, `figure_caption` 4 and `page` 1. They resolve to real spans and
are out of this stage's reach because no table was built around them.

The brief named 10,828 results sitting on a cell the extractor can place. This build measures
10,789 inside a table extent. The 39 are a difference between builds, not a disagreement about
what counts: the span resolvers moved between the two runs. The dump this evaluation was first
drafted against held 11,410 resolved locators; the one it now reads, regenerated on this tree,
holds 18,667.

### Class spread

| Cut | Spread |
| --- | --- |
| Tables | 115 over 58 sources |
| Results | 10,789 |
| Truth records | 416 distinct, no benchmark among them; across tables, 409 protocol mentions and 19 task mentions |
| Layer normaliser | `europepmc-fulltext-xml@1` 65, `ooxml-sheet-tsv@1` 48, `html-text@1` 2 |
| Locator class of the results | `table_row_col` 4,444, `identifier_column` 2,597, `line_addressed` 1,462, `sheet_cell` 983, `table_unquoted_row` 673, `table_no_row_keyword` 520, `other` 110 |
| Cells per table | min 6, median 63, p90 360, max 9,603 |
| Results per table | min 1, median 48, p90 218, max 1,410 |
| Anchor text | caption 65, bare label 48, none 2 |
| Assessments per table | 1 on 66 tables, 2 on 16, 3 on 4, 4 on 6, 5 on 1, 6 on 6, 7 on 1, 8 on 6, 10 on 2, 12 on 1, 18 on 1, 22 on 1, 24 on 1, 26 on 1, 27 on 1, 49 on 1 |

One bias to hold on to: the set is sources the frozen Python scripts parsed cleanly enough for a
locator to resolve, which over-represents tidy tables. It does now cover supplementary workbooks,
48 of the 115 tables, which the earlier measurement on a stale dump did not.

## 2. The live run

`ANTHROPIC_API_KEY` is absent here, so the stage asked nothing and no answer exists to score. No
figure in this report comes from a judgement.

Running the real stage over all 336 tables with an empty recording gives the exact shape of the
run a key would buy. Every question that would be asked comes back as `transport_failed`, which
is how the count below is exact rather than estimated.

| Fact | Value |
| --- | --- |
| Tables | 336 |
| Questions a live run asks | 287 |
| Refused before asking | `no_anchor_text` 49 |
| Refused for an empty shortlist | 0 |
| Refused because the pass had already decided | 0 |
| Question size, characters | min 543, median 1,233, p90 2,364, max 3,536, total 406,189 |
| Prompt bytes sent with each question | 2,907 |
| Model identifier on the receipt | `claude-opus-5-5` |
| Effort | `low` |
| `max_tokens` | 2,000 |
| Reply fields | `record_id`, `quote`, `confidence`, `reason` |

Cost is unmeasured. No call was made, so no spend was observed, and this report does not quote a
price it did not pay.

## 3. Rates

What a live run would be scored on, written down now so it cannot be scored more gently later.

- Per table, single-assessment truth: correct is that id, wrong is any other id, refused is `none`
  or any acceptance check failing.
- Per table, multi-assessment truth: correct is `none`. Any named id is wrong, including one of
  the truth ids, because the label applies to every candidate in the table and most of them
  belong to a different assessment.
- Per result: a label on table T is correct for a result in T whose truth is that id, and wrong
  for every result in T whose truth is not. Result-level wrong is the number that matters,
  because that is the count of corrupt records.

Measured now:

| Rate | Value |
| --- | --- |
| Shortlist miss, both rules, all tables | 2 of 115, 1.7 percent |
| Shortlist miss, both rules, single-assessment tables | 0 of 66 |
| Shortlist miss, lexical rule alone, all tables | 91 of 115, 79.1 percent |
| Shortlist miss, lexical rule alone, single-assessment tables | 59 of 66, 89.4 percent |
| Shortlist empty, lexical rule alone | 72 of 115 |
| Refused before any question, whole population | 49 of 336, 14.6 percent |
| Whole caption resolves to one span, held-out set | 100 of 109 anchored tables; 9 refuse `quote_ambiguous` |
| Right answer accepted at `medium`, oracle pass | 61 of 66 |
| Right answer accepted at `high`, oracle pass | 0 of 66 |

Unmeasured, and only a live run can measure them: the correct rate, the wrong rate, the
abstention rate, confidence calibration, and cost. Nothing here stands in for them. No heuristic
was built to pick an id, because its rates would read as the stage's and would not be.

### The oracle pass, and what it found

The oracle pass feeds the known-right record id into the real `checkAnswer`, with the best quote
the caption can supply, at `medium` and at `high`. It chooses no id and simulates no judgement:
it measures whether a right answer can get through the checks at all.

61 of 66 single-assessment tables accept the right answer at `medium`. The other 5 refuse
`quote_unresolved`: their caption prints more than once in the layer, so quoting it earns no span.
That is a refusal in the intended direction and it costs 601 results.

None of the 66 accepts the right answer at `high`, and the cause is the same every time.
`confidence_justified` requires the quoted words to contain the record's printed name, and no
caption in the held-out set contains one. The clearest case is
`dna-pathogen-20261009-protocol-hall2024-mtb-reads-real-illumina`, whose printed name is
`M. tuberculosis read classification, real Illumina (Hall and Coin 2024 Table 8)` against a
caption reading `Performance of M. tuberculosis read classification`, then a dash, then
`real Illumina`. The subject matches word for word; the name does not occur, because the
catalogue punctuates it differently and carries a citation the paper's caption does not print.
Elsewhere the gap is wider: the catalogue names a protocol `Feng Yeast H3K14ac sequence
classification` where the paper's caption prints neither "Feng" nor "sequence classification".
`quoteNamesRecord` asks for containment of the whole normalised name, so a pass is unreachable
here by construction, not by accident.

That makes the check a tautological refusal rather than a gate: an acceptance rule written around
`high` accepts nothing. It is safe, and it is not informative. Either the check compares against
the record's distinguishing words rather than its full constructed name, or `high` stops being
what acceptance is gated on. That decision has to be made and re-measured before the rule in
section 5 can use confidence at all.

## 4. Where a wrong label would come from

Causes, counted as exposure on the held-out set, since no wrong label exists yet to read.

| Cause | Exposure |
| --- | --- |
| Two or more assessments in one table | 49 of 115 tables, 6,802 of 10,789 results |
| Those whose truth records share a parent that is on the shortlist | 30 of 49 |
| A near-twin of the right record on the shortlist | 28 of 66 single tables, 1,707 results |
| Ambiguous caption, right answer cannot earn a span | 9 of 115 tables; 5 of them single-assessment |
| Shortlist missed the right record | 2 of 115, both at the cap of 15, both multi-assessment |
| Right record absent from the store | 0 by construction, and unmeasurable here |

The multi-assessment row is the serious one, and the shared-parent count is why. On 30 of the 49
multi-assessment tables the truth records share a parent and that parent is on the shortlist. A
plausible, fluent, well-quoted answer naming the parent is available on every one of them, and it
is wrong: the table's results belong to the children, the label would travel to all of them, and
the receipt would read as a check that passed. The prompt does tell the stage to answer `none`
when a table reports more than one benchmark, which is the right instruction, but an instruction
is not a check, and nothing in `check.ts` catches this today.

It can be caught. A refusal that drops any answer naming a record with two or more of its own
children on the same shortlist fires on all 30 of those tables and on none of the 66
single-assessment ones, so it costs no coverage on this set. That measurement is the
`parent_of_two_fires` column of `label-evaluation-2026-11-19-confusable.tsv`. It is a proposal,
not code: nothing in `check.ts` reads it yet.

Near-twins are the second cause and have no proposal behind them. 28 of 66 single tables offer
the stage at least one sibling sharing 60 percent or more of the right record's content words:
`Feng Yeast H3K4me1 sequence classification` against the H3K4me2 protocol beside it, and so on.
The checks cannot separate those, because both are on the shortlist, both are the right kind and
both accept the same quote. 1,707 results sit in those tables.

The two shortlist misses cost nothing under the scoring rule. Both are multi-assessment tables
where the correct answer is `none`, and both sat at the cap of 15. No single-assessment table in
the set was missed.

The last row matters for honesty about what this set can prove. Every truth record in it is a
record the store holds, so the set cannot measure a label attached to a record that is not there.
For a source nobody has extracted, that case is common and this evaluation says nothing about it.

## 5. The decision rule to ship

The rule follows from the rates, and the first thing the rates say is that automatic acceptance
is not available yet.

**Write nothing automatically today.** Three conditions, each measured above:

1. The `high` confidence gate accepts 0 of 66 tables where the answer is known right. An
   acceptance rule built on it writes nothing; one built on `medium` is gated on a field the
   measurement shows is not discriminating anything.
2. With 66 single-assessment tables, zero observed wrong labels bounds the table-level wrong rate
   at 4.4 percent with 95 percent confidence, by the rule of three. At the median of 28 results
   per single-assessment table that is about 80 corrupt results consistent with a perfect run.
   Certifying a wrong rate at or below 1 percent takes roughly 298 single-assessment tables with
   none wrong, and this archive offers 66.
3. 30 tables offer a wrong answer that passes every check that exists. The refusal that would
   catch them is measured in section 4 and is not written.

**What the stage is for in the meantime.** A label becomes a queued proposal, written to
`extract/stages/label.jsonl` with its shortlist, quote, span and checks, and a person or a second
pass promotes it. That is what the stage already does: it writes no record and nothing into
`candidates.jsonl`. The decision is to leave it that way.

**The rule to ship once the wrong rate has been measured**, stated now so the live run is scored
against it rather than around it. Accept a label automatically only when all of:

- the chosen record reached the shortlist by the `cites_this_source` rule, not the lexical rule
  alone, so the store already connects the record to the source;
- the quote resolves to exactly one span in the source's own layer, which is already a check and
  which refuses 9 tables here;
- no two children of the chosen record are on the same shortlist, which catches 30 of 49
  multi-assessment tables at no measured coverage cost and is not yet code;
- no other shortlist entry shares 60 percent or more of the chosen record's content words, which
  is the near-twin measure and is not yet code;
- and the live result-level wrong rate on this held-out set, extended to at least 300
  single-assessment tables, is zero.

Everything else stays unlabelled. On the current set the last condition is the binding one and it
cannot be met from this archive, so the rule's honest form today is: queue everything, write
nothing.

## 6. Can the store be rebuilt with this

Not as a whole, and the subset is smaller than the shortlist numbers suggest.

| Boundary | Results | Share of 52,278 |
| --- | --- | --- |
| Locator resolves to a span | 18,667 | 35.7 percent |
| Inside a table the stage can be asked about | 10,789 | 20.6 percent |
| In a table where one answer is the right shape | 3,987 | 7.6 percent |
| In such a table with no near-twin on the shortlist | 2,280 | 4.4 percent |
| And where the right answer can earn a span at all | 2,195 | 4.2 percent |

The last line, 37 tables and 2,195 results, is the subset this stage could label and have the
result be checkable. It is also the subset where the store already holds the answer, so labelling
it rebuilds nothing. It is the subset on which the stage can be scored.

For results the store does not already hold, the binding constraint is the pre-filter, not the
judgement. With the store's own citations stripped, which is what a source nobody has extracted
looks like, the lexical rule alone offers the right record on 7 of 66 single-assessment tables and
offers nothing at all on 72 of 115 tables. The stage cannot name a record it is never shown.

So: the store cannot be rebuilt with this stage. Re-grounding the 18,667 results that already
resolve needs no judgement at all, because their task is already stored, and that work is
unblocked. Extracting results the store does not hold is pre-filter-bound at roughly one table in
ten, and the next work is the pre-filter, with the `confidence_justified` check, the two-children
refusal and a near-twin refusal behind it.

## 7. Commands and generated files

Both commands run from the worktree root. Neither reads a key, opens a transport or writes a
record. The first takes about two minutes, the second about one.

```
SPAN_DETAIL=<scratch>/span-detail.tsv npm run spans -- measure --out <scratch>
npm run extract -- label-evaluate --spans <scratch>/span-detail.tsv \
  --out maintenance/reports --date 2026-11-19
git status --porcelain data/entities data/evidence data/provenance
npx tsc --noEmit
npx vitest run tests/omics-extract-label.test.ts --pool=forks \
  --poolOptions.forks.minForks=1 --poolOptions.forks.maxForks=1
```

`--out <scratch>` on the first keeps it from rewriting the dated span-resolution reports. Without
`SPAN_DETAIL` the span dump is not written and the second command has nothing to read.

Generated files this report leaves changed:

- `maintenance/reports/label-evaluation-2026-11-19.md`, this file, written by hand
- `maintenance/reports/label-evaluation-2026-11-19.json`, every summary figure as data
- `maintenance/reports/label-evaluation-2026-11-19-heldout.tsv`, the frozen held-out set, 115 lines
- `maintenance/reports/label-evaluation-2026-11-19-oracle.tsv`, the oracle pass, 66 lines
- `maintenance/reports/label-evaluation-2026-11-19-confusable.tsv`, near-twin counts and the
  two-children proposal, 115 lines

Code changed to make the measurement reproducible:

- `scripts/omics/extract/label-evaluate.ts`, new, the whole measurement in one command
- `scripts/omics/extract/cli.ts`, the `label-evaluate` subcommand
- `scripts/omics/spans/cli.ts`, three columns added to the `SPAN_DETAIL` dump: `source_ids`,
  `start` and `end`, which are the span the run already committed to. No reported span figure
  changes; `npx tsc --noEmit` is clean and the 34 label tests pass.

`git status --porcelain data/entities data/evidence data/provenance` is empty: no record in the
store was read into, written or moved by any of this.
