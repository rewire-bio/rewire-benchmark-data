/** Span resolution over the whole store, ADR 0002 step 5.
 *
 * Usage: npm run spans -- measure [--out <dir>] [--no-grid] [--no-sheet] [--legacy-quote]
 *                                                 resolve every stored locator and report
 *        npm run spans -- retag                   rewrite the tagged figures in the documents
 *        npm run spans -- control                 agree or disagree with the 14 value-check files
 *        npm run spans -- value-check             the rates the numeric value check is held to
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
import { changedInputs, inputFiles, readFigures, retag, SPAN_FIGURES, writeFigures } from "../../../shared/omics/reports/figures";
import { latestBySource, readReceipts } from "../../archive/receipts";
import type { Grid } from "../../../shared/archive/layers/index";
import {
  coverageOf as layerCoverage,
  gridForLayer,
  gridOfRecord,
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
  gridRoutes,
  indexLayer,
  refusalReasons,
  resolveLocator,
  type GridRoute,
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
  /** Whether the span's text is the stored value and nothing else. Containment is the looser
   * test and a cell that holds a whole sentence containing the number passes it; equality is
   * what a check that gated anything would have to use, so both are reported. */
  value_exact: boolean | null;
  value_partial: boolean | null;
  /** Whether the value is in an image and so cannot be in any span of a text layer. See
   * `valueInImage`. */
  value_in_image: boolean | null;
  /** Set where a table grid was read for this locator. */
  grid_route: GridRoute | null;
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

/** One spelling for the marks a layer and a record may write differently: the Unicode minus, the
 * en and em dashes, the plus-minus sign, whitespace and case. */
const flattenValue = (text: string): string =>
  text
    .replace(/[−–—]/g, "-")
    .replace(/±/g, "+/-")
    .replace(/\s+/g, "")
    .toLowerCase();

/** One number and nothing else, as a flattened text. The whole string has to be the number: a
 * text holding a number beside anything else, a second number among them, is not a number pair
 * and is compared as characters. That is what keeps a span of several cells from passing because
 * one of its numbers happens to round to the stored value. */
const ONE_NUMBER = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/;

/** How many decimal places a spelling writes, which is the precision the record keeps.
 *
 * `0.82` writes two, `0.050` writes three, `12` writes none, and `5.0e-2` writes three: an
 * exponent moves the point, so the places written are the mantissa's places less the exponent. */
function decimalsWritten(spelling: string): number {
  const [mantissa, exponent] = spelling.split("e");
  const fraction = mantissa.includes(".") ? mantissa.split(".")[1].length : 0;
  return Math.max(0, Math.min(100, fraction - Number(exponent ?? "0")));
}

/** A number as a plain decimal spelling, exponent written out: the shortest spelling that reads
 * back as the same number. `0.8875` for 0.88749999999999996, `0.050452599342583802` for
 * 5.0452599342583802E-2. The shortest spelling is the number as a person writes it, and it is
 * what the rounding below works on. */
function plainDecimal(value: number): string {
  const text = String(value);
  const match = /^(-?)(\d+)(?:\.(\d+))?e([+-]\d+)$/i.exec(text);
  if (!match) return text;
  const [, sign, whole, fraction, exponent] = match;
  const digits = whole + (fraction ?? "");
  const point = whole.length + Number(exponent);
  if (point <= 0) return `${sign}0.${"0".repeat(-point)}${digits}`;
  if (point >= digits.length) return `${sign}${digits}${"0".repeat(point - digits.length)}`;
  return `${sign}${digits.slice(0, point)}.${digits.slice(point)}`;
}

/** A plain decimal spelling rounded to `places` decimals, half away from zero, which is how a
 * spreadsheet displays a cell and how a paper rounds a number.
 *
 * Done on the digits rather than on the double, because the double is the problem. A cell holding
 * 0.8875 prints as 0.88749999999999996, the nearest double, which sits a hair below the midpoint:
 * rounding that double to three places gives 0.887 and the spreadsheet displays 0.888. Rounding
 * the digits gives 0.888, so a record keeping what the sheet displays is not read as a wrong
 * answer on every cell whose value ends in a 5. */
function roundDecimal(spelling: string, places: number): string {
  const sign = spelling.startsWith("-") ? "-" : "";
  const [whole, fraction = ""] = spelling.replace(/^[+-]/, "").split(".");
  if (fraction.length <= places) return `${sign}${whole}.${fraction.padEnd(places, "0")}`;
  const digits = (whole + fraction.slice(0, places)).split("");
  if (fraction.charCodeAt(places) >= 53) {
    let at = digits.length - 1;
    for (;;) {
      if (at < 0) {
        digits.unshift("1");
        break;
      }
      if (digits[at] === "9") {
        digits[at] = "0";
        at -= 1;
        continue;
      }
      digits[at] = String(Number(digits[at]) + 1);
      break;
    }
  }
  const text = digits.join("");
  const cut = text.length - places;
  return `${sign}${text.slice(0, cut) || "0"}.${text.slice(cut)}`;
}

/**
 * Do a span and a stored value that are each one number print the same number?
 *
 * The rule: at the precision the record writes, and no finer. A record keeping `0.82` says the
 * value is 0.82 to two places, so a span printing 0.81699999999999995 prints it and a span
 * printing 0.73 does not. A record keeping `0.050` says three places, so 5.0452599342583802E-2
 * prints it. The comparison is one directional on purpose: the record's spelling sets the
 * precision, because the record is what a reader is being asked to re-check.
 *
 * Both sides have to be one number. Neither side is scaled, so a percentage against a fraction is
 * not a match here, and nothing strips a thousands separator.
 */
function printsSameNumber(span: string, value: string): boolean {
  if (!ONE_NUMBER.test(span) || !ONE_NUMBER.test(value)) return false;
  const theirs = Number(span);
  const ours = Number(value);
  if (!Number.isFinite(theirs) || !Number.isFinite(ours)) return false;
  const places = decimalsWritten(value);
  return Number(roundDecimal(plainDecimal(theirs), places)) === Number(roundDecimal(plainDecimal(ours), places));
}

/** Does the span print the value the record stores? Never consulted by a resolver: this is the
 * measurement's own check on the resolvers, and using it to choose a cell would make the number
 * meaningless.
 *
 * Three answers, and the order matters. `exact` is the span printing the stored value and
 * nothing else, and it is the headline: it is the only one of the three that a cell span can be
 * held to, because a cell span states that these characters are the value. `present` is the
 * looser figure, the value printed somewhere inside the span, which is the right check for a
 * quote or a page and the wrong one for a cell: a span covering three columns with the stored
 * value in the middle passes it, and 66 such spans did on 2026-11-18. `partial` is the span
 * being part of the value rather than the other way round.
 *
 * A cell span wider than the value is not automatically a defect. A cell printing
 * "0.271 (0.282)" against a record storing "0.271" is the right cell and the paper prints more
 * in it than the record keeps. So the gap between `exact` and `present` is reported, not
 * gated, and the geometry rather than this check is what refuses a span over several columns.
 *
 * ONE NUMBER SPELLED TWO WAYS. Containment is a test on characters and a number has more than one
 * spelling. `ooxml-sheet-tsv@1` prints the characters the workbook stores, which for a computed
 * cell is the full double: 0.81699999999999995, or 5.0452599342583802E-2. The record keeps what
 * the spreadsheet displays, 0.82 or 0.050. The characters share no substring and the two are the
 * same number, so a check that can only compare characters calls the right cell a wrong answer.
 * That is what it did: a run of this check named 1,706 sheet cells as printing no part of the
 * stored value and each one of those 1,706 was the right cell.
 *
 * So the rule below is: where the span and the stored value each reduce to one number and nothing
 * else, they match when the span's number equals the stored value at the precision the record
 * writes. Everything else is still compared as characters. */
export function valuePresence(exact: string, printed: string): { present: boolean; exact: boolean; partial: boolean } {
  if (!printed) return { present: false, exact: false, partial: false };
  const span = flattenValue(exact);
  const value = flattenValue(printed);
  // A number pair is decided as numbers first, because the character test gets the second column
  // wrong on one of them even where it gets the first right: a cell printing 0.81700000000000005
  // against a record keeping 0.817 contains the record's characters, so containment would call it
  // present and not exact, and it would be counted among the spans wider than the value. It is
  // not wider. It is one number and nothing else, printed to more places than the record keeps,
  // so a number pair that matches is `exact` as well as `present`.
  if (printsSameNumber(span, value)) return { present: true, exact: true, partial: false };
  if (span.includes(value)) return { present: true, exact: span === value, partial: false };
  // The span is part of the value: a layer that prints "0.662" and "(+/- 0.044)" as two fields
  // against a record that stores both. The cell is the right cell and the record keeps more of
  // the line than the cell holds, which is a different finding from a wrong cell.
  if (span.length > 0 && /[0-9]/.test(span) && value.includes(span)) return { present: false, exact: false, partial: true };
  return { present: false, exact: false, partial: false };
}

/**
 * Does the locator say the value is in an image?
 *
 * A figure caption is the span a figure locator names and the number is inside the image, which
 * ADR 0002 already calls unverifiable. Some prose locators say the same thing in words:
 * `Results 'Results for "Species out of the database" settings' paragraph 3, last sentences
 * (values shown in Fig. 3f)` names the paragraph that describes the result and says where the
 * number is printed, which is a bar chart. A span on either is the place the locator names, and
 * the value check cannot see the value there however right the span is.
 *
 * So those spans are counted apart from the spans that commit to text which should print the
 * value and does not. The test is on the locator's own words, not on the record or on the
 * outcome: "citing Fig. 2A:" followed by a quoted sentence does not match, because that locator
 * says the sentence prints the number and the figure draws it as well.
 */
const VALUE_IN_IMAGE = /\b(?:shown|drawn|plotted|depicted|read)\s+(?:in|on|off|from)\s+(?:the\s+)?(?:fig\b|fig\.|figure|panel|chart|plot|bar)/i;

interface MeasureOptions {
  root: string;
  limit?: number;
  log?: (line: string) => void;
  /** Read the table grid beside each markup text layer and cross a row and a column against it.
   * On by default. `measure --no-grid` turns it off, which is how the gain the grids buy is
   * measured as a rate over the same locators rather than as an anecdote. */
  grid?: boolean;
  /** Read the sheet blocks of an office layer and resolve a cell reference against them. On by
   * default. `measure --no-sheet` turns it off, which is how the coverage the sheet blocks buy is
   * measured as a rate over the same locators rather than as an anecdote. The layer prints the
   * workbook's stored double and the record keeps the value the spreadsheet displays, so these
   * spans are checked against the record by `printsSameNumber` and not by characters. */
  sheet?: boolean;
  /** Choose the quoted run to resolve the way the resolver did before the label rule. Off by
   * default, and `measure --legacy-quote` turns it on, which is how the rule's effect is
   * measured over the same locators in the same process. */
  legacyQuote?: boolean;
}

export interface MeasureReport {
  locators: number;
  resolved: number;
  value_present: number;
  value_exact: number;
  value_partial: number;
  /** Spans the value check cannot see the value in because the value is in an image. See
   * `VALUE_IN_IMAGE`. */
  value_in_image: number;
  /** Locators a table grid was read for, by the route that found the table. */
  by_grid_route: Map<GridRoute, { locators: number; resolved: number; value_present: number; value_exact: number }>;
  /** Grids read, and grids whose bytes would not come back. */
  grids_read: number;
  grids_unreadable: number;
  by_reason: Map<RefusalReason, number>;
  by_kind: Map<SpanKind, number>;
  by_class: Map<LocatorClass, { locators: number; resolved: number; value_present: number; value_exact: number }>;
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
      value_exact: null,
      value_partial: null,
      value_in_image: null,
      grid_route: null,
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
  let gridsRead = 0;
  let gridsUnreadable = 0;
  const useGrids = options.grid !== false;
  /** The grid beside one text layer, read once. A text layer with no grid normaliser, or whose
   * grid is not in the registry, gets null and the aligned resolver, which is where it was. */
  const gridCache = new Map<string, Grid | null>();
  const gridFor = (layerSha: string): Grid | null => {
    if (!useGrids) return null;
    const known = gridCache.get(layerSha);
    if (known !== undefined) return known;
    let grid: Grid | null = null;
    const record = gridForLayer(layerSha, root);
    if (record) {
      try {
        grid = gridOfRecord(record, root);
        gridsRead += 1;
      } catch {
        gridsUnreadable += 1;
        grid = null;
      }
    }
    gridCache.set(layerSha, grid);
    return grid;
  };
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
      const grid = gridFor(layerSha);
      for (const item of items) {
        item.tried += 1;
        const outcome = resolveLocator(item.parsed, index, grid, { sheet: options.sheet !== false, legacyQuote: options.legacyQuote === true });
        if (outcome.grid_route) item.grid_route = outcome.grid_route;
        if (outcome.ok) {
          item.resolved = outcome;
          const presence = valuePresence(outcome.span.exact, item.result.printed_value);
          item.value_present = presence.present;
          item.value_exact = presence.exact;
          item.value_partial = presence.partial;
          item.value_in_image =
            !presence.present && !presence.partial && (outcome.kind === "figure_caption" || VALUE_IN_IMAGE.test(item.result.locator));
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
    value_exact: 0,
    value_partial: 0,
    value_in_image: 0,
    by_grid_route: new Map(),
    grids_read: gridsRead,
    grids_unreadable: gridsUnreadable,
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
    const byClass = report.by_class.get(item.class) ?? { locators: 0, resolved: 0, value_present: 0, value_exact: 0 };
    byClass.locators += 1;
    const byBucket = report.by_parse_bucket.get(item.parse_bucket) ?? { locators: 0, resolved: 0 };
    byBucket.locators += 1;
    if (item.grid_route) {
      const byRoute = report.by_grid_route.get(item.grid_route) ?? { locators: 0, resolved: 0, value_present: 0, value_exact: 0 };
      byRoute.locators += 1;
      // Only a span the grid produced counts as resolved here. A locator whose grid attempt
      // refused and which then resolved on a PDF layer is a grid attempt and not a grid span.
      if (item.resolved?.kind === "grid_cell") {
        byRoute.resolved += 1;
        if (item.value_present) byRoute.value_present += 1;
        if (item.value_exact) byRoute.value_exact += 1;
      }
      report.by_grid_route.set(item.grid_route, byRoute);
    }
    if (item.resolved) {
      report.resolved += 1;
      byClass.resolved += 1;
      byBucket.resolved += 1;
      if (item.tried > 1) report.later_layer += 1;
      if (item.value_present) {
        report.value_present += 1;
        byClass.value_present += 1;
      }
      if (item.value_exact) {
        report.value_exact += 1;
        byClass.value_exact += 1;
      }
      if (item.value_partial) report.value_partial += 1;
      if (item.value_in_image) report.value_in_image += 1;
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
  const lines = ["class\tlocators\tresolved\tresolved_pct\tvalue_exact\tvalue_exact_pct\tvalue_present\tvalue_present_pct\ttop_refusal\ttop_refusal_count"];
  for (const [cls, row] of [...report.by_class.entries()].sort((a, b) => b[1].locators - a[1].locators)) {
    const reasons = new Map<RefusalReason, number>();
    for (const item of report.work)
      if (item.class === cls && !item.resolved && item.refusal)
        reasons.set(item.refusal.reason, (reasons.get(item.refusal.reason) ?? 0) + 1);
    const top = [...reasons.entries()].sort((a, b) => b[1] - a[1])[0];
    lines.push(
      [cls, row.locators, row.resolved, pct(row.resolved, row.locators), row.value_exact, pct(row.value_exact, row.resolved), row.value_present, pct(row.value_present, row.resolved), top ? top[0] : "", top ? top[1] : 0].join("\t"),
    );
  }
  lines.push(
    ["TOTAL", report.locators, report.resolved, pct(report.resolved, report.locators), report.value_exact, pct(report.value_exact, report.resolved), report.value_present, pct(report.value_present, report.resolved), "", ""].join("\t"),
  );
  return lines.join("\n");
}

function kindTable(report: MeasureReport): string {
  // Exact first, then containment. A cell span is held to printing the stored value and nothing
  // else; a quote or a page span is not, and reading the two columns together is what tells one
  // from the other.
  const lines = [
    "span_kind\tspans\tvalue_exact\tvalue_exact_pct\tvalue_present\tvalue_present_pct\twider_than_value\tvalue_partly_present\tvalue_in_image\tno_value",
  ];
  for (const [kind, count] of [...report.by_kind.entries()].sort((a, b) => b[1] - a[1])) {
    const exact = report.work.filter((item) => item.resolved?.kind === kind && item.value_exact).length;
    const present = report.work.filter((item) => item.resolved?.kind === kind && item.value_present).length;
    const partial = report.work.filter((item) => item.resolved?.kind === kind && item.value_partial).length;
    // A span whose value is in an image is counted out of `no_value` and into its own column. It
    // is the place the locator names and no span of a text layer can print what a chart draws, so
    // counting it as a wrong span makes the error rate say something it does not mean.
    const image = report.work.filter((item) => item.resolved?.kind === kind && item.value_in_image).length;
    lines.push(
      `${kind}\t${count}\t${exact}\t${pct(exact, count)}\t${present}\t${pct(present, count)}\t${present - exact}\t${partial}\t${image}\t${count - present - partial - image}`,
    );
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

/** Locators a grid was read for, and what came of it. The route split matters: a label is what
 * the markup wrote on the table and a caption window is a line of prose above it. */
function gridTable(report: MeasureReport): string {
  const lines = ["grid_route\tlocators\tresolved\tresolved_pct\tvalue_present\tvalue_present_pct\tvalue_exact\tvalue_exact_pct"];
  let locators = 0;
  let resolved = 0;
  let present = 0;
  let exact = 0;
  for (const route of gridRoutes) {
    const row = report.by_grid_route.get(route);
    if (!row) continue;
    locators += row.locators;
    resolved += row.resolved;
    present += row.value_present;
    exact += row.value_exact;
    lines.push(
      [route, row.locators, row.resolved, pct(row.resolved, row.locators), row.value_present, pct(row.value_present, row.resolved), row.value_exact, pct(row.value_exact, row.resolved)].join("\t"),
    );
  }
  lines.push(["TOTAL", locators, resolved, pct(resolved, locators), present, pct(present, resolved), exact, pct(exact, resolved)].join("\t"));
  return lines.join("\n");
}

function detailRows(report: MeasureReport): string {
  const lines = ["id\tclass\tparse_bucket\toutcome\treason_or_kind\tlayer_sha256\tvalue_present\tvalue_exact\tgrid_route\tlayers_tried"];
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
        item.resolved ? String(item.value_exact) : "",
        item.grid_route ?? "",
        String(item.tried),
      ].join("\t"),
    );
  return lines.join("\n");
}

/** Spans that commit to text which should print the stored value and does not.
 *
 * Three kinds of span are not one of these and are counted on their own. A span printing more
 * than the value prints the value. A span printing part of it is the right cell with the record
 * keeping more than the cell does. A span whose value is in an image is the place the locator
 * names, and no span of a text layer can print what a chart draws. */
export const wrongCommits = (report: MeasureReport): number =>
  report.resolved - report.value_present - report.value_partial - report.value_in_image;

/** The figures this command stands behind, flat and named, for `shared/omics/reports/figures.ts`.
 *
 * Every figure a committed document prints should be in here. A document tags the number with the
 * figure's name and `tests/omics-report-drift.test.ts` holds the two to each other, so a figure
 * that is not in this map cannot be checked and a number in a document that disagrees with this
 * map fails a test by name. Percentages are rounded here exactly as the tables print them, so a
 * document and this file spell a figure the same way or one of them is wrong. */
function figuresOf(report: MeasureReport): Record<string, number> {
  const share = (part: number, whole: number): number => Number(pct(part, whole));
  const figures: Record<string, number> = {
    locators: report.locators,
    resolved: report.resolved,
    resolved_pct: share(report.resolved, report.locators),
    refused: report.locators - report.resolved,
    value_exact: report.value_exact,
    value_exact_pct: share(report.value_exact, report.resolved),
    value_present: report.value_present,
    value_present_pct: share(report.value_present, report.resolved),
    value_partial: report.value_partial,
    value_in_image: report.value_in_image,
    wrong_commits: wrongCommits(report),
    wider_than_value: report.value_present - report.value_exact,
    layers_read: report.layers_read,
    layers_astral: report.layers_astral,
    astral_points: report.astral_points,
    grids_read: report.grids_read,
    later_layer: report.later_layer,
  };
  for (const [reason, count] of report.by_reason) {
    figures[`reason.${reason}`] = count;
    figures[`reason.${reason}.pct`] = share(count, report.locators);
  }
  for (const [kind, count] of report.by_kind) {
    const of = (test: (item: Work) => boolean): number => report.work.filter((item) => item.resolved?.kind === kind && test(item)).length;
    figures[`kind.${kind}.spans`] = count;
    figures[`kind.${kind}.value_exact`] = of((item) => item.value_exact === true);
    figures[`kind.${kind}.value_present`] = of((item) => item.value_present === true);
    figures[`kind.${kind}.value_in_image`] = of((item) => item.value_in_image === true);
    figures[`kind.${kind}.no_value`] =
      count - of((item) => item.value_present === true) - of((item) => item.value_partial === true) - of((item) => item.value_in_image === true);
  }
  for (const [cls, row] of report.by_class) {
    figures[`class.${cls}.locators`] = row.locators;
    figures[`class.${cls}.resolved`] = row.resolved;
    figures[`class.${cls}.resolved_pct`] = share(row.resolved, row.locators);
    figures[`class.${cls}.value_exact`] = row.value_exact;
    figures[`class.${cls}.value_present`] = row.value_present;
  }
  for (const [bucket, row] of report.by_parse_bucket) {
    figures[`bucket.${bucket}.locators`] = row.locators;
    figures[`bucket.${bucket}.resolved`] = row.resolved;
  }
  return figures;
}

/** The paired arm's figures, under `legacy.`, so the report's pair table can tag both of its
 * columns. Only the six the table prints: a figure nothing prints is a figure nothing checks. */
function legacyFiguresOf(report: MeasureReport | null): Record<string, number> {
  if (!report) return {};
  const quotes = report.by_kind.get("quote") ?? 0;
  const of = (test: (item: Work) => boolean): number => report.work.filter((item) => item.resolved?.kind === "quote" && test(item)).length;
  return {
    "legacy.resolved": report.resolved,
    "legacy.value_present": report.value_present,
    "legacy.value_exact": report.value_exact,
    "legacy.wrong_commits": wrongCommits(report),
    "legacy.kind.quote.spans": quotes,
    "legacy.kind.quote.no_value":
      quotes - of((item) => item.value_present === true) - of((item) => item.value_partial === true) - of((item) => item.value_in_image === true),
  };
}

/** The documents whose span figures this command's sidecar holds. A document named here is
 * checked for tagged figures; one that tags a figure and is not named here is checked too. */
const FIGURE_DOCUMENTS = ["maintenance/reports/span-resolution-2026-11-18.md", "docs/adr/0002-claim-extraction.html"];

function runMeasure(root: string, out: string, grid: boolean, sheet: boolean, legacyQuote: boolean): void {
  const started = Date.now();
  // The tree every figure below is a measurement of, read before the first layer is and again
  // after the last. A run that loaded a source file which then changed has measured a tree that
  // no longer exists, and it has no way of knowing that from its own output: the run is
  // self-consistent and the figures are of nothing. This is the only place that can catch it,
  // because the files the figures depend on are read once and held in memory for the rest of the
  // run.
  const openedWith = inputFiles(root);
  const report = measure({ root, grid, sheet, legacyQuote, log: (line) => process.stderr.write(`${line}\n`) });
  // A run with any arm flag set is one half of a pair and not a measurement of the tree, so it
  // writes nothing. A `--no-grid` run that overwrote the committed tables is how the span report
  // went stale once already.
  const pinned = grid && sheet && !legacyQuote;
  // The quote rule is reported as a pair, and the report prints both arms of it in one table. A
  // figure a document prints has to be one the figures file holds or no test can see it, so the
  // paired arm is run here rather than by hand: same process, same layer bytes, same tree, and
  // its figures are written beside the shipped ones under `legacy.`.
  const legacy = pinned ? measure({ root, grid, sheet, legacyQuote: true, log: (line) => process.stderr.write(`legacy arm: ${line}\n`) }) : null;
  const moved = changedInputs(openedWith, inputFiles(root));
  const date = new Date().toISOString().slice(0, 10);
  const prefix = path.join(out, `span-resolution-${date}`);
  if (moved.length > 0) {
    process.stderr.write(
      `the tree moved while this run was measuring it, so nothing was written. ${moved.length} input ` +
        `${moved.length === 1 ? "file" : "files"} changed:\n${moved.map((file) => `  ${file.path}`).join("\n")}\n` +
        "the figures this run holds are of a tree that no longer exists. run it again.\n",
    );
    process.exitCode = 1;
  } else if (pinned) {
    fs.mkdirSync(out, { recursive: true });
    fs.writeFileSync(`${prefix}-by-class.tsv`, `${classTable(report)}\n`);
    fs.writeFileSync(`${prefix}-by-reason.tsv`, `${reasonTable(report)}\n`);
    fs.writeFileSync(`${prefix}-by-kind.tsv`, `${kindTable(report)}\n`);
    fs.writeFileSync(`${prefix}-by-parse-bucket.tsv`, `${bucketTable(report)}\n`);
    fs.writeFileSync(`${prefix}-by-grid-route.tsv`, `${gridTable(report)}\n`);
    // The figures file sits beside the committed tables and is read against them, so a run
    // writing its tables somewhere else does not write it.
    if (path.resolve(out) === path.resolve(path.join(root, REPORTS)))
      writeFigures(root, {
        command: "npm run spans -- measure",
        produced: date,
        documents: FIGURE_DOCUMENTS,
        inputs: openedWith,
        figures: { ...figuresOf(report), ...legacyFiguresOf(legacy) },
      });
    if (process.env.SPAN_DETAIL) fs.writeFileSync(process.env.SPAN_DETAIL, `${detailRows(report)}\n`);
  } else {
    process.stdout.write("one arm of a pair: nothing written, because these figures are not the tree's\n");
    if (process.env.SPAN_DETAIL) fs.writeFileSync(process.env.SPAN_DETAIL, `${detailRows(report)}\n`);
  }
  process.stdout.write(`${classTable(report)}\n\n${reasonTable(report)}\n\n${kindTable(report)}\n\n${bucketTable(report)}\n\n${gridTable(report)}\n\n`);
  process.stdout.write(
    `locators ${report.locators}, resolved ${report.resolved} (${pct(report.resolved, report.locators)}%), ` +
      `span prints the stored value and nothing else ${report.value_exact} ` +
      `(${pct(report.value_exact, report.resolved)}% of resolved), ` +
      `span prints it somewhere ${report.value_present} (${pct(report.value_present, report.resolved)}%, the looser check), ` +
      `span is part of the value ${report.value_partial} (${pct(report.value_partial, report.resolved)}%)\n`,
  );
  process.stdout.write(
    `committed to text that does not print the stored value: ${wrongCommits(report)}; ` +
      `committed to more text than the stored value: ${report.value_present - report.value_exact}; ` +
      `span right and the value in an image: ${report.value_in_image}\n` +
      `grids read ${report.grids_read}${report.grids_unreadable > 0 ? `, ${report.grids_unreadable} unreadable` : ""}\n`,
  );
  process.stdout.write(
    `layers read ${report.layers_read}, of which ${report.layers_astral} hold a code point above the basic ` +
      `multilingual plane (${report.astral_points} in all); ${report.later_layer} locators resolved on a layer after the first\n`,
  );
  if (legacy)
    process.stdout.write(
      `the quote rule as a pair, legacy then shipped: resolved ${legacy.resolved} then ${report.resolved}; ` +
        `prints the value somewhere ${legacy.value_present} then ${report.value_present}; ` +
        `prints it and nothing else ${legacy.value_exact} then ${report.value_exact}; ` +
        `commits to text that does not print it ${wrongCommits(legacy)} then ${wrongCommits(report)}; ` +
        `quote spans ${legacy.by_kind.get("quote") ?? 0} then ${report.by_kind.get("quote") ?? 0}\n`,
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

/** The value check as it stood before the numeric rule: characters only, kept so the effect of
 * the rule can be counted over the same spans rather than described. */
function stringOnlyPresence(exact: string, printed: string): boolean {
  if (!printed) return false;
  return flattenValue(exact).includes(flattenValue(printed));
}

/**
 * `npm run spans -- value-check`: the two properties the numeric rule is held to, as rates over
 * every span the store resolves.
 *
 * Coverage is not the thing to prove about a value check. A check that accepts everything has
 * perfect coverage and says nothing, and a check that cannot compare numbers withdraws thousands
 * of correct spans, which is what happened here. So the two rates below are the result, and both
 * are measured by perturbing the store's own spans rather than by inventing cases:
 *
 *   1. A genuinely different number still fails. Each accepted number pair is perturbed to a
 *      number that differs from the record at the record's own precision, spelled both the way a
 *      reader writes it and the way a workbook stores it. A perturbation finer than the record's
 *      precision is accepted by design, not wrongly, so it is excluded and counted.
 *   2. A span holding several numbers does not pass because one of them rounds to the stored
 *      value. Each accepted pair's own number is put beside a different one, three ways. A
 *      constructed span that prints the record's characters outright is excluded, because there
 *      the character test answers and the numeric rule is not what passed it.
 *
 * Acceptances are split by which test said yes, because the character test is older than this
 * rule and still answers first for everything that is not a number pair.
 */
function runValueCheck(root: string): void {
  const report = measure({ root, log: (line) => process.stderr.write(`${line}\n`) });
  const resolved = report.work.filter((item) => item.resolved !== null);
  const pairs = resolved
    .map((item) => ({
      kind: item.resolved!.kind,
      span: flattenValue(item.resolved!.span.exact),
      value: flattenValue(item.result.printed_value),
    }))
    .filter((pair) => ONE_NUMBER.test(pair.span) && ONE_NUMBER.test(pair.value))
    .map((pair) => ({ ...pair, places: decimalsWritten(pair.value) }));
  const accepted = pairs.filter((pair) => valuePresence(pair.span, pair.value).present);

  /** Numbers that differ from the record at the record's own precision, spelled two ways: the
   * shortest spelling a reader writes and the 17 significant digits a workbook stores.
   *
   * Whether a perturbation is a different number is judged by `toFixed`, which rounds the double,
   * and not by the rule's own rounding of the digits. A test that excluded what the rule accepts
   * could never find anything. `far` marks the perturbations that differ from the record by more
   * than a whole unit of the last place it writes, where no rounding of any kind can reach the
   * record's value and an acceptance would be unarguable. */
  const wrongNumbers = (pair: (typeof pairs)[number]): { text: string; far: boolean }[] => {
    const unit = 10 ** -pair.places;
    const base = Number(pair.span);
    const ours = Number(pair.value);
    const stored = ours.toFixed(pair.places);
    const out: { text: string; far: boolean }[] = [];
    for (const candidate of [base + unit, base - unit, base + 10 * unit, base * 1.1]) {
      if (!Number.isFinite(candidate)) continue;
      if (candidate.toFixed(pair.places) === stored) continue;
      const far = Math.abs(candidate - ours) > unit;
      out.push({ text: String(candidate), far }, { text: candidate.toPrecision(17), far });
    }
    return out;
  };

  let wrongTried = 0;
  let wrongByNumber = 0;
  let wrongByString = 0;
  let wrongExcluded = 0;
  let coarseTried = 0;
  let coarseByNumber = 0;
  let farTried = 0;
  let farByNumber = 0;
  let severalTried = 0;
  let severalAccepted = 0;
  let severalExcluded = 0;
  for (const pair of accepted) {
    const wrongs = wrongNumbers(pair);
    wrongExcluded += 8 - wrongs.length;
    for (const wrong of wrongs) {
      wrongTried += 1;
      if (pair.places <= 15) coarseTried += 1;
      if (wrong.far) farTried += 1;
      if (!valuePresence(wrong.text, pair.value).present) continue;
      if (stringOnlyPresence(wrong.text, pair.value)) wrongByString += 1;
      else {
        wrongByNumber += 1;
        if (pair.places <= 15) coarseByNumber += 1;
        if (wrong.far) farByNumber += 1;
      }
    }
    const other = wrongs[0]?.text ?? "0";
    for (const text of [`${pair.span}\t${other}`, `${pair.span} (${other})`, `${other}\t${pair.span}`]) {
      if (flattenValue(text).includes(pair.value)) {
        severalExcluded += 1;
        continue;
      }
      severalTried += 1;
      if (valuePresence(text, pair.value).present) severalAccepted += 1;
    }
  }

  const rate = (part: number, whole: number): string => (whole === 0 ? "0.0000" : ((part / whole) * 100).toFixed(4));
  const sheet = resolved.filter((item) => item.resolved!.kind === "sheet_cell");
  const sheetByString = sheet.filter((item) => stringOnlyPresence(item.resolved!.span.exact, item.result.printed_value)).length;
  const flipped = resolved.filter((item) => item.value_present === true && !stringOnlyPresence(item.resolved!.span.exact, item.result.printed_value));
  const byKind = new Map<SpanKind, number>();
  for (const item of flipped) byKind.set(item.resolved!.kind, (byKind.get(item.resolved!.kind) ?? 0) + 1);
  // What the character test said about those spans before. Some printed nothing the record holds,
  // and some were a substring of the record, `0.5` against a record of `0.50`, which the old
  // check reported as the span being part of the value rather than as a wrong span.
  const wasPartial = flipped.filter((item) =>
    flattenValue(item.result.printed_value).includes(flattenValue(item.resolved!.span.exact)),
  ).length;

  process.stdout.write(
    `resolved spans ${resolved.length}; number pairs ${pairs.length}, of which the rule accepts ${accepted.length}\n` +
      `spans the numeric rule alone finds the value in: ${flipped.length} ` +
      `(${[...byKind.entries()].sort((a, b) => b[1] - a[1]).map(([kind, count]) => `${kind} ${count}`).join(", ")}), ` +
      `of which the character test called ${wasPartial} part of the value and ${flipped.length - wasPartial} no part of it\n` +
      `a different number at the record's precision: tried ${wrongTried}, accepted by the numeric rule ${wrongByNumber} ` +
      `(${rate(wrongByNumber, wrongTried)}%), accepted by the character test ${wrongByString} (${rate(wrongByString, wrongTried)}%), ` +
      `excluded as finer than the record's precision ${wrongExcluded}\n` +
      `  over the records writing 15 decimal places or fewer: tried ${coarseTried}, accepted by the numeric rule ${coarseByNumber}\n` +
      `  over the perturbations further than one unit of the record's last place: tried ${farTried}, accepted by the numeric rule ${farByNumber}\n` +
      `several numbers, one of them rounding to the stored value: tried ${severalTried}, accepted ${severalAccepted} ` +
      `(${rate(severalAccepted, severalTried)}%), excluded as printing the value outright ${severalExcluded}\n` +
      `sheet_cell spans ${sheet.length}: print the stored value ${sheet.filter((item) => item.value_present === true).length}, ` +
      `of which the character test alone sees ${sheetByString}; print no part of it ` +
      `${sheet.filter((item) => item.value_present !== true && item.value_partial !== true && item.value_in_image !== true).length}\n`,
  );
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

/** `npm run spans -- retag`: rewrite the number in front of every figure tag in the documents the
 * figures file names, from the figures file. The measuring run is what produces those figures, so
 * this reads no layer and resolves nothing. */
function runRetag(root: string): void {
  const figures = readFigures(root);
  for (const document of figures.documents) {
    const file = path.join(root, document);
    if (!fs.existsSync(file)) {
      process.stdout.write(`${document}: not in this tree\n`);
      continue;
    }
    const before = fs.readFileSync(file, "utf8");
    const { text, changed, unknown } = retag(before, figures.figures);
    if (text !== before) fs.writeFileSync(file, text);
    process.stdout.write(
      `${document}: ${changed.length} ${changed.length === 1 ? "figure" : "figures"} rewritten` +
        `${changed.length > 0 ? ` (${changed.map((mark) => `${mark.figure} was ${mark.printed}`).join(", ")})` : ""}` +
        `${unknown.length > 0 ? `; ${unknown.length} tagged ${unknown.length === 1 ? "figure" : "figures"} ${SPAN_FIGURES} does not hold: ${unknown.map((mark) => mark.figure).join(", ")}` : ""}\n`,
    );
  }
}

function main(argv: string[]): void {
  const root = process.env.SPAN_ROOT ?? ".";
  const command = argv[0] ?? "measure";
  const outAt = argv.indexOf("--out");
  const out = outAt >= 0 ? argv[outAt + 1] : path.join(root, REPORTS);
  if (command === "measure")
    return runMeasure(root, out, !argv.includes("--no-grid"), !argv.includes("--no-sheet"), argv.includes("--legacy-quote"));
  if (command === "retag") return runRetag(root);
  if (command === "control") return runControl(root);
  if (command === "value-check") return runValueCheck(root);
  if (command === "show") return runShow(root, argv[1] ?? "");
  process.stdout.write("usage: npm run spans -- measure [--out <dir>] [--no-grid] [--no-sheet] [--legacy-quote] | retag | control | value-check | show <result id>\n");
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main(process.argv.slice(2));
