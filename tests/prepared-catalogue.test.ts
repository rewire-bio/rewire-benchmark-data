import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterAll, describe, expect, it } from "vitest";
import { buildRelease } from "../scripts/omics/release";
import { buildPreparedCatalogue } from "../scripts/serving/sqlite";
import { checkParity } from "../scripts/serving/parity";
import { gunzipSync, gzipSync } from "node:zlib";
import { openPreparedCatalogue } from "../shared/omics/prepared-catalogue";
import { decodeRecords, unpackEvidence } from "../shared/omics/serving-codec";
import { records } from "./helpers/records";
const { DatabaseSync } = process.getBuiltinModule("node:sqlite");

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

  it("refuses a file with an unsupported serving contract", () => {
    const copy = path.join(directory, "other.sqlite");
    fs.copyFileSync(file, copy);
    const db = new DatabaseSync(copy);
    db.prepare("UPDATE meta SET value = '9.0' WHERE key = 'serving_contract_version'").run();
    db.close();
    expect(() => openPreparedCatalogue(copy)).toThrow("Unsupported prepared release contract");
  });
});
