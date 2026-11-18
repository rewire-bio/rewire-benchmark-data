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
 * stored locators the grammar fully addresses, 40,464 of 52,278, 77.4% on 2026-11-18.
 * Resolution coverage is the share that reach a span in a layer the archive holds, 11,360,
 * 21.7%, and it is bounded by the archive and by what a layer can carry. The second is the
 * honest one for re-checking. A third is the one that decides whether either can gate anything:
 * 11,347 of the 11,360 spans print the value the record stores, 99.9%, and 10,943 are the stored
 * value and nothing else.
 *
 * 3,767 of those spans are cells crossed against a table grid, which is the geometry a markup
 * text layer flattens away. Resolving them read no new bytes: the grids were already built and
 * nothing had read one.
 */
import { gridNormaliserFor } from "../../archive/layers/grid/index";
import type { Grid } from "../../archive/layers/grid/types";
import { carriesNoAddress, selectorRole, type LocatorSelector, type ParsedLocator } from "../locator";
import { resolveFigureCaption } from "./figure";
import { gridRequest, resolveGridCell } from "./grid";
import { resolveJsonPointer } from "./json";
import { indexLayer, type LayerIndex } from "./offsets";
import { resolveQuote, resolveSectionParagraph } from "./prose";
import { FILE_NORMALISERS, resolveDelimitedCell, resolveKeyedRow, resolveLineRange, resolvePage } from "./regions";
import { resolveTableCell } from "./table";
import { refuse, type Resolution } from "./types";

export * from "./types";
export { CONTEXT_POINTS, countPoints, indexLayer, layerPoints, spanAt, spanOfLines, type LayerIndex } from "./offsets";
export { ALIGNED_NORMALISERS, blockAbove, cellsOf, captionLines, columnForms, normaliseLabel, resolveTableCell, tableWindow, widerWindow } from "./table";
export { cellWidth, overlap, tokensOf, type Extent, type Width } from "./width";
export { resolveFigureCaption } from "./figure";
export { gridRequest, gridRouteFor, namesTable, resolveGridCell, unitOfPoint, type GridCellRequest } from "./grid";
export { jsonOf, pointerTokens, readJson, renderPointer, resolveJsonPointer, scalarsOf, step, walk, type JsonNode, type JsonSelector } from "./json";
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
function roles(selectors: LocatorSelector[]): {
  row: string | null;
  column: string | null;
  keys: string[];
  subColumns: string[];
} {
  let row: string | null = null;
  let column: string | null = null;
  const keys: string[] = [];
  const subColumns: string[] = [];
  for (const selector of selectors) {
    if (selector.value === null) continue;
    const role = selectorRole(selector.key);
    if (role === "row" && row === null) row = selector.value;
    else if (role === "column" && column === null) column = selector.value;
    else if (role === "column") subColumns.push(selector.value);
    else if (role === "other") {
      const first = selector.key.split(/\s+/)[0];
      if (ROW_WORDS.has(first) && row === null) row = labelFromRaw(selector) ?? row;
      else if (COLUMN_WORDS.has(first) && column === null) column = labelFromRaw(selector) ?? column;
      else keys.push(selector.value);
    }
  }
  return { row, column, keys, subColumns };
}

/** Numbers in the text the grammar did not read, which still say which row was meant.
 *
 * `Table 3, row 'Medium' / 'Chroma' / length 300, column 'Ci'` leaves `length 300` as residue,
 * because `length` is not a selector keyword. The table prints one block per type and one line
 * per length, so a resolver that takes the first line labelled `Medium` returns a different
 * length's number: measured wrong on 30 locators from one source. The number is carried through
 * as a key the accepted row has to print, which resolves the right line where the layer prints
 * it on that line and refuses `row_key_unmatched` where it does not.
 *
 * Two digits at least. A one-digit residue number is a table or a panel number far more often
 * than a row key, and it is printed on nearly every line of a table that holds any count.
 *
 * One kind of word comes through with them: the name of a block. `Table 1, lower block, row
 * "random mutations", column "edits/seq"` leaves `lower block` as residue because the grammar
 * reads a block only when its name is quoted. The table prints the same row label in an upper
 * and a lower block and the resolver read the upper one, on 12 locators. Nothing else in the
 * residue is taken: it is prose as often as not, and `(printed 'SCimilarity' with superscript l,
 * trained with cell-type labels)` holds no key, which taking every word from it was measured
 * withdrawing 83 correct spans to remove those 12 wrong ones. */
function residueKeys(residue: string[]): string[] {
  const text = residue.join(" ");
  const numbers = text.match(/(?<![\p{L}\p{N}.])\d{2,}(?:\.\d+)?(?![\p{L}\p{N}.])/gu) ?? [];
  const blocks = [...text.matchAll(/([\p{L}\p{N}][\p{L}\p{N}-]*)\s+(?:block|group|panel|section|part)\b/giu)]
    .map((match) => match[1])
    // One character is not a block name worth matching a whole line against: `Gene Frequency 4
    // block` against a table of counts matches almost any line, and it committed 2 wrong cells.
    .filter((word) => word.length >= 2 && !carriesNoAddress(word));
  return [...new Set([...numbers, ...blocks])];
}

/** Which closing mark each opening mark takes. A straight quote closes on a straight quote and
 * a curly one on its partner, which is what tells an apostrophe from a delimiter: the stored
 * `'3’ UTR categories (0.50 vs. GPN-Star-M’s 0.18)'` holds two curly apostrophes inside a
 * straight-quoted run, and a scanner that closed on any mark read it as the two characters
 * `3’`. */
const CLOSERS: Record<string, string> = { "'": "'", '"': '"', "‘": "’", "“": "”" };
/** How long a quoted run has to be before it is taken as the evidence rather than a label. */
const EVIDENCE_POINTS = 8;

/** The quoted runs of a printed locator, in the order they are printed. */
function quotedRuns(printed: string): { text: string; at: number }[] {
  const runs: { text: string; at: number }[] = [];
  for (let i = 0; i < printed.length; i += 1) {
    const closer = CLOSERS[printed[i]];
    if (closer === undefined) continue;
    const end = printed.indexOf(closer, i + 1);
    if (end < 0) break;
    runs.push({ text: printed.slice(i + 1, end).trim(), at: i + 1 });
    i = end;
  }
  return runs;
}

/**
 * The text a quoting locator says to go and find, and whether it names a whole sentence.
 *
 * A locator that quotes anything usually quotes two things: the section it was read from and the
 * evidence itself, in that order. `Results, 'State-of-the-art interpretable genome-wide variant
 * prioritization with AVI' paragraph 1 (page 5), citing Fig. 2A: 'synonymous (0.57 vs. CADD
 * v1.7's 0.35)'` is the common shape. Taking the first quote resolves the heading, which is a
 * span in the right paper at the wrong place, and 60 of the 93 wrong quote spans of 2026-11-18
 * were exactly that. The last quoted run is the evidence, and because the evidence is often
 * under the grammar's 40-point threshold it is read off the printed string rather than off the
 * addresses. The span is still only ever returned when that text occurs in the layer once.
 */
function evidenceQuote(parsed: ParsedLocator): { text: string; whole: boolean } | null {
  const quoted = parsed.addresses.filter((address) => address.kind === "quote" || address.kind === "sentence");
  if (quoted.length === 0) return null;
  const address = quoted[quoted.length - 1];
  const chosen = { text: address.value, whole: address.kind === "sentence" };
  const runs = quotedRuns(parsed.printed).filter((run) => [...run.text].length >= EVIDENCE_POINTS);
  // Of the quoted runs, the evidence is the last one that prints a number. A locator quotes a
  // section, then the sentence the value is in, and sometimes a panel or a label after it:
  // `Main 'Modeling tissue-specific splicing' paragraph 2 '(13,770 splice junctions, Pearson
  // r = 0.58)'; Fig. 2b panel 'Cerebellum vs blood'` ends on the panel. This asks nothing about
  // the value the record stores, only whether the quoted text prints any number at all, and the
  // span is still returned only where that text occurs in the layer exactly once.
  const numbered = runs.filter((run) => /\d/.test(run.text));
  const last = (numbered.length > 0 ? numbered : runs)[(numbered.length > 0 ? numbered : runs).length - 1];
  if (!last || last.text === chosen.text) return chosen;
  // The later run wins only where it is printed after the address it displaces. A quote address
  // that already stands last in the string is the evidence.
  return last.at > parsed.printed.lastIndexOf(address.value) ? { text: last.text, whole: false } : chosen;
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
export function resolveLocator(parsed: ParsedLocator, index: LayerIndex, grid?: Grid | null): Resolution {
  const outcome = resolveParsed(parsed, index, usableGrid(index, grid));
  // A span has to cover characters. `spanSchema` requires `exact` to hold at least one, so a
  // span over a blank line is not a span a record could carry, and one states a place where
  // nothing is printed. Measured once, on a locator addressing a blank line of a PDF layer.
  if (outcome.ok && outcome.span.exact.length === 0)
    return refuse("empty_span", "the address names a place in the layer that prints nothing", index.layer_sha256);
  return outcome;
}

/**
 * The grid to cross a row and a column against, or null.
 *
 * Three things have to hold before a grid is read. It has to be the grid normaliser that shadows
 * this text normaliser, because a grid is built beside one text layer and not beside any other.
 * It has to name this layer as the one its offsets are into. And it has to hold a table. Any of
 * them failing leaves the locator on the aligned resolver, which refuses it, which is where it
 * already was.
 */
function usableGrid(index: LayerIndex, grid?: Grid | null): Grid | null {
  if (!grid) return null;
  if (gridNormaliserFor(index.normaliser) !== grid.normaliser) return null;
  if (grid.text_layer_sha256 !== index.layer_sha256) return null;
  return grid.tables.length > 0 ? grid : null;
}

function resolveParsed(parsed: ParsedLocator, index: LayerIndex, grid: Grid | null): Resolution {
  const { row, column, keys, subColumns } = roles(parsed.selectors);
  const addresses = parsed.addresses;
  const anchors = parsed.anchors;

  const table = anchors.find((anchor) => anchor.kind === "table" || anchor.kind === "figure" || anchor.kind === "sheet");

  // A quote is the strongest evidence a locator carries and is resolved first, with one
  // exception: a locator that names a table, a row and a column is addressing a cell, and the
  // long quoted run in it is a row or column label rather than a sentence to go and find.
  const quoted = table && row && column ? null : evidenceQuote(parsed);
  if (quoted) return resolveQuote(index, quoted.text, quoted.whole);

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
    return resolveJsonPointer(index, {
      path: jsonPath.value,
      selectors: parsed.selectors
        .filter((selector) => selector.value !== null)
        .map((selector) => ({ key: selector.key, value: selector.value as string, role: selectorRole(selector.key) })),
    });
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

  if (table && row && column) {
    const request = { anchor: table, row, column, keys: [...keys, ...residueKeys(parsed.residue)], subColumns };
    // A grid in hand is the geometry the text layer lost, so it is read instead of the aligned
    // resolver and not after it. There is no fall through: the aligned resolver on a markup layer
    // can only answer `no_column_geometry`, and the grid's own refusal says more than that. The
    // request the grid gets carries two things more, which only a grid can read: see
    // `gridRequest`.
    return grid ? resolveGridCell(index, grid, gridRequest(parsed, request, selectorRole)) : resolveTableCell(index, request);
  }
  if (table && row) return refuse("no_column_in_locator", `the locator names a row and no column`, index.layer_sha256);
  if (table && column && table.kind !== "figure")
    return refuse("no_row_in_locator", `the locator names a column and no row`, index.layer_sha256);

  const figure = anchors.find((anchor) => anchor.kind === "figure");
  if (figure && !row && !column) return resolveFigureCaption(index, figure.value);

  const paragraph = addresses.find((address) => address.kind === "paragraph");
  const section = anchors.find((anchor) => anchor.kind === "container");
  // "Results P13, sentence 1" names the publisher's paragraph 13 of the Results and the first
  // sentence of it. Two things go wrong with it. The grammar reads P13 as the container's object
  // number and "sentence 1" as a paragraph, because the two are written the same way, so the
  // resolver counted to 1 and returned the opening paragraph: that was 23 of the 24 section
  // paragraph spans of 2026-11-18. Reading P13 as the paragraph instead does not rescue them,
  // because the publisher's numbering is not the count of blank-line-separated blocks in the
  // layer: measured on the one source that uses this form, P13 is the 11th block of the Results
  // and P14 the 12th, and the offset is the figure blocks the layer prints and the publisher
  // does not number. A count that cannot be reproduced is refused.
  if (section && section.container && /^P\.?\s*\d{1,3}$/i.test(section.value))
    return refuse(
      "no_resolver_for_kind",
      `"${section.container} ${section.value}" is the publisher's paragraph number, which this layer does not carry`,
      index.layer_sha256,
    );
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

