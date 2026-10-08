/** Keep only the current release's files. The build archives a new release
 * under data/omics/releases/<id>/; earlier releases keep their receipts. */
import fs from "node:fs";
import path from "node:path";

const root = "data/omics/releases";
const current: string = JSON.parse(fs.readFileSync("public/omics/manifest.json", "utf8")).release_id;
if (!fs.existsSync(path.join(root, `${current}.json`)) || !fs.existsSync(path.join(root, current)))
  throw new Error(`Current release ${current} is not archived yet; run npm run build first`);
for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
  if (entry.isDirectory() && entry.name !== current) {
    fs.rmSync(path.join(root, entry.name), { recursive: true });
    console.log(`Removed files of ${entry.name}; its receipt is kept.`);
  }
}
