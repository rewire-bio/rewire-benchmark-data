import { describe, expect, it } from "vitest";
import type { CatalogueRecord } from "../shared/omics/catalogue-query";
import {
  benchmarkTaskSchema,
  checkpointSchema,
  validateStructuredFacts,
} from "../shared/omics/structured-facts";

const evidence = { source_ids: ["s1"], source_locator: "readme.md: parameters" };
const checkpoint = {
  checkpoint: "org/model-650m",
  parameters: 650_000_000,
  context_length: 1024,
  context_unit: "tokens",
  code_licence: "MIT",
  weights_licence: "CC-BY-4.0",
  code_url: "https://github.com/org/model",
  weights_url: "https://huggingface.co/org/model-650m",
  gated: false,
  released: "2024-05-01",
  ...evidence,
};
const task = {
  task: "Variant effect prediction",
  dataset: "ClinVar missense",
  size: 1200,
  size_unit: "variants",
  split: "held-out genes",
  primary_metric: "AUROC",
  metric_direction: "higher",
  results_url: null,
  code_url: "https://github.com/org/bench",
  data_url: null,
  data_licence: null,
  code_licence: "Apache-2.0",
  released: "2023-11",
  ...evidence,
};

describe("checkpoint entries", () => {
  it("accept a complete entry and one with every optional value null", () => {
    expect(checkpointSchema.safeParse(checkpoint).success).toBe(true);
    const nulls = Object.fromEntries(Object.keys(checkpoint).map((k) => [k, null]));
    expect(checkpointSchema.safeParse({ ...nulls, checkpoint: "x", ...evidence }).success).toBe(true);
  });
  it.each([
    ["an empty name", { checkpoint: "" }],
    ["a parameter count as text", { parameters: "650M" }],
    ["a fractional parameter count", { parameters: 6.5 }],
    ["a negative context length", { context_length: -1 }],
    ["an empty licence", { code_licence: "" }],
    ["gated as text", { gated: "no" }],
    ["a release that is not an ISO date", { released: "May 2024" }],
    ["no source ids", { source_ids: [] }],
    ["an empty locator", { source_locator: " " }],
    ["a key the schema does not know", { quotes: [] }],
  ])("refuse %s", (_, change) => {
    expect(checkpointSchema.safeParse({ ...checkpoint, ...change }).success).toBe(false);
  });
  it("refuse an entry with a field missing", () => {
    const { weights_url: _, ...rest } = checkpoint;
    expect(checkpointSchema.safeParse(rest).success).toBe(false);
  });
});

describe("benchmark task entries", () => {
  it("accept a complete entry", () => {
    expect(benchmarkTaskSchema.safeParse(task).success).toBe(true);
  });
  it.each([
    ["an empty task", { task: "" }],
    ["a size as text", { size: "1.2k" }],
    ["a fractional size", { size: 1.5 }],
    ["a direction other than higher or lower", { metric_direction: "up" }],
    ["an empty dataset", { dataset: "" }],
    ["a release that is not an ISO date", { released: "2023/11/01" }],
    ["no source ids", { source_ids: [] }],
    ["a key the schema does not know", { checkpoint: "x" }],
  ])("refuse %s", (_, change) => {
    expect(benchmarkTaskSchema.safeParse({ ...task, ...change }).success).toBe(false);
  });
});

describe("validateStructuredFacts", () => {
  const source = {
    id: "s1", kind: "source", source_ids: [], links: [],
    attributes: { artifact_sha256: "a".repeat(64) },
  } as unknown as CatalogueRecord;
  const record = (kind: string, attributes: Record<string, unknown>, source_ids = ["s1"]) =>
    ({ id: "r1", kind, source_ids, links: [], attributes }) as unknown as CatalogueRecord;
  const byId = new Map([["s1", source]]);
  it("accepts entries that cite the record's pinned sources", () => {
    expect(() => validateStructuredFacts(record("model", { checkpoints: [checkpoint] }), byId)).not.toThrow();
    expect(() => validateStructuredFacts(record("benchmark", { benchmark_tasks: [task] }), byId)).not.toThrow();
  });
  it("refuses the attribute on another kind", () => {
    expect(() => validateStructuredFacts(record("benchmark", { checkpoints: [checkpoint] }), byId)).toThrow(/Only model/);
    expect(() => validateStructuredFacts(record("model", { benchmark_tasks: [task] }), byId)).toThrow(/Only benchmark/);
  });
  it("refuses an empty list", () => {
    expect(() => validateStructuredFacts(record("model", { checkpoints: [] }), byId)).toThrow();
  });
  it("refuses a source the record does not cite", () => {
    expect(() => validateStructuredFacts(record("model", { checkpoints: [checkpoint] }, []), byId)).toThrow(/Unpinned/);
  });
  it("refuses a source without a pinned hash", () => {
    const unpinned = new Map([["s1", { ...source, attributes: {} } as CatalogueRecord]]);
    expect(() => validateStructuredFacts(record("model", { checkpoints: [checkpoint] }), unpinned)).toThrow(/Unpinned/);
  });
});
