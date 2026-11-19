/** Printed labels to concept keys and record ids, by exact match and nothing else.
 *
 * A column headed "AUROC" names the metric concept `auroc`, and a pass that reads it as such
 * has decided nothing: the vocabulary already carries "AUROC" as an alternative label of that
 * concept, and the match is a lookup. A column headed "Performance" names no concept, and a
 * pass that picks one has invented a fact. So the rule here is one match or none: zero
 * candidates and two candidates are both left undecided, with the printed text carried through
 * as the evidence a later stage would read.
 *
 * Matching is `normaliseLabel` from `shared/omics/spans/table.ts`, which is what the span
 * resolvers compare labels with. Using a second normalisation here would mean a heading that
 * resolves a span and a heading that names a metric are compared by different rules.
 *
 * No fuzzy matching, no stemming, no prefix rule. Every one of those turns a miss into a wrong
 * answer at some rate, and nothing downstream could tell which. The measured cost is that the
 * pass decides fewer fields, which is reported rather than hidden.
 */
import fs from "node:fs";
import path from "node:path";
import { Parser } from "n3";
import { normaliseLabel } from "../spans/table";

const SKOS = "http://www.w3.org/2004/02/skos/core#";

/** A normalised printed label to the keys or ids that carry it. */
export type LabelIndex = Map<string, string[]>;

const add = (index: LabelIndex, label: string, value: string) => {
  const key = normaliseLabel(label);
  if (key === "") return;
  const held = index.get(key);
  if (!held) index.set(key, [value]);
  else if (!held.includes(value)) held.push(value);
};

/**
 * Every preferred and alternative label of one SKOS scheme, pointing at the concept key.
 *
 * `loadSchemes` in `scripts/omics/vocab.ts` keeps only the preferred label, because validation
 * only needs to know a key exists. Matching a printed heading needs the alternatives: the
 * metric scheme carries "ACC", "ACC (%)" and "overall_accuracy" on `accuracy`, and those are
 * what a table actually prints.
 */
export function conceptLabels(scheme: string, root = "."): LabelIndex {
  const file = path.join(root, "data", "vocab", `${scheme}.ttl`);
  const index: LabelIndex = new Map();
  if (!fs.existsSync(file)) return index;
  const base = `https://benchmarks.rewire.it/vocab/${scheme}/`;
  for (const quad of new Parser({ format: "Turtle" }).parse(fs.readFileSync(file, "utf8"))) {
    if (quad.predicate.value !== `${SKOS}prefLabel` && quad.predicate.value !== `${SKOS}altLabel`) continue;
    if (!quad.subject.value.startsWith(base)) continue;
    const key = quad.subject.value.slice(base.length);
    if (key === "") continue;
    add(index, quad.object.value, key);
  }
  return index;
}

/** A record the name index points at. */
export interface NamedRecord {
  id: string;
  kind: string;
  name?: string;
  attributes?: Record<string, unknown>;
}

/**
 * Store record names and reported names, pointing at the record id.
 *
 * `reported_name` is in here because it is the field the extraction skill puts a tool's printed
 * name in, which makes it the one field written to be matched against a table row. A record
 * whose name and reported name differ is reachable by both.
 */
export function recordNames(records: NamedRecord[]): LabelIndex {
  const index: LabelIndex = new Map();
  for (const record of records) {
    if (record.name) add(index, record.name, record.id);
    const reported = record.attributes?.reported_name;
    if (typeof reported === "string") add(index, reported, record.id);
  }
  return index;
}

/** The one value a printed label names, or null where it names none or several. */
export function lookup(index: LabelIndex, printed: string): { decided: string | null; matches: number } {
  const held = index.get(normaliseLabel(printed)) ?? [];
  return { decided: held.length === 1 ? held[0] : null, matches: held.length };
}

/**
 * The unit the cell itself prints, where it prints one.
 *
 * Only the percent sign, and only on the value or on the heading it sits under. Everything else
 * a table might print as a unit is a convention question that ADR 0002's own open-question
 * section leaves to a person: percent against fraction against unitless on a proportion metric
 * is 25 of the 36 contested metric concepts. So this reads the one mark whose meaning is not in
 * dispute and leaves the rest undecided.
 */
export function printedUnit(value: string, heading: string): string | null {
  if (/%/.test(value)) return "percent";
  if (/\(\s*%\s*\)|\bin\s*%|%\s*\)/.test(heading)) return "percent";
  return null;
}
