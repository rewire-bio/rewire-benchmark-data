/** The figure caption resolver.
 *
 * A figure's numbers are in the image, and an image has no text layer. ADR 0002 says so plainly:
 * figure-only values stay gaps, and a value read off a raster image is unverifiable at any layer.
 * What a layer does hold is the caption, and a caption is worth a span: it is where the figure's
 * units, panel letters and sample sizes are printed, and it is the text a reader checks a
 * figure-sourced claim against.
 *
 * So this resolver returns the caption, and says so. It never returns a number from inside a
 * figure, because there is none to return.
 */
import { captionLines, tableWindow } from "./table";
import { spanAt, type LayerIndex } from "./offsets";
import { refuse, type Resolution } from "./types";

/** A caption runs from its first line to the first blank line after it, or 12 lines. */
const CAPTION_LINES = 12;

/** The caption of the figure this anchor names, as a span. */
export function resolveFigureCaption(index: LayerIndex, value: string): Resolution {
  const captions = captionLines(index, "Figure", value);
  if (captions.length === 0) return refuse("anchor_not_found", `no caption line names Figure ${value}`, index.layer_sha256);
  if (captions.length > 1)
    return refuse("anchor_ambiguous", `${captions.length} caption lines name Figure ${value}`, index.layer_sha256);

  const first = captions[0];
  const window = tableWindow(index, first);
  const limit = Math.min(window.to, first + 1 + CAPTION_LINES);
  let last = first;
  for (let line = first + 1; line < limit; line += 1) {
    if (index.lines[line].trim() === "") break;
    last = line;
  }
  return {
    ok: true,
    kind: "figure_caption",
    span: spanAt(index, index.u16[first] + (index.lines[first].length - index.lines[first].trimStart().length), index.u16[last] + index.lines[last].replace(/\s+$/, "").length),
    layer_sha256: index.layer_sha256,
  };
}
