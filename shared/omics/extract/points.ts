/** Code point offsets to the span the rest of the repository takes.
 *
 * A grid cell carries `start` and `end` as code point offsets into the text layer, because that
 * is what `oa:TextPositionSelector` counts. `spanAt` in `shared/omics/spans/offsets.ts` takes
 * UTF-16 offsets, because that is what a search over a JavaScript string returns. The two bases
 * differ on any layer holding an astral character, so the conversion is written once here
 * rather than guessed at each call site.
 *
 * `sliceSpan` in `shared/omics/layers` converts the same way and is the obvious thing to call.
 * It walks the layer with `[...text]` on every call, which is one pass over the whole layer per
 * cell. The grids hold 73,292 cells, so this does the walk once per layer, through the line
 * tables `indexLayer` already built, and walks only the line the offset falls in.
 */
import { countPoints, spanAt, type LayerIndex } from "../spans/offsets";
import type { Span } from "../locator";

/** The UTF-16 offset of a code point offset, clamped to the layer. */
export function u16AtPoint(index: LayerIndex, point: number): number {
  const total = index.points[index.points.length - 1];
  const wanted = Math.max(0, Math.min(point, total));
  // Which line the offset falls in: the last line whose start is at or before it.
  let low = 0;
  let high = index.points.length - 1;
  while (low < high) {
    const middle = (low + high + 1) >> 1;
    if (index.points[middle] <= wanted) low = middle;
    else high = middle - 1;
  }
  const line = Math.min(low, index.lines.length - 1);
  const text = index.lines[line];
  let remaining = wanted - index.points[line];
  // The separator after the line is one code point and one UTF-16 unit, so an offset past the
  // end of the line's own characters lands on it.
  if (remaining >= countPoints(text)) return index.u16[line] + text.length + Math.max(0, remaining - countPoints(text));
  let unit = 0;
  while (remaining > 0 && unit < text.length) {
    const code = text.codePointAt(unit)!;
    unit += code > 0xffff ? 2 : 1;
    remaining -= 1;
  }
  return index.u16[line] + unit;
}

/** The span a half open code point range names, with both bases and the quote selector. */
export const spanOfPoints = (index: LayerIndex, start: number, end: number): Span =>
  spanAt(index, u16AtPoint(index, start), u16AtPoint(index, end));
