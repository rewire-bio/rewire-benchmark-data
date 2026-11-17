# Measurements against three ADR open questions, 2026-11-17

Three of the open questions in ADRs 0002 and 0005 were posed as owner judgements but are
empirical. They were measured at store commit `7818ff6`, 93,187 records, read-only. Two of the
three break a figure printed in the records; both corrections are applied in the pages and noted
there, and this report is what they cite.

No record, vocabulary file or check was changed by this work.

## 1. The ratchet costs far more than the record says (ADR 0002, question 2)

ADR 0002 estimated that option (a), the ratchet as shipped in `tests/checks-baseline.test.ts`,
would force a baseline update on "roughly one PR in five". Measured by running the current check
pack at each pull request's first parent and at its merge:

| Denominator | Would fail the ratchet |
| --- | --- |
| Result-adding pull requests | 13 of 14, 93 percent |
| Evidence-adding pull requests (evaluation, result or claim) | 13 of 19, 68 percent |
| All store-touching first-parent merges in the window | 13 of 23, 57 percent |

The estimate was wrong by a factor of about four. Each failing pull request would need a median
rise of 95 findings, ranging from 4 (#173) to 1,432 (#172).

Method: `data/entities`, `data/evidence` and `data/vocab` were extracted per commit with
`git archive` into a scratch directory, with no checkout, and the current pack was run over each
snapshot. Those are the only paths the pack reads. The window starts at the shard migration
(#147, 2026-10-14), because an earlier store reads as about 9,700 records under the current
reader, which gives 23 store-touching merges over five weeks rather than 30. The method
reproduces the pinned baseline exactly at HEAD (10,754 findings: C1 5,391, C2 1,256, C3 3,436,
C4 338, C5 146, C9 187, C13 0), so the pack behaves as shipped. The six passes are small
claim-only or entity-only pull requests, median 6 new records, plus #157, whose 305 new results
happened to produce a byte-identical finding set.

Which rule did the failing, over the 19 evidence-adding pull requests: C1 minority-unit 9,
C2 asserted-where-none 8, C3 unparseable-printed 8, C4 verdict-or-vendor-token 8,
C5 column-splits-comparability-key 5, C3 printed-is-rounded 2, and one each of
C2 unknown-where-declared, C2 opposite, C3 numeric-is-the-second-number. Seven rules never rose
on any evidence pull request: C1 unit-scope-note, C2 metric-not-a-concept, C3 differs,
C3 rescaled-by-100, C3 numeric-not-a-number, C9 same-artifact-and-url, C13 would-be-rewritten.

C1 is not the cause. Strike C1 from the pack entirely and the same 13 pull requests still fail;
4 of the 13 had no C1 rise at all.

The cost of the other branch is also measured. The store went from 7,728 findings at 73,362
records (#160, 2026-10-14) to 10,754 at 93,187 records, so the backlog grew by 3,026 findings on
19,825 new records in five weeks. ADR 0002 budgets 20 to 40 agent-days of triage over months, so
under option (b) the backlog outruns triage.

That points at a third shape neither option names, and it is what the rule distribution supports:
ratchet the rules that never rose on an evidence pull request, since a rise there is a new defect
rather than inherited convention, and leave the convention-dominated rules (C1,
C2 asserted-where-none, C3 unparseable-printed, C4, C5) advisory with a tracked count. Recommended
over both (a) and (b). It is a change to the test's scope, not to any check.

Unmeasured, and it matters: whether the 13 failures are real defects or inherited store
convention. C1's own 100-row hand audit is still outstanding.

## 2. The unit vocabulary pass is 27 to 36 decisions, not 275 (ADR 0002, question 3)

The record frames the pass as a human decision on each of 275 metric concepts, 2 to 3 days. None
of the 275 carries a unit assertion today. Measured over 52,278 results, all of which carry both
a metric and a unit:

| Bucket | Concepts | Results | Share of the 5,093 C1 findings |
| --- | --- | --- | --- |
| One observed unit store-wide, so a generated line | 230 | | |
| (i) Top unit at or above 95 percent of uses | 140 | 32,783 | 71 |
| (ii) Contested, top unit below 95 percent, 20 or more uses | 36 | 18,566 | 5,014 |
| (iii) Under 20 uses, so the share test cannot apply | 99 | 929 | 8 |

The human part is bucket (ii), and it is smaller than 36. Of those, 25 are purely
percent against fraction against unitless on proportion metrics, 2 are a scale split plus
`unit-unreported`, and 9 are dimensional metrics where several units are legitimate. The 27
proportion metrics turn on one convention question, not 27 independent ones, if the ruling is
made once for all of them.

So the pass is worth committing to, and C1 can become a gate. Three readings qualify that. A
set-valued `allowedUnit` is assumed; if one canonical unit per metric is wanted instead, the 9
dimensional concepts become human decisions too. `unit-unreported` appears as a unit value in 743
results across 17 concepts and must be excluded from any generated set; excluding it moves
`root-mean-squared-error` to kcal/mol 136 against unitless 60, and splits
`mean-absolute-error` across three physical quantities, which suggests that concept is
overloaded and needs splitting rather than a unit. Bucket (iii) would write `allowedUnit` from a
median of 8 uses and 7 concepts from a single result, so some generated lines will be wrong; each
surfaces as a gate failure on the next batch using that metric and costs one vocabulary line to
fix.

Two concepts are contested but invisible in the 5,093, because they have no majority unit at all:
`root-mean-squared-error` and `mean-absolute-error`, 642 results between them.

## 3. Pipeline recipe yield is 23 percent, and the model denominator was wrong (ADR 0005, question 2)

ADR 0005 recommended opening the gate to `model` plus `pipeline` but called the pipeline yield
unmeasured and deferred it to PR 3. Measured:

| | Pipelines (133) | Model checkpoints (29) |
| --- | --- | --- |
| Pinned code or doc location, 40-hex revision | 31, 23 percent (24 in own attributes, 7 only via a cited source) | 13 (9 own, 4 via a source) |
| Weights pin | 0 | 9 |
| No code location at all | 101, 76 percent | 8 |
| Install or invocation text anywhere | 25, all curator prose, no executable line | install 11, invocation 12 |
| Container image | 0 | 0 |
| Pinned source bytes already stored here | 1 of 31 | 13 of 29 |
| Recipe-able with no network call | 0 | 12, across 2 projects |

Pipeline yield at 23 percent is the same order as the 38-of-128 benchmark yield the record
already commits curation to, and the model gate reaches none of it: the 7 pipelines whose pinned
repository belongs to an upstream model point at 3 model records, all `entity_level: family`,
which the record rules inapplicable. So a pipeline recipe duplicates nothing. The gate change is
one array element, so admitting `pipeline` costs nothing and the deferral buys nothing.

Sequencing is the real decision, and it goes the other way: 12 checkpoints are writable from bytes
already on disk, 8 of them with both an obtainable weights pin and a readable how-to, while each
pipeline recipe needs a fetch, a `source_ids` edit and, for 25 of the 31, a review pass first.

Two corrections to the record, independent of the gate decision and verified a second time
against `data/entities` for this report. The 9 weights pins span three projects, not one: 7
bacformer, `finedna-20261101-model-carbon-x`, and `hycell-20261106-model-hycell`. And only 8 of
the 9 are a 40-hex revision; hycell records a `weights_sha256` verified against downloaded
weights, which is a stronger pin of a different kind. Two further bacformer records carry no
revision because the repository returned HTTP 401 on 2026-11-15.

Caveats. Pinned means a revision is recorded, not that it still resolves; confirming that needs
network calls, and the 20.4 percent drift figure for pinned artifacts is why these are not called
resolvable. For the 30 pipelines whose pinned README is unarchived, the only evidence that an
executable how-to exists is the curator's locator prose; measured install text in stored pipeline
bytes is 0. The install and invocation patterns undercount rather than overcount, so an unusual
README style escapes them.
