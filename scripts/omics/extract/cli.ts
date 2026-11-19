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
 * Two more commands live here and extract nothing, both writing a dated report under
 * `maintenance/reports/` and neither touching the store:
 *
 *   npm run extract -- label-evaluate   every bound the pipeline imposes before a question is
 *                                       asked. It asks nothing and reads no key.
 *   npm run extract -- label-measure    the stage asked for real against the frozen held-out set
 *                                       label-evaluate wrote, capped by --max-questions. This is
 *                                       the one command in the repository that spends money, and
 *                                       --plan reports what it would ask without asking.
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
import {
  DEFAULT_EFFORT,
  DEFAULT_MODEL,
  buildShortlistIndex,
  labelTables,
  loadPrompt,
  readCache,
  recordedTransport,
  liveTransport,
  tablesOf,
  writeCache,
  type LabelTransport,
} from "../../../shared/omics/extract/label/index";
import { layerText, layersForSource } from "../../../shared/omics/layers/index";
import { indexLayer, type LayerIndex } from "../../../shared/omics/spans/offsets";
import { readKind } from "../records";

const usage = [
  "Usage: npm run extract -- <source id> [--batch <name>] [--date <YYYY-MM-DD>] [--out <dir>] [--json]",
  "                        [--label] [--model <id>] [--effort <level>] [--replies <file>]",
  "       npm run extract -- label-measure --heldout <tsv> --max-questions <n> [--plan] [--out <dir>]",
  "                        [--replies <file>] [--model <id>] [--effort <level>] [--date <YYYY-MM-DD>]",
].join("\n");

interface Options {
  sourceId: string;
  batch: string | null;
  date: string;
  out: string;
  json: boolean;
  /** Run the one stage that asks a language model which record each table is about. Off by
   * default: the deterministic pass is the baseline and is measured without it. */
  label: boolean;
  model: string;
  effort: string;
  /** A file of recorded replies, keyed by request digest. With one, the stage answers from the
   * recording and opens no socket, which is how a reviewer reruns a labelled batch. */
  replies: string | null;
}

function parseArgs(argv: string[]): Options {
  let sourceId = "";
  let batch: string | null = null;
  let date = "";
  let out = "data/omics";
  let json = false;
  let label = false;
  let model = DEFAULT_MODEL;
  let effort = DEFAULT_EFFORT;
  let replies: string | null = null;
  for (let at = 0; at < argv.length; at += 1) {
    const arg = argv[at];
    if (arg === "--batch") batch = argv[++at] ?? "";
    else if (arg === "--date") date = argv[++at] ?? "";
    else if (arg === "--out") out = argv[++at] ?? out;
    else if (arg === "--json") json = true;
    else if (arg === "--label") label = true;
    else if (arg === "--model") model = argv[++at] ?? model;
    else if (arg === "--effort") effort = argv[++at] ?? effort;
    else if (arg === "--replies") replies = argv[++at] ?? null;
    else if (arg.startsWith("--")) throw new Error(`${usage}\nUnknown option ${arg}`);
    else if (sourceId === "") sourceId = arg;
    else throw new Error(`${usage}\nOne source at a time; got ${sourceId} and ${arg}`);
  }
  if (sourceId === "") throw new Error(usage);
  // The date is the receipt's and nothing else reads it. It is an argument rather than a clock
  // so that a rerun of the same extraction writes the same receipt.
  if (date === "") date = new Date().toISOString().slice(0, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) throw new Error(`${usage}\n--date takes YYYY-MM-DD; got ${date}`);
  if (replies !== null && !label) throw new Error(`${usage}\n--replies is for --label and does nothing without it`);
  return { sourceId, batch, date, out, json, label, model, effort, replies };
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

/**
 * The one stage that asks anything outside this repository, over the tables this run read.
 *
 * It writes its own files and touches neither `candidates.jsonl` nor the store. Every answer
 * is refused unless the record it names is on the shortlist and in the store, the words it
 * quotes are in the caption the question printed, and those words resolve to one span in the
 * source's own text layer. A refused answer leaves the table unlabelled with the reason on the
 * line.
 */
async function runLabelStage(input: {
  options: Options;
  extract: string;
  candidates: Candidate[];
  sourceTitle: string;
  named: { id: string; kind: string; name?: string; source_ids?: string[]; attributes?: Record<string, unknown> }[];
  sources: { id: string; links?: { relation: string; target_id: string }[] }[];
}): Promise<{ labelled: number; abstained: number; refused: number; asked: number }> {
  const { options, extract } = input;
  const tables = tablesOf(input.candidates);
  const assessments = input.named.filter((record) => (assessmentKinds as readonly string[]).includes(record.kind));
  const shortlistIndex = buildShortlistIndex(assessments, input.sources);
  const prompt = loadPrompt();

  const indexes = new Map<string, LayerIndex | null>();
  const layerIndex = (layerSha256: string): LayerIndex | null => {
    if (!indexes.has(layerSha256)) {
      const record = layersForSource(options.sourceId).find((layer) => layer.layer_sha256 === layerSha256);
      indexes.set(layerSha256, record ? indexLayer(layerText(record), record.layer_sha256, record.normaliser) : null);
    }
    return indexes.get(layerSha256) ?? null;
  };

  const transport: LabelTransport = options.replies
    ? recordedTransport(JSON.parse(fs.readFileSync(options.replies, "utf8")) as Record<string, string>)
    : liveTransport();

  const cacheFile = path.join(extract, "label-cache.json");
  const cache = readCache(cacheFile);
  const { outcomes, receipt } = await labelTables({
    tables,
    shortlistIndex,
    sourceTitle: () => input.sourceTitle,
    layerIndex,
    transport,
    prompt,
    cache,
    model: options.model,
    effort: options.effort,
  });
  writeCache(cacheFile, cache);

  // The receipt names this path, so it is taken from the receipt rather than written twice.
  const perTable = path.join(path.dirname(extract), receipt.per_table);
  fs.mkdirSync(path.dirname(perTable), { recursive: true });
  const lines = outcomes.map((outcome) => canonicalJson(outcome)).join("\n");
  fs.writeFileSync(perTable, outcomes.length ? `${lines}\n` : "");
  fs.writeFileSync(path.join(extract, "label-receipt.json"), `${JSON.stringify(receipt, null, 2)}\n`);

  if (!options.json) {
    console.log(`  label stage: ${receipt.labelled} labelled, ${receipt.abstained} could not tell, ${receipt.refused} refused, over ${receipt.tables} tables (${receipt.candidates_labelled} candidates labelled)`);
    console.log(`  shortlist: median ${receipt.shortlist.median} of ${receipt.shortlist.considered} records, ${receipt.shortlist.empty} tables with none`);
    for (const [reason, count] of Object.entries(receipt.refusals_by_reason).sort((a, b) => b[1] - a[1]))
      console.log(`  refused ${reason}: ${count}`);
  }
  return { labelled: receipt.labelled, abstained: receipt.abstained, refused: receipt.refused, asked: receipt.asked };
}

async function main(argv: string[]): Promise<void> {
  // The evaluation is a second command rather than a flag on the first: it reads the whole
  // store and writes a dated report, and it extracts nothing.
  if (argv[0] === "label-evaluate") {
    const rest = argv.slice(1);
    const value = (flag: string, fallback: string): string => {
      const at = rest.indexOf(flag);
      return at >= 0 ? (rest[at + 1] ?? fallback) : fallback;
    };
    const spans = value("--spans", "");
    if (!spans)
      throw new Error(
        "label-evaluate needs --spans <tsv>, the dump SPAN_DETAIL=<tsv> npm run spans -- measure writes.",
      );
    const { labelEvaluate } = await import("./label-evaluate");
    await labelEvaluate(".", {
      spans,
      out: value("--out", "maintenance/reports"),
      date: value("--date", new Date().toISOString().slice(0, 10)),
    });
    return;
  }

  // The measurement is a third command for the same reason: it reads the whole store, writes a
  // dated report and extracts nothing. It is the only command here that can spend money, and the
  // cap is a required argument rather than a default somebody can forget.
  if (argv[0] === "label-measure") {
    const rest = argv.slice(1);
    const value = (flag: string, fallback: string): string => {
      const at = rest.indexOf(flag);
      return at >= 0 ? (rest[at + 1] ?? fallback) : fallback;
    };
    const heldout = value("--heldout", "");
    if (!heldout)
      throw new Error("label-measure needs --heldout <tsv>, the frozen held-out set npm run extract -- label-evaluate writes.");
    const cap = Number(value("--max-questions", "0"));
    const planOnly = rest.includes("--plan");
    if (!planOnly && (!Number.isInteger(cap) || cap <= 0))
      throw new Error("label-measure needs --max-questions <n>, a positive whole number. It is the ceiling on what this run can spend.");
    // A recording answers without a socket, which is how a reviewer reruns a
    // measurement and how the pipeline is exercised offline. An empty one
    // answers nothing, so every question becomes a transport failure and the
    // report says so rather than inventing a rate.
    const replies = value("--replies", "");
    const { labelMeasure, recordedTransport: recorded } = await import("./label-measure");
    await labelMeasure(".", {
      heldout,
      transport: replies ? recorded(JSON.parse(fs.readFileSync(replies, "utf8")) as Record<string, string>) : undefined,
      out: value("--out", "maintenance/reports"),
      date: value("--date", new Date().toISOString().slice(0, 10)),
      maxQuestions: planOnly ? Number(value("--max-questions", String(Number.MAX_SAFE_INTEGER))) : cap,
      model: value("--model", DEFAULT_MODEL),
      effort: value("--effort", DEFAULT_EFFORT),
      planOnly,
    });
    return;
  }

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

  const label = options.label
    ? await runLabelStage({
        options,
        extract,
        candidates,
        sourceTitle: typeof source.name === "string" ? source.name : options.sourceId,
        named,
        sources,
      })
    : null;

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
          label === null
            ? "No model ran. Every field this pass could not decide is named in extract/questions.jsonl with the text it would be decided from."
            : "No value was read by anything but the deterministic pass. Every value, metric and span in extract/candidates.jsonl can be re-checked from the layer bytes alone. The one field decided by machine judgement is which benchmark or task each table reports, in extract/stages/label.jsonl, and extract/label-receipt.json states what that is worth.",
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

main(process.argv.slice(2)).catch((error: Error) => {
  console.error(error.message);
  process.exitCode = 1;
});
