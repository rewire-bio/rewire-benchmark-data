/** The validator pack: deterministic checks over the store, report only.
 *
 *   npm run checks -- report      run every check, write the TSV, compare with the baseline
 *   npm run checks -- baseline    run every check and write data/omics/checks-baseline.json
 *
 * Nothing here writes a record, reads the network or calls a model. The report is a TSV under
 * maintenance/reports/, one row per finding, and the counts it prints are the deliverable.
 * data/omics/checks-baseline.json pins each rule's count and tests/checks-baseline.test.ts
 * compares a run with it.
 *
 * The comparison is report only since 23 November 2026 (issue #272): the test prints each
 * count beside its baseline and passes when counts rise. defaultRatchetMode below is the switch,
 * and CHECKS_RATCHET=blocking overrides it for one run. Every check is report severity: nothing
 * here gates `records -- add`, and a finding is a lead to read, not a wrong value.
 *
 * In blocking mode the test fails when a run raises a count. That failure is a backlog ratchet,
 * not a correctness failure: an evidence pull request may leave the existing backlog alone but
 * may not add to it. The failure names the check and rule that rose and by how much, and gives
 * the two ways forward: fix the new findings (they are rows of the TSV under the named rule), or
 * raise the baseline in the same pull request with a dated review in docs/reviews/.
 * ratchetRemedy below is that wording.
 *
 * The store is read with readKind, which returns the stored JSON as it is. loadRecords would
 * validate it against the schema, five validators and the provenance hashes, which is a
 * different job: these checks are meant to report on records the store already accepted.
 */
import fs from "node:fs";
import path from "node:path";
import { Parser } from "n3";
import { readKind } from "../records";
import { entityKinds } from "../../../shared/omics/entity-kinds";
import { countByRule, tsvHeader, tsvRow, type Check, type CheckInput, type Finding, type MetricConcept, type Rec, type UnitConcept } from "./finding";
import { unitForMetric } from "./unit_for_metric";
import { directionDefault } from "./direction_default";
import { printedVsNumeric } from "./printed_vs_numeric";
import { duplicateArtifact } from "./duplicate_artifact";
import { normaliseOrRefuse } from "./normalise_or_refuse";

export const checks: Check[] = [
  unitForMetric,
  directionDefault,
  printedVsNumeric,
  duplicateArtifact,
  normaliseOrRefuse,
];

export const baselineFile = process.env.CHECKS_BASELINE ?? "data/omics/checks-baseline.json";
export const reportDir = "maintenance/reports";

const SKOS = "http://www.w3.org/2004/02/skos/core#";
const RB = "https://benchmarks.rewire.it/vocab#";
const vocabBase = "https://benchmarks.rewire.it/vocab/";

/** Concepts of one scheme file, with the two predicates the checks read.
 *
 * vocab.ts loads schemes for key, IRI and label only, so the predicates are read here instead
 * of widening its Concept type, which the record loader and the exporters depend on. */
function readScheme(file: string, scheme: string): { key: string; direction: string | null; scopeNote: string | null }[] {
  const iri = `${vocabBase}${scheme}/`;
  const quads = new Parser({ format: "Turtle" }).parse(fs.readFileSync(file, "utf8"));
  const keys = quads
    .filter((quad) => quad.predicate.value === `${SKOS}inScheme` && quad.object.value === iri)
    .map((quad) => quad.subject.value);
  return keys.map((subject) => {
    const direction = quads.find((quad) => quad.subject.value === subject && quad.predicate.value === `${RB}defaultDirection`);
    const note = quads.find((quad) => quad.subject.value === subject && quad.predicate.value === `${SKOS}scopeNote`);
    return {
      key: subject.slice(iri.length),
      direction: direction ? direction.object.value.split("/").pop() ?? null : null,
      scopeNote: note ? note.object.value : null,
    };
  });
}

export function loadInput(root = "."): CheckInput {
  const records: Rec[] = entityKinds.flatMap((kind) => readKind<Rec>(kind, root));
  const metrics = new Map<string, MetricConcept>();
  // A concept pointing at direction/unknown is declaring that the metric has no default, so
  // the checks see null rather than the concept key "unknown".
  for (const concept of readScheme(path.join(root, "data/vocab/metric.ttl"), "metric"))
    metrics.set(concept.key, { key: concept.key, defaultDirection: concept.direction === "unknown" ? null : concept.direction });
  const units = new Map<string, UnitConcept>();
  for (const concept of readScheme(path.join(root, "data/vocab/unit.ttl"), "unit"))
    units.set(concept.key, { key: concept.key, scopeNote: concept.scopeNote });
  return {
    records,
    results: records.filter((record) => record.kind === "result"),
    sources: records.filter((record) => record.kind === "source"),
    metrics,
    units,
  };
}

export type CheckSummary = {
  id: string;
  title: string;
  findings: number;
  rules: Record<string, number>;
  context: Record<string, number>;
};

export type RunResult = { findings: Finding[]; summaries: CheckSummary[] };

export function runAll(input: CheckInput, only: Check[] = checks): RunResult {
  const findings: Finding[] = [];
  const summaries: CheckSummary[] = [];
  for (const check of only) {
    const raised = check.run(input);
    findings.push(...raised);
    summaries.push({
      id: check.id,
      title: check.title,
      findings: raised.length,
      rules: countByRule(check, raised),
      context: check.context ? check.context(input, raised) : {},
    });
  }
  return { findings, summaries };
}

export type Baseline = {
  note: string;
  notes: string[];
  commit: string;
  run_date: string;
  store: Record<string, number>;
  total_findings: number;
  checks: Record<string, { title: string; findings: number; rules: Record<string, number>; context?: Record<string, number> }>;
};

/** Every count the baseline pins: each rule, each check total, and the grand total. */
export function ratchetCounts(source: Baseline | RunResult): Record<string, number> {
  const counts: Record<string, number> = {};
  const entries = "checks" in source
    ? Object.entries(source.checks).map(([id, check]) => ({ id, findings: check.findings, rules: check.rules }))
    : source.summaries.map((summary) => ({ id: summary.id, findings: summary.findings, rules: summary.rules }));
  let total = 0;
  for (const entry of entries) {
    counts[entry.id] = entry.findings;
    total += entry.findings;
    for (const [rule, n] of Object.entries(entry.rules)) counts[`${entry.id}.${rule}`] = n;
  }
  counts.total = "checks" in source ? source.total_findings : total;
  return counts;
}

/** Blocking mode only: why a count may not rise and what to do when one has. The ratchet test
 * fails with these words when CHECKS_RATCHET is blocking. The committed baseline file's `note`
 * still carries them from the first run, and is out of date while the ratchet is report only. */
export const ratchetRemedy =
  "Every check is report severity: nothing here gates records -- add, and a finding is a lead to read, not a wrong value. " +
  "tests/checks-baseline.test.ts fails when a run raises any count above the number pinned in data/omics/checks-baseline.json, " +
  "so the backlog can be worked down but not grown. A failure on an unrelated evidence pull request means the records that " +
  "pull request adds raised the check and rule the failure names: a backlog ratchet, not a correctness failure. Two ways " +
  "forward, both in that same pull request. Fix the new findings: npm run checks -- report writes one row per finding to " +
  "maintenance/reports/checks-<date>.tsv, and the rows carrying the named rule are the ones to read. Or raise the baseline: " +
  "rerun npm run checks -- baseline and add a dated review in docs/reviews/ saying which rule rose, by how much, and why the " +
  "new findings stand.";

export type RatchetMode = "selective" | "report" | "blocking";

/** Blocking rules in selective mode (issue #380): clean invariants pinned at zero whose
 * findings indicate duplicate sources, omitted metric directions, unknown metrics, or
 * non-normalised attributes. */
export const blockingRatchetKeys = new Set([
  "C2.unknown-where-declared",
  "C2.metric-not-a-concept",
  "C9",
  "C9.same-artifact-and-url",
  "C13",
  "C13.would-be-rewritten",
]);

/** The default ratchet mode (issue #380): block on C2 omission/concept checks, C9, and C13,
 * while reporting C1.unit-scope-note, C2.opposite, and C3.* advisories. */
export const defaultRatchetMode: RatchetMode = "selective";

/** The mode in force: CHECKS_RATCHET when it is set, defaultRatchetMode otherwise. */
export function ratchetMode(env: Record<string, string | undefined> = process.env): RatchetMode {
  const asked = env.CHECKS_RATCHET;
  if (asked === undefined || asked === "") return defaultRatchetMode;
  if (asked === "selective" || asked === "report" || asked === "blocking") return asked;
  throw new Error(`CHECKS_RATCHET must be "selective", "report", or "blocking", not "${asked}".`);
}

/** What a report-only or selective advisory run says after its table. */
export const reportOnlyNotice =
  "Advisory counts (C1, C2.opposite, C3) do not fail the test in selective/report mode (issues #272, #380); " +
  "npm run checks -- report writes one row per finding to maintenance/reports/checks-<date>.tsv. " +
  "Set CHECKS_RATCHET=blocking to gate on every rule.";

/** The baseline file's `note`, as `checks -- baseline` writes it in each mode. */
export const ratchetNote = (mode: RatchetMode): string =>
  "Counts of every deterministic check in scripts/omics/checks/, pinned after cleanup (#380). " +
  (mode === "blocking" ? ratchetRemedy : reportOnlyNotice);

export type RatchetRise = { key: string; count: number; baseline: number; rise: number };

function risesAboveBaseline(baseline: Baseline, run: RunResult): RatchetRise[] {
  const want = ratchetCounts(baseline);
  const got = ratchetCounts(run);
  return Object.entries(got)
    .filter(([key, n]) => want[key] !== undefined && n > want[key])
    .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
    .map(([key, n]) => ({ key, count: n, baseline: want[key], rise: n - want[key] }));
}

/** Counts above their baseline, as readable lines. Empty when nothing grew. */
export function aboveBaseline(baseline: Baseline, run: RunResult): string[] {
  return risesAboveBaseline(baseline, run).map((rise) => `${rise.key}: ${rise.count}, baseline ${rise.baseline}`);
}

/** The whole failure a maintainer should see: which check and rule rose, by how much, and the two
 * ways forward. Empty when nothing grew. */
export function ratchetFailure(baseline: Baseline, run: RunResult, keys?: Set<string>): string {
  const grown = risesAboveBaseline(baseline, run).filter((rise) => !keys || keys.has(rise.key));
  if (!grown.length) return "";
  const name = (key: string): string => {
    if (key === "total") return "total findings";
    const dot = key.indexOf(".");
    const id = dot < 0 ? key : key.slice(0, dot);
    const title = baseline.checks[id]?.title;
    const check = title ? `${id} ${title}` : id;
    return dot < 0 ? `${check} (check total)` : `${check}, rule ${key.slice(dot + 1)}`;
  };
  const lines = grown.map((rise) => `  ${name(rise.key)}: ${rise.count}, baseline ${rise.baseline}, up ${rise.rise}`);
  return [`Check counts rose above ${baselineFile}:`, ...lines, "", ratchetRemedy].join("\n");
}

export type RatchetRow = { key: string; baseline: number | null; count: number | null; difference: number | null };

/** Every count beside its baseline: each check total, each rule under it, then the grand total.
 * A count only one side names has null on the other and no difference. */
export function ratchetRows(baseline: Baseline, run: RunResult): RatchetRow[] {
  const want = ratchetCounts(baseline);
  const got = ratchetCounts(run);
  const keys = [...Object.keys(got), ...Object.keys(want).filter((key) => !(key in got))];
  const rank = (key: string) => (key === "total" ? 1 : 0);
  return keys
    .map((key, at) => ({ key, at }))
    .sort((a, b) => rank(a.key) - rank(b.key) || a.at - b.at)
    .map(({ key }) => {
      const pinned = want[key] ?? null;
      const count = got[key] ?? null;
      return { key, baseline: pinned, count, difference: pinned === null || count === null ? null : count - pinned };
    });
}

const signed = (n: number | null): string => (n === null ? "" : n > 0 ? `+${n}` : String(n));
const cell = (n: number | null): string => (n === null ? "" : String(n));

/** The rows as a table: aligned plain text for a job log, or Markdown for a step summary. */
export function ratchetTable(rows: RatchetRow[], format: "text" | "markdown" = "text"): string {
  const head = ["count", "baseline", "current", "difference"];
  const body = rows.map((row) => [row.key, cell(row.baseline), cell(row.count), signed(row.difference)]);
  if (format === "markdown")
    return ["| Count | Baseline | Current | Difference |", "| --- | ---: | ---: | ---: |", ...body.map((line) => `| ${line.join(" | ")} |`)].join("\n");
  const widths = head.map((title, column) => Math.max(title.length, ...body.map((line) => line[column].length)));
  const line = (cells: string[]) => cells.map((text, column) => (column ? text.padStart(widths[column]) : text.padEnd(widths[column]))).join("  ").trimEnd();
  return [line(head), ...body.map(line)].join("\n");
}

export type RatchetVerdict = { mode: RatchetMode; rose: number; blocks: boolean; message: string; summary: string };

/** The comparison in one mode. `blocks` is what the ratchet test asserts on: true only when the
 * mode is blocking and a count rose. `message` is for the job log and the assertion, `summary`
 * is the same report as Markdown for the GitHub step summary. */
export function ratchetVerdict(baseline: Baseline, run: RunResult, mode: RatchetMode = ratchetMode()): RatchetVerdict {
  const rows = ratchetRows(baseline, run);
  const rose = rows.filter((row) => (row.difference ?? 0) > 0).length;
  const blockingKeys = mode === "selective" ? blockingRatchetKeys : undefined;
  const blocks = mode === "blocking"
    ? rose > 0
    : mode === "selective"
      ? rows.some((row) => (row.difference ?? 0) > 0 && blockingRatchetKeys.has(row.key))
      : false;
  const headline = rose
    ? `${rose} ${rose === 1 ? "count" : "counts"} above ${baselineFile} (ratchet mode: ${mode}).`
    : `No count above ${baselineFile} (ratchet mode: ${mode}).`;
  const closing = blocks ? ratchetFailure(baseline, run, blockingKeys) : mode !== "blocking" ? reportOnlyNotice : "";
  const parts = (table: string) => [headline, "", table, ...(closing ? ["", closing] : [])].join("\n");
  return {
    mode,
    rose,
    blocks,
    message: parts(ratchetTable(rows, "text")),
    summary: ["### Deterministic checks against the baseline", "", parts(ratchetTable(rows, "markdown")), ""].join("\n"),
  };
}

/** Print the verdict to the log and, on GitHub Actions, append it to the step summary. */
export function publishVerdict(
  verdict: RatchetVerdict,
  env: Record<string, string | undefined> = process.env,
  log: (text: string) => void = console.log,
): void {
  log(verdict.message);
  if (env.GITHUB_STEP_SUMMARY) fs.appendFileSync(env.GITHUB_STEP_SUMMARY, verdict.summary + "\n");
}

const storeCounts = (input: CheckInput): Record<string, number> => ({
  records: input.records.length,
  results: input.results.length,
  sources: input.sources.length,
  metric_concepts: input.metrics.size,
  unit_concepts: input.units.size,
});

function writeReport(findings: Finding[], date: string): string {
  fs.mkdirSync(reportDir, { recursive: true });
  const file = path.join(reportDir, `checks-${date}.tsv`);
  fs.writeFileSync(file, [tsvHeader, ...findings.map(tsvRow)].join("\n") + "\n");
  return file;
}

function printSummary(run: RunResult): void {
  for (const summary of run.summaries) {
    console.log(`${summary.id} ${summary.title}: ${summary.findings}`);
    for (const [rule, n] of Object.entries(summary.rules)) console.log(`    ${rule}: ${n}`);
    for (const [key, n] of Object.entries(summary.context)) console.log(`    (${key}: ${n})`);
  }
  console.log(`total findings: ${run.findings.length}`);
}

const today = () => new Date().toISOString().slice(0, 10);

const argValue = (args: string[], name: string): string | undefined => {
  const found = args.indexOf(name);
  return found >= 0 ? args[found + 1] : undefined;
};

if (process.argv[1]?.endsWith(path.join("checks", "cli.ts"))) {
  const [command, ...args] = process.argv.slice(2);
  const usage = "Usage: npm run checks -- report [--date YYYY-MM-DD] | baseline [--date YYYY-MM-DD] [--commit <sha>]";
  if (command !== "report" && command !== "baseline") {
    console.error(usage);
    process.exit(1);
  }
  const date = argValue(args, "--date") ?? today();
  const started = Date.now();
  const input = loadInput();
  const run = runAll(input);
  const file = writeReport(run.findings, date);
  printSummary(run);
  console.log(`\n${run.findings.length} findings written to ${file} in ${((Date.now() - started) / 1000).toFixed(1)} s`);
  if (command === "baseline") {
    const commit = argValue(args, "--commit") ?? "";
    const baseline: Baseline = {
      note: ratchetNote(ratchetMode()),
      notes: [
        "Re-pinned for issue #380 after retiring high-noise rules, widening parseCell, merging 187 duplicate source groups, backfilling 147 omitted metric directions, removing the default direction from cohens-d, and fixing 61 CACHE 3 compound-count directions.",
        "C1 keeps only unit-scope-note (advisory); minority-unit is retired.",
        "C2 drops asserted-where-none. C2.unknown-where-declared and C2.metric-not-a-concept stand at 0 and block in default selective mode; C2.opposite captures legitimate domain reversals and remains advisory.",
        "C3 drops numeric-is-the-second-number, adds null-numeric-value (386), honours declared numeric_representation and printed_value_basis, checks bracketed second numbers before rounding, and runs against widened parseCell.",
        "C4 and C5 are retired.",
        "C9 ignores superseded/excluded sources and supersedes-linked components, stands at 0 after merging all 187 duplicate groups, and blocks in default selective mode.",
        "C13 stands at 0 and blocks in default selective mode.",
      ],
      commit,
      run_date: date,
      store: storeCounts(input),
      total_findings: run.findings.length,
      checks: Object.fromEntries(
        run.summaries.map((summary) => [summary.id, { title: summary.title, findings: summary.findings, rules: summary.rules, context: summary.context }]),
      ),
    };
    fs.mkdirSync(path.dirname(baselineFile), { recursive: true });
    fs.writeFileSync(baselineFile, JSON.stringify(baseline, null, 2) + "\n");
    console.log(`Wrote ${baselineFile}.`);
  } else if (fs.existsSync(baselineFile)) {
    const baseline = JSON.parse(fs.readFileSync(baselineFile, "utf8")) as Baseline;
    const verdict = ratchetVerdict(baseline, run);
    const shrunk = ratchetRows(baseline, run).filter((row) => (row.difference ?? 0) < 0);
    console.log(`\n${verdict.message}`);
    if (!verdict.rose && shrunk.length) console.log(`\nBelow ${baselineFile} on ${shrunk.length} counts; lower the baseline in the same PR.`);
    else if (!verdict.rose) console.log(`\nCounts equal ${baselineFile}.`);
  } else {
    console.log(`\nNo ${baselineFile} yet; run npm run checks -- baseline to write one.`);
  }
}
