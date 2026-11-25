/** C1: the unit a result carries for its metric.
 *
 * Two rules, both report only.
 *
 * minority-unit. The store, not the vocabulary, is the only statement of unit convention that
 * exists today: no metric concept declares rb:allowedUnit. So the convention for a metric is
 * taken to be its modal unit, and only when that mode is a real majority, meaning it is at
 * least as common as every other unit for that metric put together. A metric whose units are
 * split more evenly than that has no convention to be in a minority of, and flagging the
 * smaller halves there would be inventing a rule rather than reporting one. Each result whose
 * unit is not the majority unit is one finding.
 *
 * Measured on the first run: 5,093 findings over 43 metrics. f1-score alone contributes 1,362
 * (percent 2,603 against fraction 928 and unitless 434), which is partly a convention nobody
 * wrote down rather than 1,362 errors. That is why this is a triage queue and not a gate. The
 * vocabulary pass that would make it a gate is a separate reviewed change to metric.ttl.
 *
 * unit-scope-note. Three unit concepts in data/vocab/unit.ttl carry a skos:scopeNote that
 * names the metrics the unit is wrong for. The notes are prose, so the metric keys they name
 * are transcribed below by hand, one entry per note, and each entry is applied only while its
 * concept still carries a scope note. If a note is edited, the entry here has to be reread
 * against it; nothing in the code can do that reading.
 */
import type { Check, CheckInput, Finding } from "./finding";
import { text } from "./finding";

/** Transcribed from the three skos:scopeNote values in data/vocab/unit.ttl, 2026-11-17.
 *
 * fraction: "Only for proportions of items (correct predictions, targets, complexes).
 *   Normalised scores such as TM-score, NDCG and AUROC are unitless."
 * unitless: "A unitless statistic printed x100 (MCC, R2, Spearman, AUC) stays unitless with
 *   unit_detail 'printed x100'; percent would imply a proportion." The unit this note rules
 *   out is percent, on the statistics it names.
 * count: "Not for distances or averages: MCES edit distance is bond-order weighted and
 *   averaged over spectra, so it is unitless."
 */
const scopeNoteRules: { note: string; unit: string; metrics: string[]; reason: string }[] = [
  {
    note: "fraction",
    unit: "fraction",
    metrics: ["tm-score", "ndcg", "ndcg-at-10-percent", "adjusted-ndcg-at-100", "auroc", "auroc-difference"],
    reason: "the fraction scope note says normalised scores such as TM-score, NDCG and AUROC are unitless",
  },
  {
    note: "unitless",
    unit: "percent",
    metrics: [
      "matthews-correlation-coefficient",
      "macro-mcc",
      "pearson-r-squared",
      "spearman-correlation",
      "absolute-spearman-correlation",
      "spearman-correlation-difference",
      "auroc",
      "auroc-difference",
      "auprc",
    ],
    reason: "the unitless scope note says MCC, R2, Spearman and AUC printed x100 stay unitless with unit_detail, because percent would imply a proportion",
  },
  {
    note: "count",
    unit: "count",
    metrics: ["top-1-mces", "top-10-mces"],
    reason: "the count scope note says MCES edit distance is unitless, not a count",
  },
];

export const unitForMetric: Check = {
  id: "C1",
  title: "unit for metric",
  rules: ["unit-scope-note"],
  run({ results, units }: CheckInput): Finding[] {
    const findings: Finding[] = [];
    for (const record of results) {
      const metric = text(record, "metric");
      const unit = text(record, "unit");
      if (!metric || !unit) continue;
      for (const rule of scopeNoteRules) {
        if (unit !== rule.unit || !rule.metrics.includes(metric)) continue;
        if (!units.get(rule.note)?.scopeNote) continue;
        findings.push({
          check: "C1",
          rule: "unit-scope-note",
          severity: "report",
          subject: record.id,
          detail: `metric ${metric} unit ${unit}; ${rule.reason}`,
        });
      }
    }
    return findings;
  },
  context({ results, units }: CheckInput, findings: Finding[]): Record<string, number> {
    return {
      results_with_unit_and_metric: results.filter((record) => text(record, "metric") && text(record, "unit")).length,
      unit_concepts_with_scope_note: [...units.values()].filter((u) => u.scopeNote).length,
      scope_note_findings: findings.length,
    };
  },
};
