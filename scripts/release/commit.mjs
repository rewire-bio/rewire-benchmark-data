// The release commit and the check that a release tag names it (.github/workflows/release.yml, #267).
//   node scripts/release/commit.mjs commit <release-id>
//       commit the staged receipt, website manifest and release config on the commit the release
//       was built from, push it to main, and print the release commit's SHA
//   node scripts/release/commit.mjs verify <release-commit> [tag ...]
//       exit 1 unless the commit sits directly on the commit the release was built from
//       (`source_revision` in its data/omics/release-config.json), changes only data/ and
//       website/, and is on origin/main; with tags, also unless each tag on origin names it
//
// `commit` runs the first two of those checks before it pushes anything, so a commit that
// would fail them never reaches main. `verify` is for automated releases only. A release cut
// by hand (docs/release.md) is tagged at its pull request's merge commit, which data.yml
// rebuilt the release from in the same run.
//
// rewire-database pins the commit that `serving/<id>` names and copies shared/omics from it, so
// that commit must hold exactly the code the release was built with. When main has moved on
// while the release was being cut, the release commit is therefore merged into main, never
// rebased onto it: the merge keeps the release commit as it is, and the tag names it.
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const CONFIG = 'data/omics/release-config.json';
const RELEASE_PATHS = ['data/', 'website/'];

const runner = cwd => (...args) => execFileSync('git', args, { cwd, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], maxBuffer: 64 * 1024 ** 2 }).trim();
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));

/** Throws unless `sha` has one parent, the commit its release config says the release was built from, and changes only release paths. Returns that parent. */
function checkReleaseCommit(git, sha) {
  const built = JSON.parse(git('show', `${sha}:${CONFIG}`)).source_revision;
  if (!built) throw new Error(`${CONFIG} at ${sha} records no source_revision`);
  const parents = git('rev-list', '--parents', '-n', '1', sha).split(' ').slice(1);
  if (parents.length !== 1 || parents[0] !== built)
    throw new Error(`Release commit ${sha} has parent ${parents.join(' ') || '(none)'}, but the release was built from ${built}. The tag would name code the release was not built from.`);
  const outside = git('diff', '--name-only', built, sha).split('\n').filter(file => file && !RELEASE_PATHS.some(prefix => file.startsWith(prefix)));
  if (outside.length) throw new Error(`Release commit ${sha} changes files outside ${RELEASE_PATHS.join(' and ')}: ${outside.slice(0, 5).join(', ')}`);
  return built;
}

/**
 * Commit the release on the commit it was built from and push it to main. If main has moved
 * on, merge the release commit into the new main (main first, so its first-parent history
 * stays the list of merged pull requests) and push that. The work tree ends at the release
 * commit, so the publish steps run the code the release was built with.
 * The release commit is checked before the first push: a commit that is not on the commit the
 * release config names, or that changes other files, is refused and main is left as it was.
 * Returns { release, built, main }: the release commit, its parent, and the commit pushed to main.
 */
export async function commitRelease({ releaseId, cwd = process.cwd(), attempts = 5, wait = attempt => pause(attempt * 5000), log = console.error }) {
  const git = runner(cwd);
  const message = `Cut release ${releaseId} [skip ci]`;
  const built = git('rev-parse', 'HEAD');
  git('add', '-A', 'data', 'website');
  git('commit', '-m', message);
  const release = git('rev-parse', 'HEAD');
  // Nothing is pushed unless the commit can be tagged. A failure after the push would leave
  // main naming a release that cannot be published.
  checkReleaseCommit(git, release);
  log(`Release commit ${release}, made on ${built}.`);
  for (let attempt = 1; ; attempt++) {
    try {
      git('push', 'origin', 'HEAD:main');
      break;
    } catch (error) {
      if (attempt >= attempts) throw new Error(`Could not push the release after ${attempt} attempts: ${String(error.stderr || error.message).trim()}`);
    }
    await wait(attempt);
    git('fetch', 'origin', 'main');
    const remote = git('rev-parse', 'FETCH_HEAD');
    // The push failed for another reason and main is where this push expects it: push again.
    try { git('merge-base', '--is-ancestor', remote, 'HEAD'); continue; } catch { /* main has moved */ }
    // A pull request merged while this release was being cut. The next run releases it.
    git('checkout', '--detach', remote);
    git('merge', '--no-ff', '-m', message, release);
    log(`main moved to ${remote}; merged release commit ${release} into it.`);
  }
  const main = git('rev-parse', 'HEAD');
  if (main !== release) git('checkout', '--detach', release);
  return { release, built, main };
}

/** Throws unless `commit` is a release commit made directly on the commit its release was built from, and each given tag on origin names it. */
export function verifyReleaseCommit({ commit, tags = [], cwd = process.cwd() }) {
  const git = runner(cwd);
  const sha = git('rev-parse', `${commit}^{commit}`);
  const built = checkReleaseCommit(git, sha);
  try {
    git('merge-base', '--is-ancestor', sha, 'origin/main');
  } catch {
    throw new Error(`Release commit ${sha} is not on origin/main`);
  }
  for (const tag of tags) {
    const refs = new Map(git('ls-remote', 'origin', `refs/tags/${tag}`, `refs/tags/${tag}^{}`).split('\n').filter(Boolean).map(line => line.split('\t').reverse()));
    const target = refs.get(`refs/tags/${tag}^{}`) ?? refs.get(`refs/tags/${tag}`);
    if (target !== sha) throw new Error(`Tag ${tag} names ${target ?? 'nothing'}, not release commit ${sha}`);
  }
  return { release: sha, built };
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  const [command, argument, ...rest] = process.argv.slice(2);
  try {
    if (command === 'commit' && argument) {
      console.log((await commitRelease({ releaseId: argument })).release);
    } else if (command === 'verify' && argument) {
      const { release, built } = verifyReleaseCommit({ commit: argument, tags: rest });
      console.log(`Release commit ${release} sits on ${built}, the commit the release was built from${rest.length ? `; ${rest.join(' and ')} name it` : ''}.`);
    } else {
      throw new Error('Usage: commit.mjs commit <release-id> | verify <release-commit> [tag ...]');
    }
  } catch (error) {
    console.error(`::error::${error.message}`);
    process.exit(1);
  }
}
