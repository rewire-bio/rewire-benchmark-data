/** What a resolver returns: a span, or a refusal with a stated reason.
 *
 * A locator says where a value came from in words a person can read. A span says where it is in a
 * layer, exactly, so a machine can re-check it with no model. A resolver turns the first into the
 * second or says why it cannot.
 *
 * Refusal is the common case and has to stay cheap. A resolver that guesses puts a wrong span on
 * a record, and a wrong span is worse than no span: it reads as a check that passed. So every
 * refusal names one reason from a closed list, and the measurement reports the list.
 */
import type { Span } from "../locator";

/** Which resolver read the locator. One per locator shape the store uses. */
export const spanKinds = [
  /** A table anchor with a row label and a column header, in column-aligned text. */
  "table_cell",
  /** The same, crossed against a table grid rather than against aligned text. Counted apart
   * from `table_cell` because the two read different geometry: one reads the horizontal
   * position a layout renderer left in the characters, the other reads the row and column the
   * markup wrote. */
  "grid_cell",
  /** A row and a column in a delimited file, by line number or by A1 notation. */
  "delimited_cell",
  /** A figure anchor: the span is the caption. */
  "figure_caption",
  /** A section heading and a paragraph number within it. */
  "section_paragraph",
  /** One page of a PDF text layer, between form feeds. */
  "page",
  /** A line or a range of lines. */
  "line_range",
  /** A quoted sentence or phrase, found in the layer. */
  "quote",
  /** The value an RFC 6901 JSON Pointer addresses, in the JSON text itself. */
  "json_value",
] as const;
export type SpanKind = (typeof spanKinds)[number];

/** Why a locator did not reach a span. Exactly one applies, and the groups are ordered: a locator
 * refused for want of a layer never reaches a resolver, so its reason is one of the first group.
 *
 * The first group is the archive's answer, copied from the layer registry's coverage buckets so
 * the two reports reconcile. The second is this lane's own reading of the locator. The third is a
 * resolver that read the layer and would not commit. */
export const refusalReasons = [
  // The substrate is missing. The archive lane owns these, not this one.
  "no_capture",
  "no_normaliser",
  "not_the_artifact",
  "layer_unusable",
  "layer_not_readable",
  // The locator does not address anything this lane resolves.
  "no_anchor",
  "no_resolver_for_kind",
  "no_column_geometry",
  "no_row_in_locator",
  "no_column_in_locator",
  // A resolver read the layer and refused.
  "anchor_not_found",
  "anchor_ambiguous",
  "empty_table_window",
  "column_not_found",
  "column_ambiguous",
  "column_unaligned",
  "column_merged",
  "row_not_found",
  "row_ambiguous",
  "row_key_unmatched",
  "cell_empty",
  "line_out_of_range",
  "page_out_of_range",
  "section_not_found",
  "section_ambiguous",
  "paragraph_out_of_range",
  "quote_not_found",
  "quote_ambiguous",
  "empty_span",
  "json_not_parsed",
] as const;
export type RefusalReason = (typeof refusalReasons)[number];

/** How a grid resolver found the table it read, where a grid was read at all.
 *
 * `label` is the label the markup wrote on the table itself. `caption_window` is a caption line
 * of the text layer, with the tables beginning under it and the table standing against it from
 * above as the candidates and only one of them allowed to yield the cell. It is the only route
 * to an HTML table and the weaker evidence of the two, so the measurement reports them apart.
 * `none` is a grid that was read and holds no table the anchor names.
 *
 * The field's presence on an outcome is what the measurement counts as a grid attempt. */
export const gridRoutes = ["label", "caption_window", "none"] as const;
export type GridRoute = (typeof gridRoutes)[number];

/** A refusal. `detail` is for a reader of the report and is never parsed. */
export interface Refusal {
  ok: false;
  reason: RefusalReason;
  detail: string;
  /** The layer the refusal was reached on, where one was read. */
  layer_sha256?: string;
  /** Set where a table grid was read. */
  grid_route?: GridRoute;
}

/** A span, with what the resolver crossed it against.
 *
 * `row_label` and `column_header` are the redundancy ADR 0002 decision 2 requires: a cell span
 * that cannot name the row and column it sits in has no defence against resolving to a plausible
 * neighbour. They carry the layer's own text, not the locator's, so a report can compare them. */
export interface Resolved {
  ok: true;
  kind: SpanKind;
  span: Span;
  layer_sha256: string;
  /** The row label as the layer prints it. */
  row_label?: string;
  /** The column header as the layer prints it. */
  column_header?: string;
  /** How many candidate places the resolver had to choose between, where it chose by
   * cross-check rather than because there was only one. Not a count of anchors: in the grid it is
   * the number of tables the route found, and in the plain-text path it is the number of regions
   * read around the matching captions, accumulated across the stages tried, so a span found in a
   * later stage counts the regions the earlier stages offered as well. */
  anchor_candidates?: number;
  /** Set where a table grid was read. */
  grid_route?: GridRoute;
}

export type Resolution = Resolved | Refusal;

export const refuse = (reason: RefusalReason, detail: string, layer_sha256?: string): Refusal =>
  layer_sha256 === undefined ? { ok: false, reason, detail } : { ok: false, reason, detail, layer_sha256 };
