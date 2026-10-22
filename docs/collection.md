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

In scope: specialist omics and molecular models, including DNA and RNA language models, protein models, molecular interactions, single-cell and spatial omics, microbial communities, metabolomics and other molecular measurements, and mechanistic or network models. Agent systems are in scope when they are scored on a task with a molecular or omics endpoint (for example BioDiscoveryAgent on CRISPR screen hit recovery). Record the agent scaffold as a method and the underlying LLM as a model it uses.

Out of scope: clinical assistants, general medical question answering, language-agent benchmarks of question answering, clinical or literature reasoning, and imaging without a molecular or omics endpoint.

Research is organised in nine lanes, used as scope IDs in the search ledger and the refresh schedule:

`genomics`, `rna`, `protein-fitness`, `structure-design`, `cells-spatial`, `microbial`, `interactions`, `other-omics`, `networks-mechanistic`.

Two further scopes cover cross-cutting checks: `scope-screen` (include or exclude decisions) and `source-resolution` (finding the primary artifact behind a lead). The use cases (`use_case` records in `data/entities/use-cases.jsonl`) are a separate axis: each defines a user decision and the evidence it needs (see [use-cases.md](use-cases.md)). Enumerate them from the file each time rather than relying on a remembered count.

A dataset is the underlying measurements. A benchmark is how a capability is evaluated on a dataset: its split, allowed inputs and metrics. Keep the two separate.

## 2. Search the literature

Goal: find existing published results for models on benchmarks, and record the search well enough that someone else can see what was and was not covered.

1. Fix the search window (cutoff date) and the scope: a lane, a use case, a benchmark or a model family.
2. Search primary literature (Europe PMC, PubMed, bioRxiv, arXiv), official benchmark repositories and leaderboards, and model cards. Follow citations from benchmark papers to the evaluations that use them.
3. Log each search pass in `data/omics/search-ledger.jsonl` as one JSON object: one line per pass, not per query. The query list is what shows coverage; repeating the window, lane and coverage statement on every query adds nothing.

   | Field | Meaning |
   | --- | --- |
   | `id` | `search-<purpose>-<lane>`, for example `search-discovery-genomics` |
   | `lane` | scope ID from step 1 |
   | `queries` | every query run, including failed ones: `{query, channel, outcome}`, where `query` is the exact string or browse path and `outcome` is a few words (hits, the lead it gave, or the failure) |
   | `channels` | for example `web_search`, `official_repository_readme`, `official_project_site` |
   | `searched_at` | when the pass ran (UTC) |
   | `cutoff_date` | end of the search window |
   | `status` | for example `initial_pass_complete`, `screened`, `documented` |
   | `included_record_ids` | record IDs this search led to |
   | `reviewed_source_ids` | source records actually read |
   | `excluded`, `failed_candidates` | optional: leads screened out or not retrievable, with reasons |
   | `decision` | what was done with the results |
   | `gaps` | what remains unchecked or inaccessible |
   | `coverage_claim` | an honest statement of coverage, for example "Bounded discovery pass, not systematic exhaustion or all-model coverage." |

4. Record each include or exclude decision about a paper in `data/omics/scope-audit.jsonl`: `paper_id`, `decision` (`included` or `excluded`), `reason`, `reviewed_at`, `reviewer`.
5. New benchmarks, models, datasets and their sources found by discovery, but not yet carrying results, are added as records through step 6 with status `discovered`.

Older ledger entries hold one query each in a `query` field; leave them as they are.

Use-case passes also write one search report, `notes.md` in the batch folder: the candidates worth extracting (primary URL, version, exact table, endpoint, whether values are per-target or pooled, leakage control, whether the authors built the method), what the store already holds, what could not be retrieved and why, and what the search did not cover. It replaces the separate search report, `research.md` and dossier search log; point to the ledger entry rather than copying the queries.

## 3. Capture the source

Before extracting anything, pin the source.

- Retrieve the primary artifact (PDF, XML, supplement, README at a commit, leaderboard file) and compute its SHA-256. Hash the artifact the values come from, not intermediates such as a text layer or an unzipped copy; those can be regenerated from it.
- Create one `source` record per artifact with `url`, `version` (commit, DOI version, preprint version), `retrieved_at` (UTC), `artifact_sha256`, and where known `doi`, `publication_status` (`peer_reviewed`, `preprint` or `official_project_source`) and `licence`.
- Pin GitHub links to a commit, not a branch.
- For a mutable website, record that it is mutable and that the hash describes one retrieval.
- If the bytes are needed for later review and the licence allows it, archive a gzip copy under the batch folder (for example `artifacts/`) and record both the raw and archived hashes in the review receipt.
- If the source cannot be retrieved, stop and record the gap. Do not extract from a summary. Failed retrieval routes go in the ledger entry's `gaps` and in `notes.md`; a step-by-step retrieval narrative is not needed, because the source record already holds the URL, version, time and hash.

Source records live in `data/entities/sources.jsonl` like any other record. Search it before adding one: 197 source URLs already have more than one record, and new duplicates make the graph harder to use.

## 4. Extract models and evaluations

Write records following [record-contract.md](record-contract.md). Search existing records first and reuse their IDs when the source describes the same model, benchmark or dataset at the same version. A typical published comparison table becomes:

- `model`, `method`, `pipeline` or `service` records for what was evaluated, and a `configuration` record for the exact setup that produced the scores (checkpoint, size, fine-tuning), with versions exactly as published. Each description is one sentence saying what the method does, written from the primary source; where the record came from goes in `attributes.provenance_note` (see [record-contract.md](record-contract.md)).
- `benchmark`, `task`, `protocol`, `dataset` and `dataset_subset` records for what it was evaluated on. A protocol fixes the split, inputs and metric; two tables with different splits are two protocols.
- One `evaluation` per configuration and protocol, linked with exactly one `system`, one `assessment` and one `data` (see [record-contract.md](record-contract.md) for every relation), with `origin` (`author_reported`, `independent_paper`, `paper_compilation`, `rewire_run`, or `unreported` when the source does not say who ran it) and a `comparison` object. Comparison fields that the source does not state are `null`; that blocks automatic comparison, which is intended.
- One `result` per printed cell, with:
  - `printed_value`: the string exactly as printed, including `%`, `±` and rounding. The one exception is a value computed from the source's own supplementary data (see [Values computed from source data](#values-computed-from-source-data)).
  - `numeric_value`: decimal string, or `null` if not numeric
  - `metric`, `metric_direction` (`higher`, `lower` or `unknown`), `unit` and `uncertainty`. `metric` and `unit` are concept keys from [data/vocab/metric.ttl](../data/vocab/metric.ttl) and [data/vocab/unit.ttl](../data/vocab/unit.ttl), not the source's wording. When the source's metric carries more than the concept (a class, a setting such as zero-shot, a scope such as SNV only, a cutoff, or an aggregation such as median over targets), put it in `metric_qualifier`, phrased the same way as existing qualifiers. Detail a unit concept cannot hold (the counted entity, a printed scale) goes in `unit_detail`.
  - `source_locator`: precise enough to find the cell again, for example `Table 2, row "ESM-2 650M", column "Spearman"` or `Figure S10, Panel B (page 15 of 18), row "SVMrejection", test set ALM`
  - `review`: see [step 5](#5-review)
- `claim` records for descriptive facts about a model or benchmark (training data, licence, input type), each with its own `source_locator`.

The full list of kinds is in `shared/omics/entity-kinds.ts`; allowed link relations are in the same file.

Controlled fields hold concept keys from the SKOS vocabularies in `data/vocab/` (`<scheme>.ttl`): metric, unit, metric direction, areas, method types, contexts, publication status, origin, entity level, baseline type, configuration type, review method and reviewer (`agent`). `npm run records -- add` rejects any other value. If no concept fits, add one to the scheme in the same PR, with a definition and an external match (STATO, QUDT or EDAM) where one exists, and get it reviewed like a record change. Never add a concept that only respells an existing one.

Every record carries `source_ids`. Missing results stay missing: never record a blank cell as zero.

Where a deterministic extractor exists for the source (`scripts/omics/extract/<benchmark>.ts`), use it and assert the expected row labels. Otherwise transcribe by hand and say so in the review notes. Figures without printed numbers are not read by eye, by colour or from pixels; record them as a gap, unless the source publishes the figure's underlying rows (below).

### Values computed from source data

Some sources print results only as figures but publish the per-item rows behind them, for example a Source Data workbook with one row per perturbation. A result may be computed from those rows when all of these hold:

- The rows are the source's own supplementary data, retrieved from the publisher or the authors' repository. A third party's reanalysis, or a compilation paper's copy, does not count.
- The source states the aggregation in its own words, for example "The horizontal red lines show the mean per model". If the aggregation is ambiguous (a bootstrap with no resample count, a ratio that could be a ratio of means or a mean of ratios, a filter the rows do not let you apply), do not compute it. Record a gap.
- Each input file is pinned: one `source` record per file, with its SHA-256, re-downloaded and checked before use.
- The computation is a deterministic script in the repository, run on the pinned files, which asserts the row counts it expects.

Record the result with a `derivation` ([record-contract.md](record-contract.md)): the inputs and their row filters and counts, the quoted aggregation and where it is printed, the script and its hash, and the precision. `printed_value` is the computed value at that precision. The evaluation keeps its usual origin; the derivation is what marks the number as computed by Rewire, and the website labels it that way. Inconsistencies between the rows and the paper's text (counts that do not match a legend, a method the text says was excluded) go in the source's `evidence_concerns`.

### Where records live

All records live in one canonical store. Every file is JSONL, sorted by ID:

| Location | Content |
| --- | --- |
| `data/entities/<kind>.jsonl` | one file per kind: `models`, `methods`, `configurations`, `pipelines`, `services`, `benchmarks`, `tasks`, `protocols`, `evaluators`, `datasets`, `dataset-subsets`, `baselines`, `sources`, `use-cases` |
| `data/evidence/<kind>/<shard>.jsonl` | `evaluations`, `results` and `claims`, each split into 16 shards |
| `data/provenance/records/<shard>.jsonl` | one line per record, in 16 shards: its SHA-256, the batch that added it, and every reviewed change since |

A record's shard is the first hex digit of the SHA-256 of its ID (UTF-8). For example, `printf %s <id> | shasum -a 256 | cut -c1` names the file that holds it, in its evidence folder and in `data/provenance/records/`. Sharding keeps every file far below GitHub's 50 MB warning and 100 MB limit; CI fails if any file under `data/` exceeds 50 MB. `records -- add` and `records -- change` place records and provenance in the right shard, and `records -- check` rejects a record in the wrong file. Scripts should read and write the store through `scripts/omics/records.ts` (`loadRecords`, `readKind`, `writeKind`, `recordFiles`) rather than by path.

If a shard approaches 50 MB, raise `shardDigits` in `scripts/omics/records.ts` (2 gives 256 shards) or add the kind to `shardedKinds`, run `npm run records -- reshard`, which moves every line unchanged to its new file, and commit the result. Release receipts list the store as one logical file per kind (`data/evidence/results.jsonl`, `data/provenance/records.jsonl`) with the SHA-256 of its lines in ID order, so changing the shard layout does not change a release ID.

The build reads only this store. A record whose bytes no longer match its provenance hash fails the build until the change is recorded (step 6).

### The batch folder

Each extraction keeps its working evidence in a batch folder, `data/omics/<batch>/` (existing batches are under `data/omics/reviewed/`, `data/omics/acquisition/` and `data/omics/use-case-coverage-*/`). The folder holds provenance, not records:

| File | Content |
| --- | --- |
| `batch.jsonl` | the new records, as reviewed; added to the store in step 6 |
| `extract/` | the table specification or script that produced the results, where one was used |
| `notes.md` | the search report and the decisions taken, with reasons (step 2) |
| `coverage.json` | for use-case work: existing IDs reused, new IDs, and remaining gaps |
| `review.json` | the review receipt (step 5) |
| `artifacts/` | archived source bytes, where the licence allows |

Older batches also hold `claims.csv`, `sources.md`, `retrieval-log.md` and `research.md`. New batches do not write them: each repeats what `batch.jsonl`, the source records or `notes.md` already hold. If a script needs one, generate it from `batch.jsonl`.

Unreviewed or disputed extractions that are not ready go in `data/omics/pending-review/<batch>/` with a README stating their status. The build never reads that folder.

## 5. Review

Review is a separate pass by a different worker from the one that extracted the data.

Start review only on a frozen extraction: a commit the extractor has finished and will not change. Make every ruling and edit in `batch.jsonl` first, then write the receipt, then add the batch (step 6) and run the checks once. Adding the batch before the rulings are done turns each later fix into a `records -- change` and repin cycle.

1. Re-open the pinned source (check the hash matches) and check every result against it. For a large batch, an automated comparison of every value against the source (for example a deterministic parse with asserted row labels) plus a sampled manual check of values is enough; record the sample and the comparison in the receipt. Write the comparison as one script run over the whole batch, and save its mismatch report in the batch folder. Check printed value, numeric value, locator, metric, direction, denominator and the model/benchmark identity. For a result with a `derivation`, re-download each input, check its SHA-256 and row count, rerun the script and compare its output with `printed_value`; check the quoted aggregation against the source and that the script applies it.
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
4. Write the batch receipt `review.json`: schema version, method, reviewer, `reviewed_at`, scope, limitations, an empty `errors` list, the SHA-256 of `batch.jsonl` and every other file in the batch folder, and the SHA-256 of each source artifact checked. Compute the hashes with a script as the last step, not by hand. After step 6, each record's hash in `data/provenance/records/` locks the reviewed bytes. A script that rebuilds the batch (`build.py`) is optional: keep one when it is how the batch was made, but the receipt and the provenance hashes are the record of review.
5. Summarise the pass in a dated review in `docs/reviews/` (or `docs/reviews/use-cases/` for a use-case pass): sources and hashes, how values were compared and the sample drawn, a link to the mismatch report, each ruling on a question the extractor raised with the source text that decides it, conflicts found, and remaining gaps. Do not copy every value into a table; the mismatch report and the records already hold them.

A review can conclude that nothing should change. Record that in the dated review; no data change or release is needed.

### Corrections and concerns

Edit the record in its canonical file (for an evaluation, result or claim, the shard named in [Where records live](#where-records-live); `grep -l '"id":"<record-id>"' data/evidence/*/*.jsonl` also finds it), then record the change with the review that justifies it:

```sh
npm run records -- change docs/reviews/<date>-<topic>.md data/omics/<batch> <record-id> [<record-id> ...]
```

That updates each record's provenance hash and appends a `changed_by` entry (inputs, date, review). Without it the build fails.

- A wrong descriptive field: change the field, and add a `claim` record that keeps the old value (`field`, `previous_value`, `value`, `source_locator`, `review`, with a `subject` link). Existing examples have IDs starting `metadata-correction-`.
- A problem with a source or result that should block comparison (conflicting tables, unclear units, abstract and body disagree): add an entry to the source record's `attributes.evidence_concerns` with `source_id`, `message`, `source_locator`, `artifact_sha256` and review date. The value is kept and marked.
- A wrong numerical result: add a corrected result that supersedes the old one, with the evidence. Do not edit the old record's value.

### Auditing existing records

Audits are append-only checks on a specific catalogue release, stored in `data/omics/audits/`. To audit:

1. Freeze the release and retrieve primary sources with `scripts/omics/audit/check-sources.py`, recording hashes and access failures.
2. Run independent source-cell and metadata checks. A parser rerun, an HTTP 200 or an old review date is not a new verification.
3. Write the run, checks and resolutions in the audit format defined in `shared/omics/audit.ts`, under a new run ID. Existing audit files cannot be overwritten with different bytes. (The generators for the September 2026 runs were tied to releases that are no longer stored; their output remains in `data/omics/audits/`.)
4. Resolve confirmed errors through a reviewed record change and a linked follow-up check. Never erase a contradictory finding.

## 6. Add the batch to the store

```sh
npm run records -- add data/omics/<batch>/batch.jsonl data/omics/<batch>
```

This appends each record to the right canonical file or shard, keeps the files sorted, and writes its provenance line. It then validates the new records, the records that link to them and their link targets against the SHACL shapes (`npm run kg -- subset`, then `kg:build --shapes-only`; needs [uv](https://docs.astral.sh/uv/) and takes well under a minute); if any of them fails, the store is put back as it was. `records -- change` runs the same check on the changed records. CI checks the whole store against the shapes on every pull request (`npm run kg:shapes`). It refuses any ID that already exists; to change an existing record, use `records -- change` (step 5). `npm run records -- check` confirms the whole store matches its provenance.

For use-case work, also add a relevance judgement for each new protocol that bears on a use case: an `assessed_by` link on the `use_case` record and a judgement claim (`field` `links:assessed_by:<protocol>`) recording relevance, endpoint, rationale, caveats and sources, with status `needs_review`. Evaluations on the protocol are found automatically. The reviewer lists the evaluations it checked in `reviewed_evaluations` and records the pins with `npm run use-cases:repin -- <review.md> <claim-id>...`. Fill `method_types`, version and access on each new configuration, so the use-case page can say what kind of method it is. See [use-cases.md](use-cases.md).

## 7. Validate and open a PR

```sh
npm run test:fast
npm run typecheck
npm run build
```

CI runs the full tests, the Python tests and the SHACL check of the whole store. Then open a PR containing the batch folder, the store and provenance changes, the ledger and scope entries, and the dated review. Plain JSONL keeps every changed record visible in the diff. Do not change `data/omics/release-config.json` or commit the build's `data/omics/releases/` and `website/` changes in an evidence PR; after merge, the release workflow cuts the release (see [release.md](release.md)). The PR title becomes the release note, so make it describe the change.

## Running a pass with agents

- Brief each phase with questions, not conclusions. Hand the extractor the ambiguities the search found ("decide whether these values are per series, from the source text") rather than the answer you expect. A brief that states the answer gets reversed by the extractor or the reviewer, and each reversal is another round.
- Run one extraction worker per source where sources are independent, so each worker's context stays small. One reviewer then checks the merged batch.
- Workers write long reports to files in the batch folder and return a short summary.
- Batch exploratory reads into one script rather than many single commands, and trim command output (`| tail`) before reading it.
- Coordinate from a fresh session per pass. A coordinator carrying an unrelated long conversation re-reads all of it each time a worker reports.

## Where each claim is tracked

| What | Where | What proves it |
| --- | --- | --- |
| A search was done | `data/omics/search-ledger.jsonl`, batch `notes.md` | exact queries, channels, cutoff, gaps |
| A paper was included or excluded | `data/omics/scope-audit.jsonl` | stated reason |
| The source is what we say it is | `source` record | URL, version, `retrieved_at`, `artifact_sha256` |
| A value was printed in the source | `result` record | `printed_value` and `source_locator` |
| A value was computed from the source's own data | `result.attributes.derivation`, the script in the repository | pinned input hashes, row filters and counts, the quoted aggregation, the script hash |
| The value was checked | `result.attributes.review`, batch `review.json`, dated review | actor, method, time; file hashes |
| The record has not changed since review | `data/provenance/records/` | per-record SHA-256 and `changed_by` history |
| A descriptive fact about a model or benchmark | `claim` record, profile facts | `source_locator`, `status` |
| A known problem | source `attributes.evidence_concerns` | artifact hash and locator |
| A correction | `metadata-correction-*` claim, superseding records, provenance `changed_by` | linked evidence and review |
| What was not covered | ledger `gaps`, `coverage.json`, `missing_metadata` | explicit entries |
