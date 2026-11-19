/** `npm run extract -- <source id>`: read one archived source's layers and write a batch of
 * candidate results.
 *
 * The fifth of the five commands. Four exist:
 *
 *   npm run archive -- fetch      every source, resumable, a receipt each
 *   npm run archive -- publish    the publishable ones to release assets
 *   npm run layers -- build       deterministic text per source
 *   npm run extract -- <source>   read values out of that text
 *   npm run records -- add        write them to the store
 *
 * This writes files and never writes the store. ADR 0002 decision 6: candidates are files,
 * never records, because `publicRecords` blocks only `excluded` and `disputed` and a
 * candidate-ish status would be exported to the published bundle. A candidate that is not a
 * record cannot leak.
 *
 * The batch folder is `data/omics/<batch>/`, which is where every batch in this repository
 * lives, and the candidate files sit under `extract/` in it, which is the path ADR 0002
 * decision 6 names. `review.json` is the receipt `writeBatch` writes, with the review fields
 * left empty for a second worker, as the extraction skill requires.
 *
 * Nothing but the receipt reads a clock. `candidates.jsonl` and `coverage.json` are a function
 * of the archived bytes and the store, with keys sorted at every depth, so two runs over one
 * archive give byte-identical files and a diff means something changed.
 */
import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";
import { canonicalJson } from "../../../shared/archive/layers/grid/index";
import { buildDecider, extractSource, assessmentKinds, systemKinds } from "../../../shared/omics/extract/index";
import type { Candidate } from "../../../shared/omics/extract/index";
import { readKind } from "../records";

const usage = "Usage: npm run extract -- <source id> [--batch <name>] [--date <YYYY-MM-DD>] [--out <dir>] [--json]";

interface Options {
  sourceId: string;
  batch: string | null;
  date: string;
  out: string;
  json: boolean;
}

function parseArgs(argv: string[]): Options {
  let sourceId = "";
  let batch: string | null = null;
  let date = "";
  let out = "data/omics";
  let json = false;
  for (let at = 0; at < argv.length; at += 1) {
    const arg = argv[at];
    if (arg === "--batch") batch = argv[++at] ?? "";
    else if (arg === "--date") date = argv[++at] ?? "";
    else if (arg === "--out") out = argv[++at] ?? out;
    else if (arg === "--json") json = true;
    else if (arg.startsWith("--")) throw new Error(`${usage}\nUnknown option ${arg}`);
    else if (sourceId === "") sourceId = arg;
    else throw new Error(`${usage}\nOne source at a time; got ${sourceId} and ${arg}`);
  }
  if (sourceId === "") throw new Error(usage);
  // The date is the receipt's and nothing else reads it. It is an argument rather than a clock
  // so that a rerun of the same extraction writes the same receipt.
  if (date === "") date = new Date().toISOString().slice(0, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) throw new Error(`${usage}\n--date takes YYYY-MM-DD; got ${date}`);
  return { sourceId, batch, date, out, json };
}

/** One line per distinct question, with the candidates that ask it.
 *
 * The questions file is the handover to whatever decides these later, a reviewer or a model
 * stage. Aggregating by the words the document prints rather than listing one line per
 * candidate is what makes it readable: a table of forty rows under one unrecognised heading is
 * one question, asked forty times. */
function questionsOf(candidates: Candidate[]): string[] {
  const groups = new Map<string, { field: string; reason: string; evidence: string; decide: string; candidates: string[] }>();
  for (const candidate of candidates)
    for (const question of candidate.undecided) {
      const key = `${question.field}\u0000${question.reason}\u0000${question.evidence}`;
      const held = groups.get(key);
      if (held) held.candidates.push(candidate.candidate_id);
      else groups.set(key, { ...question, candidates: [candidate.candidate_id] });
    }
  return [...groups.values()]
    .sort((a, b) => b.candidates.length - a.candidates.length || (a.field < b.field ? -1 : a.field > b.field ? 1 : 0))
    .map((group) => canonicalJson({ ...group, asked: group.candidates.length, candidates: group.candidates.slice(0, 50) }));
}

function main(argv: string[]): void {
  const options = parseArgs(argv);
  const sources = readKind("source");
  const source = sources.find((record) => record.id === options.sourceId);
  if (!source) throw new Error(`No source record is called ${options.sourceId}`);

  const kinds = new Set<string>([...systemKinds, ...assessmentKinds]);
  const named = [...kinds].sort().flatMap((kind) => readKind(kind));
  const { candidates, tally } = extractSource(options.sourceId, buildDecider(named));

  const batch = options.batch ?? `extract-${options.sourceId}-${options.date}`;
  const folder = path.join(options.out, batch);
  const extract = path.join(folder, "extract");
  fs.mkdirSync(extract, { recursive: true });

  const candidateFile = path.join(extract, "candidates.jsonl");
  const body = candidates.map((candidate) => canonicalJson(candidate)).join("\n");
  fs.writeFileSync(candidateFile, candidates.length ? `${body}\n` : "");
  fs.writeFileSync(path.join(extract, "coverage.json"), `${canonicalJson(tally)}\n`);
  const questions = questionsOf(candidates);
  fs.writeFileSync(path.join(extract, "questions.jsonl"), questions.length ? `${questions.join("\n")}\n` : "");

  // The records file a reviewer promotes into. It is empty, and the reason is on the receipt
  // rather than left for a reader to work out: a result record needs a description, an
  // evaluation and a dataset, and none of the three is in the document as a value to be read.
  // Promoting a candidate is the next command, and it is not this one.
  const records = path.join(folder, "batch.jsonl");
  if (!fs.existsSync(records)) fs.writeFileSync(records, "");

  const receipt = path.join(folder, "review.json");
  const held = fs.existsSync(receipt) ? (JSON.parse(fs.readFileSync(receipt, "utf8")) as Record<string, unknown>) : {};
  const attributes = (source.attributes ?? {}) as Record<string, unknown>;
  fs.writeFileSync(
    receipt,
    `${JSON.stringify(
      {
        schema_version: "1.0",
        method: null,
        review_methods: [],
        reviewer: null,
        reviewed_at: null,
        scope: null,
        limitations: [
          "Candidates only. batch.jsonl is empty: a result record needs a description, an evaluation and a dataset record, and none of those is a value printed in the document.",
          "No model ran. Every field this pass could not decide is named in extract/questions.jsonl with the text it would be decided from.",
        ],
        errors: [],
        ...held,
        extraction: {
          batch,
          source: options.sourceId,
          url: attributes.url ?? null,
          artifact_sha256: attributes.artifact_sha256 ?? null,
          candidates: candidates.length,
          complete: tally.complete,
          needs_completion: tally.needs_completion,
          candidates_sha256: createHash("sha256").update(fs.readFileSync(candidateFile)).digest("hex"),
          method: "Deterministic table and sheet read over the registered text layers; no model, no network.",
          extracted_by: "npm run extract",
          extracted_at: options.date,
        },
      },
      null,
      2,
    )}\n`,
  );

  if (options.json) {
    console.log(canonicalJson(tally));
    return;
  }
  const classes = [...new Set(tally.layers.map((layer) => layer.normaliser))].sort().join(", ") || "none";
  const skipped = [...new Set(tally.skipped.map((layer) => `${layer.normaliser}:${layer.reason}`))].sort().join(", ") || "none";
  console.log(`${candidateFile}: ${candidates.length} candidates, ${tally.complete} complete, ${tally.needs_completion} needing completion`);
  console.log(`  layers read: ${classes}`);
  console.log(`  layers skipped: ${skipped}`);
  for (const [field, count] of Object.entries(tally.undecided_by_field).sort((a, b) => b[1] - a[1]))
    console.log(`  undecided ${field}: ${count}`);
}

try {
  main(process.argv.slice(2));
} catch (error) {
  console.error((error as Error).message);
  process.exitCode = 1;
}
