import { describe, expect, it } from "vitest";
import { areaTier, deriveTier } from "../shared/omics/depth-tier";
import { linkedUseCaseTiers } from "../scripts/omics/depth-tier";
import { attributeIssues } from "../shared/omics/attributes";

const rec = (kind: string, areas: string[], contexts: string[] = []) => ({ id: `${kind}-x`, kind, facets: { areas, contexts } });

describe("tier rule", () => {
  it("puts DNA and RNA models and methods in tier 1, protein in tier 2, the rest in tier 3", () => {
    expect(deriveTier(rec("model", ["dna-genomes"]))).toBe(1);
    expect(deriveTier(rec("method", ["rna-transcriptomes"]))).toBe(1);
    expect(deriveTier(rec("model", ["protein-function"]))).toBe(2);
    expect(deriveTier(rec("benchmark", ["proteins-complexes", "molecular-interactions"]))).toBe(2);
    expect(deriveTier(rec("model", ["cells-tissues", "single-cell"]))).toBe(3);
    expect(deriveTier(rec("model", ["molecular-interactions"]))).toBe(3);
  });
  it("gives a record with genomic and protein areas the lower tier number", () => {
    expect(deriveTier(rec("method", ["dna-genomes", "proteins-complexes"]))).toBe(1);
    expect(deriveTier(rec("model", ["protein-structure", "rna-transcriptomes"]))).toBe(1);
  });
  it("puts every genomic use case in tier 1, clinical or not", () => {
    expect(deriveTier(rec("use_case", ["dna-genomes"], ["clinical_research"]))).toBe(1);
    expect(deriveTier(rec("use_case", ["rna-transcriptomes"], ["research"]))).toBe(1);
    expect(deriveTier(rec("use_case", ["proteins-complexes"], ["clinical_research"]))).toBe(2);
  });
  it("cannot place a record without areas unless a tier is set by hand", () => {
    expect(areaTier(rec("model", []))).toBeUndefined();
    expect(deriveTier(rec("model", []))).toBeUndefined();
    expect(deriveTier(rec("model", []), [], 2)).toBe(2);
  });
  it("raises a benchmark to the best tier of the use cases that judge it relevant", () => {
    expect(deriveTier(rec("benchmark", ["microbes-communities"]), [1, 3])).toBe(1);
    expect(deriveTier(rec("benchmark", ["dna-genomes"]), [3])).toBe(1);
    expect(deriveTier(rec("benchmark", []), [2])).toBe(2);
    expect(deriveTier(rec("model", ["cells-tissues"]), [1])).toBe(3);
  });
});

describe("linked use-case tiers", () => {
  const r = (id: string, kind: string, links: [string, string][] = [], extra: object = {}) =>
    ({ id, kind, name: id, status: "source_checked", facets: {}, source_ids: [], links: links.map(([relation, target_id]) => ({ relation, target_id })), attributes: {}, ...extra }) as never;
  it("follows relevance judgements through protocols and tasks to their benchmarks, skipping excluded ones", () => {
    const useCases = [r("uc-clin", "use_case", [], { facets: { areas: ["dna-genomes"], contexts: ["clinical_research"] } }),
      r("uc-res", "use_case", [], { facets: { areas: ["cells-tissues"], contexts: ["research"] } })];
    const benchmarks = [r("b1", "benchmark"), r("b2", "benchmark")];
    const parents = [r("p1", "protocol", [["part_of", "t1"]]), r("t1", "task", [["part_of", "b1"]]), r("p2", "protocol", [["part_of", "b2"]])];
    const judge = (id: string, uc: string, target: string, status = "source_checked") =>
      r(id, "claim", [["subject", uc]], { status, attributes: { field: `links:assessed_by:${target}`, value: target } });
    const claims = [judge("c1", "uc-clin", "p1"), judge("c2", "uc-res", "p2"), judge("c3", "uc-clin", "p2", "excluded")];
    const linked = linkedUseCaseTiers({ useCases, benchmarks, parents, claims });
    expect(linked.get("b1")).toEqual([1]);
    expect(linked.get("b2")).toEqual([3]);
  });
});

describe("depth_tier attribute", () => {
  it("accepts 1, 2 or 3 on the four kinds and nothing else", () => {
    const at = (kind: string, tier: unknown) => attributeIssues({ id: "x", kind, links: [], attributes: { depth_tier: tier } });
    for (const kind of ["model", "method", "benchmark", "use_case"]) expect(at(kind, 2)).toEqual([]);
    expect(at("model", 4)).toHaveLength(1);
    expect(at("model", "1")).toHaveLength(1);
    expect(at("dataset", 1)).toEqual(["undeclared attribute depth_tier"]);
  });
});
