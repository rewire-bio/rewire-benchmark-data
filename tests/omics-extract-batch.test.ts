/**
 * The shared extraction lane against the declared attribute contract.
 *
 * buildBatch is the one shared record renderer in the repository, so every
 * record it emits is run through attributeIssues here: the same check
 * `npm run records -- add` applies. writeBatch is checked against the batch
 * folder docs/collection.md describes, not the path layout it replaced.
 */
import { describe, expect, it } from "vitest";
import { createHash } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { buildBatch, writeBatch, type BatchSpec } from "../scripts/omics/extract/batch";
import { attributeIssues } from "../shared/omics/attributes";

const fixture = (): BatchSpec => ({
  key: "example",
  benchmarkId: "example-benchmark",
  benchmarkName: "Example",
  area: "proteins-complexes",
  source: {
    id: "example-source",
    name: "Paper",
    url: "https://example.org/paper",
    artifactUrl: "https://example.org/paper.pdf",
    sha256: "a".repeat(64),
    version: "v1",
    venue: "Example",
    retrievedAt: "2026-11-17",
  },
  reviewer: "Claude research agent; no human review claimed",
  date: "2026-11-17",
  method: "Deterministic parse of the pinned PDF text layer, row labels asserted",
  caveats: ["Author-reported numbers, source checked but not reproduced."],
  tasks: [
    {
      label: "A",
      title: "Task A",
      metric: "Spearman r",
      metricKey: "spearman-correlation",
      unit: "unitless",
      direction: "higher",
      dataset: "Dataset",
      protocol: "Test split",
      locator: "Table 1, row(Task A)",
    },
  ],
  methods: [
    { name: "First", kind: "method", description: "First method", locator: "Table 1, column(First)" },
    { name: "Second", kind: "configuration", description: "Second method", locator: "Table 1, column(Second)" },
    { name: "Third", kind: "pipeline", description: "Third method", locator: "Table 1, column(Third)" },
  ],
  cells: [
    { method: "First", task: "A", printed: "0.90 ± 0.01", value: "0.90", sd: "0.01", locator: "Table 1, row(Task A), column(First)" },
    { method: "Second", task: "A", printed: "0.84", value: "0.84", locator: "Table 1, row(Task A), column(Second)" },
    { method: "Third", task: "A", printed: "-", value: null, locator: "Table 1, row(Task A), column(Third)" },
  ],
});

const issues = (spec: BatchSpec) =>
  buildBatch(spec).flatMap((record) =>
    attributeIssues(record).map((issue) => `${record.kind} ${record.id}: ${issue}`),
  );

const record = (spec: BatchSpec, id: string) =>
  buildBatch(spec).find((entry) => entry.id === id)!;

describe("buildBatch against the declared attributes", () => {
  it("emits no attribute issue on any record it renders", () => {
    expect(issues(fixture())).toEqual([]);
  });

  it("emits a declared uncertainty type and omits the key with a reason when no spread is printed", () => {
    const spec = fixture();
    const withSpread = record(spec, "example-result-first-a-spearman-correlation");
    expect(withSpread.attributes.uncertainty).toEqual({ type: "unresolved_spread", value: "0.01" });
    expect(withSpread.attributes.missing_metadata).not.toHaveProperty("uncertainty");

    const withoutSpread = record(spec, "example-result-second-a-spearman-correlation");
    expect(withoutSpread.attributes).not.toHaveProperty("uncertainty");
    expect(withoutSpread.attributes.missing_metadata).toMatchObject({
      uncertainty: { reason: "unextracted" },
    });
  });

  it("keeps a spread the source defines, and still passes the contract", () => {
    const spec = { ...fixture(), uncertaintyType: "standard_error" as const };
    expect(record(spec, "example-result-first-a-spearman-correlation").attributes.uncertainty)
      .toEqual({ type: "standard_error", value: "0.01" });
    expect(issues(spec)).toEqual([]);
  });

  it("gives every missing field a reason object rather than a token", () => {
    const spec = fixture();
    expect(record(spec, "example-dataset-dataset").attributes.missing_metadata).toEqual({
      version: { reason: "unreported" },
      url: { reason: "unextracted" },
    });
    expect(record(spec, "example-method-first").attributes.missing_metadata).toEqual({
      checkpoint_revision: { reason: "unreported" },
      parameters: { reason: "unextracted" },
    });
  });

  it("records review methods and reviewers as lists of concept keys", () => {
    const spec = fixture();
    expect(record(spec, "example-result-first-a-spearman-correlation").attributes.review).toMatchObject({
      method: ["automated-source-review"],
      reviewer: ["unidentified-automated-reviewer"],
      method_note: spec.method,
      reviewer_note: spec.reviewer,
    });
    expect(record(spec, "example-association-a").attributes.review).toMatchObject({
      method: ["automated-source-review"],
    });
    const declared = {
      ...fixture(),
      reviewMethods: ["pdf-text-parse", "deterministic-table-parse"],
      reviewerAgents: ["claude"],
    };
    expect(record(declared, "example-result-first-a-spearman-correlation").attributes.review).toMatchObject({
      method: ["pdf-text-parse", "deterministic-table-parse"],
      reviewer: ["claude"],
    });
    expect(issues(declared)).toEqual([]);
  });
});

describe("writeBatch output layout", () => {
  const written = (spec: BatchSpec) => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "omics-batch-"));
    const records = writeBatch(spec, root);
    const folder = path.join(root, spec.batch ?? spec.key);
    const files = fs.readdirSync(root, { recursive: true, encoding: "utf8" });
    return { root, folder, records, files };
  };

  it("writes data/omics/<batch>/batch.jsonl and review.json, and nothing else", () => {
    const spec = fixture();
    const { root, folder, records, files } = written(spec);
    try {
      expect(files.sort()).toEqual(["example", "example/batch.jsonl", "example/review.json"]);
      const lines = fs.readFileSync(path.join(folder, "batch.jsonl"), "utf8").trimEnd().split("\n");
      expect(lines.map((line) => JSON.parse(line))).toEqual(records);
      expect(files.some((file) => file.includes("reviewed"))).toBe(false);
      expect(files.some((file) => /2026-09-18|-2026\.jsonl|-extraction\.json/.test(file))).toBe(false);
    } finally {
      fs.rmSync(root, { recursive: true, force: true });
    }
  });

  it("names the folder the batch asks for", () => {
    const spec = { ...fixture(), batch: "example-20261117" };
    const { root, files } = written(spec);
    try {
      expect(files.sort()).toEqual([
        "example-20261117",
        "example-20261117/batch.jsonl",
        "example-20261117/review.json",
      ]);
    } finally {
      fs.rmSync(root, { recursive: true, force: true });
    }
  });

  it("writes a receipt that pins the records and leaves review sign-off empty", () => {
    const spec = fixture();
    const { root, folder } = written(spec);
    try {
      const receipt = JSON.parse(fs.readFileSync(path.join(folder, "review.json"), "utf8"));
      expect(receipt).toMatchObject({
        schema_version: "1.0",
        method: null,
        review_methods: [],
        reviewer: null,
        reviewed_at: null,
        scope: null,
        limitations: [],
        errors: [],
        extraction: {
          batch: "example",
          benchmark: spec.benchmarkId,
          source: spec.source.artifactUrl,
          artifact_sha256: spec.source.sha256,
          method: spec.method,
          extracted_by: spec.reviewer,
          extracted_at: spec.date,
        },
      });
      const bytes = fs.readFileSync(path.join(folder, "batch.jsonl"));
      expect(receipt.extraction.records_sha256).toBe(createHash("sha256").update(bytes).digest("hex"));
    } finally {
      fs.rmSync(root, { recursive: true, force: true });
    }
  });

  it("keeps a receipt the reviewer has already filled in", () => {
    const spec = fixture();
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "omics-batch-"));
    try {
      fs.mkdirSync(path.join(root, spec.key));
      fs.writeFileSync(
        path.join(root, spec.key, "review.json"),
        JSON.stringify({ schema_version: "1.0", reviewer: "claude", errors: ["one"] }) + "\n",
      );
      writeBatch(spec, root);
      const receipt = JSON.parse(fs.readFileSync(path.join(root, spec.key, "review.json"), "utf8"));
      expect(receipt.reviewer).toBe("claude");
      expect(receipt.errors).toEqual(["one"]);
      expect(receipt.extraction.batch).toBe("example");
    } finally {
      fs.rmSync(root, { recursive: true, force: true });
    }
  });
});
