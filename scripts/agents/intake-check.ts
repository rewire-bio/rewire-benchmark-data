/** Checks the intake agent runs on its batch before records -- add (#255). Exits 1 and lists the
 * problems when a record would fail a check that records -- add does not make:
 *   - normalizeAttributes would rewrite it (check C13 in scripts/omics/checks, and the case
 *     tests/attributes.test.ts fails CI on), for example a review carrying `date` beside `reviewed_at`;
 *   - its depth tier differs from the rule in docs/tiers.md;
 *   - it is an evaluation, result or claim (intake adds entities only until #274);
 *   - the release would refuse it (validateSnapshot, the check tests/release-validation.test.ts
 *     runs on the whole store), for example a model without entity_level.
 * And, per record, the checks records -- add makes only on the whole batch, stopping at the first
 * problem, and the ones rdf-kg-mcp's draft overlay made that nothing else does (recordChecks):
 *   - a controlled value that is not a concept of its vocabulary (validateVocabularies);
 *   - an ID already in the store, or twice in the batch;
 *   - a source_ids entry listed twice, that is not a source record (a stored record not in
 *     data/entities is evidence, so not a source), or that is neither in the batch nor in the store;
 *   - a link listed twice (same relation and target), a link to the record itself, or a link to
 *     another record of the batch that the relation rules do not allow (releaseProblems checks
 *     links to stored records);
 *   - a number JSON cannot carry exactly (an integer beyond 2^53, or one too large to be finite)
 *     and text with a lone surrogate.
 * Usage: npx tsx scripts/agents/intake-check.ts [--json] <batch.jsonl>... (an update checks its changed
 * record and its new sources together; the record of a changes line is expected in the store).
 * --json prints {records: {<id>: [problems]}, batch: [problems]} instead, so that a record with
 * problems can be dropped and the rest kept; `batch` holds problems no record of the batch is named in. */
import fs from "node:fs";
import { attributeIssues, normalizeAttributes } from "../../shared/omics/attributes";
import { deriveTier, tierKinds } from "../../shared/omics/depth-tier";
import { relationAllows } from "../../shared/omics/relations";
import { validateSnapshot } from "../../shared/omics/validation";
import { controlledValues, loadSchemes, type Scheme } from "../omics/vocab";
import { ZodError } from "zod";

type Rec = { id: string; kind: string; links: { relation: string; target_id: string }[]; facets: { areas?: string[] }; attributes: Record<string, unknown> };

/** What the per-record checks know of the store. Without `ids` the store is unknown, so an ID
 * already in it and a source in neither the batch nor the store are not reported. `changed` are
 * the IDs of records from a changes file, which must already be in the store. */
export type StoreFacts = { ids?: Set<string>; changed?: Set<string> };

let vocabularies: { mapping: Parameters<typeof controlledValues>[0]; schemes: Map<string, Scheme> } | undefined;
const vocab = () =>
  (vocabularies ??= { mapping: JSON.parse(fs.readFileSync("data/ontology/mapping.json", "utf8")), schemes: loadSchemes() });

const LONE_SURROGATE = /[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/;

/** Numbers and text that do not survive a round trip through JSON, by path. An integer is unsafe
 * when JSON.stringify, which writes the store, would write it as digits beyond 2^53: from 1e21 up
 * it writes an exponent, which other readers take as a floating-point number. */
export function valueProblems(value: unknown, path = ""): string[] {
  const where = path || "(record)";
  if (typeof value === "number") {
    if (!Number.isFinite(value)) return [`${where}: ${value} is not a finite number`];
    if (Number.isInteger(value) && !Number.isSafeInteger(value) && Math.abs(value) < 1e21)
      return [`${where}: integer ${value} is outside the range JSON numbers carry exactly (2^53)`];
    return [];
  }
  if (typeof value === "string") return LONE_SURROGATE.test(value) ? [`${where}: text holds a lone surrogate`] : [];
  if (Array.isArray(value)) return value.flatMap((item, i) => valueProblems(item, `${path}[${i}]`));
  if (value && typeof value === "object")
    return Object.entries(value).flatMap(([key, item]) => {
      const at = path ? `${path}/${key}` : key;
      return [...valueProblems(key, at), ...valueProblems(item, at)];
    });
  return [];
}

/** The per-record checks, each problem prefixed with the record's ID. `storedTargets` gives the
 * kind of stored records, for sources the batch cites but does not add. */
export function recordChecks(records: Rec[], storedTargets: Map<string, { kind: string }> = new Map(), store: StoreFacts = {}): string[] {
  const problems: string[] = [];
  const { mapping, schemes } = vocab();
  const kindOf = new Map<string, string>([...storedTargets].map(([id, t]) => [id, t.kind]));
  const count = new Map<string, number>();
  for (const record of records) {
    kindOf.set(record.id, record.kind);
    count.set(record.id, (count.get(record.id) ?? 0) + 1);
  }
  for (const record of records) {
    const id = record.id;
    const changed = store.changed?.has(id) ?? false;
    if ((count.get(id) ?? 0) > 1) problems.push(`${id}: the batch holds this ID ${count.get(id)} times`);
    if (store.ids?.has(id) && !changed) problems.push(`${id}: already in the store; records add only adds new records`);
    if (store.ids && changed && !store.ids.has(id)) problems.push(`${id}: a change to a record the store does not hold`);
    const shaped = { ...record, facets: record.facets ?? {}, attributes: record.attributes ?? {} } as Parameters<typeof controlledValues>[1];
    for (const { field, scheme, value } of controlledValues(mapping, shaped)) {
      const concepts = schemes.get(scheme)?.concepts;
      if (!concepts) problems.push(`${id}: ${field} uses scheme "${scheme}", which has no data/vocab/${scheme}.ttl`);
      else if (typeof value !== "string" || !concepts.has(value))
        problems.push(`${id}: ${field} ${JSON.stringify(value)} is not a concept in the ${scheme} vocabulary`);
    }
    const listed = (record as unknown as { source_ids?: unknown }).source_ids;
    const sources: unknown[] = Array.isArray(listed) ? listed : [];
    sources.forEach((source, i) => {
      if (typeof source !== "string") return;
      if (sources.indexOf(source) !== i) problems.push(`${id}: source_ids[${i}] ${source} is listed twice`);
      else if (kindOf.has(source)) {
        if (kindOf.get(source) !== "source") problems.push(`${id}: source_ids[${i}] ${source} is a ${kindOf.get(source)}, not a source`);
      } else if (store.ids?.has(source)) problems.push(`${id}: source_ids[${i}] ${source} is a stored evidence record, not a source`);
      else if (store.ids) problems.push(`${id}: source_ids[${i}] ${source} is neither in the batch nor in the store`);
    });
    const seen = new Set<string>();
    (Array.isArray(record.links) ? record.links : []).forEach((link, i) => {
      if (!link || typeof link.relation !== "string" || typeof link.target_id !== "string") return;
      const key = JSON.stringify([link.relation, link.target_id]);
      if (seen.has(key)) problems.push(`${id}: links[${i}] ${link.relation} to ${link.target_id} is listed twice`);
      else if (link.target_id === id) problems.push(`${id}: links[${i}] ${link.relation} links the record to itself`);
      else if ((count.get(link.target_id) ?? 0) > 0) {
        const target = records.find((r) => r.id === link.target_id)!;
        if (!relationAllows(link.relation, record.kind, target.kind))
          problems.push(`${id}: links[${i}] relation ${link.relation} cannot link a ${record.kind} to a ${target.kind} (${link.target_id})`);
      }
      seen.add(key);
    });
    for (const p of valueProblems(record)) problems.push(`${id}: ${p}`);
  }
  return problems;
}

/** Problems by the batch record they name (the `${id}: ` prefix every per-record problem carries),
 * and the rest under `batch`: release validation messages that name no record of the batch, or
 * name a stored source the batch cites. Every batch record has an entry, empty when it passes. */
export function problemsByRecord(records: Rec[], problems: string[]): { records: Record<string, string[]>; batch: string[] } {
  const byRecord: Record<string, string[]> = Object.fromEntries(records.map((r) => [r.id, [] as string[]]));
  const batch: string[] = [];
  // The longest ID first, so an ID that starts another ID's problem text does not claim it.
  const ids = [...new Set(records.map((r) => r.id))].sort((a, b) => b.length - a.length);
  for (const problem of problems) {
    const id = ids.find((x) => problem.startsWith(`${x}: `));
    if (id === undefined) batch.push(problem);
    else byRecord[id].push(problem.slice(id.length + 2));
  }
  return { records: byRecord, batch };
}

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

export function intakeProblems(
  records: Rec[],
  storedSources: Rec[] = [],
  storedTargets: Map<string, { kind: string }> = new Map(),
  store: StoreFacts = {},
): string[] {
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
  return [...problems, ...recordChecks(records, storedTargets, store)];
}

/** Every record ID in the store: the provenance log lists each record once, evidence included. */
export function storedIds(root = "."): Set<string> {
  const dir = `${root}/data/provenance/records`;
  const ids = new Set<string>();
  if (!fs.existsSync(dir)) return ids;
  for (const file of fs.readdirSync(dir).filter((f) => f.endsWith(".jsonl")))
    for (const line of fs.readFileSync(`${dir}/${file}`, "utf8").split("\n"))
      if (line) ids.add((JSON.parse(line) as { id: string }).id);
  return ids;
}

if (process.argv[1]?.endsWith("intake-check.ts")) {
  const args = process.argv.slice(2);
  const json = args.includes("--json");
  const files = args.filter((a) => a !== "--json");
  if (!files.length) {
    console.error("Usage: npx tsx scripts/agents/intake-check.ts [--json] <batch.jsonl>...");
    process.exit(1);
  }
  // A changes file (records change --changes) holds {id, base_sha256, sha256, record} lines; check the records.
  const changed = new Set<string>();
  const unwrap = (value: Rec & { record?: Rec; base_sha256?: string }) => {
    if (!(value.record && value.base_sha256)) return value;
    changed.add(value.record.id);
    return value.record;
  };
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
  const problems = intakeProblems(records, stored, targets, { ids: storedIds(), changed });
  if (json) console.log(JSON.stringify(problemsByRecord(records, problems), null, 1));
  else for (const p of problems) console.error(p);
  const summary = problems.length ? `${problems.length} problems in ${records.length} records.` : `${records.length} records pass the intake checks.`;
  if (json) console.error(summary);
  else console.log(summary);
  process.exit(problems.length ? 1 : 0);
}
