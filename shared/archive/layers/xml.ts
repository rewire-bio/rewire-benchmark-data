/** europepmc-fulltext-xml@1: JATS and other publisher XML.
 *
 * The text content in document order, whitespace runs collapsed, with the
 * element boundaries a reader would see. Forty-seven of the top one hundred
 * and fifty cited unstored sources are Europe PMC fullTextXML, so this is the
 * normaliser that carries the most citations.
 *
 * What it keeps: everything, including the reference list and the front
 * matter. Dropping a section would make a span cited against this layer
 * depend on a judgement about what is worth keeping, and that judgement would
 * then be impossible to change. Only the two elements below are discarded,
 * because neither holds article text.
 *
 * What it does not do: Unicode normalisation. ADR 0003 section 2 forbids it
 * here, because an ICU version change would move every stored offset.
 */
import { decode, encodingOf, type Encoding } from "./classify";
import { scanMarkup, type ScanRules, type Strength } from "./markup";
import { layerFromText } from "./text";
import type { Layer } from "./types";

/** Neither holds article text: one is the Europe PMC tagging record, the
 * other is base64 image data. */
const skip = new Set(["processing-meta", "inline-graphic"]);

/** A blank line between these: the structures a reader sees as sections. */
const sections = new Set([
  "abstract",
  "ack",
  "app",
  "app-group",
  "article-meta",
  "back",
  "body",
  "boxed-text",
  "fig",
  "fn-group",
  "front",
  "glossary",
  "notes",
  "ref-list",
  "sec",
  "supplementary-material",
  "table-wrap",
  "trans-abstract",
]);

/** Run together with the text around them. Everything else gets a line, so a
 * metadata element that nobody listed still reads as its own field rather
 * than running into the next one. The exceptions are the JATS inline set plus
 * MathML and TeX, which are inline by definition. */
const inline = new Set([
  "abbrev",
  "bold",
  "chem-struct",
  "email",
  "ext-link",
  "inline-formula",
  "inline-supplementary-material",
  "italic",
  "milestone-end",
  "milestone-start",
  "monospace",
  "named-content",
  "overline",
  "private-char",
  "roman",
  "sans-serif",
  "sc",
  "strike",
  "styled-content",
  "sub",
  "sup",
  "target",
  "tex-math",
  "underline",
  "uri",
  "x",
  "xref",
]);

/** A space, not a line, so that a table row reads as one line. */
const cells = new Set(["td", "th", "entry"]);

const boundary = (name: string): Strength => {
  if (sections.has(name)) return 3;
  if (inline.has(name) || name.startsWith("mml:") || name.startsWith("m:")) return 0;
  if (cells.has(name)) return 1;
  return 2;
};

/** The rules the normaliser scans by, in one object, so that the table grid
 * built from the same bytes sees exactly the text this layer holds. */
export const xmlRules: ScanRules = { skip, boundary };

/** The text layer of a JATS or other publisher XML document. */
export function xmlLayer(input: Buffer, encoding?: Encoding): Layer {
  const found = encoding ?? encodingOf(input);
  if (!found) throw new Error("xmlLayer was given bytes that do not decode as text");
  const text = scanMarkup(decode(input, found), xmlRules);
  return layerFromText(input, text, "europepmc-fulltext-xml@1", "europepmc-fulltext-xml@1 text content in document order");
}
