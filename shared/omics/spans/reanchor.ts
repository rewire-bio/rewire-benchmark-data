/** Re-anchoring: does a stored span still mean what it meant, against a layer that moved?
 *
 * A layer is rebuilt when a tool changes. pdftotext 26.08.0 and its successor will not agree on
 * every character of every page, and when they disagree the layer gets a new sha256 and every
 * offset taken against the old one is a number pointing at the wrong place. The stored offsets
 * cannot be trusted and the stored quote can, which is the whole reason ADR 0002 decision 1 puts
 * an `oa:TextQuoteSelector` on every resolvable locator.
 *
 * The rule, in order. The first test that applies decides, and nothing later is consulted.
 *
 *   1. The layer hash equals the span's, and the characters at the offsets equal `exact`.
 *      The span is unchanged. This is the ordinary case and costs one slice.
 *   2. `prefix` + `exact` + `suffix` occurs exactly once in the layer. The span is relocated to
 *      the `exact` inside that one occurrence. Context is tried before the quote alone because a
 *      number such as "0.412" occurs many times and its surroundings do not.
 *   3. `exact` occurs exactly once. The span is relocated to it.
 *   4. `exact` occurs more than once and no context pinned it down: refused, `quote_ambiguous`.
 *   5. `exact` does not occur: refused, `quote_not_found`.
 *
 * Steps 2 and 3 are literal, character for character, because the layer is never normalised. A
 * fourth attempt allows the whitespace inside the quote to differ, which is what a renderer
 * changes when it rewraps a line, and it is reported as its own evidence so a reader can see
 * that the characters were not identical. Nothing picks the occurrence nearest the old offset:
 * proximity is not evidence, and a span placed by proximity is the silent wrong answer this lane
 * exists to prevent.
 */
import type { Span } from "../locator";
import { escape } from "./table";
import { spanAt, type LayerIndex } from "./offsets";
import { refuse, type Refusal } from "./types";

/** What settled the re-anchoring. `offsets` means nothing moved. */
export type AnchorEvidence = "offsets" | "context" | "exact" | "whitespace";

export type Anchoring =
  | { ok: true; outcome: "unchanged" | "relocated"; evidence: AnchorEvidence; span: Span }
  | Refusal;

/** Every occurrence of a literal, as UTF-16 ranges, stopping once the count settles the case. */
function findAll(text: string, needle: string, limit = 2): number[] {
  const found: number[] = [];
  let at = text.indexOf(needle);
  while (at >= 0 && found.length < limit) {
    found.push(at);
    at = text.indexOf(needle, at + 1);
  }
  return found;
}

/** Occurrences of a quote whose internal whitespace is free. */
function findFlexible(index: LayerIndex, quote: string, limit = 2): { from: number; to: number }[] {
  const pattern = new RegExp(quote.trim().split(/\s+/).map(escape).join("\\s+"), "g");
  const found: { from: number; to: number }[] = [];
  let match: RegExpExecArray | null;
  while ((match = pattern.exec(index.text)) !== null && found.length < limit) {
    found.push({ from: match.index, to: match.index + match[0].length });
    pattern.lastIndex = match.index + Math.max(1, match[0].length);
  }
  return found;
}

/** Decide whether a span still resolves against this layer, and where. */
export function reanchor(span: Span, index: LayerIndex): Anchoring {
  if (span.layer_sha256 === index.layer_sha256) {
    const at = codePointSlice(index, span.start, span.end);
    if (at === span.exact) return { ok: true, outcome: "unchanged", evidence: "offsets", span };
  }

  const context = `${span.prefix ?? ""}${span.exact}${span.suffix ?? ""}`;
  if (context !== span.exact) {
    const hits = findAll(index.text, context);
    if (hits.length === 1) {
      const from = hits[0] + (span.prefix ?? "").length;
      return { ok: true, outcome: "relocated", evidence: "context", span: spanAt(index, from, from + span.exact.length) };
    }
  }

  const literal = findAll(index.text, span.exact);
  if (literal.length === 1)
    return { ok: true, outcome: "relocated", evidence: "exact", span: spanAt(index, literal[0], literal[0] + span.exact.length) };
  if (literal.length > 1) return refuse("quote_ambiguous", `the quote occurs more than once and its context does not pin it down`, index.layer_sha256);

  const flexible = findFlexible(index, span.exact);
  if (flexible.length === 1)
    return { ok: true, outcome: "relocated", evidence: "whitespace", span: spanAt(index, flexible[0].from, flexible[0].to) };
  if (flexible.length > 1) return refuse("quote_ambiguous", `the quote occurs more than once once whitespace is allowed to differ`, index.layer_sha256);
  return refuse("quote_not_found", "the quote is not in this layer", index.layer_sha256);
}

/** The characters between two code point offsets, without spreading the layer. */
function codePointSlice(index: LayerIndex, start: number, end: number): string {
  const from = utf16Of(index, start);
  const to = utf16Of(index, end);
  if (from < 0 || to < 0) return "";
  return index.text.slice(from, to);
}

/** The UTF-16 offset of a code point offset, by the same per-line tables the index holds. */
function utf16Of(index: LayerIndex, point: number): number {
  if (point < 0 || point > index.points[index.points.length - 1]) return -1;
  let low = 0;
  let high = index.points.length - 1;
  while (low < high) {
    const middle = (low + high + 1) >> 1;
    if (index.points[middle] <= point) low = middle;
    else high = middle - 1;
  }
  if (low >= index.lines.length) return index.text.length;
  let unit = index.u16[low];
  let remaining = point - index.points[low];
  while (remaining > 0 && unit < index.text.length) {
    const code = index.text.charCodeAt(unit);
    unit += code >= 0xd800 && code <= 0xdbff && unit + 1 < index.text.length ? 2 : 1;
    remaining -= 1;
  }
  return remaining > 0 ? -1 : unit;
}

export { codePointSlice, utf16Of };
