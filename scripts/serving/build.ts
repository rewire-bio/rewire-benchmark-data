/** Prepare the serving artifacts for the current release (issue #31): one
 * bounded page per record route, route inventories, bootstrap summaries and a
 * download inventory, all derived once here so the website does not rebuild
 * them at startup. Output: public/serving/<release_id>/. Deterministic. */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { gzipSync } from "node:zlib";
import { z } from "zod";
import {
  createCatalogueQuery,
  type CatalogueRecord,
  type CatalogueSnapshot,
  type ResultRow,
} from "../../services/omics/src/catalogue-query";
import { createUseCaseQuery, type UseCaseArtifact, type UseCaseDeclaration } from "../../services/omics/src/use-cases";
import { recordRouteKinds } from "../../services/omics/src/entity-kinds";
import {
  ARTIFACT_SCHEMA_VERSION, ENVELOPE_SCHEMA_VERSION, EVIDENCE_LIMIT, MAX_FILE_BYTES, MAX_PAGE_BYTES,
  PAGE_SHARDS, RESULTS_LIMIT, SERVING_CONTRACT_VERSION, bootstrapSchema, downloadsSchema, groups,
  pageSchema, pageShardSchema, routesSchema, schemas, servingManifestSchema,
} from "./contract";

type Page = z.infer<typeof pageSchema>;
type FileEntry = z.infer<typeof servingManifestSchema>["files"][number];
const sha256 = (bytes: Buffer | string) => crypto.createHash("sha256").update(bytes).digest("hex");
const shardOf = (id: string) => sha256(id).slice(0, 2);
const canonicalRoute = (record: { kind: string; id: string }) => `/database/${record.kind}/${record.id}/`;
const rowLinkKeys = ["models", "benchmarks", "methods", "configurations", "pipelines", "services", "tasks",
  "protocols", "evaluators", "datasets", "dataset_subsets", "sources"] as const;

export function buildPages(
  snapshot: CatalogueSnapshot,
  useCases?: { artifact: UseCaseArtifact; declaration: UseCaseDeclaration },
  only?: Set<string>,
) {
  const query = createCatalogueQuery(snapshot);
  const caseQuery = useCases ? createUseCaseQuery(snapshot, useCases.artifact, useCases.declaration, query) : null;
  const byId = new Map(snapshot.records.map((record) => [record.id, record]));

  function page(record: CatalogueRecord, resultsLimit: number, comparisonsLimit: number): Page {
    const detail = query.get({ id: record.id, include_comparisons: true })!;
    const results = query.results({ id: record.id, limit: resultsLimit });
    const evidence = query.evidence({ id: record.id, limit: EVIDENCE_LIMIT });
    const links = caseQuery ? caseQuery.links({ id: record.id }).items : [];
    const referenced = new Set<string>();
    const ref = (id: string) => (referenced.add(id), id);
    const rows = results.items.map((row: ResultRow) => ({
      result: row.result as unknown as Record<string, unknown>,
      evaluation_id: row.evaluation ? ref(row.evaluation.id) : null,
      origin: row.origin,
      review_status: row.review_status,
      links: Object.fromEntries(rowLinkKeys.map((key) => [key, (row[key] as CatalogueRecord[]).map((r) => ref(r.id))])),
    }));
    const evaluations: Record<string, Record<string, unknown>> = Object.fromEntries(
      results.items.flatMap((row) => row.evaluation ? [[row.evaluation.id, row.evaluation as unknown as Record<string, unknown>]] : []));
    const direct = detail.direct.map((item) => ({ relation: item.relation, id: ref(item.record.id) }));
    const reverse = detail.reverse.map((item) => ({ relation: item.relation, id: ref(item.record.id) }));
    const source_ids = detail.sources.map((source) => ref(source.id));
    return {
      route_kind: record.kind,
      record_id: record.id,
      canonical_route: canonicalRoute(record),
      record: record as unknown as Record<string, unknown>,
      direct,
      reverse,
      source_ids,
      summary: {
        results: results.total,
        evaluations: "evaluation_count" in results ? Number(results.evaluation_count) : Object.keys(evaluations).length,
        evidence_rows: evidence.total,
        published_comparisons: detail.published_comparisons.length,
        use_case_links: links.length,
      },
      sections: {
        results: { items: rows, total: results.total, limit: resultsLimit, next_cursor: results.next_cursor },
        evaluations,
        evidence: { items: evidence.items as unknown as Record<string, unknown>[], total: evidence.total, limit: EVIDENCE_LIMIT, next_cursor: evidence.next_cursor },
        published_comparisons: detail.published_comparisons.slice(0, comparisonsLimit) as unknown as Record<string, unknown>[],
        use_case_links: links as unknown as Record<string, unknown>[],
      },
      references: Object.fromEntries([...referenced].sort().flatMap((id) => {
        const target = byId.get(id);
        return target ? [[id, { id, kind: target.kind, name: target.name, status: target.status }]] : [];
      })),
    };
  }

  /** Shrink the tables of an oversized page; totals and cursors keep the rest reachable. */
  function boundedPage(record: CatalogueRecord): Page {
    for (const [results, comparisons] of [[RESULTS_LIMIT, Infinity], [RESULTS_LIMIT, 5], [10, 1], [1, 0]] as const) {
      const built = page(record, results, comparisons);
      if (Buffer.byteLength(JSON.stringify(built)) <= MAX_PAGE_BYTES) return built;
    }
    throw new Error(`Page for ${record.id} exceeds ${MAX_PAGE_BYTES} bytes even at minimum table sizes`);
  }

  const pages = snapshot.records
    .filter((record) => record.status !== "excluded" && (!only || only.has(record.id)))
    .map(boundedPage);
  return { pages, query };
}

export function buildServing(input: {
  snapshot: CatalogueSnapshot;
  catalogueBytes: Buffer;
  releaseManifest: { files: Record<string, string> };
  receipts: string[];
  useCases?: { artifact: UseCaseArtifact; declaration: UseCaseDeclaration };
  generatorSha256: string;
  /** Build pages for these records only (tests). Routes always cover every record. */
  only?: Set<string>;
}) {
  const { snapshot } = input;
  const release_id = snapshot.release_id;
  const { pages, query } = buildPages(snapshot, input.useCases, input.only);
  const visible = snapshot.records.filter((record) => record.status !== "excluded");
  const documents = new Map<string, { group: (typeof groups)[number]; type: string; value: unknown }>();
  const count = <T,>(items: T[], key: (item: T) => string) =>
    Object.fromEntries([...items.reduce((m, i) => m.set(key(i), (m.get(key(i)) ?? 0) + 1), new Map<string, number>())].sort());

  documents.set("bootstrap.json", { group: "bootstrap", type: "bootstrap", value: bootstrapSchema.parse({
    release_id, released_at: snapshot.released_at, artifact_schema_version: ARTIFACT_SCHEMA_VERSION,
    counts: {
      records_by_kind: count(visible, (r) => r.kind),
      results_by_review_status: count(visible.filter((r) => r.kind === "result"), (r) => r.status),
      evaluations_by_origin: count(visible.filter((r) => r.kind === "evaluation"), (r) => String(r.attributes.origin ?? "unstated")),
    },
    facets: query.release().facets as Record<string, unknown>,
  }) });

  const routes = visible.flatMap((record) => recordRouteKinds(record).map((kind) => ({
    route: `/database/${kind}/${record.id}/`, route_kind: kind, record_id: record.id,
    canonical_route: canonicalRoute(record), alias: kind !== record.kind,
    page_shard: `pages/${shardOf(record.id)}.json`, status: record.status,
  })));
  for (const kind of [...new Set(routes.map((r) => r.route_kind))].sort()) {
    documents.set(`routes/${kind}.json`, { group: "routes", type: "routes", value: routesSchema.parse({
      release_id, artifact_schema_version: ARTIFACT_SCHEMA_VERSION, route_kind: kind,
      routes: routes.filter((r) => r.route_kind === kind).sort((a, b) => (a.record_id < b.record_id ? -1 : 1)),
    }) });
  }

  const shards = new Map<string, Page[]>();
  for (const page of pages) shards.set(shardOf(page.record_id), [...(shards.get(shardOf(page.record_id)) ?? []), page]);
  for (let i = 0; i < PAGE_SHARDS; i++) {
    const shard = i.toString(16).padStart(2, "0");
    const items = (shards.get(shard) ?? []).sort((a, b) => (a.record_id < b.record_id ? -1 : 1));
    documents.set(`pages/${shard}.json`, { group: "pages", type: "page-shard", value: pageShardSchema.parse({
      release_id, artifact_schema_version: ARTIFACT_SCHEMA_VERSION, shard,
      pages: Object.fromEntries(items.map((p) => [p.record_id, p])),
    }) });
  }

  documents.set("downloads.json", { group: "downloads", type: "downloads", value: downloadsSchema.parse({
    release_id, artifact_schema_version: ARTIFACT_SCHEMA_VERSION,
    url_template: "https://raw.githubusercontent.com/rewire-bio/rewire-benchmark-data/{commit}/{archive_path}",
    files: Object.entries(input.releaseManifest.files).sort(([a], [b]) => (a < b ? -1 : 1)).map(([name, digest]) => ({
      name, sha256: digest, archive_path: `data/omics/releases/${release_id}/${name}.gz`,
    })),
    historical_receipts: input.receipts.filter((id) => id !== release_id).sort(),
  }) });

  const files: { entry: FileEntry; stored: Buffer }[] = [];
  for (const [source, doc] of [...documents].sort(([a], [b]) => (a < b ? -1 : 1))) {
    const decoded = Buffer.from(JSON.stringify(doc.value));
    if (decoded.length > MAX_FILE_BYTES) throw new Error(`${source} exceeds ${MAX_FILE_BYTES} bytes`);
    const stored = gzipSync(decoded, { level: 9 });
    files.push({ stored, entry: {
      source: `${source}.gz`, group: doc.group, artifact_type: doc.type, artifact_schema_version: ARTIFACT_SCHEMA_VERSION,
      encoding: "gzip", bytes: decoded.length, sha256: sha256(decoded), stored_bytes: stored.length, stored_sha256: sha256(stored),
    } });
  }
  const manifest = servingManifestSchema.parse({
    schema_version: ENVELOPE_SCHEMA_VERSION,
    serving_contract_version: SERVING_CONTRACT_VERSION,
    record_schema_version: snapshot.schema_version,
    release_id,
    released_at: snapshot.released_at,
    catalogue_sha256: sha256(input.catalogueBytes),
    generator_sha256: input.generatorSha256,
    capabilities: Object.fromEntries(groups.map((g) => [g, ["bootstrap", "routes", "pages", "downloads"].includes(g)])),
    counts: {
      records_by_kind: count(visible, (r) => r.kind),
      routes_by_kind: count(routes, (r) => r.route_kind),
      alias_routes: routes.filter((r) => r.alias).length,
      pages: pages.length,
    },
    files: files.map((f) => f.entry),
  });
  return { manifest, files };
}

export const generatorFiles = [
  "scripts/serving/build.ts", "scripts/serving/contract.ts", "services/omics/src/catalogue-query.ts",
  "services/omics/src/evidence-table.ts", "services/omics/src/use-cases.ts", "services/omics/src/entity-kinds.ts",
];

export const schemaDir = "docs/serving/schemas";
export function jsonSchemas(): Record<string, unknown> {
  return Object.fromEntries(Object.entries(schemas).map(([name, schema]) => [`${name}.schema.json`, z.toJSONSchema(schema)]));
}

if (process.argv[1]?.endsWith("build.ts") && process.argv[2] === "schemas") {
  fs.mkdirSync(schemaDir, { recursive: true });
  for (const [name, schema] of Object.entries(jsonSchemas()))
    fs.writeFileSync(path.join(schemaDir, name), JSON.stringify(schema, null, 2) + "\n");
  console.log(`Wrote ${Object.keys(schemas).length} schemas to ${schemaDir}`);
} else if (process.argv[1]?.endsWith("build.ts")) {
  const catalogueBytes = fs.readFileSync("public/omics/catalogue.json");
  const snapshot = JSON.parse(catalogueBytes.toString("utf8")) as CatalogueSnapshot;
  const releaseManifest = JSON.parse(fs.readFileSync(`public/omics/releases/${snapshot.release_id}/manifest.json`, "utf8"));
  const useCaseFile = `public/omics/releases/${snapshot.release_id}/use-cases.json`;
  const declaration = snapshot.coverage.use_cases as UseCaseDeclaration | undefined;
  const useCases = fs.existsSync(useCaseFile) && declaration
    ? { artifact: JSON.parse(fs.readFileSync(useCaseFile, "utf8")) as UseCaseArtifact, declaration }
    : undefined;
  const receipts = fs.readdirSync("data/omics/releases").filter((n) => n.endsWith(".json")).map((n) => n.slice(0, -5));
  const generatorSha256 = sha256(generatorFiles.map((f) => fs.readFileSync(f, "utf8")).join("\n"));
  const { manifest, files } = buildServing({ snapshot, catalogueBytes, releaseManifest, receipts, useCases, generatorSha256 });
  const out = path.join("public/serving", snapshot.release_id);
  fs.rmSync(out, { recursive: true, force: true });
  for (const { entry, stored } of files) {
    fs.mkdirSync(path.dirname(path.join(out, entry.source)), { recursive: true });
    fs.writeFileSync(path.join(out, entry.source), stored);
  }
  fs.writeFileSync(path.join(out, "manifest.json"), JSON.stringify(manifest, null, 2) + "\n");
  const stored = files.reduce((n, f) => n + f.entry.stored_bytes, 0);
  const decoded = files.reduce((n, f) => n + f.entry.bytes, 0);
  console.log(`Serving ${snapshot.release_id}: ${manifest.counts.pages} pages, ${files.length} files, ${(decoded / 1e6).toFixed(0)} MB decoded, ${(stored / 1e6).toFixed(0)} MB stored`);
}
