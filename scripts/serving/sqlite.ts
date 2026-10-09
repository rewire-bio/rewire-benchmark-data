/** Build the prepared release file the website and API read: one SQLite
 * database per release, holding the live query engine's outputs so that no
 * consumer rebuilds catalogue-wide indexes. Deterministic for a given release,
 * generator and Node SQLite version.
 *   npm run serving            build public/serving/catalogue-<release>.sqlite
 */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { gzipSync } from "node:zlib";
import { createCatalogueQuery, type CatalogueSnapshot } from "../../services/omics/src/catalogue-query";
import { createEvidenceIndex } from "../../services/omics/src/evidence-table";
import { deriveResearchReadiness, getResearch } from "../../services/omics/src/research";
import { useCaseState, type UseCaseArtifact, type UseCaseDeclaration } from "../../services/omics/src/use-cases";
import { PREPARED_CONTRACT_VERSION } from "../../services/omics/src/prepared-catalogue";
import { isBenchmarkSubject, isDatasetSubject } from "../../services/omics/src/entity-kinds";
const { DatabaseSync } = process.getBuiltinModule("node:sqlite");

export const generatorFiles = [
  "scripts/serving/sqlite.ts",
  "services/omics/src/catalogue-query.ts",
  "services/omics/src/evidence-table.ts",
  "services/omics/src/prepared-catalogue.ts",
  "services/omics/src/published-comparisons.ts",
  "services/omics/src/research.ts",
  "services/omics/src/source-identity.ts",
  "services/omics/src/use-cases.ts",
];
const sha256 = (bytes: Buffer | string) => crypto.createHash("sha256").update(bytes).digest("hex");
const gz = (value: unknown) => gzipSync(JSON.stringify(value), { level: 9 });

export function buildPreparedCatalogue(input: {
  snapshot: CatalogueSnapshot;
  catalogueBytes: Buffer;
  useCases?: { artifact: UseCaseArtifact; declaration: UseCaseDeclaration };
  generatorSha256: string;
  file: string;
}) {
  const { snapshot } = input;
  const query = createCatalogueQuery(snapshot);
  fs.rmSync(input.file, { force: true });
  const db = new DatabaseSync(input.file);
  db.exec(`
    PRAGMA page_size = 8192; PRAGMA journal_mode = OFF; PRAGMA synchronous = OFF;
    CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID;
    CREATE TABLE blobs (key TEXT PRIMARY KEY, value BLOB NOT NULL);
    CREATE TABLE records (id TEXT PRIMARY KEY, kind TEXT NOT NULL, status TEXT NOT NULL, json TEXT NOT NULL);
    CREATE INDEX records_kind ON records (kind, id);
    CREATE TABLE details (id TEXT PRIMARY KEY, gz BLOB NOT NULL);
    CREATE TABLE result_rows (result_id TEXT PRIMARY KEY, gz BLOB NOT NULL);
    CREATE TABLE result_index (record_id TEXT NOT NULL, pos INTEGER NOT NULL, result_id TEXT NOT NULL, PRIMARY KEY (record_id, pos)) WITHOUT ROWID;
    CREATE TABLE evidence (record_id TEXT PRIMARY KEY, gz BLOB NOT NULL);
  `);
  const meta = db.prepare("INSERT INTO meta VALUES (?, ?)");
  const blob = db.prepare("INSERT INTO blobs VALUES (?, ?)");
  const insertRecord = db.prepare("INSERT INTO records VALUES (?, ?, ?, ?)");
  const insertDetail = db.prepare("INSERT INTO details VALUES (?, ?)");
  const insertRow = db.prepare("INSERT INTO result_rows VALUES (?, ?)");
  const insertIndex = db.prepare("INSERT INTO result_index VALUES (?, ?, ?)");
  const insertEvidence = db.prepare("INSERT INTO evidence VALUES (?, ?)");

  // The engine's own record set: non-excluded records, ordered by ID.
  const records = snapshot.records
    .filter((record) => record.status !== "excluded")
    .sort((a, b) => a.id.localeCompare(b.id));
  const evidence = createEvidenceIndex(snapshot);
  const counts = { records: 0, details: 0, result_rows: 0, result_index: 0, evidence: 0 };
  const rowsWritten = new Set<string>();
  db.exec("BEGIN");
  for (const record of records) {
    insertRecord.run(record.id, record.kind, record.status, JSON.stringify(record));
    counts.records++;
    const detail = query.get({ id: record.id, include_comparisons: true });
    if (detail) {
      insertDetail.run(record.id, gz(detail));
      counts.details++;
    }
    // All of this record's result rows, in the engine's order. Rows are stored once.
    const rows = [];
    let cursor: string | undefined;
    do {
      const page = query.results({ id: record.id, limit: 100, ...(cursor ? { cursor } : {}) });
      rows.push(...page.items.map((item) => item.result.id));
      cursor = page.next_cursor || undefined;
    } while (cursor);
    rows.forEach((resultId, pos) => insertIndex.run(record.id, pos, resultId));
    counts.result_index += rows.length;
    const evidenceRows = evidence.forRecord(record.id);
    if (evidenceRows.length) {
      insertEvidence.run(record.id, gz(evidenceRows));
      counts.evidence++;
    }
  }
  // Full rows (results() pages compact them; filters need the full form).
  for (const row of query.resultRows()) {
    if (rowsWritten.has(row.result.id)) continue;
    rowsWritten.add(row.result.id);
    insertRow.run(row.result.id, gz(row));
    counts.result_rows++;
  }
  blob.run("list_entries", gz(query.listEntries()));
  blob.run("readiness", gz(deriveResearchReadiness(snapshot)));
  blob.run("research", gz(getResearch(snapshot)));
  blob.run(
    "inactive_assessment_dataset_ids",
    gz(
      snapshot.records
        .filter(
          (record) =>
            (isBenchmarkSubject(record.kind) || isDatasetSubject(record.kind)) &&
            ["superseded", "disputed", "excluded"].includes(record.status),
        )
        .map((record) => record.id)
        .sort(),
    ),
  );
  blob.run(
    "use_cases",
    gz(useCaseState(snapshot, input.useCases?.artifact, input.useCases?.declaration, query)),
  );
  const metadata: Record<string, string> = {
    serving_contract_version: PREPARED_CONTRACT_VERSION,
    record_schema_version: snapshot.schema_version,
    release_id: snapshot.release_id,
    released_at: snapshot.released_at,
    catalogue_sha256: sha256(input.catalogueBytes),
    generator_sha256: input.generatorSha256,
    release_json: JSON.stringify(query.release()),
    counts_json: JSON.stringify(counts),
  };
  for (const key of Object.keys(metadata).sort()) meta.run(key, metadata[key]);
  db.exec("COMMIT");
  db.exec("VACUUM");
  db.close();
  return counts;
}

if (process.argv[1]?.endsWith("sqlite.ts")) {
  const catalogueBytes = fs.readFileSync("public/omics/catalogue.json");
  const snapshot = JSON.parse(catalogueBytes.toString("utf8")) as CatalogueSnapshot;
  const useCaseFile = `public/omics/releases/${snapshot.release_id}/use-cases.json`;
  const declaration = snapshot.coverage.use_cases as UseCaseDeclaration | undefined;
  const useCases = fs.existsSync(useCaseFile) && declaration
    ? { artifact: JSON.parse(fs.readFileSync(useCaseFile, "utf8")) as UseCaseArtifact, declaration }
    : undefined;
  const generatorSha256 = sha256(generatorFiles.map((file) => fs.readFileSync(file, "utf8")).join("\n"));
  const file = path.join("public/serving", `catalogue-${snapshot.release_id}.sqlite`);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const started = Date.now();
  const counts = buildPreparedCatalogue({ snapshot, catalogueBytes, useCases, generatorSha256, file });
  const bytes = fs.readFileSync(file);
  const receipt = {
    serving_contract_version: PREPARED_CONTRACT_VERSION,
    release_id: snapshot.release_id,
    file: path.basename(file),
    bytes: bytes.length,
    sha256: sha256(bytes),
    generator_sha256: generatorSha256,
    counts,
  };
  fs.writeFileSync(file.replace(/\.sqlite$/, ".json"), JSON.stringify(receipt, null, 2) + "\n");
  console.log(`Prepared ${snapshot.release_id}: ${(bytes.length / 1e6).toFixed(0)} MB in ${((Date.now() - started) / 1000).toFixed(0)} s, sha256 ${receipt.sha256}`);
}
