import fs from "node:fs";
import { describe, it, expect } from "vitest";
import { records, recordsById as byId, readJsonl } from "./helpers/records";
import { publicRecords, type RecordEntry } from "../scripts/omics/schema";
import { createCatalogueQuery } from "../services/omics/src/catalogue-query";
const visible = publicRecords(records);
const query = createCatalogueQuery({
  schema_version: "1.0",
  release_id: "test",
  released_at: "2026-09-17T08:29:06Z",
  coverage: {},
  records: visible,
});
const root = "data/omics/reviews/benchmark-evidence-2026/";
const occurrences = JSON.parse(
  fs.readFileSync(root + "occurrences.json", "utf8"),
) as {
  group_id: string;
  result_id: string;
  source_id: string;
  numeric_value: string | null;
  existing: boolean;
  quarantined: boolean;
}[];
describe("reviewed benchmark paper expansion", () => {
  it("attaches a dated primary-source audit to all 221 original benchmarks and every new exact protocol", () => {
    const audits = readJsonl<any>(root + "search-audit.jsonl");
    expect(audits).toHaveLength(221);
    expect(new Set(audits.map((a) => a.benchmark_id)).size).toBe(221);
    for (const audit of audits) {
      expect(audit.searched_queries.length).toBeGreaterThan(0);
      expect(audit.primary_sources.length).toBeGreaterThan(0);
      const record = byId.get(audit.benchmark_id)!;
      expect(record.attributes.benchmark_research).toBeTruthy();
      for (const id of audit.primary_sources) {
        expect(byId.get(id)?.kind).toBe("source");
        expect(record.source_ids).toContain(id);
      }
    }
  });
  it("accounts for all 1187 source cells and reuses copied observation identities", () => {
    expect(occurrences).toHaveLength(1187);
    expect(new Set(occurrences.map((o) => o.result_id)).size).toBe(1171);
    expect(
      new Set(occurrences.filter((o) => o.existing).map((o) => o.result_id))
        .size,
    ).toBe(26);
    for (const cell of occurrences) {
      const record = byId.get(cell.result_id)!;
      expect(record.source_ids).toContain(cell.source_id);
      if (cell.numeric_value === null)
        expect(record.attributes.numeric_value).toBeNull();
      else
        expect(Number(record.attributes.numeric_value)).toBe(
          Number(cell.numeric_value),
        );
      expect(record.status === "disputed").toBe(cell.quarantined);
    }
  });
  it("publishes one complete source-scoped panel per extracted task without quarantined values or pagination truncation", () => {
    // A census of the whole catalogue, not just the reviewed expansion: 120
    // pages and 223 panels came from that batch, and each task extracted from a
    // paper's comparison table adds one page carrying one panel.
    const pages = visible.filter((r) => r.attributes.comparison_panels);
    expect(pages.length).toBeGreaterThanOrEqual(133);
    const panels = pages.flatMap(
      (r) => query.get({ id: r.id })!.published_comparisons,
    );
    // Every declared panel resolves. A panel can be declared on more than one
    // page, so the ids are compared as sets rather than counted.
    const declared = new Set(
      pages.flatMap((record) =>
        (record.attributes.comparison_panels as { id: string }[]).map(
          (panel) => panel.id,
        ),
      ),
    );
    expect(declared.size).toBeGreaterThanOrEqual(223);
    expect(new Set(panels.map((p) => p.id))).toEqual(declared);
    for (const panel of panels)
      for (const row of panel.rows)
        expect(["source_checked", "reproduced"]).toContain(row.result.status);
    expect(
      panels.some((p) =>
        p.rows.some((r) => r.result.attributes.numeric_value === null),
      ),
    ).toBe(true);
    expect(
      panels.some(
        (p) =>
          p.id.startsWith("part2-genomeocean") &&
          p.metric.toLowerCase().includes("f1"),
      ),
    ).toBe(true);
    for (const model of [
      "transformer",
      "lstm",
      "resnet",
      "bepler",
      "unirep",
      "one-hot",
    ]) {
      const page = query.results({
        id: "discovery-model-tape-" + model,
        limit: 100,
      });
      expect(
        new Set(page.items.flatMap((r) => r.benchmarks.map((b) => b.id))).size,
      ).toBeGreaterThanOrEqual(5);
    }
  });
});
