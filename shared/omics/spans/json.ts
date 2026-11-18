/** A JSON Pointer resolver over a text layer that is the JSON file itself.
 *
 * ADR 0002 names RFC 6901 as the address for JSON, and 2,893 stored locators are JSON paths with
 * a `text-utf8@1` layer held for every one of them. Nothing resolved any of them before this
 * module: the measurement of 2026-11-18 reports all 2,893 refusing, 1,845 `no_resolver_for_kind`
 * and 1,048 `no_anchor`.
 *
 * The problem a JSON locator poses is the opposite of a table's. A table's geometry is lost in
 * the rendering and has to be guessed back; a JSON document's structure is exact and the only
 * question is where in the text each value sits. `JSON.parse` answers the first question and
 * discards the second, so this reads the document itself and keeps every node's offsets.
 *
 * What is refused, and why each refusal is a refusal rather than a guess:
 *
 *   the text is not one JSON document        `json_not_parsed`
 *   the pointer leaves the document          `column_not_found`, with the token that did it
 *   a key is printed twice in one object     `column_ambiguous`: RFC 6901 does not say which
 *   the pointer stops on an array or object  `column_not_found`: a span over a subtree is not
 *                                            a span over a value
 *   a selector picks no element, or several  `row_not_found`, `row_ambiguous`
 *   a cross-check the locator carries fails  `row_key_unmatched`
 *
 * Offsets are UTF-16 into the layer, as everything in this lane is before `spanAt` converts
 * them. A string's span includes its quotes, as a quoted field's span does in `regions.ts`, so
 * the span covers what the file prints.
 */
import { spanAt, type LayerIndex } from "./offsets";
import { FILE_NORMALISERS } from "./regions";
import { refuse, type Resolution } from "./types";

/** What a node is. Objects and arrays are kept whole so a pointer can walk them; a scalar is
 * where a pointer stops. */
export type JsonKind = "object" | "array" | "string" | "number" | "boolean" | "null";

export interface JsonNode {
  kind: JsonKind;
  /** UTF-16 offset of the first character of the value, the opening quote included. */
  from: number;
  /** UTF-16 offset one past its last character. */
  to: number;
  /** For an object: every member, in order, duplicates kept. */
  members?: { key: string; node: JsonNode }[];
  /** For an array: its elements. */
  items?: JsonNode[];
  /** For a string: the decoded text. For a number or a boolean: the text as printed. */
  text?: string;
}

/** How many nodes a document may hold before this refuses to index it. The largest JSON layer
 * in the store holds 1,837,310 characters and indexes to well under this. */
const MAX_NODES = 4_000_000;

class JsonReader {
  private at = 0;
  private nodes = 0;

  constructor(private readonly text: string) {}

  read(): JsonNode {
    this.space();
    const node = this.value();
    this.space();
    if (this.at !== this.text.length) throw new Error(`trailing text at ${this.at}`);
    return node;
  }

  private space(): void {
    while (this.at < this.text.length && (this.text[this.at] === " " || this.text[this.at] === "\n" || this.text[this.at] === "\r" || this.text[this.at] === "\t"))
      this.at += 1;
  }

  private expect(character: string): void {
    if (this.text[this.at] !== character) throw new Error(`expected ${character} at ${this.at}`);
    this.at += 1;
  }

  private value(): JsonNode {
    this.nodes += 1;
    if (this.nodes > MAX_NODES) throw new Error("document holds more nodes than this reader indexes");
    const from = this.at;
    const here = this.text[this.at];
    if (here === "{") return this.object(from);
    if (here === "[") return this.array(from);
    if (here === '"') {
      const text = this.string();
      return { kind: "string", from, to: this.at, text };
    }
    const literal = /^(?:true|false|null|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)/.exec(this.text.slice(this.at, this.at + 48));
    if (!literal) throw new Error(`not a JSON value at ${this.at}`);
    this.at += literal[0].length;
    const kind: JsonKind = literal[0] === "true" || literal[0] === "false" ? "boolean" : literal[0] === "null" ? "null" : "number";
    return { kind, from, to: this.at, text: literal[0] };
  }

  private object(from: number): JsonNode {
    this.expect("{");
    const members: { key: string; node: JsonNode }[] = [];
    this.space();
    if (this.text[this.at] === "}") {
      this.at += 1;
      return { kind: "object", from, to: this.at, members };
    }
    for (;;) {
      this.space();
      const key = this.string();
      this.space();
      this.expect(":");
      this.space();
      members.push({ key, node: this.value() });
      this.space();
      if (this.text[this.at] === ",") {
        this.at += 1;
        continue;
      }
      this.expect("}");
      return { kind: "object", from, to: this.at, members };
    }
  }

  private array(from: number): JsonNode {
    this.expect("[");
    const items: JsonNode[] = [];
    this.space();
    if (this.text[this.at] === "]") {
      this.at += 1;
      return { kind: "array", from, to: this.at, items };
    }
    for (;;) {
      this.space();
      items.push(this.value());
      this.space();
      if (this.text[this.at] === ",") {
        this.at += 1;
        continue;
      }
      this.expect("]");
      return { kind: "array", from, to: this.at, items };
    }
  }

  private string(): string {
    this.expect('"');
    let out = "";
    for (;;) {
      const here = this.text[this.at];
      if (here === undefined) throw new Error("the document ends inside a string");
      if (here === '"') {
        this.at += 1;
        return out;
      }
      if (here !== "\\") {
        out += here;
        this.at += 1;
        continue;
      }
      const escape = this.text[this.at + 1];
      this.at += 2;
      if (escape === "u") {
        out += String.fromCharCode(Number.parseInt(this.text.slice(this.at, this.at + 4), 16));
        this.at += 4;
        continue;
      }
      const simple: Record<string, string> = { '"': '"', "\\": "\\", "/": "/", b: "\b", f: "\f", n: "\n", r: "\r", t: "\t" };
      const decoded = simple[escape ?? ""];
      if (decoded === undefined) throw new Error(`unknown escape at ${this.at - 2}`);
      out += decoded;
    }
  }
}

/** Read one JSON document, keeping every node's offsets, or null where the text is not one.
 *
 * JSON Lines is not JSON and is not read here: a reader that accepted it would have to decide
 * what a pointer into the second line means, and RFC 6901 does not say. */
export function readJson(text: string): JsonNode | null {
  try {
    return new JsonReader(text).read();
  } catch {
    return null;
  }
}

const documents = new WeakMap<LayerIndex, { node: JsonNode | null }>();

/** The parsed document for this layer, read once. */
export function jsonOf(index: LayerIndex): JsonNode | null {
  const held = documents.get(index);
  if (held) return held.node;
  const node = readJson(index.text);
  documents.set(index, { node });
  return node;
}

/** RFC 6901: `~1` is `/` and `~0` is `~`, in that order. */
export function unescapeToken(token: string): string {
  return token.replace(/~1/g, "/").replace(/~0/g, "~");
}

/** RFC 6901, the other way, for printing a pointer back in a refusal. */
export function escapeToken(token: string): string {
  return token.replace(/~/g, "~0").replace(/\//g, "~1");
}

export const renderPointer = (tokens: string[]): string => tokens.map((token) => `/${escapeToken(token)}`).join("");

/**
 * The reference tokens a stored JSON path names.
 *
 * The store writes JSON addresses in the dotted and bracketed form a reader types, not as a
 * pointer: `entries[63].score_avg`, `data.10shot`. Both are read into the same token list that
 * RFC 6901 defines, `["entries", "63", "score_avg"]`, and `$` or `root` at the head is the
 * document itself and names no token. A path already written as a pointer is read as one.
 */
export function pointerTokens(path: string): string[] {
  const text = path.trim();
  if (text.startsWith("/")) return text.split("/").slice(1).map(unescapeToken);
  const tokens: string[] = [];
  for (const part of text.split(".")) {
    const head = /^([^[\]]*)/.exec(part)?.[1] ?? "";
    if (head !== "") tokens.push(head);
    for (const match of part.matchAll(/\[(\d+)\]/g)) tokens.push(match[1]);
  }
  if (tokens.length > 0 && (tokens[0] === "$" || tokens[0] === "root")) tokens.shift();
  return tokens;
}

/** An array index, as RFC 6901 defines it: digits, and no leading zero unless the index is 0. */
const ARRAY_INDEX = /^(?:0|[1-9]\d*)$/;

export type Step =
  | { ok: true; node: JsonNode }
  | { ok: false; reason: "missing" | "duplicate" | "not_a_container" | "index_out_of_range" | "bad_index"; token: string };

/** One reference token applied to one node. */
export function step(node: JsonNode, token: string): Step {
  if (node.kind === "object") {
    const found = (node.members ?? []).filter((member) => member.key === token);
    if (found.length === 0) return { ok: false, reason: "missing", token };
    // RFC 6901 does not say which member a duplicated key names, so neither does this.
    if (found.length > 1) return { ok: false, reason: "duplicate", token };
    return { ok: true, node: found[0].node };
  }
  if (node.kind === "array") {
    if (!ARRAY_INDEX.test(token)) return { ok: false, reason: "bad_index", token };
    const items = node.items ?? [];
    const at = Number(token);
    if (at >= items.length) return { ok: false, reason: "index_out_of_range", token };
    return { ok: true, node: items[at] };
  }
  return { ok: false, reason: "not_a_container", token };
}

export type Walk = { ok: true; node: JsonNode } | { ok: false; at: number; step: Extract<Step, { ok: false }> };

/** Follow every token from the document root, or say which one failed. */
export function walk(root: JsonNode, tokens: string[]): Walk {
  let node = root;
  for (let at = 0; at < tokens.length; at += 1) {
    const next = step(node, tokens[at]);
    if (!next.ok) return { ok: false, at, step: next };
    node = next.node;
  }
  return { ok: true, node };
}

/** The scalar members of an object, as the document prints them. What a cross-check compares. */
export function scalarsOf(node: JsonNode): string[] {
  if (node.kind !== "object") return node.text === undefined ? [] : [node.text];
  const out: string[] = [];
  for (const member of node.members ?? []) if (member.node.text !== undefined) out.push(member.node.text);
  return out;
}

// ---------------------------------------------------------------------------------------------
// The resolver.

/** How a locator's selectors are used against a JSON document: one picks an element of an
 * array, the other descends by key. `selectorRole` in the grammar already tells them apart, so
 * the caller passes the role with each one rather than this guessing it again. */
export interface JsonSelector {
  key: string;
  value: string;
  role: "row" | "column" | "other";
}

/** Compare a selector's value with what the document prints. Exact first, because a JSON
 * document prints its own strings and a locator quotes them; then with surrounding space and
 * case set aside, because a locator is typed by a person. */
const sameValue = (printed: string, wanted: string): boolean =>
  printed === wanted || printed.trim().toLowerCase() === wanted.trim().toLowerCase();

/** Every way a dotted selector value reads as a path from this node.
 *
 * A locator writes a key path with dots, and a key may hold a dot of its own: the stored
 * `key 'cat_MCC.DNA Methyl.'` is the member `DNA Methyl.` of the member `cat_MCC`, and the
 * abbreviating full stop at the end is part of the name. So every split is tried and only the
 * splits the document itself answers survive. Exactly one reading has to resolve; where two do,
 * the document is genuinely ambiguous about what the locator meant and the caller refuses. */
function readings(node: JsonNode, value: string): JsonNode[] {
  const found: JsonNode[] = [];
  const whole = step(node, value);
  if (whole.ok) found.push(whole.node);
  for (let dot = value.indexOf("."); dot >= 0; dot = value.indexOf(".", dot + 1)) {
    const head = step(node, value.slice(0, dot));
    if (head.ok) found.push(...readings(head.node, value.slice(dot + 1)));
  }
  return found;
}

function descend(node: JsonNode, value: string): { ok: true; node: JsonNode } | { ok: false; both: boolean } {
  const found = readings(node, value);
  if (found.length === 1) return { ok: true, node: found[0] };
  return { ok: false, both: found.length > 1 };
}

/**
 * The span of the value a JSON locator names, or the one reason it does not.
 *
 * The address is a pointer and the selectors do the rest. `entries[63].score_avg; submission
 * u2MMaChop9DM3fjqkS7z` is a pointer that lands on the value, with a submission id the
 * addressed object has to print: that is the redundancy ADR 0002 decision 2 asks for, and the
 * resolver refuses when the object does not print it rather than trusting the index. `data.1shot,
 * model 'deepgene', key 'cat_MCC.Promoters'` is a pointer that lands on an array, a selector
 * that has to pick exactly one element of it, and a key path under that element.
 */
export function resolveJsonPointer(
  index: LayerIndex,
  request: { path: string; selectors: JsonSelector[] },
): Resolution {
  if (!FILE_NORMALISERS.has(index.normaliser))
    return refuse("no_column_geometry", `${index.normaliser} is not the JSON file the pointer addresses`, index.layer_sha256);
  const root = jsonOf(index);
  if (root === null) return refuse("json_not_parsed", "the layer is not one JSON document", index.layer_sha256);

  const tokens = pointerTokens(request.path);
  if (tokens.length === 0) return refuse("no_anchor", `"${request.path}" names no reference token`, index.layer_sha256);
  const walked = walk(root, tokens);
  if (!walked.ok) {
    const { step: failed, at } = walked;
    const where = `${renderPointer(tokens.slice(0, at))} has no "${failed.token}"`;
    if (failed.reason === "duplicate")
      return refuse("column_ambiguous", `${renderPointer(tokens.slice(0, at))} prints "${failed.token}" more than once`, index.layer_sha256);
    return refuse("column_not_found", where, index.layer_sha256);
  }

  let node = walked.node;
  // The object the value sits in, which is what a cross-check compares against. A pointer walk
  // keeps it: `/entries/63/score_avg` ends in the object at `/entries/63`.
  let parent: JsonNode | null = tokens.length < 2 ? null : (walk(root, tokens.slice(0, -1)) as Extract<Walk, { ok: true }>).node;
  let picked: string | null = null;
  const used = new Set<JsonSelector>();

  // An array needs a selector to pick an element, and exactly one element may match.
  if (node.kind === "array") {
    const picks = request.selectors.filter((selector) => selector.role !== "column");
    if (picks.length === 0)
      return refuse("no_row_in_locator", `${renderPointer(tokens)} is an array and the locator names nothing to pick an element by`, index.layer_sha256);
    const matched = (node.items ?? []).filter((item) =>
      picks.every((selector) => scalarsOf(item).some((printed) => sameValue(printed, selector.value))),
    );
    if (matched.length === 0)
      return refuse("row_not_found", `no element of ${renderPointer(tokens)} prints ${picks.map((s) => `"${s.value}"`).join(" and ")}`, index.layer_sha256);
    if (matched.length > 1)
      return refuse("row_ambiguous", `${matched.length} elements of ${renderPointer(tokens)} print ${picks.map((s) => `"${s.value}"`).join(" and ")}`, index.layer_sha256);
    parent = matched[0];
    node = matched[0];
    picked = picks.map((selector) => selector.value).join(" / ");
    for (const selector of picks) used.add(selector);
  }

  // A key selector descends from wherever the pointer stopped.
  const header: string[] = [];
  for (const selector of request.selectors) {
    if (selector.role !== "column") continue;
    const next = descend(node, selector.value);
    if (!next.ok)
      return next.both
        ? refuse("column_ambiguous", `"${selector.value}" reads both as one key and as a path, and both are printed`, index.layer_sha256)
        : refuse("column_not_found", `nothing under ${renderPointer(tokens)} is named by "${selector.value}"`, index.layer_sha256);
    parent = node;
    node = next.node;
    header.push(selector.value);
    used.add(selector);
  }

  if (node.kind === "object" || node.kind === "array")
    return refuse("column_not_found", `${renderPointer(tokens)} stops on ${node.kind === "array" ? "an array" : "an object"} and a span over a value is wanted`, index.layer_sha256);
  if (node.kind === "null" || node.text === "" ) return refuse("cell_empty", `${renderPointer(tokens)} prints nothing`, index.layer_sha256);

  // Everything the locator says about the value that was not used to find it is a cross-check.
  // A pointer carries an index and nothing else, and an index into a file that was re-ordered
  // between the reading and the check addresses a different row with no sign that it has.
  const printed = parent === null ? [] : scalarsOf(parent);
  for (const selector of request.selectors) {
    if (used.has(selector)) continue;
    if (!printed.some((text) => sameValue(text, selector.value)))
      return refuse(
        "row_key_unmatched",
        `${renderPointer(tokens)} and ${selector.key} "${selector.value}" name different places: the object the pointer lands in does not print it`,
        index.layer_sha256,
      );
  }

  return {
    ok: true,
    kind: "json_value",
    span: spanAt(index, node.from, node.to),
    layer_sha256: index.layer_sha256,
    row_label: picked ?? undefined,
    column_header: header.length > 0 ? header.join(" / ") : (tokens[tokens.length - 1] ?? undefined),
  };
}
