/** The archive contract: object manifest rows, fetch receipts and the small
 * vocabularies both of them draw on.
 *
 * Three pieces of work share this file. The fetcher (scripts/archive/) writes
 * exact-bytes objects and receipts. The text layer work writes derived objects
 * beside them. The licence work decides a tier for an object and nothing here
 * decides one for it: the default is the most restrictive tier, and a caller
 * passes a classifier in.
 *
 * Layout is ADR 0004's. An object is keyed on the sha256 of its expanded
 * bytes, the manifest is committed at data/archive/objects/<0-f>.jsonl sorted
 * by that key, and the shard is the key's first hex digit.
 */
import { z } from "zod";

/** What an object holds. ADR 0004: anything but exact-bytes is derived and
 * must name the container it came from and the command that produced it. */
export const layers = ["exact-bytes", "archive-member", "text-layer", "canonical-json", "warc"] as const;
export type Layer = (typeof layers)[number];

/** Which backend holds the bytes. local-cache is the gitignored working copy
 * every object starts in; the others are added when a credential exists.
 *
 * `store` on a row names the one authoritative home, and `mirrors` names the
 * derived copies. R2 is the home for every object the archive holds, whatever
 * its tier: the bucket is the archive, and a release asset is a convenience
 * copy of the public subset that can be deleted and rebuilt from the bucket
 * without losing anything. Before 2026-11-19 the two backends were peers,
 * `store` named whichever one a command had last written to, and the archive
 * had no single place that held all of it. */
export const stores = ["local-cache", "github-release", "r2"] as const;
export type Store = (typeof stores)[number];

export const visibilities = ["public", "restricted"] as const;
export type Visibility = (typeof visibilities)[number];

/** ADR 0003's six licence archiveTiers. They govern publication, never possession. */
export const archiveTiers = ["t0-public", "t1-public-nc", "t2-verbatim-nd", "t3-verbatim-nd-nc", "t4-private", "t5-no-store"] as const;
export type ArchiveTier = (typeof archiveTiers)[number];

/** Whether an object predates the licence policy. */
export const exposures = ["policy", "pre-policy"] as const;
export type Exposure = (typeof exposures)[number];

/** The four routes, in the order the fetcher tries them. No route circumvents
 * access control: each one asks a public service for a copy it may serve. */
export const routes = ["direct", "unpaywall", "europepmc", "preprint"] as const;
export type Route = (typeof routes)[number];

/** Why a route, or a whole source, produced no artifact. One vocabulary for
 * both, so a receipt's reason and its per-route reasons read the same way.
 *
 * The first thirteen are "no bytes arrived". The last three are "bytes
 * arrived and they are not the artifact", which is the distinction the 2026
 * pilot forced: four of thirty-eight stored objects were cookie walls or
 * landing pages that a 200 had called a success. They are set by
 * checkArtifact in ./artifact. */
export const reasons = [
  "http_error",
  "network_error",
  "timeout",
  "empty_body",
  "too_large",
  "not_found",
  "rate_limited",
  "host_stopped",
  "no_doi",
  "no_open_copy",
  "unpaywall_no_email",
  "paywalled_not_held",
  "unsupported_url",
  "interstitial_body",
  "text_below_threshold",
  "publisher_html_only",
] as const;
export type Reason = (typeof reasons)[number];

/** What a receipt says the archive came away with.
 *
 * stored means we hold the artifact. not_artifact means we hold bytes that
 * are demonstrably not it: a cookie wall, a page that renders to nothing, or
 * a publisher's HTML standing in for a PDF or a JATS XML no route reached.
 * The bytes are kept either way, because what a host served is a fact worth
 * holding, but only stored counts as the source being held. */
export const outcomes = ["stored", "not_artifact", "failed"] as const;
export type Outcome = (typeof outcomes)[number];

/** The host-behaviour class a source's treatment is keyed on. */
export const sourceClasses = [
  "europepmc-api",
  "pmc",
  "arxiv",
  "preprint-server",
  "publisher",
  "code-repository",
  "model-hub",
  "data-repository",
  "other-web",
] as const;
export type SourceClass = (typeof sourceClasses)[number];

/** Which archiveTiers may reach a public backend.
 *
 * Four of the six publish. The owner determinations of 2026-11-17 settle the
 * two that used to be refused here, and docs/source-preservation.md carries
 * both with the premise each rests on.
 *
 * Determination 1 reads our use as NonCommercial under CC 4.0, so the two
 * non-commercial archiveTiers publish non-commercially. Determination 2 reads a text
 * layer as a technical modification across formats rather than adapted
 * material, so a no-derivatives work publishes verbatim and its text layer
 * publishes with it. That is what makes t2-verbatim-nd behave like t0-public
 * and t3-verbatim-nd-nc like t1-public-nc for visibility, while the archiveTiers
 * stay distinct: they record a different permission and a different premise.
 *
 * t4-private is store only and t5-no-store keeps no copy, so those two stay
 * restricted.
 *
 * Determination 1 falls if its premise falls. If any part of this data is
 * ever sold, licensed to a partner or paywalled, t1-public-nc and
 * t3-verbatim-nd-nc have to be determined again from the licence text and
 * this function changes with them.
 */
export const visibilityOf = (tier: ArchiveTier): Visibility =>
  tier === "t4-private" || tier === "t5-no-store" ? "restricted" : "public";

/** The tier an object gets when no licence has been determined. ADR 0003:
 * unknown never means public and never means unstored. */
export const defaultArchiveTier: ArchiveTier = "t4-private";

/** What the licence work supplies. It sees the object's provenance and returns
 * a tier with the string the determination was read from. */
export type LicenceClassifier = (input: {
  sourceIds: string[];
  url: string;
  mediaType: string;
}) => { archive_tier: ArchiveTier; observed_licence: string | null; exposure?: Exposure };

const hex64 = z.string().regex(/^[a-f0-9]{64}$/);
const utc = z.string().regex(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,3})?Z$/);
const bytes = z.number().int().min(0);
const text = z.string().min(1);

/** One manifest line. Keys are written sorted, one object per line, shards
 * sorted by sha256. */
export const manifestRowSchema = z
  .object({
    sha256: hex64,
    bytes,
    /** The media type as served, parameters stripped. */
    media_type: text,
    layer: z.enum(layers),
    /** Where the bytes came from: the final URL for a fetch, or a repository
     * path for bytes already committed here. */
    origin: text,
    /** The URL asked for, where it differs from origin. */
    requested_url: z.string().nullable(),
    first_seen_at: utc,
    store: z.enum(stores),
    /** Backends holding a copy of these bytes besides `store`, sorted. A
     * mirror is rebuildable from the home, so losing one loses nothing; a
     * reader that wants the bytes reads `store`. Defaulted so that every row
     * written before this field existed parses as having no mirror, which is
     * what those rows meant. */
    mirrors: z.array(z.enum(stores)).default([]),
    visibility: z.enum(visibilities),
    archive_tier: z.enum(archiveTiers),
    observed_licence: z.string().nullable(),
    exposure: z.enum(exposures),
    /** The container digest a derived layer was produced from. */
    derived_from: hex64.nullable(),
    /** The exact command that produced a derived layer. */
    derivation: z.string().nullable(),
    /** Where these bytes were tracked in git before the archive held them. */
    previous_path: z.string().nullable(),
    /** The source records these bytes answer for. */
    source_ids: z.array(text),
    /** The three takedown columns, determination 4 of 2026-11-17. They are
     * optional because a row that holds bytes carries none of them, and
     * because the rows written before this field existed carry none either.
     *
     * When the bytes were removed on a rights holder's request. The row stays,
     * so the removal is a recorded fact and no later reader finds a silent
     * hole: the key, the byte count, first_seen_at and source_ids are
     * unchanged, and only the bytes are gone. */
    removed_at: utc.optional(),
    /** Why, in one line. Required beside removed_at. */
    removed_reason: text.optional(),
    /** Who asked. The rights holder, or the dated review under docs/reviews/
     * that recorded the request. This file is committed to a public
     * repository, so it names an organisation or a review, never a private
     * person's contact details. Required beside removed_at. */
    removed_requester: text.optional(),
  })
  .strict()
  .superRefine((row, ctx) => {
    if (row.layer !== "exact-bytes" && (!row.derived_from || !row.derivation))
      ctx.addIssue({ code: "custom", message: `layer ${row.layer} needs derived_from and derivation` });
    if (row.layer === "exact-bytes" && (row.derived_from || row.derivation))
      ctx.addIssue({ code: "custom", message: "layer exact-bytes carries no derived_from or derivation" });
    if (row.visibility !== visibilityOf(row.archive_tier))
      ctx.addIssue({ code: "custom", message: `tier ${row.archive_tier} is ${visibilityOf(row.archive_tier)}, not ${row.visibility}` });
    // A removal is a fact with three parts. A date with no reason and no
    // requester records that something happened and loses why and to whom,
    // which is the gap determination 4 names.
    if (row.removed_at && (!row.removed_reason || !row.removed_requester))
      ctx.addIssue({ code: "custom", message: "a removed row carries removed_at, removed_reason and removed_requester" });
    if (!row.removed_at && (row.removed_reason || row.removed_requester))
      ctx.addIssue({ code: "custom", message: "removed_reason and removed_requester belong to a removed row, which carries removed_at" });
    // This is what keeps a removed row out of every publish path. Both
    // uploaders refuse t5-no-store by name, as their first test and before
    // any tier or visibility question, so a removed row is never a candidate
    // for either. Until 2026-11-19 the upload path selected on visibility and
    // this rule leaned on t5-no-store being restricted; the upload path now
    // takes every tier, so that reasoning is gone and the explicit refusal is
    // the whole of it.
    if (row.removed_at && row.archive_tier !== "t5-no-store")
      ctx.addIssue({ code: "custom", message: `a removed row sits at t5-no-store, not ${row.archive_tier}` });
    // A mirror is a second copy, so naming the home again says nothing and
    // naming a backend twice says it twice. Sorted so two manifests that hold
    // the same fact hold the same bytes.
    const sorted = [...row.mirrors].sort();
    if (new Set(row.mirrors).size !== row.mirrors.length || row.mirrors.some((store, at) => store !== sorted[at]))
      ctx.addIssue({ code: "custom", message: `mirrors are sorted and distinct, not ${row.mirrors.join(", ")}` });
    if (row.mirrors.includes(row.store))
      ctx.addIssue({ code: "custom", message: `${row.store} is this row's store, so it is not also a mirror of it` });
    // The release assets are a public tag anyone can read. A restricted row
    // held there would be restricted bytes served to the world, which is the
    // one thing the tiers exist to prevent. The home is checked as well as the
    // mirrors: a rule that covered only the mirrors would refuse the copy and
    // allow the original.
    // Not applied to a removed row. Its visibility is a consequence of the t5 tier rather than
    // a statement about bytes, which no longer exist anywhere, and its store is the historical
    // note of where they were. A rule that covered it would make a published object
    // untakedownable, and a takedown has to work whatever else a row says.
    if (!row.removed_at && row.visibility === "restricted" && (row.store === "github-release" || row.mirrors.includes("github-release")))
      ctx.addIssue({
        code: "custom",
        message: `tier ${row.archive_tier} is restricted, so a public release is neither its home nor a mirror of it`,
      });
    // Removed bytes are gone from every backend, so a mirror of them is a
    // claim that a copy survived the takedown.
    if (row.removed_at && row.mirrors.length > 0)
      ctx.addIssue({ code: "custom", message: `a removed row keeps no copy, so it names no mirror, not ${row.mirrors.join(", ")}` });
  });
export type ManifestRow = z.infer<typeof manifestRowSchema>;

/** Whether a row's bytes were removed on request. The tier says the same
 * thing for publication, because removed_at forces t5-no-store; this reads
 * the removal itself, for a message that has to name the date. */
export const isRemoved = (row: Pick<ManifestRow, "removed_at">): boolean => Boolean(row.removed_at);

/** One attempt at one route, kept whether it worked or not, so that "tried in
 * this order" is a checkable claim rather than a description. */
export const routeAttemptSchema = z
  .object({
    route: z.enum(routes),
    url: z.string().nullable(),
    status: z.number().int().nullable(),
    reason: z.enum(reasons).nullable(),
  })
  .strict();
export type RouteAttempt = z.infer<typeof routeAttemptSchema>;

/** The fetch receipt. Written for a failure as well as a success, because a
 * source we could not get is a fact the recollection needs. */
export const fetchReceiptSchema = z
  .object({
    schema_version: z.literal(1),
    source_id: text,
    requested_url: text,
    /** The URL after redirects, absent when nothing answered. */
    final_url: z.string().nullable(),
    http_status: z.number().int().nullable(),
    fetched_at: utc,
    /** The Content-Type header exactly as served. */
    content_type: z.string().nullable(),
    bytes: bytes.nullable(),
    sha256: hex64.nullable(),
    /** The route that produced the bytes, absent on a failure. */
    route: z.enum(routes).nullable(),
    routes_tried: z.array(routeAttemptSchema),
    outcome: z.enum(outcomes),
    reason: z.enum(reasons).nullable(),
    source_class: z.enum(sourceClasses),
  })
  .strict()
  .superRefine((receipt, ctx) => {
    // stored and not_artifact both hold bytes, so both name them. failed
    // holds none. Only stored needs no reason: the other two exist to say
    // what went wrong, so a missing reason there would lose the finding.
    if (receipt.outcome !== "failed" && (!receipt.sha256 || receipt.bytes === null || !receipt.route))
      ctx.addIssue({ code: "custom", message: `a ${receipt.outcome} receipt carries sha256, bytes and route` });
    if (receipt.outcome !== "stored" && !receipt.reason)
      ctx.addIssue({ code: "custom", message: `a ${receipt.outcome} receipt carries a reason` });
    if (receipt.outcome === "stored" && receipt.reason)
      ctx.addIssue({ code: "custom", message: "a stored receipt carries no reason" });
  });
export type FetchReceipt = z.infer<typeof fetchReceiptSchema>;

/** The manifest shard a key belongs to: ADR 0004's first hex digit. */
export const objectShard = (sha256: string): string => {
  if (!/^[a-f0-9]{64}$/.test(sha256)) throw new Error(`Not a sha256 key: ${sha256}`);
  return sha256[0];
};
export const objectShards = "0123456789abcdef".split("");

/** JSON with keys in sorted order, which is what both files are written in. */
export const canonicalLine = (value: Record<string, unknown>): string =>
  JSON.stringify(Object.fromEntries(Object.entries(value).sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))));

/** A Content-Type header reduced to its media type. The raw header stays on
 * the receipt; the manifest carries this. */
export const mediaTypeOf = (header: string | null | undefined): string => {
  const value = (header ?? "").split(";")[0].trim().toLowerCase();
  return value || "application/octet-stream";
};

/** A UTC timestamp to the second, which is the only form either file holds. */
export const utcNow = (now = new Date()): string => `${now.toISOString().slice(0, 19)}Z`;
