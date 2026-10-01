import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { gzipSync, gunzipSync } from 'node:zlib';
import { afterEach, describe, expect, it } from 'vitest';
import { packageWebsite } from '../scripts/package-website.mjs';

const current = '2026-09-29-0123456789ab';
const historical = '2026-09-20-fedcba987654';
const roots: string[] = [];
const sha = (bytes: string | Buffer) => createHash('sha256').update(bytes).digest('hex');
type PreparedFile = { source: string; destination: string; sha256: string; bytes: number; scope: string };
type PreparedManifest = { schema_version: number; release_id: string; files: PreparedFile[] };
function write(root: string, name: string, bytes: string | Buffer) {
  const file = path.join(root, name);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, bytes);
  return file;
}
function release(root: string, id: string) {
  const bytes = JSON.stringify({ schema_version: '1.1', release_id: id, records: [], coverage: {} }) + '\n';
  const manifest = JSON.stringify({ release_id: id, files: { 'catalogue.json': sha(bytes) } }, null, 2) + '\n';
  write(root, `public/omics/releases/${id}/catalogue.json`, bytes);
  write(root, `public/omics/releases/${id}/manifest.json`, manifest);
  write(root, `data/omics/releases/${id}.json`, manifest);
  return { bytes, manifest };
}
function fixture() {
  const root = fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()), 'benchmark-package-'));
  roots.push(root);
  const latest = release(root, current);
  const previous = release(root, historical);
  write(root, 'public/omics/catalogue.json', latest.bytes);
  write(root, 'public/omics/manifest.json', latest.manifest);
  write(root, 'data/benchmark-literature/papers.json', '[]\n');
  write(root, 'data/benchmark-literature/results.csv', 'id,paper_id\n');
  write(root, 'public/benchmark-literature/papers.json', '[]\n');
  write(root, 'public/benchmark-literature/results.csv', 'id,paper_id\n');
  write(root, 'data/benchmark-runs/mfass-v2.json', '{"fixture":true}\n');
  write(root, 'data/omics/scope-audit.jsonl', '{"paper_id":"excluded","decision":"excluded"}\n');
  write(root, 'lib/benchmark-catalog.ts', 'export const MODELS = [];\n');
  return { root, latest, previous };
}
afterEach(() => { for (const root of roots.splice(0)) fs.rmSync(root, { recursive: true, force: true }); });

describe('prepared website package', () => {
  it('round-trips every prepared byte with a deterministic destination inventory and digest', async () => {
    const { root } = fixture();
    const result = await packageWebsite({ dataDir: root });
    const manifest = result.manifest as PreparedManifest;
    expect(manifest.schema_version).toBe(1);
    expect(manifest.release_id).toBe(current);
    expect(result.filesCount).toBe(manifest.files.length);
    expect(manifest.files.map(row => row.destination)).toEqual(manifest.files.map(row => row.destination).sort((a, b) => a.localeCompare(b)));
    expect(new Set(manifest.files.map(row => row.destination)).size).toBe(manifest.files.length);
    for (const entry of manifest.files) {
      const actual = gunzipSync(fs.readFileSync(path.join(root, entry.source)));
      const original = fs.readFileSync(path.join(root, entry.destination === 'lib/generated-benchmark-catalog.ts' ? 'lib/benchmark-catalog.ts' : entry.destination));
      expect(actual).toEqual(original);
      expect(entry.sha256).toBe(sha(original));
      expect(entry.bytes).toBe(original.length);
      expect(entry.scope).toBe(entry.destination.startsWith(`public/omics/releases/${historical}/`) ? 'historical' : 'current');
    }
    expect(JSON.parse(fs.readFileSync(result.manifestPath, 'utf8'))).toEqual(manifest);
    const first = fs.readFileSync(result.manifestPath);
    await packageWebsite({ dataDir: root });
    expect(fs.readFileSync(result.manifestPath)).toEqual(first);
  });

  it.each([
    'public/omics/catalogue.json',
    'public/benchmark-literature/papers.json',
    'public/benchmark-literature/results.csv',
    'data/benchmark-literature/papers.json',
    'data/benchmark-literature/results.csv',
    'data/benchmark-runs/mfass-v2.json',
    'data/omics/scope-audit.jsonl',
    'lib/benchmark-catalog.ts',
    `public/omics/releases/${current}/catalogue.json`,
  ])('refuses to publish a package missing required input %s', async name => {
    const { root } = fixture();
    fs.unlinkSync(path.join(root, name));
    await expect(packageWebsite({ dataDir: root })).rejects.toThrow('Missing required prepared input');
    expect(fs.existsSync(path.join(root, 'website/manifest.json'))).toBe(false);
  });

  it('rejects a changed immutable receipt and leaves it intact', async () => {
    const { root } = fixture();
    const receipt = write(root, `data/omics/releases/${current}.json`, '{"conflict":true}\n');
    const before = fs.readFileSync(receipt);
    await expect(packageWebsite({ dataDir: root })).rejects.toThrow('Immutable current receipt conflict');
    expect(fs.readFileSync(receipt)).toEqual(before);
  });

  it('rejects conflicting immutable compressed bytes without rewriting the archive', async () => {
    const { root } = fixture();
    const archive = write(root, `data/omics/releases/${historical}/catalogue.json.gz`, gzipSync('conflicting bytes\n'));
    const original = fs.readFileSync(archive);
    await expect(packageWebsite({ dataDir: root })).rejects.toThrow('Immutable archive conflict');
    expect(fs.readFileSync(archive)).toEqual(original);
    expect(fs.existsSync(path.join(root, 'website/manifest.json'))).toBe(false);
  });

  it('reuses direct historical gzip files byte-for-byte instead of duplicating or recompressing them', async () => {
    const { root, previous } = fixture();
    const source = `data/omics/releases/${historical}/catalogue.json.gz`;
    const bytes = gzipSync(previous.bytes, { level: 1 });
    const archive = write(root, source, bytes);
    const untouched = new Date('2020-01-01T00:00:00Z');
    fs.utimesSync(archive, untouched, untouched);
    const { manifest: raw } = await packageWebsite({ dataDir: root });
    const row = (raw as PreparedManifest).files.find(entry => entry.destination === `public/omics/releases/${historical}/catalogue.json`)!;
    expect(row.source).toBe(source);
    expect(fs.readFileSync(archive)).toEqual(bytes);
    expect(fs.statSync(archive).mtimeMs).toBe(untouched.valueOf());
    expect(fs.existsSync(path.join(root, `website/files/public/omics/releases/${historical}/catalogue.json.gz`))).toBe(false);
  });

  it('keeps current-only packages scoped while retaining historical preservation receipts', async () => {
    const { root } = fixture();
    fs.rmSync(path.join(root, `public/omics/releases/${historical}`), { recursive: true });
    const { manifest: raw } = await packageWebsite({ dataDir: root, currentOnly: true });
    const manifest = raw as PreparedManifest;
    expect(manifest.files.every(row => row.scope === 'current')).toBe(true);
    expect(manifest.files.some(row => row.destination === `data/omics/releases/${historical}.json`)).toBe(true);
    expect(manifest.files.some(row => row.destination.startsWith(`public/omics/releases/${historical}/`))).toBe(false);
    await expect(packageWebsite({ dataDir: root, currentOnly: false })).rejects.toThrow('Incomplete historical release');
  });

  it('preserves unrelated local files and pre-existing immutable archives', async () => {
    const { root, previous } = fixture();
    const archive = write(root, `data/omics/releases/${historical}/catalogue.json.gz`, gzipSync(previous.bytes));
    const sentinel = write(root, 'website/operator-notes.txt', 'keep this\n');
    const archiveBefore = fs.readFileSync(archive);
    await packageWebsite({ dataDir: root });
    expect(fs.readFileSync(sentinel, 'utf8')).toBe('keep this\n');
    expect(fs.readFileSync(archive)).toEqual(archiveBefore);
  });

  it('rejects prepared source symlinks before publishing an inventory', async () => {
    const { root } = fixture();
    const filename = path.join(root, 'data/benchmark-literature/papers.json');
    fs.unlinkSync(filename);
    fs.symlinkSync(path.join(root, 'public/benchmark-literature/papers.json'), filename);
    await expect(packageWebsite({ dataDir: root })).rejects.toThrow(/regular file|Symlink/);
    expect(fs.existsSync(path.join(root, 'website/manifest.json'))).toBe(false);
  });

  it('does not leave an invalid new archive behind and permits a corrected retry', async () => {
    const { root } = fixture();
    const manifestFile = path.join(root, 'public/omics/manifest.json');
    const manifest = JSON.parse(fs.readFileSync(manifestFile, 'utf8'));
    manifest.files['evidence.csv'] = sha('verified evidence\n');
    const manifestBytes = JSON.stringify(manifest) + '\n';
    for (const filename of ['public/omics/manifest.json', `public/omics/releases/${current}/manifest.json`, `data/omics/releases/${current}.json`]) write(root, filename, manifestBytes);
    const source = write(root, `public/omics/releases/${current}/evidence.csv`, 'incorrect evidence\n');
    const archive = path.join(root, `data/omics/releases/${current}/evidence.csv.gz`);
    await expect(packageWebsite({ dataDir: root })).rejects.toThrow('Prepared bytes differ from immutable receipt');
    expect(fs.existsSync(archive)).toBe(false);
    expect(fs.readdirSync(path.dirname(archive)).some(name => name.includes('.tmp-'))).toBe(false);
    fs.writeFileSync(source, 'verified evidence\n');
    await packageWebsite({ dataDir: root });
    expect(gunzipSync(fs.readFileSync(archive)).toString()).toBe('verified evidence\n');
  });

  it.each(['public/omics/catalogue.json', `public/omics/releases/${current}/catalogue.json`])('rejects a mismatched current catalogue pointer at %s', async filename => {
    const { root } = fixture();
    write(root, filename, '{"different":true}\n');
    await expect(packageWebsite({ dataDir: root })).rejects.toThrow('Current catalogue pointer differs');
    expect(fs.existsSync(path.join(root, 'website/manifest.json'))).toBe(false);
  });

  it('requires byte-identical top-level and immutable current manifests', async () => {
    const { root } = fixture();
    fs.appendFileSync(path.join(root, 'public/omics/manifest.json'), ' ');
    await expect(packageWebsite({ dataDir: root })).rejects.toThrow('Current manifest pointer differs');
  });

  it('creates the missing current archive receipt only from validated current outputs', async () => {
    const { root, latest } = fixture();
    fs.unlinkSync(path.join(root, `data/omics/releases/${current}.json`));
    const { manifest } = await packageWebsite({ dataDir: root });
    expect(fs.readFileSync(path.join(root, `data/omics/releases/${current}.json`), 'utf8')).toBe(latest.manifest);
    expect(manifest.files.filter(row => row.destination === `data/omics/releases/${current}.json`)).toHaveLength(1);
  });

  it('rejects a symlinked producer root without following it', async () => {
    const { root } = fixture();
    const alias = `${root}-alias`; roots.push(alias);
    fs.symlinkSync(root, alias);
    await expect(packageWebsite({ dataDir: alias })).rejects.toThrow('Symlink path');
    expect(fs.existsSync(path.join(root, 'website/manifest.json'))).toBe(false);
  });

  it.each(['public', 'data', 'lib'])('rejects symlinked parent directory %s', async directory => {
    const { root } = fixture();
    fs.renameSync(path.join(root, directory), path.join(root, `${directory}-actual`));
    fs.symlinkSync(path.join(root, `${directory}-actual`), path.join(root, directory));
    await expect(packageWebsite({ dataDir: root })).rejects.toThrow('Symlink path');
    expect(fs.existsSync(path.join(root, 'website/manifest.json'))).toBe(false);
  });

  it('rejects a symlinked output directory without touching its target', async () => {
    const { root } = fixture();
    const target = path.join(root, 'operator-files'); fs.mkdirSync(target);
    write(root, 'operator-files/notes.txt', 'preserve\n');
    fs.symlinkSync(target, path.join(root, 'website'));
    await expect(packageWebsite({ dataDir: root })).rejects.toThrow('Symlink path');
    expect(fs.readdirSync(target)).toEqual(['notes.txt']);
  });

});


describe('historical baseline audit preservation on clean builds', () => {
  async function prepared() {
    const value = fixture();
    for (const releaseId of [historical, current]) {
      const files: Record<string, string> = {};
      for (const name of ['coverage.json', 'model-evaluation-matrix.csv', 'protocol-baselines.csv', 'sources.csv', 'sources.json', 'suite-coverage.csv']) {
        const bytes = `Reviewed ${releaseId} ${name}\n`;
        write(value.root, `public/omics/baseline-coverage/${releaseId}/${name}`, bytes);
        files[name] = sha(bytes);
      }
      const receipt = JSON.parse(fs.readFileSync(path.join(value.root, `data/omics/releases/${releaseId}.json`), 'utf8'));
      write(value.root, `public/omics/baseline-coverage/${releaseId}/manifest.json`, JSON.stringify({
        release_id: releaseId, publication_status: 'published_release', catalogue_sha256: receipt.files['catalogue.json'], files,
      }) + '\n');
    }
    await packageWebsite({ dataDir: value.root });
    const inventoryPath = path.join(value.root, 'website/manifest.json');
    const inventoryBytes = fs.readFileSync(inventoryPath);
    const inventory = JSON.parse(inventoryBytes.toString()) as PreparedManifest;
    const oldDirectory = path.join(value.root, `public/omics/baseline-coverage/${historical}`);
    fs.rmSync(oldDirectory, { recursive: true });
    return { ...value, inventoryPath, inventoryBytes, inventory, oldDirectory };
  }

  it('reconstructs all prior audit bytes and reproduces the exact package inventory', async () => {
    const f = await prepared();
    await packageWebsite({ dataDir: f.root });
    expect(fs.readFileSync(f.inventoryPath)).toEqual(f.inventoryBytes);
    for (const entry of f.inventory.files.filter(entry => entry.destination.startsWith(`public/omics/baseline-coverage/${historical}/`))) {
      expect(fs.readFileSync(path.join(f.root, entry.destination))).toEqual(gunzipSync(fs.readFileSync(path.join(f.root, entry.source))));
    }
    const oldFile = path.join(f.oldDirectory, 'coverage.json');
    const before = fs.statSync(oldFile);
    await packageWebsite({ dataDir: f.root });
    expect(fs.statSync(oldFile).ino).toBe(before.ino);
    expect(fs.statSync(oldFile).mtimeMs).toBe(before.mtimeMs);
  });

  it('never restores missing current audit outputs from an old package', async () => {
    const f = await prepared();
    const currentDirectory = path.join(f.root, `public/omics/baseline-coverage/${current}`);
    fs.rmSync(currentDirectory, { recursive: true });
    const { manifest } = await packageWebsite({ dataDir: f.root });
    expect(fs.existsSync(currentDirectory)).toBe(false);
    expect(manifest.files.some(entry => entry.destination.startsWith(`public/omics/baseline-coverage/${current}/`))).toBe(false);
  });

  it('refuses corrupted compressed audit bytes without changing the package inventory', async () => {
    const f = await prepared();
    const entry = f.inventory.files.find(entry => entry.destination.endsWith(`${historical}/coverage.json`))!;
    fs.writeFileSync(path.join(f.root, entry.source), gzipSync('wrong bytes'));
    await expect(packageWebsite({ dataDir: f.root })).rejects.toThrow(/checksum or size mismatch/);
    expect(fs.existsSync(f.oldDirectory)).toBe(false);
    expect(fs.readFileSync(f.inventoryPath)).toEqual(f.inventoryBytes);
  });

  it('bounds historical inflation by the declared byte count', async () => {
    const f = await prepared();
    const entry = f.inventory.files.find(entry => entry.destination.endsWith(`${historical}/coverage.json`))!;
    fs.writeFileSync(path.join(f.root, entry.source), gzipSync(Buffer.alloc(1024 * 1024)));
    await expect(packageWebsite({ dataDir: f.root })).rejects.toThrow();
    expect(fs.existsSync(f.oldDirectory)).toBe(false);
  });

  it('rejects existing conflicting historical files without overwriting them', async () => {
    const f = await prepared();
    const target = write(f.root, `public/omics/baseline-coverage/${historical}/coverage.json`, 'preserve conflict');
    await expect(packageWebsite({ dataDir: f.root })).rejects.toThrow(/Immutable historical baseline conflict/);
    expect(fs.readFileSync(target, 'utf8')).toBe('preserve conflict');
  });

  it.each(['source', 'destination'])('rejects symlinked historical %s parents', async kind => {
    const f = await prepared();
    const directory = kind === 'source'
      ? path.join(f.root, `website/files/public/omics/baseline-coverage/${historical}`)
      : f.oldDirectory;
    const target = path.join(f.root, 'outside');
    if (kind === 'source') fs.renameSync(directory, target);
    else fs.mkdirSync(target);
    fs.symlinkSync(target, directory);
    await expect(packageWebsite({ dataDir: f.root })).rejects.toThrow(/Symlink path/);
  });

  it.each(['missing entry', 'unsafe source', 'unexpected name', 'wrong release binding'])('rejects %s in a historical audit', async kind => {
    const f = await prepared();
    const entry = f.inventory.files.find(entry => entry.destination.endsWith(`${historical}/coverage.json`))!;
    if (kind === 'missing entry') f.inventory.files = f.inventory.files.filter(row => row !== entry);
    else if (kind === 'unsafe source') entry.source = '../private.gz';
    else if (kind === 'unexpected name') entry.destination = `public/omics/baseline-coverage/${historical}/unexpected.json`;
    else {
      const manifestEntry = f.inventory.files.find(entry => entry.destination.endsWith(`${historical}/manifest.json`) && entry.destination.includes('baseline-coverage'))!;
      const audit = JSON.parse(gunzipSync(fs.readFileSync(path.join(f.root, manifestEntry.source))).toString());
      audit.catalogue_sha256 = '0'.repeat(64);
      const bytes = JSON.stringify(audit);
      fs.writeFileSync(path.join(f.root, manifestEntry.source), gzipSync(bytes));
      manifestEntry.sha256 = sha(bytes); manifestEntry.bytes = Buffer.byteLength(bytes);
    }
    fs.writeFileSync(f.inventoryPath, JSON.stringify(f.inventory));
    await expect(packageWebsite({ dataDir: f.root })).rejects.toThrow(/historical baseline|Historical baseline/);
    expect(fs.existsSync(f.oldDirectory)).toBe(false);
  });
});
