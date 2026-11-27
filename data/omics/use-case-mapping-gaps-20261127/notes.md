# Use-case mapping gaps, links applied (2026-11-27)

Batch `data/omics/use-case-mapping-gaps-20261127/` adds 12 `proxy` relevance judgements, pinned with
`use-cases:repin` against `docs/reviews/use-cases/use-case-mapping-gaps-2026-11-27.md`: 4 on
cell-type annotation transfer and 8 on mass spectrum shortlisting. `applied.jsonl` lists each with
the protocol passage it rests on. `extract/build_links.py . <this folder> --check` rebuilds
`batch.jsonl` and compares it. The candidates considered and not applied, with reasons, are in the
review and in `kb/curation/use_case_mapping_candidates.jsonl`.
