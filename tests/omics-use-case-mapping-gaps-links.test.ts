import { describe, expect, it } from "vitest";
import { loadRecords } from "../scripts/omics/records";
import { deriveUseCaseInputs, type JudgementPin } from "../shared/omics/use-cases";
import type { CatalogueRecord } from "../shared/omics/catalogue-query";
import { batchRecords } from "./helpers/records";

describe("use-case mapping gaps links (2026-11-27)", () => {
  const stored = batchRecords("data/omics/use-case-mapping-gaps-20261127");
  const allRecords = loadRecords() as unknown as CatalogueRecord[];
  const inputs = deriveUseCaseInputs({ records: allRecords });

  it("activates all 12 proxy judgements, each pinned and with eligible evaluations", () => {
    expect(stored).toHaveLength(12);
    for (const claim of stored) {
      const mapping = inputs.mappings.find((m) => m.id === claim.id);
      expect(mapping, claim.id).toBeDefined();
      expect(mapping!.lifecycle, claim.id).toBe("active");
      expect(mapping!.relevance, claim.id).toBe("proxy");
      expect(mapping!.evaluation_ids.length, claim.id).toBeGreaterThan(0);
      const pinned = allRecords.find((r) => r.id === claim.id)!;
      expect(((pinned.attributes.pins as JudgementPin[]) || []).length, claim.id).toBeGreaterThan(0);
    }
    const byUseCase = (id: string) => stored.filter((c) => c.links[0].target_id === id).length;
    expect(byUseCase("use-case-cell-type-annotation-transfer")).toBe(4);
    expect(byUseCase("use-case-mass-spectrum-molecule-shortlisting")).toBe(8);
  });

  it("leaves out method-linked, concerned, unreviewed, formula-conditioned and out-of-scope protocols", () => {
    const linked = new Set(inputs.mappings.map((m) => `${m.use_case_id}|${m.protocol_id}`));
    for (const [useCase, protocol] of [
      ["use-case-cell-type-annotation-transfer", "scfoundation-2024-supp-table4-task-zheng68k"],
      ["use-case-cell-type-annotation-transfer", "scfoundation-2024-supp-table4-task-segerstolpe"],
      ["use-case-phenotype-perturbation-selection", "pheno-20261022-protocol-song2025-simple-hit-classification"],
      ["use-case-mass-spectrum-molecule-shortlisting", "paper-protocol-a18b4bc79049513fb7"],
      ["use-case-mass-spectrum-molecule-shortlisting", "msalign-2026-table3-task-nplib1-formula-supplied-r-1"],
      ["use-case-splicing-follow-up", "rna-splicing-20261011-fortier2026-protocol-barbosa-clinvar"],
      ["use-case-genetic-perturbation-response", "lit-cells-networks-20261011-perturbench-v4-protocol-srivatsan20"],
    ]) expect(linked.has(`${useCase}|${protocol}`), protocol).toBe(false);
  });
});
