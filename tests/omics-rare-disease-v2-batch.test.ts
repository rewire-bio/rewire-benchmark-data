import { describe, expect, it } from "vitest";
import { batchRecords, recordsById } from "./helpers/records";

// Rewire's rare-disease-v2 study. These rulings came out of a review of the first draft of the
// batch (docs/reviews/2026-11-21-rare-disease-v2-records.md).
describe("rare-disease-v2 records", () => {
  const prefix = "rewire-local-20261121-rdv2";
  const stored = batchRecords("data/omics/rewire-rare-disease-v2-20261121");
  const evaluations = stored.filter((record) => record.kind === "evaluation");
  const receipt = (name: string) => `${prefix}-receipt-evo2-${name}`;
  const citing = (name: string) =>
    stored.filter((record) => record.kind !== "source" && record.source_ids.includes(receipt(name))).map((record) => record.id);

  it("claim no reproduction and carry no run recipe", () => {
    expect(stored.length).toBeGreaterThan(0);
    expect(stored.filter((record) => record.status !== "source_checked").map((record) => record.id)).toEqual([]);
    expect(stored.filter((record) => record.attributes.run_recipes || record.attributes.reproduction).map((record) => record.id)).toEqual([]);
  });

  it("do not cite the first study's SNV-only scoring run on the indel cases", () => {
    // The 120 indel analysis ranks indels only, and rare-disease/evo2/run scored no indel.
    expect(citing("run").filter((id) => id.includes("indel-120"))).toEqual([]);
    // run-extra scored 9 diagnostics of the 200 only. The locked model was fitted on the 200, so its configuration cites it too.
    const fittedOn200 = (id: string) => id.includes("snv-200") || id.endsWith("-configuration-evo-2") || id.endsWith("-configuration-lookups-evo-2-locked");
    expect(citing("run-extra").filter((id) => !fittedOn200(id))).toEqual([]);
    // The runs that did score ranked indels are still cited there.
    for (const name of ["run2", "run3"])
      expect(citing(name).filter((id) => id.includes("indel-120")).length).toBe(9);
    const note = String(recordsById.get(`${prefix}-evaluation-evo-2-indel-120`)!.attributes.reproduction_note);
    expect(note).not.toContain("16 to 17 October");
    expect(note).toContain("of the type the analysis ranks");
  });

  it("name the fit of each evaluation in comparison.split", () => {
    for (const evaluation of evaluations) {
      const { split, adaptation } = evaluation.attributes.comparison as { split: string; adaptation: string };
      const system = evaluation.links.find((link) => link.relation === "system")!.target_id;
      const kind = system.endsWith("-locked") ? "locked" : /-cv-(replication-500|snv-200|indel-120)$/.test(system) ? "cross-validated" : "none";
      expect(split.startsWith(kind), `${evaluation.id}: ${split}`).toBe(true);
      expect(adaptation.startsWith(kind === "none" ? "none" : kind), `${evaluation.id}: ${adaptation}`).toBe(true);
    }
    const count = (start: string) =>
      evaluations.filter((evaluation) => (evaluation.attributes.comparison as { split: string }).split.startsWith(start)).length;
    expect([count("locked"), count("cross-validated"), count("none")]).toEqual([6, 14, 25]);
  });

  it("say the gnomAD split check tested the AVI gains only", () => {
    const concerns = recordsById.get(`${prefix}-source-readme`)!.attributes.evidence_concerns as { message: string; applies_to: string[] }[];
    expect(concerns).toHaveLength(1);
    expect(concerns[0].message).toContain("untested, not cleared");
    expect(concerns[0].message).not.toContain("flags no other gain");
    expect(concerns[0].message).not.toContain("weaker, unflagged");
  });
});
