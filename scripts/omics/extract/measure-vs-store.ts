/** Stage two: the new extractor against the 115 hand-written Python scripts, on the same bytes.
 *
 * The store holds 52,278 results. Nobody has measured how good they are. This runs the new
 * deterministic extractor over every source that has stored results and a geometry the
 * extractor can read, then joins the two sides by position in a hashed text layer: a stored
 * result's resolved span against a candidate's span, same layer, overlapping code points.
 *
 * Position, never value. A table of f1 scores prints 0.73 in four places, so a value join
 * would manufacture agreement.
 *
 * Bins, and why each is split:
 *
 *   agreement        same cell, same number at the precision the record writes
 *   disagreement     same cell, different number, split into formatting and digits
 *   missed           the stored span is inside a layer the extractor read and no candidate
 *                    covers it. Only this is a miss. A stored result whose locator does not
 *                    resolve, or resolves in a layer the extractor does not read, is not
 *                    comparable and is counted apart, because folding it in would report a
 *                    miss rate that is really a statement about PDFs.
 *   extra            a candidate no stored result sits on, split three ways: an invented
 *                    value (the span does not print it), a cell in a table the old scripts
 *                    did touch, and a cell in a table they never touched.
 *
 * Usage: npx tsx scripts/omics/extract/measure-vs-store.ts <store-spans.jsonl> <out-dir>
 * Reads the store read-only and writes nothing into data/.
 */
import fs from "node:fs";
import path from "node:path";
import { valuePresence } from "../spans/cli";
import { gridForLayer, layerText, layersForSource, readRegistry } from "../../../shared/omics/layers/index";
import { buildDecider, extractSource, assessmentKinds, systemKinds } from "../../../shared/omics/extract/index";
import type { Candidate } from "../../../shared/omics/extract/index";
import { readKind } from "../records";

const ROOT = ".";
const dumpFile = process.argv[2];
const outDir = process.argv[3];
if (!dumpFile || !outDir) throw new Error("Usage: npx tsx scripts/omics/extract/measure-vs-store.ts <store-spans.jsonl> <out-dir>");

interface Stored {
  id: string;
  sources: string[];
  locator: string;
  printed_value: string;
  ok: boolean;
  reason: string | null;
  layer: string | null;
  start: number | null;
  end: number | null;
  exact: string | null;
}

const stored: Stored[] = fs
  .readFileSync(dumpFile, "utf8")
  .split("\n")
  .filter((line) => line.trim())
  .map((line) => JSON.parse(line) as Stored);

/** Results per source, and the whole result set keyed by id. */
const bySource = new Map<string, Stored[]>();
for (const item of stored)
  for (const source of item.sources) {
    const held = bySource.get(source);
    if (held) held.push(item);
    else bySource.set(source, [item]);
  }

/** The gold set: every source that has stored results and at least one layer carrying a
 * geometry the extractor reads. Not a hand pick, and not the 20 the build was demonstrated on:
 * those were chosen by source id and most of them hold no stored results to compare against. */
const registry = readRegistry(ROOT);
const classOf = new Map<string, string>();
const gold: string[] = [];
for (const source of [...bySource.keys()].sort()) {
  const classes = new Set<string>();
  for (const record of layersForSource(source, ROOT)) {
    if (record.sanity === "fail") continue;
    const grid = gridForLayer(record.layer_sha256, ROOT);
    if (grid) classes.add(grid.normaliser);
    else if (record.normaliser === "ooxml-sheet-tsv@1") classes.add("ooxml-sheet-tsv@1");
  }
  if (classes.size === 0) continue;
  gold.push(source);
  classOf.set(source, [...classes].sort().join("+"));
}
/** A fourth argument narrows the run to named sources, for probing the join before scaling. */
const only = process.argv[4] ? new Set(process.argv[4].split(",")) : null;
const run = only ? gold.filter((source) => only.has(source)) : gold;

const kinds = new Set<string>([...systemKinds, ...assessmentKinds]);
const named = [...kinds].sort().flatMap((kind) => readKind(kind));
const decider = buildDecider(named);

type Outcome =
  | "agreement"
  | "disagree_scale"
  | "disagree_digits"
  | "missed"
  | "not_comparable_layer"
  | "not_comparable_unresolved";

const rank: Record<Outcome, number> = {
  agreement: 0,
  disagree_scale: 1,
  disagree_digits: 2,
  missed: 3,
  not_comparable_layer: 4,
  not_comparable_unresolved: 5,
};

interface Verdict {
  outcome: Outcome;
  source: string;
  cls: string;
  candidate: string | null;
  candidate_value: string | null;
}

const verdicts = new Map<string, Verdict>();
/** Every candidate ever matched by a stored result, and every table a stored result landed in. */
const matchedCandidates = new Set<string>();
const touchedTables = new Set<string>();

interface ExtraRow {
  candidate_id: string;
  source: string;
  cls: string;
  bin: "invented" | "extra_value_already_stored" | "extra_touched_table" | "extra_untouched_table";
  printed_value: string;
  table: string;
}
const extras: ExtraRow[] = [];
const sourceRows: string[] = [];
const disagreements: string[] = [];
const misses: string[] = [];
/** Agreements where the two sides keep different text around the same number. */
let textDiffers = 0;
/** The invention test, counted over every candidate. */
let spanChecked = 0;
let spanBytesWrong = 0;
let spanPointsWrong = 0;
let spanValueWrong = 0;
const inventions: string[] = [];
/** Fields decided on the candidates that agreed with a stored result. */
const decidedOnAgreement: Record<string, number> = {};
let completeOnAgreement = 0;
/** Agreements where more than one candidate overlapped the stored span, which is the only way
 * the join could pick a neighbour that happens to print the same number. */
let agreementsAmbiguous = 0;
/** Agreements the numbers matched only after reading the stored value's leading number, which
 * is the looser half of the comparison and the half worth reading by eye. */
const headMatches: string[] = [];
/** Which stored results each candidate was matched to, to find a candidate matched twice. */
const matchedBy = new Map<string, string[]>();

/** The number a side reports, as against the text it keeps around it.
 *
 * The two sides keep different text by design and comparing the text would report a
 * disagreement on every cell that prints a spread. A record written by the old scripts keeps
 * `0.114` and puts the spread in its own field; a candidate keeps the cell verbatim,
 * `0.114 (0.007)`, with `0.114` in `numeric_value` and `0.007` in `uncertainty_printed`. The
 * same reading, written two ways. So the comparison is between the numbers, and the text
 * difference is counted separately. */
const headNumber = (text: string): string | null => {
  // The same cleaning `numberFrom` in scripts/omics/extract/tables.ts does: every unicode dash
  // is a minus and a thousands separator is not a digit boundary. Without it a record keeping
  // "398,597" reads as 398 and a record keeping "1.74E‐5" loses its exponent, and the
  // comparison reports as disagreements 27 cells that are one number written two ways.
  const clean = text.replace(/[‐-―−]/g, "-").replace(/[,\s ]/g, "");
  const match = /(-?\d*\.?\d+(?:[eE][-+]?\d+)?)/.exec(clean);
  return match ? match[1] : null;
};
/** Do the two sides report the same number, at the precision the record writes?
 * `valuePresence` applies the repository's own rule, which is the one the span measurement is
 * held to. */
const sameNumber = (candidate: string | null, stored: string): boolean => {
  if (candidate === null) return false;
  if (valuePresence(candidate, stored).exact) return true;
  const head = headNumber(stored);
  return head !== null && valuePresence(candidate, head).exact;
};
/** One side writing a percentage where the other writes a fraction. A convention difference,
 * not a wrong number, and worth its own bin because nothing downstream could tell which
 * convention the metric wants. */
const sameScaled = (candidate: string | null, stored: string): boolean => {
  const head = headNumber(stored);
  if (candidate === null || head === null) return false;
  const a = Number(candidate);
  const b = Number(head);
  if (!Number.isFinite(a) || !Number.isFinite(b) || a === 0 || b === 0) return false;
  const ratio = a / b;
  return Math.abs(ratio - 100) < 1e-6 || Math.abs(ratio - 0.01) < 1e-9;
};

/** A TSV field: one line, tabs and newlines written as escapes so a row stays a row. */
const field = (text: string): string => text.replace(/\\/g, "\\\\").replace(/\t/g, "\\t").replace(/\r?\n/g, "\\n");

/** Why a stored result the extractor missed was missed, read off the text at its own span.
 *
 * The bins are shapes of printed cell, not guesses about intent, and they are what says
 * whether a miss is a defect or a boundary. */
const missShape = (text: string): string => {
  const flat = text.replace(/[−–—]/g, "-").replace(/\s+/g, " ").trim();
  if (flat === "") return "empty_span";
  if (/^-?[\d.]+\s*(?:±|\().+$/.test(flat)) return "value_with_tail";
  if (/^[[(]\s*-?[\d.]+\s*[,;-]\s*-?[\d.]+\s*[\])]$/.test(flat)) return "interval_only";
  if (/^(?:≤|≥|<|>|~|≈)\s*-?[\d.]+/.test(flat)) return "bound_only";
  if (/^-?[\d.,]+%?$/.test(flat)) return "plain_number";
  if (flat.split(" ").length > 6) return "prose";
  return "other";
};

const tableKey = (candidate: Candidate): string =>
  `${candidate.layer_sha256}\u0000${candidate.anchor.kind}\u0000${candidate.anchor.index}`;

let done = 0;
for (const source of run) {
  done += 1;
  const cls = classOf.get(source) ?? "none";
  let extraction;
  try {
    extraction = extractSource(source, decider, ROOT);
  } catch (error) {
    sourceRows.push([source, cls, "error", String((error as Error).message).slice(0, 120)].join("\t"));
    continue;
  }
  const { candidates, tally } = extraction;
  const readLayers = new Set(tally.layers.map((layer) => layer.layer_sha256));

  /** Candidates by layer, ordered by where they start, so an overlap search is a scan. */
  const byLayer = new Map<string, Candidate[]>();
  for (const candidate of candidates) {
    const held = byLayer.get(candidate.span.layer_sha256);
    if (held) held.push(candidate);
    else byLayer.set(candidate.span.layer_sha256, [candidate]);
  }
  for (const held of byLayer.values()) held.sort((a, b) => a.span.start - b.span.start);

  // The invention test, run on every candidate of every gold source rather than a sample, and
  // run against the layer bytes rather than against the index the pass built its spans from.
  // Three separate questions. Do the byte offsets cover the characters the span claims? Do the
  // code point offsets? And does the layer, at those characters, print the number the candidate
  // reports? A candidate that fails the third has invented a value.
  for (const [layerSha, held] of byLayer) {
    const record = registry.find((row) => row.layer_sha256 === layerSha);
    if (!record) continue;
    const text = layerText(record, ROOT);
    const bytes = Buffer.from(text, "utf8");
    const points = Array.from(text);
    for (const candidate of held) {
      spanChecked += 1;
      if (bytes.subarray(candidate.span.byte_start, candidate.span.byte_end).toString("utf8") !== candidate.span.exact)
        spanBytesWrong += 1;
      if (points.slice(candidate.span.start, candidate.span.end).join("") !== candidate.span.exact) spanPointsWrong += 1;
      const inSpan =
        candidate.numeric_value !== null &&
        (valuePresence(candidate.span.exact, candidate.numeric_value).present ||
          sameNumber(candidate.numeric_value, candidate.span.exact));
      if (!inSpan) {
        spanValueWrong += 1;
        if (inventions.length < 200)
          inventions.push([candidate.candidate_id, source, cls, candidate.numeric_value ?? "", candidate.span.exact].map(field).join("\t"));
      }
    }
  }

  const localMatched = new Set<string>();
  const localTouched = new Set<string>();
  /** Numbers this source's stored results hold that the span join could not place. */
  const unplaced = new Map<string, number>();

  for (const item of bySource.get(source) ?? []) {
    let outcome: Outcome;
    let hit: Candidate | null = null;
    if (!item.ok || item.layer === null || item.start === null || item.end === null) {
      outcome = "not_comparable_unresolved";
    } else if (!readLayers.has(item.layer)) {
      outcome = "not_comparable_layer";
    } else {
      const here = byLayer.get(item.layer) ?? [];
      const overlapping = here.filter((candidate) => candidate.span.start < (item.end as number) && candidate.span.end > (item.start as number));
      if (overlapping.length === 0) {
        outcome = "missed";
      } else {
        hit =
          overlapping.find((candidate) => sameNumber(candidate.numeric_value, item.printed_value)) ??
          overlapping[0];
        if (sameNumber(hit.numeric_value, item.printed_value)) {
          outcome = "agreement";
          if (overlapping.length > 1) agreementsAmbiguous += 1;
          if (hit.printed_value.trim() !== item.printed_value.trim()) textDiffers += 1;
          if (hit.numeric_value !== null && !valuePresence(hit.numeric_value, item.printed_value).exact && headMatches.length < 400)
            headMatches.push([item.id, source, item.printed_value, hit.numeric_value, hit.printed_value].map(field).join("\t"));
          // What a candidate that found a real result still cannot say. This is the record
          // question rather than the cell question: a candidate with the right number and no
          // decided metric cannot become a record, so these counts are what a later stage
          // would have to settle before any of this could be written back to the store.
          for (const name of ["metric", "direction", "unit", "model", "assessment"] as const)
            if (hit[name].decided !== null) decidedOnAgreement[name] = (decidedOnAgreement[name] ?? 0) + 1;
          if (hit.complete) completeOnAgreement += 1;
        } else outcome = sameScaled(hit.numeric_value, item.printed_value) ? "disagree_scale" : "disagree_digits";
      }
    }
    if (hit) {
      const held = matchedBy.get(hit.candidate_id);
      if (held) held.push(item.id);
      else matchedBy.set(hit.candidate_id, [item.id]);
      localMatched.add(hit.candidate_id);
      localTouched.add(tableKey(hit));
    }
    const held = verdicts.get(item.id);
    if (!held || rank[outcome] < rank[held.outcome])
      verdicts.set(item.id, {
        outcome,
        source,
        cls,
        candidate: hit?.candidate_id ?? null,
        candidate_value: hit?.printed_value ?? null,
      });
    if (outcome === "disagree_digits" || outcome === "disagree_scale")
      disagreements.push(
        [
          item.id,
          source,
          cls,
          outcome,
          item.printed_value,
          hit?.numeric_value ?? "",
          hit?.printed_value ?? "",
          item.exact ?? "",
          item.locator,
          hit?.source_locator ?? "",
        ].map(field).join("\t"),
      );
    if (outcome === "missed")
      misses.push(
        [item.id, source, cls, missShape(item.exact ?? ""), item.printed_value, item.exact ?? "", item.locator]
          .map(field)
          .join("\t"),
      );
    if (outcome === "not_comparable_unresolved" || outcome === "not_comparable_layer") {
      const head = headNumber(item.printed_value);
      if (head !== null) unplaced.set(head, (unplaced.get(head) ?? 0) + 1);
    }
  }

  for (const id of localMatched) matchedCandidates.add(id);
  for (const key of localTouched) touchedTables.add(key);

  for (const candidate of candidates) {
    if (localMatched.has(candidate.candidate_id)) continue;
    // A candidate the join did not reach is not automatically a result nobody holds. Half the
    // store's locators do not resolve to a span at all, and a stored result that could not be
    // placed in a layer cannot match any candidate however right both are. So before a
    // candidate is called new, it is checked against the numbers this source's unplaced stored
    // results hold, one for one: 20 unplaced results can account for at most 20 candidates.
    // Measured on hitdisc-20261022-source-shen2025: the extractor emits exactly the 20 Table 2
    // cells the store holds for the row 'ipTM' and the span join reached none of them.
    const head = candidate.numeric_value === null ? null : headNumber(candidate.numeric_value);
    const held = head === null ? 0 : unplaced.get(head) ?? 0;
    let bin: ExtraRow["bin"];
    if (candidate.span.exact !== candidate.printed_value) bin = "invented";
    else if (held > 0) {
      unplaced.set(head as string, held - 1);
      bin = "extra_value_already_stored";
    } else bin = localTouched.has(tableKey(candidate)) ? "extra_touched_table" : "extra_untouched_table";
    extras.push({
      candidate_id: candidate.candidate_id,
      source,
      cls,
      bin,
      printed_value: candidate.printed_value,
      table: `${candidate.anchor.kind} ${candidate.anchor.label || candidate.anchor.index}`,
    });
  }

  sourceRows.push(
    [
      source,
      cls,
      String((bySource.get(source) ?? []).length),
      String(candidates.length),
      String(tally.complete),
      tally.layers.map((layer) => `${layer.normaliser}:${layer.candidates}`).join(" "),
      tally.skipped.map((layer) => `${layer.normaliser}:${layer.reason}`).join(" "),
    ].join("\t"),
  );
  if (done % 20 === 0) console.error(`${done} of ${run.length} sources`);
}

/** A candidate's span must print its own value by construction. Measured over every candidate
 * of every gold source, not a sample. */
const invented = extras.filter((row) => row.bin === "invented").length;

fs.mkdirSync(outDir, { recursive: true });
const tally = new Map<string, Map<Outcome, number>>();
for (const verdict of verdicts.values()) {
  const held = tally.get(verdict.cls) ?? new Map<Outcome, number>();
  held.set(verdict.outcome, (held.get(verdict.outcome) ?? 0) + 1);
  tally.set(verdict.cls, held);
}
const outcomes: Outcome[] = [
  "agreement",
  "disagree_scale",
  "disagree_digits",
  "missed",
  "not_comparable_layer",
  "not_comparable_unresolved",
];
const lines = [["class", ...outcomes, "total"].join("\t")];
for (const [cls, held] of [...tally.entries()].sort()) {
  const row = outcomes.map((outcome) => held.get(outcome) ?? 0);
  lines.push([cls, ...row.map(String), String(row.reduce((sum, n) => sum + n, 0))].join("\t"));
}
fs.writeFileSync(path.join(outDir, "by-class.tsv"), `${lines.join("\n")}\n`);

const extraTally = new Map<string, Map<string, number>>();
for (const row of extras) {
  const held = extraTally.get(row.cls) ?? new Map<string, number>();
  held.set(row.bin, (held.get(row.bin) ?? 0) + 1);
  extraTally.set(row.cls, held);
}
const extraBins = ["invented", "extra_value_already_stored", "extra_touched_table", "extra_untouched_table"];
const extraLines = [["class", ...extraBins, "total"].join("\t")];
for (const [cls, held] of [...extraTally.entries()].sort()) {
  const row = extraBins.map((bin) => held.get(bin) ?? 0);
  extraLines.push([cls, ...row.map(String), String(row.reduce((sum, n) => sum + n, 0))].join("\t"));
}
fs.writeFileSync(path.join(outDir, "extras-by-class.tsv"), `${extraLines.join("\n")}\n`);

fs.writeFileSync(
  path.join(outDir, "by-source.tsv"),
  `${["source", "class", "stored_results", "candidates", "complete", "layers_read", "layers_skipped"].join("\t")}\n${sourceRows.join("\n")}\n`,
);
fs.writeFileSync(
  path.join(outDir, "disagreements.tsv"),
  `${["result_id", "source", "class", "bin", "stored_value", "candidate_numeric", "candidate_printed", "stored_span_text", "stored_locator", "candidate_locator"].join("\t")}\n${disagreements.join("\n")}\n`,
);
fs.writeFileSync(
  path.join(outDir, "misses.tsv"),
  `${["result_id", "source", "class", "shape", "stored_value", "stored_span_text", "stored_locator"].join("\t")}\n${misses.join("\n")}\n`,
);
fs.writeFileSync(
  path.join(outDir, "span-value-mismatch.tsv"),
  `${["candidate_id", "source", "class", "numeric_value", "span_text"].join("\t")}\n${inventions.join("\n")}\n`,
);
fs.writeFileSync(
  path.join(outDir, "head-matches.tsv"),
  `${["result_id", "source", "stored_value", "candidate_numeric", "candidate_printed"].join("\t")}\n${headMatches.join("\n")}\n`,
);
fs.writeFileSync(
  path.join(outDir, "doubly-matched.tsv"),
  `${["candidate_id", "result_ids"].join("\t")}\n${[...matchedBy.entries()].filter(([, ids]) => ids.length > 1).map(([id, ids]) => `${id}\t${ids.join(" ")}`).join("\n")}\n`,
);
fs.writeFileSync(path.join(outDir, "extras.jsonl"), `${extras.map((row) => JSON.stringify(row)).join("\n")}\n`);

/** What the document prints at the span of every stored result the extractor did not find.
 * A miss on a cell printing a plain number is a defect; a miss on a sentence is the boundary
 * of a pass that reads tables. */
const shapes = new Map<string, Map<string, number>>();
for (const line of misses) {
  const [, , cls, shape] = line.split("\t");
  const held = shapes.get(cls) ?? new Map<string, number>();
  held.set(shape, (held.get(shape) ?? 0) + 1);
  shapes.set(cls, held);
}
const shapeNames = [...new Set(misses.map((line) => line.split("\t")[3]))].sort();
const shapeLines = [["class", ...shapeNames, "total"].join("\t")];
for (const [cls, held] of [...shapes.entries()].sort()) {
  const row = shapeNames.map((shape) => held.get(shape) ?? 0);
  shapeLines.push([cls, ...row.map(String), String(row.reduce((sum, n) => sum + n, 0))].join("\t"));
}
fs.writeFileSync(path.join(outDir, "misses-by-shape.tsv"), `${shapeLines.join("\n")}\n`);

const summary = {
  gold_sources: run.length,
  stored_results_on_gold_sources: verdicts.size,
  stored_results_total: stored.length,
  candidates: extras.length + matchedCandidates.size,
  candidates_matched: matchedCandidates.size,
  invented,
  agreements_with_different_text: textDiffers,
  span_checked: spanChecked,
  span_bytes_wrong: spanBytesWrong,
  span_points_wrong: spanPointsWrong,
  span_value_wrong: spanValueWrong,
  agreements_with_several_overlapping_candidates: agreementsAmbiguous,
  candidates_matched_to_more_than_one_result: [...matchedBy.values()].filter((ids) => ids.length > 1).length,
  decided_on_agreement: decidedOnAgreement,
  complete_on_agreement: completeOnAgreement,
  by_outcome: Object.fromEntries(
    outcomes.map((outcome) => [outcome, [...verdicts.values()].filter((verdict) => verdict.outcome === outcome).length]),
  ),
};
fs.writeFileSync(path.join(outDir, "summary.json"), `${JSON.stringify(summary, null, 2)}\n`);
console.log(JSON.stringify(summary, null, 2));
