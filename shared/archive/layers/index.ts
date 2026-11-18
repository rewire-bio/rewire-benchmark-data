/** The text layer: one layer per stored object, so that a later extractor can
 * address a claim to a span of characters in a specific file.
 *
 * layerOf is pure. Bytes go in, a tree of layers comes out, and nothing is
 * written. The caller stores what it wants with storeLayers in ./store.
 *
 * Three rules a reader of this module needs.
 *
 * 1. The class comes from the bytes. A served media type is a hint and the
 *    file suffix is nothing at all. In the committed corpus, file(1) calls
 *    sixty-nine gzipped artifacts text/plain and a third of those are JATS
 *    XML whose first byte is the root element with no prolog.
 * 2. A layer that equals its input is not stored twice. Plain UTF-8 text
 *    passes through unchanged, so its layer sha256 equals the object's own
 *    key and the object already is its own text layer. The result says
 *    identity: true and no second manifest row is written, because the
 *    manifest holds one row per sha256 and a second write would only widen
 *    its source_ids. Several committed artifacts are already pdftotext
 *    output and land here.
 * 3. A container has no text layer. It produces an archive-member object per
 *    member, and the member's text layer is derived from the member, not
 *    from the container. A gzipped PDF is three objects.
 */
import { createHash } from "node:crypto";
import { classify, type Classification } from "./classify";
import { defaultLimits, expandContainer, type Limits } from "./container";
import { hasPdftotext, pdfLayer } from "./pdf";
import { htmlLayer } from "./html";
import { officeLayer } from "./office/index";
import { textLayer } from "./text";
import { xmlLayer } from "./xml";
import type { Layer } from "./types";

export * from "./types";
export { classify, type Classification, type LayerClass } from "./classify";
export { expandContainer, type Member, type Expansion } from "./container";
export { hasPdftotext } from "./pdf";
export { characterCount } from "./text";
export {
  cellRange,
  cellRangeByReference,
  detectOffice,
  officeLayer,
  rfc7111Fragment,
  sheetBlocks,
  type CellRange,
  type OfficeKind,
  type OfficeResult,
  type SheetBlock,
} from "./office/index";

const digest = (bytes: Buffer): string => createHash("sha256").update(bytes).digest("hex");

export interface LayerOptions {
  /** The Content-Type as served, where there is one. Committed bytes have
   * none, so the measurement over them sniffs only. */
  mediaType?: string | null;
  /** How many container expansions deep to go. A .tar.gz is two. */
  maxDepth?: number;
  limits?: Limits;
  /** Override the pdftotext probe. A run without poppler produces no PDF
   * layers and reports why, rather than producing empty ones. */
  pdftotext?: boolean;
}

export interface LayerNode {
  sha256: string;
  bytes: number;
  /** The node's own bytes, so a container member can be stored without the
   * caller expanding the container a second time. */
  content: Buffer;
  classification: Classification;
  /** The text layer, or null when the class carries none. */
  layer: Layer | null;
  /** Why there is no layer. Null when there is one. */
  unsupported: string | null;
  /** Container members, each the root of its own node. */
  members: { path: string; node: LayerNode }[];
  /** What could not be read. Never thrown, always reported. */
  problems: string[];
}

function node(bytes: Buffer, classification: Classification, unsupported: string | null): LayerNode {
  return {
    sha256: digest(bytes),
    bytes: bytes.length,
    content: bytes,
    classification,
    layer: null,
    unsupported,
    members: [],
    problems: [],
  };
}

/** The layer tree for one run of bytes. */
export function layerOf(input: Buffer, options: LayerOptions = {}): LayerNode {
  const depth = options.maxDepth ?? 3;
  const limits = options.limits ?? defaultLimits;
  const pdftotext = options.pdftotext ?? hasPdftotext();
  const classification = classify(input, options.mediaType);
  const result = node(input, classification, classification.unsupported);

  if (classification.class === "container") {
    if (depth <= 0) {
      result.unsupported = "container nested deeper than the expansion limit";
      return result;
    }
    let expansion;
    try {
      expansion = expandContainer(input, limits);
    } catch (error) {
      result.unsupported = (error as Error).message;
      return result;
    }
    result.problems = expansion.problems;
    if (expansion.members.length === 0 && expansion.problems.length === 0)
      result.unsupported = "container holds no readable member";
    for (const member of expansion.members)
      result.members.push({
        path: member.path,
        node: layerOf(member.bytes, { ...options, maxDepth: depth - 1, mediaType: null, pdftotext }),
      });
    return result;
  }

  try {
    if (classification.class === "pdf") {
      if (!pdftotext) {
        result.unsupported = "pdftotext is not installed, so no PDF layer was made";
        return result;
      }
      result.layer = pdfLayer(input);
    } else if (classification.class === "xml") {
      result.layer = xmlLayer(input, classification.encoding ?? undefined);
    } else if (classification.class === "html") {
      result.layer = htmlLayer(input, classification.encoding ?? undefined);
    } else if (classification.class === "text") {
      result.layer = textLayer(input, classification.encoding ?? undefined);
    } else if (classification.class === "office") {
      // An Office package is a zip whose members nobody cites, so it gets one
      // layer of its own and no member objects.
      const office = officeLayer(input, limits);
      if (!office) {
        result.unsupported = "office package that the detector no longer recognises";
        return result;
      }
      result.problems.push(...office.problems);
      result.layer = office.layer;
      result.unsupported = office.unsupported;
    }
  } catch (error) {
    result.unsupported = `${classification.class} normaliser failed: ${(error as Error).message}`;
    result.layer = null;
    return result;
  }
  if (result.layer && result.layer.characters === 0) {
    result.problems.push(`${result.layer.normaliser} produced an empty layer`);
  }
  return result;
}

/** Every node in the tree, parents before children, with the container digest
 * each one came from and the path it sat at. */
export function walk(root: LayerNode): { node: LayerNode; parent: string | null; path: string | null }[] {
  const out: { node: LayerNode; parent: string | null; path: string | null }[] = [];
  const visit = (current: LayerNode, parent: string | null, path: string | null): void => {
    out.push({ node: current, parent, path });
    for (const member of current.members) visit(member.node, current.sha256, member.path);
  };
  visit(root, null, null);
  return out;
}
