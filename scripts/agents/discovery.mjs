// Daily discovery scan (rewire-benchmark-data #254). Finds AI-for-biology models, methods,
// benchmarks and datasets that the database does not hold yet, checks them against primary
// sources, and files a data issue here and an article issue in rewire.it for each one.
//
// "New" means new to the database. The scan looks first at the last 30 days of releases, and
// an older resource is still a candidate when the database lacks it. Release age never drops
// a candidate; it only decides which candidates are judged first.
//
// The model only searches, reads and writes notes. This script owns everything that must be
// exact: deduplication against issues, the record store and published articles; the depth
// tier and labels; the issue bodies; and every GitHub write. The prompt is agents/discovery.md.
//
//   node scripts/agents/discovery.mjs --dry-run [--fixtures <dir>] [--out <dir>]
//   node scripts/agents/discovery.mjs [--report-only] [--max-pairs 4] [--lookback-days 30] [--out <dir>] [--state <file>]
//
// --dry-run   reads candidates, issues, store names and articles from fixtures; no model
//             call, no network, no write. CI runs it through tests/agents-discovery.test.ts.
// --report-only  calls the models and reads GitHub, but prints the issues instead of filing.
// --state     a JSON file of candidates the judge rejected. They are not judged again until
//             the lookback period has passed. The workflow keeps the file in the Actions cache.
//
// Environment: ANTHROPIC_API_KEY (live only; when empty the run writes a notice and exits 0),
// GH_TOKEN or GITHUB_TOKEN for this repository, ARTICLE_TOKEN for rewire.it (optional; without
// it the article request goes into the data issue), GITHUB_REPOSITORY, GITHUB_STEP_SUMMARY.
//
// The Anthropic SDK is imported only in live mode, so tests and dry runs need no install.

import { createReadStream, existsSync, mkdirSync, readFileSync, appendFileSync, writeFileSync } from 'node:fs';
import { createInterface } from 'node:readline';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../..');

/** The record store's repository when GITHUB_REPOSITORY is unset (local runs). Workflows always set it. One constant for every agent, so the store rebuild changes it in one place. */
export const DEFAULT_REPO = 'rewire-bio/rewire-benchmark-data';
export const ARTICLE_REPO = 'rewire-bio/rewire.it';
export const PROMPT_PATH = 'agents/discovery.md';
export const FIXTURES = 'tests/agents-discovery-fixtures';

// Models and limits. Haiku runs the scan and turns notes into structured fields; Sonnet judges
// each candidate against its primary sources. DISCOVERY_SCAN_MODEL overrides the scan model.
export const MODELS = { scan: 'claude-haiku-5-5', judge: 'claude-sonnet-5-5', triage: 'claude-haiku-5-5' };
// Worst case per research call is (1 + maxContinuations) requests, each holding every page
// fetched so far. researchTurn counts searches and fetches across resumes, so the allowances
// below hold for the whole call. docs/agents.md derives the cost bounds from these numbers.
//
// Scan budget: about $0.35 a run. Search fees are nearly all of it ($0.01 each); the three
// scheduled runs of 18 to 20 November 2026 cost $0.10 to $0.12 for 9 or 10 searches, of which
// tokens were about $0.01. Three lanes of 8 searches are 24 searches, about $0.24 to $0.30.
export const LIMITS = {
  maxPairs: 4, // issue pairs filed per run
  maxJudged: 6, // candidates sent to the judge per run
  maxRunUsd: 1, // no further candidate is judged once the run's estimated cost passes this
  maxContinuations: 2, // pause_turn resumes per research call
  maxTokens: 16000, // structuring calls
  researchMaxTokens: 10000, // scan and judge calls: notes plus thinking
  scanSearches: 8, // per scan lane
  scanFetches: 2, // per scan lane
  scanCandidates: 6, // per scan lane
  maxScanUsd: 0.35, // no further lane starts when the scan would pass this
  scanLaneUsd: 0.1, // measured cost of one lane, used for that check
  knownTitles: 60, // request titles shown to the scan so it does not return them
  judgeSearches: 3,
  judgeFetches: 4,
  fetchContentTokens: 15000,
};

// USD per million tokens and per web search, from the Claude pricing page on 2026-11-17.
// Haiku 5.5 costs more for a request whose prompt is over 100,000 tokens; Usage prices those
// requests under the second key.
export const PRICES = {
  'claude-sonnet-5-5': { input: 2, output: 10, cacheWrite: 2.5, cacheRead: 0.1 },
  'claude-haiku-5-5': { input: 0.1, output: 0.5, cacheWrite: 0.125, cacheRead: 0.01 },
  'claude-haiku-5-5 (prompt over 100k)': { input: 0.5, output: 2.5, cacheWrite: 0.625, cacheRead: 0.05 },
  // Possible refusal fallbacks for Sonnet 5.5. A model not listed is priced as Opus 5.5.
  'claude-sonnet-5': { input: 2, output: 10, cacheWrite: 2.5, cacheRead: 0.2 },
  'claude-opus-5-5': { input: 4, output: 20, cacheWrite: 5, cacheRead: 0.2 },
  webSearch: 10 / 1000,
};

// Areas (data/vocab/area.ttl) and the depth-tier rule (docs/tiers.md, shared/omics/depth-tier.ts).
// tests/agents-discovery.test.ts checks these lists against both files.
export const AREAS = [
  'biological-networks', 'cells-tissues', 'dna-genomes', 'glycans', 'lipidomics', 'mechanistic-biology',
  'metabolomics', 'microbes-communities', 'molecular-interactions', 'protein-function', 'protein-structure',
  'proteins-complexes', 'rna-transcriptomes', 'single-cell', 'spatial-omics',
];
export const GENOMIC_AREAS = ['dna-genomes', 'rna-transcriptomes'];
export const PROTEIN_AREAS = ['proteins-complexes', 'protein-function', 'protein-structure'];
export const KINDS = ['model', 'method', 'benchmark', 'dataset'];
// One scan call per lane. A single call with every search in it wandered, and its prompt
// passed 100,000 tokens, where Haiku costs five times as much. The first lane each day rotates.
export const SCAN_LANES = [
  { name: 'genomics', focus: 'DNA and RNA: genomic and transcriptomic sequence models, variant effect and regulatory prediction, RNA structure and function, and the benchmarks and datasets that evaluate them' },
  { name: 'proteins', focus: 'proteins: structure prediction, protein and antibody design, function and fitness prediction, protein language models, protein interactions, and the benchmarks and datasets that evaluate them' },
  { name: 'cells and other biology', focus: 'single-cell and spatial models, perturbation prediction, molecular interactions and small molecules in a biological setting, microbes, metabolomics, biological networks, scientific agents for biology, and the benchmarks and datasets that evaluate them' },
];
const STORE_FILES = ['models', 'methods', 'benchmarks', 'datasets', 'pipelines', 'services'];
const PRIMARY_ROLES = new Set(['paper', 'preprint', 'repository', 'model_card', 'dataset_card']);

export const LABELS = {
  'entity-request': { color: '1d76db', description: 'A new record for the intake agent' },
  'tier-1': { color: '0e8a16', description: 'Depth tier 1: DNA and RNA genomics, full records' },
  'tier-2': { color: 'fbca04', description: 'Depth tier 2: proteins, full records' },
  'tier-3': { color: 'c5def5', description: 'Depth tier 3: everything else, metadata only' },
  article: { color: '5319e7', description: 'Article request for the writer agent' },
  // Filed by the disagreement watcher (watcher.mjs).
  lead: { color: 'd93f0b', description: 'A discrepancy between studies to investigate' },
  'needs-tim': { color: 'b60205', description: 'Needs a decision or action from Tim' },
  // Filed by the monthly entity sweep (sweep.mjs). entity-update starts the intake agent.
  'entity-update': { color: '1d76db', description: 'A change to an existing record for the intake agent' },
  'entity-sweep': { color: 'c2e0c6', description: 'Dead links and other findings of the monthly entity sweep' },
};

const TIER_SCOPE = {
  1: 'Tier 1 (DNA and RNA genomics): full records, evaluations, and relevance judgements to the use cases that rely on it.',
  2: 'Tier 2 (proteins): full records.',
  3: 'Tier 3 (outside genomics and proteins): a metadata-only record. Do not extract evaluations or results.',
};

/** Depth tier from areas: any genomic area is 1, else any protein area is 2, else 3. */
export function tierOf(areas = []) {
  if (areas.some((a) => GENOMIC_AREAS.includes(a))) return 1;
  if (areas.some((a) => PROTEIN_AREAS.includes(a))) return 2;
  return 3;
}

export function dataLabels(tier) {
  return ['entity-request', `tier-${tier}`];
}

/** Lower case, with every run of non-alphanumerics collapsed to one space. */
export function normalise(text) {
  return String(text ?? '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
}

export function keyOf(name) {
  return normalise(name).replace(/ /g, '-');
}

/**
 * The form names are compared in. Like normalise, but accents are dropped ("Proteína" equals
 * "Proteina") and a letter next to a digit is split ("BioEmu2" equals "BioEmu-2"). Keys and
 * markers keep using normalise, so a marker already written stays valid.
 */
export function matchForm(text) {
  return normalise(String(text ?? '').normalize('NFKD').replace(/[\u0300-\u036f]/g, ''))
    .replace(/([a-z])(?=\d)|(\d)(?=[a-z])/g, '$1$2 ');
}

/** A name long enough to compare: three characters or more, not counting the spaces matchForm adds ("v3" is not). */
function longEnough(form) {
  return form.replace(/ /g, '').length >= 3;
}

/**
 * A name with its spelling differences removed: matchForm without the spaces, without a "v"
 * before a version number and without a trailing ".0". "Torch Craft", "Alpha Genome", "Splice AI",
 * "Enchant-3" and "BioEmu 2.0" equal "TorchCraft", "AlphaGenome", "SpliceAI", "Enchant v3" and
 * "BioEmu-2". A different version number is a different name: "ESM3" does not equal "ESM-2".
 */
export function spellForm(text) {
  return squash(matchForm(text));
}

function squash(form) {
  return form.replace(/(^| )v (?=\d)/g, '$1').replace(/(\d) 0(?= |$)/g, '$1').replace(/ /g, '');
}

/** Long enough to compare as a spelling: four characters or more. */
function spelled(spelling) {
  return spelling.length >= 4;
}

/**
 * True when the text holds the name in another spelling. A word of the text is what stands
 * between two spaces, so "HyPLM-Flash" is one word and spells "HyPLMFlash". A version after
 * the word counts as part of it ("Enchant v3" spells "Enchant-3"). Two separate words do not
 * make a name: "the tier rule" does not spell "TierRule".
 */
function spells(text, spelling) {
  const words = String(text ?? '').split(/\s+/).map(spellForm).filter(Boolean);
  for (let i = 0; i < words.length; i++) {
    let run = words[i];
    if (run === spelling) return true;
    for (let j = i + 1; j < words.length && /^\d+$/.test(words[j]) && run.length < spelling.length; j++) {
      run += words[j];
      if (run === spelling) return true;
    }
  }
  return false;
}

/** A name without its trailing version or size ("ESM-2 650M" and "ESM3" give "esm"), in spellForm. */
function baseOf(text) {
  const words = matchForm(text).split(' ');
  while (words.length > 1 && /^(\d+|v|[mbk])$/.test(words.at(-1))) words.pop();
  return words.join('');
}

// Store maps are built once per run; these indexes are derived from them once.
const storeIndexes = new WeakMap();
function storeIndex(storeNames) {
  let index = storeIndexes.get(storeNames);
  if (!index) {
    index = { spelling: new Map(), base: new Map() };
    for (const [form, id] of storeNames) {
      const spelling = squash(form);
      if (spelled(spelling) && !index.spelling.has(spelling)) index.spelling.set(spelling, { form, id });
      const base = baseOf(form);
      if (base.length >= 3) index.base.set(base, [...(index.base.get(base) ?? []), { form, id }]);
    }
    storeIndexes.set(storeNames, index);
  }
  return index;
}

const MARKER = /<!-- discovery-key: ([a-z0-9-]+) -->/g;

/** Keys of issues this script filed. */
export function markersIn(body) {
  return [...String(body ?? '').matchAll(MARKER)].map((m) => m[1]);
}

/** Stable identifiers in a candidate's primary sources: DOIs, arXiv IDs, GitHub and Hugging Face repos. */
export function identifiersOf(candidate) {
  const ids = new Set();
  for (const source of candidate.sources ?? []) {
    if (!PRIMARY_ROLES.has(source.role)) continue;
    const url = String(source.url ?? '').toLowerCase();
    // bioRxiv-style DOIs: drop a trailing .full, .full.pdf or .pdf, then the version.
    const doi = /10\.\d{4,9}\/[^\s?#]+/.exec(url)?.[0]
      ?.replace(/[./]+$/, '').replace(/(\.full)?(\.pdf)?$/, '').replace(/v\d+$/, '');
    if (doi) ids.add(doi);
    // The bare arXiv ID, so abs, pdf and html links all match.
    const arxiv = /arxiv\.org\/(?:abs|pdf|html)\/(\d{4}\.\d{4,5})/.exec(url)?.[1];
    if (arxiv) ids.add(arxiv);
    const gh = /github\.com\/([\w.-]+\/[\w.-]+)/.exec(url)?.[1]?.replace(/\.git$/, '');
    if (gh) ids.add(`github.com/${gh}`);
    const hf = /huggingface\.co\/(?:datasets\/)?([\w.-]+\/[\w.-]+)/.exec(url)?.[1];
    if (hf) ids.add(`huggingface.co/${hf}`);
  }
  return [...ids];
}

function namesOf(candidate) {
  return [...new Set([candidate.name, ...(candidate.aliases ?? [])].map(matchForm))].filter(longEnough);
}

function mentions(text, name) {
  return ` ${matchForm(text)} `.includes(` ${name} `);
}

/**
 * Where a candidate is already known, or null. Checks, in order: a discovery marker; a name or
 * alias in an issue title (issues filed by hand or by the old automation have no marker, so
 * the title is all there is to match); a primary identifier in an issue body; a name in the
 * record store. Names are compared in matchForm, whoever filed the issue.
 */
export function findDuplicate(candidate, { issues = [], storeNames = new Map(), articles = [] }) {
  const key = keyOf(candidate.name);
  const names = namesOf(candidate);
  const spellings = [...new Set(names.map(squash))].filter(spelled);
  const ids = identifiersOf(candidate);
  for (const issue of issues) {
    const ref = `${issue.repo}#${issue.number}`;
    if (markersIn(issue.body).includes(key)) return { where: 'issue', ref, url: issue.html_url, reason: `filed before as ${ref}` };
    const name = names.find((n) => mentions(issue.title, n));
    if (name) return { where: 'issue', ref, url: issue.html_url, reason: `"${name}" is in the title of ${ref}` };
    const spelling = spellings.find((n) => spells(issue.title, n));
    if (spelling) return { where: 'issue', ref, url: issue.html_url, reason: `"${spelling}" is in the title of ${ref} under another spelling` };
    const body = String(issue.body ?? '').toLowerCase();
    const id = ids.find((i) => body.includes(i));
    if (id) return { where: 'issue', ref, url: issue.html_url, reason: `${id} is cited in ${ref}` };
  }
  // The store map is keyed by matchForm here and by normalise when another agent built it.
  for (const raw of [candidate.name, ...(candidate.aliases ?? [])]) {
    const n = [matchForm(raw), normalise(raw)].find((form) => longEnough(form) && storeNames.has(form));
    if (n) return { where: 'store', ref: storeNames.get(n), reason: `"${n}" matches store record ${storeNames.get(n)}` };
  }
  if (storeNames.size) {
    const index = storeIndex(storeNames).spelling;
    const spelling = spellings.find((n) => index.has(n));
    if (spelling) return { where: 'store', ref: index.get(spelling).id, reason: `"${spelling}" matches store record ${index.get(spelling).id} ("${index.get(spelling).form}") under another spelling` };
  }
  return null;
}

/**
 * Records and requests whose name differs from the candidate's only by a version or size
 * ("ESM-2 650M" and "ESM-2", "BioEmu-3" and "BioEmu-2"). These are not duplicates: a new version
 * is a resource of its own. They are given to the judge, which decides.
 */
export function nearMatches(candidate, { issues = [], storeNames = new Map() }, limit = 5) {
  const bases = [...new Set([candidate.name, ...(candidate.aliases ?? [])].map(baseOf))].filter((b) => b.length >= 3);
  const out = [];
  const index = storeNames.size ? storeIndex(storeNames).base : new Map();
  for (const base of bases) for (const { form, id } of index.get(base) ?? []) out.push(`store record ${id} ("${form}")`);
  for (const issue of issues) {
    const words = String(issue.title ?? '').split(/\s+/).map(baseOf);
    if (bases.some((b) => words.includes(b))) out.push(`${issue.repo}#${issue.number}: ${clean(issue.title)}`);
  }
  return [...new Set(out)].slice(0, limit);
}

/** The last FILE or SKIP in the judge's notes, or null when the notes give neither in capitals. */
export function verdictOf(notes) {
  return [...String(notes ?? '').matchAll(/\b(FILE|SKIP)\b/g)].at(-1)?.[1] ?? null;
}

// ---------- Rejected candidates ----------

/**
 * Candidates the judge rejected, read from the state file. A missing file is an empty list. An
 * unreadable one is too, with a note: the cost of that is judging a candidate again.
 */
export function readRejected(path, notes = []) {
  if (!path || !existsSync(path)) return [];
  try {
    const list = JSON.parse(readFileSync(path, 'utf8')).rejected;
    if (!Array.isArray(list)) throw new Error('no "rejected" list');
    return list.filter((r) => r && Array.isArray(r.names) && typeof r.date === 'string');
  } catch (e) {
    notes.push(`The rejected-candidate file could not be read (${errorText(e)}); candidates rejected before may be judged again.`);
    return [];
  }
}

/** The rejection that still covers this candidate, or null. A rejection lapses after `days`. */
export function findRejected(candidate, rejected, runDate, days) {
  const names = namesOf(candidate);
  for (const r of rejected) {
    const age = ageInDays(r.date, runDate);
    if (age === null || age < 0 || age >= days) continue;
    if (!names.some((n) => r.names.includes(n))) continue;
    const until = new Date(Date.parse(`${r.date}T00:00:00Z`) + days * 86_400_000).toISOString().slice(0, 10);
    return { where: 'rejected', ref: r.name, reason: `the judge rejected it on ${r.date} (${clean(r.reason) || 'no reason recorded'}); it can be judged again from ${until}` };
  }
  return null;
}

/** A published article that covers the candidate, or null. */
export function findArticle(candidate, articles = []) {
  const names = namesOf(candidate);
  for (const article of articles) {
    const slug = String(article.url ?? '').split('/').filter(Boolean).pop() ?? '';
    const name = names.find((n) => mentions(article.title, n) || mentions(slug, n));
    if (name) return article;
  }
  return null;
}

/**
 * Names (and reported names) of every record of the kinds discovery can add, by streaming the
 * store files. `form` is how a name becomes a key: normalise for the other agents, matchForm here.
 */
export async function readStoreNames(dir = join(ROOT, 'data/entities'), form = normalise) {
  const names = new Map();
  for (const kind of STORE_FILES) {
    const file = join(dir, `${kind}.jsonl`);
    if (!existsSync(file)) continue;
    const lines = createInterface({ input: createReadStream(file), crlfDelay: Infinity });
    for await (const line of lines) {
      if (!line.trim()) continue;
      const record = JSON.parse(line);
      for (const name of [record.name, record.attributes?.reported_name]) {
        const n = form(name);
        if (longEnough(n) && !names.has(n)) names.set(n, record.id);
      }
    }
  }
  return names;
}

/**
 * Model text goes into public issues. Remove @-mentions (they would notify people), HTML
 * comments (they could fake a discovery marker) and em and en dashes (house style).
 */
export function clean(text) {
  return String(text ?? '')
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/(^|[^\w`])@(?=[A-Za-z0-9])/g, '$1')
    .replace(/\s*\u2014\s*/g, ', ')
    .replace(/\u2013/g, '-')
    .trim();
}

function bullets(items) {
  const list = (items ?? []).map(clean).filter(Boolean);
  return list.length ? list.map((i) => `- ${i}`).join('\n') : '- None recorded.';
}

function sourceLines(candidate) {
  return bullets((candidate.sources ?? []).map((s) =>
    `${s.title ? `${s.title}: ` : ''}${s.url} (${s.role ?? 'source'}; ${s.retrieved_at ? `retrieved ${s.retrieved_at}` : 'seen in search results, not opened'})`));
}

function announcementLine(candidate) {
  const a = candidate.announcement;
  if (!a?.url) return 'Original announcement: none found.';
  return `Original announcement: ${clean(a.author) || 'author not recorded'}, ${a.url}`;
}

function licenceLines(candidate) {
  const l = candidate.licence ?? {};
  return bullets([`Code: ${l.code || 'not verified'}`, `Weights: ${l.weights || 'not verified'}`, `Data: ${l.data || 'not verified'}`]);
}

function articleSection(candidate, heading) {
  const a = candidate.article ?? {};
  return [
    heading,
    '',
    `Working title: ${clean(a.title) || clean(candidate.name)}`,
    '',
    `Editorial angle: ${clean(a.angle) || 'to be set by the writer.'}`,
    '',
    'Explain the scientific task, inputs and outputs, useful capabilities, evidence, baselines, access and licensing, and limitations in plain language for AI researchers and practitioners.',
    '',
    `After reading, a reader should be able to: ${clean(a.reader_outcome) || 'explain what the resource does and when to use it.'}`,
    '',
    'Unresolved fact-checks:',
    '',
    bullets(a.fact_checks),
    '',
    'Acceptance: a substantive sourced article through the blog-write-post workflow (research dossier, fact verification, drafting, independent review, explanatory assets). Do not describe author-reported results as independently reproduced or invent experiments. Filing this request does not mean an article has been written; publication needs the separate blog-publish approval.',
  ].join('\n');
}

/** The data issue: always labelled entity-request and its tier. */
export function renderDataIssue(candidate, { tier, runDate, article, existingArticle, dedupNote }) {
  const kind = KINDS.includes(candidate.kind) ? candidate.kind : 'resource';
  const title = `Add discovered ${kind} ${clean(candidate.name)}: ${clean(candidate.task_short || candidate.task)}`.slice(0, 200);
  const counterpart = article?.url
    ? `Counterpart article issue: ${article.url}`
    : existingArticle
      ? `Existing article: ${existingArticle.url}. No new article issue was filed.`
      : article?.inline
        ? 'Counterpart article issue: not filed, because this run had no access to rewire.it. The request is at the end of this issue; copy it there.'
        : 'Counterpart article issue: pending.';
  const body = [
    counterpart,
    '',
    `Request a source-backed \`discovered\` ${kind} record for **${clean(candidate.name)}**${candidate.version ? ` (${clean(candidate.version)})` : ''}${candidate.release_date ? `, released ${clean(candidate.release_date)}` : ''}.`,
    candidate.aliases?.length ? `Aliases: ${candidate.aliases.map(clean).join(', ')}.` : '',
    candidate.existing_name ? `Related record already known: ${clean(candidate.existing_name)}. ${clean(candidate.existing_note)}` : '',
    '',
    `**Scope.** ${TIER_SCOPE[tier]} Suggested areas: ${(candidate.areas ?? []).join(', ') || 'none given'}.`,
    '',
    `**Task.** ${clean(candidate.task)}`,
    '',
    `Inputs: ${clean(candidate.inputs) || 'not recorded'}. Outputs: ${clean(candidate.outputs) || 'not recorded'}.`,
    '',
    '**Evidence the authors report.** Not independently reproduced.',
    '',
    clean(candidate.evidence) || 'Not recorded.',
    '',
    '**Limitations and access gaps.**',
    '',
    bullets(candidate.limitations),
    '',
    '**Licence and access.**',
    '',
    licenceLines(candidate),
    '',
    '**Primary sources.**',
    '',
    sourceLines(candidate),
    '',
    announcementLine(candidate),
    '',
    '**Open fact-checks.**',
    '',
    bullets(candidate.open_questions),
    '',
    `**Acceptance.** Deduplicate against existing records; add only grounded metadata with exact source locators and keep unknown fields empty with a reason. Follow docs/collection.md and the literature-search, extract-evaluations and review-evidence skills; pin retrieved sources. Give the record its depth tier (${tier}). Obtain an independent review before a data PR. Filing this issue does not authorise merging or a release.`,
    '',
    `**Deduplication (${runDate}).** ${dedupNote}`,
    '',
    article?.inline ? `${articleSection(candidate, '## Article request')}\n` : '',
    `Filed by the discovery scan (\`.github/workflows/discovery.yml\`, prompt \`${PROMPT_PATH}\`). Indexing a resource is not an evaluation or endorsement of it.`,
    '',
    `<!-- discovery-key: ${keyOf(candidate.name)} -->`,
  ];
  return { title, body: body.filter((line, i, all) => !(line === '' && all[i - 1] === '')).join('\n'), labels: dataLabels(tier) };
}

/** The article issue in rewire.it: labelled article, whatever the tier. */
export function renderArticleIssue(candidate, { dataUrl, runDate, dedupNote }) {
  const title = `Research ${clean(candidate.name)}: ${clean(candidate.article?.title) || clean(candidate.task_short || candidate.task)}`.slice(0, 200);
  const body = [
    `Counterpart database issue: ${dataUrl}`,
    '',
    articleSection(candidate, '## Article request'),
    '',
    '**Primary sources.**',
    '',
    sourceLines(candidate),
    '',
    announcementLine(candidate),
    '',
    `**Deduplication (${runDate}).** ${dedupNote}`,
    '',
    `Filed by the discovery scan in rewire-benchmark-data (prompt \`${PROMPT_PATH}\`).`,
    '',
    `<!-- discovery-key: ${keyOf(candidate.name)} -->`,
  ].join('\n');
  return { title, body, labels: ['article'] };
}

/**
 * Decide what to file. Candidates the judge rejected, duplicates of issues or store records,
 * and repeats within the run are skipped with a reason. At most maxPairs are filed in a day:
 * `filedToday` is how many this script already filed on the run date.
 */
export function planFiling(candidates, { issues, storeNames, articles, articleAccess, runDate, maxPairs = LIMITS.maxPairs, filedToday = 0 }) {
  const file = [];
  const skipped = [];
  const seen = [];
  const checked = `Checked ${issues.length} open and closed issues${articleAccess ? ' in rewire-benchmark-data and rewire.it' : ' in rewire-benchmark-data (rewire.it was not readable)'}, ${storeNames.size} record-store names and ${articles.length} published articles.`;
  for (const candidate of candidates) {
    if (candidate.decision && candidate.decision !== 'file') {
      skipped.push({ name: candidate.name, reason: `judge: ${clean(candidate.skip_reason) || 'not worthwhile'}` });
      continue;
    }
    if (!candidate.name || !candidate.task || !(candidate.sources ?? []).some((s) => s.retrieved_at)) {
      skipped.push({ name: candidate.name ?? '(no name)', reason: 'no name, task or retrieved primary source' });
      continue;
    }
    const dup = findDuplicate(candidate, { issues, storeNames });
    if (dup) {
      skipped.push({ name: candidate.name, reason: dup.reason });
      continue;
    }
    const repeat = seen.find((c) => findDuplicate(candidate, { issues: [{ repo: 'this run', number: 0, title: c.name, body: c.marker }] }));
    if (repeat) {
      skipped.push({ name: candidate.name, reason: `repeats ${repeat.name} in this run` });
      continue;
    }
    if (file.length + filedToday >= maxPairs) {
      skipped.push({ name: candidate.name, reason: filedToday
        ? `over the daily cap of ${maxPairs} (${filedToday} already filed today); the next run picks it up`
        : `over the per-run cap of ${maxPairs}; the next run picks it up` });
      continue;
    }
    seen.push({ name: candidate.name, marker: `<!-- discovery-key: ${keyOf(candidate.name)} --> ${identifiersOf(candidate).join(' ')}` });
    const tier = tierOf(candidate.areas);
    const existingArticle = findArticle(candidate, articles);
    file.push({ candidate, tier, existingArticle, dedupNote: `${checked} No match for ${[candidate.name, ...(candidate.aliases ?? [])].map(clean).join(', ')} or its primary identifiers.` });
  }
  return { file, skipped };
}

// ---------- Usage and cost ----------

export class Usage {
  constructor() {
    this.byModel = {};
    this.calls = 0;
  }
  /** `assumed` is the tool use to count when the response does not report any (researchTurn). */
  add(model, usage, assumed) {
    if (!usage) return;
    this.calls += 1;
    const prompt = (usage.input_tokens ?? 0) + (usage.cache_creation_input_tokens ?? 0) + (usage.cache_read_input_tokens ?? 0);
    if (model === 'claude-haiku-5-5' && prompt > 100_000) model = 'claude-haiku-5-5 (prompt over 100k)';
    const m = (this.byModel[model] ??= { input: 0, output: 0, cacheWrite: 0, cacheRead: 0, webSearches: 0, webFetches: 0 });
    m.input += usage.input_tokens ?? 0;
    m.output += usage.output_tokens ?? 0;
    m.cacheWrite += usage.cache_creation_input_tokens ?? 0;
    m.cacheRead += usage.cache_read_input_tokens ?? 0;
    const tools = usage.server_tool_use ?? assumed;
    m.webSearches += tools?.web_search_requests ?? 0;
    m.webFetches += tools?.web_fetch_requests ?? 0;
  }
  costOf(model) {
    const m = this.byModel[model];
    const p = PRICES[model] ?? PRICES['claude-opus-5-5'];
    if (!m) return 0;
    return (m.input * p.input + m.output * p.output + m.cacheWrite * p.cacheWrite + m.cacheRead * p.cacheRead) / 1e6 + m.webSearches * PRICES.webSearch;
  }
  total() {
    return Object.keys(this.byModel).reduce((sum, model) => sum + this.costOf(model), 0);
  }
  table() {
    const rows = Object.entries(this.byModel).map(([model, m]) =>
      `| ${model} | ${m.input} | ${m.cacheWrite} | ${m.cacheRead} | ${m.output} | ${m.webSearches} | ${m.webFetches} | $${this.costOf(model).toFixed(4)} |`);
    if (!rows.length) return 'No model calls.';
    return [
      '| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |',
      '| --- | --- | --- | --- | --- | --- | --- | --- |',
      ...rows,
      `| Total | | | | | | | $${this.total().toFixed(4)} |`,
    ].join('\n');
  }
}

export function renderSummary({ mode, runDate, usage, filed, skipped, notes = [] }) {
  return [
    `## Discovery scan, ${runDate} (${mode})`,
    '',
    ...notes.map((n) => `- ${n}`),
    notes.length ? '' : null,
    '### Filed',
    '',
    filed.length
      ? filed.map((f) => `- tier ${f.tier}, ${f.labels.join(', ')}: ${f.dataUrl ?? '(not filed)'} ${f.title}${f.articleUrl ? `; article ${f.articleUrl}` : f.articleNote ? `; ${f.articleNote}` : ''}`).join('\n')
      : 'Nothing filed.',
    '',
    '### Skipped',
    '',
    skipped.length ? skipped.map((s) => `- ${s.name}: ${s.reason}`).join('\n') : 'Nothing skipped.',
    '',
    '### Token usage',
    '',
    usage.table(),
    '',
  ].filter((l) => l !== null).join('\n');
}

// ---------- GitHub ----------

export function githubClient(token, fetchImpl = fetch) {
  async function call(method, path, body) {
    const res = await fetchImpl(`https://api.github.com${path}`, {
      method,
      headers: { authorization: `Bearer ${token}`, accept: 'application/vnd.github+json', 'x-github-api-version': '2022-11-28', 'user-agent': 'rewire-discovery' },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) {
      const err = new Error(`${method} ${path}: ${res.status} ${await res.text()}`);
      err.status = res.status;
      throw err;
    }
    return { data: res.status === 204 ? null : await res.json(), link: res.headers.get('link') ?? '' };
  }
  return {
    async listIssues(repo) {
      const out = [];
      for (let page = 1; page < 50; page++) {
        const { data, link } = await call('GET', `/repos/${repo}/issues?state=all&per_page=100&page=${page}`);
        for (const i of data) {
          if (i.pull_request) continue;
          out.push({ repo, number: i.number, title: i.title, body: i.body ?? '', html_url: i.html_url, state: i.state, labels: (i.labels ?? []).map((l) => l.name ?? l), created_at: i.created_at, user: i.user?.login });
        }
        if (!link.includes('rel="next"')) break;
      }
      return out;
    },
    async ensureLabels(repo, names) {
      for (const name of names) {
        try {
          await call('GET', `/repos/${repo}/labels/${encodeURIComponent(name)}`);
        } catch (e) {
          if (e.status !== 404) throw e;
          await call('POST', `/repos/${repo}/labels`, { name, ...LABELS[name] });
        }
      }
    },
    async createIssue(repo, issue) {
      return (await call('POST', `/repos/${repo}/issues`, issue)).data;
    },
    async updateIssue(repo, number, patch) {
      return (await call('PATCH', `/repos/${repo}/issues/${number}`, patch)).data;
    },
  };
}

/** Published articles from the blog index: every /blog/<slug>/ link and its text. */
export function parseBlogIndex(html, base = 'https://rewirebio.io') {
  const out = new Map();
  for (const m of String(html).matchAll(/<a[^>]+href="((?:https:\/\/rewirebio\.io)?\/blog\/[a-z0-9-]+\/?)"[^>]*>([\s\S]*?)<\/a>/g)) {
    const url = new URL(m[1], base).href;
    const title = m[2].replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    if (!out.has(url) || (title && !out.get(url).title)) out.set(url, { url, title });
  }
  return [...out.values()];
}

// ---------- Model calls (live only) ----------

const SCAN_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['candidates'],
  properties: {
    candidates: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['name', 'aliases', 'kind', 'released', 'summary', 'urls', 'in_scope', 'reason'],
        properties: {
          name: { type: 'string' },
          aliases: { type: 'array', items: { type: 'string' } },
          kind: { type: 'string', enum: KINDS },
          released: { type: 'string', description: 'Release date as YYYY-MM-DD or YYYY-MM; empty when the notes do not give one' },
          summary: { type: 'string' },
          urls: { type: 'array', items: { type: 'string' } },
          in_scope: { type: 'boolean' },
          reason: { type: 'string' },
        },
      },
    },
  },
};

const SOURCE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['url', 'title', 'role', 'retrieved_at'],
  properties: {
    url: { type: 'string' },
    title: { type: 'string' },
    role: { type: 'string', enum: ['paper', 'preprint', 'repository', 'model_card', 'dataset_card', 'documentation', 'announcement', 'other'] },
    retrieved_at: { type: 'string', description: 'YYYY-MM-DD when opened; empty when only seen in search results' },
  },
};

const STR = { type: 'string' };
const STRS = { type: 'array', items: STR };
export const JUDGEMENT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['decision', 'skip_reason', 'name', 'aliases', 'kind', 'version', 'release_date', 'task', 'task_short', 'inputs', 'outputs', 'areas', 'evidence', 'limitations', 'licence', 'sources', 'announcement', 'existing_name', 'existing_note', 'open_questions', 'article'],
  properties: {
    decision: { type: 'string', enum: ['file', 'skip'] },
    skip_reason: STR,
    name: STR,
    aliases: STRS,
    kind: { type: 'string', enum: KINDS },
    version: STR,
    release_date: STR,
    task: STR,
    task_short: { type: 'string', description: 'Under 80 characters, for the issue title' },
    inputs: STR,
    outputs: STR,
    areas: { type: 'array', items: { type: 'string', enum: AREAS } },
    evidence: STR,
    limitations: STRS,
    licence: { type: 'object', additionalProperties: false, required: ['code', 'weights', 'data'], properties: { code: STR, weights: STR, data: STR } },
    sources: { type: 'array', items: SOURCE_SCHEMA },
    announcement: { type: 'object', additionalProperties: false, required: ['url', 'author'], properties: { url: STR, author: STR } },
    existing_name: STR,
    existing_note: STR,
    open_questions: STRS,
    article: { type: 'object', additionalProperties: false, required: ['title', 'angle', 'fact_checks', 'reader_outcome'], properties: { title: STR, angle: STR, fact_checks: STRS, reader_outcome: STR } },
  },
};

function textOf(message) {
  return message.content.filter((b) => b.type === 'text').map((b) => b.text).join('\n').trim();
}

/**
 * One research call with the server web tools, resuming pause_turn up to the cap. Returns the
 * notes, or null on a refusal, when the cap is reached, or when the reply was cut off at
 * max_tokens. With `partial`, a call that reaches the cap returns the text written so far, and
 * a reply cut off at max_tokens is returned as it is. The scan uses that, because every
 * candidate in its notes is still checked and judged; the judge does not, because notes without
 * their ending have no verdict. Sonnet 5.5 can decline biology
 * requests (refusal category `bio`); for Sonnet the server-side fallback re-runs a declined
 * request on a model the API picks, billed at that model's prices (usage.add reads
 * message.model). Haiku 5.5 has no server-side fallback.
 *
 * The search and fetch allowances are for the whole call. This tool version runs searches from
 * code execution, and the API does not count those against max_uses after a resume, so each
 * resume is given only what is left. A resume keeps at least one use, because the tool cannot
 * be removed from a conversation that already holds its results.
 *
 * The counts come from usage.server_tool_use. A response that does not report it is counted as
 * having used everything the request allowed, in the allowance and in the cost estimate, so a
 * missing field cannot hide searches from either dollar check.
 */
async function researchTurn(client, usage, { model, system, prompt, searches, fetches, log, partial = false }) {
  const messages = [{ role: 'user', content: prompt }];
  const fallback = model.startsWith('claude-haiku') ? {} : { betas: ['server-side-fallback-2026-07-01'], fallbacks: 'default' };
  const written = [];
  let searched = 0;
  let fetched = 0;
  for (let turn = 0; turn <= LIMITS.maxContinuations; turn++) {
    const allowed = { web_search_requests: Math.max(1, searches - searched), web_fetch_requests: Math.max(1, fetches - fetched) };
    const message = await client.beta.messages.stream({
      model,
      ...fallback,
      max_tokens: LIMITS.researchMaxTokens,
      system: [{ type: 'text', text: system, cache_control: { type: 'ephemeral' } }],
      output_config: { effort: 'medium' },
      tools: [
        { type: 'web_search_20260318', name: 'web_search', max_uses: allowed.web_search_requests },
        { type: 'web_fetch_20260209', name: 'web_fetch', max_uses: allowed.web_fetch_requests, max_content_tokens: LIMITS.fetchContentTokens },
      ],
      messages,
    }).finalMessage();
    const used = message.usage?.server_tool_use ?? allowed;
    if (!message.usage?.server_tool_use) log('the response did not report its tool use; counted as the full allowance');
    usage.add(message.model ?? model, message.usage ?? {}, allowed);
    searched += used.web_search_requests ?? 0;
    fetched += used.web_fetch_requests ?? 0;
    if (message.stop_reason === 'refusal') {
      log(`refused (${message.stop_details?.category ?? 'no category'})`);
      return null;
    }
    if (message.stop_reason === 'max_tokens' && !partial) {
      log('cut off at max_tokens');
      return null;
    }
    if (message.stop_reason !== 'pause_turn') return textOf(message);
    written.push(textOf(message));
    messages.push({ role: 'assistant', content: message.content });
  }
  log('stopped after the pause_turn cap');
  const text = written.filter(Boolean).join('\n\n');
  return partial && text ? text : null;
}

/** One Haiku call that turns notes into JSON matching a schema. Null if it cannot. */
async function structure(client, usage, { instruction, notes, schema }) {
  const message = await client.messages.create({
    model: MODELS.triage,
    max_tokens: LIMITS.maxTokens,
    output_config: { effort: 'low', format: { type: 'json_schema', schema } },
    messages: [{ role: 'user', content: `${instruction}\n\n<notes>\n${notes}\n</notes>` }],
  });
  usage.add(MODELS.triage, message.usage);
  if (message.stop_reason !== 'end_turn') return null;
  try {
    return JSON.parse(textOf(message));
  } catch {
    return null;
  }
}

function errorText(e) {
  return `${e?.status ? `${e.status} ` : ''}${String(e?.message ?? e).split('\n')[0].slice(0, 200)}`;
}

/** Days from a release date (YYYY-MM-DD or YYYY-MM) to the run date, or null when it does not parse. */
export function ageInDays(released, runDate) {
  const m = /^(\d{4})-(\d{2})(?:-(\d{2}))?/.exec(String(released ?? '').trim());
  if (!m) return null;
  const then = Date.UTC(Number(m[1]), Number(m[2]) - 1, Number(m[3] ?? 1));
  const days = Math.floor((Date.parse(`${runDate}T00:00:00Z`) - then) / 86_400_000);
  return Number.isFinite(days) ? days : null;
}

/**
 * Titles of the requests already filed here, newest first, for the scan to leave out. A
 * request is an issue this script filed (marker), one labelled entity-request, or one titled
 * "Add <Name> ..." as the old automation and the owner write them. Other issues ("Add areas
 * to the records ...", lanes, leads) are not resources and only cost tokens.
 */
export function knownTitles(issues, repo, limit = LIMITS.knownTitles) {
  return issues
    .filter((i) => i.repo === repo)
    .filter((i) => markersIn(i.body).length || (i.labels ?? []).includes('entity-request') || /^Add (discovered )?[A-Z0-9]/.test(i.title ?? ''))
    .sort((a, b) => b.number - a.number)
    .slice(0, limit)
    .map((i) => i.title);
}

/** The scan prompt for one lane. */
export function scanPrompt({ lane, runDate, lookbackDays, titles, rejected = [] }) {
  const since = new Date(Date.parse(`${runDate}T00:00:00Z`) - lookbackDays * 86_400_000).toISOString().slice(0, 10);
  return [
    `Run date: ${runDate}. Find AI-for-biology models, methods, benchmarks and datasets that the database does not hold yet.`,
    `Lane: ${lane.name}. This search covers one part of the field: ${lane.focus}.`,
    '',
    `Look first for resources released or first announced in the last ${lookbackDays} days (since ${since}). An older resource is also a candidate when it is substantive and something public happened to it in that period: a new version, a journal paper for an earlier preprint, a first release of code or weights, a new benchmark round, or new use as a baseline. Give each candidate's release date when a source states it. Never leave a candidate out for its age alone.`,
    '',
    `You have ${LIMITS.scanSearches} web searches and ${LIMITS.scanFetches} page fetches. Make each query different, and do not search for a name in the list below.`,
    `Valid areas: ${AREAS.join(', ')}.`,
    '',
    'Already requested. These are issue titles. Do not list a resource they name as a candidate, under any spelling or version, and do not write about it in your notes:',
    ...(titles.length ? titles.map((t) => `- ${t}`) : ['- (none yet)']),
    '',
    ...(rejected.length ? ['Checked in an earlier run and not filed. Do not list these either:', ...rejected.map((n) => `- ${n}`), ''] : []),
    `List each candidate with its name, aliases, type, release date, a one-paragraph summary, its primary URLs, and whether it is in scope and why. Up to ${LIMITS.scanCandidates} candidates. If you find nothing that is not already requested, say so; do not fill the list.`,
  ].join('\n');
}

/**
 * Scan, triage and judge. Dropped candidates go into `skipped` with a reason. A failed call
 * (rate limit, overload, timeout) loses only its own lane or candidate. `judged` is filled in
 * place so the caller keeps whatever finished.
 *
 * A candidate the script already knows never reaches the judge, whatever the scan wrote about
 * it: the prompt asks the scan not to return known names, and this check enforces it.
 */
async function liveCandidates(client, usage, { scanModel, system, runDate, lookbackDays, titles, rejectedNames = [], isKnown, near = () => [], checked = '', onReject = () => {}, skipped, judged, notes, log }) {
  // Scan and triage, one lane at a time. The first lane rotates by day, so a lane the budget
  // check skips one day runs first on another.
  const first = Math.floor(Date.parse(`${runDate}T00:00:00Z`) / 86_400_000) % SCAN_LANES.length;
  const lanes = SCAN_LANES.map((_, i) => SCAN_LANES[(first + i) % SCAN_LANES.length]);
  const byLane = [];
  const seen = new Map();
  let echoed = 0;
  let rejectedBefore = 0;
  for (const lane of lanes) {
    if (usage.total() + LIMITS.scanLaneUsd > LIMITS.maxScanUsd) {
      notes.push(`Scan lane "${lane.name}" was not run: the scan would have passed $${LIMITS.maxScanUsd}.`);
      continue;
    }
    let triaged;
    try {
      const scanNotes = await researchTurn(client, usage, {
        model: scanModel,
        system,
        searches: LIMITS.scanSearches,
        fetches: LIMITS.scanFetches,
        partial: true,
        log: (m) => log(`scan ${lane.name}: ${m}`),
        prompt: scanPrompt({ lane, runDate, lookbackDays, titles, rejected: rejectedNames }),
      });
      if (!scanNotes) {
        notes.push(`Scan lane "${lane.name}" was refused or did not finish.`);
        continue;
      }
      triaged = await structure(client, usage, {
        instruction: 'Extract every candidate from these scan notes. Keep URLs exactly as written. Set released to the release date the notes give, as YYYY-MM-DD or YYYY-MM, or leave it empty. Set in_scope false only for a candidate the notes call out of scope or weak. Do not set in_scope false because of a release date, and do not set it false because the notes call the candidate a duplicate or already known: a script checks that.',
        notes: scanNotes,
        schema: SCAN_SCHEMA,
      });
    } catch (e) {
      notes.push(`Scan lane "${lane.name}" failed (${errorText(e)}).`);
      continue;
    }
    if (!triaged) {
      notes.push(`Scan lane "${lane.name}": triage returned no usable candidate list.`);
      continue;
    }
    const fresh = [];
    for (const c of triaged.candidates ?? []) {
      if (!c?.name) continue;
      const dup = isKnown(c);
      if (dup?.where === 'rejected') {
        rejectedBefore += 1;
        skipped.push({ name: c.name, reason: `not judged again: ${dup.reason}` });
        continue;
      }
      if (dup) {
        echoed += 1;
        skipped.push({ name: c.name, reason: `already known, not judged: ${dup.reason}` });
        continue;
      }
      if (!c.in_scope) {
        skipped.push({ name: c.name, reason: `triage: ${clean(c.reason)}` });
        continue;
      }
      const forms = [c.name, ...(c.aliases ?? [])].map(matchForm).filter(longEnough);
      const other = forms.map((n) => seen.get(n)).find(Boolean);
      if (other) {
        skipped.push({ name: c.name, reason: `repeats ${other} from another scan lane` });
        continue;
      }
      for (const n of forms) seen.set(n, c.name);
      fresh.push(c);
    }
    // Inside the lookback first, then undated, then older. A stable sort keeps the scan's order within each group.
    const rank = (c) => {
      const age = ageInDays(c.released, runDate);
      return age === null ? 1 : age <= lookbackDays ? 0 : 2;
    };
    byLane.push(fresh.map((c, i) => ({ c, i })).sort((a, b) => rank(a.c) - rank(b.c) || a.i - b.i).map((x) => x.c));
    log(`scan ${lane.name}: ${triaged.candidates?.length ?? 0} candidates, ${fresh.length} to judge`);
  }
  if (!byLane.length) {
    notes.push('No scan lane finished; nothing was judged.');
    return;
  }
  if (echoed) notes.push(`The scan returned ${echoed} candidate${echoed === 1 ? '' : 's'} that an issue or the record store already holds. None was judged.`);
  if (rejectedBefore) notes.push(`The scan returned ${rejectedBefore} candidate${rejectedBefore === 1 ? '' : 's'} that the judge rejected in the last ${lookbackDays} days. None was judged again.`);

  // One from each lane in turn, so the judge cap is shared between lanes.
  const out = [];
  for (let i = 0; byLane.some((l) => i < l.length); i++) for (const l of byLane) if (i < l.length) out.push(l[i]);

  for (const c of out.slice(LIMITS.maxJudged)) skipped.push({ name: c.name, reason: `over the judge cap of ${LIMITS.maxJudged}; the next run picks it up` });
  for (const c of out.slice(0, LIMITS.maxJudged)) {
    if (usage.total() > LIMITS.maxRunUsd) {
      skipped.push({ name: c.name, reason: `run cost passed $${LIMITS.maxRunUsd}; not judged, the next run picks it up` });
      continue;
    }
    try {
      const similar = near(c);
      const research = await researchTurn(client, usage, {
        model: MODELS.judge,
        system,
        searches: LIMITS.judgeSearches,
        fetches: LIMITS.judgeFetches,
        log: (m) => log(`judge ${c.name}: ${m}`),
        prompt: [
          `Run date: ${runDate}. Verify this candidate against its primary sources and decide whether it should be filed.`,
          `Valid areas: ${AREAS.join(', ')}.`,
          '',
          `Name: ${c.name}`,
          `Aliases: ${(c.aliases ?? []).join(', ') || 'none'}`,
          `Type: ${c.kind}`,
          `Released: ${c.released || 'not known'}`,
          `Summary: ${c.summary}`,
          `URLs: ${(c.urls ?? []).join(' ')}`,
          '',
          `A script compared the name and aliases with ${checked || 'the issues and the record store'} and found none under this spelling. It cannot tell whether the database holds the resource under another name.`,
          ...(similar.length ? [
            'Records and requests with a similar name:',
            ...similar.map((s) => `- ${s}`),
            'If the candidate is one of these under another spelling, or only a size, checkpoint or minor release of it, conclude SKIP and name the one it matches. A new version that changes what the resource can do is a resource of its own.',
          ] : []),
          'An earlier release date is not a reason to skip it; record the date and judge the resource on its substance.',
          'Open the primary sources. Write notes covering every point under Verification and Articles in your instructions, with each URL and its retrieval date. End with FILE or SKIP and the reason.',
        ].join('\n'),
      });
      if (!research) {
        skipped.push({ name: c.name, reason: 'judge refused or did not finish' });
        continue;
      }
      const judgement = await structure(client, usage, {
        instruction: `Turn these verification notes into the schema. Use only facts in the notes. Leave a string empty when the notes do not give it. A source has retrieved_at only if the notes say it was opened; use ${runDate} for those. decision is "skip" when the notes conclude SKIP.`,
        notes: research,
        schema: JUDGEMENT_SCHEMA,
      });
      if (!judgement) {
        skipped.push({ name: c.name, reason: 'could not structure the judge notes' });
        continue;
      }
      // The notes decide, not the structuring call: notes that end with SKIP are never filed.
      if (verdictOf(research) === 'SKIP' && judgement.decision !== 'skip') {
        judgement.decision = 'skip';
        judgement.skip_reason ||= 'the judge notes conclude SKIP';
      }
      if (judgement.decision === 'skip') onReject(c, judgement);
      judged.push(judgement);
    } catch (e) {
      skipped.push({ name: c.name, reason: `judge call failed (${errorText(e)}); the next run picks it up` });
    }
  }
}

// ---------- Main ----------

function parseArgs(argv) {
  const args = { dryRun: false, reportOnly: false, fixtures: FIXTURES, out: '', storeDir: '', state: '', maxPairs: LIMITS.maxPairs, lookbackDays: 30 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--dry-run') args.dryRun = true;
    else if (a === '--report-only') args.reportOnly = true;
    else if (a === '--fixtures') args.fixtures = argv[++i];
    else if (a === '--out') args.out = argv[++i];
    else if (a === '--store-dir') args.storeDir = argv[++i];
    else if (a === '--state') args.state = argv[++i];
    else if (a === '--max-pairs') args.maxPairs = /^\d+$/.test(argv[++i] ?? '') ? Number(argv[i]) : NaN;
    else if (a === '--lookback-days') args.lookbackDays = Number(argv[++i]);
    else throw new Error(`unknown argument ${a}`);
  }
  if (!Number.isFinite(args.lookbackDays) || args.lookbackDays < 1) throw new Error('--lookback-days needs a positive number');
  // A mistyped value (NaN) would switch the cap off: every comparison with NaN is false.
  if (!Number.isInteger(args.maxPairs)) throw new Error('--max-pairs needs a whole number, 0 or more');
  return args;
}

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'));
}

/**
 * Run the scan. Returns { summary, planned } so tests can inspect a dry run. `deps` replaces
 * the GitHub client, the Anthropic client and the clock in tests.
 */
export async function main(argv = process.argv.slice(2), env = process.env, deps = {}) {
  const args = parseArgs(argv);
  const mode = args.dryRun ? 'dry run' : args.reportOnly ? 'report only' : 'live';
  const runDate = (deps.now ?? new Date()).toISOString().slice(0, 10);
  const repo = env.GITHUB_REPOSITORY || DEFAULT_REPO;
  const usage = new Usage();
  const notes = [];
  const log = deps.log ?? ((m) => console.log(m));
  const emit = (summary) => {
    if (env.GITHUB_STEP_SUMMARY) appendFileSync(env.GITHUB_STEP_SUMMARY, `${summary}\n`);
    else log(summary);
  };

  if (!args.dryRun && !env.ANTHROPIC_API_KEY) {
    const summary = `## Discovery scan, ${runDate}\n\nSkipped: the ANTHROPIC_API_KEY secret is not set. Set it in the repository or organisation secrets to turn the scan on (docs/agents.md).\n`;
    emit(summary);
    log('::notice::Discovery scan skipped: ANTHROPIC_API_KEY is not set.');
    return { summary, planned: [] };
  }

  const fixtures = resolve(ROOT, args.fixtures);
  let articleAccess = Boolean(env.ARTICLE_TOKEN);
  const gh = args.dryRun ? null : (deps.github ?? githubClient(env.GH_TOKEN || env.GITHUB_TOKEN));
  const articleGh = args.dryRun || !env.ARTICLE_TOKEN ? null : (deps.articleGithub ?? githubClient(env.ARTICLE_TOKEN));

  // Known resources.
  let issues;
  let articles;
  let storeNames;
  if (args.dryRun) {
    issues = [...readJson(join(fixtures, 'issues.json')), ...(articleAccess ? readJson(join(fixtures, 'article-issues.json')) : [])];
    articles = readJson(join(fixtures, 'articles.json'));
    storeNames = await readStoreNames(join(fixtures, 'entities'), matchForm);
  } else {
    issues = await gh.listIssues(repo);
    if (articleGh) {
      try {
        issues.push(...(await articleGh.listIssues(ARTICLE_REPO)));
      } catch (e) {
        articleAccess = false;
        notes.push(`Could not read ${ARTICLE_REPO} issues (${errorText(e)}); article requests go into the data issues.`);
      }
    } else {
      notes.push('No rewire.it token (REWIRE_BOT app); each article request is a section of its data issue, and rewire.it issues were not checked.');
    }
    try {
      const res = await (deps.fetch ?? fetch)('https://rewirebio.io/blog/');
      articles = res.ok ? parseBlogIndex(await res.text()) : [];
      if (!res.ok) notes.push(`Blog index returned ${res.status}; published articles were not checked.`);
      else if (!articles.length) notes.push('Blog index had no article links; published articles were not checked.');
    } catch (e) {
      articles = [];
      notes.push(`Blog index could not be read (${errorText(e)}); published articles were not checked.`);
    }
    const storeDir = args.storeDir ? resolve(ROOT, args.storeDir) : join(ROOT, 'data/entities');
    storeNames = await readStoreNames(storeDir, matchForm);
    // readStoreNames skips files that are missing, so a store that moved, or a checkout without
    // it, reads as empty. Then every stored resource would look new and be filed. Stop before
    // any model call or GitHub write.
    if (!storeNames.size) {
      const message = `No record-store names were read from ${storeDir}. Nothing was scanned or filed, because every stored resource would look new. Check that the workflow checks out data/entities.`;
      emit(`## Discovery scan, ${runDate} (${mode})\n\nStopped: ${message}\n`);
      throw new Error(message);
    }
  }
  const statePath = !args.dryRun && args.state ? resolve(args.state) : '';
  const rejected = readRejected(statePath, notes).filter((r) => {
    const age = ageInDays(r.date, runDate);
    return age !== null && age < args.lookbackDays;
  });

  const skipped = [];
  const filed = [];
  // Whatever happens below, the summary with token usage is written.
  try {
    // Candidates.
    let candidates = [];
    if (args.dryRun) {
      candidates = readJson(join(fixtures, 'judgements.json'));
    } else {
      let client = deps.anthropic;
      if (!client) {
        const { default: Anthropic } = await import('@anthropic-ai/sdk');
        client = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY, maxRetries: 3, timeout: 10 * 60 * 1000 });
      }
      const system = readFileSync(join(ROOT, PROMPT_PATH), 'utf8');
      await liveCandidates(client, usage, {
        scanModel: env.DISCOVERY_SCAN_MODEL || MODELS.scan,
        system,
        runDate,
        lookbackDays: args.lookbackDays,
        titles: knownTitles(issues, repo),
        rejectedNames: rejected.slice(-LIMITS.knownTitles).map((r) => r.name),
        // Names only before judging: a scan URL may be a dependency, not the candidate's own source.
        isKnown: (c) => findDuplicate({ ...c, sources: [] }, { issues, storeNames }) ?? findRejected(c, rejected, runDate, args.lookbackDays),
        near: (c) => nearMatches(c, { issues, storeNames }),
        checked: `${issues.length} issue titles and ${storeNames.size} record-store names`,
        // Remembered under the scan's names and the judge's, because the next scan may return either.
        onReject: (c, judgement) => rejected.push({
          name: c.name,
          names: [...new Set([c.name, ...(c.aliases ?? []), judgement.name, ...(judgement.aliases ?? [])].map(matchForm))].filter(longEnough),
          date: runDate,
          reason: clean(judgement.skip_reason).slice(0, 200),
        }),
        skipped,
        judged: candidates,
        notes,
        log,
      });
    }

    // Plan and file.
    // The cap is per day, not per run: a second live run on the same date files only what the
    // first left of it. Issues this script filed carry its marker.
    const filedToday = issues.filter((i) => i.repo === repo && markersIn(i.body).length && String(i.created_at ?? '').slice(0, 10) === runDate).length;
    if (filedToday) notes.push(`${filedToday} issue${filedToday === 1 ? ' was' : 's were'} already filed today; the cap of ${args.maxPairs} counts them.`);
    const plan = planFiling(candidates, { issues, storeNames, articles, articleAccess, runDate, maxPairs: args.maxPairs, filedToday });
    skipped.push(...plan.skipped);
    const write = !args.dryRun && !args.reportOnly;
    if (write && plan.file.length) {
      await gh.ensureLabels(repo, ['entity-request', 'tier-1', 'tier-2', 'tier-3']);
      if (articleGh && articleAccess) await articleGh.ensureLabels(ARTICLE_REPO, ['article']);
    }
    for (const { candidate, tier, existingArticle, dedupNote } of plan.file) {
      const pairArticle = !existingArticle && articleAccess;
      const data = renderDataIssue(candidate, { tier, runDate, existingArticle, dedupNote, article: pairArticle || existingArticle ? null : { inline: true } });
      const entry = { name: candidate.name, tier, labels: data.labels, title: data.title, data, article: null };
      if (pairArticle) entry.article = renderArticleIssue(candidate, { dataUrl: '(data issue URL)', runDate, dedupNote });
      if (write) {
        const created = await gh.createIssue(repo, data);
        entry.dataUrl = created.html_url;
        if (pairArticle) {
          // The data issue exists now and its marker blocks a retry, so a failed article issue
          // falls back to the article request inside the data issue.
          let article;
          try {
            const art = await articleGh.createIssue(ARTICLE_REPO, renderArticleIssue(candidate, { dataUrl: created.html_url, runDate, dedupNote }));
            entry.articleUrl = art.html_url;
            article = { url: art.html_url };
          } catch (e) {
            notes.push(`Article issue for ${clean(candidate.name)} failed (${errorText(e)}); the request is inside its data issue.`);
            article = { inline: true };
          }
          await gh.updateIssue(repo, created.number, { body: renderDataIssue(candidate, { tier, runDate, existingArticle, dedupNote, article }).body });
        }
      }
      if (!entry.articleUrl) entry.articleNote = existingArticle ? `existing article ${existingArticle.url}` : pairArticle && !write ? 'article issue planned in rewire.it' : 'article request inside the data issue';
      filed.push(entry);
    }
  } finally {
    const summary = renderSummary({ mode, runDate, usage, filed, skipped, notes });
    emit(summary);
    if (statePath) {
      mkdirSync(dirname(statePath), { recursive: true });
      writeFileSync(statePath, `${JSON.stringify({ rejected }, null, 2)}\n`);
    }
    if (args.out) {
      mkdirSync(args.out, { recursive: true });
      writeFileSync(join(args.out, 'plan.json'), `${JSON.stringify(filed, null, 2)}\n`);
      for (const [i, p] of filed.entries()) {
        writeFileSync(join(args.out, `${i + 1}-data.md`), `# ${p.data.title}\n\nLabels: ${p.data.labels.join(', ')}\n\n${p.data.body}\n`);
        if (p.article) writeFileSync(join(args.out, `${i + 1}-article.md`), `# ${p.article.title}\n\nLabels: ${p.article.labels.join(', ')}\n\n${p.article.body}\n`);
      }
      writeFileSync(join(args.out, 'usage.json'), `${JSON.stringify({ byModel: usage.byModel, estimatedUsd: usage.total() }, null, 2)}\n`);
    }
    log(`Estimated cost of this run: $${usage.total().toFixed(4)}`);
  }
  return { summary: renderSummary({ mode, runDate, usage, filed, skipped, notes }), planned: filed, skipped, usage };
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  main().catch((e) => {
    console.error(e);
    process.exit(1);
  });
}
