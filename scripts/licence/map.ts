/** The licence map: an observed licence string to an archive tier.
 *
 * Tiers govern publication and nothing else. Nothing here decides whether a
 * source is fetched, and no caller may use a tier to skip a fetch.
 *
 * data/archive/licence-map.tsv holds one hand-reviewed row per distinct value
 * of attributes.licence on a source record. A string with no row is an error,
 * not a default: tests/licence-map.test.ts fails the build when the store
 * carries one. A source with no licence string at all is a different case and
 * takes t4-private, because an unresolved licence never means public and never
 * means unstored (ADR 0003, docs/source-preservation.md).
 */
import fs from "node:fs";
import path from "node:path";
import { defaultArchiveTier, archiveTiers, type Exposure, type LicenceClassifier, type ArchiveTier } from "../../shared/archive/schema";

export const licenceMapPath = (root = "."): string => path.join(root, "data/archive/licence-map.tsv");
export const sourcesPath = (root = "."): string => path.join(root, "data/entities/sources.jsonl");

export interface LicenceRow {
  /** The licence string exactly as a source record carries it. */
  licence: string;
  /** A concept key in data/vocab/licence-family.ttl. */
  family: string;
  archive_tier: ArchiveTier;
  /** A concept key in data/vocab/licence-basis.ttl. */
  basis: string;
  note: string;
}

export const columns = ["licence", "family", "tier", "basis", "note"] as const;

/** How restrictive a tier is, lowest first, for picking one tier when several
 * sources share an object. It is a judgement, not a lattice: t2 sits below t1
 * because a no-derivatives condition does not restrict what this archive
 * publishes once a text layer counts as a format conversion, while a
 * non-commercial condition rests on a premise that can change. */
const restrictiveness: Record<ArchiveTier, number> = {
  "t0-public": 0,
  "t2-verbatim-nd": 1,
  "t1-public-nc": 2,
  "t3-verbatim-nd-nc": 3,
  "t4-private": 4,
  "t5-no-store": 5,
};

/** The more restrictive of two archiveTiers. */
export const stricterTier = (a: ArchiveTier, b: ArchiveTier): ArchiveTier => (restrictiveness[a] >= restrictiveness[b] ? a : b);

const isTier = (value: string): value is ArchiveTier => (archiveTiers as readonly string[]).includes(value);

/** Parse the map. Comment lines start with #, then one header line, then one
 * row per licence string. Every field is literal: no quoting, no escapes. */
export function readLicenceMap(root = "."): Map<string, LicenceRow> {
  const file = licenceMapPath(root);
  const lines = fs.readFileSync(file, "utf8").split("\n");
  const rows = new Map<string, LicenceRow>();
  let header = false;
  lines.forEach((line, index) => {
    const where = `${file} line ${index + 1}`;
    if (!line.trim() || line.startsWith("#")) return;
    const fields = line.split("\t");
    if (!header) {
      if (fields.join("\t") !== columns.join("\t")) throw new Error(`${where}: expected the header ${columns.join(", ")}`);
      header = true;
      return;
    }
    if (fields.length !== columns.length) throw new Error(`${where}: ${fields.length} columns, expected ${columns.length}`);
    const [licence, family, tier, basis, note] = fields;
    if (!licence) throw new Error(`${where}: the licence column is empty`);
    if (!isTier(tier)) throw new Error(`${where}: "${tier}" is not an archive tier`);
    if (rows.has(licence)) throw new Error(`${where}: a second row for the licence string "${licence}"`);
    rows.set(licence, { licence, family, archive_tier: tier, basis, note });
  });
  if (!header) throw new Error(`${file}: no header row`);
  return rows;
}

/** Every source record's id and the licence string it carries, if any. */
export function readSourceLicences(root = "."): Map<string, string | null> {
  const licences = new Map<string, string | null>();
  for (const line of fs.readFileSync(sourcesPath(root), "utf8").split("\n")) {
    if (!line.trim()) continue;
    const record = JSON.parse(line) as { id: string; kind: string; attributes?: { licence?: unknown } };
    if (record.kind !== "source") continue;
    const licence = record.attributes?.licence;
    licences.set(record.id, typeof licence === "string" && licence.trim() ? licence : null);
  }
  return licences;
}

/** The seven originals committed to this public repository before the policy
 * existed, enumerated in ADR 0003 section 5 and ruled on in determination 3 of
 * 2026-11-17. Their bytes cannot be removed from git history, so the set is
 * recorded rather than cleaned up quietly. */
export const prePolicySourceIds: readonly string[] = [
  "gpn-paper-20261116-source-biorxiv-v3",
  "gpn-paper-20261116-source-pnas-2023",
  "gpn-paper-20261116-source-pnas-2023-si-appendix",
  "phylogpn-2025",
  "phylogpn-20261116-source-supplement",
  "protein-stability-20261009-source-dieckhaus2024",
  "protein-stability-20261009-source-pancotti2022",
];

export interface Determination {
  archive_tier: ArchiveTier;
  /** The licence string the tier was read from, or null when none was found. */
  observed_licence: string | null;
  exposure: Exposure;
  /** Why this tier, for a reader of the manifest row. */
  reason: "licence-map" | "no-licence-recorded" | "no-source-record" | "unmapped-licence";
}

/** The tier for one source record.
 *
 * This never throws. A licence string with no row is a build failure, caught
 * by tests/licence-map.test.ts, but it is not a reason to stop a fetch: the
 * first rule of this policy is that a licence never blocks capture. The object
 * is stored at the private default with the unmapped string recorded beside
 * it, so the manifest row shows which string nobody has mapped. */
export function determineForSource(sourceId: string, map: Map<string, LicenceRow>, licences: Map<string, string | null>): Determination {
  const exposure: Exposure = prePolicySourceIds.includes(sourceId) ? "pre-policy" : "policy";
  if (!licences.has(sourceId)) return { archive_tier: defaultArchiveTier, observed_licence: null, exposure, reason: "no-source-record" };
  const licence = licences.get(sourceId) ?? null;
  if (licence === null) return { archive_tier: defaultArchiveTier, observed_licence: null, exposure, reason: "no-licence-recorded" };
  const row = map.get(licence);
  if (!row) return { archive_tier: defaultArchiveTier, observed_licence: licence, exposure, reason: "unmapped-licence" };
  return { archive_tier: row.archive_tier, observed_licence: licence, exposure, reason: "licence-map" };
}

/** The classifier shared/archive/schema.ts asks the licence work for. An
 * object answers for one or more source records, so it takes the most
 * restrictive tier of them, and it carries pre-policy exposure if any of them
 * is one of the seven. */
export function licenceClassifier(root = "."): LicenceClassifier {
  const map = readLicenceMap(root);
  const licences = readSourceLicences(root);
  return ({ sourceIds }) => {
    // An object nothing claims is private, like an object whose licence nobody
    // has determined. It is stored either way.
    let tier: ArchiveTier | null = null;
    let observed: string | null = null;
    let exposure: Exposure = "policy";
    for (const sourceId of sourceIds) {
      const determination = determineForSource(sourceId, map, licences);
      if (determination.exposure === "pre-policy") exposure = "pre-policy";
      // stricterTier is the rule, and the one the test pins. Inlining the
      // comparison here would be a second copy of it.
      if (tier === null || stricterTier(tier, determination.archive_tier) !== tier) {
        tier = determination.archive_tier;
        observed = determination.observed_licence;
      }
    }
    return { archive_tier: tier ?? defaultArchiveTier, observed_licence: tier === null ? null : observed, exposure };
  };
}
