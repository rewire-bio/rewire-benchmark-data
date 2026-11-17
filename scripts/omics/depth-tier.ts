/** Derive and check the depth tier of models, methods, benchmarks and use cases (#260).
 *
 *   npm run depth-tier -- check        list records whose stored tier is missing or differs from the rule
 *   npm run depth-tier -- backfill <ids> write the derived tier into each record that lacks it or differs,
 *                                      and the changed IDs to <ids>, one per line, for records -- change
 *
 * The rule is in shared/omics/depth-tier.ts and docs/tiers.md. A record whose areas
 * are empty gets the tier in `noAreaTiers`, set by hand from its name and source and recorded in
 * the dated review; any other record without areas is reported and left alone. */
import fs from "node:fs";
import { readKind, writeKind } from "./records";
import { deriveTier, tierKinds, type Tier } from "../../shared/omics/depth-tier";
import type { RecordEntry } from "./schema";

/** Tiers set by hand for records with no areas (docs/reviews/2026-11-17-depth-tier-backfill.md). */
export const noAreaTiers: Record<string, Tier> = {
  "ucc-research-model-helixfold3": 2,
  "ucc-research-model-protenix": 2,
  "acquired-configuration-c7901cd0e9a2eb889951": 3,
  "ucc-research-method-abdelaal-scmapcell": 3,
  "ucc-research-method-abdelaal-scpred": 3,
  "ucc-research-method-abdelaal-svm-linear": 3,
  "ucc-research-method-ciform": 3,
  "ucc-research-method-linear": 3,
  "ucc-research-method-mlp": 3,
  "ucc-research-method-mprabc-abc": 3,
  "ucc-research-method-mprabc-full": 3,
  "ucc-research-method-mprabc-megamap": 3,
  "ucc-research-method-mprabc-mpralegnet": 3,
  "ucc-research-method-mprabc-re2g": 3,
  "ucc-research-method-mprabc-sei": 3,
  "ucc-research-method-sctab": 3,
  "ucc-research-method-uce": 3,
  "ucc-research-method-xgboost": 3,
};

type Rec = RecordEntry & { attributes: Record<string, unknown> };

/** For each benchmark, the tiers of the use cases that judge it, one of its protocols or tasks,
 * or anything part of it, relevant. Relevance judgements are claims whose field is
 * `links:assessed_by:<id>` and whose subject is the use case; excluded judgements do not count. */
export function linkedUseCaseTiers(records: { useCases: Rec[]; claims: Rec[]; parents: Rec[]; benchmarks: Rec[] }): Map<string, Tier[]> {
  const useCaseTier = new Map(records.useCases.map((u) => [u.id, deriveTier(u)]));
  const up = new Map<string, string[]>();
  for (const r of [...records.parents, ...records.benchmarks])
    up.set(r.id, r.links.filter((l) => l.relation === "part_of" || l.relation === "parent").map((l) => l.target_id));
  const benchmarkIds = new Set(records.benchmarks.map((b) => b.id));
  const out = new Map<string, Tier[]>();
  for (const claim of records.claims) {
    const field = String(claim.attributes.field ?? "");
    if (!field.startsWith("links:assessed_by:") || claim.status === "excluded") continue;
    const subject = claim.links.find((l) => l.relation === "subject")?.target_id;
    const tier = subject ? useCaseTier.get(subject) : undefined;
    if (!tier) continue;
    const seen = new Set<string>();
    const stack = [field.slice("links:assessed_by:".length)];
    while (stack.length) {
      const id = stack.pop()!;
      if (seen.has(id)) continue;
      seen.add(id);
      if (benchmarkIds.has(id)) out.set(id, [...(out.get(id) ?? []), tier]);
      stack.push(...(up.get(id) ?? []));
    }
  }
  return out;
}

export function derivedTiers(root = "."): { kind: string; record: Rec; tier: Tier | undefined }[] {
  const load = (kind: string) => readKind<Rec>(kind, root);
  const byKind = Object.fromEntries(tierKinds.map((k) => [k, load(k)])) as Record<(typeof tierKinds)[number], Rec[]>;
  const linked = linkedUseCaseTiers({
    useCases: byKind.use_case,
    benchmarks: byKind.benchmark,
    parents: [...load("protocol"), ...load("task")],
    claims: load("claim"),
  });
  return tierKinds.flatMap((kind) =>
    byKind[kind].map((record) => ({ kind, record, tier: deriveTier(record, linked.get(record.id) ?? [], noAreaTiers[record.id]) })));
}

if (process.argv[1]?.endsWith("depth-tier.ts")) {
  const [command, idsFile] = process.argv.slice(2);
  const rows = derivedTiers();
  const unplaced = rows.filter((r) => r.tier === undefined);
  const differ = rows.filter((r) => r.tier !== undefined && r.record.attributes.depth_tier !== r.tier);
  if (command === "check") {
    for (const r of differ) console.log(`${r.record.id}\tstored ${r.record.attributes.depth_tier ?? "none"}\trule ${r.tier}`);
    for (const r of unplaced) console.log(`${r.record.id}\tno areas; set its depth tier by hand in scripts/omics/depth-tier.ts`);
    const counts = rows.reduce((m, r) => m.set(`${r.kind} ${r.tier ?? "none"}`, (m.get(`${r.kind} ${r.tier ?? "none"}`) ?? 0) + 1), new Map<string, number>());
    console.log([...counts].sort().map(([k, n]) => `${k}: ${n}`).join("\n"));
    console.log(`${differ.length} records differ from the rule; ${unplaced.length} cannot be placed.`);
  } else if (command === "backfill" && idsFile) {
    const changed = new Set(differ.map((r) => r.record.id));
    for (const kind of tierKinds) {
      const records = rows.filter((r) => r.kind === kind).map(({ record, tier }) =>
        changed.has(record.id) ? { ...record, attributes: { ...record.attributes, depth_tier: tier } } : record);
      if (records.some((r) => changed.has(r.id))) writeKind(kind, records);
    }
    fs.writeFileSync(idsFile, [...changed].sort().join("\n") + (changed.size ? "\n" : ""));
    console.log(`Set the depth tier on ${changed.size} records; ${unplaced.length} cannot be placed. IDs in ${idsFile}.`);
  } else {
    console.error("Usage: npm run depth-tier -- check | backfill <ids-file>");
    process.exit(1);
  }
}
