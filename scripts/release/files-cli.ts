/** npm run verify:package | npm run release:fetch [-- <release-id>]; see files.ts. */
import { fetchRelease, newestPublished, verifyPackage } from "./files";

async function main() {
  const [command, id] = process.argv.slice(2);
  if (command === "verify") {
    const result = verifyPackage();
    console.log(`Verified ${result.sources} release files for ${result.releaseId}: present with the listed bytes, and not committed.`);
  } else if (command === "fetch") {
    const releaseId = id || await newestPublished();
    const counts = await fetchRelease(releaseId);
    console.log(`Release ${releaseId} files in data/omics/releases/${releaseId}/: ${counts.assets} from release assets, ${counts.git} from Git, ${counts.kept} already present.`);
  } else {
    throw new Error("Usage: tsx scripts/release/files-cli.ts verify | fetch [release-id]");
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});
