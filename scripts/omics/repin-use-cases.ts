/** Re-pin reviewed relevance judgements to the store as it is now.
 *
 * A judgement claim pins the fields of its use case, protocol and protocol sources that it relies
 * on (shared/omics/use-cases.ts judgementPinFields). When a reviewed change alters how those
 * records are written but not what they say, such as an issue #42 migration, re-pin the
 * judgements it touched and name the review that justifies it. Each changed claim is recorded in
 * data/provenance/records.jsonl. Judgements that still match are left alone.
 *   npm run use-cases:repin -- <review.md> */
import fs from "node:fs";
import { judgementPins, useCaseHash, type JudgementPin } from "../../shared/omics/use-cases";
import type { CatalogueRecord } from "../../shared/omics/catalogue-query";
import { recordChanges, recordFile } from "./records";

const review = process.argv[2];
if (!review || !fs.existsSync(review)) {
  console.error("Usage: npm run use-cases:repin -- <review.md>  (the review must exist)");
  process.exit(1);
}
const read = (kind: string) =>
  fs.readFileSync(recordFile(kind), "utf8").split("\n").filter(Boolean).map((line) => JSON.parse(line) as CatalogueRecord);
const byId = new Map(["use_case", "protocol", "source"].flatMap(read).map((r) => [r.id, r]));
const claims = read("claim");
const repinned: string[] = [];
const next = claims.map((claim) => {
  const field = claim.attributes.field;
  if (typeof field !== "string" || !field.startsWith("links:assessed_by:") || claim.status !== "source_checked") return claim;
  const subject = claim.links.find((l) => l.relation === "subject")!.target_id;
  const pins = judgementPins(byId, subject, field.slice("links:assessed_by:".length));
  if (useCaseHash(pins) === useCaseHash(claim.attributes.pins as JudgementPin[])) return claim;
  repinned.push(claim.id);
  return { ...claim, attributes: { ...claim.attributes, pins } };
});
if (repinned.length) {
  fs.writeFileSync(recordFile("claim"), next.map((r) => JSON.stringify(r) + "\n").join(""));
  recordChanges(repinned, "shared/omics/use-cases.ts judgementPins", review);
}
console.log(`Re-pinned ${repinned.length} relevance judgements against ${review}.`);
for (const id of repinned) console.log(`  ${id}`);
