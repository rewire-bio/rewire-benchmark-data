/** Move use cases into the record store (issue #42, use-case stage).
 *
 * Converts data/omics/use-cases/inputs.json into one use_case record per use case and one
 * relevance judgement claim per mapping, with the use case linking `assessed_by` each mapped
 * protocol. Judgements record the pins (shared/omics/use-cases.ts judgementPins) of the store as
 * it is now, so a later change to a pinned field withholds them until they are reviewed again.
 * Writes a batch for `npm run records -- add`; changes nothing else.
 *
 * Usage: npm run use-cases:migrate -- <batch-dir> */
import fs from "node:fs";
import path from "node:path";
import { judgementField, judgementPins, parseUseCaseInputs, type Mapping, type Review, type UseCase } from "../../shared/omics/use-cases";
import type { CatalogueRecord } from "../../shared/omics/catalogue-query";
import { loadRecords } from "./records";

const migratedAt = "2026-10-09";

/** The record review shape for a use-case or mapping review. The free-text actor is kept
 * verbatim as reviewer_note, so deriveUseCaseInputs gives back the original review. */
export function recordReview(review: Review) {
  const reviewer = [
    ...(/codex/i.test(review.actor) ? ["codex"] : []),
    ...(/claude sonnet/i.test(review.actor) ? ["claude-sonnet"] : /claude/i.test(review.actor) ? ["claude"] : []),
  ];
  return {
    method: [review.method === "human_domain_review" ? "human-domain-review" : "automated-source-review"],
    reviewer: reviewer.length ? reviewer : ["unidentified-automated-reviewer"],
    reviewer_note: review.actor,
    reviewed_at: review.reviewed_at,
    note: review.note,
  };
}

const nonEmpty = <T extends Record<string, unknown>>(value: T) =>
  Object.fromEntries(Object.entries(value).filter(([, v]) => v !== undefined && !(Array.isArray(v) && v.length === 0)));

export function useCaseRecord(u: UseCase, mappings: Mapping[]) {
  const protocols = [...new Set(mappings.filter((m) => m.protocol_id && !["withdrawn", "superseded"].includes(m.lifecycle)).map((m) => m.protocol_id!))].sort();
  return {
    id: u.id, kind: "use_case", name: u.title, description: u.question, status: "source_checked",
    facets: { areas: [u.area], contexts: u.contexts },
    source_ids: [...new Set(u.citations.map((c) => c.source_id))],
    links: protocols.map((target_id) => ({ relation: "assessed_by", target_id })),
    attributes: nonEmpty({
      slug: u.slug, question: u.question, intended_users: u.intended_users, decision: u.decision,
      inputs: u.inputs, output: u.output, setting: u.setting, exclusions: u.exclusions,
      clinical_scope: u.clinical_scope, evidence_gaps: u.evidence_gaps, search_terms: u.search_terms,
      citation_locators: u.citations, collection_plan: u.collection_plan, planned_work: u.planned_work,
      review: recordReview(u.review),
    }),
  };
}

export function judgementClaim(m: Mapping, title: string, records: Map<string, CatalogueRecord>, evaluationsOnProtocol: string[]) {
  const protocol = m.protocol_id!;
  const excluded = evaluationsOnProtocol.filter((id) => !m.evaluation_ids.includes(id)).sort();
  const status = m.lifecycle === "active" || m.lifecycle === "needs_review" ? "source_checked" : "needs_review";
  return {
    id: m.id, kind: "claim",
    name: `Relevance of ${records.get(protocol)?.name ?? protocol} to "${title}"`,
    description: m.rationale ?? "",
    status, facets: {},
    source_ids: [...new Set(m.citations.map((c) => c.source_id))],
    links: [{ relation: "subject", target_id: m.use_case_id }],
    attributes: nonEmpty({
      field: judgementField(protocol), value: protocol, relevance: m.relevance, endpoint: m.endpoint,
      rationale: m.rationale, constraints: m.constraints, limitations: m.limitations,
      revision: m.revision, reason: m.reason, task_id: m.task_id,
      citation_locators: m.citations,
      source_locator: m.citations.map((c) => `${c.source_id}: ${c.locator}`).join("; "),
      excluded_evaluations: m.relevance === "direct" || m.relevance === "proxy"
        ? excluded.map((id) => ({ id, reason: `Not in the reviewed mapping's evaluation list when use cases moved into the store (${migratedAt}).` }))
        : undefined,
      review: m.review ? recordReview(m.review) : undefined,
      // The evaluations this judgement was reviewed with; one dropping out withholds it.
      reviewed_evaluations: [...m.evaluation_ids].sort(),
      pins: status === "source_checked"
        ? judgementPins(records, { useCaseId: m.use_case_id, protocolId: protocol, sourceIds: [...new Set(m.citations.map((c) => c.source_id))], evaluationIds: m.evaluation_ids })
        : undefined,
    }),
  };
}

if (process.argv[1]?.endsWith("migrate-use-cases.ts")) {
  const dir = process.argv[2];
  if (!dir) {
    console.error("Usage: npm run use-cases:migrate -- <batch-dir>");
    process.exit(1);
  }
  const inputs = parseUseCaseInputs(JSON.parse(fs.readFileSync("data/omics/use-cases/inputs.json", "utf8")));
  const store = loadRecords() as unknown as CatalogueRecord[];
  const byId = new Map(store.map((r) => [r.id, r]));
  const useCaseRecords = inputs.use_cases.map((u) => useCaseRecord(u, inputs.mappings.filter((m) => m.use_case_id === u.id)));
  // Pins cover the use case itself, so they are computed with the new use_case records in view.
  for (const r of useCaseRecords) byId.set(r.id, r as unknown as CatalogueRecord);
  const onProtocol = new Map<string, string[]>();
  for (const r of store) if (r.kind === "evaluation")
    for (const l of r.links) if (l.relation === "assessment") onProtocol.set(l.target_id, [...(onProtocol.get(l.target_id) || []), r.id]);
  const titles = new Map(inputs.use_cases.map((u) => [u.id, u.title]));
  // Optional page grouping per judgement and draft summaries per use case (presentation.json).
  const presentationFile = path.join(dir, "presentation.json");
  const presentation = fs.existsSync(presentationFile)
    ? JSON.parse(fs.readFileSync(presentationFile, "utf8")) as {
        judgements?: Record<string, Record<string, unknown>>;
        summaries?: Record<string, { id: string; text: string; source_ids: string[]; source_locator: string }>;
      }
    : {};
  const claims = inputs.mappings
    .filter((m) => !["withdrawn", "superseded"].includes(m.lifecycle))
    .map((m) => judgementClaim(m, titles.get(m.use_case_id)!, byId, onProtocol.get(m.protocol_id!) || []))
    .map((c) => ({ ...c, attributes: { ...c.attributes, ...(presentation.judgements?.[c.id] || {}) } }));
  const summaries = Object.entries(presentation.summaries || {}).map(([useCaseId, s]) => ({
    id: s.id, kind: "claim", name: `Evidence summary: ${titles.get(useCaseId) ?? useCaseId}`,
    description: "Plain-language summary of what the reviewed evidence shows. Draft until reviewed.",
    status: "needs_review", facets: {}, source_ids: s.source_ids,
    links: [{ relation: "subject", target_id: useCaseId }],
    attributes: { field: "summary", value: s.text, source_locator: s.source_locator },
  }));
  const batch = [...useCaseRecords, ...claims, ...summaries].sort((a, b) => a.id.localeCompare(b.id));
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, "batch.jsonl"), batch.map((r) => JSON.stringify(r) + "\n").join(""));
  console.log(`Wrote ${useCaseRecords.length} use cases and ${claims.length} relevance judgements to ${dir}/batch.jsonl`);
}
