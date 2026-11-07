# BenchBench-Cloning, independent review

2026-11-06. Batch `data/omics/benchbench-cloning-20261106/`, issue
[#235](https://github.com/rewire-bio/rewire-benchmark-data/issues/235). Reviewed by a Claude
research agent that did not extract the batch, against the extraction frozen at commit `36414d4`.
Not human scientific review. Nothing was reproduced: transcription was checked against the pinned
source, which is not reproduction.

Receipt: `data/omics/benchbench-cloning-20261106/review.json`. Mismatch report:
`data/omics/benchbench-cloning-20261106/value-check.tsv`. Edits:
`data/omics/benchbench-cloning-20261106/review/apply-review.py`.

## Sources and access

| Record | SHA-256 |
| --- | --- |
| `benchbench-cloning-20261106-source-arxiv-v1` | `6f5044b1bbbd81ad86b23cb536e2cae6428e0d9126f11546041355518febdc39` |
| `benchbench-cloning-20261106-source-arxiv-abs` | `f9e233e9c65ab7470e5817defe75e749436122d677da9e540d51b5384100ee65` |
| `benchbench-cloning-20261106-source-benchling-announcement` | `eb67d3c73b14e40232bb5ea7633c64572c893c60b4f22a225320dcbac20354bf` |

All three matched. The archived text layer matters more than usual here, because every stored value
was parsed from it: its own hash matches the `archive_sha256` on the source record, and it
decompresses byte for byte to a `pdftotext -layout` run on the refetched PDF, so the archive is
provably derived from the pinned bytes rather than merely asserted to be.

Access rechecked at review time, not taken from the issue or from `notes.md`. At
2026-11-06T12:33:21Z, `https://github.com/benchling/benchbench-cloning` returns 404 from the web
page and `https://api.github.com/repos/benchling/benchbench-cloning` returns 404 from the REST API;
the arXiv abstract page returns 200. The batch's consequences follow and are correctly applied: the
dataset is not marked openly downloadable, no evaluation is marked reproduced, and `code_licence` is
not inherited from the article's CC BY 4.0.

## How the values were compared

`check-values` reproduced the extractor's figures exactly: 224 of 224 found, 112 `in_cell`, 112
`in_row`, no `wrong_column`, no `overclaimed_in_row`, nothing missing.

All 224 were then re-read by `review/check-cells.py`, written for this pass. It does not use either
of the extractor's scripts, and it differs from both in the one way that matters for this document:
**it locates each table body by that table's own printed header line, not by proximity to a
caption.** Every body in this paper sits above its own caption, so caption proximity is exactly what
goes wrong here. Column order comes from the printed header and each row is split on runs of two or
more spaces, so a cell cannot be taken from a neighbour. Every printed value and every printed
interval matched its own field, with zero disagreements. The only printed cells of Tables D2, G1 and
G2 the batch does not record are Table G1's eight pass@1 cells, which duplicate Table D2's
top-effort protocol-development column and are deliberately not stored twice.

Three arithmetic constraints were re-derived rather than taken from the extractor's assertions, and
all three hold: each of the eight Table G2 columns sums to the printed top-effort construct-design
numerator over 75; each Table G1 Solved-at-least-once count over 50 equals the printed pass@10; and
every Table D2 aggregate equals (50 x protocol + 15 x construct) / 65 within rounding. The single
residue is GPT-6.1 Sol at max effort, where the rounded components give 22.146 against a printed
22.2 and the unrounded construct value 31/75 gives 22.154, which rounds to 22.2. That is the
extractor's explanation and it checks out.

Manual check, concentrated where the coordinator asked. All 16 Table G1 count cells, the set the
extractor's own audit flags as having the value more than once in its row or on another line
starting with the same system label, were read in full by eye against the printed body. A further 20
results were drawn from all 224 with `random.sample` and seed 20261106 and read the same way. All
matched, column assignment included. For the Solved-at-least-once column the eye check is backed by
arithmetic, since the count over 50 reproduces the printed pass@10 for all eight systems; for Solved
all there is no such constraint, which is why reading all eight by eye mattered.

## The repository's table parser answers a different question without erroring

Confirmed, and worth recording beyond this batch. Asked for `Table G1`,
`npm run -s batch -- table` returns Table G2's body: the same 15 task rows and 8 model columns as a
`Table G2` request, with no warning. Asked for `Table D2` it fails honestly, with "fewer than two
body rows".

The cause is the layout. Every table in this paper prints its body above its caption, so between
Table G1's body and Table G2's caption sit both Table G1's caption and Table G2's body. A parser
that searches around a caption for the nearest body finds the wrong one. Table D2 fails instead
because its body sits above the Table D1 caption, leaving nothing adjacent to its own.

This is the third silent-failure mode found in `batch.py`'s caption-and-window heuristics in one
day, after the figure label inside a table's match window (HyInv) and the part-1/part-2 split with
shared row labels (HyPLM-Flash). The pattern is the same each time: the heuristic assumes captions
and bodies appear in a particular order, and when they do not it returns a confident wrong answer
rather than an error. The general lesson for `decisions.md`: **`batch -- table` output must be
checked against the row labels you expect before it is used as evidence, because a wrong table is
indistinguishable from a right one in its output.**

## Rulings on the extractor's questions

### 1. Table D1's token, cost and runtime columns

Leave them out, but not for the reason given. The extractor's stated ground was that cost is "not a
molecular or omics endpoint, which is what brings an agent system into scope". That misreads
`docs/collection.md` section 1. The sentence there is "Agent systems are in scope when they are
scored on a task with a molecular or omics endpoint", which gates whether the *system* enters the
catalogue, not which of its metrics may be recorded. BenchBench-Cloning is in scope on that test, so
the clause does not exclude its cost columns, and there is no vocabulary barrier either: `metric.ttl`
has `compute-cost` and `unit.ttl` has `us-dollar`.

So the real question is relevance rather than scope, and it is a judgement about what the database is
for: it compares methods on molecular endpoints, and cost per attempt is a property of the vendor's
pricing and the harness rather than of the model's molecular capability. On that ground leaving them
out is defensible, and the paper's Section 4.3 cost frontier is preserved in claims. But it is the
owner's call, not mine, and it is cheap to reverse: the two cost columns are already parsed and
cross-checked against Table D2 for all 24 lanes, so storing them is 48 results and no new parsing.
The coordinator settled it: leave them out. Issue #235 did not ask for cost, nothing in the store
consumes it, and 48 results that no use case reads is the weight the owner has asked us not to add.
The parse stays in the batch, which is the cheap half of the option if anyone later wants the
columns. The token and runtime columns are a weaker case again, since the paper prints means with no
spread.

### 2. Is 224 results plus 223 claims the right size

Yes, and the coordinator's reasoning is the right one. Issue #235 withheld numeric extraction "until
exact configurations, denominators and primary-paper tables are reviewed". This batch did that review
first, in `notes.md`, and the record count follows from choosing whole tables over headline rows.
Verifying before extracting is compliance with that instruction, not scope creep, and ruling 9
already settled that JSONL record counts are not the release bloat the owner's priority refers to.

I would not drop a table. Each of the four extracted tables is load-bearing for a different reason:
D2 is the complete performance surface and the only source for 16 of the 24 lanes; G1 is the only
source for pass@k and task coverage, which is where three of the eight systems change rank; G2 is the
only per-task resolution anywhere in the paper and the only independent check on the construct-design
numerators; and Table 2 is correctly *not* stored, because it duplicates D2's eight top rows, which I
verified cell for cell rather than taking on assertion.

### 3. The off-grid 31.9%

It needs an evidence concern, and the contract settles it rather than leaving it to taste.
`docs/record-contract.md`: "Result-level `source_warnings` and `source_discrepancy` are notes for
readers and do not block." As extracted, the value carried `source_anomaly` and `source_warnings`
only, so it still supported automatic comparison. That is the one thing it should not do.

The evidence is two independent signals, both of which I recomputed. Of the 24 printed
construct-design rates, 31.9% is the only one with no integer numerator available in its own rounding
window over 75 attempts: the window is [23.8875, 23.9625] and the grid offers 23 (30.7%) or 24
(32.0%). And its printed 95% interval [10.7, 52.0] is byte-identical to the same system's top-effort
interval two rows below. A rate that cannot be a mean of binary outcomes over the stated grid is the
"conflicting tables" case `docs/collection.md` gives for a concern.

So the printed value stays exactly as published, with `source_anomaly` and `source_warnings` as the
reader-facing explanation, and a new `evidence_concerns` entry on the paper source names that one
result in `applies_to`. The scope is deliberately that narrow: the lane's aggregate is 15.8 whether
the rate is 31.9 or 32.0, so the aggregate is not corrupted and is not withheld, and Table G2 is
top-effort only so it cannot disambiguate. Nothing else in the batch is covered.

### 4. Is 500 the right denominator

This is the question that bears on the most records, and the answer is that 500 is the stated
*budget* and the denominator of the *rate* is not established. The batch conflated the two.

Appendix B states the budget: "Each system completed 10 attempts per protocol-development task",
which with 50 tasks is 500. So `coverage.eligible: 500` is right. But the extractor's protocol
limitation went further, saying "The stated denominator is 500 attempts (50 tasks x 10), and every
printed pass rate equals the Table E1 passed count divided by 500", and offered that arithmetic as
evidence. I tested it per system, and for the only two systems where the budget and the graded count
differ it is not evidence at all:

| System | Graded | Passed | Printed | n/500 | n/graded |
| --- | --- | --- | --- | --- | --- |
| Grok 4.7 | 498 | 31 | 6.2 | 6.200 | 6.225 |
| Gemini 3.8 Flash | 496 | 20 | 4.0 | 4.000 | 4.032 |

Both readings round to the printed value, so the printed rate cannot distinguish them. For the other
six systems the graded count is 500 and the question does not arise. The paper never says whether
ungraded attempts count as failures or are dropped.

The protocol limitation now says that, separating the stated budget from the unstated denominator and
giving the arithmetic for both readings. And yes to the coordinator's question: those two results
carry a `source_warnings` entry as well as the coverage note, because a reader of one of them needs to
know the denominator is undetermined, and the coverage note alone asserted "the printed pass rate
equals 31/500" as though it were settled.

Two further things I checked. Table E2 records 548 attempts for Grok 4.7 and 501 for Kimi K3 against a
budget of 500, which the paper does not explain; the extractor flagged Grok 4.7 but not Kimi K3, and
both are now in the limitation. And Tables E1 and E2 are top-effort only, so for the other 16
protocol-development lanes there is no published graded count at all and the denominator rests
entirely on the budget.

### 5. Should the aggregate be a result

Yes, a result. The authors printed it, which is the same ground on which HyInv's fitted-curve values
were stored, and the qualifier already does the work that ruling 3 requires: "aggregate
single-attempt score over all 65 tasks, task-weighted 50/65 protocol development and 15/65 construct
design". So nothing presents it as a direct measurement. I verified the composite arithmetic on all
24 lanes independently.

### 6. Is `success-rate` the right concept for it

Yes, for now, and the cross-batch point the coordinator raised cannot be acted on from this branch.
`weighted-composite-score`, introduced by the HyCell batch, does not exist in this tree:
`claude/benchbench-cloning` is based on `main`, not on the Hyra stack, so adding it here would create
a second, independent definition of the same concept in a shared vocabulary file, which is exactly
what the shared-vocabulary rule in `decisions.md` exists to prevent. Of the two concepts that do
exist here, `success-rate` is the better fit: the quantity is a weighted mean of two pass rates and
the paper's own table heading is "Aggregate %", while `accuracy` matches only the looser Figure 2 and
Figure 5 wording. Recorded below as a follow-up for after the HyCell batch merges.

### 7. Is the announcement concern correctly scoped

Yes, scoped to the one claim, as extracted. Ruling 4 reserves a source-level entry for a wholly
unreliable source, and a press page that misstates one ranking is not that. I checked the
substance: the post attributes to Kimi K3's 8.8% "the gap between frontier and open-weight models at
this task", while Table 2 puts Gemini 3.8 Flash, a hosted frontier model, at 8.6%, below it. The
misstatement is real and it is confined to that sentence; the post's other figures (30.6, 22.2, 20.5,
8.8, 72, 27) agree with Tables 2 and G1, which I spot-checked.

### 8. Should the Figure 7 counts be claims

Claims, as stored. Ruling 2 permits them, since they are printed digits present in the text layer,
but ruling 5 decides where they go: they count how many of 39 submissions contained a given
construct, which is a property of what was submitted, not a system's score on a panel. The same test
that sends Table C1's judge agreement and Table E1's failure categories to claims sends these there
too.

### 9. Does the construct-design source studies need a second dataset record

No. Six of the 15 tasks reuse experimental records from published papers, and Table A1 names the
source study per task, but the paper prints no file, accession or version for any of them. A dataset
record whose identity is "whatever records that paper reported" would assert an identity the source
does not pin down, which is the reasoning the HyInv review applied to ProteinMPNN's two generated
temperatures. A limitation naming Table A1 is the right home, which is where it is.

## A comparison-blocking defect found in review: the effort qualifier

Every result's `metric_qualifier` ended with the vendor's own name for the reasoning setting: `max`
for four systems, `high` for three, `xhigh` for one. Comparisons key on metric, qualifier, unit and
direction, so two systems at the same tier did not share a qualifier and did not compare. The
measured effect: the eight top-effort protocol-development results, which are the paper's Table 2
and the comparison the benchmark exists to make, sat under eight separate comparability keys.

This was a defect, not a wording preference. A field whose purpose is to permit comparison between
like things must not encode a vendor's spelling of the same thing. The contract supports the
extractor by the letter, since a qualifier holds "a setting", but the setting was already on each of
the 24 configurations, so the same fact blocked comparison twice; and the HyInv precedent in this
programme put the setting *class* in the qualifier and the specific setting on the configuration.

The fix replaces the vendor label with the tier: 24 results at the low tier, 24 at the mid tier and
176 at the top tier. Nothing is inferred. Table D2 prints a `Tier` column, low, mid or top, for all
24 lanes, and the captions of Tables G1 and G2 both say "at top effort", so every system's tier comes
from the page. No system needed a judgement call, so none was left out. Nothing is lost either: each
configuration still carries the vendor label in its `name`, `description`, `version`,
`hyperparameters`, `provenance_note` and `source_locator`, so a reader of a result reaches both.

What a reader gains: the distinct comparability keys over the 224 results fall from 36 to 15, and the
eight top-effort lanes of each metric now form one comparable set, as do the eight systems on each of
the 15 per-task rows of Table G2. The three tiers stay apart, which is correct, because low, mid and
top are genuinely different settings. Before the fix the database held 224 results that could not be
compared with each other at all, which is close to holding none.

## What the extractor got right that is worth keeping

Two of its findings outlive this batch and I confirmed both.

Footnote 1 on page 3 offers only the construct-design tasks, graders and reference solutions. The 50
protocol-development tasks, their hidden targets and the cloning simulator are offered nowhere in the
preprint. So even if the repository resolved, half the suite would remain unreproducible, and the 404
is not the only barrier. That belongs on the protocol-development benchmark, which is where it is.

Its three-route value check was the right response to a weak `in_row` signal, and its honesty about
the fourth route is what let me confirm the parser bug quickly rather than discovering it as a
disagreement.

## A finding of my own on the frozen batch

The extractor set status `source_checked` on 752 of the 756 records, while `notes.md` states "Not
reviewed: every record is `needs_review`, no human review is claimed, and `review-evidence` has not
run." Both cannot be true, and the records were the wrong one at extraction time: `source_checked`
is the status that says a value has been checked against its source, and no review had run.

After this pass it is true of those records, so I have not changed it; the review object on all 224
results and 223 claims now names the actor and the method.

Recorded here as a process finding, not only as something that is now true. Had this batch been
added to the store before review, or had the review been skipped, the store would have carried 752
records asserting a check nobody had performed, and nothing downstream would have known: status is
what the build, the comparisons and the use-case judgements read to decide whether a value has been
checked against its source, and there is no second field that would have contradicted it. The two
Hyra extractors in the same programme set `needs_review` on every record and left the promotion to
the review pass, which is the pattern. An extractor setting `source_checked` on its own output
removes the only signal that distinguishes a checked value from an unchecked one.

The four evaluator records keep `discovered`. They carry no `source_locator`, so there is no place in
the paper against which their descriptions could be said to have been checked; adding locators from
Sections 3.2 to 3.4 and Table A1 would let a later pass promote them.

## Gaps

The extractor's twelve gaps stand as recorded in `notes.md`, and I confirmed the three that carry the
most weight: the repository 404 at my own retrieval time, the unverified code and data licence, and
the undetermined denominator. The review adds two.

1. **Kimi K3's 501 recorded attempts** were not in the extractor's denominator gap, which named only
   Grok 4.7 and Gemini 3.8 Flash. Three of the eight systems have a recorded attempt count other
   than the 500 the budget implies, and the paper explains none of them.
2. **The four evaluator records have no source_locator**, so the graders are described without a
   pointer into the paper. See above.

## For the owner

All three items raised in review are settled, two by the coordinator and one by this pass.

1. **Cost per attempt stays out** (question 1). The scope argument against it does not hold, so the
   ground is relevance: nothing in the store consumes cost, and 48 results no use case reads is
   weight without a reader. The parse remains in the batch.
2. **The effort qualifier is fixed** (see above). Done in review rather than left, because after
   merge it would cost a repin cycle on 224 records.
3. **`success-rate` stands for the aggregate, and `weighted-composite-score` is not added here**
   (question 6). A second independent definition of one concept in a shared vocabulary file is worse
   than a concept key that is merely less specific. Re-pointing it is a follow-up after the HyCell
   batch merges.
