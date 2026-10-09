/** Check that the prepared release file answers exactly as the live query
 * engine does for the same release: details, results and evidence across
 * cursor pages and filters, list searches and facets, comparisons, research
 * readiness, investigations and use cases. Run after `npm run serving`.
 *   npm run serving:parity
 */
import fs from "node:fs";
import assert from "node:assert/strict";
import { createCatalogueQuery, type CatalogueSnapshot } from "../../services/omics/src/catalogue-query";
import { openPreparedCatalogue } from "../../services/omics/src/prepared-catalogue";
import { createUseCaseQuery } from "../../services/omics/src/use-cases";

type Query = Record<string, (input?: unknown) => unknown>;

export function checkParity(snapshot: CatalogueSnapshot, file: string, useCaseArtifact?: unknown): number {
  const live = createCatalogueQuery(snapshot) as unknown as Query;
  const prepared = openPreparedCatalogue(file);
  const B = prepared as unknown as Query;
  const plain = (value: unknown) => JSON.parse(JSON.stringify(value ?? null));
  let checks = 0;
  const same = (label: string, call: (q: Query) => unknown) => {
    let a: unknown, b: unknown, errorA: unknown, errorB: unknown;
    try { a = call(live); } catch (error) { errorA = String(error); }
    try { b = call(B); } catch (error) { errorB = String(error); }
    assert.deepEqual(errorB, errorA, label);
    assert.deepEqual(plain(b), plain(a), label);
    checks++;
  };
  // Walk a paged call through up to `pages` pages using its next cursor.
  const walk = (label: string, input: Record<string, unknown>, method: string, pages = 3) => {
    let cursor: string | undefined;
    for (let page = 0; page < pages; page++) {
      const current = cursor;
      const call = (q: Query) => q[method]({ ...input, ...(current ? { cursor: current } : {}) });
      same(`${label} page ${page}`, call);
      cursor = ((call(live) as { next_cursor?: string | null }).next_cursor) || undefined;
      if (!cursor) break;
    }
  };
  const records = snapshot.records.filter((record) => record.status !== "excluded");
  const busiest = [...records]
    .map((record) => ({ id: record.id, total: (live.results({ id: record.id, limit: 1 }) as { total: number }).total }))
    .sort((a, b) => b.total - a.total || a.id.localeCompare(b.id))
    .slice(0, 3)
    .map((item) => item.id);
  const sample = [...new Set([...busiest, ...records.filter((_, index) => index % 199 === 0).map((record) => record.id)])];
  same("release", (q) => q.release());
  for (const id of sample) {
    same(`record ${id}`, (q) => q.record(id));
    same(`get ${id}`, (q) => q.get({ id, include_comparisons: false }));
    same(`get+panels ${id}`, (q) => q.get({ id }));
    walk(`results ${id}`, { id, limit: 10 }, "results");
    walk(`evidence ${id}`, { id, limit: 10 }, "evidence", 2);
    same(`evidence q ${id}`, (q) => q.evidence({ id, q: "source", limit: 5 }));
    const first = (live.results({ id, limit: 5 }) as { items: { result: { attributes: Record<string, unknown> }; origin: string; protocols: { id: string }[] }[] }).items[0];
    if (first) {
      same(`results metric ${id}`, (q) => q.results({ id, metric: first.result.attributes.metric }));
      same(`results origin ${id}`, (q) => q.results({ id, origin: first.origin }));
      if (first.protocols[0]) same(`results protocol ${id}`, (q) => q.results({ id, protocol_id: first.protocols[0].id }));
    }
    const panel = (live.get({ id }) as { published_comparisons: { id: string }[] } | null)?.published_comparisons[0];
    if (panel) same(`comparison ${id}`, (q) => q.comparison({ id, panel_id: panel.id }));
  }
  for (const input of [{}, { kind: "model" }, { kind: "benchmark", q: "protein" }, { q: "dnabert" },
    { status: "source_checked", kind: "result" }, { area: "protein" }, { kind: "evaluation", origin: "literature" },
    { kind: "result", origin: "rewire" }, { kind: "dataset", readiness: "analysis" }, { q: "  ESM ", limit: 50 }])
    walk(`list ${JSON.stringify(input)}`, input, "list");
  walk("readiness", { limit: 50 }, "researchReadiness");
  same("investigations", (q) => q.investigations({}));
  const resultIds = records.filter((record) => record.kind === "result").slice(0, 120).map((record) => record.id);
  for (let index = 0; index < 40; index++)
    same(`compare ${index}`, (q) => q.compare({ ids: resultIds.slice(index * 3, index * 3 + 2 + (index % 3)) }));
  for (const id of ["does-not-exist"]) {
    same("missing record", (q) => q.record(id));
    same("missing get", (q) => q.get({ id }));
    same("missing results", (q) => q.results({ id }));
  }
  if (useCaseArtifact) {
    const liveCases = createUseCaseQuery(snapshot, useCaseArtifact as never, snapshot.coverage.use_cases as never, live as never);
    const preparedCases = prepared.useCases();
    const artifact = useCaseArtifact as { use_cases: { slug: string }[] };
    for (const { slug } of artifact.use_cases) {
      assert.deepEqual(plain(preparedCases.get({ slug })), plain(liveCases.get({ slug })), `use case ${slug}`);
      checks++;
    }
    for (const input of [{}, { q: "variant" }, { context: "research" as const }]) {
      assert.deepEqual(plain(preparedCases.list(input)), plain(liveCases.list(input)), `use cases ${JSON.stringify(input)}`);
      checks++;
    }
  }
  prepared.close();
  return checks;
}

if (process.argv[1]?.endsWith("parity.ts")) {
  const snapshot = JSON.parse(fs.readFileSync("public/omics/catalogue.json", "utf8")) as CatalogueSnapshot;
  const useCaseFile = `public/omics/releases/${snapshot.release_id}/use-cases.json`;
  const artifact = fs.existsSync(useCaseFile) ? JSON.parse(fs.readFileSync(useCaseFile, "utf8")) : undefined;
  const checks = checkParity(snapshot, `public/serving/catalogue-${snapshot.release_id}.sqlite`, artifact);
  console.log(`Prepared release matches the live query engine: ${checks} checks.`);
}
