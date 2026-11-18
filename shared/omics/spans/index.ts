/** From a locator to a span: what this lane adds to the grammar.
 *
 * `shared/omics/locator.ts` reads a stored locator string into anchors, addresses, selectors and
 * qualifiers. It says what the locator means. It does not say where in a layer the value is, and
 * a reader with the parse in hand still has to open the paper.
 *
 * This module closes that gap. Given a parse and one indexed layer, it picks the resolver the
 * locator's shape calls for and either returns a span or refuses with one stated reason. Nothing
 * here reads a stored value, and nothing here calls a model. A span it returns can be re-checked
 * on a fresh clone with the layer bytes and nothing else.
 *
 *   const [layer] = layersForSource(sourceId);
 *   const index = indexLayer(layerText(layer), layer.layer_sha256, layer.normaliser);
 *   const outcome = resolveLocator(parseLocator(record.attributes.source_locator), index);
 *
 * Two numbers are measured separately and must not be confused. Parse coverage is the share of
 * stored locators the grammar fully addresses, 75.4% on 2026-11-17. Resolution coverage is the
 * share that reach a span in a layer the archive holds, which is bounded by the archive and by
 * what a text layer can carry. The second is the honest one for re-checking.
 */
import { selectorRole, type LocatorSelector, type ParsedLocator } from "../locator";
import { resolveFigureCaption } from "./figure";
import { indexLayer, type LayerIndex } from "./offsets";
import { resolveQuote, resolveSectionParagraph } from "./prose";
import { FILE_NORMALISERS, resolveDelimitedCell, resolveKeyedRow, resolveLineRange, resolvePage } from "./regions";
import { resolveTableCell } from "./table";
import { refuse, type Resolution } from "./types";

export * from "./types";
export { CONTEXT_POINTS, countPoints, indexLayer, layerPoints, spanAt, spanOfLines, type LayerIndex } from "./offsets";
export { ALIGNED_NORMALISERS, cellsOf, captionLines, normaliseLabel, resolveTableCell, tableWindow } from "./table";
export { resolveFigureCaption } from "./figure";
export { resolveQuote, resolveSectionParagraph } from "./prose";
export { FILE_NORMALISERS, columnIndex, delimiterOf, fieldsOf, resolveDelimitedCell, resolveKeyedRow, resolveLineRange, resolvePage } from "./regions";
export { reanchor, type Anchoring, type AnchorEvidence } from "./reanchor";

/** Keys whose first word names the row or the column, where the rest of the key is the label.
 *
 * The grammar reads `row Ridge (one-hot)` as the key `row ridge` with the bracketed value
 * `one-hot`, because a bracket is a selector form and the row keyword is not reserved. The parse
 * is right about the text and the resolver needs the label, which is the whole printed phrase
 * after the keyword. Reading it off `raw` changes no grammar and loses nothing: `raw` is the
 * text the selector was read from. */
const ROW_WORDS = new Set(["row", "rows"]);
const COLUMN_WORDS = new Set(["column", "col", "columns", "sub-column", "sub-col"]);

function labelFromRaw(selector: LocatorSelector): string | null {
  const match = /^\s*\S+\s+(.+)$/.exec(selector.raw);
  return match ? match[1].trim() : null;
}

/** The first selector whose key names the row, the first that names the column, and the rest.
 *
 * The rest are not decoration. A locator that says `row 'Medium' / 'FrameDiff' / length 400`
 * identifies one row by three facts, and a resolver that reads the first and drops the other two
 * will find a row and find the wrong one. They are carried through as keys the accepted row has
 * to print. */
function roles(selectors: LocatorSelector[]): { row: string | null; column: string | null; keys: string[] } {
  let row: string | null = null;
  let column: string | null = null;
  const keys: string[] = [];
  for (const selector of selectors) {
    if (selector.value === null) continue;
    const role = selectorRole(selector.key);
    if (role === "row" && row === null) row = selector.value;
    else if (role === "column" && column === null) column = selector.value;
    else if (role === "other") {
      const first = selector.key.split(/\s+/)[0];
      if (ROW_WORDS.has(first) && row === null) row = labelFromRaw(selector) ?? row;
      else if (COLUMN_WORDS.has(first) && column === null) column = labelFromRaw(selector) ?? column;
      else keys.push(selector.value);
    }
  }
  return { row, column, keys };
}

/** A page number from a page qualifier, where the qualifier carries one. */
function pageOf(parsed: ParsedLocator): number | null {
  for (const qualifier of parsed.qualifiers) {
    if (qualifier.kind !== "page") continue;
    const match = /(\d+)/.exec(qualifier.text);
    if (match) return Number(match[1]);
  }
  return null;
}

/**
 * The span a parsed locator names in this layer, or the one reason it does not.
 *
 * The order of the tests is the order of specificity: a locator that quotes its own text is
 * resolved by the quote whatever else it carries, because the quote is the strongest evidence in
 * the string. A cell comes next, then a region. Nothing falls through to a looser resolver: a
 * locator that names a row and no column is refused, not resolved to the whole row, because a
 * span over a row does not check the value that was read out of it.
 */
export function resolveLocator(parsed: ParsedLocator, index: LayerIndex): Resolution {
  const { row, column, keys } = roles(parsed.selectors);
  const addresses = parsed.addresses;
  const anchors = parsed.anchors;

  const quoted = addresses.find((address) => address.kind === "quote" || address.kind === "sentence");
  if (quoted) return resolveQuote(index, quoted.value);

  const table = anchors.find((anchor) => anchor.kind === "table" || anchor.kind === "figure" || anchor.kind === "sheet");
  const sheetCell = addresses.find((address) => address.kind === "sheet_cell");
  const lineLike = addresses.find((address) => address.kind === "line" || address.kind === "row_number");

  // An address into a file reads only against a layer that is the file. On a rendering, the same
  // locator's table anchor and labels are what can be followed, so the dispatch falls through to
  // the table resolver rather than refusing on a file address the layer cannot carry.
  const isFile = FILE_NORMALISERS.has(index.normaliser);
  if (sheetCell && isFile) return resolveDelimitedCell(index, { cell: sheetCell.value, column: column ?? undefined });
  if (lineLike && column && isFile) return resolveDelimitedCell(index, { line: Number(lineLike.value), column });
  const jsonPath = addresses.find((address) => address.kind === "json_path");
  if (jsonPath)
    return refuse("no_resolver_for_kind", "a JSON Pointer resolver over the file layer is not built", index.layer_sha256);
  if (isFile && column && (row !== null || keys.length > 0)) {
    const constraints = [
      ...(row === null ? [] : [{ key: null, value: row }]),
      ...parsed.selectors
        .filter((selector) => selector.value !== null && selectorRole(selector.key) === "other")
        .map((selector) => ({ key: selector.key, value: selector.value as string })),
    ];
    const keyed = resolveKeyedRow(index, { column, constraints });
    if (keyed.ok) return keyed;
    if (!sheetCell && !lineLike) return keyed;
  }
  if (sheetCell && !isFile && !(table && row && column))
    return refuse("no_column_geometry", `${index.normaliser} is not the file the cell address names`, index.layer_sha256);
  if (lineLike && column && !isFile && !(table && row && column))
    return refuse("no_column_geometry", `${index.normaliser} is not the file the line address names`, index.layer_sha256);

  if (table && row && column) return resolveTableCell(index, { anchor: table, row, column, keys });
  if (table && row) return refuse("no_column_in_locator", `the locator names a row and no column`, index.layer_sha256);
  if (table && column && table.kind !== "figure")
    return refuse("no_row_in_locator", `the locator names a column and no row`, index.layer_sha256);

  const figure = anchors.find((anchor) => anchor.kind === "figure");
  if (figure && !row && !column) return resolveFigureCaption(index, figure.value);

  const paragraph = addresses.find((address) => address.kind === "paragraph");
  const section = anchors.find((anchor) => anchor.kind === "container");
  if (paragraph && section) return resolveSectionParagraph(index, section.container ?? section.value, Number(paragraph.value));
  if (paragraph) return refuse("no_anchor", "a paragraph number with no section names no place", index.layer_sha256);

  if (lineLike) {
    // "line 446" counts lines of the text layer, so it reads against any layer. "row 7" counts
    // rows of a table, and a table row is a line only where the layer is the file itself. On a
    // PDF or an HTML rendering the two differ by the whole of the front matter, and resolving one
    // as the other puts a span on an unrelated line.
    if (lineLike.kind === "row_number" && !FILE_NORMALISERS.has(index.normaliser))
      return refuse("no_resolver_for_kind", "a table row number needs a layer that is the file, not a rendering of it", index.layer_sha256);
    const from = Number(lineLike.value);
    const second = addresses.filter((address) => address.kind === lineLike.kind)[1];
    return resolveLineRange(index, from, second ? Number(second.value) : from);
  }

  const page = pageOf(parsed);
  if (page !== null) return resolvePage(index, page);

  if (anchors.length === 0 && addresses.length === 0) return refuse("no_anchor", "the locator addresses nothing the grammar reads", index.layer_sha256);
  const kinds = [...addresses.map((address) => address.kind), ...anchors.map((anchor) => anchor.kind)];
  return refuse("no_resolver_for_kind", `no resolver reads ${[...new Set(kinds)].sort().join(" plus ") || "this locator"}`, index.layer_sha256);
}

