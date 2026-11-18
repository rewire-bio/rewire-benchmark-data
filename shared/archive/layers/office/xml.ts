/** A deterministic element scanner for the XML parts of an Office package.
 *
 * `shared/archive/layers/markup.ts` already scans markup for the XML and
 * HTML normalisers, and it is the right tool for prose: it returns text with
 * element boundaries applied and whitespace tidied. An Office package needs
 * the opposite. A spreadsheet cell's value must come back exactly as stored,
 * leading and trailing spaces included, and the text inside one shared string
 * must be joined in document order across its runs. A tidied string would
 * change a value and a tree would lose the order, so this file scans events
 * and the caller assembles.
 *
 * `fast-xml-parser` 5.11.2 is in the dependency tree and was tried first. Two
 * things ruled it out. A shared string is `<si>` holding `<t>` elements and
 * `<r>` runs that each hold their own `<t>`, and the concatenation is
 * document order; with `preserveOrder: false` that order is lost, and with
 * `preserveOrder: true` the walk is longer than this scanner. Its defaults
 * also rewrite values: `parseTagValue` turns the stored text "0.10" into 0.1
 * and "1E-05" into 0.00001, which is the one thing a value layer may never
 * do. The scanner has no options to get wrong.
 *
 * Names are lower-cased local names with the namespace prefix dropped, so
 * `<x:row>` and `<row>` both arrive as `row`, and `<w:tc>` arrives as `tc`.
 * Every part this module reads has distinct local names, so nothing collides.
 *
 * Entity decoding is the five XML entities and numeric references, which is
 * all a standalone XML document may use. It is deliberately not the larger
 * table in markup.ts, so that a change there cannot move a layer hash here.
 */

/** The five named entities XML defines without a DTD. */
const named: Record<string, string> = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'" };
const reference = /&(#[0-9]+|#[xX][0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]{1,31});/g;

/** Decode the references XML defines. An unknown reference is left exactly as
 * written, because inventing a character is worse than keeping what is
 * there. */
export function decodeXml(text: string): string {
  if (!text.includes("&")) return text;
  return text.replace(reference, (whole, body: string) => {
    if (body[0] === "#") {
      const code = body[1] === "x" || body[1] === "X" ? Number.parseInt(body.slice(2), 16) : Number.parseInt(body.slice(1), 10);
      if (!Number.isFinite(code) || code <= 0 || code > 0x10ffff) return whole;
      if (code >= 0xd800 && code <= 0xdfff) return whole;
      return String.fromCodePoint(code);
    }
    return Object.hasOwn(named, body) ? named[body] : whole;
  });
}

/** XML 1.0 section 2.11: a parser hands the application a single U+000A
 * wherever the file writes CR LF or a lone CR. The rule is the parser's, not
 * the document's, so two files that differ only in line ending hold the same
 * text and must produce the same layer. It runs before entity decoding,
 * because a numeric reference to CR is a character the author asked for and
 * is not normalised away. */
export const normaliseLineEndings = (text: string): string =>
  text.includes("\r") ? text.replace(/\r\n?/g, "\n") : text;

/** Character data as a parser yields it: line endings normalised, then
 * entities decoded. */
export const readCharacters = (raw: string): string => decodeXml(normaliseLineEndings(raw));

export interface XmlHandler {
  /** An element opens. `selfClosing` elements get no matching close. */
  open?(name: string, attributes: Record<string, string>, selfClosing: boolean): void;
  close?(name: string): void;
  /** Character data, decoded, in document order. */
  text?(value: string): void;
}

/** The local name of a tag or attribute, lower-cased. */
const localName = (name: string): string => {
  const colon = name.lastIndexOf(":");
  return (colon < 0 ? name : name.slice(colon + 1)).toLowerCase();
};

/** The end of a tag, respecting quoted attribute values so a `>` inside an
 * attribute does not close it early. */
function tagEnd(text: string, from: number): number {
  let quote = "";
  for (let index = from; index < text.length; index += 1) {
    const character = text[index];
    if (quote) {
      if (character === quote) quote = "";
      continue;
    }
    if (character === '"' || character === "'") quote = character;
    else if (character === ">") return index;
  }
  return -1;
}

const attributePattern = /([A-Za-z_][\w.:-]*)\s*=\s*("([^"]*)"|'([^']*)')/g;

function attributesOf(body: string): Record<string, string> {
  const attributes: Record<string, string> = {};
  attributePattern.lastIndex = 0;
  let match = attributePattern.exec(body);
  while (match) {
    attributes[localName(match[1])] = readCharacters(match[3] ?? match[4] ?? "");
    match = attributePattern.exec(body);
  }
  return attributes;
}

/** Walk an XML document and report every element and every run of character
 * data, in order. Nothing is buffered and nothing is reordered, so the same
 * bytes always produce the same event sequence. */
export function scanXml(text: string, handler: XmlHandler): void {
  let index = 0;
  while (index < text.length) {
    const open = text.indexOf("<", index);
    if (open < 0) {
      if (handler.text && open !== index) handler.text(readCharacters(text.slice(index)));
      return;
    }
    if (open > index && handler.text) handler.text(readCharacters(text.slice(index, open)));

    if (text.startsWith("<!--", open)) {
      const end = text.indexOf("-->", open + 4);
      index = end < 0 ? text.length : end + 3;
      continue;
    }
    if (text.startsWith("<![CDATA[", open)) {
      const end = text.indexOf("]]>", open + 9);
      if (handler.text) handler.text(normaliseLineEndings(text.slice(open + 9, end < 0 ? text.length : end)));
      index = end < 0 ? text.length : end + 3;
      continue;
    }
    if (text.startsWith("<?", open)) {
      const end = text.indexOf("?>", open + 2);
      index = end < 0 ? text.length : end + 2;
      continue;
    }
    if (text.startsWith("<!", open)) {
      let depth = 0;
      let end = -1;
      for (let at = open + 2; at < text.length; at += 1) {
        const character = text[at];
        if (character === "[") depth += 1;
        else if (character === "]") depth -= 1;
        else if (character === ">" && depth <= 0) {
          end = at;
          break;
        }
      }
      index = end < 0 ? text.length : end + 1;
      continue;
    }

    const end = tagEnd(text, open + 1);
    if (end < 0) {
      // An unterminated `<` is character data, not a tag.
      if (handler.text) handler.text(readCharacters(text.slice(open)));
      return;
    }
    const body = text.slice(open + 1, end);
    index = end + 1;
    const match = /^(\/?)\s*([A-Za-z_][\w.:-]*)/.exec(body);
    if (!match) continue;
    const name = localName(match[2]);
    if (match[1] === "/") {
      handler.close?.(name);
      continue;
    }
    const selfClosing = body.endsWith("/");
    handler.open?.(name, attributesOf(body), selfClosing);
    if (selfClosing) handler.close?.(name);
  }
}

/** Every character of text inside one element, in document order, with the
 * named elements skipped along with their content.
 *
 * This is what a shared string needs: `<si>` may hold one `<t>`, or a list of
 * `<r>` runs each holding a `<t>`, and the value is the concatenation in the
 * order the file writes them.
 */
export function textWithin(fragment: string, keep: ReadonlySet<string>, skip: ReadonlySet<string> = new Set()): string {
  const parts: string[] = [];
  const stack: string[] = [];
  let kept = 0;
  let skipping = 0;
  scanXml(fragment, {
    // scanXml closes a self-closing element straight away, so every open is
    // matched and the stack stays balanced on well formed XML.
    open(name) {
      stack.push(name);
      if (keep.has(name)) kept += 1;
      if (skip.has(name)) skipping += 1;
    },
    close(name) {
      const at = stack.lastIndexOf(name);
      if (at < 0) return;
      for (let index = stack.length - 1; index >= at; index -= 1) {
        if (keep.has(stack[index])) kept -= 1;
        if (skip.has(stack[index])) skipping -= 1;
      }
      stack.length = at;
    },
    text(value) {
      if (skipping === 0 && kept > 0) parts.push(value);
    },
  });
  return parts.join("");
}
