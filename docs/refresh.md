# Monthly benchmark evidence refresh

The benchmark-data producer owns discovery, reviewed records, source evidence, ingestion, and immutable releases. The database website/API consumes those releases; the benchmark runner owns experimental execution. This workflow prepares and reviews evidence changes without automatically publishing them.

## Operational status and ownership

`maintenance/schedule.json` describes a **planned** monthly cycle: the first day of each month at 09:00 Europe/London. No scheduler is activated by that file. The proposed maintainer is `timini`; assignment and operational activation still require agreement. Qualified human scientific review is unassigned (`scientific_reviewer: null`). Automated curation and cross-review must stay labelled as such.

The schedule's `configured_at` records when this operational metadata was established; it is not a completed-review or publication time. The first future due time after setup on 1 October 2026 is 1 November 2026 at 09:00 London time (09:00 UTC). Future times follow the Europe/London calendar across daylight-saving changes; do not schedule a fixed UTC offset year-round. A manual October pilot is separate from that future due time.

Before activation, complete and inspect a full manual pilot, confirm operator and notification ownership, and explicitly authorize the operational schedule. Scheduled-cycle acceptance remains pending until the activated scheduler has produced one observed, durable cycle with the expected reporting and recovery behaviour. Installing the skill, creating schedule metadata, or completing a partial pilot does not satisfy that acceptance criterion.

## Scope and evidence

Read the configured scope at the start of every cycle. The current search ledger contains nine research lanes: `cells-spatial`, `genomics`, `interactions`, `microbial`, `networks-mechanistic`, `other-omics`, `protein-fitness`, `rna`, and `structure-design`. Also cover `scope-screen` and `source-resolution`, plus the `existing-sources` and `use-cases` scopes.

For `use-cases`, enumerate every current ID from `data/entities/use-cases.jsonl`. Enumerate the file again when running rather than preserving a count in code. Examine active relevance judgements, exact endpoints/protocols, conventional baselines, source revisions, review fingerprints, and remaining direct/proxy evidence gaps. A source-level change can affect multiple use cases, which must remain explicit.

Each cycle includes:

- New eligible papers, models, benchmarks, datasets, and protocols within the frozen coverage window.
- Existing source revisions, changed URLs or versions, corrections, withdrawals/retractions, and relevant changes to evaluation conditions.
- Unresolved source access, conflicting measurements, unmapped evidence, and previously recorded coverage gaps.
- Changes to use-case applicability and whether existing evidence still supports its exact recorded scope.

Use current primary sources and preserve source URLs, version identifiers, retrieval times, artifact hashes, and exact numerical locators where relevant. Queries and documented exclusion decisions are evidence too. A failed retrieval, unavailable supplement, search-service failure, or unreviewed source remains blocked; do not describe it as checked or as proof that no evidence exists.

The existing pinned-GitHub HEAD check is a useful subcheck. It does not cover publication discovery, retractions, unversioned sites, all previously added source records, or the whole use-case inventory.

## Durable commands and recovery

Run from the producer repository using `npm run refresh -- <command>`. Inspect command-specific help if options change. State is stored in `maintenance/runs/*.json`; report artifacts belong under `maintenance/reports/<attempt-id>/`.

1. `npm run refresh -- status`: inspect existing cycles, attempts, saved windows, blockers, and PR links before beginning work.
2. `npm run refresh -- begin --cycle YYYY-MM --scope comma-list --baseline releaseId`: start one bounded attempt with the current immutable baseline release and every configured scope.
3. Research and review within the frozen window and budget; preserve the returned attempt ID. Store a substantive JSON report under its report directory.
4. `npm run refresh -- finish --id UUID --report maintenance/reports/UUID/report.json --status completed --outcome no_change` records a complete no-change sweep. Use `--outcome review_required` for a complete sweep that produces candidate changes.
5. Use `--status blocked` when scope or source checks remain incomplete, or `--status failed` for an execution failure. Omit an outcome for those states. Record the actual gaps and completed checks rather than discarding partial work.
6. `npm run refresh -- resume --id UUID` inspects the saved attempt. A retry requires `npm run refresh -- begin --cycle YYYY-MM --scope original-comma-list --baseline original-releaseId --retry-of UUID`, retaining the original cycle, coverage window, scope, and baseline. Do not overwrite or reopen terminal receipts.
7. `npm run refresh -- link-pr --id UUID --url URL` associates an existing candidate PR with the attempt. `npm run refresh -- export` prepares the public maintenance export; it does not prove or perform publication.

The overlap is 14 days to catch delayed indexing or revisions. Reuse the exact window recorded by the CLI; never recompute it midway through an attempt or retry. Successful coverage dates and scientific release dates are different: a complete no-change sweep can advance coverage without creating a scientific release, while an incomplete sweep must not conceal its unchecked interval.

Record genuine query/retrieval times, including research performed before the CLI attempt began. A retry may reuse documented evidence from its original frozen window; do not relabel old checks as newly executed. Historical source snapshots can support unchanged facts, but a new monthly sweep must actually check developments since the previous completed coverage cutoff. Reusing an overlapping-window report alone does not establish fresh monthly coverage. Distinguish reused source evidence from new searches in each check's reason and the report's limitations.

Default limits are three attempts, 120 minutes per attempt, and 60 queries. Allocate the shared budget across any parallel workers. Count actual searches, including retries; do not omit queries from the report to appear within budget. If the complete scope cannot fit, finish blocked with honest gaps and request a deliberate scope/budget decision. Do not silently narrow a monthly cycle or increase limits. A subset pilot must finish blocked, even if every selected subset check passed.

## Report contract

`finish` accepts this report shape:

```json
{
  "summary": "A concise account of the actual work and outcome",
  "coverage": {
    "checked_ids": ["genomics"],
    "gaps": ["Remaining scopes have not been checked"]
  },
  "checks": [
    {
      "scope_id": "genomics",
      "query": "The exact query or source-check operation performed",
      "checked_at": "2026-10-01T15:00:00Z",
      "url": "https://example.org/primary-source",
      "decision": "unchanged",
      "reason": "What was inspected and what the evidence supports",
      "record_ids": []
    }
  ],
  "use_case_review": {
    "reviewed_ids": [],
    "fingerprint_policy": "preserved",
    "review_receipt": null
  },
  "limitations": ["Automated source checks are not human scientific review"]
}
```

This illustrative subset is **blocked**, not a completed monthly report. Replace every example with actual evidence. `decision` is one of `included`, `revised`, `excluded`, `unchanged`, or `blocked`. `checked_ids` refers to configured scope IDs; `reviewed_ids` enumerates the current use-case IDs. Completion requires every required scope to be both targeted and checked, actual check evidence for each checked scope, all current use cases reviewed, and no gaps or blocked checks.

Use `fingerprint_policy: "preserved"` when the tracked use-case inputs remain unchanged against the captured beginning state. If real curation changes them, use `"explicitly_reviewed"` and supply a nonempty `review_receipt` path to the matching existing native review receipt. Its bytes are hashed and validated by the native receipt loader. The receipt must identify its actual reviewer, method, and time and pass the producer's existing review gates; simply regenerating hashes does not constitute review. Do not forge a human reviewer or mark inaccessible source content as inspected.

## Review, PRs, and publication

Stage proposed evidence changes through existing receipt-bound ingestion. Preserve scientific record IDs, numerical values, source identities, protocol distinctions, and prior release bytes. Candidate additions and corrections need independent review; a maintenance run alone cannot promote them. A no-change cycle creates no scientific release merely to update a date.

Before creating a PR, inspect the current cycle's linked PR and open PRs for the same refresh. Update the existing candidate when appropriate; do not create one PR per retry. Carry the same PR link across attempts and record it with `link-pr`. If an earlier PR is closed unmerged, explain its replacement before linking a new one. Do not claim a candidate is live after generation, review, or merge.

Publication is recorded separately using a verified live deployment receipt bound to the existing immutable release ID and manifest checksum. A release manifest on disk is not publication proof. After the existing publication workflow has deployed the reviewed release, prepare a notes JSON file:

```json
{
  "summary": ["Describe the reviewed change actually present in the live release"],
  "links": [
    {"label": "Reviewed change", "url": "https://github.com/rewire-bio/rewire-benchmark-data/pull/123"}
  ],
  "maintenance_run_id": null
}
```

Replace the illustrative PR link and summary with the actual evidence. Use a completed `review_required` attempt's ID only when it produced this release; use `null` for an independently published release. Record and export using:

```sh
npm run refresh -- record-publication --notes maintenance/reports/publication-notes.json
npm run refresh -- export
```

`record-publication` reads live deployment metadata before and after the live manifest, verifies that the deployment stayed stable, and compares manifest bytes with the producer's immutable archive. It retains a hash-bound publication proof. The resulting `published_at` has `time_basis: "observed"`: it is when this release was confirmed live, not a claimed exact deployment instant. The release's own `released_at` remains a separate scientific metadata date. Do not infer missing historical deployment dates from archive filenames or rewrite a prior first-observation receipt to make it appear earlier.

The public update history must distinguish attempted refreshes, completed/no-change sweeps, candidates awaiting review, and confirmed releases. Keep private contributor data, credentials, internal error payloads, and unreviewed candidate content out of public exports. Live-receipt verification establishes publication identity and integrity, not scientific validity or a human-review credential.

Notify in the calling task on meaningful completion, a candidate needing review, failure, or required user action. Keep repeated unchanged status quiet. A complete no-change monthly result receives one concise completion report; retries should not duplicate it. Email, chat, or GitHub-comment delivery requires an explicitly authorized channel and destination. Do not activate an automation or send external notifications merely because this runbook exists.

## Acceptance checks before operational activation

Confirm a complete manual pilot, immutable attempt records, preserved retry window/baseline/scope, enforced budgets, rejection of partial completion, evidence for every configured scope and current use case, and rejection of unreviewed fingerprint changes. Check that repeated execution does not create duplicate PRs or scientific releases and that public exports exclude private data. Verify publication history against actual deployment evidence. Then obtain the separate activation decision and observe the first real scheduled cycle before declaring scheduled operation proven.

## Extending a partial pilot

A retry preserves its original baseline and search window. To add the remaining configured scope after a deliberately narrow pilot, include `--scope-amendment "Complete the remaining monthly scope after the bounded pilot"` and the full comma-separated scope with `begin --retry-of`. Scope may expand, never shrink; the reason is persisted on the new attempt. The original terminal attempt and evidence remain immutable.

Reports may include `artifact_sha256`, a mapping of repository-relative evidence paths to SHA256 values. Finish and export check every referenced file, so missing or altered pilot evidence blocks export. Publication proofs are also rechecked on export. `check-due` exits 2 for actionable overdue, failed, blocked, or over-budget attempts; an authorized scheduler can use that result for its configured notification channel.
