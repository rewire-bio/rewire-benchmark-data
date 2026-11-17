/** The measured licence numbers quoted in docs/source-preservation.md.
 *
 *   npx tsx scripts/licence/counts.ts
 *
 * One command for every figure in that document, so a reader can re-derive
 * each one instead of trusting it. Reads only the record store, the licence
 * map and the vocabularies. Writes nothing.
 */
import { determineForSource, readLicenceMap, readSourceLicences } from "./map";
import { buildTriage } from "./triage";
import { archiveTiers, visibilityOf, type ArchiveTier } from "../../shared/archive/schema";

function main(): void {
  const root = process.argv[2] ?? ".";
  const map = readLicenceMap(root);
  const licences = readSourceLicences(root);
  const withLicence = [...licences.values()].filter((licence) => licence !== null).length;

  const byTier = new Map<ArchiveTier, number>(archiveTiers.map((tier) => [tier, 0]));
  for (const id of licences.keys()) {
    const tier = determineForSource(id, map, licences).archive_tier;
    byTier.set(tier, (byTier.get(tier) ?? 0) + 1);
  }
  const byBasis = new Map<string, number>();
  const byFamily = new Map<string, number>();
  for (const licence of licences.values()) {
    if (licence === null) continue;
    const row = map.get(licence)!;
    byBasis.set(row.basis, (byBasis.get(row.basis) ?? 0) + 1);
    byFamily.set(row.family, (byFamily.get(row.family) ?? 0) + 1);
  }

  const pad = (value: unknown, width = 6) => String(value).padStart(width);
  console.log(`source records                     ${pad(licences.size)}`);
  console.log(`carrying a licence string          ${pad(withLicence)}`);
  console.log(`carrying none                      ${pad(licences.size - withLicence)}`);
  console.log(`distinct licence strings           ${pad(map.size)}`);
  console.log("");
  console.log("sources by tier");
  for (const tier of archiveTiers) console.log(`  ${tier.padEnd(20)} ${pad(byTier.get(tier))}  ${visibilityOf(tier)}`);
  const determinationBound = (["t1-public-nc", "t2-verbatim-nd", "t3-verbatim-nd-nc"] as ArchiveTier[]).reduce(
    (total, tier) => total + (byTier.get(tier) ?? 0),
    0,
  );
  console.log(`  publication resting on determinations 1 and 2: ${determinationBound}`);
  console.log("");
  console.log("sources by licence family");
  for (const [family, count] of [...byFamily].sort()) console.log(`  ${family.padEnd(20)} ${pad(count)}`);
  console.log("");
  console.log("sources by determination basis");
  for (const [basis, count] of [...byBasis].sort()) console.log(`  ${basis.padEnd(20)} ${pad(count)}`);
  console.log("");
  console.log(`licence triage queue               ${pad(buildTriage(root).length)}`);
}

main();
