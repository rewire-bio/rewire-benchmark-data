/** The ratchet. data/omics/checks-baseline.json pins the count of every rule in
 * scripts/omics/checks/, and this test fails when a run raises one.
 *
 * The checks are report severity and gate nothing at write time, so this is the only thing
 * that bites. It bites on growth: a PR may leave the existing backlog alone, but it may not
 * add to it. Working a count down and lowering the baseline in the same PR is the way to make
 * progress; raising a baseline number needs a dated review saying why.
 */
import fs from "node:fs";
import { describe, expect, it } from "vitest";
import { aboveBaseline, baselineFile, loadInput, ratchetCounts, runAll, type Baseline } from "../scripts/omics/checks/cli";
import type { Rec } from "../scripts/omics/checks/finding";

const baseline = JSON.parse(fs.readFileSync(baselineFile, "utf8")) as Baseline;
const input = loadInput();
const run = runAll(input);

describe("deterministic checks", () => {
  it("raises no count above its baseline", () => {
    expect(aboveBaseline(baseline, run)).toEqual([]);
  });

  // A count worked down is not failed here. The ratchet bites on growth, not on the backlog,
  // so a correction PR that shrinks a queue passes; `npm run checks -- report` says which
  // counts are now below the baseline and the author lowers them in the same PR.

  it("names every check and rule the baseline pins", () => {
    expect(Object.keys(ratchetCounts(run)).sort()).toEqual(Object.keys(ratchetCounts(baseline)).sort());
  });

  it("fails when the store raises a count", () => {
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
    const before = baseline.checks.C4.rules["verdict-or-vendor-token"];
    expect(aboveBaseline(baseline, grown)).toEqual([
      `C4: ${before + 1}, baseline ${before}`,
      `C4.verdict-or-vendor-token: ${before + 1}, baseline ${before}`,
      `total: ${baseline.total_findings + 1}, baseline ${baseline.total_findings}`,
    ]);
  });

  it("fails when a baseline count is lowered under an unchanged store", () => {
    const lowered = structuredClone(baseline);
    const before = lowered.checks.C9.rules["same-artifact-and-url"];
    lowered.checks.C9.rules["same-artifact-and-url"] = before - 1;
    lowered.checks.C9.findings -= 1;
    lowered.total_findings -= 1;
    expect(aboveBaseline(lowered, run)).toEqual([
      `C9: ${before}, baseline ${before - 1}`,
      `C9.same-artifact-and-url: ${before}, baseline ${before - 1}`,
      `total: ${baseline.total_findings}, baseline ${baseline.total_findings - 1}`,
    ]);
  });
});
