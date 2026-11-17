/** npm run archive -- reclassify: make a resolved licence real.
 *
 * Every manifest row carries the tier the classifier gave it at fetch time.
 * A later run of the licence map, or a licence the resolver found, changes
 * nothing on its own: the row still says what it said when the bytes landed.
 * This command re-runs the classifier over every row with the licence map as
 * it stands today and the candidates on disk, and writes back the three
 * columns a licence decides and no others.
 *
 * What moves: archive_tier, visibility and observed_licence, through
 * updateRow() in ./manifest. What never moves: sha256, bytes, media_type,
 * layer, origin, requested_url, first_seen_at, store, exposure, derived_from,
 * derivation, previous_path, source_ids and the three removal fields. The
 * bytes are not read and nothing is fetched.
 *
 * Three rules, and tests/archive-reclassify.test.ts holds each of them.
 *
 * 1. A row only ever moves to a tier the classifier can justify from
 *    evidence. Evidence is a licence string with a row in the map, read off
 *    the source record or off what a service served. A row whose sources
 *    produce no evidence at all keeps the tier it has: absence is not a
 *    determination, and reading it as one would quietly re-privatise rows
 *    that an earlier reviewed map made public.
 * 2. A human-recorded licence always beats a candidate. If a source record
 *    carries a licence string, that string decides the source's tier, mapped
 *    or not, and no candidate is consulted for it. A candidate is a service's
 *    statement nobody has reviewed; attributes.licence is a determination
 *    somebody signed.
 * 3. A row that would move from public to restricted is a takedown, not a
 *    reclassification. Its bytes may already be a release asset, so this
 *    command reports every such row on its own and refuses to write any of
 *    them. The takedown path in docs/source-preservation.md, markRemoved()
 *    and the asset delete, is what removes a published object, and it records
 *    who asked and why. A restrictive move makes the whole run exit non-zero
 *    so it cannot pass unnoticed.
 *
 * A row at t5-no-store is skipped before any of that. The tier is a recorded
 * decision not to hold bytes, so a classifier reading of a licence must never
 * lift a row out of it.
 */
import {
  archiveTiers,
  isRemoved,
  visibilityOf,
  defaultArchiveTier,
  type ArchiveTier,
  type ManifestRow,
  type Visibility,
} from "../../shared/archive/schema";
import { readManifest, updateRow } from "./manifest";
import { determineForSource, readLicenceMap, readSourceLicences, stricterTier, type LicenceRow } from "../licence/map";
import { buildCandidate, readCandidates, type Candidate } from "../licence/resolve";

/** How one source record's tier was arrived at, for a reader of the plan. */
export type Evidence = "recorded-licence" | "candidate" | "none";

export interface SourceReading {
  source_id: string;
  archive_tier: ArchiveTier;
  observed_licence: string | null;
  evidence: Evidence;
}

/** The tier one source record justifies today.
 *
 * Rule 2 is the shape of this function. The recorded licence is asked first
 * and its answer is returned whether the map covers the string or not: an
 * unmapped recorded string is a determination the map has not read yet, which
 * is a reason to leave the source private and report the string, not a reason
 * to let a service's guess stand in for it.
 *
 * The candidate is re-read against the map passed in, never against the tier
 * stored in the candidates file. That file was written against the map as it
 * stood when the resolver ran, so its status, family and archive_tier are
 * stale the moment a row is added. buildCandidate() does the re-reading, so
 * the resolver's own rules hold here too: a tier comes from the map alone, and
 * two services whose families disagree resolve to nothing.
 */
export function readSource(input: {
  sourceId: string;
  map: Map<string, LicenceRow>;
  licences: Map<string, string | null>;
  candidates: Map<string, Candidate>;
}): SourceReading {
  const { sourceId, map, licences, candidates } = input;
  const recorded = determineForSource(sourceId, map, licences);
  if (recorded.reason === "licence-map" || recorded.reason === "unmapped-licence")
    return { source_id: sourceId, archive_tier: recorded.archive_tier, observed_licence: recorded.observed_licence, evidence: "recorded-licence" };

  const held = candidates.get(sourceId);
  if (held) {
    const reread = buildCandidate({
      target: {
        source_id: sourceId,
        url: "",
        host: "",
        doi: null,
        recorded_licence: null,
        recorded_tier: recorded.archive_tier,
        keys: {},
      },
      observations: held.observations,
      map,
    });
    if (reread?.status === "resolved" && reread.archive_tier)
      return { source_id: sourceId, archive_tier: reread.archive_tier, observed_licence: reread.observed_licence, evidence: "candidate" };
  }
  return { source_id: sourceId, archive_tier: recorded.archive_tier, observed_licence: recorded.observed_licence, evidence: "none" };
}

export interface RowReading {
  archive_tier: ArchiveTier;
  observed_licence: string | null;
  /** Whether anything justified the tier, rather than the private default
   * standing in for a licence nobody has determined. */
  evidenced: boolean;
  sources: SourceReading[];
}

/** The tier one object justifies: the most restrictive of its sources, which
 * is the rule licenceClassifier() already applies when several records share
 * one set of bytes. */
export function readRow(input: {
  sourceIds: string[];
  map: Map<string, LicenceRow>;
  licences: Map<string, string | null>;
  candidates: Map<string, Candidate>;
}): RowReading {
  const sources = input.sourceIds.map((sourceId) => readSource({ ...input, sourceId }));
  let tier: ArchiveTier | null = null;
  let observed: string | null = null;
  for (const source of sources)
    if (tier === null || stricterTier(tier, source.archive_tier) !== tier) {
      tier = source.archive_tier;
      observed = source.observed_licence;
    }
  return {
    archive_tier: tier ?? defaultArchiveTier,
    observed_licence: tier === null ? null : observed,
    evidenced: sources.some((source) => source.evidence !== "none"),
    sources,
  };
}

export interface Move {
  sha256: string;
  from: ArchiveTier;
  to: ArchiveTier;
  from_visibility: Visibility;
  to_visibility: Visibility;
  observed_licence: string | null;
  previous_observed_licence: string | null;
  store: string;
  source_ids: string[];
  evidence: Evidence[];
}

export interface ReclassifyPlan {
  manifest_rows: number;
  /** Rows at t5-no-store, skipped before any reading. */
  skipped_removed: number;
  /** Rows whose sources justify nothing, left exactly as they are. */
  unevidenced: number;
  before: Record<string, number>;
  after: Record<string, number>;
  /** Every move, keyed "<from> to <to>". */
  moves_by_tier: Record<string, number>;
  moves: Move[];
  /** The subset of moves that take a row from public to restricted. Reported
   * apart and never written: those bytes may already be a release asset. */
  restrictive: Move[];
  /** Moves to a more restrictive tier that stay publishable, for example
   * t0-public to t3-verbatim-nd-nc. They are not a takedown and do not block
   * the run, but the bytes may already be a release asset carrying the old
   * tier, so they are listed rather than left as a count. */
  tightening: Move[];
  /** Rows the manifest calls public after the plan is applied. */
  publishable_after: number;
  publishable_before: number;
}

const emptyDistribution = (): Record<string, number> => Object.fromEntries(archiveTiers.map((tier) => [tier, 0]));

/** Read the whole manifest and work out what each row should say. Pure: no
 * write, no network, so the dry run and the real run plan identically. */
export function planReclassify(root = "."): ReclassifyPlan {
  const manifest = readManifest(root);
  const map = readLicenceMap(root);
  const licences = readSourceLicences(root);
  const candidates = readCandidates(root);

  const before = emptyDistribution();
  const after = emptyDistribution();
  const movesByTier: Record<string, number> = {};
  const moves: Move[] = [];
  const restrictive: Move[] = [];
  const tightening: Move[] = [];
  let skippedRemoved = 0;
  let unevidenced = 0;
  let publishableBefore = 0;
  let publishableAfter = 0;

  for (const key of [...manifest.keys()].sort()) {
    const row = manifest.get(key) as ManifestRow;
    before[row.archive_tier] += 1;
    if (row.visibility === "public") publishableBefore += 1;

    // A removed row is a recorded decision, not a licence reading.
    if (row.archive_tier === "t5-no-store" || isRemoved(row)) {
      skippedRemoved += 1;
      after[row.archive_tier] += 1;
      if (visibilityOf(row.archive_tier) === "public") publishableAfter += 1;
      continue;
    }

    const reading = readRow({ sourceIds: row.source_ids, map, licences, candidates });
    // Rule 1. Nothing justified a tier, so the row keeps the one it has.
    const tier = reading.evidenced ? reading.archive_tier : row.archive_tier;
    const observed = reading.evidenced ? reading.observed_licence : row.observed_licence;
    if (!reading.evidenced) unevidenced += 1;

    after[tier] += 1;
    if (visibilityOf(tier) === "public") publishableAfter += 1;
    if (tier === row.archive_tier) continue;

    const move: Move = {
      sha256: key,
      from: row.archive_tier,
      to: tier,
      from_visibility: row.visibility,
      to_visibility: visibilityOf(tier),
      observed_licence: observed,
      previous_observed_licence: row.observed_licence,
      store: row.store,
      source_ids: row.source_ids,
      evidence: reading.sources.map((source) => source.evidence),
    };
    moves.push(move);
    const pair = `${move.from} to ${move.to}`;
    movesByTier[pair] = (movesByTier[pair] ?? 0) + 1;
    if (move.from_visibility === "public" && move.to_visibility === "restricted") restrictive.push(move);
    else if (stricterTier(move.from, move.to) === move.to && move.to_visibility === "public") tightening.push(move);
  }

  return {
    manifest_rows: manifest.size,
    skipped_removed: skippedRemoved,
    unevidenced,
    before,
    after,
    moves_by_tier: Object.fromEntries(Object.entries(movesByTier).sort()),
    moves,
    restrictive,
    tightening,
    publishable_before: publishableBefore,
    publishable_after: publishableAfter,
  };
}

export interface ReclassifySummary extends ReclassifyPlan {
  dry_run: boolean;
  /** Rows written. Zero on a dry run, and zero on a real run that found a
   * restrictive move. */
  written: number;
  /** Set when a real run wrote nothing because rule 3 refused it. */
  refused: boolean;
}

/** Apply the plan, or report it.
 *
 * A real run with any restrictive move writes nothing at all, rather than
 * writing the safe moves and leaving the operator to notice the rest. The
 * plan is one reading of one map; if part of it is a takedown, the whole
 * reading wants a person before any of it lands.
 */
export async function reclassifyObjects(
  options: { root?: string; dryRun?: boolean; log?: (line: string) => void } = {},
): Promise<ReclassifySummary> {
  const root = options.root ?? ".";
  const dryRun = options.dryRun ?? false;
  const log = options.log ?? (() => undefined);
  const plan = planReclassify(root);
  const summary: ReclassifySummary = { ...plan, dry_run: dryRun, written: 0, refused: false };

  if (dryRun) return summary;
  if (plan.restrictive.length) {
    summary.refused = true;
    log(`refusing to write: ${plan.restrictive.length} row(s) would move from public to restricted, which is a takedown`);
    return summary;
  }
  for (const move of plan.moves) {
    if (await updateRow(move.sha256, { archive_tier: move.to, observed_licence: move.observed_licence }, root)) summary.written += 1;
    log(`${move.sha256} ${move.from} to ${move.to}`);
  }
  return summary;
}
