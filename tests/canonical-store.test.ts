import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { addBatch, loadRecords, provenanceFileFor, readKind, recordChanges, recordFile, recordSha256, reshardStore, shardOf, storeDigests } from "../scripts/omics/records";
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

const claim = (id: string) => record(id, "claim", { links: [{ relation: "subject", target_id: "test-source" }] });

function store(records: RecordEntry[]) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "canonical-store-"));
  roots.push(root);
  const sorted = [...records].sort((a, b) => (a.id < b.id ? -1 : 1));
  for (const r of sorted) {
    const file = recordFile(r, root);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.appendFileSync(file, JSON.stringify(r) + "\n");
    const provenance = provenanceFileFor(r.id, root);
    fs.mkdirSync(path.dirname(provenance), { recursive: true });
    fs.appendFileSync(provenance, JSON.stringify({
      id: r.id, sha256: recordSha256(r), added_in: "test", added_by: "test", changed_by: [],
    }) + "\n");
  }
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

  it("shards evidence kinds and provenance by the first hex digit of SHA-256(id)", () => {
    const claims = ["c-1", "c-2", "c-3", "c-4", "c-5"].map(claim);
    const root = store([record("test-source", "source"), ...claims]);
    for (const r of claims) {
      expect(recordFile(r, root)).toBe(path.join(root, "data/evidence/claims", `${shardOf(r.id)}.jsonl`));
      expect(fs.readFileSync(recordFile(r, root), "utf8")).toContain(`"id":"${r.id}"`);
      expect(fs.readFileSync(path.join(root, "data/provenance/records", `${shardOf(r.id)}.jsonl`), "utf8")).toContain(`"id":"${r.id}"`);
    }
    expect(new Set(claims.map((r) => shardOf(r.id))).size).toBeGreaterThan(1);
    expect(recordFile(record("a-model", "model"), root)).toBe(path.join(root, "data/entities/models.jsonl"));
    expect(readKind("claim", root).map((r) => r.id)).toEqual(claims.map((r) => r.id));
    expect(loadRecords(root)).toHaveLength(6);
  });

  it("rejects an evidence record in another shard", () => {
    const claims = ["c-1", "c-2", "c-3", "c-4", "c-5"].map(claim);
    const root = store([record("test-source", "source"), ...claims]);
    const stray = claims.find((r) => shardOf(r.id) !== shardOf(claims[0].id))!;
    fs.appendFileSync(recordFile(claims[0], root), JSON.stringify(stray) + "\n");
    expect(() => loadRecords(root)).toThrow("wrong file");
  });

  it("reshards an unsharded store without changing its digests", () => {
    const claims = ["c-1", "c-2", "c-3", "c-4", "c-5"].map(claim);
    const all = [record("test-source", "source"), ...claims];
    const root = store(all);
    const sharded = storeDigests(root);
    // Rewrite it as the single files the store used before sharding.
    const lines = (rows: { id: string }[]) => rows.map((r) => JSON.stringify(r) + "\n").join("");
    fs.rmSync(path.join(root, "data/evidence/claims"), { recursive: true });
    fs.rmSync(path.join(root, "data/provenance/records"), { recursive: true });
    fs.writeFileSync(path.join(root, "data/evidence/claims.jsonl"), lines(claims));
    const provenance = all.map((r) => ({ id: r.id, sha256: recordSha256(r), added_in: "test", added_by: "test", changed_by: [] }))
      .sort((a, b) => (a.id < b.id ? -1 : 1));
    fs.writeFileSync(path.join(root, "data/provenance/records.jsonl"), lines(provenance));
    expect(sharded.find((d) => d.file === "data/evidence/claims.jsonl")!.sha256)
      .toBe(crypto.createHash("sha256").update(lines(claims)).digest("hex"));
    expect(sharded.find((d) => d.file === "data/provenance/records.jsonl")!.sha256)
      .toBe(crypto.createHash("sha256").update(lines(provenance)).digest("hex"));
    expect(reshardStore(root)).toBe(6);
    expect(fs.existsSync(path.join(root, "data/evidence/claims.jsonl"))).toBe(false);
    expect(fs.existsSync(path.join(root, "data/provenance/records.jsonl"))).toBe(false);
    expect(storeDigests(root)).toEqual(sharded);
    expect(loadRecords(root)).toHaveLength(6);
  });

  it("keeps reviewed identity changes in the stored record", () => {
    const configuration = recordsById.get("atom3d-method-karimi-et-al-2019")!;
    expect(configuration.name).toBe("DeepAffinity (unified RNN/RNN-CNN; DSSP-derived SPS)");
    expect(configuration.attributes.source_label).toBe("[Karimi et al., 2019]");
  });
});
