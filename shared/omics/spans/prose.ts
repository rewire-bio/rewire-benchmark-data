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

/** The end of the sentence the quote starts, as a UTF-16 offset, or null where none is found
 * within `SENTENCE_UNITS`.
 *
 * A full stop ends a sentence when a space and a capital letter follow it, or when the text
 * does. A full stop between two digits is a decimal point, and the values this lane exists to
 * find are mostly decimals, so that case is excluded explicitly. An abbreviation followed by a
 * capital ("et al. The") ends a sentence here and should not, which over-reads by one sentence
 * and never under-reads: the span stays a superset of the quote. */
function sentenceEnd(text: string, from: number): number | null {
  const limit = Math.min(text.length, from + SENTENCE_UNITS);
  for (let at = from; at < limit; at += 1) {
    const here = text[at];
    if (here !== "." && here !== "!" && here !== "?") continue;
    if (here === "." && /[0-9]/.test(text[at - 1] ?? "") && /[0-9]/.test(text[at + 1] ?? "")) continue;
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
 * optionally numbered. A sentence mentioning "Methods" is not a heading. */
function headingLines(index: LayerIndex, name: string): number[] {
  const wanted = normaliseLabel(name);
  const numbered = /^\s*(?:[0-9]+(?:\.[0-9]+)*\.?|[IVXL]+\.)\s+/i;
  const found: number[] = [];
  for (let line = 0; line < index.lines.length; line += 1) {
    const text = index.lines[line].trim();
    if (text.length === 0 || text.length > 80) continue;
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

/**
 * The nth paragraph of a named section, counted from 1.
 *
 * A paragraph is a run of non-blank lines. The section ends at the next heading-shaped line.
 */
export function resolveSectionParagraph(index: LayerIndex, section: string, paragraph: number): Resolution {
  const headings = headingLines(index, section);
  if (headings.length === 0) return refuse("section_not_found", `no heading line reads "${section}"`, index.layer_sha256);
  if (headings.length > 1) return refuse("section_ambiguous", `${headings.length} heading lines read "${section}"`, index.layer_sha256);
  if (!Number.isInteger(paragraph) || paragraph < 1) return refuse("paragraph_out_of_range", `paragraph ${paragraph} is not a paragraph number`, index.layer_sha256);

  const blocks: { from: number; to: number }[] = [];
  let open: number | null = null;
  for (let line = headings[0] + 1; line < index.lines.length; line += 1) {
    const text = index.lines[line].trim();
    if (text !== "" && headingShaped(index.lines, line)) {
      if (open !== null) blocks.push({ from: open, to: line - 1 });
      open = null;
      break;
    }
    if (text === "") {
      if (open !== null) blocks.push({ from: open, to: line - 1 });
      open = null;
      if (blocks.length >= paragraph) break;
      continue;
    }
    if (open === null) open = line;
  }
  if (open !== null && blocks.length < paragraph) blocks.push({ from: open, to: index.lines.length - 1 });
  if (blocks.length < paragraph)
    return refuse("paragraph_out_of_range", `the section "${section}" holds ${blocks.length} paragraphs and the locator names ${paragraph}`, index.layer_sha256);

  const block = blocks[paragraph - 1];
  const lead = index.lines[block.from].length - index.lines[block.from].trimStart().length;
  return {
    ok: true,
    kind: "section_paragraph",
    span: spanAt(index, index.u16[block.from] + lead, index.u16[block.to] + index.lines[block.to].replace(/\s+$/, "").length),
    layer_sha256: index.layer_sha256,
  };
}
