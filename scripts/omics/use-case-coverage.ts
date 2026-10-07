import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";
import { gunzipSync } from "node:zlib";
import { z } from "zod";
import { recordSchema, type RecordEntry } from "./schema";

export const useCaseCoverageRoot = "data/omics/use-case-coverage-20260930";
const lanes = ["clinical", "research", "experimental"] as const;
const receiptSchema = z.object({
  schema_version: z.literal("1.0"),
  method: z.literal("automated_source_review"),
  reviewer: z.string().min(1),
  reviewed_at: z.string().datetime(),
  scope: z.string().min(1),
  limitations: z.array(z.string().min(1)).min(1),
  errors: z.array(z.string()).length(0),
  files: z.record(z.string(), z.string().regex(/^[a-f0-9]{64}$/)),
}).strict();
const digest = (bytes: Buffer) => createHash("sha256").update(bytes).digest("hex");

/** Public evidence copies and original retrieved source bytes have distinct
 * identities. Verify the archived copy actually bound by the lane receipt;
 * a curator extract does not establish fresh-clone access to the full source. */
export function verifyReviewedArtifacts(review: unknown, repositoryRoot = process.cwd()): void {
  if (!review || typeof review !== "object") return;
  const checked = (review as { checked?: Record<string, unknown> }).checked;
  if (!checked || (!checked.bound_artifacts_raw_sha256 && !checked.bound_artifacts_archive_sha256)) return;
  const hashes = z.record(z.string(), z.string().regex(/^[a-f0-9]{64}$/));
  const raw = hashes.parse(checked.bound_artifacts_raw_sha256);
  const archived = hashes.parse(checked.bound_artifacts_archive_sha256);
  if (JSON.stringify(Object.keys(raw).sort()) !== JSON.stringify(Object.keys(archived).sort()))
    throw Error("Reviewed evidence raw/archive inventories differ");
  const allowedRoot = path.resolve(repositoryRoot, "data/omics");
  for (const [relativePath, rawHash] of Object.entries(raw)) {
    const file = path.resolve(repositoryRoot, relativePath);
    const inside = path.relative(allowedRoot, file);
    if (path.isAbsolute(relativePath) || inside.startsWith("..") || path.isAbsolute(inside))
      throw Error(`Reviewed evidence path escapes data/omics: ${relativePath}`);
    const realInside = path.relative(fs.realpathSync(allowedRoot), fs.realpathSync(file));
    if (realInside.startsWith("..") || path.isAbsolute(realInside))
      throw Error(`Reviewed evidence symlink escapes data/omics: ${relativePath}`);
    const bytes = fs.readFileSync(file);
    if (digest(bytes) !== archived[relativePath])
      throw Error(`Reviewed evidence archive changed: ${relativePath}`);
    const uncompressed = relativePath.endsWith(".gz") ? gunzipSync(bytes) : bytes;
    if (digest(uncompressed) !== rawHash)
      throw Error(`Reviewed evidence content changed: ${relativePath}`);
  }
}

export function useCaseCoverageInputFiles(root = useCaseCoverageRoot): string[] {
  return ["review.json", "before.json", "review-clinical.json", "review-research.json", "review-experimental.json", ...lanes.flatMap(lane =>
    ["records.jsonl", "coverage.json", "research.md", "sources.md", "claims.csv", "retrieval-log.md"]
      .map(file => `${lane}/${file}`),
  )].map(file => path.join(root, file));
}

/** Append reviewed evidence only. Never replace an existing scientific record. */
export function addUseCaseCoverage(records: RecordEntry[], root = useCaseCoverageRoot): RecordEntry[] {
  const receipt = receiptSchema.parse(JSON.parse(fs.readFileSync(path.join(root, "review.json"), "utf8")));
  const files = useCaseCoverageInputFiles(root).slice(1);
  const expected = files.map(file => path.relative(root, file)).sort();
  if (JSON.stringify(Object.keys(receipt.files).sort()) !== JSON.stringify(expected))
    throw Error("Use-case coverage review does not bind every expected input");
  for (const file of files) {
    if (digest(fs.readFileSync(file)) !== receipt.files[path.relative(root, file)])
      throw Error(`Use-case coverage input changed since review: ${file}`);
  }
  for (const lane of lanes) {
    const reviewFile = path.join(root, `review-${lane}.json`);
    const reviewText = fs.readFileSync(reviewFile, "utf8").trim();
    if (reviewText) verifyReviewedArtifacts(JSON.parse(reviewText));
  }
  const additions = lanes.flatMap(lane => fs.readFileSync(path.join(root, lane, "records.jsonl"), "utf8")
    .split("\n").filter(Boolean).map(line => recordSchema.parse(JSON.parse(line))));
  const ids = new Set(records.map(record => record.id));
  for (const record of additions) {
    if (ids.has(record.id)) throw Error(`Use-case coverage cannot replace or duplicate record: ${record.id}`);
    ids.add(record.id);
    if (record.status === "reproduced" || record.attributes.origin === "rewire_run")
      throw Error(`Literature curation cannot claim a new execution: ${record.id}`);
  }
  return [...records, ...additions];
}
