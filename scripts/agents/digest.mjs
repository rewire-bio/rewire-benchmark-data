// Weekly digest of agent activity (rewire-benchmark-data #259). Every Monday, in live mode, it opens one issue,
// "Weekly digest: <from> to <to>", assigned to timini and labelled digest, and closes the
// previous week's. Every fact comes from GitHub, the release assets and the live site; a model
// only writes an optional three-sentence summary from those facts.
//
//   node scripts/agents/digest.mjs --dry-run [--fixtures <dir>] [--out <dir>]
//   node scripts/agents/digest.mjs --report-only [--days 7] [--out <dir>] [--no-summary]
//   node scripts/agents/digest.mjs [--days 7] [--out <dir>]
//
// --dry-run      reads every input from fixtures; no model call, no network, no write.
// --report-only  reads GitHub and the site and prints the digest; posts nothing.
// (no flag)      live: opens or updates the digest issue and closes older ones.
//
// Environment: GITHUB_REPOSITORY (the repository the digest is about and is posted in), GH_TOKEN
// or GITHUB_TOKEN (the rewire-bot app token: posts the issue and reads the other repositories),
// ACTIONS_TOKEN (reads workflow runs and artifacts; defaults to GH_TOKEN), DIGEST_REPOS (other
// repositories to read, comma separated; default <owner>/rewire.it,<owner>/rewire-database),
// DIGEST_SITE (default https://benchmarks.rewirebio.io), ANTHROPIC_API_KEY (optional summary),
// GITHUB_STEP_SUMMARY, GITHUB_SERVER_URL, GITHUB_RUN_ID.

import { execFileSync } from 'node:child_process';
import { createReadStream, existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, appendFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { createInterface } from 'node:readline';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { PRICES, Usage, clean } from './discovery.mjs';
import { ASSIGNEE, LABEL as PIPELINE_LABEL, staleness } from '../ops/pipeline-alert.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../..');

export const PROMPT_PATH = 'agents/digest.md';
export const FIXTURES = 'tests/agents-digest-fixtures';
export const LABEL = 'digest';
export const NEEDS_TIM = 'needs-tim';
export const SITE = 'https://benchmarks.rewirebio.io';
export const AGENTS = { discovery: 'discovery.yml', intake: 'intake.yml', reviewer: 'reviewer.yml', sweep: 'sweep.yml' };
export const MODELS = { summary: 'claude-haiku-5-5' };
export const LIMITS = { costUsd: 0.25, summaryMaxTokens: 400, artifacts: 100, maxListed: 15, maxDays: 31, bodyChars: 65000 };
const FAIL = new Set(['failure', 'timed_out', 'startup_failure']);
const PROVISIONAL = new Set(['discovered', 'needs_review']);
const STORE_FILES = { model: 'models', method: 'methods', benchmark: 'benchmarks', dataset: 'datasets', source: 'sources' };
const DISCOVERY_MARKER = /<!-- discovery-key: [a-z0-9-]+ -->/;
const DIGEST_MARKER = /<!-- weekly-digest: (\{.*?\}) -->/;

// ---------- Pure helpers ----------

const day = (iso) => String(iso).slice(0, 10);
const inWindow = (iso, w) => Boolean(iso) && iso >= w.since && iso < w.until;

/**
 * The reporting window: from `since` (the previous digest's end, see anchorSince) to `now`, or the
 * `days` days before `now` when there is no previous digest.
 */
export function windowOf(now, days = 7, since = null) {
  const until = new Date(now).toISOString();
  const start = since && since < until ? new Date(since).toISOString() : new Date(Date.parse(until) - days * 86_400_000).toISOString();
  return { since: start, until, label: `${day(start)} to ${day(until)}` };
}

/** ISO 8601 week of a timestamp, in UTC: "2026-W48". */
export function isoWeek(iso) {
  const d = new Date(`${day(iso)}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + 3 - ((d.getUTCDay() + 6) % 7));
  const year = d.getUTCFullYear();
  const week = Math.ceil(((d - Date.UTC(year, 0, 1)) / 86_400_000 + 1) / 7);
  return `${year}-W${String(week).padStart(2, '0')}`;
}

/** The { since, until } stored in a digest issue's marker, or null. */
export function digestMarker(body) {
  try {
    const m = JSON.parse(DIGEST_MARKER.exec(String(body ?? ''))?.[1] ?? 'null');
    return m && typeof m.since === 'string' && typeof m.until === 'string' ? m : null;
  } catch {
    return null;
  }
}

/** The reviewer agent's headline: `**Reviewer agent verdict: <verdict>.** ...`. Null if absent. */
export function parseVerdict(body) {
  const m = /\*\*Reviewer agent verdict: ([^.*]+)\.?/.exec(String(body ?? ''));
  if (!m) return null;
  const text = String(body);
  const fails = Number(/(\d+) fields? fails?/.exec(text)?.[1] ?? 0);
  const unverifiable = Number(/(\d+) could not be verified/.exec(text)?.[1] ?? 0);
  const total = Number(/out of (\d+)/.exec(text)?.[1] ?? /All (\d+) fields pass/.exec(text)?.[1] ?? 0);
  return { verdict: m[1].trim(), fails, unverifiable, total };
}

/** A pull request opened by an agent: the intake agent's branches. */
export const isAgentPull = (pull) => String(pull.head?.ref ?? '').startsWith('intake/');

/** Intake pull requests opened, merged and closed in the window, with the reviewer's latest verdict on each. */
export function agentPulls(pulls, reviewsByPull, w) {
  const out = { opened: [], merged: [], closed: [], open: [], reviews: [] };
  for (const p of pulls.filter(isAgentPull)) {
    const item = { number: p.number, title: p.title, url: p.html_url, repo: p.repo };
    if (inWindow(p.created_at, w)) out.opened.push(item);
    if (inWindow(p.merged_at, w)) out.merged.push(item);
    else if (!p.merged_at && inWindow(p.closed_at, w)) out.closed.push(item);
    if (p.state === 'open') out.open.push(item);
    for (const r of reviewsByPull[p.number] ?? []) {
      const parsed = parseVerdict(r.body);
      if (!parsed || !inWindow(r.submitted_at, w)) continue;
      out.reviews.push({ ...item, ...parsed, state: r.state, at: r.submitted_at, reviewUrl: r.html_url });
    }
  }
  return out;
}

/** GitHub's review state agrees with the verdict in its body. */
export function stateMatches(review) {
  const approve = review.verdict === 'approve';
  if (review.state === 'APPROVED') return approve;
  if (review.state === 'CHANGES_REQUESTED') return !approve;
  return true;
}

/**
 * Agent runs in the window. A run counts when its agent job ran: it left an artifact
 * (<agent>-<run id>) or it failed. Discovery and intake runs from pull requests are fixture dry
 * runs and do not count; reviewer runs from pull requests are real reviews (its dry-run job
 * uploads nothing). usage maps run id to the artifact's usage.json, or null when unreadable.
 */
export function agentRuns(runsByAgent, artifacts, usage, w, unread = new Set()) {
  const withArtifact = new Set(artifacts.map((a) => String(a.workflow_run?.id ?? a.name.split('-').pop())));
  const out = {};
  for (const [agent, runs] of Object.entries(runsByAgent)) {
    const counted = runs.filter((r) => inWindow(r.created_at, w)
      && (agent === 'reviewer' || r.event !== 'pull_request')
      && (withArtifact.has(String(r.id)) || FAIL.has(r.conclusion) && r.agentJobFailed !== false));
    const failed = counted.filter((r) => FAIL.has(r.conclusion));
    let spend = 0;
    let recorded = 0;
    let skipped = 0;
    for (const r of counted) {
      if (unread.has(String(r.id))) {
        skipped += 1;
        continue;
      }
      const u = usage[r.id];
      if (u && typeof u.estimatedUsd === 'number') {
        spend += u.estimatedUsd;
        recorded += 1;
      }
    }
    out[agent] = { runs: counted.length, failed: failed.map((r) => ({ id: r.id, url: r.html_url, conclusion: r.conclusion })), spend, recorded, unread: skipped };
  }
  return out;
}

/** Runs that count for agentRuns: in the window, and not a discovery or intake pull request dry run. */
export function countedRunIds(runsByAgent, w) {
  const ids = new Set();
  for (const [agent, runs] of Object.entries(runsByAgent)) {
    for (const r of runs) if (inWindow(r.created_at, w) && (agent === 'reviewer' || r.event !== 'pull_request')) ids.add(String(r.id));
  }
  return ids;
}

/**
 * The agent artifacts to read usage.json from: only those of counted runs, newest first, at most
 * `cap`. `unread` holds the run ids of counted artifacts left out by the cap.
 */
export function artifactsToRead(artifacts, runIds, cap = LIMITS.artifacts) {
  const counted = artifacts.filter((a) => runIds.has(String(a.workflow_run?.id))).sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)));
  return { read: counted.slice(0, cap), unread: new Set(counted.slice(cap).map((a) => String(a.workflow_run.id))), total: counted.length };
}

/**
 * Discrepancies new, resolved and stopped firing between two releases' discrepancies.json. Open
 * means unsettled, as on the site and over MCP (docs/discrepancies.md); `settled` lists live
 * findings settled since the baseline that still fire.
 */
export function diffDiscrepancies(baseline, current) {
  const before = new Map((baseline?.discrepancies ?? []).map((d) => [d.id, d]));
  const now = current?.discrepancies ?? [];
  const seen = new Set();
  const out = { added: [], resolved: [], stopped: [], settled: [], open: 0, openPublic: 0 };
  const isSettled = (d) => Boolean(d.resolved || d.settled);
  for (const d of now) {
    const prev = before.get(d.id) ?? (d.previous_ids ?? []).map((id) => before.get(id)).find(Boolean);
    if (prev) seen.add(prev.id);
    if (!isSettled(d)) {
      out.open += 1;
      if (d.listing === 'public') out.openPublic += 1;
    }
    if (!d.resolved && d.settled && (!prev || !isSettled(prev))) out.settled.push(d);
    if (!prev && !d.resolved) out.added.push(d);
    if (d.resolved && (!prev || !prev.resolved)) out.resolved.push(d);
  }
  if (baseline) for (const d of before.values()) if (!seen.has(d.id) && !d.resolved) out.stopped.push(d);
  return out;
}

/**
 * Records from merged agent batches whose status in the store is still provisional (discovered
 * or needs_review), by batch folder. A batch record no longer in the store is not counted.
 */
export function provisionalBatches(batches, statusById) {
  return batches.map((b) => {
    const stored = b.records.filter((r) => statusById.has(r.id));
    const pending = stored.filter((r) => PROVISIONAL.has(statusById.get(r.id)));
    return { folder: b.folder, total: stored.length, provisional: pending.length };
  }).filter((b) => b.provisional > 0);
}

/** "1 run", "2 runs". */
export function count(n, singular, plural = `${singular}s`) {
  return `${n} ${n === 1 ? singular : plural}`;
}

/**
 * Open or update this week's digest issue and close older ones. A digest whose window ends in the
 * same ISO week (UTC) as this one is this week's, so a re-run on any day of the week updates it.
 */
export function planIssue(existing, w) {
  const mine = existing.filter((i) => digestMarker(i.body));
  const week = isoWeek(w.until);
  const same = mine.find((i) => isoWeek(digestMarker(i.body).until) === week);
  return { update: same ?? null, close: mine.filter((i) => i !== same) };
}

/**
 * Where the next window starts, so consecutive digests neither overlap nor leave a gap: this
 * week's digest keeps its own start; otherwise the newest earlier digest's end. Null when there is
 * none, or it is more than LIMITS.maxDays old.
 */
export function anchorSince(existing, now) {
  const until = new Date(now).toISOString();
  const markers = existing.map((i) => digestMarker(i.body)).filter((m) => m && m.until <= until);
  const week = isoWeek(until);
  const start = markers.find((m) => isoWeek(m.until) === week)?.since
    ?? markers.filter((m) => isoWeek(m.until) !== week).map((m) => m.until).sort().pop();
  if (!start || start >= until || Date.parse(until) - Date.parse(start) > LIMITS.maxDays * 86_400_000) return null;
  return start;
}

const link = (item) => `[${item.repo && item.repo !== item.home ? `${item.repo.split('/')[1]}#` : '#'}${item.number}](${item.url})`;

function list(items, render, max = LIMITS.maxListed) {
  if (!items.length) return [];
  const lines = items.slice(0, max).map((i) => `  - ${render(i)}`);
  if (items.length > max) lines.push(`  - and ${items.length - max} more`);
  return lines;
}

const money = (n) => `$${n.toFixed(2)}`;

/** Remove the characters house style forbids in shipped prose. */
export function plain(text) {
  return clean(text).replace(/\s*(->|=>|→)\s*/g, ' to ').replace(/[✓✔✗✘✅❌]/g, '');
}

/** The digest issue body. `facts` comes from collect(). */
export function renderDigest(facts, { summary = '' } = {}) {
  const { window: w, repo, site } = facts;
  const home = repo;
  const L = (i) => link({ ...i, home });
  const out = [];
  if (summary) out.push(plain(summary), '');
  out.push(`Agent activity in \`${repo}\` and the other repositories the agents act in, ${w.since.slice(0, 16).replace('T', ' ')} to ${w.until.slice(0, 16).replace('T', ' ')} UTC. Counts first, then links. Filed by \`.github/workflows/digest.yml\` (#259).`, '');

  // Waiting on Tim first: it is the reason to open the issue.
  const waiting = facts.waiting;
  const waitCount = waiting.needsTim.length + waiting.reviewRequested.length + waiting.agentPullsOpen.length;
  out.push(`### Waiting on Tim: ${waitCount}`, '');
  if (!waiting.labelExists) out.push(`- No \`${NEEDS_TIM}\` label exists yet, so no issue is marked as waiting on Tim.`);
  else out.push(`- Issues labelled \`${NEEDS_TIM}\`: ${waiting.needsTim.length}`, ...list(waiting.needsTim, (i) => `${L(i)} ${plain(i.title)}`));
  out.push(`- Pull requests requesting his review: ${waiting.reviewRequested.length}`, ...list(waiting.reviewRequested, (i) => `${L(i)} ${plain(i.title)}`));
  out.push(`- Open agent pull requests not merged: ${waiting.agentPullsOpen.length}`, ...list(waiting.agentPullsOpen, (i) => `${L(i)} ${plain(i.title)}${i.verdict ? ` (reviewer: ${i.verdict}${i.mismatch ? `, but GitHub recorded ${i.state}` : ''})` : ' (no reviewer verdict yet)'}`));
  out.push('');

  // Agents.
  const d = facts.discovery;
  const p = facts.pulls;
  out.push('### What the agents did', '');
  out.push(`- Discovery: ${count(d.dataIssues.length, 'data issue')} filed here, ${count(d.articleIssues.length, 'article issue')} in other repositories`);
  out.push(...list(d.dataIssues, (i) => `${L(i)} ${plain(i.title)}`), ...list(d.articleIssues, (i) => `${L(i)} ${plain(i.title)}`));
  out.push(`- Intake: ${count(p.opened.length, 'pull request')} opened, ${p.merged.length} merged, ${p.closed.length} closed without merging`);
  out.push(...list(p.opened, (i) => `opened ${L(i)} ${plain(i.title)}`), ...list(p.merged, (i) => `merged ${L(i)}`), ...list(p.closed, (i) => `closed ${L(i)}`));
  const approvals = p.reviews.filter((r) => r.verdict === 'approve').length;
  const failedFields = p.reviews.reduce((s, r) => s + r.fails, 0);
  out.push(`- Reviewer: ${count(p.reviews.length, 'verdict')}, ${approvals} approve and ${p.reviews.length - approvals} not approved; ${count(failedFields, 'field')} failed in total`);
  out.push(...list(p.reviews, (r) => `${L(r)} [${r.verdict}](${r.reviewUrl}): ${r.fails} of ${r.total} fields fail, ${r.unverifiable} unverifiable${stateMatches(r) ? '' : `. GitHub recorded the review as ${r.state}, which does not match`}`));
  out.push('');

  // Runs and spend.
  out.push('### Runs and spend', '');
  out.push('| Agent | Runs | Failed | Spend |', '| --- | --- | --- | --- |');
  let total = 0;
  let unrecorded = 0;
  let unread = 0;
  for (const [agent, r] of Object.entries(facts.runs)) {
    total += r.spend;
    const skipped = r.unread ?? 0;
    const missing = r.runs - r.recorded - skipped;
    unrecorded += missing;
    unread += skipped;
    const gaps = [missing ? `${count(missing, 'run')} not recorded` : '', skipped ? `${skipped} not read, over the artifact cap` : ''].filter(Boolean).join(', ');
    const spend = r.runs === 0 ? 'none' : r.recorded === 0 ? (skipped && !missing ? 'not read, over the artifact cap' : 'not recorded') : `${money(r.spend)}${gaps ? ` (${gaps})` : ''}`;
    out.push(`| ${agent} | ${r.runs} | ${r.failed.length ? r.failed.map((f, k) => `[${k + 1}](${f.url})`).join(' ') : '0'} | ${spend} |`);
  }
  out.push('', `Anthropic spend recorded: ${money(total)}${unrecorded ? `; ${count(unrecorded, 'run')} left no readable usage.json, so ${unrecorded === 1 ? 'its' : 'their'} spend is not recorded` : ''}${unread ? `; ${count(unread, 'run')} not read because the digest reads at most ${LIMITS.artifacts} artifacts` : ''}. Spend is each run's own estimate from token counts, not the Console bill.`);
  if (facts.runsNote) out.push('', facts.runsNote);
  out.push('');

  // Releases.
  const r = facts.releases;
  out.push(`### Releases: ${count(r.cut.length, 'release')} cut`, '');
  out.push(...r.cut.map((x) => `- [${x.id}](${x.url}), ${day(x.publishedAt)}${x.id === r.liveId ? ', live on the site' : ''}`));
  if (r.liveId) {
    out.push(`- The site serves \`${r.liveId}\`${r.newest && r.newest !== r.liveId ? `; the newest release \`${r.newest}\` is not live yet (published ${Math.floor(r.ageHours)} hours ago)` : ', the newest release'}. ([deployment.json](${site}/deployment.json))`);
  } else out.push(`- Could not read ${site}/deployment.json, so adoption is unknown.`);
  out.push('');

  // Records.
  out.push('### Agent records still provisional', '');
  if (!facts.provisional.length) out.push('- None: no merged agent batch has records with status `discovered` or `needs_review`.');
  for (const b of facts.provisional) out.push(`- [\`${b.folder}\`](${facts.server}/${repo}/tree/main/data/omics/${b.folder}): ${b.provisional} of ${count(b.total, 'record')} still provisional`);
  out.push('');

  // Discrepancies.
  const x = facts.discrepancies;
  const c = (dd) => `[\`${dd.id}\`](${site}/contested/${dd.id}/) ${plain(dd.label ?? '')}`;
  out.push('### Discrepancies', '');
  if (!x) out.push('- No knowledge-graph release to compare.');
  else {
    out.push(`- Compared \`${x.from ?? 'nothing'}\` with \`${x.to}\`: ${x.added.length} new, ${x.resolved.length} resolved, ${x.stopped.length} stopped firing. ${x.open} open (not settled), ${x.openPublic} of them public.`);
    out.push(...list(x.added.filter((dd) => dd.listing === 'public'), (dd) => `new ${c(dd)}`));
    if (x.added.some((dd) => dd.listing !== 'public')) out.push(`  - and ${count(x.added.filter((dd) => dd.listing !== 'public').length, 'new finding')} listed for curation only`);
    out.push(...list(x.resolved, (dd) => `resolved (${dd.review_state}) ${c(dd)}`), ...list(x.stopped, (dd) => `stopped firing \`${dd.id}\` ${plain(dd.label ?? '')}`));
    if (x.settled?.length) out.push(`- Settled since \`${x.from ?? 'nothing'}\` and still firing: ${x.settled.length}`, ...list(x.settled, (dd) => `settled (${dd.review_state}) ${c(dd)}`));
  }
  out.push(`- Open leads: ${facts.leads.length}`, ...list(facts.leads, (i) => `${L(i)} ${plain(i.title.replace(/^Lead:\s*/, ''))}`));
  out.push('');

  // Pipeline.
  const pb = facts.pipeline;
  out.push(`### Pipeline: ${count(pb.open.length, `\`${PIPELINE_LABEL}\` issue`)} open`, '');
  out.push(...list(pb.open, (i) => `${L(i)} ${plain(i.title)}, open since ${day(i.created_at)}`).map((l) => l.slice(2)));
  if (pb.closed.length) out.push(`- Closed this week: ${pb.closed.map(L).join(', ')}`);
  out.push('');

  out.push('### Not covered', '');
  out.push('- Tier 1 use-case ranking changes per release and the gap scanner\'s proposals (#259) are not in the digest yet.');
  if (facts.skipped.length) out.push(...facts.skipped.map((s) => `- Not read: \`${s.repo}\` (${s.reason}).`));
  out.push(...facts.notes.map((n) => `- ${n}`));
  // The marker goes on after any cut, so planIssue and anchorSince always find it.
  const marker = `<!-- weekly-digest: ${JSON.stringify({ since: w.since, until: w.until })} -->`;
  const body = out.filter((l, i, all) => !(l === '' && all[i - 1] === '')).join('\n');
  const room = LIMITS.bodyChars - marker.length - 60;
  const kept = body.length > room ? `${body.slice(0, room).replace(/\n[^\n]*$/, '')}\n\n(Cut at GitHub's issue size limit.)` : body;
  return `${kept}\n\n${marker}`;
}

// ---------- Inputs ----------

/** Records of the agent batches in data/omics, and their status in data/entities. */
export async function readStore(root) {
  const omics = join(root, 'data/omics');
  const batches = [];
  if (existsSync(omics)) {
    for (const folder of readdirSync(omics).filter((f) => f.startsWith('intake-')).sort()) {
      const file = join(omics, folder, 'batch.jsonl');
      if (!existsSync(file)) continue;
      const records = readFileSync(file, 'utf8').split('\n').filter(Boolean).map((l) => JSON.parse(l)).map((r) => ({ id: r.id, kind: r.kind, status: r.status }));
      batches.push({ folder, records });
    }
  }
  const wanted = new Set(batches.flatMap((b) => b.records.map((r) => r.id)));
  const status = new Map();
  const kinds = new Set(batches.flatMap((b) => b.records.map((r) => STORE_FILES[r.kind])).filter(Boolean));
  for (const name of kinds) {
    const file = join(root, 'data/entities', `${name}.jsonl`);
    if (!existsSync(file)) continue;
    for await (const line of createInterface({ input: createReadStream(file), crlfDelay: Infinity })) {
      const id = /^\{"id":\s*"([^"]+)"/.exec(line)?.[1];
      if (!id || !wanted.has(id)) continue;
      status.set(id, JSON.parse(line).status);
    }
  }
  return { batches, status };
}

/**
 * GitHub REST with pagination; `stop(item)` ends paging early for lists sorted newest first.
 * `onLimit(path)` is called when a list stops at its page limit with more items left.
 */
export function githubClient(token, fetchImpl = fetch, onLimit = () => {}) {
  async function call(method, path, body, { raw = false, accept = 'application/vnd.github+json' } = {}) {
    const res = await fetchImpl(path.startsWith('http') ? path : `https://api.github.com${path}`, {
      method,
      headers: { ...(token ? { authorization: `Bearer ${token}` } : {}), accept, 'x-github-api-version': '2022-11-28', 'user-agent': 'rewire-digest' },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) {
      const err = new Error(`${method} ${path}: ${res.status} ${(await res.text()).slice(0, 200)}`);
      err.status = res.status;
      throw err;
    }
    if (raw) return Buffer.from(await res.arrayBuffer());
    return res.status === 204 ? null : res.json();
  }
  async function all(path, { key, stop = () => false, pages = 20 } = {}) {
    const out = [];
    for (let page = 1; page <= pages; page++) {
      const data = await call('GET', `${path}${path.includes('?') ? '&' : '?'}per_page=100&page=${page}`);
      const items = key ? data[key] : data;
      for (const item of items) {
        if (stop(item)) return out;
        out.push(item);
      }
      if (items.length < 100) return out;
    }
    onLimit(path);
    return out;
  }
  return { call, all };
}

/** Inputs from fixtures, in the same shape as liveSource gives them. */
export function fixtureSource(dir) {
  const read = (name) => JSON.parse(readFileSync(join(dir, name), 'utf8'));
  const gh = read('github.json');
  return {
    now: gh.now,
    readable: async (repo) => (gh.unreadable?.includes(repo) ? { ok: false, reason: 'fixture: no access' } : { ok: true }),
    issues: async (repo) => gh.issues[repo] ?? [],
    openIssues: async (repo) => (gh.issues[repo] ?? []).filter((i) => i.state === 'open'),
    labelExists: async (repo, name) => (gh.labels?.[repo] ?? []).includes(name),
    pulls: async (repo) => gh.pulls[repo] ?? [],
    openPulls: async (repo) => (gh.pulls[repo] ?? []).filter((p) => p.state === 'open'),
    reviews: async (repo, n) => gh.reviews[String(n)] ?? [],
    runs: async (file) => gh.runs[file] ?? [],
    jobs: async (id) => gh.jobs?.[String(id)] ?? [],
    artifacts: async () => gh.artifacts,
    usage: async (artifact) => gh.usage[String(artifact.workflow_run.id)] ?? null,
    releases: async () => gh.releases,
    deployment: async () => gh.deployment,
    discrepancies: async (tag) => (gh.discrepancies[tag] ? read(gh.discrepancies[tag]) : null),
    store: async () => readStore(join(dir, 'store')),
  };
}

/** Inputs from GitHub, the release assets and the site. */
export function liveSource({ repo, token, actionsToken, site, root, fetchImpl = fetch, log }) {
  const limits = [];
  const onLimit = (path) => {
    limits.push(path.split('?')[0]);
    log(`Page limit reached reading ${path}`);
  };
  const gh = githubClient(token, fetchImpl, onLimit);
  const actions = actionsToken && actionsToken !== token ? githubClient(actionsToken, fetchImpl, onLimit) : gh;
  const now = new Date().toISOString();
  return {
    now,
    limits,
    async readable(r) {
      try {
        await gh.call('GET', `/repos/${r}`);
        return { ok: true };
      } catch (e) {
        return { ok: false, reason: `${e.status ?? 'error'}: the token cannot read it` };
      }
    },
    // Issues updated since a date include everything created or closed in the window.
    issues: (r, since) => gh.all(`/repos/${r}/issues?state=all&sort=updated&direction=desc&since=${since}`).then((xs) => xs.filter((i) => !i.pull_request)),
    openIssues: (r) => gh.all(`/repos/${r}/issues?state=open`).then((xs) => xs.filter((i) => !i.pull_request)),
    async labelExists(r, name) {
      try {
        await gh.call('GET', `/repos/${r}/labels/${encodeURIComponent(name)}`);
        return true;
      } catch (e) {
        if (e.status === 404) return false;
        throw e;
      }
    },
    pulls: (r, since) => gh.all(`/repos/${r}/pulls?state=all&sort=updated&direction=desc`, { stop: (p) => p.updated_at < since, pages: 5 }),
    openPulls: (r) => gh.all(`/repos/${r}/pulls?state=open`),
    reviews: (r, n) => gh.all(`/repos/${r}/pulls/${n}/reviews`),
    runs: (file, since) => actions.all(`/repos/${repo}/actions/workflows/${file}/runs?created=%3E%3D${since}`, { key: 'workflow_runs', pages: 5 }),
    jobs: (id) => actions.call('GET', `/repos/${repo}/actions/runs/${id}/jobs`).then((j) => j.jobs),
    artifacts: (since) => actions.all(`/repos/${repo}/actions/artifacts`, { key: 'artifacts', stop: (a) => a.created_at < since, pages: 10 }),
    async usage(artifact) {
      if (artifact.expired) return null;
      const dir = mkdtempSync(join(tmpdir(), 'digest-'));
      try {
        const zip = join(dir, 'a.zip');
        writeFileSync(zip, await actions.call('GET', artifact.archive_download_url, undefined, { raw: true }));
        return JSON.parse(execFileSync('unzip', ['-p', zip, 'usage.json'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }));
      } catch (e) {
        log(`usage.json not read from ${artifact.name}: ${String(e.message).split('\n')[0]}`);
        return null;
      } finally {
        rmSync(dir, { recursive: true, force: true });
      }
    },
    releases: () => gh.all(`/repos/${repo}/releases`, { pages: 3 }).then((xs) => xs.map((x) => ({ tagName: x.tag_name, publishedAt: x.published_at, url: x.html_url, assets: x.assets }))),
    async deployment() {
      try {
        const res = await fetchImpl(`${site}/deployment.json`, { headers: { 'cache-control': 'no-cache' } });
        return res.ok ? res.json() : null;
      } catch {
        return null;
      }
    },
    async discrepancies(tag, releases) {
      const asset = releases.find((x) => x.tagName === tag)?.assets?.find((a) => a.name === 'discrepancies.json');
      if (!asset) return null;
      // The API asset URL works for private repositories too.
      const bytes = await gh.call('GET', asset.url, undefined, { raw: true, accept: 'application/octet-stream' });
      return JSON.parse(bytes.toString('utf8'));
    },
    store: () => readStore(root),
  };
}

// ---------- Collect ----------

/** Every fact the digest shows. */
export async function collect(src, { repo, otherRepos, site, server = 'https://github.com', days = 7, since = null, log = () => {} }) {
  const w = windowOf(src.now, days, since);
  const notes = [];
  const skipped = [];
  const repos = [repo];
  for (const r of otherRepos) {
    const access = await src.readable(r);
    if (access.ok) repos.push(r);
    else skipped.push({ repo: r, reason: access.reason });
  }

  // Issues, per repository.
  const dataIssues = [];
  const articleIssues = [];
  const needsTim = [];
  const leads = [];
  const pipeline = { open: [], closed: [] };
  let labelExists = false;
  const allPulls = [];
  for (const r of repos) {
    const tag = (i) => ({ ...i, repo: r, url: i.html_url ?? i.url });
    const labels = (i) => (i.labels ?? []).map((l) => (typeof l === 'string' ? l : l.name));
    // Events in the window come from issues updated in it; the current state from every open issue.
    for (const i of (await src.issues(r, w.since)).map(tag)) {
      if (DISCOVERY_MARKER.test(i.body ?? '') && inWindow(i.created_at, w)) (r === repo ? dataIssues : articleIssues).push(i);
      if (i.state !== 'open' && labels(i).includes(PIPELINE_LABEL) && inWindow(i.closed_at, w)) pipeline.closed.push(i);
    }
    for (const i of (await src.openIssues(r)).map(tag)) {
      if (labels(i).includes(NEEDS_TIM)) needsTim.push(i);
      if (labels(i).includes(PIPELINE_LABEL)) pipeline.open.push(i);
      if (r === repo && /^Lead:/.test(i.title)) leads.push(i);
    }
    if (await src.labelExists(r, NEEDS_TIM)) labelExists = true;
    const recent = (await src.pulls(r, w.since)).map(tag);
    const seen = new Set(recent.map((p) => p.number));
    allPulls.push(...recent, ...(await src.openPulls(r)).map(tag).filter((p) => !seen.has(p.number)));
  }

  // Agent pull requests and reviewer verdicts.
  const reviewsByPull = {};
  for (const p of allPulls.filter((x) => x.repo === repo && isAgentPull(x) && (x.state === 'open' || x.updated_at >= w.since))) {
    reviewsByPull[p.number] = await src.reviews(repo, p.number);
  }
  const pulls = agentPulls(allPulls.filter((x) => x.repo === repo), reviewsByPull, w);
  const latest = (n) => pulls.reviews.filter((x) => x.number === n).sort((a, b) => b.at.localeCompare(a.at))[0]
    ?? (reviewsByPull[n] ?? []).map((x) => ({ ...parseVerdict(x.body), state: x.state, at: x.submitted_at })).filter((x) => x.verdict).sort((a, b) => b.at.localeCompare(a.at))[0];
  const agentPullsOpen = pulls.open.map((p) => {
    const v = latest(p.number);
    return { ...p, verdict: v?.verdict, state: v?.state, mismatch: v ? !stateMatches(v) : false };
  });
  const reviewRequested = allPulls.filter((p) => p.state === 'open' && (p.requested_reviewers ?? []).some((u) => u.login === ASSIGNEE));

  // Runs, failures and spend.
  const runsByAgent = {};
  for (const [agent, file] of Object.entries(AGENTS)) {
    const runs = await src.runs(file, w.since);
    // A failed reviewer run on a person's pull request is its dry-run job: check which job failed.
    for (const run of runs.filter((x) => agent === 'reviewer' && FAIL.has(x.conclusion))) {
      const jobs = await src.jobs(run.id);
      run.agentJobFailed = jobs.some((j) => FAIL.has(j.conclusion) && j.name !== 'dry-run');
    }
    runsByAgent[agent] = runs;
  }
  // Pull request dry runs leave artifacts too; drop them before the cap so they cannot use it up.
  const artifacts = (await src.artifacts(w.since)).filter((a) => new RegExp(`^(${Object.keys(AGENTS).join('|')})-\\d+$`).test(a.name) && inWindow(a.created_at, w));
  const toRead = artifactsToRead(artifacts, countedRunIds(runsByAgent, w));
  const usage = {};
  for (const a of toRead.read) usage[a.workflow_run.id] = await src.usage(a);
  if (toRead.unread.size) notes.push(`Only the newest ${LIMITS.artifacts} of ${toRead.total} agent run artifacts were read for spend.`);
  const runs = agentRuns(runsByAgent, artifacts, usage, w, toRead.unread);

  // Releases and adoption.
  const releases = await src.releases();
  const serving = releases.filter((x) => x.tagName?.startsWith('serving/') && x.publishedAt);
  const cut = serving.filter((x) => inWindow(x.publishedAt, w)).map((x) => ({ id: x.tagName.slice(8), url: x.url, publishedAt: x.publishedAt }))
    .sort((a, b) => a.publishedAt.localeCompare(b.publishedAt));
  const deployment = await src.deployment();
  const liveId = deployment?.release_id ?? null;
  let fresh = {};
  if (liveId && serving.length) fresh = staleness({ liveId, releases: serving, now: w.until, maxAgeHours: 24 });

  // Discrepancies: the newest kg/ release against the newest one published before the window.
  const kg = releases.filter((x) => x.tagName?.startsWith('kg/') && x.publishedAt && x.publishedAt < w.until).sort((a, b) => b.publishedAt.localeCompare(a.publishedAt));
  const to = kg[0];
  const from = kg.find((x) => x.publishedAt < w.since);
  let discrepancies = null;
  if (to && (!from || to !== from)) {
    const current = await src.discrepancies(to.tagName, releases);
    const baseline = from ? await src.discrepancies(from.tagName, releases) : null;
    if (current) discrepancies = { from: from?.tagName.slice(3) ?? null, to: to.tagName.slice(3), ...diffDiscrepancies(baseline, current) };
    else notes.push(`Could not read discrepancies.json from ${to.tagName}.`);
  } else if (to) {
    const current = await src.discrepancies(to.tagName, releases);
    if (current) discrepancies = { from: to.tagName.slice(3), to: to.tagName.slice(3), ...diffDiscrepancies(current, current) };
  }

  // Records from agent batches that no person or later pass has moved on.
  const store = await src.store();
  const provisional = provisionalBatches(store.batches, store.status);

  for (const path of new Set(src.limits ?? [])) notes.push(`Stopped reading \`${path}\` at its page limit, so older items may be missing.`);

  log(`Collected: ${dataIssues.length} discovery issues, ${pulls.opened.length} intake pull requests opened, ${pulls.reviews.length} reviews, ${cut.length} releases.`);
  return {
    repo, site, server, window: w, skipped, notes,
    waiting: { labelExists, needsTim, reviewRequested, agentPullsOpen },
    discovery: { dataIssues, articleIssues },
    pulls, runs,
    releases: { cut, liveId, newest: fresh.newest ?? null, ageHours: fresh.ageHours ?? 0 },
    provisional, discrepancies, leads, pipeline,
  };
}

/** The facts the summary model sees: counts and titles only. */
export function summaryInput(facts) {
  const r = facts.runs;
  return JSON.stringify({
    window: facts.window.label,
    waiting_on_tim: facts.waiting.needsTim.length + facts.waiting.reviewRequested.length + facts.waiting.agentPullsOpen.length,
    open_agent_pulls: facts.waiting.agentPullsOpen.map((p) => ({ title: p.title, reviewer: p.verdict ?? null, github_state: p.state ?? null })),
    discovery_issues: facts.discovery.dataIssues.length,
    article_issues: facts.discovery.articleIssues.length,
    intake: { opened: facts.pulls.opened.length, merged: facts.pulls.merged.length, closed: facts.pulls.closed.length },
    reviews: facts.pulls.reviews.map((x) => ({ verdict: x.verdict, fails: x.fails, total: x.total })),
    runs: Object.fromEntries(Object.entries(r).map(([k, v]) => [k, { runs: v.runs, failed: v.failed.length }])),
    releases_cut: facts.releases.cut.length,
    live_release_is_newest: !facts.releases.newest || facts.releases.newest === facts.releases.liveId,
    discrepancies: facts.discrepancies && { new: facts.discrepancies.added.length, resolved: facts.discrepancies.resolved.length, open: facts.discrepancies.open },
    open_leads: facts.leads.length,
    pipeline_broken_open: facts.pipeline.open.length,
    provisional_batches: facts.provisional.length,
  });
}

/**
 * The optional summary: one Haiku call, skipped when its worst-case cost would pass the cap.
 * Returns { text, reason }: `reason` says why `text` is empty.
 */
export async function writeSummary(client, usage, { system, facts, log }) {
  const input = summaryInput(facts);
  const p = PRICES[MODELS.summary];
  const worst = ((system.length + input.length) / 3 * p.input + LIMITS.summaryMaxTokens * p.output) / 1e6;
  if (usage.total() + worst > LIMITS.costUsd) {
    const reason = `its worst-case cost $${worst.toFixed(4)} would pass the $${LIMITS.costUsd} cap`;
    log(`Summary skipped: ${reason}.`);
    return { text: '', reason };
  }
  const message = await client.messages.create({
    model: MODELS.summary,
    max_tokens: LIMITS.summaryMaxTokens,
    // Haiku 5.5 thinks by default and thinking counts against max_tokens; three sentences need none.
    thinking: { type: 'disabled' },
    system,
    messages: [{ role: 'user', content: `<facts>\n${input}\n</facts>` }],
  });
  usage.add(MODELS.summary, message.usage);
  if (message.stop_reason !== 'end_turn') return { text: '', reason: `the model stopped with ${message.stop_reason}` };
  const text = plain(message.content.filter((b) => b.type === 'text').map((b) => b.text).join(' ').replace(/\s+/g, ' ')).trim();
  return { text, reason: text ? null : 'the model returned no text' };
}

// ---------- Main ----------

function parseArgs(argv) {
  const args = { fixtures: FIXTURES, days: 7, summary: true };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--dry-run') args.dryRun = true;
    else if (a === '--report-only') args.reportOnly = true;
    else if (a === '--no-summary') args.summary = false;
    else if (a === '--out') args.out = argv[++i];
    else if (a === '--fixtures') args.fixtures = argv[++i];
    else if (a === '--days') args.days = Number(argv[++i]);
    else if (a === '--root') args.root = argv[++i];
    else throw new Error(`unknown argument ${a}`);
  }
  return args;
}

/** Run the digest. Returns { title, body, action }. `deps` replaces the source, GitHub client and model in tests. */
export async function main(argv = process.argv.slice(2), env = process.env, deps = {}) {
  const args = parseArgs(argv);
  const mode = args.dryRun ? 'dry run' : args.reportOnly ? 'report only' : 'live';
  const repo = env.GITHUB_REPOSITORY || 'rewire-bio/rewire-benchmark-data';
  const owner = repo.split('/')[0];
  const otherRepos = (env.DIGEST_REPOS || `${owner}/rewire.it,${owner}/rewire-database`).split(',').map((s) => s.trim()).filter((s) => s && s !== repo);
  const site = (env.DIGEST_SITE || SITE).replace(/\/$/, '');
  const server = env.GITHUB_SERVER_URL || 'https://github.com';
  const token = env.GH_TOKEN || env.GITHUB_TOKEN;
  const log = deps.log ?? ((m) => console.log(m));
  const usage = new Usage();

  const src = deps.source ?? (args.dryRun
    ? fixtureSource(resolve(ROOT, args.fixtures))
    : liveSource({ repo, token, actionsToken: env.ACTIONS_TOKEN || token, site, root: resolve(args.root ?? ROOT), log }));

  // Live: start where the last digest ended, and find the issue to update or close.
  let gh = null;
  let existing = [];
  let since = null;
  if (mode === 'live') {
    gh = deps.github ?? githubClient(token);
    existing = (await gh.all(`/repos/${repo}/issues?state=open&labels=${LABEL}`)).filter((i) => !i.pull_request);
    since = anchorSince(existing, src.now);
    log(since ? `Window starts where the last digest ended: ${since}.` : `No digest to continue from; covering the last ${args.days} days.`);
  }
  const facts = await collect(src, { repo, otherRepos, site, server, days: args.days, since, log });

  let summary = '';
  if (args.summary && !args.dryRun && env.ANTHROPIC_API_KEY) {
    try {
      const client = deps.anthropic ?? new (await import('@anthropic-ai/sdk')).default();
      const result = await writeSummary(client, usage, { system: readFileSync(join(ROOT, PROMPT_PATH), 'utf8'), facts, log });
      summary = result.text;
      if (!summary) facts.notes.push(`No summary: ${result.reason}.`);
    } catch (e) {
      facts.notes.push(`No summary: the model call failed (${String(e?.message ?? e).split('\n')[0].slice(0, 120)}).`);
    }
  }
  if (args.summary && !summary && !args.dryRun && !env.ANTHROPIC_API_KEY) facts.notes.push('No summary: ANTHROPIC_API_KEY is not set.');
  if (usage.total() > 0) facts.notes.push(`This digest cost an estimated $${usage.total().toFixed(4)} (summary only).`);
  const title = `Weekly digest: ${facts.window.label}`;
  const body = renderDigest(facts, { summary });

  let action = 'none';
  let url = null;
  if (mode === 'live') {
    try {
      await gh.call('GET', `/repos/${repo}/labels/${LABEL}`);
    } catch (e) {
      if (e.status !== 404) throw e;
      await gh.call('POST', `/repos/${repo}/labels`, { name: LABEL, color: '0e8a16', description: 'Weekly digest of agent activity' });
    }
    const plan = planIssue(existing, facts.window);
    let number;
    if (plan.update) {
      number = plan.update.number;
      url = (await gh.call('PATCH', `/repos/${repo}/issues/${number}`, { title, body })).html_url;
      action = 'updated';
    } else {
      const created = await gh.call('POST', `/repos/${repo}/issues`, { title, body, labels: [LABEL], assignees: [ASSIGNEE] });
      number = created.number;
      url = created.html_url;
      action = 'opened';
    }
    for (const old of plan.close) {
      await gh.call('POST', `/repos/${repo}/issues/${old.number}/comments`, { body: `Superseded by #${number}.` });
      await gh.call('PATCH', `/repos/${repo}/issues/${old.number}`, { state: 'closed', state_reason: 'completed' });
    }
    log(`${action} ${url}; closed ${plan.close.map((i) => `#${i.number}`).join(', ') || 'nothing'}.`);
  }

  const report = [`## ${title} (${mode})`, '', action === 'none' ? 'Not posted.' : `${action}: ${url}`, '', '---', '', body, '', '### Token usage', '', usage.table(), ''].join('\n');
  if (env.GITHUB_STEP_SUMMARY) appendFileSync(env.GITHUB_STEP_SUMMARY, `${report}\n`);
  if (args.out) {
    mkdirSync(args.out, { recursive: true });
    writeFileSync(join(args.out, 'digest.md'), `# ${title}\n\n${body}\n`);
    writeFileSync(join(args.out, 'facts.json'), `${JSON.stringify(facts, null, 2)}\n`);
    writeFileSync(join(args.out, 'usage.json'), `${JSON.stringify({ byModel: usage.byModel, estimatedUsd: usage.total() }, null, 2)}\n`);
  } else if (!env.GITHUB_STEP_SUMMARY) log(report);
  return { title, body, action, url, facts, usage };
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  main().catch((e) => {
    console.error(e);
    process.exit(1);
  });
}
