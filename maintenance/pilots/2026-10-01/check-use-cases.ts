/** Read-only pilot: use existing receipt and evidence-fingerprint validators. */
import fs from "node:fs";
import { createHash } from "node:crypto";
import { gunzipSync } from "node:zlib";
import { loadUseCases } from "../../../scripts/omics/use-cases";
import { buildUseCaseArtifact, validateUseCaseArtifact } from "../../../services/omics/src/use-cases";

const releaseId = "2026-09-30-e37e3ab1284d";
const root = `data/omics/releases/${releaseId}`;
const manifest = JSON.parse(fs.readFileSync(`${root}.json`, "utf8"));
const sha = (bytes: Buffer) => createHash("sha256").update(bytes).digest("hex");
const readArchive = (name: string) => {
  const bytes = gunzipSync(fs.readFileSync(`${root}/${name}.gz`));
  if (sha(bytes) !== manifest.files[name]) throw Error(`Archive checksum mismatch: ${name}`);
  return JSON.parse(bytes.toString("utf8"));
};
const snapshot = readArchive("catalogue.json");
const archivedArtifact = readArchive("use-cases.json");
const reviewed = loadUseCases();
if (!reviewed) throw Error("Missing reviewed use-case inputs");
validateUseCaseArtifact(snapshot, archivedArtifact, snapshot.coverage.use_cases);
const current = buildUseCaseArtifact(snapshot, reviewed.inputs);
const count = (items: string[]) => items.reduce<Record<string, number>>((out, value) => {
  out[value] = (out[value] ?? 0) + 1;
  return out;
}, {});
console.log(JSON.stringify({
  checked_at: new Date().toISOString(),
  method: "Existing loadUseCases, buildUseCaseArtifact and validateUseCaseArtifact; read-only",
  baseline_release_id: releaseId,
  receipt_validation: "passed",
  archived_artifact_validation: "passed",
  mapping_fingerprints: "compared without renewal against archived catalogue",
  use_cases: current.use_cases.length,
  mappings: current.mappings.length,
  mapping_lifecycle_counts: count(current.mappings.map((m) => m.lifecycle)),
  automatically_demoted_ids: current.mappings.filter((m) => m.stale_from).map((m) => m.id),
  collection_plan_counts: count(current.use_cases.map((u) => u.collection_plan?.status ?? "absent")),
  review_method_counts: count(current.use_cases.map((u) => u.review.method)),
  cases: current.use_cases.map((u) => ({
    id: u.id, title: u.title, reviewed_at: u.review.reviewed_at,
    review_method: u.review.method, collection_status: u.collection_plan?.status ?? "absent",
    evidence_gap_count: u.evidence_gaps.length, evidence_gaps: u.evidence_gaps,
    mapping_count: current.mappings.filter((m) => m.use_case_id === u.id).length,
    lifecycle_counts: count(current.mappings.filter((m) => m.use_case_id === u.id).map((m) => m.lifecycle)),
  })),
  limitations: [
    "Receipt and dependency checks do not re-review scientific applicability or clinical validity.",
    "All comparisons use the archived baseline; unimported upstream changes cannot change its mapping fingerprints.",
    "No reviewed_at values, scientific inputs, receipts or evidence hashes were changed.",
  ],
}, null, 2));
