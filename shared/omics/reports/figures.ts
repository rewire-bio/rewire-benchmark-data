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
  /** How many records a JSONL input held when the figures were measured. */
  lines?: number;
  /** One entry per record the figures were measured over, so a data input can be checked
   * record by record rather than as a whole file. A data file grows as evidence is collected,
   * and a figure measured over 1,483 sources is not made wrong by a 1,484th arriving: the
   * records that were measured have to still be there and still say the same thing, while the
   * file is allowed to have gained others. A code input has no records and is checked whole,
   * because changing the code does make the figures stale.
   *
   * This cannot be done by hashing the first `lines` lines of the file. `records add` keeps
   * every store file sorted by ID (`scripts/omics/records.ts`, and `validateRecords` refuses a
   * file that is not), so a new record lands wherever its ID sorts and shifts every line below
   * it. A positional check read that as a changed record: one intake of 116 new sources, none
   * of which touched a measured line, failed as `a measured record changed`.
   *
   * Lives in a file of its own beside the figures, because it is 56,000 lines against the
   * figures file's 500. Held here in memory so the rest of this module sees one shape. */
  records?: MeasuredRecord[];
}

/** One record as it stood when a figure was measured. */
export interface MeasuredRecord {
  /** The record's `id`, or its own line digest for a file whose rows carry no `id`, which is
   * the layer registry. A row keyed on its own content reads as gone rather than as changed
   * when it is edited, which still fails, and registry rows are keyed on content hashes
   * upstream anyway: a different derivation is a different row, not an edit to this one. */
  key: string;
  /** The first `KEY_DIGEST` hex digits of the digest of the line as it was measured. */
  sha256: string;
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

/** Where the measured records of a figures file are kept: one line per record, under a
 * `# <path>` header per input file. A text file sorted the way the store sorts means a commit
 * that adds records shows exactly which, and costs a few lines of delta rather than a rewrite. */
export const recordsFileFor = (figuresFile: string): string => figuresFile.replace(/\.json$/, "-records.tsv");

/** Hex digits kept per record. 48 bits, because the only thing that has to be hard here is for
 * an edited record to collide with its own former content, and nothing is adversarial. */
const KEY_DIGEST = 12;

/** Every record of a JSONL input as it stands, in file order, or null for a code input.
 *
 * Keys repeat only in a file the store would already refuse, so a repeat is numbered rather
 * than dropped: two records that are byte for byte the same are two records, and a check that
 * silently counted them as one could be made to pass by deleting one of them. */
function recordsOf(file: string): MeasuredRecord[] | null {
  if (!file.endsWith(".jsonl")) return null;
  const text = fs.readFileSync(file, "utf8");
  if (text.length === 0) return [];
  const seen = new Map<string, number>();
  return text
    .replace(/\n$/, "")
    .split("\n")
    .map((line) => {
      const sha256 = createHash("sha256").update(line).digest("hex").slice(0, KEY_DIGEST);
      const id = (JSON.parse(line) as { id?: unknown }).id;
      const key = typeof id === "string" && id !== "" ? id : sha256;
      const before = seen.get(key) ?? 0;
      seen.set(key, before + 1);
      return { key: before === 0 ? key : `${key}#${before + 1}`, sha256 };
    });
}

/** Every input file with its digest, sorted by path. */
export function inputFiles(root: string, inputs: string[] = SPAN_INPUTS): FigureInput[] {
  const found = new Map<string, string>();
  const records = new Map<string, MeasuredRecord[] | null>();
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
        records.set(`${entry}/${name}`, recordsOf(file));
      }
      continue;
    }
    found.set(entry, digestOf(full));
    records.set(entry, recordsOf(full));
  }
  return [...found.entries()]
    .sort((a, b) => (a[0] < b[0] ? -1 : 1))
    .map(([file, sha256]) => {
      const rows = records.get(file);
      return rows ? { path: file, sha256, lines: rows.length, records: rows } : { path: file, sha256 };
    });
}

/** One digest over the lot, for a run that only needs to know whether anything moved. */
export const inputDigest = (inputs: FigureInput[]): string =>
  createHash("sha256").update(inputs.map((input) => `${input.path} ${input.sha256}`).join("\n")).digest("hex");

/** The first few record keys, named in a failure so it points at records rather than at a file. */
const NAMED = 3;
const names = (rows: MeasuredRecord[]): string =>
  rows
    .slice(0, NAMED)
    .map((row) => row.key)
    .join(", ") + (rows.length > NAMED ? `, and ${rows.length - NAMED} more` : "");

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
    // A data file that only grew still holds what was measured, so it is checked record by
    // record and may have gained others. Position says nothing: the store keeps these files
    // sorted by ID, so an added record moves every line below it.
    if (input.records !== undefined) {
      const now = current.records ?? recordsOf(path.join(root, input.path)) ?? [];
      const have = new Map(now.map((row) => [row.key, row.sha256]));
      const gone = input.records.filter((row) => !have.has(row.key));
      const edited = input.records.filter((row) => have.has(row.key) && have.get(row.key) !== row.sha256);
      if (gone.length === 0 && edited.length === 0) continue;
      changed.push({
        path: input.path,
        was: `${input.records.length} records measured`,
        now: [
          edited.length > 0 ? `${edited.length} measured ${edited.length === 1 ? "record" : "records"} changed: ${names(edited)}` : "",
          gone.length > 0 ? `${gone.length} measured ${gone.length === 1 ? "record is" : "records are"} gone: ${names(gone)}` : "",
        ]
          .filter((part) => part !== "")
          .join("; "),
      });
      continue;
    }
    changed.push({ path: input.path, was: input.sha256, now: current.sha256 });
  }
  for (const input of now) if (!recorded.some((old) => old.path === input.path)) changed.push({ path: input.path, was: "absent", now: input.sha256 });
  return changed.sort((a, b) => (a.path < b.path ? -1 : 1));
}

/** The figures file with the measured records of its data inputs folded back in from beside it. */
export function readFigures(root: string, file = SPAN_FIGURES): FigureFile {
  const content = JSON.parse(fs.readFileSync(path.join(root, file), "utf8")) as FigureFile;
  const beside = path.join(root, recordsFileFor(file));
  if (!fs.existsSync(beside)) return content;
  const byPath = new Map<string, MeasuredRecord[]>();
  let section: MeasuredRecord[] | undefined;
  for (const line of fs.readFileSync(beside, "utf8").split("\n")) {
    if (line === "") continue;
    if (line.startsWith("# ")) {
      section = [];
      byPath.set(line.slice(2), section);
      continue;
    }
    const [key, sha256] = line.split("\t");
    if (section === undefined) throw new Error(`${recordsFileFor(file)} names a record before any file: ${key}`);
    section.push({ key, sha256 });
  }
  return { ...content, inputs: content.inputs.map((input) => (byPath.has(input.path) ? { ...input, records: byPath.get(input.path) } : input)) };
}

export function writeFigures(root: string, content: FigureFile, file = SPAN_FIGURES): void {
  const full = path.join(root, file);
  fs.mkdirSync(path.dirname(full), { recursive: true });
  const beside = path.join(root, recordsFileFor(file));
  const withRecords = content.inputs.filter((input) => input.records !== undefined);
  for (const input of withRecords)
    for (const row of input.records ?? [])
      if (/[\t\n]/.test(row.key)) throw new Error(`${input.path} holds a record whose ID has a tab or newline in it: ${JSON.stringify(row.key)}`);
  if (withRecords.length === 0) fs.rmSync(beside, { force: true });
  else
    fs.writeFileSync(
      beside,
      `${withRecords.map((input) => [`# ${input.path}`, ...(input.records ?? []).map((row) => `${row.key}\t${row.sha256}`)].join("\n")).join("\n")}\n`,
    );
  // The records live beside the figures, not in them: 56,000 lines against 500.
  const stored = content.inputs.map(({ records, ...rest }) => rest);
  fs.writeFileSync(full, `${JSON.stringify({ ...content, inputs: stored }, null, 2)}\n`);
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
