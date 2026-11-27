import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { intakeProblems, problemsByRecord, recordChecks, valueProblems } from "../scripts/agents/intake-check";

// The per-record checks of scripts/agents/intake-check.ts, on a batch the intake agent wrote (a
// model and its source, since merged) and on changed copies of it. Each check has one record that
// passes and one that fails.
type Rec = Parameters<typeof intakeProblems>[0][number];
const batch = (): Rec[] =>
  readFileSync("tests/agents-intake-refresh-fixtures/batch.jsonl", "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const MODEL = "intake-350-20261121-model-protcell";
const SOURCE = "intake-350-20261121-source-protcell-a-foundation-model-for-single-cell-proteomics-biorx";
const withModel = (change: (model: Rec & Record<string, unknown>) => void) => {
  const records = batch();
  change(records.find((r) => r.id === MODEL) as Rec & Record<string, unknown>);
  return records;
};
const roots: string[] = [];
afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
});

describe("intake-check keeps what it checked before", () => {
  it("passes a batch the intake agent wrote", () => {
    expect(intakeProblems(batch())).toEqual([]);
    expect(recordChecks(batch())).toEqual([]);
  });

  it("still reports a model without entity_level through release validation", () => {
    const records = withModel((m) => delete m.attributes.entity_level);
    expect(intakeProblems(records).some((p) => p.includes("Model needs explicit entity_level"))).toBe(true);
  });
});

describe("per-record checks", () => {
  it("controlled values must be concepts of their vocabulary", () => {
    const records = withModel((m) => {
      (m.facets as Record<string, string[]>).areas = ["single-cell", "not-an-area"];
      m.attributes.entity_level = "galaxy";
    });
    expect(recordChecks(records)).toEqual([
      `${MODEL}: facets.areas "not-an-area" is not a concept in the area vocabulary`,
      `${MODEL}: attributes.entity_level "galaxy" is not a concept in the entity-level vocabulary`,
    ]);
    expect(intakeProblems(records)).toContain(`${MODEL}: facets.areas "not-an-area" is not a concept in the area vocabulary`);
  });

  it("an ID already in the store is refused, unless the record is a change to it", () => {
    const ids = new Set([MODEL]);
    expect(recordChecks(batch(), new Map(), { ids: new Set() })).toEqual([]);
    expect(recordChecks(batch(), new Map(), { ids })).toEqual([`${MODEL}: already in the store; records add only adds new records`]);
    expect(recordChecks(batch(), new Map(), { ids, changed: new Set([MODEL]) })).toEqual([]);
    expect(recordChecks(batch(), new Map(), { ids: new Set(["another-record"]), changed: new Set([MODEL]) })).toEqual([
      `${MODEL}: a change to a record the store does not hold`,
    ]);
  });

  it("an ID may appear once in the batch", () => {
    const records = batch();
    expect(recordChecks([...records, records[1]])).toEqual([
      `${SOURCE}: the batch holds this ID 2 times`,
      `${SOURCE}: the batch holds this ID 2 times`,
    ]);
  });

  it("a source is listed once and is a source record in the batch or the store", () => {
    const stored = new Map([["stored-source", { kind: "source" }], ["stored-model", { kind: "model" }]]);
    const cite = (ids: string[]) => withModel((m) => (m.source_ids = ids));
    expect(recordChecks(cite([SOURCE, "stored-source"]), stored, { ids: new Set(stored.keys()) })).toEqual([]);
    expect(recordChecks(cite([SOURCE, SOURCE]), stored)).toEqual([`${MODEL}: source_ids[1] ${SOURCE} is listed twice`]);
    expect(recordChecks(cite(["stored-model"]), stored)).toEqual([`${MODEL}: source_ids[0] stored-model is a model, not a source`]);
    expect(recordChecks(cite(["nowhere"]), stored, { ids: new Set(stored.keys()) })).toEqual([
      `${MODEL}: source_ids[0] nowhere is neither in the batch nor in the store`,
    ]);
    // Without the store's IDs a source it may hold is not reported.
    expect(recordChecks(cite(["nowhere"]), stored)).toEqual([]);
  });

  it("a link is listed once and does not point to its own record", () => {
    const link = (links: { relation: string; target_id: string }[]) => withModel((m) => (m.links = links));
    expect(recordChecks(link([{ relation: "variant_of", target_id: "a" }, { relation: "family", target_id: "a" }]))).toEqual([]);
    expect(recordChecks(link([{ relation: "variant_of", target_id: "a" }, { relation: "variant_of", target_id: "a" }]))).toEqual([
      `${MODEL}: links[1] variant_of to a is listed twice`,
    ]);
    expect(recordChecks(link([{ relation: "variant_of", target_id: MODEL }]))).toEqual([`${MODEL}: links[0] variant_of links the record to itself`]);
  });

  it("numbers JSON carries exactly and text without lone surrogates", () => {
    expect(valueProblems(JSON.parse('{"a": [9007199254740991, -9007199254740991, 1.5e300, 1e21, "\\ud83e\\uddec"]}'))).toEqual([]);
    expect(valueProblems(JSON.parse('{"a": [9007199254740993, 1e400, "\\ud800 x"], "\\udc00": 1}'))).toEqual([
      "a[0]: integer 9007199254740992 is outside the range JSON numbers carry exactly (2^53)",
      "a[1]: Infinity is not a finite number",
      "a[2]: text holds a lone surrogate",
      "\udc00: text holds a lone surrogate",
    ]);
    const records = withModel((m) => (m.attributes.parameter_count = 2 ** 60));
    expect(recordChecks(records)).toEqual([
      `${MODEL}: attributes/parameter_count: integer ${2 ** 60} is outside the range JSON numbers carry exactly (2^53)`,
    ]);
  });
});

describe("problems by record", () => {
  it("groups problems under the record they name and keeps the rest for the batch", () => {
    const records = batch();
    const grouped = problemsByRecord(records, [`${MODEL}: one`, `${SOURCE}: two`, `${MODEL}-other: three`, "release validation: four"]);
    expect(grouped).toEqual({ records: { [MODEL]: ["one"], [SOURCE]: ["two"] }, batch: [`${MODEL}-other: three`, "release validation: four"] });
    expect(problemsByRecord(records, [])).toEqual({ records: { [MODEL]: [], [SOURCE]: [] }, batch: [] });
  });

  it("--json prints them, and the store's IDs refuse a record it already holds", () => {
    const dir = mkdtempSync(join(tmpdir(), "intake-check-"));
    roots.push(dir);
    const file = join(dir, "batch.jsonl");
    // The model under an ID the store does not hold; its source as merged, so already stored.
    writeFileSync(file, readFileSync("tests/agents-intake-refresh-fixtures/batch.jsonl", "utf8").replaceAll(`"${MODEL}"`, '"intake-check-test-model"'));
    let out = "";
    let status = 0;
    try {
      out = execFileSync("npx", ["tsx", "scripts/agents/intake-check.ts", "--json", file], { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] });
    } catch (error) {
      ({ stdout: out, status } = error as { stdout: string; status: number });
    }
    expect(status).toBe(1);
    expect(JSON.parse(out)).toEqual({
      records: { "intake-check-test-model": [], [SOURCE]: ["already in the store; records add only adds new records"] },
      batch: [],
    });
  });
});
