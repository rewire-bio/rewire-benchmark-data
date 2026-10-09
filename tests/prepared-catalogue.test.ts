import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterAll, describe, expect, it } from "vitest";
import { buildRelease } from "../scripts/omics/release";
import { buildPreparedCatalogue } from "../scripts/serving/sqlite";
import { checkParity } from "../scripts/serving/parity";
import { openPreparedCatalogue } from "../services/omics/src/prepared-catalogue";
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

  it("refuses a file with an unsupported serving contract", () => {
    const copy = path.join(directory, "other.sqlite");
    fs.copyFileSync(file, copy);
    const db = new DatabaseSync(copy);
    db.prepare("UPDATE meta SET value = '9.0' WHERE key = 'serving_contract_version'").run();
    db.close();
    expect(() => openPreparedCatalogue(copy)).toThrow("Unsupported prepared release contract");
  });
});
