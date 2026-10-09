/** Apply a reviewed correction table to the canonical store.
 *
 * The table is a CSV with columns record_id, field, old_value, new_value, evidence, one row per
 * record and field. field is attributes.<key>, attributes.review.<key> or facets.<name>.
 * - Attribute: old_value must equal the current value (empty means absent); new_value replaces
 *   it (empty removes it).
 * - Facet: old_value names the value to replace (empty adds new_value); new_value is its
 *   replacement (empty removes old_value).
 * Every row is checked against the store before anything is written, so a table drafted against
 * an older state of a record is refused rather than half applied. Changed records are recorded
 * in data/provenance/records.jsonl with the table as input and the review as evidence.
 *
 * Usage: npm run records:correct -- <table.csv> <review.md> */
import fs from "node:fs";
import { readCsv } from "./migrate-vocab";
import { recordChanges, recordFiles } from "./records";

type StoreRecord = { id: string; facets: Record<string, string[]>; attributes: Record<string, unknown> };
export type Correction = { record_id: string; field: string; old_value: string; new_value: string; evidence: string };

export function applyCorrection(record: StoreRecord, row: Correction): void {
  const fail = (why: string) => {
    throw new Error(`${row.record_id} ${row.field}: ${why}`);
  };
  const [section, ...path] = row.field.split(".");
  if (section === "facets" && path.length === 1) {
    const values = [...(record.facets[path[0]] ?? [])];
    if (row.old_value && !values.includes(row.old_value)) fail(`has no value ${JSON.stringify(row.old_value)}`);
    const next = values.flatMap((value) => (value === row.old_value ? (row.new_value ? [row.new_value] : []) : [value]));
    if (!row.old_value) next.push(row.new_value);
    record.facets[path[0]] = [...new Set(next)];
    if (!record.facets[path[0]].length) delete record.facets[path[0]];
    return;
  }
  if (section !== "attributes" || !path.length || path.length > 2) fail("unsupported field");
  let target = record.attributes;
  if (path.length === 2) {
    const nested = target[path[0]];
    if (!nested || typeof nested !== "object" || Array.isArray(nested)) fail(`has no ${path[0]} object`);
    target = nested as Record<string, unknown>;
  }
  const key = path[path.length - 1];
  const current = target[key];
  const shown = current === undefined || current === null ? "" : String(current);
  if (typeof current === "object" && current !== null) fail("is not a scalar value");
  if (shown !== row.old_value) fail(`is ${JSON.stringify(shown)}, the table expects ${JSON.stringify(row.old_value)}`);
  if (row.new_value) target[key] = row.new_value;
  else delete target[key];
}

if (process.argv[1]?.endsWith("apply-corrections.ts")) {
  const [table, review] = process.argv.slice(2);
  if (!table || !review || !fs.existsSync(table) || !fs.existsSync(review)) {
    console.error("Usage: npm run records:correct -- <table.csv> <review.md>  (both must exist)");
    process.exit(1);
  }
  const rows = readCsv(fs.readFileSync(table, "utf8")) as Correction[];
  const files = new Map(
    recordFiles().map((file) => [
      file,
      fs.readFileSync(file, "utf8").split("\n").filter(Boolean).map((line) => JSON.parse(line) as StoreRecord),
    ]),
  );
  const byId = new Map([...files.values()].flat().map((record) => [record.id, record]));
  for (const row of rows) {
    const record = byId.get(row.record_id);
    if (!record) throw new Error(`Unknown record ${row.record_id}`);
    if (!row.evidence.trim()) throw new Error(`${row.record_id} ${row.field}: no evidence`);
    applyCorrection(record, row);
  }
  const changed = new Set(rows.map((row) => row.record_id));
  // Curated panels name the metric, unit and qualifier of the results they show; keep them in
  // step with corrected results, and refuse a correction that would mix them within a panel.
  for (const record of byId.values()) {
    const panels = record.attributes.comparison_panels;
    if (!Array.isArray(panels)) continue;
    const before = JSON.stringify(panels);
    for (const panel of panels as Record<string, unknown>[]) {
      const rows = (panel.result_ids as string[]).map((id) => byId.get(id)?.attributes);
      const first = rows[0];
      if (!first || rows.some((a) => !a || a.metric !== first.metric || a.unit !== first.unit || a.metric_qualifier !== first.metric_qualifier))
        throw new Error(`${record.id}: panel ${String(panel.id)} would mix metrics, units or qualifiers`);
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
  recordChanges([...changed].sort(), table, review);
  console.log(`Applied ${rows.length} corrections to ${changed.size} records.`);
}
