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
3. The script drops each proposed entity that has no area from `data/vocab/area.ttl`, or whose name or alias is already in `data/entities/`.
4. The script, not the model, fetches every source a remaining entity cites. When the draft cites none for an entity, it uses every source the draft lists, and failing that the URLs in the issue body (not social posts or GitHub issue links). It records the SHA-256, media type and retrieval time. It takes the source's name from the page title, its version from what the URL pins (arXiv or bioRxiv version, git commit, otherwise the retrieval date) and its publication status from the host. A URL already in `data/entities/sources.jsonl` is reused, not added again. A bot check page served with HTTP 200 (reCAPTCHA, Cloudflare) counts as not opened. A short reference from the draft, such as `github.com/org/repo`, is resolved to the full URLs that contain it. An entity with no source that opens is dropped.
5. Sonnet 5.5 opens the sources and marks each proposed field supported (with a location), corrected or unsupported. Haiku structures the verdicts. Each entity carries a key the script gave it (`e1`, `e2`, ...), so a respelt name still matches. Only supported and corrected values are stored. An unconfirmed field is left out and listed in `missing_metadata` with reason `unextracted`. An entity whose description or areas are not confirmed is dropped, because the areas set the depth tier.
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
