// Dry-run validation of a batch file against the store, running the same checks
// as `records -- add` without writing anything.
import { readFileSync } from "node:fs";
import fs from "node:fs";
import { loadRecords } from "../../../../scripts/omics/records";
import { loadSchemes, validateVocabularies } from "../../../../scripts/omics/vocab";
import { validateRecords, recordSchema, type RecordEntry } from "../../../../scripts/omics/schema";
import { validateAttributes } from "../../../../shared/omics/attributes";
import { validateDescriptions } from "../../../../shared/omics/descriptions";
import { validateConcerns } from "../../../../shared/omics/concerns";

const readMapping = () => JSON.parse(fs.readFileSync("data/ontology/mapping.json", "utf8"));

const batch = readFileSync(process.argv[2], "utf8")
  .split("\n").filter(Boolean).map((line) => recordSchema.parse(JSON.parse(line)));
const existing = loadRecords();
const ids = new Set(existing.map((r) => r.id));
const clashes = batch.filter((r) => ids.has(r.id)).map((r) => r.id);
if (clashes.length) throw new Error(`ids already in the store: ${clashes.join(", ")}`);
validateVocabularies(readMapping(), batch, loadSchemes());
validateAttributes(batch);
validateDescriptions([...existing, ...batch]);
validateConcerns([...existing, ...batch]);
validateRecords([...existing, ...batch] as RecordEntry[]);
console.log(`${batch.length} batch records pass vocabulary, attribute, description, concern and schema checks against ${existing.length} stored records.`);
