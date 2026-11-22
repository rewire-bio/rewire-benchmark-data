# Scheduled agents

Agents that run from GitHub Actions and call the Claude API. They are paid from the API credits linked to the owner's Claude plan (#253). The whole fleet should stay under about $100 a month, so each run writes its token use and estimated cost to the job summary.

## Discovery scan

`.github/workflows/discovery.yml` runs `scripts/agents/discovery.mjs` every day at 08:00 UTC. The prompt is [agents/discovery.md](../agents/discovery.md); change it in a pull request. It replaced a local desktop automation (#254).

What it does:

1. Haiku 5.5 searches the web for AI-for-biology models, methods, benchmarks and datasets that the database does not hold yet (web search and web fetch server tools). It makes one call for each of three lanes: genomics, proteins, and cells and other biology. Set the repository variable `DISCOVERY_SCAN_MODEL` to `claude-sonnet-5-5` to scan with Sonnet instead.
2. Haiku 5.5 turns each lane's notes into a candidate list. The script drops candidates whose name is already in an issue title or the record store, then those the judge rejected in the last 30 days, then those triage calls out of scope or weak.
3. Sonnet 5.5 checks each remaining candidate against its primary sources (up to six a run, taken from the lanes in turn). It is given the records and requests whose name differs only by a version or size. Haiku 5.5 turns those notes into fixed fields. Notes that end with SKIP are never filed, whatever the fixed fields say, and notes cut off at the output limit are dropped.
4. The script deduplicates again, on names, aliases, DOIs, arXiv IDs and GitHub or Hugging Face repositories, against:
   - every open and closed issue in this repository, and in rewire.it when it has a token;
   - the names in `data/entities/` (read line by line, not through the record store loader);
   - the article links on rewirebio.io/blog.
5. For each new candidate, up to four a day, it files:
   - **a data issue here**, labelled `entity-request` and `tier-1`, `tier-2` or `tier-3`. The depth tier comes from the candidate's areas by the rule in [tiers.md](tiers.md). Tier 1 and 2 issues ask for full records; tier 3 issues ask for a metadata-only record. The intake agent reads the `tier-3` label to decide whether its pull request closes the issue.
   - **an article issue in rewire.it**, labelled `article`, for every tier. When a published article already covers the resource, the data issue links it instead.

### What counts as new

New means new to the database, not released this week. The scan looks first at resources released or first announced in the last 30 days (`--lookback-days`), and an older resource is still a candidate when the database lacks it. Release age never drops a candidate. It only decides the order: within a lane, candidates released inside the 30 days are judged first, then undated ones, then older ones.

Why 30 days and not 3. The first three scheduled runs (18 to 20 November 2026) asked for the last three days and filed nothing: 9 of their 18 candidates were dropped for their release date alone. In the same month the old local automation filed resources that were weeks or months old when it found them: RFD4-Proteína 22 days after release, MIMOSA 48 days after its preprint, SEPIQ 2026 five months after publication. A resource usually becomes findable some weeks after its date: the preprint is indexed, the code and weights follow, other papers start to cite it. Thirty days covers that lag and keeps the search queries specific to a recent period. A longer period costs nothing more, because the search count is fixed.

### Known resources

Three checks keep a known resource from being filed twice.

- The scan is shown the titles of the 60 most recent requests in this repository and told not to return them. A request is an issue this script filed, one labelled `entity-request`, or one titled "Add <Name> ...".
- The script does not rely on that. Before judging, it drops every candidate whose name or alias is in the title of any issue, open or closed, or in the record store. The scheduled run of 20 November returned five names from its own list; `tests/agents-discovery.test.ts` replays that reply and checks that none reaches the judge.
- After judging, it checks again with the primary identifiers.

Issues filed by hand or by the old automation have no marker, so they are matched by the name in the title, whoever opened them. Names are compared without accents and with letters split from digits, so "RFD4-Proteina" matches "RFD4-Proteína" and "BioEmu2" matches "BioEmu-2".

A name of four characters or more is also compared as a spelling: without spaces or hyphens, without a "v" before a version number, and without a trailing ".0". So "Torch Craft", "HyPLMFlash", "Enchant-3" and "BioEmu 2.0" match the requests for TorchCraft, HyPLM-Flash, Enchant v3 and BioEmu-2, and "Alpha Genome" matches a stored AlphaGenome. In a title, one word (what stands between two spaces) and the version after it are compared; two separate words are not joined, so "the tier rule" does not match a resource called TierRule.

A different version or a size is not a match: "BioEmu-3", "ESM3" and "ESM-2 650M" go to the judge. The judge is told which records and requests have the same name without its version or size, and to skip the candidate when it is one of them under another spelling, or only a size, checkpoint or minor release of it. The judge is not told that the database lacks the resource. It is told what the script compared.

The script stops before any model call when it reads no name from `data/entities/`. A store that had moved, or a checkout without it, would otherwise make every stored resource look new.

### Rejected candidates

A candidate the judge rejects is remembered for the lookback period (30 days) and not judged again in that time. Without this, the same rejected candidates would take the six judge slots every day. The scan is also told not to return them. Only a SKIP verdict is remembered: a refusal, a failed call or a filed candidate is not.

The list is `discovery-state/rejected.json` (`--state`), kept between runs in the Actions cache. A cache cannot be overwritten, so each run saves under its own key and restores the newest. GitHub removes a cache that is not read for seven days, and a cache can be deleted by hand. Losing it costs judging those candidates once more and nothing else. `report-only` runs read and write the list too; dry runs do not.

The cap of four is per day. The script counts the issues it already filed on the run date (by their marker and creation date), so a second live run on the same day files only the remainder. The day is the UTC date, so a run just before 00:00 UTC and one just after can file four each. Issues without the marker, such as those of the old local automation, are not counted. `--max-pairs` must be a whole number; anything else stops the run.

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
4. Optional, for article issues in rewire.it: set the organisation variable `REWIRE_BOT_APP_ID` and the secret `REWIRE_BOT_PRIVATE_KEY` for a GitHub App installed on rewire.it with issues read and write. Without it, each article request is a section at the end of its data issue.

### Limits and cost

Limits are in `LIMITS` in the script:

- web searches: 8 for each of the three scan lanes (24 a run) and 3 per judged candidate;
- web fetches: 2 per scan lane and 4 per judged candidate, each up to 15,000 tokens;
- 10,000 output tokens per research response, including thinking;
- 2 `pause_turn` resumes per research call. The script counts searches and fetches across resumes and gives each resume only what is left, with a minimum of one. A response that does not report its tool use is counted as having used everything the request allowed, in the allowance and in the cost estimate;
- 6 candidates judged a run and 4 issue pairs filed a day;
- a 30-minute job timeout.

No further scan lane starts when the scan would pass $0.35, and no further candidate is judged once the run's estimated cost passes $1. The first lane rotates by day, so a lane that the budget check skips one day runs first on another.

Prices used for the estimate (Claude pricing page, 17 November 2026):

- Sonnet 5.5: $2 input and $10 output per million tokens.
- Haiku 5.5: $0.10 input and $0.50 output, or $0.50 and $2.50 for a request whose prompt is over 100,000 tokens.
- Web search: $10 per 1,000 searches.
- Web fetch: tokens only.

The scan budget is about $0.35 a run. Search fees are nearly all of it. Measured on the scheduled runs of 18 to 20 November 2026, one scan call with 9 or 10 searches and one fetch:

| Run | Searches | Prompt tokens (mostly cache reads) | Cost |
| --- | --- | --- | --- |
| 18 November | 9 | 73,000 | $0.095 |
| 19 November | 10 | 110,000, in the higher price band | $0.124 |
| 20 November | 10 | 85,000 | $0.105 |

Tokens were $0.005 to $0.02 of each. Three lanes of 8 searches are 24 searches, so expect $0.24 in search fees and $0.27 to $0.30 in all. With one extra search for each of the two resumes of each lane, the search fees can reach $0.30. Each lane holds 8 searches, not 24, so its prompt should stay under 100,000 tokens.

Worst case, from the limits, if nothing is cached. A research call can make 3 requests, and each request holds every page fetched so far.

| Step | Input | Output | Searches | Cost |
| --- | --- | --- | --- | --- |
| Scan, per lane (Haiku) | 3 requests of up to about 110,000 tokens, at the higher band | 30,000 | 10 | about $0.34 |
| Judge, per candidate (Sonnet) | 3 requests of up to about 82,000 tokens | 30,000 | 5 | about $0.84 |

A lane starts only while the scan has spent $0.25 or less, so the uncached worst case for the scan is about $0.59. Judging stops after the $1 mark, so a run can reach about $1.84 and a month about $55.

Two things are outside that figure. A judge request that Sonnet refuses is run again on a fallback model, and a model missing from the price table is estimated at Opus prices, twice Sonnet's, so one judge call can cost about $1.65 and a run about $2.65. The SDK retries a failed request up to three times; a retried request that was billed is not in the estimate.

Each data issue filed as the rewire-bot app starts one intake run, and an intake pull request starts one reviewer run. Four issues a day is up to 120 intake runs and 120 reviewer runs a month. Their cost is in the intake and reviewer sections below and is not part of the discovery figures here. Watch the weekly digest's spend against the $100 a month for the fleet, and lower `max_pairs` in the workflow if it runs over.

Typical cost of judging is not measured yet, because no run has reached the judge. Expect $0.15 to $0.25 per judged candidate, so about $0.90 for a day with three candidates and $15 to $30 a month. Each run's job summary has the real token counts and cost.

A Sonnet 5.5 request about biology can be refused (refusal category `bio`). Judge calls use the server-side fallback (`fallbacks: "default"`), which retries on another model at that model's price. Haiku 5.5 has no fallback. A refused candidate is skipped and named in the summary. A failed call (rate limit, overload) skips only its own candidate; the summary is written whatever fails.

### Known gaps

- A candidate that matches an existing rewire.it article issue or a record in the store is skipped whole. The old automation filed the missing half of the pair and linked the existing one; this version does not.
- The scan and triage calls have run against the API (18 to 20 November 2026). The judge call, the filing path and the lane prompts have not: no candidate has reached the judge yet. Run `report-only` once after a prompt change and read the skipped reasons.
- The search count across `pause_turn` resumes relies on `usage.server_tool_use` in each response. It has not been observed on a resumed scan. When the field is missing the script counts the full allowance, so a resumed call then gets one search and one fetch.
- A candidate whose name or alias is a common word in some issue title ("Atlas", "Evo", "State", "Cell") is dropped as known. The summary lists it under Skipped with the issue it matched, so it can be filed by hand. Title matching was left strict for the first live runs.
- The rejected-candidate cache has not run in Actions yet. The script side is tested; the restore and save steps first run on the first scheduled or manual run after #339.
- A resource stored under a different name, not just another spelling or version, is not recognised by the script. The judge and the intake agent's duplicate check are what catch it.

## Intake agent

`.github/workflows/intake.yml` runs `scripts/agents/intake.mjs` when someone adds the `entity-request` label to an issue (#255). The prompt is [agents/intake.md](../agents/intake.md). It turns the issue into a pull request that adds entity records, and it never merges. Live runs queue, one at a time, and each works every issue that waits (Queue and rate limits, below). An intake pull request that comes to conflict with main is rebuilt on it (Refresh of a conflicting pull request, below).

Until the claims recollection (#274) it adds entities only: models, methods, benchmarks and datasets, with their sources. It extracts no evaluation, result or claim, whatever the issue asks for.

What it does:

1. The script reads the issue. It stops if the issue is closed, or if an open or merged pull request from `intake/issue-<n>` already exists. It starts the knowledge graph server (below) at the same time, so the graph is loaded by the time the draft is.
2. Haiku 5.5 reads the issue, opens up to three of its primary sources (web fetch) and drafts the records. A second Haiku call turns the notes into fixed fields. When the issue names URLs, the schema lets the draft cite sources only by those exact URLs.
3. The script drops each proposed entity whose name or alias is already in `data/entities/`. An entity the draft gave no area from `data/vocab/area.ttl` goes on to verification, which can supply its areas.
4. The script, not the model, fetches every source a remaining entity cites. When the draft cites none for an entity, it uses every source the draft lists, and failing that the URLs in the issue body (not social posts or GitHub issue links). It records the SHA-256, media type and retrieval time. It takes the source's name from the page title, its version from what the URL pins (arXiv or bioRxiv version, git commit, otherwise the retrieval date) and its publication status from the host. A URL already in `data/entities/sources.jsonl` is reused, not added again. A bot check page served with HTTP 200 (reCAPTCHA, Cloudflare) counts as not opened. A short reference from the draft, such as `github.com/org/repo`, is resolved to the full URLs that contain it. An entity with no source that opens is dropped.
5. For each remaining entity the script asks the knowledge graph for the store records that may be the same resource (the server's possible duplicates for a record with this name and kind, and for each alias) and for records of the kinds a link from it may reach. A possible duplicate needs a ruling only when it has the same kind (or model against method) and shares at least half its distinctive words with the name: words such as "benchmark" or a bare version number do not count.
6. Sonnet 5.5 reads the text of the pages the script fetched and hashed (web fetch only for a page with no text, such as a PDF) and marks each proposed field supported (with a location), corrected or unsupported. Haiku structures the verdicts. It also names, per entity, cited sources that are about a sibling resource or only link to it, and fetched sources from the issue that are about it; the script drops the first and adds the second. A corrected name replaces the drafted one. Each entity carries a key the script gave it (`e1`, `e2`, ...), so a respelt name still matches. Only supported and corrected values are stored. An unconfirmed field is left out and listed in `missing_metadata` with reason `unextracted`. An entity whose description or areas are not confirmed is dropped, because the areas set the depth tier. With the graph loaded, the verifier also gets the possible duplicates and link targets of each entity, and two read-only tools, `kg_search` and `kg_describe` (8 calls at most). It rules each possible duplicate `same` or `distinct` with what decides it, and lists the relations a source states from each entity to another proposed entity (by key) or to a store record (by id), each with its locator.
7. The script builds the records. An entity ruled the same as a store record is dropped as a duplicate, and so is one with a possible duplicate nobody ruled on. Links are written on the new record only, and only `family`, `variant_of`, `alias_of` (models and methods), `part_of`, `evaluates_task` and `uses_data` (benchmarks), each when it is supported at a location, reaches a kept sibling or a store record the run looked up, and is a relation `shared/omics/relations.ts` allows between the two kinds. `applicable_to` is off. Nothing links a model to a use case, so intake makes no such link. The links stay unused by result navigation until claims arrive (#274).
8. The script writes every record into the server's draft overlay (`draft_upsert`). An entity the overlay finds problems in, or that has a possible duplicate in the release with no ruling (its name may have been corrected since step 5), is dropped with its links and any source only it cited, and the rest is drafted again. `draft_export` then gives the batch: one line per record as `JSON.stringify` writes it, with the keys inside `attributes` and `facets` sorted, so the same batch always gives the same bytes. The server is closed before the store checks.
9. The script writes `data/omics/intake-<n>-<date>/` with `batch.jsonl`, `notes.md` (every proposed field and whether it was kept, the links and the duplicate rulings), `kg.json` (each link and ruling with its locator, the release and the overlay's diff of the batch, for the reviewer) and `review.json`. Then it runs:
   - `scripts/agents/intake-check.ts`, which checks that `normalizeAttributes` leaves every record unchanged (check C13), that each depth tier matches [tiers.md](tiers.md), that there are only entity kinds, that each link to a stored record reaches a record of a kind the relation allows, and that the release's `validateSnapshot` accepts the batch (for example, every model and benchmark needs `entity_level`);
   - `npm run records -- add`, including its SHACL subset check;
   - `npm run records -- check`.
10. If every check passes, it commits on `intake/issue-<n>`, pushes as the rewire-bot app, opens a pull request, and comments the link on the issue. The pull request closes a `tier-3` issue. For other tiers it only refers to the issue, which stays open for the evaluations that wait for #274. Otherwise it comments why it stopped: out of scope, duplicate, sources not openable, nothing verified, the cost cap, a failed model call, the output of the failing check, or an unexpected error.

Every record has status `discovered`. Models, methods and benchmarks carry `depth_tier` from their areas, and an `entity_level` (model `family`, `checkpoint` or `service`; method `method` or `family`; benchmark `suite` or `challenge`) that the verifier may correct, with `family`, `method` or `suite` when none is valid. Datasets and sources do not, because the attribute registry does not declare it for them. Each review object carries `reviewed_at` and no `date`, `reviewer` `claude-sonnet` (or `claude` if a refusal fallback answered) and a `reviewer_note` naming the run. Sources carry no licence string, because a new one would need a reviewed row in `data/archive/licence-map.tsv`.

### The knowledge graph

The intake loads the newest knowledge graph release (`kg/<id>`, built by `kg-release.yml`) into [rdf-kg-mcp](https://github.com/rewire-bio/rdf-kg-mcp) and talks to it over stdio with the MCP client (`scripts/agents/kg.mjs`). The workflow installs the server with `uv tool install`, downloads the bundle and writes the draft block for this checkout with `npm run kg -- draft-block <file>`, because bundles built before #325 carry none. The graph is read and drafted, never written: the release graphs do not change, and the overlay is gone when the run ends. JSONL stays the source of truth, and the batch reaches the store only through `records -- add` in a pull request that passes CI.

New records go through `draft_upsert`. A change to an existing record goes through `draft_change` (rdf-kg-mcp #10), which the intake uses for entity-update issues: the server is also given the checkout's entity lines (`--draft-records data/entities`), and a change names the record, the fields to change and the SHA-256 of the committed line it was based on. The server refuses any other digest, keeps every key the change does not touch in its place, and `draft_export` writes the change as `changes.jsonl`. Intake is pinned to rdf-kg-mcp v0.4.0, the first release with `draft_change`. Results, evaluations and claims are not drafted: a result's quote must resolve byte for byte against archived layer bytes, which the overlay cannot reach.

The release lags `main` by up to a day, so the name check in step 3 against the checkout stays. If the bundle cannot be downloaded or the server does not start within 3 minutes, the run goes on as before the graph: name checks only, links between the new records only, and the batch written by the script. The job summary, the pull request and `result.json` (its `kg` block) say which happened, with the release, the time to ready, the tool calls and the server's peak memory. The step "Knowledge graph load" warns when the server takes over 60 s or 4 GB (rdf-kg-mcp #8).

### Entity-update issues

The monthly entity sweep (below) files `entity-update` issues, and that label starts the intake too. Each issue carries a hidden `entity-update` marker with JSON that says what to do:

- `"action": "add"`: new checkpoints next to an existing record. The issue reads like an entity request (names and primary source URLs), so it takes the same path as one. Its pull request closes the issue, as for tier 3, because the sweep asks for entities only.
- `"action": "update"`: change fields of an existing record (`record_id`, `fields`, `evidence`). Only the fields the attribute registry declares for that kind may change: model `version`, `checkpoint_revision`, `licence` and `access`; method the same without `licence`; benchmark `version`. The script fetches and hashes each evidence page (reusing a stored source with the same URL), and Sonnet 5.5 marks each proposed value supported, corrected or unsupported, as in step 5. Only supported and corrected values are written. The record keeps its ID, status and review object; its `source_locator` gains a sentence naming the issue and where each value is stated, and new evidence sources are added to its `source_ids`. The sweep's marker also carries `base_sha256`, the digest of the record as the sweep checked it; if the store now holds another line, the run stops with a comment and changes nothing. A marker without `base_sha256` (a hand-written issue, or one filed before the sweep wrote it) is worked against the line the store holds now, and the pull request says so, so the reviewer can check the issue still applies. The change goes through the knowledge graph server: new sources with `draft_upsert`, the record with `draft_change` against the digest of its committed line, then `draft_export`. If the server is not available, the script writes the same changes file itself and the pull request says so. The batch folder `data/omics/update-<n>-<date>/` holds `changes.jsonl` (one `{id, base_sha256, sha256, record}` line: the whole changed record in its committed key order, the digest of the line it replaces and the digest of the new line), `batch.jsonl` (new sources), `notes.md` (with the field-level diff) and `review.json`. The checks are `intake-check.ts` on both files, `records -- add` for the new sources, `records -- change <review.json> <batch-dir> --changes <changes.jsonl>` and `records -- check`. `records -- change --changes` refuses a line whose `base_sha256` is not the record's provenance digest (the record changed since) or whose record, as the store writes it, does not have the line's `sha256`, and writes nothing then. The pull request closes the issue and shows the field-level diff.

To run it again on the same issue, remove and re-add the label, or run the workflow by hand. A rerun pushes the branch only when there is no open or merged pull request for it. It deletes a branch left by an earlier run before pushing, so the push never carries main's later changes to workflow files, which GitHub can refuse from a token without the workflows permission. A failed store check or a refused push is commented on the issue and fails the run, so the pipeline alert sees it.

### Queue and rate limits

Live intake runs queue. On 21 Nov 2026 the discovery scan labelled four issues within seconds, four runs started at once, and one (#347) failed with HTTP 429, "Number of concurrent connections has exceeded your rate limit". Nothing tried it again.

- **One run at a time.** Every live run (an intake label, or a manual run in `live` mode) is in the concurrency group `intake-queue`, which never cancels a run that has started. A label the intake does not act on, such as `tier-2`, gets a group of its own, so it cannot take the waiting place.
- **A run works the whole queue.** GitHub keeps one waiting run per group: a newer waiting run replaces the older one, which is cancelled. With four labels at once, the first run starts, and of the other three only the last survives. So a live run does not stop at its own issue (`intake.mjs --drain`). It works its issue, then every open issue labelled `entity-request` or `entity-update` that has no open or merged pull request from `intake/issue-<n>` and no final answer from the intake, lowest number first. It looks at the list again after each issue. Each issue runs in its own process, on the checkout put back to the commit the run started on, so no issue sees another's batch.
- **What counts as answered.** Every comment the intake posts on an issue ends with a hidden `<!-- intake-run: {"outcome": ..., "retry": ...} -->` marker. An issue with no intake comment is new. One whose last intake comment says `retry` is tried again. Anything else is final: a pull request, a skip, a failed check. A final answer is run again only by removing and re-adding the label. For that, an issue the comments call final or out of attempts is read once more against the time an intake label was last added (the issue's events): answers older than the label are not counted, so the issue is new again and its attempts start at none. Without this, a label added again whose own run was the waiting run GitHub cancelled would be hidden by the old answer and never run. #347's comment has no marker; a failure comment of that form that names 429, 529, `rate_limit_error` or `overloaded_error` is read as `retry`, so the next live run picks #347 up.
- **The waiting run.** When the surviving run starts, an earlier run may have worked its issue already. The workflow passes the time the label was added (`--since`); if the intake gave the issue a final answer after that, or used up its attempts, the run does not work it again and posts nothing, then works whatever else waits. An answer that says `retry` does not stop it: the run tries the issue again, as one more attempt.
- **Limits.** A run works at most 6 issues and starts none after 25 minutes; one issue gets 20 minutes; the job has 60. So the last issue ends by minute 45 of the script, and the setup has 10 minutes under both the job's limit and the hour the app token lives. What is left is named in the job summary and a warning, and the next live run works it.
- **The two-hourly check.** A burst gives two runs (the one that starts and the one that waits), so 12 issues at most; the monthly sweep can file 15 at once. A run that ends on a rate limit stops with issues still waiting. So a second workflow, `intake-queue.yml`, starts every two hours (minute 23). It runs `intake.mjs --queued`, which reads the labelled issues, their pull requests and comments with the default token and installs nothing. Only when an issue waits does it start `intake.yml` in `live` mode with no issue number (`gh workflow run`, with `actions: write` on the default token), which works the queue only, in the same group. It is a workflow of its own so that a check that found nothing is not an intake run that passed: the pipeline alert clears a workflow's failure on its next success, and watches `Intake queue` as a source of its own. To stop the scheduled check: `gh variable set INTAKE_QUEUE_SCHEDULE --body off`. A manual run of `intake.yml` in `live` mode with no issue number does the same work at once.
- **Every run of an issue leaves an answer.** After each issue the queue reads the issue again. If it carries no answer (the process was ended at its time limit, or its comment did not post), the queue writes one with the marker, so the run is counted and the issue is not worked again at every check. If the answer cannot be read or written, the run stops and fails.
- **The time limit ends the whole process group.** Each issue's process is started in a group of its own. At 20 minutes the group gets SIGTERM, and SIGKILL 10 seconds later, so the knowledge graph server, npm, uv or git that the issue started do not run on beside the next issue.
- **Waits on 429 and 529.** The SDK retries a failed request 3 times within a few seconds, which was not enough on the day. The script now also waits and tries a model call again on HTTP 429 and 529 (and on `rate_limit_error` or `overloaded_error` inside a stream): after 20, 40 and 80 seconds, or as long as the reply's `retry-after` says, never more than 120 seconds. At most 3 such retries per call, at most 480 seconds of waiting in a run, and none once the run's estimated cost is over $1.50.
- **Cost of a retry.** A request refused with 429 or 529 before it starts reports no tokens and adds nothing to the estimate. A stream that fails after it started has reported its input tokens, and those are added to the estimate before the retry, so the cost cap sees them; the output tokens it had produced are not known and are not counted. `usage.json` and the job summary give the number of retries, the seconds waited and the calls that still failed.
- **A run that still fails.** A run that ends on a rate limit, an overload, a server error (5xx) or a dropped connection comments the failure with `retry: true` and says so in plain words. The queue then stops (the limit is the account's, so the next issue would hit it too) and the run fails. An issue gets at most 3 runs that end this way; after that it waits for a person. Any other error is final.

The reviewer, the discovery scan and the other agents use the same API key and are not in this queue, so a rate limit is still possible; the waits are for that.

### Revision after a review

When the reviewer agent requests changes on a pull request the intake opened, the intake revises the batch once and the reviewer reviews again. Before this, such a pull request stayed open with nothing acting on it (#338: 8 of 9 fields passed and the review asked to drop one area).

What starts it: a review by `rewire-reviewer[bot]` with the state changes requested, on an open pull request by `rewire-bot[bot]` whose head is an `intake/issue-<n>` branch of this repository (`pull_request_review` in `intake.yml`, the `revise` job). Any other review starts no job. The reviewer requests changes only in `approve` mode with the rewire-reviewer app; in `comment` mode its reviews are comments and nothing is revised. To start it by hand, run the workflow with `revise_pr` set to the pull request number; the script reads the latest review from the API either way, and does nothing unless that review requests changes on the head commit.

What it does (`node scripts/agents/intake.mjs --revise --pr <n>`):

1. Reads the verdict. Each review ends with a hidden `<!-- reviewer-verdict: {...} -->` comment: the head commit, the verdict and every field that did not pass. Only a marker on the last line of the review is read. A review posted before the marker existed is read from its Problems list.
2. Decides, without a model call, whether it may act. It revises only fields of new entity records, and only these: `areas`, `limitations`, `links`, `entity_level`, `version`, `access`, `licence`, `training_data`, `task`, `scope_note`, `species`, `repository`, and `duplicates` when the finding is a list of store records without a ruling (Rewording and duplicate rulings, below). A failure on `name`, `description`, `source_ids` or the store diff, any other finding on `duplicates`, a pull request that changes an existing record (`changes.jsonl`), one that touches a file outside its batch folder and the store, and a request for changes that lists no failed field (red CI) all go to a person.
3. Fetches the sources of the records concerned again, reads from main the store records a `duplicates` finding names, and makes one Sonnet 5.5 call and one Haiku 5.5 structuring call. For each failed field the answer is `drop`, `cite`, `amend` or `rule`. A drop removes the named values of `areas`, `limitations` or `links` (a drop that names no value of the record settles nothing), or the whole attribute, which is then listed in `missing_metadata`. A cite keeps the value and quotes the passage that states it; the script accepts the quote only if it finds it in the page text of a source the record cites. An amend replaces a free-text value with a run of words copied from a quoted passage, and a rule records a ruling on a possible duplicate; both are described below. The model cannot propose a value in its own words.
4. Applies the answer in the script. For a record whose areas were dropped, or whose depth tier the review failed, the depth tier is worked out again from the areas, and each new source that record cites takes the areas of the records that cite it. Every other record keeps every byte. If any failed field is left unsettled, nothing is pushed.
5. Builds on main as it is now, not on the commit the pull request started from. The job checks out main; the script puts the pull request's batch folder on it and adds the first batch again, as a refresh does (below), before any model call. That shows the batch still passes the store checks on main and that the store lines the pull request held are its batch and nothing else. It then puts the store back as main has it, writes the revised records through the same draft overlay as the first run (`draft_upsert`, `draft_export`), and checks that the exported batch differs from the first one only in the failed fields and what follows from them. It rewrites `batch.jsonl`, `kg.json` and `review.json` (the file digests), appends to `notes.md`, and writes `revision.json`: each field, what was dropped or which passage was cited.
6. Runs `intake-check.ts`, `records -- add` and `records -- check` on the revised batch, as the first run does.
7. Commits, writes the revision marker in the pull request description, then pushes and comments. The branch is replaced by two commits on main: the first batch, then the revision. The push carries a lease on the head commit the review was read against (`--force-with-lease=<branch>:<sha>`), so it replaces that commit and no other. If the branch moved in the meantime (a refresh, a person), nothing is pushed, the marker is taken off the description again, and the review of the new head starts the revision afresh. The push starts the reviewer again. The reviewer is given the cited passages, new wordings, rulings and removals as claims to check against the source and the store itself.

Before this, the revision restored the store from the pull request's parent commit and pushed one commit on top. Once any other batch had merged, that branch conflicted with main, its CI did not run and the reviewer never saw the revision (#338).

At most one revision per pull request. The count is kept in three places, and any one stops a second revision: a hidden `<!-- intake-revision: {...} -->` comment in the pull request description, `revision.json` in the batch folder, and the number of commits (the intake pushes one; a second commit means a revision or a hand edit). The marker is written before the push, so a pushed revision is always counted. A refresh is not a revision and does not count: it leaves one commit, and it carries the marker and `revision.json` of a revised pull request along unchanged.

When the reviewer requests changes again, or the revision cannot act (step 2), cannot settle every field, passes its cost cap, or fails a store check or the push, the pull request is labelled `needs-tim`, gets one comment that says why, and is left. A pull request that already has the label is not looked at again. A failed store check or push also fails the run, so the pipeline alert sees it.

The duplicate rule holds across a revision. The revised `kg.json` keeps every failed step of the first run. If the knowledge graph does not start for the revision, or the draft overlay does not export, the script writes the batch itself and records a `draft_overlay` failure, also when the first run had none. The reviewer does not approve a batch with a failed duplicate check, revised or not.

Modes are the intake's. `dry-run` reads `tests/agents-intake-revise-fixtures/` (pull request #338) and calls nothing; pull requests that touch the agent run it. `--fixtures tests/agents-intake-revise-amend-fixtures/pr-352` or `pr-354` runs the same on those two pull requests. `report-only` calls the model, restores the store and runs the checks in the runner, and shows the description, label and comment it would write; it writes nothing to GitHub and pushes nothing. `live` does all of it. A review starts a `report-only` run unless the repository variable `INTAKE_REVISE_MODE` is `live`. It has been `live` since 21 Nov 2026 (`gh variable set INTAKE_REVISE_MODE --body live`), so a review starts a live revision. With `REVIEWER_MODE=approve` a pull request can be revised, approved and merged with no person involved, as #338 was. A `report-only` run leaves no marker, so each later request for changes on the same pull request makes the model calls again; without a push the reviewer does not review again, so that takes a new push or a reopened pull request. A run that names a pull request by hand first checks from the API that its author is `rewire-bot[bot]` and its head is an `intake/issue-<n>` branch of this repository, before the app token is made. The job checks out the default branch only: the agent, the prompt, the records CLI and the store are all main's. The script takes one thing from the pull request, its batch folder, which holds data. A pull request that changes anything outside its batch folder and the store is not revised.

#### Rewording and duplicate rulings

On 21 Nov 2026 the revision settled #338 and handed #352 and #354 to a person. Both were cases it had no action for.

**Amend (#352).** The record said about 380 million cells from 98 datasets were training data. The abstract gives that figure for pretraining and evaluation together. Dropping the value loses a true fact and citing it keeps a wrong one; the fix is to say what the source says. An amend gives a passage, the URL of its source and the new wording. The model does not write the wording: it picks a run of the source's own words. The script accepts it only when all of these hold:

- The field is `training_data`, `task` or `scope_note` (`AMEND_FIELDS`). These are the attributes of an intake record that the registry declares as text and that hold a sentence about the resource. `name` and `description` stay a person's. `version`, `licence` and `species` hold the source's own term, `access` and `repository` hold addresses, `areas` and `entity_level` are vocabularies, and links and `source_ids` are ids: none of these is reworded. The intake writes no numeric result.
- The record has a text value in that field. The new wording is not empty, is at most 500 characters, and is not the old value again: a change of case, spacing or punctuation alone is not an amend.
- The passage is in the page text the script fetched for a source the record cites, letter for letter. Only runs of white space are folded. Case, punctuation and every word must match, the passage is 20 to 600 characters long, and text the model fetched or remembers does not count. If the script could not open the page, no amend passes.
- The new wording is one unbroken run of that passage (`sourceSpan`). Nothing is added, left out or reordered. Only the case of its first letter and one final full stop may differ.
- The run is placed in the page, not in the passage, so a passage that is cut short does not make an end. It starts at a word, and not just after a negation or a hedge ("not", "without", "more than", "up to", "approximately" and a short list like them): that word has to be part of the run. It ends where the page ends a clause: a full stop, a semicolon or a colon followed by a space, or the end of the text. A comma is not an end, so a list or an "and" cannot be cut ("for pretraining" out of "for pretraining and evaluation" is refused).
- The wording holds nothing a stored value may not: no link, no @-mention, no HTML comment, no em or en dash. A run of the page that has one goes to a person.
- The revised batch differs from the first in that attribute and in the segment of `source_locator` for that field, which now names the source and says the value is its own words. No other segment of the locator and nothing of `missing_metadata` changes.

For #352 the wording that passes is "Approximately 380 million cells from 98 datasets for pretraining and evaluation."

This is narrower than the first version of the amend (#358), which let the model write a sentence and checked its numbers and capitalised names against the passage and the old value. That check compared words, not meaning. It accepted the failed claim again ("... for pretraining."), the old value with its full stop removed, swapped numbers, a dropped "million", an added "not", and any number or name the old value had, whether or not the source did. A run of the source's own words cannot add a number, a name, a unit or a negation, and the old value now gives the new one nothing. The cost is that a sound rewording in other words goes to a person.

What the check still cannot see: whether the run says enough. Words left out before it can matter when they are not on the short list, and a sentence can be true of something other than this resource. The reviewer is given the old value, the new one and the passage, and is asked whether the new value, read by itself, says what the source says.

The run on #352 also showed a fault in reading the reply: the structuring call wrote the record id with the field name after it (`<id>-training_data`), so the script matched no answer and reported "gave neither a value to drop nor a passage" for what was a drop. The script accepts an id in that form, and the structuring call is told to write the id alone. An answer that gives the id alone comes first, so a record whose own id is another record's id with a field name after it cannot take that record's answer.

**Dropping a link (#354).** The review failed a `uses_data` link no source states. The existing drop already covers links: it removes the named link from the record and from `kg.json`. The run never reached it, and made no model call, because the same review failed `duplicates` and the plan stopped there. Nothing was added for links.

**Rule (#354).** The reviewer searches the knowledge graph for store records that share at least half their distinctive words with a new record's name, and fails `duplicates` with "possible duplicate `<id>` ... in the store has no ruling in kg.json" for each one that `kg.json` does not rule on (`mechanicalProblems` in `reviewer.mjs`). The intake's own duplicate check records its rulings in `kg.json` as `duplicate_rulings`: the new record's name, the store record's id, label and kind, `same` or `distinct`, and a locator that says what decides it. The reviewer reads that list, passes the mechanical check when each record it found has a ruling that is not `same`, and has its model judge each ruling. So a revision ruling goes in the same list, marked `ruled_by: revision`.

The script reads the finding only when all of it is such a list. A finding cut short by the reviewer's length limit, a ruling of `same` the reviewer objects to, or any other text goes to a person with no model call. It then reads each named record from the store on main (every entity file, because a possible duplicate may be of another kind, as the dataset subset on #354 was). A record not found on main cannot be ruled on.

The script compares the addresses the two records give (`sourceKeys`): the URL, artifact URL, original URL and DOI of each source a record cites, and the URLs in the record's own `repository` and `access` attributes and its own DOI. Each address is reduced to a key (`addressKey`), so that two forms of one address match:

- a DOI, from a doi.org URL, a publisher URL with `/doi/`, a bioRxiv or medRxiv page (any version, with or without `.full`), a nature.com article or a Zenodo record;
- an arXiv id, from an abs, pdf or html page of any version or from an arXiv DOI;
- a repository (GitHub, GitLab, Bitbucket, Codeberg, Hugging Face): owner and name in lower case, whatever branch, file or query follows, with or without `.git`;
- any other URL: the host without `www.`, the path in lower case without a trailing slash, and the query. The scheme and the fragment never count.

The key is used only here. Matching a URL against stored sources still uses `urlKey`, which is exact.

A ruling of `distinct` counts only when:

- every store record the finding names has a ruling, given by its id or, as the structuring call sometimes writes it, by its whole name. A name is read only when one listed record has it;
- both records give at least one address. A record with none cannot be compared, on any ground;
- the two records share no address, or they share one, are of different kinds and the ground is `different_scope` (a dataset and a dataset subset from one repository). Two records of one kind at one address go to a person, whatever the ground and the phrases;
- neither name holds every distinctive word of the other (`nameOverlap` below 1). "Kinase Inhibitor Datasets v2" against "Kinase_Inhibitor_Datasets" goes to a person;
- the reply quotes one phrase from the new record and one from the store record, each found letter for letter in that record's own name or description and at least 12 characters long, and each holds two words or more that the other record's name and description lack. Words under four letters, common words ("other", "from", "five"), generic words ("dataset", "benchmark") and bare numbers do not count.

The locator the script writes holds the ground, both phrases, the model's reason and what the address comparison found. It says "found none in common", not "share no source": the comparison sees only the addresses the two records give. One resource cited at two unrelated addresses (a paper in one record, its data portal in the other, with no DOI or repository in common) is not seen. Publisher pages other than those listed above are not mapped to their DOI either.

A ruling of `same` counts only when the two records share an address, are of the same kind, and have the same name once case, spaces and punctuation are set aside. A whole and its subset share a source by construction, and two datasets from one paper do too, so a shared address alone closes nothing: a record of another kind, or with another name, goes to a person. The new record is then closed out: it leaves the batch, with any new source that only it cited. A link another record of the batch had to it moves to the store record and keeps its locator in `kg.json` with a note of the move, unless the record already links there, in which case the link is dropped. Other failed fields of the closed record need no answer. The store record itself is not changed: the intake's revision adds records and never edits one, so anything the new record knew that the store record lacks is left for an update request. If closing out would leave no record in the batch, the pull request adds nothing and goes to a person to close.

If any named record has no ruling, or a ruling fails a check, the field is unsettled, nothing is pushed and the pull request keeps `needs-tim`.

A ruling that passes these checks is still a claim, and the reviewer judges each one again with its own input (`revisionPromptLines` in `reviewer.mjs`, read from `revision.json`):

- for a ruling of `distinct`, the store record itself as the intake script read it from main (name, description, addresses), the ground, and the addresses the two records have in common. Before, the reviewer saw only the id, the label and the locator the revision wrote;
- for a close-out, the removed record (name, kind, description), the store record, the links that moved, and the id of a record still in the batch (`report_on`). The removed record is not among the records under review, so the reviewer fails `duplicates` on that record when it finds the removal wrong;
- for an amend, the old value, the new one and the passage.

`kg.json` keeps its shape. A second request for changes sends the pull request to a person.

One revision per pull request is unchanged. An amend, a ruling and a close-out are all part of the one revision, made with the same two model calls.

#352 and #354 carry `needs-tim` and no revision commit, marker or `revision.json`, and the latest review of each is of its head commit, so each can still have its one revision. The script skips a labelled pull request, and nothing starts a revision again by itself. To try them again a person removes the label and starts the job by hand, once for each:

```
gh pr edit 352 --remove-label needs-tim
gh workflow run intake.yml -f revise_pr=352 -f mode=live
```

If the pull request has been rebuilt on main since its last review, wait for the reviewer's review of the new head first; the script does nothing unless the latest review requests changes on the head commit.

### Refresh of a conflicting pull request

Every intake batch adds lines to the same store files (`data/entities/*.jsonl`, `data/provenance/records/*.jsonl`), and the files are sorted by ID, so two batches of the same day add neighbouring lines. As soon as one intake pull request merges, every other open one conflicts with main. GitHub runs no CI on a conflicting pull request, so the reviewer never reviews it again and it stays open. On 21 Nov 2026 this left #338, #352 and #354 stuck.

The refresh rebuilds such a pull request on main (`node scripts/agents/intake.mjs --refresh [--pr <n>]`, the `refresh` job in `intake.yml`). It makes no model call, needs no API key, changes no field, and is not the one revision.

What starts it: a push to main that touches `data/` (every merged batch is one), or a manual run with `refresh_pr` set to a pull request number. After a push the job looks at every open pull request by `rewire-bot[bot]` whose head is an `intake/issue-<n>` branch of this repository. When none is open, nothing is installed or run.

What it does, per pull request:

1. Reads it from the API and skips it unless it is open, the bot's, on an intake branch (the whole branch name is `intake/issue-<n>`), against the default branch, not labelled `needs-tim`, and conflicting. GitHub works out whether a pull request merges some seconds after each push to main; until then the API says `mergeable: null`. The script asks up to 6 more times, 5 seconds apart, and treats an answer that never comes as "skip, look again next run", never as "merges".
2. Checks it is something a refresh may rebuild: exactly one `data/omics/intake-<n>-<date>/batch.jsonl`, in a folder named for the issue its branch names, and no file outside that folder and the store. A pull request that changes an existing record (`changes.jsonl`) is not refreshed: `records -- change` stamps the day it runs into the provenance line and refuses a base digest that has moved, so the change has to be made again by a new intake run. A pull request with more than one commit that the intake did not revise (no revision marker and no `revision.json`) holds a person's commit, which the one commit of a rebuild would replace. These, and a pull request already refreshed 20 times, are labelled `needs-tim` with one comment. A pull request already rebuilt on the commit of main the run would build on is skipped: a commit on that commit cannot conflict with it, so main has moved since the checkout or GitHub's answer is an old one, and the next run looks again. The count of 20 is over the whole life of the pull request and is high on purpose: every other batch that merges takes one refresh.
3. Puts the working tree on main as the job checked it out, clean, and takes the batch folder from the pull request's head commit, byte for byte (`git checkout <head> -- <folder>`). Nothing else of the pull request is used.
4. Reads the store lines the pull request adds (its diff from the commit it shares with main) and ties them to the batch: one record line and one provenance line per record of `batch.jsonl`, the provenance line names the batch folder and carries the SHA-256 of the record line, nothing else is added and nothing is removed. A hand edit of the store on the branch fails here.
5. Runs `intake-check.ts`, `records -- add` and `records -- check`, as the first run did, on main's store.
6. Compares: the store must now gain exactly the lines the pull request held. If it does not, nothing is pushed.
7. Commits once, with the pull request's title, and pushes in place of the branch with a lease on the head commit it read in step 1. If the branch moved meanwhile, the push is refused, nothing else happens and the next run looks again. It then comments what it did. The push starts CI and the reviewer on the new commit.

Why a rebuilt commit and a forced push, and not a merge of main into the branch:

- Record digests and provenance are the same either way. `records -- add` writes no date and nothing of the store's state into a line: the record line is the batch record, and its provenance line is `{id, sha256, added_in, added_by, changed_by: []}`. The same batch added to any main gives the same lines, so every record keeps its identity (the SHA-256 of its stored line). Steps 4 and 6 check this on every refresh instead of assuming it.
- A merge would need its conflicts settled by taking main's store files and adding the batch again inside the merge commit. The result is the same tree, with a second commit whose content no tool wrote as a unit, and a history in which the first commit's store lines sit on an old main.
- The number of commits is one of the three counts of a revision. A merge commit would make an unrevised pull request look revised, and the next request for changes would then go to a person instead of being revised.
- A forced push can lose work, which is what the lease is for: it names the commit that was read, so the push replaces that commit or nothing. A commit someone added to the branch in the meantime is never overwritten.

When step 4 or 6 does not hold, the pull request is labelled `needs-tim`, gets one comment with the reason, and is not looked at again.

A step that fails (`intake-check`, `records -- add`, `records -- check`, or a git command) is treated differently, because the exit code cannot tell a batch that no longer fits main (main now holds a record with the same ID) from a tool that broke (`records -- add` downloads the SHACL checker with uv, and one failed download would otherwise label every conflicting pull request of the run). The first time a step fails on a pull request, the refresh leaves one comment with the failing output and a hidden `intake-refresh-failed` marker that names the step, labels nothing, and fails the run, so the pipeline alert sees it. If the same step fails again on a later run, the pull request is labelled `needs-tim` and that run fails too. A rebuild that was pushed in between clears the count. So a real fault costs two failed runs and a passing fault costs one. A `report-only` run labels nothing, so it would meet the same pull request after every push; it reports what it would write in the job summary and does not fail. One pull request that fails does not stop the others. Every pull request of a run is rebuilt on main as the job checked it out, never on the commit made for the one before it.

One push can be refused for a reason the script cannot fix. GitHub refuses a push from a token without the workflows permission when it brings a change to a workflow file onto a branch, and a rebuilt branch carries every change main made since the pull request was opened. The first intake run avoids this by deleting a stale branch before it pushes; a refresh cannot, because deleting the branch closes the pull request. The token the jobs ask for has contents, pull requests and issues only. So when main changed a file under `.github/workflows/` after the pull request was opened, the refresh may be refused. The change that added the refresh edits `intake.yml`, so this applies to every intake pull request that was open when it merged (#338, #352, #354). The fault is the token's, not the pull request's, so the script does not label: it fails the run with the reason, the pipeline alert fires, and it leaves one comment with a hidden `intake-refresh-refused` marker. After that comment, the refreshes that follow a push to main skip the pull request and do not fail on it again; a manual run with `refresh_pr` still tries the push, and a pushed rebuild clears the mark. A revision refused the same way takes its marker off the description again and fails its run; a review comes once per commit, so that does not repeat.

No refresh has pushed yet, so it is not known whether GitHub refuses in this case. If it does, the way out is one line. The rewire-bot installation already holds the workflows permission (`gh api orgs/rewire-bio/installations`, read on 21 Nov 2026); the jobs do not ask for it. Adding `permission-workflows: write` to the `Token for the rewire-bot app` step of the `refresh` job, and of the `revise` job, lets the push through. It is not added here, because it lets those two tokens change workflow files, and that is the owner's decision. The script would still push only a commit that holds the batch folder and the store lines on top of main. The first live trial should be one manual run with `refresh_pr` and `mode: live`, before the variable is set.

Modes are the intake's. `dry-run` reads `tests/agents-intake-refresh-fixtures/` (pull request #352 as it stood on 21 Nov 2026) and ties its store diff to its batch; pull requests that touch the agent run it. `report-only` does steps 1 to 6 in the runner and shows what it would push, or the label and comment it would write; it writes nothing to GitHub and pushes nothing. `live` does all of it. A push to main starts a `report-only` refresh unless the repository variable `INTAKE_REFRESH_MODE` is `live`; the variable is not set, so nothing is refreshed yet. To turn it on: `gh variable set INTAKE_REFRESH_MODE --body live`. A manual run uses the `mode` input.

Cost: no model call in the refresh itself. Each pushed refresh starts the reviewer on the new commit, at the reviewer's usual cost per review. With several intake pull requests open, each merge makes the others conflict and be refreshed and reviewed again, so reviews grow with the square of the number open at once: four pull requests merged one after another cost 3 + 2 + 1 extra reviews. Each automatic run rebuilds every conflicting pull request, in order of number, on the same main.

`tests/agents-intake-refresh.test.ts` covers each guard with fakes, runs the rebuild, the lease and the merge against a real repository in a temporary folder (with a stand-in for `records -- add`), and reads the `refresh` job and the queue from `intake.yml`. No refresh has run in Actions yet.

Cost: one Sonnet call that holds the page text of the sources (about the size of the first verification, $0.10 to $0.40), at most 2 web fetches and no search, and one Haiku call. Before the Sonnet call the script works out the most it can cost (`reviseCostBound`: three turns, each reading the whole prompt and both fetched pages, at 3 characters a token and no cache discount) and does not make it when that passes $1.50, which is about 12 sources of full length. The figure is priced as Sonnet 5.5; a refusal fallback to a dearer model is not covered. The structuring call is not made once the run passes $1.50. An amend or a ruling adds no call and no fetch: the store records a `duplicates` finding names are read from the checkout and go into the same prompt (a few hundred characters each), which the bound counts. `tests/agents-intake-revise.test.ts` covers these paths with fakes and written replies, and reads the `revise` job's condition, mode and token steps from `intake.yml`. `tests/agents-intake-revise-amend.test.ts` covers each guard of amend and rule with the real reviews of #352 and #354. Revisions have run live in Actions since 21 Nov 2026 (#338 settled); amend, rule and close-out have not yet run against the real model or in Actions.

### Modes

| Mode | Model calls | Writes | When |
| --- | --- | --- | --- |
| `dry-run` | No | Batch in the runner only | Pull requests that touch the agent, and by hand. It reads `tests/agents-intake-fixtures/` and runs the real `records add` and `records check` on the fixture batch against the real store. It then runs again on `tests/agents-intake-kg-fixtures/` with the real server on the small bundle there (42 records copied from a release), and fails unless the UCE request is ruled a duplicate and the fixture checkpoint links to its stored family. |
| `report-only` | Yes | Batch in the runner only | By hand with an issue number. The job summary and the `intake-<run>` artifact hold the pull request it would open, or the comment it would post, the draft proposal, the verification and the cost. The inputs `kg_release` (a `kg/<id>` tag) and `store_ref` (a commit) replay an issue against an earlier store and graph; a replay skips the existing pull request check. |
| `live` | Yes | Branch, pull request, issue comment | The `entity-request` or `entity-update` label, the two-hourly check when a labelled issue still waits (`intake-queue.yml`), and by hand. A live run works the queue after its own issue; the run the check starts, and a run by hand with no issue number, work the queue only. |

Locally: `node scripts/agents/intake.mjs --dry-run --store-dir tests/agents-intake-fixtures/entities --root /tmp/intake --no-store-checks` writes the fixture batch under `/tmp/intake` without loading the store. `tests/agents-intake.test.ts` runs the same paths with fakes, and `tests/agents-intake-kg.test.ts` the knowledge-graph paths with a fake server. To run the real server locally, set `KG_BUNDLE` (a bundle directory or `.tar.gz`), `KG_DRAFT_CONFIG` (from `npm run kg -- draft-block`) and, if `rdf-kg-mcp` is not on the path, `KG_MCP_COMMAND`.

### Setup

It uses the same `ANTHROPIC_API_KEY` secret as discovery, and the rewire-bot app (`REWIRE_BOT_APP_ID` variable, `REWIRE_BOT_PRIVATE_KEY` secret), which needs contents, pull requests and issues write on this repository. The workflow asks for a token limited to those three permissions on this repository only. Without the key a run writes a notice and passes.

The discovery scan files its data issues as the rewire-bot app, so their `entity-request` label starts the intake. If the app token cannot be made, discovery files them with the workflow's own `GITHUB_TOKEN`, which starts no workflow; then add the label again by hand, or run the intake by hand. Both of discovery's app tokens are limited to issues write: one on this repository, one on rewire.it.

### Limits and cost

Limits are in `LIMITS` in the script:

- draft: up to 3 web fetches, no search;
- verification: up to 5 web fetches and 1 web search, and up to 8 knowledge-graph lookups;
- each fetch up to 15,000 tokens; 10,000 output tokens per research response; 2 `pause_turn` resumes;
- 6 entities per issue;
- revision after a review: one per pull request, with up to 2 web fetches and no search; its structuring call is not made once the run's estimated cost passes $1.50;
- the verification call is not made once the run's estimated cost passes $1.50;
- waits on HTTP 429 and 529: 3 retries per call, 480 seconds of waiting per run, none over the cost cap (Queue and rate limits, above);
- a queued live run: 6 issues, no new issue after 25 minutes, 20 minutes per issue, a 60-minute job timeout; the cost limits are per issue, so a run that works 6 issues can cost 6 times the figure below;
- the two-hourly check is one short job with no model call; when an issue waits it starts a queued live run, and an issue gets at most 3 runs that end on a temporary failure per label;
- refresh: 20 per pull request, then a person; never twice on the same commit of main; a step that fails twice, then a person; a 45-minute job timeout, as for the revision, which now runs the store checks twice.

Prices are the same as for discovery (above). A typical issue should cost about $0.02 for the Haiku draft and $0.15 to $0.40 for the Sonnet verification, which holds every fetched page. Each knowledge-graph lookup is one more verification turn; the prompt is cached, so a turn costs a cache read of it plus the new tokens. The worst case is about $1.50 plus one verification call, about $0.90, so about $2.40. The job summary, the pull request body and `usage.json` in the artifact give each run's real token counts, cost and wall-clock time.

### Known gaps

- Source bytes are hashed, not stored. `npm run archive -- fetch` is a whole-store pass and runs separately.
- Links go on new records only. Linking an existing record (a stored checkpoint to its family) needs the change path rdf-kg-mcp #8 proposes (`records -- update`), which is not built.
- The reviewer checks links against the pull request's store, but starts its own server read-only: it does not draft the batch again.
- The verification runs in the same job as the draft. It is a second model, not an independent review; the reviewer agent (#256) is meant to provide that.
- A pull request that changes an existing record (`changes.jsonl`) is not refreshed when it conflicts; it is handed to a person.
- A refresh or a revision may be refused when main changed a workflow file after the pull request was opened (Refresh of a conflicting pull request, above). That is the case for #338, #352 and #354. The one-line way out is named there and is not applied.
- A revision whose store step fails labels the pull request `needs-tim` the first time, unlike a refresh. Nothing starts a revision again after a failed run (the review is of that commit and comes once), so the label is how a person hears of it; remove the label and run `revise_pr` by hand.
- The two-hourly check has not run in Actions, and neither has a run it starts. A job that GitHub ends at its limit, or cancels, writes no answer on the issue it was working; the limits are set so that this should not happen, and the next run would work that issue again with nothing counted.
- The cost estimate of a stream that failed part way counts its input tokens only.
- `reviseCostBound` is worked out for a call that is not retried. A retry after a refused request costs nothing more; a stream that fails part way and is tried again can cost up to one more turn, which the checks against the cost cap after the call see, and the bound before it does not.

## Reviewer agent

`.github/workflows/reviewer.yml` runs `scripts/agents/reviewer.mjs` on every pull request the rewire-bot app opens or updates (#256). Its rewire-bot token is limited to this repository, pull requests write and checks read. It reviews intake pull requests independently of the intake agent: its own prompt ([agents/reviewer.md](../agents/reviewer.md)), and Sonnet 5.5 opens the primary sources again itself.

What it does:

1. It reads the `data/omics/*/batch.jsonl` and `changes.jsonl` files the pull request adds, and the store, from the pull request's head, and each store file's diff from GitHub. The review code and prompt always come from `main`, so a pull request cannot change how it is reviewed.
2. The script checks what is mechanical:
   - each `depth_tier` against the rule in [tiers.md](tiers.md);
   - `entity_level` against the levels the release accepts;
   - names against the store (without the records under review) and against each other;
   - that every cited source is in the pull request or the store;
   - only entity kinds;
   - each link: its target is in the pull request or the store, the relation is one the intake writes and `shared/omics/relations.ts` allows between the two kinds, and `kg.json` lists it with a locator;
   - possible duplicates: each one the intake's draft overlay listed (the diff in `kg.json`), and each the reviewer finds itself with `search` on the newest knowledge graph release (rdf-kg-mcp, read-only), must carry a ruling in `kg.json`, and none may be ruled the same;
   - the store diff: every record line and provenance line the pull request adds or removes must belong to a record in `batch.jsonl` (added once, nothing removed, and the added line is the batch record as `records -- add` writes it: top-level fields and link fields in schema order) or `changes.jsonl` (one line removed whose SHA-256 is the change's `base_sha256`, one added whose SHA-256 is its `sha256`, with every key the change did not touch in the place it has in the removed line). A store file GitHub gives no diff for counts as untied, and so does any changed file under `data/entities`, `data/evidence` or `data/provenance` that is neither a record file nor a `data/provenance/records` file (such as `moved-attributes.jsonl`). Any other record touched fails the `store diff` row, so the pull request cannot be approved.
   - for each changed record, the field-level diff between the line the store diff removes and the record in `changes.jsonl`.
3. It fetches every new source again and compares the SHA-256 with the recorded one. A changed hash is reported, not failed, because many pages are generated per request.
4. Sonnet 5.5 reads the text of the pages the reviewer re-fetched itself (web fetch for anything else) and gives every field of every record a verdict: `pass` with the location, `fail` with the problem, or `unverifiable`. It checks source attribution: a page about a sibling model, size or variant does not support a record. It also checks `entity_level` against the vocabulary definitions, whether a source states each link (the `links` field), and whether each store record ruled distinct is a different resource (the `duplicates` field). For a changed record it judges every changed field (each path of the field-level diff, such as `/attributes/access`) against the sources. Haiku 5.5 only turns the notes into the fixed shape.
5. It posts one review: the problems, then a table per record (field, value, source, verdict, evidence). The verdict is `approve` only when every field passes. A field the model did not return counts as unverifiable. The review ends with a hidden `<!-- reviewer-verdict: {...} -->` comment that holds the head commit, the verdict and every field that did not pass (at most 30,000 characters: notes are shortened, then left out, before any row is). The intake agent reads it to make its one revision when the review requests changes ([Revision after a review](#revision-after-a-review)). When the batch folder holds `revision.json`, the review says the batch was revised, and the model is given each passage the revision cited as a claim to find in the source itself.

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

