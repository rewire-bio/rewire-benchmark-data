/** html-text@1: an HTML page to text, with the boilerplate removed.
 *
 * Boilerplate here means a fixed list of elements and nothing cleverer: the
 * script, style and template content a reader never sees, and the site
 * furniture in nav, header, footer, aside and dialog. A heuristic that
 * guessed at the main content from link density or text length would move
 * every span the first time a page changed shape, so this normaliser prefers
 * keeping too much to guessing.
 *
 * form is deliberately not on the list. The committed CASP16 results page
 * wraps all forty-one of its result tables in one form element, and dropping
 * it left a three hundred and fifty one character layer from an eighty two
 * kilobyte page. Site furniture is named by the HTML5 sectioning elements;
 * a form is a container, not furniture.
 *
 * The result is a function of the input bytes alone. Nothing here reads a
 * clock, a locale or an environment variable.
 */
import { decode, encodingOf, type Encoding } from "./classify";
import { scanMarkup, type Strength } from "./markup";
import { layerFromText } from "./text";
import type { Layer } from "./types";

/** Removed with their content. */
const skip = new Set([
  "script",
  "style",
  "noscript",
  "template",
  "svg",
  "canvas",
  "iframe",
  "nav",
  "header",
  "footer",
  "aside",
  "dialog",
]);

/** A blank line at these: the page's own sections. */
const sections = new Set([
  "article",
  "blockquote",
  "details",
  "figure",
  "h1",
  "h2",
  "h3",
  "h4",
  "h5",
  "h6",
  "hr",
  "main",
  "ol",
  "p",
  "pre",
  "section",
  "table",
  "ul",
]);

/** A line break at these. */
const lines = new Set(["br", "caption", "dd", "div", "dt", "figcaption", "li", "option", "summary", "tr"]);

/** A space, not a line, so that a table row reads as one line. The CASP16
 * results page is forty one tables and nothing else. */
const cells = new Set(["td", "th"]);

const boundary = (name: string): Strength =>
  sections.has(name) ? 3 : lines.has(name) ? 2 : cells.has(name) ? 1 : 0;

/** The text layer of an HTML page. */
export function htmlLayer(input: Buffer, encoding?: Encoding): Layer {
  const found = encoding ?? encodingOf(input);
  if (!found) throw new Error("htmlLayer was given bytes that do not decode as text");
  const text = scanMarkup(decode(input, found), { skip, boundary });
  return layerFromText(input, text, "html-text@1", `html-text@1 strip ${[...skip].sort().join(",")} then tags`);
}
