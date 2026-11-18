/** Text layers for Office Open XML packages.
 *
 * An Office package is a zip of XML parts. It is not a container in the sense
 * ../container means, because its members are not artifacts a claim would
 * cite: nobody addresses `xl/worksheets/sheet3.xml`. So the package produces
 * one text layer of its own, the way a PDF does, and no member objects.
 *
 * Two normalisers, both pure. `ooxml-sheet-tsv@1` reads a workbook and
 * `ooxml-document-text@1` reads a Word document. A presentation or an
 * OpenDocument package is detected and reported as unsupported, with the
 * reason naming the kind, because the store holds none of either and a
 * normaliser written against nothing cannot be checked.
 */
import type { Layer } from "../types";
import type { Limits } from "../container";
import { documentLayer } from "./document";
import { normalisedKinds, officeMediaTypes, readPackage, unsupportedReason, type OfficeKind, type OfficePackage } from "./package";
import { sheetLayer } from "./sheet";

export { decodeXml, scanXml, textWithin, type XmlHandler } from "./xml";
export {
  detectOffice,
  kindFromNames,
  normalisedKinds,
  officeKinds,
  officeMediaTypes,
  part,
  readPackage,
  unsupportedReason,
  type OfficeDetection,
  type OfficeKind,
  type OfficePackage,
} from "./package";
export {
  blockMarker,
  columnLabel,
  columnNumber,
  escapeCell,
  parseReference,
  readSheet,
  readWorkbook,
  serialiseWorkbook,
  sharedStrings,
  sheetLayer,
  sheetLimits,
  sheetParts,
  unescapeCell,
  type Sheet,
  type SheetCell,
} from "./sheet";
export { bodyPart, documentLayer, serialiseDocument } from "./document";
export {
  cellRange,
  cellRangeByReference,
  findBlock,
  reference,
  rfc7111Fragment,
  sheetBlocks,
  type CellRange,
  type SheetBlock,
} from "./address";

export interface OfficeResult {
  kind: OfficeKind;
  /** What in the package decided the kind. */
  evidence: string;
  media_type: string;
  /** Null when the kind carries no normaliser. */
  layer: Layer | null;
  /** Set when there is no layer. */
  unsupported: string | null;
  problems: string[];
}

/**
 * The text layer of an Office package, or the reason there is none.
 *
 * Returns null when the bytes are not an Office or OpenDocument package, so a
 * caller can fall through to the plain zip reader.
 */
export function officeLayer(input: Buffer, limits?: Limits): OfficeResult | null {
  let pkg: OfficePackage | null;
  try {
    pkg = readPackage(input, limits);
  } catch (error) {
    return {
      kind: "ooxml",
      evidence: "zip signature",
      media_type: officeMediaTypes.ooxml,
      layer: null,
      unsupported: `office package did not expand: ${(error as Error).message}`,
      problems: [],
    };
  }
  if (!pkg) return null;

  const result: OfficeResult = {
    kind: pkg.kind,
    evidence: pkg.evidence,
    media_type: officeMediaTypes[pkg.kind],
    layer: null,
    unsupported: null,
    problems: [...pkg.problems],
  };
  if (!normalisedKinds.has(pkg.kind)) {
    result.unsupported = unsupportedReason(pkg.kind);
    return result;
  }
  try {
    result.layer = pkg.kind === "docx" ? documentLayer(input, pkg, result.problems) : sheetLayer(input, pkg, result.problems);
  } catch (error) {
    result.layer = null;
    result.unsupported = `${pkg.kind} normaliser failed: ${(error as Error).message}`;
  }
  return result;
}
