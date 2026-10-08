/** Serving-data contract between this producer and the website (issue #31).
 * Envelope schema 2, serving contract 1.0. The zod schemas here are the source
 * of truth; docs/serving/schemas/*.json are generated from them. */
import { z } from "zod";

export const ENVELOPE_SCHEMA_VERSION = 2;
export const SERVING_CONTRACT_VERSION = "1.0";
export const ARTIFACT_SCHEMA_VERSION = "1.0";
/** Upper bound on one decoded page document. */
export const MAX_PAGE_BYTES = 1_000_000;
/** Upper bound on one decoded artifact file. */
export const MAX_FILE_BYTES = 16_000_000;
export const RESULTS_LIMIT = 25;
export const EVIDENCE_LIMIT = 10;
export const PAGE_SHARDS = 256;

const sha256 = z.string().regex(/^[a-f0-9]{64}$/);
const safePath = z.string().regex(/^(?!\/)(?!.*\.\.)[A-Za-z0-9_.\/-]+$/);
export const groups = ["bootstrap", "routes", "pages", "browse", "search", "supporting", "downloads"] as const;

export const fileEntrySchema = z.object({
  source: safePath,
  group: z.enum(groups),
  artifact_type: z.string().min(1),
  artifact_schema_version: z.string(),
  encoding: z.enum(["identity", "gzip"]),
  bytes: z.number().int().nonnegative(),
  sha256,
  stored_bytes: z.number().int().nonnegative(),
  stored_sha256: sha256,
}).strict();

export const servingManifestSchema = z.object({
  schema_version: z.literal(ENVELOPE_SCHEMA_VERSION),
  serving_contract_version: z.literal(SERVING_CONTRACT_VERSION),
  record_schema_version: z.string(),
  release_id: z.string().regex(/^\d{4}-\d{2}-\d{2}-[a-f0-9]{12}$/),
  released_at: z.string(),
  catalogue_sha256: sha256,
  generator_sha256: sha256,
  capabilities: z.record(z.enum(groups), z.boolean()),
  counts: z.object({
    records_by_kind: z.record(z.string(), z.number().int()),
    routes_by_kind: z.record(z.string(), z.number().int()),
    alias_routes: z.number().int(),
    pages: z.number().int(),
  }).strict(),
  files: z.array(fileEntrySchema),
}).strict();

const reference = z.object({ id: z.string(), kind: z.string(), name: z.string(), status: z.string() }).strict();

/** A bounded table. `next_cursor` continues it through the release-pinned API. */
const section = <T extends z.ZodTypeAny>(item: T) => z.object({
  items: z.array(item),
  total: z.number().int().nonnegative(),
  limit: z.number().int().positive(),
  next_cursor: z.string().nullable(),
}).strict();

const resultRow = z.object({
  result: z.record(z.string(), z.unknown()),
  evaluation_id: z.string().nullable(),
  origin: z.string(),
  review_status: z.string(),
  links: z.record(z.string(), z.array(z.string())),
}).strict();

export const pageSchema = z.object({
  route_kind: z.string(),
  record_id: z.string(),
  canonical_route: z.string(),
  record: z.record(z.string(), z.unknown()),
  direct: z.array(z.object({ relation: z.string(), id: z.string() }).strict()),
  reverse: z.array(z.object({ relation: z.string(), id: z.string() }).strict()),
  source_ids: z.array(z.string()),
  summary: z.object({
    results: z.number().int(),
    evaluations: z.number().int(),
    evidence_rows: z.number().int(),
    published_comparisons: z.number().int(),
    use_case_links: z.number().int(),
  }).strict(),
  sections: z.object({
    results: section(resultRow),
    evaluations: z.record(z.string(), z.record(z.string(), z.unknown())),
    evidence: section(z.record(z.string(), z.unknown())),
    published_comparisons: z.array(z.record(z.string(), z.unknown())),
    use_case_links: z.array(z.record(z.string(), z.unknown())),
  }).strict(),
  references: z.record(z.string(), reference),
}).strict();

export const pageShardSchema = z.object({
  release_id: z.string(),
  artifact_schema_version: z.literal(ARTIFACT_SCHEMA_VERSION),
  shard: z.string(),
  pages: z.record(z.string(), pageSchema),
}).strict();

export const routeSchema = z.object({
  route: z.string(),
  route_kind: z.string(),
  record_id: z.string(),
  canonical_route: z.string(),
  alias: z.boolean(),
  page_shard: z.string(),
  status: z.string(),
}).strict();

export const routesSchema = z.object({
  release_id: z.string(),
  artifact_schema_version: z.literal(ARTIFACT_SCHEMA_VERSION),
  route_kind: z.string(),
  routes: z.array(routeSchema),
}).strict();

export const bootstrapSchema = z.object({
  release_id: z.string(),
  released_at: z.string(),
  artifact_schema_version: z.literal(ARTIFACT_SCHEMA_VERSION),
  counts: z.object({
    records_by_kind: z.record(z.string(), z.number().int()),
    results_by_review_status: z.record(z.string(), z.number().int()),
    evaluations_by_origin: z.record(z.string(), z.number().int()),
  }).strict(),
  facets: z.record(z.string(), z.unknown()),
}).strict();

export const downloadsSchema = z.object({
  release_id: z.string(),
  artifact_schema_version: z.literal(ARTIFACT_SCHEMA_VERSION),
  url_template: z.string(),
  files: z.array(z.object({ name: z.string(), sha256, archive_path: z.string() }).strict()),
  historical_receipts: z.array(z.string()),
}).strict();

export const schemas = {
  "manifest": servingManifestSchema,
  "page-shard": pageShardSchema,
  "routes": routesSchema,
  "bootstrap": bootstrapSchema,
  "downloads": downloadsSchema,
} as const;
