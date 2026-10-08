---
name: literature-search
description: Search primary literature, preprints, official benchmark repositories and leaderboards for existing published results of omics and molecular models, and record every query, decision and gap. Use when looking for new benchmark evidence for a research lane, use case, benchmark or model family. Does not extract values.
---

# Literature search

Follow [docs/collection.md](../../../docs/collection.md), sections 1 and 2. This skill finds and screens sources; `extract-evaluations` turns them into records.

## Inputs

- A scope: a research lane (`genomics`, `rna`, `protein-fitness`, `structure-design`, `cells-spatial`, `microbial`, `interactions`, `other-omics`, `networks-mechanistic`), a use-case ID from `data/omics/use-cases/inputs.json`, a benchmark or a model family.
- A search window (cutoff date) and a query budget. Ask if either is missing.

## Steps

1. Read what already exists for the scope: matching entries in `data/omics/search-ledger.jsonl`, `data/omics/discovery.jsonl`, `data/omics/scope-audit.jsonl`, the use-case definition and its `coverage.json` gaps, and the latest dossier in `docs/reviews/use-cases/` if there is one. Do not repeat a search already logged for the same window.
2. Search Europe PMC, PubMed, bioRxiv and arXiv, the benchmark's official repository and leaderboard, and model cards. Follow citations from benchmark papers to later evaluations. Treat search snippets, mirrors and press coverage as leads only.
3. For each candidate, find the primary artifact (paper version, supplement, repository commit) and check that it reports numbers for a model on a benchmark in scope. Note the table or figure.
4. Count every query against the budget, including failed ones.

## Outputs

Write only these files:

- `data/omics/search-ledger.jsonl`: one entry per search, with the exact `query`, `channels`, `searched_at`, `cutoff_date`, `status`, `included_record_ids`, `reviewed_source_ids`, `decision`, `gaps` and an honest `coverage_claim`. Copy the field set from an existing entry.
- `data/omics/scope-audit.jsonl`: include or exclude decisions with reasons.
- `data/omics/discovery.jsonl`: only for new benchmarks, models or datasets that have no results yet, each with a pinned `source` record.

Finish with a short report: candidates worth extracting (source URL, version, table or figure, why it matters), sources that could not be retrieved, and what the search did not cover.

## Rules

- An inaccessible source or failed search is a gap in `gaps`, never "nothing found".
- Do not create result records here.
- Do not claim exhaustive coverage.
