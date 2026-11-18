/** Three offset systems over one layer, and the index that converts between them.
 *
 * A span is published in code points, because that is what `oa:TextPositionSelector` counts. A
 * resolver slices bytes, because that is what a UTF-8 file holds. Everything in JavaScript that
 * finds text (`indexOf`, a regular expression, `slice`) works in UTF-16 code units, which is
 * neither. A layer holding one astral character makes all three disagree from that character on.
 *
 * The naive conversion, spreading the layer into an array of code points per span, is correct and
 * unusable: the longest layer in the store holds 13,778,216 characters and the store holds 52,278
 * locators. This index is built once per layer and converts in time proportional to one line.
 *
 * Nothing here normalises. ADR 0002 decision 1 forbids it: NFC would move every stored offset the
 * next time ICU changed.
 */
import type { Span } from "../locator";

/** Code points of context either side of a quote selector. ADR 0002 decision 1 fixes it at 48. */
export const CONTEXT_POINTS = 48;

/** A layer, with the per-line tables that make an offset conversion cheap.
 *
 * `lines` is the layer split on "\n" with the separators removed, so line `i` occupies UTF-16
 * units `[u16[i], u16[i] + lines[i].length)`. The three cumulative arrays hold the count before
 * each line in each system, and carry one extra entry for the end of the layer. */
export interface LayerIndex {
  /** The layer, verbatim. */
  text: string;
  /** The hash the layer registry names it by, which every span taken here cites. */
  layer_sha256: string;
  /** The normaliser that produced it, which decides what a resolver may assume. */
  normaliser: string;
  lines: string[];
  /** UTF-16 unit at which each line starts, plus the layer length. */
  u16: number[];
  /** Code points before each line starts, plus the code point count. */
  points: number[];
  /** UTF-8 bytes before each line starts, plus the byte count. */
  bytes: number[];
}

const isHighSurrogate = (unit: number): boolean => unit >= 0xd800 && unit <= 0xdbff;
const isLowSurrogate = (unit: number): boolean => unit >= 0xdc00 && unit <= 0xdfff;

/** Code points in a string: UTF-16 units less one for each surrogate pair. */
export function countPoints(text: string): number {
  let count = 0;
  for (let i = 0; i < text.length; i += 1) {
    count += 1;
    if (isHighSurrogate(text.charCodeAt(i)) && i + 1 < text.length && isLowSurrogate(text.charCodeAt(i + 1))) i += 1;
  }
  return count;
}

/** Build the per-line tables. One pass over the layer. */
export function indexLayer(text: string, layer_sha256: string, normaliser: string): LayerIndex {
  const lines = text.split("\n");
  const u16: number[] = [];
  const points: number[] = [];
  const bytes: number[] = [];
  let unit = 0;
  let point = 0;
  let byte = 0;
  for (const line of lines) {
    u16.push(unit);
    points.push(point);
    bytes.push(byte);
    unit += line.length + 1;
    point += countPoints(line) + 1;
    byte += Buffer.byteLength(line, "utf8") + 1;
  }
  // The last line has no separator after it, so the closing entry drops the one each loop added.
  u16.push(unit - 1);
  points.push(point - 1);
  bytes.push(byte - 1);
  return { text, layer_sha256, normaliser, lines, u16, points, bytes };
}

/** The line a UTF-16 offset falls in, by binary search over the line starts. */
export function lineAt(index: LayerIndex, u16: number): number {
  let low = 0;
  let high = index.lines.length - 1;
  while (low < high) {
    const middle = (low + high + 1) >> 1;
    if (index.u16[middle] <= u16) low = middle;
    else high = middle - 1;
  }
  return low;
}

/** The code point offset of a UTF-16 offset. */
export function pointAt(index: LayerIndex, u16: number): number {
  const line = lineAt(index, u16);
  return index.points[line] + countPoints(index.text.slice(index.u16[line], u16));
}

/** The UTF-8 byte offset of a UTF-16 offset. */
export function byteAt(index: LayerIndex, u16: number): number {
  const line = lineAt(index, u16);
  return index.bytes[line] + Buffer.byteLength(index.text.slice(index.u16[line], u16), "utf8");
}

/** Code points in the whole layer. */
export const layerPoints = (index: LayerIndex): number => index.points[index.points.length - 1];

/** Pull back a UTF-16 offset that fell inside a surrogate pair, so a slice never splits one. */
function alignStart(text: string, u16: number): number {
  if (u16 > 0 && u16 < text.length && isLowSurrogate(text.charCodeAt(u16)) && isHighSurrogate(text.charCodeAt(u16 - 1))) return u16 - 1;
  return u16;
}

/** Push on a UTF-16 end offset that fell inside a surrogate pair. */
function alignEnd(text: string, u16: number): number {
  if (u16 > 0 && u16 < text.length && isLowSurrogate(text.charCodeAt(u16)) && isHighSurrogate(text.charCodeAt(u16 - 1))) return u16 + 1;
  return u16;
}

/** The last `points` code points of a string, without splitting a surrogate pair. */
function tail(text: string, points: number): string {
  let unit = text.length;
  let taken = 0;
  while (unit > 0 && taken < points) {
    unit -= 1;
    if (unit > 0 && isLowSurrogate(text.charCodeAt(unit)) && isHighSurrogate(text.charCodeAt(unit - 1))) unit -= 1;
    taken += 1;
  }
  return text.slice(unit);
}

/** The first `points` code points of a string, without splitting a surrogate pair. */
function head(text: string, points: number): string {
  let unit = 0;
  let taken = 0;
  while (unit < text.length && taken < points) {
    if (isHighSurrogate(text.charCodeAt(unit)) && unit + 1 < text.length && isLowSurrogate(text.charCodeAt(unit + 1))) unit += 2;
    else unit += 1;
    taken += 1;
  }
  return text.slice(0, unit);
}

/**
 * The span at a UTF-16 half-open range: both offset systems, the exact text, and the 48 code
 * points of context either side that let the span be found again in a rebuilt layer.
 *
 * The caller passes UTF-16 offsets because that is what a search over the layer returns. The span
 * that comes back carries no UTF-16 offset at all, because nothing outside this process should
 * hold one.
 */
export function spanAt(index: LayerIndex, from: number, to: number): Span {
  const start = alignStart(index.text, Math.max(0, Math.min(from, index.text.length)));
  const end = alignEnd(index.text, Math.max(start, Math.min(to, index.text.length)));
  const exact = index.text.slice(start, end);
  const span: Span = {
    layer_sha256: index.layer_sha256,
    start: pointAt(index, start),
    end: pointAt(index, end),
    byte_start: byteAt(index, start),
    byte_end: byteAt(index, end),
    exact,
  };
  const prefix = tail(index.text.slice(Math.max(0, start - CONTEXT_POINTS * 2), start), CONTEXT_POINTS);
  const suffix = head(index.text.slice(end, Math.min(index.text.length, end + CONTEXT_POINTS * 2)), CONTEXT_POINTS);
  if (prefix) span.prefix = prefix;
  if (suffix) span.suffix = suffix;
  return span;
}

/** The span covering whole lines `from` to `to`, both zero based and inclusive. */
export function spanOfLines(index: LayerIndex, from: number, to: number): Span {
  const first = Math.max(0, Math.min(from, index.lines.length - 1));
  const last = Math.max(first, Math.min(to, index.lines.length - 1));
  return spanAt(index, index.u16[first], index.u16[last] + index.lines[last].length);
}
