/** The figures a committed report prints, and the tree they were measured on.
 *
 * A report in `maintenance/reports` states numbers that came out of a command. The numbers go
 * stale the moment the code or the store moves, and a stale number in a committed document reads
 * exactly like a measured one. It has happened in three phases of this work: the layer registry
 * figures, the span resolution figures, and a correction block in ADR 0002 that was stale within
 * the hour of being written.
 *
 * So a measuring command writes its figures here as well as into its prose, with the digest of
 * every file the figures depend on beside them. Two cheap checks then hold the prose to the code,
 * and `tests/omics-report-drift.test.ts` is where they run:
 *
 *   1. Every figure a document tags has to print the value this file records.
 *   2. Every input file has to hash to what this file records.
 *
 * Neither check re-runs the measurement. Check 2 is what makes check 1 mean anything: the figures
 * are only what the code produces now while the code and the store are the ones they were
 * measured on. On a clean clone the object cache is absent by design and a re-run would measure a
 * different store, so re-running in a test would fail for a reason that is not drift.
 *
 * The object cache is deliberately not an input. `layerText` re-derives every layer and checks it
 * against the hash the registry pins, so an object that moved is an error at read time and never
 * a silent change to a figure.
 */
import { createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";

/** Where a measuring command writes its figures. One file per command. */
export const SPAN_FIGURES = "maintenance/reports/span-resolution-figures.json";

/** The files whose content decides the span figures: the resolvers, the grammar, the layer
 * readers, the normalisers, the measurement itself, the layer registry and the records the
 * locators are stored on. A directory entry takes every `.ts` file in it, one level deep. */
export const SPAN_INPUTS = [
  "shared/omics/spans",
  "shared/omics/locator.ts",
  "shared/omics/layers",
  "shared/archive/layers",
  "shared/archive/layers/grid",
  "shared/archive/layers/office",
  "scripts/omics/spans/cli.ts",
  "data/omics/layers/registry.jsonl",
  "data/entities/sources.jsonl",
  "data/evidence/results",
];

export interface FigureInput {
  path: string;
  sha256: string;
  /** Records in a JSONL input when the figures were measured, and the digest of exactly
   * those records. A data file grows as evidence is collected, and appending a record does
   * not make a measured figure wrong about the records it measured. So a data input is
   * checked on its measured prefix: the records that were there must still be there and
   * still say the same thing, while the file is allowed to have grown. A code input has no
   * prefix and is checked whole, because changing the code does make the figures stale. */
  lines?: number;
  prefix_sha256?: string;
}

export interface FigureFile {
  /** The command that wrote this file. */
  command: string;
  /** The date it was written, as the report names it. */
  produced: string;
  /** The documents whose tagged figures these are. */
  documents: string[];
  inputs: FigureInput[];
  /** Flat, dotted keys: `resolved`, `reason.column_not_found`, `kind.quote.no_value`. */
  figures: Record<string, number>;
}

const digestOf = (file: string): string => createHash("sha256").update(fs.readFileSync(file)).digest("hex");

/** A JSONL input also records how many records it held and the digest of just those, so a
 * later append can be told apart from a change to what was measured. */
function prefixOf(file: string): { lines: number; prefix_sha256: string } | null {
  if (!file.endsWith(".jsonl")) return null;
  const text = fs.readFileSync(file, "utf8");
  const lines = text.length === 0 ? [] : text.replace(/\n$/, "").split("\n");
  return { lines: lines.length, prefix_sha256: createHash("sha256").update(lines.join("\n")).digest("hex") };
}

/** The measured prefix of a file as it stands now, or null when it is shorter than it was,
 * which is a removal rather than an append and must fail. */
export function prefixNow(file: string, lines: number): string | null {
  const text = fs.readFileSync(file, "utf8");
  const all = text.length === 0 ? [] : text.replace(/\n$/, "").split("\n");
  if (all.length < lines) return null;
  return createHash("sha256").update(all.slice(0, lines).join("\n")).digest("hex");
}

/** Every input file with its digest, sorted by path. */
export function inputFiles(root: string, inputs: string[] = SPAN_INPUTS): FigureInput[] {
  const found = new Map<string, string>();
  const prefixes = new Map<string, { lines: number; prefix_sha256: string } | null>();
  for (const entry of inputs) {
    const full = path.join(root, entry);
    if (!fs.existsSync(full)) continue;
    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      for (const name of fs.readdirSync(full).sort()) {
        const file = path.join(full, name);
        if (!fs.statSync(file).isFile()) continue;
        if (!name.endsWith(".ts") && !name.endsWith(".jsonl")) continue;
        found.set(`${entry}/${name}`, digestOf(file));
        prefixes.set(`${entry}/${name}`, prefixOf(file));
      }
      continue;
    }
    found.set(entry, digestOf(full));
    prefixes.set(entry, prefixOf(full));
  }
  return [...found.entries()]
    .sort((a, b) => (a[0] < b[0] ? -1 : 1))
    .map(([file, sha256]) => ({ path: file, sha256, ...(prefixes.get(file) ?? {}) }));
}

/** One digest over the lot, for a run that only needs to know whether anything moved. */
export const inputDigest = (inputs: FigureInput[]): string =>
  createHash("sha256").update(inputs.map((input) => `${input.path} ${input.sha256}`).join("\n")).digest("hex");

/** Which input files differ between what a figures file records and the tree now. */
export function changedInputs(recorded: FigureInput[], now: FigureInput[], root = "."): { path: string; was: string; now: string }[] {
  const after = new Map(now.map((input) => [input.path, input]));
  const changed: { path: string; was: string; now: string }[] = [];
  for (const input of recorded) {
    const current = after.get(input.path);
    if (!current) {
      changed.push({ path: input.path, was: input.sha256, now: "absent" });
      continue;
    }
    if (current.sha256 === input.sha256) continue;
    // A data file that only grew still holds what was measured, and a figure measured over
    // 1,483 sources is not made wrong by a 1,484th arriving. Compare the measured prefix.
    if (input.prefix_sha256 !== undefined && input.lines !== undefined) {
      const still = prefixNow(path.join(root, input.path), input.lines);
      if (still === input.prefix_sha256) continue;
      changed.push({
        path: input.path,
        was: `${input.lines} records measured`,
        now: still === null ? "fewer records than were measured" : "a measured record changed",
      });
      continue;
    }
    changed.push({ path: input.path, was: input.sha256, now: current.sha256 });
  }
  for (const input of now) if (!recorded.some((old) => old.path === input.path)) changed.push({ path: input.path, was: "absent", now: input.sha256 });
  return changed.sort((a, b) => (a.path < b.path ? -1 : 1));
}

export const readFigures = (root: string, file = SPAN_FIGURES): FigureFile =>
  JSON.parse(fs.readFileSync(path.join(root, file), "utf8")) as FigureFile;

export function writeFigures(root: string, content: FigureFile, file = SPAN_FIGURES): void {
  const full = path.join(root, file);
  fs.mkdirSync(path.dirname(full), { recursive: true });
  fs.writeFileSync(full, `${JSON.stringify(content, null, 2)}\n`);
}

/**
 * A figure a document prints, tagged so a test can find it.
 *
 * The tag is an HTML comment standing after the number, which renders as nothing in Markdown and
 * in HTML: `11,360 <!--figure:resolved-->`. Tagging rather than parsing the prose is what lets
 * the check name the figure that disagrees instead of reporting that a document holds a number
 * the code does not produce, which a document full of correction blocks does on purpose.
 */
export interface FigureMark {
  /** The dotted figure name. */
  figure: string;
  /** The number printed in front of the tag, as printed. */
  printed: string;
  /** 1 based line of the document, for the failure message. */
  line: number;
}

const MARK = /<!--\s*figure:([a-z0-9_.]+)\s*-->/gi;

export function marks(text: string): FigureMark[] {
  const found: FigureMark[] = [];
  MARK.lastIndex = 0;
  let match: RegExpExecArray | null;
  while ((match = MARK.exec(text)) !== null) {
    const before = text.slice(Math.max(0, match.index - 32), match.index);
    const number = /([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:percent|%|-fold)?[\s)\]]*$/.exec(before);
    found.push({
      figure: match[1],
      printed: number ? number[1] : "",
      line: text.slice(0, match.index).split("\n").length,
    });
  }
  return found;
}

/** Does the printed spelling say this number? Thousands separators are allowed and nothing else
 * is. A figure rounded differently is a different number: the figures file holds a percentage
 * rounded exactly as the tables print it, so a document printing 21.74 where the file holds 21.7
 * fails, which is the whole point. */
export function printsFigure(printed: string, value: number): boolean {
  const plain = printed.replace(/,/g, "");
  if (plain === "" || !/^[0-9]+(?:\.[0-9]+)?$/.test(plain)) return false;
  return Number(plain) === value;
}

/**
 * The same document with the number in front of every tag rewritten from the figures file.
 *
 * Tagging holds a document to the code and leaves a person to retype the numbers, which is the
 * step that did not happen in three phases. This does that step. It touches nothing but the digits
 * standing in front of a tag, so the prose around a figure is still written by whoever owns the
 * document, and a figure the file does not hold is left exactly as it was and reported.
 */
export function retag(text: string, figures: Record<string, number>): { text: string; changed: FigureMark[]; unknown: FigureMark[] } {
  const changed: FigureMark[] = [];
  const unknown: FigureMark[] = [];
  let out = "";
  let read = 0;
  for (const mark of marks(text)) {
    const value = figures[mark.figure];
    if (value === undefined) {
      unknown.push(mark);
      continue;
    }
    if (mark.printed === "" || printsFigure(mark.printed, value)) continue;
    const at = text.indexOf(mark.printed, Math.max(0, lineStart(text, mark.line)));
    if (at < 0) continue;
    out += text.slice(read, at) + spell(value, mark.printed);
    read = at + mark.printed.length;
    changed.push(mark);
  }
  return { text: out + text.slice(read), changed, unknown };
}

/** The start of a 1 based line, so a tag's number is replaced on its own line and not on an
 * earlier line that happens to print the same digits. */
function lineStart(text: string, line: number): number {
  let at = 0;
  for (let count = 1; count < line; count += 1) {
    const next = text.indexOf("\n", at);
    if (next < 0) return at;
    at = next + 1;
  }
  return at;
}

/** The figure spelled the way the one it replaces was spelled, which is with thousands
 * separators or without. */
function spell(value: number, like: string): string {
  const plain = String(value);
  if (!like.includes(",") || !Number.isInteger(value)) return plain;
  return plain.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
