/** The licence triage queue: every source whose licence is still undetermined.
 *
 *   npx tsx scripts/licence/triage.ts
 *
 * Writes maintenance/reports/licence-triage-<date>.tsv and prints the counts.
 * Pass --date <YYYY-MM-DD> to name the file, --out <path> to put it somewhere
 * else, and --stdout to write the rows instead of a file.
 *
 * The queue is generated. Do not edit the file it writes: add a row to
 * data/archive/licence-map.tsv or resolve the licence on the source record,
 * then run this again.
 *
 * Nothing here blocks a fetch. A source in this queue is fetched and stored
 * privately like any other; the queue says what cannot be published yet.
 */
import fs from "node:fs";
import path from "node:path";
import { parseArgs } from "node:util";
import { readLicenceMap, sourcesPath } from "./map";
import { sourceClassOf } from "../../shared/archive/worklist";
import type { SourceClass } from "../../shared/archive/schema";

/** Why this source is in the queue, most actionable first. */
const reasons = [
  "string-conflicting",
  "string-unresolved",
  "missing-unreported",
  "missing-unavailable",
  "missing-unextracted",
  "no-licence-recorded",
] as const;
type Reason = (typeof reasons)[number];

/** Where to look for terms, by the host class the source sits on. */
const resolvers: Record<SourceClass, string> = {
  "europepmc-api": "europepmc-permissions",
  pmc: "europepmc-permissions",
  arxiv: "arxiv-api",
  "preprint-server": "preprint-api-license-field",
  publisher: "crossref-license",
  "code-repository": "repository-licence-at-commit",
  "model-hub": "model-card-front-matter",
  "data-repository": "record-rights-field",
  "other-web": "retrieved-page",
};

export interface TriageRow {
  source_id: string;
  reason: Reason;
  resolver: string;
  host: string;
  publication_status: string;
  doi: string;
  url: string;
  licence: string;
}

const text = (value: unknown): string => (typeof value === "string" && value.trim() ? value.trim() : "");

const hostOf = (url: string): string => {
  try {
    return new URL(url).hostname.toLowerCase();
  } catch {
    return "";
  }
};

/** Every source needing a licence determination, sorted by id.
 *
 * A source whose missing_metadata.licence reason is inapplicable is left out:
 * a curator's factual receipt is not a third party's work and no licence
 * applies to it. Everything else blank is in the queue, including a recorded
 * unreported, because the source page stating nothing is not the end of the
 * search: Crossref, Unpaywall and a repository LICENSE are still to ask. */
export function buildTriage(root = "."): TriageRow[] {
  const map = readLicenceMap(root);
  const rows: TriageRow[] = [];
  for (const line of fs.readFileSync(sourcesPath(root), "utf8").split("\n")) {
    if (!line.trim()) continue;
    const record = JSON.parse(line) as { id: string; kind: string; attributes?: Record<string, unknown> };
    if (record.kind !== "source") continue;
    const attributes = record.attributes ?? {};
    const licence = text(attributes.licence);
    const missing = (attributes.missing_metadata ?? {}) as Record<string, { reason?: string }>;
    let reason: Reason | null = null;
    if (licence) {
      const row = map.get(licence);
      if (!row)
        throw new Error(
          `No row in data/archive/licence-map.tsv for the licence string "${licence}" (source ${record.id}). ` +
            "Add a reviewed row before regenerating the queue.",
        );
      if (row.basis === "unresolved") reason = "string-unresolved";
      else if (row.basis === "conflicting") reason = "string-conflicting";
    } else {
      const recorded = text(missing.licence?.reason);
      if (recorded === "inapplicable") continue;
      if (recorded === "unreported") reason = "missing-unreported";
      else if (recorded === "unavailable") reason = "missing-unavailable";
      else if (recorded === "unextracted") reason = "missing-unextracted";
      else reason = "no-licence-recorded";
    }
    if (!reason) continue;
    const url = text(attributes.artifact_url) || text(attributes.url);
    const host = hostOf(url);
    rows.push({
      source_id: record.id,
      reason,
      resolver: host ? resolvers[sourceClassOf(host)] : text(attributes.doi) ? "crossref-license" : "no-url-recorded",
      host,
      publication_status: text(attributes.publication_status),
      doi: text(attributes.doi),
      url,
      licence,
    });
  }
  rows.sort((a, b) => (a.source_id < b.source_id ? -1 : a.source_id > b.source_id ? 1 : 0));
  return rows;
}

const columns: (keyof TriageRow)[] = ["source_id", "reason", "resolver", "host", "publication_status", "doi", "url", "licence"];

export function render(rows: TriageRow[], date: string): string {
  const counts = new Map<Reason, number>();
  for (const row of rows) counts.set(row.reason, (counts.get(row.reason) ?? 0) + 1);
  const head = [
    "# Sources needing a licence determination. Generated, never hand written.",
    "#   npx tsx scripts/licence/triage.ts",
    `# Generated ${date} from data/entities/sources.jsonl and data/archive/licence-map.tsv.`,
    `# ${rows.length} sources in the queue.`,
    ...reasons.filter((reason) => counts.has(reason)).map((reason) => `#   ${reason.padEnd(22)} ${counts.get(reason)}`),
    "# A source here is still fetched and still stored. Its bytes are private until the",
    "# determination is made. See docs/source-preservation.md.",
    columns.join("\t"),
  ];
  const body = rows.map((row) => columns.map((column) => row[column]).join("\t"));
  return `${[...head, ...body].join("\n")}\n`;
}

function main(): void {
  const { values } = parseArgs({
    options: {
      root: { type: "string" },
      date: { type: "string" },
      out: { type: "string" },
      stdout: { type: "boolean" },
    },
  });
  const root = values.root ?? ".";
  const date = values.date ?? new Date().toISOString().slice(0, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) throw new Error(`--date must be YYYY-MM-DD, not "${date}"`);
  const rows = buildTriage(root);
  const body = render(rows, date);
  if (values.stdout) {
    process.stdout.write(body);
    return;
  }
  const file = values.out ?? path.join(root, "maintenance/reports", `licence-triage-${date}.tsv`);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, body);
  const counts = new Map<Reason, number>();
  for (const row of rows) counts.set(row.reason, (counts.get(row.reason) ?? 0) + 1);
  console.log(`${file}: ${rows.length} sources`);
  for (const reason of reasons) if (counts.has(reason)) console.log(`  ${reason.padEnd(22)} ${counts.get(reason)}`);
}

if (process.argv[1] && import.meta.url === `file://${process.argv[1]}`) main();
