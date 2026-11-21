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

`.github/workflows/intake.yml` runs `scripts/agents/intake.mjs` when someone adds the `entity-request` label to an issue (#255). The prompt is [agents/intake.md](../agents/intake.md). It turns the issue into a pull request that adds entity records, and it never merges.

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

### Revision after a review

When the reviewer agent requests changes on a pull request the intake opened, the intake revises the batch once and the reviewer reviews again. Before this, such a pull request stayed open with nothing acting on it (#338: 8 of 9 fields passed and the review asked to drop one area).

What starts it: a review by `rewire-reviewer[bot]` with the state changes requested, on an open pull request by `rewire-bot[bot]` whose head is an `intake/issue-<n>` branch of this repository (`pull_request_review` in `intake.yml`, the `revise` job). Any other review starts no job. The reviewer requests changes only in `approve` mode with the rewire-reviewer app; in `comment` mode its reviews are comments and nothing is revised. To start it by hand, run the workflow with `revise_pr` set to the pull request number; the script reads the latest review from the API either way, and does nothing unless that review requests changes on the head commit.

What it does (`node scripts/agents/intake.mjs --revise --pr <n>`):

1. Reads the verdict. Each review ends with a hidden `<!-- reviewer-verdict: {...} -->` comment: the head commit, the verdict and every field that did not pass. Only a marker on the last line of the review is read. A review posted before the marker existed is read from its Problems list.
2. Decides, without a model call, whether it may act. It revises only fields of new entity records, and only these: `areas`, `limitations`, `links`, `entity_level`, `version`, `access`, `licence`, `training_data`, `task`, `scope_note`, `species`, `repository`. A failure on `name`, `description`, `source_ids`, `duplicates` or the store diff, a pull request that changes an existing record (`changes.jsonl`), one that touches a file outside its batch folder and the store, and a request for changes that lists no failed field (red CI) all go to a person.
3. Fetches the sources of the records concerned again, and makes one Sonnet 5.5 call and one Haiku 5.5 structuring call. For each failed field the answer is `drop` or `cite`. A drop removes the named values of `areas`, `limitations` or `links` (a drop that names no value of the record settles nothing), or the whole attribute, which is then listed in `missing_metadata`. A cite keeps the value and quotes the passage that states it; the script accepts the quote only if it finds it in the page text of a source the record cites. The model cannot propose a new value.
4. Applies the answer in the script. For a record whose areas were dropped, or whose depth tier the review failed, the depth tier is worked out again from the areas, and each new source that record cites takes the areas of the records that cite it. Every other record keeps every byte. If any failed field is left unsettled, nothing is pushed.
5. Restores the store files the pull request changed to their state in the parent commit, writes the revised records through the same draft overlay as the first run (`draft_upsert`, `draft_export`), and checks that the exported batch differs from the first one only in the failed fields and what follows from them. It rewrites `batch.jsonl`, `kg.json` and `review.json` (the file digests), appends to `notes.md`, and writes `revision.json`: each field, what was dropped or which passage was cited.
6. Runs `intake-check.ts`, `records -- add` and `records -- check`, as the first run does.
7. Commits, writes the revision marker in the pull request description, then pushes one commit to the same branch (never a force push) and comments. The push starts the reviewer again. The reviewer is given the cited passages as claims to check against the source itself.

At most one revision per pull request. The count is kept in three places, and any one stops a second revision: a hidden `<!-- intake-revision: {...} -->` comment in the pull request description, `revision.json` in the batch folder, and the number of commits (the intake pushes one; a second commit means a revision or a hand edit). The marker is written before the push, so a pushed revision is always counted.

When the reviewer requests changes again, or the revision cannot act (step 2), cannot settle every field, passes its cost cap, or fails a store check or the push, the pull request is labelled `needs-tim`, gets one comment that says why, and is left. A pull request that already has the label is not looked at again. A failed store check or push also fails the run, so the pipeline alert sees it.

The duplicate rule holds across a revision. The revised `kg.json` keeps every failed step of the first run. If the knowledge graph does not start for the revision, or the draft overlay does not export, the script writes the batch itself and records a `draft_overlay` failure, also when the first run had none. The reviewer does not approve a batch with a failed duplicate check, revised or not.

Modes are the intake's. `dry-run` reads `tests/agents-intake-revise-fixtures/` (pull request #338) and calls nothing; pull requests that touch the agent run it. `report-only` calls the model, restores the store and runs the checks in the runner, and shows the description, label and comment it would write; it writes nothing to GitHub and pushes nothing. `live` does all of it. A review starts a `report-only` run unless the repository variable `INTAKE_REVISE_MODE` is `live`; the variable is not set, so reviews revise nothing yet. To turn it on: `gh variable set INTAKE_REVISE_MODE --body live`. With `REVIEWER_MODE=approve` a pull request can then be revised, approved and merged with no person involved. A `report-only` run leaves no marker, so each later request for changes on the same pull request makes the model calls again; without a push the reviewer does not review again, so that takes a new push or a reopened pull request. A run that names a pull request by hand first checks from the API that its author is `rewire-bot[bot]` and its head is an `intake/issue-<n>` branch of this repository, before the app token is made. The job checks out the pull request head with its parent commit, and takes the agent code and prompt from the default branch. The store checks run the pull request's own records CLI, which is why a pull request that changes anything but data is not revised.

Cost: one Sonnet call that holds the page text of the sources (about the size of the first verification, $0.10 to $0.40), at most 2 web fetches and no search, and one Haiku call. Before the Sonnet call the script works out the most it can cost (`reviseCostBound`: three turns, each reading the whole prompt and both fetched pages, at 3 characters a token and no cache discount) and does not make it when that passes $1.50, which is about 12 sources of full length. The figure is priced as Sonnet 5.5; a refusal fallback to a dearer model is not covered. The structuring call is not made once the run passes $1.50. `tests/agents-intake-revise.test.ts` covers these paths with fakes and written replies, and reads the `revise` job's condition, mode and token steps from `intake.yml`; no revision has run against the real model or in Actions yet.

### Modes

| Mode | Model calls | Writes | When |
| --- | --- | --- | --- |
| `dry-run` | No | Batch in the runner only | Pull requests that touch the agent, and by hand. It reads `tests/agents-intake-fixtures/` and runs the real `records add` and `records check` on the fixture batch against the real store. It then runs again on `tests/agents-intake-kg-fixtures/` with the real server on the small bundle there (42 records copied from a release), and fails unless the UCE request is ruled a duplicate and the fixture checkpoint links to its stored family. |
| `report-only` | Yes | Batch in the runner only | By hand with an issue number. The job summary and the `intake-<run>` artifact hold the pull request it would open, or the comment it would post, the draft proposal, the verification and the cost. The inputs `kg_release` (a `kg/<id>` tag) and `store_ref` (a commit) replay an issue against an earlier store and graph; a replay skips the existing pull request check. |
| `live` | Yes | Branch, pull request, issue comment | The `entity-request` label, and by hand. |

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
- a 30-minute job timeout.

Prices are the same as for discovery (above). A typical issue should cost about $0.02 for the Haiku draft and $0.15 to $0.40 for the Sonnet verification, which holds every fetched page. Each knowledge-graph lookup is one more verification turn; the prompt is cached, so a turn costs a cache read of it plus the new tokens. The worst case is about $1.50 plus one verification call, about $0.90, so about $2.40. The job summary, the pull request body and `usage.json` in the artifact give each run's real token counts, cost and wall-clock time.

### Known gaps

- Source bytes are hashed, not stored. `npm run archive -- fetch` is a whole-store pass and runs separately.
- Links go on new records only. Linking an existing record (a stored checkpoint to its family) needs the change path rdf-kg-mcp #8 proposes (`records -- update`), which is not built.
- The reviewer checks links against the pull request's store, but starts its own server read-only: it does not draft the batch again.
- The verification runs in the same job as the draft. It is a second model, not an independent review; the reviewer agent (#256) is meant to provide that.

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

