import { describe, expect, it } from "vitest";
import { loadRecords } from "../scripts/omics/records";
import { deriveUseCaseInputs, type JudgementPin } from "../shared/omics/use-cases";
import type { CatalogueRecord } from "../shared/omics/catalogue-query";
import { batchRecords } from "./helpers/records";

describe("proxy candidates applied (2026-11-27)", () => {
  const stored = batchRecords("data/omics/use-case-mapping-proxy-20261127");
  const allRecords = loadRecords() as unknown as CatalogueRecord[];
  const inputs = deriveUseCaseInputs({ records: allRecords });

  it("keeps the 34 of 72 proxy judgements the second verification pass agreed, each pinned", () => {
    expect(stored).toHaveLength(72);
    const current = new Map(allRecords.map((r) => [r.id, r]));
    const live = stored.filter((c) => current.get(c.id)!.status !== "excluded");
    expect(live).toHaveLength(34);
    for (const claim of stored.filter((c) => current.get(c.id)!.status === "excluded"))
      expect(inputs.mappings.some((m) => m.id === claim.id), String(claim.id)).toBe(false);
    for (const claim of live) {
      const mapping = inputs.mappings.find((m) => m.id === claim.id);
      expect(mapping?.lifecycle, String(claim.id)).toBe("active");
      // The two CASP16 series tests each score one congeneric series, so they are direct.
      expect(mapping!.relevance, String(claim.id)).toBe(/leakctl-protocol-casp16-l[13]000$/.test(String(claim.id)) ? "direct" : "proxy");
      expect(((current.get(claim.id)!.attributes.pins as JudgementPin[]) || []).length, String(claim.id)).toBeGreaterThan(0);
    }
  });

  it("feeds only the missense stratum of Lu et al. to missense PP3/BP4", () => {
    const lu = inputs.mappings.find((m) => m.id === "use-case-mapping-20261127-proxy-missense-pp3-bp4-calibrated-evidence-lu-hetero-20261019-protocol-clinvar-variant-type-auroc")!;
    expect(lu.lifecycle).toBe("active");
    expect(lu.evaluation_ids).toHaveLength(12);
  });

  it("refuses what an exclusion, a precedent or a gate rules out", () => {
    const linked = new Set(inputs.mappings.map((m) => `${m.use_case_id}|${m.protocol_id}`));
    for (const [useCase, protocol] of [
      ["use-case-de-novo-binder-design", "rfd4-proteina-20261115-protocol-ppi-all-atom-passers-per-gpu-hour"],
      ["use-case-splicing-follow-up", "rna-splicing-20261011-fortier2026-protocol-barbosa-clinvar"],
      ["use-case-structural-hypotheses-experiments", "ucc-research-protocol-foldbench-rna-monomer"],
      ["use-case-structural-hypotheses-experiments", "acquired-protocol-8068932c1a23c9c3f049"],
      ["use-case-missense-pp3-bp4-calibrated-evidence", "gfm-guides-20261014-evo2-brixi2026-protocol-clinvar-coding-non-snv"],
      // Strata of a tied set, totals of tied parts, and rows that compare no models.
      ["use-case-missense-pp3-bp4-calibrated-evidence", "gfm-guides-20261014-evo2-brixi2026-protocol-clinvar-coding-snv-near-splice-site"],
      ["use-case-regulatory-variant-gene-follow-up", "gfm-guides-20261014-evo2-brixi2026-protocol-clinvar-noncoding-snv-highly-conserved"],
      ["use-case-regulatory-variant-gene-follow-up", "traitgym-20261116-protocol-complex-per-trait-best-borzoi-tissue-track-auprc"],
      ["use-case-structural-hypotheses-experiments", "ucc-docking-cluspro-bm5-2020-protocol-total-top10"],
      ["use-case-structural-hypotheses-experiments", "lit-structure-20261011-lipp-protocol-rmsd-lipp-331"],
    ]) expect(linked.has(`${useCase}|${protocol}`), protocol).toBe(false);
  });
});
