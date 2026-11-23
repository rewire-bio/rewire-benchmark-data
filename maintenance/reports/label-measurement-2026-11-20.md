# Label stage: measured answers, 2026-11-20

The label stage decides one field: which benchmark or task a table reports. This report is the
stage asked for real, scored against the answers frozen in
`label-evaluation-2026-11-19-heldout.tsv` before any answer existed.

## Read the two sections apart

The pre-filter that puts records in front of the stage is two rules, and they bound different
things. `cites_this_source` holds where the store already records that a record names this
source, which is true only of sources somebody has already extracted. `name_in_table` holds
where the words of a record's name are printed in the table, and it is the only rule that can
reach a paper nothing in the store points at.

Each rule has its own section below, its own denominators and its own run of questions. The
first section's numbers do not apply to a new source and must not be quoted as if they did.

## What it cost

| Item | Value |
| --- | --- |
| Questions asked | 147 |
| Cap this run was given | 152 |
| Askable questions the cap left unasked | 0 |
| Input tokens | 295898 |
| Output tokens | 20758 |
| Tables in the frozen set | 115 |
| Frozen tables this build reproduced | 115 |
| Transport failures, which are a job fault and not a stage result | 0 |

## Both pre-filter rules: a source the store already cites

Rule: `cites_this_source or name_in_table`.

### Does the shortlist hold the right answer at all

Denominator: the 115 tables of the frozen set this build rebuilt.

| Outcome | Rate |
| --- | --- |
| Shortlist holds a truth record | 113 of 115, 98.3 percent |
| Shortlist offered records, none of them right | 2 of 115, 1.7 percent |
| Shortlist offered nothing, so nothing was asked | 0 of 115, 0.0 percent |
| Shortlist miss, the two above together | 2 of 115, 1.7 percent |

### What the stage answered

Denominator: the 109 questions asked under this rule.

| Outcome | Rate |
| --- | --- |
| Correct label | 15 of 109, 13.8 percent |
| Wrong label | 2 of 109, 1.8 percent |
| Abstained | 75 of 109, 68.8 percent |
| No label: the answer was refused, or the transport failed | 17 of 109, 15.6 percent |

Questions about a table reporting more than one assessment: 43 of 109.
No single label can be right on one of those and abstaining is the only correct answer; the stage
abstained on 42. Those abstentions are counted in the abstained row above and not in the
correct row, so the correct rate is labels only.

Refusals by reason:

| Reason | Count |
| --- | --- |
| `confidence_unjustified` | 16 |
| `quote_unresolved` | 1 |

Questions this rule could have asked but the cap did not reach: 0 of 109.

## The lexical rule alone: a source nothing in the store points at

Rule: `name_in_table`.

### Does the shortlist hold the right answer at all

Denominator: the 115 tables of the frozen set this build rebuilt.

| Outcome | Rate |
| --- | --- |
| Shortlist holds a truth record | 24 of 115, 20.9 percent |
| Shortlist offered records, none of them right | 19 of 115, 16.5 percent |
| Shortlist offered nothing, so nothing was asked | 72 of 115, 62.6 percent |
| Shortlist miss, the two above together | 91 of 115, 79.1 percent |

### What the stage answered

Denominator: the 43 questions asked under this rule.

| Outcome | Rate |
| --- | --- |
| Correct label | 0 of 43, 0.0 percent |
| Wrong label | 5 of 43, 11.6 percent |
| Abstained | 32 of 43, 74.4 percent |
| No label: the answer was refused, or the transport failed | 6 of 43, 14.0 percent |

Questions about a table reporting more than one assessment: 24 of 43.
No single label can be right on one of those and abstaining is the only correct answer; the stage
abstained on 21. Those abstentions are counted in the abstained row above and not in the
correct row, so the correct rate is labels only.

Refusals by reason:

| Reason | Count |
| --- | --- |
| `confidence_unjustified` | 6 |

Questions this rule could have asked but the cap did not reach: 0 of 43.

## What this run could not do

It wrote a report. It holds no path to the record store: every file it wrote is under the
report directory, the only record-store function it imports is `readKind`, and the job that
runs it holds a read-only token. `tests/omics-extract-label-measure.test.ts` checks the first
two against this command's own source.

