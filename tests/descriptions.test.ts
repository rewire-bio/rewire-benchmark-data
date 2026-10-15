import { describe, expect, it } from "vitest";
import { descriptionProblems, validateDescriptions } from "../shared/omics/descriptions";
import { applyCorrection } from "../scripts/omics/apply-corrections";

const rec = (id: string, kind: string, description: string, extra: { name?: string; status?: string } = {}) =>
  ({ id, kind, name: extra.name ?? id, description, status: extra.status ?? "source_checked" });
const rules = (description: string, kind = "model") => descriptionProblems([rec("a", kind, description)]).map((p) => p.rule);

describe("functional descriptions (issue #88)", () => {
  it("accepts a sentence that says what the method does", () => {
    expect(rules("Calls somatic SNVs by a Bayesian comparison of tumour and normal genotype likelihoods.", "method")).toEqual([]);
    expect(rules("AIDO.DNA-300M: Frozen backbone; sequence embeddings fed to an MLP head.", "configuration")).toEqual([]);
  });

  it("rejects placeholders", () => {
    expect(rules("Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.")).toContain("named-family-placeholder");
    expect(rules("Identity as reported in this paper. Unspecified versions are not assumed equivalent to other papers.")).toContain("identity-as-reported");
    expect(rules("Exact source-reported configuration or submission label. Family membership, checkpoint identity and aliases have not been inferred.", "configuration")).toContain("source-label-placeholder");
    expect(rules("Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.", "service")).toContain("catalogue-placeholder");
  });

  it("rejects provenance and source locators", () => {
    expect(rules("Kraken2 as run in Portik et al. 2022.", "configuration")).toContain("as-run-in");
    expect(rules("Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution.", "pipeline")).toEqual(
      expect.arrayContaining(["quoted-in", "not-new-execution"]));
    expect(rules("Sequence-to-function model of regulatory DNA (Manzo et al. 2025 Table 3).")).toContain("locator-in-parentheses");
    expect(rules("RNA language model pre-trained on small non-coding RNA (Table 1).")).toContain("locator-in-parentheses");
    expect(rules("Shannon entropy of fragment lengths per exon. Cited in the source as ref 18.", "method")).toContain("cited-as-reference");
  });

  it("rejects one description shared by differently named entities, but not by configurations", () => {
    const shared = "Biomolecular structure and affinity model family.";
    const problems = descriptionProblems([rec("boltz", "model", shared, { name: "Boltz" }), rec("boltz-2", "model", shared, { name: "Boltz-2" })]);
    expect(problems.map((p) => [p.id, p.rule])).toEqual([["boltz", "shared-description"], ["boltz-2", "shared-description"]]);
    expect(descriptionProblems([rec("c1", "configuration", "Configuration of X; its settings are not recorded.", { name: "X a" }),
      rec("c2", "configuration", "Configuration of X; its settings are not recorded.", { name: "X b" })])).toEqual([]);
  });

  it("ignores excluded records and kinds that are not described systems", () => {
    expect(descriptionProblems([rec("a", "model", "Identity as reported in this paper.", { status: "excluded" })])).toEqual([]);
    expect(descriptionProblems([rec("d", "dataset", "Kraken2 as run in Portik et al. 2022.")])).toEqual([]);
  });

  it("leaves a missing description to the schema check", () => {
    expect(descriptionProblems([{ id: "a", kind: "model", name: "a" } as unknown as Parameters<typeof descriptionProblems>[0][number]])).toEqual([]);
  });

  it("fails validation with the record and a pointer to provenance_note", () => {
    expect(() => validateDescriptions([rec("a", "model", "Identity as reported in this paper.")])).toThrow(/a: placeholder[\s\S]*provenance_note|provenance_note[\s\S]*a: placeholder/);
  });
});

describe("records:correct description rows", () => {
  const row = (old_value: string, new_value: string) => ({ record_id: "a", field: "description", old_value, new_value, evidence: "review" });
  it("replaces a description only when the old value matches", () => {
    const record = { id: "a", description: "Kraken2 as run in Portik et al. 2022.", facets: {}, attributes: {} };
    applyCorrection(record, row("Kraken2 as run in Portik et al. 2022.", "Kraken2 with the PlusPF database."));
    expect(record.description).toBe("Kraken2 with the PlusPF database.");
    expect(() => applyCorrection(record, row("stale", "x"))).toThrow("the table expects");
    expect(() => applyCorrection(record, row("Kraken2 with the PlusPF database.", ""))).toThrow("cannot be removed");
  });
});
