#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
import { fileURLToPath } from 'node:url';
import { pipeline } from 'node:stream/promises';
import { Transform } from 'node:stream';

/** Reject links in roots and parent directories as well as final files. */
function assertNoSymlinkPath(filename) {
  const absolute = path.resolve(filename);
  let prefix = path.parse(absolute).root;
  for (const segment of absolute.slice(prefix.length).split(path.sep).filter(Boolean)) {
    prefix = path.join(prefix, segment);
    let stat;
    try { stat = fs.lstatSync(prefix); }
    catch (error) { if (error.code === 'ENOENT') return; throw error; }
    if (stat.isSymbolicLink()) throw new Error(`Symlink path rejected: ${prefix}`);
  }
}

async function fileDigest(filename) {
  assertNoSymlinkPath(filename);
  if (!fs.lstatSync(filename).isFile()) throw new Error(`Expected a regular file: ${filename}`);
  const hash = crypto.createHash('sha256');
  for await (const chunk of fs.createReadStream(filename)) hash.update(chunk);
  return hash.digest('hex');
}

function checkedReleaseManifest(bytes, releaseId) {
  const manifest = JSON.parse(bytes.toString('utf8'));
  if (manifest.release_id !== releaseId || !manifest.files || typeof manifest.files !== 'object' || Array.isArray(manifest.files) ||
      !Object.entries(manifest.files).every(([name, hash]) => /^[a-zA-Z0-9][a-zA-Z0-9._-]*$/.test(name) && name !== 'manifest.json' && typeof hash === 'string' && /^[a-f0-9]{64}$/.test(hash)) ||
      !manifest.files['catalogue.json']) throw new Error(`Invalid immutable release manifest: ${releaseId}`);
  return manifest;
}

const BASELINE_FILES = [
  'coverage.json', 'manifest.json', 'model-evaluation-matrix.csv',
  'protocol-baselines.csv', 'sources.csv', 'sources.json', 'suite-coverage.csv',
];
const MAX_BASELINE_BYTES = 64 * 1024 ** 2;

/** Restore reviewed historical audits omitted by a clean current-release build. */
function restoreHistoricalBaselineAudits(dataDir, currentRelease) {
  const inventoryPath = path.join(dataDir, 'website/manifest.json');
  assertNoSymlinkPath(inventoryPath);
  if (!fs.existsSync(inventoryPath)) return;
  if (!fs.lstatSync(inventoryPath).isFile()) throw new Error('Prepared inventory must be a regular file');
  const inventory = JSON.parse(fs.readFileSync(inventoryPath, 'utf8'));
  if (inventory.schema_version !== 1 || !Array.isArray(inventory.files)) throw new Error('Invalid previous prepared inventory');
  const groups = new Map();
  for (const entry of inventory.files) {
    if (typeof entry?.destination !== 'string' || !entry.destination.startsWith('public/omics/baseline-coverage/')) continue;
    const match = /^public\/omics\/baseline-coverage\/(\d{4}-\d{2}-\d{2}-[a-f0-9]{12})\/([^/]+)$/.exec(entry.destination);
    if (!match || !BASELINE_FILES.includes(match[2])) throw new Error(`Unexpected historical baseline destination: ${entry.destination}`);
    const [, releaseId, name] = match;
    // Current outputs must come from this build, never from the prior package.
    if (releaseId === currentRelease) continue;
    const expectedSource = `website/files/${entry.destination}.gz`;
    if (entry.source !== expectedSource || entry.scope !== 'current' ||
        typeof entry.sha256 !== 'string' || !/^[a-f0-9]{64}$/.test(entry.sha256) ||
        !Number.isSafeInteger(entry.bytes) || entry.bytes < 0 || entry.bytes > MAX_BASELINE_BYTES) {
      throw new Error(`Invalid historical baseline metadata: ${entry.destination}`);
    }
    if (!groups.has(releaseId)) groups.set(releaseId, new Map());
    const group = groups.get(releaseId);
    if (group.has(name)) throw new Error(`Duplicate historical baseline entry: ${entry.destination}`);
    const source = path.join(dataDir, expectedSource);
    const destination = path.join(dataDir, entry.destination);
    assertNoSymlinkPath(source);
    assertNoSymlinkPath(destination);
    const sourceStat = fs.lstatSync(source);
    if (!sourceStat.isFile() || sourceStat.size > MAX_BASELINE_BYTES + 1024 ** 2) throw new Error(`Invalid historical baseline source: ${source}`);
    const bytes = zlib.gunzipSync(fs.readFileSync(source), { maxOutputLength: entry.bytes + 1 });
    if (bytes.length !== entry.bytes || crypto.createHash('sha256').update(bytes).digest('hex') !== entry.sha256) {
      throw new Error(`Historical baseline checksum or size mismatch: ${entry.destination}`);
    }
    if (fs.existsSync(destination) && (!fs.lstatSync(destination).isFile() || !fs.readFileSync(destination).equals(bytes))) {
      throw new Error(`Immutable historical baseline conflict: ${entry.destination}`);
    }
    group.set(name, { entry, destination, bytes });
  }
  // Validate complete audit groups and their archive binding before any writes.
  for (const [releaseId, group] of groups) {
    if (group.size !== BASELINE_FILES.length || BASELINE_FILES.some(name => !group.has(name))) {
      throw new Error(`Incomplete historical baseline audit: ${releaseId}`);
    }
    const receiptPath = path.join(dataDir, `data/omics/releases/${releaseId}.json`);
    assertNoSymlinkPath(receiptPath);
    if (!fs.lstatSync(receiptPath).isFile()) throw new Error(`Invalid historical receipt: ${releaseId}`);
    const receipt = checkedReleaseManifest(fs.readFileSync(receiptPath), releaseId);
    const audit = JSON.parse(group.get('manifest.json').bytes.toString('utf8'));
    if (audit.release_id !== releaseId || audit.publication_status !== 'published_release' ||
        audit.catalogue_sha256 !== receipt.files['catalogue.json'] ||
        !audit.files || typeof audit.files !== 'object' || Array.isArray(audit.files) ||
        Object.keys(audit.files).length !== BASELINE_FILES.length - 1 ||
        BASELINE_FILES.filter(name => name !== 'manifest.json').some(name => audit.files[name] !== group.get(name).entry.sha256)) {
      throw new Error(`Historical baseline release binding mismatch: ${releaseId}`);
    }
  }
  for (const group of groups.values()) {
    for (const { destination, bytes } of group.values()) {
      assertNoSymlinkPath(destination);
      if (fs.existsSync(destination)) continue;
      fs.mkdirSync(path.dirname(destination), { recursive: true });
      fs.writeFileSync(destination, bytes, { flag: 'wx' });
    }
  }
}

const MAX_COVERAGE_BYTES = 64 * 1024 ** 2;

/**
 * Restore reviewed historical public coverage exports omitted by a clean build.
 * Only paths already declared by the previous reviewed inventory are restored,
 * from their exact reviewed compressed sources; the current release's coverage
 * export must always come from this build.
 */
function restoreHistoricalCoverageExports(dataDir, currentRelease) {
  const inventoryPath = path.join(dataDir, 'website/manifest.json');
  assertNoSymlinkPath(inventoryPath);
  if (!fs.existsSync(inventoryPath)) return;
  if (!fs.lstatSync(inventoryPath).isFile()) throw new Error('Prepared inventory must be a regular file');
  const inventory = JSON.parse(fs.readFileSync(inventoryPath, 'utf8'));
  if (inventory.schema_version !== 1 || !Array.isArray(inventory.files)) throw new Error('Invalid previous prepared inventory');
  const restores = new Map();
  for (const entry of inventory.files) {
    if (typeof entry?.destination !== 'string' || !entry.destination.startsWith('public/omics/coverage/')) continue;
    const match = /^public\/omics\/coverage\/(\d{4}-\d{2}-\d{2}-[a-f0-9]{12})\.json$/.exec(entry.destination);
    if (!match) throw new Error(`Unexpected historical coverage destination: ${entry.destination}`);
    const releaseId = match[1];
    // Current outputs must come from this build, never from the prior package.
    if (releaseId === currentRelease) continue;
    const expectedSource = `website/files/${entry.destination}.gz`;
    if (entry.source !== expectedSource || entry.scope !== 'current' ||
        typeof entry.sha256 !== 'string' || !/^[a-f0-9]{64}$/.test(entry.sha256) ||
        !Number.isSafeInteger(entry.bytes) || entry.bytes < 0 || entry.bytes > MAX_COVERAGE_BYTES) {
      throw new Error(`Invalid historical coverage metadata: ${entry.destination}`);
    }
    if (restores.has(releaseId)) throw new Error(`Duplicate historical coverage entry: ${entry.destination}`);
    const source = path.join(dataDir, expectedSource);
    const destination = path.join(dataDir, entry.destination);
    assertNoSymlinkPath(source);
    assertNoSymlinkPath(destination);
    const sourceStat = fs.lstatSync(source);
    if (!sourceStat.isFile() || sourceStat.size > MAX_COVERAGE_BYTES + 1024 ** 2) throw new Error(`Invalid historical coverage source: ${source}`);
    const bytes = zlib.gunzipSync(fs.readFileSync(source), { maxOutputLength: entry.bytes + 1 });
    if (bytes.length !== entry.bytes || crypto.createHash('sha256').update(bytes).digest('hex') !== entry.sha256) {
      throw new Error(`Historical coverage checksum or size mismatch: ${entry.destination}`);
    }
    if (fs.existsSync(destination) && (!fs.lstatSync(destination).isFile() || !fs.readFileSync(destination).equals(bytes))) {
      throw new Error(`Immutable historical coverage conflict: ${entry.destination}`);
    }
    restores.set(releaseId, { destination, bytes });
  }
  // Bind each export to its own immutable release receipt before any writes.
  for (const [releaseId, { bytes }] of restores) {
    const receiptPath = path.join(dataDir, `data/omics/releases/${releaseId}.json`);
    assertNoSymlinkPath(receiptPath);
    if (!fs.existsSync(receiptPath) || !fs.lstatSync(receiptPath).isFile()) throw new Error(`Invalid historical receipt: ${releaseId}`);
    const receiptBytes = fs.readFileSync(receiptPath);
    const receipt = checkedReleaseManifest(receiptBytes, releaseId);
    const coverage = JSON.parse(bytes.toString('utf8'));
    if (coverage === null || typeof coverage !== 'object' || Array.isArray(coverage) || coverage.release_id !== releaseId ||
        (typeof receipt.released_at === 'string' && coverage.released_at !== receipt.released_at)) {
      throw new Error(`Historical coverage release binding mismatch: ${releaseId}`);
    }
  }
  for (const { destination, bytes } of restores.values()) {
    assertNoSymlinkPath(destination);
    if (fs.existsSync(destination)) continue;
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    fs.writeFileSync(destination, bytes, { flag: 'wx' });
  }
}

/**
 * Recursively collect regular files from a directory, rejecting symlinks.
 * @param {string} dir
 * @returns {string[]} absolute file paths
 */
function collectRegularFiles(dir) {
  assertNoSymlinkPath(dir);
  const results = [];
  if (!fs.existsSync(dir)) return results;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    const lstat = fs.lstatSync(fullPath);
    if (lstat.isSymbolicLink()) {
      throw new Error(`Symlink source rejected: ${fullPath}`);
    }
    if (entry.isDirectory()) {
      results.push(...collectRegularFiles(fullPath));
    } else if (entry.isFile()) {
      results.push(fullPath);
    } else {
      throw new Error(`Unsupported non-regular file: ${fullPath}`);
    }
  }
  return results;
}

/**
 * Stream an uncompressed source file to a gzip destination, computing
 * uncompressed sha256 and byte length on the fly.
 * @param {string} sourcePath
 * @param {string} targetGzPath
 * @param {string | undefined} [expectedSha256]
 * @returns {Promise<{ sha256: string, bytes: number }>}
 */
async function streamGzipAndHash(sourcePath, targetGzPath, expectedSha256) {
  assertNoSymlinkPath(sourcePath);
  assertNoSymlinkPath(targetGzPath);
  const lstat = fs.lstatSync(sourcePath);
  if (lstat.isSymbolicLink()) {
    throw new Error(`Symlink source rejected: ${sourcePath}`);
  }
  if (!lstat.isFile()) {
    throw new Error(`Expected a regular file: ${sourcePath}`);
  }

  fs.mkdirSync(path.dirname(targetGzPath), { recursive: true });
  const tempTarget = `${targetGzPath}.tmp-${Date.now()}-${Math.random().toString(36).slice(2)}`;

  const readStream = fs.createReadStream(sourcePath);
  const hasher = crypto.createHash('sha256');
  let bytes = 0;

  const tap = new Transform({
    transform(chunk, encoding, callback) {
      bytes += chunk.length;
      hasher.update(chunk);
      callback(null, chunk);
    },
  });

  const gzip = zlib.createGzip({ level: zlib.constants.Z_DEFAULT_COMPRESSION });
  const writeStream = fs.createWriteStream(tempTarget);

  let sha256;
  try {
    await pipeline(readStream, tap, gzip, writeStream);
    sha256 = hasher.digest('hex');
    if (expectedSha256 && sha256 !== expectedSha256) throw new Error(`Prepared bytes differ from immutable receipt: ${sourcePath}`);
    assertNoSymlinkPath(targetGzPath);
    fs.renameSync(tempTarget, targetGzPath);
  } catch (err) {
    try {
      if (fs.existsSync(tempTarget)) fs.unlinkSync(tempTarget);
    } catch {}
    throw err;
  }

  return { sha256, bytes };
}

/**
 * Package prepared outputs into website/ in the data repository.
 *
 * @param {object} [options]
 * @param {string} [options.dataDir] - Root of the benchmark data repository
 * @param {string} [options.outputDir] - Directory where website package should be written (default: <dataDir>/website)
 * @param {boolean} [options.currentOnly] - If true, skip historical public outputs (keep receipts)
 * @returns {Promise<{ manifest: object, manifestPath: string, filesCount: number }>}
 */
export async function packageWebsite(options = {}) {
  const defaultDataDir = path.resolve(fileURLToPath(import.meta.url), '..', '..');
  const dataDir = path.resolve(options.dataDir || defaultDataDir);
  const outputDir = path.resolve(options.outputDir || path.join(dataDir, 'website'));
  assertNoSymlinkPath(dataDir);
  assertNoSymlinkPath(outputDir);
  if (!fs.lstatSync(dataDir).isDirectory()) throw new Error('Data root must be a directory');
  const currentOnly = Boolean(
    options.currentOnly ?? process.argv.includes('--current-only'),
  );

  // 1. Read release_id from public/omics/manifest.json
  const omicsManifestPath = path.join(dataDir, 'public', 'omics', 'manifest.json');
  assertNoSymlinkPath(omicsManifestPath);
  if (!fs.existsSync(omicsManifestPath)) {
    throw new Error(
      `Missing ${omicsManifestPath}. The data release generator must run before packaging website outputs.`,
    );
  }
  const omicsManifestStat = fs.lstatSync(omicsManifestPath);
  if (omicsManifestStat.isSymbolicLink() || !omicsManifestStat.isFile()) {
    throw new Error(`Invalid manifest file: ${omicsManifestPath}`);
  }
  const topManifestBytes = fs.readFileSync(omicsManifestPath);
  const omicsManifest = JSON.parse(topManifestBytes.toString('utf8'));
  const releaseId = omicsManifest.release_id;
  if (typeof releaseId !== 'string' || !/^\d{4}-\d{2}-\d{2}-[a-f0-9]{12}$/.test(releaseId)) {
    throw new Error(`Invalid or missing release_id in ${omicsManifestPath}`);
  }

  restoreHistoricalBaselineAudits(dataDir, releaseId);
  restoreHistoricalCoverageExports(dataDir, releaseId);

  /** @type {Array<{ filePath: string, destination: string, scope: 'current' | 'historical' }>} */
  const items = [];

  // 2. Include every public/omics file
  // Current scope for current release and all non-historical paths; historical scope for old public/omics/releases.
  const publicOmicsDir = path.join(dataDir, 'public', 'omics');
  if (fs.existsSync(publicOmicsDir)) {
    const omicsFiles = collectRegularFiles(publicOmicsDir);
    for (const fullPath of omicsFiles) {
      const rel = path.relative(dataDir, fullPath).split(path.sep).join('/');
      const destination = rel;
      if (destination.startsWith('public/omics/releases/')) {
        const parts = destination.split('/');
        const releaseFolder = parts[3];
        if (releaseFolder === releaseId) {
          items.push({ filePath: fullPath, destination, scope: 'current' });
        } else {
          if (!currentOnly) {
            items.push({ filePath: fullPath, destination, scope: 'historical' });
          }
        }
      } else {
        items.push({ filePath: fullPath, destination, scope: 'current' });
      }
    }
  }

  // 3. Include public/benchmark-literature exports
  const publicLitDir = path.join(dataDir, 'public', 'benchmark-literature');
  if (fs.existsSync(publicLitDir)) {
    const litFiles = collectRegularFiles(publicLitDir);
    for (const fullPath of litFiles) {
      const rel = path.relative(dataDir, fullPath).split(path.sep).join('/');
      items.push({ filePath: fullPath, destination: rel, scope: 'current' });
    }
  }

  // 4. Include frontend raw inputs
  const rawInputFiles = [
    'data/benchmark-literature/papers.json',
    'data/benchmark-literature/results.csv',
    'data/benchmark-runs/mfass-v2.json',
    'data/omics/scope-audit.jsonl',
  ];
  for (const rawRel of rawInputFiles) {
    const fullPath = path.join(dataDir, rawRel);
    if (fs.existsSync(fullPath)) {
      assertNoSymlinkPath(fullPath);
      const stat = fs.lstatSync(fullPath);
      if (stat.isSymbolicLink() || !stat.isFile()) {
        throw new Error(`Raw input must be a regular file: ${fullPath}`);
      }
      items.push({ filePath: fullPath, destination: rawRel, scope: 'current' });
    }
  }

  // Store the current receipt with the immutable archives. The generator only
  // writes public exports; release adoption also needs this canonical receipt.
  const currentReceipt = path.join(dataDir, 'data/omics/releases', `${releaseId}.json`);
  assertNoSymlinkPath(currentReceipt);
  const currentManifestPath = path.join(publicOmicsDir, 'releases', releaseId, 'manifest.json');
  assertNoSymlinkPath(currentManifestPath);
  const currentReceiptBytes = fs.readFileSync(currentManifestPath);
  checkedReleaseManifest(currentReceiptBytes, releaseId);
  if (!topManifestBytes.equals(currentReceiptBytes)) throw new Error('Current manifest pointer differs from immutable release');
  if (fs.existsSync(currentReceipt) && !fs.readFileSync(currentReceipt).equals(currentReceiptBytes)) throw new Error('Immutable current receipt conflict');
  const needsCurrentReceipt = !fs.existsSync(currentReceipt);
  if (needsCurrentReceipt) items.push({ filePath: currentReceipt, destination: `data/omics/releases/${releaseId}.json`, scope: 'current' });

  // 5. Include all data/omics/releases/*.json receipts
  const receiptsDir = path.join(dataDir, 'data', 'omics', 'releases');
  assertNoSymlinkPath(receiptsDir);
  if (fs.existsSync(receiptsDir)) {
    const receiptEntries = fs.readdirSync(receiptsDir, { withFileTypes: true });
    for (const entry of receiptEntries) {
      if (entry.isSymbolicLink()) throw new Error(`Symlink receipt rejected: ${entry.name}`);
      if (entry.isFile() && entry.name.endsWith('.json')) {
        const fullPath = path.join(receiptsDir, entry.name);
        const stat = fs.lstatSync(fullPath);
        if (stat.isSymbolicLink() || !stat.isFile()) {
          throw new Error(`Receipt must be a regular file: ${fullPath}`);
        }
        const destination = `data/omics/releases/${entry.name}`;
        items.push({ filePath: fullPath, destination, scope: 'current' });
      }
    }
  }

  // 6. Include legacy candidate catalogue lib/benchmark-catalog.ts as destination lib/generated-benchmark-catalog.ts
  const legacyCatalogPath = path.join(dataDir, 'lib', 'benchmark-catalog.ts');
  if (fs.existsSync(legacyCatalogPath)) {
    assertNoSymlinkPath(legacyCatalogPath);
    const stat = fs.lstatSync(legacyCatalogPath);
    if (stat.isSymbolicLink() || !stat.isFile()) {
      throw new Error(`Legacy catalogue must be a regular file: ${legacyCatalogPath}`);
    }
    items.push({
      filePath: legacyCatalogPath,
      destination: 'lib/generated-benchmark-catalog.ts',
      scope: 'current',
    });
  }

  const required = [
    ...rawInputFiles, 'lib/generated-benchmark-catalog.ts',
    'public/benchmark-literature/papers.json', 'public/benchmark-literature/results.csv',
    'public/omics/manifest.json', 'public/omics/catalogue.json',
    `public/omics/releases/${releaseId}/manifest.json`,
    ...Object.keys(omicsManifest.files).map(name => `public/omics/releases/${releaseId}/${name}`),
  ];
  const destinations = new Set(items.map(item => item.destination));
  if (destinations.size !== items.length) throw new Error('Duplicate prepared destination');
  for (const name of required) if (!destinations.has(name)) throw new Error(`Missing required prepared input: ${name}`);
  if (await fileDigest(path.join(publicOmicsDir, 'catalogue.json')) !== omicsManifest.files['catalogue.json'] ||
      await fileDigest(path.join(publicOmicsDir, 'releases', releaseId, 'catalogue.json')) !== omicsManifest.files['catalogue.json']) {
    throw new Error('Current catalogue pointer differs from immutable release');
  }
  if (needsCurrentReceipt) {
    fs.mkdirSync(receiptsDir, { recursive: true });
    fs.writeFileSync(currentReceipt, currentReceiptBytes, { flag: 'wx' });
  }
  if (!currentOnly) {
    for (const name of fs.readdirSync(receiptsDir).filter(name => name.endsWith('.json'))) {
      const receipt = checkedReleaseManifest(fs.readFileSync(path.join(receiptsDir, name)), name.slice(0, -5));
      for (const file of ['manifest.json', ...Object.keys(receipt.files)]) {
        if (!destinations.has(`public/omics/releases/${receipt.release_id}/${file}`)) throw new Error(`Incomplete historical release: ${receipt.release_id}/${file}`);
      }
    }
  }
  const filesOutputDir = path.join(outputDir, 'files');
  fs.mkdirSync(filesOutputDir, { recursive: true });
  const manifestFiles = [];
  for (const item of items) {
    const destPath = item.destination;
    let sourceInManifest = path.posix.join('website', 'files', destPath) + '.gz';
    let targetGzPath = path.join(dataDir, sourceInManifest);
    const archive = /^public\/omics\/releases\/([0-9a-f-]+)\/(.+)$/.exec(destPath);
    // Reuse existing compressed scientific archives instead of storing a second
    // 2.5 GB copy. New release files become canonical immutable archives here.
    if (archive && archive[2] !== 'manifest.json') {
      const candidate = `data/omics/releases/${archive[1]}/${archive[2]}.gz`;
      const legacyBundle = path.join(receiptsDir, `${archive[1]}.bundle.json.gz`);
      if (!fs.existsSync(legacyBundle)) {
        sourceInManifest = candidate;
        targetGzPath = path.join(dataDir, candidate);
      }
    }
    assertNoSymlinkPath(targetGzPath);
    let expectedSha256;
    if (archive) {
      const receiptPath = path.join(receiptsDir, `${archive[1]}.json`);
      assertNoSymlinkPath(receiptPath);
      const receiptBytes = fs.readFileSync(receiptPath);
      const receipt = checkedReleaseManifest(receiptBytes, archive[1]);
      expectedSha256 = archive[2] === 'manifest.json'
        ? crypto.createHash('sha256').update(receiptBytes).digest('hex')
        : receipt.files[archive[2]];
      if (!expectedSha256) throw new Error(`Unreceipted release file: ${destPath}`);
    }
    let sha256, bytes;
    if (fs.existsSync(targetGzPath)) {
      if (!fs.lstatSync(targetGzPath).isFile()) throw new Error(`Archive is not a regular file: ${targetGzPath}`);
      const original = crypto.createHash('sha256'); bytes = 0;
      for await (const chunk of fs.createReadStream(item.filePath)) { original.update(chunk); bytes += chunk.length; }
      sha256 = original.digest('hex');
      if (expectedSha256 && expectedSha256 !== sha256) throw new Error(`Prepared bytes differ from immutable receipt: ${destPath}`);
      const archived = crypto.createHash('sha256'); let archivedBytes = 0;
      for await (const chunk of fs.createReadStream(targetGzPath).pipe(zlib.createGunzip())) { archived.update(chunk); archivedBytes += chunk.length; }
      if (archived.digest('hex') !== sha256 || archivedBytes !== bytes) {
        if (sourceInManifest.startsWith('data/omics/releases/')) throw new Error(`Immutable archive conflict: ${sourceInManifest}`);
        ({ sha256, bytes } = await streamGzipAndHash(item.filePath, targetGzPath, expectedSha256));
      }
    } else ({ sha256, bytes } = await streamGzipAndHash(item.filePath, targetGzPath, expectedSha256));
    manifestFiles.push({ source: sourceInManifest, destination: destPath, sha256, bytes, scope: item.scope });
  }

  // 9. Deterministic sort by destination
  manifestFiles.sort((a, b) => a.destination.localeCompare(b.destination));

  // 10. Write website/manifest.json
  const manifest = {
    schema_version: 1,
    release_id: releaseId,
    files: manifestFiles,
  };
  const manifestPath = path.join(outputDir, 'manifest.json');
  assertNoSymlinkPath(manifestPath);
  const temporaryManifest = `${manifestPath}.tmp-${crypto.randomUUID()}`;
  try {
    fs.writeFileSync(temporaryManifest, JSON.stringify(manifest, null, 2) + '\n', { flag: 'wx' });
    fs.renameSync(temporaryManifest, manifestPath);
  } finally {
    if (fs.existsSync(temporaryManifest)) fs.unlinkSync(temporaryManifest);
  }

  return {
    manifest,
    manifestPath,
    filesCount: manifestFiles.length,
  };
}

// CLI execution guard
if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  const currentOnly = process.argv.includes('--current-only');
  let dataDir;
  const dataDirIdx = process.argv.indexOf('--data-dir') !== -1
    ? process.argv.indexOf('--data-dir')
    : process.argv.indexOf('--root');
  if (dataDirIdx !== -1 && dataDirIdx + 1 < process.argv.length) {
    dataDir = process.argv[dataDirIdx + 1];
  }
  let outputDir;
  const outIdx = process.argv.indexOf('--output');
  if (outIdx !== -1 && outIdx + 1 < process.argv.length) {
    outputDir = process.argv[outIdx + 1];
  }

  packageWebsite({ dataDir, outputDir, currentOnly })
    .then(({ manifest, filesCount }) => {
      console.log(
        `Packaged benchmark website data (${manifest.release_id}): ${filesCount} files (current-only: ${currentOnly})`,
      );
    })
    .catch((err) => {
      console.error(`Packaging failed: ${err.message}`);
      process.exit(1);
    });
}
