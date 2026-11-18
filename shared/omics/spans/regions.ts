/** Resolvers that address a region of a layer directly: a delimited cell, a line range, a page.
 *
 * These are the locators that need no caption and no label, because the address is the answer.
 * They are also the ones where a counting convention has to be written down rather than assumed,
 * so each is stated here:
 *
 *   line N        the Nth physical line of the layer, counted from 1, newline as the separator.
 *                 Not RFC 7111's record count: a quoted field holding a newline makes a record
 *                 span two lines, and the stored locators were written by someone reading a file
 *                 in an editor. A file with such a field is refused rather than renumbered.
 *   row N         the same, so "row 12" and "line 12" address one line.
 *   A1 notation   column letters from A, row number from 1, the header being row 1.
 *   page N        the Nth form-feed-separated region of a PDF text layer, counted from 1.
 */
import { spanAt, spanOfLines, type LayerIndex } from "./offsets";
import { normaliseLabel } from "./table";
import { refuse, type Resolution } from "./types";

/** Normalisers whose layers are the file itself, so a delimiter in them is the file's. */
export const FILE_NORMALISERS = new Set(["text-utf8@1"]);

/** One field of a delimited line, with its UTF-16 offsets into the layer. */
export interface Field {
  text: string;
  from: number;
  to: number;
}

/** The delimiter a line uses, read off the line itself. Tab beats comma, because a tab inside an
 * unquoted field does not happen and a comma does. */
export function delimiterOf(line: string): "\t" | "," | null {
  if (line.includes("\t")) return "\t";
  if (line.includes(",")) return ",";
  return null;
}

/** Split one line into fields, honouring RFC 4180 double quoting. A quoted field keeps its
 * quotes out of `text` and its offsets include them, so a span over the field covers what the
 * file prints. */
export function fieldsOf(index: LayerIndex, line: number, delimiter: string): Field[] {
  const text = index.lines[line];
  const base = index.u16[line];
  const fields: Field[] = [];
  let from = 0;
  let quoted = false;
  for (let i = 0; i <= text.length; i += 1) {
    if (i === text.length || (text[i] === delimiter && !quoted)) {
      const raw = text.slice(from, i);
      const inner = raw.startsWith('"') && raw.endsWith('"') && raw.length > 1 ? raw.slice(1, -1).replace(/""/g, '"') : raw;
      fields.push({ text: inner.trim(), from: base + from, to: base + i });
      from = i + 1;
      continue;
    }
    if (text[i] === '"') quoted = !quoted;
  }
  return fields;
}

/** A1 column letters to a zero-based index: A is 0, Z is 25, AA is 26. */
export function columnIndex(letters: string): number {
  let value = 0;
  for (const character of letters.toUpperCase()) value = value * 26 + (character.charCodeAt(0) - 64);
  return value - 1;
}

/** The first line of the layer that holds any printed text, which is where a header is. */
function headerLine(index: LayerIndex): number {
  for (let line = 0; line < index.lines.length; line += 1) if (index.lines[line].trim() !== "") return line;
  return 0;
}

interface GridRequest {
  /** One-based line number, as the locator prints it. */
  line?: number;
  /** A1 notation, as the locator prints it. */
  cell?: string;
  /** The column's printed header, where the locator names one. */
  column?: string;
}

/** A cell of a delimited file, by line and column header or by A1 notation. */
export function resolveDelimitedCell(index: LayerIndex, request: GridRequest): Resolution {
  if (!FILE_NORMALISERS.has(index.normaliser))
    return refuse("no_column_geometry", `${index.normaliser} is not the file itself, so it has no delimited columns`, index.layer_sha256);
  const header = headerLine(index);
  const delimiter = delimiterOf(index.lines[header]);
  if (delimiter === null) return refuse("no_column_geometry", "the first line of this layer holds no tab and no comma", index.layer_sha256);

  let line: number;
  let column: number | null = null;
  if (request.cell) {
    const match = /^([A-Z]{1,3})([0-9]{1,6})$/.exec(request.cell.toUpperCase());
    if (!match) return refuse("no_resolver_for_kind", `"${request.cell}" is not A1 notation`, index.layer_sha256);
    column = columnIndex(match[1]);
    line = Number(match[2]) - 1;
  } else if (request.line !== undefined) {
    line = request.line - 1;
  } else {
    return refuse("no_anchor", "the locator names neither a line nor a cell", index.layer_sha256);
  }
  if (line < 0 || line >= index.lines.length)
    return refuse("line_out_of_range", `line ${line + 1} is outside a layer of ${index.lines.length} lines`, index.layer_sha256);

  const fields = fieldsOf(index, line, delimiter);
  if (column === null) {
    if (request.column === undefined) return refuse("column_not_found", "the locator names no column", index.layer_sha256);
    const wanted = normaliseLabel(request.column);
    const headers = fieldsOf(index, header, delimiter);
    const matches = headers.map((field, at) => ({ at, field })).filter((entry) => normaliseLabel(entry.field.text) === wanted);
    if (matches.length === 0) return refuse("column_not_found", `no header field reads "${request.column}"`, index.layer_sha256);
    if (matches.length > 1) return refuse("column_ambiguous", `${matches.length} header fields read "${request.column}"`, index.layer_sha256);
    column = matches[0].at;
  }
  if (column >= fields.length) return refuse("cell_empty", `line ${line + 1} holds ${fields.length} fields and the column is number ${column + 1}`, index.layer_sha256);
  const field = fields[column];
  if (field.text === "") return refuse("cell_empty", `line ${line + 1} prints nothing in column ${column + 1}`, index.layer_sha256);
  const headers = fieldsOf(index, header, delimiter);
  const outcome: Resolution = {
    ok: true,
    kind: "delimited_cell",
    span: spanAt(index, field.from, field.to),
    layer_sha256: index.layer_sha256,
    column_header: column < headers.length ? headers[column].text : undefined,
    row_label: fields.length > 0 ? fields[0].text : undefined,
  };
  return outcome;
}

/**
 * A cell of a delimited file whose row is identified by keys rather than by a line number.
 *
 * This is the form ADR 0002 decision 2 names as the measured reason the old grammar failed: half
 * the locators it could not read select a row by a composite source-specific key, `Source
 * 'SGNex_MCF7_directRNA', Algorithm 'GFSeeker'`, because that is how a machine-readable result
 * file is keyed. The file holds the answer and the keys are its own column names.
 *
 * A constraint whose key names a header field is checked against that field. A constraint whose
 * key names nothing in the header, which is what `row 'Arriba'` gives, is satisfied by any field
 * on the line holding that value. Every constraint has to hold, and exactly one row has to
 * survive, or the resolver refuses.
 */
export function resolveKeyedRow(
  index: LayerIndex,
  request: { column: string; constraints: { key: string | null; value: string }[] },
): Resolution {
  if (!FILE_NORMALISERS.has(index.normaliser))
    return refuse("no_column_geometry", `${index.normaliser} is not the file itself, so it has no keyed rows`, index.layer_sha256);
  if (request.constraints.length === 0) return refuse("no_row_in_locator", "the locator names a column and nothing that identifies a row", index.layer_sha256);
  const header = headerLine(index);
  const delimiter = delimiterOf(index.lines[header]);
  if (delimiter === null) return refuse("no_column_geometry", "the first line of this layer holds no tab and no comma", index.layer_sha256);
  const headers = fieldsOf(index, header, delimiter).map((field) => normaliseLabel(field.text));

  const wantedColumn = normaliseLabel(request.column);
  const columns = headers.map((name, at) => ({ name, at })).filter((entry) => entry.name === wantedColumn);
  if (columns.length === 0) return refuse("column_not_found", `no header field reads "${request.column}"`, index.layer_sha256);
  if (columns.length > 1) return refuse("column_ambiguous", `${columns.length} header fields read "${request.column}"`, index.layer_sha256);

  const constraints = request.constraints.map((constraint) => ({
    at: constraint.key === null ? -1 : headers.indexOf(normaliseLabel(constraint.key)),
    value: normaliseLabel(constraint.value),
  }));
  const rows: Field[][] = [];
  for (let line = header + 1; line < index.lines.length && rows.length < 3; line += 1) {
    if (index.lines[line].trim() === "") continue;
    const fields = fieldsOf(index, line, delimiter);
    const values = fields.map((field) => normaliseLabel(field.text));
    const holds = constraints.every((constraint) =>
      constraint.at >= 0 ? values[constraint.at] === constraint.value : values.includes(constraint.value),
    );
    if (holds) rows.push(fields);
  }
  if (rows.length === 0) return refuse("row_key_unmatched", `no line satisfies all ${constraints.length} keys the locator names`, index.layer_sha256);
  if (rows.length > 1) return refuse("row_ambiguous", `more than one line satisfies the keys the locator names`, index.layer_sha256);

  const fields = rows[0];
  if (columns[0].at >= fields.length) return refuse("cell_empty", `the row holds ${fields.length} fields and the column is number ${columns[0].at + 1}`, index.layer_sha256);
  const field = fields[columns[0].at];
  if (field.text === "") return refuse("cell_empty", `the row prints nothing under "${request.column}"`, index.layer_sha256);
  return {
    ok: true,
    kind: "delimited_cell",
    span: spanAt(index, field.from, field.to),
    layer_sha256: index.layer_sha256,
    column_header: fieldsOf(index, header, delimiter)[columns[0].at].text,
    row_label: fields[0].text,
  };
}

/** A line, or a run of lines, as a span. Both ends are one based and inclusive, as printed. */
export function resolveLineRange(index: LayerIndex, from: number, to = from): Resolution {
  if (!Number.isInteger(from) || from < 1) return refuse("line_out_of_range", `"${from}" is not a line number`, index.layer_sha256);
  if (from > index.lines.length)
    return refuse("line_out_of_range", `line ${from} is outside a layer of ${index.lines.length} lines`, index.layer_sha256);
  const last = Math.min(Math.max(to, from), index.lines.length);
  return { ok: true, kind: "line_range", span: spanOfLines(index, from - 1, last - 1), layer_sha256: index.layer_sha256 };
}

/** One page of a PDF text layer, between form feeds, counted from 1. */
export function resolvePage(index: LayerIndex, page: number): Resolution {
  if (!index.text.includes("\f"))
    return refuse("page_out_of_range", `${index.normaliser} writes no page breaks, so a page cannot be addressed`, index.layer_sha256);
  if (!Number.isInteger(page) || page < 1) return refuse("page_out_of_range", `"${page}" is not a page number`, index.layer_sha256);
  let from = 0;
  for (let seen = 1; seen < page; seen += 1) {
    const next = index.text.indexOf("\f", from);
    if (next < 0) {
      const pages = index.text.split("\f").length;
      return refuse("page_out_of_range", `page ${page} is outside a layer of ${pages} pages`, index.layer_sha256);
    }
    from = next + 1;
  }
  const end = index.text.indexOf("\f", from);
  return { ok: true, kind: "page", span: spanAt(index, from, end < 0 ? index.text.length : end), layer_sha256: index.layer_sha256 };
}
