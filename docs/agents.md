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
