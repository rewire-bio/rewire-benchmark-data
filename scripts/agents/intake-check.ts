/** Checks the intake agent runs on its batch before records -- add (#255). Exits 1 and lists the
 * problems when a record would fail a check that records -- add does not make:
 *   - normalizeAttributes would rewrite it (check C13 in scripts/omics/checks, which CI ratchets
 *     at zero), for example a review carrying `date` beside `reviewed_at`;
 *   - its depth tier differs from the rule in docs/tiers.md;
 *   - it is an evaluation, result or claim (intake adds entities only until #274);
 *   - the release would refuse it (validateSnapshot, the check tests/release-validation.test.ts
 *     runs on the whole store), for example a model without entity_level.
 * Usage: npx tsx scripts/agents/intake-check.ts <batch.jsonl>... (an update checks its changed record and its new sources together) */
import fs from "node:fs";
import { attributeIssues, normalizeAttributes } from "../../shared/omics/attributes";
import { deriveTier, tierKinds } from "../../shared/omics/depth-tier";
import { relationAllows } from "../../shared/omics/relations";
import { validateSnapshot } from "../../shared/omics/validation";
import { ZodError } from "zod";

type Rec = { id: string; kind: string; links: { relation: string; target_id: string }[]; facets: { areas?: string[] }; attributes: Record<string, unknown> };

/** What the release's snapshot validation says about the batch. `storedSources` are the stored
 * source records the batch cites but does not add, in source_ids or anywhere else in a record
 * (an existing record's profile cites sources of its own). */
export function releaseProblems(records: Rec[], storedSources: Rec[] = [], storedTargets: Map<string, { kind: string }> = new Map()): string[] {
  // A link to a record already in the store is checked here, against that record's kind, and left
  // out of the snapshot below: the stored record would bring its own links and sources with it.
  // records -- add checks the whole store again.
  const own = new Set(records.map((r) => r.id));
  const problems: string[] = [];
  records = records.map((record) => {
    const stored = record.links.filter((l) => !own.has(l.target_id));
    for (const link of stored) {
      const target = storedTargets.get(link.target_id);
      if (!target) problems.push(`${record.id}: link ${link.relation} to ${link.target_id}, which is neither in the batch nor in the store`);
      else if (!relationAllows(link.relation, record.kind, target.kind))
        problems.push(`${record.id}: relation ${link.relation} cannot link a ${record.kind} to a ${target.kind} (${link.target_id})`);
    }
    return stored.length ? { ...record, links: record.links.filter((l) => own.has(l.target_id)) } : record;
  });
  if (problems.length) return problems;
  const text = records.map((r) => JSON.stringify(r)).join("\n");
  const cited = new Set([
    ...records.flatMap((r) => (r as unknown as { source_ids: string[] }).source_ids ?? []),
    ...storedSources.filter((s) => text.includes(`"${s.id}"`)).map((s) => s.id),
  ]);
  const visible = [...records, ...storedSources.filter((s) => cited.has(s.id) && !own.has(s.id))];
  try {
    validateSnapshot({ schema_version: "1.1", release_id: "2026-01-01-000000000000", released_at: "2026-01-01T00:00:00Z", records: visible, coverage: {} });
    return [];
  } catch (error) {
    if (error instanceof ZodError)
      return [...new Set(error.issues.map((i) => `${visible[Number(i.path[1])]?.id ?? i.path.join(".")}: release validation: ${i.message}`))];
    return [`release validation: ${(error as Error).message}`];
  }
}

export function intakeProblems(records: Rec[], storedSources: Rec[] = [], storedTargets: Map<string, { kind: string }> = new Map()): string[] {
  const problems: string[] = [...releaseProblems(records, storedSources, storedTargets)];
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
  const files = process.argv.slice(2);
  if (!files.length) {
    console.error("Usage: npx tsx scripts/agents/intake-check.ts <batch.jsonl>...");
    process.exit(1);
  }
  // A changes file (records change --changes) holds {id, base_sha256, sha256, record} lines; check the records.
  const unwrap = (value: Rec & { record?: Rec; base_sha256?: string }) => (value.record && value.base_sha256 ? value.record : value);
  const records = files.flatMap((file) => fs.readFileSync(file, "utf8").split("\n").filter(Boolean).map((line) => unwrap(JSON.parse(line)) as Rec));
  const sourcesFile = "data/entities/sources.jsonl";
  const stored = fs.existsSync(sourcesFile)
    ? fs.readFileSync(sourcesFile, "utf8").split("\n").filter(Boolean).map((line) => JSON.parse(line) as Rec)
    : [];
  // The kind of every stored entity, for links from the batch to records already in the store.
  const targets = new Map<string, { kind: string }>();
  for (const file of fs.existsSync("data/entities") ? fs.readdirSync("data/entities").filter((f) => f.endsWith(".jsonl")) : [])
    for (const line of fs.readFileSync(`data/entities/${file}`, "utf8").split("\n"))
      if (line) {
        const { id, kind } = JSON.parse(line) as Rec;
        targets.set(id, { kind });
      }
  const problems = intakeProblems(records, stored, targets);
  for (const p of problems) console.error(p);
  console.log(problems.length ? `${problems.length} problems in ${records.length} records.` : `${records.length} records pass the intake checks.`);
  process.exit(problems.length ? 1 : 0);
}
