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

/** What a reader of the scan is told, as the scan happens.
 *
 * The offsets are UTF-16 indices into the untidied text the scan builds, not
 * into the layer. `tidyTraced` maps them onto the layer afterwards. A reader
 * that wants the table grid listens here rather than parsing the markup a
 * second time, so there is one scanner and the two results cannot drift.
 *
 * `text` reports a run of content that was appended. It excludes the space
 * or newline a boundary inserts before it, so a cell's range starts at its
 * own first character.
 */
export interface ScanEvents {
  open?: (name: string, attributes: string, selfClosing: boolean, at: number) => void;
  close?: (name: string, at: number) => void;
  text?: (from: number, to: number) => void;
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
export function scanMarkup(text: string, rules: ScanRules, events?: ScanEvents): string {
  return tidy(scanRaw(text, rules, events));
}

/**
 * The scan before `tidy` runs: the same characters, with the whitespace the
 * source wrote still in them.
 *
 * `scanMarkup` is this plus `tidy`, so a caller that needs offsets into the
 * untidied text gets them from the one scan the layer is built by.
 */
export function scanRaw(text: string, rules: ScanRules, events?: ScanEvents): string {
  const parts: string[] = [];
  /** 0 is no pending boundary. */
  let pending: Strength = 0;
  let skipping: string | null = null;
  let skipDepth = 0;
  /** UTF-16 units appended so far, which is where the next one lands. */
  let length = 0;

  const push = (value: string): void => {
    parts.push(value);
    length += value.length;
  };
  const emit = (value: string): void => {
    if (!value) return;
    if (pending) {
      push(pending === 3 ? "\n\n" : pending === 2 ? "\n" : " ");
      pending = 0;
    }
    const from = length;
    push(value);
    events?.text?.(from, length);
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
    if (events) {
      const attributes = body.slice(match[0].length).replace(/\/$/, "");
      if (closing) events.close?.(name, length);
      else {
        events.open?.(name, attributes, selfClosing, length);
        if (selfClosing) events.close?.(name, length);
      }
    }
    boundary(rules.boundary(name));
  }

  return parts.join("");
}

/** Collapse whitespace runs inside a line, drop blank lines beyond one, and
 * end with a single newline. A layer with no characters is the empty string,
 * never a lone newline. */
export function tidy(text: string): string {
  return tidyTraced(text).text;
}

/** Whitespace that is not a line break. JavaScript's \s, less "\n", so a
 * no-break space and a tab collapse the same way the regular expression in
 * the first version of `tidy` collapsed them. */
const blank = (unit: string): boolean => unit !== "\n" && /\s/.test(unit);

/** `tidy`, with where every character went. */
export interface TidyTrace {
  text: string;
  /** For each UTF-16 unit of the input, its index in `text`, or -1 when
   * `tidy` dropped it. A whitespace run that collapsed to one space maps its
   * first unit to that space and the rest to -1. */
  out: Int32Array;
}

/**
 * The tidied text and the map from the untidied text onto it.
 *
 * `tidy` is this function's `text`, so there is one implementation and a
 * span taken through the map lands in the layer the normaliser stored.
 */
export function tidyTraced(raw: string): TidyTrace {
  const out = new Int32Array(raw.length).fill(-1);
  const pieces: string[] = [];
  let length = 0;
  /** A blank line waiting to be written, which a trailing one never is. */
  let held = 0;
  let wrote = false;

  let at = 0;
  while (at <= raw.length) {
    let stop = raw.indexOf("\n", at);
    if (stop < 0) stop = raw.length;
    // The line, with runs of whitespace collapsed and both ends trimmed.
    const units: string[] = [];
    const from: number[] = [];
    let run = -1;
    for (let index = at; index < stop; index += 1) {
      const unit = raw[index];
      if (blank(unit)) {
        if (run < 0) run = index;
        continue;
      }
      if (run >= 0) {
        if (units.length > 0) {
          units.push(" ");
          from.push(run);
        }
        run = -1;
      }
      units.push(unit);
      from.push(index);
    }
    if (units.length === 0) {
      if (wrote) held = 1;
    } else {
      if (wrote) {
        pieces.push("\n".repeat(1 + held));
        length += 1 + held;
      }
      held = 0;
      for (let index = 0; index < units.length; index += 1) out[from[index]] = length + index;
      pieces.push(units.join(""));
      length += units.length;
      wrote = true;
    }
    if (stop === raw.length) break;
    at = stop + 1;
  }
  if (wrote) pieces.push("\n");
  return { text: pieces.join(""), out };
}
