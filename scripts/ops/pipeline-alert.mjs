// File, update and close the `pipeline-broken` issue for failed releases, adoptions, deploys
// and agent runs (rewire-benchmark-data #252).
//
// The same file lives in rewire-benchmark-data and rewire-database, at
// scripts/ops/pipeline-alert.mjs; keep the two copies identical. It has no dependencies, so
// it runs straight after checkout. `workflow_run` only fires inside one repository and
// there is no cross-repository token yet, so each repository files its own issue with its
// own GITHUB_TOKEN.
//
// One open issue per repository carries every failing source (a workflow file, or the live
// release check). A failure adds its source and comments with the run link and the log
// lines before the first error. A success clears its source; the issue closes once no
// source is failing. Cancelled and skipped runs change nothing, and neither does a failed run
// whose only unsuccessful jobs were cancelled rather than timed out.
//
// Only runs on main count, except that --pr-workflows names workflows whose pull request runs
// also count when the pull request comes from a branch in the same repository starting with
// --pr-branch-prefix: the record pull requests an agent opens, not anyone's own work in review.
//
//   node scripts/ops/pipeline-alert.mjs run --run-id <id> [--pr-workflows a.yml,b.yml --pr-branch-prefix x/] [--dry-run]
//   node scripts/ops/pipeline-alert.mjs stale --site <url> [--max-age-hours 24] [--dry-run]
//
// GITHUB_REPOSITORY names the repository; GH_TOKEN or GITHUB_TOKEN authenticates. With
// --dry-run it reads from GitHub but prints what it would write instead of writing it.

import { pathToFileURL } from 'node:url';

export const LABEL = 'pipeline-broken';
export const ASSIGNEE = 'timini';
export const LIVE_SOURCE = 'live-release';
const MARKER = /<!-- pipeline-alert-state: (\{.*?\}) -->/s;
const FAIL = new Set(['failure', 'timed_out', 'startup_failure']);
const LOG_LINES = 40;
const LOG_CHARS = 6000;

/**
 * What a finished run means for its source: 'fail', 'pass' or 'ignore'.
 * prRuns: { workflows: ['reviewer.yml'], branchPrefix: 'intake/' } also counts pull request runs
 * of those workflow files whose head is a branch of this repository with that prefix.
 */
export function outcomeOf(run, prRuns = {}) {
  if (run.event === 'merge_group') return 'ignore';
  const pr = run.event === 'pull_request' || run.event === 'pull_request_target';
  if (pr ? !watchedPullRequest(run, prRuns) : run.head_branch !== 'main') return 'ignore';
  if (FAIL.has(run.conclusion)) return 'fail';
  if (run.conclusion === 'success') return 'pass';
  return 'ignore';
}

function watchedPullRequest(run, { workflows = [], branchPrefix = '' }) {
  const head = run.head_repository?.full_name;
  return Boolean(branchPrefix) && workflows.includes(sourceOf(run))
    && String(run.head_branch ?? '').startsWith(branchPrefix)
    && Boolean(head) && head === run.repository?.full_name;
}

/**
 * Whether a failed run failed or was only cancelled: 'fail' or 'ignore'. A run can conclude
 * `failure` when a job was cancelled and none failed. A job that hit its time limit also shows
 * as cancelled, so the ids in timedOut count as failures.
 */
export function judgeJobs(jobs, timedOut = new Set()) {
  if (jobs.some((job) => FAIL.has(job.conclusion) || timedOut.has(job.id))) return 'fail';
  return jobs.some((job) => job.conclusion === 'cancelled') ? 'ignore' : 'fail';
}

/** Whether a cancelled job's annotations say it ran past its time limit. */
export function timedOutByAnnotations(annotations) {
  return (annotations ?? []).some((a) => /exceeded the maximum execution time/i.test(a.message ?? ''));
}

/** The source a run belongs to: its workflow file name. */
export function sourceOf(run) {
  return String(run.path ?? run.name).split('/').pop();
}

/** The failing sources recorded in an issue body. */
export function readState(body) {
  const match = MARKER.exec(body ?? '');
  if (!match) return { failing: {} };
  try {
    const state = JSON.parse(match[1]);
    return { failing: state.failing ?? {} };
  } catch {
    return { failing: {} };
  }
}

export function renderBody(state) {
  const sources = Object.entries(state.failing);
  const lines = [
    'A release, adoption, deploy, check or agent run is failing. This issue is opened and closed by `scripts/ops/pipeline-alert.mjs` (#252 in rewire-benchmark-data); it closes itself when every source below has succeeded again.',
    '',
    '**Failing**',
    '',
    ...sources.map(([source, info]) => `- \`${source}\`: ${info.summary} ([run](${info.url}), since ${info.since})`),
    '',
    'Each failure adds a comment with the lines before the first error.',
    '',
    `<!-- pipeline-alert-state: ${JSON.stringify(state)} -->`,
  ];
  return lines.join('\n');
}

/**
 * Decide what to do with the open issue (or its absence) for one source's new outcome.
 * Returns { action: 'none' | 'create' | 'update' | 'close', body?, comment?, title? }.
 */
export function plan({ issue, source, outcome, url, summary, details, now }) {
  const state = issue ? readState(issue.body) : { failing: {} };
  if (outcome === 'fail') {
    const since = state.failing[source]?.since ?? now;
    const next = { failing: { ...state.failing, [source]: { url, summary, since } } };
    const comment = [`**${source}** failed: ${summary}`, '', url, ...(details ? ['', details] : [])].join('\n');
    if (!issue) return { action: 'create', title: 'Pipeline broken on main', body: renderBody(next), comment };
    return { action: 'update', body: renderBody(next), comment };
  }
  if (outcome !== 'pass' || !issue || !(source in state.failing)) return { action: 'none' };
  const { [source]: _cleared, ...rest } = state.failing;
  const next = { failing: rest };
  const still = Object.keys(rest);
  if (still.length === 0) {
    return { action: 'close', body: renderBody(next), comment: `**${source}** succeeded: ${url}\n\nNothing is failing now; closing.` };
  }
  return {
    action: 'update',
    body: renderBody(next),
    comment: `**${source}** succeeded: ${url}\n\nStill failing: ${still.map((s) => `\`${s}\``).join(', ')}.`,
  };
}

/** The lines before the first `##[error]` of a job log, without timestamps, as a code block. */
export function logExcerpt(log, lines = LOG_LINES) {
  const all = String(log)
    .replace(/\r/g, '')
    .replace(/\u001b\[[0-9;]*m/g, '')
    .split('\n').map((line) => line.replace(/^\d{4}-\d\d-\d\dT[\d:.]+Z ?/, ''));
  const errorAt = all.findIndex((line) => line.startsWith('##[error]'));
  const end = errorAt === -1 ? all.length : errorAt + 1;
  let text = all
    .slice(Math.max(0, end - lines), end)
    .filter((line) => !/^##\[(group|endgroup)\]/.test(line))
    .join('\n')
    .trimEnd();
  if (text.length > LOG_CHARS) text = '...\n' + text.slice(-LOG_CHARS);
  return text.replace(/```/g, "'''");
}

/**
 * Whether the live site lags the newest `serving/` release by more than maxAgeHours.
 * releases: [{ tagName, publishedAt }]. Returns { stale, newest, ageHours }.
 */
export function staleness({ liveId, releases, now, maxAgeHours = 24 }) {
  const serving = releases
    .filter((r) => r.tagName?.startsWith('serving/') && r.publishedAt)
    .sort((a, b) => Date.parse(b.publishedAt) - Date.parse(a.publishedAt));
  if (serving.length === 0) throw new Error('No published serving/ release found.');
  const newest = serving[0].tagName.slice('serving/'.length);
  const ageHours = (Date.parse(now) - Date.parse(serving[0].publishedAt)) / 3_600_000;
  return { stale: liveId !== newest && ageHours > maxAgeHours, newest, ageHours };
}

// ---- GitHub I/O -------------------------------------------------------------------------

function client({ repo, token, dryRun }) {
  const base = `https://api.github.com/repos/${repo}`;
  async function call(method, path, body, { raw = false, allow = [] } = {}) {
    const res = await fetch(path.startsWith('http') ? path : base + path, {
      method,
      headers: {
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(body ? { 'Content-Type': 'application/json' } : {}),
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok && !allow.includes(res.status)) {
      throw new Error(`${method} ${path}: ${res.status} ${await res.text()}`);
    }
    if (!res.ok) return null;
    return raw ? res.text() : res.status === 204 ? null : res.json();
  }
  const write = (method, path, body, opts) => {
    if (dryRun) {
      console.log(`[dry run] ${method} ${path}\n${body ? JSON.stringify(body, null, 2) : ''}`);
      return Promise.resolve(null);
    }
    return call(method, path, body, opts);
  };
  return { read: (path, opts) => call('GET', path, undefined, opts), write };
}

async function openIssue(gh) {
  const issues = await gh.read(`/issues?state=open&labels=${LABEL}&sort=created&direction=asc&per_page=20`);
  return issues.find((issue) => !issue.pull_request && MARKER.test(issue.body ?? '')) ?? null;
}

async function apply(gh, issue, decision) {
  if (decision.action === 'none') {
    console.log('Nothing to change.');
    return;
  }
  if (decision.action === 'create') {
    await gh.write('POST', '/labels', { name: LABEL, color: 'b60205', description: 'A release, adoption or deploy is failing on main' }, { allow: [422] });
    const created = await gh.write('POST', '/issues', { title: decision.title, body: decision.body, labels: [LABEL], assignees: [ASSIGNEE] });
    const number = created?.number ?? '<new>';
    await gh.write('POST', `/issues/${number}/comments`, { body: decision.comment });
    console.log(`Opened issue ${number}.`);
    return;
  }
  await gh.write('PATCH', `/issues/${issue.number}`, { body: decision.body, ...(decision.action === 'close' ? { state: 'closed', state_reason: 'completed' } : {}) });
  await gh.write('POST', `/issues/${issue.number}/comments`, { body: decision.comment });
  console.log(`${decision.action === 'close' ? 'Closed' : 'Updated'} issue ${issue.number}.`);
}

/** The jobs of a failed run, with the ids of cancelled jobs that in fact timed out. */
async function runJobs(gh, run) {
  const { jobs } = await gh.read(`/actions/runs/${run.id}/attempts/${run.run_attempt ?? 1}/jobs?per_page=100`);
  const timedOut = new Set();
  for (const job of jobs.filter((j) => j.conclusion === 'cancelled').slice(0, 10)) {
    const annotations = await gh.read(`/check-runs/${job.id}/annotations`, { allow: [403, 404] });
    if (annotations === null) console.log(`Could not read the annotations of job ${job.id}; counting it as cancelled.`);
    if (timedOutByAnnotations(annotations)) timedOut.add(job.id);
  }
  return { jobs, timedOut };
}

async function failureDetails(gh, run, { jobs, timedOut }) {
  const failed = jobs.filter((job) => FAIL.has(job.conclusion) || timedOut.has(job.id));
  const parts = [];
  for (const job of failed.slice(0, 3)) {
    const step = job.steps?.find((s) => FAIL.has(s.conclusion) || s.conclusion === 'cancelled');
    const log = await gh.read(`/actions/jobs/${job.id}/logs`, { raw: true, allow: [404, 410] });
    parts.push(`Job \`${job.name}\`${step ? `, step "${step.name}"` : ''}:`);
    parts.push(log ? '```\n' + logExcerpt(log) + '\n```' : '(log not available)');
  }
  const names = failed.map((job) => job.name);
  const summary = names.length ? `job ${names.map((n) => `\`${n}\``).join(', ')} ${timedOut.size ? 'failed or timed out' : run.conclusion}` : run.conclusion;
  return { summary, details: parts.join('\n') };
}

function args(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const a = argv[i];
    if (a === '--dry-run') out.dryRun = true;
    else if (a.startsWith('--')) out[a.slice(2)] = argv[(i += 1)];
    else out._.push(a);
  }
  return out;
}

export async function main(argv = process.argv.slice(2), env = process.env) {
  const opts = args(argv);
  const repo = opts.repo ?? env.GITHUB_REPOSITORY;
  if (!repo) throw new Error('Set GITHUB_REPOSITORY or pass --repo owner/name.');
  const gh = client({ repo, token: env.GH_TOKEN ?? env.GITHUB_TOKEN, dryRun: Boolean(opts.dryRun) });
  const now = new Date().toISOString();
  const issue = await openIssue(gh);

  if (opts._[0] === 'run') {
    const run = await gh.read(`/actions/runs/${opts['run-id']}`);
    const prRuns = { workflows: String(opts['pr-workflows'] ?? '').split(',').map((s) => s.trim()).filter(Boolean), branchPrefix: opts['pr-branch-prefix'] ?? '' };
    let outcome = outcomeOf(run, prRuns);
    const source = sourceOf(run);
    const jobs = outcome === 'fail' ? await runJobs(gh, run) : null;
    if (jobs && judgeJobs(jobs.jobs, jobs.timedOut) === 'ignore') outcome = 'ignore';
    console.log(`${source} run ${run.id} on ${run.head_branch} (${run.event}): ${run.conclusion}, so ${outcome}.`);
    const { summary, details } = outcome === 'fail' ? await failureDetails(gh, run, jobs) : { summary: run.conclusion, details: '' };
    await apply(gh, issue, plan({ issue, source, outcome, url: run.html_url, summary, details, now }));
    return;
  }

  if (opts._[0] === 'stale') {
    const site = (opts.site ?? 'https://benchmarks.rewirebio.io').replace(/\/$/, '');
    const res = await fetch(`${site}/deployment.json`, { headers: { 'Cache-Control': 'no-cache' } });
    if (!res.ok) throw new Error(`${site}/deployment.json: ${res.status}`);
    const liveId = (await res.json()).release_id;
    if (!liveId) throw new Error(`${site}/deployment.json has no release_id.`);
    const listed = await gh.read('/releases?per_page=100');
    const releases = listed.map((r) => ({ tagName: r.tag_name, publishedAt: r.published_at }));
    const maxAgeHours = Number(opts['max-age-hours'] ?? 24);
    const result = staleness({ liveId, releases, now, maxAgeHours });
    console.log(`Live ${liveId}; newest serving ${result.newest}, published ${result.ageHours.toFixed(1)} h ago.`);
    const summary = `the site serves ${liveId}, but serving/${result.newest} was published ${Math.floor(result.ageHours)} hours ago`;
    const url = `${site}/deployment.json`;
    const outcome = result.stale ? 'fail' : liveId === result.newest ? 'pass' : 'ignore';
    await apply(gh, issue, plan({ issue, source: LIVE_SOURCE, outcome, url, summary, details: '', now }));
    return;
  }

  throw new Error('Usage: pipeline-alert.mjs run --run-id <id> [--pr-workflows a.yml,b.yml --pr-branch-prefix x/] | stale --site <url> [--dry-run]');
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  main().catch((error) => {
    console.error(`::error::${error.message}`);
    process.exit(1);
  });
}
