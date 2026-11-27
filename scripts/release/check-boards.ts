/** npm run boards:check: the current release's boards file (kb/board.py) is valid and names the release.
 * Reads public/omics/manifest.json for the release id; the file is public/omics/boards/<release_id>.json. */
import fs from "node:fs";
import { parseBoards } from "../../shared/omics/boards";

const releaseId: string = JSON.parse(fs.readFileSync("public/omics/manifest.json", "utf8")).release_id;
const file = `public/omics/boards/${releaseId}.json`;
try {
  const boards = parseBoards(JSON.parse(fs.readFileSync(file, "utf8")), releaseId);
  const ranked = boards.boards.filter((b) => b.rows.length).length;
  console.log(`${file}: ${boards.boards.length} boards, ${ranked} with a ranking.`);
} catch (error) {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
}
