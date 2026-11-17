/** A deterministic tag scanner, shared by the XML and HTML normalisers.
 *
 * No HTML or XML parser is in this repository's dependencies and neither
 * normaliser needs a tree: both want the text content in document order with
 * the element boundaries that a reader would see as a line or a section
 * break. A scanner gives that, handles a document with no prolog, and cannot
 * reorder anything, so the same characters always come out in the same order.
 *
 * Entity decoding is a fixed table plus numeric references. A table that
 * grows changes the output, so it is part of the normaliser version.
 */

/** Boundary strength an element contributes. 0 is inline and contributes
 * nothing; 1 separates with a space, which is what a table cell needs so
 * that a row stays one line; 2 is a line break; 3 is a blank line between
 * sections. */
export type Strength = 0 | 1 | 2 | 3;

export interface ScanRules {
  /** Elements whose content is discarded along with their tags. */
  skip: ReadonlySet<string>;
  /** Boundary strength by lowercased element name. */
  boundary: (name: string) => Strength;
}

const named: Record<string, string> = {
  amp: "&",
  lt: "<",
  gt: ">",
  quot: '"',
  apos: "'",
  nbsp: " ",
  ensp: " ",
  emsp: " ",
  thinsp: " ",
  shy: "",
  // Escaped, not literal: the house style forbids an em or en dash in source
  // text, and these two are data, not prose. The decoded string is identical.
  mdash: "\u2014",
  ndash: "\u2013",
  minus: "−",
  hellip: "…",
  lsquo: "‘",
  rsquo: "’",
  ldquo: "“",
  rdquo: "”",
  sbquo: "‚",
  bdquo: "„",
  dagger: "†",
  Dagger: "‡",
  bull: "•",
  middot: "·",
  deg: "°",
  plusmn: "±",
  times: "×",
  divide: "÷",
  frac12: "½",
  micro: "µ",
  copy: "©",
  reg: "®",
  trade: "™",
  sect: "§",
  para: "¶",
  prime: "′",
  Prime: "″",
  le: "≤",
  ge: "≥",
  ne: "≠",
  asymp: "≈",
  equiv: "≡",
  sim: "∼",
  prop: "∝",
  infin: "∞",
  sum: "∑",
  prod: "∏",
  radic: "√",
  int: "∫",
  part: "∂",
  nabla: "∇",
  isin: "∈",
  notin: "∉",
  cap: "∩",
  cup: "∪",
  alpha: "α",
  beta: "β",
  gamma: "γ",
  delta: "δ",
  epsilon: "ε",
  zeta: "ζ",
  eta: "η",
  theta: "θ",
  kappa: "κ",
  lambda: "λ",
  mu: "μ",
  nu: "ν",
  xi: "ξ",
  pi: "π",
  rho: "ρ",
  sigma: "σ",
  tau: "τ",
  phi: "φ",
  chi: "χ",
  psi: "ψ",
  omega: "ω",
  Alpha: "Α",
  Beta: "Β",
  Gamma: "Γ",
  Delta: "Δ",
  Theta: "Θ",
  Lambda: "Λ",
  Pi: "Π",
  Sigma: "Σ",
  Phi: "Φ",
  Psi: "Ψ",
  Omega: "Ω",
  larr: "\u2190",
  rarr: "\u2192",
  harr: "\u2194",
  uarr: "\u2191",
  darr: "\u2193",
  aacute: "á",
  eacute: "é",
  iacute: "í",
  oacute: "ó",
  uacute: "ú",
  agrave: "à",
  egrave: "è",
  auml: "ä",
  ouml: "ö",
  uuml: "ü",
  szlig: "ß",
  ccedil: "ç",
  ntilde: "ñ",
  oslash: "ø",
  aring: "å",
  ae: "æ",
};

const reference = /&(#[0-9]+|#[xX][0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]{1,31});/g;

/** Decode the entity references the table knows. An unknown reference is left
 * exactly as written, because inventing a character is worse than keeping the
 * source text a reader can see. */
export function decodeEntities(text: string): string {
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

/** The end of a tag, respecting quoted attribute values so that a `>` inside
 * an attribute does not close it early. */
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

/** The text content of a markup document, in order, with boundaries kept. */
export function scanMarkup(text: string, rules: ScanRules): string {
  const parts: string[] = [];
  /** 0 is no pending boundary. */
  let pending: Strength = 0;
  let skipping: string | null = null;
  let skipDepth = 0;

  const emit = (value: string): void => {
    if (!value) return;
    if (pending) {
      parts.push(pending === 3 ? "\n\n" : pending === 2 ? "\n" : " ");
      pending = 0;
    }
    parts.push(value);
  };
  const boundary = (strength: Strength): void => {
    if (strength > pending) pending = strength;
  };

  let index = 0;
  while (index < text.length) {
    const open = text.indexOf("<", index);
    if (open < 0) {
      if (!skipping) emit(decodeEntities(text.slice(index)));
      break;
    }
    if (open > index && !skipping) emit(decodeEntities(text.slice(index, open)));

    if (text.startsWith("<!--", open)) {
      const end = text.indexOf("-->", open + 4);
      index = end < 0 ? text.length : end + 3;
      continue;
    }
    if (text.startsWith("<![CDATA[", open)) {
      const end = text.indexOf("]]>", open + 9);
      if (!skipping) emit(text.slice(open + 9, end < 0 ? text.length : end));
      index = end < 0 ? text.length : end + 3;
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
    if (text.startsWith("<?", open)) {
      const end = text.indexOf("?>", open + 2);
      index = end < 0 ? text.length : end + 2;
      continue;
    }

    const end = tagEnd(text, open + 1);
    if (end < 0) {
      // An unterminated `<` is text, not a tag.
      if (!skipping) emit(decodeEntities(text.slice(open)));
      break;
    }
    const body = text.slice(open + 1, end);
    const closing = body.startsWith("/");
    const selfClosing = body.endsWith("/");
    const match = /^\/?\s*([A-Za-z_][\w.:-]*)/.exec(body);
    index = end + 1;
    if (!match) continue;
    const name = match[1].toLowerCase();

    if (skipping) {
      if (name !== skipping) continue;
      if (closing) {
        skipDepth -= 1;
        if (skipDepth <= 0) {
          skipping = null;
          boundary(2);
        }
      } else if (!selfClosing) skipDepth += 1;
      continue;
    }
    if (!closing && rules.skip.has(name)) {
      if (!selfClosing) {
        skipping = name;
        skipDepth = 1;
      }
      boundary(2);
      continue;
    }
    boundary(rules.boundary(name));
  }

  return tidy(parts.join(""));
}

/** Collapse whitespace runs inside a line, drop blank lines beyond one, and
 * end with a single newline. A layer with no characters is the empty string,
 * never a lone newline. */
export function tidy(text: string): string {
  const lines = text
    .split("\n")
    .map((line) => line.replace(/[^\S\n]+/g, " ").trim());
  const kept: string[] = [];
  for (const line of lines) {
    if (line === "" && (kept.length === 0 || kept[kept.length - 1] === "")) continue;
    kept.push(line);
  }
  while (kept.length && kept[kept.length - 1] === "") kept.pop();
  return kept.length ? `${kept.join("\n")}\n` : "";
}
