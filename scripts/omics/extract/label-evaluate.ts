/** The label stage measured against the store's own answers.
 *
 * The stage decides one field: which benchmark or task a table reports. 52,278 stored results
 * already carry that field, assigned by the frozen Python scripts, so the store is its own
 * held-out set. This command builds that set, measures every bound the pipeline imposes before
 * a question is asked, and writes the files `maintenance/reports/label-evaluation-<date>.*`.
 *
 * It asks nothing. No key is read, no transport is opened and no answer is scored: a run with
 * an empty recording is used to count exactly how many questions a live run would ask, and an
 * oracle pass feeds the known-right record id through the real checks to see whether a right
 * answer could get through them. Neither invents an answer, and no heuristic picks an id here,
 * because its rates would read as the stage's and would not be.
 *
 * Everything is read-only over `data/`.
 *
 * Usage:
 *   SPAN_DETAIL=<tsv> npm run spans -- measure --out <scratch>   # produces the span dump
 *   npm run extract -- label-evaluate --spans <tsv> [--out maintenance/reports] [--date <d>]
 */
import fs from "node:fs";
import path from "node:path";
import { buildDecider, extractSource, assessmentKinds, systemKinds } from "../../../shared/omics/extract/index";
import {
  buildShortlistIndex, shortlistFor, tablesOf, contentWords, SHORTLIST_MAX, labelTables,
  loadPrompt, recordedTransport, renderQuestion, checkAnswer, collapse, answerJsonSchema,
  type LabelTable,
} from "../../../shared/omics/extract/label/index";
import { gridForLayer, layerText, layersForSource } from "../../../shared/omics/layers/index";
import { indexLayer, type LayerIndex } from "../../../shared/omics/spans/offsets";
import { resolveQuote } from "../../../shared/omics/spans/prose";
import { readKind } from "../records";

/** How alike two record names must be before one counts as a near-twin of the other on a
 * shortlist. Jaccard over content words, so `Feng Yeast H3K4me1 sequence classification` and
 * the H3K4me2 protocol beside it are twins and an unrelated protocol is not. Reported rather
 * than enforced: nothing in `check.ts` reads this yet. */
export const TWIN_SIMILARITY = 0.6;

/** The relations that make one record a child of another. These are the two the store writes:
 * `part_of` 1,472 times and `parent` 36, over protocols and tasks. `evaluates_task` is not one
 * of them and adding it changes nothing measured, which is why it is named here and left out. */
export const PARENT_RELATIONS = ["parent", "part_of"];

interface Stored { id: string; sources: string[]; ok: boolean; layer: string; start: number; end: number; kind: string; class: string }

/** The span dump `npm run spans -- measure` writes when `SPAN_DETAIL` is set. */
function readSpans(file: string): Stored[] {
  const lines = fs.readFileSync(file, "utf8").split("\n").filter((line) => line.trim());
  const header = lines[0].split("\t");
  const at = (name: string) => {
    const index = header.indexOf(name);
    if (index < 0) throw new Error(`${file} has no ${name} column. Regenerate it with SPAN_DETAIL set on a current build.`);
    return index;
  };
  const columns = { id: at("id"), cls: at("class"), outcome: at("outcome"), kind: at("reason_or_kind"), layer: at("layer_sha256"), sources: at("source_ids"), start: at("start"), end: at("end") };
  const out: Stored[] = [];
  for (const line of lines.slice(1)) {
    const cells = line.split("\t");
    if (cells[columns.outcome] !== "resolved") continue;
    out.push({
      id: cells[columns.id], sources: cells[columns.sources].split("|").filter(Boolean),
      ok: true, layer: cells[columns.layer], start: Number(cells[columns.start]), end: Number(cells[columns.end]),
      kind: cells[columns.kind], class: cells[columns.cls],
    });
  }
  return out;
}

const stat = (values: number[]) => {
  const sorted = [...values].sort((x, y) => x - y);
  const at = (q: number) => sorted[Math.min(sorted.length - 1, Math.floor(q * sorted.length))] ?? 0;
  return { n: sorted.length, min: sorted[0] ?? 0, p50: at(0.5), p90: at(0.9), max: sorted[sorted.length - 1] ?? 0,
    mean: Number((sorted.reduce((t, v) => t + v, 0) / (sorted.length || 1)).toFixed(1)) };
};

const jaccard = (a: string[], b: string[]): number => {
  const A = new Set(a), B = new Set(b);
  const union = new Set([...A, ...B]).size;
  return union === 0 ? 0 : [...A].filter((w) => B.has(w)).length / union;
};

export async function labelEvaluate(root: string, options: { spans: string; out: string; date: string }): Promise<void> {
  const stored = readSpans(options.spans);
  fs.mkdirSync(options.out, { recursive: true });

  // Ground truth: a stored result reaches an assessment through its evaluation. Nothing else in
  // the store says what a stored result is a result of.
  const evaluations = new Map<string, string>();
  for (const evaluation of readKind("evaluation") as { id: string; links?: { relation: string; target_id: string }[] }[]) {
    const link = (evaluation.links ?? []).find((l) => l.relation === "assessment");
    if (link) evaluations.set(evaluation.id, link.target_id);
  }
  const assessmentOf = new Map<string, string>();
  for (const result of readKind("result") as { id: string; links?: { relation: string; target_id: string }[] }[]) {
    const link = (result.links ?? []).find((l) => l.relation === "evaluation");
    const assessment = link ? evaluations.get(link.target_id) : undefined;
    if (assessment) assessmentOf.set(result.id, assessment);
  }

  const kinds = new Set<string>([...systemKinds, ...assessmentKinds]);
  const named = [...kinds].sort().flatMap((kind) => readKind(kind)) as {
    id: string; kind: string; name?: string; source_ids?: string[]; links?: { relation: string; target_id: string }[];
  }[];
  const sourceRecords = readKind("source") as { id: string; name?: string; attributes?: Record<string, unknown>; links?: { relation: string; target_id: string }[] }[];
  const titleOf = new Map(sourceRecords.map((s) => [s.id, s.name ?? String((s.attributes ?? {}).title ?? s.id)]));
  const kindOf = new Map(named.map((r) => [r.id, r.kind]));
  const nameOf = new Map(named.map((r) => [r.id, r.name ?? ""]));
  const parentOf = new Map(named.map((r) => [r.id, (r.links ?? []).filter((l) => PARENT_RELATIONS.includes(l.relation)).map((l) => l.target_id)]));

  const decider = buildDecider(named);
  const full = buildShortlistIndex(named, sourceRecords);
  // The lexical rule on its own: the store's citations removed, which is what a source nobody
  // has extracted yet looks like.
  const lexical = buildShortlistIndex(named.map((record) => ({ ...record, source_ids: [] })), []);

  const bySource = new Map<string, Stored[]>();
  for (const item of stored) for (const source of item.sources) bySource.set(source, [...(bySource.get(source) ?? []), item]);

  // The population: every source holding resolved results whose layer geometry the extractor
  // reads. No further filter, so capped, multi-assessment and ambiguous-caption tables stay in.
  const normaliserOf = new Map<string, string>();
  const run = [...bySource.keys()].filter((source) => {
    let keep = false;
    for (const record of layersForSource(source)) {
      if (record.sanity === "fail") continue;
      normaliserOf.set(record.layer_sha256, record.normaliser);
      if (gridForLayer(record.layer_sha256) || record.normaliser === "ooxml-sheet-tsv@1") keep = true;
    }
    return keep;
  }).sort();
  const inRun = new Set(run);

  const indexes = new Map<string, LayerIndex | null>();
  const layerIndex = (source: string, sha: string): LayerIndex | null => {
    if (!indexes.has(sha)) {
      const record = layersForSource(source).find((l) => l.layer_sha256 === sha);
      indexes.set(sha, record ? indexLayer(layerText(record), record.layer_sha256, record.normaliser) : null);
    }
    return indexes.get(sha) ?? null;
  };

  interface Row { source: string; table: LabelTable; truth: string[]; results: Stored[]; fullIds: string[]; fullHit: boolean; lexIds: string[]; lexHit: boolean }
  const rows: Row[] = [];
  const allTables: { source: string; table: LabelTable }[] = [];
  const extentsOf = new Map<string, { layer: string; start: number; end: number }[]>();
  let inTable = 0;
  const resultsByClassInside: Record<string, number> = {};

  for (const source of run) {
    let candidates;
    try { ({ candidates } = extractSource(source, decider)); }
    catch (error) { console.error(`${source}: ${(error as Error).message}`); continue; }
    const tables = tablesOf(candidates);
    extentsOf.set(source, tables.map((t) => ({ layer: t.layer_sha256, start: t.extent.start, end: t.extent.end })));
    const resolved = bySource.get(source) ?? [];
    for (const table of tables) {
      allTables.push({ source, table });
      const inside = resolved.filter((i) => i.layer === table.layer_sha256 && i.start >= table.extent.start && i.end <= table.extent.end);
      inTable += inside.length;
      for (const item of inside) resultsByClassInside[item.class] = (resultsByClassInside[item.class] ?? 0) + 1;
      const truth = [...new Set(inside.map((i) => assessmentOf.get(i.id)).filter((x): x is string => !!x))].sort();
      if (truth.length === 0) continue;
      const a = shortlistFor(full, table);
      const b = shortlistFor(lexical, table);
      rows.push({ source, table, truth, results: inside,
        fullIds: a.ids, fullHit: truth.some((id) => a.ids.includes(id)),
        lexIds: b.ids, lexHit: truth.some((id) => b.ids.includes(id)) });
    }
  }

  // Where every resolved result went, so the held-out set states what it left behind.
  let outsideRunSources = 0, sameLayerOutside = 0, noTableInLayer = 0;
  const outsideByKind: Record<string, number> = {};
  for (const item of stored) {
    const sources = item.sources.filter((s) => inRun.has(s));
    if (sources.length === 0) { outsideRunSources += 1; outsideByKind[item.kind] = (outsideByKind[item.kind] ?? 0) + 1; continue; }
    const list = sources.flatMap((s) => extentsOf.get(s) ?? []);
    if (list.some((e) => e.layer === item.layer && item.start >= e.start && item.end <= e.end)) continue;
    if (list.some((e) => e.layer === item.layer)) sameLayerOutside += 1; else noTableInLayer += 1;
  }

  // ------------------------------------------------------------------- the held-out set, frozen
  const prefix = path.join(options.out, `label-evaluation-${options.date}`);
  const heldout = [[
    "source", "table_id", "layer_sha256", "normaliser", "anchor_from", "anchor_chars", "caption",
    "cells", "results", "truth_count", "truth_ids", "truth_kinds", "decided",
    "shortlist_full", "shortlist_full_hit", "shortlist_lexical", "shortlist_lexical_hit",
    "caption_resolves", "scored_answer",
  ].join("\t")];
  const truthRecords = new Set<string>();
  const truthKinds: Record<string, number> = {};
  const normalisers: Record<string, number> = {};
  const captionVerdict: Record<string, number> = {};
  for (const row of rows) {
    const index = layerIndex(row.source, row.table.layer_sha256);
    const out = row.table.anchor_text.trim().length >= 4 && index ? resolveQuote(index, row.table.anchor_text) : null;
    const verdict = out === null ? "not_attempted" : out.ok ? "ok" : out.reason;
    captionVerdict[verdict] = (captionVerdict[verdict] ?? 0) + 1;
    const normaliser = normaliserOf.get(row.table.layer_sha256) ?? "unknown";
    normalisers[normaliser] = (normalisers[normaliser] ?? 0) + 1;
    for (const id of row.truth) { truthRecords.add(id); truthKinds[kindOf.get(id) ?? "unknown"] = (truthKinds[kindOf.get(id) ?? "unknown"] ?? 0) + 1; }
    heldout.push([
      row.source, row.table.table_id, row.table.layer_sha256.slice(0, 16), normaliser,
      row.table.anchor_text_from, String(row.table.anchor_text.length), JSON.stringify(row.table.anchor_text.slice(0, 120)),
      String(row.table.candidate_ids.length), String(row.results.length),
      String(row.truth.length), row.truth.join("|"),
      [...new Set(row.truth.map((id) => kindOf.get(id) ?? "unknown"))].sort().join("|"),
      String(row.table.decided.length),
      String(row.fullIds.length), row.fullHit ? "1" : "0",
      String(row.lexIds.length), row.lexHit ? "1" : "0",
      verdict,
      // The scored answer, written before any answer exists: one id where the store maps the
      // table to one assessment, `none` where it maps it to several.
      row.truth.length === 1 ? row.truth[0] : "none",
    ].join("\t"));
  }
  fs.writeFileSync(`${prefix}-heldout.tsv`, `${heldout.join("\n")}\n`);

  // ------------------------------------------------- the dry run: what a live run would ask for
  const prompt = loadPrompt(root);
  const dry = await labelTables({
    tables: allTables.map((t) => t.table),
    shortlistIndex: full,
    sourceTitle: (id) => titleOf.get(id) ?? id,
    layerIndex: (sha) => {
      const owner = allTables.find((t) => t.table.layer_sha256 === sha);
      return owner ? layerIndex(owner.source, sha) : null;
    },
    transport: recordedTransport({}),
    prompt,
  });
  const questionChars: number[] = [];
  for (const { source, table } of allTables) {
    const shortlist = shortlistFor(full, table);
    if (table.decided.length > 0 || table.anchor_text.trim().length < 4 || shortlist.ids.length === 0) continue;
    if (!layerIndex(source, table.layer_sha256)) continue;
    questionChars.push(renderQuestion({ table, shortlist, sourceTitle: titleOf.get(source) ?? source }).length);
  }

  // ----------------------------------------------------------------------------- the oracle pass
  // The known-right id through the real checks, with the best quote the caption can supply. This
  // measures the checks and the layer. It chooses no id.
  const oracle = [["source", "table_id", "truth", "quote_kind", "medium", "high", "refusal"].join("\t")];
  const counts = { single: 0, medium_ok: 0, high_ok: 0, name_in_caption: 0 };
  const oracleRefusals: Record<string, number> = {};
  for (const row of rows) {
    if (row.truth.length !== 1) continue;
    counts.single += 1;
    const truth = row.truth[0];
    const index = layerIndex(row.source, row.table.layer_sha256);
    const shortlist = shortlistFor(full, row.table);
    const names = full.namesOf.get(truth) ?? [];
    const printed = collapse(nameOf.get(truth) ?? "");
    const caption = collapse(row.table.anchor_text);
    const at = printed === "" ? -1 : caption.toLowerCase().indexOf(printed.toLowerCase());
    if (at >= 0) counts.name_in_caption += 1;
    const quotes = at >= 0
      ? [{ kind: "record_name", quote: caption.slice(at, at + printed.length) }, { kind: "whole_caption", quote: row.table.anchor_text }]
      : [{ kind: "whole_caption", quote: row.table.anchor_text }];
    let best: { kind: string; medium: boolean; high: boolean; refusal: string } | null = null;
    for (const option of quotes) {
      if (!index) { best = { kind: option.kind, medium: false, high: false, refusal: "no_layer" }; break; }
      const ask = (confidence: "medium" | "high") => checkAnswer({
        table: row.table, shortlist, index, names,
        answer: { record_id: truth, quote: option.quote, confidence, reason: "oracle" },
        record: { id: truth, kind: kindOf.get(truth) ?? "unknown" },
      });
      const m = ask("medium"), h = ask("high");
      const entry = { kind: option.kind, medium: m.outcome === "labelled", high: h.outcome === "labelled",
        refusal: m.outcome === "refused" ? m.reason : h.outcome === "refused" ? h.reason : "" };
      if (!best || (entry.high && !best.high) || (entry.medium && !best.medium)) best = entry;
      if (entry.high) break;
    }
    if (!best) continue;
    if (best.medium) counts.medium_ok += 1;
    if (best.high) counts.high_ok += 1;
    if (!best.high) oracleRefusals[best.refusal || "none"] = (oracleRefusals[best.refusal || "none"] ?? 0) + 1;
    oracle.push([row.source, row.table.table_id, truth, best.kind, best.medium ? "1" : "0", best.high ? "1" : "0", best.refusal].join("\t"));
  }
  fs.writeFileSync(`${prefix}-oracle.tsv`, `${oracle.join("\n")}\n`);

  // ------------------------------------- two refusals that do not exist yet, measured as proposals
  // near_twin:  another shortlist entry whose name is a near-twin of the chosen one.
  // parent_of_two: the chosen record has two or more of its children on the same shortlist, which
  // is what a table reporting a suite's tasks looks like. Both are reported on the ground-truth
  // tables so their cost in coverage and their catch in wrong labels are measured together.
  const confusable = [["source", "table_id", "truth_count", "scored_answer", "shortlist", "near_twins", "parent_of_two_fires", "results", "caption"].join("\t")];
  const proposal = { single_tables: 0, single_results: 0, single_with_twin: 0, results_with_twin: 0,
    multi_tables: 0, multi_results: 0, multi_parent_on_shortlist: 0, parent_rule_fires_on_multi: 0,
    parent_rule_fires_on_single: 0, parent_rule_results_lost: 0 };
  for (const row of rows) {
    const single = row.truth.length === 1;
    const sl = shortlistFor(full, row.table);
    const target = single ? contentWords(nameOf.get(row.truth[0]) ?? "") : [];
    const twins = single ? sl.entries.filter((e) => e.id !== row.truth[0] && jaccard(target, contentWords(e.name)) >= TWIN_SIMILARITY).length : 0;
    // Would the parent rule refuse the answer the scoring rule calls correct?
    const children = (id: string) => sl.ids.filter((other) => other !== id && (parentOf.get(other) ?? []).includes(id)).length;
    const fires = single ? children(row.truth[0]) >= 2 : sl.ids.some((id) => children(id) >= 2);
    if (single) {
      proposal.single_tables += 1; proposal.single_results += row.results.length;
      if (twins > 0) { proposal.single_with_twin += 1; proposal.results_with_twin += row.results.length; }
      if (fires) { proposal.parent_rule_fires_on_single += 1; proposal.parent_rule_results_lost += row.results.length; }
    } else {
      proposal.multi_tables += 1; proposal.multi_results += row.results.length;
      const parents = row.truth.map((id) => new Set(parentOf.get(id) ?? []));
      const common = [...(parents[0] ?? [])].filter((p) => parents.every((set) => set.has(p)));
      if (common.some((p) => sl.ids.includes(p))) proposal.multi_parent_on_shortlist += 1;
      if (fires) proposal.parent_rule_fires_on_multi += 1;
    }
    confusable.push([row.source, row.table.table_id, String(row.truth.length), single ? row.truth[0] : "none",
      String(sl.ids.length), String(twins), fires ? "1" : "0", String(row.results.length),
      JSON.stringify(row.table.anchor_text.slice(0, 80))].join("\t"));
  }
  fs.writeFileSync(`${prefix}-confusable.tsv`, `${confusable.join("\n")}\n`);

  const single = rows.filter((r) => r.truth.length === 1);
  const summary = {
    generated: options.date,
    spans: path.basename(options.spans),
    store: { resolved_to_a_span: stored.length, resolved_by_class: Object.fromEntries(Object.entries(stored.reduce((acc: Record<string, number>, s) => ({ ...acc, [s.class]: (acc[s.class] ?? 0) + 1 }), {})).sort()) },
    population: { sources: run.length, tables: allTables.length, results_inside_a_table_extent: inTable,
      results_by_class_inside: resultsByClassInside, outside_run_sources: outsideRunSources,
      outside_by_kind: outsideByKind, same_layer_outside_every_extent: sameLayerOutside, no_table_in_that_layer: noTableInLayer },
    heldout: { tables: rows.length, sources: new Set(rows.map((r) => r.source)).size,
      results: rows.reduce((t, r) => t + r.results.length, 0),
      single_assessment_tables: single.length, multi_assessment_tables: rows.length - single.length,
      results_in_single_tables: single.reduce((t, r) => t + r.results.length, 0),
      distinct_truth_records: truthRecords.size, truth_record_mentions_by_kind: truthKinds,
      layer_normalisers: normalisers, whole_caption_resolves: captionVerdict,
      cells_per_table: stat(rows.map((r) => r.table.candidate_ids.length)),
      results_per_table: stat(rows.map((r) => r.results.length)),
      results_per_single_table: stat(single.map((r) => r.results.length)) },
    shortlist: { cap: SHORTLIST_MAX, considered: full.considered,
      both_rules: { hit: rows.filter((r) => r.fullHit).length, hit_single: single.filter((r) => r.fullHit).length,
        size: stat(rows.map((r) => r.fullIds.length)), at_cap: rows.filter((r) => r.fullIds.length === SHORTLIST_MAX).length,
        miss_at_cap: rows.filter((r) => !r.fullHit && r.fullIds.length === SHORTLIST_MAX).length },
      lexical_only: { hit: rows.filter((r) => r.lexHit).length, hit_single: single.filter((r) => r.lexHit).length,
        size: stat(rows.map((r) => r.lexIds.length)), empty: rows.filter((r) => r.lexIds.length === 0).length } },
    dry_run: { tables: dry.receipt.tables, questions_a_live_run_would_ask: dry.receipt.refusals_by_reason.transport_failed ?? 0,
      refused_before_asking: Object.fromEntries(Object.entries(dry.receipt.refusals_by_reason).filter(([k]) => k !== "transport_failed")),
      question_characters: stat(questionChars), question_characters_total: questionChars.reduce((t, v) => t + v, 0),
      prompt: dry.receipt.prompt, prompt_bytes: Buffer.byteLength(prompt.text), model: dry.receipt.model,
      effort: dry.receipt.effort, max_tokens: dry.receipt.max_tokens,
      reply_fields: Object.keys((answerJsonSchema as { properties: Record<string, unknown> }).properties) },
    oracle: { ...counts, refused_by_reason: oracleRefusals },
    proposed_refusals: { twin_similarity: TWIN_SIMILARITY, ...proposal },
  };
  fs.writeFileSync(`${prefix}.json`, `${JSON.stringify(summary, null, 2)}\n`);
  console.log(JSON.stringify(summary, null, 2));
}
