import { describe, expect, it } from "vitest";
import { loadRecords } from "../scripts/omics/records";
import { deriveUseCaseInputs, type JudgementPin } from "../shared/omics/use-cases";
import type { CatalogueRecord } from "../shared/omics/catalogue-query";
import { batchRecords } from "./helpers/records";

const BATCH = "data/omics/use-case-pages-20261127";
const SLUGS = [
  "genomic-sequence-element-annotation", "rna-structure-prediction", "single-cell-data-integration",
  "protein-function-annotation", "protein-representation-property-prediction", "protein-design-quality",
  "glycan-property-prediction",
];
// Held after the independent verification and removed with their judgements before any release.
const HELD = ["rna-sequence-property-prediction", "gene-regulatory-network-inference"];

describe("new use cases (2026-11-27)", () => {
  const stored = batchRecords(BATCH);
  const allRecords = loadRecords() as unknown as CatalogueRecord[];
  const inputs = deriveUseCaseInputs({ records: allRecords });
  const cases = stored.filter((r) => r.kind === "use_case");
  const claims = stored.filter((r) => r.kind === "claim");

  it("keeps seven research-only use cases, each citing sources and stating how many studies it rests on", () => {
    expect(cases.map((c) => c.attributes.slug).sort()).toEqual([...SLUGS].sort());
    for (const slug of HELD) expect(inputs.use_cases.some((u) => u.slug === slug), slug).toBe(false);
    const fixes = batchRecords("data/omics/use-case-pages-fixes-20261127");
    expect(fixes.filter((r) => r.kind === "use_case").map((r) => r.attributes.slug)).toEqual(["viral-microbial-sequence-classification"]);
    // The second verification pass untied GenBench human-vs-worm and long-range species classification.
    const untied = /genbench-protocol-(short-human-vs-worm|long-species-classification)$/;
    for (const claim of fixes.filter((r) => r.kind === "claim"))
      expect(inputs.mappings.find((m) => m.id === claim.id)?.lifecycle, String(claim.id)).toBe(untied.test(String(claim.id)) ? undefined : "active");
    for (const entry of cases) {
      const published = inputs.use_cases.find((u) => u.slug === entry.attributes.slug);
      expect(published, String(entry.id)).toBeDefined();
      expect(published!.contexts, String(entry.id)).toEqual(["research"]);
      expect(entry.source_ids.length, String(entry.id)).toBeGreaterThan(0);
      expect(published!.citations.length, String(entry.id)).toBeGreaterThan(0);
      // Every page says what its evidence rests on, so a one-study page does not read as settled.
      expect(published!.evidence_gaps.some((gap) => /\bstud(y|ies)\b/.test(gap)), String(entry.id)).toBe(true);
      expect(published!.clinical_scope, String(entry.id)).toMatch(/Research only/);
      // No literature search ran for these questions, so none claims a checked date.
      expect(published!.evidence_checked, String(entry.id)).toBeUndefined();
      expect([1, 2, 3], String(entry.id)).toContain(entry.attributes.depth_tier);
    }
  });

  it("activates every judgement it adds that was not later withdrawn, with pins and eligible evaluations", () => {
    expect(claims).toHaveLength(221);
    const withdrawn = claims.filter((c) => c.status === "excluded");
    expect(withdrawn).toHaveLength(18);
    for (const claim of withdrawn) expect(inputs.mappings.some((m) => m.id === claim.id), String(claim.id)).toBe(false);
    for (const claim of claims.filter((c) => c.status !== "excluded")) {
      const mapping = inputs.mappings.find((m) => m.id === claim.id);
      expect(mapping, String(claim.id)).toBeDefined();
      expect(mapping!.lifecycle, String(claim.id)).toBe("active");
      expect(mapping!.evaluation_ids.length, String(claim.id)).toBeGreaterThan(0);
      expect(((claim.attributes.pins as JudgementPin[]) || []).length, String(claim.id)).toBeGreaterThan(0);
    }
  });

  it("keeps the questions apart: variant effect, annotation transfer and binder design stay where they were", () => {
    const linked = new Set(inputs.mappings.map((m) => `${m.use_case_id}|${m.protocol_id}`));
    for (const [useCase, protocol] of [
      // Zero-shot likelihood scoring is the protein variant effect question, not representation probing.
      ["use-case-protein-representation-property-prediction", "hyplm-flash-20261106-protocol-proteingym-zero-shot"],
      // Annotation transfer stays on the annotation use case.
      ["use-case-single-cell-data-integration", "hycell-20261106-protocol-annotation-transfer-knn"],
      // Conservation and variant scoring are not element annotation.
      ["use-case-genomic-sequence-element-annotation", "lit-genomics-20261011-guanine-protocol-cons30"],
      ["use-case-genomic-sequence-element-annotation", "lit-genomics-20261011-guanine-protocol-clinvar-snv"],
      ["use-case-genomic-sequence-element-annotation", "lit-genomics-20261011-guanine-protocol-gpra-c"],
      // Expression, 3D structure and taxonomic classification are not element annotation.
      ["use-case-genomic-sequence-element-annotation", "lit-genomics-20261011-genbench-protocol-bulk-rna-expression"],
      ["use-case-genomic-sequence-element-annotation", "lit-genomics-20261011-genbench-protocol-short-virus-covid-variant-classification"],
      // Means of tied rows, and GENEB scores that mix element and species categories.
      ["use-case-genomic-sequence-element-annotation", "lit-genomics-20261011-genbench-protocol-short-human-promoter-detection"],
      ["use-case-genomic-sequence-element-annotation", "lit-genomics-20261011-geneb-protocol-full"],
      ["use-case-single-cell-data-integration", "hycell-20261106-protocol-composite-score"],
      ["use-case-protein-representation-property-prediction", "hyplm-flash-20261106-protocol-regression-ten-split-average"],
      // The RNA structure use case excludes attention-map secondary structure in as many words.
      ["use-case-rna-structure-prediction", "lit-rna-20261011-rnalm-zeroshot-protocol-t4-mcc-mean"],
      // Folding stability of substitutions is the protein stability question; throughput is a cost.
      ["use-case-protein-representation-property-prediction", "hyplm-flash-20261106-protocol-stability"],
      ["use-case-protein-representation-property-prediction", "hyplm-flash-20261106-protocol-embedding-throughput-h20"],
    ]) expect(linked.has(`${useCase}|${protocol}`), protocol).toBe(false);
    // The question names splice sites, so splice-site classification is direct (verification, 27 November).
    const splice = inputs.mappings.filter((m) => m.use_case_id === "use-case-genomic-sequence-element-annotation"
      && /ntbench-protocol-splice-|segmentnt-supplement-2025-task-splice-|genbench-protocol-(long-splice-splice|short-human-splice-site)/.test(m.protocol_id!));
    expect(splice).toHaveLength(13);
    for (const m of splice) expect(m.relevance, m.protocol_id).toBe("direct");
    // The RhoFold+ developers' best-of-five targets are proxy.
    const rhofold = inputs.mappings.filter((m) => /rhofold-2024-casp15-natural-task-/.test(m.protocol_id!));
    expect(rhofold).toHaveLength(12);
    for (const m of rhofold) expect(m.relevance, m.protocol_id).toBe("proxy");
    expect(inputs.mappings.find((m) => m.protocol_id === "rewire-protocol-flip2-rhomax-by-wild-type-v1"
      && m.use_case_id === "use-case-protein-representation-property-prediction")?.relevance).toBe("proxy");
  });
});
