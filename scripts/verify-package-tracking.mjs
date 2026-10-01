import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

/** All hydration objects must survive a Git checkout, including nested public/ paths. */
export function verifyPackageTracking(root = process.cwd()) {
  const manifestPath = 'website/manifest.json';
  const manifest = JSON.parse(fs.readFileSync(path.join(root, manifestPath), 'utf8'));
  if (!Array.isArray(manifest.files)) throw new Error('Prepared manifest has no file inventory');
  const sources = new Set([manifestPath]);
  for (const entry of manifest.files) {
    const source = entry?.source;
    if (typeof source !== 'string' || !source || source.includes('\\') || path.posix.isAbsolute(source) ||
        source.split('/').some(part => !part || part === '.' || part === '..')) {
      throw new Error('Invalid prepared source path');
    }
    sources.add(source);
  }
  const tracked = new Map();
  const entries = execFileSync('git', ['ls-files', '--stage', '-z'], { cwd: root, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 }).split('\0').filter(Boolean);
  for (const entry of entries) {
    const tab = entry.indexOf('\t');
    const [mode, , stage] = entry.slice(0, tab).split(' ');
    tracked.set(entry.slice(tab + 1), { mode, stage });
  }
  const missing = [...sources].filter(source => !tracked.has(source));
  if (missing.length) throw new Error(`Prepared artifact sources are not tracked (${missing.length}):\n${missing.join('\n')}`);
  for (const source of sources) {
    if (!fs.lstatSync(path.join(root, source)).isFile()) throw new Error(`Prepared artifact source is not a regular file: ${source}`);
    const { mode, stage } = tracked.get(source);
    if (stage !== '0' || !['100644', '100755'].includes(mode)) throw new Error(`Prepared artifact source is not tracked as a regular file: ${source}`);
  }
  return { releaseId: manifest.release_id, sources: sources.size - 1 };
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const result = verifyPackageTracking();
  console.log(`Verified ${result.sources} tracked prepared sources for ${result.releaseId}.`);
}
