import fs from "node:fs";
import { gunzipSync } from "node:zlib";
import { describe, expect, it } from "vitest";
import { createCatalogueQuery } from "../services/omics/src/catalogue-query";
import { benchmarkCoverage, assertCoverageFloor } from "../scripts/omics/audit-benchmark-evidence";
const snapshot = JSON.parse(gunzipSync(fs.readFileSync("data/omics/releases/2026-10-07-1448159e6a81/catalogue.json.gz")).toString());
const query = createCatalogueQuery(snapshot);
describe("released benchmark coverage floor", () => {
  it("uses the production graph and detects per-benchmark regressions", () => {
    const coverage = benchmarkCoverage(snapshot.records);
    for (const row of coverage) {
      expect(row.results).toBe(query.results({id: row.id}).total);
      expect(row.charts).toBe(query.get({id: row.id})!.comparison_options.length);
    }
    const floor = JSON.parse(fs.readFileSync("data/omics/benchmark-evidence-floor.json", "utf8"));
    expect(() => assertCoverageFloor(coverage, floor)).not.toThrow();
    const damaged = coverage.map(row => ({...row}));
    damaged.find(row => row.results > 0)!.charts = 0;
    expect(() => assertCoverageFloor(damaged, floor)).toThrow("regressed");
    expect(() => benchmarkCoverage(snapshot.records.filter((r: {kind: string}) => r.kind !== "claim")))
      .toThrow("unverified protocol association");
  });
});
