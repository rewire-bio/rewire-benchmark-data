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

### Entity-update issues

The monthly entity sweep (below) files `entity-update` issues, and that label starts the intake too. Each issue carries a hidden `entity-update` marker with JSON that says what to do:

- `"action": "add"`: new checkpoints next to an existing record. The issue reads like an entity request (names and primary source URLs), so it takes the same path as one. Its pull request closes the issue, as for tier 3, because the sweep asks for entities only.
- `"action": "update"`: change fields of an existing record (`record_id`, `fields`, `evidence`). Only the fields the attribute registry declares for that kind may change: model `version`, `checkpoint_revision`, `licence` and `access`; method the same without `licence`; benchmark `version`. The script fetches and hashes each evidence page (reusing a stored source with the same URL), and Sonnet 5.5 marks each proposed value supported, corrected or unsupported, as in step 5. Only supported and corrected values are written. The record keeps its ID, status and review object; its `source_locator` gains a sentence naming the issue and where each value is stated, and new evidence sources are added to its `source_ids`. The batch folder `data/omics/update-<n>-<date>/` holds `changed.jsonl` (the record as changed), `batch.jsonl` (new sources), `notes.md` and `review.json`. The checks are `intake-check.ts` on both files, `records -- add` for the new sources, the edit in place, `records -- change <review.json> <batch-dir> <id>` and `records -- check`. The pull request closes the issue.

To run it again on the same issue, remove and re-add the label, or run the workflow by hand. A rerun pushes the branch only when there is no open or merged pull request for it. It deletes a branch left by an earlier run before pushing, so the push never carries main's later changes to workflow files, which GitHub can refuse from a token without the workflows permission. A failed store check or a refused push is commented on the issue and fails the run, so the pipeline alert sees it.

### Modes

| Mode | Model calls | Writes | When |
| --- | --- | --- | --- |
| `dry-run` | No | Batch in the runner only | Pull requests that touch the agent, and by hand. It reads `tests/agents-intake-fixtures/` and runs the real `records add` and `records check` on the fixture batch against the real store. |
| `report-only` | Yes | Batch in the runner only | By hand with an issue number. The job summary and the `intake-<run>` artifact hold the pull request it would open, or the comment it would post, the draft proposal, the verification and the cost. |
| `live` | Yes | Branch, pull request, issue comment | The `entity-request` label, and by hand. |

Locally: `node scripts/agents/intake.mjs --dry-run --store-dir tests/agents-intake-fixtures/entities --root /tmp/intake --no-store-checks` writes the fixture batch under `/tmp/intake` without loading the store. `tests/agents-intake.test.ts` runs the same paths with fakes.

### Setup

It uses the same `ANTHROPIC_API_KEY` secret as discovery, and the rewire-bot app (`REWIRE_BOT_APP_ID` variable, `REWIRE_BOT_PRIVATE_KEY` secret), which needs contents, pull requests and issues write on this repository. The workflow asks for a token limited to those three permissions on this repository only. Without the key a run writes a notice and passes.

The discovery scan files its data issues as the rewire-bot app, so their `entity-request` label starts the intake. If the app token cannot be made, discovery files them with the workflow's own `GITHUB_TOKEN`, which starts no workflow; then add the label again by hand, or run the intake by hand. Both of discovery's app tokens are limited to issues write: one on this repository, one on rewire.it.

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

`.github/workflows/reviewer.yml` runs `scripts/agents/reviewer.mjs` on every pull request the rewire-bot app opens or updates (#256). Its rewire-bot token is limited to this repository, pull requests write and checks read. It reviews intake pull requests independently of the intake agent: its own prompt ([agents/reviewer.md](../agents/reviewer.md)), and Sonnet 5.5 opens the primary sources again itself.

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

- GitHub does not let the author of a pull request approve it, and intake pull requests are authored by rewire-bot. Approve mode approves as a second app, rewire-reviewer (repository variable `REVIEWER_APP_ID`, secret `REVIEWER_APP_PRIVATE_KEY`; it needs pull requests and contents write on this repository, and the workflow asks for a token limited to those two on this repository only). The same token enables auto-merge, so the merge, made by an app and not by `GITHUB_TOKEN`, starts the checks and the release on `main`. Without the app the review is posted as a comment and nothing merges.
- Auto-merge is on for this repository.
- A ruleset requiring the 14 `checks (...)` jobs on `main` is planned. Until it is on, auto-merge waits for nothing GitHub requires, so the reviewer itself waits for every other check on the head commit to pass before it approves.
- For the same reason, rewire-bot cannot request changes on its own pull request. In approve mode the rewire-reviewer app posts that verdict; in comment mode it is a comment review that states the verdict.

### Limits and cost

One Sonnet call per review with up to 1 web search and 2 web fetches plus one per distinct source URL (at most 10), 16,000 output tokens, 2 `pause_turn` resumes, effort `high`. No structuring call once the estimated cost passes $1.50. The job summary and `usage.json` in the artifact give each review's tokens and cost.

## Disagreement watcher

`.github/workflows/watcher.yml` runs `scripts/agents/watcher.mjs` after every successful run of "Cut and publish a release", and by hand (#258). It turns new discrepancies between studies ([discrepancies.md](discrepancies.md)) into "Lead:" issues in the format of #209 to #211, so new findings are noticed without someone opening `/contested/`.

What it does:

1. It diffs `discrepancies.json` of the newest release's knowledge-graph bundle (`kg/<id>`, releases in the order `serving/<id>` was cut) against the release the last watcher run in the same mode compared to, or, with no such run, the release before it. A finding is matched to its earlier self by ID or through `previous_ids`, or, failing both, by the stable parts of its key (rule, systems, anchor, metric and study keys) among earlier findings whose ID has gone. `previous_ids` are written only for findings with a review claim, so when a rule change alters the key itself, an unreviewed finding shows as new and its old ID as gone; the "gone" comment then says the finding may continue under a new ID. When one finding covers several earlier ones, all of them are matched. Resolved findings are not live.
2. For each new medium or high finding, each finding whose severity rose, and each resolved finding that fires again, it files one issue labelled `lead` and `needs-tim` and assigned to timini, so GitHub emails him. The issue links the contested page and gives, from the release data only: each study's verdict and comparison counts, up to four comparisons per study with their values, and the protocols, datasets, metrics and configurations each study used. Names and links come from the release's `records.jsonl.gz`.
3. Sonnet 5.5 writes one paragraph, "Likely explanations to check", from those facts (prompt [agents/watcher.md](../agents/watcher.md)). The paragraph may state no numbers and refers to studies by role. The script drops it if it contains a link, any digit outside a name the facts gave (such as ESM-2, or a word of a name such as ESM-1b or a year in a study name), a count or fraction in words ("nine of twelve", "three", "half"; "one" and "the two systems" are allowed), or if the call stopped before the end; the issue is then filed without it and says why. Without `ANTHROPIC_API_KEY` the issues are filed without it.
4. Dedupe: every issue carries a hidden `discrepancy-lead` marker with the finding's ID. A finding is never filed twice: not when a lead issue has its marker, and not when a hand-written "Lead:" issue names its ID or one of its `previous_ids`. A finding that already has a lead issue gets a comment instead when its severity rises or it fires again, also on a closed issue (a comment notifies without reopening it). A finding that has follow-up actions but no lead issue is skipped and named in the job summary.
5. At most 5 lead issues a run, most severe first. Any more go into one summary issue (same labels and assignee) listing each finding, whose markers stop later runs filing them separately.
6. A finding that stops being live gets a comment on its open lead issue saying so. The issue is not closed.

After a release run that cuts no release, the watcher stops early: the last run in its mode already compared the newest release, so it makes no model call. Every comment also carries a marker with the release ID, so a repeated comparison files and posts nothing.

It records nothing in the store. A `discrepancy_review` revision counts only with status `source_checked`, and every action in `data/vocab/discrepancy-action.ttl` (`investigated` included) and every working state in `discrepancy-state.ttl` (`investigating` included) says someone has looked at the sources. When the watcher files a lead nobody has, so the finding stays `open` until the first real revision. Each lead's "To check" list ends with recording that revision.

Depth tiers: #258 asks for tier 3 findings to go to a weekly digest only. The weekly digest does not route findings by tier yet, so the watcher files leads for every tier and states the finding's tier (the lowest of its two systems) in the issue.

### Modes

| Mode | Model calls | GitHub writes | When |
| --- | --- | --- | --- |
| `dry-run` | No | No | Pull requests that touch the watcher, and by hand. It reads `tests/agents-watcher-fixtures/`: real findings from release `2026-11-19-0528a0ffe3cb`, trimmed and arranged into two new findings, a rise and two findings that stopped. |
| `report-only` | Yes | No | After every successful release run (the default), and by hand with optional `current` and `previous` release IDs. The planned issues and comments are in the job summary and the `watcher-<run>` artifact. |
| `live` | Yes | Issues and comments | After every successful release run once the repository variable `WATCHER_MODE` is `live`, and by hand. |

To go live, set the repository variable: `gh variable set WATCHER_MODE --body live`. Delete it (or set it to `report-only`) to go back. The first live run after the switch compares the newest release with the one before it, since no live run has recorded a release yet; run it by hand with `previous` set to an earlier release to cover more.

Locally, against any two releases: download `discrepancies.json` from both `kg/<id>` releases and `public.omics.releases.<id>.records.jsonl.gz` from the newer `serving/<id>`, then run `node scripts/agents/watcher.mjs --dry-run --previous <old.json> --current <new.json> --records <records.jsonl.gz> --issues <issues.json> --out /tmp/watcher`. `--issues` takes the issue list as JSON (`number`, `title`, `body`, `state`); without it the fixture list is used.

### Setup and cost

It uses the `ANTHROPIC_API_KEY` secret and the rewire-bot app (`REWIRE_BOT_APP_ID`, `REWIRE_BOT_PRIVATE_KEY`, issues write), like discovery. Without the app it files with `GITHUB_TOKEN`. It refuses to run outside the rewire-bio organisation, and takes the repository from the run, so it moves with the code.

One Sonnet call per filed lead, with no tools and up to 2,000 output tokens. The script checks the paragraph: no links, no numbers of its own, and at most six sentences (it counts them, erring low). A paragraph that fails is sent back once with the reason; if the rewrite fails too, the lead is filed without it and says why. The facts sent for the three medium findings live on 19 November 2026 measured about 1,800, 2,700 and 3,800 input tokens with the prompt, so a call costs about $0.01 to $0.03. The lists sent per study are cut to 10 protocols, datasets and metrics, which bounds a call at about 20,000 input tokens, about $0.06. No call is made once the run's estimated cost passes $1; with at most 5 leads and one rewrite each, that bound is about $0.60. A release with no new finding costs nothing.

### Known gaps

- A run after a release compares the newest release with the last one a successful run in the same mode compared to, read from that run's artifact (kept 30 days). So a failed watcher run, a release run that failed after publishing its bundle, or a run replaced in the queue does not lose findings: the next run compares across the gap and lists the releases in between in its job summary. A finding that appeared and went away inside the gap is not reported. If the artifact has expired the run falls back to the release before the newest. A failed watcher run opens or updates the `pipeline-broken` issue, as a failed run of any agent does (docs/release.md).
- The lead issue is filed before the website has adopted the release, so its contested page link can show the previous release's findings for a short while.
- The Sonnet call has only been tested with fakes. The first `report-only` run after merge is the first real call.

## Weekly digest

`.github/workflows/digest.yml` runs `scripts/agents/digest.mjs` every Monday at 06:30 UTC (#259). In live mode (see Modes) it opens one issue, "Weekly digest: <from> to <to>", labelled `digest` and assigned to timini, and closes the previous week's with a link to the new one. A second live run in the same ISO week (UTC, Monday to Sunday) updates that week's issue instead of opening another, whatever the day.

The window starts where the previous digest ended (the `until` in its issue's hidden marker), so consecutive digests neither overlap nor leave a gap when a scheduled run starts late. A re-run in the same week keeps that week's start. With no open digest to continue from, or one more than 31 days old, it covers the last `--days` days (default 7). Report-only and dry runs always use the last `--days` days.

Every fact is read from GitHub, the release assets and `deployment.json` on the site. No model decides any of them. Sections, each a count with links:

- **Waiting on Tim:** open issues labelled `needs-tim`, open pull requests requesting his review, and open agent pull requests with the reviewer's latest verdict. When GitHub recorded a review state that contradicts the verdict in its body (an "approve" body recorded as changes requested), it says so.
- **What the agents did:** discovery issues filed here and article issues in other repositories (found by their `discovery-key` marker), intake pull requests (`intake/` branches) opened, merged and closed, and reviewer verdicts with failed and unverifiable field counts (parsed from the reviewer's headline).
- **Runs and spend:** runs per agent (discovery, intake, reviewer and the monthly entity sweep), links to failed runs, and spend summed from each run's `usage.json` artifact. A run counts when its agent job ran: it left an artifact or failed. Pull request dry runs of discovery and intake do not count. A run without a readable `usage.json` is shown as not recorded. It reads at most 100 artifacts, newest first, after dropping those of pull request dry runs; a counted run left out by that cap is shown as not read, not as missing.
- **Releases:** `serving/` releases cut in the window, which one the site serves, and whether the newest is live.
- **Agent records still provisional:** records from `data/omics/intake-*` batches on main whose status in `data/entities` is still `discovered` or `needs_review`.
- **Discrepancies:** the newest `kg/` release's `discrepancies.json` compared with the newest one published before the window: new (public ones linked to `/contested/`), resolved, and stopped firing; the number open, meaning not settled, as on the site and over MCP; findings settled since the baseline that still fire; then the open `Lead:` issues.
- **Pipeline:** open `pipeline-broken` issues, and those closed in the window, in every repository it can read.

Tier 1 ranking changes and the gap scanner's proposals, also asked for in #259, are not in it yet.

### Modes

| Mode | Model calls | GitHub writes | When |
| --- | --- | --- | --- |
| `dry-run` | No | No | Pull requests that touch the digest, and by hand. It reads `tests/agents-digest-fixtures/`. |
| `report-only` | Summary only | No | The Monday schedule while `DIGEST_MODE` is unset, and by hand (the default for manual runs). The digest is in the job summary and the `digest-<run>` artifact. |
| `live` | Summary only | The digest issue | The Monday schedule once the repository variable `DIGEST_MODE` is `live`, and by hand. |

To post the issue every Monday, set the repository variable: `gh variable set DIGEST_MODE --body live`. Deleting it returns the schedule to report-only.

Locally: `GH_TOKEN=$(gh auth token) node scripts/agents/digest.mjs --report-only --no-summary --out /tmp/digest`. A personal token can read more than the bot, so a local run may cover repositories the scheduled one skips.

### Setup and cost

It posts as the rewire-bot app (`REWIRE_BOT_APP_ID`, `REWIRE_BOT_PRIVATE_KEY`), which needs issues write here. The token is made for every repository the app is installed on but limited to issues write and contents, pull requests and metadata read, so it cannot push; the digest reads the other repositories in `DIGEST_REPOS` (a repository variable, comma separated; default `rewire.it` and `rewire-database` under the same owner) and lists any it cannot read under "Not covered". Without the app it posts with the workflow's own token and reads only this repository. Workflow runs and artifacts are read with the workflow's own token (`actions: read`). The repository comes from `GITHUB_REPOSITORY`, so it moves with the workflow file.

With `ANTHROPIC_API_KEY` set, Haiku 5.5 writes a three-sentence summary at the top from the computed counts only (prompt [agents/digest.md](../agents/digest.md)). The call is skipped if its worst-case cost would pass $0.25; a typical one costs well under $0.01. Without the key, if the call fails, would pass the cap, or stops before it finishes, the digest has no summary and says why under "Not covered". A list cut short by its page limit is noted there too, and a body over GitHub's size limit is cut before the hidden marker so the next run still finds the issue.

## Monthly entity sweep

`.github/workflows/sweep.yml` runs `scripts/agents/sweep.mjs` at 05:00 UTC on the 1st of each month (#257). It checks whether the entities in the store have changed at their own sources and files one `entity-update` issue per entity with a confirmed change, which the intake agent turns into a pull request. The prompt is [agents/sweep.md](../agents/sweep.md).

Which entities: models, methods, benchmarks and use cases by `attributes.depth_tier` ([tiers.md](tiers.md)). Tier 1 every month; tier 2 in January, April, July and October; tier 3 never. Datasets carry no depth tier and are not swept. A manual run can choose `tier` (1, 2 or 1,2), `limit` or `ids`.

What it checks, deterministic first:

1. **Repositories.** The GitHub and Hugging Face repositories in each entity's sources and in its own `version`, `licence` and `access` text. A repository that the record's own fields name is the entity's own. So is one whose name matches the entity's, unless records of more than one name claim it (an umbrella such as `facebookresearch/esm` for ESM-1v, ESM-2 and ESMFold, or `songlab-cal/tape` for TAPE and TAPE LSTM); then only a record named exactly as the repository keeps it. Any other (a shared leaderboard repository cited by twenty models, or a benchmark pipeline that wraps many models) is never the source of a record change, and no model is asked about it: a model's answer on such a pair changed between runs on the same store. If it was archived, moved or is gone, the job summary lists it under "Needs a human look", unless a record that owns the repository already reports the same event. Each repository is read once from the APIs:
   - GitHub: archived, moved (the API's `full_name` differs), licence, releases (not drafts or prereleases), and the tags, when a record named exactly for the repository has sources that pin one commit in it (a `blob`, `tree` or `commit` URL, or a source version that is a full SHA);
   - Hugging Face: moved, licence, and newer repositories by the same author whose name starts with the checkpoint's base name (`gLM2_650M` gives `gLM2`). The author is taken from the canonical ID the API returns, because the API's author filter is case-sensitive.

   A read that fails (a 403 or 429 rate limit, a timeout) is not treated as an empty answer: the job summary counts and lists every repository, release list or checkpoint list that was not read.
2. **Candidates.** A version candidate needs a record that tracks a version (it has one, or its version is missing for a reason other than `inapplicable`) and a repository named exactly for the record; a release of a repository named for more than the entity (ViennaRNA for RNAfold) versions a shared package and is only listed under "Needs a human look". When the record's sources pin one commit, the record describes that commit: a record with no version gets a `version_gap` candidate for the tag at that commit (mRNABench pinned at 74f96b8e gets v1.3.0, not the newer v1.3.2), and a newer release is listed under "Needs a human look", never proposed. Sources that pin different commits, or a commit with no single tag, give no candidate. Without a pinned commit, a release published after the stored sources were retrieved whose tag the record does not mention is a `release` candidate when the record has a version; when it has none, nothing says which version the record describes, so the release is only listed under "Needs a human look". A model `family` record with no version gets none: a code release is not the version of a model family. A licence that the record's licence text does not name. An archived or moved repository, for kinds with an `access` field. A new Hugging Face checkpoint created after the stored sources and not named anywhere in the store.
3. **Benchmark pages.** A benchmark's project page (not a paper host) is fetched and its SHA-256 compared with the stored `artifact_sha256`. Each page is fetched once, whatever the number of records citing it. A changed page goes to Haiku, which says whether it names a newer version than the record's. Up to 25 changed pages a run; the summary says how many were over the cap or could not be fetched, and how many cited pages were skipped because their address does not name the benchmark.
4. **Confirmation.** Sonnet 5.5 (low effort, refusal fallback on) gets each entity's record and its candidates with the facts the APIs returned, and says for each whether it is real and what the field should now say. Only confirmed changes are filed, and only when Sonnet's text carries what the APIs observed: the release tag, the new location or the licence, or the word archived. A new checkpoint is filed under its observed ID, never under a name the model wrote.
5. **Dead links.** Every source URL of the swept entities, once: HEAD, then GET if HEAD fails. Dead means 404 or 410 on both, or a host that does not resolve. Anything else (401, 403, 429, 5xx, timeouts, bot walls) is blocked and only listed in the job summary; most of these are paper hosts rate-limiting a bulk check.

What it files, in live mode, as the rewire-bot app:

- One issue per entity and action, labelled `entity-update` and the entity's `tier-N`: "Update <name>: ..." for field changes, "Add new checkpoint ..." for new checkpoints. The body has a table of stored and proposed values with the evidence, and the hidden marker the intake agent reads (see "Entity-update issues" under the intake agent).
- At most 15 a run, tier 1 first. Any more go into one summary issue labelled `entity-sweep`; the next month's run files them if they still hold.
- One issue for the run's new dead links, labelled `entity-sweep` (not `entity-update`, so the intake does not pick it up), which also lists archived or moved repositories of benchmarks and use cases, which have no `access` field. A missing repository whose link is in the dead list is one event: it gets one line (the dead link) and keeps its hidden marker.

Each event is reported in one place. Issue bodies are never cut short: the table and the facts are written whole.

Dedupe: each change has a hidden `entity-update-key` marker (record, change type and value). A change whose key is in any issue, open or closed, is not filed again, so a rejected change is not proposed every month. A new checkpoint is keyed by its Hugging Face ID alone, so when a family record and its checkpoint records all find it, one add issue is filed, by the first record in tier and kind order, naming the others. Dead links and repository changes on benchmarks and use cases are listed once: not again while any sweep issue, open or closed, lists them.

Entities only: it never proposes results, scores or leaderboard values, only metadata (versions, checkpoints, licences, access) and new checkpoint records. #257 also asks for new leaderboard values and retracted or revised preprints; the first waits for the store rebuild, and the second is not covered yet. It does not run the `database-refresh` cycle (`docs/refresh.md`), whose schedule in `maintenance/schedule.json` stays `planned`; it only works the metadata part of that cycle.

### Modes

| Mode | Model calls | GitHub writes | When |
| --- | --- | --- | --- |
| `dry-run` | No | No | Pull requests that touch the sweep, and by hand. It reads `tests/agents-sweep-fixtures/`: a small store, the HTTP and API answers, the model answers and the existing issues. |
| `report-only` | Yes | No | The monthly schedule while `SWEEP_MODE` is unset, and by hand (the default for manual runs). The planned issues are in the job summary and the `sweep-<run>` artifact (`plan.json`, `issues/*.md`, `usage.json`). |
| `live` | Yes | The issues | The schedule once the repository variable `SWEEP_MODE` is `live` (`gh variable set SWEEP_MODE --body live`), and by hand. |

Without `ANTHROPIC_API_KEY` the deterministic checks still run and the summary lists every candidate as not confirmed; nothing is filed. Locally: `READ_TOKEN=$(gh auth token) node scripts/agents/sweep.mjs --report-only --tier 1 --out /tmp/sweep` (a full tier 1 pass of about 590 entities took under two minutes).

### Setup and cost

The app token is limited to issues write on this repository. Issues filed with it start the intake agent; if the token cannot be made, the issues are filed with the workflow's own token, which starts no workflow, and the summary says to re-add the label by hand. GitHub API reads use the workflow's own token for its rate limit. The repository comes from `GITHUB_REPOSITORY` and must belong to rewire-bio. It never starts a GPU run or anything billable other than the Anthropic API.

No model call is made whose worst case (prompt length and `max_tokens`) would take the run past $2. Expected cost per run: a few Haiku page calls at well under $0.01 each, and one Sonnet call per entity with candidates at about $0.01 to $0.02, so under $0.50 for a month with twenty candidates. `usage.json` in the artifact has the real figure, and the weekly digest adds it to the spend table.

### Known gaps

- Repository ownership by name match misses an entity whose repository has an unrelated name and is not named in its fields. Such a repository is never checked for record changes; the summary lists it only if it moved, was archived or is gone.
- Releases without a GitHub release (tags only) are not seen, because tags carry no date.
- A dead source is reported, not replaced: finding where it moved is a person's job.

