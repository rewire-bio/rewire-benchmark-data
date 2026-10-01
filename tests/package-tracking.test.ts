import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { afterEach, expect, it } from 'vitest';
import { verifyPackageTracking } from '../scripts/verify-package-tracking.mjs';
const roots: string[] = [];
function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'package-tracking-')); roots.push(root);
  execFileSync('git', ['init', '-q', root]);
  const source = 'website/files/public/omics/catalogue.json.gz';
  fs.mkdirSync(path.dirname(path.join(root, source)), { recursive: true });
  fs.writeFileSync(path.join(root, source), 'compressed fixture');
  fs.writeFileSync(path.join(root, 'website/manifest.json'), JSON.stringify({ release_id: 'fixture', files: [{ source }] }));
  execFileSync('git', ['add', 'website/manifest.json'], { cwd: root });
  return { root, source };
}
afterEach(() => { for (const root of roots.splice(0)) fs.rmSync(root, { recursive: true, force: true }); });

it('rejects a locally available object that would be absent from a Git checkout', () => {
  const { root, source } = fixture();
  expect(() => verifyPackageTracking(root)).toThrow(`Prepared artifact sources are not tracked (1):\n${source}`);
  execFileSync('git', ['add', source], { cwd: root });
  expect(verifyPackageTracking(root)).toEqual({ releaseId: 'fixture', sources: 1 });
});

it('keeps generated root public output ignored while tracking prepared nested public objects', () => {
  const { root, source } = fixture();
  fs.writeFileSync(path.join(root, '.gitignore'), '/public/\n');
  fs.mkdirSync(path.join(root, 'public'));
  fs.writeFileSync(path.join(root, 'public/catalogue.json'), 'generated');
  execFileSync('git', ['add', '.'], { cwd: root });
  const tracked = execFileSync('git', ['ls-files'], { cwd: root, encoding: 'utf8' });
  expect(tracked).toContain(source);
  expect(tracked.split('\n')).not.toContain('public/catalogue.json');
  expect(verifyPackageTracking(root).sources).toBe(1);
});

it('rejects missing or symlinked source bytes even when the path is tracked', () => {
  const { root, source } = fixture();
  execFileSync('git', ['add', source], { cwd: root });
  fs.unlinkSync(path.join(root, source));
  expect(() => verifyPackageTracking(root)).toThrow();
  fs.symlinkSync(path.join(root, 'website/manifest.json'), path.join(root, source));
  expect(() => verifyPackageTracking(root)).toThrow('not a regular file');
});

it('rejects source traversal before querying tracked paths', () => {
  const { root } = fixture();
  fs.writeFileSync(path.join(root, 'website/manifest.json'), JSON.stringify({ files: [{ source: '../outside.gz' }] }));
  expect(() => verifyPackageTracking(root)).toThrow('Invalid prepared source path');
});
