// Dry-run validation of this batch without writing to the store.
// Run from the repository root:
//   npx tsx data/omics/use-case-coverage-binder-20261022/extract/validate_batch.ts \
//     data/omics/use-case-coverage-binder-20261022/batch.jsonl
// It runs everything addBatch checks except the SHACL subset, which needs the records in the
// store and therefore runs when the review agent adds the batch (and in CI).
import fs from "node:fs";
import { loadRecords } from "../../../../scripts/omics/records";

const readJsonl = (file: string) =>
  fs.readFileSync(file, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
import { readMapping } from "../../../../scripts/kg/export";
import { loadSchemes, validateVocabularies } from "../../../../scripts/omics/vocab";
import { validateAttributes } from "../../../../shared/omics/attributes";
import { validateDescriptions } from "../../../../shared/omics/descriptions";
import { validateDerivations } from "../../../../scripts/omics/derivations";
import { recordSchema, validateRecords } from "../../../../scripts/omics/schema";

const file = process.argv[2];
const additions = readJsonl(file).map((value) => recordSchema.parse(value));
const existing = loadRecords();
const ids = new Set(existing.map((r) => r.id));
for (const rec of additions) if (ids.has(rec.id)) throw new Error(`id already in store: ${rec.id}`);
validateVocabularies(readMapping(), additions, loadSchemes());
validateAttributes(additions);
validateDescriptions([...existing, ...additions]);
validateDerivations([...existing, ...additions]);
validateRecords([...existing, ...additions]);
console.log(`${additions.length} records pass schema, vocabulary, attribute and description validation.`);
