import fs from 'node:fs';
import { createHash } from 'node:crypto';

// This receipt records the extraction baseline. Later reviewed scientific edits
// require explicitly updating this check; historical archives remain immutable.
const receipt = JSON.parse(fs.readFileSync('docs/data-extraction.json', 'utf8'));
for (const row of receipt.files) {
  const actual = createHash('sha256').update(fs.readFileSync(row.path)).digest('hex');
  if (actual !== row.sha256) throw new Error(`Extraction preservation failed: ${row.path}`);
}
console.log(`Verified ${receipt.files.length} source files from ${receipt.source_repository}@${receipt.source_revision}.`);
