import { describe, expect, it } from "vitest";
import { loadRecords } from "../scripts/omics/records";
import { deriveUseCaseInputs } from "../shared/omics/use-cases";
import type { CatalogueRecord } from "../shared/omics/catalogue-query";

const store = loadRecords() as unknown as CatalogueRecord[];
const derive = (records: CatalogueRecord[]) => deriveUseCaseInputs({ records });
const mappingId = "use-case-mapping-cnv-20261009-gabrielaite2021-na12878";
const protocolId = "cnv-20261009-protocol-gabrielaite2021-na12878-wgs-overlap";
const mapping = (records: CatalogueRecord[]) => derive(records).mappings.find((m) => m.id === mappingId)!;
const edit = (id: string, change: (r: CatalogueRecord) => CatalogueRecord) =>
  store.map((r) => (r.id === id ? change(structuredClone(r)) : r));

describe("use cases as records", () => {
  it("derives every use case and relevance judgement from the store", () => {
    const inputs = derive(store);
    expect(inputs.use_cases).toHaveLength(26);
    expect(inputs.mappings).toHaveLength(100);
    expect(inputs.mappings.filter((m) => m.lifecycle === "active")).toHaveLength(97);
    expect(inputs.mappings.filter((m) => m.lifecycle === "draft").map((m) => m.id).sort()).toEqual([
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

  it("does not withhold a judgement when only a relation name changes", () => {
    const renamed = edit(protocolId, (r) => ({ ...r, links: r.links.map((l) => ({ ...l, relation: l.relation === "uses_data" ? "used_in" : l.relation })) }));
    expect(mapping(renamed).lifecycle).toBe("active");
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
    const source = store.find((r) => r.id === mapping(store).citations[0].source_id)!;
    const m = mapping(edit(source.id, (r) => ({ ...r, attributes: { ...r.attributes, evidence_concerns: [{ message: "test" }] } })));
    expect(m.lifecycle).toBe("needs_review");
  });

  it("treats an unreviewed judgement as a draft", () => {
    expect(mapping(edit(mappingId, (r) => ({ ...r, status: "needs_review" }))).lifecycle).toBe("draft");
  });

  it("rejects an assessed_by link that no judgement backs", () => {
    const useCase = "use-case-cnv-detection-characterisation";
    const orphan = edit(useCase, (r) => ({ ...r, links: [...r.links, { relation: "assessed_by", target_id: "ucc-research-protocol-cppc-prospective-selection" }] }));
    expect(() => derive(orphan)).toThrow("no relevance judgement claim");
  });
});
