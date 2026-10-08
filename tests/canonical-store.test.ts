import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { addBatch, loadRecords, recordChanges, recordFile, recordSha256 } from "../scripts/omics/records";
import type { RecordEntry } from "../scripts/omics/schema";
import { recordsById } from "./helpers/records";

const roots: string[] = [];
afterEach(() => { for (const root of roots.splice(0)) fs.rmSync(root, { recursive: true, force: true }); });

const record = (id: string, kind: RecordEntry["kind"], extra: Partial<RecordEntry> = {}): RecordEntry => ({
  id, kind, name: id, description: "", status: "source_checked", facets: {},
  source_ids: kind === "source" ? [] : ["test-source"], links: [],
  attributes: kind === "source" ? { url: "https://example.org/paper", version: "v1", retrieved_at: "2026-10-08T00:00:00Z" } : {},
  ...extra,
});

function store(records: RecordEntry[]) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "canonical-store-"));
  roots.push(root);
  const sorted = [...records].sort((a, b) => (a.id < b.id ? -1 : 1));
  for (const r of sorted) {
    const file = recordFile(r.kind, root);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.appendFileSync(file, JSON.stringify(r) + "\n");
  }
  fs.mkdirSync(path.join(root, "data/provenance"), { recursive: true });
  fs.writeFileSync(path.join(root, "data/provenance/records.jsonl"), sorted.map((r) => JSON.stringify({
    id: r.id, sha256: recordSha256(r), added_in: "test", added_by: "test", changed_by: [],
  }) + "\n").join(""));
  return root;
}

describe("canonical record store", () => {
  it("loads sorted records from one file per kind", () => {
    const root = store([record("test-source", "source"), record("b-model", "model"), record("a-model", "model")]);
    expect(loadRecords(root).map((r) => r.id)).toEqual(["a-model", "b-model", "test-source"]);
    expect(fs.existsSync(path.join(root, "data/entities/models.jsonl"))).toBe(true);
  });

  it("fails when a record changes without a recorded change", () => {
    const root = store([record("test-source", "source"), record("a-model", "model")]);
    const file = path.join(root, "data/entities/models.jsonl");
    fs.writeFileSync(file, fs.readFileSync(file, "utf8").replace('"name":"a-model"', '"name":"renamed"'));
    expect(() => loadRecords(root)).toThrow("changed without a provenance entry");
    recordChanges(["a-model"], "test-batch", "docs/reviews/test.md", root);
    expect(loadRecords(root).find((r) => r.id === "a-model")!.name).toBe("renamed");
  });

  it("appends a batch and rejects duplicate IDs", () => {
    const root = store([record("test-source", "source"), record("a-model", "model")]);
    const batch = path.join(root, "batch.jsonl");
    fs.writeFileSync(batch, JSON.stringify(record("c-model", "model")) + "\n");
    expect(addBatch(batch, "data/omics/test-batch", root)).toBe(1);
    expect(loadRecords(root)).toHaveLength(3);
    expect(() => addBatch(batch, "data/omics/test-batch", root)).toThrow("cannot replace or duplicate");
  });

  it("rejects records in the wrong file", () => {
    const root = store([record("test-source", "source"), record("a-model", "model")]);
    fs.appendFileSync(path.join(root, "data/entities/models.jsonl"), JSON.stringify(record("z-task", "task")) + "\n");
    expect(() => loadRecords(root)).toThrow("wrong file");
  });

  it("keeps reviewed identity changes in the stored record", () => {
    const configuration = recordsById.get("atom3d-method-karimi-et-al-2019")!;
    expect(configuration.name).toBe("DeepAffinity (unified RNN/RNN-CNN; DSSP-derived SPS)");
    expect(configuration.attributes.source_label).toBe("[Karimi et al., 2019]");
  });
});
