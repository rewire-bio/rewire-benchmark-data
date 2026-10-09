/** Re-pin the evidence fingerprint (evidence_sha256) of every active use-case mapping to the
 * current built snapshot (public/omics/catalogue.json; run npm run omics:release first).
 * For changes that only alter how records are written, not what they say, such as the
 * issue #42 migrations. Name the review that justifies it.
 *   npm run use-cases:repin -- <review.md> */
import fs from "node:fs";
import crypto from "node:crypto";
import { mappingEvidenceHash, parseUseCaseInputs } from "../../shared/omics/use-cases";
import type { CatalogueSnapshot } from "../../shared/omics/catalogue-query";

const review = process.argv[2];
if (!review || !fs.existsSync(review)) {
  console.error("Usage: npm run use-cases:repin -- <review.md>  (the review must exist)");
  process.exit(1);
}
const file = "data/omics/use-cases/inputs.json";
const snapshot: CatalogueSnapshot = JSON.parse(fs.readFileSync("public/omics/catalogue.json", "utf8"));
const raw = JSON.parse(fs.readFileSync(file, "utf8"));
const useCases = new Map(parseUseCaseInputs(raw).use_cases.map((u) => [u.id, u]));
const repinned: string[] = [];
raw.mappings = raw.mappings.map((m: { id: string; use_case_id: string; lifecycle: string; evidence_sha256?: string }) => {
  if (m.lifecycle !== "active") return m;
  const hash = mappingEvidenceHash(snapshot, useCases.get(m.use_case_id)!, m as never);
  if (hash === m.evidence_sha256) return m;
  repinned.push(m.id);
  return { ...m, evidence_sha256: hash };
});
const text = JSON.stringify(raw, null, 2) + "\n";
fs.writeFileSync(file, text);
// The use-case review receipt pins inputs.json; record the re-pin there.
const receiptFile = "data/omics/use-cases/review.json";
const receipt = JSON.parse(fs.readFileSync(receiptFile, "utf8"));
receipt.files["inputs.json"] = crypto.createHash("sha256").update(text).digest("hex");
if (repinned.length)
  receipt.limitations.push(`${new Date().toISOString().slice(0, 10)}: ${repinned.length} active mappings had evidence_sha256 re-pinned after record migrations, without re-reading the mappings; see ${review}.`);
fs.writeFileSync(receiptFile, JSON.stringify(receipt, null, 2) + "\n");
console.log(`Re-pinned ${repinned.length} active mappings (${review}).`);
