import { describe, expect, it } from "vitest";
import { profileSchema } from "../lib/omics-profile";
import { buildRelease } from "../scripts/omics/release";
import { loadRecords } from "../scripts/omics/records";
import { publicRecords, validateRecords, type RecordEntry } from "../scripts/omics/schema";
import { createCatalogueQuery } from "../shared/omics/catalogue-query";

const records = loadRecords();
const profiles = records
  .filter((record) => record.attributes.profile)
  .map((record) => ({ id: record.id, profile: record.attributes.profile }));
const published = buildRelease(records, "2026-09-16T10:50:02Z", {
  entity_schema_version: "1.1",
}).snapshot;
const query = createCatalogueQuery(published);
const sourceId = "barcodebert-2026";
const barcodeId = "reported-model-05103f72325fe5";
const benchmarkId = "reported-task-4a54ce01b5a855";
const review = {
  method: "automated_source_review",
  date: "2026-09-16",
  note: "Synthetic relationship fixture; not a scientific claim.",
};
// Each record's full result list and reverse links are paged once and reused: the
// reachability test asks for the same models and evaluations thousands of times.
const resultIdCache = new Map<string, string[]>();
function resultIds(id: string) {
  const cached = resultIdCache.get(id);
  if (cached) return cached;
  const ids: string[] = [];
  let cursor: string | undefined;
  do {
    const page = query.results({ id, limit: 100, cursor });
    ids.push(...page.items.map((row) => row.result.id));
    cursor = page.next_cursor || undefined;
  } while (cursor);
  resultIdCache.set(id, ids);
  return ids;
}
const reverseCache = new Map<string, Set<string>>();
function reverseIds(id: string) {
  let ids = reverseCache.get(id);
  if (!ids) reverseCache.set(id, (ids = new Set(query.get({ id })!.reverse.map((item) => item.record.id))));
  return ids;
}

describe("source-backed profile publication", () => {
  it("keeps cited, pinned evidence on every profiled model and benchmark", () => {
    const targets = records.filter((record) => record.attributes.profile);
    expect(targets.length).toBeGreaterThanOrEqual(396);
    expect(publicRecords(targets)).toHaveLength(targets.length);
    for (const original of targets) {
      const current = query.get({ id: original.id })!.record;
      const profile = profileSchema.parse(current.attributes.profile);
      if (profile.coverage === "limited")
        expect(profile.gaps.length).toBeGreaterThan(0);
      if (profile.coverage === "reviewed")
        expect(profile.sections.length).toBeGreaterThan(0);
      expect(profile.review.method).toBe("automated_source_review");
      expect(profile.summary_source_ids?.length).toBeGreaterThan(0);
      expect(profile.summary_source_locator?.trim()).toBeTruthy();
      for (const fact of profile.facts) expect(fact.status).toBeTruthy();
      const claims = [
        profile,
        ...profile.facts,
        ...profile.sections,
        ...profile.strengths,
        ...profile.limitations,
        ...(profile.diagram ? [profile.diagram] : []),
      ];
      for (const claim of claims) {
        const ids =
          "source_ids" in claim ? claim.source_ids : claim.summary_source_ids!;
        for (const id of ids)
          expect(query.get({ id })!.record.attributes.artifact_sha256).toMatch(
            /^[a-f0-9]{64}$/,
          );
      }
    }
  });

  it("rejects stored profiles with missing or non-source evidence and empty locators", () => {
    const withProfile = (change: (profile: ReturnType<typeof profileSchema.parse>) => void) => {
      const copy = records.map((record) => record.id === barcodeId ? structuredClone(record) : record);
      const target = copy.find((record) => record.id === barcodeId)!;
      const profile = profileSchema.parse(target.attributes.profile);
      change(profile);
      target.attributes.profile = profile;
      return copy;
    };
    expect(() => validateRecords(withProfile((p) => { p.sections[0].source_ids = ["missing-source"]; }))).toThrow("missing source");
    expect(() => validateRecords(withProfile((p) => { p.sections[0].source_ids = [barcodeId]; }))).toThrow("missing source");
    expect(() => validateRecords(withProfile((p) => {
      p.sections[0].source_ids = [sourceId];
      p.sections[0].source_locator = " ";
    }))).toThrow();
  });

  it("requires explicit gaps for limited profiles and cited explanation for reviewed coverage", () => {
    const limited = profileSchema.parse(
      profiles.find(
        (item) => profileSchema.parse(item.profile).coverage === "limited",
      )!.profile,
    );
    expect(() => profileSchema.parse({ ...limited, gaps: [] })).toThrow(
      "evidence gaps",
    );
    const reviewed = profileSchema.parse(
      profiles.find(
        (item) => profileSchema.parse(item.profile).coverage === "reviewed",
      )!.profile,
    );
    expect(() => profileSchema.parse({ ...reviewed, sections: [] })).toThrow(
      "sourced explanation",
    );
  });

  it("makes every result reachable through its exact model, benchmark and evaluation", () => {
    for (const result of published.records.filter(
      (record) => record.kind === "result",
    )) {
      const detail = query.get({ id: result.id })!;
      const evaluation = detail.direct.find(
        (item) => item.relation === "evaluation",
      )!.record;
      expect(reverseIds(evaluation.id).has(result.id)).toBe(true);
      const row = query.results({ id: result.id }).items[0];
      expect(row.result.id).toBe(result.id);
      expect(row.evaluation?.id).toBe(evaluation.id);
      expect(row.models.length).toBeGreaterThan(0);
      expect(row.benchmarks.length).toBeGreaterThan(0);
      expect(row.sources.length).toBeGreaterThan(0);
      expect(row.review_status).toBe(result.status);
      for (const linked of [...row.models, ...row.benchmarks]) {
        expect(new Set(resultIds(linked.id)).has(result.id)).toBe(true);
        expect(reverseIds(linked.id).has(evaluation.id)).toBe(true);
      }
    }
  });

  it("rolls up verified family members but never a pipeline merely using the family", () => {
    function fixtureRecord(
      id: string,
      kind: RecordEntry["kind"],
      links: RecordEntry["links"] = [],
      attributes: RecordEntry["attributes"] = {},
    ): RecordEntry {
      return {
        id,
        kind,
        name: id,
        description: "Synthetic test fixture",
        status: "source_checked",
        facets: {},
        source_ids: kind === "source" ? [] : ["test-source"],
        links,
        attributes,
      };
    }
    // A model relationship counts only when a source-checked claim backs it.
    const claim = (subject: string, relation: string, target: string) =>
      fixtureRecord(`test-claim-${subject}`, "claim", [{ relation: "subject", target_id: subject }], {
        field: `links:${relation}:${target}`,
        target_id: target,
        source_locator: "Synthetic locator",
        review,
      });
    const linked = [
      fixtureRecord("test-source", "source"),
      fixtureRecord("test-family", "model"),
      fixtureRecord("test-variant", "model", [{ relation: "variant_of", target_id: "test-family" }]),
      fixtureRecord("test-pipeline", "model", [{ relation: "uses_model", target_id: "test-family" }]),
      claim("test-variant", "variant_of", "test-family"),
      claim("test-pipeline", "uses_model", "test-family"),
      ...["variant", "pipeline"].flatMap((kind) => [
        fixtureRecord(`test-evaluation-${kind}`, "evaluation", [
          { relation: "model", target_id: `test-${kind}` },
        ]),
        fixtureRecord(`test-result-${kind}`, "result", [
          { relation: "evaluation", target_id: `test-evaluation-${kind}` },
        ]),
      ]),
    ];
    const snapshot = { ...published, records: linked };
    expect(
      createCatalogueQuery(snapshot)
        .results({ id: "test-family" })
        .items.map((row) => row.result.id),
    ).toEqual(["test-result-variant"]);
    const unverified = {
      ...snapshot,
      records: linked.filter((record) => record.kind !== "claim"),
    };
    expect(
      createCatalogueQuery(unverified).results({ id: "test-family" }).items,
    ).toEqual([]);
    expect(
      createCatalogueQuery(unverified).results({ id: "test-variant" }).items,
    ).toHaveLength(1);
  });

  it("exposes BarcodeBERT's 78.5 percent genus result on both exact detail pages", () => {
    const row = query.results({ id: "b2-barcodebert-2026" }).items[0];
    expect(row.result.attributes.printed_value).toBe("78.5");
    expect(row.result.attributes.unit).toBe("percent");
    expect(row.models.map((record) => record.id)).toEqual([barcodeId]);
    expect(row.benchmarks.map((record) => record.id)).toEqual([benchmarkId]);
    expect(String(row.evaluation!.attributes.protocol)).toContain(
      "genus-level nearest-neighbor",
    );
    expect(resultIds(barcodeId)).toContain(row.result.id);
    expect(resultIds(benchmarkId)).toContain(row.result.id);
    expect(
      profileSchema.parse(
        query.get({ id: barcodeId })!.record.attributes.profile,
      ).summary,
    ).toContain("four-layer");
  });

  it("keeps the frozen DNABERT logistic pipeline separate from base-model performance", () => {
    const pipeline = "rewire-model-dnabert2-117m-frozen-pair-logreg";
    const family = "discovery-model-dnabert-2";
    const pipelineResults = resultIds(pipeline);
    expect(pipelineResults).toHaveLength(3);
    expect(query.get({ id: pipeline })!.direct).toContainEqual(
      expect.objectContaining({
        relation: "uses_model",
        record: expect.objectContaining({ id: family }),
      }),
    );
    expect(
      resultIds(family).filter((id) => pipelineResults.includes(id)),
    ).toEqual([]);
    expect(query.get({ id: pipeline })!.record.attributes.entity_level).toBe(
      "method",
    );
    expect(query.get({ id: family })!.record.attributes.entity_level).toBe(
      "family",
    );
    expect(
      profileSchema.parse(
        query.get({ id: pipeline })!.record.attributes.profile,
      ).summary,
    ).toContain("logistic-regression");
  });

});
