/** Findings: what a deterministic check reports.
 *
 * A check is a pure function over the store and the vocabularies. It reads nothing else, calls
 * nothing over the network, and returns a list of findings. Every finding is report severity:
 * it names a record and a rule, it does not decide whether the record is wrong, and nothing in
 * this directory gates `npm run records -- add`.
 *
 * Counts are the deliverable. data/omics/checks-baseline.json pins the count of each rule from
 * the first run, and tests/checks-baseline.test.ts fails when a later run raises one, so the
 * backlog can be worked down but not grown.
 */

/** Report is the only severity this pack emits. The field exists so a later check can declare a
 * gate severity without changing the shape of the report. */
export type Severity = "report";

export type Finding = {
  /** The check that raised it: C1, C2, C3, C4, C5, C9 or C13. */
  check: string;
  /** The rule inside the check. Baselines and the ratchet are per rule, not per check. */
  rule: string;
  severity: Severity;
  /** The record ID, or a group key when the finding is about several records at once. */
  subject: string;
  /** One line of evidence, with the values that triggered the rule. */
  detail: string;
};

/** A stored record as the checks read it. Raw JSON from the store files, not schema validated:
 * the checks report on what is there rather than refusing to run on it. */
export type Rec = {
  id: string;
  kind: string;
  name?: string;
  status?: string;
  source_ids?: string[];
  links?: { relation: string; target_id: string }[];
  attributes: Record<string, unknown>;
};

/** A metric concept. `defaultDirection` is null when the concept declares none, which in
 * data/vocab/metric.ttl is written as rb:defaultDirection <.../direction/unknown>. */
export type MetricConcept = { key: string; defaultDirection: string | null };

/** A unit concept, with the scope note if it carries one. */
export type UnitConcept = { key: string; scopeNote: string | null };

export type CheckInput = {
  /** Every result record. */
  results: Rec[];
  /** Every source record. */
  sources: Rec[];
  /** Every record of every kind. C13 needs all of them because normalizeAttributes reads an
   * evaluation's links to resolve a result's parent. */
  records: Rec[];
  metrics: Map<string, MetricConcept>;
  units: Map<string, UnitConcept>;
};

export type Check = {
  id: string;
  title: string;
  /** Every rule this check can raise, in report order. A rule with no findings still gets a
   * baseline line of 0, so a rule that starts firing is caught by the ratchet. */
  rules: readonly string[];
  run(input: CheckInput): Finding[];
  /** Counts that describe the run rather than the findings: how many groups were formed, how
   * many records a rule could not be applied to. They are written to the baseline and shown in
   * the report. The ratchet does not test them, because a bigger store raises them honestly. */
  context?(input: CheckInput, findings: Finding[]): Record<string, number>;
};

const attr = (record: Rec, key: string): unknown => record.attributes?.[key];

/** A string attribute, or undefined when it is absent or is not a string. */
export const text = (record: Rec, key: string): string | undefined => {
  const value = attr(record, key);
  return typeof value === "string" ? value : undefined;
};

/** Tabs and newlines would break the TSV, so they are shown as spaces. */
export const oneLine = (value: string): string => value.replace(/[\t\r\n]+/g, " ").trim();

export const tsvHeader = "check\trule\tseverity\tsubject\tdetail";

export const tsvRow = (finding: Finding): string =>
  [finding.check, finding.rule, finding.severity, finding.subject, oneLine(finding.detail)].join("\t");

/** Count findings by rule, with every declared rule present even at zero. */
export function countByRule(check: Check, findings: Finding[]): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const rule of check.rules) counts[rule] = 0;
  for (const finding of findings) counts[finding.rule] = (counts[finding.rule] ?? 0) + 1;
  return counts;
}
