/** Coverage with an arithmetic identity, ADR 0002 decision 7 at source level.
 *
 * Every source record is in exactly one bucket and the buckets sum to the
 * source count. That is the whole point: a coverage report whose parts do not
 * add up lets a source go missing between two numbers that both look right.
 *
 * The bucket comes from two facts and nothing else.
 *
 * 1. The latest fetch receipt for the source, which the archive lane writes
 *    for a failure as well as a success. `failed` means no bytes arrived.
 *    `not_artifact` means bytes arrived and are demonstrably not the source,
 *    which the archive lane decided at capture time and this does not
 *    second-guess.
 * 2. For a `stored` receipt, the layers the registry holds for the object
 *    that receipt names. The receipt names the primary artifact, so a source
 *    that also cites a supplement is bucketed on its paper and the supplement
 *    is still in the registry under its own object.
 *
 * A source with no receipt at all is counted and named rather than dropped.
 * There are none today, and a reader should not have to trust that.
 *
 * A source's character count is its best layer, not the sum of the layers
 * under its object: a supplement zip holding five passing PDFs counts the
 * longest one. That is the substrate an extractor starts from, and the other
 * four are in the registry for it to ask for by object. The tally reports
 * the per-source sum and the distinct sum separately, because a layer cited
 * by two sources is read twice and exists once.
 */
import { usable } from "./sanity";
import type { CoverageBucket, LayerRecord, SanityVerdict } from "./types";
import { coverageBuckets } from "./types";

/** What the coverage reader needs from a fetch receipt. The archive lane's
 * full receipt satisfies this, and so does a fixture. */
export interface ReceiptFact {
  source_id: string;
  outcome: "stored" | "not_artifact" | "failed";
  sha256: string | null;
  reason: string | null;
  source_class: string;
}

/** Why a held object produced no layer, from the registry build. */
export interface UnsupportedFact {
  object_sha256: string;
  reason: string;
}

export interface SourceCoverage {
  source_id: string;
  bucket: CoverageBucket;
  /** The object the receipt named, when there is one. */
  object_sha256: string | null;
  /** The best layer under that object, when there is one. */
  layer_sha256: string | null;
  sanity: SanityVerdict | null;
  /** Characters in that layer. Zero when there is none, so the extraction
   * surface is a sum over this column. */
  characters: number;
  source_class: string;
  /** Why this source is where it is, in one line. */
  detail: string;
}

export interface CoverageTally {
  sources: number;
  buckets: Record<CoverageBucket, number>;
  /** Sources whose receipt is missing. Part of no_capture, named apart
   * because it is a fault in the ledger rather than a fact about a host. */
  no_receipt: number;
  /** Characters summed over the sources counted in layer_pass or
   * layer_suspect. A layer serving two sources is counted twice, because
   * this is what the extractor reads: once per source. */
  characters: number;
  /** The same text counted once. Several sources cite one object, so the
   * distinct total is the volume of text that exists and the per-source
   * total is the volume of reading. The two differ and a report that gives
   * only the larger one overstates the corpus. */
  distinct_characters: number;
  /** Distinct layers behind distinct_characters. */
  distinct_layers: number;
  /** The same, per source class. */
  by_class: Record<string, { sources: number; usable: number; characters: number }>;
}

export interface CoverageResult {
  rows: SourceCoverage[];
  tally: CoverageTally;
  /** Empty when the identity holds. One line per breach otherwise. */
  problems: string[];
}

const rank: Record<SanityVerdict, number> = { pass: 0, suspect: 1, fail: 2 };

const bucketOfVerdict = (verdict: SanityVerdict): CoverageBucket =>
  verdict === "pass" ? "layer_pass" : verdict === "suspect" ? "layer_suspect" : "layer_fail";

/**
 * The bucket for every source, and the tally.
 *
 * `sourceIds` is the full set from the store, which is what the identity is
 * asserted against. `receipts` is the latest receipt per source.
 */
export function coverageOf(
  sourceIds: string[],
  receipts: Map<string, ReceiptFact>,
  registry: LayerRecord[],
  unsupported: UnsupportedFact[] = [],
): CoverageResult {
  const byObject = new Map<string, LayerRecord[]>();
  for (const record of registry) {
    const held = byObject.get(record.object_sha256);
    if (held) held.push(record);
    else byObject.set(record.object_sha256, [record]);
  }
  const reasonOf = new Map<string, string[]>();
  for (const entry of unsupported) {
    const held = reasonOf.get(entry.object_sha256);
    if (held) {
      if (!held.includes(entry.reason)) held.push(entry.reason);
    } else reasonOf.set(entry.object_sha256, [entry.reason]);
  }

  const rows: SourceCoverage[] = [];
  let missingReceipts = 0;
  for (const sourceId of [...sourceIds].sort()) {
    const receipt = receipts.get(sourceId);
    if (!receipt) {
      missingReceipts += 1;
      rows.push({
        source_id: sourceId,
        bucket: "no_capture",
        object_sha256: null,
        layer_sha256: null,
        sanity: null,
        characters: 0,
        source_class: "unknown",
        detail: "no fetch receipt names this source",
      });
      continue;
    }
    const base = { source_id: sourceId, source_class: receipt.source_class };
    if (receipt.outcome === "failed") {
      rows.push({
        ...base,
        bucket: "no_capture",
        object_sha256: null,
        layer_sha256: null,
        sanity: null,
        characters: 0,
        detail: `the fetch failed: ${receipt.reason ?? "no reason recorded"}`,
      });
      continue;
    }
    if (receipt.outcome === "not_artifact") {
      rows.push({
        ...base,
        bucket: "not_the_artifact",
        object_sha256: receipt.sha256,
        layer_sha256: null,
        sanity: null,
        characters: 0,
        detail: `bytes are held and are not the source: ${receipt.reason ?? "no reason recorded"}`,
      });
      continue;
    }
    const object = receipt.sha256;
    const layers = object ? (byObject.get(object) ?? []) : [];
    if (!layers.length) {
      const reasons = object ? (reasonOf.get(object) ?? []) : [];
      rows.push({
        ...base,
        bucket: "no_normaliser",
        object_sha256: object,
        layer_sha256: null,
        sanity: null,
        characters: 0,
        detail: reasons.length ? reasons.sort().join("; ") : "the held bytes produced no text layer",
      });
      continue;
    }
    const best = [...layers].sort((a, b) =>
      rank[a.sanity] !== rank[b.sanity]
        ? rank[a.sanity] - rank[b.sanity]
        : b.metrics.characters - a.metrics.characters || (a.layer_sha256 < b.layer_sha256 ? -1 : 1),
    )[0];
    rows.push({
      ...base,
      bucket: bucketOfVerdict(best.sanity),
      object_sha256: object,
      layer_sha256: best.layer_sha256,
      sanity: best.sanity,
      characters: usable(best.sanity) ? best.metrics.characters : 0,
      detail: best.sanity === "pass" ? `${best.normaliser}, ${best.metrics.characters} characters` : best.sanity_reasons.join("; "),
    });
  }

  const buckets = Object.fromEntries(coverageBuckets.map((bucket) => [bucket, 0])) as Record<CoverageBucket, number>;
  const byClass: CoverageTally["by_class"] = {};
  const distinct = new Map<string, number>();
  let characters = 0;
  for (const row of rows) {
    buckets[row.bucket] += 1;
    characters += row.characters;
    if (row.layer_sha256 && row.characters > 0) distinct.set(row.layer_sha256, row.characters);
    const held = (byClass[row.source_class] ??= { sources: 0, usable: 0, characters: 0 });
    held.sources += 1;
    held.characters += row.characters;
    if (row.bucket === "layer_pass" || row.bucket === "layer_suspect") held.usable += 1;
  }
  let distinctCharacters = 0;
  for (const value of distinct.values()) distinctCharacters += value;

  const problems: string[] = [];
  const sum = coverageBuckets.reduce((total, bucket) => total + buckets[bucket], 0);
  if (sum !== sourceIds.length) problems.push(`the buckets sum to ${sum} and the store holds ${sourceIds.length} sources`);
  if (rows.length !== sourceIds.length) problems.push(`${rows.length} rows for ${sourceIds.length} sources`);
  const seen = new Set<string>();
  for (const row of rows) {
    if (seen.has(row.source_id)) problems.push(`${row.source_id} is in the table twice`);
    seen.add(row.source_id);
  }

  return {
    rows,
    tally: {
      sources: sourceIds.length,
      buckets,
      no_receipt: missingReceipts,
      characters,
      distinct_characters: distinctCharacters,
      distinct_layers: distinct.size,
      by_class: byClass,
    },
    problems,
  };
}
