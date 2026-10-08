import fs from "node:fs";
import { gunzipSync } from "node:zlib";
import { createHash } from "node:crypto";
import { XMLParser } from "fast-xml-parser";
import { describe, expect, it } from "vitest";
import type { RecordEntry } from "../scripts/omics/schema";

// Independent scientific oracle: primary XML, not generated scores or builder IDs.
const ROOT = "data/omics/use-case-coverage-amp-20261007";
const SOURCE = "evidence-expansion-dna-foundation-models-2025-5d8ca9bc";
const xmlBytes = gunzipSync(fs.readFileSync("data/omics/amp-coverage-20261007/feng/fulltext.xml.gz"));
type Node = any;
const xml = new XMLParser({ ignoreAttributes: false, parseTagValue: false }).parse(xmlBytes.toString());
const array = (x: Node): Node[] => x === undefined ? [] : Array.isArray(x) ? x : [x];
function text(x: Node): string {
  if (x === undefined) return "";
  if (typeof x !== "object") return String(x);
  return Object.entries(x).filter(([k]) => !k.startsWith("@_")).map(([, v]) => array(v).map(text).join("")).join("").trim();
}
function find(node: Node, id: string): Node {
  if (!node || typeof node !== "object") return undefined;
  if (node["@_id"] === id) return node;
  for (const value of Object.values(node)) for (const child of array(value)) {
    const found = find(child, id); if (found) return found;
  }
}
type Cell = { table: number; model: string; task: string; metric: string; printed: string };
function primaryCells(): Cell[] {
  const cells: Cell[] = [];
  for (const table of [1, 2]) {
    const t = find(xml, `Tab${table}`).table;
    const headers = array(t.thead.tr.th).map(text).slice(1);
    for (const tr of array(t.tbody.tr)) {
      const row = array(tr.td).map(text);
      const task = table === 1 ? row[0] : row[0].replace("Promoter Arabidopsis ", "");
      if (!(["Acceptor", "Donor", "TATA", "NonTATA"].includes(task))) continue;
      headers.forEach((model, i) => cells.push({ table, model, task, metric: "AUC", printed: row[i + 1] }));
    }
  }
  for (const tr of array(find(xml, "Tab5").table.tbody.tr)) {
    const row = array(tr.td).map(text);
    ["AUC", "Cohen's d"].forEach((metric, i) => cells.push({ table: 5, model: row[0], task: "variant", metric, printed: row[i + 1] }));
  }
  let metric = "";
  for (const tr of array(find(xml, "Tab6").table.tbody.tr)) {
    const td = array(tr.td); const row = td.map(text);
    if (row.length === 6) {
      metric = row.shift()!.replace(/’/g, "'");
      expect(Number(td[0]["@_rowspan"])).toBe(12); // Metric block applies to exactly twelve model rows.
    }
    const model = row.shift()!;
    ["eQTL", "sQTL", "paQTL", "ipaQTL"].forEach((task, i) => cells.push({ table: 6, model, task, metric, printed: row[i] }));
  }
  return cells;
}
const records: RecordEntry[] = ["clinical", "research", "experimental"].flatMap(lane =>
  fs.readFileSync(`${ROOT}/${lane}/records.jsonl`, "utf8").split("\n").filter(Boolean).map(line => JSON.parse(line)));
const byId = new Map(records.map(r => [r.id, r]));
const feng = records.filter(r => r.source_ids.includes(SOURCE));
const evaluations = feng.filter(r => r.kind === "evaluation");
const results = feng.filter(r => r.kind === "result");
function linked(r: RecordEntry, relation: string): RecordEntry {
  const links = r.links.filter(l => l.relation === relation);
  expect(links, `${r.id}: exactly one ${relation}`).toHaveLength(1);
  const target = byId.get(links[0].target_id);
  expect(target, `${r.id}: missing linked ${relation}`).toBeDefined();
  return target!;
}
function taskOf(e: RecordEntry): string {
  const p = linked(e, "protocol");
  const task = String(p.attributes.task);
  for (const q of ["ipaQTL", "paQTL", "sQTL", "eQTL"]) if (task.includes(q)) return q;
  if (/pathogenic/i.test(task)) return "variant";
  for (const q of ["NonTATA", "TATA", "Acceptor", "Donor"]) if (task.includes(q)) return q;
  throw Error(`Unknown exact Feng task: ${task}`);
}
const prose = (r: RecordEntry) => JSON.stringify({ name: r.name, description: r.description, attributes: r.attributes });
const compact = (s: string) => s.replace(/,/g, "");

describe("AMP primary-source scientific regressions", () => {
  it("pins independently checked primary XML and preserves all 138 model/task/metric cells, including eight negatives", () => {
    expect(createHash("sha256").update(xmlBytes).digest("hex")).toBe("5d8ca9bcf88cc1b38ad667906a2e4699b1aefa6d31c6f49259784930353f3202");
    const expected = primaryCells();
    expect(expected).toHaveLength(138);
    expect(expected.filter(c => /^[−-]/.test(c.printed))).toHaveLength(8);
    expect(results).toHaveLength(138);
    const consumed = new Set<string>();
    for (const cell of expected) {
      const match = results.filter(r => {
        const e = linked(r, "evaluation"); const c = linked(e, "configuration");
        return c.attributes.reported_name === cell.model && taskOf(e) === cell.task &&
          r.attributes.unit === cell.metric && String(r.attributes.source_locator).startsWith(`Table ${cell.table},`);
      });
      expect(match, JSON.stringify(cell)).toHaveLength(1);
      const r = match[0];
      expect(r.attributes.printed_value, JSON.stringify(cell)).toBe(cell.printed);
      expect(r.attributes.numeric_value).toBe(cell.printed.replace(/−/g, "-"));
      if (cell.metric === "Cohen's d") expect(r.attributes.metric_direction).toBe("unknown");
      expect(consumed.has(r.id)).toBe(false); consumed.add(r.id);
    }
    expect(consumed.size).toBe(138);
  });

  it("gives 79 evaluations one exact task and a task-specific fitted head and population", () => {
    expect(evaluations).toHaveLength(79);
    const counts: Record<string, number> = {};
    const protocolTasks = new Map<string, Set<string>>(); const configTasks = new Map<string, Set<string>>();
    for (const e of evaluations) {
      const task = taskOf(e); counts[task] = (counts[task] ?? 0) + 1;
      const p = linked(e, "protocol"); const c = linked(e, "configuration"); linked(e, "dataset");
      for (const [map, id] of [[protocolTasks, p.id], [configTasks, c.id]] as const) {
        if (!map.has(id)) map.set(id, new Set()); map.get(id)!.add(task);
      }
      const comparison = e.attributes.comparison as Record<string, unknown>;
      expect(String(comparison.adaptation)).toMatch(/random.?forest/i);
      expect(String(comparison.split)).not.toBe("null");
      const ownResults = results.filter(r => r.links.some(l => l.relation === "evaluation" && l.target_id === e.id));
      expect(ownResults.length).toBe(task === "variant" || task.endsWith("QTL") ? 2 : 1);
    }
    expect(counts).toEqual({ Acceptor: 5, Donor: 5, TATA: 5, NonTATA: 5, variant: 11, eQTL: 12, sQTL: 12, paQTL: 12, ipaQTL: 12 });
    for (const set of [...protocolTasks.values(), ...configTasks.values()]) expect(set.size).toBe(1);
  });

  it("keeps each QTL task's counts and generated short/long population distinct from consumed model inputs", () => {
    const prefilter: Record<string, number> = { eQTL: 1896, sQTL: 540, paQTL: 142, ipaQTL: 116 };
    for (const [task, count] of Object.entries(prefilter)) {
      const group = evaluations.filter(e => taskOf(e) === task);
      const datasets = [...new Set(group.map(e => linked(e, "dataset").id))];
      expect(datasets, task).toHaveLength(2); // AlphaGenome crops the long population; no third scored population.
      for (const id of datasets) {
        const d = byId.get(id)!; const description = compact(prose(d));
        expect(description).toContain(String(count)); expect(description).toMatch(/pre[- ](?:window[- ]filter|filter)/i);
        for (const snpCount of [22239, 17398, 22222, 17374]) expect(description).not.toContain(String(snpCount));
        expect(description).toMatch(/6000|196608/);
        expect(description).toMatch(/chromosom/i);
        expect(description).toMatch(/post[- ](?:window[- ])?filter|scored denominator/i);
      }
      const alpha = group.find(e => linked(e, "configuration").attributes.reported_name === "AlphaGenome, output tracks*")!;
      const enformer = group.find(e => linked(e, "configuration").attributes.reported_name === "Enformer, output tracks*")!;
      expect(linked(alpha, "dataset").id).toBe(linked(enformer, "dataset").id);
      expect(compact(prose(linked(alpha, "dataset")))).toContain("196608");
      const modelMetadata = compact(prose(linked(alpha, "configuration")) + prose(alpha));
      expect(modelMetadata).toMatch(/(?:input|consum)[^\.]{0,100}131072|131072[^\.]{0,100}(?:input|consum)/i);
      expect(modelMetadata).toMatch(/(?:output|averag|aggregation)[^\.]{0,100}2048|2048[^\.]{0,100}(?:output|averag|aggregation)/i);
      expect(modelMetadata).not.toMatch(/Actual consumed central window: 2048/);
    }
  });

  it("retains the source's specialised genomic comparator roles", () => {
    for (const e of evaluations) {
      const c = linked(e, "configuration"); const model = String(c.attributes.reported_name);
      const comparator = /^(Sei|Enformer|AlphaGenome)/.test(model);
      expect(c.attributes.foundation_model_eligible, model).toBe(!comparator);
      if (comparator) expect(c.facets.method_types ?? []).not.toContain("foundation_model");
    }
  });

});
