// Automated release support (.github/workflows/release.yml).
//   node scripts/release/next.mjs prepare   set released_at to now; print the current release ID
//   node scripts/release/next.mjs latest    print the newest release whose files are present
//   node scripts/release/next.mjs withheld <previous-id> <next-id>
//       exit 4 if the next release withholds or drops use-case mappings that the
//       previous release serves, unless the judgement was withdrawn on purpose
//       (its claim is excluded or superseded in data/evidence/claims.jsonl)
//   node scripts/release/next.mjs pending <previous-id> <next-id> [published-serving-receipt]
//       exit 0 if the next release differs from the previous one in anything but
//       its release ID and date (new or changed records, evidence, audits, use
//       cases, exports), or if its prepared file uses a different serving contract
//       from the one published for the previous release; exit 3 if it is the same
//       release under a new name.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import readline from 'node:readline';

const releases = 'data/omics/releases';
const configFile = 'data/omics/release-config.json';
const [command, previous, next, publishedReceipt] = process.argv.slice(2);

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
  // A withheld mapping is one the previous release served that is now needs_review: older
  // releases mark it with stale_from, newer ones derive it from its relevance judgement.
  const withheld = (after?.mappings || []).filter(mapping => live.has(mapping.id) && !['active', 'withdrawn', 'superseded'].includes(mapping.lifecycle));
  // A served mapping missing from the next release counts too, unless its judgement was withdrawn.
  const present = new Set((after?.mappings || []).map(mapping => mapping.id));
  const withdrawn = new Set(fs.readFileSync('data/evidence/claims.jsonl', 'utf8').split('\n').filter(Boolean)
    .map(line => JSON.parse(line)).filter(claim => ['excluded', 'superseded'].includes(claim.status)).map(claim => claim.id));
  for (const id of live) if (!present.has(id) && !withdrawn.has(id)) withheld.push({ id, reason: 'missing from the release without a withdrawn judgement' });
  if (withheld.length) {
    const detail = withheld.slice(0, 10).map(mapping => `${mapping.id} (${mapping.reason})`).join('; ');
    console.log(`::error::${next} withholds ${withheld.length} use-case mappings that ${previous} serves: ${detail}. Re-review their relevance judgements and re-pin them (npm run use-cases:repin -- <review> <claim-id>...), or withdraw them by excluding the claim, before releasing.`);
    process.exitCode = 4;
  } else console.log(`No use-case mapping that ${previous} serves is withheld or dropped by ${next}.`);
} else if (command === 'pending') {
  if (!previous || !next) throw new Error('Usage: next.mjs pending <previous-id> <next-id>');
  const a = releaseOf(previous), b = releaseOf(next);
  const normalise = line => line.split(b.id).join(a.id).split(b.released_at).join(a.released_at);
  const before = await digests(a.id), after = await digests(b.id, normalise);
  const changed = [...new Set([...before.keys(), ...after.keys()])]
    .filter(name => before.get(name) !== after.get(name));
  // The prepared file is published beside the release, not in it, so a new serving
  // contract with unchanged records still needs a release for the website to adopt it.
  const contract = file => fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')).serving_contract_version : null;
  const published = publishedReceipt ? contract(publishedReceipt) : null;
  const built = contract(path.join('public/serving', `catalogue-${b.id}.json`));
  if (changed.length) {
    console.log(`Release ${b.id} changes ${changed.length} file(s) against ${a.id}: ${changed.slice(0, 10).join(', ')}`);
  } else if (published && built && published !== built) {
    console.log(`Release ${b.id} has the same records as ${a.id} but serving contract ${built} instead of ${published}.`);
  } else {
    console.log(`Release ${b.id} only renames ${a.id}; nothing to release.`);
    process.exitCode = 3;
  }
} else {
  throw new Error('Usage: next.mjs prepare | latest | withheld <previous-id> <next-id> | pending <previous-id> <next-id>');
}
