// Parse every planned profile and run guide of a batch with the store's own schemas.
// Usage: npx tsx scripts/enrich/validate.ts <batch name>
import fs from "node:fs";
import { profileSchema } from "../../shared/omics/profile-schema";
import { runGuideSchema } from "../../shared/omics/run-guide";

const dir = `data/omics/${process.argv[2]}`;
const planFile = ["models.json", "benchmarks.json"].map((name) => `${dir}/${name}`).find((path) => fs.existsSync(path));
if (!planFile) throw new Error(`${dir} has no models.json or benchmarks.json`);
const plan = JSON.parse(fs.readFileSync(planFile, "utf8")) as Record<string, { profile: unknown; run_guide: unknown }>;
let failed = 0;
for (const [id, entry] of Object.entries(plan)) {
  const profile = profileSchema.safeParse(entry.profile);
  const guide = entry.run_guide ? runGuideSchema.safeParse(entry.run_guide) : null;
  const error = !profile.success ? profile.error : guide && !guide.success ? guide.error : null;
  if (error) { failed++; console.log(id, JSON.stringify(error.issues.slice(0, 3))); }
}
console.log(`${Object.keys(plan).length} checked, ${failed} failed`);
process.exit(failed ? 1 : 0);
