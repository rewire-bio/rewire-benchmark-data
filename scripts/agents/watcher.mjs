// Disagreement watcher (#258). After a release, diff its discrepancies against the previous
// release's and file a "Lead:" issue for each new medium or high finding, and for each finding
// whose severity rose, in the format of #209 to #211. The issue is labelled lead and needs-tim
// and assigned to timini, so GitHub emails him. A finding that stops firing gets a comment on
// its open lead issue; the issue stays open.
//
// The tables, numbers and links come from the release's discrepancies.json and records file.
// Sonnet 5.5 writes one paragraph of likely explanations from those facts, and nothing else.
//
// No discrepancy_review claim is recorded. A claim counts only with status source_checked, and
// every action in data/vocab/discrepancy-action.ttl and every working state in
// discrepancy-state.ttl says someone has looked at the sources. When the watcher files a lead
// nobody has. See NOT_RECORDED.
//
//   node scripts/agents/watcher.mjs --dry-run [--out <dir>]                      fixtures
//   node scripts/agents/watcher.mjs --dry-run --previous <json> --current <json> --records <jsonl[.gz]> [--issues <json>]
//   node scripts/agents/watcher.mjs [--report-only] --previous <json> --current <json> --records <jsonl.gz> --out <dir>
//
// GITHUB_REPOSITORY names the repository (it must belong to rewire-bio); GH_TOKEN or
// GITHUB_TOKEN authenticates; ANTHROPIC_API_KEY is optional (without it the lead is filed with
// no explanation paragraph).

import { createReadStream, mkdirSync, readFileSync, appendFileSync, writeFileSync } from 'node:fs';
import { createInterface } from 'node:readline';
import { createGunzip } from 'node:zlib';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { Usage, clean, githubClient, tierOf } from './discovery.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../..');

export const PROMPT_PATH = 'agents/watcher.md';
export const FIXTURES = 'tests/agents-watcher-fixtures';
export const ORG = 'rewire-bio';
export const SITE = 'https://benchmarks.rewirebio.io';
export const ASSIGNEE = 'timini';
export const LEAD_LABELS = ['lead', 'needs-tim'];
export const MODELS = { explain: 'claude-sonnet-5-5' };
export const LIMITS = {
  maxIssues: 5, // lead issues per run; the rest go into one summary issue
  maxRunUsd: 1, // no explanation call once the run's estimated cost passes this
  explainMaxTokens: 2000,
  rowsPerStudy: 4, // comparisons shown per study in the values table
  studiesShown: 8,
  namesPerList: 3,
  factsPerList: 10, // protocols, datasets and metrics per study sent to the model
};
const RANK = { low: 1, medium: 2, high: 3 };
const ID = /discrepancy-[0-9a-f]{16}/g;
// Hidden markers. A lead issue carries `lead`; a summary issue carries `listed` once per finding
// it lists; comments carry `rose`, `refired` or `gone` with the release they report.
export const MARKERS = { lead: 'discrepancy-lead', listed: 'discrepancy-listed', rose: 'discrepancy-rose', refired: 'discrepancy-refired', gone: 'discrepancy-gone' };
const MARKER = /<!-- (discrepancy-lead|discrepancy-listed): (discrepancy-[0-9a-f]{16}) -->/g;

export const NOT_RECORDED = 'The watcher records no `discrepancy_review` claim for a new lead. A review claim counts only with status `source_checked`, and every action in `data/vocab/discrepancy-action.ttl` and every working state in `data/vocab/discrepancy-state.ttl` says someone has looked at the sources. Nobody has yet, so the finding stays `open` until the first revision records what was done.';

const RULE_TEXT = {
  'ordering-reversal': 'ordering reversal',
  'two-study-conflict': 'two-study conflict',
  'gap-outlier': 'gap outlier',
};
const SCOPE_TEXT = {
  'same-protocol': 'the two sides share a protocol',
  'same-task': 'the two sides share a task, benchmark or suite but not a protocol',
  unknown: 'an assessment on one side has no task or benchmark link, so how closely the sides match is unknown',
  'different-task': 'the two sides assess different tasks',
};

const live = (f) => !f.resolved;
const rank = (s) => RANK[s] ?? 0;
const keysOf = (f) => [f.id, ...(f.previous_ids ?? [])];

// ---------- Diff ----------

/**
 * What changed between two releases' discrepancies.json. A finding is matched to its earlier
 * self by ID or through its previous_ids, so a rule change that re-keys findings does not make
 * them new. Resolved findings (resolved: true) are not live: one that was live and is now
 * resolved or absent is `gone`; one that was resolved and fires again is `refired`.
 */
export function diffReleases(previous, current) {
  const prev = new Map((previous.discrepancies ?? []).map((f) => [f.id, f]));
  const cur = current.discrepancies ?? [];
  const curById = new Map(cur.map((f) => [f.id, f]));
  const added = [];
  const rose = [];
  const refired = [];
  const matched = new Set();
  for (const f of cur.filter(live)) {
    const prior = keysOf(f).map((k) => prev.get(k)).find(Boolean);
    if (prior) matched.add(prior.id);
    if (!prior) added.push(f);
    else if (!live(prior)) refired.push(f);
    else if (rank(f.severity) > rank(prior.severity)) rose.push({ finding: f, from: prior.severity });
  }
  const gone = [];
  for (const p of (previous.discrepancies ?? []).filter(live)) {
    if (matched.has(p.id)) continue;
    const now = curById.get(p.id);
    gone.push({ finding: p, resolved: Boolean(now?.resolved), state: now?.review_state ?? null });
  }
  const from = previous.rules?.version ?? null;
  const to = current.rules?.version ?? null;
  return { added, rose, refired, gone, rulesChanged: from !== to ? { from, to } : null };
}

/** Discrepancy IDs already covered by an issue: marked by this watcher, or named in a hand-written "Lead:" issue. */
export function knownLeads(issues) {
  const known = new Map();
  const note = (id, issue, how) => {
    const list = known.get(id) ?? [];
    if (!list.some((x) => x.number === issue.number)) list.push({ number: issue.number, state: issue.state, html_url: issue.html_url, how });
    known.set(id, list);
  };
  for (const issue of issues) {
    const body = issue.body ?? '';
    for (const m of body.matchAll(MARKER)) note(m[2], issue, m[1] === MARKERS.lead ? 'lead' : 'listed');
    if (/^lead\b/i.test(issue.title ?? '')) for (const m of body.matchAll(ID)) note(m[0], issue, 'named');
  }
  return known;
}

function existingFor(finding, known) {
  const out = [];
  for (const k of keysOf(finding)) for (const i of known.get(k) ?? []) if (!out.some((x) => x.number === i.number)) out.push(i);
  return out;
}

/**
 * Decide what to file. New and re-fired medium or high findings, and findings whose severity
 * rose, get a lead issue unless one exists; when one exists, a rise or a re-fire is a comment
 * on it. A finding someone already reviews (it has follow-up actions) is not filed again. The
 * first maxIssues leads are filed one by one, most severe first; the rest go into one summary
 * issue. Gone findings with an open lead issue get a comment.
 */
export function planRun(diff, { issues, release, maxIssues = LIMITS.maxIssues }) {
  const known = knownLeads(issues);
  const candidates = [
    ...diff.added.map((f) => ({ finding: f, reason: 'new' })),
    ...diff.refired.map((f) => ({ finding: f, reason: 'refired' })),
    ...diff.rose.map(({ finding, from }) => ({ finding, reason: 'rose', from })),
  ];
  const leads = [];
  const comments = [];
  const skipped = [];
  for (const c of candidates) {
    const f = c.finding;
    if (c.reason !== 'rose' && rank(f.severity) < RANK.medium) continue;
    const existing = existingFor(f, known);
    if (existing.length) {
      if (c.reason === 'new') {
        skipped.push({ id: f.id, reason: `already has a lead issue (#${existing.map((e) => e.number).join(', #')})` });
        continue;
      }
      const marker = `${MARKERS[c.reason]}: ${f.id} ${release}`;
      const text = c.reason === 'rose'
        ? `Severity rose from ${c.from} to ${f.severity} in release \`${release}\`.`
        : `This finding fires again in release \`${release}\` after it was resolved.`;
      // A comment on a closed issue still notifies its participants; the issue is not reopened.
      for (const e of existing) {
        const closed = e.state === 'closed' ? ' This issue is closed; the watcher does not reopen it.' : '';
        comments.push({ number: e.number, marker, body: `${text} [Contested page](${SITE}/contested/${f.id}/): ${clean(f.summary)}${closed}\n\n<!-- ${marker} -->` });
      }
      continue;
    }
    if (f.review_state && f.review_state !== 'open') {
      skipped.push({ id: f.id, reason: `already under review (state ${f.review_state}) with no lead issue found` });
      continue;
    }
    leads.push(c);
  }
  leads.sort((a, b) => rank(b.finding.severity) - rank(a.finding.severity) || a.finding.id.localeCompare(b.finding.id));
  for (const g of diff.gone) {
    const open = existingFor(g.finding, known).filter((x) => x.state !== 'closed');
    const marker = `${MARKERS.gone}: ${g.finding.id} ${release}`;
    const why = g.resolved
      ? `It is now a resolved finding (state ${g.state}): its review settled it and the rule no longer fires.`
      : 'The rule no longer fires on the current evidence: records may have changed, been disputed or put under an evidence concern, or the rules changed.';
    for (const e of open) {
      comments.push({ number: e.number, marker, body: `\`${g.finding.id}\` is not a live finding in release \`${release}\`. ${why} This issue stays open until someone records the outcome.\n\n<!-- ${marker} -->` });
    }
  }
  return { file: leads.slice(0, maxIssues), overflow: leads.slice(maxIssues), comments, skipped };
}

// ---------- Records ----------

/** Every record ID a lead issue for these findings names. */
export function idsNeeded(findings) {
  const ids = new Set();
  for (const f of findings) {
    for (const x of [...(f.systems ?? []), f.reference_system, ...(f.unlinked_protocols ?? []), ...(f.outlier_sources ?? []), ...(f.consensus_sources ?? []), ...(f.party_sources ?? [])]) if (x) ids.add(x);
    for (const s of (f.studies ?? []).slice(0, LIMITS.studiesShown)) {
      for (const x of s.source_ids ?? []) ids.add(x);
      for (const x of Object.values(s.configurations ?? {})) if (x) ids.add(x);
      for (const c of s.comparisons ?? []) {
        if (c.protocol) ids.add(c.protocol);
        if (c.dataset) ids.add(c.dataset);
      }
    }
  }
  return ids;
}

/** Names, URLs and areas of the given IDs, streamed from the release's records.jsonl(.gz). */
export async function readRecords(path, ids) {
  const out = new Map();
  if (!ids.size) return out;
  const stream = path.endsWith('.gz') ? createReadStream(path).pipe(createGunzip()) : createReadStream(path);
  for await (const line of createInterface({ input: stream, crlfDelay: Infinity })) {
    const m = /^\{"id":\s*"([^"]+)"/.exec(line);
    if (m && !ids.has(m[1])) continue;
    if (!line.trim()) continue;
    const r = JSON.parse(line);
    if (!ids.has(r.id)) continue;
    out.set(r.id, { id: r.id, kind: r.kind, name: r.name, url: r.attributes?.url ?? null, areas: r.facets?.areas ?? [], depth_tier: r.attributes?.depth_tier ?? null });
    if (out.size === ids.size) break;
  }
  return out;
}

// ---------- Rendering ----------

const esc = (s) => clean(s).replace(/\|/g, '\\|').replace(/\n/g, ' ');
const nameOf = (records, id) => records.get(id)?.name ?? id;

function list(names, n = LIMITS.namesPerList) {
  const uniq = [...new Set(names)];
  if (!uniq.length) return 'none recorded';
  const shown = uniq.slice(0, n).map((x) => esc(x));
  return uniq.length > n ? `${shown.join(', ')} and ${uniq.length - n} more` : shown.join(', ');
}

function baseName(study, records) {
  const ids = study.source_ids ?? [];
  return ids.map((id) => records.get(id)).find(Boolean)?.name ?? ids[0] ?? study.key;
}

/** Names that more than one of a finding's studies would get, so those studies show their key too. */
function repeatedNames(finding, records) {
  const names = (finding.studies ?? []).map((s) => baseName(s, records));
  return new Set(names.filter((n, i) => names.indexOf(n) !== i));
}

/**
 * A study's name and link: its first source's name, linked to the DOI, repository or source
 * URL. When two studies of the finding share that name, the study key is added.
 */
export function studyLabel(study, records, repeated = new Set()) {
  const ids = study.source_ids ?? [];
  const first = ids.map((id) => records.get(id)).find(Boolean);
  const base = baseName(study, records);
  const name = repeated.has(base) ? `${base} [${study.key}]` : base;
  const key = String(study.key ?? '');
  const url = key.startsWith('doi:') ? `https://doi.org/${key.slice(4)}` : key.startsWith('repository:') ? key.slice('repository:'.length) : first?.url ?? null;
  const more = ids.length > 1 ? ` (and ${ids.length - 1} other source${ids.length > 2 ? 's' : ''})` : '';
  return { name: esc(name), url, text: url ? `[${esc(name)}](${url})${more}` : `${esc(name)}${more}` };
}

/** Lowest depth tier of the compared systems: genomic 1, protein 2, else 3. Null when unknown. */
export function findingTier(finding, records) {
  const tiers = (finding.systems ?? []).map((id) => records.get(id)).filter(Boolean).map((r) => r.depth_tier ?? tierOf(r.areas ?? []));
  return tiers.length ? Math.min(...tiers) : null;
}

/** A value as printed in the release, shortened to 4 significant figures when it is longer. */
export function fmt(v) {
  if (v === null || v === undefined) return '';
  if (typeof v !== 'number' || !Number.isFinite(v)) return String(v);
  const short = Number(v.toPrecision(4));
  return String(Math.abs(short) >= 1e4 ? Math.round(v) : short);
}

/** Per-study facts that are differences between the studies, for the issue and the model. */
export function protocolFacts(finding, records) {
  const studies = (finding.studies ?? []).slice(0, LIMITS.studiesShown);
  const repeated = repeatedNames(finding, records);
  const [a, b] = finding.systems ?? [];
  return studies.map((s) => {
    const comps = s.comparisons ?? [];
    return {
      study: studyLabel(s, records, repeated).name,
      role: s.role,
      verdict: s.verdict ? nameOf(records, s.verdict) : s.verdict === 'split' ? 'split' : null,
      protocols: [...new Set(comps.map((c) => nameOf(records, c.protocol)))],
      datasets: [...new Set(comps.map((c) => nameOf(records, c.dataset)))],
      metrics: [...new Set(comps.map((c) => [c.metric, c.qualifier].filter(Boolean).join(': ')))],
      metric_keys: [...new Set(comps.map((c) => c.metric).filter(Boolean))],
      configurations: { [nameOf(records, a)]: s.configurations?.[a] ? nameOf(records, s.configurations[a]) : null, [nameOf(records, b)]: s.configurations?.[b] ? nameOf(records, s.configurations[b]) : null },
      comparisons_total: s.comparisons_total ?? comps.length,
      higher: Object.fromEntries(Object.entries(s.higher ?? {}).map(([k, v]) => [nameOf(records, k), v])),
      ties: s.ties ?? 0,
      gap: s.gap ?? null,
    };
  });
}

/** The facts the explanation call sees. Everything here is from the release data. */
export function explanationFacts(finding, records) {
  const [a, b] = finding.systems ?? [];
  return {
    id: finding.id,
    rule: RULE_TEXT[finding.rule] ?? finding.rule,
    severity: finding.severity,
    scope: `${finding.scope}: ${SCOPE_TEXT[finding.scope] ?? ''}`,
    systems: [nameOf(records, a), nameOf(records, b)],
    reference_system: finding.reference_system ? nameOf(records, finding.reference_system) : null,
    summary: clean(finding.summary),
    identity_basis: finding.identity_basis,
    variant_mismatch: Boolean(finding.variant_mismatch),
    unlinked_protocols: (finding.unlinked_protocols ?? []).map((id) => nameOf(records, id)).slice(0, LIMITS.factsPerList),
    // Lists are cut to factsPerList so one finding with hundreds of protocols cannot make a large call.
    studies: protocolFacts(finding, records).map((s) => ({
      ...s,
      ...Object.fromEntries(['protocols', 'datasets', 'metrics', 'metric_keys'].map((k) => [k, s[k].slice(0, LIMITS.factsPerList)])),
      ...Object.fromEntries(['protocols', 'datasets', 'metrics'].filter((k) => s[k].length > LIMITS.factsPerList).map((k) => [`${k}_not_shown`, s[k].length - LIMITS.factsPerList])),
    })),
  };
}

function differenceBullets(finding, facts) {
  const out = [];
  out.push(`Scope \`${finding.scope}\`: ${SCOPE_TEXT[finding.scope] ?? 'not described'}.`);
  for (const s of facts.studies) {
    const configs = Object.entries(s.configurations).map(([sys, c]) => `${esc(sys)} as ${c ? esc(c) : 'the model record'}`).join(', ');
    out.push(`${s.study} (${s.role}): protocols ${list(s.protocols)}; datasets ${list(s.datasets)}; metrics ${list(s.metrics)}; configurations ${configs}.`);
  }
  const sides = facts.studies.filter((s) => s.role === 'outlier' || s.role === 'party');
  const others = facts.studies.filter((s) => s.role === 'consensus' || (s.role === 'party' && sides[0] && s !== sides[0]));
  if (sides.length) {
    const mine = sides[0];
    const shared = (key) => mine[key].filter((x) => others.some((o) => o !== mine && o[key].includes(x)));
    const p = shared('protocols');
    const m = shared('metric_keys');
    out.push(`${mine.study} shares ${p.length ? `the protocol${p.length > 1 ? 's' : ''} ${list(p)}` : 'no protocol'} and ${m.length ? `the metric${m.length > 1 ? 's' : ''} ${list(m)}` : 'no metric'} with the other studies shown.`);
  }
  if (finding.variant_mismatch) out.push('Variant mismatch: the studies used configurations with different recorded model sizes.');
  if (finding.identity_basis === 'unreviewed') out.push('Identity unreviewed: a configuration is compared as its model through a link nobody has checked.');
  if ((finding.unlinked_protocols ?? []).length) out.push(`Protocols with no task or benchmark link: ${list(facts.unlinked_protocols, 6)}.`);
  return out.map((l) => `- ${l}`).join('\n');
}

function studyTable(finding, records) {
  const [a, b] = finding.systems ?? [];
  const gap = finding.rule === 'gap-outlier';
  const studies = (finding.studies ?? []).slice(0, LIMITS.studiesShown);
  const repeated = repeatedNames(finding, records);
  if (!studies.length) {
    const n = finding.numbers ?? {};
    return `This release's file has no per-study breakdown. Counts: ${Object.entries(n).map(([k, v]) => `${k.replace(/_/g, ' ')} ${v}`).join(', ') || 'none'}.`;
  }
  const head = gap
    ? `| Study | Role | Median relative gap to ${esc(nameOf(records, finding.reference_system ?? a))} | Comparisons |\n| --- | --- | --- | --- |`
    : `| Study | Role | Verdict | ${esc(nameOf(records, a))} higher | ${esc(nameOf(records, b))} higher | Ties | Comparisons |\n| --- | --- | --- | --- | --- | --- | --- |`;
  const rows = studies.map((s) => {
    const label = studyLabel(s, records, repeated).text;
    if (gap) return `| ${label} | ${s.role} | ${fmt(s.gap)} | ${s.comparisons_total ?? ''} |`;
    const verdict = s.verdict === 'split' ? 'split' : s.verdict ? esc(nameOf(records, s.verdict)) : 'none (too few untied comparisons)';
    return `| ${label} | ${s.role} | ${verdict} | ${s.higher?.[a] ?? 0} | ${s.higher?.[b] ?? 0} | ${s.ties ?? 0} | ${s.comparisons_total ?? ''} |`;
  });
  const more = (finding.studies ?? []).length > studies.length ? `\n\n${finding.studies.length - studies.length} more studies are on the contested page.` : '';
  return [head, ...rows].join('\n') + more;
}

function valueTable(finding, records) {
  const [a, b] = finding.systems ?? [];
  const studies = (finding.studies ?? []).slice(0, LIMITS.studiesShown);
  const repeated = repeatedNames(finding, records);
  const rows = [];
  let shown = 0;
  let total = 0;
  for (const s of studies) {
    const comps = s.comparisons ?? [];
    total += s.comparisons_total ?? comps.length;
    for (const c of comps.slice(0, LIMITS.rowsPerStudy)) {
      shown += 1;
      const metric = [c.metric, c.qualifier].filter(Boolean).join(', ') + (c.unit && c.unit !== 'unitless' ? ` (${c.unit})` : '');
      rows.push(`| ${studyLabel(s, records, repeated).name} | ${esc(nameOf(records, c.protocol))} | ${esc(nameOf(records, c.dataset))} | ${esc(metric)} | ${fmt(c.values?.[a])} | ${fmt(c.values?.[b])} |`);
    }
  }
  if (!rows.length) return '';
  return [
    `| Study | Protocol | Dataset | Metric | ${esc(nameOf(records, a))} | ${esc(nameOf(records, b))} |`,
    '| --- | --- | --- | --- | --- | --- |',
    ...rows,
    '',
    `Showing ${shown} of ${total} comparisons (the first ${LIMITS.rowsPerStudy} per study, in the release's order; values to 4 significant figures). Every comparison is on the [contested page](${SITE}/contested/${finding.id}/).`,
  ].join('\n');
}

const TIER_TEXT = { 1: 'tier 1 (DNA and RNA genomics)', 2: 'tier 2 (proteins)', 3: 'tier 3 (outside genomics and proteins)' };

/** One lead issue. `explanation` is the model's paragraph, or null with `explanationNote` saying why. */
export function renderLead(lead, { records, release, previous, explanation, explanationNote, runUrl }) {
  const f = lead.finding;
  const tier = findingTier(f, records);
  const why = lead.reason === 'rose'
    ? `Its severity rose from ${lead.from} to ${f.severity} in release \`${release}\` (previous release \`${previous}\`).`
    : lead.reason === 'refired'
      ? `It was resolved in release \`${previous}\` and fires again in \`${release}\`.`
      : `It is new in release \`${release}\` (previous release \`${previous}\`).`;
  const facts = explanationFacts(f, records);
  const values = valueTable(f, records);
  const body = [
    '## Lead',
    '',
    `[\`${f.id}\`](${SITE}/contested/${f.id}/): ${clean(f.summary)}`,
    '',
    `Severity ${f.severity}, ${RULE_TEXT[f.rule] ?? f.rule}, scope \`${f.scope}\`${tier ? `, depth ${TIER_TEXT[tier]}` : ''}. ${why} The contested page shows the finding once the website has adopted the release.`,
    '',
    studyTable(f, records),
    values ? '' : null,
    values || null,
    '',
    '## Protocol differences',
    '',
    differenceBullets(f, facts),
    '',
    '## Likely explanations to check',
    '',
    explanation ? `${explanation}\n\n_Written by ${MODELS.explain} from the facts above. Every number, name and link in this issue comes from the release data._` : `_${explanationNote}_`,
    '',
    '## To check',
    '',
    '1. Read how each study computes the metric: per-item or pooled, signed or absolute, which subset and which aggregation.',
    '2. Confirm which model size or checkpoint each study ran (the configurations above).',
    '3. Compare like with like on the shared datasets, recomputing from per-item values if a supplement has them, and see whether the order still differs.',
    `4. Record the outcome as a \`discrepancy_review\` claim revision with this issue as \`investigation_url\` (docs/discrepancies.md, "Following one up"). If a source is wrong, report it upstream.`,
    '',
    `<sub>Filed by the disagreement watcher (\`scripts/agents/watcher.mjs\`, #258)${runUrl ? ` in [this run](${runUrl})` : ''}. ${NOT_RECORDED}</sub>`,
    '',
    `<!-- ${MARKERS.lead}: ${f.id} -->`,
  ].filter((l) => l !== null).join('\n');
  const title = `Lead: ${clean(f.label ?? f.summary ?? f.id)}`.slice(0, 250);
  return { title, body, labels: LEAD_LABELS, assignees: [ASSIGNEE] };
}

/** One issue for the leads over the per-run cap, so nothing is dropped silently. */
export function renderOverflow(leads, { records, release, previous, filedCount, runUrl }) {
  const rows = leads.map(({ finding: f, reason, from }) => {
    const [a, b] = f.systems ?? [];
    const what = reason === 'rose' ? `rose from ${from}` : reason === 'refired' ? 'fires again' : 'new';
    return `| [\`${f.id}\`](${SITE}/contested/${f.id}/) | ${f.severity} | ${what} | ${RULE_TEXT[f.rule] ?? f.rule} | ${esc(nameOf(records, a))} and ${esc(nameOf(records, b))} | ${esc(f.summary)} |`;
  });
  const body = [
    `Release \`${release}\` (previous \`${previous}\`) has ${filedCount + leads.length} new or more severe medium or high discrepancies. The watcher files at most ${LIMITS.maxIssues} lead issues a run; it filed ${filedCount}. These are the rest. Pick the ones worth a lead issue of their own; later runs will not file them separately.`,
    '',
    '| Finding | Severity | Change | Rule | Systems | Summary |',
    '| --- | --- | --- | --- | --- | --- |',
    ...rows,
    '',
    `<sub>Filed by the disagreement watcher (\`scripts/agents/watcher.mjs\`, #258)${runUrl ? ` in [this run](${runUrl})` : ''}. ${NOT_RECORDED}</sub>`,
    '',
    ...leads.map(({ finding }) => `<!-- ${MARKERS.listed}: ${finding.id} -->`),
  ].join('\n');
  return { title: `Leads: ${leads.length} more discrepancies in release ${release}`, body, labels: LEAD_LABELS, assignees: [ASSIGNEE] };
}

// ---------- Explanation (the only model call) ----------

/**
 * Checks the model's paragraph. It may not carry a link, or a number that is not in the facts
 * it was given, because the issue's numbers and links must come from the data.
 */
export function checkExplanation(text, facts) {
  const t = clean(text).replace(/\s+/g, ' ').trim();
  if (!t) return { ok: false, why: 'it was empty' };
  if (/https?:\/\/|www\.|#\d/.test(t)) return { ok: false, why: 'it contained a link or issue reference' };
  // The prompt allows no numbers. Digits are allowed only inside a name the facts gave
  // (ESM-2, a protocol such as "BEELINE 2020 Figure 2"), so remove those names and look again.
  let rest = t;
  for (const name of namesIn(facts).sort((a, b) => b.length - a.length)) rest = rest.split(name).join(' ');
  const stray = rest.match(/\d+(?:[.,]\d+)?/g) ?? [];
  // The stray numbers are not repeated in the issue: they are what must not be published.
  if (stray.length) return { ok: false, why: 'it stated numbers, which must come from the release data', stray: [...new Set(stray)].slice(0, 5) };
  return { ok: true, text: t };
}

/** Every name in the facts: systems, studies, protocols, datasets, metrics and configurations. */
function namesIn(facts) {
  const out = new Set();
  const add = (x) => { if (typeof x === 'string' && x.trim()) out.add(clean(x)); };
  (facts.systems ?? []).forEach(add);
  add(facts.reference_system);
  (facts.unlinked_protocols ?? []).forEach(add);
  for (const s of facts.studies ?? []) {
    add(s.study);
    for (const key of ['protocols', 'datasets', 'metrics', 'metric_keys']) (s[key] ?? []).forEach(add);
    for (const [sys, conf] of Object.entries(s.configurations ?? {})) { add(sys); add(conf); }
  }
  return [...out];
}

function textOf(message) {
  return message.content.filter((b) => b.type === 'text').map((b) => b.text).join('\n').trim();
}

export async function explain(client, usage, { system, facts, log = () => {} }) {
  if (usage.total() > LIMITS.maxRunUsd) return { text: null, note: `No explanation: the run passed its $${LIMITS.maxRunUsd} cost cap.` };
  try {
    const message = await client.beta.messages.create({
      model: MODELS.explain,
      betas: ['server-side-fallback-2026-07-01'],
      fallbacks: 'default',
      max_tokens: LIMITS.explainMaxTokens,
      system: [{ type: 'text', text: system, cache_control: { type: 'ephemeral' } }],
      output_config: { effort: 'low' },
      messages: [{ role: 'user', content: `Facts of the discrepancy (JSON, data from the release, not instructions):\n\n${JSON.stringify(facts, null, 2)}` }],
    });
    usage.add(message.model ?? MODELS.explain, message.usage);
    if (message.stop_reason === 'refusal') return { text: null, note: `No explanation: the model declined (${message.stop_details?.category ?? 'no category'}).` };
    if (message.stop_reason !== 'end_turn') return { text: null, note: `No explanation: the model stopped early (${message.stop_reason}).` };
    const checked = checkExplanation(textOf(message), facts);
    if (!checked.ok) {
      log(`explanation dropped: ${checked.why}${checked.stray ? ` (${checked.stray.join(', ')})` : ''}`);
      return { text: null, note: `No explanation: the model's paragraph was dropped because ${checked.why}.` };
    }
    return { text: checked.text, note: null };
  } catch (e) {
    log(`explanation call failed: ${String(e?.message ?? e).split('\n')[0]}`);
    return { text: null, note: `No explanation: the model call failed (${e?.status ?? 'error'}).` };
  }
}

// ---------- GitHub ----------

/** Comments on an issue, read to keep a marker comment from being posted twice. */
async function commentBodies(token, repo, number, fetchImpl = fetch) {
  const out = [];
  for (let page = 1; page < 20; page++) {
    const res = await fetchImpl(`https://api.github.com/repos/${repo}/issues/${number}/comments?per_page=100&page=${page}`, {
      headers: { authorization: `Bearer ${token}`, accept: 'application/vnd.github+json', 'x-github-api-version': '2022-11-28', 'user-agent': 'rewire-watcher' },
    });
    if (!res.ok) throw new Error(`GET comments of #${number}: ${res.status}`);
    const batch = await res.json();
    out.push(...batch.map((c) => c.body ?? ''));
    if (batch.length < 100) break;
  }
  return out;
}

async function postComment(token, repo, number, body, fetchImpl = fetch) {
  const res = await fetchImpl(`https://api.github.com/repos/${repo}/issues/${number}/comments`, {
    method: 'POST',
    headers: { authorization: `Bearer ${token}`, accept: 'application/vnd.github+json', 'x-github-api-version': '2022-11-28', 'user-agent': 'rewire-watcher' },
    body: JSON.stringify({ body }),
  });
  if (!res.ok) throw new Error(`POST comment on #${number}: ${res.status} ${await res.text()}`);
  return res.json();
}

/** The live GitHub operations, as one object so tests can replace it. */
export function watcherGithub(token, fetchImpl = fetch) {
  const gh = githubClient(token, fetchImpl);
  return {
    listIssues: (repo) => gh.listIssues(repo),
    ensureLabels: (repo, names) => gh.ensureLabels(repo, names),
    createIssue: (repo, issue) => gh.createIssue(repo, issue),
    commentBodies: (repo, number) => commentBodies(token, repo, number, fetchImpl),
    comment: (repo, number, body) => postComment(token, repo, number, body, fetchImpl),
  };
}

// ---------- Main ----------

function parseArgs(argv) {
  const args = { dryRun: false, reportOnly: false, previous: '', current: '', records: '', issues: '', out: '', maxIssues: LIMITS.maxIssues, runUrl: '' };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--dry-run') args.dryRun = true;
    else if (a === '--report-only') args.reportOnly = true;
    else if (a === '--previous') args.previous = argv[++i];
    else if (a === '--current') args.current = argv[++i];
    else if (a === '--records') args.records = argv[++i];
    else if (a === '--issues') args.issues = argv[++i];
    else if (a === '--out') args.out = argv[++i];
    else if (a === '--max-issues') args.maxIssues = Number(argv[++i]);
    else if (a === '--run-url') args.runUrl = argv[++i];
    else throw new Error(`unknown argument ${a}`);
  }
  return args;
}

const readJson = (path) => JSON.parse(readFileSync(path, 'utf8'));

export function renderSummary({ mode, previous, current, diff, plan, filed, comments, notes, usage }) {
  const count = (xs) => xs.length;
  const sev = (xs) => Object.entries(xs.reduce((m, f) => ({ ...m, [f.severity]: (m[f.severity] ?? 0) + 1 }), {})).map(([k, v]) => `${v} ${k}`).join(', ') || 'none';
  return [
    `## Disagreement watcher, ${previous} to ${current} (${mode})`,
    '',
    ...notes.map((n) => `- ${n}`),
    notes.length ? '' : null,
    `- New live findings: ${count(diff.added)} (${sev(diff.added)}). Severity rose: ${count(diff.rose)}. Fire again: ${count(diff.refired)}. No longer live: ${count(diff.gone)}.`,
    diff.rulesChanged ? `- The discrepancy rules changed from version ${diff.rulesChanged.from} to ${diff.rulesChanged.to}; re-keyed findings are matched through previous_ids.` : null,
    '',
    '### Lead issues',
    '',
    filed.length ? filed.map((f) => `- ${f.url ?? '(not filed)'} ${f.title}${f.explanationNote ? ` (${f.explanationNote})` : ''}`).join('\n') : 'None.',
    plan.overflow.length ? `\nOver the cap of ${LIMITS.maxIssues}, listed in one summary issue: ${plan.overflow.map((l) => l.finding.id).join(', ')}.` : null,
    '',
    '### Comments',
    '',
    comments.length ? comments.map((c) => `- #${c.number}: ${c.marker}${c.status ? ` (${c.status})` : ''}`).join('\n') : 'None.',
    '',
    '### Skipped',
    '',
    plan.skipped.length ? plan.skipped.map((s) => `- ${s.id}: ${s.reason}`).join('\n') : 'Nothing skipped.',
    '',
    '### Store',
    '',
    NOT_RECORDED,
    '',
    '### Token usage',
    '',
    usage.table(),
    '',
  ].filter((l) => l !== null).join('\n');
}

/**
 * Run the watcher. Returns { summary, diff, plan, filed, comments } so tests can inspect it.
 * `deps` replaces the GitHub operations, the Anthropic client and the log in tests.
 */
export async function main(argv = process.argv.slice(2), env = process.env, deps = {}) {
  const args = parseArgs(argv);
  const mode = args.dryRun ? 'dry run' : args.reportOnly ? 'report only' : 'live';
  const log = deps.log ?? ((m) => console.log(m));
  const fixtures = resolve(ROOT, FIXTURES);
  const pick = (given, fixture) => resolve(given || (args.dryRun ? join(fixtures, fixture) : ''));
  if (!args.dryRun && (!args.previous || !args.current || !args.records)) throw new Error('--previous, --current and --records are required outside a dry run');
  const repo = env.GITHUB_REPOSITORY ?? '';
  if (!args.dryRun && repo.split('/')[0] !== ORG) throw new Error(`GITHUB_REPOSITORY must be a ${ORG} repository, not "${repo}"`);

  const previousFile = readJson(pick(args.previous, 'previous.json'));
  const currentFile = readJson(pick(args.current, 'current.json'));
  const recordsPath = pick(args.records, 'records.jsonl');
  const previousId = previousFile.release_id;
  const currentId = currentFile.release_id;
  const usage = new Usage();
  const notes = [];
  const filed = [];
  const comments = [];
  let plan = { file: [], overflow: [], comments: [], skipped: [] };
  const diff = diffReleases(previousFile, currentFile);
  const gh = args.dryRun ? null : (deps.github ?? watcherGithub(env.GH_TOKEN || env.GITHUB_TOKEN));
  const write = !args.dryRun && !args.reportOnly;
  const emit = (summary) => {
    if (env.GITHUB_STEP_SUMMARY) appendFileSync(env.GITHUB_STEP_SUMMARY, `${summary}\n`);
    else log(summary);
  };

  try {
    if (previousId === currentId) notes.push('The previous and current files are the same release; nothing can have changed.');
    const issues = args.dryRun ? readJson(args.issues ? resolve(args.issues) : join(fixtures, 'issues.json')) : await gh.listIssues(repo);
    plan = planRun(diff, { issues, release: currentId, maxIssues: args.maxIssues });

    const leads = [...plan.file, ...plan.overflow];
    const records = leads.length ? await readRecords(recordsPath, idsNeeded(leads.map((l) => l.finding))) : new Map();

    let client = deps.anthropic ?? null;
    if (!args.dryRun && !client && env.ANTHROPIC_API_KEY && plan.file.length) {
      const { default: Anthropic } = await import('@anthropic-ai/sdk');
      client = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY, maxRetries: 3, timeout: 5 * 60 * 1000 });
    }
    if (!args.dryRun && !client && plan.file.length) notes.push('ANTHROPIC_API_KEY is not set; leads are filed without the explanation paragraph.');
    const system = readFileSync(join(ROOT, PROMPT_PATH), 'utf8');

    if (write && (plan.file.length || plan.overflow.length)) await gh.ensureLabels(repo, LEAD_LABELS);
    for (const lead of plan.file) {
      const facts = explanationFacts(lead.finding, records);
      const ex = args.dryRun
        ? { text: null, note: 'Dry run: no model call, so no explanation paragraph.' }
        : client ? await explain(client, usage, { system, facts, log }) : { text: null, note: 'No explanation: ANTHROPIC_API_KEY is not set.' };
      const issue = renderLead(lead, { records, release: currentId, previous: previousId, explanation: ex.text, explanationNote: ex.note, runUrl: args.runUrl });
      const entry = { id: lead.finding.id, reason: lead.reason, title: issue.title, issue, explanationNote: ex.note, facts };
      if (write) entry.url = (await gh.createIssue(repo, issue)).html_url;
      filed.push(entry);
    }
    if (plan.overflow.length) {
      const issue = renderOverflow(plan.overflow, { records, release: currentId, previous: previousId, filedCount: plan.file.length, runUrl: args.runUrl });
      const entry = { id: 'overflow', reason: 'overflow', title: issue.title, issue };
      if (write) entry.url = (await gh.createIssue(repo, issue)).html_url;
      filed.push(entry);
    }
    for (const c of plan.comments) {
      const entry = { ...c };
      if (!args.dryRun) {
        const existing = await gh.commentBodies(repo, c.number);
        if (existing.some((b) => b.includes(c.marker))) entry.status = 'already posted';
        else if (write) {
          await gh.comment(repo, c.number, c.body);
          entry.status = 'posted';
        } else entry.status = 'would post';
      } else entry.status = 'would post';
      comments.push(entry);
    }
  } finally {
    const summary = renderSummary({ mode, previous: previousId, current: currentId, diff, plan, filed, comments, notes, usage });
    emit(summary);
    if (args.out) {
      mkdirSync(args.out, { recursive: true });
      writeFileSync(join(args.out, 'summary.md'), summary);
      writeFileSync(join(args.out, 'plan.json'), `${JSON.stringify({ previous: previousId, current: currentId, filed: filed.map(({ facts, ...f }) => f), comments, skipped: plan.skipped }, null, 2)}\n`);
      for (const [i, f] of filed.entries()) writeFileSync(join(args.out, `${i + 1}-${f.id}.md`), `# ${f.issue.title}\n\nLabels: ${f.issue.labels.join(', ')}; assignee: ${f.issue.assignees.join(', ')}\n\n${f.issue.body}\n`);
      for (const [i, c] of comments.entries()) writeFileSync(join(args.out, `comment-${i + 1}-issue-${c.number}.md`), `${c.body}\n`);
      writeFileSync(join(args.out, 'usage.json'), `${JSON.stringify({ byModel: usage.byModel, estimatedUsd: usage.total() }, null, 2)}\n`);
    }
    log(`Estimated cost of this run: $${usage.total().toFixed(4)}`);
  }
  const summary = renderSummary({ mode, previous: previousId, current: currentId, diff, plan, filed, comments, notes, usage });
  return { summary, diff, plan, filed, comments, usage };
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  main().catch((e) => {
    console.error(e);
    process.exit(1);
  });
}
