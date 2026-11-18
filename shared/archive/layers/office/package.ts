/** What kind of Office package a run of bytes holds, read from its content.
 *
 * The suffix decides nothing and the first entry in the file decides nothing
 * either. A zip records its members twice: a local header before each
 * member's bytes, and a central directory at the end that lists all of them.
 * A reader that looks only at the first local header sees whichever part the
 * writer happened to put first, and that is not a fixed part. Measured over
 * the 29 Office packages committed under data/omics, 25 open with
 * `[Content_Types].xml`, two with `xl/drawings/drawing1.xml`, one with
 * `docProps/` and one with `_rels/.rels`. The last of those four names no
 * application at all. So the detector reads the central directory, which
 * `zipEntryNames` in ../container already gives without expanding a byte.
 *
 * Two passes, cheapest first.
 *
 * 1. `kindFromNames` reads the central directory only. It is what `classify`
 *    calls, because classification runs over every object in the store and
 *    must not inflate a 5 MB workbook to answer.
 * 2. `readPackage` expands the members and reads `[Content_Types].xml`,
 *    whose Override for the main part is the authoritative statement of what
 *    the package is. It is what the normaliser calls, which has to expand the
 *    members anyway.
 *
 * Where the two disagree the content type wins, because a part prefix is a
 * convention and the content type is a declaration.
 */
import { expandContainer, zipEntryNames, type Limits } from "../container";
import { scanXml } from "./xml";

export const officeKinds = ["xlsx", "xlsm", "docx", "pptx", "opendocument", "ooxml"] as const;
export type OfficeKind = (typeof officeKinds)[number];

/** The media type each kind is recorded under. */
export const officeMediaTypes: Record<OfficeKind, string> = {
  xlsx: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  xlsm: "application/vnd.ms-excel.sheet.macroEnabled.12",
  docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  pptx: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  opendocument: "application/vnd.oasis.opendocument",
  ooxml: "application/vnd.openxmlformats-officedocument",
};

/** Kinds this module builds a layer for. A presentation and an OpenDocument
 * package are detected and reported, not guessed at: there are none in the
 * store, so a normaliser for either would be written against nothing. */
export const normalisedKinds: ReadonlySet<OfficeKind> = new Set<OfficeKind>(["xlsx", "xlsm", "docx"]);

/** Why a detected kind carries no layer. */
export function unsupportedReason(kind: OfficeKind): string {
  if (kind === "pptx") return "office presentation package, no normaliser";
  if (kind === "opendocument") return "opendocument package, no normaliser";
  return "office package with no recognised main part, no normaliser";
}

export interface OfficeDetection {
  kind: OfficeKind;
  /** What in the package decided it. */
  evidence: string;
}

/** The main-part content types OOXML defines, and the kind each one names.
 * Templates and macro-enabled variants carry the same body parts as the
 * document they template, so they map to the same normaliser. */
const mainContentTypes: [string, OfficeKind][] = [
  ["application/vnd.ms-excel.sheet.macroenabled.main+xml", "xlsm"],
  ["application/vnd.ms-excel.template.macroenabled.main+xml", "xlsm"],
  ["application/vnd.ms-excel.addin.macroenabled.main+xml", "xlsm"],
  ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml", "xlsx"],
  ["application/vnd.openxmlformats-officedocument.spreadsheetml.template.main+xml", "xlsx"],
  ["application/vnd.ms-word.document.macroenabled.main+xml", "docx"],
  ["application/vnd.ms-word.template.macroenabled.main+xml", "docx"],
  ["application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml", "docx"],
  ["application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml", "docx"],
  ["application/vnd.ms-powerpoint.presentation.macroenabled.main+xml", "pptx"],
  ["application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml", "pptx"],
  ["application/vnd.openxmlformats-officedocument.presentationml.slideshow.main+xml", "pptx"],
  ["application/vnd.openxmlformats-officedocument.presentationml.template.main+xml", "pptx"],
];

/** The central directory, read far enough to see every member. A workbook in
 * the store holds at most 60 members and the default limit is 64, which is
 * too close to the measured maximum to rely on. */
const entryLimit = 8192;

/**
 * The kind, from the member names alone.
 *
 * Returns null when the bytes are a zip that is not an Office or
 * OpenDocument package, and when the central directory cannot be read.
 */
export function kindFromNames(names: readonly string[]): OfficeDetection | null {
  if (names.includes("mimetype") && names.some((name) => name.startsWith("META-INF/")))
    return { kind: "opendocument", evidence: "mimetype member and a META-INF directory" };
  const part = (prefix: string) => names.find((name) => name.startsWith(prefix));
  const workbook = names.find((name) => name === "xl/workbook.xml" || name === "xl/workbook.bin");
  if (workbook) return { kind: "xlsx", evidence: `member ${workbook}` };
  const document = names.find((name) => name === "word/document.xml");
  if (document) return { kind: "docx", evidence: `member ${document}` };
  const presentation = names.find((name) => name === "ppt/presentation.xml");
  if (presentation) return { kind: "pptx", evidence: `member ${presentation}` };
  for (const [prefix, kind] of [["xl/", "xlsx"], ["word/", "docx"], ["ppt/", "pptx"]] as [string, OfficeKind][]) {
    const found = part(prefix);
    if (found) return { kind, evidence: `member ${found}` };
  }
  if (names.includes("[Content_Types].xml"))
    return { kind: "ooxml", evidence: "member [Content_Types].xml and no recognised main part" };
  return null;
}

/** The kind of a zip, from its central directory. The caller has already seen
 * a zip signature. */
export function detectOffice(bytes: Buffer): OfficeDetection | null {
  return kindFromNames(zipEntryNames(bytes, entryLimit));
}

export interface OfficePackage {
  kind: OfficeKind;
  evidence: string;
  /** Every member, keyed on its path inside the package. */
  members: Map<string, Buffer>;
  /** What the central directory promised and the reader could not deliver. */
  problems: string[];
}

/** The member as text, or null when the package does not hold it. */
export function part(pkg: OfficePackage, path: string): string | null {
  const bytes = pkg.members.get(path);
  if (!bytes) return null;
  // Every OOXML part is UTF-8 or UTF-16 with a byte order mark. Node decodes
  // UTF-8 and leaves a BOM behind, which is stripped because it is framing,
  // not content.
  if (bytes.length >= 2 && bytes[0] === 0xff && bytes[1] === 0xfe) return bytes.subarray(2).toString("utf16le");
  const text = bytes.toString("utf8");
  return text.charCodeAt(0) === 0xfeff ? text.slice(1) : text;
}

/** The kind `[Content_Types].xml` declares, which outranks a part prefix. */
function kindFromContentTypes(pkg: OfficePackage): OfficeDetection | null {
  const text = part(pkg, "[Content_Types].xml");
  if (text === null) return null;
  const declared: string[] = [];
  scanXml(text, {
    open(name, attributes) {
      if (name === "override" && attributes.contenttype) declared.push(attributes.contenttype.toLowerCase());
    },
  });
  for (const [type, kind] of mainContentTypes)
    if (declared.includes(type)) return { kind, evidence: `[Content_Types].xml declares ${type}` };
  return null;
}

/**
 * Expand an Office package and settle its kind.
 *
 * Returns null when the bytes are not an Office or OpenDocument package. The
 * members come back whatever the kind is, because a caller that reports an
 * unsupported kind still wants to say what was in it.
 */
export function readPackage(bytes: Buffer, limits?: Limits): OfficePackage | null {
  const byNames = detectOffice(bytes);
  if (!byNames) return null;
  const expansion = expandContainer(bytes, limits);
  const members = new Map<string, Buffer>();
  for (const member of expansion.members) members.set(member.path, member.bytes);
  const pkg: OfficePackage = { ...byNames, members, problems: expansion.problems };
  const declared = kindFromContentTypes(pkg);
  if (declared) {
    pkg.kind = declared.kind;
    pkg.evidence = declared.evidence;
  }
  return pkg;
}
