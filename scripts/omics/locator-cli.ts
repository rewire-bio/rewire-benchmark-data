/** How much of a stored locator the v2 grammar reads, over every result record in the store.
 *
 * Usage: npm run locator -- coverage [--out <path>]
 *        npm run locator -- parse "<locator string>"
 *
 * `coverage` reads `data/evidence/results/*.jsonl` directly, parses each `source_locator`, and
 * counts the four buckets (fully addressed, partially addressed, residue-carrying, unanchored) by
 * class. It writes `maintenance/reports/locator-coverage-<date>.tsv` and writes nothing else: no
 * record changes, no store load.
 *
 * `parse` prints one locator's parse, for looking at a class the report flags.
 */
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import {
  classifyLocator, coverageOf, locatorClasses, parseLocator, renderLocator,
  type LocatorClass, type LocatorCoverage, type ParsedLocator,
} from "../../shared/omics/locator";

const RESULTS_DIR = "data/evidence/results";
const REPORT_DIR = "maintenance/reports";

export type ClassTally = {
  locators: number;
  full: number;
  partial: number;
  residue: number;
  unanchored: number;
  /** A cell address with no label to check it. Counted inside `partial`, reported on its own
   * because it is the bucket a looser definition of "addressed" would quietly absorb. */
  cell_only: number;
  /** renderLocator(parseLocator(x)) === x, over the fully addressed locators of this class. */
  round_trip_exact: number;
  /** parseLocator(renderLocator(parseLocator(x))) reads back the same structure. */
  round_trip_idempotent: number;
};

const emptyTally = (): ClassTally => ({
  locators: 0, full: 0, partial: 0, residue: 0, unanchored: 0,
  cell_only: 0, round_trip_exact: 0, round_trip_idempotent: 0,
});

/** The typed fields a round trip has to preserve. `raw` is the text a component was read from, so
 * it is left out: a rendered locator spells its components canonically. */
function structure(parsed: ParsedLocator): string {
  return JSON.stringify({
    anchors: parsed.anchors.map((a) => [a.kind, a.value, a.container ?? null]),
    addresses: parsed.addresses.map((a) => [a.kind, a.value, a.value2 ?? null]),
    selectors: parsed.selectors.map((s) => [s.key, s.value, s.form]),
    qualifiers: parsed.qualifiers.map((q) => [q.kind, q.text]),
  });
}

export function tallyLocators(locators: string[]): Map<LocatorClass, ClassTally> {
  const tallies = new Map<LocatorClass, ClassTally>();
  for (const printed of locators) {
    const parsed = parseLocator(printed);
    const cls = classifyLocator(printed);
    const bucket: LocatorCoverage = coverageOf(parsed.verdict);
    const tally = tallies.get(cls) ?? emptyTally();
    tally.locators += 1;
    tally[bucket] += 1;
    if (parsed.verdict === "cell_only") tally.cell_only += 1;
    if (bucket === "full") {
      const rendered = renderLocator(parsed);
      if (rendered === printed) tally.round_trip_exact += 1;
      if (structure(parseLocator(rendered)) === structure(parsed)) tally.round_trip_idempotent += 1;
    }
    tallies.set(cls, tally);
  }
  return tallies;
}

function storedLocators(root: string): string[] {
  const dir = path.join(root, RESULTS_DIR);
  const locators: string[] = [];
  for (const file of fs.readdirSync(dir).filter((f) => f.endsWith(".jsonl")).sort()) {
    const text = fs.readFileSync(path.join(dir, file), "utf8");
    for (const line of text.split("\n")) {
      if (!line.trim()) continue;
      const record = JSON.parse(line) as { kind?: string; attributes?: { source_locator?: unknown } };
      if (record.kind !== "result") continue;
      const locator = record.attributes?.source_locator;
      if (typeof locator === "string") locators.push(locator);
    }
  }
  return locators;
}

const pct = (part: number, whole: number) => (whole === 0 ? "0.0" : ((100 * part) / whole).toFixed(1));

function report(tallies: Map<LocatorClass, ClassTally>): { header: string[]; rows: string[][] } {
  const header = [
    "class", "locators", "fully_addressed", "fully_addressed_pct", "partially_addressed",
    "residue", "unanchored", "cell_only", "round_trip_exact", "round_trip_idempotent",
  ];
  const total = emptyTally();
  const rows: string[][] = [];
  const row = (name: string, t: ClassTally) => [
    name, String(t.locators), String(t.full), pct(t.full, t.locators), String(t.partial),
    String(t.residue), String(t.unanchored), String(t.cell_only),
    String(t.round_trip_exact), String(t.round_trip_idempotent),
  ];
  for (const cls of locatorClasses) {
    const tally = tallies.get(cls);
    if (!tally) continue;
    for (const key of Object.keys(total) as (keyof ClassTally)[]) total[key] += tally[key];
    rows.push(row(cls, tally));
  }
  rows.push(row("TOTAL", total));
  return { header, rows };
}

function coverage(root: string, out: string | null): number {
  const locators = storedLocators(root);
  const tallies = tallyLocators(locators);
  const { header, rows } = report(tallies);
  const widths = header.map((h, i) => Math.max(h.length, ...rows.map((r) => r[i].length)));
  const line = (cells: string[]) =>
    cells.map((c, i) => (i === 0 ? c.padEnd(widths[i]) : c.padStart(widths[i]))).join("  ");
  console.log(line(header));
  for (const r of rows) console.log(line(r));
  const totals = rows[rows.length - 1];
  const [, all, full, fullPct, partial, residue, unanchored, cellOnly, exact, idempotent] = totals;
  console.log("");
  console.log(`fully addressed            ${full} of ${all} (${fullPct}%)`);
  console.log(`plus partially addressed   ${Number(full) + Number(partial)} of ${all} (${pct(Number(full) + Number(partial), Number(all))}%)`);
  console.log(`residue-carrying           ${residue} of ${all} (${pct(Number(residue), Number(all))}%)`);
  console.log(`unanchored                 ${unanchored} of ${all} (${pct(Number(unanchored), Number(all))}%)`);
  console.log(`of the partial, cell only  ${cellOnly}`);
  console.log(`round trip exact           ${exact} of ${full} addressed (${pct(Number(exact), Number(full))}%)`);
  console.log(`round trip idempotent      ${idempotent} of ${full} addressed (${pct(Number(idempotent), Number(full))}%)`);
  const date = new Date().toISOString().slice(0, 10);
  const target = out ?? path.join(root, REPORT_DIR, `locator-coverage-${date}.tsv`);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, [header, ...rows].map((r) => r.join("\t")).join("\n") + "\n");
  console.log(`\nwrote ${path.relative(root, target)}`);
  return 0;
}

function parseOne(printed: string): number {
  const parsed = parseLocator(printed);
  console.log(JSON.stringify({
    class: classifyLocator(printed),
    verdict: parsed.verdict,
    coverage: coverageOf(parsed.verdict),
    anchors: parsed.anchors,
    addresses: parsed.addresses,
    selectors: parsed.selectors,
    qualifiers: parsed.qualifiers,
    residue: parsed.residue,
    rendered: renderLocator(parsed),
  }, null, 2));
  return 0;
}

function main(argv: string[]): number {
  const root = process.cwd();
  const [command, ...rest] = argv;
  if (command === "coverage") {
    const at = rest.indexOf("--out");
    return coverage(root, at >= 0 ? rest[at + 1] : null);
  }
  if (command === "parse" && rest[0]) return parseOne(rest.join(" "));
  console.error("usage: npm run locator -- coverage [--out <path>]\n       npm run locator -- parse \"<locator>\"");
  return 2;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  process.exit(main(process.argv.slice(2)));
}
