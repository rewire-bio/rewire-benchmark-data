/** The baseline comparison, called the ratchet. data/omics/checks-baseline.json pins the count of
 * every rule in scripts/omics/checks/, and this file compares a run over the store with it.
 *
 * Selective blocking since 25 November 2026 (issue #380): `defaultRatchetMode` is `"selective"`,
 * which fails when a blocking invariant (`C2.unknown-where-declared`, `C2.metric-not-a-concept`,
 * `C9`, `C13`) rises above its baseline while keeping advisory rules (`C1.unit-scope-note`,
 * `C2.opposite`, `C3`) report-only. `CHECKS_RATCHET=report` or `CHECKS_RATCHET=blocking` overrides
 * the mode for one run.
 *
 * The other tests guard the comparison code itself. They compare seeded runs with the counts of
 * this run, not with the baseline file, so they hold whatever the store has grown to.
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import {
  aboveBaseline, baselineFile, blockingRatchetKeys, defaultRatchetMode, loadInput, publishVerdict, ratchetCounts,
  ratchetFailure, ratchetMode, ratchetRows, ratchetTable, ratchetVerdict, reportOnlyNotice, runAll,
  type Baseline, type RunResult,
} from "../scripts/omics/checks/cli";
import type { Rec } from "../scripts/omics/checks/finding";
import { duplicateArtifact } from "../scripts/omics/checks/duplicate_artifact";
import { printedVsNumeric } from "../scripts/omics/checks/printed_vs_numeric";

const baseline = JSON.parse(fs.readFileSync(baselineFile, "utf8")) as Baseline;
const input = loadInput();
const run = runAll(input);

/** A baseline holding exactly the counts of one run, as `checks -- baseline` would pin it. */
const pinnedAt = (result: RunResult): Baseline => ({
  ...baseline,
  total_findings: result.findings.length,
  checks: Object.fromEntries(result.summaries.map((summary) => [summary.id, { title: summary.title, findings: summary.findings, rules: { ...summary.rules } }])),
});
const current = pinnedAt(run);

// One seeded result whose printed_value is unparseable (advisory C3 rule).
const seededAdvisory: Rec = {
  id: "seeded-result-for-the-advisory-ratchet-test",
  kind: "result",
  status: "source_checked",
  source_ids: [],
  links: [],
  attributes: { metric: "auroc", metric_direction: "higher", unit: "unitless", printed_value: "unreadable cell", numeric_value: "0.9", source_locator: "Table 1, column 'AUROC'" },
};
const grown = runAll({ ...input, results: [...input.results, seededAdvisory] });
const before = current.checks.C3.rules["unparseable-printed"];

// One seeded result omitting metric_direction on a metric with a declared default (blocking C2 rule).
const seededBlocking: Rec = {
  id: "seeded-result-for-the-blocking-ratchet-test",
  kind: "result",
  status: "source_checked",
  source_ids: [],
  links: [],
  attributes: { metric: "auroc", metric_direction: "unknown", unit: "unitless", printed_value: "0.9", numeric_value: "0.9", source_locator: "Table 1, column 'AUROC'" },
};
const grownBlocking = runAll({ ...input, results: [...input.results, seededBlocking] });

describe("deterministic checks", () => {
  it("reports every count beside its baseline, and blocks only blocking keys by default", () => {
    const verdict = ratchetVerdict(baseline, run, ratchetMode());
    publishVerdict(verdict);
    expect(verdict.blocks, verdict.message).toBe(false);
  });

  it("names every check and rule the baseline pins", () => {
    expect(Object.keys(ratchetCounts(run)).sort()).toEqual(Object.keys(ratchetCounts(baseline)).sort());
  });

  it("takes the mode from CHECKS_RATCHET, and from defaultRatchetMode without it", () => {
    expect(["selective", "report", "blocking"]).toContain(defaultRatchetMode);
    expect(ratchetMode({})).toBe(defaultRatchetMode);
    expect(ratchetMode({ CHECKS_RATCHET: "" })).toBe(defaultRatchetMode);
    expect(ratchetMode({ CHECKS_RATCHET: "selective" })).toBe("selective");
    expect(ratchetMode({ CHECKS_RATCHET: "report" })).toBe("report");
    expect(ratchetMode({ CHECKS_RATCHET: "blocking" })).toBe("blocking");
    expect(() => ratchetMode({ CHECKS_RATCHET: "on" })).toThrow('CHECKS_RATCHET must be "selective", "report", or "blocking"');
  });

  it("passes a raised advisory count in report and selective modes, and blocks C2/C9 rises in selective mode", () => {
    const reportVerdict = ratchetVerdict(current, grown, "report");
    expect(reportVerdict.blocks).toBe(false);
    expect(reportVerdict.rose).toBe(3);
    expect(reportVerdict.message).toContain(`3 counts above ${baselineFile} (ratchet mode: report).`);
    expect(reportVerdict.message).toMatch(new RegExp(`^C3\\.unparseable-printed +${before} +${before + 1} +\\+1$`, "m"));
    expect(reportVerdict.message).toContain(reportOnlyNotice);
    expect(reportVerdict.summary).toContain(`| C3.unparseable-printed | ${before} | ${before + 1} | +1 |`);

    const selectiveAdvisory = ratchetVerdict(current, grown, "selective");
    expect(selectiveAdvisory.blocks).toBe(false);
    expect(selectiveAdvisory.rose).toBe(3);

    const selectiveBlocking = ratchetVerdict(current, grownBlocking, "selective");
    expect(selectiveBlocking.blocks).toBe(true);
    expect(selectiveBlocking.message).toContain("C2.unknown-where-declared");
    expect(blockingRatchetKeys.has("C9.same-artifact-and-url")).toBe(true);
  });

  it("fails a raised count in blocking mode, and passes an unchanged store", () => {
    const verdict = ratchetVerdict(current, grown, "blocking");
    expect(verdict.blocks).toBe(true);
    expect(verdict.message).toContain(ratchetFailure(current, grown));
    expect(verdict.message).not.toContain(reportOnlyNotice);
    expect(ratchetVerdict(current, run, "blocking").blocks).toBe(false);
    expect(ratchetVerdict(current, run, "blocking").rose).toBe(0);
  });

  it("lists each check total, each rule and the grand total, with a signed difference", () => {
    const rows = ratchetRows(current, grown);
    expect(rows.map((row) => row.key)).toEqual(Object.keys(ratchetCounts(grown)));
    expect(rows.at(-1)).toEqual({ key: "total", baseline: run.findings.length, count: run.findings.length + 1, difference: 1 });
    expect(rows.filter((row) => row.difference !== 0).map((row) => row.key)).toEqual(["C3", "C3.unparseable-printed", "total"]);
    const lowered = ratchetRows(pinnedAt(grown), run).find((row) => row.key === "C3.unparseable-printed");
    expect(lowered).toEqual({ key: "C3.unparseable-printed", baseline: before + 1, count: before, difference: -1 });
    expect(ratchetTable([lowered!], "markdown")).toContain(`| C3.unparseable-printed | ${before + 1} | ${before} | -1 |`);
    expect(ratchetTable(rows).split("\n")).toHaveLength(rows.length + 1);
  });

  it("writes the table to the GitHub step summary when there is one", () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "checks-summary-"));
    const file = path.join(dir, "summary.md");
    const logged: string[] = [];
    const verdict = ratchetVerdict(current, grown, "report");
    publishVerdict(verdict, { GITHUB_STEP_SUMMARY: file }, (text) => logged.push(text));
    publishVerdict(verdict, {}, (text) => logged.push(text));
    const written = fs.readFileSync(file, "utf8");
    fs.rmSync(dir, { recursive: true });
    expect(logged).toEqual([verdict.message, verdict.message]);
    expect(written).toBe(verdict.summary + "\n");
    expect(written).toContain("| Count | Baseline | Current | Difference |");
    expect(written).toContain(`| C3.unparseable-printed | ${before} | ${before + 1} | +1 |`);
  });

  it("finds the counts a seeded record raises", () => {
    expect(aboveBaseline(current, grown)).toEqual([
      `C3: ${current.checks.C3.findings + 1}, baseline ${current.checks.C3.findings}`,
      `C3.unparseable-printed: ${before + 1}, baseline ${before}`,
      `total: ${run.findings.length + 1}, baseline ${run.findings.length}`,
    ]);
  });

  it("says in the blocking failure which rule rose, by how much, and what to do", () => {
    const message = ratchetFailure(current, grown);
    expect(message).toContain(`C3 ${current.checks.C3.title}, rule unparseable-printed: ${before + 1}, baseline ${before}, up 1`);
    expect(message).toContain("report severity");
    expect(message).toContain("not a correctness failure");
    expect(message).toContain("npm run checks -- report");
    expect(message).toContain("docs/reviews/");
    expect(ratchetFailure(current, { findings: [], summaries: [] })).toBe("");
  });

  it("finds a baseline count lowered under an unchanged store", () => {
    const lowered = structuredClone(current);
    const pinned = lowered.checks.C3.rules["unparseable-printed"];
    lowered.checks.C3.rules["unparseable-printed"] = pinned - 1;
    lowered.checks.C3.findings -= 1;
    lowered.total_findings -= 1;
    expect(aboveBaseline(lowered, run)).toEqual([
      `C3: ${current.checks.C3.findings}, baseline ${current.checks.C3.findings - 1}`,
      `C3.unparseable-printed: ${pinned}, baseline ${pinned - 1}`,
      `total: ${run.findings.length}, baseline ${run.findings.length - 1}`,
    ]);
  });

  it("covers C3 null-numeric-value, declared formats, and C9 supersession rules", () => {
    const baseInput = { ...input, records: [], results: [], sources: [] };
    const c3Findings = printedVsNumeric.run({
      ...baseInput,
      results: [
        { id: "r-null", kind: "result", status: "source_checked", source_ids: [], links: [], attributes: { printed_value: "N/A", numeric_value: null } },
        { id: "r-euro", kind: "result", status: "source_checked", source_ids: [], links: [], attributes: { printed_value: "2.782", numeric_value: "2782", unit: "count", numeric_representation: "Prints '.' as a thousands separator and ',' as the decimal separator" } },
        { id: "r-basis", kind: "result", status: "source_checked", source_ids: [], links: [], attributes: { printed_value: "0.56", numeric_value: "0.562", printed_value_basis: "Workbook number format 0.00" } },
        { id: "r-second", kind: "result", status: "source_checked", source_ids: [], links: [], attributes: { printed_value: "7 (6.5%)", numeric_value: "6.5", unit: "percent" } },
      ],
    });
    expect(c3Findings.map((f) => [f.subject, f.rule])).toEqual([["r-null", "null-numeric-value"]]);

    const c9Superseded = duplicateArtifact.run({
      ...baseInput,
      sources: [
        { id: "s1", kind: "source", status: "source_checked", source_ids: [], links: [], attributes: { artifact_sha256: "abc", url: "https://example.org/a" } },
        { id: "s2", kind: "source", status: "superseded", source_ids: [], links: [], attributes: { artifact_sha256: "abc", url: "https://example.org/a" } },
        { id: "s3", kind: "source", status: "source_checked", source_ids: [], links: [{ relation: "supersedes", target_id: "s4" }], attributes: { artifact_sha256: "def", url: "https://example.org/b" } },
        { id: "s4", kind: "source", status: "source_checked", source_ids: [], links: [], attributes: { artifact_sha256: "def", url: "https://example.org/b" } },
        { id: "s5", kind: "source", status: "source_checked", source_ids: [], links: [], attributes: { artifact_sha256: "ghi", url: "https://example.org/c" } },
        { id: "s6", kind: "source", status: "discovered", source_ids: [], links: [], attributes: { artifact_sha256: "ghi", url: "https://example.org/c" } },
      ],
    });
    expect(c9Superseded.map((f) => f.subject)).toEqual(["ghi https://example.org/c"]);
  });
});
