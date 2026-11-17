/** C2: metric_direction against the metric concept's rb:defaultDirection.
 *
 * data/vocab/metric.ttl gives all 275 metric concepts an rb:defaultDirection. One of the three
 * direction concepts is `unknown`, and a concept pointing at it is declaring that the metric
 * has no default: whether higher is better depends on what was measured. So the three rules
 * are not symmetrical.
 *
 * opposite. The concept declares higher or lower and the result asserts the other one. This is
 * the rule worth reading first: one of the two is wrong, and which one it is cannot be decided
 * without the source.
 *
 * unknown-where-declared. The concept declares a direction and the result stores `unknown`.
 * The record is less specific than the vocabulary allows, which usually means the extractor
 * did not look the metric up.
 *
 * asserted-where-none. The concept declares no default (rb:defaultDirection unknown) and the
 * result asserts higher or lower. Not an error by itself, and often the right call, because
 * the direction of a count or a proportion is a property of the measurement rather than of the
 * metric. It is reported because an assertion the vocabulary cannot support should be visible,
 * and because it is the queue from which rb:defaultDirection gains per-metric exceptions.
 *
 * Measured on the first run: 1,256 findings, splitting 58 opposite, 206 unknown-where-declared
 * and 992 asserted-where-none.
 */
import type { Check, CheckInput, Finding } from "./finding";
import { text } from "./finding";

export const directionDefault: Check = {
  id: "C2",
  title: "direction against the metric default",
  rules: ["opposite", "unknown-where-declared", "asserted-where-none", "metric-not-a-concept"],
  run({ results, metrics }: CheckInput): Finding[] {
    const findings: Finding[] = [];
    for (const record of results) {
      const metric = text(record, "metric");
      const direction = text(record, "metric_direction");
      if (!metric || !direction) continue;
      const concept = metrics.get(metric);
      if (!concept) {
        findings.push({
          check: "C2",
          rule: "metric-not-a-concept",
          severity: "report",
          subject: record.id,
          detail: `metric ${metric} is not a concept in data/vocab/metric.ttl`,
        });
        continue;
      }
      const declared = concept.defaultDirection;
      if (declared === null) {
        if (direction !== "unknown")
          findings.push({
            check: "C2",
            rule: "asserted-where-none",
            severity: "report",
            subject: record.id,
            detail: `metric ${metric} declares no default direction; the result asserts ${direction}`,
          });
      } else if (direction === "unknown") {
        findings.push({
          check: "C2",
          rule: "unknown-where-declared",
          severity: "report",
          subject: record.id,
          detail: `metric ${metric} declares default direction ${declared}; the result stores unknown`,
        });
      } else if (direction !== declared) {
        findings.push({
          check: "C2",
          rule: "opposite",
          severity: "report",
          subject: record.id,
          detail: `metric ${metric} declares default direction ${declared}; the result stores ${direction}`,
        });
      }
    }
    return findings;
  },
  context({ metrics }: CheckInput): Record<string, number> {
    return {
      metric_concepts: metrics.size,
      metric_concepts_declaring_a_direction: [...metrics.values()].filter((c) => c.defaultDirection !== null).length,
    };
  },
};
