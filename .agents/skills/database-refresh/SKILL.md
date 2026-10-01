---
name: database-refresh
description: Run, resume, or assess a bounded monthly refresh of benchmark evidence and use-case coverage using durable maintenance receipts. Use in the benchmark-data producer; publication and benchmark execution remain separate workflows.
---

# Monthly database refresh

Read `docs/database-refresh.md` and `maintenance/schedule.json` before starting. Work in the benchmark-data producer repository. The website consumes its reviewed artifacts; scientific benchmark execution belongs in the benchmark runner repository.

Inspect `npm run refresh -- status`, existing attempt records, and linked pull requests before creating work. Use the CLI to record lifecycle state, immutable terminal attempts, frozen coverage windows, and PR links. Do not rewrite finished receipts or create duplicate attempts/PRs for the same cycle. `resume` inspects the saved attempt; a retry is an explicit new `begin --retry-of` attempt with the same window, baseline, and scope.

Cover every configured scope: the nine research lanes, scope-screen, source-resolution, existing sources, and all current use cases. Enumerate use cases from `data/omics/use-cases/inputs.json`, never from a stale remembered count. Check new work, revisions to existing sources and protocols, corrections/retractions, and unresolved gaps. Follow current primary sources; record queries, retrieval dates, URLs, decisions, and affected record IDs. An inaccessible source is a gap, not a completed review. The GitHub HEAD checker covers only one portion of this work.

Use independent workers for research and review where available, assigning distinct report paths and portions of the shared query/time budget. Preserve scientific record IDs, numerical values, exact protocol scopes, source bytes, and historical releases. Stage proposed changes for independent review using existing ingestion gates. Never silently refresh a review fingerprint to clear a validation failure. A documented no-change outcome is valid only when the entire configured scope was checked.

Finish with a substantive report matching the runbook schema. Mark partial or inaccessible coverage `blocked`, execution errors `failed`, and complete sweeps `completed` with `no_change` or `review_required`. Automated review must identify its actual actor and method and must not be described as qualified human scientific review or independent experimental reproduction.

The schedule is planned, not active. Run and assess a full manual pilot before a separate explicit operational activation decision. Do not create an automation merely by reading this skill or the schedule file. A bounded partial pilot does not satisfy scheduled-cycle acceptance.

Summarize meaningful completion, review requirements, failures, or required user action in the calling task. Keep repeated unchanged status quiet. Do not send email, chat, or GitHub comments without authorization. PR links are audit metadata; publication is confirmed separately against a live deployment receipt. Never equate candidate generation, a passing review, or PR merge with successful publication.
