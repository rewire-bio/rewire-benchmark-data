/** What one deterministic pass over a source produces, and what it may never produce.
 *
 * A candidate is not a record. It is the smallest thing a later stage, a reviewer or a model,
 * can act on: one printed number, the place in a hashed text layer it is printed, and the
 * labels the document itself puts around it. ADR 0002 decision 6 keeps candidates in files so
 * that nothing candidate-shaped can reach the published bundle.
 *
 * Two rules decide the shape and neither is negotiable.
 *
 * 1. A candidate with no span is not emitted. The span is what lets a stranger open the layer
 *    the archive holds and read the same characters. A number with no span is a number
 *    somebody typed, and this file has no way to express one.
 * 2. A field the pass cannot decide is empty and is named in `undecided`, with the printed
 *    evidence a later stage would decide from. It is never guessed and never defaulted. That
 *    is what keeps the model-free baseline measurable on its own: the count of undecided
 *    entries by field is the work a model stage would have to do, stated before the model
 *    stage exists.
 *
 * Nothing here records a clock. The candidate file is a function of the layer bytes and the
 * store, so two runs over the same archive produce the same bytes and a diff means something
 * changed.
 */
import { z } from "zod";
import { spanSchema } from "../locator";

/** Which deterministic reader produced the candidate. One per geometry the archive carries.
 *
 * There is no PDF route. `shared/archive/layers/grid/index.ts` records why: a
 * `pdftotext -layout` layer gives aligned text and the only way to a column from aligned text
 * is to infer one from runs of spaces, which is wrong on every table with a spanning header.
 * A PDF source therefore yields no cell candidates from this pass, which is a measurement and
 * not a failure. */
export const routes = ["grid_cell", "sheet_cell"] as const;
export type Route = (typeof routes)[number];

/** Why a field is empty. Each one is a fact about the document or the store, never a verdict
 * on the value. */
export const undecidedReasons = [
  /** The markup marked no header row, so no column heading stands over the cell. */
  "no_header_marked",
  /** A heading row exists and prints nothing over this column. */
  "header_blank",
  /** The heading matches no concept in the scheme. */
  "no_concept_matched",
  /** The heading matches more than one concept, so the pass may not pick. */
  "concept_ambiguous",
  /** Nothing in the printed cell or its heading names a unit. */
  "no_unit_printed",
  /** The table prints no label in the first column of this row. */
  "no_row_label",
  /** The printed name matches no record in the store. */
  "no_record_matched",
  /** The printed name matches more than one record. */
  "record_ambiguous",
  /** The document prints no caption or label for the table the cell sits in. */
  "no_anchor_text",
] as const;
export type UndecidedReason = (typeof undecidedReasons)[number];

/** One field a later stage has to settle, with what it would settle it from. */
export const undecidedSchema = z
  .object({
    /** The candidate field that is empty: `metric`, `unit`, `model` or `assessment`. */
    field: z.string().min(1),
    reason: z.enum(undecidedReasons),
    /** The text the document prints at the place the field would be read from. Empty where
     * the document prints nothing there, which is itself the evidence. */
    evidence: z.string(),
    /** What a later stage has to decide, in one sentence, so the question is on the record
     * before anything is built to answer it. */
    decide: z.string().min(1),
  })
  .strict();
export type Undecided = z.infer<typeof undecidedSchema>;

/** A field the pass either decided or left empty.
 *
 * `printed` is always the document's own words, verbatim, including when nothing was decided
 * from them. `decided` is a concept key or a store record id, and null means undecided. The
 * two are kept apart because the printed text is evidence and the decision is an
 * interpretation, and conflating them is how a wrong model name becomes a stored fact. */
export const fieldSchema = z
  .object({
    printed: z.string(),
    decided: z.string().nullable(),
    /** Where in the document `printed` was read: `column_header`, `row_label`, `caption`,
     * `table_label`, `sheet_name`, `printed_value`, or `none`. */
    read_from: z.string().min(1),
  })
  .strict();
export type CandidateField = z.infer<typeof fieldSchema>;

/** Where the column heading came from, which decides how much it is worth.
 *
 * `markup` is a header row the markup marked. `inferred` is the one inference a grid carries,
 * `GridInferredHeader`, kept in its own field there and in its own value here so that a reader
 * who declines inferences has one word to look at. `first_row` is a sheet's row 1, which is
 * where `shared/omics/spans/sheet.ts` says a sheet puts its column names. */
export const headerSources = ["markup", "inferred", "first_row", "none"] as const;
export type HeaderSource = (typeof headerSources)[number];

export const candidateSchema = z
  .object({
    /** Stable over reruns: a digest of the source, the layer, the table and the cell
     * coordinates. Not a content hash, so a candidate keeps its name when a neighbouring cell
     * changes. */
    candidate_id: z.string().regex(/^[a-f0-9]{16}$/),
    source_id: z.string().min(1),
    /** The text layer the span indexes. */
    layer_sha256: z.string().regex(/^[a-f0-9]{64}$/),
    normaliser: z.string().min(1),
    route: z.enum(routes),
    /** The grid layer the geometry was read from, for a grid cell. Null for a sheet cell,
     * where the geometry is in the text layer itself. */
    grid_layer_sha256: z.string().regex(/^[a-f0-9]{64}$/).nullable(),
    /** The table or sheet, as the document names it. */
    anchor: z
      .object({
        kind: z.enum(["table", "sheet"]),
        /** Zero based for a grid table, one based for a sheet block, as each counts itself. */
        index: z.number().int(),
        /** The label the markup writes, such as "Table 3", or the sheet name. */
        label: z.string(),
        caption: z.string(),
      })
      .strict(),
    /** Zero based row and column within the table, or the sheet's own one-based row and
     * column numbers. `basis` says which. */
    position: z
      .object({ row: z.number().int(), column: z.number().int(), basis: z.enum(["grid", "a1"]) })
      .strict(),
    row_label: z.string(),
    /** One entry per header level over this column, top level first. */
    column_header: z.array(z.string()),
    header_source: z.enum(headerSources),
    /** The rule that put forward an inferred header, where one did. */
    header_rule: z.string().nullable(),

    metric: fieldSchema,
    /** Which way is better, read off `rb:defaultDirection` on the metric concept. It follows
     * the metric and is never read off the numbers, so it is decided exactly when the metric
     * is and the vocabulary states one. */
    direction: fieldSchema,
    unit: fieldSchema,
    /** What was evaluated. The task calls this the model; the store's kinds call a table row a
     * method, configuration, pipeline or service as often as a model, so the printed name is
     * what travels and the record id is the decision. */
    model: fieldSchema,
    /** The benchmark or task. */
    assessment: fieldSchema,

    /** The value exactly as the layer prints it. */
    printed_value: z.string().min(1),
    /** The same value as a decimal string, or null where the cell prints a value the parser
     * reads as not reported. */
    numeric_value: z.string().nullable(),
    /** The spread the cell prints beside the value, verbatim, where it prints one. Its
     * meaning is not decided here: ADR 0002 and the record contract both say a printed spread
     * the source does not define is an unresolved spread and never a standard deviation. */
    uncertainty_printed: z.string().nullable(),

    /** The cell, in the text layer. */
    span: spanSchema,
    /** The row label and the column heading, in the same layer. These are the redundancy ADR
     * 0002 decision 2 requires: a cell span that cannot name its own row and column has no
     * defence against having resolved to a plausible neighbour. */
    row_label_span: spanSchema.nullable(),
    column_header_span: spanSchema.nullable(),

    /** The locator as structure, authored rather than parsed, as ADR 0002 decision 2 requires
     * of a new batch. */
    locator: z.record(z.string(), z.unknown()),
    /** `renderLocator(locator)`, which is what a record would carry in `source_locator`. */
    source_locator: z.string().min(1),

    undecided: z.array(undecidedSchema),
    /** True when `undecided` is empty: every field a record needs was decided from the
     * document and the store, with no model and no person. */
    complete: z.boolean(),
  })
  .strict();
export type Candidate = z.infer<typeof candidateSchema>;

/** What the pass saw, so the candidates can be read against the document rather than on their
 * own. Every count is an integer over one source, and the identity the report checks is
 * `cells_seen = cells_header + cells_label + cells_empty + cells_not_numeric + candidates`. */
export const tallySchema = z
  .object({
    source_id: z.string().min(1),
    /** One entry per layer the pass read. */
    layers: z.array(
      z
        .object({
          layer_sha256: z.string(),
          normaliser: z.string(),
          sanity: z.string(),
          route: z.string(),
          tables: z.number().int(),
          cells_seen: z.number().int(),
          /** Cells in a header row, which carry the column names rather than a value. */
          cells_header: z.number().int(),
          /** Cells in the column the row labels are read from. */
          cells_label: z.number().int(),
          /** Cells the markup wrote that print nothing, which carry no span. */
          cells_empty: z.number().int(),
          /** Cells that print something the numeric parser will not read as a number. */
          cells_not_numeric: z.number().int(),
          candidates: z.number().int(),
        })
        .strict(),
    ),
    /** Layers the pass could not read a geometry from, with the reason. A PDF layer is here,
     * always, by design. */
    skipped: z.array(
      z.object({ layer_sha256: z.string(), normaliser: z.string(), reason: z.string() }).strict(),
    ),
    candidates: z.number().int(),
    complete: z.number().int(),
    /** Candidates carrying at least one undecided field. */
    needs_completion: z.number().int(),
    /** How many candidates leave each field empty. */
    undecided_by_field: z.record(z.string(), z.number().int()),
    undecided_by_reason: z.record(z.string(), z.number().int()),
  })
  .strict();
export type Tally = z.infer<typeof tallySchema>;
