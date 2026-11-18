/** The layer registry: what another lane calls to get a text layer and the
 * offsets a claim cites into it.
 *
 * Four questions this answers, and nothing else.
 *
 *   which layers does this source have   layersForSource(id)
 *   which layers does this object have   layersForObject(sha256)
 *   give me the text                     layerText(record)
 *   give me the characters at this span  sliceSpan(text, span)
 *
 * `layerText` re-derives the layer from the stored bytes and refuses to
 * return text whose sha256 is not the one the registry names. There is no
 * second copy of a layer anywhere: ADR 0002 decision 1 says one hash, one
 * home, and the home is ADR 0004's object store. The cost is a pdftotext run
 * per PDF, so a caller working over many spans in one layer reads it once and
 * slices it many times.
 *
 * Offsets. `sliceSpan` takes the code point offsets `shared/omics/locator.ts`
 * declares, because that is what `oa:TextPositionSelector` counts, and
 * returns the UTF-8 byte offsets beside them, because that is what the
 * resolvers slice. JavaScript string indices are neither: they are UTF-16
 * code units, so `slice` on a layer holding an astral character gives the
 * wrong characters. Everything here counts code points.
 *
 * The layer is never Unicode-normalised, here or anywhere, because NFC would
 * move every stored offset the next time ICU changed.
 */
import { readManifest } from "../../../scripts/archive/manifest";
import { readObject } from "../../../scripts/archive/objects";
import { gridNormaliserFor, layerOf, readGrid, walk } from "../../archive/layers/index";
import type { ManifestRow } from "../../archive/schema";
import { readRegistry } from "./registry";
import type { LayerRecord } from "./types";

export * from "./types";
export { metricsOf, ratiosOf, sanityOf, thresholds, usable } from "./sanity";
export {
  buildRegistry,
  layersOfObject,
  pdfPageCount,
  readRegistry,
  readUnsupported,
  registryPath,
  serialiseRegistry,
  serialiseUnsupported,
  unsupportedPath,
  writeRegistry,
  writeUnsupported,
  type BuildProblem,
  type BuildResult,
} from "./registry";
export { coverageOf, type CoverageResult, type CoverageTally, type ReceiptFact, type SourceCoverage } from "./coverage";

/** The registry, read once per process. A caller that has just rebuilt the
 * file passes `reload` to see the new one. */
let cached: { root: string; records: LayerRecord[] } | null = null;
export function registry(root = ".", reload = false): LayerRecord[] {
  if (reload || !cached || cached.root !== root) cached = { root, records: readRegistry(root) };
  return cached.records;
}

/** The object manifest, read once per process. Reading it is sixteen files,
 * and `layerText` needs the served media type the derivation was given. */
let manifestCache: { root: string; rows: Map<string, ManifestRow> } | null = null;
function manifest(root: string): Map<string, ManifestRow> {
  if (!manifestCache || manifestCache.root !== root) manifestCache = { root, rows: readManifest(root) };
  return manifestCache.rows;
}

/** Whether a registry row is a table grid rather than a text layer.
 *
 * A grid is a second layer over the same bytes, holding the table geometry
 * the text layer flattens. It is not an extraction substrate and it is not
 * text, so every reader that means "the text of this source" leaves it out
 * and asks for it by name instead. */
export const isGrid = (record: LayerRecord): boolean => record.normaliser.endsWith("-table-grid@1");

/** Every text layer the registry holds for a source record, best verdict
 * first, then longest. A source with no held bytes has none. Grids are not
 * included: `gridsForSource` returns those. */
export function layersForSource(sourceId: string, root = "."): LayerRecord[] {
  const rank = { pass: 0, suspect: 1, fail: 2 } as const;
  return registry(root)
    .filter((record) => record.source_ids.includes(sourceId) && !isGrid(record))
    .sort((a, b) => rank[a.sanity] - rank[b.sanity] || b.metrics.characters - a.metrics.characters);
}

/** The table grids held for a source, in the same order. */
export function gridsForSource(sourceId: string, root = "."): LayerRecord[] {
  const rank = { pass: 0, suspect: 1, fail: 2 } as const;
  return registry(root)
    .filter((record) => record.source_ids.includes(sourceId) && isGrid(record))
    .sort((a, b) => rank[a.sanity] - rank[b.sanity] || b.metrics.characters - a.metrics.characters);
}

/** The grid that addresses a text layer, by that layer's hash, or null.
 *
 * This is the one call a resolver needs: it has a text layer in hand and
 * wants the geometry the layer lost. The grid's header names the text layer
 * it was built against, and the two are always derived from one object, so
 * the lookup is by object and then by header. */
export function gridForLayer(layerSha256: string, root = "."): LayerRecord | null {
  const text = registry(root).find((record) => record.layer_sha256 === layerSha256);
  if (!text) return null;
  const grid = gridNormaliserFor(text.normaliser);
  if (!grid) return null;
  return (
    registry(root).find(
      (record) => record.object_sha256 === text.object_sha256 && record.derived_from === text.derived_from && record.normaliser === grid,
    ) ?? null
  );
}

/** Every layer under one stored object, text layers and grids both,
 * including the layers of a container's members. */
export function layersForObject(objectSha256: string, root = "."): LayerRecord[] {
  return registry(root).filter((record) => record.object_sha256 === objectSha256);
}

/** One layer by its own hash. A layer reachable from two objects has two
 * registry rows and one set of bytes, so this returns the first. */
export function layerByHash(layerSha256: string, root = "."): LayerRecord | null {
  return registry(root).find((record) => record.layer_sha256 === layerSha256) ?? null;
}

/**
 * The layer text, re-derived from the stored bytes and verified.
 *
 * Throws when the bytes are not held, when the container no longer holds the
 * member the record names, or when the derived layer does not hash to
 * `layer_sha256`. The last case is the one that matters: it means a tool
 * version moved under a stored span, and returning the text anyway would let
 * a span resolve against characters nobody checked.
 */
export function layerText(record: LayerRecord, root = "."): string {
  const row = manifest(root).get(record.object_sha256);
  if (!row) throw new Error(`${record.object_sha256} is not in the object manifest`);
  const tree = layerOf(readObject(record.object_sha256, root), { mediaType: row.media_type });
  for (const { node } of walk(tree)) {
    if (node.layer && node.layer.output_sha256 === record.layer_sha256) return node.layer.bytes.toString("utf8");
    if (node.grid && node.grid.output_sha256 === record.layer_sha256) return node.grid.bytes.toString("utf8");
  }
  const where = record.container_path === null ? "" : ` member ${record.container_path}`;
  throw new Error(`re-deriving ${record.object_sha256}${where} did not reproduce layer ${record.layer_sha256}`);
}

/** A span into a layer, in the two bases `shared/omics/locator.ts` declares. */
export interface SpanSlice {
  /** The characters between the offsets, for an `oa:TextQuoteSelector`. */
  exact: string;
  /** Code point offsets, as given. */
  start: number;
  end: number;
  /** UTF-8 byte offsets into the same layer, which is what a resolver
   * slices. */
  byte_start: number;
  byte_end: number;
}

/**
 * The characters at a code point span, with the byte offsets beside them.
 *
 * Counting is in code points from 0, half open, so `[0, 1)` is the first
 * character however many bytes or UTF-16 units it takes.
 */
export function sliceSpan(text: string, start: number, end: number): SpanSlice {
  if (!Number.isInteger(start) || !Number.isInteger(end)) throw new Error("a span is a pair of integer code point offsets");
  if (start < 0 || end < start) throw new Error(`span ${start} to ${end} is not a range`);
  const points = [...text];
  if (end > points.length) throw new Error(`span ends at ${end} and the layer holds ${points.length} characters`);
  const before = points.slice(0, start).join("");
  const exact = points.slice(start, end).join("");
  const byteStart = Buffer.byteLength(before, "utf8");
  return { exact, start, end, byte_start: byteStart, byte_end: byteStart + Buffer.byteLength(exact, "utf8") };
}

/** The grid a registry row holds, read from its bytes.
 *
 * `record` is a row whose normaliser is a grid normaliser. The bytes are
 * re-derived and hash checked the same way `layerText` does it, so a grid
 * whose builder moved under a stored span is an error and not a silent
 * relocation. */
export function gridOfRecord(record: LayerRecord, root = ".") {
  if (!isGrid(record)) throw new Error(`${record.layer_sha256} is a ${record.normaliser} layer, not a grid`);
  return readGrid(layerText(record, root));
}

/** Characters in a layer, counted the way a span counts them. */
export const characterCount = (text: string): number => [...text].length;
