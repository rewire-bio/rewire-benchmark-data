/** Resolvers for prose: a quoted phrase, and a paragraph of a named section.
 *
 * A quote is the strongest locator in the store, because it carries its own answer. The only work
 * is finding it, and the only question is whether it is there once or more than once.
 *
 * Line wrapping is the complication. A sentence printed across two lines of a PDF has a newline
 * and some indentation inside it that nobody typed, so a locator quoting that sentence will not
 * match the layer character for character. The rule is a whitespace-flexible match: every run of
 * whitespace in the quote matches any run of whitespace in the layer, and nothing else is
 * relaxed. A hyphen that the renderer inserted at a line break is not relaxed, because relaxing
 * it would let two different words match the same quote.
 */
import { escape, normaliseLabel } from "./table";
import { spanAt, type LayerIndex } from "./offsets";
import { refuse, type Resolution } from "./types";

/** A quote with its internal whitespace left free, which is the only difference a line break in
 * a text layer makes to a sentence. */
function flexible(quote: string): RegExp {
  const parts = quote.trim().split(/\s+/).map(escape);
  return new RegExp(parts.join("\\s+"), "g");
}

/** Every place a quote occurs, as UTF-16 ranges. */
function occurrences(index: LayerIndex, quote: string, limit = 8): { from: number; to: number }[] {
  const found: { from: number; to: number }[] = [];
  const pattern = flexible(quote);
  let match: RegExpExecArray | null;
  while ((match = pattern.exec(index.text)) !== null && found.length < limit) {
    found.push({ from: match.index, to: match.index + match[0].length });
    pattern.lastIndex = match.index + Math.max(1, match[0].length);
  }
  return found;
}

/** How far past the quote a sentence may run before the resolver gives up looking for its end. */
const SENTENCE_UNITS = 900;

/** Words that take a full stop and do not end a sentence.
 *
 * "(Fig. 6C)" ends a sentence under the test below, because a space and a digit follow the stop.
 * One quote span of 2026-11-18 was cut there: the locator named the sentence that prints a
 * 10.3-fold odds ratio, the sentence cites the figure before it prints the number, and the span
 * stopped at "(Fig." with the value outside it. Reading past a known abbreviation lengthens the
 * span and never shortens it, so where one of these really does end a sentence the span covers
 * one sentence more than it needs and still holds what the locator named. */
const ABBREVIATIONS = new Set([
  "al", "approx", "ca", "cf", "chr", "dr", "e.g", "eq", "eqs", "est", "etc", "ext", "fig", "figs",
  "i.e", "no", "nos", "pp", "prof", "ref", "refs", "resp", "sec", "secs", "suppl", "supp", "tab",
  "tabs", "vs", "viz",
]);

/** The word a full stop follows, lower cased, with its own inner stops kept so "e.g." arrives as
 * "e.g" and "et al." as "al". */
function wordBefore(text: string, at: number): string {
  let from = at;
  while (from > 0 && /[\p{L}\p{N}.]/u.test(text[from - 1])) from -= 1;
  return text.slice(from, at).toLowerCase();
}

/** The end of the sentence the quote starts, as a UTF-16 offset, or null where none is found
 * within `SENTENCE_UNITS`.
 *
 * A full stop ends a sentence when a space and a capital letter follow it, or when the text
 * does. A full stop between two digits is a decimal point, and the values this lane exists to
 * find are mostly decimals, so that case is excluded explicitly. A full stop after a known
 * abbreviation does not end a sentence, which over-reads by one sentence where the abbreviation
 * stands at a real end and never under-reads: the span stays a superset of the quote. */
function sentenceEnd(text: string, from: number): number | null {
  const limit = Math.min(text.length, from + SENTENCE_UNITS);
  for (let at = from; at < limit; at += 1) {
    const here = text[at];
    if (here !== "." && here !== "!" && here !== "?") continue;
    if (here === "." && /[0-9]/.test(text[at - 1] ?? "") && /[0-9]/.test(text[at + 1] ?? "")) continue;
    if (here === "." && ABBREVIATIONS.has(wordBefore(text, at))) continue;
    const after = text.slice(at + 1, at + 4);
    if (after === "" || /^\s*$/.test(after) || /^\s+["'(‘“]?[A-Z0-9]/.test(after)) return at + 1;
  }
  return null;
}

/**
 * The span of a quoted sentence or phrase.
 *
 * `whole` is for `sentence beginning "X"`, where the locator names the sentence and prints only
 * its opening. The value the record stores is further along it, so a span over the opening alone
 * states a place the value is not: 9 of the 2026-11-18 quote spans were that. With `whole` the
 * span runs from the quote to the end of its sentence, and where no end is found within
 * `SENTENCE_UNITS` the span stays the quote rather than guessing one.
 */
export function resolveQuote(index: LayerIndex, quote: string, whole = false): Resolution {
  if (quote.trim().length < 4) return refuse("no_anchor", "a quote under four characters addresses nothing", index.layer_sha256);
  const hits = occurrences(index, quote);
  if (hits.length === 0) return refuse("quote_not_found", `the quoted text is not in this layer`, index.layer_sha256);
  if (hits.length > 1) return refuse("quote_ambiguous", `the quoted text occurs ${hits.length} times or more in this layer`, index.layer_sha256);
  const to = whole ? (sentenceEnd(index.text, hits[0].to) ?? hits[0].to) : hits[0].to;
  return { ok: true, kind: "quote", span: spanAt(index, hits[0].from, to), layer_sha256: index.layer_sha256 };
}

/** Lines that are a heading for this section name: the line's whole printed text is the name,
 * optionally numbered. A sentence mentioning "Methods" is not a heading.
 *
 * The length bound is on the line against the name it has to equal, not a fixed 80 characters.
 * The test is equality after normalisation, so no line much longer than the name can pass it and
 * the bound only keeps the scan off whole paragraphs. A fixed 80 dropped the heading "MetageNN
 * is faster and requires less storage than alignment and k-mer-based tools, respectively", which
 * is 95 characters and is the heading three stored locators name. */
function headingLines(index: LayerIndex, name: string): number[] {
  const wanted = normaliseLabel(name);
  const numbered = /^\s*(?:[0-9]+(?:\.[0-9]+)*\.?|[IVXL]+\.)\s+/i;
  const bound = Math.max(80, wanted.length + 16);
  const found: number[] = [];
  for (let line = 0; line < index.lines.length; line += 1) {
    const text = index.lines[line].trim();
    if (text.length === 0 || text.length > bound) continue;
    if (normaliseLabel(text.replace(numbered, "")) === wanted) found.push(line);
  }
  return found;
}

/** A line shaped like a heading: short, standing alone between blank lines, and not ending in
 * the punctuation a sentence ends with. The section being read ends at the first of these, so a
 * paragraph count never runs on into the next section. Where the shape is missed the resolver
 * refuses with `paragraph_out_of_range`, which is the safe direction. */
function headingShaped(lines: string[], line: number): boolean {
  const text = lines[line].trim();
  if (text === "" || text.length > 80) return false;
  if (/[.;:,]$/.test(text)) return false;
  const before = line === 0 || lines[line - 1].trim() === "";
  const after = line + 1 >= lines.length || lines[line + 1].trim() === "";
  return before && after;
}

/** Normalisers that print one block element per line.
 *
 * A JATS or an HTML normaliser writes one line per paragraph, heading, table label, caption and
 * table row, so a paragraph here is a line and not a run of lines. Two locators on one Europe
 * PMC layer show why that matters and where it stops. In one subsection the author's paragraph 3
 * is the third line under the heading, which the run-of-lines rule merged into a single
 * paragraph and read as paragraph 1. In another the third line under the heading is a table's
 * label, because the layer prints a blank line and then the float.
 *
 * Nothing past the first blank line after a heading is numbered on these layers. The blank line
 * before a float's label and the blank line before the next section's heading are the same blank
 * line, and the flattened text cannot tell one from the other, so a count that runs past it can
 * land in another section. That is a refusal here and was a wrong span before.
 */
const BLOCK_PER_LINE = new Set(["europepmc-fulltext-xml@1", "html-text@1"]);

/** Paragraphs as runs of non-blank lines, which is what a layout renderer leaves: a paragraph
 * wraps over several lines and a blank line separates two of them. */
function wrappedParagraphs(index: LayerIndex, heading: number, wanted: number): { from: number; to: number }[] {
  const blocks: { from: number; to: number }[] = [];
  let open: number | null = null;
  for (let line = heading + 1; line < index.lines.length; line += 1) {
    const text = index.lines[line].trim();
    if (text !== "" && headingShaped(index.lines, line)) {
      if (open !== null) blocks.push({ from: open, to: line - 1 });
      open = null;
      break;
    }
    if (text === "") {
      if (open !== null) blocks.push({ from: open, to: line - 1 });
      open = null;
      if (blocks.length >= wanted) break;
      continue;
    }
    if (open === null) open = line;
  }
  if (open !== null && blocks.length < wanted) blocks.push({ from: open, to: index.lines.length - 1 });
  return blocks;
}

/** Paragraphs as lines, which is what a markup normaliser leaves, stopping at the first blank
 * line because what follows one cannot be placed in this section. */
function lineParagraphs(index: LayerIndex, heading: number): { from: number; to: number }[] {
  const blocks: { from: number; to: number }[] = [];
  for (let line = heading + 1; line < index.lines.length; line += 1) {
    if (index.lines[line].trim() === "") break;
    blocks.push({ from: line, to: line });
  }
  return blocks;
}

/**
 * The nth paragraph of a named section, counted from 1.
 *
 * What a paragraph is depends on the normaliser, and the two conventions are in
 * `wrappedParagraphs` and `lineParagraphs`.
 */
export function resolveSectionParagraph(index: LayerIndex, section: string, paragraph: number): Resolution {
  const headings = headingLines(index, section);
  if (headings.length === 0) return refuse("section_not_found", `no heading line reads "${section}"`, index.layer_sha256);
  if (headings.length > 1) return refuse("section_ambiguous", `${headings.length} heading lines read "${section}"`, index.layer_sha256);
  if (!Number.isInteger(paragraph) || paragraph < 1) return refuse("paragraph_out_of_range", `paragraph ${paragraph} is not a paragraph number`, index.layer_sha256);

  const perLine = BLOCK_PER_LINE.has(index.normaliser);
  const blocks = perLine ? lineParagraphs(index, headings[0]) : wrappedParagraphs(index, headings[0], paragraph);
  if (blocks.length < paragraph)
    return refuse(
      "paragraph_out_of_range",
      perLine
        ? `the section "${section}" prints ${blocks.length} ${blocks.length === 1 ? "paragraph" : "paragraphs"} before the first blank line and the locator names ${paragraph}`
        : `the section "${section}" holds ${blocks.length} ${blocks.length === 1 ? "paragraph" : "paragraphs"} and the locator names ${paragraph}`,
      index.layer_sha256,
    );

  const block = blocks[paragraph - 1];
  const lead = index.lines[block.from].length - index.lines[block.from].trimStart().length;
  return {
    ok: true,
    kind: "section_paragraph",
    span: spanAt(index, index.u16[block.from] + lead, index.u16[block.to] + index.lines[block.to].replace(/\s+$/, "").length),
    layer_sha256: index.layer_sha256,
  };
}
