# Attribute normalisation and one reverted source reference, 2026-11-16

Two corrections to the store after CI on PR #248 failed two test shards. Both failures were
real and both were caused by this pass, not by anything older.

Reviewer: Claude coordinator session; no human review claimed. No scientific value, metric,
unit, direction, denominator or uncertainty is changed by either correction.

## 1. Review objects were stored in a non-canonical shape

`tests/attributes.test.ts`, "leaves current records unchanged", failed with 2,574 records that
`normalizeAttributes` would rewrite. Reproduced locally before changing anything.

Cause: every per-record `review` object written in this pass carries both `reviewed_at`, a
timestamp, and `date`, the same day as `YYYY-MM-DD`. `shared/omics/attributes.ts` treats that
pair as redundant and keeps one (`if (typeof r.reviewed_at === "string" && r.date ===
r.reviewed_at.slice(0, 10)) delete r.date`). `npm run records -- add` does not normalise, so
the non-canonical shape reached the store, and that test is the invariant which catches it.

Fix: `npm run attributes:migrate -- docs/reviews/2026-11-16-attribute-normalisation.md`, the
repository's own migration for this, which applies the same `normalizeAttributes` every reader
applies, records each changed record in `data/provenance/records/`, and changes nothing on a
second run. No field is lost: the dropped `date` duplicated `reviewed_at` to the day in every
case.

The batch folders keep the records as they were reviewed, so each `review.json` receipt still
matches its own `batch.jsonl`. The store holds the canonical form, and the provenance entry on
each record records the conversion.

## 2. A source reference that a frozen audit depends on

`tests/omics-benchmark-evidence.test.ts` failed on `reported-task-ed3dd3b83c4505`:

    expected [ 'phylogpn-2025' ] to include 'evidence-expansion-p2-phylogpn-2025-807f3a26cbfa'

Cause: item 5 of `docs/reviews/2026-11-16-coordinator-fixes.md` dropped the retired duplicate
source from that legacy task's `source_ids` and `attributes.benchmark_research.primary_sources`,
following ruling 5 of `docs/reviews/2026-11-16-phylogpn.md`. That went one step too far. The
frozen audit `data/omics/reviews/benchmark-evidence-2026/search-audit.jsonl` names the duplicate
ID as this benchmark's primary source, and the test checks the record still cites every source
that audit names. The audit is a dated artifact of an earlier pass and is not rewritten to suit
a later tidy-up.

Fix: both fields restored to cite `evidence-expansion-p2-phylogpn-2025-807f3a26cbfa` as well as
`phylogpn-2025`. The two records pin the same bytes, so citing both withholds nothing and
misleads no one.

The PhyloGPN ruling's intent is still served without this reference: the duplicate source record
itself is `superseded` by `phylogpn-2025`, which is what marks the retirement for readers and for
the graph. No correction claim is added for the revert, because the restored value is exactly the
value the coordinator pass's own correction claims already record as the previous one; those
claims now describe a change that was reverted, and this review is the record of that.

## Checks after both corrections

- `npm run records -- check`: every record matches its provenance.
- `tests/attributes.test.ts` and `tests/omics-benchmark-evidence.test.ts`: pass locally, run as
  single files with one fork.
- `npm run check:task-links`: passes, no protocol added to the unlinked baseline.

## What this says about the pass

`records -- add` accepting a non-canonical `review` object is the gap that let 2,574 records
through thirteen independent reviews without anyone noticing. Each reviewer checked its own
batch against its sources, which is what the review step is for, and no reviewer checks the
store's canonical form. The invariant that caught it only runs in CI. Worth considering whether
`records -- add` should normalise, or refuse a record it would normalise, so a batch cannot
reach the store in this shape.
