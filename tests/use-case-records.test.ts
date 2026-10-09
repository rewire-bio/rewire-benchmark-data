import fs from "node:fs";
import { describe, expect, it } from "vitest";
import { loadRecords } from "../scripts/omics/records";
import { claimPins, deriveUseCaseInputs, useCaseHash, type JudgementPin } from "../shared/omics/use-cases";
import type { CatalogueRecord } from "../shared/omics/catalogue-query";

const store = loadRecords() as unknown as CatalogueRecord[];
const derive = (records: CatalogueRecord[]) => deriveUseCaseInputs({ records });
const mappingId = "use-case-mapping-cnv-20261009-gabrielaite2021-na12878";
const protocolId = "cnv-20261009-protocol-gabrielaite2021-na12878-wgs-overlap";
const mapping = (records: CatalogueRecord[]) => derive(records).mappings.find((m) => m.id === mappingId)!;
const edit = (id: string, change: (r: CatalogueRecord) => CatalogueRecord) =>
  store.map((r) => (r.id === id ? change(structuredClone(r)) : r));

describe("use cases as records", () => {
  it("derives every migrated use case and relevance judgement from the store", () => {
    // Later collection batches add judgements, so count only the ones the migration wrote.
    const migrated = new Set(fs.readFileSync("data/omics/use-case-records-20261009/batch.jsonl", "utf8")
      .split("\n").filter(Boolean).map((line) => JSON.parse(line).id as string));
    const inputs = derive(store);
    const mappings = inputs.mappings.filter((m) => migrated.has(m.id));
    expect(inputs.use_cases.filter((u) => migrated.has(u.id))).toHaveLength(26);
    expect(mappings).toHaveLength(100);
    expect(mappings.filter((m) => m.lifecycle === "active")).toHaveLength(97);
    expect(mappings.filter((m) => m.lifecycle === "draft").map((m) => m.id).sort()).toEqual([
      "use-case-mapping-cnv-20261009-delavega2025-coriell-panel",
      "use-case-mapping-cnv-20261009-delavega2025-hg002",
      "use-case-mapping-cnv-20261009-nardone2025-hg002-deletions",
    ]);
  });

  it("withholds a judgement when a pinned field changes meaning", () => {
    const m = mapping(edit(protocolId, (r) => ({ ...r, attributes: { ...r.attributes, protocol: "A different matching rule" } })));
    expect(m.lifecycle).toBe("needs_review");
    expect(m.reason).toContain("pinned evidence changed");
  });

  it("withholds on a link change, and a re-pin after review restores it", () => {
    const renamed = edit(protocolId, (r) => ({ ...r, links: r.links.map((l) => ({ ...l, relation: l.relation === "uses_data" ? "used_in" : l.relation })) }));
    expect(mapping(renamed).lifecycle).toBe("needs_review");
    const byId = new Map(renamed.map((r) => [r.id, r]));
    const repinned = renamed.map((r) => (r.id === mappingId ? { ...r, attributes: { ...r.attributes, pins: claimPins(byId, r) } } : r));
    expect(mapping(repinned).lifecycle).toBe("active");
  });

  it("includes a new reviewed evaluation on the protocol without a new judgement", () => {
    const original = mapping(store);
    const template = store.find((r) => r.id === original.evaluation_ids[0])!;
    const results = store.filter((r) => r.kind === "result" && r.links.some((l) => l.target_id === template.id));
    const copy = { ...structuredClone(template), id: "test-new-evaluation" };
    const copiedResults = results.map((r, i) => ({ ...structuredClone(r), id: `test-new-result-${i}`, links: [{ relation: "evaluation", target_id: copy.id }] }));
    const m = mapping([...store, copy, ...copiedResults]);
    expect(m.lifecycle).toBe("active");
    expect(m.evaluation_ids).toContain("test-new-evaluation");
    expect(m.evaluation_ids).toHaveLength(original.evaluation_ids.length + 1);
  });

  it("withholds a judgement when a cited source gains an evidence concern", () => {
    const sourceId = mapping(store).citations[0].source_id;
    const m = mapping(edit(sourceId, (r) => ({ ...r, attributes: { ...r.attributes, evidence_concerns: [{ message: "test" }] } })));
    expect(m.lifecycle).toBe("needs_review");
  });

  it("treats an unreviewed judgement as a draft", () => {
    expect(mapping(edit(mappingId, (r) => ({ ...r, status: "needs_review" }))).lifecycle).toBe("draft");
  });

  it("groups strata of one comparison in order", () => {
    const inputs = derive(store);
    const bins = inputs.mappings
      .filter((m) => m.presentation?.group === "behera2024-hg002-deletions")
      .sort((a, b) => (a.presentation!.stratum_order ?? 0) - (b.presentation!.stratum_order ?? 0));
    expect(bins.map((m) => m.presentation!.stratum_label)).toEqual(["1 to 5 kb", "5 to 10 kb", "10 to 20 kb", "20 to 50 kb", "Over 50 kb"]);
    expect(new Set(bins.map((m) => m.presentation!.headline_metric))).toEqual(new Set(["f1-score"]));
  });

  it("publishes a summary only once it is reviewed and pinned", () => {
    const summaryId = "use-case-summary-cnv-detection-characterisation";
    const cnv = (records: CatalogueRecord[]) => derive(records).use_cases.find((u) => u.id === "use-case-cnv-detection-characterisation")!;
    const draft = edit(summaryId, (r) => ({ ...r, status: "needs_review" as const, attributes: { ...r.attributes, pins: undefined } }));
    expect(cnv(draft).summary).toBeUndefined();
    const byId = new Map(store.map((r) => [r.id, r]));
    expect(cnv(store).summary?.status).toBe("reviewed");
    const reviewed = edit(summaryId, (r) => {
      const next = { ...r, status: "source_checked" as const };
      return { ...next, attributes: { ...next.attributes, pins: claimPins(byId, next) } };
    });
    expect(cnv(reviewed).summary?.status).toBe("reviewed");
    const evaluationId = mapping(store).evaluation_ids[0];
    const resultId = store.find((r) => r.kind === "result" && r.links.some((l) => l.target_id === evaluationId))!.id;
    const changed = reviewed.map((r) => (r.id === resultId ? { ...r, attributes: { ...r.attributes, printed_value: "0.999" } } : r));
    expect(cnv(changed).summary).toBeUndefined();
  });

  it("stores pins that match the store for every reviewed judgement", () => {
    const byId = new Map(store.map((r) => [r.id, r]));
    const stale = store.filter((r) => r.kind === "claim" && r.status === "source_checked" && String(r.attributes.field).startsWith("links:assessed_by:"))
      .filter((r) => useCaseHash(claimPins(byId, r)!) !== useCaseHash(r.attributes.pins as JudgementPin[]));
    expect(stale.map((r) => r.id)).toEqual([]);
  });

  it("withholds a judgement when a reviewed result changes value", () => {
    const evaluationId = mapping(store).evaluation_ids[0];
    const resultId = store.find((r) => r.kind === "result" && r.links.some((l) => l.target_id === evaluationId))!.id;
    const m = mapping(edit(resultId, (r) => ({ ...r, attributes: { ...r.attributes, numeric_value: "0.999" } })));
    expect(m.lifecycle).toBe("needs_review");
    expect(m.reason).toContain(resultId);
  });

  it("withholds the whole judgement when a reviewed evaluation drops out, rather than shrinking it", () => {
    const evaluationId = mapping(store).evaluation_ids[0];
    const m = mapping(edit(evaluationId, (r) => ({ ...r, status: "disputed" })));
    expect(m.lifecycle).toBe("needs_review");
    expect(m.reason).toContain("no longer eligible");
  });

  it("withholds rather than fails on a disputed judgement or a use-case source concern", () => {
    expect(mapping(edit(mappingId, (r) => ({ ...r, status: "disputed" }))).lifecycle).toBe("needs_review");
    const useCase = store.find((r) => r.id === "use-case-cnv-detection-characterisation")!;
    if (useCase.source_ids.length) {
      const m = mapping(edit(useCase.source_ids[0], (r) => ({ ...r, attributes: { ...r.attributes, evidence_concerns: [{ message: "test" }] } })));
      expect(m.lifecycle).toBe("needs_review");
    }
  });

  it("does not withhold judgements when the use case gains a gap", () => {
    const grown = edit("use-case-cnv-detection-characterisation", (r) => ({ ...r, attributes: { ...r.attributes, evidence_gaps: [...(r.attributes.evidence_gaps as string[]), "A new gap"] } }));
    expect(mapping(grown).lifecycle).toBe("active");
  });

  it("rejects an assessed_by link that no judgement backs", () => {
    const useCase = "use-case-cnv-detection-characterisation";
    const orphan = edit(useCase, (r) => ({ ...r, links: [...r.links, { relation: "assessed_by", target_id: "ucc-research-protocol-cppc-prospective-selection" }] }));
    expect(() => derive(orphan)).toThrow("no relevance judgement claim");
  });
});
