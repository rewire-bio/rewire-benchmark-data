/** Pin reviewed relevance judgement and summary claims to the store as it is now.
 *
 * A reviewed claim pins the fields of the records it rests on (shared/omics/use-cases.ts claimPins).
 * Re-pinning tells the release those records still support it, so it needs a review that says so:
 *   npm run use-cases:repin -- <review.md>                 pin reviewed claims that have no pins yet
 *   npm run use-cases:repin -- <review.md> <claim-id>...   re-pin the named claims, after re-review
 *   npm run use-cases:repin -- <review.md> --all           re-pin every reviewed claim; only for a
 *                                                          reviewed change of form, never of meaning
 * Each changed claim is recorded in data/provenance/records.jsonl. */
import fs from "node:fs";
import { claimPins, useCaseHash, type JudgementPin } from "../../shared/omics/use-cases";
import type { CatalogueRecord } from "../../shared/omics/catalogue-query";
import { recordChanges, recordFile } from "./records";

const [review, ...rest] = process.argv.slice(2);
const all = rest.includes("--all");
const named = new Set(rest.filter((a) => a !== "--all"));
if (!review || !fs.existsSync(review) || (all && named.size)) {
  console.error("Usage: npm run use-cases:repin -- <review.md> [<claim-id>... | --all]  (the review must exist)");
  process.exit(1);
}
const read = (kind: string) =>
  fs.readFileSync(recordFile(kind), "utf8").split("\n").filter(Boolean).map((line) => JSON.parse(line) as CatalogueRecord);
const kinds = ["use_case", "protocol", "source", "evaluation", "result", "claim"];
const records = new Map(kinds.flatMap(read).map((r) => [r.id, r]));
const claims = read("claim");
const reviewed = (c: CatalogueRecord) => ["source_checked", "reproduced"].includes(c.status);
const pinnable = (c: CatalogueRecord) => typeof c.attributes.field === "string"
  && (c.attributes.field.startsWith("links:assessed_by:") || c.attributes.field === "summary");

for (const id of named) {
  const claim = records.get(id);
  if (!claim || claim.kind !== "claim" || !pinnable(claim)) { console.error(`${id} is not a judgement or summary claim.`); process.exit(1); }
  if (!reviewed(claim)) { console.error(`${id} is ${claim.status}; review it before pinning.`); process.exit(1); }
}

const repinned: string[] = [];
const next = claims.map((claim) => {
  if (!pinnable(claim) || !reviewed(claim)) return claim;
  const stored = claim.attributes.pins as JudgementPin[] | undefined;
  if (!(all || named.has(claim.id) || !stored?.length)) return claim;
  const pins = claimPins(records, claim);
  if (!pins || (stored && useCaseHash(pins) === useCaseHash(stored))) return claim;
  repinned.push(claim.id);
  return { ...claim, attributes: { ...claim.attributes, pins } };
});
if (repinned.length) {
  fs.writeFileSync(recordFile("claim"), next.map((r) => JSON.stringify(r) + "\n").join(""));
  recordChanges(repinned, "shared/omics/use-cases.ts claimPins", review);
}
console.log(`Pinned ${repinned.length} claims against ${review}.`);
for (const id of repinned) console.log(`  ${id}`);
