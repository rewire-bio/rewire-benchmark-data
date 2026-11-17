/** What class of bytes an object holds.
 *
 * The class decides which normaliser runs. It is read from the bytes
 * themselves, with a served media type as a hint only, because the committed
 * corpus shows the suffix and the served type are both unreliable: 69 of the
 * 236 gzipped artifacts are called text/plain by file(1) and a third of those
 * are JATS XML whose first byte is the root element with no prolog, and one
 * markdown README is called text/html because it carries image tags.
 *
 * Nothing here throws. A class that cannot be determined comes back as
 * "unknown" with the reason, because an unclassifiable source is a finding.
 */
import { isUtf8 as nodeIsUtf8 } from "node:buffer";
import { zipEntryNames } from "./container";

export const layerClasses = ["pdf", "xml", "html", "text", "container", "unknown"] as const;
export type LayerClass = (typeof layerClasses)[number];

export interface Classification {
  class: LayerClass;
  /** The media type this classification implies, not the one served. */
  media_type: string;
  /** What in the bytes decided it, or why nothing did. */
  evidence: string;
  /** Set when the class is known but no text layer can be made from it. */
  unsupported: string | null;
  /** How the bytes decode, for the text classes. */
  encoding: Encoding | null;
}

export type Encoding = "utf-8" | "utf-8-bom" | "utf-16le" | "utf-16be" | "latin-1";

const starts = (bytes: Buffer, prefix: string, at = 0): boolean =>
  bytes.length >= at + prefix.length && bytes.subarray(at, at + prefix.length).toString("latin1") === prefix;

/** Whether the buffer is well formed UTF-8. node:buffer answers this without
 * decoding, which matters here: the largest object in the store is 13 MB and
 * a round trip through a string would copy it twice to answer. */
export function isUtf8(bytes: Buffer): boolean {
  return nodeIsUtf8(bytes);
}

/** How the bytes decode to characters, or null when they are not text. */
export function encodingOf(bytes: Buffer): Encoding | null {
  if (starts(bytes, "\xef\xbb\xbf")) return "utf-8-bom";
  if (starts(bytes, "\xff\xfe")) return "utf-16le";
  if (starts(bytes, "\xfe\xff")) return "utf-16be";
  if (isUtf8(bytes)) return bytes.includes(0) ? null : "utf-8";
  if (bytes.includes(0)) return null;
  // No NUL and not UTF-8. Treat it as text only when the bytes outside the
  // ASCII range are a minority, which separates a latin-1 page from a binary.
  let high = 0;
  for (const byte of bytes) if (byte >= 0x80) high += 1;
  return high * 20 <= bytes.length ? "latin-1" : null;
}

/** The characters the bytes decode to, in UTF-8, with any BOM removed. */
export function decode(bytes: Buffer, encoding: Encoding): string {
  if (encoding === "utf-8") return bytes.toString("utf8");
  if (encoding === "utf-8-bom") return bytes.subarray(3).toString("utf8");
  if (encoding === "utf-16le") return bytes.subarray(2).toString("utf16le");
  if (encoding === "utf-16be") {
    const swapped = Buffer.from(bytes.subarray(2));
    if (swapped.length % 2 !== 0) swapped.writeUInt8(0, swapped.length - 1);
    swapped.swap16();
    return swapped.toString("utf16le");
  }
  return bytes.toString("latin1");
}

/** HTML flow elements that a markdown file commonly opens with. A document
 * rooted at one of these, with no prolog, no doctype and no html element, is
 * markdown or a fragment, not a document: two committed README files open
 * with a centred div or a picture block and the whole rest of the file is
 * markdown.
 *
 * The list is deliberately short. Every name that is also a plausible XML
 * root is left out, article above all, because JATS articles from bioRxiv
 * open at their root element with no prolog and must not land here. */
const htmlElements = new Set([
  "b", "blockquote", "br", "center", "details", "div", "em", "font", "h1", "h2", "h3", "h4", "h5",
  "h6", "hr", "i", "iframe", "img", "kbd", "li", "ol", "p", "picture", "small", "span", "strong",
  "sub", "summary", "sup", "u", "ul", "video",
]);

/** The first markup token, with a prolog, doctype or comment skipped. */
function firstElement(text: string): { name: string; doctype: string | null; prolog: boolean } | null {
  let rest = text.replace(/^﻿/, "").trimStart();
  let doctype: string | null = null;
  let prolog = false;
  for (let step = 0; step < 16; step += 1) {
    if (rest.startsWith("<?")) {
      const end = rest.indexOf("?>");
      if (end < 0) return null;
      if (/^<\?xml[\s?]/i.test(rest)) prolog = true;
      rest = rest.slice(end + 2).trimStart();
      continue;
    }
    if (rest.startsWith("<!--")) {
      const end = rest.indexOf("-->");
      if (end < 0) return null;
      rest = rest.slice(end + 3).trimStart();
      continue;
    }
    if (/^<!doctype/i.test(rest)) {
      // A doctype may carry a bracketed internal subset before its closing >.
      let depth = 0;
      let end = -1;
      for (let index = 0; index < rest.length; index += 1) {
        const character = rest[index];
        if (character === "[") depth += 1;
        else if (character === "]") depth -= 1;
        else if (character === ">" && depth <= 0) {
          end = index;
          break;
        }
      }
      if (end < 0) return null;
      doctype = rest.slice(0, end + 1);
      rest = rest.slice(end + 1).trimStart();
      continue;
    }
    break;
  }
  const match = /^<([A-Za-z_][\w.:-]*)/.exec(rest);
  if (!match) return null;
  return { name: match[1], doctype, prolog };
}

/** Whether a zip is an Office Open XML or OpenDocument package rather than a
 * plain archive. The member that says so is not always the first one: three
 * of the committed packages begin with xl/drawings or docProps, so the whole
 * central directory is read. */
function officePackage(bytes: Buffer): string | null {
  for (const name of zipEntryNames(bytes)) {
    if (name === "[Content_Types].xml") return name;
    if (name === "mimetype") return name;
    if (name.startsWith("xl/") || name.startsWith("word/") || name.startsWith("ppt/") || name.startsWith("docProps/")) return name;
  }
  return null;
}

/**
 * The class of a run of bytes.
 *
 * mediaTypeHint is the served Content-Type where one exists. It decides
 * nothing on its own: magic bytes and the first markup token override it, and
 * it is used only to separate text subclasses that look identical.
 */
export function classify(bytes: Buffer, mediaTypeHint?: string | null): Classification {
  const hint = (mediaTypeHint ?? "").split(";")[0].trim().toLowerCase();
  const no = (klass: LayerClass, media: string, evidence: string, unsupported: string): Classification => ({
    class: klass,
    media_type: media,
    evidence,
    unsupported,
    encoding: null,
  });

  if (bytes.length === 0) return no("unknown", "application/octet-stream", "zero bytes", "empty object");
  if (starts(bytes, "%PDF-"))
    return { class: "pdf", media_type: "application/pdf", evidence: "%PDF- signature", unsupported: null, encoding: null };
  if (starts(bytes, "\x1f\x8b"))
    return { class: "container", media_type: "application/gzip", evidence: "gzip signature", unsupported: null, encoding: null };
  if (starts(bytes, "PK\x03\x04") || starts(bytes, "PK\x05\x06") || starts(bytes, "PK\x07\x08")) {
    const office = officePackage(bytes);
    if (office)
      return no("unknown", "application/zip", `office or opendocument package, member ${office}`, "office package, no normaliser");
    return { class: "container", media_type: "application/zip", evidence: "zip signature", unsupported: null, encoding: null };
  }
  if (starts(bytes, "ustar", 257) && bytes.length >= 512)
    return { class: "container", media_type: "application/x-tar", evidence: "ustar magic at offset 257", unsupported: null, encoding: null };
  if (starts(bytes, "\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"))
    return no("unknown", "application/x-ole-storage", "ole2 compound file signature", "legacy office binary, no normaliser");
  if (starts(bytes, "BZh") || starts(bytes, "\xfd7zXZ") || starts(bytes, "\x28\xb5\x2f\xfd"))
    return no("unknown", "application/octet-stream", "compressed container that is not gzip, zip or tar", "unsupported compression");
  if (starts(bytes, "\x89PNG") || starts(bytes, "\xff\xd8\xff") || starts(bytes, "GIF8"))
    return no("unknown", "image/unknown", "raster image signature", "raster image, no text layer");

  const encoding = encodingOf(bytes);
  if (!encoding) return no("unknown", "application/octet-stream", "not decodable as text and no known signature", "binary, no normaliser");

  const text = decode(bytes, encoding);
  const head = text.slice(0, 4096);
  const element = firstElement(head);
  if (element) {
    const doctype = (element.doctype ?? "").toLowerCase();
    const name = element.name.toLowerCase();
    if (name === "html" || /^<!doctype\s+html/.test(doctype) || hint === "text/html")
      return { class: "html", media_type: "text/html", evidence: `root element ${element.name}`, unsupported: null, encoding };
    if (!element.prolog && !element.doctype && htmlElements.has(name))
      return {
        class: "text",
        media_type: hint && hint.startsWith("text/") ? hint : "text/markdown",
        evidence: `opens with the html element ${element.name} and is not a document`,
        unsupported: null,
        encoding,
      };
    return {
      class: "xml",
      media_type: "application/xml",
      evidence: element.prolog
        ? `root element ${element.name}, xml prolog`
        : element.doctype
          ? `root element ${element.name}, doctype present`
          : `root element ${element.name}`,
      unsupported: null,
      encoding,
    };
  }
  if (hint === "text/html")
    return { class: "html", media_type: "text/html", evidence: "served as text/html, no markup root", unsupported: null, encoding };
  return {
    class: "text",
    media_type: hint && hint.startsWith("text/") ? hint : "text/plain",
    evidence: `decodes as ${encoding}, no markup root`,
    unsupported: null,
    encoding,
  };
}
