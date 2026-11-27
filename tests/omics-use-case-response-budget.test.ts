import { describe, expect, it } from "vitest";
import type { CatalogueRecord, CatalogueSnapshot } from "../shared/omics/catalogue-query";
import {
  buildUseCaseArtifact, createUseCaseQuery, mappingEvidenceHash, useCaseDeclaration,
  MAX_USE_CASE_RESPONSE_BYTES, type Mapping, type UseCase, type UseCaseInputs,
} from "../shared/omics/use-cases";

const review = { method: "automated_source_review" as const, actor: "Automated test fixture", reviewed_at: "2026-09-25T12:00:00Z", note: "Synthetic fixture, not scientific review" };

// Many mappings, each sent whole on every page with a padded rationale, so the fixed metadata
// alone is large; every mapping has a few evaluations with padded records.
function manyMappingsFixture(options: { mappingCount: number; rationaleBytes: number; evaluationsPerMapping: number; padDescription: number }) {
  const { mappingCount, rationaleBytes, evaluationsPerMapping, padDescription } = options;
  const pad = "x".repeat(padDescription);
  const record = (id: string, kind: CatalogueRecord["kind"], extra: Partial<CatalogueRecord> = {}): CatalogueRecord => ({
    id, kind, name: id, description: pad, status: "source_checked", facets: { areas: ["genomics"] },
    source_ids: kind === "source" ? [] : ["source"], links: [], attributes: {}, ...extra,
  });
  const claim = (id: string, subject: string, relation: string, target: string) => record(id, "claim", {
    links: [{ relation: "subject", target_id: subject }], attributes: { field: `links:${relation}:${target}`, value: target, source_locator: "Synthetic relationship" },
  });
  const records: CatalogueRecord[] = [
    record("source", "source", { attributes: { url: "https://example.org/fixture", sha256: "a".repeat(64) } }),
    record("suite", "benchmark"), record("task", "task", { status: "discovered" }),
  ];
  const entry: UseCase = {
    id: "wide-case", slug: "wide", title: "Wide use case", question: "Does this scale?", area: "genomics",
    contexts: ["research"], search_terms: ["scale"], intended_users: ["Researcher"], decision: "Choose a method", inputs: ["Inputs"],
    output: "Output", setting: "Setting", exclusions: [], clinical_scope: "Research only", evidence_gaps: [],
    citations: [{ source_id: "source", locator: "Scope" }], review, planned_work: [],
  };
  const mappings: Mapping[] = [];
  const evaluationIds: string[] = [];
  for (let m = 0; m < mappingCount; m++) {
    const protocol = `protocol-${m}`;
    records.push(record(protocol, "protocol", { links: [{ relation: "evaluates_task", target_id: "task" }, { relation: "part_of", target_id: "suite" }] }));
    records.push(claim(`task-link-${m}`, protocol, "evaluates_task", "task"), claim(`suite-link-${m}`, protocol, "part_of", "suite"));
    const ids: string[] = [];
    for (let e = 0; e < evaluationsPerMapping; e++) {
      const id = `evaluation-${m}-${e}`;
      ids.push(id);
      records.push(record(`config-${m}-${e}`, "configuration"));
      records.push(record(id, "evaluation", { links: [{ relation: "configuration", target_id: `config-${m}-${e}` }, { relation: "protocol", target_id: protocol }], attributes: { origin: "rewire_run" } }));
      records.push(record(`result-${m}-${e}`, "result", { links: [{ relation: "evaluation", target_id: id }], attributes: { metric: "Spearman", numeric_value: "0.5", uncertainty: null, source_locator: "/metric" } }));
    }
    evaluationIds.push(...ids);
    mappings.push({
      id: `mapping-${m}`, use_case_id: entry.id, lifecycle: "active", revision: 1, reason: "Source review",
      protocol_id: protocol, task_id: "task", evaluation_ids: ids, endpoint: "Scaled endpoint", relevance: "proxy",
      rationale: "r".repeat(rationaleBytes), constraints: [], limitations: [], citations: [{ source_id: "source", locator: "/metric" }], review,
    });
  }
  const snapshot: CatalogueSnapshot = { schema_version: "1.1", release_id: "2026-09-25-333333333333", released_at: "2026-09-25T12:00:00Z", coverage: {}, records };
  for (const mapping of mappings) mapping.evidence_sha256 = mappingEvidenceHash(snapshot, entry, mapping);
  const inputs: UseCaseInputs = { schema_version: "1.0", use_cases: [entry], mappings };
  const query = createUseCaseQuery(snapshot, buildUseCaseArtifact(snapshot, inputs), useCaseDeclaration(inputs));
  return { query, evaluationIds };
}

const wrapped = (value: unknown) => Buffer.byteLength(JSON.stringify({ result: { data: value } }));

describe("use-case detail with large fixed metadata", () => {
  it("keeps every page under the response budget when mappings alone exceed 500 KB", () => {
    const { query, evaluationIds } = manyMappingsFixture({ mappingCount: 120, rationaleBytes: 2_500, evaluationsPerMapping: 4, padDescription: 1_000 });
    const first = query.get({ slug: "wide", limit: 100 })!;
    const fixed = wrapped({ ...first, mappings: first.mappings.map((m) => ({ ...m, evaluations: [] })), evaluations_next_cursor: null });
    expect(fixed).toBeGreaterThan(500_000);
    for (const limit of [20, 100]) {
      const seen: string[] = [];
      let cursor: string | undefined;
      do {
        const page = query.get({ slug: "wide", limit, cursor })!;
        expect(wrapped(page)).toBeLessThanOrEqual(MAX_USE_CASE_RESPONSE_BYTES - 40_000);
        seen.push(...page.mappings.flatMap((m) => m.evaluations.map((e) => e.evaluation.id)));
        cursor = page.evaluations_next_cursor || undefined;
      } while (cursor);
      expect(seen.sort()).toEqual([...evaluationIds].sort());
    }
  });
  it("fails loudly, naming the use case, when the fixed metadata alone leaves no room", () => {
    const { query } = manyMappingsFixture({ mappingCount: 120, rationaleBytes: 8_000, evaluationsPerMapping: 1, padDescription: 100 });
    expect(() => query.get({ slug: "wide" })).toThrow(/metadata for wide is \d+ bytes before any evaluation/);
  });
});
