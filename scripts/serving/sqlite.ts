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
import { createCatalogueQuery, type CatalogueSnapshot } from "../../shared/omics/catalogue-query";
import { createEvidenceIndex } from "../../shared/omics/evidence-table";
import { deriveResearchReadiness, getResearch } from "../../shared/omics/research";
import { useCaseState, type UseCaseArtifact, type UseCaseDeclaration } from "../../shared/omics/use-cases";
import { PREPARED_CONTRACT_VERSION } from "../../shared/omics/prepared-catalogue";
import { createRecordEncoder, decodeRecords, packEvidence, slimListRecord, unpackEvidence } from "../../shared/omics/serving-codec";
import { isBenchmarkSubject, isDatasetSubject } from "../../shared/omics/entity-kinds";
import { benchmarkCoverage } from "../omics/audit-benchmark-evidence";
import { buildBaselineAudit } from "../../lib/baseline-coverage";
import type { CatalogueRecord } from "../../shared/omics/catalogue-query";
import type { AuditCheck, AuditIndexRow } from "../../shared/omics/audit";
const { DatabaseSync } = process.getBuiltinModule("node:sqlite");

export const generatorFiles = [
  "scripts/serving/sqlite.ts",
  "shared/omics/catalogue-query.ts",
  "shared/omics/audit-query.ts",
  "shared/omics/audit.ts",
  "scripts/omics/audit-benchmark-evidence.ts",
  "lib/baseline-coverage.ts",
  "shared/omics/evidence-table.ts",
  "shared/omics/prepared-catalogue.ts",
  "shared/omics/serving-codec.ts",
  "shared/omics/published-comparisons.ts",
  "shared/omics/research.ts",
  "shared/omics/source-identity.ts",
  "shared/omics/use-cases.ts",
];
/** Catalogue-wide counts shown on the homepage, prepared once per release.
 * Labels stay raw; the website formats them. */
export function homeSummary(records: readonly CatalogueRecord[]) {
  const tally = (pick: (record: CatalogueRecord) => string[]) => {
    const counts = new Map<string, number>();
    for (const record of records) for (const key of pick(record)) counts.set(key, (counts.get(key) || 0) + 1);
    return [...counts.entries()].sort((a, b) => b[1] - a[1]).map(([label, value]) => ({ label, value }));
  };
  const coverage = benchmarkCoverage(records);
  return {
    records: records.length,
    external: records.filter((r) => r.kind === "result" && r.status === "source_checked").length,
    own: records.filter((r) => r.kind === "result" && r.status === "reproduced").length,
    kinds: tally((record) => [record.kind]),
    areas: tally((record) => record.facets.areas || []).slice(0, 10),
    coverage: coverage.map((entry) => ({ name: entry.name, evaluations: entry.evaluations })),
    covered: coverage.filter((entry) => entry.evaluations > 0).length,
    benchmarks: coverage.length,
  };
}

/** Counts the evidence guide shows: rows by scope, and unique profile facts by review status. */
export function evidenceSummary(rows: readonly { evidence_scope: string; field_path: string; record_id: string; review_status: string }[]) {
  const byScope: Record<string, number> = {};
  for (const row of rows) byScope[row.evidence_scope] = (byScope[row.evidence_scope] || 0) + 1;
  const facts = new Map<string, (typeof rows)[number]>();
  for (const row of rows)
    if (/\.profile\.facts\.\d+\.value$/.test(row.field_path)) facts.set(`${row.record_id}:${row.field_path}`, row);
  const factsByStatus: Record<string, number> = {};
  for (const row of facts.values()) factsByStatus[row.review_status] = (factsByStatus[row.review_status] || 0) + 1;
  return { rows: rows.length, by_scope: byScope, facts: facts.size, facts_by_status: factsByStatus };
}

/** Reviewed association claims, as `subject|field` keys (the rollup gate). */
export function associationKeys(records: readonly CatalogueRecord[]): string[] {
  const keys = new Set<string>();
  for (const item of records)
    if (
      item.kind === "claim" &&
      ["source_checked", "reproduced"].includes(item.status) &&
      item.source_ids.length > 0 &&
      !!item.attributes.source_locator
    )
      for (const link of item.links)
        if (link.relation === "subject") keys.add(`${link.target_id}|${String(item.attributes.field)}`);
  return [...keys].sort();
}

const sha256 = (bytes: Buffer | string) => crypto.createHash("sha256").update(bytes).digest("hex");
const gz = (value: unknown) => gzipSync(JSON.stringify(value), { level: 9 });

export function buildPreparedCatalogue(input: {
  snapshot: CatalogueSnapshot;
  catalogueBytes: Buffer;
  useCases?: { artifact: UseCaseArtifact; declaration: UseCaseDeclaration };
  /** The release's audit files: index rows, runs, resolutions and check chunks by file name. */
  audit?: { index: AuditIndexRow[]; runs: unknown[]; resolutions: unknown[]; chunks: Map<string, AuditCheck[]> };
  generatorSha256: string;
  file: string;
}) {
  const { snapshot } = input;
  const query = createCatalogueQuery(snapshot);
  fs.rmSync(input.file, { force: true });
  const db = new DatabaseSync(input.file);
  // Contract 3: records are stored once, compressed; every other table refers to
  // them by ID (serving-codec.ts). Use cases are one row per entry.
  db.exec(`
    PRAGMA page_size = 8192; PRAGMA journal_mode = OFF; PRAGMA synchronous = OFF;
    CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID;
    CREATE TABLE blobs (key TEXT PRIMARY KEY, value BLOB NOT NULL);
    CREATE TABLE records (id TEXT PRIMARY KEY, kind TEXT NOT NULL, status TEXT NOT NULL, gz BLOB NOT NULL);
    CREATE INDEX records_kind ON records (kind, id);
    CREATE TABLE details (id TEXT PRIMARY KEY, gz BLOB NOT NULL);
    CREATE TABLE result_rows (result_id TEXT PRIMARY KEY, gz BLOB NOT NULL);
    CREATE TABLE result_index (record_id TEXT NOT NULL, pos INTEGER NOT NULL, result_id TEXT NOT NULL, PRIMARY KEY (record_id, pos)) WITHOUT ROWID;
    CREATE TABLE evidence (record_id TEXT PRIMARY KEY, gz BLOB NOT NULL);
    CREATE TABLE audit_checks (record_id TEXT PRIMARY KEY, gz BLOB NOT NULL);
    CREATE TABLE use_case_entries (section TEXT NOT NULL, key TEXT NOT NULL, gz BLOB NOT NULL, PRIMARY KEY (section, key)) WITHOUT ROWID;
  `);
  const meta = db.prepare("INSERT INTO meta VALUES (?, ?)");
  const blob = db.prepare("INSERT INTO blobs VALUES (?, ?)");
  const insertRecord = db.prepare("INSERT INTO records VALUES (?, ?, ?, ?)");
  const insertDetail = db.prepare("INSERT INTO details VALUES (?, ?)");
  const insertRow = db.prepare("INSERT INTO result_rows VALUES (?, ?)");
  const insertIndex = db.prepare("INSERT INTO result_index VALUES (?, ?, ?)");
  const insertEvidence = db.prepare("INSERT INTO evidence VALUES (?, ?)");
  const insertUseCase = db.prepare("INSERT INTO use_case_entries VALUES (?, ?, ?)");

  // The engine's own record set: non-excluded records, ordered by ID.
  const records = snapshot.records
    .filter((record) => record.status !== "excluded")
    .sort((a, b) => a.id.localeCompare(b.id));
  const byId = new Map(records.map((record) => [record.id, record]));
  const encodeRecords = createRecordEncoder(records);
  // Every encoded value must decode to exactly what the engine returned.
  const packed = (value: unknown, label: string) => {
    const encoded = encodeRecords(value);
    const decoded = decodeRecords(encoded, (id) => byId.get(id) || null);
    if (JSON.stringify(decoded) !== JSON.stringify(value)) throw new Error(`Prepared ${label} does not round-trip`);
    return gz(encoded);
  };
  const evidence = createEvidenceIndex(snapshot);
  const evidenceSources: Parameters<typeof packEvidence>[1] = new Map();
  const counts = { records: 0, details: 0, result_rows: 0, result_index: 0, evidence: 0, use_case_entries: 0 };
  const rowsWritten = new Set<string>();
  db.exec("BEGIN");
  for (const record of records) {
    insertRecord.run(record.id, record.kind, record.status, gz(record));
    counts.records++;
    const detail = query.get({ id: record.id, include_comparisons: true });
    if (detail) {
      insertDetail.run(record.id, packed(detail, `detail ${record.id}`));
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
      const packedRows = packEvidence(evidenceRows, evidenceSources);
      const unpacked = unpackEvidence(packedRows, record, snapshot.release_id, Object.fromEntries(evidenceSources));
      if (JSON.stringify(unpacked) !== JSON.stringify(evidenceRows)) throw new Error(`Prepared evidence of ${record.id} does not round-trip`);
      insertEvidence.run(record.id, gz(packedRows));
      counts.evidence++;
    }
  }
  // Full rows (results() pages compact them; filters need the full form).
  for (const row of query.resultRows()) {
    if (rowsWritten.has(row.result.id)) continue;
    rowsWritten.add(row.result.id);
    insertRow.run(row.result.id, packed(row, `result row ${row.result.id}`));
    counts.result_rows++;
  }
  blob.run("evidence_sources", gz(Object.fromEntries([...evidenceSources].sort(([a], [b]) => a.localeCompare(b)))));
  // List entries carry only the record fields listPage filters on; pages read the rest.
  blob.run("list_entries", gz(query.listEntries().map((entry) => ({ ...entry, record: slimListRecord(entry.record) }))));
  blob.run("home_summary", gz(homeSummary(snapshot.records)));
  blob.run("baseline_audit", gz(buildBaselineAudit(snapshot as never)));
  blob.run("evidence_summary", gz(evidenceSummary(evidence.all())));
  blob.run("association_keys", gz(associationKeys(snapshot.records)));
  // Audit history: the index, runs and resolutions, and each record's checks in index order.
  const audit = input.audit || { index: [], runs: [], resolutions: [], chunks: new Map<string, AuditCheck[]>() };
  blob.run("audit", gz({ index: audit.index, runs: audit.runs, resolutions: audit.resolutions }));
  const insertAudit = db.prepare("INSERT INTO audit_checks VALUES (?, ?)");
  for (const row of audit.index) {
    const checks = row.chunk_ids.flatMap((id) => (audit.chunks.get(id) || []).filter((check) => check.record_id === row.record_id));
    insertAudit.run(row.record_id, gz(checks));
  }
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
  // Use cases: the small index (entries and backlinks) as one blob, and each
  // mapping list, result list and source list as its own row.
  const { mappings, results, sources, ...base } = useCaseState(
    snapshot, input.useCases?.artifact, input.useCases?.declaration, query,
  );
  blob.run("use_case_base", gz(base));
  for (const [section, entries] of [["mappings", mappings], ["results", results], ["sources", sources]] as const)
    for (const [key, value] of entries) {
      insertUseCase.run(section, key, packed(value, `use case ${section} ${key}`));
      counts.use_case_entries++;
    }
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
  const releaseDir = `public/omics/releases/${snapshot.release_id}`;
  const readJson = (name: string) => JSON.parse(fs.readFileSync(path.join(releaseDir, name), "utf8"));
  const audit = fs.existsSync(path.join(releaseDir, "audit-index.json"))
    ? {
        index: readJson("audit-index.json") as AuditIndexRow[],
        runs: readJson("audit-runs.json"),
        resolutions: readJson("audit-resolutions.json"),
        chunks: new Map(
          fs.readdirSync(releaseDir).filter((name) => /^audit-checks-\d{6}\.json$/.test(name)).sort()
            .map((name) => [name.replace(/^audit-checks-|\.json$/g, ""), readJson(name) as AuditCheck[]] as const),
        ),
      }
    : undefined;
  const generatorSha256 = sha256(generatorFiles.map((file) => fs.readFileSync(file, "utf8")).join("\n"));
  const file = path.join("public/serving", `catalogue-${snapshot.release_id}.sqlite`);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const started = Date.now();
  const counts = buildPreparedCatalogue({ snapshot, catalogueBytes, useCases, audit, generatorSha256, file });
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
