/** Span resolution over the whole store, ADR 0002 step 5.
 *
 * Usage: npm run spans -- measure [--out <dir>]   resolve every stored locator and report
 *        npm run spans -- control                 agree or disagree with the 14 value-check files
 *        npm run spans -- show <result id>        one locator, its layers and its outcome
 *
 * Two different numbers come out of this and the difference is the point. Parse coverage is what
 * `npm run locator -- coverage` reports: the share of stored locator strings the grammar fully
 * addresses, 40,464 of 52,278, 77.4%. Resolution coverage is the share that reach a span in a
 * layer the archive holds. A locator can parse perfectly and resolve nothing, because the bytes
 * are not held, because the layer prints no columns, or because the caption it names is not in
 * the text. Only the second number says whether a stored value can be re-checked without a
 * reader, so both are reported and the gap between them is itemised by reason.
 *
 * Everything here is offline, reads the store read-only and calls no model.
 */
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { hasObject } from "../../archive/objects";
import { latestBySource, readReceipts } from "../../archive/receipts";
import {
  coverageOf as layerCoverage,
  isGrid,
  layerText,
  readRegistry,
  readUnsupported,
  type LayerRecord,
  type ReceiptFact,
} from "../../../shared/omics/layers/index";
import {
  classifyLocator,
  coverageOf as parseCoverage,
  parseLocator,
  type LocatorClass,
  type LocatorCoverage,
  type ParsedLocator,
} from "../../../shared/omics/locator";
import {
  indexLayer,
  refusalReasons,
  resolveLocator,
  type RefusalReason,
  type Resolution,
  type SpanKind,
} from "../../../shared/omics/spans/index";

const RESULTS = "data/evidence/results";
const SOURCES = "data/entities/sources.jsonl";
const REPORTS = "maintenance/reports";
/** Layers tried per locator, best first. Beyond this a locator is refused on what it has. */
const MAX_LAYERS = 4;

interface StoredResult {
  id: string;
  source_ids: string[];
  locator: string;
  printed_value: string;
}

interface Candidate {
  layer_sha256: string;
  object_sha256: string;
  normaliser: string;
}

interface Work {
  result: StoredResult;
  parsed: ParsedLocator;
  class: LocatorClass;
  parse_bucket: LocatorCoverage;
  candidates: Candidate[];
  tried: number;
  resolved: Extract<Resolution, { ok: true }> | null;
  refusal: Extract<Resolution, { ok: false }> | null;
  /** Whether the span's text prints the value the record stores. Null when unresolved. */
  value_present: boolean | null;
  value_partial: boolean | null;
}

function readResults(root: string): StoredResult[] {
  const directory = path.join(root, RESULTS);
  const out: StoredResult[] = [];
  for (const file of fs.readdirSync(directory).filter((name) => name.endsWith(".jsonl")).sort()) {
    for (const line of fs.readFileSync(path.join(directory, file), "utf8").split("\n")) {
      if (!line.trim()) continue;
      const record = JSON.parse(line) as { id: string; source_ids?: string[]; attributes?: Record<string, unknown> };
      const attributes = record.attributes ?? {};
      out.push({
        id: record.id,
        source_ids: record.source_ids ?? [],
        locator: typeof attributes.source_locator === "string" ? attributes.source_locator : "",
        printed_value: typeof attributes.printed_value === "string" ? attributes.printed_value : "",
      });
    }
  }
  return out;
}

const sourceIds = (root: string): string[] =>
  fs
    .readFileSync(path.join(root, SOURCES), "utf8")
    .split("\n")
    .filter((line) => line.trim())
    .map((line) => (JSON.parse(line) as { id: string }).id);

function receiptFacts(root: string): Map<string, ReceiptFact> {
  const facts = new Map<string, ReceiptFact>();
  for (const [source, receipt] of latestBySource(readReceipts(root)))
    facts.set(source, {
      source_id: source,
      outcome: receipt.outcome,
      sha256: receipt.sha256 ?? null,
      reason: receipt.reason ?? null,
      source_class: receipt.source_class,
    });
  return facts;
}

/** A locator may say which rendering it was read from. Honour it: a locator that says PDF is
 * about the PDF, and resolving it against the publisher's HTML would be a different document. */
function preferredNormaliser(parsed: ParsedLocator): string | null {
  for (const qualifier of parsed.qualifiers) {
    if (qualifier.kind !== "layer") continue;
    const text = qualifier.text.toLowerCase();
    if (text.includes("pdf")) return "pdf-text-layer@1";
    if (text.includes("xml") || text.includes("jats")) return "europepmc-fulltext-xml@1";
    if (text.includes("html")) return "html-text@1";
    if (text.includes("csv") || text.includes("tsv") || text.includes("json")) return "text-utf8@1";
  }
  return null;
}

/** The refusal that got furthest. `refusalReasons` is ordered from the substrate outwards, so a
 * later reason is a resolver that read more of the layer before it stopped. */
const progress = (reason: RefusalReason): number => refusalReasons.indexOf(reason);

function keep(work: Work, refusal: Extract<Resolution, { ok: false }>): void {
  if (work.refusal === null || progress(refusal.reason) > progress(work.refusal.reason)) work.refusal = refusal;
}

/** Does the span print the value the record stores? Never consulted by a resolver: this is the
 * measurement's own check on the resolvers, and using it to choose a cell would make the number
 * meaningless. */
function valuePresence(exact: string, printed: string): { present: boolean; partial: boolean } {
  if (!printed) return { present: false, partial: false };
  const flatten = (text: string): string =>
    text
      // Unicode minus, en dash and em dash, which a printed value uses and a layer may not.
      .replace(/[\u2212\u2013\u2014]/g, "-")
      .replace(/\u00b1/g, "+/-")
      .replace(/\s+/g, "")
      .toLowerCase();
  const span = flatten(exact);
  const value = flatten(printed);
  if (span.includes(value)) return { present: true, partial: false };
  // The span is part of the value: a layer that prints "0.662" and "(+/- 0.044)" as two fields
  // against a record that stores both. The cell is the right cell and the record keeps more of
  // the line than the cell holds, which is a different finding from a wrong cell.
  if (span.length > 0 && /[0-9]/.test(span) && value.includes(span)) return { present: false, partial: true };
  return { present: false, partial: false };
}

interface MeasureOptions {
  root: string;
  limit?: number;
  log?: (line: string) => void;
}

export interface MeasureReport {
  locators: number;
  resolved: number;
  value_present: number;
  value_partial: number;
  by_reason: Map<RefusalReason, number>;
  by_kind: Map<SpanKind, number>;
  by_class: Map<LocatorClass, { locators: number; resolved: number; value_present: number }>;
  by_parse_bucket: Map<LocatorCoverage, { locators: number; resolved: number }>;
  /** Layers read, and how many of them hold a code point outside the basic multilingual plane. */
  layers_read: number;
  layers_astral: number;
  astral_points: number;
  /** Locators whose span came from the second or a later layer. */
  later_layer: number;
  work: Work[];
}

export function measure(options: MeasureOptions): MeasureReport {
  const { root } = options;
  const log = options.log ?? (() => {});
  const registry = readRegistry(root);
  const unsupported = readUnsupported(root);
  const coverage = layerCoverage(sourceIds(root), receiptFacts(root), registry, unsupported);
  const bucketOf = new Map(coverage.rows.map((row) => [row.source_id, row.bucket]));

  const bySource = new Map<string, LayerRecord[]>();
  const rank = { pass: 0, suspect: 1, fail: 2 } as const;
  for (const record of registry) {
    // A table grid is a registry row over the same bytes holding the geometry the text layer
    // flattens. Its bytes are JSON, not the source text, so a resolver run against them can only
    // refuse on the wrong substrate or, worse, place a span inside the geometry. It is also
    // competing for one of the MAX_LAYERS slots a real text layer needs.
    if (isGrid(record)) continue;
    for (const source of record.source_ids) {
      const held = bySource.get(source);
      if (held) held.push(record);
      else bySource.set(source, [record]);
    }
  }
  for (const held of bySource.values())
    held.sort((a, b) => rank[a.sanity] - rank[b.sanity] || b.metrics.characters - a.metrics.characters);

  const readable = new Map<string, boolean>();
  const isReadable = (object: string): boolean => {
    const known = readable.get(object);
    if (known !== undefined) return known;
    const found = hasObject(object, root);
    readable.set(object, found);
    return found;
  };

  let results = readResults(root);
  if (options.limit) results = results.slice(0, options.limit);

  const work: Work[] = [];
  for (const result of results) {
    const parsed = parseLocator(result.locator);
    const item: Work = {
      result,
      parsed,
      class: classifyLocator(result.locator),
      parse_bucket: parseCoverage(parsed.verdict),
      candidates: [],
      tried: 0,
      resolved: null,
      refusal: null,
      value_present: null,
      value_partial: null,
    };
    const seen = new Set<string>();
    let unusable = 0;
    let unreadable = 0;
    for (const source of result.source_ids)
      for (const record of bySource.get(source) ?? []) {
        if (seen.has(record.layer_sha256)) continue;
        seen.add(record.layer_sha256);
        if (record.sanity === "fail") {
          unusable += 1;
          continue;
        }
        if (!isReadable(record.object_sha256)) {
          unreadable += 1;
          continue;
        }
        item.candidates.push({ layer_sha256: record.layer_sha256, object_sha256: record.object_sha256, normaliser: record.normaliser });
      }
    const preferred = preferredNormaliser(parsed);
    if (preferred) {
      const first = item.candidates.filter((candidate) => candidate.normaliser === preferred);
      const rest = item.candidates.filter((candidate) => candidate.normaliser !== preferred);
      item.candidates = [...first, ...rest];
    }
    item.candidates = item.candidates.slice(0, MAX_LAYERS);
    if (item.candidates.length === 0) {
      const buckets = result.source_ids.map((source) => bucketOf.get(source));
      const reason: RefusalReason = unreadable > 0
        ? "layer_not_readable"
        : unusable > 0
          ? "layer_unusable"
          : buckets.includes("no_normaliser")
            ? "no_normaliser"
            : buckets.includes("not_the_artifact")
              ? "not_the_artifact"
              : "no_capture";
      item.refusal = { ok: false, reason, detail: `no readable layer for ${result.source_ids.join(" ")}` };
    }
    work.push(item);
  }

  let layersRead = 0;
  let layersAstral = 0;
  let astralPoints = 0;
  for (let attempt = 0; attempt < MAX_LAYERS; attempt += 1) {
    const byLayer = new Map<string, Work[]>();
    for (const item of work) {
      if (item.resolved || item.candidates.length <= attempt) continue;
      const key = item.candidates[attempt].layer_sha256;
      const held = byLayer.get(key);
      if (held) held.push(item);
      else byLayer.set(key, [item]);
    }
    if (byLayer.size === 0) break;
    log(`pass ${attempt + 1}: ${byLayer.size} layers, ${[...byLayer.values()].reduce((sum, items) => sum + items.length, 0)} locators`);
    let done = 0;
    for (const [layerSha, items] of byLayer) {
      const record = registry.find((row) => row.layer_sha256 === layerSha) as LayerRecord;
      let text: string;
      try {
        text = layerText(record, root);
      } catch (error) {
        for (const item of items) keep(item, { ok: false, reason: "layer_not_readable", detail: String(error), layer_sha256: layerSha });
        continue;
      }
      layersRead += 1;
      let astral = 0;
      for (const point of text) if ((point.codePointAt(0) ?? 0) > 0xffff) astral += 1;
      if (astral > 0) {
        layersAstral += 1;
        astralPoints += astral;
      }
      const index = indexLayer(text, layerSha, record.normaliser);
      for (const item of items) {
        item.tried += 1;
        const outcome = resolveLocator(item.parsed, index);
        if (outcome.ok) {
          item.resolved = outcome;
          const presence = valuePresence(outcome.span.exact, item.result.printed_value);
          item.value_present = presence.present;
          item.value_partial = presence.partial;
        } else keep(item, outcome);
      }
      done += 1;
      if (done % 100 === 0) log(`  ${done} of ${byLayer.size} layers`);
    }
  }

  const report: MeasureReport = {
    locators: work.length,
    resolved: 0,
    value_present: 0,
    value_partial: 0,
    by_reason: new Map(),
    by_kind: new Map(),
    by_class: new Map(),
    by_parse_bucket: new Map(),
    layers_read: layersRead,
    layers_astral: layersAstral,
    astral_points: astralPoints,
    later_layer: 0,
    work,
  };
  for (const item of work) {
    const byClass = report.by_class.get(item.class) ?? { locators: 0, resolved: 0, value_present: 0 };
    byClass.locators += 1;
    const byBucket = report.by_parse_bucket.get(item.parse_bucket) ?? { locators: 0, resolved: 0 };
    byBucket.locators += 1;
    if (item.resolved) {
      report.resolved += 1;
      byClass.resolved += 1;
      byBucket.resolved += 1;
      if (item.tried > 1) report.later_layer += 1;
      if (item.value_present) {
        report.value_present += 1;
        byClass.value_present += 1;
      }
      if (item.value_partial) report.value_partial += 1;
      report.by_kind.set(item.resolved.kind, (report.by_kind.get(item.resolved.kind) ?? 0) + 1);
    } else if (item.refusal) {
      report.by_reason.set(item.refusal.reason, (report.by_reason.get(item.refusal.reason) ?? 0) + 1);
    } else {
      report.by_reason.set("no_resolver_for_kind", (report.by_reason.get("no_resolver_for_kind") ?? 0) + 1);
    }
    report.by_class.set(item.class, byClass);
    report.by_parse_bucket.set(item.parse_bucket, byBucket);
  }
  return report;
}

const pct = (part: number, whole: number): string => (whole === 0 ? "0.0" : ((part / whole) * 100).toFixed(1));

function reasonTable(report: MeasureReport): string {
  const lines = ["reason\tlocators\tshare_of_all"];
  for (const reason of refusalReasons) {
    const count = report.by_reason.get(reason) ?? 0;
    if (count === 0) continue;
    lines.push(`${reason}\t${count}\t${pct(count, report.locators)}`);
  }
  const refused = report.locators - report.resolved;
  lines.push(`TOTAL REFUSED\t${refused}\t${pct(refused, report.locators)}`);
  return lines.join("\n");
}

function classTable(report: MeasureReport): string {
  const lines = ["class\tlocators\tresolved\tresolved_pct\tvalue_present\tvalue_present_pct\ttop_refusal\ttop_refusal_count"];
  for (const [cls, row] of [...report.by_class.entries()].sort((a, b) => b[1].locators - a[1].locators)) {
    const reasons = new Map<RefusalReason, number>();
    for (const item of report.work)
      if (item.class === cls && !item.resolved && item.refusal)
        reasons.set(item.refusal.reason, (reasons.get(item.refusal.reason) ?? 0) + 1);
    const top = [...reasons.entries()].sort((a, b) => b[1] - a[1])[0];
    lines.push(
      [cls, row.locators, row.resolved, pct(row.resolved, row.locators), row.value_present, pct(row.value_present, row.resolved), top ? top[0] : "", top ? top[1] : 0].join("\t"),
    );
  }
  lines.push(
    ["TOTAL", report.locators, report.resolved, pct(report.resolved, report.locators), report.value_present, pct(report.value_present, report.resolved), "", ""].join("\t"),
  );
  return lines.join("\n");
}

function kindTable(report: MeasureReport): string {
  const lines = ["span_kind\tspans\tvalue_present\tvalue_present_pct\tvalue_partly_present"];
  for (const [kind, count] of [...report.by_kind.entries()].sort((a, b) => b[1] - a[1])) {
    const present = report.work.filter((item) => item.resolved?.kind === kind && item.value_present).length;
    const partial = report.work.filter((item) => item.resolved?.kind === kind && item.value_partial).length;
    lines.push(`${kind}\t${count}\t${present}\t${pct(present, count)}\t${partial}`);
  }
  return lines.join("\n");
}

function bucketTable(report: MeasureReport): string {
  const lines = ["parse_bucket\tlocators\tresolved\tresolved_pct"];
  for (const bucket of ["full", "partial", "residue", "unanchored"] as LocatorCoverage[]) {
    const row = report.by_parse_bucket.get(bucket);
    if (!row) continue;
    lines.push(`${bucket}\t${row.locators}\t${row.resolved}\t${pct(row.resolved, row.locators)}`);
  }
  return lines.join("\n");
}

function detailRows(report: MeasureReport): string {
  const lines = ["id\tclass\tparse_bucket\toutcome\treason_or_kind\tlayer_sha256\tvalue_present\tlayers_tried"];
  for (const item of report.work)
    lines.push(
      [
        item.result.id,
        item.class,
        item.parse_bucket,
        item.resolved ? "resolved" : "refused",
        item.resolved ? item.resolved.kind : (item.refusal?.reason ?? "none"),
        item.resolved ? item.resolved.layer_sha256 : (item.refusal?.layer_sha256 ?? ""),
        item.resolved ? String(item.value_present) : "",
        String(item.tried),
      ].join("\t"),
    );
  return lines.join("\n");
}

function runMeasure(root: string, out: string): void {
  const started = Date.now();
  const report = measure({ root, log: (line) => process.stderr.write(`${line}\n`) });
  fs.mkdirSync(out, { recursive: true });
  const date = new Date().toISOString().slice(0, 10);
  const prefix = path.join(out, `span-resolution-${date}`);
  fs.writeFileSync(`${prefix}-by-class.tsv`, `${classTable(report)}\n`);
  fs.writeFileSync(`${prefix}-by-reason.tsv`, `${reasonTable(report)}\n`);
  fs.writeFileSync(`${prefix}-by-kind.tsv`, `${kindTable(report)}\n`);
  fs.writeFileSync(`${prefix}-by-parse-bucket.tsv`, `${bucketTable(report)}\n`);
  if (process.env.SPAN_DETAIL) fs.writeFileSync(process.env.SPAN_DETAIL, `${detailRows(report)}\n`);
  process.stdout.write(`${classTable(report)}\n\n${reasonTable(report)}\n\n${kindTable(report)}\n\n${bucketTable(report)}\n\n`);
  process.stdout.write(
    `locators ${report.locators}, resolved ${report.resolved} (${pct(report.resolved, report.locators)}%), ` +
      `value present ${report.value_present} (${pct(report.value_present, report.resolved)}% of resolved), ` +
      `value partly present ${report.value_partial} (${pct(report.value_partial, report.resolved)}%)\n`,
  );
  process.stdout.write(
    `layers read ${report.layers_read}, of which ${report.layers_astral} hold a code point above the basic ` +
      `multilingual plane (${report.astral_points} in all); ${report.later_layer} locators resolved on a layer after the first\n`,
  );
  process.stdout.write(`${((Date.now() - started) / 1000).toFixed(0)} s\n`);
}

/** The control ADR 0002 decision 10 names: the 14 value-check files, which record what a reader
 * found at each locator. Agreement is reported, never used to choose a span. */
function runControl(root: string): void {
  const files = fs
    .readdirSync(path.join(root, "data/omics"))
    .map((batch) => path.join(root, "data/omics", batch, "value-check.tsv"))
    .filter((file) => fs.existsSync(file));
  const wanted = new Map<string, string>();
  for (const file of files)
    for (const line of fs.readFileSync(file, "utf8").split("\n").slice(1)) {
      const parts = line.split("\t");
      if (parts.length < 4) continue;
      wanted.set(parts[0], parts[1]);
    }
  const report = measure({ root, log: (line) => process.stderr.write(`${line}\n`) });
  const grid = new Map<string, number>();
  let matched = 0;
  for (const item of report.work) {
    const status = wanted.get(item.result.id);
    if (!status) continue;
    matched += 1;
    const mine = item.resolved
      ? item.value_present
        ? "span_with_value"
        : item.value_partial
          ? "span_inside_value"
          : "span_without_value"
      : (item.refusal?.reason ?? "none");
    const key = `${status}\t${mine}`;
    grid.set(key, (grid.get(key) ?? 0) + 1);
  }
  process.stdout.write(`value-check rows found in the store: ${matched} of ${wanted.size} over ${files.length} files\n\n`);
  process.stdout.write("value_check_status\tspan_outcome\trows\n");
  for (const [key, count] of [...grid.entries()].sort((a, b) => b[1] - a[1])) process.stdout.write(`${key}\t${count}\n`);
}

function runShow(root: string, id: string): void {
  const report = measure({ root, limit: undefined, log: () => {} });
  const item = report.work.find((candidate) => candidate.result.id === id);
  if (!item) {
    process.stdout.write(`no result with id ${id}\n`);
    return;
  }
  process.stdout.write(`${item.result.id}\n  locator  ${item.result.locator}\n  printed  ${item.result.printed_value}\n`);
  process.stdout.write(`  class    ${item.class}, parse bucket ${item.parse_bucket}, verdict ${item.parsed.verdict}\n`);
  process.stdout.write(`  layers   ${item.candidates.map((candidate) => `${candidate.normaliser} ${candidate.layer_sha256.slice(0, 12)}`).join(", ") || "none"}\n`);
  if (item.resolved)
    process.stdout.write(
      `  span     ${item.resolved.kind} [${item.resolved.span.start}, ${item.resolved.span.end}) code points, ` +
        `[${item.resolved.span.byte_start}, ${item.resolved.span.byte_end}) bytes\n  exact    ${JSON.stringify(item.resolved.span.exact)}\n` +
        `  crossed  row ${JSON.stringify(item.resolved.row_label ?? null)}, column ${JSON.stringify(item.resolved.column_header ?? null)}\n`,
    );
  else process.stdout.write(`  refused  ${item.refusal?.reason}: ${item.refusal?.detail}\n`);
}

function main(argv: string[]): void {
  const root = process.env.SPAN_ROOT ?? ".";
  const command = argv[0] ?? "measure";
  const outAt = argv.indexOf("--out");
  const out = outAt >= 0 ? argv[outAt + 1] : path.join(root, REPORTS);
  if (command === "measure") return runMeasure(root, out);
  if (command === "control") return runControl(root);
  if (command === "show") return runShow(root, argv[1] ?? "");
  process.stdout.write("usage: npm run spans -- measure | control | show <result id>\n");
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main(process.argv.slice(2));
