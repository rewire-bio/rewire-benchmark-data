/** The four decisions the deterministic pass is allowed to make, and the questions it leaves.
 *
 * Each decision is a lookup against something already written down: a SKOS label in
 * `data/vocab`, or the name of a record already in the store. None of them is a judgement. A
 * lookup that finds one answer decides the field; a lookup that finds none or several leaves it
 * empty and writes the question, with the document's own words as the evidence.
 *
 * The axis rule is the one thing here that is a reading of the table rather than a lookup, and
 * it is made once per table rather than once per cell. A comparison table puts the systems down
 * the rows and the metrics across the columns far more often than the other way round, so that
 * is the default; the other way round is taken only where the store recognises strictly more
 * column headings as systems than it recognises row labels. Deciding per cell would let one
 * table answer in both directions, which is a table nobody could check.
 */
import { conceptLabels, lookup, printedUnit, recordNames, type LabelIndex, type NamedRecord } from "./labels";
import type { CandidateField, Undecided } from "./candidate";
import fs from "node:fs";
import path from "node:path";
import { Parser } from "n3";

const RB = "https://benchmarks.rewire.it/vocab#";

/** Record kinds whose names a table row or column heading may be naming.
 *
 * `model` is in the list and is not the only kind in it. The store's own contract says a
 * comparison table holds a method the authors wrote or a published model as they configured
 * it, which is why `batch.ts` refuses to emit a bare `model`. The task's word for this field is
 * "the model"; the store's word is whichever of these five the entity is. */
export const systemKinds = ["model", "method", "configuration", "pipeline", "service"] as const;
/** Record kinds a table caption may be naming. */
export const assessmentKinds = ["benchmark", "task", "protocol"] as const;

/** Every lookup table the pass needs, built once per run. */
export interface Decider {
  metrics: LabelIndex;
  units: LabelIndex;
  /** Metric concept key to the direction the vocabulary declares, where it declares one. */
  directions: Map<string, string>;
  systems: LabelIndex;
  assessments: LabelIndex;
}

/** `rb:defaultDirection` on each metric concept, as the key at the end of the direction IRI. */
export function metricDirections(root = "."): Map<string, string> {
  const file = path.join(root, "data", "vocab", "metric.ttl");
  const out = new Map<string, string>();
  if (!fs.existsSync(file)) return out;
  const base = "https://benchmarks.rewire.it/vocab/metric/";
  const direction = "https://benchmarks.rewire.it/vocab/direction/";
  for (const quad of new Parser({ format: "Turtle" }).parse(fs.readFileSync(file, "utf8"))) {
    if (quad.predicate.value !== `${RB}defaultDirection`) continue;
    if (!quad.subject.value.startsWith(base) || !quad.object.value.startsWith(direction)) continue;
    out.set(quad.subject.value.slice(base.length), quad.object.value.slice(direction.length));
  }
  return out;
}

export function buildDecider(records: NamedRecord[], root = "."): Decider {
  return {
    metrics: conceptLabels("metric", root),
    units: conceptLabels("unit", root),
    directions: metricDirections(root),
    systems: recordNames(records.filter((record) => (systemKinds as readonly string[]).includes(record.kind))),
    assessments: recordNames(records.filter((record) => (assessmentKinds as readonly string[]).includes(record.kind))),
  };
}

const empty = (printed: string, read_from: string): CandidateField => ({ printed, decided: null, read_from });

/** The levels of a column heading, deepest first, with the blanks dropped.
 *
 * A two-level heading prints "AUROC" under "Variant effect", and the metric is the leaf. The
 * level above is tried next, because a table that prints the metric once over a band of
 * columns puts it at the top and the sub-columns hold the split. Nothing is joined: "Variant
 * effect AUROC" is a string the document never prints, and matching it against a label would
 * be matching against text that exists nowhere. */
export const headingLevels = (path: string[]): string[] => path.filter((level) => level.trim() !== "").reverse();

/** The parenthetical at the end of a heading, which is where a table prints a unit. */
export function trailingParenthetical(heading: string): string | null {
  const match = /\(([^()]{1,24})\)\s*$/.exec(heading.trim());
  return match ? match[1].trim() : null;
}

/** The first heading level that names exactly one concept, with what was tried. */
function conceptFromHeading(index: LabelIndex, levels: string[]): { printed: string; decided: string | null; ambiguous: boolean } {
  let ambiguous = false;
  for (const level of levels) {
    const { decided, matches } = lookup(index, level);
    if (decided) return { printed: level, decided, ambiguous: false };
    if (matches > 1) ambiguous = true;
  }
  return { printed: levels[0] ?? "", decided: null, ambiguous };
}

/** What one cell's fields are, and the questions the empty ones leave.
 *
 * `metricText` and `systemText` are already the right way round for this table: the caller
 * applies the axis rule and hands this the heading the metric is read from and the label the
 * system is read from.
 */
export function decideCell(
  decider: Decider,
  input: {
    metricLevels: string[];
    metricReadFrom: string;
    systemText: string;
    systemReadFrom: string;
    assessmentText: string;
    assessmentReadFrom: string;
    printedValue: string;
    headerPresent: boolean;
    headerReason: "no_header_marked" | "header_blank" | null;
  },
): { fields: Record<"metric" | "direction" | "unit" | "model" | "assessment", CandidateField>; undecided: Undecided[] } {
  const undecided: Undecided[] = [];
  const leaf = input.metricLevels[0] ?? "";

  // Metric.
  let metric: CandidateField;
  if (!input.headerPresent) {
    metric = empty("", input.metricReadFrom);
    undecided.push({
      field: "metric",
      reason: input.headerReason ?? "no_header_marked",
      evidence: "",
      decide: "which quantity this column reports, from the table's caption and the surrounding text, since the markup marks no heading over it",
    });
  } else {
    const found = conceptFromHeading(decider.metrics, input.metricLevels);
    if (found.decided) metric = { printed: found.printed, decided: found.decided, read_from: input.metricReadFrom };
    else {
      metric = empty(found.printed, input.metricReadFrom);
      undecided.push({
        field: "metric",
        reason: found.ambiguous ? "concept_ambiguous" : "no_concept_matched",
        evidence: input.metricLevels.join(" | "),
        decide: `which concept of data/vocab/metric.ttl the heading ${JSON.stringify(found.printed)} names, or that it names none`,
      });
    }
  }

  // Direction follows the metric and is never read off the numbers.
  let direction: CandidateField;
  const declared = metric.decided ? decider.directions.get(metric.decided) : undefined;
  if (declared) direction = { printed: "", decided: declared, read_from: "metric_concept" };
  else {
    direction = empty("", "metric_concept");
    undecided.push({
      field: "direction",
      reason: "no_concept_matched",
      evidence: metric.decided ?? "",
      decide: metric.decided
        ? `whether a higher or a lower ${metric.decided} is better, which data/vocab/metric.ttl does not declare for that concept`
        : "whether a higher or a lower value is better, which follows from the metric once the metric is decided",
    });
  }

  // Unit. The percent sign, or a parenthetical the unit scheme already names.
  let unit: CandidateField;
  const printed = printedUnit(input.printedValue, leaf);
  const bracket = trailingParenthetical(leaf);
  const fromBracket = bracket ? lookup(decider.units, bracket) : { decided: null, matches: 0 };
  if (printed) unit = { printed: "%", decided: printed, read_from: /%/.test(input.printedValue) ? "printed_value" : input.metricReadFrom };
  else if (fromBracket.decided) unit = { printed: bracket!, decided: fromBracket.decided, read_from: input.metricReadFrom };
  else {
    unit = empty(bracket ?? "", input.metricReadFrom);
    undecided.push({
      field: "unit",
      reason: fromBracket.matches > 1 ? "concept_ambiguous" : "no_unit_printed",
      evidence: leaf,
      decide: `which concept of data/vocab/unit.ttl this column's values carry; the document prints no unit mark, and percent against fraction against unitless on a proportion metric is the convention question ADR 0002 leaves to a person`,
    });
  }

  // The system, by exact name against the store.
  let model: CandidateField;
  if (input.systemText.trim() === "") {
    model = empty("", input.systemReadFrom);
    undecided.push({
      field: "model",
      reason: "no_row_label",
      evidence: "",
      decide: "what this row is a row of, which the table prints nowhere this pass can read",
    });
  } else {
    const found = lookup(decider.systems, input.systemText);
    if (found.decided) model = { printed: input.systemText, decided: found.decided, read_from: input.systemReadFrom };
    else {
      model = empty(input.systemText, input.systemReadFrom);
      undecided.push({
        field: "model",
        reason: found.matches > 1 ? "record_ambiguous" : "no_record_matched",
        evidence: input.systemText,
        decide: `which stored ${systemKinds.join(", ")} record the printed name ${JSON.stringify(input.systemText)} is, or that it is a new one`,
      });
    }
  }

  // The benchmark or task, from the caption.
  let assessment: CandidateField;
  if (input.assessmentText.trim() === "") {
    assessment = empty("", input.assessmentReadFrom);
    undecided.push({
      field: "assessment",
      reason: "no_anchor_text",
      evidence: "",
      decide: "which benchmark or task this table reports, which the document labels nowhere this pass can read",
    });
  } else {
    const found = lookup(decider.assessments, input.assessmentText);
    if (found.decided) assessment = { printed: input.assessmentText, decided: found.decided, read_from: input.assessmentReadFrom };
    else {
      assessment = empty(input.assessmentText, input.assessmentReadFrom);
      undecided.push({
        field: "assessment",
        reason: found.matches > 1 ? "record_ambiguous" : "no_record_matched",
        evidence: input.assessmentText,
        decide: `which benchmark, task or protocol record this caption names, which needs the caption read as a sentence rather than matched as a name`,
      });
    }
  }

  return { fields: { metric, direction, unit, model, assessment }, undecided };
}

/**
 * Which way round the table is, decided once for the whole table.
 *
 * The store is asked, not the text: how many row labels name a system it holds, against how
 * many column headings do. Strictly more headings than labels is the only thing that moves it
 * off the default, so a table the store recognises nothing in stays the way round that tables
 * usually are.
 */
export function orientationOf(decider: Decider, rowLabels: string[], columnHeadings: string[]): "systems_in_rows" | "systems_in_columns" {
  const hits = (labels: string[]) => labels.filter((label) => lookup(decider.systems, label).decided !== null).length;
  return hits(columnHeadings) > hits(rowLabels) ? "systems_in_columns" : "systems_in_rows";
}
