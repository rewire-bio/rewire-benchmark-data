/** The validator pack: deterministic checks over the store, report only.
 *
 *   npm run checks -- report      run every check, write the TSV, compare with the baseline
 *   npm run checks -- baseline    run every check and write data/omics/checks-baseline.json
 *
 * Nothing here writes a record, reads the network or calls a model. The report is a TSV under
 * maintenance/reports/, one row per finding, and the counts it prints are the deliverable.
 * data/omics/checks-baseline.json pins each rule's count and tests/checks-baseline.test.ts
 * fails when a later run raises one.
 *
 * That failure is a backlog ratchet, not a correctness failure. Every check is report severity:
 * nothing here gates `records -- add`, and a finding is a lead to read, not a wrong value. The
 * ratchet bites on growth, so an evidence pull request may leave the existing backlog alone but
 * may not add to it. When it fires, the failure names the check and rule that rose and by how
 * much, and gives the two ways forward: fix the new findings (they are rows of the TSV under the
 * named rule), or raise the baseline in the same pull request with a dated review in
 * docs/reviews/. ratchetRemedy below is the wording, and the baseline file's `note` carries it.
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
import { qualifierShape } from "./qualifier_shape";
import { columnCoherence } from "./column_coherence";
import { duplicateArtifact } from "./duplicate_artifact";
import { normaliseOrRefuse } from "./normalise_or_refuse";

export const checks: Check[] = [
  unitForMetric,
  directionDefault,
  printedVsNumeric,
  qualifierShape,
  columnCoherence,
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

/** Every count a later run must not exceed: each rule, each check total, and the grand total. */
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

/** Why a count may not rise and what to do when one has. The baseline file's `note` carries the
 * same words, the ratchet test fails with them, and `checks -- report` prints them. */
export const ratchetRemedy =
  "Every check is report severity: nothing here gates records -- add, and a finding is a lead to read, not a wrong value. " +
  "tests/checks-baseline.test.ts fails when a run raises any count above the number pinned in data/omics/checks-baseline.json, " +
  "so the backlog can be worked down but not grown. A failure on an unrelated evidence pull request means the records that " +
  "pull request adds raised the check and rule the failure names: a backlog ratchet, not a correctness failure. Two ways " +
  "forward, both in that same pull request. Fix the new findings: npm run checks -- report writes one row per finding to " +
  "maintenance/reports/checks-<date>.tsv, and the rows carrying the named rule are the ones to read. Or raise the baseline: " +
  "rerun npm run checks -- baseline and add a dated review in docs/reviews/ saying which rule rose, by how much, and why the " +
  "new findings stand.";

/** The baseline file's `note`. Written by `checks -- baseline`, so the file and this string match. */
export const ratchetNote =
  "Counts of every deterministic check in scripts/omics/checks/, pinned from the first run. " + ratchetRemedy;

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
export function ratchetFailure(baseline: Baseline, run: RunResult): string {
  const grown = risesAboveBaseline(baseline, run);
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
      note: ratchetNote,
      notes: [
        "The commit is the HEAD the pack was written against. The checks themselves were not committed when this file was written, so the run was from the working tree at that commit. Rerun npm run checks -- baseline --commit <sha> after committing: the run is deterministic, so only this field changes.",
        "The sentences below carry the numbers of the first run. Re-pinning this file after a count changes means rewriting them in scripts/omics/checks/cli.ts first, or they describe a run that no longer exists.",
        "C1 minority-unit, C2 and C4 reproduce the figures the design predicted exactly: 5,093 over 43 metrics; 1,256 splitting 58, 206 and 992; 338 splitting high 171, no 161 and max 6. C1 unit-scope-note is new work and is measured here for the first time.",
        "C3: the prototype figure of 170 did not reproduce and was not inherited, and nor did the two other figures in circulation (1,640 from a strict check, 603 from a naive half-up check). parseCell measures 3,436 findings over 51,892 results holding both values, and the split is the deliverable: 1,784 printed values parseCell cannot read, 1,473 where the printed value is the numeric value rounded, 167 where the stored number is the second number of a two-number cell, 6 off by a factor of 100 and 6 disagreeing outright. The last two rules, 12 records, are one source printing numbers with a dot thousands separator and a comma decimal.",
        "C5: neither prototype grouping was inherited (676 of 2,446 columns and 19,374 results by one, 362 of 530 tables and 32,141 results by the other). This implementation groups by source, table or figure anchor and column, which column_coherence.ts states and argues for: 146 of 2,092 columns, holding 2,436 of the 34,688 results that could be placed in a column.",
        "C9: this implementation reports 187 groups where the design carried 171. The difference is the grouping, not the store, and duplicate_artifact.ts says why.",
        "C13: zero is the expected count. The 2,574 records of docs/reviews/2026-11-16-attribute-normalisation.md were migrated before this check existed; the ratchet is what keeps the count at zero.",
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
    const failure = ratchetFailure(baseline, run);
    const want = ratchetCounts(baseline);
    const got = ratchetCounts(run);
    const shrunk = Object.entries(got).filter(([key, n]) => want[key] !== undefined && n < want[key]);
    if (failure) console.log(`\n${failure}`);
    else if (shrunk.length) console.log(`\nBelow ${baselineFile} on ${shrunk.length} counts; lower the baseline in the same PR.`);
    else console.log(`\nCounts equal ${baselineFile}.`);
  } else {
    console.log(`\nNo ${baselineFile} yet; run npm run checks -- baseline to write one.`);
  }
}
