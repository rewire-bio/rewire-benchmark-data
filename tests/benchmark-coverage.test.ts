import { describe, it, expect } from "vitest";
import { benchmarkCoverage } from "../shared/omics/benchmark-coverage";
import { createCatalogueQuery, type CatalogueRecord, type CatalogueSnapshot } from "../shared/omics/catalogue-query";
import type { PublishedComparison } from "../shared/omics/published-comparisons";

const record = (
  id: string,
  kind: CatalogueRecord["kind"],
  attributes: Record<string, unknown> = {},
  links: CatalogueRecord["links"] = [],
): CatalogueRecord => ({
  id,
  kind,
  name: id,
  description: "",
  status: "source_checked",
  facets: {},
  source_ids: ["source"],
  links,
  attributes,
});
function fixture(): CatalogueSnapshot {
  const panel: PublishedComparison = {
    id: "comparison",
    title: "One paper, one test split",
    protocol_id: "benchmark",
    dataset_id: "dataset",
    metric: "correlation",
    unit: "dimensionless",
    direction: "higher",
    result_ids: Array.from({ length: 30 }, (_, i) => `result-${i}`),
    source_ids: ["source"],
    source_locator: "Table 1",
    context:
      "Same held-out cohort; input information differs by configuration.",
    caveats: [
      "Unreported compute prevents a controlled efficiency comparison.",
    ],
    review: { method: "automated_source_review", date: "2026-09-17" },
  };
  const records = [
    record("source", "source", {
      url: "https://example.org/paper",
      version: "v1",
      retrieved_at: "2026-09-17",
      artifact_sha256: "a".repeat(64),
    }),
    record("benchmark", "benchmark", { comparison_panels: [panel] }),
    record("dataset", "dataset"),
  ];
  for (let i = 0; i < 30; i++)
    records.push(
      record(`model-${i}`, "model"),
      record(
        `evaluation-${i}`,
        "evaluation",
        {
          origin: i === 29 ? "paper_compilation" : "author_reported",
          comparison: { split: "test", aggregation: "mean" },
        },
        [
          { relation: "model", target_id: `model-${i}` },
          { relation: "benchmark", target_id: "benchmark" },
          { relation: "dataset", target_id: "dataset" },
        ],
      ),
      record(
        `result-${i}`,
        "result",
        {
          metric: "correlation",
          unit: "dimensionless",
          metric_direction: "higher",
          numeric_value: String((i - 5) / 30),
          printed_value: String((i - 5) / 30),
          source_locator: `Table 1 row ${i + 1}`,
        },
        [{ relation: "evaluation", target_id: `evaluation-${i}` }],
      ),
    );
  return {
    schema_version: "1.0",
    release_id: "release",
    released_at: "2026-09-17T00:00:00Z",
    coverage: {},
    records,
  };
}
describe("benchmark coverage and inherited comparison validation", () => {
  it("rejects conflicting inherited panel IDs while retaining identical duplicates", () => {
    const snapshot = fixture();
    const benchmark = snapshot.records.find(r => r.id === "benchmark")!;
    const panels = structuredClone(benchmark.attributes.comparison_panels) as PublishedComparison[];
    snapshot.records.push(record("parent", "benchmark", { comparison_panels: panels }),
      record("claim", "claim", { field: "links:evaluates_task:parent", value: "parent", source_locator: "Methods" }, [{ relation: "subject", target_id: "benchmark" }]));
    benchmark.links.push({ relation: "evaluates_task", target_id: "parent" });
    expect(createCatalogueQuery(snapshot).get({ id: "parent" })!.published_comparisons).toHaveLength(1);
    panels[0].title = "Conflicting figure";
    expect(() => createCatalogueQuery(snapshot).get({ id: "parent" })).toThrow("Conflicting inherited comparison: comparison");
  });
  it("audits complete row counts, inherited figures, evidence sources and empty pages", () => {
    const snapshot = fixture();
    const benchmark = snapshot.records.find(r => r.id === "benchmark")!;
    snapshot.records.push(record("parent", "benchmark"), record("empty", "task"),
      record("hidden", "benchmark"), record("historical", "protocol"),
      record("claim", "claim", { field: "links:evaluates_task:parent", value: "parent", source_locator: "Methods" }, [{ relation: "subject", target_id: "benchmark" }]));
    snapshot.records.find(r => r.id === "hidden")!.status = "excluded";
    snapshot.records.find(r => r.id === "historical")!.status = "superseded";
    benchmark.links.push({ relation: "evaluates_task", target_id: "parent" });
    const audit = benchmarkCoverage(snapshot);
    expect(audit.release_id).toBe("release");
    expect(audit.pages.find(p => p.id === "parent")).toMatchObject({ metric_rows: 30, evaluations: 30, charts: 1, charted_metric_rows: 30, chart_protocol_ids: ["benchmark"], source_urls: ["https://example.org/paper"] });
    expect(audit.pages.find(p => p.id === "empty")).toMatchObject({ metric_rows: 0, state: "results_not_yet_collected" });
    expect(audit.pages.find(p => p.id === "historical")!.state).toBe("historical");
    expect(audit.pages.some(p => p.id === "hidden")).toBe(false);
    expect(audit.summary.benchmark).toEqual({ pages: 2, with_results: 2, with_charts: 2 });
  });
});
