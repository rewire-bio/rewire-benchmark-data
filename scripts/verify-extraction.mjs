import fs from 'node:fs';
import { createHash } from 'node:crypto';

// This receipt records the extraction baseline and must never be rewritten.
// CI checks its immutable archives; the full extraction check is a migration audit.
const receipt = JSON.parse(fs.readFileSync('docs/data-extraction.json', 'utf8'));
const files = process.argv.includes('--archives-only') ? receipt.files.filter(row => row.path.startsWith('data/omics/releases/')) : receipt.files;
for (const row of files) {
  const actual = createHash('sha256').update(fs.readFileSync(row.path)).digest('hex');
  if (actual !== row.sha256) throw new Error(`Extraction preservation failed: ${row.path}`);
}
console.log(`Verified ${files.length} source files from ${receipt.source_repository}@${receipt.source_revision}.`);
