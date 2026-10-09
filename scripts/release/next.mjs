// Automated release support (.github/workflows/release.yml).
//   node scripts/release/next.mjs prepare   set released_at to now; print the current release ID
//   node scripts/release/next.mjs latest    print the newest release whose files are present
//   node scripts/release/next.mjs withheld <previous-id> <next-id>
//       exit 4 if the next release automatically withholds use-case mappings
//       that the previous release serves (their evidence changed since review)
//   node scripts/release/next.mjs pending <previous-id> <next-id>
//       exit 0 if the next release differs from the previous one in anything but
//       its release ID and date (new or changed records, evidence, audits, use
//       cases, exports); exit 3 if it is the same release under a new name.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import readline from 'node:readline';

const releases = 'data/omics/releases';
const configFile = 'data/omics/release-config.json';
const [command, previous, next] = process.argv.slice(2);

function releaseOf(id) {
  const receipt = JSON.parse(fs.readFileSync(path.join(releases, `${id}.json`), 'utf8'));
  return { id, released_at: receipt.released_at };
}
// Hash each file line by line (some decompress to more than Node's string limit),
// after mapping the release's own ID and date to the ones it is compared with.
async function digests(id, normalise = line => line) {
  const directory = path.join(releases, id);
  const files = new Map();
  for (const name of fs.readdirSync(directory).sort()) {
    const raw = fs.createReadStream(path.join(directory, name));
    const input = readline.createInterface({ input: name.endsWith('.gz') ? raw.pipe(zlib.createGunzip()) : raw, crlfDelay: Infinity });
    const hash = crypto.createHash('sha256');
    for await (const line of input) hash.update(normalise(line) + '\n');
    files.set(name.replace(/\.gz$/, ''), hash.digest('hex'));
  }
  return files;
}

// Newest by its receipt's released_at; IDs end in a hash, so names do not sort by time.
function latest() {
  return fs.readdirSync(releases).filter(name => fs.statSync(path.join(releases, name)).isDirectory())
    .map(releaseOf).sort((a, b) => a.released_at.localeCompare(b.released_at)).pop()?.id;
}

if (command === 'latest') {
  console.log(latest());
} else if (command === 'prepare') {
  const config = JSON.parse(fs.readFileSync(configFile, 'utf8'));
  const current = latest();
  config.released_at = new Date(Math.floor(Date.now() / 1000) * 1000).toISOString();
  fs.writeFileSync(configFile, JSON.stringify(config, null, 2) + '\n');
  console.log(current);
} else if (command === 'withheld') {
  if (!previous || !next) throw new Error('Usage: next.mjs withheld <previous-id> <next-id>');
  const useCases = id => {
    const file = path.join(releases, id, 'use-cases.json.gz');
    return fs.existsSync(file) ? JSON.parse(zlib.gunzipSync(fs.readFileSync(file)).toString('utf8')) : null;
  };
  const before = useCases(previous), after = useCases(next);
  const live = new Set((before?.mappings || []).filter(mapping => mapping.lifecycle === 'active').map(mapping => mapping.id));
  const withheld = (after?.mappings || []).filter(mapping => live.has(mapping.id) && mapping.lifecycle !== 'active' && mapping.stale_from).map(mapping => mapping.id);
  if (withheld.length) {
    console.log(`::error::${next} withholds ${withheld.length} use-case mappings that ${previous} serves, because their evidence changed since review: ${withheld.slice(0, 10).join(', ')}. Re-review them (update their evidence_sha256 in data/omics/use-cases/inputs.json after review) before releasing.`);
    process.exitCode = 4;
  } else console.log(`No use-case mapping that ${previous} serves is withheld by ${next}.`);
} else if (command === 'pending') {
  if (!previous || !next) throw new Error('Usage: next.mjs pending <previous-id> <next-id>');
  const a = releaseOf(previous), b = releaseOf(next);
  const normalise = line => line.split(b.id).join(a.id).split(b.released_at).join(a.released_at);
  const before = await digests(a.id), after = await digests(b.id, normalise);
  const changed = [...new Set([...before.keys(), ...after.keys()])]
    .filter(name => before.get(name) !== after.get(name));
  if (changed.length) {
    console.log(`Release ${b.id} changes ${changed.length} file(s) against ${a.id}: ${changed.slice(0, 10).join(', ')}`);
  } else {
    console.log(`Release ${b.id} only renames ${a.id}; nothing to release.`);
    process.exitCode = 3;
  }
} else {
  throw new Error('Usage: next.mjs prepare | latest | withheld <previous-id> <next-id> | pending <previous-id> <next-id>');
}
