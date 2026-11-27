/** npm run use-cases:check-pages: every page of every use case in the built release fits the response budget.
 * Pages each use case to its last page at 20 and at 100 evaluations per page, as the website and
 * the live check do, and fails if any page is over budget or cannot be built. Reads the prepared
 * file (public/serving/catalogue-<release>.sqlite) when it exists, else the release's catalogue
 * and use-case files through the live query engine. Prints each use case's fixed metadata (what
 * every page repeats) and its largest page, against the budget. */
import fs from "node:fs";
import type { CatalogueSnapshot } from "../../shared/omics/catalogue-query";
import { openPreparedCatalogue } from "../../shared/omics/prepared-catalogue";
import { createUseCaseQuery, MAX_USE_CASE_RESPONSE_BYTES } from "../../shared/omics/use-cases";

const wrapped = (value: unknown) => Buffer.byteLength(JSON.stringify({ result: { data: value } }));
const snapshot = JSON.parse(fs.readFileSync("public/omics/catalogue.json", "utf8")) as CatalogueSnapshot;
const release = snapshot.release_id;
const artifactFile = `public/omics/releases/${release}/use-cases.json`;
if (!fs.existsSync(artifactFile)) {
  console.log(`${release} has no use cases.`);
  process.exit(0);
}
const artifact = JSON.parse(fs.readFileSync(artifactFile, "utf8"));
const preparedFile = `public/serving/catalogue-${release}.sqlite`;
const prepared = fs.existsSync(preparedFile) ? openPreparedCatalogue(preparedFile) : null;
type Query = ReturnType<typeof createUseCaseQuery>;
const query: Query = prepared ? (prepared.useCases() as Query) : createUseCaseQuery(snapshot, artifact, snapshot.coverage.use_cases as never);
const percent = (bytes: number) => `${((100 * bytes) / MAX_USE_CASE_RESPONSE_BYTES).toFixed(1)}%`;

let failures = 0;
const rows: { slug: string; fixed: number; largest: number; pages: number }[] = [];
for (const { slug } of artifact.use_cases as { slug: string }[]) {
  let fixed = 0, largest = 0, pages = 0;
  try {
    for (const limit of [20, 100]) {
      let cursor: string | undefined;
      do {
        const page = query.get({ slug, limit, cursor });
        if (!page) throw Error("not served");
        const bytes = wrapped(page);
        if (bytes > MAX_USE_CASE_RESPONSE_BYTES) throw Error(`page of ${bytes} bytes at ${limit} per page`);
        fixed = wrapped({ ...page, mappings: page.mappings.map((m) => ({ ...m, evaluations: [] })), evaluations_next_cursor: null });
        largest = Math.max(largest, bytes);
        pages++;
        cursor = page.evaluations_next_cursor || undefined;
      } while (cursor);
    }
  } catch (error) {
    failures++;
    console.error(`::error::Use case ${slug} cannot be served: ${error instanceof Error ? error.message : error}`);
  }
  rows.push({ slug, fixed, largest, pages });
}
prepared?.close();
rows.sort((a, b) => b.fixed - a.fixed);
console.log(`Use-case pages of ${release} against the ${MAX_USE_CASE_RESPONSE_BYTES}-byte budget (${prepared ? "prepared file" : "live query engine"}):`);
console.log("fixed metadata\tlargest page\tpages\tuse case");
for (const r of rows) console.log(`${r.fixed} (${percent(r.fixed)})\t${r.largest} (${percent(r.largest)})\t${r.pages}\t${r.slug}`);
if (failures) {
  console.error(`${failures} use case(s) cannot be served within the budget; do not publish this release.`);
  process.exit(1);
}
