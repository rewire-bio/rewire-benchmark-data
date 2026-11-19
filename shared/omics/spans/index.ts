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
import { carriesNoAddress, selectorRole, type LocatorAddress, type LocatorSelector, type ParsedLocator } from "../locator";
import { resolveFigureCaption } from "./figure";
import { gridRequest, resolveGridCell } from "./grid";
import { resolveJsonPointer } from "./json";
import { indexLayer, type LayerIndex } from "./offsets";
import { resolveQuote, resolveSectionParagraph } from "./prose";
import { FILE_NORMALISERS, resolveDelimitedCell, resolveKeyedRow, resolveLineRange, resolvePage } from "./regions";
import { isSheetLayer, resolveSheetCell, sheetRequest } from "./sheet";
import { normaliseLabel, resolveTableCell } from "./table";
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
export {
  SHEET_NORMALISERS,
  blocksOf,
  fieldsOfLine,
  isSheetLayer,
  resolveSheetCell,
  sheetRequest,
  type SheetCellRequest,
  type SheetField,
} from "./sheet";
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

/** Addresses that say where to look rather than what to find.
 *
 * A quoted run printed before the last of these is a label for one of them and not the evidence.
 * `Table 2 (Tab2), row 3 ('Qwen2.5', 'Binary class prompt + Default temperature (0.8)',
 * 'FoundationOne'), column 'Accuracy'` prints a composite row key that holds a number, and the
 * rule below reads the last quoted run that prints a number: on that locator it read the key and
 * put the span on a row label. The same cut takes the section heading out of
 * `Results 'MetageNN is faster ...' paragraph 3, sentence 5`, where the place the locator names
 * is the paragraph and the quoted run is the name of the section it sits in. */
const PLACE_KINDS = new Set<ParsedLocator["addresses"][number]["kind"]>([
  "row_number",
  "line",
  "paragraph",
  "sheet_cell",
  "cell_range",
  "xml_cell",
  "json_path",
]);

/** Which closing mark each opening mark takes. A straight quote closes on a straight quote and
 * a curly one on its partner, which is what tells an apostrophe from a delimiter: the stored
 * `'3’ UTR categories (0.50 vs. GPN-Star-M’s 0.18)'` holds two curly apostrophes inside a
 * straight-quoted run, and a scanner that closed on any mark read it as the two characters
 * `3’`. */
const CLOSERS: Record<string, string> = { "'": "'", '"': '"', "‘": "’", "“": "”" };
/** How long a quoted run has to be before it is taken as the evidence rather than a label. */
const EVIDENCE_POINTS = 8;
/** How long it has to be where the grammar read no quote at all, which is the grammar's own
 * threshold for reading a quoted run as a quote.
 *
 * A run the grammar did not read as a quote is the only record of a text to go and find, and
 * `the sentence beginning 'Scoring real homologs against real homologs'` is the shape worth
 * resolving. Short runs in that position are labels and were measured as such: `columns 'AP' and
 * 'AP 95% CI'`, `run 'rrf prf rprec'`, `sentence 'Within single donors', value for Tahoe-x1
 * (70M)`. Taking every run of eight points or more committed 14 spans to a label that prints no
 * part of the stored value, against 108 spans that print it. At 40 points the labels go and the
 * sentences stay, and a run the locator itself calls a sentence is taken whatever its length. */
const LONG_RUN_POINTS = 40;

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
function evidenceQuote(parsed: ParsedLocator, legacy = false): { text: string; whole: boolean } | null {
  if (legacy) return legacyEvidenceQuote(parsed);
  const quoted = parsed.addresses.filter((address) => address.kind === "quote" || address.kind === "sentence");
  const cut = placeCut(parsed);
  const labels = labelValues(parsed);
  const floor = quoted.length > 0 ? EVIDENCE_POINTS : LONG_RUN_POINTS;
  const runs = quotedRuns(parsed.printed).filter(
    (run) =>
      ([...run.text].length >= floor || namesSentence(parsed.printed, run.at)) &&
      run.at > cut &&
      !labels.has(normaliseLabel(run.text)),
  );
  // Of the candidate runs, the evidence is the last one that prints a number. A locator quotes a
  // section, then the sentence the value is in, and sometimes a panel or a label after it:
  // `Main 'Modeling tissue-specific splicing' paragraph 2 '(13,770 splice junctions, Pearson
  // r = 0.58)'; Fig. 2b panel 'Cerebellum vs blood'` ends on the panel. This asks nothing about
  // the value the record stores, only whether the quoted text prints any number at all, and the
  // span is still returned only where that text occurs in the layer exactly once.
  const numbered = runs.filter((run) => /\d/.test(run.text));
  const pool = numbered.length > 0 ? numbered : runs;
  const last = pool[pool.length - 1];
  const address = quoted.length > 0 ? quoted[quoted.length - 1] : null;
  const addressAt = address === null ? -1 : parsed.printed.lastIndexOf(address.value);
  // A run wins over the quote address only where it is printed after it. It can win where the
  // grammar read no quote at all: `the sentence beginning 'Scoring real homologs against real
  // homologs'` arrives as a selector, so the run is the only record of the text to find.
  if (last && last.at > addressAt) return { text: last.text, whole: namesSentence(parsed.printed, last.at) };
  // An address printed before the place the locator names is a label for that place, which is
  // the section heading case. There is no evidence quote in the string.
  if (address && addressAt > cut)
    return { text: address.value, whole: address.kind === "sentence" || namesSentence(parsed.printed, addressAt) };
  return null;
}

/** The quote selection as it stood before the label rule, kept so the rule's effect can be
 * measured as a paired run in one process. `measure --legacy-quote` is the only caller. */
function legacyEvidenceQuote(parsed: ParsedLocator): { text: string; whole: boolean } | null {
  const quoted = parsed.addresses.filter((address) => address.kind === "quote" || address.kind === "sentence");
  if (quoted.length === 0) return null;
  const address = quoted[quoted.length - 1];
  const chosen = { text: address.value, whole: address.kind === "sentence" };
  const runs = quotedRuns(parsed.printed).filter((run) => [...run.text].length >= EVIDENCE_POINTS);
  const numbered = runs.filter((run) => /\d/.test(run.text));
  const last = (numbered.length > 0 ? numbered : runs)[(numbered.length > 0 ? numbered : runs).length - 1];
  if (!last || last.text === chosen.text) return chosen;
  return last.at > parsed.printed.lastIndexOf(address.value) ? { text: last.text, whole: false } : chosen;
}

/** Where the last place-naming part of the locator ends, as an index into the printed string, or
 * -1 where the locator names no place. */
function placeCut(parsed: ParsedLocator): number {
  let cut = -1;
  const mark = (raw: string): void => {
    const at = parsed.printed.lastIndexOf(raw);
    if (at >= 0) cut = Math.max(cut, at + raw.length);
  };
  for (const address of parsed.addresses) if (PLACE_KINDS.has(address.kind)) mark(address.raw);
  for (const selector of parsed.selectors) if (selectorRole(selector.key) !== "other") mark(selector.raw);
  return cut;
}

/** The text of every part the grammar read as a label: an anchor's identifier and the value of
 * any selector naming a row or a column. A quoted run printing one of them is that label and not
 * a sentence to go and find. */
function labelValues(parsed: ParsedLocator): Set<string> {
  const labels = new Set<string>();
  for (const anchor of parsed.anchors) labels.add(normaliseLabel(anchor.value));
  for (const selector of parsed.selectors)
    if (selector.value !== null && selectorRole(selector.key) !== "other") labels.add(normaliseLabel(selector.value));
  return labels;
}

/** Does the locator say this run opens a sentence rather than standing for one?
 *
 * `the sentence beginning 'Scoring real homologs against real homologs'` is read by the grammar
 * as a selector, so the span ran to the end of the quoted opening and the value the record keeps
 * is further along the sentence: three stored locators were that. The phrase printed in front of
 * the run is what says so, and it is read off the printed string because the selector key is not
 * reserved. "beginning" is optional because `sentence 'Within single donors', value for
 * Tahoe-x1 (70M)` names a sentence by its opening in the same way and prints the value further
 * along it. */
const SENTENCE_PHRASE = /\b(?:sentence|sentences)(?:\s+(?:beginning|starting|begins|opening|that begins|which begins))?$/i;

function namesSentence(printed: string, at: number): boolean {
  return SENTENCE_PHRASE.test(printed.slice(0, Math.max(0, at - 1)).replace(/[\s:,'"‘“]+$/, ""));
}

/**
 * The section name a locator quotes, where it quotes one before the paragraph it names.
 *
 * `Results 'MetageNN is faster and requires less storage than alignment and k-mer-based tools,
 * respectively' paragraph 3` names a subsection by printing its heading, and the container
 * anchor is the parent section. Counting paragraphs from the parent counts the wrong paragraphs:
 * on the layer these three locators address, paragraph 3 of the quoted subsection prints the
 * value and paragraph 3 of "Results" is in another subsection entirely. So the quoted heading is
 * the name used, and where the layer prints no heading line reading it the resolver refuses
 * `section_not_found` rather than counting from the parent, because that count states a place
 * the locator did not name.
 */
function quotedSection(parsed: ParsedLocator, paragraph: LocatorAddress): string | null {
  const at = parsed.printed.lastIndexOf(paragraph.raw);
  let name: string | null = null;
  for (const address of parsed.addresses) {
    if (address.kind !== "quote" && address.kind !== "sentence") continue;
    const position = parsed.printed.lastIndexOf(address.raw);
    if (position >= 0 && (at < 0 || position < at)) name = address.value;
  }
  return name;
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
export function resolveLocator(parsed: ParsedLocator, index: LayerIndex, grid?: Grid | null, options?: ResolveOptions): Resolution {
  const outcome = resolveParsed(parsed, index, usableGrid(index, grid), options ?? {});
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

/** What a caller may vary, so a rule's effect can be measured against the same store in one
 * process rather than reported as an anecdote: the quote selection, and whether a sheet layer's
 * blocks are read at all. */
export interface ResolveOptions {
  legacyQuote?: boolean;
  /** True or absent reads the blocks of a sheet layer, which is the shipped path. False leaves a
   * sheet layer where it was, refusing every cell address on it, and is the other arm of the
   * paired run that measures what the sheet blocks are worth. */
  sheet?: boolean;
}

function resolveParsed(parsed: ParsedLocator, index: LayerIndex, grid: Grid | null, options: ResolveOptions): Resolution {
  const { row, column, keys, subColumns } = roles(parsed.selectors);
  const addresses = parsed.addresses;
  const anchors = parsed.anchors;

  const table = anchors.find((anchor) => anchor.kind === "table" || anchor.kind === "figure" || anchor.kind === "sheet");

  const sheetCell = addresses.find((address) => address.kind === "sheet_cell");
  const lineLike = addresses.find((address) => address.kind === "line" || address.kind === "row_number");

  // A sheet layer keeps the geometry of the workbook, one block per sheet, so a cell reference on
  // it is an address and not a wish. It is read before everything else on this layer for two
  // reasons. A quoted run in such a locator is a sheet name, a row label or a column heading, and
  // the layer holds no prose for a sentence to be found in, so a quote resolved against a sheet
  // layer can only land on a label, which is a span in the right workbook at a place that prints
  // no value. And `table` includes a sheet anchor, so a locator
  // naming a sheet, a row and a column would otherwise reach the aligned resolver, which can
  // only answer `no_column_geometry` on a layer of tab separated blocks. A locator whose shape
  // this layer cannot carry gets null back and stays on the dispatch it had.
  // On by default. Checking these spans against the record takes a value check that can compare
  // numbers: `ooxml-sheet-tsv@1` prints the characters the workbook stores, which for a computed
  // cell is the full double, 0.81699999999999995, while the record keeps what the spreadsheet
  // displays, 0.82. The two share no substring and are the same number, so a check comparing
  // characters alone reads the right cell as a wrong answer, and once did, on 1,706 of these
  // spans. The resolver was not the defect and the comparison is numeric: see `valuePresence` in
  // `scripts/omics/spans/cli.ts`.
  if (isSheetLayer(index.normaliser) && options.sheet !== false) {
    const request = sheetRequest(parsed);
    if (request) return resolveSheetCell(index, request);
  }

  // A quote is the strongest evidence a locator carries and is resolved first, with one
  // exception: a locator that names a table, a row and a column is addressing a cell, and the
  // long quoted run in it is a row or column label rather than a sentence to go and find. The
  // row may arrive as an address rather than as a selector, which is `Table 2, row 3 (...),
  // column 'Accuracy'`, and that locator addresses a cell just as plainly.
  const addressesACell = options.legacyQuote ? Boolean(table && row && column) : Boolean(table && column && (row || lineLike));
  const quoted = addressesACell ? null : evidenceQuote(parsed, options.legacyQuote);
  if (quoted) return resolveQuote(index, quoted.text, quoted.whole);

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
  if (paragraph && section) {
    const named = options.legacyQuote ? null : quotedSection(parsed, paragraph);
    return resolveSectionParagraph(index, named ?? section.container ?? section.value, Number(paragraph.value));
  }
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

