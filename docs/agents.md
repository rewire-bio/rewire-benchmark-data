# Scheduled agents

Agents that run from GitHub Actions and call the Claude API. They are paid from the API credits linked to the owner's Claude plan (#253). The whole fleet should stay under about $100 a month, so each run writes its token use and estimated cost to the job summary.

## Discovery scan

`.github/workflows/discovery.yml` runs `scripts/agents/discovery.mjs` every day at 08:00 UTC. The prompt is [agents/discovery.md](../agents/discovery.md); change it in a pull request. It replaced a local desktop automation (#254).

What it does:

1. Haiku 5.5 searches the web for AI-for-biology models, methods, benchmarks and datasets announced in the last three days (web search and web fetch server tools). Set the repository variable `DISCOVERY_SCAN_MODEL` to `claude-sonnet-5-5` to scan with Sonnet instead.
2. Haiku 5.5 turns the notes into a candidate list. The script drops candidates that are out of scope or whose name is already in an issue title or the record store.
3. Sonnet 5.5 checks each remaining candidate against its primary sources (up to six a run). Haiku 5.5 turns those notes into fixed fields.
4. The script deduplicates again, on names, aliases, DOIs, arXiv IDs and GitHub or Hugging Face repositories, against:
   - every open and closed issue in this repository, and in rewire.it when it has a token;
   - the names in `data/entities/` (read line by line, not through the record store loader);
   - the article links on rewirebio.io/blog.
5. For each new candidate, up to four a run, it files:
   - **a data issue here**, labelled `entity-request` and `tier-1`, `tier-2` or `tier-3`. The depth tier comes from the candidate's areas by the rule in [tiers.md](tiers.md). Tier 1 and 2 issues ask for full records; tier 3 issues ask for a metadata-only record.
   - **an article issue in rewire.it**, labelled `article`, for every tier. When a published article already covers the resource, the data issue links it instead.

Each issue carries a hidden `discovery-key` marker so later runs recognise it.

Social posting is not part of this agent; it is rewire.it#452. The old automation found candidates on LinkedIn through a signed-in browser. Actions cannot do that, so this scan searches preprint servers, journals, Hugging Face, GitHub and research blogs instead.

### Modes

| Mode | Model calls | GitHub writes | When |
| --- | --- | --- | --- |
| `dry-run` | No | No | Pull requests that touch the agent, and by hand. It reads `tests/agents-discovery-fixtures/` and runs dedup, labelling and issue formatting. |
| `report-only` | Yes | No | By hand, to see what a real run would file. The planned issues are in the job summary and the run artifact. |
| `live` | Yes | Yes | The daily schedule, and by hand. |

Locally: `node scripts/agents/discovery.mjs --dry-run --out /tmp/discovery` writes the planned issue bodies to that folder. The live modes need `npm ci --prefix scripts/agents` first; the SDK is kept out of the root package.

### Switching it on

1. Add the repository or organisation secret `ANTHROPIC_API_KEY`, from the Console organisation linked to the plan's API credits. Without it every run passes with a notice and does nothing.
2. Run "Discovery scan" by hand with mode `report-only` and check the summary: the candidates, the skipped reasons and the cost.
3. Then the daily schedule files issues on its own. Run it by hand in `live` mode if you do not want to wait.
4. Optional, for article issues in rewire.it: set the organisation variable `REWIRE_BOT_APP_ID` and the secret `REWIRE_BOT_PRIVATE_KEY` for a GitHub App installed on rewire.it with issues read and write. Without it, each article request is a section at the### Limits and cost

Limits are in `LIMITS` in the script:

- web searches: 10 for the scan and 3 per candidate;
- web fetches: 5 for the scan and 4 per candidate, each up to 15,000 tokens;
- 10,000 output tokens per research response, including thinking;
- 2 `pause_turn` resumes per research call;
- 6 candidates judged and 4 issue pairs filed per run;
- a 30-minute job timeout.

No further candidate is judged once the run's estimated cost passes $1.

Prices used for the estimate (Claude pricing page, 17 November 2026):

- Sonnet 5.5: $2 input and $10 output per million tokens.
- Haiku 5.5: $0.10 input and $0.50 output, or $0.50 and $2.50 for a request whose prompt is over 100,000 tokens.
- Web search: $10 per 1,000 searches.
- Web fetch: tokens only.

Worst case, from the limits. A research call can make 3 requests, and each request holds every page fetched so far. Search allowances can restart on a resume.

| Step | Input | Output | Searches | Cost |
| --- | --- | --- | --- | --- |
| Scan (Haiku) | 3 requests of up to about 110,000 tokens, at the higher band | 30,000 | 30 | about $0.55 |
| Judge, per candidate (Sonnet) | 3 requests of up to about 82,000 tokens | 30,000 | 9 | about $0.88 |

Judging stops after the $1 mark, so a run can reach about $1.90 and a month about $57.

Typical cost is not measured yet. Expect about $0.10 for the scan and $0.15 to $0.25 per judged candidate, so about $0.60 for a day with three candidates and $15 to $25 a month. Each run's job summary has the real token counts and cost; check them after the first week.

A Sonnet 5.5 request about biology can be refused (refusal category `bio`). Judge calls use the server-side fallback (`fallbacks: "default"`), which retries on another model at that model's price. Haiku 5.5 has no fallback. A refused candidate is skipped and named in the summary. A failed call (rate limit, overload) skips only its own candidate; the summary is written whatever fails.

### Known gaps

- A candidate that matches an existing rewire.it article issue or a record in the store is skipped whole. The old automation filed the missing half of the pair and linked the existing one; this version does not.
- No real API call has been made yet. The first `report-only` run is the first real test of the request shapes and the prompt.

## Intake agent

`.github/workflows/intake.yml` runs `scripts/agents/intake.mjs` when someone adds the `entity-request` label to an issue (#255). The prompt is [agents/intake.md](../agents/intake.md). It turns the issue into a pull request that adds entity records, and it never merges.

Until the claims recollection (#274) it adds entities only: models, methods, benchmarks and datasets, with their sources. It extracts no evaluation, result or claim, whatever the issue asks for.

What it does:

1. The script reads the issue. It stops if the issue is closed, or if an open or merged pull request from `intake/issue-<n>` already exists.
2. Haiku 5.5 reads the issue, opens up to three of its primary sources (web fetch) and drafts the records. A second Haiku call turns the notes into fixed fields. When the issue names URLs, the schema lets the draft cite sources only by those exact URLs.
3. The script drops each proposed entity whose name or alias is already in `data/entities/`. An entity the draft gave no area from `data/vocab/area.ttl` goes on to verification, which can supply its areas.
4. The script, not the model, fetches every source a remaining entity cites. When the draft cites none for an entity, it uses every source the draft lists, and failing that the URLs in the issue body (not social posts or GitHub issue links). It records the SHA-256, media type and retrieval time. It takes the source's name from the page title, its version from what the URL pins (arXiv or bioRxiv version, git commit, otherwise the retrieval date) and its publication status from the host. A URL already in `data/entities/sources.jsonl` is reused, not added again. A bot check page served with HTTP 200 (reCAPTCHA, Cloudflare) counts as not opened. A short reference from the draft, such as `github.com/org/repo`, is resolved to the full URLs that contain it. An entity with no source that opens is dropped.
5. Sonnet 5.5 reads the text of the pages the script fetched and hashed (web fetch only for a page with no text, such as a PDF) and marks each proposed field supported (with a location), corrected or unsupported. Haiku structures the verdicts. It also names, per entity, cited sources that are about a sibling resource or only link to it, and fetched sources from the issue that are about it; the script drops the first and adds the second. A corrected name replaces the drafted one. Each entity carries a key the script gave it (`e1`, `e2`, ...), so a respelt name still matches. Only supported and corrected values are stored. An unconfirmed field is left out and listed in `missing_metadata` with reason `unextracted`. An entity whose description or areas are not confirmed is dropped, because the areas set the depth tier.
6. The script writes `data/omics/intake-<n>-<date>/` with `batch.jsonl`, `notes.md` (every proposed field and whether it was kept) and `review.json`. Then it runs:
   - `scripts/agents/intake-check.ts`, which checks that `normalizeAttributes` leaves every record unchanged (check C13), that each depth tier matches [tiers.md](tiers.md), that there are only entity kinds, and that the release's `validateSnapshot` accepts the batch (for example, every model and benchmark needs `entity_level`);
   - `npm run records -- add`, including its SHACL subset check;
   - `npm run records -- check`.
7. If every check passes, it commits on `intake/issue-<n>`, pushes as the rewire-bot app, opens a pull request, and comments the link on the issue. The pull request closes a `tier-3` issue. For other tiers it only refers to the issue, which stays open for the evaluations that wait for #274. Otherwise it comments why it stopped: out of scope, duplicate, sources not openable, nothing verified, the cost cap, a failed model call, the output of the failing check, or an unexpected error.

Every record has status `discovered`. Models, methods and benchmarks carry `depth_tier` from their areas, and an `entity_level` (model `family`, `checkpoint` or `service`; method `method` or `family`; benchmark `suite` or `challenge`) that the verifier may correct, with `family`, `method` or `suite` when none is valid. Datasets and sources do not, because the attribute registry does not declare it for them. Each review object carries `reviewed_at` and no `date`, `reviewer` `claude-sonnet` (or `claude` if a refusal fallback answered) and a `reviewer_note` naming the run. Sources carry no licence string, because a new one would need a reviewed row in `data/archive/licence-map.tsv`. The agent adds no links between records.

To run it again on the same issue, remove and re-add the label, or run the workflow by hand. A rerun force-pushes the branch only when there is no open or merged pull request for it.

### Modes

| Mode | Model calls | Writes | When |
| --- | --- | --- | --- |
| `dry-run` | No | Batch in the runner only | Pull requests that touch the agent, and by hand. It reads `tests/agents-intake-fixtures/` and runs the real `records add` and `records check` on the fixture batch against the real store. |
| `report-only` | Yes | Batch in the runner only | By hand with an issue number. The job summary and the `intake-<run>` artifact hold the pull request it would open, or the comment it would post, the draft proposal, the verification and the cost. |
| `live` | Yes | Branch, pull request, issue comment | The `entity-request` label, and by hand. |

Locally: `node scripts/agents/intake.mjs --dry-run --store-dir tests/agents-intake-fixtures/entities --root /tmp/intake --no-store-checks` writes the fixture batch under `/tmp/intake` without loading the store. `tests/agents-intake.test.ts` runs the same paths with fakes.

### Setup

It uses the same `ANTHROPIC_API_KEY` secret as discovery, and the rewire-bot app (`REWIRE_BOT_APP_ID` variable, `REWIRE_BOT_PRIVATE_KEY` secret), which needs contents, pull requests and issues write on this repository. Without the key a run writes a notice and passes.

The discovery scan files its data issues as the rewire-bot app, so their `entity-request` label starts the intake. If the app token cannot be made, discovery files them with the workflow's own `GITHUB_TOKEN`, which starts no workflow; then add the label again by hand, or run the intake by hand.

### Limits and cost

Limits are in `LIMITS` in the script:

- draft: up to 3 web fetches, no search;
- verification: up to 5 web fetches and 1 web search;
- each fetch up to 15,000 tokens; 10,000 output tokens per research response; 2 `pause_turn` resumes;
- 6 entities per issue;
- the verification call is not made once the run's estimated cost passes $1.50;
- a 30-minute job timeout.

Prices are the same as for discovery (above). A typical issue should cost about $0.02 for the Haiku draft and $0.15 to $0.40 for the Sonnet verification, which holds every fetched page. The worst case is about $1.50 plus one verification call, about $0.90, so about $2.40. The job summary, the pull request body and `usage.json` in the artifact give each run's real token counts, cost and wall-clock time.

### Known gaps

- Source bytes are hashed, not stored. `npm run archive -- fetch` is a whole-store pass and runs separately.
- No relationship links (for example a method to the models it uses); a reviewer adds them.
- The verification runs in the same job as the draft. It is a second model, not an independent review; the reviewer agent (#256) is meant to provide that.

## Reviewer agent

`.github/workflows/reviewer.yml` runs `scripts/agents/reviewer.mjs` on every pull request the rewire-bot app opens or updates (#256). It reviews intake pull requests independently of the intake agent: its own prompt ([agents/reviewer.md](../agents/reviewer.md)), and Sonnet 5.5 opens the primary sources again itself.

What it does:

1. It reads the `data/omics/*/batch.jsonl` files the pull request adds, and the store, from the pull request's head. The review code and prompt always come from `main`, so a pull request cannot change how it is reviewed.
2. The script checks what is mechanical:
   - each `depth_tier` against the rule in [tiers.md](tiers.md);
   - `entity_level` against the levels the release accepts;
   - names against the store (without the records under review) and against each other;
   - that every cited source is in the pull request or the store;
   - only entity kinds.
3. It fetches every new source again and compares the SHA-256 with the recorded one. A changed hash is reported, not failed, because many pages are generated per request.
4. Sonnet 5.5 reads the text of the pages the reviewer re-fetched itself (web fetch for anything else) and gives every field of every record a verdict: `pass` with the location, `fail` with the problem, or `unverifiable`. It checks source attribution: a page about a sibling model, size or variant does not support a record. It also checks `entity_level` against the vocabulary definitions. Haiku 5.5 only turns the notes into the fixed shape.
5. It posts one review: the problems, then a table per record (field, value, source, verdict, evidence). The verdict is `approve` only when every field passes. A field the model did not return counts as unverifiable.

### Modes

| Mode | Model calls | Posts | Approves or merges |
| --- | --- | --- | --- |
| `dry-run` | No | No | No. Runs on every other pull request, on `tests/agents-reviewer-fixtures/` (the batch of the first intake pull request for #250). |
| `report-only` | Yes | No | No. By hand; the review is in the job summary and the artifact. |
| `comment` | Yes | A comment review | No. The default for bot pull requests. |
| `approve` | Yes | Approval, or changes requested | When every field passes and every other check on the head commit is green (it waits up to 25 minutes), it approves and runs `gh pr merge --auto --merge`. |

The mode for bot pull requests is the repository variable `REVIEWER_MODE` (unset means `comment`).

### Before switching to approve

- GitHub does not let the author of a pull request approve it, and intake pull requests are authored by rewire-bot. Approve mode approves as a second app, rewire-reviewer (repository variable `REVIEWER_APP_ID`, secret `REVIEWER_APP_PRIVATE_KEY`; it needs pull requests and contents write on this repository). The same token enables auto-merge, so the merge, made by an app and not by `GITHUB_TOKEN`, starts the checks and the release on `main`. Without the app the review is posted as a comment and nothing merges.
- Auto-merge is on for this repository.
- A ruleset requiring the 14 `checks (...)` jobs on `main` is planned. Until it is on, auto-merge waits for nothing GitHub requires, so the reviewer itself waits for every other check on the head commit to pass before it approves.
- For the same reason, rewire-bot cannot request changes on its own pull request. In approve mode the rewire-reviewer app posts that verdict; in comment mode it is a comment review that states the verdict.

### Limits and cost

One Sonnet call per review with up to 1 web search and 2 web fetches plus one per distinct source URL (at most 10), 16,000 output tokens, 2 `pause_turn` resumes, effort `high`. No structuring call once the estimated cost passes $1.50. The job summary and `usage.json` in the artifact give each review's tokens and cost.

## Disagreement watcher

`.github/workflows/watcher.yml` runs `scripts/agents/watcher.mjs` after every successful run of "Cut and publish a release", and by hand (#258). It turns new discrepancies between studies ([discrepancies.md](discrepancies.md)) into "Lead:" issues in the format of #209 to #211, so new findings are noticed without someone opening `/contested/`.

What it does:

1. It diffs `discrepancies.json` of the newest knowledge-graph bundle (`kg/<id>`, in publication order) against the bundle published before it. A finding is matched to its earlier self by ID or through `previous_ids`, so a rule change that re-keys findings does not make them new. Resolved findings are not live.
2. For each new medium or high finding, each finding whose severity rose, and each resolved finding that fires again, it files one issue labelled `lead` and `needs-tim` and assigned to timini, so GitHub emails him. The issue links the contested page and gives, from the release data only: each study's verdict and comparison counts, up to four comparisons per study with their values, and the protocols, datasets, metrics and configurations each study used. Names and links come from the release's `records.jsonl.gz`.
3. Sonnet 5.5 writes one paragraph, "Likely explanations to check", from those facts (prompt [agents/watcher.md](../agents/watcher.md)). The paragraph may state no numbers. The script drops it if it contains a link, or any digit outside a name the facts gave (such as ESM-2), or if the call stopped before the end; the issue is then filed without it and says why. Without `ANTHROPIC_API_KEY` the issues are filed without it.
4. Dedupe: every issue carries a hidden `discrepancy-lead` marker with the finding's ID. A finding is never filed twice: not when a lead issue has its marker, and not when a hand-written "Lead:" issue names its ID or one of its `previous_ids`. A finding that already has a lead issue gets a comment instead when its severity rises or it fires again, also on a closed issue (a comment notifies without reopening it). A finding that has follow-up actions but no lead issue is skipped and named in the job summary.
5. At most 5 lead issues a run, most severe first. Any more go into one summary issue (same labels and assignee) listing each finding, whose markers stop later runs filing them separately.
6. A finding that stops being live gets a comment on its open lead issue saying so. The issue is not closed.

Every comment carries a marker with the release ID, so a release run that cuts no release (the watcher then diffs the same two releases again) files and posts nothing.

It records nothing in the store. A `discrepancy_review` revision counts only with status `source_checked`, and every action in `data/vocab/discrepancy-action.ttl` (`investigated` included) and every working state in `discrepancy-state.ttl` (`investigating` included) says someone has looked at the sources. When the watcher files a lead nobody has, so the finding stays `open` until the first real revision. Each lead's "To check" list ends with recording that revision.

Depth tiers: #258 asks for tier 3 findings to go to a weekly digest only. There is no digest yet, so the watcher files leads for every tier and states the finding's tier (the lowest of its two systems) in the issue.

### Modes

| Mode | Model calls | GitHub writes | When |
| --- | --- | --- | --- |
| `dry-run` | No | No | Pull requests that touch the watcher, and by hand. It reads `tests/agents-watcher-fixtures/`: real findings from release `2026-11-19-0528a0ffe3cb`, trimmed and arranged into two new findings, a rise and two findings that stopped. |
| `report-only` | Yes | No | By hand, with optional `current` and `previous` release IDs. The planned issues and comments are in the job summary and the `watcher-<run>` artifact. |
| `live` | Yes | Issues and comments | After every successful release run, and by hand. |

Locally, against any two releases: download `discrepancies.json` from both `kg/<id>` releases and `public.omics.releases.<id>.records.jsonl.gz` from the newer `serving/<id>`, then run `node scripts/agents/watcher.mjs --dry-run --previous <old.json> --current <new.json> --records <records.jsonl.gz> --issues <issues.json> --out /tmp/watcher`. `--issues` takes the issue list as JSON (`number`, `title`, `body`, `state`); without it the fixture list is used.

### Setup and cost

It uses the `ANTHROPIC_API_KEY` secret and the rewire-bot app (`REWIRE_BOT_APP_ID`, `REWIRE_BOT_PRIVATE_KEY`, issues write), like discovery. Without the app it files with `GITHUB_TOKEN`. It refuses to run outside the rewire-bio organisation, and takes the repository from the run, so it moves with the code.

One Sonnet call per filed lead, with no tools and up to 2,000 output tokens. The facts sent for the three medium findings live on 19 November 2026 measured about 1,800, 2,700 and 3,800 input tokens with the prompt, so a call costs about $0.01 to $0.03. The lists sent per study are cut to 10 protocols, datasets and metrics, which bounds a call at about 20,000 input tokens, about $0.06. No call is made once the run's estimated cost passes $1; with at most 5 calls a run, that bound is about $0.30. A release with no new finding costs nothing.

### Known gaps

- Each run compares only the newest bundle with the one before it. If a watcher run fails, or a release is published while one is queued, the next run compares a later pair and findings new in the missed release are never "new" again. Nothing alerts on a failed watcher run. Recover by running it by hand with `previous` and `current` set to the missed pair.
- The lead issue is filed before the website has adopted the release, so its contested page link can show the previous release's findings for a short while.
- The Sonnet call has only been tested with fakes. The first `report-only` run after merge is the first real call.
