import { describe, expect, it } from "vitest";
import { loadRecords } from "../scripts/omics/records";
import { deriveUseCaseInputs, type JudgementPin } from "../shared/omics/use-cases";
import type { CatalogueRecord } from "../shared/omics/catalogue-query";
import { batchRecords } from "./helpers/records";

describe("variant interpretation use-case links (2026-11-23)", () => {
  const stored = batchRecords("data/omics/use-case-variant-links-20261123");
  const allRecords = loadRecords() as unknown as CatalogueRecord[];
  const inputs = deriveUseCaseInputs({ records: allRecords });

  it("activates all 28 newly added proxy relevance judgements", () => {
    expect(stored).toHaveLength(28);
    for (const claim of stored) {
      const mapping = inputs.mappings.find((m) => m.id === claim.id);
      expect(mapping, claim.id).toBeDefined();
      expect(mapping!.lifecycle, claim.id).toBe("active");
      expect(mapping!.relevance, claim.id).toBe("proxy");
      expect(mapping!.evaluation_ids.length).toBeGreaterThan(0);
    }
  });

  it("excludes concerned and non-configuration evaluations from active mappings", () => {
    const snv200 = inputs.mappings.find((m) => m.id === "use-case-mapping-20261123-rewire-local-20261121-rdv2-protocol-snv-200-main")!;
    expect(snv200.evaluation_ids).toHaveLength(16);
    expect(snv200.evaluation_ids).not.toContain("rewire-local-20261121-rdv2-evaluation-rule-avi-snv-200");

    const evee = inputs.mappings.find((m) => m.id === "use-case-mapping-20261123-gfm-guide-20261014-protocol-evee-deconfounded-snv-auroc")!;
    expect(evee.evaluation_ids).toHaveLength(6);
    expect(evee.evaluation_ids).not.toContain("gfm-guide-20261014-eval-evee-deconfounded-ntv3-cosine");
    expect(evee.evaluation_ids).not.toContain("gfm-guide-20261014-eval-evee-deconfounded-alphamissense");

    const gpnmsa = inputs.mappings.find((m) => m.id === "use-case-mapping-20261123-gfm-guides-20261014-gpnmsa-protocol-ablation-clinvar-auroc")!;
    expect(gpnmsa.evaluation_ids).toHaveLength(15);
    expect(gpnmsa.evaluation_ids).not.toContain("gfm-guides-20261014-gpnmsa-eval-ablation-msa-frequency-clinvar");
    expect(gpnmsa.evaluation_ids).not.toContain("gfm-guides-20261014-gpnmsa-eval-ablation-phylop-phastcons-combined-clinvar");
  });

  it("leaves disputed #163 Brixi strata, unreviewed alphagenome-2026 splicing, and method/model-only traitgym-20261116 protocols unlinked", () => {
    const linked = new Set(inputs.mappings.map((m) => m.protocol_id));
    for (const excluded of [
      "gfm-guides-20261014-evo2-brixi2026-protocol-clinvar-coding-non-snv",
      "gfm-guides-20261014-evo2-brixi2026-protocol-clinvar-noncoding-non-snv",
      "gfm-guides-20261014-evo2-brixi2026-protocol-clinvar-noncoding-snv",
      "gfm-guides-20261014-evo2-brixi2026-protocol-splicevardb-intronic-snv",
      "alphagenome-2026-t3-protocol-1",
      "alphagenome-2026-t4-protocol-7",
      "traitgym-20261116-protocol-mendelian-matched-feature-global-auprc",
      "traitgym-20261116-protocol-mendelian-per-trait-best-of-zero-shot-and-linear-probing",
    ]) {
      expect(linked.has(excluded), excluded).toBe(false);
    }
    expect(stored.every((c) => Array.isArray((c.attributes.pins as JudgementPin[]) || []) && (c.attributes.pins as JudgementPin[]).length > 0)).toBe(true);
  });
});
