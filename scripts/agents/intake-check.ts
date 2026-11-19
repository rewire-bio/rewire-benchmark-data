/** Checks the intake agent runs on its batch before records -- add (#255). Exits 1 and lists the
 * problems when a record would fail a check that records -- add does not make:
 *   - normalizeAttributes would rewrite it (check C13 in scripts/omics/checks, which CI ratchets
 *     at zero), for example a review carrying `date` beside `reviewed_at`;
 *   - its depth tier differs from the rule in docs/tiers.md;
 *   - it is an evaluation, result or claim (intake adds entities only until #274).
 * Usage: npx tsx scripts/agents/intake-check.ts <batch.jsonl> */
import fs from "node:fs";
import { attributeIssues, normalizeAttributes } from "../../shared/omics/attributes";
import { deriveTier, tierKinds } from "../../shared/omics/depth-tier";

type Rec = { id: string; kind: string; links: { relation: string; target_id: string }[]; facets: { areas?: string[] }; attributes: Record<string, unknown> };

export function intakeProblems(records: Rec[]): string[] {
  const problems: string[] = [];
  const after = normalizeAttributes(records);
  records.forEach((record, i) => {
    if (!["model", "method", "benchmark", "dataset", "source"].includes(record.kind))
      problems.push(`${record.id}: kind ${record.kind} is not an entity the intake agent may add`);
    if (after[i] !== record) problems.push(`${record.id}: normalizeAttributes would rewrite its attributes (check C13)`);
    for (const issue of attributeIssues(record)) problems.push(`${record.id}: ${issue}`);
    const review = record.attributes.review as Record<string, unknown> | undefined;
    if (review && "date" in review) problems.push(`${record.id}: review carries date; use reviewed_at only`);
    if ((tierKinds as readonly string[]).includes(record.kind)) {
      const tier = deriveTier(record);
      if (tier === undefined || record.attributes.depth_tier !== tier)
        problems.push(`${record.id}: depth_tier ${String(record.attributes.depth_tier)} but the rule gives ${String(tier)}`);
    }
  });
  return problems;
}

if (process.argv[1]?.endsWith("intake-check.ts")) {
  const file = process.argv[2];
  if (!file) {
    console.error("Usage: npx tsx scripts/agents/intake-check.ts <batch.jsonl>");
    process.exit(1);
  }
  const records = fs.readFileSync(file, "utf8").split("\n").filter(Boolean).map((line) => JSON.parse(line) as Rec);
  const problems = intakeProblems(records);
  for (const p of problems) console.error(p);
  console.log(problems.length ? `${problems.length} problems in ${records.length} records.` : `${records.length} records pass the intake checks.`);
  process.exit(problems.length ? 1 : 0);
}
