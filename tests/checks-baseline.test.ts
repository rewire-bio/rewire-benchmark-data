/** The baseline comparison, called the ratchet. data/omics/checks-baseline.json pins the count of
 * every rule in scripts/omics/checks/, and this file compares a run over the store with it.
 *
 * Report only since 23 November 2026 (issue #272). The first test prints every count beside its
 * baseline, to the job log and to the GitHub step summary, and passes when counts rise. The
 * blocking ratchet failed 13 of 14 pull requests that added results, and nobody had measured how
 * often a finding is a real error. The switch is defaultRatchetMode in scripts/omics/checks/cli.ts,
 * and CHECKS_RATCHET=blocking overrides it for one run.
 *
 * In blocking mode the first test fails when a run raises a count, and ratchetFailure is the
 * assertion message: it names the check and rule that rose, by how much, and the two ways
 * forward, so the failure alone is enough to act on.
 *
 * The other tests guard the comparison code itself. They compare seeded runs with the counts of
 * this run, not with the baseline file, so they hold whatever the store has grown to.
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import {
  aboveBaseline, baselineFile, defaultRatchetMode, loadInput, publishVerdict, ratchetCounts, ratchetFailure, ratchetMode, ratchetRows,
  ratchetTable, ratchetVerdict, reportOnlyNotice, runAll, type Baseline, type RunResult,
} from "../scripts/omics/checks/cli";
import type { Rec } from "../scripts/omics/checks/finding";

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

// One seeded result whose metric_qualifier is a bare verdict, which is what C4 reports.
const seeded: Rec = {
  id: "seeded-result-for-the-ratchet-test",
  kind: "result",
  status: "source_checked",
  source_ids: [],
  links: [],
  attributes: { metric: "auroc", metric_direction: "higher", unit: "unitless", metric_qualifier: "high", printed_value: "0.9", numeric_value: "0.9", source_locator: "Table 1, column 'AUROC'" },
};
const grown = runAll({ ...input, results: [...input.results, seeded] });
const before = current.checks.C4.rules["verdict-or-vendor-token"];

describe("deterministic checks", () => {
  it("reports every count beside its baseline, and fails on a rise only in blocking mode", () => {
    const verdict = ratchetVerdict(baseline, run, ratchetMode());
    publishVerdict(verdict);
    expect(verdict.blocks, verdict.message).toBe(false);
  });

  it("names every check and rule the baseline pins", () => {
    expect(Object.keys(ratchetCounts(run)).sort()).toEqual(Object.keys(ratchetCounts(baseline)).sort());
  });

  // defaultRatchetMode is not pinned here: changing it is how blocking is turned back on.
  it("takes the mode from CHECKS_RATCHET, and from defaultRatchetMode without it", () => {
    expect(["report", "blocking"]).toContain(defaultRatchetMode);
    expect(ratchetMode({})).toBe(defaultRatchetMode);
    expect(ratchetMode({ CHECKS_RATCHET: "" })).toBe(defaultRatchetMode);
    expect(ratchetMode({ CHECKS_RATCHET: "report" })).toBe("report");
    expect(ratchetMode({ CHECKS_RATCHET: "blocking" })).toBe("blocking");
    expect(() => ratchetMode({ CHECKS_RATCHET: "on" })).toThrow('CHECKS_RATCHET must be "report" or "blocking"');
  });

  it("passes a raised count in report mode and prints the difference", () => {
    const verdict = ratchetVerdict(current, grown, "report");
    expect(verdict.blocks).toBe(false);
    expect(verdict.rose).toBe(3);
    expect(verdict.message).toContain(`3 counts above ${baselineFile} (ratchet mode: report).`);
    expect(verdict.message).toMatch(new RegExp(`^C4\\.verdict-or-vendor-token +${before} +${before + 1} +\\+1$`, "m"));
    expect(verdict.message).toContain(reportOnlyNotice);
    expect(verdict.summary).toContain(`| C4.verdict-or-vendor-token | ${before} | ${before + 1} | +1 |`);
    expect(verdict.summary).toContain("issue #272");
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
    expect(rows.filter((row) => row.difference !== 0).map((row) => row.key)).toEqual(["C4", "C4.verdict-or-vendor-token", "total"]);
    const lowered = ratchetRows(pinnedAt(grown), run).find((row) => row.key === "C4.verdict-or-vendor-token");
    expect(lowered).toEqual({ key: "C4.verdict-or-vendor-token", baseline: before + 1, count: before, difference: -1 });
    expect(ratchetTable([lowered!], "markdown")).toContain(`| C4.verdict-or-vendor-token | ${before + 1} | ${before} | -1 |`);
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
    expect(written).toContain(`| C4.verdict-or-vendor-token | ${before} | ${before + 1} | +1 |`);
  });

  it("finds the counts a seeded record raises", () => {
    expect(aboveBaseline(current, grown)).toEqual([
      `C4: ${current.checks.C4.findings + 1}, baseline ${current.checks.C4.findings}`,
      `C4.verdict-or-vendor-token: ${before + 1}, baseline ${before}`,
      `total: ${run.findings.length + 1}, baseline ${run.findings.length}`,
    ]);
  });

  it("says in the blocking failure which rule rose, by how much, and what to do", () => {
    const message = ratchetFailure(current, grown);
    expect(message).toContain(`C4 ${current.checks.C4.title}, rule verdict-or-vendor-token: ${before + 1}, baseline ${before}, up 1`);
    expect(message).toContain("report severity");
    expect(message).toContain("not a correctness failure");
    expect(message).toContain("npm run checks -- report");
    expect(message).toContain("docs/reviews/");
    expect(ratchetFailure(current, { findings: [], summaries: [] })).toBe("");
  });

  it("finds a baseline count lowered under an unchanged store", () => {
    const lowered = structuredClone(current);
    const pinned = lowered.checks.C9.rules["same-artifact-and-url"];
    lowered.checks.C9.rules["same-artifact-and-url"] = pinned - 1;
    lowered.checks.C9.findings -= 1;
    lowered.total_findings -= 1;
    expect(aboveBaseline(lowered, run)).toEqual([
      `C9: ${current.checks.C9.findings}, baseline ${current.checks.C9.findings - 1}`,
      `C9.same-artifact-and-url: ${pinned}, baseline ${pinned - 1}`,
      `total: ${run.findings.length}, baseline ${run.findings.length - 1}`,
    ]);
  });
});
