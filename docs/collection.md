# Collecting benchmark data

How published benchmark results for omics and molecular models get into this repository. The aim is that every stored number, and every claim about a model or benchmark, can be traced to a retrieved source, an exact location in it, and a recorded review.

The steps are the same whether the work is a monthly refresh, a use-case evidence pass, or a one-off extraction:

1. [Scope](#1-scope)
2. [Search the literature](#2-search-the-literature)
3. [Capture the source](#3-capture-the-source)
4. [Extract models and evaluations](#4-extract-models-and-evaluations)
5. [Review](#5-review)
6. [Add the batch to the build](#6-add-the-batch-to-the-build)
7. [Validate and open a PR](#7-validate-and-open-a-pr)

Agents should use the matching skills: `literature-search` (step 2), `extract-evaluations` (steps 3, 4 and 6) and `review-evidence` (step 5). The monthly cycle in [refresh.md](refresh.md) runs all of them. Record fields are defined in [record-contract.md](record-contract.md).

## Rules that apply throughout

- Record what was done, not what should have been done. A failed search, a paywalled supplement or an unreadable figure is a recorded gap. It is never evidence that nothing exists.
- Never change a stored value, ID or source hash. Corrections are new records that supersede old ones (see [Corrections and concerns](#corrections-and-concerns)).
- Never guess. Unknown fields are `null` with a reason in `missing_metadata`. An unidentified model version stays at family level and is not assigned to a specific checkpoint.
- Name the actual actor. Automated or AI review is recorded as such (for example `"reviewer": "Codex research agent; no human review claimed"`). It is never described as human scientific review, and source transcription is never described as reproduction.
- Search results, mirrors, press releases and summaries are leads. Only primary sources (the paper, its supplement, the official repository or project page, the official leaderboard) support a record.
- Keep work bounded. State the time window, budget and scope at the start, and report coverage against what was actually screened, not against a target count.

## 1. Scope

In scope: specialist omics and molecular models, including DNA and RNA language models, protein models, molecular interactions, single-cell and spatial omics, microbial communities, metabolomics and other molecular measurements, and mechanistic or network models.

Out of scope: clinical assistants, general medical question answering, language-agent benchmarks, and imaging without a molecular or omics endpoint.

Research is organised in nine lanes, used as scope IDs in the search ledger and the refresh schedule:

`genomics`, `rna`, `protein-fitness`, `structure-design`, `cells-spatial`, `microbial`, `interactions`, `other-omics`, `networks-mechanistic`.

Two further scopes cover cross-cutting checks: `scope-screen` (include or exclude decisions) and `source-resolution` (finding the primary artifact behind a lead). The 17 use cases in `data/omics/use-cases/inputs.json` are a separate axis: each defines a user decision and the evidence it needs (see [use-cases.md](use-cases.md)). Enumerate them from the file each time rather than relying on a remembered count.

A dataset is the underlying measurements. A benchmark is how a capability is evaluated on a dataset: its split, allowed inputs and metrics. Keep the two separate.

## 2. Search the literature

Goal: find existing published results for models on benchmarks, and record the search well enough that someone else can see what was and was not covered.

1. Fix the search window (cutoff date) and the scope: a lane, a use case, a benchmark or a model family.
2. Search primary literature (Europe PMC, PubMed, bioRxiv, arXiv), official benchmark repositories and leaderboards, and model cards. Follow citations from benchmark papers to the evaluations that use them.
3. Log every search in `data/omics/search-ledger.jsonl`, one JSON object per line:

   | Field | Meaning |
   | --- | --- |
   | `id` | `search-<purpose>-<lane>`, for example `search-discovery-genomics` |
   | `lane` | scope ID from step 1 |
   | `query` | the exact query string or browse path |
   | `channels` | for example `web_search`, `official_repository_readme`, `official_project_site` |
   | `searched_at` | when the search ran (UTC) |
   | `cutoff_date` | end of the search window |
   | `status` | for example `initial_pass_complete`, `screened`, `documented` |
   | `included_record_ids` | record IDs this search led to |
   | `reviewed_source_ids` | source records actually read |
   | `excluded`, `failed_candidates` | optional: leads screened out or not retrievable, with reasons |
   | `decision` | what was done with the results |
   | `gaps` | what remains unchecked or inaccessible |
   | `coverage_claim` | an honest statement of coverage, for example "Bounded discovery pass, not systematic exhaustion or all-model coverage." |

4. Record each include or exclude decision about a paper in `data/omics/scope-audit.jsonl`: `paper_id`, `decision` (`included` or `excluded`), `reason`, `reviewed_at`, `reviewer`.
5. New benchmarks, models, datasets and their sources found by discovery, but not yet carrying results, go in `data/omics/discovery.jsonl`.

Use-case passes also write a dated dossier in `docs/reviews/use-cases/` with the exact search log (query, mode, time, outcome). See `docs/reviews/use-cases/somatic-small-variant-oncogenicity-2026-10-08.md` for the expected level of detail.

## 3. Capture the source

Before extracting anything, pin the source.

- Retrieve the primary artifact (PDF, XML, supplement, README at a commit, leaderboard file) and compute its SHA-256.
- Create one `source` record per artifact with `url`, `version` (commit, DOI version, preprint version), `retrieved_at` (UTC), `artifact_sha256`, and where known `doi`, `publication_status` (`peer_reviewed`, `preprint` or `official_project_source`) and `licence`.
- Pin GitHub links to a commit, not a branch.
- For a mutable website, record that it is mutable and that the hash describes one retrieval.
- If the bytes are needed for later review and the licence allows it, archive a gzip copy under the batch folder (for example `artifacts/`) and record both the raw and archived hashes in the review receipt.
- If the source cannot be retrieved, stop and record the gap. Do not extract from a summary.

Sources that support profiles or several batches go in `data/omics/evidence-sources.jsonl`. Sources for a single batch go in that batch's `records.jsonl`.

## 4. Extract models and evaluations

Write records following [record-contract.md](record-contract.md). Search existing records first and reuse their IDs when the source describes the same model, benchmark or dataset at the same version. A typical published comparison table becomes:

- `model`, `method`, `pipeline` or `service` records for what was evaluated, and a `configuration` record for the exact setup that produced the scores (checkpoint, size, fine-tuning), with versions exactly as published.
- `benchmark`, `task`, `protocol`, `dataset` and `dataset_subset` records for what it was evaluated on. A protocol fixes the split, inputs and metric; two tables with different splits are two protocols.
- One `evaluation` per configuration and protocol, with `origin` (`author_reported`, `independent_paper`, `paper_compilation`, `rewire_run`, or `unreported` when the source does not say who ran it) and a `comparison` object. Comparison fields that the source does not state are `null`; that blocks automatic comparison, which is intended.
- One `result` per printed cell, with:
  - `printed_value`: the string exactly as printed, including `%`, `±` and rounding
  - `numeric_value`: decimal string, or `null` if not numeric
  - `metric`, `metric_direction` (`higher`, `lower` or `unknown`), `unit`, `uncertainty`
  - `source_locator`: precise enough to find the cell again, for example `Table 2, row "ESM-2 650M", column "Spearman"` or `Figure S10, Panel B (page 15 of 18), row "SVMrejection", test set ALM`
  - `review`: see [step 5](#5-review)
- `claim` records for descriptive facts about a model or benchmark (training data, licence, input type), each with its own `source_locator`.

The full list of kinds is in `services/omics/src/entity-kinds.ts`; allowed link relations are in the same file.

Every record carries `source_ids`. Missing results stay missing: never record a blank cell as zero.

Where a deterministic extractor exists for the source (`scripts/omics/extract/<benchmark>.ts`), use it and assert the expected row labels. Otherwise transcribe by hand and say so in the review notes. Figures without printed numbers are not read by eye or by colour; record them as a gap.

### Where extracted records go

There are two intake forms in use:

| Form | Use for | Location |
| --- | --- | --- |
| Benchmark batch | Complete tables from one benchmark source | `data/omics/reviewed/<benchmark>-<year>.jsonl`, receipt `data/omics/reviews/<date>-<benchmark>-extraction.json` |
| Use-case coverage batch | Evidence gathered for one or more use cases | `data/omics/use-case-coverage-<batch>/<lane>/` where lane is `clinical`, `research` or `experimental` |

A use-case coverage lane folder contains exactly these files, all bound by hash in the batch's `review.json`:

| File | Content |
| --- | --- |
| `records.jsonl` | the new records |
| `claims.csv` | one row per result or claim: `record_id, source_id, locator, printed_value, review_scope` |
| `coverage.json` | per use case: existing IDs reused, new IDs, and remaining gaps |
| `sources.md` | each source with URL, version, retrieval time and hash |
| `retrieval-log.md` | how each artifact was retrieved and read, step by step |
| `research.md` | what was searched, what was decided and why |

Unreviewed or disputed extractions that are not ready for the build go in `data/omics/pending-review/<batch>/` with a README stating their status. The release never reads that folder.

## 5. Review

Review is a separate pass by a different worker from the one that extracted the data.

1. Re-open the pinned source (check the hash matches) and check every result against it: printed value, numeric value, locator, metric, direction, denominator and the model/benchmark identity.
2. Check that `missing_metadata` and `null` fields are genuinely unstated in the source, and that nothing was inferred.
3. Fill each result's `review` object. The usual shape is:

   ```json
   {
     "method": "Plain description of how the value was checked, e.g. deterministic parse of the pinned PDF text layer with row labels asserted",
     "reviewer": "Who did it, e.g. Codex research agent; no human review claimed",
     "date": "2026-10-08",
     "artifact_sha256": "<hash of the source artifact checked>",
     "retrieval_url": "<URL the artifact was retrieved from>",
     "notes": "Anything a later reader needs: conflicts, rounding, what was not checked"
   }
   ```

   Human review is recorded only when a named person did it.
4. Write the batch receipt. For a use-case batch this is `review.json` (schema version, method, reviewer, reviewed_at, scope, limitations, empty `errors`, and the SHA-256 of every input file) plus per-lane `review-<lane>.json`. For a benchmark batch it is the extraction receipt (source, artifact hash, records hash, method, reviewer, date). The build refuses a batch whose files no longer match their receipt.
5. Summarise the pass in a dated review in `docs/reviews/` (or `docs/reviews/use-cases/` for a use-case pass): sources, a table of every value checked and its outcome, conflicts found, and remaining gaps.

A review can conclude that nothing should change. Record that in the dated review; no data change or release is needed.

### Corrections and concerns

- A wrong descriptive field: add a superseding entry to `data/omics/metadata-corrections.jsonl` with the evidence. The original stays in history.
- A problem with a source or result that should block comparison (conflicting tables, unclear units, abstract and body disagree): add an entry to `data/omics/evidence-concerns.jsonl` with the artifact hash, precise locator and review date. The value is kept and marked.
- A wrong numerical result: add a corrected result that supersedes the old one, with the evidence. Do not edit the old record.

### Auditing existing records

Audits are append-only checks on a specific catalogue release, stored in `data/omics/audits/`. To audit:

1. Freeze the release and retrieve primary sources with `scripts/omics/audit/check-sources.py`, recording hashes and access failures.
2. Run independent source-cell and metadata checks. A parser rerun, an HTTP 200 or an old review date is not a new verification.
3. Generate the run with `scripts/omics/audit/generate.ts`. Existing audit files cannot be overwritten with different bytes.
4. Resolve confirmed errors through a reviewed record change and a linked follow-up check. Never erase a contradictory finding.

## 6. Add the batch to the build

- Use-case mappings: add or update the mapping in `data/omics/use-cases/inputs.json` that links a use case to the new protocol, evaluation and result IDs. Mappings carry an evidence fingerprint that the build checks against the records.
- Register the batch as a build input. Benchmark batches are listed in `scripts/omics/inputs.ts`; use-case coverage folders are chained in `scripts/omics/release.ts` (search for `addUseCaseCoverage`). Additions must not replace or duplicate an existing record ID; the build rejects that.

## 7. Validate and open a PR

```sh
npm test
npm run test:python
npm run typecheck
npm run build
```

Then open a PR containing the batch, the ledger and scope entries, the review receipt and the dated review. Do not change `data/omics/release-config.json` in an evidence PR; releases are cut separately (see [release.md](release.md)).

## Where each claim is tracked

| What | Where | What proves it |
| --- | --- | --- |
| A search was done | `data/omics/search-ledger.jsonl`, use-case dossier | exact queries, channels, cutoff, gaps |
| A paper was included or excluded | `data/omics/scope-audit.jsonl` | stated reason |
| The source is what we say it is | `source` record | URL, version, `retrieved_at`, `artifact_sha256` |
| A value was printed in the source | `result` record, `claims.csv` | `printed_value` and `source_locator` |
| The value was checked | `result.attributes.review`, batch receipt, dated review | actor, method, time; file hashes |
| A descriptive fact about a model or benchmark | `claim` record, profile facts | `source_locator`, `status` |
| A known problem | `data/omics/evidence-concerns.jsonl` | artifact hash and locator |
| A correction | `data/omics/metadata-corrections.jsonl`, superseding records | linked evidence |
| What was not covered | ledger `gaps`, `coverage.json`, `missing_metadata` | explicit entries |
