/** One candidate, assembled. Both passes end here so that both produce the same thing.
 *
 * The locator is authored as structure and the printed string is rendered from it, which is
 * what ADR 0002 decision 2 requires of a new batch: today the string is the record and the
 * structure is guessed back out of it, and afterwards a locator that does not round trip
 * cannot be written at all.
 */
import { createHash } from "node:crypto";
import type { LocatorAddress, LocatorAnchor, LocatorSelector, Span } from "../locator";
import { renderLocator } from "../locator";
import type { Candidate, CandidateField, HeaderSource, Route, Undecided } from "./candidate";

export interface CandidateInput {
  source_id: string;
  layer_sha256: string;
  normaliser: string;
  route: Route;
  grid_layer_sha256: string | null;
  anchor: { kind: "table" | "sheet"; index: number; label: string; caption: string };
  position: { row: number; column: number; basis: "grid" | "a1" };
  row_label: string;
  column_header: string[];
  header_source: HeaderSource;
  header_rule: string | null;
  fields: Record<"metric" | "direction" | "unit" | "model" | "assessment", CandidateField>;
  printed_value: string;
  numeric_value: string | null;
  uncertainty_printed: string | null;
  span: Span;
  row_label_span: Span | null;
  column_header_span: Span | null;
  /** The address the locator carries, where the geometry has one a reader can write. A grid
   * cell has none: the markup gives the table and the row and column labels, and no A1
   * reference exists to name. */
  address: LocatorAddress | null;
  undecided: Undecided[];
}

/** The identifier, stable across reruns over the same archive. */
export const candidateId = (input: CandidateInput): string =>
  createHash("sha256")
    .update(
      [input.source_id, input.layer_sha256, input.route, input.anchor.index, input.position.row, input.position.column].join("\u0000"),
    )
    .digest("hex")
    .slice(0, 16);

const quoted = (key: string, value: string): LocatorSelector => ({ key, value, form: "quoted", raw: `${key} '${value}'` });

/** The identifier a table prints for itself, from its label or from the head of its caption.
 *
 * Both markup normalisers write the label where the markup marks one, and plenty of HTML marks
 * none and prints "Table 2." as the first words of the caption instead. Reading it from there
 * is still reading what the document prints.
 */
export function tableIdentifier(label: string, caption: string): string {
  const fromLabel = label.replace(/^\s*(?:table|tab\.?)\s*/i, "").replace(/[.:,\s]+$/, "").trim();
  if (fromLabel !== "") return fromLabel;
  const head = /^\s*(?:table|tab\.?)\s*([A-Za-z]?[0-9]+[A-Za-z]?(?:\.[0-9]+)?)\b/i.exec(caption);
  return head ? head[1] : "";
}

/**
 * The anchor a table or a sheet gives the locator, or none.
 *
 * A table the document labels is addressed by that label, which is what a reader of the paper
 * would write. A table the document labels nowhere gets no anchor at all. The alternative is to
 * number it by its position and write "Table 4" for a table the document never calls Table 4,
 * and a string that parses as a false claim about the document is worse than a weak one: the
 * span is the address that matters, and it is on the candidate either way.
 */
export function anchorOf(anchor: CandidateInput["anchor"]): LocatorAnchor | null {
  if (anchor.kind === "sheet") return { kind: "sheet", value: anchor.label, raw: `sheet '${anchor.label}'` };
  const identifier = tableIdentifier(anchor.label, anchor.caption);
  if (identifier === "") return null;
  return { kind: "table", value: identifier, raw: `Table ${identifier}` };
}

export function buildCandidate(input: CandidateInput): Candidate {
  const anchor = anchorOf(input.anchor);
  const anchors = anchor ? [anchor] : [];
  const selectors: LocatorSelector[] = [];
  if (input.row_label.trim() !== "") selectors.push(quoted("row", input.row_label));
  const heading = input.column_header.filter((level) => level.trim() !== "").slice(-1)[0] ?? "";
  if (heading !== "") selectors.push(quoted("column", heading));
  const qualifiers = [{ kind: "layer" as const, text: `layer ${input.layer_sha256.slice(0, 12)}` }];
  const locator = {
    anchors,
    ...(input.address ? { address: input.address } : {}),
    selectors,
    qualifiers,
    span: input.span,
  };
  const printed = renderLocator({ anchors, address: input.address ?? undefined, selectors, qualifiers });
  return {
    candidate_id: candidateId(input),
    source_id: input.source_id,
    layer_sha256: input.layer_sha256,
    normaliser: input.normaliser,
    route: input.route,
    grid_layer_sha256: input.grid_layer_sha256,
    anchor: input.anchor,
    position: input.position,
    row_label: input.row_label,
    column_header: input.column_header,
    header_source: input.header_source,
    header_rule: input.header_rule,
    metric: input.fields.metric,
    direction: input.fields.direction,
    unit: input.fields.unit,
    model: input.fields.model,
    assessment: input.fields.assessment,
    printed_value: input.printed_value,
    numeric_value: input.numeric_value,
    uncertainty_printed: input.uncertainty_printed,
    span: input.span,
    row_label_span: input.row_label_span,
    column_header_span: input.column_header_span,
    locator: { ...locator, printed },
    source_locator: printed,
    undecided: input.undecided,
    complete: input.undecided.length === 0,
  };
}
