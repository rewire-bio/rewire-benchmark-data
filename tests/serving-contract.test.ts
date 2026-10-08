import fs from "node:fs";
import { describe, expect, it } from "vitest";
import { buildPages, buildServing, jsonSchemas, schemaDir } from "../scripts/serving/build";
import { MAX_PAGE_BYTES, pageSchema, pageShardSchema, servingManifestSchema } from "../scripts/serving/contract";
import { buildRelease } from "../scripts/omics/release";
import { createCatalogueQuery } from "../services/omics/src/catalogue-query";
import { records } from "./helpers/records";

const snapshot = buildRelease(records, "2026-10-07T00:00:00Z", { entity_schema_version: "1.1" }).snapshot;
const visible = snapshot.records.filter((r) => r.status !== "excluded");
const alias = visible.find((r) => Array.isArray(r.attributes.legacy_kinds) && r.attributes.legacy_kinds.length)!;
const query = createCatalogueQuery(snapshot);
const busiest = [...visible].filter((r) => r.kind === "benchmark")
  .sort((a, b) => query.results({ id: b.id, limit: 1 }).total - query.results({ id: a.id, limit: 1 }).total)[0];
const sample = new Set([alias.id, busiest.id, ...visible.filter((_, i) => i % 1500 === 0).map((r) => r.id)]);

describe("serving contract schemas", () => {
  it("keeps the committed JSON Schemas in step with the contract", () => {
    for (const [name, schema] of Object.entries(jsonSchemas()))
      expect(JSON.parse(fs.readFileSync(`${schemaDir}/${name}`, "utf8")), name).toEqual(schema);
  });

  it("accepts the valid fixture and rejects a page without a table total", () => {
    const read = (name: string) => JSON.parse(fs.readFileSync(`docs/serving/fixtures/${name}`, "utf8"));
    expect(pageShardSchema.safeParse(read("page-shard.valid.json")).success).toBe(true);
    expect(pageShardSchema.safeParse(read("page-shard.invalid-missing-total.json")).success).toBe(false);
  });
});

describe("prepared pages", () => {
  const { pages } = buildPages(snapshot, undefined, sample);

  it("builds a valid, bounded page for each sampled record", () => {
    expect(pages.map((p) => p.record_id).sort()).toEqual([...sample].sort());
    for (const page of pages) {
      expect(pageSchema.safeParse(page).success, page.record_id).toBe(true);
      expect(Buffer.byteLength(JSON.stringify(page))).toBeLessThanOrEqual(MAX_PAGE_BYTES);
    }
  });

  it("keeps totals and a continuation cursor instead of silently truncating", () => {
    const page = pages.find((p) => p.record_id === busiest.id)!;
    const { results } = page.sections;
    expect(results.total).toBe(query.results({ id: busiest.id, limit: 1 }).total);
    expect(results.total).toBeGreaterThan(results.items.length);
    expect(results.next_cursor).toBeTruthy();
    expect(query.results({ id: busiest.id, limit: results.limit, cursor: results.next_cursor! }).items.length).toBeGreaterThan(0);
  });

  it("resolves every referenced ID and embeds no related record twice", () => {
    for (const page of pages) {
      const ids = [
        ...page.direct.map((d) => d.id), ...page.reverse.map((r) => r.id), ...page.source_ids,
        ...page.sections.results.items.flatMap((row) => [row.evaluation_id ?? [], ...Object.values(row.links).flat()].flat()),
      ];
      for (const id of ids) expect(page.references[id], `${page.record_id} -> ${id}`).toBeDefined();
    }
  });
});

describe("serving manifest", () => {
  const build = () => buildServing({
    snapshot, catalogueBytes: Buffer.from(JSON.stringify(snapshot)), releaseManifest: { files: {} },
    receipts: [], generatorSha256: "0".repeat(64), only: sample,
  });
  const first = build();

  it("declares versions, capabilities and every file with decoded and stored hashes", () => {
    expect(servingManifestSchema.safeParse(first.manifest).success).toBe(true);
    expect(first.manifest.capabilities).toMatchObject({ pages: true, routes: true, search: false, browse: false });
    expect(first.manifest.counts.alias_routes).toBeGreaterThan(0);
    expect(new Set(first.manifest.files.map((f) => f.source)).size).toBe(first.manifest.files.length);
  });

  it("is deterministic", () => {
    expect(build().manifest).toEqual(first.manifest);
  });

  it("routes alias kinds to the canonical page", () => {
    const routes = first.files.filter((f) => f.entry.group === "routes");
    expect(routes.length).toBeGreaterThan(0);
    expect(first.manifest.counts.routes_by_kind[alias.kind]).toBeGreaterThan(0);
  });
});
