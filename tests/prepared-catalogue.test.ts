import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterAll, describe, expect, it } from "vitest";
import { buildRelease } from "../scripts/omics/release";
import { buildPreparedCatalogue } from "../scripts/serving/sqlite";
import { checkDiscrepancyParity, checkParity } from "../scripts/serving/parity";
import { gunzipSync, gzipSync } from "node:zlib";
import { openPreparedCatalogue } from "../shared/omics/prepared-catalogue";
import { decodeRecords, unpackEvidence } from "../shared/omics/serving-codec";
import { normaliseDiscrepancies } from "../shared/omics/discrepancies";
import { records } from "./helpers/records";
const { DatabaseSync } = process.getBuiltinModule("node:sqlite");

const sum = (kinds: Map<string, Set<string>>) => [...kinds.values()].reduce((total, ids) => total + ids.size, 0);
const snapshot = buildRelease(records, "2026-10-07T00:00:00Z", { entity_schema_version: "1.1" }).snapshot;
const directory = fs.mkdtempSync(path.join(os.tmpdir(), "prepared-"));
const file = path.join(directory, "catalogue.sqlite");
const counts = buildPreparedCatalogue({
  snapshot,
  catalogueBytes: Buffer.from(JSON.stringify(snapshot)),
  generatorSha256: "0".repeat(64),
  file,
});
afterAll(() => fs.rmSync(directory, { recursive: true, force: true }));

describe("prepared release file", () => {
  it("holds every public record, detail, result row and evidence table", () => {
    const visible = snapshot.records.filter((record) => record.status !== "excluded");
    expect(counts.records).toBe(visible.length);
    expect(counts.details).toBe(visible.length);
    expect(counts.result_rows).toBe(visible.filter((record) => record.kind === "result").length);
  });

  it("answers exactly as the live query engine", () => {
    expect(checkParity(snapshot, file)).toBeGreaterThan(1000);
  });

  it("stores each record once and refers to it from details and result rows", () => {
    const db = new DatabaseSync(file, { readOnly: true });
    const unzip = (gz: Uint8Array) => gunzipSync(gz).toString("utf8");
    const row = db.prepare("SELECT gz FROM result_rows LIMIT 1").get() as { gz: Uint8Array };
    const detail = db.prepare("SELECT gz FROM details WHERE id = (SELECT result_id FROM result_rows LIMIT 1)").get() as { gz: Uint8Array };
    db.close();
    expect(JSON.parse(unzip(row.gz)).result).toEqual({ $r: expect.any(String) });
    expect(JSON.parse(unzip(detail.gz)).record).toEqual({ $r: expect.any(String) });
  });

  it("still reads a contract 2 file, the form earlier releases were published in", () => {
    const copy = path.join(directory, "contract-2.sqlite");
    fs.copyFileSync(file, copy);
    const db = new DatabaseSync(copy);
    const unzip = (gz: Uint8Array) => JSON.parse(gunzipSync(gz).toString("utf8"));
    const zip = (value: unknown) => gzipSync(JSON.stringify(value));
    const blobValue = (key: string) =>
      unzip((db.prepare("SELECT value FROM blobs WHERE key = ?").get(key) as { value: Uint8Array }).value);
    const byId = new Map(
      (db.prepare("SELECT id, gz FROM records").all() as { id: string; gz: Uint8Array }[]).map((row) => [row.id, unzip(row.gz)]),
    );
    const lookup = (id: string) => byId.get(id) || null;
    const sources = blobValue("evidence_sources");
    const base = blobValue("use_case_base");
    const listEntries = blobValue("list_entries") as { record: { id: string } }[];
    db.exec("BEGIN");
    db.exec("ALTER TABLE records ADD COLUMN json TEXT");
    for (const [id, record] of byId) db.prepare("UPDATE records SET json = ? WHERE id = ?").run(JSON.stringify(record), id);
    db.exec("ALTER TABLE records DROP COLUMN gz");
    for (const [table, key] of [["details", "id"], ["result_rows", "result_id"]])
      for (const row of db.prepare(`SELECT ${key} AS id, gz FROM ${table}`).all() as { id: string; gz: Uint8Array }[])
        db.prepare(`UPDATE ${table} SET gz = ? WHERE ${key} = ?`).run(zip(decodeRecords(unzip(row.gz), lookup)), row.id);
    for (const row of db.prepare("SELECT record_id AS id, gz FROM evidence").all() as { id: string; gz: Uint8Array }[])
      db.prepare("UPDATE evidence SET gz = ? WHERE record_id = ?").run(
        zip(unpackEvidence(unzip(row.gz), byId.get(row.id), snapshot.release_id, sources)),
        row.id,
      );
    db.prepare("UPDATE blobs SET value = ? WHERE key = 'list_entries'").run(
      zip(listEntries.map((entry) => ({ ...entry, record: byId.get(entry.record.id) }))),
    );
    db.prepare("INSERT INTO blobs VALUES ('use_cases', ?)").run(zip({ ...base, mappings: [], results: [], sources: [] }));
    db.exec("DELETE FROM blobs WHERE key IN ('use_case_base', 'evidence_sources'); DROP TABLE use_case_entries");
    db.prepare("UPDATE meta SET value = '2.0' WHERE key = 'serving_contract_version'").run();
    db.exec("COMMIT");
    db.close();
    expect(checkParity(snapshot, copy)).toBeGreaterThan(1000);
  });

  describe("source records", () => {
    // Brute force: every source ID anywhere in a record other than its own ID,
    // and, for a result, in its evaluation's sources (the result row shows them).
    const visible = snapshot.records.filter((record) => record.status !== "excluded");
    const byId = new Map(visible.map((record) => [record.id, record]));
    const sourceIds = new Set(visible.filter((record) => record.kind === "source").map((record) => record.id));
    const strings = (value: unknown): string[] =>
      typeof value === "string" ? [value]
        : Array.isArray(value) ? value.flatMap(strings)
        : value && typeof value === "object" ? Object.values(value).flatMap(strings) : [];
    const scan = new Map<string, Map<string, Set<string>>>();
    for (const record of visible) {
      const { id, ...rest } = record;
      const found = strings(rest);
      if (record.kind === "result") {
        const evaluation = byId.get(record.links.find((link) => link.relation === "evaluation")?.target_id || "");
        if (evaluation) found.push(...evaluation.source_ids, ...strings(evaluation.attributes.profile), ...strings(evaluation.attributes.run_guide));
      }
      for (const sourceId of new Set(found.filter((value) => sourceIds.has(value) && value !== id))) {
        const kinds = scan.get(sourceId) || new Map<string, Set<string>>();
        kinds.set(record.kind, (kinds.get(record.kind) || new Set()).add(id));
        scan.set(sourceId, kinds);
      }
    }
    const prepared = openPreparedCatalogue(file);
    afterAll(() => prepared.close());
    // Every ID of one kind, read a page at a time.
    const allPages = (id: string, kind: string, limit: number) => {
      const ids: string[] = [];
      let cursor: string | undefined;
      do {
        const page = prepared.sourceRecords({ id, kind, limit, ...(cursor ? { cursor } : {}) }).pages[kind];
        expect(page.range_start).toBe(page.items.length ? ids.length + 1 : 0);
        ids.push(...page.items);
        cursor = page.next_cursor || undefined;
      } while (cursor);
      return ids;
    };

    it("lists every source that has citing records, and no other", () => {
      const listed = [...sourceIds].filter((id) => prepared.sourceRecords({ id, limit: 1 }).total > 0).sort();
      expect(listed).toEqual([...scan.keys()].sort());
      expect(listed.length).toBeGreaterThan(1000);
    });

    it("matches a brute-force scan of the store", () => {
      const busiest = [...scan].sort((a, b) => sum(b[1]) - sum(a[1])).slice(0, 5).map(([id]) => id);
      const sample = [...new Set([...busiest, ...[...scan.keys()].filter((_, index) => index % 17 === 0)])];
      for (const id of sample) {
        const expected = scan.get(id)!;
        const answer = prepared.sourceRecords({ id, limit: 100 });
        expect(answer.counts, id).toEqual(Object.fromEntries([...expected].map(([kind, ids]) => [kind, ids.size])));
        for (const [kind, ids] of expected) expect(new Set(allPages(id, kind, 100)), `${id} ${kind}`).toEqual(ids);
      }
    });

    it("pages every kind without gaps or repeats, results by evaluation then metric", () => {
      const [id] = [...scan].sort((a, b) => (b[1].get("result")?.size || 0) - (a[1].get("result")?.size || 0))[0];
      const counts = prepared.sourceRecords({ id }).counts;
      for (const [kind, count] of Object.entries(counts)) {
        const ids = allPages(id, kind, 7);
        expect(ids.length).toBe(count);
        expect(new Set(ids).size).toBe(count);
        expect(ids).toEqual(allPages(id, kind, 100));
      }
      const rows: { id: string; evaluation: { id: string } | null; metric: string }[] = [];
      let cursor: string | undefined;
      do {
        const page = prepared.sourceResults({ id, limit: 30, ...(cursor ? { cursor } : {}) });
        rows.push(...page.items);
        cursor = page.next_cursor || undefined;
      } while (cursor);
      expect(rows.map((row) => row.id)).toEqual(allPages(id, "result", 100));
      // Each evaluation's results are contiguous.
      const runs = rows.map((row) => row.evaluation?.id).filter((value, index, list) => value !== list[index - 1]);
      expect(new Set(runs).size).toBe(runs.length);
      const first = prepared.sourceResults({ id, limit: 1 }).items[0];
      const record = prepared.record(first.id)!;
      expect(first).toMatchObject({ metric: record.attributes.metric, printed_value: record.attributes.printed_value });
      expect(first.tested.length + first.datasets.length).toBeGreaterThan(0);
    });

    it("reads a contract 3.0 file as having no source records", () => {
      const copy = path.join(directory, "contract-3.0.sqlite");
      fs.copyFileSync(file, copy);
      const db = new DatabaseSync(copy);
      db.exec("DROP TABLE source_records");
      db.prepare("UPDATE meta SET value = '3.0' WHERE key = 'serving_contract_version'").run();
      db.close();
      const old = openPreparedCatalogue(copy);
      const [id] = scan.keys();
      expect(old.sourceRecords({ id })).toEqual({ release_id: snapshot.release_id, source_id: id, counts: {}, total: 0, pages: {} });
      expect(old.sourceResults({ id }).items).toEqual([]);
      old.close();
    });
  });

  it("refuses a file with an unsupported serving contract", () => {
    const copy = path.join(directory, "other.sqlite");
    fs.copyFileSync(file, copy);
    const db = new DatabaseSync(copy);
    db.prepare("UPDATE meta SET value = '9.0' WHERE key = 'serving_contract_version'").run();
    db.close();
    expect(() => openPreparedCatalogue(copy)).toThrow("Unsupported prepared release contract");
  });
});

describe("discrepancies between studies (3.3)", () => {
  const results = snapshot.records.filter((r) => r.kind === "result" && r.status !== "excluded").slice(0, 4).map((r) => r.id);
  const finding = (id: string, severity: string, extra: Record<string, unknown> = {}) => ({
    id, rule: "ordering-reversal", label: `Finding ${id}`, summary: "One study ranks the pair the other way.",
    severity, scope: "same-protocol", identity_basis: "reviewed", review_state: "open", review_claim: null,
    settled: false, resolution: {}, systems: ["model-a", "model-b"], consensus_higher: "model-a", reference_system: null,
    outlier_sources: ["source-x"], consensus_sources: ["source-y"], outlier_results: [results[0]],
    consensus_results: [results[1], results[2]], numbers: { outlier_reversals: 2 }, ...extra,
  });
  const file2 = path.join(directory, "discrepancies.sqlite");
  const findings = normaliseDiscrepancies({
    release_id: snapshot.release_id, schema_version: 2, rules: { version: 3 }, excluded: { disputed: 1, concern: 2 },
    discrepancies: [
      finding("discrepancy-low", "low"),
      finding("discrepancy-conflict", "low", {
        rule: "two-study-conflict", scope: "different-task", listing: "review", outlier_sources: [], consensus_sources: [],
        outlier_results: [], consensus_results: [], party_sources: ["source-x", "source-y"], party_results: [results[3]],
      }),
      finding("discrepancy-high", "high", {
        review_state: "awaiting-correction", review_claim: "claim-r2", previous_ids: ["discrepancy-old"],
        actions: [
          { revision: 2, claim_id: "claim-r2", action: "awaiting-correction", state: "awaiting-correction", date: "2026-10-22", next_check: "2026-11-10" },
          { revision: 1, claim_id: "claim-r1", action: "reported-upstream", state: "reported-upstream", date: "2026-10-19", report_url: "https://example.org/issue/2" },
        ],
      }),
    ],
  });
  buildPreparedCatalogue({
    snapshot, catalogueBytes: Buffer.from(JSON.stringify(snapshot)), discrepancies: findings, generatorSha256: "0".repeat(64), file: file2,
  });
  const prepared = openPreparedCatalogue(file2);
  afterAll(() => prepared.close());

  it("lists findings most severe first, with counts and filters", () => {
    const page = prepared.discrepancies();
    expect(page.items.map((d) => d.id)).toEqual(["discrepancy-high", "discrepancy-low", "discrepancy-conflict"]);
    expect(page.counts.severity).toEqual({ high: 1, low: 2 });
    expect(prepared.discrepancies({ listing: "review" }).items.map((d) => d.id)).toEqual(["discrepancy-conflict"]);
    expect(prepared.discrepancies({ settled: "open", severity: "low" }).total).toBe(2);
    const first = prepared.discrepancies({ limit: 1 });
    expect(prepared.discrepancies({ limit: 1, cursor: first.next_cursor! }).items[0].id).toBe("discrepancy-low");
    expect(prepared.discrepancyRules()).toEqual({ rules: { version: 3 }, excluded: { disputed: 1, concern: 2 } });
  });

  it("holds exactly the knowledge-graph build's findings", () => {
    expect(checkDiscrepancyParity(file2, findings)).toBeGreaterThan(5);
  });

  it("returns a finding's follow-up actions oldest first, also under an earlier ID", () => {
    const d = prepared.discrepancy("discrepancy-old")!;
    expect(d.id).toBe("discrepancy-high");
    expect(d.actions.map((a) => a.action)).toEqual(["reported-upstream", "awaiting-correction"]);
    expect(prepared.discrepancies().items[0]).toMatchObject({ actions: 2, next_check: "2026-11-10", last_action_date: "2026-10-22" });
  });

  it("finds the findings a result or a system takes part in", () => {
    const by = prepared.contestedBy([results[0], results[1], results[3]]);
    expect(by[results[0]].map((x) => x.role)).toEqual(["outlier", "outlier"]);
    expect(by[results[1]][0]).toMatchObject({ role: "consensus", discrepancy: { id: "discrepancy-high" } });
    expect(by[results[3]].map((x) => [x.role, x.discrepancy.id])).toEqual([["party", "discrepancy-conflict"]]);
    expect(prepared.discrepanciesForSystem("model-a").map((d) => d.id)).toEqual(["discrepancy-high", "discrepancy-low", "discrepancy-conflict"]);
  });

  it("reads a schema 1 file's latest review as one action", () => {
    const old = normaliseDiscrepancies({
      release_id: "r", rules: {},
      discrepancies: [finding("d", "medium", { review_state: "reported-upstream", review_claim: "c", resolution: { report_url: "https://example.org", reported_on: "2026-10-19" } })],
    });
    expect(old.discrepancies[0].actions).toEqual([expect.objectContaining({ claim_id: "c", state: "reported-upstream", date: "2026-10-19", report_url: "https://example.org" })]);
  });

  it("refuses findings built for another release", () => {
    expect(() => buildPreparedCatalogue({
      snapshot, catalogueBytes: Buffer.from("{}"), discrepancies: { ...findings, release_id: "other" },
      generatorSha256: "0".repeat(64), file: path.join(directory, "wrong.sqlite"),
    })).toThrow("rebuild the knowledge graph");
  });

  it("serves no findings from a file built without the knowledge graph", () => {
    const plain = openPreparedCatalogue(file);
    expect(plain.hasDiscrepancies()).toBe(false);
    expect(plain.discrepancies().total).toBe(0);
    expect(plain.contestedBy(results)).toEqual({});
    plain.close();
  });
});
