# New use cases and their evidence (2026-11-27)

Batch `data/omics/use-case-pages-20261127/` adds 9 use cases and the relevance judgements that link
existing protocols to them. The questions come from the leftovers of
`docs/reviews/2026-11-27-use-case-mapping-gaps.md`, section 5: unmapped benchmarks with two or more
studies, or ten or more models, that fit no existing use case.

`extract/use-cases.json` holds each use case's text, `extract/links.json` the rules that pick its
protocols with one reason per rule, and `extract/build.py . <this folder> --check` rebuilds
`batch.jsonl` and compares it. `applied.jsonl` lists every link with the protocol passage it rests
on. A protocol is linked only when it passes the evaluation gates of `shared/omics/use-cases.ts`;
the ones that do not are printed by the builder and listed in the review.

Each use case states in its `evidence_gaps` how many studies its linked evidence rests on, so a page
resting on one study does not read as settled. None carries `evidence_checked`: no literature search
ran for these questions, so each reads as not yet checked.

`batch.jsonl` is the full rebuild; four of its claims and one use-case edit were applied in a second
step (`changes.jsonl`) after the GenBench splice protocols were added to the rules, so the batch and
the store agree and `--check` passes.
