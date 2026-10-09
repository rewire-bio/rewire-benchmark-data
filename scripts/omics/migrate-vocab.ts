/** Migrate free-text values in the canonical store to controlled-vocabulary keys (issue #42).
 *
 * Reads the reviewed lookup tables in data/vocab/migration/ (one CSV per scheme:
 * source_string, concept, match, keep_detail, note), rewrites every record in place and
 * records each changed record in data/provenance/records.jsonl. A value that no table covers
 * stops the migration. Detail a concept cannot hold (a counted entity, a scale, a reviewer's
 * role) is kept in a note field next to the value. It runs once: some concept keys are also
 * source strings for other concepts, so a second run would remap migrated values. It refuses
 * to run when the provenance log already records it.
 *
 * Usage: npm run vocab:migrate -- <review.md> */
import fs from "node:fs";
import path from "node:path";
import { recordChanges, recordFiles } from "./records";
import { loadSchemes } from "./vocab";

export const migrationDir = "data/vocab/migration";
/** keep_detail: text a concept cannot hold, kept in a note field. qualifier (metric table only):
 * what distinguishes rows that share a metric concept, kept in attributes.metric_qualifier. */
type Row = { source_string: string; concept: string; match: string; keep_detail: string; note: string; qualifier?: string };
type StoreRecord = { id: string; kind: string; facets: Record<string, string[]>; attributes: Record<string, unknown> };

/** Minimal RFC 4180 reader: quoted fields, doubled quotes, commas and newlines inside quotes. */
export function readCsv(text: string): Record<string, string>[] {
  const rows: string[][] = [];
  let field = "", row: string[] = [], quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') quoted = false;
      else field += c;
    } else if (c === '"') quoted = true;
    else if (c === ",") { row.push(field); field = ""; }
    else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(field); field = "";
      if (row.some((value) => value !== "")) rows.push(row);
      row = [];
    } else field += c;
  }
  if (field !== "" || row.length) { row.push(field); rows.push(row); }
  const [header, ...body] = rows;
  return body.map((values) => Object.fromEntries(header.map((name, i) => [name, values[i] ?? ""])));
}

export function readTable(scheme: string, root = "."): Map<string, Row> {
  const file = path.join(root, migrationDir, `${scheme}.csv`);
  return new Map((readCsv(fs.readFileSync(file, "utf8")) as Row[]).map((row) => [row.source_string, row]));
}

type Override = { [column: string]: string };
const readOverrides = (name: string, root = "."): Override[] => {
  const file = path.join(root, migrationDir, `${name}.csv`);
  return fs.existsSync(file) ? readCsv(fs.readFileSync(file, "utf8")) : [];
};

const conceptsOf = (row: Row): string[] => row.concept.split(";").map((value) => value.trim()).filter(Boolean);
const single = (keys: string[]) => (keys.length === 1 ? keys[0] : keys);

export function migrateRecord(
  record: StoreRecord,
  tables: Map<string, Map<string, Row>>,
  overrides: { unit: Override[]; area: Override[] },
): boolean {
  const before = JSON.stringify(record);
  const a = record.attributes;
  const lookup = (scheme: string, value: unknown, where: string): Row => {
    if (typeof value !== "string") throw new Error(`${record.id}: ${where} is not a string`);
    const row = tables.get(scheme)!.get(value);
    if (row) return row;
    throw new Error(`${record.id}: ${where} ${JSON.stringify(value)} is not in ${migrationDir}/${scheme}.csv`);
  };
  const addNote = (target: Record<string, unknown>, field: string, text: string) => {
    if (!text) return;
    const existing = typeof target[field] === "string" ? (target[field] as string) : "";
    if (!existing.split("; ").includes(text)) target[field] = existing ? `${existing}; ${text}` : text;
  };
  const scalar = (scheme: string, field: string, noteField?: string, target: Record<string, unknown> = a) => {
    if (target[field] === null || target[field] === undefined) return;
    const row = lookup(scheme, target[field], field);
    if (!row) return;
    target[field] = single(conceptsOf(row));
    if (noteField) addNote(target, noteField, row.keep_detail);
  };
  const facet = (scheme: string, name: string) => {
    const values = record.facets[name];
    if (!values) return;
    const out: string[] = [];
    for (const value of values) {
      const row = lookup(scheme, value, `facets.${name}`);
      let keys = row ? conceptsOf(row) : [value];
      if (scheme === "area" && keys.length > 1) {
        const rule = overrides.area.find((o) => o.source_string === value && record.id.startsWith(o.id_prefix));
        if (!rule) throw new Error(`${record.id}: area ${value} needs a per-record rule in area-by-record.csv`);
        keys = [rule.concept];
      }
      for (const key of keys) if (!out.includes(key)) out.push(key);
    }
    record.facets[name] = out;
  };

  // The metric comes first: unit overrides are keyed by the migrated metric.
  if (a.metric !== null && a.metric !== undefined) {
    const row = lookup("metric", a.metric, "metric");
    if (row) {
      a.metric = single(conceptsOf(row));
      if (row.qualifier) a.metric_qualifier = row.qualifier;
    }
  }
  if (a.unit !== null && a.unit !== undefined) {
    const unitText = a.unit;
    const rule = overrides.unit.find((o) => o.unit_string === unitText && o.metric === a.metric);
    if (rule) {
      a.unit = rule.unit;
      addNote(a, "unit_detail", rule.keep_detail);
    } else scalar("unit", "unit", "unit_detail");
  }
  scalar("direction", "metric_direction");
  facet("area", "areas");
  facet("method-type", "method_types");
  facet("context", "contexts");
  if (record.facets.domain) delete record.facets.domain; // duplicated areas; retired
  scalar("method-type", "method_type");
  scalar("publication-status", "publication_status");
  scalar("origin", "origin");
  scalar("entity-level", "entity_level");
  scalar("baseline-type", "baseline_type");
  scalar("configuration-type", "configuration_type");
  const review = a.review;
  if (review && typeof review === "object" && !Array.isArray(review)) {
    const r = review as Record<string, unknown>;
    scalar("review-method", "method", "method_note", r);
    scalar("agent", "reviewer", "reviewer_note", r);
    scalar("agent", "actor", "reviewer_note", r);
  }
  return JSON.stringify(record) !== before;
}

export const migratedSchemes = [
  "metric", "unit", "direction", "area", "method-type", "context", "publication-status", "origin",
  "entity-level", "baseline-type", "configuration-type", "review-method", "agent",
];

if (process.argv[1]?.endsWith("migrate-vocab.ts")) {
  const review = process.argv[2];
  if (!review || !fs.existsSync(review)) {
    console.error("Usage: npm run vocab:migrate -- <review.md>  (the review must exist)");
    process.exit(1);
  }
  if (fs.readFileSync("data/provenance/records.jsonl", "utf8").includes(`"inputs":"${migrationDir}"`)) {
    console.error(`The vocabulary migration has already been applied (provenance cites ${migrationDir}).`);
    process.exit(1);
  }
  const schemes = loadSchemes();
  const tables = new Map(migratedSchemes.map((scheme) => [scheme, readTable(scheme)]));
  const validKeys = new Map(migratedSchemes.map((scheme) => [scheme, new Set(schemes.get(scheme)!.concepts.keys())]));
  for (const [scheme, table] of tables)
    for (const row of table.values())
      for (const key of conceptsOf(row))
        if (!validKeys.get(scheme)!.has(key)) throw new Error(`${scheme}.csv maps to unknown concept ${key}`);
  const overrides = { unit: readOverrides("unit-by-metric"), area: readOverrides("area-by-record") };
  const changed = new Set<string>();
  const files = new Map(recordFiles().map((file) => [
    file,
    fs.readFileSync(file, "utf8").split("\n").filter(Boolean).map((line) => JSON.parse(line) as StoreRecord),
  ]));
  const byId = new Map([...files.values()].flat().map((record) => [record.id, record]));
  for (const record of byId.values())
    if (migrateRecord(record, tables, overrides)) changed.add(record.id);
  // Curated panels name the metric, unit and qualifier of the results they show; take them
  // from those migrated results so a panel and its rows always agree.
  for (const record of byId.values()) {
    const panels = record.attributes.comparison_panels;
    if (!Array.isArray(panels)) continue;
    const before = JSON.stringify(panels);
    for (const panel of panels as Record<string, unknown>[]) {
      const rows = (panel.result_ids as string[]).map((id) => byId.get(id)?.attributes);
      const first = rows[0];
      if (!first || rows.some((a) => !a || a.metric !== first.metric || a.unit !== first.unit || a.metric_qualifier !== first.metric_qualifier))
        throw new Error(`${record.id}: panel ${String(panel.id)} mixes metrics, units or qualifiers after migration`);
      panel.metric = first.metric;
      panel.unit = first.unit;
      if (first.metric_qualifier) panel.metric_qualifier = first.metric_qualifier;
      else delete panel.metric_qualifier;
    }
    if (JSON.stringify(panels) !== before) changed.add(record.id);
  }
  for (const [file, records] of files)
    if (records.some((record) => changed.has(record.id)))
      fs.writeFileSync(file, records.map((record) => JSON.stringify(record) + "\n").join(""));
  if (changed.size) recordChanges([...changed].sort(), migrationDir, review);
  console.log(`Migrated ${changed.size} records to controlled vocabularies.`);
}
