/** C4: what metric_qualifier holds.
 *
 * metric_qualifier is free text and its job is to distinguish one result from another result
 * of the same metric on the same benchmark: which split, which subset, which aggregation. A
 * qualifier that is a bare verdict (yes, no, high, max) distinguishes nothing, and a vendor
 * effort label (xhigh, low effort, medium effort) names a setting of a commercial product
 * rather than a property of the measurement, so it belongs in scoring_conditions.
 *
 * The rule is a token list. A token matches when it stands alone: the boundary characters are
 * the start or end of the string, whitespace, a comma, a semicolon or a bracket. A hyphen is
 * deliberately not a boundary, so "high-ranking docking false positives" and "min-max
 * normalised" do not match while "High quality (DockQ >= 0.80)" and "max absolute track
 * aggregation" do. One finding per token per result, so a qualifier holding two tokens is two
 * findings.
 *
 * Measured on the first run: 338 findings, splitting high 171, no 161 and max 6. The other
 * four tokens do not occur. They are kept in the list because the list is the rule, and a
 * token that starts occurring should raise the count rather than pass unseen.
 */
import type { Check, CheckInput, Finding } from "./finding";
import { text } from "./finding";

/** Verdicts first, then vendor effort labels. */
const tokens = ["yes", "no", "max", "high", "xhigh", "low effort", "medium effort"] as const;

const escape = (token: string) => token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const matcher = (token: string) => new RegExp(`(^|[;,(\\s])${escape(token)}($|[;,)\\s])`, "i");
const matchers = tokens.map((token) => ({ token, re: matcher(token) }));

export const qualifierShape: Check = {
  id: "C4",
  title: "qualifier shape",
  rules: ["verdict-or-vendor-token"],
  run({ results }: CheckInput): Finding[] {
    const findings: Finding[] = [];
    for (const record of results) {
      const qualifier = text(record, "metric_qualifier");
      if (!qualifier) continue;
      for (const { token, re } of matchers) {
        if (!re.test(qualifier)) continue;
        findings.push({
          check: "C4",
          rule: "verdict-or-vendor-token",
          severity: "report",
          subject: record.id,
          detail: `metric_qualifier holds the token "${token}": ${JSON.stringify(qualifier)}`,
        });
      }
    }
    return findings;
  },
  context({ results }: CheckInput, findings: Finding[]): Record<string, number> {
    const counts: Record<string, number> = { results_with_a_qualifier: 0, results_flagged: new Set(findings.map((f) => f.subject)).size };
    for (const record of results) if (text(record, "metric_qualifier")) counts.results_with_a_qualifier += 1;
    for (const { token, re } of matchers)
      counts[`token_${token.replace(/\s+/g, "_")}`] = results.filter((record) => {
        const qualifier = text(record, "metric_qualifier");
        return qualifier ? re.test(qualifier) : false;
      }).length;
    return counts;
  },
};
