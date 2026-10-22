---
name: literature-search
description: Search primary literature, preprints, official benchmark repositories and leaderboards for existing published results of omics and molecular models, and record every query, decision and gap. Use when looking for new benchmark evidence for a research lane, use case, benchmark or model family. Does not extract values.
---

# Literature search

Follow [docs/collection.md](../../../docs/collection.md), sections 1 and 2. This skill finds and screens sources; `extract-evaluations` turns them into records.

## Inputs

- A scope: a research lane (`genomics`, `rna`, `protein-fitness`, `structure-design`, `cells-spatial`, `microbial`, `interactions`, `other-omics`, `networks-mechanistic`), a use-case ID from `data/entities/use-cases.jsonl`, a benchmark or a model family.
- A search window (cutoff date) and a query budget. Ask if either is missing.

## Steps

1. Read what already exists for the scope: matching entries in `data/omics/search-ledger.jsonl`, `data/omics/scope-audit.jsonl`, the canonical store (`data/entities/`, `data/evidence/`), the use-case definition and its `coverage.json` gaps, and the latest dossier in `docs/reviews/use-cases/` if there is one. Do not repeat a search already logged for the same window.
2. Search Europe PMC, PubMed, bioRxiv and arXiv, the benchmark's official repository and leaderboard, and model cards. Follow citations from benchmark papers to later evaluations. Treat search snippets, mirrors and press coverage as leads only.
3. For each candidate, find the primary artifact (paper version, supplement, repository commit) and check that it reports numbers for a model on a benchmark in scope. Note the table or figure.
4. Count every query against the budget, including failed ones.

## Outputs

Write only these files:

- `data/omics/search-ledger.jsonl`: one entry for the pass, with `queries` (every query run, including failures, as `{query, channel, outcome}`), `channels`, `searched_at`, `cutoff_date`, `status`, `included_record_ids`, `reviewed_source_ids`, `decision`, `gaps` and an honest `coverage_claim` (docs/collection.md, section 2).
- `data/omics/scope-audit.jsonl`: include or exclude decisions with reasons.
- For a use-case scope: the search report as `notes.md` in the batch folder (docs/collection.md, section 2). Write it once; do not keep draft copies elsewhere.
- For a use-case scope: the use case's `evidence_checked` (date, cutoff, ledger and review paths), set after review with `records -- change`, even when nothing new is found ([docs/use-cases.md](../../../docs/use-cases.md#when-the-evidence-was-last-checked)).
- New benchmarks, models or datasets with no results yet: hand them to `extract-evaluations` as a small batch with status `discovered`.

Finish with a short summary pointing to `notes.md`: the number of candidates, queries used, and anything the extractor must decide. Phrase open points as questions for the extractor, not as settled conclusions.

## Rules

- An inaccessible source or failed search is a gap in `gaps`, never "nothing found".
- Do not create result records here.
- Do not claim exhaustive coverage.
