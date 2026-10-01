import { describe, expect, it } from "vitest";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { getLiterature, parseCsv, validateLiterature } from "../lib/benchmark-literature";

describe("literature build validators", () => {
  it("distinguishes model and dataset versions while rejecting repeated evidence in both validators", () => {
    const { papers, results } = getLiterature();
    const modelRevision = { ...results[0], id: "model-revision", model_version: "another-model-revision" };
    const datasetRevision = { ...results[0], id: "dataset-revision", dataset_version: "another-dataset-release" };
    const distinctVersions = [...results, modelRevision, datasetRevision];
    const repeatedVersion = [...distinctVersions, { ...modelRevision, id: "repeated-model-revision" }];
    expect(() => validateLiterature(papers, distinctVersions)).not.toThrow();
    expect(() => validateLiterature(papers, repeatedVersion)).toThrow("Duplicate paper/model/test/metric result");

    const root = fs.mkdtempSync(path.join(os.tmpdir(), "rewire-literature-versions-"));
    const fixture = path.join(root, "data", "benchmark-literature");
    const validator = path.resolve("scripts/validate-benchmark-literature.mjs");
    fs.mkdirSync(fixture, { recursive: true });
    fs.writeFileSync(path.join(fixture, "papers.json"), JSON.stringify(papers));
    const columns = Object.keys(results[0]) as (keyof typeof results[number])[];
    const encode = (value: string) => `"${value.replace(/"/g, '""')}"`;
    try {
      for (const [rows, valid] of [[distinctVersions, true], [repeatedVersion, false]] as const) {
        fs.writeFileSync(path.join(fixture, "results.csv"), [
          columns.join(","),
          ...rows.map((row) => columns.map((column) => encode(row[column])).join(",")),
        ].join("\n"));
        const run = spawnSync(process.execPath, [validator], { cwd: root, encoding: "utf8" });
        if (valid) expect(run.status, run.stderr).toBe(0);
        else {
          expect(run.status).not.toBe(0);
          expect(run.stderr).toContain("Duplicate paper/model/test/metric result");
        }
      }
    } finally {
      fs.rmSync(root, { recursive: true, force: true });
    }
  });

  it("also rejects missing scores and malformed quoted fields during build validation", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "rewire-literature-"));
    const fixture = path.join(root, "data", "benchmark-literature");
    const validator = path.resolve("scripts/validate-benchmark-literature.mjs");
    const { papers, results } = getLiterature();
    fs.mkdirSync(fixture, { recursive: true });
    fs.writeFileSync(path.join(fixture, "papers.json"), JSON.stringify(papers));
    const columns = Object.keys(results[0]);
    const encode = (value: string) => `"${value.replace(/"/g, '""')}"`;
    try {
      for (const [value, expected] of [["", "Non-numeric printed value"], ['"0.9"2', "Unexpected character after closing CSV quote"]]) {
        const rows = results.map((result, index) => columns.map((column) => {
          if (index === 0 && column === "value") return value;
          return encode(result[column as keyof typeof result]);
        }).join(","));
        fs.writeFileSync(path.join(fixture, "results.csv"), [columns.join(","), ...rows].join("\n"));
        const run = spawnSync(process.execPath, [validator], { cwd: root, encoding: "utf8" });
        expect(run.status).not.toBe(0);
        expect(run.stderr).toContain(expected);
      }
    } finally {
      fs.rmSync(root, { recursive: true, force: true });
    }
  });
});
