// Release notes from the pull requests merged since the previous release.
// The previous release records the main commit it was built from (`source_revision` in
// data/omics/release-config.json). Every pull request merged on main's first-parent line
// after that commit gives one line: its title and number. Commits pushed directly to main,
// such as the release commits themselves, are left out.
import { execFileSync } from 'node:child_process';

const git = (...args) => execFileSync('git', args, { encoding: 'utf8', maxBuffer: 64 * 1024 ** 2 }).trim();

/** Changelog lines from `git log --first-parent --format=%s%x1f%b%x1e` output, oldest first. */
export function pullRequestLines(log) {
  const lines = [];
  for (const entry of log.split('\x1e')) {
    const [subject = '', body = ''] = entry.replace(/^\n+/, '').split('\x1f');
    const merge = /^Merge pull request #(\d+) from \S+/.exec(subject);
    const squash = /^(.*\S) \(#(\d+)\)$/.exec(subject);
    if (merge) {
      const title = body.split('\n').map(line => line.trim()).find(Boolean) || subject;
      lines.push(`${title} (#${merge[1]})`);
    } else if (squash) lines.push(`${squash[1]} (#${squash[2]})`);
  }
  return lines.reverse();
}

/** The pull requests merged between `since` and HEAD, or null if `since` is not in this clone. */
export function changelogSince(since) {
  try { git('cat-file', '-e', `${since}^{commit}`); } catch { return null; }
  return pullRequestLines(git('log', '--first-parent', '--format=%s%x1f%b%x1e', `${since}..HEAD`));
}

/** The commit the current release was built from: its recorded source, else the last commit that changed the config. */
export function previousSource(config, configFile) {
  return config.source_revision || git('log', '-1', '--format=%H', '--', configFile) || null;
}

export const head = () => git('rev-parse', 'HEAD');
