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

/** The span of a quoted sentence or phrase. */
export function resolveQuote(index: LayerIndex, quote: string): Resolution {
  if (quote.trim().length < 4) return refuse("no_anchor", "a quote under four characters addresses nothing", index.layer_sha256);
  const hits = occurrences(index, quote);
  if (hits.length === 0) return refuse("quote_not_found", `the quoted text is not in this layer`, index.layer_sha256);
  if (hits.length > 1) return refuse("quote_ambiguous", `the quoted text occurs ${hits.length} times or more in this layer`, index.layer_sha256);
  return { ok: true, kind: "quote", span: spanAt(index, hits[0].from, hits[0].to), layer_sha256: index.layer_sha256 };
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
