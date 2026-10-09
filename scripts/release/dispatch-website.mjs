// Start rewire-database's adopt-data-release workflow after a release is
// published. GitHub's workflow token cannot reach another repository, so this
// needs the secret WEBSITE_DISPATCH_TOKEN: a fine-grained token for
// rewire-bio/rewire-database with Contents: read and write (needed by the
// repository dispatch API). Without it the release stays published and the
// website can adopt it by hand ("Adopt the newest data release").
import { execFileSync } from 'node:child_process';

if (!process.env.GH_TOKEN) {
  console.log('::warning::WEBSITE_DISPATCH_TOKEN is not set; run "Adopt the newest data release" in rewire-database to deploy this release.');
} else {
  execFileSync('gh', ['api', 'repos/rewire-bio/rewire-database/dispatches', '-f', 'event_type=data-release'], { stdio: 'inherit' });
  console.log('Dispatched data-release to rewire-bio/rewire-database.');
}
